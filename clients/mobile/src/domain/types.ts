/**
 * Draft presentation contracts (Sx_AUREN_MOBILE_EXPERIENCE_VNEXT §8).
 *
 * These mirror `src/fixtures/lab_fixture.json`, produced by
 * `scripts/generate_fixtures.py` from the canonical FastAPI services. The client
 * READS these shapes; it never derives any of their values.
 */

export type Guidance = {
  state: string;
  intent_label: string;
  target_summary: string | null;
  reasons: string[];
  is_silent: boolean;
};

export type Prefill = {
  weight_kg: number | null;
  reps: number | null;
  origin: 'OVERLOAD_TARGET' | 'LAST_SET' | 'NONE';
};

export type PlanExercise = {
  se_id: number;
  code: string;
  prescribed_name: string;
  executed_name: string;
  set_scheme: string | null;
  rep_range: { min: number; max: number } | null;
  guidance: Guidance | null;
  previous: { relative: string; weights: string; reps: string } | null;
  prefill: Prefill;
  substitutes: string[];
  /**
   * Primary zone, by the server recap's own rule (`session_recap._zones_touched`).
   * The id is OPAQUE to the client: legacy codes today, the 15 canonical zones of
   * engine V2 tomorrow — the client never enumerates zones, it only shows labels.
   */
  zone: { zone: string; label: string } | null;
  /**
   * Rest after a set of this exercise, supplied by the read model (engine V2
   * derives it at prescription time). Absent → the plan's default. The client
   * never hardcodes a rest duration.
   */
  rest_seconds?: number | null;
  /** Best work set ever RECORDED for this exercise (same template, same code). */
  best: { weight_kg: number; reps: number } | null;
};

export type PlanSet = { set_id: number; se_id: number; index: number };

/** Server-computed nominal-path transition table (§8.8). Followed, never recomputed. */
export type Transition =
  | { kind: 'REST_THEN_SET'; set_id: number }
  | { kind: 'REST_THEN_EXERCISE'; se_id: number; set_id: number }
  | { kind: 'BILAN' };

export type SessionPlan = {
  session_id: number;
  template_slug: string;
  template_name: string;
  server_now: string;
  rest_default_seconds: number;
  exercises: PlanExercise[];
  sets: PlanSet[];
  on_complete: Record<string, Transition>;
};

export type Mission = {
  state: 'READY';
  template: { slug: string; name: string; subtitle: string | null };
  reason: {
    phrase: string;
    reasons: string[];
    winning: string[];
    limiting: string[];
    horizon: string;
    provenance: string;
  };
  alternatives: { slug: string; name: string; phrase: string }[];
  scope: {
    exercise_count: number;
    work_set_count: number;
    first_exercise: { name: string; set_scheme: string | null };
  };
  duration_estimate: null;
};

export type Recap = {
  work_sets_total: number;
  substitution_count: number;
  top_progression: unknown;
  zones_touched: { zone: string; label: string; sets: number }[];
};

export type FamilyKey = 'upper' | 'lower' | 'full';

/** D13 — one real newcomer per catalogue session, each on an empty history (generate_fixtures.py). */
export type OnboardingSession = {
  slug: string;
  name: string;
  subtitle: string | null;
  plan: SessionPlan;
  /** what the served engine proposes once that first session is done */
  next_mission: Mission;
  next_plan: SessionPlan;
};

/** A family groups the catalogue's sessions, in the served engine's order. */
export type OnboardingFamily = { label: string; sessions: OnboardingSession[] };

export type LabFixture = {
  generated_at: string;
  mission: Mission;
  plans: Record<string, SessionPlan>;
  recaps: Record<string, Recap>;
  onboarding: { families: Record<FamilyKey, OnboardingFamily> };
};
