"""Owned read contracts, independently of unpublished HTTP/UI adapters."""

from datetime import UTC, date, datetime

import pytest
from sqlalchemy import event, select
from test_body_measurement_commands import correction, create

pytest_plugins = ["test_body_measurement_commands"]


def capture(db, request_id, measured_on, values=None):
    from app.services.body_measurement_commands import apply_command

    return apply_command(
        db,
        1,
        {
            "operation": "CREATE",
            "request_id": request_id,
            "measured_on": measured_on,
            "values": {"weight_kg": 71.25} if values is None else values,
        },
        source="MANUAL_ENTRY",
    )


def test_versions_preserve_field_sources_and_do_not_make_two_current_observations(body_db):
    from app.services.body_measurement_reads import owned_document, page

    original = create(body_db)
    corrected = correction(body_db, original["root_ref"], {"waist_cm": 85})
    current = owned_document(body_db, 1, original["root_ref"])
    assert current["measurement_id"] == corrected["measurement_id"]
    assert current["date_precision"] == "DAY_UTC_CONVENTION"
    assert current["timezone_basis"] == "DATABASE_UTC_CONVENTION"
    fields = current["fields"]
    assert fields["weight_kg"]["unit"] == "kg"
    assert fields["waist_cm"]["unit"] == "cm"
    assert fields["weight_kg"]["provenance"]["source_ref"] == (
        f"body_measurements/{original['measurement_id']}/weight_kg"
    )
    assert fields["waist_cm"]["provenance"]["acquisition"] == "MANUAL_CORRECTION"
    assert fields["arm_cm_right"]["quality"] == "MISSING"
    versions = page(body_db, 1, kind="VERSIONS", root_ref=original["root_ref"])["entries"]
    assert [entry["state"] for entry in versions] == ["CURRENT", "SUPERSEDED"]
    assert versions[0]["head_token"]
    assert versions[1]["head_token"] is None
    assert versions[1]["fields"]["waist_cm"]["value"] == 90
    assert len(page(body_db, 1, kind="CURRENT")["entries"]) == 1
    assert len(page(body_db, 1, kind="EXPORT")["entries"]) == 2


@pytest.mark.parametrize(
    ("value", "quality", "serialized"),
    [
        (800.0, "LEGACY_OUTSIDE_CURRENT_BOUNDS", 800.0),
        (float("inf"), "INVALID_NONFINITE", None),
        (float("-inf"), "INVALID_NONFINITE", None),
    ],
)
def test_legacy_quality_is_explicit_and_never_requalified(body_db, value, quality, serialized):
    from app.models.measurement import BodyMeasurement
    from app.services.body_measurement_reads import owned_document

    row = BodyMeasurement(user_id=1, measured_at=datetime(2020, 1, 1, tzinfo=UTC), weight_kg=value)
    body_db.add(row)
    body_db.commit()
    doc = owned_document(body_db, 1, row.id)
    field = doc["fields"]["weight_kg"]
    assert field["quality"] == quality
    assert field["value"] == serialized
    assert field["provenance"]["origin"] == "UNKNOWN"
    assert doc["date_precision"] == "UNKNOWN"
    if serialized is None:
        assert field["raw_value_repr"] == str(value)


def test_weight_pages_do_not_resurrect_a_cleared_ancestor_or_expose_another_owner(body_db):
    from app.models.measurement import BodyMeasurement
    from app.services.body_measurement_reads import page

    first = create(body_db)
    correction(body_db, first["root_ref"], {"weight_kg": None})
    body_db.add(BodyMeasurement(user_id=2, weight_kg=62, measured_at=datetime(2020, 1, 1)))
    body_db.commit()
    result = page(body_db, 1, kind="WEIGHT")
    assert result["state"] == "EMPTY"
    assert result["entries"] == []
    assert result["next_cursor"] is None
    assert page(body_db, 2, kind="WEIGHT")["entries"][0]["fields"]["weight_kg"]["value"] == 62


def test_day_window_and_tied_dates_paginate_without_duplicating_or_skipping(body_db):
    from app.services.body_measurement_reads import page

    capture(body_db, "older", "2025-01-01")
    first = capture(body_db, "same-day-1", "2025-01-02")
    second = capture(body_db, "same-day-2", "2025-01-02")
    capture(body_db, "newer", "2025-01-03")
    args = {
        "kind": "CURRENT",
        "limit": 1,
        "from_day": date(2025, 1, 2),
        "through_day": date(2025, 1, 2),
    }
    start = page(body_db, 1, **args)
    end = page(body_db, 1, **args, cursor=start["next_cursor"])
    assert [entry["measurement_id"] for part in [start, end] for entry in part["entries"]] == [
        second["measurement_id"],
        first["measurement_id"],
    ]
    assert end["next_cursor"] is None
    assert end["window"] == {"from": "2025-01-02", "through": "2025-01-02"}


@pytest.mark.parametrize("change", ["owner", "kind", "window", "revision"])
def test_cursor_is_bound_to_owner_query_and_current_revision(body_db, change):
    from app.services.body_measurement_reads import BodyCommandError, page

    capture(body_db, "page-1", "2025-01-01")
    capture(body_db, "page-2", "2025-01-02")
    cursor = page(body_db, 1, kind="CURRENT", limit=1)["next_cursor"]
    owner, args = 1, {"kind": "CURRENT", "limit": 1}
    if change == "owner":
        owner = 2
    elif change == "kind":
        args["kind"] = "WEIGHT"
    elif change == "window":
        args["from_day"] = date(2025, 1, 1)
    else:
        capture(body_db, "new-after-page", "2025-01-03")
    with pytest.raises(BodyCommandError) as error:
        page(body_db, owner, cursor=cursor, **args)
    assert error.value.code == "body_cursor_conflict"
    assert error.value.status == 409


@pytest.mark.parametrize("cursor", ["tampered", "a.b", "a.é", "x" * 4097, 7])
def test_untrusted_cursor_is_rejected_without_returning_facts(body_db, cursor):
    from app.services.body_measurement_reads import BodyCommandError, page

    create(body_db)
    with pytest.raises(BodyCommandError) as error:
        page(body_db, 1, kind="CURRENT", cursor=cursor)
    assert error.value.code == "invalid_body_cursor"
    assert error.value.status == 422


@pytest.mark.parametrize("limit", [True, 0, 101, 1.5])
def test_page_limit_is_a_bounded_integer(body_db, limit):
    from app.services.body_measurement_reads import BodyCommandError, page

    with pytest.raises(BodyCommandError) as error:
        page(body_db, 1, kind="CURRENT", limit=limit)
    assert error.value.code == "invalid_body_limit"
    assert error.value.status == 422


def test_erasure_removes_numbers_from_export_but_not_other_roots(body_db):
    from app.services.body_measurement_commands import apply_command
    from app.services.body_measurement_reads import BodyCommandError, owned_head, page

    first = create(body_db)
    correction(body_db, first["root_ref"], {"waist_cm": 85})
    survivor = capture(body_db, "surviving-root", "2025-01-03")
    apply_command(
        body_db,
        1,
        {
            "operation": "ERASE",
            "request_id": "erase-read-witness",
            "root_ref": first["root_ref"],
            "confirm_all_versions": True,
            "expected_head_token": owned_head(body_db, 1, first["root_ref"])[1],
        },
        source="MANUAL_ERASURE",
    )
    assert [entry["measurement_id"] for entry in page(body_db, 1, kind="EXPORT")["entries"]] == [
        survivor["measurement_id"]
    ]
    with pytest.raises(BodyCommandError) as error:
        page(body_db, 1, kind="VERSIONS", root_ref=first["root_ref"])
    assert error.value.status == 404


def test_ssr_context_counts_real_versions_without_per_row_queries(body_db):
    from app.models.measurement import BodyMeasurement
    from app.services.body_measurement_reads import current_measurement_predicate, head_contexts

    first = create(body_db)
    correction(body_db, first["root_ref"], {"waist_cm": 85})
    for index in range(7):
        capture(body_db, f"context-{index}", "2025-01-03")
    rows = list(body_db.scalars(select(BodyMeasurement).where(current_measurement_predicate())))
    queries = []

    def record(_connection, _cursor, statement, _parameters, _context, _many):
        queries.append(statement)

    event.listen(body_db.bind, "before_cursor_execute", record)
    try:
        contexts = head_contexts(body_db, 1, rows)
    finally:
        event.remove(body_db.bind, "before_cursor_execute", record)
    assert len(queries) <= 2
    assert len(contexts) == 8
    assert sorted(item["version_count"] for item in contexts.values()) == [1] * 7 + [2]


def test_erasure_projection_lists_current_owned_roots_without_observation_fields(body_db):
    from app.models.measurement import BodyMeasurement
    from app.services.body_measurement_reads import owned_erasure_document, owned_head, page

    original = create(body_db)
    correction(body_db, original["root_ref"], {"waist_cm": 85})
    legacy = BodyMeasurement(user_id=1, measured_at=datetime(2000, 1, 1), weight_kg=800)
    body_db.add(legacy)
    body_db.commit()
    result = page(body_db, 1, kind="ERASURE")
    assert result["projection"] == "ERASURE_ONLY"
    assert "field_specs" not in result
    assert result["window"] == {"from": None, "through": None}
    assert len(result["entries"]) == 2
    projected = {row["root_ref"]: row for row in result["entries"]}
    assert projected[original["root_ref"]]["version_count"] == 2
    assert projected[legacy.id]["version_count"] == 1
    assert projected[legacy.id]["date_precision"] == "UNKNOWN"
    assert set(projected[legacy.id]) == {
        "root_ref", "measurement_id", "revision", "head_token", "measured_at",
        "date_precision", "version_count",
    }
    head = owned_erasure_document(body_db, 1, original["root_ref"])
    assert head == projected[original["root_ref"]]
    assert head["head_token"] == owned_head(body_db, 1, original["root_ref"])[1]
    assert page(body_db, 2, kind="ERASURE")["entries"] == []


def test_erasure_cursor_does_not_become_a_fact_cursor_or_survive_an_owner_mutation(body_db):
    from app.services.body_measurement_reads import BodyCommandError, page

    capture(body_db, "erasure-cursor-1", "2025-01-01")
    capture(body_db, "erasure-cursor-2", "2025-01-01")
    first = page(body_db, 1, kind="ERASURE", limit=1)
    second = page(body_db, 1, kind="ERASURE", limit=1, cursor=first["next_cursor"])
    assert first["entries"][0]["root_ref"] != second["entries"][0]["root_ref"]
    assert second["next_cursor"] is None
    with pytest.raises(BodyCommandError, match="body_cursor_conflict"):
        page(body_db, 1, kind="CURRENT", limit=1, cursor=first["next_cursor"])
    capture(body_db, "erasure-cursor-3", "2025-01-02")
    with pytest.raises(BodyCommandError, match="body_cursor_conflict"):
        page(body_db, 1, kind="ERASURE", limit=1, cursor=first["next_cursor"])
