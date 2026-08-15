"""Read-only EKB exercise catalog for the draft editor picker (WIZARD_05).

Projects the canonical Exercise Knowledge Base JSON (`data/exercise_knowledge_
base.json`, EKB_02, 103 entrées) into two template-ready, side-effect-free vues :
- `picker_options()` : la liste triée des noms canoniques + métadonnées
  d'affichage, qui alimente un `<datalist>` no-JS pour que la saisie manuelle
  s'aligne sur les noms reconnus par l'EKB (donc par le scoring — le moteur
  résout l'EKB par `exercise_name`) ;
- `enrich(name)` : les champs EKB dénormalisés pour un match canonique EXACT,
  destinés à peupler les colonnes déjà existantes de `UserProgramExercise`.

Frontières dures :
- **LECTURE SEULE** du JSON (jamais d'écriture) ; aucun ORM, aucune session DB,
  aucun HTTP, aucune mutation de modèle. EKB_04 (seed DB) reste **différé** — ce
  service lit le JSON canonique, **pas une table**.
- **Déterministe, sans effet de bord** ; le catalogue parsé est mis en cache
  (`functools.lru_cache`) ; les vues renvoient des **copies fraîches**, jamais
  une référence mutable interne du cache (un appelant ne peut pas muter l'état
  caché).
- **Match EXACT V1** : ni casse, ni accents, ni espaces, ni aliases (`_aliases`)
  ne sont normalisés — un nom altéré retombe en texte libre `manual` (fallback
  **non bloquant**), sans dégât.
- **N'importe ni ne modifie le moteur de score** (`program_quality_engine`) : ce
  lecteur est autonome pour garder la surface isolée.
"""
from __future__ import annotations

import json
from functools import lru_cache

from app.config import BASE_DIR

_EKB_PATH = BASE_DIR / "data" / "exercise_knowledge_base.json"

# Champs dénormalisés recopiés sur un exercice matché (miroir des colonnes
# nullable de `UserProgramExercise` que `replace_draft_tree` persiste déjà).
_ENRICH_FIELDS = ("variant_key", "variant_group", "equipment_family", "movement_pattern")
# Métadonnées d'affichage du picker (peuvent être null — les gaps restent honnêtes).
_OPTION_META_FIELDS = ("zone_primary", "movement_pattern", "equipment_family")


@lru_cache(maxsize=1)
def _entries() -> dict[str, dict]:
    """Parse le JSON EKB canonique une seule fois (indexé par nom canonique).

    Lecture seule ; la valeur cachée est traitée comme immuable — les appelants
    ne la reçoivent jamais directement (les vues construisent des copies)."""
    with _EKB_PATH.open(encoding="utf-8") as fh:
        payload = json.load(fh)
    return payload.get("exercises", {})


def detailed_zone_regions() -> dict[str, str]:
    """Detailed zone -> macro region, as the EKB curates it. Fresh dict, no cache leak.

    The EKB is the only curated source that carries **both** granularities on the
    same row (`zone_primary` detailed, `zone_macro` macro), which makes it the
    place to ask "which macro region does this detailed zone belong to" for the
    zones the radar does not cover — `core` in particular.

    Entries whose curation is still a gap (either field `null`) contribute
    nothing: a missing value is left missing rather than guessed.
    """
    out: dict[str, str] = {}
    for entry in _entries().values():
        zone, macro = entry.get("zone_primary"), entry.get("zone_macro")
        if zone and macro:
            out.setdefault(zone, macro)
    return out


def picker_options() -> list[dict]:
    """Toutes les entrées EKB, triées par nom, en dicts prêts pour le template.

    Shape exact : `{name, zone_primary, movement_pattern, equipment_family}`. Les
    métadonnées peuvent être `None` (les gaps ne sont jamais masqués). Renvoie
    des dicts **frais** — le cache n'est jamais exposé.
    """
    return [
        {"name": name, **{field: entry.get(field) for field in _OPTION_META_FIELDS}}
        for name, entry in sorted(_entries().items(), key=lambda kv: kv[0])
    ]


def enrich(name: str) -> dict:
    """Champs EKB dénormalisés pour un match canonique **EXACT**, sinon `{}`.

    Aucune normalisation (casse / accents / espaces / aliases) en V1 — un nom
    altéré renvoie `{}` pour que l'appelant le conserve en texte libre `manual`.
    Renvoie un dict **frais** ; jamais une référence dans le cache.
    """
    entry = _entries().get(name)
    if entry is None:
        return {}
    return {field: entry.get(field) for field in _ENRICH_FIELDS}
