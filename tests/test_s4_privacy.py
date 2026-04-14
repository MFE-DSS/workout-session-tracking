"""Privacy enforcement tests for S4 features."""
from __future__ import annotations


def test_challenge_standings_only_allowed_keys(client):
    from datetime import date, timedelta
    from app.database import SessionLocal
    from app.services.challenge import create_challenge, compute_standings
    from app.services.squad import create_squad
    from app.models.challenge import SquadChallenge
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    with SessionLocal() as db:
        squad = create_squad(db, uid, f"Privacy Chal {id(client)}")
        c = create_challenge(db, squad.id, uid, "P", "sessions",
                            date.today() - timedelta(days=7), date.today() + timedelta(days=1))
        cid = c.id
    with SessionLocal() as db:
        c = db.get(SquadChallenge, cid)
        standings = compute_standings(db, c)
    for entry in standings:
        assert set(entry.keys()) == {"rank", "username", "value"}


def test_shared_session_no_weights_or_reps(client):
    from app.database import SessionLocal
    from app.services.sharing import share_session, get_squad_activity
    from app.services.squad import create_squad
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    r = client.post("/sessions", data={"template_slug": "push-a"}, follow_redirects=False)
    session_id = int(r.headers["location"].split("/")[-1])

    with SessionLocal() as db:
        squad = create_squad(db, uid, f"Privacy Share {id(client)}")
        sid = squad.id
    with SessionLocal() as db:
        share_session(db, sid, uid, session_id)
    with SessionLocal() as db:
        activity = get_squad_activity(db, sid)

    shared = [a for a in activity if a["type"] == "shared_session"]
    assert len(shared) >= 1
    for ex in shared[0]["exercises"]:
        assert "weight_kg" not in ex
        assert "reps" not in ex
        assert "free_note" not in ex
        assert "muscle_sensation" not in ex


def test_compare_page_no_private_data(client):
    r = client.post("/squads/create", data={"name": f"Privacy Comp {id(client)}"}, follow_redirects=False)
    squad_id = r.headers["location"].rstrip("/").split("/")[-1]

    from tests.helpers import get_test_user_id
    uid = get_test_user_id()

    r2 = client.get(f"/squads/{squad_id}/compare?a={uid}&b={uid}")
    assert r2.status_code == 200
    body = r2.text.lower()
    assert "weight_kg" not in body
    assert "chest_cm" not in body
    assert "readiness" not in body
    assert "bodyweight" not in body
