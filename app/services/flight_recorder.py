"""`UI-CP5 FLIGHT_RECORDER` — le DEBRIEFING, et rien qu'une lecture.

LA QUESTION QUE CET INSTRUMENT POSSÈDE
---------------------------------------
    « Qu'est-ce qui vient réellement de changer ? »

Le contrat (`AUREN_INSTRUMENTS §FLIGHT_RECORDER`) fixe trois rangs de détail —
`L1 le debrief · L2 le dernier mouvement · SHEET le détail par exercice` — et
**L1 n'existait nulle part**. Ce module le construit.

⚠ `ACTION : aucune. C'est une lecture.` Aucune fonction d'ici ne mute quoi que
ce soit, et le module ne connaît ni base ni horloge.

CE QUI N'EST PAS UN SCORE, ET COMMENT ON S'EN ASSURE
------------------------------------------------------
L'arbitrage opérateur est explicite : **pas de moteur de « plus
significatif »**, pas de score composite, aucun classement numérique de
métriques hétérogènes. Ce module obéit par CONSTRUCTION, pas par discipline :

* la précédence est un `if / elif / else` sur **trois booléens** ;
* les kilos ne rencontrent jamais les anomalies — aucune grandeur n'est
  comparée à une grandeur d'une autre nature ;
* **aucune** des trois variantes ne porte de champ de rang, de poids ou de
  gravité : un moteur de signification n'a littéralement pas d'endroit où
  écrire son résultat. Les seuls entiers exposés sont des **comptes** ;
* une garde AST vérifie l'absence de `sorted` / `max` / `min` et de toute
  multiplication dans ce fichier — un score a besoin de pondérer ou d'ordonner,
  et les deux sont absents.

LA PRÉCÉDENCE EST SÉMANTIQUE ET VERSIONNÉE
--------------------------------------------
    1. ATTENTION   — la dernière séance porte un signal nommable
    2. MOUVEMENT   — sinon, un mouvement comparable existe
    3. INSUFFISANT — sinon

`ORDRE_PRECEDENCE` et `PRECEDENCE_VERSION` sont épinglés **dans la même
assertion** : réordonner la précédence oblige à toucher la ligne qui porte la
version. C'est le mécanisme d'application du « versionné », pas une convention.

POURQUOI CE MODULE CHOISIT LA DERNIÈRE SÉANCE, ET PAS LA SEMAINE
------------------------------------------------------------------
`weekly_loop._pick_top_anomaly` existe et rend déjà une anomalie. Il n'est
**pas** réutilisé, pour trois raisons mesurées :

1. **Sa fenêtre est structurellement fausse pour cette question.** Elle est
   bornée à la semaine ISO courante. Le lundi matin, la dernière séance
   appartient à la semaine précédente : le signal se tait alors que « depuis ta
   dernière séance » doit encore parler.
2. **Il choisit la plus ANCIENNE.** `_load_window_sessions` trie
   `started_at.asc()` et `_pick_top_anomaly` rend les anomalies de la
   **première** séance qui en porte. C'est l'exact contraire d'un signal
   courant. *(Défaut réel du dépôt, pas hypothétique : la garde de récence de
   cette tranche le met en rouge en une ligne.)*
3. **`severity` vaut toujours `"info"`** — cinq occurrences dans
   `anomalies.py`, zéro pouvoir discriminant. Il n'y a pas de « top ». Ce
   module nomme donc ce qu'il fait : *le premier signal NOMMABLE de la dernière
   séance*, dans l'ordre d'émission du détecteur.

⚠ LA RÈGLE C RESTE DORMANTE ICI, ET C'EST UNE DÉCISION
--------------------------------------------------------
`compute_anomalies` est appelée **sans** `prior_weight_by_code`, donc la règle
C (« ±30 % de charge vs la dernière fois ») ne se déclenche pas sur cette
surface. Ce n'est pas un oubli.

`stats.last_time_by_exercise_code` — la seule carte existante — scope « la
dernière fois » sur l'identité **héritée** `(gabarit, code)`, précisément celle
que `progression_facts` a délibérément abandonnée au profit de l'identité
stable. La réveiller ferait cohabiter **deux « dernière fois » contradictoires
dans le même instrument** : le rung 1 sur une définition, le rung 2 sur une
autre. `/done` la réveille sur son identité héritée, et les deux surfaces
diffèrent **par conception**.

Condition de déblocage, nommée : une définition unique de l'occurrence
antérieure, partagée par la règle C et `progression_facts`.

LA GRAMMAIRE DE CONFIANCE EST EMPRUNTÉE, PAS DUPLIQUÉE
--------------------------------------------------------
Les quatre états ci-dessous sont ceux de `zone_exposure`. Ils sont **recopiés**
et non importés parce que `zone_exposure` importe `sqlalchemy` et que ce module
doit rester chargeable sans base ; une garde compare les deux jeux littéral par
littéral et rougit si l'un dérive.

**Ce n'est pas un second système de confiance.** Il n'y a ni score global, ni
badge, ni couche de fiabilité. L'état qualifie le **corpus de comparaison**,
exactement comme `zone_exposure` qualifie l'exposition ; il est **orthogonal**
au signal et ne se multiplie jamais avec lui. Un `ATTENTION` dans un corpus
`zero` est honnête : il y a un point à vérifier, et aucune comparaison n'est
encore possible.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar

from app.services.anomalies import compute_anomalies
from app.services.progression_view import (
    RAISON_AUCUNE_SERIE,
    RAISON_UNE_SEULE_SEANCE,
)

# ── la précédence ──────────────────────────────────────────────────────────

#: ⚠ VERSIONNÉE. Toute modification de `ORDRE_PRECEDENCE` exige d'incrémenter
#: cette chaîne — une garde les épingle dans la MÊME assertion, pour qu'on ne
#: puisse pas réordonner la précédence sans toucher la ligne de version.
PRECEDENCE_VERSION = "L1-DEBRIEF/1"

SIGNAL_ATTENTION = "attention"
SIGNAL_MOUVEMENT = "mouvement"
SIGNAL_INSUFFISANT = "comparaison_insuffisante"

#: Ordre de PRÉCÉDENCE SÉMANTIQUE. Ce n'est pas un ordre de gravité, et ce
#: n'est pas un classement : c'est la question « de quoi parle-t-on d'abord ? »,
#: tranchée une fois et écrite.
ORDRE_PRECEDENCE = (SIGNAL_ATTENTION, SIGNAL_MOUVEMENT, SIGNAL_INSUFFISANT)

# ── la grammaire de confiance, empruntée à `zone_exposure` ─────────────────

ETAT_CONNU = "known"
ETAT_ZERO = "zero"
ETAT_PARTIEL = "partial"
ETAT_INCONNU = "unknown"

# ── les causes d'insuffisance ──────────────────────────────────────────────

CAUSE_AUCUNE_SEANCE = "aucune_seance"
CAUSE_AUCUN_MOUVEMENT = "aucun_mouvement"
CAUSE_UNE_SEULE_SEANCE = "une_seule_seance"
CAUSE_AUCUNE_SERIE = "aucune_serie"
CAUSE_NOM_NON_RATTACHE = "nom_non_rattache"

#: L'en-tête de l'instrument. Constant : il nomme la FENÊTRE, jamais le verdict.
EN_TETE = "Depuis ta dernière séance"

#: ⚠ Aucun de ces libellés ne revendique une importance. Ni « le plus », ni
#: « principal », ni « significatif » : l'interface expose la règle par son
#: étiquette sémantique, pas par un score caché. Une garde le vérifie sur la
#: source ET sur la page rendue.
LIBELLE_ATTENTION = "À vérifier"
LIBELLE_MOUVEMENT = "Changé"
LIBELLE_INSUFFISANT = "Comparaison pas encore possible"


def _s(n: int) -> str:
    """Marque du pluriel. Copie assumée de `zone_exposure._s` — le filtre
    `pluriel` vit dans `app.templating`, qui importe `fastapi`."""
    return "s" if n > 1 else ""


# ── les trois variantes ────────────────────────────────────────────────────


@dataclass(frozen=True)
class Debrief:
    """Base commune. Jamais rendue seule.

    ⚠ `signal` est une `ClassVar` : c'est la marque du TYPE, pas une donnée
    d'instance. L'annoter en champ laisserait une instance mentir sur sa propre
    nature. Leçon `UI-CP4` — et la garde interroge `dataclasses.fields()`, pas
    `__dataclass_fields__`, qui inclut les pseudo-champs `ClassVar`.
    """

    signal: ClassVar[str] = ""

    etat: str
    libelle: str
    #: L'équivalent textuel complet, pour qui n'a que la voix.
    sr: str
    precedence_version: str = PRECEDENCE_VERSION


@dataclass(frozen=True)
class DebriefAttention(Debrief):
    """Un point à vérifier sur la dernière séance.

    Aucun champ d'écart : ce rang ne compare pas, il signale.
    """

    signal: ClassVar[str] = SIGNAL_ATTENTION

    rule_code: str = ""
    #: La phrase du détecteur, déjà écrite pour être lue (`anomalies.py`).
    message: str = ""
    exercice: str | None = None
    seance_id: int | None = None
    seance_gabarit: str | None = None
    #: Les AUTRES signaux nommables de la même séance. Un COMPTE, pas un rang.
    autres: int = 0


@dataclass(frozen=True)
class DebriefMouvement(Debrief):
    """Le dernier mouvement comparable.

    ⚠ Aucun champ ne peut porter un message d'anomalie : les deux rangs ne
    peuvent pas se confondre, même par accident de remplissage.

    Les valeurs sont **projetées** de `progression["lead"]` sans être
    reformatées. Ce module n'appelle aucun `format_*` : le relevé souverain a
    déjà décidé de son vocabulaire, et le redire ici le ferait diverger.
    """

    signal: ClassVar[str] = SIGNAL_MOUVEMENT

    slug: str = ""
    nom: str = ""
    dernier_poids: str = ""
    dernier_reps: str = ""
    precedent_poids: str = ""
    precedent_reps: str = ""
    ecart_poids: str | None = None
    ecart_reps: str | None = None
    trace: tuple[str, ...] = ()
    href: str = ""


@dataclass(frozen=True)
class Cause:
    """Une raison pour laquelle la comparaison n'est pas encore possible.

    `compte` est un COMPTE d'objets concernés. Il n'ordonne rien.
    """

    code: str
    compte: int
    libelle: str


@dataclass(frozen=True)
class DebriefInsuffisant(Debrief):
    """Pas encore de comparaison — et on dit POURQUOI.

    ⚠ Ce n'est **pas** un état d'erreur, et ce n'est pas un écran vide. Le L1
    possède la hiérarchie même quand il n'a rien à comparer : c'est l'état de
    tout compte neuf, et le taire inverserait la hiérarchie de la page (mesuré :
    à deux séances, le plus gros objet de l'écran devenait un titre de section).

    ⚠ Aucun champ ne peut porter un écart, une performance ou une trace : une
    comparaison inventée dans l'état « pas encore comparable » est
    **inexprimable**, pas seulement déconseillée.
    """

    signal: ClassVar[str] = SIGNAL_INSUFFISANT

    causes: tuple[Cause, ...] = ()
    non_rattachees: int = 0
    noms_non_rattaches: tuple[str, ...] = ()


# ── le rung 1 ──────────────────────────────────────────────────────────────


def _nom_exercice(seance, code: str | None) -> str | None:
    """Le nom RÉELLEMENT exécuté, substitution comprise.

    Même politique que `weekly_loop._exercise_name_for` — réimplémentée plutôt
    qu'importée, parce que `weekly_loop` importe `sqlalchemy` et casserait la
    pureté de ce module. Une garde compare les deux comportements.
    """
    if code is None:
        return None
    for se in getattr(seance, "session_exercises", ()) or ():
        if getattr(se, "exercise_code_snapshot", None) == code:
            return (getattr(se, "substituted_name", None)
                    or getattr(se, "exercise_name_snapshot", None))
    return None


def _signaux_nommables(seance) -> list:
    """Les anomalies de la séance qu'on sait nommer, dans l'ordre d'émission.

    ⚠ AUCUN TRI. `severity` vaut toujours `"info"` : trier dessus serait du
    théâtre. L'ordre retenu — exercices de la séance, puis règles A→E — est
    celui que le détecteur produit déjà, donc déterministe et non inventé.

    Une anomalie qu'on ne sait pas nommer n'est pas une information : elle est
    écartée plutôt qu'affichée vide. Leçon `test_anomaly_is_nameable.py`.
    """
    if seance is None:
        return []
    try:
        brutes = compute_anomalies(seance)
    except Exception:
        # Le debriefing ne fait jamais tomber la page. Même posture que
        # `_pick_top_anomaly` : en cas d'échec du détecteur, on descend d'un
        # rang plutôt que de rendre une erreur.
        return []
    return [a for a in brutes if getattr(a, "message", None)
            or getattr(a, "rule_code", None)]


# ── le rung 3 ──────────────────────────────────────────────────────────────


def _causes(seance, progression: dict[str, Any]) -> tuple[Cause, ...]:
    """Pourquoi la comparaison n'est pas encore possible.

    Chaque cause est prouvée par un champ qui EXISTE déjà. Aucune n'est
    devinée, et l'ordre est celui de la DÉCLARATION — jamais une gravité.
    """
    attente = progression.get("awaiting") or []
    non_rattachees = int(progression.get("unresolved") or 0)

    if not progression.get("any"):
        # Deux vides très différents, et les confondre serait la faute que
        # `zone_exposure` a déjà nommée : « aucune séance » est une absence de
        # matière, « des séances sans mouvement comparable » est un fait connu.
        if seance is None:
            return (Cause(
                CAUSE_AUCUNE_SEANCE, 0,
                "Aucune séance terminée : il n'y a encore rien à comparer.",
            ),)
        return (Cause(
            CAUSE_AUCUN_MOUVEMENT, 0,
            "Les séances enregistrées ne portent aucun mouvement comparable.",
        ),)

    causes: list[Cause] = []
    seules = [r for r in attente if r.get("reason") == RAISON_UNE_SEULE_SEANCE]
    sans_serie = [r for r in attente if r.get("reason") == RAISON_AUCUNE_SERIE]

    if seules:
        n = len(seules)
        causes.append(Cause(
            CAUSE_UNE_SEULE_SEANCE, n,
            f"{n} exercice{_s(n)} pratiqué{_s(n)} une seule fois.",
        ))
    if sans_serie:
        n = len(sans_serie)
        causes.append(Cause(
            CAUSE_AUCUNE_SERIE, n,
            f"{n} exercice{_s(n)} revu{_s(n)}, mais sans série notée.",
        ))
    if non_rattachees:
        causes.append(Cause(
            CAUSE_NOM_NON_RATTACHE, non_rattachees,
            f"{non_rattachees} occurrence{_s(non_rattachees)} dont le nom "
            f"n'est rattaché à aucun exercice connu.",
        ))

    if not causes:
        # Filet : `any` est vrai mais rien n'explique l'absence de `lead`. On
        # dit l'état plutôt que de rendre un tuple vide — « pas encore
        # possible » sans raison serait exactement le vide silencieux qu'on
        # corrige.
        causes.append(Cause(
            CAUSE_AUCUN_MOUVEMENT, 0,
            "Les séances enregistrées ne portent aucun mouvement comparable.",
        ))
    return tuple(causes)


# ── l'état du corpus de comparaison ────────────────────────────────────────


def _etat(seance, progression: dict[str, Any]) -> str:
    """Ce que le produit SAIT de son propre corpus de comparaison.

    Quatre états, ceux de `zone_exposure`, appliqués à la comparaison :

    * `unknown` — aucune matière du tout ;
    * `partial` — des preuves existent qu'on ne sait pas rattacher ;
    * `known`   — une comparaison est possible ;
    * `zero`    — de la matière, mais rien de comparable, et on le SAIT.
    """
    if seance is None and not progression.get("any"):
        return ETAT_INCONNU
    if progression.get("unresolved"):
        return ETAT_PARTIEL
    if progression.get("lead") is not None:
        return ETAT_CONNU
    return ETAT_ZERO


# ── la précédence ──────────────────────────────────────────────────────────


def construire_debriefing(seance, progression: dict[str, Any]) -> Debrief:
    """LE point d'entrée. Trois booléens, un `if / elif / else`.

    `progression` est **exactement** la sortie de `build_progression_view`. Ce
    module ne la recalcule pas, ne la reformate pas, et ne la trie pas.

    `build_progression_view` garantit la totalité — `lead` vaut `None`, jamais
    `{}`, et ne lève jamais — donc le prédicat du rung 2 est sûr sans défense.
    """
    progression = progression or {}
    etat = _etat(seance, progression)

    signaux = _signaux_nommables(seance)
    if signaux:
        premier = signaux[0]
        exercice = _nom_exercice(seance, getattr(premier, "exercise_code", None))
        autres = len(signaux) - 1
        return DebriefAttention(
            etat=etat,
            libelle=LIBELLE_ATTENTION,
            sr=f"{EN_TETE} — à vérifier : "
               f"{exercice or 'un exercice'}. {premier.message}",
            rule_code=getattr(premier, "rule_code", ""),
            message=getattr(premier, "message", ""),
            exercice=exercice,
            seance_id=getattr(seance, "id", None),
            seance_gabarit=getattr(seance, "template_name_snapshot", None),
            autres=autres,
        )

    lead = progression.get("lead")
    if lead is not None:
        ecarts = [e for e in (lead.get("delta_weight"), lead.get("delta_reps"))
                  if e]
        return DebriefMouvement(
            etat=etat,
            libelle=LIBELLE_MOUVEMENT,
            sr=f"{EN_TETE} — {lead.get('name')} : "
               f"{lead.get('latest')}, contre {lead.get('previous')} avant. "
               + (" ".join(ecarts) if ecarts else ""),
            slug=lead.get("slug", ""),
            nom=lead.get("name", ""),
            dernier_poids=lead.get("latest_weight", ""),
            dernier_reps=lead.get("latest_reps", ""),
            precedent_poids=lead.get("previous_weight", ""),
            precedent_reps=lead.get("previous_reps", ""),
            ecart_poids=lead.get("delta_weight"),
            ecart_reps=lead.get("delta_reps"),
            trace=tuple(lead.get("trace") or ()),
            href=lead.get("href", ""),
        )

    causes = _causes(seance, progression)
    non_rattachees = int(progression.get("unresolved") or 0)
    return DebriefInsuffisant(
        etat=etat,
        libelle=LIBELLE_INSUFFISANT,
        sr=f"{EN_TETE} — comparaison pas encore possible. "
           + " ".join(c.libelle for c in causes),
        causes=causes,
        non_rattachees=non_rattachees,
        noms_non_rattaches=tuple(progression.get("unresolved_names") or ()),
    )
