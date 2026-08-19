"""Source-policy regression tests — Sb_ASSET_03B.2R BodyParts3D source-contract reset.

Stable semantic assertions on the versioned doctrine (not brittle whole-document
snapshots). Guards that the BodyParts3D-primary reset, the proven segmentation
facts and the governance gates cannot silently regress, and that no raw binary
source enters Git.
"""
from __future__ import annotations

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SPEC = DOCS / "strategy" / "Sb_ASSET_03B_2R_BODYPARTS3D_SOURCE_RESET_SPEC.md"
STRATEGY = DOCS / "production" / "muscle-focus" / "AUREN_MUSCLE_FOCUS_SOURCE_STRATEGY.md"
LEDGER = DOCS / "production" / "muscle-focus" / "AUREN_MUSCLE_FOCUS_SOURCE_LEDGER.md"


def _spec() -> str:
    return SPEC.read_text(encoding="utf-8").lower()


def _strategy() -> str:
    return STRATEGY.read_text(encoding="utf-8").lower()


def test_reset_spec_exists():
    assert SPEC.is_file(), "corrective source-reset spec must exist"


def test_bodyparts3d_is_primary_derivation():
    s = _spec()
    assert "bodyparts3d" in s and "primary derivation" in s
    assert "primary derivation: bodyparts3d" in s


def test_servier_superseded_for_body_fitting():
    assert "superseded for body-fitting geometry" in _spec()
    # history preserved in the strategy doc (Servier still documented, labelled superseded)
    strat = _strategy()
    assert "servier" in strat and "superseded" in strat


def test_bodyparts3d_not_canonical_truth_and_adult_male():
    s = _spec()
    assert "vérité anatomique canonique" in s  # stated as NOT canonical truth
    assert "adulte" in s  # adult-male reference limitation
    assert "peut contenir des erreurs" in s


def test_professional_claims_not_claimed():
    s = _spec()
    assert "legal clearance: not claimed" in s
    assert "professional anatomical review: not claimed" in s or "anatomical review: required_pending" in s


def test_qualified_anatomical_review_required_and_runtime_blocked():
    s = _spec()
    assert "required_pending" in s
    assert "runtime: blocked" in s


def test_plan_b_human_only_no_free_invention():
    s = _spec()
    assert "human-only" in s
    assert "invention anatomique libre" in s  # "aucune invention anatomique libre"


def test_plan_c_separated_and_unauthorized():
    s = _spec()
    assert "cc by-sa" in s
    assert "non autorisé" in s
    assert "blanchiment" in s  # no whitening into BodyParts3D chain


def test_generative_anatomy_forbidden():
    s = _spec()
    assert "générative" in s and "interdite" in s


def test_pectoralis_whole_functional_visual_partition():
    s = _spec()
    assert "source_mesh_separately_segmented: false" in s
    assert "functional-visual-region" in s


def test_deltoid_source_segmented_terminology_mapping():
    s = _spec()
    assert "source_mesh_separately_segmented: true" in s
    for term in ("clavicular", "acromial", "spinal"):
        assert term in s
    assert "antérieur" in s and "latéral" in s and "postérieur" in s


def test_posterior_modes_not_reversed():
    s = _spec()
    assert "muscle-heads" in s
    assert "grouped-honest" in s


def test_5bis_not_enacted():
    s = _spec()
    assert "5bis" in s and "not enacted" in s


#: Exception ÉTROITE, ouverte par `UIV3_HOME_CAUSAL_COCKPIT`, réversible.
#:
#: La garde vise les SOURCES anatomiques — sa docstring de module dit « no raw
#: binary source enters Git », dans le contexte de `Sb_ASSET_03B.2R` : maillages
#: BodyParts3D, provenance, licence. Les formats de source restent bannis
#: PARTOUT, sans exception.
#:
#: Ce répertoire contient des SORTIES, pas des sources : des captures de notre
#: propre interface, qu'aucune licence tierce ne grève. Elles existent parce que
#: `AUREN_UI_BLUEPRINT §2.3` fixe le rendu par des images versionnées — le
#: programme a déjà dérivé une fois avec des décisions écrites et aucune
#: référence visuelle. Une URL ne versionne rien ; c'est le point.
#:
#: Le plafond est là pour que l'exception ne devienne pas un dépotoir.
UIV3_REFERENCE_DIR = DOCS / "assets" / "uiv3"
UIV3_REFERENCE_MAX_BYTES = 300 * 1024
UIV3_REFERENCE_MAX_FILES = 8


def test_no_raw_binary_source_in_git_docs():
    """Aucune source binaire dans Git. Les formats de source, sans exception."""
    source_formats = (".zip", ".obj", ".blend", ".pdf")
    image_formats = (".png", ".jpg", ".jpeg")
    offenders = []
    for path in DOCS.rglob("*"):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix in source_formats:
            offenders.append(path)
        elif suffix in image_formats and UIV3_REFERENCE_DIR not in path.parents:
            offenders.append(path)
    assert not offenders, f"no raw binary source may be committed under docs/: {offenders}"


def test_the_uiv3_reference_exception_stays_narrow():
    """Une exception sans plafond devient une règle, puis un dépotoir.

    Trois bornes : un seul répertoire, un nombre de fichiers, une taille
    unitaire. Dépasser l'une d'elles fait tomber ce test — c'est-à-dire que
    l'exception doit être **rediscutée**, pas élargie en silence.
    """
    if not UIV3_REFERENCE_DIR.is_dir():
        return
    files = [p for p in UIV3_REFERENCE_DIR.rglob("*") if p.is_file()]
    assert len(files) <= UIV3_REFERENCE_MAX_FILES, (
        f"{len(files)} fichiers de référence — l'exception déborde"
    )
    oversized = [
        f"{p.name} ({p.stat().st_size // 1024} Ko)"
        for p in files
        if p.stat().st_size > UIV3_REFERENCE_MAX_BYTES
    ]
    assert not oversized, f"référence trop lourde pour un dépôt : {oversized}"
    wrong_kind = [p.name for p in files if p.suffix.lower() != ".png"]
    assert not wrong_kind, f"seules des captures PNG sont admises : {wrong_kind}"
