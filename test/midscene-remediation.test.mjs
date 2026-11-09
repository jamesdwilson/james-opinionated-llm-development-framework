import { expect, test } from 'bun:test';
import { spawn } from 'node:child_process';
import { readFile } from 'node:fs/promises';
import { candidatePaths } from '../scripts/candidate.mjs';

const expectedOverrides = {
  '@midscene/playground': 'file:stubs/midscene-playground',
  'puppeteer-core': 'file:stubs/puppeteer-core',
  'js-yaml': '4.3.2',
  sharp: '0.35.5',
  uuid: '11.1.1',
  zod: '4.6.6',
};

test('Midscene Playwright review route uses fixed transitives and fail-closed unused-package stubs', async () => {
  const pkg = JSON.parse(await readFile('package.json', 'utf8'));
  expect(pkg.overrides).toEqual(expectedOverrides);

  const playgroundPackage = JSON.parse(
    await readFile('stubs/midscene-playground/package.json', 'utf8'),
  );
  const puppeteerPackage = JSON.parse(
    await readFile('stubs/puppeteer-core/package.json', 'utf8'),
  );
  expect(playgroundPackage).toMatchObject({
    name: '@midscene/playground',
    version: '1.17.4',
    private: true,
  });
  expect(puppeteerPackage).toMatchObject({
    name: 'puppeteer-core',
    version: '24.6.0',
    private: true,
  });

  const playgroundStub = await readFile(
    'stubs/midscene-playground/index.mjs',
    'utf8',
  );
  const puppeteerStub = await readFile('stubs/puppeteer-core/index.mjs', 'utf8');
  expect(playgroundStub).toContain('stub was imported');
  expect(puppeteerStub).toContain('stub was imported');

  const lock = await readFile('bun.lock', 'utf8');
  expect(lock).not.toContain('"basic-ftp": [');
  expect(lock).not.toContain('"extract-zip": [');
  expect(lock).toContain('"js-yaml": ["js-yaml@4.3.2"');
  expect(lock).toContain('"sharp": ["sharp@0.35.5"');
  expect(lock).toContain('"uuid": ["uuid@11.1.1"');
  expect(lock).toContain('"zod": ["zod@4.6.6"');
  expect(candidatePaths).toContain('stubs');

  const playwright = await import('@midscene/web/playwright');
  expect(typeof playwright.PlaywrightAiFixture).toBe('function');
});

test('the canonical stack audit gate accepts this empty current graph', async () => {
  const child = spawn(process.execPath, ['scripts/audit-block.mjs'], {
    cwd: process.cwd(),
    env: { PATH: '/opt/homebrew/bin:/usr/bin:/bin', HOME: process.env.HOME },
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  let stdout = '';
  let stderr = '';
  child.stdout.on('data', chunk => {
    stdout += chunk;
  });
  child.stderr.on('data', chunk => {
    stderr += chunk;
  });
  const exit = await new Promise(resolve => {
    child.once('error', () => resolve(1));
    child.once('close', code => resolve(code ?? 1));
  });
  expect(exit).toBe(0);
  expect(stderr).toBe('');
  expect(JSON.parse(stdout)).toEqual({
    passed: true,
    advisories: 0,
    audit: {},
  });
});
