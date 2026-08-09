"""Sb_CUSTOM_PROGRAM_WIZARD_01 — HTTP tests for the custom-program creation
entry flow.

Uses the authenticated `client` fixture (conftest logs in `testuser`). Covers
auth redirects, the strict title form + trim, server-derived slug, per-user
slug collision, the reused active-program quota, owner-scope with no existence
leak, archived exclusion, and the hard NON-goals of this first build: no
quality-review write, no `WorkoutTemplate` creation.

Every `app.*` import is done INSIDE the test/helper: conftest resets the `app`
module tree when it builds the per-test DB, so a module-level import would bind
to a stale, pre-reset class.
"""
from __future__ import annotations

from urllib.parse import urlparse

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


def _make_other_user_program(*, title="Programme Autrui", slug="programme-autrui"):
    """Create a program owned by a DIFFERENT user, for cross-user isolation."""
    from app.models.user import User
    from app.services.auth import hash_password
    from app.services.user_program_drafts import create_draft

    with _session() as db:
        other = db.execute(
            select(User).where(User.username == "other")
        ).scalar_one_or_none()
        if other is None:
            other = User(username="other", password_hash=hash_password("x"))
            db.add(other)
            db.commit()
        program = create_draft(db, other.id, title, slug)
        return other.id, program.id


def _count_owned() -> int:
    from app.models.user_program import UserProgram

    with _session() as db:
        return db.execute(
            select(func.count())
            .select_from(UserProgram)
            .where(UserProgram.user_id == _uid())
        ).scalar_one()


# ─────────────────────────── auth (1-3) ───────────────────────────


def test_list_unauthenticated_redirects_to_login(client):
    client.cookies.clear()
    r = client.get("/programs", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/login"


def test_new_unauthenticated_redirects_to_login(client):
    client.cookies.clear()
    r = client.get("/programs/new", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/login"


def test_post_unauthenticated_redirects_to_login(client):
    client.cookies.clear()
    r = client.post("/programs", data={"title": "X"}, follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/login"


# ─────────────────────────── GET pages (4-5) ───────────────────────────


def test_list_authenticated_ok(client):
    r = client.get("/programs")
    assert r.status_code == 200
    assert "Mes programmes" in r.text


def test_new_authenticated_shows_title_form(client):
    r = client.get("/programs/new")
    assert r.status_code == 200
    assert 'name="title"' in r.text


# ─────────────────────────── create (6-8) ───────────────────────────


def test_post_valid_title_creates_owned_draft(client):
    from app.models.user_program import UserProgram

    r = client.post("/programs", data={"title": "Mon programme"}, follow_redirects=False)
    assert r.status_code == 303
    assert urlparse(r.headers["location"]).path.startswith("/programs/")
    with _session() as db:
        program = db.execute(
            select(UserProgram).where(UserProgram.title == "Mon programme")
        ).scalar_one()
        assert program.user_id == _uid()
        assert program.status == "draft"


def test_redirect_target_shows_created_program(client):
    r = client.post("/programs", data={"title": "Prog Detail"}, follow_redirects=False)
    path = urlparse(r.headers["location"]).path
    detail = client.get(path)
    assert detail.status_code == 200
    assert "Prog Detail" in detail.text
    # DOGFOOD_01 (F1): the lifecycle badge now shows the French label, not raw "draft".
    assert "Brouillon" in detail.text


def test_title_is_trimmed(client):
    from app.models.user_program import UserProgram

    client.post("/programs", data={"title": "  Espaces  "}, follow_redirects=False)
    with _session() as db:
        program = db.execute(
            select(UserProgram).where(UserProgram.user_id == _uid())
        ).scalar_one()
        assert program.title == "Espaces"


# ─────────────────────────── validation (9-12) ───────────────────────────


def test_blank_title_rerenders_error_no_row(client):
    r = client.post("/programs", data={"title": "   "}, follow_redirects=False)
    assert r.status_code == 200
    assert "titre" in r.text.lower()
    assert _count_owned() == 0


def test_slug_is_derived_from_title(client):
    from app.models.user_program import UserProgram

    client.post(
        "/programs", data={"title": "Mon Programme Hyper 2024 !"}, follow_redirects=False
    )
    with _session() as db:
        program = db.execute(
            select(UserProgram).where(UserProgram.user_id == _uid())
        ).scalar_one()
        assert program.slug_base == "mon-programme-hyper-2024"


def test_slug_collision_same_user_rerenders_error_no_second_row(client):
    from app.models.user_program import UserProgram

    first = client.post("/programs", data={"title": "Push A"}, follow_redirects=False)
    assert first.status_code == 303
    second = client.post("/programs", data={"title": "push a"}, follow_redirects=False)
    assert second.status_code == 200
    assert "existe" in second.text.lower() or "slug" in second.text.lower()
    with _session() as db:
        count = db.execute(
            select(func.count())
            .select_from(UserProgram)
            .where(
                UserProgram.user_id == _uid(),
                UserProgram.slug_base == "push-a",
            )
        ).scalar_one()
        assert count == 1


def test_quota_blocks_eleventh_program(client):
    from app.services.user_program_drafts import create_draft

    uid = _uid()
    with _session() as db:
        for i in range(10):
            create_draft(db, uid, f"Programme {i}", f"programme-{i}")
    r = client.post("/programs", data={"title": "Onzieme"}, follow_redirects=False)
    assert r.status_code == 200
    assert "10" in r.text  # gentle quota message names the cap
    assert _count_owned() == 10


# ─────────────────────────── owner-scope (13-16) ───────────────────────────


def test_list_is_owner_scoped(client):
    _make_other_user_program(title="Programme Autrui", slug="programme-autrui")
    r = client.get("/programs")
    assert r.status_code == 200
    assert "Programme Autrui" not in r.text


def test_detail_of_other_users_program_is_404(client):
    _other_id, pid = _make_other_user_program(slug="autre-detail")
    r = client.get(f"/programs/{pid}")
    assert r.status_code == 404


def test_detail_of_absent_program_is_same_404(client):
    r = client.get("/programs/999999")
    assert r.status_code == 404


def test_archived_program_excluded_from_list(client):
    from app.services.user_program_drafts import archive_draft, create_draft

    uid = _uid()
    with _session() as db:
        program = create_draft(db, uid, "A archiver", "a-archiver")
        archive_draft(db, uid, program.id)
    r = client.get("/programs")
    assert "A archiver" not in r.text


# ─────────────────────────── NON-goals (17-19) ───────────────────────────


def test_no_quality_review_written(client):
    from app.models.user_program import UserProgramQualityReview

    client.post("/programs", data={"title": "Sans review"}, follow_redirects=False)
    with _session() as db:
        count = db.execute(
            select(func.count()).select_from(UserProgramQualityReview)
        ).scalar_one()
        assert count == 0


def test_no_workout_template_created(client):
    from app.models.catalog import WorkoutTemplate

    with _session() as db:
        before = db.execute(
            select(func.count()).select_from(WorkoutTemplate)
        ).scalar_one()
    client.post("/programs", data={"title": "Sans template"}, follow_redirects=False)
    with _session() as db:
        after = db.execute(
            select(func.count()).select_from(WorkoutTemplate)
        ).scalar_one()
    assert after == before


def test_openapi_exposes_the_four_program_routes(client):
    spec = client.get("/openapi.json")
    assert spec.status_code == 200
    paths = spec.json()["paths"]
    assert "/programs" in paths
    assert "/programs/new" in paths
    assert "/programs/{program_id}" in paths
