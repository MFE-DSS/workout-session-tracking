"""UI-CP3.5 — table `plan_adaptation_dismissals`.

**Strictement additive.** Une seule table neuve, aucune colonne ajoutée à une
table existante, aucun DROP, aucun RENAME, aucun UPDATE de données historiques.

**Pourquoi une table plutôt qu'une colonne.** Tout ce qui constitue une
décision d'adaptation vit dans `decision_traces`, dont l'immuabilité est
imposée par un écouteur `before_update`. On ne peut donc pas y poser un
`dismissed_at` : une preuve historique ne se réécrit pas. Le cycle de vie a son
propre support, et il ne porte que ce que la trace refuse.

**Aucun backfill.** Aucune adaptation n'a jamais été proposée, donc aucune n'a
jamais été écartée. Fabriquer des lignes affirmerait un geste que personne n'a
fait.

**Trois états, un seul persisté.** `ACTIVE` est l'absence de ligne ;
`DISMISSED` est une ligne ; `SUPERSEDED` est **dérivé** de l'empreinte de plan
au moment de la lecture. Marquer la supersession exigerait d'écrire pendant un
`GET`, ce que le contrat de la tranche interdit.

Rétention : `ON DELETE CASCADE` sur le compte, comme `decision_traces`.

Idempotent (`_table_exists`) et downgrade symétrique, comme le reste du dépôt.

Revision ID: u2v7p3q4s15
Revises: t1u6o2p3r14
"""
import sqlalchemy as sa
from alembic import op

revision = "u2v7p3q4s15"
down_revision = "t1u6o2p3r14"
branch_labels = None
depends_on = None

_TABLE = "plan_adaptation_dismissals"
_IX_USER = "ix_plan_adapt_dismissal_user"


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
        # L'identité d'EXÉCUTION de la trace écartée. Pas une clé étrangère SQL :
        # `decision_traces` a sa propre politique de rétention, et l'y attacher
        # ferait de cette table une contrainte sur elle.
        sa.Column("decision_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "dismissed_at", sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "decision_id", name="uq_plan_adapt_dismissal_decision_id"),
    )
    op.create_index(_IX_USER, _TABLE, ["user_id"], unique=False)


def downgrade() -> None:
    if not _table_exists(_TABLE):
        return
    op.drop_index(_IX_USER, table_name=_TABLE)
    op.drop_table(_TABLE)
