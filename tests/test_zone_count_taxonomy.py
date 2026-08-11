"""Sb_ZONE_COUNT_TAXONOMY_FIX_01 — detailed zone → radar axis projection.

The defect: ``_zone_session_counts`` keyed its accumulator on the 6 macro radar
axes but fed it the *detailed* zone returned by ``classify_exercise``, behind an
``if z in counts`` guard. ``pecs`` is the only label that exists at both
taxonomic levels, so it was the only axis that could ever increment. Every other
axis — shoulders, back_width, back_thickness, arms, lower — was structurally
pinned to 0, which made "zone travaillée / peu travaillée", the coach report and
the Body Intelligence radar report an artefact of that accidental overlap rather
than of actual training.

These tests pin the projection itself (pure, derived from ``RADAR_AXES``), the
session-counting semantics, and the fact that the two downstream consumers named
by the spec — coach inference and Body Intelligence input — now receive the
corrected values.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.services.muscle_mapping import (
    RADAR_AXES,
    RADAR_AXIS_ORDER,
    ZONE_LABELS,
    ZONE_TO_RADAR_AXIS,
    classify_exercise,
    radar_axis_for_zone,
)
from tests.helpers import get_test_user_id

# Exercise names whose *detailed* classification is pinned below, so the
# fixtures stay truthful if the substring patterns ever move.
CHEST = "Développé couché barre"
DELT_LAT = "Élévation latérale haltères"
DELT_POST = "Face pull poulie"
LATS = "Traction pronation"
UPPER_BACK = "Rowing barre"
BICEPS = "Curl incliné haltères"
TRICEPS = "Pushdown corde"
QUADS = "Hack squat"
POSTERIOR = "Leg curl allongé"
CALVES = "Mollets debout"
CORE = "Crunch au sol"


# ---------------------------------------------------------------------------
# The projection itself (pure — no DB, no session)
# ---------------------------------------------------------------------------


def test_projection_is_derived_from_the_canonical_radar_axes():
    """``ZONE_TO_RADAR_AXIS`` must be the inverse of ``RADAR_AXES``.

    ``RADAR_AXES`` is the mapping the architecture already designates as
    canonical: ``muscle_scoring`` aggregates zone scores through it and
    ``test_auren_body_zone_contract`` pins it. Deriving the inverse rather than
    hand-writing it is what prevents a competing table from drifting.
    """
    expected = {
        zone: axis
        for axis in RADAR_AXIS_ORDER
        for zone in RADAR_AXES[axis]["zones"]
    }
    assert ZONE_TO_RADAR_AXIS == expected


def test_every_projected_axis_is_a_real_radar_axis():
    assert set(ZONE_TO_RADAR_AXIS.values()) <= set(RADAR_AXIS_ORDER)


def test_every_detailed_zone_except_core_projects_onto_an_axis():
    """The 11 detailed zones minus ``core`` cover the 6 axes exactly."""
    projected = {z for z in ZONE_LABELS if radar_axis_for_zone(z) is not None}
    assert projected == set(ZONE_LABELS) - {"core"}
    assert set(ZONE_TO_RADAR_AXIS[z] for z in projected) == set(RADAR_AXIS_ORDER)


def test_core_has_no_radar_axis_and_is_not_fabricated():
    """``core`` is a detailed zone with no radar axis — it must stay unmapped.

    ``test_auren_bodymap_master`` pins "core" in CANONICAL_MACROS and not in
    RADAR_AXIS_ORDER. Forcing it onto an axis would invent taxonomy.
    """
    assert "core" in ZONE_LABELS
    assert radar_axis_for_zone("core") is None


def test_unknown_and_macro_keys_do_not_project():
    assert radar_axis_for_zone("unknown") is None
    assert radar_axis_for_zone("") is None
    # Macro keys are not detailed zones; only "pecs" legitimately overlaps.
    assert radar_axis_for_zone("shoulders") is None
    assert radar_axis_for_zone("back_width") is None
    assert radar_axis_for_zone("pecs") == "pecs"


def test_detailed_zone_of_each_fixture_exercise_is_what_we_claim():
    """Guards the fixtures below against a substring-pattern change."""
    pinned = {
        CHEST: "pecs",
        DELT_LAT: "delt_lat",
        DELT_POST: "delt_post",
        LATS: "lats",
        UPPER_BACK: "upper_back",
        BICEPS: "biceps",
        TRICEPS: "triceps",
        QUADS: "quads",
        POSTERIOR: "posterior",
        CALVES: "calves",
        CORE: "core",
    }
    for name, zone in pinned.items():
        assert classify_exercise(name)[0] == zone, name


def test_each_family_projects_onto_its_expected_axis():
    """The four families the spec calls out by name, end to end."""
    assert radar_axis_for_zone(classify_exercise(CHEST)[0]) == "pecs"
    assert radar_axis_for_zone(classify_exercise(DELT_LAT)[0]) == "shoulders"
    assert radar_axis_for_zone(classify_exercise(DELT_POST)[0]) == "shoulders"
    assert radar_axis_for_zone(classify_exercise(LATS)[0]) == "back_width"
    assert radar_axis_for_zone(classify_exercise(UPPER_BACK)[0]) == "back_thickness"
    assert radar_axis_for_zone(classify_exercise(BICEPS)[0]) == "arms"
    assert radar_axis_for_zone(classify_exercise(TRICEPS)[0]) == "arms"
    assert radar_axis_for_zone(classify_exercise(QUADS)[0]) == "lower"
    assert radar_axis_for_zone(classify_exercise(POSTERIOR)[0]) == "lower"
    assert radar_axis_for_zone(classify_exercise(CALVES)[0]) == "lower"


# ---------------------------------------------------------------------------
# Seeding helper
# ---------------------------------------------------------------------------


def _seed_session(db, user_id, exercise_names, *, days_ago=1,
                  status="completed", excluded=False, substituted=None):
    """Create one session holding ``exercise_names``.

    ``substituted`` maps a snapshot name to the name actually performed, so the
    substituted_name-precedence test uses the same seeding path as the others.
    """
    from app.models.session import SessionExercise, WorkoutSession

    s = WorkoutSession(
        user_id=user_id,
        template_slug_snapshot="push-a",
        template_name_snapshot="Push A",
        started_at=datetime.now(UTC) - timedelta(days=days_ago),
        status=status,
        excluded_from_stats=excluded,
    )
    for i, name in enumerate(exercise_names, start=1):
        s.session_exercises.append(SessionExercise(
            exercise_code_snapshot=f"ZC{i}",
            exercise_name_snapshot=name,
            substituted_name=(substituted or {}).get(name),
            position=i,
        ))
    db.add(s)
    db.commit()
    return s


def _counts_for(db, user_id):
    from app.services.profile_metrics import zone_session_counts

    return zone_session_counts(db, user_id, 30)


# ---------------------------------------------------------------------------
# Session counting
# ---------------------------------------------------------------------------


def test_each_family_reaches_its_axis_through_the_real_counter(client):
    """One session per family — every axis must be reachable, not just pecs."""
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _seed_session(db, uid, [CHEST], days_ago=1)
        _seed_session(db, uid, [DELT_LAT], days_ago=2)
        _seed_session(db, uid, [LATS], days_ago=3)
        _seed_session(db, uid, [UPPER_BACK], days_ago=4)
        _seed_session(db, uid, [BICEPS], days_ago=5)
        _seed_session(db, uid, [QUADS], days_ago=6)
        counts = _counts_for(db, uid)

    assert counts == {
        "pecs": 1,
        "shoulders": 1,
        "back_width": 1,
        "back_thickness": 1,
        "arms": 1,
        "lower": 1,
    }


def test_regression_non_pecs_zone_no_longer_disappears(client):
    """The old bug, stated explicitly.

    Before the fix this dataset produced ``{pecs: 0, shoulders: 0, ...}``:
    ``delt_lat`` was not a key of a macro-keyed dict, so ``if z in counts``
    dropped it silently. It must now count.
    """
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _seed_session(db, uid, [DELT_LAT], days_ago=1)
        counts = _counts_for(db, uid)

    assert counts["shoulders"] == 1
    assert sum(counts.values()) == 1


def test_two_distinct_axes_are_non_zero_in_the_same_dataset(client):
    """Impossible before the fix: only ``pecs`` could ever be non-zero."""
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _seed_session(db, uid, [CHEST, TRICEPS], days_ago=1)
        _seed_session(db, uid, [QUADS], days_ago=2)
        counts = _counts_for(db, uid)

    non_zero = {k for k, v in counts.items() if v > 0}
    assert non_zero == {"pecs", "arms", "lower"}
    assert len(non_zero) >= 2


def test_session_counts_once_per_axis_not_once_per_exercise(client):
    """``delt_lat`` + ``delt_post`` in one session is ONE shoulders session."""
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _seed_session(db, uid, [DELT_LAT, DELT_POST], days_ago=1)
        counts = _counts_for(db, uid)

    assert counts["shoulders"] == 1


def test_three_lower_zones_in_one_session_count_once(client):
    """quads + posterior + calves all fold into ``lower`` — still one."""
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _seed_session(db, uid, [QUADS, POSTERIOR, CALVES], days_ago=1)
        counts = _counts_for(db, uid)

    assert counts["lower"] == 1


def test_distinct_sessions_on_the_same_axis_accumulate(client):
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _seed_session(db, uid, [DELT_LAT], days_ago=1)
        _seed_session(db, uid, [DELT_POST], days_ago=2)
        _seed_session(db, uid, [DELT_LAT, DELT_POST], days_ago=3)
        counts = _counts_for(db, uid)

    assert counts["shoulders"] == 3


def test_core_only_session_contributes_to_no_axis(client):
    """``core`` has no radar axis — it must not be forced onto one."""
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _seed_session(db, uid, [CORE], days_ago=1)
        counts = _counts_for(db, uid)

    assert set(counts) == set(RADAR_AXIS_ORDER)
    assert sum(counts.values()) == 0


def test_unclassifiable_exercise_contributes_to_no_axis(client):
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _seed_session(db, uid, ["Zzz Machine Inconnue"], days_ago=1)
        counts = _counts_for(db, uid)

    assert sum(counts.values()) == 0


def test_substituted_name_still_takes_precedence(client):
    """Snapshot says chest, the athlete actually did a lateral raise."""
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _seed_session(db, uid, [CHEST], days_ago=1,
                      substituted={CHEST: DELT_LAT})
        counts = _counts_for(db, uid)

    assert counts["shoulders"] == 1
    assert counts["pecs"] == 0


def test_filters_are_preserved(client):
    """Non-completed and excluded_from_stats sessions still do not count."""
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _seed_session(db, uid, [DELT_LAT], days_ago=1, status="in_progress")
        _seed_session(db, uid, [LATS], days_ago=2, excluded=True)
        _seed_session(db, uid, [QUADS], days_ago=400)
        counts = _counts_for(db, uid)

    assert sum(counts.values()) == 0


# ---------------------------------------------------------------------------
# top_zone / neglected_zone
# ---------------------------------------------------------------------------


def test_top_zone_can_now_be_a_non_pecs_axis(client):
    from app.database import SessionLocal
    from app.services.profile_metrics import top_zone

    uid = get_test_user_id()
    with SessionLocal() as db:
        _seed_session(db, uid, [CHEST], days_ago=1)
        _seed_session(db, uid, [QUADS], days_ago=2)
        _seed_session(db, uid, [POSTERIOR], days_ago=3)
        tz = top_zone(db, uid)

    assert tz is not None
    assert tz.zone == "lower"
    assert tz.sessions == 2


def test_top_and_neglected_zone_remain_deterministic(client):
    """Same dataset, repeated reads — identical verdicts (tie-break intact)."""
    from app.database import SessionLocal
    from app.services.profile_metrics import neglected_zone, top_zone

    uid = get_test_user_id()
    with SessionLocal() as db:
        _seed_session(db, uid, [CHEST], days_ago=1)
        _seed_session(db, uid, [DELT_LAT], days_ago=2)
        first_top = top_zone(db, uid)
        second_top = top_zone(db, uid)
        first_neg = neglected_zone(db, uid)
        second_neg = neglected_zone(db, uid)

    assert first_top == second_top
    assert first_neg == second_neg
    # pecs and shoulders tie at 1 → RADAR_AXIS_ORDER breaks it toward pecs.
    assert first_top is not None
    assert first_top.zone == "pecs"
    # Lowest count wins, earliest axis in RADAR_AXIS_ORDER breaks the tie.
    assert first_neg is not None
    assert first_neg.zone == "back_width"
    assert first_neg.sessions == 0


# ---------------------------------------------------------------------------
# Downstream consumers named by the spec
# ---------------------------------------------------------------------------


def test_coach_report_zones_are_labelled_macro_axes(client):
    """``coach_report._zones`` labels through ``RADAR_AXES`` — keys must match.

    Before the fix every non-pecs entry was labelled but pinned at 0.
    """
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.coach_report import build_report

    uid = get_test_user_id()
    with SessionLocal() as db:
        _seed_session(db, uid, [DELT_LAT], days_ago=1)
        _seed_session(db, uid, [DELT_POST], days_ago=2)
        _seed_session(db, uid, [DELT_LAT], days_ago=3)
        user = db.get(User, uid)
        report = build_report(db, user)

    counts = {key: n for key, _label, n in report.zones.counts}
    assert counts["shoulders"] == 3
    labels = {key: label for key, label, _n in report.zones.counts}
    assert labels["shoulders"] == RADAR_AXES["shoulders"]["label"]


def test_coach_inference_receives_corrected_values(client):
    """A shoulders-only athlete must be told shoulders is a strong point.

    ``strong_points`` needs ≥ TOP_ZONE_MIN_SESSIONS on a top zone. Before the
    fix shoulders could not exceed 0, so this line was unreachable for every
    axis except pecs.
    """
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.coach_inference import TOP_ZONE_MIN_SESSIONS, strong_points
    from app.services.coach_report import build_report

    uid = get_test_user_id()
    with SessionLocal() as db:
        for d in range(1, TOP_ZONE_MIN_SESSIONS + 1):
            _seed_session(db, uid, [DELT_LAT], days_ago=d)
        user = db.get(User, uid)
        report = build_report(db, user)
        points = strong_points(report)

    top = {key: n for key, _label, n in report.zones.top_zones}
    assert top.get("shoulders") == TOP_ZONE_MIN_SESSIONS
    assert any(RADAR_AXES["shoulders"]["label"] in p for p in points)


def test_body_intelligence_input_receives_corrected_values(client):
    """The BI radar input carried its own duplicate zone→axis table.

    With the projection moved upstream, that table would have dropped every
    axis but ``pecs`` a second time. It is gone; BI now sees real counts.
    """
    from app.database import SessionLocal
    from app.services.body_intelligence_inputs import _radar_zone_counts

    uid = get_test_user_id()
    with SessionLocal() as db:
        _seed_session(db, uid, [LATS], days_ago=1)
        _seed_session(db, uid, [QUADS], days_ago=2)
        _seed_session(db, uid, [QUADS], days_ago=3)
        axis_counts = _radar_zone_counts(db, uid, days=30)

    assert set(axis_counts) == set(RADAR_AXIS_ORDER)
    assert axis_counts["back_width"] == 1
    assert axis_counts["lower"] == 2
    assert axis_counts["pecs"] == 0


def test_body_intelligence_input_is_always_the_full_six_axes(client):
    """No sessions at all must still yield six zeros, never an empty dict.

    The composer keys ``undertrained_zone`` off the full structure, so an
    absent axis and an axis at zero are not interchangeable. A ``return {}``
    short-circuit used to sit here; it was unreachable, and had it fired it
    would have broken exactly that guarantee.
    """
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.user import User
    from app.services.auth import hash_password
    from app.services.body_intelligence_inputs import _radar_zone_counts

    with SessionLocal() as db:
        db.add(User(username="bi_no_data",
                    password_hash=hash_password("anything1"), is_active=True))
        db.commit()
        uid = db.execute(
            select(User.id).where(User.username == "bi_no_data")
        ).scalar_one()
        axis_counts = _radar_zone_counts(db, uid, days=30)

    assert axis_counts == dict.fromkeys(RADAR_AXIS_ORDER, 0)


def test_body_intelligence_input_no_longer_holds_a_second_mapping(client):
    """No sixth table: the BI module must not redefine zone→axis.

    Pinned on the source because the regression it guards is "someone
    reintroduces a local mapping dict", which behaves correctly in isolation
    and only breaks the single-projection-boundary invariant.
    """
    from pathlib import Path

    import app.services.body_intelligence_inputs as bii

    source = Path(bii.__file__).read_text(encoding="utf-8")
    assert '"delt_lat": "shoulders"' not in source
    assert '"upper_back": "back_thickness"' not in source


def test_body_intelligence_composer_sees_a_non_pecs_axis_as_trained(client):
    """End to end: a non-pecs axis can now drive the undertrained verdict.

    ``_undertrained_zones`` only speaks once some axis clears
    ``UNDERTRAINED_OTHER_ZONE_MIN``. Before the fix only ``pecs`` could clear
    it, so a shoulders-only athlete got an empty verdict — and if the verdict
    did fire, ``shoulders`` was itself listed as untrained.
    """
    from app.database import SessionLocal
    from app.services.body_intelligence import (
        UNDERTRAINED_OTHER_ZONE_MIN,
        _undertrained_zones,
    )
    from app.services.body_intelligence_inputs import _radar_zone_counts

    uid = get_test_user_id()
    with SessionLocal() as db:
        for d in range(1, UNDERTRAINED_OTHER_ZONE_MIN + 1):
            _seed_session(db, uid, [DELT_LAT], days_ago=d)
        axis_counts = _radar_zone_counts(db, uid, days=30)

    assert axis_counts["shoulders"] >= UNDERTRAINED_OTHER_ZONE_MIN
    under = _undertrained_zones(axis_counts)
    assert "shoulders" not in under
    assert "pecs" in under
    assert "lower" in under
