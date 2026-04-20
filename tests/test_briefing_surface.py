"""Integration tests — chip on summary, peek at the bottom of the active
card (Sb_11a)."""
from __future__ import annotations

import re


def _start(client, slug: str = "push-a") -> int:
    r = client.post("/sessions", data={"template_slug": slug}, follow_redirects=False)
    return int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


def _get_exercise_ids(sid: int) -> list[int]:
    from sqlalchemy import select
    from app.database import SessionLocal
    from app.models.session import SessionExercise
    from app.models.user import User  # noqa: F401 — mapper resolution

    with SessionLocal() as db:
        rows = db.execute(
            select(SessionExercise)
            .where(SessionExercise.session_id == sid)
            .order_by(SessionExercise.position.asc())
        ).scalars().all()
        return [se.id for se in rows]


# ---- Chip on future / partial cards ----------------------------------


def test_chip_present_on_future_card_summary(client):
    """A fresh session has E1 active and E2+ future → chips on E2+."""
    sid = _start(client, "push-a")
    r = client.get(f"/sessions/{sid}")
    body = r.text
    assert 'exercise-card__chip' in body
    # The chip carries the rep scheme and last-time.
    # Push A E1 is '3x 6-10' but E1 is active so we look at another card.
    # Any chip suffices — we just verify the markup class is rendered.
    assert 'première fois' in body or 'dernière fois' in body


def test_chip_absent_on_active_card(client):
    """The active card has no chip — the scheme is already on the open form."""
    sid = _start(client, "push-a")
    r = client.get(f"/sessions/{sid}")
    body = r.text
    # Extract the first <details open> block (the active card) and assert
    # no chip inside its <summary>.
    m = re.search(
        r'<details[^>]*class="[^"]*exercise-card[^"]*"[^>]*\bopen\b[^>]*>.*?</summary>',
        body,
        re.DOTALL,
    )
    assert m, "expected an active <details open> card with a summary"
    active_summary = m.group(0)
    assert 'exercise-card__chip' not in active_summary


def test_chip_absent_on_completed_card(client):
    """Once a card is fully completed (done), the chip is replaced by the
    recap line — no chip markup should remain on that summary."""
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession
    from app.models.user import User  # noqa: F401

    sid = _start(client, "push-a")
    ex_ids = _get_exercise_ids(sid)

    # Force E1 to be fully done: mark every work set as completed with data.
    with SessionLocal() as db:
        se = db.get(SessionExercise, ex_ids[0])
        for sl in se.set_logs:
            if sl.kind == "work":
                sl.completed = True
                sl.weight_kg = 50.0
                sl.reps = 10
        db.commit()

    # Now open the session on E2 so E1 is not the active card.
    r = client.get(f"/sessions/{sid}?active={ex_ids[1]}")
    body = r.text
    # Isolate E1's card markup and assert no chip.
    m = re.search(
        r'<details[^>]*id="exercise-%d"[^>]*>.*?</summary>' % ex_ids[0],
        body,
        re.DOTALL,
    )
    assert m, "expected E1 card in DOM"
    e1_summary = m.group(0)
    assert 'exercise-card__chip' not in e1_summary
    # Recap line should be there instead.
    assert 'exercise-card__recap' in e1_summary


# ---- Peek at the bottom of the active card ---------------------------


def test_peek_rendered_on_active_card_when_next_exists(client):
    """Active E1 + next E2 exists → peek block visible."""
    sid = _start(client, "push-a")
    r = client.get(f"/sessions/{sid}")
    body = r.text
    assert 'card-peek' in body
    assert 'Prochain' in body


def test_peek_carries_scheme_and_last_time(client):
    sid = _start(client, "push-a")
    r = client.get(f"/sessions/{sid}")
    body = r.text
    assert 'card-peek__scheme' in body
    # Push A is fully strength so all next cards have schemes.
    assert re.search(r'\d+×\d+', body) is not None


def test_peek_absent_on_last_card(client):
    """On the last exercise (no next), no peek rendered."""
    sid = _start(client, "push-a")
    ex_ids = _get_exercise_ids(sid)
    last_id = ex_ids[-1]
    r = client.get(f"/sessions/{sid}?active={last_id}")
    body = r.text
    # Isolate the last card (active <details open>) and check no peek
    # inside its form.
    m = re.search(
        r'<details[^>]*id="exercise-%d"[^>]*\bopen\b[^>]*>(.*?)</details>\s*(?=<details|$)' % last_id,
        body,
        re.DOTALL,
    )
    assert m, "expected last card rendered open"
    active_block = m.group(1)
    assert 'card-peek' not in active_block


def test_peek_includes_cues_when_next_has_atlas_link(client):
    """Push A E2 is Chest Press machine, linked to the atlas → when the
    active card is E1, the peek for E2 must include execution cues."""
    sid = _start(client, "push-a")
    r = client.get(f"/sessions/{sid}")
    body = r.text
    # The peek block wraps a <ul class="card-peek__cues">.
    assert 'card-peek__cues' in body


def test_peek_head_shows_next_code_and_name(client):
    sid = _start(client, "push-a")
    r = client.get(f"/sessions/{sid}")
    body = r.text
    assert 'card-peek__code' in body
    assert 'card-peek__name' in body
