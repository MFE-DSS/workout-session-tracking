"""Authority failures cannot silently become static catalogue classifications."""

import importlib
from pathlib import Path

import pytest


def module():
    try:
        return importlib.import_module("app.services.muscle_observed_load.provenance")
    except ModuleNotFoundError:
        pytest.fail("BUILD01 provenance not implemented")


def test_data_only_effective_composition_matches_attested_reference():
    m = module()
    from tools.science_initial_policy.v2_registry import load_v2_registry, thaw

    root = Path(__file__).resolve().parents[1]
    view = m.SourceView.local()
    actual = m.compose_effective(view)
    expected = load_v2_registry(root)
    assert actual["candidates"] == thaw(expected.candidates)
    assert actual["effective_science_digest"] == expected.effective_science_digest
    assert actual["bundle_digest"] == expected.bundle_digest
    assert (
        actual["candidates"]["tirage-poulie-haute-prise-neutre"]["effective_roles"]
        != actual["candidates"]["tirage-poulie-haute-prise-neutre"]["source_roles"]
    )


def test_bundle_rejects_path_escape_symlink_and_unattested_bytes(tmp_path):
    m = module()
    import hashlib
    import json

    for path in ["../outside", "/absolute", "missing.py"]:
        raw = json.dumps(
            {"contract_version": "plan-v3-private-science-bundle/1.0.0", "sha256": {path: "0" * 64}}
        ).encode()
        (tmp_path / "packaging-manifest.v1.json").write_bytes(raw)
        with pytest.raises((ValueError, OSError)):
            m.SourceView.bundle(tmp_path, hashlib.sha256(raw).hexdigest())


def test_actual_canonical_asset_fails_approved_string_ceiling_without_budget_increase():
    m = module()
    with pytest.raises(ValueError, match="json_string_limit"):
        m.SourceView.local().json("data/sci/exercise_catalogue.json")


def v3_case(tmp_path, *, mutate=None):
    import json
    import sqlite3
    from datetime import UTC, datetime
    from types import SimpleNamespace

    from test_muscle_observed_load_sqlite import capture, seed

    m = module()
    path = seed(tmp_path / "db")
    context = dict(
        context_ref="ctx",
        equipment_ref="machine",
        realization_ref="real",
        side="BILATERAL",
        load_semantics="MACHINE_DISPLAY_KG",
    )
    slot = dict(
        slot_id="slot",
        intent_id="intent",
        selected={"canonical_exercise_id": "identity"},
        prescription={"context": context, "dose": {"work_sets": 1}},
    )
    authority = {k: "value" for k in m.V3_AUTHORITY_FIELDS}
    authority.update(
        binding_digest="b" * 64, bundle_digest="c" * 64, effective_science_digest="d" * 64
    )
    payload = dict(
        authority=authority,
        authority_generation=1,
        allocation_ref="allocation",
        scientific_session={"slots": [slot]},
        mapping=[
            dict(
                se_id=1,
                canonical_exercise_id="identity",
                slot_id="slot",
                intent_id="intent",
                set_ids=[1],
            )
        ],
    )
    evaluated = dict(
        authority,
        candidate_plan=dict(sessions=[payload["scientific_session"]], allocation_ref="allocation"),
    )
    observation = dict(
        context=context,
        setting=dict(kind="MASS_KG", value=35, unit="kg"),
        reps=9,
        completed=True,
        performed_at="2026-11-02T00:00:00Z",
        performed_at_estimated=True,
    )
    receipt = dict(
        state="APPLIED",
        session_id=1,
        set_id=1,
        op_id="op",
        applied_revision=1,
        performed_at="2026-11-02T00:00:00Z",
        performed_at_adjusted=False,
    )
    if mutate:
        mutate(payload, evaluated, observation, receipt)
    with sqlite3.connect(path) as db:
        db.executescript(
            "CREATE TABLE first_plan_execution_bindings(session_id INTEGER PRIMARY KEY,owner_id INTEGER,execution_profile_version TEXT,scientific_session_id TEXT,evaluation_id TEXT,binding_digest TEXT,immutable_payload_json TEXT); CREATE TABLE first_plan_evaluations(id TEXT PRIMARY KEY,owner_id INTEGER,authority_generation INTEGER,result_json TEXT); CREATE TABLE first_plan_runtime_authorities(profile_key TEXT PRIMARY KEY,generation INTEGER,state TEXT,publication_json TEXT,packaging_digest TEXT,approval_ref TEXT);"
        )
        db.execute(
            "UPDATE workout_sessions SET template_slug_snapshot='science:v3:first-session' WHERE id=1"
        )
        db.execute(
            "INSERT INTO first_plan_execution_bindings VALUES(1,1,?,?,?,?,?)",
            (
                "first-plan-execution/3.0.0",
                "science-session",
                "eval",
                m.digest(payload),
                json.dumps(payload),
            ),
        )
        db.execute(
            "INSERT INTO first_plan_evaluations VALUES(?,1,1,?)", ("eval", json.dumps(evaluated))
        )
        publication = {
            k: authority[k] for k in ("binding_digest", "bundle_digest", "effective_science_digest")
        }
        publication["registry_digest"] = "r" * 64
        db.execute(
            "INSERT INTO first_plan_runtime_authorities VALUES(?,1,?,?,?,?)",
            (
                "first-session-runtime/3.0.0",
                "ACTIVE",
                json.dumps(publication),
                "p" * 64,
                "approval",
            ),
        )
        db.execute(
            "UPDATE first_plan_set_observations SET body_digest=?,observation_json=?,receipt_json=?",
            (
                m.digest(
                    dict(session_id=1, set_id=1, expected_revision=0, observation=observation)
                ),
                json.dumps(observation),
                json.dumps(receipt),
            ),
        )
    effective = dict(
        authority,
        registry_digest="r" * 64,
        candidates={"identity": dict(intent_id="intent", realization_ref="real")},
    )

    class Sources:
        def bundle_for(self, _):
            return SimpleNamespace(v3=effective)

        def v3_resolution(self, *_):
            return dict(
                status="RESOLVED",
                query="identity",
                step=1,
                variant_key="identity",
                scientific_identity_id="science-id",
                canonical_exercise_id="identity",
                catalogue_version="synthetic-effective",
                reason=None,
            ), [
                dict(
                    zone="pecs",
                    raw_role="PRIMARY",
                    role_basis="synthetic canonical role port",
                    evidence_refs=["synthetic"],
                    execution_uncertain=False,
                )
            ]

    return path, capture, Sources(), datetime(2026, 11, 25, tzinfo=UTC)


def test_complete_chain_keeps_machine_setting_separate_from_total_mass(tmp_path):
    path, capture, sources, now = v3_case(tmp_path)
    with capture(path) as c:
        f = module().qualify_fact(c, list(c.candidates())[0], sources, as_of=now).fact
    assert f["provenance"]["source_status"] == "QUALIFIED"
    assert f["setting"] == {"kind": "MASS_KG", "value": 35, "unit": "kg"} and f["weight_kg"] is None
    assert f["temporal"]["performed_at_estimated"] is True
    assert f["temporal"]["status"] == "CANONICAL_DATE_PARTIAL_ORIGIN"
    assert f["provenance"]["origin_operation"]["applied_revision"] == 1


@pytest.mark.parametrize(
    "change",
    [
        lambda p, e, o, r: e.update(request_fingerprint="different"),
        lambda p, e, o, r: p["mapping"][0].update(canonical_exercise_id="E1"),
        lambda p, e, o, r: o.update(reps=10),
        lambda p, e, o, r: r.update(set_id=2),
        lambda p, e, o, r: o["context"].update(load_semantics="INVENTED"),
        lambda p, e, o, r: o["context"].update(side="UNKNOWN"),
        lambda p, e, o, r: r.update(performed_at=None),
    ],
)
def test_incomplete_or_contradictory_authority_is_unknown(tmp_path, change):
    path, capture, sources, now = v3_case(tmp_path, mutate=change)
    with capture(path) as c:
        f = module().qualify_fact(c, list(c.candidates())[0], sources, as_of=now).fact
    assert f["provenance"]["source_status"] == "UNKNOWN"
    assert f["contributions"] == []


def test_decomplete_recomplete_does_not_certify_reused_timestamp(tmp_path):
    import json
    import sqlite3

    path, capture, sources, now = v3_case(tmp_path)
    with sqlite3.connect(path) as db:
        original = db.execute(
            "SELECT observation_json,receipt_json FROM first_plan_set_observations"
        ).fetchone()
        for revision, completed in [(2, False), (3, True)]:
            observation = json.loads(original[0])
            observation["completed"] = completed
            observation["performed_at_estimated"] = False  # newer flag cannot launder origin
            receipt = json.loads(original[1])
            receipt.update(applied_revision=revision, op_id="op" + str(revision))
            db.execute(
                "INSERT INTO first_plan_set_observations VALUES (?,1,1,1,1,?,?,?,?,?,?,?)",
                (
                    "row" + str(revision),
                    revision,
                    revision - 1,
                    receipt["op_id"],
                    module().digest(
                        dict(
                            session_id=1,
                            set_id=1,
                            expected_revision=revision - 1,
                            observation=observation,
                        )
                    ),
                    json.dumps(observation),
                    json.dumps(receipt),
                    "2026-11-03 00:00:00",
                ),
            )
    with capture(path) as c:
        f = module().qualify_fact(c, list(c.candidates())[0], sources, as_of=now).fact
    assert f["temporal"]["membership"] == "UNKNOWN"
    assert f["temporal"]["status"] == "CONTRADICTORY_EPISODE"


@pytest.mark.parametrize("marker", ["science:v4:first-session", None, "ordinary-marker"])
def test_positive_v3_binding_prevents_legacy_fallback(tmp_path, marker):
    import sqlite3

    path, capture, sources, now = v3_case(tmp_path)
    with sqlite3.connect(path) as db:
        db.execute("UPDATE workout_sessions SET template_slug_snapshot=? WHERE id=1", (marker,))
    with capture(path) as c:
        f = module().qualify_fact(c, list(c.candidates())[0], sources, as_of=now).fact
    assert f["provenance"]["profile"] == "UNKNOWN" and not f["contributions"]


def test_outside_current_row_does_not_skip_in_window_receipt_contradiction(tmp_path):
    import sqlite3

    path, capture, sources, now = v3_case(tmp_path)
    with sqlite3.connect(path) as db:
        db.execute("UPDATE set_logs SET completed_at='2026-10-02 00:00:00' WHERE id=1")
    with capture(path) as c:
        qualified = module().qualify_fact(c, list(c.candidates())[0], sources, as_of=now)
    assert not qualified.outside
    assert qualified.fact["temporal"]["membership"] == "UNKNOWN"


def test_wrong_body_digest_cannot_be_certified_as_exact_provenance(tmp_path):
    import sqlite3

    path, capture, sources, now = v3_case(tmp_path)
    with sqlite3.connect(path) as db:
        db.execute("UPDATE first_plan_set_observations SET body_digest=?", ("f" * 64,))
    with capture(path) as c:
        f = module().qualify_fact(c, list(c.candidates())[0], sources, as_of=now).fact
    assert f["provenance"]["source_status"] == "UNKNOWN"
    assert "SOURCE_DIGEST_MISMATCH" in f["provenance"]["reasons"]


def test_total_external_recorded_mass_is_preserved_and_conflict_is_unknown(tmp_path):
    import sqlite3

    def total(p, e, o, r):
        o["context"]["load_semantics"] = "TOTAL_EXTERNAL"

    path, capture, sources, now = v3_case(tmp_path, mutate=total)
    with sqlite3.connect(path) as db:
        db.execute("UPDATE set_logs SET weight_kg=35 WHERE id=1")
    with capture(path) as c:
        f = module().qualify_fact(c, list(c.candidates())[0], sources, as_of=now).fact
    assert f["weight_kg"] == 35 and f["provenance"]["source_status"] == "QUALIFIED"
    with sqlite3.connect(path) as db:
        db.execute("UPDATE set_logs SET weight_kg=36 WHERE id=1")
    with capture(path) as c:
        f = module().qualify_fact(c, list(c.candidates())[0], sources, as_of=now).fact
    assert f["provenance"]["source_status"] == "UNKNOWN"


def test_local_and_historical_sources_share_resource_budget(tmp_path):
    m = module()
    from app.services.muscle_observed_load.limits import ReadLimits

    (tmp_path / "a").write_bytes(b"a")
    (tmp_path / "b").write_bytes(b"b")
    one = m.SourceView(tmp_path, ReadLimits(source_files=1))
    one.read("a")
    two = m.SourceView(tmp_path, ReadLimits(source_files=1), budget=one.budget)
    with pytest.raises(ValueError, match="source_file_limit"):
        two.read("b")


def test_inventory2_extension_digest_matches_trusted_reference_and_rejects_wrong_parent():
    from pathlib import Path

    from tools.science_calibration_extension.policy import load_authority

    reference = load_authority(Path(__file__).resolve().parents[1])
    m = module()
    view = m.SourceView.local()
    view.v3 = {"bundle_digest": reference.historical.bundle_digest}
    # Only this adapter's immutable source set; full bounded bundle admission remains separate.
    for path, expected in reference.source_digests.items():
        view.read(path, expected)
    manifest = {"calibration_extension_bundle_digest": reference.bundle_digest}
    m.verify_extension(view, manifest)
    view.v3 = {"bundle_digest": "0" * 64}
    with pytest.raises(ValueError, match="extension_authority_mismatch"):
        m.verify_extension(view, manifest)


def test_real_catalogue_and_inventory2_preserve_v3_authority_under_shared_budget(tmp_path):
    from app.services.muscle_observed_load import supervisor
    from app.services.muscle_observed_load.projection import SourceView
    from tools.plan_calibration_runtime_bundle import build_bundle
    from tools.science_initial_policy.v3_admission import load_v3_registry

    root = Path(__file__).resolve().parents[1]
    bundle = tmp_path / "bundle"
    packaging = build_bundle(bundle, root)
    local = SourceView.local(root)
    for name in supervisor._REQUIRED:
        local.read(name)
    local.catalogue_view()
    local.bundle_root = bundle
    captured = local.bundle_for({"packaging_digest": packaging})
    reference = load_v3_registry(root)
    assert captured.v3["binding_digest"] == reference.binding_digest
    assert captured.v3["bundle_digest"] == reference.bundle_digest
    identity = "tirage-poulie-haute-prise-neutre"
    resolution, roles = local.v3_resolution({"canonical_exercise_id": identity}, captured.v3)
    assert resolution["canonical_exercise_id"] == identity
    assert [row["raw_role"] for row in roles] == [
        row["role"] for row in reference.historical.candidates[identity]["effective_roles"]
    ]
    assert local.budget.files <= 128 and local.budget.total <= 16777216
    assert captured.budget is local.budget
    # Attested source replacement cannot inherit the previously verified hash.
    (bundle / "data/sci/exercise_catalogue.json").write_bytes(b'{"changed":true}')
    with pytest.raises(ValueError, match="source_digest_mismatch"):
        module().SourceView.bundle(bundle, packaging)
