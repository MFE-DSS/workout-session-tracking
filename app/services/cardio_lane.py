"""`TRAIN1-B` — la voie cardio. Lecture seule, et volontairement à part.

POURQUOI CE MODULE N'EST PAS DANS `progression_facts`
------------------------------------------------------
Décision opérateur, mot pour mot :

    « Ne pas forcer le cardio dans une identité SetLog/exercice.
      Le cardio est une voie SECONDAIRE, au niveau de la séance. »

Ce n'est pas une commodité d'écriture, c'est le modèle qui le dit : les
données cardio — ``cardio_duration_min``, ``cardio_bpm_avg``,
``cardio_machine_type`` — vivent sur ``WorkoutSession``, **pas** sur
``SessionExercise``. Il n'y a ni série, ni charge, ni répétition à comparer.
Les y forcer aurait demandé d'inventer une identité d'exercice qui n'existe
pas dans les données.

CE QUI EST COMPARÉ, ET CE QUI NE L'EST JAMAIS
-----------------------------------------------
============================  =============================================
``cardio_duration_min``       **fait primaire** — la seule grandeur comparée
``cardio_bpm_avg``            **contexte** — rendu à côté, jamais comparé
``cardio_machine_type``       **condition** de comparabilité
``cardio_machine_calories``   **jamais** une métrique de progression
============================  =============================================

Trois interdits, tous explicites dans la décision :

1. **Comparaison uniquement à machine identique.** Vingt minutes de rameur et
   vingt minutes de tapis ne sont pas la même chose ; les mettre en regard
   fabriquerait une équivalence que rien n'établit.
2. **Les calories machine ne progressent pas.** Ce sont des estimations
   propriétaires, non comparables entre appareils et sans contrat de mesure.
3. **Une comparaison chronologique n'implique aucune amélioration.** Plus
   longtemps n'est pas mieux — ce peut être une séance de récupération. Ce
   module rend donc un **écart**, jamais un jugement, et aucun score.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.session import WorkoutSession

#: Profondeur retenue par type de machine.
KEEP_SESSIONS = 6


@dataclass(frozen=True)
class CardioBout:
    """Une séance cardio, réduite à ce que le contrat autorise à montrer."""

    session_id: int
    at: datetime
    machine: str | None
    duration_min: int | None
    bpm_avg: int | None
    #: ⚠ `cardio_machine_calories` N'EST PAS LU ICI, et c'est délibéré. Ne pas
    #: le charger est plus solide qu'une note disant de ne pas s'en servir :
    #: on ne peut pas afficher par distraction une valeur qu'on n'a pas.


@dataclass
class CardioMachineLane:
    """Une machine, ses sorties récentes, et l'écart des deux dernières."""

    machine: str
    bouts: list[CardioBout] = field(default_factory=list)

    @property
    def latest(self) -> CardioBout | None:
        return self.bouts[0] if self.bouts else None

    @property
    def previous(self) -> CardioBout | None:
        return self.bouts[1] if len(self.bouts) > 1 else None

    @property
    def duration_delta(self) -> int | None:
        """Écart de durée entre les deux dernières sorties de CETTE machine.

        **Un écart, pas un verdict.** Plus long n'est pas mieux : une sortie
        courte peut être une récupération voulue. La surface rend le signe et
        la valeur ; elle ne les qualifie pas.
        """
        a, b = self.latest, self.previous
        if a is None or b is None:
            return None
        if a.duration_min is None or b.duration_min is None:
            return None
        return a.duration_min - b.duration_min


@dataclass
class CardioFacts:
    lanes: list[CardioMachineLane] = field(default_factory=list)

    #: Séances cardio sans type de machine renseigné. Elles ne peuvent être
    #: comparées à rien — la comparabilité est conditionnée à la machine — et
    #: leur nombre est rendu plutôt que passé sous silence.
    untyped: int = 0

    @property
    def any_data(self) -> bool:
        return bool(self.lanes) or self.untyped > 0


def build_cardio_facts(
    db: Session, user_id: int, *, now: datetime | None = None
) -> CardioFacts:
    """Lecture seule. Une requête, au niveau séance.

    Même filtre d'éligibilité que partout ailleurs sur Progression : terminée
    et non exclue des statistiques.
    """
    now = now or datetime.now(UTC)

    rows = db.execute(
        select(WorkoutSession)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == "completed",
            WorkoutSession.excluded_from_stats.is_(False),
            WorkoutSession.cardio_duration_min.is_not(None),
        )
        .order_by(WorkoutSession.started_at.desc())
    ).scalars().all()

    lanes: dict[str, CardioMachineLane] = {}
    untyped = 0

    for s in rows:
        machine = (s.cardio_machine_type or "").strip()
        if not machine:
            # Sans machine, aucune comparaison n'est licite. On la compte, on
            # ne la range pas d'office dans une voie qu'elle n'a pas déclarée.
            untyped += 1
            continue
        lane = lanes.setdefault(machine, CardioMachineLane(machine=machine))
        if len(lane.bouts) >= KEEP_SESSIONS:
            continue
        lane.bouts.append(CardioBout(
            session_id=s.id,
            at=s.started_at,
            machine=machine,
            duration_min=s.cardio_duration_min,
            bpm_avg=s.cardio_bpm_avg,
        ))

    return CardioFacts(lanes=list(lanes.values()), untyped=untyped)


__all__ = [
    "KEEP_SESSIONS",
    "CardioBout",
    "CardioFacts",
    "CardioMachineLane",
    "build_cardio_facts",
]
