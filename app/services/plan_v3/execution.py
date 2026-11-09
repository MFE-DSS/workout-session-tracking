"""Lossless bridge into the canonical session graph, without a template builder."""

from __future__ import annotations

from datetime import UTC, datetime

from app.models.first_plan_runtime import FirstPlanExecutionBinding
from app.models.session import SessionExercise, SetLog, WorkoutSession
from app.services.plan_v3.snapshots import canonical, digest
from app.services.plan_v3.transactions import RuntimeFailure

MARKER = "science:v3:first-session"
EXECUTION_VERSION = "first-plan-execution/3.0.0"
AUTHORITY_FIELDS = (
    "contract_version",
    "engine_version",
    "policy_version",
    "binding_ref",
    "binding_digest",
    "bundle_digest",
    "effective_science_digest",
    "request_fingerprint",
    "observation_fingerprint",
    "full_evaluation_fingerprint",
    "plan_time_fingerprint",
    "start_policy_ref",
)


def is_scientific_session(session):
    return getattr(session, "template_slug_snapshot", None) == MARKER


def materialize_first_plan_session(
    db, owner_id, *, validated_evaluation, result, first_scientific_session_id, started_at=None
):
    plan = result["candidate_plan"]
    scientific = plan["sessions"][0]
    if scientific["session_id"] != first_scientific_session_id:
        raise RuntimeFailure("first_scientific_session_required")
    # Check the complete projection before adding any canonical object.
    supported = {"TOTAL_EXTERNAL", "PER_IMPLEMENT", "MACHINE_DISPLAY_KG"}
    for slot in scientific["slots"]:
        prescription = slot["prescription"]
        if (
            prescription["mode"] != "OBSERVED_SETTING"
            or prescription["context"]["side"] != "BILATERAL"
            or prescription["context"]["load_semantics"] not in supported
            or prescription["setting"]["kind"] != "MASS_KG"
            or prescription["setting"]["unit"] != "kg"
        ):
            raise RuntimeFailure("execution_not_representable")
    session = WorkoutSession(
        user_id=owner_id,
        template_id=None,
        template_slug_snapshot=MARKER,
        template_name_snapshot="Première séance",
        started_at=started_at or datetime.now(UTC),
        status="in_progress",
    )
    db.add(session)
    db.flush()
    mapping = []
    for index, slot in enumerate(scientific["slots"]):
        identity = slot["selected"]["canonical_exercise_id"]
        exercise = SessionExercise(
            session_id=session.id,
            template_exercise_id=None,
            exercise_code_snapshot=f"sci-v3-{index + 1}",
            exercise_name_snapshot=identity,
            position=index,
        )
        db.add(exercise)
        db.flush()
        set_ids = []
        for set_index in range(1, slot["prescription"]["dose"]["work_sets"] + 1):
            logged = SetLog(
                session_exercise_id=exercise.id,
                kind="work",
                set_index=set_index,
                completed=False,
                reps=None,
                weight_kg=None,
            )
            db.add(logged)
            db.flush()
            set_ids.append(logged.id)
        mapping.append(
            {
                "slot_id": slot["slot_id"],
                "intent_id": slot["intent_id"],
                "canonical_exercise_id": identity,
                "se_id": exercise.id,
                "set_ids": set_ids,
            }
        )
    payload = {
        "scientific_session": scientific,
        "allocation_ref": plan["allocation_ref"],
        "mapping": mapping,
        "authority": {key: result[key] for key in AUTHORITY_FIELDS},
        "authority_generation": validated_evaluation.authority_generation,
    }
    binding = FirstPlanExecutionBinding(
        session_id=session.id,
        owner_id=owner_id,
        evaluation_id=validated_evaluation.id,
        execution_profile_version=EXECUTION_VERSION,
        scientific_session_id=first_scientific_session_id,
        immutable_payload_json=canonical(payload),
        binding_digest=digest(payload),
    )
    db.add(binding)
    db.flush()
    return session


def owned_binding(db, owner_id, session_id):
    import json

    from sqlalchemy import select

    from app.models.first_plan_runtime import FirstPlanEvaluation

    session = db.scalar(
        select(WorkoutSession)
        .where(WorkoutSession.id == session_id, WorkoutSession.user_id == owner_id)
        .execution_options(populate_existing=True)
    )
    if session is None:
        raise RuntimeFailure("not_found", 404)
    if not is_scientific_session(session):
        raise RuntimeFailure("execution_profile_mismatch", 406)
    binding = db.get(FirstPlanExecutionBinding, session_id)
    if binding is None or binding.owner_id != owner_id:
        raise RuntimeFailure("execution_binding_unavailable", 503)
    try:
        payload = json.loads(binding.immutable_payload_json)
        if digest(payload) != binding.binding_digest:
            raise ValueError("binding changed")
        actual = list(
            db.scalars(
                select(SessionExercise)
                .where(SessionExercise.session_id == session_id)
                .order_by(SessionExercise.position)
            )
        )
        if len(payload["mapping"]) != len(actual):
            raise ValueError("canonical exercise graph mismatch")
        for se, mapping, slot in zip(
            actual, payload["mapping"], payload["scientific_session"]["slots"], strict=True
        ):
            if (
                se.id != mapping["se_id"]
                or mapping["slot_id"] != slot["slot_id"]
                or mapping["canonical_exercise_id"] != slot["selected"]["canonical_exercise_id"]
                or se.template_exercise_id is not None
            ):
                raise ValueError("canonical mapping changed")
            rows = list(
                db.scalars(
                    select(SetLog)
                    .where(SetLog.session_exercise_id == se.id)
                    .order_by(SetLog.set_index)
                )
            )
            if [row.id for row in rows] != mapping["set_ids"] or any(
                row.kind != "work" for row in rows
            ):
                raise ValueError("canonical set graph changed")
        evaluation = db.get(FirstPlanEvaluation, binding.evaluation_id)
        if evaluation is None or evaluation.owner_id != owner_id:
            raise ValueError("missing owned evaluation")
        captured = json.loads(evaluation.result_json)
        if (
            captured["candidate_plan"] is None
            or canonical(payload["scientific_session"])
            != canonical(captured["candidate_plan"]["sessions"][0])
            or payload["allocation_ref"] != captured["candidate_plan"]["allocation_ref"]
            or canonical(payload["authority"])
            != canonical({key: captured[key] for key in AUTHORITY_FIELDS})
            or payload["authority_generation"] != evaluation.authority_generation
            or any(
                len(mapping["set_ids"]) != slot["prescription"]["dose"]["work_sets"]
                or mapping["intent_id"] != slot["intent_id"]
                for mapping, slot in zip(
                    payload["mapping"], payload["scientific_session"]["slots"], strict=True
                )
            )
        ):
            raise ValueError("binding differs from its captured admitted evaluation")
    except (ValueError, TypeError, KeyError):
        raise RuntimeFailure("execution_binding_unavailable", 503) from None
    return session, binding, payload, evaluation


def assess_applicability(db, owner_id, session_id, *, auth=None):
    import json

    from app.config import get_settings
    from app.models.first_plan_runtime import FirstPlanRuntimeAuthority
    from app.services.plan_v3.authority import PROFILE, lock_authority
    from app.services.plan_v3.packaging import execute_science
    from app.services.plan_v3.snapshots import check_revision
    from app.services.plan_v3.transactions import guard_owner

    session, binding, payload, evaluation = owned_binding(db, owner_id, session_id)
    try:
        operational, authorities, _ = lock_authority(db)
        guard_owner(db, owner_id, **(auth or {}))
        from app.services.plan_v3.calibration_profiles import assert_snapshot_runtime

        assert_snapshot_runtime(db, evaluation.snapshot_id, operational, authorities)
        check_revision(db, owner_id, evaluation.source_revision)
        if operational.generation != evaluation.authority_generation:
            raise RuntimeFailure("authority_generation_changed")
        if not get_settings().plan_v3_guidance_enabled:
            raise RuntimeFailure("guidance_not_served")
        result = execute_science(
            "evaluate",
            json.loads(evaluation.request_json),
            expected_digest=operational.packaging_digest,
        )
        if result["start_permission"] != "ELIGIBLE":
            raise RuntimeFailure("scientific_permission_required")
        if session.status != "in_progress":
            raise RuntimeFailure("session_closed")
        return {
            "state": "CURRENT",
            "reason": None,
            "authority_generation": operational.generation,
            "source_revision": evaluation.source_revision,
        }
    except (RuntimeFailure, ValueError) as error:
        if isinstance(error, RuntimeFailure) and error.status == 401:
            raise
        guard_owner(db, owner_id, **(auth or {}))
        operational = db.get(FirstPlanRuntimeAuthority, PROFILE)
        state = (
            "BLOCKED" if operational is not None and operational.state != "ACTIVE" else "UNKNOWN"
        )
        if isinstance(error, RuntimeFailure) and error.code in {
            "source_revision_changed",
            "authority_generation_changed",
            "session_closed",
            "scientific_permission_required",
        }:
            state = "BLOCKED"
        return {
            "state": state,
            "reason": error.code if isinstance(error, RuntimeFailure) else "authority_unavailable",
            "authority_generation": operational.generation if operational is not None else None,
            "source_revision": evaluation.source_revision,
        }


def first_plan_execution_read_model(db, owner_id, session_id, *, auth=None):
    import json

    from sqlalchemy import select

    from app.models.first_plan_runtime import FirstPlanSetObservation

    session, binding, payload, evaluation = owned_binding(db, owner_id, session_id)
    applicability = assess_applicability(db, owner_id, session_id, auth=auth)
    exercises = []
    cursor = None
    for position, (mapping, slot) in enumerate(
        zip(payload["mapping"], payload["scientific_session"]["slots"], strict=True)
    ):
        rows = []
        for index, set_id in enumerate(mapping["set_ids"]):
            logged = db.get(SetLog, set_id)
            observation = db.scalar(
                select(FirstPlanSetObservation)
                .where(
                    FirstPlanSetObservation.owner_id == owner_id,
                    FirstPlanSetObservation.set_id == set_id,
                )
                .order_by(FirstPlanSetObservation.applied_revision.desc())
                .limit(1)
            )
            fact = json.loads(observation.observation_json) if observation is not None else None
            if cursor is None and not logged.completed:
                cursor = {"exercise_index": position, "set_index": index, "set_id": set_id}
            rows.append(
                {
                    "set_id": set_id,
                    "set_index": logged.set_index,
                    "kind": logged.kind,
                    "completed": logged.completed,
                    "reps": logged.reps,
                    "completed_at": logged.completed_at.replace(tzinfo=UTC).isoformat()
                    if logged.completed_at
                    else None,
                    "observation": fact,
                    "revision": observation.applied_revision if observation else 0,
                    "transition_after_set": {
                        "kind": "REST_THEN_SET",
                        "duration_seconds": slot["prescription"]["dose"]["rest_seconds"],
                    }
                    if index < len(mapping["set_ids"]) - 1
                    else None,
                }
            )
        exercises.append(
            {
                "se_id": mapping["se_id"],
                "slot_id": slot["slot_id"],
                "canonical_exercise_id": mapping["canonical_exercise_id"],
                "intent_id": slot["intent_id"],
                "prescription": slot["prescription"],
                "sets": rows,
                "transition_after_exercise": {
                    "kind": "SETUP_NEXT_EXERCISE",
                    "duration_seconds": None,
                }
                if position < len(payload["mapping"]) - 1
                else {"kind": "BILAN", "duration_seconds": None},
            }
        )
    actions = ["RECORD_FACT", "FINISH", "PAUSE", "ABANDON"]
    if applicability["state"] == "CURRENT":
        actions.append("NEXT_WORK_SET")
    return {
        "contract_version": EXECUTION_VERSION,
        "server_now": datetime.now(UTC).isoformat(),
        "session_id": session.id,
        "status": session.status,
        "started_at": session.started_at.replace(tzinfo=UTC).isoformat(),
        "ended_at": session.ended_at.replace(tzinfo=UTC).isoformat() if session.ended_at else None,
        "excluded_from_stats": session.excluded_from_stats,
        "cursor": cursor,
        "exercises": exercises,
        "applicability": applicability,
        "observation_only": applicability["state"] != "CURRENT",
        "allowed_actions": actions,
        "evaluation_ref": evaluation.id,
        "binding_digest": binding.binding_digest,
        "scientific_session_id": binding.scientific_session_id,
        "derived_metrics": "NON_EVALUABLE",
    }


def require_legacy_http(session):
    from fastapi import HTTPException

    if is_scientific_session(session):
        raise HTTPException(
            409,
            detail={"error": "execution_profile_required", "execution_contract": EXECUTION_VERSION},
        )


def export_first_plan_session(db, session):
    """Private owned export of typed evidence. No current permission is asserted."""
    import json

    from sqlalchemy import select

    from app.models.first_plan_runtime import FirstPlanSetObservation

    _, binding, payload, evaluation = owned_binding(db, session.user_id, session.id)
    observations = list(
        db.scalars(
            select(FirstPlanSetObservation)
            .where(
                FirstPlanSetObservation.session_id == session.id,
                FirstPlanSetObservation.owner_id == session.user_id,
            )
            .order_by(FirstPlanSetObservation.set_id, FirstPlanSetObservation.applied_revision)
        )
    )
    return {
        "contract_version": EXECUTION_VERSION,
        "binding": payload,
        "binding_digest": binding.binding_digest,
        "evaluation_ref": evaluation.id,
        "snapshot_ref": evaluation.snapshot_id,
        "operations": [
            {
                "set_id": row.set_id,
                "se_id": row.session_exercise_id,
                "op_id": row.op_id,
                "applied_revision": row.applied_revision,
                "observation": json.loads(row.observation_json),
                "receipt": json.loads(row.receipt_json),
            }
            for row in observations
        ],
        "current_permission": "NOT_ASSERTED_BY_EXPORT",
        "derived_metrics": "NON_EVALUABLE",
    }
