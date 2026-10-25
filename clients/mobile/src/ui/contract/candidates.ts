/**
 * DA-02.4B.1 — fixtures rendered for the OPERATOR'S REVIEW, not yet governed.
 *
 * A candidate is captured (`run.sh review`) and shown to the operator; it is never
 * compared by the gate, and it has no baseline. Only once the operator approves it
 * does it move to `CONTRACT_FIXTURES` (fixtures.ts) and get its baseline through
 * `run.sh approve` + the manifest (docs/strategy/AUREN_VISUAL_CONTRACT.md §5).
 *
 * Empty between two iterations: B.2's REST renders were approved (« ACCEPT — LOCK B.2 »)
 * and moved to fixtures.ts. The next iteration adds its own candidates here.
 */
import type { Presentation } from '../instrument/disclosure';

export type CandidateFixture = {
  /** `<visual id>-<width>x<height>-<scenario>-<state>` */
  id: string;
  candidate: 'INSTRUMENT-SURFACE';
  width: number;
  height: number;
  scenario: 'TARGET' | 'PUSH' | 'HIGH_COST';
  selectedValue: number;
  presentation: Presentation;
};

export const CANDIDATE_FIXTURES: readonly CandidateFixture[] = [];

export function candidateById(id: string | null | undefined): CandidateFixture | undefined {
  return CANDIDATE_FIXTURES.find((f) => f.id === id);
}
