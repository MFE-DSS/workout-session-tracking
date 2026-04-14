# Sb_launcher_v1 — Intelligent Session Launcher Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the flat `/library` entry point with a guided 2-step launcher (`/launcher`) that routes the user from "type of session" → "zone/variant" → 1-3 templates, with dynamic branch resolution (empty branches never shown) and preserving `/library` as a separate full-catalog access.

**Architecture:** Pure SSR addition — new route `/launcher`, new service `launcher.py` holding a static `BRANCH_TREE` that resolves to existing catalog slugs at request time. Branches returning zero existing templates are hidden from the menu. No migration, no model changes, no touch to `POST /sessions`.

**Tech Stack:** FastAPI route, Jinja2 template, SQLAlchemy query (read-only on WorkoutTemplate), pytest

---

## 6 arbitrages verrouilles respectes

- (1) Branches vides jamais affichees — resolution dynamique
- (2) Catalogue existant strict — pas de nouveaux templates
- (6) `data/reference_split.json` (via la DB seedee) est la source de verite

---

## File Structure

| File | Responsibility |
|------|---------------|
| `app/services/launcher.py` | **New** — `BRANCH_TREE` constant, `resolve_branch(db, type, variant) -> list[WorkoutTemplate]`, `get_available_branches(db, type) -> list[branch]` |
| `app/routers/pages.py` | Modify — add `GET /launcher` route |
| `app/templates/launcher.html` | **New** — 3-state template (no params → step 1; type → step 2; type+variant → templates) |
| `app/templates/index.html` | Modify — tile "Nouvelle séance" points to `/launcher` |
| `tests/test_launcher.py` | **New** — service unit tests (dynamic branch resolution) |
| `tests/test_launcher_routes.py` | **New** — route integration tests |

---

### Task 1: Launcher Service

**Files:**
- Create: `app/services/launcher.py`
- Create: `tests/test_launcher.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_launcher.py`:

```python
"""Tests for launcher service — dynamic branch resolution."""
from __future__ import annotations


def test_branch_tree_structure():
    """BRANCH_TREE must define type → variant → slugs mapping."""
    from app.services.launcher import BRANCH_TREE
    assert "standard" in BRANCH_TREE
    assert "short" in BRANCH_TREE
    assert "cardio" in BRANCH_TREE
    # Each type has variants or direct slugs
    assert isinstance(BRANCH_TREE["standard"], dict)
    assert isinstance(BRANCH_TREE["cardio"], dict)


def test_resolve_branch_standard_upper_push(client):
    """Standard / upper-push returns push-a and push-b."""
    from app.database import SessionLocal
    from app.services.launcher import resolve_branch
    with SessionLocal() as db:
        templates = resolve_branch(db, "standard", "upper-push")
    slugs = [t.slug for t in templates]
    assert "push-a" in slugs
    assert "push-b" in slugs


def test_resolve_branch_cardio(client):
    """Cardio branch returns liss-abs (catalog v7 state)."""
    from app.database import SessionLocal
    from app.services.launcher import resolve_branch
    with SessionLocal() as db:
        templates = resolve_branch(db, "cardio", None)
    slugs = [t.slug for t in templates]
    assert "liss-abs" in slugs


def test_resolve_branch_empty_for_unknown_variant(client):
    """Unknown variant returns empty list."""
    from app.database import SessionLocal
    from app.services.launcher import resolve_branch
    with SessionLocal() as db:
        templates = resolve_branch(db, "standard", "does-not-exist")
    assert templates == []


def test_get_available_variants_standard(client):
    """get_available_variants returns only variants with >= 1 existing template."""
    from app.database import SessionLocal
    from app.services.launcher import get_available_variants
    with SessionLocal() as db:
        variants = get_available_variants(db, "standard")
    keys = [v["key"] for v in variants]
    assert "upper-push" in keys
    assert "upper-pull" in keys
    assert "lower-quads" in keys


def test_get_available_variants_short_filters_empty_branches(client):
    """short/full-lower and short/full-body don't exist → not shown."""
    from app.database import SessionLocal
    from app.services.launcher import get_available_variants
    with SessionLocal() as db:
        variants = get_available_variants(db, "short")
    keys = [v["key"] for v in variants]
    # short-upper exists → visible
    assert "upper" in keys
    # full-lower and full-body have no templates → must NOT appear
    assert "full-lower" not in keys
    assert "full-body" not in keys


def test_get_available_types_only_shows_types_with_content(client):
    """get_available_types returns types that have at least one available variant."""
    from app.database import SessionLocal
    from app.services.launcher import get_available_types
    with SessionLocal() as db:
        types = get_available_types(db)
    keys = [t["key"] for t in types]
    assert "standard" in keys
    assert "short" in keys  # upper variant exists
    assert "cardio" in keys  # liss-abs exists
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_launcher.py -v`
Expected: FAIL (ImportError — module does not exist)

- [ ] **Step 3: Implement the launcher service**

Create `app/services/launcher.py`:

```python
"""Intelligent session launcher — branch tree + dynamic resolution.

The launcher is a pure routing layer over the existing catalog.
BRANCH_TREE is a static decision tree; resolve_branch reads the
catalog at request time and returns only existing templates.
Branches with zero existing templates are hidden from the UI.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.catalog import WorkoutTemplate


# Static branch tree — maps (type, variant) -> list of candidate slugs.
# The service filters this at request time against existing templates.
#
# Structure:
#   BRANCH_TREE[type]: either dict {variant_key: {"label": str, "slugs": [str]}}
#   for multi-variant types, or dict {"_direct": {"label": str, "slugs": [str]}}
#   for types that skip step 2 (cardio).

BRANCH_TREE: dict[str, dict[str, dict]] = {
    "standard": {
        "upper-push": {
            "label": "Haut / Push (pecs, épaules, triceps)",
            "slugs": ["push-a", "push-b"],
        },
        "upper-pull": {
            "label": "Haut / Pull (dos, biceps)",
            "slugs": ["pull-a", "pull-b"],
        },
        "lower-quads": {
            "label": "Bas / Quads dominant",
            "slugs": ["legs-a"],
        },
        "lower-post": {
            "label": "Bas / Postérieur dominant",
            "slugs": ["legs-b"],
        },
        "catch-shoulders": {
            "label": "Rattrapage épaules",
            "slugs": ["catch-up-shoulders"],
        },
        "catch-arms": {
            "label": "Rattrapage bras",
            "slugs": ["catch-up-arms"],
        },
        "catch-back": {
            "label": "Rattrapage dos largeur",
            "slugs": ["catch-up-back-width"],
        },
    },
    "short": {
        "upper": {
            "label": "Full upper court",
            "slugs": ["short-upper"],
        },
        "full-lower": {
            "label": "Full lower court",
            "slugs": ["short-lower"],  # not in v7 — filtered out dynamically
        },
        "full-body": {
            "label": "Full body court",
            "slugs": ["short-full-body"],  # not in v7 — filtered out
        },
        "spec": {
            "label": "Spécialisation courte",
            "slugs": ["catch-up-shoulders", "catch-up-arms", "catch-up-back-width"],
        },
    },
    "cardio": {
        "_direct": {
            "label": "LISS + abdos",
            "slugs": ["liss-abs"],
        },
    },
}


TYPE_LABELS = {
    "standard": "Séance standard",
    "short": "Séance courte",
    "cardio": "Cardio",
}


def _existing_slugs(db: Session) -> set[str]:
    """Return the set of slugs currently in the catalog."""
    rows = db.execute(select(WorkoutTemplate.slug)).scalars().all()
    return set(rows)


def resolve_branch(
    db: Session, type_: str, variant: str | None,
) -> list[WorkoutTemplate]:
    """Return templates for a given (type, variant), filtered to
    those that exist in the catalog."""
    if type_ not in BRANCH_TREE:
        return []

    type_branches = BRANCH_TREE[type_]

    # Direct resolution (cardio)
    if variant is None and "_direct" in type_branches:
        slugs = type_branches["_direct"]["slugs"]
    elif variant is None:
        return []
    else:
        if variant not in type_branches:
            return []
        slugs = type_branches[variant]["slugs"]

    existing = _existing_slugs(db)
    final_slugs = [s for s in slugs if s in existing]
    if not final_slugs:
        return []

    templates = list(db.execute(
        select(WorkoutTemplate).where(WorkoutTemplate.slug.in_(final_slugs))
    ).scalars().all())
    # Preserve order defined in BRANCH_TREE
    order = {s: i for i, s in enumerate(slugs)}
    templates.sort(key=lambda t: order.get(t.slug, 999))
    return templates


def get_available_variants(db: Session, type_: str) -> list[dict]:
    """Return variants for a type, filtered to those with >= 1 existing template.
    Each entry: {"key": str, "label": str}."""
    if type_ not in BRANCH_TREE:
        return []
    existing = _existing_slugs(db)
    out: list[dict] = []
    for key, branch in BRANCH_TREE[type_].items():
        if key == "_direct":
            continue
        if any(s in existing for s in branch["slugs"]):
            out.append({"key": key, "label": branch["label"]})
    return out


def get_available_types(db: Session) -> list[dict]:
    """Return types that have at least one resolvable branch.
    Each entry: {"key": str, "label": str}."""
    existing = _existing_slugs(db)
    out: list[dict] = []
    for type_key, branches in BRANCH_TREE.items():
        has_any = False
        for branch in branches.values():
            if any(s in existing for s in branch["slugs"]):
                has_any = True
                break
        if has_any:
            out.append({"key": type_key, "label": TYPE_LABELS[type_key]})
    return out
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_launcher.py -v`
Expected: All 7 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add app/services/launcher.py tests/test_launcher.py
git commit -m "feat(sb-launcher): launcher service — static BRANCH_TREE + dynamic resolution"
```

---

### Task 2: Launcher Route + Template

**Files:**
- Modify: `app/routers/pages.py`
- Create: `app/templates/launcher.html`
- Create: `tests/test_launcher_routes.py`

- [ ] **Step 1: Write failing route tests**

Create `tests/test_launcher_routes.py`:

```python
"""Integration tests for /launcher route."""
from __future__ import annotations


def test_launcher_step1_renders(client):
    """GET /launcher (no params) shows step 1 — types."""
    r = client.get("/launcher")
    assert r.status_code == 200
    assert "Séance standard" in r.text
    assert "Séance courte" in r.text
    assert "Cardio" in r.text


def test_launcher_step2_standard(client):
    """GET /launcher?type=standard shows variants."""
    r = client.get("/launcher?type=standard")
    assert r.status_code == 200
    assert "Haut / Push" in r.text
    assert "Haut / Pull" in r.text
    assert "Bas / Quads dominant" in r.text


def test_launcher_step2_hides_empty_branches(client):
    """short type does NOT show full-lower or full-body in v7."""
    r = client.get("/launcher?type=short")
    assert r.status_code == 200
    assert "Full upper court" in r.text
    # Empty branches must NOT appear
    assert "Full lower court" not in r.text
    assert "Full body court" not in r.text


def test_launcher_final_standard_upper_push(client):
    """GET /launcher?type=standard&variant=upper-push shows push-a and push-b."""
    r = client.get("/launcher?type=standard&variant=upper-push")
    assert r.status_code == 200
    assert "Push A" in r.text
    assert "Push B" in r.text


def test_launcher_cardio_direct(client):
    """GET /launcher?type=cardio shows liss-abs directly (no variant step)."""
    r = client.get("/launcher?type=cardio")
    assert r.status_code == 200
    assert "LISS cardio + abdos" in r.text or "liss-abs" in r.text


def test_launcher_unknown_type_falls_back_to_step1(client):
    """Unknown type param falls back to step 1."""
    r = client.get("/launcher?type=bogus")
    assert r.status_code == 200
    assert "Séance standard" in r.text


def test_launcher_library_link_present(client):
    """Every launcher page shows a 'Voir tous les programmes →' link."""
    r = client.get("/launcher")
    assert r.status_code == 200
    assert "/library" in r.text


def test_launcher_requires_auth(client):
    """/launcher requires authentication."""
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    r = client.get("/launcher", follow_redirects=False)
    assert r.status_code == 303


def test_home_tile_points_to_launcher(client):
    """The home tile 'Nouvelle séance' points to /launcher, not /library."""
    r = client.get("/")
    assert "/launcher" in r.text
    # Verify the tile block contains /launcher, not just any mention
    assert 'href="/launcher"' in r.text or "'/launcher'" in r.text
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_launcher_routes.py::test_launcher_step1_renders -v`
Expected: FAIL (404 — route does not exist)

- [ ] **Step 3: Add the launcher route**

In `app/routers/pages.py`, add after the `library` route (after the `/library/{slug}` handler):

```python
@router.get("/launcher", response_class=HTMLResponse, name="launcher")
def launcher(
    request: Request,
    db: DbSession,
    user: CurrentUser,
    type: str | None = Query(None),
    variant: str | None = Query(None),
) -> HTMLResponse:
    from app.services.launcher import (
        get_available_types,
        get_available_variants,
        resolve_branch,
        TYPE_LABELS,
        BRANCH_TREE,
    )

    # Validate type param; fall back to step 1 if unknown
    if type is not None and type not in BRANCH_TREE:
        type = None

    if type is None:
        # Step 1 — list types
        return templates.TemplateResponse(
            request,
            "launcher.html",
            {
                "page_title": "Nouvelle séance",
                "step": 1,
                "types": get_available_types(db),
                "active_session": latest_open_session(db, user.id),
            },
        )

    # Cardio has no step 2 — resolve directly
    if "_direct" in BRANCH_TREE[type]:
        final_templates = resolve_branch(db, type, None)
        return templates.TemplateResponse(
            request,
            "launcher.html",
            {
                "page_title": TYPE_LABELS[type],
                "step": 3,
                "type_key": type,
                "type_label": TYPE_LABELS[type],
                "templates_list": final_templates,
                "active_session": latest_open_session(db, user.id),
            },
        )

    if variant is None:
        # Step 2 — list variants
        return templates.TemplateResponse(
            request,
            "launcher.html",
            {
                "page_title": TYPE_LABELS[type],
                "step": 2,
                "type_key": type,
                "type_label": TYPE_LABELS[type],
                "variants": get_available_variants(db, type),
                "active_session": latest_open_session(db, user.id),
            },
        )

    # Step 3 — final templates list
    final_templates = resolve_branch(db, type, variant)
    # If variant unknown or empty, fall back to step 2
    if not final_templates:
        return templates.TemplateResponse(
            request,
            "launcher.html",
            {
                "page_title": TYPE_LABELS[type],
                "step": 2,
                "type_key": type,
                "type_label": TYPE_LABELS[type],
                "variants": get_available_variants(db, type),
                "active_session": latest_open_session(db, user.id),
            },
        )

    return templates.TemplateResponse(
        request,
        "launcher.html",
        {
            "page_title": TYPE_LABELS[type],
            "step": 3,
            "type_key": type,
            "type_label": TYPE_LABELS[type],
            "variant_key": variant,
            "templates_list": final_templates,
            "active_session": latest_open_session(db, user.id),
        },
    )
```

- [ ] **Step 4: Create the launcher template**

Create `app/templates/launcher.html`:

```html
{% extends "base.html" %}
{% block content %}
<h1 class="page-title">Nouvelle séance</h1>

{% if step == 1 %}
  <p class="lede">Quel type de séance veux-tu faire ?</p>
  <div class="tile-grid">
    {% for t in types %}
      <a class="tile {% if t.key == 'standard' %}tile--primary{% endif %}" href="/launcher?type={{ t.key }}">
        <div class="tile__label">{{ t.label }}</div>
      </a>
    {% endfor %}
  </div>

{% elif step == 2 %}
  <p class="lede">{{ type_label }} — quelle zone ?</p>
  <div class="tile-grid">
    {% for v in variants %}
      <a class="tile" href="/launcher?type={{ type_key }}&variant={{ v.key }}">
        <div class="tile__label">{{ v.label }}</div>
      </a>
    {% endfor %}
  </div>
  <p class="mt-md"><a class="text-muted" href="/launcher">← Retour</a></p>

{% elif step == 3 %}
  <p class="lede">{{ type_label }}</p>
  <ul class="template-list">
    {% for tpl in templates_list %}
      <li class="template-card template-card--{{ tpl.kind }}">
        <a class="template-card__link" href="{{ url_for('template_detail', slug=tpl.slug) }}">
          <div class="template-card__row">
            <span class="template-card__name">{{ tpl.name }}</span>
            <span class="template-card__kind">{{ tpl.kind|upper }}</span>
          </div>
          <div class="template-card__focus">{{ tpl.focus }}</div>
          {% if tpl.kind == 'cardio' and tpl.cardio_note %}
            <div class="template-card__cardio">{{ tpl.cardio_note }}</div>
          {% endif %}
          <form method="post" action="{{ url_for('create_session') }}" class="template-card__start" onclick="event.stopPropagation();">
            <input type="hidden" name="template_slug" value="{{ tpl.slug }}" />
            <button type="submit" class="btn btn--primary btn--sm">Démarrer</button>
          </form>
        </a>
      </li>
    {% endfor %}
  </ul>
  <p class="mt-md">
    <a class="text-muted" href="/launcher?type={{ type_key }}">← Autre zone</a>
    &nbsp;·&nbsp;
    <a class="text-muted" href="/launcher">← Autre type</a>
  </p>
{% endif %}

<p class="mt-lg text-dim" style="font-size:13px;">
  <a href="/library">Voir tous les programmes →</a>
</p>
{% endblock %}
```

- [ ] **Step 5: Update home tile**

In `app/templates/index.html`, find the tile:

```html
<a class="tile tile--primary" href="{{ url_for('library') }}">
  <div class="tile__label">Nouvelle séance</div>
  <div class="tile__hint">Choisir un programme</div>
</a>
```

Replace `href="{{ url_for('library') }}"` with `href="{{ url_for('launcher') }}"`.

- [ ] **Step 6: Run tests**

Run: `pytest tests/test_launcher_routes.py -v`
Expected: All 9 tests PASS.

- [ ] **Step 7: Run full suite**

Run: `pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q`
Expected: All pass.

- [ ] **Step 8: Commit**

```bash
git add app/routers/pages.py app/templates/launcher.html app/templates/index.html tests/test_launcher_routes.py
git commit -m "feat(sb-launcher): /launcher route + template + home tile"
```

---

### Task 3: Sprint Report

**Files:**
- Create: `docs/SPRINT_Sb_launcher_v1_REPORT.md`

- [ ] **Step 1: Run full test suite**

Run: `pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q`
Expected: All pass.

- [ ] **Step 2: Write sprint report**

Create `docs/SPRINT_Sb_launcher_v1_REPORT.md`:

```markdown
# Sprint Sb_launcher_v1 Report — Intelligent Session Launcher

**Date:** 2026-04-14
**Status:** Complete
**Spec:** docs/strategy/SPIGNOS_INTELLIGENT_SESSION_LAUNCHER_SPEC.md

## Objective

Replace flat /library entry with guided /launcher — 2 steps max,
dynamic branch resolution (empty branches never shown).

## Deliverables

| Artifact | Path |
|----------|------|
| Service | `app/services/launcher.py` |
| Route | `GET /launcher?type&variant` in `pages.py` |
| Template | `app/templates/launcher.html` |
| Home tile | `app/templates/index.html` (updated href) |
| Tests | `tests/test_launcher.py` + `tests/test_launcher_routes.py` |

## 6 arbitrages respectes

- (1) Branches vides jamais affichees → `get_available_variants` filtre
- (2) Catalogue existant strict → slugs hardcodes mais filtres dynamiquement
- (6) reference_split.json via DB → `_existing_slugs(db)` lit WorkoutTemplate

## Verification

```
pytest tests/test_launcher.py tests/test_launcher_routes.py -v
pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q
```

## Coexistence /library

/library reste accessible via nav topbar et via "Voir tous les programmes →" sur toutes les etapes du launcher.
```

- [ ] **Step 3: Commit**

```bash
git add docs/SPRINT_Sb_launcher_v1_REPORT.md
git commit -m "docs(sb-launcher): sprint report — intelligent session launcher V1 complete"
```
