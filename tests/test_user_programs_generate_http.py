"""Sb_CUSTOM_PROGRAM_WIZARD_03 — HTTP tests for deterministic generation.

Uses the authenticated `client` fixture (conftest logs in `testuser`). Pins
auth, owner-scope with no existence leak, generate-only-if-empty, status
refusal, and the hard NON-goals (no quality review, no `WorkoutTemplate`, no
scoring). Every `app.*` import is inside the test/helper (conftest resets the
`app` module tree per test).
"""
from __future__ import annotations

import pytest
from sqlalchemy import func, select

# ─────────────────────────── helpers ───────────────────────────


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


def _make_other_program(title: str, slug: str) -> tuple[int, int]:
    from app.models.user import User
    from app.services.auth import hash_password
    from app.services.user_program_drafts import create_draft

    with _session() as db:
        other = db.execute(
            select(User).where(User.username == "gen-other")
        ).scalar_one_or_none()
        if other is None:
            other = User(username="gen-other", password_hash=hash_password("x"))
            db.add(other)
            db.commit()
        return other.id, create_draft(db, other.id, title, slug).id


def _seed_one_session(pid: int) -> None:
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
                            "exercise_name": "Squat",
                            "set_scheme": "3x 8-12",
                            "rep_targets": [{"min_reps": 8, "max_reps": 12}],
                        }
                    ],
                }
            ],
        )


def _session_count(pid: int) -> int:
    from app.models.user_program import UserProgramSession

    with _session() as db:
        return db.execute(
            select(func.count())
            .select_from(UserProgramSession)
            .where(UserProgramSession.user_program_id == pid)
        ).scalar_one()


def _count(model) -> int:
    with _session() as db:
        return db.execute(select(func.count()).select_from(model)).scalar_one()


# ─────────────────────────── auth (1-3) ───────────────────────────


def test_get_generate_unauthenticated_redirects(client):
    pid = _make_program("Auth", "gen-auth-g")
    client.cookies.clear()
    r = client.get(f"/programs/{pid}/generate", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/login"


def test_post_generate_unauthenticated_redirects(client):
    pid = _make_program("Auth", "gen-auth-p")
    client.cookies.clear()
    r = client.post(
        f"/programs/{pid}/generate",
        data={"split": "ppl", "sessions": 3},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert r.headers["location"] == "/login"


def test_get_generate_authenticated_empty_ok(client):
    pid = _make_program("Empty", "gen-empty")
    r = client.get(f"/programs/{pid}/generate")
    assert r.status_code == 200
    assert 'name="split"' in r.text


# ─────────────────────────── generation (4-8) ───────────────────────────


def test_generate_ppl_three_creates_tree(client):
    from app.models.user_program import UserProgramExercise

    pid = _make_program("PPL", "gen-ppl")
    r = client.post(
        f"/programs/{pid}/generate",
        data={"split": "ppl", "sessions": 3},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert _session_count(pid) == 3
    assert _count(UserProgramExercise) > 0


def test_generate_upper_lower_creates_tree(client):
    pid = _make_program("UL", "gen-ul")
    r = client.post(
        f"/programs/{pid}/generate",
        data={"split": "upper_lower", "sessions": 2},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert _session_count(pid) == 2


def test_generate_on_nonempty_program_refused(client):
    pid = _make_program("NonEmpty", "gen-ne")
    _seed_one_session(pid)
    r = client.post(
        f"/programs/{pid}/generate",
        data={"split": "ppl", "sessions": 3},
        follow_redirects=False,
    )
    assert r.status_code == 200
    assert "déjà" in r.text.lower()
    assert _session_count(pid) == 1  # unchanged


def test_generate_invalid_split_rerenders_no_creation(client):
    pid = _make_program("BadSplit", "gen-badsplit")
    r = client.post(
        f"/programs/{pid}/generate",
        data={"split": "bro-split", "sessions": 3},
        follow_redirects=False,
    )
    assert r.status_code == 200
    assert _session_count(pid) == 0


def test_generate_invalid_sessions_rerenders_no_creation(client):
    pid = _make_program("BadSessions", "gen-badsessions")
    r = client.post(
        f"/programs/{pid}/generate",
        data={"split": "ppl", "sessions": 0},
        follow_redirects=False,
    )
    assert r.status_code == 200
    assert _session_count(pid) == 0


# ─────────────────────────── owner-scope + status (9-11) ─────────────────────


def test_generate_on_foreign_program_is_404(client):
    _other_id, pid = _make_other_program("Foreign", "gen-foreign")
    r = client.post(
        f"/programs/{pid}/generate",
        data={"split": "ppl", "sessions": 3},
        follow_redirects=False,
    )
    assert r.status_code == 404


def test_generate_on_absent_program_is_same_404(client):
    r = client.post(
        "/programs/999999/generate",
        data={"split": "ppl", "sessions": 3},
        follow_redirects=False,
    )
    assert r.status_code == 404


@pytest.mark.parametrize("locked", ["published", "archived"])
def test_generate_on_locked_program_refused(client, locked):
    from app.models.user_program import UserProgram
    from app.services.user_program_drafts import archive_draft

    pid = _make_program("Locked", f"gen-locked-{locked}")
    with _session() as db:
        if locked == "archived":
            archive_draft(db, _uid(), pid)
        else:
            db.get(UserProgram, pid).status = "published"
            db.commit()
    r = client.post(
        f"/programs/{pid}/generate",
        data={"split": "ppl", "sessions": 3},
        follow_redirects=False,
    )
    assert r.status_code == 200
    assert _session_count(pid) == 0


# ─────────────────────────── NON-goals (12-15) ───────────────────────────


def test_no_quality_review_written(client):
    from app.models.user_program import UserProgramQualityReview

    pid = _make_program("NoRev", "gen-norev")
    client.post(
        f"/programs/{pid}/generate",
        data={"split": "ppl", "sessions": 3},
        follow_redirects=False,
    )
    assert _count(UserProgramQualityReview) == 0


def test_no_workout_template_created(client):
    from app.models.catalog import WorkoutTemplate

    before = _count(WorkoutTemplate)
    pid = _make_program("NoTpl", "gen-notpl")
    client.post(
        f"/programs/{pid}/generate",
        data={"split": "ppl", "sessions": 3},
        follow_redirects=False,
    )
    assert _count(WorkoutTemplate) == before


def test_generated_editor_shows_no_scoring(client):
    pid = _make_program("NoScore", "gen-noscore")
    client.post(
        f"/programs/{pid}/generate",
        data={"split": "ppl", "sessions": 3},
        follow_redirects=False,
    )
    body = client.get(f"/programs/{pid}").text.lower()
    assert "grade" not in body
    assert "/100" not in body


def test_wizard01_02_routes_still_green(client):
    assert client.get("/programs").status_code == 200
    assert client.get("/programs/new").status_code == 200
    pid = _make_program("NonReg", "gen-nonreg")
    assert client.get(f"/programs/{pid}").status_code == 200
    r = client.post(
        f"/programs/{pid}/sessions", data={"name": "S1"}, follow_redirects=False
    )
    assert r.status_code == 303
