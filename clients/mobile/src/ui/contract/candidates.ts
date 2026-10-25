/**
 * DA-02.4B.1 — fixtures rendered for the OPERATOR'S REVIEW, not yet governed.
 *
 * A candidate is captured (`run.sh review`) and shown to the operator; it is never
 * compared by the gate, and it has no baseline. Only once the operator approves it
 * does it move to `CONTRACT_FIXTURES` (fixtures.ts) and get its baseline through
 * `run.sh approve` + the manifest (docs/strategy/AUREN_VISUAL_CONTRACT.md §5).
 *
 * Empty between two iterations: DA-02.5's W1 was approved (« ACCEPT — LOCK W1 ») and
 * moved to fixtures.ts as RECESSED-WINDOW-V1. The next iteration adds its own candidates.
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
