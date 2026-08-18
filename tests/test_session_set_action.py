"""Sb_SESSION_SET_ACTION_01 — l'action de série existe vraiment.

Avant cette tranche, le cockpit paraissait set-by-set alors que la seule
action réelle était exercise-by-exercise : le routeur n'offrait que `prev` et
`next`, qui quittent tous deux l'exercice. Ces tests gardent l'action neuve
ET les comportements qu'elle ne doit pas casser.

Ce qui n'est PAS introduit ici, et que les tests vérifient aussi :
aucune sémantique de complétion nouvelle (`completed` reste dérivé serveur de
la présence de weight/reps), aucune persistance du repos, aucune dépendance
critique au JS.
"""
from __future__ import annotations

import pathlib
import re

CARD = pathlib.Path(__file__).resolve().parent.parent / (
    "app/templates/_partials/exercise_card.html"
)
ROUTER = pathlib.Path(__file__).resolve().parent.parent / "app/routers/sessions.py"


def _start(client, slug: str = "push-a") -> int:
    r = client.post("/sessions", data={"template_slug": slug},
                    follow_redirects=False)
    return int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


def _first_exercise(session_id: int):
    """(session_exercise_id, [work set logs]) du premier exercice."""
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog

    with SessionLocal() as db:
        se = db.execute(
            select(SessionExercise)
            .where(SessionExercise.session_id == session_id)
            .order_by(SessionExercise.position.asc())
            .limit(1)
        ).scalar_one()
        sets = db.execute(
            select(SetLog)
            .where(SetLog.session_exercise_id == se.id)
            .where(SetLog.kind == "work")
            .order_by(SetLog.set_index.asc())
        ).scalars().all()
        return se.id, [(s.id, s.set_index) for s in sets]


def _set_state(set_id: int):
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import SetLog

    with SessionLocal() as db:
        sl = db.execute(select(SetLog).where(SetLog.id == set_id)).scalar_one()
        return sl.weight_kg, sl.reps, sl.completed


# ───────── A1 — l'action existe et sauvegarde réellement ─────────


def test_stay_persists_the_set_values(client):
    sid = _start(client)
    se_id, sets = _first_exercise(sid)
    first_id = sets[0][0]

    r = client.post(
        f"/sessions/{sid}/exercises/{se_id}",
        data={f"set_{first_id}_weight_kg": "60", f"set_{first_id}_reps": "8",
              "nav": "stay"},
        follow_redirects=False,
    )
    assert r.status_code == 303

    weight, reps, completed = _set_state(first_id)
    assert weight == 60.0
    assert reps == 8
    assert completed is True, (
        "completed stays derived from weight/reps presence — no new semantics"
    )


def test_stay_returns_to_the_same_exercise(client):
    sid = _start(client)
    se_id, sets = _first_exercise(sid)
    r = client.post(
        f"/sessions/{sid}/exercises/{se_id}",
        data={f"set_{sets[0][0]}_weight_kg": "60", "nav": "stay"},
        follow_redirects=False,
    )
    loc = r.headers["location"]
    assert f"active={se_id}" in loc, "stay must not leave the active exercise"


# ───────── A4 — retour sur la prochaine série, jamais en haut ─────────


def test_stay_anchors_on_the_next_incomplete_set(client):
    sid = _start(client)
    se_id, sets = _first_exercise(sid)
    first_id, second_id = sets[0][0], sets[1][0]

    r = client.post(
        f"/sessions/{sid}/exercises/{se_id}",
        data={f"set_{first_id}_weight_kg": "60", f"set_{first_id}_reps": "8",
              "nav": "stay"},
        follow_redirects=False,
    )
    assert r.headers["location"].endswith(f"#set-{second_id}"), (
        "after saving set 1 the user must land on set 2, not at the top"
    )


def test_stay_anchors_on_the_card_when_every_work_set_is_done(client):
    sid = _start(client)
    se_id, sets = _first_exercise(sid)
    data = {"nav": "stay"}
    for set_id, _ in sets:
        data[f"set_{set_id}_weight_kg"] = "60"
        data[f"set_{set_id}_reps"] = "8"

    r = client.post(f"/sessions/{sid}/exercises/{se_id}", data=data,
                    follow_redirects=False)
    assert r.headers["location"].endswith(f"#exercise-{se_id}"), (
        "with no set left to fill, the anchor points at the card and its "
        "next-exercise CTA"
    )


def test_the_anchor_target_exists_in_the_rendered_page(client):
    """Une ancre qui ne correspond à aucun `id` ramène en haut de page —
    exactement le défaut que cette tranche doit éviter."""
    sid = _start(client)
    se_id, sets = _first_exercise(sid)
    client.post(
        f"/sessions/{sid}/exercises/{se_id}",
        data={f"set_{sets[0][0]}_weight_kg": "60", "nav": "stay"},
        follow_redirects=False,
    )
    body = client.get(f"/sessions/{sid}").text
    assert f'id="set-{sets[1][0]}"' in body


# ───────── A2 — prev / next intacts ─────────


def test_next_still_advances_to_the_following_exercise(client):
    sid = _start(client)
    se_id, sets = _first_exercise(sid)
    r = client.post(
        f"/sessions/{sid}/exercises/{se_id}",
        data={f"set_{sets[0][0]}_weight_kg": "60", "nav": "next"},
        follow_redirects=False,
    )
    loc = r.headers["location"]
    assert f"active={se_id}" not in loc, "next must leave the current exercise"
    assert "#exercise-" in loc


def test_absent_nav_still_defaults_to_next(client):
    """Le repli historique : un POST sans `nav` avance. Le contrat existant
    ne doit pas dépendre de l'ajout de `stay`."""
    sid = _start(client)
    se_id, sets = _first_exercise(sid)
    r = client.post(
        f"/sessions/{sid}/exercises/{se_id}",
        data={f"set_{sets[0][0]}_weight_kg": "60"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert f"active={se_id}" not in r.headers["location"]


def test_prev_still_goes_back(client):
    sid = _start(client)
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import SessionExercise

    with SessionLocal() as db:
        exercises = db.execute(
            select(SessionExercise)
            .where(SessionExercise.session_id == sid)
            .order_by(SessionExercise.position.asc())
        ).scalars().all()
        first_id, second_id = exercises[0].id, exercises[1].id

    r = client.post(f"/sessions/{sid}/exercises/{second_id}",
                    data={"nav": "prev"}, follow_redirects=False)
    assert f"active={first_id}" in r.headers["location"]


# ───────── A3 — pas de CTA menteur ─────────


def test_the_set_action_button_posts_stay(client):
    """Le libellé « Enregistrer la série » n'est autorisé que parce que la
    valeur `stay` est réellement traitée par le routeur."""
    src = CARD.read_text(encoding="utf-8")
    match = re.search(
        r"<button[^>]*session-focus__set-action[^>]*>.*?</button>",
        src, re.DOTALL,
    )
    assert match, "set-level action button missing"
    block = match.group(0)
    assert 'name="nav"' in block
    assert 'value="stay"' in block

    # D5_SESSION_INSTRUMENT_ROWS_01 — le libellé VISIBLE est passé à
    # « Valider » (compact, aligné sur « Valider · E2 » du bouton voisin), et
    # la phrase entière vit dans le `title`.
    #
    # L'assertion d'origine cherchait « Enregistrer la série » n'importe où
    # dans le bloc. Elle serait restée verte sur le seul `title`, sans plus
    # rien vérifier du libellé rendu : on l'ouvre en deux pour que chaque
    # moitié dise ce qu'elle garde vraiment.
    label = re.sub(r"<[^>]+>", "", block).strip()
    assert label == "Valider", f"unexpected visible label: {label!r}"
    assert "Enregistrer la série et rester sur cet exercice" in block, (
        "the full claim must survive somewhere reachable — here, the title"
    )

    assert 'nav_direction == "stay"' in ROUTER.read_text(encoding="utf-8"), (
        "the button may only claim the action if the router implements it"
    )


def test_the_set_action_only_renders_on_the_current_set(client):
    """Une action de série sur chaque ligne rendrait l'écran ambigu : la
    série courante est la seule à porter l'action."""
    sid = _start(client)
    body = client.get(f"/sessions/{sid}").text
    assert body.count("session-focus__set-action") == 1


# ───────── A6 — repos émis par le serveur, jamais critique ─────────


def test_rest_is_not_started_before_any_set_is_saved(client):
    sid = _start(client)
    body = client.get(f"/sessions/{sid}").text
    assert "session-focus__rest-timer" in body
    assert 'data-rest-started="1"' not in body


def test_rest_starts_only_after_a_saved_set(client):
    sid = _start(client)
    se_id, sets = _first_exercise(sid)
    r = client.post(
        f"/sessions/{sid}/exercises/{se_id}",
        data={f"set_{sets[0][0]}_weight_kg": "60", "nav": "stay"},
        follow_redirects=False,
    )
    assert "rest=1" in r.headers["location"]

    body = client.get(f"/sessions/{sid}?rest=1").text
    assert 'data-rest-started="1"' in body
    assert "Repos en cours" in body


def test_saving_never_depends_on_the_timer(client):
    """Sans JS, le compte à rebours n'existe pas — la sauvegarde doit
    fonctionner quand même. Le POST est un formulaire natif."""
    src = CARD.read_text(encoding="utf-8")
    match = re.search(
        r"<button[^>]*session-focus__set-action[^>]*>.*?</button>",
        src, re.DOTALL,
    )
    block = match.group(0)
    assert 'type="submit"' in block
    for js_only in ("onclick", "data-js-only", "hx-post"):
        assert js_only not in block, (
            "the set action must be a native form submit, never JS-gated"
        )


def test_rest_state_is_not_persisted():
    """Le repos est un signal de rendu, pas une donnée. Une persistance
    durable exigerait une migration → Sb_REST_EVENT_TRACE_01."""
    router = ROUTER.read_text(encoding="utf-8")
    for forbidden in ("rest_started_at", "rest_duration_s", "RestEvent"):
        assert forbidden not in router


# ───────── A7 — noms accessibles ─────────


def test_set_action_has_an_accessible_name(client):
    sid = _start(client)
    body = client.get(f"/sessions/{sid}").text
    match = re.search(
        r"<button[^>]*session-focus__set-action[^>]*>(.*?)</button>",
        body, re.DOTALL,
    )
    assert match, "set action button not rendered"
    assert match.group(1).strip(), "the button must carry visible text"


def test_set_inputs_keep_their_accessible_names(client):
    sid = _start(client)
    body = client.get(f"/sessions/{sid}").text
    assert "Charge en kg — série" in body
    assert "Répétitions — série" in body
