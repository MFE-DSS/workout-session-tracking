"""No trend, physiology, machine-mass inference or prescribed-as-performed data."""

import importlib
import sqlite3
from datetime import UTC, datetime

import pytest
from test_muscle_observed_load_sqlite import capture, seed


def project(path, *, source_transform=None, **kwargs):
    try:
        m = importlib.import_module("app.services.muscle_observed_load.projection")
    except ModuleNotFoundError:
        pytest.fail("BUILD01 projection not implemented")
    from app.services.muscle_observed_load.limits import ReadLimits

    with capture(path, **kwargs) as c:
        sources = m.SourceView.local()
        # Synthetic semantic port only: the actual canonical asset separately fails
        # admission at its 4,302-byte editorial note. No production file changes.
        import json

        original = sources.json

        def semantic_json(path, *args, **kw):
            if path == "data/sci/exercise_catalogue.json":
                raw = sources.read(path)
                value = json.loads(raw)
                value["records"][75]["exercise_operational"]["curation"].pop("notes")
                return value
            return original(path, *args, **kw)

        sources.json = semantic_json
        if source_transform is not None:
            source_transform(sources)
        return m.project_capture(
            c,
            c.query,
            sources,
            ReadLimits(),
            as_of=datetime(2026, 11, 25, tzinfo=UTC),
            runtime_profile_digest="0" * 64,
        ).model_dump()


def test_legacy_fact_is_dated_partial_and_preserves_null_mass(tmp_path):
    d = project(seed(tmp_path / "db"))
    assert d["state"] == "PARTIAL"
    f = d["facts"][0]
    assert f["reps"] == 9 and f["weight_kg"] is None
    assert f["temporal"]["membership"] == "IN_WINDOW"
    assert f["provenance"]["profile"] == "LEGACY"
    z = next(z for z in d["zones"] if z["zone"] == "pecs")
    assert z["window_result"]["documented_sets"] == 1
    assert z["window_result"]["bound"] == "EXACT"  # role/scan exact, origin still partial
    assert z["last_qualified_observation"] is None
    assert z["evidence"]["exact_evidence"]


def test_old_prefix_missing_recent_cannot_claim_empty_or_zero(tmp_path):
    d = project(seed(tmp_path / "db", 201))
    assert d["state"] == "UNKNOWN" and d["scan"]["truncated"]
    assert d["facts"] == []
    assert all(z["window_result"]["documented_sets"] is None for z in d["zones"])


@pytest.mark.parametrize("when", ["2026-11-25 00:00:00", "2026-10-31 23:59:59"])
def test_window_end_exclusive_and_start_applies_to_event_not_session(tmp_path, when):
    p = seed(tmp_path / "db")
    with sqlite3.connect(p) as db:
        db.execute("UPDATE set_logs SET completed_at=? WHERE id=1", (when,))
    d = project(p)
    assert d["state"] == "EMPTY" and d["facts"] == []


@pytest.mark.parametrize("when", [None, "2027-01-01 00:00:00", "invalid"])
def test_unknown_temporal_membership_cannot_make_minimum(tmp_path, when):
    p = seed(tmp_path / "db")
    with sqlite3.connect(p) as db:
        db.execute("UPDATE set_logs SET completed_at=? WHERE id=1", (when,))
    d = project(p)
    assert d["state"] == "UNKNOWN"
    assert all(z["window_result"]["documented_sets"] is None for z in d["zones"])


def test_unknown_executed_substitution_has_no_prescribed_fallback(tmp_path):
    p = seed(tmp_path / "db")
    with sqlite3.connect(p) as db:
        db.execute("UPDATE session_exercises SET substituted_name='not mapped'")
    d = project(p)
    assert d["facts"][0]["resolution"]["status"] == "UNKNOWN_IDENTITY"
    assert d["facts"][0]["contributions"] == []
    assert all(z["window_result"]["documented_sets"] is None for z in d["zones"])


def test_v3_missing_captured_authority_never_uses_legacy_name(tmp_path):
    p = seed(tmp_path / "db")
    with sqlite3.connect(p) as db:
        db.execute(
            "UPDATE workout_sessions SET template_slug_snapshot='science:v3:first-session' WHERE id=1"
        )
    d = project(p)
    assert d["state"] == "UNKNOWN"
    assert d["facts"][0]["provenance"]["profile"] == "V3"
    assert d["facts"][0]["contributions"] == []


def test_posterior_is_union_without_scalar_credit(tmp_path):
    p = seed(tmp_path / "db")
    with sqlite3.connect(p) as db:
        db.execute(
            "UPDATE session_exercises SET exercise_name_snapshot='Romanian deadlift haltères' WHERE id=1"
        )
    d = project(p)
    z = next(z for z in d["bodymap_projection"]["targets"] if z["bodymap_zone"] == "posterior")
    assert z["components"] == ["hamstrings", "glutes"]
    assert z["window_result"]["resolved_credit"] is None
    assert z["window_result"]["documented_sets"] == 1
    assert d["bodymap_projection"]["not_represented"] == [
        "anterior_delts",
        "adductors",
        "hip_flexors",
    ]


def test_zone_without_any_role_has_null_evidence_not_zero_vector(tmp_path):
    d = project(seed(tmp_path / "db"))
    zone = next(z for z in d["zones"] if z["zone"] == "calves")
    assert zone["evidence"] is None


def test_dated_plus_undated_and_unclassifiable_session_cannot_claim_exact(tmp_path):
    p = seed(tmp_path / "db", 3)
    with sqlite3.connect(p) as db:
        db.execute("UPDATE set_logs SET completed_at='2026-11-02 00:00:00' WHERE id=1")
        db.execute("UPDATE set_logs SET completed_at=NULL WHERE id=2")
        db.execute("UPDATE workout_sessions SET status='malformed-status' WHERE id=3")
    d = project(p)
    pecs = next(z for z in d["zones"] if z["zone"] == "pecs")
    assert pecs["window_result"]["bound"] == "MINIMUM"
    assert pecs["window_result"]["documented_sets"] == 1


def test_malformed_status_is_not_an_empty_history(tmp_path):
    p = seed(tmp_path / "db")
    with sqlite3.connect(p) as db:
        db.execute("UPDATE workout_sessions SET status='not-a-status' WHERE id=1")
    assert project(p)["state"] == "UNKNOWN"


def test_outside_rows_have_explicit_observed_exclusion_counts(tmp_path):
    p = seed(tmp_path / "db")
    with sqlite3.connect(p) as db:
        db.execute("UPDATE set_logs SET completed_at='2026-10-02 00:00:00' WHERE id=1")
    d = project(p)
    assert {"reason": "OUTSIDE_WINDOW", "inspected_count": 1} in d["exclusions"]


def test_p07_runtime_artifact_cannot_silently_replace_posterior_components():
    from app.services.muscle_observed_load.projection import SourceView

    view = SourceView.local()
    original = view.json

    def changed(path, *args, **kwargs):
        data = original(path, *args, **kwargs)
        if path == "data/sci/readiness_bodymap_projection.v1.json":
            data["posterior"]["resolved_credit"] = 1.5
        return data

    view.json = changed
    with pytest.raises(ValueError):
        view.credit_policy()


def test_only_unknown_roles_produce_unknown_not_a_certain_partial(tmp_path):
    def unknown(sources):
        original = sources.legacy

        def adapted(capture, candidate):
            resolution, roles = original(capture, candidate)
            for role in roles:
                role["raw_role"] = "UNKNOWN"
            return resolution, roles

        sources.legacy = adapted

    result = project(seed(tmp_path / "db"), source_transform=unknown)
    assert result["state"] == "UNKNOWN"
    assert all(z["window_result"]["documented_sets"] is None for z in result["zones"])


def _independent_wire_digest(data):
    import copy
    import hashlib
    import json

    body = copy.deepcopy(data)
    body["consistency"]["result_digest"] = "0" * 64
    return hashlib.sha256(
        json.dumps(
            body, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(",", ":")
        ).encode()
    ).hexdigest()


@pytest.mark.parametrize("setting", [35, 35.0, 35.5])
def test_final_digest_describes_normalized_v3_setting(tmp_path, setting):
    from test_muscle_observed_load_provenance import v3_case

    path, _, ports, _ = v3_case(
        tmp_path, mutate=lambda p, e, o, r: o["setting"].update(value=setting)
    )

    def use_captured_authority(sources):
        sources.bundle_for = ports.bundle_for
        sources.v3_resolution = ports.v3_resolution

    data = project(path, source_transform=use_captured_authority)
    assert data["facts"][0]["setting"]["value"] == setting
    assert type(data["facts"][0]["setting"]["value"]) is float
    assert data["facts"][0]["weight_kg"] is None
    assert data["consistency"]["result_digest"] == _independent_wire_digest(data)


def test_corrupt_digest_calculation_cannot_return_a_response(tmp_path, monkeypatch):
    from app.services.muscle_observed_load import projection

    monkeypatch.setattr(projection, "digest", lambda _: "f" * 64)
    with pytest.raises(ValueError, match="result_digest_mismatch"):
        project(seed(tmp_path / "db"))
