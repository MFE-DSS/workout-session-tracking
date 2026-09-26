"""UI-CP8R — la vérité temporelle du repos : deux colonnes sur `set_logs`.

**Strictement additive.** Deux colonnes nullables sur une table existante.
Aucun DROP, aucun RENAME, aucun UPDATE de données historiques.

**AUCUN BACKFILL, ET C'EST LE CŒUR DE LA TRANCHE.**

Une ligne existante porte `completed = 1` et `completed_at = NULL`. Cela se
lit, exactement :

    la série a été exécutée · l'heure d'exécution est inconnue.

Rien dans ce dépôt ne permet de reconstituer cette heure. Ni
`session.started_at` (elle date la SÉANCE, pas la série), ni l'ordre des
séries (il dit une succession, pas des instants), ni la durée de séance (elle
ne se répartit pas), ni un repos estimé (ce serait inventer la donnée que
cette migration existe pour arrêter d'inventer), ni les séries voisines
(elles n'ont pas d'heure non plus). Remplir ces colonnes fabriquerait une
chronologie que personne n'a observée, et l'état `REPOS` se dériverait alors
de temps imaginaires sur des séances vieilles de plusieurs mois.

`NULL` dit « on ne sait pas », et une séance historique ne rend jamais de
repos actif. C'est la seule lecture honnête.

**POURQUOI DEUX COLONNES ET NON UNE.**

`completed_at` est un FAIT (quand la série a été faite). `rest_dismissed_at`
est une DÉCISION (l'utilisateur a choisi de dépasser ce repos). Les fondre en
une échéance unique `rest_until` aurait rendu l'heure de complétion
déductible seulement par `rest_until − REST_FALLBACK_SECONDS`, c'est-à-dire
**à travers une constante de politique** : le jour où la politique change,
toute la chronologie historique glisse en silence. Vérité et politique ne
partagent pas une colonne.

**PORTÉE PAR SÉRIE, PAS PAR SÉANCE.** Une décision de repos appartient à la
transition qui l'a produite. Portée séance, corriger une vieille série
effacerait la décision prise sur la série courante.

Ceci est le sprint que `stay_redirect_target` nommait depuis `UI-CP2` :
`Sb_REST_EVENT_TRACE_01`, « un tracé durable exigerait une migration ».

Idempotent (`_has_column`) et downgrade symétrique, comme le reste du dépôt.

Revision ID: w4x9r5s6u17
Revises: v3w8q4r5t16
"""
import sqlalchemy as sa
from alembic import op

revision = "w4x9r5s6u17"
down_revision = "v3w8q4r5t16"
branch_labels = None
depends_on = None

_TABLE = "set_logs"
_COMPLETED_AT = "completed_at"
_REST_DISMISSED_AT = "rest_dismissed_at"


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if table not in inspector.get_table_names():
        return False
    return column in {c["name"] for c in inspector.get_columns(table)}


def upgrade() -> None:
    if not _has_column(_TABLE, _COMPLETED_AT):
        op.add_column(
            _TABLE,
            sa.Column(_COMPLETED_AT, sa.DateTime(timezone=True), nullable=True),
        )
    if not _has_column(_TABLE, _REST_DISMISSED_AT):
        op.add_column(
            _TABLE,
            sa.Column(
                _REST_DISMISSED_AT, sa.DateTime(timezone=True), nullable=True
            ),
        )
    # Aucun UPDATE. Voir la docstring : il n'existe aucune source honnête.


def downgrade() -> None:
    # Le retour arrière rend le produit au comportement `?rest=1` : le repos
    # redevient un signal de requête. Aucune donnée d'entraînement n'est
    # perdue — `completed`, poids et répétitions vivent dans d'autres
    # colonnes, intouchées. Ce qui disparaît est la chronologie fine, qui
    # n'existait pas avant cette migration.
    if _has_column(_TABLE, _REST_DISMISSED_AT):
        op.drop_column(_TABLE, _REST_DISMISSED_AT)
    if _has_column(_TABLE, _COMPLETED_AT):
        op.drop_column(_TABLE, _COMPLETED_AT)
