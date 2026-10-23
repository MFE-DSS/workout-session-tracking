"""Génère le catalogue scientifique d'exercices depuis ses sources (`Sb_SCI_V2_01`).

Chemin canonique de génération de `data/sci/`. Aucune fiche scientifique ne s'édite à la main :
ce script rejoue la **clôture** — les rulings de l'opérateur — sur les sources curées et revues
de `data/sci/sources/`, et rend quatre artefacts, reproductibles à l'octet :

* `exercise_catalogue.schema.json` — schéma arbitré + delta de clôture (vocabulaires fermés) ;
* `exercise_catalogue.json`        — les 107 fiches closes ;
* `train_a_delta_proposal.json`    — delta TRAIN A **proposé**, jamais appliqué au registre servi ;
* `exercise_catalogue.changes.txt` — journal des changements appliqués par la clôture.

Le rapport de validation est produit par `scripts/validate_sci_catalogue.py`.

Spec : `docs/strategy/Sx_SCI_V2_CATALOGUE_INTEGRATION_01_SPEC.md` (§19 pour les rulings du
GO BUILD). Les invariants des rulings sont gardés **indépendamment** par
`tests/test_sci_catalogue_rulings.py`.

Usage :
    python scripts/generate_sci_catalogue.py           # écrit les artefacts
    python scripts/generate_sci_catalogue.py --check   # échoue si un artefact diffère
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCI = "data/sci"
SOURCES = f"{SCI}/sources"
SCHEMA = f"{SCI}/exercise_catalogue.schema.json"
CATALOGUE = f"{SCI}/exercise_catalogue.json"
DELTA = f"{SCI}/train_a_delta_proposal.json"
CHANGES = f"{SCI}/exercise_catalogue.changes.txt"
OUTPUTS = (SCHEMA, CATALOGUE, DELTA, CHANGES)
#: autorités lues par le générateur en plus des sources curées
AUTHORITIES = (f"{SCI}/evidence_registry.json", f"{SCI}/exposure_credit_policy.json")

SCHEMA_VERSION = "v2-closure-2026-10-23"
CATALOGUE_VERSION = "auren-exercise-catalogue-v2-closure-2"
DELTA_VERSION = "Sb_SCI_V2_01"
TODAY = "2026-10-23"
ROPE, BAR = "cable_attachment_rope", "cable_attachment_straight_bar"
CLOSE_NEUTRAL_ROW = "cable_attachment_close_neutral_row_handle"


def _read(root: Path, rel: str):
    return json.loads((root / rel).read_text(encoding="utf-8"))


def _dump(obj) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def sources_digest(root: Path = ROOT) -> str:
    """Condensat des sources et autorités lues : remplace l'horodatage, qui interdisait l'octet."""
    h = hashlib.sha256()
    files = sorted((root / SOURCES).rglob("*")) + [root / a for a in AUTHORITIES]
    for path in files:
        if path.is_file():
            h.update(path.relative_to(root).as_posix().encode("utf-8") + b"\0")
            h.update(path.read_bytes() + b"\0")
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Schéma : arbitré + delta de clôture
# ---------------------------------------------------------------------------

ACTIONS_ADDED = ["trunk_anti_rotation", "trunk_anti_extension", "scapular_upward_rotation",
                 "scapular_downward_rotation"]
PATTERNS_ADDED = ["chest_fly", "shrug", "pullover", "trunk_anti_rotation", "trunk_anti_extension"]
CAPABILITY_ATOM = {"type": "string", "pattern": "^[a-z0-9_]+$"}


def _schema_vocabularies(s: dict) -> None:
    sci = s["properties"]["exercise_science"]["properties"]
    sci["loaded_joint_actions"]["items"]["enum"] += ACTIONS_ADDED
    sci["loaded_joint_actions"]["x-justification"] = (
        sci["loaded_joint_actions"].get("x-justification", "")
        + " Clôture : trunk_anti_rotation et trunk_anti_extension sont des actions ISOMÉTRIQUES CHARGÉES "
          "(résistance à un moment externe imposé) ; scapular_upward_rotation / scapular_downward_rotation "
          "sont les rotations de l'omoplate chargées (Y-raise, élévations ; tirages verticaux)."
    ).strip()
    sci["movement_pattern"]["enum"] += PATTERNS_ADDED
    sci["movement_pattern"]["x-justification"] = (
        "Liste fermée. Clôture : chest_fly, shrug, pullover, trunk_anti_rotation, trunk_anti_extension ajoutés ; "
        "aucun exercice n'est plus rangé dans le pattern le plus proche.")
    defs = s["$defs"]
    defs["contribution"]["properties"]["role"]["x-justification"] = (
        "PRIMARY : la zone est le contributeur principal (a) d'une action articulaire chargée, OU (b) de la "
        "résistance à un moment externe imposé pendant une action ISOMÉTRIQUE chargée (trunk_anti_rotation, "
        "trunk_anti_extension). Le simple gainage générique (isometric_trunk_bracing) ne fonde toujours pas un "
        "PRIMARY. SECONDARY : synergiste. MINOR : stabilisateur, crédit 0 par politique versionnée. UNKNOWN : "
        "ne bloque que le PRIMARY de cette zone, vecteur incomplet, jamais une preuve d'absence.")
    defs["zone"]["x-justification"] = (
        "15 zones atomiques (arbitrage 1). posterior_chain n'est pas une zone. Comptabilité de `abs` : PAROI "
        "ABDOMINALE ANTÉROLATÉRALE (droit de l'abdomen, obliques interne et externe, transverse), pas le seul "
        "droit de l'abdomen (clôture, ruling 1).")
    sci["canonical_execution"] = {
        "type": "string", "minLength": 20,
        "x-evidence-label": "DERIVED_PRODUCT_HEURISTIC", "x-requirement": "CONDITIONAL",
        "x-justification": "Exécution canonique fixée par l'opérateur quand le nom historique est ambigu. Les "
                           "contributions sont curées depuis CETTE exécution, jamais depuis l'ancien nom.",
    }


def _schema_equipment(s: dict) -> None:
    op = s["properties"]["exercise_operational"]
    op["properties"]["equipment_mode"]["enum"] += ["machine_unspecified", "unknown"]
    op["properties"]["equipment_mode"]["x-justification"] += (
        " Clôture : machine_unspecified = machine connue, mécanisme de résistance non établi ; unknown = rien "
        "d'établi. « Machine » seul ne devient jamais machine_selectorized.")
    del op["properties"]["equipment_required"]
    op["required"] = [r for r in op["required"] if r != "equipment_required"]
    op["required"] += ["equipment_requirements", "equipment_requirement_status"]
    op["properties"]["equipment_requirements"] = {
        "type": "array", "uniqueItems": True,
        "items": {"oneOf": [
            CAPABILITY_ATOM,
            {"type": "object", "additionalProperties": False, "required": ["any_of"],
             "properties": {"any_of": {"type": "array", "minItems": 2, "uniqueItems": True, "items": CAPABILITY_ATOM}}},
        ]},
        "x-evidence-label": "DERIVED_PRODUCT_HEURISTIC", "x-requirement": "REQUIRED",
        "x-placement": "Vocabulaire des CAPACITÉS du registre TRAIN A (data/equipment_registry.json + delta proposé) ; "
                       "aucune seconde ontologie d'équipement.",
        "x-justification": "Grammaire V1 : conjonction de capacités atomiques et de groupes {any_of} de capacités "
                           "atomiques (au moins deux). Aucune expression booléenne imbriquée. Liste vide RÉSOLUE = "
                           "aucun équipement requis.",
    }
    op["properties"]["equipment_requirement_status"] = {
        "enum": ["RESOLVED", "UNKNOWN"],
        "x-evidence-label": "DERIVED_PRODUCT_HEURISTIC", "x-requirement": "REQUIRED",
        "x-justification": "Distingue « rien de requis » (RESOLVED + liste vide) de « exigence inconnue » (UNKNOWN). "
                           "Une liste vide ne signifie jamais « vocabulaire manquant ».",
    }
    s["allOf"].append({
        "if": {"properties": {"exercise_operational": {"properties": {"equipment_requirement_status": {"const": "UNKNOWN"}},
                                                        "required": ["equipment_requirement_status"]}},
               "required": ["exercise_operational"]},
        "then": {"properties": {"exercise_operational": {"properties": {"equipment_requirements": {"maxItems": 0}}}}},
        "x-justification": "Une exigence UNKNOWN ne porte pas de capacités partielles qui se feraient passer pour complètes.",
    })


def _schema_identity(s: dict) -> None:
    s["required"] = list(dict.fromkeys(s["required"] + ["identity"]))
    s["properties"]["identity"] = {
        "type": "object", "additionalProperties": False,
        "required": ["scientific_identity_id", "identity_relation", "alias_of", "group_classification"],
        "properties": {
            "scientific_identity_id": {"type": "string", "pattern": "^[a-z][a-z0-9_]+$"},
            "identity_relation": {"enum": ["CANONICAL", "LEGACY_ALIAS"]},
            "alias_of": {"type": ["string", "null"]},
            "group_classification": {"enum": ["UNIQUE", "EXACT_CANONICAL_DUPLICATE", "LEGITIMATE_VARIANT", "UNRESOLVED"]},
            "canonical_display_name": {"type": "string", "minLength": 3},
            "merge_basis": {"enum": ["source_facts", "operator_definition"],
                            "x-justification": "Pourquoi un alias rejoint son identité : les faits sources le prouvent, ou "
                                               "l'opérateur a DÉFINI l'exécution canonique (définition produit, pas "
                                               "l'affirmation que chaque exécution historique est connue)."},
        },
        "x-evidence-label": "DERIVED_PRODUCT_HEURISTIC", "x-requirement": "REQUIRED",
        "x-justification": "Une identité scientifique canonique par mouvement ; les identifiants historiques sont "
                           "conservés comme alias (jamais supprimés ni réécrits). Le compilateur ne voit que les "
                           "fiches CANONICAL.",
    }
    s["allOf"].append({
        "if": {"properties": {"identity": {"properties": {"identity_relation": {"const": "LEGACY_ALIAS"}},
                                           "required": ["identity_relation"]}}, "required": ["identity"]},
        "then": {"properties": {"identity": {"properties": {"alias_of": {"type": "string"},
                                                            "group_classification": {"const": "EXACT_CANONICAL_DUPLICATE"}},
                                             "required": ["merge_basis"]}}},
        "else": {"properties": {"identity": {"properties": {"alias_of": {"type": "null"}},
                                             "required": ["canonical_display_name"]}}},
        "x-justification": "Un alias pointe vers sa fiche canonique et n'existe que pour un doublon exact ; une fiche "
                           "canonique porte son nom d'affichage.",
    })


def _schema_content_alignment(s: dict) -> None:
    text = {"type": "string", "minLength": 3}
    s["properties"]["content_alignment"] = {
        "type": "object", "additionalProperties": False,
        "required": ["status", "served_content", "exact_exposure_evidence", "note"],
        "properties": {
            "status": {"enum": ["CONTENT_EXECUTION_MISMATCH"]},
            "served_content": {"type": "array", "minItems": 1, "items": {
                "type": "object", "additionalProperties": False, "required": ["source", "text"],
                "properties": {"source": text, "text": text}}},
            "exact_exposure_evidence": {"const": False},
            "note": {"type": "string", "minLength": 20},
        },
        "x-evidence-label": "DERIVED_PRODUCT_HEURISTIC", "x-requirement": "CONDITIONAL",
        "x-justification": "Contenu servi (consigne, note) qui contredit l'exécution canonique. Présent seulement "
                           "pour un écart CONNU ; absent ne vaut pas « aligné ». Tant qu'il subsiste, une preuve "
                           "d'ombre sur dogfood réel n'est pas une exposition exacte pour cette fiche (spec §5, §19).",
    }


def _schema_derived_view(s: dict) -> None:
    dv = s["$defs"]["derived_exercise_view"]
    dv.setdefault("properties", {})
    dv["properties"]["coverage_zones"] = {
        "type": "array", "items": {"$ref": "#/$defs/zone"},
        "x-justification": "Zones à contribution RÉSOLUE (PRIMARY/SECONDARY) : seules utilisables pour la couverture "
                           "et les départages. UNKNOWN n'est jamais lu comme une absence.",
    }
    dv["properties"]["compiler_candidate"] = {
        "type": "boolean",
        "x-justification": "Vrai seulement pour une fiche CANONICAL publiable : un mouvement = un candidat.",
    }


def build_schema(root: Path) -> dict:
    s = copy.deepcopy(_read(root, f"{SOURCES}/schema_arbitrated.json"))
    s["$id"] = "auren/exercise_utility_schema/" + SCHEMA_VERSION
    s["properties"]["schema_version"]["const"] = SCHEMA_VERSION
    _schema_vocabularies(s)
    _schema_equipment(s)
    _schema_identity(s)
    _schema_content_alignment(s)
    _schema_derived_view(s)
    return s


# ---------------------------------------------------------------------------
# Clôture : rulings appliqués aux fiches revues
# ---------------------------------------------------------------------------


class Closure:
    def __init__(self, records: list[dict]):
        self.records = {r["exercise_id"]: r for r in records}
        self.changes: list[str] = []

    def note(self, rid: str, text: str) -> None:
        cur = self.records[rid]["exercise_operational"]["curation"]
        cur["notes"] = (cur.get("notes", "") + "\nclosure: " + text).strip()
        self.changes.append(f"{rid}: {text}")

    def ruled(self, rid: str, ruling: str) -> None:
        cur = self.records[rid]["exercise_operational"]["curation"]
        cur["status"], cur["curated_at"] = "reviewed", TODAY
        self.note(rid, f"operator ruling {ruling} — dispute resolved, status reviewed")

    def science(self, rid: str) -> dict:
        return self.records[rid]["exercise_science"]

    def set_roles(self, rid: str, wanted: dict[str, str]) -> None:
        """Fixe le rôle des zones listées (joint_action_anatomy, EV-71), garde toutes les autres."""
        s = self.science(rid)
        keep = [c for c in s["contributions"] if c["zone"] not in wanted]
        s["contributions"] = [_contrib(z, role) for z, role in wanted.items()] + keep


def _contrib(zone: str, role: str) -> dict:
    return {"zone": zone, "role": role, "role_basis": "joint_action_anatomy", "evidence_refs": ["EV-71"]}


AB_WHEEL_EXECUTION = ("Roulette à genoux : flexion d'épaule contrôlée pendant le déroulé ; bassin et tronc "
                      "tenus contre l'extension lombaire, sans hyperextension lombaire volontaire ; retour sans "
                      "transformer volontairement le mouvement en flexion de hanche dominante.")


def rule_disputed_cases(c: Closure) -> None:
    """Rulings 1–4 et 12 : les cinq cas contestés."""
    s = c.science("pallof-press-cable")
    c.set_roles("pallof-press-cable", {"abs": "PRIMARY"})
    s.update(loaded_joint_actions=["trunk_anti_rotation"], movement_pattern="trunk_anti_rotation",
             strength_specificity_group="pallof_press_cable")
    c.note("pallof-press-cable", "abs PRIMARY — principal contributor to resisting the imposed rotational moment "
           "(loaded isometric action trunk_anti_rotation); abs = anterolateral abdominal wall. No Pallof hypertrophy "
           "trial is claimed: basis joint_action_anatomy (EV-71). Pattern carry → trunk_anti_rotation.")
    c.ruled("pallof-press-cable", "1")

    for rid in ("roulette-abdominale", "roulette-abdominale-paren-ab-wheel-rollout"):
        c.set_roles(rid, {"abs": "PRIMARY", "lats": "SECONDARY", "hip_flexors": "MINOR"})
        c.science(rid).update(loaded_joint_actions=["trunk_anti_extension", "shoulder_flexion", "shoulder_extension"],
                              movement_pattern="trunk_anti_extension",
                              strength_specificity_group="kneeling_ab_wheel_rollout_bodyweight",
                              canonical_execution=AB_WHEEL_EXECUTION)
        c.note(rid, "canonical movement kneeling_ab_wheel_rollout: abs PRIMARY (resisting lumbar extension, loaded "
               "isometric trunk_anti_extension), lats SECONDARY, hip_flexors MINOR; other zones kept as curated "
               "(honest UNKNOWNs stay UNKNOWN). Acute EMG is consistency evidence only, never role authority.")
        c.ruled(rid, "2")

    s = c.science("y-raise-haltere")
    s["contributions"] = [_contrib("upper_back", "PRIMARY"), _contrib("lateral_delts", "SECONDARY"),
                          _contrib("anterior_delts", "SECONDARY"), _contrib("rear_delts", "MINOR")]
    s.update(loaded_joint_actions=["scapular_upward_rotation", "shoulder_abduction", "shoulder_flexion"],
             movement_pattern="shoulder_abduction",
             strength_specificity_group="prone_incline_y_raise_free_weight_dumbbell",
             canonical_execution="Poitrine en appui sur un banc incliné ; bras levés dans le plan de l'omoplate, "
                                 "en Y, avec un mouvement scapulaire contrôlé.")
    c.note("y-raise-haltere", "re-curated from the canonical prone_incline_y_raise (not from the old name): upper_back "
           "PRIMARY (lower trapezius drives the loaded scapular upward rotation with the chest supported), lateral and "
           "anterior delts SECONDARY (elevation in the scapular plane), rear_delts MINOR. No generic standing or cable "
           "Y-raise is inferred.")
    c.ruled("y-raise-haltere", "3")

    c.set_roles("rowing-chest-supported", {"upper_back": "PRIMARY", "lats": "SECONDARY", "rear_delts": "SECONDARY"})
    c.note("rowing-chest-supported", "generic variant, neither lat- nor rear-delt-biased: upper_back PRIMARY, lats and "
           "rear_delts SECONDARY. A lat-biased or high-elbow rear-delt variant must be a distinct exercise.")
    c.ruled("rowing-chest-supported", "4")

    c.science("tirage-front-cable-paren-prise-large").update(
        loaded_joint_actions=["shoulder_abduction", "scapular_elevation", "scapular_upward_rotation", "elbow_flexion"],
        movement_pattern="shoulder_abduction")
    c.note("tirage-front-cable-paren-prise-large", "upright-row family (notes: toward chin, elbows high), lateral_delts "
           "PRIMARY; remaining contributions re-derived from the loaded actions (upper_back SECONDARY via scapular "
           "elevation/upward rotation, biceps SECONDARY via elbow flexion, anterior_delts MINOR). Not front-delt work "
           "from the old French label.")


def _remap_pattern(c: Closure, rid: str) -> None:
    s = c.science(rid)
    acts = s["loaded_joint_actions"]
    if s["movement_pattern"] == "horizontal_push" and "shoulder_horizontal_adduction" in acts \
            and "elbow_extension" not in acts:
        s["movement_pattern"] = "chest_fly"
        c.note(rid, "pattern horizontal_push → chest_fly (horizontal adduction without elbow extension)")
    if rid.startswith("shrugs") and s["movement_pattern"] != "shrug":
        s["movement_pattern"] = "shrug"
        c.note(rid, "pattern → shrug (scapular elevation)")
    if ("pullover" in rid or "straight-arm-pulldown" in rid) and s["movement_pattern"] != "pullover":
        s["movement_pattern"] = "pullover"
        c.note(rid, "pattern → pullover (shoulder extension from overhead, elbows fixed)")


def _add_scapular_actions(c: Closure, rid: str) -> None:
    s = c.science(rid)
    acts = s["loaded_joint_actions"]
    upper_back = {x["zone"]: x["role"] for x in s["contributions"]}.get("upper_back")
    if s["movement_pattern"] in ("vertical_pull", "pullover") and upper_back == "SECONDARY" \
            and "scapular_downward_rotation" not in acts:
        acts.append("scapular_downward_rotation")
        c.note(rid, "loaded action + scapular_downward_rotation (the upper_back SECONDARY role rests on it)")
    if ("shoulder_abduction" in acts or s["movement_pattern"] == "vertical_push") \
            and upper_back in ("PRIMARY", "SECONDARY") and "scapular_upward_rotation" not in acts:
        acts.append("scapular_upward_rotation")
        c.note(rid, "loaded action + scapular_upward_rotation (the upper_back role rests on it)")


def rule_vocabulary(c: Closure) -> None:
    """Ruling 7 : plus aucun exercice rangé dans le pattern le plus proche."""
    for rid in c.records:
        _remap_pattern(c, rid)
        _add_scapular_actions(c, rid)


def _rename_strength_group(c: Closure, rid: str, mode: str) -> None:
    """Ruling 8 : un groupe de force n'affirme pas le mécanisme que le mode ne revendique plus."""
    s = c.science(rid)
    g = s["strength_specificity_group"]
    for claimed in ("machine_selectorized", "machine_plate", "bodyweight"):
        if g.endswith("_" + claimed) and mode != claimed:
            s["strength_specificity_group"] = g.removesuffix(claimed) + mode
            c.note(rid, f"strength_specificity_group {g} → {s['strength_specificity_group']}")
            return


def rule_equipment(c: Closure, patch: dict) -> None:
    """Rulings 5, 6, 8 : exigences dans le langage des capacités TRAIN A."""
    for rid, r in c.records.items():
        p = patch[rid]
        op = r["exercise_operational"]
        op.pop("equipment_required", None)
        # UNKNOWN ne porte aucune capacité : c'est le statut, pas la liste vide, qui dit « inconnu »
        op["equipment_requirements"] = p["equipment_requirements"] or []
        op["equipment_requirement_status"] = p["equipment_requirement_status"]
        if op["equipment_mode"] != p["equipment_mode"]:
            c.note(rid, f"equipment_mode {op['equipment_mode']} → {p['equipment_mode']}")
        op["equipment_mode"] = p["equipment_mode"]
        c.note(rid, f"equipment ({p['basis']}): {p['note']}")
        _rename_strength_group(c, rid, p["equipment_mode"])
    y = c.records["y-raise-haltere"]["exercise_operational"]
    y["equipment_requirements"], y["equipment_requirement_status"] = ["dumbbells", "incline_bench_support"], "RESOLVED"
    c.note("y-raise-haltere", "equipment set from the canonical execution: dumbbells + incline_bench_support")


def _identity_block(m: dict) -> dict:
    block = {k: m[k] for k in ("scientific_identity_id", "identity_relation", "alias_of", "group_classification")}
    if m["identity_relation"] == "CANONICAL":
        block["canonical_display_name"] = m["canonical_display_name"]
    else:
        block["merge_basis"] = "source_facts"
    return block


#: rulings d'identité finaux (G08–G31) et décisions déléguées : fiche canonique, identité, affichage,
#: alias fusionnés PAR DÉFINITION OPÉRATEUR, exécution canonique, exigence quand la définition la fixe
FINAL_IDENTITY_RULINGS = [
    {"ruling": "G08", "canonical": "triceps-pushdown-corde", "identity": "cable_rope_triceps_pushdown",
     "display": "Triceps pushdown corde", "members": ["triceps-extension-poulie-haute-paren-corde"],
     "execution": "Poulie haute, corde ; bras le long du buste ; extension des coudes vers le bas."},
    {"ruling": "G12", "canonical": "curl-poulie-basse-paren-barre", "identity": "low_cable_straight_bar_curl",
     "display": "Curl poulie basse (barre)", "members": ["curl-poulie-basse", "curl-cable-basse"],
     "execution": "Bilatéral, prise en supination, poulie basse, barre droite.",
     "requirements": ["cable_anchor_low", BAR]},
    {"ruling": "G14", "canonical": "curl-marteau-cable-paren-corde", "identity": "cable_rope_hammer_curl",
     "display": "Curl marteau câble (corde)", "members": ["curl-prise-neutre-cable"],
     "execution": "Poulie basse, corde, prise neutre (marteau).", "requirements": ["cable_anchor_low", ROPE]},
    {"ruling": "G17", "canonical": "tirage-poulie-haute-prise-neutre", "identity": "neutral_grip_lat_pulldown",
     "display": "Tirage poulie haute prise neutre", "members": ["lat-pulldown-prise-neutre"],
     "execution": "Tirage vertical devant, poignée parallèle en prise neutre, écartement proche de la largeur "
                  "d'épaules (neutre serrée).",
     "requirements": ["pulldown_seated_station", "cable_attachment_neutral_grip"]},
    {"ruling": "G21/G22", "canonical": "pullover-cable-paren-bras-tendus-poulie-haute",
     "identity": "straight_arm_cable_pullover", "display": "Pullover câble bras tendus (poulie haute)",
     "members": ["pullover-cable-paren-bras-tendus", "straight-arm-pulldown-cable"],
     "execution": "Poulie haute ; bras quasi tendus, coudes souples ; extension d'épaule chargée. Corde ou barre "
                  "droite : alternatives opérationnelles du même mouvement.",
     "requirements": ["cable_anchor_high", {"any_of": [ROPE, BAR]}]},
    {"ruling": "G24", "canonical": "rowing-chest-supported", "identity": "chest_supported_row",
     "display": "Rowing chest-supported", "members": ["rowing-machine-chest-supported"],
     "execution": "Poitrine en appui continu ; coudes à environ 30–45° du buste ; tirer vers le bas du sternum / "
                  "le haut de l'abdomen."},
    {"ruling": "G27", "canonical": "tirage-front-cable-paren-prise-large", "identity": "wide_grip_cable_upright_row",
     "display": "Tirage menton câble — prise large", "members": ["upright-row-cable"],
     "execution": "Mains nettement plus larges que les épaules ; câble tiré vers le haut de la poitrine / le menton ; "
                  "coudes qui montent haut."},
    {"ruling": "G28", "canonical": "leg-press-paren-pieds-bas", "identity": "leg_press_low_feet",
     "display": "Presse à cuisses (pieds bas)", "members": ["leg-press-paren-pieds-bas-serres"],
     "execution": "Pieds bas sur la plateforme ; écartement environ largeur de hanches, choisi confortable ; "
                  "rotation des pieds neutre et confortable."},
    {"ruling": "G30", "canonical": "releve-de-jambes-suspendu", "identity": "hanging_straight_leg_raise",
     "display": "Relevé de jambes suspendu (jambes tendues)", "members": [], "classification": "LEGITIMATE_VARIANT",
     "execution": "Suspendu à un appui au-dessus de la tête ; genoux tendus ou à peine déverrouillés ; jambes "
                  "montées avec contrôle lombo-pelvien ; rétroversion du bassin permise, encouragée en haut."},
    {"ruling": "G30", "canonical": "hanging-knee-raise", "identity": "hanging_bent_knee_raise",
     "display": "Relevé de genoux suspendu", "members": [], "classification": "LEGITIMATE_VARIANT",
     "execution": "Suspendu à un appui au-dessus de la tête ; genoux fléchis montés vers la poitrine."},
    {"ruling": "G31", "canonical": "rowing-haltere-un-bras-paren-banc",
     "identity": "bench_supported_one_arm_dumbbell_row", "display": "Rowing haltère un bras (appui banc)",
     "members": ["rowing-haltere-un-bras"],
     "execution": "Un bras, haltère ; main opposée en appui ; buste stable soutenu par le banc ; tirer vers la "
                  "hanche / le bas des côtes.",
     "requirements": ["dumbbells", "flat_bench_support"]},
    {"ruling": "delegated: preacher curl", "canonical": "preacher-curl", "identity": "machine_preacher_curl",
     "display": "Preacher curl machine", "members": [],
     "execution": "Curl au pupitre sur machine dédiée (fonction machine « curl pupitre ») ; une variante pupitre "
                  "charges libres ou câble est une autre identité opérationnelle.",
     "requirements": ["machine_preacher_curl"]},
    {"ruling": "delegated: dumbbell hip thrust", "canonical": "hip-thrust-halteres", "identity": "dumbbell_hip_thrust",
     "display": "Hip thrust haltères", "members": [],
     "execution": "Haut du dos en appui sur un banc plat, haltère sur les hanches ; extension de hanche. Ce n'est "
                  "pas un pont fessier au sol.",
     "requirements": ["dumbbells", "flat_bench_support"]},
    {"ruling": "delegated: unilateral vertical cable pull", "canonical": "tirage-vertical-unilateral-cable",
     "identity": "unilateral_cable_pulldown", "display": "Tirage vertical unilatéral câble", "members": [],
     "execution": "Tirage vertical à un bras, poignée simple (poignée D) ; coude tiré vers la hanche.",
     "requirements": ["pulldown_seated_station", "cable_attachment_single_handle"]},
    {"ruling": "delegated: face pull", "canonical": "face-pull-cable-paren-corde", "identity": "cable_rope_face_pull",
     "display": "Face pull câble (corde)", "members": ["face-pull-cable"],
     "execution": "Câble à hauteur du visage / des yeux environ ; corde, prise neutre ; tirer vers le visage ; "
                  "rétraction scapulaire avec rotation externe contrôlée.",
     "requirements": ["cable_anchor_adjustable", ROPE]},
    # l'opérateur a statué sur l'ACCESSOIRE, pas sur l'exécution : aucune exécution canonique n'est inventée
    {"ruling": "Sb_SCI_V2_01: close-neutral seated row", "canonical": "rowing-cable-assis-prise-neutre",
     "identity": None, "display": None, "members": [],
     "requirements": ["row_seated_station", CLOSE_NEUTRAL_ROW]},
    {"ruling": "Sb_SCI_V2_01: close-neutral seated row", "canonical": "rowing-cable-assis-prise-serree",
     "identity": None, "display": None, "members": [],
     "requirements": ["row_seated_station", CLOSE_NEUTRAL_ROW]},
]


def _apply_canonical(c: Closure, fr: dict) -> None:
    canon = c.records[fr["canonical"]]
    identity = canon["identity"]
    if fr["identity"] is not None:
        canon["identity"] = {
            "scientific_identity_id": fr["identity"], "identity_relation": "CANONICAL", "alias_of": None,
            "group_classification": fr.get("classification", "EXACT_CANONICAL_DUPLICATE" if fr["members"]
                                           else identity["group_classification"]),
            "canonical_display_name": fr["display"],
        }
    if "execution" in fr:
        canon["exercise_science"]["canonical_execution"] = fr["execution"]
    if "requirements" in fr:
        op = canon["exercise_operational"]
        if op["equipment_requirements"] != fr["requirements"]:
            c.note(fr["canonical"], f"equipment {op['equipment_requirements']} → {fr['requirements']} "
                                    f"(operator ruling {fr['ruling']})")
        op["equipment_requirements"], op["equipment_requirement_status"] = fr["requirements"], "RESOLVED"
    shown = canon["identity"]
    defined = "execution defined" if "execution" in fr else "requirement defined"
    c.note(fr["canonical"], f"operator ruling {fr['ruling']}: canonical {shown['scientific_identity_id']} "
                            f"« {shown['canonical_display_name']} » — {defined}")


def _apply_members(c: Closure, fr: dict) -> None:
    for mid in fr["members"]:
        c.records[mid]["identity"] = {
            "scientific_identity_id": fr["identity"], "identity_relation": "LEGACY_ALIAS", "alias_of": fr["canonical"],
            "group_classification": "EXACT_CANONICAL_DUPLICATE", "merge_basis": "operator_definition",
        }
        c.note(mid, f"operator ruling {fr['ruling']}: legacy alias of {fr['canonical']} by operator definition "
                    "(product definition, not a claim that every historical execution is known)")


def _resolve_alias_chains(c: Closure) -> None:
    """Un alias ne pointe jamais vers un autre alias : chaque chaîne est ramenée à sa racine canonique."""
    for r in c.records.values():
        ident = r["identity"]
        hops = 0
        while ident["identity_relation"] == "LEGACY_ALIAS" \
                and c.records[ident["alias_of"]]["identity"]["identity_relation"] == "LEGACY_ALIAS":
            ident["alias_of"] = c.records[ident["alias_of"]]["identity"]["alias_of"]
            hops += 1
            if hops > 5:
                raise SystemExit(f"alias cycle at {r['exercise_id']}")
        if ident["identity_relation"] == "LEGACY_ALIAS":
            ident["scientific_identity_id"] = c.records[ident["alias_of"]]["identity"]["scientific_identity_id"]


def _align_aliases(c: Closure) -> None:
    """Un alias EST son mouvement canonique : même science, mêmes faits opérationnels ; sa curation reste la sienne."""
    for rid, r in c.records.items():
        ident = r["identity"]
        if ident["identity_relation"] != "LEGACY_ALIAS":
            continue
        canon = c.records[ident["alias_of"]]
        if r["exercise_science"] != canon["exercise_science"]:
            r["exercise_science"] = copy.deepcopy(canon["exercise_science"])
            c.note(rid, f"legacy alias of {ident['alias_of']}: science aligned on the canonical record")
        own = r["exercise_operational"]["curation"]
        canon_op = {k: copy.deepcopy(v) for k, v in canon["exercise_operational"].items() if k != "curation"}
        if {k: v for k, v in r["exercise_operational"].items() if k != "curation"} != canon_op:
            c.note(rid, f"legacy alias of {ident['alias_of']}: operational facts aligned on the canonical record")
        r["exercise_operational"] = {**canon_op, "curation": own}
        c.note(rid, f"legacy alias of {ident['alias_of']} ({ident['merge_basis']})")


def rule_identities(c: Closure, identity_map: dict) -> None:
    """Ruling 10 et rulings d'identité finaux."""
    for rid, r in c.records.items():
        r["identity"] = _identity_block(identity_map[rid])
    row = c.records["rowing-chest-supported"]["identity"]
    row["scientific_identity_id"], row["canonical_display_name"] = "chest_supported_row", "Rowing chest-supported"
    c.note("rowing-chest-supported", "identity chest_supported_row_elbows_open → chest_supported_row (ruling 4: "
           "generic, not rear-delt-biased)")
    for fr in FINAL_IDENTITY_RULINGS:
        _apply_canonical(c, fr)
        _apply_members(c, fr)
    _resolve_alias_chains(c)
    _align_aliases(c)


#: GO BUILD Sb_SCI_V2_01 — contenu servi connu pour contredire l'exécution canonique (spec §5, §19)
CONTENT_MISMATCHES = {
    "releve-de-jambes-suspendu": {
        "served_content": [{"source": "data/reference_split.json — note de gabarit",
                            "text": "Contrôler le balancement, monter les genoux au-dessus des hanches."}],
        "note": "L'exécution canonique est jambes tendues (G30) ; la note servie décrit un relevé de genoux. Tant que "
                "l'écart subsiste, une preuve d'ombre tirée du dogfood ne peut pas être lue comme une exposition "
                "exacte pour cette fiche.",
    },
    "rowing-machine-chest-supported": {
        "served_content": [{"source": "data/machine_atlas.json — consigne d'exécution",
                            "text": "Tirer les coudes vers les hanches, squeeze en fin"}],
        "note": "Identité générique chest_supported_row (G24), coudes à environ 30–45° du buste ; la consigne servie "
                "oriente vers un tirage coudes serrés, biais dorsaux. Aucune identité biaisée n'est créée sur cette "
                "seule phrase ; tant que l'écart subsiste, une preuve d'ombre tirée du dogfood ne peut pas être lue "
                "comme une exposition exacte pour cette fiche.",
    },
}


def rule_content_alignment(c: Closure) -> None:
    for rid, entry in CONTENT_MISMATCHES.items():
        c.records[rid]["content_alignment"] = {"status": "CONTENT_EXECUTION_MISMATCH",
                                               "served_content": entry["served_content"],
                                               "exact_exposure_evidence": False, "note": entry["note"]}
        c.note(rid, "content_alignment CONTENT_EXECUTION_MISMATCH recorded (GO BUILD Sb_SCI_V2_01)")


# ---------------------------------------------------------------------------
# Delta TRAIN A proposé — aucun accessoire déduit
# ---------------------------------------------------------------------------

NO_INFERRED_ACCESSORY = ("Opérateur 2026-10-23 : une station accorde des ancrages, un accessoire accorde sa propre "
                         "capacité. La provenance en prose (« poignées LIVRÉES ») n'est pas une définition de "
                         "capacité de l'objet ; aucun accessoire n'est déduit. L'utilisateur déclare la poignée D "
                         "(cable_d_handle).")


def build_delta(base: dict) -> dict:
    d = copy.deepcopy(base)
    d["delta_version"] = DELTA_VERSION
    dropped = [a for a in d.get("item_capability_additions", [])
               if any(cap.startswith("cable_attachment_") for cap in a["add_capabilities"])]
    d["item_capability_additions"] = [a for a in d.get("item_capability_additions", []) if a not in dropped]
    d.setdefault("not_added", [])
    for a in dropped:
        d["not_added"].append({"what": f"{a['item_id']} + {a['add_capabilities']}", "reason": NO_INFERRED_ACCESSORY})
    d["new_capabilities"]["cable_attachment_neutral_grip"] = (
        "une poignée de tirage à prise neutre (poignées parallèles) à fixer sur une poulie ou une station de tirage")
    d["new_capabilities"][CLOSE_NEUTRAL_ROW] = (
        "une poignée de tirage horizontal à prise neutre serrée (poignée en V) à fixer sur une station de tirage "
        "horizontal. N'est PAS accordée par la station elle-même")
    d["new_items"].append({
        "item_id": "cable_neutral_grip_handle", "label": "Poignée de tirage prise neutre",
        "capabilities": ["cable_attachment_neutral_grip"], "group": "poulies",
        "provenance": f"curation {DELTA_VERSION} — accessoire déclarable séparément (§4 TRAIN A)",
        "reason": "G17 : le tirage vertical prise neutre exige cet accessoire ; une station de tirage générique ne le "
                  "garantit pas. Accordé par aucun autre objet.",
    })
    d["new_items"].append({
        "item_id": "close_neutral_row_handle", "label": "Poignée de rowing prise neutre serrée",
        "capabilities": [CLOSE_NEUTRAL_ROW], "group": "poulies",
        "provenance": f"curation {DELTA_VERSION} — accessoire déclarable séparément (§4 TRAIN A)",
        "reason": "Ruling opérateur Sb_SCI_V2_01 : les rowings câble assis prise neutre et prise serrée exigent cet "
                  "accessoire amovible ; low_row_station ne l'accorde PAS — une station et son accessoire sont deux "
                  "faits physiques distincts tant que le registre ne prouve pas ce lot exact.",
    })
    return d


# ---------------------------------------------------------------------------
# Assemblage
# ---------------------------------------------------------------------------


def _header(root: Path, src_header: dict, schema: dict, base: dict, delta: dict) -> dict:
    policy = _read(root, f"{SCI}/exposure_credit_policy.json")
    return {
        "catalogue_version": CATALOGUE_VERSION,
        "schema_id": schema["$id"],
        "zone_model_version": src_header["zone_model_version"],
        "credit_policy_version": policy["policy_id"],
        "evidence_registry_version": src_header["evidence_registry_version"],
        "substitution_graph_version": src_header["substitution_graph_version"],
        "equipment_registry_base": base.get("base_version"),
        "equipment_registry_delta": delta["delta_version"],
        "source_exercise_ids": src_header["source_exercise_ids"],
        "sources_digest": sources_digest(root),
    }


def build(root: Path = ROOT) -> dict[str, bytes]:
    """Rend les quatre artefacts en octets, sans rien écrire."""
    schema = build_schema(root)
    reviewed = _read(root, f"{SOURCES}/curation_reviewed.json")
    base = _read(root, f"{SOURCES}/train_a_delta_proposal_base.json")
    closure = Closure(copy.deepcopy(reviewed["records"]))
    rule_disputed_cases(closure)
    rule_vocabulary(closure)
    rule_equipment(closure, _read(root, f"{SOURCES}/equipment_patch.json"))
    rule_identities(closure, _read(root, f"{SOURCES}/identity_map.json"))
    rule_content_alignment(closure)
    for r in closure.records.values():
        r["schema_version"] = SCHEMA_VERSION
    delta = build_delta(base)
    catalogue = {"catalogue_header": _header(root, reviewed["catalogue_header"], schema, base, delta),
                 "records": [closure.records[k] for k in sorted(closure.records)]}
    return {SCHEMA: _dump(schema), CATALOGUE: _dump(catalogue), DELTA: _dump(delta),
            CHANGES: ("\n".join(closure.changes) + "\n").encode("utf-8")}


def main(argv: list[str]) -> int:
    outputs = build(ROOT)
    if "--check" in argv:
        drift = [rel for rel, data in outputs.items() if (ROOT / rel).read_bytes() != data]
        for rel in drift:
            print(f"DRIFT {rel} — régénérer avec scripts/generate_sci_catalogue.py")
        return 1 if drift else 0
    for rel, data in outputs.items():
        (ROOT / rel).write_bytes(data)
    print(f"{len(outputs)} artefacts écrits · sources {sources_digest(ROOT)[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
