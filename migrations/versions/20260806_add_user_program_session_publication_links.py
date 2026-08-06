"""Sb_CUSTOM_PROGRAM_PUBLICATION_01 — session→template publication links.

Additive only (ADD COLUMN ONLY contract, hérité Sx_26). No drop, no rename,
no UPDATE/DELETE of existing data, no backfill, no seed, no new table. DEUX
colonnes nullable sur `user_program_sessions` — le lien programme→template que
la spec 05 §6 place côté SÉANCE (une `UserProgramSession` → un `WorkoutTemplate`
custom à la publication) :

  * published_template_id   INTEGER      NULL  FK workout_templates.id
                                                 ON DELETE SET NULL
  * template_slug_snapshot  VARCHAR(64)  NULL

Pourquoi (justification de la migration) :
  La matérialisation (PUBLICATION_01) crée N `WorkoutTemplate` custom, un par
  séance planifiée (slug `up{uid}-{base}-v{n}-s{position}`, spec 05 §6). Le lien
  programme→templates vit côté séance : `published_template_id` pointe la template
  matérialisée, `template_slug_snapshot` fige le slug publié — trace historique
  étanche qui survit même si la template est un jour supprimée (ON DELETE SET
  NULL dénoue la FK, le snapshot reste). Nullable + AUCUN backfill : les séances
  existantes (jamais publiées) restent `NULL`, l'état correct d'un programme non
  publié.

  ON DELETE SET NULL (et non CASCADE) : supprimer une template publiée ne doit
  JAMAIS détruire la séance-source du programme utilisateur — le programme reste
  la source de vérité éditable, la template n'est que son artefact.

Idempotent : guard `_column_exists` par colonne. Downgrade symétrique (FK +
index avant colonnes), même pattern que `36be39e26189` (FK sur ADD COLUMN via
`batch_alter_table`, seule voie propre pour une FK sur SQLite).

Revision ID: p7q2k8l9n10
Revises: o6p1j7k8m09
"""
from alembic import op
import sqlalchemy as sa

revision = "p7q2k8l9n10"
down_revision = "o6p1j7k8m09"
branch_labels = None
depends_on = None

_TABLE = "user_program_sessions"
_FK_COL = "published_template_id"
_SNAP_COL = "template_slug_snapshot"
_FK_NAME = "fk_user_program_sessions_published_template_id"
_IX_NAME = "ix_user_program_sessions_published_template_id"


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
    need_fk = not _column_exists(_TABLE, _FK_COL)
    need_snap = not _column_exists(_TABLE, _SNAP_COL)
    if not (need_fk or need_snap):
        return
    with op.batch_alter_table(_TABLE, schema=None) as batch_op:
        if need_fk:
            batch_op.add_column(sa.Column(_FK_COL, sa.Integer(), nullable=True))
        if need_snap:
            batch_op.add_column(
                sa.Column(_SNAP_COL, sa.String(length=64), nullable=True)
            )
        if need_fk:
            batch_op.create_index(_IX_NAME, [_FK_COL], unique=False)
            batch_op.create_foreign_key(
                _FK_NAME,
                "workout_templates",
                [_FK_COL],
                ["id"],
                ondelete="SET NULL",
            )


def downgrade() -> None:
    if not _table_exists(_TABLE):
        return
    with op.batch_alter_table(_TABLE, schema=None) as batch_op:
        if _column_exists(_TABLE, _FK_COL):
            batch_op.drop_constraint(_FK_NAME, type_="foreignkey")
            batch_op.drop_index(_IX_NAME)
            batch_op.drop_column(_FK_COL)
        if _column_exists(_TABLE, _SNAP_COL):
            batch_op.drop_column(_SNAP_COL)
