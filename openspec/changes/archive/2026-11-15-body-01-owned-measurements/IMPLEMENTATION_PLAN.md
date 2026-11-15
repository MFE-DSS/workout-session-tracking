# BODY-01 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans inline; no per-task implementer/reviewer. One fresh whole-branch review at end. Steps use checkbox syntax.

**Goal:** Owned native dated measurements, original-preserving corrections, truthful current/history readers and exact recovery.
**Architecture:** BodyMeasurement numeric versions; one metadata lineage/operation table; shared canonical writers and SQL head predicate; one local pending-command table and native BODY family feeding existing Progress chart.
**Tech Stack:** Existing Python/FastAPI/SQLAlchemy/Alembic SQLite; Expo58/React Native/TypeScript/SQLite/SVG. No new dependency.
**Spec:** design.md, BUILD_SCOPE.md, CONTRACT_RECONCILIATION.md, TEST_SPEC.md, UX_BOARD.md in this change.

## Global Constraints
- GO received call_106057b169a74bc9887b1fea9f527f5d: amend contracts + revised BODY + G1, synthetic only.
- Original rows unchanged by correction; no backfill/rebuild/second numerical series. Ordinary erasure distinct and explicitly confirmed.
- kg/cm, same-row G/D, UNKNOWN and nonfini legacy honest. No new average/body science.
- All runtime writers and effective readers; no rollback to raw readers after lineage.
- Pixels before UI commit; standing merge only after gates. No APK/OTA or deployment.

## Review Focus
- Mixed old/new fields in correction: inherited provenance/invalid data must not be requalified; task1/3 tests.
- Null on corrected head must not revive ancestor in any current reader; task2 real consumers.
- Lost erase receipt then id allocation across owners must never target new fact; task1/4 tests.
- Stale SSR form and A/B late responses must not overwrite new head or display another account; task2/4/5.
- Missing migration/schema and rollback must not silently return raw old facts; task1/2/6.

### Task 1: Atomic lineage and additive migration
**Files:** new app/models/body_measurement_operation.py, services/body_measurement_commands.py, services/body_measurement_reads.py; models/__init__.py, database.py; migrations/versions/body_measurement_operations_01.py; tests/test_body_measurement_commands.py and migration tests.
**Interfaces:** apply_command(db, owner_id, command:dict, *, source:str, require_consent:bool=True)->dict receipt; current_measurement_predicate()->SQL expression; owned_head(db,owner,root)->(row,token,revision); BodyCommandError(code,status).
- [ ] Write real failing tests: original immutable/new version/current head, null versus absent, exact replay, cross-owner, erase/root and nonreuse.
- [ ] Run targeted RED under check_scope; Expected feature assertion failure, not an unrelated import/config error.
- [ ] Implement model, metadata guard, SQLite write transaction/global allocator, digest/token, atomic commands/replay and head queries; no startup DDL.
- [ ] Run targeted GREEN and separate-connection races/rollback tests. Expected all cases pass.
- [ ] Add migration-only table/index, schema snapshot and real upgrade/no historical mutation tests; Expected additive drift checks pass.
- [ ] Backend checkpoint commit only once required verification/review permits; no UI files committed here.

### Task 2: Canonical legacy writers and current readers
**Files:** body_profile.py; routers/body.py/auth_routes.py; all B05 readers; two SSR templates; targeted legacy suites/tests and test schema helpers/fixtures.
**Interfaces:** wrappers delegate apply_command and return new BodyMeasurement; all selectors use current_measurement_predicate from task1. SSR hidden token from owned_head, stale refusal.
- [ ] RED tests: web edit conserves original; stale web form409; every reader excludes corrected predecessor/never resurrects null; body_ledger one-query budget.
- [ ] Integrate kernel/wrappers and SQL head predicate, preserve formula/date/partial semantics; amend the three named normative documents explicitly.
- [ ] Provision sidecar explicitly in test harness fixtures, never application startup. Existing fixtures must model migrated deployment without disabling missing-schema tests.
- [ ] GREEN broad legacy/body/profile/morphology/BI/score/coach/dashboard; Expected unchanged legacy facts and formulas, deliberate edit expectations versioned, ownership retained.
- [ ] Keep template changes uncommitted until family pixel acceptance.

### Task 3: Owned API, DTO, audit and export
**Files:** routers/mobile_body_measurements.py, routers/mobile_api.py, service reads; tests/test_body_measurements_api.py.
**Interfaces:** body-measurements/1.0.0 DTO and B07 routes; source-aware current fields and audit; no change legacy weight DTO/decode.
- [ ] RED HTTP tests for bearer/consent/no-store/404 parity/version/date/strict inputs; cursor revision/conflict; correction/audit/erase/replay/export and no side effects on failed command.
- [ ] Implement boundaries, controlled native write admission (test environment + existing body flag), exact owner; metadata folding preserves inherited provenance/date and bounds resources.
- [ ] GREEN actual file DB and real auth/HTTP consumer, including Progrès-compatible weight projection. Expected scoped facts only, legacy v1 shape intact.

### Task 4: Native exact commands and source-aware reader
**Files:** api/bodyMeasurements.ts + resource/tests; storage/bodyPendingCommands.ts; sync/bodyCommandRecovery.ts/tests; journal/journalTypes/web only BODY extension.
**Interfaces:** BodyMeasurementsClient / BodyMeasurementsResource ; BodyPendingCommands.prepare/read/ack; BodyCommandRecovery.verify/replay, partition resolved by existing ownership.
- [ ] RED strict decoder/source/root/head/unit tests and real storage recovery: local failure no HTTP, kill/reload same payload, A/B/late result isolation.
- [ ] Implement exact persistent command before HTTP, status then explicit replay; no automatic offline queue and no second canonical history.
- [ ] GREEN tests and TypeScript. Expected same command survives restart and stale response cannot change another owner.

### Task 5: Native BODY family and Progress readback
**Files:** ui/body/BodyMeasurementsSurface.tsx, MeasurementSheet.tsx, BodyFamilyBoard.tsx; ConnectedApp/ShellContext/progres/profil; WeightTrend and presentation adapter; consumer tests.
**Interfaces:** same BODY resource shared by Profil entry and Progrès weight; existing chart source-aware, session history untouched.
- [ ] RED consumer tests: create/correct/audit/erase, date/side/unit/unknown, pending recovery, source-aware Progress, consent and focus/48dp actions.
- [ ] Implement accepted G1 exactly, relevant help on demand, preserve primitives and references. No hidden required date/clear/confirmation.
- [ ] GREEN actual component/resource tests and TypeScript; produce real iOS/Android native captures and minimal SSR confirmation.
- [ ] Submit one consolidated board normal/large fonts and transport states; wait only for required operator pixel decision before UI commit.

### Task 6: Verification and independent review
**Files:** evidence outside worktree; scoped tests; change/review receipts.
- [ ] check_scope current diff; run migration/drift/snapshot/ciblés/broad and bounded local sweep per verdict, mobile+TS, security/spec/OpenSpec/visual required. Expected PASS without lowered gates.
- [ ] One fresh whole-branch code/consumer review using plan/spec/ledger; fix Critical/Important via RED→GREEN in one pass. Preserve exact findings/rulings/minors.
- [ ] Once pixel decision and checks are satisfied, final source review/commit/push PR; Expected exact HEAD mandatory CI green, no blocking threads.

### Task 7: Guarded integration and closeout
**Files:** docs/pilot/body-01, docs/pilot/mvp-integration manifest/policy; OpenSpec archive/registry.
- [ ] Merge exact reviewed HEAD under GOV-MERGE-01, real canonical CI and Sonar observed; no new routine GO.
- [ ] Update engineering/integration/external release manifest, relevant composed smoke; distinguish candidate readiness and actual APK/physical gaps.
- [ ] Archive finished engineering scope, docs closeout PR/gates, preserve receipts and only clean own items after no unique work proof. No build/OTA/deploy.

## Pre-flight interfaces and rulings
Task1→2 shared predicate/token: SQL predicate references sidecar and fails if absent, preserving one-query body_ledger budget; no introspection per measurement.
Task1→3 commands: receipt contains no values, read fresh separately; no nested commit kernel.
Task3→4→5 body DTO: source-aware separate from legacy v1 decoder, preserve raw invalid/UNKNOWN and root vs physical id.
Task4→5 ownership/recovery: use existing partition decision and serialized SQLite queue, no reassignment.
Ruling: fixtures need explicit migrated schema provisioning (tests/conftest.py, tests/helpers.py and relevant custom body fixtures in scope); product startup must not create sidecar. Cost if wrong: missing-schema tests could be masked, so dedicated refusal test mandatory.
Ruling: intermediate task commits are deferred until verification/review, and all UI until pixel approval; continuity ledger is durable while working. This respects repository delivery gates over skill commit cadence.
