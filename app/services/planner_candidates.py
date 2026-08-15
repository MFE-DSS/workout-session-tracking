"""Pool de candidats du PLANIFICATEUR (Sb_CORE_EXERCISE_PROPERTIES_01).

Tranche 2/4 du train `AUREN_EFFECTIVE_VOLUME_COMPLETION_01`.

## Pourquoi un registre séparé, et pas cinq lignes dans `exercise_properties.json`

`exercise_properties.json` se décrit lui-même comme les « propriétés enrichies
par exercice **pour la substitution heuristique** ». Son contrat, épinglé par
`test_exercise_properties_loads_and_validates`, exige que **chaque** entrée
déclare un `equipment_family` — parce que la proximité de substitution le score
et que le tiroir N1/N2/N3 s'en sert.

Or **aucune source du dépôt ne documente le matériel des exercices de tronc** :
ni l'EKB, ni `machine_slug`/`machine_family` dans `reference_split`, ni le
registre lui-même. Les y ajouter imposait donc l'un des deux :

- **inventer** un `equipment_family` — interdit, et doublement faux ici puisque
  le vocabulaire existant (`barbell`/`bodyweight`/`cable`/`dumbbell`/`machine`/
  `smith`) n'a pas de famille pour une roulette abdominale ;
- **relâcher le contrat** du registre de substitution pour tout le dépôt.

La première tentative les a écrits dans ce fichier ; le **full sweep** a
immédiatement fait tomber le contrat, plus la cohérence EKB
(`coverage_status`) et l'empreinte du programme morpho. C'est le signal utile :
ce n'était pas le bon endroit.

**Un exercice de tronc n'est pas un candidat de substitution.** Il est
inatteignable par N1 (aucune liste curée ne le cite), par N2 (même
`pattern_motor` — aucun exercice existant n'a `core`), par N3 (même
`zone_primary` — idem) et par les passerelles (`core` n'y figure pas). Le
placer dans le registre de substitution était une **erreur de catégorie** que
le contrat a révélée.

D'où ce registre distinct : le planificateur compose sa propre vue, le registre
de substitution reste **inchangé au bit près**, et l'isolement est garanti *par
construction* plutôt que démontré après coup.

## Ce que les entrées déclarent, et ce qu'elles taisent

`pattern_motor: "core"` — un `PatternMotor` **déjà valide** et jusqu'ici
inutilisé, légitime ici parce que ces exercices sont canoniquement classés
`core` par le contrat de zones et que la correspondance est univoque.

`zone_primary: "core"` — la macro-région que l'EKB porte déjà
(`_zone_macro_vocab`), et non un axe radar fabriqué.

**Pas de `equipment_family`.** Conséquence assumée et correcte : sous
restriction de matériel, le filtre écarte ces candidats et la zone sort en
`UNMET_EQUIPMENT`. Ce qui manque est un matériel **documenté**, pas un exercice.

Chaque entrée cite sa preuve : présence dans un template curé de
`reference_split.json` — le catalogue les programme déjà, avec un `set_scheme`
réel.
"""
from __future__ import annotations

from app.services.substitution import load_exercise_properties

PLANNER_CANDIDATE_REGISTRY_VERSION = "planner-candidates-v1"

#: Candidats de tronc, avec la preuve qui les autorise.
#:
#: Critère d'entrée, appliqué sans exception : classé `core` par le contrat
#: canonique de zones **ET** programmé dans au moins un template curé de
#: `reference_split.json`.
#:
#: Trois exercices canoniques en sont **absents** — `Decline crunch`,
#: `Hanging knee raise`, `Machine crunch` : aucun template ne les programme et
#: l'EKB ne leur attribue aucune zone (`confidence: todo`). Rien ne dit comment
#: ils se programment ; leur inventer un motif serait de la fabrication.
CORE_CANDIDATES: dict[str, dict] = {
    # template `legs-b`, `lower-posterior-bias`, `liss-abs` — 3x 12-15
    "Crunch câble à genoux": {
        "pattern_motor": "core", "zone_primary": "core", "chain": "isolation",
    },
    # template `liss-abs` — 3x 12-15
    "Pallof press câble": {
        "pattern_motor": "core", "zone_primary": "core", "chain": "isolation",
    },
    # template `liss-abs` — 3x 10-15 ; zone `core` via KNOWN_MAPPING_CORRECTIONS
    "Relevé de jambes suspendu": {
        "pattern_motor": "core", "zone_primary": "core", "chain": "isolation",
    },
    # templates `legs-a`, `lower-quad-bias` — 3x 10-15
    "Roulette abdominale": {
        "pattern_motor": "core", "zone_primary": "core", "chain": "isolation",
    },
    # template `liss-abs` — 3x 10-15
    "Roulette abdominale (ab wheel rollout)": {
        "pattern_motor": "core", "zone_primary": "core", "chain": "isolation",
    },
}

#: Exercices canoniquement `core` mais **volontairement non programmables**,
#: nommés pour que la lacune reste lisible plutôt que silencieuse.
CORE_WITHOUT_EVIDENCE: tuple[str, ...] = (
    "Decline crunch",
    "Hanging knee raise",
    "Machine crunch",
)


def planner_candidate_pool() -> dict[str, dict]:
    """Registre de substitution **+** candidats du planificateur. Dict frais.

    Le registre de substitution est lu tel quel et jamais muté : la copie
    protège son cache, et l'ordre garantit qu'une entrée de tronc ne peut pas
    écraser une entrée existante.
    """
    pool = dict(load_exercise_properties())
    for name, props in CORE_CANDIDATES.items():
        pool.setdefault(name, dict(props))
    return pool


__all__ = [
    "CORE_CANDIDATES",
    "CORE_WITHOUT_EVIDENCE",
    "PLANNER_CANDIDATE_REGISTRY_VERSION",
    "planner_candidate_pool",
]
