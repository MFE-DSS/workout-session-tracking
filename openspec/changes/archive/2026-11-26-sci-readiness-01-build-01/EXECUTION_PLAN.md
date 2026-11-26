# SCI-READINESS-01-BUILD-01 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development only after recorded SCI admission and separate GO BUILD. Steps use checkbox tracking. This plan is PROPOSED, not authorization to execute.

**Goal:** One owned server read-only projection of documented muscular exposure, with honest coverage and strict runtime boundaries.
**Architecture:** thin GET adapter, bounded supervisor/isolated Linux worker, coherent SQLite source, provenance and pure role projection; existing writers/engine untouched.
**Tech Stack:** existing Python3.11.14/FastAPI/Pydantic/SQLite/SCI assets, standard library subprocess/resource, no dependency addition.
**Spec:** design.md, WIRE_CONTRACT.md, PROPOSED_RESPONSE.schema.json, SOURCE_AUTHORITY.md, RUNTIME_LIMITS.md, CONTRACT_RECONCILIATION.md and amended SCI D1–D5.

## Global Constraints
Preparation only until admission+GO ; source1f0122bf to refresh at execution ; onechange/onePR ; all caps exact in RUNTIME_LIMITS ; no migration, native, writer, allocation, TIME01 or deployment. New consumer whitelist exact only. Default disabled.

## Review Focus
- Old-ID prefix can omit recent facts: UNKNOWN/PARTIAL instead of misleading absence.
- Current row vs originreceipt/catalogue revision: no mixed snapshots or currentcatalogue fallback.
- Empty/raw0 vs unknown quantities: canonical evidence scope distinct from window_result.
- Resource kill/output/JSON failure: no unbounded parent capture or orphan child.
- V3 graph/typed machine uncertainty: do not turn a setting into mass or invalid mapping into Legacy.

## Task 1 — strict contract and bounds
Files: new contracts.py/limits.py and test_muscle_observed_load_contract.py.
Interfaces: proposed `parse_query(values, contract_header, *, as_of) -> ObservedLoadQuery`; immutable `ReadLimits`; `ObservedLoadReadError(code,status)`; `ObservedLoadResponse` strict DTO matching WIRE_CONTRACT. No code bodies fixed by this plan.
- [ ] Write named failing tests strict_request_and_nullable_states and unknown/EXACT/MINIMUM combinations; run module, preserve RED.
- [ ] Implement only these types, query codec and immutable limits with exact candidates.
- [ ] Run same tests to GREEN; no new route yet.

## Task 2 — coherent bounded SQLite source
Files: sqlite_source.py and test_muscle_observed_load_sqlite.py.
Interfaces: `open_owned_capture(database_url, owner_id, query, limits) -> context manager[OwnedReadCapture]`; capture exposes scalar candidates, guarded text, bounded alias/binding/evaluation/operation records and stats within the same connection. No externally supplied path.
- [ ] RED tests old_id_prefix_misses_recent_window, budgets, times, owners/read_only, snapshot, text admission.
- [ ] Implement explicit BEGIN/read-only/authorizer/progress +bounded keysets, no canonical reader mutation; G/R joins guarded.
- [ ] GREEN tests including real disposable WAL concurrency and rawbyte/VM/statement probes. No original DB write.

## Task 3 — provenance and projection
Files: provenance.py/projection.py/P07data and provenance/projection tests ; scoped spec/guard amendment only after its authority.
Interfaces: `qualify_fact(capture, candidate, sources) -> QualifiedFact`; `project_capture(capture, query, sources, limits) -> ObservedLoadResponse`. `QualifiedFact` keeps canonical IDs/context plus declared membership/source quality ; never invent a revision or time.
- [ ] RED effective catalogue/graph/episode/replay/unit/roles/partial/minimum/P07 tests from TEST_PLAN and exact importer guard.
- [ ] Amend canonical consumption addendum and guard only as explicitly admitted, implement bounded source adapter and pure fold reuse in sole importer. Existing folds/writers unchanged.
- [ ] GREEN +parity on same canonical role fixtures; no new enginerecommendations or datefix. Record source unknown cases rather than weakening tests.

## Task 4 — bounded worker and supervisor
Files: worker.py/supervisor.py and test_muscle_observed_load_worker.py.
Interfaces: fixed child entry accepts bounded internal owner/query JSON; `read_owned_muscle_observed_load(owner_id, query, *, runtime_profile) -> ObservedLoadResponse`, supervisor owns slot, read-limit, timeout, kill+wait. Child never receives Bearer token.
- [ ] RED/Linux qualification witnesses caps/cleanup, slot/profile and no parentrlimit changes; failed capability ->UNAVAILABLE.
- [ ] Implement isolation with caps before heavy imports ; no unbounded capture_output/communicate stdout, no preexec_fn.
- [ ] GREEN unit failures +actual Linux normal/adversarial cases in isolated runtime, record fingerprint/memory/time/source manifest. If nominal unavailable, HOLD rather than raise caps silently.

## Task 5 — GET integration and delivery
Files: new router ; two sharedfile deltas mobile_api/config ; canonical routeinventory ; test_mobile_muscle_observed_load.py ; scoped docs.
- [ ] Recheck parent/leases and implement RED Bearer/header/query/no-store/disabled/inventory tests.
- [ ] Add defaultfalse feature config +profile reference, mount GET only ; no endpoints/schedules/consents elsewhere.
- [ ] GREEN complete route on synthetic DB, ownerisolation and expected PARTIAL/UNKNOWN/EMPTY; zero DML assertions. Run tier’s local checks/broad/security and full independentreview.
- [ ] After all authorized gates: commit/push/PR, protected CI exactHEAD, mergecommit underGOV, canonicalCI/closeout/cleanup scope only. No sourceCI reuse; no deployment/OTA/activation.

Commits in these tasks are deferred until the whole authorized backend scope is reviewable ; do not publish a technical checkpoint as a complete feature. Current plan never authorizes these unchecked execution steps. Self-review coverage is in PREPARATION_RECEIPT, not a test result of this implementation.

Self-review après revue : Task1 couvre tous les $defs et les10invariants croisés du contrat ; Task3 couvre les10maillons d’autorité, manifeste historique et source overlay, sous lecture bornée et parité. Les nouveaux fichiers schema/authority sont documentaires dans le change ; aucun package runtime supplémentaire créé.
