"""Sb_CUSTOM_PROGRAM_SCORING_03 — quality review runtime fields.

Additive only (ADD COLUMN ONLY contract, hérité Sx_26). No drop, no rename,
no UPDATE/DELETE of existing data, no backfill, no seed, no new table.
TROIS colonnes nullable sur `user_program_quality_reviews` :

  * confidence       VARCHAR(16) NULL
  * coverage_ratio   FLOAT       NULL
  * grade_cap_reason TEXT        NULL

Pourquoi (justification de la migration) :
  Le réceptacle créé par `PERSISTENCE_03` reflète exactement le modèle
  `QualityReview` de la spec 03 §4. Le moteur livré par `SCORING_01`
  produit TROIS champs supplémentaires, nés de la doctrine des gaps
  honnêtes imposée par la réalité de l'EKB (4 sous-scores sur 8 non
  mesurables) :
    - `confidence` et `coverage_ratio` : fiabilité de la lecture, fonction
      de l'état de l'EKB **au moment du scoring** — un EKB futur enrichi
      donnerait d'autres valeurs, donc NON dérivables après coup ;
    - `grade_cap_reason` : explique pourquoi un grade est plafonné à B.
  Sans ces colonnes, une trace figée portant « B » se lirait comme un B
  pleinement mesuré : la trace serait TROMPEUSE. L'invariance historique
  exige une trace fidèle — d'où ces trois colonnes.

  Les glisser dans un payload JSON existant (`subscores_json`…) ferait
  mentir le nom de la colonne : écarté.

Non stockés volontairement :
  - `disclaimer` : constante du moteur, aucune colonne nécessaire ;
  - le feedback de `SCORING_02` : fonction PURE du résultat, reconstructible
    à tout moment — le stocker dupliquerait du dérivé.

Idempotent : guard `_column_exists` par colonne. Downgrade symétrique.

Revision ID: o6p1j7k8m09
Revises: n5o0i6j7l98
"""
from alembic import op
import sqlalchemy as sa

revision = "o6p1j7k8m09"
down_revision = "n5o0i6j7l98"
branch_labels = None
depends_on = None

_TABLE = "user_program_quality_reviews"

_COLUMNS = (
    ("confidence", sa.String(length=16)),
    ("coverage_ratio", sa.Float()),
    ("grade_cap_reason", sa.Text()),
)


def _table_exists(name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return name in inspector.get_table_names()


def _column_exists(table: str, column: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return column in {col["name"] for col in inspector.get_columns(table)}


def upgrade() -> None:
    if not _table_exists(_TABLE):
        return
    for name, type_ in _COLUMNS:
        if not _column_exists(_TABLE, name):
            op.add_column(_TABLE, sa.Column(name, type_, nullable=True))


def downgrade() -> None:
    if not _table_exists(_TABLE):
        return
    for name, _type in reversed(_COLUMNS):
        if _column_exists(_TABLE, name):
            op.drop_column(_TABLE, name)
