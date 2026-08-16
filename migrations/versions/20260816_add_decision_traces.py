"""Sb_DECISION_ANALYTICS_RUNTIME_01 — table `decision_traces`.

**Strictement additive.** Une seule table neuve, aucune colonne ajoutée à une
table existante, aucun DROP, aucun RENAME, aucun UPDATE de données historiques.

**Aucun backfill, et c'est un choix de fond.** Les décisions déjà prises n'ont
pas été tracées ; fabriquer des lignes à partir de l'état actuel produirait des
preuves d'un raisonnement qui n'a jamais eu lieu — exactement l'inverse de ce
que cette table sert à établir. L'absence de trace pour un plan ancien est une
information vraie.

**Rétention = durée de vie du propriétaire** (`RETENTION_POLICY_V1`). Pas de
TTL, pas de purge, pas d'archivage : `ON DELETE CASCADE` suffit, la trace
disparaît avec le compte qui l'a produite.

Idempotent (`_table_exists`) et downgrade symétrique, comme le reste du dépôt.

Revision ID: s0t5n1o2q13
Revises: r9s4m0n1p12
"""
from alembic import op
import sqlalchemy as sa

revision = "s0t5n1o2q13"
down_revision = "r9s4m0n1p12"
branch_labels = None
depends_on = None

_TABLE = "decision_traces"
_IX_USER_CREATED = "ix_decision_traces_user_created"
_IX_GROUP = "ix_decision_traces_group"
_IX_FINGERPRINT = "ix_decision_traces_fingerprint"


def _table_exists(name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return name in inspector.get_table_names()


def upgrade() -> None:
    if _table_exists(_TABLE):
        return

    op.create_table(
        _TABLE,
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("decision_id", sa.String(length=64), nullable=False),
        sa.Column("trace_group_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("decision_type", sa.String(length=48), nullable=False),
        sa.Column("policy_version", sa.String(length=48), nullable=False),
        sa.Column("decision_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("upstream_decision_ids", sa.Text(), nullable=False),
        # Quatre colonnes distinctes plutôt qu'un champ « sources » unique :
        # la séparation des natures est le contrat, pas une commodité.
        sa.Column("constraint_sources", sa.Text(), nullable=False),
        sa.Column("preference_sources", sa.Text(), nullable=False),
        sa.Column("morphology_sources", sa.Text(), nullable=False),
        sa.Column("recovery_sources", sa.Text(), nullable=False),
        sa.Column("selected_output", sa.Text(), nullable=False),
        sa.Column("rejected_alternatives", sa.Text(), nullable=False),
        sa.Column("basis", sa.Text(), nullable=False),
        sa.Column("confidence", sa.String(length=32), nullable=True),
        sa.Column("plan_fingerprint", sa.String(length=64), nullable=True),
        sa.Column("program_id", sa.Integer(), nullable=True),
        sa.Column("program_version", sa.Integer(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("decision_id", name="uq_decision_traces_decision_id"),
    )
    op.create_index(_IX_USER_CREATED, _TABLE, ["user_id", "created_at"], unique=False)
    op.create_index(_IX_GROUP, _TABLE, ["trace_group_id"], unique=False)
    op.create_index(_IX_FINGERPRINT, _TABLE, ["decision_fingerprint"], unique=False)


def downgrade() -> None:
    if not _table_exists(_TABLE):
        return
    op.drop_index(_IX_FINGERPRINT, table_name=_TABLE)
    op.drop_index(_IX_GROUP, table_name=_TABLE)
    op.drop_index(_IX_USER_CREATED, table_name=_TABLE)
    op.drop_table(_TABLE)
