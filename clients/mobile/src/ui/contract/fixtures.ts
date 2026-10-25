/**
 * DA-GOV-01 — the visual contract's deterministic fixtures
 * (`docs/strategy/AUREN_VISUAL_CONTRACT.md`).
 *
 * One fixture = one exact state of one governed component, at one width. The
 * data is the DA-02.2 acceptance bench's, verbatim (CalibrationGallery: 55–85 kg
 * every 2,5 kg, prescription 70, the same zone boundaries), so the baseline
 * renders exactly what the operator approved. Changing a value here changes a
 * baseline: it is a contract change, not a refactor.
 */
import type { Boundaries } from '../calibration/layout';

const LOW_KG = 52.5;
const HIGH_KG = 87.5;
const pos = (kg: number) => (kg - LOW_KG) / (HIGH_KG - LOW_KG);
const LOADS = Array.from({ length: 13 }, (_, i) => 55 + i * 2.5);

/** CALIBRATION-LINE-V1 — the DA-02.2 bench data. */
export const CALIBRATION_LINE_DEMO: Boundaries & {
  steps: number[];
  stepValues: number[];
  referencePosition: number;
  referenceValue: number;
  unit: string;
} = {
  lowBoundary: 0,
  targetLowBoundary: pos(68.75),
  targetHighBoundary: pos(71.25),
  highCostBoundary: pos(78.75),
  steps: LOADS.map(pos),
  stepValues: LOADS,
  referencePosition: pos(70),
  referenceValue: 70,
  unit: 'kg',
};

export type ContractFixture = {
  /** the baseline id: `<visual id>-<width>-<scenario>` */
  id: string;
  contract: 'CALIBRATION-LINE-V1';
  width: number;
  scenario: 'TARGET' | 'PUSH' | 'HIGH_COST';
  selectedValue: number;
};

export const CONTRACT_FIXTURES: readonly ContractFixture[] = [
  { id: 'calibration-line-320-target', contract: 'CALIBRATION-LINE-V1', width: 320, scenario: 'TARGET', selectedValue: 70 },
  { id: 'calibration-line-390-target', contract: 'CALIBRATION-LINE-V1', width: 390, scenario: 'TARGET', selectedValue: 70 },
  { id: 'calibration-line-390-push', contract: 'CALIBRATION-LINE-V1', width: 390, scenario: 'PUSH', selectedValue: 75 },
  { id: 'calibration-line-390-high-cost', contract: 'CALIBRATION-LINE-V1', width: 390, scenario: 'HIGH_COST', selectedValue: 82.5 },
];

export function selectedPositionOf(f: ContractFixture): number {
  return pos(f.selectedValue);
}

export function fixtureById(id: string | null | undefined): ContractFixture | undefined {
  return CONTRACT_FIXTURES.find((f) => f.id === id);
}
