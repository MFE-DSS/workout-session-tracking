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


# ───────── Sb_CUSTOM_PROGRAM_WIZARD_06 — controlled regeneration (16-26) ─────────
#
# The hard refusal became an explicit confirmation. What must not change is that an
# UNCONFIRMED post never touches the tree — the previous behaviour protected manual
# work by refusing outright, and the new one has to protect it just as well while
# offering a way through.


def _exercise_count(pid: int) -> int:
    from app.models.user_program import UserProgramExercise, UserProgramSession

    with _session() as db:
        return db.execute(
            select(func.count())
            .select_from(UserProgramExercise)
            .join(UserProgramSession)
            .where(UserProgramSession.user_program_id == pid)
        ).scalar_one()


def _status(pid: int) -> str:
    from app.models.user_program import UserProgram

    with _session() as db:
        return db.get(UserProgram, pid).status


def _first_session_name(pid: int) -> str:
    from app.models.user_program import UserProgramSession

    with _session() as db:
        return db.execute(
            select(UserProgramSession.name)
            .where(UserProgramSession.user_program_id == pid)
            .order_by(UserProgramSession.position)
            .limit(1)
        ).scalar_one()


def test_empty_program_generation_is_unchanged_by_wizard06(client):
    """The existing path keeps working without any confirmation: an empty program has
    nothing to lose, so asking for consent would be ceremony."""
    pid = _make_program("Still Empty", "gen06-empty")
    r = client.post(
        f"/programs/{pid}/generate",
        data={"split": "ppl", "sessions": 3},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert _session_count(pid) == 3


def test_nonempty_without_confirm_leaves_the_tree_untouched(client):
    """A soft 200, and — the part that matters — the same tree afterwards."""
    pid = _make_program("Guard", "gen06-guard")
    _seed_one_session(pid)
    before = _first_session_name(pid)
    r = client.post(
        f"/programs/{pid}/generate",
        data={"split": "ppl", "sessions": 3},
        follow_redirects=False,
    )
    assert r.status_code == 200
    assert _session_count(pid) == 1
    assert _exercise_count(pid) == 1
    assert _first_session_name(pid) == before


def test_nonempty_with_confirm_replaces_the_tree(client):
    pid = _make_program("Replace", "gen06-replace")
    _seed_one_session(pid)
    assert _session_count(pid) == 1
    r = client.post(
        f"/programs/{pid}/generate",
        data={"split": "ppl", "sessions": 3, "confirm_replace": "true"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert _session_count(pid) == 3
    # The seeded session is gone, not merely joined by new ones.
    assert _first_session_name(pid) != "S1"


def test_validated_program_regenerates_and_reopens_as_draft(client):
    """Regenerating a validated program reopens it: the validation attested to content
    that no longer exists, so keeping the badge would be a false claim."""
    from app.services.user_program_drafts import validate_draft

    pid = _make_program("Validated", "gen06-validated")
    _seed_one_session(pid)
    with _session() as db:
        validate_draft(db, _uid(), pid)
    assert _status(pid) == "validated"

    r = client.post(
        f"/programs/{pid}/generate",
        data={"split": "ppl", "sessions": 3, "confirm_replace": "true"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert _status(pid) == "draft"
    assert _session_count(pid) == 3


@pytest.mark.parametrize("locked", ["published", "archived"])
def test_locked_program_refuses_even_with_confirmation(client, locked):
    """Confirmation is consent to lose the tree, never authority over the lifecycle.

    The existing service owns that refusal; the checkbox must not become a way past it.
    """
    from app.models.user_program import UserProgram
    from app.services.user_program_drafts import archive_draft

    pid = _make_program("Locked06", f"gen06-locked-{locked}")
    _seed_one_session(pid)
    with _session() as db:
        if locked == "archived":
            archive_draft(db, _uid(), pid)
        else:
            db.get(UserProgram, pid).status = "published"
            db.commit()

    r = client.post(
        f"/programs/{pid}/generate",
        data={"split": "ppl", "sessions": 3, "confirm_replace": "true"},
        follow_redirects=False,
    )
    assert r.status_code == 200
    assert _session_count(pid) == 1  # untouched
    assert _exercise_count(pid) == 1


def test_get_generate_on_nonempty_shows_the_warning_and_the_checkbox(client):
    pid = _make_program("Warn", "gen06-warn")
    _seed_one_session(pid)
    r = client.get(f"/programs/{pid}/generate")
    assert r.status_code == 200
    assert 'name="confirm_replace"' in r.text
    assert "remplacera" in r.text.lower()


def test_get_generate_summarises_sessions_exercises_and_sets(client):
    """The three numbers are the consent: "this will overwrite your program" is not."""
    pid = _make_program("Summary", "gen06-summary")
    _seed_one_session(pid)  # 1 session, 1 exercise, 1 rep target
    r = client.get(f"/programs/{pid}/generate")
    assert r.status_code == 200
    body = r.text.lower()
    assert "séance" in body
    assert "exercice" in body
    assert "série" in body
    assert "<strong>1</strong>" in r.text


def test_empty_program_shows_no_confirmation_checkbox(client):
    pid = _make_program("NoBox", "gen06-nobox")
    r = client.get(f"/programs/{pid}/generate")
    assert r.status_code == 200
    assert 'name="confirm_replace"' not in r.text


def test_regeneration_on_foreign_program_is_404(client):
    """Owner-scope is not relaxed by the confirmation."""
    _other_id, pid = _make_other_program("Foreign06", "gen06-foreign")
    r = client.post(
        f"/programs/{pid}/generate",
        data={"split": "ppl", "sessions": 3, "confirm_replace": "true"},
        follow_redirects=False,
    )
    assert r.status_code == 404


def test_regeneration_on_absent_program_is_the_same_404(client):
    """Indistinct from the foreign case: a 404 that differed would leak existence."""
    r = client.post(
        "/programs/999998/generate",
        data={"split": "ppl", "sessions": 3, "confirm_replace": "true"},
        follow_redirects=False,
    )
    assert r.status_code == 404


def test_regeneration_writes_no_quality_review_and_no_workout_template(client):
    """The WIZARD_03 non-goals survive regeneration."""
    from app.models.catalog import WorkoutTemplate
    from app.models.user_program import UserProgramQualityReview

    pid = _make_program("NonGoals06", "gen06-nongoals")
    _seed_one_session(pid)
    reviews_before = _count(UserProgramQualityReview)
    templates_before = _count(WorkoutTemplate)

    r = client.post(
        f"/programs/{pid}/generate",
        data={"split": "ppl", "sessions": 3, "confirm_replace": "true"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert _count(UserProgramQualityReview) == reviews_before
    assert _count(WorkoutTemplate) == templates_before


@pytest.mark.parametrize(
    "value", ["", "false", "False", "0", "off", "no", "maybe", "TRUE-ish"]
)
def test_unaccepted_confirmation_values_never_replace_the_tree(client, value):
    """Consent is parsed SERVER-side, and anything not explicitly true fails closed.

    Browser checkbox behaviour proves nothing here: a direct POST can carry any string.
    A malformed value is a 422 rather than a silent pass — either way the tree survives.
    """
    pid = _make_program("Bypass", f"gen06-bypass-{abs(hash(value))}")
    _seed_one_session(pid)
    r = client.post(
        f"/programs/{pid}/generate",
        data={"split": "ppl", "sessions": 3, "confirm_replace": value},
        follow_redirects=False,
    )
    assert r.status_code in (200, 422)
    assert _session_count(pid) == 1
    assert _exercise_count(pid) == 1


def test_a_duplicated_confirmation_field_cannot_smuggle_consent(client):
    """`false` then `true` in the same body is refused outright, not resolved to the last."""
    pid = _make_program("Dup", "gen06-dup")
    _seed_one_session(pid)
    r = client.post(
        f"/programs/{pid}/generate",
        data=[
            ("split", "ppl"),
            ("sessions", "3"),
            ("confirm_replace", "false"),
            ("confirm_replace", "true"),
        ],
        follow_redirects=False,
    )
    assert r.status_code == 422
    assert _session_count(pid) == 1


def test_the_unconfirmed_page_is_not_presented_as_an_error(client):
    """An unconfirmed replacement is a step not yet taken, not a mistake made.

    The message must therefore not be rendered in the danger colour reserved for real
    errors (unknown split, out-of-range session count).
    """
    pid = _make_program("Tone", "gen06-tone")
    _seed_one_session(pid)
    r = client.post(
        f"/programs/{pid}/generate",
        data={"split": "ppl", "sessions": 3},
        follow_redirects=False,
    )
    assert r.status_code == 200
    assert "Cochez la confirmation" in r.text
    assert "color:var(--danger)\">Ce programme contient déjà" not in r.text


def test_a_real_error_is_still_rendered_as_an_error(client):
    """The danger styling is not removed — it is reserved for actual input errors."""
    pid = _make_program("RealErr", "gen06-realerr")
    r = client.post(
        f"/programs/{pid}/generate",
        data={"split": "bro-split", "sessions": 3},
        follow_redirects=False,
    )
    assert r.status_code == 200
    assert "color:var(--danger)" in r.text
    assert _session_count(pid) == 0


def test_the_unconfirmed_page_can_be_resubmitted_with_confirmation(client):
    """The returned form carries everything a confirmed retry needs — no re-navigation."""
    pid = _make_program("Retry", "gen06-retry")
    _seed_one_session(pid)
    first = client.post(
        f"/programs/{pid}/generate",
        data={"split": "ppl", "sessions": 3},
        follow_redirects=False,
    )
    assert first.status_code == 200
    assert 'name="split"' in first.text
    assert 'name="sessions"' in first.text
    assert 'name="confirm_replace"' in first.text

    second = client.post(
        f"/programs/{pid}/generate",
        data={"split": "ppl", "sessions": 3, "confirm_replace": "true"},
        follow_redirects=False,
    )
    assert second.status_code == 303
    assert _session_count(pid) == 3


def test_the_summary_survives_sessions_and_exercises_with_no_children(client):
    """Counts are derived, so an empty collection must render 0 rather than break."""
    from app.services.user_program_drafts import replace_draft_tree

    pid = _make_program("Sparse", "gen06-sparse")
    with _session() as db:
        replace_draft_tree(
            db,
            _uid(),
            pid,
            [
                {"position": 1, "name": "Sans exercice", "exercises": []},
                {
                    "position": 2,
                    "name": "Sans série",
                    "exercises": [
                        {
                            "position": 1,
                            "exercise_name": "Squat",
                            "set_scheme": "3x8",
                            "rep_targets": [],
                        }
                    ],
                },
            ],
        )
    r = client.get(f"/programs/{pid}/generate")
    assert r.status_code == 200
    assert "<strong>2</strong>" in r.text  # 2 séances
    assert "<strong>0</strong>" in r.text  # 0 séries
