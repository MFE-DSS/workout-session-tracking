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
) -> ConsoleState:
    """Dérive l'état de la console pour un exercice.

    `rest_signal` vient de `?rest=1`, posé par le serveur après un `nav=stay`.
    `fix_set_id` vient de `?fix=<id>`, posé par le lien de correction. **Les
    deux sont à portée de requête et ne survivent pas au rechargement suivant
    — c'est voulu.**

    ═══════════════════════════════════════════════════════════════════════
    `UI-CP2.1` — L'ÉCHAUFFEMENT CESSE D'ÊTRE UNE PORTE.

    CE QUE L'OPÉRATEUR A VÉCU, en usage réel, et qui a décidé cette tranche :

        « je clique sur sauter l'échauffement, ça passe à la première série ;
          mais si je valide la première série, ça retourne sur l'échauffement.
          Et ça désactive le timer. »

    `UI-CP2.0` avait déjà rendu la progression monotone, ce qui refermait ce
    symptôme précis. **Le fond restait ouvert** : l'échauffement gardait le
    pouvoir de retenir l'exercice, et le seul moyen DURABLE d'en sortir était
    d'y saisir des valeurs — puisque `completed` se dérive de la présence d'un
    poids ou de répétitions.

    L'utilisateur était donc devant un choix que le produit n'a pas à imposer :
    **fabriquer des chiffres, ou rebondir**. Et `SAUTER L'ÉCHAUFFEMENT`, à
    portée de requête, ne survivait pas au rechargement — un bouton qui ne
    tient pas sa promesse.

    LE REMÈDE N'EST PAS DE PERSISTER LE SAUT, C'EST DE RETIRER LA PORTE.
    L'exercice s'ouvre sur sa première série de TRAVAIL. Les échauffements
    restent disponibles et saisissables, jamais bloquants. Il n'y a plus rien
    à sauter — donc plus de bouton pour le faire, et plus jamais de valeur
    obligatoire.

    `Q-C` n'est pas contredite, elle devient **sans objet** : rien n'est
    écrit, parce qu'il n'y a plus d'obstacle à contourner.

    ⚠ `WARMUP` SURVIT, POUR UN SEUL CAS. Un exercice qui n'a QUE des
    échauffements — `work_total == 0` — n'a pas d'autre travail : ses
    échauffements SONT son travail, et l'état reste souverain pour lui. Le
    retirer complètement aurait laissé cet exercice sans état.
    ═══════════════════════════════════════════════════════════════════════
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

    # ═══════════════════════════════════════════════════════════════════════
    # `UI-CP2.0` — LA PROGRESSION EST MONOTONE.
    #
    # L'ordre des branches ci-dessous EST le contrat. L'ancien ordre plaçait
    # l'échauffement en premier, sans condition, et produisait deux défauts
    # mesurés au labo sur une séance réelle :
    #
    #   F1  Un exercice dont les TROIS séries de travail étaient faites, mais
    #       dont un échauffement n'était pas coché, rendait `WARMUP` avec la
    #       commande dominante « PASSER AUX SÉRIES » — vers des séries déjà
    #       faites. `EXERCISE_COMPLETE` n'était JAMAIS atteint, et
    #       « CONTINUER → E2 » n'apparaissait jamais.
    #
    #   F2  Le même verrou avalait `?rest=1` : on pouvait enregistrer une
    #       série de travail et voir l'instrument réclamer l'échauffement.
    #
    # Le chemin est ordinaire, pas exotique : sauter l'échauffement — qui, par
    # décision produit `Q-C`, **n'écrit rien** — puis faire ses séries.
    #
    # ⚠ CE N'EST PAS UN SIMPLE RÉORDONNANCEMENT. `UI-CP2.0` avait rendu la
    # progression monotone : l'échauffement cessait d'être souverain dès que le
    # travail avait commencé.
    #
    # `UI-CP2.1` va au bout, sur constat d'usage réel : **l'échauffement n'est
    # plus jamais une porte**. Il ne retient plus rien, donc il n'y a plus rien
    # à sauter — et plus aucune valeur à saisir pour en sortir.
    # ═══════════════════════════════════════════════════════════════════════

    # 1 — L'EXERCICE EST FINI QUAND SON TRAVAIL EST FINI.
    #     Un échauffement non coché ne retient pas un exercice terminé.
    #     Garde : un exercice SANS série de travail n'a que ses échauffements —
    #     ils sont alors son travail, et cette branche ne doit pas le déclarer
    #     fini avant qu'ils le soient.
    if not pending_works and works:
        return ConsoleState(
            state=EXERCISE_COMPLETE if next_code else LAST_EXERCISE_COMPLETE,
            current_set=None,
            future_sets=[],
            **common,
        )

    # 2 — LE TRAVAIL PASSE AVANT L'ÉCHAUFFEMENT, TOUJOURS.
    #     `REST` n'existe que s'il reste quelque chose à faire après : afficher
    #     « repos » quand l'exercice est fini annoncerait une série qui n'existe
    #     pas. Une série de travail fraîchement validée produit désormais un
    #     repos légitime MÊME si un échauffement reste non résolu.
    if pending_works:
        current, rest = pending_works[0], pending_works[1:]
        return ConsoleState(
            state=REST if rest_signal else CURRENT_SET,
            current_set=current,
            future_sets=rest,
            **common,
        )

    # 3 — LE SEUL CAS OÙ L'ÉCHAUFFEMENT EST ENCORE SOUVERAIN.
    #     Un exercice sans AUCUNE série de travail n'a que ses échauffements :
    #     ils SONT son travail. Sans cette branche, il n'aurait pas d'état.
    if pending_warmups:
        return ConsoleState(
            state=WARMUP,
            current_set=pending_warmups[0],
            future_sets=[],
            **common,
        )

    # 4 — Ni travail restant, ni échauffement restant : l'exercice est fini.
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
        # ⚠ `sl = state.current_set` RETIRÉ (`python:S1854`, et il avait
        # raison). Le libellé citait `sl.set_index` — « VALIDER ÉCHAUFFEMENT
        # 1 » — ; depuis `R6` il nomme une DESTINATION et ne cite plus aucun
        # rang. L'affectation est devenue morte au moment où le libellé a
        # changé, et rien ne le disait : une variable morte se lit comme une
        # variable utile.
        # `stay_norest`, pas `stay` : le repos suit une série de TRAVAIL.
        # Mesuré au navigateur — valider le dernier échauffement avec `stay`
        # faisait démarrer le décompte de repos avant la première série.
        # `D3 = B`, tranché par l'opérateur sur trois variantes rendues à
        # 360 px. Le bouton disait `VALIDER É1` alors que `DF-C` avait retiré
        # les codes `É`/`S` des lignes : plus rien à l'écran ne portait ce nom.
        # Le libellé reprend désormais le mot que le nom accessible emploie
        # déjà — aucun vocabulaire n'est inventé. Mesuré : tient sur une ligne
        # à 360 px, hauteur de bouton inchangée (56 px).
        # `R6` (opérateur, 2026-09-04) — « LE BOUTON, C'EST JAMAIS VALIDER ».
        #
        # Le mot est devenu FAUX, pas seulement encombrant : depuis `R5`, la
        # saisie valide d'elle-même. Un bouton nommé « VALIDER » annonce une
        # étape qui n'existe plus, et laisse croire qu'oublier de l'appuyer
        # perd la série — c'est l'inverse.
        #
        # Ce que le bouton fait réellement : enregistrer ce qui est saisi ET
        # avancer. Il nomme donc sa DESTINATION. Il reste par ailleurs le seul
        # chemin d'enregistrement **sans JavaScript** : le renommer était
        # possible, le supprimer non.
        #
        # ⚠ `Sx_UIV3_02 §4` (amendement B) FIGEAIT ces deux libellés. Ils sont
        # superséde par `R5`/`R6`, arbitrés sur rendu. La garde qui les
        # épinglait est mise à jour dans la même livraison, pas contournée.
        return {
            "label": (
                "PASSER AUX SÉRIES" if state.warmup_done + 1 >= state.warmup_total
                else "ÉCHAUFFEMENT SUIVANT"
            ),
            "sub": None,
            "nav": "stay_norest",
        }
    if kind == CURRENT_SET:
        sl = state.current_set
        # Dernière série de travail : la destination n'est plus « la suivante ».
        # Annoncer une série qui n'existe pas serait pire que l'ancien libellé.
        is_last_work = sl.set_index >= state.work_total
        return {
            "label": "EXERCICE TERMINÉ" if is_last_work else "SÉRIE SUIVANTE",
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
        # ⚠ `UI-CP2` — LE TON REDEVIENT DOMINANT, ET LA PRÉMISSE A CHANGÉ.
        #
        # `DF-B` avait rendu cette sortie SECONDAIRE pour une raison exacte :
        # l'écran portait alors DEUX affordances ambre pour une seule
        # intention — « Commencer S{n} » sur la ligne de la série, et ce
        # bouton pleine largeur juste en dessous. La ligne devenait la
        # commande, celle-ci cessait de rivaliser.
        #
        # A+ retire la bande de séries pendant le repos : la question de cet
        # état est le TEMPS, pas la position dans l'exercice. **Il n'y a donc
        # plus de ligne pour porter la commande**, et un état sans propriétaire
        # d'action dominant n'existe pas dans ce cockpit.
        #
        # La raison de `DF-B` n'est pas contredite — elle est devenue sans
        # objet. Le LIBELLÉ, lui, ne bouge pas : trois gardes l'épinglent, et
        # le changer serait un choix d'écriture que personne n'a demandé.
        return {
            "label": "PASSER LE REPOS",
            "sub": f"S{sl.set_index} →",
            "nav": None,  # lien, pas soumission : rien à enregistrer
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
    # ⚠ `UI-CP2.1` — « SAUTER L'ÉCHAUFFEMENT » EST RETIRÉ, ET SON REMPLAÇANT
    # PART DANS LA MÊME LIVRAISON (`CLAUDE.md §5.3`).
    #
    # Cette sortie existait parce que l'échauffement RETENAIT l'exercice. Elle
    # ne tenait d'ailleurs pas sa promesse : `?skipwarm=1` vivait dans l'URL,
    # donc le saut ne survivait pas au rechargement — constaté en usage réel
    # par l'opérateur, « le CTA ne va nulle part ».
    #
    # Ce qui la remplace n'est pas un autre bouton : **il n'y a plus de porte**.
    # L'exercice s'ouvre sur sa première série de travail, les échauffements
    # restent disponibles au-dessus, et aucune valeur n'est jamais requise pour
    # avancer. Une commande dont l'objet a disparu ne se remplace pas, elle se
    # retire — c'est une commande de moins dans un cockpit qui en comptait
    # treize de trop.
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
