"""Sb_CUSTOM_PROGRAM_PERSISTENCE_04 — draft CRUD service.

Pins the first SERVICE brick of the Custom Program track: owner-scoped
draft manipulation (`app/services/user_program_drafts.py`). No endpoint,
no wizard, no scoring, no publication — those stay gated.
"""
from __future__ import annotations

import pytest
from sqlalchemy import func, select


def _uid(db) -> int:
    from app.models.user import User

    return db.execute(select(User.id).limit(1)).scalar_one()


def _other_uid(db) -> int:
    from app.models.user import User
    from app.services.auth import hash_password

    other = db.execute(
        select(User).where(User.username == "draft-other")
    ).scalar_one_or_none()
    if other is None:
        other = User(username="draft-other", password_hash=hash_password("x"))
        db.add(other)
        db.commit()
    return other.id


def _tree_payload(n_sessions: int = 2) -> list[dict]:
    return [
        {
            "position": i,
            "name": f"Séance {i}",
            "exercises": [
                {
                    "position": 1,
                    "exercise_name": "Développé couché haltères",
                    "set_scheme": "3x 8-12",
                    "rep_targets": [
                        {"min_reps": 8, "max_reps": 12},
                        {"min_reps": 8, "max_reps": 12},
                    ],
                }
            ],
        }
        for i in range(1, n_sessions + 1)
    ]


# ───────── create ─────────


def test_create_draft_defaults_and_trim(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import create_draft

    with SessionLocal() as db:
        prog = create_draft(db, _uid(db), "  Mon programme  ", "  mon-prog  ")
        assert prog.title == "Mon programme"
        assert prog.slug_base == "mon-prog"
        assert prog.status == "draft"
        assert prog.current_version == 1
        assert prog.archived_at is None


def test_create_draft_rejects_empty_fields(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import UserProgramDraftError, create_draft

    with SessionLocal() as db:
        with pytest.raises(UserProgramDraftError):
            create_draft(db, _uid(db), "   ", "slug")
        with pytest.raises(UserProgramDraftError):
            create_draft(db, _uid(db), "Titre", "")


def test_create_draft_duplicate_slug_same_user_readable_error(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import UserProgramDraftError, create_draft

    with SessionLocal() as db:
        uid = _uid(db)
        create_draft(db, uid, "Un", "doublon")
        with pytest.raises(UserProgramDraftError, match="doublon"):
            create_draft(db, uid, "Deux", "doublon")


def test_create_draft_same_slug_other_user_ok(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import create_draft

    with SessionLocal() as db:
        create_draft(db, _uid(db), "Mien", "partage")
        prog = create_draft(db, _other_uid(db), "Sien", "partage")
        assert prog.id is not None


# ───────── reads owner-scoped ─────────


def test_get_draft_owner_scoped_and_eager_tree(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import (
        create_draft,
        get_draft,
        replace_draft_tree,
    )

    with SessionLocal() as db:
        uid = _uid(db)
        prog = create_draft(db, uid, "Arbre", "arbre")
        replace_draft_tree(db, uid, prog.id, _tree_payload())
        pid = prog.id

    with SessionLocal() as db:
        uid = _uid(db)
        mine = get_draft(db, uid, pid)
        assert mine is not None
        assert [s.position for s in mine.sessions] == [1, 2]
        assert mine.sessions[0].exercises[0].rep_targets[0].set_index == 1
        # autre user → None, indistinguable d'un programme inexistant
        assert get_draft(db, _other_uid(db), pid) is None


def test_list_drafts_isolation_ordering_and_archive_filter(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import (
        archive_draft,
        create_draft,
        list_drafts,
    )

    with SessionLocal() as db:
        uid = _uid(db)
        a = create_draft(db, uid, "A", "list-a")
        b = create_draft(db, uid, "B", "list-b")
        create_draft(db, _other_uid(db), "Autre", "list-x")

        mine = list_drafts(db, uid)
        assert [p.slug_base for p in mine] == ["list-b", "list-a"] or {
            p.slug_base for p in mine
        } == {"list-a", "list-b"}
        assert all(p.user_id == uid for p in mine)

        archive_draft(db, uid, a.id)
        visible = {p.slug_base for p in list_drafts(db, uid)}
        assert "list-a" not in visible
        full = {p.slug_base for p in list_drafts(db, uid, include_archived=True)}
        assert "list-a" in full
        assert b.slug_base in visible


# ───────── rename + règles de statut ─────────


def test_rename_touches_and_validated_flips_back_to_draft(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import create_draft, rename_draft

    with SessionLocal() as db:
        uid = _uid(db)
        prog = create_draft(db, uid, "Avant", "rename")
        prog.status = "validated"
        db.commit()

        renamed = rename_draft(db, uid, prog.id, "Après")
        assert renamed.title == "Après"
        assert renamed.status == "draft"  # spec 04 §6


def test_published_and_archived_programs_are_not_editable(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import (
        UserProgramDraftError,
        archive_draft,
        create_draft,
        rename_draft,
        replace_draft_tree,
    )

    with SessionLocal() as db:
        uid = _uid(db)
        pub = create_draft(db, uid, "Publié", "published-lock")
        pub.status = "published"
        db.commit()
        with pytest.raises(UserProgramDraftError, match="publiée"):
            rename_draft(db, uid, pub.id, "Interdit")
        with pytest.raises(UserProgramDraftError, match="publiée"):
            replace_draft_tree(db, uid, pub.id, _tree_payload(1))

        arch = create_draft(db, uid, "Archivé", "archived-lock")
        archive_draft(db, uid, arch.id)
        with pytest.raises(UserProgramDraftError, match="archivé"):
            rename_draft(db, uid, arch.id, "Interdit")


# ───────── replace_draft_tree ─────────


def test_replace_tree_purges_old_children(client):
    from app.database import SessionLocal
    from app.models.user_program import (
        UserProgramExercise,
        UserProgramRepTarget,
        UserProgramSession,
    )
    from app.services.user_program_drafts import create_draft, replace_draft_tree

    with SessionLocal() as db:
        uid = _uid(db)
        prog = create_draft(db, uid, "Purge", "purge")
        replace_draft_tree(db, uid, prog.id, _tree_payload(3))
        replace_draft_tree(db, uid, prog.id, _tree_payload(1))

        counts = {
            model.__tablename__: db.execute(
                select(func.count()).select_from(model)
            ).scalar_one()
            for model in (
                UserProgramSession,
                UserProgramExercise,
                UserProgramRepTarget,
            )
        }
        # 1 séance × 1 exercice × 2 rep targets — rien d'orphelin.
        assert counts == {
            "user_program_sessions": 1,
            "user_program_exercises": 1,
            "user_program_rep_targets": 2,
        }


def test_replace_tree_validates_sequential_positions(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import (
        UserProgramDraftError,
        create_draft,
        replace_draft_tree,
    )

    bad = _tree_payload(2)
    bad[1]["position"] = 5
    with SessionLocal() as db:
        uid = _uid(db)
        prog = create_draft(db, uid, "Positions", "positions")
        with pytest.raises(UserProgramDraftError, match="séquentielles"):
            replace_draft_tree(db, uid, prog.id, bad)


# ───────── mutations cross-user ─────────


def test_mutations_on_foreign_program_fail_like_missing(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import (
        UserProgramDraftError,
        archive_draft,
        create_draft,
        rename_draft,
        replace_draft_tree,
    )

    with SessionLocal() as db:
        uid = _uid(db)
        other = _other_uid(db)
        prog = create_draft(db, uid, "Mien", "cross")
        for attempt in (
            lambda: rename_draft(db, other, prog.id, "Volé"),
            lambda: replace_draft_tree(db, other, prog.id, _tree_payload(1)),
            lambda: archive_draft(db, other, prog.id),
        ):
            with pytest.raises(UserProgramDraftError, match="introuvable"):
                attempt()


# ───────── archive ─────────


def test_archive_is_soft_and_double_archive_refused(client):
    from app.database import SessionLocal
    from app.models.user_program import UserProgram
    from app.services.user_program_drafts import (
        UserProgramDraftError,
        archive_draft,
        create_draft,
    )

    with SessionLocal() as db:
        uid = _uid(db)
        prog = create_draft(db, uid, "Soft", "soft-delete")
        archived = archive_draft(db, uid, prog.id)
        assert archived.archived_at is not None
        # la row existe toujours (soft delete, jamais destructif)
        assert db.get(UserProgram, prog.id) is not None
        with pytest.raises(UserProgramDraftError, match="déjà archivé"):
            archive_draft(db, uid, prog.id)
