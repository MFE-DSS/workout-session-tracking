"""Vue-modèle des signaux d'entraînement de `/progress` (`UX4_03B`).

**Ce module ne calcule rien.** Il traduit des `ProgressFacts` déjà produits en
lignes de gabarit. Aucune requête, aucun seuil, aucune formule — même patron que
`home_training_state`, qui sélectionne des phrases déjà écrites plutôt que d'en
réécrire.

La séparation en deux modules n'est pas cosmétique : `progress_facts` touche la
base, celui-ci est **pur**, et une garde vérifie qu'il n'importe ni `sqlalchemy`
ni `datetime`. C'est ce qui permet de tester chaque état de rendu — connu,
inconnu, déclaration périmée — sans base ni serveur.

CE QUE `UX4_03A` A ÉTABLI, ET QUI GOUVERNE CE FICHIER
-----------------------------------------------------

L'audit sémantique a mesuré trois défauts dans le premier rendu, tous du même
genre : **une donnée manquante y prenait l'apparence d'une mesure.**

===================  ====================  ===================================
Rendu refusé         Mesure                Ce que ce module rend
===================  ====================  ===================================
« Charge 45/100 »    45,0 = LE DÉFAUT      le mot que l'utilisateur a déclaré
« Régularité 0/100 » 3 séances → 21/100    un comptage, sans dénominateur
« Continuité         `compute_trend(0,0)`  ``—`` quand les deux fenêtres sont
  stable »           rend « stable »         vides
===================  ====================  ===================================

Le dépôt avait déjà écrit la règle, dans `recovery_contract` :

    « the user told us nothing » is not a measurement and must not be dressed
    up as a neutral reading.

DEUX INTERDITS STRUCTURELS, REPRIS DU CONTRAT EXISTANT
-------------------------------------------------------

1. **Aucun scalaire agrégé.** `FatigueSignal` refuse explicitement l'agrégat :
   « collapsing them into one number destroys exactly the information an
   explanation surface needs ». Un `/100` ici serait ce nombre.

2. **Aucune barre proportionnelle.** L'Accueil l'a déjà tranché pour la même
   classe de signal (`Sx_UIV3_01`) : « une barre proportionnelle serait une
   affirmation de pourcentage physiologique ». La première version de
   `UX4_03` en affichait trois.

POURQUOI LE RESSENTI N'EST PAS REBINNÉ
----------------------------------------

`global_state` **naît catégoriel** : l'utilisateur choisit entre trois boutons.
`compute_session_fatigue` le convertit en 80/50/20, en moyenne trois séances,
puis un affichage en bandes le rebinnerait en trois mots. Cet aller-retour perd
l'information et **en invente une autre** : une précision décimale que la saisie
n'a jamais eue.

La présentation honnête d'une catégorie, c'est la catégorie. On renvoie donc à
l'utilisateur **le mot qu'il a lui-même choisi**.
"""
from __future__ import annotations

from typing import Any

from app.services.progress_facts import ProgressFacts

#: Les libellés que l'utilisateur a vus AU MOMENT DE DÉCLARER.
#:
#: Ils ne sont pas réécrits ici : ce sont ceux du formulaire de fin de séance
#: (`session_detail.html`). Renvoyer un synonyme — « modéré » pour « Moyen » —
#: donnerait l'impression qu'AUREN a interprété la réponse, alors qu'il la cite.
#: Une garde compare cette table à celle du gabarit et rougit si l'une dérive.
DECLARED_STATE_LABELS: dict[str, str] = {
    "good": "En forme",
    "flat": "Moyen",
    "fatigued": "Fatigué",
}

#: Libellé du signal subjectif.
#:
#: **Pas « Charge perçue ».** Ce libellé surinterprétait la source. Le
#: formulaire de fin de séance demande, mot pour mot :
#:
#:     Énergie générale
#:     Comment te sentais-tu pendant la séance ?
#:     En forme · Moyen · Fatigué
#:
#: C'est une question sur le RESSENTI, pas sur l'effort. « Charge perçue » est
#: le vocabulaire du RPE — une échelle d'effort perçu que ce dépôt ne collecte
#: nulle part. L'employer ici ferait passer une question d'humeur pour une
#: mesure d'intensité, et rendrait le terme indisponible le jour où AUREN
#: mesurera vraiment l'effort perçu.
SUBJECTIVE_LABEL = "Ressenti général"

#: Rendu de l'inconnu. Un mot, pas un tiret : l'absence de déclaration est un
#: état qui se lit, pas une case vide. Masculin — il s'accorde avec
#: « Ressenti », pas avec l'ancienne « Charge ».
UNKNOWN_VALUE = "inconnu"

#: Rendu de l'indécidable. Le tiret est correct ici : il n'y a rien à nommer.
NO_DATA_VALUE = "—"


def _general_feeling(facts: ProgressFacts) -> dict[str, Any]:
    """Le ressenti déclaré, cité tel quel — daté s'il n'est plus le dernier.

    TROIS ÉTATS, PAS DEUX. Remonter jusqu'à la dernière déclaration réelle est
    le bon comportement : se taire parce que la séance la plus récente a été
    terminée sans répondre perdrait une information vraie. Mais rendre une
    déclaration de neuf jours comme si elle datait de la dernière séance
    **fabriquerait une fraîcheur** — le défaut du 45,0 déplacé du contenu vers
    le temps. Elle porte donc sa date, et seulement dans ce cas : la dater
    quand elle est la plus récente ajouterait du bruit sans rien apprendre.
    """
    label = DECLARED_STATE_LABELS.get(facts.declared_state or "")
    if label is None:
        return {
            "name": SUBJECTIVE_LABEL,
            "value": UNKNOWN_VALUE,
            "context": "aucun ressenti déclaré",
            "known": False,
        }
    if facts.declared_is_latest or facts.declared_at is None:
        context = "déclaré en fin de séance"
    else:
        context = f"dernière déclaration · {facts.declared_at:%d/%m}"
    return {
        "name": SUBJECTIVE_LABEL,
        "value": label,
        "context": context,
        "known": True,
    }


def _sessions(facts: ProgressFacts) -> dict[str, Any]:
    """Un comptage. Pas de dénominateur : 14 séances en 14 jours n'est pas la
    cible du produit, et en faire le 100 % affichait un rythme sain comme un
    quasi-échec (3 séances → « 21/100 »)."""
    n = facts.sessions_14d
    return {
        "name": "Séances",
        "value": str(n) if n else "aucune",
        "context": "14 derniers jours",
        "known": True,
    }


# ── `UX4_03D` — L'OBJET « CADENCE 7 J » EST RETIRÉ ───────────────────────────
#
# `OPERATOR_DECISION`, décision 2 : **la cadence est absorbée par le rail.**
# Elle rendait `3 → 2`, c'est-à-dire le nombre de séances des sept jours
# précédents puis des sept derniers. Le rail rend ces quatorze jours un par un :
# la densité de sa moitié droite contre celle de sa moitié gauche EST cette
# comparaison, à l'œil, sans un objet de plus.
#
# Ce n'est pas une soustraction (`CLAUDE.md §5.3`) : la preuve visuelle part
# dans la MÊME livraison que le retrait, et elle en dit davantage — la cadence
# donnait deux nombres, le rail donne les quatorze jours qui les composent.


#: Classe CSS par état de trace. Aucune couleur ne code le TYPE de séance :
#: musculation et cardio sont deux actions utilisateur, et le socle réserve
#: l'ambre à « action / actuel ». Le type passe par une texture.
_TRACE_CLASS = {
    "done": "rail__c rail__c--on",
    "rest": "rail__c rail__c--rest",
    "active": "rail__c rail__c--active",
    "none": "rail__c rail__c--void",
}


def build_progress_rail(facts: ProgressFacts) -> list[dict[str, Any]]:
    """Les 14 traces, prêtes pour le gabarit. Fonction pure.

    Le `title` n'invente rien : il cite le nom du programme quand il existe,
    et dit « repos » ou « séance en cours » sinon. Le type n'est ajouté que
    s'il est **connu** — un template supprimé rend `kind is None`, et la trace
    reste alors une trace sans qualificatif plutôt qu'une musculation
    supposée.
    """
    cells = []
    for d in facts.days:
        cls = _TRACE_CLASS.get(d.state, _TRACE_CLASS["rest"])
        if d.state == "done" and d.kind == "cardio":
            cls += " rail__c--cardio"
        if d.state == "done":
            title = f"{d.label} · {d.name}" if d.name else d.label
        elif d.state == "active":
            title = f"{d.label} · séance en cours"
        elif d.state == "none":
            title = f"{d.label} · hors historique"
        else:
            title = f"{d.label} · repos"
        cells.append({"cls": cls, "title": title, "label": d.label})
    return cells


#: Comment nommer un type de séance à l'oreille. Le rail le distingue par une
#: texture ; un lecteur d'écran ne voit pas de texture.
_KIND_WORD = {"strength": "musculation", "cardio": "cardio"}


def build_rail_summary(facts: ProgressFacts) -> str:
    """Équivalent TEXTUEL du rail, rendu côté serveur.

    POURQUOI CETTE FONCTION EXISTE
    --------------------------------
    Le rail est `aria-hidden` — `Web:S6819` avait raison, le compte « 5 séances
    · 14 derniers jours » est déjà rendu en texte juste au-dessus et une
    étiquette d'image le répétait à l'oreille.

    Mais le rail porte **davantage** que ce compte : la répartition des jours,
    la distinction entre séance terminée et séance en cours, la couverture de
    l'historique, et le type de chaque séance. Rien de tout cela n'était
    accessible — les `title` ne sont pas annoncés de façon fiable.

    Masquer un objet dont l'information n'existe nulle part ailleurs, c'est la
    rendre visuelle-seulement. D'où cet équivalent, **construit à partir des
    mêmes `facts.days`** que `build_progress_rail` : aucun recalcul, une seule
    source, et la divergence entre ce qu'on voit et ce qu'on entend devient
    structurellement impossible.
    """
    done, active, void = [], [], 0
    for d in facts.days:
        if d.state == "done":
            word = _KIND_WORD.get(d.kind or "")
            done.append(f"{d.label} {word}" if word else d.label)
        elif d.state == "active":
            active.append(d.label)
        elif d.state == "none":
            void += 1

    # ⚠ Aucun `+`, pas même sur des chaînes. `test_no_new_business_calculation`
    # interdit tout `ast.BinOp` additif dans ce module, et il a rougi sur une
    # concaténation. La garde vise l'arithmétique métier, pas le formatage —
    # mais elle ne peut pas distinguer les deux statiquement, et l'affaiblir
    # pour un confort d'écriture serait le mauvais échange. On formate donc
    # sans opérateur.
    parts = ["Quatorze derniers jours."]
    if done:
        n = len(done)
        s = "s" if n > 1 else ""
        parts.append(f"{n} séance{s} terminée{s} : {', '.join(done)}.")
    else:
        parts.append("Aucune séance terminée.")
    if active:
        parts.append(f"Séance en cours, non comptée : {', '.join(active)}.")
    if void:
        parts.append(f"{void} jour{'s' if void > 1 else ''} hors historique.")
    return " ".join(parts)


def build_progress_signals(facts: ProgressFacts) -> list[dict[str, Any]]:
    """Les trois lignes L1, dans un ordre stable.

    Le ressenti d'abord — ce que l'utilisateur a **dit** passe avant ce
    qu'AUREN **compte**, comme dans `home_training_state._select_items`.
    """
    return [_general_feeling(facts), _sessions(facts)]


__all__ = [
    "DECLARED_STATE_LABELS",
    "SUBJECTIVE_LABEL",
    "UNKNOWN_VALUE",
    "build_progress_rail",
    "build_progress_signals",
    "build_rail_summary",
]
