# Sb_R3 — Session Terminal State Implementation Plan

> **For agentic workers:** Steps use checkbox (`- [ ]`) syntax for tracking. Each step is one action (2-5 minutes). TDD-first: failing test → verify fail → minimal impl → verify pass → commit.

**Goal:** Donner à la clôture de séance une vraie réponse visuelle — route dédiée `/sessions/{id}/done`, template lecture-seule avec résumé, CTA cohérents, ré-ouverture explicite.

**Architecture:** Zéro JS. Nouvelle route `GET /sessions/{id}/done` et nouveau template `session_done.html`. Le POST `action=end` existant bascule son redirect vers `/done`. L'accès direct à `/sessions/{id}` sur une séance `completed` est redirigé vers `/done`. `Rouvrir` reste un POST sur le feedback, bascule le status, puis redirige vers `/sessions/{id}` éditable. Aucune migration Alembic.

**Tech Stack:** FastAPI, Jinja2, SQLAlchemy, pytest + TestClient.

**Dépendances :** Aucune (standalone — cf. spec §13).

**Spec source :** [`SPIGNOS_SESSION_REAL_WORLD_ADAPTATION_AND_COMPLETION_SPEC.md`](./SPIGNOS_SESSION_REAL_WORLD_ADAPTATION_AND_COMPLETION_SPEC.md) Section III.

---

## File Structure

### À créer

| Fichier | Responsabilité |
|---|---|
| `app/services/session_recap.py` | Agrège les données de recap (résumé global + ligne par exercice) — pure lecture, une seule fonction publique `build_recap(session)`. |
| `app/templates/session_done.html` | Template dédié du mode recap (lecture seule). Extends `base.html`. |
| `tests/test_session_done.py` | Tests de route + redirect + contenu recap + Rouvrir + dispatch cardio. |
| `tests/test_session_recap.py` | Tests unitaires de `build_recap()`. |

### À modifier

| Fichier | Changement |
|---|---|
| `app/routers/sessions.py` | Nouvelle route `GET /sessions/{id}/done`. Dans `update_session` : si `action=end`, rediriger vers `/done` au lieu de `#session-feedback`. Dans `session_detail` : si `status=completed` et pas de query param `?edit=1`, rediriger vers `/done`. |
| `app/static/css/app.css` | Ajouter styles `.session-done-*` (header badge, résumé, liste compacte, CTA bas). |

### Inchangés (par conception)

- `app/templates/session_detail.html` — continue de servir uniquement l'état `in_progress` (après redirect).
- `app/services/quality_score.py`, `kpis.py`, `feedback.py` — aucun changement, le recap **consomme** leurs sorties.
- Modèle `session.py` — aucune migration.

---

## Task 1 — Service `build_recap()` (TDD)

**Files:**
- Create: `app/services/session_recap.py`
- Test: `tests/test_session_recap.py`

### Step 1.1 — Écrire le test d'échec

- [ ] Créer `tests/test_session_recap.py` :

```python
"""Tests for session_recap.build_recap — agrégat lecture-seule pour /done."""
from __future__ import annotations

from datetime import datetime, timezone

from app.services.session_recap import build_recap


def test_build_recap_returns_expected_shape(db_session, seed_catalog, user_fx):
    """build_recap returns a dict with keys: header, summary, exercises."""
    from tests.factories import make_completed_session  # helper to create

    session = make_completed_session(
        db_session,
        user_fx,
        template_slug="push-a",
        started_at=datetime(2026, 4, 13, 18, 45, tzinfo=timezone.utc),
        ended_at=datetime(2026, 4, 13, 20, 2, tzinfo=timezone.utc),
    )
    recap = build_recap(session)
    assert set(recap.keys()) == {"header", "summary", "exercises"}
    assert recap["header"]["duration_label"]  # non-empty
    assert isinstance(recap["exercises"], list)
```

### Step 1.2 — Vérifier l'échec

- [ ] Run: `pytest tests/test_session_recap.py -v`
- [ ] Expected: FAIL with `ModuleNotFoundError: app.services.session_recap`

### Step 1.3 — Implémentation minimale du service

- [ ] Créer `app/services/session_recap.py` :

```python
"""Read-only recap aggregation for the /done terminal state view.

Consumes existing session data. Computes no new analytics — only
assembles what's already derivable (duration, done/total work sets,
exercise summaries, substitution+added badges).
"""
from __future__ import annotations

from typing import Any

from app.models.session import WorkoutSession
from app.services.stats import summarise_current_exercise
from app.services.time_format import format_duration


def build_recap(session: WorkoutSession) -> dict[str, Any]:
    """Return a dict shaped for the session_done.html template."""
    duration_label = ""
    if session.ended_at and session.started_at:
        duration_label = format_duration(session.ended_at - session.started_at)

    total_work = 0
    done_work = 0
    exercises: list[dict[str, Any]] = []
    for se in session.session_exercises:
        work_sets = [sl for sl in se.set_logs if sl.kind == "work"]
        done = [sl for sl in work_sets if sl.completed]
        total_work += len(work_sets)
        done_work += len(done)
        summary = summarise_current_exercise(se)
        exercises.append({
            "code": se.exercise_code_snapshot,
            "name": se.exercise_name_snapshot,
            "substituted_name": se.substituted_name,
            "display_name": se.substituted_name or se.exercise_name_snapshot,
            "done": len(done),
            "total": len(work_sets),
            "score": se.success_score,
            "weights_str": summary["weights_str"] if summary else None,
            "reps_str": summary["reps_str"] if summary else None,
        })

    completion_pct = round(100 * done_work / total_work) if total_work else None
    substitution_count = sum(1 for e in exercises if e["substituted_name"])

    return {
        "header": {
            "template_name": session.template_name_snapshot,
            "started_at": session.started_at,
            "ended_at": session.ended_at,
            "duration_label": duration_label,
        },
        "summary": {
            "work_sets_done": done_work,
            "work_sets_total": total_work,
            "completion_pct": completion_pct,
            "substitution_count": substitution_count,
            "bodyweight_kg": session.bodyweight_kg,
            "concentration": session.concentration,
            "global_state": session.global_state,
        },
        "exercises": exercises,
    }
```

### Step 1.4 — Créer la factory de test (si absente)

- [ ] Si `tests/factories.py` n'a pas `make_completed_session`, l'ajouter. Sinon passer.

```python
# tests/factories.py (ajout ou création)
from datetime import datetime, timezone

from app.enums import SessionStatus
from app.models.session import WorkoutSession, SessionExercise, SetLog
from app.models.catalog import WorkoutTemplate, TemplateExercise


def make_completed_session(
    db, user, template_slug="push-a",
    started_at=None, ended_at=None,
) -> WorkoutSession:
    """Create a minimal completed session with 2 exercises, each 3 work sets,
    half of them completed, for recap testing."""
    started = started_at or datetime(2026, 4, 13, 18, 0, tzinfo=timezone.utc)
    ended = ended_at or datetime(2026, 4, 13, 19, 30, tzinfo=timezone.utc)
    session = WorkoutSession(
        user_id=user.id,
        template_slug_snapshot=template_slug,
        template_name_snapshot="Push A — test",
        started_at=started,
        ended_at=ended,
        status=SessionStatus.COMPLETED,
        concentration="high",
        global_state="good",
        bodyweight_kg=79.4,
    )
    db.add(session)
    db.flush()

    for pos, (code, name) in enumerate([("E1", "Incline Smith Press"), ("E2", "Chest Press machine")], start=1):
        se = SessionExercise(
            session_id=session.id,
            exercise_code_snapshot=code,
            exercise_name_snapshot=name,
            position=pos,
            success_score=80,
        )
        db.add(se)
        db.flush()
        for i in range(1, 4):
            sl = SetLog(
                session_exercise_id=se.id,
                kind="work",
                set_index=i,
                weight_kg=60.0,
                reps=10,
                completed=(i <= 2),  # 2/3 completed
            )
            db.add(sl)

    db.commit()
    db.refresh(session)
    return session
```

### Step 1.5 — Vérifier le test passe

- [ ] Run: `pytest tests/test_session_recap.py -v`
- [ ] Expected: PASS

### Step 1.6 — Ajouter test de substitution visible dans le recap

- [ ] Ajouter à `tests/test_session_recap.py` :

```python
def test_build_recap_marks_substituted_exercise(db_session, seed_catalog, user_fx):
    session = make_completed_session(db_session, user_fx)
    se0 = session.session_exercises[0]
    se0.substituted_name = "Développé couché haltères"
    db_session.commit()

    recap = build_recap(session)
    e0 = recap["exercises"][0]
    assert e0["substituted_name"] == "Développé couché haltères"
    assert e0["display_name"] == "Développé couché haltères"
    assert recap["summary"]["substitution_count"] == 1
```

- [ ] Run: `pytest tests/test_session_recap.py -v`
- [ ] Expected: PASS

### Step 1.7 — Commit

```bash
git add app/services/session_recap.py tests/test_session_recap.py tests/factories.py
git commit -m "feat(session-recap): add build_recap() aggregator for terminal state"
```

---

## Task 2 — Route `GET /sessions/{id}/done` (TDD)

**Files:**
- Modify: `app/routers/sessions.py`
- Create: `app/templates/session_done.html` (stub minimal pour faire passer le test de status)
- Test: `tests/test_session_done.py`

### Step 2.1 — Test d'échec : la route n'existe pas encore

- [ ] Créer `tests/test_session_done.py` :

```python
"""Tests for the /sessions/{id}/done terminal-state route."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from tests.factories import make_completed_session


def test_done_route_returns_200_for_completed_session(client_auth, db_session, user_fx, seed_catalog):
    session = make_completed_session(db_session, user_fx)
    r = client_auth.get(f"/sessions/{session.id}/done")
    assert r.status_code == 200
    assert "Séance terminée" in r.text


def test_done_route_redirects_when_session_in_progress(client_auth, db_session, user_fx, seed_catalog):
    session = make_completed_session(db_session, user_fx)
    from app.enums import SessionStatus
    session.status = SessionStatus.IN_PROGRESS
    session.ended_at = None
    db_session.commit()

    r = client_auth.get(f"/sessions/{session.id}/done", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == f"/sessions/{session.id}"


def test_done_route_404_for_other_users_session(client_auth_other, db_session, user_fx, seed_catalog):
    session = make_completed_session(db_session, user_fx)
    r = client_auth_other.get(f"/sessions/{session.id}/done")
    assert r.status_code == 404
```

### Step 2.2 — Vérifier l'échec

- [ ] Run: `pytest tests/test_session_done.py::test_done_route_returns_200_for_completed_session -v`
- [ ] Expected: FAIL with 404 (route not defined)

### Step 2.3 — Créer le template stub

- [ ] Créer `app/templates/session_done.html` :

```html
{% extends "base.html" %}
{% block content %}
<div class="session-done">
  <header class="session-done__header">
    <div class="session-done__badge">✓ Séance terminée</div>
    <h1 class="page-title">{{ recap.header.template_name }}</h1>
    <div class="session-done__meta text-dim">
      {{ recap.header.started_at.strftime('%a %d/%m %H:%M') }}
      {% if recap.header.ended_at %}
        → {{ recap.header.ended_at.strftime('%H:%M') }}
      {% endif %}
      {% if recap.header.duration_label %}
        · {{ recap.header.duration_label }}
      {% endif %}
    </div>
  </header>
</div>
{% endblock %}
```

### Step 2.4 — Ajouter la route

- [ ] Dans `app/routers/sessions.py`, après `session_detail` (vers ligne 265), ajouter :

```python
@router.get("/sessions/{session_id}/done", response_class=HTMLResponse, name="session_done")
def session_done(
    session_id: int, request: Request, db: DbSession, user: CurrentUser
) -> HTMLResponse | RedirectResponse:
    session = _load_session(db, session_id, user.id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != SessionStatus.COMPLETED:
        return RedirectResponse(url=f"/sessions/{session_id}", status_code=303)

    from app.services.session_recap import build_recap
    recap = build_recap(session)
    return templates.TemplateResponse(
        request,
        "session_done.html",
        {
            "page_title": session.template_name_snapshot,
            "session": session,
            "recap": recap,
        },
    )
```

### Step 2.5 — Vérifier les 3 tests passent

- [ ] Run: `pytest tests/test_session_done.py -v`
- [ ] Expected: 3 PASS

### Step 2.6 — Commit

```bash
git add app/routers/sessions.py app/templates/session_done.html tests/test_session_done.py
git commit -m "feat(session-done): add /sessions/{id}/done route with guard on status"
```

---

## Task 3 — Rediriger le POST `action=end` vers `/done` (TDD)

**Files:**
- Modify: `app/routers/sessions.py`
- Test: `tests/test_session_done.py` (ajouts)

### Step 3.1 — Test d'échec

- [ ] Ajouter à `tests/test_session_done.py` :

```python
def test_action_end_redirects_to_done(client_auth, db_session, user_fx, seed_catalog):
    from app.enums import SessionStatus
    session = make_completed_session(db_session, user_fx)
    session.status = SessionStatus.IN_PROGRESS
    session.ended_at = None
    db_session.commit()

    r = client_auth.post(
        f"/sessions/{session.id}",
        data={"action": "end"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert r.headers["location"] == f"/sessions/{session.id}/done"


def test_action_reopen_redirects_to_editable_session(client_auth, db_session, user_fx, seed_catalog):
    session = make_completed_session(db_session, user_fx)
    r = client_auth.post(
        f"/sessions/{session.id}",
        data={"action": "reopen"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert r.headers["location"] == f"/sessions/{session.id}"
```

### Step 3.2 — Vérifier l'échec

- [ ] Run: `pytest tests/test_session_done.py::test_action_end_redirects_to_done -v`
- [ ] Expected: FAIL — redirect va vers `#session-feedback`, pas `/done`.

### Step 3.3 — Modifier `update_session` pour router le redirect

- [ ] Dans `app/routers/sessions.py`, remplacer le bloc de fin de `update_session` (lignes ~295-305) :

**Avant :**
```python
if form.get("action") == "end":
    session.ended_at = datetime.now(timezone.utc)
    session.status = SessionStatus.COMPLETED
elif form.get("action") == "reopen" and session.status == SessionStatus.COMPLETED:
    session.ended_at = None
    session.status = SessionStatus.IN_PROGRESS

db.commit()
return RedirectResponse(
    url=f"/sessions/{session_id}#session-feedback", status_code=303
)
```

**Après :**
```python
action = form.get("action")
if action == "end":
    session.ended_at = datetime.now(timezone.utc)
    session.status = SessionStatus.COMPLETED
elif action == "reopen" and session.status == SessionStatus.COMPLETED:
    session.ended_at = None
    session.status = SessionStatus.IN_PROGRESS

db.commit()

if action == "end":
    return RedirectResponse(url=f"/sessions/{session_id}/done", status_code=303)
if action == "reopen":
    return RedirectResponse(url=f"/sessions/{session_id}", status_code=303)
return RedirectResponse(
    url=f"/sessions/{session_id}#session-feedback", status_code=303
)
```

### Step 3.4 — Vérifier les tests passent

- [ ] Run: `pytest tests/test_session_done.py -v`
- [ ] Expected: tous PASS

### Step 3.5 — Lancer la suite feedback existante pour éviter toute régression

- [ ] Run: `pytest tests/test_session_flow.py tests/test_session_routes.py -q`
- [ ] Si un test échoue car il attendait `#session-feedback` après `action=end`, le mettre à jour pour attendre `/done`.

### Step 3.6 — Commit

```bash
git add app/routers/sessions.py tests/test_session_done.py
git commit -m "feat(session-done): redirect action=end to /done, reopen to editable"
```

---

## Task 4 — Rediriger l'accès direct à une séance `completed` vers `/done` (TDD)

**Files:**
- Modify: `app/routers/sessions.py` (dans `session_detail`)
- Test: `tests/test_session_done.py` (ajouts)

### Step 4.1 — Test d'échec

- [ ] Ajouter à `tests/test_session_done.py` :

```python
def test_get_session_completed_redirects_to_done(client_auth, db_session, user_fx, seed_catalog):
    session = make_completed_session(db_session, user_fx)
    r = client_auth.get(f"/sessions/{session.id}", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == f"/sessions/{session.id}/done"


def test_get_session_in_progress_renders_normally(client_auth, db_session, user_fx, seed_catalog):
    from app.enums import SessionStatus
    session = make_completed_session(db_session, user_fx)
    session.status = SessionStatus.IN_PROGRESS
    session.ended_at = None
    db_session.commit()
    r = client_auth.get(f"/sessions/{session.id}")
    assert r.status_code == 200
    assert "session-feedback" in r.text  # éditable = feedback form visible
```

### Step 4.2 — Vérifier l'échec du premier test

- [ ] Run: `pytest tests/test_session_done.py::test_get_session_completed_redirects_to_done -v`
- [ ] Expected: FAIL (GET retourne 200, pas 303)

### Step 4.3 — Ajouter le guard dans `session_detail`

- [ ] Dans `app/routers/sessions.py`, au début de `session_detail` juste après `if session is None: raise ...` (ligne ~156) :

```python
if session.status == SessionStatus.COMPLETED:
    return RedirectResponse(
        url=f"/sessions/{session_id}/done", status_code=303
    )
```

- [ ] Modifier la signature de retour de `session_detail` pour autoriser `RedirectResponse` :

```python
def session_detail(
    session_id: int, request: Request, db: DbSession, user: CurrentUser
) -> HTMLResponse | RedirectResponse:
```

### Step 4.4 — Vérifier les tests passent

- [ ] Run: `pytest tests/test_session_done.py -v`
- [ ] Expected: tous PASS

### Step 4.5 — Lancer la suite complète pour détecter les régressions

- [ ] Run: `pytest -q -k "session" 2>&1 | tail -20`
- [ ] Si un test appelait `GET /sessions/{id}` sur une session completed pour vérifier un rendu éditable, l'adapter : soit passer par `Rouvrir` avant, soit tester `/done` à la place.

### Step 4.6 — Commit

```bash
git add app/routers/sessions.py tests/test_session_done.py
git commit -m "feat(session-done): redirect GET on completed session to /done"
```

---

## Task 5 — Contenu complet du template recap (TDD)

**Files:**
- Modify: `app/templates/session_done.html`
- Test: `tests/test_session_done.py` (ajouts)

### Step 5.1 — Tests d'échec sur le contenu du recap

- [ ] Ajouter à `tests/test_session_done.py` :

```python
def test_done_page_shows_summary_block(client_auth, db_session, user_fx, seed_catalog):
    session = make_completed_session(db_session, user_fx)
    r = client_auth.get(f"/sessions/{session.id}/done")
    body = r.text
    # Summary
    assert "Work sets" in body
    assert "4 / 6" in body  # 2 exos × 2/3 done from factory
    assert "79,4" in body or "79.4" in body  # bodyweight
    # Per-exercise line
    assert "E1" in body
    assert "Incline Smith Press" in body
    assert "2/3" in body
    # CTAs
    assert 'href="/dashboard"' in body or "Synthèse" in body
    assert 'href="/history"' in body or "Historique" in body
    # Reopen form (discreet)
    assert "Rouvrir" in body
    assert 'action="/sessions/{}"'.format(session.id) in body


def test_done_page_shows_substitution_arrow(client_auth, db_session, user_fx, seed_catalog):
    session = make_completed_session(db_session, user_fx)
    se0 = session.session_exercises[0]
    se0.substituted_name = "Développé couché haltères"
    db_session.commit()

    r = client_auth.get(f"/sessions/{session.id}/done")
    assert "Développé couché haltères" in r.text
    assert "→" in r.text
```

### Step 5.2 — Vérifier l'échec

- [ ] Run: `pytest tests/test_session_done.py::test_done_page_shows_summary_block -v`
- [ ] Expected: FAIL (le stub actuel n'affiche que le header)

### Step 5.3 — Compléter le template

- [ ] Remplacer `app/templates/session_done.html` par :

```html
{% extends "base.html" %}
{% block content %}
<div class="session-done">

  {# ─── Header ─── #}
  <header class="session-done__header card">
    <div class="session-done__badge">✓ Séance terminée</div>
    <h1 class="page-title session-done__title">{{ recap.header.template_name }}</h1>
    <div class="session-done__meta text-dim">
      {{ recap.header.started_at.strftime('%a %d/%m %H:%M') }}
      {% if recap.header.ended_at %}
        → {{ recap.header.ended_at.strftime('%H:%M') }}
      {% endif %}
      {% if recap.header.duration_label %}
        · {{ recap.header.duration_label }}
      {% endif %}
    </div>
  </header>

  {# ─── Résumé ─── #}
  <section class="card session-done__summary">
    <h2 class="card__title">Résumé</h2>
    <ul class="session-done__stats">
      <li>
        <span>Work sets</span>
        <b>
          {{ recap.summary.work_sets_done }} / {{ recap.summary.work_sets_total }}
          {% if recap.summary.completion_pct is not none %}
            ({{ recap.summary.completion_pct }}%)
          {% endif %}
        </b>
      </li>
      {% if recap.summary.substitution_count > 0 %}
        <li>
          <span>Substitutions</span>
          <b>{{ recap.summary.substitution_count }}</b>
        </li>
      {% endif %}
      {% if recap.summary.bodyweight_kg %}
        <li>
          <span>Bodyweight</span>
          <b>{{ "%.1f"|format(recap.summary.bodyweight_kg)|replace('.', ',') }} kg</b>
        </li>
      {% endif %}
      {% if recap.summary.concentration %}
        <li>
          <span>Concentration</span>
          <b>{{ recap.summary.concentration }}</b>
        </li>
      {% endif %}
      {% if recap.summary.global_state %}
        <li>
          <span>État</span>
          <b>{{ recap.summary.global_state }}</b>
        </li>
      {% endif %}
    </ul>
  </section>

  {# ─── Par exercice ─── #}
  <section class="card session-done__exercises">
    <h2 class="card__title">Par exercice</h2>
    <ul class="session-done__exlist">
      {% for ex in recap.exercises %}
        <li class="session-done__exrow">
          <span class="session-done__code">{{ ex.code }}</span>
          <span class="session-done__name">
            {% if ex.substituted_name %}
              → {{ ex.substituted_name }}
            {% else %}
              {{ ex.name }}
            {% endif %}
          </span>
          <span class="session-done__prog">{{ ex.done }}/{{ ex.total }}</span>
          {% if ex.score is not none %}
            <span class="session-done__score">{{ ex.score }}</span>
          {% endif %}
        </li>
      {% endfor %}
    </ul>
  </section>

  {# ─── CTA principaux ─── #}
  <div class="session-done__cta">
    <a class="btn btn--primary btn--wide" href="{{ url_for('dashboard') }}">
      Voir la synthèse →
    </a>
    <a class="btn btn--wide" href="{{ url_for('history') }}">
      Historique →
    </a>
  </div>

  {# ─── Rouvrir (discret) ─── #}
  <form method="post"
        action="{{ url_for('update_session', session_id=session.id) }}"
        class="session-done__reopen">
    <input type="hidden" name="action" value="reopen">
    <button type="submit" class="btn btn--ghost btn--sm">
      Rouvrir pour éditer
    </button>
  </form>

</div>
{% endblock %}
```

### Step 5.4 — Ajouter les styles CSS

- [ ] Dans `app/static/css/app.css`, ajouter à la fin du fichier :

```css
/* ---- Session Done (Sb_R3 terminal state) ---- */

.session-done { display: block; }

.session-done__header {
  text-align: center;
  margin-bottom: var(--space-md);
  border-left: 3px solid var(--ok);
}
.session-done__badge {
  display: inline-block;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--ok);
  margin-bottom: var(--space-xs);
}
.session-done__title { margin: 0 0 var(--space-xs); }
.session-done__meta { font-size: 13px; }

.session-done__stats {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: var(--space-xs);
}
.session-done__stats li {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}
.session-done__stats span { color: var(--fg-muted); }

.session-done__exlist {
  list-style: none;
  padding: 0;
  margin: 0;
}
.session-done__exrow {
  display: grid;
  grid-template-columns: auto 1fr auto auto;
  gap: var(--space-sm);
  align-items: baseline;
  padding: 6px 0;
  border-bottom: 1px solid var(--border);
  font-size: 14px;
}
.session-done__exrow:last-child { border-bottom: none; }
.session-done__code {
  font-family: var(--font-mono);
  font-weight: 600;
  color: var(--accent);
}
.session-done__name { color: var(--fg); }
.session-done__prog, .session-done__score {
  font-family: var(--font-mono);
  color: var(--fg-muted);
  font-size: 13px;
}

.session-done__cta {
  display: flex;
  gap: var(--space-sm);
  margin: var(--space-md) 0;
  flex-wrap: wrap;
}
.session-done__cta .btn { flex: 1; min-width: 140px; }

.session-done__reopen {
  text-align: center;
  margin-top: var(--space-lg);
  padding-top: var(--space-md);
  border-top: 1px solid var(--border);
}
```

### Step 5.5 — Vérifier les tests passent

- [ ] Run: `pytest tests/test_session_done.py -v`
- [ ] Expected: tous PASS

### Step 5.6 — Commit

```bash
git add app/templates/session_done.html app/static/css/app.css tests/test_session_done.py
git commit -m "feat(session-done): full recap template + styles (header, summary, per-exercise, CTAs)"
```

---

## Task 6 — Dispatch cardio (TDD)

**Files:**
- Modify: `app/templates/session_done.html`, `app/services/session_recap.py`
- Test: `tests/test_session_done.py` (ajouts)

### Step 6.1 — Test d'échec

- [ ] Ajouter à `tests/test_session_done.py` :

```python
def test_done_page_shows_cardio_recap_for_cardio_kind(client_auth, db_session, user_fx, seed_catalog):
    from tests.factories import make_completed_cardio_session
    session = make_completed_cardio_session(
        db_session, user_fx,
        duration_min=45, bpm_avg=132, machine_calories=410, machine_type="stairmaster",
    )
    r = client_auth.get(f"/sessions/{session.id}/done")
    body = r.text
    assert "45" in body and "min" in body
    assert "132" in body and "bpm" in body.lower()
    assert "410" in body
    # Strength table must NOT render
    assert "Par exercice" not in body
```

### Step 6.2 — Ajouter la factory cardio

- [ ] Ajouter à `tests/factories.py` :

```python
def make_completed_cardio_session(
    db, user,
    duration_min=30, bpm_avg=130, machine_calories=300, machine_type="rowing",
) -> WorkoutSession:
    session = WorkoutSession(
        user_id=user.id,
        template_slug_snapshot="cardio-liss",
        template_name_snapshot="Cardio LISS — test",
        started_at=datetime(2026, 4, 13, 18, 0, tzinfo=timezone.utc),
        ended_at=datetime(2026, 4, 13, 18, 45, tzinfo=timezone.utc),
        status=SessionStatus.COMPLETED,
        cardio_duration_min=duration_min,
        cardio_bpm_avg=bpm_avg,
        cardio_machine_calories=machine_calories,
        cardio_machine_type=machine_type,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session
```

### Step 6.3 — Vérifier l'échec

- [ ] Run: `pytest tests/test_session_done.py::test_done_page_shows_cardio_recap_for_cardio_kind -v`
- [ ] Expected: FAIL (table "Par exercice" encore rendue)

### Step 6.4 — Enrichir `build_recap` pour exposer le kind

- [ ] Dans `app/services/session_recap.py`, dans le dict retourné, ajouter au bloc `header` :

```python
"kind": (session.template.kind if session.template else "strength"),
```

- [ ] Dans `summary`, si kind=cardio, ajouter les champs cardio :

```python
summary_cardio = None
is_cardio = session.template and session.template.kind == "cardio"
if is_cardio:
    summary_cardio = {
        "duration_min": session.cardio_duration_min,
        "bpm_avg": session.cardio_bpm_avg,
        "machine_calories": session.cardio_machine_calories,
        "machine_type": session.cardio_machine_type,
    }
```

- [ ] Retourner `"cardio": summary_cardio` dans le dict `summary`.

### Step 6.5 — Adapter le template

- [ ] Dans `session_done.html`, wrapper le bloc "Par exercice" avec :

```html
{% if recap.header.kind != 'cardio' %}
  <section class="card session-done__exercises">
    ...
  </section>
{% endif %}
```

- [ ] Ajouter un bloc cardio avant ou à la place :

```html
{% if recap.header.kind == 'cardio' and recap.summary.cardio %}
  <section class="card session-done__cardio">
    <h2 class="card__title">Cardio</h2>
    <ul class="session-done__stats">
      {% if recap.summary.cardio.duration_min %}
        <li><span>Durée</span><b>{{ recap.summary.cardio.duration_min }} min</b></li>
      {% endif %}
      {% if recap.summary.cardio.bpm_avg %}
        <li><span>BPM moyen</span><b>{{ recap.summary.cardio.bpm_avg }} bpm</b></li>
      {% endif %}
      {% if recap.summary.cardio.machine_calories %}
        <li>
          <span>Calories machine</span>
          <b>{{ recap.summary.cardio.machine_calories }}
            <span class="text-dim" style="font-size:11px;">(indicatif)</span></b>
        </li>
      {% endif %}
      {% if recap.summary.cardio.machine_type %}
        <li><span>Machine</span><b>{{ recap.summary.cardio.machine_type }}</b></li>
      {% endif %}
    </ul>
  </section>
{% endif %}
```

### Step 6.6 — Vérifier les tests passent

- [ ] Run: `pytest tests/test_session_done.py -v`
- [ ] Expected: tous PASS (incluant le cardio)

### Step 6.7 — Commit

```bash
git add app/services/session_recap.py app/templates/session_done.html tests/test_session_done.py tests/factories.py
git commit -m "feat(session-done): dispatch cardio recap (duration/bpm/calories) vs strength table"
```

---

## Task 7 — Lien depuis le cockpit pour les séances terminées récemment

**Files:**
- Modify: `app/templates/index.html` (optionnel, nice-to-have)

### Step 7.1 — Décision

- [ ] Décider : faut-il un lien `Voir la séance terminée` sur le cockpit si la dernière séance a été bouclée aujourd'hui ? **Recommandation : non en V1**, le flow naturel est POST end → /done → CTA. Skip Task 7. Revoir après feedback terrain.

---

## Task 8 — Revue globale et acceptance

### Step 8.1 — Full test run

- [ ] Run: `pytest -q 2>&1 | tail -15`
- [ ] Expected: tous les tests pertinents PASS ; les 6 échecs pré-existants `.vscode/*` et `.env.production.example` sont tolérés.

### Step 8.2 — Vérifier le chemin critique manuellement (si dev server dispo)

- [ ] Démarrer le serveur : `uvicorn app.main:app --reload`
- [ ] Créer une séance, saisir quelques sets, cliquer Terminer → vérifier qu'on arrive sur `/done` avec header vert + résumé.
- [ ] Cliquer Rouvrir → vérifier qu'on revient sur la page éditable.
- [ ] Accéder directement à `/sessions/{id}` d'une séance completed via l'historique → vérifier redirect vers `/done`.
- [ ] Créer une séance cardio, la terminer → vérifier le recap cardio (durée/bpm/calories).

### Step 8.3 — Mettre à jour les docs stratégiques

- [ ] Dans `docs/strategy/SPIGNOS_EXERCISE_SYSTEM_ROADMAP.md`, ajouter une ligne "Phase 5 — R_T3SX (session real-world adaptation) : Sb_R3 livré ✓".
- [ ] Dans `docs/strategy/SPIGNOS_SUPERPOWER_SPRINT_QUEUE.md`, marquer Sb_R3 en complete, noter que Sb_R1 est la prochaine priorité.

### Step 8.4 — Commit final et sprint report

- [ ] Créer `docs/SPRINT_Sb_R3_REPORT.md` avec : résumé livré, fichiers modifiés, tests ajoutés, acceptance criteria cochés, next steps (Sb_R1).

```bash
git add docs/
git commit -m "docs(Sb_R3): sprint report + roadmap update for terminal state build"
```

---

## Acceptance Criteria (dériv de la spec §12 Axe 3)

- [ ] Route `GET /sessions/{id}/done` existe et répond 200 pour une séance completed du user propriétaire.
- [ ] Route retourne 404 pour un autre user, 303 → `/sessions/{id}` pour une séance `in_progress`.
- [ ] POST `action=end` redirige vers `/done` (plus vers `#session-feedback`).
- [ ] POST `action=reopen` redirige vers `/sessions/{id}` éditable.
- [ ] GET `/sessions/{id}` sur une séance completed redirige vers `/done`.
- [ ] Template recap affiche : header ✓ + titre + durée, résumé (work sets, bodyweight, concentration, état, substitutions count), liste par exercice (code, nom ou `→ substituté`, done/total, score).
- [ ] CTAs "Voir la synthèse" et "Historique" présents et fonctionnels.
- [ ] "Rouvrir pour éditer" discret et fonctionnel (bouton POST).
- [ ] Dispatch cardio : pour `template.kind=cardio`, affiche durée/BPM/calories au lieu de la table exercice.
- [ ] Aucun JS ajouté (zéro `<script>` hors de ce qui existait déjà).
- [ ] Aucune migration Alembic.
- [ ] Tous les tests passent, aucune régression sur les suites `session_flow`, `session_routes`, `kpis`, `quality_score`.

---

## Risques spécifiques au build

| Risque | Mitigation |
|---|---|
| Tests existants testant le redirect vers `#session-feedback` après `action=end` | À identifier via `grep "session-feedback" tests/`, adapter un par un. |
| Un test fait `GET /sessions/{id}` puis asserte le rendu complet sur une session completed | Modifier le test : soit créer une session `in_progress`, soit tester `/done`. |
| `template.kind` est `None` pour les sessions très anciennes dont le template a été dé-seedé | `session.template` peut être `None` → fallback `kind="strength"` dans `build_recap` (déjà codé). |
| `summarise_current_exercise` retourne `None` pour un exercice sans set log | Géré : on passe par un ternaire. |

---

## DO NOT BUILD (dans ce sprint)

- Lien depuis le cockpit vers la dernière séance terminée (cf. Task 7).
- Graphique ou courbe d'évolution sur le recap (la Synthèse en a déjà).
- Animation ou confetti.
- Son ou vibration.
- Modification du flow saisie (Sb_02 reste intact).
- Toute logique added (c'est Sb_R2, pas Sb_R3).

---

**Fin du plan.**
