import { test } from 'node:test';
import assert from 'node:assert/strict';
import { chromium } from '@playwright/test';
import { candidatePaths, closure } from '../scripts/candidate.mjs';

const candidate = { id: 'candidate', files: { a: 'hash' } };
const cleanup = Object.fromEntries(
  [
    'browserProcessExited',
    'browserDisconnected',
    'taskServerClosed',
    'stateDeleted',
    'portsClear',
    'childExited',
    'existing8100Unchanged',
  ].map(key => [key, true]),
);
let executionSequence = 0;

function record(kind, run) {
  return {
    before: candidate,
    after: candidate,
    kind,
    run: `${kind}-${run}`,
    exit: 0,
    artifactsVerified: true,
    resultsVerified: true,
    semanticVerified: true,
    executionId: `00000000-0000-4000-8000-${String(++executionSequence).padStart(12, '0')}`,
    cleanup,
    review: {
      model: 'gpt-6-sol',
      auth: 'siwc',
      providerReasoning: 'low',
      planningEffort: 'balance',
      verdict: kind === 'J05' ? 'RED' : 'GREEN',
      outcome:
        kind === 'J05' ? 'stopped_at_unclear_choice' : 'completed_goal',
      contradictions: [],
    },
  };
}

const records = ['bun', 'chromium', 'bugsink', 'J05', 'J06', 'audit'].flatMap(
  kind => [1, 2].map(run => record(kind, run)),
);
records.push(
  ...['bootstrap', 'callback', 'already-exited', 'output', 'response'].map(
    mode => ({
      ...record('failure', mode),
      failureMode: mode,
      exit: 1,
    }),
  ),
);

test('F4 closure accepts complete independently verified lineage', () => {
  assert.equal(closure(candidate, records).passed, true);
});

test('F4 closure rejects stale, unverified, incomplete and semantically false evidence', () => {
  const badCases = [
    [],
    records.map(item => ({ ...item, after: { id: 'stale', files: {} } })),
    records.map(item => ({ ...item, artifactsVerified: false })),
    records.filter(item => item.kind !== 'J06'),
    records.map(item => ({ ...item, cleanup: {} })),
    records.filter(item => item.run.endsWith('-1')),
    records.map(item =>
      item.kind === 'audit' ? { ...item, semanticVerified: false } : item,
    ),
    records.map(item =>
      item.kind === 'failure'
        ? { ...item, before: { id: candidate.id, files: {} } }
        : item,
    ),
  ];
  for (const bad of badCases) assert.equal(closure(candidate, bad).passed, false);
});

test('F4 relabeling one execution cannot satisfy repeated-run requirements', () => {
  const repeatedKinds = ['bun', 'chromium', 'bugsink', 'J05', 'J06'];
  const relabeled = records.filter(
    item => !repeatedKinds.includes(item.kind) || item.run.endsWith('-1'),
  );
  for (const kind of repeatedKinds) {
    const first = records.find(item => item.kind === kind && item.run.endsWith('-1'));
    relabeled.push({ ...first, run: `${kind}-relabeled` });
  }
  assert.equal(closure(candidate, relabeled).passed, false);
});

test('F4 closure rejects an unresolved later exact-candidate gate failure', () => {
  const laterFailure = {
    ...record('bun', 'later-failure'),
    exit: 1,
    resultsVerified: false,
    semanticVerified: false,
  };
  assert.equal(closure(candidate, [...records, laterFailure]).passed, false);
});

test('accepted journey and check authorities are bound into candidate identity', () => {
  assert.equal(candidatePaths.includes('JOURNEY_CATALOG.md'), true);
  assert.equal(candidatePaths.includes('ACCEPTED_CHECKS.json'), true);
  assert.equal(candidatePaths.includes('README.md'), true);
  assert.equal(candidatePaths.includes('.gitignore'), true);
});

test('candidate binds the headless Chromium runtime selected by Playwright', () => {
  const selected = chromium.executablePath().match(/^(.*\/ms-playwright)\/chromium-(\d+)\//);
  assert.ok(selected, 'expected a revisioned Playwright Chromium path');
  assert.equal(
    candidatePaths.includes(`${selected[1]}/chromium_headless_shell-${selected[2]}`),
    true,
  );
});
