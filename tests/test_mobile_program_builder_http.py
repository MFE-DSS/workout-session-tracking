"""Actual mounted builder API and owned source/readback, synthetic SQLite only."""

import pytest

ROOT = "/api/mobile/v1/me/program-builder"
VERSION = "program-builder/1.0.0"
HEADER = "X-Auren-Program-Builder"


@pytest.fixture
def api(client):
    from pydantic import SecretStr

    from app.config import get_settings
    from app.database import SessionLocal
    from app.models.program_builder_operations import ProgramBuilderOperation
    from app.models.user import User
    from app.services.device_auth import open_device_session

    settings = get_settings()
    settings.program_builder_backend_identity = "synthetic-builder"
    settings.program_builder_signing_key = SecretStr("b" * 40)
    settings.program_builder_controlled_test_enabled = True
    ProgramBuilderOperation.__table__.create(SessionLocal.kw["bind"], checkfirst=True)
    with SessionLocal() as db:
        user = db.query(User).one()
        issued = open_device_session(db, user)
        db.commit()
        owner = user.id
    return client, {HEADER: VERSION, "Authorization": f"Bearer {issued.access_token}"}, owner


def body(key, op, receipt=None, payload=None):
    return {
        "contract_version": VERSION,
        "command_id": key,
        "operation": op,
        "program_id": receipt["program_id"] if receipt else None,
        "expected_source_digest": receipt["resulting_source_digest"] if receipt else None,
        "payload": payload or {},
    }


def post(c, headers, command):
    pre = (
        {"If-None-Match": "*"}
        if command["operation"] == "CREATE"
        else {"If-Match": command["expected_source_digest"]}
    )
    return c.post(ROOT + "/commands", json=command, headers={**headers, **pre})


def test_http_real_create_save_validate_publish_and_exact_receipt(api):
    c, h, owner = api
    created = post(c, h, body("create", "CREATE", payload={"title": "HTTP réel"}))
    assert created.status_code == 200, created.text
    receipt = created.json()
    assert receipt["owner_id"] == owner
    picker = c.get(ROOT + "/exercises", headers=h)
    assert picker.status_code == 200, picker.text
    selection = {k: picker.json()["items"][0][k] for k in ("slug", "name", "ekb_version")}
    sessions = [
        {
            "position": 1,
            "name": "A",
            "kind": "strength",
            "focus": "",
            "duration_target_minutes": None,
            "notes": None,
            "exercises": [
                {
                    "position": 1,
                    "selection": selection,
                    "keep": None,
                    "rep_targets": [
                        {"min_reps": 8, "max_reps": 12, "technique": None, "is_warmup": False}
                    ],
                    "notes": None,
                }
            ],
        }
    ]
    sent_commands = {}
    for key, op, payload in [
        ("save", "SAVE_TREE", {"sessions": sessions}),
        ("validate", "VALIDATE", {}),
        ("publish", "PUBLISH", {}),
    ]:
        sent_commands[key] = body(key, op, receipt, payload)
        result = post(c, h, sent_commands[key])
        assert result.status_code == 200, result.text
        receipt = result.json()
    assert len(receipt["publication_ids"]) == 1
    detail = c.get(ROOT + f"/programs/{receipt['program_id']}", headers=h)
    assert detail.status_code == 200, detail.text
    assert detail.json()["program"]["status"] == "published"
    assert detail.headers["cache-control"] == "no-store"
    assert c.get(ROOT + "/operations/publish", headers=h).json() == receipt
    # Read the new canonical publication through MOB06, then start the same
    # owned occurrence consumed by execution, mission and training history.
    from pydantic import SecretStr

    from app.config import get_settings

    settings = get_settings()
    settings.library_backend_identity = "synthetic-builder-library"
    settings.library_signing_key = SecretStr("l" * 40)
    settings.library_controlled_test_enabled = True
    library_headers = {**h, "X-Auren-Library-Contract": "owned-library/1.0.0"}
    index = c.get(
        "/api/mobile/v1/me/library", params={"section": "programs"}, headers=library_headers
    )
    assert index.status_code == 200, index.text
    entry = next(e for e in index.json()["entries"] if e["name"] == "HTTP réel")
    library_detail = c.get(
        "/api/mobile/v1/me/library/items/" + entry["source_ref"], headers=library_headers
    )
    assert library_detail.status_code == 200, library_detail.text
    chosen = library_detail.json()["composition"][0]["selection"]
    started = c.post(
        "/api/mobile/v1/me/library/start",
        json={"contract_version": "owned-library/1.0.0", "selection_ref": chosen["selection_ref"]},
        headers=library_headers,
    )
    assert started.status_code == 201, started.text
    session_id = started.json()["execution"]["session_id"]
    execution = c.get(f"/api/mobile/v1/sessions/{session_id}/execution", headers=h)
    assert execution.status_code == 200
    assert execution.json()["session_id"] == session_id
    action = c.get(
        "/api/mobile/v1/mission-action",
        params={"requested_path": "FIRST_USE"},
        headers={**h, "X-Auren-Mission-Action": "mission-action/1.0.0"},
    )
    assert action.status_code == 200, action.text
    assert action.json()["primary_action"]["session_id"] == session_id
    history = c.get(
        "/api/mobile/v1/me/training-history",
        params={"period": "all", "time_zone": "UTC"},
        headers=h,
    )
    assert history.status_code == 200, history.text
    assert any(e["session_id"] == session_id for e in history.json()["entries"])
    cycle = post(c, h, body("cycle", "NEW_CYCLE", receipt, {}))
    assert cycle.status_code == 200, cycle.text
    assert cycle.json()["resulting_version"] == 2
    assert cycle.json()["publication_ids"] == []
    # Exact old publication receipt survives a subsequent edit cycle, and the
    # original execution's planned facts/template identity stay unchanged.
    assert c.get(ROOT + "/operations/publish", headers=h).json() == receipt
    after_cycle = c.get(f"/api/mobile/v1/sessions/{session_id}/execution", headers=h).json()
    before_cycle = execution.json()
    after_cycle.pop("server_now")
    before_cycle.pop("server_now")
    assert after_cycle == before_cycle
    # Fresh-operation permission withdrawal does not invalidate historical replay.
    from app.config import get_settings

    get_settings().program_builder_controlled_test_enabled = False
    assert c.post(ROOT + "/commands", headers=h, json=sent_commands["publish"]).json() == receipt
    assert c.get(ROOT + "/operations/publish", headers=h).json() == receipt
    assert (
        c.post(
            ROOT + "/commands",
            json=body("create", "CREATE", payload={"title": "HTTP réel"}),
            headers=h,
        ).json()
        == created.json()
    )
    assert post(c, h, body("blocked", "CREATE", payload={"title": "Blocked"})).status_code == 403


def test_bearer_challenge_and_strict_request(api):
    c, h, _ = api
    response = c.get(ROOT + "/programs", headers={HEADER: VERSION})
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Bearer"
    for suffix in ["/programs?limit=51", "/programs?limit=1&limit=2", "/exercises?extra=1"]:
        assert c.get(ROOT + suffix, headers=h).status_code == 422
    assert (
        c.post(
            ROOT + "/commands", json=body("missing", "CREATE", payload={"title": "X"}), headers=h
        ).status_code
        == 428
    )


def test_web_missing_and_stale_rendered_token_refuse(api):
    import re

    c, h, _ = api
    create_page = c.get("/programs/new")
    token = re.search(r'name="source_digest" value="([0-9a-f]{64})"', create_page.text).group(1)
    assert (
        c.post("/programs", data={"title": "No token"}, follow_redirects=False).status_code == 428
    )
    created = c.post(
        "/programs", data={"title": "Web", "source_digest": token}, follow_redirects=False
    )
    assert created.status_code == 303, created.text
    url = created.headers["location"]
    page = c.get(url)
    source = re.search(r'name="source_digest" value="([0-9a-f]{64})"', page.text).group(1)
    assert (
        c.post(
            url + "/sessions", data={"name": "A", "source_digest": source}, follow_redirects=False
        ).status_code
        == 303
    )
    stale = c.post(
        url + "/sessions", data={"name": "B", "source_digest": source}, follow_redirects=False
    )
    assert stale.status_code == 409
    from app.database import SessionLocal
    from app.models.user_program import UserProgramSession

    with SessionLocal() as db:
        assert [s.name for s in db.query(UserProgramSession).all()] == ["A"]


def test_cursor_is_invalidated_by_owner_source_change(api):
    c, h, _ = api
    post(c, h, body("one", "CREATE", payload={"title": "One"}))
    post(c, h, body("two", "CREATE", payload={"title": "Two"}))
    first = c.get(ROOT + "/programs?limit=1", headers=h).json()
    post(c, h, body("three", "CREATE", payload={"title": "Three"}))
    stale = c.get(
        ROOT + "/programs", params={"limit": 1, "cursor": first["next_cursor"]}, headers=h
    )
    assert stale.status_code == 409


def test_detail_bounds_tree_before_loading_relationships(api):
    c, h, owner = api
    receipt = post(c, h, body("oversized", "CREATE", payload={"title": "Oversized"})).json()
    from app.database import SessionLocal
    from app.models.user_program import UserProgramSession

    with SessionLocal() as db:
        db.add_all(
            [
                UserProgramSession(user_program_id=receipt["program_id"], position=i, name="S")
                for i in range(1, 1002)
            ]
        )
        db.commit()
    response = c.get(ROOT + f"/programs/{receipt['program_id']}", headers=h)
    assert response.status_code == 413


@pytest.mark.parametrize("operation,archived", [("PUBLISH", False), ("NEW_CYCLE", True)])
def test_known_lifecycle_refusal_is_definite_not_storage_uncertainty(api, operation, archived):
    c, h, _ = api
    receipt = post(c, h, body("lifecycle-create", "CREATE", payload={"title": "Lifecycle"})).json()
    if archived:
        receipt = post(c, h, body("lifecycle-archive", "ARCHIVE", receipt, {})).json()
    response = post(c, h, body("lifecycle-refused", operation, receipt, {}))
    assert response.status_code == 409, response.text
    assert response.json()["detail"]["error"] == "domain_refused"
    assert c.get(ROOT + "/operations/lifecycle-refused", headers=h).status_code == 404


def test_weekly_observer_runs_after_atomic_source_commit(api, monkeypatch):
    from program_builder_web_helpers import post_program

    from app.database import SessionLocal
    from app.models.user_program import UserProgram
    from app.services import decision_analytics
    from app.services.training_preferences import save_training_preferences

    c, _, owner = api
    with SessionLocal() as db:
        save_training_preferences(db, owner, sessions_per_week=4)
    observed = []

    def observer(db, user_id, plan):
        with SessionLocal() as independent:
            observed.append(
                independent.query(UserProgram).filter(UserProgram.user_id == user_id).count()
            )

    monkeypatch.setattr(decision_analytics, "observe_plan_generation_for_user", observer)
    response = post_program(c, "/programs/from-weekly-plan", follow_redirects=False)
    assert response.status_code == 303, response.text
    assert observed == [1]


def _three_full_legal_programs(owner):
    from app.database import SessionLocal
    from app.services.user_program_drafts import create_draft, replace_draft_tree

    program_ids = []
    with SessionLocal() as db:
        for index in range(3):
            program = create_draft(db, owner, f"Legal full {index}", f"legal-full-{index}")
            tree = [
                {
                    "position": s,
                    "name": f"Séance {s}",
                    "kind": "strength",
                    "focus": "",
                    "duration_target_minutes": None,
                    "notes": None,
                    "exercises": [
                        {
                            "position": e,
                            "exercise_name": f"Manuel {e}",
                            "set_scheme": "6x 8-12",
                            "rep_targets": [{"min_reps": 8, "max_reps": 12} for _ in range(6)],
                        }
                        for e in range(1, 11)
                    ],
                }
                for s in range(1, 8)
            ]
            replace_draft_tree(db, owner, program.id, tree)
            program_ids.append(program.id)
    return program_ids


def test_collection_budget_is_per_program_and_off_page_tree_invalidates_cursor(api):
    from app.database import SessionLocal
    from app.routers.user_programs import _tree_to_payload
    from app.services.user_program_drafts import get_draft, replace_draft_tree

    c, h, owner = api
    program_ids = _three_full_legal_programs(owner)
    first = c.get(ROOT + "/programs?limit=1", headers=h)
    assert first.status_code == 200, first.text
    assert first.json()["items"][0]["id"] == program_ids[0]
    cursor = first.json()["next_cursor"]
    second = c.get(ROOT + "/programs", params={"limit": 1, "cursor": cursor}, headers=h)
    assert second.status_code == 200, second.text
    assert second.json()["items"][0]["id"] == program_ids[1]
    for program_id in program_ids:
        assert c.get(ROOT + f"/programs/{program_id}", headers=h).status_code == 200
    # Root title/status/version stay identical; an off-page numeric prescription
    # still invalidates the exact full-source watermark.
    with SessionLocal() as db:
        program = get_draft(db, owner, program_ids[-1])
        tree = _tree_to_payload(program)
        tree[0]["exercises"][0]["rep_targets"][0]["max_reps"] = 13
        replace_draft_tree(db, owner, program.id, tree)
    assert (
        c.get(ROOT + "/programs", params={"limit": 1, "cursor": cursor}, headers=h).status_code
        == 409
    )


def test_ssr_collection_token_accepts_several_legal_trees_and_detects_tree_change(api):
    import re

    from app.database import SessionLocal
    from app.models.user_program import UserProgram
    from app.routers.user_programs import _tree_to_payload
    from app.services.user_program_drafts import get_draft, replace_draft_tree

    c, _, owner = api
    program_ids = _three_full_legal_programs(owner)
    for url in ["/programs", "/plan", f"/programs/{program_ids[0]}"]:
        assert c.get(url).status_code == 200
    page = c.get("/programs/new")
    assert page.status_code == 200
    token = re.search(r'name="source_digest" value="([0-9a-f]{64})"', page.text).group(1)
    with SessionLocal() as db:
        program = get_draft(db, owner, program_ids[-1])
        tree = _tree_to_payload(program)
        tree[0]["exercises"][0]["rep_targets"][0]["min_reps"] = 9
        replace_draft_tree(db, owner, program.id, tree)
    stale = c.post(
        "/programs",
        data={"title": "Stale collection", "source_digest": token},
        follow_redirects=False,
    )
    assert stale.status_code == 409
    refreshed = c.get("/programs/new")
    current = re.search(r'name="source_digest" value="([0-9a-f]{64})"', refreshed.text).group(1)
    created = c.post(
        "/programs",
        data={"title": "Fourth legal root", "source_digest": current},
        follow_redirects=False,
    )
    assert created.status_code == 303, created.text
    with SessionLocal() as db:
        assert db.query(UserProgram).filter(UserProgram.user_id == owner).count() == 4
