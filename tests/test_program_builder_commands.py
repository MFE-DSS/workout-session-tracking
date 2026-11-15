"""MOB07 real SQLite owner/CAS/receipt and historical source boundaries."""

import pytest
from sqlalchemy import select


def test_create_replay_owner_and_cas(client):
    from app.database import SessionLocal
    from app.models.program_builder_operations import ProgramBuilderOperation
    from app.models.user import User
    from app.services.program_builder_commands import (
        ProgramBuilderError,
        apply_command,
        read_program,
    )

    ProgramBuilderOperation.__table__.create(SessionLocal.kw["bind"], checkfirst=True)
    with SessionLocal() as db:
        owner = db.scalar(select(User.id))
        body = dict(
            contract_version="program-builder/1.0.0",
            command_id="create-1",
            operation="CREATE",
            program_id=None,
            expected_source_digest=None,
            payload={"title": "Mon programme"},
        )
        receipt = apply_command(db, owner, body, auth_proof={}, controlled=True)
        assert receipt["program_id"] > 0
        assert apply_command(db, owner, body, auth_proof={}, controlled=False) == receipt
        changed = {**body, "payload": {"title": "Autre"}}
        with pytest.raises(ProgramBuilderError) as error:
            apply_command(db, owner, changed, auth_proof={}, controlled=True)
        assert (error.value.code, error.value.status) == ("command_conflict", 409)
        rename = {
            **body,
            "command_id": "rename-1",
            "operation": "RENAME",
            "program_id": receipt["program_id"],
            "expected_source_digest": receipt["resulting_source_digest"],
            "payload": {"title": "Renommé"},
        }
        apply_command(db, owner, rename, auth_proof={}, controlled=True)
        with pytest.raises(ProgramBuilderError) as error:
            apply_command(
                db, owner, {**rename, "command_id": "stale"}, auth_proof={}, controlled=True
            )
        assert error.value.status == 409
        assert read_program(db, owner, receipt["program_id"])["title"] == "Renommé"
        with pytest.raises(ProgramBuilderError) as error:
            read_program(db, owner, 999999)
        assert error.value.status == 404


def test_command_strict_shape_and_hash(client):
    from app.services.program_builder_commands import (
        ProgramBuilderError,
        canonical_command,
        command_digest,
    )

    body = dict(
        contract_version="program-builder/1.0.0",
        command_id="a",
        operation="CREATE",
        program_id=None,
        expected_source_digest=None,
        payload={"title": "Été"},
    )
    assert canonical_command(body) == body
    assert len(command_digest(body)) == 64
    for bad in (
        {**body, "extra": 1},
        {**body, "program_id": True},
        {**body, "payload": {"title": "x", "extra": 1}},
    ):
        with pytest.raises(ProgramBuilderError):
            canonical_command(bad)


def test_keep_preserves_historical_unknown_target_indexes_and_old_bounds(client):
    from app.database import SessionLocal
    from app.models.program_builder_operations import ProgramBuilderOperation
    from app.models.user import User
    from app.services.program_builder_commands import apply_command, read_program
    from app.services.user_program_drafts import create_draft, get_draft, replace_draft_tree

    ProgramBuilderOperation.__table__.create(SessionLocal.kw["bind"], checkfirst=True)
    with SessionLocal() as db:
        owner = db.scalar(select(User.id))
        p = create_draft(db, owner, "Histoire", "histoire")
        replace_draft_tree(
            db,
            owner,
            p.id,
            [
                {
                    "position": 1,
                    "name": "Ancien",
                    "exercises": [
                        {
                            "position": 1,
                            "exercise_name": "Mouvement manuel inconnu",
                            "set_scheme": "ancien texte",
                            "source_reason": "legacy",
                            "notes": "figé",
                            "rep_targets": [
                                {
                                    "min_reps": 0,
                                    "max_reps": 80,
                                    "technique": "old",
                                    "is_warmup": True,
                                }
                            ],
                        }
                    ],
                }
            ],
        )
        p = get_draft(db, owner, p.id)
        p.sessions[0].exercises[0].rep_targets[0].set_index = 4
        db.commit()
        before = read_program(db, owner, p.id)
        slot = before["sessions"][0]["exercises"][0]
        sessions = [
            {
                **{k: v for k, v in before["sessions"][0].items() if k != "exercises"},
                "exercises": [
                    {
                        "position": 1,
                        "selection": None,
                        "keep": {"slot_id": slot["slot_id"], "slot_digest": slot["slot_digest"]},
                        "rep_targets": None,
                        "notes": None,
                    }
                ],
            }
        ]
        apply_command(
            db,
            owner,
            dict(
                contract_version="program-builder/1.0.0",
                command_id="keep",
                operation="SAVE_TREE",
                program_id=p.id,
                expected_source_digest=before["source_digest"],
                payload={"sessions": sessions},
            ),
            auth_proof={},
            controlled=True,
        )
        after = read_program(db, owner, p.id)["sessions"][0]["exercises"][0]
        assert after["rep_targets"] == slot["rep_targets"]
        assert after["set_scheme"] == "ancien texte"
        assert after["identity"]["state"] == "UNRESOLVED"
        assert after["source_reason"] == "legacy"


def test_failed_publish_rolls_back_frozen_quality_and_templates(client, monkeypatch):
    from app.database import SessionLocal
    from app.models.catalog import WorkoutTemplate
    from app.models.program_builder_operations import ProgramBuilderOperation
    from app.models.user import User
    from app.models.user_program import UserProgramQualityReview
    from app.services import user_program_publish
    from app.services.program_builder_commands import apply_command, read_program
    from app.services.user_program_drafts import (
        create_draft,
        get_draft,
        replace_draft_tree,
        validate_draft,
    )

    ProgramBuilderOperation.__table__.create(SessionLocal.kw["bind"], checkfirst=True)
    with SessionLocal() as db:
        owner = db.scalar(select(User.id))
        p = create_draft(db, owner, "Atomique", "atomique")
        replace_draft_tree(
            db,
            owner,
            p.id,
            [
                {
                    "position": 1,
                    "name": "A",
                    "exercises": [
                        {
                            "position": 1,
                            "exercise_name": "manuel",
                            "set_scheme": "1x 8-12",
                            "rep_targets": [{"min_reps": 8, "max_reps": 12}],
                        }
                    ],
                }
            ],
        )
        validate_draft(db, owner, p.id)
        source = read_program(db, owner, p.id)
        initial = list(db.scalars(select(WorkoutTemplate.id)))

        def fail(*args):
            raise RuntimeError("injected after freeze")

        monkeypatch.setattr(user_program_publish, "_materialize_session", fail)
        body = dict(
            contract_version="program-builder/1.0.0",
            command_id="publish-failed",
            operation="PUBLISH",
            program_id=p.id,
            expected_source_digest=source["source_digest"],
            payload={},
        )
        with pytest.raises(RuntimeError, match="injected"):
            apply_command(db, owner, body, auth_proof={}, controlled=True)
        assert get_draft(db, owner, p.id).status == "validated"
        assert not list(
            db.scalars(
                select(UserProgramQualityReview).where(
                    UserProgramQualityReview.user_program_id == p.id
                )
            )
        )
        assert list(db.scalars(select(WorkoutTemplate.id))) == initial
        assert not list(db.scalars(select(ProgramBuilderOperation)))


@pytest.mark.parametrize("field,value", [("kind", []), ("notes", "\ud800")])
def test_new_tree_invalid_unicode_and_shapes_are_definite_refusals(client, field, value):
    from app.services.program_builder_commands import ProgramBuilderError, canonical_command

    session = {
        "position": 1,
        "name": "A",
        "kind": "strength",
        "focus": "",
        "duration_target_minutes": None,
        "notes": None,
        "exercises": [],
    }
    session[field] = value
    command = {
        "contract_version": "program-builder/1.0.0",
        "command_id": "invalid",
        "operation": "SAVE_TREE",
        "program_id": 1,
        "expected_source_digest": "a" * 64,
        "payload": {"sessions": [session]},
    }
    with pytest.raises(ProgramBuilderError) as error:
        canonical_command(command)
    assert error.value.status == 422


def test_two_real_connections_compete_for_last_quota_place(client):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    from app.database import SessionLocal
    from app.models.user import User
    from app.models.user_program import UserProgram
    from app.services.user_program_drafts import UserProgramDraftError, create_draft

    with SessionLocal() as db:
        owner = db.scalar(select(User.id))
        for index in range(9):
            create_draft(db, owner, f"Existing {index}", f"existing-{index}")
    barrier = Barrier(2)

    def writer(index):
        with SessionLocal() as db:
            # An old reader must not be accepted as quota authority.
            db.scalar(select(UserProgram.id).where(UserProgram.user_id == owner).limit(1))
            barrier.wait(timeout=10)
            try:
                create_draft(db, owner, f"Concurrent {index}", f"concurrent-{index}")
                return "created"
            except UserProgramDraftError:
                return "quota"

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(writer, [1, 2]))
    assert sorted(results) == ["created", "quota"]
    with SessionLocal() as db:
        assert len(list(db.scalars(select(UserProgram).where(UserProgram.user_id == owner)))) == 10


def test_native_identity_stale_and_foreign_keep_refused_without_source_change(client):
    from app.database import SessionLocal
    from app.models.exercise import Exercise
    from app.models.program_builder_operations import ProgramBuilderOperation
    from app.models.user import User
    from app.services.mobile_program_builder import picker
    from app.services.program_builder_commands import (
        ProgramBuilderError,
        apply_command,
        read_program,
    )
    from app.services.user_program_drafts import create_draft, replace_draft_tree

    ProgramBuilderOperation.__table__.create(SessionLocal.kw["bind"], checkfirst=True)
    with SessionLocal() as db:
        owner = db.scalar(select(User.id))
        p = create_draft(db, owner, "Identité", "identity")
        options = picker(db)
        selection = {k: options[0][k] for k in ("slug", "name", "ekb_version")}
        source = read_program(db, owner, p.id)
        chosen = db.scalar(select(Exercise).where(Exercise.slug == selection["slug"]))
        chosen.name = "Identity no longer canonical"
        chosen.aliases.clear()
        db.commit()
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
        command = {
            "contract_version": "program-builder/1.0.0",
            "command_id": "stale-selection",
            "operation": "SAVE_TREE",
            "program_id": p.id,
            "expected_source_digest": source["source_digest"],
            "payload": {"sessions": sessions},
        }
        with pytest.raises(ProgramBuilderError) as error:
            apply_command(db, owner, command, auth_proof={}, controlled=True)
        assert (error.value.code, error.value.status) == ("stale_selection", 409)
        assert read_program(db, owner, p.id)["sessions"] == []
        other = User(username="other-builder", password_hash="synthetic")
        db.add(other)
        db.commit()
        foreign = create_draft(db, other.id, "Foreign", "foreign")
        replace_draft_tree(
            db,
            other.id,
            foreign.id,
            [
                {
                    "position": 1,
                    "name": "X",
                    "exercises": [
                        {
                            "position": 1,
                            "exercise_name": "unknown",
                            "set_scheme": "old",
                            "rep_targets": [{"min_reps": 0, "max_reps": 80}],
                        }
                    ],
                }
            ],
        )
        foreign_source = read_program(db, other.id, foreign.id)
        slot = foreign_source["sessions"][0]["exercises"][0]
        sessions[0]["exercises"][0] = {
            "position": 1,
            "selection": None,
            "keep": {"slot_id": slot["slot_id"], "slot_digest": slot["slot_digest"]},
            "rep_targets": None,
            "notes": None,
        }
        command["command_id"] = "foreign-keep"
        with pytest.raises(ProgramBuilderError) as error:
            apply_command(db, owner, command, auth_proof={}, controlled=True)
        assert error.value.status == 409
        with pytest.raises(ProgramBuilderError) as error:
            read_program(db, owner, foreign.id)
        assert error.value.status == 404


@pytest.mark.parametrize("key", ["key/with/slash", "?query", " leading", "-leading"])
def test_command_keys_are_recoverable_single_path_segments(client, key):
    from app.services.program_builder_commands import ProgramBuilderError, canonical_command

    command = {
        "contract_version": "program-builder/1.0.0",
        "command_id": key,
        "operation": "CREATE",
        "program_id": None,
        "expected_source_digest": None,
        "payload": {"title": "Key"},
    }
    with pytest.raises(ProgramBuilderError):
        canonical_command(command)


def test_exact_unambiguous_ekb_alias_keeps_canonical_selection(client):
    import json

    from app.database import SessionLocal
    from app.models.exercise import Exercise
    from app.services.mobile_program_builder import picker
    from app.services.user_program_exercise_catalog import _EKB_PATH

    with _EKB_PATH.open(encoding="utf-8") as source:
        ekb = json.load(source)
    with SessionLocal() as db:
        # Use a canonical identity already present in the synthetic seed and
        # retain its immutable slug while its current name becomes an exact alias.
        existing = {e.name: e for e in db.scalars(select(Exercise))}
        alias, canonical = next((a, n) for a, n in ekb["_aliases"].items() if n in existing)
        row = existing[canonical]
        slug = row.slug
        row.name = alias
        row.aliases.clear()
        db.commit()
        matches = [e for e in picker(db) if e["slug"] == slug]
        assert len(matches) == 1
        assert matches[0]["name"] == canonical


@pytest.mark.parametrize("duration", [0, -10, 1441])
def test_duration_is_declared_safe_integer_without_invented_new_bounds(client, duration):
    from app.services.program_builder_commands import canonical_command

    session = {
        "position": 1,
        "name": "A",
        "kind": "strength",
        "focus": "",
        "duration_target_minutes": duration,
        "notes": None,
        "exercises": [],
    }
    command = {
        "contract_version": "program-builder/1.0.0",
        "command_id": "duration",
        "operation": "SAVE_TREE",
        "program_id": 1,
        "expected_source_digest": "a" * 64,
        "payload": {"sessions": [session]},
    }
    assert canonical_command(command) == command
