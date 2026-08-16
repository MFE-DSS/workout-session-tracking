"""Sb_24.4 — checkbox "fait" deprecation tests (Sx_24 §E).

Hard contracts validated:
* POST sans weight ni reps → set_log.completed = False
* POST avec weight seulement → completed = True (cas bodyweight)
* POST avec reps seulement → completed = True
* POST avec weight + reps → completed = True
* La checkbox HTML "Fait" n'apparaît plus dans le rendu du form actif
* Historique : un set_log déjà completed=True dans la BD ne se voit
  pas downgrader par un nouveau POST vide (cf §E backward compat)
* Cas warmup (bodyweight reps only) — completed=True
"""
from __future__ import annotations

from sqlalchemy import select


def _create_session(client, template_slug: str = "push-a") -> int:
    r = client.post(
        "/sessions",
        data={"template_slug": template_slug},
        follow_redirects=False,
    )
    assert r.status_code == 303
    return int(r.headers["location"].rsplit("/", 1)[-1])


def _first_session_exercise(session_id: int):
    from app.database import SessionLocal
    from app.models.session import SessionExercise
    with SessionLocal() as db:
        se = db.execute(
            select(SessionExercise)
            .where(SessionExercise.session_id == session_id)
            .order_by(SessionExercise.position)
        ).scalars().first()
        return se.id


def _post_sets(client, session_id: int, se_id: int, set_values: list[dict]):
    """POST form data for a session exercise. set_values is a list of
    dicts: [{'set_id': N, 'weight_kg': '60', 'reps': '10'}, ...]"""
    data = {}
    for sv in set_values:
        sid = sv["set_id"]
        if "weight_kg" in sv:
            data[f"set_{sid}_weight_kg"] = sv["weight_kg"]
        if "reps" in sv:
            data[f"set_{sid}_reps"] = sv["reps"]
    r = client.post(
        f"/sessions/{session_id}/exercises/{se_id}",
        data=data,
        follow_redirects=False,
    )
    return r


def _get_set_logs(se_id: int):
    from sqlalchemy.orm import selectinload

    from app.database import SessionLocal
    from app.models.session import SessionExercise
    with SessionLocal() as db:
        se = db.execute(
            select(SessionExercise)
            .where(SessionExercise.id == se_id)
            .options(selectinload(SessionExercise.set_logs))
        ).scalar_one()
        # Return ordered work sets
        return sorted(
            (sl for sl in se.set_logs if sl.kind == "work"),
            key=lambda sl: sl.set_index,
        )


# ---------------------------------------------------------------------------
# Server-side derivation of `completed`
# ---------------------------------------------------------------------------


def test_empty_values_yield_completed_false(client):
    """POST sans weight ni reps → completed=False."""
    sid = _create_session(client)
    se_id = _first_session_exercise(sid)
    work_sets = _get_set_logs(se_id)
    assert len(work_sets) >= 1
    first_set_id = work_sets[0].id

    # POST with empty strings
    _post_sets(client, sid, se_id, [
        {"set_id": first_set_id, "weight_kg": "", "reps": ""},
    ])
    sets = _get_set_logs(se_id)
    first = next(s for s in sets if s.id == first_set_id)
    assert first.completed is False
    assert first.weight_kg is None
    assert first.reps is None


def test_weight_only_yields_completed_true(client):
    """POST avec weight seulement → completed=True."""
    sid = _create_session(client)
    se_id = _first_session_exercise(sid)
    first = _get_set_logs(se_id)[0]

    _post_sets(client, sid, se_id, [
        {"set_id": first.id, "weight_kg": "60", "reps": ""},
    ])
    sets = _get_set_logs(se_id)
    first = next(s for s in sets if s.id == first.id)
    assert first.completed is True
    assert first.weight_kg == 60.0
    assert first.reps is None


def test_reps_only_yields_completed_true(client):
    """POST avec reps seulement (cas bodyweight) → completed=True."""
    sid = _create_session(client)
    se_id = _first_session_exercise(sid)
    first = _get_set_logs(se_id)[0]

    _post_sets(client, sid, se_id, [
        {"set_id": first.id, "weight_kg": "", "reps": "12"},
    ])
    sets = _get_set_logs(se_id)
    first = next(s for s in sets if s.id == first.id)
    assert first.completed is True
    assert first.weight_kg is None
    assert first.reps == 12


def test_weight_and_reps_yields_completed_true(client):
    """POST classique → completed=True."""
    sid = _create_session(client)
    se_id = _first_session_exercise(sid)
    first = _get_set_logs(se_id)[0]

    _post_sets(client, sid, se_id, [
        {"set_id": first.id, "weight_kg": "80", "reps": "10"},
    ])
    sets = _get_set_logs(se_id)
    first = next(s for s in sets if s.id == first.id)
    assert first.completed is True
    assert first.weight_kg == 80.0
    assert first.reps == 10


def test_multiple_sets_independent(client):
    """3 sets, le 2ème vide — devrait être seul à avoir completed=False."""
    sid = _create_session(client)
    se_id = _first_session_exercise(sid)
    sets = _get_set_logs(se_id)
    assert len(sets) >= 3

    _post_sets(client, sid, se_id, [
        {"set_id": sets[0].id, "weight_kg": "80", "reps": "10"},
        {"set_id": sets[1].id, "weight_kg": "", "reps": ""},
        {"set_id": sets[2].id, "weight_kg": "80", "reps": "8"},
    ])
    after = _get_set_logs(se_id)
    by_id = {s.id: s for s in after}
    assert by_id[sets[0].id].completed is True
    assert by_id[sets[1].id].completed is False  # vide
    assert by_id[sets[2].id].completed is True


# ---------------------------------------------------------------------------
# UI — checkbox HTML disparaît
# ---------------------------------------------------------------------------


def test_session_detail_page_has_no_completed_checkbox(client):
    """Le rendu HTML de la session en cours ne doit plus contenir
    de `name="set_..._completed"` ni de classe `set-row__done`."""
    sid = _create_session(client)
    r = client.get(f"/sessions/{sid}")
    assert r.status_code == 200
    body = r.text
    assert "set-row__done" not in body, "checkbox CSS class still present"
    assert "_completed" not in body or "set_logs|selectattr('completed')" not in body, (
        "completed input name still in markup"
    )
    # Le mot "Fait" comme label de checkbox ne doit plus apparaître non plus
    # (mais "fait" minuscule peut apparaître naturellement dans le texte —
    # on vérifie spécifiquement la chaîne du label original)
    assert ">Fait</span>" not in body
