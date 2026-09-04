"""Dérivation de l'état de la console de séance — `Sx_UIV3_02 §4`.

POURQUOI CE MODULE EXISTE
-------------------------
Jusqu'ici la console proposait **deux commandes concurrentes en permanence** :
« Enregistrer la série » et « Enregistrer et passer à E2 ». Mesuré à 390 px,
l'étiquette de la seconde demandait ~180 px dans un bouton de 62 et se
peignait par-dessus la première (`Sx_UIV3_02B §D2`). La coexistence était un
**artefact de réparation**, pas un besoin de deux actions simultanées.

Le remède tranché par la spec : **l'état devient le contrôleur de la
commande**. Ce module calcule cet état.

CE QU'IL N'EST PAS
------------------
**Aucun état n'est persisté.** Il n'y a ni colonne, ni modèle, ni migration :
les six états se déduisent intégralement de `SetLog.completed`, de la position
de l'exercice dans la séance, et de deux paramètres de requête (`rest`,
`fix`). `rest=1` existait déjà — il est émis par le routeur après un
`nav=stay` (`Sb_SESSION_SET_ACTION_01`) ; `fix` est la **seule addition** de
la tranche, et suit exactement la même discipline : portée requête, jamais
écrit, repli sans JS naturel puisque c'est un lien.

Persister l'état de repos ferait de la durée une **affirmation du produit**
alors qu'elle est une suggestion (`Sx_UIV3_04 §1bis C`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# ── les six états, plus rien ─────────────────────────────────────────────

WARMUP = "warmup"
CURRENT_SET = "current_set"
REST = "rest"
CORRECTION = "correction"
EXERCISE_COMPLETE = "exercise_complete"
LAST_EXERCISE_COMPLETE = "last_exercise_complete"

#: Durée de repli affichée à l'état `REST`. **Repli de présentation, jamais
#: une prescription** (`Sx_UIV3_02 §amendement C`). La littérature récente
#: trouve un petit avantage hypertrophique aux repos > 60 s sans avantage
#: clairement détecté au-delà de 90 s. Un `rest_target_seconds` par exercice
#: serait une prescription, donc une feature métier séparée.
REST_FALLBACK_SECONDS = 90


@dataclass(frozen=True)
class ConsoleState:
    """Ce que la console doit rendre, pour un exercice, à cette requête."""

    state: str
    #: `SetLog` sur lequel porte l'action, ou `None` quand l'exercice est fini.
    current_set: Any | None = None
    #: Séries déjà validées, dans l'ordre — rendues compactes.
    past_sets: list = field(default_factory=list)
    #: Séries restantes après la courante — rendues compactes.
    future_sets: list = field(default_factory=list)
    #: Échauffements, séparés des séries de travail.
    warmup_sets: list = field(default_factory=list)
    warmup_done: int = 0
    warmup_total: int = 0
    work_done: int = 0
    work_total: int = 0
    #: Code de l'exercice suivant (`None` sur le dernier).
    next_code: str | None = None
    #: Nom de l'exercice suivant. `R4` (opérateur, 2026-09-04) — « PASSER À E2 »
    #: n'est pas intelligible : un code de position ne dit pas ce qu'on va
    #: faire. Le nom vit ici plutôt que dans le gabarit parce que la commande
    #: est construite ici, et qu'un libellé assemblé à deux endroits diverge.
    next_name: str | None = None
    #: Code de l'exercice précédent (`None` sur le premier).
    prev_code: str | None = None
    rest_seconds: int = REST_FALLBACK_SECONDS

    # ── lectures de commodité pour le gabarit ────────────────────────────

    @property
    def is_correcting(self) -> bool:
        return self.state == CORRECTION

    @property
    def is_resting(self) -> bool:
        return self.state == REST

    @property
    def is_finished(self) -> bool:
        return self.state in (EXERCISE_COMPLETE, LAST_EXERCISE_COMPLETE)

    @property
    def is_last_exercise(self) -> bool:
        return self.next_code is None


def condense_reference(weights_str: str, reps_str: str) -> str | None:
    """« 57.5 / 57.5 / 57.5 kg × 11 / 11 / 11 » → « 57.5 kg × 11 ».

    Le `DeltaReadout` est un PONT, pas un tableau : il répond à « qu'est-ce
    que j'ai fait la dernière fois ? », et trois fois la même valeur ne
    répond pas mieux qu'une. Quand les séries divergent réellement, on garde
    la forme longue — c'est alors une information, pas du bruit.

    Aucun calcul : on ne fait que replier des répétitions littérales. Inventer
    une moyenne ou un « top set » serait produire une donnée que la séance
    précédente n'a jamais affirmée.
    """
    if not weights_str or not reps_str:
        return None
    weights = [w.strip() for w in weights_str.split("/")]
    reps = [r.strip() for r in reps_str.split("/")]
    w = weights[0] if len(set(weights)) == 1 else weights_str
    r = reps[0] if len(set(reps)) == 1 else reps_str
    return f"{w} kg × {r}"


def _split_sets(session_exercise) -> tuple[list, list]:
    """Échauffements et séries de travail, chacun trié par `set_index`.

    Le tri est explicite : l'ordre de `set_logs` vient de la base et n'est pas
    garanti par le contrat de la relation.
    """
    warmups, works = [], []
    for sl in session_exercise.set_logs:
        (warmups if sl.kind == "warmup" else works).append(sl)
    warmups.sort(key=lambda sl: sl.set_index)
    works.sort(key=lambda sl: sl.set_index)
    return warmups, works


def _resolve_correction(works: list, fix_set_id: int | None):
    """La série visée par `fix`, si elle appartient bien à cet exercice.

    Un `fix` pointant ailleurs — série d'un autre exercice, identifiant
    inventé, série jamais validée — est **ignoré silencieusement** plutôt que
    de faire échouer le rendu : un paramètre d'URL est une entrée hostile.
    Corriger une série non validée n'a pas de sens non plus, c'est déjà la
    série courante.
    """
    if fix_set_id is None:
        return None
    for sl in works:
        if sl.id == fix_set_id and sl.completed:
            return sl
    return None


def build_console_state(
    session_exercise,
    *,
    next_code: str | None,
    next_name: str | None = None,
    prev_code: str | None = None,
    rest_signal: bool = False,
    fix_set_id: int | None = None,
    skip_warmup: bool = False,
) -> ConsoleState:
    """Dérive l'état de la console pour un exercice.

    `rest_signal` vient de `?rest=1`, posé par le serveur après un `nav=stay`.
    `fix_set_id` vient de `?fix=<id>`, posé par le lien de correction.
    `skip_warmup` vient de `?skipwarm=1`, posé par la sortie « SAUTER
    L'ÉCHAUFFEMENT ». **Les trois sont à portée de requête et ne survivent pas
    au rechargement suivant — c'est voulu.**

    `Q-C` (opérateur, 2026-09-04) — sauter l'échauffement est une **pure
    navigation** : elle amène à la première série de travail et **n'écrit
    rien**. Marquer les échauffements comme faits fabriquerait des données
    d'entraînement que l'utilisateur n'a pas produites, et un échauffement
    sauté n'est pas un échauffement fait.
    """
    warmups, works = _split_sets(session_exercise)

    warmup_done = sum(1 for sl in warmups if sl.completed)
    work_done = sum(1 for sl in works if sl.completed)

    pending_warmups = [sl for sl in warmups if not sl.completed]
    pending_works = [sl for sl in works if not sl.completed]
    done_works = [sl for sl in works if sl.completed]

    common = {
        "past_sets": done_works,
        "warmup_sets": warmups,
        "warmup_done": warmup_done,
        "warmup_total": len(warmups),
        "work_done": work_done,
        "work_total": len(works),
        "next_code": next_code,
        "next_name": next_name,
        "prev_code": prev_code,
    }

    # `CORRECTION` prime sur tout le reste : l'utilisateur a explicitement
    # demandé à revenir sur une série déjà validée, et cette demande ne doit
    # pas être arbitrée par l'avancement de l'exercice.
    corrected = _resolve_correction(works, fix_set_id)
    if corrected is not None:
        # `future_sets` ne contient QUE ce qui reste à faire.
        #
        # La première écriture prenait « toutes les séries sauf la corrigée »,
        # ce qui y remettait les séries DÉJÀ validées — lesquelles figurent
        # aussi dans `past_sets`. Une série terminée était alors rendue DEUX
        # FOIS : une fois en `✓`, une fois en `○`, avec le même `id` d'ancre
        # et les mêmes `name` de champs masqués.
        #
        # Trouvé par le moteur Sonar (`Web:S7930`, identifiant dupliqué), pas
        # par les 34 gardes neuves ni par les 1178 tests du broad sweep :
        # aucun ne comparait l'état `CORRECTION` à deux séries déjà validées.
        return ConsoleState(
            state=CORRECTION,
            current_set=corrected,
            future_sets=list(pending_works),
            **common,
        )

    # `Q-C` — SAUTER L'ÉCHAUFFEMENT. Signal de requête, jamais un état écrit :
    # on n'entre dans cette branche que s'il reste une série de TRAVAIL à
    # faire. Sans ce garde, sauter l'échauffement d'un exercice dont le travail
    # est terminé afficherait `CURRENT_SET` sans série courante.
    #
    # Les échauffements restent `pending` en base : ils ne sont pas marqués
    # faits, et l'utilisateur peut y revenir en rechargeant sans le paramètre.
    if pending_warmups and not (skip_warmup and pending_works):
        return ConsoleState(
            state=WARMUP,
            current_set=pending_warmups[0],
            future_sets=pending_works,
            **common,
        )

    if pending_works:
        current, rest = pending_works[0], pending_works[1:]
        # `REST` n'existe que s'il reste quelque chose à faire après : afficher
        # « repos » quand l'exercice est fini annoncerait une série qui n'existe
        # pas.
        return ConsoleState(
            state=REST if rest_signal else CURRENT_SET,
            current_set=current,
            future_sets=rest,
            **common,
        )

    return ConsoleState(
        state=EXERCISE_COMPLETE if next_code else LAST_EXERCISE_COMPLETE,
        current_set=None,
        future_sets=[],
        **common,
    )


# ── libellés de commande, figés par l'opérateur ──────────────────────────
#
# `Sx_UIV3_02 §4` (amendement B) fige les libellés ; les amendements Q2 et Q4
# du 2026-08-19 ajoutent les sorties secondaires. Aucune autre formulation
# n'est autorisée, et `Valider · E2` est définitivement supprimé : il faisait
# porter à une commande de SÉRIE la destination d'un EXERCICE.


def command_for(state: ConsoleState) -> dict:
    """Commande dominante et sous-titre, pour un état donné.

    Le sous-titre porte la **conséquence** de l'action, jamais une répétition
    du libellé : c'est lui qui remplace le libellé d'état empilé au-dessus du
    bouton dans le concept C (`Sx_UIV3_02 §6`).
    """
    kind = state.state
    if kind == WARMUP:
        sl = state.current_set
        # `stay_norest`, pas `stay` : le repos suit une série de TRAVAIL.
        # Mesuré au navigateur — valider le dernier échauffement avec `stay`
        # faisait démarrer le décompte de repos avant la première série.
        # `D3 = B`, tranché par l'opérateur sur trois variantes rendues à
        # 360 px. Le bouton disait `VALIDER É1` alors que `DF-C` avait retiré
        # les codes `É`/`S` des lignes : plus rien à l'écran ne portait ce nom.
        # Le libellé reprend désormais le mot que le nom accessible emploie
        # déjà — aucun vocabulaire n'est inventé. Mesuré : tient sur une ligne
        # à 360 px, hauteur de bouton inchangée (56 px).
        return {
            "label": f"VALIDER ÉCHAUFFEMENT {sl.set_index}",
            "sub": None,
            "nav": "stay_norest",
        }
    if kind == CURRENT_SET:
        sl = state.current_set
        return {
            "label": f"VALIDER SÉRIE {sl.set_index}",
            "sub": f"→ repos {state.rest_seconds} s",
            "nav": "stay",
        }
    if kind == REST:
        sl = state.current_set
        # `DF-B` — LA SORTIE RESTE, MAIS CESSE D'ÊTRE DOMINANTE.
        #
        # Mesuré au rendu : pendant le repos, l'écran portait DEUX affordances
        # ambre pour une seule intention — « Commencer S{n} » sur la ligne de
        # la série, et ce bouton pleine largeur juste en dessous. C'est le
        # « bouton de trop » relevé en dogfood.
        #
        # La ligne de la série devient la commande — c'est là que le regard
        # est, et « je commence S{n} » est l'intention réelle. Ce bouton reste
        # disponible comme sortie explicite, au ton secondaire : il ne
        # disparaît pas, il cesse de rivaliser.
        # Le LIBELLÉ ne bouge pas : trois gardes l'épinglent, et le changer
        # serait un choix d'écriture que personne n'a demandé. Seul le TON
        # change — c'est la compétition visuelle qu'on retire, pas la sortie.
        return {
            "label": "PASSER LE REPOS",
            "sub": f"S{sl.set_index} →",
            "nav": None,  # lien, pas soumission : rien à enregistrer
            "tone": "muted",
        }
    if kind == CORRECTION:
        # Corriger une série passée n'est pas exécuter une série : aucun repos
        # ne démarre, sinon l'utilisateur qui rectifie une faute de frappe se
        # verrait imposer 90 secondes.
        return {
            "label": "ENREGISTRER LA CORRECTION",
            "sub": None,
            "nav": "stay_norest",
        }
    if kind == EXERCISE_COMPLETE:
        # ⚠ LIBELLÉ FIGÉ par `Sx_UIV3_02 §4` (amendement B), et gardé par
        # `test_exactly_one_dominant_command_per_state`.
        #
        # L'argument de `R4` — « un code de position ne dit pas ce qu'on va
        # faire » — s'applique tout autant ici. Mais l'opérateur a tranché sur
        # `PASSER À E2`, la sortie SECONDAIRE. Étendre par analogie à un
        # libellé figé serait amender une spec versionnée sans mandat, ce que
        # `CLAUDE.md §4` interdit. Reporté, et posé en question.
        return {
            "label": f"CONTINUER → {state.next_code}",
            "sub": None,
            "nav": "next",
        }
    return {"label": "ALLER AU BILAN", "sub": None, "nav": "next"}


def secondary_for(state: ConsoleState) -> list[dict]:
    """Sorties secondaires — jamais vides sauf à l'ultime état.

    **Q2, tranché par l'opérateur** : un exercice incomplet peut être quitté à
    tout moment. Le produit ne force jamais la complétion. Retirer cette
    capacité serait une soustraction, et `CLAUDE.md §5.3` l'interdit.
    """
    kind = state.state
    if kind == CORRECTION:
        # `RETIRER CETTE SÉRIE` rend INTENTIONNEL ce qui n'était qu'un effet de
        # bord : `completed` est dérivé de la présence de weight ou reps, donc
        # vider les deux champs dé-complétait déjà la série — silencieusement.
        # La sémantique ne change pas (Q3), elle devient nommée.
        return [
            {"label": "RETIRER CETTE SÉRIE", "kind": "remove"},
            {"label": "annuler", "kind": "cancel"},
        ]
    if kind == LAST_EXERCISE_COMPLETE:
        return []
    if kind == EXERCISE_COMPLETE:
        return [{"label": "revoir l'exercice", "kind": "review"}]
    if kind == REST:
        return [
            {"label": "−15 s", "kind": "rest_minus"},
            {"label": "+15 s", "kind": "rest_plus"},
        ]
    # `WARMUP` et `CURRENT_SET` : l'exercice est incomplet, la sortie existe.
    out = []
    # `Q-C` — la sortie d'échauffement précède la sortie d'exercice : quand on
    # est en échauffement, « je ne m'échauffe pas ici » est bien plus fréquent
    # que « je saute tout l'exercice ».
    if kind == WARMUP and state.work_done < state.work_total:
        out.append({"label": "SAUTER L'ÉCHAUFFEMENT", "kind": "skip_warmup"})
    if state.next_code:
        # `R4` / `Q-B` — « PASSER À E2 » ne dit pas ce qu'on va faire. Le
        # libellé nomme l'INTENTION, la sous-ligne nomme la DESTINATION : un
        # nom comme « Neutral Grip Shoulder Press machine » casse un libellé
        # et devient illisible tronqué.
        out.append({
            "label": "EXERCICE SUIVANT",
            "sub": state.next_name or state.next_code,
            "kind": "skip",
        })
    else:
        out.append({"label": "ALLER AU BILAN", "kind": "skip"})
    # « Enregistrer et revenir » — capacité PRÉEXISTANTE (`nav=prev`).
    # Elle n'est pas couverte par la navigation par ancres de Q1 : un lien
    # ne sauvegarde pas, et l'utilisateur qui vient de saisir une valeur la
    # perdrait. La retirer serait une soustraction (`CLAUDE.md §5.3`).
    if state.prev_code:
        out.append({"label": f"← {state.prev_code}", "kind": "back"})
    return out
