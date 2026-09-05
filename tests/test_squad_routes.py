"""Tests for squad routes: list, create, join, detail, leave, delete."""
from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# 1. List renders
# ---------------------------------------------------------------------------


def test_squads_list_renders(client):
    r = client.get("/squads")
    assert r.status_code == 200
    assert "Squads" in r.text


# ---------------------------------------------------------------------------
# 2. Auth required
# ---------------------------------------------------------------------------


def test_squads_list_requires_auth(client):
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    r = client.get("/squads", follow_redirects=False)
    assert r.status_code == 303
    assert "/login" in r.headers["location"]


# ---------------------------------------------------------------------------
# 3. Create page renders
# ---------------------------------------------------------------------------


def test_squad_create_page_renders(client):
    r = client.get("/squads/create")
    assert r.status_code == 200
    assert "Créer une squad" in r.text


# ---------------------------------------------------------------------------
# 4. Create POST redirects to detail
# ---------------------------------------------------------------------------


def test_squad_create_post(client):
    r = client.post(
        "/squads/create",
        data={"name": "TestSquad"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert "/squads/" in r.headers["location"]


# ---------------------------------------------------------------------------
# 5. Detail page
# ---------------------------------------------------------------------------


def test_squad_detail_page(client):
    # Create a squad first
    r = client.post(
        "/squads/create",
        data={"name": "DetailSquad"},
        follow_redirects=False,
    )
    location = r.headers["location"]
    # Follow redirect to detail page
    r2 = client.get(location)
    assert r2.status_code == 200
    assert "DetailSquad" in r2.text
    assert "Classement" in r2.text


# ---------------------------------------------------------------------------
# 6. Non-member gets 403
# ---------------------------------------------------------------------------


def test_squad_detail_non_member_gets_403(client):
    # Create a squad as testuser
    r = client.post(
        "/squads/create",
        data={"name": "PrivateSquad"},
        follow_redirects=False,
    )
    location = r.headers["location"]
    squad_path = location  # e.g. /squads/1

    # Logout, register and login as outsider
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    client.post(
        "/register",
        data={
            "username": "outsider",
            "password": "testpass123",
            "password_confirm": "testpass123",
        },
        follow_redirects=False,
    )
    client.post(
        "/login",
        data={"username": "outsider", "password": "testpass123"},
        follow_redirects=False,
    )

    r2 = client.get(squad_path)
    assert r2.status_code == 403


# ---------------------------------------------------------------------------
# 7. Join page renders
# ---------------------------------------------------------------------------


def test_squad_join_page_renders(client):
    r = client.get("/squads/join")
    assert r.status_code == 200
    assert "Rejoindre une squad" in r.text


# ---------------------------------------------------------------------------
# 8. Full invite + join flow
# ---------------------------------------------------------------------------


def test_squad_invite_and_join_flow(client):
    # 1. Create a squad as testuser (owner)
    r = client.post(
        "/squads/create",
        data={"name": "JoinSquad"},
        follow_redirects=False,
    )
    location = r.headers["location"]
    squad_id = location.rstrip("/").split("/")[-1]

    # 2. Generate invite code
    client.post(f"/squads/{squad_id}/invite", follow_redirects=False)

    # 3. Get the invite code from the detail page
    detail = client.get(f"/squads/{squad_id}")
    assert detail.status_code == 200
    # Extract code (SPGN-XXXX pattern)
    match = re.search(r"SPGN-[A-Z0-9]{4}", detail.text)
    assert match, "Invite code not found on detail page"
    code = match.group(0)

    # 4. Logout, register new user, login
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    client.post(
        "/register",
        data={
            "username": "joiner",
            "password": "testpass123",
            "password_confirm": "testpass123",
        },
        follow_redirects=False,
    )
    client.post(
        "/login",
        data={"username": "joiner", "password": "testpass123"},
        follow_redirects=False,
    )

    # 5. Join using the invite code
    r2 = client.post(
        "/squads/join",
        data={"code": code},
        follow_redirects=False,
    )
    assert r2.status_code == 303
    assert f"/squads/{squad_id}" in r2.headers["location"]

    # 6. Verify can view the squad detail
    r3 = client.get(f"/squads/{squad_id}")
    assert r3.status_code == 200
    assert "JoinSquad" in r3.text


# ---------------------------------------------------------------------------
# 9. Nav link present
# ---------------------------------------------------------------------------


def test_squad_nav_link_present(client):
    r = client.get("/squads")
    assert r.status_code == 200
    assert 'href="' in r.text
    assert "Squads" in r.text
    # Check the topbar link specifically
    assert "squads" in r.text.lower()


# ---------------------------------------------------------------------------
# `Sb_UI_FORMULAIRES_01` — le nom d'une recommandation est DÉRIVÉ, pas reçu
# ---------------------------------------------------------------------------
#
# ⚠ CES DEUX TESTS EXISTENT PARCE QUE LA PORTE DE COUVERTURE LES A RÉCLAMÉS.
#
# J'ai changé la logique de `squad_recommend` — le nom de la séance n'est plus
# lu dans le formulaire mais dérivé du slug côté serveur — et j'ai vérifié le
# résultat À LA MAIN, dans un navigateur. Aucun test ne l'exerçait : Sonar a
# rendu `new_coverage: 0.0` sur la tranche.
#
# La porte avait raison, et pas seulement sur la forme. Ce que le changement
# apporte est une propriété d'INTÉGRITÉ — un client ne peut plus faire dire à
# une recommandation un nom qui ne correspond pas au gabarit qu'elle désigne —
# et une propriété pareille sans test n'est pas une propriété, c'est une
# intention.


def _squad_id(client) -> int:
    r = client.post("/squads/create", data={"name": "RecoSquad"},
                    follow_redirects=False)
    assert r.status_code == 303
    return int(re.search(r"/squads/(\d+)", r.headers["location"]).group(1))


def test_the_recommended_name_comes_from_the_slug(client):
    """Le serveur nomme la séance lui-même, à partir du gabarit désigné."""
    sid = _squad_id(client)
    r = client.post(f"/squads/{sid}/recommend",
                    data={"template_slug": "push-a", "note": "essai"},
                    follow_redirects=False)
    assert r.status_code == 303

    body = client.get(f"/squads/{sid}").text
    assert "Push A" in body, (
        "la recommandation ne porte aucun nom : le serveur ne l'a pas dérivé"
    )


def test_a_client_supplied_name_is_ignored(client):
    """LA PROPRIÉTÉ QUI COMPTE, et que le champ caché ne garantissait pas.

    Avant, `template_name` arrivait d'un champ caché rempli par un `onchange`.
    Rien n'obligeait ce nom à correspondre au slug : un client pouvait faire
    dire à une recommandation ce qu'il voulait.
    """
    sid = _squad_id(client)
    r = client.post(f"/squads/{sid}/recommend",
                    data={"template_slug": "push-a",
                          "template_name": "Un nom totalement inventé",
                          "note": ""},
                    follow_redirects=False)
    assert r.status_code == 303

    body = client.get(f"/squads/{sid}").text
    assert "Un nom totalement inventé" not in body, (
        "le nom fourni par le client est rendu tel quel — la dérivation "
        "serveur ne sert à rien"
    )
    assert "Push A" in body


def test_an_unknown_slug_does_not_raise(client):
    """Un formulaire est une entrée hostile : il ne lève jamais.

    Un 500 sur une recommandation serait une réponse disproportionnée à un slug
    inconnu — le dépôt applique déjà cette règle aux paramètres d'URL.
    """
    sid = _squad_id(client)
    r = client.post(f"/squads/{sid}/recommend",
                    data={"template_slug": "gabarit-qui-n-existe-pas"},
                    follow_redirects=False)
    assert r.status_code == 303
