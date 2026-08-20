"""Sb_MORPHO_PROFILE_RUNTIME_01 — brancher de vraies mesures sur le moteur pur.

Ce fichier vérifie trois choses que le sprint promet et qu'un lecteur pressé
pourrait croire acquises : qu'il n'existe **qu'un** écrivain, qu'une envergure
non mesurée reste absente au lieu d'être fabriquée, et que le planificateur
n'a **rien** vu passer.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

# NOTE — no module-level `app.*` import in this file, on purpose.
#
# The `client` fixture drops every `app.*` entry from `sys.modules` and
# re-imports the package so a fresh `DATABASE_URL` takes effect. Anything this
# module imported at collection time would still reference the PREVIOUS
# generation of those modules — in particular a `SessionLocal` bound to an
# engine for a database that no longer exists. The failure reads as
# "no such table", which looks like a broken migration and is not one.
#
# So every application import lives inside a function, after the fixture has
# run. The neighbouring measurement tests already do this.


# Named once rather than repeated: Sonar's S1192 fires at three duplications
# of a literal, and a single MAJOR (weight 15) breaks the new-code gate
# (threshold 14) on its own.
MEASUREMENTS_URL = "/profile/measurements"
MEASURE_ERROR_URL = "/profile?measure_error=1"
WINGSPAN = "wingspan_cm"
MEASURED_AT = "measured_at"


@pytest.fixture(autouse=True)
def _app_db(client):
    """Bind every test here to the fixture-owned database and test user."""
    return client


def _add(db, uid, *, days_ago=0, **fields):
    from app.models.measurement import BodyMeasurement

    row = BodyMeasurement(
        user_id=uid,
        measured_at=datetime.now(UTC) - timedelta(days=days_ago),
        **fields,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _set_height(db, uid, height):
    from sqlalchemy import select

    from app.models.user import User

    db.execute(select(User).where(User.id == uid)).scalar_one().height_cm = height
    db.commit()


def _session():
    from app.database import SessionLocal

    return SessionLocal()


def _uid():
    from tests.helpers import get_test_user_id

    return get_test_user_id()


def _rows(db, uid):
    from sqlalchemy import select

    from app.models.measurement import BodyMeasurement

    return list(db.execute(
        select(BodyMeasurement)
        .where(BodyMeasurement.user_id == uid)
        .order_by(BodyMeasurement.id)
    ).scalars().all())


# ── L'écrivain canonique ─────────────────────────────────────────────────────


def test_the_route_writes_through_the_canonical_service(client, monkeypatch):
    """The form must not carry its own persistence any more."""
    from app.services import body_profile as bp

    seen: dict = {}
    real = bp.create_measurement

    def _spy(db, user_id, cleaned, *, measured_at=None):
        seen["cleaned"] = dict(cleaned)
        seen["measured_at"] = measured_at
        return real(db, user_id, cleaned, measured_at=measured_at)

    monkeypatch.setattr(bp, "create_measurement", _spy)

    client.post(MEASUREMENTS_URL, data={
        MEASURED_AT: "2026-04-12", "chest_cm": "100",
    }, follow_redirects=False)

    assert seen["cleaned"] == {"chest_cm": 100.0}
    # The user-supplied date survived the delegation.
    assert seen["measured_at"].date() == datetime(2026, 4, 12).date()


def test_the_route_no_longer_writes_the_legacy_calf_column(client):
    """`calf_cm` is readable history, not a write target.

    The submission below deliberately *includes* `calf_cm`. An earlier version
    of this test posted only the lateral fields, so the legacy column was never
    a write candidate and the assertion held no matter what the whitelist
    contained — it passed for the wrong reason. Re-adding `calf_cm` to
    `BODY_MEASUREMENT_FIELDS` left the whole file green, which is how the dead
    guard surfaced.
    """
    client.post(MEASUREMENTS_URL, data={
        "calf_cm_left": "38", "calf_cm_right": "38.5", "calf_cm": "37",
    }, follow_redirects=False)

    with _session() as db:
        row = _rows(db, _uid())[-1]
        assert row.calf_cm_left == 38.0
        assert row.calf_cm_right == 38.5
        # Submitted, accepted by the form, and deliberately not persisted.
        assert row.calf_cm is None


def test_the_canonical_whitelist_excludes_the_legacy_calf_column(client):
    """The structural half of the guard above."""
    from app.services import body_profile as bp

    assert "calf_cm" not in {s.key for s in bp.BODY_MEASUREMENT_FIELDS}
    assert {"calf_cm_left", "calf_cm_right"} <= {
        s.key for s in bp.BODY_MEASUREMENT_FIELDS
    }


def test_an_out_of_range_value_is_rejected_instead_of_silently_dropped(client):
    """The old parser turned 1750 cm into NULL and reported success."""
    with _session() as db:
        before = len(_rows(db, _uid()))

    r = client.post(MEASUREMENTS_URL, data={
        "chest_cm": "1750",
    }, follow_redirects=False)

    assert r.headers["location"] == MEASURE_ERROR_URL
    with _session() as db:
        assert len(_rows(db, _uid())) == before


def test_history_written_by_the_old_upsert_path_is_left_alone(client):
    """Rows that predate the unification stay exactly as they were."""
    with _session() as db:
        legacy = _add(db, _uid(), days_ago=400, chest_cm=90.0, calf_cm=36.0)
        legacy_id = legacy.id

    client.post(MEASUREMENTS_URL, data={"chest_cm": "101"},
                follow_redirects=False)

    with _session() as db:
        from app.models.measurement import BodyMeasurement

        still = db.get(BodyMeasurement, legacy_id)
        assert still.calf_cm == 36.0
        assert still.chest_cm == 90.0


# ── Envergure ────────────────────────────────────────────────────────────────


def test_a_valid_wingspan_is_accepted(client):
    client.post(MEASUREMENTS_URL, data={WINGSPAN: "182.5"},
                follow_redirects=False)
    with _session() as db:
        assert _rows(db, _uid())[-1].wingspan_cm == 182.5


@pytest.mark.parametrize("bad", ["119", "231", "abc"])
def test_an_implausible_wingspan_is_rejected(client, bad):
    r = client.post(MEASUREMENTS_URL, data={WINGSPAN: bad},
                    follow_redirects=False)
    assert r.headers["location"] == MEASURE_ERROR_URL


def test_a_missing_wingspan_stays_missing(client):
    """No height copy, no estimate, no zero."""
    from app.services.morphology_runtime import build_morphology_facts

    with _session() as db:
        _set_height(db, _uid(), 180)
    client.post(MEASUREMENTS_URL, data={"chest_cm": "100"},
                follow_redirects=False)
    with _session() as db:
        assert _rows(db, _uid())[-1].wingspan_cm is None
        bundle = build_morphology_facts(db, _uid())
    assert bundle.facts.wingspan_cm is None
    assert bundle.facts.height_cm == 180.0


def test_the_migration_never_backfills_wingspan(client):
    """Every pre-existing row must still read NULL."""
    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 178)
        for d in (10, 20, 30):
            _add(db, uid, days_ago=d, chest_cm=100.0)
        rows = _rows(db, uid)
        assert rows
        assert all(r.wingspan_cm is None for r in rows)


def test_ape_index_is_never_persisted():
    """It is a subtraction of two facts, not a fact."""
    from app.models.measurement import BodyMeasurement
    from app.services import body_profile as bp

    assert not hasattr(BodyMeasurement, "ape_index_cm")
    assert "ape_index_cm" not in {s.key for s in bp.BODY_MEASUREMENT_FIELDS}


# ── Ape index — dérivé, jamais stocké ────────────────────────────────────────


def test_height_and_wingspan_yield_a_derived_ape_index():
    from app.services.morphology_profile import build_morphology_profile
    from app.services.morphology_runtime import build_morphology_facts

    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, wingspan_cm=186.0)
        bundle = build_morphology_facts(db, uid)

    # The adapter hands over the two raw facts and derives nothing itself.
    assert bundle.facts.ape_index_cm is None
    assert bundle.facts.wingspan_cm == 186.0

    ape = [d for d in build_morphology_profile(bundle.facts)
           if d.descriptor_id == "slightly_positive_ape_index_not_extreme"]
    assert len(ape) == 1
    # 186 − 180 = 6, derived by the engine from two measured facts.
    assert ape[0].value == 6.0
    assert ape[0].confidence == "derived"


def test_height_without_wingspan_yields_no_ape_index():
    from app.services.morphology_profile import build_morphology_profile
    from app.services.morphology_runtime import build_morphology_facts

    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, chest_cm=100.0)
        bundle = build_morphology_facts(db, uid)

    ids = {d.descriptor_id for d in build_morphology_profile(bundle.facts)}
    assert "slightly_positive_ape_index_not_extreme" not in ids
    # And nothing filled the gap: no descriptor claims an ape index at all.
    assert not any("ape" in i for i in ids)


# ── Réduction latérale ───────────────────────────────────────────────────────


def test_both_thighs_reduce_to_their_mean():
    from app.services.morphology_runtime import (
        BASIS_BILATERAL_MEAN,
        build_morphology_facts,
    )

    with _session() as db:
        uid = _uid()
        _add(db, uid, thigh_cm_left=58.0, thigh_cm_right=60.0)
        bundle = build_morphology_facts(db, uid)
    assert bundle.facts.thigh_cm == 59.0
    assert bundle.provenance_for("thigh_cm").basis == BASIS_BILATERAL_MEAN


@pytest.mark.parametrize("side", ["left", "right"])
def test_a_single_thigh_side_is_used_alone_and_says_so(side):
    from app.services.morphology_runtime import (
        BASIS_SINGLE_SIDE_LEFT,
        BASIS_SINGLE_SIDE_RIGHT,
        build_morphology_facts,
    )

    expected = BASIS_SINGLE_SIDE_LEFT if side == "left" else BASIS_SINGLE_SIDE_RIGHT
    with _session() as db:
        uid = _uid()
        _add(db, uid, **{f"thigh_cm_{side}": 57.0})
        bundle = build_morphology_facts(db, uid)
    assert bundle.facts.thigh_cm == 57.0
    assert bundle.provenance_for("thigh_cm").basis == expected


def test_both_calves_reduce_to_their_mean():
    from app.services.morphology_runtime import (
        BASIS_BILATERAL_MEAN,
        build_morphology_facts,
    )

    with _session() as db:
        uid = _uid()
        _add(db, uid, calf_cm_left=37.0, calf_cm_right=39.0)
        bundle = build_morphology_facts(db, uid)
    assert bundle.facts.calf_cm == 38.0
    assert bundle.provenance_for("calf_cm").basis == BASIS_BILATERAL_MEAN


def test_the_legacy_calf_column_is_read_only_when_no_lateral_value_exists():
    from app.services.morphology_runtime import (
        BASIS_LEGACY_CALF,
        build_morphology_facts,
    )

    with _session() as db:
        uid = _uid()
        _add(db, uid, days_ago=5, calf_cm=35.0)
        bundle = build_morphology_facts(db, uid)
    assert bundle.facts.calf_cm == 35.0
    assert bundle.provenance_for("calf_cm").basis == BASIS_LEGACY_CALF


def test_lateral_values_win_over_the_legacy_column():
    from app.services.morphology_runtime import (
        BASIS_BILATERAL_MEAN,
        build_morphology_facts,
    )

    with _session() as db:
        uid = _uid()
        _add(db, uid, days_ago=5, calf_cm=35.0)
        _add(db, uid, days_ago=1, calf_cm_left=40.0, calf_cm_right=40.0)
        bundle = build_morphology_facts(db, uid)
    assert bundle.facts.calf_cm == 40.0
    assert bundle.provenance_for("calf_cm").basis == BASIS_BILATERAL_MEAN


def test_two_sides_are_never_averaged_across_different_measurements():
    """A left thigh from Tuesday and a right from January is not a thigh."""
    from app.services.morphology_runtime import (
        BASIS_SINGLE_SIDE_LEFT,
        build_morphology_facts,
    )

    with _session() as db:
        uid = _uid()
        _add(db, uid, days_ago=90, thigh_cm_right=50.0)
        _add(db, uid, days_ago=1, thigh_cm_left=60.0)
        bundle = build_morphology_facts(db, uid)
    # 55.0 would be the fabricated mean of two unrelated dates.
    assert bundle.facts.thigh_cm == 60.0
    assert bundle.provenance_for("thigh_cm").basis == BASIS_SINGLE_SIDE_LEFT


# ── Traçabilité temporelle ───────────────────────────────────────────────────


def test_a_single_measurement_profile_is_labelled_as_such():
    from app.services.morphology_runtime import (
        PROFILE_SINGLE_MEASUREMENT,
        build_morphology_facts,
    )

    with _session() as db:
        uid = _uid()
        _add(db, uid, waist_cm=80.0, chest_cm=100.0)
        bundle = build_morphology_facts(db, uid)
    assert bundle.profile_kind == PROFILE_SINGLE_MEASUREMENT
    assert bundle.is_mixed_date is False


def test_facts_from_several_dates_are_labelled_latest_known_facts():
    from app.services.morphology_runtime import (
        PROFILE_LATEST_KNOWN_FACTS,
        build_morphology_facts,
    )

    with _session() as db:
        uid = _uid()
        _add(db, uid, days_ago=60, chest_cm=100.0)
        _add(db, uid, days_ago=1, waist_cm=80.0)
        bundle = build_morphology_facts(db, uid)

    assert bundle.profile_kind == PROFILE_LATEST_KNOWN_FACTS
    assert bundle.is_mixed_date is True
    assert len(bundle.measurement_dates) == 2
    # Each fact still names the row it came from.
    assert bundle.provenance_for("chest_cm").measurement_id != \
        bundle.provenance_for("waist_cm").measurement_id


def test_every_measured_fact_carries_its_row_and_its_date():
    from app.services.morphology_runtime import (
        SOURCE_MEASUREMENT,
        build_morphology_facts,
    )

    with _session() as db:
        uid = _uid()
        row = _add(db, uid, waist_cm=80.0)
        bundle = build_morphology_facts(db, uid)
    p = bundle.provenance_for("waist_cm")
    assert p.measurement_id == row.id
    assert p.measured_at is not None
    assert p.source == SOURCE_MEASUREMENT


def test_height_is_sourced_from_the_profile_not_from_a_measurement():
    from app.services.morphology_runtime import (
        SOURCE_USER_PROFILE,
        build_morphology_facts,
    )

    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 175)
        _add(db, uid, waist_cm=80.0)
        bundle = build_morphology_facts(db, uid)
    p = bundle.provenance_for("height_cm")
    assert p.source == SOURCE_USER_PROFILE
    assert p.measurement_id is None


def test_a_user_without_measurements_yields_an_empty_profile():
    from app.services.morphology_runtime import (
        PROFILE_EMPTY,
        build_morphology_facts,
    )

    with _session() as db:
        bundle = build_morphology_facts(db, _uid())
    assert bundle.profile_kind == PROFILE_EMPTY
    assert bundle.facts.waist_cm is None


def test_as_of_replays_the_profile_as_it_was():
    from app.services.morphology_runtime import build_morphology_facts

    with _session() as db:
        uid = _uid()
        _add(db, uid, days_ago=30, waist_cm=85.0)
        _add(db, uid, days_ago=1, waist_cm=80.0)
        past = build_morphology_facts(
            db, uid, as_of=datetime.now(UTC) - timedelta(days=10)
        )
        now = build_morphology_facts(db, uid)
    assert past.facts.waist_cm == 85.0
    assert now.facts.waist_cm == 80.0


# ── Séparation déclaré / inféré ──────────────────────────────────────────────


def test_declared_preferences_never_enter_the_morphology_facts():
    """A declared priority and an inferred candidate are different sources."""
    from app.services.morphology_runtime import build_morphology_facts
    from app.services.training_preferences import (
        get_training_preferences,
        save_training_preferences,
    )

    with _session() as db:
        uid = _uid()
        save_training_preferences(
            db, uid, sessions_per_week=4,
            focus_priorities=["arms"], available_equipment=["barbell"],
        )
        _add(db, uid, waist_cm=80.0)
        bundle = build_morphology_facts(db, uid)
        declared = get_training_preferences(db, uid)

    # The declaration exists and is readable — it simply does not leak into
    # the engine input, where it would become indistinguishable from an
    # inferred candidate.
    assert "arms" in declared.focus_priorities
    assert bundle.facts.focus_candidates == ()


# ── Propriété ────────────────────────────────────────────────────────────────


def test_another_users_measurements_are_invisible():
    from app.models.user import User
    from app.services.morphology_runtime import build_morphology_facts

    with _session() as db:
        uid = _uid()
        other = User(username="morpho_other", password_hash="x")
        db.add(other)
        db.commit()
        db.refresh(other)
        _add(db, other.id, waist_cm=99.0)

        mine = build_morphology_facts(db, uid)
        theirs = build_morphology_facts(db, other.id)

    assert mine.facts.waist_cm is None
    assert theirs.facts.waist_cm == 99.0


# ── Garde-fous de capture ────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "banned",
    ["photo", "image", "body_fat", "bodyfat", "masse_grasse", "posture",
     "femur", "humerus", "bone", "insertion"],
)
def test_the_capture_whitelist_admits_no_forbidden_field(banned):
    from app.services import body_profile as bp

    keys = " ".join(s.key for s in bp.BODY_MEASUREMENT_FIELDS).lower()
    assert banned not in keys


def _capture_form(client) -> str:
    """The measurement form only — not the whole profile page.

    Scoped deliberately. The page also renders workout-template names, and the
    catalog happens to contain one called "full body — morphotype priority".
    That string is a pre-existing catalog label, not a capture prompt, and it
    is outside this slice's perimeter; asserting against the entire page would
    make this guard fail for a reason it is not designed to catch.
    """
    page = client.get("/profile").text
    # `url_for` renders an absolute URL (http://testserver/...), so anchor on
    # the path's tail rather than on `action="/profile/measurements"`.
    #
    # ⚠ `UX4_01` — s'ancrer sur la PREMIÈRE occurrence de cette URL ne suffit
    # plus : le quick-log de poids poste vers la MÊME route canonique et vient
    # avant dans la page. La garde lisait donc un formulaire à un champ et
    # concluait que le protocole d'envergure avait disparu.
    #
    # L'intention de ce helper — « le formulaire de mesure SEULEMENT » — était
    # juste ; c'est son ancrage qui ne l'était plus. On vise la classe qui
    # identifie la saisie complète.
    start = page.index('class="body-profile"')
    return page[start:page.index("</form>", start)].lower()


@pytest.mark.parametrize(
    "banned",
    ["photo", "body fat", "masse grasse", "posture", "fémur", "humérus",
     "insertion", "morphotype", "pli cutané", "impédance"],
)
def test_the_capture_form_never_asks_for_a_forbidden_fact(client, banned):
    assert banned not in _capture_form(client)


def test_the_capture_form_offers_no_file_or_image_input(client):
    form = _capture_form(client)
    assert 'type="file"' not in form
    assert "<img" not in form


def test_the_form_tells_the_user_to_measure_rather_than_estimate(client):
    form = _capture_form(client)
    assert "laisse vide" in form
    # "estimate if unsure" is exactly the instruction the spec forbids.
    assert "estime" not in form
    assert "au jugé" not in form


def test_the_wingspan_field_states_one_consistent_protocol(client):
    form = _capture_form(client)
    assert WINGSPAN in form
    assert "majeur" in form          # fingertip-to-fingertip, named concretely
    assert "même protocole" in form


def test_the_aggregation_guard_claims_no_physiology():
    from app.services.morphology_runtime import AGGREGATION_GUARD

    low = AGGREGATION_GUARD.lower()
    assert "convention" in low
    assert "aucune lecture de symetrie" in low


# ── Isolation du planificateur ───────────────────────────────────────────────
#
# Le train gèle la sortie du planificateur tant que le dogfood réel n'a pas
# statué. Ces gardes existent pour que « la morphologie n'influence pas encore
# le programme » soit une propriété vérifiée, pas une intention.

FROZEN_PLANNER_MODULES = (
    "weekly_volume_budget",
    "weekly_planner",
    "weekly_capacity_allocator",
    "weekly_set_allocation",
    "weekly_plan_materialization",
    "set_contribution",
    "adaptive_replan",
    "recommendation",
)


@pytest.mark.parametrize("module_name", FROZEN_PLANNER_MODULES)
def test_no_frozen_planner_module_imports_the_morphology_runtime(module_name):
    """The consumer does not exist yet, and must not appear by accident."""
    import pathlib

    import app.services as services_pkg

    path = pathlib.Path(services_pkg.__file__).parent / f"{module_name}.py"
    source = path.read_text(encoding="utf-8")
    assert "morphology_runtime" not in source
    assert "morphology_profile" not in source


def test_the_planner_cannot_reach_a_database_at_all():
    """Structural isolation: measurements are not reachable from a pure call."""
    import inspect

    from app.services.weekly_planner import build_weekly_plan

    params = set(inspect.signature(build_weekly_plan).parameters)
    assert params == {"preferences", "budget", "pool"}
    assert "db" not in params
    assert "user_id" not in params


def test_recorded_morphology_does_not_move_the_weekly_plan():
    """Behavioural isolation, measured rather than asserted.

    The same declared preferences must produce the same plan fingerprint
    before and after a full set of morphology facts lands in the database.
    """
    from app.services.morphology_runtime import build_morphology_facts
    from app.services.training_preferences import TrainingPreferencesData
    from app.services.weekly_planner import build_weekly_plan

    prefs = TrainingPreferencesData(
        sessions_per_week=4, focus_priorities=("arms",),
    )
    before = build_weekly_plan(prefs)

    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, wingspan_cm=188.0, waist_cm=78.0, chest_cm=104.0,
             thigh_cm_left=60.0, thigh_cm_right=60.0,
             calf_cm_left=38.0, calf_cm_right=38.0)
        bundle = build_morphology_facts(db, uid)

    # The morphology really is populated — otherwise this proves nothing.
    assert bundle.facts.wingspan_cm == 188.0
    assert bundle.facts.thigh_cm == 60.0

    after = build_weekly_plan(prefs)
    assert after.fingerprint == before.fingerprint
    assert after.planner_version == before.planner_version


def test_recorded_morphology_does_not_move_the_volume_budget():
    from app.services.morphology_runtime import build_morphology_facts
    from app.services.training_preferences import TrainingPreferencesData
    from app.services.weekly_volume_budget import build_weekly_volume_budget

    prefs = TrainingPreferencesData(
        sessions_per_week=4, focus_priorities=("arms",),
    )
    before = build_weekly_volume_budget(prefs)

    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, wingspan_cm=188.0, waist_cm=78.0, chest_cm=104.0)
        assert build_morphology_facts(db, uid).facts.wingspan_cm == 188.0

    after = build_weekly_volume_budget(prefs)
    assert [(z.zone_code, z.planning_low_sets, z.planning_high_sets)
            for z in after.zones] == \
        [(z.zone_code, z.planning_low_sets, z.planning_high_sets)
         for z in before.zones]
