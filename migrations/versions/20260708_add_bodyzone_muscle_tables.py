"""Sb_32.1 — BodyZone & Muscle foundation.

Additive only (ADD TABLE ONLY contract, hérité Sx_26). No drop, no rename,
no UPDATE/DELETE of existing data. Two NEW tables:

  * CREATE TABLE body_zones   — 11 zones backfillées depuis les constantes
    ``muscle_mapping`` (ZONE_LABELS / ZONE_MEASUREMENT / ZONE_VOLUME_TARGET /
    RADAR_AXES). Source de vérité unique, préparée pour Sb_32.2.
  * CREATE TABLE muscles      — table préparée, EMPTY V1 (OQ-32-B/F : aucune
    anatomie fine inventée ; peuplement depuis sources explicites plus tard).

Hard contract :
  - Aucune table existante touchée (invariance historique = contrainte #1).
  - Le backfill dérive STRICTEMENT des constantes existantes au moment de la
    migration (import du module) → aucune valeur inventée, aucune divergence
    possible vs la source actuelle. Une valeur absente aujourd'hui reste NULL.
  - ``classify_exercise`` et tous les consommateurs restent inchangés (aucune
    bascule runtime en Sb_32.1).
  - Idempotent : guards ``_table_exists`` ; le backfill ne s'exécute que si la
    table vient d'être créée.
  - Downgrade : drop des deux nouvelles tables uniquement (sûr — aucun code
    existant ne branche dessus en V1).

Revision ID: j1k6e2f3h54
Revises: 7i0f5d1e2g43
"""
from alembic import op
import sqlalchemy as sa

revision = "j1k6e2f3h54"
down_revision = "7i0f5d1e2g43"
branch_labels = None
depends_on = None


def _table_exists(table: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table in set(inspector.get_table_names())


def _zone_backfill_rows() -> list[dict]:
    """Derive the 11 zone rows STRICTLY from the current muscle_mapping
    constants — never hardcoded here, so the backfill stays in lockstep
    with the existing source of truth (invariance)."""
    from app.services.muscle_mapping import (
        RADAR_AXES,
        ZONE_LABELS,
        ZONE_MEASUREMENT,
        ZONE_VOLUME_TARGET,
    )

    zone_to_axis: dict[str, str] = {}
    for axis, spec in RADAR_AXES.items():
        for zone_code in spec["zones"]:
            zone_to_axis[zone_code] = axis

    rows: list[dict] = []
    for code, label in ZONE_LABELS.items():
        rows.append(
            {
                "code": code,
                "label": label,
                "measurement_field": ZONE_MEASUREMENT.get(code),
                "radar_axis": zone_to_axis.get(code),  # None for zones off-radar (core)
                "volume_target": ZONE_VOLUME_TARGET.get(code),
                "is_active": True,
            }
        )
    return rows


def upgrade() -> None:
    created_body_zones = False

    if not _table_exists("body_zones"):
        op.create_table(
            "body_zones",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("code", sa.String(length=64), nullable=False, unique=True),
            sa.Column("label", sa.String(length=128), nullable=False),
            sa.Column("measurement_field", sa.String(length=64), nullable=True),
            sa.Column("radar_axis", sa.String(length=64), nullable=True),
            sa.Column("volume_target", sa.Integer(), nullable=True),
            sa.Column(
                "is_active", sa.Boolean(), nullable=False, server_default="1"
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )
        created_body_zones = True

    if not _table_exists("muscles"):
        op.create_table(
            "muscles",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("code", sa.String(length=64), nullable=False, unique=True),
            sa.Column("name", sa.String(length=128), nullable=False),
            sa.Column(
                "body_zone_code",
                sa.String(length=64),
                sa.ForeignKey("body_zones.code", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("category", sa.String(length=32), nullable=True),
            sa.Column(
                "is_active", sa.Boolean(), nullable=False, server_default="1"
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )
        # muscles stays EMPTY in V1 (OQ-32-B/F : no invented anatomy).

    # Backfill body_zones only if the table was just created (idempotent).
    if created_body_zones:
        body_zones = sa.table(
            "body_zones",
            sa.column("code", sa.String),
            sa.column("label", sa.String),
            sa.column("measurement_field", sa.String),
            sa.column("radar_axis", sa.String),
            sa.column("volume_target", sa.Integer),
            sa.column("is_active", sa.Boolean),
        )
        op.bulk_insert(body_zones, _zone_backfill_rows())


def downgrade() -> None:
    if _table_exists("muscles"):
        op.drop_table("muscles")
    if _table_exists("body_zones"):
        op.drop_table("body_zones")
