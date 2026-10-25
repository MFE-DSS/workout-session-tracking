import { railBlocks } from './CalibrationRail';
import type { Density } from './layout';

const DENSITIES: Density[] = ['compact', 'regular', 'expanded'];

describe('DA-02.4B.1 — the readout opt-out is presentation only', () => {
  it.each(DENSITIES)('%s: the default is the locked rendering', (density) => {
    expect(railBlocks(density, {})).toEqual({ zoneLabels: density === 'expanded', readout: density !== 'compact' });
    expect(railBlocks(density, { showReadout: true })).toEqual(railBlocks(density, {}));
  });

  it.each(DENSITIES)('%s: opting out removes the readout and nothing else', (density) => {
    expect(railBlocks(density, { showReadout: false })).toEqual({ ...railBlocks(density, {}), readout: false });
  });
});
