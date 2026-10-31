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
import type { ZoneCode } from '../bodymap/bodyGeometry';
import { zoneGridHeight } from '../bodymap/triptychLayout';
import type { BodyMapViewPresetId } from '../bodymap/viewPresets';
import type { MarkFixture } from '../brand/MarkPlacementFixture';
import type { Boundaries } from '../calibration/layout';
import type { WindowFixture } from '../instrument/RecessedWindowFixture';
import type { ScreenPhase } from './ExecutionScreenFixture';

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

/** DA-04.1 — the T1 triptych, one camera in the session card's 60/40 module, or that module above the instrument. */
export type BodyMapFixture =
  | { kind: 'triptych' }
  | { kind: 'crop'; preset: BodyMapViewPresetId }
  | { kind: 'context'; preset: BodyMapViewPresetId }
  /** DA-04.2 — a session's panel, DERIVED from its exercises' primary zones (never composed by hand) */
  | { kind: 'session'; zones: readonly ZoneCode[] };

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
    }
  | {
      /** the baseline id: `controls-<width>x<height>-<scenario>-<state>` — the instrument with its − / + (B.3) */
      id: string;
      contract: 'INSTRUMENT-CONTROLS-B3';
      width: number;
      height: number;
      scenario: 'TARGET' | 'PUSH' | 'HIGH_COST';
      selectedValue: number;
      presentation: 'rest' | 'adjusting';
    }
  | {
      /** the baseline id: `window-<width>x<height>-<fixture>` — Recessed Window(s) in Frame C (DA-02.5) */
      id: string;
      contract: 'RECESSED-WINDOW-V1';
      width: number;
      height: number;
      fixture: WindowFixture;
    }
  | {
      /** the baseline id: `session-card-<width>x<height>-<scenario>-<state>` — the set card's target composition (R1) */
      id: string;
      contract: 'SESSION-CARD-R1';
      width: number;
      height: number;
      scenario: 'TARGET' | 'PUSH' | 'HIGH_COST';
      selectedValue: number;
      presentation: 'rest' | 'adjusting';
    }
  | {
      /** the baseline id: `mark-v1-<size or placement>` — AUREN-MARK-V1 (DA-03.2) */
      id: string;
      contract: 'AUREN-MARK-V1';
      mark: MarkFixture;
    }
  | {
      /** the baseline id: `bodymap-<view>-<width>x<height>[-<preset>]` — PUSH-A-BODYMAP-TRIPTYCH-V1 (DA-04.1) */
      id: string;
      contract: 'PUSH-A-BODYMAP-TRIPTYCH-V1';
      width: number;
      height: number;
      bodymap: BodyMapFixture;
    }
  | {
      /** the baseline id: `bodymap-crop-390x188-<zone>` or `bodymap-session-<slug>` — BODYMAP-ZONES-V1 (DA-04.2) */
      id: string;
      contract: 'BODYMAP-ZONES-V1';
      width: number;
      height: number;
      bodymap: BodyMapFixture;
    }
  | {
      /**
       * the baseline id: `execution-<phase>-<width>x<height>-<plan>-e<exercise>` — EXECUTION-SCREEN-V1 (DA-05.1):
       * the REAL execution screen on a lab plan, on an iPhone frame with its insets
       */
      id: string;
      contract: 'EXECUTION-SCREEN-V1';
      width: number;
      height: number;
      plan: string;
      exercise: number;
      phase: ScreenPhase;
    };

export const CONTRACT_FIXTURES: readonly ContractFixture[] = [
  { id: 'calibration-line-320-target', contract: 'CALIBRATION-LINE-V1', width: 320, scenario: 'TARGET', selectedValue: 70 },
  { id: 'calibration-line-390-target', contract: 'CALIBRATION-LINE-V1', width: 390, scenario: 'TARGET', selectedValue: 70 },
  { id: 'calibration-line-390-push', contract: 'CALIBRATION-LINE-V1', width: 390, scenario: 'PUSH', selectedValue: 75 },
  { id: 'calibration-line-390-high-cost', contract: 'CALIBRATION-LINE-V1', width: 390, scenario: 'HIGH_COST', selectedValue: 82.5 },
  // DA-02.4B.1 (G2) — approved by the operator on 2026-10-25, before anything is composed in the frame
  { id: 'frame-c-390x220-empty', contract: 'FRAME-C-V1', width: 390, height: 220 },
  { id: 'frame-c-320x180-empty', contract: 'FRAME-C-V1', width: 320, height: 180 },
  // DA-02.4B.1 — « ACCEPT — LOCK B.1 » by the operator on 2026-10-25: the sovereign readout above the rail.
  // DA-02.7 R2 (operator, option B, 2026-10-26): the rail on a 1,5× grid, the module taller (220 → 290, 180 → 210)
  { id: 'surface-390x290-target', contract: 'INSTRUMENT-SURFACE-B1', width: 390, height: 290, scenario: 'TARGET', selectedValue: 70 },
  { id: 'surface-390x290-push', contract: 'INSTRUMENT-SURFACE-B1', width: 390, height: 290, scenario: 'PUSH', selectedValue: 75 },
  { id: 'surface-390x290-high-cost', contract: 'INSTRUMENT-SURFACE-B1', width: 390, height: 290, scenario: 'HIGH_COST', selectedValue: 82.5 },
  { id: 'surface-320x210-target', contract: 'INSTRUMENT-SURFACE-B1', width: 320, height: 210, scenario: 'TARGET', selectedValue: 70 },
  { id: 'surface-320x210-push', contract: 'INSTRUMENT-SURFACE-B1', width: 320, height: 210, scenario: 'PUSH', selectedValue: 75 },
  { id: 'surface-320x210-high-cost', contract: 'INSTRUMENT-SURFACE-B1', width: 320, height: 210, scenario: 'HIGH_COST', selectedValue: 82.5 },
  // DA-02.4B.2 — « ACCEPT — LOCK B.2 » by the operator on 2026-10-25: the surface at REST.
  // ADJUSTING is B.1 above; at 320 (regular) REST is byte-identical to B.1, so no fixture there.
  { id: 'surface-390x290-target-rest', contract: 'INSTRUMENT-SURFACE-B2', width: 390, height: 290, scenario: 'TARGET', selectedValue: 70 },
  { id: 'surface-390x290-push-rest', contract: 'INSTRUMENT-SURFACE-B2', width: 390, height: 290, scenario: 'PUSH', selectedValue: 75 },
  { id: 'surface-390x290-high-cost-rest', contract: 'INSTRUMENT-SURFACE-B2', width: 390, height: 290, scenario: 'HIGH_COST', selectedValue: 82.5 },
  // DA-02.4B.3 — « ACCEPT — LOCK B.3 » by the operator on 2026-10-25: the − / + under the frame (P1),
  // at REST on the locked value and right after a press on + (ADJUSTING, one step up)
  { id: 'controls-390x290-target-rest', contract: 'INSTRUMENT-CONTROLS-B3', width: 390, height: 290, scenario: 'TARGET', selectedValue: 70, presentation: 'rest' },
  { id: 'controls-390x290-push-rest', contract: 'INSTRUMENT-CONTROLS-B3', width: 390, height: 290, scenario: 'PUSH', selectedValue: 75, presentation: 'rest' },
  { id: 'controls-390x290-high-cost-rest', contract: 'INSTRUMENT-CONTROLS-B3', width: 390, height: 290, scenario: 'HIGH_COST', selectedValue: 82.5, presentation: 'rest' },
  { id: 'controls-390x290-target-adjusting', contract: 'INSTRUMENT-CONTROLS-B3', width: 390, height: 290, scenario: 'TARGET', selectedValue: 72.5, presentation: 'adjusting' },
  { id: 'controls-390x290-push-adjusting', contract: 'INSTRUMENT-CONTROLS-B3', width: 390, height: 290, scenario: 'PUSH', selectedValue: 77.5, presentation: 'adjusting' },
  { id: 'controls-390x290-high-cost-adjusting', contract: 'INSTRUMENT-CONTROLS-B3', width: 390, height: 290, scenario: 'HIGH_COST', selectedValue: 85, presentation: 'adjusting' },
  { id: 'controls-320x210-target-rest', contract: 'INSTRUMENT-CONTROLS-B3', width: 320, height: 210, scenario: 'TARGET', selectedValue: 70, presentation: 'rest' },
  { id: 'controls-320x210-push-rest', contract: 'INSTRUMENT-CONTROLS-B3', width: 320, height: 210, scenario: 'PUSH', selectedValue: 75, presentation: 'rest' },
  { id: 'controls-320x210-high-cost-rest', contract: 'INSTRUMENT-CONTROLS-B3', width: 320, height: 210, scenario: 'HIGH_COST', selectedValue: 82.5, presentation: 'rest' },
  { id: 'controls-320x210-target-adjusting', contract: 'INSTRUMENT-CONTROLS-B3', width: 320, height: 210, scenario: 'TARGET', selectedValue: 72.5, presentation: 'adjusting' },
  { id: 'controls-320x210-push-adjusting', contract: 'INSTRUMENT-CONTROLS-B3', width: 320, height: 210, scenario: 'PUSH', selectedValue: 77.5, presentation: 'adjusting' },
  { id: 'controls-320x210-high-cost-adjusting', contract: 'INSTRUMENT-CONTROLS-B3', width: 320, height: 210, scenario: 'HIGH_COST', selectedValue: 85, presentation: 'adjusting' },
  // DA-02.5 — « ACCEPT — LOCK W1 » by the operator on 2026-10-25: the Recessed Window (W1 · Inset),
  // values as large as they fit, F1 text / figure · F2 BodyMap placeholder · F3 pair and 60/40
  { id: 'window-390x220-f1', contract: 'RECESSED-WINDOW-V1', width: 390, height: 220, fixture: 'f1' },
  { id: 'window-390x220-f2', contract: 'RECESSED-WINDOW-V1', width: 390, height: 220, fixture: 'f2' },
  { id: 'window-390x220-f3-pair', contract: 'RECESSED-WINDOW-V1', width: 390, height: 220, fixture: 'f3-pair' },
  { id: 'window-390x220-f3-split', contract: 'RECESSED-WINDOW-V1', width: 390, height: 220, fixture: 'f3-split' },
  { id: 'window-320x180-f1', contract: 'RECESSED-WINDOW-V1', width: 320, height: 180, fixture: 'f1' },
  { id: 'window-320x180-f2', contract: 'RECESSED-WINDOW-V1', width: 320, height: 180, fixture: 'f2' },
  { id: 'window-320x180-f3-pair', contract: 'RECESSED-WINDOW-V1', width: 320, height: 180, fixture: 'f3-pair' },
  { id: 'window-320x180-f3-split', contract: 'RECESSED-WINDOW-V1', width: 320, height: 180, fixture: 'f3-split' },
  // DA-02.7 R1 — the set card's target composition (operator, 2026-10-26: « tu prends le recommandé et boucle »):
  // the exercise, its windows, and the instrument with its keys at the bottom. Bench only (E7).
  { id: 'session-card-390x844-push-rest', contract: 'SESSION-CARD-R1', width: 390, height: 844, scenario: 'PUSH', selectedValue: 75, presentation: 'rest' },
  { id: 'session-card-390x844-push-adjusting', contract: 'SESSION-CARD-R1', width: 390, height: 844, scenario: 'PUSH', selectedValue: 77.5, presentation: 'adjusting' },
  // DA-03.2 — « ACCEPT », AUREN-MARK-V1 (operator, 2026-10-27): the master in both inks, each optical
  // drawing at a size where it is pixel-exact, and the three placements on the approved components
  { id: 'mark-v1-128-paper', contract: 'AUREN-MARK-V1', mark: { kind: 'swatch', size: 128, on: 'paper' } },
  { id: 'mark-v1-128-inverse', contract: 'AUREN-MARK-V1', mark: { kind: 'swatch', size: 128, on: 'field' } },
  { id: 'mark-v1-12-micro', contract: 'AUREN-MARK-V1', mark: { kind: 'swatch', size: 12, on: 'field' } },
  { id: 'mark-v1-16-compact', contract: 'AUREN-MARK-V1', mark: { kind: 'swatch', size: 16, on: 'field' } },
  { id: 'mark-v1-32-primary', contract: 'AUREN-MARK-V1', mark: { kind: 'swatch', size: 32, on: 'field' } },
  { id: 'mark-v1-64-primary', contract: 'AUREN-MARK-V1', mark: { kind: 'swatch', size: 64, on: 'field' } },
  { id: 'mark-v1-frame-c-390x290', contract: 'AUREN-MARK-V1', mark: { kind: 'frame-c' } },
  { id: 'mark-v1-session-card-390x844', contract: 'AUREN-MARK-V1', mark: { kind: 'session-card' } },
  { id: 'mark-v1-splash-390x844', contract: 'AUREN-MARK-V1', mark: { kind: 'splash' } },
  // DA-04.1 — « oui go » on the final gate board, PUSH-A-BODYMAP-TRIPTYCH-V1 (operator, 2026-10-29):
  // T1, the zone in `system`; each camera at the session card's BodyMap window; the module above
  // the locked load instrument
  { id: 'bodymap-t1-390x180', contract: 'PUSH-A-BODYMAP-TRIPTYCH-V1', width: 390, height: 180, bodymap: { kind: 'triptych' } },
  { id: 'bodymap-crop-390x188-push-pecs', contract: 'PUSH-A-BODYMAP-TRIPTYCH-V1', width: 390, height: 188, bodymap: { kind: 'crop', preset: 'push-pecs' } },
  { id: 'bodymap-crop-390x188-push-delt-lat', contract: 'PUSH-A-BODYMAP-TRIPTYCH-V1', width: 390, height: 188, bodymap: { kind: 'crop', preset: 'push-delt-lat' } },
  { id: 'bodymap-crop-390x188-push-triceps', contract: 'PUSH-A-BODYMAP-TRIPTYCH-V1', width: 390, height: 188, bodymap: { kind: 'crop', preset: 'push-triceps' } },
  { id: 'bodymap-context-390-push-pecs', contract: 'PUSH-A-BODYMAP-TRIPTYCH-V1', width: 390, height: 562, bodymap: { kind: 'context', preset: 'push-pecs' } },
  // DA-04.2 — « Ok, très bien » (operator, 2026-10-29), BODYMAP-ZONES-V1: one camera per zone, agnostic of
  // any program (zone → image); a session's panel is derived from its exercises (exercise → zones), here
  // one example per grid shape: 1, 2, 4, 6 and 7 zones (3 is the locked T1)
  { id: 'bodymap-crop-390x188-delt-post', contract: 'BODYMAP-ZONES-V1', width: 390, height: 188, bodymap: { kind: 'crop', preset: 'zone-delt-post' } },
  { id: 'bodymap-crop-390x188-lats', contract: 'BODYMAP-ZONES-V1', width: 390, height: 188, bodymap: { kind: 'crop', preset: 'zone-lats' } },
  { id: 'bodymap-crop-390x188-upper-back', contract: 'BODYMAP-ZONES-V1', width: 390, height: 188, bodymap: { kind: 'crop', preset: 'zone-upper-back' } },
  { id: 'bodymap-crop-390x188-biceps', contract: 'BODYMAP-ZONES-V1', width: 390, height: 188, bodymap: { kind: 'crop', preset: 'zone-biceps' } },
  { id: 'bodymap-crop-390x188-quads', contract: 'BODYMAP-ZONES-V1', width: 390, height: 188, bodymap: { kind: 'crop', preset: 'zone-quads' } },
  { id: 'bodymap-crop-390x188-posterior', contract: 'BODYMAP-ZONES-V1', width: 390, height: 188, bodymap: { kind: 'crop', preset: 'zone-posterior' } },
  { id: 'bodymap-crop-390x188-calves', contract: 'BODYMAP-ZONES-V1', width: 390, height: 188, bodymap: { kind: 'crop', preset: 'zone-calves' } },
  { id: 'bodymap-crop-390x188-core', contract: 'BODYMAP-ZONES-V1', width: 390, height: 188, bodymap: { kind: 'crop', preset: 'zone-core' } },
  { id: 'bodymap-session-liss-abs', contract: 'BODYMAP-ZONES-V1', width: 390, height: zoneGridHeight(1), bodymap: { kind: 'session', zones: ['core'] } },
  { id: 'bodymap-session-pull-a', contract: 'BODYMAP-ZONES-V1', width: 390, height: zoneGridHeight(2), bodymap: { kind: 'session', zones: ['lats', 'delt_post'] } },
  { id: 'bodymap-session-push-a', contract: 'BODYMAP-ZONES-V1', width: 390, height: zoneGridHeight(4), bodymap: { kind: 'session', zones: ['pecs', 'delt_lat', 'delt_post', 'triceps'] } },
  { id: 'bodymap-session-short-upper', contract: 'BODYMAP-ZONES-V1', width: 390, height: zoneGridHeight(6), bodymap: { kind: 'session', zones: ['pecs', 'lats', 'delt_lat', 'biceps', 'triceps', 'delt_post'] } },
  { id: 'bodymap-session-full-body-morphotype-priority-v1', contract: 'BODYMAP-ZONES-V1', width: 390, height: zoneGridHeight(7), bodymap: { kind: 'session', zones: ['pecs', 'upper_back', 'quads', 'posterior', 'delt_lat', 'delt_post', 'calves'] } },
  // DA-05.1 — EXECUTION-SCREEN-V1 (operator, 2026-10-31: « go »): the set screen with its zone, the rest before the next exercise
  { id: 'execution-set-390x844-push-a-e0', contract: 'EXECUTION-SCREEN-V1', width: 390, height: 844, plan: 'push-a', exercise: 0, phase: 'set' },
  { id: 'execution-set-390x844-push-a-e6', contract: 'EXECUTION-SCREEN-V1', width: 390, height: 844, plan: 'push-a', exercise: 6, phase: 'set' },
  { id: 'execution-set-390x844-catch-up-shoulders-e0', contract: 'EXECUTION-SCREEN-V1', width: 390, height: 844, plan: 'catch-up-shoulders', exercise: 0, phase: 'set' },
  { id: 'execution-rest-next-390x844-push-a-e0', contract: 'EXECUTION-SCREEN-V1', width: 390, height: 844, plan: 'push-a', exercise: 0, phase: 'rest-next' },
  { id: 'execution-rest-next-390x844-push-a-e2', contract: 'EXECUTION-SCREEN-V1', width: 390, height: 844, plan: 'push-a', exercise: 2, phase: 'rest-next' },
  { id: 'execution-rest-next-390x844-catch-up-shoulders-e0', contract: 'EXECUTION-SCREEN-V1', width: 390, height: 844, plan: 'catch-up-shoulders', exercise: 0, phase: 'rest-next' },
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
