"""Sb_SCI_V2_02 — le résolveur d'identité scientifique (spec §6).

nom historique / variant_key → identité scientifique → fiche canonique.
Déterministe, en lecture seule, sans correspondance floue, et l'inconnu est une VALEUR.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

import app.models  # noqa: F401 — peuple Base.metadata
from app.database import Base
from app.models.exercise import Exercise, ExerciseAlias
from app.services import sci_identity as si
from app.services.exercise_identity import add_alias, ensure_exercise
from app.services.sci_catalogue import load_catalogue
from app.services.seed_exercise_identity import seed_exercise_identity

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


@pytest.fixture(scope="module")
def resolver() -> si.SciIdentityResolver:
    return si.load_resolver()


@pytest.fixture
def db():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine)() as s:
        yield s


@pytest.fixture
def seeded(db: Session) -> Session:
    seed_exercise_identity(db)
    db.commit()
    return db


def _ekb() -> dict:
    return json.loads((DATA / "exercise_knowledge_base.json").read_text(encoding="utf-8"))


# ── étape 2 : l'index des noms, dérivé de l'EKB


def test_every_ekb_canonical_name_resolves_to_its_record(resolver):
    catalogue = load_catalogue()
    for name, entry in _ekb()["exercises"].items():
        res = resolver.resolve_name(name)
        assert res.status == si.RESOLVED, name
        assert res.step == si.STEP_NAME_INDEX
        assert res.canonical_exercise_id == catalogue.canonical_of(entry["variant_key"])["exercise_id"], name


def test_declared_ekb_aliases_resolve(resolver):
    res = resolver.resolve_name("Incline Dumbbell Press")
    assert res.is_resolved
    assert res.canonical_exercise_id == "developpe-incline-halteres-30"


def test_case_accents_and_punctuation_do_not_matter(resolver):
    for spelling in ("TRICEPS PUSHDOWN CORDE", "triceps   pushdown, corde", "Élévations latérales câble",
                     "elevations laterales cable"):
        assert resolver.resolve_name(spelling).is_resolved, spelling


def test_the_one_collision_under_normalize_is_the_same_identity(resolver):
    """« Curl marteau câble (corde) » et « … corde » se normalisent à l'identique (mesuré) :
    ce sont deux alias d'une même identité, résolus vers la fiche canonique."""
    a = resolver.resolve_name("Curl marteau câble (corde)")
    b = resolver.resolve_name("Curl marteau câble corde")
    assert a.scientific_identity_id == b.scientific_identity_id == "cable_rope_hammer_curl"
    assert a.canonical_exercise_id == b.canonical_exercise_id == "curl-marteau-cable-paren-corde"


def test_a_collision_between_distinct_identities_is_refused():
    ekb = _ekb()
    ekb["exercises"]["Pompes!"] = dict(ekb["exercises"]["Squat au poids du corps"])
    catalogue = load_catalogue()
    with pytest.raises(si.SciIdentityError):
        si.build_name_index(ekb, catalogue)


# ── un alias n'est jamais un candidat : la résolution rend toujours la fiche canonique


def test_a_legacy_alias_resolves_to_its_canonical_record(resolver):
    res = resolver.resolve_name("Pushdown corde")
    assert res.variant_key == "pushdown-corde"
    assert res.canonical_exercise_id == "triceps-pushdown-corde"
    assert res.scientific_identity_id == "cable_rope_triceps_pushdown"


def test_every_resolution_lands_on_a_canonical_record(resolver):
    catalogue = load_catalogue()
    for name in _ekb()["exercises"]:
        rid = resolver.resolve_name(name).canonical_exercise_id
        assert catalogue.record(rid)["identity"]["identity_relation"] == "CANONICAL"


def test_operator_merges_resolve_together(resolver):
    """G12 : un ancien « Curl poulie basse » compte comme le curl barre (définition opérateur)."""
    assert resolver.resolve_name("Curl poulie basse").canonical_exercise_id == "curl-poulie-basse-paren-barre"
    assert resolver.resolve_name("Curl câble basse").canonical_exercise_id == "curl-poulie-basse-paren-barre"


# ── étape 1 : variant_key


def test_a_known_variant_key_resolves_at_step_one(resolver):
    res = resolver.resolve(variant_key="face-pull-cable", name="anything")
    assert res.step == si.STEP_VARIANT_KEY
    assert res.canonical_exercise_id == "face-pull-cable-paren-corde"


def test_an_unknown_variant_key_falls_back_to_the_name(resolver):
    res = resolver.resolve(variant_key="no-such-key", name="Pompes")
    assert res.step == si.STEP_NAME_INDEX
    assert res.canonical_exercise_id == "pompes"


# ── l'inconnu est une valeur, jamais None ni une ressemblance


@pytest.mark.parametrize("name", [
    "Curl marteau cable",        # mot manquant
    "Triceps pushdwn corde",     # faute de frappe
    "Développé couché",          # préfixe d'un nom réel
    "Mon exercice perso",
])
def test_no_fuzzy_matching(resolver, name):
    res = resolver.resolve_name(name)
    assert res.status == si.UNKNOWN_IDENTITY
    assert res.canonical_exercise_id is None
    assert res.scientific_identity_id is None
    assert res.reason


@pytest.mark.parametrize("name", ["", "   ", None, "!!!"])
def test_a_blank_name_is_unknown_not_an_error(resolver, name):
    res = resolver.resolve_name(name)
    assert res.status == si.UNKNOWN_IDENTITY
    assert res.reason


def test_resolution_is_deterministic():
    a, b = si.load_resolver(), si.build_resolver()
    for name in list(_ekb()["exercises"]) + ["Mon exercice perso"]:
        assert a.resolve_name(name) == b.resolve_name(name)


def test_every_resolution_carries_the_catalogue_version(resolver):
    version = load_catalogue().header["catalogue_version"]
    assert resolver.resolve_name("Pompes").catalogue_version == version
    assert resolver.resolve_name("inconnu").catalogue_version == version


# ── étape 3 : l'identité d'exercice en base, en LECTURE SEULE


def test_a_database_alias_resolves_at_step_three(resolver, seeded):
    target = seeded.execute(select(Exercise).where(Exercise.name == "Pompes")).scalar_one()
    add_alias(seeded, target, "Push-up classique")
    seeded.commit()
    assert resolver.resolve_name("Push-up classique").status == si.UNKNOWN_IDENTITY
    res = resolver.resolve_name("Push-up classique", db=seeded)
    assert res.step == si.STEP_DATABASE
    assert res.canonical_exercise_id == "pompes"


def test_a_database_identity_without_scientific_record_stays_unknown(resolver, db):
    ensure_exercise(db, "Exercice maison inédit")
    db.commit()
    res = resolver.resolve_name("Exercice maison inédit", db=db)
    assert res.status == si.UNKNOWN_IDENTITY
    assert "sans fiche scientifique" in res.reason


def test_resolving_never_writes_to_the_database(resolver, seeded):
    before = (seeded.scalar(select(func.count(Exercise.id))), seeded.scalar(select(func.count(ExerciseAlias.id))))
    for name in ("Mon exercice perso", "Pompes", "Exercice jamais vu"):
        resolver.resolve_name(name, db=seeded)
    assert not seeded.new
    assert not seeded.dirty
    after = (seeded.scalar(select(func.count(Exercise.id))), seeded.scalar(select(func.count(ExerciseAlias.id))))
    assert after == before


# ── concordance des étapes 2 et 3 sur tout le corpus de noms du produit


def _product_names() -> set[str]:
    split = json.loads((DATA / "reference_split.json").read_text(encoding="utf-8"))
    names = set()
    for template in split["templates"]:
        for ex in template.get("exercises", []):
            names.add(ex["name"])
            names.update(s for s in ex.get("substitutes", []) or [] if isinstance(s, str))
    names |= set(json.loads((DATA / "exercise_properties.json").read_text(encoding="utf-8"))["exercises"])
    names |= set(json.loads((DATA / "equipment_curation.json").read_text(encoding="utf-8"))["rows"])
    ekb = _ekb()
    return names | set(ekb["exercises"]) | set(ekb.get("_aliases", {}))


def test_every_product_name_resolves(resolver):
    unknown = sorted(n for n in _product_names() if not resolver.resolve_name(n).is_resolved)
    assert unknown == []


def test_steps_two_and_three_agree_on_the_whole_corpus(resolver, seeded):
    disagreements = []
    for name in sorted(_product_names()):
        by_index = resolver.resolve_name(name)
        by_db = resolver.resolve_through_database(name, seeded)
        if by_db.is_resolved and by_db.canonical_exercise_id != by_index.canonical_exercise_id:
            disagreements.append((name, by_index.canonical_exercise_id, by_db.canonical_exercise_id))
    assert disagreements == []


# ── garde de renommage : les noms passés restent lisibles (relevé figé)


def _ledger() -> dict:
    return json.loads((DATA / "sci" / "legacy_name_ledger.json").read_text(encoding="utf-8"))


def test_every_recorded_name_still_resolves_to_its_record(resolver):
    catalogue = load_catalogue()
    ledger = _ledger()
    for name, variant_key in {**ledger["canonical_names"], **ledger["declared_aliases"]}.items():
        res = resolver.resolve_name(name)
        assert res.is_resolved, f"« {name} » ne se résout plus : renommage sans alias préalable ?"
        assert res.canonical_exercise_id == catalogue.canonical_of(variant_key)["exercise_id"], name


def test_every_current_ekb_name_is_recorded():
    ledger = _ledger()
    ekb = _ekb()
    assert set(ekb["exercises"]) <= set(ledger["canonical_names"])
    assert set(ekb.get("_aliases", {})) <= set(ledger["declared_aliases"])


def test_the_rename_guard_bites(tmp_path):
    """Planter le défaut : renommer une entrée EKB sans alias rend le nom relevé irrésoluble."""
    ekb = _ekb()
    ekb["exercises"]["Pompes classiques"] = ekb["exercises"].pop("Pompes")
    renamed = si.SciIdentityResolver(load_catalogue(), si.build_name_index(ekb, load_catalogue()))
    assert renamed.resolve_name("Pompes").status == si.UNKNOWN_IDENTITY
    ekb["_aliases"]["Pompes"] = "Pompes classiques"
    with_alias = si.SciIdentityResolver(load_catalogue(), si.build_name_index(ekb, load_catalogue()))
    assert with_alias.resolve_name("Pompes").canonical_exercise_id == "pompes"
