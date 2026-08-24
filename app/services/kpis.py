"""KPI aggregation for the /progress page.

**KPI rules (all explicit, see docs/PRODUCT_SPEC.md):**

- Work set completion rate counts only `SetLog.kind == "work"`.
  Warmup rows never contribute to the denominator OR the numerator.
- Average success score counts only `SessionExercise.success_score`
  rows where the value is not NULL. NULLs mean "not rated" and are
  excluded from the mean entirely (not treated as 0 or anything).
- The "last 30 days" window is `now - 30d`, no timezone tricks.
- **In-progress sessions are excluded** from the long-term KPIs
  (`completion_rate_30d`, `avg_success_score_30d`, `completed_last_30`).
  They would otherwise drag the completion rate down with unfilled
  rows that simply haven't been touched yet.
- `total_sessions` includes every session regardless of status — it answers
  "how often am I opening the app", which must not depend on whether I
  pressed *Terminer*. **It is not rendered on Progression.**
- `sessions_this_week` **no longer does** (`UX4_03D`,
  `PROGRESSION_SESSION_COUNT = COMPLETED_STAT_ELIGIBLE`). It counted every
  status, and rendered "3" beside `weekly_loop`'s "2" for the same ISO week —
  two definitions, one page, nothing on screen to tell them apart.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.session import SessionExercise, SetLog, WorkoutSession


@dataclass
class GlobalKPIs:
    total_sessions: int
    completed_total: int
    sessions_this_week: int
    sessions_last_30: int
    completed_last_30: int
    avg_success_score_30d: Optional[float]
    completion_rate_30d: Optional[float]
    work_sets_done_30d: int
    work_sets_total_30d: int


def _start_of_iso_week(now: datetime) -> datetime:
    """Midnight UTC at the start of the current ISO week (Monday)."""
    monday = now - timedelta(days=now.isoweekday() - 1)
    return monday.replace(hour=0, minute=0, second=0, microsecond=0)


def compute_global_kpis(
    db: Session, now: Optional[datetime] = None, *, user_id: int | None = None
) -> GlobalKPIs:
    now = now or datetime.now(timezone.utc)
    _uf = (WorkoutSession.user_id == user_id) if user_id is not None else True
    week_start = _start_of_iso_week(now)
    window_start = now - timedelta(days=30)

    total_sessions = db.execute(
        select(func.count(WorkoutSession.id)).where(_uf)
    ).scalar_one() or 0

    completed_total = db.execute(
        select(func.count(WorkoutSession.id))
        .where(_uf)
        .where(WorkoutSession.status == "completed")
        .where(WorkoutSession.excluded_from_stats.is_(False))
    ).scalar_one() or 0

    # `UX4_03D` — `PROGRESSION_SESSION_COUNT = COMPLETED_STAT_ELIGIBLE`.
    #
    # Ce compteur incluait TOUS les statuts, séances exclues des stats
    # comprises. L'intention était « à quelle fréquence j'ouvre l'app » — une
    # question légitime, mais opérationnelle, pas analytique.
    #
    # Mesuré : sur une même page, `weekly_loop` affichait « 2 séances cette
    # semaine » et ce KPI « 3 sessions cette semaine ». MÊME fenêtre ISO, les
    # deux appellent `_start_of_iso_week`. La seule différence était le filtre,
    # et rien à l'écran ne permettait de la deviner.
    #
    # Sur Progression, une séance compte pour l'analytique si et seulement si
    # elle est TERMINÉE et NON EXCLUE des statistiques. L'état « séance
    # ouverte » appartient aux surfaces opérationnelles — l'Accueil et la
    # console de séance —, pas à la lecture d'entraînement.
    sessions_this_week = db.execute(
        select(func.count(WorkoutSession.id))
        .where(_uf)
        .where(WorkoutSession.started_at >= week_start)
        .where(WorkoutSession.status == "completed")
        .where(WorkoutSession.excluded_from_stats.is_(False))
    ).scalar_one() or 0

    sessions_last_30 = db.execute(
        select(func.count(WorkoutSession.id)).where(
            WorkoutSession.started_at >= window_start).where(_uf
        )
    ).scalar_one() or 0

    completed_last_30 = db.execute(
        select(func.count(WorkoutSession.id))
        .where(_uf)
        .where(WorkoutSession.started_at >= window_start)
        .where(WorkoutSession.status == "completed")
        .where(WorkoutSession.excluded_from_stats.is_(False))
    ).scalar_one() or 0

    avg_success_score = db.execute(
        select(func.avg(SessionExercise.success_score))
        .join(WorkoutSession, WorkoutSession.id == SessionExercise.session_id)
        .where(_uf)
        .where(WorkoutSession.started_at >= window_start)
        .where(WorkoutSession.status == "completed")
        .where(WorkoutSession.excluded_from_stats.is_(False))
        .where(SessionExercise.success_score.is_not(None))
    ).scalar()

    work_sets_total = db.execute(
        select(func.count(SetLog.id))
        .join(SessionExercise, SessionExercise.id == SetLog.session_exercise_id)
        .join(WorkoutSession, WorkoutSession.id == SessionExercise.session_id)
        .where(SetLog.kind == "work")
        .where(_uf)
        .where(WorkoutSession.started_at >= window_start)
        .where(WorkoutSession.status == "completed")
        .where(WorkoutSession.excluded_from_stats.is_(False))
    ).scalar_one() or 0

    work_sets_done = db.execute(
        select(func.count(SetLog.id))
        .join(SessionExercise, SessionExercise.id == SetLog.session_exercise_id)
        .join(WorkoutSession, WorkoutSession.id == SessionExercise.session_id)
        .where(SetLog.kind == "work")
        .where(SetLog.completed.is_(True))
        .where(_uf)
        .where(WorkoutSession.started_at >= window_start)
        .where(WorkoutSession.status == "completed")
        .where(WorkoutSession.excluded_from_stats.is_(False))
    ).scalar_one() or 0

    completion_rate = (
        (work_sets_done / work_sets_total) if work_sets_total > 0 else None
    )

    return GlobalKPIs(
        total_sessions=total_sessions,
        completed_total=completed_total,
        sessions_this_week=sessions_this_week,
        sessions_last_30=sessions_last_30,
        completed_last_30=completed_last_30,
        avg_success_score_30d=float(avg_success_score)
        if avg_success_score is not None
        else None,
        completion_rate_30d=completion_rate,
        work_sets_done_30d=work_sets_done,
        work_sets_total_30d=work_sets_total,
    )


def absent_measures(kpis: GlobalKPIs) -> list[str]:
    """`TRAIN1-C` — CE QUI N'EST PAS CALCULABLE, DIT COMME TEL.

    UN DÉNOMINATEUR ABSENT N'EST PAS UN ZÉRO, et ce n'est pas non plus un
    tiret. Les deux mesures dérivées de cette page rendaient un `—` en grand,
    à la place d'un nombre, dans une carte de la même taille que les autres :
    l'écran affichait quatre KPI dont deux ne mesuraient rien.

    Le cas n'est pas théorique — un compte qui ne fait que du cardio a des
    séances terminées, **zéro série de travail prescrite** et **zéro exercice
    noté**. Il lisait donc deux tirets géants, présentés comme des résultats.

    Chaque entrée nomme la CAUSE, telle que le producteur la définit :

      · `completion_rate_30d is None` ⟺ `work_sets_total_30d == 0` — aucune
        série de travail n'a été prescrite. Ce n'est pas « 0 % validé » : à 0
        prescrit, il n'y a rien à valider. (À l'inverse, 0 validé sur 12
        prescrits vaut bien 0 %, et ce 0 % est rendu — c'est une mesure.)
      · `avg_success_score_30d is None` ⟺ aucune ligne `success_score` non
        NULL — aucun exercice n'a été noté. Une moyenne sans terme n'existe
        pas ; `NULL` est explicitement exclu de la moyenne, jamais compté 0.

    La carte disparaît, la raison reste. Retirer les deux sans rien dire
    laisserait croire que la page n'a jamais eu ces mesures.
    """
    absent: list[str] = []
    if kpis.completion_rate_30d is None:
        absent.append("aucune série de travail prescrite")
    if kpis.avg_success_score_30d is None:
        absent.append("aucun exercice noté")
    return absent


@dataclass
class TemplateKPI:
    slug: str
    name: str
    n_completed: int
    last_done_at: Optional[datetime]
    avg_success_score: Optional[float]

    #: `TRAIN1-A` / A11 — séances de ce programme **dans la semaine ISO en
    #: cours**, là où `n_completed` porte sur tout l'historique.
    #:
    #: Ce champ n'est PAS calculé ici : `compute_template_kpis` reste une
    #: requête d'historique, et la fenêtre hebdomadaire est déjà produite par
    #: `build_weekly_loop`. La surface les rapproche plutôt que d'ajouter un
    #: second comptage — deux blocs disaient ce fait sur deux fenêtres, il n'en
    #: reste qu'un, à deux colonnes.
    week_count: int = 0


@dataclass
class RecentExerciseActivity:
    template_slug: str
    template_name: str
    exercise_code: str
    exercise_name: str
    n_sessions_30d: int
    last_done_at: datetime
    last_weights_str: str
    last_reps_str: str


def _fmt_weight(w: Optional[float]) -> str:
    if w is None:
        return "—"
    if w == int(w):
        return str(int(w))
    return f"{w:g}"


def compute_recent_exercise_activity(
    db: Session,
    *,
    limit: int = 10,
    now: Optional[datetime] = None,
    user_id: int | None = None,
) -> list[RecentExerciseActivity]:
    """Last N exercise codes (across all templates) with completed
    work sets in the trailing 30 days, most recent first.

    Intentionally compact: one row per
    (template_slug_snapshot, exercise_code_snapshot), summarising the
    most recent completed work sets. Feeds the /progress "Activité
    récente par exercice" section.

    Rules:
      - only `completed` sessions enter the aggregate
      - only `work` sets are summarised (warmups ignored)
      - only completed work sets contribute to the weight/reps strings
      - window = 30 days back from `now`
    """
    from app.models.session import SessionExercise, SetLog

    now = now or datetime.now(timezone.utc)
    _uf = (WorkoutSession.user_id == user_id) if user_id is not None else True
    window_start = now - timedelta(days=30)

    stmt = (
        select(SessionExercise)
        .join(WorkoutSession, WorkoutSession.id == SessionExercise.session_id)
        .where(_uf)
        .where(WorkoutSession.status == "completed")
        .where(WorkoutSession.excluded_from_stats.is_(False))
        .where(WorkoutSession.started_at >= window_start)
        .order_by(WorkoutSession.started_at.desc())
    )
    rows = db.execute(stmt).scalars().all()
    # Eager-load parent + set_logs in separate queries to avoid
    # an explosion of cartesian products.
    if rows:
        ids = [r.id for r in rows]
        set_rows = db.execute(
            select(SetLog).where(SetLog.session_exercise_id.in_(ids))
        ).scalars().all()
        by_se: dict[int, list] = {}
        for sl in set_rows:
            by_se.setdefault(sl.session_exercise_id, []).append(sl)
        sess_ids = {r.session_id for r in rows}
        sess_rows = db.execute(
            select(WorkoutSession).where(WorkoutSession.id.in_(sess_ids))
        ).scalars().all()
        by_sid = {s.id: s for s in sess_rows}
    else:
        by_se = {}
        by_sid = {}

    # Group by (template_slug, code); keep the most recent hit.
    grouped: dict[tuple[str, str], dict] = {}
    for se in rows:
        parent = by_sid.get(se.session_id)
        if parent is None:
            continue
        key = (parent.template_slug_snapshot, se.exercise_code_snapshot)
        entry = grouped.setdefault(
            key,
            {
                "template_name": parent.template_name_snapshot,
                "exercise_name": se.exercise_name_snapshot,
                "n": 0,
                "last_done_at": parent.started_at,
                "last_se": se,
            },
        )
        entry["n"] += 1
        if parent.started_at > entry["last_done_at"]:
            entry["last_done_at"] = parent.started_at
            entry["last_se"] = se

    def _build(key, entry) -> RecentExerciseActivity:
        slug, code = key
        last_se = entry["last_se"]
        done_work = sorted(
            (
                sl
                for sl in by_se.get(last_se.id, [])
                if sl.kind == "work" and sl.completed
            ),
            key=lambda s: s.set_index,
        )
        weights_str = " / ".join(_fmt_weight(sl.weight_kg) for sl in done_work)
        reps_str = " / ".join(
            ("—" if sl.reps is None else str(sl.reps)) for sl in done_work
        )
        return RecentExerciseActivity(
            template_slug=slug,
            template_name=entry["template_name"],
            exercise_code=code,
            exercise_name=entry["exercise_name"],
            n_sessions_30d=entry["n"],
            last_done_at=entry["last_done_at"],
            last_weights_str=weights_str,
            last_reps_str=reps_str,
        )

    out = [_build(k, v) for k, v in grouped.items()]
    out.sort(key=lambda a: a.last_done_at, reverse=True)
    return out[:limit]


def compute_template_kpis(db: Session, *, user_id: int | None = None) -> list[TemplateKPI]:
    """Per-template summary: number of completed sessions, when the
    last one happened, and the average success score across all its
    logged exercises. Keyed on `template_slug_snapshot` so reseeded
    templates still show up coherently.
    """
    stmt = (
        select(
            WorkoutSession.template_slug_snapshot.label("slug"),
            WorkoutSession.template_name_snapshot.label("name"),
            func.count(WorkoutSession.id.distinct()).label("n_completed"),
            func.max(WorkoutSession.started_at).label("last_done_at"),
            func.avg(SessionExercise.success_score).label("avg_success_score"),
        )
        .outerjoin(
            SessionExercise, SessionExercise.session_id == WorkoutSession.id
        )
        .where(WorkoutSession.user_id == user_id if user_id is not None else True)
        .where(WorkoutSession.status == "completed")
        .where(WorkoutSession.excluded_from_stats.is_(False))
        .group_by(
            WorkoutSession.template_slug_snapshot,
            WorkoutSession.template_name_snapshot,
        )
        .order_by(func.max(WorkoutSession.started_at).desc())
    )
    rows = db.execute(stmt).all()
    return [
        TemplateKPI(
            slug=r.slug,
            name=r.name,
            n_completed=r.n_completed,
            last_done_at=r.last_done_at,
            avg_success_score=float(r.avg_success_score)
            if r.avg_success_score is not None
            else None,
        )
        for r in rows
    ]
