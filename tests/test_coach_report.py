"""Sb_23 — Coach Report tests.

Hard contracts validated:
* /coach-report 200 for authenticated user, 303→login when anon
* 10 blocks present, each carries a {Mesuré, Inféré, Non déductible} tag
* 4 forbiddens never appear in the rendered HTML (esthétique,
  pronostic morphologique, verdict performance max, comparaison users)
* inference rules produce deterministic outputs from a fake report
"""
from __future__ import annotations

import pytest

# ---------------------------------------------------------------------------
# Endpoint smoke + ownership
# ---------------------------------------------------------------------------


def test_coach_report_requires_auth(client):
    """Anonymous access redirects to /login (like every private route)."""
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    r = client.get("/coach-report", follow_redirects=False)
    assert r.status_code == 303
    assert "/login" in r.headers.get("location", "")


def test_coach_report_200_for_authenticated_user(client):
    r = client.get("/coach-report")
    assert r.status_code == 200
    body = r.text
    # Page identity
    assert "Coach Report" in body
    assert "@testuser" in body


def test_coach_report_contains_10_blocks(client):
    """Each of the 10 blocks of the report must be present. Titles are
    "1. Identité physique" … "10. Garde-fous"."""
    r = client.get("/coach-report")
    body = r.text
    expected_titles = [
        "1. Identité physique",
        "2. Volume et fréquence",
        "3. Ratio strength",
        "4. Répartition par zone",
        "5. Patterns moteurs",
        "6. Discipline de logging",
        "7. Points forts probables",
        "8. Points faibles probables",
        "9. Axes de travail",
        "10. Garde-fous",
    ]
    for title in expected_titles:
        assert title in body, f"missing block titled '{title}'"


def test_coach_report_carries_explicit_tags(client):
    r = client.get("/coach-report")
    body = r.text
    # The triptyque must appear visibly somewhere in the document.
    assert "Mesuré" in body
    assert "Inféré" in body
    assert "Non déductible" in body


# ---------------------------------------------------------------------------
# §B.bis forbiddens (no aesthetic / morphological / perf / inter-user)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("forbidden", [
    "physique harmonieux",
    "bel équilibre",
    "vous êtes fort",
    "vous êtes faible",
    "vous prenez de la masse",
    "vous perdez du gras",
    "top 20%",
    "supérieur à la moyenne",
])
def test_coach_report_forbidden_phrases_absent(client, forbidden):
    """Spec Sx_23 v1.1 §B.bis — these classes of statement must NEVER
    appear in the rendered coach report."""
    r = client.get("/coach-report")
    assert forbidden.lower() not in r.text.lower(), (
        f"Forbidden phrase '{forbidden}' surfaced in coach report"
    )


def test_coach_report_guardrails_block_visible(client):
    r = client.get("/coach-report")
    body = r.text
    # The fixed §10 garde-fous block must be present.
    assert "ne remplace pas" in body
    assert "avis médical" in body


# ---------------------------------------------------------------------------
# coach_inference deterministic rules — fake CoachReport synthetic test
# ---------------------------------------------------------------------------


def _fake_report(
    sessions_30d=10,
    cardio_min_per_week=60,
    top_zone_n=5,
    neglected_zone_n=0,
    dominant_pattern_pct=42,
    discipline_bw_rate=30,
):
    """Build a minimal CoachReport-shaped namespace for inference tests."""
    from app.services.coach_report import (
        CoachReport,
        IdentityBlock,
        ImplicitSignalsBlock,
        PatternsBlock,
        VolumeBlock,
        ZonesBlock,
    )
    from app.services.profile_metrics import (
        DisciplineRates,
        StrengthCardioRatio,
    )
    return CoachReport(
        identity=IdentityBlock(
            username="u", report_date="2026-05-31",
            height_cm=178, weight_kg=78.5, weight_trend_kg_90d=None,
            waist_cm=None, resting_hr=None,
            bp_systolic=None, bp_diastolic=None, year_of_birth=None,
        ),
        volume=VolumeBlock(
            sessions_30d=sessions_30d, sessions_90d=sessions_30d * 3,
            streak_days=2, cardio_minutes_per_week=cardio_min_per_week,
            work_sets_per_week=50,
        ),
        ratio=StrengthCardioRatio(10, 7, 3, 70, 30),
        zones=ZonesBlock(
            counts=[("pecs", "Pectoraux", top_zone_n),
                    ("lower", "Lower", neglected_zone_n)],
            top_zones=[("pecs", "Pectoraux", top_zone_n)],
            neglected_zones=[("lower", "Lower", neglected_zone_n)],
        ),
        patterns=PatternsBlock(
            distribution=[("push_horizontal", dominant_pattern_pct)],
            dominant=("push_horizontal", dominant_pattern_pct),
        ),
        discipline=DisciplineRates(
            sessions_total=sessions_30d, completion_rate=90,
            with_free_note_rate=70, with_bodyweight_rate=discipline_bw_rate,
            with_sensation_rate=60, avg_quality_score=72,
        ),
        last_session=None,
        # Sb_24.7 — bloc Implicite vide par défaut pour les tests
        # d'inférence (qui ne s'en servent pas).
        implicit_signals=ImplicitSignalsBlock(
            total_labeled_exercises=0, distribution=[], dominant=None,
        ),
    )


def test_inference_strong_point_when_top_zone_active():
    from app.services.coach_inference import strong_points
    rep = _fake_report(top_zone_n=5)
    out = strong_points(rep)
    assert len(out) == 1
    assert "Pectoraux" in out[0]
    assert "probable" in out[0].lower()


def test_inference_no_strong_point_when_top_zone_too_low():
    from app.services.coach_inference import strong_points
    rep = _fake_report(top_zone_n=1)
    assert strong_points(rep) == []


def test_inference_weak_point_when_zone_neglected():
    from app.services.coach_inference import weak_points
    rep = _fake_report(neglected_zone_n=0)
    out = weak_points(rep)
    assert len(out) == 1
    assert "Lower" in out[0]
    assert "probable" in out[0].lower()


def test_inference_suggested_axes_cardio_when_low():
    from app.services.coach_inference import suggested_axes
    rep = _fake_report(cardio_min_per_week=30)
    out = suggested_axes(rep)
    assert any("cardio" in axis.lower() for axis in out)
    assert len(out) <= 3


def test_inference_suggested_axes_pattern_when_overweighted():
    from app.services.coach_inference import suggested_axes
    rep = _fake_report(dominant_pattern_pct=60)
    out = suggested_axes(rep)
    assert any("push_horizontal" in axis for axis in out)


def test_inference_axes_capped_at_3():
    from app.services.coach_inference import suggested_axes
    rep = _fake_report(
        cardio_min_per_week=10,
        dominant_pattern_pct=60,
        discipline_bw_rate=10,
        sessions_30d=2,
        neglected_zone_n=0,
    )
    out = suggested_axes(rep)
    assert len(out) <= 3
