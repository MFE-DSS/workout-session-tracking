"""Tests for the deterministic progression hint.

The rule is documented in docs/PRODUCT_SPEC.md. These tests both
exercise the pure function and verify the hint surfaces on the
session detail page at the right moment.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone


# ----- Pure function -----


def test_hint_none_when_no_prior_reps(client):
    from app.services.progression_hint import compute_progression_hint

    assert compute_progression_hint(6, 10, None, None) is None
    assert compute_progression_hint(6, 10, 60.0, None) is None
    assert compute_progression_hint(6, 10, None, 8) is None


def test_hint_none_when_no_targets(client):
    from app.services.progression_hint import compute_progression_hint

    assert compute_progression_hint(None, None, 60.0, 8) is None
    assert compute_progression_hint(6, None, 60.0, 8) is None


def test_hint_says_increase_load_when_top_reached(client):
    from app.services.progression_hint import compute_progression_hint

    msg = compute_progression_hint(6, 10, 60.0, 10)
    assert msg == "tenter d'augmenter la charge sur le premier set"
    # Strictly greater than max also triggers the increase hint
    assert (
        compute_progression_hint(6, 10, 60.0, 12)
        == "tenter d'augmenter la charge sur le premier set"
    )


def test_hint_says_consolidate_when_below_range(client):
    from app.services.progression_hint import compute_progression_hint

    assert (
        compute_progression_hint(6, 10, 60.0, 5)
        == "consolider la charge actuelle"
    )


def test_hint_says_aim_for_top_when_inside_range(client):
    from app.services.progression_hint import compute_progression_hint

    assert (
        compute_progression_hint(6, 10, 60.0, 8)
        == "viser 10 reps avant d'augmenter la charge"
    )


# ----- Integration with session detail -----


def _new_session(client, slug: str = "push-a") -> int:
    r = client.post("/sessions", data={"template_slug": slug}, follow_redirects=False)
    return int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


def _seed_prior_push_a_e2(
    first_weight: float, first_reps: int, completed: bool = True
) -> None:
    """Inject a prior completed Push A session with E2 first work set
    matching the given weight/reps. E2 rep_target is 6-10."""
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    with SessionLocal() as db:
        s = WorkoutSession(
            template_slug_snapshot="push-a",
            template_name_snapshot="Push A",
            started_at=datetime.now(timezone.utc) - timedelta(days=3),
            status="completed",
        )
        se = SessionExercise(
            exercise_code_snapshot="E2",
            exercise_name_snapshot="Incline Smith Chest Press",
            position=2,
        )
        se.set_logs.append(
            SetLog(
                kind="work",
                set_index=1,
                weight_kg=first_weight,
                reps=first_reps,
                completed=completed,
            )
        )
        s.session_exercises.append(se)
        db.add(s)
        db.commit()


def test_session_detail_shows_no_hint_when_no_prior(client):
    sid = _new_session(client, "push-a")
    r = client.get(f"/sessions/{sid}")
    body = r.text
    # No Repère block at all when there's no prior data
    assert "hint__label" not in body
    assert "Repère" not in body


def test_session_detail_shows_increase_hint_on_top_of_range(client):
    _seed_prior_push_a_e2(first_weight=60.0, first_reps=10)
    sid = _new_session(client, "push-a")
    r = client.get(f"/sessions/{sid}")
    body = r.text
    assert "Repère" in body
    assert "tenter d&#39;augmenter la charge sur le premier set" in body


def test_session_detail_shows_consolidate_hint_below_range(client):
    _seed_prior_push_a_e2(first_weight=60.0, first_reps=5)
    sid = _new_session(client, "push-a")
    r = client.get(f"/sessions/{sid}")
    body = r.text
    assert "consolider la charge actuelle" in body


def test_session_detail_shows_aim_hint_inside_range(client):
    _seed_prior_push_a_e2(first_weight=60.0, first_reps=8)
    sid = _new_session(client, "push-a")
    body = client.get(f"/sessions/{sid}").text
    assert "viser 10 reps avant d&#39;augmenter la charge" in body
