/**
 * Which lab user is holding the phone, and therefore which canonical fixture
 * applies. LAB ONLY — in the product the server answers « what now? ».
 *
 *  - no persona yet  → first launch (D13 onboarding);
 *  - newcomer        → the real newcomer who chose that catalogue session:
 *                      first session, then what the served engine proposed
 *                      once it was done;
 *  - seeded          → the two-week history user of the first N0 trial.
 *
 * Known lab limit: after the newcomer's SECOND session the fixture has no third
 * proposal; the second one is shown again.
 */
import type { DoneSession } from '../domain/adherence';
import type { LabFixture, Mission, OnboardingSession, SessionPlan } from '../domain/types';
import type { Persona } from './profile';

export type LabSession = DoneSession & { id: number };

export function firstMission(s: OnboardingSession): Mission {
  const phrase = 'Ta première séance, choisie à l’accueil.';
  const first = s.plan.exercises[0];
  return {
    state: 'READY',
    template: { slug: s.slug, name: s.name, subtitle: s.subtitle },
    reason: { phrase, reasons: [phrase], winning: [], limiting: [], horizon: 'premier lancement', provenance: 'choix' },
    alternatives: [],
    scope: {
      exercise_count: s.plan.exercises.length,
      work_set_count: s.plan.sets.length,
      first_exercise: { name: first.executed_name, set_scheme: first.set_scheme },
    },
    duration_estimate: null,
  };
}

export function sessionOf(fx: LabFixture, persona: Persona | null): OnboardingSession | undefined {
  if (persona?.kind !== 'newcomer') return undefined;
  return fx.onboarding.families[persona.family].sessions.find((s) => s.slug === persona.slug);
}

export function missionFor(fx: LabFixture, persona: Persona | null, sessions: LabSession[]): Mission | null {
  if (!persona) return null;
  if (persona.kind === 'seeded') return fx.mission;
  const s = sessionOf(fx, persona);
  if (!s) return null; // a stale persona from an older fixture: replay the first launch
  return sessions.length === 0 ? firstMission(s) : s.next_mission;
}

export function planFor(fx: LabFixture, persona: Persona | null, sessions: LabSession[], slug: string): SessionPlan | undefined {
  if (persona?.kind === 'newcomer') {
    const s = sessionOf(fx, persona);
    const own = s && (sessions.length === 0 ? s.plan : s.next_plan);
    return own?.template_slug === slug ? own : undefined;
  }
  return fx.plans[slug];
}

/** What the engine has prepared after THIS session — known only for the newcomer's first. */
export function nextAfter(fx: LabFixture, persona: Persona | null, before: LabSession[]): Mission | null {
  if (before.length > 0) return null;
  return sessionOf(fx, persona)?.next_mission ?? null;
}
