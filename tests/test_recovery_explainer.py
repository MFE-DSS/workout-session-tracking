"""Sb_RECOVERY_EXPLAINER_01 — la couche de langage de P0.4 (tranche 5/5).

Ces tests portent sur ce qui est **réellement rendu**. Le garde-fou de
formulation (§8.4) n'inspecte pas la source du module : il exécute l'explainer
public sur des `TrainingState` représentatifs et scanne chaque chaîne produite.
Plusieurs tests **plantent une violation** dans le module pour prouver que le
garde-fou mord au lieu de l'affirmer.
"""
from __future__ import annotations

import inspect
import re
from datetime import UTC, datetime, timedelta

import pytest

from app.services import recovery_explainer as rx
from app.services.muscle_mapping import RADAR_AXIS_ORDER, ZONE_LABELS
from app.services.recovery_contract import (
    CardioModality,
    Confidence,
    FatigueSignal,
    MacroAxisRecovery,
    ReadinessSignal,
    RecoveryBand,
    Sufficiency,
    TrainingState,
    ZoneRecoveryEstimate,
)
from app.services.recovery_explainer import (
    BAND_MESSAGES,
    EXPLAINER_VERSION,
    INSUFFICIENT_DATA_LABEL,
    KIND_CARDIO,
    KIND_DATA_PROMPT,
    KIND_MACRO_AXIS,
    KIND_READINESS,
    KIND_ZONE_RECOVERY,
    MAX_RENDERABLE_CONFIDENCE,
    SURFACE_DETAILED,
    SURFACE_PROACTIVE,
    ExplanationItem,
    build_detailed_explanation,
    build_proactive_explanation,
    confidence_label,
    explain_axis,
    explain_cardio,
    explain_readiness,
    explain_zone,
    recognised_modalities,
    recovery_rank_key,
    rendered_strings,
    wording_violations,
)
from app.services.zone_recovery import build_zone_recovery_from_evidence

NOW = datetime(2026, 8, 12, 9, 0, tzinfo=UTC)

ZONE_QUADS = "quads"
ZONE_PECS = "pecs"
ZONE_CORE = "core"
ZONE_POSTERIOR = "posterior"
MODALITY_BASIS_VELO = "modality: velo"
SIGNAL_STRENGTH = "strength_load"
SIGNAL_CARDIO = "cardio_exposure"
AXIS_LOWER = "lower"

SUBSTRING_BASIS = (
    "attribution fell back to the substring classifier for at least one exercise"
)
CARDIO_BASIS_VELO = "cardio exposure noted (velo) but not placed in time"


# ---------------------------------------------------------------------------
# Fabriques
# ---------------------------------------------------------------------------


def zone(
    code: str = ZONE_QUADS,
    *,
    estimate: float | None = 0.9,
    band: RecoveryBand = RecoveryBand.LIKELY_AVAILABLE,
    confidence: Confidence = Confidence.MEDIUM,
    basis: tuple[str, ...] = (),
    signals: tuple[str, ...] = (SIGNAL_STRENGTH,),
) -> ZoneRecoveryEstimate:
    return ZoneRecoveryEstimate(
        zone_code=code,
        estimate=estimate,
        band=band,
        confidence=confidence,
        basis=basis,
        contributing_signals=signals,
        staleness=Sufficiency.SUFFICIENT,
    )


def state_with(*estimates: ZoneRecoveryEstimate, **kwargs) -> TrainingState:
    return TrainingState(computed_at=NOW, zone_recovery=estimates, **kwargs)


def new_user_state() -> TrainingState:
    """L'état d'un compte neuf : onze zones explicitement inconnues."""
    return TrainingState(
        computed_at=NOW,
        zone_recovery=build_zone_recovery_from_evidence({}, now=NOW),
    )


def declared_readiness(overall: float, *, age_days: int = 0) -> ReadinessSignal:
    return ReadinessSignal(
        overall=overall,
        age_days=age_days,
        declared_on=(NOW - timedelta(days=age_days)).date(),
        sufficiency=Sufficiency.SUFFICIENT,
    )


def all_text(explanation) -> str:
    return " || ".join(rendered_strings(explanation)).lower()


# ---------------------------------------------------------------------------
# ZONE — MEDIUM
# ---------------------------------------------------------------------------


class TestZoneMedium:
    def test_emits_an_actual_explanation(self):
        item = explain_zone(zone())
        assert item.is_estimate is True

    def test_message_is_the_band_sentence(self):
        item = explain_zone(zone())
        assert item.message == BAND_MESSAGES[RecoveryBand.LIKELY_AVAILABLE]

    def test_confidence_is_included(self):
        item = explain_zone(zone())
        assert item.confidence is Confidence.MEDIUM

    def test_confidence_is_labelled_ordinally(self):
        item = explain_zone(zone())
        assert item.confidence_label == "Confiance moyenne"

    def test_basis_is_traceable_to_a_reason(self):
        item = explain_zone(zone())
        assert rx.SIGNAL_REASONS[SIGNAL_STRENGTH] in item.reasons

    def test_subject_carries_the_machine_code(self):
        item = explain_zone(zone())
        assert item.subject == ZONE_QUADS

    def test_subject_label_uses_canonical_vocabulary(self):
        item = explain_zone(zone())
        assert item.subject_label == ZONE_LABELS[ZONE_QUADS]

    def test_band_is_carried_for_the_consumer(self):
        item = explain_zone(zone())
        assert item.band is RecoveryBand.LIKELY_AVAILABLE

    def test_no_numeric_estimate_is_exposed(self):
        item = explain_zone(zone(estimate=0.87))
        assert "0.87" not in item.message

    def test_partially_recovered_stays_an_estimate_in_words(self):
        item = explain_zone(
            zone(estimate=0.5, band=RecoveryBand.PARTIALLY_RECOVERED))
        assert "estimée" in item.message


# ---------------------------------------------------------------------------
# ZONE — LOW
# ---------------------------------------------------------------------------


class TestZoneLow:
    def test_low_still_produces_an_explanation(self):
        item = explain_zone(zone(confidence=Confidence.LOW))
        assert item.is_estimate is True

    def test_low_is_preserved_never_promoted(self):
        item = explain_zone(zone(confidence=Confidence.LOW))
        assert item.confidence is Confidence.LOW

    def test_low_label_is_explicitly_weak(self):
        item = explain_zone(zone(confidence=Confidence.LOW))
        assert item.confidence_label == "Confiance faible"

    def test_low_never_renders_as_medium(self):
        item = explain_zone(zone(confidence=Confidence.LOW))
        assert item.confidence_label != confidence_label(Confidence.MEDIUM)

    def test_fatigued_wording_stays_cautious(self):
        item = explain_zone(
            zone(band=RecoveryBand.LIKELY_FATIGUED, confidence=Confidence.LOW))
        assert "semble" in item.message

    def test_substring_attribution_is_surfaced_as_approximate(self):
        item = explain_zone(
            zone(confidence=Confidence.LOW, basis=(SUBSTRING_BASIS,)))
        assert any("approximative" in reason for reason in item.reasons)


# ---------------------------------------------------------------------------
# ZONE — NONE : silence sur la physiologie, explicite sur la donnée
# ---------------------------------------------------------------------------


class TestZoneConfidenceNone:
    def test_no_recovery_interpretation_is_emitted(self):
        item = explain_zone(
            zone(estimate=None, band=RecoveryBand.UNKNOWN,
                 confidence=Confidence.NONE, signals=()))
        assert item.message not in BAND_MESSAGES.values()

    def test_it_is_not_flagged_as_an_estimate(self):
        item = explain_zone(
            zone(estimate=None, band=RecoveryBand.UNKNOWN,
                 confidence=Confidence.NONE, signals=()))
        assert item.is_estimate is False

    def test_the_notice_is_about_data_not_the_body(self):
        item = explain_zone(
            zone(estimate=None, band=RecoveryBand.UNKNOWN,
                 confidence=Confidence.NONE, signals=()))
        assert item.message == rx.ZONE_INSUFFICIENT_MESSAGE

    def test_the_canonical_label_is_data_insufficiency(self):
        item = explain_zone(
            zone(estimate=None, band=RecoveryBand.UNKNOWN,
                 confidence=Confidence.NONE, signals=()))
        assert item.confidence_label == INSUFFICIENT_DATA_LABEL

    def test_no_reassuring_word_appears(self):
        item = explain_zone(
            zone(estimate=None, band=RecoveryBand.UNKNOWN,
                 confidence=Confidence.NONE, signals=()))
        assert "disponible" not in item.message

    def test_no_alarming_word_appears(self):
        item = explain_zone(
            zone(estimate=None, band=RecoveryBand.UNKNOWN,
                 confidence=Confidence.NONE, signals=()))
        assert "chargée" not in item.message

    def test_a_band_without_confidence_cannot_sneak_through(self):
        """Bande exploitable mais `Confidence.NONE` : la confiance l'emporte.

        Une bande calculée sur une confiance nulle resterait une affirmation
        sur le corps sans preuve. C'est la confiance qui décide, pas la bande.
        """
        item = explain_zone(
            zone(band=RecoveryBand.LIKELY_AVAILABLE, confidence=Confidence.NONE))
        assert item.is_estimate is False

    def test_detailed_surface_keeps_the_zone_visible(self):
        state = state_with(
            zone(estimate=None, band=RecoveryBand.UNKNOWN,
                 confidence=Confidence.NONE, signals=()))
        detailed = build_detailed_explanation(state)
        subjects = [item.subject for item in detailed.data_state_items]
        assert ZONE_QUADS in subjects

    def test_proactive_surface_omits_it_entirely(self):
        state = state_with(
            zone(),
            zone(code=ZONE_PECS, estimate=None, band=RecoveryBand.UNKNOWN,
                 confidence=Confidence.NONE, signals=()),
        )
        proactive = build_proactive_explanation(state)
        subjects = [item.subject for item in proactive.all_items()]
        assert ZONE_PECS not in subjects

    def test_proactive_keeps_the_zone_that_does_have_an_estimate(self):
        state = state_with(
            zone(),
            zone(code=ZONE_PECS, estimate=None, band=RecoveryBand.UNKNOWN,
                 confidence=Confidence.NONE, signals=()),
        )
        proactive = build_proactive_explanation(state)
        assert [item.subject for item in proactive.zone_items] == [ZONE_QUADS]


# ---------------------------------------------------------------------------
# Séparation estimation / état de donnée
# ---------------------------------------------------------------------------


class TestEstimateVersusDataState:
    def test_the_two_live_in_separate_collections(self):
        state = state_with(
            zone(),
            zone(code=ZONE_PECS, estimate=None, band=RecoveryBand.UNKNOWN,
                 confidence=Confidence.NONE, signals=()),
        )
        detailed = build_detailed_explanation(state)
        assert detailed.zone_items[0].subject == ZONE_QUADS

    def test_no_data_state_leaks_into_the_estimates(self):
        state = state_with(
            zone(),
            zone(code=ZONE_PECS, estimate=None, band=RecoveryBand.UNKNOWN,
                 confidence=Confidence.NONE, signals=()),
        )
        detailed = build_detailed_explanation(state)
        assert all(item.is_estimate for item in detailed.zone_items)

    def test_no_estimate_leaks_into_the_data_states(self):
        state = state_with(
            zone(),
            zone(code=ZONE_PECS, estimate=None, band=RecoveryBand.UNKNOWN,
                 confidence=Confidence.NONE, signals=()),
        )
        detailed = build_detailed_explanation(state)
        assert not any(item.is_estimate for item in detailed.data_state_items)

    def test_a_data_state_is_not_rankable_as_a_band(self):
        notice = explain_zone(
            zone(estimate=None, band=RecoveryBand.UNKNOWN,
                 confidence=Confidence.NONE, signals=()))
        with pytest.raises(ValueError, match="not rankable"):
            recovery_rank_key(notice)

    def test_an_estimate_is_rankable(self):
        key = recovery_rank_key(explain_zone(zone()))
        assert isinstance(key, tuple)

    def test_ranking_orders_the_most_constrained_first(self):
        available = explain_zone(zone())
        fatigued = explain_zone(zone(code=ZONE_PECS,
                                     band=RecoveryBand.LIKELY_FATIGUED))
        ordered = sorted([available, fatigued], key=recovery_rank_key)
        assert ordered[0].band is RecoveryBand.LIKELY_FATIGUED

    def test_an_estimate_item_must_carry_a_confidence(self):
        with pytest.raises(ValueError, match="must carry a confidence"):
            ExplanationItem(
                kind=KIND_ZONE_RECOVERY, message="x", is_estimate=True)

    def test_an_unknown_kind_is_refused(self):
        with pytest.raises(ValueError, match="unknown explanation kind"):
            ExplanationItem(kind="freestyle", message="x", is_estimate=False)


# ---------------------------------------------------------------------------
# NOUVEL UTILISATEUR — onze inconnues ne font pas onze affirmations
# ---------------------------------------------------------------------------


class TestNewUser:
    def test_the_state_really_has_eleven_unknown_zones(self):
        state = new_user_state()
        unknown = [
            estimate for estimate in state.zone_recovery
            if estimate.confidence is Confidence.NONE
        ]
        assert len(unknown) == 11

    def test_detailed_emits_zero_physiological_explanations(self):
        detailed = build_detailed_explanation(new_user_state())
        assert detailed.zone_items == ()

    def test_detailed_keeps_all_eleven_zones_structurally_present(self):
        detailed = build_detailed_explanation(new_user_state())
        subjects = {
            item.subject for item in detailed.data_state_items
            if item.kind == KIND_ZONE_RECOVERY
        }
        assert subjects == set(ZONE_LABELS)

    def test_detailed_says_nothing_about_a_body(self):
        text = all_text(build_detailed_explanation(new_user_state()))
        assert "récupér" not in text

    def test_proactive_does_not_flood_with_eleven_messages(self):
        proactive = build_proactive_explanation(new_user_state())
        assert len(proactive.data_state_items) <= 1

    def test_proactive_still_says_something_useful(self):
        proactive = build_proactive_explanation(new_user_state())
        assert proactive.data_state_items[0].message == (
            rx.GLOBAL_INSUFFICIENT_MESSAGE)

    def test_proactive_emits_no_zone_estimate(self):
        proactive = build_proactive_explanation(new_user_state())
        assert proactive.zone_items == ()

    def test_proactive_invites_data_entry_rather_than_training(self):
        proactive = build_proactive_explanation(new_user_state())
        assert proactive.data_prompt.message == rx.DATA_PROMPT_MESSAGE

    def test_the_prompt_is_not_an_estimate(self):
        proactive = build_proactive_explanation(new_user_state())
        assert proactive.data_prompt.is_estimate is False

    def test_the_prompt_is_its_own_category(self):
        proactive = build_proactive_explanation(new_user_state())
        assert proactive.data_prompt.kind == KIND_DATA_PROMPT

    def test_a_new_user_triggers_no_wording_violation(self):
        detailed = build_detailed_explanation(new_user_state())
        assert wording_violations(rendered_strings(detailed)) == ()


# ---------------------------------------------------------------------------
# CARDIO
# ---------------------------------------------------------------------------


def cardio_state(*basis: str, component: float | None = 0.6) -> TrainingState:
    return TrainingState(
        computed_at=NOW,
        fatigue=FatigueSignal(
            cardio_component=component,
            confidence=Confidence.LOW,
            basis=basis,
        ),
    )


class TestCardio:
    def test_a_known_modality_is_named(self):
        item = explain_cardio(cardio_state(MODALITY_BASIS_VELO))
        assert "vélo" in item.message

    def test_a_known_modality_names_its_zones_from_the_canonical_table(self):
        item = explain_cardio(cardio_state(MODALITY_BASIS_VELO))
        assert ZONE_LABELS[ZONE_QUADS] in item.message

    def test_it_is_framed_as_exposure_not_fatigue(self):
        item = explain_cardio(cardio_state(MODALITY_BASIS_VELO))
        assert "exposition" in item.message

    def test_it_is_never_flagged_as_a_recovery_estimate(self):
        item = explain_cardio(cardio_state(MODALITY_BASIS_VELO))
        assert item.is_estimate is False

    def test_it_states_it_is_not_a_measurement(self):
        item = explain_cardio(cardio_state(MODALITY_BASIS_VELO))
        assert any("pas une mesure" in reason for reason in item.reasons)

    def test_an_unknown_modality_invents_no_zone(self):
        item = explain_cardio(
            cardio_state("modality outside the known vocabulary: 'trampoline'"))
        assert ZONE_LABELS[ZONE_QUADS] not in item.message

    def test_an_unknown_modality_says_so_plainly(self):
        item = explain_cardio(
            cardio_state("modality outside the known vocabulary: 'trampoline'"))
        assert item.message == rx.CARDIO_UNKNOWN_MESSAGE

    def test_the_autre_bucket_names_no_zone(self):
        item = explain_cardio(cardio_state("modality: autre"))
        assert item.message == rx.CARDIO_UNKNOWN_MESSAGE

    def test_autre_is_not_recognised_as_nameable(self):
        assert recognised_modalities(("modality: autre",)) == ()

    def test_the_unknown_bucket_is_not_nameable_either(self):
        assert recognised_modalities(("modality: unknown",)) == ()

    def test_no_cardio_evidence_yields_no_item(self):
        item = explain_cardio(cardio_state("no cardio session in window",
                                           component=None))
        assert item is None

    def test_bpm_never_appears(self):
        item = explain_cardio(cardio_state(
            MODALITY_BASIS_VELO,
            "average BPM recorded — raises evidence, never the magnitude",
        ))
        assert "bpm" not in item.message.lower()

    def test_bpm_makes_no_causal_intensity_claim(self):
        item = explain_cardio(cardio_state(
            MODALITY_BASIS_VELO,
            "average BPM recorded — raises evidence, never the magnitude",
        ))
        assert "intensité" not in item.message.lower()

    def test_calories_never_appear(self):
        item = explain_cardio(cardio_state(MODALITY_BASIS_VELO, "1200 kcal"))
        assert "kcal" not in item.message.lower()

    def test_duration_never_appears_as_a_recovery_input(self):
        item = explain_cardio(cardio_state(
            MODALITY_BASIS_VELO,
            "45 min vs 30 min reference (product normalization)",
        ))
        assert "min" not in item.message

    def test_a_zone_level_cardio_signal_stays_cautious(self):
        item = explain_zone(zone(
            confidence=Confidence.LOW,
            basis=(CARDIO_BASIS_VELO,),
            signals=(SIGNAL_STRENGTH, SIGNAL_CARDIO),
        ))
        assert rx.SIGNAL_REASONS[SIGNAL_CARDIO] in item.reasons

    def test_cardio_never_reads_as_a_recovery_penalty(self):
        item = explain_zone(zone(
            confidence=Confidence.LOW,
            basis=(CARDIO_BASIS_VELO,),
            signals=(SIGNAL_STRENGTH, SIGNAL_CARDIO),
        ))
        assert "réduit" not in " ".join(item.reasons)

    def test_the_modality_vocabulary_covers_every_specific_modality(self):
        from app.services.recovery_contract import CARDIO_SPECIFIC_MODALITIES

        assert set(rx.MODALITY_LABELS) == set(CARDIO_SPECIFIC_MODALITIES)

    def test_the_catch_all_buckets_are_deliberately_unlabelled(self):
        assert CardioModality.AUTRE not in rx.MODALITY_LABELS


# ---------------------------------------------------------------------------
# READINESS — déclarée, jamais mesurée
# ---------------------------------------------------------------------------


class TestReadiness:
    def test_a_poor_declaration_is_described_as_declared(self):
        item = explain_readiness(declared_readiness(0.2))
        assert item.message.startswith("Tu as déclaré")

    def test_a_poor_declaration_mentions_today(self):
        item = explain_readiness(declared_readiness(0.2))
        assert "aujourd'hui" in item.message

    def test_a_poor_declaration_never_speaks_of_the_body(self):
        item = explain_readiness(declared_readiness(0.2))
        assert "ton corps" not in item.message.lower()

    def test_a_good_declaration_emits_no_escalation(self):
        item = explain_readiness(declared_readiness(0.95))
        assert "plus lourd" not in item.message.lower()

    def test_a_good_declaration_prescribes_no_session(self):
        item = explain_readiness(declared_readiness(0.95))
        assert "séance" not in item.message.lower()

    def test_a_good_declaration_stays_a_statement_of_state(self):
        item = explain_readiness(declared_readiness(0.95))
        assert item.message == "Tu as déclaré te sentir en forme aujourd'hui."

    def test_a_middling_declaration_makes_no_direction_claim(self):
        item = explain_readiness(declared_readiness(0.55))
        assert item.message == "Tu as déclaré ton état du jour aujourd'hui."

    def test_readiness_is_never_an_estimate_item(self):
        item = explain_readiness(declared_readiness(0.2))
        assert item.is_estimate is False

    def test_readiness_states_it_is_a_declaration(self):
        item = explain_readiness(declared_readiness(0.2))
        assert any("Déclaration" in reason for reason in item.reasons)

    def test_a_recent_but_not_today_declaration_drops_today(self):
        item = explain_readiness(declared_readiness(0.2, age_days=2))
        assert "aujourd'hui" not in item.message

    def test_a_stale_declaration_is_only_context(self):
        stale = ReadinessSignal(
            overall=0.9, age_days=9, sufficiency=Sufficiency.STALE)
        item = explain_readiness(stale)
        assert item.message == rx.READINESS_STALE_MESSAGE

    def test_a_stale_good_declaration_never_becomes_encouragement(self):
        stale = ReadinessSignal(
            overall=0.95, age_days=9, sufficiency=Sufficiency.STALE)
        item = explain_readiness(stale)
        assert "en forme" not in item.message

    def test_no_declaration_yields_no_readiness_item(self):
        assert explain_readiness(ReadinessSignal()) is None

    def test_no_declaration_yields_a_data_prompt_instead(self):
        detailed = build_detailed_explanation(state_with(zone()))
        assert detailed.data_prompt is not None

    def test_a_declaration_removes_the_prompt(self):
        state = state_with(zone(), readiness=declared_readiness(0.5))
        assert build_detailed_explanation(state).data_prompt is None

    def test_a_stale_declaration_is_not_pushed_to_proactive_surfaces(self):
        stale = ReadinessSignal(
            overall=0.9, age_days=9, sufficiency=Sufficiency.STALE)
        state = state_with(zone(), readiness=stale)
        assert build_proactive_explanation(state).readiness_item is None

    def test_a_stale_declaration_is_kept_on_the_detailed_surface(self):
        stale = ReadinessSignal(
            overall=0.9, age_days=9, sufficiency=Sufficiency.STALE)
        state = state_with(zone(), readiness=stale)
        assert build_detailed_explanation(state).readiness_item is not None

    def test_the_wording_thresholds_are_named_not_inline(self):
        source = inspect.getsource(explain_readiness)
        assert "0.4" not in source

    def test_the_good_threshold_is_named_too(self):
        source = inspect.getsource(explain_readiness)
        assert "0.7" not in source


# ---------------------------------------------------------------------------
# AXES MACRO — consommés, jamais recalculés
# ---------------------------------------------------------------------------


class TestMacroAxis:
    def test_axes_are_built_from_the_canonical_rollup(self):
        state = state_with(
            zone(), zone(code=ZONE_POSTERIOR), zone(code="calves"))
        detailed = build_detailed_explanation(state)
        assert [item.subject for item in detailed.macro_items] == [AXIS_LOWER]

    def test_the_limiting_zone_is_explained(self):
        state = state_with(
            zone(),
            zone(code=ZONE_POSTERIOR, estimate=0.1,
                 band=RecoveryBand.LIKELY_FATIGUED),
            zone(code="calves"),
        )
        detailed = build_detailed_explanation(state)
        reasons = " ".join(detailed.macro_items[0].reasons)
        assert ZONE_LABELS[ZONE_POSTERIOR] in reasons

    def test_core_is_never_attached_to_an_axis(self):
        state = state_with(zone(code=ZONE_CORE))
        detailed = build_detailed_explanation(state)
        assert detailed.macro_items == ()

    def test_core_remains_present_at_the_detailed_level(self):
        state = state_with(zone(code=ZONE_CORE))
        detailed = build_detailed_explanation(state)
        assert detailed.zone_items[0].subject == ZONE_CORE

    def test_axes_follow_the_canonical_display_order(self):
        state = state_with(zone(), zone(code=ZONE_PECS))
        detailed = build_detailed_explanation(state)
        subjects = [item.subject for item in detailed.macro_items]
        expected = [key for key in RADAR_AXIS_ORDER if key in subjects]
        assert subjects == expected

    def test_the_explainer_does_no_rollup_arithmetic(self):
        """Aucun opérateur de calcul dans la couche de langage macro.

        Si `explain_axis` recalculait un agrégat, il pourrait diverger
        silencieusement de `build_macro_recovery`. Le seul chemin autorisé est
        la consommation du résultat déjà produit.
        """
        source = inspect.getsource(explain_axis)
        assert not re.search(r"[+\-*/]=|\bmin\(|\bmax\(|\bsum\(", source)

    def test_an_unknown_axis_becomes_a_data_state_not_a_band(self):
        axis = MacroAxisRecovery(axis_key=AXIS_LOWER)
        assert explain_axis(axis).is_estimate is False

    def test_an_unknown_axis_still_names_its_limiting_zone_if_known(self):
        axis = MacroAxisRecovery(
            axis_key=AXIS_LOWER, limiting_zone_code=ZONE_QUADS)
        reasons = " ".join(explain_axis(axis).reasons)
        assert ZONE_LABELS[ZONE_QUADS] in reasons


# ---------------------------------------------------------------------------
# DÉTERMINISME
# ---------------------------------------------------------------------------


class TestDeterminism:
    def test_two_renders_of_one_state_are_identical(self):
        state = new_user_state()
        first = build_detailed_explanation(state)
        second = build_detailed_explanation(state)
        assert first == second

    def test_rendered_text_is_byte_identical(self):
        state = new_user_state()
        first = rendered_strings(build_detailed_explanation(state))
        second = rendered_strings(build_detailed_explanation(state))
        assert first == second

    def test_the_proactive_surface_is_deterministic_too(self):
        state = state_with(zone(), zone(code=ZONE_PECS))
        first = build_proactive_explanation(state)
        second = build_proactive_explanation(state)
        assert first == second

    def test_the_module_reads_no_clock(self):
        source = inspect.getsource(rx)
        assert "datetime.now" not in source

    def test_the_module_uses_no_randomness(self):
        source = inspect.getsource(rx)
        assert "random" not in source

    def test_the_module_calls_no_model(self):
        source = inspect.getsource(rx)
        assert "openai" not in source.lower()

    def test_the_module_touches_no_database(self):
        source = inspect.getsource(rx)
        assert "Session" not in source

    def test_the_module_does_not_import_the_recommendation_engine(self):
        source = inspect.getsource(rx)
        assert "recommendation" not in source

    def test_the_module_does_not_import_the_behavioral_producer(self):
        source = inspect.getsource(rx)
        assert "behavioral" not in source

    def test_the_surfaces_are_tagged(self):
        detailed = build_detailed_explanation(new_user_state())
        assert detailed.surface == SURFACE_DETAILED

    def test_the_proactive_surface_is_tagged(self):
        proactive = build_proactive_explanation(new_user_state())
        assert proactive.surface == SURFACE_PROACTIVE

    def test_the_layer_is_versioned_independently(self):
        detailed = build_detailed_explanation(new_user_state())
        assert detailed.version == EXPLAINER_VERSION


# ---------------------------------------------------------------------------
# CONFIANCE — ordinale, jamais chiffrée, jamais HIGH
# ---------------------------------------------------------------------------


class TestConfidenceExposure:
    def test_high_is_never_rendered_as_high(self):
        assert confidence_label(Confidence.HIGH) != "Confiance élevée"

    def test_high_degrades_to_the_maximum_renderable_level(self):
        assert confidence_label(Confidence.HIGH) == confidence_label(
            MAX_RENDERABLE_CONFIDENCE)

    def test_the_renderable_ceiling_matches_what_the_contract_produces(self):
        from app.services.recovery_contract import CARDIO_MAX_CONFIDENCE

        assert MAX_RENDERABLE_CONFIDENCE is CARDIO_MAX_CONFIDENCE

    def test_a_high_confidence_estimate_is_clamped_on_the_item(self):
        item = explain_zone(zone(confidence=Confidence.HIGH))
        assert item.confidence is MAX_RENDERABLE_CONFIDENCE

    def test_no_label_contains_a_digit(self):
        digits = [
            label for label in rx.CONFIDENCE_LABELS.values()
            if any(char.isdigit() for char in label)
        ]
        assert digits == []

    def test_no_label_contains_a_percent_sign(self):
        percents = [
            label for label in rx.CONFIDENCE_LABELS.values() if "%" in label
        ]
        assert percents == []

    def test_every_renderable_confidence_has_a_label(self):
        renderable = {Confidence.MEDIUM, Confidence.LOW, Confidence.NONE}
        assert renderable <= set(rx.CONFIDENCE_LABELS)


# ---------------------------------------------------------------------------
# GARDE-FOU DE FORMULATION — sur la sortie rendue, et il doit MORDRE
# ---------------------------------------------------------------------------


def representative_states() -> list[TrainingState]:
    """États couvrant chaque chemin de rendu."""
    return [
        new_user_state(),
        state_with(zone()),
        state_with(zone(band=RecoveryBand.LIKELY_FATIGUED,
                        confidence=Confidence.LOW,
                        basis=(SUBSTRING_BASIS, CARDIO_BASIS_VELO),
                        signals=(SIGNAL_STRENGTH, SIGNAL_CARDIO))),
        state_with(zone(estimate=0.5, band=RecoveryBand.PARTIALLY_RECOVERED)),
        state_with(zone(), readiness=declared_readiness(0.1)),
        state_with(zone(), readiness=declared_readiness(0.99)),
        state_with(
            zone(),
            readiness=ReadinessSignal(overall=0.9, age_days=9,
                                      sufficiency=Sufficiency.STALE),
        ),
        TrainingState(
            computed_at=NOW,
            zone_recovery=(zone(),),
            fatigue=FatigueSignal(
                cardio_component=0.6,
                basis=(MODALITY_BASIS_VELO, "average BPM recorded", "1200 kcal"),
            ),
        ),
        TrainingState(
            computed_at=NOW,
            zone_recovery=(zone(),),
            fatigue=FatigueSignal(
                cardio_component=0.6,
                basis=("modality outside the known vocabulary: 'x'",),
            ),
        ),
    ]


def every_rendered_string() -> list[str]:
    strings: list[str] = []
    for state in representative_states():
        for builder in (build_detailed_explanation, build_proactive_explanation):
            strings.extend(rendered_strings(builder(state)))
    return strings


class TestRenderedWordingGuard:
    def test_the_real_public_output_is_clean(self):
        assert wording_violations(tuple(every_rendered_string())) == ()

    def test_no_rendered_string_contains_a_percent_sign(self):
        offenders = [text for text in every_rendered_string() if "%" in text]
        assert offenders == []

    def test_no_rendered_string_claims_a_recovery_duration(self):
        pattern = re.compile(r"\d+\s*(?:h|heures?)\b")
        offenders = [
            text for text in every_rendered_string() if pattern.search(text)
        ]
        assert offenders == []

    def test_no_internal_identifier_leaks_into_rendered_text(self):
        pattern = re.compile(r"\b[a-z]{2,}_[a-z]{2,}\b")
        offenders = [
            text for text in every_rendered_string() if pattern.search(text)
        ]
        assert offenders == []

    def test_an_unrecognised_basis_is_omitted_rather_than_dumped(self):
        item = explain_zone(zone(
            basis=("brand_new internal sentinel NEVER_TRAINED_HOURS",)))
        assert "NEVER_TRAINED_HOURS" not in " ".join(item.reasons)

    def test_an_unrecognised_basis_adds_no_invented_reason(self):
        clean = explain_zone(zone())
        noisy = explain_zone(zone(basis=("totally unmapped engineering prose",)))
        assert noisy.reasons == clean.reasons

    # --- preuve que le garde-fou mord ------------------------------------

    def test_the_guard_catches_a_physiological_claim(self):
        planted = ("Cette zone est physiologiquement récupérée.",)
        assert wording_violations(planted) != ()

    def test_the_guard_catches_a_measured_activation_claim(self):
        planted = ("Activation mesurée sur les quadriceps.",)
        assert wording_violations(planted) != ()

    def test_the_guard_catches_an_injury_claim(self):
        planted = ("Risque de blessure sur cette zone.",)
        assert wording_violations(planted) != ()

    def test_the_guard_catches_a_therapeutic_prescription(self):
        planted = ("Prescription : deux jours de repos complet.",)
        assert wording_violations(planted) != ()

    def test_the_guard_catches_a_percentage(self):
        planted = ("Quadriceps récupérés à 80 %.",)
        assert wording_violations(planted) != ()

    def test_the_guard_catches_an_exact_recovery_hour_claim(self):
        planted = ("Il te faut encore 24 heures pour cette zone.",)
        assert wording_violations(planted) != ()

    def test_the_guard_catches_a_bpm_claim(self):
        planted = ("Ton cardio à 145 bpm a chargé le bas du corps.",)
        assert wording_violations(planted) != ()

    def test_the_guard_catches_an_internal_identifier(self):
        planted = ("Basé sur strength_load pour cette zone.",)
        assert wording_violations(planted) != ()

    def test_the_guard_bites_through_the_real_public_explainer(self, monkeypatch):
        """Violation plantée dans le vrai module, pas dans une chaîne de test.

        C'est la preuve qui compte : si demain quelqu'un réécrit une phrase de
        bande en langage interdit, le test qui scanne la sortie publique
        échoue — le garde-fou n'est pas une liste décorative.
        """
        monkeypatch.setitem(
            rx.BAND_MESSAGES,
            RecoveryBand.LIKELY_AVAILABLE,
            "Cette zone est physiologiquement récupérée à 100 %.",
        )
        detailed = build_detailed_explanation(state_with(zone()))
        assert wording_violations(rendered_strings(detailed)) != ()

    def test_a_planted_decision_sentence_is_caught_through_the_explainer(
        self, monkeypatch
    ):
        monkeypatch.setitem(
            rx.BAND_MESSAGES,
            RecoveryBand.LIKELY_AVAILABLE,
            "Tu dois augmenter la charge sur cette zone.",
        )
        detailed = build_detailed_explanation(state_with(zone()))
        assert wording_violations(rendered_strings(detailed)) != ()

    def test_a_planted_leak_in_a_reason_is_caught(self, monkeypatch):
        monkeypatch.setitem(
            rx.SIGNAL_REASONS, SIGNAL_STRENGTH, "Vu via zone_code interne.")
        detailed = build_detailed_explanation(state_with(zone()))
        assert wording_violations(rendered_strings(detailed)) != ()

    def test_machine_codes_are_not_scanned_as_rendered_text(self):
        """`delt_lat` est un code, pas du texte affiché.

        Sans cette exclusion le motif anti-fuite condamnerait le vocabulaire
        canonique lui-même, et la seule issue serait d'affaiblir le motif.
        """
        detailed = build_detailed_explanation(new_user_state())
        assert "delt_lat" not in rendered_strings(detailed)


# ---------------------------------------------------------------------------
# AUCUN LANGAGE DE DÉCISION
# ---------------------------------------------------------------------------

DECISION_VERBS = (
    "augmente", "baisse", "remplace", "reporte", "repose-toi",
    "entraîne-toi", "skip", "ajoute des séries", "fais une séance",
    "tu peux pousser", "tu devrais",
)


class TestNoDecisionLanguage:
    @pytest.mark.parametrize("verb", DECISION_VERBS)
    def test_no_rendered_string_gives_a_training_order(self, verb):
        offenders = [
            text for text in every_rendered_string() if verb in text.lower()
        ]
        assert offenders == []

    def test_the_only_imperative_is_about_data_collection(self):
        assert "Renseigne" in rx.DATA_PROMPT_MESSAGE

    def test_the_data_prompt_says_nothing_about_training(self):
        assert "séance" not in rx.DATA_PROMPT_MESSAGE.lower()

    def test_the_data_prompt_is_kept_out_of_the_estimates(self):
        detailed = build_detailed_explanation(new_user_state())
        assert detailed.data_prompt not in detailed.zone_items

    def test_no_session_is_ranked(self):
        source = inspect.getsource(rx)
        assert "WorkoutSession" not in source

    def test_no_volume_is_adjusted(self):
        source = inspect.getsource(rx)
        assert "sets" not in source

    def test_the_layer_exposes_no_overall_score(self):
        detailed = build_detailed_explanation(state_with(zone(estimate=0.87)))
        assert "0.87" not in " ".join(rendered_strings(detailed))

    def test_the_numeric_estimate_never_reaches_an_item(self):
        item = explain_zone(zone(estimate=0.87))
        assert not hasattr(item, "estimate")


# ---------------------------------------------------------------------------
# BOUT EN BOUT SUR UN ÉTAT RÉEL
# ---------------------------------------------------------------------------


def _live_state(client, *, with_history: bool):
    """Un `TrainingState` construit depuis la base réelle, pas une fabrique.

    Les imports sont locaux : la `conftest` purge `app.*` de `sys.modules` à
    chaque test, et un symbole lié à la collecte appartiendrait à une autre
    génération du module que celui que la fixture `client` a chargé.
    """
    from app.database import SessionLocal
    from app.models.session import SessionExercise, WorkoutSession
    from app.services.training_state import build_training_state
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    if with_history:
        with SessionLocal() as db:
            session = WorkoutSession(
                user_id=uid,
                template_slug_snapshot="push-a",
                template_name_snapshot="Push A",
                started_at=NOW.replace(tzinfo=None) - timedelta(days=1),
                status="completed",
                global_state="good",
                concentration="high",
                cardio_duration_min=25,
                cardio_bpm_avg=130,
                cardio_machine_type="velo",
                cardio_machine_calories=300,
            )
            session.session_exercises.append(SessionExercise(
                exercise_code_snapshot="E1",
                exercise_name_snapshot="Développé couché barre",
                position=1,
            ))
            db.add(session)
            db.commit()
    with SessionLocal() as db:
        return build_training_state(db, uid, now=NOW)


class TestAgainstLivePersistedState:
    def test_a_real_empty_account_renders_without_violation(self, client):
        from app.services import recovery_explainer as live

        state = _live_state(client, with_history=False)
        detailed = live.build_detailed_explanation(state)
        assert live.wording_violations(live.rendered_strings(detailed)) == ()

    def test_a_real_empty_account_claims_nothing_about_the_body(self, client):
        from app.services import recovery_explainer as live

        state = _live_state(client, with_history=False)
        assert live.build_detailed_explanation(state).zone_items == ()

    def test_a_real_empty_account_keeps_every_zone_visible(self, client):
        from app.services import recovery_explainer as live

        state = _live_state(client, with_history=False)
        zones = [
            item for item in live.build_detailed_explanation(state).data_state_items
            if item.kind == live.KIND_ZONE_RECOVERY
        ]
        assert len(zones) == 11

    def test_a_real_account_with_history_renders_without_violation(self, client):
        from app.services import recovery_explainer as live

        state = _live_state(client, with_history=True)
        detailed = live.build_detailed_explanation(state)
        assert live.wording_violations(live.rendered_strings(detailed)) == ()

    def test_a_real_account_with_history_renders_real_estimates(self, client):
        from app.services import recovery_explainer as live

        state = _live_state(client, with_history=True)
        assert live.build_detailed_explanation(state).zone_items != ()

    def test_real_persisted_cardio_never_leaks_its_raw_fields(self, client):
        """Les 300 kcal et les 130 bpm sont en base — ils ne doivent pas sortir."""
        from app.services import recovery_explainer as live

        state = _live_state(client, with_history=True)
        detailed = live.build_detailed_explanation(state)
        text = " ".join(live.rendered_strings(detailed))
        assert "300" not in text

    def test_real_persisted_bpm_never_leaks(self, client):
        from app.services import recovery_explainer as live

        state = _live_state(client, with_history=True)
        detailed = live.build_detailed_explanation(state)
        text = " ".join(live.rendered_strings(detailed))
        assert "130" not in text

    def test_the_proactive_surface_of_a_real_account_is_clean(self, client):
        from app.services import recovery_explainer as live

        state = _live_state(client, with_history=True)
        proactive = live.build_proactive_explanation(state)
        assert live.wording_violations(live.rendered_strings(proactive)) == ()


# ---------------------------------------------------------------------------
# NON-RÉGRESSION DE LA COUCHE HÉRITÉE
# ---------------------------------------------------------------------------


class TestLegacyExplainerUntouched:
    def test_the_legacy_explainer_is_not_imported(self):
        source = inspect.getsource(rx)
        assert "recommendation_explainer" not in source

    def test_the_legacy_explainer_still_exposes_its_entry_point(self):
        from app.services.recommendation_explainer import explain_recommendation

        assert callable(explain_recommendation)

    def test_the_two_layers_use_different_confidence_vocabularies(self):
        """La couche héritée dit `ok`/`low`, celle-ci dit une bande ordinale.

        Rien n'est aligné de force : les deux coexistent, et la conversion
        canonique reste `confidence_from_legacy_label` dans le contrat.

        `Confidence` est réimporté ici : la `conftest` purge `app.*` entre les
        tests, et comparer par identité un membre issu d'une autre génération du
        module échouerait pour une raison qui n'a rien à voir avec le contrat.
        """
        from app.services.recovery_contract import (
            Confidence as LiveConfidence,
        )
        from app.services.recovery_contract import confidence_from_legacy_label

        assert confidence_from_legacy_label("moyenne") is LiveConfidence.MEDIUM

    def test_the_kinds_are_a_closed_vocabulary(self):
        assert set(rx.EXPLANATION_KINDS) == {
            KIND_ZONE_RECOVERY, KIND_MACRO_AXIS, KIND_READINESS,
            KIND_CARDIO, KIND_DATA_PROMPT,
        }
