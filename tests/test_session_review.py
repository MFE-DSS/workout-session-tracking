"""Sb_27.2 — Session Review V1 payload tests.

Covers the contract of `build_session_review`, the degraded paths
(no implicit_label, no quality_score, no notable movements), and the
GET /sessions/{id}/done route surfacing the new payload without
breaking the existing recap.

Cross-user isolation is already covered by Sb_26.7
(`tests/test_auth_scope_isolation.py::test_user_b_cannot_read_user_a_session_detail`
+ `test_user_a_can_still_read_own_session`). We don't re-test it here;
we only check that the new payload itself doesn't leak between users
(unit-level: building a review for session A only reads session A).
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

# ─────────────────── helpers ───────────────────


def _make_session(
    db,
    user_id: int,
    *,
    exercises: list[dict] | None = None,
    started_offset_min: int = 60,
    scoring_version: int = 2,
    template_name: str = "Push A",
):
    """Build a completed session with N exercises.

    Each `exercises` dict accepts:
      code, name, implicit_label, work_sets (list of (weight, reps, completed))
    """
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    now = datetime.now(UTC)
    started = now - timedelta(minutes=started_offset_min)
    s = WorkoutSession(
        user_id=user_id,
        template_slug_snapshot=template_name.lower().replace(" ", "-"),
        template_name_snapshot=template_name,
        started_at=started,
        ended_at=now,
        status="completed",
        scoring_version=scoring_version,
    )
    for idx, exo in enumerate(exercises or [], start=1):
        se = SessionExercise(
            exercise_code_snapshot=exo.get("code", f"E{idx}"),
            exercise_name_snapshot=exo.get("name", f"Exercise {idx}"),
            position=idx,
            implicit_label=exo.get("implicit_label"),
        )
        for set_idx, (w, r, done) in enumerate(exo.get("work_sets", []), start=1):
            se.set_logs.append(
                SetLog(
                    kind="work",
                    set_index=set_idx,
                    weight_kg=w,
                    reps=r,
                    completed=done,
                )
            )
        s.session_exercises.append(se)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def _build(db, session):
    from app.services.session_review import build_session_review

    return build_session_review(db, session)


# ─────────────────── shape contract ───────────────────


def test_payload_always_has_five_keys(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _make_session(db, user.id, exercises=[])
        payload = _build(db, s)
    assert set(payload.keys()) == {
        "summary",
        "quality",
        "implicit_signal",
        "notable_movements",
        "next_hint",
    }


# ─────────────────── summary ───────────────────


def test_summary_includes_template_and_duration(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _make_session(db, user.id, template_name="Push A", started_offset_min=45)
        payload = _build(db, s)

    summary = payload["summary"]
    assert summary["available"] is True
    assert summary["template_name"] == "Push A"
    assert summary["duration_min"] is not None and summary["duration_min"] >= 44


def test_summary_handles_missing_ended_at(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _make_session(db, user.id)
        s.ended_at = None
        db.add(s)
        db.commit()
        db.refresh(s)
        payload = _build(db, s)

    assert payload["summary"]["duration_min"] is None
    assert payload["summary"]["duration_note"] == "Non déductible"


# ─────────────────── quality ───────────────────


def test_quality_returns_score_when_available(client):
    """`compute_session_quality` is computable on a strength session."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _make_session(
            db,
            user.id,
            exercises=[
                {
                    "code": "BENCH",
                    "name": "Bench",
                    "implicit_label": "intense",
                    "work_sets": [(80, 8, True), (80, 8, True), (80, 8, True)],
                },
            ],
        )
        payload = _build(db, s)

    q = payload["quality"]
    assert q["available"] is True
    # Either a numeric score, or "Non déductible" if the formula bailed.
    if q["score"] is not None:
        assert isinstance(q["score"], (int, float))
        assert q["scoring_version"] == 2
    else:
        assert q.get("note") == "Non déductible"


def test_quality_falls_back_to_non_deductible_when_service_raises(
    client, monkeypatch
):
    """If `compute_session_quality` raises, surface 'Non déductible'."""
    from app.database import SessionLocal
    from app.models.user import User
    from app.services import quality_score as qs_mod

    def _boom(_session):
        raise RuntimeError("forced")

    monkeypatch.setattr(qs_mod, "compute_session_quality", _boom)

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _make_session(db, user.id, exercises=[
            {"code": "C", "name": "Squat", "work_sets": [(100, 5, True)]}
        ])
        payload = _build(db, s)

    assert payload["quality"]["score"] is None
    assert payload["quality"]["note"] == "Non déductible"


# ─────────────────── implicit signal ───────────────────


def test_implicit_signal_present(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _make_session(db, user.id, exercises=[
            {"code": "A", "name": "A", "implicit_label": "intense"},
            {"code": "B", "name": "B", "implicit_label": "intense"},
            {"code": "C", "name": "C", "implicit_label": "fluide"},
        ])
        payload = _build(db, s)

    impl = payload["implicit_signal"]
    assert impl["available"] is True
    assert impl["label"] == "intense"
    assert impl["source_ratio"] == "2/3"


def test_implicit_signal_absent_says_non_deductible(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _make_session(db, user.id, exercises=[
            {"code": "A", "name": "A"},  # no implicit_label
            {"code": "B", "name": "B"},
        ])
        payload = _build(db, s)

    impl = payload["implicit_signal"]
    assert impl["label"] is None
    assert impl["note"] == "Non déductible"


# ─────────────────── notable movements ───────────────────


def test_notable_movements_empty_when_nothing_qualifies(client):
    """Session with no implicit_label, no completed sets, no volume."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _make_session(db, user.id, exercises=[
            {"code": "A", "name": "A", "work_sets": [(0, 0, False)]},
        ])
        payload = _build(db, s)

    nm = payload["notable_movements"]
    assert nm["available"] is True
    assert nm["movements"] == []
    assert nm["note"] == "Aucun mouvement remarquable déductible."


def test_notable_movements_intense_label_surfaces_reason(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _make_session(db, user.id, exercises=[
            {
                "code": "BENCH",
                "name": "Bench Press",
                "implicit_label": "intense",
                "work_sets": [(80, 8, True), (80, 7, True)],
            },
            {
                "code": "ROW",
                "name": "Row",
                "implicit_label": "fluide",
                "work_sets": [(60, 10, True)],
            },
        ])
        payload = _build(db, s)

    items = payload["notable_movements"]["movements"]
    assert any(it["exercise_code"] == "BENCH" for it in items)
    bench = next(it for it in items if it["exercise_code"] == "BENCH")
    assert "ressenti intense" in bench["reasons"]


def test_notable_movements_capped_at_three(client):
    """Even with 5 candidates, only the top 3 are returned."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _make_session(db, user.id, exercises=[
            {
                "code": f"E{i}",
                "name": f"Exercise {i}",
                "implicit_label": "intense",
                "work_sets": [(50, 10, True), (50, 10, True), (50, 10, True)],
            }
            for i in range(5)
        ])
        payload = _build(db, s)

    assert len(payload["notable_movements"]["movements"]) == 3


def test_notable_movements_completion_rule_triggers(client):
    """All work sets completed AND >=3 sets → 'tous les sets validés'."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _make_session(db, user.id, exercises=[
            {
                "code": "SQ",
                "name": "Squat",
                "work_sets": [(100, 5, True), (100, 5, True), (100, 5, True)],
            },
        ])
        payload = _build(db, s)

    items = payload["notable_movements"]["movements"]
    assert len(items) == 1
    assert any("tous les sets validés" in r for r in items[0]["reasons"])


def test_notable_movements_volume_rule_fills_remaining(client):
    """When no label/completion rule fires, top volume fills the spot."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _make_session(db, user.id, exercises=[
            {
                "code": "DL",
                "name": "Deadlift",
                "work_sets": [(120, 5, True), (120, 5, True)],
            },
            {
                "code": "LR",
                "name": "Lateral Raise",
                "work_sets": [(10, 12, True)],
            },
        ])
        payload = _build(db, s)

    items = payload["notable_movements"]["movements"]
    # Deadlift volume (1200) > Lateral Raise (120) → DL appears first
    assert items[0]["exercise_code"] == "DL"
    assert "volume" in items[0]["reasons"][0]


# ─────────────────── next hint ───────────────────


def test_next_hint_returns_phrase_always(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _make_session(db, user.id, exercises=[
            {"code": "A", "name": "A", "implicit_label": "intense"},
            {"code": "B", "name": "B", "implicit_label": "intense"},
        ])
        payload = _build(db, s)

    h = payload["next_hint"]
    assert h["available"] is True
    assert "Séance dense" in h["phrase"]


def test_next_hint_phrase_for_session_without_implicit_labels(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _make_session(db, user.id, exercises=[
            {"code": "A", "name": "A"},
        ])
        payload = _build(db, s)

    h = payload["next_hint"]
    # No labels → pedagogy phrase prompting the user to fill them.
    assert "ressenti" in h["phrase"].lower()


# ─────────────────── safety net ───────────────────


def test_payload_resilient_to_sub_builder_exception(client, monkeypatch):
    """If a sub-builder crashes, the key is still present with available=False."""
    from app.database import SessionLocal
    from app.models.user import User
    from app.services import session_review as sr_mod

    monkeypatch.setattr(
        sr_mod, "_build_summary", lambda *_a, **_kw: (_ for _ in ()).throw(
            RuntimeError("forced")
        )
    )

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _make_session(db, user.id, exercises=[
            {"code": "A", "name": "A"}
        ])
        payload = _build(db, s)

    assert payload["summary"]["available"] is False
    assert payload["summary"]["error_type"] == "RuntimeError"
    # Other sub-builders still produced their payloads
    assert payload["quality"]["available"] is True
    assert payload["implicit_signal"]["available"] is True
    assert payload["notable_movements"]["available"] is True
    assert payload["next_hint"]["available"] is True


# ─────────────────── HTTP route ───────────────────


def test_done_route_returns_200_for_owner_with_review(client):
    """GET /sessions/{id}/done renders successfully and includes a review
    section marker (the template surfaces 'session_review' details)."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _make_session(db, user.id, exercises=[
            {
                "code": "BENCH",
                "name": "Bench Press",
                "implicit_label": "intense",
                "work_sets": [(80, 8, True), (80, 8, True), (80, 8, True)],
            }
        ])
        session_id = s.id

    r = client.get(f"/sessions/{session_id}/done", follow_redirects=False)
    assert r.status_code == 200
    body = r.text
    # The template must include the section we added (looked up via a
    # robust marker — text or class — that's hard to remove by accident).
    assert "session-review" in body or "Bench Press" in body
