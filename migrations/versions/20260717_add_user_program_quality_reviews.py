"""Sb_CUSTOM_PROGRAM_PERSISTENCE_03 — user_program_quality_reviews table.

Additive only (ADD TABLE ONLY contract, hérité Sx_26). No drop, no rename,
no UPDATE/DELETE of existing data, no backfill, no seed. ONE new table:

  * CREATE TABLE user_program_quality_reviews — trace FIGÉE d'un scoring
    de programme custom (Sx_CUSTOM_PROGRAM_03 §9-C / 04 §5) : une row par
    version publiée, jamais réécrite.

Contract :
  - `user_program_id` NOT NULL, FK user_programs.id ON DELETE CASCADE
    (+ index) — la trace vit et meurt avec son programme.
  - UNIQUE (user_program_id, version) — `uq_user_program_quality_review_version` :
    une seule trace par version ; l'immutabilité est portée par cette
    contrainte + la discipline service (le passé n'est jamais recalculé,
    doctrine `scoring_version` Sx_30/Sb_24.1).
  - `grade` (A/B/C) et `scoring_version` NOT NULL ; `ekb_version` nullable
    (OQ-PERS-J tranchée : colonne dédiée requêtable).
  - 5 payloads JSON textuels opaques (subscores/alerts/suggestions/
    assumptions/missing_data) — le contenu appartient au futur moteur
    (`Sb_CUSTOM_PROGRAM_SCORING_01+`) : AUCUN score calculé/interprété ici.
  - `computed_at` NOT NULL server_default now() (posé par l'appelant,
    le moteur pur reste sans horloge — spec 03 §4).
  - Idempotent : guard `_table_exists`. Aucun consommateur.

Revision ID: n5o0i6j7l98
Revises: m4n9h5i6k87
"""
from alembic import op
import sqlalchemy as sa

revision = "n5o0i6j7l98"
down_revision = "m4n9h5i6k87"
branch_labels = None
depends_on = None

_TABLE = "user_program_quality_reviews"


def _table_exists(name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return name in inspector.get_table_names()


def upgrade() -> None:
    if _table_exists(_TABLE):
        return

    op.create_table(
        _TABLE,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_program_id",
            sa.Integer(),
            sa.ForeignKey("user_programs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("grade", sa.String(length=1), nullable=False),
        sa.Column("global_score", sa.Integer(), nullable=True),
        sa.Column("subscores_json", sa.Text(), nullable=True),
        sa.Column("alerts_json", sa.Text(), nullable=True),
        sa.Column("suggestions_json", sa.Text(), nullable=True),
        sa.Column("assumptions_json", sa.Text(), nullable=True),
        sa.Column("missing_data_json", sa.Text(), nullable=True),
        sa.Column("scoring_version", sa.Integer(), nullable=False),
        sa.Column("ekb_version", sa.String(length=32), nullable=True),
        sa.Column(
            "computed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "user_program_id",
            "version",
            name="uq_user_program_quality_review_version",
        ),
    )
    op.create_index(
        "ix_user_program_quality_reviews_user_program_id",
        _TABLE,
        ["user_program_id"],
    )


def downgrade() -> None:
    # Roundtrip contract: the new table is empty and unconsumed at
    # downgrade time in the roundtrip check.
    if not _table_exists(_TABLE):
        return
    op.drop_index(
        "ix_user_program_quality_reviews_user_program_id", table_name=_TABLE
    )
    op.drop_table(_TABLE)
