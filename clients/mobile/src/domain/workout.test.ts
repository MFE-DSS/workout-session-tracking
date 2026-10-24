import rawFixture from '../fixtures/lab_fixture.json';
import type { LabFixture, SessionPlan } from './types';
import { canValidate, draftFor, Event, initialState, reduce, WorkoutState } from './workout';

const fixture = rawFixture as unknown as LabFixture;
const T0 = 1_800_000_000_000;
const at = (ms: number) => ({ epochMs: ms, estimated: false });

function run(state: WorkoutState, ...events: Event[]): WorkoutState {
  return events.reduce(reduce, state);
}

function start(plan: SessionPlan): WorkoutState {
  return reduce(initialState, { type: 'START', plan, nowMs: T0 });
}

describe('the instrument follows the server, it does not decide', () => {
  const plan = fixture.plans['push-a'];

  test('START opens the first set of the materialised plan', () => {
    const s = start(plan);
    expect(s.phase).toBe('SET');
    expect(s.cursorSetId).toBe(plan.sets[0].set_id);
  });

  test('the first set shows the server prefill; validating it opens REST with the default duration', () => {
    const s = start(plan);
    const first = plan.sets[0].set_id;
    const ex = plan.exercises[0];
    expect(draftFor(s, first)).toEqual({ weight: ex.prefill.weight_kg, reps: ex.prefill.reps });
    const r = reduce(s, { type: 'VALIDATED', setId: first, performedAt: at(T0 + 5000), nowMs: T0 + 5000 });
    expect(r.phase).toBe('REST');
    expect(r.rest!.deadlineMs).toBe(T0 + 5000 + plan.rest_default_seconds * 1000);
    expect(r.rest!.after).toEqual(plan.on_complete[String(first)]);
    expect(r.done[first].local).toBe('pending_local');
  });

  test('a later set repeats the last validated set of the same exercise (D6, lab presentation rule)', () => {
    const [s1, s2] = plan.sets;
    const s = run(
      start(plan),
      { type: 'ADJUST', setId: s1.set_id, field: 'weight', delta: 1 },
      { type: 'VALIDATED', setId: s1.set_id, performedAt: at(T0), nowMs: T0 },
      { type: 'REST_END', nowMs: T0 + 90_000 },
    );
    const expectedWeight = (plan.exercises[0].prefill.weight_kg as number) + 2.5;
    expect(s.cursorSetId).toBe(s2.set_id);
    expect(draftFor(s, s2.set_id).weight).toBe(expectedWeight);
  });

  test('it follows the transition table even where it could never derive the jump itself', () => {
    const [a, b] = plan.sets;
    const far = plan.sets[plan.sets.length - 1];
    const twisted: SessionPlan = {
      ...plan,
      on_complete: { ...plan.on_complete, [String(a.set_id)]: { kind: 'REST_THEN_EXERCISE', se_id: far.se_id, set_id: far.set_id } },
    };
    const s = run(start(twisted),
      { type: 'VALIDATED', setId: a.set_id, performedAt: at(T0), nowMs: T0 },
      { type: 'REST_END', nowMs: T0 + 1 });
    expect(s.cursorSetId).toBe(far.set_id);
    expect(s.cursorSetId).not.toBe(b.set_id);
  });

  test('a whole nominal workout needs no navigation event: validate, rest ends, repeat — then COMPLETE', () => {
    let s = start(plan);
    let clock = T0;
    let restEnds = 0;
    for (const set of plan.sets) {
      expect(s.phase).toBe('SET');
      expect(s.cursorSetId).toBe(set.set_id);
      clock += 40_000;
      s = reduce(s, { type: 'VALIDATED', setId: set.set_id, performedAt: at(clock), nowMs: clock });
      if (s.phase === 'REST') {
        clock = s.rest!.deadlineMs;
        s = reduce(s, { type: 'REST_END', nowMs: clock });
        restEnds += 1;
      }
    }
    expect(s.phase).toBe('COMPLETE');
    expect(restEnds).toBe(plan.sets.length - 1);
    expect(Object.keys(s.done)).toHaveLength(plan.sets.length);
    expect(s.completedMs).toBe(clock);
  });

  test('after the last set of an exercise, REST then the next exercise opens by itself (D5)', () => {
    const firstEx = plan.exercises[0].se_id;
    const lastOfFirst = plan.sets.filter((x) => x.se_id === firstEx).at(-1)!;
    expect(plan.on_complete[String(lastOfFirst.set_id)].kind).toBe('REST_THEN_EXERCISE');
  });
});

describe('refusals and boundaries', () => {
  const plan = fixture.plans['catch-up-shoulders'];

  test('a first-time exercise with no weight cannot be validated, and nothing changes', () => {
    const s = start(plan);
    const first = plan.sets[0].set_id;
    expect(canValidate(draftFor(s, first))).toBe(false);
    const r = reduce(s, { type: 'VALIDATED', setId: first, performedAt: at(T0), nowMs: T0 });
    expect(r).toBe(s);
  });

  test('a set that is not the current one is ignored', () => {
    const s = start(fixture.plans['push-a']);
    const r = reduce(s, { type: 'VALIDATED', setId: fixture.plans['push-a'].sets[2].set_id, performedAt: at(T0), nowMs: T0 });
    expect(r).toBe(s);
  });

  test('values are clamped: reps ≥ 1, weight ≥ 0, half-kilo grain', () => {
    const s = start(plan);
    const id = plan.sets[0].set_id;
    const r = run(s,
      { type: 'SET_VALUE', setId: id, field: 'weight', value: -4 },
      { type: 'SET_VALUE', setId: id, field: 'reps', value: 0 });
    expect(draftFor(r, id)).toEqual({ weight: 0, reps: 1 });
    expect(draftFor(reduce(r, { type: 'SET_VALUE', setId: id, field: 'weight', value: 12.74 }), id).weight).toBe(12.5);
  });

  test('a substitution is a REQUEST (REQUIRES_SYNC): the plan on the device is not changed', () => {
    const s = start(plan);
    const ex = plan.exercises[0];
    const r = reduce(s, { type: 'REQUEST_SUBSTITUTE', seId: ex.se_id, substitute: ex.substitutes[0] });
    expect(r.requiresSync[ex.se_id]).toEqual({ substitute: ex.substitutes[0] });
    expect(r.plan).toBe(s.plan);
    expect(r.plan!.exercises[0].executed_name).toBe(ex.executed_name);
  });

  test('rest shift never goes below now', () => {
    const p = fixture.plans['push-a'];
    const s = run(start(p),
      { type: 'VALIDATED', setId: p.sets[0].set_id, performedAt: at(T0), nowMs: T0 },
      { type: 'REST_SHIFT', deltaMs: -600_000, nowMs: T0 + 10_000 });
    expect(s.rest!.deadlineMs).toBe(T0 + 10_000);
  });

  test('a local commit result is recorded on the set, success or failure', () => {
    const p = fixture.plans['push-a'];
    const id = p.sets[0].set_id;
    const s = run(start(p), { type: 'VALIDATED', setId: id, performedAt: at(T0), nowMs: T0 });
    expect(reduce(s, { type: 'LOCAL_COMMIT', setId: id, ok: true }).done[id].local).toBe('saved_local');
    expect(reduce(s, { type: 'LOCAL_COMMIT', setId: id, ok: false }).done[id].local).toBe('not_saved');
  });
});

describe('the fixture is canonical output, not invention', () => {
  test('no duration estimate is carried (AUREN_INSTRUMENTS §6.2bis-3)', () => {
    expect(fixture.mission.duration_estimate).toBeNull();
  });

  test('every set of every plan has exactly one server transition', () => {
    for (const plan of Object.values(fixture.plans)) {
      for (const set of plan.sets) expect(plan.on_complete[String(set.set_id)]).toBeDefined();
      expect(Object.values(plan.on_complete).filter((t) => t.kind === 'BILAN')).toHaveLength(1);
    }
  });
});
