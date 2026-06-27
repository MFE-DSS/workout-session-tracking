"""Sb_31.1 — Tests du composeur Body Intelligence v2.

Couvre les contrats verbatim du brief :
- insufficient_data si données trop faibles
- partial_data si certaines métriques clés manquent
- ok si données suffisantes
- BMI calculé seulement si height ET weight
- BMI étiqueté ``derived``, jamais ``measured``
- aucun verdict esthétique / composition corporelle / médical
- max 3 priorités
- ordre de priorité déterministe
- seuils figés et testés
- dataclasses frozen
- fonction déterministe à input égal
- aucune dépendance DB / router / template / fichier
- overload compliance explicitement non calculée V1
"""

from __future__ import annotations

import importlib

import pytest

from app.services.body_intelligence import (
    BODY_INTELLIGENCE_VERSION,
    DEFAULT_LIMITS,
    IMBALANCE_HIGH_RATIO,
    IMBALANCE_LOW_RATIO,
    LOW_CONFIDENCE_THRESHOLD,
    LOW_QUALITY_THRESHOLD,
    MAX_PRIORITIES,
    MIN_QUALITY_SAMPLE,
    MIN_SESSIONS_CONSISTENCY_30D,
    MIN_SESSIONS_OK,
    RADAR_AXIS_ORDER,
    BodyIntelligenceBlock,
    BodyIntelligenceInput,
    BodyIntelligencePriority,
    BodyIntelligenceSnapshot,
    compute_body_intelligence,
)

# ───────── helpers ─────────


def _solid_zones() -> dict[str, int]:
    """Zones équilibrées : push≈pull≈8, upper/lower ≈ 20/11 = 1.82 (sous le
    seuil IMBALANCE_HIGH_RATIO=2.0)."""
    return {
        "pecs": 4,
        "shoulders": 4,
        "back_width": 4,
        "back_thickness": 4,
        "arms": 4,
        "lower": 11,
    }


def _solid_input(**overrides) -> BodyIntelligenceInput:
    base = dict(
        sessions_7d=3,
        sessions_30d=12,
        sessions_90d=36,
        work_sets_per_week_30d=24,
        cardio_minutes_per_week_30d=90,
        strength_volume_delta_pct_30d=5.0,
        zone_session_counts_30d=_solid_zones(),
        dominant_pattern_30d="push_horizontal",
        pattern_distribution_30d={
            "push_horizontal": 4,
            "pull_horizontal": 4,
            "squat": 3,
        },
        quality_score_avg_30d=78.0,
        quality_score_n=12,
        confidence_score_avg=80.0,
        implicit_labels_30d={"trajectoire_coherente": 8, "reserve_probable": 2},
        body_height_cm=180,
        body_weight_kg=78.0,
        body_weight_measured_at_iso="2026-06-27",
        waist_cm=82.0,
        weight_trend_90d_kg=0.4,
    )
    base.update(overrides)
    return BodyIntelligenceInput(**base)


# ───────── version + structure ─────────


def test_engine_version_is_one():
    assert BODY_INTELLIGENCE_VERSION == 1
    snap = compute_body_intelligence(BodyIntelligenceInput())
    assert snap.engine_version == 1


def test_dataclasses_are_frozen():
    snap = compute_body_intelligence(_solid_input())
    with pytest.raises(Exception):
        snap.engine_version = 2  # type: ignore[misc]
    with pytest.raises(Exception):
        snap.blocks[0].title = "x"  # type: ignore[misc]
    with pytest.raises(Exception):
        snap.priorities[0].message = "x" if snap.priorities else "x"  # type: ignore[misc]


def test_module_has_no_db_or_framework_imports():
    """Garde structurelle : le composeur ne doit importer ni la DB,
    ni FastAPI, ni Jinja, ni le réseau."""
    import inspect

    from app.services import body_intelligence

    src = inspect.getsource(body_intelligence)
    forbidden = (
        "from sqlalchemy",
        "import sqlalchemy",
        "from app.database",
        "from app.models",
        "from fastapi",
        "import fastapi",
        "from jinja",
        "import jinja",
        "import requests",
        "from urllib",
        "import socket",
        "open(",
        "Path(",
    )
    for tok in forbidden:
        assert tok not in src, f"forbidden import / I/O token in composer: {tok!r}"


# ───────── status ─────────


def test_status_insufficient_data_when_too_few_sessions():
    snap = compute_body_intelligence(BodyIntelligenceInput(sessions_30d=2))
    assert snap.status == "insufficient_data"
    assert "Données insuffisantes" in snap.headline


def test_status_ok_on_solid_input():
    snap = compute_body_intelligence(_solid_input())
    assert snap.status == "ok"
    assert "30 derniers jours" in snap.headline


def test_status_partial_data_when_zone_counts_missing():
    inp = _solid_input(zone_session_counts_30d={})
    snap = compute_body_intelligence(inp)
    assert snap.status == "partial_data"


def test_status_partial_data_when_quality_block_unavailable():
    inp = _solid_input(quality_score_avg_30d=None, confidence_score_avg=None)
    snap = compute_body_intelligence(inp)
    assert snap.status == "partial_data"


# ───────── blocs ─────────


def test_seven_blocks_always_emitted():
    snap = compute_body_intelligence(_solid_input())
    keys = [b.key for b in snap.blocks]
    assert keys == [
        "training_consistency",
        "body_metrics",
        "muscle_zone_balance",
        "push_pull_legs_balance",
        "quality_and_confidence",
        "implicit_signal_summary",
        "unavailable_or_limits",
    ]


def test_unavailable_or_limits_always_present_and_marked():
    snap = compute_body_intelligence(BodyIntelligenceInput())
    limits_block = next(b for b in snap.blocks if b.key == "unavailable_or_limits")
    assert limits_block.available is True
    assert limits_block.classification == "not_deductible"


# ───────── BMI ─────────


def test_bmi_computed_when_height_and_weight_present():
    snap = compute_body_intelligence(_solid_input())
    bm = next(b for b in snap.blocks if b.key == "body_metrics")
    # 78 / 1.80² = 24.07 → 24.1
    assert bm.content["bmi"] == 24.1
    assert bm.content["bmi_classification"] == "derived"


def test_bmi_none_when_height_missing():
    snap = compute_body_intelligence(_solid_input(body_height_cm=None))
    bm = next(b for b in snap.blocks if b.key == "body_metrics")
    assert bm.content["bmi"] is None


def test_bmi_none_when_weight_missing():
    snap = compute_body_intelligence(_solid_input(body_weight_kg=None))
    bm = next(b for b in snap.blocks if b.key == "body_metrics")
    assert bm.content["bmi"] is None


def test_bmi_never_classified_as_measured():
    snap = compute_body_intelligence(_solid_input())
    bm = next(b for b in snap.blocks if b.key == "body_metrics")
    assert bm.content["bmi_classification"] != "measured"


# ───────── priorités ─────────


def test_priorities_capped_at_max_3():
    # Cas pathologique : peu de séances + qualité basse + déséquilibre +
    # zone manquante. L'arbre doit toujours rester ≤ MAX_PRIORITIES.
    inp = _solid_input(
        sessions_30d=4,
        quality_score_avg_30d=30.0,
        quality_score_n=4,
        confidence_score_avg=30.0,
        zone_session_counts_30d={"pecs": 6, "shoulders": 4, "back_width": 0},
    )
    snap = compute_body_intelligence(inp)
    assert len(snap.priorities) <= MAX_PRIORITIES
    assert len(snap.priorities) <= 3


def test_priority_insufficient_data_fires_first_and_blocks_others():
    snap = compute_body_intelligence(BodyIntelligenceInput(sessions_30d=1))
    assert len(snap.priorities) == 1
    assert snap.priorities[0].key == "insufficient_data"


def test_priority_low_logging_confidence():
    inp = _solid_input(
        quality_score_avg_30d=40.0,
        quality_score_n=12,
        confidence_score_avg=40.0,
    )
    snap = compute_body_intelligence(inp)
    keys = [p.key for p in snap.priorities]
    assert "low_logging_confidence" in keys


def test_priority_consistency_gap():
    inp = _solid_input(sessions_30d=5)
    snap = compute_body_intelligence(inp)
    keys = [p.key for p in snap.priorities]
    assert "consistency_gap" in keys


def test_priority_imbalance_gap_when_push_pull_skewed():
    inp = _solid_input(
        zone_session_counts_30d={
            "pecs": 8,
            "shoulders": 8,
            "back_width": 1,
            "back_thickness": 1,
            "arms": 2,
            "lower": 4,
        }
    )
    snap = compute_body_intelligence(inp)
    keys = [p.key for p in snap.priorities]
    assert "imbalance_gap" in keys


def test_priority_undertrained_zone():
    zones = _solid_zones()
    zones["arms"] = 0
    inp = _solid_input(zone_session_counts_30d=zones)
    snap = compute_body_intelligence(inp)
    keys = [p.key for p in snap.priorities]
    assert "undertrained_zone" in keys


def test_priority_stable_or_progressing_default():
    snap = compute_body_intelligence(_solid_input())
    keys = [p.key for p in snap.priorities]
    assert keys == ["stable_or_progressing"]


def test_priorities_are_deterministic_order():
    # 2 cas : qualité basse + consistency_gap → low_logging_confidence
    # doit venir AVANT consistency_gap (ordre figé spec §6).
    inp = _solid_input(
        sessions_30d=5,
        quality_score_avg_30d=40.0,
        quality_score_n=5,
    )
    snap = compute_body_intelligence(inp)
    keys = [p.key for p in snap.priorities]
    assert keys.index("low_logging_confidence") < keys.index("consistency_gap")


# ───────── seuils figés ─────────


def test_thresholds_are_constants_and_typed():
    assert isinstance(MIN_SESSIONS_OK, int)
    assert isinstance(MIN_SESSIONS_CONSISTENCY_30D, int)
    assert isinstance(LOW_QUALITY_THRESHOLD, float)
    assert isinstance(LOW_CONFIDENCE_THRESHOLD, float)
    assert isinstance(IMBALANCE_LOW_RATIO, float)
    assert isinstance(IMBALANCE_HIGH_RATIO, float)
    assert isinstance(MAX_PRIORITIES, int)
    assert isinstance(MIN_QUALITY_SAMPLE, int)
    # Cohérence : low < high pour les ratios.
    assert IMBALANCE_LOW_RATIO < IMBALANCE_HIGH_RATIO


def test_radar_axis_order_matches_muscle_mapping():
    """Garde anti-drift : si muscle_mapping bouge, on saute aux yeux."""
    from app.services.muscle_mapping import RADAR_AXIS_ORDER as canonical

    assert tuple(RADAR_AXIS_ORDER) == tuple(canonical)


# ───────── déterminisme ─────────


def test_compute_is_deterministic():
    inp = _solid_input()
    a = compute_body_intelligence(inp)
    b = compute_body_intelligence(inp)
    assert a == b


def test_compute_returns_snapshot_type():
    snap = compute_body_intelligence(BodyIntelligenceInput())
    assert isinstance(snap, BodyIntelligenceSnapshot)
    assert all(isinstance(b, BodyIntelligenceBlock) for b in snap.blocks)
    assert all(isinstance(p, BodyIntelligencePriority) for p in snap.priorities)


# ───────── vocabulaire — anti-pseudo-science ─────────


def _all_strings(snap: BodyIntelligenceSnapshot) -> list[str]:
    out: list[str] = [snap.headline]
    out.extend(snap.bullets)
    out.extend(snap.limits)
    for b in snap.blocks:
        out.append(b.title)
        for v in b.content.values():
            if isinstance(v, str):
                out.append(v)
    for p in snap.priorities:
        out.append(p.message)
        out.append(p.reason)
    return out


@pytest.mark.parametrize(
    "scenario",
    [
        BodyIntelligenceInput(),  # insufficient
        _solid_input(),
        _solid_input(sessions_30d=5),
        _solid_input(quality_score_avg_30d=30.0, quality_score_n=5),
        _solid_input(
            zone_session_counts_30d={
                "pecs": 10,
                "shoulders": 6,
                "back_width": 1,
                "back_thickness": 1,
                "arms": 4,
                "lower": 4,
            }
        ),
    ],
)
def test_no_aesthetic_or_medical_wording_anywhere(scenario):
    snap = compute_body_intelligence(scenario)
    forbidden = (
        "tu es déséquilibré",
        "tu es gras",
        "tu es sec",
        "ton physique est",
        "ton taux de gras",
        "ta posture",
        "symétrie corporelle",
        "diagnostic",
        "problème médical",
        "tu dois",
        "il faut absolument",
        "obligatoire",
    )
    blob = " | ".join(_all_strings(snap)).lower()
    for tok in forbidden:
        assert tok not in blob, f"forbidden token {tok!r} in snapshot wording"


def test_authorized_vocabulary_used_when_appropriate():
    """Les messages doivent privilégier ``semble`` / ``à confirmer`` /
    ``données insuffisantes`` / ``zone moins représentée`` etc."""
    insufficient = compute_body_intelligence(BodyIntelligenceInput(sessions_30d=2))
    blob_ins = " | ".join(_all_strings(insufficient)).lower()
    assert "données insuffisantes" in blob_ins

    zones = _solid_zones()
    zones["arms"] = 0
    snap = compute_body_intelligence(
        _solid_input(zone_session_counts_30d=zones)
    )
    blob = " | ".join(_all_strings(snap)).lower()
    assert "zone moins représentée" in blob


# ───────── overload compliance non calculée V1 ─────────


def test_overload_compliance_not_calculated_v1():
    snap = compute_body_intelligence(_solid_input())
    limits_block = next(b for b in snap.blocks if b.key == "unavailable_or_limits")
    assert (
        limits_block.content.get("overload_compliance_status")
        == "not_available_v1"
    )


def test_no_overload_compliance_block_emitted():
    snap = compute_body_intelligence(_solid_input())
    keys = [b.key for b in snap.blocks]
    assert "overload_compliance" not in keys


# ───────── limits par défaut ─────────


def test_default_limits_exposed():
    snap = compute_body_intelligence(_solid_input())
    assert snap.limits == DEFAULT_LIMITS
    # Doivent mentionner explicitement composition / esthétique / posture.
    blob = " ".join(snap.limits).lower()
    assert "composition" in blob
    assert "esthétique" in blob
    assert "posture" in blob


# ───────── ratios ─────────


def test_push_pull_ratio_none_when_pull_zero():
    inp = _solid_input(
        zone_session_counts_30d={
            "pecs": 4,
            "shoulders": 4,
            "back_width": 0,
            "back_thickness": 0,
            "arms": 2,
            "lower": 4,
        }
    )
    snap = compute_body_intelligence(inp)
    ppl = next(b for b in snap.blocks if b.key == "push_pull_legs_balance")
    assert ppl.content["push_pull_ratio"] is None


def test_upper_lower_ratio_none_when_lower_zero():
    zones = _solid_zones()
    zones["lower"] = 0
    inp = _solid_input(zone_session_counts_30d=zones)
    snap = compute_body_intelligence(inp)
    ppl = next(b for b in snap.blocks if b.key == "push_pull_legs_balance")
    assert ppl.content["upper_lower_ratio"] is None


# ───────── output sérialisable simple ─────────


def test_block_content_only_uses_simple_scalars_and_collections():
    """Garde : ``content`` reste sérialisable pour faciliter le
    rendu Jinja (Sb_31.2) — pas d'objets opaques."""
    snap = compute_body_intelligence(_solid_input())
    for b in snap.blocks:
        for k, v in b.content.items():
            assert isinstance(
                v, (int, float, str, bool, list, dict, tuple, type(None))
            ), f"block {b.key}.{k} carries non-trivial type {type(v).__name__}"


def test_module_importable_without_side_effects():
    """Re-importer le module ne doit pas avoir d'effet de bord."""
    importlib.reload(
        importlib.import_module("app.services.body_intelligence")
    )
