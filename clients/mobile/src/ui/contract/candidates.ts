/**
 * DA-02.4B.1 — fixtures rendered for the OPERATOR'S REVIEW, not yet governed.
 *
 * A candidate is captured (`run.sh review`) and shown to the operator; it is never
 * compared by the gate, and it has no baseline. Only once the operator approves it
 * does it move to `CONTRACT_FIXTURES` (fixtures.ts) and get its baseline through
 * `run.sh approve` + the manifest (docs/strategy/AUREN_VISUAL_CONTRACT.md §5).
 *
 * Empty between two iterations: DA-04.1's five BodyMap renders were approved (« oui go »)
 * and moved to fixtures.ts as PUSH-A-BODYMAP-TRIPTYCH-V1. The next iteration adds its own.
 */
import type { WindowFixture } from '../instrument/RecessedWindowFixture';

export type CandidateFixture = {
  /** `window-<width>x<height>-<fixture>` */
  id: string;
  candidate: 'RECESSED-WINDOW';
  width: number;
  height: number;
  fixture: WindowFixture;
};

export const CANDIDATE_FIXTURES: readonly CandidateFixture[] = [];

export function candidateById(id: string | null | undefined): CandidateFixture | undefined {
  return CANDIDATE_FIXTURES.find((f) => f.id === id);
}
