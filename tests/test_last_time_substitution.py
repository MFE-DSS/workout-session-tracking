"""Sb_DOGFOOD_01.1 — last_time substitution-aware (5 transition scenarios).

`last_time_by_exercise_code` must only surface a previous load that belongs
to the SAME exercise actually performed for the current slot, applying the
same substitution policy as the overload inputs:

  S1 prescribed → prescribed        : prior prescribed load returned
  S2 prescribed → substituted       : absent (no prescribed→substituted mix)
  S3 substituted → prescribed       : the older PRESCRIBED prior returned,
                                      never the recent substitution; absent
                                      if no prescribed prior exists
  S4 substituted(X) → substituted(X): the same-substitution load returned
  S5 substituted(X) → substituted(Y): the older Y prior if any, else absent;
                                      never the recent X substitution

Rule: silence rather than a false previous load from another exercise.
The return contract (dict[str, dict] keyed by exercise_code_snapshot) is
unchanged, so all consumers inherit the guarantee.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.services.stats import last_time_by_exercise_code


def _mk_session(
    db,
    user_id,
    *,
    slug="push-a",
    started_at,
    status="completed",
    code="E1",
    prescribed_name="Squat prescrit",
    substituted_name=None,
    weight=None,
    reps=None,
):
    """Create a session with a single work SessionExercise for slot `code`,
    optionally substituted, with one completed work set."""
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    s = WorkoutSession(
        user_id=user_id,
        template_slug_snapshot=slug,
        template_name_snapshot="Push A",
        started_at=started_at,
        status=status,
    )
    se = SessionExercise(
        exercise_code_snapshot=code,
        exercise_name_snapshot=prescribed_name,
        substituted_name=substituted_name,
        position=1,
    )
    if weight is not None or reps is not None:
        se.set_logs.append(
            SetLog(kind="work", set_index=1, weight_kg=weight, reps=reps, completed=True)
        )
    s.session_exercises.append(se)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def _ctx(client):
    from app.database import SessionLocal
    from app.models.user import User

    db = SessionLocal()
    uid = db.query(User).first().id
    now = datetime(2026, 5, 1, 12, 0, tzinfo=UTC)
    return db, uid, now


def _days(now, n):
    return now - timedelta(days=n)


# ───────── S1 prescribed → prescribed ─────────


def test_s1_prescribed_to_prescribed_returns_prior(client):
    db, uid, now = _ctx(client)
    _mk_session(db, uid, started_at=_days(now, 5), code="E1",
                substituted_name=None, weight=60.0, reps=10)
    current = _mk_session(db, uid, started_at=now, status="in_progress", code="E1",
                          substituted_name=None)
    lt = last_time_by_exercise_code(db, current, now)
    db.close()
    assert "E1" in lt
    assert lt["E1"]["has_data"] is True
    assert "60" in lt["E1"]["weights_str"]


# ───────── S2 prescribed → substituted ─────────


def test_s2_prescribed_history_to_substituted_current_is_absent(client):
    db, uid, now = _ctx(client)
    _mk_session(db, uid, started_at=_days(now, 5), code="E1",
                substituted_name=None, weight=60.0, reps=10)
    current = _mk_session(db, uid, started_at=now, status="in_progress", code="E1",
                          substituted_name="Leg Press")
    lt = last_time_by_exercise_code(db, current, now)
    db.close()
    # no prescribed→substituted mix: no comparable prior for the substitution
    assert "E1" not in lt


# ───────── S3 substituted → prescribed ─────────


def test_s3_recent_substitution_to_prescribed_current_skips_substitution(client):
    """Recent prior was substituted; an older prior was prescribed. Current
    is prescribed → must return the OLDER prescribed, never the substitution."""
    db, uid, now = _ctx(client)
    _mk_session(db, uid, started_at=_days(now, 10), code="E1",
                substituted_name=None, weight=55.0, reps=8)          # older prescribed
    _mk_session(db, uid, started_at=_days(now, 3), code="E1",
                substituted_name="Leg Press", weight=80.0, reps=12)  # recent substituted
    current = _mk_session(db, uid, started_at=now, status="in_progress", code="E1",
                          substituted_name=None)
    lt = last_time_by_exercise_code(db, current, now)
    db.close()
    assert "E1" in lt
    assert "55" in lt["E1"]["weights_str"]     # the prescribed one
    assert "80" not in lt["E1"]["weights_str"]  # never the substitution


def test_s3_only_substitution_history_prescribed_current_is_absent(client):
    """Current prescribed but the only history is substituted → silence."""
    db, uid, now = _ctx(client)
    _mk_session(db, uid, started_at=_days(now, 3), code="E1",
                substituted_name="Leg Press", weight=80.0, reps=12)
    current = _mk_session(db, uid, started_at=now, status="in_progress", code="E1",
                          substituted_name=None)
    lt = last_time_by_exercise_code(db, current, now)
    db.close()
    assert "E1" not in lt


# ───────── S4 substituted(X) → substituted(X) ─────────


def test_s4_same_substitution_returns_prior(client):
    db, uid, now = _ctx(client)
    _mk_session(db, uid, started_at=_days(now, 5), code="E1",
                substituted_name="Leg Press", weight=80.0, reps=12)
    current = _mk_session(db, uid, started_at=now, status="in_progress", code="E1",
                          substituted_name="Leg Press")
    lt = last_time_by_exercise_code(db, current, now)
    db.close()
    assert "E1" in lt
    assert "80" in lt["E1"]["weights_str"]


def test_s4_same_substitution_ignores_whitespace_variance(client):
    """Normalization: ' Leg Press ' matches 'Leg Press'."""
    db, uid, now = _ctx(client)
    _mk_session(db, uid, started_at=_days(now, 5), code="E1",
                substituted_name="Leg Press", weight=80.0, reps=12)
    current = _mk_session(db, uid, started_at=now, status="in_progress", code="E1",
                          substituted_name="  Leg Press  ")
    lt = last_time_by_exercise_code(db, current, now)
    db.close()
    assert "E1" in lt


# ───────── S5 substituted(X) → substituted(Y) ─────────


def test_s5_other_substitution_only_recent_is_absent(client):
    """Recent prior substituted by Hack Squat; current substituted by Leg
    Press; no Leg Press history → silence (never Hack Squat's load)."""
    db, uid, now = _ctx(client)
    _mk_session(db, uid, started_at=_days(now, 3), code="E1",
                substituted_name="Hack Squat", weight=90.0, reps=8)
    current = _mk_session(db, uid, started_at=now, status="in_progress", code="E1",
                          substituted_name="Leg Press")
    lt = last_time_by_exercise_code(db, current, now)
    db.close()
    assert "E1" not in lt


def test_s5_other_substitution_older_matching_is_returned(client):
    """Older prior matches the current substitution (Leg Press); a more
    recent prior is a different substitution (Hack Squat). Must return the
    older matching Leg Press, never Hack Squat."""
    db, uid, now = _ctx(client)
    _mk_session(db, uid, started_at=_days(now, 10), code="E1",
                substituted_name="Leg Press", weight=75.0, reps=10)   # older match
    _mk_session(db, uid, started_at=_days(now, 3), code="E1",
                substituted_name="Hack Squat", weight=90.0, reps=8)   # recent other
    current = _mk_session(db, uid, started_at=now, status="in_progress", code="E1",
                          substituted_name="Leg Press")
    lt = last_time_by_exercise_code(db, current, now)
    db.close()
    assert "E1" in lt
    assert "75" in lt["E1"]["weights_str"]
    assert "90" not in lt["E1"]["weights_str"]


# ───────── contract & isolation ─────────


def test_return_contract_unchanged_keyed_by_code(client):
    db, uid, now = _ctx(client)
    _mk_session(db, uid, started_at=_days(now, 5), code="E1",
                substituted_name=None, weight=60.0, reps=10)
    current = _mk_session(db, uid, started_at=now, status="in_progress", code="E1",
                          substituted_name=None)
    lt = last_time_by_exercise_code(db, current, now)
    db.close()
    assert isinstance(lt, dict)
    assert set(lt.keys()) <= {"E1"}
    assert set(lt["E1"]) >= {"has_data", "weights_str", "reps_str"}
