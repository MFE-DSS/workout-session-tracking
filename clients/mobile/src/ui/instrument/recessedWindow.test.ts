import React from 'react';

import { densityFor, UNIT } from '../calibration/layout';
import { color } from '../theme';
import { frameGeometry, SECONDARY_U } from './frameGeometry';
import { RecessedWindow, WINDOW_ROLE } from './RecessedWindow';
import { recessedWindowGeometry, WINDOW_PADDING_U, WINDOW_STROKE_U, type WindowLayout, windowLayout } from './recessedWindowGeometry';

type Node = React.ReactElement<Record<string, unknown>>;
function walk(node: unknown, out: Node[] = []): Node[] {
  if (Array.isArray(node)) node.forEach((n) => walk(n, out));
  else if (React.isValidElement(node)) {
    out.push(node as Node);
    walk((node as Node).props.children, out);
  }
  return out;
}

const LAYOUTS: WindowLayout[] = ['single', 'pair', 'split-60-40'];
const SIZES: [number, number][] = [
  [390, 220],
  [320, 180],
];
const parent = (W: number, H: number) => {
  const u = UNIT[densityFor(W)];
  const c = frameGeometry('rail', W, H, u).content;
  return { u, content: { x: 0, y: 0, w: c.w, h: c.h } };
};
const inside = (a: { x: number; y: number; w: number; h: number }, b: { x: number; y: number; w: number; h: number }) =>
  a.x >= b.x - 1e-6 && a.y >= b.y - 1e-6 && a.x + a.w <= b.x + b.w + 1e-6 && a.y + a.h <= b.y + b.h + 1e-6;
const apart = (a: { x: number; w: number }, b: { x: number; w: number }) => a.x + a.w <= b.x || b.x + b.w <= a.x;

describe('RECESSED-WINDOW-V1 — the windows fit the parent: inside Frame C, apart, on the grid', () => {
  it.each(SIZES.flatMap(([W, H]) => LAYOUTS.map((l) => [W, H, l] as const)))('%i×%i %s: every window inside Frame C content, none overlapping', (W, H, layout) => {
    const { u, content } = parent(W, H);
    const boxes = windowLayout(layout, content, u);
    for (const b of boxes) expect(inside(b, content)).toBe(true);
    if (boxes.length === 2) {
      expect(apart(boxes[0], boxes[1])).toBe(true);
      expect(boxes[1].x - (boxes[0].x + boxes[0].w)).toBe(2 * u); // the gap is on the grid
    }
  });

  it.each(SIZES)('%i×%i: the 60/40 pair is 60/40 and stays inside Frame C', (W, H) => {
    const { u, content } = parent(W, H);
    const [a, b] = windowLayout('split-60-40', content, u);
    expect(a.w / (a.w + b.w)).toBeCloseTo(0.6, 1);
    expect(b.x + b.w).toBeLessThanOrEqual(content.w + 1e-6);
  });
});

describe('RECESSED-WINDOW-V1 — every structural measure is a multiple of u', () => {
  it.each([3, 4])('u = %i: one 3u break in the top edge, a 1u × 1.6u mark, 2u padding', (u) => {
    const W = 60 * u;
    const H = 40 * u;
    const g = recessedWindowGeometry(W, H, u);
    const top = g.segments.filter((s) => s.y1 === s.y2 && s.y1 < u);
    expect(top).toHaveLength(2);
    expect(top[1].x1 - top[0].x2).toBeCloseTo(3 * u);
    expect(g.segments).toHaveLength(5); // a closed outline, broken once
    expect(g.blocks).toEqual([{ x: 0, y: H - 1.6 * u, w: u, h: 1.6 * u, role: 'structure' }]);
    expect(g.content.y).toBeCloseTo(WINDOW_PADDING_U * u + g.stroke);
  });
});

describe('RECESSED-WINDOW-V1 — content always sits inside its window', () => {
  it.each(SIZES.flatMap(([W, H]) => LAYOUTS.map((l) => [W, H, l] as const)))('%i×%i %s', (W, H, layout) => {
    const { u, content } = parent(W, H);
    for (const b of windowLayout(layout, content, u)) {
      const g = recessedWindowGeometry(b.w, b.h, u);
      expect(g.content.w).toBeGreaterThan(0);
      expect(g.content.h).toBeGreaterThan(0);
      expect(inside(g.content, { x: 0, y: 0, w: b.w, h: b.h })).toBe(true);
      for (const blk of g.blocks) expect(inside(blk, { x: 0, y: 0, w: b.w, h: b.h })).toBe(true);
    }
  });
});

describe('RECESSED-WINDOW-V1 — quieter than Frame C, monochrome, no card', () => {
  it("its line is thinner than Frame C's secondary stroke, and never ink3", () => {
    expect(WINDOW_STROKE_U).toBeLessThan(SECONDARY_U);
    expect(WINDOW_ROLE.line).not.toBe(color.ink3);
  });

  it('no semantic colour: a window carries no state', () => {
    const semantic = [color.signal, color.system, color.alert, color.perfAbove, color.perfBelow];
    for (const v of Object.values(WINDOW_ROLE)) expect(semantic).not.toContain(v);
    for (const v of Object.values(WINDOW_ROLE)) expect(Object.values(color)).toContain(v);
  });

  it('no rounded corner, every colour painted is a window role', () => {
    const allowed = new Set<string>(Object.values(WINDOW_ROLE));
    for (const n of walk(RecessedWindow({ width: 180, height: 150 }))) {
      expect(JSON.stringify(n.props.style ?? {})).not.toMatch(/[Rr]adius/);
      expect(n.props.rx ?? 0).toBe(0);
      for (const key of ['fill', 'stroke']) {
        const v = n.props[key];
        if (typeof v === 'string') expect(allowed.has(v)).toBe(true);
      }
    }
  });
});
