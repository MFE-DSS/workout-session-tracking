"""Sb_24.5 — quality_score V2 tests (Sx_24 §F.2).

Hard contracts validated (par ordre de criticité) :

1. INVARIANCE ABSOLUE V1 — scoring_version=1 → ancien formule bit-pour-bit.
   La protection : ``compute_session_quality_strength()`` est inchangé,
   et le dispatcher ne le touche que sur les sessions V2.

2. V2 = 0.75·V1 + 0.25·implicit_avg quand au moins un exo est labellé.

3. V2 = V1 (fallback) si aucun exo de la session n'a d'implicit_label.

4. Cardio non concerné — formule cardio inchangée pour V1 et V2.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.services.implicit_signal import LABEL_SCORE_CONTRIBUTION, ImplicitLabel
from app.services.quality_score import (
    W_IMPLICIT,
    W_V1,
    _implicit_signal_avg,
    compute_session_quality,
    compute_session_quality_strength,
)


# ---------------------------------------------------------------------------
# Helpers — fake session with full control over fields
# ---------------------------------------------------------------------------


def _fake_set_log(weight=80, reps=10, kind="work", completed=True):
    sl = MagicMock()
    sl.weight_kg = weight
    sl.reps = reps
    sl.kind = kind
    sl.completed = completed
    return sl


def _fake_session_exercise(
    set_logs=None, success_score=80, implicit_label=None
):
    se = MagicMock()
    se.set_logs = set_logs or []
    se.success_score = success_score
    se.implicit_label = implicit_label
    return se


def _fake_session(
    template_kind="strength",
    scoring_version=1,
    session_exercises=None,
    concentration="high",
    global_state="good",
):
    s = MagicMock()
    s.template = MagicMock()
    s.template.kind = template_kind
    s.scoring_version = scoring_version
    s.session_exercises = session_exercises or []
    s.concentration = concentration
    s.global_state = global_state
    s.cardio_duration_min = None
    s.cardio_bpm_avg = None
    return s


def _three_completed_work_sets():
    return [
        _fake_set_log(80, 10, "work", True),
        _fake_set_log(80, 8, "work", True),
        _fake_set_log(80, 6, "work", True),
    ]


# ---------------------------------------------------------------------------
# 1. INVARIANCE V1 — bit-pour-bit identique avant/après Sb_24.5
# ---------------------------------------------------------------------------


def test_v1_session_returns_legacy_score():
    """Une session avec scoring_version=1 doit produire EXACTEMENT le
    résultat de l'ancienne formule (compute_session_quality_strength)."""
    se = _fake_session_exercise(set_logs=_three_completed_work_sets())
    s = _fake_session(scoring_version=1, session_exercises=[se])

    v1_direct = compute_session_quality_strength(s)
    via_dispatcher = compute_session_quality(s)
    assert v1_direct == via_dispatcher


def test_v1_invariant_even_when_implicit_label_present():
    """Cas critique : une session V1 qui se trouve avoir un implicit_label
    (cas théorique impossible sur prod mais hardlock le contrat) NE DOIT
    PAS voir son score modifié par la V2 formula."""
    se = _fake_session_exercise(
        set_logs=_three_completed_work_sets(),
        implicit_label="trajectoire_coherente",  # label présent
    )
    s = _fake_session(scoring_version=1, session_exercises=[se])  # mais V1
    v1_pure = compute_session_quality_strength(s)
    via_dispatcher = compute_session_quality(s)
    assert via_dispatcher == v1_pure, (
        "V1 must IGNORE implicit_label entirely — even if it's there"
    )


def test_v1_default_when_scoring_version_attribute_missing():
    """Backward compat : un mock sans scoring_version → fallback V1."""
    se = _fake_session_exercise(set_logs=_three_completed_work_sets())
    s = _fake_session(session_exercises=[se])
    del s.scoring_version  # force missing attribute
    v1 = compute_session_quality_strength(s)
    out = compute_session_quality(s)
    assert out == v1


# ---------------------------------------------------------------------------
# 2. V2 formula correctness — 0.75·V1 + 0.25·implicit_avg
# ---------------------------------------------------------------------------


def test_v2_blends_v1_and_implicit_when_label_present():
    """V2 = 0.75·V1 + 0.25·avg(contributions)."""
    se = _fake_session_exercise(
        set_logs=_three_completed_work_sets(),
        implicit_label=ImplicitLabel.TRAJECTOIRE_COHERENTE.value,
    )
    s = _fake_session(scoring_version=2, session_exercises=[se])
    v1 = compute_session_quality_strength(s)
    implicit_contrib = LABEL_SCORE_CONTRIBUTION[ImplicitLabel.TRAJECTOIRE_COHERENTE]
    expected = round(W_V1 * v1 + W_IMPLICIT * implicit_contrib)
    assert compute_session_quality(s) == expected


def test_v2_uses_average_across_multiple_labels():
    """Multi-exercice : l'implicit_avg est la moyenne des contributions."""
    se_a = _fake_session_exercise(
        set_logs=_three_completed_work_sets(),
        implicit_label=ImplicitLabel.TRAJECTOIRE_COHERENTE.value,  # 90
    )
    se_b = _fake_session_exercise(
        set_logs=_three_completed_work_sets(),
        implicit_label=ImplicitLabel.RESERVE_PROBABLE.value,  # 30
    )
    s = _fake_session(scoring_version=2, session_exercises=[se_a, se_b])
    avg = (90 + 30) / 2  # = 60
    v1 = compute_session_quality_strength(s)
    expected = round(W_V1 * v1 + W_IMPLICIT * avg)
    assert compute_session_quality(s) == expected


def test_v2_ignores_unlabeled_exercises_in_average():
    """Un exo sans implicit_label n'entre pas dans la moyenne (spec §F.2)."""
    se_labeled = _fake_session_exercise(
        set_logs=_three_completed_work_sets(),
        implicit_label=ImplicitLabel.RESERVE_PROBABLE.value,
    )
    se_unlabeled = _fake_session_exercise(
        set_logs=_three_completed_work_sets(),
        implicit_label=None,
    )
    s = _fake_session(scoring_version=2, session_exercises=[se_labeled, se_unlabeled])
    # avg = 30 (single labeled exo only)
    v1 = compute_session_quality_strength(s)
    expected = round(W_V1 * v1 + W_IMPLICIT * 30)
    assert compute_session_quality(s) == expected


def test_v2_falls_back_to_v1_when_no_label_at_all():
    """Si aucun exo n'est labellé → V2 = V1 (pas de score artificiel)."""
    se = _fake_session_exercise(
        set_logs=_three_completed_work_sets(),
        implicit_label=None,
    )
    s = _fake_session(scoring_version=2, session_exercises=[se])
    v1 = compute_session_quality_strength(s)
    assert compute_session_quality(s) == v1


def test_v2_bounded_to_100():
    """Cap supérieur — un V1 de 100 + label 90 ne déborde pas."""
    # Forcer V1 = 100 (success_score 100 partout)
    se = _fake_session_exercise(
        set_logs=_three_completed_work_sets(),
        success_score=100,
        implicit_label=ImplicitLabel.TRAJECTOIRE_COHERENTE.value,
    )
    s = _fake_session(scoring_version=2, session_exercises=[se])
    out = compute_session_quality(s)
    assert 0 <= out <= 100


def test_v2_bounded_to_zero():
    """Cap inférieur — V1=0 + reserve_probable (30) ≈ 8, jamais négatif."""
    se = _fake_session_exercise(
        set_logs=[],  # no work sets → V1 components mostly 0
        success_score=None,
        implicit_label=ImplicitLabel.RESERVE_PROBABLE.value,
    )
    s = _fake_session(
        scoring_version=2,
        session_exercises=[se],
        concentration=None,
        global_state=None,
    )
    out = compute_session_quality(s)
    assert 0 <= out <= 100


# ---------------------------------------------------------------------------
# 3. Cardio inchangé — scoring_version sans effet
# ---------------------------------------------------------------------------


def test_cardio_v1_and_v2_identical():
    """Une session cardio doit produire le même score quelle que soit
    sa scoring_version (le dispatcher la route vers la formule cardio
    qui n'a pas de notion d'implicit)."""
    s_v1 = _fake_session(template_kind="cardio", scoring_version=1)
    s_v1.cardio_duration_min = 25
    s_v1.cardio_bpm_avg = 125

    s_v2 = _fake_session(template_kind="cardio", scoring_version=2)
    s_v2.cardio_duration_min = 25
    s_v2.cardio_bpm_avg = 125

    assert compute_session_quality(s_v1) == compute_session_quality(s_v2)


# ---------------------------------------------------------------------------
# 4. _implicit_signal_avg edge cases
# ---------------------------------------------------------------------------


def test_implicit_avg_handles_invalid_label_value():
    """Si quelqu'un (humain via SQL direct) écrit une string non-enum
    dans implicit_label, on l'ignore au lieu de crasher."""
    se = _fake_session_exercise(implicit_label="not_a_real_label")
    s = _fake_session(scoring_version=2, session_exercises=[se])
    assert _implicit_signal_avg(s) is None


def test_implicit_avg_returns_float_when_label_present():
    se = _fake_session_exercise(
        implicit_label=ImplicitLabel.PYRAMIDAL_ASCENDANT.value,
    )
    s = _fake_session(scoring_version=2, session_exercises=[se])
    avg = _implicit_signal_avg(s)
    assert avg == LABEL_SCORE_CONTRIBUTION[ImplicitLabel.PYRAMIDAL_ASCENDANT]


# ---------------------------------------------------------------------------
# 5. Parametric — sanity battery on all 5 labels
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("label", list(ImplicitLabel))
def test_v2_formula_works_for_each_label(label):
    """Pour chacun des 5 labels, V2 doit produire un score valide
    et différent (ou égal) à V1 selon la contribution."""
    se = _fake_session_exercise(
        set_logs=_three_completed_work_sets(),
        implicit_label=label.value,
    )
    s = _fake_session(scoring_version=2, session_exercises=[se])
    out = compute_session_quality(s)
    assert 0 <= out <= 100
    v1 = compute_session_quality_strength(s)
    contrib = LABEL_SCORE_CONTRIBUTION[label]
    expected = round(W_V1 * v1 + W_IMPLICIT * contrib)
    assert out == expected
