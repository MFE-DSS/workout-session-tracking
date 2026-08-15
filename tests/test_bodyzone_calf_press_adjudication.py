"""Sb_BODYZONE_CALF_PRESS_ADJUDICATION_01 — une correction exacte, et rien d'autre.

Le risque de ce sprint n'est pas la correction : c'est le **dégât collatéral**.
Toucher au classement d'un exercice peut déplacer une zone ailleurs, changer le
tiroir de substitution, ou faire dériver le seed. Les tests portent donc
d'abord sur ce qui **ne doit pas** bouger.
"""
from __future__ import annotations

import pytest

from app.services.body_zone_source import (
    KNOWN_MAPPING_CORRECTIONS,
    PATH_CORRECTION,
    resolve_exercise_zones,
)
from app.services.reference_data_seed import canonical_exercise_referential
from app.services.set_contribution import ContributionRole, exercise_roles

ADJUDICATED = "Calf press leg press"

#: Les autres presses à cuisses du référentiel — elles ne doivent PAS bouger.
ORDINARY_LEG_PRESSES = (
    "Leg Press (pieds bas)",
    "Leg Press (pieds bas, serrés)",
    "Leg Press (pieds hauts, écartés)",
)

#: L'état attendu du référentiel APRÈS adjudication, exercice par exercice.
#: Construit une seule fois et comparé intégralement : c'est le garde-fou
#: anti-collatéral, pas une liste décorative.
EXPECTED_CHANGES = {ADJUDICATED: ("quads", "calves")}


# ── La correction elle-même ─────────────────────────────────────────────────


def test_the_adjudicated_exercise_now_resolves_to_calves():
    resolution = resolve_exercise_zones(None, ADJUDICATED)
    assert resolution.primary == "calves"
    assert resolution.resolution_path == PATH_CORRECTION
    assert resolution.from_formal_mapping is True


def test_the_correction_is_registered_with_its_evidence():
    entry = next(
        c for c in KNOWN_MAPPING_CORRECTIONS if c.exercise_name == ADJUDICATED)
    assert entry.legacy_primary == "quads"
    assert entry.primary == "calves"
    assert entry.evidence, "une correction sans preuve n'a rien à faire ici"
    # Les deux sources curées qui contredisent le matcher sont citées.
    assert "exercise_properties" in entry.evidence
    assert "EKB" in entry.evidence


def test_the_contribution_now_credits_calves_not_quads():
    roles = exercise_roles(ADJUDICATED)
    assert roles == {"calves": ContributionRole.DIRECT}
    assert "quads" not in roles


# ── Ce qui ne doit PAS bouger — le vrai risque ──────────────────────────────


def test_only_the_adjudicated_exercise_changed_across_the_whole_referential():
    """Diff complet sur les 105 exercices canoniques.

    Une correction exacte ne doit toucher qu'une identité. Si ce test tombe,
    c'est qu'une règle générique a été déplacée — et il faut s'arrêter, pas
    ajuster la liste attendue.
    """
    from app.services.muscle_mapping import _classify_exercise_by_patterns

    moved = {}
    for name in canonical_exercise_referential():
        legacy_primary, _ = _classify_exercise_by_patterns(name)
        resolved = resolve_exercise_zones(None, name)
        if resolved.primary != legacy_primary:
            moved[name] = (legacy_primary, resolved.primary)

    # Les deux corrections historiques + la nôtre, et rien de plus.
    expected = {
        "Rear delt fly machine (pec deck inversé)": ("pecs", "delt_post"),
        "Relevé de jambes suspendu": ("calves", "core"),
        **EXPECTED_CHANGES,
    }
    assert moved == expected, (
        "des exercices non adjudiqués ont changé de zone — HARD STOP"
    )


@pytest.mark.parametrize("name", ORDINARY_LEG_PRESSES)
def test_the_ordinary_leg_press_family_stays_quads(name):
    """La correction ne redéfinit PAS le sens générique de « leg press »."""
    assert resolve_exercise_zones(None, name).primary == "quads"


def test_the_generic_classifier_itself_was_not_reordered():
    """La table de motifs reste intacte : seule la couche de correction agit."""
    from app.services.muscle_mapping import _classify_exercise_by_patterns

    legacy, _ = _classify_exercise_by_patterns(ADJUDICATED)
    assert legacy == "quads", (
        "le classifieur générique a été modifié — la correction devait être "
        "une couche au-dessus, pas une réécriture"
    )


def test_every_canonical_calf_exercise_still_resolves_to_calves():
    calves = [
        n for n in canonical_exercise_referential()
        if "mollet" in n.lower() or "calf" in n.lower()
    ]
    assert len(calves) >= 4
    for name in calves:
        assert resolve_exercise_zones(None, name).primary == "calves"


def test_the_substitution_drawer_is_unchanged():
    """Le tiroir ne lit pas les zones : il ne peut pas bouger — vérifié."""
    from app.services.substitution import (
        compute_suggestions,
        load_exercise_properties,
    )

    class _TE:
        def __init__(self, name):
            self.exercise_name = name
            self.name = name
            self.substitutes = []

    props = load_exercise_properties()
    # `Calf press leg press` garde ses propriétés d'origine : la correction
    # porte sur la ZONE canonique, pas sur le registre de substitution.
    assert props[ADJUDICATED]["muscle_group"] == "calves"
    assert props[ADJUDICATED]["zone_primary"] == "lower"

    suggestions = compute_suggestions(_TE(ADJUDICATED))
    assert any(suggestions[level] for level in ("N1", "N2", "N3"))


def test_no_scientific_claim_is_made_in_the_evidence():
    """La classification est une attribution de PROGRAMMATION."""
    entry = next(
        c for c in KNOWN_MAPPING_CORRECTIONS if c.exercise_name == ADJUDICATED)
    lowered = entry.evidence.lower()
    for banned in ("emg", "%", "activation", "scientifically proven",
                   "prouvé scientifiquement"):
        assert banned not in lowered, f"revendication interdite : {banned!r}"
    assert "programming" in lowered


# ── Cohérence en aval ───────────────────────────────────────────────────────


def test_the_seed_rows_carry_the_corrected_zone():
    """`mapping_rows` applique déjà les corrections — le seed reste cohérent."""
    from app.services.reference_data_seed import mapping_rows

    primary = {
        r["exercise_code"]: r["body_zone_code"]
        for r in mapping_rows() if r["role"] == "primary"
    }
    assert primary[ADJUDICATED] == "calves"
    for name in ORDINARY_LEG_PRESSES:
        assert primary[name] == "quads"


def test_the_planner_is_unaffected_because_it_selects_another_exercise():
    """Constat honnête : la fixture cadence 4 ne sélectionne pas cet exercice.

    L'allocateur retient « Mollets assis machine » pour les mollets et réutilise
    cette identité d'une séance à l'autre. La correction n'a donc **aucun
    effet** sur ce plan — elle en aura un dès que cet exercice sera retenu
    (restriction de matériel, seconde identité nécessaire, catalogue élargi).

    Le dire vaut mieux que d'exhiber un gain qui n'existe pas.
    """
    from app.services.training_preferences import TrainingPreferencesData
    from app.services.weekly_planner import build_weekly_plan

    plan = build_weekly_plan(TrainingPreferencesData(sessions_per_week=4))
    selected = {
        slot.exercise_name for session in plan.sessions
        for slot in session.slots if slot.zone_code == "calves"
    }
    assert ADJUDICATED not in selected
    calves = next(z for z in plan.zone_coverage if z.zone_code == "calves")
    assert calves.direct_sets == calves.planned_sets, (
        "toutes les séries mollets créditent bien les mollets"
    )
