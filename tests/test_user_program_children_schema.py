"""Sb_CUSTOM_PROGRAM_PERSISTENCE_02 — user program child tables schema.

Pins the second persistence brick of the Custom Program track
(Sx_CUSTOM_PROGRAM_04 §5): the ownership tree
user_programs → user_program_sessions → user_program_exercises →
user_program_rep_targets — cascades, per-parent uniqueness, defaults,
ordering, and ZERO foreign key toward the system catalog or the EKB.
No consumer wiring (CRUD = PERSISTENCE_04).
"""
from __future__ import annotations

import pytest
from sqlalchemy import func, inspect, select
from sqlalchemy.exc import IntegrityError

_CHILD_TABLES = (
    "user_program_sessions",
    "user_program_exercises",
    "user_program_rep_targets",
)


def _mk_tree(db, user_id: int, slug_base: str = "arbre"):
    """Program → 2 sessions → exercises → rep targets, via the ORM tree."""
    from app.models.user_program import (
        UserProgram,
        UserProgramExercise,
        UserProgramRepTarget,
        UserProgramSession,
    )

    prog = UserProgram(user_id=user_id, title="Arbre", slug_base=slug_base)
    s1 = UserProgramSession(position=1, name="Push A")
    s2 = UserProgramSession(position=2, name="Pull A")
    e1 = UserProgramExercise(
        position=1, exercise_name="Développé couché haltères", set_scheme="3x 8-12"
    )
    e1.rep_targets.append(UserProgramRepTarget(set_index=1, min_reps=8, max_reps=12))
    e1.rep_targets.append(UserProgramRepTarget(set_index=2, min_reps=8, max_reps=12))
    s1.exercises.append(e1)
    prog.sessions.extend([s2, s1])  # insertion désordonnée exprès (test d'ordre)
    db.add(prog)
    db.commit()
    db.refresh(prog)
    return prog


def _uid(db) -> int:
    from app.models.user import User

    return db.execute(select(User.id).limit(1)).scalar_one()


# ───────── 1-2. existence + colonnes ─────────


def test_child_tables_exist(client):
    from app.database import engine

    names = set(inspect(engine).get_table_names())
    assert set(_CHILD_TABLES) <= names


def test_child_tables_have_expected_columns(client):
    from app.database import engine

    inspector = inspect(engine)
    cols = {t: {c["name"] for c in inspector.get_columns(t)} for t in _CHILD_TABLES}
    assert cols["user_program_sessions"] == {
        "id", "user_program_id", "position", "name", "kind", "focus",
        "duration_target_minutes", "notes",
        # PUBLICATION_01 (spec 05 §6) — the session→published-template link.
        "published_template_id", "template_slug_snapshot",
    }
    assert cols["user_program_exercises"] == {
        "id", "user_program_session_id", "position", "exercise_name",
        "variant_key", "variant_group", "equipment_family", "movement_pattern",
        "set_scheme", "notes", "source_reason",
    }
    assert cols["user_program_rep_targets"] == {
        "id", "user_program_exercise_id", "set_index", "min_reps", "max_reps",
        "technique", "is_warmup",
    }


# ───────── 3. cascade en chaîne ─────────


def test_deleting_program_cascades_through_whole_tree(client):
    from app.database import SessionLocal
    from app.models.user_program import (
        UserProgramExercise,
        UserProgramRepTarget,
        UserProgramSession,
    )

    with SessionLocal() as db:
        prog = _mk_tree(db, _uid(db), slug_base="cascade")
        db.delete(prog)
        db.commit()
        for model in (UserProgramSession, UserProgramExercise, UserProgramRepTarget):
            count = db.execute(select(func.count()).select_from(model)).scalar_one()
            assert count == 0, f"{model.__tablename__} non purgée par la cascade"


# ───────── 4-6. uniques par parent ─────────


def test_session_position_unique_per_program(client):
    from app.database import SessionLocal
    from app.models.user_program import UserProgramSession

    with SessionLocal() as db:
        prog = _mk_tree(db, _uid(db), slug_base="uniq-session")
        db.add(
            UserProgramSession(user_program_id=prog.id, position=1, name="Doublon")
        )
        with pytest.raises(IntegrityError):
            db.commit()


def test_exercise_position_unique_per_session(client):
    from app.database import SessionLocal
    from app.models.user_program import UserProgramExercise

    with SessionLocal() as db:
        prog = _mk_tree(db, _uid(db), slug_base="uniq-exercise")
        session_id = prog.sessions[0].exercises[0].user_program_session_id
        db.add(
            UserProgramExercise(
                user_program_session_id=session_id,
                position=1,
                exercise_name="Doublon",
                set_scheme="3x 8-12",
            )
        )
        with pytest.raises(IntegrityError):
            db.commit()


def test_rep_target_set_index_unique_per_exercise(client):
    from app.database import SessionLocal
    from app.models.user_program import UserProgramRepTarget

    with SessionLocal() as db:
        prog = _mk_tree(db, _uid(db), slug_base="uniq-target")
        exercise_id = prog.sessions[0].exercises[0].rep_targets[0].user_program_exercise_id
        db.add(
            UserProgramRepTarget(
                user_program_exercise_id=exercise_id,
                set_index=1,
                min_reps=6,
                max_reps=10,
            )
        )
        with pytest.raises(IntegrityError):
            db.commit()


# ───────── 7. defaults ─────────


def test_defaults_kind_strength_and_is_warmup_false(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        prog = _mk_tree(db, _uid(db), slug_base="defaults")
        session = prog.sessions[0]
        target = session.exercises[0].rep_targets[0]
        assert session.kind == "strength"
        assert session.focus == ""
        assert target.is_warmup is False
        assert target.technique is None


# ───────── 8. zéro FK catalogue/EKB ─────────


def test_child_tables_have_no_fk_to_catalog_or_ekb(client):
    """PERSISTENCE contract: the tree only references itself and (at the root)
    users — never the EKB. The SOLE sanctioned catalog reference is the
    PUBLICATION_01 publication link `user_program_sessions.published_template_id`
    → workout_templates (spec 05 §6, ON DELETE SET NULL); nothing else may reach
    the catalog."""
    from app.database import engine

    inspector = inspect(engine)
    allowed = {"user_programs", "user_program_sessions", "user_program_exercises"}
    for table in _CHILD_TABLES:
        for fk in inspector.get_foreign_keys(table):
            referred = fk["referred_table"]
            if referred in allowed:
                continue
            # The one whitelisted catalog reference: the publication link.
            assert table == "user_program_sessions", (
                f"{table} référence hors arbre: {referred}"
            )
            assert referred == "workout_templates"
            assert fk["constrained_columns"] == ["published_template_id"]


# ───────── 9. ordre relationnel ─────────


def test_relationships_ordered_by_position_and_set_index(client):
    from app.database import SessionLocal
    from app.models.user_program import UserProgram

    with SessionLocal() as db:
        prog_id = _mk_tree(db, _uid(db), slug_base="ordre").id

    with SessionLocal() as db:  # session neuve → ordre garanti par order_by
        prog = db.get(UserProgram, prog_id)
        assert [s.position for s in prog.sessions] == [1, 2]
        targets = prog.sessions[0].exercises[0].rep_targets
        assert [t.set_index for t in targets] == [1, 2]


# ───────── 10. non-régression ownership racine ─────────


def test_root_ownership_isolation_still_holds(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.models.user_program import UserProgram
    from app.services.auth import hash_password

    with SessionLocal() as db:
        uid = _uid(db)
        other = User(username="tree-other", password_hash=hash_password("x"))
        db.add(other)
        db.commit()
        _mk_tree(db, uid, slug_base="mien")
        _mk_tree(db, other.id, slug_base="sien")
        mine = db.execute(
            select(UserProgram).where(UserProgram.user_id == uid)
        ).scalars().all()
        assert {p.slug_base for p in mine} == {"mien"}
