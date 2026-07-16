"""Sb_CUSTOM_PROGRAM_PERSISTENCE_01 — user_programs root table schema.

Pins the FIRST persistence brick of the Custom Program track
(Sx_CUSTOM_PROGRAM_04 §5): the `user_programs` root table — ownership,
minimal identity, draft status, versioning counter, timestamps, soft
delete. NO child tables, NO publication pointer, NO consumer wiring in
this build.

The table is created via `Base.metadata` at app boot (like every other
model); the Alembic migration is exercised by the migration QA scripts
(drift / snapshot / patterns / roundtrip), not re-simulated here.
"""
from __future__ import annotations

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError


def _mk_program(db, user_id: int, slug_base: str = "mon-programme", **kw):
    from app.models.user_program import UserProgram

    prog = UserProgram(
        user_id=user_id,
        title=kw.pop("title", "Mon programme"),
        slug_base=slug_base,
        **kw,
    )
    db.add(prog)
    db.commit()
    db.refresh(prog)
    return prog


def _test_user_id(db) -> int:
    from app.models.user import User

    return db.execute(select(User.id).limit(1)).scalar_one()


# ───────── existence, defaults, timestamps ─────────


def test_user_programs_table_exists_with_expected_columns(client):
    from sqlalchemy import inspect

    from app.database import engine

    inspector = inspect(engine)
    assert "user_programs" in inspector.get_table_names()
    cols = {c["name"] for c in inspector.get_columns("user_programs")}
    assert cols == {
        "id",
        "user_id",
        "title",
        "slug_base",
        "status",
        "current_version",
        "created_at",
        "updated_at",
        "archived_at",
    }


def test_defaults_draft_status_and_version_1(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        prog = _mk_program(db, _test_user_id(db))
        assert prog.status == "draft"
        assert prog.current_version == 1
        assert prog.archived_at is None


def test_timestamps_are_set_server_side(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        prog = _mk_program(db, _test_user_id(db))
        assert prog.created_at is not None
        assert prog.updated_at is not None


# ───────── ownership: NOT NULL + CASCADE ─────────


def test_user_id_is_mandatory(client):
    from app.database import SessionLocal
    from app.models.user_program import UserProgram

    with SessionLocal() as db:
        db.add(UserProgram(user_id=None, title="Sans owner", slug_base="orphelin"))
        with pytest.raises(IntegrityError):
            db.commit()


def test_deleting_user_cascades_to_programs(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.models.user_program import UserProgram
    from app.services.auth import hash_password

    with SessionLocal() as db:
        ghost = User(username="ghost-owner", password_hash=hash_password("x"))
        db.add(ghost)
        db.commit()
        _mk_program(db, ghost.id, slug_base="prog-fantome")

        db.delete(ghost)
        db.commit()

        remaining = db.execute(
            select(func.count())
            .select_from(UserProgram)
            .where(UserProgram.slug_base == "prog-fantome")
        ).scalar_one()
        assert remaining == 0


# ───────── slug_base uniqueness scoped per user ─────────


def test_slug_base_unique_per_user(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _test_user_id(db)
        _mk_program(db, uid, slug_base="doublon")
        with pytest.raises(IntegrityError):
            _mk_program(db, uid, slug_base="doublon")


def test_same_slug_base_allowed_for_different_users(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.auth import hash_password

    with SessionLocal() as db:
        uid = _test_user_id(db)
        other = User(username="other-owner", password_hash=hash_password("x"))
        db.add(other)
        db.commit()

        _mk_program(db, uid, slug_base="partage")
        prog2 = _mk_program(db, other.id, slug_base="partage")
        assert prog2.id is not None


# ───────── isolation: reads are owner-scoped by construction ─────────


def test_programs_are_isolated_per_user(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.models.user_program import UserProgram
    from app.services.auth import hash_password

    with SessionLocal() as db:
        uid = _test_user_id(db)
        other = User(username="second-owner", password_hash=hash_password("x"))
        db.add(other)
        db.commit()
        _mk_program(db, uid, slug_base="mien")
        _mk_program(db, other.id, slug_base="sien")

        mine = db.execute(
            select(UserProgram).where(UserProgram.user_id == uid)
        ).scalars().all()
        assert {p.slug_base for p in mine} == {"mien"}


# ───────── no coupling with the system catalog ─────────


def test_user_programs_has_no_fk_to_catalog(client):
    """PERSISTENCE_01 contract: zero FK toward workout_templates — the
    publication pointer is a later, separately gated build."""
    from sqlalchemy import inspect

    from app.database import engine

    fks = inspect(engine).get_foreign_keys("user_programs")
    targets = {fk["referred_table"] for fk in fks}
    assert targets == {"users"}
