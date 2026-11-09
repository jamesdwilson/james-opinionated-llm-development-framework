import { expect } from '@playwright/test';
export async function driveNorthStar(page, expectedErrors, hold = () => Promise.resolve()) {
    await hold(); await page.getByRole('radio',{name:"Require another person's approval",exact:true}).check();
    await page.getByLabel('Task title',{exact:true}).fill('   '); expectedErrors.push(400); await page.getByRole('button',{name:'Create task'}).click(); await expect(page.locator('#title-error')).toHaveText('Task title is required.'); await hold();
    await page.getByLabel('Task title',{exact:true}).fill('Wash dishes'); await expect(page.locator('#title-error')).toBeEmpty(); await expect(page.getByLabel('Task title',{exact:true})).not.toHaveAttribute('aria-invalid','true'); await hold(); await page.getByRole('button',{name:'Create task'}).click(); await expect(page.getByRole('article')).toBeVisible(); await hold();
    await page.getByRole('button',{name:'Request completion'}).click(); await expect(page.getByTestId('task-status')).toContainText('Waiting'); await hold();
    await expect(page.getByRole('button',{name:'Approve completion'})).toHaveCount(0);
    await expect(page.getByRole('article')).toContainText('Switch “Acting as” to Sam to approve.');
    await page.getByLabel('Acting as').selectOption('Sam'); await expect(page.getByRole('article')).not.toContainText('Switch “Acting as”'); await expect(page.getByRole('button',{name:'Approve completion'})).toBeEnabled(); await hold(); await page.getByRole('button',{name:'Approve completion'}).click(); await expect(page.getByTestId('task-status')).toHaveText('Complete'); await hold();
    await page.reload(); await page.getByRole('article').scrollIntoViewIfNeeded(); await expect(page.getByRole('article').locator('li')).toHaveCount(3); await hold();
}
