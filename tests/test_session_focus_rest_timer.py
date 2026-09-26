"""Sb_29.4 — Rest timer progressive enhancement tests.

Verifies:
* `app/templates/_partials/rest_timer.html` exists.
* No-JS fallback markup "Repos suggéré" is rendered on the session page.
* `data-start-rest` and `data-rest-duration` attributes are present
  on the active card rest timer wrapper.
* `app/static/js/session_focus.js` exists and is vanilla JS (no React,
  no Vue, no Angular, no import / require).
* `session_focus.js` contains cleanup logic (clearInterval).
* `session_detail.html` loads `session_focus.js`.
* No critical action depends on JS (POST forms still standalone).
* Sticky CTA from Sb_29.3 still present (no regression).
* Update_exercise_card form action preserved.
* Owner isolation preserved (Sb_26.7).
* No new JS file other than preview.js + session_focus.js.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARTIAL_REST = ROOT / "app" / "templates" / "_partials" / "rest_timer.html"
PARTIAL_CARD = ROOT / "app" / "templates" / "_partials" / "exercise_card.html"
SESSION_DETAIL = ROOT / "app" / "templates" / "session_detail.html"
JS_FILE = ROOT / "app" / "static" / "js" / "session_focus.js"
APP_CSS = ROOT / "app" / "static" / "css" / "app.css"
FOCUS_CSS = ROOT / "app" / "static" / "css" / "session_focus.css"


# ───────── seed helpers ─────────


def _seed_in_progress(db, user_id, n_exercises=2):
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    s = WorkoutSession(
        user_id=user_id,
        template_slug_snapshot="rest-timer",
        template_name_snapshot="Rest timer test",
        started_at=datetime.now(UTC),
        status="in_progress",
    )
    for i in range(n_exercises):
        se = SessionExercise(
            exercise_code_snapshot=f"R{i + 1}",
            exercise_name_snapshot=f"Exercise {i + 1}",
            position=i + 1,
        )
        se.set_logs.append(
            SetLog(kind="work", set_index=1, weight_kg=80.0, reps=8, completed=False)
        )
        s.session_exercises.append(se)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def _seed_resting(db, user_id, n_exercises=2, il_y_a_secondes=0):
    """Une séance RÉELLEMENT au repos — par les faits, pas par l'URL.

    ⚠ `UI-CP8R` — CE QUI A CHANGÉ DANS CE FICHIER, ET POURQUOI.

    Chaque garde de ce module atteignait l'état `REST` en accolant `?rest=1`
    à l'URL. Ce paramètre n'existe plus : c'était précisément le défaut que
    la tranche corrige — un booléen de requête ne peut pas dire depuis
    QUAND, donc le décompte repartait de 1:30 à chaque rechargement.

    **Les propriétés vérifiées ici n'ont pas bougé d'un iota** — le minuteur
    existe à l'état repos, seulement sur la carte active, avec un repli
    lisible sans JS et des contrôles non critiques. Seul le MOYEN d'atteindre
    l'état change : on sème une série de travail complétée avec son heure,
    et le serveur dérive le repos comme il le fera en production.

    C'est d'ailleurs plus fidèle : l'ancien montage pouvait rendre `REST`
    sur une séance où aucune série n'avait jamais été faite.
    """
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    quand = datetime.now(UTC) - timedelta(seconds=il_y_a_secondes)
    s = WorkoutSession(
        user_id=user_id,
        template_slug_snapshot="rest-timer",
        template_name_snapshot="Rest timer test",
        started_at=datetime.now(UTC),
        status="in_progress",
    )
    for i in range(n_exercises):
        se = SessionExercise(
            exercise_code_snapshot=f"R{i + 1}",
            exercise_name_snapshot=f"Exercise {i + 1}",
            position=i + 1,
        )
        # S1 faite, à l'instant → repos. S2 en attente → il reste du travail.
        se.set_logs.append(SetLog(
            kind="work", set_index=1, weight_kg=80.0, reps=8,
            completed=True, completed_at=quand,
        ))
        se.set_logs.append(SetLog(
            kind="work", set_index=2, weight_kg=None, reps=None, completed=False,
        ))
        s.session_exercises.append(se)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def _premier_exercice_id(db, session_id) -> int:
    from app.models.session import SessionExercise

    return db.query(SessionExercise).filter_by(
        session_id=session_id, position=1).one().id


def _render(client, session_id, query: str = "") -> str:
    """`query` cible la carte ACTIVE — la seule où un repos est dérivé."""
    r = client.get(f"/sessions/{session_id}{query}", follow_redirects=False)
    assert r.status_code == 200, r.text[:400]
    return r.text


# ───────── partial / files exist ─────────


def test_rest_timer_partial_exists():
    assert PARTIAL_REST.exists(), "rest_timer.html partial missing"
    body = PARTIAL_REST.read_text(encoding="utf-8")
    assert "session-focus__rest-timer" in body
    # ⚠ LA PROSE N'EST PAS DU BALISAGE. Ce fichier EXPLIQUE, dans un
    # commentaire Jinja, quels attributs ont été retirés et pourquoi — il
    # les NOMME donc. Une recherche de sous-chaîne sur le fichier entier
    # trouverait `data-rest-duration` dans une phrase qui dit précisément
    # qu'il n'est plus émis, et conclurait l'inverse de la vérité.
    # Le dépôt a déjà payé cette erreur (`_sans_commentaires_python`).
    balisage = re.sub(r"\{#.*?#\}", "", body, flags=re.DOTALL)
    # `UI-CP8R` — un SEUL attribut porte désormais le repos, et il porte le
    # RESTANT dérivé du serveur, pas la durée nominale. `data-start-rest`
    # avait déjà disparu ; `data-rest-duration` le suit pour la même raison
    # de fond : une durée pleine ne dit pas depuis quand on se repose.
    assert "data-rest-remaining" in balisage
    assert "data-start-rest" not in balisage
    assert "data-rest-duration" not in balisage
    # ⚠ « Repos suggéré » N'EST PAS RETIRÉ : IL ÉTAIT DÉJÀ MORT.
    # Le libellé vivait dans un `{% else %}` dont la condition était
    # `rest_active`, tandis que le partiel n'est inclus que si
    # `cs.is_resting` — deux lectures de la même source. La branche n'était
    # donc jamais atteinte. Cette garde l'épinglait comme si elle l'était :
    # elle lisait le FICHIER, jamais un rendu. Elle lit maintenant le
    # libellé réellement servi.
    assert "Repos en cours" in body


def test_session_focus_js_exists():
    assert JS_FILE.exists(), "session_focus.js missing"


# ───────── no-JS markup rendered ─────────


def test_no_js_fallback_text_present(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        repos = _seed_resting(db, user.id)
        actif = _premier_exercice_id(db, repos.id)
        session = _seed_in_progress(db, user.id)
        session_id, repos_id = session.id, repos.id

    body = _render(client, session_id)
    # Le repli statique existe dans l'état `REST` seul. Hors repos, il n'y a
    # pas de repos à annoncer : le rendre en permanence est ce qui a masqué
    # le défaut `D3`.
    rest_body = _render(client, repos_id, query=f"?active={actif}")
    assert "Repos" in rest_body
    assert "Repos" not in body


def test_le_restant_derive_est_rendu_et_non_la_duree_nominale(client):
    """`UI-CP8R` — l'attribut porte le RESTANT du serveur.

    Cette garde s'appelait `test_data_start_rest_attr_present` et n'exigeait
    que la PRÉSENCE d'un drapeau. Un drapeau présent était compatible avec
    le défaut : le décompte repartait de 90 s à chaque rendu et la garde
    restait verte. Elle vérifie maintenant la VALEUR, et qu'elle décroît.
    """
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_resting(db, user.id, il_y_a_secondes=30)
        actif = _premier_exercice_id(db, session.id)
        session_id = session.id

    body = _render(client, session_id, query=f"?active={actif}")
    assert "data-start-rest=" not in body
    assert 'data-rest-started="1"' not in body
    restant = re.search(r'data-rest-remaining="(\d+)"', body)
    assert restant is not None, "le restant dérivé n'est pas rendu"
    # 90 − 30 = 60, à la seconde de latence près. Surtout : PAS 90.
    assert 55 <= int(restant.group(1)) <= 60, restant.group(1)


def test_rest_timer_only_on_active_card(client):
    """Rest timer is included only inside the active card."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_resting(db, user.id, n_exercises=3)
        actif = _premier_exercice_id(db, session.id)
        ordinaire = _seed_in_progress(db, user.id)
        session_id, ordinaire_id = session.id, ordinaire.id

    body = _render(client, session_id, query=f"?active={actif}")
    # ⚠ ON COMPTE DES MINUTEURS, PAS DES SOUS-CHAÎNES. `rest-readout`
    # apparaît CINQ fois pour un seul minuteur (le conteneur, le libellé, la
    # valeur, et les deux pas de ±15 s) : le compter rendait `5` là où il y
    # a `1`. L'attribut de racine, lui, est unique par minuteur.
    occurrences = body.count("data-rest-remaining=")
    assert occurrences == 1, (
        "le minuteur doit exister à l'état repos, et une seule fois — les "
        "deux autres cartes ont pourtant le MÊME fait durable, et ne "
        "doivent rien dériver puisqu'elles ne sont pas actives"
    )
    plain = _render(client, ordinaire_id)
    assert "rest-readout" not in plain, (
        "et nulle part ailleurs — c'est l'objet de la correction D3"
    )


# ───────── JS contract ─────────


def test_session_focus_js_is_vanilla():
    src = JS_FILE.read_text(encoding="utf-8")
    forbidden = (
        "import ",
        "require(",
        "from 'react'",
        'from "react"',
        "ReactDOM",
        "Vue.",
        "angular",
        "@angular",
        "esm.sh",
        "unpkg.com",
    )
    low = src
    for token in forbidden:
        assert token not in low, f"forbidden token in session_focus.js: {token!r}"


def test_session_focus_js_has_cleanup():
    src = JS_FILE.read_text(encoding="utf-8")
    assert "clearInterval" in src, (
        "session_focus.js must include cleanup via clearInterval"
    )


def test_session_focus_js_reads_data_attributes():
    src = JS_FILE.read_text(encoding="utf-8")
    # `UI-CP8R` — l'attribut lu est le RESTANT dérivé par le serveur.
    assert 'getAttribute("data-rest-remaining")' in src


def test_session_focus_js_default_90s():
    src = JS_FILE.read_text(encoding="utf-8")
    assert "90" in src, "default 90s fallback not found in session_focus.js"


def test_session_focus_js_handles_empty_dom():
    """The init function must not throw when no [data-start-rest] is in DOM.

    We assert structural guard: a length-or-existence check before iteration.
    """
    src = JS_FILE.read_text(encoding="utf-8")
    # Either an explicit length === 0 / length == 0 / !length guard.
    pattern = re.compile(r"length\s*(===?|<=|<)\s*0|!\s*\w+\.length")
    assert pattern.search(src), (
        "session_focus.js should short-circuit when no rest timer roots present"
    )


# ───────── script loaded on session detail ─────────


def test_session_detail_loads_session_focus_js():
    src = SESSION_DETAIL.read_text(encoding="utf-8")
    assert "session_focus.js" in src
    assert "<script" in src


def test_session_focus_js_loaded_in_rendered_page(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_in_progress(db, user.id)
        session_id = session.id

    body = _render(client, session_id)
    assert "js/session_focus.js" in body


# ───────── no critical action depends on JS ─────────


def test_skip_button_is_type_button(client):
    """Skip rest must be type=button so it never submits a form."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_resting(db, user.id)
        actif = _premier_exercice_id(db, session.id)
        session_id = session.id

    # ⚠ `UI-CP8R` — CETTE GARDE COMPTE PLUS QU'AVANT, PAS MOINS.
    #
    # « Skip rest » (anglais, `type="button"`, sans effet serveur) était
    # devenu `PASSER LE REPOS`, un LIEN. C'est maintenant un BOUTON DE
    # SOUMISSION, parce que passer le repos écrit un fait durable.
    #
    # Un `<button>` sans `type` explicite vaut `type="submit"`. Les ±15 s
    # vivent dans le MÊME formulaire : si l'un d'eux perdait son
    # `type="button"`, ajuster l'affichage de 15 secondes soumettrait le
    # formulaire — et, avec la déviation `formaction` absente, écrirait les
    # valeurs de série. La garde tient précisément cette porte.
    body = _render(client, session_id, query=f"?active={actif}")
    assert "PASSER LE REPOS" in body
    pattern = re.compile(r'<button\b[^>]*data-rest-step[^>]*>', re.IGNORECASE)
    m = pattern.search(body)
    assert m is not None, "les ajustements ±15 s ne sont pas rendus"
    assert 'type="button"' in m.group(0)


def test_rest_timer_is_outside_post_form(client):
    """Rest timer must NOT live inside the <form action=update_exercise_card>.
    This guarantees that submitting the form does not submit any timer state
    and the no-JS fallback POST is unchanged.
    """
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_in_progress(db, user.id)
        session_id = session.id

    body = _render(client, session_id)
    pattern = re.compile(
        r'<form\b[^>]*action="[^"]*/sessions/\d+/exercises/\d+"[^>]*>'
        r"(.*?)</form>",
        re.DOTALL,
    )
    forms = pattern.findall(body)
    assert forms, "no per-exercise update form found"
    for f in forms:
        assert "session-focus__rest-timer" not in f, (
            "rest timer must NOT live inside the update_exercise_card form"
        )


# ───────── no regression Sb_29.3 sticky CTA ─────────


def test_sticky_cta_still_present(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_in_progress(db, user.id)
        session_id = session.id

    # MIGRÉ — plus AUCUNE barre collante (`Sx_UIV3_02 §7.9` + Q1). Elle
    # produisait un recouvrement mesuré et n'existait que parce que la
    # commande était loin. Ce qui la remplace est vérifié ici.
    body = _render(client, session_id)
    assert "session-focus__sticky-cta" not in body
    assert "dock__cmd" in body


def test_update_exercise_card_form_action_preserved(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_in_progress(db, user.id)
        session_id = session.id

    body = _render(client, session_id)
    assert f"/sessions/{session_id}/exercises/" in body


# ───────── CSS contract ─────────


def test_css_has_rest_timer_block():
    css = APP_CSS.read_text(encoding="utf-8") + "\n" + FOCUS_CSS.read_text(encoding="utf-8")
    assert ".session-focus__rest-timer" in css
    assert ".session-focus__rest-timer__countdown" in css


# ───────── no new JS file beyond preview + session_focus ─────────


def test_no_unexpected_js_file_introduced():
    # Sb_UI_JS_CAPACITY_GUARD_01 — l'inventaire devient une PROPRIÉTÉ.
    #
    # Le nom de cette garde ne contenait pas `no_new_js` : un relevé par nom
    # l'a manquée, et deux autres avec elle. C'est un balayage par CLASSE
    # — toute fonction qui compare la liste du répertoire à une constante —
    # qui l'a trouvée. La famille comptait SEIZE membres, pas quatorze.
    #
    # `AUREN_VISUAL_BACKBONE §5bis` : ce que le produit garde n'est pas un
    # NOMBRE de fichiers mais une PROPRIÉTÉ.
    from tests.helpers import assert_aucune_ecriture_parallele

    assert_aucune_ecriture_parallele()


def test_no_react_or_bundle_in_page(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        session = _seed_in_progress(db, user.id)
        session_id = session.id

    body = _render(client, session_id).lower()
    for forbidden in (
        "react-dom",
        "vue.js",
        "/main.bundle.js",
        "esm.sh",
        "unpkg.com",
    ):
        assert forbidden not in body, f"forbidden token: {forbidden}"


# ───────── owner isolation preserved ─────────


def test_owner_isolation_unaffected(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.auth import hash_password

    with SessionLocal() as db:
        owner = db.query(User).first()
        session = _seed_in_progress(db, owner.id)
        session_id = session.id
        other = User(
            username="rest_other",
            password_hash=hash_password("rest_other_str_xyz"),  # noqa: S106
        )
        db.add(other)
        db.commit()

    client.cookies.clear()
    r = client.post(
        "/login",
        data={"username": "rest_other", "password": "rest_other_str_xyz"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    r = client.get(f"/sessions/{session_id}", follow_redirects=False)
    assert r.status_code == 404
