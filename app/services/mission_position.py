"""`UI-CP3` — MISSION : où reprendre une séance ouverte.

POURQUOI CE MODULE EXISTE
-------------------------
L'accueil disait « En cours · depuis 37 min ». **Une durée n'est pas une
position.** Quelqu'un qui revient au milieu d'une séance ne se demande pas
depuis combien de temps il est parti, il se demande *où il en est*.

Mesuré au labo avant d'écrire une ligne : une séance ouverte avec deux
exercices terminés sur quatre et le troisième entamé n'affichait, sur
l'accueil, aucune de ces trois informations.

CE QUE CE MODULE N'EST PAS
--------------------------
Ce n'est **pas** un second instrument d'exécution. MISSION n'a pas besoin de
l'état de console, ni des cibles, ni des deltas, ni de la bande de séries —
tout cela appartient à `EXECUTION` et y reste. MISSION a besoin du strict
nécessaire pour reprendre intelligemment, et rien de plus.

LE COÛT, DIT D'AVANCE
---------------------
`AUREN_INSTRUMENTS.md` nomme « progression intra-séance » comme un trou dont
le coût est de charger `session_exercises → set_logs`. Ce module **ne charge
pas l'arbre** : il pose **une** requête d'agrégation qui rend cinq entiers.
Le coût annoncé était celui de l'implémentation naïve ; celle-ci l'évite.
"""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.session import SessionExercise, SetLog


@dataclass(frozen=True)
class MissionPosition:
    """Position de reprise. Tous les champs sont des FAITS comptés.

    Aucun pourcentage, aucun score, aucune estimation de temps restant : la
    précision ne doit pas dépasser le modèle (`AUREN_INSTRUMENTS §6.3`).
    """

    exercise_index: int      #: rang de l'exercice où l'on reprend (1-based)
    exercise_total: int      #: nombre d'exercices de la séance
    sets_done: int           #: séries de TRAVAIL enregistrées
    sets_total: int          #: séries de travail prescrites
    exercise_name: str | None    #: l'exercice où l'on reprend
    set_index: int | None        #: la série locale où l'on reprend, si connue

    @property
    def is_meaningful(self) -> bool:
        """Vrai quand la position apprend quelque chose.

        Une séance sans aucune série de travail prescrite n'a pas de position
        à annoncer — et prétendre « exercice 1 sur 0 » serait pire que se
        taire. C'est la même discipline que `UI-CP2.1` a appliquée au libellé
        « PASSER AUX SÉRIES » : une commande ne nomme pas une destination
        inexistante.
        """
        return self.exercise_total > 0 and self.sets_total > 0


def open_session_position(db: Session, session_id: int) -> MissionPosition | None:
    """Rend la position de reprise d'une séance, en UNE requête d'agrégation.

    Rend ``None`` si la séance ne porte aucun exercice — cas réel : une séance
    cardio. L'appelant n'affiche alors aucune position plutôt qu'un zéro qu'il
    n'a pas mesuré.
    """
    done = func.sum(
        case((SetLog.completed.is_(True), 1), else_=0)
    ).label("done")

    rows = db.execute(
        select(
            SessionExercise.id,
            SessionExercise.position,
            SessionExercise.exercise_name_snapshot,
            SessionExercise.substituted_name,
            func.count(SetLog.id).label("total"),
            done,
        )
        .join(SetLog, SetLog.session_exercise_id == SessionExercise.id)
        .where(SessionExercise.session_id == session_id)
        .where(SetLog.kind == "work")
        .group_by(SessionExercise.id)
        .order_by(SessionExercise.position.asc())
    ).all()

    if not rows:
        return None

    sets_done = sum(int(r.done or 0) for r in rows)
    sets_total = sum(int(r.total or 0) for r in rows)

    # L'exercice de reprise est le PREMIER dont le travail n'est pas fini.
    # Quand tout est fait, on reprend au dernier — la séance attend sa
    # clôture, pas un exercice de plus.
    reprise = next(
        (r for r in rows if int(r.done or 0) < int(r.total or 0)),
        rows[-1],
    )
    index = [r.id for r in rows].index(reprise.id) + 1
    restant = int(reprise.total or 0) - int(reprise.done or 0)

    return MissionPosition(
        exercise_index=index,
        exercise_total=len(rows),
        sets_done=sets_done,
        sets_total=sets_total,
        exercise_name=reprise.substituted_name or reprise.exercise_name_snapshot,
        # La série locale n'est annoncée que s'il en reste une à faire.
        set_index=(int(reprise.done or 0) + 1) if restant > 0 else None,
    )
