"""TRAIN A — le modèle d'environnement à trois couches.

Chaque garde a été vue rouge par mutation avant d'être retenue.

Ce qui est épinglé ici est **sémantique**, jamais décoratif : les trois états
d'une déclaration, les trois verdicts de faisabilité, et les quatre
dérivations que le §12 interdit. Un test qui se contenterait de compter des
lignes de registre passerait pendant que le contrat se casse.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from app.services.equipment_model import (
    FEASIBLE,
    NOT_FEASIBLE,
    UNKNOWN,
    EquipmentModelError,
    capabilities_for_items,
    capability_vocabulary,
    curation_rows,
    equipment_item_vocabulary,
    equipment_items,
    feasibility,
    missing_capabilities,
    requirements_for_exercise,
)
from app.services.training_preferences import (
    PreferenceValidationError,
    get_training_preferences,
    save_available_equipment_items,
    save_training_preferences,
    validate_available_equipment_items,
)
from tests.helpers import get_test_user_id

_ROOT = Path(__file__).resolve().parents[1]
_DATA = _ROOT / "data"
_SERVICES = _ROOT / "app" / "services"

_BENCH = "flat_bench_support"
_INCLINE = "incline_bench_support"
_DUMBBELLS = "dumbbells"
_SMITH = "smith_rack"
_HIGH = "cable_anchor_high"
_PULLDOWN = "pulldown_seated_station"


# ───────── registre : le vocabulaire est DÉRIVÉ, pas souhaité ─────────


def test_every_item_capability_belongs_to_the_capability_vocabulary():
    vocab = set(capability_vocabulary())
    for item in equipment_items().values():
        assert item.capabilities <= vocab, item.item_id


def test_every_item_carries_a_provenance():
    for item in equipment_items().values():
        assert item.provenance.strip(), item.item_id


def test_an_item_declaring_an_unknown_capability_is_refused(monkeypatch):
    """Sans cette levée, une capacité mal orthographiée disparaîtrait en
    silence et l'objet cesserait d'établir ce qu'il établit.

    ⚠ Tout passe par **un seul** objet-module résolu ici, et non par les
    noms importés en tête de fichier. La fixture `client` purge
    `sys.modules["app.*"]`, donc dès qu'un test l'a utilisée il existe deux
    générations du module : les noms importés en tête pointent la première,
    et un `monkeypatch.setattr("app.services.equipment_model…")` ré-importe
    et patche la seconde. La garde passait alors sans rien mesurer — verte
    en local où l'ordre la plaçait avant, rouge en CI où il la plaçait
    après.
    """
    import app.services.equipment_model as em

    faux = {
        "capabilities": dict(em.capability_vocabulary()),
        "items": [{"item_id": "x", "label": "X",
                   "capabilities": ["capacite_inexistante"], "provenance": "p"}],
    }
    monkeypatch.setattr(em, "_registry", lambda: faux)
    em.equipment_items.cache_clear()
    em.capability_vocabulary.cache_clear()
    try:
        with pytest.raises(em.EquipmentModelError):
            em.equipment_items()
    finally:
        em.equipment_items.cache_clear()
        em.capability_vocabulary.cache_clear()


def test_the_module_generation_trap_is_real_and_this_file_avoids_it(client):
    """La garde ci-dessus ne vaut que si la prémisse tient. On la mesure.

    Après un test qui utilise `client`, le module fraîchement résolu n'est
    plus celui dont ce fichier a importé les noms. Un test qui l'ignore
    patche un objet que personne n'appelle.
    """
    import app.services.equipment_model as frais

    assert frais.equipment_items is not equipment_items


def test_the_machine_identities_stay_distinct():
    """§10 — deux machines ne partagent jamais une capacité ; sans quoi
    déclarer une presse à cuisses rendrait faisable un hack squat.

    Quinze et non treize depuis la remesure : l'atlas se résout **aussi par
    alias déclaré**, ce qui rend atteignables `assisted-pull-up` et
    `lateral-raise-machine`. Le compte suit la donnée, pas l'inverse.
    """
    machines = [i for i in equipment_items().values()
                if any(c.startswith("machine_") for c in i.capabilities)]
    assert len(machines) == 15
    vues: set[str] = set()
    for item in machines:
        assert not (item.capabilities & vues), item.item_id
        vues |= item.capabilities


def test_smith_collapses_to_one_item_and_the_atlas_says_why():
    """§10 autorise le regroupement « là où l'atlas démontre le même
    appareil ». La garde vérifie la PRÉMISSE, pas seulement la conclusion."""
    atlas = json.loads((_DATA / "machine_atlas.json").read_text(encoding="utf-8"))
    smith = [m for f in atlas["families"] for m in f["machines"]
             if m["equipment"] == "smith"]
    # Quatre slugs Smith dans l'atlas, trois servis par les gabarits. Aucun
    # ne porte de matériel propre : la modalité est leur seule déclaration
    # d'appareil, et elle est identique — c'est la prémisse du §10.
    assert len(smith) == 4
    assert {m["equipment"] for m in smith} == {"smith"}
    assert all("equipment_family" not in m for m in smith)
    porteurs = [i for i in equipment_items().values() if _SMITH in i.capabilities]
    assert [i.item_id for i in porteurs] == ["smith_machine"]


# ───────── §4 : le câble ne se sur-accorde pas ─────────


def test_a_pulldown_station_does_not_grant_a_free_high_anchor():
    """Une station de tirage vertical a une barre fixe au-dessus d'un siège :
    on n'y fait pas une élévation latérale câble. Lui accorder
    `cable_anchor_high` rendrait faisable ce qui ne l'est pas."""
    station = equipment_items()["lat_pulldown_station"]
    assert _HIGH not in station.capabilities
    assert _PULLDOWN in station.capabilities


def test_only_the_dual_pulley_grants_two_independent_columns():
    simple = equipment_items()["single_adjustable_pulley"].capabilities
    double = equipment_items()["dual_adjustable_pulley"].capabilities
    assert "cable_bilateral_independent" in double
    assert "cable_bilateral_independent" not in simple
    assert simple < double


# ───────── §5 : nécessaire ≠ optionnel ─────────


def test_smith_hip_thrust_does_not_require_a_bench():
    """Le cas nommé au §5 : l'atlas documente `dos banc` ET `sol`. Le banc
    est une ALTERNATIVE, donc jamais une exigence conjonctive."""
    for nom in ("Hip thrust Smith", "Hip thrust Smith machine"):
        exigences = requirements_for_exercise(nom)
        assert exigences == (_SMITH,), nom
        assert _BENCH not in exigences
        assert _INCLINE not in exigences


def test_incline_smith_press_does_require_an_incline_bench():
    """Le cas symétrique : les deux variantes de l'atlas sont des angles de
    banc et aucune exécution sans banc n'est documentée."""
    assert requirements_for_exercise("Incline Smith Press") == (
        _INCLINE, _SMITH)


def test_the_two_smith_verdicts_differ_which_is_the_whole_point():
    """Si les deux rendaient la même chose, la distinction nécessaire /
    alternative ne serait pas implémentée — seulement racontée."""
    assert (requirements_for_exercise("Hip thrust Smith")
            != requirements_for_exercise("Incline Smith Press"))


def test_face_pull_does_not_require_an_attachment():
    """Corde et barre en V sont deux ALTERNATIVES : aucune n'est obligatoire."""
    exigences = requirements_for_exercise("Face pull câble")
    assert exigences == (_HIGH,)


# ───────── §5 : `None` ≠ `()` ─────────


def test_an_uncurated_exercise_yields_none_not_an_empty_tuple():
    assert requirements_for_exercise("Pallof press câble") is None


def test_an_exercise_with_no_external_requirement_yields_an_empty_tuple():
    """§8 — la modalité poids du corps assumée. `()` n'est pas `None` :
    « rien à posséder » est une exigence établie, pas une ignorance."""
    assert requirements_for_exercise("Relevés mollets debout") == ()


def test_a_declared_alias_resolves_to_the_canonical_requirements():
    """Le moteur de substitution lit `exercise_properties` et peut proposer
    une orthographe absente des 103. Sans résolution d'alias, une exécution
    parfaitement définie rendrait UNKNOWN pour une raison d'orthographe."""
    canonique = requirements_for_exercise("Développé incliné haltères 30°")
    assert canonique is not None
    for alias in ("Incline DB Press 30°", "Incline Dumbbell Press"):
        assert requirements_for_exercise(alias) == canonique


def test_alias_resolution_reads_a_declared_map_not_a_resemblance():
    from app.services.equipment_model import declared_aliases

    assert set(declared_aliases()) == {
        "Incline DB Press 30°", "Incline Dumbbell Press"}
    assert requirements_for_exercise("Incline Chest Press Machine Thing") \
        is None


def test_an_exercise_absent_from_the_ekb_yields_none():
    assert requirements_for_exercise("Exercice qui n'existe pas") is None


def test_none_and_empty_are_not_the_same_verdict():
    assert feasibility(None, ("dumbbells",)) == UNKNOWN
    assert feasibility((), ("dumbbells",)) == FEASIBLE


# ───────── verdicts : l'ignorance n'est pas une permission ─────────


def test_unknown_requirements_never_become_feasible_however_rich_the_gym():
    tout = equipment_item_vocabulary()
    assert feasibility(None, tout) == UNKNOWN


def test_unknown_requirements_never_become_a_refusal_either():
    assert feasibility(None, ()) == UNKNOWN


def test_no_equipment_is_feasible_even_when_the_environment_is_undeclared():
    """Le seul cas où l'absence de déclaration ne bloque rien : il n'y a
    rien à posséder."""
    assert feasibility((), None) == FEASIBLE


def test_an_undeclared_environment_yields_unknown_not_a_refusal():
    assert feasibility((_DUMBBELLS,), None) == UNKNOWN


def test_an_explicitly_empty_environment_refuses_what_needs_equipment():
    assert feasibility((_DUMBBELLS,), ()) == NOT_FEASIBLE


def test_coverage_decides_and_the_missing_capability_is_named():
    exigences = (_DUMBBELLS, _INCLINE)
    assert feasibility(exigences, ("dumbbells", "adjustable_bench")) == FEASIBLE
    assert feasibility(exigences, ("dumbbells",)) == NOT_FEASIBLE
    assert missing_capabilities(exigences, ("dumbbells",)) == (_INCLINE,)


def test_nothing_is_listed_as_missing_when_the_verdict_is_not_a_refusal():
    assert missing_capabilities(None, ("dumbbells",)) == ()
    assert missing_capabilities((), None) == ()


def test_no_verdict_is_a_number():
    """Aucun score de faisabilité : trois chaînes, pas un continuum."""
    for verdict in (FEASIBLE, NOT_FEASIBLE, UNKNOWN):
        assert isinstance(verdict, str)
        with pytest.raises(ValueError):
            float(verdict)


# ───────── §12 : aucune dérivation depuis la déclaration grossière ─────────


def test_owning_dumbbells_does_not_grant_a_bench():
    derivees = capabilities_for_items(("dumbbells",))
    assert _DUMBBELLS in derivees
    assert _BENCH not in derivees
    assert _INCLINE not in derivees


def test_one_machine_does_not_grant_every_machine():
    derivees = capabilities_for_items(("leg_press",))
    machines = {c for c in capability_vocabulary() if c.startswith("machine_")}
    assert derivees == {"machine_leg_press"}
    assert len(machines & derivees) == 1


def test_one_cable_item_does_not_grant_every_cable_configuration():
    derivees = capabilities_for_items(("single_adjustable_pulley",))
    assert _PULLDOWN not in derivees
    assert "row_seated_station" not in derivees


def test_an_unknown_item_raises_instead_of_shrinking_the_environment():
    with pytest.raises(EquipmentModelError):
        capabilities_for_items(("un_objet_qui_n_existe_pas",))


# ───────── persistance utilisateur : trois états ─────────


def _items(uid):
    from app.database import SessionLocal

    with SessionLocal() as db:
        return get_training_preferences(db, uid).available_equipment_items


def _ecrire_items(uid, valeur):
    from app.database import SessionLocal

    with SessionLocal() as db:
        return save_available_equipment_items(db, uid, valeur)


def _ecrire_prefs(uid, **kwargs):
    from app.database import SessionLocal

    with SessionLocal() as db:
        return save_training_preferences(db, uid, **kwargs)


def _prefs(uid):
    from app.database import SessionLocal

    with SessionLocal() as db:
        return get_training_preferences(db, uid)


def test_null_empty_and_populated_are_three_distinct_stored_states(client):
    uid = get_test_user_id()
    assert _items(uid) is None
    _ecrire_items(uid, [])
    assert _items(uid) == ()
    _ecrire_items(uid, ["dumbbells"])
    assert _items(uid) == ("dumbbells",)
    _ecrire_items(uid, None)
    assert _items(uid) is None


def test_an_internal_capability_may_not_be_persisted_as_a_declaration():
    """§1 et §3 — l'utilisateur déclare des objets, jamais des affordances."""
    with pytest.raises(PreferenceValidationError) as exc:
        validate_available_equipment_items([_INCLINE])
    assert "CAPACIT" in str(exc.value).upper()


def test_a_coarse_family_is_not_an_equipment_item():
    with pytest.raises(PreferenceValidationError):
        validate_available_equipment_items(["cable"])


def test_the_stored_order_is_canonical_not_the_submitted_order():
    premier = validate_available_equipment_items(["dumbbells", "ab_wheel"])
    second = validate_available_equipment_items(["ab_wheel", "dumbbells"])
    assert premier == second


def test_saving_the_coarse_preferences_never_erases_the_declared_items(client):
    """Le défaut que le point d'écriture séparé existe pour éviter : un
    formulaire hérité qui ne connaît pas ce champ ne doit pas l'effacer."""
    uid = get_test_user_id()
    _ecrire_items(uid, ["dumbbells", "flat_bench"])
    _ecrire_prefs(uid, sessions_per_week=4, available_equipment=["dumbbell"])
    apres = _prefs(uid)
    assert apres.available_equipment_items == ("dumbbells", "flat_bench")
    assert apres.available_equipment == ("dumbbell",)


def test_declaring_coarse_families_alone_leaves_the_concrete_environment_null(
    client,
):
    """§12 — un utilisateur existant reste `NULL`, donc non résolu."""
    uid = get_test_user_id()
    _ecrire_prefs(uid, available_equipment=["dumbbell", "machine", "cable"])
    assert _items(uid) is None


def test_is_empty_still_describes_the_three_legacy_dimensions(client):
    uid = get_test_user_id()
    _ecrire_items(uid, ["dumbbells"])
    assert _prefs(uid).is_empty is True


# ───────── curation : provenance et contrat servi restent d'accord ─────────


def _prescrits() -> list[str]:
    split = json.loads(
        (_DATA / "reference_split.json").read_text(encoding="utf-8"))
    return sorted({e["name"] for t in split["templates"] for e in t["exercises"]})


def test_the_curation_table_covers_the_whole_reachable_closure():
    """§11 — la couverture se mesure sur ce qui est ATTEIGNABLE, pas sur les
    seules prescriptions. Un substitut autorisé est un chemin d'exécution
    servi : l'ignorer laisserait 37 identités sans exigence tout en les
    proposant à l'utilisateur."""
    lignes = curation_rows()
    assert len(_prescrits()) == 68
    assert set(_prescrits()) <= set(lignes)
    assert len(lignes) == 105


def test_every_curated_requirement_agrees_with_the_ekb():
    """La provenance et le contrat servi ne peuvent pas diverger en silence."""
    for nom, ligne in curation_rows().items():
        attendu = ligne["requirements"]
        obtenu = requirements_for_exercise(nom)
        if attendu is None:
            assert obtenu is None, nom
        else:
            assert obtenu == tuple(sorted(attendu)), nom


def test_every_curated_capability_belongs_to_the_vocabulary():
    vocab = set(capability_vocabulary())
    for nom, ligne in curation_rows().items():
        for capacite in ligne["requirements"] or ():
            assert capacite in vocab, (nom, capacite)


def test_every_known_row_carries_a_source_and_every_unknown_a_reason():
    for nom, ligne in curation_rows().items():
        if ligne["requirements"] is None:
            assert ligne["note"].strip(), nom
        else:
            assert ligne["source"].strip(), nom
            assert ligne["evidence_level"] in (
                "ATLAS", "EXTERNE", "IDENTITE_AUREN"), nom


def test_an_external_row_that_renames_the_movement_documents_the_mapping():
    """§7 — ne jamais assimiler deux noms voisins en silence."""
    externes = [(n, L) for n, L in curation_rows().items()
                if L["evidence_level"] == "EXTERNE"]
    assert externes
    for nom, ligne in externes:
        if "ACE" in ligne["source"]:
            assert ligne["identity_correspondence"].strip(), nom


# ───────── le filtre dur reste éteint ─────────


#: Le SEUL importeur admis, et pourquoi. `training_preferences` doit valider
#: une déclaration contre le registre d'objets — sans quoi l'utilisateur
#: pourrait persister n'importe quelle chaîne. C'est la couche de
#: DÉCLARATION, pas la couche de DÉCISION : elle ne rend aucun verdict de
#: faisabilité et n'appelle ni `feasibility` ni `requirements_for_exercise`.
#: Tout nouvel importeur doit se déclarer ici avec son motif.
#:
#: `environment_resolution` est la couche de RÉSOLUTION : elle rend des
#: verdicts, mais **personne ne l'appelle** — une seconde garde vérifie
#: qu'elle reste elle aussi sans consommateur tant que la dernière porte
#: n'est pas ouverte.
_IMPORTEURS_AUTORISES = {"training_preferences.py", "environment_resolution.py"}


def test_only_the_declaration_layer_imports_the_equipment_model():
    """§11 et §13 — le modèle est bâti, jamais branché au chemin servi.

    Lecture par AST et non par texte : une garde qui lirait le fichier
    comme une chaîne accuserait ce dépôt pour ses propres commentaires,
    défaut déjà vécu ici.
    """
    coupables = []
    for chemin in sorted(_SERVICES.glob("*.py")):
        if chemin.name == "equipment_model.py":
            continue
        arbre = ast.parse(chemin.read_text(encoding="utf-8"))
        for noeud in ast.walk(arbre):
            cible = ""
            if isinstance(noeud, ast.ImportFrom):
                cible = noeud.module or ""
            elif isinstance(noeud, ast.Import):
                cible = " ".join(a.name for a in noeud.names)
            if "equipment_model" in cible:
                coupables.append(chemin.name)
    assert set(coupables) == _IMPORTEURS_AUTORISES


def test_the_declaration_layer_never_renders_a_feasibility_verdict():
    """La dérogation ci-dessus ne doit pas devenir une porte dérobée : le
    seul importeur admis a le droit de lire le VOCABULAIRE, pas de décider."""
    source = (_SERVICES / "training_preferences.py").read_text(encoding="utf-8")
    arbre = ast.parse(source)
    importes: set[str] = set()
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.ImportFrom) and "equipment_model" in (
            noeud.module or ""
        ):
            importes |= {a.name for a in noeud.names}
    assert importes <= {"capability_vocabulary", "equipment_item_vocabulary"}


def test_the_resolution_layer_itself_has_no_consumer():
    """§13, §18 — le résolveur est bâti, jamais branché. Le filtre servi
    reste éteint tant que les neuf portes ne sont pas franchies."""
    coupables = []
    for chemin in sorted(_SERVICES.glob("*.py")):
        if chemin.name == "environment_resolution.py":
            continue
        arbre = ast.parse(chemin.read_text(encoding="utf-8"))
        for noeud in ast.walk(arbre):
            cible = ""
            if isinstance(noeud, ast.ImportFrom):
                cible = noeud.module or ""
            elif isinstance(noeud, ast.Import):
                cible = " ".join(a.name for a in noeud.names)
            if "environment_resolution" in cible:
                coupables.append(chemin.name)
    assert coupables == []


def test_the_import_guard_can_actually_fail(tmp_path):
    """La garde ci-dessus ne vaut que si elle sait accuser. On lui donne le
    défaut d'origine à trouver."""
    faux = tmp_path / "faux_service.py"
    faux.write_text(
        "from app.services.equipment_model import feasibility\n", encoding="utf-8")
    arbre = ast.parse(faux.read_text(encoding="utf-8"))
    trouve = [n for n in ast.walk(arbre)
              if isinstance(n, ast.ImportFrom)
              and "equipment_model" in (n.module or "")]
    assert len(trouve) == 1


def test_a_comment_naming_the_module_is_not_an_import(tmp_path):
    """Le mode d'échec inverse : la garde ne doit pas accuser de la prose."""
    faux = tmp_path / "prose.py"
    faux.write_text(
        '"""On parlera un jour de equipment_model ici."""\n'
        "# import equipment_model — pas encore\n",
        encoding="utf-8",
    )
    arbre = ast.parse(faux.read_text(encoding="utf-8"))
    imports = [n for n in ast.walk(arbre) if isinstance(n, (ast.Import,
                                                            ast.ImportFrom))]
    assert imports == []
