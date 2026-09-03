"""`Sx_CI_TIME_BOMB_GUARD_01` — un test ne doit pas expirer tout seul.

CE QUE CETTE GARDE FERME
------------------------
Le 2026-09-03 à minuit UTC, la CI canonique est tombée (run 33732658392) sans
qu'aucun commit n'ait touché ni le produit ni les tests concernés. Cause :

    NOW = datetime(2026, 8, 21, 12, 0, tzinfo=UTC)   # ancrage GELÉ
    _session(db, uid, days_ago=2)                    # donnée au 2026-08-19
    client.get("/progress")                          # la route lit l'heure RÉELLE
    WINDOW_DAYS = 14                                 # fenêtre depuis 2026-08-20

La donnée est sortie de la fenêtre glissante. **Une bombe posée dix-neuf jours
plus tôt**, dans un test qui était vert le jour où il a été écrit et resté vert
jusqu'à l'instant où il ne pouvait plus l'être.

POURQUOI UNE GARDE, ET PAS SEULEMENT LE CORRECTIF
-------------------------------------------------
Corriger les deux fichiers ne coûte rien et ne protège rien : le motif est
facile à réintroduire, et il ne se voit pas à la relecture — il se voit des
semaines plus tard, sur une canonique rouge, un jour où personne ne cherche
ça. C'est exactement le profil de défaut que `CLAUDE.md §1` demande de fermer
par une garde plutôt que par de la vigilance.

CE QU'ELLE N'INTERDIT PAS
-------------------------
Une date littérale reste légitime quand le test **injecte** cet instant dans le
code appelé (`build_zone_exposure(db, uid, now=NOW)`) : rien n'y lit l'horloge,
donc rien ne dérive. La garde ne mord que sur la combinaison **ancrage gelé +
appel à une vraie route**, la seule où l'horloge du produit et celle du test
peuvent s'éloigner.
"""
from __future__ import annotations

import pathlib
import re

TESTS = pathlib.Path(__file__).resolve().parent

#: Un nom de module qui sert manifestement d'ancrage temporel.
_ANCHOR = re.compile(
    r"^\s*(NOW|_NOW|TODAY|ANCHOR|REF_DATE|BASE_DATE)\s*=\s*datetime\(\s*\d{4}\s*,",
    re.M,
)
#: Un appel à une vraie route : le client HTTP rend une page qui, elle, lit
#: `datetime.now()` sans que le test puisse l'injecter.
_REAL_ROUTE = re.compile(r"\bclient\.(get|post|put|delete)\(")


def _offenders() -> list[str]:
    bad = []
    for path in sorted(TESTS.rglob("test_*.py")):
        if path.name == pathlib.Path(__file__).name:
            continue
        src = path.read_text(encoding="utf-8", errors="ignore")
        if _ANCHOR.search(src) and _REAL_ROUTE.search(src):
            bad.append(path.name)
    return bad


def test_no_test_file_combines_a_frozen_anchor_with_a_real_route():
    """LA GARDE. Une date littérale + une vraie route = une date d'expiration.

    Le correctif est d'une ligne : ancrer sur l'horloge au lieu d'une date.

        NOW = datetime.now(UTC).replace(hour=12, minute=0, second=0, microsecond=0)

    Le déterminisme DANS un run est préservé — l'horloge est lue une fois, au
    chargement du module — et la distance à la fenêtre glissante reste
    constante d'un jour à l'autre.
    """
    offenders = _offenders()
    assert offenders == [], (
        "ancrage temporel GELÉ combiné à un appel de route réelle dans : "
        + ", ".join(offenders)
        + " — ces tests expireront d'eux-mêmes quand la dérive dépassera la "
        "fenêtre du produit. Ancrer sur `datetime.now(UTC)`."
    )


def test_the_guard_would_catch_the_defect_it_was_written_for(tmp_path):
    """⚠ Une garde verte ne prouve rien tant qu'on ne l'a pas vue rougir.

    On reconstruit ici le fichier fautif TEL QU'IL ÉTAIT le 2026-09-03, et on
    vérifie que les deux motifs sont bien détectés — séparément, pour qu'un
    faux positif sur l'un ne masque pas l'absence de l'autre.
    """
    coupable = (
        "from datetime import UTC, datetime\n"
        "NOW = datetime(2026, 8, 21, 12, 0, tzinfo=UTC)\n"
        "def test_x(client):\n"
        "    r = client.get('/progress')\n"
    )
    assert _ANCHOR.search(coupable), "l'ancrage gelé n'est pas détecté"
    assert _REAL_ROUTE.search(coupable), "l'appel de route n'est pas détecté"

    sain = (
        "from datetime import UTC, datetime\n"
        "NOW = datetime.now(UTC).replace(hour=12)\n"
        "def test_x(client):\n"
        "    r = client.get('/progress')\n"
    )
    assert not _ANCHOR.search(sain), (
        "l'ancrage FLOTTANT est signalé à tort — la garde interdirait le correctif"
    )


def test_an_injected_instant_stays_allowed():
    """Le cas légitime doit rester légitime, sinon la garde pousse à contourner.

    Un test de service qui passe `now=` n'a aucune dérive possible : le code
    appelé ne lit pas l'horloge. Ce fichier-ci en est la preuve vivante — il
    n'appelle aucune route, donc il ne déclenche pas la garde.
    """
    service_only = (
        "from datetime import UTC, datetime\n"
        "NOW = datetime(2026, 8, 21, 12, 0, tzinfo=UTC)\n"
        "def test_x():\n"
        "    build_zone_exposure(db, uid, now=NOW)\n"
    )
    assert _ANCHOR.search(service_only)
    assert not _REAL_ROUTE.search(service_only), (
        "un test de service pur ne doit pas être vu comme appelant une route"
    )
