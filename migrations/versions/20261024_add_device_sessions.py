"""D9 — table `device_sessions` : l'identité serveur d'une application connectée.

**Strictement additive.** Une seule table neuve, aucune colonne ajoutée à une
table existante, aucun DROP, aucun RENAME, aucun UPDATE de données historiques.

**Pourquoi elle est inévitable.** `users.session_epoch` (`y6z1t7u8w19`) révoque
toutes les sessions d'un compte à la fois. `D9` exige deux choses qu'une époque
par compte ne peut pas exprimer : révoquer UN appareil (déconnexion mobile), et
refuser un jeton de rafraîchissement déjà échangé (rotation). Les deux
supposent un état par appareil, tenu côté serveur.

**Aucun backfill.** Aucune application n'a jamais été connectée : la table naît
vide, et chaque ligne naît d'une connexion réelle.

Le secret de rafraîchissement n'est jamais stocké, seulement son condensat.
Rétention : `ON DELETE CASCADE` sur le compte, comme `recommendation_episodes`.

Idempotent (`_table_exists`) et downgrade symétrique, comme le reste du dépôt.

Revision ID: z7a2u8v9x20
Revises: y6z1t7u8w19
"""
import sqlalchemy as sa
from alembic import op

revision = "z7a2u8v9x20"
down_revision = "y6z1t7u8w19"
branch_labels = None
depends_on = None

_TABLE = "device_sessions"
_IX = "ix_device_sessions_user_id"


def _table_exists(name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return name in inspector.get_table_names()


def upgrade() -> None:
    if _table_exists(_TABLE):
        return

    op.create_table(
        _TABLE,
        sa.Column("id", sa.String(length=32), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("refresh_hash", sa.String(length=64), nullable=False),
        # L'époque A0 du compte à l'émission : une révocation globale la rend caduque.
        sa.Column("session_epoch", sa.Integer(), nullable=False),
        sa.Column("device_label", sa.String(length=64), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False,
        ),
        sa.Column("last_used_at", sa.DateTime(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(_IX, _TABLE, ["user_id"], unique=False)


def downgrade() -> None:
    # Ce qui disparaît est l'état de connexion des applications, qui n'existait pas avant.
    if not _table_exists(_TABLE):
        return
    op.drop_index(_IX, table_name=_TABLE)
    op.drop_table(_TABLE)
