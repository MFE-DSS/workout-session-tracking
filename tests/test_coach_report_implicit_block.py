"""Sb_24.7 — Coach Report bloc Implicite 30j.

Hard contracts validated:
* ImplicitSignalsBlock builds correctly from the user's labeled exercises.
* Distribution sorted descending by count + pct rounded.
* Dominant = first item if any labeled exos, else None.
* Empty state when no labeled exercises in 30j.
* Cross-user isolation: user A's labels don't leak into user B's report.
* Coach report page renders the new block with tag Inféré.
* Empty state message renders when no data.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select


def _seed_labeled_session(user_id: int, labels: list[str], days_ago: int = 1):
    """Create a completed session with N session_exercises each carrying
    a different implicit_label. Returns session_id."""
    from app.database import SessionLocal
    from app.models.session import SessionExercise, WorkoutSession

    started = datetime.now(timezone.utc) - timedelta(days=days_ago)
    with SessionLocal() as db:
        s = WorkoutSession(
            user_id=user_id,
            template_slug_snapshot="push-a",
            template_name_snapshot="Push A",
            started_at=started,
            ended_at=started + timedelta(minutes=60),
            status="completed",
            scoring_version=2,
        )
        db.add(s)
        db.flush()
        for idx, lab in enumerate(labels, start=1):
            db.add(SessionExercise(
                session_id=s.id,
                exercise_code_snapshot=f"E{idx}",
                exercise_name_snapshot=f"Exo {idx}",
                position=idx,
                implicit_label=lab,
                implicit_label_computed_at=started,
            ))
        db.commit()
        return s.id


def _get_user_id(client, username: str) -> int:
    from app.database import SessionLocal
    from app.models.user import User
    with SessionLocal() as db:
        return db.execute(
            select(User.id).where(User.username == username)
        ).scalar_one()


# ---------------------------------------------------------------------------
# ImplicitSignalsBlock unit tests
# ---------------------------------------------------------------------------


def test_empty_block_when_no_labeled_exercises(client):
    """Aucun exercice labellé sur 30j → total = 0, distribution vide."""
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.auth import hash_password
    from app.services.coach_report import _implicit_signals_30d

    with SessionLocal() as db:
        u = User(
            username="empty_implicit",
            password_hash=hash_password("anything1"),
            is_active=True,
        )
        db.add(u)
        db.commit()
        block = _implicit_signals_30d(db, u.id)
    assert block.total_labeled_exercises == 0
    assert block.distribution == []
    assert block.dominant is None


def test_block_aggregates_labels_correctly(client):
    """3 trajectoire_coherente + 2 reserve_probable + 1 incoherent →
    distribution sorted desc, dominant = trajectoire_coherente."""
    from app.database import SessionLocal
    from app.services.coach_report import _implicit_signals_30d

    uid = _get_user_id(client, "testuser")
    _seed_labeled_session(uid, [
        "trajectoire_coherente",
        "trajectoire_coherente",
        "trajectoire_coherente",
        "reserve_probable",
        "reserve_probable",
        "incoherent",
    ])

    with SessionLocal() as db:
        block = _implicit_signals_30d(db, uid)

    assert block.total_labeled_exercises == 6
    # First item = dominant
    assert block.dominant == ("trajectoire_coherente", "Cohérente")
    # Distribution descending
    assert block.distribution[0][2] == 3  # count
    assert block.distribution[0][3] == 50  # pct
    assert block.distribution[1][2] == 2
    assert block.distribution[1][3] == 33  # round(100*2/6) = 33
    assert block.distribution[2][2] == 1


def test_block_ignores_sessions_outside_window(client):
    """Une session vieille de 35 jours ne contribue pas au 30j."""
    from app.database import SessionLocal
    from app.services.coach_report import _implicit_signals_30d

    uid = _get_user_id(client, "testuser")
    _seed_labeled_session(uid, ["trajectoire_coherente"], days_ago=35)

    with SessionLocal() as db:
        block = _implicit_signals_30d(db, uid)
    # No labels in the 30d window
    assert block.total_labeled_exercises == 0


def test_block_isolates_users(client):
    """Les labels de l'user A ne contaminent pas le report de l'user B."""
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.auth import hash_password
    from app.services.coach_report import _implicit_signals_30d

    # Create user B with their own labeled session
    with SessionLocal() as db:
        b = User(
            username="other_user",
            password_hash=hash_password("anything1"),
            is_active=True,
        )
        db.add(b)
        db.commit()
        b_id = b.id

    _seed_labeled_session(b_id, ["reserve_probable"] * 5)
    # testuser has no labeled session → its block must remain empty
    uid = _get_user_id(client, "testuser")

    with SessionLocal() as db:
        block_test = _implicit_signals_30d(db, uid)
    assert block_test.total_labeled_exercises == 0


def test_block_ignores_invalid_label_values(client):
    """Un label hors enum (saisi par erreur via SQL direct) est ignoré."""
    from app.database import SessionLocal
    from app.services.coach_report import _implicit_signals_30d

    uid = _get_user_id(client, "testuser")
    _seed_labeled_session(uid, [
        "trajectoire_coherente",
        "not_a_real_label",  # invalid — should be filtered out
    ])

    with SessionLocal() as db:
        block = _implicit_signals_30d(db, uid)
    # Only the valid label contributes
    assert block.total_labeled_exercises == 1


# ---------------------------------------------------------------------------
# End-to-end : the /coach-report page renders the new block
# ---------------------------------------------------------------------------


def test_coach_report_page_renders_implicit_block(client):
    """La page rend le nouveau bloc + le tag Inféré."""
    uid = _get_user_id(client, "testuser")
    _seed_labeled_session(uid, ["trajectoire_coherente", "reserve_probable"])
    r = client.get("/coach-report")
    assert r.status_code == 200
    body = r.text
    assert "Signaux d'effort 30j" in body
    assert "Inféré" in body
    # Display names visible
    assert "Cohérente" in body
    assert "Réserve probable" in body


def test_coach_report_page_renders_empty_state(client):
    """Si aucun label, on affiche un message explicatif, pas une distrib vide."""
    r = client.get("/coach-report")
    assert r.status_code == 200
    body = r.text
    assert "Signaux d'effort 30j" in body
    # Empty state message
    assert "Pas d'exercice labellé" in body or "labellé sur les 30 derniers jours" in body


def test_coach_report_implicit_block_tagged_inferred(client):
    """Spec §B.bis : tous les blocs doivent porter un tag explicite.
    Ce nouveau bloc est tagué Inféré (statistique dérivée)."""
    r = client.get("/coach-report")
    body = r.text
    # The new block's heading should be followed by the Inféré tag
    idx = body.find("Signaux d'effort 30j")
    assert idx >= 0
    # Look for Inféré within 200 chars after the heading
    surrounding = body[idx : idx + 200]
    assert "Inféré" in surrounding
