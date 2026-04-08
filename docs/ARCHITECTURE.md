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
    sessions.py      Logging flow (POST /sessions, GET/POST /sessions/{id}, /rules)
  schemas/
    catalog.py       Pydantic DTOs for read APIs (future-proofing)
  services/
    seed.py          Idempotent seed of catalog + method rules
    session_builder.py  Build a session tree from a template
    form_parsing.py     Typed form field helpers (empty→None, enum whitelist)
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
