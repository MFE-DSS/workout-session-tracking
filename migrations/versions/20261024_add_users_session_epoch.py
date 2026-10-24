"""A0 — l'époque de session : une colonne sur `users`.

**Strictement additive.** Une colonne entière, non nulle, de défaut 0, sur une table existante.
Aucun DROP, aucun RENAME, aucun UPDATE de données historiques.

Chaque jeton de session porte l'époque de l'utilisateur au moment où il a été émis ; le lecteur
qui fait autorité refuse un jeton dont l'époque n'est plus la sienne. Incrémenter l'époque rend
donc invalides, sans attendre leur expiration, tous les jetons déjà émis : c'est l'état serveur
qu'exige `Sx_SEC_A0_SESSION_TOKEN_INTEGRITY` (I4 à I7, forme E retenue par l'opérateur).

**Le défaut 0 n'est pas un backfill.** Il ne dit rien sur le passé : tous les jetons émis avant
ce déploiement sont de toute façon refusés par la transition T1 (signature typée par usage), et
chacun se reconnecte une fois.

Idempotent (`_has_column`) et downgrade symétrique, comme le reste du dépôt.

Revision ID: y6z1t7u8w19
Revises: x5y0s6t7v18
"""
import sqlalchemy as sa
from alembic import op

revision = "y6z1t7u8w19"
down_revision = "x5y0s6t7v18"
branch_labels = None
depends_on = None

_TABLE = "users"
_COLUMN = "session_epoch"


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if table not in inspector.get_table_names():
        return False
    return column in {c["name"] for c in inspector.get_columns(table)}


def upgrade() -> None:
    if not _has_column(_TABLE, _COLUMN):
        op.add_column(_TABLE, sa.Column(_COLUMN, sa.Integer(), nullable=False, server_default="0"))


def downgrade() -> None:
    # Ce qui disparaît est l'état de révocation, qui n'existait pas avant cette migration.
    if _has_column(_TABLE, _COLUMN):
        op.drop_column(_TABLE, _COLUMN)
