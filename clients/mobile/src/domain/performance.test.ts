import { ExerciseResult, headline, lineReading, previousTop, sessionPerformance, setVerdict } from './performance';
import type { PlanExercise, SessionPlan } from './types';
import type { DoneSet } from './workout';

const at = { epochMs: 0, estimated: false } as unknown as DoneSet['performedAt'];
const doneSet = (weight: number, reps: number): DoneSet => ({ weight, reps, performedAt: at, local: 'saved_local' });

function exercise(se_id: number, over: Partial<PlanExercise> = {}): PlanExercise {
  return {
    se_id, code: `E${se_id}`, prescribed_name: `Ex ${se_id}`, executed_name: `Ex ${se_id}`,
    set_scheme: '3x8-12', rep_range: { min: 8, max: 12 }, guidance: null, previous: null,
    prefill: { weight_kg: null, reps: 8, origin: 'NONE' }, substitutes: [], zone: null, best: null, ...over,
  };
}

function plan(exs: PlanExercise[], setsPer = 2): SessionPlan {
  const sets = exs.flatMap((e) => Array.from({ length: setsPer }, (_, i) => ({ set_id: e.se_id * 10 + i, se_id: e.se_id, index: i + 1 })));
  return { session_id: 1, template_slug: 't', template_name: 'T', server_now: '', rest_default_seconds: 90, exercises: exs, sets, on_complete: {} };
}

describe('performance — what the session showed, never a grade', () => {
  test('there is no total, no points, no /100 anywhere in the result', () => {
    const p = sessionPerformance(plan([exercise(1)]), { 10: doneSet(40, 12) }, {});
    expect(Object.keys(p).sort()).toEqual(['exercises', 'firstMarks', 'records', 'setsDone', 'setsPlanned']);
  });

  test('the per-set reading is AUREN’s own: top, inside, below, no target', () => {
    expect(setVerdict(12, { min: 8, max: 12 })).toBe('top');
    expect(setVerdict(8, { min: 8, max: 12 })).toBe('range');
    expect(setVerdict(7, { min: 8, max: 12 })).toBe('below');
    expect(setVerdict(7, null)).toBe('free');
  });

  test('a first session posts first marks', () => {
    const p = sessionPerformance(plan([exercise(1), exercise(2)]), { 10: doneSet(40, 12), 20: doneSet(20, 12) }, {});
    expect(p.firstMarks.map((e) => e.top)).toEqual([{ weight: 40, reps: 12 }, { weight: 20, reps: 12 }]);
    expect(headline(p)).toBe('Premiers repères posés. AUREN sait maintenant d’où tu pars.');
  });

  test('a record is announced only when it beats the best ever RECORDED — never invented', () => {
    const ex = exercise(1, { best: { weight_kg: 50, reps: 10 }, previous: { relative: 'il y a 2 j', weights: '47.5 / 50', reps: '10 / 10' } });
    const equal = sessionPerformance(plan([ex]), { 10: doneSet(50, 10) }, {});
    expect(equal.records).toHaveLength(0);
    expect(equal.exercises[0].trend).toBe('held');
    expect(headline(equal)).toBe('Repères tenus.');
    const beat = sessionPerformance(plan([ex]), { 10: doneSet(50, 11) }, {});
    expect(beat.records).toHaveLength(1);
    expect(headline(beat)).toBe('Record battu.');
  });

  test('a replaced exercise is compared with nothing — its history belongs to another exercise', () => {
    const ex = exercise(1, { rep_range: { min: 10, max: 12 }, best: { weight_kg: 80, reps: 12 }, previous: { relative: 'hier', weights: '80', reps: '12' } });
    const r = sessionPerformance(plan([ex]), { 10: doneSet(30, 6) }, { 1: { substitute: 'Remplaçant' } }).exercises[0];
    expect(r.name).toBe('Remplaçant');
    expect(r.sets).toEqual(['free']);
    expect(r.trend).toBe('first');
    expect(r.previousTop).toBeNull();
  });

  test('more sets do not make a better session: volume is reported, not rewarded', () => {
    const ex = exercise(1);
    const few = sessionPerformance(plan([ex], 2), { 10: doneSet(40, 10) }, {});
    const many = sessionPerformance(plan([ex], 5), { 10: doneSet(40, 10), 11: doneSet(40, 10), 12: doneSet(40, 10) }, {});
    expect(headline(few)).toBe(headline(many));
  });

  test('the server’s previous strings are read as pairs', () => {
    expect(previousTop({ relative: '', weights: '47.5 / 50 / 50', reps: '10 / 8 / 9' })).toEqual({ weight: 50, reps: 9 });
    expect(previousTop(null)).toBeNull();
  });
});

describe('R13 — la lecture d’une ligne du bilan, contre la prescription', () => {
  const line = (sets: ExerciseResult['sets'], over: Partial<ExerciseResult> = {}): ExerciseResult => ({
    se_id: 1, name: 'Ex', replaced: null, sets, top: { weight: 40, reps: 10 }, trend: 'held',
    record: null, previousTop: null, previousBest: null, ...over,
  });

  test('toutes les séries au plafond de la fourchette : au-dessus', () => {
    expect(lineReading(line(['top', 'top', 'top']))).toBe('above');
  });
  test('la plupart sous la fourchette : en dessous', () => {
    expect(lineReading(line(['below', 'below', 'range']))).toBe('below');
  });
  test('sinon : conforme — une seule série faible ne fait pas une ligne faible', () => {
    expect(lineReading(line(['top', 'range', 'below']))).toBe('on');
    expect(lineReading(line(['below', 'top']))).toBe('on');
  });
  test('une première fois n’est jugée sur rien : repère posé', () => {
    expect(lineReading(line(['below', 'below'], { trend: 'first' }))).toBe('first');
  });
  test('un exercice remplacé ou sans fourchette n’est pas lu', () => {
    expect(lineReading(line(['top'], { replaced: 'Autre' }))).toBe('free');
    expect(lineReading(line(['free', 'free']))).toBe('free');
  });
});
