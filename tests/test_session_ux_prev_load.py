"""Sb_SESSION_UX_01.3 (F2) — Previous-load readability on the active set row.

A discreet reminder of last session's load (« dernière : X kg · Y reps ») is
rendered ON the ACTIVE set row, at the exact point of input. Additive: the
existing « Référence précédente » console block is preserved. Silence when
there is no prior data (never an invented performance). Decorative
(aria-hidden); text source of truth unchanged.

Template/CSS only — no route/service/data/model change.
"""
from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from pathlib import Path

from tests.helpers import get_test_user_id

ROOT = Path(__file__).resolve().parent.parent
FOCUS_CSS = ROOT / "app" / "static" / "css" / "session_focus.css"
EXERCISE_CARD = ROOT / "app" / "templates" / "_partials" / "exercise_card.html"
JS_DIR = ROOT / "app" / "static" / "js"


def _new_session(client, slug: str = "push-a") -> int:
    r = client.post("/sessions", data={"template_slug": slug}, follow_redirects=False)
    m = re.match(r"/sessions/(\d+)", r.headers["location"])
    return int(m.group(1))


def _insert_prior(client, *, exercise_code, exercise_name, work_sets, slug="push-a"):
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    with SessionLocal() as db:
        prior = WorkoutSession(
            template_id=None,
            template_slug_snapshot=slug,
            template_name_snapshot="Push A",
            user_id=get_test_user_id(),
            started_at=datetime.now(UTC) - timedelta(days=5),
            status="completed",
        )
        se = SessionExercise(
            template_exercise_id=None,
            exercise_code_snapshot=exercise_code,
            exercise_name_snapshot=exercise_name,
            position=1,
        )
        for i, ws in enumerate(work_sets, start=1):
            se.set_logs.append(
                SetLog(
                    kind="work",
                    set_index=i,
                    weight_kg=ws.get("weight_kg"),
                    reps=ws.get("reps"),
                    completed=ws.get("completed", True),
                )
            )
        prior.session_exercises.append(se)
        db.add(prior)
        db.commit()
        return prior.id


# ───────── in-row previous-load hint ─────────


def test_prev_load_hint_on_active_row_when_data(client):
    """With a prior session, the active set row shows the discreet reminder."""
    _insert_prior(
        client,
        exercise_code="E1",
        exercise_name="Incline Smith Press",
        work_sets=[{"weight_kg": 60.0, "reps": 10}, {"weight_kg": 62.5, "reps": 8}],
    )
    sid = _new_session(client, "push-a")
    body = client.get(f"/sessions/{sid}").text
    assert "session-focus__console-row-prev" in body
    # discreet reminder text carries the previous load
    assert "dernière :" in body


def test_prev_load_hint_absent_when_no_data(client):
    """No prior session ⇒ silence (never an invented performance)."""
    sid = _new_session(client, "push-a")
    body = client.get(f"/sessions/{sid}").text
    assert "session-focus__console-row-prev" not in body


def test_prev_load_hint_is_aria_hidden(client):
    """The in-row reminder is decorative (the console-ref block carries the
    accessible reference); it must be aria-hidden."""
    _insert_prior(
        client,
        exercise_code="E1",
        exercise_name="Incline Smith Press",
        work_sets=[{"weight_kg": 60.0, "reps": 10}],
    )
    sid = _new_session(client, "push-a")
    body = client.get(f"/sessions/{sid}").text
    m = re.search(r'<span class="session-focus__console-row-prev"[^>]*>', body)
    assert m is not None
    assert "aria-hidden" in m.group(0)


def test_console_ref_block_preserved(client):
    """Non-regression: the « Référence précédente » console block still lives
    (single accessible home of the previous-load info)."""
    _insert_prior(
        client,
        exercise_code="E1",
        exercise_name="Incline Smith Press",
        work_sets=[{"weight_kg": 60.0, "reps": 10}],
    )
    sid = _new_session(client, "push-a")
    body = client.get(f"/sessions/{sid}").text
    assert "session-focus__console-ref--prev" in body
    assert "Référence précédente" in body


def test_prev_load_hint_only_on_active_row(client):
    """The reminder appears at most once (only the active set)."""
    _insert_prior(
        client,
        exercise_code="E1",
        exercise_name="Incline Smith Press",
        work_sets=[{"weight_kg": 60.0, "reps": 10}],
    )
    sid = _new_session(client, "push-a")
    body = client.get(f"/sessions/{sid}").text
    assert body.count("session-focus__console-row-prev") == 1


# ───────── non-goals: no JS, no new colour ─────────


def test_no_new_hex_colour_in_prev_hint_css():
    css = FOCUS_CSS.read_text(encoding="utf-8")
    m = re.search(
        r"\.session-focus__console-row-prev\s*\{([^}]*)\}", css
    )
    assert m is not None
    rule = m.group(1)
    assert "#" not in rule  # reuses --fg-dim; no raw hex
    assert "var(--fg-dim)" in rule


def test_no_js_added_for_prev_load():
    src = EXERCISE_CARD.read_text(encoding="utf-8")
    # the in-row hint is pure SSR
    assert "session-focus__console-row-prev" in src
    if JS_DIR.exists():
        assert not any("prev_load" in p.name.lower() for p in JS_DIR.glob("*.js"))
