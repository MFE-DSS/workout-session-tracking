"""Tests for cardio capture flow."""
from __future__ import annotations

import re


def test_cardio_session_shows_cardio_section(client):
    r = client.post("/sessions", data={"template_slug": "liss-only"}, follow_redirects=False)
    sid = int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))
    r2 = client.get(f"/sessions/{sid}")
    assert r2.status_code == 200
    assert "Cardio" in r2.text
    assert "Durée (min)" in r2.text
    assert "BPM moyen" in r2.text
    assert "Calories machine (indicatif)" in r2.text


def test_strength_session_does_not_show_cardio_section(client):
    r = client.post("/sessions", data={"template_slug": "push-a"}, follow_redirects=False)
    sid = int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))
    r2 = client.get(f"/sessions/{sid}")
    assert r2.status_code == 200
    assert "Durée (min)" not in r2.text


def test_cardio_fields_persist_on_save(client):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    r = client.post("/sessions", data={"template_slug": "liss-only"}, follow_redirects=False)
    sid = int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))

    client.post(f"/sessions/{sid}", data={
        "concentration": "medium",
        "global_state": "good",
        "cardio_duration_min": "25",
        "cardio_bpm_avg": "128",
        "cardio_machine_calories": "220",
        "cardio_machine_type": "velo",
    }, follow_redirects=False)

    with SessionLocal() as db:
        s = db.get(WorkoutSession, sid)
        assert s.cardio_duration_min == 25
        assert s.cardio_bpm_avg == 128
        assert s.cardio_machine_calories == 220
        assert s.cardio_machine_type == "velo"


def test_calories_label_warns_indicative(client):
    r = client.post("/sessions", data={"template_slug": "liss-only"}, follow_redirects=False)
    sid = int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))
    r2 = client.get(f"/sessions/{sid}")
    assert "Calories machine (indicatif)" in r2.text


def test_export_includes_cardio_fields(client):
    import json as json_lib
    r = client.post("/sessions", data={"template_slug": "liss-only"}, follow_redirects=False)
    sid = int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))
    client.post(f"/sessions/{sid}", data={
        "cardio_duration_min": "20",
        "cardio_bpm_avg": "120",
        "action": "end",
    }, follow_redirects=False)

    body = client.get("/export/sessions.json").text
    data = json_lib.loads(body)
    session_data = [s for s in data["sessions"] if s["id"] == sid][0]
    assert session_data["cardio_duration_min"] == 20
    assert session_data["cardio_bpm_avg"] == 120
