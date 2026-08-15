"""Sb_SLOT_INTENT_COVERAGE_01 — couverture primaire des 11 zones détaillées.

Ce que ces tests protègent, dans l'ordre d'importance :

1. **La discrimination des candidats est réelle**, pas déclarative. Un créneau
   biceps ne doit jamais pouvoir sélectionner un exercice triceps, et
   réciproquement — alors que les deux sont *strictement indiscernables* dans
   `exercise_properties.json`. Le test qui compte est celui qui **prouve
   l'indiscernabilité** de la source, puis prouve que la sélection sépare
   quand même.
2. **Un créneau vide ne couvre rien.** Le générateur émet un créneau pour toute
   intention retenue ; le compter comme couverture ferait passer une lacune
   pour une réussite.
3. **Le moteur de substitution est inchangé.** La discrimination a été obtenue
   sans écrire dans `exercise_properties.json`, précisément parce que le champ
   `muscle_group` conditionne l'éligibilité N1 en runtime.
"""
from __future__ import annotations

import json

import pytest

from app.services import morpho_program_generator as MPG
from app.services import slot_intent as SI
from app.services.body_zone_source import resolve_exercise_zones
from app.services.muscle_mapping import RADAR_AXES, ZONE_VOLUME_TARGET
from app.services.substitution import load_exercise_properties
from app.services.training_preferences import TrainingPreferencesData
from app.services.weekly_planner import (
    UNMET_EQUIPMENT,
    UNMET_NO_CANDIDATE,
    UNMET_NO_INTENT,
    build_weekly_plan,
    zones_servable_as_primary,
)

NEW_INTENTS = (
    "lats_width_vertical_pull",
    "elbow_flexor_direct",
    "elbow_extensor_direct",
    "trunk_core_direct",
)


def _pool() -> dict[str, dict]:
    return load_exercise_properties()


def _plan(**kwargs):
    return build_weekly_plan(TrainingPreferencesData(**kwargs))


def _zone(plan, code):
    return next(z for z in plan.zone_coverage if z.zone_code == code)


def _exercise_for(plan, zone_code) -> str | None:
    for session in plan.sessions:
        for slot in session.slots:
            if slot.zone_code == zone_code:
                return slot.exercise_name
    return None


# ── 1. Audit de couverture des 11 zones ──────────────────────────────────────


def test_every_canonical_zone_is_reachable_as_a_primary_target():
    """Les 11 zones détaillées ont une intention primaire. Aucune exception."""
    assert zones_servable_as_primary() == set(ZONE_VOLUME_TARGET)


def test_every_declarable_axis_has_all_of_its_zones_servable():
    """Un axe n'est servable que si TOUTES ses zones le sont — pas seulement une."""
    servable = zones_servable_as_primary()
    for axis_key, axis in RADAR_AXES.items():
        unservable = [z for z in axis["zones"] if z not in servable]
        assert not unservable, f"axe {axis_key} incomplet : {unservable}"


def test_the_new_intents_use_only_existing_pattern_vocabulary():
    """Aucun PatternMotor inventé — `core` existait déjà dans le vocabulaire."""
    from app.services.substitution import VALID_PATTERN_MOTORS

    for intent_id in NEW_INTENTS:
        spec = SI._INTENT_SPECS[intent_id]
        assert spec["movement_pattern"] in VALID_PATTERN_MOTORS
        assert set(spec["forbidden"]) <= VALID_PATTERN_MOTORS


def test_core_keeps_no_radar_axis():
    """`core` reste une zone détaillée SANS axe radar — aucun axe fabriqué."""
    from app.services.muscle_mapping import RADAR_AXIS_ORDER, radar_axis_for_zone

    assert radar_axis_for_zone("core") is None
    assert "core" not in RADAR_AXIS_ORDER
    assert all("core" not in axis["zones"] for axis in RADAR_AXES.values())
    # …et il est pourtant programmable comme préoccupation de zone détaillée.
    assert "core" in zones_servable_as_primary()


def test_the_core_region_is_read_from_the_knowledge_base_not_invented():
    """La région de `core` vient de la source curatée, et les deux sources concordent."""
    from app.services.user_program_exercise_catalog import detailed_zone_regions

    curated = detailed_zone_regions()
    assert curated["core"] == "core"
    assert SI.DETAILED_TO_REGION["core"] == "core"
    # Sur les dix zones qui ont un axe, EKB et RADAR_AXES disent la même chose :
    # les deux sources ne peuvent pas diverger en silence.
    for zone, axis in SI._REGION_FROM_RADAR.items():
        if zone in curated:
            assert curated[zone] == axis, f"divergence EKB/radar sur {zone}"


# ── 2. La preuve qui compte : la source NE SÉPARE PAS, la sélection SI ───────


def test_the_pool_genuinely_cannot_tell_a_curl_from_a_pushdown():
    """Preuve de la prémisse : sans discriminateur, biceps et triceps sont IDENTIQUES.

    Si ce test venait à échouer parce que `exercise_properties.json` a gagné un
    `muscle_group` sur les bras, le mécanisme de discrimination canonique
    deviendrait redondant — et il faudrait le reconsidérer plutôt que le garder
    par inertie.
    """
    arms = {n: p for n, p in _pool().items() if p.get("zone_primary") == "arms"}
    assert len(arms) >= 15, "le référentiel bras a changé de taille"
    assert all(p.get("muscle_group") is None for p in arms.values())
    signatures = {
        (p.get("zone_primary"), p.get("pattern_motor"), p.get("chain"))
        for p in arms.values()
    }
    assert len(signatures) == 1, (
        "les bras ne sont plus indiscernables dans le pool : "
        f"{signatures}"
    )


def test_a_biceps_slot_never_selects_a_triceps_exercise():
    plan = _plan(sessions_per_week=3, focus_priorities=("arms",))
    chosen = _exercise_for(plan, "biceps")
    assert chosen is not None
    assert resolve_exercise_zones(None, chosen).primary == "biceps"


def test_a_triceps_slot_never_selects_a_biceps_exercise():
    plan = _plan(sessions_per_week=3, focus_priorities=("arms",))
    chosen = _exercise_for(plan, "triceps")
    assert chosen is not None
    assert resolve_exercise_zones(None, chosen).primary == "triceps"


def test_every_arm_candidate_is_partitioned_by_canonical_zone():
    """Exhaustif, pas anecdotique : chaque candidat qualifiant est de la bonne zone."""
    for zone in ("biceps", "triceps"):
        intent = SI.build_slot_intent(
            SI.PRIORITY_TO_INTENTS[zone][0], slot_id="s1", priority_level=1)
        ranked = MPG._rank_qualifying(intent, _pool())
        assert ranked, f"aucun candidat pour {zone}"
        for name, _score in ranked:
            assert resolve_exercise_zones(None, name).primary == zone


def test_the_discrimination_guard_bites_when_removed(monkeypatch):
    """Plant : sans le discriminateur canonique, la séparation disparaît vraiment.

    Une garde non prouvée est une garde supposée. On retire la région `arms` de
    l'ensemble discriminé et on vérifie que les deux intentions retombent bien
    sur le MÊME jeu de candidats — c'est ce que le mécanisme empêche.

    Le cache de `_canonical_detailed_zone` n'a pas à être vidé : il indexe des
    noms d'exercices vers leur zone canonique, sans lire l'ensemble patché.
    """
    intents = {
        zone: SI.build_slot_intent(
            SI.PRIORITY_TO_INTENTS[zone][0], slot_id="s1", priority_level=1)
        for zone in ("biceps", "triceps")
    }
    with_guard = {
        zone: {n for n, _ in MPG._rank_qualifying(intents[zone], _pool())}
        for zone in intents
    }
    assert not (with_guard["biceps"] & with_guard["triceps"])

    monkeypatch.setattr(MPG, "_REGION_BY_CANONICAL_ZONE", frozenset())
    without = {
        zone: {n for n, _ in MPG._rank_qualifying(intents[zone], _pool())}
        for zone in intents
    }

    assert without["biceps"] == without["triceps"], (
        "le plant est inerte : les deux intentions se séparaient déjà sans le "
        "discriminateur, donc ce test ne prouve rien"
    )
    assert without["biceps"] > with_guard["biceps"]


# ── 3. Lats vs upper_back — séparation structurelle ──────────────────────────


def test_a_lats_slot_selects_only_a_vertical_pull_mapped_to_lats():
    plan = _plan(sessions_per_week=3, focus_priorities=("back_width",))
    chosen = _exercise_for(plan, "lats")
    assert chosen is not None
    assert resolve_exercise_zones(None, chosen).primary == "lats"
    assert _pool()[chosen]["zone_primary"] == "back_width"


def test_a_row_can_never_satisfy_a_lats_slot():
    """L'épaisseur ne sert pas la largeur : deux régions macro distinctes."""
    intent = SI.build_slot_intent(
        "lats_width_vertical_pull", slot_id="s1", priority_level=1)
    pool = _pool()
    rows = [n for n, p in pool.items() if p.get("zone_primary") == "back_thickness"]
    assert rows, "plus aucun exercice d'épaisseur dans le pool"
    for name in rows:
        assert not MPG._qualifies(intent, name, pool[name])


def test_upper_back_still_selects_a_row_and_is_unaffected():
    plan = _plan(sessions_per_week=3, focus_priorities=("back_thickness",))
    chosen = _exercise_for(plan, "upper_back")
    assert chosen is not None
    assert _pool()[chosen]["pattern_motor"] == "pull_horizontal"


# ── 4. Core — intention réelle, lacune de données nommée ─────────────────────


def test_core_has_an_intent_but_no_programmable_candidate():
    """La lacune `core` est une lacune de DONNÉES, dite comme telle.

    Les huit exercices de tronc du référentiel canonique existent, mais aucun
    n'a de propriétés programmables (`exercise_properties.json` ne les contient
    pas ; l'EKB les marque `coverage_status: gap`). Rien n'est fabriqué pour
    combler ce trou : la zone sort en `UNMET_NO_CANDIDATE`.
    """
    plan = _plan(sessions_per_week=3)
    core = _zone(plan, "core")
    assert core.unmet_reason == UNMET_NO_CANDIDATE
    assert core.unmet_reason != UNMET_NO_INTENT
    assert core.planned_slots == 0


def test_core_never_selects_an_upper_body_isolation():
    """Un créneau tronc ne peut pas être servi par une isolation de bras/épaules."""
    intent = SI.build_slot_intent("trunk_core_direct", slot_id="s1", priority_level=1)
    pool = _pool()
    isolations = [
        n for n, p in pool.items() if p.get("pattern_motor") == "isolation_upper"
    ]
    assert isolations
    for name in isolations:
        assert not MPG._qualifies(intent, name, pool[name])
    assert not MPG._rank_qualifying(intent, pool)


def test_the_canonical_referential_does_carry_core_exercises():
    """La lacune est bien dans les PROPRIÉTÉS, pas dans l'identité des exercices."""
    from app.services.reference_data_seed import mapping_rows

    core_names = [
        r["exercise_code"] for r in mapping_rows()
        if r["role"] == "primary" and r["body_zone_code"] == "core"
    ]
    assert len(core_names) >= 5
    pool = _pool()
    assert not [n for n in core_names if n in pool], (
        "des exercices core ont gagné des propriétés — la lacune est fermée et "
        "ce test doit devenir une assertion de couverture"
    )


# ── 5. Créneau vide ≠ couverture ─────────────────────────────────────────────


def test_an_empty_slot_is_not_counted_as_coverage():
    """Le fail-open que `core` met au jour : un créneau sans exercice ne couvre rien."""
    plan = _plan(sessions_per_week=3)
    core_slots = [
        slot for session in plan.sessions for slot in session.slots
        if slot.zone_code == "core"
    ]
    assert core_slots, "le créneau core doit exister — l'intention est réelle"
    assert all(slot.exercise_name is None for slot in core_slots)
    assert _zone(plan, "core").planned_slots == 0
    assert _zone(plan, "core") in plan.unmet_budget


def test_equipment_restriction_is_reported_as_such_not_as_a_missing_candidate():
    """Les cinq candidats triceps sont tous à la poulie : sans câble, la zone tombe."""
    plan = _plan(
        sessions_per_week=3,
        focus_priorities=("arms",),
        available_equipment=("dumbbell", "barbell", "machine"),
    )
    assert _zone(plan, "triceps").unmet_reason == UNMET_EQUIPMENT
    assert _zone(plan, "biceps").unmet_reason is None


def test_a_half_served_axis_is_not_reported_as_served():
    """« Bras » n'est pas satisfait quand seuls les biceps sont programmables."""
    plan = _plan(
        sessions_per_week=3,
        focus_priorities=("arms",),
        available_equipment=("dumbbell", "barbell", "machine"),
    )
    assert plan.unmet_constraints
    assert any("Bras" in c and "Triceps" in c for c in plan.unmet_constraints)


# ── 6. Non-régression : rien d'autre n'a bougé ───────────────────────────────


def test_substitution_runtime_is_untouched():
    """La discrimination n'a coûté aucune écriture dans le pool d'exercices.

    `substitution._classify_suggestion` conditionne l'éligibilité N1 à l'égalité
    de `muscle_group` : ajouter le champ sur les 17 exercices de bras aurait
    changé les suggestions du tiroir en production. Le fichier reste intact.
    """
    from app.config import BASE_DIR

    raw = json.loads(
        (BASE_DIR / "data" / "exercise_properties.json").read_text(encoding="utf-8")
    )["exercises"]
    arms = [p for p in raw.values() if p.get("zone_primary") == "arms"]
    assert arms
    assert all("muscle_group" not in p or p["muscle_group"] is None for p in arms)


def test_pre_existing_intents_still_select_what_they_used_to():
    """Le générateur est inchangé hors des nouvelles intentions."""
    expectations = {
        "pecs": "push_horizontal",
        "delt_lat": "isolation_upper",
        "delt_post": "isolation_upper",
        "upper_back": "pull_horizontal",
        "quads": "isolation_lower",
        "posterior": "hinge",
    }
    plan = _plan(sessions_per_week=6)
    pool = _pool()
    for zone, pattern in expectations.items():
        chosen = _exercise_for(plan, zone)
        assert chosen is not None, f"{zone} n'est plus servi"
        assert pool[chosen]["pattern_motor"] == pattern


def test_no_new_substring_classifier_was_written():
    """La discrimination délègue au contrat canonique — aucun matcher local."""
    from tests.helpers import module_code_only

    code = module_code_only(MPG)
    for token in ("curl", "pushdown", "startswith(", "in name", "lower()"):
        assert token not in code.lower() or token == "lower()", (
            f"un matcher de nom semble avoir été écrit ({token!r})"
        )
    assert "resolve_exercise_zones" in code


def test_the_plan_stays_deterministic():
    first = _plan(sessions_per_week=4, focus_priorities=("arms", "back_width"))
    second = _plan(sessions_per_week=4, focus_priorities=("arms", "back_width"))
    assert first.fingerprint == second.fingerprint
    assert first.fingerprint


@pytest.mark.parametrize("intent_id", NEW_INTENTS)
def test_new_intents_make_no_physiological_claim(intent_id):
    """Le rationale décrit une FONCTION DE PROGRAMMATION, jamais une certitude."""
    rationale = SI._INTENT_SPECS[intent_id]["rationale"].lower()
    for forbidden in (
        "emg", "activation", "%", "recrutement", "obligatoire", "seul",
        "supérieur", "prouvé", "scientifi",
    ):
        assert forbidden not in rationale, (
            f"{intent_id} revendique une propriété physiologique : {forbidden!r}"
        )


def test_the_scientific_guard_is_recorded_in_code():
    guard = SI.SCIENTIFIC_GUARD.lower()
    assert "programming taxonomy" in guard
    assert "no emg percentage" in guard
    assert "no mandatory isolation" in guard
