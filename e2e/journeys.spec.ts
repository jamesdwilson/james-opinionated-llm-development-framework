import { driveNorthStar } from './review-driver';
import { test, expect } from './fixture';
import type { Page } from '@playwright/test';
export async function create(page: Page) {
  await page.getByLabel('Task title', { exact: true }).fill('Wash dishes');
  await page.getByRole('radio', { name: "Require another person's approval", exact: true }).check();
  await page.getByRole('button', { name: 'Create task', exact: true }).click();
  await expect(page.getByRole('article')).toContainText('Wash dishes');
}
async function layout(page: Page) {
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  for (const button of await page.getByRole('button').all()) {
    await button.scrollIntoViewIfNeeded(); const box = await button.boundingBox();
    expect(box!.width).toBeGreaterThanOrEqual(44); expect(box!.height).toBeGreaterThanOrEqual(44);
    expect(box!.x).toBeGreaterThanOrEqual(0); expect(box!.x + box!.width).toBeLessThanOrEqual(page.viewportSize()!.width);
  }
}
for (const viewport of [{ width: 390, height: 844 }, { width: 1280, height: 800 }]) {
  test(`J01-J03 creation approval reload provenance ${viewport.width}`, async ({ page, url, expectedErrors }) => {
    await page.setViewportSize(viewport); await page.goto(url); await create(page);
    const article = page.getByRole('article');
    await expect(article).toContainText('Created by Alex'); await expect(article).toContainText("Require another person's approval");
    await expect(article).toContainText('Open'); await expect(page.locator('body')).not.toContainText(/\b(Core|Required)\b/);
    const tasks = (await (await page.request.get(url + '/api/tasks')).json()).tasks; const id = tasks[0].id;
    await expect(article).toContainText(id); await page.reload(); await expect(article).toContainText(id);
    await layout(page); await page.getByRole('button', { name: 'Request completion' }).click();
    await expect(article).toContainText("Waiting for Sam's approval");
    const denied = await page.request.post(`${url}/api/tasks/${id}/approve`, { data: { actor: 'Alex' } });
    expect(denied.status()).toBe(403);
    expect((await denied.json()).error.message).toBe('Another household member must approve this completion.');
    await expect(article.getByRole('button', { name: 'Approve completion' })).toHaveCount(0);
    await expect(article).toContainText('Switch “Acting as” to Sam to approve.');
    await page.getByLabel('Acting as').selectOption('Sam'); await page.getByRole('button', { name: 'Approve completion' }).click();
    await expect(article.getByTestId('task-status')).toHaveText('Complete');
    await expect(page.getByRole('button', { name: 'Approve completion' })).toHaveCount(0);
    const repeated = await page.request.post(`${url}/api/tasks/${id}/approve`, { data: { actor: 'Sam' } });
    expect((await repeated.json()).idempotent).toBe(true);
    await page.reload(); await expect(article.getByTestId('task-status')).toHaveText('Complete');
    const events = (await (await page.request.get(`${url}/api/tasks/${id}/events`)).json()).events;
    expect(events.map(e => [e.type, e.actor])).toEqual([['task.created','Alex'],['task.completion_requested','Alex'],['task.approved','Sam']]);
    await expect(article.locator('li')).toHaveCount(3);
    for (let i=0;i<3;i++) { await expect(article.locator('li').nth(i)).toContainText(events[i].actor); await expect(article.locator('time').nth(i)).toHaveAttribute('datetime',events[i].occurredAt); await expect(article.locator('time').nth(i)).toHaveText(events[i].occurredAt); }
    await layout(page);
  });
}
test('J04 keyboard validation and direct completion recovery', async ({ page, url, expectedErrors }) => {
  await page.goto(url);
  await page.waitForFunction(() => typeof document.querySelector('form')?.onsubmit === 'function');
  const title = page.getByLabel('Task title', { exact: true });
  await page.keyboard.press('Tab'); await expect(page.getByLabel('Acting as')).toBeFocused();
  await page.keyboard.press('Tab'); await expect(title).toBeFocused();
  await page.keyboard.type('   '); await page.keyboard.press('Tab'); await page.keyboard.press('Space');
  await page.keyboard.press('Tab'); await expect(page.getByRole('button', { name: 'Create task' })).toBeFocused();
  expectedErrors.push(400); await page.keyboard.press('Enter');
  await expect(title).toBeFocused(); await expect(title).toHaveValue('   '); await expect(title).toHaveAttribute('aria-describedby','title-error'); await expect(title).toHaveAttribute('aria-invalid','true');
  await expect(page.getByRole('alert')).toHaveText('Task title is required.');
  await title.fill(''); expectedErrors.push(400); await page.getByRole('button', { name: 'Create task' }).click(); await expect(title).toBeFocused();
  await page.keyboard.type('Wash dishes');
  await expect(page.locator('#title-error')).toBeEmpty();
  await expect(title).not.toHaveAttribute('aria-invalid', 'true');
  await page.keyboard.press('Tab'); await page.keyboard.press('Tab'); await page.keyboard.press('Enter');
  await expect(page.getByRole('article')).toContainText('Wash dishes');
  await page.getByRole('button', { name: 'Request completion' }).focus(); await page.keyboard.press('Enter');
  await expect(page.getByTestId('task-status')).toHaveText('Complete'); await expect(page.getByRole('article').locator('li')).toHaveCount(2);
});
test('J05 cold choice cannot continue without selection', async ({ page, url }) => {
  await page.setViewportSize({ width:390,height:844 }); await page.goto(url+'/ambiguous');
  await page.getByLabel('Task title', { exact:true }).fill('Wash dishes');
  await expect(page.getByRole('radio',{name:'Core',exact:true})).not.toBeChecked(); await expect(page.getByRole('radio',{name:'Required',exact:true})).not.toBeChecked();
  await expect(page.getByRole('button',{name:'Create task'})).toBeDisabled();
  await page.getByLabel('Task title', {exact:true}).press('Enter');
  await expect(page.locator('input:checked')).toHaveCount(0); expect((await (await page.request.get(url+'/api/tasks')).json()).tasks).toEqual([]); await layout(page);
});

test('J06 observation driver mechanics without a model', async ({page,url,expectedErrors}) => {
  await page.goto(url); await driveNorthStar(page,expectedErrors);
});

test('J06 actor change refreshes pending approval capability and preserves entered work', async ({page,url}) => {
  await page.goto(url); await create(page);
  await page.getByRole('button', {name:'Request completion'}).click();
  await expect(page.getByTestId('task-status')).toHaveText("Waiting for Sam's approval");
  await page.getByLabel('Task title', {exact:true}).fill('Next task');
  await page.getByLabel('Acting as').selectOption('Sam');
  await expect(page.getByRole('article')).not.toContainText('Switch “Acting as”');
  await expect(page.getByRole('button', {name:'Approve completion'})).toBeEnabled();
  await expect(page.getByLabel('Task title', {exact:true})).toHaveValue('Next task');
  await page.getByRole('button', {name:'Approve completion'}).click();
  await expect(page.getByTestId('task-status')).toHaveText('Complete');
  await expect(page.getByRole('article').getByRole('heading', {name:'Wash dishes',exact:true})).toBeFocused();
});
