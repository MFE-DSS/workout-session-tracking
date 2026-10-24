/**
 * D9 — the two server read models (`/api/mobile/v1`), as the server returns them.
 *
 * The execution plan IS the lab's `SessionPlan`, plus what only the server
 * knows: the canonical lifecycle, the sets it already holds, where to resume.
 */
import type { Mission, SessionPlan } from '../domain/types';

export type Decision = {
  fingerprint: string | null;
  policy: string | null;
  top: string;
  alternatives: string[];
};

export type ReadyMission = Omit<Mission, 'scope' | 'alternatives'> & {
  alternatives: { slug: string; name: string; phrase: string; executable: boolean }[];
  scope: Omit<Mission['scope'], 'first_exercise'> & {
    first_exercise: Mission['scope']['first_exercise'] | null;
  };
  executable: boolean;
  decision: Decision;
  primary_action: 'START' | null;
};

export type ResumeMission = {
  state: 'RESUME';
  session: { id: number; template_slug: string; name: string; subtitle: string | null; started_at: string };
  position: {
    exercise_index: number;
    exercise_total: number;
    sets_done: number;
    sets_total: number;
    exercise_name: string | null;
    set_index: number | null;
  } | null;
  primary_action: 'RESUME';
};

export type ServerMission = ReadyMission | ResumeMission | { state: 'NO_MISSION'; primary_action: null };

export type ServerDoneSet = { weight_kg: number | null; reps: number; performed_at: string | null };

export type ExecutionPlan = SessionPlan & {
  status: 'in_progress' | 'completed';
  excluded_from_stats: boolean;
  started_at: string;
  ended_at: string | null;
  done: Record<string, ServerDoneSet>;
  cursor_set_id: number | null;
  allowed_actions: string[];
};

export type TokenPair = {
  token_type: 'Bearer';
  access_token: string;
  access_expires_in: number;
  refresh_token: string;
  server_now: string;
};

/** A mission that the instrument can open: READY with something to execute. */
export function isStartable(m: ServerMission | null): m is ReadyMission & { scope: Mission['scope'] } {
  return m !== null && m.state === 'READY' && m.executable && m.scope.first_exercise !== null;
}
