import type { PlanExercise, SessionPlan } from '../../domain/types';
import type { WorkoutState } from '../../domain/workout';
import { zonePanelPresets, zonesDone } from './zonesDone';

const ex = (se_id: number, zone: string | null, label = zone ?? '') =>
  ({ se_id, zone: zone ? { zone, label } : null }) as unknown as PlanExercise;

function stateWith(exercises: PlanExercise[], sets: [number, number][], done: number[]): WorkoutState {
  const plan = { exercises, sets: sets.map(([set_id, se_id]) => ({ set_id, se_id })) } as unknown as SessionPlan;
  return { plan, done: Object.fromEntries(done.map((id) => [id, {}])) } as unknown as WorkoutState;
}

describe('COMPLETE — the zones a session worked', () => {
  const exercises = [ex(1, 'pecs', 'Pectoraux'), ex(2, 'triceps', 'Triceps'), ex(3, null), ex(4, 'pecs', 'Pectoraux')];
  const sets: [number, number][] = [[10, 1], [11, 1], [20, 2], [30, 3], [40, 4], [41, 4]];

  it('counts DONE sets only, per primary zone, most first', () => {
    const z = zonesDone(stateWith(exercises, sets, [10, 11, 20, 30, 40]));
    expect(z).toEqual([
      { zone: 'pecs', label: 'Pectoraux', sets: 3 },
      { zone: 'triceps', label: 'Triceps', sets: 1 },
    ]);
  });

  it('an exercise without a known zone adds no zone', () => {
    expect(zonesDone(stateWith(exercises, sets, [30]))).toEqual([]);
  });

  it('names each window with its zone and its count of sets done', () => {
    const p = zonePanelPresets([{ zone: 'pecs', sets: 9 }, { zone: 'delt_lat', sets: 6 }]);
    expect(p.map((q) => q.label)).toEqual(['Pectoraux · 9', 'Deltoïdes latéraux · 6']);
    expect(p.map((q) => q.zone)).toEqual(['pecs', 'delt_lat']);
  });

  it('a zone outside the taxonomy draws no window', () => {
    expect(zonePanelPresets([{ zone: 'unknown', sets: 2 }])).toEqual([]);
  });
});
