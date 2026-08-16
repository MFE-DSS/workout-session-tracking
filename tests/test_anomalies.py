"""Tests for app.services.anomalies (Sb_08 — 5 rules)."""
from __future__ import annotations

from datetime import UTC, datetime

from tests.helpers import get_test_user_id


def _mk_session_for_anomalies(
    *,
    exercises: list[dict],
    concentration: str | None = "high",
    global_state: str | None = "good",
):
    """Build a minimal session with full control over per-exercise data.

    Each exercise dict may provide:
        code, name, success_score,
        work_sets: [{weight_kg, reps, completed}, ...]
        warmup_sets: [{weight_kg, reps, completed}, ...]
        rep_targets: [{min_reps, max_reps}, ...]  (sets template_exercise inline)
    """
    from app.database import SessionLocal
    from app.models.catalog import RepTarget, TemplateExercise, WorkoutTemplate
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    with SessionLocal() as db:
        tpl = WorkoutTemplate(
            slug=f"anom-{int(datetime.now(UTC).timestamp()*1000)}",
            name="Anom T",
            kind="strength",
        )
        db.add(tpl)
        db.flush()

        s = WorkoutSession(
            user_id=get_test_user_id(),
            template_id=tpl.id,
            template_slug_snapshot=tpl.slug,
            template_name_snapshot=tpl.name,
            started_at=datetime(2026, 4, 18, 18, 0, tzinfo=UTC),
            ended_at=datetime(2026, 4, 18, 19, 0, tzinfo=UTC),
            status="completed",
            concentration=concentration,
            global_state=global_state,
        )

        for pos, ex in enumerate(exercises, start=1):
            te = TemplateExercise(
                template_id=tpl.id,
                position=pos,
                code=ex.get("code", f"E{pos}"),
                name=ex.get("name", f"Ex{pos}"),
                set_scheme=ex.get("set_scheme", "3x8"),
            )
            for i, rt in enumerate(ex.get("rep_targets", []), start=1):
                te.rep_targets.append(
                    RepTarget(set_index=i, min_reps=rt["min_reps"], max_reps=rt["max_reps"])
                )
            db.add(te)
            db.flush()

            se = SessionExercise(
                template_exercise_id=te.id,
                exercise_code_snapshot=ex.get("code", f"E{pos}"),
                exercise_name_snapshot=ex.get("name", f"Ex{pos}"),
                position=pos,
                success_score=ex.get("success_score"),
            )
            for i, sl in enumerate(ex.get("warmup_sets", []), start=1):
                se.set_logs.append(SetLog(
                    kind="warmup", set_index=i,
                    weight_kg=sl.get("weight_kg"), reps=sl.get("reps"),
                    completed=sl.get("completed", False),
                ))
            for i, sl in enumerate(ex.get("work_sets", []), start=1):
                se.set_logs.append(SetLog(
                    kind="work", set_index=i,
                    weight_kg=sl.get("weight_kg"), reps=sl.get("reps"),
                    completed=sl.get("completed", False),
                ))
            s.session_exercises.append(se)

        db.add(s)
        db.commit()
        return s.id


def _load(sid):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    db = SessionLocal()
    return db, db.get(WorkoutSession, sid)


# ---- Rule A — completed set without data ------------------------------

def test_rule_a_triggers_on_completed_empty_set(client):
    from app.services.anomalies import compute_anomalies
    sid = _mk_session_for_anomalies(exercises=[{
        "code": "E1",
        "work_sets": [
            {"weight_kg": 50, "reps": 10, "completed": True},
            {"weight_kg": None, "reps": None, "completed": True},  # anomaly
            {"weight_kg": 50, "reps": 8, "completed": False},
        ],
    }])
    db, s = _load(sid)
    try:
        anomalies = compute_anomalies(s)
        codes = [a.rule_code for a in anomalies]
        assert "A" in codes
        a = next(x for x in anomalies if x.rule_code == "A")
        assert a.exercise_code == "E1"
        assert a.severity == "info"
    finally:
        db.close()


def test_rule_a_silent_when_empty_but_not_completed(client):
    from app.services.anomalies import compute_anomalies
    sid = _mk_session_for_anomalies(exercises=[{
        "code": "E1",
        "work_sets": [
            {"weight_kg": None, "reps": None, "completed": False},
        ],
    }])
    db, s = _load(sid)
    try:
        assert not any(a.rule_code == "A" for a in compute_anomalies(s))
    finally:
        db.close()


# ---- Rule B — weight and reps both grow -------------------------------

def test_rule_b_triggers_when_both_grow(client):
    from app.services.anomalies import compute_anomalies
    sid = _mk_session_for_anomalies(exercises=[{
        "code": "E2",
        "work_sets": [
            {"weight_kg": 40, "reps": 8, "completed": True},
            {"weight_kg": 45, "reps": 9, "completed": True},
            {"weight_kg": 50, "reps": 10, "completed": True},
        ],
    }])
    db, s = _load(sid)
    try:
        assert any(a.rule_code == "B" for a in compute_anomalies(s))
    finally:
        db.close()


def test_rule_b_silent_when_classic_pattern(client):
    from app.services.anomalies import compute_anomalies
    # Classic surcharge: weight up, reps down
    sid = _mk_session_for_anomalies(exercises=[{
        "code": "E2",
        "work_sets": [
            {"weight_kg": 40, "reps": 10, "completed": True},
            {"weight_kg": 45, "reps": 8, "completed": True},
            {"weight_kg": 50, "reps": 6, "completed": True},
        ],
    }])
    db, s = _load(sid)
    try:
        assert not any(a.rule_code == "B" for a in compute_anomalies(s))
    finally:
        db.close()


# ---- Rule C — extreme weight delta vs prior ---------------------------

def test_rule_c_triggers_above_30pct(client):
    from app.services.anomalies import compute_anomalies
    sid = _mk_session_for_anomalies(exercises=[{
        "code": "E3",
        "work_sets": [{"weight_kg": 80, "reps": 10, "completed": True}],
    }])
    db, s = _load(sid)
    try:
        anomalies = compute_anomalies(s, prior_weight_by_code={"E3": 50})
        assert any(a.rule_code == "C" for a in anomalies)
    finally:
        db.close()


def test_rule_c_silent_below_30pct(client):
    from app.services.anomalies import compute_anomalies
    sid = _mk_session_for_anomalies(exercises=[{
        "code": "E3",
        "work_sets": [{"weight_kg": 55, "reps": 10, "completed": True}],
    }])
    db, s = _load(sid)
    try:
        anomalies = compute_anomalies(s, prior_weight_by_code={"E3": 50})
        assert not any(a.rule_code == "C" for a in anomalies)
    finally:
        db.close()


def test_rule_c_skipped_without_prior(client):
    from app.services.anomalies import compute_anomalies
    sid = _mk_session_for_anomalies(exercises=[{
        "code": "E3",
        "work_sets": [{"weight_kg": 80, "reps": 10, "completed": True}],
    }])
    db, s = _load(sid)
    try:
        assert not any(a.rule_code == "C" for a in compute_anomalies(s))
    finally:
        db.close()


# ---- Rule D — only warmup done ----------------------------------------

def test_rule_d_triggers_when_only_warmup_completed(client):
    from app.services.anomalies import compute_anomalies
    sid = _mk_session_for_anomalies(exercises=[{
        "code": "E4",
        "warmup_sets": [{"weight_kg": 20, "reps": 15, "completed": True}],
        "work_sets": [
            {"weight_kg": 40, "reps": 10, "completed": False},
            {"weight_kg": 40, "reps": 10, "completed": False},
        ],
    }])
    db, s = _load(sid)
    try:
        assert any(a.rule_code == "D" for a in compute_anomalies(s))
    finally:
        db.close()


def test_rule_d_silent_when_work_done(client):
    from app.services.anomalies import compute_anomalies
    sid = _mk_session_for_anomalies(exercises=[{
        "code": "E4",
        "warmup_sets": [{"weight_kg": 20, "reps": 15, "completed": True}],
        "work_sets": [{"weight_kg": 40, "reps": 10, "completed": True}],
    }])
    db, s = _load(sid)
    try:
        assert not any(a.rule_code == "D" for a in compute_anomalies(s))
    finally:
        db.close()


# ---- Rule E — score vs reps -------------------------------------------

def test_rule_e_triggers_when_score_high_but_reps_low(client):
    from app.services.anomalies import compute_anomalies
    sid = _mk_session_for_anomalies(exercises=[{
        "code": "E5",
        "success_score": 100,
        "rep_targets": [{"min_reps": 8, "max_reps": 12}],
        "work_sets": [
            {"weight_kg": 40, "reps": 5, "completed": True},
            {"weight_kg": 40, "reps": 6, "completed": True},
        ],
    }])
    db, s = _load(sid)
    try:
        assert any(a.rule_code == "E" for a in compute_anomalies(s))
    finally:
        db.close()


def test_rule_e_silent_when_score_matches_reps(client):
    from app.services.anomalies import compute_anomalies
    sid = _mk_session_for_anomalies(exercises=[{
        "code": "E5",
        "success_score": 100,
        "rep_targets": [{"min_reps": 8, "max_reps": 12}],
        "work_sets": [
            {"weight_kg": 40, "reps": 10, "completed": True},
        ],
    }])
    db, s = _load(sid)
    try:
        assert not any(a.rule_code == "E" for a in compute_anomalies(s))
    finally:
        db.close()


# ---- Aggregate --------------------------------------------------------

def test_compute_anomalies_returns_empty_on_clean_session(client):
    from app.services.anomalies import compute_anomalies
    sid = _mk_session_for_anomalies(exercises=[{
        "code": "E1",
        "rep_targets": [{"min_reps": 8, "max_reps": 12}],
        "success_score": 80,
        "work_sets": [
            {"weight_kg": 50, "reps": 10, "completed": True},
            {"weight_kg": 50, "reps": 9, "completed": True},
            {"weight_kg": 50, "reps": 8, "completed": True},
        ],
    }])
    db, s = _load(sid)
    try:
        assert compute_anomalies(s) == []
    finally:
        db.close()
