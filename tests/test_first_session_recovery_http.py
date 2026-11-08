"""Real transactions: competing keys, legacy admission, cancel and lost responses."""

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from threading import Barrier

import pytest

from tests import plan_v3_test_support as support
from tests.test_first_session_commands import final_evaluation, start_body
from tests.test_plan_v3_persistence import install

science_bundle = support.science_bundle
plan_bundle = support.plan_bundle


@pytest.mark.parametrize("competitor", ["second_key", "cancel", "legacy"])
def test_actual_connections_serialize_first_handoff_competitors(
    client, monkeypatch, science_bundle, competitor
):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from app.models.user import User
    from app.services.plan_v3 import commands as c
    from app.services.plan_v3.transactions import RuntimeFailure, admit_legacy_start

    install()
    with SessionLocal() as db:
        owner = db.query(User).one().id
        body = start_body(final_evaluation(db, owner, science_bundle, monkeypatch))
    barrier = Barrier(2)

    def run(which):
        with SessionLocal() as db:
            barrier.wait(timeout=15)
            try:
                if which == 0:
                    row = c.start_owned_first_session(db, owner, request_id="first", body=body)
                    result = (row.state, row.session_id)
                elif competitor == "second_key":
                    row = c.start_owned_first_session(db, owner, request_id="second", body=body)
                    result = (row.state, row.session_id)
                elif competitor == "cancel":
                    row = c.cancel_owned_first_session(db, owner, request_id="first", body=body)
                    result = (row.state, row.session_id)
                else:
                    admit_legacy_start(db, owner, reject_any_open=True)
                    row = WorkoutSession(
                        user_id=owner,
                        template_slug_snapshot="legacy",
                        template_name_snapshot="Historical",
                        started_at=datetime.now(UTC),
                        status="in_progress",
                    )
                    db.add(row)
                    db.flush()
                    result = ("LEGACY", row.id)
                db.commit()
                return result
            except RuntimeFailure as error:
                db.rollback()
                return (error.code, None)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(run, [0, 1]))
    with SessionLocal() as db:
        sessions = db.query(WorkoutSession).all()
        if competitor == "cancel":
            assert len(sessions) <= 1
            assert results[0][0] == results[1][0]
        else:
            assert len(sessions) == 1
            assert sum(state in {"CREATED", "LEGACY"} for state, _ in results) == 1
        if sessions:
            replay = c.start_owned_first_session(db, owner, request_id="first", body=body)
            assert replay.session_id in (None, sessions[0].id)


def test_lost_http_response_after_commit_recovers_same_owned_session(
    client, monkeypatch, science_bundle
):
    from app.config import get_settings
    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from app.models.user import User
    from app.services.plan_v3 import commands as c
    from tests.test_blueprint_runtime_http import ROOT, enable, token

    enable(monkeypatch)
    monkeypatch.setattr(get_settings(), "plan_v3_creation_enabled", True)
    install()
    with SessionLocal() as db:
        owner = db.query(User).one().id
        body = start_body(final_evaluation(db, owner, science_bundle, monkeypatch))
    headers = token(client)
    original = c.start_owned_first_session

    def committed_but_response_lost(db, *args, **kwargs):
        original(db, *args, **kwargs)
        db.commit()
        raise ConnectionError("injected_after_commit")

    monkeypatch.setattr(c, "start_owned_first_session", committed_but_response_lost)
    with pytest.raises(ConnectionError, match="injected_after_commit"):
        client.post(
            ROOT + "/me/first-session-requests",
            headers=headers,
            json={"request_id": "lost", "command": body},
        )
    monkeypatch.setattr(c, "start_owned_first_session", original)
    recovered = client.get(ROOT + "/me/first-session-requests/lost", headers=headers)
    assert recovered.status_code == 200, recovered.text
    assert recovered.json()["state"] == "CREATED"
    replay = client.post(
        ROOT + "/me/first-session-requests",
        headers=headers,
        json={"request_id": "lost", "command": body},
    )
    assert replay.json()["session_id"] == recovered.json()["session_id"]
    with SessionLocal() as db:
        assert db.query(WorkoutSession).count() == 1


def test_http_failure_before_commit_rolls_back_every_session_artifact(
    client, monkeypatch, science_bundle
):
    from app.config import get_settings
    from app.database import SessionLocal
    from app.models.first_plan_runtime import FirstPlanExecutionBinding, FirstSessionRequest
    from app.models.session import SessionExercise, SetLog, WorkoutSession
    from app.models.user import User
    from app.services.plan_v3 import commands as c
    from tests.test_blueprint_runtime_http import ROOT, enable, token

    enable(monkeypatch)
    monkeypatch.setattr(get_settings(), "plan_v3_creation_enabled", True)
    install()
    with SessionLocal() as db:
        owner = db.query(User).one().id
        body = start_body(final_evaluation(db, owner, science_bundle, monkeypatch))
    headers = token(client)
    original = c.start_owned_first_session

    def response_fails_before_commit(db, *args, **kwargs):
        original(db, *args, **kwargs)
        raise ConnectionError("injected_before_commit")

    monkeypatch.setattr(c, "start_owned_first_session", response_fails_before_commit)
    with pytest.raises(ConnectionError, match="injected_before_commit"):
        client.post(ROOT + "/me/first-session-requests", headers=headers,
                    json={"request_id": "same-before", "command": body})
    with SessionLocal() as db:
        for model in (WorkoutSession, SessionExercise, SetLog, FirstPlanExecutionBinding, FirstSessionRequest):
            assert db.query(model).count() == 0
    monkeypatch.setattr(c, "start_owned_first_session", original)
    replay = client.post(ROOT + "/me/first-session-requests", headers=headers,
                         json={"request_id": "same-before", "command": body})
    assert replay.status_code == 200, replay.text
    assert replay.json()["state"] == "CREATED"
