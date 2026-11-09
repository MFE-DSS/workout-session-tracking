# Six calibration encounters — implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans inline. Steps use checkbox syntax; the approved design travels with this plan.

**Goal:** Six actual limited encounter evaluators provide qualified portable observations that pass the real seven-context V3 producer, without calculated starting loads.

**Architecture:** New isolated policy loader, per-profile orchestration and independent validation reuse encounter1.0.0 and historical pure C3 helpers read-only. Reviewed authority publication precedes any admitted public result. Exports are synthetic, reproducible and never a runtime dependency.

**Tech Stack:** Python/Pydantic, existing pytest/ruff/Bandit/OpenSpec; no new dependency.

**Spec:** [Approved design](design.md), [test cases](TEST_SPEC.md), [admission case](../../../../docs/science/sci-p02-initial-policy/calibration-six-extensions/ADMISSION_CASE.md).

## Global Constraints

- Operator reply 9 November 2026: « Valider ce design et le build SCI isolé ».
- Same encounter1.0.0 and V3; all historical modules/publications/exports read-only.
- Five MACHINE_DISPLAY_KG, bilateral RDL PER_IMPLEMENT. No setting or increment generated.
- No admission until effective per-realization SCI review. No app/API/SDK/UI/activation.
- Standing merge applies after mandatory final HEAD controls, not a substitute for admission.

## Review Focus

- Changed choice/setup after a prior trial: no stale acceptance or qualification.
- Familiarization without exact setting or with trial boolean alone: no loaded permission.
- Later current confirmation/setup after historical qualified event: facts preserved, permission closed.
- Caller authority, changed source or unchecked parent: closed failure even with cached authority.
- Concern/retry/withdrawal and novel episode IDs: no bypass, no conversion UNKNOWN to clear.

### Task 1: Six encounter profiles and observed progression

**Files:** Create `tools/science_calibration_extension/{__init__,evaluator}.py`; test `tests/test_science_calibration_six_extensions.py`; document six procedures under `docs/science/sci-p02-initial-policy/calibration-six-extensions/OPERATIONAL_PROTOCOL.md`.

**Interfaces:** `compile_candidate(raw, historical_registry=None) -> EncounterResult` is preview only. `loaded_familiarization(req, before=None) -> bool` requires exact setting, current source, prior current context and preparation/choice chronology; used by validator too. Historical helper semantics remain unchanged.

- [ ] Write parameterized progression tests open/setup/trial/observed/qualified for six exact IDs, plus wrong realization/semantics, missing exact familiarization, changed setup/choice, concerns and explicit retry.
- [ ] Run scope then targeted file; expect missing extension implementation (RED).
- [ ] Implement thin profile selection and extra guards around current/concerns/C3 helpers; no historical compile/evaluate or PILOT patch.
- [ ] Run targeted tests; expect all preview cases PASS and no public authority inferred.

### Task 2: Published authority and canonical validation

**Files:** Create `tools/science_calibration_extension/{policy,validation}.py`, new `authority/{registry.v1.json,sources.v1.json,ADMISSION.md,SCI_REVIEW.md}` within the scientific dossier; same test module.

**Interfaces:** `load_authority(root=ROOT) -> ExtensionAuthority`; `assert_authority(authority)` strictly checks actual publication/source closure/current parent; `evaluate(raw, authority=None) -> EncounterResult` requires that authority for permissions. `validate_result(raw,response,authority=None) -> EncounterResult` strictly revalidates, independently checks observed C3 and exact loaded gate, and returns canonical recomputation.

- [ ] Write tests no authority, forged object/publication/source/cached drift, per-realization inactive status, forged action/portable qualification and strict native scalar types; run RED.
- [ ] Implement loader and evaluator using unpublished status first, with versioned per-realization references and exact source inventory. Add independent validator.
- [ ] Request fresh scientific review of actual code/protocol/effective bundle separately from code review. Correct Important with regression first. Publish only defensible reviewed decisions and final source pins; never self-label review as empirical validation.
- [ ] Run authority/adversarial tests; expect PASS, actual source closure verified.

### Task 3: Reproducible bridge, delivery and handoff

**Files:** Create `tools/science_calibration_extension/artifacts.py`; exports in new dossier only; extend same tests; update tasks/registry and delivery/handoff docs.

**Interfaces:** `synthetic_encounter(candidate_id, stage='qualified', root=ROOT)` constructs explicitly synthetic human-choice/observations; `build_artifacts(root)`, `export_artifacts(root)`, `verify_artifacts(root)` never imported by loader/product. `bridge(root)` calls six real evaluators, historical pilot, V3 producer and validators, then exact ack.

- [ ] Write bridge tests seven actual outputs, one missing, changed ack, no observation mutation and reproducible exports; run RED before artifacts implementation.
- [ ] Implement synthetic examples using fixed test observations, never a prescription or caller authority. Output real UNKNOWN/ack-required then ELIGIBLE from V3; no handmade positive envelope.
- [ ] Run final targeted and broad scientific modules once; Ruff new files/budget, Bandit, Gitleaks, spec protocol and OpenSpec strict according to scope. No full local sweep for isolated scope.
- [ ] Fresh whole-branch code review; single correction pass for Important with RED/GREEN and affected suites. Record minor debt and actual review limits.
- [ ] Commit/push/PR, inspect exact HEAD CI/Sonar/readiness, guarded merge, canonical CI, archive/closeout PR, final receipt and cleanup of only owned integrated work.

## Self-review / execution decision

The same request/result/authority interfaces flow tasks1→2→3; no shared product schema change. Every design gate maps to the targeted adversarial/progression tests and independent reviews. The operator approved inline execution in the design; no further routine plan or delivery confirmation. Task commits follow validated units; no publication of an unreviewed positive policy.
