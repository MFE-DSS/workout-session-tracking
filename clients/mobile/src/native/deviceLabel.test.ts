import { DEVICE_LABEL_MAX, deviceLabel } from './deviceLabel';

describe('PLAT-01 — device session label', () => {
  it('names the real platform and model', () => {
    expect(deviceLabel({ platform: 'android', model: 'Pixel 8' })).toBe('AUREN · android · Pixel 8');
    expect(deviceLabel({ platform: 'ios', model: 'iPhone 15 Plus' })).toBe('AUREN · ios · iPhone 15 Plus');
  });

  it('never announces another platform', () => {
    expect(deviceLabel({ platform: 'android', model: 'SM-S921B' })).not.toMatch(/iPhone/);
  });

  it('keeps the platform alone when the model is unknown or blank', () => {
    expect(deviceLabel({ platform: 'android', model: null })).toBe('AUREN · android');
    expect(deviceLabel({ platform: 'android', model: '   ' })).toBe('AUREN · android');
  });

  it('stays within what the server keeps', () => {
    expect(deviceLabel({ platform: 'android', model: 'x'.repeat(200) })).toHaveLength(DEVICE_LABEL_MAX);
  });
});
