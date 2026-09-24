"""`REC-CP4` — la mémoire du conseil.

CE QU'ELLE CORRIGE
--------------------
`REC-CP1..CP3` a mesuré que le moteur n'est pas « bloqué » :

    conseil SUIVI    → il tourne, six gabarits sur dix décisions
    conseil DÉCLINÉ  → il répète le même conseil indéfiniment

Le défaut est donc une **mémoire d'interaction**, pas un poids de score.

CE QU'ELLE N'EST PAS
----------------------
**Pas une pénalité de score.** Aucun `score -= X` nulle part. La mémoire est un
**étage de décision sémantique**, inséré dans la précédence :

    éligibilité → contraintes courantes → besoin longitudinal
    → MÉMOIRE DU CONSEIL → justification de répétition
    → modalité → départage par récence

**Pas une préférence.** Écarter le LISS aujourd'hui ne dit pas que
l'utilisateur n'aime pas le cardio ; choisir `pull-b` plutôt que le LISS ne dit
pas que le tirage est préféré. L'observation appartient à **cette décision,
dans ce contexte**. Une préférence durable exigerait des preuves répétées et
elle est hors périmètre.

**Pas une TTL.** Un refus ne « dure pas 24 h ». Il vaut tant que le CONTEXTE
MATÉRIEL de la décision reste équivalent, et cesse dès qu'il change.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.recommendation_episode import (
    ACCEPTED_ALTERNATIVE,
    ACCEPTED_TOP,
    CHOSE_OTHER,
    RecommendationEpisode,
)
from app.services.recommendation import Signals

#: Les politiques que le banc sait rejouer.
POLITIQUES = ("v2", "v3")

# ═══ CE QUI SERT EN PRODUCTION — UN SEUL ENDROIT, ET IL EST DÉCLARÉ ═══
#
# ⚠ Ces deux constantes sont la porte de promotion du `§13`, rendue explicite.
# Les changer EST le basculement de politique ; le faire ailleurs, ou par
# effet de bord, serait le « basculement silencieux » que le `§12` interdit.
#
# Une garde épingle ces valeurs contre les conclusions du rapport de tranche :
# elles ne peuvent pas dériver sans que quelqu'un vienne l'écrire.
POLITIQUE_SERVIE = "v2"
MEMOIRE_SERVIE = True

#: Au plus deux alternatives sont proposées ; on borne l'écriture en dur pour
#: qu'un changement d'affichage ne fasse pas déborder la colonne.
MAX_ALTERNATIVES = 4


# ═══════════════ 1. L'EMPREINTE DE CONTEXTE ═══════════════
#
# ⚠ ELLE NE DÉRIVE QUE DES ENTRÉES QUE LE MOTEUR CONSOMME.
#
# Y mettre autre chose — une préférence que le moteur ne lit pas, un état de
# page, l'heure — reviendrait à inventer une dépendance et à périmer des refus
# pour des raisons étrangères à la décision.
#
# ⚠ ET ELLE EST QUANTIFIÉE.
#
# `Signals` porte des valeurs continues : `availability_by_zone` bouge à chaque
# seconde, `fatigue_score` est un flottant. Les prendre brutes donnerait une
# empreinte différente à chaque rendu — donc un refus périmé avant même d'avoir
# servi, et la mémoire ne mémoriserait rien.
#
# On quantifie donc en BANDES, en réutilisant les seuils que `V3` emploie déjà
# pour la récupération. Aucun seuil nouveau n'est introduit ici.


def _bande_de_disponibilite(valeur: float) -> int:
    if valeur >= 1.0:
        return 0
    if valeur >= 0.5:
        return 1
    return 2


def _bande_de_fatigue(score: float) -> int:
    """Quantifie la fatigue sur le seul seuil que le moteur utilise déjà.

    `FATIGUE_HIGH_THRESHOLD = 70` est la frontière qui change le POOL de
    candidats (`_passes_fatigue_filter`). C'est donc la seule graduation dont
    le franchissement change matériellement la décision — en inventer une plus
    fine ferait périmer des refus sans qu'aucune décision n'ait bougé.
    """
    from app.services.recommendation import FATIGUE_HIGH_THRESHOLD

    return 1 if score >= FATIGUE_HIGH_THRESHOLD else 0


def _fige(mapping: dict) -> tuple:
    return tuple(sorted((str(k), v) for k, v in mapping.items()))


def empreinte_de_contexte(signaux: Signals) -> str:
    """L'identité du contexte matériel de décision.

    Deux décisions qui partagent cette empreinte sont, du point de vue du
    moteur, **la même décision** : mêmes entrées, même sortie — la causalité
    établie par `REC-CP0a` le garantit (`SAME_HISTORY => SAME_RECOMMENDATION`).

    C'est ce qui permet de se passer d'écriture pendant un `GET` : la décision
    n'a pas besoin d'être enregistrée pour être identifiable.

    ⚠ CE QUI EST DÉLIBÉRÉMENT EXCLU, ET POURQUOI :

    * `hours_since_last_by_zone` — continu, et redondant avec la disponibilité,
      dont on garde la bande ;
    * `availability_by_zone` **brute** — continue ; on garde ses bandes ;
    * `fatigue_score` **brut** — continu ; on garde sa bande ;
    * `median_hard_sets_14d` — entièrement dérivé de `hard_sets_14d_by_zone`,
      déjà présent ; l'ajouter compterait deux fois le même fait ;
    * `last_strength_session_zones` — redondant avec le premier élément de
      `recent_strength_zones_by_session` ;
    * les préférences d'entraînement — **le moteur ne les lit pas**
      (`test_the_recommendation_engine_never_reads_preferences`). Les inclure
      inventerait une dépendance que le produit n'a pas.

    ⚠ CE QUE L'INCLUSION DE `days_since_last_*` IMPLIQUE, DIT FRANCHEMENT :
    un jour qui passe change ces entiers, donc périme le refus. Ce n'est pas
    une TTL déguisée — c'est que le moteur consomme réellement ces valeurs
    (alternance, reprise), donc un jour plus tard la décision n'est plus la
    même décision. À l'intérieur d'une même journée, ils sont constants : le
    refus lie, ce qui est précisément le cas d'usage rapporté.
    """
    pieces: list[Any] = [
        ("froid", signaux.cold_start),
        ("dispo", tuple(
            (z, _bande_de_disponibilite(v))
            for z, v in sorted(signaux.availability_by_zone.items()))),
        ("24h", _fige(signaux.hard_sets_by_zone_24h)),
        ("7j", _fige(signaux.hard_sets_by_zone_recent)),
        ("14j", _fige(signaux.hard_sets_14d_by_zone)),
        ("genres", tuple(signaux.kinds_recent)),
        ("zones_recentes", tuple(
            tuple(z) for z in signaux.recent_strength_zones_by_session)),
        ("cardio_depuis", signaux.days_since_last_cardio),
        ("force_depuis", signaux.days_since_last_strength),
        ("fatigue", _bande_de_fatigue(signaux.fatigue_score)),
        ("reprise", signaux.soft_restart),
        ("partielle", signaux.observation_partielle),
    ]
    brut = repr(pieces).encode("utf-8")
    return hashlib.sha256(brut).hexdigest()[:32]


# ═══════════════ 2. LA LECTURE — AUCUNE ÉCRITURE ═══════════════


def conseils_ecartes(
    db: Session, user_id: int, empreinte: str
) -> frozenset[str]:
    """Les gabarits explicitement écartés **dans ce contexte-ci**.

    ⚠ LA SUPERSESSION EST ICI, ET ELLE EST DÉRIVÉE.

    On ne cherche pas « les refus récents » puis on ne juge pas leur validité :
    on cherche les refus **dont l'empreinte est celle du moment**. Un contexte
    qui a changé ne ramène tout simplement rien. Aucune ligne n'est marquée,
    aucune écriture n'a lieu — cette fonction est appelée pendant un `GET`.

    ⚠ SEUL LE GABARIT EN TÊTE EST « LE CONSEIL ».

    Les alternatives ont été OFFERTES, pas conseillées. Ne pas en choisir une
    n'est pas la refuser, et les traiter comme refusées surgénéraliserait un
    geste unique — ce que le `§8` proscrit.
    """
    lignes = db.execute(
        select(RecommendationEpisode)
        .where(RecommendationEpisode.user_id == user_id)
        .where(RecommendationEpisode.context_fingerprint == empreinte)
    ).scalars().all()
    return frozenset(
        ligne.proposed_top_slug for ligne in lignes if ligne.est_un_refus
    )


# ═══════════════ 3. L'ÉCRITURE — SUR ACTION SEULEMENT ═══════════════


def issue_de(
    slug_demarre: str, top: str, alternatives: tuple[str, ...]
) -> str:
    """Quelle issue un démarrage de séance exprime **réellement**.

    On ne déduit rien de plus que le geste : démarrer le conseil l'accepte,
    démarrer une alternative offerte l'accepte aussi, démarrer autre chose
    alors qu'un conseil était affiché l'écarte.
    """
    if slug_demarre == top:
        return ACCEPTED_TOP
    if slug_demarre in alternatives:
        return ACCEPTED_ALTERNATIVE
    return CHOSE_OTHER


@dataclass(frozen=True)
class Proposition:
    """Ce qu'un formulaire rapporte de la décision qui l'a produit."""

    empreinte: str
    politique: str
    top: str
    alternatives: tuple[str, ...]
    decidee_a: datetime


def enregistrer_episode(
    db: Session,
    user_id: int,
    proposition: Proposition,
    *,
    issue: str,
    slug_choisi: str | None,
    session_id: int | None = None,
    empreinte_courante: str,
) -> bool:
    """Persiste l'issue d'un conseil. Rend `True` si une ligne est née.

    ⚠ UNE PROPOSITION PÉRIMÉE N'EST PAS ENREGISTRÉE.

    Le formulaire rapporte l'empreinte du contexte **au moment du rendu**. Si
    elle ne correspond plus à celle du moment, la page était vieille : le
    contexte a bougé entre l'affichage et le clic. Enregistrer un refus contre
    un contexte qui n'existe plus attribuerait un geste à une décision que
    l'utilisateur n'a pas vue.

    C'est aussi ce qui rend l'épisode infalsifiable de fait : une empreinte
    forgée ne coïncide pas avec celle que le serveur recalcule.

    ⚠ IDEMPOTENT (`§11-G`). Deux rendus de la même décision ne font pas deux
    mémoires, et un double envoi est le même fait. L'unicité est portée par la
    base ; cette fonction ne la contourne pas, elle la respecte.
    """
    if proposition.empreinte != empreinte_courante:
        return False

    deja = db.execute(
        select(RecommendationEpisode)
        .where(RecommendationEpisode.user_id == user_id)
        .where(RecommendationEpisode.context_fingerprint == proposition.empreinte)
    ).scalars().first()
    if deja is not None:
        return False

    db.add(RecommendationEpisode(
        user_id=user_id,
        context_fingerprint=proposition.empreinte,
        policy_version=proposition.politique,
        decided_at=proposition.decidee_a,
        proposed_top_slug=proposition.top,
        proposed_alt_slugs=",".join(
            proposition.alternatives[:MAX_ALTERNATIVES]),
        outcome=issue,
        chosen_slug=slug_choisi,
        session_id=session_id,
    ))
    return True


# ═══════════════ 4. L'ÉTAGE DE DÉCISION ═══════════════


def appliquer(reco: dict, ecartes: frozenset[str]) -> dict:
    """Fait avancer la décision au candidat suivant quand le conseil a été
    écarté dans ce même contexte.

    ⚠ CE N'EST PAS UN FILTRE. Un candidat écarté n'est pas retiré du pool : il
    est **rétrogradé**. Le `§7` l'exige — quand aucune alternative valable
    n'existe, le candidat écarté PEUT revenir, mais l'explication doit dire
    pourquoi il reste la recommandation.

    ⚠ ON NE TOUCHE AUCUN SCORE. Cet étage réordonne une sortie déjà classée ;
    il ne re-note rien. C'est ce qui le rend identique pour `V2` et pour `V3`,
    alors que l'un additionne des poids et que l'autre range des critères.
    """
    if not ecartes:
        return reco

    top = reco["top"]
    if top["template"].slug not in ecartes:
        return reco

    alternatives = list(reco["alternatives"])
    remplacant = next(
        (i for i, a in enumerate(alternatives)
         if a["template"].slug not in ecartes),
        None,
    )

    contexte = dict(reco.get("context") or {})
    contexte["conseil_ecarte"] = top["template"].slug
    # Le NOM, pas seulement le slug : `§14` veut que Mission puisse dire la
    # conséquence, et « liss-abs » n'est pas une phrase qu'on montre.
    contexte["conseil_ecarte_nom"] = getattr(
        top["template"], "name", None) or top["template"].slug

    if remplacant is None:
        # `§7` — il reviendra, mais il devra se justifier.
        contexte["sans_alternative"] = True
        return {**reco, "context": contexte}

    promu = alternatives.pop(remplacant)
    contexte["sans_alternative"] = False
    return {
        "top": promu,
        # Le conseil écarté reste VISIBLE, en tête des alternatives. Le faire
        # disparaître donnerait l'impression qu'AUREN a changé d'avis, alors
        # qu'il a seulement tenu compte d'un geste.
        "alternatives": [top, *alternatives],
        "context": contexte,
    }


# ═══════════════ 5. LA COMPOSITION ═══════════════


def politique_brute(nom: str):
    """La politique de classement, sans mémoire."""
    if nom == "v2":
        from app.services.recommendation import recommend_next_session
        return recommend_next_session
    if nom == "v3":
        from app.services.recommendation_v3 import recommander_v3
        return recommander_v3
    raise ValueError(f"politique inconnue : {nom!r}")


def recommander(
    db: Session,
    user_id: int,
    now: datetime | None = None,
    *,
    politique: str = "v2",
    avec_memoire: bool = False,
) -> dict | None:
    """Le point d'entrée unique des quatre systèmes comparés.

    `V2`, `V2 + mémoire`, `V3`, `V3 + mémoire` — une seule composition, pour
    que la comparaison porte sur la politique et sur la mémoire, jamais sur
    deux chemins d'appel différents.
    """
    from app.services.recommendation import _compute_signals

    now = now or datetime.now(UTC)
    reco = politique_brute(politique)(db, user_id, now=now)
    if reco is None:
        return None

    empreinte = empreinte_de_contexte(_compute_signals(db, user_id, now))
    contexte = dict(reco.get("context") or {})
    contexte["empreinte_contexte"] = empreinte
    contexte["politique"] = politique
    reco = {**reco, "context": contexte}

    if not avec_memoire:
        return reco
    return appliquer(reco, conseils_ecartes(db, user_id, empreinte))
