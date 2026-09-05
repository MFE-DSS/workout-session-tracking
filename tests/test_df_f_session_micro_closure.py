"""`DF-F` — micro-clôture de l'écran de séance : `D1`, `D2`, `D3`.

Trois décisions tranchées par l'opérateur sur des rendus mesurés, après le
registre d'arbitrage du 2026-08-29. Elles ne partagent pas un mécanisme : elles
partagent le fait d'avoir été **soumises puis tranchées**, et c'est la raison
pour laquelle elles voyagent ensemble.

  * `D1 = variante D` — le lien d'historique RÉPÉTÉ quitte les cartes repliées.
    Il y était dupliqué six fois pour un accès que la carte active porte déjà.
    Les VALEURS de la performance précédente et la puce restent : ce sont des
    données qu'on lit, pas une action qu'on déclenche.
  * `D2 = a` — la puce cesse d'annoncer `première fois` quand il y a bien eu
    une séance, sans valeurs saisies. Elle disait quelque chose de faux.
  * `D3 = B` — la commande dominante cesse d'employer des codes que `DF-C` a
    retirés partout ailleurs.

CE QUE CES GARDES DOIVENT AUSSI PROTÉGER — sur ordre explicite : `D9` et `D10`
restent EXACTEMENT en l'état. Aucune validation à la frappe ni au `blur`, et
aucun contrôle de sortie d'exercice supplémentaire pendant le repos. Deux
tranches les ont installés ; une troisième pourrait les défaire par mégarde en
« améliorant » le dock.
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
CARD = ROOT / "app/templates/_partials/exercise_card.html"
HISTORY_PATH = "/exercise-history/"
# Hoisté : écrit trois fois, il déclenchait `S1192`.
FIRST_SET = "first_set"
SESSIONS = "/sessions"


def _card() -> str:
    return re.sub(r"\{#.*?#\}", " ", CARD.read_text(encoding="utf-8"), flags=re.S)


def _session(client) -> int:
    r = client.post(SESSIONS, data={"template_slug": "push-a"},
                    follow_redirects=False)
    return int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


def _page(client, sid: int) -> str:
    return client.get(f"{SESSIONS}/{sid}").text


# ═════════ D1 — L'HISTORIQUE N'EST PLUS RÉPÉTÉ, ET RESTE ATTEIGNABLE ═════════


def test_the_history_link_is_not_repeated_on_collapsed_cards(client):
    """Un accès par carte, six fois, pour une action qu'on déclenche une fois.

    La garde compte : un seul lien d'historique doit être rendu, celui de
    l'exercice actif.
    """
    body = _page(client, _session(client))
    links = re.findall(rf'href="[^"]*{HISTORY_PATH}[^"]*"', body)
    assert len(links) == 1, (
        f"{len(links)} liens d'historique rendus — un seul est attendu, "
        "celui de l'exercice actif"
    )


def test_the_active_exercise_still_reaches_its_history(client):
    """`§5.3` — l'accès n'est pas supprimé, il cesse d'être répété."""
    body = _page(client, _session(client))
    assert f"{HISTORY_PATH}push-a/E1" in body, (
        "l'exercice actif n'expose plus son historique"
    )


def test_any_other_exercise_reaches_its_history_once_activated(client):
    """L'autre moitié de `§5.3`, et elle n'existe que grâce à `DF-E` :
    toucher une carte l'active, donc rend son historique disponible."""
    sid = _session(client)
    body = _page(client, sid)
    target = re.search(r'href="([^"]*\?active=\d+[^"]*)"', body)
    assert target, "aucun lien d'activation — voir `DF-E`"
    on_other = client.get(target.group(1).split("#", 1)[0]).text
    assert re.search(rf"{HISTORY_PATH}push-a/E\d", on_other), (
        "activer un autre exercice n'expose pas son historique"
    )


def test_the_previous_performance_values_stay_on_collapsed_cards(client):
    """Décision explicite : les VALEURS restent, le LIEN part. La puce résume
    le schéma et la date ; ce bloc porte les charges et les répétitions — ce
    ne sont pas les mêmes informations."""
    body = _page(client, _session(client))
    assert "last-time--compact" in body, (
        "« Dernière fois » a disparu des cartes repliées"
    )
    assert "exercise-card__chip" in body, "la puce a disparu"


# ═════════ D2 — LA PUCE CESSE D'ÉNONCER QUELQUE CHOSE DE FAUX ═════════


def test_a_prior_session_without_values_is_not_called_a_first_time():
    """LE DÉFAUT FERMÉ. `première fois` était renvoyé dans TROIS situations,
    dont deux où l'utilisateur était déjà venu."""
    from app.services.briefing import _last_time_chip

    assert _last_time_chip({FIRST_SET: {"weight_kg": None, "reps": None}}) == (
        "sans données"
    )
    assert _last_time_chip({FIRST_SET: {}}) == "sans données"
    assert _last_time_chip({}) == "première fois"


def test_a_genuine_first_time_is_still_called_a_first_time():
    """L'inverse compte autant : élargir un libellé ne doit pas l'étendre au
    cas qu'il décrivait correctement."""
    from app.services.briefing import _last_time_chip

    assert _last_time_chip(None) == "première fois"


def test_values_still_produce_the_values(client):
    from app.services.briefing import _last_time_chip

    chip = _last_time_chip({FIRST_SET: {"weight_kg": 60.0, "reps": 10}})
    assert "60" in chip
    assert "10" in chip


# ═════════ D3 — LE BOUTON NOMME CE QUE L'ÉCRAN MONTRE ═════════


def test_the_dominant_command_says_the_type_in_words():
    from app.services.console_state import build_console_state, command_for
    from tests.test_uiv3_session_console import _exercise

    warm = command_for(build_console_state(_exercise(), next_code=None))
    work = command_for(
        build_console_state(_exercise(warmups_done=1), next_code=None))
    # `R5`/`R6` — les libellés changent, L'INVARIANT DE `D3` NE CHANGE PAS :
    # la commande nomme le TYPE en toutes lettres. Épingler la chaîne exacte
    # protégeait une formulation ; ce qui compte est que le mot y soit.
    #
    # « VALIDER » a disparu parce que la saisie valide d'elle-même : le mot
    # annonçait une étape qui n'existe plus.
    assert "ÉCHAUFFEMENT" in warm["label"] or "SÉRIES" in warm["label"], warm
    assert "SÉRIE" in work["label"], work


def test_no_letter_code_survives_in_any_dominant_command():
    """LA PROPRIÉTÉ, pas les deux cas. `DF-C` a retiré `É`/`S` des lignes ;
    aucune commande ne doit les réintroduire."""
    from app.services.console_state import build_console_state, command_for
    from tests.test_uiv3_session_console import _exercise

    states = [
        _exercise(),
        _exercise(warmups_done=1),
        _exercise(warmups_done=1, works_done=3),
    ]
    for ex in states:
        label = command_for(build_console_state(ex, next_code="E2"))["label"]
        assert not re.search(r"\b[ÉS]\d", label), (
            f"code alphabétique dans une commande : {label!r}"
        )


# ═════════ D9 ET D10 — CE QUE CETTE TRANCHE NE DOIT PAS DÉFAIRE ═════════


def test_no_commit_on_typing_or_blur():
    """`D9` — le MOTIF est préservé, le déclencheur est amendé (`R5 = C`).

    Ce qui reste interdit, et pour les raisons d'origine : `input` partirait
    en cours de frappe — il enregistrerait « 7 » pendant qu'on tape « 70 » —
    et `blur` part quand le clavier se referme, ce qui n'est pas une
    intention.

    Ce qui est admis : `change`, qui **ne part que si la valeur a changé**.
    Relire ne le déclenche pas. Il dit « j'ai fini de saisir ce champ »,
    c'est-à-dire exactement l'intention que `D9` protégeait.
    """
    js = (ROOT / "app/static/js/session_focus.js").read_text(encoding="utf-8")
    stripped = re.sub(r"/\*[\s\S]*?\*/", " ", js)
    stripped = re.sub(r"(?m)^\s*//.*$", " ", stripped)
    for forbidden in ('"blur"', "'blur'", '"input"', "'input'"):
        assert forbidden not in stripped, (
            f"la validation implicite écoute {forbidden} — `D9` l'interdit"
        )
    assert "keydown" in stripped, "la transition explicite a disparu"


def test_no_extra_exercise_exit_during_rest():
    """`D10`, préservé à l'identique. Un troisième contrôle dans le dock du
    repos recréerait le « bouton de trop » que `DF-B` a supprimé."""
    from app.services.console_state import REST, ConsoleState, secondary_for

    kinds = {s["kind"] for s in secondary_for(ConsoleState(state=REST))}
    assert kinds == {"rest_minus", "rest_plus"}, (
        f"le dock du repos porte autre chose que les ajustements : {kinds}"
    )
