/**
 * DA-02.4B.1 — fixtures rendered for the OPERATOR'S REVIEW, not yet governed.
 *
 * A candidate is captured (`run.sh review`) and shown to the operator; it is never
 * compared by the gate, and it has no baseline. Only once the operator approves it
 * does it move to `CONTRACT_FIXTURES` (fixtures.ts) and get its baseline through
 * `run.sh approve` + the manifest (docs/strategy/AUREN_VISUAL_CONTRACT.md §5).
 *
 * DA-05.1 — WHOLE SCREENS: the real execution screen, on a lab plan — what the operator judges is the
 * screen he will hold, never a crop. A set, and the rest that leads to the next exercise (where the
 * next exercise's zone is shown).
 */
import type { WindowFixture } from '../instrument/RecessedWindowFixture';
import type { ScreenPhase } from './ExecutionScreenFixture';
import type { MissionSource } from './MissionScreenFixture';

export type CandidateFixture =
  | {
      /** `window-<width>x<height>-<fixture>` */
      id: string;
      candidate: 'RECESSED-WINDOW';
      width: number;
      height: number;
      fixture: WindowFixture;
    }
  | {
      /** `screen-<phase>-<width>x<height>-<plan>-e<exercise>` */
      id: string;
      candidate: 'EXECUTION-SCREEN';
      width: number;
      height: number;
      /** a plan of the lab fixture (`lab_fixture.json` → plans) */
      plan: string;
      /** 0-based exercise of that plan (its first set, or the rest after its last set) */
      exercise: number;
      phase: ScreenPhase;
    }
  | {
      /** `screen-mission-<width>x<height>-<slug>` */
      id: string;
      candidate: 'MISSION-SCREEN';
      width: number;
      height: number;
      /** `main` or `<family>:<session index>` (MissionScreenFixture) */
      source: MissionSource;
    };

/**
 * Empty between two iterations: the MISSION screens were approved (« go », 2026-10-31) and moved to fixtures.ts
 * as MISSION-SCREEN-V1. The next iteration adds its own.
 */
export const CANDIDATE_FIXTURES: readonly CandidateFixture[] = [];

export function candidateById(id: string | null | undefined): CandidateFixture | undefined {
  return CANDIDATE_FIXTURES.find((f) => f.id === id);
}
