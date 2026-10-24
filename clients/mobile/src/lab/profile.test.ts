import { emptyProfile, plausible, WHY } from './profile';

describe('entry profile — every field skippable, every field justified', () => {
  test('a fresh profile asks nothing and blocks nothing', () => {
    const p = emptyProfile('upper', 0);
    expect(Object.entries(p).filter(([k, v]) => v !== null && !['family', 'tutorialDone', 'createdAtMs'].includes(k))).toEqual([]);
    expect(p.slug).toBeNull();
  });

  test('every asked field carries its reason', () => {
    expect(Object.keys(WHY).sort()).toEqual(['birthYear', 'dailyActivity', 'experience', 'height', 'sessionsPerWeek', 'sex', 'weight']);
    for (const why of Object.values(WHY)) expect(why.length).toBeGreaterThan(10);
  });

  test('a mistyped number is dropped, not stored', () => {
    expect(plausible('heightCm', 182, 2026)).toBe(182);
    expect(plausible('heightCm', 18.2, 2026)).toBeNull();
    expect(plausible('weightKg', 82.35, 2026)).toBe(82.4);
    expect(plausible('birthYear', 1990, 2026)).toBe(1990);
    expect(plausible('birthYear', 2020, 2026)).toBeNull();
    expect(plausible('weightKg', null, 2026)).toBeNull();
  });
});
