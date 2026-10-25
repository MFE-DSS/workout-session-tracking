import { formatClock, isElapsed, remainingFraction, remainingMs, REST_MAX_MS, shift } from './timer';

const clock = { startedMs: 1_000_000, deadlineMs: 1_090_000 };

describe('deadline model — the truth is the deadline, never a counter', () => {
  test('remaining time depends only on the deadline and the current time', () => {
    expect(remainingMs(clock, 1_000_000)).toBe(90_000);
    expect(remainingMs(clock, 1_072_400)).toBe(17_600);
    expect(remainingMs(clock, 2_000_000)).toBe(0);
  });

  test('render cadence is irrelevant: skipping 59 seconds of frames gives the same answer', () => {
    const everyFrame = Array.from({ length: 60 }, (_, i) => remainingMs(clock, 1_000_000 + i * 1000)).at(-1);
    const oneFrame = remainingMs(clock, 1_059_000);
    expect(everyFrame).toBe(oneFrame);
  });

  test('coming back from the background after the deadline reads as elapsed, at once', () => {
    expect(isElapsed(clock, 1_090_000)).toBe(true);
    expect(isElapsed(clock, 1_089_999)).toBe(false);
  });

  test('±15 s moves the deadline, never below now, never past the cap', () => {
    expect(shift(clock, 15_000, 1_010_000).deadlineMs).toBe(1_105_000);
    expect(shift(clock, -15_000, 1_085_000).deadlineMs).toBe(1_085_000);
    expect(shift(clock, 99 * 60_000, 1_000_000).deadlineMs).toBe(1_000_000 + REST_MAX_MS);
  });

  test('the clock rounds UP: 0:00 only once the rest is really over', () => {
    expect(formatClock(90_000)).toBe('1:30');
    expect(formatClock(400)).toBe('0:01');
    expect(formatClock(0)).toBe('0:00');
    expect(formatClock(61_000)).toBe('1:01');
  });

  test('the ring proportion is bounded', () => {
    expect(remainingFraction(clock, 1_000_000)).toBe(1);
    expect(remainingFraction(clock, 1_045_000)).toBe(0.5);
    expect(remainingFraction(clock, 3_000_000)).toBe(0);
  });
});
