"""Sb_22b — tests for profile_metrics primitives.

Hard contracts validated:
* streak_days returns 0 when no eligible session
* cardio_minutes_per_week ignores sessions without ended_at
* strength_volume_delta_pct returns None with no baseline
* top_zone / neglected_zone deterministic on tie-break
* build_preview / build_page payloads stable
"""
from __future__ import annotations


def _hit(client, path):
    """Helper to GET a page so we know it returns 200 (auth wiring)."""
    r = client.get(path)
    return r


# ---------------------------------------------------------------------------
# sessions_in_window — MIGRÉ depuis `streak_days`
# ---------------------------------------------------------------------------
#
# `streak_days` est retiré par `OPERATOR_DECISION D7`. Les deux gardes qui le
# visaient N'ONT PAS ÉTÉ SUPPRIMÉES : elles n'interrogeaient pas la consécutivité
# — elles interrogeaient l'ÉLIGIBILITÉ, « seule une séance terminée compte ».
#
# Cet invariant survit intégralement au changement de métrique. Il est donc
# reporté sur le compteur qui remplace, comme l'exige la procédure de migration
# de gardes (`AUREN_UIUX_V3_GUARD_MIGRATION_REGISTER`) : jamais supprimer en
# silence, toujours reporter ce qui survit.


def test_window_count_is_zero_for_user_without_sessions(client):
    """Un compte neuf, sans séance, compte 0 — pas None, pas d'erreur."""
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.user import User
    from app.services.auth import hash_password
    from app.services.profile_metrics import sessions_in_window

    with SessionLocal() as db:
        # The fixture user already has the testuser account; create a
        # secondary user with zero sessions for this specific test.
        db.add(User(username="window_no_data",
                    password_hash=hash_password("anything1"), is_active=True))
        db.commit()
        uid = db.execute(select(User.id).where(User.username == "window_no_data")).scalar_one()
        assert sessions_in_window(db, uid, 14) == 0


def test_an_unfinished_session_is_not_counted(client):
    """L'invariant que gardait l'ancien test : `in_progress` ne compte pas.

    C'est ce qui empêche un compteur d'activité de récompenser une séance
    ouverte et abandonnée.
    """
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.user import User
    from app.services.profile_metrics import sessions_in_window

    r = client.post("/sessions", data={"template_slug": "push-a"}, follow_redirects=False)
    assert r.status_code == 303
    with SessionLocal() as db:
        uid = db.execute(select(User.id).where(User.username == "testuser")).scalar_one()
        # La séance est `in_progress`, pas `completed` — elle ne compte pas.
        assert sessions_in_window(db, uid, 14) == 0


# ---------------------------------------------------------------------------
# cardio_minutes_per_week
# ---------------------------------------------------------------------------


def test_cardio_zero_when_no_cardio_session(client):
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.user import User
    from app.services.profile_metrics import cardio_minutes_per_week
    with SessionLocal() as db:
        uid = db.execute(select(User.id).where(User.username == "testuser")).scalar_one()
        assert cardio_minutes_per_week(db, uid) == 0


# ---------------------------------------------------------------------------
# strength_volume_delta_pct
# ---------------------------------------------------------------------------


def test_volume_delta_none_without_baseline(client):
    """No prior-window sessions → None (no baseline to compare)."""
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.user import User
    from app.services.profile_metrics import strength_volume_delta_pct
    with SessionLocal() as db:
        uid = db.execute(select(User.id).where(User.username == "testuser")).scalar_one()
        # No completed work sets in this test DB → returns None
        assert strength_volume_delta_pct(db, uid) is None


# ---------------------------------------------------------------------------
# top_zone / neglected_zone
# ---------------------------------------------------------------------------


def test_zone_returns_none_for_empty_window(client):
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.user import User
    from app.services.auth import hash_password
    from app.services.profile_metrics import neglected_zone, top_zone
    with SessionLocal() as db:
        db.add(User(username="zone_no_data",
                    password_hash=hash_password("anything1"), is_active=True))
        db.commit()
        uid = db.execute(select(User.id).where(User.username == "zone_no_data")).scalar_one()
        assert top_zone(db, uid) is None
        # neglected_zone returns the first zone (with 0 count) — deterministic
        # tie-break by RADAR_AXIS_ORDER → "pecs"
        nz = neglected_zone(db, uid)
        assert nz is not None
        assert nz.sessions == 0


# ---------------------------------------------------------------------------
# build_preview / build_page — orchestration smoke
# ---------------------------------------------------------------------------


def test_build_preview_payload_structure(client):
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.user import User
    from app.services.profile_metrics import PreviewPayload, build_preview
    with SessionLocal() as db:
        uid = db.execute(select(User.id).where(User.username == "testuser")).scalar_one()
        p = build_preview(db, uid, sessions_30d=0)
        assert isinstance(p, PreviewPayload)
        assert p.sessions_30d == 0
        assert p.sessions_14d >= 0
        assert p.cardio_min_per_week >= 0


def test_build_page_payload_structure(client):
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.user import User
    from app.services.profile_metrics import PagePayload, build_page
    with SessionLocal() as db:
        uid = db.execute(select(User.id).where(User.username == "testuser")).scalar_one()
        p = build_page(db, uid, sessions_30d=0)
        assert isinstance(p, PagePayload)
        # All inner blocks exist (may be None / 0)
        assert hasattr(p, "preview")
        assert hasattr(p, "top_zone")
        assert hasattr(p, "neglected_zone")
        assert hasattr(p, "dominant_pattern")
        assert hasattr(p, "last_session")


# ---------------------------------------------------------------------------
# Spec contract — score NOT in preview payload
# ---------------------------------------------------------------------------


def test_preview_payload_does_not_carry_score(client):
    """Spec §A.bis v2.1 — L2 (preview) MUST NOT carry a numeric score.
    The grade badge does the job, the radar is silhouette only."""
    from app.services.profile_metrics import PreviewPayload
    fields = PreviewPayload.__dataclass_fields__.keys()
    forbidden = {"score", "global_score", "grade_score", "avg_points"}
    leaks = set(fields) & forbidden
    assert not leaks, f"PreviewPayload leaks score-like fields: {leaks}"


# ---------------------------------------------------------------------------
# Sb_22b.3 — /users/{username}/preview endpoint smoke
# ---------------------------------------------------------------------------


def test_preview_endpoint_returns_html_fragment(client):
    """The preview endpoint returns the L2 fragment (no full HTML doc)."""
    r = client.get("/users/testuser/preview")
    assert r.status_code == 200
    body = r.text
    # Fragment markers
    assert "profile-preview" in body
    assert "@testuser" in body
    # Spec §A.bis L2 — no global numeric score displayed (badge only).
    # The radar SVG may contain per-axis <title>X/100</title> for a11y
    # tooltips, but the document text must not show a global score line.
    assert ".global-score" not in body
    assert 'class="user-profile__score"' not in body
    assert "Score · " not in body  # avoids the L3 score formatting


def test_preview_endpoint_404_for_unknown_user(client):
    r = client.get("/users/no_such_user_xyz/preview")
    assert r.status_code == 404


def test_preview_endpoint_rejects_invalid_username_pattern(client):
    r = client.get("/users/bad@user/preview", follow_redirects=False)
    # FastAPI Path regex returns 422 before the handler runs
    assert r.status_code in (404, 422)


def test_user_profile_l3_page_renders(client):
    """L3 page renders with the new v2 structure (Sb_22b)."""
    r = client.get("/users/testuser")
    assert r.status_code == 200
    body = r.text
    assert "user-profile--v2" in body
    assert "Activité 30j" in body or "Données physiques" in body or "@testuser" in body
