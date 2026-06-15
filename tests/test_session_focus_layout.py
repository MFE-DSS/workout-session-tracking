"""Sb_29.1 — Mobile Session Focus Visual Skeleton tests.

Verifies:
* GET /sessions/{id} renders successfully for the authenticated owner
* The new partials (session_focus_header, exercise_card) are inlined
* The Sx_29 hook classes are present on the rendered HTML
* The 6 UI state classes (pending/active/partial/done/skipped/
  substituted) exist in the rendered CSS bundle (app.css)
* The existing POST forms are still wired (update_exercise_card,
  update_session)
* The anchors #exercise-{id} are preserved
* The jump_states semantics are honored (active card carries the active
  hook class)
* No React / SPA framework / JS bundle is introduced
* The tap-target hook class is applied on the action buttons

These tests don't depend on real-time behavior — they assert on rendered
HTML / CSS file content.
"""
from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_CSS = ROOT / "app" / "static" / "css" / "app.css"
SESSION_DETAIL = ROOT / "app" / "templates" / "session_detail.html"
PARTIALS = ROOT / "app" / "templates" / "_partials"


def _create_in_progress_session(db, user_id, template_slug="test-tpl"):
    """Seed a minimal in-progress session with one exercise and one set."""
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    s = WorkoutSession(
        user_id=user_id,
        template_slug_snapshot=template_slug,
        template_name_snapshot="Test Template",
        started_at=datetime.now(UTC),
        status="in_progress",
    )
    se = SessionExercise(
        exercise_code_snapshot="E1",
        exercise_name_snapshot="Bench Press",
        position=1,
    )
    se.set_logs.append(
        SetLog(kind="work", set_index=1, weight_kg=80.0, reps=8, completed=False)
    )
    s.session_exercises.append(se)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


# ───────── partials extracted ─────────


def test_partials_exist():
    """Both new partials must exist on disk."""
    assert (PARTIALS / "session_focus_header.html").exists()
    assert (PARTIALS / "exercise_card.html").exists()


def test_session_detail_includes_partials():
    """session_detail.html must reference both partials via Jinja include."""
    src = SESSION_DETAIL.read_text(encoding="utf-8")
    assert '"_partials/session_focus_header.html"' in src
    assert '"_partials/exercise_card.html"' in src


def test_session_detail_no_inline_form_kept():
    """The big per-exercise <form> block has been moved into the partial —
    the parent template should NOT contain the inline action of
    update_exercise_card anymore (only via the include)."""
    src = SESSION_DETAIL.read_text(encoding="utf-8")
    # The parent should not embed the per-card form anymore
    assert src.count("update_exercise_card") == 0
    # update_session (session-level feedback) remains in the parent
    assert "update_session" in src


# ───────── route still 200 ─────────


def test_session_detail_route_renders(client):
    """GET /sessions/{id} must return 200 for the owner of an in-progress session."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _create_in_progress_session(db, user.id)
        session_id = session.id

    r = client.get(f"/sessions/{session_id}", follow_redirects=False)
    assert r.status_code == 200, r.text[:500]


# ───────── hook classes ─────────


def test_focus_wrapper_class_present(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _create_in_progress_session(db, user.id)
        session_id = session.id

    body = client.get(f"/sessions/{session_id}").text
    assert "session-focus" in body


def test_focus_header_hook_present(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _create_in_progress_session(db, user.id)
        session_id = session.id

    body = client.get(f"/sessions/{session_id}").text
    assert "session-focus__header" in body
    assert "session-focus__sticky-header" in body


def test_focus_jump_bar_hook_present(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _create_in_progress_session(db, user.id)
        session_id = session.id

    body = client.get(f"/sessions/{session_id}").text
    assert "session-focus__jump" in body
    assert "session-focus__sticky-jump" in body


def test_at_least_one_exercise_card_rendered(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _create_in_progress_session(db, user.id)
        session_id = session.id

    body = client.get(f"/sessions/{session_id}").text
    # legacy class
    assert "exercise-card" in body
    # Sx_29 hook
    assert "session-focus__card" in body
    # anchor preserved
    assert "id=\"exercise-" in body


def test_active_card_carries_active_class(client):
    """The first exercise of an in-progress session should be active."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _create_in_progress_session(db, user.id)
        session_id = session.id

    body = client.get(f"/sessions/{session_id}").text
    assert "session-focus__card--active" in body


def test_tap_target_class_applied_on_action_buttons(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _create_in_progress_session(db, user.id)
        session_id = session.id

    body = client.get(f"/sessions/{session_id}").text
    assert "session-focus__tap-target" in body


# ───────── POST forms preserved ─────────


def test_exercise_card_form_action_preserved(client):
    """The per-card POST form (now in the partial) must still target
    update_exercise_card with the same name + value semantics."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _create_in_progress_session(db, user.id)
        session_id = session.id

    body = client.get(f"/sessions/{session_id}").text
    # form action present
    assert f"/sessions/{session_id}/exercises/" in body
    # weight + reps inputs present
    assert 'name="set_' in body
    assert "_weight_kg" in body
    assert "_reps" in body
    # nav prev/next buttons present
    assert 'name="nav"' in body
    assert 'value="next"' in body


def test_session_level_form_action_preserved(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _create_in_progress_session(db, user.id)
        session_id = session.id

    body = client.get(f"/sessions/{session_id}").text
    assert f"/sessions/{session_id}" in body
    # session-level form still has its own anchor
    assert 'id="session-feedback"' in body
    # session-level CTA still rendered
    assert "Terminer la séance" in body or "Rouvrir" in body


# ───────── CSS classes present in stylesheet ─────────


def _css() -> str:
    return APP_CSS.read_text(encoding="utf-8")


def test_css_contains_focus_wrapper():
    assert ".session-focus" in _css()


def test_css_contains_header_hooks():
    css = _css()
    assert ".session-focus__header" in css
    assert ".session-focus__sticky-header" in css


def test_css_contains_jump_hooks():
    css = _css()
    assert ".session-focus__jump" in css
    assert ".session-focus__sticky-jump" in css


def test_css_contains_all_six_state_classes():
    css = _css()
    for state in ("pending", "active", "partial", "done", "skipped", "substituted"):
        assert f".session-focus__card--{state}" in css, (
            f"missing state class: {state}"
        )


def test_css_contains_tap_target_class():
    css = _css()
    assert ".session-focus__tap-target" in css
    # Minimum 44x44 expected for WCAG 2.5.5
    assert "min-height: 44px" in css or "min-height:44px" in css
    assert "min-width: 44px" in css or "min-width:44px" in css


# ───────── No React / SPA / bundle introduced ─────────


def test_no_react_or_bundle_introduced(client):
    """The rendered HTML must not load React, Vue, Angular, a bundler
    output, or any external framework JS bundle. JS files must be
    served locally from /static/js/* only (no CDN external import)."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _create_in_progress_session(db, user.id)
        session_id = session.id

    body = client.get(f"/sessions/{session_id}").text.lower()
    for forbidden in (
        "react",
        "react-dom",
        "vue.js",
        "angular",
        "/main.bundle.js",
        "esm.sh",
        "unpkg.com",
        "cdnjs.cloudflare.com/ajax/libs/react",
    ):
        assert forbidden not in body, f"forbidden token in rendered HTML: {forbidden}"


def test_no_new_js_file_introduced():
    """Sb_29.1 must not introduce any new JS file. session_focus.js
    is explicitly reserved for Sb_29.4 (rest timer)."""
    js_dir = ROOT / "app" / "static" / "js"
    existing = {p.name for p in js_dir.glob("*.js")}
    # Before Sb_29.1 the only JS was preview.js. Sb_29.1 must not add
    # session_focus.js (that's Sb_29.4) or any other file.
    assert existing == {"preview.js"}, (
        f"unexpected JS files in app/static/js/: {existing}"
    )


# ───────── anchors and jump_states semantics ─────────


def test_anchors_for_each_exercise(client):
    """Each session_exercise must have an id=exercise-{id} anchor and a
    corresponding jump bar item linking to it."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _create_in_progress_session(db, user.id)
        session_id = session.id
        # we created exactly one exercise; capture its id
        first_se_id = session.session_exercises[0].id

    body = client.get(f"/sessions/{session_id}").text
    # anchor target
    assert f'id="exercise-{first_se_id}"' in body
    # jump bar href to that anchor
    assert f'href="#exercise-{first_se_id}"' in body


def test_owner_isolation_unaffected(client):
    """Sanity: the session_detail route still 404s for non-owners.

    Sb_26.7 hard contract — the focus mode refactor must not weaken
    the cross-user isolation that has been in place since Sx_26.
    """
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.auth import hash_password

    with SessionLocal() as db:
        # current user owns this session
        owner = db.query(User).first()
        session = _create_in_progress_session(db, owner.id)
        session_id = session.id
        # create a different user
        other = User(
            username="other_owner",
            password_hash=hash_password("pwd_other_str_x"),  # noqa: S106
        )
        db.add(other)
        db.commit()
        db.refresh(other)

    # log in as the other user
    client.cookies.clear()
    r = client.post(
        "/login",
        data={"username": "other_owner", "password": "pwd_other_str_x"},
        follow_redirects=False,
    )
    assert r.status_code == 303

    # /sessions/{owner_session} → 404 for non-owner
    r = client.get(f"/sessions/{session_id}", follow_redirects=False)
    assert r.status_code == 404
