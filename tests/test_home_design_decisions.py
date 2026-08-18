"""DESIGN_DECISIONS_HOME_UIV2_01 — le relevé de décisions Accueil, gardé.

POURQUOI CES TESTS EXISTENT
---------------------------
Un relevé de décisions validées qui vit dans un fichier **non suivi par git**
n'existe pas : il disparaît au premier nettoyage, et tout le travail de
brainstorm avec lui. Ce document a passé une journée dans cet état.

Deux protections, volontairement légères — aucune ne préjuge de l'implémentation :

1. le document est présent et porte encore ses cinq décisions ;
2. **l'interdit de D2 est appliqué tout de suite** — aucune surface applicative
   ne revendique « Recommandé IA ». C'est la seule décision exécutable avant
   build, parce qu'elle interdit quelque chose plutôt que d'exiger quelque chose.

Statut du chantier : `DOCUMENTED — NOT BUILT`. Ces tests ne vérifient pas que
l'Accueil a changé — il n'a pas changé, et un test qui l'exigerait serait faux.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "DESIGN_DECISIONS_HOME_UIV2.md"
APP = ROOT / "app"

DECISIONS = ("D1", "D2", "D3", "D4", "D5")

#: D2 — the engine is deterministic and explainable; claiming AI would be a lie.
FORBIDDEN_ORIGIN_CLAIMS = (
    "recommandé ia",
    "recommande ia",
    "recommandé par l'ia",
    "suggéré par l'ia",
    "propulsé par l'ia",
    "powered by ai",
    "ai-powered",
)


def _app_text_surfaces() -> list[Path]:
    """Templates and Python that can put words in front of a user."""
    return [
        p for p in list(APP.rglob("*.html")) + list(APP.rglob("*.py"))
        if p.is_file()
    ]


# ───────────── the record survives ─────────────

def test_the_decision_record_is_tracked_by_git():
    """The whole point of the sprint: an untracked decision record is no record."""
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(DOC.relative_to(ROOT))],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, (
        "docs/DESIGN_DECISIONS_HOME_UIV2.md is not tracked by git"
    )


def test_the_decision_record_exists_and_is_not_empty():
    assert DOC.is_file()
    assert len(DOC.read_text(encoding="utf-8")) > 2000


def test_every_validated_decision_is_still_present():
    doc = DOC.read_text(encoding="utf-8")
    for decision in DECISIONS:
        assert f"## {decision} " in doc, f"decision {decision} disappeared from the record"


def test_the_record_states_it_is_not_built():
    doc = DOC.read_text(encoding="utf-8")
    assert "DOCUMENTED — NOT BUILT" in doc
    assert "Aucune de ces décisions n'est implémentée" in doc


def test_the_record_keeps_the_deletion_targets_locatable():
    """D4 is only actionable later if its targets stay written down."""
    doc = DOC.read_text(encoding="utf-8")
    assert "Aucune séance active" in doc
    assert "Cette semaine" in doc
    assert "index.html:48" in doc


# ───────────── D2, enforced now ─────────────

def test_no_surface_claims_the_recommendation_comes_from_ai():
    """D2's hard interdiction. The engine is `zero-ML`; the claim would be false."""
    offenders: list[str] = []
    for path in _app_text_surfaces():
        lowered = path.read_text(encoding="utf-8").lower()
        for claim in FORBIDDEN_ORIGIN_CLAIMS:
            if claim in lowered:
                offenders.append(f"{path.relative_to(ROOT)}: {claim!r}")
    assert offenders == [], f"D2 violated — AI origin claimed: {offenders}"


def test_the_record_states_why_the_ai_claim_is_forbidden():
    """A ban without its reason gets reversed by the next person."""
    doc = DOC.read_text(encoding="utf-8")
    assert "zero-ML" in doc
    assert "Aucune revendication d'IA" in doc
