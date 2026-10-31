import { lastLoadKg, showsLastTime } from './lastTime';

const prev = (weights: string) => ({ relative: 'il y a 1 sem', weights, reps: '11 / 10 / 9' });

describe('DA-05.1 — la dernière fois', () => {
  it('reads the heaviest load of the last time', () => {
    expect(lastLoadKg(prev('52.5 / 52.5 / 52.5'))).toBe(52.5);
    expect(lastLoadKg(prev('50 / 52.5 / 47.5'))).toBe(52.5);
  });

  it('has no load when there is no last time or it cannot be read', () => {
    expect(lastLoadKg(null)).toBeNull();
    expect(lastLoadKg(prev(''))).toBeNull();
    expect(lastLoadKg(prev('— / —'))).toBeNull();
  });

  it('is hidden when the dial already shows the load of last time', () => {
    expect(showsLastTime(prev('52.5 / 52.5 / 52.5'), 52.5)).toBe(false);
  });

  it('is shown when the dial says something else — a change, or the athlete moving away', () => {
    expect(showsLastTime(prev('52.5 / 52.5 / 52.5'), 55)).toBe(true);
    expect(showsLastTime(prev('52.5 / 52.5 / 52.5'), null)).toBe(true);
  });

  it('is shown when the last time has no readable load, never invented', () => {
    expect(showsLastTime(prev('— / —'), 40)).toBe(true);
  });

  it('is never shown without a last time', () => {
    expect(showsLastTime(null, 40)).toBe(false);
  });
});
