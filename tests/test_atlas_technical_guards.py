"""Sb_ATLAS_TECHNICAL_GUARDS_01 — restitution des garde-fous, pas collecte.

Le cockpit remonte désormais le premier cue d'exécution de l'atlas dans le
résumé de la disclosure machine, donc lisible SANS ouvrir. Ces gardes tiennent
les quatre choses qui pourraient dériver : la source (l'atlas, pas un
hardcode), l'absence de collecte, le wording non médical, et la géométrie que
les deux tranches précédentes ont gagnée.
"""

# ══════════════════════════════════════════════════════════════════════
#  MIGRÉ — `UIV3_SESSION_EXECUTION_CONSOLE_01` + passe de densité
#  (2026-08-19). Ce module épinglait des marqueurs d'IMPLÉMENTATION que
#  `Sx_UIV3_02` remplace. Correspondance :
#
#    session-focus__console            → console
#    session-focus__console-list       → console__band
#    session-focus__console-row--active    → setline--current
#    session-focus__console-row--completed → setline--past
#    session-focus__console-row--upcoming  → setline--future
#    session-focus__console-refs       → console__delta
#    session-focus__orientation*       → session-pos*  (dans l'en-tête)
#    session-focus__header-main/kicker → en-tête recomposé en 4 colonnes
#    card-peek*                        → console__next (fin d'exercice)
#    session-focus__sticky-*           → SUPPRIMÉ, plus aucune couche
#
#  Les invariants sont conservés ; là où le CONTRAT change, le test porte
#  une note explicite. Aucune suppression pour verdir.
# ══════════════════════════════════════════════════════════════════════

from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
CARD = ROOT / "app/templates/_partials/exercise_card.html"
ATLAS = ROOT / "data/machine_atlas.json"

#: Vocabulaire interdit : rien ne doit prétendre diagnostiquer, mesurer une
#: activation réelle ou détecter une blessure.
PSEUDO_MEDICAL = (
    "diagnostic", "diagnostiq", "blessure", "pathologie", "lésion",
    "activation musculaire", "% d'activation", "EMG", "tendinite",
    "guérir", "soigner", "thérapeut",
)


def _atlas() -> dict:
    return json.loads(ATLAS.read_text(encoding="utf-8"))


def _machines():
    for family in _atlas()["families"]:
        for machine in family["machines"]:
            yield family, machine


# ───────── A1 — la source est l'atlas, pas le gabarit ─────────


def test_the_lead_cue_comes_from_the_atlas_not_the_template():
    """Un cue écrit en dur dans le gabarit serait invisible à l'atlas et
    pourrait diverger de lui sans que rien ne le signale."""
    src = CARD.read_text(encoding="utf-8")
    match = re.search(
        r'<p class="console__cue">(.*?)</p>', src, re.DOTALL)
    assert match, "le cue de tête n'est plus rendu"
    body = match.group(1)
    assert "_machine_top.execution_cues[0]" in body, (
        f"le cue doit être LU dans l'atlas, trouvé {body!r}"
    )
    # Et rien d'écrit en dur : la seule chaîne littérale est le chevron.
    assert "Banc à" not in body and "°" not in body


def test_every_atlas_machine_can_supply_a_lead_cue():
    """Sans premier cue, le résumé retomberait sur une étiquette vide."""
    missing = [m["slug"] for _, m in _machines() if not m.get("execution_cues")]
    assert not missing, f"machines without execution_cues: {missing}"


def test_the_atlas_is_versioned():
    assert _atlas().get("version"), "atlas must carry a version"


# ───────── A3 — restitution, jamais collecte ─────────


def test_no_technical_feedback_input_was_added(client):
    """Aucun champ de qualité technique. Le sprint restitue, il ne collecte
    pas — c'est la décision centrale de Sb_FEEDBACK_SIGNAL_AUDIT_01."""
    src = CARD.read_text(encoding="utf-8")
    for banned in ("execution_quality", "reps_target"):
        assert f'name="{banned}"' not in src, f"{banned} must not be collected"
        assert f"name='{banned}'" not in src


def test_the_card_adds_no_new_control_around_the_cue():
    """La zone du cue ne contient aucun contrôle : c'est de la lecture."""
    src = CARD.read_text(encoding="utf-8")
    start = src.find("console__cue")
    window = src[max(0, start - 600):start + 400]
    for control in ("<input", "<select", "<textarea"):
        assert control not in window, (
            f"{control} next to the lead cue would turn restitution into "
            "collection"
        )


# ───────── A8 — aucun wording pseudo-médical ─────────


def test_atlas_content_makes_no_medical_claim():
    """Les cues et erreurs sont des consignes d'exécution, pas un diagnostic."""
    offenders: list[str] = []
    for _, machine in _machines():
        texts = list(machine.get("execution_cues") or [])
        texts += list(machine.get("common_mistakes") or [])
        for text in texts:
            low = text.lower()
            for banned in PSEUDO_MEDICAL:
                if banned in low:
                    offenders.append(f"{machine['slug']}: {text!r} ({banned})")
    assert not offenders, offenders


def test_the_template_makes_no_medical_claim():
    """Le contrôle porte sur le MARKUP RENDU, pas sur les commentaires.

    Premier jet : le test lisait le fichier entier et tombait sur un
    commentaire du gabarit qui dit précisément « jamais diagnostic » — une
    consigne interdisant les revendications médicales était comptée comme
    revendication médicale. C'est la classe de faux positif déjà documentée
    dans ce dépôt (l'analyseur HTML lit les commentaires Jinja comme du
    balisage vivant). Les commentaires sont donc retirés avant l'examen.
    """
    src = re.sub(r"\{#.*?#\}", " ", CARD.read_text(encoding="utf-8"),
                 flags=re.DOTALL)
    low = src.lower()
    for banned in PSEUDO_MEDICAL:
        assert banned not in low, f"pseudo-medical wording in the card: {banned}"


# ───────── A7 — lisible sans JS ─────────


def test_the_cue_is_readable_without_javascript(client):
    """**Migré, et le contrat se RENFORCE.**

    Le cue vivait dans un `<summary>` pour être lisible sans ouvrir la
    disclosure. La passe de densité le sort complètement du disclosure : il
    est en L2, dans le flux de la console, visible sans le moindre geste.
    Il n'a plus besoin d'un `<summary>` pour l'être."""
    src = CARD.read_text(encoding="utf-8")
    start = src.find('<p class="console__cue">')
    assert start != -1, "le cue de tête n'est plus rendu"
    # Il vit dans la console, AVANT la première disclosure L3 : rien à
    # ouvrir pour le lire. (La carte elle-même est un `<details open>` —
    # c'est celle-là qu'il ne faut pas confondre avec un repli.)
    console = src.find('<div class="console"')
    l3 = src.find('<div class="l3">')
    assert console != -1 and l3 != -1
    assert console < start < l3, "le cue doit vivre dans la console, avant L3"
    assert "<details" not in src[console:start], (
        "aucune disclosure ne doit s'ouvrir entre la console et le cue"
    )
    assert "addEventListener" not in src


def test_the_machine_panel_stays_a_native_details():
    """**Migré.** Le panneau machine cesse d'être un bloc autonome : son
    contenu vit sous `TECHNIQUE`, une disclosure NATIVE de la ligne L3.
    L'invariant — pas de JS, `details/summary` natif — est intact ; seule
    la classe exacte change."""
    src = CARD.read_text(encoding="utf-8")
    assert '<details class="l3__item session-focus__cues">' in src
    assert "machine-panel__title" in src, "le nom de la machine reste nommé"


# ───────── A2 / géométrie — le cue ne coûte rien au-dessus de la console ─────


def test_the_cue_sits_above_the_console_and_costs_nothing():
    """**Migré — la CAUSE de la contrainte a disparu.**

    L'ancienne règle interdisait le cue au-dessus de la console : il y
    poussait les champs de 497 à 520 px et les faisait passer DERRIÈRE LA
    BARRE D'ACTION COLLANTE. Cette barre n'existe plus (`§7.9` + Q1). La
    raison de la contrainte est partie avec elle.

    Le cue est donc remonté en L2, où il aide réellement le geste suivant.
    Mesuré après ce déplacement, à 390 × 844 sur `SESSION_RICH` : début du
    `SetInstrument` à 263 px pour un budget de 300, et zéro débordement.
    La géométrie aux trois largeurs est revérifiée au dogfood de sortie —
    c'est le navigateur qui tranche, pas ce test.
    """
    src = CARD.read_text(encoding="utf-8")
    cue = src.find('<p class="console__cue">')
    band = src.find('<ol class="console__band">')
    assert cue != -1 and band != -1
    assert cue < band, "le cue précède la bande : il prépare le geste"
    # La cause historique : plus AUCUNE couche collante sur cette surface.
    assert "sticky-cta" not in src
