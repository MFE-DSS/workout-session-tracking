"""Sb_ZONE_RECOVERY_ESTIMATE_01 — per-zone recovery estimates.

Spec: `Sx_RECOVERY_READINESS_01_SPEC` §2.3, §5.3, §11, §12bis (OQ-2, OQ-5).

The properties that matter, and why each is easy to lose:

* **the never-trained fail-open stays closed** — the legacy path calls an unseen
  zone perfectly available; here it is unknown, and the divergence is enumerated
  rather than discovered;
* **no new physiology** — the temporal rule is the legacy formula reached
  through the contract, with no decay curve, no half-life, no "72h rule";
* **OQ-2 holds** — the policy is versioned in code, never a schema column, and
  the legacy constant is read through the existing adapter;
* **cardio can never raise availability** — an uncertain signal may make the
  system more cautious, never more aggressive;
* **OQ-5 holds** — macro roll-up is presentation-only, takes the worst zone, and
  reuses the P0.1 projection instead of recopying it.
"""
from __future__ import annotations

import ast
import inspect
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from app.services import zone_recovery as zr
from app.services.muscle_mapping import ZONE_LABELS, radar_axis_for_zone
from app.services.recovery_contract import (
    Confidence,
    RecoveryBand,
    Sufficiency,
)
from app.services.training_state import _ZoneEvidence
from app.services.zone_recovery import (
    DEFAULT_RECOVERY_POLICY,
    LEGACY_DIVERGENCES,
    RECOVERY_POLICY_VERSION,
    RecoveryPolicy,
    build_macro_recovery,
    build_zone_recovery_from_evidence,
    canonical_zone_codes,
    estimate_for_zone,
)

NOW = datetime(2026, 8, 12, 12, 0, tzinfo=UTC)


def _evidence(zone, *, hours_ago=None, occurrences=1, paths=("db_lookup",),
              cardio=()):
    return _ZoneEvidence(
        zone_code=zone,
        last_strength_load_at=(
            None if hours_ago is None else NOW - timedelta(hours=hours_ago)),
        strength_occurrences=occurrences,
        cardio_exposure_modalities=set(cardio),
        resolution_paths=set(paths),
    )


def _module_code() -> str:
    """The module's code with docstrings stripped.

    The docstrings name what must not happen — decay, half-life, a BodyZone
    column — in order to forbid it. Scanning them would flag the prohibition.
    """
    tree = ast.parse(Path(zr.__file__).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef)) \
                and ast.get_docstring(node):
            node.body = node.body[1:]
    return ast.unparse(tree)


# ---------------------------------------------------------------------------
# OQ-2 — the policy is versioned in code, not in the schema
# ---------------------------------------------------------------------------


def test_no_bodyzone_column_was_added():
    """OQ-2: recovery duration is not an intrinsic anatomical property."""
    from app.models.body_zone import BodyZone

    for forbidden in ("recovery_hours", "recovery_target", "recovery_policy"):
        assert not hasattr(BodyZone, forbidden), forbidden


def test_no_migration_is_introduced():
    source = _module_code()
    for forbidden in ("op.add_column", "alembic", "mapped_column", "Column("):
        assert forbidden not in source, forbidden


def test_the_policy_is_versioned():
    assert RECOVERY_POLICY_VERSION == 1
    assert DEFAULT_RECOVERY_POLICY.version == RECOVERY_POLICY_VERSION
    assert RecoveryPolicy(version=2).version == 2


def test_the_policy_reads_the_legacy_constant_through_the_adapter():
    """Reading `recommendation.py` is allowed; modifying it is not."""
    from app.services.recommendation import RECOVERY_HOURS_TARGET

    for zone, hours in RECOVERY_HOURS_TARGET.items():
        assert DEFAULT_RECOVERY_POLICY.target_hours(zone) == float(hours)
    assert DEFAULT_RECOVERY_POLICY.target_hours("not_a_zone") is None


def test_recommendation_py_is_not_modified():
    import app.services.recommendation as recommendation

    source = Path(recommendation.__file__).read_text(encoding="utf-8")
    assert "zone_recovery" not in source


def test_the_policy_owns_no_arithmetic_of_its_own():
    """It delegates to the contract; it is a named seam, not a formula."""
    for method in (RecoveryPolicy.target_hours, RecoveryPolicy.estimate):
        body = inspect.getsource(method).split('"""')[-1]
        for operator in ("/", "*", "**", "exp", "log"):
            assert operator not in body, (method.__name__, operator)


def test_a_replacement_policy_changes_the_estimate_without_touching_the_module():
    """The seam works: version 2 can behave differently, in code, no schema."""
    class FlatPolicy(RecoveryPolicy):
        def estimate(self, hours_since_load, zone_code):
            return 0.0

    default = estimate_for_zone("quads", _evidence("quads", hours_ago=200),
                                now=NOW)
    flat = estimate_for_zone("quads", _evidence("quads", hours_ago=200),
                             now=NOW, policy=FlatPolicy(version=2))
    assert default.estimate == 1.0
    assert flat.estimate == 0.0
    assert flat.band is RecoveryBand.LIKELY_FATIGUED


# ---------------------------------------------------------------------------
# No new physiology
# ---------------------------------------------------------------------------


def test_no_decay_curve_is_introduced():
    source = _module_code()
    for forbidden in ("decay", "half_life", "halflife", "exp(", "math.e",
                      "0.72", "72 *", "48 *"):
        assert forbidden not in source, forbidden


def test_the_estimate_is_exactly_the_contract_formula():
    """hours / target, clamped — reached through the canonical normaliser."""
    from app.services.recovery_contract import normalize_training_suitability

    for zone, hours in (("quads", 36), ("pecs", 24), ("core", 12), ("calves", 18)):
        result = estimate_for_zone(zone, _evidence(zone, hours_ago=hours), now=NOW)
        assert result.estimate == normalize_training_suitability(hours, zone)


def test_the_estimate_saturates_rather_than_exceeding_one():
    result = estimate_for_zone("quads", _evidence("quads", hours_ago=5000),
                               now=NOW)
    assert result.estimate == 1.0
    assert result.band is RecoveryBand.LIKELY_AVAILABLE


def test_the_estimate_is_monotonic_in_elapsed_time():
    values = [
        estimate_for_zone("quads", _evidence("quads", hours_ago=h), now=NOW).estimate
        for h in (1, 6, 18, 36, 54, 71)
    ]
    assert values == sorted(values)
    assert len(set(values)) == len(values)


def test_a_recent_heavy_zone_reads_as_likely_fatigued():
    result = estimate_for_zone("quads", _evidence("quads", hours_ago=2), now=NOW)
    assert result.band is RecoveryBand.LIKELY_FATIGUED


# ---------------------------------------------------------------------------
# The never-trained fail-open
# ---------------------------------------------------------------------------


def test_a_zone_never_seen_is_unknown_not_available():
    """The fail-open this slice exists to close."""
    result = estimate_for_zone("quads", None, now=NOW)
    assert result.estimate is None
    assert result.estimate != 1.0
    assert result.band is RecoveryBand.UNKNOWN
    assert result.confidence is Confidence.NONE
    assert result.hours_since_last_load is None
    assert result.staleness is Sufficiency.INSUFFICIENT
    assert result.is_informative is False


def test_evidence_without_a_load_timestamp_is_also_unknown():
    result = estimate_for_zone("lats", _evidence("lats", hours_ago=None), now=NOW)
    assert result.estimate is None
    assert result.band is RecoveryBand.UNKNOWN


def test_a_brand_new_user_gets_eleven_explicitly_unknown_zones():
    estimates = build_zone_recovery_from_evidence({}, now=NOW)
    assert len(estimates) == len(ZONE_LABELS)
    assert all(e.estimate is None for e in estimates)
    assert all(e.band is RecoveryBand.UNKNOWN for e in estimates)
    assert all(e.confidence is Confidence.NONE for e in estimates)


def test_a_load_in_the_future_does_not_read_as_just_trained():
    """A clock skew must not become the strongest possible fatigue signal."""
    future = _ZoneEvidence(zone_code="pecs",
                           last_strength_load_at=NOW + timedelta(hours=5),
                           strength_occurrences=1,
                           resolution_paths={"db_lookup"})
    result = estimate_for_zone("pecs", future, now=NOW)
    assert result.estimate is None
    assert result.band is RecoveryBand.UNKNOWN


def test_an_unknown_zone_code_yields_no_estimate():
    result = estimate_for_zone("not_a_zone",
                               _evidence("not_a_zone", hours_ago=10), now=NOW)
    assert result.estimate is None
    assert result.band is RecoveryBand.UNKNOWN


# ---------------------------------------------------------------------------
# Divergence from the legacy path — enumerated, not discovered
# ---------------------------------------------------------------------------


def test_the_legacy_divergences_are_enumerated():
    assert LEGACY_DIVERGENCES
    for case, legacy, here in LEGACY_DIVERGENCES:
        # One assert per condition: a chained `and` cannot say which part
        # failed, and Sonar rejects it (python:S9073).
        assert case, LEGACY_DIVERGENCES
        assert legacy, case
        assert here, case
        assert "legacy:" in legacy, case
        assert "here:" in here, case


def test_the_never_trained_divergence_is_real_and_pinned():
    """The legacy formula really does return 1.0 where this returns None."""
    from app.services.recommendation import RECOVERY_HOURS_TARGET

    sentinel_hours = 24 * 365  # what build_signals writes for "never"
    legacy = max(0.0, min(1.0, sentinel_hours / RECOVERY_HOURS_TARGET["quads"]))
    assert legacy == 1.0

    ours = estimate_for_zone("quads", None, now=NOW)
    assert ours.estimate is None
    assert any("never-trained" in case for case, _, _ in LEGACY_DIVERGENCES)


def test_the_hours_sentinel_divergence_is_real():
    from app.services.recovery_contract import (
        NEVER_TRAINED_HOURS_SENTINEL,
        hours_since_last_or_none,
    )

    assert hours_since_last_or_none(NEVER_TRAINED_HOURS_SENTINEL) is None
    assert estimate_for_zone("quads", None, now=NOW).hours_since_last_load is None


# ---------------------------------------------------------------------------
# Cardio may lower confidence, never raise availability
# ---------------------------------------------------------------------------


def test_cardio_exposure_never_raises_the_estimate():
    without = estimate_for_zone("quads", _evidence("quads", hours_ago=36), now=NOW)
    with_cardio = estimate_for_zone(
        "quads", _evidence("quads", hours_ago=36, cardio=("velo",)), now=NOW)
    assert with_cardio.estimate == without.estimate


def test_cardio_exposure_lowers_confidence():
    without = estimate_for_zone("quads", _evidence("quads", hours_ago=36), now=NOW)
    with_cardio = estimate_for_zone(
        "quads", _evidence("quads", hours_ago=36, cardio=("velo",)), now=NOW)
    assert without.confidence is Confidence.MEDIUM
    assert with_cardio.confidence is Confidence.LOW
    assert "cardio_exposure" in with_cardio.contributing_signals


def test_cardio_only_exposure_stays_unknown():
    """Nothing places cardio exposure on a recovery clock in this slice."""
    result = estimate_for_zone(
        "quads", _evidence("quads", hours_ago=None, cardio=("rameur",)), now=NOW)
    assert result.estimate is None
    assert result.band is RecoveryBand.UNKNOWN
    assert result.confidence is Confidence.NONE
    assert "cardio_exposure" in result.contributing_signals
    assert any("not placed in time" in b for b in result.basis)


def test_confidence_never_reaches_high():
    for hours in (1, 12, 36, 200):
        for paths in (("db_lookup",), ("reviewed_correction",),
                      ("substring_fallback",), ("db_lookup", "substring_fallback")):
            for cardio in ((), ("velo",)):
                result = estimate_for_zone(
                    "quads",
                    _evidence("quads", hours_ago=hours, paths=paths, cardio=cardio),
                    now=NOW)
                assert result.confidence is not Confidence.HIGH


def test_a_substring_fallback_attribution_lowers_confidence():
    formal = estimate_for_zone(
        "quads", _evidence("quads", hours_ago=36, paths=("db_lookup",)), now=NOW)
    fallback = estimate_for_zone(
        "quads", _evidence("quads", hours_ago=36, paths=("substring_fallback",)),
        now=NOW)
    assert formal.confidence is Confidence.MEDIUM
    assert fallback.confidence is Confidence.LOW
    assert any("substring" in b for b in fallback.basis)


# ---------------------------------------------------------------------------
# Band over number, and the informativeness contract
# ---------------------------------------------------------------------------


def test_the_band_is_derivable_without_showing_the_number():
    result = estimate_for_zone("pecs", _evidence("pecs", hours_ago=48), now=NOW)
    assert result.band is RecoveryBand.LIKELY_AVAILABLE
    assert isinstance(result.band.value, str)


def test_an_informative_estimate_carries_confidence_and_basis():
    result = estimate_for_zone("pecs", _evidence("pecs", hours_ago=48), now=NOW)
    assert result.is_informative is True
    assert result.basis
    assert result.contributing_signals == ("strength_load",)


def test_the_basis_says_estimate_not_measurement():
    result = estimate_for_zone("pecs", _evidence("pecs", hours_ago=24), now=NOW)
    assert any("not a measurement" in b for b in result.basis)


# ---------------------------------------------------------------------------
# The canonical zone universe
# ---------------------------------------------------------------------------


def test_all_eleven_canonical_zones_are_always_returned():
    estimates = build_zone_recovery_from_evidence(
        {"quads": _evidence("quads", hours_ago=10)}, now=NOW)
    assert len(estimates) == len(ZONE_LABELS)
    assert [e.zone_code for e in estimates] == list(ZONE_LABELS)


def test_no_new_zone_taxonomy_is_declared():
    source = _module_code()
    assert "ZONE_LABELS = " not in source
    assert "_EXERCISE_PATTERNS" not in source
    assert canonical_zone_codes() == tuple(ZONE_LABELS)


def test_core_is_present_at_the_detailed_level():
    estimates = build_zone_recovery_from_evidence(
        {"core": _evidence("core", hours_ago=12)}, now=NOW)
    core = next(e for e in estimates if e.zone_code == "core")
    assert core.estimate is not None


# ---------------------------------------------------------------------------
# OQ-5 — macro roll-up is presentation only
# ---------------------------------------------------------------------------


def test_the_macro_rollup_reuses_the_p01_projection_rather_than_recopying_it():
    source = _module_code()
    assert "radar_axis_for_zone" in source
    for forbidden in ("ZONE_TO_RADAR_AXIS = ", "RADAR_AXES = ",
                      '"shoulders": ["delt_lat"'):
        assert forbidden not in source, forbidden


def test_the_macro_rollup_takes_the_worst_zone_and_names_it():
    estimates = build_zone_recovery_from_evidence({
        "quads": _evidence("quads", hours_ago=200),      # 1.0
        "posterior": _evidence("posterior", hours_ago=8),  # 8/72
        "calves": _evidence("calves", hours_ago=36),       # 1.0
    }, now=NOW)
    lower = next(a for a in build_macro_recovery(estimates) if a.axis_key == "lower")
    assert lower.limiting_zone_code == "posterior"
    assert lower.band is RecoveryBand.LIKELY_FATIGUED


def test_core_is_absent_from_the_macro_rollup():
    """`core` has no radar axis; it must not be attached to one."""
    assert radar_axis_for_zone("core") is None
    estimates = build_zone_recovery_from_evidence(
        {"core": _evidence("core", hours_ago=12)}, now=NOW)
    axes = build_macro_recovery(estimates)
    assert all(a.axis_key != "core" for a in axes)
    assert "core" not in {a.limiting_zone_code for a in axes}


def test_every_rollup_axis_is_a_real_radar_axis():
    from app.services.muscle_mapping import RADAR_AXIS_ORDER

    estimates = build_zone_recovery_from_evidence(
        {z: _evidence(z, hours_ago=24) for z in ZONE_LABELS}, now=NOW)
    for axis in build_macro_recovery(estimates):
        assert axis.axis_key in RADAR_AXIS_ORDER


def test_an_axis_with_an_unknown_zone_has_its_confidence_downgraded():
    estimates = build_zone_recovery_from_evidence({
        "biceps": _evidence("biceps", hours_ago=36),
        # triceps absent -> unknown
    }, now=NOW)
    arms = next(a for a in build_macro_recovery(estimates) if a.axis_key == "arms")
    assert arms.confidence is Confidence.LOW  # downgraded from the zone's MEDIUM
    assert any("triceps" in b for b in arms.basis)


def test_the_rollup_is_documented_as_presentation_only():
    doc = (inspect.getdoc(build_macro_recovery) or "").casefold()
    assert "presentation only" in doc


# ---------------------------------------------------------------------------
# Determinism, purity, wording
# ---------------------------------------------------------------------------


def test_the_pure_path_touches_no_database():
    source = _module_code()
    for forbidden in ("db.query", "select(", "db.execute", "SessionLocal",
                      "db.add", "db.commit"):
        assert forbidden not in source, forbidden


def test_the_module_reads_no_clock_of_its_own():
    source = _module_code()
    for forbidden in ("datetime.now(", "date.today(", "time.time("):
        assert forbidden not in source, forbidden


def test_estimates_are_deterministic():
    evidence = {"quads": _evidence("quads", hours_ago=36)}
    first = build_zone_recovery_from_evidence(evidence, now=NOW)
    second = build_zone_recovery_from_evidence(evidence, now=NOW)
    assert first == second


def test_naive_and_aware_timestamps_are_both_handled():
    """SQLite hands back naive datetimes for the repo's DateTime columns."""
    naive = _ZoneEvidence(
        zone_code="pecs",
        last_strength_load_at=(NOW - timedelta(hours=24)).replace(tzinfo=None),
        strength_occurrences=1, resolution_paths={"db_lookup"})
    aware = _evidence("pecs", hours_ago=24)
    assert estimate_for_zone("pecs", naive, now=NOW).estimate == \
        estimate_for_zone("pecs", aware, now=NOW).estimate


def test_the_module_never_claims_to_measure_a_body():
    from app.services.recovery_contract import FORBIDDEN_CONTRACT_WORDING

    surface = [inspect.getdoc(zr) or ""]
    for name in dir(zr):
        if name.startswith("_"):
            continue
        obj = getattr(zr, name)
        if inspect.isclass(obj) or inspect.isfunction(obj):
            surface.append(inspect.getdoc(obj) or "")
    haystack = " ".join(surface).casefold()
    for forbidden in FORBIDDEN_CONTRACT_WORDING:
        assert forbidden.casefold() not in haystack, forbidden


# ---------------------------------------------------------------------------
# End to end through the aggregator
# ---------------------------------------------------------------------------


def test_the_training_state_now_carries_the_estimates(client):
    # Every symbol is imported here, not at module level: the conftest purges
    # `app.*` between tests, so a module-level enum bound at collection time is
    # a *different class object* from the one a freshly imported service uses,
    # and `is` comparisons would fail for values that are in fact identical.
    from app.database import SessionLocal
    from app.models.session import SessionExercise, WorkoutSession
    from app.services.muscle_mapping import ZONE_LABELS
    from app.services.recovery_contract import RecoveryBand
    from app.services.training_state import build_training_state
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    with SessionLocal() as db:
        session = WorkoutSession(
            user_id=uid, template_slug_snapshot="push-a",
            template_name_snapshot="Push A", status="completed",
            started_at=NOW - timedelta(hours=12))
        session.session_exercises.append(SessionExercise(
            exercise_code_snapshot="E1",
            exercise_name_snapshot="Hack squat", position=1))
        db.add(session)
        db.commit()
        state = build_training_state(db, uid, now=NOW)

    by_zone = {e.zone_code: e for e in state.zone_recovery}
    assert len(by_zone) == len(ZONE_LABELS)
    quads = by_zone["quads"]
    assert quads.estimate == pytest.approx(12 / 72)
    assert quads.band is RecoveryBand.LIKELY_FATIGUED
    # A zone the session never touched stays explicitly unknown.
    assert by_zone["pecs"].estimate is None
    assert by_zone["pecs"].band is RecoveryBand.UNKNOWN


def test_the_database_path_matches_the_pure_path(client):
    # Same generation for both paths — see the note above.
    from app.database import SessionLocal
    from app.models.session import SessionExercise, WorkoutSession
    from app.services.training_state import zone_evidence_for
    from app.services.zone_recovery import (
        build_zone_recovery,
        build_zone_recovery_from_evidence,
    )
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    with SessionLocal() as db:
        session = WorkoutSession(
            user_id=uid, template_slug_snapshot="pull-a",
            template_name_snapshot="Pull A", status="completed",
            started_at=NOW - timedelta(hours=30))
        session.session_exercises.append(SessionExercise(
            exercise_code_snapshot="E1",
            exercise_name_snapshot="Traction pronation", position=1))
        db.add(session)
        db.commit()
        from_db = build_zone_recovery(db, uid, now=NOW)
        pure = build_zone_recovery_from_evidence(
            zone_evidence_for(db, uid, now=NOW), now=NOW)

    assert from_db == pure
