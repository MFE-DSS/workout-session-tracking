"""Owned library projections preserve publication, planned facts and read identity."""

from __future__ import annotations

import pytest
from sqlalchemy import select


@pytest.fixture(name="library")
def library_source(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services import library_read_model as service

    with SessionLocal() as db:
        owner = db.scalar(select(User).where(User.username == "testuser"))
        ctx = service.LibraryContext(
            owner.id, "synthetic-library-tests", "k" * 40, owner.session_epoch
        )
        yield service, db, ctx


def template(db, slug, *, kind="strength", section="utility", sets=2):
    from app.models.catalog import RepTarget, TemplateExercise, WorkoutTemplate

    row = WorkoutTemplate(slug=slug, name=slug, kind=kind, catalog_section=section)
    if sets:
        ex = TemplateExercise(
            position=1, code="QA", name="Synthetic unmapped exercise", set_scheme="2 x 8–12"
        )
        ex.rep_targets = [RepTarget(set_index=i + 1, min_reps=8, max_reps=12) for i in range(sets)]
        row.exercises = [ex]
    db.add(row)
    db.commit()
    return row


def entry(service, db, ctx, name):
    page = service.read_library(db, ctx, limit=100)
    return next(row for row in page["entries"] if row["name"] == name)


def test_catalogue_excludes_personal_and_archived_templates(library):
    s, db, ctx = library
    template(db, "qa-visible")
    template(db, "qa-archived", section="archived")
    template(db, "qa-personal-materialization", section="user")
    page = s.read_library(db, ctx, limit=100)
    names = [r["name"] for r in page["entries"]]
    assert "qa-visible" in names
    assert "qa-archived" not in names
    assert "qa-personal-materialization" not in names
    row = entry(s, db, ctx, "qa-visible")
    assert row["counts"] == {
        "sessions": 1,
        "exercise_slots": 1,
        "prescribed_sets": 2,
        "count_state": "KNOWN",
    }
    assert row["zones"]["state"] == "ZONES_UNKNOWN"


def test_detail_is_planned_source_not_performed_or_external_mass(library):
    s, db, ctx = library
    template(db, "qa-strength")
    row = entry(s, db, ctx, "qa-strength")
    detail = s.read_library_item(db, ctx, row["source_ref"])
    exercise = detail["composition"][0]["exercises"][0]
    assert exercise["name"] == "Synthetic unmapped exercise"
    assert exercise["equipment_context"] == "UNKNOWN"
    assert exercise["rep_targets"][0] == {
        "set_index": 1,
        "min_reps": 8,
        "max_reps": 12,
        "technique": None,
        "is_warmup": False,
    }
    assert "weight_kg" not in exercise
    assert "completed" not in exercise
    assert detail["selection"]["native_support"]["state"] == "SUPPORTED"
    selected = s.resolve_library_selection(db, ctx, detail["selection"]["selection_ref"])
    assert selected.slug == "qa-strength"


def test_zero_set_cardio_is_readable_but_never_has_a_start_capability(library):
    s, db, ctx = library
    template(db, "qa-liss", kind="cardio", sets=0)
    detail = s.read_library_item(db, ctx, entry(s, db, ctx, "qa-liss")["source_ref"])
    assert detail["composition"][0]["exercises"] == []
    assert detail["selection"]["domain_launchable"] is True
    assert detail["selection"]["selection_ref"] is None
    assert detail["selection"]["native_support"] == {
        "state": "UNSUPPORTED",
        "reason": "NATIVE_EXECUTION_UNSUPPORTED",
    }


def test_program_has_no_global_start_and_keeps_validated_state(library):
    from app.services.user_program_drafts import create_draft, replace_draft_tree, validate_draft

    s, db, ctx = library
    p = create_draft(db, ctx.owner_id, "qa-program", "qa-program")
    replace_draft_tree(
        db,
        ctx.owner_id,
        p.id,
        [
            {
                "position": 1,
                "name": "Alpha",
                "exercises": [
                    {
                        "position": 1,
                        "exercise_name": "Synthetic",
                        "set_scheme": "2x8",
                        "rep_targets": [{"min_reps": 8, "max_reps": 12}],
                    }
                ],
            }
        ],
    )
    validate_draft(db, ctx.owner_id, p.id)
    row = entry(s, db, ctx, "qa-program")
    assert row["source_status"] == "VALIDATED"
    detail = s.read_library_item(db, ctx, row["source_ref"])
    assert detail["selection"] is None
    session = detail["composition"][0]
    assert session["selection"]["selection_ref"] is None
    assert session["selection"]["domain_launchable"] is False
    readback = s.read_library_item(db, ctx, session["source_ref"])
    assert readback["source"]["kind"] == "OWNED_SESSION"


def test_published_program_has_one_exact_selection_per_session(library):
    from app.services.user_program_drafts import create_draft, replace_draft_tree, validate_draft
    from app.services.user_program_publish import publish_user_program

    s, db, ctx = library
    p = create_draft(db, ctx.owner_id, "qa-two", "qa-two")
    tree = [
        {
            "position": n,
            "name": f"Session {n}",
            "exercises": [
                {
                    "position": 1,
                    "exercise_name": "Synthetic",
                    "set_scheme": "1x8",
                    "rep_targets": [{"min_reps": 8, "max_reps": 12}],
                }
            ],
        }
        for n in (1, 2)
    ]
    replace_draft_tree(db, ctx.owner_id, p.id, tree)
    validate_draft(db, ctx.owner_id, p.id)
    publish_user_program(db, ctx.owner_id, p.id)
    d = s.read_library_item(db, ctx, entry(s, db, ctx, "qa-two")["source_ref"])
    assert d["selection"] is None
    selections = [x["selection"]["selection_ref"] for x in d["composition"]]
    assert all(selections) and selections[0] != selections[1]
    templates = [s.resolve_library_selection(db, ctx, r) for r in selections]
    assert templates[0].id != templates[1].id
    p.status = "validated"  # even if a stale published pointer survived, deny fresh start
    db.commit()
    with pytest.raises(s.LibraryError) as e:
        s.resolve_library_selection(db, ctx, selections[0])
    assert e.value.status == 409


@pytest.mark.parametrize("change", ["owner", "backend", "epoch", "key", "tamper"])
def test_references_are_owner_environment_and_auth_bound(library, change):
    from dataclasses import replace

    s, db, ctx = library
    template(db, "qa-ref")
    ref = entry(s, db, ctx, "qa-ref")["source_ref"]
    changed = ctx
    if change == "owner":
        changed = replace(ctx, owner_id=ctx.owner_id + 1)
    if change == "backend":
        changed = replace(ctx, backend_identity="elsewhere")
    if change == "epoch":
        changed = replace(ctx, epoch=ctx.epoch + 1)
    if change == "key":
        changed = replace(ctx, signing_key="z" * 40)
    if change == "tamper":
        ref = ref[:-1] + ("a" if ref[-1] != "a" else "b")
    with pytest.raises(s.LibraryError) as e:
        s.read_library_item(db, changed, ref)
    assert (e.value.status, e.value.code) == (404, "foreign_or_missing")


def test_changed_page_never_becomes_a_mixed_complete_collection(library):
    s, db, ctx = library
    t = template(db, "qa-page")
    page = s.read_library(db, ctx, limit=1)
    assert page["collection_state"] == "PARTIAL" and page["next_cursor"]
    t.name = "changed projection"
    db.commit()
    with pytest.raises(s.LibraryError) as e:
        s.read_library(db, ctx, limit=1, cursor=page["next_cursor"])
    assert (e.value.status, e.value.code) == (409, "source_changed")


def test_stale_selection_cannot_start_modified_prescription(library):
    s, db, ctx = library
    t = template(db, "qa-stale")
    d = s.read_library_item(db, ctx, entry(s, db, ctx, t.name)["source_ref"])
    ref = d["selection"]["selection_ref"]
    t.exercises[0].rep_targets[0].min_reps = 9
    db.commit()
    with pytest.raises(s.LibraryError) as e:
        s.resolve_library_selection(db, ctx, ref)
    assert e.value.code == "stale_selection"


def test_unknown_zone_is_echoed_but_not_silently_applied(library):
    s, db, ctx = library
    page = s.read_library(db, ctx, zone="fictional-zone")
    assert page["requested_zone"] == "fictional-zone"
    assert page["applied_zone"] is None


def test_detail_budget_refuses_instead_of_truncating(library, monkeypatch):
    s, db, ctx = library
    t = template(db, "qa-budget", sets=3)
    ref = entry(s, db, ctx, t.name)["source_ref"]
    monkeypatch.setattr(s, "MAX_TARGETS_PER_SLOT", 2)
    with pytest.raises(s.LibraryError) as e:
        s.read_library_item(db, ctx, ref)
    assert (e.value.code, e.value.status) == ("source_too_large", 413)


def test_configuration_has_no_development_signing_fallback(client):
    from app.services.library_read_model import LibraryContext, LibraryError

    with pytest.raises(LibraryError) as e:
        LibraryContext(1, "", "short", 0)
    assert e.value.status == 503


def test_foreign_program_and_missing_reference_have_same_refusal(library):
    from dataclasses import replace

    from app.models.user import User
    from app.services.user_program_drafts import create_draft

    s, db, ctx = library
    other = User(username="qa-other", password_hash="not-a-real-login")
    db.add(other)
    db.commit()
    foreign_ctx = replace(ctx, owner_id=other.id)
    p = create_draft(db, other.id, "private title", "qa-private")
    assert all(x["name"] != "private title" for x in s.read_library(db, ctx)["entries"])
    foreign = s._ref(foreign_ctx, "OWNED_PROGRAM", p.id)
    missing = s._ref(ctx, "OWNED_PROGRAM", p.id + 999)
    errors = []
    for ref in (foreign, missing):
        with pytest.raises(s.LibraryError) as e:
            s.read_library_item(db, ctx, ref)
        errors.append((e.value.code, e.value.status))
    assert errors == [("foreign_or_missing", 404)] * 2


def test_index_budget_and_detail_slot_budget_fail_before_hydration(library, monkeypatch):
    s, db, ctx = library
    row = template(db, "qa-small-cap")
    ref = s._ref(ctx, "CATALOG_SESSION", row.id)
    monkeypatch.setattr(s, "MAX_CATALOGUE", 0)
    with pytest.raises(s.LibraryError) as e:
        s.read_library(db, ctx)
    assert e.value.status == 413
    monkeypatch.setattr(s, "MAX_DETAIL_SLOTS", 0)
    with pytest.raises(s.LibraryError) as e:
        s.read_library_item(db, ctx, ref)
    assert e.value.status == 413


def test_tied_program_times_have_stable_id_order_and_complete_pagination(library):
    from datetime import datetime

    from app.services.user_program_drafts import create_draft

    s, db, ctx = library
    a = create_draft(db, ctx.owner_id, "qa-tie-a", "qa-tie-a")
    b = create_draft(db, ctx.owner_id, "qa-tie-b", "qa-tie-b")
    a.updated_at = b.updated_at = datetime(2026, 11, 12)
    db.commit()
    first = s.read_library(db, ctx, section="programs", limit=1)
    second = s.read_library(db, ctx, section="programs", limit=1, cursor=first["next_cursor"])
    assert [first["entries"][0]["name"], second["entries"][0]["name"]] == ["qa-tie-b", "qa-tie-a"]
    assert second["collection_state"] == "COMPLETE"
    assert second["next_cursor"] is None


def test_non_finite_or_reversed_prescription_is_unavailable_not_repaired(library):
    s, db, ctx = library
    t = template(db, "qa-corrupt")
    t.exercises[0].rep_targets[0].min_reps = 99
    db.commit()
    with pytest.raises(s.LibraryError) as e:
        s.read_library_item(db, ctx, s._ref(ctx, "CATALOG_SESSION", t.id))
    assert (e.value.code, e.value.status) == ("storage_unavailable", 503)


def test_one_read_transaction_keeps_counts_coherent_during_concurrent_change(library):
    from sqlalchemy import text

    from app.database import SessionLocal
    from app.models.catalog import RepTarget

    s, db, ctx = library
    t = template(db, "qa-read-snapshot")
    ex_id = t.exercises[0].id
    db.commit()
    db.execute(text("PRAGMA journal_mode=WAL"))
    db.commit()
    first = entry(s, db, ctx, "qa-read-snapshot")
    with SessionLocal() as writer:
        writer.add(RepTarget(template_exercise_id=ex_id, set_index=3, min_reps=8, max_reps=12))
        writer.commit()
    second = entry(s, db, ctx, "qa-read-snapshot")
    assert second["counts"] == first["counts"]
    db.rollback()
    fresh = entry(s, db, ctx, "qa-read-snapshot")
    assert fresh["counts"]["prescribed_sets"] == 3


def test_native_zone_vocabulary_matches_the_canonical_library_domain():
    import json
    from pathlib import Path

    from app.services.muscle_mapping import ZONE_LABELS

    root = Path(__file__).resolve().parents[1]
    vocabulary = json.loads((root / "clients/mobile/src/api/libraryVocabulary.json").read_text())
    assert vocabulary["contract"] == "owned-library/1.0.0"
    assert vocabulary["zones"] == list(ZONE_LABELS)
