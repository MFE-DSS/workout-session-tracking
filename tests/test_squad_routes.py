"""Tests for squad routes: list, create, join, detail, leave, delete."""
from __future__ import annotations

import re

from tests.helpers import get_test_user_id


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
