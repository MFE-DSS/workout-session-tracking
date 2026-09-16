"""`UI-CP3.5` — une séance a-t-elle été matériellement incomplète ?

POURQUOI CE MODULE EXISTE
-------------------------
`INCOMPLETE_SESSION` est déclaré dans `DivergenceKind` depuis l'écriture du
moteur de replanification, et **émis nulle part** — ni dans `app/`, ni dans ses
trois fichiers de tests. Ce module produit le fait qui lui manquait.

CE QU'IL EST, ET CE QU'IL N'EST PAS
-----------------------------------
C'est une **propriété de la séance seule**. Il ne rapproche aucune séance
enregistrée d'un créneau planifié : cette identité plan↔séance n'est persistée
nulle part, et `detect_divergences` dit explicitement que la deviner
« produirait des divergences fantômes ».

PURETÉ
------
`completion_of` est **pure** : aucune I/O, aucune horloge. Elle lit des lignes
déjà chargées. C'est ce qui permet de l'appeler à la clôture d'une séance, au
même instant que `_persist_implicit_labels_on_completion`, sans une requête de
plus.
"""
from __future__ import annotations

from dataclasses import dataclass

#: Seuil tranché par l'opérateur : **moins de 50 % du travail prescrit
#: effectué**. Nommé plutôt qu'inséré dans une comparaison — le déplacer est
#: une décision produit, et elle doit être visible.
MATERIALLY_INCOMPLETE_BELOW = 0.50


@dataclass(frozen=True)
class SessionCompletion:
    """Ce qui a été fait, sur ce qui était prescrit. Des comptes, rien d'autre."""

    done: int
    total: int

    @property
    def ratio(self) -> float | None:
        """`None` quand il n'y a rien à compléter — jamais 0,0.

        Une séance cardio n'a aucune série de travail prescrite. Lui attribuer
        un taux de 0 % en ferait la plus incomplète de toutes, alors qu'elle
        est simplement d'une autre nature. C'est la règle du contrat de
        récupération appliquée ici : *une donnée manquante n'est jamais
        promue en zéro.*
        """
        if self.total <= 0:
            return None
        return self.done / self.total

    @property
    def is_materially_incomplete(self) -> bool:
        """Vrai uniquement quand un ratio EXISTE et passe sous le seuil."""
        r = self.ratio
        if r is None:
            return False
        return r < MATERIALLY_INCOMPLETE_BELOW


def completion_of(session) -> SessionCompletion:
    """Séries de travail validées sur séries de travail prescrites.

    ⚠ MÊME DÉFINITION QUE LE RESTE DU DÉPÔT, PAS UNE VARIANTE.
    « Série faite » = `kind == "work"` **et** `completed` — exactement
    `zone_exposure._work_sets` et `kpis.work_sets_done_30d`. Le dépôt n'a
    besoin que d'une seule notion de série faite ; en écrire une seconde ferait
    diverger deux surfaces sur le même fait.

    L'échauffement ne compte pas : depuis `UI-CP2.1` il n'est plus une porte,
    et il ne doit pas non plus gonfler un compte que l'utilisateur lit comme du
    travail.
    """
    done = 0
    total = 0
    for se in session.session_exercises:
        for sl in se.set_logs:
            if sl.kind != "work":
                continue
            total += 1
            if sl.completed:
                done += 1
    return SessionCompletion(done=done, total=total)
