"""Tests for Sb_10 polish (G1 home sparkline legend + G2 session note details)."""
from __future__ import annotations

import re
from datetime import datetime, timezone

from tests.helpers import get_test_user_id


def _start(client, slug: str) -> int:
    r = client.post("/sessions", data={"template_slug": slug}, follow_redirects=False)
    return int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


def _complete_minimal(sid: int, kind: str = "strength") -> None:
    """Mark a session as completed with a minimal work set for the strength
    dispatcher path, or with cardio duration for the cardio path."""
    from app.database import SessionLocal
    from app.models.session import SetLog, WorkoutSession
    from app.models.catalog import WorkoutTemplate

    with SessionLocal() as db:
        s = db.get(WorkoutSession, sid)
        s.status = "completed"
        s.ended_at = datetime.now(timezone.utc)
        s.concentration = "high"
        s.global_state = "good"
        if kind == "cardio":
            # Force cardio kind via template.kind on the linked template.
            if s.template is not None:
                s.template.kind = "cardio"
            s.cardio_duration_min = 25
            s.cardio_bpm_avg = 125
        else:
            # Give the first exercise one completed work set so the
            # strength scorer returns something meaningful.
            if s.session_exercises:
                se = s.session_exercises[0]
                se.set_logs.append(SetLog(
                    kind="work", set_index=99,
                    weight_kg=50.0, reps=10, completed=True,
                ))
        db.commit()


# ---- G1 — home sparkline legend --------------------------------------

def test_home_sparkline_no_legend_without_cardio_session(client):
    """Only strength sessions → legend hidden (single color, no noise)."""
    sid = _start(client, "push-a")
    _complete_minimal(sid, kind="strength")
    r = client.get("/")
    assert r.status_code == 200
    # Sparkline renders but no legend because only one kind is present.
    assert 'timeline-legend--compact' not in r.text


def test_home_sparkline_legend_appears_when_kinds_mix(client):
    """One strength + one cardio session → compact legend is visible."""
    sid_s = _start(client, "push-a")
    _complete_minimal(sid_s, kind="strength")
    sid_c = _start(client, "liss-abs")
    _complete_minimal(sid_c, kind="cardio")

    r = client.get("/")
    body = r.text
    assert r.status_code == 200
    assert 'timeline-legend--compact' in body
    assert 'Musculation' in body
    assert 'Cardio' in body


# ---- G2 — session note in <details> ----------------------------------

def test_session_note_wrapped_in_details(client):
    """Session-level free_note is inside <details class="session-feedback__note">."""
    sid = _start(client, "push-a")
    r = client.get(f"/sessions/{sid}")
    body = r.text
    assert 'session-feedback__note' in body
    assert 'Note séance (optionnel)' in body
    # The <details> must wrap the textarea (not render it bare).
    assert '<details class="session-feedback__note"' in body


def test_session_note_details_open_when_filled(client):
    """When a note is persisted, the <details> is opened so the user sees it."""
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    sid = _start(client, "push-a")
    with SessionLocal() as db:
        s = db.get(WorkoutSession, sid)
        s.free_note = "Ressenti moyen aujourd'hui"
        db.commit()

    r = client.get(f"/sessions/{sid}")
    body = r.text
    # Jinja renders `open` when free_note is truthy.
    assert '<details class="session-feedback__note" open>' in body


def test_session_note_details_collapsed_when_empty(client):
    """Empty note → <details> with no `open` attribute (collapsed by default)."""
    sid = _start(client, "push-a")
    r = client.get(f"/sessions/{sid}")
    body = r.text
    # No `open` attribute on the details wrapper.
    assert '<details class="session-feedback__note" >' in body or \
           '<details class="session-feedback__note">' in body


def test_session_note_still_submits_on_post(client):
    """Ensure the <details> refacto didn't break the POST path — the
    textarea is still named free_note and still persists."""
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    sid = _start(client, "push-a")
    r = client.post(
        f"/sessions/{sid}",
        data={
            "free_note": "Polish Sb_10 — note écrite pliée",
            "concentration": "medium",
            "global_state": "flat",
            "bodyweight_kg": "77.5",
        },
        follow_redirects=False,
    )
    assert r.status_code in {303, 200}

    with SessionLocal() as db:
        s = db.get(WorkoutSession, sid)
        assert s.free_note == "Polish Sb_10 — note écrite pliée"
