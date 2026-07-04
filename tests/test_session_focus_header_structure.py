"""Sb_UI_04.2 — Session Focus header structure tests.

Verifies the Auren-refactored header structure:
- required Jinja wrappers present (session-focus__header-main,
  session-focus__header-title-row, session-focus__header-kicker,
  session-focus__header-meta, session-focus__header-progress)
- title still rendered inside .page-title
- badge status still rendered with .badge--{status}
- back link "← Accueil" is now inside the header (not floating outside)
- progression value is wrapped in .session-focus__header-progress-value
- no duplicate back link outside the header

Non-brittle : reads rendered HTML only, no pixel assertions.
"""
from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _seed(db, user_id):
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    s = WorkoutSession(
        user_id=user_id,
        template_slug_snapshot="test-hdr",
        template_name_snapshot="Header Structure Test",
        started_at=datetime.now(UTC),
        status="in_progress",
    )
    se = SessionExercise(
        exercise_code_snapshot="E1",
        exercise_name_snapshot="Test Exo",
        position=1,
    )
    se.set_logs.append(
        SetLog(kind="work", set_index=1, weight_kg=None, reps=None, completed=False)
    )
    s.session_exercises.append(se)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def _render(client, session_id: int) -> str:
    r = client.get(f"/sessions/{session_id}")
    assert r.status_code == 200, r.text[:200]
    return r.text


class TestHeaderStructure:
    def test_header_main_wrapper_present(self, client):
        from app.database import SessionLocal
        from app.models.user import User

        with SessionLocal() as db:
            user = db.query(User).first()
            s = _seed(db, user.id)
            body = _render(client, s.id)

        assert 'session-focus__header-main' in body

    def test_title_row_wrapper_present(self, client):
        from app.database import SessionLocal
        from app.models.user import User

        with SessionLocal() as db:
            user = db.query(User).first()
            s = _seed(db, user.id)
            body = _render(client, s.id)

        assert 'session-focus__header-title-row' in body

    def test_kicker_wrapper_present(self, client):
        from app.database import SessionLocal
        from app.models.user import User

        with SessionLocal() as db:
            user = db.query(User).first()
            s = _seed(db, user.id)
            body = _render(client, s.id)

        assert 'session-focus__header-kicker' in body

    def test_meta_wrapper_present(self, client):
        from app.database import SessionLocal
        from app.models.user import User

        with SessionLocal() as db:
            user = db.query(User).first()
            s = _seed(db, user.id)
            body = _render(client, s.id)

        assert 'session-focus__header-meta' in body

    def test_progress_value_present(self, client):
        from app.database import SessionLocal
        from app.models.user import User

        with SessionLocal() as db:
            user = db.query(User).first()
            s = _seed(db, user.id)
            body = _render(client, s.id)

        assert 'session-focus__header-progress-value' in body

    def test_page_title_class_preserved(self, client):
        """Legacy .page-title class must remain for cascade compat."""
        from app.database import SessionLocal
        from app.models.user import User

        with SessionLocal() as db:
            user = db.query(User).first()
            s = _seed(db, user.id)
            body = _render(client, s.id)

        assert 'class="page-title"' in body

    def test_badge_status_preserved(self, client):
        """badge / badge--{status} must remain."""
        from app.database import SessionLocal
        from app.models.user import User

        with SessionLocal() as db:
            user = db.query(User).first()
            s = _seed(db, user.id)
            body = _render(client, s.id)

        # in_progress status seeded
        assert 'badge--in_progress' in body

    def test_back_link_inside_header(self, client):
        """After Sb_UI_04.2 the back link is inside the session focus header,
        not floating outside. We target the session-focus__header specifically
        (the global topbar also uses <header>). """
        from app.database import SessionLocal
        from app.models.user import User

        with SessionLocal() as db:
            user = db.query(User).first()
            s = _seed(db, user.id)
            body = _render(client, s.id)

        # Locate the session focus header specifically.
        marker = 'session-focus__header'
        header_start = body.find(f'<header class="session-header {marker}')
        assert header_start != -1, (
            "no <header class=\"session-header session-focus__header ...\"> found"
        )
        header_end = body.find('</header>', header_start)
        assert header_end != -1, "no </header> closing tag for session focus header"
        header_html = body[header_start:header_end]
        assert 'class="back"' in header_html, (
            "back link must be inside the session focus header (Sb_UI_04.2 : back link "
            "moved from session_detail.html to session_focus_header.html)"
        )

    def test_no_duplicate_back_link_outside_header(self, client):
        """Only one back link in the whole session detail page."""
        from app.database import SessionLocal
        from app.models.user import User

        with SessionLocal() as db:
            user = db.query(User).first()
            s = _seed(db, user.id)
            body = _render(client, s.id)

        # count occurrences of the exact opening tag `<a class="back"`
        occurrences = len(re.findall(r'<a\s+class="back"', body))
        assert occurrences == 1, (
            f"expected exactly one back link, got {occurrences} — Sb_UI_04.2 "
            "requires the back link to live only inside session_focus_header.html"
        )

    def test_progression_value_is_mono_wrapped(self, client):
        """Progress value must be wrapped in the mono-styled span, not raw text."""
        from app.database import SessionLocal
        from app.models.user import User

        with SessionLocal() as db:
            user = db.query(User).first()
            s = _seed(db, user.id)
            body = _render(client, s.id)

        # e.g. <span class="session-focus__header-progress-value">0 / 1</span>
        pattern = re.compile(
            r'<span[^>]*\bsession-focus__header-progress-value\b[^>]*>\s*\d+\s*/\s*\d+\s*</span>'
        )
        assert pattern.search(body), (
            "progression value must be wrapped in .session-focus__header-progress-value"
        )


class TestJumpBarAriaCurrent:
    def test_no_aria_current_false_leftover(self, client):
        """Sb_UI_04.2 removed aria-current="false" ; only active carries."""
        from app.database import SessionLocal
        from app.models.user import User

        with SessionLocal() as db:
            user = db.query(User).first()
            s = _seed(db, user.id)
            body = _render(client, s.id)

        assert 'aria-current="false"' not in body

    def test_no_aria_current_step_leftover(self, client):
        """Sb_UI_04.2 replaced "step" by "location"."""
        from app.database import SessionLocal
        from app.models.user import User

        with SessionLocal() as db:
            user = db.query(User).first()
            s = _seed(db, user.id)
            body = _render(client, s.id)

        assert 'aria-current="step"' not in body

    def test_active_item_carries_aria_current_location(self, client):
        from app.database import SessionLocal
        from app.models.user import User

        with SessionLocal() as db:
            user = db.query(User).first()
            s = _seed(db, user.id)
            body = _render(client, s.id)

        assert 'aria-current="location"' in body
