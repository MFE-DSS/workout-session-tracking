"""add performance indexes for KPI and behavioral queries

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-04-12

Three composite indexes targeting the hot query paths:

1. workout_sessions(user_id, status, excluded_from_stats, started_at)
   — Covers KPIs, leaderboard, behavioral engine, timelines.
     Every query that filters "completed, non-excluded sessions
     for user X ordered by date" benefits.

2. session_exercises(session_id)
   — Covers the JOIN from WorkoutSession → SessionExercise used
     in quality score, KPI, and leaderboard computations. The
     existing unique constraint (session_id, position) helps but
     a bare leading-column index is more efficient for joins.

3. set_logs(session_exercise_id, kind, completed)
   — Covers work set completion counts. The pattern
     WHERE kind='work' AND completed=True is the hottest SetLog
     access pattern (quality score, completion rate, KPIs).

All CREATE INDEX operations are non-destructive and non-blocking
on SQLite. On PostgreSQL, consider CREATE INDEX CONCURRENTLY for
large tables (requires manual migration edit).
"""
from typing import Sequence, Union

from alembic import op


revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Composite covering index for session filtering + ordering.
    op.create_index(
        "ix_ws_user_status_excl_started",
        "workout_sessions",
        ["user_id", "status", "excluded_from_stats", "started_at"],
    )

    # 2. Bare FK index for session_exercises → workout_sessions join.
    op.create_index(
        "ix_session_exercises_session_id",
        "session_exercises",
        ["session_id"],
    )

    # 3. Composite index for work set completion filtering.
    op.create_index(
        "ix_set_logs_exercise_kind_completed",
        "set_logs",
        ["session_exercise_id", "kind", "completed"],
    )


def downgrade() -> None:
    op.drop_index("ix_set_logs_exercise_kind_completed", table_name="set_logs")
    op.drop_index("ix_session_exercises_session_id", table_name="session_exercises")
    op.drop_index("ix_ws_user_status_excl_started", table_name="workout_sessions")
