# Calibration and session time — implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver an actual isolated v2 producer integrating observation-backed starting-load calibration and honest conditional time feasibility, preserving all historical outputs.

**Architecture:** Strict immutable inputs feed pure replay and timing functions. A source-pinned v2 registry composes reviewed curation/pull and proposed calibration/time policies; a new producer returns a canonical v1 recommendation and a fully fingerprinted diagnostic envelope. No default authority admits a policy or READY.

**Tech Stack:** Existing Python3.11/Pydantic2/pytest, stdlib hashes/JSON; no new dependencies.

**Spec:** `docs/science/sci-p02-initial-policy/calibration-time-01/DESIGN.md` and `TEST_SPEC.md`; delta `calibration-time-01.md` in this change. GO BUILD: operator « continue » after scoped approval question. Autonomous inline execution, no new routine plan/merge approval.

## Global Constraints

- `initial-policy-producer/2.0.0`; proposed `initial-hypertrophy-policy/0.3.0-proposed`; runtime `NOT_SERVED`, READY `NOT_PRODUCED` until actual scientific admission.
- Historical producer/registry/planning, contract v1, E0/catalogue/credit, admission/curation/pull bundles unchanged; no app/mobile/API/model/migration/rail edit.
- No invented kg, anthropometric/sex/age transfer, increment, physiological RIR precision, timing constant, equipment inventory or silent loss of coverage/rest.
- CALIBRATED is a provisional observed/accepted setting, not true2RIR. Concerns/failure terminal within an episode; restart authority registry empty by default.
- Keep canonical request_fingerprint and a separate full evaluation fingerprint covering observations and trusted references; neither authenticates a caller.
- No synthetic approval or READY fixture. Positive conditional engineering timing cases never imply scientific admission.
- Run check_scope before local checks. Targeted/broad scoped suites and real CI; no full local sweep. User commit trailer Codex Opus4.8 as supplied in AGENTS.

## Review Focus

- Reordering/duplicating events or mutating a Pydantic model must not bypass chronology, identity, source or complete-input fingerprints (Task1/3).
- Old accepted loads cannot survive a later concern or leak across equipment/side/subject, and unknown flags cannot mean no concern (Task1).
- A past elapsed duration or overlapping setup/rest must not become a falsely precise future bound or be counted twice (Task2).
- A v2 engine/effective catalogue must not be silently rewritten to v1 to call its engine-pinned resolver; G17 needs its qualified context (Task3).
- A forged admission label or edited result must never pass the verifier; a lack of evidence stays blocked despite a large budget (Task3).

---

### Task 1: Strict observation contracts and load-calibration replay

**Files:** Create `tools/science_initial_policy/calibration_time_contracts.py`, `load_calibration.py`, `tests/science_calibration_samples.py`, `tests/test_science_load_calibration.py`.

**Interfaces:** ContextKey, Setting, CalibrationEvent, CalibrationEpisode are strict frozen Pydantic records. `context_digest(context: ContextKey) -> str`; `calibrate(episode: CalibrationEpisode | dict, *, min_reps: int, max_reps: int) -> dict`. Result has state, observed_setting, reference_event_id/source_ref, load_kg/load_mode projection, effort_sufficiency UNKNOWN, confidence/limitations/reasons, automatic_next_action, version. No load increase/decrease.

- [x] Write RED tests for C01–C06 and L01–L15 with independent literal observations, including file roundtrip and no source mutation. Example: known context/no history => NEEDS_CALIBRATION/load_kg null; accepted40kg×10 trial with explicit familiarization/no concerns => CALIBRATED/reference exact40kg, not a calculated target.
- [x] Run `python -m pytest -q tests/test_science_load_calibration.py`; Expected: behavioral failures for absent API, not collection errors.
- [x] Implement strict finite/unit/context/event validation, dedupe and replay; current sourced confirmations required; pending/unknown safety signals stay nonpositive; blocked predecessor never revived by a string restart ref.
- [x] Run targeted plus broad `python -m pytest -q tests/test_science_load_calibration.py tests/test_science_blueprint_first_plan_contracts.py tests/test_science_initial_plan_policy.py`. Expected: all pass, only existing dependency warnings.
- [x] Required local static checks on new files, then commit scoped task with tests. task-done records the final broad command/result.

### Task 2: Component timing and structured configuration constraints

**Files:** Create `tools/science_initial_policy/session_time.py`, `tests/test_science_session_time.py`; extend the new shared contracts only for time records if needed, not shared SCI v1.

**Interfaces:** `assess_session_time(session: dict, *, budget_minutes: int | None, components: list[dict], structure: str = 'TRADITIONAL_SEQUENTIAL', layout: str = 'UNSPECIFIED') -> dict`. Input session has actual slot IDs/prescriptions; each component covers explicit work/preparation/operations/session-preparation/rest keys with bounds, context, basis/source, optional exact clock interval. Returns ordinal, duration UNKNOWN unless real admitted authority exists, bounds/coverage/uncertainty, required rest floor and scoped planner constraint; no authority accepted via caller kwargs.

- [x] Write RED tests T01–T13 with known fixture observations. Literal case2sets with60s rest + work20s + prep10s + operations10s + sessionprep0s =>100s conditional DISJOINT_SEQUENTIAL total, likely fits2minutes but public Duration UNKNOWN because no admitted model. These are synthetic observations, not policy constants.
- [x] Run `python -m pytest -q tests/test_science_session_time.py`; Expected: absent-model behavioral failures.
- [x] Implement strict bounds/coverage and existing rest-floor reuse. Reject reduced-rest estimates; exact common-clock union counts overlaps once. Mixed/unproved layouts remain UNKNOWN. No automatic minutes/rep or setup filler.
- [x] Run `python -m pytest -q tests/test_science_session_time.py tests/test_science_load_calibration.py tests/test_science_initial_policy_admission.py tests/test_duration_ceiling.py`. Expected: all pass; historical floor behavior unchanged.
- [x] Static checks per tier, commit; task-done records this broad command/result.

### Task 3: Trusted v2 producer, fixtures and admission handoff

**Files:** Create `tools/science_initial_policy/v2_registry.py`, `v2_producer.py`, `v2_fixtures.py`, `tests/test_science_initial_policy_v2.py`. Artefacts under `docs/science/sci-p02-initial-policy/calibration-time-01/`: `policy.v1.json`, generated evaluation schemas/cases/manifest and concise delivery/admission handoff. Update only this change tasks/registry/dependency status.

**Interfaces:** `load_v2_registry(root: Path = ROOT) -> V2Registry`; `produce_v2(evaluation_request: dict, trusted_bundle: V2Registry) -> dict`; `verify_evaluation(request: dict, result: dict, trusted_bundle: V2Registry) -> dict`; `evaluation_fingerprint(request: dict, trusted_bundle: V2Registry) -> str`; `generated_cases() -> list[dict]`. Request explicitly includes canonical FirstPlanRequest with engine/effective-catalogue v2, subject, context episodes/timing inputs and frozen-source declarations. Result embeds FirstPlanRecommendation v1 (validated), both digests, selected draft/calibration/time/constraints and NOT_SERVED.

- [x] Write RED P01–P13/C07–C08 tests against actual producer. Cases: novice, returning, unknown/conflicting context, limited time, cadences2/3/out-of-scope, missing/conflicting inputs, qualified/unqualified G17, held/excluded vertical candidates, pending calibration, stale engine/bundle/owner/output digest. Historical hashes/eleven v1 fixtures must reproduce.
- [x] Run `python -m pytest -q tests/test_science_initial_policy_v2.py`; Expected: behavioral failures for missing v2.
- [x] Implement source-pinned trusted registry (approved policy/restart refs empty). Use validated curation/pull rows with v2 validation; never rewrite v2 request to v1 engine. Reuse pure match_distinct, preserving all candidate exclusions/conflicts/qualification. Compose effective role projection only for intended qualified plan, not executed history.
- [x] Implement strict complete-input/result verification, real per-session calibration/time and canonical status precedence. None of policy labels, operational calibration, experimental fits or large budgets creates READY. Generate cases from the actual producer, not expected JSON stubs.
- [x] Run three new modules, existing scientific contracts/producer/admission/curation/pull and slot/exposure/planner consumers (scoped broad). Expected: all pass, source/fixture hashes stable. Run Ruff/Bandit/budget/protocol/OpenSpec per check_scope, fixture generation check and secret scan of new artefacts.
- [x] Record exact scientific NOT_ADMITTED or actual earned admission, narrow remaining blocker and preparation for SCI-P02-INITIAL-POLICY-ADMISSION. Commit task and task-done evidence.
- [x] Independent scientific review separate from whole-branch code review, fix in-scope Critical/Important with RED→GREEN and scoped suites. Record rulings/minors without claiming global safety/biology review.
- [x] Implementation delivered in PR366, narrow same-boundary correction PR367; expected-SHA merges, real final-HEAD CI, scoped reviews/fixes and admission package recorded in calibration-time-01/VERIFICATION.md. Canonical verification, closeout publication and owned cleanup are explicit delivery gates tracked by that receipt and the closeout PR; no advance success or global science/MOB03 closure/deployment.

## Self-review

All six design sections map to tasks1–3 and49 test-spec rows; five Review Focus classes each have owned negative tests. Task1's calibration dictionary is consumed by3; task2's time input/result by3; both contracts remain isolated. Product-policy numbers are unchanged; no new predictive timing/calibration threshold. Detailed low-level model shape remains an implementation choice constrained by strict source/identity/replay tests.
