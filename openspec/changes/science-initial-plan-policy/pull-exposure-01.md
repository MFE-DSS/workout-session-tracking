# SCI-P02-PULL-EXPOSURE-RESOLUTION-01 — isolated scientific design

Base: 37d39bac4ff826daea1c21e97245e5720e58506c, 6 November 2026. Operator mandate: the five existing vertical-pull candidates only, explicit role/participation decisions, an additive versioned overlay, deterministic non-served fixtures, TDD and separate fresh scientific/code reviews. Previous curation is closed and immutable. No API, UI, shared schema or producer binding is authorized by this design.

## Brainstorming / Options / Risques / Choix retenu

**A — resolve a qualitative role under EV-71.** The canonical neutral candidate already fixes front path, parallel grip near shoulder width and loaded shoulder extension. Infer a pectoralis synergist from relevant regional anatomy and the actual loaded action; use acute observations only as corroboration. This is a DERIVED curation judgment, never a measured force fraction or a longitudinal hypertrophy result. Risk: anatomical capacity or nonmatching EMG could be mistaken for sufficiently specific functional participation. The independent scientific review must judge that inferential bridge explicitly.

**B — distinguish participation from unresolved role magnitude.** Catalogue UNKNOWN is already scoped per zone, not absence or invalidity of the whole exercise. Historical exposure can already retain unknown counters and MINIMUM bounds. An additive diagnostic can explain this without a new canonical enum. However, admitting incomplete exposure into FirstPlan READY would require a versioned shared-contract amendment, consumer compatibility work and explicit review; not a silent weakening of v1.

**C — retain the gap.** Valid if neither a bounded role decision nor a sufficiently specified primary realization is earned. No new pool, rowing substitute, default winner, EMG threshold, zero credit or artificial READY.

**Provisional choice for independent review:** A for `tirage-poulie-haute-prise-neutre / pecs` only: UNKNOWN to SECONDARY, `joint_action_anatomy`, EV-71. The categorical meaning is loaded synergist rather than stabilizer; the existing secondary-credit coefficient remains an accounting convention and is not revalidated physiologically. All other existing UNKNOWN roles remain; the other four candidates remain held for ancillary role or execution uncertainty. If review rejects A, retain UNKNOWN and use B/C with their genuine gates. No approved conversion is claimed in advance.

## Versioned design and boundaries

- `docs/science/sci-p02-initial-policy/pull-exposure-01/`: source snapshot, evidence separated by anatomy/acute/modelling/longitudinal, five-candidate overlay `vertical-pull-exposure/1.0.0`, explicit role delta and contract decision, non-served fixtures, handoff and verification receipt.
- `tools/science_initial_policy/pull_exposure.py`: strict pinned loader/validator and pure five-candidate diagnostic. Reuse FirstPlanRequest, validate_input and decision_fingerprint. No import by the old producer or app. Structural validity is not scientific authority: resolver accepts only the reviewed pinned bundle.
- `tools/science_initial_policy/pull_exposure_fixtures.py`: reproducible outputs for unconfirmed context, available equipment, explicit exclusions, unavailable/conflicting context and missing/limited user inputs. No recommendation or credit calculator.
- `tests/test_science_pull_exposure.py`: semantic boundaries, real source/pool validation and consumer outputs, historical replay. No source-text assertion as a substitute for behavior.

Source roles are preserved alongside effective overlay roles. A changed role requires candidate/zone/before/after/claim/authority/evidence/limits/reviewer decision. No global enum, E0, credit or catalogue mutation. Anatomy, acute activation, plausible hypertrophy and qualitative ordinal inference have separate fields. Unknown contributions remain uncounted; this tool emits no numeric credit, load, duration or READY.

The diagnostic separates scientific candidate admission, current equipment compatibility and user execution/calibration. AVAILABLE never certifies technique or calibration. Scientific admission is conditional on canonical execution, not permission to execute. Existing curation1.0.0 and producer1.0.0 outputs remain unchanged. Any effective reference snapshot or runtime use needs a later explicit versioned producer-binding operation.

## Implementation plan

> For agentic workers: execute inline with superpowers:executing-plans; one fresh scientific review distinct from whole-branch code review. Repository scope checks supersede generic full-local-suite suggestions.

**Goal:** resolve the five-candidate scientific blocker honestly, with a reviewed source-bound overlay and non-served executable diagnostic.

**Architecture:** additive pure leaf modules and artefacts; old contracts/policies/catalogue/curation are read-only. The loader binds sources and reviewed decisions; the resolver never treats arbitrary user JSON as authority.

**Tech stack:** existing Python3.11/Pydantic, pytest and JSON artefacts; no new dependency.

**Spec:** operator SCI-P02-PULL-EXPOSURE-RESOLUTION-01, this design, canonical EV-70/71 and the existing catalogue/FirstPlan contracts.

### Global Constraints

- Pool exactly five canonical IDs; intent `initial_vertical_pull_v1`, movement vertical_pull. No default selection.
- Preserve all old hashes, source credits, policies and producer outputs. No runtime/API/mobile import, shared-schema change or deployment.
- EMG never creates PRIMARY or hypertrophy percentage; supported participation never silently becomes SECONDARY/MINOR/credit.
- Neutral grip width/front path comes from canonical execution, not its name. Assistance mechanism and unilateral loads are never inferred.
- Preparation/calibration classes retained; no positive time feasibility or new prescription constants.

### Review Focus

- Noncanonical/alias/extra candidate or altered source role: reject, never widen pool.
- EMG-only role conversion, unknown-to-zero or unsupported delta: reject even if structurally valid.
- AVAILABLE plus UNAVAILABLE plus UNKNOWN: conflict remains blocking; another context is rejected by v1.
- User exclusions or reported limitations: no fallback candidate, no diagnosis or READY.
- Forged review flag/model copy/source path/hash: not authority; reject or retain the scientific hold.

### Task 1: reviewed overlay and non-served diagnostic

**Files:** create the two tools, one test module and the dedicated artefact folder above. Modify only the existing task/registry tracking after results; no source authority edits.

**Interfaces:** `load_pull_exposure(root=ROOT) -> PullExposure`; `validate_pull_exposure(data, root=ROOT) -> PullExposure`; `resolve_vertical_pull(request, bundle) -> dict`; `generated_cases() -> list[dict]`. Consumes the immutable old curation and canonical v1 request; produces a source-bound candidate/uncertainty diagnostic, not a FirstPlanRecommendation.

- [ ] Write tests for no fabricated role from acute evidence, five-only pool, source/old-version integrity, pending/rejected review rejection, neutral canonical execution, unknown ancillary roles without credit, primary uncertainty rejection, availability not execution, exclusions/conflicts and reproducible non-READY output.
- [ ] Run `check_scope` then the new test module; observe feature-missing RED before implementing the modules.
- [ ] Implement the strict model, source/pin guards and minimal resolver; add generator and review-backed artefact. Run the new tests to GREEN; log any ruling or science-driven change explicitly.
- [ ] Run the scoped scientific broad suite and applicable static/security/spec checks once after final changes; no full local sweep. Record commands/results in the execution ledger.
- [ ] Complete fresh scientific review (all ten mandate questions) and distinct code review. Fix in-scope Critical/Important with RED/GREEN. Keep unresolved science as unresolved.
- [ ] Commit/push scoped work and verify final HEAD CI under standing authorization. Merge only when mandatory checks and applicable reviews pass. Canonical verification, closeout and cleanup are governed by GOV-MERGE-01, without global science/MOB03 closure or activation.
