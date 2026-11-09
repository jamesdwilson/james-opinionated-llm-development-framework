import { readFile, readdir } from 'node:fs/promises';
import { resolve } from 'node:path';
import { manifest, closure, hash } from './candidate.mjs';
import {
  artifactPathsFor,
  auditOutputPassed,
  bindingPassed,
  bunReportPassed,
  playwrightLogPassed,
  reportPassed,
} from './acceptance-contract.mjs';

const candidate = await manifest();
const acceptedChecks = JSON.parse(await readFile('ACCEPTED_CHECKS.json', 'utf8'));
const records = [];
const cleanupKeys = [
  'browserProcessExited',
  'browserDisconnected',
  'taskServerClosed',
  'stateDeleted',
  'portsClear',
  'childExited',
  'existing8100Unchanged',
];
const same = (left, right) => JSON.stringify(left) === JSON.stringify(right);
const cleanupPassed = cleanup =>
  cleanup && cleanupKeys.every(key => cleanup[key] === true);

const scanPassed = (scan, run, minimumBytes) =>
  scan?.passed === true &&
  Number.isInteger(scan.files) &&
  Number.isInteger(scan.members) &&
  Number.isInteger(scan.decoded) &&
  Number.isInteger(scan.bytes) &&
  scan.members >= 0 &&
  scan.decoded >= 0 &&
  scan.bytes >= minimumBytes &&
  scan.findings === 0 &&
  scan.limits === 0 &&
  scan.symlinks === 0 &&
  scan.files > 0 &&
  Array.isArray(scan.inventory) &&
  scan.inventory.length === scan.files &&
  new Set(scan.inventory).size === scan.files &&
  scan.inventory.includes(`${run}.json`) &&
  scan.inventory.every(path => typeof path === 'string' && path.length > 0 && !path.startsWith('/') && !path.split('/').includes('..'));
async function verifyArtifacts(record, expectedPaths) {
  if (!Array.isArray(record.artifacts) || record.artifacts.length !== expectedPaths.length)
    return { verified: false, files: new Map() };
  const expected = new Set(expectedPaths.map(path => resolve(path)));
  const actual = new Set(record.artifacts.map(artifact => resolve(artifact.path)));
  if (!same([...actual].sort(), [...expected].sort()))
    return { verified: false, files: new Map() };
  const files = new Map();
  for (const artifact of record.artifacts) {
    try {
      const bytes = await readFile(artifact.path);
      if (hash(bytes) !== artifact.sha256)
        return { verified: false, files: new Map() };
      files.set(resolve(artifact.path), bytes);
    } catch {
      return { verified: false, files: new Map() };
    }
  }
  return { verified: true, files };
}

async function verifyRecord(record) {
  const base = `evidence/hostile-repair/${record.run}`;
  let expectedCommand;
  if (record.kind === 'bun') {
    expectedCommand = ['bun', 'test', 'test'];
  } else if (record.kind === 'chromium') {
    expectedCommand = [
      'bun',
      'x',
      '--bun',
      'playwright',
      'test',
      'e2e/journeys.spec.ts',
    ];
  } else if (record.kind === 'bugsink' || record.kind === 'failure') {
    expectedCommand = [
      'bun',
      'scripts/bugsink-gate.mjs',
      record.run,
      ...(record.kind === 'failure' ? [`--fail-${record.failureMode}`] : []),
    ];
  } else if (record.kind === 'J05' || record.kind === 'J06') {
    expectedCommand = ['bun', 'scripts/run-reviews.mjs'];
  } else if (record.kind === 'audit') {
    expectedCommand = ['bun', 'audit', '--json'];
  } else {
    return false;
  }
  if (!same(record.command, expectedCommand)) return false;
  const expectedPaths = artifactPathsFor(record.kind, base, expectedCommand);
  const artifacts = await verifyArtifacts(record, expectedPaths);
  record.artifactsVerified = artifacts.verified;
  if (!artifacts.verified) return false;
  const text = path => artifacts.files.get(resolve(path)).toString('utf8');
  const json = path => JSON.parse(text(path));
  const logLines = text(`${base}.log`).split('\n');
  if (logLines.shift() !== `LAB_EXECUTION_ID=${record.executionId}`) return false;
  const logPayload = logLines.join('\n');
  const binding = {
    executionId: record.executionId,
    candidateId: record.before.id,
    start: record.start,
    end: record.end,
  };

  if (record.kind === 'bun') {
    return record.exit === 0 && bunReportPassed(logPayload, acceptedChecks.deterministic);
  }
  if (record.kind === 'chromium') {
    return record.exit === 0 && reportPassed(
      json(`${base}-chromium.json`),
      acceptedChecks.chromiumTitles,
      binding,
    ) && playwrightLogPassed(logPayload, acceptedChecks.chromiumTitles, 'e2e/journeys.spec.ts');
  }
  if (record.kind === 'bugsink' || record.kind === 'failure') {
    const resultPath = `evidence/bugsink/${record.run}.json`;
    const result = json(resultPath);
    const scan = json(`evidence/bugsink/${record.run}-scan.json`);
    const expectedExit = record.kind === 'failure' ? 1 : 0;
    const resultSemantics = record.kind === 'bugsink'
      ? result.passed === true &&
        result.version === '2.6.3' &&
        result.fresh === true &&
        result.sqliteDatabases === 2 &&
        result.events === 1 &&
        result.exactPayload === true &&
        result.recovery === true &&
        result.phase === 'complete'
      : result.passed === false &&
        result.failureMode === record.failureMode &&
        result.failureReached === true;
    let loggedResult;
    try{loggedResult=JSON.parse(logPayload);}catch{return false;}
    return record.exit === expectedExit &&
      resultSemantics &&
      result.scanFailure !== true &&
      same(loggedResult,result) &&
      cleanupPassed(result.cleanup) &&
      cleanupPassed(record.cleanup) &&
      same(result.cleanup,record.cleanup) &&
      same(result.cleanup.existing8100Before,result.cleanup.existing8100After) &&
      result.cleanup.existing8100Before?.status === 'present' &&
      Array.isArray(result.cleanup.existing8100Before?.owners) &&
      result.cleanup.existing8100Before.owners.length > 0 &&
      scanPassed(scan,record.run,artifacts.files.get(resolve(resultPath)).byteLength);
  }
  if (record.kind === 'J05' || record.kind === 'J06') {
    const playwright = json(`${base}-chromium.json`);
    const evidence = json(`${base}-${record.kind}.json`);
    const review = {
      ...evidence.review,
      model: evidence.model,
      auth: evidence.auth,
      providerReasoning: evidence.providerReasoning,
      planningEffort: evidence.planningEffort,
    };
    return record.exit === 0 &&
      reportPassed(playwright, acceptedChecks.reviewTitles, binding) &&
      playwrightLogPassed(logPayload, acceptedChecks.reviewTitles, 'e2e/reviews.spec.ts') &&
      bindingPassed(evidence, binding) &&
      evidence.observedFrames > 0 &&
      same(record.review, review) &&
      review.model === 'gpt-6-sol' &&
      review.auth === 'siwc' &&
      review.providerReasoning === 'low' &&
      review.planningEffort === 'balance' &&
      review.verdict === (record.kind === 'J05' ? 'RED' : 'GREEN') &&
      review.outcome ===
        (record.kind === 'J05'
          ? 'stopped_at_unclear_choice'
          : 'completed_goal') &&
      (record.kind !== 'J06' || review.contradictions?.length === 0);
  }
  const audit = json(`${base}-audit.json`);
  const streamPayload = path => {
    const lines = text(path).split('\n');
    if (lines.shift() !== `LAB_EXECUTION_ID=${record.executionId}`) return null;
    return lines.join('\n');
  };
  const stdout = streamPayload(`${base}.stdout.log`);
  const stderr = streamPayload(`${base}.stderr.log`);
  return stdout !== null &&
    stderr !== null &&
    auditOutputPassed(record.exit, stdout, stderr) &&
    same(JSON.parse(stdout), audit) &&
    logPayload === stdout;
}

for (const name of await readdir('evidence/hostile-repair')) {
  if (!name.endsWith('-execution.json')) continue;
  const record = JSON.parse(
    await readFile(`evidence/hostile-repair/${name}`, 'utf8'),
  );
  record.artifactsVerified = false;
  record.semanticVerified = false;
  if (record.before?.id === candidate.id && record.after?.id === candidate.id) {
    try {
      record.semanticVerified = await verifyRecord(record);
    } catch {
      record.semanticVerified = false;
    }
  }
  records.push(record);
}

const result = closure(candidate, records);
console.log(JSON.stringify(result, null, 2));
process.exitCode = result.passed ? 0 : 1;
