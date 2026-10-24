/**
 * What the session showed, exercise by exercise — LAB PROTOTYPE.
 *
 * Engine V2, ruling 11: there is NO single session score. Three concepts stay
 * separate and none is a grade: the decision trace (internal), PERFORMANCE
 * (each exercise against comparable personal history — this module) and
 * ADHERENCE to the agreed programme (`adherence.ts`). Nothing here rewards
 * extra sets, extra sessions or tonnage.
 *
 * A replaced exercise is compared with nothing: its history is another
 * exercise's (like with like, as `stats.last_time_by_exercise_code` does).
 */
import type { DoneSet } from './workout';
import type { PlanExercise, SessionPlan } from './types';

export type SetVerdict = 'top' | 'range' | 'below' | 'free';
export type Trend = 'up' | 'held' | 'down' | 'first';

export type Top = { weight: number; reps: number };

export type ExerciseResult = {
  se_id: number;
  name: string;
  replaced: string | null;
  sets: SetVerdict[];
  top: Top | null;
  /** against the last comparable session of the SAME exercise */
  trend: Trend | null;
  /** beats the best set ever recorded; `first` = nothing recorded before */
  record: 'record' | 'first' | null;
  previousTop: Top | null;
  previousBest: Top | null;
};

export type SessionPerformance = {
  exercises: ExerciseResult[];
  records: ExerciseResult[];
  firstMarks: ExerciseResult[];
  setsDone: number;
  setsPlanned: number;
};

export function setVerdict(reps: number, range: { min: number; max: number } | null): SetVerdict {
  if (!range) return 'free';
  if (reps >= range.max) return 'top';
  if (reps >= range.min) return 'range';
  return 'below';
}

export function better(a: Top, b: Top): boolean {
  return a.weight > b.weight || (a.weight === b.weight && a.reps > b.reps);
}

function topOf(sets: Top[]): Top | null {
  return sets.reduce<Top | null>((best, s) => (best === null || better(s, best) ? s : best), null);
}

/** `previous` arrives as the server's display strings: `47.5 / 47.5`, `10 / 9`. */
export function previousTop(prev: PlanExercise['previous']): Top | null {
  if (!prev) return null;
  const w = prev.weights.split('/').map((x) => Number(x.trim()));
  const r = prev.reps.split('/').map((x) => Number(x.trim()));
  const pairs = w.map((weight, i) => ({ weight, reps: r[i] })).filter((p) => Number.isFinite(p.weight) && Number.isFinite(p.reps));
  return topOf(pairs);
}

function trendOf(now: Top, before: Top | null): Trend {
  if (!before) return 'first';
  if (better(now, before)) return 'up';
  if (now.weight === before.weight && now.reps === before.reps) return 'held';
  return 'down';
}

export function sessionPerformance(
  plan: SessionPlan,
  done: Record<number, DoneSet>,
  replacedBySeId: Record<number, { substitute: string }>,
): SessionPerformance {
  const exercises: ExerciseResult[] = plan.exercises.map((ex) => {
    const replaced = replacedBySeId[ex.se_id]?.substitute ?? null;
    const sets = plan.sets.filter((s) => s.se_id === ex.se_id && done[s.set_id]).map((s) => done[s.set_id]);
    const top = topOf(sets.map((d) => ({ weight: d.weight, reps: d.reps })));
    const verdicts = sets.map((d) => (replaced ? 'free' : setVerdict(d.reps, ex.rep_range)));
    const previousBest = replaced || !ex.best ? null : { weight: ex.best.weight_kg, reps: ex.best.reps };
    const prevTop = replaced ? null : previousTop(ex.previous);
    let record: ExerciseResult['record'] = null;
    let trend: Trend | null = null;
    if (top) {
      if (previousBest === null) record = 'first';
      else if (better(top, previousBest)) record = 'record';
      trend = trendOf(top, prevTop);
    }
    return { se_id: ex.se_id, name: replaced ?? ex.executed_name, replaced, sets: verdicts, top, trend, record, previousTop: prevTop, previousBest };
  });
  const setsDone = Object.keys(done).filter((id) => plan.sets.some((s) => String(s.set_id) === id)).length;
  return {
    exercises,
    records: exercises.filter((e) => e.record === 'record'),
    firstMarks: exercises.filter((e) => e.record === 'first'),
    setsDone,
    setsPlanned: plan.sets.length,
  };
}

/** The agent's one line — what the session showed, never a grade. */
export function headline(p: SessionPerformance): string {
  const n = p.records.length;
  if (n) return n > 1 ? `${n} records battus.` : 'Record battu.';
  const worked = p.exercises.filter((e) => e.top);
  if (worked.length && p.firstMarks.length === worked.length) return 'Premiers repères posés. AUREN sait maintenant d’où tu pars.';
  const up = worked.filter((e) => e.trend === 'up').length;
  if (up) return up > 1 ? `En progrès sur ${up} exercices.` : 'En progrès sur un exercice.';
  if (worked.some((e) => e.trend === 'held')) return 'Repères tenus.';
  return 'Séance enregistrée.';
}
