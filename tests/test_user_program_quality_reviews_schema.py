"""Sb_CUSTOM_PROGRAM_PERSISTENCE_03 — user_program_quality_reviews schema.

Pins the LAST persistence brick of the Custom Program track: the frozen
quality-review trace table (spec 03 §9-C / spec 04 §5). One immutable row
per published program version — this build ships the RECEPTACLE only:
no score is computed, thresholded or interpreted anywhere here (the
scoring engine is `Sb_CUSTOM_PROGRAM_SCORING_01+`).
"""
from __future__ import annotations

import json

import pytest
from sqlalchemy import func, inspect, select
from sqlalchemy.exc import IntegrityError

_PAYLOADS = (
    "subscores_json",
    "alerts_json",
    "suggestions_json",
    "assumptions_json",
    "missing_data_json",
)


def _mk_program(db, user_id: int, slug_base: str = "score"):
    from app.models.user_program import UserProgram

    prog = UserProgram(user_id=user_id, title="Scoré", slug_base=slug_base)
    db.add(prog)
    db.commit()
    db.refresh(prog)
    return prog


def _mk_review(db, program_id: int, version: int = 1, **kw):
    from app.models.user_program import UserProgramQualityReview

    review = UserProgramQualityReview(
        user_program_id=program_id,
        version=version,
        grade=kw.pop("grade", "B"),
        scoring_version=kw.pop("scoring_version", 1),
        **kw,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def _uid(db) -> int:
    from app.models.user import User

    return db.execute(select(User.id).limit(1)).scalar_one()


# ───────── 1-2. existence + colonnes ─────────


def test_quality_reviews_table_exists_with_expected_columns(client):
    from app.database import engine

    inspector = inspect(engine)
    assert "user_program_quality_reviews" in inspector.get_table_names()
    cols = {c["name"] for c in inspector.get_columns("user_program_quality_reviews")}
    assert cols == {
        "id", "user_program_id", "version", "grade", "global_score",
        "subscores_json", "alerts_json", "suggestions_json",
        "assumptions_json", "missing_data_json", "scoring_version",
        "ekb_version", "computed_at",
        # SCORING_03 (migration o6p1j7k8m09) — champs runtime du moteur.
        "confidence", "coverage_ratio", "grade_cap_reason",
    }


# ───────── 3. cascade ─────────


def test_deleting_program_cascades_to_reviews(client):
    from app.database import SessionLocal
    from app.models.user_program import UserProgramQualityReview

    with SessionLocal() as db:
        prog = _mk_program(db, _uid(db), slug_base="cascade-review")
        _mk_review(db, prog.id, version=1)
        db.delete(prog)
        db.commit()
        count = db.execute(
            select(func.count()).select_from(UserProgramQualityReview)
        ).scalar_one()
        assert count == 0


# ───────── 4. une trace par version (immutabilité structurelle) ─────────


def test_one_review_per_program_version(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        prog = _mk_program(db, _uid(db), slug_base="uniq-version")
        _mk_review(db, prog.id, version=1)
        with pytest.raises(IntegrityError):
            _mk_review(db, prog.id, version=1, grade="A")


def test_reviews_allowed_across_versions_and_programs(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid(db)
        p1 = _mk_program(db, uid, slug_base="multi-v")
        p2 = _mk_program(db, uid, slug_base="autre")
        _mk_review(db, p1.id, version=1)
        _mk_review(db, p1.id, version=2, grade="A")  # nouvelle version : OK
        _mk_review(db, p2.id, version=1)  # autre programme : OK


# ───────── 5-6. NOT NULL grade / scoring_version ─────────


def test_grade_is_mandatory(client):
    from app.database import SessionLocal
    from app.models.user_program import UserProgramQualityReview

    with SessionLocal() as db:
        prog = _mk_program(db, _uid(db), slug_base="no-grade")
        db.add(
            UserProgramQualityReview(
                user_program_id=prog.id, version=1, grade=None, scoring_version=1
            )
        )
        with pytest.raises(IntegrityError):
            db.commit()


def test_scoring_version_is_mandatory(client):
    from app.database import SessionLocal
    from app.models.user_program import UserProgramQualityReview

    with SessionLocal() as db:
        prog = _mk_program(db, _uid(db), slug_base="no-engine-v")
        db.add(
            UserProgramQualityReview(
                user_program_id=prog.id, version=1, grade="B", scoring_version=None
            )
        )
        with pytest.raises(IntegrityError):
            db.commit()


# ───────── 7. round-trip des 5 payloads JSON ─────────


def test_json_payloads_round_trip(client):
    from app.database import SessionLocal
    from app.models.user_program import UserProgramQualityReview

    payloads = {
        "subscores_json": {"volume_per_zone": {"score": 72, "reasons": ["ok"]}},
        "alerts_json": [{"subscore": "duration_realism", "severity": "warn"}],
        "suggestions_json": [{"subscore": "redundancy", "message": "varier"}],
        "assumptions_json": ["niveau supposé débutant"],
        "missing_data_json": ["matériel non déclaré"],
    }
    with SessionLocal() as db:
        prog = _mk_program(db, _uid(db), slug_base="payloads")
        review = _mk_review(
            db,
            prog.id,
            version=1,
            **{k: json.dumps(v, ensure_ascii=False) for k, v in payloads.items()},
        )
        rid = review.id

    with SessionLocal() as db:
        stored = db.get(UserProgramQualityReview, rid)
        for field, expected in payloads.items():
            assert json.loads(getattr(stored, field)) == expected


# ───────── 8. ekb_version optionnelle + computed_at ─────────


def test_ekb_version_optional_and_computed_at_set(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        prog = _mk_program(db, _uid(db), slug_base="ekb-opt")
        bare = _mk_review(db, prog.id, version=1)
        assert bare.ekb_version is None
        assert bare.computed_at is not None
        pinned = _mk_review(db, prog.id, version=2, ekb_version="ekb-2026-07.v1")
        assert pinned.ekb_version == "ekb-2026-07.v1"


# ───────── 9. ordre relationnel par version ─────────


def test_reviews_relationship_ordered_by_version(client):
    from app.database import SessionLocal
    from app.models.user_program import UserProgram

    with SessionLocal() as db:
        prog = _mk_program(db, _uid(db), slug_base="ordre-reviews")
        _mk_review(db, prog.id, version=3, grade="C")
        _mk_review(db, prog.id, version=1)
        _mk_review(db, prog.id, version=2, grade="A")
        pid = prog.id

    with SessionLocal() as db:
        prog = db.get(UserProgram, pid)
        assert [r.version for r in prog.quality_reviews] == [1, 2, 3]


# ───────── 10. zéro FK hors arbre ─────────


def test_quality_reviews_has_no_fk_outside_tree(client):
    from app.database import engine

    fks = inspect(engine).get_foreign_keys("user_program_quality_reviews")
    targets = {fk["referred_table"] for fk in fks}
    assert targets == {"user_programs"}
