"""Signaux comportementaux — MIGRÉS depuis le Profil (`UX4_01`).

CE QUI A CHANGÉ, ET POURQUOI CES GARDES NE SONT PAS SUPPRIMÉES
---------------------------------------------------------------
Ces trois tests exigeaient que fatigue, régularité et série s'affichent **sur
le Profil**. La décision opérateur du 2026-08-20 déplace cette lecture :

    Le Profil répond à « que sait AUREN de moi ? » et « que puis-je changer
    volontairement ? ». Il ne répond PAS à « comment est-ce que je progresse ? ».

Une garde qui protège un placement officiellement abandonné n'est pas un
argument contre la refonte : **c'est un élément à migrer**
(`AUREN_UIUX_V3_GUARD_MIGRATION_REGISTER`, règle 6). Elles sont donc
retournées, pas effacées.

L'INVARIANT QUI NE PÉRIME PAS
------------------------------
Les signaux comportementaux restent **calculés et disponibles**. Seul leur
lieu d'affichage bouge. Ce qui est gardé ici :

  1. le Profil ne les rend plus — le déplacement a bien eu lieu ;
  2. le service qui les produit existe toujours — la capacité n'est pas perdue
     en passant par une suppression de gabarit.

DÉPENDANCE ENREGISTRÉE — NON RÉSOLUE DANS CETTE TRANCHE
--------------------------------------------------------
`PROGRESSION` est la destination désignée et **existe déjà**, mais **ne rend
pas encore** ces trois signaux : son chapeau annonce « la régularité » sans
l'afficher. L'opérateur interdit explicitement toute refonte de Progression
dans `UX4_01`.

Conséquence assumée et signalée : entre cette tranche et `UX4_03`, fatigue,
régularité et série sont **calculées mais nulle part visibles**. Ce n'est pas
un oubli — c'est le coût d'un déplacement en deux temps, et il appartient à
l'opérateur de décider s'il est acceptable.
"""
from __future__ import annotations


def test_the_profile_no_longer_answers_how_am_i_progressing(client):
    """**Migré.** La garde exigeait « fatigue » sur le Profil ; elle exige
    désormais son absence.

    Le bloc rendait aussi `0` comme une valeur mesurée — fatigue 0,
    régularité 0, série 0 — alors qu'aucune observation ne les soutenait.
    """
    body = client.get("/profile").text.lower()
    for signal in ("fatigue", "gularit", "jours de s"):
        assert signal not in body, (
            f"« {signal} » est encore rendu sur le Profil : la lecture de "
            "progression appartient à Progression"
        )


def test_the_behavioural_signals_are_still_computed():
    """**L'invariant qui survit au déplacement.** Retirer un gabarit ne doit
    pas supprimer la capacité : le service reste, et `UX4_03` le branchera sur
    Progression."""
    import dataclasses

    from app.services.behavioral import BehavioralState

    # ⚠ La première écriture interrogeait `__doc__` et `__dict__.keys()` du
    # module : du bricolage qui rougissait sans rien prouver. On lit le
    # CONTRAT — les champs de l'état comportemental.
    fields = {f.name for f in dataclasses.fields(BehavioralState)}
    for name in ("fatigue_score", "consistency_score", "streak_days"):
        assert name in fields, (
            f"{name} n'est plus produit — la capacité a été perdue, pas déplacée"
        )
