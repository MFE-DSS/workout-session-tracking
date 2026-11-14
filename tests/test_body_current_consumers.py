"""A correction is not another weighing or an anthropometric trend."""

from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from test_body_measurement_commands import correction

pytest_plugins = ["test_body_measurement_commands"]


def test_canonical_wrapper_returns_new_version_without_mutating_original(body_db):
    from app.models.measurement import BodyMeasurement
    from app.services import body_profile as bp

    original = bp.create_measurement(body_db, 1, {"weight_kg": 80, "waist_cm": 90})
    fixed = bp.update_measurement(body_db, original, {"waist_cm": 85}, champs_soumis={"waist_cm"})
    assert fixed.id != original.id
    body_db.refresh(original)
    assert (original.weight_kg, original.waist_cm) == (80, 90)
    assert (fixed.weight_kg, fixed.waist_cm) == (80, 85)
    assert [r.id for r in bp.list_measurements(body_db, 1)] == [fixed.id]
    assert len(list(body_db.scalars(select(BodyMeasurement)))) == 2


@pytest.mark.parametrize(
    "consumer",
    [
        "profile",
        "ledger",
        "morphology",
        "weight_v1",
        "latest",
        "series",
        "inputs",
        "score",
        "dashboard",
        "coach",
    ],
)
def test_current_readers_do_not_count_or_resurrect_superseded_facts(body_db, consumer):
    from app.services import body_profile as bp
    from app.services.body_measurement_commands import apply_command

    first = apply_command(
        body_db,
        1,
        {
            "request_id": "current-read-fact",
            "operation": "CREATE",
            "measured_on": datetime.now(UTC).date().isoformat(),
            "values": {"weight_kg": 80, "waist_cm": 90},
        },
        source="MANUAL_ENTRY",
    )
    fixed = correction(
        body_db,
        first["root_ref"],
        {"weight_kg": None, "waist_cm": 80},
        date="2020-01-01" if consumer == "latest" else None,
    )
    if consumer == "profile":
        assert [r.id for r in bp.list_measurements(body_db, 1)] == [fixed["measurement_id"]]
    elif consumer == "ledger":
        from app.services.body_ledger import _mesures

        assert [r.id for r in _mesures(body_db, 1)] == [fixed["measurement_id"]]
    elif consumer == "morphology":
        from app.services.morphology_runtime import _measurements

        assert [r.id for r in _measurements(body_db, 1, None)] == [fixed["measurement_id"]]
    elif consumer == "weight_v1":
        assert bp.list_weight_measurements(body_db, 1) == []
    elif consumer == "latest":
        from app.services.measurements import get_latest_measurement

        assert get_latest_measurement(body_db, 1).id == fixed["measurement_id"]
    elif consumer == "series":
        from app.services.measurements import get_measurement_series

        assert get_measurement_series(body_db, 1, "weight_kg") == []
    elif consumer == "inputs":
        from app.services.body_intelligence_inputs import (
            _latest_waist_measurement,
            _latest_weight_measurement,
        )

        assert _latest_weight_measurement(body_db, 1) == (None, None)
        assert _latest_waist_measurement(body_db, 1) == 80
    elif consumer == "score":
        from app.services.muscle_scoring import _score_anthropo

        assert _score_anthropo(body_db, 1, "core", datetime(2020, 1, 1, tzinfo=UTC)) == (None, None)
    elif consumer == "dashboard":
        from app.services.dashboard import compute_body_trend_axis

        axis = compute_body_trend_axis(body_db, 1)
        assert axis.active is False
        assert axis.detail.startswith("1 mesure(s)")
    else:
        from datetime import timedelta

        from app.services.coach_report import _weight_trend_90d

        apply_command(
            body_db,
            1,
            {
                "request_id": "other-actual-weighing",
                "operation": "CREATE",
                "measured_on": (datetime.now(UTC).date() - timedelta(days=1)).isoformat(),
                "values": {"weight_kg": 70},
            },
            source="MANUAL_ENTRY",
        )
        assert _weight_trend_90d(body_db, 1) is None
