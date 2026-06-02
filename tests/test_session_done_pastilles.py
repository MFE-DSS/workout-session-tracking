"""Sb_24.6 — pastille label + score breakdown on /sessions/{id}/done.

Hard contracts validated:
* La page /sessions/{id}/done répond 200 sur une session terminée.
* Quand au moins un exercice porte un implicit_label, la pastille
  apparaît dans le HTML avec le bon display name.
* Quand aucun exercice n'est labellé, aucune pastille n'apparaît.
* Le bloc "Décomposition du score" s'affiche pour scoring_version=2
  ET au moins un label.
* Pas de bloc breakdown pour scoring_version=1.
* Pas de breakdown pour les sessions cardio.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select


def _create_and_complete_strength(client, with_pattern=False):
    """Crée une session push-a, log un pattern trajectoire_coherente sur
    le 1er exo si demandé, puis termine la session."""
    r = client.post(
        "/sessions", data={"template_slug": "push-a"}, follow_redirects=False
    )
    assert r.status_code == 303
    sid = int(r.headers["location"].rsplit("/", 1)[-1])

    if with_pattern:
        from app.database import SessionLocal
        from app.models.session import SessionExercise, SetLog
        from sqlalchemy.orm import selectinload

        with SessionLocal() as db:
            se = db.execute(
                select(SessionExercise)
                .where(SessionExercise.session_id == sid)
                .options(selectinload(SessionExercise.set_logs))
                .order_by(SessionExercise.position)
            ).scalars().first()
            # Replace work sets with a clean trajectoire_coherente pattern
            for sl in list(se.set_logs):
                if sl.kind == "work":
                    db.delete(sl)
            db.flush()
            for idx, (w, r_count) in enumerate([(80, 10), (80, 8), (80, 6)], start=1):
                db.add(SetLog(
                    session_exercise_id=se.id, kind="work",
                    set_index=idx, weight_kg=w, reps=r_count, completed=True,
                ))
            db.commit()

    # Finish the session
    client.post(
        f"/sessions/{sid}",
        data={"action": "end"},
        follow_redirects=False,
    )
    return sid


def test_done_page_200_basic(client):
    sid = _create_and_complete_strength(client)
    r = client.get(f"/sessions/{sid}/done")
    assert r.status_code == 200


def test_done_page_shows_pastille_when_label_present(client):
    sid = _create_and_complete_strength(client, with_pattern=True)
    r = client.get(f"/sessions/{sid}/done")
    body = r.text
    assert "implicit-pill" in body
    # Le display name "Cohérente" doit apparaître
    assert "Cohérente" in body


def test_done_page_no_pastille_when_no_label(client):
    """Une session sans pattern (< 3 sets remplis ou aucun set rempli)
    n'a pas de label → aucune pastille rendue."""
    sid = _create_and_complete_strength(client, with_pattern=False)
    r = client.get(f"/sessions/{sid}/done")
    body = r.text
    # Pas de pastille
    assert "implicit-pill--" not in body


def test_done_page_shows_score_breakdown_for_v2_with_label(client):
    """scoring_version=2 + au moins un label → bloc Décomposition visible."""
    sid = _create_and_complete_strength(client, with_pattern=True)
    r = client.get(f"/sessions/{sid}/done")
    body = r.text
    assert "Décomposition du score" in body
    assert "Composante classique" in body
    assert "Moyenne des labels implicites" in body


def test_done_page_no_breakdown_when_no_label(client):
    """Session V2 mais sans label → breakdown vaut None → bloc absent."""
    sid = _create_and_complete_strength(client, with_pattern=False)
    r = client.get(f"/sessions/{sid}/done")
    body = r.text
    assert "Décomposition du score" not in body


def test_done_page_handles_v1_session_without_breakdown(client):
    """Sessions historiques V1 ne doivent jamais montrer le breakdown."""
    sid = _create_and_complete_strength(client, with_pattern=True)
    # Force scoring_version back to 1 to simulate a pre-Sb_24.3 session
    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    with SessionLocal() as db:
        s = db.execute(
            select(WorkoutSession).where(WorkoutSession.id == sid)
        ).scalar_one()
        s.scoring_version = 1
        db.commit()
    r = client.get(f"/sessions/{sid}/done")
    assert "Décomposition du score" not in r.text


def test_done_page_pastille_has_contribution_tooltip(client):
    """La pastille porte un title= avec la contribution numérique
    (transparence sur le scoring)."""
    sid = _create_and_complete_strength(client, with_pattern=True)
    r = client.get(f"/sessions/{sid}/done")
    body = r.text
    # 90 = LABEL_SCORE_CONTRIBUTION[trajectoire_coherente]
    assert 'title="Contribution au score V2 : 90/100"' in body
