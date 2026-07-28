"""Sb_CUSTOM_PROGRAM_WIZARD_02 — HTTP tests for the draft tree editor.

Uses the authenticated `client` fixture (conftest logs in `testuser`). Every
mutation route reads the current tree, applies one change and delegates to
`replace_draft_tree`; these tests pin auth, owner-scope with no existence leak,
the reused quotas (7 sessions / 10 exercises), status rules, and the hard
NON-goals (no quality review, no `WorkoutTemplate`, no scoring).

Every `app.*` import is done INSIDE the test/helper: conftest resets the `app`
module tree when it builds the per-test DB, so a module-level import would bind
to a stale, pre-reset class.
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
            select(User).where(User.username == "editor-other")
        ).scalar_one_or_none()
        if other is None:
            other = User(username="editor-other", password_hash=hash_password("x"))
            db.add(other)
            db.commit()
        return other.id, create_draft(db, other.id, title, slug).id


def _session_payload(position: int, n_exercises: int = 0) -> dict:
    return {
        "position": position,
        "name": f"S{position}",
        "exercises": [
            {
                "position": i,
                "exercise_name": f"Ex {i}",
                "set_scheme": "3x 8-12",
                "rep_targets": [{"min_reps": 8, "max_reps": 12}],
            }
            for i in range(1, n_exercises + 1)
        ],
    }


def _seed_tree(pid: int, sessions_payload: list[dict]) -> None:
    from app.services.user_program_drafts import replace_draft_tree

    with _session() as db:
        replace_draft_tree(db, _uid(), pid, sessions_payload)


def _count(model) -> int:
    with _session() as db:
        return db.execute(select(func.count()).select_from(model)).scalar_one()


def _status(pid: int) -> str:
    from app.models.user_program import UserProgram

    with _session() as db:
        return db.get(UserProgram, pid).status


# ─────────────────────────── auth (1-3) ───────────────────────────


def test_add_session_unauthenticated_redirects(client):
    pid = _make_program("Auth", "auth-s")
    client.cookies.clear()
    r = client.post(f"/programs/{pid}/sessions", data={"name": "X"}, follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/login"


def test_add_exercise_unauthenticated_redirects(client):
    pid = _make_program("Auth", "auth-e")
    client.cookies.clear()
    r = client.post(
        f"/programs/{pid}/sessions/1/exercises",
        data={"exercise_name": "X", "sets": 3, "min_reps": 8, "max_reps": 12},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert r.headers["location"] == "/login"


def test_validate_unauthenticated_redirects(client):
    pid = _make_program("Auth", "auth-v")
    client.cookies.clear()
    r = client.post(f"/programs/{pid}/validate", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/login"


# ─────────────────────────── editor render (4) ───────────────────────────


def test_get_editor_renders_empty_tree(client):
    pid = _make_program("Empty", "empty-ed")
    r = client.get(f"/programs/{pid}")
    assert r.status_code == 200
    assert "Ajouter une séance" in r.text
    assert "vide" in r.text.lower()


# ─────────────────────────── sessions (5-9) ───────────────────────────


def test_add_session_creates_position_1(client):
    from app.models.user_program import UserProgramSession

    pid = _make_program("Edit", "edit-1")
    r = client.post(f"/programs/{pid}/sessions", data={"name": "Push A"}, follow_redirects=False)
    assert r.status_code == 303
    with _session() as db:
        sessions = (
            db.execute(
                select(UserProgramSession).where(
                    UserProgramSession.user_program_id == pid
                )
            )
            .scalars()
            .all()
        )
        assert len(sessions) == 1
        assert sessions[0].position == 1
        assert sessions[0].name == "Push A"


def test_add_session_trims_name(client):
    from app.models.user_program import UserProgramSession

    pid = _make_program("Trim", "trim-s")
    client.post(f"/programs/{pid}/sessions", data={"name": "  Push A  "}, follow_redirects=False)
    with _session() as db:
        s = db.execute(select(UserProgramSession)).scalar_one()
        assert s.name == "Push A"


def test_add_session_empty_name_rerenders_no_row(client):
    from app.models.user_program import UserProgramSession

    pid = _make_program("EmptyN", "empty-n")
    r = client.post(f"/programs/{pid}/sessions", data={"name": "   "}, follow_redirects=False)
    assert r.status_code == 200
    assert "séance" in r.text.lower()
    assert _count(UserProgramSession) == 0


def test_quota_seven_sessions_blocks_eighth(client):
    from app.models.user_program import UserProgramSession

    pid = _make_program("Quota", "quota-s")
    _seed_tree(pid, [_session_payload(i) for i in range(1, 8)])
    r = client.post(f"/programs/{pid}/sessions", data={"name": "8e"}, follow_redirects=False)
    assert r.status_code == 200
    assert "7" in r.text  # gentle quota message names the cap
    assert _count(UserProgramSession) == 7


def test_delete_session_resequences(client):
    from app.models.user_program import UserProgramSession

    pid = _make_program("Del", "del-s")
    _seed_tree(pid, [_session_payload(1), _session_payload(2), _session_payload(3)])
    r = client.post(f"/programs/{pid}/sessions/2/delete", follow_redirects=False)
    assert r.status_code == 303
    with _session() as db:
        positions = [
            s.position
            for s in db.execute(
                select(UserProgramSession).order_by(UserProgramSession.position)
            )
            .scalars()
            .all()
        ]
        assert positions == [1, 2]  # was [1, 3] -> resequenced


# ─────────────────────────── exercises (10-13) ───────────────────────────


def test_add_exercise_creates_rep_targets(client):
    from app.models.user_program import UserProgramExercise, UserProgramRepTarget

    pid = _make_program("Ex", "ex-1")
    client.post(f"/programs/{pid}/sessions", data={"name": "S1"}, follow_redirects=False)
    r = client.post(
        f"/programs/{pid}/sessions/1/exercises",
        data={"exercise_name": "Squat", "sets": 3, "min_reps": 8, "max_reps": 12},
        follow_redirects=False,
    )
    assert r.status_code == 303
    with _session() as db:
        ex = db.execute(select(UserProgramExercise)).scalars().all()
        assert len(ex) == 1
        assert ex[0].exercise_name == "Squat"
        assert ex[0].set_scheme == "3x 8-12"
        assert ex[0].source_reason == "manual"
        rts = db.execute(select(UserProgramRepTarget)).scalars().all()
        assert len(rts) == 3
        assert all(rt.min_reps == 8 and rt.max_reps == 12 for rt in rts)


@pytest.mark.parametrize(
    "data",
    [
        {"exercise_name": "   ", "sets": 3, "min_reps": 8, "max_reps": 12},
        {"exercise_name": "X", "sets": 0, "min_reps": 8, "max_reps": 12},
        {"exercise_name": "X", "sets": 3, "min_reps": 0, "max_reps": 12},
        {"exercise_name": "X", "sets": 3, "min_reps": 15, "max_reps": 10},
    ],
)
def test_invalid_exercise_form_rerenders_no_row(client, data):
    from app.models.user_program import UserProgramExercise

    pid = _make_program("Inv", "inv-ex")
    client.post(f"/programs/{pid}/sessions", data={"name": "S1"}, follow_redirects=False)
    r = client.post(
        f"/programs/{pid}/sessions/1/exercises", data=data, follow_redirects=False
    )
    assert r.status_code == 200
    assert _count(UserProgramExercise) == 0


def test_quota_ten_exercises_blocks_eleventh(client):
    from app.models.user_program import UserProgramExercise

    pid = _make_program("QuotaE", "quota-e")
    _seed_tree(pid, [_session_payload(1, n_exercises=10)])
    r = client.post(
        f"/programs/{pid}/sessions/1/exercises",
        data={"exercise_name": "11e", "sets": 3, "min_reps": 8, "max_reps": 12},
        follow_redirects=False,
    )
    assert r.status_code == 200
    assert "10" in r.text
    assert _count(UserProgramExercise) == 10


def test_delete_exercise_resequences(client):
    from app.models.user_program import UserProgramExercise

    pid = _make_program("DelE", "del-e")
    _seed_tree(pid, [_session_payload(1, n_exercises=3)])
    r = client.post(
        f"/programs/{pid}/sessions/1/exercises/2/delete", follow_redirects=False
    )
    assert r.status_code == 303
    with _session() as db:
        positions = [
            e.position
            for e in db.execute(
                select(UserProgramExercise).order_by(UserProgramExercise.position)
            )
            .scalars()
            .all()
        ]
        assert positions == [1, 2]  # was [1, 3] -> resequenced


# ─────────────────────────── owner-scope (14-15) ───────────────────────────


def test_mutation_on_foreign_program_is_404(client):
    _other_id, pid = _make_other_program("Foreign", "foreign-1")
    r = client.post(f"/programs/{pid}/sessions", data={"name": "X"}, follow_redirects=False)
    assert r.status_code == 404


def test_mutation_on_absent_program_is_same_404(client):
    r = client.post("/programs/999999/sessions", data={"name": "X"}, follow_redirects=False)
    assert r.status_code == 404


# ─────────────────────────── statuses (16-19) ───────────────────────────


def test_published_program_editing_refused(client):
    from app.models.user_program import UserProgram, UserProgramSession

    pid = _make_program("Pub", "pub-lock")
    with _session() as db:
        db.get(UserProgram, pid).status = "published"
        db.commit()
    r = client.post(f"/programs/{pid}/sessions", data={"name": "X"}, follow_redirects=False)
    assert r.status_code == 200
    assert "publiée" in r.text.lower()
    assert _count(UserProgramSession) == 0


def test_archived_program_editing_refused(client):
    from app.models.user_program import UserProgramSession
    from app.services.user_program_drafts import archive_draft

    pid = _make_program("Arch", "arch-lock")
    with _session() as db:
        archive_draft(db, _uid(), pid)
    r = client.post(f"/programs/{pid}/sessions", data={"name": "X"}, follow_redirects=False)
    assert r.status_code == 200
    assert "archiv" in r.text.lower()
    assert _count(UserProgramSession) == 0


def test_editing_validated_program_flips_back_to_draft(client):
    pid = _make_program("Val", "val-flip")
    _seed_tree(pid, [_session_payload(1, n_exercises=1)])
    client.post(f"/programs/{pid}/validate", follow_redirects=False)
    assert _status(pid) == "validated"
    client.post(f"/programs/{pid}/sessions", data={"name": "S2"}, follow_redirects=False)
    assert _status(pid) == "draft"


def test_validate_complete_draft_becomes_validated(client):
    pid = _make_program("VOk", "v-ok")
    _seed_tree(pid, [_session_payload(1, n_exercises=1)])
    r = client.post(f"/programs/{pid}/validate", follow_redirects=False)
    assert r.status_code == 303
    assert _status(pid) == "validated"


def test_validate_empty_draft_soft_error(client):
    pid = _make_program("VEmpty", "v-empty")
    r = client.post(f"/programs/{pid}/validate", follow_redirects=False)
    assert r.status_code == 200
    assert "séance" in r.text.lower()
    assert _status(pid) == "draft"


# ─────────────────────────── NON-goals (20-23) ───────────────────────────


def test_no_quality_review_written(client):
    from app.models.user_program import UserProgramQualityReview

    pid = _make_program("NoRev", "no-rev")
    client.post(f"/programs/{pid}/sessions", data={"name": "S1"}, follow_redirects=False)
    client.post(
        f"/programs/{pid}/sessions/1/exercises",
        data={"exercise_name": "Squat", "sets": 3, "min_reps": 8, "max_reps": 12},
        follow_redirects=False,
    )
    client.post(f"/programs/{pid}/validate", follow_redirects=False)
    assert _count(UserProgramQualityReview) == 0


def test_no_workout_template_created(client):
    from app.models.catalog import WorkoutTemplate

    before = _count(WorkoutTemplate)
    pid = _make_program("NoTpl", "no-tpl")
    client.post(f"/programs/{pid}/sessions", data={"name": "S1"}, follow_redirects=False)
    client.post(
        f"/programs/{pid}/sessions/1/exercises",
        data={"exercise_name": "Squat", "sets": 3, "min_reps": 8, "max_reps": 12},
        follow_redirects=False,
    )
    assert _count(WorkoutTemplate) == before


def test_editor_shows_no_scoring(client):
    pid = _make_program("NoScore", "no-score")
    _seed_tree(pid, [_session_payload(1, n_exercises=1)])
    client.post(f"/programs/{pid}/validate", follow_redirects=False)
    body = client.get(f"/programs/{pid}").text.lower()
    assert "grade" not in body
    assert "/100" not in body


def test_wizard01_routes_still_green(client):
    assert client.get("/programs").status_code == 200
    assert client.get("/programs/new").status_code == 200
    r = client.post("/programs", data={"title": "Non-regression"}, follow_redirects=False)
    assert r.status_code == 303
