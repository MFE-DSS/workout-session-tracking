"""Sb_24.1 — implicit signal + scoring version (Sx_24).

Additive only. Three new nullable/defaulted columns to support the
implicit signal scoring model defined by Sx_24 spec:

  * session_exercises.implicit_label           VARCHAR(32) NULL
  * session_exercises.implicit_label_computed_at TIMESTAMP NULL
  * workout_sessions.scoring_version           INT NOT NULL DEFAULT 1

Hard contract (spec §H — backward compatibility):
  - No UPDATE on existing rows.
  - All pre-existing rows get scoring_version=1 via the column DEFAULT,
    so compute_session_quality() continues to use the v1 formula
    forever for any session created before this migration runs.
  - implicit_label stays NULL on pre-existing rows — the future
    detection service only populates it on the completed→ transition
    of NEW sessions.
  - Downgrade drops the columns — safe because no other code references
    them yet (the service consuming them lands in Sb_24.2 → Sb_24.5).

Revision ID: 4f7c2a8b9d10
Revises: c3d5f1e82a04
"""
from alembic import op
import sqlalchemy as sa

revision = "4f7c2a8b9d10"
down_revision = "c3d5f1e82a04"
branch_labels = None
depends_on = None


def _column_exists(table: str, column: str) -> bool:
    """Check if a column already exists — makes the migration idempotent.

    A previous deploy attempt may have partially applied the upgrade
    (some columns added) without advancing alembic_version (because a
    later step failed). Retrying must not raise "duplicate column" on
    the already-present columns. This helper turns each add_column into
    a no-op if the column is already there.
    """
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = {col["name"] for col in inspector.get_columns(table)}
    return column in existing


def upgrade() -> None:
    # ADD COLUMN direct — SQLite supporte ça nativement pour les colonnes
    # NULL (sans recréation de table). Idempotent : si une tentative de
    # déploiement précédente a partiellement appliqué le ALTER, on
    # skip silencieusement la colonne existante.
    if not _column_exists("session_exercises", "implicit_label"):
        op.add_column(
            "session_exercises",
            sa.Column("implicit_label", sa.String(32), nullable=True),
        )
    if not _column_exists("session_exercises", "implicit_label_computed_at"):
        op.add_column(
            "session_exercises",
            sa.Column(
                "implicit_label_computed_at",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
        )
    # Pour la colonne NOT NULL avec default — SQLite supporte le pattern
    # ALTER TABLE … ADD COLUMN … NOT NULL DEFAULT N directement, sans
    # recréation de table, dès SQLite 3.32 (Ubuntu 22.04+ : 3.37). Le
    # DEFAULT est appliqué aux rows existantes au moment du ALTER.
    if not _column_exists("workout_sessions", "scoring_version"):
        op.add_column(
            "workout_sessions",
            sa.Column(
                "scoring_version",
                sa.Integer(),
                nullable=False,
                server_default="1",
            ),
        )


def downgrade() -> None:
    if _column_exists("workout_sessions", "scoring_version"):
        op.drop_column("workout_sessions", "scoring_version")
    if _column_exists("session_exercises", "implicit_label_computed_at"):
        op.drop_column("session_exercises", "implicit_label_computed_at")
    if _column_exists("session_exercises", "implicit_label"):
        op.drop_column("session_exercises", "implicit_label")
