"""Sb_27.3 — Weekly training loop payload tests.

Covers the shape contract of `build_weekly_loop`, the degraded paths
(zero session, low data, anomaly unavailable, hint unavailable), the
user-scope (another user's sessions never leak), and the GET /progress
route (200 + budget-friendly).

The builder never invents — these tests confirm explicit fallbacks
appear instead of crashes (Sx_27 §16).
"""
from __future__ import annotations

import pathlib
import re
from datetime import UTC, datetime, timedelta

_REQUIRED_KEYS = {
    "available",
    "week_start",
    "week_end",
    "sessions_count",
    "previous_week_sessions_count",
    "delta_sessions_count",
    "volume_signal",
    "dominant_templates",
    "top_anomaly",
    "top_anomaly_note",
    "hint",
    "hint_note",
    "data_quality",
    "data_quality_note",
}


def _seed_completed_session(
    db,
    user_id: int,
    *,
    template_name: str = "Push A",
    days_ago: float = 1,
    started_at: datetime | None = None,
    implicit_label: str | None = None,
    excluded: bool = False,
):
    """Helper: create one completed session for `user_id`.

    `started_at` takes precedence over `days_ago` when both supplied —
    needed for tests that target an exact ISO-week position regardless
    of the runner's current weekday.
    """
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    if started_at is not None:
        started = started_at
    else:
        started = datetime.now(UTC) - timedelta(days=days_ago)
    s = WorkoutSession(
        user_id=user_id,
        template_slug_snapshot=template_name.lower().replace(" ", "-"),
        template_name_snapshot=template_name,
        started_at=started,
        ended_at=started + timedelta(minutes=45),
        status="completed",
        scoring_version=2,
        excluded_from_stats=excluded,
    )
    se = SessionExercise(
        exercise_code_snapshot="BENCH",
        exercise_name_snapshot="Bench Press",
        position=1,
        implicit_label=implicit_label,
    )
    se.set_logs.append(
        SetLog(kind="work", set_index=1, weight_kg=80.0, reps=8, completed=True)
    )
    s.session_exercises.append(se)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def _build(db, user):
    from app.services.weekly_loop import build_weekly_loop

    return build_weekly_loop(db, user)


# ─────────────────── shape contract ───────────────────


def test_payload_has_required_keys(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        payload = _build(db, user)
    assert _REQUIRED_KEYS.issubset(payload.keys())


def test_payload_zero_sessions_shows_explicit_fallback(client):
    """Fresh user → low-data fallback strings everywhere."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        payload = _build(db, user)

    assert payload["sessions_count"] == 0
    assert payload["data_quality"] == "low"
    assert "Pas encore assez de données" in payload["volume_signal"]
    assert payload["dominant_templates"] == []
    assert payload["top_anomaly"] is None
    assert payload["top_anomaly_note"] == "Aucune anomalie détectée."
    assert payload["hint"] is None
    assert payload["hint_note"]


# ─────────────────── counts + delta ───────────────────


def test_one_session_this_week(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        _seed_completed_session(db, user.id, days_ago=0)
        payload = _build(db, user)

    assert payload["sessions_count"] == 1
    assert "1 séance" in payload["volume_signal"]
    assert payload["hint"] is not None
    # 1 session → "Bon démarrage" hint
    assert "démarrage" in payload["hint"].lower()


def test_three_sessions_this_week(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        for _ in range(3):
            _seed_completed_session(db, user.id, days_ago=0)
        payload = _build(db, user)

    assert payload["sessions_count"] == 3
    assert "3 séances" in payload["volume_signal"]
    assert payload["data_quality"] == "ok"


def test_four_sessions_triggers_volume_soutenu_hint(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        for _ in range(4):
            _seed_completed_session(db, user.id, days_ago=0)
        payload = _build(db, user)

    assert payload["sessions_count"] == 4
    assert "Volume soutenu" in payload["volume_signal"]
    assert payload["hint"] is not None
    assert "récupération" in payload["hint"].lower()


def test_previous_week_count_present(client):
    """Sessions from the previous ISO week are counted separately.

    Anchored on an explicit ISO Monday so the test is independent of the
    runner's current weekday.
    """
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.weekly_loop import build_weekly_loop

    # Anchor: a fixed Wednesday in 2026-W24 (Wed 2026-06-10 12:00 UTC).
    ref = datetime(2026, 6, 10, 12, 0, tzinfo=UTC)
    this_week_monday = ref - timedelta(days=ref.weekday())  # Mon 2026-06-08
    last_week_tuesday = this_week_monday - timedelta(days=6)  # Tue 2026-06-02
    last_week_wednesday = this_week_monday - timedelta(days=5)  # Wed 2026-06-03

    with SessionLocal() as db:
        user = db.query(User).first()
        # 1 session this week (Tuesday of this week)
        _seed_completed_session(
            db, user.id, started_at=this_week_monday + timedelta(days=1)
        )
        # 2 sessions last week
        _seed_completed_session(db, user.id, started_at=last_week_tuesday)
        _seed_completed_session(db, user.id, started_at=last_week_wednesday)

    with SessionLocal() as db:
        user = db.query(User).first()
        payload = build_weekly_loop(db, user, now=ref)

    assert payload["sessions_count"] == 1
    assert payload["previous_week_sessions_count"] == 2
    assert payload["delta_sessions_count"] == -1


def test_delta_positive_triggers_acceleration_hint(client):
    """Δ ≥ +2 vs prev week → acceleration phrase."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        # 3 this week, 0 last week → delta = +3
        _seed_completed_session(db, user.id, days_ago=0)
        _seed_completed_session(db, user.id, days_ago=0)
        _seed_completed_session(db, user.id, days_ago=0)
        payload = _build(db, user)

    assert payload["delta_sessions_count"] == 3
    # 3 sessions doesn't hit the "≥4" rule, so we fall into the delta-based
    # branch which says "accélères vs la semaine passée".
    assert "accélère" in payload["hint"]


# ─────────────────── filters ───────────────────


def test_excluded_from_stats_session_is_ignored(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        # one legit + one excluded — only the legit counts
        _seed_completed_session(db, user.id, days_ago=0)
        _seed_completed_session(db, user.id, days_ago=0, excluded=True)
        payload = _build(db, user)

    assert payload["sessions_count"] == 1


# ─────────────────── user-scope isolation ───────────────────


def test_payload_does_not_leak_other_users_sessions(client):
    """A session belonging to another user must NEVER affect payload."""
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.auth import hash_password

    with SessionLocal() as db:
        other = User(
            username="weekly_other",
            password_hash=hash_password("pwd_str_a"),  # noqa: S106
        )
        db.add(other)
        db.commit()
        db.refresh(other)
        # Seed for OTHER
        _seed_completed_session(db, other.id, days_ago=0)
        _seed_completed_session(db, other.id, days_ago=8)

    with SessionLocal() as db:
        testuser = db.query(User).filter(User.username == "testuser").first()
        payload = _build(db, testuser)

    assert payload["sessions_count"] == 0
    assert payload["previous_week_sessions_count"] == 0
    assert payload["dominant_templates"] == []


# ─────────────────── dominant templates ───────────────────


def test_dominant_templates_top_two(client):
    """Top-2 by count, in descending order."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        for _ in range(2):
            _seed_completed_session(db, user.id, template_name="Push A", days_ago=0)
        _seed_completed_session(db, user.id, template_name="Pull B", days_ago=0)
        _seed_completed_session(db, user.id, template_name="Legs", days_ago=0)
        payload = _build(db, user)

    names = [t["name"] for t in payload["dominant_templates"]]
    assert len(payload["dominant_templates"]) == 2
    assert names[0] == "Push A"
    assert payload["dominant_templates"][0]["count"] == 2


# ─────────────────── anomaly fallback ───────────────────


def test_top_anomaly_fallback_when_service_returns_nothing(client, monkeypatch):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services import anomalies as anomalies_mod

    monkeypatch.setattr(anomalies_mod, "compute_anomalies", lambda _s: [])

    with SessionLocal() as db:
        user = db.query(User).first()
        _seed_completed_session(db, user.id, days_ago=0)
        payload = _build(db, user)

    assert payload["top_anomaly"] is None
    assert payload["top_anomaly_note"] == "Aucune anomalie détectée."


def test_top_anomaly_fallback_when_service_raises(client, monkeypatch):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services import anomalies as anomalies_mod

    def _boom(_session):
        raise RuntimeError("forced")

    monkeypatch.setattr(anomalies_mod, "compute_anomalies", _boom)

    with SessionLocal() as db:
        user = db.query(User).first()
        _seed_completed_session(db, user.id, days_ago=0)
        payload = _build(db, user)

    # Anomaly service raised → still no anomaly surfaced, never crashes
    assert payload["top_anomaly"] is None


# ─────────────────── HTTP route ───────────────────


def test_progress_route_returns_200(client):
    r = client.get("/progress", follow_redirects=False)
    assert r.status_code == 200


def test_progress_route_no_longer_renders_the_weekly_container(client):
    """`TRAIN1-A` / A11 — RÉORIENTÉ VERS LA NOUVELLE VÉRITÉ, PAS AFFAIBLI.

    Ce test assertait que le conteneur `weekly-loop` se rendait sur
    `/progress`. La décision opérateur le retire : il portait deux
    duplications mesurées — « 3 séances cette semaine » et « Semaine
    précédente : 2 (+1) » répétaient la ligne « Séances » et les quatorze
    cellules du rail.

    L'invariant utile n'était pas « ce conteneur existe » mais **« ses faits
    atteignent la surface »**. C'est ce qui est asserté maintenant, et c'est
    plus strict : le conteneur doit être ABSENT, et ses deux faits uniques
    présents ailleurs — l'anomalie dans l'instrument temporel, la dominance
    hebdomadaire dans « Par programme ».
    """
    r = client.get("/progress", follow_redirects=False)
    assert r.status_code == 200
    assert "weekly-loop" not in r.text

    template = (
        pathlib.Path(__file__).resolve().parent.parent
        / "app/templates/progress.html"
    ).read_text(encoding="utf-8")
    template = re.sub(r"\{#.*?#\}", " ", template, flags=re.S)
    assert "top_anomaly" in template
    assert "tk.week_count" in template


def test_the_weekly_producer_is_still_called_by_the_route():
    """La décision porte sur le conteneur, jamais sur la capacité."""
    pages = (
        pathlib.Path(__file__).resolve().parent.parent / "app/routers/pages.py"
    ).read_text(encoding="utf-8")
    assert "build_weekly_loop(db, user)" in pages


def test_progress_route_no_secret_leak(client):
    r = client.get("/progress")
    body = r.text.lower()
    for forbidden in ("sentry_dsn", "discord_webhook_url", "secret_key"):
        assert forbidden not in body
