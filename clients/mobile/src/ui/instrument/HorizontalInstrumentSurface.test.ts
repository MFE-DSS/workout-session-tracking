import { CALIBRATION_LINE_DEMO, selectedPositionOf, SURFACE_B1_FIXTURES } from '../contract/fixtures';
import { type } from '../theme';
import { surfaceLayout } from './HorizontalInstrumentSurface';

const layoutOf = (f: (typeof SURFACE_B1_FIXTURES)[number]) =>
  surfaceLayout({
    ...CALIBRATION_LINE_DEMO,
    width: f.width,
    height: f.height,
    selectedPosition: selectedPositionOf(f),
    selectedValue: f.selectedValue,
  });

describe('DA-02.4B.1 — the sovereign readout above the calibration line', () => {
  it.each(SURFACE_B1_FIXTURES.map((f) => [f.id, f] as const))('%s: the stack fits in the frame content', (_, f) => {
    const s = layoutOf(f);
    expect(s.fits).toBe(true);
  });

  it.each(SURFACE_B1_FIXTURES.map((f) => [f.id, f] as const))('%s: the rail keeps the full content width', (_, f) => {
    const s = layoutOf(f);
    expect(s.railWidth).toBe(Math.floor(s.frame.content.w));
    expect(s.rail.width).toBe(s.railWidth);
  });

  it('P2: the rail scale follows the density, never the DA-02.3 2× field scale', () => {
    const at = (w: number) => layoutOf(SURFACE_B1_FIXTURES.find((f) => f.width === w)!);
    expect(at(390).rail.u).toBe(4);
    expect(at(390).rail.density).toBe('expanded');
    expect(at(320).rail.u).toBe(3);
    expect(at(320).rail.density).toBe('regular');
  });

  it('the value takes the approved role for the surface size', () => {
    const at = (w: number) => layoutOf(SURFACE_B1_FIXTURES.find((f) => f.width === w)!);
    expect(at(390).value).toBe(type.readout);
    expect(at(320).value).toBe(type.figure);
  });

  it('D-B (i): the prescribed value sits under the whole rail block, zone names included', () => {
    const s390 = layoutOf(SURFACE_B1_FIXTURES.find((f) => f.width === 390)!);
    expect(s390.referenceTop).toBeGreaterThanOrEqual(s390.rail.height + 16);
    const s320 = layoutOf(SURFACE_B1_FIXTURES.find((f) => f.width === 320)!);
    expect(s320.referenceTop).toBeGreaterThanOrEqual(s320.rail.height);
  });
});
