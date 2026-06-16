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


def _render(client, session_id) -> str:
    r = client.get(f"/sessions/{session_id}", follow_redirects=False)
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
    assert "Repos suggéré" in body


def test_data_start_rest_attr_present(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_in_progress(db, user.id)
        session_id = session.id

    body = _render(client, session_id)
    assert "data-start-rest=" in body
    assert "data-rest-duration=" in body


def test_rest_timer_only_on_active_card(client):
    """Rest timer is included only inside the active card."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_in_progress(db, user.id, n_exercises=3)
        session_id = session.id

    body = _render(client, session_id)
    occurrences = body.count('class="session-focus__rest-timer"')
    assert occurrences == 1, (
        f"rest timer should appear exactly once (active card), got {occurrences}"
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

    body = _render(client, session_id)
    pattern = re.compile(
        r'<button\b[^>]*data-rest-skip[^>]*>',
        re.IGNORECASE,
    )
    m = pattern.search(body)
    assert m is not None, "Skip button not rendered"
    assert 'type="button"' in m.group(0), (
        "Skip button must be type='button' (non critical)"
    )


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

    body = _render(client, session_id)
    assert "session-focus__sticky-cta" in body
    assert "session-focus__cta-primary" in body


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
    assert existing == {"preview.js", "session_focus.js"}, (
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
