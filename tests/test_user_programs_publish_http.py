"""Sb_CUSTOM_PROGRAM_PUBLICATION_01 — HTTP tests for program publication.

Uses the authenticated `client` fixture (conftest logs in `testuser`). Pins
auth, owner-scope with no existence leak, the SSR confirmation page, the
validated→published POST, the soft draft/archived refusals, idempotence, the
detail CTA, and the shared `/library` exclusion of `catalog_section="user"`.
Every `app.*` import is inside the test/helper (conftest resets the `app`
module tree per test).
"""
from __future__ import annotations

from sqlalchemy import func, select

# ─────────────────────────── helpers ───────────────────────────


def _session():
    from app.database import SessionLocal

    return SessionLocal()


def _uid_in(db) -> int:
    from app.models.user import User

    return db.execute(
        select(User.id).where(User.username == "testuser")
    ).scalar_one()


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


def _make_draft(slug: str) -> int:
    from app.services.user_program_drafts import create_draft

    with _session() as db:
        return create_draft(db, _uid_in(db), f"Programme {slug}", slug).id


def _make_validated(slug: str, *, n_sessions: int = 2, ex_per: int = 2) -> int:
    from app.services.user_program_drafts import (
        create_draft,
        replace_draft_tree,
        validate_draft,
    )

    with _session() as db:
        uid = _uid_in(db)
        pid = create_draft(db, uid, f"Programme {slug}", slug).id
        replace_draft_tree(db, uid, pid, _tree(n_sessions, ex_per))
        validate_draft(db, uid, pid)
        return pid


def _make_other_validated(slug: str) -> int:
    from app.models.user import User
    from app.services.auth import hash_password
    from app.services.user_program_drafts import (
        create_draft,
        replace_draft_tree,
        validate_draft,
    )

    with _session() as db:
        other = db.execute(
            select(User).where(User.username == "pub-other")
        ).scalar_one_or_none()
        if other is None:
            other = User(username="pub-other", password_hash=hash_password("x"))
            db.add(other)
            db.commit()
        pid = create_draft(db, other.id, f"Programme {slug}", slug).id
        replace_draft_tree(db, other.id, pid, _tree(1, 1))
        validate_draft(db, other.id, pid)
        return pid


def _archive(pid: int) -> None:
    from app.services.user_program_drafts import archive_draft

    with _session() as db:
        archive_draft(db, _uid_in(db), pid)


def _user_template_count() -> int:
    from app.models.catalog import WorkoutTemplate

    with _session() as db:
        return db.execute(
            select(func.count())
            .select_from(WorkoutTemplate)
            .where(WorkoutTemplate.catalog_section == "user")
        ).scalar_one()


def _program_status(pid: int) -> str:
    from app.models.user_program import UserProgram

    with _session() as db:
        return db.execute(
            select(UserProgram.status).where(UserProgram.id == pid)
        ).scalar_one()


def _a_system_slug() -> str:
    from app.models.catalog import WorkoutTemplate

    with _session() as db:
        return db.execute(
            select(WorkoutTemplate.slug)
            .where(WorkoutTemplate.catalog_section.notin_(["user", "archived"]))
            .limit(1)
        ).scalar_one()


def _uid() -> int:
    with _session() as db:
        return _uid_in(db)


# ─────────────────────────── auth ───────────────────────────


def test_get_publish_unauthenticated_redirects(client):
    pid = _make_validated("pub-auth-g")
    client.cookies.clear()
    r = client.get(f"/programs/{pid}/publish", follow_redirects=False)
    assert r.headers["location"] == "/login"


def test_post_publish_unauthenticated_redirects(client):
    pid = _make_validated("pub-auth-p")
    client.cookies.clear()
    r = client.post(f"/programs/{pid}/publish", follow_redirects=False)
    assert r.headers["location"] == "/login"


# ─────────────────────────── GET confirmation page ───────────────────────────


def test_get_publish_validated_shows_summary(client):
    uid = _uid()
    pid = _make_validated("pub-summary", n_sessions=2)
    r = client.get(f"/programs/{pid}/publish")
    assert r.status_code == 200
    assert "2 modèle" in r.text or "2 séance" in r.text  # session count surfaced
    assert f"up{uid}-pub-summary-v1-s1" in r.text  # future slug preview
    assert "définitive" in r.text  # immutable-publication warning
    assert "Publier" in r.text


def test_get_publish_foreign_and_missing_are_404(client):
    foreign = _make_other_validated("pub-foreign-get")
    assert client.get(f"/programs/{foreign}/publish").status_code == 404
    assert client.get("/programs/999999/publish").status_code == 404


# ─────────────────────────── POST publication ───────────────────────────


def test_post_publish_validated_creates_templates(client):
    pid = _make_validated("pub-go", n_sessions=3)
    assert _user_template_count() == 0
    r = client.post(f"/programs/{pid}/publish")
    assert r.status_code == 200
    assert "publié" in r.text
    assert _user_template_count() == 3
    assert _program_status(pid) == "published"


def test_post_publish_draft_is_soft_refusal_no_template(client):
    pid = _make_draft("pub-draft")
    r = client.post(f"/programs/{pid}/publish")
    assert r.status_code == 200
    assert "Validez" in r.text or "validé" in r.text
    assert _user_template_count() == 0
    assert _program_status(pid) == "draft"


def test_post_publish_archived_is_soft_refusal_no_template(client):
    pid = _make_validated("pub-arch")
    _archive(pid)
    r = client.post(f"/programs/{pid}/publish")
    assert r.status_code == 200
    assert "archiv" in r.text
    assert _user_template_count() == 0


def test_post_publish_is_idempotent_no_duplicate(client):
    pid = _make_validated("pub-idem", n_sessions=2)
    client.post(f"/programs/{pid}/publish")
    assert _user_template_count() == 2
    r2 = client.post(f"/programs/{pid}/publish")
    assert r2.status_code == 200
    assert _user_template_count() == 2  # no duplicate on re-submit
    assert "déjà publié" in r2.text


def test_post_publish_foreign_is_404(client):
    foreign = _make_other_validated("pub-foreign-post")
    r = client.post(f"/programs/{foreign}/publish")
    assert r.status_code == 404
    assert _user_template_count() == 0


# ─────────────────────────── detail CTA + /library exclusion ───────────────────


def test_detail_shows_publish_cta_for_validated(client):
    pid = _make_validated("pub-cta")
    r = client.get(f"/programs/{pid}")
    assert r.status_code == 200
    assert "Publier ce programme" in r.text
    assert f"/programs/{pid}/publish" in r.text


def test_library_excludes_published_user_templates(client):
    uid = _uid()
    pid = _make_validated("pub-libx", n_sessions=2)
    client.post(f"/programs/{pid}/publish")
    assert _user_template_count() == 2

    r = client.get("/library")
    assert r.status_code == 200
    # The distinctive user slug must NOT leak into the shared catalog…
    assert f"up{uid}-pub-libx" not in r.text
    # …while the system catalog is still shown.
    assert _a_system_slug() in r.text


def test_library_slug_detail_404_for_user_template(client):
    uid = _uid()
    pid = _make_validated("pub-libd", n_sessions=1)
    client.post(f"/programs/{pid}/publish")
    r = client.get(f"/library/up{uid}-pub-libd-v1-s1")
    assert r.status_code == 404
