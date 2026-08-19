"""Sb_29.4 — Rest timer progressive enhancement tests.

Verifies:
* `app/templates/_partials/rest_timer.html` exists.
* No-JS fallback markup "Repos suggéré" is rendered on the session page.
* `data-start-rest` and `data-rest-duration` attributes are present
  on the active card rest timer wrapper.
* `app/static/js/session_focus.js` exists and is vanilla JS (no React,
  no Vue, no Angular, no import / require).
* `session_focus.js` contains cleanup logic (clearInterval).
* `session_detail.html` loads `session_focus.js`.
* No critical action depends on JS (POST forms still standalone).
* Sticky CTA from Sb_29.3 still present (no regression).
* Update_exercise_card form action preserved.
* Owner isolation preserved (Sb_26.7).
* No new JS file other than preview.js + session_focus.js.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARTIAL_REST = ROOT / "app" / "templates" / "_partials" / "rest_timer.html"
PARTIAL_CARD = ROOT / "app" / "templates" / "_partials" / "exercise_card.html"
SESSION_DETAIL = ROOT / "app" / "templates" / "session_detail.html"
JS_FILE = ROOT / "app" / "static" / "js" / "session_focus.js"
APP_CSS = ROOT / "app" / "static" / "css" / "app.css"
FOCUS_CSS = ROOT / "app" / "static" / "css" / "session_focus.css"


# ───────── seed helpers ─────────


def _seed_in_progress(db, user_id, n_exercises=2):
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    s = WorkoutSession(
        user_id=user_id,
        template_slug_snapshot="rest-timer",
        template_name_snapshot="Rest timer test",
        started_at=datetime.now(UTC),
        status="in_progress",
    )
    for i in range(n_exercises):
        se = SessionExercise(
            exercise_code_snapshot=f"R{i + 1}",
            exercise_name_snapshot=f"Exercise {i + 1}",
            position=i + 1,
        )
        se.set_logs.append(
            SetLog(kind="work", set_index=1, weight_kg=80.0, reps=8, completed=False)
        )
        s.session_exercises.append(se)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def _render(client, session_id, query: str = "") -> str:
    """`query` permet de demander l'état `REST`, désormais le SEUL état où le
    minuteur existe (`Sx_UIV3_02 §7.2`)."""
    r = client.get(f"/sessions/{session_id}{query}", follow_redirects=False)
    assert r.status_code == 200, r.text[:400]
    return r.text


# ───────── partial / files exist ─────────


def test_rest_timer_partial_exists():
    assert PARTIAL_REST.exists(), "rest_timer.html partial missing"
    body = PARTIAL_REST.read_text(encoding="utf-8")
    assert "session-focus__rest-timer" in body
    assert "data-start-rest" in body
    assert "data-rest-duration" in body
    assert "Repos suggéré" in body


def test_session_focus_js_exists():
    assert JS_FILE.exists(), "session_focus.js missing"


# ───────── no-JS markup rendered ─────────


def test_no_js_fallback_text_present(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_in_progress(db, user.id)
        session_id = session.id

    body = _render(client, session_id)
    # MIGRÉ — le repli statique existe toujours, mais dans l'état `REST` seul.
    # Hors repos, il n'y a pas de repos à annoncer : le rendre en permanence
    # est ce qui a masqué le défaut `D3`.
    rest_body = _render(client, session_id, query="?rest=1")
    assert "Repos" in rest_body
    assert "Repos suggéré" not in body


def test_data_start_rest_attr_present(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_in_progress(db, user.id)
        session_id = session.id

    # MIGRÉ — `data-start-rest` est SUPPRIMÉ : rendu inconditionnellement,
    # il faisait démarrer le décompte pendant la série. Le seul déclencheur
    # est désormais `data-rest-started`, posé par le serveur.
    body = _render(client, session_id, query="?rest=1")
    assert "data-start-rest=" not in body
    assert 'data-rest-started="1"' in body
    assert "data-rest-duration=" in body


def test_rest_timer_only_on_active_card(client):
    """Rest timer is included only inside the active card."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_in_progress(db, user.id, n_exercises=3)
        session_id = session.id

    body = _render(client, session_id, query="?rest=1")
    occurrences = body.count("rest-readout")
    assert occurrences >= 1, "le minuteur doit exister à l'état repos"
    plain = _render(client, session_id)
    assert "rest-readout" not in plain, (
        "et nulle part ailleurs — c'est l'objet de la correction D3"
    )


# ───────── JS contract ─────────


def test_session_focus_js_is_vanilla():
    src = JS_FILE.read_text(encoding="utf-8")
    forbidden = (
        "import ",
        "require(",
        "from 'react'",
        'from "react"',
        "ReactDOM",
        "Vue.",
        "angular",
        "@angular",
        "esm.sh",
        "unpkg.com",
    )
    low = src
    for token in forbidden:
        assert token not in low, f"forbidden token in session_focus.js: {token!r}"


def test_session_focus_js_has_cleanup():
    src = JS_FILE.read_text(encoding="utf-8")
    assert "clearInterval" in src, (
        "session_focus.js must include cleanup via clearInterval"
    )


def test_session_focus_js_reads_data_attributes():
    src = JS_FILE.read_text(encoding="utf-8")
    assert "data-start-rest" in src
    assert "data-rest-duration" in src or "data-start-rest" in src


def test_session_focus_js_default_90s():
    src = JS_FILE.read_text(encoding="utf-8")
    assert "90" in src, "default 90s fallback not found in session_focus.js"


def test_session_focus_js_handles_empty_dom():
    """The init function must not throw when no [data-start-rest] is in DOM.

    We assert structural guard: a length-or-existence check before iteration.
    """
    src = JS_FILE.read_text(encoding="utf-8")
    # Either an explicit length === 0 / length == 0 / !length guard.
    pattern = re.compile(r"length\s*(===?|<=|<)\s*0|!\s*\w+\.length")
    assert pattern.search(src), (
        "session_focus.js should short-circuit when no rest timer roots present"
    )


# ───────── script loaded on session detail ─────────


def test_session_detail_loads_session_focus_js():
    src = SESSION_DETAIL.read_text(encoding="utf-8")
    assert "session_focus.js" in src
    assert "<script" in src


def test_session_focus_js_loaded_in_rendered_page(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_in_progress(db, user.id)
        session_id = session.id

    body = _render(client, session_id)
    assert "js/session_focus.js" in body


# ───────── no critical action depends on JS ─────────


def test_skip_button_is_type_button(client):
    """Skip rest must be type=button so it never submits a form."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_in_progress(db, user.id)
        session_id = session.id

    # MIGRÉ — « Skip rest » (anglais, `type="button"`, sans effet serveur)
    # devient `PASSER LE REPOS`, la commande dominante de l'état `REST`, et
    # un LIEN : soumettre marquerait « complétée » une série à peine
    # commencée, puisque `completed` dérive de la présence d'une valeur.
    # Les seuls boutons restants sont les ±15 s, toujours non critiques.
    body = _render(client, session_id, query="?rest=1")
    assert "PASSER LE REPOS" in body
    pattern = re.compile(r'<button\b[^>]*data-rest-step[^>]*>', re.IGNORECASE)
    m = pattern.search(body)
    assert m is not None, "les ajustements ±15 s ne sont pas rendus"
    assert 'type="button"' in m.group(0)


def test_rest_timer_is_outside_post_form(client):
    """Rest timer must NOT live inside the <form action=update_exercise_card>.
    This guarantees that submitting the form does not submit any timer state
    and the no-JS fallback POST is unchanged.
    """
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_in_progress(db, user.id)
        session_id = session.id

    body = _render(client, session_id)
    pattern = re.compile(
        r'<form\b[^>]*action="[^"]*/sessions/\d+/exercises/\d+"[^>]*>'
        r"(.*?)</form>",
        re.DOTALL,
    )
    forms = pattern.findall(body)
    assert forms, "no per-exercise update form found"
    for f in forms:
        assert "session-focus__rest-timer" not in f, (
            "rest timer must NOT live inside the update_exercise_card form"
        )


# ───────── no regression Sb_29.3 sticky CTA ─────────


def test_sticky_cta_still_present(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_in_progress(db, user.id)
        session_id = session.id

    # MIGRÉ — plus AUCUNE barre collante (`Sx_UIV3_02 §7.9` + Q1). Elle
    # produisait un recouvrement mesuré et n'existait que parce que la
    # commande était loin. Ce qui la remplace est vérifié ici.
    body = _render(client, session_id)
    assert "session-focus__sticky-cta" not in body
    assert "dock__cmd" in body


def test_update_exercise_card_form_action_preserved(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_in_progress(db, user.id)
        session_id = session.id

    body = _render(client, session_id)
    assert f"/sessions/{session_id}/exercises/" in body


# ───────── CSS contract ─────────


def test_css_has_rest_timer_block():
    css = APP_CSS.read_text(encoding="utf-8") + "\n" + FOCUS_CSS.read_text(encoding="utf-8")
    assert ".session-focus__rest-timer" in css
    assert ".session-focus__rest-timer__countdown" in css


# ───────── no new JS file beyond preview + session_focus ─────────


def test_no_unexpected_js_file_introduced():
    js_dir = ROOT / "app" / "static" / "js"
    existing = {p.name for p in js_dir.glob("*.js")}
    # Sb_UI_PROFILE_PREFERENCES_REDESIGN_01 — inventaire JS versionné.
    #
    # Cette assertion prouvait à l'origine que CETTE tranche n'ajoutait
    # aucun JS. Écrite comme un inventaire exact du répertoire, elle a
    # transformé une garantie historique de tranche en interdiction
    # permanente de toute amélioration progressive future — ce n'était
    # pas le contrat produit visé.
    #
    # L'inventaire JS courant de l'application est désormais versionné
    # explicitement ; `prefs_focus_rank.js` est autorisé par l'opérateur
    # au titre de AUREN_INTERACTION_REFINEMENT_01. Le caractère EXACT est
    # conservé : un quatrième fichier JS inattendu fait toujours échouer.
    assert existing == {"prefs_focus_rank.js", "preview.js", "session_focus.js"}, (
        f"unexpected JS files: {existing}"
    )


def test_no_react_or_bundle_in_page(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_in_progress(db, user.id)
        session_id = session.id

    body = _render(client, session_id).lower()
    for forbidden in (
        "react-dom",
        "vue.js",
        "/main.bundle.js",
        "esm.sh",
        "unpkg.com",
    ):
        assert forbidden not in body, f"forbidden token: {forbidden}"


# ───────── owner isolation preserved ─────────


def test_owner_isolation_unaffected(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.auth import hash_password

    with SessionLocal() as db:
        owner = db.query(User).first()
        session = _seed_in_progress(db, owner.id)
        session_id = session.id
        other = User(
            username="rest_other",
            password_hash=hash_password("rest_other_str_xyz"),  # noqa: S106
        )
        db.add(other)
        db.commit()

    client.cookies.clear()
    r = client.post(
        "/login",
        data={"username": "rest_other", "password": "rest_other_str_xyz"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    r = client.get(f"/sessions/{session_id}", follow_redirects=False)
    assert r.status_code == 404
