"""`Sb_EXERCISE_IDENTITY_01` — gardes de l'identité d'exercice.

CE QUE CES GARDES DÉFENDENT
---------------------------
Avant cette tranche, **aucune table ne représentait un exercice**. Trois
vocabulaires coexistaient (`template_exercises.code` = position `E1…E8`,
`exercise_muscle_mappings.exercise_code` = un nom, `session_exercises` = du
texte figé), et la seule clé de jointure possible était **le nom** — donc la
seule chose que le produit ait le droit de changer.

Mesures qui ont dicté la forme retenue, toutes reproduites ici en garde :

* 7 codes sur 8 portent plusieurs noms → le code n'est pas une identité ;
* 28 noms sur 68 vivent dans ≥2 gabarits → `template_exercises.id` non plus ;
* slugification déterministe des 68 noms → 68 slugs, **0 collision** ;
* l'EKB est un **surensemble strict** du catalogue (68 ⊂ 103).
"""
from __future__ import annotations

import ast
import json
import pathlib

import pytest
from sqlalchemy import create_engine, func, inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base
from app.models.exercise import Exercise, ExerciseAlias
from app.services.exercise_identity import (
    SLUG_MAX,
    add_alias,
    ensure_exercise,
    normalize,
    resolve_exercise,
    slugify,
)
from app.services.seed_exercise_identity import seed_exercise_identity

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


@pytest.fixture
def db():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine)() as s:
        yield s


# ───────────── normalisation : la seule clé de comparaison ─────────────

def test_normalize_folds_accents_case_and_punctuation():
    assert normalize("Élévations latérales câble") == "elevations laterales cable"


def test_the_two_spellings_the_repo_actually_contains_collapse():
    """Le catalogue écrit « (corde) », l'EKB écrit « corde ». Même mouvement.

    Ce n'est pas un cas d'école : les deux chaînes sont dans deux fichiers de
    `data/`, et leur similarité après normalisation vaut 1,00.
    """
    assert normalize("Curl marteau câble (corde)") == normalize(
        "Curl marteau câble corde"
    )


def test_normalize_is_idempotent():
    once = normalize("Rowing haltère un bras (banc)")
    assert normalize(once) == once


@pytest.mark.parametrize("blank", ["", "   ", "()", "—", "///"])
def test_names_with_nothing_to_normalize_resolve_to_nothing(blank):
    assert normalize(blank) == ""


# ───────────── slug : engendré une fois, jamais régénéré ─────────────

def test_slug_has_a_stated_value_not_merely_a_stable_one():
    """Asserter `slugify(x) == slugify(x)` ne prouve que la pureté. Le contrat
    est la **forme** produite, parce que c'est elle qui sera figée en base."""
    assert slugify("Développé incliné haltères 30°") == "developpe-incline-halteres-30"
    assert slugify("Rear delt fly machine (pec deck inversé)") == (
        "rear-delt-fly-machine-pec-deck-inverse"
    )


def test_slug_refuses_a_name_it_cannot_represent():
    with pytest.raises(ValueError):
        slugify("///")


def test_slug_refuses_to_truncate_rather_than_break_uniqueness_silently():
    with pytest.raises(ValueError, match="unicité"):
        slugify("a" * (SLUG_MAX + 1))


def test_renaming_an_exercise_does_not_change_its_identity(db: Session):
    """Le point de toute la tranche. `name` bouge, `slug` non."""
    ex = ensure_exercise(db, "Développé incliné haltères")
    slug = ex.slug
    ex.name = "Incline dumbbell press"
    db.flush()
    assert ex.slug == slug


def test_ensure_never_rewrites_the_name_of_an_existing_row(db: Session):
    """Renommer est un geste produit, pas un effet de bord de graine."""
    ensure_exercise(db, "Curl marteau câble (corde)")
    again = ensure_exercise(db, "Curl marteau câble corde")
    assert again.name == "Curl marteau câble (corde)"


# ───────────── résolution ─────────────

def test_ensure_is_idempotent(db: Session):
    a = ensure_exercise(db, "Hip thrust Smith")
    b = ensure_exercise(db, "Hip thrust Smith")
    assert a.id == b.id
    assert db.execute(select(func.count()).select_from(Exercise)).scalar_one() == 1


def test_resolution_goes_through_the_alias_table_even_for_the_own_name(db: Session):
    """Un seul chemin de résolution — pas de « principal » et « alias » à tenir
    en accord. L'exercice possède toujours un alias : le sien."""
    ex = ensure_exercise(db, "Face pull câble")
    aliases = db.execute(
        select(ExerciseAlias).where(ExerciseAlias.exercise_id == ex.id)
    ).scalars().all()
    assert [a.alias for a in aliases] == ["Face pull câble"]


def test_an_alias_resolves_to_its_exercise(db: Session):
    ex = ensure_exercise(db, "Développé incliné haltères 30°")
    add_alias(db, ex, "Incline DB Press 30°")
    assert resolve_exercise(db, "incline db press 30").id == ex.id


def test_an_unknown_name_resolves_to_nothing(db: Session):
    ensure_exercise(db, "Hip thrust Smith")
    assert resolve_exercise(db, "Exercice qui n'existe pas") is None


def test_a_blank_name_resolves_to_nothing_rather_than_the_first_row(db: Session):
    ensure_exercise(db, "Hip thrust Smith")
    assert resolve_exercise(db, "   ") is None


def test_claiming_an_alias_already_held_by_another_exercise_is_refused(db: Session):
    """Repointer serait une FUSION, et une fusion est un jugement produit."""
    a = ensure_exercise(db, "Triceps pushdown corde")
    b = ensure_exercise(db, "Triceps pushdown barre")
    assert add_alias(db, b, "Triceps pushdown corde") is None
    assert resolve_exercise(db, "Triceps pushdown corde").id == a.id


def test_the_database_itself_refuses_a_duplicate_normalized_alias(db: Session):
    """La garde applicative ne suffit pas : la contrainte est en base."""
    a = ensure_exercise(db, "Face pull câble")
    db.add(ExerciseAlias(
        exercise_id=a.id, alias="FACE PULL CABLE",
        normalized=normalize("Face pull câble"), source="manual",
    ))
    with pytest.raises(IntegrityError):
        db.flush()


# ───────────── graine ─────────────

def test_seed_creates_one_identity_per_distinct_catalog_name(db: Session):
    report = seed_exercise_identity(db)
    payload = json.loads((DATA / "reference_split.json").read_text(encoding="utf-8"))
    distinct = {e["name"] for t in payload["templates"] for e in t.get("exercises", [])}
    assert report.created_catalog == len(distinct)


def test_seed_covers_every_catalog_name(db: Session):
    seed_exercise_identity(db)
    payload = json.loads((DATA / "reference_split.json").read_text(encoding="utf-8"))
    missing = [
        e["name"]
        for t in payload["templates"]
        for e in t.get("exercises", [])
        if resolve_exercise(db, e["name"]) is None
    ]
    assert missing == []


def test_every_ekb_name_resolves(db: Session):
    """Mesuré : les 68 du catalogue ⊂ les 103 de l'EKB."""
    seed_exercise_identity(db)
    ekb = json.loads((DATA / "exercise_knowledge_base.json").read_text(encoding="utf-8"))
    missing = [n for n in ekb["exercises"] if resolve_exercise(db, n) is None]
    assert missing == []


#: **103 entrées EKB, 102 exercices.** Deux lignes désignent le même mouvement
#: — écart d'orthographe invisible avant normalisation — et elles se
#: CONTREDISENT : `Curl marteau câble (corde)` porte `zone_primary=biceps`
#: avec `confidence=measured`, `Curl marteau câble corde` porte `None` avec
#: `confidence=derived`. Le même exercice était donc cartographié ou non selon
#: l'orthographe rencontrée.
#:
#: La graine passe le catalogue en premier, si bien que l'entrée conservée est
#: celle que l'utilisateur voit — ici, aussi la mesurée. Le jour où l'EKB sera
#: nettoyé, cette garde tombera et dira laquelle des deux a survécu.
EKB_KNOWN_COLLAPSE = ("Curl marteau câble (corde)", "Curl marteau câble corde")


def test_the_ekb_holds_exactly_one_pair_of_names_for_the_same_exercise(db: Session):
    report = seed_exercise_identity(db)
    ekb = json.loads((DATA / "exercise_knowledge_base.json").read_text(encoding="utf-8"))
    assert report.total == len(ekb["exercises"]) - 1, (
        "le nombre de doublons d'orthographe dans l'EKB a changé — le "
        "constater, pas l'absorber"
    )
    a, b = EKB_KNOWN_COLLAPSE
    assert {a, b} <= set(ekb["exercises"])
    assert resolve_exercise(db, a).id == resolve_exercise(db, b).id


def test_the_surviving_row_of_the_collapse_is_the_one_the_user_sees(db: Session):
    """Ordre des sources : le catalogue d'abord, pour que `name` soit le nom
    affiché et non une variante d'enrichissement."""
    seed_exercise_identity(db)
    kept, _ = EKB_KNOWN_COLLAPSE
    assert resolve_exercise(db, kept).name == kept


def test_seed_is_idempotent(db: Session):
    first = seed_exercise_identity(db)
    second = seed_exercise_identity(db)
    assert second.created_catalog == 0
    assert second.created_ekb == 0
    assert second.aliases_declared == 0
    assert second.total == first.total


def test_the_declared_aliases_are_applied(db: Session):
    seed_exercise_identity(db)
    ekb = json.loads((DATA / "exercise_knowledge_base.json").read_text(encoding="utf-8"))
    for alias, canonical in ekb["_aliases"].items():
        assert resolve_exercise(db, alias) is not None, alias
        assert resolve_exercise(db, alias).id == resolve_exercise(db, canonical).id


def test_seed_reports_conflicts_instead_of_resolving_them_silently(db: Session):
    """Un alias réclamant un nom déjà pris est RENDU, jamais absorbé."""
    ensure_exercise(db, "Incline DB Press 30°")  # squatte l'alias déclaré
    report = seed_exercise_identity(db)
    assert any("Incline DB Press 30" in c for c in report.alias_conflicts)


def test_no_slug_collides_across_the_whole_seed(db: Session):
    """Mesuré à 0 collision sur 68 noms. La garde couvre les 103."""
    seed_exercise_identity(db)
    slugs = db.execute(select(Exercise.slug)).scalars().all()
    assert len(slugs) == len(set(slugs))


# ───────────── périmètre ─────────────

def test_the_migration_adds_no_column_to_any_existing_table():
    """Additive stricte. Remplir une colonne neuve sur `session_exercises`
    resterait un UPDATE de lignes historiques — arrêt dur du contrat."""
    src = (ROOT / "migrations" / "versions"
           / "20260822_add_exercise_identity.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    calls = [
        n.func.attr for n in ast.walk(tree)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
        and isinstance(n.func.value, ast.Name) and n.func.value.id == "op"
    ]
    assert "add_column" not in calls
    assert "alter_column" not in calls
    assert "execute" not in calls, "une migration qui exécute du SQL sème ou mute"
    assert set(calls) <= {"create_table", "create_index", "drop_table",
                          "drop_index", "get_bind"}


def test_the_two_tables_exist_after_metadata_create():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    tables = set(inspect(engine).get_table_names())
    assert {"exercises", "exercise_aliases"} <= tables


def test_the_decision_engines_never_import_the_identity_service():
    """Même garde que pour le résolveur de zones : les moteurs gelés
    n'apprennent rien de cette tranche."""
    offenders = []
    for name in ("recommendation", "substitution", "behavioral"):
        path = ROOT / "app" / "services" / f"{name}.py"
        if not path.exists():
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            mod = getattr(node, "module", None) or ""
            names = [a.name for a in getattr(node, "names", [])]
            if "exercise_identity" in mod or any("exercise_identity" in n for n in names):
                offenders.append(name)
    assert offenders == []
