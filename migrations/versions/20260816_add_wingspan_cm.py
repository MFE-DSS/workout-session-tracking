"""Sb_MORPHO_PROFILE_RUNTIME_01 — colonne `wingspan_cm` sur `body_measurements`.

**Strictement additive.** Une seule colonne neuve, nullable. Aucun DROP, aucun
RENAME, aucun UPDATE de données historiques. La colonne héritée `calf_cm` n'est
ni fusionnée, ni supprimée, ni réécrite : elle reste lisible telle quelle.

**Zéro backfill — c'est la garantie centrale de cette migration.** Aucune ligne
existante n'est touchée. Une envergure non mesurée reste `NULL`, et `NULL`
signifie « non mesuré » — pas « égale à la taille ». Estimer l'envergure depuis
la taille fabriquerait exactement l'ape index que la mesure cherche à établir
(`wingspan − height`) : la valeur dérivée vaudrait alors zéro pour tout le monde,
ce qui est une invention présentée comme une mesure.

C'est pourquoi la migration n'écrit aucune valeur, y compris « raisonnable ».
`Sx_MORPHO_CAPTURE_01_SPEC` §4.1 et §6.

Idempotent (`_column_exists`) et downgrade symétrique, comme le reste du dépôt.

Revision ID: r9s4m0n1p12
Revises: q8r3l9m0o11
"""
from alembic import op
import sqlalchemy as sa

revision = "r9s4m0n1p12"
down_revision = "q8r3l9m0o11"
branch_labels = None
depends_on = None

_TABLE = "body_measurements"
_COLUMN = "wingspan_cm"


def _column_exists(table: str, column: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if table not in inspector.get_table_names():
        return False
    return column in {c["name"] for c in inspector.get_columns(table)}


def upgrade() -> None:
    if _column_exists(_TABLE, _COLUMN):
        return
    # ADD COLUMN only. No server_default: a default would materialise a value
    # on every existing row, which is the backfill this migration forbids.
    op.add_column(_TABLE, sa.Column(_COLUMN, sa.Float(), nullable=True))


def downgrade() -> None:
    if not _column_exists(_TABLE, _COLUMN):
        return
    op.drop_column(_TABLE, _COLUMN)
