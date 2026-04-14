# Sb_03 — Minimal Substitution Graph Build Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add exercise substitution to the session flow — users can swap a prescribed exercise for an equivalent from a catalogue-defined list, with the actual exercise tracked for analytics.

**Architecture:** Two new DB columns (`substitutes_json` on TemplateExercise, `substituted_name` on SessionExercise). Substitution lists in `reference_split.json`. A select dropdown in the exercise card (locked after first completed set). `muscle_scoring` uses actual exercise name for zone classification.

**Tech Stack:** SQLAlchemy 2.0, Alembic, FastAPI form parsing, Jinja2, pytest

---

## File Structure

| File | Responsibility |
|------|---------------|
| `app/models/catalog.py` | Add `substitutes_json` to TemplateExercise |
| `app/models/session.py` | Add `substituted_name` to SessionExercise |
| `app/services/substitution.py` | **New** — `actual_exercise_name()`, `get_substitutes()`, `can_substitute()` |
| `app/services/seed.py` | Read and store `substitutes` from JSON |
| `app/services/muscle_scoring.py` | Use `actual_exercise_name()` for classify |
| `app/routers/sessions.py` | Parse `substituted_name`, enforce lock |
| `app/templates/session_detail.html` | Select dropdown / static badge |
| `data/reference_split.json` | Add `substitutes` to ~10 exercises, bump version |
| `migrations/versions/...` | 1 migration (2 columns) |
| `scripts/catalog_qa.py` | Add substitute classifiability check |
| `tests/test_substitution.py` | **New** — service + route tests |

---

### Task 1: Migration + Model Changes

**Files:**
- Modify: `app/models/catalog.py`
- Modify: `app/models/session.py`
- Create: `migrations/versions/20260414_add_substitution.py`

- [ ] **Step 1: Add `substitutes_json` to TemplateExercise**

In `app/models/catalog.py`, add after the `notes` field on TemplateExercise (line 80):

```python
    substitutes_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
```

- [ ] **Step 2: Add `substituted_name` to SessionExercise**

In `app/models/session.py`, add after the `free_note` field on SessionExercise (line 146):

```python
    substituted_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
```

- [ ] **Step 3: Create the migration**

Run `alembic heads` to get the current head. Create the migration:

```python
"""Add substitution columns — substitutes_json on template_exercises, substituted_name on session_exercises.

Revision ID: <generate>
Revises: <head>
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    with op.batch_alter_table("template_exercises") as batch_op:
        batch_op.add_column(sa.Column("substitutes_json", sa.Text(), nullable=True))
    with op.batch_alter_table("session_exercises") as batch_op:
        batch_op.add_column(sa.Column("substituted_name", sa.String(255), nullable=True))

def downgrade():
    with op.batch_alter_table("session_exercises") as batch_op:
        batch_op.drop_column("substituted_name")
    with op.batch_alter_table("template_exercises") as batch_op:
        batch_op.drop_column("substitutes_json")
```

Run: `alembic upgrade head`

- [ ] **Step 4: Verify**

Run: `pytest tests/test_alembic_drift.py -v`
Expected: PASS (no drift).

- [ ] **Step 5: Commit**

```bash
git add app/models/catalog.py app/models/session.py migrations/versions/20260414_add_substitution.py
git commit -m "feat(sb03): migration — substitutes_json on TemplateExercise, substituted_name on SessionExercise"
```

---

### Task 2: Substitution Service + Seed Update

**Files:**
- Create: `app/services/substitution.py`
- Modify: `app/services/seed.py`
- Create: `tests/test_substitution.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_substitution.py`:

```python
"""Tests for exercise substitution service."""
from __future__ import annotations

from unittest.mock import MagicMock


def test_actual_exercise_name_no_substitution():
    from app.services.substitution import actual_exercise_name
    se = MagicMock()
    se.substituted_name = None
    se.exercise_name_snapshot = "Chest Press machine"
    assert actual_exercise_name(se) == "Chest Press machine"


def test_actual_exercise_name_with_substitution():
    from app.services.substitution import actual_exercise_name
    se = MagicMock()
    se.substituted_name = "Développé couché haltères"
    se.exercise_name_snapshot = "Chest Press machine"
    assert actual_exercise_name(se) == "Développé couché haltères"


def test_get_substitutes_from_json():
    from app.services.substitution import get_substitutes
    te = MagicMock()
    te.substitutes_json = '["Développé couché haltères", "Dips pectoraux"]'
    assert get_substitutes(te) == ["Développé couché haltères", "Dips pectoraux"]


def test_get_substitutes_none():
    from app.services.substitution import get_substitutes
    te = MagicMock()
    te.substitutes_json = None
    assert get_substitutes(te) == []


def test_get_substitutes_empty_json():
    from app.services.substitution import get_substitutes
    te = MagicMock()
    te.substitutes_json = "[]"
    assert get_substitutes(te) == []


def test_get_substitutes_no_template_exercise():
    from app.services.substitution import get_substitutes
    assert get_substitutes(None) == []


def test_can_substitute_no_completed_sets():
    from app.services.substitution import can_substitute
    se = MagicMock()
    sl1 = MagicMock(); sl1.kind = "work"; sl1.completed = False
    sl2 = MagicMock(); sl2.kind = "work"; sl2.completed = False
    se.set_logs = [sl1, sl2]
    assert can_substitute(se) is True


def test_can_substitute_has_completed_set():
    from app.services.substitution import can_substitute
    se = MagicMock()
    sl1 = MagicMock(); sl1.kind = "work"; sl1.completed = True
    sl2 = MagicMock(); sl2.kind = "work"; sl2.completed = False
    se.set_logs = [sl1, sl2]
    assert can_substitute(se) is False


def test_can_substitute_warmup_only_does_not_lock():
    from app.services.substitution import can_substitute
    se = MagicMock()
    sl1 = MagicMock(); sl1.kind = "warmup"; sl1.completed = True
    sl2 = MagicMock(); sl2.kind = "work"; sl2.completed = False
    se.set_logs = [sl1, sl2]
    assert can_substitute(se) is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_substitution.py -v`
Expected: FAIL (ImportError)

- [ ] **Step 3: Create substitution service**

Create `app/services/substitution.py`:

```python
"""Exercise substitution helpers.

Substitution is catalogue-driven: each TemplateExercise can carry
a JSON list of substitute exercise names. The user picks one before
their first completed set. After that, the choice is locked.

The `actual_exercise_name()` helper is the single point of truth
for "what exercise was actually performed" — used by muscle_scoring
and exercise_history for correct zone classification.
"""
from __future__ import annotations

import json


def actual_exercise_name(session_exercise) -> str:
    """Return the exercise name that was actually performed."""
    return session_exercise.substituted_name or session_exercise.exercise_name_snapshot


def get_substitutes(template_exercise) -> list[str]:
    """Return the list of substitute names, or empty list."""
    if template_exercise is None:
        return []
    raw = getattr(template_exercise, "substitutes_json", None)
    if not raw:
        return []
    try:
        result = json.loads(raw)
        return result if isinstance(result, list) else []
    except (json.JSONDecodeError, TypeError):
        return []


def can_substitute(session_exercise) -> bool:
    """True if no work set has been completed yet (substitution still allowed)."""
    for sl in session_exercise.set_logs:
        if sl.kind == "work" and sl.completed:
            return False
    return True
```

- [ ] **Step 4: Update seed to read substitutes**

In `app/services/seed.py`, in the exercise loop (around line 74), add after `notes=ex.get("notes")`:

```python
                substitutes_json=json.dumps(ex["substitutes"]) if ex.get("substitutes") else None,
```

The `json` import is already at the top of the file.

- [ ] **Step 5: Run tests**

Run: `pytest tests/test_substitution.py -v`
Expected: All PASS (9 tests).

- [ ] **Step 6: Commit**

```bash
git add app/services/substitution.py app/services/seed.py tests/test_substitution.py
git commit -m "feat(sb03): substitution service — actual_exercise_name, get_substitutes, can_substitute + seed"
```

---

### Task 3: Catalogue Update — Add Substitutes

**Files:**
- Modify: `data/reference_split.json`

- [ ] **Step 1: Add substitutes to ~10 exercises and bump version**

In `data/reference_split.json`:

1. Bump version from current to next (e.g., `2026-04-14.v7`)

2. Add `"substitutes"` field to these exercises:

**push-a:**
- E1 Incline Smith Press: `"substitutes": ["Développé incliné haltères 30°"]`
- E2 Chest Press machine: `"substitutes": ["Développé couché haltères", "Dips pectoraux (buste penché)"]`
- E4 Neutral Grip Shoulder Press machine: `"substitutes": ["Machine shoulder press"]`

**push-b:**
- E2 Développé couché haltères: `"substitutes": ["Chest Press machine", "Incline Smith Press"]`

**pull-a:**
- E4 Rear delt fly machine (pec deck inversé): `"substitutes": ["Écarté arrière d'épaule câble", "Face pull câble"]`

**pull-b:**
- E1 Rowing machine chest-supported: `"substitutes": ["Rowing haltère un bras (banc)", "Rowing câble assis prise neutre"]`

**legs-a:**
- E1 Hack Squat machine: `"substitutes": ["Squat Smith machine (pieds avancés)", "Leg Press (pieds bas, serrés)"]`
- E2 Leg Press (pieds bas, serrés): `"substitutes": ["Hack Squat machine"]`

**legs-b:**
- E4 Hip thrust Smith machine: `"substitutes": ["Hip thrust haltères"]`

Add `"substitutes"` right after `"notes"` (or after `"set_scheme"` if no notes) in the JSON structure for each exercise. The field is a simple JSON array of strings.

- [ ] **Step 2: Run QA script**

Run: `python scripts/catalog_qa.py`
Expected: PASS (substitutes don't affect existing checks).

- [ ] **Step 3: Run seed to verify**

Run: `pytest tests/test_catalog_integrity.py -v`
Expected: All pass.

- [ ] **Step 4: Commit**

```bash
git add data/reference_split.json
git commit -m "feat(sb03): add substitution lists to ~10 catalogue exercises, bump v7"
```

---

### Task 4: Router + Template — Substitution UI

**Files:**
- Modify: `app/routers/sessions.py`
- Modify: `app/templates/session_detail.html`

- [ ] **Step 1: Update router — pass substitution data + parse form**

In `app/routers/sessions.py`:

**In `session_detail` (GET):** After computing hints, add substitution data per exercise:

```python
    from app.services.substitution import get_substitutes, can_substitute
    substitution_data: dict[int, dict] = {}
    for se in session.session_exercises:
        subs = get_substitutes(se.template_exercise)
        substitution_data[se.id] = {
            "substitutes": subs,
            "can_substitute": can_substitute(se),
        }
```

Add `"substitution_data": substitution_data` to the template context.

**In `update_exercise_card` (POST):** After the exercise-level feedback parsing (muscle_sensation, free_note) and BEFORE the set loop, add:

```python
    # Substitution (Sb_03) — only if no work set is completed yet
    from app.services.substitution import can_substitute
    sub_name = clean_str(form.get("substituted_name"), max_length=255)
    if sub_name and can_substitute(se):
        se.substituted_name = sub_name
    elif not sub_name:
        # Empty string = revert to prescribed (if still allowed)
        if can_substitute(se):
            se.substituted_name = None
```

- [ ] **Step 2: Update template — add select / badge**

In `app/templates/session_detail.html`, inside the exercise card `<form>`, after the `exercise-card__head-expanded` div (history link) and before `last-time`, add:

```html
      {# Substitution (Sb_03) #}
      {% set sub_data = substitution_data.get(se.id, {}) %}
      {% set subs = sub_data.get('substitutes', []) %}
      {% set can_sub = sub_data.get('can_substitute', False) %}

      {% if can_sub and subs %}
        <div class="substitute-picker">
          <label style="font-size:12px;color:var(--fg-dim);display:block;margin-bottom:2px;">Substituer</label>
          <select name="substituted_name" style="width:100%;padding:var(--space-xs);background:var(--surface-2);color:var(--fg);border:1px solid var(--border);border-radius:var(--radius-sm);font-size:13px;">
            <option value="">{{ se.exercise_name_snapshot }} (prescrit)</option>
            {% for sub in subs %}
              <option value="{{ sub }}" {% if se.substituted_name == sub %}selected{% endif %}>{{ sub }}</option>
            {% endfor %}
          </select>
        </div>
      {% elif se.substituted_name %}
        <div class="substitute-badge" style="font-size:12px;margin-bottom:var(--space-sm);padding:var(--space-xs) var(--space-sm);background:var(--accent-soft);border-radius:var(--radius-sm);">
          Substitué : <b>{{ se.substituted_name }}</b>
          <span style="color:var(--fg-dim);">(prescrit : {{ se.exercise_name_snapshot }})</span>
        </div>
      {% endif %}
```

Also update the compact `<summary>` to show the actual name when substituted:

In the summary, replace:
```html
      <span class="exercise-card__name">{{ se.exercise_name_snapshot }}</span>
```

With:
```html
      <span class="exercise-card__name">{{ se.substituted_name or se.exercise_name_snapshot }}</span>
```

- [ ] **Step 3: Run session flow tests**

Run: `pytest tests/test_session_flow.py -v --tb=short`
Expected: All pass (substitution is additive — no existing behavior changes).

- [ ] **Step 4: Commit**

```bash
git add app/routers/sessions.py app/templates/session_detail.html
git commit -m "feat(sb03): substitution UI — select dropdown + badge + router parsing + lock enforcement"
```

---

### Task 5: Muscle Scoring — Use Actual Exercise Name

**Files:**
- Modify: `app/services/muscle_scoring.py`

- [ ] **Step 1: Update classify_exercise call**

In `app/services/muscle_scoring.py`, in the `_compute_tonnage_by_zone` function (around line 88), change:

```python
            primary, secondary = classify_exercise(se.exercise_name_snapshot)
```

To:

```python
            from app.services.substitution import actual_exercise_name
            primary, secondary = classify_exercise(actual_exercise_name(se))
```

- [ ] **Step 2: Run scoring tests**

Run: `pytest tests/test_muscle_scoring.py -v`
Expected: All pass.

- [ ] **Step 3: Commit**

```bash
git add app/services/muscle_scoring.py
git commit -m "feat(sb03): muscle_scoring uses actual_exercise_name for zone classification"
```

---

### Task 6: Export + QA + Route Tests + Report

**Files:**
- Modify: `app/services/export_builder.py`
- Modify: `scripts/catalog_qa.py`
- Modify: `tests/test_substitution.py`
- Create: `docs/SPRINT_Sb03_REPORT.md`

- [ ] **Step 1: Add substituted_name to export**

In `app/services/export_builder.py`, in the `serialise_session` function, add `"substituted_name": se.substituted_name` to the exercise dict (after `"free_note"`).

In the CSV builder, add `"substituted_name"` to the CSV header row and the corresponding value in the data row.

- [ ] **Step 2: Add substitute classifiability check to QA script**

In `scripts/catalog_qa.py`, add a new check function:

```python
def check_substitute_classifiability(templates: list[dict]) -> list[str]:
    """Every substitute name must be classifiable."""
    from app.services.muscle_mapping import classify_exercise
    warnings = []
    for tpl in templates:
        for ex in tpl.get("exercises", []):
            for sub in ex.get("substitutes", []):
                primary, _ = classify_exercise(sub)
                if primary == "unknown":
                    warnings.append(
                        f"[{tpl['slug']}] {ex['code']}: substitute '{sub}' is unclassifiable"
                    )
    return warnings
```

Call it in `main()` and add results to `all_warnings`.

- [ ] **Step 3: Add route integration tests**

Add to `tests/test_substitution.py`:

```python
def test_substitution_select_appears_for_new_session(client):
    """Exercise with substitutes shows a select dropdown."""
    r = client.post("/sessions", data={"template_slug": "push-a"}, follow_redirects=False)
    sid = r.headers["location"].split("/")[-1]
    r2 = client.get(f"/sessions/{sid}")
    # push-a E2 (Chest Press machine) has substitutes
    assert "substituted_name" in r2.text or "Substituer" in r2.text or "prescrit" in r2.text


def test_substitution_persists_after_save(client):
    """Submitting a substituted_name stores it."""
    import re
    from app.database import SessionLocal
    from app.models.session import SessionExercise

    r = client.post("/sessions", data={"template_slug": "push-a"}, follow_redirects=False)
    sid = int(r.headers["location"].split("/")[-1])

    # Get E2's session_exercise_id
    with SessionLocal() as db:
        from sqlalchemy import select
        from app.models.session import WorkoutSession
        se = db.execute(
            select(SessionExercise)
            .where(SessionExercise.session_id == sid)
            .where(SessionExercise.exercise_code_snapshot == "E2")
        ).scalar_one()
        se_id = se.id

    # Submit with substitution (no completed sets yet)
    client.post(
        f"/sessions/{sid}/exercises/{se_id}",
        data={"substituted_name": "Développé couché haltères"},
        follow_redirects=False,
    )

    with SessionLocal() as db:
        se = db.get(SessionExercise, se_id)
        assert se.substituted_name == "Développé couché haltères"
```

- [ ] **Step 4: Run full test suite**

Run: `pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q`
Expected: All pass.

- [ ] **Step 5: Write sprint report**

Create `docs/SPRINT_Sb03_REPORT.md`:

```markdown
# Sprint Sb_03 Report — Minimal Substitution Graph Build

**Date:** 2026-04-14
**Status:** Complete
**Spec:** docs/strategy/SPIGNOS_EXERCISE_SUBSTITUTION_GRAPH_SPEC.md

## Objective

Add exercise substitution to the session flow — swap prescribed
exercises for catalogue-defined equivalents, tracked for analytics.

## Deliverables

| Artifact | Path | Status |
|----------|------|--------|
| Migration | `migrations/versions/20260414_add_substitution.py` | Applied |
| Substitution service | `app/services/substitution.py` | Done |
| Catalogue update | `data/reference_split.json` v7 | Done — ~10 exercises with substitutes |
| Template UI | `app/templates/session_detail.html` | Done — select + badge |
| Muscle scoring | `app/services/muscle_scoring.py` | Uses actual_exercise_name() |
| Export | `app/services/export_builder.py` | Includes substituted_name |
| QA script | `scripts/catalog_qa.py` | Validates substitute classifiability |

## Verification

```bash
pytest tests/test_substitution.py -v
pytest tests/test_muscle_scoring.py -v
python scripts/catalog_qa.py
pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q
```

## Unblocks

- Sb_04 (history + analytics alignment) — exercise_history shows actual name
```

- [ ] **Step 6: Commit**

```bash
git add app/services/export_builder.py scripts/catalog_qa.py tests/test_substitution.py docs/SPRINT_Sb03_REPORT.md
git commit -m "docs(sb03): substitution export + QA check + route tests + sprint report"
```
