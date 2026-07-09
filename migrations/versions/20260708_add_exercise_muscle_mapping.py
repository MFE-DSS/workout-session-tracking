"""Sb_32.2 — ExerciseMuscleMapping + backfill from Sb_32.1 baseline.

Additive only (ADD TABLE ONLY contract, hérité Sx_26). No drop, no rename,
no UPDATE/DELETE of existing data. ONE new table:

  * CREATE TABLE exercise_muscle_mappings — la relation explicite
    exercice → zone (role primary/secondary). Backfillée depuis le
    **snapshot Sb_32.1** (`tests/fixtures/classify_exercise_baseline.json`)
    figé au moment du build.

Backfill : les lignes ci-dessous (``_BACKFILL_ROWS``) sont **générées à la
main-d'œuvre du build** à partir de la baseline Sb_32.1 (dédupliquée par nom
d'exercice — seule identité stable, cf. modèle). Elles ne sont **PAS** lues
depuis le fichier fixture au runtime (migration déterministe, sans dépendance
sur tests/). Un test compare ces lignes ↔ la baseline pour garantir la
synchronisation. `unknown` n'est jamais inséré → le fallback substring
conserve le comportement `unknown`.

Contract :
  - `exercise_code` = nom d'exercice (identité stable actuelle) → lookup DB
    et fallback substring keyés sur la même valeur → équivalence prouvable.
  - `role` ∈ {primary, secondary} en V1 ; stabilizer possible mais jamais
    inventé. `muscle_code` NULL (aucune anatomie fine inventée).
  - `position` : 0 pour la ligne primary, 1..n pour les secondary (préserve
    l'ordre historique déterministe).
  - Idempotent : guard `_table_exists` ; backfill conditionné à la création.
  - Aucun consommateur muté (bascule à un futur sous-sprint).

Revision ID: k2l7f3g4i65
Revises: j1k6e2f3h54
"""
from alembic import op
import sqlalchemy as sa

revision = "k2l7f3g4i65"
down_revision = "j1k6e2f3h54"
branch_labels = None
depends_on = None


# Static rows generated from the Sb_32.1 baseline at build time
# (NOT a runtime fixture import). Tuple = (exercise_code, body_zone_code, role).
# 65 primary + 22 secondary = 87 rows. Ordering preserved for `position`.
_BACKFILL_ROWS: list[tuple[str, str, str]] = [
    ("Adduction assise", "posterior", "primary"),
    ("Butterfly pec machine", "pecs", "primary"),
    ("Butterfly pec machine", "triceps", "secondary"),
    ("Cable cross-over (bas→haut)", "pecs", "primary"),
    ("Cable cross-over (bas→haut)", "triceps", "secondary"),
    ("Chest Press machine", "pecs", "primary"),
    ("Chest Press machine", "triceps", "secondary"),
    ("Crunch câble à genoux", "core", "primary"),
    ("Curl EZ-bar debout", "biceps", "primary"),
    ("Curl incliné haltères", "biceps", "primary"),
    ("Curl incliné haltères (banc 45°)", "biceps", "primary"),
    ("Curl marteau câble (corde)", "biceps", "primary"),
    ("Curl marteau haltères", "biceps", "primary"),
    ("Curl poulie basse", "biceps", "primary"),
    ("Curl poulie basse (barre)", "biceps", "primary"),
    ("Dips pectoraux (buste penché)", "pecs", "primary"),
    ("Dips pectoraux (buste penché)", "triceps", "secondary"),
    ("Développé couché haltères", "pecs", "primary"),
    ("Développé couché haltères", "triceps", "secondary"),
    ("Développé incliné haltères 30°", "pecs", "primary"),
    ("Développé incliné haltères 30°", "triceps", "secondary"),
    ("Extension overhead câble (corde)", "triceps", "primary"),
    ("Face pull câble", "delt_post", "primary"),
    ("Face pull câble (corde)", "delt_post", "primary"),
    ("Hack Squat machine", "quads", "primary"),
    ("Hip thrust Smith", "posterior", "primary"),
    ("Hip thrust Smith machine", "posterior", "primary"),
    ("Incline Smith Press", "pecs", "primary"),
    ("Incline Smith Press", "triceps", "secondary"),
    ("Kickback câble", "triceps", "primary"),
    ("Leg Press (pieds bas)", "quads", "primary"),
    ("Leg Press (pieds bas, serrés)", "quads", "primary"),
    ("Leg Press (pieds hauts, écartés)", "quads", "primary"),
    ("Leg curls allongé", "posterior", "primary"),
    ("Leg curls assis", "posterior", "primary"),
    ("Leg extensions assises", "quads", "primary"),
    ("Machine shoulder press", "delt_lat", "primary"),
    ("Mollets assis machine", "calves", "primary"),
    ("Neutral Grip Shoulder Press machine", "delt_lat", "primary"),
    ("Pallof press câble", "core", "primary"),
    ("Pullover câble (bras tendus)", "lats", "primary"),
    ("Pullover câble (bras tendus)", "biceps", "secondary"),
    ("Pullover câble (bras tendus, poulie haute)", "lats", "primary"),
    ("Pullover câble (bras tendus, poulie haute)", "biceps", "secondary"),
    ("Pullover machine", "lats", "primary"),
    ("Pullover machine", "biceps", "secondary"),
    ("Rear delt fly machine", "delt_post", "primary"),
    ("Rear delt fly machine (pec deck inversé)", "pecs", "primary"),
    ("Rear delt fly machine (pec deck inversé)", "triceps", "secondary"),
    ("Relevé de jambes suspendu", "calves", "primary"),
    ("Relevés mollets debout", "calves", "primary"),
    ("Relevés mollets debout machine", "calves", "primary"),
    ("Romanian Deadlift haltères", "posterior", "primary"),
    ("Roulette abdominale", "core", "primary"),
    ("Roulette abdominale (ab wheel rollout)", "core", "primary"),
    ("Rowing câble assis prise large", "upper_back", "primary"),
    ("Rowing câble assis prise large", "biceps", "secondary"),
    ("Rowing câble assis prise neutre", "upper_back", "primary"),
    ("Rowing câble assis prise neutre", "biceps", "secondary"),
    ("Rowing câble assis prise serrée", "upper_back", "primary"),
    ("Rowing câble assis prise serrée", "biceps", "secondary"),
    ("Rowing haltère un bras (banc)", "upper_back", "primary"),
    ("Rowing haltère un bras (banc)", "biceps", "secondary"),
    ("Rowing machine chest-supported", "upper_back", "primary"),
    ("Rowing machine chest-supported", "biceps", "secondary"),
    ("Shrugs haltères", "upper_back", "primary"),
    ("Shrugs haltères", "biceps", "secondary"),
    ("Skull crushers EZ-bar", "triceps", "primary"),
    ("Squat Smith machine (pieds avancés)", "quads", "primary"),
    ("Straight-arm pulldown câble", "lats", "primary"),
    ("Straight-arm pulldown câble", "biceps", "secondary"),
    ("Tirage front câble (prise large)", "delt_lat", "primary"),
    ("Tirage poulie haute prise large", "lats", "primary"),
    ("Tirage poulie haute prise large", "biceps", "secondary"),
    ("Tirage poulie haute prise neutre", "lats", "primary"),
    ("Tirage poulie haute prise neutre", "biceps", "secondary"),
    ("Tirage vertical unilatéral câble", "lats", "primary"),
    ("Tirage vertical unilatéral câble", "biceps", "secondary"),
    ("Triceps extension poulie haute (corde)", "triceps", "primary"),
    ("Triceps pushdown barre", "triceps", "primary"),
    ("Triceps pushdown corde", "triceps", "primary"),
    ("Écarté arrière d'épaule câble", "delt_post", "primary"),
    ("Écarté pec aux câbles (incliné bas→haut)", "pecs", "primary"),
    ("Écarté pec aux câbles (incliné bas→haut)", "triceps", "secondary"),
    ("Élévations latérales câble", "delt_lat", "primary"),
    ("Élévations latérales câble (derrière le dos)", "delt_lat", "primary"),
    ("Élévations latérales haltères assis", "delt_lat", "primary"),
]


def _table_exists(table: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table in set(inspector.get_table_names())


def _backfill_insert_rows() -> list[dict]:
    """Turn the static tuples into insert dicts, computing `position`
    per (exercise_code, role) group in declaration order."""
    rows: list[dict] = []
    sec_counter: dict[str, int] = {}
    for exercise_code, zone_code, role in _BACKFILL_ROWS:
        if role == "primary":
            position = 0
        else:
            n = sec_counter.get(exercise_code, 0) + 1
            sec_counter[exercise_code] = n
            position = n
        rows.append(
            {
                "exercise_code": exercise_code,
                "body_zone_code": zone_code,
                "muscle_code": None,
                "role": role,
                "source": "baseline",
                "position": position,
                "is_active": True,
            }
        )
    return rows


def upgrade() -> None:
    created = False
    if not _table_exists("exercise_muscle_mappings"):
        op.create_table(
            "exercise_muscle_mappings",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("exercise_code", sa.String(length=256), nullable=False),
            sa.Column(
                "body_zone_code",
                sa.String(length=64),
                sa.ForeignKey("body_zones.code", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "muscle_code",
                sa.String(length=64),
                sa.ForeignKey("muscles.code", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("role", sa.String(length=16), nullable=False),
            sa.Column("source", sa.String(length=16), nullable=False),
            sa.Column(
                "position", sa.Integer(), nullable=False, server_default="0"
            ),
            sa.Column(
                "is_active", sa.Boolean(), nullable=False, server_default="1"
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.UniqueConstraint(
                "exercise_code",
                "body_zone_code",
                "role",
                name="uq_exercise_muscle_mapping",
            ),
        )
        op.create_index(
            "ix_exercise_muscle_mapping_exercise",
            "exercise_muscle_mappings",
            ["exercise_code"],
        )
        op.create_index(
            "ix_exercise_muscle_mapping_zone",
            "exercise_muscle_mappings",
            ["body_zone_code"],
        )
        created = True

    if created:
        table = sa.table(
            "exercise_muscle_mappings",
            sa.column("exercise_code", sa.String),
            sa.column("body_zone_code", sa.String),
            sa.column("muscle_code", sa.String),
            sa.column("role", sa.String),
            sa.column("source", sa.String),
            sa.column("position", sa.Integer),
            sa.column("is_active", sa.Boolean),
        )
        op.bulk_insert(table, _backfill_insert_rows())


def downgrade() -> None:
    if _table_exists("exercise_muscle_mappings"):
        op.drop_index(
            "ix_exercise_muscle_mapping_zone",
            table_name="exercise_muscle_mappings",
        )
        op.drop_index(
            "ix_exercise_muscle_mapping_exercise",
            table_name="exercise_muscle_mappings",
        )
        op.drop_table("exercise_muscle_mappings")
