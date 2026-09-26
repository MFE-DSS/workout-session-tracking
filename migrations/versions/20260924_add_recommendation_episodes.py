"""REC-CP4 — table `recommendation_episodes`.

**Strictement additive.** Une seule table neuve, aucune colonne ajoutée à une
table existante, aucun DROP, aucun RENAME, aucun UPDATE de données historiques.

**Pourquoi une table plutôt qu'une colonne sur `workout_sessions`.**
`creation_source` dit d'où vient une séance CRÉÉE. Un épisode de recommandation
existe aussi quand aucune séance n'est créée, et il porte ce que la séance ne
peut pas porter : ce qui avait été PROPOSÉ. Le loger sur la séance rendrait
inexprimable le refus sans démarrage.

**Aucun backfill.** Aucun épisode n'a jamais été enregistré, et `creation_source`
ne dit pas quelle recommandation était affichée. Fabriquer des lignes
affirmerait une présentation que personne n'a observée.

**Trois états, un seul persisté** — même doctrine que
`plan_adaptation_dismissals` (`u2v7p3q4s15`). `UNRESOLVED` est l'absence de
ligne ; `RESOLVED` est la ligne ; `SUPERSEDED` est **dérivé** en comparant
l'empreinte de contexte à celle du moment. Il n'y a donc pas de colonne de
cycle de vie : elle serait la seule source possible d'un état périmé.

**Unicité `(user_id, context_fingerprint)`.** Deux rendus de la même décision
ne font pas deux mémoires, et un double envoi de formulaire est le même fait.
La contrainte est portée par la base, pas par la politesse des appelants.

Rétention : `ON DELETE CASCADE` sur le compte, comme `decision_traces`.

Idempotent (`_table_exists`) et downgrade symétrique, comme le reste du dépôt.

Revision ID: v3w8q4r5t16
Revises: u2v7p3q4s15
"""
import sqlalchemy as sa
from alembic import op

revision = "v3w8q4r5t16"
down_revision = "u2v7p3q4s15"
branch_labels = None
depends_on = None

_TABLE = "recommendation_episodes"
_IX = "ix_reco_episode_user_context"
_UQ = "uq_reco_episode_user_context"


def _table_exists(name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return name in inspector.get_table_names()


def upgrade() -> None:
    if _table_exists(_TABLE):
        return

    op.create_table(
        _TABLE,
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        # Identité de CONTENU du contexte : déterministe, sans horodatage,
        # dérivée des seules entrées que le moteur consomme.
        sa.Column("context_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("policy_version", sa.String(length=16), nullable=False),
        sa.Column("decided_at", sa.DateTime(), nullable=False),
        sa.Column(
            "resolved_at", sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False,
        ),
        sa.Column("proposed_top_slug", sa.String(length=64), nullable=False),
        sa.Column(
            "proposed_alt_slugs", sa.String(length=255),
            server_default="", nullable=False),
        sa.Column("outcome", sa.String(length=32), nullable=False),
        sa.Column("chosen_slug", sa.String(length=64), nullable=True),
        # Pas une clé étrangère : une séance supprimée ne doit pas effacer la
        # mémoire du conseil, qui reste un fait observé.
        sa.Column("session_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "context_fingerprint", name=_UQ),
    )
    op.create_index(
        _IX, _TABLE, ["user_id", "context_fingerprint"], unique=False)


def downgrade() -> None:
    if not _table_exists(_TABLE):
        return
    op.drop_index(_IX, table_name=_TABLE)
    op.drop_table(_TABLE)
