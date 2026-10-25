/**
 * DA-02.3 — Instrument Frame, EXPLORATION (four structural candidates, A–D).
 *
 * The calibration grid is authoritative: `u` = the width of one CalibrationRail
 * index (DA-02.2). Every thickness, notch, break and padding below is a multiple
 * of `u`. Pure geometry: rectilinear only, no colour — the renderer maps the
 * three roles (chassis, structure, field) to monochrome tokens.
 *
 * Nothing here is a product API yet: the operator chooses one family first.
 */

export type FrameVariant = 'recessed' | 'indexed' | 'rail' | 'faceplate';

/** A straight segment, drawn with a stroke of `weight`. Axis-aligned by construction. */
export type Segment = { x1: number; y1: number; x2: number; y2: number; weight: 'primary' | 'secondary' };
/** A solid rectangle: structural mass (`structure`) or the recessed field (`field`). */
export type Block = { x: number; y: number; w: number; h: number; role: 'structure' | 'field' };

export type FrameGeometry = {
  width: number;
  height: number;
  u: number;
  /** stroke widths, in px */
  primary: number;
  secondary: number;
  segments: Segment[];
  blocks: Block[];
  /** where the instrument goes: never overlapped by structure */
  content: { x: number; y: number; w: number; h: number };
};

/** Stroke hierarchy from the brief: primary 0.5–0.75u, secondary 0.25–0.5u. */
export const PRIMARY_U = 0.6;
export const SECONDARY_U = 0.35;
/** Minimum internal padding from the brief. */
export const MIN_PADDING_U = 2;

type Frame = Omit<FrameGeometry, 'width' | 'height' | 'u' | 'primary' | 'secondary'>;

const h = (y: number, x1: number, x2: number, weight: Segment['weight']): Segment => ({ x1, y1: y, x2, y2: y, weight });
const v = (x: number, y1: number, y2: number, weight: Segment['weight']): Segment => ({ x1: x, y1, x2: x, y2, weight });

/** A closed rectangle as four segments, its stroke kept inside [0, W] × [0, H]. */
function perimeter(W: number, H: number, inset: number, weight: Segment['weight']): Segment[] {
  const a = inset;
  return [h(a, a, W - a, weight), v(W - a, a, H - a, weight), h(H - a, a, W - a, weight), v(a, a, H - a, weight)];
}

/** Remove [from, to] from a horizontal or vertical segment list (a structural break). */
function breakAt(segs: Segment[], target: number, from: number, to: number): Segment[] {
  return segs.flatMap((s) => {
    if (s !== segs[target]) return [s];
    const horizontal = s.y1 === s.y2;
    const lo = horizontal ? Math.min(s.x1, s.x2) : Math.min(s.y1, s.y2);
    const hi = horizontal ? Math.max(s.x1, s.x2) : Math.max(s.y1, s.y2);
    const parts: [number, number][] = [
      [lo, Math.max(lo, from)],
      [Math.min(hi, to), hi],
    ];
    return parts
      .filter(([a, b]) => b - a > 0)
      .map(([a, b]) => (horizontal ? h(s.y1, a, b, s.weight) : v(s.x1, a, b, s.weight)));
  });
}

/**
 * A — RECESSED. Thin perimeter, one recessed inner field, restrained corner
 * reinforcement, one small intentional break (top edge, right of centre).
 */
function frameA(W: number, H: number, u: number, p: number): Frame {
  const edge = perimeter(W, H, p / 2, 'primary');
  const segments = breakAt(edge, 0, W - 7 * u, W - 5 * u);
  const leg = 2.5 * u;
  const t = 0.75 * u;
  const corners: Block[] = [
    { x: 0, y: 0, w: leg, h: t, role: 'structure' }, { x: 0, y: 0, w: t, h: leg, role: 'structure' },
    { x: W - leg, y: 0, w: leg, h: t, role: 'structure' }, { x: W - t, y: 0, w: t, h: leg, role: 'structure' },
    { x: 0, y: H - t, w: leg, h: t, role: 'structure' }, { x: 0, y: H - leg, w: t, h: leg, role: 'structure' },
    { x: W - leg, y: H - t, w: leg, h: t, role: 'structure' }, { x: W - t, y: H - leg, w: t, h: leg, role: 'structure' },
  ];
  const r = 1.5 * u; // the recess
  const field: Block = { x: r, y: r, w: W - 2 * r, h: H - 2 * r, role: 'field' };
  const pad = r + MIN_PADDING_U * u;
  return { segments, blocks: [field, ...corners], content: { x: pad, y: pad, w: W - 2 * pad, h: H - 2 * pad } };
}

/**
 * B — INDEXED. A 1u targeting notch cut into the top edge — the markers' slot —
 * aligned on the grid; one interrupted edge (bottom, right); nothing else.
 */
function frameB(W: number, H: number, u: number, p: number): Frame {
  const a = p / 2;
  const nx = 6 * u; // the notch sits on the grid, 6u from the left: one marker width
  const depth = 1.5 * u;
  const top: Segment[] = [
    h(a, a, nx, 'primary'),
    v(nx, a, a + depth, 'primary'),
    h(a + depth, nx, nx + u, 'primary'),
    v(nx + u, a, a + depth, 'primary'),
    h(a, nx + u, W - a, 'primary'),
  ];
  const sides = [v(W - a, a, H - a, 'primary'), h(H - a, a, W - a, 'primary'), v(a, a, H - a, 'primary')];
  const segments = [...top, ...breakAt(sides, 1, W - 9 * u, W - 6 * u)];
  // padding is measured from the stroke's EDGE (axis + half stroke), not its axis
  const pad = a + depth + p / 2 + MIN_PADDING_U * u;
  return { segments, blocks: [], content: { x: pad, y: pad, w: W - 2 * pad, h: H - 2 * pad } };
}

/**
 * C — RAIL-MOUNTED. The bottom edge is a mounting rail (1u, the index width),
 * two registration marks rise from it like rail indexes; the rest is a quiet
 * secondary line.
 */
function frameC(W: number, H: number, u: number, s: number): Frame {
  const a = s / 2;
  const rail: Block = { x: 0, y: H - u, w: W, h: u, role: 'structure' };
  const marks: Block[] = [
    { x: 3 * u, y: H - 2.6 * u, w: u, h: 1.6 * u, role: 'structure' },
    { x: W - 4 * u, y: H - 2.6 * u, w: u, h: 1.6 * u, role: 'structure' },
  ];
  const segments = [h(a, a, W - a, 'secondary'), v(W - a, a, H - u, 'secondary'), v(a, a, H - u, 'secondary')];
  const pad = MIN_PADDING_U * u + s; // from the stroke's edge
  const bottom = 2.6 * u + MIN_PADDING_U * u;
  return { segments, blocks: [rail, ...marks], content: { x: pad, y: pad, w: W - 2 * pad, h: H - pad - bottom } };
}

/**
 * D — ASYMMETRIC FACEPLATE. A reinforced spine on the left (1u) turning into
 * the top-left corner; one structural interruption on the opposite (right) side;
 * a large uninterrupted field. Nothing else.
 */
function frameD(W: number, H: number, u: number, s: number): Frame {
  const a = s / 2;
  const spine: Block[] = [
    { x: 0, y: 0, w: u, h: H, role: 'structure' },
    { x: 0, y: 0, w: 5 * u, h: u, role: 'structure' },
  ];
  const right = v(W - a, a, H - a, 'secondary');
  const mid = H / 2;
  const segments = [
    h(a, 5 * u, W - a, 'secondary'),
    ...breakAt([right], 0, mid - 2 * u, mid + 2 * u),
    h(H - a, u, W - a, 'secondary'),
  ];
  const left = u + 2.5 * u;
  const pad = MIN_PADDING_U * u + u;
  return { segments, blocks: spine, content: { x: left, y: pad, w: W - left - pad, h: H - 2 * pad } };
}

export function frameGeometry(variant: FrameVariant, width: number, height: number, u: number): FrameGeometry {
  const primary = PRIMARY_U * u;
  const secondary = SECONDARY_U * u;
  const build = { recessed: frameA, indexed: frameB, rail: frameC, faceplate: frameD }[variant];
  const f = build(width, height, u, variant === 'rail' || variant === 'faceplate' ? secondary : primary);
  return { width, height, u, primary, secondary, ...f };
}
