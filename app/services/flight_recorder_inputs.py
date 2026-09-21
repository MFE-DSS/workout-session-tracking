"""`UI-CP5 FLIGHT_RECORDER` — l'unique lecture en base du debriefing.

POURQUOI CE MODULE EXISTE SÉPARÉMENT
--------------------------------------
`flight_recorder` doit rester **pur** : ni `sqlalchemy`, ni `datetime`, donc
testable sans base et incapable de muter quoi que ce soit. Le patron est celui
d'`overload_engine` / `overload_inputs` et de `body_intelligence*` — il n'est
pas inventé pour cette tranche.

CE QUE LA REQUÊTE CHARGE, ET POURQUOI JUSQUE-LÀ
-------------------------------------------------
Une séance, avec **tout** ce dont les cinq règles d'anomalie ont besoin :

* `session_exercises → set_logs` — les règles A, B, D, E lisent les séries ;
* `session_exercises → template_exercise → rep_targets` — la règle E lit
  `min_reps` via `_min_rep_target`.

⚠ Cette seconde chaîne est la raison d'être du module. `template_exercise` est
une relation **paresseuse** : sans elle, la règle E déclenche ~2 SELECT par
exercice. Ce coût existe **aujourd'hui**, silencieusement, dans
`weekly_loop._pick_top_anomaly`, et sur toutes les séances de la semaine. Ici il
est payé une fois, explicitement, sur une seule séance.

Bilan net pour `/progress` : **+1 aller-retour borné, −N chargements
paresseux.**

CE QUE « EXPLOITABLE » VEUT DIRE, ET POURQUOI C'EST LE MÊME FILTRE QU'AILLEURS
-------------------------------------------------------------------------------
`completed` et **non exclue des statistiques** — exactement les deux filtres
qu'emploient déjà `weekly_loop._load_window_sessions`, `progression_facts` et
`compute_global_kpis`. Une séance que l'utilisateur a retirée de ses KPI ne doit
pas revenir lui parler par la porte du debriefing.

⚠ AUCUNE FENÊTRE DE TEMPS. C'est délibéré : la question est « depuis ta dernière
séance », pas « cette semaine ». Une fenêtre hebdomadaire se tait le lundi matin
alors que la dernière séance date de la veille — c'est le défaut de la surface
précédente, et il n'est pas reconduit.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.catalog import TemplateExercise
from app.models.session import SessionExercise, WorkoutSession


def derniere_seance_exploitable(db: Session, user_id: int) -> WorkoutSession | None:
    """La dernière séance terminée et comptée, hydratée pour le détecteur.

    Rend `None` quand il n'y en a aucune — ce n'est pas une erreur, c'est l'état
    d'un compte neuf, et le debriefing sait le dire.
    """
    stmt = (
        select(WorkoutSession)
        .where(WorkoutSession.user_id == user_id)
        .where(WorkoutSession.status == "completed")
        .where(WorkoutSession.excluded_from_stats.is_(False))
        .order_by(WorkoutSession.started_at.desc())
        .limit(1)
        .options(
            selectinload(WorkoutSession.session_exercises)
            .selectinload(SessionExercise.set_logs),
            # ⚠ La chaîne va jusqu'à `rep_targets`, pas jusqu'à
            # `template_exercise`. S'arrêter un cran plus tôt laisserait la
            # règle E charger `rep_targets` en paresseux — c'est-à-dire
            # exactement le coût que ce module existe pour supprimer.
            selectinload(WorkoutSession.session_exercises)
            .selectinload(SessionExercise.template_exercise)
            .selectinload(TemplateExercise.rep_targets),
        )
    )
    return db.execute(stmt).scalars().first()
