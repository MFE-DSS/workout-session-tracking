# REL03 canonical schema compatibility repair — implementation plan and ledger

**Goal:** admit the actual canonical `nutrition_manual_01` schema to the existing whole-DB verification/backup/release gates without changing their strictness or performing a migration remotely.
**Architecture:** keep one explicitly pinned supported server schema and exact canonical SQLite shape/integrity/FK guards. Replace the artificial snapshot-plus-old-revision test fixture with real Alembic migrations; exercise its existing identity/server/ownership/pipeline consumers.
**Spec/authorization:** `BUILD_AUTHORIZATION.md`, `BUILD_SCOPE.md`, `TEST_SPEC.md`; correction of the already authorized backup/identity engineering. Canonical starting SHA `59a28dc6db2554babc924701e11fe9f1a86bf613`. Root requested implementation inline, then independent review, with no commit/push by this worker.

## Brainstorming / Options / Risques / Choix retenu

- Option1: accept any Alembic revision/shape. Rejected: admits unqualified older/future DBs and weakens release safety.
- Option2: stamp old PLAN head or manufacture test schema. Rejected: conceals real migration state and produces invalid continuity evidence.
- **Choice:** pin `nutrition_manual_01` consistently in database, release compatibility and tracked candidate; prove full migrated synthetic DB preservation and older/forged/schema/FK/corruption refusal. No new migration or runtime auto-upgrade.
- Risks: a future canonical migration must intentionally update this compatibility boundary; historical PLAN backups remain evidence of their source, not silently admitted current deployments. Tests must not derive expected head from the code under test. All row reads/writes in this repair are disposable synthetic local fixtures only.
- Ruling: this is a narrow corrective continuation of existing REL03 engineering, not a new OVH implementation. Provider, exact-origin admission, BODY/NUT/LIB runtime activation/configuration, operational host support, remote service/DNS/secrets, EAS/native/UI remain separate pending proposals. No implicit deployment authorization.

## Owned files and task

Production: `tools/qa_delivery/database.py`, `tools/qa_delivery/releases.py`, `docs/release/rel-03/candidate.json`. Tests: `tests/test_qa_delivery_database.py`, release/server expectations and existing QA delivery consumer tests as needed. Docs: this ledger, `deploy/qa/README.md`, minimal existing REL03 preparation notes/tasks. No shared app/migration/schema snapshot changes.

1. [x] RED: migrate the synthetic QA fixture using `alembic upgrade head` instead of copying DDL/stamping. Assert actual `nutrition_manual_01`, full backup/export/restore continuity and fresh destinations. Exercise prepared+approved release against that real observed head. Add older genuine migrated and forged-head/malformed/FK refusal cases.
2. [x] Run `check_scope` before tests. Observe expected schema verification/release refusals with old code; preserve RED evidence outside Git.
3. [x] GREEN: align explicit production/candidate pins and consumer expectations only; retain exact schema/integrity/FK validation and destination no-overwrite guards.
4. [x] Run targeted regression files and broad scoped QA delivery/gateway + BODY/NUT migration/schema consumers in bounded serial batches, ruff budget/spec/OpenSpec checks. No full local sweep; required real PR CI remains root delivery responsibility.
5. [x] Record exact outcomes/limitations; hand off uncommitted diff for fresh root review.

## Review focus

Real migration head/shape admission; genuine older or forged current head refusal; all auth/PLAN/BODY/NUT rows/digests retained through fresh-path export+restore; malformed/FK/integrity refusal before destination publication; candidate identity/server-schema consistency while PREPARED stays nondistributable.

## Execution ledger

- Preflight: database SCHEMA is consumed by identity/server/ownership; release COMPATIBILITY is consumed by candidate validator/pipeline. Existing fixture manually stamped PLAN onto current snapshot, explaining the false compatibility signal. No public API/signature changes needed.
- RED: four intended regressions failed in0.89s before production edits: `test_real_canonical_migration_is_verified_without_revision_stamping`, full backup/export/restore, actual migrated-schema release gate, tracked-candidate preparation. First two raised `qa_database_invalid`, release raised `qa_release_refused`, tracked candidate still declared PLAN.
- GREEN: `database.py`, `releases.py` and tracked candidate now pin `nutrition_manual_01`; no validator branch/shape/FK/integrity/manifest/overwrite guard changed. Real canonical migration template executes once/session, then fresh independent copies receive populated synthetic auth/PLAN/BODY/NUT facts. Independent release regression also reads its observed actual migration head.
- Targeted: `python -m pytest -q tests/test_qa_delivery_database.py tests/test_qa_delivery_releases.py tests/test_qa_delivery_server.py tests/test_qa_delivery_pipeline.py` → **264passed in50.51s**.
- Broad scoped consumers: `python -m pytest -q tests/test_qa_delivery_bootstrap.py tests/test_qa_delivery_proofs.py tests/test_release_qa_gateway.py tests/test_body_operations_migration.py tests/test_nutrition_migration.py tests/test_nutrition_models.py` → **93passed in15.10s**. All six QA delivery modules plus gateway and BODY/NUT storage/migration boundaries exercised; no full sweep.
- Local interpreter: existing `/Users/martinfeldmann/workout-session-tracking/.venv/bin/python`, Python3.14.7; no installation. `check_scope` before runs: ISOLATED. Changed Python files ruff clean; budget260≤548, spec protocol and `openspec validate rel-03-continuous-android-qa --strict` pass; `git diff --check` clean. Initial budget command lacked the existing venv's `ruff` on PATH; corrected PATH, no dependency/code change. One new test import-order warning was corrected before final checks.
- Source/test freeze after import correction; subsequent edits documentation only. Root fresh independent review pending at local publication. No commit/push/PR/CI/merge claim by this worker. [Local receipt](../../../docs/release/rel-03/SCHEMA_COMPATIBILITY_RECEIPT_20261115.md); root owns review and actual delivery gates.
- Security/check detail: `python scripts/check_scope.py` final diff13files → ISOLATED. `openspec validate --all --strict --no-interactive` →27passed/0failed. Bandit1.9.4 on the two changed tools reports four findings identical to the exact starting canonical by rule/line/severity/confidence/source: database.py:75/78 B608 MEDIUM, releases.py:313 B404 LOW and324 B603 LOW; zero new issues, no errors/rule suppression. Gitleaks8.30.1 diff+both complete new-document scan →0findings, no ignore changes. Existing synthetic raw export-copy test is not proof of encrypted off-service export/custody; proof crypto is exercised separately and locally in the proofs batch. No external export/upload was performed.
- Boundary: REL03 operational remains **ACTIVE / NOT READY**. Old backups are not silently relabeled/migrated; any future cutover/migration/export uses an independently authorized synthetic copy procedure. OVH/provider/exact hostname/runtime feature configuration/production/DNS/secrets/APK/OTA/physical acceptance unchanged and not approved here.

- Fresh independent review completed before commit: no Critical/Important or actionable Minor; frozen source/test/candidate diff SHA256 `2e2dd3bb70f70b91a57ca237074561cb564b5475e0e1c032322059ef6407475c`. Root verified the final documentation and local evidence. PR and canonical CI remain delivery gates; whole REL03 operational tasks stay open.
