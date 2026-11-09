import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
test('executable researched role policy and exact SIWC command',async()=>{
 const p=JSON.parse(await readFile('llm-policy.json','utf8'));
 assert.deepEqual(p.deterministic,{roles:['domain','persistence','api','playwright-mechanics','bugsink','audit','evidence','cleanup'],llm:false});
 assert.deepEqual(p.reviewer,{route:'siwc',model:'gpt-6-sol',family:'gpt-6',planner:'balance',providerReasoning:'low',driver:'playwright',unclearPasses:false,overridesDeterministicFailure:false});
 assert.deepEqual(p.implementation,{provider:'openai-codex',model:'gpt-6-astra',reasoning:'medium'});
 assert.deepEqual(p.hostileReview,{...p.implementation,readOnly:true,independent:true});assert.equal(p.gemini,false);
 assert.deepEqual(p.escalation,{layersAtOnce:1,triggers:['repeatable-miss','long-branching-journey'],autonomousOnly:['calibration','material-ux-change','exact-release-candidate']});
 const pkg=JSON.parse(await readFile('package.json','utf8'));
 assert.equal(pkg.scripts['test:reviews'],'bun scripts/run-reviews.mjs');
 const docs=await readFile('LLM_POLICY.md','utf8');for(const word of ['gpt-6-astra','openai-codex','medium','gpt-6-sol','balance','low','UNCLEAR'])assert.ok(docs.includes(word));
 const active=await readFile('e2e/reviews.spec.ts','utf8'); assert.ok(!/codex:\/\/app-server|\.aiAct\(/.test(active));
});
