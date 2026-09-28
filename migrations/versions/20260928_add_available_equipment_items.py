"""TRAIN A — l'environnement concret : une colonne sur `training_preferences`.

**Strictement additive.** Une colonne nullable sur une table existante. Aucun
DROP, aucun RENAME, aucun UPDATE de données historiques.

**AUCUN BACKFILL, ET C'EST LE CŒUR DE LA TRANCHE.**

La table porte déjà `available_equipment` : un ensemble de **familles**
(`barbell`, `cable`, `dumbbell`, `machine`, `smith`, `bodyweight`). La colonne
ajoutée ici porte des **objets physiques** (`adjustable_bench`,
`dual_adjustable_pulley`, `lat_pulldown_station`, `leg_press`…).

Remplir la seconde depuis la première serait inventer du matériel :

    `dumbbell` ⇏ « possède un banc »
    `machine`  ⇏ « possède les treize machines »
    `cable`    ⇏ « possède une poulie double réglable »

La dernière est la plus nette, et elle est documentée par le constructeur :
sur un Life Fitness MJ4, le tirage vertical et le tirage bas sont deux
stations sélectorisées **distinctes**, chacune avec sa propre colonne de
charge, et la poulie double réglable est encore un autre produit. « Du
câble » ne dit pas lequel.

`NULL` dit donc exactement « l'environnement concret n'est pas résolu », et
c'est ce que porte tout utilisateur existant après cette migration. Un
environnement non résolu ne rend jamais un exercice infaisable : le verdict
est `UNKNOWN`, jamais un refus.

Idempotent (`_has_column`) et downgrade symétrique, comme le reste du dépôt.

Revision ID: x5y0s6t7v18
Revises: w4x9r5s6u17
"""
import sqlalchemy as sa
from alembic import op

revision = "x5y0s6t7v18"
down_revision = "w4x9r5s6u17"
branch_labels = None
depends_on = None

_TABLE = "training_preferences"
_COLUMN = "available_equipment_items"


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if table not in inspector.get_table_names():
        return False
    return column in {c["name"] for c in inspector.get_columns(table)}


def upgrade() -> None:
    if not _has_column(_TABLE, _COLUMN):
        op.add_column(_TABLE, sa.Column(_COLUMN, sa.Text(), nullable=True))
    # Aucun UPDATE. Voir la docstring : aucune dérivation honnête n'existe.


def downgrade() -> None:
    # Ce qui disparaît est la déclaration d'environnement concret, qui
    # n'existait pas avant cette migration. Les familles grossières, les
    # priorités et la cadence vivent dans d'autres colonnes, intouchées.
    if _has_column(_TABLE, _COLUMN):
        op.drop_column(_TABLE, _COLUMN)
