"""Sb_MORPHO_DOGFOOD_01 — the generated morphology program through the REAL Custom Program cycle.

Final build of `Sx_MORPHO_PROGRAM_01`. Proves Martin's deterministic generated program can enter
the existing lifecycle — draft → validate → quality preview → publish → launchable session —
**without changing any lifecycle semantics**, and without leaking a private user program into the
public catalog or `/library`.

Everything Martin-specific stays in the private test-only fixture (`tests/fixtures/dogfood/`).
No production data, no photo, no medical claim, no new lifecycle state, no migration.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

from sqlalchemy import func, select

# PURE modules are imported at module level, like the sibling pure test files. The `client`
# fixture purges every `app.*` entry from `sys.modules`, so a function-local import of a pure
# module could rebind it to a SECOND module object (or fail outright) once another test in the
# same xdist worker has purged. Importing here keeps one identity, shared with the fixture below.
# DB/lifecycle services stay function-local on purpose: they MUST be re-imported after a purge.
from app.services import morpho_program_draft_mapper as MAPPER  # noqa: E402
from app.services import morpho_program_generator as GEN  # noqa: E402

_ROOT = pathlib.Path(__file__).resolve().parent.parent
_FIXTURE_DIR = _ROOT / "tests" / "fixtures" / "dogfood"
sys.path.insert(0, str(_FIXTURE_DIR))
import martin_program  # noqa: E402

_DATA = _ROOT / "data"

# Pinned deterministic identity of Martin's generated program (content-addressed).
MARTIN_FINGERPRINT = "mpg1-eadcab6e2d104c45"
EXPECTED_EXERCISE_COUNT = 8

# intent_id -> position of its counterpart in the merged catalog program (E1-E8), the declared
# source of each intent's volume prescription.
INTENT_TO_CATALOG_POSITION = {
    "upper_chest_primary_press": 1,
    "upper_back_depth_row": 2,
    "quad_minimum_effective_dose": 3,
    "posterior_chain_hinge": 4,
    "lateral_delt_priority": 5,
    "rear_delt_upper_back_accessory": 6,
    "calves_gastrocnemius_priority": 7,
    "calves_soleus_priority": 8,
}


def _sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _session():
    from app.database import SessionLocal

    return SessionLocal()


def _uid(db) -> int:
    from app.models.user import User

    return db.execute(select(User.id).where(User.username == "testuser")).scalar_one()


def _other_uid(db) -> int:
    from app.models.user import User
    from app.services.auth import hash_password

    other = db.execute(
        select(User).where(User.username == "morpho-other")
    ).scalar_one_or_none()
    if other is None:
        other = User(username="morpho-other", password_hash=hash_password("x"))
        db.add(other)
        db.commit()
    return other.id


def _make_martin_draft(db, uid, slug=None):
    """Drive the EXISTING draft services with the mapped generated tree (no bypass)."""
    from app.services.user_program_drafts import create_draft, replace_draft_tree

    program = create_draft(
        db, uid, martin_program.MARTIN_PROGRAM_TITLE, slug or martin_program.MARTIN_PROGRAM_SLUG
    )
    replace_draft_tree(db, uid, program.id, martin_program.martin_draft_tree())
    db.refresh(program)
    return program


def _make_martin_validated(db, uid, slug=None):
    from app.services.user_program_drafts import validate_draft

    program = _make_martin_draft(db, uid, slug)
    validate_draft(db, uid, program.id)
    db.refresh(program)
    return program


def _make_martin_published(db, uid, slug=None):
    from app.services.user_program_publish import publish_user_program

    program = _make_martin_validated(db, uid, slug)
    publish_user_program(db, uid, program.id)
    db.refresh(program)
    return program


# ─────────────────── the generated program itself (pinned) ───────────────────


def test_martin_generated_program_is_pinned_and_complete():
    """The dogfood input is the known deterministic result: 8/8 filled, distinct, 0 warning."""
    program = martin_program.martin_program()
    assert program.generated_program_id == MARTIN_FINGERPRINT
    assert len(program.selections) == EXPECTED_EXERCISE_COUNT
    assert program.warnings == ()
    picks = [s.preferred_exercise for s in program.selections]
    assert all(picks)
    assert len(set(picks)) == EXPECTED_EXERCISE_COUNT


# ─────────────────── mapper: GeneratedProgram → draft tree ───────────────────


def test_mapper_payload_is_replace_draft_tree_compatible():
    """Same contract test as the existing reference_split generator (shape compatibility)."""
    tree = martin_program.martin_draft_tree()
    for session in tree:
        assert {"position", "name", "exercises"} <= set(session)
        for exercise in session["exercises"]:
            assert {"position", "exercise_name", "set_scheme", "rep_targets"} <= set(exercise)


def test_mapper_preserves_all_eight_exercises_in_slot_order():
    program = martin_program.martin_program()
    tree = martin_program.martin_draft_tree()
    assert len(tree) == 1  # smallest valid structure: one full-body session
    names = [e["exercise_name"] for e in tree[0]["exercises"]]
    assert names == [s.preferred_exercise for s in MAPPER.mapped_selections(program)]
    assert len(names) == EXPECTED_EXERCISE_COUNT
    positions = [e["position"] for e in tree[0]["exercises"]]
    assert positions == list(range(1, EXPECTED_EXERCISE_COUNT + 1))


def test_mapper_carries_intent_traceability_and_rationale():
    program = martin_program.martin_program()
    by_name = {s.preferred_exercise: s for s in program.selections}
    for exercise in martin_program.martin_draft_tree()[0]["exercises"]:
        selection = by_name[exercise["exercise_name"]]
        assert exercise["source_reason"] == f"generated:morpho:{selection.intent_id}"
        assert exercise["notes"] == selection.rationale
        assert len(exercise["source_reason"]) <= 255


def test_mapper_set_scheme_matches_rep_target_count():
    for exercise in martin_program.martin_draft_tree()[0]["exercises"]:
        declared_sets = int(exercise["set_scheme"].split("x")[0])
        assert len(exercise["rep_targets"]) == declared_sets


def test_prescriptions_match_the_catalog_program():
    """Each intent's volume is the one prescribed by its counterpart (E1-E8) in the merged
    « Full Body — Morphotype Priority » catalog program — pinned against reference_split.json."""
    catalog = json.loads((_DATA / "reference_split.json").read_text(encoding="utf-8"))
    template = next(
        t for t in catalog["templates"] if t["slug"] == "full-body-morphotype-priority-v1"
    )
    by_position = {e["position"]: e for e in template["exercises"]}
    for intent_id, position in INTENT_TO_CATALOG_POSITION.items():
        entry = by_position[position]
        sets, min_reps, max_reps = MAPPER._INTENT_PRESCRIPTION[intent_id]
        assert len(entry["rep_targets"]) == sets
        assert entry["rep_targets"][0]["min_reps"] == min_reps
        assert entry["rep_targets"][0]["max_reps"] == max_reps


def test_mapper_drops_slots_without_exercise_instead_of_faking_one():
    """A gap slot yields no exercise (exercise_name is NOT NULL) and is reported, never invented."""
    starved = GEN.generate_program(
        priorities=[("calves", 1)],
        pool={
            "CalfX": {
                "pattern_motor": "isolation_lower", "zone_primary": "lower",
                "muscle_group": "calves", "equipment_family": "machine", "chain": "isolation",
            }
        },
    )
    tree = MAPPER.generated_program_to_draft_tree(starved)
    assert len(tree[0]["exercises"]) == 1
    dropped = MAPPER.unmappable_slots(starved)
    assert len(dropped) == 1
    assert "distinctness gap" in dropped[0][1]


def test_mapper_writes_nothing_and_mutates_no_data_file():
    files = [
        _DATA / "reference_split.json",
        _DATA / "exercise_properties.json",
        _DATA / "exercise_knowledge_base.json",
    ]
    before = [_sha(f) for f in files]
    martin_program.martin_draft_tree()
    assert [_sha(f) for f in files] == before


# ─────────────────── lifecycle: draft → validate ───────────────────


def test_generated_program_maps_to_a_valid_draft(client):
    from app.services.user_program_drafts import validate_draft

    with _session() as db:
        uid = _uid(db)
        program = _make_martin_draft(db, uid)
        assert program.status == "draft"
        assert len(program.sessions) == 1
        assert len(program.sessions[0].exercises) == EXPECTED_EXERCISE_COUNT

        validated = validate_draft(db, uid, program.id)
        assert validated.status == "validated"


def test_draft_keeps_exercise_identity_and_order_through_the_services(client):
    with _session() as db:
        program = _make_martin_draft(db, _uid(db))
        stored = [(e.position, e.exercise_name) for e in program.sessions[0].exercises]
        expected = [
            (e["position"], e["exercise_name"])
            for e in martin_program.martin_draft_tree()[0]["exercises"]
        ]
        assert stored == expected


def test_draft_persists_intent_traceability(client):
    with _session() as db:
        program = _make_martin_draft(db, _uid(db))
        for exercise in program.sessions[0].exercises:
            assert exercise.source_reason.startswith("generated:morpho:")


# ─────────────────── lifecycle: quality preview (zero write) ───────────────────


def test_quality_preview_works_and_writes_nothing(client):
    from app.models.user_program import UserProgramQualityReview
    from app.services.user_program_quality_preview import compute_quality_preview

    with _session() as db:
        uid = _uid(db)
        program = _make_martin_draft(db, uid)
        before = db.execute(
            select(func.count()).select_from(UserProgramQualityReview)
        ).scalar_one()

        preview = compute_quality_preview(program)
        assert preview.result is not None
        assert preview.feedback is not None

        after = db.execute(
            select(func.count()).select_from(UserProgramQualityReview)
        ).scalar_one()
        assert after == before


# ─────────────────── lifecycle: publication (freeze unchanged) ───────────────────


def test_publication_uses_existing_behaviour_and_freezes_the_session(client):
    from app.models.catalog import WorkoutTemplate
    from app.services.seed import CUSTOM_CATALOG_SECTION
    from app.services.user_program_publish import publish_user_program

    with _session() as db:
        uid = _uid(db)
        program = _make_martin_validated(db, uid)
        result = publish_user_program(db, uid, program.id)

        assert result.created is True
        assert len(result.templates) == 1  # one session -> one template
        db.refresh(program)
        assert program.status == "published"

        session = program.sessions[0]
        assert session.published_template_id is not None
        assert session.template_slug_snapshot is not None

        template = db.get(WorkoutTemplate, session.published_template_id)
        assert template.catalog_section == CUSTOM_CATALOG_SECTION
        codes = [e.code for e in sorted(template.exercises, key=lambda e: e.position)]
        assert codes == [f"E{i}" for i in range(1, EXPECTED_EXERCISE_COUNT + 1)]


def test_publication_preserves_the_eight_generated_exercises(client):
    from app.models.catalog import WorkoutTemplate

    with _session() as db:
        uid = _uid(db)
        program = _make_martin_published(db, uid)
        template = db.get(WorkoutTemplate, program.sessions[0].published_template_id)
        published = [
            e.name for e in sorted(template.exercises, key=lambda e: e.position)
        ]
        generated = [
            e["exercise_name"] for e in martin_program.martin_draft_tree()[0]["exercises"]
        ]
        assert published == generated


def test_publication_writes_exactly_one_quality_review(client):
    from app.models.user_program import UserProgramQualityReview

    with _session() as db:
        uid = _uid(db)
        program = _make_martin_published(db, uid)
        count = db.execute(
            select(func.count())
            .select_from(UserProgramQualityReview)
            .where(UserProgramQualityReview.user_program_id == program.id)
        ).scalar_one()
        assert count == 1


def test_draft_publication_is_still_refused(client):
    """Non-regression: the generated program does not get a shortcut around validation."""
    from app.services.user_program_publish import PublishRefused, publish_user_program

    with _session() as db:
        uid = _uid(db)
        program = _make_martin_draft(db, uid, slug="martin-morpho-refused")
        try:
            publish_user_program(db, uid, program.id)
            raised = False
        except PublishRefused:
            raised = True
        assert raised is True


# ─────────────────── lifecycle: launch by owner ───────────────────


def test_owner_can_launch_the_published_dogfood_session(client):
    with _session() as db:
        uid = _uid(db)
        program = _make_martin_published(db, uid)
        pid = program.id
        sid = program.sessions[0].id

    response = client.post(f"/programs/{pid}/sessions/{sid}/start", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"].startswith("/sessions/")


def test_launch_is_refused_for_a_non_owner(client):
    from app.services.user_program_launch import LaunchNotFound, resolve_owned_published_template

    with _session() as db:
        uid = _uid(db)
        program = _make_martin_published(db, uid, slug="martin-morpho-owner")
        other = _other_uid(db)
        try:
            resolve_owned_published_template(db, other, program.id, program.sessions[0].id)
            raised = False
        except LaunchNotFound:
            raised = True
        assert raised is True


# ─────────────────── privacy: no catalog / no /library exposure ───────────────────


def test_library_does_not_expose_the_dogfood_program(client):
    with _session() as db:
        uid = _uid(db)
        _make_martin_published(db, uid, slug="martin-morpho-lib")

    response = client.get("/library")
    assert response.status_code == 200
    assert "martin-morpho-lib" not in response.text
    assert martin_program.MARTIN_PROGRAM_TITLE not in response.text


def test_library_slug_detail_is_404_for_the_dogfood_template(client):
    with _session() as db:
        uid = _uid(db)
        program = _make_martin_published(db, uid, slug="martin-morpho-slug")
        slug = program.sessions[0].template_slug_snapshot

    assert client.get(f"/library/{slug}").status_code == 404


def test_dogfood_publication_creates_no_global_catalog_template(client):
    """Only `catalog_section="user"` templates appear; the public catalog is untouched."""
    from app.models.catalog import WorkoutTemplate
    from app.services.seed import CUSTOM_CATALOG_SECTION

    with _session() as db:
        uid = _uid(db)
        before = db.execute(
            select(func.count())
            .select_from(WorkoutTemplate)
            .where(WorkoutTemplate.catalog_section != CUSTOM_CATALOG_SECTION)
        ).scalar_one()

        _make_martin_published(db, uid, slug="martin-morpho-global")

        after = db.execute(
            select(func.count())
            .select_from(WorkoutTemplate)
            .where(WorkoutTemplate.catalog_section != CUSTOM_CATALOG_SECTION)
        ).scalar_one()
        assert after == before


def test_martin_identity_lives_only_in_the_private_fixture():
    """No operator identity value leaks into shipped code — only into the test-only fixture."""
    assert "private" in martin_program.MARTIN_PROGRAM_SOURCE.lower()
    assert "tests/fixtures/dogfood" in martin_program.__file__.replace("\\", "/")

    shipped = (_ROOT / "app" / "services" / "morpho_program_draft_mapper.py").read_text(
        encoding="utf-8"
    )
    for private_value in (
        martin_program.MARTIN_PROGRAM_TITLE,
        martin_program.MARTIN_PROGRAM_SLUG,
        martin_program.MARTIN_SESSION_FOCUS,
        martin_program.MARTIN_PROGRAM_SOURCE,
    ):
        assert private_value not in shipped


# ─────────────────── non-regression: versioning / republication ───────────────────


def test_new_edit_cycle_and_republication_stay_unchanged(client):
    from app.services.user_program_publish import publish_user_program
    from app.services.user_program_versioning import start_new_edit_cycle

    with _session() as db:
        uid = _uid(db)
        program = _make_martin_published(db, uid, slug="martin-morpho-v2")
        pid = program.id

        cycle = start_new_edit_cycle(db, uid, pid)
        assert cycle.incremented is True
        db.refresh(program)
        assert program.status == "draft"
        assert program.current_version == 2
        assert program.sessions[0].published_template_id is None

        from app.services.user_program_drafts import validate_draft

        validate_draft(db, uid, pid)
        result = publish_user_program(db, uid, pid)
        assert result.created is True
        db.refresh(program)
        assert program.sessions[0].template_slug_snapshot.endswith("-v2-s1")


def test_full_cycle_mutates_no_generator_or_catalog_data(client):
    files = [
        _DATA / "reference_split.json",
        _DATA / "exercise_properties.json",
        _DATA / "exercise_knowledge_base.json",
    ]
    before = [_sha(f) for f in files]
    with _session() as db:
        _make_martin_published(db, _uid(db), slug="martin-morpho-nomut")
    assert [_sha(f) for f in files] == before
