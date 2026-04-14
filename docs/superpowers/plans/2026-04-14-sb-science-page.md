# Sb_science_page — Science Page + SVG Architecture Diagram

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform `/rules` into `/science` — a structured usage manual (not a marketing manifesto) with 5 sections: (1) why journaling changes progression, (2) training principles (existing method_rules preserved), (3) role of cardio, (4) how SPIGNOS materializes these concepts, (5) SVG SSR static architecture diagram. Keep `/rules` as a 301 redirect. Update home tile.

**Architecture:** Pure SSR — new template `science.html` replaces `rules.html` rendering. Route `rules_page` renamed to `science_page`, URL `/science`. `/rules` becomes a 301 redirect. Method rules data unchanged. SVG diagram is a static Jinja block referencing CSS tokens.

**Tech Stack:** Jinja2 template, FastAPI route, SVG markup, CSS tokens V2.1

---

## 6 arbitrages verrouilles respectes

- (4) Manuel structure, pas manifeste de marque
- (5) Diagramme SVG SSR statique (pas Mermaid, pas hover)
- Ordre editorial : pratique → principes → materialisation → architecture

---

## File Structure

| File | Responsibility |
|------|---------------|
| `app/templates/science.html` | **New** — 5 sections + SVG diagram |
| `app/templates/rules.html` | **Delete** (replaced by redirect) |
| `app/routers/sessions.py` | Modify — rename `rules_page` → `science_page`, URL `/science`, add `/rules` → 301 redirect |
| `app/templates/index.html` | Modify — tile "Règles" → "Science", href → `/science` |
| `app/static/css/app.css` | Modify — add `.science-section`, `.science-diagram` styles |
| `tests/test_science_page.py` | **New** |

---

### Task 1: Route Rename + Redirect

**Files:**
- Modify: `app/routers/sessions.py`

- [ ] **Step 1: Rename route and add redirect**

In `app/routers/sessions.py`, find the `rules_page` route (around line 341):

```python
@router.get("/rules", response_class=HTMLResponse)
def rules_page(request: Request, db: DbSession, user: CurrentUser) -> HTMLResponse:
    rules = db.execute(
        select(MethodRule).order_by(MethodRule.position)
    ).scalars().all()
    return templates.TemplateResponse(
        request,
        "rules.html",
        {
            "page_title": "Règles",
            "rules": rules,
            "active_session": latest_open_session(db, user.id),
        },
    )
```

Replace with:

```python
@router.get("/science", response_class=HTMLResponse, name="science_page")
def science_page(request: Request, db: DbSession, user: CurrentUser) -> HTMLResponse:
    rules = db.execute(
        select(MethodRule).order_by(MethodRule.position)
    ).scalars().all()
    return templates.TemplateResponse(
        request,
        "science.html",
        {
            "page_title": "Science",
            "rules": rules,
            "active_session": latest_open_session(db, user.id),
        },
    )


@router.get("/rules", name="rules_page")
def rules_redirect() -> RedirectResponse:
    """Legacy URL — /rules now redirects to /science (301)."""
    return RedirectResponse(url="/science", status_code=301)
```

Make sure `RedirectResponse` is imported at the top of the file (it should already be).

- [ ] **Step 2: Quick smoke test**

Run: `python -c "from app.main import app; print('OK')"`
Expected: "OK" (no import errors).

- [ ] **Step 3: Commit**

```bash
git add app/routers/sessions.py
git commit -m "feat(sb-science): rename route rules→science, /rules redirects 301"
```

Note: this commit will temporarily break the page render because `science.html` doesn't exist yet. The next task creates it.

---

### Task 2: Science Template — 5 Sections (editorial)

**Files:**
- Create: `app/templates/science.html`

- [ ] **Step 1: Create the template**

Create `app/templates/science.html`:

```html
{% extends "base.html" %}
{% block content %}
<h1 class="page-title">Science</h1>
<p class="lede">Comprendre pourquoi noter change la progression, et comment SPIGNOS materialise cette discipline.</p>

<!-- ================================================================ -->
<!-- SECTION 1 — PRATIQUE : Pourquoi noter change la progression      -->
<!-- ================================================================ -->
<section class="science-section" id="section-journal">
  <h2 class="section-header">Pourquoi noter change la progression</h2>
  <div class="card">
    <p>La memoire subjective est un mauvais outil de progression. Elle surestime les bonnes seances, oublie les stagnations, et fabrique des souvenirs qui arrangent le moment.</p>
    <p>Un carnet la remplace. La surcharge progressive suppose que tu saches ce que tu as fait la derniere fois. C'est tout. Sans trace, tu ne peux pas comparer. Sans comparaison, tu ne peux pas ajuster la charge, les reps, la frequence.</p>
    <p>L'auto-illusion — croire qu'on progresse quand on stagne — est la premiere cause de stagnation reelle. Noter l'elimine. Pas par discipline morale, par lucidite.</p>
    <p>Quand tu notes, ta seance devient une donnee. Quand ta seance devient une donnee, tu peux l'ameliorer.</p>
  </div>
</section>

<!-- ================================================================ -->
<!-- SECTION 2 — PRINCIPES : Methode d'entrainement                   -->
<!-- ================================================================ -->
<section class="science-section" id="section-method">
  <h2 class="section-header">Methode d'entrainement</h2>
  {% for rule in rules %}
  <article class="card rule-card" id="rule-{{ rule.slug }}">
    <h3 class="card__title">{{ rule.title }}</h3>
    <p class="rule__body">{{ rule.body }}</p>
  </article>
  {% endfor %}
</section>

<!-- ================================================================ -->
<!-- SECTION 3 — PRINCIPES : Place du cardio (LISS)                   -->
<!-- ================================================================ -->
<section class="science-section" id="section-cardio">
  <h2 class="section-header">Place du cardio</h2>
  <div class="card">
    <p>Le LISS (Low Intensity Steady State) n'est pas un outil de perte de gras magique. C'est un outil de discipline cardio-vasculaire et de recuperation active.</p>
    <p>Dans un programme muscu, il a trois fonctions :</p>
    <ul>
      <li>Maintenir une base cardio sans tirer sur la recuperation musculaire.</li>
      <li>Servir de seance "entre deux" qui preserve la regularite les jours ou tu n'as pas le temps pour du lourd.</li>
      <li>Ameliorer la tolerance au volume — la capacite a enchainer les seances sans craquer.</li>
    </ul>
    <p>SPIGNOS capture le cardio avec : duree, BPM moyen (si tu le mesures), machine utilisee. Les calories affichees par la machine peuvent etre notees, mais elles sont une donnee machine indicative, pas une verite metabolique.</p>
    <p class="text-dim" style="font-size:12px;">SPIGNOS stocke des donnees cardio operatoires, pas des verites physiologiques absolues.</p>
  </div>
</section>

<!-- ================================================================ -->
<!-- SECTION 4 — MATERIALISATION : Comment SPIGNOS materialise        -->
<!-- ================================================================ -->
<section class="science-section" id="section-manual">
  <h2 class="section-header">Comment SPIGNOS materialise ces concepts</h2>

  <div class="card">
    <h3 class="card__title">Programmes et seances</h3>
    <p>Les programmes (Push A, Pull B, Legs A...) sont des modeles figes. Chaque version du catalogue a un numero. Quand tu demarres une seance, SPIGNOS en fait une copie vivante que tu remplis. Meme si le programme change plus tard, ta seance reste telle qu'elle a ete logguee.</p>
  </div>

  <div class="card">
    <h3 class="card__title">Exercices et series</h3>
    <p>Chaque exercice a des series d'echauffement (1 ou 2) et des series de travail. Tu entres pour chaque serie : poids, reps, coche "fait". Pas de case obligatoire en plus. <a href="#rule-plages-repetitions">Voir plages de reps</a>.</p>
  </div>

  <div class="card">
    <h3 class="card__title">Score derive</h3>
    <p>Le score d'un exercice est calcule automatiquement a partir des reps vs la plage prescrite, et du nombre de series completees. Tu n'as pas a poser un ressenti arbitraire — le chiffre vient de ce que tu as fait. La sensation musculaire, optionnelle, reste une note subjective.</p>
  </div>

  <div class="card">
    <h3 class="card__title">Historique</h3>
    <p>Chaque seance est conservee telle qu'elle a ete logguee. Tu peux la revoir, comparer a la meme seance passee, voir les deltas (charge, reps) pour un meme exercice.</p>
  </div>

  <div class="card">
    <h3 class="card__title">Synthese et physique</h3>
    <p>La page <b>Synthese</b> calcule 5 axes (regularite, progression, evolution corporelle, recuperation, equilibre musculaire) avec un niveau de confiance par axe. Si les donnees sont insuffisantes, l'axe est grise. Tu ne vois jamais un score qu'on ne peut pas calculer honnetement.</p>
    <p>La page <b>Physique</b> montre l'equilibre de developpement par zone musculaire, base sur le volume d'entrainement et les mesures corporelles si saisies.</p>
  </div>

  <div class="card">
    <h3 class="card__title">Ce qui reste prive</h3>
    <p>Tes mesures corporelles, ta readiness, tes notes, tes poids par serie : strictement privees. Meme dans une squad (groupe prive), seule l'activite agregee est partagee — jamais les details.</p>
  </div>
</section>

<!-- ================================================================ -->
<!-- SECTION 5 — ARCHITECTURE : diagramme SVG SSR statique            -->
<!-- ================================================================ -->
<section class="science-section" id="section-diagram">
  <h2 class="section-header">Architecture du produit</h2>
  <figure class="science-diagram">
    {% include "_partials/science_diagram.svg" %}
    <figcaption class="text-dim" style="font-size:12px;text-align:center;margin-top:var(--space-sm);">
      Les donnees alimentent un cockpit personnel unique. Les zones en pointille sont privees.
    </figcaption>
  </figure>
</section>
{% endblock %}
```

- [ ] **Step 2: Verify content is ready but diagram partial is missing**

Run: `pytest tests/test_mobile_polish.py tests/test_session_flow.py -v --tb=short -k rules` (existing rules tests may fail; will fix next)

- [ ] **Step 3: Commit**

```bash
git add app/templates/science.html
git commit -m "feat(sb-science): /science template — 5 editorial sections (pratique→principes→materialisation→architecture)"
```

---

### Task 3: SVG Architecture Diagram Partial

**Files:**
- Create: `app/templates/_partials/science_diagram.svg`

- [ ] **Step 1: Create the SVG partial**

Create `app/templates/_partials/science_diagram.svg`:

```svg
<svg viewBox="0 0 800 520" xmlns="http://www.w3.org/2000/svg"
     role="img" aria-labelledby="diagram-title diagram-desc"
     style="width:100%;height:auto;max-width:800px;display:block;margin:0 auto;">
  <title id="diagram-title">Architecture des modules SPIGNOS</title>
  <desc id="diagram-desc">
    Programmes alimente Seance. Seance alimente Historique. Historique alimente
    Synthese, Physique, Classement et Squads. Etat du jour et Mesures alimentent
    Synthese et Physique. Les donnees privees (mesures, etat du jour) ne sont
    jamais partagees dans Classement et Squads.
  </desc>

  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="7" markerHeight="7" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#9aa3ad" />
    </marker>
    <marker id="arrow-dim" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="7" markerHeight="7" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#6e7785" />
    </marker>
  </defs>

  <!-- Row 1: inputs -->
  <g>
    <!-- Programmes -->
    <rect x="40" y="40" width="140" height="50" rx="8"
          fill="#161a22" stroke="#f25f3a" stroke-width="2" />
    <text x="110" y="70" text-anchor="middle" fill="#e8ecf1"
          font-family="JetBrains Mono, monospace" font-size="12">Programmes</text>

    <!-- Etat du jour (prive) -->
    <rect x="330" y="40" width="140" height="50" rx="8"
          fill="#161a22" stroke="#6e7785" stroke-width="1" stroke-dasharray="4 3" />
    <text x="400" y="64" text-anchor="middle" fill="#e8ecf1"
          font-family="JetBrains Mono, monospace" font-size="12">Etat du jour</text>
    <text x="400" y="80" text-anchor="middle" fill="#6e7785"
          font-family="Inter, sans-serif" font-size="10">prive</text>

    <!-- Mesures (prive) -->
    <rect x="620" y="40" width="140" height="50" rx="8"
          fill="#161a22" stroke="#6e7785" stroke-width="1" stroke-dasharray="4 3" />
    <text x="690" y="64" text-anchor="middle" fill="#e8ecf1"
          font-family="JetBrains Mono, monospace" font-size="12">Mesures</text>
    <text x="690" y="80" text-anchor="middle" fill="#6e7785"
          font-family="Inter, sans-serif" font-size="10">prive</text>
  </g>

  <!-- Row 2: Seance (center pivot) -->
  <g>
    <rect x="330" y="170" width="140" height="50" rx="8"
          fill="#161a22" stroke="#f25f3a" stroke-width="2" />
    <text x="400" y="200" text-anchor="middle" fill="#e8ecf1"
          font-family="JetBrains Mono, monospace" font-size="12">Seance</text>
  </g>

  <!-- Row 3: Historique -->
  <g>
    <rect x="330" y="280" width="140" height="50" rx="8"
          fill="#161a22" stroke="#232834" stroke-width="1" />
    <text x="400" y="310" text-anchor="middle" fill="#e8ecf1"
          font-family="JetBrains Mono, monospace" font-size="12">Historique</text>
  </g>

  <!-- Row 4: outputs -->
  <g>
    <!-- Synthese -->
    <rect x="40" y="400" width="140" height="50" rx="8"
          fill="#161a22" stroke="#232834" stroke-width="1" />
    <text x="110" y="430" text-anchor="middle" fill="#e8ecf1"
          font-family="JetBrains Mono, monospace" font-size="12">Synthese</text>

    <!-- Physique -->
    <rect x="230" y="400" width="140" height="50" rx="8"
          fill="#161a22" stroke="#232834" stroke-width="1" />
    <text x="300" y="430" text-anchor="middle" fill="#e8ecf1"
          font-family="JetBrains Mono, monospace" font-size="12">Physique</text>

    <!-- Classement -->
    <rect x="420" y="400" width="140" height="50" rx="8"
          fill="#161a22" stroke="#232834" stroke-width="1" />
    <text x="490" y="430" text-anchor="middle" fill="#e8ecf1"
          font-family="JetBrains Mono, monospace" font-size="12">Classement</text>

    <!-- Squads -->
    <rect x="620" y="400" width="140" height="50" rx="8"
          fill="#161a22" stroke="#232834" stroke-width="1" />
    <text x="690" y="430" text-anchor="middle" fill="#e8ecf1"
          font-family="JetBrains Mono, monospace" font-size="12">Squads</text>
  </g>

  <!-- Edges -->
  <!-- Programmes → Seance -->
  <line x1="110" y1="90" x2="380" y2="170" stroke="#9aa3ad" stroke-width="1"
        marker-end="url(#arrow)" />
  <!-- Etat du jour → Synthese (long curve) -->
  <path d="M 380 90 Q 200 200 110 400" fill="none" stroke="#6e7785"
        stroke-width="1" stroke-dasharray="3 3" marker-end="url(#arrow-dim)" />
  <!-- Mesures → Physique + Synthese -->
  <path d="M 670 90 Q 500 200 300 400" fill="none" stroke="#6e7785"
        stroke-width="1" stroke-dasharray="3 3" marker-end="url(#arrow-dim)" />
  <path d="M 680 90 Q 400 200 150 400" fill="none" stroke="#6e7785"
        stroke-width="1" stroke-dasharray="3 3" marker-end="url(#arrow-dim)" />
  <!-- Seance → Historique -->
  <line x1="400" y1="220" x2="400" y2="280" stroke="#9aa3ad" stroke-width="1"
        marker-end="url(#arrow)" />
  <!-- Historique → Synthese, Physique, Classement, Squads -->
  <line x1="360" y1="330" x2="130" y2="400" stroke="#9aa3ad" stroke-width="1"
        marker-end="url(#arrow)" />
  <line x1="380" y1="330" x2="300" y2="400" stroke="#9aa3ad" stroke-width="1"
        marker-end="url(#arrow)" />
  <line x1="420" y1="330" x2="490" y2="400" stroke="#9aa3ad" stroke-width="1"
        marker-end="url(#arrow)" />
  <line x1="440" y1="330" x2="670" y2="400" stroke="#9aa3ad" stroke-width="1"
        marker-end="url(#arrow)" />

  <!-- Legend -->
  <g transform="translate(40, 480)">
    <line x1="0" y1="0" x2="30" y2="0" stroke="#9aa3ad" stroke-width="1"
          marker-end="url(#arrow)" />
    <text x="38" y="4" fill="#9aa3ad"
          font-family="Inter, sans-serif" font-size="11">flux principal</text>

    <line x1="180" y1="0" x2="210" y2="0" stroke="#6e7785" stroke-width="1"
          stroke-dasharray="3 3" marker-end="url(#arrow-dim)" />
    <text x="218" y="4" fill="#6e7785"
          font-family="Inter, sans-serif" font-size="11">donnee privee</text>
  </g>
</svg>
```

**Note on colors:** the SVG uses hardcoded hex values matching the CSS tokens (`#f25f3a`, `#161a22`, etc.). CSS variables don't propagate inside SVG elements reliably without JS, so hardcoded values are the SSR-compatible choice. If the palette changes, this SVG must be updated.

- [ ] **Step 2: Verify the SVG renders**

Start the server or test:
```bash
pytest tests/test_session_flow.py -v -k rules
```

Visit `/science` in browser — the diagram should render.

- [ ] **Step 3: Commit**

```bash
git add app/templates/_partials/science_diagram.svg
git commit -m "feat(sb-science): SVG SSR static architecture diagram (programmes → seance → historique → outputs)"
```

---

### Task 4: Home Tile Update + CSS

**Files:**
- Modify: `app/templates/index.html`
- Modify: `app/static/css/app.css`

- [ ] **Step 1: Update home tile**

In `app/templates/index.html`, find the Règles tile:

```html
<a class="tile" href="{{ url_for('rules_page') }}">
  <div class="tile__label">Règles</div>
  <div class="tile__hint">Rappels techniques</div>
</a>
```

Replace with:

```html
<a class="tile" href="{{ url_for('science_page') }}">
  <div class="tile__label">Science</div>
  <div class="tile__hint">Méthode et fonctionnement</div>
</a>
```

- [ ] **Step 2: Add CSS for science sections**

Append to `app/static/css/app.css`:

```css
/* ---- Science page sections ---- */
.science-section {
  margin-bottom: var(--space-xl);
}

.science-section > .card + .card {
  margin-top: var(--space-sm);
}

.science-diagram {
  margin: 0;
  padding: var(--space-md);
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow-x: auto;
}

.science-diagram svg {
  display: block;
  margin: 0 auto;
}
```

- [ ] **Step 3: Commit**

```bash
git add app/templates/index.html app/static/css/app.css
git commit -m "feat(sb-science): home tile Règles→Science + CSS science-section + science-diagram"
```

---

### Task 5: Fix Broken Tests + Add Science Tests

**Files:**
- Modify: existing tests referencing "Règles" or `/rules`
- Create: `tests/test_science_page.py`

- [ ] **Step 1: Create science-specific tests**

Create `tests/test_science_page.py`:

```python
"""Tests for the /science page (replaces /rules)."""
from __future__ import annotations


def test_science_page_renders(client):
    r = client.get("/science")
    assert r.status_code == 200
    assert "Science" in r.text
    assert "Pourquoi noter" in r.text


def test_science_page_shows_all_method_rules(client):
    """All 8 seeded method_rules must appear."""
    r = client.get("/science")
    body = r.text
    # Check rule anchors are present
    assert "id=\"rule-carnet-progression\"" in body
    assert "id=\"rule-plages-repetitions\"" in body
    assert "id=\"rule-series-approche\"" in body
    assert "id=\"rule-tempo\"" in body
    assert "id=\"rule-temps-repos\"" in body
    assert "id=\"rule-legende-technique\"" in body
    assert "id=\"rule-rest-pause\"" in body
    assert "id=\"rule-drop-sets\"" in body


def test_science_page_has_architecture_diagram(client):
    """The SVG diagram must be rendered."""
    r = client.get("/science")
    body = r.text
    assert "<svg" in body
    assert "diagram-title" in body
    assert "Programmes" in body
    assert "Seance" in body
    assert "Historique" in body


def test_science_page_has_cardio_section(client):
    """The cardio section must be present with the anti-pseudo-science disclaimer."""
    r = client.get("/science")
    body = r.text
    assert "Place du cardio" in body
    assert "LISS" in body
    assert "donnees cardio operatoires" in body


def test_science_page_has_materialisation_section(client):
    """The 'Comment SPIGNOS materialise' section must appear."""
    r = client.get("/science")
    body = r.text
    assert "Comment SPIGNOS materialise" in body
    assert "Ce qui reste prive" in body


def test_rules_redirects_to_science(client):
    """Legacy /rules must redirect (301) to /science."""
    r = client.get("/rules", follow_redirects=False)
    assert r.status_code == 301
    assert r.headers["location"] == "/science"


def test_home_tile_points_to_science(client):
    """Home tile 'Science' must link to /science."""
    r = client.get("/")
    body = r.text
    assert ">Science<" in body
    assert "/science" in body


def test_science_page_requires_auth(client):
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    r = client.get("/science", follow_redirects=False)
    assert r.status_code == 303
```

- [ ] **Step 2: Find and fix existing tests referencing /rules or "Règles"**

Search for broken assertions:
- Any test asserting `"Règles"` in home → should now expect `"Science"`
- Any test hitting `GET /rules` expecting 200 → should expect 301
- `tests/test_session_flow.py::test_rules_page_renders_seeded_rules` likely exists

Fix strategy: update assertions to match new text ("Science" instead of "Règles"), and update any direct `/rules` GET tests to follow the redirect or expect 301.

Example fix in `test_session_flow.py`:
```python
# OLD:
def test_rules_page_renders_seeded_rules(client):
    r = client.get("/rules")
    assert r.status_code == 200
    ...

# NEW:
def test_science_page_renders_seeded_rules(client):
    r = client.get("/science")
    assert r.status_code == 200
    ...
```

- [ ] **Step 3: Run all tests**

Run: `pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q`
Expected: All pass.

- [ ] **Step 4: Commit**

```bash
git add tests/
git commit -m "test(sb-science): add science page tests + adapt legacy rules tests"
```

---

### Task 6: Sprint Report

**Files:**
- Create: `docs/SPRINT_Sb_science_page_REPORT.md`

- [ ] **Step 1: Run full test suite**

Run: `pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q`
Expected: All pass.

- [ ] **Step 2: Write report**

Create `docs/SPRINT_Sb_science_page_REPORT.md`:

```markdown
# Sprint Sb_science_page Report

**Date:** 2026-04-14
**Status:** Complete
**Spec:** docs/strategy/SPIGNOS_SCIENCE_PAGE_SPEC.md

## Objective

Transform /rules into /science with 5 sections (pratique → principes → materialisation → architecture).
SVG SSR static diagram at the bottom.

## Deliverables

| Artifact | Path |
|----------|------|
| Route | `GET /science` in `pages.py` |
| Redirect | `GET /rules → 301 /science` |
| Template | `app/templates/science.html` |
| SVG partial | `app/templates/_partials/science_diagram.svg` |
| CSS | `.science-section`, `.science-diagram` in `app.css` |
| Home tile | `app/templates/index.html` updated |
| Tests | `tests/test_science_page.py` |

## 6 arbitrages respectes

- (4) Manuel d'usage, pas manifeste de marque
- (5) SVG SSR statique (pas Mermaid, pas hover)
- Ordre pratique → principes → materialisation → architecture

## Verification

```
pytest tests/test_science_page.py -v
pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q
```
```

- [ ] **Step 3: Commit**

```bash
git add docs/SPRINT_Sb_science_page_REPORT.md
git commit -m "docs(sb-science): sprint report — /science page + architecture diagram complete"
```
