/// <reference types="node" />
// Node types for this test only: it reads the slice's own sources to prove what they do not contain.
import { readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import React from 'react';

import { color } from '../theme';
import { FRAME_ROLE, InstrumentFrame, type InstrumentFrameProps } from './InstrumentFrame';
import { FIXTURES, fixtureContent, SIZES, VARIANTS } from './InstrumentFrameGallery';

type Node = React.ReactElement<Record<string, unknown>>;

/** Every element of a tree returned by the (hook-free) frame component. */
function walk(node: unknown, out: Node[] = []): Node[] {
  if (Array.isArray(node)) {
    node.forEach((n) => walk(n, out));
  } else if (React.isValidElement(node)) {
    out.push(node as Node);
    walk((node as Node).props.children, out);
  }
  return out;
}

const render = (p: InstrumentFrameProps) => walk(InstrumentFrame(p));
const CASES = VARIANTS.flatMap((v) => SIZES.flatMap(([w, h]) => FIXTURES.map((f) => [v, w, h, f] as const)));

describe('DA-02.3 — the frames render, with every fixture, at every size', () => {
  it.each(CASES)('%s %i×%i with %s: renders without crash and mounts the content', (variant, width, height, fixture) => {
    const content = fixtureContent(fixture);
    const tree = render({ variant, width, height, children: content });
    expect(tree.length).toBeGreaterThan(3);
    if (content) expect(tree.some((n) => n === content)).toBe(true);
  });

  it.each(VARIANTS)('%s: no generic border-radius anywhere in the frame', (variant) => {
    for (const n of render({ variant, width: 390, height: 220, children: fixtureContent('readout') })) {
      const style = JSON.stringify(n.props.style ?? {});
      expect(style).not.toMatch(/[Rr]adius/);
      expect(n.props.rx ?? 0).toBe(0);
      expect(n.props.ry ?? 0).toBe(0);
    }
  });

  it.each(VARIANTS)('%s: every colour it paints is one of the three existing roles', (variant) => {
    const allowed = new Set<string>(Object.values(FRAME_ROLE));
    for (const n of render({ variant, width: 320, height: 180 })) {
      for (const key of ['fill', 'stroke']) {
        const v = n.props[key];
        if (typeof v === 'string') expect(allowed.has(v)).toBe(true);
      }
    }
    for (const v of Object.values(FRAME_ROLE)) expect(Object.values(color)).toContain(v);
  });
});

describe('DA-02.3 — the slice adds no colour and no dependency', () => {
  const dir = __dirname;
  const sources = readdirSync(dir)
    .filter((f) => /\.tsx?$/.test(f) && !f.endsWith('.test.ts'))
    .map((f) => ({ f, src: readFileSync(join(dir, f), 'utf8') }));

  it('no hard-coded colour in any source of the slice (tokens only)', () => {
    for (const { f, src } of sources) {
      expect({ f, hex: src.match(/#[0-9a-fA-F]{3,8}\b/g) }).toEqual({ f, hex: null });
      expect({ f, rgb: /rgba?\(/.test(src) }).toEqual({ f, rgb: false });
    }
  });

  it('imports only what the client already uses: no new package', () => {
    const allowed = ['react', 'react-native', 'react-native-svg', 'react-native-safe-area-context'];
    for (const { f, src } of sources) {
      for (const [, mod] of src.matchAll(/from '([^']+)'/g)) {
        if (mod.startsWith('.')) continue;
        expect({ f, mod, ok: allowed.includes(mod) }).toEqual({ f, mod, ok: true });
      }
    }
  });
});
