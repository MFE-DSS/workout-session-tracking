"""Dogfood déterministe de bout en bout (`AUREN_EFFECTIVE_VOLUME_COMPLETION_01`).

Chaîne complète pour une configuration réaliste, à quatre cadences :

préférences → budget → politique de contribution → plan → allocation de
capacité → matérialisation → validation → aperçu qualité.

**Rien n'est publié.** Le brouillon reste un brouillon ; publier demeure un
geste explicite de l'utilisateur, par le service existant.
"""
from __future__ import annotations

import statistics

import pytest

from app.services.weekly_capacity_allocator import coverage_ratio
from app.services.weekly_plan_materialization import (
    MaterializationStatus,
    assess_materialization,
)

CADENCES = (2, 3, 4, 5)


def _report(plan) -> dict:
    zones = plan.zone_coverage
    ratios = [
        coverage_ratio(z.effective_units, z.planning_low_sets) for z in zones]
    return {
        "physical": plan.planned_sets_total,
        "effective": sum(z.effective_sets for z in zones),
        "identities": len({p.exercise_name for p in plan.prescriptions}),
        "occurrences": len(plan.prescriptions),
        "sessions": len(plan.sessions),
        "exercises_per_session": [len(s.slots) for s in plan.sessions],
        "sets_per_session": [
            sum(x.planned_sets for x in s.slots) for s in plan.sessions],
        "zones_with_volume": sum(1 for z in zones if z.effective_units > 0),
        "at_planning_low": sum(1 for z in zones if z.reaches_planning_low),
        "at_baseline": sum(1 for z in zones if z.reaches_baseline),
        "worst": round(min(ratios), 2),
        "median": round(statistics.median(ratios), 2),
        "incidental": sum(
            1 for z in zones if z.overshoot_kind.startswith("incidental")),
        "preventable": sum(
            1 for z in zones if z.overshoot_kind == "preventable"),
        "constraints": list(plan.unmet_constraints),
    }


@pytest.mark.parametrize("cadence", CADENCES)
def test_the_whole_chain_holds_at_every_cadence(cadence, client):
    """Préférences persistées → programme validé, pour chaque cadence."""
    from app.database import SessionLocal
    from app.services.training_preferences import save_training_preferences
    from app.services.user_program_drafts import get_draft, validate_draft
    from app.services.user_program_quality_preview import (
        compute_quality_preview,
    )
    from app.services.weekly_plan_materialization import materialize_weekly_plan
    from app.services.weekly_planner import build_weekly_plan_for_user
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    with SessionLocal() as db:
        save_training_preferences(
            db, uid, sessions_per_week=cadence, focus_priorities=["arms"])

    with SessionLocal() as db:
        plan = build_weekly_plan_for_user(db, uid)
        report = _report(plan)
        readiness = assess_materialization(plan)

        # — Portes de sortie, vérifiées et non supposées —
        assert report["preventable"] == 0, "dépassement préventable"
        assert readiness.status is not MaterializationStatus.BLOCKED

        # Une priorité déclarée doit être MATÉRIELLEMENT représentée : des
        # compteurs remplis par du crédit indirect ne suffisent pas.
        for zone_code in ("biceps", "triceps"):
            exercises = [
                slot.exercise_name for session in plan.sessions
                for slot in session.slots if slot.zone_code == zone_code
            ]
            assert exercises, (
                f"priorité « Bras » déclarée mais {zone_code} n'a aucun "
                f"exercice à cadence {cadence}"
            )

        # Forme de séance plausible au regard du précédent catalogue.
        for count in report["exercises_per_session"]:
            assert 1 <= count <= 8
        for sets in report["sets_per_session"]:
            assert sets <= 24

        program, _ = materialize_weekly_plan(
            db, uid, plan,
            title=f"Dogfood cadence {cadence}",
            slug_base=f"dogfood-cadence-{cadence}")
        program_id = program.id
        assert program.status == "draft", "rien n'est publié"

    with SessionLocal() as db:
        preview = compute_quality_preview(get_draft(db, uid, program_id))
        assert preview.result.global_score is not None

    with SessionLocal() as db:
        validated = validate_draft(db, uid, program_id)
        assert validated.status == "validated"

    with SessionLocal() as db:
        from app.models.user_program import UserProgram

        statuses = {
            p.status for p in db.query(UserProgram).filter(
                UserProgram.user_id == uid).all()
        }
        assert statuses <= {"draft", "validated"}, "un programme a été publié"


def test_the_materialized_sets_are_the_physical_ones(client):
    """La matérialisation prescrit ce qui s'exécute, jamais l'effectif."""
    from app.database import SessionLocal
    from app.services.training_preferences import save_training_preferences
    from app.services.weekly_plan_materialization import materialize_weekly_plan
    from app.services.weekly_planner import build_weekly_plan_for_user
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    with SessionLocal() as db:
        save_training_preferences(db, uid, sessions_per_week=4)

    with SessionLocal() as db:
        plan = build_weekly_plan_for_user(db, uid)
        physical = plan.planned_sets_total
        effective = sum(z.effective_sets for z in plan.zone_coverage)
        assert effective != physical, "le cas ne prouverait rien s'ils coïncidaient"

        program, _ = materialize_weekly_plan(
            db, uid, plan, title="Dogfood physique", slug_base="dogfood-phys")
        stored = sum(
            len(e.rep_targets)
            for s in program.sessions for e in s.exercises
        )
        assert stored == physical


def test_a_repeated_exercise_identity_survives_materialization(client):
    """Une même identité dans plusieurs séances ne doit pas être fusionnée."""
    from app.database import SessionLocal
    from app.services.training_preferences import save_training_preferences
    from app.services.weekly_plan_materialization import materialize_weekly_plan
    from app.services.weekly_planner import build_weekly_plan_for_user
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    with SessionLocal() as db:
        save_training_preferences(db, uid, sessions_per_week=4)

    with SessionLocal() as db:
        plan = build_weekly_plan_for_user(db, uid)
        occurrences = len(plan.prescriptions)
        identities = len({p.exercise_name for p in plan.prescriptions})
        assert occurrences > identities, "aucune répétition à éprouver"

        program, _ = materialize_weekly_plan(
            db, uid, plan, title="Dogfood répétition", slug_base="dogfood-rep")
        stored = sum(len(s.exercises) for s in program.sessions)
        assert stored == occurrences, "des occurrences ont été perdues"
