"""Sb_CUSTOM_PROGRAM_PUBLICATION_02 — start a new edit cycle on a published program.

Pins the spec 04 §6-7 / spec 05 §6-7 mono-row versioning: editing a published program
returns the SAME `UserProgram` row to `draft` at `current_version + 1` — no copy row,
no versions table, no migration, published v{n} templates untouched, no quality write.
Covers same-row transition, exact-once increment, double-submit safety, link clearing,
template immutability, owner-scope, lifecycle guards, and the published-only UI CTA.
"""
from __future__ import annotations

import pytest
from sqlalchemy import func, select

from app.services.user_program_versioning import (
    NewCycleResult,
    VersioningNotFound,
    VersioningRefused,
    start_new_edit_cycle,
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
        select(User).where(User.username == "ver-other")
    ).scalar_one_or_none()
    if other is None:
        other = User(username="ver-other", password_hash=hash_password("x"))
        db.add(other)
        db.commit()
    return other.id


def _tree(n_sessions=2, ex_per=2, sets=3):
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


def _make_validated(db, uid, slug, *, n_sessions=2, ex_per=2):
    from app.services.user_program_drafts import (
        create_draft,
        replace_draft_tree,
        validate_draft,
    )

    program = create_draft(db, uid, f"Programme {slug}", slug)
    replace_draft_tree(db, uid, program.id, _tree(n_sessions, ex_per))
    validate_draft(db, uid, program.id)
    db.refresh(program)
    return program


def _make_published(db, uid, slug, *, n_sessions=2, ex_per=2):
    from app.services.user_program_publish import publish_user_program

    program = _make_validated(db, uid, slug, n_sessions=n_sessions, ex_per=ex_per)
    publish_user_program(db, uid, program.id)
    db.refresh(program)
    return program


def _program_count(db) -> int:
    from app.models.user_program import UserProgram

    return db.execute(
        select(func.count()).select_from(UserProgram)
    ).scalar_one()


def _template_count(db) -> int:
    from app.models.catalog import WorkoutTemplate

    return db.execute(
        select(func.count()).select_from(WorkoutTemplate)
    ).scalar_one()


def _sessions(db, program_id):
    from app.models.user_program import UserProgramSession

    return (
        db.execute(
            select(UserProgramSession).where(
                UserProgramSession.user_program_id == program_id
            )
        )
        .scalars()
        .all()
    )


# ───────────────────────── service: same-row versioning ─────────────────────────


def test_published_starts_new_cycle_on_same_row(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid(db)
        program = _make_published(db, uid, "cycle", n_sessions=2)
        pid = program.id
        assert program.status == "published"
        assert program.current_version == 1

        result = start_new_edit_cycle(db, uid, pid)

        assert isinstance(result, NewCycleResult)
        assert result.incremented is True
        assert result.program.id == pid  # (#1) same row, id unchanged
        assert result.program.status == "draft"
        assert result.program.current_version == 2  # (#2) +1 exactly once


def test_repeated_call_does_not_increment_twice(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid(db)
        pid = _make_published(db, uid, "dbl").id

        start_new_edit_cycle(db, uid, pid)  # published → draft v2
        second = start_new_edit_cycle(db, uid, pid)  # now draft → no-op

        assert second.incremented is False  # (#3)
        assert second.program.current_version == 2  # not 3


def test_no_new_user_program_row(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid(db)
        pid = _make_published(db, uid, "norow").id
        before = _program_count(db)
        start_new_edit_cycle(db, uid, pid)
        assert _program_count(db) == before  # (#4) no copy row


def test_sessions_and_exercises_remain_editable(client):
    from app.database import SessionLocal
    from app.models.user_program import UserProgramExercise

    with SessionLocal() as db:
        uid = _uid(db)
        pid = _make_published(db, uid, "tree", n_sessions=2, ex_per=2).id
        start_new_edit_cycle(db, uid, pid)

        sessions = _sessions(db, pid)
        assert len(sessions) == 2  # (#5) tree kept
        session_ids = [s.id for s in sessions]
        ex_count = db.execute(
            select(func.count())
            .select_from(UserProgramExercise)
            .where(UserProgramExercise.user_program_session_id.in_(session_ids))
        ).scalar_one()
        assert ex_count == 4


def test_session_publication_links_are_cleared(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid(db)
        program = _make_published(db, uid, "links", n_sessions=2)
        pid = program.id
        # after publication the links are set
        assert all(s.published_template_id is not None for s in _sessions(db, pid))

        start_new_edit_cycle(db, uid, pid)

        for s in _sessions(db, pid):
            assert s.published_template_id is None  # (#6)
            assert s.template_slug_snapshot is None  # (#7)


def test_old_templates_unchanged_and_not_deleted(client):
    from app.database import SessionLocal
    from app.models.catalog import WorkoutTemplate

    with SessionLocal() as db:
        uid = _uid(db)
        program = _make_published(db, uid, "keep", n_sessions=2)
        pid = program.id

        def _snapshot():
            rows = db.execute(
                select(
                    WorkoutTemplate.slug,
                    WorkoutTemplate.catalog_section,
                    WorkoutTemplate.name,
                ).where(WorkoutTemplate.catalog_section == "user")
            ).all()
            return sorted(tuple(r) for r in rows)

        before = _snapshot()
        count_before = _template_count(db)

        start_new_edit_cycle(db, uid, pid)

        assert _snapshot() == before  # (#8) v1 templates byte-identical
        assert _template_count(db) == count_before  # (#9) none deleted


def test_no_quality_review_written_on_new_cycle(client):
    from app.database import SessionLocal
    from app.models.user_program import UserProgramQualityReview

    with SessionLocal() as db:
        uid = _uid(db)
        program = _make_published(db, uid, "qual")
        pid = program.id

        def _reviews():
            return db.execute(
                select(func.count())
                .select_from(UserProgramQualityReview)
                .where(UserProgramQualityReview.user_program_id == pid)
            ).scalar_one()

        before = _reviews()  # one review frozen at publication
        start_new_edit_cycle(db, uid, pid)
        assert _reviews() == before  # (#10) no new review for v2


def test_owner_scope_and_missing_are_not_found(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid(db)
        other = _other_uid(db)
        foreign = _make_published(db, other, "foreign")
        with pytest.raises(VersioningNotFound):
            start_new_edit_cycle(db, uid, foreign.id)  # (#11) foreign
        with pytest.raises(VersioningNotFound):
            start_new_edit_cycle(db, uid, 999999)  # missing, same error


def test_draft_and_validated_do_not_increment(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import create_draft

    with SessionLocal() as db:
        uid = _uid(db)
        # draft — already editable, no increment
        draft = create_draft(db, uid, "Draft", "verdraft")
        r_draft = start_new_edit_cycle(db, uid, draft.id)
        assert r_draft.incremented is False
        assert r_draft.program.current_version == 1
        assert r_draft.program.status == "draft"

        # validated — already editable, no increment
        validated = _make_validated(db, uid, "verval")
        r_val = start_new_edit_cycle(db, uid, validated.id)
        assert r_val.incremented is False  # (#12)
        assert r_val.program.current_version == 1
        assert r_val.program.status == "validated"


def test_archived_is_softly_refused(client):
    from app.database import SessionLocal
    from app.services.user_program_drafts import archive_draft

    with SessionLocal() as db:
        uid = _uid(db)
        program = _make_published(db, uid, "verarch")
        archive_draft(db, uid, program.id)
        with pytest.raises(VersioningRefused):
            start_new_edit_cycle(db, uid, program.id)  # (#12) archived guard
        db.refresh(program)
        assert program.current_version == 1  # no increment


# ───────────────────────── HTTP: CTA + editor (SSR, no-JS) ─────────────────────────


def _session():
    from app.database import SessionLocal

    return SessionLocal()


def _make_published_http(slug: str) -> int:
    with _session() as db:
        return _make_published(db, _uid(db), slug).id


def _make_draft_http(slug: str) -> int:
    from app.services.user_program_drafts import create_draft

    with _session() as db:
        return create_draft(db, _uid(db), f"Programme {slug}", slug).id


def test_cta_appears_only_for_published(client):
    published = _make_published_http("cta-pub")
    draft = _make_draft_http("cta-draft")

    pub_body = client.get(f"/programs/{published}").text
    assert "Créer une nouvelle version" in pub_body  # (#13) shown for published

    draft_body = client.get(f"/programs/{draft}").text
    assert "Créer une nouvelle version" not in draft_body  # hidden otherwise


def test_post_new_version_returns_editable_draft(client):
    pid = _make_published_http("http-cycle")
    r = client.post(f"/programs/{pid}/new-version", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"].endswith(f"/programs/{pid}")

    # (#14) the existing editor route opens the returned draft (now draft v2)
    from app.models.user_program import UserProgram

    with _session() as db:
        program = db.get(UserProgram, pid)
        assert program.status == "draft"
        assert program.current_version == 2
    editor = client.get(f"/programs/{pid}").text
    assert "Séance 1" in editor  # tree still editable


def test_post_new_version_foreign_is_404(client):
    from app.models.user import User
    from app.services.auth import hash_password

    with _session() as db:
        other = db.execute(
            select(User).where(User.username == "ver-http-other")
        ).scalar_one_or_none()
        if other is None:
            other = User(username="ver-http-other", password_hash=hash_password("x"))
            db.add(other)
            db.commit()
        foreign = _make_published(db, other.id, "http-foreign").id
    assert client.post(f"/programs/{foreign}/new-version").status_code == 404


def test_post_new_version_unauthenticated_redirects(client):
    pid = _make_published_http("http-auth")
    client.cookies.clear()
    r = client.post(f"/programs/{pid}/new-version", follow_redirects=False)
    assert r.headers["location"] == "/login"
