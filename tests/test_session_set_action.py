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


def test_the_dominant_command_posts_stay_on_a_work_set(client):
    """**Migré T5 → T3** par `UIV3_SESSION_EXECUTION_CONSOLE_01`.

    La garde d'origine cherchait `session-focus__set-action`, le bouton
    secondaire « Enregistrer la série » qui COEXISTAIT en permanence avec
    « Enregistrer et passer à E2 ». Mesuré à 390 px, cette coexistence ne
    tenait pas dans la largeur d'un téléphone : l'étiquette de la seconde
    demandait ~180 px dans un bouton de 62 et se peignait par-dessus la
    première (`Sx_UIV3_02B §D2`).

    L'invariant, lui, ne périme pas : **un libellé ne peut revendiquer une
    action que si le routeur la traite**. Il est ici reporté sur la commande
    dominante de l'état `CURRENT SET`.
    """
    from app.services.console_state import (
        CURRENT_SET,
        build_console_state,  # noqa: PLC0415
        command_for,
    )
    from tests.test_uiv3_session_console import _exercise  # noqa: PLC0415

    st = build_console_state(_exercise(warmups_done=1), next_code="E2")
    assert st.state == CURRENT_SET
    assert command_for(st)["nav"] == "stay"

    router = ROUTER.read_text(encoding="utf-8")
    assert '"stay"' in router, (
        "the command may only claim the action if the router implements it"
    )
    assert "stay_redirect_target" in router


def test_exactly_one_dominant_command_is_rendered(client):
    """**Migré T5 → T3.** La garde comptait une occurrence de l'action de
    série ; elle compte désormais la commande dominante. Le principe est
    inchangé et durci : deux commandes concurrentes sur un écran rendaient
    l'action ambiguë — c'est le défaut que la tranche supprime."""
    sid = _start(client)
    body = client.get(f"/sessions/{sid}").text
    assert body.count('class="dock__cmd"') == 1, body.count('class="dock__cmd"')


# ───────── A6 — repos émis par le serveur, jamais critique ─────────


def test_rest_is_not_started_before_any_set_is_saved(client):
    """**Durci par `UIV3_SESSION_EXECUTION_CONSOLE_01`.**

    La garde d'origine vérifiait que le minuteur était PRÉSENT et non
    démarré. C'est exactement l'angle mort qui a laissé passer `D3` : le
    bloc était bien là, l'attribut `data-rest-started` bien absent, et le JS
    démarrait quand même le décompte parce qu'il lisait un AUTRE attribut,
    rendu inconditionnellement. Mesuré au navigateur : `running=True, 89s`
    sans qu'aucune série n'ait été saisie.

    Le minuteur n'existe désormais **que** dans l'état `REST`. La garde
    vérifie donc son absence, ce qu'aucune lecture d'attribut ne peut
    contredire.
    """
    sid = _start(client)
    body = client.get(f"/sessions/{sid}").text
    assert "rest-readout" not in body
    assert 'data-rest-started="1"' not in body


def test_rest_starts_only_after_a_saved_work_set(client):
    """Un échauffement validé ne démarre PAS de repos — mesuré au
    navigateur, `nav=stay` sur le dernier échauffement faisait partir le
    décompte avant la première série de travail."""
    sid = _start(client)
    se_id, sets = _first_exercise(sid)
    r = client.post(
        f"/sessions/{sid}/exercises/{se_id}",
        data={f"set_{sets[0][0]}_weight_kg": "60", "nav": "stay"},
        follow_redirects=False,
    )
    assert "rest=1" in r.headers["location"]

    warm = client.post(
        f"/sessions/{sid}/exercises/{se_id}",
        data={f"set_{sets[0][0]}_weight_kg": "60", "nav": "stay_norest"},
        follow_redirects=False,
    )
    assert "rest=1" not in warm.headers["location"]


def test_saving_never_depends_on_the_timer(client):
    """Sans JS, le compte à rebours n'existe pas — la sauvegarde doit
    fonctionner quand même. La commande dominante est une soumission de
    formulaire native."""
    # ⚠ `DF-B` — l'expression exigeait `class="dock__cmd">`, donc la classe
    # SUIVIE IMMÉDIATEMENT du chevron. Ajouter un attribut après elle
    # (`data-dominant-submit`, l'ancrage de l'auto-validation) faisait échouer
    # la garde sans que la propriété testée change d'un iota. On vérifie
    # désormais ce qui compte : c'est bien un `<button type="submit">` portant
    # `name="nav"` et la classe de la commande dominante.
    src = CARD.read_text(encoding="utf-8")
    match = re.search(
        r'<button type="submit" name="nav"[^>]*class="dock__cmd"[^>]*>',
        src, re.DOTALL,
    )
    assert match, "dominant command is no longer a native submit"
    for js_only in ("onclick", "data-js-only", "hx-post"):
        assert js_only not in src, (
            "the command must be a native form submit, never JS-gated"
        )


def test_rest_state_is_not_persisted():
    """Le repos est un signal de rendu, pas une donnée. Une persistance
    durable exigerait une migration → Sb_REST_EVENT_TRACE_01."""
    router = ROUTER.read_text(encoding="utf-8")
    for forbidden in ("rest_started_at", "rest_duration_s", "RestEvent"):
        assert forbidden not in router


# ───────── A7 — noms accessibles ─────────


def test_the_dominant_command_has_an_accessible_name(client):
    """**Migré T5 → T2.** Le changement d'état est annoncé par le LIBELLÉ de
    la commande, pas seulement par la couleur (`Sx_UIV3_02 §7.11`)."""
    sid = _start(client)
    body = client.get(f"/sessions/{sid}").text
    # ⚠ Même fragilité que ci-dessus : la classe peut être suivie d'autres
    # attributs. Ce qui est gardé, c'est que la commande dominante EXISTE et
    # porte un libellé — pas l'ordre de ses attributs.
    match = re.search(
        r'<button[^>]*class="dock__cmd"[^>]*>(.*?)</button>', body, re.DOTALL,
    )
    assert match, "dominant command not rendered"
    assert "VALIDER" in match.group(1), match.group(1)


def test_set_inputs_keep_their_accessible_names(client):
    sid = _start(client)
    body = client.get(f"/sessions/{sid}").text
    assert "Charge en kg — série" in body
    assert "Répétitions — série" in body
