"""Sprint 4 integration tests for the exercise history detail page
and the delta surface on session detail."""
from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta

from tests.helpers import get_test_user_id


def _new_session(client, slug: str = "push-a") -> int:
    r = client.post("/sessions", data={"template_slug": slug}, follow_redirects=False)
    return int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


def _manual_session(
    *,
    template_slug: str,
    template_name: str,
    exercise_code: str,
    exercise_name: str,
    work_sets: list[dict],
    status: str = "completed",
    success_score: int | None = None,
    started_at: datetime | None = None,
) -> int:
    """Insert a hand-crafted session bypassing the builder."""
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    with SessionLocal() as db:
        s = WorkoutSession(
            template_id=None,
            template_slug_snapshot=template_slug,
            template_name_snapshot=template_name, user_id=get_test_user_id(),
            started_at=started_at or datetime.now(UTC),
            status=status,
        )
        se = SessionExercise(
            template_exercise_id=None,
            exercise_code_snapshot=exercise_code,
            exercise_name_snapshot=exercise_name,
            position=1,
            success_score=success_score,
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
        s.session_exercises.append(se)
        db.add(s)
        db.commit()
        return s.id


# ---------------------------------------------------------------------------
# /exercise-history page
# ---------------------------------------------------------------------------


def test_exercise_history_renders_empty_state_for_unknown_identity(client):
    r = client.get("/exercise-history/push-a/E2")
    assert r.status_code == 200
    assert "Aucune séance pour cet exercice" in r.text


def test_exercise_history_handles_unknown_template_slug(client):
    r = client.get("/exercise-history/does-not-exist/E2")
    assert r.status_code == 200
    assert "Aucune séance pour cet exercice" in r.text


def test_exercise_history_lists_occurrences_newest_first(client):
    now = datetime.now(UTC)
    _manual_session(
        template_slug="push-a",
        template_name="Push A",
        exercise_code="E2",
        exercise_name="Incline Smith Chest Press",
        work_sets=[{"weight_kg": 60.0, "reps": 10}],
        started_at=now - timedelta(days=7),
        success_score=80,
    )
    _manual_session(
        template_slug="push-a",
        template_name="Push A",
        exercise_code="E2",
        exercise_name="Incline Smith Chest Press",
        work_sets=[{"weight_kg": 62.5, "reps": 10}],
        started_at=now - timedelta(days=1),
        success_score=100,
    )
    r = client.get("/exercise-history/push-a/E2")
    assert r.status_code == 200
    body = r.text
    assert "Incline Smith Chest Press" in body
    assert "2 occurrences" in body
    # Most recent (62.5 kg) must appear before the older one (60 kg)
    i_recent = body.find("62.5 kg")
    i_old = body.find("60 kg")
    assert 0 <= i_recent < i_old


def test_exercise_history_cross_template_isolation(client):
    _manual_session(
        template_slug="pull-b",
        template_name="Pull B",
        exercise_code="E2",
        exercise_name="Tirage nuque",
        work_sets=[{"weight_kg": 70.0, "reps": 8}],
    )
    r = client.get("/exercise-history/push-a/E2")
    body = r.text
    assert "70 kg" not in body
    assert "Aucune séance pour cet exercice" in body


def test_exercise_history_renders_delta_vs_next_older(client):
    now = datetime.now(UTC)
    _manual_session(
        template_slug="push-a",
        template_name="Push A",
        exercise_code="E2",
        exercise_name="Incline Smith Chest Press",
        work_sets=[{"weight_kg": 60.0, "reps": 8}],
        started_at=now - timedelta(days=7),
        success_score=80,
    )
    _manual_session(
        template_slug="push-a",
        template_name="Push A",
        exercise_code="E2",
        exercise_name="Incline Smith Chest Press",
        work_sets=[{"weight_kg": 62.5, "reps": 10}],
        started_at=now - timedelta(days=1),
        success_score=100,
    )
    r = client.get("/exercise-history/push-a/E2")
    body = r.text
    # Most recent row shows +2.5 kg · +2 reps · score en hausse
    assert "+2.5 kg" in body
    assert "+2 reps" in body
    assert "score en hausse" in body


def test_exercise_history_no_delta_on_oldest_row(client):
    """The oldest row has nothing older to compare against — it
    must not render a delta badge."""
    _manual_session(
        template_slug="push-a",
        template_name="Push A",
        exercise_code="E2",
        exercise_name="Incline Smith Chest Press",
        work_sets=[{"weight_kg": 60.0, "reps": 10}],
    )
    r = client.get("/exercise-history/push-a/E2")
    body = r.text
    # Exactly one row, no delta
    assert "badge--delta" not in body


# ---------------------------------------------------------------------------
# Delta surface on the session detail page
# ---------------------------------------------------------------------------


def test_session_detail_shows_delta_when_prior_exists(client):
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog

    # Prior: 60 kg x 8
    _manual_session(
        template_slug="push-a",
        template_name="Push A",
        exercise_code="E2",
        exercise_name="Incline Smith Chest Press",
        work_sets=[{"weight_kg": 60.0, "reps": 8}],
        started_at=datetime.now(UTC) - timedelta(days=3),
        success_score=80,
    )
    # Current Push A
    sid = _new_session(client, "push-a")
    with SessionLocal() as db:
        se = db.execute(
            select(SessionExercise)
            .where(SessionExercise.session_id == sid)
            .where(SessionExercise.exercise_code_snapshot == "E2")
        ).scalar_one()
        se_id = se.id
        work_ids = sorted([
            s.id for s in db.execute(
                select(SetLog).where(SetLog.session_exercise_id == se_id)
            ).scalars().all()
            if s.kind == "work"
        ])
    # Fill ALL work sets with 62.5 kg x 12 so derived score hits 100
    data = {"muscle_sensation": "strong"}
    for wid in work_ids:
        data[f"set_{wid}_weight_kg"] = "62.5"
        data[f"set_{wid}_reps"] = "12"
        data[f"set_{wid}_completed"] = "1"
    client.post(
        f"/sessions/{sid}/exercises/{se_id}",
        data=data,
        follow_redirects=False,
    )
    body = client.get(f"/sessions/{sid}").text
    assert "Delta" in body
    assert "+2.5 kg" in body
    assert "+4 reps" in body
    assert "score en hausse" in body


def test_session_detail_has_no_delta_without_prior(client):
    sid = _new_session(client, "push-a")
    body = client.get(f"/sessions/{sid}").text
    # No prior -> no Delta block (the Dernière fois block still shows
    # the empty state).
    assert "delta__label" not in body


# ---------------------------------------------------------------------------
# Navigation integration
# ---------------------------------------------------------------------------


def test_session_detail_links_exercise_code_to_history_page(client):
    """L'historique d'un exercice reste atteignable depuis la séance.

    ⚠ `D1 = variante D`, tranché par l'opérateur : le lien d'historique
    RÉPÉTÉ sur chaque carte repliée est retiré — il était dupliqué six fois
    pour un accès que la carte ACTIVE porte déjà.

    Cette garde visait `E2`, un exercice NON actif. Elle mesurait donc la
    duplication, pas l'accès. La propriété réelle — « depuis la séance, on
    atteint l'historique d'un exercice » — est vérifiée ici sur les deux
    chemins qui la portent : l'exercice actif directement, et n'importe quel
    autre après activation (le geste que `DF-E` a rendu possible).
    """
    sid = _new_session(client, "push-a")
    body = client.get(f"/sessions/{sid}").text
    assert "/exercise-history/push-a/E1" in body, (
        "l'exercice actif n'expose plus son historique"
    )

    import re as _re

    target = _re.search(r'href="([^"]*\?active=\d+[^"]*)"', body)
    assert target, "aucun lien d'activation — voir `DF-E`"
    on_other = client.get(target.group(1).split("#", 1)[0]).text
    assert _re.search(r"/exercise-history/push-a/E\d", on_other), (
        "activer un autre exercice n'expose pas son historique"
    )


def test_progress_links_to_exercise_history_on_the_stable_identity(client):
    """`TRAIN1-B` — RÉORIENTÉ, PAS AFFAIBLI.

    Ce test assertait `/exercise-history/push-a/E2` sur `/progress` : le
    drill-down par identité HÉRITÉE `(gabarit, code)`. Décision opérateur :
    « converger le drill-down d'historique d'exercice sur la même identité
    stable ; conserver les entrées héritées en compatibilité seulement ».

    L'invariant — « depuis Progression on atteint l'historique d'un
    exercice » — est intact. Ce qui change est la clé, et pour cause :
    `Leg extensions assises` vit dans 4 gabarits sous 3 codes, donc l'ancienne
    entrée ne menait jamais qu'à un quart de son histoire.
    """
    _manual_session(
        template_slug="push-a",
        template_name="Push A",
        exercise_code="E2",
        exercise_name="Chest Press machine",
        work_sets=[{"weight_kg": 60.0, "reps": 10}],
        success_score=80,
    )
    _manual_session(
        template_slug="push-b",
        template_name="Push B",
        exercise_code="E1",
        exercise_name="Chest Press machine",
        work_sets=[{"weight_kg": 62.5, "reps": 10}],
        success_score=80,
    )
    body = client.get("/progress").text
    assert "/exercise-history/chest-press-machine" in body


def test_the_legacy_two_segment_entrypoint_still_answers(client):
    """« conservées en compatibilité » veut dire qu'elles répondent encore :
    des liens existants la visent, et casser une URL pour gagner de
    l'élégance serait un mauvais échange."""
    _manual_session(
        template_slug="push-a",
        template_name="Push A",
        exercise_code="E2",
        exercise_name="Chest Press machine",
        work_sets=[{"weight_kg": 60.0, "reps": 10}],
        success_score=80,
    )
    r = client.get("/exercise-history/push-a/E2", follow_redirects=False)
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# History / resume duration display
# ---------------------------------------------------------------------------


def test_history_row_shows_duration_for_completed_session(client):
    sid = _new_session(client, "push-a")
    # End the session right away: duration should be "< 1 min"
    client.post(f"/sessions/{sid}", data={"action": "end"}, follow_redirects=False)
    body = client.get("/history").text
    assert "durée" in body
    assert "< 1 min" in body or "0 min" in body


def test_history_row_shows_depuis_for_in_progress_session(client):
    _new_session(client, "push-a")
    body = client.get("/history").text
    assert "depuis" in body


def test_home_resume_tile_shows_duration_since_start(client):
    _new_session(client, "push-a")
    body = client.get("/").text
    assert "depuis" in body
