"""Une anomalie qu'on ne sait pas nommer n'est pas une information.

POURQUOI CETTE GARDE EXISTE
---------------------------
`/progress` affichait, sur un compte avec données :

    ANOMALIE None  voir la séance

`_pick_top_anomaly` lisait **quatre attributs qui n'existent pas** sur
`Anomaly` — `code`, `label`, `session_exercise_id`, et par ricochet le nom de
l'exercice. La classe porte `exercise_code`, `rule_code`, `severity`,
`message` et `context`, et rien d'autre.

Les `getattr(..., None)` rendaient l'absence **silencieuse** : aucune
exception, un dict bien formé, et le gabarit — `{{ label or code }}` —
imprimait `None or None`, c'est-à-dire la chaîne « None ».

**Toute anomalie jamais affichée sur cette surface l'a donc été sous le nom
« Anomalie None ».** Le lecteur ne pouvait pas savoir laquelle.

C'est le motif que ce dépôt a déjà nommé : *un repli défensif sur un contexte
manquant produit un objet vert et sans comportement*. Et il a été trouvé en
REGARDANT l'écran — aucune des 5 000 gardes ne comparait un rendu à un mot
lisible.
"""

from __future__ import annotations

import pytest

from app.services.anomalies import Anomaly
from app.services.weekly_loop import _exercise_name_for, _pick_top_anomaly


class _SE:
    def __init__(self, code, name, sub=None):
        self.exercise_code_snapshot = code
        self.exercise_name_snapshot = name
        self.substituted_name = sub


class _Session:
    id = 42
    template_name_snapshot = "Push A — Pecs"

    def __init__(self, exercises):
        self.session_exercises = exercises


def _anomaly(**kw):
    base = {
        "exercise_code": "BENCH",
        "rule_code": "C",
        "severity": "info",
        "message": "+25% de charge vs dernière fois. Volontaire ?",
    }
    base.update(kw)
    return Anomaly(**base)


def test_the_anomaly_object_has_no_code_or_label_attribute():
    """LA CAUSE, épinglée.

    Si `Anomaly` gagnait un jour un vrai `label`, ce test échouerait — et ce
    serait le bon moment pour simplifier le producteur. Tant qu'il ne l'a pas,
    quiconque écrit `anomaly.label` écrit `None`.
    """
    a = _anomaly()
    assert not hasattr(a, "label"), "Anomaly a désormais un `label` — simplifier"
    assert not hasattr(a, "code"), "Anomaly a désormais un `code` — simplifier"
    assert not hasattr(a, "session_exercise_id")


def test_a_surfaced_anomaly_always_carries_a_readable_label(monkeypatch):
    """LE DÉFAUT D'ORIGINE, énoncé comme propriété du rendu.

    Ce qui compte n'est pas quel champ est lu, mais qu'un humain puisse lire
    le résultat. Épingler `message` protégerait une implémentation ; épingler
    « le libellé est un mot, pas `None` » protège l'utilisateur.
    """
    session = _Session([_SE("BENCH", "Développé couché")])
    monkeypatch.setattr(
        "app.services.anomalies.compute_anomalies", lambda s: [_anomaly()]
    )
    top = _pick_top_anomaly([session])
    assert top is not None, "l'anomalie a disparu"
    assert top["label"], "libellé vide"
    assert top["label"] != "None", "le libellé rend la chaîne « None »"
    assert "None" not in str(top["label"]), top["label"]


def test_an_unnameable_anomaly_is_dropped_rather_than_shown_empty(monkeypatch):
    """Taire vaut mieux qu'afficher un objet vide.

    Une anomalie sans message ET sans code ne dit rien à personne. La
    précédente version l'affichait quand même — c'est ainsi que « None » est
    arrivé à l'écran.
    """
    session = _Session([_SE("BENCH", "Développé couché")])
    monkeypatch.setattr(
        "app.services.anomalies.compute_anomalies",
        lambda s: [_anomaly(message="", rule_code="")],
    )
    assert _pick_top_anomaly([session]) is None


def test_the_exercise_name_is_actually_resolved(monkeypatch):
    """Le nom de l'exercice était TOUJOURS absent.

    La recherche passait par `session_exercise_id`, qui n'existe pas : la
    boucle ne s'exécutait jamais. Rien ne le signalait, puisque `None` est un
    nom d'exercice acceptable pour un gabarit qui teste sa présence.
    """
    session = _Session([_SE("BENCH", "Développé couché")])
    monkeypatch.setattr(
        "app.services.anomalies.compute_anomalies", lambda s: [_anomaly()]
    )
    top = _pick_top_anomaly([session])
    assert top["exercise_name"] == "Développé couché"


def test_the_substituted_name_wins():
    """Si l'exercice a été remplacé, l'anomalie porte sur ce qui a été FAIT."""
    session = _Session([_SE("BENCH", "Développé couché", sub="Développé incliné")])
    assert _exercise_name_for(session, _anomaly()) == "Développé incliné"


@pytest.mark.parametrize("code", [None, ""])
def test_an_anomaly_without_exercise_code_names_no_exercise(code):
    """Aucune invention : sans lien, pas de nom."""
    session = _Session([_SE("BENCH", "Développé couché")])
    assert _exercise_name_for(session, _anomaly(exercise_code=code)) is None
