/**
 * D13 — the entry profile, LAB ONLY: kept on the device, never sent anywhere.
 *
 * Every field says why it is asked (spec §0quinquies, rule 2) and every field
 * can be skipped (rule 3). In the product these become additive columns, each
 * arriving WITH the calculation that reads it (rule 1, business slice 4) —
 * today only `sessionsPerWeek` (weekly goal) and `weightKg` have a reader.
 */
import type { FamilyKey } from '../domain/types';

export type Objective = 'muscle' | 'strength' | 'lean' | 'fitness';
export type Sex = 'male' | 'female' | 'undisclosed';
export type Experience = 'new' | 'lt1' | 'y1_3' | 'gt3';
export type DailyActivity = 'sitting' | 'moving' | 'physical';

export type Profile = {
  objective: Objective | null;
  family: FamilyKey;
  /** the catalogue session chosen for the first launch */
  slug: string | null;
  heightCm: number | null;
  weightKg: number | null;
  birthYear: number | null;
  sex: Sex | null;
  experience: Experience | null;
  dailyActivity: DailyActivity | null;
  sessionsPerWeek: number | null;
  tutorialDone: boolean;
  createdAtMs: number;
};

export type Persona = { kind: 'newcomer'; family: FamilyKey; slug: string } | { kind: 'seeded' };

export type Choice<T extends string> = { value: T; label: string; detail?: string };

export const OBJECTIVES: Choice<Objective>[] = [
  { value: 'muscle', label: 'Prendre du muscle', detail: 'Hypertrophie : du volume, des séries de 6 à 15 répétitions.' },
  { value: 'strength', label: 'Gagner en force', detail: 'Des charges plus lourdes, moins de répétitions.' },
  { value: 'lean', label: 'Sécher sans perdre de muscle', detail: 'Garder ta force pendant une perte de gras.' },
  { value: 'fitness', label: 'Me remettre en forme', detail: 'Reprendre et tenir, sans te blesser.' },
];

export const SEXES: Choice<Sex>[] = [
  { value: 'male', label: 'Homme' },
  { value: 'female', label: 'Femme' },
  { value: 'undisclosed', label: 'Je préfère ne pas répondre' },
];

export const EXPERIENCES: Choice<Experience>[] = [
  { value: 'new', label: 'Je débute' },
  { value: 'lt1', label: 'Moins d’un an' },
  { value: 'y1_3', label: '1 à 3 ans' },
  { value: 'gt3', label: 'Plus de 3 ans' },
];

export const ACTIVITIES: Choice<DailyActivity>[] = [
  { value: 'sitting', label: 'Plutôt assis' },
  { value: 'moving', label: 'Debout, en mouvement' },
  { value: 'physical', label: 'Travail physique' },
];

export const SESSIONS_PER_WEEK = [2, 3, 4, 5] as const;

/** Shown when the user skipped the question — said, never hidden. */
export const DEFAULT_SESSIONS_PER_WEEK = 3;

/** Why each field is asked, in one line, at the moment it is asked. */
export const WHY = {
  height: 'Pour les exercices au poids du corps et ta force relative.',
  weight: 'Pour tes charges de départ et ta force relative.',
  birthYear: 'Pour adapter les charges de départ et la récupération.',
  sex: 'Pour les repères de charge de départ.',
  experience: 'Le meilleur indicateur de ta charge de départ et de ton rythme de progrès.',
  dailyActivity: 'Ta fatigue hors de la salle compte dans ta récupération.',
  sessionsPerWeek: 'Pour fixer ton objectif de la semaine.',
} as const;

export function emptyProfile(family: FamilyKey, nowMs: number): Profile {
  return {
    objective: null, family, slug: null, heightCm: null, weightKg: null, birthYear: null, sex: null,
    experience: null, dailyActivity: null, sessionsPerWeek: null, tutorialDone: false, createdAtMs: nowMs,
  };
}

/** A number typed by hand: kept only when it is a plausible human value. */
export function plausible(field: 'heightCm' | 'weightKg' | 'birthYear', value: number | null, nowYear: number): number | null {
  if (value === null || !Number.isFinite(value)) return null;
  const range = { heightCm: [120, 230], weightKg: [35, 250], birthYear: [nowYear - 90, nowYear - 14] }[field];
  return value >= range[0] && value <= range[1] ? Math.round(value * 10) / 10 : null;
}
