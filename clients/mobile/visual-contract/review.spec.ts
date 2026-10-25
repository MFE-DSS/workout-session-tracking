/**
 * DA-02.4B.1 — every candidate fixture, captured for the operator's review.
 * Not a gate: it compares nothing. Approval is the operator's (AUREN_VISUAL_CONTRACT §5).
 *
 * Two captures per candidate: `<id>.png` at the gate's scale (what a baseline would be)
 * and `<id>@2x.png` at the device scale, to be LOOKED AT. Composed candidates are also
 * MEASURED in the rendered page into review-output/<id>.json — the layout is judged on
 * real geometry — and fail if anything leaves the frame's content field (STOP condition).
 */
import { writeFileSync } from 'node:fs';
import path from 'node:path';

import { expect, type Locator, test } from '@playwright/test';

import { densityFor, UNIT } from '../src/ui/calibration/layout';
import { CANDIDATE_FIXTURES } from '../src/ui/contract/candidates';
import { frameGeometry } from '../src/ui/instrument/frameGeometry';

const OUT = path.join(__dirname, 'review-output');
/** ContractFixtureScreen's page margin around the component. */
const PAD = 12;

type Box = { x: number; y: number; w: number; h: number };

async function box(l: Locator) {
  return (await l.count()) ? l.first().boundingBox() : null;
}

const overlaps = (a: Box | null, b: Box | null) =>
  Boolean(a && b && a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h);

if (CANDIDATE_FIXTURES.length === 0) {
  // between two iterations: everything reviewed was approved and moved to fixtures.ts
  test('no candidate to review', () => undefined);
}

for (const f of CANDIDATE_FIXTURES) {
  test(`${f.candidate} · ${f.id} (review)`, async ({ page }) => {
    await page.goto(`/?fixture=${f.id}`);
    const fixture = page.getByTestId('contract-candidate');
    await expect(fixture).toBeVisible();
    await page.evaluate(() => document.fonts.ready);
    // same capture as toHaveScreenshot: css scale, no animation, no caret
    await fixture.screenshot({ path: path.join(OUT, `${f.id}.png`), scale: 'css', animations: 'disabled', caret: 'hide' });
    await fixture.screenshot({ path: path.join(OUT, `${f.id}@2x.png`), scale: 'device', animations: 'disabled', caret: 'hide' });

    const origin = await fixture.boundingBox();
    const rel = (b: Awaited<ReturnType<typeof box>>): Box | null =>
      b && origin ? { x: b.x - origin.x, y: b.y - origin.y, w: b.width, h: b.height } : null;
    const c = frameGeometry('rail', f.width, f.height, UNIT[densityFor(f.width)]).content;
    const content: Box = { x: PAD + c.x, y: PAD + c.y, w: c.w, h: c.h };
    const measured = {
      id: f.id,
      content,
      value: rel(await box(fixture.getByTestId('surface-value'))),
      rail: rel(await box(fixture.getByTestId('surface-rail'))),
      reference: rel(await box(fixture.getByTestId('surface-reference'))),
      targetLabel: rel(await box(fixture.getByText('TARGET', { exact: true }))),
    };
    const inside = (b: Box | null) =>
      !b || (b.x >= content.x - 0.5 && b.y >= content.y - 0.5 && b.x + b.w <= content.x + content.w + 0.5 && b.y + b.h <= content.y + content.h + 0.5);
    const verdict = {
      valueInside: inside(measured.value),
      railInside: inside(measured.rail),
      referenceInside: inside(measured.reference),
      referenceOverlapsTarget: overlaps(measured.reference, measured.targetLabel),
      railFullContentWidth: measured.rail ? Math.abs(measured.rail.w - Math.floor(c.w)) < 0.5 : false,
    };
    writeFileSync(path.join(OUT, `${f.id}.json`), JSON.stringify({ ...measured, verdict }, null, 2));
    expect(verdict, `${f.id}: content must stay inside the frame and the rail keep its full width`).toEqual({
      valueInside: true,
      railInside: true,
      referenceInside: true,
      referenceOverlapsTarget: false,
      railFullContentWidth: true,
    });
  });
}
