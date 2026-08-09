"""Sb_CUSTOM_PROGRAM_PUBLICATION_03 — owner launch of published session templates.

Pins the spec 05 §14 owned-access model: the owner launches published custom sessions
through the owned UserProgram context (UserProgram → UserProgramSession →
published_template_id), never through the shared catalogue. A user can only launch their
own custom templates; system templates stay public; a non-published program is not
launchable. Covers the owned-start route, the create_session ownership guard, the /library
exclusions, and the no-mutation invariants.
"""
from __future__ import annotations

import pytest
from sqlalchemy import func, select

from app.services.user_program_launch import (
    LaunchNotFound,
    is_owned_published_template,
    resolve_owned_published_template,
)

# ─────────────────────────────── helpers ───────────────────────────────


def _uid_in(db) -> int:
    from app.models.user import User

    return db.execute(
        select(User.id).where(User.username == "testuser")
    ).scalar_one()


def _other_uid(db) -> int:
    from app.models.user import User
    from app.services.auth import hash_password

    other = db.execute(
        select(User).where(User.username == "launch-other")
    ).scalar_one_or_none()
    if other is None:
        other = User(username="launch-other", password_hash=hash_password("x"))
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


def _make_published(db, uid, slug, *, n_sessions=2):
    from app.services.user_program_publish import publish_user_program

    program = _make_validated(db, uid, slug, n_sessions=n_sessions)
    publish_user_program(db, uid, program.id)
    db.refresh(program)
    return program


def _session_ids(db, program_id):
    from app.models.user_program import UserProgramSession

    return list(
        db.execute(
            select(UserProgramSession.id).where(
                UserProgramSession.user_program_id == program_id
            )
        ).scalars()
    )


def _session():
    from app.database import SessionLocal

    return SessionLocal()


def _uid() -> int:
    with _session() as db:
        return _uid_in(db)


def _workout_session_count(db) -> int:
    from app.models.session import WorkoutSession

    return db.execute(
        select(func.count()).select_from(WorkoutSession)
    ).scalar_one()


def _a_system_slug(db) -> str:
    from app.models.catalog import WorkoutTemplate

    return db.execute(
        select(WorkoutTemplate.slug)
        .where(WorkoutTemplate.catalog_section.notin_(["user", "archived"]))
        .limit(1)
    ).scalar_one()


# ─────────────────────── service: owned resolution + reverse lookup ───────────────────────


def test_resolve_owned_published_template_ok(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid_in(db)
        program = _make_published(db, uid, "resolve", n_sessions=2)
        sid = _session_ids(db, program.id)[0]
        template = resolve_owned_published_template(db, uid, program.id, sid)
        assert template.catalog_section == "user"
        assert template.slug.startswith(f"up{uid}-resolve-v1-s")
        assert len(template.exercises) == 2  # eager-loaded for instantiation


def test_resolve_foreign_and_missing_are_not_found(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid_in(db)
        other = _other_uid(db)
        foreign = _make_published(db, other, "foreign", n_sessions=1)
        fsid = _session_ids(db, foreign.id)[0]
        with pytest.raises(LaunchNotFound):
            resolve_owned_published_template(db, uid, foreign.id, fsid)  # foreign
        with pytest.raises(LaunchNotFound):
            resolve_owned_published_template(db, uid, foreign.id, 999999)  # missing session


def test_resolve_unpublished_draft_is_not_found(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid_in(db)
        program = _make_validated(db, uid, "draftresolve", n_sessions=1)  # not published
        sid = _session_ids(db, program.id)[0]
        with pytest.raises(LaunchNotFound):
            resolve_owned_published_template(db, uid, program.id, sid)


def test_is_owned_published_template_reverse_lookup(client):
    from app.database import SessionLocal
    from app.models.user_program import UserProgramSession

    with SessionLocal() as db:
        uid = _uid_in(db)
        other = _other_uid(db)
        mine = _make_published(db, uid, "mine", n_sessions=1)
        theirs = _make_published(db, other, "theirs", n_sessions=1)
        my_tid = db.execute(
            select(UserProgramSession.published_template_id).where(
                UserProgramSession.user_program_id == mine.id
            )
        ).scalar_one()
        their_tid = db.execute(
            select(UserProgramSession.published_template_id).where(
                UserProgramSession.user_program_id == theirs.id
            )
        ).scalar_one()
        assert is_owned_published_template(db, uid, my_tid) is True
        assert is_owned_published_template(db, uid, their_tid) is False  # foreign


# ─────────────────────────── HTTP: CTA + owned start ───────────────────────────


def _make_published_http(slug: str) -> int:
    with _session() as db:
        return _make_published(db, _uid_in(db), slug).id


def test_published_detail_shows_launch_cta(client):
    pid = _make_published_http("cta-pub")
    body = client.get(f"/programs/{pid}").text
    assert "Démarrer cette séance" in body  # launch CTA present for published


def test_draft_validated_archived_show_no_launch_cta(client):
    from app.services.user_program_drafts import archive_draft, create_draft

    with _session() as db:
        uid = _uid_in(db)
        draft = create_draft(db, uid, "Draft", "cta-draft").id
        validated = _make_validated(db, uid, "cta-val").id
        arch = _make_published(db, uid, "cta-arch").id
        arch_sid = _session_ids(db, arch)[0]
        archive_draft(db, uid, arch)  # soft-delete: keeps status='published', sets archived_at

    for pid in (draft, validated, arch):
        assert "Démarrer cette séance" not in client.get(f"/programs/{pid}").text
    # archived program is soft-deleted: its linked session is not launchable either (spec 04 §8)
    assert client.post(f"/programs/{arch}/sessions/{arch_sid}/start").status_code == 404


def test_owner_can_start_published_session(client):
    pid = _make_published_http("start-ok")
    with _session() as db:
        sid = _session_ids(db, pid)[0]
        before = _workout_session_count(db)

    r = client.post(
        f"/programs/{pid}/sessions/{sid}/start", follow_redirects=False
    )
    assert r.status_code == 303
    assert r.headers["location"].startswith("/sessions/")

    with _session() as db:
        assert _workout_session_count(db) == before + 1  # a real session was created


def test_start_foreign_and_missing_are_404(client):
    from app.models.user import User
    from app.services.auth import hash_password

    with _session() as db:
        other = db.execute(
            select(User).where(User.username == "launch-http-other")
        ).scalar_one_or_none()
        if other is None:
            other = User(username="launch-http-other", password_hash=hash_password("x"))
            db.add(other)
            db.commit()
        foreign = _make_published(db, other.id, "start-foreign", n_sessions=1)
        fsid = _session_ids(db, foreign.id)[0]

    assert client.post(f"/programs/{foreign.id}/sessions/{fsid}/start").status_code == 404
    assert client.post(f"/programs/{foreign.id}/sessions/999999/start").status_code == 404


def test_launch_does_not_mutate_template_or_program(client):
    from app.models.catalog import WorkoutTemplate
    from app.models.user_program import UserProgram, UserProgramSession

    pid = _make_published_http("nomutate")
    with _session() as db:
        sid = _session_ids(db, pid)[0]
        tid = db.execute(
            select(UserProgramSession.published_template_id).where(
                UserProgramSession.id == sid
            )
        ).scalar_one()
        tpl_before = db.execute(
            select(WorkoutTemplate.slug, WorkoutTemplate.name, WorkoutTemplate.catalog_section)
            .where(WorkoutTemplate.id == tid)
        ).one()
        prog_before = db.execute(
            select(UserProgram.status, UserProgram.current_version).where(
                UserProgram.id == pid
            )
        ).one()

    client.post(f"/programs/{pid}/sessions/{sid}/start", follow_redirects=False)

    with _session() as db:
        tpl_after = db.execute(
            select(WorkoutTemplate.slug, WorkoutTemplate.name, WorkoutTemplate.catalog_section)
            .where(WorkoutTemplate.id == tid)
        ).one()
        prog_after = db.execute(
            select(UserProgram.status, UserProgram.current_version).where(
                UserProgram.id == pid
            )
        ).one()
        assert tpl_after == tpl_before  # WorkoutTemplate unchanged
        assert prog_after == prog_before  # UserProgram status/version unchanged


def test_start_unauthenticated_redirects(client):
    pid = _make_published_http("start-auth")
    with _session() as db:
        sid = _session_ids(db, pid)[0]
    client.cookies.clear()
    r = client.post(f"/programs/{pid}/sessions/{sid}/start", follow_redirects=False)
    assert r.headers["location"] == "/login"


# ─────────────────────── create_session guard + /library exclusion ───────────────────────


def test_create_session_owned_user_template_ok(client):
    from app.models.catalog import WorkoutTemplate
    from app.models.user_program import UserProgramSession

    pid = _make_published_http("cs-owned")
    with _session() as db:
        tid = db.execute(
            select(UserProgramSession.published_template_id)
            .where(UserProgramSession.user_program_id == pid)
            .limit(1)
        ).scalar_one()
        slug = db.execute(
            select(WorkoutTemplate.slug).where(WorkoutTemplate.id == tid)
        ).scalar_one()

    r = client.post(
        "/sessions", data={"template_slug": slug}, follow_redirects=False
    )
    assert r.status_code == 303  # owner can launch own custom template by slug


def test_create_session_foreign_user_template_is_404(client):
    from app.models.catalog import WorkoutTemplate
    from app.models.user import User
    from app.models.user_program import UserProgramSession
    from app.services.auth import hash_password

    with _session() as db:
        other = db.execute(
            select(User).where(User.username == "cs-other")
        ).scalar_one_or_none()
        if other is None:
            other = User(username="cs-other", password_hash=hash_password("x"))
            db.add(other)
            db.commit()
        foreign = _make_published(db, other.id, "cs-foreign", n_sessions=1)
        tid = db.execute(
            select(UserProgramSession.published_template_id)
            .where(UserProgramSession.user_program_id == foreign.id)
            .limit(1)
        ).scalar_one()
        slug = db.execute(
            select(WorkoutTemplate.slug).where(WorkoutTemplate.id == tid)
        ).scalar_one()

    # testuser tries to launch another user's custom template by slug -> 404 (spec 05 §14)
    assert client.post("/sessions", data={"template_slug": slug}).status_code == 404


def test_create_session_system_template_still_ok(client):
    with _session() as db:
        slug = _a_system_slug(db)
    r = client.post(
        "/sessions", data={"template_slug": slug}, follow_redirects=False
    )
    assert r.status_code == 303  # system templates remain launchable by all


def test_library_excludes_user_templates(client):
    uid = _uid()
    _make_published_http("libx")
    r = client.get("/library")
    assert r.status_code == 200
    assert f"up{uid}-libx" not in r.text
    with _session() as db:
        assert _a_system_slug(db) in r.text


def test_library_slug_user_template_404(client):
    uid = _uid()
    _make_published_http("libd")
    assert client.get(f"/library/up{uid}-libd-v1-s1").status_code == 404
