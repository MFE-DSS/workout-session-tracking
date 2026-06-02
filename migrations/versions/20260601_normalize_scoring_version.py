"""Sb_24.5.cleanup — bump scoring_version to 2 on all completed sessions.

Option C choisie en revue humaine après Sb_24.5 : aligner le flag
scoring_version sur 2 pour TOUTES les sessions terminées, y compris
historiques. Choix purement cosmétique — la formule V2 fallback
exactement sur V1 quand aucun exercice de la session n'a
d'implicit_label (cas systématique pour les sessions terminées AVANT
le déploiement Sb_24.3 du 2026-05-31 ~22h UTC).

Conséquence sur les valeurs affichées : **aucune**. Le score V1 et le
score V2 d'une session sans label sont mathématiquement identiques
(V2 = 0.75·V1 + 0.25·implicit_avg, et si implicit_avg est None on
retombe sur V1 inchangé, cf services/quality_score.py).

Bénéfice : downstream Sb_24.6/7/8 n'ont plus à gérer deux cas
"V1 historique" vs "V2 récent" pour la même fenêtre temporelle. La
métrique est uniforme.

Le hook _persist_implicit_labels_on_completion (Sb_24.3) continue à
gérer correctement les sessions in_progress : il fait son propre
bump 1→2 à la complétion. Cette migration ne touche QUE les sessions
déjà completed.

Revision ID: 5g8d3b9c0e21
Revises: 4f7c2a8b9d10
"""
from alembic import op


revision = "5g8d3b9c0e21"
down_revision = "4f7c2a8b9d10"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "UPDATE workout_sessions "
        "SET scoring_version = 2 "
        "WHERE scoring_version = 1 AND status = 'completed'"
    )


def downgrade() -> None:
    # Revient à scoring_version=1 UNIQUEMENT pour les sessions qui n'ont
    # aucun implicit_label sur leurs exercices — c'est-à-dire celles que
    # la migration upgrade a bumpées. Les sessions véritablement V2
    # (celles qui ont au moins un exercice labellé) restent à 2.
    op.execute(
        "UPDATE workout_sessions "
        "SET scoring_version = 1 "
        "WHERE scoring_version = 2 "
        "  AND status = 'completed' "
        "  AND id NOT IN ("
        "    SELECT DISTINCT session_id FROM session_exercises "
        "    WHERE implicit_label IS NOT NULL"
        "  )"
    )
