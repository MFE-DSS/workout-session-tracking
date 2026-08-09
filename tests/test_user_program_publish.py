"""Sb_CUSTOM_PROGRAM_PUBLICATION_01 — publish a validated program to N templates.

Pins the spec 05 §6 materialization contract at the service level: ONE
`UserProgramSession` → ONE custom `WorkoutTemplate` (N per program, never a
single flattened one), slug `up{uid}-{base}-v{n}-s{position}` bounded to 64,
codes `E1..En`, working rep targets copied, quality frozen once, lifecycle
refusals (draft/archived/foreign) that create nothing, idempotent re-publish,
reseed survival, and native `session_builder` compatibility.
"""
from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy import func, inspect, select

from app.services.user_program_publish import (
    PublishNotFound,
    PublishRefused,
    publication_slug,
    publish_user_program,
)

# ─────────────────────────────── helpers ───────────────────────────────


def _uid(db) -> int:
    from app.models.user import User

    return db.execute(
        select(User.id).where(User.username == "testuser")
    ).scalar_one()


def _other_uid(db) -> int:
    from app.models.user import User
    from app.services.auth import hash_password

    other = db.execute(
        select(User).where(User.username == "pub-other")
    ).scalar_one_or_none()
    if other is None:
        other = User(username="pub-other", password_hash=hash_password("x"))
        db.add(other)
        db.commit()
    return other.id


def _tree(n_sessions: int = 2, ex_per: int = 2, sets: int = 3) -> list[dict]:
    return [
        {
            "position": s,
            "name": f"Séance {s}",
            "exercises": [
                {
                    "position": e,
                    "exercise_name": f"Exercice {s}-{e}",
                    "set_scheme": f"{sets}x 8-12",
                    "rep_targets": [
                        {"min_reps": 8, "max_reps": 12} for _ in range(sets)
                    ],
                }
                for e in range(1, ex_per + 1)
            ],
        }
        for s in range(1, n_sessions + 1)
    ]


def _make_validated(db, uid, slug, *, n_sessions=2, ex_per=2, sets=3, title=None):
    from app.services.user_program_drafts import (
        create_draft,
        replace_draft_tree,
        validate_draft,
    )

    program = create_draft(db, uid, title or f"Programme {slug}", slug)
    replace_draft_tree(db, uid, program.id, _tree(n_sessions, ex_per, sets))
    validate_draft(db, uid, program.id)
    db.refresh(program)
    return program


def _user_template_count(db) -> int:
    from app.models.catalog import WorkoutTemplate

    return db.execute(
        select(func.count())
        .select_from(WorkoutTemplate)
        .where(WorkoutTemplate.catalog_section == "user")
    ).scalar_one()


# ─────────────────────── nominal materialization (1-10) ───────────────────────


def test_validated_multi_session_publishes_to_n_templates(client):
    from app.database import SessionLocal
    from app.models.user_program import UserProgramSession

    with SessionLocal() as db:
        uid = _uid(db)
        program = _make_validated(db, uid, "multi", n_sessions=3)
        result = publish_user_program(db, uid, program.id)

        assert result.created is True
        n_sessions = db.execute(
            select(func.count())
            .select_from(UserProgramSession)
            .where(UserProgramSession.user_program_id == program.id)
        ).scalar_one()
        assert n_sessions == 3  # (#2)
        assert len(result.templates) == 3  # (#1)


def test_sessions_get_link_and_program_published(client):
    from app.database import SessionLocal
    from app.models.user_program import UserProgramSession

    with SessionLocal() as db:
        uid = _uid(db)
        program = _make_validated(db, uid, "link", n_sessions=2)
        publish_user_program(db, uid, program.id)

        sessions = (
            db.execute(
                select(UserProgramSession).where(
                    UserProgramSession.user_program_id == program.id
                )
            )
            .scalars()
            .all()
        )
        for s in sessions:
            assert s.published_template_id is not None  # (#3)
            assert s.template_slug_snapshot is not None  # (#4)
            assert s.template_slug_snapshot.startswith(f"up{uid}-link-v1-s")
        db.refresh(program)
        assert program.status == "published"  # (#5)


def test_each_template_is_user_section(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid(db)
        program = _make_validated(db, uid, "section", n_sessions=2)
        result = publish_user_program(db, uid, program.id)
        for template in result.templates:
            assert template.catalog_section == "user"  # (#6)


def test_slug_format_matches_spec(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid(db)
        program = _make_validated(db, uid, "shoulders", n_sessions=2)
        result = publish_user_program(db, uid, program.id)
        slugs = sorted(t.slug for t in result.templates)
        assert slugs == [
            f"up{uid}-shoulders-v1-s1",
            f"up{uid}-shoulders-v1-s2",
        ]  # (#7)


def test_publication_slug_truncates_and_stays_under_64():
    # (#8) — pure, deterministic: an 80-char base still fits 64 with the fixed
    # identity parts (prefix + version + position) preserved.
    slug = publication_slug(12345, "x" * 80, 9, 7)
    assert len(slug) <= 64
    assert slug.startswith("up12345-")
    assert slug.endswith("-v9-s7")
    assert not slug.endswith("--v9-s7")  # no dangling hyphen after truncation


def test_long_slug_base_is_truncated_when_published(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid(db)
        program = _make_validated(db, uid, "a" * 64, n_sessions=2)
        result = publish_user_program(db, uid, program.id)
        for template in result.templates:
            assert len(template.slug) <= 64  # (#8)
            assert template.slug.startswith(f"up{uid}-")
        assert any(t.slug.endswith("-v1-s2") for t in result.templates)


def test_template_exercise_codes_are_e1_en(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid(db)
        program = _make_validated(db, uid, "codes", n_sessions=2, ex_per=3)
        result = publish_user_program(db, uid, program.id)
        for template in result.templates:
            codes = [e.code for e in sorted(template.exercises, key=lambda x: x.position)]
            assert codes == ["E1", "E2", "E3"]  # (#9)


def test_exercises_and_rep_targets_are_copied(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid(db)
        program = _make_validated(db, uid, "copy", n_sessions=1, ex_per=2, sets=3)
        result = publish_user_program(db, uid, program.id)
        template = result.templates[0]
        assert len(template.exercises) == 2
        for te in template.exercises:
            assert te.name.startswith("Exercice")
            assert te.set_scheme == "3x 8-12"
            assert len(te.rep_targets) == 3
            assert sorted(rt.set_index for rt in te.rep_targets) == [1, 2, 3]
            for rt in te.rep_targets:
                assert (rt.min_reps, rt.max_reps) == (8, 12)  # (#10)


def test_quality_review_written_exactly_once(client):
    from app.database import SessionLocal
    from app.models.user_program import UserProgramQualityReview

    with SessionLocal() as db:
        uid = _uid(db)
        program = _make_validated(db, uid, "qual")

        def _reviews() -> int:
            return db.execute(
                select(func.count())
                .select_from(UserProgramQualityReview)
                .where(UserProgramQualityReview.user_program_id == program.id)
            ).scalar_one()

        publish_user_program(db, uid, program.id)
        assert _reviews() == 1  # (#11)
        publish_user_program(db, uid, program.id)  # idempotent re-publish
        assert _reviews() == 1  # still one — the past is never re-scored


# ─────────────────────── lifecycle refusals (12-15) ───────────────────────


def test_draft_is_refused_and_creates_nothing(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import create_draft

    with SessionLocal() as db:
        uid = _uid(db)
        program = create_draft(db, uid, "Draft", "draftp")
        before = _user_template_count(db)
        with pytest.raises(PublishRefused):
            publish_user_program(db, uid, program.id)
        assert _user_template_count(db) == before  # (#12)


def test_archived_is_refused_and_creates_nothing(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import archive_draft

    with SessionLocal() as db:
        uid = _uid(db)
        program = _make_validated(db, uid, "archp")
        archive_draft(db, uid, program.id)
        before = _user_template_count(db)
        with pytest.raises(PublishRefused):
            publish_user_program(db, uid, program.id)
        assert _user_template_count(db) == before  # (#13)


def test_already_published_is_idempotent(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid(db)
        program = _make_validated(db, uid, "idem", n_sessions=2)
        first = publish_user_program(db, uid, program.id)
        count_after_first = _user_template_count(db)

        second = publish_user_program(db, uid, program.id)
        assert second.created is False
        assert _user_template_count(db) == count_after_first  # no duplicates (#14)
        assert len(second.templates) == len(first.templates) == 2


def test_other_user_and_missing_are_indistinct_not_found(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid(db)
        other = _other_uid(db)
        foreign = _make_validated(db, other, "foreign", n_sessions=1)
        with pytest.raises(PublishNotFound):
            publish_user_program(db, uid, foreign.id)  # (#15) foreign
        with pytest.raises(PublishNotFound):
            publish_user_program(db, uid, 999999)  # missing, same error


# ─────────────────────── integration invariants (16-20) ───────────────────────


def test_user_templates_survive_reseed(client):
    from app.database import SessionLocal
    from app.models.catalog import WorkoutTemplate
    from app.services.seed import seed_reference_split

    with SessionLocal() as db:
        uid = _uid(db)
        program = _make_validated(db, uid, "survive", n_sessions=2)
        result = publish_user_program(db, uid, program.id)
        user_slugs = {t.slug for t in result.templates}

        seed_reference_split(db)  # reseed the SYSTEM catalog
        db.commit()

        remaining = {
            s
            for (s,) in db.execute(
                select(WorkoutTemplate.slug).where(
                    WorkoutTemplate.catalog_section == "user"
                )
            ).all()
        }
        assert user_slugs <= remaining  # (#16) — survived the wipe-guard
        system = db.execute(
            select(func.count())
            .select_from(WorkoutTemplate)
            .where(WorkoutTemplate.catalog_section != "user")
        ).scalar_one()
        assert system > 0  # system catalog was rebuilt alongside


def test_session_builder_instantiates_a_published_template(client):
    from app.database import SessionLocal
    from app.enums import SetKind
    from app.services.session_builder import instantiate_session

    with SessionLocal() as db:
        uid = _uid(db)
        program = _make_validated(db, uid, "instant", n_sessions=1, ex_per=2, sets=3)
        result = publish_user_program(db, uid, program.id)
        template = result.templates[0]

        # (#18) — the existing builder must run UNCHANGED on a published template.
        session = instantiate_session(db, template, datetime.now(UTC), user_id=uid)
        db.add(session)
        db.commit()

        assert len(session.session_exercises) == 2
        for se in session.session_exercises:
            work = [s for s in se.set_logs if s.kind == SetKind.WORK]
            assert len(work) == 3  # one work row per copied rep target


def test_published_template_id_is_on_sessions_not_programs(client):
    from app.database import engine

    up_cols = {c["name"] for c in inspect(engine).get_columns("user_programs")}
    ups_cols = {
        c["name"] for c in inspect(engine).get_columns("user_program_sessions")
    }
    assert "published_template_id" not in up_cols  # (#19)
    assert "published_template_id" in ups_cols
    assert "template_slug_snapshot" in ups_cols


def test_publish_does_not_mutate_the_ekb(client):
    from app.database import SessionLocal
    from app.services.program_quality_engine import ExerciseKnowledgeBase

    before = dict(ExerciseKnowledgeBase.load().entries)
    with SessionLocal() as db:
        uid = _uid(db)
        program = _make_validated(db, uid, "ekb")
        publish_user_program(db, uid, program.id)
    after = ExerciseKnowledgeBase.load().entries
    assert after == before  # (#20) — publication reads, never writes the EKB
