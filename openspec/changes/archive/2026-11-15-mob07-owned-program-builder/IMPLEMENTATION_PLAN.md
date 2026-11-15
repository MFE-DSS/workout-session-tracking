# MOB-07 Owned Program Builder Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans; implement task by task with TDD, a durable ledger and final independent whole-branch review.

**Goal:** create, compose, save, structurally validate and publish user-owned programmes from the real native Programmes tab, preserving canonical services and all historical sessions.
**Architecture:** one transactional owner/CAS/replay boundary shared by native commands and web writers; existing UserProgram tree remains canonical. Typed native adapter and durable intents on the owned journal feed an additive DA08 builder consumer, then MOB06 readback/launch.
**Tech Stack:** existing FastAPI/SQLAlchemy/Alembic SQLite; existing Expo58/React Native/TypeScript/Jest/SQLite; no new dependency.
**Spec:** design.md, WIRE_PROTOCOL.md, CONTRACT_RECONCILIATION.md, specs/mobile/owned-program-builder/spec.md, UX_BOARD.md in this change.
**Authority:** BUILD_AUTHORIZATION.json records exact GO “Autoriser MOB-07, l’amendement et G1”,15November2026. Parent dc970d4d1b0352614cbdbbf1b694ff764f290829 (fast-forward from59, only REL03 correction added). No GO is asked again for this scope. Implementation method/ordinary technical choices are already delegated by the operator; this plan is executable, not another approval gate.

## Brainstorming / Options / Risques / Choix retenu

Option A, a native-only writer beside the existing web writers, would be faster but permit stale whole-tree overwrites and quota races; rejected. Option B, a second programme/prescription storage model, would duplicate canonical facts and historical identity; rejected. Choice: one owner/CAS transaction around the existing domain, an additive technical receipt, and the existing owned journal queue. The native surface uses DA08 and explicit manual inputs, with no scientific engine or recommendations. Main risks are nested domain commits, web compatibility, historical unknown slots, stale auth/receipt responses and shared journal recovery; Tasks1–5 assign concrete regression evidence. Cost: more existing-writer hooks and affected consumer tests, deliberately included by the accepted web/CAS amendment. Operational deployment and final visual pixels remain separate gates.

## Global Constraints

- One existing change/one completed feature PR; no technical checkpoint merged as a delivered feature. No reset/stash/clean/force/prune or unique-file destruction.
- UserProgram/UserProgramSession/UserProgramExercise/UserProgramRepTarget remain canonical. No second prescription model, new scientific scoring, new generator or EKB/catalogue seed.
- Existing quotas10active programmes/7sessions/10exercises; new native inputs1–6sets,1–50reps,min≤max. These are transport/domain bounds, not recommendations. No numeric prescription default invented.
- Canonical exercise picker: exact unambiguous Exercise slug/name and EKB intersection, resolved again at mutation. Historical slots can be kept unchanged under owner/slot/content digest, including unknown identity and old bounds.
- Structural VALIDATED is not scientific approval or launch permission. Publication/new-cycle use existing services; historical templates and sessions remain immutable. MOB06 controls launches, UNKNOWN and Legacy/V3 guards.
- program_builder_operations_v1 additive after nutrition_manual_01; no startup DDL/backfill; populated downgrade refuses. No source tree/numeric prescription copied into receipt storage.
- Native intent persists exact body/digest before HTTP, on existing journal connection/serial queue, account/backend isolated. No automatic mutation replay; lost response stays UNKNOWN until exact receipt or explicit human same-command retry.
- Family DA08, D4/four tabs, Frame C/RecessedWindow/NumericReadout/tokens unchanged. No global geometry, palette, baseline, module, SDK, lock, EAS change.
- No commit of visible UI/template changes before applicable SSR/native pixel acceptance. Preserve work/ledger/snapshots in durable paths during this gate. Engineering commits may be deferred to avoid committing unapproved templates.
- check_scope before local checks; migration tier uses only scripts/run_local_sweep.sh, with resource guard. Never pytest -n auto or local CI sweep. Do not overlap a full sweep with mobile/native-heavy runs.
- Whole-branch independent review, actual CI final HEAD, merge commit with expected_head_sha under GOV-MERGE-01. Separate release/operational/physical gates; no APK/OTA/live OVH action.

## Task 1 — Atomic domain and web writers

**Files:** app/models/program_builder_operations.py, app/models/__init__.py, migrations/versions/program_builder_operations_01.py, data/schema_snapshot.sql; services/program_builder_commands.py plus bounded draft/publish/versioning/quality/weekly-materialization hooks; routers/user_programs.py and its owned forms; new focused command/migration/web tests. FILE_OWNERSHIP.md governs all paths.

**Interfaces:** ProgramBuilderError(code,status); canonical_command(body)->dict; command_digest(body)->str; read_program(db,owner,id)->projection; program_source_digest(program)->hex64; apply_command(db,owner,body,*,auth_proof,controlled)->receipt; web_mutation(db,owner,*,program_id,expected_source_digest,callback)->domain result. One guarded transaction does fresh owner/source/quota read, callback and receipt, with exactly one commit. Existing helpers gain keyword commit=True and flush-only internal path; nested publish quality freeze must share outer transaction.

**Command wire frozen for clients:** exact root keys contract_version,command_id,operation,program_id,expected_source_digest,payload. contract_version=program-builder/1.0.0. CREATE: program_id=null,expected_source_digest=null,payload={title}. RENAME:{title}; SAVE_TREE:{sessions}; VALIDATE/PUBLISH/NEW_CYCLE/ARCHIVE:{}. IDs positive safe integers; command_id ASCII1–128; Unknown fields are refused. JSON duplicate fields, floats and nonfinite numbers are refused. Max command131072bytes. source digests64lowerhex. Canonical digest is SHA256(JSONUTF8 sorted keys,compact separators,ensure_ascii=False,allow_nan=False); no transport envelope or normalization added to hash.

**Native tree wire:** sessions array, each {position,name,kind,focus,duration_target_minutes,notes,exercises}; exercises {position,selection,keep,rep_targets,notes}; selected new slot selection={slug,name,ekb_version},keep=null,rep_targets explicit array {min_reps,max_reps,technique,is_warmup}; preserved slot selection=null,keep={slot_id,slot_digest},rep_targets=null,notes=null. Keep reconstructs all historical source fields unchanged, only enclosing order may change; reject duplicate/foreign/changed slots. Names use existing domain lengths; preserve historical source metadata. No direct identity FK introduced. Server derives set_scheme from exact chosen rep targets, never recommends values.

**Receipt exact fields:** contract_version,owner_id,command_id,request_sha256,operation,program_id,resulting_source_digest,resulting_version,publication_ids,selections,recorded_at. selections carries {slot_id,slug,name,ekb_version} for new selections only; no numeric tree. Stored JSON receipt and native decoder must share exact shape. Replayed receipt is historical, not current source/permission.

- [ ] RED real SQLite tests: owner404; exact replay/samekey409; old web token409/missing428; true two-writer quota race; stale identity; keep unknown/out-of-bound historical slot; failed publish after quality freeze rolls back source/review/templates/receipt; new-cycle old templates/session facts unchanged.
- [ ] Add receipt migration and model; test upgrade on populated parent, FK/index/unique, empty roundtrip and populated downgrade refusal; refresh snapshot through canonical tool.
- [ ] Implement shared guard using existing guard_owner SQLite write reservation; validate native auth proof under lock. No ORM stale identity-map source after guard. Reject unsupported storage instead of implying PG qualification.
- [ ] Make all existing writers join the same transaction/CAS boundary, including weekly materialization and web generation/create/publish/new-version. Web callbacks reconstruct tree only from refreshed owned source under lock. Web free text remains allowed; generator/formula unchanged.
- [ ] All root-mutating web forms carry source_digest; creation/materialization forms carry owner collection token. Missing428/stale409 use existing error rendering. Keep existing success/domain error semantics. Update web tests to fetch actual rendered token, never bypass it.
- [ ] GREEN targeted and broad existing domain/web consumers; record exact commands, failures and rulings.

## Task 2 — Owned read model and real API

**Files:** app/services/mobile_program_builder.py, app/routers/mobile_program_builder.py, config.py/main.py; route migration inventory and tests. Backend worker owns these; REL03 source files remain outside this scope.

**GET envelope:** {contract_version,owner_id,...}. GET/exercises returns {items:[{slug,name,ekb_version,equipment_family,movement_pattern}],next_cursor}; GET/programs returns {items:[{id,title,status,version,source_digest}],next_cursor}; GET/programs/{id} returns {program:{id,title,slug_base,status,version,source_digest,sessions,publication_ids}}; session tree preserves canonical source metadata; each exercise includes slot_id,slot_digest,exercise_name,set_scheme,rep_targets,notes,identity:{state,slug,name,ekb_version} with state RESOLVED_CURRENT_NAME or UNRESOLVED. No inference of original selection provenance from current name resolution.

- [ ] RED exact contract/header/Bearer/no-store, query duplicates/extra fields, bounded pagination and coherent owner reads, missing=foreign404, ambiguous picker identity refused, operation GET readback and withdrawn fresh-operation flag after replay.
- [ ] Mount five exact routes under /api/mobile/v1/me/program-builder, negotiate X-Auren-Program-Builder; page limit default25/max50, stable cursor with owner/scope binding using backend identity and signing key; source/tree transport cap131072bytes. Finite source scans bounded before full materialization. Add default-closed PROGRAM_BUILDER_CONTROLLED_TEST_ENABLED and explicit builder backend identity/signing key configuration; inject through runtime adapter, never read production .env.
- [ ] POST: exact replay lookup precedes fresh-operation preconditions; CREATE needs If-None-Match:*, root writes need If-Match=body expected_source_digest; missing428, disagreement400, stale409. Auth always rechecked. Errors distinguish definite refusal from storage/commit uncertainty; no assumed success.
- [ ] Route inventory and actual app mount tests updated; real HTTP consumer flow create→save→validate→publish→MOB06readback/start→sameownedjournal/history.

## Task 3 — Strict client and durable command recovery

**Files:** clients/mobile/src/domain/programBuilderCommand.ts, api/programBuilder.ts, api/programBuilderDTO.ts, storage/programBuilderPendingCommands.ts, sync/programBuilderRecovery.ts; journal.ts/journalTypes.ts hooks and focused Jest/SQLite tests.

- [ ] RED strict integer/null/shape/owner/source/receipt decoders and canonical JSON/hash cross-language fixtures; active auth refresh cannot substitute account; transport caps and exact headers.
- [ ] Implement typed API from frozen Task1/2 shapes. Use existing injected base URL/auth/timeout patterns, no global EAS config edits.
- [ ] Add program_builder_pending_commands_v1 to owned journal connection/serial queue with account/backend/key/body/hash and PREPARED/UNKNOWN/RECEIPTED state. No second programme source copy; unsent draft lives in memory distinctly.
- [ ] Prepare exact intent durably before POST; failed local commit means no send; 503/response loss UNKNOWN. GET operation reconciles exact owner/key/hash/operation/program/result before UI closure. Only explicit human retry can send identical command again; never newkey/time normalization after timeout.
- [ ] Prove SQLite close/reopen, offline/reconnect, A/B/backend separation, late replies and no automatic POST. All existing BODY/NUT/LIB journal consumers stay green.

## Task 4 — Native Programmes consumer and visual proof

**Files:** ui/programs/ProgramBuilderScreen.tsx and focused controller/model as needed, existing LibraryHost/LibraryScreen, ConnectedApp/routes/ShellContext; no global tabs geometry or existing BODY/NUT source changes.

- [ ] RED native consumer tests create/session ordering/canonical picker/manual targets/save/validate/publish/new-cycle/archive and pending recovery/readback. Preserve four-tab shell and owned-session identity.
- [ ] Implement accepted G1 in existing DA08 family: ordered session structure, one active edit instrument, manual prescriptions empty until chosen, exact stored facts/unknowns, separate structural validation/publication actions. No active programme/calendar invented.
- [ ] Integrate real ConnectedApp injected transport/storage; refresh library after exact command receipt; use MOB06 launch only. Return to same Today/journal/history occurrence.
- [ ] Reuse native/synthetic test banc with real API/SQLite, normal/enlarged iOS390×844 and supported Android360/480, real keyboard/back/focus where target supported. Preserve existing evidence and personal devices; no ExpoGo module removal or cloud/native build without release GO.
- [ ] Produce ONE before/after board including small SSR token/error delta, field-source inventory, normal/large/IME/pending/conflict/historical slot and readback; request applicable pixel decision once. No unapproved UI/template commit. Unsupported full Android/physical remains explicitly unavailable.

## Task 5 — Full verification, review and delivery

- [ ] Freeze source; check_scope actual tier; targeted+broad backend; all migration guards/drift/snapshot/empty roundtrip/populated refusal; required bounded local full sweep. Native Jest/TypeScript and visual contract/security checks; serialize heavy campaigns.
- [ ] Fresh independent whole-branch review; repair in-scope Important with RED→GREEN and exact evidence, do not weaken gates. Reconcile final source and operator pixels before commit UI.
- [ ] Commit/push existing branch, one MOB07 PR; required final-HEAD CI/reviews/thread/base check; guarded commit merge automatically under GOV-MERGE-01. Canonical CI and genuine Sonar evidence.
- [ ] OpenSpec archive via CLI after complete scope, scoped docs closeout PR/CI, live receipts, preserve unrelated work/unique files. Update release component manifest, no new APK/OTA.

## Review Focus / self-review

Five adversarial inputs are explicitly assigned: stale full-tree web edits (Task1), final quota concurrent create (Task1), exact historical slots outside new bounds (Task1), lost publication response while source subsequently changed (Tasks1/3), auth/backend switch during recovery (Task3). Additional body hash/projection drift is covered by shared wire fixtures (Tasks2/3). None of these are scientific admissions. No scope gap identified; source/type choices above are fixed before implementation.

## Execution / leases / conflict scan

Ruling: existing operator GO authorizes autonomous plan execution; no additional method/plan approval is sought. Ruling: commits touching templates/new UI are deferred until pixel gate; durable snapshots/ledger protect intermediate work. Ruling: use disjoint backend and native leases under one scope; only the root integrates shared contracts. REL03 finishing owns docs/release/rel-03 and tools/qa_delivery, outside MOB07; DA08 finishing remains backlog-only. No other active writer for MOB07 source files identified.

Task1 produces digest/command/receipt consumed by Tasks2/3; shapes fixed above and tested cross-language. Task2 supplies actual auth/config/router consumed by Task4; no mobile route mounted with a fake source. Task3 owns journal table/queue used by Task4; serial.ts stays read-only. Backend and mobile heavy tests are scheduled, not overlapped with full migration sweep. Historical proposal files remain historical; BUILD_AUTHORIZATION.json supersedes their NO_GO only for this scope.

Ruling: the pure command canonicalization and strict read DTOs use separate domain/programBuilderCommand.ts and api/programBuilderDTO.ts modules, following the existing nutrition module boundary. This adds no storage or domain model; it keeps transport validation and acquisition state independently testable. Root owns these mobile paths.
