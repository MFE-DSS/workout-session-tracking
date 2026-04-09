# Sprint 07 — Backup Integrity, Strict Health, First-Deploy Checklist

Branch : `claude/sprint-reporting-fitness-app-V7Qr6`
Tests  : 149 passed (was 126)

## Shipped

- **Backup integrity verifier** (`app/services/backup_verifier.py`):
  `verify_latest_backup(backup_dir, db=None)` returning a
  `BackupVerification` dataclass. Validates: file presence,
  JSON parseability, `schema_version == 1`, `count` ↔
  `sessions` consistency. Reports live DB session count as an
  informational field.
- **CLI verifier** (`scripts/verify_backup.py`): standalone
  entry point for cron / systemd. Exits 0 / 1, prints a
  one-line summary + per-field block.
- **Strict health endpoint** (`GET /healthz/strict`): JSON
  report on DB + `BACKUP_DIR` + latest backup presence /
  validity. Returns 200 / "ok" on a healthy state (including
  fresh deploys with no backup yet), 503 / "degraded" when the
  DB is down or a present backup is invalid. JSON shape locked
  by a contract test.
- **`/export` integrity display**: inline integrity badge
  (**OK** / **FAIL**), age label ("il y a 2 h"), exported vs
  live count, and a red error box when the verifier returns
  errors. Cheap (one file read + one COUNT query).
- **Optional verifier systemd units**:
  `deploy/workout-backup-verify.service` (oneshot) +
  `deploy/workout-backup-verify.timer` (daily 04:00 UTC, 30
  minutes after the backup, `Persistent=true`).
- **First-deploy / update / verification / restore
  checklist** (`deploy/CHECKLISTS.md`): four concrete
  tickable sections with the exact commands AND the expected
  output at each step.
- **`relative_hours_ago` helper** added to
  `app/services/time_format.py` (à l'instant / N min / N h /
  hier / N j / N mois). Used by `/export` for the backup age
  label.
- **23 new tests** (126 → 149).
- Documentation refreshed: deploy/README.md (sections 7.3, 7.4,
  7.5 + checklists pointer at the top), docs/ARCHITECTURE.md
  (services tree + new "Strict health + backup verifier"
  subsection), README.md, new `docs/SPRINT_07_REPORT.md`.

## Decisions

### Count mismatch with the live DB is NOT a fatal error
Backups are nightly, the live DB drifts during the day. A count
diff is normal. The verifier reports `live_session_count` as an
informational field so the operator can eyeball "did I train
today?", but the verifier's `ok` boolean only flips False on
truly broken states (missing file, broken JSON, missing fields,
wrong schema_version, internal inconsistency).

### Fresh deploys do NOT trip `/healthz/strict`
On a brand-new VPS the backup cron hasn't run yet, so no
`sessions-*.json` exists. The strict endpoint treats "no backup
present" as "nothing to verify" and returns 200 / "ok". Only a
PRESENT-but-INVALID backup marks the state as degraded. This
lets operators enable the endpoint immediately without getting
a spurious 503 on day 1.

### Both health endpoints stay public
`/healthz` is the standard public liveness probe. `/healthz/strict`
exposes the latest backup filename, size, age, schema_version,
and session count. None of that is secret in V1 (single user,
single VPS), so it also stays public by default. Operators can
move it under nginx basic_auth if they prefer; the entry is
documented in `deploy/README.md` section 7.5.

### Verifier is a pure function, not a method on a model
The verifier takes a filesystem path and an optional DB session.
Zero model coupling. Makes it trivially unit-testable (16 of
the 23 new tests poke it directly), and lets the CLI script
bypass the FastAPI router entirely.

### One verifier, three consumers
The same `verify_latest_backup` function powers:
- `scripts/verify_backup.py` (CLI)
- `GET /healthz/strict` (route)
- `GET /export` (route, inline badge)
Ensures all three surfaces report the same verdict for the same
state.

### CHECKLISTS.md is a separate file
`deploy/README.md` is already long. A dedicated checklist file
reads faster in a terminal and can be grep'd step-by-step
during a real deploy.

## Files

### Created
- `app/services/backup_verifier.py`
- `scripts/verify_backup.py`
- `deploy/workout-backup-verify.service`
- `deploy/workout-backup-verify.timer`
- `deploy/CHECKLISTS.md`
- `tests/test_ops_closure.py`
- `docs/SPRINT_07_REPORT.md`

### Modified
- `app/routers/health.py` — adds `/healthz/strict`, imports the
  verifier and `get_settings`. Docstring explains the split
  between the public `/healthz` and the operator-facing strict
  endpoint.
- `app/routers/export.py` — computes the verifier result and
  relative age label inline, passes both to the template.
- `app/services/time_format.py` — adds `relative_hours_ago()`.
- `app/templates/export.html` — renders the integrity badge, age
  label, schema_version line, exported-vs-live count line, and
  an error box.
- `app/static/css/app.css` — `.integrity-ok`, `.integrity-fail`,
  `.integrity-errors`.
- `deploy/README.md` — new sections 7.3 (three-signal
  verification), 7.4 (planned verification), 7.5 (strict
  health surface), plus a pointer to CHECKLISTS.md at the top.
- `docs/ARCHITECTURE.md` — services tree (+ `backup_verifier.py`,
  updated `time_format.py`), new "Strict health + backup
  verifier (Sprint 7)" subsection.
- `README.md` — Sprint 7 report link + strict health mention.

### Deleted
None.

## Tests

```
tests/
  test_health.py                    1
  test_library.py                   9
  test_session_schema.py            2
  test_session_builder.py           4
  test_session_flow.py             17
  test_last_time.py                 6
  test_kpis.py                      7
  test_history_upgrade.py           6
  test_progression_hint.py         10
  test_export.py                    4
  test_past_session_readability.py  5
  test_delta.py                     9
  test_exercise_history.py         13
  test_alembic_drift.py             2
  test_mobile_polish.py            14
  test_csv_export.py                6
  test_backup_workflow.py          11
  test_ops_closure.py              23   ← new
  -----                            ---
  total                            149
```
