# Sprint 06 — Operational Hardening, Scheduled Backups, Restore Path

Branch : `claude/sprint-reporting-fitness-app-V7Qr6`
Tests  : 126 passed (was 115)

## Shipped

- **Refactored exports**: serialisation logic extracted to
  `app/services/export_builder.py` with `build_json_payload(db)`
  and `build_csv_text(db)`. The HTTP routes are now thin
  wrappers; the standalone backup script reuses the SAME
  builder so JSON and CSV bytes are guaranteed identical
  between the web download and the cron dump.
- **Standalone backup script** at `scripts/backup_sessions.py`
  that opens its own DB session, writes
  `sessions-YYYYMMDD_HHMM.json` and `.csv` to `BACKUP_DIR`, and
  prunes anything older than `BACKUP_RETENTION_DAYS`. No HTTP,
  no uvicorn dependency. Runs from cron, systemd, or manually.
- **Backup inspector helper** at `app/services/backup_inspector.py`:
  `latest_backup_info()` and `list_backups()` for read-only
  filesystem checks. Used by the /export landing page and the
  CLI helper script.
- **`scripts/list_backups.py`**: CLI helper that lists every
  backup file in `BACKUP_DIR`, oldest first, with size + mtime.
  Exit 0 if at least one backup exists, 1 otherwise.
- **systemd units**: `deploy/workout-backup.service` (oneshot)
  + `deploy/workout-backup.timer` (daily 03:30 UTC,
  `Persistent=true`, `RandomizedDelaySec=120`).
- **`/export` landing page upgrade**: a new "Sauvegarde
  planifiée" card now shows the latest detected backup file
  (name, size, modified-at), or a clean empty state pointing
  the user to the deploy doc.
- **`backup_dir` and `backup_retention_days`** added to
  `app/config.Settings` so both the web app and the script
  share the same source of truth (env-driven).
- **`deploy/README.md` overhaul** of three sections:
  - Section 5 (Protection minimale V1): full nginx vhost
    example with `auth_basic` + `/healthz` exempt + `/static/`
    exempt + an explicit "Ce qui est exposé / pas exposé" table
  - Section 7 (Sauvegardes): three-layer backup story with the
    new systemd units AND a cron alternative; explicit env-var
    table; manual test commands
  - Section 8 (Restauration): three concrete scenarios
    (rollback / new VPS / ad hoc analysis) + the V1
    recommendation.
- **11 new tests** (115 -> 126).

## Decisions

### Builder is the single source of truth for both formats
Before Sprint 6, the JSON and CSV serialisation lived inline in
the route handlers. The backup script would have had to either
duplicate them or call the routes via HTTP. Extracting the
builder makes both producers byte-equivalent and unit-testable.
A parity test (`test_json_route_uses_export_builder` +
`test_csv_route_uses_export_builder`) prevents future drift.

### Backup script reads SQLite directly, not via HTTP
Two reasons:
1. The backup must work even if uvicorn is down for maintenance.
2. No auth-bypass loopback hack needed if nginx basic_auth is
   active in front.
The script just opens a `SessionLocal()` and calls the builder.

### `BACKUP_DIR` is configurable via env var
Both `Settings.backup_dir` and the script accept it. In dev it
falls back to `<repo>/var/backups`; in prod the systemd unit
loads `/srv/workout/.env` which sets it to
`/srv/workout/var/backups`.

### Retention defaults to 30 days, 0 = disable
A simple `find -mtime` style prune. The script does it itself
so no extra cron line is needed.

### systemd is recommended over cron
Reasons: `Persistent=true` re-runs after a missed boot,
`RandomizedDelaySec` avoids cron stampedes, and the unit
inherits the `EnvironmentFile=/srv/workout/.env` from the main
service. Cron is documented as the simpler alternative.

### Latest-backup signal lives on /export, not /
The user goes to `/export` when they think about backups. Adding
the signal to `/` would clutter the home tile grid for almost
no benefit.

### No app-level auth — period
The product cadrage was explicit. nginx basic_auth + the
"exposed routes" table in deploy/README.md cover the V1
threat model.

## Files

### Created
- `app/services/export_builder.py`
- `app/services/backup_inspector.py`
- `scripts/backup_sessions.py`
- `scripts/list_backups.py`
- `deploy/workout-backup.service`
- `deploy/workout-backup.timer`
- `tests/test_backup_workflow.py`
- `docs/SPRINT_06_REPORT.md`

### Modified
- `app/config.py` — `backup_dir`, `backup_retention_days`
- `app/routers/export.py` — slimmed down to thin wrappers around
  `export_builder.build_json_payload` /
  `export_builder.build_csv_text`; `/export` landing now calls
  `latest_backup_info`
- `app/templates/export.html` — new "Sauvegarde planifiée" card
  with the latest-backup-or-empty-state UI
- `deploy/README.md` — sections 5, 7, 8 overhauled
- `docs/ARCHITECTURE.md` — services tree updated +
  "Backup workflow (Sprint 6)" subsection

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
  test_backup_workflow.py          11   ← new
  -----                            ---
  total                            126
```
