"""Real owned start transaction, not a fixture manufacturing a successful session."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from sqlalchemy import func, select
from test_mobile_library_reads import entry, library_source, template  # noqa: F401


def selection(service, db, ctx, slug):
    template(db, slug)
    return service.read_library_item(db, ctx, entry(service, db, ctx, slug)["source_ref"])[
        "selection"
    ]["selection_ref"]


def start(db, ctx, ref, **overrides):
    from app.models.user import User
    from app.services.library_start import start_library_session

    user = db.get(User, ctx.owner_id)
    args = {
        "expected_epoch": ctx.epoch,
        "expected_hash": user.password_hash,
        "device_id": None,
        "controlled_test_enabled": True,
        "app_env": "test",
    }
    return start_library_session(db, ctx, ref, **{**args, **overrides})


def count(db):
    from app.models.session import WorkoutSession

    return db.scalar(select(func.count()).select_from(WorkoutSession))


def test_start_creates_owned_planned_session_without_completed_facts(library):
    from app.models.session import WorkoutSession

    s, db, ctx = library
    ref = selection(s, db, ctx, "qa-start")
    before = count(db)
    result = start(db, ctx, ref)
    assert count(db) == before + 1
    assert result["execution_profile"] == "LEGACY"
    row = db.get(WorkoutSession, result["execution"]["session_id"])
    assert row.user_id == ctx.owner_id
    assert row.creation_source == "library"
    assert row.template_slug_snapshot == "qa-start"
    assert all(
        not fact.completed and fact.weight_kg is None and fact.reps is None
        for exercise in row.session_exercises
        for fact in exercise.set_logs
    )
    assert result["source_ref"] == entry(s, db, ctx, "qa-start")["source_ref"]


def test_second_start_is_refused_without_creating_a_second_session(library):
    s, db, ctx = library
    ref = selection(s, db, ctx, "qa-one-open")
    start(db, ctx, ref)
    before = count(db)
    with pytest.raises(s.LibraryError) as e:
        start(db, ctx, ref)
    assert (e.value.code, e.value.status) == ("session_open", 409)
    assert count(db) == before


@pytest.mark.parametrize(
    "override", [dict(controlled_test_enabled=False), dict(app_env="production")]
)
def test_write_is_closed_outside_explicit_synthetic_scope(library, override):
    s, db, ctx = library
    ref = selection(s, db, ctx, "qa-closed")
    before = count(db)
    with pytest.raises(s.LibraryError) as e:
        start(db, ctx, ref, **override)
    assert (e.value.code, e.value.status) == ("acquisition_unavailable", 403)
    assert count(db) == before


@pytest.mark.parametrize(
    "override",
    [
        dict(expected_epoch=999),
        dict(expected_hash="changed"),
        dict(device_id="not-a-current-device"),
    ],
)
def test_current_auth_is_revalidated_under_owner_lock(library, override):
    s, db, ctx = library
    ref = selection(s, db, ctx, "qa-auth-lock")
    before = count(db)
    with pytest.raises(s.LibraryError) as e:
        start(db, ctx, ref, **override)
    assert e.value.status == 401
    assert count(db) == before


def test_partial_materialization_rolls_back_whole_real_session(library, monkeypatch):
    from app.services import library_start

    s, db, ctx = library
    ref = selection(s, db, ctx, "qa-partial")
    before = count(db)
    monkeypatch.setattr(
        library_start,
        "preparer_demarrage",
        lambda *a: SimpleNamespace(etat="adaptable", plan=(object(),), attendu=1),
    )
    monkeypatch.setattr(library_start, "_poser_adaptations", lambda *a: 0)
    with pytest.raises(s.LibraryError) as e:
        start(db, ctx, ref)
    assert e.value.code == "start_blocked"
    assert count(db) == before


def test_preflight_refusal_creates_no_session(library, monkeypatch):
    from app.services import library_start

    s, db, ctx = library
    ref = selection(s, db, ctx, "qa-refused")
    before = count(db)
    monkeypatch.setattr(
        library_start, "preparer_demarrage", lambda *a: SimpleNamespace(etat="refuse")
    )
    with pytest.raises(s.LibraryError) as e:
        start(db, ctx, ref)
    assert e.value.code == "start_blocked"
    assert count(db) == before


def test_owner_serializes_two_real_concurrent_fresh_starts(library):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    from app.database import SessionLocal
    from app.models.user import User

    s, db, ctx = library
    ref = selection(s, db, ctx, "qa-race")
    expected_hash = db.get(User, ctx.owner_id).password_hash
    before = count(db)
    db.rollback()
    barrier = Barrier(2)

    def run():
        from app.services.library_start import start_library_session

        with SessionLocal() as other:
            barrier.wait(timeout=5)
            try:
                start_library_session(
                    other,
                    ctx,
                    ref,
                    expected_epoch=ctx.epoch,
                    expected_hash=expected_hash,
                    device_id=None,
                    controlled_test_enabled=True,
                    app_env="test",
                )
                return "created"
            except s.LibraryError as e:
                return e.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: run(), range(2)))
    assert sorted(results) == ["created", "session_open"]
    assert count(db) == before + 1
