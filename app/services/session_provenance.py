"""`UI-CP8D` — la PROVENANCE d'une séance terminée.

⚠ CETTE DONNÉE EXISTE DEPUIS `REC-CP4` ET N'EST RENDUE NULLE PART.

`recommendation_episodes` porte, pour chaque contexte de décision, le conseil
donné (`proposed_top_slug`, `proposed_alt_slugs`), son issue (`outcome`) et la
séance qui l'a résolu (`session_id`). Mesuré en base : l'épisode de la séance
8 dit `ACCEPTED_TOP · liss-abs`. Aucune surface du produit ne le lit.

C'est la boucle que le programme construit depuis `REC-CP1` — recommander,
exécuter, apprendre — et il lui manquait sa dernière moitié : **dire à
l'utilisateur ce qui avait été conseillé, et ce qu'il en a fait**. Sans ça,
`JOURNEY C` n'a aucune continuité causale : on voit ce qu'on a fait, jamais
pourquoi on l'a fait.

⚠ AUCUNE ÉCRITURE ICI. Ce module LIT. `§4` de l'arbitrage interdit toute
écriture sur un GET, et la porte d'écriture reste `enregistrer_episode`,
appelée après le commit de création de séance.
"""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.recommendation_episode import (
    ACCEPTED_ALTERNATIVE,
    ACCEPTED_TOP,
    CHOSE_OTHER,
    EXPLICITLY_DISMISSED,
    RecommendationEpisode,
)

#: Ce que chaque issue raconte, du point de vue de l'utilisateur qui relit sa
#: séance. Les clés sont le vocabulaire versionné du modèle ; les phrases sont
#: à lui.
#:
#: ⚠ `UNRESOLVED` n'est PAS dans cette table, et c'est le contrat du modèle :
#: l'absence d'épisode est l'absence de ligne, jamais une valeur. Une séance
#: sans provenance est une séance démarrée hors d'un conseil — on le dit,
#: on ne l'invente pas.
RECITS = {
    ACCEPTED_TOP: "AUREN recommandait cette séance. Tu l'as suivie.",
    ACCEPTED_ALTERNATIVE: (
        "AUREN recommandait {top}. Tu as pris une de ses alternatives."
    ),
    CHOSE_OTHER: "AUREN recommandait {top}. Tu as fait autre chose.",
    EXPLICITLY_DISMISSED: "AUREN recommandait {top}. Tu as écarté le conseil.",
}


@dataclass(frozen=True)
class Provenance:
    """D'où vient cette séance — conseil suivi, écarté, ou aucun conseil."""

    issue: str
    recit: str
    #: Le gabarit conseillé en tête, quand il diffère de ce qui a été fait.
    conseille: str | None
    politique: str


def provenance_de(db: Session, session) -> Provenance | None:
    """La provenance d'une séance terminée, ou `None` si elle n'en a pas.

    `None` est un état LÉGITIME et fréquent : toutes les séances
    antérieures à `REC-CP4` en sont dépourvues, et une séance démarrée
    hors d'un conseil n'en aura jamais. On ne fabrique rien.
    """
    episode = db.execute(
        select(RecommendationEpisode)
        .where(RecommendationEpisode.session_id == session.id)
    ).scalar_one_or_none()
    if episode is None or episode.outcome is None:
        return None

    modele = RECITS.get(episode.outcome)
    if modele is None:
        return None

    conseille = episode.proposed_top_slug
    # Le nom du gabarit conseillé n'est utile que s'il DIFFÈRE de ce qui a
    # été fait — sinon la phrase se répéterait à elle-même.
    montre = conseille if conseille != session.template_slug_snapshot else None
    return Provenance(
        issue=episode.outcome,
        recit=modele.format(top=_nom_de(db, conseille) or "une autre séance"),
        conseille=montre,
        politique=episode.policy_version or "",
    )


def _nom_de(db: Session, slug: str | None) -> str | None:
    if not slug:
        return None
    from app.models.catalog import WorkoutTemplate

    return db.execute(
        select(WorkoutTemplate.name).where(WorkoutTemplate.slug == slug)
    ).scalar_one_or_none()
