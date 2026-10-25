/**
 * DA-GOV-01 — every governed fixture against its operator-approved baseline.
 *
 * A failure is not automatically a bug: it means VISUAL REVIEW REQUIRED. Only the
 * operator approves a new baseline (docs/strategy/AUREN_VISUAL_CONTRACT.md §5).
 */
import { expect, test } from '@playwright/test';

import { CONTRACT_FIXTURES } from '../src/ui/contract/fixtures';

for (const f of CONTRACT_FIXTURES) {
  test(`${f.contract} · ${f.id}`, async ({ page }) => {
    await page.goto(`/?fixture=${f.id}`);
    const fixture = page.getByTestId('contract-fixture');
    await expect(fixture).toBeVisible();
    await page.evaluate(() => document.fonts.ready);
    // DA-02.6 — a fitted readout measures itself first: capture only once every measurer is gone
    await expect(page.getByTestId('readout-measure')).toHaveCount(0);
    await expect(fixture).toHaveScreenshot(`${f.id}.png`);
  });
}

test('an unknown fixture is said, never rendered as a blank pass', async ({ page }) => {
  await page.goto('/?fixture=does-not-exist');
  await expect(page.getByTestId('contract-unknown')).toBeVisible();
});
