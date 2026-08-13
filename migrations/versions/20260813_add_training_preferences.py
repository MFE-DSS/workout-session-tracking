"""Sb_TRAINING_PREFERENCES_01 — table des préférences d'entraînement déclarées.

**Strictement additive.** Une seule table neuve, aucune colonne ajoutée à
`users`, aucun DROP, aucun RENAME, aucun UPDATE de données historiques.

**Aucun backfill.** C'est la garantie centrale de la tranche : la migration ne
crée **aucune ligne**, pour personne. Un utilisateur existant reste parfaitement
valide **sans** ligne de préférences, et cet état signifie « rien n'a été
déclaré » — pas « 3 séances par semaine », pas « tout le matériel disponible ».
Fabriquer une ligne par défaut transformerait une absence de déclaration en fait
stocké, exactement ce qu'un futur planificateur doit pouvoir distinguer.

Unicité `user_id` : une ligne **au plus** par utilisateur, imposée par contrainte
et non par convention applicative. `ON DELETE CASCADE` : les préférences n'ont
aucun sens sans leur propriétaire, et ce sont des données déclaratives
reconstituables — contrairement à l'historique d'entraînement, jamais supprimé.

Idempotent (`_table_exists`) et downgrade symétrique, comme le reste du dépôt.

Revision ID: q8r3l9m0o11
Revises: p7q2k8l9n10
"""
from alembic import op
import sqlalchemy as sa

revision = "q8r3l9m0o11"
down_revision = "p7q2k8l9n10"
branch_labels = None
depends_on = None

_TABLE = "training_preferences"
_IX_NAME = "ix_training_preferences_user_id"
_UQ_NAME = "uq_training_preferences_user_id"


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
        sa.Column("user_id", sa.Integer(), nullable=False),
        # Toutes les préférences sont nullable : « non déclaré » est un état
        # de premier ordre, pas une valeur manquante à combler.
        sa.Column("sessions_per_week", sa.Integer(), nullable=True),
        sa.Column("focus_priorities", sa.Text(), nullable=True),
        sa.Column("available_equipment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name=_UQ_NAME),
    )
    op.create_index(_IX_NAME, _TABLE, ["user_id"], unique=False)


def downgrade() -> None:
    if not _table_exists(_TABLE):
        return
    op.drop_index(_IX_NAME, table_name=_TABLE)
    op.drop_table(_TABLE)
