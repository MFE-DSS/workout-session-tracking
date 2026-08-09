"""Sb_CUSTOM_PROGRAM_DOGFOOD_01 — UX frictions fixed during the lifecycle dogfood.

Pins two owner-facing frictions found while walking the full Custom Program journey:

F1 — the lifecycle badge rendered the raw DB status (`draft`/`validated`/`published`)
     in an otherwise French UI. It now renders a French label via the shared
     `user_programs/_status.html` macro on every custom-program surface.
F2 — after publishing, the publish page explained the sessions were launchable but
     offered no way to reach them; it now shows a direct "Voir et démarrer mes séances"
     CTA to the program page where the launch buttons live.
"""
from __future__ import annotations

from sqlalchemy import select

# ─────────────────────────────── helpers ───────────────────────────────


def _uid_in(db) -> int:
    from app.models.user import User

    return db.execute(
        select(User.id).where(User.username == "testuser")
    ).scalar_one()


def _tree(n_sessions=1, ex_per=1, sets=3):
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


def _session():
    from app.database import SessionLocal

    return SessionLocal()


def _make_draft(db, uid, slug):
    from app.services.user_program_drafts import create_draft, replace_draft_tree

    program = create_draft(db, uid, f"Programme {slug}", slug)
    replace_draft_tree(db, uid, program.id, _tree())
    db.refresh(program)
    return program


def _make_validated(db, uid, slug):
    from app.services.user_program_drafts import validate_draft

    program = _make_draft(db, uid, slug)
    validate_draft(db, uid, program.id)
    db.refresh(program)
    return program


def _make_published(db, uid, slug):
    from app.services.user_program_publish import publish_user_program

    program = _make_validated(db, uid, slug)
    publish_user_program(db, uid, program.id)
    db.commit()
    db.refresh(program)
    return program


# ───────────────────────────── F1 : French labels ─────────────────────────────


def test_detail_draft_shows_french_label_not_raw(client):
    with _session() as db:
        pid = _make_draft(db, _uid_in(db), "df-draft").id
    body = client.get(f"/programs/{pid}").text
    assert "Brouillon" in body
    assert 'class="badge">draft<' not in body  # raw status never leaks in the badge


def test_detail_validated_shows_french_label(client):
    with _session() as db:
        pid = _make_validated(db, _uid_in(db), "df-val").id
    body = client.get(f"/programs/{pid}").text
    assert "Validé" in body
    assert 'class="badge">validated<' not in body


def test_detail_published_shows_french_label(client):
    with _session() as db:
        pid = _make_published(db, _uid_in(db), "df-pub").id
    body = client.get(f"/programs/{pid}").text
    assert "Publié" in body
    assert 'class="badge">published<' not in body


def test_list_shows_french_label(client):
    with _session() as db:
        _make_draft(db, _uid_in(db), "df-list")
    body = client.get("/programs").text
    assert "Brouillon" in body
    assert 'class="badge">draft<' not in body


def test_quality_page_shows_french_label(client):
    with _session() as db:
        pid = _make_draft(db, _uid_in(db), "df-qual").id
    body = client.get(f"/programs/{pid}/quality").text
    assert "Validé" not in body  # a draft is a draft
    assert "Brouillon" in body
    assert 'class="badge">draft<' not in body


# ───────────────────────────── F2 : post-publish CTA ─────────────────────────────


def test_publish_page_offers_launch_path_when_published(client):
    with _session() as db:
        pid = _make_published(db, _uid_in(db), "df-cta").id
    body = client.get(f"/programs/{pid}/publish").text
    assert "Voir et démarrer mes séances" in body  # forward CTA present
    assert f"/programs/{pid}" in body  # ...linking back to the program page


def test_publish_success_offers_launch_path(client):
    """Publishing (POST) lands on a page that routes the owner to the launch CTAs."""
    with _session() as db:
        pid = _make_validated(db, _uid_in(db), "df-cta2").id
    r = client.post(f"/programs/{pid}/publish", follow_redirects=False)
    assert r.status_code == 200  # publish renders in place (idempotent, safe to refresh)
    assert "Voir et démarrer mes séances" in r.text
    assert "Publié" in r.text  # French label on the success page too


def test_publishable_page_still_shows_definitive_warning(client):
    """The pre-publish (validated) page keeps its irreversibility warning — not removed."""
    with _session() as db:
        pid = _make_validated(db, _uid_in(db), "df-warn").id
    body = client.get(f"/programs/{pid}/publish").text
    assert "définitive" in body  # the "publication is definitive for this version" warning
    assert "Voir et démarrer mes séances" not in body  # forward CTA is published-only
