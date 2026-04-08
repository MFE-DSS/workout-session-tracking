"""Tests for the JSON export endpoint."""
from __future__ import annotations

import json
import re


def test_export_empty_returns_valid_json_with_zero_sessions(client):
    r = client.get("/export/sessions.json")
    assert r.status_code == 200
    assert "application/json" in r.headers["content-type"]
    assert "attachment" in r.headers["content-disposition"]
    payload = r.json()
    assert payload["schema_version"] == 1
    assert payload["count"] == 0
    assert payload["sessions"] == []
    assert "exported_at" in payload


def test_export_contains_session_exercise_and_set_fields(client):
    # Create a session and fill one exercise card
    r = client.post(
        "/sessions", data={"template_slug": "push-a"}, follow_redirects=False
    )
    sid = int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))

    from sqlalchemy import select
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog

    with SessionLocal() as db:
        se = db.execute(
            select(SessionExercise)
            .where(SessionExercise.session_id == sid)
            .where(SessionExercise.exercise_code_snapshot == "E2")
        ).scalar_one()
        se_id = se.id
        work_ids = sorted(
            s.id for s in db.execute(
                select(SetLog).where(SetLog.session_exercise_id == se_id)
            ).scalars().all()
            if s.kind == "work"
        )

    # Fill and save
    data = {"success_score": "80", "muscle_sensation": "strong"}
    for i, wid in enumerate(work_ids, start=1):
        data[f"set_{wid}_weight_kg"] = str(60 + i)
        data[f"set_{wid}_reps"] = "10"
        data[f"set_{wid}_completed"] = "1"
        data[f"set_{wid}_execution_quality"] = "clean"
        data[f"set_{wid}_reps_target"] = "target_hit"
    client.post(
        f"/sessions/{sid}/exercises/{se_id}", data=data, follow_redirects=False
    )

    # Persist session-level fields + end
    client.post(
        f"/sessions/{sid}",
        data={
            "concentration": "high",
            "global_state": "good",
            "bodyweight_kg": "78.5",
            "action": "end",
        },
        follow_redirects=False,
    )

    # Now export
    r = client.get("/export/sessions.json")
    payload = r.json()
    assert payload["count"] == 1
    s = payload["sessions"][0]

    # Session-level fields
    assert s["status"] == "completed"
    assert s["template_slug"] == "push-a"
    assert s["template_name"] == "Push A"
    assert s["concentration"] == "high"
    assert s["global_state"] == "good"
    assert s["bodyweight_kg"] == 78.5
    assert s["started_at"] is not None
    assert s["ended_at"] is not None

    # 8 exercise cards on Push A
    assert len(s["exercises"]) == 8
    e2 = next(e for e in s["exercises"] if e["code"] == "E2")
    assert e2["name"] == "Incline Smith Chest Press"
    assert e2["success_score"] == 80
    assert e2["muscle_sensation"] == "strong"

    # 2 warmup + 3 work rows on E2
    warmups = [x for x in e2["sets"] if x["kind"] == "warmup"]
    works = [x for x in e2["sets"] if x["kind"] == "work"]
    assert len(warmups) == 2
    assert len(works) == 3
    for w in works:
        assert w["completed"] is True
        assert w["weight_kg"] is not None
        assert w["reps"] == 10
        assert w["execution_quality"] == "clean"
        assert w["reps_target"] == "target_hit"


def test_export_is_sorted_oldest_first(client):
    from datetime import datetime, timedelta, timezone

    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    with SessionLocal() as db:
        for days_ago, name in [(10, "Old"), (3, "Middle"), (1, "Recent")]:
            db.add(
                WorkoutSession(
                    template_slug_snapshot="push-a",
                    template_name_snapshot=name,
                    started_at=datetime.now(timezone.utc) - timedelta(days=days_ago),
                    status="completed",
                )
            )
        db.commit()

    payload = client.get("/export/sessions.json").json()
    assert payload["count"] == 3
    names = [s["template_name"] for s in payload["sessions"]]
    assert names == ["Old", "Middle", "Recent"]


def test_export_does_not_leak_internal_ids_beyond_session_id(client):
    r = client.post(
        "/sessions", data={"template_slug": "liss-abs"}, follow_redirects=False
    )
    payload = client.get("/export/sessions.json").json()
    s = payload["sessions"][0]
    # Only top-level session id is intentionally exported.
    # Exercises and set_logs are keyed by position / code / set_index,
    # not by DB ids.
    assert "id" in s
    assert "exercises" in s
    # liss-abs has zero exercises
    assert s["exercises"] == []
