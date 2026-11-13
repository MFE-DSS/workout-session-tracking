# NUT-01 Technical Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans inline. One fresh whole-branch review after technical scope, no per-task implementer.

**Goal:** Actual owned manual daily nutrition/declared targets with truthful reads, distinct consent and durable command recovery, without new UI composition.
**Architecture:** Two append-only integer-milli tables contain canonical revisions and receipts. SQLite guard_owner/public auth proofs, exact namespaces and CAS. A nutrition-specific transport/local module preserves bytes on existing owned journal.
**Tech Stack:** Existing Python/FastAPI/SQLAlchemy/Alembic SQLite and Expo58/TS; no dependency/provider/SCI change.
**Spec:** design.md, PERSISTENCE_AND_COMMANDS.md, WIRE_AND_READ_PROTOCOL.md, EXECUTION_SCOPE_20261112.md, CANONICAL_VECTORS.md. Technical GO call_c1496d1a84e04b1a8dd61ad04f063aa6.

## Global Constraints
- Synthetic technical build only; UI/G1/pixels/activation/release remain separate.
- No second weight model or scientific calorie target, no media/provider.
- Integer milli values0..999999999, null/absence/0 distinct, no4/4/9.
- No overwrite/backfill/startupDDL; heads only, exact historical target refs.
- Parent BODY migration is unmerged; implement independent models/services first. Draft migration/pinned synthetic integration uses BODY parent only after explicit dependency preflight; do not claim canonically runnable migration before that parent exists.
- Shared ConnectedApp/journal/metadata/API mounts sequenced with BODY; no overlapping source PRs. No commits/push until all applicable gates.

## Review Focus
- Two SQLite connections, stale epoch/device and revoked consent between auth and write must refuse effects.
- Target replaced/disabled after page read: new selection refuses stale ref, historical day stays readable.
- Null/zero/correction/withdraw/reopen and explicit completeness never fabricate consumption or double count versions.
- Same owner IDs on two backends and response lost after kill never transfer/recreate a command.
- Watermarks across corrections/targets and multi-page export keep one stable view; interrupted read not empty complete.

## Task1 — canonical command validation, models and owner transaction
Files: new app/models/nutrition.py, app/services/nutrition_commands.py, tests/test_nutrition_commands.py. Inputs: closed DAY/TARGET wire, public guard_owner; outputs validate/canonical_digest/apply_command(db,owner_id,namespace,key,body,auth_proof)->receipt. Tests: integer/finite/bool/unknown/duplicate strictness and vector bytes; SQLite file append/correction/null/replay/mismatch/CAS/rollback/foreign refs. Write RED, check_scope, implement minimal, targeted GREEN. Marking tables info nutrition_manual avoids accidental startupDDL; no production registration before exclusion test.

## Task2 — consent and applicability
Files: new nutrition_consent.py, tests/test_nutrition_consent.py. Interfaces read_consent/set_consent/require_consent with type nutrition_manual, wording1, monotonic timestamp CAS, owner auth proofs. RED body grant not transferable, stale wording, frozen clock ABA, races, revoke-versuswrite, status after response loss. GREEN; no BODY helper mutation.

## Task3 — reads and owned API
Files: nutrition_reads.py/mobile_nutrition.py and tests nutrition_reads/api. Interfaces head_state, list_days, targets, revisions/export under stable owner/watermark cursor; strict header/version, schemas and error mapping per protocol. Test missing versus withdrawn versus partial/known0, target refs current at selection/history thereafter, page mutation/read isolation, A/B/404/replay. Attach controlled flag in config, metadata/DDL exclusion, route inventory only under sequenced lease; no web/production exposure.

## Task4 — additive migration/dependency qualification
Files: migrations/versions/nutrition_manual_01.py, schema snapshot and test_nutrition_migration.py. Depends on actual BODY head. New tables/indexes only; legacy rows untouched, fresh upgrade/head drift, empty roundtrip, populated downgrade refuses. If parent still unmerged, test pinned composed copy with exact BODY source identified, not served runtime or fake canonical migration. Source integration waits for parent merge.

## Task5 — typed native clients and exact local recovery
Files: api/nutrition.ts/nutritionResource.ts, storage/nutritionPendingCommands.ts, sync/nutritionRecovery.ts plus tests; journal attachment lease only after BODY. Interfaces PreparedNutritionRequest, NutritionClient, pending prepare/read/ack, recovery verify/replay; backend/owner filter each operation. RED actual file SQLite reopen/lostresponse/A-B/backend, no HTTP on localfailure, stale callback and401 no hidden retry. GREEN +TypeScript; no new screen or visual grammar.

## Task6 — verification, review and delivery gates
Run real check_scope tier then targeted/broad/migration/full local memory-bounded, mobile/TS/security/spec/OpenSpec. Fresh whole technical diff review, RED/GREEN fixes, preserved minors. No full rewrite/autoUI pixel. Same change remains open until approved composition/actual native consumer/required visual and CI/merge gates; no fake COMPLETE backend-only, no feature APK.

Ruling: record technical milestones in IMPLEMENTATION_LEDGER.md; no routine plan/merge GO is re-requested after exact technical authorization. UI commits remain withheld; isolated technical source is durable before any future integration.
