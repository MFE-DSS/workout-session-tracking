"""CP-0 — `/profile` ne dépense plus de requêtes pour personne.

⚠ POURQUOI CETTE GARDE EXISTE, ET POURQUOI ELLE COMPTE DES REQUÊTES.

Le routeur du Profil construisait **19 clés de contexte ; le gabarit en lit 9**.
Les dix autres — `session_count`, `completed_count`, `quality_svg`,
`sessions_30d_count`, `trend`, `trend_label`, `measurement_charts`,
`measurement_labels`, `measurement_fields`, `related_templates` — étaient
calculées à chaque affichage et lues par personne. Mesuré : **22 requêtes SQL
sur 27**, dont dix courbes SVG, un chargement de 30 jours de séances en cascade
`selectinload`, et **la table des templates en entier**.

**Ce n'était pas une découverte : c'était une récidive.** Le même défaut, sur la
même route, est déjà documenté dans le routeur sous `UX4_03B` — « `UX4_01` a
retiré les modules analytiques du Profil sans retirer le calcul qui les
alimentait ». Il est revenu parce que **rien ne le surveillait**.

**Et rien ne le surveillait au sens fort** : aucun test du dépôt n'observait ces
dix clés. Le retrait a été joué sur 44 fichiers, 1 348 tests — **zéro échec**.
Un défaut invisible à toute une suite revient une troisième fois.

D'où le choix de compter des REQUÊTES plutôt que d'analyser le contexte :

* une analyse statique « clé de contexte non lue » serait **peu fiable ici** —
  `base.html` lit `active_session`, qu'un balayage du seul `profile.html`
  déclarerait morte ;
* le compte de requêtes mesure ce que la route **fait**, pas ce qu'elle déclare.

⚠ CE N'EST PAS UN JUGEMENT DE PERFORMANCE. Ce cliquet borne une dérive ; il ne
prononce pas que la route est optimale. Un budget respecté ne veut pas dire que
les requêtes restantes sont nécessaires.
"""
from __future__ import annotations

import pytest
from sqlalchemy import event

from tests.helpers import get_test_user_id

PROFILE_URL = "/profile"

#: Budget de requêtes de `GET /profile`, gelé par `CP-0`.
#:
#: ⚠ STRICT, ET MESURÉ — pas estimé. Les **quatre** combinaisons de chemin
#: (avec/sans mesure × avec/sans séance ouverte) rendent **exactement 5**
#: requêtes. Aucune marge n'est donc justifiée par une variation observée.
#:
#: Un premier jet posait 12 « pour la marge ». C'était vide de sens : le plus
#: petit module retiré, `related_templates`, ne coûte QU'UNE requête — un
#: budget lâche l'aurait laissé revenir sans un mot. Une marge qu'aucune mesure
#: ne réclame n'est pas de la prudence, c'est un cliquet qui ne serre rien.
#:
#: Les 5 qui restent, et pourquoi chacune est là :
#:   · la session d'authentification              (`services/auth.py`)
#:   · le read-model morphologique                (`build_morphology_readmodel`, ×2)
#:   · la dernière mesure                         (`get_latest_measurement`)
#:   · la séance ouverte                          (`latest_open_session`, lue
#:                                                  par `base.html`)
#:
#: **Relever ce nombre est une décision, pas un ajustement.** Une requête neuve
#: et légitime met à jour cette ligne DANS LE MÊME COMMIT, avec sa raison. Le
#: pire cas mesuré avant `CP-0` était **27**.
BUDGET_PROFILE = 5


def _compter_requetes(fn) -> list[str]:
    """Les requêtes émises pendant `fn`, dans l'ordre.

    Même idiome que `test_recovery_home_consumer._count_queries` — repris et
    non réécrit : deux compteurs de requêtes qui divergent finiraient par
    mesurer deux choses différentes sous le même nom.
    """
    from app.database import engine

    vues: list[str] = []

    def ecouteur(_conn, _cursor, statement, *_a, **_k):
        vues.append(statement)

    event.listen(engine, "before_cursor_execute", ecouteur)
    try:
        fn()
    finally:
        event.remove(engine, "before_cursor_execute", ecouteur)
    return vues


def _avec_mesure(uid: int) -> None:
    from datetime import UTC, datetime

    from app.database import SessionLocal
    from app.models.measurement import BodyMeasurement

    with SessionLocal() as db:
        db.add(BodyMeasurement(
            user_id=uid, measured_at=datetime.now(UTC),
            weight_kg=75.4, waist_cm=81.0, chest_cm=104.0,
        ))
        db.commit()


def _avec_seance_ouverte(uid: int) -> None:
    """`latest_open_session` est un chemin distinct, et `base.html` le lit.

    Sans ce cas, le budget serait gelé sur un utilisateur qui n'a jamais de
    séance en cours — et la première séance ouverte le ferait rougir pour une
    raison légitime.
    """
    from datetime import UTC, datetime

    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    with SessionLocal() as db:
        db.add(WorkoutSession(
            user_id=uid, status="in_progress", started_at=datetime.now(UTC),
            template_slug_snapshot="push-a", template_name_snapshot="Push A",
            excluded_from_stats=False,
        ))
        db.commit()


@pytest.mark.parametrize(
    ("avec_mesures", "avec_seance"),
    [(False, False), (True, False), (False, True), (True, True)],
    ids=["nu", "mesure", "seance", "mesure_et_seance"],
)
def test_le_profil_reste_dans_son_budget_de_requetes(
    client, avec_mesures, avec_seance
):
    """Les QUATRE combinaisons de chemin, parce qu'ils divergent.

    `latest_values` n'est peuplé que si `get_latest_measurement` rend quelque
    chose (branche `if latest_measurement:`), et `latest_open_session` est une
    lecture séparée que `base.html` consomme. Geler le budget sur un seul
    chemin laisserait les trois autres sans garde — et ferait rougir la route
    pour une raison légitime le jour où l'utilisateur ouvre une séance.
    """
    uid = get_test_user_id()
    if avec_mesures:
        _avec_mesure(uid)
    if avec_seance:
        _avec_seance_ouverte(uid)

    requetes = _compter_requetes(lambda: client.get(PROFILE_URL))
    assert len(requetes) <= BUDGET_PROFILE, (
        f"GET /profile émet {len(requetes)} requêtes, budget {BUDGET_PROFILE}.\n"
        "Un module analytique a probablement été rebranché sans consommateur — "
        "c'est exactement `UX4_03B`, pour la troisième fois.\n"
        + "\n".join(f"  · {q.split(chr(10))[0][:100]}" for q in requetes)
    )


def test_le_profil_repond_toujours(client):
    """Un budget respecté par une page cassée ne garde rien.

    Sans cette garde, remplacer le corps de la route par `return 500` ferait
    passer le test de budget — le compteur mesurerait zéro requête.
    """
    r = client.get(PROFILE_URL)
    assert r.status_code == 200
    assert "Profil" in r.text


def test_le_compteur_voit_bien_des_requetes(client):
    """Une garde qui ne mesure rien ne garde rien.

    Si l'écouteur cesse d'être branché — changement de moteur, fixture qui
    remplace `engine` — le compte tomberait à zéro et le budget passerait
    silencieusement. Cette garde exige que le compteur voie quelque chose.
    """
    requetes = _compter_requetes(lambda: client.get(PROFILE_URL))
    assert requetes, (
        "le compteur n'a vu AUCUNE requête sur /profile — l'écouteur n'est pas "
        "branché sur le bon moteur, et le budget ne mesure plus rien"
    )
