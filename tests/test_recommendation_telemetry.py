"""Tests for Sb_13 telemetry — creation_source persisted on POST /sessions."""
from __future__ import annotations

import re
from datetime import UTC


def _start(client, data: dict) -> int:
    r = client.post("/sessions", data=data, follow_redirects=False)
    assert r.status_code in {302, 303}
    return int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


def _creation_source(sid: int) -> str | None:
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    with SessionLocal() as db:
        s = db.get(WorkoutSession, sid)
        return s.creation_source


def test_creation_source_reco_top_persists(client):
    sid = _start(client, {"template_slug": "push-a", "creation_source": "reco_top"})
    assert _creation_source(sid) == "reco_top"


def test_creation_source_reco_alt_persists(client):
    sid = _start(client, {"template_slug": "pull-a", "creation_source": "reco_alt"})
    assert _creation_source(sid) == "reco_alt"


def test_creation_source_launcher_persists(client):
    sid = _start(client, {"template_slug": "legs-a", "creation_source": "launcher"})
    assert _creation_source(sid) == "launcher"


def test_creation_source_library_persists(client):
    sid = _start(client, {"template_slug": "push-b", "creation_source": "library"})
    assert _creation_source(sid) == "library"


def test_invalid_creation_source_stored_as_null(client):
    """Non-whitelisted values are silently ignored — stored as NULL to
    keep the field strictly analytical."""
    sid = _start(client, {"template_slug": "push-a", "creation_source": "xxx-not-in-list"})
    assert _creation_source(sid) is None


def test_absent_creation_source_is_null(client):
    """No field → NULL (backward compatible)."""
    sid = _start(client, {"template_slug": "pull-b"})
    assert _creation_source(sid) is None


def test_home_partial_has_reco_top_hidden_input(client):
    r = client.get("/")
    body = r.text
    assert 'name="creation_source"' in body
    assert 'value="reco_top"' in body


def test_home_partial_alternatives_carry_reco_alt(client):
    """When alternatives are shown, each carries creation_source=reco_alt."""
    # Seed a bit of history so we exit cold-start.
    from datetime import datetime, timedelta

    from tests.test_recommendation_service import _mk_session

    now = datetime(2026, 4, 21, 18, 0, tzinfo=UTC)
    for delta in (9, 5, 2):
        _mk_session(template_slug="push-a", started_at=now - timedelta(days=delta))

    r = client.get("/")
    body = r.text
    if "reco-next__alternatives" in body:
        assert 'value="reco_alt"' in body


def test_launcher_step3_form_carries_launcher_source(client):
    r = client.get("/launcher?type=standard&variant=upper-push")
    body = r.text
    assert 'name="creation_source"' in body
    assert 'value="launcher"' in body


def test_library_form_carries_library_source(client):
    r = client.get("/library")
    body = r.text
    assert 'value="library"' in body
