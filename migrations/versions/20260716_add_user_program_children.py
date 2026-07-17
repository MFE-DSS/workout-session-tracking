"""Sb_CUSTOM_PROGRAM_PERSISTENCE_02 — user program child tables.

Additive only (ADD TABLE ONLY contract, hérité Sx_26). No drop, no rename,
no UPDATE/DELETE of existing data, no backfill, no seed. THREE new tables
(lot unique validé opérateur — l'arbre est cohésif) :

  * CREATE TABLE user_program_sessions   — slots de séance planifiés
  * CREATE TABLE user_program_exercises  — slots d'exercice par séance
  * CREATE TABLE user_program_rep_targets — ranges prescrits par set

Contract (Sx_CUSTOM_PROGRAM_04 §5) :
  - Arbre d'ownership : user_programs → sessions → exercises → rep_targets,
    FK ON DELETE CASCADE à chaque niveau (+ index FK).
  - Uniques : (user_program_id, position) · (user_program_session_id,
    position) · (user_program_exercise_id, set_index, is_warmup).
  - `exercise_name` = nom canonique EKB (identité historique, jamais
    renommé) ; `variant_key`/`variant_group` + copies dénormalisées
    equipment/pattern = aides d'édition/scoring, l'EKB reste la référence.
  - **ZÉRO FK vers le catalogue système ou l'EKB** — la matérialisation
    (spec 05 §6 : 1 session → 1 WorkoutTemplate custom) est un build
    ultérieur gaté, jamais ici.
  - `kind` default 'strength' (vocabulaire catalogue) ; `is_warmup`
    default false partout en V1.
  - Idempotent : guard `_table_exists` par table.
  - Aucun consommateur : tables créées, non branchées (CRUD =
    PERSISTENCE_04).

Revision ID: m4n9h5i6k87
Revises: l3m8g4h5j76
"""
from alembic import op
import sqlalchemy as sa

revision = "m4n9h5i6k87"
down_revision = "l3m8g4h5j76"
branch_labels = None
depends_on = None

_SESSIONS = "user_program_sessions"
_EXERCISES = "user_program_exercises"
_REP_TARGETS = "user_program_rep_targets"


def _table_exists(name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return name in inspector.get_table_names()


def upgrade() -> None:
    if not _table_exists(_SESSIONS):
        op.create_table(
            _SESSIONS,
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_program_id",
                sa.Integer(),
                sa.ForeignKey("user_programs.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("position", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=128), nullable=False),
            sa.Column(
                "kind",
                sa.String(length=16),
                nullable=False,
                server_default="strength",
            ),
            sa.Column(
                "focus", sa.String(length=128), nullable=False, server_default=""
            ),
            sa.Column("duration_target_minutes", sa.Integer(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.UniqueConstraint(
                "user_program_id", "position", name="uq_user_program_session_position"
            ),
        )
        op.create_index(
            "ix_user_program_sessions_user_program_id", _SESSIONS, ["user_program_id"]
        )

    if not _table_exists(_EXERCISES):
        op.create_table(
            _EXERCISES,
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_program_session_id",
                sa.Integer(),
                sa.ForeignKey("user_program_sessions.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("position", sa.Integer(), nullable=False),
            sa.Column("exercise_name", sa.String(length=255), nullable=False),
            sa.Column("variant_key", sa.String(length=128), nullable=True),
            sa.Column("variant_group", sa.String(length=128), nullable=True),
            sa.Column("equipment_family", sa.String(length=64), nullable=True),
            sa.Column("movement_pattern", sa.String(length=64), nullable=True),
            sa.Column("set_scheme", sa.String(length=255), nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("source_reason", sa.String(length=255), nullable=True),
            sa.UniqueConstraint(
                "user_program_session_id",
                "position",
                name="uq_user_program_exercise_position",
            ),
        )
        op.create_index(
            "ix_user_program_exercises_user_program_session_id",
            _EXERCISES,
            ["user_program_session_id"],
        )

    if not _table_exists(_REP_TARGETS):
        op.create_table(
            _REP_TARGETS,
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_program_exercise_id",
                sa.Integer(),
                sa.ForeignKey("user_program_exercises.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("set_index", sa.Integer(), nullable=False),
            sa.Column("min_reps", sa.Integer(), nullable=False),
            sa.Column("max_reps", sa.Integer(), nullable=False),
            sa.Column("technique", sa.String(length=8), nullable=True),
            sa.Column(
                "is_warmup", sa.Boolean(), nullable=False, server_default="0"
            ),
            sa.UniqueConstraint(
                "user_program_exercise_id",
                "set_index",
                "is_warmup",
                name="uq_user_program_rep_target_set",
            ),
        )
        op.create_index(
            "ix_user_program_rep_targets_user_program_exercise_id",
            _REP_TARGETS,
            ["user_program_exercise_id"],
        )


def downgrade() -> None:
    # Roundtrip contract: children first, empty and unconsumed at
    # downgrade time in the roundtrip check.
    if _table_exists(_REP_TARGETS):
        op.drop_index(
            "ix_user_program_rep_targets_user_program_exercise_id",
            table_name=_REP_TARGETS,
        )
        op.drop_table(_REP_TARGETS)
    if _table_exists(_EXERCISES):
        op.drop_index(
            "ix_user_program_exercises_user_program_session_id",
            table_name=_EXERCISES,
        )
        op.drop_table(_EXERCISES)
    if _table_exists(_SESSIONS):
        op.drop_index(
            "ix_user_program_sessions_user_program_id", table_name=_SESSIONS
        )
        op.drop_table(_SESSIONS)
