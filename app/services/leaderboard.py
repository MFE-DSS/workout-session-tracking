"""Leaderboard scoring and ranking.

Score rule (documented in docs/PRODUCT_SPEC.md):

For each eligible session:
  - status == "completed"
  - excluded_from_stats == False
  - total_work_sets > 0

  session_points = session_quality_score
                   * (completed_work_sets / total_work_sets)

Per user:
  total_points = sum(session_points) across all eligible sessions
  counted_sessions = number of eligible sessions
  avg_points = total_points / counted_sessions (if > 0)

Grade:
  grade_score = avg_points * log(1 + counted_sessions)
  A: grade_score >= 120
  B: grade_score >= 50
  C: grade_score < 50

Tie handling: users with equal total_points are ordered by
username ASC (deterministic, alphabetical). Documented.
"""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.session import SessionExercise, WorkoutSession
from app.models.user import User
from app.services.performance import GRADE_LABELS, compute_grade
from app.services.quality_score import compute_session_quality


@dataclass
class LeaderboardEntry:
    rank: int
    username: str
    total_points: float
    counted_sessions: int
    avg_points: float | None
    last_session_score: int | None
    grade: str
    grade_label: str

    #: `Sb_UI_CLASSEMENT_01` — L'ÉCART, ET POURQUOI IL REMPLACE LA MOYENNE.
    #:
    #: Un total de points n'a pas d'échelle : personne ne sait si 600 est
    #: beaucoup. Un classement ne répond pas « combien », il répond « où suis-je
    #: et à quelle distance ». L'écart au voisin est la seule donnée qui rend la
    #: liste actionnable, et elle était déjà calculable — elle n'était pas dite.
    #:
    #: Signé, et le signe porte le sens :
    #:   · rang 1 → POSITIF, c'est une avance sur le rang 2 ;
    #:   · rang n → NÉGATIF, c'est un retard sur le rang n-1.
    #: `None` quand il n'y a personne à qui se comparer (un seul classé).
    #:
    #: Entier : la moyenne qu'il remplace s'affichait « moy. 60.0 », et le
    #: dixième de point ne sépare personne.
    points_gap: int | None = None
    #: Le rang auquel `points_gap` se compare — 2 pour le premier, n-1 sinon.
    gap_rank: int | None = None


def compute_leaderboard(db: Session) -> list[LeaderboardEntry]:
    """Compute the full leaderboard across all active users."""
    users = db.execute(
        select(User).where(User.is_active.is_(True))
    ).scalars().all()

    raw: list[tuple[str, float, int, int | None]] = []

    for user in users:
        sessions = db.execute(
            select(WorkoutSession)
            .where(
                WorkoutSession.user_id == user.id,
                WorkoutSession.status == "completed",
                WorkoutSession.excluded_from_stats.is_(False),
            )
            .options(
                selectinload(WorkoutSession.session_exercises)
                .selectinload(SessionExercise.set_logs)
            )
            .order_by(WorkoutSession.started_at.desc())
        ).scalars().all()

        total_pts = 0.0
        counted = 0
        last_score: int | None = None

        for s in sessions:
            total_work = sum(
                1 for se in s.session_exercises
                for sl in se.set_logs if sl.kind == "work"
            )
            if total_work == 0:
                continue
            done_work = sum(
                1 for se in s.session_exercises
                for sl in se.set_logs if sl.kind == "work" and sl.completed
            )
            quality = compute_session_quality(s)
            if last_score is None:
                last_score = quality
            completion_ratio = done_work / total_work
            session_pts = quality * completion_ratio
            total_pts += session_pts
            counted += 1

        raw.append((user.id, user.username, total_pts, counted, last_score))

    raw.sort(key=lambda x: (-x[2], x[1]))

    # `TRAIN1-E` / C4 — LE MINI-RADAR N'EST PLUS PRODUIT.
    #
    # Sb_19 le générait par utilisateur sur le chemin de construction du
    # classement, en notant que « le volume est petit ; si on dépasse 50
    # utilisateurs actifs on mettra en cache ». Le problème n'était pas le coût.
    #
    # Il appelait `compute_physique_dashboard` UNE FOIS PAR LIGNE de classement,
    # pour rendre l'analytique physique en infobulle sur le profil des autres.
    # La surface ne la rend plus ; la calculer serait payer une lecture
    # corporelle par utilisateur affiché pour la jeter — et garder le chemin
    # ouvert pour qu'un `{{ e.radar_svg_mini }}` la ramène sans arbitrage.
    #
    # Effet de bord assumé et mesurable : le classement ne dépend plus du tout
    # de `muscle_scoring`. Un consommateur `LEGACY_SCORE_CONSUMER` de moins.
    entries: list[LeaderboardEntry] = []
    # `_uid` : plus aucun consommateur depuis le retrait du radar. Le tuple le
    # porte encore parce que `raw` sert aussi au tri ; le préfixe dit qu'il
    # n'est pas lu ici plutôt que de laisser ruff signaler une variable morte.
    for i, (_uid, username, pts, counted, last_score) in enumerate(raw, start=1):
        avg = round(pts / counted, 1) if counted > 0 else None
        grade = compute_grade(avg or 0.0, counted)

        entries.append(LeaderboardEntry(
            rank=i,
            username=username,
            total_points=round(pts, 1),
            counted_sessions=counted,
            avg_points=avg,
            last_session_score=last_score,
            grade=grade,
            grade_label=GRADE_LABELS.get(grade, ""),
        ))

    _attach_gaps(entries, [r[2] for r in raw])
    return entries


def _attach_gaps(
    entries: list[LeaderboardEntry], points: list[float]
) -> None:
    """Renseigne `points_gap` / `gap_rank` sur chaque entrée, en place.

    Calculé sur les points BRUTS (`raw`), pas sur `total_points` déjà arrondi :
    deux arrondis successifs déplacent l'écart d'une unité, et un écart faux de
    1 sur un classement se voit.

    Le premier regarde vers le bas (son avance), tout le monde regarde vers le
    haut (son retard). Un classé seul n'a pas d'écart : `None`, pas zéro — zéro
    signifierait « à égalité », ce qui est faux.
    """
    if len(entries) < 2:
        return
    for i, entry in enumerate(entries):
        if i == 0:
            entry.points_gap = round(points[0] - points[1])
            entry.gap_rank = 2
        else:
            entry.points_gap = -round(points[i - 1] - points[i])
            entry.gap_rank = i
