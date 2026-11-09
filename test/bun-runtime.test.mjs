import { describe, expect, test } from 'bun:test';
import { readFile } from 'node:fs/promises';

const packageJson = JSON.parse(await readFile(new URL('../package.json', import.meta.url), 'utf8'));

describe('Bun-only lab runtime contract', () => {
  test('pins Bun 1.4.4 as the package and JavaScript runtime', () => {
    expect(packageJson.packageManager).toBe('bun@1.4.4');
    expect(packageJson.engines).toEqual({ bun: '1.4.4' });
  });

  test('contains no Node or npm runtime commands', () => {
    for (const [name, command] of Object.entries(packageJson.scripts)) {
      expect(command, `${name}: ${command}`).not.toMatch(/(^|[\s;&|])(node|npm|npx)(?=[\s;&|]|$)/);
    }
  });

  test('forces Playwright to execute under Bun', () => {
    expect(packageJson.scripts['test:browser']).toBe('bun x --bun playwright test e2e/journeys.spec.ts');
  });
});
