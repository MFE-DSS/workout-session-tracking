"""Tests for the Dernière fois block on the session detail page.

Covers:
- empty state when there is no prior session
- populated state when a prior session has completed work sets
- current session is strictly excluded from its own lookup
- warmup rows never contribute
- incomplete prior sets are excluded
- cross-template isolation (E2 on Push A != E2 on Pull B)
"""
from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta

from tests.helpers import get_test_user_id


def _new_session(client, slug: str = "push-a") -> int:
    r = client.post("/sessions", data={"template_slug": slug}, follow_redirects=False)
    m = re.match(r"/sessions/(\d+)", r.headers["location"])
    return int(m.group(1))


def _render_exercise(client, session_id: int, code: str) -> str:
    """La page de séance AVEC l'exercice `code` actif.

    ⚠ `UI-CP2` — POURQUOI CES GARDES NAVIGUENT MAINTENANT.

    Elles lisaient le bloc « Dernière fois » sur les cartes REPLIÉES des
    exercices inactifs. A+ ne rend plus que l'exercice ACTIF : l'instrument
    répond à « que fais-je maintenant », et sept performances passées
    empilées ne servaient pas cette question.

    La capacité n'est pas perdue, elle est DÉPLACÉE AU POINT DE DÉCISION :
    la référence de l'exercice s'affiche quand on l'exécute. `?active=` est
    une sélection SERVEUR — pas une ancre — et elle existait déjà.

    Ces gardes vérifient donc la même chose qu'avant : que la performance
    précédente atteint l'utilisateur. Elles la cherchent là où elle est
    désormais utile.
    """
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import SessionExercise

    with SessionLocal() as db:
        se_id = db.execute(
            select(SessionExercise.id).where(
                SessionExercise.session_id == session_id,
                SessionExercise.exercise_code_snapshot == code,
            )
        ).scalars().first()
    assert se_id is not None, f"aucun exercice {code} dans la séance {session_id}"
    r = client.get(f"/sessions/{session_id}?active={se_id}")
    assert r.status_code == 200, r.text[:300]
    return r.text


def _manually_insert_prior_session(
    client,
    *,
    template_slug: str,
    template_name: str,
    exercise_code: str,
    exercise_name: str,
    work_sets: list[dict],
    started_at: datetime | None = None,
) -> int:
    """Create a prior session with a single SessionExercise + given
    work sets, bypassing the normal builder to control exact values
    and avoid interfering with the current session's tree.
    """
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    with SessionLocal() as db:
        prior = WorkoutSession(
            template_id=None,
            template_slug_snapshot=template_slug,
            template_name_snapshot=template_name, user_id=get_test_user_id(),
            started_at=started_at or (datetime.now(UTC) - timedelta(days=5)),
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


def test_last_time_is_absent_when_no_prior_session(client):
    sid = _new_session(client, "push-a")
    r = client.get(f"/sessions/{sid}")
    assert r.status_code == 200
    body = r.text
    # Sx_UI_06 D1 : the « Dernière fois » block is now suppressed on the
    # ACTIVE card (its previous-load info lives in the console « Référence
    # précédente »). It still renders on every NON-active card, so the empty
    # state shows for the 6 non-active exercises (7 total − 1 active).
    # ⚠ `UI-CP2` — CE COMPTAGE DÉCRIVAIT LA LISTE, PAS LA CAPACITÉ.
    # « au moins six » supposait que les six exercices INACTIFS soient rendus.
    # A+ ne rend que l'actif : compter les autres reviendrait à exiger la
    # composition que la refonte retire. Ce qui doit tenir, c'est qu'AUCUNE
    # performance ne soit INVENTÉE là où il n'y en a pas.
    assert "Aucune référence prescrite" in body
    assert "Réf." not in body, "une référence apparaît sans séance précédente"


def test_last_time_shows_weights_and_reps_when_prior_exists(client):
    _manually_insert_prior_session(
        client,
        template_slug="push-a",
        template_name="Push A",
        exercise_code="E2",
        exercise_name="Incline Smith Chest Press",
        work_sets=[
            {"weight_kg": 60.0, "reps": 10},
            {"weight_kg": 62.5, "reps": 8},
            {"weight_kg": 55.0, "reps": 12},
        ],
    )
    sid = _new_session(client, "push-a")
    body = _render_exercise(client, sid, "E2")
    # Our compact format: "60 / 62.5 / 55 kg · 10 / 8 / 12 reps"
    # (HTML escaping may apply to the middle dot but "kg" and "reps" are ASCII).
    assert "60 / 62.5 / 55 kg" in body
    # `UI-CP2` — le format de la CONSOLE est `… kg × …`, celui de la carte
    # repliée était `… kg · … reps`. La donnée est la même ; seule
    # l'écriture change, et c'est celle qui atteint désormais l'œil.
    assert "10 / 8 / 12" in body


def test_current_session_is_excluded_from_its_own_last_time(client):
    """Create one session, fill E1, re-GET it and expect the E1 card
    to still show the empty state (not the values you just saved)."""
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import SessionExercise

    sid = _new_session(client, "push-a")
    with SessionLocal() as db:
        se = db.execute(
            select(SessionExercise)
            .where(SessionExercise.session_id == sid)
            .where(SessionExercise.exercise_code_snapshot == "E1")
        ).scalar_one()
        se_id = se.id
        work_ids = sorted([s.id for s in se.set_logs if s.kind == "work"])

    # Fill E1 work sets with completed values
    data = {
        "muscle_sensation": "strong",
    }
    for idx, set_id in enumerate(work_ids, start=1):
        data[f"set_{set_id}_weight_kg"] = str(50 + idx)
        data[f"set_{set_id}_reps"] = "10"
        data[f"set_{set_id}_completed"] = "1"
    client.post(f"/sessions/{sid}/exercises/{se_id}", data=data, follow_redirects=False)

    body = _render_exercise(client, sid, "E1")

    # Current session is excluded from its own last-time lookup: every
    # NON-active card still shows the empty state. Sx_UI_06 D1 : the active
    # card (E1, just filled) no longer renders the « Dernière fois » block
    # (its info lives in the console « Référence précédente »), so the empty
    # state shows on the 6 non-active cards.
    # NB: the just-saved values DO legitimately appear in this session's own
    # compact recap (.exercise-card__recap) — that is the CURRENT session, not
    # a previous-load — so we do not assert their global absence here.
    # ⚠ `UI-CP2` — CE COMPTAGE DÉCRIVAIT LA LISTE, PAS LA CAPACITÉ.
    # « au moins six » supposait que les six exercices INACTIFS soient rendus.
    # A+ ne rend que l'actif : compter les autres reviendrait à exiger la
    # composition que la refonte retire. Ce qui doit tenir, c'est qu'AUCUNE
    # performance ne soit INVENTÉE là où il n'y en a pas.
    assert "Aucune référence prescrite" in body
    assert "Réf." not in body, "une référence apparaît sans séance précédente"


def test_last_time_uses_only_completed_work_sets(client):
    """Prior session has 3 work set rows but only 2 were marked
    completed. The summary must reflect only the completed ones."""
    _manually_insert_prior_session(
        client,
        template_slug="push-a",
        template_name="Push A",
        exercise_code="E2",
        exercise_name="Incline Smith Chest Press",
        work_sets=[
            {"weight_kg": 60.0, "reps": 10, "completed": True},
            {"weight_kg": 62.5, "reps": 8, "completed": True},
            {"weight_kg": None, "reps": None, "completed": False},
        ],
    )
    sid = _new_session(client, "push-a")
    body = _render_exercise(client, sid, "E2")
    assert "60 / 62.5 kg" in body
    assert "10 / 8" in body
    # The dropped (incomplete) third set must NOT have leaked "— kg" noise.
    assert "60 / 62.5 / —" not in body


def test_last_time_is_template_scoped(client):
    """A prior session on Pull B must not surface for Push A."""
    _manually_insert_prior_session(
        client,
        template_slug="pull-b",
        template_name="Pull B",
        exercise_code="E2",
        exercise_name="Tirage nuque / tirage vertical prise large",
        work_sets=[{"weight_kg": 70.0, "reps": 6}],
    )
    sid = _new_session(client, "push-a")
    body = _render_exercise(client, sid, "E2")
    # The Pull B values must not leak onto the Push A page
    assert "70 kg" not in body


def test_last_time_with_prior_but_no_completed_data(client):
    """Prior session exists but had no completed work sets. The
    block must render the date but a clear 'no data' message."""
    _manually_insert_prior_session(
        client,
        template_slug="push-a",
        template_name="Push A",
        exercise_code="E2",
        exercise_name="Incline Smith Chest Press",
        work_sets=[
            {"weight_kg": None, "reps": None, "completed": False},
        ],
    )
    sid = _new_session(client, "push-a")
    body = _render_exercise(client, sid, "E2")
    # La console nomme l'absence de référence PRESCRITE ; « aucune donnée
    # saisie » était le vocabulaire du bloc replié, qui n'existe plus.
    assert "Aucune référence prescrite" in body
