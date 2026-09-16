"""`UI-CP3.5` — écrire et relire une décision d'adaptation.

CE MODULE EST LA FRONTIÈRE ENTRE LE NOYAU PUR ET LA BASE
--------------------------------------------------------
`plan_adaptation` ne connaît ni base ni horloge : il décide et il compose.
Ici on persiste la décision, et on la relit.

⚠ RIEN N'EST INVENTÉ : `decision_traces` EXISTAIT DÉJÀ.
Elle porte l'identité d'exécution, l'identité de contenu, l'empreinte de plan,
la justification, l'horodatage — et son immuabilité est **imposée** par un
écouteur `before_update` qui lève plutôt que de laisser réécrire une preuve.
Le type `REPLAN_DELTA` y était **déclaré et jamais émis**. On l'émet.

Seul le cycle de vie manquait, parce qu'une trace immuable ne peut pas en
porter : il vit dans `plan_adaptation_dismissals`, qui ne contient rien
d'autre.

QUAND ON ÉCRIT
--------------
À la **clôture d'une séance**, et nulle part ailleurs. Jamais pendant un `GET` :
afficher l'accueil n'écrit rien, jamais. C'est ce qui distingue une mémoire
d'une recomputation déguisée.
"""
from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.services.plan_adaptation import Adaptation, ZoneDeferral

#: Version de la politique d'adaptation. Une décision prise sous une règle
#: ancienne reste lisible pour ce qu'elle était — c'est le rôle de ce champ
#: dans `decision_traces`, et on l'emploie pour ce qu'il est.
ADAPTATION_POLICY_VERSION = "cp3.5.1"


def record_adaptation(
    db: Session,
    user_id: int,
    *,
    plan_fingerprint: str,
    deferrals: tuple[ZoneDeferral, ...],
    done: int,
    total: int,
    basis: tuple[str, ...],
) -> str | None:
    """Écrit UNE décision. Rend son `decision_id`, ou `None` si rien à écrire.

    Rend `None` quand aucun report n'a de conséquence : une décision sans effet
    produirait un bloc de continuité qui n'annonce aucun changement.
    """
    if not any(d.sets_deferred > 0 for d in deferrals):
        return None

    from app.services.decision_analytics import (
        REPLAN_DELTA,
        DraftTrace,
        persist_traces,
    )

    draft = DraftTrace(
        decision_type=REPLAN_DELTA,
        policy_version=ADAPTATION_POLICY_VERSION,
        selected_output={
            "done": done,
            "total": total,
            "deferrals": [
                {
                    "zone_code": d.zone_code,
                    "sets_before": d.sets_before,
                    "sets_after": d.sets_after,
                }
                for d in deferrals
                if d.sets_deferred > 0
            ],
        },
        basis=basis,
    )
    persist_traces(db, user_id, (draft,), plan_fingerprint=plan_fingerprint)

    # `persist_traces` rend l'identifiant de GROUPE, pas celui de la décision.
    # On relit la ligne qu'on vient d'écrire plutôt que de deviner : une
    # identité devinée serait exactement le genre de raccourci qui rend une
    # trace inutilisable.
    from app.models.decision_trace import DecisionTrace

    ligne = db.execute(
        select(DecisionTrace)
        .where(DecisionTrace.user_id == user_id)
        .where(DecisionTrace.decision_type == REPLAN_DELTA)
        .order_by(DecisionTrace.id.desc())
        .limit(1)
    ).scalars().first()
    return ligne.decision_id if ligne is not None else None


def _adaptation_from(ligne) -> Adaptation | None:
    """Reconstruit une adaptation depuis sa trace. Tolérant, jamais devinant.

    Une trace dont la charge utile n'a pas la forme attendue est **ignorée**,
    pas réparée : elle vient d'une version antérieure de la politique, et lui
    prêter un sens qu'elle n'a pas serait pire que de l'omettre.
    """
    try:
        payload = json.loads(ligne.selected_output or "{}")
        reports = tuple(
            ZoneDeferral(
                zone_code=d["zone_code"],
                sets_before=int(d["sets_before"]),
                sets_after=int(d["sets_after"]),
            )
            for d in payload.get("deferrals", [])
        )
    except (ValueError, TypeError, KeyError):
        return None

    if not reports:
        return None

    try:
        motifs = tuple(json.loads(ligne.basis or "[]"))
    except (ValueError, TypeError):
        motifs = ()

    return Adaptation(
        decision_id=ligne.decision_id,
        decided_at=ligne.created_at,
        plan_fingerprint=ligne.plan_fingerprint or "",
        deferrals=reports,
        done=int(payload.get("done", 0)),
        total=int(payload.get("total", 0)),
        basis=motifs,
    )


def active_adaptations(db: Session, user_id: int) -> tuple[Adaptation, ...]:
    """Les décisions **non écartées**, la plus récente d'abord.

    ⚠ CE QUE CETTE FONCTION NE FAIT PAS : juger de l'applicabilité.

    La supersession se dérive contre le plan de BASE, que ce module ne
    construit pas. `plan_adaptation.build_effective_plan` s'en charge, et c'est
    volontaire : mélanger « ce qui est stocké » et « ce qui s'applique » ferait
    de la lecture une décision, et une décision prise à la lecture n'est pas
    une mémoire.

    ⚠ AUCUNE ÉCRITURE. Pas de marquage `SUPERSEDED`, pas de nettoyage. Cette
    fonction est appelée pendant un `GET`.
    """
    from app.models.decision_trace import DecisionTrace
    from app.models.plan_adaptation_dismissal import PlanAdaptationDismissal
    from app.services.decision_analytics import REPLAN_DELTA

    ecartees = set(db.execute(
        select(PlanAdaptationDismissal.decision_id)
        .where(PlanAdaptationDismissal.user_id == user_id)
    ).scalars().all())

    lignes = db.execute(
        select(DecisionTrace)
        .where(DecisionTrace.user_id == user_id)
        .where(DecisionTrace.decision_type == REPLAN_DELTA)
        .order_by(DecisionTrace.id.desc())
        .limit(20)
    ).scalars().all()

    out = []
    for ligne in lignes:
        if ligne.decision_id in ecartees:
            continue
        a = _adaptation_from(ligne)
        if a is not None and a.is_material:
            out.append(a)
    return tuple(out)


def dismiss(db: Session, user_id: int, decision_id: str) -> bool:
    """Écarte une adaptation. **La trace historique n'est pas touchée.**

    Ce qui cesse, c'est l'EFFET : l'adaptation ne compose plus le plan
    effectif. Écarter deux fois est le même fait, donc la seconde fois ne
    produit rien et ne lève pas.
    """
    from app.models.plan_adaptation_dismissal import PlanAdaptationDismissal

    deja = db.execute(
        select(PlanAdaptationDismissal)
        .where(PlanAdaptationDismissal.decision_id == decision_id)
        .where(PlanAdaptationDismissal.user_id == user_id)
    ).scalars().first()
    if deja is not None:
        return False

    db.add(PlanAdaptationDismissal(
        decision_id=decision_id, user_id=user_id))
    return True


def effective_plan_for_user(db: Session, user_id: int):
    """`(plan_de_base, plan_effectif)` pour un utilisateur — le point d'entrée
    UNIQUE de la continuité côté lecture.

    ⚠ POURQUOI UN SEUL POINT D'ENTRÉE.

    Deux surfaces qui composeraient l'adaptation chacune à leur manière
    divergeraient au premier correctif — c'est l'avertissement que
    `zone_exposure` porte déjà pour ses résolveurs, et il vaut ici. Toute
    surface qui veut le plan de l'utilisateur passe par cette fonction.

    ⚠ AUCUNE ÉCRITURE. Appelée pendant des `GET`.

    ⚠ ET ELLE N'EST PAS CÂBLÉE SUR L'ACCUEIL, DÉLIBÉRÉMENT.
    `home.build_home_payload` construit un plan que MISSION **ne rend plus**
    depuis `UI-CP3`. Y brancher la continuité coûterait deux requêtes sur la
    route la plus chaude du produit pour un rendu inexistant — exactement les
    cinq calculs morts que `UI-CP3` vient de retirer. L'accueil lit
    l'adaptation elle-même, pas le plan qu'elle transforme.
    """
    from app.services.plan_adaptation import build_effective_plan
    from app.services.training_preferences import get_training_preferences

    prefs = get_training_preferences(db, user_id)
    return build_effective_plan(prefs, active_adaptations(db, user_id))


__all__ = [
    "ADAPTATION_POLICY_VERSION",
    "active_adaptations",
    "dismiss",
    "effective_plan_for_user",
    "record_adaptation",
]
