"""Sb_SCI_V2_01 — le validateur du catalogue scientifique, et ses défauts plantés.

Un validateur vert ne prouve rien tant qu'on ne l'a pas vu rejeter. Chaque défaut planté doit
échouer **pour sa raison nommée**, pas seulement rendre un code de sortie non nul : une garde qui
rejette pour une autre raison que celle qu'on a plantée laisse passer le défaut le jour où l'autre
raison disparaît.
"""

from __future__ import annotations

import copy
import dataclasses
from pathlib import Path

import pytest

from scripts import validate_sci_catalogue as v

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def inputs() -> v.Inputs:
    return v.load_inputs(ROOT)


@pytest.fixture(scope="module")
def baseline() -> dict:
    return v.load_catalogue_doc(ROOT)


def _rec(doc: dict, rid: str) -> dict:
    return next(r for r in doc["records"] if r["exercise_id"] == rid)


def _set_role(doc: dict, rid: str, zone: str, role: str) -> None:
    contributions = _rec(doc, rid)["exercise_science"]["contributions"]
    for c in contributions:
        if c["zone"] == zone:
            c["role"] = role
            return
    contributions.append({"zone": zone, "role": role, "role_basis": "joint_action_anatomy",
                          "evidence_refs": ["EV-71"]})


def _op(doc: dict, rid: str) -> dict:
    return _rec(doc, rid)["exercise_operational"]


def test_the_versioned_catalogue_has_zero_format_errors(baseline, inputs):
    result = v.validate(baseline, inputs)
    assert result.format_errors == []
    assert result.metrics["source_records"] == "107/107"
    assert result.metrics["publishable"] == 107


def test_metrics_report_the_closure_counts(baseline, inputs):
    m = v.validate(baseline, inputs).metrics
    assert m["canonical_identities"] == 84
    assert m["compiler_candidates"] == 84
    assert m["legacy_aliases"] == 23
    assert m["canonical_by_classification"]["UNRESOLVED"] == 0
    assert m["equipment_requirements_unknown"] == 1
    assert m["machine_unspecified"] == 29
    assert m["true_any_of_requirements"] == 1


# ── défauts plantés : (nom, mutation du catalogue, raison attendue)

PLANTS = [
    ("R11 reverse pec deck tagged pecs",
     lambda d: _set_role(d, "reverse-fly-machine", "pecs", "MINOR"), "LEGACY_ERR_REVERSE_PEC_DECK_PECS"),
    ("R11 hanging leg raise tagged calves",
     lambda d: _set_role(d, "releve-de-jambes-suspendu", "calves", "MINOR"), "LEGACY_ERR_HANGING_LEG_RAISE_CALVES"),
    ("R11 seated adduction on the posterior chain",
     lambda d: _set_role(d, "adduction-assise", "hamstrings", "SECONDARY"),
     "LEGACY_ERR_SEATED_ADDUCTION_POSTERIOR_CHAIN"),
    ("R11 cable pullover back on the machine",
     lambda d: _op(d, "pullover-cable-paren-bras-tendus-poulie-haute").__setitem__(
         "equipment_requirements", ["machine_pullover"]),
     "LEGACY_ERR_CABLE_PULLOVER_MACHINE_DESCRIPTION"),
    ("alias science diverges from its canonical",
     lambda d: _set_role(d, "reverse-fly-machine", "biceps", "MINOR"), "alias science differs"),
    ("alias operational facts diverge",
     lambda d: _op(d, "face-pull-cable").__setitem__("equipment_requirements", ["cable_anchor_high"]),
     "operational facts differ"),
    ("two CANONICAL records in one identity",
     lambda d: _rec(d, "reverse-fly-machine").__setitem__("identity", {
         "scientific_identity_id": "reverse_pec_deck_fly", "identity_relation": "CANONICAL", "alias_of": None,
         "group_classification": "UNIQUE", "canonical_display_name": "Reverse fly"}),
     "CANONICAL records (exactly 1 required)"),
    ("alias pointing to another alias",
     lambda d: _rec(d, "curl-cable-basse")["identity"].__setitem__("alias_of", "curl-poulie-basse"),
     "alias_of must be"),
    ("alias without a merge basis",
     lambda d: _rec(d, "upright-row-cable")["identity"].pop("merge_basis"), "schema: identity"),
    ("UNKNOWN requirement carrying capabilities",
     lambda d: _op(d, "adduction-couchee-machine").__setitem__("equipment_requirements", ["dumbbells"]),
     "schema: exercise_operational"),
    ("UNKNOWN requirement disguised as no-equipment",
     lambda d: _op(d, "adduction-couchee-machine").__setitem__("equipment_requirement_status", "RESOLVED"),
     "RESOLVED [] (no equipment)"),
    ("capability outside TRAIN A",
     lambda d: _op(d, "pompes").__setitem__("equipment_requirements", ["yoga_mat"]),
     "capability not in TRAIN A"),
    ("nested any_of",
     lambda d: _op(d, "pullover-cable-paren-bras-tendus-poulie-haute").__setitem__("equipment_requirements", [
         "cable_anchor_high", {"any_of": [{"any_of": [ROPE, BAR]}, ROPE]}]),
     "schema: exercise_operational/equipment_requirements"),
    ("any_of with a single member",
     lambda d: _op(d, "pullover-cable-paren-bras-tendus-poulie-haute").__setitem__("equipment_requirements", [
         "cable_anchor_high", {"any_of": [ROPE]}]),
     "schema: exercise_operational/equipment_requirements"),
    ("pattern outside the closed vocabulary",
     lambda d: _rec(d, "pompes")["exercise_science"].__setitem__("movement_pattern", "anti_flexion"),
     "schema: exercise_science/movement_pattern"),
    ("zone outside the closed vocabulary",
     lambda d: _set_role(d, "pompes", "posterior_chain", "MINOR"), "schema: exercise_science/contributions"),
    ("role outside the closed vocabulary",
     lambda d: _rec(d, "pompes")["exercise_science"]["contributions"][0].__setitem__("role", "HALF"),
     "schema: exercise_science/contributions"),
    ("bare 'machine' equipment mode",
     lambda d: _op(d, "adduction-assise").__setitem__("equipment_mode", "machine"),
     "schema: exercise_operational/equipment_mode"),
    ("EMG model presented as a longitudinal trial",
     lambda d: _rec(d, "pompes")["exercise_science"]["contributions"][0].update(
         {"role_basis": "longitudinal_trial", "evidence_refs": ["EV-73"]}),
     "longitudinal_trial without a longitudinal hypertrophy trial"),
    ("evidence reference absent from E0",
     lambda d: _rec(d, "pompes")["exercise_science"]["contributions"][0].__setitem__("evidence_refs", ["EV-999"]),
     "evidence_ref not in E0"),
    ("reviewed record without a resolved PRIMARY",
     lambda d: [c.__setitem__("role", "SECONDARY") for c in _rec(d, "pompes")["exercise_science"]["contributions"]
                if c["role"] == "PRIMARY"],
     "schema:"),
    ("content alignment with an invented status",
     lambda d: _rec(d, "rowing-machine-chest-supported")["content_alignment"].__setitem__("status", "ALIGNED"),
     "schema: content_alignment"),
    ("unknown top-level property",
     lambda d: _rec(d, "pompes").__setitem__("activation_percent", 87), "schema: <root>"),
    ("a source record goes missing",
     lambda d: d["records"].pop(0), "missing records"),
    ("records out of order",
     lambda d: d["records"].reverse(), "not sorted"),
    ("header names another credit policy",
     lambda d: d["catalogue_header"].__setitem__("credit_policy_version", "credit_policy_v2"),
     "credit_policy_version"),
]
ROPE, BAR = "cable_attachment_rope", "cable_attachment_straight_bar"


@pytest.mark.parametrize("name,plant,reason", PLANTS, ids=[p[0] for p in PLANTS])
def test_each_planted_defect_is_rejected_for_its_named_reason(baseline, inputs, name, plant, reason):
    doc = copy.deepcopy(baseline)
    plant(doc)
    errors = v.validate(doc, inputs).format_errors
    assert errors, f"{name}: accepted"
    assert any(reason in e for e in errors), f"{name}: rejected for another reason: {errors[:3]}"


DELTA_PLANTS = [
    ("inferred accessory on the dual pulley",
     lambda dl: dl["item_capability_additions"].append(
         {"item_id": "dual_adjustable_pulley", "add_capabilities": ["cable_attachment_single_handle"]}),
     "inferred accessory"),
    ("inferred accessory on the low row station",
     lambda dl: dl["item_capability_additions"].append(
         {"item_id": "low_row_station", "add_capabilities": ["cable_attachment_close_neutral_row_handle"]}),
     "inferred accessory"),
    ("neutral grip granted by no physical object",
     lambda dl: dl.__setitem__("new_items", [i for i in dl["new_items"] if i["item_id"] != "cable_neutral_grip_handle"]),
     "granted by no physical object"),
]


@pytest.mark.parametrize("name,plant,reason", DELTA_PLANTS, ids=[p[0] for p in DELTA_PLANTS])
def test_each_planted_registry_delta_defect_is_rejected(baseline, inputs, name, plant, reason):
    delta = copy.deepcopy(inputs.delta)
    plant(delta)
    errors = v.validate(baseline, dataclasses.replace(inputs, delta=delta)).format_errors
    assert any(reason in e for e in errors), f"{name}: {errors[:3]}"


def test_an_unresolved_identity_is_counted_never_hidden(baseline, inputs):
    doc = copy.deepcopy(baseline)
    _rec(doc, "hip-thrust-halteres")["identity"]["group_classification"] = "UNRESOLVED"
    assert v.validate(doc, inputs).metrics["canonical_by_classification"]["UNRESOLVED"] == 1


# ── le moteur de schéma interne : ce qu'il ne sait pas faire, il le refuse


def test_every_keyword_of_the_versioned_schema_is_supported(inputs):
    assert v.unsupported_keywords(inputs.schema) == set()


def test_an_unsupported_keyword_fails_instead_of_being_ignored():
    schema = {"type": "object", "patternProperties": {"^x": {"type": "string"}}}
    assert v.unsupported_keywords(schema) == {"patternProperties"}
    with pytest.raises(v.UnsupportedSchemaKeyword):
        v.schema_errors({"x1": 3}, schema)


@pytest.mark.parametrize("instance,schema,valid", [
    (3, {"type": "integer"}, True),
    (True, {"type": "integer"}, False),
    (3.0, {"type": "integer"}, True),
    ("a", {"enum": ["a", "b"]}, True),
    ("c", {"enum": ["a", "b"]}, False),
    ([1, 1], {"type": "array", "uniqueItems": True}, False),
    ({"a": 1}, {"type": "object", "additionalProperties": False, "properties": {"b": {}}}, False),
    ("ab", {"type": "string", "pattern": "^a"}, True),
    (1, {"oneOf": [{"type": "integer"}, {"minimum": 0}]}, False),
    (5, {"if": {"minimum": 3}, "then": {"maximum": 4}}, False),
    (2, {"if": {"minimum": 3}, "then": {"maximum": 4}, "else": {"const": 2}}, True),
    ([1, "x"], {"type": "array", "contains": {"type": "string"}}, True),
    (4, {"not": {"type": "integer"}}, False),
])
def test_schema_engine_semantics_on_small_cases(instance, schema, valid):
    assert (not v.schema_errors(instance, schema)) is valid


def test_schema_engine_agrees_with_jsonschema_when_available(baseline, inputs):
    """Concordance avec l'implémentation de référence. Sautée là où `jsonschema` n'est pas
    installé (la CI installe le lock, qui ne la contient pas) ; exécutée sur le poste."""
    jsonschema = pytest.importorskip("jsonschema")
    reference = jsonschema.Draft202012Validator(inputs.schema)
    docs = [baseline]
    for _, plant, _ in PLANTS:
        doc = copy.deepcopy(baseline)
        plant(doc)
        docs.append(doc)
    for doc in docs:
        for record in doc["records"]:
            ours = bool(v.schema_errors(record, inputs.schema))
            theirs = any(True for _ in reference.iter_errors(record))
            assert ours == theirs, record.get("exercise_id")
