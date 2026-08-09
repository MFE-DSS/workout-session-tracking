"""Sb_CUSTOM_PROGRAM_PUBLICATION_04 — safe republication lifecycle.

Pins the full republication cycle end-to-end and its safety invariants (spec 04 §6-7 /
spec 05 publication+versioning). The cycle is:

    publish v{n}  →  PUBLICATION_02 new edit cycle (same row → draft v{n+1}, session links
    cleared)  →  edit + validate  →  publish v{n+1}

**Schema decision (recorded in the spec/report):** the required lifecycle is expressible
with ZERO schema change and NO migration. Old v{n} templates are NOT re-labelled/archived:
the only archival mechanism (`catalog_section="archived"`) is unsafe for user templates —
it would (1) expose them via `/library/{slug}` (which only 404s on `catalog_section="user"`),
(2) drop the seed wipe-guard protection (`catalog_section != "user"` rows are wiped on
reseed), and (3) overload a section reserved for system-template retirement. So old v{n}
templates stay `catalog_section="user"`: owner-private, immutable, excluded from `/library`,
and no longer owner-launchable because PUBLICATION_02 already cleared their session links.

These tests therefore lock the *behaviour*, not a new field. A regression that re-links,
deletes, mutates, or exposes old templates — or that breaks the fresh-version materialization
— fails here.
"""
from __future__ import annotations

from sqlalchemy import func, select

from app.services.user_program_launch import (
    is_owned_published_template,
    resolve_owned_published_template,
)
from app.services.user_program_publish import publish_user_program

# ─────────────────────────────── helpers ───────────────────────────────


def _uid_in(db) -> int:
    from app.models.user import User

    return db.execute(
        select(User.id).where(User.username == "testuser")
    ).scalar_one()


def _tree(names, sets=3):
    """One session per entry in `names`; each entry is a list of exercise names."""
    return [
        {
            "position": s,
            "name": f"Séance {s}",
            "exercises": [
                {
                    "position": e,
                    "exercise_name": name,
                    "set_scheme": f"{sets}x 8-12",
                    "rep_targets": [
                        {"min_reps": 8, "max_reps": 12} for _ in range(sets)
                    ],
                }
                for e, name in enumerate(session_names, start=1)
            ],
        }
        for s, session_names in enumerate(names, start=1)
    ]


def _make_validated(db, uid, slug, tree):
    from app.services.user_program_drafts import (
        create_draft,
        replace_draft_tree,
        validate_draft,
    )

    program = create_draft(db, uid, f"Programme {slug}", slug)
    replace_draft_tree(db, uid, program.id, tree)
    validate_draft(db, uid, program.id)
    db.refresh(program)
    return program


def _revalidate_with_tree(db, uid, program_id, tree):
    """Edit an already-draft program's tree and re-validate (the v{n+1} edit step)."""
    from app.services.user_program_drafts import replace_draft_tree, validate_draft

    replace_draft_tree(db, uid, program_id, tree)
    validate_draft(db, uid, program_id)


def _session_ids(db, program_id):
    from app.models.user_program import UserProgramSession

    return list(
        db.execute(
            select(UserProgramSession.id)
            .where(UserProgramSession.user_program_id == program_id)
            .order_by(UserProgramSession.position)
        ).scalars()
    )


def _linked_template_ids(db, program_id):
    from app.models.user_program import UserProgramSession

    return list(
        db.execute(
            select(UserProgramSession.published_template_id)
            .where(UserProgramSession.user_program_id == program_id)
            .order_by(UserProgramSession.position)
        ).scalars()
    )


def _snapshot_template(db, template_id):
    """Deep, order-stable snapshot of a template's identity + full exercise tree."""
    from app.models.catalog import RepTarget, TemplateExercise, WorkoutTemplate

    tpl = db.get(WorkoutTemplate, template_id)
    if tpl is None:
        return None
    exercises = db.execute(
        select(TemplateExercise)
        .where(TemplateExercise.template_id == template_id)
        .order_by(TemplateExercise.position)
    ).scalars().all()
    tree = []
    for te in exercises:
        reps = db.execute(
            select(RepTarget.set_index, RepTarget.min_reps, RepTarget.max_reps)
            .where(RepTarget.template_exercise_id == te.id)
            .order_by(RepTarget.set_index)
        ).all()
        tree.append((te.position, te.code, te.name, te.set_scheme, tuple(reps)))
    return (tpl.slug, tpl.name, tpl.catalog_section, tpl.display_order, tuple(tree))


def _review_count(db, program_id) -> int:
    from app.models.user_program import UserProgramQualityReview

    return db.execute(
        select(func.count()).select_from(UserProgramQualityReview).where(
            UserProgramQualityReview.user_program_id == program_id
        )
    ).scalar_one()


def _template_count(db) -> int:
    from app.models.catalog import WorkoutTemplate

    return db.execute(
        select(func.count()).select_from(WorkoutTemplate)
    ).scalar_one()


def _a_system_slug(db) -> str:
    from app.models.catalog import WorkoutTemplate

    return db.execute(
        select(WorkoutTemplate.slug)
        .where(WorkoutTemplate.catalog_section.notin_(["user", "archived"]))
        .limit(1)
    ).scalar_one()


def _publish(db, uid, program_id):
    result = publish_user_program(db, uid, program_id)
    db.commit()
    return result


def _new_cycle(db, uid, program_id):
    from app.services.user_program_versioning import start_new_edit_cycle

    result = start_new_edit_cycle(db, uid, program_id)
    db.commit()
    return result


# ─────────────────── full-cycle fixtures built inline per test ───────────────────

_V1_TREE = [["Exercice A1", "Exercice A2"], ["Exercice B1"]]  # 2 sessions
_V2_TREE = [["Exercice A1 MODIFIÉ", "Exercice A2"], ["Exercice B1"]]  # s1e1 edited


def _publish_v1(db, uid, slug):
    program = _make_validated(db, uid, slug, _tree(_V1_TREE))
    res = _publish(db, uid, program.id)
    return program.id, [t.id for t in res.templates]


def _republish_v2(db, uid, program_id, tree=None):
    _new_cycle(db, uid, program_id)
    _revalidate_with_tree(db, uid, program_id, _tree(tree or _V2_TREE))
    res = _publish(db, uid, program_id)
    return [t.id for t in res.templates]


# ─────────────────────────────── tests ───────────────────────────────


def test_republish_v2_creates_new_v2_templates(client):
    from app.database import SessionLocal
    from app.models.catalog import WorkoutTemplate

    with SessionLocal() as db:
        uid = _uid_in(db)
        pid, v1_ids = _publish_v1(db, uid, "rep-a")
        v2_ids = _republish_v2(db, uid, pid)

        assert set(v1_ids).isdisjoint(v2_ids)  # brand-new rows, not reused
        for pos, tid in enumerate(v2_ids, start=1):
            tpl = db.get(WorkoutTemplate, tid)
            assert tpl.slug == f"up{uid}-rep-a-v2-s{pos}"  # version bumped in slug
            assert tpl.catalog_section == "user"


def test_old_v1_templates_are_not_deleted(client):
    from app.database import SessionLocal
    from app.models.catalog import WorkoutTemplate

    with SessionLocal() as db:
        uid = _uid_in(db)
        pid, v1_ids = _publish_v1(db, uid, "rep-keep")
        _republish_v2(db, uid, pid)
        for tid in v1_ids:
            assert db.get(WorkoutTemplate, tid) is not None  # preserved, not deleted


def test_old_v1_template_content_is_unchanged(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid_in(db)
        pid, v1_ids = _publish_v1(db, uid, "rep-immut")
        before = [_snapshot_template(db, tid) for tid in v1_ids]

        v2_ids = _republish_v2(db, uid, pid)  # edits s1e1 name in v2
        after = [_snapshot_template(db, tid) for tid in v1_ids]
        assert after == before  # old v1 content byte-identical

        # ...and the edit landed on the NEW v2 template, not the old one.
        v2_first = _snapshot_template(db, v2_ids[0])
        assert any("MODIFIÉ" in ex[2] for ex in v2_first[4])
        assert all("MODIFIÉ" not in ex[2] for ex in before[0][4])


def test_old_v1_not_launchable_through_current_program(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid_in(db)
        pid, v1_ids = _publish_v1(db, uid, "rep-nolaunch")
        v1_slugs = [_snapshot_template(db, tid)[0] for tid in v1_ids]
        _republish_v2(db, uid, pid)

        for tid in v1_ids:
            assert is_owned_published_template(db, uid, tid) is False  # no session links here

    # by slug, create_session must 404 for the now-orphaned v1 templates
    for slug in v1_slugs:
        assert client.post("/sessions", data={"template_slug": slug}).status_code == 404


def test_current_program_links_only_to_v2(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid_in(db)
        pid, v1_ids = _publish_v1(db, uid, "rep-links")
        v2_ids = _republish_v2(db, uid, pid)

        linked = _linked_template_ids(db, pid)
        assert set(linked) == set(v2_ids)  # every session points at a v2 template
        assert set(linked).isdisjoint(v1_ids)  # none point at v1 anymore

        # resolve_owned_published_template (PUBLICATION_03) yields the v2 template
        for sid in _session_ids(db, pid):
            tpl = resolve_owned_published_template(db, uid, pid, sid)
            assert tpl.id in v2_ids


def test_v2_templates_are_launchable_by_owner(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid_in(db)
        pid, _ = _publish_v1(db, uid, "rep-v2launch")
        _republish_v2(db, uid, pid)
        sid = _session_ids(db, pid)[0]

    r = client.post(f"/programs/{pid}/sessions/{sid}/start", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"].startswith("/sessions/")


def test_library_still_excludes_user_templates(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid_in(db)
        pid, v1_ids = _publish_v1(db, uid, "rep-lib")
        v2_ids = _republish_v2(db, uid, pid)
        v1_slugs = [_snapshot_template(db, t)[0] for t in v1_ids]
        v2_slugs = [_snapshot_template(db, t)[0] for t in v2_ids]
        sys_slug = _a_system_slug(db)

    listing = client.get("/library")
    assert listing.status_code == 200
    for slug in v1_slugs + v2_slugs:
        assert slug not in listing.text  # neither old nor new user templates listed
        assert client.get(f"/library/{slug}").status_code == 404  # nor reachable by slug
    assert sys_slug in listing.text  # system catalog still shown


def test_foreign_user_still_gets_404_on_republished_program(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.auth import hash_password

    with SessionLocal() as db:
        other = db.execute(
            select(User).where(User.username == "rep-foreign")
        ).scalar_one_or_none()
        if other is None:
            other = User(username="rep-foreign", password_hash=hash_password("x"))
            db.add(other)
            db.commit()
        pid, _ = _publish_v1(db, other.id, "rep-foreign-prog")
        _republish_v2(db, other.id, pid)
        sid = _session_ids(db, pid)[0]

    # testuser (the client) is not the owner → indistinct 404
    assert client.post(f"/programs/{pid}/sessions/{sid}/start").status_code == 404


def test_system_templates_unaffected_by_republication(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid_in(db)
        pid, _ = _publish_v1(db, uid, "rep-sys")
        _republish_v2(db, uid, pid)
        sys_slug = _a_system_slug(db)

    assert client.get(f"/library/{sys_slug}").status_code == 200  # still viewable by slug
    r = client.post("/sessions", data={"template_slug": sys_slug}, follow_redirects=False)
    assert r.status_code == 303  # still launchable by anyone


def test_republish_is_idempotent_no_duplicate(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid_in(db)
        pid, _ = _publish_v1(db, uid, "rep-idem")
        v2_ids = _republish_v2(db, uid, pid)

        count_before = _template_count(db)
        # re-publishing an already-published v2 returns the existing templates
        again = publish_user_program(db, uid, pid)
        db.commit()
        assert again.created is False
        assert {t.id for t in again.templates} == set(v2_ids)
        assert _template_count(db) == count_before  # zero duplicates created


def test_no_quality_write_outside_publication_freeze(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        uid = _uid_in(db)
        pid, _ = _publish_v1(db, uid, "rep-quality")
        assert _review_count(db, pid) == 1  # v1 freeze

        _new_cycle(db, uid, pid)
        assert _review_count(db, pid) == 1  # new edit cycle writes NOTHING

        _revalidate_with_tree(db, uid, pid, _tree(_V2_TREE))
        db.commit()
        assert _review_count(db, pid) == 1  # editing/validating writes NOTHING

        publish_user_program(db, uid, pid)
        db.commit()
        assert _review_count(db, pid) == 2  # v2 freeze — exactly one per version

        # idempotent re-publish writes nothing more
        publish_user_program(db, uid, pid)
        db.commit()
        assert _review_count(db, pid) == 2
