# MOB-06 implementation plan

> Execute inline with superpowers:executing-plans and test-driven-development.

**Goal:** An owned native library with explicit supported-session start and honest recovery.
**Architecture:** Bounded projections of canonical catalogue/program domains, signed owner/backend-scoped references, transactional existing start services. Typed native consumers and one operational local intention table on the owned journal connection.
**Tech stack:** Existing SQLAlchemy/FastAPI, TypeScript/React Native/Expo SQLite. No dependencies.
**Spec:** specs/mobile/owned-program-library/spec.md; design.md; WIRE_AND_RECOVERY.md.

## Global constraints
- Authorization call_4321044cec284c79898cb7d2dd483990; G1 accepted, pixels pending.
- No SCI/PLAN producer or acknowledgement change, no program writer, no server schema change.
- BODY/NUT shared leases remain sequential; no overlapping source PR or unapproved UI commit.
- No real data, deployment, build cloud, APK or OTA. Existing primitives and baselines retained.
- Local verification follows check_scope, never an automatic full sweep for isolated/shared code.

## Review focus
- A foreign or expired reference must reveal no other owner's program.
- Mutable page changes must refuse continuation without pretending COMPLETE.
- Draft/validated/archived publication and native unsupported shapes must never create sessions.
- A lost response or local save failure must not trigger a second POST or false receipt.
- Legacy/V3 snapshot transitions must preserve owner/backend operational intentions.

## Task 1 — bounded source projections and references
Files: new app/services/library_read_model.py and tests/test_mobile_library_reads.py.
Interfaces: LibraryContext(owner_id, backend_identity, signing_key, epoch); read_library(db, context, section='all', zone=None, limit=30, cursor=None); read_library_item(db, context, source_ref); resolve_library_selection(db, context, selection_ref). Closed dict DTO per WIRE; LibraryError(code,status).
- [ ] Write behavioral tests for catalogue filtering/order, owner program tree, typed planned facts, source/selection identity, no-set support, bounds and mutable pagination.
- [ ] Run failing tests, then implement actual SQL bounded projections/signatures and canonical zone/working-set semantics.
- [ ] Run targeted tests and existing library/program consumers; record exact results.

## Task 2 — transaction and HTTP consumer
Files: new app/services/library_start.py, app/routers/mobile_library.py, tests/test_mobile_library_start.py and tests/test_mobile_library_http.py.
Interfaces: start_library_session(db, context, selection_ref, expected_epoch, expected_hash, device_id); router consumes existing ApiUser/get_db. New config/mount only after shared leases.
- [ ] Tests first: Bearer/version/no-store/strict body, real start/readback, publication/stale/A-B refusal, concurrent owned start, complete preflight materialization/rollback, unsupported shape, current auth guards.
- [ ] Implement public guard_owner/admit_legacy_start/preparer_demarrage/instantiate_session/read_model consumers without MISSION recommendation fabrication.
- [ ] Prove API with isolated app mount on synthetic DB, exact digest refusal/201 envelope; broad domain regression.

## Task 3 — strict native client and durable intentions
Files: new api/library.ts/libraryResource.ts, storage/libraryPendingOpenings.ts, sync/libraryOpening.ts and colocated tests. Attach journal.ts/journalTypes.ts/journal.web.ts only after leases.
Interfaces: exact owned-library/1.0.0 DTO decode, backend/AuthSession revision-bound resource; owned operational PREPARED/SENT_UNKNOWN/RESOLVED port on existing Serial connection.
- [ ] Tests first: closed DTOs, integer/unit/source states, partial pages, unknown response, no POST before persistence, one POST after prepare, A/B/backend guards, 201-save failure, kill/native SQLite restoration and V3 snapshot survival.
- [ ] Implement canonical digest/body, strict refusal handling, explicit verify/resume/local cancel; no automatic replay or false idempotence.
- [ ] Run mobile Jest/TS and actual SQLite/native module proof; limits source-labelled.

## Task 4 — real native surface and visual acceptance
Files: ui/library/LibraryHost.tsx/LibraryScreen.tsx and tests; then ConnectedApp/routes/shell/missionOpening after shared leases.
- [ ] Reproduce accepted G1, preserve four tabs and locked primitives, 48dp targets; tests for actual selection/program→session→confirm/recovery, A/B/offline/back.
- [ ] Render real iOS/Android list/detail/confirmed/unknown/empty/previous/unsupported, normal and enlarged text, compare references. Submit ONE board before UI commit.
- [ ] On operator pixel acceptance, complete actual ConnectedApp integrated consumer proof and mandatory checks.

## Task 5 — review and delivery
- [ ] Fresh whole-change independent review; repair functional Important/Critical RED→GREEN, ledger deferred minors.
- [ ] Required local checks, native consumer tests, feature route inventory, security/OpenSpec; no weakened thresholds.
- [ ] Commit/push/PR, exact HEAD required CI + genuine advisory Sonar, merge commit guarded by expected SHA under GOV-MERGE-01.
- [ ] Canonical checks, archive/closeout, release manifest and parity evidence; preserve unrelated worktrees and device gates. No APK per merge.
