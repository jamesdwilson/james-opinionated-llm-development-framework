import { test as base, expect } from '@playwright/test';
import { mkdtemp, rm } from 'node:fs/promises';
import { resolve, join } from 'node:path';
import { createTaskServer } from '../src/server.mjs';
export const test = base.extend<{ url: string; expectedErrors: number[] }>({
  url: async ({}, use) => {
    const dir = await mkdtemp(resolve('.tmp/browser-'));
    const server = createTaskServer({ databasePath: join(dir, 'tasks.sqlite') });
    const address = await server.listen();
    try { await use(`http://127.0.0.1:${address.port}`); }
    finally { await server.close(); await rm(dir, { recursive: true, force: true }); }
  },
  expectedErrors: async ({}, use) => { await use([]); },
  page: async ({ page, url, expectedErrors }, use) => {
    const errors: string[] = []; const statuses: number[] = []; let consoleErrors = 0;
    page.on('pageerror', e => errors.push(e.message));
    page.on('console', m => { if (m.type() === 'error') { if (/Failed to load resource: the server responded with a status of (400|403)/.test(m.text())) consoleErrors++; else errors.push(m.text()); } });
    page.on('response', r => { if (r.url().startsWith(url) && r.status() >= 400) statuses.push(r.status()); });
    page.on('requestfailed', r => errors.push(r.failure()?.errorText || 'request failed'));
    await use(page);
    expect(errors).toEqual([]); expect(statuses).toEqual(expectedErrors); expect(consoleErrors).toBeLessThanOrEqual(expectedErrors.length);
  },
});
export { expect };
