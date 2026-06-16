"""Sb_29.3 — Sticky CTA on Active Exercise Card tests.

Verifies:
* The CTA wrapper carries the Sx_29 hook classes (`session-focus__cta`,
  `session-focus__sticky-cta`)
* The primary submit button carries `session-focus__cta-primary` and
  the existing `session-focus__tap-target` (Sb_29.1)
* CSS contains a sticky rule **scoped** to `.session-focus__card--active`
  (so non-active cards don't get a useless sticky CTA)
* CSS handles iOS safe-area via `env(safe-area-inset-bottom)`
* The CSS uses `position: sticky` and `bottom: 0`
* The POST form action (`update_exercise_card`) is preserved verbatim
* The button `name="nav"` / `value="next"` (and `value="prev"`) are preserved
* Tap target minimum 44×44px not regressed (Sb_29.1 contract)
* No new JS file introduced — `session_focus.js` reserved for Sb_29.4
* No React / SPA / bundle marker leaks into the rendered HTML
* GET /sessions/{id} still 200
* Owner isolation still 404 for non-owner (Sb_26.7 contract)
"""
from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_CSS = ROOT / "app" / "static" / "css" / "app.css"
FOCUS_CSS = ROOT / "app" / "static" / "css" / "session_focus.css"
PARTIAL = ROOT / "app" / "templates" / "_partials" / "exercise_card.html"


# ───────── seed helpers ─────────


def _seed_in_progress(db, user_id, n_exercises=2):
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    s = WorkoutSession(
        user_id=user_id,
        template_slug_snapshot="sticky-cta",
        template_name_snapshot="Sticky CTA test",
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
            SetLog(kind="work", set_index=1, weight_kg=80.0, reps=8, completed=False)
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


def _css() -> str:
    return APP_CSS.read_text(encoding="utf-8") + "\n" + FOCUS_CSS.read_text(encoding="utf-8")


# ───────── CTA hook classes on the rendered HTML ─────────


def test_cta_wrapper_carries_focus_hooks(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_in_progress(db, user.id)
        session_id = session.id

    body = _render(client, session_id)
    assert "session-focus__cta" in body
    assert "session-focus__sticky-cta" in body


def test_primary_button_carries_focus_cta_primary(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_in_progress(db, user.id)
        session_id = session.id

    body = _render(client, session_id)
    # The Sb_29.3 primary CTA marker class
    assert "session-focus__cta-primary" in body
    # Sb_29.1 tap-target class still present on the same button
    pattern = re.compile(
        r'<button\b[^>]*\bclass="[^"]*session-focus__cta-primary[^"]*"',
        re.IGNORECASE,
    )
    m = pattern.search(body)
    assert m is not None, "no <button> found with session-focus__cta-primary"
    assert "session-focus__tap-target" in m.group(0), (
        "primary CTA button should also keep session-focus__tap-target"
    )


def test_prev_and_next_button_attributes_preserved(client):
    """The POST form name=nav value=prev / value=next contract is intact."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_in_progress(db, user.id, n_exercises=2)
        session_id = session.id

    body = _render(client, session_id)
    # the active card is the first exercise; it has a `next` button.
    # the second exercise has a `prev` button on its own form.
    assert 'name="nav"' in body
    assert 'value="next"' in body
    # second exercise carries the prev button
    assert 'value="prev"' in body


def test_form_action_preserved(client):
    """update_exercise_card endpoint is reached unchanged."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_in_progress(db, user.id)
        session_id = session.id

    body = _render(client, session_id)
    assert f"/sessions/{session_id}/exercises/" in body


# ───────── CSS contract ─────────


def test_css_contains_sticky_cta_block():
    css = _css()
    # The Sx_29.3 CTA rule must include position:sticky with bottom:0
    # scoped to the active card.
    pattern = re.compile(
        r"\.session-focus__card--active\s+\.session-focus__sticky-cta\s*\{"
        r"[^}]*position:\s*sticky[^}]*bottom:\s*0",
        re.DOTALL,
    )
    assert pattern.search(css), (
        "sticky CTA rule scoped to active card not found"
    )


def test_css_sticky_cta_has_safe_area_support():
    css = _css()
    # env(safe-area-inset-bottom) must appear in the active sticky rule
    pattern = re.compile(
        r"\.session-focus__card--active\s+\.session-focus__sticky-cta\s*\{"
        r"[^}]*env\(safe-area-inset-bottom",
        re.DOTALL,
    )
    assert pattern.search(css), (
        "sticky CTA rule should include env(safe-area-inset-bottom)"
    )


def test_css_sticky_cta_has_background_and_border():
    """Sticky CTA must have an opaque background and a top separator."""
    css = _css()
    pattern = re.compile(
        r"\.session-focus__card--active\s+\.session-focus__sticky-cta\s*\{"
        r"[^}]*background[^}]*border-top",
        re.DOTALL,
    )
    # `background` then `border-top` (order may differ in the file)
    if pattern.search(css):
        return
    # Try reverse order
    pattern_rev = re.compile(
        r"\.session-focus__card--active\s+\.session-focus__sticky-cta\s*\{"
        r"[^}]*border-top[^}]*background",
        re.DOTALL,
    )
    assert pattern_rev.search(css), (
        "sticky CTA rule should include background + border-top"
    )


def test_css_sticky_cta_is_scoped_to_active_only():
    """Sticky positioning must not be applied to non-active cards.

    Heuristic line-scan: every selector line that contains
    `.session-focus__sticky-cta` and opens a rule (`{`) must also include
    the `.session-focus__card--active` scope. Multi-line selectors are
    not used in this stylesheet.
    """
    css = _css()
    for i, line in enumerate(css.splitlines()):
        if ".session-focus__sticky-cta" in line and "{" in line:
            assert ".session-focus__card--active" in line, (
                f"line {i + 1}: sticky-cta selector without --active scope: "
                f"{line.strip()!r}"
            )


def test_css_uses_z_index_explicit():
    css = _css()
    pattern = re.compile(
        r"\.session-focus__card--active\s+\.session-focus__sticky-cta\s*\{"
        r"[^}]*z-index",
        re.DOTALL,
    )
    assert pattern.search(css)


def test_tap_target_min_size_still_44px():
    css = _css()
    assert "min-height: 44px" in css or "min-height:44px" in css
    assert "min-width: 44px" in css or "min-width:44px" in css


# ───────── No new JS / no React introduced ─────────


def test_no_new_js_file_introduced():
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
        session = _seed_in_progress(db, user.id)
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
        assert forbidden not in body, f"forbidden token: {forbidden}"


def test_partial_has_no_script_tag():
    """The exercise_card partial must NOT contain any <script> tag.
    Sticky CTA is CSS-only."""
    src = PARTIAL.read_text(encoding="utf-8")
    assert "<script" not in src.lower()


# ───────── No-JS structural fallback preserved ─────────


def test_cta_button_remains_inside_form(client):
    """Even with the sticky wrapper, the primary CTA must remain inside
    the same <form> so a no-JS POST works identically."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_in_progress(db, user.id)
        session_id = session.id

    body = _render(client, session_id)
    # Crude DOM containment heuristic : the substring containing both
    # action="...update_exercise_card..." and the cta-primary marker must
    # exist before the matching </form>.
    # url_for resolves to the actual URL path (testserver/sessions/{id}/
    # exercises/{seid}), not the route name.
    pattern = re.compile(
        r'<form\b[^>]*action="[^"]*/sessions/\d+/exercises/\d+"[^>]*>'
        r"(.*?)</form>",
        re.DOTALL,
    )
    forms = pattern.findall(body)
    assert forms, "no per-exercise update form found"
    # At least one of the forms must include the sticky CTA wrapper +
    # the cta-primary button.
    matched = [
        f
        for f in forms
        if "session-focus__sticky-cta" in f and "session-focus__cta-primary" in f
    ]
    assert matched, (
        "no form contains the sticky CTA wrapper with cta-primary button"
    )


def test_route_still_200(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_in_progress(db, user.id)
        session_id = session.id

    r = client.get(f"/sessions/{session_id}", follow_redirects=False)
    assert r.status_code == 200


# ───────── Owner isolation preserved ─────────


def test_owner_isolation_unaffected(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.auth import hash_password

    with SessionLocal() as db:
        owner = db.query(User).first()
        session = _seed_in_progress(db, owner.id)
        session_id = session.id
        other = User(
            username="cta_other",
            password_hash=hash_password("cta_other_str_xyz"),  # noqa: S106
        )
        db.add(other)
        db.commit()

    client.cookies.clear()
    r = client.post(
        "/login",
        data={"username": "cta_other", "password": "cta_other_str_xyz"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    r = client.get(f"/sessions/{session_id}", follow_redirects=False)
    assert r.status_code == 404
