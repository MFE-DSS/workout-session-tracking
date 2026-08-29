"""`DF-E` — ouvrir un exercice, c'est l'activer. Les deux ne divergent plus.

CE QUE CETTE TRANCHE FERME
---------------------------
Trois notions étaient portées par un seul contrôle :

  * « carte dépliée »   — `<details open>`, que n'importe quel toucher
    changeait **côté client**, sans rien demander au serveur ;
  * « exercice actif »  — `?active=<id>`, décidé par le serveur seul, et qui
    gouverne **tout** : lignes saisissables, commande dominante, `Adapter` ;
  * « je veux travailler ici » — que rien n'exprimait.

Toucher une carte repliée satisfaisait la première et pas la seconde. On
obtenait alors une **seconde interface** pour le même exercice : liste plate,
libellés `Échauf. #1` / `Série #2` que `Q4` puis `DF-C` avaient remplacés,
aucun `Adapter`, aucune validation implicite. Laquelle des deux on obtenait
dépendait du **chemin d'arrivée**.

LA NATURE DE CES GARDES
-----------------------
Elles ne surveillent pas le défaut : elles vérifient que la **structure** qui
le rendait exprimable a disparu. Dans une séance en cours, il n'existe plus
qu'un seul `<details>` d'exercice — l'actif. Les autres sont des liens. L'état
« ouvert mais pas actif » n'a plus de représentation possible.

Deux gardes existent quand même pour ce que la structure ne peut pas garantir
seule : que **tout** chemin d'arrivée demande l'activation, et que la séance
**terminée** conserve sa liste de relecture — la retirer aurait été une
soustraction (`CLAUDE.md §5.3`).
"""
from __future__ import annotations

import re

# Hoistés : chacun était écrit trois fois et déclenchait `S1192`. Le pré-scan
# AST les voit avant Sonar — la faute de méthode de `DF-B` ne se répète pas.
ANCHOR_A = r"<a\b[^>]*\b"
SESSIONS = "/sessions"
LOCATION = "location"

ACTIVATE = "exercise-card--activate"
FLAT_LIST = "set-list--compact"
LEGACY_KIND = "set-row__kind"


def _session(client) -> int:
    r = client.post(SESSIONS, data={"template_slug": "push-a"},
                    follow_redirects=False)
    return int(re.match(r"/sessions/(\d+)", r.headers[LOCATION]).group(1))


def _page(client, sid: int, active: int | None = None) -> str:
    suffix = f"?active={active}" if active is not None else ""
    return client.get(f"{SESSIONS}/{sid}{suffix}").text


def _exercises(sid: int) -> list[int]:
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import SessionExercise

    with SessionLocal() as db:
        rows = db.execute(
            select(SessionExercise)
            .where(SessionExercise.session_id == sid)
            .order_by(SessionExercise.position.asc())
        ).scalars().all()
        return [se.id for se in rows]


# ═════════ 1. LA STRUCTURE QUI RENDAIT LE DÉFAUT POSSIBLE A DISPARU ═════════


def test_only_the_active_exercise_is_a_disclosure(client):
    """LA GARDE DE FOND. Un seul `<details>` d'exercice : l'actif.

    Tant que les sept cartes étaient des `<details>`, l'utilisateur pouvait en
    ouvrir une sans que le serveur l'active. Ce n'est plus représentable.
    """
    body = _page(client, _session(client))
    cards = re.findall(
        r'<details\b[^>]*\bclass="[^"]*\bcard\s+exercise-card\b[^"]*"', body)
    assert len(cards) == 1, f"{len(cards)} cartes dépliables au lieu d'une"


def test_every_other_exercise_is_an_activation_link(client):
    sid = _session(client)
    body = _page(client, sid)
    links = re.findall(rf'{ANCHOR_A}{ACTIVATE}\b[^>]*>', body)
    assert len(links) == len(_exercises(sid)) - 1, (
        f"{len(links)} liens d'activation pour {len(_exercises(sid))} exercices"
    )


def test_each_activation_link_asks_the_server_to_activate(client):
    """Une ancre seule fait défiler sans rien activer — c'est le défaut."""
    sid = _session(client)
    body = _page(client, sid)
    hrefs = re.findall(rf'{ANCHOR_A}{ACTIVATE}\b[^>]*href="([^"]+)"', body)
    assert hrefs, "aucun lien d'activation — la garde ne mesure rien"
    for href in hrefs:
        assert "active=" in href, f"lien d'activation sans activation : {href!r}"


def test_the_header_selector_activates_too(client):
    """L'autre chemin d'arrivée. Il portait `href="#exercise-N"` : une ancre
    pure, qui nommait une action qu'elle n'accomplissait pas."""
    body = _page(client, _session(client))
    hrefs = re.findall(rf'{ANCHOR_A}ex-jump__item\b[^>]*href="([^"]+)"', body)
    targeted = [h for h in hrefs if "#exercise-" in h]
    assert targeted, "le sélecteur ne vise aucun exercice"
    for href in targeted:
        assert "active=" in href, f"entrée de sélecteur sans activation : {href!r}"


def test_the_second_interface_is_gone_from_a_live_session(client):
    """La liste plate et ses libellés `Échauf. #1` ne sont plus rendus dans
    une séance en cours — ils n'existaient que sur la carte non active."""
    body = _page(client, _session(client))
    assert FLAT_LIST not in body, "la liste plate est encore rendue"
    assert LEGACY_KIND not in body, "les libellés de l'ancienne interface sont là"


# ═════════ 2. CE QUE LA STRUCTURE NE GARANTIT PAS SEULE ═════════


def _follow_to(client, body: str, se_id: int) -> str:
    """Suit un CONTRÔLE RÉELLEMENT RENDU qui mène à cet exercice.

    ⚠ CETTE INDIRECTION EST TOUT L'INTÉRÊT. Mes deux premières versions de
    `test_coming_back_…` et `test_adapter_…` fabriquaient l'URL `?active=N`
    elles-mêmes. Or le routeur a **toujours** honoré ce paramètre : le défaut
    n'a jamais été là. Il était qu'AUCUN CONTRÔLE NE PRODUISAIT CETTE URL.

    Vérifié en plantant : avec l'activation intégralement rétablie à l'ancien
    comportement, ces deux gardes restaient **VERTES**. Elles affirmaient une
    propriété déjà vraie. Elles ne gardaient rien.

    On part donc du HTML, on cherche un lien qui vise cet exercice, et on le
    suit. S'il n'existe pas, la garde échoue — et c'est exactement le défaut.
    """
    hrefs = re.findall(rf'href="([^"]*#exercise-{se_id})"', body)
    assert hrefs, (
        f"aucun contrôle rendu ne mène à l'exercice {se_id} — "
        "c'est précisément le défaut que `DF-E` ferme"
    )
    url = hrefs[0].split("#", 1)[0]
    assert url, f"le contrôle vers {se_id} est une ancre pure : {hrefs[0]!r}"
    return client.get(url).text


def test_coming_back_to_an_exercise_makes_it_truly_active(client):
    """LE POINT 7, DE BOUT EN BOUT, ET PAR LES CONTRÔLES.

    Aller sur E2 en suivant ce que l'écran propose, revenir sur E1 de même :
    E1 doit être **utilisable**, pas seulement ouvert.
    """
    sid = _session(client)
    first, second = _exercises(sid)[0], _exercises(sid)[1]

    start = _page(client, sid)
    on_second = _follow_to(client, start, second)
    assert f'id="exercise-{second}"' in on_second, "E2 n'est pas rendu"
    assert "data-console-state" in on_second, "E2 n'a pas de console"

    back = _follow_to(client, on_second, first)
    assert "data-console-state" in back, "E1 n'a pas de console au retour"
    assert "setline--current" in back, "aucune ligne courante au retour"
    inputs = re.findall(r'<input[^>]*name="set_\d+_reps"[^>]*>', back)
    visible = [i for i in inputs if 'type="hidden"' not in i]
    assert visible, "aucun champ saisissable au retour sur l'exercice"


def test_adapter_survives_the_detour(client):
    """LE POINT 8, PAR LES CONTRÔLES AUSSI.

    `can_substitute` est une règle de DONNÉES — « aucune série de travail
    complétée » — et elle ne dépend d'aucune navigation. `Adapter` disparaissait
    pourtant après un détour : non parce que la règle changeait, mais parce
    qu'il n'était rendu que sur la carte active et qu'on ne savait plus la
    redevenir.
    """
    sid = _session(client)
    first, second = _exercises(sid)[0], _exercises(sid)[1]

    start = _page(client, sid)
    assert "substitute-picker__summary" in start, "`Adapter` absent au départ"

    detour = _follow_to(client, start, second)
    back = _follow_to(client, detour, first)
    assert "substitute-picker__summary" in back, (
        "`Adapter` a disparu après un détour, alors qu'aucune série de travail "
        "n'a été faite"
    )


def test_the_substitution_rule_itself_is_not_weakened(client):
    """L'inverse de la garde précédente, et elle compte autant : `Adapter`
    doit TOUJOURS disparaître une fois une série de travail faite. Rendre la
    capacité plus durable ne doit pas la rendre permanente."""
    from app.services.substitution import can_substitute

    sid = _session(client)
    first = _exercises(sid)[0]
    _page(client, sid, active=first)

    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog

    with SessionLocal() as db:
        work = db.execute(
            select(SetLog)
            .where(SetLog.session_exercise_id == first, SetLog.kind == "work")
            .order_by(SetLog.set_index.asc()).limit(1)).scalar_one()
        work.completed = True
        db.commit()
        se = db.execute(
            select(SessionExercise).where(SessionExercise.id == first)
        ).scalar_one()
        assert can_substitute(se) is False, (
            "la règle de substitution a été affaiblie"
        )


def test_a_completed_session_goes_to_its_own_recap(client):
    """La relecture d'une séance terminée a sa PROPRE page.

    ⚠ J'avais écrit l'inverse : « la séance terminée garde sa liste plate,
    c'est sa surface de relecture », et j'avais posé une condition
    `status != 'completed'` dans le gabarit pour la protéger. **Faux.** Mesuré :
    la page de séance REDIRIGE (303) vers `/sessions/{id}/done`, qui n'inclut
    pas ce gabarit. Ma condition n'était donc jamais évaluée, et la liste plate
    n'a jamais servi à relire quoi que ce soit.

    La garde énonce désormais ce qui est vrai, et elle a une valeur propre :
    si cette redirection disparaissait, une séance terminée retomberait sur la
    page d'exécution — où tout serait activable alors qu'il n'y a plus rien à
    exécuter.
    """
    sid = _session(client)
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    with SessionLocal() as db:
        s = db.get(WorkoutSession, sid)
        s.status = "completed"
        db.commit()

    r = client.get(f"{SESSIONS}/{sid}", follow_redirects=False)
    assert r.status_code == 303, f"séance terminée : {r.status_code}, pas 303"
    assert r.headers[LOCATION].endswith("/done"), r.headers[LOCATION]
    assert ACTIVATE not in _page(client, sid), (
        "une séance terminée n'a rien à activer"
    )


def test_reaching_another_exercise_survives_the_rest_state(client):
    """Le repos est un état où l'écran se tait — mais pas au point d'enfermer.
    Les autres exercices restent atteignables pendant le décompte."""
    sid = _session(client)
    first = _exercises(sid)[0]
    body = client.get(f"{SESSIONS}/{sid}?active={first}&rest=1").text
    assert ACTIVATE in body, "aucun exercice atteignable pendant le repos"


def test_activation_needs_no_javascript(client):
    """Le repli sans JS est une propriété du produit, vérifiée en `DF-B`. Et
    l'incident du script périmé a prouvé qu'un JS peut silencieusement ne pas
    tourner. L'activation passe donc par des liens NATIFS."""
    body = _page(client, _session(client))
    links = re.findall(rf'{ANCHOR_A}{ACTIVATE}\b[^>]*>', body)
    assert links, "aucun lien d'activation — la garde ne mesure rien"
    for link in links:
        assert "href=" in link, f"activation sans href : {link[:100]!r}"
        assert "onclick" not in link, f"activation confiée au JS : {link[:100]!r}"


def test_the_activation_link_says_what_it_does(client):
    """Sans nom d'action, un lecteur d'écran annoncerait « E2 Chest Press 0/3 »
    sans dire ce que le lien fait."""
    body = _page(client, _session(client))
    first = body.split(ACTIVATE, 1)[1].split("</a>", 1)[0]
    assert '<span class="sr-only">' in first, (
        "le lien d'activation ne nomme pas son action"
    )
