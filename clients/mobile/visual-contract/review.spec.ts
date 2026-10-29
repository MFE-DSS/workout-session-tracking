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
    // DA-02.6 — a fitted readout measures itself first: capture only once every measurer is gone
    await expect(page.getByTestId('readout-measure')).toHaveCount(0);
    // same capture as toHaveScreenshot: css scale, no animation, no caret
    await fixture.screenshot({ path: path.join(OUT, `${f.id}.png`), scale: 'css', animations: 'disabled', caret: 'hide' });
    await fixture.screenshot({ path: path.join(OUT, `${f.id}@2x.png`), scale: 'device', animations: 'disabled', caret: 'hide' });

    const origin = await fixture.boundingBox();
    const rel = (b: Awaited<ReturnType<typeof box>>): Box | null =>
      b && origin ? { x: b.x - origin.x, y: b.y - origin.y, w: b.width, h: b.height } : null;
    const c = frameGeometry('rail', f.width, f.height, UNIT[densityFor(f.width)]).content;
    const content: Box = { x: PAD + c.x, y: PAD + c.y, w: c.w, h: c.h };
    const within = (b: Box | null, outer: Box) =>
      !b || (b.x >= outer.x - 0.5 && b.y >= outer.y - 0.5 && b.x + b.w <= outer.x + outer.w + 0.5 && b.y + b.h <= outer.y + outer.h + 0.5);
    const all = async (id: string) =>
      Promise.all((await fixture.getByTestId(id).all()).map(async (l) => rel(await l.boundingBox())));

    // DA-02.5 — Recessed Window candidates: inside Frame C, apart, every content inside its window
    const windows = (await all('recessed-window')).filter((b): b is Box => b !== null);
    if (windows.length) {
      const fields = (await all('recessed-content')).filter((b): b is Box => b !== null);
      const items = [...(await all('window-text')), ...(await all('window-value')), ...(await all('window-bodymap'))].filter(
        (b): b is Box => b !== null,
      );
      // a value pushed to its largest size must never be cut (ellipsis or clipping)
      const cut = await fixture
        .getByTestId('window-value')
        .evaluateAll((els) => els.filter((e) => e.scrollWidth > e.clientWidth + 1).length);
      // DA-04.1 — a zone label is clamped to two lines: it must fit them, never be cut
      const labelsCut = await fixture
        .getByTestId('window-text')
        .evaluateAll((els) => els.filter((e) => e.scrollHeight > e.clientHeight + 1 || e.scrollWidth > e.clientWidth + 1).length);
      const windowVerdict = {
        windowsInsideFrame: windows.every((w) => within(w, content)),
        windowsApart: windows.every((a, i) => windows.every((b, j) => i === j || !overlaps(a, b))),
        contentInsideItsWindow: items.every((it) => fields.some((fl) => within(it, fl))),
        valuesNotCut: cut === 0 && labelsCut === 0,
      };
      writeFileSync(path.join(OUT, `${f.id}.json`), JSON.stringify({ id: f.id, content, windows, fields, items, verdict: windowVerdict }, null, 2));
      expect(windowVerdict, `${f.id}: windows inside Frame C, apart, their content inside them, no value cut`).toEqual({
        windowsInsideFrame: true,
        windowsApart: true,
        contentInsideItsWindow: true,
        valuesNotCut: true,
      });
      return;
    }
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
    // DA-02.4B.3 — the − / + controls: under the frame, thumb-sized, apart from each other
    const minus = rel(await box(fixture.getByTestId('step-decrement')));
    const plus = rel(await box(fixture.getByTestId('step-increment')));
    const frameBottom = PAD + f.height;
    const controls = minus || plus ? { minus, plus } : null;
    const controlsVerdict = controls
      ? {
          controlsUnderFrame: [minus, plus].every((b) => b !== null && b.y >= frameBottom - 0.5),
          controlsThumbSized: [minus, plus].every((b) => b !== null && b.w >= 44 && b.h >= 44),
          controlsApart: !overlaps(minus, plus),
        }
      : {};
    writeFileSync(path.join(OUT, `${f.id}.json`), JSON.stringify({ ...measured, controls, verdict: { ...verdict, ...controlsVerdict } }, null, 2));
    expect(verdict, `${f.id}: content must stay inside the frame and the rail keep its full width`).toEqual({
      valueInside: true,
      railInside: true,
      referenceInside: true,
      referenceOverlapsTarget: false,
      railFullContentWidth: true,
    });
    if (controls) {
      expect(controlsVerdict, `${f.id}: the controls stay under the frame, thumb-sized and apart`).toEqual({
        controlsUnderFrame: true,
        controlsThumbSized: true,
        controlsApart: true,
      });
    }
  });
}
