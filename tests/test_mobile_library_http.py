"""Isolated HTTP mount using real ApiUser, DB, domains and router; product mount pending lease."""

from __future__ import annotations

import pytest

ROOT = "/api/mobile/v1/me/library"
HEADER = "X-Auren-Library-Contract"
VERSION = "owned-library/1.0.0"


@pytest.fixture
def api(client):
    from test_mobile_library_reads import template

    from app.database import SessionLocal
    from app.main import app
    from app.models.user import User
    from app.routers.mobile_library import LibraryRuntime, create_library_router
    from app.services.device_auth import open_device_session

    app.include_router(
        create_library_router(LibraryRuntime("synthetic-http", "q" * 40, True, "test")),
        prefix="/api/mobile/v1",
    )
    with SessionLocal() as db:
        user = db.query(User).one()
        issued = open_device_session(db, user)
        db.commit()
        template(db, "qa-http")
        owner = user.id
    return client, {HEADER: VERSION, "Authorization": f"Bearer {issued.access_token}"}, owner


def detail(c, headers):
    page = c.get(ROOT, params={"limit": 100}, headers=headers)
    assert page.status_code == 200
    row = next(x for x in page.json()["entries"] if x["name"] == "qa-http")
    result = c.get(ROOT + "/items/" + row["source_ref"], headers=headers)
    assert result.status_code == 200
    return result.json()


def test_cookie_does_not_grant_library_access(api):
    c, _, _ = api
    r = c.get(ROOT, headers={HEADER: VERSION})
    assert r.status_code == 401
    assert r.headers["cache-control"] == "no-store"
    assert r.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize("version", [None, "", "owned-library/2.0.0"])
def test_library_requires_exact_negotiation(api, version):
    c, headers, _ = api
    if version is None:
        headers.pop(HEADER)
    else:
        headers[HEADER] = version
    r = c.get(ROOT, headers=headers)
    assert r.status_code == 406
    assert r.headers[HEADER] == VERSION
    assert r.headers["cache-control"] == "no-store"


@pytest.mark.parametrize(
    "query", ["?limit=0", "?limit=101", "?limit=1&limit=2", "?secret=private", "?section=garbage"]
)
def test_unbounded_duplicated_or_unknown_queries_are_refused(api, query):
    c, headers, _ = api
    r = c.get(ROOT + query, headers=headers)
    assert r.status_code == 422
    assert "private" not in r.text


def test_http_creates_real_execution_and_exact_second_start_refusal(api):
    from app.services.library_read_model import request_digest

    c, headers, owner = api
    d = detail(c, headers)
    body = {"contract_version": VERSION, "selection_ref": d["selection"]["selection_ref"]}
    r = c.post(ROOT + "/start", json=body, headers=headers)
    assert r.status_code == 201
    x = r.json()
    assert (x["owner_id"], x["request_sha256"]) == (owner, request_digest(body))
    assert x["execution"]["template_slug"] == "qa-http"
    assert x["execution"]["session_id"] > 0
    assert x["execution"]["done"] == {}
    assert r.headers["cache-control"] == "no-store"
    again = c.post(ROOT + "/start", json=body, headers=headers)
    assert again.status_code == 409
    assert again.json() == {
        "contract_version": VERSION,
        "owner_id": owner,
        "request_sha256": request_digest(body),
        "effect": "NOT_CREATED",
        "code": "session_open",
    }


@pytest.mark.parametrize(
    "body",
    [
        dict(contract_version=VERSION),
        dict(contract_version=VERSION, selection_ref="x", request_id="invented"),
        dict(contract_version=VERSION, selection_ref=True),
    ],
)
def test_http_mutation_body_is_closed(api, body):
    c, headers, _ = api
    r = c.post(ROOT + "/start", json=body, headers=headers)
    assert r.status_code == 422
    assert "NOT_CREATED" not in r.text  # no valid exact body to correlate


def test_storage_failure_does_not_claim_definitive_non_creation(api, monkeypatch):
    from app.routers import mobile_library

    c, headers, _ = api
    d = detail(c, headers)

    def fail(*args, **kwargs):
        raise RuntimeError("private database location and token")

    monkeypatch.setattr(mobile_library, "start_library_session", fail)
    r = c.post(
        ROOT + "/start",
        json={"contract_version": VERSION, "selection_ref": d["selection"]["selection_ref"]},
        headers=headers,
    )
    assert r.status_code == 503
    assert r.json() == {"detail": {"error": "storage_unavailable"}}
    assert "private" not in r.text and "NOT_CREATED" not in r.text


def test_source_labelled_http_witness_for_native_decoder(api):
    """Optional export is test-only, never a served positive fixture."""
    import json
    import os
    from pathlib import Path

    c, headers, _ = api
    page = c.get(ROOT, params={"limit": 100}, headers=headers).json()
    d = detail(c, headers)
    body = {"contract_version": VERSION, "selection_ref": d["selection"]["selection_ref"]}
    created = c.post(ROOT + "/start", json=body, headers=headers)
    refused = c.post(ROOT + "/start", json=body, headers=headers)
    assert created.status_code == 201 and refused.status_code == 409
    target = os.getenv("AUREN_MOB06_WITNESS_PATH")
    if target:
        Path(target).write_text(
            json.dumps(
                {
                    "source": "synthetic-real-router-domain-SQLite-test",
                    "base_sha": "1462482a4e2bcd1fcde121d6f207a2131616e849",
                    "page": page,
                    "detail": d,
                    "request": body,
                    "created": created.json(),
                    "refused": refused.json(),
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n"
        )
