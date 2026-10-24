import { performedAt, withinServerBounds } from './performedAt';

const anchor = { serverMs: 1_800_000_000_000, monoMs: 5_000, processId: 'p1' };

describe('D11 integrity — never the raw wall clock alone', () => {
  test('execution time = server anchor + monotonic elapsed', () => {
    expect(performedAt(anchor, 65_000, 'p1', 0)).toEqual({ epochMs: anchor.serverMs + 60_000, estimated: false });
  });

  test('a wall clock moved by the user does not move the execution time', () => {
    const honest = performedAt(anchor, 65_000, 'p1', anchor.serverMs + 60_000);
    const skewed = performedAt(anchor, 65_000, 'p1', anchor.serverMs + 7 * 86_400_000);
    expect(skewed).toEqual(honest);
  });

  test('after a process restart the monotonic link is gone: the time is flagged estimated', () => {
    const t = performedAt(anchor, 3_000, 'p2', 1_800_000_100_000);
    expect(t).toEqual({ epochMs: 1_800_000_100_000, estimated: true });
  });

  test('a monotonic reading earlier than the anchor is not trusted', () => {
    expect(performedAt(anchor, 4_000, 'p1', 42).estimated).toBe(true);
  });
});

describe('the bounds the server applies', () => {
  const start = 1_000;
  const now = 10_000;

  test('inside the session and not in the future', () => {
    expect(withinServerBounds(5_000, start, now, null)).toBe(true);
    expect(withinServerBounds(999, start, now, null)).toBe(false);
    expect(withinServerBounds(10_001, start, now, null)).toBe(false);
  });

  test('non-decreasing within an exercise', () => {
    expect(withinServerBounds(5_000, start, now, 4_000)).toBe(true);
    expect(withinServerBounds(5_000, start, now, 6_000)).toBe(false);
  });
});
