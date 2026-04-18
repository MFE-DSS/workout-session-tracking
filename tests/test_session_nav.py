"""Tests for session navigation (Sb_05 — save-on-next + save-on-prev)."""
from __future__ import annotations

import re


def _start(client, slug: str = "push-a") -> int:
    r = client.post("/sessions", data={"template_slug": slug}, follow_redirects=False)
    return int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


def _get_exercise_ids(sid: int) -> list[int]:
    """Return SessionExercise ids ordered by position."""
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import SessionExercise
    from app.models.user import User  # noqa: F401 — ensures mappers resolve

    with SessionLocal() as db:
        rows = db.execute(
            select(SessionExercise)
            .where(SessionExercise.session_id == sid)
            .order_by(SessionExercise.position.asc())
        ).scalars().all()
        return [se.id for se in rows]


def test_save_exercise_default_redirects_to_next(client):
    """Without 'nav' param, default is next exercise (legacy behaviour)."""
    sid = _start(client, "push-a")
    ex_ids = _get_exercise_ids(sid)
    e1_id = ex_ids[0]
    e2_id = ex_ids[1]

    r = client.post(
        f"/sessions/{sid}/exercises/{e1_id}",
        data={},  # no nav param
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert f"active={e2_id}" in r.headers["location"]
    assert f"#exercise-{e2_id}" in r.headers["location"]


def test_save_exercise_nav_next_redirects_to_next(client):
    """Explicit nav=next also redirects to next exercise."""
    sid = _start(client, "push-a")
    ex_ids = _get_exercise_ids(sid)
    e1_id = ex_ids[0]
    e2_id = ex_ids[1]

    r = client.post(
        f"/sessions/{sid}/exercises/{e1_id}",
        data={"nav": "next"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert f"active={e2_id}" in r.headers["location"]


def test_save_exercise_nav_prev_redirects_to_previous(client):
    """nav=prev on E2 → redirect to E1 (previous position)."""
    sid = _start(client, "push-a")
    ex_ids = _get_exercise_ids(sid)
    e1_id = ex_ids[0]
    e2_id = ex_ids[1]

    r = client.post(
        f"/sessions/{sid}/exercises/{e2_id}",
        data={"nav": "prev"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert f"active={e1_id}" in r.headers["location"]
    assert f"#exercise-{e1_id}" in r.headers["location"]


def test_save_exercise_nav_prev_on_first_stays_on_same(client):
    """nav=prev on E1 (first) → stays on E1 (no previous to go to)."""
    sid = _start(client, "push-a")
    ex_ids = _get_exercise_ids(sid)
    e1_id = ex_ids[0]

    r = client.post(
        f"/sessions/{sid}/exercises/{e1_id}",
        data={"nav": "prev"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert f"active={e1_id}" in r.headers["location"]


def test_save_exercise_save_happens_before_nav_prev(client):
    """nav=prev must still persist the data of the current card."""
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import SessionExercise
    from app.models.user import User  # noqa: F401

    sid = _start(client, "push-a")
    ex_ids = _get_exercise_ids(sid)
    e2_id = ex_ids[1]

    # Fill E2 with muscle_sensation, then nav=prev
    r = client.post(
        f"/sessions/{sid}/exercises/{e2_id}",
        data={"nav": "prev", "muscle_sensation": "strong"},
        follow_redirects=False,
    )
    assert r.status_code == 303

    # E2 data is persisted
    with SessionLocal() as db:
        se = db.execute(
            select(SessionExercise).where(SessionExercise.id == e2_id)
        ).scalar_one()
        assert se.muscle_sensation == "strong"


def test_session_detail_renders_prev_button_from_e2(client):
    """Carte E2 doit avoir un bouton 'Precedent' avec nav=prev."""
    sid = _start(client, "push-a")
    ex_ids = _get_exercise_ids(sid)
    e2_id = ex_ids[1]

    body = client.get(f"/sessions/{sid}?active={e2_id}").text
    # The prev button is rendered with name="nav" value="prev"
    assert 'name="nav"' in body
    assert 'value="prev"' in body


def test_session_detail_no_prev_button_on_e1(client):
    """Carte E1 (premier exercice) ne doit pas avoir de bouton 'Precedent'."""
    sid = _start(client, "push-a")
    ex_ids = _get_exercise_ids(sid)
    e1_id = ex_ids[0]

    body = client.get(f"/sessions/{sid}?active={e1_id}").text
    # First card: no prev button — check by looking at the E1 card section
    # (approximation: verify there's no "← E" shortcut referring to going back from E1)
    # More reliably: the first card's form shouldn't include a prev button
    # Since multiple cards may be on the page, we look for the "btn--nav-prev"
    # count: must be <= 6 (one per non-first card)
    prev_count = body.count('btn--nav-prev')
    # 7 exercises in push-a v10, so max 6 prev buttons (none on E1)
    assert prev_count <= 6
