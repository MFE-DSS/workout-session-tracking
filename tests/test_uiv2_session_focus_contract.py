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
    # `DF-E` — LE PORTEUR A CHANGÉ, LA PROPRIÉTÉ NON.
    #
    # `session-focus__cta-primary` marquait le submit de la CARTE REPLIÉE.
    # Depuis `DF-E`, une carte non active est un LIEN d'activation : elle n'a
    # plus de submit, et ce marqueur n'existe plus nulle part.
    #
    # La capacité, elle, survit — sur le dock de la carte ACTIVE. On vise donc
    # ce que la propriété DIT (« un submit qui avance d'un exercice »), pas le
    # nom de classe que portait son ancien support.
    match = re.search(
        r"<button\b[^>]*name=\"nav\"[^>]*value=\"next\"[^>]*>.*?</button>",
        src,
        re.DOTALL,
    )
    assert match, "aucun submit d'avancement d'exercice trouvé"
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
    # `DF-E` — le marqueur de classe a disparu avec la carte repliée ; la
    # propriété gardée reste que l'action de SÉANCE ne se confond pas avec
    # l'avancement d'EXERCICE. On l'énonce sur ce qui existe.
    assert 'value="next"' not in detail.split('value="end"')[0][-400:], (
        "the exercise advance action must not leak onto the session finish"
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


def test_the_set_level_action_is_real_and_wired():
    """Ce test a fait exactement ce pour quoi il avait été écrit.

    ANCIEN CONTRAT (`test_no_set_level_submit_exists_in_the_set_rows`) :
    aucun `<button>` dans la macro de ligne, parce qu'aucune action de série
    n'existait — `completed` était dérivé serveur et le routeur n'offrait que
    `prev`/`next`. Sa docstring annonçait sa propre chute : « si un jour une
    action de série apparaît, ce test tombe, et c'est le signal que
    Sb_SESSION_SET_ACTION_01 a été livré ».

    C'est arrivé. La limitation est levée, donc la garde change de sens : au
    lieu d'interdire un bouton, elle exige que celui qui existe soit **réel**
    — un submit natif, câblé sur une valeur de `nav` réellement traitée par
    le routeur. La règle de fond est inchangée : **l'UI ne montre pas une
    action que le backend n'a pas.**
    """
    src = " ".join(CARD.read_text(encoding="utf-8").split())
    assert 'type="submit" name="nav" value="{{ cmd.nav }}" class="dock__cmd"' in src, (
        "la commande dominante n'est plus un submit natif"
    )

    # MIGRÉ — la commande ne vit plus dans une barre collante : elle vit dans
    # la console, au-dessus du pli, ce qui rend le collant inutile. Mesuré,
    # ce collant recouvrait la ligne `É1`.
    assert "session-focus__sticky-cta" not in src

    # La règle de fond est INCHANGÉE : l'UI ne montre jamais une action que
    # le routeur n'implémente pas.
    router = (pathlib.Path(__file__).resolve().parent.parent
              / "app/routers/sessions.py").read_text(encoding="utf-8")
    for nav in ('"stay"', '"stay_norest"', '"prev"'):
        assert nav in router, nav


# ───────── 3. ordre CURRENT-FIRST, en SOURCE ─────────


def test_current_set_is_rendered_before_completed_sets():
    # MIGRÉ — l'amendement B remplace « courante d'abord, historique
    # ensuite » par TROIS POSITIONS TEMPORELLES : passé compact, courante
    # développée, futur compact. L'utilisateur lit passé/maintenant/après
    # d'un coup d'œil. L'invariant conservé : une SEULE surface de saisie,
    # et c'est la courante.
    src = CARD.read_text(encoding="utf-8")
    assert "setline--past" in src
    assert "setline--current" in src
    assert "setline--future" in src
    # `set_inputs` (la surface de saisie) n'est appelée que pour la ligne
    # courante et pour l'échauffement — jamais pour une ligne passée ou
    # future, qui portent `set_values` (des hidden).
    body = src[src.find("{% macro past_line"):]
    past = body[:body.find("endmacro")]
    assert "set_inputs" not in past, (
        "une ligne passée ne doit pas ouvrir une seconde surface de saisie"
    )


def test_completed_and_warmup_history_stay_editable_in_the_dom():
    """Repliés, mais jamais retirés : un `details` fermé soumet ses
    contrôles, donc la sérialisation est identique."""
    src = CARD.read_text(encoding="utf-8")
    assert "setline--past" in src
    assert "warmup-recap" in src
    # MIGRÉ — les valeurs passées ne sont plus éditables SUR PLACE : elles
    # sont conservées en `hidden` (donc postées à l'identique) et rouvertes
    # explicitement par l'état `CORRECTION`. C'est le §7.4 : la correction
    # existait déjà mais était MUETTE, aucune affordance ne la signalait.
    assert "macro set_values(sl)" in src
    assert 'type="hidden"' in src
    assert "setline__fix" in src, "l'affordance de correction doit être visible"
    # L'échauffement replié, lui, reste directement saisissable.
    assert "setline--warmup-done" in src


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
