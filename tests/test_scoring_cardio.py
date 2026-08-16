"""Tests for cardio session quality scoring (Sb_06 etape 3).

Validates the new cardio dispatcher and formula per Sx_06 §2.3.
"""
from __future__ import annotations

from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Test fixtures (no DB roundtrip needed)
# ---------------------------------------------------------------------------


@dataclass
class FakeSetLog:
    kind: str = "work"
    completed: bool = False


@dataclass
class FakeSessionExercise:
    set_logs: list = field(default_factory=list)
    success_score: int | None = None


@dataclass
class FakeTemplate:
    kind: str = "cardio"


@dataclass
class FakeSession:
    template: FakeTemplate | None = None
    session_exercises: list = field(default_factory=list)
    concentration: str | None = None
    global_state: str | None = None
    cardio_duration_min: int | None = None
    cardio_bpm_avg: int | None = None
    cardio_machine_calories: int | None = None
    cardio_machine_type: str | None = None


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------


def test_dispatcher_routes_cardio_to_cardio():
    from app.services.quality_score import compute_session_quality

    session = FakeSession(
        template=FakeTemplate(kind="cardio"),
        cardio_duration_min=20,
        concentration="high",
        global_state="good",
    )
    score = compute_session_quality(session)
    assert score >= 85  # Well-executed LISS


def test_dispatcher_routes_strength_to_strength():
    from app.services.quality_score import compute_session_quality

    session = FakeSession(
        template=FakeTemplate(kind="strength"),
        session_exercises=[
            FakeSessionExercise(
                set_logs=[FakeSetLog(kind="work", completed=True) for _ in range(3)],
                success_score=100,
            ),
        ],
        concentration="high",
        global_state="good",
    )
    score = compute_session_quality(session)
    assert score == 100  # Perfect strength session


def test_dispatcher_defaults_to_strength_when_template_none():
    from app.services.quality_score import compute_session_quality

    session = FakeSession(template=None)
    score = compute_session_quality(session)
    # Empty strength session → 0 for work/score + 0 for subjective
    assert score == 0


# ---------------------------------------------------------------------------
# Cardio formula — scenarios
# ---------------------------------------------------------------------------


def test_cardio_liss_25min_zone_cible_full_feedback():
    """Perfect LISS: 25min, BPM 125, abs complete, subjective good."""
    from app.services.quality_score import compute_session_quality_cardio

    session = FakeSession(
        template=FakeTemplate(kind="cardio"),
        cardio_duration_min=25,
        cardio_bpm_avg=125,
        session_exercises=[
            FakeSessionExercise(
                set_logs=[FakeSetLog(kind="work", completed=True) for _ in range(3)],
            ),
        ],
        concentration="high",
        global_state="good",
    )
    score = compute_session_quality_cardio(session)
    # 50 + 20 + 20 + 10 = 100
    assert score == 100


def test_cardio_liss_20min_zone_cible_no_feedback():
    """LISS 20min, zone cible, pas de feedback subjectif."""
    from app.services.quality_score import compute_session_quality_cardio

    session = FakeSession(
        template=FakeTemplate(kind="cardio"),
        cardio_duration_min=20,
        cardio_bpm_avg=125,
    )
    score = compute_session_quality_cardio(session)
    # 50 + 20 + 20 (no exs = full credit) + 0 = 90
    assert score == 90


def test_cardio_liss_20min_no_bpm_full_subjective():
    """LISS 20min, pas de BPM mesure, feedback good."""
    from app.services.quality_score import compute_session_quality_cardio

    session = FakeSession(
        template=FakeTemplate(kind="cardio"),
        cardio_duration_min=20,
        concentration="high",
        global_state="good",
    )
    score = compute_session_quality_cardio(session)
    # 50 + 15 (baseline no bpm) + 20 + 10 = 95
    assert score == 95


def test_cardio_short_10min():
    """Cardio court 10min dans zone, pas d'abs, feedback moyen."""
    from app.services.quality_score import compute_session_quality_cardio

    session = FakeSession(
        template=FakeTemplate(kind="cardio"),
        cardio_duration_min=10,
        cardio_bpm_avg=120,
        concentration="medium",
        global_state="flat",
    )
    score = compute_session_quality_cardio(session)
    # 25 + 20 + 20 + 6 = 71
    assert score == 71


def test_cardio_missing_duration():
    """Cardio sans duration → 0 duration component."""
    from app.services.quality_score import compute_session_quality_cardio

    session = FakeSession(
        template=FakeTemplate(kind="cardio"),
        cardio_duration_min=None,
        cardio_bpm_avg=125,
        concentration="high",
        global_state="good",
    )
    score = compute_session_quality_cardio(session)
    # 0 + 20 + 20 + 10 = 50
    assert score == 50


def test_cardio_bpm_out_of_zone():
    """BPM hors zone (trop intense)."""
    from app.services.quality_score import compute_session_quality_cardio

    session = FakeSession(
        template=FakeTemplate(kind="cardio"),
        cardio_duration_min=20,
        cardio_bpm_avg=160,  # Out of zone
    )
    score = compute_session_quality_cardio(session)
    # 50 + 5 + 20 + 0 = 75
    assert score == 75


def test_cardio_liss_abs_partial_completion():
    """LISS avec abs partiellement completes."""
    from app.services.quality_score import compute_session_quality_cardio

    session = FakeSession(
        template=FakeTemplate(kind="cardio"),
        cardio_duration_min=25,
        cardio_bpm_avg=125,
        session_exercises=[
            FakeSessionExercise(
                set_logs=[
                    FakeSetLog(kind="work", completed=True),
                    FakeSetLog(kind="work", completed=True),
                    FakeSetLog(kind="work", completed=False),
                    FakeSetLog(kind="work", completed=False),
                ],
            ),
        ],
        concentration="high",
        global_state="good",
    )
    score = compute_session_quality_cardio(session)
    # 50 + 20 + 10 (2/4 work done = 50%) + 10 = 90
    assert score == 90


# ---------------------------------------------------------------------------
# Strength formula — regression (unchanged)
# ---------------------------------------------------------------------------


def test_strength_perfect():
    from app.services.quality_score import compute_session_quality_strength

    session = FakeSession(
        session_exercises=[
            FakeSessionExercise(
                set_logs=[FakeSetLog(kind="work", completed=True) for _ in range(3)],
                success_score=100,
            ),
        ],
        concentration="high",
        global_state="good",
    )
    # 40 + 40 + 10 + 10 = 100
    assert compute_session_quality_strength(session) == 100


def test_strength_null_success_score():
    from app.services.quality_score import compute_session_quality_strength

    session = FakeSession(
        session_exercises=[
            FakeSessionExercise(
                set_logs=[FakeSetLog(kind="work", completed=True) for _ in range(3)],
                success_score=None,
            ),
        ],
        concentration="high",
        global_state="good",
    )
    # 40 + 0 + 10 + 10 = 60
    assert compute_session_quality_strength(session) == 60


def test_strength_empty():
    from app.services.quality_score import compute_session_quality_strength

    session = FakeSession(session_exercises=[])
    assert compute_session_quality_strength(session) == 0
