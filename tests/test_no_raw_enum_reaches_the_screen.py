"""Une clé de programme ne s'affiche pas à un utilisateur.

LE CONSTAT, MESURÉ SUR LE RÉCAP DE SÉANCE

    Concentration            low
    État                     tired
    Confiance du logging     eleve (90)
    Bodyweight               75,6 kg

Quatre lignes, quatre fuites : deux valeurs d'énumération anglaises, une clé
française **sans accent** (`eleve` est un identifiant, pas un mot), et un
libellé anglais.

Les libellés français EXISTAIENT pour deux d'entre elles. L'utilisateur les
avait lus au moment même de répondre, dans le formulaire de fin de séance :
« Focalisé · Correct · Distrait » et « En forme · Moyen · Fatigué ».
`DECLARED_STATE_LABELS` traduisait déjà l'énergie depuis
`Sb_SESSION_REVIEW_SIGNAL_01` ; la concentration n'avait **jamais** eu sa
table. Une des deux questions du bilan était citée, l'autre exposée en clé.

CE QUE CETTE GARDE VÉRIFIE

1. les tables de libellés couvrent **exactement** les valeurs que le
   formulaire propose — ni plus, ni moins ;
2. les identifiants restent **intacts** : ils partent dans l'export JSON et
   CSV, les renommer casserait un contrat livré ;
3. aucun gabarit ne rend une valeur d'énumération **sans son repli de
   libellé**.
"""
from __future__ import annotations

import pathlib
import re

from app.services.confidence import LEVEL_HIGH, LEVEL_LABELS, LEVEL_LOW, LEVEL_MID
from app.services.progress_signals import (
    DECLARED_CONCENTRATION_LABELS,
    DECLARED_STATE_LABELS,
)

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "app/templates"
SESSION_FORM = TEMPLATES / "session_detail.html"
JINJA_COMMENT = re.compile(r"\{#.*?#\}", re.S)


def _paires_du_formulaire(champ: str) -> dict[str, str]:
    """Les couples (valeur, libellé) que le FORMULAIRE propose réellement.

    Lus dans le gabarit plutôt que recopiés : c'est l'écran que l'utilisateur
    a sous les yeux qui fait autorité, pas une constante qu'on croit à jour.
    """
    src = JINJA_COMMENT.sub(" ", SESSION_FORM.read_text(encoding="utf-8"))
    bloc = re.search(
        re.escape(f'"{champ}"') + r",\s*\[(.*?)\]", src, flags=re.S
    )
    assert bloc, f"le formulaire ne propose plus de choix pour « {champ} »"
    return dict(re.findall(r'\("([^"]+)",\s*"([^"]+)"\)', bloc.group(1)))


def test_the_concentration_labels_quote_the_form():
    """Pas un synonyme : le mot que l'utilisateur a lu en répondant."""
    assert DECLARED_CONCENTRATION_LABELS == _paires_du_formulaire("concentration"), (
        "la table des libellés de concentration a dérivé du formulaire — "
        "AUREN citerait une réponse que l'utilisateur n'a pas donnée"
    )


def test_the_state_labels_quote_the_form():
    assert DECLARED_STATE_LABELS == _paires_du_formulaire("global_state"), (
        "la table des libellés d'énergie a dérivé du formulaire"
    )


def test_the_confidence_identifiers_are_never_renamed():
    """`eleve` n'a pas d'accent, et c'est VOULU.

    Ces trois valeurs partent dans l'export JSON et CSV (`export_builder.py`,
    colonne `confidence_level`). Les « corriger » en français casserait un
    contrat de données déjà livré — l'accent appartient au LIBELLÉ, pas à la
    clé.
    """
    assert (LEVEL_HIGH, LEVEL_MID, LEVEL_LOW) == ("eleve", "moyen", "faible")
    assert set(LEVEL_LABELS) == {LEVEL_HIGH, LEVEL_MID, LEVEL_LOW}
    assert LEVEL_LABELS[LEVEL_HIGH] == "élevée", (
        "le libellé rendu à l'écran doit porter son accent, contrairement à la clé"
    )


def test_no_template_renders_a_raw_enum_without_its_label():
    """Une valeur d'énumération ne se rend jamais seule.

    Le repli `label or valeur` est autorisé — mieux vaut afficher une clé
    inattendue que faire disparaître une déclaration réelle. Ce qui est
    interdit, c'est de rendre la valeur SANS avoir tenté le libellé.
    """
    brutes = []
    for f in sorted(TEMPLATES.rglob("*.html")):
        src = JINJA_COMMENT.sub(" ", f.read_text(encoding="utf-8"))
        # ⚠ LES ATTRIBUTS SONT RETIRÉS AVANT LA RECHERCHE.
        #
        # Première écriture : elle accusait
        # `class="confidence-badge--{{ confidence_level }}"`, où la clé pilote
        # une classe CSS et n'est jamais lue par personne. Une garde qui ne
        # distingue pas le TEXTE de l'ATTRIBUT accuse l'usage légitime de la
        # valeur — et se fait désarmer.
        sans_attributs = re.sub(r'\s[a-z-]+="[^"]*"', " ", src)
        for champ in ("concentration", "global_state", "confidence_level"):
            for m in re.finditer(
                r"\{\{\s*([a-z_.]*\b" + champ + r")\s*\}\}", sans_attributs
            ):
                ligne = sans_attributs[: m.start()].count("\n") + 1
                brutes.append(f"{f.relative_to(TEMPLATES)}:~{ligne} — {m.group(1)}")
    assert not brutes, (
        "valeur d'énumération rendue sans libellé — l'utilisateur y lirait une "
        "clé de programme :\n  " + "\n  ".join(brutes)
    )


def test_the_recap_says_no_english_label():
    """« Bodyweight » et « logging » sur un écran français."""
    src = JINJA_COMMENT.sub(
        " ", (TEMPLATES / "session_done.html").read_text(encoding="utf-8")
    )
    texte = re.sub(r"<[^>]+>|\{\{.*?\}\}|\{%.*?%\}", " ", src, flags=re.S)
    for mot in ("Bodyweight", "logging"):
        assert mot not in texte, (
            f"« {mot} » est rendu sur le récap — le produit est en français"
        )
