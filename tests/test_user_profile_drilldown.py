"""Sb_19 — leaderboard drilldown (mini radar tooltip + /users/{username})."""
from __future__ import annotations

from datetime import UTC, datetime

from tests.helpers import get_test_user_id
from tests.test_leaderboard_ui import _add_session

# ---- Mini radar inside the leaderboard tooltip --------------------------


def test_leaderboard_tooltip_carries_no_physique_radar(client):
    """`TRAIN1-E` / C4 — GARDE RETOURNÉE.

    Elle EXIGEAIT le mini-radar dans l'infobulle. Or ce radar est l'analytique
    physique — les six axes de `compute_physique_dashboard` —, c'est-à-dire la
    doctrine que `TRAIN1-C` a retirée de Progression. La garder ici la
    réintroduisait par la porte sociale, et sur le profil des AUTRES.

    L'infobulle RESTE, avec la note sociale : un classement sans ordre n'est
    pas un classement, et la lettre vient de `compute_grade`, dérivée de la
    qualité de séance, pas du physique.
    """
    uid = get_test_user_id()
    _add_session(uid, quality_inputs={
        "concentration": "high", "global_state": "good", "success_score": 100,
    })
    body = client.get("/leaderboard").text
    assert "tooltip-content--rich" in body
    assert "grade-badge" in body
    assert "tooltip-radar" not in body


def test_leaderboard_username_is_clickable(client):
    uid = get_test_user_id()
    _add_session(uid, quality_inputs={
        "concentration": "high", "global_state": "good", "success_score": 100,
    })
    body = client.get("/leaderboard").text
    assert "lb-row__name-link" in body
    # url_for produces absolute or relative depending on context; assert
    # the path appears in the link href.
    assert "/users/testuser" in body


# ---- Public profile page /users/{username} ------------------------------


def test_user_profile_returns_200_for_active_user(client):
    uid = get_test_user_id()
    _add_session(uid, quality_inputs={
        "concentration": "high", "global_state": "good", "success_score": 100,
    })
    r = client.get("/users/testuser")
    assert r.status_code == 200
    body = r.text
    assert "testuser" in body
    # `TRAIN1-E` / C4 — la lettre RESTE (note sociale), le radar et le score
    # physique partent : un score sur 100 que le produit ne sait pas justifier
    # est déjà discutable pour soi ; rendu sur autrui, il devient une
    # comparaison, que le contrat du rapport coach s'interdit explicitement.
    assert "grade-badge" in body
    assert "user-profile__radar" not in body
    assert "radar-wrap" not in body


def test_user_profile_returns_404_for_unknown_user(client):
    r = client.get("/users/this-user-does-not-exist")
    assert r.status_code == 404


def test_user_profile_returns_404_for_inactive_user(client):
    """Deactivated user must not be reachable via /users/{username}."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        u = User(
            username="ghostuser",
            password_hash="x",
            is_active=False,
        )
        db.add(u)
        db.commit()

    r = client.get("/users/ghostuser")
    assert r.status_code == 404


def test_user_profile_exposes_height_and_weight_when_present(client):
    """Public metadata only when set on the User row."""
    uid = get_test_user_id()
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        u = db.get(User, uid)
        u.height_cm = 178
        u.weight_kg = 78.5
        db.commit()

    body = client.get("/users/testuser").text
    assert "178 cm" in body
    assert "78,5 kg" in body


def test_user_profile_does_not_leak_session_details(client):
    """Sb_19 disclosure contract: no per-session detail on the public page.

    The synthesis page must not expose exercise names, set logs, or
    free notes — even if the user has a rich session history. We seed
    a session with a distinctive exercise name and assert it does NOT
    appear on /users/{username}.
    """
    uid = get_test_user_id()
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    with SessionLocal() as db:
        s = WorkoutSession(
            user_id=uid,
            template_slug_snapshot="push-a",
            template_name_snapshot="Push A",
            started_at=datetime.now(UTC),
            status="completed",
            free_note="A SECRET PRIVATE NOTE",
        )
        se = SessionExercise(
            exercise_code_snapshot="E1",
            exercise_name_snapshot="DistinctiveSecretExerciseName",
            position=1,
            success_score=80,
            free_note="exercise secret",
        )
        se.set_logs.append(SetLog(
            kind="work", set_index=1, weight_kg=60.0, reps=10, completed=True,
        ))
        s.session_exercises.append(se)
        db.add(s)
        db.commit()

    body = client.get("/users/testuser").text
    assert "DistinctiveSecretExerciseName" not in body
    assert "A SECRET PRIVATE NOTE" not in body
    assert "exercise secret" not in body
