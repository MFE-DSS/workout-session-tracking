"""Contract boundaries: no coercion, inferred time or unknown-to-zero."""

import importlib
from datetime import UTC, datetime

import pytest


def contracts():
    try:
        return importlib.import_module("app.services.muscle_observed_load.contracts")
    except ModuleNotFoundError:
        pytest.fail("BUILD01 strict contract is not implemented")


def test_request_normalizes_offsets_without_inventing_time():
    c = contracts()
    q = c.parse_query(
        [("from", "2026-11-01T01:00:00+01:00"), ("until", "2026-11-02T00:00:00Z")],
        "muscle-observed-load/1.0.0",
        as_of=datetime(2026, 11, 3, tzinfo=UTC),
    )
    assert q.window_start == datetime(2026, 11, 1, tzinfo=UTC)
    assert q.window_until == datetime(2026, 11, 2, tzinfo=UTC)


@pytest.mark.parametrize(
    "pairs",
    [
        [("from", "2026-11-01"), ("until", "2026-11-02T00:00:00Z")],
        [("from", "2026-11-02T00:00:00Z"), ("until", "2026-11-01T00:00:00Z")],
        [("from", "2026-11-01T00:00:00Z"), ("until", "2027-01-01T00:00:00Z")],
        [("from", "2026-11-01T00:00:00Z"), ("from", "2026-11-01T00:00:00Z")],
        [("owner_id", "2"), ("from", "2026-11-01T00:00:00Z")],
        [
            ("from", "2026-11-01T00:00:00Z"),
            ("until", "2026-11-02T00:00:00Z"),
            ("time_zone", "Europe/Paris"),
        ],
    ],
)
def test_invalid_or_owner_supplied_query_never_reaches_reader(pairs):
    c = contracts()
    with pytest.raises(c.ObservedLoadReadError) as caught:
        c.parse_query(pairs, "muscle-observed-load/1.0.0", as_of=datetime(2026, 11, 3, tzinfo=UTC))
    assert caught.value.status == 422


@pytest.mark.parametrize("header", [None, "muscle-observed-load/2.0.0", ""])
def test_negotiation_is_explicit(header):
    c = contracts()
    with pytest.raises(c.ObservedLoadReadError) as caught:
        c.parse_query([], header, as_of=datetime(2026, 11, 3, tzinfo=UTC))
    assert caught.value.status == 406


def test_error_dto_forbids_private_details_and_mixed_availability():
    c = contracts()
    value = {
        "contract_version": "muscle-observed-load/1.0.0",
        "availability": "UNAVAILABLE",
        "state": "UNAVAILABLE",
        "detail": {"error": "muscle_observed_load_unavailable"},
    }
    assert c.ObservedLoadResponse.model_validate(value).model_dump() == value
    value["detail"]["sql"] = "private"
    with pytest.raises(ValueError):
        c.ObservedLoadResponse.model_validate(value)
    value["detail"].pop("sql")
    value["availability"] = "AVAILABLE"
    with pytest.raises(ValueError):
        c.ObservedLoadResponse.model_validate(value)


def test_immutable_budget_rejects_increases_and_stops_before_excess():
    try:
        m = importlib.import_module("app.services.muscle_observed_load.limits")
    except ModuleNotFoundError:
        pytest.fail("BUILD01 resource budgets not implemented")
    with pytest.raises(ValueError):
        m.ReadLimits(work_sets=501)
    b = m.ReadBudget(m.ReadLimits(work_sets=1))
    b.take("work_sets")
    with pytest.raises(m.BudgetExceeded):
        b.take("work_sets")
    assert b.used["work_sets"] == 1


def empty_wire():
    """Hand-authored empty documented subset, not a product response factory."""
    zones = [
        "pecs",
        "lats",
        "upper_back",
        "anterior_delts",
        "lateral_delts",
        "rear_delts",
        "biceps",
        "triceps",
        "quads",
        "hamstrings",
        "glutes",
        "adductors",
        "calves",
        "abs",
        "hip_flexors",
    ]
    targets = {
        "pecs": ["pecs"],
        "lats": ["lats"],
        "upper_back": ["upper_back"],
        "delt_lat": ["lateral_delts"],
        "delt_post": ["rear_delts"],
        "biceps": ["biceps"],
        "triceps": ["triceps"],
        "quads": ["quads"],
        "posterior": ["hamstrings", "glutes"],
        "calves": ["calves"],
        "core": ["abs"],
    }

    def q():
        return {
            "state": "EMPTY",
            "documented_sets": None,
            "resolved_credit": None,
            "bound": None,
            "reasons": ["NO_DOCUMENTED_FACTS"],
        }

    return {
        "contract_version": "muscle-observed-load/1.0.0",
        "availability": "AVAILABLE",
        "state": "EMPTY",
        "owner_id": 1,
        "read_id": "00000000-0000-4000-8000-000000000001",
        "as_of": "2026-11-25T00:00:00Z",
        "window": {
            "from": "2026-11-01T00:00:00Z",
            "until": "2026-11-25T00:00:00Z",
            "time_zone": "UTC",
        },
        "membership": "LIVE_BOUNDED_MEMBERSHIP",
        "policy_id": "sci-exposure-credit-v1",
        "catalogue_versions": [],
        "mapping_version": "sci-p07-bodymap-projection/0.1.0",
        "coverage": {
            "scan": "COMPLETE",
            "temporal": "COMPLETE",
            "mapping": "COMPLETE",
            "scope": "CURRENT_DOCUMENTED_ELIGIBLE_SUBSET_NOT_REAL_TRAINING_COMPLETENESS",
            "reasons": [],
        },
        "scan": {
            "strategy": "OWNER_ID_ASC_NESTED",
            "truncated": False,
            "reasons": [],
            "limits": {
                "sessions": 200,
                "exercises": 200,
                "work_sets": 500,
                "operations": 1000,
                "graph_rows": 500,
                "statements": 4096,
            },
            "usage": {
                "sessions": 0,
                "exercises": 0,
                "work_sets": 0,
                "operations": 0,
                "graph_rows": 0,
                "statements": 0,
                "sentinels": 0,
                "unvisited_frontiers": 0,
                "db_input_bytes": 0,
            },
        },
        "consistency": {
            "kind": "READ_TRANSACTION",
            "runtime_profile_digest": "0" * 64,
            "result_digest": "1" * 64,
            "source_digests": [],
        },
        "zones": [
            {"zone": z, "evidence": None, "window_result": q(), "last_qualified_observation": None}
            for z in zones
        ],
        "bodymap_projection": {
            "mapping_version": "sci-p07-bodymap-projection/0.1.0",
            "targets": [
                {
                    "bodymap_zone": z,
                    "components": v,
                    "window_result": q(),
                    "last_qualified_observation": None,
                }
                for z, v in targets.items()
            ],
            "not_represented": ["anterior_delts", "adductors", "hip_flexors"],
        },
        "facts": [],
        "exclusions": [],
    }


def test_unknown_and_missing_do_not_become_zero():
    c = contracts()
    wire = empty_wire()
    assert (
        c.ObservedLoadResponse.model_validate(wire).model_dump()["zones"][0]["window_result"][
            "documented_sets"
        ]
        is None
    )
    wire["zones"][0]["window_result"]["documented_sets"] = 0
    with pytest.raises(ValueError):
        c.ObservedLoadResponse.model_validate(wire)


@pytest.mark.parametrize(
    "change",
    [
        lambda d: d.update(owner_id=True),
        lambda d: d["zones"].append(d["zones"][0]),
        lambda d: d["zones"][0].update(zone="new_anatomy"),
        lambda d: d["bodymap_projection"]["targets"][8]["window_result"].update(
            resolved_credit=1.5
        ),
        lambda d: d["scan"].update(truncated=True),
        lambda d: d["coverage"].update(temporal="PARTIAL"),
    ],
)
def test_cross_field_or_strict_type_lie_is_rejected(change):
    c = contracts()
    wire = empty_wire()
    change(wire)
    with pytest.raises(ValueError):
        c.ObservedLoadResponse.model_validate(wire)


def test_compiled_wire_schema_matches_the_admitted_document_exactly():
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    files = list(
        (root / "openspec/changes").rglob("sci-readiness-01-build-01/PROPOSED_RESPONSE.schema.json")
    )
    assert len(files) == 1
    assert contracts()._SCHEMA == json.loads(files[0].read_text())
