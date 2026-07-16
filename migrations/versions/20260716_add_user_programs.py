"""Sb_CUSTOM_PROGRAM_PERSISTENCE_01 — user_programs root table.

Additive only (ADD TABLE ONLY contract, hérité Sx_26). No drop, no rename,
no UPDATE/DELETE of existing data, no backfill, no seed. ONE new table:

  * CREATE TABLE user_programs — racine du modèle d'édition Custom Program
    (Sx_CUSTOM_PROGRAM_04 §5, Option C : `UserProgram*` = source de vérité
    d'édition, strictement séparée du catalogue système).

Contract :
  - `user_id` NOT NULL, FK users.id ON DELETE CASCADE — ownership dur,
    aucun programme partagé/global V1 (spec 04 §8).
  - `slug_base` figé à la création, UNIQUE par user
    (`uq_user_program_slug_base`) — base du futur slug publié
    `up{user_id}-{slug_base}-v{n}` (spec 05 §5).
  - `status` ∈ {draft, validated, published, archived} (spec 04 §6) ;
    default `draft`. Seul `draft` est actif tant que wizard/publication
    ne sont pas buildés.
  - `current_version` default 1 (spec 04 §7) ; versions publiées immuables.
  - Soft delete via `archived_at` (jamais destructif).
  - AUCUNE structure enfant, AUCUN pointeur publication dans ce lot
    (différés aux builds gatés suivants) — zéro FK vers le catalogue.
  - Idempotent : guard `_table_exists`.
  - Aucun consommateur : table créée, non branchée (CRUD = PERSISTENCE_04).

Revision ID: l3m8g4h5j76
Revises: k2l7f3g4i65
"""
from alembic import op
import sqlalchemy as sa

revision = "l3m8g4h5j76"
down_revision = "k2l7f3g4i65"
branch_labels = None
depends_on = None

_TABLE = "user_programs"


def _table_exists(name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return name in inspector.get_table_names()


def upgrade() -> None:
    if _table_exists(_TABLE):
        return

    op.create_table(
        _TABLE,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=128), nullable=False),
        sa.Column("slug_base", sa.String(length=64), nullable=False),
        sa.Column(
            "status", sa.String(length=16), nullable=False, server_default="draft"
        ),
        sa.Column(
            "current_version", sa.Integer(), nullable=False, server_default="1"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("user_id", "slug_base", name="uq_user_program_slug_base"),
    )
    op.create_index("ix_user_programs_user_id", _TABLE, ["user_id"])
    op.create_index("ix_user_programs_user_status", _TABLE, ["user_id", "status"])
    op.create_index("ix_user_programs_user_updated", _TABLE, ["user_id", "updated_at"])


def downgrade() -> None:
    # Roundtrip contract: dropping the (empty, unconsumed) new table restores
    # the exact previous schema. No historical data can exist in it at
    # downgrade time in the roundtrip check.
    if not _table_exists(_TABLE):
        return
    op.drop_index("ix_user_programs_user_updated", table_name=_TABLE)
    op.drop_index("ix_user_programs_user_status", table_name=_TABLE)
    op.drop_index("ix_user_programs_user_id", table_name=_TABLE)
    op.drop_table(_TABLE)
