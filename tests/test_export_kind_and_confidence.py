"""Tests for Sb_09 export schema v2: session_kind, quality_score,
confidence_score, confidence_level."""
from __future__ import annotations

import json
import re


def _start(client, slug: str) -> int:
    r = client.post("/sessions", data={"template_slug": slug}, follow_redirects=False)
    return int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


def _finish(client, sid: int):
    client.post(
        f"/sessions/{sid}",
        data={
            "action": "end",
            "concentration": "high",
            "global_state": "good",
            "bodyweight_kg": "78.0",
        },
        follow_redirects=False,
    )


def test_export_json_includes_session_kind_and_confidence(client):
    sid = _start(client, "push-a")
    _finish(client, sid)

    r = client.get("/export/sessions.json")
    assert r.status_code == 200
    payload = r.json()
    assert payload["schema_version"] == 2
    assert payload["sessions"], "expected at least one session"
    s = payload["sessions"][0]
    assert s["session_kind"] in {"strength", "cardio"}
    assert "quality_score" in s
    assert "confidence_score" in s
    assert "confidence_level" in s


def test_export_csv_header_carries_new_columns(client):
    r = client.get("/export/sessions.csv")
    assert r.status_code == 200
    header = r.text.splitlines()[0]
    for col in ["session_kind", "quality_score", "confidence_score", "confidence_level"]:
        assert col in header


def test_export_strength_session_has_kind_strength(client):
    sid = _start(client, "push-a")
    _finish(client, sid)
    r = client.get("/export/sessions.json")
    kinds = {s["session_kind"] for s in r.json()["sessions"]}
    assert "strength" in kinds


def test_export_schema_constant_is_two():
    from app.services.export_builder import SCHEMA_VERSION
    assert SCHEMA_VERSION == 2
