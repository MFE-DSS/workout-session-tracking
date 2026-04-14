# Sb_cardio_capture — Cardio Data Capture + `liss-only` Template

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make cardio sessions loggable with proper data (duration, BPM avg, machine calories, machine type), add a `liss-only` template for cardio pur sans abdos, and enforce anti-pseudo-science wording in the UI.

**Architecture:** Alembic migration adds 4 nullable fields to `WorkoutSession`. Catalog bump v7→v8 adds `liss-only` (preserving `liss-abs` for historical continuity — ADD, not rename). Session detail template shows a "Cardio" section at the top when `session.template.kind == "cardio"`. Machine calories field has explicit "(indicatif)" label. Zero impact on scoring (dashboard, physique).

**Tech Stack:** SQLAlchemy 2.0, Alembic (batch_alter_table), FastAPI form, Jinja2

---

## 6 arbitrages verrouilles respectes

- (3) Option A : 2 templates separes (`liss-only` + `liss-abs` preserve)
- (6) reference_split.json = source de verite (bump version)
- Wording strict anti-pseudo-science sur calories

---

## File Structure

| File | Responsibility |
|------|---------------|
| `app/models/session.py` | Modify — add 4 cardio fields to WorkoutSession |
| `migrations/versions/20260414_add_cardio_fields.py` | **New** — add nullable columns |
| `data/reference_split.json` | Modify — bump to v8, add `liss-only` template |
| `app/services/seed.py` | No change needed (JSON-driven) |
| `app/routers/sessions.py` | Modify — `update_session` parses cardio fields |
| `app/templates/session_detail.html` | Modify — render cardio section at top for `kind=cardio` |
| `app/services/export_builder.py` | Modify — include cardio fields in JSON/CSV export |
| `tests/test_cardio_capture.py` | **New** — cardio save + privacy |

---

### Task 1: Model + Migration

**Files:**
- Modify: `app/models/session.py`
- Create: `migrations/versions/20260414_add_cardio_fields.py`

- [ ] **Step 1: Add fields to WorkoutSession model**

In `app/models/session.py`, add after `bodyweight_kg` and before `free_note` (around line 98):

```python
    bodyweight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Cardio capture (Sb_cardio_capture) — relevant only for kind=cardio templates.
    # Machine calories is explicitly an indicative machine value, NEVER a
    # physiological truth. See SPIGNOS_SCIENCE_PAGE_SPEC.md section 3.
    cardio_duration_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cardio_bpm_avg: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cardio_machine_calories: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cardio_machine_type: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    free_note: Mapped[Optional[str]] = mapped_column(String(280), nullable=True)
```

- [ ] **Step 2: Create migration**

Run `alembic heads` to get current head. Create `migrations/versions/20260414_add_cardio_fields.py`:

```python
"""Add cardio capture fields to workout_sessions.

Revision ID: <generate>
Revises: <current_head>
Create Date: 2026-04-14
"""
from alembic import op
import sqlalchemy as sa

revision = "<generate>"
down_revision = "<current_head>"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("workout_sessions") as batch_op:
        batch_op.add_column(sa.Column("cardio_duration_min", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("cardio_bpm_avg", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("cardio_machine_calories", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("cardio_machine_type", sa.String(32), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("workout_sessions") as batch_op:
        batch_op.drop_column("cardio_machine_type")
        batch_op.drop_column("cardio_machine_calories")
        batch_op.drop_column("cardio_bpm_avg")
        batch_op.drop_column("cardio_duration_min")
```

Replace `<generate>` with `alembic revision --autogenerate` output or a fixed UUID string. Replace `<current_head>` with the actual head.

- [ ] **Step 3: Apply migration**

Run: `alembic upgrade head`
Run: `pytest tests/test_alembic_drift.py -v`
Expected: All pass.

- [ ] **Step 4: Commit**

```bash
git add app/models/session.py migrations/versions/20260414_add_cardio_fields.py
git commit -m "feat(sb-cardio): migration + 4 nullable cardio fields on WorkoutSession"
```

---

### Task 2: Catalog — Add `liss-only` template (ADD, not rename)

**Files:**
- Modify: `data/reference_split.json`

- [ ] **Step 1: Bump version**

At the top of `data/reference_split.json`, change:
```json
"version": "2026-04-14.v7"
```
To:
```json
"version": "2026-04-14.v8"
```

- [ ] **Step 2: Add `liss-only` template**

Insert a new template object in the `templates` array — preferably right before `liss-abs` so it appears first in the cardio group. The template has ZERO exercises (pure cardio):

```json
{
  "slug": "liss-only",
  "name": "LISS cardio pur",
  "kind": "cardio",
  "focus": "Cardio faible intensite",
  "cardio_note": "20-30 min LISS (velo, marche inclinee, rameur) a 120-130 bpm",
  "suggested_label": "Seance cardio sans abdos. Ideale entre deux seances muscu.",
  "exercises": [],
  "catalog_section": "utility",
  "display_order": 10
},
```

Leave `liss-abs` untouched (preservation historique). Adjust `display_order` of `liss-abs` if needed to keep visual ordering (e.g., move liss-abs from 11 to 12, or keep both and liss-only gets 10).

- [ ] **Step 3: Run catalog QA**

Run: `python scripts/catalog_qa.py`
Expected: PASS (0 errors). Template with 0 exercises should pass — verify the QA script handles cardio templates. If the QA script errors on "no exercises", the cardio case must be allowed (liss-abs also has exercises, but a new cardio-only template has zero).

If QA errors on zero exercises: adjust `scripts/catalog_qa.py` schema check to allow `len(exercises) >= 0` when `kind == "cardio"`. This is a legitimate relaxation — cardio templates can have no strength exercises.

- [ ] **Step 4: Run catalog integrity tests + seed**

Run: `pytest tests/test_catalog_integrity.py -v`
Expected: PASS.

Restart the app or run a test that creates a SessionLocal — the seed should detect version v8 and re-insert templates. Verify:

```bash
python -c "from app.database import SessionLocal; from app.models.catalog import WorkoutTemplate; from sqlalchemy import select; db = SessionLocal(); print([t.slug for t in db.execute(select(WorkoutTemplate)).scalars().all()])"
```

Expected: `liss-only` appears in the list.

- [ ] **Step 5: Commit**

```bash
git add data/reference_split.json scripts/catalog_qa.py
git commit -m "feat(sb-cardio): catalog v8 — add liss-only template (preserve liss-abs for history)"
```

---

### Task 3: Launcher integration (ensure `liss-only` appears)

**Files:**
- Modify: `app/services/launcher.py`

- [ ] **Step 1: Add `liss-only` to cardio branch**

In `app/services/launcher.py`, update the `BRANCH_TREE["cardio"]` entry:

```python
    "cardio": {
        "_direct": {
            "label": "Cardio",
            "slugs": ["liss-only", "liss-abs"],
        },
    },
```

Note: `liss-only` comes first because most users want cardio pur. `liss-abs` follows for those who want the cardio+core variant. Both resolve thanks to the dynamic filter.

- [ ] **Step 2: Update launcher tests**

In `tests/test_launcher.py`, update `test_resolve_branch_cardio`:

```python
def test_resolve_branch_cardio(client):
    """Cardio branch returns liss-only + liss-abs (catalog v8)."""
    from app.database import SessionLocal
    from app.services.launcher import resolve_branch
    with SessionLocal() as db:
        templates = resolve_branch(db, "cardio", None)
    slugs = [t.slug for t in templates]
    assert "liss-only" in slugs
    assert "liss-abs" in slugs
```

- [ ] **Step 3: Run tests**

Run: `pytest tests/test_launcher.py -v`
Expected: All PASS.

- [ ] **Step 4: Commit**

```bash
git add app/services/launcher.py tests/test_launcher.py
git commit -m "feat(sb-cardio): launcher cardio branch resolves liss-only + liss-abs"
```

---

### Task 4: Router — parse cardio fields on session update

**Files:**
- Modify: `app/routers/sessions.py`

- [ ] **Step 1: Update `update_session` to parse cardio fields**

In `app/routers/sessions.py`, in `update_session` (around line 243), add cardio parsing before the `action` check:

```python
    session.concentration = enum_str(form.get("concentration"), _CONCENTRATION)
    session.global_state = enum_str(form.get("global_state"), _GLOBAL_STATE)
    session.bodyweight_kg = to_float(form.get("bodyweight_kg"))
    session.free_note = clean_str(form.get("free_note"), max_length=280)

    # Cardio capture (Sb_cardio_capture) — only meaningful for kind=cardio
    # sessions but we parse unconditionally; non-cardio sessions will have
    # these fields absent from the form, resulting in None.
    session.cardio_duration_min = to_int(form.get("cardio_duration_min"))
    session.cardio_bpm_avg = to_int(form.get("cardio_bpm_avg"))
    session.cardio_machine_calories = to_int(form.get("cardio_machine_calories"))
    session.cardio_machine_type = clean_str(
        form.get("cardio_machine_type"), max_length=32
    )
```

`to_int` and `clean_str` already exist in `app.services.form_parsing`.

- [ ] **Step 2: Commit**

```bash
git add app/routers/sessions.py
git commit -m "feat(sb-cardio): router parses cardio fields on session update"
```

---

### Task 5: Template — cardio section in session detail

**Files:**
- Modify: `app/templates/session_detail.html`

- [ ] **Step 1: Add cardio section at top of session form**

In `app/templates/session_detail.html`, find the session feedback form (the `<form>` with `id="session-feedback"` which is at the bottom after the exercise cards loop).

Inside this form, BEFORE the existing "Bilan de la séance" section, add a conditional cardio section:

```html
  {% if session.template and session.template.kind == 'cardio' %}
  <h2 class="card__title">Cardio</h2>
  <p class="text-dim" style="font-size:12px;margin-bottom:var(--space-sm);">
    Donnees operatoires saisies. Elles ne sont pas une verite physiologique.
  </p>

  {% call field_group("Duree (min)") %}
    <input type="number" inputmode="numeric" name="cardio_duration_min"
           min="1" max="300" placeholder="20"
           value="{{ session.cardio_duration_min if session.cardio_duration_min is not none else '' }}" />
  {% endcall %}

  {% call field_group("BPM moyen (si mesure)") %}
    <input type="number" inputmode="numeric" name="cardio_bpm_avg"
           min="40" max="220" placeholder="125"
           value="{{ session.cardio_bpm_avg if session.cardio_bpm_avg is not none else '' }}" />
  {% endcall %}

  {% call field_group("Machine") %}
    <select name="cardio_machine_type">
      <option value="">—</option>
      <option value="velo"     {% if session.cardio_machine_type == 'velo' %}selected{% endif %}>Velo</option>
      <option value="marche"   {% if session.cardio_machine_type == 'marche' %}selected{% endif %}>Marche inclinee</option>
      <option value="rameur"   {% if session.cardio_machine_type == 'rameur' %}selected{% endif %}>Rameur</option>
      <option value="elliptique" {% if session.cardio_machine_type == 'elliptique' %}selected{% endif %}>Elliptique</option>
      <option value="autre"    {% if session.cardio_machine_type == 'autre' %}selected{% endif %}>Autre</option>
    </select>
  {% endcall %}

  {% call field_group("Calories machine (indicatif)") %}
    <input type="number" inputmode="numeric" name="cardio_machine_calories"
           min="0" max="5000" placeholder="— selon affichage machine"
           value="{{ session.cardio_machine_calories if session.cardio_machine_calories is not none else '' }}" />
  {% endcall %}
  {% endif %}

  <h2 class="card__title">Bilan de la séance</h2>
```

- [ ] **Step 2: Verify template access to session.template**

The `session.template` relationship must be loaded in `session_detail` route. Check `_load_session` in `app/routers/sessions.py`:

Current code loads `WorkoutSession` with `session_exercises` + `session_exercises.set_logs` + `session_exercises.template_exercise`. It does NOT load `session.template` directly.

Add a `selectinload(WorkoutSession.template)` to the options:

In `_load_session` in `app/routers/sessions.py`, modify:

```python
def _load_session(db: Session, session_id: int, user_id: int) -> WorkoutSession | None:
    stmt = (
        select(WorkoutSession)
        .where(WorkoutSession.id == session_id, WorkoutSession.user_id == user_id)
        .options(
            selectinload(WorkoutSession.template),  # for kind check in template
            selectinload(WorkoutSession.session_exercises)
            .selectinload(SessionExercise.set_logs),
            selectinload(WorkoutSession.session_exercises)
            .selectinload(SessionExercise.template_exercise),
        )
    )
    return db.execute(stmt).scalar_one_or_none()
```

**Important:** `WorkoutSession.template_id` has `ondelete=SET NULL` — if the template has been removed from the catalog, `session.template` may be `None`. The template condition `{% if session.template and session.template.kind == 'cardio' %}` handles this safely.

- [ ] **Step 3: Commit**

```bash
git add app/templates/session_detail.html app/routers/sessions.py
git commit -m "feat(sb-cardio): cardio section in session_detail for kind=cardio templates"
```

---

### Task 6: Export + Privacy Tests

**Files:**
- Modify: `app/services/export_builder.py`
- Create: `tests/test_cardio_capture.py`

- [ ] **Step 1: Include cardio fields in export**

In `app/services/export_builder.py`, in `serialise_session`, add cardio fields after `bodyweight_kg`:

```python
        "bodyweight_kg": s.bodyweight_kg,
        "cardio_duration_min": s.cardio_duration_min,
        "cardio_bpm_avg": s.cardio_bpm_avg,
        "cardio_machine_calories": s.cardio_machine_calories,
        "cardio_machine_type": s.cardio_machine_type,
        "free_note": s.free_note,
```

In the CSV builder, add these to the header row and data row. Find the existing header list and append the 4 cardio columns. Find the `_opt(...)` data row and append `_opt(s.cardio_duration_min)`, etc.

- [ ] **Step 2: Create cardio tests**

Create `tests/test_cardio_capture.py`:

```python
"""Tests for cardio capture flow."""
from __future__ import annotations

import re


def test_cardio_session_shows_cardio_section(client):
    """Session detail of a cardio template shows the Cardio section."""
    r = client.post("/sessions", data={"template_slug": "liss-only"}, follow_redirects=False)
    sid = int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))
    r2 = client.get(f"/sessions/{sid}")
    assert r2.status_code == 200
    assert "Cardio" in r2.text
    assert "Duree (min)" in r2.text
    assert "BPM moyen" in r2.text
    assert "Calories machine (indicatif)" in r2.text


def test_strength_session_does_not_show_cardio_section(client):
    """A strength template session does NOT show the Cardio section."""
    r = client.post("/sessions", data={"template_slug": "push-a"}, follow_redirects=False)
    sid = int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))
    r2 = client.get(f"/sessions/{sid}")
    assert r2.status_code == 200
    # "Duree (min)" must not appear on strength sessions
    assert "Duree (min)" not in r2.text


def test_cardio_fields_persist_on_save(client):
    """Submitting cardio fields persists them."""
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    r = client.post("/sessions", data={"template_slug": "liss-only"}, follow_redirects=False)
    sid = int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))

    client.post(f"/sessions/{sid}", data={
        "concentration": "medium",
        "global_state": "good",
        "cardio_duration_min": "25",
        "cardio_bpm_avg": "128",
        "cardio_machine_calories": "220",
        "cardio_machine_type": "velo",
    }, follow_redirects=False)

    with SessionLocal() as db:
        s = db.get(WorkoutSession, sid)
        assert s.cardio_duration_min == 25
        assert s.cardio_bpm_avg == 128
        assert s.cardio_machine_calories == 220
        assert s.cardio_machine_type == "velo"


def test_calories_label_warns_indicative(client):
    """The calories field label contains '(indicatif)' to avoid pseudo-science."""
    r = client.post("/sessions", data={"template_slug": "liss-only"}, follow_redirects=False)
    sid = int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))
    r2 = client.get(f"/sessions/{sid}")
    assert "Calories machine (indicatif)" in r2.text


def test_export_includes_cardio_fields(client):
    """JSON export includes cardio fields."""
    import json as json_lib
    r = client.post("/sessions", data={"template_slug": "liss-only"}, follow_redirects=False)
    sid = int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))
    client.post(f"/sessions/{sid}", data={
        "cardio_duration_min": "20",
        "cardio_bpm_avg": "120",
        "action": "end",
    }, follow_redirects=False)

    body = client.get("/export/sessions.json").text
    data = json_lib.loads(body)
    session_data = [s for s in data["sessions"] if s["id"] == sid][0]
    assert session_data["cardio_duration_min"] == 20
    assert session_data["cardio_bpm_avg"] == 120
```

- [ ] **Step 3: Run tests**

Run: `pytest tests/test_cardio_capture.py -v`
Expected: All PASS.

- [ ] **Step 4: Run full suite**

Run: `pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q`
Expected: All pass.

- [ ] **Step 5: Commit**

```bash
git add app/services/export_builder.py tests/test_cardio_capture.py
git commit -m "feat(sb-cardio): export cardio fields + privacy + label tests"
```

---

### Task 7: Sprint Report

**Files:**
- Create: `docs/SPRINT_Sb_cardio_capture_REPORT.md`

- [ ] **Step 1: Write report**

Create `docs/SPRINT_Sb_cardio_capture_REPORT.md`:

```markdown
# Sprint Sb_cardio_capture Report

**Date:** 2026-04-14
**Status:** Complete
**Spec:** docs/strategy/SPIGNOS_SESSION_ENTRY_AND_SCIENCE_TRANSVERSAL_NOTES.md

## Objective

Add cardio data capture (duration, BPM, calories, machine) and
`liss-only` template (Option A: split templates, preserve liss-abs).

## Deliverables

| Artifact | Path |
|----------|------|
| Migration | `migrations/versions/20260414_add_cardio_fields.py` |
| Model | `app/models/session.py` +4 fields |
| Catalog | `data/reference_split.json` v7→v8 with `liss-only` |
| Router | `app/routers/sessions.py` parses cardio fields |
| Template | `app/templates/session_detail.html` cardio section |
| Export | `app/services/export_builder.py` cardio fields |
| Launcher | `app/services/launcher.py` resolves liss-only + liss-abs |
| Tests | `tests/test_cardio_capture.py` |

## 6 arbitrages respectes

- (3) Option A: 2 templates separes — liss-only added, liss-abs preserved
- (6) reference_split.json bumped v7→v8
- Calories labeled "(indicatif)" — no pseudo-science

## Verification

```
pytest tests/test_cardio_capture.py -v
pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q
```
```

- [ ] **Step 2: Commit**

```bash
git add docs/SPRINT_Sb_cardio_capture_REPORT.md
git commit -m "docs(sb-cardio): sprint report — cardio capture + liss-only complete"
```
