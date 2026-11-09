const same = (left, right) => JSON.stringify(left) === JSON.stringify(right);

const statsPassed = (stats, expected) =>
  stats?.expected === expected &&
  stats?.unexpected === 0 &&
  stats?.flaky === 0 &&
  stats?.skipped === 0;

function collectSpecs(suites) {
  const specs = [];
  for (const suite of suites || []) {
    specs.push(...(suite.specs || []));
    specs.push(...collectSpecs(suite.suites));
  }
  return specs;
}

function stepsPassed(steps) {
  if (steps === undefined) return true;
  return Array.isArray(steps) && steps.every(step =>
    step !== null &&
    typeof step === 'object' &&
    !Array.isArray(step) &&
    typeof step.title === 'string' &&
    step.title.length > 0 &&
    Number.isFinite(step.duration) &&
    step.duration >= 0 &&
    step?.error == null &&
    (step.errors === undefined ||
      (Array.isArray(step.errors) && step.errors.length === 0)) &&
    stepsPassed(step?.steps),
  );
}

export function bindingPassed(value, binding) {
  return value?.labExecutionId === binding?.executionId &&
    value?.labCandidateId === binding?.candidateId;
}

export function reportPassed(report, expectedTitles, binding) {
  const control = /[\u0000-\u001f\u007f]/;
  if (!Array.isArray(expectedTitles) ||
      expectedTitles.length === 0 ||
      new Set(expectedTitles).size !== expectedTitles.length ||
      expectedTitles.some(title =>
        typeof title !== 'string' || title.length === 0 || control.test(title),
      )) return false;
  const reportStart = Date.parse(report?.stats?.startTime);
  const recordStart = Date.parse(binding?.start);
  const recordEnd = Date.parse(binding?.end);
  const duration = report?.stats?.duration;
  if (!statsPassed(report?.stats, expectedTitles.length) ||
      !Array.isArray(report?.errors) || report.errors.length !== 0 ||
      !bindingPassed(report?.config?.metadata, binding) ||
      !Number.isFinite(reportStart) ||
      !Number.isFinite(recordStart) ||
      !Number.isFinite(recordEnd) ||
      recordStart > recordEnd ||
      !Number.isFinite(duration) || duration < 0 ||
      reportStart < recordStart || reportStart + duration > recordEnd)
    return false;
  const specs = collectSpecs(report?.suites);
  if (!same(specs.map(spec => spec.title).sort(), [...expectedTitles].sort()))
    return false;
  return specs.every(spec =>
    spec.ok === true &&
    Array.isArray(spec.tests) &&
    spec.tests.length === 1 &&
    spec.tests.every(test =>
      test.status === 'expected' &&
      test.expectedStatus === 'passed' &&
      Array.isArray(test.results) &&
      test.results.length === 1 &&
      test.results.every(result => {
        const resultStart = Date.parse(result?.startTime);
        const resultDuration = result?.duration;
        return result.status === 'passed' &&
        result.retry === 0 &&
        Number.isFinite(resultStart) &&
        Number.isFinite(resultDuration) &&
        resultDuration >= 0 &&
        resultStart >= recordStart &&
        resultStart + resultDuration <= recordEnd &&
        resultStart >= reportStart &&
        resultStart + resultDuration <= reportStart + duration &&
        result.error == null &&
        Array.isArray(result.errors) &&
        result.errors.length === 0 &&
        stepsPassed(result.steps) &&
        Array.isArray(result.stdout) &&
        Array.isArray(result.stderr) &&
        result.stderr.length === 0;
      }),
    ),
  );
}

export function playwrightLogPassed(logPayload, expectedTitles, expectedFile) {
  const control = /[\u0000-\u001f\u007f]/;
  if (typeof logPayload !== 'string' ||
      !Array.isArray(expectedTitles) ||
      expectedTitles.length === 0 ||
      new Set(expectedTitles).size !== expectedTitles.length ||
      expectedTitles.some(title =>
        typeof title !== 'string' || title.length === 0 || control.test(title),
      ) ||
      typeof expectedFile !== 'string' ||
      !/^(?:e2e\/)\S+\.spec\.ts$/.test(expectedFile) ||
      control.test(expectedFile)) return false;
  const lines = logPayload.split('\n');
  const running = lines.filter(line => /^Running \d+ tests? using \d+ workers?$/.test(line));
  const passed = lines.filter(line => /^\s*\d+ passed \([^)]+\)\s*$/.test(line));
  const resultLines = lines.filter(line => /^\s*[✓×-]\s+\d+\s+/.test(line));
  const resultPattern = /^\s*([✓×-])\s+(\d+)\s+(\S+):(\d+):(\d+)\s+›\s+(.+?)\s+\((\d+(?:\.\d+)?(?:ms|s|m))\)\s*$/;
  const results = resultLines.map(line => line.match(resultPattern));
  if (results.some(result => result === null)) return false;
  const identities = results.map(result => ({
    marker: result[1],
    ordinal: Number(result[2]),
    file: result[3],
    line: Number(result[4]),
    column: Number(result[5]),
    title: result[6],
  }));
  return running.length === 1 &&
    running[0].startsWith(`Running ${expectedTitles.length} test${expectedTitles.length === 1 ? '' : 's'} `) &&
    passed.length === 1 &&
    Number(passed[0].trim().split(' ')[0]) === expectedTitles.length &&
    !lines.some(line => /^\s*\d+ (?:failed|skipped|flaky)\b/.test(line)) &&
    identities.length === expectedTitles.length &&
    identities.every((item, index) =>
      item.marker === '✓' &&
      item.ordinal === index + 1 &&
      item.file === expectedFile &&
      item.line > 0 &&
      item.column > 0
    ) &&
    same(
      identities.map(item => item.title).sort(),
      [...expectedTitles].sort(),
    );
}

export function bunReportPassed(logPayload, acceptedTests) {
  const payloadControl = /[\u0000-\u0009\u000b-\u001f\u007f]/;
  const identityControl = /[\u0000-\u001f\u007f]/;
  if (typeof logPayload !== 'string' || payloadControl.test(logPayload) ||
      !Array.isArray(acceptedTests) || acceptedTests.length === 0 ||
      acceptedTests.some(item =>
        item === null ||
        typeof item !== 'object' ||
        typeof item.file !== 'string' ||
        !/^test\/[^\u0000-\u001f\u007f]+\.test\.mjs$/.test(item.file) ||
        item.file.split('/').includes('..') ||
        typeof item.title !== 'string' ||
        item.title.length === 0 ||
        identityControl.test(item.title),
      )) return false;
  const observed = [];
  const summaries = [];
  let currentFile;
  for (const line of logPayload.split('\n')) {
    const file = line.match(/^(test\/[^:]+):$/);
    if (file) {
      currentFile = file[1];
      continue;
    }
    if (/^\s*\((?:pass|fail|skip|todo)\)/.test(line)) {
      const result = line.match(/^\((pass|fail|skip|todo)\) (.*?)(?: \[(?:\d+(?:\.\d+)?(?:ns|µs|ms|s))\])?$/);
      if (!result) return false;
      observed.push({ status: result[1], file: currentFile, title: result[2] });
      continue;
    }
    const summaryLike = line.match(/^\s*(\d+)\s+(pass|fail|skip|todo)(.*)$/);
    if (summaryLike) {
      if (summaryLike[3] !== '') return false;
      summaries.push({ count: Number(summaryLike[1]), kind: summaryLike[2] });
    }
  }
  if (observed.some(item => item.status !== 'pass' || typeof item.file !== 'string')) return false;
  const expectedKeys = acceptedTests.map(item => `${item.file}\u0000${item.title}`).sort();
  const observedKeys = observed.map(item => `${item.file}\u0000${item.title}`).sort();
  if (new Set(expectedKeys).size !== expectedKeys.length ||
      new Set(observedKeys).size !== observedKeys.length ||
      !same(expectedKeys, observedKeys)) return false;
  const passLines = summaries.filter(item => item.kind === 'pass');
  const failLines = summaries.filter(item => item.kind === 'fail');
  const skipLines = summaries.filter(item => item.kind === 'skip');
  const todoLines = summaries.filter(item => item.kind === 'todo');
  const ranLines = [...logPayload.matchAll(/^Ran (\d+) tests across (\d+) files\. \[(?:\d+(?:\.\d+)?(?:ns|µs|ms|s))\]$/gm)];
  const passed = passLines[0]?.count;
  return passLines.length === 1 &&
    failLines.length === 1 &&
    skipLines.length === 0 &&
    todoLines.length === 0 &&
    ranLines.length === 1 &&
    passed === acceptedTests.length &&
    failLines[0].count === 0 &&
    Number(ranLines[0][1]) === passed &&
    Number(ranLines[0][2]) === new Set(acceptedTests.map(item => item.file)).size;
}

export function plainEmptyObject(value) {
  return value !== null &&
    typeof value === 'object' &&
    !Array.isArray(value) &&
    Object.getPrototypeOf(value) === Object.prototype &&
    Object.keys(value).length === 0;
}

export function auditOutputPassed(exit, stdout, stderr) {
  if (exit !== 0 || typeof stdout !== 'string' || stderr !== '') return false;
  try {
    return plainEmptyObject(JSON.parse(stdout));
  } catch {
    return false;
  }
}

export function artifactPathsFor(kind, base, args) {
  const paths = [`${base}.log`];
  if (kind === 'chromium' || kind === 'stack' || kind === 'reviews')
    paths.push(`${base}-chromium.json`);
  if (kind === 'J05' || kind === 'J06')
    paths.push(`${base}-chromium.json`, `${base}-${kind}.json`);
  if (kind === 'bugsink' || kind === 'failure') {
    const resultPath = `evidence/bugsink/${args[2]}.json`;
    paths.push(resultPath, resultPath.replace('.json', '-scan.json'));
  }
  if (kind === 'audit') paths.push(
    `${base}.stdout.log`,
    `${base}.stderr.log`,
    `${base}-audit.json`,
  );
  return paths;
}
