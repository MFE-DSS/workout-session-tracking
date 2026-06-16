"""Sb_29.2 — Active Exercise Navigation tests.

Verifies the reinforcement of visual navigation between exercises:
* exactly one exercise card is `<details open>` by default (the active one)
* non-active cards are collapsed by default
* jump bar contains one item per session_exercise
* jump bar item for the active exercise carries aria-current="step"
* every jump bar item has an href="#exercise-{id}" anchor
* the 6 UI state classes exist in app.css for both cards and jump items
* prev/next nav buttons are still wired (`name="nav"` values present)
* no new JS file is introduced
* no React / SPA / bundle marker leaks into the rendered HTML

The tests rely on rendered HTML + CSS file content only — no real-time
behaviour assumptions. Independent of timezone/weekday.
"""
from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_CSS = ROOT / "app" / "static" / "css" / "app.css"
FOCUS_CSS = ROOT / "app" / "static" / "css" / "session_focus.css"


# ───────── seed helpers ─────────


def _seed_multi_exercise_session(db, user_id, n_exercises=3):
    """Seed an in-progress session with N exercises, each with 1 work set."""
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    s = WorkoutSession(
        user_id=user_id,
        template_slug_snapshot="multi-exo",
        template_name_snapshot="Multi-exo test",
        started_at=datetime.now(UTC),
        status="in_progress",
    )
    for i in range(n_exercises):
        se = SessionExercise(
            exercise_code_snapshot=f"E{i + 1}",
            exercise_name_snapshot=f"Exercise {i + 1}",
            position=i + 1,
        )
        se.set_logs.append(
            SetLog(
                kind="work",
                set_index=1,
                weight_kg=80.0,
                reps=8,
                completed=False,
            )
        )
        s.session_exercises.append(se)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def _render(client, session_id) -> str:
    r = client.get(f"/sessions/{session_id}", follow_redirects=False)
    assert r.status_code == 200, r.text[:400]
    return r.text


# ───────── one active card open ─────────


def test_only_active_card_is_open_by_default(client):
    """Exactly one <details ... open> with class exercise-card on a
    freshly created session: the active (first) one."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_multi_exercise_session(db, user.id, n_exercises=3)
        session_id = session.id

    body = _render(client, session_id)

    # Match every <details> tag for an exercise card and check the `open`
    # presence per match.
    # Match only the TOP-level exercise card <details>, not the nested
    # ones (`exercise-card__note`, `machine-panel`, etc.). The top-level
    # card always carries both `card` and `exercise-card` classes.
    pattern = re.compile(
        r'<details\b([^>]*\bclass="[^"]*\bcard\s+exercise-card\b[^"]*"[^>]*)>',
        re.IGNORECASE,
    )
    cards = pattern.findall(body)
    assert len(cards) == 3, f"expected 3 cards rendered, got {len(cards)}"
    open_count = sum(1 for attrs in cards if re.search(r"\bopen\b", attrs))
    assert open_count == 1, (
        f"expected exactly 1 open card by default, got {open_count}"
    )


def test_active_card_carries_active_modifier(client):
    """The opened card must carry session-focus__card--active class."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_multi_exercise_session(db, user.id, n_exercises=3)
        session_id = session.id

    body = _render(client, session_id)
    # The active card must combine the modifier and the open attribute.
    pattern = re.compile(
        r'<details\b[^>]*\bclass="[^"]*session-focus__card--active[^"]*"'
        r"[^>]*\bopen\b",
        re.IGNORECASE,
    )
    assert pattern.search(body) is not None, (
        "no <details open> with session-focus__card--active class found"
    )


def test_non_active_cards_have_no_open_attribute(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_multi_exercise_session(db, user.id, n_exercises=4)
        session_id = session.id

    body = _render(client, session_id)
    # For each non-active card we expect no `open` attribute on the
    # <details>. We check that any card whose class does NOT contain
    # --active is not opened by default.
    # Match only the TOP-level exercise card <details>, not the nested
    # ones (`exercise-card__note`, `machine-panel`, etc.). The top-level
    # card always carries both `card` and `exercise-card` classes.
    pattern = re.compile(
        r'<details\b([^>]*\bclass="[^"]*\bcard\s+exercise-card\b[^"]*"[^>]*)>',
        re.IGNORECASE,
    )
    cards = pattern.findall(body)
    non_active_open = 0
    for attrs in cards:
        is_active = "session-focus__card--active" in attrs
        is_open = re.search(r"\bopen\b", attrs) is not None
        if (not is_active) and is_open:
            non_active_open += 1
    assert non_active_open == 0, (
        f"{non_active_open} non-active card(s) were opened by default"
    )


# ───────── jump bar contract ─────────


def test_jump_bar_contains_one_item_per_exercise(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_multi_exercise_session(db, user.id, n_exercises=5)
        session_id = session.id
        ex_ids = [se.id for se in session.session_exercises]

    body = _render(client, session_id)
    for ex_id in ex_ids:
        assert f'href="#exercise-{ex_id}"' in body, (
            f"jump bar missing href to exercise {ex_id}"
        )


def test_jump_bar_active_item_carries_aria_current_step(client):
    """The active exercise's jump bar item must have aria-current="step"."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_multi_exercise_session(db, user.id, n_exercises=3)
        session_id = session.id

    body = _render(client, session_id)
    # Look for an <a ...> item with aria-current="step" inside the jump nav.
    # The simplest check: at least one element with both ex-jump__item--active
    # and aria-current="step".
    pattern = re.compile(
        r'<a\b[^>]*\bex-jump__item--active\b[^>]*\baria-current="step"',
        re.IGNORECASE,
    )
    assert pattern.search(body) is not None, (
        "active jump bar item missing aria-current=\"step\""
    )


def test_jump_bar_anchors_match_exercise_anchors(client):
    """Each jump bar href must point at a real id=exercise-{id} anchor."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_multi_exercise_session(db, user.id, n_exercises=3)
        session_id = session.id

    body = _render(client, session_id)
    hrefs = set(re.findall(r'href="#exercise-(\d+)"', body))
    anchors = set(re.findall(r'id="exercise-(\d+)"', body))
    assert hrefs == anchors, (
        f"jump bar hrefs ({hrefs}) and anchors ({anchors}) diverge"
    )


# ───────── prev / next buttons preserved ─────────


def test_prev_next_buttons_preserved(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_multi_exercise_session(db, user.id, n_exercises=3)
        session_id = session.id

    body = _render(client, session_id)
    # next button on the active card
    assert 'name="nav"' in body
    assert 'value="next"' in body
    # prev/next form action preserved
    assert f"/sessions/{session_id}/exercises/" in body


# ───────── CSS state classes (Sb_29.2 reinforcement) ─────────


def _css() -> str:
    return APP_CSS.read_text(encoding="utf-8") + "\n" + FOCUS_CSS.read_text(encoding="utf-8")


def test_css_active_card_has_box_shadow():
    """Sb_29.2 strengthens the active card highlight with a box-shadow
    + thicker border, on top of the Sb_29.1 minimal border."""
    css = _css()
    # The active card rule must include box-shadow now.
    pattern = re.compile(
        r"\.session-focus__card--active\s*\{[^}]*box-shadow",
        re.DOTALL,
    )
    assert pattern.search(css), (
        "session-focus__card--active should carry box-shadow (Sb_29.2)"
    )


def test_css_done_state_has_non_color_cue():
    """Done card should expose a non-color cue (border-left + checkmark)."""
    css = _css()
    # checkmark via ::after on the code
    assert ".session-focus__card--done" in css
    # presence of a non-color cue: border-left on the summary or checkmark
    pattern = re.compile(
        r"\.session-focus__card--done\s*>\s*summary\s*\{[^}]*border-left",
        re.DOTALL,
    )
    assert pattern.search(css), (
        "done state should add a non-color border-left cue"
    )


def test_css_skipped_state_has_non_color_cue():
    css = _css()
    pattern = re.compile(
        r"\.session-focus__card--skipped\s*>\s*summary\s*\{[^}]*border-left",
        re.DOTALL,
    )
    assert pattern.search(css), (
        "skipped state should add a non-color border-left cue"
    )


def test_css_substituted_state_has_non_color_cue():
    css = _css()
    pattern = re.compile(
        r"\.session-focus__card--substituted\s*>\s*summary\s*\{[^}]*border-left",
        re.DOTALL,
    )
    assert pattern.search(css), (
        "substituted state should add a non-color border-left cue"
    )


def test_css_jump_bar_skipped_state_present():
    css = _css()
    assert ".ex-jump__item--skipped" in css


def test_css_jump_bar_substituted_state_present():
    css = _css()
    assert ".ex-jump__item--substituted" in css


def test_css_jump_bar_active_has_non_color_cue():
    """Active jump bar item should add a non-color cue via ::before."""
    css = _css()
    # We look for a rule targeting active item with ::before content set.
    pattern = re.compile(
        r"\.ex-jump__item--active::before\s*\{[^}]*content",
        re.DOTALL,
    )
    assert pattern.search(css), (
        "active jump bar item should add a ::before cue"
    )


# ───────── tap targets preserved ─────────


def test_tap_target_min_size_still_44px():
    """Sb_29.2 must not regress the WCAG 2.5.5 contract from Sb_29.1."""
    css = _css()
    assert "min-height: 44px" in css or "min-height:44px" in css
    assert "min-width: 44px" in css or "min-width:44px" in css


# ───────── no new JS / no React introduced ─────────


def test_no_new_js_file_introduced():
    """Only authorized JS files exist (preview.js + session_focus.js Sb_29.4)."""
    js_dir = ROOT / "app" / "static" / "js"
    existing = {p.name for p in js_dir.glob("*.js")}
    assert existing <= {"preview.js", "session_focus.js"}, (
        f"unexpected JS files in app/static/js/: {existing}"
    )


def test_no_react_or_bundle_introduced(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_multi_exercise_session(db, user.id, n_exercises=2)
        session_id = session.id

    body = _render(client, session_id).lower()
    for forbidden in (
        "react",
        "react-dom",
        "vue.js",
        "angular",
        "/main.bundle.js",
        "esm.sh",
        "unpkg.com",
        "cdnjs.cloudflare.com/ajax/libs/react",
    ):
        assert forbidden not in body, (
            f"forbidden token in rendered HTML: {forbidden}"
        )


def test_no_routing_change_for_sessions(client):
    """The session detail route signature must be unchanged."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_multi_exercise_session(db, user.id, n_exercises=2)
        session_id = session.id

    r = client.get(f"/sessions/{session_id}", follow_redirects=False)
    assert r.status_code == 200
    # POST signature on the same path still answers (we just GET to confirm
    # the route is wired ; POSTs are exercised by other test files).


# ───────── owner isolation preserved ─────────


def test_owner_isolation_unaffected(client):
    """Sb_26.7 hard contract must hold."""
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.auth import hash_password

    with SessionLocal() as db:
        owner = db.query(User).first()
        session = _seed_multi_exercise_session(db, owner.id, n_exercises=2)
        session_id = session.id
        other = User(
            username="nav_other",
            password_hash=hash_password("nav_other_str_pw"),  # noqa: S106
        )
        db.add(other)
        db.commit()

    client.cookies.clear()
    r = client.post(
        "/login",
        data={"username": "nav_other", "password": "nav_other_str_pw"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    r = client.get(f"/sessions/{session_id}", follow_redirects=False)
    assert r.status_code == 404
