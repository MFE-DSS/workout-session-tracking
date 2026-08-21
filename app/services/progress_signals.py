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

#: Rendu de l'indécidable. Ici le tiret est correct : il n'y a pas de rythme à
#: comparer, donc rien à nommer.
NO_CADENCE_VALUE = "—"


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


def _cadence(facts: ProgressFacts) -> dict[str, Any]:
    """Deux comptages comparés, rendus comme deux comptages.

    Le défaut que ceci ferme : `compute_trend(0, 0)` rend `"stable"`, donc
    l'ancien gabarit annonçait une continuité **stable** à quelqu'un qui n'avait
    jamais rien enregistré. Zéro contre zéro n'est pas une stabilité, c'est une
    absence de rythme — et c'est ce que dit `NO_CADENCE_VALUE`.
    """
    last_7, prev_7 = facts.sessions_last_7, facts.sessions_prev_7
    if not last_7 and not prev_7:
        return {
            "name": "Cadence 7 j",
            "value": NO_CADENCE_VALUE,
            "context": "aucune séance sur 14 jours",
            "known": False,
        }
    return {
        "name": "Cadence 7 j",
        "value": f"{prev_7} → {last_7}",
        "context": "7 jours précédents, puis les 7 derniers",
        "known": True,
    }


def build_progress_signals(facts: ProgressFacts) -> list[dict[str, Any]]:
    """Les trois lignes L1, dans un ordre stable.

    Le ressenti d'abord — ce que l'utilisateur a **dit** passe avant ce
    qu'AUREN **compte**, comme dans `home_training_state._select_items`.
    """
    return [_general_feeling(facts), _sessions(facts), _cadence(facts)]


__all__ = [
    "DECLARED_STATE_LABELS",
    "NO_CADENCE_VALUE",
    "SUBJECTIVE_LABEL",
    "UNKNOWN_VALUE",
    "build_progress_signals",
]
