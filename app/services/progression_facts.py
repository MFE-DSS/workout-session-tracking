"""`TRAIN1-B` — les faits de progression par exercice. Lecture seule.

CE QUE CE MODULE PRODUIT
------------------------
Des **comparaisons factuelles d'exercice à exercice** : la dernière performance
contre la précédente, sur l'identité stable d'`A1`. Rien d'autre.

**Aucun score, aucun seuil, aucun agrégat.** Décision opérateur :

    « Pas de score global inventé. Pas de seuil de progrès.
      Des comparaisons factuelles par exercice. »

Le dépôt écrivait déjà cette règle, dans `delta.py` :

    « The function NEVER infers a "delta" from partial data. »

Ce module ne l'invente donc pas — il la **réutilise**. `compute_delta` reste
l'unique primitive de comparaison ; on ne fait que l'appliquer sur une identité
qui, elle, a changé.

L'IDENTITÉ ANALYTIQUE A CHANGÉ, ET C'EST TOUT L'ENJEU
------------------------------------------------------
`exercise_history` compare sur `(template_slug, exercise_code)` et documente :
« Deliberately does not merge exercises across templates ». Cette frontière
avait un sens quand aucune identité d'exercice n'existait — c'était la seule
clé disponible.

Mesuré sur le catalogue canonique, elle coûtait cher :

* **106 identités héritées pour 68 exercices réels** — 38 fusionnent ;
* **28 exercices sur 68 vivent dans au moins deux gabarits**, et leur
  historique était donc éclaté d'autant ;
* `Leg extensions assises` apparaît dans **4 gabarits sous 3 codes
  différents** (`E3`, `E4`, `E5`) : même la clé héritée n'était pas stable
  pour lui.

Décision opérateur : **le gabarit devient une provenance, pas une identité.**

CE QUI RESTE NON COMPARABLE, ET LE DIT
---------------------------------------
`resolve_exercise` fait une correspondance **exacte après normalisation**, via
la table d'alias. **Aucun rapprochement approximatif** — un nom libre qui ne
correspond à rien reste explicitement hors comparaison, il n'est pas rattaché
au plus ressemblant. Le compte de ces occurrences est **rendu**, pas tu : c'est
la même règle que l'état `PARTIAL` de l'exposition anatomique.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.session import SessionExercise, WorkoutSession
from app.services.delta import Delta, compute_delta
from app.services.exercise_identity import resolve_exercise

#: Profondeur d'historique retenue par exercice. Deux occurrences suffisent à
#: comparer ; on en garde quelques-unes de plus pour que le niveau 2 ait de
#: quoi montrer sans seconde requête.
KEEP_OCCURRENCES = 6

#: Nombre d'exercices rendus au premier niveau. Le reste vit au niveau 2 —
#: un cockpit montre ce qui a bougé récemment, pas un catalogue.
TOP_N = 5


@dataclass(frozen=True)
class Performance:
    """Une occurrence d'exercice, réduite à ce qui se compare.

    `weight` et `reps` viennent de la **première série de travail complétée**,
    comme partout ailleurs dans ce dépôt (`exercise_history._summarise`). Ce
    n'est pas un choix neuf : c'est le point de comparaison que `delta.py`
    attend, et en changer ici rendrait les deux surfaces incohérentes.
    """

    session_id: int
    at: datetime
    weight: float | None
    reps: int | None
    score: int | None
    #: Le gabarit d'où vient cette occurrence. **Provenance, pas identité** —
    #: il est rendu pour que l'utilisateur sache d'où sort le chiffre, jamais
    #: pour séparer deux performances du même mouvement.
    template: str | None


@dataclass
class ExerciseProgression:
    """Un exercice, ses dernières occurrences, et la comparaison des deux
    plus récentes."""

    slug: str
    name: str
    occurrences: list[Performance] = field(default_factory=list)
    delta: Delta | None = None

    @property
    def latest(self) -> Performance | None:
        return self.occurrences[0] if self.occurrences else None

    @property
    def previous(self) -> Performance | None:
        return self.occurrences[1] if len(self.occurrences) > 1 else None

    @property
    def comparable(self) -> bool:
        """Deux occurrences ne suffisent pas : il faut deux occurrences
        **mesurées**. Une séance ouverte sans série complétée ne compare rien."""
        return self.delta is not None

    @property
    def templates(self) -> list[str]:
        """Les gabarits qui ont produit ces occurrences, du plus récent au
        moins. Plusieurs entrées = l'exercice a franchi une frontière que
        l'identité héritée traitait comme deux exercices distincts."""
        seen: dict[str, None] = {}
        for o in self.occurrences:
            if o.template:
                seen.setdefault(o.template, None)
        return list(seen)


@dataclass
class ProgressionFacts:
    """Ce que la surface reçoit. Aucun classement par « progrès » : l'ordre
    est **chronologique**, du dernier exercice pratiqué au plus ancien."""

    exercises: list[ExerciseProgression] = field(default_factory=list)

    #: Occurrences dont le nom n'a pu être résolu vers aucune identité.
    #: **Rendues, jamais tues** : les taire ferait passer une couverture
    #: partielle pour une couverture totale.
    unresolved: int = 0

    #: Noms non résolus, dédupliqués — de quoi agir plutôt que de constater.
    unresolved_names: list[str] = field(default_factory=list)

    @property
    def comparable(self) -> list[ExerciseProgression]:
        return [e for e in self.exercises if e.comparable]

    @property
    def awaiting(self) -> list[ExerciseProgression]:
        """Pratiqués une seule fois, ou sans série complétée : rien à
        comparer **encore**. Ce n'est pas une absence de progrès."""
        return [e for e in self.exercises if not e.comparable]


def _first_completed_work_set(se: SessionExercise):
    """Même règle que `exercise_history._summarise`, et pour la même raison :
    deux surfaces qui comparent des points différents se contrediraient."""
    work = sorted(
        (sl for sl in se.set_logs if sl.kind == "work"),
        key=lambda s: s.set_index,
    )
    for sl in work:
        if sl.completed and (sl.weight_kg is not None or sl.reps is not None):
            return sl
    return None


def _performed_name(se: SessionExercise) -> str:
    """Le nom RÉELLEMENT exécuté. Une substitution remplace l'exercice prévu ;
    la comparer au prévu comparerait deux mouvements différents."""
    return se.substituted_name or se.exercise_name_snapshot or ""


def build_progression_facts(
    db: Session, user_id: int, *, now: datetime | None = None
) -> ProgressionFacts:
    """Lecture seule, déterministe. Une requête, puis une résolution par nom.

    **Seules les séances terminées et éligibles aux statistiques** entrent ici
    — même filtre que `progress_facts`, pour la même raison : une séance
    ouverte n'est pas une performance, et une séance exclue des stats a été
    exclue par l'utilisateur.
    """
    now = now or datetime.now(UTC)

    rows = db.execute(
        select(SessionExercise)
        .join(WorkoutSession, WorkoutSession.id == SessionExercise.session_id)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == "completed",
            WorkoutSession.excluded_from_stats.is_(False),
        )
        .options(
            selectinload(SessionExercise.set_logs),
            joinedload(SessionExercise.session),
        )
        .order_by(WorkoutSession.started_at.desc())
    ).unique().scalars().all()

    by_slug: dict[str, ExerciseProgression] = {}
    unresolved = 0
    unresolved_names: dict[str, None] = {}

    for se in rows:
        name = _performed_name(se)
        found = resolve_exercise(db, name)
        if found is None:
            # Aucun rapprochement approximatif : on ne rattache pas au plus
            # ressemblant. L'occurrence reste hors comparaison, et se compte.
            unresolved += 1
            if name.strip():
                unresolved_names.setdefault(name.strip(), None)
            continue

        prog = by_slug.setdefault(
            found.slug, ExerciseProgression(slug=found.slug, name=found.name)
        )
        if len(prog.occurrences) >= KEEP_OCCURRENCES:
            continue

        sl = _first_completed_work_set(se)
        prog.occurrences.append(Performance(
            session_id=se.session_id,
            at=se.session.started_at,
            weight=sl.weight_kg if sl else None,
            reps=sl.reps if sl else None,
            score=se.success_score,
            template=se.session.template_name_snapshot,
        ))

    for prog in by_slug.values():
        _attach_delta(prog)

    return ProgressionFacts(
        exercises=list(by_slug.values()),
        unresolved=unresolved,
        unresolved_names=list(unresolved_names),
    )


def _attach_delta(prog: ExerciseProgression) -> None:
    """La comparaison des deux occurrences les plus récentes, ou rien.

    On ne saute PAS une occurrence sans mesure pour aller chercher une plus
    ancienne comparable : « la dernière fois » veut dire la dernière fois. Une
    séance où l'exercice a été fait sans rien noter est une information, pas un
    trou à combler.
    """
    latest, previous = prog.latest, prog.previous
    if latest is None or previous is None:
        return
    if latest.weight is None and latest.reps is None:
        return
    if previous.weight is None and previous.reps is None:
        return
    prog.delta = compute_delta(
        latest.weight, latest.reps, latest.score,
        previous.weight, previous.reps, previous.score,
    )


__all__ = [
    "KEEP_OCCURRENCES",
    "TOP_N",
    "ExerciseProgression",
    "Performance",
    "ProgressionFacts",
    "build_progression_facts",
]
