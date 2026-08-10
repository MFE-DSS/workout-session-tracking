"""Sb_CUSTOM_PROGRAM_SCORING_03 — persistance des traces de scoring.

Pins l'écriture INSERT-ONLY d'une trace figée dans
`user_program_quality_reviews` : mapping exact des 13 champs (dont les 3
colonnes runtime ajoutées par la migration `o6p1j7k8m09`), idempotence douce,
immutabilité, owner-scope sans fuite d'existence, statuts scorables, et
l'adaptateur ORM → payload pur.
"""
from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest
from sqlalchemy import func, inspect, select

from app.services.program_quality_reviews import (
    SCORABLE_STATUSES,
    QualityReviewError,
    compute_and_store_quality_review,
    get_quality_review,
    program_to_quality_definition,
)


def _uid(db) -> int:
    from app.models.user import User

    return db.execute(select(User.id).limit(1)).scalar_one()


def _other_uid(db) -> int:
    from app.models.user import User
    from app.services.auth import hash_password

    other = db.execute(
        select(User).where(User.username == "review-other")
    ).scalar_one_or_none()
    if other is None:
        other = User(username="review-other", password_hash=hash_password("x"))
        db.add(other)
        db.commit()
    return other.id


def _known_exercises(limit: int) -> list[str]:
    """Noms réellement présents dans l'EKB (zone + pattern connus)."""
    from app.services.program_quality_engine import ExerciseKnowledgeBase

    ekb = ExerciseKnowledgeBase.load()
    usable = [
        name
        for name, entry in ekb.entries.items()
        if entry.get("zone_primary") and entry.get("movement_pattern")
    ]
    return usable[:limit]


def _tree(names: list[str], warmups: int = 0) -> list[dict]:
    return [
        {
            "position": 1,
            "name": "Séance 1",
            "exercises": [
                {
                    "position": i + 1,
                    "exercise_name": name,
                    "set_scheme": "3x 8-12",
                    "rep_targets": (
                        [{"min_reps": 8, "max_reps": 12} for _ in range(3)]
                        + [
                            {"min_reps": 12, "max_reps": 15, "is_warmup": True}
                            for _ in range(warmups)
                        ]
                    ),
                }
                for i, name in enumerate(names)
            ],
        }
    ]


def _make_program(db, uid, slug, names=None, warmups=0):
    from app.services.user_program_drafts import create_draft, replace_draft_tree

    program = create_draft(db, uid, f"Programme {slug}", slug)
    replace_draft_tree(db, uid, program.id, _tree(names or _known_exercises(3), warmups))
    db.refresh(program)
    return program


# ───────── migration / schéma ─────────


def test_migration_added_the_three_runtime_columns(client):
    from app.database import engine

    columns = {c["name"] for c in inspect(engine).get_columns("user_program_quality_reviews")}
    assert {"confidence", "coverage_ratio", "grade_cap_reason"} <= columns


def test_snapshot_contains_the_new_columns():
    from pathlib import Path

    snapshot = Path(__file__).resolve().parent.parent / "data" / "schema_snapshot.sql"
    text = snapshot.read_text(encoding="utf-8")
    assert "confidence VARCHAR(16)" in text
    assert "coverage_ratio FLOAT" in text
    assert "grade_cap_reason TEXT" in text


# ───────── écriture nominale + mapping ─────────


def test_writes_a_review_and_maps_every_field(client):
    from app.database import SessionLocal
    from app.services.program_quality_engine import score_program

    with SessionLocal() as db:
        uid = _uid(db)
        program = _make_program(db, uid, "map")
        stored = compute_and_store_quality_review(db, uid, program.id)

        assert stored.created is True
        review = stored.review
        expected = score_program(program_to_quality_definition(program))

        assert review.user_program_id == program.id
        assert review.version == program.current_version
        assert review.grade == expected.grade
        assert review.global_score == expected.global_score
        assert review.scoring_version == expected.scoring_version
        assert review.ekb_version == expected.ekb_version
        assert review.computed_at is not None


def test_runtime_fields_are_populated(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid(db)
        # Explicit zone-diverse covered exercises (lower / pecs / arms) so the program grades A/B
        # and the V1 B-cap reason is populated — robust to EKB ordering (Sb_MORPHO_POOL_COVERAGE_01
        # added covered exercises that shifted the alphabetical `_known_exercises(3)` selection).
        program = _make_program(
            db, uid, "runtime",
            names=["Adduction assise", "Chest Press machine", "Curl EZ-bar debout"],
        )
        review = compute_and_store_quality_review(db, uid, program.id).review

        assert review.confidence in {"moderate", "low", "very_low"}
        assert isinstance(review.coverage_ratio, float)
        assert 0.0 <= review.coverage_ratio <= 1.0
        # grade plafonné à B en V1 → la raison est renseignée
        assert review.grade_cap_reason


def test_stored_json_payloads_are_reparsable(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid(db)
        program = _make_program(db, uid, "json")
        review = compute_and_store_quality_review(db, uid, program.id).review

        for field in (
            review.subscores_json,
            review.alerts_json,
            review.suggestions_json,
            review.assumptions_json,
            review.missing_data_json,
        ):
            assert isinstance(json.loads(field), list)
        subscores = json.loads(review.subscores_json)
        assert {"key", "score", "reasons"} <= set(subscores[0])
        assert len(json.loads(review.missing_data_json)) == 4


def test_explicit_computed_at_is_honoured(client):
    from app.database import SessionLocal

    stamp = datetime(2026, 7, 23, 12, 0, tzinfo=UTC)
    with SessionLocal() as db:
        uid = _uid(db)
        program = _make_program(db, uid, "stamp")
        review = compute_and_store_quality_review(
            db, uid, program.id, computed_at=stamp
        ).review
        assert review.computed_at.replace(tzinfo=UTC) == stamp


# ───────── idempotence & immutabilité ─────────


def test_second_call_same_version_returns_existing_without_writing(client):
    from app.database import SessionLocal
    from app.models.user_program import UserProgramQualityReview

    with SessionLocal() as db:
        uid = _uid(db)
        program = _make_program(db, uid, "idem")
        first = compute_and_store_quality_review(db, uid, program.id)
        second = compute_and_store_quality_review(db, uid, program.id)

        assert first.created is True
        assert second.created is False
        assert second.review.id == first.review.id
        count = db.execute(
            select(func.count())
            .select_from(UserProgramQualityReview)
            .where(UserProgramQualityReview.user_program_id == program.id)
        ).scalar_one()
        assert count == 1


def test_new_version_gets_its_own_trace(client):
    from app.database import SessionLocal
    from app.models.user_program import UserProgramQualityReview

    with SessionLocal() as db:
        uid = _uid(db)
        program = _make_program(db, uid, "versions")
        compute_and_store_quality_review(db, uid, program.id)

        program.current_version = 2
        db.commit()
        second = compute_and_store_quality_review(db, uid, program.id)

        assert second.created is True
        assert second.review.version == 2
        count = db.execute(
            select(func.count())
            .select_from(UserProgramQualityReview)
            .where(UserProgramQualityReview.user_program_id == program.id)
        ).scalar_one()
        assert count == 2


def test_existing_trace_is_never_updated(client):
    """Le listener before_update (PERSISTENCE_05) ne doit jamais se déclencher."""
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid(db)
        program = _make_program(db, uid, "immutable")
        first = compute_and_store_quality_review(db, uid, program.id).review
        grade_before = first.grade
        computed_before = first.computed_at

        again = compute_and_store_quality_review(db, uid, program.id).review
        assert again.grade == grade_before
        assert again.computed_at == computed_before


# ───────── owner-scope & statuts ─────────


def test_cross_user_is_indistinguishable_from_missing(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid(db)
        program = _make_program(db, uid, "cross")
        other_uid = _other_uid(db)
        with pytest.raises(QualityReviewError, match="introuvable"):
            compute_and_store_quality_review(db, other_uid, program.id)


def test_missing_program_raises_the_same_error(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid(db)
        with pytest.raises(QualityReviewError, match="introuvable"):
            compute_and_store_quality_review(db, uid, 999_999)


def test_archived_program_is_refused(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import archive_draft

    with SessionLocal() as db:
        uid = _uid(db)
        program = _make_program(db, uid, "archived")
        archive_draft(db, uid, program.id)
        with pytest.raises(QualityReviewError, match="archivé"):
            compute_and_store_quality_review(db, uid, program.id)


def test_published_program_is_refused(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid(db)
        program = _make_program(db, uid, "published")
        program.status = "published"
        db.commit()
        with pytest.raises(QualityReviewError, match="publiée"):
            compute_and_store_quality_review(db, uid, program.id)


def test_draft_and_validated_are_both_scorable(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import validate_draft

    assert SCORABLE_STATUSES == ("draft", "validated")
    with SessionLocal() as db:
        uid = _uid(db)
        draft = _make_program(db, uid, "as-draft")
        assert draft.status == "draft"
        assert compute_and_store_quality_review(db, uid, draft.id).created is True

        other = _make_program(db, uid, "as-validated")
        validate_draft(db, uid, other.id)
        db.refresh(other)
        assert other.status == "validated"
        assert compute_and_store_quality_review(db, uid, other.id).created is True


def test_get_quality_review_is_owner_scoped(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid(db)
        program = _make_program(db, uid, "scoped-read")
        compute_and_store_quality_review(db, uid, program.id)

        assert get_quality_review(db, uid, program.id, 1) is not None
        assert get_quality_review(db, _other_uid(db), program.id, 1) is None


# ───────── adaptateur ORM → payload ─────────


def test_adapter_projects_the_whole_tree(client):
    from app.database import SessionLocal

    names = _known_exercises(3)
    with SessionLocal() as db:
        uid = _uid(db)
        program = _make_program(db, uid, "adapter", names)
        definition = program_to_quality_definition(program)

        assert definition.title == program.title
        assert len(definition.sessions) == 1
        slots = definition.sessions[0].exercises
        assert [s.exercise_name for s in slots] == names
        assert [s.position for s in slots] == [1, 2, 3]


def test_working_sets_count_rep_targets_excluding_warmups(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid(db)
        program = _make_program(db, uid, "warmups", _known_exercises(2), warmups=2)
        definition = program_to_quality_definition(program)
        # 3 séries de travail + 2 échauffements → working_sets == 3
        assert all(slot.working_sets == 3 for slot in definition.sessions[0].exercises)


def test_empty_program_does_not_crash(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import create_draft

    with SessionLocal() as db:
        uid = _uid(db)
        program = create_draft(db, uid, "Vide", "vide-review")
        stored = compute_and_store_quality_review(db, uid, program.id)
        assert stored.created is True
        assert stored.review.grade == "C"


def test_unknown_exercises_do_not_crash(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import create_draft, replace_draft_tree

    with SessionLocal() as db:
        uid = _uid(db)
        program = create_draft(db, uid, "Inconnus", "inconnus-review")
        replace_draft_tree(db, uid, program.id, _tree(["Exercice inconnu XYZ"]))
        stored = compute_and_store_quality_review(db, uid, program.id)
        assert stored.created is True
        assert stored.review.confidence in {"moderate", "low", "very_low"}
