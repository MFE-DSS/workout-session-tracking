"""Sb_CUSTOM_PROGRAM_WIZARD_04 — HTTP tests for the non-persisted quality preview.

Uses the authenticated `client` fixture (conftest logs in `testuser`). Pins
auth, owner-scope with no existence leak, the three display states (non-scorable
era / empty prompt / scorecard), draft AND validated scorability, the editor CTA
gating, and the HARD invariant: visiting the preview writes NO
`UserProgramQualityReview`. Every `app.*` import is inside the test/helper.
"""
from __future__ import annotations

import pytest
from sqlalchemy import func, select


def _session():
    from app.database import SessionLocal

    return SessionLocal()


def _uid() -> int:
    from app.models.user import User

    with _session() as db:
        return db.execute(
            select(User.id).where(User.username == "testuser")
        ).scalar_one()


def _make_program(title: str, slug: str) -> int:
    from app.services.user_program_drafts import create_draft

    with _session() as db:
        return create_draft(db, _uid(), title, slug).id


def _make_other_program(title: str, slug: str) -> int:
    from app.models.user import User
    from app.services.auth import hash_password
    from app.services.user_program_drafts import create_draft

    with _session() as db:
        other = db.execute(
            select(User).where(User.username == "quality-other")
        ).scalar_one_or_none()
        if other is None:
            other = User(username="quality-other", password_hash=hash_password("x"))
            db.add(other)
            db.commit()
        return create_draft(db, other.id, title, slug).id


def _seed_one_session(pid: int, exercise_name: str = "Squat") -> None:
    from app.services.user_program_drafts import replace_draft_tree

    with _session() as db:
        replace_draft_tree(
            db,
            _uid(),
            pid,
            [
                {
                    "position": 1,
                    "name": "S1",
                    "exercises": [
                        {
                            "position": 1,
                            "exercise_name": exercise_name,
                            "set_scheme": "3x 8-12",
                            "rep_targets": [{"min_reps": 8, "max_reps": 12}],
                        }
                    ],
                }
            ],
        )


def _count(model) -> int:
    with _session() as db:
        return db.execute(select(func.count()).select_from(model)).scalar_one()


# ─────────────────────────── auth ───────────────────────────


def test_get_quality_unauthenticated_redirects(client):
    pid = _make_program("Auth", "q-auth")
    client.cookies.clear()
    r = client.get(f"/programs/{pid}/quality", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/login"


# ─────────────────────────── owner-scope (no leak) ───────────────────────────


def test_get_quality_foreign_program_is_404(client):
    pid = _make_other_program("Foreign", "q-foreign")
    r = client.get(f"/programs/{pid}/quality")
    assert r.status_code == 404


def test_get_quality_absent_program_is_same_404(client):
    r = client.get("/programs/999999/quality")
    assert r.status_code == 404


# ─────────────────────────── empty prompt (state #2) ─────────────────────────


def test_get_quality_empty_program_prompts_no_scorecard(client):
    pid = _make_program("Empty", "q-empty")
    r = client.get(f"/programs/{pid}/quality")
    assert r.status_code == 200
    assert "pas encore d'exercice" in r.text.lower()
    assert "grade" not in r.text.lower()
    assert "/100" not in r.text


# ─────────────────────────── scorecard (state #3) ───────────────────────────


def test_get_quality_with_exercises_shows_scorecard(client):
    pid = _make_program("Scored", "q-scored")
    _seed_one_session(pid)
    r = client.get(f"/programs/{pid}/quality")
    assert r.status_code == 200
    assert "grade" in r.text.lower()
    assert "/100" in r.text


def test_get_quality_shows_the_disclaimer(client):
    pid = _make_program("Disc", "q-disc")
    _seed_one_session(pid)
    body = client.get(f"/programs/{pid}/quality").text.lower()
    assert "indicative" in body


def test_get_quality_validated_program_shows_scorecard(client):
    from app.services.user_program_drafts import validate_draft

    pid = _make_program("Validated", "q-validated")
    _seed_one_session(pid)
    with _session() as db:
        validate_draft(db, _uid(), pid)
    r = client.get(f"/programs/{pid}/quality")
    assert r.status_code == 200
    assert "grade" in r.text.lower()


# ─────────────────────────── non-scorable eras (state #1) ────────────────────


@pytest.mark.parametrize("locked", ["published", "archived"])
def test_get_quality_locked_program_is_not_scorable(client, locked):
    from app.models.user_program import UserProgram
    from app.services.user_program_drafts import archive_draft

    pid = _make_program("Locked", f"q-locked-{locked}")
    _seed_one_session(pid)
    with _session() as db:
        if locked == "archived":
            archive_draft(db, _uid(), pid)
        else:
            db.get(UserProgram, pid).status = "published"
            db.commit()
    r = client.get(f"/programs/{pid}/quality")
    assert r.status_code == 200
    assert "ne se prévisualise pas" in r.text.lower()
    assert "grade" not in r.text.lower()


# ─────────────────────────── HARD invariant: no write ────────────────────────


def test_quality_preview_writes_no_review(client):
    from app.models.user_program import UserProgramQualityReview

    pid = _make_program("NoWrite", "q-nowrite")
    _seed_one_session(pid)
    client.get(f"/programs/{pid}/quality")
    assert _count(UserProgramQualityReview) == 0


# ─────────────────────────── editor CTA gating ───────────────────────────────


def test_editor_shows_quality_link_when_exercises(client):
    pid = _make_program("WithLink", "q-withlink")
    _seed_one_session(pid)
    body = client.get(f"/programs/{pid}").text
    assert f"/programs/{pid}/quality" in body


def test_editor_hides_quality_link_when_empty(client):
    pid = _make_program("NoLink", "q-nolink")
    body = client.get(f"/programs/{pid}").text
    assert f"/programs/{pid}/quality" not in body
