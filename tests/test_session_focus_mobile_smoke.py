"""Sb_29.5 — Sx_29 mobile smoke tests (structural, no real browser).

Consolidates structural assertions across Sb_29.1 → Sb_29.4 to give a
single smoke-test surface that can be re-run cheaply when refactoring
the focus mode surface.

Scope :
- GET /sessions/{id} still 200
- session_focus.css is loaded on session_detail
- session_focus.js is loaded on session_detail
- sticky header / sticky jump / active card / sticky CTA / rest timer
  all rendered together
- no horizontal scroll markers (overflow-x:scroll on key wrappers,
  flex-wrap present on rest timer wrapper)
- session_focus.css present and non-empty
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_CSS = ROOT / "app" / "static" / "css" / "app.css"
FOCUS_CSS = ROOT / "app" / "static" / "css" / "session_focus.css"
SESSION_DETAIL = ROOT / "app" / "templates" / "session_detail.html"


def _seed_session(db, user_id, n_exercises=3):
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    s = WorkoutSession(
        user_id=user_id,
        template_slug_snapshot="mobile-smoke",
        template_name_snapshot="Mobile smoke test",
        started_at=datetime.now(UTC),
        status="in_progress",
    )
    for i in range(n_exercises):
        se = SessionExercise(
            exercise_code_snapshot=f"M{i + 1}",
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


# ───────── extraction guard ─────────


def test_session_focus_css_exists_and_nonempty():
    assert FOCUS_CSS.exists(), "session_focus.css missing after Sb_29.5 extraction"
    body = FOCUS_CSS.read_text(encoding="utf-8")
    assert len(body) > 1000, "session_focus.css unexpectedly small"
    # All four Sx_29 blocks must have been moved over.
    for marker in ("Sb_29.1", "Sb_29.2", "Sb_29.3", "Sb_29.4"):
        assert marker in body, f"{marker} block missing in session_focus.css"


def test_app_css_no_longer_contains_sx29_blocks():
    """The Sb_29.1 → Sb_29.4 block headers must be GONE from app.css."""
    body = APP_CSS.read_text(encoding="utf-8")
    for marker in (
        "Sb_29.1 — Mobile Session Focus Mode",
        "Sb_29.2 — Active Exercise Navigation",
        "Sb_29.3 — Sticky CTA",
        "Sb_29.4 — Rest timer",
    ):
        assert marker not in body, (
            f"residual Sx_29 block in app.css after extraction: {marker}"
        )


def test_session_detail_loads_session_focus_css():
    src = SESSION_DETAIL.read_text(encoding="utf-8")
    assert "session_focus.css" in src


def test_session_focus_css_link_in_rendered_page(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_session(db, user.id)
        session_id = session.id

    body = _render(client, session_id)
    assert "css/session_focus.css" in body
    # app.css still loaded too (cascade order)
    assert "css/app.css" in body
    # app.css link comes BEFORE session_focus.css link in the rendered head
    assert body.index("css/app.css") < body.index("css/session_focus.css"), (
        "session_focus.css must load AFTER app.css to preserve cascade"
    )


# ───────── all surfaces rendered together ─────────


def test_all_sx29_surfaces_rendered(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_session(db, user.id, n_exercises=3)
        session_id = session.id

    body = _render(client, session_id)
    # Sticky header (Sb_29.1)
    assert "session-focus__sticky-header" in body
    # Sticky jump bar (Sb_29.1/2)
    assert "session-focus__sticky-jump" in body
    # Active card (Sb_29.1/2)
    assert "session-focus__card--active" in body
    # Sticky CTA (Sb_29.3)
    assert "session-focus__sticky-cta" in body
    # Rest timer (Sb_29.4)
    assert "session-focus__rest-timer" in body
    # session_focus.js progressive enhancement
    assert "js/session_focus.js" in body


def test_route_still_200_completed_session(client):
    """Smoke : a completed session still renders 200 with the new CSS link."""
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = WorkoutSession(
            user_id=user.id,
            template_slug_snapshot="smoke-completed",
            template_name_snapshot="Smoke completed",
            started_at=datetime.now(UTC),
            ended_at=datetime.now(UTC),
            status="completed",
        )
        se = SessionExercise(
            exercise_code_snapshot="DONE",
            exercise_name_snapshot="Done",
            position=1,
        )
        se.set_logs.append(
            SetLog(kind="work", set_index=1, weight_kg=60.0, reps=10, completed=True)
        )
        s.session_exercises.append(se)
        db.add(s)
        db.commit()
        db.refresh(s)
        session_id = s.id

    # Completed sessions may redirect to /sessions/{id}/done — follow it.
    r = client.get(f"/sessions/{session_id}", follow_redirects=True)
    assert r.status_code == 200


# ───────── no horizontal scroll markers ─────────


def _css() -> str:
    return APP_CSS.read_text(encoding="utf-8") + "\n" + FOCUS_CSS.read_text(
        encoding="utf-8"
    )


def test_rest_timer_uses_flex_wrap():
    """Rest timer wrapper must wrap items to avoid 360x640 horizontal scroll."""
    css = _css()
    # find the .session-focus__rest-timer block and look for flex-wrap: wrap
    import re

    pattern = re.compile(
        r"\.session-focus__rest-timer\s*\{[^}]*flex-wrap:\s*wrap",
        re.DOTALL,
    )
    assert pattern.search(css), "rest timer should set flex-wrap: wrap"


def test_no_overflow_x_scroll_introduced_in_session_focus_css():
    """Sx_29 CSS must not introduce overflow-x:scroll on session focus wrappers."""
    body = FOCUS_CSS.read_text(encoding="utf-8")
    # Naive scan: no explicit overflow-x:scroll on session-focus rules.
    assert "overflow-x: scroll" not in body
    assert "overflow-x:scroll" not in body
