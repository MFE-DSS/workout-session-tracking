# Architecture — V1

## Stack

- **FastAPI** as the HTTP layer
- **Jinja2** for server-side rendering (no SPA, no JS framework)
- **SQLAlchemy 2.0** (declarative, typed Mapped[...])
- **SQLite** file for V1, dialect-agnostic URL so a later switch
  to PostgreSQL is a single env var change
- **Uvicorn + nginx** on an OVH VPS (HTTPS via certbot)

## Layout

```
app/
  main.py            FastAPI app factory + lifespan (init_db + seed)
  config.py          Pydantic Settings (env-driven)
  database.py        Engine, Base, SessionLocal, SQLite FK pragma
  templating.py      Single Jinja2Templates instance
  enums.py           All normalized vocabularies
  models/
    catalog.py       Templates + rules + reference doc
    session.py       Sessions + exercises + set logs
  routers/
    health.py        /healthz
    pages.py         Catalog navigation (/, /library, /history, /progress)
    sessions.py      Logging flow (POST /sessions, GET/POST /sessions/{id},
                     /rules, /exercise-history/{slug}/{code})
    export.py        /export landing + /export/sessions.json
                     + /export/sessions.csv (Sprint 5)
  schemas/
    catalog.py       Pydantic DTOs for read APIs (future-proofing)
  services/
    seed.py              Idempotent seed of catalog + method rules
    session_builder.py   Build a session tree from a template
    form_parsing.py      Typed form field helpers (empty→None, enum whitelist)
    stats.py             last_time_by_exercise_code, summarise_current_exercise
    progression_hint.py  Pure deterministic hint rule (Sprint 3)
    kpis.py              GlobalKPIs + TemplateKPI + RecentExerciseActivity
    delta.py             Pure compute_delta + format_delta (Sprint 4)
    exercise_history.py  get_exercise_history() with row-wise deltas (Sprint 4)
    time_format.py       format_duration_short (Sprint 4)
    session_state.py     latest_open_session (Sprint 5, shared by pages
                         and sessions routers for the active banner)
    export_builder.py    build_json_payload + build_csv_text (Sprint 6)
                         used by both /export routes AND
                         scripts/backup_sessions.py
    backup_inspector.py  latest_backup_info / list_backups (Sprint 6)
                         used by /export landing page
  templates/
    base.html          Layout (topbar, manifest, safe-area)
    _macros.html       Jinja macros (segmented control, field group)
    index.html         Home tiles
    library.html       Template library + start forms
    template_detail.html
    session_detail.html  Main logging screen (one form per exercise card)
    history.html
    progress.html
    rules.html
  static/
    css/app.css      Mobile-first dark theme
    manifest.webmanifest
data/
  reference_split.json  Workout template catalog (source of truth)
  method_rules.json     Static method cards
scripts/seed_db.py   CLI (re)seed
deploy/              systemd + nginx + OVH guide
tests/               pytest + httpx
docs/                this folder
```

## Request flow

```
       browser (phone)
          │
      HTTPS
          │
     nginx :443
          │
    proxy_pass → uvicorn :8000
          │
        FastAPI
          │
   ┌──────┴────────┐
   │router         │
   │pages / sessions│
   └──────┬────────┘
          │
     SQLAlchemy
          │
       SQLite
```

## Form strategy (V1 decision)

The session detail page uses **two kinds of forms**:

1. **One small session-level form** at the top:
   `concentration`, `global_state`, `bodyweight_kg`, `free_note`,
   plus `Enregistrer` and `Terminer la séance` buttons.
   Submitted to `POST /sessions/{id}`.

2. **One form per exercise card**. Each card owns its
   exercise-level feedback (`success_score`, `muscle_sensation`,
   `free_note`) **and** all its warmup + work set rows. The card
   is submitted as a single POST to
   `POST /sessions/{id}/exercises/{session_exercise_id}`.

No monolithic whole-session form. No per-set PATCH. This matches
the "card = ergonomic unit" principle: the user fills an exercise
in one natural block, taps save, and moves on.

Form field names for set rows are prefixed by `set_{id}_` so the
exercise card form can carry every set at once without ambiguity.

No JS is required for the flow to work. JS can be layered later
for niceties (debounced auto-save, rest timer) without touching
the routes.

## Persistence rules

- Every POST returns `303 See Other` to a GET of the same page.
- Empty strings posted in text inputs are normalized to `None`.
- Invalid enum values posted (e.g. `concentration=EXTREME`) are
  dropped, set to `None`. Silent drop is preferred over 400 on
  a single-user SSR app.
- Checkboxes that are not in the form payload mean `False`.
- Snapshot columns (`template_*_snapshot`, `exercise_*_snapshot`)
  are filled exclusively by the server at session creation time.
  They are never exposed to user forms.

## Seed strategy

- `seed_reference_split()` is keyed on `ReferenceDoc.version`. If
  the version in `data/reference_split.json` matches the current
  row, it's a no-op. Otherwise it wipes the 3 catalog tables and
  rebuilds them.
- `seed_method_rules()` is unconditional (8 rows, no inbound FK).
- Both run on every app boot from the lifespan.

## Alembic workflow (Sprint 2)

The repo now uses Alembic for schema evolution. The baseline
migration in `migrations/versions/` captures the full schema as
of the end of Sprint 1.

### Dev workflow

```bash
# Apply every pending migration to the local DB
alembic upgrade head

# Show the currently applied revision
alembic current

# Generate a new revision after editing SQLAlchemy models
alembic revision --autogenerate -m "add xxx column"

# Review the generated file, edit if needed, then apply
alembic upgrade head
```

The Alembic config (`alembic.ini`) does **not** hardcode a DB
URL. The URL is injected at runtime by `migrations/env.py` from
`app.config.get_settings()`, so one `DATABASE_URL` env var drives
both the app and the migrations.

### Dev boot coexistence

`app/database.py::init_db()` still calls `Base.metadata.create_all()`
on lifespan to make fresh clones work out of the box. On an empty
database this creates every table. On an existing Alembic-managed
database it is a no-op (create_all skips tables that already
exist).

The recommended flow for a new environment is:

```bash
rm -rf var/workout.db            # or start on a fresh server
alembic upgrade head             # Alembic manages the schema
uvicorn app.main:app --reload    # lifespan seeds catalog + rules
```

### SQLite notes

- `render_as_batch=True` is enabled in `env.py` for SQLite
  engines, so Alembic rewrites ALTER TABLE operations using the
  copy-and-rename dance (the only way to drop/modify a column
  on SQLite).
- Alembic's `alembic_version` bookkeeping table coexists with the
  app tables without interfering.

### PostgreSQL migration path (future)

Switching to PostgreSQL later is a one-env-var change:

```bash
DATABASE_URL=postgresql+psycopg://user:pwd@host/workout
alembic upgrade head
```

All migrations were written with portable SQLAlchemy operations;
the `compare_type=True` setting in `env.py` means type changes
(e.g. `String(16)` -> `String(32)`) will be picked up by
autogenerate rather than silently ignored.

### Backup workflow (Sprint 6)

The backup story has three layers:

1. **SQLite `.backup`** — atomic file snapshot, restoration in
   place. Cron'd from the `workout` user.
2. **JSON dump** — full nested journal payload, written by
   `scripts/backup_sessions.py` using `app.services.export_builder`.
   The standalone script never touches HTTP.
3. **CSV dump** — flat one-row-per-set view, also produced by
   the script via the same builder.

Both #2 and #3 land in `BACKUP_DIR` (env var, defaults to
`<repo>/var/backups`). Files are named `sessions-YYYYMMDD_HHMM.json`
and `sessions-YYYYMMDD_HHMM.csv`. The script prunes anything
older than `BACKUP_RETENTION_DAYS` (default 30, set to 0 to
disable).

Two scheduling options ship in `deploy/`:

- `workout-backup.service` + `workout-backup.timer` (systemd,
  recommended)
- A cron one-liner (documented in `deploy/README.md` section 7.2)

The `/export` landing page calls `latest_backup_info(BACKUP_DIR)`
on every request and shows the most recent file's name, size,
and modified-at timestamp — a sanity signal that the cron is
alive without leaving the app. When no file is found, an empty
state explains how to enable the timer.

### Drift guard (Sprint 4)

A forgotten autogenerate is the single most common Alembic
failure mode. We prevent it with two paths:

1. **Pytest test** — `tests/test_alembic_drift.py` runs the full
   migration chain on a throwaway SQLite file, then uses
   `alembic.autogenerate.compare_metadata` to diff the resulting
   schema against `Base.metadata`. A non-empty diff fails the
   test with a human-readable error.

2. **Manual script** — `python -m scripts.check_alembic_drift`
   does exactly the same thing, exits 0 on clean state, 1 on
   drift, printing the diff. Suitable for a pre-commit hook.

`migrations/env.py` was updated to skip the DATABASE_URL injection
if the Alembic `Config` already has a `sqlalchemy.url` set. This
is what lets the test inject a temp SQLite URL without touching
environment variables.
