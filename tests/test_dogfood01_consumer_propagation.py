"""Sb_DOGFOOD_01.2 — consumer propagation verification.

Verification-only sprint. Sb_DOGFOOD_01.1 made `last_time_by_exercise_code`
substitution-aware at the SOURCE. This proves the consumers that read
`last_time` inherit the guarantee end-to-end (rendered HTML) + unit-checks
the pure formatters:

- delta            : no inter-exercise delta when no comparable history
- hints (Sx_08)    : no drop/+10% hint from another exercise
- chip / peek      : no previous load from another exercise
- console ref-prev : falls back to the existing empty state « Non disponible »
- « Dernière fois » : never a contaminated load on non-active cards

S1 (prescribed→prescribed) and S4 (substituted→same substitution) still show
the reference. Rule: silence rather than a false previous load.

No application code changed by this sprint (consumers already handle a
missing `last_time` — this locks that behaviour).
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

# ───────── unit: pure formatters are silent on a missing prior ─────────


def test_delta_is_none_when_no_prior():
    from app.services.delta import compute_delta

    # current values present, prior absent → no delta (inter-exercise avoided)
    assert compute_delta(80.0, 12, 3, None, None, None) is None


def test_hints_empty_when_no_prior():
    from app.services.hints import compute_hints

    class _SE:
        exercise_code_snapshot = "E1"
        substituted_name = None
        set_logs: list = []

    assert compute_hints(_SE(), None) == []


# ───────── end-to-end: rendered HTML honours the substitution identity ─────────


def _seed(db, uid, *, slug, code, sub, weight, reps, days_ago, now, status="completed"):
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    s = WorkoutSession(
        user_id=uid, template_slug_snapshot=slug, template_name_snapshot="T",
        started_at=now - timedelta(days=days_ago), status=status,
    )
    se = SessionExercise(
        exercise_code_snapshot=code, exercise_name_snapshot="Squat prescrit",
        substituted_name=sub, position=1,
    )
    if weight is not None:
        se.set_logs.append(
            SetLog(kind="work", set_index=1, weight_kg=weight, reps=reps, completed=True)
        )
    else:
        se.set_logs.append(SetLog(kind="work", set_index=1, completed=False))
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


def _render_current(client, sid):
    r = client.get(f"/sessions/{sid}", follow_redirects=False)
    assert r.status_code == 200, r.text[:300]
    return r.text


# S2 prescribed history → substituted current: no previous-load surfaced.
def test_s2_substituted_current_shows_no_contaminated_load(client):
    db, uid, now = _ctx(client)
    _seed(db, uid, slug="push-a", code="E1", sub=None, weight=60.0, reps=10, days_ago=5, now=now)
    current = _seed(db, uid, slug="push-a", code="E1", sub="Leg Press", weight=None,
                    reps=None, days_ago=0, now=now, status="in_progress")
    html = _render_current(client, current.id)
    db.close()
    # console reference falls back to the empty state, not the prescribed 60 kg
    assert "60 kg · 10 reps" not in html
    assert "Non disponible" in html


# S3 recent substitution + older prescribed → prescribed current: only the
# older prescribed load surfaces, never the substitution.
def test_s3_prescribed_current_uses_older_prescribed_not_substitution(client):
    db, uid, now = _ctx(client)
    _seed(db, uid, slug="pull-b", code="E1", sub=None, weight=55.0, reps=8, days_ago=10, now=now)
    _seed(db, uid, slug="pull-b", code="E1", sub="Leg Press", weight=80.0, reps=12, days_ago=3, now=now)
    current = _seed(db, uid, slug="pull-b", code="E1", sub=None, weight=None, reps=None,
                    days_ago=0, now=now, status="in_progress")
    html = _render_current(client, current.id)
    db.close()
    assert "55 kg · 8 reps" in html       # older prescribed
    assert "80 kg · 12 reps" not in html  # never the substitution


# S5 other substitution only → silence.
def test_s5_other_substitution_only_is_silent(client):
    db, uid, now = _ctx(client)
    _seed(db, uid, slug="push-a", code="E1", sub="Hack Squat", weight=90.0, reps=8, days_ago=3, now=now)
    current = _seed(db, uid, slug="push-a", code="E1", sub="Leg Press", weight=None, reps=None,
                    days_ago=0, now=now, status="in_progress")
    html = _render_current(client, current.id)
    db.close()
    assert "90 kg · 8 reps" not in html
    assert "Non disponible" in html


# S1 prescribed → prescribed still shows the reference.
def test_s1_prescribed_reference_still_visible(client):
    db, uid, now = _ctx(client)
    _seed(db, uid, slug="push-a", code="E1", sub=None, weight=60.0, reps=10, days_ago=5, now=now)
    current = _seed(db, uid, slug="push-a", code="E1", sub=None, weight=None, reps=None,
                    days_ago=0, now=now, status="in_progress")
    html = _render_current(client, current.id)
    db.close()
    assert "60 kg · 10 reps" in html


# S4 substituted → same substitution still shows the reference.
def test_s4_same_substitution_reference_still_visible(client):
    db, uid, now = _ctx(client)
    _seed(db, uid, slug="push-a", code="E1", sub="Leg Press", weight=80.0, reps=12, days_ago=5, now=now)
    current = _seed(db, uid, slug="push-a", code="E1", sub="Leg Press", weight=None, reps=None,
                    days_ago=0, now=now, status="in_progress")
    html = _render_current(client, current.id)
    db.close()
    assert "80 kg · 12 reps" in html


# No new "non comparable" microcopy nor forbidden "repère" wording introduced.
def test_no_new_microcopy_no_repere_in_template():
    from pathlib import Path

    card = Path(__file__).resolve().parent.parent / "app" / "templates" / "_partials" / "exercise_card.html"
    src = card.read_text(encoding="utf-8")
    assert "Repère" not in src and "repère" not in src
    # the empty-state microcopy stays the existing one
    assert "Non disponible" in src
