import test from 'node:test';
import assert from 'node:assert/strict';
import {
  artifactPathsFor,
  auditOutputPassed,
  bindingPassed,
  bunReportPassed,
  playwrightLogPassed,
  reportPassed,
} from '../scripts/acceptance-contract.mjs';

const accepted = [
  { file: 'test/a.test.mjs', title: 'first contract' },
  { file: 'test/b.test.mjs', title: 'second contract' },
];

function bunLog(items, { fail = 0, extra = [] } = {}) {
  const lines = [];
  let currentFile;
  for (const item of items) {
    if (item.file !== currentFile) {
      currentFile = item.file;
      lines.push(`${currentFile}:`);
    }
    lines.push(`(pass) ${item.title} [1.00ms]`);
  }
  lines.push(...extra);
  lines.push(` ${items.length} pass`);
  lines.push(` ${fail} fail`);
  lines.push(`Ran ${items.length} tests across ${new Set(items.map(item => item.file)).size} files. [2.00ms]`);
  return lines.join('\n');
}

const binding = {
  executionId: '00000000-0000-4000-8000-000000000001',
  candidateId: 'candidate-one',
  start: '2026-11-09T02:00:00.000Z',
  end: '2026-11-09T02:00:10.000Z',
};

function playwrightReport(title) {
  return {
    config: {
      metadata: {
        labExecutionId: binding.executionId,
        labCandidateId: binding.candidateId,
      },
    },
    stats: {
      startTime: '2026-11-09T02:00:01.000Z',
      duration: 1000,
      expected: 1,
      unexpected: 0,
      flaky: 0,
      skipped: 0,
    },
    errors: [],
    suites: [{
      title: 'suite',
      specs: [{
        title,
        ok: true,
        tests: [{
          status: 'expected',
          expectedStatus: 'passed',
          results: [{
            status: 'passed',
            retry: 0,
            startTime: '2026-11-09T02:00:01.100Z',
            duration: 500,
            errors: [],
            stdout: [],
            stderr: [],
          }],
        }],
      }],
      suites: [],
    }],
  };
}

test('Bun acceptance requires the exact reviewed test inventory', () => {
  assert.equal(bunReportPassed(bunLog(accepted), accepted), true);
});

test('Bun acceptance rejects removed, substituted, duplicated and skipped checks', () => {
  assert.equal(bunReportPassed(bunLog(accepted.slice(0, 1)), accepted), false);
  assert.equal(bunReportPassed(bunLog([
    accepted[0],
    { file: accepted[1].file, title: 'substituted contract' },
  ]), accepted), false);
  assert.equal(bunReportPassed(bunLog([accepted[0], accepted[0]]), accepted), false);
  assert.equal(bunReportPassed(bunLog(accepted, {
    extra: ['(skip) hidden contract'],
  }), accepted), false);
  assert.equal(bunReportPassed(bunLog(accepted, {
    extra: [' 1 skip'],
  }), accepted), false);
  assert.equal(bunReportPassed(bunLog(accepted, {
    extra: [' 1 todo'],
  }), accepted), false);
  const ambiguousTiming = bunLog(accepted).replace(
    '(pass) first contract [1.00ms]',
    '(pass) first contract [not a duration]',
  );
  assert.equal(bunReportPassed(ambiguousTiming, accepted), false);
  assert.equal(bunReportPassed(`\u001b[31m${bunLog(accepted)}`, accepted), false);
});

test('Playwright acceptance requires exact passing specs without nested errors', () => {
  const report = playwrightReport('expected journey');
  assert.equal(reportPassed(report, ['expected journey'], binding), true);
  report.suites[0].specs[0].tests[0].results[0].error = { message: 'contradiction' };
  assert.equal(reportPassed(report, ['expected journey'], binding), false);
  delete report.suites[0].specs[0].tests[0].results[0].error;
  report.suites[0].specs[0].tests[0].results[0].steps = [{
    title: 'outer',
    duration: 100,
    steps: [{ title: 'inner', duration: 50, error: { message: 'nested contradiction' } }],
  }];
  assert.equal(reportPassed(report, ['expected journey'], binding), false);
});

test('browser acceptance binds report provenance and interval to current execution', () => {
  const report = playwrightReport('expected journey');
  assert.equal(reportPassed(report, ['expected journey'], binding), true);
  assert.equal(reportPassed(report, ['expected journey'], {
    ...binding,
    candidateId: 'candidate-two',
  }), false);
  assert.equal(reportPassed(report, ['expected journey'], {
    ...binding,
    executionId: '00000000-0000-4000-8000-000000000002',
  }), false);
  report.stats.startTime = '2026-11-09T01:59:59.000Z';
  assert.equal(reportPassed(report, ['expected journey'], binding), false);
  assert.equal(bindingPassed({
    labExecutionId: binding.executionId,
    labCandidateId: binding.candidateId,
  }, binding), true);
  assert.equal(bindingPassed({
    labExecutionId: binding.executionId,
    labCandidateId: 'stale-candidate',
  }, binding), false);
  const browserLog = [
    'Running 1 test using 1 worker',
    '  ✓  1 e2e/journeys.spec.ts:1:1 › expected journey (10ms)',
    '  1 passed (20ms)',
  ].join('\n');
  assert.equal(playwrightLogPassed(
    browserLog,
    ['expected journey'],
    'e2e/journeys.spec.ts',
  ), true);
  assert.equal(playwrightLogPassed(
    browserLog.replace('expected journey', 'stale journey'),
    ['expected journey'],
    'e2e/journeys.spec.ts',
  ), false);
});

test('browser log acceptance rejects prefix, hierarchy and source ambiguity', () => {
  const browserLog = [
    'Running 1 test using 1 worker',
    '  ✓  1 e2e/journeys.spec.ts:1:1 › expected journey (10ms)',
    '  1 passed (20ms)',
  ].join('\n');
  const acceptedTitles = ['expected journey'];
  const expectedFile = 'e2e/journeys.spec.ts';
  assert.equal(playwrightLogPassed(browserLog, acceptedTitles, expectedFile), true);
  assert.equal(playwrightLogPassed(
    browserLog.replace('expected journey', 'expected journey (unreviewed variant)'),
    acceptedTitles,
    expectedFile,
  ), false);
  assert.equal(playwrightLogPassed(
    browserLog.replace('› expected journey', '› suite › expected journey'),
    acceptedTitles,
    expectedFile,
  ), false);
  assert.equal(playwrightLogPassed(
    browserLog.replace('e2e/journeys.spec.ts', 'e2e/unreviewed.spec.ts'),
    acceptedTitles,
    expectedFile,
  ), false);
  assert.equal(playwrightLogPassed(
    browserLog.replace('(10ms)', '(not-a-duration)'),
    acceptedTitles,
    expectedFile,
  ), false);
});

test('Bun acceptance rejects control-prefixed and malformed result-shaped output', () => {
  assert.equal(bunReportPassed(bunLog(accepted, {
    extra: [' (fail) unexpected contract [1.00ms]'],
  }), accepted), false);
  assert.equal(bunReportPassed(bunLog(accepted, {
    extra: ['\r(fail) unexpected contract [1.00ms]'],
  }), accepted), false);
  assert.equal(bunReportPassed(bunLog(accepted, {
    extra: [' 1 skip trailing-text'],
  }), accepted), false);
  assert.equal(bunReportPassed(bunLog(accepted), [
    accepted[0],
    { file: accepted[1].file, title: 'second\tcontract' },
  ]), false);
});

test('Playwright acceptance rejects retries, stale result timing and malformed steps', () => {
  const retry = playwrightReport('expected journey');
  retry.suites[0].specs[0].tests[0].results[0].retry = 1;
  assert.equal(reportPassed(retry, ['expected journey'], binding), false);

  const stale = playwrightReport('expected journey');
  stale.suites[0].specs[0].tests[0].results[0].startTime =
    '2026-11-09T01:59:59.000Z';
  assert.equal(reportPassed(stale, ['expected journey'], binding), false);

  const invalidDuration = playwrightReport('expected journey');
  invalidDuration.suites[0].specs[0].tests[0].results[0].duration = -1;
  assert.equal(reportPassed(invalidDuration, ['expected journey'], binding), false);

  const nullStep = playwrightReport('expected journey');
  nullStep.suites[0].specs[0].tests[0].results[0].steps = [null];
  assert.equal(reportPassed(nullStep, ['expected journey'], binding), false);

  const malformedErrors = playwrightReport('expected journey');
  malformedErrors.suites[0].specs[0].tests[0].results[0].steps = [{
    title: 'malformed',
    duration: 1,
    errors: {},
  }];
  assert.equal(reportPassed(malformedErrors, ['expected journey'], binding), false);

  assert.equal(reportPassed(playwrightReport('expected journey'), ['expected journey'], {
    ...binding,
    start: '2026-11-09T02:00:10.000Z',
    end: '2026-11-09T02:00:00.000Z',
  }), false);
});

test('audit acceptance requires exit zero and an exact plain empty object', () => {
  assert.equal(auditOutputPassed(0, '{}', ''), true);
  assert.equal(auditOutputPassed(1, '{}', ''), false);
  assert.equal(auditOutputPassed(0, '[]', ''), false);
  assert.equal(auditOutputPassed(0, '{"advisories":[]}', ''), false);
  assert.equal(auditOutputPassed(0, 'not json', ''), false);
  assert.equal(auditOutputPassed(0, '{}', '{}'), false);
  assert.equal(auditOutputPassed(0, '', '{}'), false);
});

test('recorded audit artifacts include the canonical audit payload', () => {
  assert.deepEqual(
    artifactPathsFor('audit', 'evidence/hostile-repair/audit-run', ['bun', 'audit', '--json']),
    [
      'evidence/hostile-repair/audit-run.log',
      'evidence/hostile-repair/audit-run.stdout.log',
      'evidence/hostile-repair/audit-run.stderr.log',
      'evidence/hostile-repair/audit-run-audit.json',
    ],
  );
});
