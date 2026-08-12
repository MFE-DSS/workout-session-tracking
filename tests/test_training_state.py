"""Sb_TRAINING_STATE_AGGREGATOR_01 — read-only evidence assembly.

Spec: `Sx_RECOVERY_READINESS_01_SPEC` §2.5, §4, §12bis.

Four properties carry this slice, and each is expensive to lose later:

* **read-only** — proven twice, at source level and by comparing a full DB
  snapshot before and after a build;
* **bounded queries** — proven by holding occurrences constant against distinct
  names, the N+1 shape that already bit `Sb_32.4`;
* **no fabricated favourable value** — a new user, a failed producer and a stale
  declaration must all stay conservative;
* **no estimate** — `zone_recovery` is empty on purpose; the next slice owns it.
"""
from __future__ import annotations

import ast
import inspect
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy import event, func, select

from app.services import training_state as ts
from app.services.recovery_contract import Confidence, Sufficiency
from app.services.training_state import (
    TRAINING_STATE_LOOKBACK_DAYS,
    build_training_state,
    zone_evidence_for,
)
from tests.helpers import get_test_user_id

NOW = datetime(2026, 8, 12, 12, 0, tzinfo=UTC)


def _module_code() -> str:
    """The service's code with every docstring stripped.

    The docstrings legitimately *name* what the module must not do — a decision,
    a `ZoneRecoveryEstimate`, `exercise_code_snapshot` — in order to explain why.
    Scanning them would flag the explanation instead of the behaviour.
    """
    tree = ast.parse(Path(ts.__file__).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef)):
            continue
        if ast.get_docstring(node):
            node.body = node.body[1:]
    return ast.unparse(tree)

CHEST = "Développé couché barre"
BACK = "Traction pronation"
LEGS = "Hack squat"


def _add_session(db, uid, *, days_ago=1, names=(), global_state=None,
                 concentration=None, cardio=None, status="completed",
                 excluded=False):
    from app.models.session import SessionExercise, WorkoutSession

    session = WorkoutSession(
        user_id=uid, template_slug_snapshot="push-a",
        template_name_snapshot="Push A", status=status,
        excluded_from_stats=excluded,
        global_state=global_state, concentration=concentration,
        started_at=NOW - timedelta(days=days_ago),
    )
    if cardio:
        session.cardio_duration_min = cardio.get("duration")
        session.cardio_bpm_avg = cardio.get("bpm")
        session.cardio_machine_type = cardio.get("machine")
        session.cardio_machine_calories = cardio.get("calories")
    for i, name in enumerate(names, start=1):
        session.session_exercises.append(SessionExercise(
            exercise_code_snapshot=f"E{i}", exercise_name_snapshot=name, position=i))
    db.add(session)
    db.commit()
    return session


def _add_readiness(db, uid, *, days_ago=0, sleep=4, fatigue=4, soreness=4,
                   stress=4, motivation=4):
    from app.models.readiness import ReadinessEntry

    entry = ReadinessEntry(
        user_id=uid, recorded_on=NOW.date() - timedelta(days=days_ago),
        sleep_quality=sleep, fatigue_level=fatigue, soreness_level=soreness,
        stress_level=stress, motivation_level=motivation)
    db.add(entry)
    db.commit()
    return entry


# ---------------------------------------------------------------------------
# Read-only — the guarantee that must never regress
# ---------------------------------------------------------------------------


def test_the_service_contains_no_write_operation():
    """Source-level guard, the pattern proven in Sb_32.4."""
    source = Path(ts.__file__).read_text(encoding="utf-8")
    for forbidden in ("db.add", "db.add_all", "db.delete", "db.commit",
                      "db.flush", "session.add", ".merge(", "bulk_save",
                      "bulk_insert", "bulk_update", "update(", "delete("):
        assert forbidden not in source, forbidden


def test_the_service_calls_no_known_writer():
    source = Path(ts.__file__).read_text(encoding="utf-8")
    for writer in ("save_readiness", "replace_draft_tree", "publish_user_program",
                   "seed_reference_data", "init_db"):
        assert writer not in source, writer


def _db_snapshot(db):
    """Row counts plus content of everything a write could disturb."""
    from app.models.readiness import ReadinessEntry
    from app.models.session import SessionExercise, SetLog, WorkoutSession
    from app.models.user import User
    from app.models.user_program import UserProgram

    counts = {
        m.__name__: db.execute(select(func.count()).select_from(m)).scalar()
        for m in (User, ReadinessEntry, WorkoutSession, SessionExercise,
                  SetLog, UserProgram)
    }
    sessions = db.execute(
        select(WorkoutSession.id, WorkoutSession.status,
               WorkoutSession.global_state, WorkoutSession.concentration,
               WorkoutSession.excluded_from_stats)
        .order_by(WorkoutSession.id)
    ).all()
    readiness = db.execute(
        select(ReadinessEntry.id, ReadinessEntry.recorded_on,
               ReadinessEntry.sleep_quality, ReadinessEntry.fatigue_level)
        .order_by(ReadinessEntry.id)
    ).all()
    return counts, sessions, readiness


def test_building_the_state_leaves_the_database_byte_identical(client):
    """Executed proof, not just a source grep."""
    from app.database import SessionLocal
    from app.models.user_program import UserProgram

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add_readiness(db, uid)
        _add_session(db, uid, days_ago=1, names=[CHEST, BACK],
                     global_state="good", concentration="high")
        _add_session(db, uid, days_ago=3, names=[LEGS],
                     cardio={"duration": 25, "bpm": 130, "machine": "velo",
                             "calories": 300})
        db.add(UserProgram(user_id=uid, title="P", slug_base="p", status="draft"))
        db.commit()
        before = _db_snapshot(db)

    with SessionLocal() as db:
        build_training_state(db, uid, now=NOW)

    with SessionLocal() as db:
        after = _db_snapshot(db)

    assert after == before


def test_the_state_object_is_immutable():
    from dataclasses import FrozenInstanceError

    from app.services.recovery_contract import TrainingState

    with pytest.raises(FrozenInstanceError):
        TrainingState().sufficiency = Sufficiency.SUFFICIENT


# ---------------------------------------------------------------------------
# Determinism and the explicit clock
# ---------------------------------------------------------------------------


def test_now_is_required_and_keyword_only():
    """A hidden clock would make the result irreproducible."""
    params = inspect.signature(build_training_state).parameters
    assert params["now"].kind is inspect.Parameter.KEYWORD_ONLY
    assert params["now"].default is inspect.Parameter.empty


def test_same_database_and_same_now_give_the_same_state(client):
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add_readiness(db, uid)
        _add_session(db, uid, days_ago=1, names=[CHEST],
                     global_state="flat", concentration="medium")
        first = build_training_state(db, uid, now=NOW)
        second = build_training_state(db, uid, now=NOW)

    assert first == second


def test_the_service_reads_no_clock_of_its_own():
    source = Path(ts.__file__).read_text(encoding="utf-8")
    for forbidden in ("datetime.now(", "date.today(", "time.time("):
        assert forbidden not in source, forbidden


# ---------------------------------------------------------------------------
# Readiness — OQ-6, and the rename
# ---------------------------------------------------------------------------


def test_a_declaration_made_today_is_sufficient_and_decision_relevant(client):
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add_readiness(db, uid, days_ago=0, sleep=5, fatigue=5, soreness=5,
                       stress=5, motivation=5)
        state = build_training_state(db, uid, now=NOW)

    assert state.readiness.age_days == 0
    assert state.readiness.sufficiency is Sufficiency.SUFFICIENT
    assert state.readiness.is_decision_relevant is True
    assert state.readiness.overall == 1.0


@pytest.mark.parametrize(("days_ago", "expected"), [
    (0, Sufficiency.SUFFICIENT),
    (1, Sufficiency.PARTIAL),
    (2, Sufficiency.PARTIAL),
    (3, Sufficiency.STALE),
    (10, Sufficiency.STALE),
])
def test_readiness_staleness_follows_oq6(client, days_ago, expected):
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add_readiness(db, uid, days_ago=days_ago)
        state = build_training_state(db, uid, now=NOW)

    assert state.readiness.sufficiency is expected
    assert state.readiness.age_days == days_ago


def test_a_historical_declaration_never_becomes_today(client):
    """No back-fill: an old entry is surfaced as old, never as current."""
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add_readiness(db, uid, days_ago=6)
        state = build_training_state(db, uid, now=NOW)

    assert state.readiness.age_days == 6
    assert state.readiness.declared_on == date(2026, 8, 6)
    assert state.readiness.is_decision_relevant is False
    assert state.readiness.sufficiency is Sufficiency.STALE


def test_the_most_recent_declaration_wins(client):
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add_readiness(db, uid, days_ago=5, sleep=1)
        _add_readiness(db, uid, days_ago=0, sleep=5)
        state = build_training_state(db, uid, now=NOW)

    assert state.readiness.age_days == 0
    assert state.readiness.sleep == 1.0


def test_persisted_fatigue_level_is_surfaced_as_freshness(client):
    """5 on that column means "Très frais" — never exposed as fatigue."""
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add_readiness(db, uid, fatigue=5)
        state = build_training_state(db, uid, now=NOW)

    assert state.readiness.self_reported_freshness == 1.0
    assert not hasattr(state.readiness, "fatigue_level")


def test_no_readiness_entry_leaves_every_value_missing(client):
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        state = build_training_state(db, uid, now=NOW)

    assert state.readiness.sufficiency is Sufficiency.INSUFFICIENT
    assert state.readiness.overall is None
    assert all(d is None for d in state.readiness.dimensions)
    assert state.readiness.is_decision_relevant is False


def test_out_of_range_dimensions_are_excluded_not_zero_filled(client):
    """A historical row outside 1-5 must drop out, not read as the worst score."""
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add_readiness(db, uid, sleep=5, fatigue=5, soreness=99, stress=5,
                       motivation=5)
        state = build_training_state(db, uid, now=NOW)

    assert state.readiness.soreness is None
    assert state.readiness.overall == 1.0  # mean of the four usable 5s


def test_behavioral_readiness_score_is_not_consumed(client):
    """OQ-1: the duplicate stays out of TrainingState."""
    source = Path(ts.__file__).read_text(encoding="utf-8")
    assert "readiness_score" not in source


# ---------------------------------------------------------------------------
# Fatigue — three separate components, no aggregate
# ---------------------------------------------------------------------------


def test_the_three_components_stay_separate_and_unaggregated(client):
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add_session(db, uid, days_ago=1, names=[CHEST],
                     global_state="fatigued", concentration="low",
                     cardio={"duration": 30, "machine": "velo"})
        state = build_training_state(db, uid, now=NOW)

    assert set(state.fatigue.components) == {"strength", "cardio", "subjective"}
    forbidden = {"overall", "as_availability", "aggregate", "score", "weighted"}
    assert {n for n in dir(state.fatigue) if not n.startswith("_")} & forbidden == set()


def test_the_service_never_complements_the_whole_signal():
    source = Path(ts.__file__).read_text(encoding="utf-8")
    assert "fatigue_to_availability" not in source


def test_subjective_component_uses_the_latest_declaration(client):
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add_session(db, uid, days_ago=5, names=[CHEST],
                     global_state="fatigued", concentration="low")
        _add_session(db, uid, days_ago=1, names=[CHEST],
                     global_state="good", concentration="high")
        state = build_training_state(db, uid, now=NOW)

    # good + high is the producible floor, 15/100.
    assert state.fatigue.subjective_component == 0.15


def test_no_declaration_leaves_the_subjective_component_missing(client):
    """`compute_session_fatigue` would substitute 50/40 defaults."""
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add_session(db, uid, days_ago=1, names=[CHEST])
        state = build_training_state(db, uid, now=NOW)

    assert state.fatigue.subjective_component is None


def test_a_failing_legacy_producer_yields_none_not_fresh(client, monkeypatch):
    """The single most important fail-closed case in this slice."""
    from app.database import SessionLocal
    from app.services import behavioral

    def boom(*_args, **_kwargs):
        raise RuntimeError("producer down")

    monkeypatch.setattr(behavioral, "compute_behavioral_state", boom)

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add_session(db, uid, days_ago=1, names=[CHEST],
                     global_state="good", concentration="high")
        state = build_training_state(db, uid, now=NOW)

    assert state.fatigue.strength_component is None
    assert state.fatigue.strength_component != 0.0
    assert any("unavailable" in b for b in state.fatigue.basis)


def test_the_strength_component_delegates_to_the_canonical_normaliser(monkeypatch):
    """No second 0-100 conversion is written here."""
    source = Path(ts.__file__).read_text(encoding="utf-8")
    assert "normalize_legacy_fatigue" in source
    assert "/ 100" not in source


def test_cardio_component_uses_the_canonical_adapter(client, monkeypatch):
    from app.database import SessionLocal

    calls = []
    real = ts.cardio_load_estimate

    def spy(**kwargs):
        calls.append(kwargs)
        return real(**kwargs)

    monkeypatch.setattr(ts, "cardio_load_estimate", spy)

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add_session(db, uid, days_ago=1, names=[],
                     cardio={"duration": 15, "bpm": 130, "machine": "velo"})
        state = build_training_state(db, uid, now=NOW)

    assert calls == [{"machine_type": "velo", "duration_min": 15, "bpm_avg": 130}]
    assert state.fatigue.cardio_component == 0.5  # 15 / 30 min reference


def test_the_service_reimplements_no_cardio_semantics():
    source = Path(ts.__file__).read_text(encoding="utf-8")
    for forbidden in ("CARDIO_DURATION_REFERENCE", "bpm_avg >", "calor",
                      "_CARDIO_ZONE_TABLE"):
        assert forbidden not in source, forbidden


def test_several_cardio_sessions_select_the_latest_without_aggregating(client):
    """A selection rule, stated as such — no invented cumulative formula."""
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add_session(db, uid, days_ago=8, names=[],
                     cardio={"duration": 30, "machine": "velo"})
        _add_session(db, uid, days_ago=2, names=[],
                     cardio={"duration": 15, "machine": "velo"})
        state = build_training_state(db, uid, now=NOW)

    assert state.fatigue.cardio_component == 0.5  # the 15 min one, not summed
    assert any("selection, not aggregation" in b for b in state.fatigue.basis)
    assert any("2 cardio session(s)" in b for b in state.fatigue.basis)


def test_no_cardio_in_window_leaves_the_component_missing(client):
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add_session(db, uid, days_ago=1, names=[CHEST])
        state = build_training_state(db, uid, now=NOW)

    assert state.fatigue.cardio_component is None


def test_calories_do_not_change_the_state(client):
    from app.database import SessionLocal

    uid = get_test_user_id()
    results = []
    for calories in (0, 500, 9999):
        with SessionLocal() as db:
            from app.models.session import WorkoutSession
            db.query(WorkoutSession).delete()
            db.commit()
            _add_session(db, uid, days_ago=1, names=[],
                         cardio={"duration": 20, "machine": "velo",
                                 "calories": calories})
            results.append(build_training_state(db, uid, now=NOW)
                           .fatigue.cardio_component)

    assert len(set(results)) == 1


# ---------------------------------------------------------------------------
# Sufficiency / confidence composition
# ---------------------------------------------------------------------------


def test_a_brand_new_user_gets_no_fabricated_favourable_signal(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.auth import hash_password

    with SessionLocal() as db:
        db.add(User(username="ts_new_user",
                    password_hash=hash_password("anything1"), is_active=True))
        db.commit()
        uid = db.execute(
            select(User.id).where(User.username == "ts_new_user")).scalar_one()
        state = build_training_state(db, uid, now=NOW)

    assert state.sufficiency is Sufficiency.INSUFFICIENT
    assert state.confidence is Confidence.NONE
    assert state.readiness.overall is None
    assert state.fatigue.observed_components == {}
    # Every canonical zone is present and explicitly unknown — stronger than the
    # empty tuple this asserted before the estimator slice existed.
    assert all(e.estimate is None for e in state.zone_recovery)
    assert all(e.confidence is Confidence.NONE for e in state.zone_recovery)
    assert state.equipment is None
    assert state.schedule is None


def test_confidence_never_reaches_high(client):
    """No accuracy claim here supports it; the conservative option is taken."""
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add_readiness(db, uid, days_ago=0)
        _add_session(db, uid, days_ago=1, names=[CHEST, BACK, LEGS],
                     global_state="good", concentration="high",
                     cardio={"duration": 30, "bpm": 130, "machine": "velo"})
        state = build_training_state(db, uid, now=NOW)

    assert state.confidence is not Confidence.HIGH


def test_more_evidence_can_only_raise_confidence_monotonically(client):
    from app.database import SessionLocal

    ladder = [Confidence.NONE, Confidence.LOW, Confidence.MEDIUM, Confidence.HIGH]
    uid = get_test_user_id()
    seen = []
    with SessionLocal() as db:
        seen.append(build_training_state(db, uid, now=NOW).confidence)
        _add_readiness(db, uid, days_ago=0)
        seen.append(build_training_state(db, uid, now=NOW).confidence)
        _add_session(db, uid, days_ago=1, names=[CHEST],
                     global_state="good", concentration="high")
        seen.append(build_training_state(db, uid, now=NOW).confidence)

    indexes = [ladder.index(c) for c in seen]
    assert indexes == sorted(indexes)


def test_stale_readiness_cannot_upgrade_the_state(client):
    """OQ-6/OQ-7: a non-current declaration is context, never an upgrade."""
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        baseline = build_training_state(db, uid, now=NOW)
        _add_readiness(db, uid, days_ago=9, sleep=5, fatigue=5, soreness=5,
                       stress=5, motivation=5)
        with_stale = build_training_state(db, uid, now=NOW)

    assert with_stale.sufficiency is baseline.sufficiency
    assert with_stale.confidence is baseline.confidence
    # Still surfaced as context.
    assert with_stale.readiness.overall == 1.0
    assert with_stale.readiness.sufficiency is Sufficiency.STALE


def test_cardio_alone_cannot_make_the_state_confident(client):
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add_session(db, uid, days_ago=1, names=[],
                     cardio={"duration": 30, "bpm": 130, "machine": "velo"})
        state = build_training_state(db, uid, now=NOW)

    assert state.confidence in (Confidence.NONE, Confidence.LOW)
    assert state.sufficiency is not Sufficiency.SUFFICIENT


def test_readiness_only_populates_readiness_and_nothing_else(client):
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add_readiness(db, uid, days_ago=0)
        state = build_training_state(db, uid, now=NOW)

    assert state.readiness.overall is not None
    assert state.fatigue.observed_components == {}


def test_sufficiency_composition_ignores_the_values_themselves():
    """A flattering number cannot lift an otherwise thin state."""
    source = inspect.getsource(ts._compose_sufficiency)
    assert "is not None" in source
    # It counts presence; no comparison against a magnitude appears.
    for forbidden in (">= 0.", "<= 0.", "> 0.5", "< 0.5"):
        assert forbidden not in source, forbidden


# ---------------------------------------------------------------------------
# Query discipline — the N+1 shape that already bit Sb_32.4
# ---------------------------------------------------------------------------


def _count_queries(fn):
    from app.database import engine

    seen: list[str] = []

    def listener(_conn, _cursor, statement, *_a, **_k):
        seen.append(statement)

    event.listen(engine, "before_cursor_execute", listener)
    try:
        fn()
    finally:
        event.remove(engine, "before_cursor_execute", listener)
    return seen


def test_repeated_exercise_names_do_not_multiply_queries(client):
    """Occurrences ×4 at constant distinct names must not move the query count."""
    from app.database import SessionLocal

    uid = get_test_user_id()
    names = [CHEST, BACK, LEGS]

    with SessionLocal() as db:
        _add_session(db, uid, days_ago=1, names=names,
                     global_state="good", concentration="high")
        small = _count_queries(
            lambda: build_training_state(db, uid, now=NOW))

    with SessionLocal() as db:
        for day in range(2, 10):
            _add_session(db, uid, days_ago=day, names=names * 3,
                         global_state="good", concentration="high")
        large = _count_queries(
            lambda: build_training_state(db, uid, now=NOW))

    # 3 occurrences -> 75 occurrences, same three distinct names.
    assert len(large) == len(small), (
        f"query count grew from {len(small)} to {len(large)} while distinct "
        "exercise names stayed constant — N+1 regression"
    )


def test_zone_resolution_happens_once_per_distinct_name(client, monkeypatch):
    from app.database import SessionLocal

    resolved: list[str] = []
    real = ts.resolve_exercise_zones

    def spy(db, name):
        resolved.append(name)
        return real(db, name)

    monkeypatch.setattr(ts, "resolve_exercise_zones", spy)

    uid = get_test_user_id()
    names = [CHEST, BACK, LEGS]
    with SessionLocal() as db:
        for day in range(1, 6):
            _add_session(db, uid, days_ago=day, names=names * 4)
        build_training_state(db, uid, now=NOW)

    assert len(resolved) == len(set(resolved)) == 3  # 60 occurrences, 3 names


def test_the_cache_is_per_invocation_not_global():
    """A module-level cache over DB-backed state would go stale."""
    source = Path(ts.__file__).read_text(encoding="utf-8")
    assert "lru_cache" not in source
    assert "@cache" not in source


# ---------------------------------------------------------------------------
# Zone evidence — facts gathered, estimates deliberately not produced
# ---------------------------------------------------------------------------


def test_zone_recovery_is_delegated_to_the_estimator_slice(client):
    """Was "empty because the next slice owns it" — that slice now exists.

    The boundary this test guarded has been filled by
    `Sb_ZONE_RECOVERY_ESTIMATE_01`. The expectation is retired rather than
    weakened: the property that matters is now stronger — all 11 canonical zones
    are always present, and this module still computes no estimate itself.
    """
    from app.database import SessionLocal
    from app.services.muscle_mapping import ZONE_LABELS

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add_session(db, uid, days_ago=1, names=[CHEST, BACK, LEGS])
        state = build_training_state(db, uid, now=NOW)

    assert len(state.zone_recovery) == len(ZONE_LABELS)
    assert {e.zone_code for e in state.zone_recovery} == set(ZONE_LABELS)
    assert state.zone_suitability == ()
    assert any("delegated to Sb_ZONE_RECOVERY_ESTIMATE_01" in b for b in state.basis)


def test_delegating_the_estimates_costs_no_additional_query(client):
    """The estimates reuse evidence already gathered — not a second pass."""
    from app.database import SessionLocal
    from app.services import training_state as mod

    uid = get_test_user_id()
    with SessionLocal() as db:
        for day in range(1, 5):
            _add_session(db, uid, days_ago=day, names=[CHEST, BACK, LEGS])
        with_estimates = _count_queries(
            lambda: build_training_state(db, uid, now=NOW))
        real = mod._zone_recovery_from
        mod._zone_recovery_from = lambda evidence, *, now: ()
        try:
            without = _count_queries(
                lambda: build_training_state(db, uid, now=NOW))
        finally:
            mod._zone_recovery_from = real

    assert len(with_estimates) == len(without)


def test_the_aggregator_computes_no_estimate_of_its_own():
    """It may delegate; it may not calculate. No band, no decay, no roll-up."""
    source = _module_code()
    for forbidden in ("band_for_estimate", "RecoveryBand", "worst_zone_rollup",
                      "never_trained_estimate", "normalize_training_suitability",
                      "recovery_target_hours", "decay", "half_life",
                      "radar_axis_for_zone"):
        assert forbidden not in source, forbidden
    # Delegation is the only permitted route to an estimate.
    assert "build_zone_recovery_from_evidence" in source


def test_zone_evidence_records_facts_not_conclusions(client):
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add_session(db, uid, days_ago=2, names=[LEGS])
        _add_session(db, uid, days_ago=1, names=[LEGS])
        evidence = zone_evidence_for(db, uid, now=NOW)

    quads = evidence["quads"]
    assert quads.strength_occurrences == 2
    # SQLite returns naive datetimes for the repo's `DateTime` columns.
    assert quads.last_strength_load_at.replace(tzinfo=UTC) == NOW - timedelta(days=1)
    assert quads.resolution_paths  # how attribution was obtained is recorded
    assert not hasattr(quads, "estimate")
    assert not hasattr(quads, "band")


def test_zone_evidence_uses_only_canonical_zone_codes(client):
    from app.database import SessionLocal
    from app.services.muscle_mapping import ZONE_LABELS

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add_session(db, uid, days_ago=1, names=[CHEST, BACK, LEGS],
                     cardio={"duration": 20, "machine": "rameur"})
        evidence = zone_evidence_for(db, uid, now=NOW)

    assert evidence
    for code in evidence:
        assert code in ZONE_LABELS, code


def test_the_canonical_zone_universe_is_discoverable_and_not_redeclared():
    """No fifth 11-zone list; `core` stays `core`."""
    from app.services.muscle_mapping import ZONE_LABELS

    assert len(ZONE_LABELS) == 11
    assert "core" in ZONE_LABELS
    source = Path(ts.__file__).read_text(encoding="utf-8")
    assert "ZONE_LABELS = " not in source
    assert "_EXERCISE_PATTERNS" not in source


def test_no_macro_projection_is_used_to_build_the_state():
    """OQ-5 is presentation-only and is not exercised here."""
    source = Path(ts.__file__).read_text(encoding="utf-8")
    for forbidden in ("radar_axis_for_zone", "ZONE_TO_RADAR_AXIS",
                      "RADAR_AXIS_ORDER", "MacroAxisRecovery"):
        assert forbidden not in source, forbidden


def test_attribution_uses_the_exercise_name_not_the_slot_code(client):
    """`exercise_code_snapshot` is a training-day slot, reused across exercises."""
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        # Both rows carry slot E1; only the names differ.
        _add_session(db, uid, days_ago=1, names=[CHEST])
        _add_session(db, uid, days_ago=2, names=[LEGS])
        evidence = zone_evidence_for(db, uid, now=NOW)

    assert "pecs" in evidence
    assert "quads" in evidence
    source = _module_code()
    assert "exercise_code_snapshot" not in source
    assert "actual_exercise_name" in source


def test_substituted_name_takes_precedence_in_attribution(client):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    uid = get_test_user_id()
    with SessionLocal() as db:
        session = _add_session(db, uid, days_ago=1, names=[CHEST])
        stored = db.get(WorkoutSession, session.id)
        stored.session_exercises[0].substituted_name = LEGS
        db.commit()
        evidence = zone_evidence_for(db, uid, now=NOW)

    assert "quads" in evidence
    assert "pecs" not in evidence


def test_cardio_zone_exposure_is_recorded_as_evidence(client):
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add_session(db, uid, days_ago=1, names=[],
                     cardio={"duration": 20, "machine": "rameur"})
        evidence = zone_evidence_for(db, uid, now=NOW)

    assert "lats" in evidence  # rowing is the mixed modality
    assert evidence["lats"].cardio_exposure_modalities == {"rameur"}
    assert evidence["lats"].strength_occurrences == 0


def test_an_unknown_cardio_modality_fabricates_no_zone(client):
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add_session(db, uid, days_ago=1, names=[],
                     cardio={"duration": 20, "machine": "stairmaster"})
        evidence = zone_evidence_for(db, uid, now=NOW)

    assert all(not e.cardio_exposure_modalities for e in evidence.values())


# ---------------------------------------------------------------------------
# Window and filters
# ---------------------------------------------------------------------------


def test_the_window_reuses_the_repository_convention():
    assert TRAINING_STATE_LOOKBACK_DAYS == 30


def test_sessions_outside_the_window_are_ignored(client):
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add_session(db, uid, days_ago=400, names=[CHEST],
                     global_state="good", concentration="high")
        state = build_training_state(db, uid, now=NOW)

    assert any("0 completed session(s)" in b for b in state.basis)
    assert state.fatigue.subjective_component is None


def test_ancient_training_cannot_present_as_current_fatigue_evidence(client):
    """Gitar finding on PR #81, and it was right.

    `behavioral` has no date filter, so a single declaration from 400 days ago
    populated `strength_component` and lifted an otherwise empty state to
    PARTIAL/LOW — while a stale *readiness* declaration is deliberately not
    counted. Abandoned training must not read as current evidence either.
    """
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add_session(db, uid, days_ago=400, names=[CHEST],
                     global_state="fatigued", concentration="low")
        state = build_training_state(db, uid, now=NOW)

    assert state.fatigue.strength_component is None
    assert state.fatigue.subjective_component is None
    assert state.sufficiency is Sufficiency.INSUFFICIENT
    assert state.confidence is Confidence.NONE


def test_a_declaration_inside_the_window_still_feeds_the_producer(client):
    """The window bounds the gate; it must not disable the component."""
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add_session(db, uid, days_ago=400, names=[CHEST],
                     global_state="good", concentration="high")
        _add_session(db, uid, days_ago=2, names=[CHEST],
                     global_state="fatigued", concentration="low")
        state = build_training_state(db, uid, now=NOW)

    assert state.fatigue.strength_component is not None


def test_incomplete_and_excluded_sessions_are_ignored(client):
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add_session(db, uid, days_ago=1, names=[CHEST], status="in_progress",
                     global_state="good", concentration="high")
        _add_session(db, uid, days_ago=2, names=[BACK], excluded=True,
                     global_state="good", concentration="high")
        state = build_training_state(db, uid, now=NOW)

    assert any("0 completed session(s)" in b for b in state.basis)


def test_another_users_data_is_not_read(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.auth import hash_password

    uid = get_test_user_id()
    with SessionLocal() as db:
        db.add(User(username="ts_other",
                    password_hash=hash_password("anything1"), is_active=True))
        db.commit()
        other = db.execute(
            select(User.id).where(User.username == "ts_other")).scalar_one()
        _add_session(db, other, days_ago=1, names=[CHEST],
                     global_state="good", concentration="high")
        _add_readiness(db, other, days_ago=0)

        state = build_training_state(db, uid, now=NOW)

    assert state.readiness.sufficiency is Sufficiency.INSUFFICIENT
    assert state.fatigue.subjective_component is None


# ---------------------------------------------------------------------------
# Boundaries this slice must not cross
# ---------------------------------------------------------------------------


def test_no_decision_or_ranking_is_produced():
    source = _module_code()
    for forbidden in ("recommend", "rank", "sort_by_score", "choose_", "select_next"):
        assert forbidden not in source, forbidden


def test_recommendation_and_behavioral_are_not_modified():
    import app.services.behavioral as behavioral
    import app.services.recommendation as recommendation

    for module in (recommendation, behavioral):
        source = Path(module.__file__).read_text(encoding="utf-8")
        assert "training_state" not in source


def test_no_equipment_or_schedule_is_manufactured(client):
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        state = build_training_state(db, uid, now=NOW)

    assert state.equipment is None
    assert state.schedule is None


def test_the_state_exposes_no_global_score(client):
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _add_readiness(db, uid)
        _add_session(db, uid, days_ago=1, names=[CHEST],
                     global_state="good", concentration="high")
        state = build_training_state(db, uid, now=NOW)

    forbidden = {"overall_score", "readiness_score", "recovery_percentage",
                 "score", "composite", "index"}
    assert {n for n in dir(state) if not n.startswith("_")} & forbidden == set()
    for name, attr in inspect.getmembers(type(state)):
        if name.startswith("_") or not isinstance(attr, property):
            continue
        assert not isinstance(getattr(state, name), float), name


def test_the_service_never_claims_to_measure_a_body():
    from app.services.recovery_contract import FORBIDDEN_CONTRACT_WORDING

    source = Path(ts.__file__).read_text(encoding="utf-8").casefold()
    for forbidden in FORBIDDEN_CONTRACT_WORDING:
        assert forbidden.casefold() not in source, forbidden
