import { sessionsThisWeek, weekStartMs, weeksHeld } from './adherence';

const day = (y: number, m: number, d: number, h = 18) => new Date(y, m - 1, d, h).getTime();
const s = (atMs: number) => ({ atMs, slug: 'x' });

describe('adherence to the agreed programme — planned rest counts, extra sessions earn nothing', () => {
  test('the week starts on Monday, local time', () => {
    const thu = day(2026, 10, 22);
    expect(new Date(weekStartMs(thu)).getDay()).toBe(1);
    expect(sessionsThisWeek([s(day(2026, 10, 18)), s(day(2026, 10, 19)), s(day(2026, 10, 21))], thu)).toBe(2);
  });

  test('a held week is one that reached its plan; rest days in between never matter', () => {
    // plan 3/week; two weeks held (Mon, Thu, Sat each), with rest days between
    const sessions = [
      s(day(2026, 10, 12)), s(day(2026, 10, 15)), s(day(2026, 10, 17)),
      s(day(2026, 10, 19)), s(day(2026, 10, 22)), s(day(2026, 10, 24)),
    ];
    expect(weeksHeld(sessions, day(2026, 10, 24, 20), 3)).toBe(2);
  });

  test('the current week, not yet held, does not break the count of finished weeks', () => {
    const sessions = [s(day(2026, 10, 12)), s(day(2026, 10, 15)), s(day(2026, 10, 17)), s(day(2026, 10, 20))];
    expect(weeksHeld(sessions, day(2026, 10, 21), 3)).toBe(1);
  });

  test('sessions beyond the plan earn nothing more', () => {
    const plan = [s(day(2026, 10, 19)), s(day(2026, 10, 21)), s(day(2026, 10, 23))];
    const extra = [...plan, s(day(2026, 10, 20)), s(day(2026, 10, 22)), s(day(2026, 10, 24))];
    const now = day(2026, 10, 25);
    expect(weeksHeld(extra, now, 3)).toBe(weeksHeld(plan, now, 3));
  });

  test('a missed week ends the count; no plan, no count', () => {
    const sessions = [s(day(2026, 10, 5)), s(day(2026, 10, 7)), s(day(2026, 10, 9)), s(day(2026, 10, 19)), s(day(2026, 10, 21)), s(day(2026, 10, 23))];
    expect(weeksHeld(sessions, day(2026, 10, 24), 3)).toBe(1);
    expect(weeksHeld(sessions, day(2026, 10, 24), 0)).toBe(0);
  });
});
