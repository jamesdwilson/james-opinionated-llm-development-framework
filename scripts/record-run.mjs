import { spawn } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { createWriteStream } from 'node:fs';
import { writeFile, readFile } from 'node:fs/promises';
import { manifest, hash } from './candidate.mjs';
import {
  artifactPathsFor,
  auditOutputPassed,
  bindingPassed,
  bunReportPassed,
  playwrightLogPassed,
  reportPassed,
} from './acceptance-contract.mjs';

const [run, kind, ...args] = process.argv.slice(2);
if (!/^[a-z0-9-]+$/.test(run) || !args.length) throw Error('Run arguments');
const acceptedChecks = JSON.parse(await readFile('ACCEPTED_CHECKS.json', 'utf8'));

const base = `evidence/hostile-repair/${run}`;
const executionId = randomUUID();
const before = await manifest();
const start = new Date().toISOString();
const log = createWriteStream(`${base}.log`, { flags: 'wx' });
const stdoutLog = createWriteStream(`${base}.stdout.log`, { flags: 'wx' });
const stderrLog = createWriteStream(`${base}.stderr.log`, { flags: 'wx' });
log.write(`LAB_EXECUTION_ID=${executionId}\n`);
stdoutLog.write(`LAB_EXECUTION_ID=${executionId}\n`);
stderrLog.write(`LAB_EXECUTION_ID=${executionId}\n`);
const env = {
  PATH: '/opt/homebrew/bin:/usr/bin:/bin',
  HOME: process.env.HOME,
  RESULT_FILE: `${base}-chromium.json`,
  LAB_EXECUTION_ID: executionId,
  LAB_CANDIDATE_ID: before.id,
};
if (kind === 'reviews') env.REVIEW_RUN = `hostile-repair/${run}`;

const child = spawn(args[0], args.slice(1), { env, stdio: ['ignore', 'pipe', 'pipe'] });
child.stdout.on('data', chunk => { log.write(chunk); stdoutLog.write(chunk); });
child.stderr.on('data', chunk => { log.write(chunk); stderrLog.write(chunk); });
const exit = await new Promise(resolve => {
  child.once('error', () => resolve(1));
  child.once('close', code => resolve(code ?? 1));
});
await Promise.all([
  new Promise(resolve => log.end(resolve)),
  new Promise(resolve => stdoutLog.end(resolve)),
  new Promise(resolve => stderrLog.end(resolve)),
]);
const end = new Date().toISOString();

const after = await manifest();
const paths = artifactPathsFor(kind, base, args);
let cleanup;
let resultsVerified = false;
const binding = { executionId, candidateId: before.id, start, end };

if (kind === 'bugsink' || kind === 'failure') {
  const resultPath = `evidence/bugsink/${args[2]}.json`;
  const result = JSON.parse(await readFile(resultPath));
  cleanup = result.cleanup;
  resultsVerified = Object.values(cleanup).filter(value => typeof value === 'boolean').every(Boolean)
    && JSON.parse(await readFile(resultPath.replace('.json', '-scan.json'))).passed === true
    && result.passed === (kind === 'bugsink');
}
if (kind === 'bun') {
  const text = await readFile(`${base}.log`, 'utf8');
  const completeSuite = args.length === 3 && args[0] === 'bun' && args[1] === 'test' && args[2] === 'test';
  const payload = text.split('\n').slice(1).join('\n');
  resultsVerified = completeSuite && bunReportPassed(payload, acceptedChecks.deterministic);
}
if (kind === 'chromium') {
  const result = JSON.parse(await readFile(`${base}-chromium.json`));
  const text = await readFile(`${base}.log`, 'utf8');
  const payload = text.split('\n').slice(1).join('\n');
  resultsVerified = reportPassed(result, acceptedChecks.chromiumTitles, binding)
    && playwrightLogPassed(payload, acceptedChecks.chromiumTitles, 'e2e/journeys.spec.ts');
}
if (kind === 'audit') {
  const stdout = (await readFile(`${base}.stdout.log`, 'utf8')).split('\n').slice(1).join('\n');
  const stderr = (await readFile(`${base}.stderr.log`, 'utf8')).split('\n').slice(1).join('\n');
  const payload = stdout.trim();
  await writeFile(`${base}-audit.json`, `${payload}\n`, { flag: 'wx' });
  resultsVerified = auditOutputPassed(exit, stdout, stderr);
}

if (kind === 'reviews') {
  const playwright = JSON.parse(await readFile(`${base}-chromium.json`));
  const text = await readFile(`${base}.log`, 'utf8');
  const payload = text.split('\n').slice(1).join('\n');
  const playwrightVerified = reportPassed(playwright, acceptedChecks.reviewTitles, binding)
    && playwrightLogPassed(payload, acceptedChecks.reviewTitles, 'e2e/reviews.spec.ts');
  for (const reviewKind of ['J05', 'J06']) {
    const reviewPath = `${base}-${reviewKind}.json`;
    const evidence = JSON.parse(await readFile(reviewPath));
    const review = {
      ...evidence.review,
      model: evidence.model,
      auth: evidence.auth,
      providerReasoning: evidence.providerReasoning,
      planningEffort: evidence.planningEffort,
    };
    const verified = playwrightVerified
      && bindingPassed(evidence, binding)
      && evidence.observedFrames > 0
      && review.model === 'gpt-6-sol'
      && review.auth === 'siwc'
      && review.providerReasoning === 'low'
      && review.planningEffort === 'balance'
      && review.verdict === (reviewKind === 'J05' ? 'RED' : 'GREEN')
      && review.outcome === (reviewKind === 'J05' ? 'stopped_at_unclear_choice' : 'completed_goal')
      && (reviewKind !== 'J06' || review.contradictions?.length === 0);
    const reviewPaths = [`${base}.log`, `${base}-chromium.json`, reviewPath];
    const artifacts = [];
    for (const path of reviewPaths) artifacts.push({ path, sha256: hash(await readFile(path)) });
    await writeFile(`${base}-${reviewKind}-execution.json`, JSON.stringify({
      run,
      kind: reviewKind,
      executionId,
      command: args,
      start,
      end,
      exit,
      before,
      after,
      resultsVerified: verified,
      review,
      artifacts,
    }, null, 2) + '\n', { flag: 'wx' });
  }
  console.log(JSON.stringify({ run, kind, exit, unchanged: before.id === after.id, reviewsRecorded: true }));
  process.exitCode = exit;
} else {
  const artifacts = [];
  for (const path of paths) artifacts.push({ path, sha256: hash(await readFile(path)) });
  await writeFile(`${base}-execution.json`, JSON.stringify({
    run,
    kind,
    executionId,
    command: args,
    start,
    end,
    exit,
    before,
    after,
    cleanup,
    resultsVerified,
    failureMode: kind === 'failure' ? args.at(-1).replace('--fail-', '') : undefined,
    artifacts,
  }, null, 2) + '\n', { flag: 'wx' });
  console.log(JSON.stringify({ run, kind, exit, unchanged: before.id === after.id }));
  process.exitCode = exit;
}
