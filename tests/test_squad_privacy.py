"""Privacy enforcement tests for squads.

Verifies that private data (measurements, readiness, weight, notes)
is NEVER exposed in squad views or scoped leaderboard.
"""
from __future__ import annotations


def test_squad_detail_does_not_contain_body_measurements(client):
    r = client.post("/squads/create", data={"name": "Privacy Squad A"}, follow_redirects=False)
    r2 = client.get(r.headers["location"])
    body = r2.text.lower()
    assert "chest_cm" not in body
    assert "arm_cm" not in body
    assert "thigh_cm" not in body
    assert "waist_cm" not in body
    assert "hip_cm" not in body
    assert "neck_cm" not in body
    assert "tour de poitrine" not in body
    assert "tour de taille" not in body


def test_squad_detail_does_not_contain_readiness(client):
    r = client.post("/squads/create", data={"name": "Privacy Squad B"}, follow_redirects=False)
    r2 = client.get(r.headers["location"])
    body = r2.text.lower()
    assert "sleep_quality" not in body
    assert "fatigue_level" not in body
    assert "soreness_level" not in body
    assert "stress_level" not in body
    assert "motivation_level" not in body


def test_squad_detail_does_not_contain_bodyweight(client):
    r = client.post("/squads/create", data={"name": "Privacy Squad C"}, follow_redirects=False)
    r2 = client.get(r.headers["location"])
    body = r2.text.lower()
    assert "bodyweight" not in body


def test_squad_leaderboard_only_contains_allowed_fields(client):
    from app.database import SessionLocal
    from app.services.squad import create_squad, compute_squad_leaderboard
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    with SessionLocal() as db:
        squad = create_squad(db, uid, "LB Privacy Squad")
    with SessionLocal() as db:
        lb = compute_squad_leaderboard(db, squad.id)

    allowed_keys = {
        "rank", "username", "total_points", "avg_points", "grade",
        "grade_label", "session_count", "last_session_date",
        "last_session_template", "streak",
    }
    for entry in lb:
        assert set(entry.keys()) == allowed_keys, f"Unexpected keys: {set(entry.keys()) - allowed_keys}"
