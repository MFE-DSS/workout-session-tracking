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

export type ContractFixture =
  | {
      /** the baseline id: `<visual id>-<width>-<scenario>` */
      id: string;
      contract: 'CALIBRATION-LINE-V1';
      width: number;
      scenario: 'TARGET' | 'PUSH' | 'HIGH_COST';
      selectedValue: number;
    }
  | {
      /** the baseline id: `<visual id>-<width>x<height>-empty` — the frame alone, nothing composed in it */
      id: string;
      contract: 'FRAME-C-V1';
      width: number;
      height: number;
    }
  | {
      /** the baseline id: `surface-<width>x<height>-<scenario>` — Frame C + rail + sovereign readout */
      id: string;
      contract: 'INSTRUMENT-SURFACE-B1';
      width: number;
      height: number;
      scenario: 'TARGET' | 'PUSH' | 'HIGH_COST';
      selectedValue: number;
    }
  | {
      /** the baseline id: `surface-<width>x<height>-<scenario>-rest` — the surface at REST (B.2) */
      id: string;
      contract: 'INSTRUMENT-SURFACE-B2';
      width: number;
      height: number;
      scenario: 'TARGET' | 'PUSH' | 'HIGH_COST';
      selectedValue: number;
    };

export const CONTRACT_FIXTURES: readonly ContractFixture[] = [
  { id: 'calibration-line-320-target', contract: 'CALIBRATION-LINE-V1', width: 320, scenario: 'TARGET', selectedValue: 70 },
  { id: 'calibration-line-390-target', contract: 'CALIBRATION-LINE-V1', width: 390, scenario: 'TARGET', selectedValue: 70 },
  { id: 'calibration-line-390-push', contract: 'CALIBRATION-LINE-V1', width: 390, scenario: 'PUSH', selectedValue: 75 },
  { id: 'calibration-line-390-high-cost', contract: 'CALIBRATION-LINE-V1', width: 390, scenario: 'HIGH_COST', selectedValue: 82.5 },
  // DA-02.4B.1 (G2) — approved by the operator on 2026-10-25, before anything is composed in the frame
  { id: 'frame-c-390x220-empty', contract: 'FRAME-C-V1', width: 390, height: 220 },
  { id: 'frame-c-320x180-empty', contract: 'FRAME-C-V1', width: 320, height: 180 },
  // DA-02.4B.1 — « ACCEPT — LOCK B.1 » by the operator on 2026-10-25: the sovereign readout above the rail
  { id: 'surface-390x220-target', contract: 'INSTRUMENT-SURFACE-B1', width: 390, height: 220, scenario: 'TARGET', selectedValue: 70 },
  { id: 'surface-390x220-push', contract: 'INSTRUMENT-SURFACE-B1', width: 390, height: 220, scenario: 'PUSH', selectedValue: 75 },
  { id: 'surface-390x220-high-cost', contract: 'INSTRUMENT-SURFACE-B1', width: 390, height: 220, scenario: 'HIGH_COST', selectedValue: 82.5 },
  { id: 'surface-320x180-target', contract: 'INSTRUMENT-SURFACE-B1', width: 320, height: 180, scenario: 'TARGET', selectedValue: 70 },
  { id: 'surface-320x180-push', contract: 'INSTRUMENT-SURFACE-B1', width: 320, height: 180, scenario: 'PUSH', selectedValue: 75 },
  { id: 'surface-320x180-high-cost', contract: 'INSTRUMENT-SURFACE-B1', width: 320, height: 180, scenario: 'HIGH_COST', selectedValue: 82.5 },
  // DA-02.4B.2 — « ACCEPT — LOCK B.2 » by the operator on 2026-10-25: the surface at REST.
  // ADJUSTING is B.1 above; at 320 (regular) REST is byte-identical to B.1, so no fixture there.
  { id: 'surface-390x220-target-rest', contract: 'INSTRUMENT-SURFACE-B2', width: 390, height: 220, scenario: 'TARGET', selectedValue: 70 },
  { id: 'surface-390x220-push-rest', contract: 'INSTRUMENT-SURFACE-B2', width: 390, height: 220, scenario: 'PUSH', selectedValue: 75 },
  { id: 'surface-390x220-high-cost-rest', contract: 'INSTRUMENT-SURFACE-B2', width: 390, height: 220, scenario: 'HIGH_COST', selectedValue: 82.5 },
];

/** The governed B.2 surfaces (REST), for the device bench. */
export const SURFACE_B2_FIXTURES = CONTRACT_FIXTURES.filter(
  (f): f is Extract<ContractFixture, { contract: 'INSTRUMENT-SURFACE-B2' }> => f.contract === 'INSTRUMENT-SURFACE-B2',
);

/** The governed B.1 surfaces, for the device bench. */
export const SURFACE_B1_FIXTURES = CONTRACT_FIXTURES.filter(
  (f): f is Extract<ContractFixture, { contract: 'INSTRUMENT-SURFACE-B1' }> => f.contract === 'INSTRUMENT-SURFACE-B1',
);

export function selectedPositionOf(f: { selectedValue: number }): number {
  return pos(f.selectedValue);
}

export function fixtureById(id: string | null | undefined): ContractFixture | undefined {
  return CONTRACT_FIXTURES.find((f) => f.id === id);
}
