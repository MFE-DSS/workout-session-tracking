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


def _est_au_repos(client, session_id: int, se_id: int) -> bool:
    """L'ÉTAT RENDU, pas un paramètre d'URL.

    `UI-CP8R` — les gardes lisaient `rest=1` dans l'en-tête `Location`,
    c'est-à-dire le signal supposé produire l'état plutôt que l'état. Ce
    signal n'existe plus ; et même du temps où il existait, le lire ne
    prouvait pas que la page rendait un repos.
    """
    body = client.get(f"/sessions/{session_id}?active={se_id}").text
    return "data-rest-remaining=" in body


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
    first_id = sets[0][0]

    r = client.post(
        f"/sessions/{sid}/exercises/{se_id}",
        data={f"set_{first_id}_weight_kg": "60", f"set_{first_id}_reps": "8",
              "nav": "stay"},
        follow_redirects=False,
    )
    # ⚠ `UI-CP2` — LA DESTINATION EST L'ÉTAT DE REPOS, QUI N'A PAS D'ANCRE.
    #
    # `nav=stay` sur une série de TRAVAIL déclenche le repos. A+ ne rend plus
    # la bande de séries à cet état — la question du repos est le temps — donc
    # `#set-<suivante>` ne résoudrait plus, et un fragment qui ne trouve pas sa
    # cible ramène silencieusement en haut de page.
    #
    # L'invariant qui compte — « après avoir enregistré, l'utilisateur arrive
    # là où l'action continue » — est tenu autrement : l'écran de repos tient
    # dans un écran, et la série suivante est nommée par la commande dominante.
    # La garde vérifie donc que la destination est bien l'exercice, à l'état
    # repos.
    lieu = r.headers["location"]
    assert f"active={se_id}" in lieu, f"on quitte l'exercice : {lieu!r}"
    assert "#" not in lieu, (
        f"une ancre morte est posée vers un état qui n'en rend pas : {lieu!r}"
    )
    # ⚠ `UI-CP8R` — ON VÉRIFIE L'ÉTAT ATTEINT, PAS LE PARAMÈTRE QUI LE
    # PRÉTENDAIT. La ligne retirée était `assert "rest=1" in lieu` : elle
    # lisait la CAUSE supposée dans l'en-tête plutôt que l'EFFET dans la
    # page. Le paramètre n'existe plus, et la destination est désormais une
    # URL d'exercice ordinaire — c'est justement la propriété recherchée,
    # puisqu'un rechargement de cette même URL doit rendre le même état.
    assert _est_au_repos(client, sid, se_id), (
        f"l'action de série ne mène pas à l'état de repos : {lieu!r}"
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
    """Une ancre qui ne correspond à aucun `id` ramène en haut de page.

    ⚠ `UI-CP8R` — CETTE GARDE NE VISITAIT PAS LA DESTINATION.

    Elle postait, puis chargeait `/sessions/{sid}` **nu** — en jetant l'URL
    que la redirection venait de produire. Elle vérifiait donc qu'une ancre
    résolvait dans une page où l'utilisateur n'arrivait jamais. Tant que
    l'état de repos dépendait de `?rest=1`, la page nue rendait la bande de
    séries et la garde passait, par accident.

    Elle suit maintenant la redirection réelle, et n'exige la résolution
    d'une ancre que lorsque la redirection en porte une — l'état de repos
    n'en pose délibérément aucune.
    """
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import SetLog

    sid = _start(client)
    se_id, _sets = _first_exercise(sid)
    # ⚠ UN ÉCHAUFFEMENT, PAS `sets[0]`. `_first_exercise` filtre sur
    # `kind == "work"` : valider sa première entrée COMPLÈTE une série de
    # travail, donc déclenche un repos, donc retire la bande de séries —
    # et l'ancre ne résoudrait pas, pour une raison qui n'a rien à voir
    # avec la propriété gardée. C'est exactement l'erreur que la version
    # précédente de ce module faisait ailleurs.
    with SessionLocal() as db:
        warmups = db.execute(
            select(SetLog)
            .where(SetLog.session_exercise_id == se_id, SetLog.kind == "warmup")
            .order_by(SetLog.set_index.asc())
        ).scalars().all()
        warmup_id = warmups[0].id if warmups else None
    assert warmup_id is not None, "labo non représentatif : aucun échauffement"

    # Chemin SANS repos : un échauffement validé ancre sur la série courante.
    r = client.post(
        f"/sessions/{sid}/exercises/{se_id}",
        data={f"set_{warmup_id}_weight_kg": "20",
              f"set_{warmup_id}_reps": "12", "nav": "stay_norest"},
        follow_redirects=False,
    )
    lieu = r.headers["location"]
    assert "#" in lieu, f"ce chemin doit poser une ancre : {lieu!r}"
    chemin, ancre = lieu.split("#", 1)
    body = client.get(chemin).text
    assert f'id="{ancre}"' in body, (
        f"l'ancre {ancre!r} ne résout pas dans {chemin!r} — un fragment "
        "orphelin ramène silencieusement en haut de page"
    )


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
    """Un échauffement validé ne démarre PAS de repos.

    ⚠ `UI-CP8R` — CETTE GARDE MESURAIT LE MAUVAIS OBJET, DEPUIS LE DÉBUT.

    Son titre parle d'échauffement ; son corps postait `sets[0]`, que
    `_first_exercise` filtre sur `kind == "work"`. Elle ne comparait donc
    pas deux KINDS mais deux valeurs du drapeau `nav`, sur la même série de
    travail. La propriété annoncée n'a jamais été vérifiée.

    Elle lisait en plus `rest=1` dans l'en-tête `Location`, c'est-à-dire la
    CAUSE supposée plutôt que l'EFFET. Ce paramètre n'existe plus : le repos
    se dérive de `completed_at`. La garde lit maintenant l'ÉTAT RENDU, et
    sépare vraiment l'échauffement de la série de travail.
    """
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import SetLog

    sid = _start(client)
    se_id, works = _first_exercise(sid)
    with SessionLocal() as db:
        warmups = db.execute(
            select(SetLog)
            .where(SetLog.session_exercise_id == se_id, SetLog.kind == "warmup")
            .order_by(SetLog.set_index.asc())
        ).scalars().all()
        warmup_ids = [w.id for w in warmups]
    assert warmup_ids, "labo non représentatif : cet exercice n'a aucun échauffement"

    # 1 — UN ÉCHAUFFEMENT VALIDÉ NE PRODUIT AUCUN REPOS.
    client.post(
        f"/sessions/{sid}/exercises/{se_id}",
        data={f"set_{warmup_ids[0]}_weight_kg": "20",
              f"set_{warmup_ids[0]}_reps": "12", "nav": "stay_norest"},
        follow_redirects=False,
    )
    assert not _est_au_repos(client, sid, se_id), (
        "un échauffement n'est pas une série exécutée : aucun repos ne lui "
        "appartient, et la dérivation ne regarde que le travail"
    )

    # 2 — UNE SÉRIE DE TRAVAIL VALIDÉE EN PRODUIT UN.
    client.post(
        f"/sessions/{sid}/exercises/{se_id}",
        data={f"set_{works[0][0]}_weight_kg": "60",
              f"set_{works[0][0]}_reps": "8", "nav": "stay"},
        follow_redirects=False,
    )
    assert _est_au_repos(client, sid, se_id)


def test_une_correction_ne_relance_aucun_repos(client):
    """`UI-CP8R §11` — corriger une vieille série ne ressuscite pas un repos.

    C'est la garde du seul autre chemin réel qui poste `stay_norest`. Elle
    tient **par construction** et non par une branche spéciale : une
    transition COMPLÈTE → COMPLÈTE préserve `completed_at`, donc le temps
    écoulé reste celui de l'exécution d'origine.

    On place l'exécution d'origine hors de la fenêtre de repos, puis on
    corrige. Sans la préservation, la correction poserait un horodatage
    neuf et l'utilisateur qui rectifie une faute de frappe se verrait
    imposer 90 secondes.
    """
    from datetime import UTC, datetime, timedelta

    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import SetLog

    sid = _start(client)
    se_id, works = _first_exercise(sid)
    first_id = works[0][0]

    client.post(
        f"/sessions/{sid}/exercises/{se_id}",
        data={f"set_{first_id}_weight_kg": "60", f"set_{first_id}_reps": "8",
              "nav": "stay"},
        follow_redirects=False,
    )
    assert _est_au_repos(client, sid, se_id), "labo non représentatif"

    # Le repos de cette série est écoulé depuis longtemps.
    ancien = datetime.now(UTC) - timedelta(minutes=30)
    with SessionLocal() as db:
        sl = db.execute(select(SetLog).where(SetLog.id == first_id)).scalar_one()
        sl.completed_at = ancien
        db.commit()
    assert not _est_au_repos(client, sid, se_id)

    # Correction : même série, nouvelle valeur, `stay_norest`.
    client.post(
        f"/sessions/{sid}/exercises/{se_id}",
        data={f"set_{first_id}_weight_kg": "62.5", f"set_{first_id}_reps": "8",
              "nav": "stay_norest"},
        follow_redirects=False,
    )
    with SessionLocal() as db:
        sl = db.execute(select(SetLog).where(SetLog.id == first_id)).scalar_one()
        assert sl.weight_kg == 62.5, "la correction doit bien être enregistrée"
        garde = sl.completed_at
    assert garde is not None
    assert abs((garde.replace(tzinfo=UTC) - ancien).total_seconds()) < 2, (
        "`completed_at` a été réécrit par une correction"
    )
    assert not _est_au_repos(client, sid, se_id)


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
    """Ni durée, ni objet « repos » : on ne persiste que des FAITS.

    ⚠ `UI-CP8R` — CETTE GARDE ÉTAIT VERTE ET SA PROSE ÉTAIT FAUSSE.

    Elle disait « le repos est un signal de rendu, pas une donnée ; une
    persistance durable exigerait une migration → `Sb_REST_EVENT_TRACE_01` ».
    Cette migration est faite. Laissée telle quelle, la garde aurait continué
    de passer en affirmant le contraire du produit — et aurait laissé croire
    qu'elle protégeait encore quelque chose.

    Les trois noms interdits le RESTENT, et pour des raisons intactes :

    * `rest_started_at` — ce serait une SECONDE source pour l'instant de
      départ, à côté de `completed_at`, avec la divergence garantie qui va
      avec. La série complétée EST le départ du repos ;
    * `rest_duration_s` — persister la durée ferait de 90 s une
      **prescription** du produit alors que c'est une suggestion
      (`Sx_UIV3_04 §1bis C`), et l'ajustement `±15 s` deviendrait une donnée ;
    * `RestEvent` — un objet « repos » serait un état stocké, donc
      désynchronisable. L'état reste DÉRIVÉ.

    Ce qui est persisté, et seulement cela : QUAND une série a été faite, et
    SI l'utilisateur a décidé de dépasser ce repos-là.
    """
    router = ROUTER.read_text(encoding="utf-8")
    code = "\n".join(
        ligne for ligne in router.splitlines()
        if not ligne.lstrip().startswith("#")
    )
    for forbidden in ("rest_started_at", "rest_duration_s", "RestEvent"):
        assert forbidden not in code

    from app.models.session import SetLog

    colonnes = set(SetLog.__table__.columns.keys())
    for interdite in ("rest_seconds", "rest_duration", "rest_until",
                      "rest_started_at", "resting", "rest_state"):
        assert interdite not in colonnes, (
            f"`{interdite}` ferait du repos un état ou une consigne stockée"
        )
    assert {"completed_at", "rest_dismissed_at"} <= colonnes


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
    # ⚠ `R5`/`R6` — la garde cherchait « VALIDER ». Depuis que la saisie valide
    # d'elle-même, ce mot est proscrit (`test_no_dominant_command_still_says_valider`).
    # Ce qui est gardé ici reste l'invariant d'origine, et il ne périme pas :
    # la commande porte un NOM lisible, pas seulement une couleur ou un glyphe.
    label = re.sub(r"<[^>]+>", " ", match.group(1))
    label = " ".join(label.split())
    assert len(label) >= 6, f"commande sans libellé lisible : {label!r}"
    assert re.search(r"[A-ZÀ-Ÿ]{3}", label), (
        f"commande sans nom en capitales : {label!r}"
    )


def test_set_inputs_keep_their_accessible_names(client):
    """TOUT champ de série rendu nomme son type et son rang.

    ⚠ `DF-E` — cette garde cherchait « Charge en kg — série » sur une séance
    NEUVE, dont l'exercice actif n'a qu'un ÉCHAUFFEMENT en cours. Elle
    passait donc grâce aux listes plates des AUTRES cartes : la seconde
    interface que `DF-E` a supprimée. Elle mesurait l'ancien écran en croyant
    mesurer le nouveau.

    La propriété réelle ne dépend d'aucun état particulier : aucun champ de
    série ne doit être rendu sans nom accessible. On la vérifie sur ce qui
    est effectivement rendu, puis on force un état où une SÉRIE DE TRAVAIL
    est courante pour couvrir aussi ce libellé-là.
    """
    sid = _start(client)

    def _labels(body: str) -> list[str]:
        fields = re.findall(
            r'<input[^>]*name="set_\d+_(?:weight_kg|reps)"[^>]*>', body)
        visible = [f for f in fields if 'type="hidden"' not in f]
        assert visible, "aucun champ de série rendu — la garde ne mesure rien"
        out = []
        for f in visible:
            m = re.search(r'aria-label="([^"]+)"', f)
            assert m, f"champ de série sans nom accessible : {f[:110]!r}"
            out.append(m.group(1))
        return out

    seen = _labels(client.get(f"/sessions/{sid}").text)
    assert any("échauffement" in x for x in seen), seen

    # Amener une série de TRAVAIL à l'état courant, par la vraie soumission —
    # cumulative, sinon chaque envoi effacerait les séries précédentes.
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import SetLog

    se_id, _works = _first_exercise(sid)
    with SessionLocal() as db:
        warm = db.execute(
            select(SetLog)
            .where(SetLog.session_exercise_id == se_id, SetLog.kind != "work")
            .order_by(SetLog.set_index.asc())
        ).scalars().all()
        ordered = [s.id for s in warm]

    # ⚠ `UI-CP8R` — ON NE REMPLIT PLUS LA PREMIÈRE SÉRIE DE TRAVAIL ICI.
    #
    # La version précédente postait les échauffements ET la première série
    # de travail sous `nav=stay_norest`, puis exigeait que les champs de
    # cette série soient encore VISIBLES. Aucun écran du produit ne produit
    # cette combinaison : `stay_norest` n'est émis que par la validation
    # d'échauffement et par la correction — et la correction ne porte que
    # sur une série DÉJÀ complétée (`_resolve_correction` exige
    # `sl.completed`).
    #
    # Le drapeau `nav` ne suffit plus à empêcher un repos : c'est le FAIT
    # d'avoir complété une série de travail qui le déclenche. Remplir la
    # série puis exiger de la voir saisissable demandait au produit d'être
    # dans deux états à la fois.
    #
    # Le chemin RÉEL donne le même écran : valider les échauffements amène
    # la première série de travail à l'état courant, champs visibles. La
    # propriété gardée — tout champ de série rendu nomme son type et son
    # rang — ne bouge pas.
    assert ordered, "labo non représentatif : aucun échauffement à valider"
    data: dict[str, str] = {"nav": "stay_norest"}
    for set_id in ordered:
        data[f"set_{set_id}_weight_kg"] = "40"
        data[f"set_{set_id}_reps"] = "10"
        client.post(f"/sessions/{sid}/exercises/{se_id}", data=dict(data),
                    follow_redirects=False)

    seen = _labels(client.get(f"/sessions/{sid}").text)
    assert any("série" in x for x in seen), seen
