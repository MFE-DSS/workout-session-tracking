"""Tuile Home « État d'entraînement » (Sb_RECOVERY_HOME_CONSUMER_01).

**Premier consommateur de la chaîne P0.4.** Rend visible, pour la première fois,
ce que `TrainingState` et `recovery_explainer` savent déjà — sans rien décider.

Chaîne de données, une seule source de vérité :

```
DB → build_training_state → build_proactive_explanation → cette vue-modèle → Home
```

Ce module **ne calcule rien**. Il ne recalcule ni fatigue, ni récupération de
zone ; il ne parse aucun `basis` ; il ne réécrit aucune phrase. Il **sélectionne**
au plus trois `ExplanationItem` déjà produits et les aplatit pour un gabarit.
Un test échoue si une table de copie de récupération réapparaît ici.

**Il ne change aucune décision d'entraînement.** La recommandation, son
classement et son contenu sont produits ailleurs et ne lisent pas ce module —
un test compare la décision avant/après branchement sur la même entrée persistée.

**Pourquoi des zones nommées et non le roll-up macro.** Le roll-up par axe
(OQ-5) semblait la granularité évidente pour un bloc compact. **Mesuré, il ne
l'est pas** : `worst_zone_rollup` dégrade la confiance d'un axe dès qu'une de
ses zones est inconnue, et comme un axe compte deux ou trois zones, il suffit
d'une seule non entraînée pour que l'axe entier tombe en `Confidence.NONE`.
Sur un compte réaliste les axes sont donc presque toujours muets — un bloc
alimenté par eux n'afficherait rien. C'est un comportement **correct** de la
tranche 4, pas un défaut : un axe partiellement inconnu ne peut pas être résumé
avec confiance.

La tuile lit donc les **estimations de zone**, plafonnées à deux. La mission
interdit d'étaler les onze zones, pas d'en nommer une ou deux : « une ou deux
observations de récupération réellement pertinentes » est exactement la classe
sémantique demandée.

**Nommage — trois surfaces d'état coexistent sur la Home, et c'est délibéré :**

| Surface | Nature | Origine |
|---|---|---|
| « État du jour » | ce que l'utilisateur **déclare** (1–5, 1×/jour) | `ReadinessEntry`, widget existant |
| « disponibilité » (0–100) | KPI **hérité** | `behavioral.readiness_score` (OQ-1) |
| « État d'entraînement » | ce qu'AUREN **infère** des séances enregistrées | chaîne P0.4 |

Le libellé retenu évite un **troisième** emploi ambigu de « readiness » ou
« récupération » (spec §1). Le KPI hérité n'est **ni retiré, ni renommé** dans
cette tranche : sa dépréciation est une décision explicite ultérieure (OQ-1).
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.services.recovery_explainer import (
    build_proactive_explanation,
    recovery_rank_key,
)
from app.services.training_state import build_training_state

#: Libellé de la tuile. Distinct de « État du jour » (déclaré) et de
#: « disponibilité » (KPI hérité 0–100).
HOME_TILE_LABEL = "État d'entraînement"

#: Sous-titre de cadrage. Ce n'est **pas** une phrase de récupération : il dit
#: d'où vient le bloc, ce qui est précisément ce qui le distingue du widget
#: déclaratif voisin.
HOME_TILE_CAPTION = "Estimé à partir de tes séances enregistrées."

#: Plafond de densité (mission : « up to 2–3 »). La Home n'est pas un tableau
#: de bord ; au-delà, le bloc cesse d'être calme.
HOME_MAX_ITEMS = 3

#: Plafond spécifique aux zones : deux au plus, jamais les onze.
HOME_MAX_ZONE_ITEMS = 2


def build_home_training_state(
    db: Session, user_id: int, *, now: datetime
) -> dict[str, Any]:
    """Vue-modèle de la tuile. Lecture seule, déterministe, sans horloge propre.

    **Une seule** construction de `TrainingState` par appel, donc par requête
    Home : `build_home_payload` est le seul appelant. Aucune requête par zone ni
    par item n'est émise ici — la sélection travaille sur des objets déjà en
    mémoire.
    """
    state = build_training_state(db, user_id, now=now)
    explanation = build_proactive_explanation(state)

    entries = _select_items(explanation)
    estimated = any(entry["is_estimate"] for entry in entries)
    return {
        "available": True,
        "label": HOME_TILE_LABEL,
        "caption": HOME_TILE_CAPTION,
        "insufficient": not estimated,
        "message": None if estimated else _insufficient_message(explanation),
        "entries": entries,
    }


def _insufficient_message(explanation) -> str | None:
    """L'état « on ne sait pas » — **un seul** message, jamais onze.

    Le texte vient de l'explainer, pas d'ici : la décision produit de P0.4
    (silence sur la physiologie, explicite sur la donnée manquante) garde un
    seul point de définition.

    Il accompagne le **contexte** plutôt que de le remplacer. Une séance à la
    fois musculation et cardio fait tomber la confiance de la zone à `NONE`
    (le cardio dégrade, tranche 4) : sans estimation, mais avec une exposition
    cardio bien réelle et peut-être un état déclaré du jour. Taire ce contexte
    parce que l'estimation manque perdrait de l'information **honnête** ; ce
    qui doit rester tu, c'est l'interprétation physiologique, pas le fait
    enregistré.
    """
    notices = explanation.data_state_items
    return notices[0].message if notices else None


def _select_items(explanation) -> list[dict[str, Any]]:
    """Au plus `HOME_MAX_ITEMS`, dans un ordre stable et justifiable.

    1. le contexte **déclaré** (readiness), s'il existe — ce que l'utilisateur a
       dit passe avant ce que le système infère ;
    2. les zones les plus contraintes, via `recovery_rank_key` — le tri
       d'**affichage** déjà fourni par la tranche 4, **jamais** un choix
       d'entraînement ;
    3. le contexte cardio, s'il existe.

    Le budget est calculé plutôt que codé en dur : les deux contextes prennent
    leur place d'abord, les zones remplissent le reste, et **au moins une** zone
    est toujours montrée quand une estimation existe — sinon la tuile pourrait
    n'afficher que du contexte et taire la seule chose qu'elle estime.

    L'invite de saisie (`data_prompt`) est **délibérément absente** : le widget
    « État du jour · à remplir » de la Home porte déjà ce CTA, et le dupliquer
    créerait la double hiérarchie d'appel à l'action que la mission interdit.
    """
    readiness = (
        [_flatten(explanation.readiness_item)]
        if explanation.readiness_item is not None else []
    )
    cardio = (
        [_flatten(explanation.cardio_item)]
        if explanation.cardio_item is not None else []
    )

    budget = HOME_MAX_ITEMS - len(readiness) - len(cardio)
    room = min(HOME_MAX_ZONE_ITEMS, max(1, budget))
    ranked = sorted(explanation.zone_items, key=recovery_rank_key)
    zones = [_flatten(item) for item in ranked[:room]]

    return [*readiness, *zones, *cardio][:HOME_MAX_ITEMS]


def _flatten(item) -> dict[str, Any]:
    """`ExplanationItem` → dict de gabarit. **Aucune phrase n'est réécrite.**"""
    return {
        "kind": item.kind,
        "subject_label": item.subject_label,
        "message": item.message,
        "confidence_label": item.confidence_label,
        "is_estimate": item.is_estimate,
        "reasons": list(item.reasons),
    }


__all__ = [
    "HOME_MAX_ITEMS",
    "HOME_MAX_ZONE_ITEMS",
    "HOME_TILE_CAPTION",
    "HOME_TILE_LABEL",
    "build_home_training_state",
]
