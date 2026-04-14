"""Route tests for the launcher page (Sb_launcher_v1 Task 2)."""
from __future__ import annotations


def test_launcher_step1_renders(client):
    r = client.get("/launcher")
    assert r.status_code == 200
    body = r.text
    assert "Séance standard" in body
    assert "Séance courte" in body
    assert "Cardio" in body


def test_launcher_step2_standard(client):
    r = client.get("/launcher?type=standard")
    assert r.status_code == 200
    body = r.text
    assert "Haut / Push" in body
    assert "Haut / Pull" in body
    assert "Bas / Quads dominant" in body


def test_launcher_step2_hides_empty_branches(client):
    r = client.get("/launcher?type=short")
    assert r.status_code == 200
    body = r.text
    assert "Full upper court" in body
    assert "Full lower court" not in body
    assert "Full body court" not in body


def test_launcher_final_standard_upper_push(client):
    r = client.get("/launcher?type=standard&variant=upper-push")
    assert r.status_code == 200
    body = r.text
    assert "Push A" in body
    assert "Push B" in body


def test_launcher_cardio_direct(client):
    r = client.get("/launcher?type=cardio")
    assert r.status_code == 200
    body = r.text
    assert "LISS" in body
    # Must be step 3 (a Démarrer form present for liss-abs).
    assert 'value="liss-abs"' in body


def test_launcher_unknown_type_falls_back_to_step1(client):
    r = client.get("/launcher?type=bogus")
    assert r.status_code == 200
    body = r.text
    # Step-1 type labels must appear.
    assert "Séance standard" in body
    assert "Séance courte" in body


def test_launcher_library_link_present(client):
    r = client.get("/launcher")
    assert r.status_code == 200
    assert "/library" in r.text


def test_launcher_requires_auth(client):
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    r = client.get("/launcher", follow_redirects=False)
    assert r.status_code == 303


def test_home_tile_points_to_launcher(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "/launcher" in r.text
