"""Sb_SCI_V2_01 — chargeur du catalogue scientifique et politique de crédit.

Le chargeur ne sert rien au produit dans cette tranche : il rend la donnée versionnée lisible,
déterministe et immuable. Ces tests fixent ce contrat avant tout consommateur.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import pytest

from app.services import sci_catalogue as sc

ROOT = Path(__file__).resolve().parents[1]
ROLES = {"PRIMARY", "SECONDARY", "MINOR", "UNKNOWN"}


@pytest.fixture(scope="module")
def catalogue() -> sc.SciCatalogue:
    return sc.load_catalogue()


def test_loads_the_107_source_records_in_exercise_id_order(catalogue):
    ids = [r["exercise_id"] for r in catalogue.records]
    assert len(ids) == 107
    assert ids == sorted(ids)
    assert len(set(ids)) == 107


def test_two_fresh_loads_have_identical_digest_and_order():
    first, second = sc.load_catalogue(), sc.load_catalogue()
    assert first.digest == second.digest
    assert [r["exercise_id"] for r in first.records] == [r["exercise_id"] for r in second.records]


def test_digest_is_the_sha256_of_the_versioned_file(catalogue):
    raw = (ROOT / "data" / "sci" / "exercise_catalogue.json").read_bytes()
    assert catalogue.digest == hashlib.sha256(raw).hexdigest()


def test_compiler_candidates_are_the_canonical_records_only(catalogue):
    candidates = catalogue.compiler_candidates()
    assert len(candidates) == 84
    assert {c["identity"]["identity_relation"] for c in candidates} == {"CANONICAL"}
    assert len({c["identity"]["scientific_identity_id"] for c in candidates}) == 84


def test_no_alias_is_ever_a_candidate(catalogue):
    candidate_ids = {c["exercise_id"] for c in catalogue.compiler_candidates()}
    aliases = [r["exercise_id"] for r in catalogue.records
               if r["identity"]["identity_relation"] == "LEGACY_ALIAS"]
    assert len(aliases) == 23
    assert candidate_ids.isdisjoint(aliases)


def test_an_alias_resolves_to_its_canonical_record(catalogue):
    canonical = catalogue.canonical_of("pushdown-corde")
    assert canonical["exercise_id"] == "triceps-pushdown-corde"
    assert catalogue.canonical_of("triceps-pushdown-corde") is canonical


def test_an_unknown_exercise_id_is_an_explicit_error(catalogue):
    with pytest.raises(KeyError):
        catalogue.record("no-such-exercise")


def test_raw_roles_stay_available_and_closed(catalogue):
    roles = catalogue.raw_roles("roulette-abdominale")
    assert roles["abs"] == "PRIMARY"
    assert roles["triceps"] == "UNKNOWN"
    every = {role for r in catalogue.records for role in catalogue.raw_roles(r["exercise_id"]).values()}
    assert every == ROLES


def test_loaded_records_are_read_only(catalogue):
    record = catalogue.record("pompes")
    with pytest.raises(TypeError):
        record["exercise_id"] = "x"  # type: ignore[index]
    with pytest.raises((TypeError, AttributeError)):
        record["exercise_science"]["contributions"].append({})  # type: ignore[union-attr]


def test_machine_unspecified_is_kept_as_written(catalogue):
    modes = [r["exercise_operational"]["equipment_mode"] for r in catalogue.records]
    assert modes.count("machine_unspecified") == 29


def test_an_unknown_requirement_is_not_an_empty_resolved_one(catalogue):
    op = catalogue.record("adduction-couchee-machine")["exercise_operational"]
    assert op["equipment_requirement_status"] == "UNKNOWN"
    assert sc.requirement_is_known(catalogue.record("adduction-couchee-machine")) is False
    assert sc.requirement_is_known(catalogue.record("pompes")) is True


# ── politique de crédit, versionnée à part des rôles bruts


def test_credit_policy_is_a_separate_versioned_file(catalogue):
    policy = sc.load_credit_policy()
    assert policy.policy_id == "sci-exposure-credit-v1"
    assert catalogue.header["credit_policy_version"] == policy.policy_id
    assert (ROOT / "data" / "sci" / "exposure_credit_policy.json").is_file()


@pytest.mark.parametrize("role,credit", [("PRIMARY", 1.0), ("SECONDARY", 0.5), ("MINOR", 0.0)])
def test_policy_v1_credits(role, credit):
    assert sc.load_credit_policy().credit(role) == credit


def test_unknown_role_credit_is_unknown_never_zero():
    credit = sc.load_credit_policy().credit("UNKNOWN")
    assert credit is sc.UNKNOWN_CREDIT
    assert credit != 0
    with pytest.raises(TypeError):
        _ = credit + 1.0  # type: ignore[operator]
    with pytest.raises(TypeError):
        float(credit)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        math.fsum([1.0, credit])  # type: ignore[list-item]


def test_a_role_outside_the_vocabulary_is_refused():
    with pytest.raises(ValueError):
        sc.load_credit_policy().credit("HALF")


def test_a_policy_that_turns_unknown_into_a_number_is_refused(tmp_path):
    bad = json.loads((ROOT / "data" / "sci" / "exposure_credit_policy.json").read_text(encoding="utf-8"))
    bad["credits"]["UNKNOWN"] = 0
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(sc.SciCatalogueError):
        sc.load_credit_policy(path)


def test_a_policy_missing_a_role_is_refused(tmp_path):
    bad = json.loads((ROOT / "data" / "sci" / "exposure_credit_policy.json").read_text(encoding="utf-8"))
    del bad["credits"]["MINOR"]
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(sc.SciCatalogueError):
        sc.load_credit_policy(path)


# ── un fichier mal formé est refusé au chargement, pas lu à moitié


def _rewrite(tmp_path: Path, mutate) -> Path:
    doc = json.loads((ROOT / "data" / "sci" / "exercise_catalogue.json").read_text(encoding="utf-8"))
    mutate(doc)
    path = tmp_path / "catalogue.json"
    path.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    return path


def test_unsorted_records_are_refused(tmp_path):
    path = _rewrite(tmp_path, lambda d: d["records"].reverse())
    with pytest.raises(sc.SciCatalogueError):
        sc.load_catalogue(path)


def test_duplicate_exercise_ids_are_refused(tmp_path):
    path = _rewrite(tmp_path, lambda d: d["records"].insert(1, d["records"][0]))
    with pytest.raises(sc.SciCatalogueError):
        sc.load_catalogue(path)


def test_an_alias_pointing_to_a_missing_canonical_is_refused(tmp_path):
    def mutate(d):
        alias = next(r for r in d["records"] if r["identity"]["identity_relation"] == "LEGACY_ALIAS")
        alias["identity"]["alias_of"] = "no-such-exercise"

    with pytest.raises(sc.SciCatalogueError):
        sc.load_catalogue(_rewrite(tmp_path, mutate))
