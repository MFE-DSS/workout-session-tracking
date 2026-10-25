import type { FamilyKey, LabFixture } from '../domain/types';
import rawFixture from '../fixtures/lab_fixture.json';
import { missionFor, nextAfter, planFor } from './persona';

const fx = rawFixture as unknown as LabFixture;
const done = [{ id: 1, atMs: 1, slug: 'x' }];
const all = (Object.keys(fx.onboarding.families) as FamilyKey[]).flatMap((family) =>
  fx.onboarding.families[family].sessions.map((s) => ({ family, s })));

describe('lab persona — the canonical fixture that applies to the person holding the phone', () => {
  test('no persona yet means first launch', () => {
    expect(missionFor(fx, null, [])).toBeNull();
  });

  test('every family offers real catalogue sessions to choose from', () => {
    for (const f of Object.values(fx.onboarding.families)) expect(f.sessions.length).toBeGreaterThan(0);
    expect(all.length).toBeGreaterThan(3);
  });

  test('a newcomer gets the session they chose, then what the engine proposed after it', () => {
    for (const { family, s } of all) {
      const persona = { kind: 'newcomer' as const, family, slug: s.slug };
      expect(missionFor(fx, persona, [])!.template.slug).toBe(s.slug);
      expect(planFor(fx, persona, [], s.slug)).toBe(s.plan);
      expect(nextAfter(fx, persona, [])).toBe(s.next_mission);
      expect(missionFor(fx, persona, done)).toBe(s.next_mission);
      expect(planFor(fx, persona, done, s.next_mission.template.slug)).toBe(s.next_plan);
      expect(nextAfter(fx, persona, done)).toBeNull();
    }
  });

  test('a newcomer never sees anyone’s history in a first plan', () => {
    for (const { s } of all) {
      expect(s.plan.exercises.every((e) => e.previous === null && e.best === null && e.prefill.weight_kg === null)).toBe(true);
    }
  });

  test('a persona from an older fixture replays the first launch instead of crashing', () => {
    expect(missionFor(fx, { kind: 'newcomer', family: 'upper', slug: 'gone' }, [])).toBeNull();
  });

  test('the seeded user keeps the first trial’s mission', () => {
    expect(missionFor(fx, { kind: 'seeded' }, [])).toBe(fx.mission);
    expect(planFor(fx, { kind: 'seeded' }, [], fx.mission.template.slug)).toBe(fx.plans[fx.mission.template.slug]);
  });
});
