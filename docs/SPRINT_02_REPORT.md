# Sprint 02 — Last Time, History Upgrade, KPIs, Alembic

Branch : `claude/sprint-reporting-fitness-app-V7Qr6`
Tests  : 52 passed (was 33)

## Shipped

- **"Dernière fois" block** on every exercise card of the
  session detail page. Identity key =
  `(template_slug_snapshot, exercise_code_snapshot)`.
  One batched SQL query, then Python picks the first hit per
  exercise code. Clean empty states for "no prior session" vs
  "prior session with no completed work data".
- **History upgrade**:
  - filter bar (Tout / En cours / Terminées) via `?status=`
  - per-session `X/Y exos` badge (exercise cards completed
    based on work sets all `completed=True`)
  - existing status / concentration / global_state badges kept
- **Progress page** (no longer a stub):
  - 4 KPI cards: sessions_this_week, completed_last_30,
    completion_rate_30d, avg_success_score_30d
  - Per-template breakdown with n_completed, last_done_at,
    avg_success_score
  - Explicit rule note at the bottom
- **Alembic baseline**: `alembic.ini`, `migrations/env.py`
  (reads DATABASE_URL from `app.config`), first migration
  auto-generated from the current metadata, `render_as_batch`
  enabled for SQLite.
- **19 new tests** (33 -> 52) covering last_time, KPIs, history
  upgrade, Alembic presence and wiring.

## Decisions taken

### Last time format
**Option B**: `Dernière fois · il y a 5 j · 60 / 62.5 / 55 kg · 10 / 8 / 12 reps`
Weights and reps are joined with " / " in set_index order.
Only completed work sets with at least one of weight or reps
populated contribute.

### Identity for last time lookup
`(template_slug_snapshot, exercise_code_snapshot)`. This prevents
cross-template leakage (E2 Push A vs E2 Pull B are different
exercises).

### Completed sessions stay editable
The session detail page does NOT switch to read-only for
`status=="completed"` sessions. The status badge changes
("Terminée"), the "Terminer" button becomes a secondary
"Rouvrir" button, and every field stays editable. Rationale:
avoids a parallel read-only template and the drift it brings;
gives the user a simple way to fix a mistake after ending.

### KPI exclusion rules
- Warmup rows never contribute to work-set KPIs.
- In-progress sessions are excluded from long-term averages and
  rates (they would drag metrics down with untouched rows).
- NULL `success_score` values are excluded from the average, not
  treated as 0.
- 30d window = `now - 30 days`, no timezone tricks.
- `sessions_this_week` is based on ISO week (Monday 00:00 UTC).

### Alembic posture
- `env.py` reads DATABASE_URL from `app.config.get_settings()`.
- `alembic.ini` has no hardcoded URL.
- `init_db()` still runs `create_all()` on boot so a fresh clone
  just works; alembic manages subsequent changes.
- `render_as_batch=True` for SQLite.

## Files

### Created
- `app/services/stats.py`
- `app/services/kpis.py`
- `alembic.ini`
- `migrations/env.py`
- `migrations/script.py.mako` (alembic init, unchanged)
- `migrations/README`
- `migrations/versions/20260408_1957_ef67ec29e3e0_initial_baseline.py`
- `tests/test_last_time.py`
- `tests/test_kpis.py`
- `tests/test_history_upgrade.py`
- `docs/SPRINT_02_REPORT.md`

### Modified
- `app/routers/sessions.py` — include last_time in detail context
- `app/routers/pages.py` — history filter + per-session counts;
  progress page with KPI cards
- `app/templates/session_detail.html` — "Dernière fois" block
- `app/templates/history.html` — filter bar, counts badge
- `app/templates/progress.html` — full rewrite (KPI cards)
- `app/static/css/app.css` — last-time, filter-bar, kpi-card,
  template-kpi, kpi-note styles
- `docs/PRODUCT_SPEC.md` — completed session rule, last time
  rule, KPI rules, invalid enum rule
- `docs/DOMAIN_MODEL.md` — read-side helpers, Alembic note
- `docs/ARCHITECTURE.md` — Alembic workflow, dev/PG path
- `README.md` — docs links + Sprint 2 summary

### Deleted
None.

## Tests

```
tests/
  test_health.py              1
  test_library.py             9
  test_session_schema.py      2
  test_session_builder.py     4
  test_session_flow.py       17
  test_last_time.py           6  ← new
  test_kpis.py                7  ← new
  test_history_upgrade.py     6  ← new
  ----                        --
  total                      52
```
