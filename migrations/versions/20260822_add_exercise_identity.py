"""Sb_EXERCISE_IDENTITY_01 — tables `exercises` et `exercise_aliases`.

**Strictement additive.** Deux tables neuves. Aucune colonne ajoutée à une
table existante, aucun DROP, aucun RENAME, **aucun UPDATE d'une donnée
historique**.

Le choix de ne poser AUCUNE clé étrangère sur `template_exercises` ni sur
`session_exercises` est délibéré. Remplir une colonne neuve sur ces tables
resterait un `UPDATE` sur des lignes historiques, et la forme d'une telle
migration est un arrêt dur du contrat de dépôt. La résolution se fait donc au
moment de la lecture, par la table d'alias — l'identité existe et est
utilisable sans qu'une seule ligne d'historique soit réécrite.

Aucune donnée n'est insérée ici non plus : le peuplement appartient à la
graine (`seed_exercise_identity`), idempotente et rejouable, comme le reste du
catalogue. Une migration qui sème diverge dès la première évolution des
données.

Idempotent (`_table_exists`) et downgrade symétrique, comme le reste du dépôt.

Revision ID: t1u6o2p3r14
Revises: s0t5n1o2q13
"""
from alembic import op
import sqlalchemy as sa

revision = "t1u6o2p3r14"
down_revision = "s0t5n1o2q13"
branch_labels = None
depends_on = None

_EXERCISES = "exercises"
_ALIASES = "exercise_aliases"
_IX_NAME = "ix_exercises_name"
_IX_ALIAS_EXERCISE = "ix_exercise_aliases_exercise"


def _table_exists(name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return name in inspector.get_table_names()


def upgrade() -> None:
    if not _table_exists(_EXERCISES):
        op.create_table(
            _EXERCISES,
            sa.Column("id", sa.Integer(), nullable=False),
            # Immuable une fois écrit. C'est l'identité.
            sa.Column("slug", sa.String(length=96), nullable=False),
            # Mutable. Ce n'est qu'un libellé.
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("source", sa.String(length=16), nullable=False),
            sa.Column(
                "created_at", sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("slug", name="uq_exercises_slug"),
        )
        op.create_index(_IX_NAME, _EXERCISES, ["name"], unique=False)

    if not _table_exists(_ALIASES):
        op.create_table(
            _ALIASES,
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("exercise_id", sa.Integer(), nullable=False),
            sa.Column("alias", sa.String(length=255), nullable=False),
            # L'unicité porte sur la forme NORMALISÉE, pas sur la forme brute :
            # « Curl marteau câble (corde) » et « Curl marteau câble corde »
            # coexistent déjà dans deux fichiers de données du dépôt et
            # désignent le même mouvement.
            sa.Column("normalized", sa.String(length=255), nullable=False),
            sa.Column("source", sa.String(length=16), nullable=False),
            sa.ForeignKeyConstraint(
                ["exercise_id"], ["exercises.id"], ondelete="CASCADE"
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "normalized", name="uq_exercise_aliases_normalized"
            ),
        )
        op.create_index(
            _IX_ALIAS_EXERCISE, _ALIASES, ["exercise_id"], unique=False
        )


def downgrade() -> None:
    if _table_exists(_ALIASES):
        op.drop_index(_IX_ALIAS_EXERCISE, table_name=_ALIASES)
        op.drop_table(_ALIASES)
    if _table_exists(_EXERCISES):
        op.drop_index(_IX_NAME, table_name=_EXERCISES)
        op.drop_table(_EXERCISES)
