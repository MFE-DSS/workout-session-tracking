import { railBlocks } from './CalibrationRail';
import type { Density } from './layout';

const DENSITIES: Density[] = ['compact', 'regular', 'expanded'];

describe('DA-02.4B — the rail\'s opt-outs are presentation only', () => {
  it.each(DENSITIES)('%s: the default is the locked rendering', (density) => {
    expect(railBlocks(density, {})).toEqual({
      zoneLabels: density === 'expanded',
      readout: density !== 'compact',
      scale: true,
    });
    expect(railBlocks(density, { showReadout: true, showScale: true, showZoneLabels: true })).toEqual(
      railBlocks(density, {}),
    );
  });

  it.each(DENSITIES)('%s: opting out of the readout removes the readout and nothing else', (density) => {
    expect(railBlocks(density, { showReadout: false })).toEqual({ ...railBlocks(density, {}), readout: false });
  });

  it.each(DENSITIES)('%s: opting out of the scale removes the scale and nothing else', (density) => {
    expect(railBlocks(density, { showScale: false })).toEqual({ ...railBlocks(density, {}), scale: false });
  });

  it.each(DENSITIES)('%s: opting out of the zone names removes them and nothing else', (density) => {
    expect(railBlocks(density, { showZoneLabels: false })).toEqual({ ...railBlocks(density, {}), zoneLabels: false });
  });
});
