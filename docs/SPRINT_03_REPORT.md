# Sprint 03 — Progression Hint, Past Session Readability, Export

Branch : `claude/sprint-reporting-fitness-app-V7Qr6`
Tests  : 71 passed (was 52)

## Shipped

- **"Repère" progression hint** on every exercise card. Pure
  function in `app/services/progression_hint.py`, documented
  rule in `docs/PRODUCT_SPEC.md`, wired into the session
  detail context.
- **Completed session readability**:
  - `session-page--completed` class on the main container
  - header note "Séance terminée — éditable via Rouvrir"
  - per-exercise-card `done-summary` strip showing
    "Work : N/M · weights · reps · score X"
  - inputs slightly dimmed via `opacity: 0.82`
  - exercise card and session feedback borders flipped to
    the "ok" green accent
- **Recent exercise activity** section on /progress:
  rolling-30-days list of exercise codes, grouped by
  (template_slug, exercise_code), with last weights/reps
  of the most recent completed session. Excludes in-progress
  sessions.
- **JSON export** at `GET /export/sessions.json`:
  - all sessions, sorted oldest-first
  - `schema_version: 1`
  - stable shape (session-level + exercises + sets)
  - no internal ids beyond the session id
  - Content-Disposition attachment with a timestamped filename
- **Operational docs**:
  - `deploy/README.md` adds explicit `alembic upgrade head`
    step in both initial deploy and update flows
  - new "Protection minimale V1" section with nginx basic_auth
    example + /healthz escape hatch
  - new backup section covering both SQLite `.backup` and
    JSON export; cron snippets included
- 19 new tests (71 total, all green).

## Decisions

### Progression hint rule (frozen)

Given `(target_min, target_max, prior_weight_kg, prior_reps)`:
- Any input missing -> `None`
- `prior_reps >= target_max` -> "tenter d'augmenter la charge
  sur le premier set"
- `prior_reps < target_min` -> "consolider la charge actuelle"
- otherwise -> "viser {target_max} reps avant d'augmenter la
  charge"

Only the first rep target + first completed work set are used.
The hint is secondary to "Dernière fois" in the UI (smaller
footprint, accent border, clear label).

### Completed-session styling = subtle, not read-only

The V1 rule from Sprint 2 stays: completed sessions remain
editable. The Sprint 3 improvements are purely visual:
readability markers, compact summary strips, dimmer inputs.
No disabled form controls, no parallel template.

### /progress addition kept small

One new section only: "Activité récente par exercice". KPI
grid + template breakdown stay as-is. No charts.

### Export format

JSON only (Option A in the spec). schema_version = 1. One
payload per request, no pagination, no filtering. Good enough
for a single-user backup workflow.

## Files

### Created
- `app/services/progression_hint.py`
- `app/routers/export.py`
- `tests/test_progression_hint.py`
- `tests/test_export.py`
- `tests/test_past_session_readability.py`
- `docs/SPRINT_03_REPORT.md`

### Modified
- `app/services/stats.py` — expose `first_set` in last_time,
  add `summarise_current_exercise()`
- `app/services/kpis.py` — add `RecentExerciseActivity` and
  `compute_recent_exercise_activity()`
- `app/routers/sessions.py` — compute hints and exercise summaries
- `app/routers/pages.py` — progress page receives recent_activity
- `app/main.py` — mount export router
- `app/templates/session_detail.html` — session-page wrapper,
  header note, done-summary strip, hint block
- `app/templates/progress.html` — recent activity section
- `app/static/css/app.css` — hint, done-summary, activity-row,
  session-page--completed styles
- `deploy/README.md` — Alembic workflow, basic_auth section,
  backup workflow (SQLite + JSON export), PostgreSQL path
- `docs/PRODUCT_SPEC.md` — progression hint rule, completed-
  session readability addendum, export rule, non-goals update
- `docs/DOMAIN_MODEL.md` — read-side helpers updated
- `docs/ARCHITECTURE.md` — layout updated with new services
- `README.md`

### Deleted
None.

## Tests

```
tests/
  test_health.py                 1
  test_library.py                9
  test_session_schema.py         2
  test_session_builder.py        4
  test_session_flow.py          17
  test_last_time.py              6
  test_kpis.py                   7
  test_history_upgrade.py        6
  test_progression_hint.py      10  ← new
  test_export.py                 4  ← new
  test_past_session_readability  5  ← new
  ----                          --
  total                         71
```
