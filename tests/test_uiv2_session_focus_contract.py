"""Sb_UIV2_SESSION_FOCUS_02 — contrat de l'écran de séance active.

Ce fichier garde trois choses que le reste de la suite ne gardait pas :

1. **Ce qu'est réellement le CTA primaire.** Il est SCOPÉ À L'EXERCICE
   (`name="nav" value="next"` — enregistrer et passer à l'exercice suivant).
   Ce n'est pas « valider la série » : Auren n'a AUCUNE action de série
   aujourd'hui (`completed` est dérivé côté serveur de la présence de
   weight/reps, cf. Sb_24.4). Le sprint Sb_SESSION_SET_ACTION_01 porte cette
   limitation.

2. **Que le libellé ne mente pas sur le comportement.** Un bouton qui dit
   « Valider la série » alors qu'il poste `nav=next` ferait sauter un
   exercice entier à l'utilisateur. Le nom accessible et le libellé visible
   doivent décrire la même action réelle.

3. **L'ordre CURRENT-FIRST**, en ordre de SOURCE et non en ordre visuel.
"""
from __future__ import annotations

import pathlib
import re

CARD = pathlib.Path(__file__).resolve().parent.parent / (
    "app/templates/_partials/exercise_card.html"
)
DETAIL = pathlib.Path(__file__).resolve().parent.parent / (
    "app/templates/session_detail.html"
)

#: Formulations qui affirmeraient une action de SÉRIE. Interdites tant qu'il
#: n'existe pas d'action de série réelle.
SET_LEVEL_CLAIMS = (
    "Valider la série",
    "Valider la serie",
    "Valider cette série",
    "Enregistrer la série",
    "Série suivante",
    "Serie suivante",
)


def _cta_block() -> str:
    """Le bloc du bouton primaire d'exercice, isolé du reste du gabarit.

    On cible l'élément `<button>` dont un attribut `class` porte réellement
    le marqueur — et pas la première occurrence textuelle du nom, qui vit
    dans le commentaire d'en-tête décrivant les hooks. Chercher la chaîne
    nue renvoyait ce commentaire et le test comparait alors un fragment qui
    n'était pas le bouton.
    """
    src = CARD.read_text(encoding="utf-8")
    match = re.search(
        r"<button\b[^>]*class=\"[^\"]*session-focus__cta-primary[^\"]*\"[^>]*>"
        r".*?</button>",
        src,
        re.DOTALL,
    )
    assert match, "primary exercise CTA <button> not found"
    return match.group(0)


# ───────── 1. sémantique réelle du CTA ─────────


def test_primary_cta_is_the_exercise_navigation_submit():
    """Le sélecteur utilisé comme « action primaire » est bien le submit
    d'exercice, pas un autre contrôle collant qui passerait par là."""
    block = _cta_block()
    assert 'type="submit"' in block
    assert 'name="nav"' in block, (
        "the primary CTA must be the exercise navigation submit"
    )
    assert 'value="next"' in block, (
        "the primary CTA advances to the NEXT EXERCISE — that is its real "
        "behaviour and the assertion must say so"
    )


def test_primary_cta_is_not_the_finish_session_action():
    """« Terminer la séance » est une action de SÉANCE, portée par
    `name="action" value="end"` dans `session_detail.html`. Confondre les
    deux ferait passer une porte d'acceptation avec le mauvais bouton."""
    block = _cta_block()
    assert 'name="action"' not in block
    assert 'value="end"' not in block
    assert "Terminer la séance" not in block

    detail = DETAIL.read_text(encoding="utf-8")
    assert 'value="end"' in detail, "the session-level finish action must exist"
    assert "session-focus__cta-primary" not in detail, (
        "the exercise CTA marker must not leak onto the session finish action"
    )


# ───────── 2. le libellé ne ment pas ─────────


def test_cta_copy_does_not_claim_a_set_level_action():
    """Garde de copie sémantique.

    Planter « Valider la série » sur ce bouton, en gardant `nav=next`, doit
    faire tomber ce test : le bouton ferait sauter un exercice entier alors
    qu'il prétendrait valider une série.
    """
    block = _cta_block()
    for claim in SET_LEVEL_CLAIMS:
        assert claim not in block, (
            f"{claim!r} claims a set-level action that does not exist; the "
            "button posts nav=next and advances the whole exercise"
        )


def test_no_set_level_submit_exists_in_the_set_rows():
    """Documente la limitation au lieu de la masquer.

    Si un jour une action de série apparaît, ce test tombe — et c'est le
    signal que Sb_SESSION_SET_ACTION_01 a été livré et que la porte
    d'acceptation UIV2 doit être rouverte.
    """
    src = CARD.read_text(encoding="utf-8")
    row_start = src.find("work_set_list")
    row_end = src.find("endmacro", row_start)
    macro = src[row_start:row_end]
    assert "<button" not in macro, (
        "no per-set action exists in the current product; adding one changes "
        "the acceptance contract and must be a deliberate slice"
    )


# ───────── 3. ordre CURRENT-FIRST, en SOURCE ─────────


def test_current_set_is_rendered_before_completed_sets():
    src = CARD.read_text(encoding="utf-8")
    current = src.find("work_set_list([_current_set]")
    completed = src.find("session-focus__completed-sets")
    assert current != -1 and completed != -1
    assert current < completed, (
        "the current set must be emitted before the completed-set history"
    )


def test_completed_and_warmup_history_stay_editable_in_the_dom():
    """Repliés, mais jamais retirés : un `details` fermé soumet ses
    contrôles, donc la sérialisation est identique."""
    src = CARD.read_text(encoding="utf-8")
    assert "session-focus__completed-sets" in src
    assert "session-focus__warmup-recap" in src
    # les deux passent par la MÊME macro que la série courante
    assert src.count("work_set_list(") >= 4
    assert "warmup_block(" in src


def test_no_css_order_is_used_to_fake_the_hierarchy():
    """L'ordre doit être réel. Un `order:` CSS satisferait l'œil et
    tromperait le clavier."""
    css = (pathlib.Path(__file__).resolve().parent.parent
           / "app/static/css/session_focus.css").read_text(encoding="utf-8")
    offenders = [
        line.strip()
        for line in css.splitlines()
        if re.match(r"^\s*order\s*:", line)
    ]
    assert not offenders, f"visual reordering found: {offenders}"
