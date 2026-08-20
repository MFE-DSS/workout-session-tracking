"""`UIV3_VISUAL_BASELINE_01` — gardes du contrat visuel et de l'environnement.

CE QUE CES GARDES EMPÊCHENT
----------------------------
1. **Qu'une capture devienne un contrat de design là où la surface est
   seulement héritée.** Sans le découpage par souveraineté, `B9` gèlerait
   l'architecture de Profile et Library — cinq surfaces déjà programmées pour
   une refonte `UX4` — et la prochaine tranche se battrait contre ses propres
   captures.

2. **Qu'une référence produite sur un portable devienne canonique.** Une
   capture dépend du système, du navigateur, des polices et du matériel :
   comparer un rendu macOS à un Chromium Linux teste la rastérisation, pas le
   design.

3. **Qu'un échec visuel souverain soit résolu en régénérant la référence.**
   Remplacer un golden est une **décision produit**, pas une commande.

4. **Qu'un plancher accepté soit raboté sans que rien ne le dise.**
   `TERMINER LA SÉANCE` est passée de 56 à 44 px sous une garde verte.
"""
from __future__ import annotations

from scripts.geometry_manifest import SOVEREIGN, TRANSITIONAL, UTILITY
from scripts.visual_contract import (
    A11Y,
    FUNCTIONAL,
    GEOMETRY,
    LEGACY_REFERENCE_FLAG,
    NO_SHRINK,
    PIXEL,
    PROTECTED_FLOORS,
    SOVEREIGN_PROMOTION_EVIDENCE,
    TARGETS,
    floor_violations,
    is_blocking,
    is_evidence_only,
    promotion_blockers,
    screenshot_flags,
    status_of,
)
from scripts.visual_env import (
    COMPARED_FIELDS,
    ENV_VERSION,
    REQUIRES_PINNED_DEPENDENCY,
    VISUAL_ENV_V1,
    EnvironmentStamp,
    may_promote_to_canonical,
    stamp_mismatches,
)


def _stamp(**kw) -> EnvironmentStamp:
    """Un tampon CONFORME par défaut ; chaque test n'en dégrade qu'un champ."""
    base = {f: getattr(VISUAL_ENV_V1, f) for f in COMPARED_FIELDS}
    base.update(kw)
    return EnvironmentStamp(**base)


# ───────────────── la capture n'est un contrat que si la surface l'est ──────


def test_only_sovereign_surfaces_have_a_blocking_pixel_gate():
    """**La décision centrale de B9.**

    Sans elle, la baseline transforme la dette visible en contrat."""
    assert is_blocking("home", PIXEL) is True
    assert is_blocking("session-active", PIXEL) is True
    for surface in ("profile", "library", "progress", "dashboard", "history"):
        assert is_blocking(surface, PIXEL) is False, surface


def test_transitional_surfaces_keep_every_mechanical_gate():
    """Retirer le gate pixel ne veut pas dire ne plus rien garder. Ce qui
    reste bloquant est ce qui ne présume RIEN de l'architecture future."""
    for gate in (GEOMETRY, TARGETS, A11Y, FUNCTIONAL, NO_SHRINK):
        assert is_blocking("profile", gate) is True, gate
        assert is_blocking("library", gate) is True, gate


def test_a_transitional_screenshot_is_evidence_not_contract():
    assert is_evidence_only("library", PIXEL) is True
    assert is_evidence_only("home", PIXEL) is False


def test_a_transitional_capture_declares_itself_legacy():
    """`legacy_reference = True` se lit « voici l'état de départ », pas
    « voici le design à préserver »."""
    assert screenshot_flags("profile")[LEGACY_REFERENCE_FLAG] is True
    assert screenshot_flags("home")[LEGACY_REFERENCE_FLAG] is False


def test_an_unknown_surface_never_gets_a_blocking_pixel_gate():
    """Un oubli d'inscription ne doit pas fossiliser une surface."""
    assert status_of("surface-jamais-inscrite") == TRANSITIONAL
    assert is_blocking("surface-jamais-inscrite", PIXEL) is False
    assert is_blocking("surface-jamais-inscrite", TARGETS) is True


def test_utility_surfaces_get_no_artistic_pixel_contract():
    assert status_of("login") == UTILITY
    assert is_blocking("login", PIXEL) is False
    assert is_blocking("login", A11Y) is True


def test_every_status_declares_both_blocking_and_evidence_sets():
    """Un statut sans entrée lèverait un `KeyError` au moment le plus
    coûteux : pendant une CI."""
    from scripts.visual_contract import BLOCKING_GATES, EVIDENCE_ARTIFACTS
    for status in (SOVEREIGN, TRANSITIONAL, UTILITY):
        assert status in BLOCKING_GATES
        assert status in EVIDENCE_ARTIFACTS


# ───────────────── l'environnement canonique ─────────────────


def test_the_environment_contract_is_versioned():
    assert ENV_VERSION == "VISUAL_ENV_V1"
    assert VISUAL_ENV_V1.version == ENV_VERSION


def test_a_matching_stamp_reports_no_mismatch():
    assert stamp_mismatches(_stamp()) == []


def test_a_different_chromium_is_a_mismatch():
    """Une version de navigateur différente change la rastérisation. C'est
    exactement ce qui transformerait chaque golden en bruit."""
    assert stamp_mismatches(_stamp(chromium="150.0.0.0")) != []


def test_a_macos_run_is_a_mismatch():
    """Les références officielles naissent dans l'environnement canonique ;
    une capture locale reste informative."""
    assert stamp_mismatches(_stamp(platform="darwin")) != []


def test_a_different_device_scale_factor_is_a_mismatch():
    assert stamp_mismatches(_stamp(device_scale_factor=1)) != []


def test_promotion_is_refused_while_a_dependency_is_unpinned():
    """**Le blocage réel de B9, nommé plutôt que contourné.**

    `pyproject.toml` déclare `playwright>=1.40` — une plage ouverte. Tant
    qu'elle tient, « ça correspond aujourd'hui » ne dit rien de demain, et
    aucune référence ne peut être canonique. Un tampon parfait ne suffit pas.
    """
    ok, reasons = may_promote_to_canonical(_stamp())
    assert ok is False
    assert reasons, "un refus doit dire POURQUOI"
    assert any("playwright" in r for r in reasons)


def test_the_open_range_blocker_is_declared_not_merely_known():
    """Un obstacle connu mais non écrit disparaît au premier changement de
    session."""
    assert REQUIRES_PINNED_DEPENDENCY
    joined = " ".join(REQUIRES_PINNED_DEPENDENCY)
    assert "playwright" in joined
    assert "ubuntu-latest" in joined


def test_the_environment_pins_everything_a_screenshot_depends_on():
    """Chacun de ces champs déplace des pixels. En omettre un, c'est laisser
    une variable libre dans une comparaison qu'on prétend déterministe."""
    for field_name in ("playwright", "chromium", "platform",
                       "device_scale_factor", "locale", "timezone",
                       "color_scheme", "reduced_motion", "font_stack",
                       "widths", "fixture"):
        assert getattr(VISUAL_ENV_V1, field_name), field_name


# ───────────────── gouvernance des références ─────────────────


def test_a_sovereign_baseline_cannot_be_replaced_without_evidence():
    """Régénérer une référence pour verdir un échec, c'est effacer la
    question. Sur une surface souveraine, c'est une décision produit."""
    missing = promotion_blockers("home", {})
    assert set(missing) == set(SOVEREIGN_PROMOTION_EVIDENCE)


def test_a_sovereign_baseline_may_be_replaced_with_full_evidence():
    complete = dict.fromkeys(SOVEREIGN_PROMOTION_EVIDENCE, "fourni")
    assert promotion_blockers("home", complete) == []


def test_partial_evidence_names_exactly_what_is_missing():
    """« Refusé » sans motif fait deviner. On nomme les pièces manquantes."""
    partial = {"before": "x", "after": "y"}
    assert set(promotion_blockers("session-active", partial)) == {
        "decision_ref", "geometry_delta", "human_verdict"}


def test_a_transitional_reference_may_be_refreshed_during_a_redesign():
    """Elle documente l'état, elle ne le gouverne pas."""
    assert promotion_blockers("library", {}) == []


# ───────────────── planchers dominants protégés ─────────────────


def test_the_terminate_action_floor_is_declared_with_its_history():
    spec = PROTECTED_FLOORS["session-review-terminate"]
    assert spec["min_height_px"] == 56
    assert spec["label"] == "TERMINER LA SÉANCE"
    assert spec["why"], "un plancher sans motif finit par être abaissé"


def test_a_regression_below_the_accepted_floor_is_reported():
    assert floor_violations({"session-review-terminate": 44.0}) != []


def test_the_accepted_floor_itself_passes():
    assert floor_violations({"session-review-terminate": 56.0}) == []


def test_a_floor_that_stopped_being_measured_is_reported():
    """Un plancher qu'on ne mesure plus est un plancher qu'on ne garde plus —
    et le silence ressemble exactement au succès."""
    violations = floor_violations({})
    assert violations
    assert "NON MESURÉ" in violations[0]
