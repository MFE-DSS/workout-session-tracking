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
        # `TRAIN1-D` / C1 — le bloc 9 prescrivait ; il compte désormais
        # ce que les données NE couvrent pas. Le rapport garde ses 10 blocs.
        "9. Couverture des données",
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
            sessions_14d=2, cardio_minutes_per_week=cardio_min_per_week,
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


# ── `TRAIN1-D` / C1 — LES PRESCRIPTIONS SONT RETIRÉES ────────────────────────
#
# Les trois tests remplacés ici EXIGEAIENT les consignes : « un axe cardio
# apparaît quand le volume est bas », « un axe pattern apparaît quand un
# pattern domine », « au plus trois axes ». Ils sont retournés plutôt que
# supprimés — qui lit l'ancien contrat doit tomber sur ce qui l'a annulé.


def test_the_external_guideline_is_a_reference_never_a_target():
    """La recommandation OMS reste citée — c'est une référence de santé
    publique légitime dans un document destiné à un tiers. Ce qui est retiré,
    c'est sa conversion en objectif calculé pour quelqu'un dont AUREN ignore
    l'âge et l'état de santé."""
    from app.services.coach_inference import external_references

    out = external_references(_fake_report(cardio_min_per_week=30))
    assert len(out) == 1
    assert "OMS" in out[0]
    assert "150" in out[0]
    assert "cible" not in out[0].lower()
    assert "objectif calculé pour toi" in out[0]


def test_the_reference_does_not_depend_on_being_below_it():
    """Une référence qui n'apparaît QUE lorsqu'on est en dessous n'est pas une
    référence : c'est un reproche déclenché par un seuil. Elle est donc rendue
    à l'identique quel que soit le volume."""
    from app.services.coach_inference import external_references

    low = external_references(_fake_report(cardio_min_per_week=10))
    high = external_references(_fake_report(cardio_min_per_week=400))
    assert low == high


def test_no_training_prescription_survives_anywhere_in_the_inference():
    """La garde de fond, et elle est plus stricte que le plafond de trois
    axes qu'elle remplace : sur un compte qui déclenchait AUTREFOIS les cinq
    prescriptions à la fois, aucun verbe de consigne ne doit subsister."""
    from app.services.coach_inference import build_inference

    blocks = build_inference(_fake_report(
        cardio_min_per_week=10,
        dominant_pattern_pct=60,
        discipline_bw_rate=10,
        sessions_30d=2,
        neglected_zone_n=0,
    ))
    produced = " ".join(
        blocks.strong_points + blocks.weak_points
        + blocks.coverage_gaps + blocks.external_references
    ).lower()
    for verb in ("viser", "augmenter", "rééquilibrer", "diversifier",
                 "intégrer", "logger", "indispensable"):
        assert verb not in produced, f"consigne rendue : « {verb} »"


def test_coverage_gaps_are_facts_not_instructions():
    """La discipline de logging devient un fait de COUVERTURE : quelle part
    des séances porte la donnée. Aucun impératif, aucun « indispensable »."""
    from app.services.coach_inference import coverage_gaps

    out = coverage_gaps(_fake_report(discipline_bw_rate=10))
    assert any("Poids de corps" in line for line in out)
    assert all("%" in line for line in out)


# ── `UX4_03B` — le streak quitte le rapport coach (`OPERATOR_DECISION` D7) ───


def test_the_coach_report_no_longer_counts_consecutive_days():
    """Le rapport affichait « Streak », un compteur de jours calendaires
    consécutifs — punissant un jour de repos correctement pris, et venant d'un
    SECOND producteur aux règles différentes de celui du moteur comportemental
    (jour de grâce et filtres d'un côté, rupture stricte et aucun filtre de
    l'autre). Deux surfaces pouvaient afficher deux valeurs le même jour.
    """
    import pathlib
    import re as _re

    tpl = (pathlib.Path(__file__).resolve().parent.parent
           / "app/templates/coach_report.html")
    body = _re.sub(r"\{#.*?#\}", " ", tpl.read_text(encoding="utf-8"),
                   flags=_re.S)
    for banned in ("Streak", "streak_days", "jours de série"):
        assert banned not in body, f"le streak est revenu : « {banned} »"


def test_the_replacement_shipped_in_the_same_slice():
    """`CLAUDE.md §5.3` — jamais une soustraction seule. Sans cette garde,
    retirer « Streak » laisserait le bloc plus pauvre qu'avant, et le test
    précédent serait vert."""
    import pathlib
    import re as _re

    tpl = (pathlib.Path(__file__).resolve().parent.parent
           / "app/templates/coach_report.html")
    body = _re.sub(r"\{#.*?#\}", " ", tpl.read_text(encoding="utf-8"),
                   flags=_re.S)
    assert "Séances 14 j" in body
    assert "report.volume.sessions_14d" in body
