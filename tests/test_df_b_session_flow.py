"""`DF-B` — la console de séance a un bouton de trop.

CE QUE CETTE TRANCHE FERME
---------------------------
Le dogfood réel a montré un flux en trois gestes là où l'intention en compte
un : saisir la charge et les répétitions, **puis** taper `VALIDER Sx`,
**puis** taper `PASSER LE REPOS`.

Or le domaine dit déjà que la donnée remplie EST la preuve du set —
`completed` se dérive de `weight OR reps`, et la case « Fait » a été retirée
pour cette raison. L'interface refusait encore de l'admettre.

Le nouveau contrat :

    SAISIR → VALIDATION IMPLICITE → REPOS → PROCHAINE SÉRIE

  * **saisir est valider** — sur une transition EXPLICITE (`Entrée`/`Done`),
    jamais sur la frappe ni sur le `blur` ;
  * **le repos est un état, pas une porte** — toucher la ligne de la prochaine
    série reprend, et le minuteur sort tout seul à zéro ;
  * **le serveur reste l'autorité** — c'est le POST existant qui écrit.

CE QUE CES GARDES FERMENT
--------------------------
  1. UN ENDPOINT PARALLÈLE APPARAÎT — un `fetch` qui n'enverrait qu'une série
     effacerait les autres, puisque le formulaire sérialise tout.
  2. L'AUTO-VALIDATION SE DÉCLENCHE À LA FRAPPE OU AU `BLUR` — enregistrer
     parce que le clavier s'est fermé surprendrait, et la note l'interdit.
  3. LA CORRECTION EST AUTO-VALIDÉE — rectifier reste un geste délibéré.
  4. LE REPOS REDEVIENT UNE PORTE — plus de sortie sans un tap dédié.
  5. LE MINUTEUR REDEVIENT UN DÉCRÉMENT — un rappel manqué deviendrait une
     seconde de repos inventée, et la dérive s'accumule.
  6. LE REPLI SANS JS DISPARAÎT.
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
JS = ROOT / "app/static/js/session_focus.js"
CARD = ROOT / "app/templates/_partials/exercise_card.html"
REST_TPL = ROOT / "app/templates/_partials/rest_timer.html"
CSS = ROOT / "app/static/css/app.css"

#: Marqueur de l'affordance de reprise. `python:S1192` mord à trois
#: occurrences, et ce littéral en compte autant.
RESUME_MARKER = "data-rest-resume"


def _js() -> str:
    """Le script SANS ses commentaires — une garde qui lit sa propre prose ne
    garde rien, et ce dépôt s'y est fait prendre plusieurs fois."""
    src = JS.read_text(encoding="utf-8")
    src = re.sub(r"/\*[\s\S]*?\*/", " ", src)
    return "\n".join(ln.split("//", 1)[0] for ln in src.splitlines())


def _card() -> str:
    return re.sub(r"\{#.*?#\}", " ", CARD.read_text(encoding="utf-8"), flags=re.S)


# ═════════ 1. LE SERVEUR RESTE L'AUTORITÉ DE PERSISTANCE ═════════


def test_no_parallel_save_endpoint_is_introduced():
    """LA GARDE LA PLUS IMPORTANTE. Le formulaire sérialise TOUTES les valeurs
    de la carte : un mini-POST qui n'enverrait que la série courante effacerait
    les autres — le gabarit le documente lui-même."""
    js = _js()
    for banned in ("fetch(", "XMLHttpRequest", "navigator.sendBeacon",
                   "FormData(", "axios"):
        assert banned not in js, f"chemin de sauvegarde parallèle : {banned}"


def test_the_commit_reuses_the_existing_form_submission():
    js = _js()
    assert "requestSubmit(" in js, (
        "l'auto-validation n'emploie pas la soumission existante"
    )
    assert "data-session-form" in js
    assert "data-dominant-submit" in js


def test_the_submitter_is_explicit_so_nav_is_sent():
    """`requestSubmit()` SANS soumetteur n'envoie pas `nav` — le serveur ne
    saurait alors pas s'il doit enchaîner sur un repos."""
    js = _js()
    m = re.search(r"requestSubmit\(\s*([A-Za-z_$][\w$]*)\s*\)", js)
    assert m, "aucun appel `requestSubmit(<soumetteur>)`"
    assert m.group(1) != "", "soumetteur vide"


def test_the_dominant_button_still_exists_for_no_js():
    """Sans JS, la validation reste ce qu'elle a toujours été : un bouton."""
    card = _card()
    assert 'type="submit" name="nav"' in card
    assert "data-dominant-submit" in card


# ═════════ 2. AUCUNE VALIDATION À LA FRAPPE NI AU BLUR ═════════


def test_the_commit_never_listens_to_typing_or_blur():
    """LA CONTRAINTE EXPLICITE DE L'ORDRE. Un `blur` part quand on touche
    l'écran ailleurs, quand le clavier se referme, quand on veut relire — ce
    n'est pas une intention de valider."""
    js = _js()
    for banned in ('"blur"', "'blur'", '"input"', "'input'",
                   '"change"', "'change'", "focusout", "setTimeout("):
        assert banned not in js, (
            f"l'auto-validation écoute « {banned} » : ce n'est pas une "
            f"transition explicite"
        )


def test_the_commit_listens_to_an_explicit_key_transition():
    js = _js()
    assert '"keydown"' in js, "aucune transition clavier explicite"
    assert "Enter" in js


def test_an_incomplete_set_is_never_committed():
    """Une série à moitié saisie ne s'enregistre pas — on avance dans la
    saisie plutôt que d'écrire un fait incomplet."""
    js = _js()
    assert "readyToCommit" in js
    body = js.split("function readyToCommit", 1)[1].split("}", 1)[0]
    # `python:S9073` — deux assertions, pas une composite : quand elle échoue,
    # on veut savoir LEQUEL des deux champs a disparu du test de complétude.
    assert "weight" in body, body
    assert "reps" in body, body


def test_a_correction_is_never_auto_committed():
    """Rectifier une série passée reste un geste délibéré."""
    js = _js()
    assert "setline--correcting" in js, (
        "l'auto-validation ne se retire pas en correction"
    )


# ═════════ 3. LE REPOS EST UN ÉTAT, PAS UNE PORTE ═════════


def test_the_next_set_row_is_a_real_link_during_rest():
    """Sans JS aussi : c'est un `<a>` vers la même page sans `rest=1`, donc
    `console_state` dérive `CURRENT_SET` et la série redevient saisissable.
    Rien n'est persisté au passage."""
    card = _card()
    assert RESUME_MARKER in card
    resume = card.split(RESUME_MARKER, 1)[1][:400]
    assert "<a" in card.split(RESUME_MARKER, 1)[0][-200:], (
        "l'affordance de reprise n'est pas un lien"
    )
    assert "rest=1" not in resume, (
        "le lien de reprise reconduirait à l'état de repos"
    )


def test_the_manual_skip_remains_available():
    """L'ordre le demande explicitement : la sortie manuelle survit."""
    from app.services.console_state import ConsoleState, command_for

    class _Set:
        set_index = 2
    cmd = command_for(ConsoleState(state="rest", current_set=_Set()))
    assert cmd["label"], "la commande de sortie de repos a disparu"
    assert cmd["nav"] is None, (
        "la sortie de repos ne doit rien soumettre : c'est un lien"
    )


def test_rest_exits_by_itself_at_zero():
    js = _js()
    assert "data-rest-resume-url" in js, "aucune URL de sortie automatique"
    # `python:S9073` — une assertion par fait. Ici la disjonction est
    # légitime (deux façons d'écrire la même navigation), mais elle se dit
    # sans `or` : on cherche l'une OU l'autre dans une liste.
    navigations = [f for f in ("location.assign", "location.href") if f in js]
    assert navigations, "le minuteur n'emmène nulle part à zéro"


def test_both_exits_lead_to_the_same_url():
    """`REST --minuteur 0--> CURRENT_SET` et `REST --tap--> CURRENT_SET`
    doivent aboutir au même état : deux destinations pour une intention
    unique serait un défaut."""
    card = _card()
    assert "set rest_resume_url" in card, (
        "l'URL de reprise n'est pas calculée une seule fois"
    )
    assert "rest_resume_url" in REST_TPL.read_text(encoding="utf-8")


# ═════════ 4. LE MINUTEUR RAISONNE SUR UNE ÉCHÉANCE ═════════


def test_the_timer_is_deadline_based_not_a_decrement():
    """EXIGENCE EXPLICITE. Un `setInterval` n'est pas une horloge : chaque
    rappel bridé deviendrait une seconde de repos inventée, et la dérive
    s'accumule d'autant plus qu'on ne regarde pas l'écran."""
    js = _js()
    assert "deadline" in js, "aucune échéance"
    assert "Date.now()" in js
    assert "remaining -= 1" not in js, "le décrément est de retour"
    assert re.search(r"remaining\s*=\s*remaining\s*-", js) is None


def test_a_late_callback_corrects_instead_of_drifting():
    """La lecture de l'heure doit se faire À CHAQUE tick, sinon l'échéance ne
    sert à rien."""
    js = _js()
    fn = js.split("function remaining()", 1)
    assert len(fn) == 2, "pas de calcul du restant à partir de l'échéance"
    assert "Date.now()" in fn[1].split("}", 1)[0]


def test_returning_from_background_catches_up():
    js = _js()
    assert "visibilitychange" in js, (
        "revenir d'un onglet en arrière-plan ne rattrape pas"
    )


def test_the_adjustment_moves_the_deadline_and_persists_nothing():
    js = _js()
    adjust = js.split("function adjust(", 1)[1].split("\n    }", 1)[0]
    assert "deadline" in adjust, "`±15 s` ne déplace pas l'échéance"
    for banned in ("fetch", "localStorage", "sessionStorage", "requestSubmit"):
        assert banned not in adjust, f"`±15 s` persiste quelque chose : {banned}"


# ═════════ 5. L'AFFORDANCE DU SÉLECTEUR DE SUBSTITUTION ═════════


def test_the_substitute_picker_summary_draws_its_marker():
    """Repliée dans cette tranche sur ordre : c'était le troisième `<summary>`
    en `display: flex` sans marqueur, mesuré en `UX4_02C` et laissé alors
    parce qu'il vit sur cette surface souveraine."""
    css = re.sub(r"/\*[\s\S]*?\*/", " ", CSS.read_text(encoding="utf-8"))
    drawing = [
        body for sel, body in re.findall(r"([^{}]+)\{([^}]*)\}", css)
        if ".substitute-picker__summary::before" in sel and "border-left" in body
    ]
    assert drawing, "« Adapter » ne dessine toujours aucun marqueur"


# ═════════ 6. AUCUNE NOUVELLE PRESCRIPTION DE REPOS ═════════


def test_no_new_rest_prescription_is_introduced():
    """L'ordre diffère `DF-D`. La durée reste un repli de présentation."""
    from app.services.console_state import REST_FALLBACK_SECONDS

    assert REST_FALLBACK_SECONDS == 90
    # ⚠ Retirer docstrings ET commentaires : `rest_target_seconds` figure
    # dans un commentaire qui l'INTERDIT, et la garde échouait sur la prose
    # expliquant qu'on ne fait pas la chose. Piège récurrent de ce dépôt.
    src = (ROOT / "app/services/console_state.py").read_text(encoding="utf-8")
    body = re.sub(r'"""[\s\S]*?"""', " ", src)
    body = "\n".join(ln.split("#", 1)[0] for ln in body.splitlines())
    for banned in ("rest_target_seconds", "RestRecommendation", "reason_code"):
        assert banned not in body, f"prescription de repos introduite : {banned}"
