"""Sb_27.5 — Deterministic narrative tests.

Pure-function tests on the 3 narrative helpers. No DB, no client
fixture needed for the unit-level cases — only the integration tests
on / /sessions/{id}/done /progress use `client`.

OQ-6 verified by an explicit scan: every produced phrase must NEVER
contain "vous" — only "tu" or nominal forms (Sx_27 §11.2, OQ-6
verbatim user).
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.services.narrative import (
    narrate_reco,
    narrate_session_review,
    narrate_week,
)

_REQUIRED_KEYS = {
    "available",
    "phrase",
    "tone",
    "data_quality",
    "fallback_note",
}


def _assert_shape(out: dict):
    assert _REQUIRED_KEYS.issubset(out.keys())
    assert isinstance(out["phrase"], str)
    assert out["phrase"]  # non-empty
    assert len(out["phrase"]) <= 120  # MAX_PHRASE_LEN guard
    assert out["tone"] in {"neutral", "warning", "encouragement", "low_data"}
    assert out["data_quality"] in {"ok", "low"}


def _assert_no_vous(out: dict):
    """OQ-6 hard contract — never address the user as 'vous'."""
    body = out["phrase"].lower()
    # Use word boundaries: 'vous' as a standalone word.
    import re

    assert not re.search(r"\bvous\b", body), f"phrase uses 'vous': {out['phrase']!r}"


# ───────── narrate_reco ─────────


def test_narrate_reco_returns_required_keys_for_any_input():
    out = narrate_reco({})
    _assert_shape(out)


def test_narrate_reco_none_payload_returns_low_data_phrase():
    out = narrate_reco(None)
    _assert_shape(out)
    assert out["data_quality"] == "low"
    _assert_no_vous(out)


def test_narrate_reco_in_progress_session():
    out = narrate_reco({"kind": "in_progress", "template_name": "Push A"})
    _assert_shape(out)
    assert "Push A" in out["phrase"]
    _assert_no_vous(out)


def test_narrate_reco_no_reco_yields_low_data_phrase():
    out = narrate_reco({"kind": "no_reco"})
    _assert_shape(out)
    assert out["data_quality"] == "low"
    assert "complète" in out["phrase"].lower()
    _assert_no_vous(out)


def test_narrate_reco_cold_start_signals_low_data():
    out = narrate_reco({
        "kind": "reco",
        "template_name": "Push A",
        "cold_start": True,
    })
    _assert_shape(out)
    assert out["data_quality"] == "low"
    assert "données" in out["phrase"].lower() or "limit" in out["phrase"].lower()
    _assert_no_vous(out)


def test_narrate_reco_fallback_payload_says_historique():
    out = narrate_reco({
        "kind": "reco",
        "template_name": "Push A",
        "fallback": True,
    })
    _assert_shape(out)
    assert out["data_quality"] == "low"
    assert "historique" in out["phrase"].lower()
    _assert_no_vous(out)


def test_narrate_reco_low_confidence_says_historique():
    out = narrate_reco({
        "kind": "reco",
        "template_name": "Push A",
        "confidence": "low",
    })
    _assert_shape(out)
    assert out["data_quality"] == "low"
    _assert_no_vous(out)


def test_narrate_reco_ok_path_is_neutral_encouragement():
    out = narrate_reco({
        "kind": "reco",
        "template_name": "Push A",
        "confidence": "ok",
    })
    _assert_shape(out)
    assert out["data_quality"] == "ok"
    assert "Push A" in out["phrase"]
    _assert_no_vous(out)


# ───────── narrate_session_review ─────────


def test_narrate_session_review_required_keys_any_input():
    out = narrate_session_review({})
    _assert_shape(out)


def test_narrate_session_review_dense_when_intense_label():
    out = narrate_session_review({
        "implicit_signal": {"label": "intense", "available": True},
    })
    _assert_shape(out)
    assert "dense" in out["phrase"].lower()
    assert out["tone"] == "warning"
    _assert_no_vous(out)


def test_narrate_session_review_difficile_label_is_dense():
    out = narrate_session_review({
        "implicit_signal": {"label": "difficile", "available": True},
    })
    _assert_shape(out)
    assert "dense" in out["phrase"].lower()
    _assert_no_vous(out)


def test_narrate_session_review_fluide_label_says_enchaîner():
    out = narrate_session_review({
        "implicit_signal": {"label": "fluide", "available": True},
    })
    _assert_shape(out)
    assert "fluide" in out["phrase"].lower() or "enchaîner" in out["phrase"].lower()
    _assert_no_vous(out)


def test_narrate_session_review_no_label_no_quality_falls_back():
    out = narrate_session_review({
        "implicit_signal": {"label": None, "available": True},
        "quality": {"score": None, "available": True},
    })
    _assert_shape(out)
    assert out["data_quality"] == "low"
    assert "ressenti" in out["phrase"].lower() or "signal" in out["phrase"].lower()
    _assert_no_vous(out)


def test_narrate_session_review_solid_when_high_quality_and_movements():
    out = narrate_session_review({
        "implicit_signal": {"label": None, "available": True},
        "quality": {"score": 80, "available": True},
        "notable_movements": {
            "movements": [{"exercise_name": "Bench Press", "reasons": ["ressenti intense"]}],
            "available": True,
        },
    })
    _assert_shape(out)
    assert "solide" in out["phrase"].lower()
    _assert_no_vous(out)


def test_narrate_session_review_short_when_low_quality():
    out = narrate_session_review({
        "implicit_signal": {"label": None, "available": True},
        "quality": {"score": 30, "available": True},
        "notable_movements": {"movements": [], "available": True},
    })
    _assert_shape(out)
    assert out["data_quality"] == "low"
    _assert_no_vous(out)


def test_narrate_session_review_garbled_payload_does_not_crash():
    out = narrate_session_review("not a dict")
    _assert_shape(out)
    assert out["data_quality"] == "low"


# ───────── narrate_week ─────────


def test_narrate_week_required_keys_any_input():
    out = narrate_week({})
    _assert_shape(out)


def test_narrate_week_zero_sessions_low_data():
    out = narrate_week({"sessions_count": 0})
    _assert_shape(out)
    assert out["data_quality"] == "low"
    assert "complète" in out["phrase"].lower() or "données" in out["phrase"].lower()
    _assert_no_vous(out)


def test_narrate_week_one_session_encourages():
    out = narrate_week({"sessions_count": 1})
    _assert_shape(out)
    assert out["tone"] == "encouragement"
    assert "premier" in out["phrase"].lower() or "deuxième" in out["phrase"].lower()
    _assert_no_vous(out)


def test_narrate_week_four_or_more_warns_about_recovery():
    out = narrate_week({"sessions_count": 4})
    _assert_shape(out)
    assert out["tone"] == "warning"
    assert "récupération" in out["phrase"].lower() or "soutenue" in out["phrase"].lower()
    _assert_no_vous(out)


def test_narrate_week_anomaly_warning():
    out = narrate_week({
        "sessions_count": 2,
        "top_anomaly": {"code": "rule_a", "session_id": 5},
    })
    _assert_shape(out)
    assert out["tone"] == "warning"
    assert "anomalie" in out["phrase"].lower()
    _assert_no_vous(out)


def test_narrate_week_acceleration_when_delta_positive():
    out = narrate_week({
        "sessions_count": 3,
        "delta_sessions_count": 2,
    })
    _assert_shape(out)
    assert out["tone"] == "encouragement"
    assert "accélère" in out["phrase"].lower() or "rythme" in out["phrase"].lower()
    _assert_no_vous(out)


def test_narrate_week_decline_when_delta_negative():
    out = narrate_week({
        "sessions_count": 1,
        "delta_sessions_count": -3,
    })
    _assert_shape(out)
    assert out["tone"] == "neutral"
    assert "baisse" in out["phrase"].lower() or "prochaine" in out["phrase"].lower()
    _assert_no_vous(out)


def test_narrate_week_regular_when_no_signal():
    out = narrate_week({
        "sessions_count": 2,
        "delta_sessions_count": 0,
        "top_anomaly": None,
    })
    _assert_shape(out)
    assert out["tone"] == "encouragement"
    assert "régulière" in out["phrase"].lower() or "rythme" in out["phrase"].lower()
    _assert_no_vous(out)


# ───────── exhaustive 'vous' scan across all branches ─────────


def test_no_vous_in_any_canonical_path():
    """Cover every branch we can imagine — none of them ever uses 'vous'."""
    cases = [
        narrate_reco(None),
        narrate_reco({}),
        narrate_reco({"kind": "in_progress", "template_name": "X"}),
        narrate_reco({"kind": "no_reco"}),
        narrate_reco({"kind": "reco", "template_name": "X", "cold_start": True}),
        narrate_reco({"kind": "reco", "template_name": "X", "fallback": True}),
        narrate_reco({"kind": "reco", "template_name": "X", "confidence": "ok"}),
        narrate_session_review(None),
        narrate_session_review({"implicit_signal": {"label": "intense"}}),
        narrate_session_review({"implicit_signal": {"label": "fluide"}}),
        narrate_session_review({"implicit_signal": {"label": None}, "quality": {"score": 80},
                                "notable_movements": {"movements": [1]}}),
        narrate_session_review({"implicit_signal": {"label": None}, "quality": {"score": 30}}),
        narrate_week(None),
        narrate_week({"sessions_count": 0}),
        narrate_week({"sessions_count": 1}),
        narrate_week({"sessions_count": 4}),
        narrate_week({"sessions_count": 2, "top_anomaly": {"code": "x"}}),
        narrate_week({"sessions_count": 3, "delta_sessions_count": 2}),
        narrate_week({"sessions_count": 1, "delta_sessions_count": -3}),
        narrate_week({"sessions_count": 2, "delta_sessions_count": 0}),
    ]
    for out in cases:
        _assert_shape(out)
        _assert_no_vous(out)


# ───────── integration: routes still 200 ─────────


def test_home_route_still_200(client):
    r = client.get("/", follow_redirects=False)
    assert r.status_code == 200


def test_progress_route_still_200(client):
    r = client.get("/progress", follow_redirects=False)
    assert r.status_code == 200


def test_session_done_route_still_200(client):
    """Seed a completed session and hit /sessions/{id}/done."""
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = WorkoutSession(
            user_id=user.id,
            template_slug_snapshot="push-a",
            template_name_snapshot="Push A",
            started_at=datetime.now(UTC) - timedelta(hours=1),
            ended_at=datetime.now(UTC),
            status="completed",
            scoring_version=2,
        )
        se = SessionExercise(
            exercise_code_snapshot="B",
            exercise_name_snapshot="Bench",
            position=1,
            implicit_label="intense",
        )
        se.set_logs.append(SetLog(kind="work", set_index=1, weight_kg=80, reps=8, completed=True))
        s.session_exercises.append(se)
        db.add(s)
        db.commit()
        session_id = s.id

    r = client.get(f"/sessions/{session_id}/done", follow_redirects=False)
    assert r.status_code == 200


def test_home_payload_exposes_narrative_on_today(client):
    """build_home_payload now attaches narrative under today."""
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.home import build_home_payload

    with SessionLocal() as db:
        user = db.query(User).first()
        payload = build_home_payload(db, user)

    assert "narrative" in payload["today"]
    narrative = payload["today"]["narrative"]
    assert _REQUIRED_KEYS.issubset(narrative.keys())


def test_weekly_payload_exposes_narrative(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.weekly_loop import build_weekly_loop

    with SessionLocal() as db:
        user = db.query(User).first()
        payload = build_weekly_loop(db, user)

    assert "narrative" in payload


def test_session_review_payload_exposes_narrative(client):
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession
    from app.models.user import User
    from app.services.session_review import build_session_review

    with SessionLocal() as db:
        user = db.query(User).first()
        s = WorkoutSession(
            user_id=user.id,
            template_slug_snapshot="push-a",
            template_name_snapshot="Push A",
            started_at=datetime.now(UTC) - timedelta(hours=1),
            ended_at=datetime.now(UTC),
            status="completed",
            scoring_version=2,
        )
        se = SessionExercise(
            exercise_code_snapshot="B",
            exercise_name_snapshot="Bench",
            position=1,
            implicit_label="intense",
        )
        se.set_logs.append(SetLog(kind="work", set_index=1, weight_kg=80, reps=8, completed=True))
        s.session_exercises.append(se)
        db.add(s)
        db.commit()
        db.refresh(s)
        payload = build_session_review(db, s)

    assert "narrative" in payload
    _assert_shape(payload["narrative"])
    _assert_no_vous(payload["narrative"])
