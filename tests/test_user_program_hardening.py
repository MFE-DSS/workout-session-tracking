"""Sb_CUSTOM_PROGRAM_PERSISTENCE_05 — QA/quotas hardening.

Pins the hardening layer over the draft CRUD service (spec 04 §6/§9,
spec 03 §9-C): V1 quotas with gentle messages, the draft → validated
completeness transition, and application-level immutability of frozen
quality-review traces. Still no endpoint, no wizard, no scoring, no
publication — those stay gated.
"""
from __future__ import annotations

import pytest
from sqlalchemy import select


def _uid(db) -> int:
    from app.models.user import User

    return db.execute(select(User.id).limit(1)).scalar_one()


def _other_uid(db) -> int:
    from app.models.user import User
    from app.services.auth import hash_password

    other = db.execute(
        select(User).where(User.username == "hardening-other")
    ).scalar_one_or_none()
    if other is None:
        other = User(username="hardening-other", password_hash=hash_password("x"))
        db.add(other)
        db.commit()
    return other.id


def _session_payload(position: int, n_exercises: int = 1) -> dict:
    return {
        "position": position,
        "name": f"Séance {position}",
        "exercises": [
            {
                "position": i,
                "exercise_name": f"Exercice {i}",
                "set_scheme": "3x 8-12",
                "rep_targets": [{"min_reps": 8, "max_reps": 12}],
            }
            for i in range(1, n_exercises + 1)
        ],
    }


def _tree_payload(n_sessions: int = 1, n_exercises: int = 1) -> list[dict]:
    return [_session_payload(i, n_exercises) for i in range(1, n_sessions + 1)]


# ───────── quota : programmes actifs ─────────


def test_create_draft_allows_up_to_max_active(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import (
        MAX_ACTIVE_PROGRAMS,
        create_draft,
        list_drafts,
    )

    with SessionLocal() as db:
        uid = _uid(db)
        for i in range(MAX_ACTIVE_PROGRAMS):
            create_draft(db, uid, f"Programme {i}", f"quota-{i}")
        assert len(list_drafts(db, uid)) == MAX_ACTIVE_PROGRAMS


def test_create_draft_over_quota_gentle_refusal(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import (
        MAX_ACTIVE_PROGRAMS,
        UserProgramDraftError,
        create_draft,
    )

    with SessionLocal() as db:
        uid = _uid(db)
        for i in range(MAX_ACTIVE_PROGRAMS):
            create_draft(db, uid, f"Programme {i}", f"plein-{i}")
        with pytest.raises(UserProgramDraftError, match="archiver") as exc:
            create_draft(db, uid, "Un de trop", "plein-extra")
        # message doux et actionnable, jamais culpabilisant
        assert "libère une place" in str(exc.value)


def test_archiving_frees_a_quota_slot(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import (
        MAX_ACTIVE_PROGRAMS,
        archive_draft,
        create_draft,
    )

    with SessionLocal() as db:
        uid = _uid(db)
        first = create_draft(db, uid, "Programme 0", "libere-0")
        for i in range(1, MAX_ACTIVE_PROGRAMS):
            create_draft(db, uid, f"Programme {i}", f"libere-{i}")
        archive_draft(db, uid, first.id)
        # l'archivé ne compte plus : une place s'est libérée
        prog = create_draft(db, uid, "Le suivant", "libere-next")
        assert prog.id is not None


def test_quota_is_per_user(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import MAX_ACTIVE_PROGRAMS, create_draft

    with SessionLocal() as db:
        uid = _uid(db)
        for i in range(MAX_ACTIVE_PROGRAMS):
            create_draft(db, uid, f"Programme {i}", f"peruser-{i}")
        # le quota d'un user ne bloque pas les autres
        prog = create_draft(db, _other_uid(db), "Autre user", "peruser-autre")
        assert prog.id is not None


# ───────── quotas : arbre (séances / exercices) ─────────


def test_replace_tree_respects_session_quota_boundary(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import (
        MAX_SESSIONS_PER_PROGRAM,
        UserProgramDraftError,
        create_draft,
        replace_draft_tree,
    )

    with SessionLocal() as db:
        uid = _uid(db)
        prog = create_draft(db, uid, "Semaine", "semaine")
        ok = replace_draft_tree(
            db, uid, prog.id, _tree_payload(MAX_SESSIONS_PER_PROGRAM)
        )
        assert len(ok.sessions) == MAX_SESSIONS_PER_PROGRAM
        with pytest.raises(UserProgramDraftError, match="séances"):
            replace_draft_tree(
                db, uid, prog.id, _tree_payload(MAX_SESSIONS_PER_PROGRAM + 1)
            )


def test_replace_tree_respects_exercise_quota_boundary(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import (
        MAX_EXERCISES_PER_SESSION,
        UserProgramDraftError,
        create_draft,
        replace_draft_tree,
    )

    with SessionLocal() as db:
        uid = _uid(db)
        prog = create_draft(db, uid, "Dense", "dense")
        ok = replace_draft_tree(
            db,
            uid,
            prog.id,
            _tree_payload(1, n_exercises=MAX_EXERCISES_PER_SESSION),
        )
        assert len(ok.sessions[0].exercises) == MAX_EXERCISES_PER_SESSION
        with pytest.raises(UserProgramDraftError, match="exercices"):
            replace_draft_tree(
                db,
                uid,
                prog.id,
                _tree_payload(1, n_exercises=MAX_EXERCISES_PER_SESSION + 1),
            )


# ───────── validate_draft : transition draft → validated ─────────


def test_validate_complete_draft_transitions_to_validated(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import (
        create_draft,
        replace_draft_tree,
        validate_draft,
    )

    with SessionLocal() as db:
        uid = _uid(db)
        prog = create_draft(db, uid, "Complet", "complet")
        replace_draft_tree(db, uid, prog.id, _tree_payload(2))
        validated = validate_draft(db, uid, prog.id)
        assert validated.status == "validated"


def test_validate_refuses_empty_program(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import (
        UserProgramDraftError,
        create_draft,
        validate_draft,
    )

    with SessionLocal() as db:
        uid = _uid(db)
        prog = create_draft(db, uid, "Vide", "vide")
        with pytest.raises(UserProgramDraftError, match="au moins une séance"):
            validate_draft(db, uid, prog.id)


def test_validate_refuses_session_without_exercises(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import (
        UserProgramDraftError,
        create_draft,
        replace_draft_tree,
        validate_draft,
    )

    with SessionLocal() as db:
        uid = _uid(db)
        prog = create_draft(db, uid, "Creux", "creux")
        payload = _tree_payload(1) + [
            {"position": 2, "name": "Séance vide", "exercises": []}
        ]
        replace_draft_tree(db, uid, prog.id, payload)
        with pytest.raises(UserProgramDraftError, match="Séance vide"):
            validate_draft(db, uid, prog.id)


def test_validate_refuses_exercise_without_rep_targets(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import (
        UserProgramDraftError,
        create_draft,
        replace_draft_tree,
        validate_draft,
    )

    with SessionLocal() as db:
        uid = _uid(db)
        prog = create_draft(db, uid, "Sans plage", "sans-plage")
        payload = _tree_payload(1)
        payload[0]["exercises"][0]["rep_targets"] = []
        replace_draft_tree(db, uid, prog.id, payload)
        with pytest.raises(UserProgramDraftError, match="répétitions"):
            validate_draft(db, uid, prog.id)


def test_validate_is_idempotent_and_locked_states_refused(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import (
        UserProgramDraftError,
        archive_draft,
        create_draft,
        replace_draft_tree,
        validate_draft,
    )

    with SessionLocal() as db:
        uid = _uid(db)
        prog = create_draft(db, uid, "Stable", "stable")
        replace_draft_tree(db, uid, prog.id, _tree_payload(1))
        validate_draft(db, uid, prog.id)
        again = validate_draft(db, uid, prog.id)  # idempotent
        assert again.status == "validated"

        pub = create_draft(db, uid, "Publié", "valide-pub")
        pub.status = "published"
        db.commit()
        with pytest.raises(UserProgramDraftError, match="publiée"):
            validate_draft(db, uid, pub.id)

        arch = create_draft(db, uid, "Archivé", "valide-arch")
        archive_draft(db, uid, arch.id)
        with pytest.raises(UserProgramDraftError, match="archivé"):
            validate_draft(db, uid, arch.id)


def test_validate_cross_user_indistinguishable_from_missing(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import (
        UserProgramDraftError,
        create_draft,
        replace_draft_tree,
        validate_draft,
    )

    with SessionLocal() as db:
        uid = _uid(db)
        prog = create_draft(db, uid, "Mien", "valide-cross")
        replace_draft_tree(db, uid, prog.id, _tree_payload(1))
        with pytest.raises(UserProgramDraftError, match="introuvable"):
            validate_draft(db, _other_uid(db), prog.id)


# ───────── invariance des quality reviews ─────────


def test_quality_review_rows_are_immutable_in_place(client):
    from app.database import SessionLocal
    from app.models.user_program import UserProgramQualityReview
    from app.services.user_program_drafts import create_draft

    with SessionLocal() as db:
        uid = _uid(db)
        prog = create_draft(db, uid, "Tracé", "trace-gel")
        review = UserProgramQualityReview(
            user_program_id=prog.id, version=1, grade="B", scoring_version=1
        )
        db.add(review)
        db.commit()  # l'INSERT d'une trace gelée reste permis
        review_id = review.id

        review.grade = "A"
        with pytest.raises(ValueError, match="immuable"):
            db.commit()
        db.rollback()

    with SessionLocal() as db:
        kept = db.get(UserProgramQualityReview, review_id)
        assert kept is not None
        assert kept.grade == "B"  # la trace gelée n'a pas bougé
