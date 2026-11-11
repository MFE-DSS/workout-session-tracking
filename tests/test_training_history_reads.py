"""Owned historical facts, not reconstructed prescriptions or strength analytics."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import event

from tests import plan_v3_test_support as support

science_bundle = support.science_bundle

NOW = datetime(2026, 11, 10, 12, tzinfo=UTC)


def add_session(
    db,
    owner,
    *,
    started=NOW,
    status="completed",
    excluded=False,
    reps=None,
    weight=None,
    kind="work",
    completed=None,
):
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    session = WorkoutSession(
        user_id=owner,
        started_at=started,
        ended_at=NOW if status == "completed" else None,
        status=status,
        excluded_from_stats=excluded,
        template_slug_snapshot="captured-template",
        template_name_snapshot="Captured session",
    )
    db.add(session)
    db.flush()
    exercise = SessionExercise(
        session_id=session.id,
        position=0,
        exercise_code_snapshot="A1",
        exercise_name_snapshot="Captured exercise",
    )
    db.add(exercise)
    db.flush()
    db.add(
        SetLog(
            session_exercise_id=exercise.id,
            kind=kind,
            set_index=1,
            reps=reps,
            weight_kg=weight,
            completed=(reps is not None or weight is not None) if completed is None else completed,
        )
    )
    db.commit()
    return session


@pytest.mark.parametrize(
    ("period", "start", "weeks"),
    [
        ("4w", "2026-10-18T22:00:00Z", 4),
        ("12w", "2026-08-23T22:00:00Z", 12),
        ("all", None, 0),
    ],
)
def test_empty_period_uses_local_calendar_across_dst_not_fixed_24h_days(
    client, period, start, weeks
):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.training_history_reads import read_sessions

    with SessionLocal() as db:
        owner = db.query(User).one().id
        page = read_sessions(db, owner, period=period, time_zone="Europe/Paris", now=NOW)
        assert page["contract_version"] == "training-history/1.0.0"
        assert page["owner_id"] == owner
        assert page["window"] == {
            "period": period,
            "time_zone": "Europe/Paris",
            "from": start,
            "until": "2026-11-10T12:00:00Z",
        }
        assert page["state"] == "EMPTY"
        assert page["counts"]["completed_with_work"] == 0
        assert page["planned_calendar"] == {"state": "NOT_PERSISTED", "count": None}
        assert len(page["weekly_counts"]) == weeks
        assert page["membership"] == "LIVE_BOUNDED_MEMBERSHIP"
        assert page["next_cursor"] is None


@pytest.mark.parametrize(
    ("period", "zone"),
    [("month", "UTC"), ("4w", ""), ("4w", "Europe/NoSuchZone"), ("4w", "../../etc/passwd")],
)
def test_invalid_period_or_missing_declared_timezone_is_not_silently_normalized(
    client, period, zone
):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.training_history_reads import HistoryReadError, read_sessions

    with SessionLocal() as db:
        with pytest.raises(HistoryReadError) as error:
            read_sessions(db, db.query(User).one().id, period=period, time_zone=zone, now=NOW)
        assert error.value.status == 422


def test_completed_empty_warmup_excluded_and_explicit_zero_remain_distinct(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.training_history_reads import read_sessions

    with SessionLocal() as db:
        owner = db.query(User).one().id
        add_session(db, owner)
        add_session(db, owner, reps=5, kind="warmup")
        add_session(db, owner, reps=5, excluded=True)
        add_session(db, owner, reps=0)
        add_session(db, owner, reps=9, status="in_progress")
        page = read_sessions(db, owner, period="4w", time_zone="UTC", now=NOW.replace(hour=13))
        assert page["counts"] == {
            "state": "AVAILABLE",
            "recorded": 5,
            "completed": 4,
            "open": 1,
            "excluded": 1,
            "completed_with_work": 1,
        }
        assert sum(row["completed_with_work"] for row in page["weekly_counts"]) == 1
        assert page["weekly_counts"][-1]["partial_current_week"] is True


def test_pages_preserve_initial_bounds_counts_and_ceiling_without_counting_first_page_only(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.training_history_reads import read_sessions

    with SessionLocal() as db:
        owner = db.query(User).one().id
        originals = [
            add_session(db, owner, started=NOW.replace(day=day), reps=8).id for day in (6, 7, 8)
        ]
        first = read_sessions(db, owner, period="4w", time_zone="UTC", limit=1, now=NOW)
        assert first["counts"]["completed_with_work"] == 3
        assert [row["session_id"] for row in first["entries"]] == [originals[-1]]
        inserted = add_session(db, owner, started=NOW.replace(day=7), reps=9).id
        second = read_sessions(
            db,
            owner,
            period="4w",
            time_zone="UTC",
            limit=1,
            cursor=first["next_cursor"],
            now=NOW.replace(day=11),
        )
        assert second["read_id"] == first["read_id"]
        assert second["window"] == first["window"]
        assert second["counts_read_at"] == first["counts_read_at"]
        assert [row["session_id"] for row in second["entries"]] == [originals[-2]]
        assert inserted not in [row["session_id"] for row in second["entries"]]


def test_other_owner_null_owner_and_exact_until_are_excluded_without_any_dml(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.training_history_reads import read_sessions

    with SessionLocal() as db:
        owner = db.query(User).one().id
        other = User(username="other-history", password_hash="synthetic-unused")
        db.add(other)
        db.commit()
        add_session(db, other.id, started=NOW.replace(day=9), reps=8)
        add_session(db, None, started=NOW.replace(day=9), reps=8)
        add_session(db, owner, started=NOW, reps=8)
        own = add_session(db, owner, started=NOW.replace(day=9), reps=8)
        writes = []

        def trace(_connection, _cursor, statement, _parameters, _context, _many):
            if statement.lstrip().split(None, 1)[0].upper() in {"INSERT", "UPDATE", "DELETE"}:
                writes.append(statement)

        event.listen(db.get_bind(), "before_cursor_execute", trace)
        try:
            page = read_sessions(db, owner, period="4w", time_zone="UTC", now=NOW)
        finally:
            event.remove(db.get_bind(), "before_cursor_execute", trace)
        assert page["counts"]["recorded"] == 1
        assert [row["session_id"] for row in page["entries"]] == [own.id]
        assert writes == []


def test_cursor_is_owner_bound_signed_and_not_reusable_for_another_window(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.training_history_reads import HistoryReadError, read_sessions

    with SessionLocal() as db:
        owner = db.query(User).one().id
        for day in (6, 7):
            add_session(db, owner, started=NOW.replace(day=day), reps=8)
        page = read_sessions(db, owner, period="4w", time_zone="UTC", limit=1, now=NOW)
        for cursor, identity, period in [
            (page["next_cursor"] + "x", owner, "4w"),
            (page["next_cursor"], owner + 1, "4w"),
            (page["next_cursor"], owner, "12w"),
        ]:
            with pytest.raises(HistoryReadError):
                read_sessions(
                    db, identity, period=period, time_zone="UTC", limit=1, cursor=cursor, now=NOW
                )


def test_legacy_detail_reads_captured_names_and_facts_without_reconstructing_prescription(client):
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog
    from app.models.user import User
    from app.services.training_history_reads import read_session_facts, read_sessions

    with SessionLocal() as db:
        owner = db.query(User).one().id
        session = add_session(db, owner, started=NOW.replace(day=9), reps=8, weight=17.5)
        exercise = db.query(SessionExercise).filter_by(session_id=session.id).one()
        exercise.substituted_name = "Captured replacement"
        logged = db.query(SetLog).filter_by(session_exercise_id=exercise.id).one()
        logged.completed_at = NOW.replace(day=9, hour=10)
        db.commit()
        entry = read_sessions(db, owner, period="4w", time_zone="UTC", now=NOW)["entries"][0]
        facts = read_session_facts(db, owner, session.id, entry["entry_ref"])
        assert facts["contract_version"] == "training-session-facts/1.0.0"
        assert facts["execution_profile"] == "LEGACY_V1"
        assert facts["prescription"] == "UNKNOWN_NOT_CAPTURED"
        first = facts["exercises"][0]
        assert first["prescribed_name"] == "Captured exercise"
        assert first["executed_name"] == "Captured replacement"
        assert first["equipment_context"] == "UNKNOWN_NOT_CAPTURED"
        assert first["load_semantics"] == "UNKNOWN"
        assert first["sets"][0] == {
            "set_id": logged.id,
            "kind": "work",
            "set_index": 1,
            "completed": True,
            "reps": 8,
            "weight_kg": 17.5,
            "raw_weight_repr": None,
            "completed_at": "2026-11-09T10:00:00Z",
        }
        assert "success_score" not in first
        assert "bodyweight_kg" not in facts


def test_detail_looks_up_owner_before_reference_and_foreign_unknown_null_owner_share_404(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.training_history_reads import (
        HistoryReadError,
        read_session_facts,
        read_sessions,
    )

    with SessionLocal() as db:
        owner = db.query(User).one().id
        own = add_session(db, owner, started=NOW.replace(day=9), reps=8)
        unowned = add_session(db, None, started=NOW.replace(day=9), reps=8)
        entry = read_sessions(db, owner, period="4w", time_zone="UTC", now=NOW)["entries"][0]
        results = []
        for identity, session_id, ref in [
            (owner + 1, own.id, entry["entry_ref"]),
            (owner, unowned.id, entry["entry_ref"]),
            (owner, 999999, "bad"),
            (owner, own.id, "bad"),
        ]:
            with pytest.raises(HistoryReadError) as error:
                read_session_facts(db, identity, session_id, ref)
            results.append((error.value.status, error.value.code))
        assert results == [(404, "history_entry_not_found")] * 4


def test_captured_metadata_change_requires_refresh_but_set_correction_remains_readable(client):
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog
    from app.models.user import User
    from app.services.training_history_reads import (
        HistoryReadError,
        read_session_facts,
        read_sessions,
    )

    with SessionLocal() as db:
        owner = db.query(User).one().id
        session = add_session(db, owner, started=NOW.replace(day=9), reps=8)
        entry = read_sessions(db, owner, period="4w", time_zone="UTC", now=NOW)["entries"][0]
        exercise = db.query(SessionExercise).filter_by(session_id=session.id).one()
        logged = db.query(SetLog).filter_by(session_exercise_id=exercise.id).one()
        logged.reps = 9
        db.commit()
        assert (
            read_session_facts(db, owner, session.id, entry["entry_ref"])["exercises"][0]["sets"][
                0
            ]["reps"]
            == 9
        )
        exercise.exercise_name_snapshot = "Changed captured metadata"
        db.commit()
        with pytest.raises(HistoryReadError) as error:
            read_session_facts(db, owner, session.id, entry["entry_ref"])
        assert (error.value.status, error.value.code) == (409, "READ_CHANGED")
        fresh = read_sessions(db, owner, period="4w", time_zone="UTC", now=NOW)["entries"][0]
        assert (
            read_session_facts(db, owner, session.id, fresh["entry_ref"])["exercises"][0][
                "prescribed_name"
            ]
            == "Changed captured metadata"
        )


def test_a_context_token_cannot_be_used_as_an_entry_reference(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.training_history_reads import (
        HistoryReadError,
        read_session_facts,
        read_sessions,
    )

    with SessionLocal() as db:
        owner = db.query(User).one().id
        session = add_session(db, owner, started=NOW.replace(day=9), reps=8)
        page = read_sessions(db, owner, period="all", time_zone="UTC", now=NOW)
        with pytest.raises(HistoryReadError) as error:
            read_session_facts(db, owner, session.id, page["read_context"])
        assert error.value.status == 404


def test_unknown_scientific_profile_never_falls_back_to_legacy_detail(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.training_history_reads import (
        HistoryReadError,
        read_session_facts,
        read_sessions,
    )

    with SessionLocal() as db:
        owner = db.query(User).one().id
        session = add_session(db, owner, started=NOW.replace(day=9), reps=8)
        session.template_slug_snapshot = "science:v3:first-session"
        db.commit()
        entry = read_sessions(db, owner, period="4w", time_zone="UTC", now=NOW)["entries"][0]
        assert entry["execution_profile"] == "UNKNOWN"
        with pytest.raises(HistoryReadError) as error:
            read_session_facts(db, owner, session.id, entry["entry_ref"])
        assert error.value.status == 503


def test_nonfinite_legacy_load_is_retained_as_explicit_invalid_representation_not_zero(client):
    import json

    from app.database import SessionLocal
    from app.models.user import User
    from app.services.training_history_reads import read_session_facts, read_sessions

    with SessionLocal() as db:
        owner = db.query(User).one().id
        session = add_session(db, owner, started=NOW.replace(day=9), weight=float("inf"))
        entry = read_sessions(db, owner, period="4w", time_zone="UTC", now=NOW)["entries"][0]
        facts = read_session_facts(db, owner, session.id, entry["entry_ref"])
        row = facts["exercises"][0]["sets"][0]
        assert row["weight_kg"] is None
        assert row["raw_weight_repr"] == "inf"
        assert row["reps"] is None
        json.dumps(facts, allow_nan=False)


def test_exercise_index_uses_exact_alias_identity_without_fuzzy_name_merges(client):
    from app.database import SessionLocal
    from app.models.session import SessionExercise
    from app.models.user import User
    from app.services.exercise_identity import add_alias, ensure_exercise
    from app.services.training_history_reads import read_exercises, read_sessions

    with SessionLocal() as db:
        owner = db.query(User).one().id
        canonical = ensure_exercise(db, "Captured exercise")
        add_alias(db, canonical, "Exact accepted alias")
        for name, day in [
            ("Captured exercise", 9),
            ("Exact accepted alias", 8),
            ("Almost captured exercise", 7),
        ]:
            session = add_session(db, owner, started=NOW.replace(day=day), reps=8)
            db.query(SessionExercise).filter_by(
                session_id=session.id
            ).one().exercise_name_snapshot = name
            db.commit()
        page = read_sessions(db, owner, period="4w", time_zone="UTC", now=NOW)
        index = read_exercises(db, owner, read_context=page["read_context"])
        assert len(index["entries"]) == 1
        assert index["entries"][0]["identity"] == {
            "namespace": "LEGACY_EXERCISE",
            "id": canonical.slug,
        }
        assert index["unresolved_count"] == 1
        assert index["coverage_complete"] is True


def test_occurrences_follow_executed_identity_preserve_excluded_facts_and_bind_selection(client):
    from app.database import SessionLocal
    from app.models.session import SessionExercise
    from app.models.user import User
    from app.services.exercise_identity import ensure_exercise
    from app.services.training_history_reads import (
        HistoryReadError,
        read_exercises,
        read_occurrences,
        read_session_facts,
        read_sessions,
    )

    with SessionLocal() as db:
        owner = db.query(User).one().id
        ensure_exercise(db, "Captured exercise")
        replacement = ensure_exercise(db, "Replacement")
        first = add_session(db, owner, started=NOW.replace(day=9), reps=8, excluded=True)
        se = db.query(SessionExercise).filter_by(session_id=first.id).one()
        se.substituted_name = "Replacement"
        db.commit()
        add_session(db, owner, started=NOW.replace(day=8), reps=9)
        page = read_sessions(db, owner, period="all", time_zone="UTC", now=NOW)
        index = read_exercises(db, owner, read_context=page["read_context"])
        selected = next(e for e in index["entries"] if e["identity"]["id"] == replacement.slug)
        occurrences = read_occurrences(
            db, owner, selected["exercise_ref"], read_context=page["read_context"]
        )
        assert len(occurrences["entries"]) == 1
        occurrence = occurrences["entries"][0]
        assert occurrence["session_id"] == first.id
        assert occurrence["excluded_from_stats"] is True
        assert occurrence["comparison"] == "NON_COMPARABLE"
        facts = read_session_facts(
            db,
            owner,
            first.id,
            occurrence["entry_ref"],
            occurrence_ref=occurrence["occurrence_ref"],
        )
        assert facts["selected_se_id"] == se.id
        with pytest.raises(HistoryReadError):
            read_occurrences(
                db, owner + 1, selected["exercise_ref"], read_context=page["read_context"]
            )


def test_zero_matches_after_1000_inspected_rows_is_partial_scan_not_empty_history(client, monkeypatch):
    from app.database import SessionLocal
    from app.models.session import SessionExercise
    from app.models.user import User
    from app.services import training_history_reads as reads
    from app.services.exercise_identity import ensure_exercise
    from app.services.training_history_reads import read_exercises, read_sessions

    batches = []
    source_batch = reads._source_batch

    def observed_batch(db, context, after, count):
        rows = source_batch(db, context, after, count)
        batches.append((count, len(rows)))
        return rows

    monkeypatch.setattr(reads, "_source_batch", observed_batch)

    with SessionLocal() as db:
        owner = db.query(User).one().id
        ensure_exercise(db, "Captured exercise")
        session = add_session(db, owner, started=NOW.replace(day=9), reps=8)
        db.query(SessionExercise).filter_by(
            session_id=session.id
        ).one().exercise_name_snapshot = "unresolved-0"
        db.add_all(
            [
                SessionExercise(
                    session_id=session.id,
                    position=i,
                    exercise_code_snapshot="raw",
                    exercise_name_snapshot="Captured exercise" if i == 1000 else f"unresolved-{i}",
                )
                for i in range(1, 1001)
            ]
        )
        db.commit()
        page = read_sessions(db, owner, period="all", time_zone="UTC", now=NOW)
        partial = read_exercises(db, owner, read_context=page["read_context"])
        assert partial["entries"] == []
        assert partial["state"] == "SCANNING"
        assert partial["scan"] == "PARTIAL_SCAN"
        assert partial["source_inspected"] == 1000
        assert partial["coverage_complete"] is False
        assert partial["next_cursor"]
        assert len(batches) == 5
        assert sum(returned for _, returned in batches) == 1000
        assert all(requested <= 200 for requested, _ in batches)
        final = read_exercises(
            db, owner, read_context=page["read_context"], cursor=partial["next_cursor"]
        )
        assert len(final["entries"]) == 1
        assert final["source_inspected"] == 1
        assert final["scan"] == "EXHAUSTED"
        assert final["coverage_complete"] is True


def test_exercise_cursor_types_and_read_contexts_are_not_interchangeable(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.exercise_identity import ensure_exercise
    from app.services.training_history_reads import (
        HistoryReadError,
        read_exercises,
        read_occurrences,
        read_sessions,
    )

    with SessionLocal() as db:
        owner = db.query(User).one().id
        ensure_exercise(db, "Captured exercise")
        for day in (8, 9):
            add_session(db, owner, started=NOW.replace(day=day), reps=8)
        first = read_sessions(db, owner, period="4w", time_zone="UTC", limit=1, now=NOW)
        index = read_exercises(db, owner, read_context=first["read_context"], limit=1)
        ref = index["entries"][0]["exercise_ref"]
        second = read_sessions(db, owner, period="12w", time_zone="UTC", now=NOW)
        for context, cursor in [
            (first["read_context"], first["next_cursor"]),
            (second["read_context"], index["next_cursor"]),
        ]:
            with pytest.raises(HistoryReadError):
                read_exercises(db, owner, read_context=context, cursor=cursor)
        with pytest.raises(HistoryReadError):
            read_occurrences(db, owner, ref, read_context=second["read_context"])


def test_occurrence_reference_detects_executed_identity_change_without_hiding_session_facts(client):
    from app.database import SessionLocal
    from app.models.session import SessionExercise
    from app.models.user import User
    from app.services.exercise_identity import ensure_exercise
    from app.services.training_history_reads import (
        HistoryReadError,
        read_exercises,
        read_occurrences,
        read_session_facts,
        read_sessions,
    )

    with SessionLocal() as db:
        owner = db.query(User).one().id
        ensure_exercise(db, "Captured exercise")
        session = add_session(db, owner, started=NOW.replace(day=9), reps=8)
        page = read_sessions(db, owner, period="all", time_zone="UTC", now=NOW)
        exercise = read_exercises(db, owner, read_context=page["read_context"])["entries"][0]
        occurrence = read_occurrences(
            db, owner, exercise["exercise_ref"], read_context=page["read_context"]
        )["entries"][0]
        se = db.query(SessionExercise).filter_by(session_id=session.id).one()
        se.substituted_name = "Different actual movement"
        db.commit()
        with pytest.raises(HistoryReadError) as error:
            read_session_facts(
                db,
                owner,
                session.id,
                occurrence["entry_ref"],
                occurrence_ref=occurrence["occurrence_ref"],
            )
        assert (error.value.status, error.value.code) == (409, "READ_CHANGED")
        # Session links now seal the executed identity too; refresh obtains the
        # changed facts without reusing a stale exercise link.
        with pytest.raises(HistoryReadError) as old_entry:
            read_session_facts(db, owner, session.id, occurrence["entry_ref"])
        assert (old_entry.value.status, old_entry.value.code) == (409, "READ_CHANGED")
        fresh = read_sessions(db, owner, period="all", time_zone="UTC", now=NOW)["entries"][0]
        assert (
            read_session_facts(db, owner, session.id, fresh["entry_ref"])["exercises"][0][
                "executed_name"
            ]
            == "Different actual movement"
        )


def test_actual_v3_history_keeps_typed_facts_after_withdrawal_without_legacy_projection(
    client, monkeypatch, science_bundle
):
    from app.config import get_settings
    from app.database import SessionLocal
    from app.models.first_plan_runtime import FirstPlanRuntimeAuthority
    from app.models.session import SetLog, WorkoutSession
    from app.models.user import User
    from app.services.plan_v3.commands import start_owned_first_session
    from app.services.plan_v3.execution import first_plan_execution_read_model
    from app.services.plan_v3.journal import record_first_plan_set
    from app.services.training_history_reads import (
        HistoryReadError,
        read_exercises,
        read_occurrences,
        read_session_facts,
        read_sessions,
    )
    from tests.test_first_session_commands import final_evaluation, start_body
    from tests.test_plan_v3_persistence import install

    install()
    monkeypatch.setattr(get_settings(), "plan_v3_bundle_path", str(science_bundle[0]))
    with SessionLocal() as db:
        owner = db.query(User).one().id
        evaluation = final_evaluation(db, owner, science_bundle, monkeypatch)
        command = start_owned_first_session(
            db, owner, request_id="progress-owned-first", body=start_body(evaluation)
        )
        db.commit()
        execution = first_plan_execution_read_model(db, owner, command.session_id)
        chosen = [
            execution["exercises"][0],
            next(
                row
                for row in execution["exercises"]
                if row["prescription"]["context"]["load_semantics"] == "PER_IMPLEMENT"
            ),
        ]
        for index, row in enumerate(chosen):
            record_first_plan_set(
                db,
                owner,
                command.session_id,
                row["sets"][0]["set_id"],
                op_id=f"progress-fact-{index}",
                expected_set_revision=0,
                observation={
                    "setting": {
                        "kind": "MASS_KG",
                        "value": 17.5 if index == 0 else 20,
                        "unit": "kg",
                    },
                    "context": row["prescription"]["context"],
                    "performed_at_estimated": True,
                    "reps": 9,
                    "completed": True,
                    "performed_at": datetime.now(UTC).isoformat(),
                },
            )
        session = db.get(WorkoutSession, command.session_id)
        session.status = "completed"
        session.ended_at = datetime.now(UTC)
        authority = db.get(FirstPlanRuntimeAuthority, "first-session-runtime/3.0.0")
        authority.state = "WITHDRAWN"
        authority.generation += 1
        db.commit()
        writes = []

        def trace(_connection, _cursor, statement, _parameters, _context, _many):
            if statement.lstrip().split(None, 1)[0].upper() in {"INSERT", "UPDATE", "DELETE"}:
                writes.append(statement)

        event.listen(db.get_bind(), "before_cursor_execute", trace)
        try:
            page = read_sessions(
                db,
                owner,
                period="all",
                time_zone="UTC",
                now=datetime.now(UTC) + timedelta(seconds=1),
            )
            entry = page["entries"][0]
            assert entry["execution_profile"] == "SCI_V3"
            assert len(entry["descriptor"]["mapping"]) == 7
            assert page["counts"]["completed_with_work"] == 1
            with pytest.raises(HistoryReadError) as error:
                read_session_facts(db, owner, command.session_id, entry["entry_ref"])
            assert (error.value.status, error.value.code) == (409, "execution_profile_required")
            index = read_exercises(db, owner, read_context=page["read_context"])
            assert len(index["entries"]) == 7
            assert all(
                row["identity"]["namespace"] == "SCI_CANONICAL_EXERCISE" for row in index["entries"]
            )
            occurrences = read_occurrences(
                db, owner, index["entries"][0]["exercise_ref"], read_context=page["read_context"]
            )
            assert len(occurrences["entries"]) == 1
        finally:
            event.remove(db.get_bind(), "before_cursor_execute", trace)
        assert writes == []
        historical = first_plan_execution_read_model(db, owner, command.session_id)
        assert historical["applicability"]["state"] != "CURRENT"
        assert historical["exercises"][0]["sets"][0]["observation"]["setting"]["value"] == 17.5
        assert all(db.get(SetLog, row["sets"][0]["set_id"]).weight_kg is None for row in chosen)


def test_session_exercise_links_reuse_the_exact_owned_index_reference(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.exercise_identity import ensure_exercise
    from app.services.training_history_reads import read_exercises, read_occurrences, read_sessions

    with SessionLocal() as db:
        owner = db.query(User).one().id
        ensure_exercise(db, "Captured exercise")
        session = add_session(db, owner, started=NOW-timedelta(minutes=1), reps=9, weight=17.5)
        page = read_sessions(db, owner, period="4w", time_zone="UTC", now=NOW)
        entry = page["entries"][0]
        link = entry["exercise_links"][0]
        index = read_exercises(db, owner, read_context=page["read_context"])
        assert link["exercise_ref"] == index["entries"][0]["exercise_ref"]
        occurrences = read_occurrences(db, owner, link["exercise_ref"], read_context=page["read_context"])
        assert occurrences["entries"][0]["session_id"] == session.id
        assert occurrences["entries"][0]["se_id"] == link["se_id"]


def test_unknown_exercise_link_is_not_guessed_and_new_identity_invalidates_old_read(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.exercise_identity import ensure_exercise
    from app.services.training_history_reads import (
        HistoryReadError,
        read_session_facts,
        read_sessions,
    )

    with SessionLocal() as db:
        owner = db.query(User).one().id
        session = add_session(db, owner, started=NOW-timedelta(minutes=1), reps=9)
        entry = read_sessions(db, owner, period="4w", time_zone="UTC", now=NOW)["entries"][0]
        assert entry["exercise_links"][0]["exercise_ref"] is None
        assert read_session_facts(db, owner, session.id, entry["entry_ref"])["session"]["session_id"] == session.id
        ensure_exercise(db, "Captured exercise")
        db.commit()
        with pytest.raises(HistoryReadError) as changed:
            read_session_facts(db, owner, session.id, entry["entry_ref"])
        assert (changed.value.status, changed.value.code) == (409, "READ_CHANGED")
