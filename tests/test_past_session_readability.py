"""Sprint 3 readability improvements on past sessions + /progress."""
from __future__ import annotations

import re
from datetime import UTC

from tests.helpers import get_test_user_id


def _start_session(client, slug="push-a") -> int:
    r = client.post("/sessions", data={"template_slug": slug}, follow_redirects=False)
    return int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


def test_in_progress_session_has_no_completed_marker(client):
    sid = _start_session(client, "push-a")
    body = client.get(f"/sessions/{sid}").text
    assert "session-page--completed" not in body
    # Banner note only shows once the session has been terminated.
    assert "Séance terminée" not in body


# NOTE (Sb_R3): the former tests
#   - test_completed_session_has_readability_markers
#   - test_completed_session_shows_per_card_summary_when_work_sets_filled
# asserted against the completed-mode render of session_detail.html.
# That rendering no longer happens: completed sessions now redirect to
# /sessions/{id}/done (dedicated recap template). Equivalent coverage
# lives in tests/test_session_done.py. Task 5 will strengthen the recap
# assertions (per-exercise work set counts, weights_str).


def test_progress_page_has_an_exercise_activity_section(client):
    """`TRAIN1-B` / A10 — RÉORIENTÉ, PAS AFFAIBLI.

    Ce test assertait « Activité récente par exercice ». Ce bloc listait, par
    exercice, la dernière charge et les dernières reps — exactement ce que
    l'instrument progressif rend, en le COMPARANT à l'occurrence précédente.

    Il était clavé sur l'identité HÉRITÉE `(gabarit, code)` : vu au rendu, il
    affichait « Chest Press machine » DEUX FOIS, une par gabarit. Garder les
    deux blocs aurait ajouté une duplication à l'écran que `TRAIN1-A` venait
    d'écrémer.

    L'invariant utile — **Progression rend l'activité par exercice** — est
    intact ; c'est le bloc qui le porte qui change.
    """
    from datetime import datetime, timedelta

    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    with SessionLocal() as db:
        for days, w in ((6, 60.0), (2, 62.5)):
            s = WorkoutSession(
                template_slug_snapshot="push-a", template_name_snapshot="Push A",
                user_id=get_test_user_id(),
                started_at=datetime.now(UTC) - timedelta(days=days),
                status="completed", excluded_from_stats=False,
            )
            se = SessionExercise(
                exercise_code_snapshot="E1",
                exercise_name_snapshot="Chest Press machine",
                position=1, success_score=80,
            )
            se.set_logs.append(SetLog(kind="work", set_index=1, weight_kg=w,
                                      reps=10, completed=True))
            s.session_exercises.append(se)
            db.add(s)
        db.commit()

    body = client.get("/progress").text
    assert "Activité récente par exercice" not in body
    assert "Progression par exercice" in body
    assert "Chest Press machine" in body


def test_progress_exercise_activity_shows_completed_exercises(client):
    from datetime import datetime, timedelta

    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    with SessionLocal() as db:
        s = WorkoutSession(
            template_slug_snapshot="push-a",
            template_name_snapshot="Push A", user_id=get_test_user_id(),
            started_at=datetime.now(UTC) - timedelta(days=2),
            status="completed",
        )
        se = SessionExercise(
            exercise_code_snapshot="E2",
            exercise_name_snapshot="Incline Smith Chest Press",
            position=2,
            success_score=80,
        )
        se.set_logs.append(
            SetLog(kind="work", set_index=1, weight_kg=62.5, reps=10, completed=True)
        )
        se.set_logs.append(
            SetLog(kind="work", set_index=2, weight_kg=60.0, reps=8, completed=True)
        )
        s.session_exercises.append(se)
        db.add(s)
        db.commit()

    body = client.get("/progress").text
    # `TRAIN1-B` — RÉORIENTÉ. L'ancien bloc listait TOUTES les séries
    # (« 62.5 / 60 kg »). L'instrument progressif rend le point de
    # comparaison — la PREMIÈRE série de travail complétée — parce que c'est
    # celui que `delta.py` compare partout ailleurs dans ce dépôt ; en changer
    # ici rendrait les deux surfaces incohérentes. La liste complète des
    # séries vit dans le drill-down d'historique, où elle a sa place.
    #
    # « Incline Smith Chest Press » n'appartient pas au catalogue : il ne se
    # résout vers aucune identité, donc il n'est pas comparé — et la surface
    # le DIT plutôt que de le taire.
    assert "ne rattache à aucun exercice connu" in body
    assert "Incline Smith Chest Press" in body


def test_progress_exercise_activity_ignores_in_progress_sessions(client):
    from datetime import datetime

    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    with SessionLocal() as db:
        s = WorkoutSession(
            template_slug_snapshot="legs",
            template_name_snapshot="Legs", user_id=get_test_user_id(),
            started_at=datetime.now(UTC),
            status="in_progress",  # should NOT surface
        )
        se = SessionExercise(
            exercise_code_snapshot="E1",
            exercise_name_snapshot="Relevés des mollets debout",
            position=1,
        )
        se.set_logs.append(
            SetLog(kind="work", set_index=1, weight_kg=100.0, reps=10, completed=True)
        )
        s.session_exercises.append(se)
        db.add(s)
        db.commit()

    body = client.get("/progress").text
    assert "Relevés des mollets" not in body
