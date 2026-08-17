"""Sb_ATLAS_TECHNICAL_GUARDS_01 — restitution des garde-fous, pas collecte.

Le cockpit remonte désormais le premier cue d'exécution de l'atlas dans le
résumé de la disclosure machine, donc lisible SANS ouvrir. Ces gardes tiennent
les quatre choses qui pourraient dériver : la source (l'atlas, pas un
hardcode), l'absence de collecte, le wording non médical, et la géométrie que
les deux tranches précédentes ont gagnée.
"""
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
        r'<span class="machine-panel__lead-cue">(.*?)</span>', src, re.DOTALL)
    assert match, "lead cue not rendered"
    body = match.group(1).strip()
    assert body == "{{ _m.execution_cues[0] }}", (
        f"the lead cue must be read from the atlas, found {body!r}"
    )


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
    start = src.find("machine-panel__lead-cue")
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
    """Le cue vit dans un `<summary>` natif : il s'affiche sans ouvrir la
    disclosure et sans JS. Aucun script n'est requis pour le lire."""
    src = CARD.read_text(encoding="utf-8")
    start = src.find("machine-panel__lead-cue")
    summary_open = src.rfind("<summary", 0, start)
    summary_close = src.find("</summary>", start)
    assert summary_open != -1, "no <summary> before the lead cue"
    assert summary_close != -1, "no </summary> after the lead cue"
    assert summary_open < start < summary_close, (
        "the lead cue must sit inside the <summary> so it is visible while "
        "the disclosure is closed"
    )
    assert "addEventListener" not in src


def test_the_machine_panel_stays_a_native_details():
    src = CARD.read_text(encoding="utf-8")
    assert '<details class="machine-panel">' in src, (
        "the exact class contract is pinned by test_machine_atlas_surface"
    )


# ───────── A2 / géométrie — le cue ne coûte rien au-dessus de la console ─────


def test_the_cue_is_not_rendered_above_the_console():
    """La contrainte mesurée : au-dessus de la console, même sur une ligne de
    20 px, le cue poussait les champs de la série courante de 497 à 520 px et
    `elementFromPoint` cessait de les retourner — ils passaient derrière la
    barre d'action collante. L'atlas est la SOURCE, pas la POSITION.
    """
    src = CARD.read_text(encoding="utf-8")
    cue = src.find("machine-panel__lead-cue")
    console = src.find("session-focus__console-list")
    assert cue != -1, "lead cue not rendered"
    assert console != -1, "console list not rendered"
    assert console < cue, (
        "the lead cue must render after the logging console; above it, it "
        "occludes the current set inputs at 360x640"
    )
