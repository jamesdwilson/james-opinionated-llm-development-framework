import { validateReviewConfig } from '../scripts/review-config.mjs';
const validated = validateReviewConfig(process.env);
import { driveNorthStar } from './review-driver';
import { test as local, expect } from './fixture';
import { PlaywrightAiFixture, type PlayWrightAiFixtureType } from '@midscene/web/playwright';
import { readFile, writeFile } from 'node:fs/promises';
const test = local.extend<PlayWrightAiFixtureType>(PlaywrightAiFixture({ cache: false, modelConfig: validated.modelConfig }));
const planningEffort = process.env.MIDSCENE_JOURNEY_EFFORT;
if (planningEffort !== 'balance') throw new Error('Review script must configure planning effort balance.');
const schema = {
  verdict: 'Return exactly GREEN, RED, or UNCLEAR. Judge only the observed visible experience relative to the goal. GREEN means the goal is clear and achieved. RED means a visible required choice does not explain practical consequences and forces a reasonable first-time user to guess or stop, or another visible obstacle prevents the goal. UNCLEAR applies only when the capture does not show the required choice or enough of the interface to judge it.',
  outcome: 'Return exactly completed_goal, stopped_at_unclear_choice, needed_recovery, or failed_goal.',
  evidence: 'Describe specific visible labels, states and transitions supporting your judgment.',
  frictionFindings: 'Return an array of visible friction findings; empty if none.',
  purpose: 'Evaluate clarity of the user purpose.', hierarchy: 'Evaluate visual hierarchy and the next action.', terminology: 'Evaluate whether the terms explain practical consequences.', progress: 'Evaluate visible progress and confirmation.', recovery: 'Evaluate observed recovery paths; state if unvisited.',
  contradictions: 'Return an array of contradictions between visible frames; empty if none.',
  unvisitedScope: 'Return an array of what the observation cannot establish, including nonvisual persistence and backend truth.'
};
async function save(info, observation, context) {
  try {
    const review = await observation.aiQuery(schema, { context });
    const evidence={ review, observedFrames:observation.frameCount, ...validated.identity, labExecutionId:process.env.LAB_EXECUTION_ID, labCandidateId:process.env.LAB_CANDIDATE_ID, cache:false, driver:'Playwright only; planning effort configured but no AI planning actions invoked' };
    await writeFile(`evidence/${process.env.REVIEW_RUN || 'review'}-${info.title.startsWith('J05')?'J05':'J06'}.json`,JSON.stringify(evidence,null,2)+'\n');
    await info.attach('structured-review',{body:Buffer.from(JSON.stringify(evidence,null,2)),contentType:'application/json'});
    expect(observation.frameCount).toBeGreaterThan(0); expect(review.evidence.length).toBeGreaterThan(0);
    expect(Array.isArray(review.frictionFindings)).toBe(true); expect(Array.isArray(review.contradictions)).toBe(true); expect(Array.isArray(review.unvisitedScope)).toBe(true);
    return review;
  } finally { await observation.dispose(); }
}
test('J05 cold-user bounded choice review', async ({page,url,agentForPage},info) => {
  await page.setViewportSize({width:390,height:844}); await page.goto(url+'/ambiguous'); await page.getByLabel('Task title',{exact:true}).fill('Wash dishes');
  const agent=await agentForPage(page); const observer=await agent.startObserving({intervalMs:400,maxFrames:4});
  await page.waitForTimeout(900); const observation=await observer.stop();
  const review=await save(info,observation,'You are a first-time household member. Your goal is to create Wash dishes so it counts as complete only after another household member approves. Use only the visible screen to decide whether you can confidently proceed. Do not invent definitions for unfamiliar terms. Review this bounded observation; you cannot operate the interface.');
  await expect(page.locator('input:checked')).toHaveCount(0); await expect(page.getByRole('button',{name:'Create task'})).toBeDisabled();
  expect((await (await page.request.get(url+'/api/tasks')).json()).tasks).toEqual([]);
  expect(review.verdict).toBe('RED'); expect(review.outcome).toBe('stopped_at_unclear_choice'); expect(review.frictionFindings.length).toBeGreaterThan(0);
});
test('J06 North-Star sequence review', async ({page,url,agentForPage,expectedErrors},info) => {
  await page.goto(url); const agent=await agentForPage(page); const observer=await agent.startObserving({intervalMs:400,maxFrames:30});
  const hold=()=>page.waitForTimeout(850);
  try {
    await driveNorthStar(page, expectedErrors, hold);
    const observation=await observer.stop();
    const northStar=await readFile('NORTH_STAR.md','utf8');
    const review=await save(info,observation,`Review this observed household task journey against this North Star: ${northStar}\nPlaywright drove the sequence. Judge only visible purpose, hierarchy, terminology, progress, recovery and contradictions. Document reload and persistence are deterministic Playwright responsibilities on this same candidate, not screenshot-review requirements. List nonvisual persistence and backend truth in unvisitedScope where appropriate; judge visible clarity only.`);
    expect(review.verdict).toBe('GREEN'); expect(review.outcome).toBe('completed_goal'); expect(review.contradictions).toEqual([]);
  } finally { await observer.dispose(); }
});
