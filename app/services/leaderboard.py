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
from typing import Optional

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
    avg_points: Optional[float]
    last_session_score: Optional[int]
    grade: str
    grade_label: str


def compute_leaderboard(db: Session) -> list[LeaderboardEntry]:
    """Compute the full leaderboard across all active users."""
    users = db.execute(
        select(User).where(User.is_active.is_(True))
    ).scalars().all()

    raw: list[tuple[str, float, int, Optional[int]]] = []

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
        last_score: Optional[int] = None

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
    return entries
