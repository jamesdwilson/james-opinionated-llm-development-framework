import { expect, test } from 'bun:test';
import { readFile } from 'node:fs/promises';

const packageJson = JSON.parse(await readFile(new URL('../package.json', import.meta.url), 'utf8'));
const service = await readFile(new URL('../scripts/bugsink/service.py', import.meta.url), 'utf8');
const settings = await readFile(new URL('../scripts/bugsink/lab_settings.py', import.meta.url), 'utf8');
const gate = await readFile(new URL('../scripts/bugsink-gate.mjs', import.meta.url), 'utf8');
const candidate = await readFile(new URL('../scripts/candidate.mjs', import.meta.url), 'utf8');

test('latest admitted dotenv is pinned in the Bun graph', () => {
  expect(packageJson.devDependencies.dotenv).toBe('18.0.9');
});

test('isolated Bugsink uses 2.6.3 native project-bound read capabilities', () => {
  expect(gate).toContain('/bugsink-2.6.3-venv/bin/python');
  expect(gate).toContain("assert.equal(config.version,'2.6.3')");
  expect(service).toContain("assert version('bugsink') == '2.6.3'");
  for (const capability of ['is_project_bound=True', 'projects_read=True', 'issues_read=True', 'events_read=True']) {
    expect(service).toContain(capability);
  }
  expect(settings).not.toContain('ReadOnlyTokenBoundary');
  expect(candidate).toContain('/bugsink-2.6.3-venv/lib');
  expect(candidate).not.toContain('/Users/james/projects/bugsink-venv/lib');
});

test('Bugsink runtime-secret scanning stays bounded to Bugsink-generated evidence', () => {
  expect(gate).toContain("['scripts/bugsink/scan.py',evidence]");
  expect(gate).toContain('failureMode');
  expect(gate).toContain('failureReached');
  expect(service).toContain('failure-reached.json');
});
