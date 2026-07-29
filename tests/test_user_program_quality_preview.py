"""Sb_CUSTOM_PROGRAM_WIZARD_04 — the pure, non-persisted quality preview helper.

Pins the read-only composition `program_to_quality_definition → score_program →
build_program_quality_feedback`: it exposes both the raw result and the product
feedback, writes NOTHING, and — critically — computes IDENTICALLY to the
SCORING_03 writer (same adapter, same engine), so a preview never contradicts a
future persisted trace of the same version.

Every `app.*` import is inside the test/helper (conftest resets the `app` module
tree per test); `client` ensures the DB + EKB are ready.
"""
from __future__ import annotations

from sqlalchemy import func, select


def _uid(db) -> int:
    from app.models.user import User

    return db.execute(select(User.id).limit(1)).scalar_one()


def _known_exercises(limit: int) -> list[str]:
    from app.services.program_quality_engine import ExerciseKnowledgeBase

    ekb = ExerciseKnowledgeBase.load()
    usable = [
        name
        for name, entry in ekb.entries.items()
        if entry.get("zone_primary") and entry.get("movement_pattern")
    ]
    return usable[:limit]


def _tree(names: list[str]) -> list[dict]:
    return [
        {
            "position": 1,
            "name": "Séance 1",
            "exercises": [
                {
                    "position": i + 1,
                    "exercise_name": name,
                    "set_scheme": "3x 8-12",
                    "rep_targets": [{"min_reps": 8, "max_reps": 12} for _ in range(3)],
                }
                for i, name in enumerate(names)
            ],
        }
    ]


def _make_program(db, uid, slug, names=None):
    from app.services.user_program_drafts import create_draft, replace_draft_tree

    program = create_draft(db, uid, f"Programme {slug}", slug)
    replace_draft_tree(db, uid, program.id, _tree(names or _known_exercises(3)))
    db.refresh(program)
    return program


def _review_count(db) -> int:
    from app.models.user_program import UserProgramQualityReview

    return db.execute(
        select(func.count()).select_from(UserProgramQualityReview)
    ).scalar_one()


# ───────── composition nominale ─────────


def test_preview_exposes_result_and_feedback(client):
    from app.database import SessionLocal
    from app.services.user_program_quality_preview import compute_quality_preview

    with SessionLocal() as db:
        program = _make_program(db, _uid(db), "preview-nominal")
        preview = compute_quality_preview(program)

        assert preview.result.grade in {"A", "B", "C"}
        assert preview.result.global_score is not None
        assert preview.feedback.grade == preview.result.grade
        assert preview.feedback.headline
        assert preview.feedback.disclaimer


def test_preview_is_deterministic(client):
    from app.database import SessionLocal
    from app.services.user_program_quality_preview import compute_quality_preview

    with SessionLocal() as db:
        program = _make_program(db, _uid(db), "preview-determinism")
        first = compute_quality_preview(program)
        second = compute_quality_preview(program)

        assert first.result.to_dict() == second.result.to_dict()
        assert first.feedback.to_dict() == second.feedback.to_dict()


def test_preview_matches_the_writer_engine(client):
    """Invariant central : la preview réutilise l'adaptateur et le moteur du
    writer SCORING_03 — même version ⇒ même note."""
    from app.database import SessionLocal
    from app.services.program_quality_engine import score_program
    from app.services.program_quality_reviews import program_to_quality_definition
    from app.services.user_program_quality_preview import compute_quality_preview

    with SessionLocal() as db:
        program = _make_program(db, _uid(db), "preview-parity")
        preview = compute_quality_preview(program)
        direct = score_program(program_to_quality_definition(program))

        assert preview.result.to_dict() == direct.to_dict()


# ───────── zéro écriture ─────────


def test_preview_writes_no_review(client):
    from app.database import SessionLocal
    from app.services.user_program_quality_preview import compute_quality_preview

    with SessionLocal() as db:
        program = _make_program(db, _uid(db), "preview-no-write")
        before = _review_count(db)
        compute_quality_preview(program)
        assert _review_count(db) == before == 0


# ───────── dégradation honnête ─────────


def test_preview_unknown_exercises_is_low_confidence(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import create_draft, replace_draft_tree
    from app.services.user_program_quality_preview import compute_quality_preview

    with SessionLocal() as db:
        uid = _uid(db)
        program = create_draft(db, uid, "Inconnus", "preview-unknown")
        replace_draft_tree(db, uid, program.id, _tree(["Exercice inconnu XYZ"]))
        db.refresh(program)
        preview = compute_quality_preview(program)

        assert preview.result.confidence == "very_low"
        assert "partielle" in preview.feedback.confidence_note.lower()
