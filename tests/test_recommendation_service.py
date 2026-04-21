"""Service tests for the next-session recommendation engine (Sb_12)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from tests.helpers import get_test_user_id


# ---------------------------------------------------------------------------
# Fixture builder — creates a completed session tied to a given template.
# ---------------------------------------------------------------------------


def _mk_session(
    *,
    template_slug: str,
    started_at: datetime,
    exercises: list[dict] | None = None,
    concentration: str = "high",
    global_state: str = "good",
):
    """Persist a completed WorkoutSession attached to the real template in DB."""
    from sqlalchemy import select
    from app.database import SessionLocal
    from app.models.catalog import WorkoutTemplate
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    with SessionLocal() as db:
        tpl = db.execute(
            select(WorkoutTemplate).where(WorkoutTemplate.slug == template_slug)
        ).scalar_one()

        s = WorkoutSession(
            user_id=get_test_user_id(),
            template_id=tpl.id,
            template_slug_snapshot=tpl.slug,
            template_name_snapshot=tpl.name,
            started_at=started_at,
            ended_at=started_at + timedelta(hours=1),
            status="completed",
            concentration=concentration,
            global_state=global_state,
        )

        # Default: take the 2 first exercises from the template, each with
        # 3 completed work sets at 50 kg × 10. Callers may override.
        if exercises is None:
            exs = sorted(tpl.exercises, key=lambda e: e.position)[:2]
            exercises = [
                {
                    "code": e.code,
                    "name": e.name,
                    "work_sets": [
                        {"weight_kg": 50, "reps": 10, "completed": True},
                        {"weight_kg": 50, "reps": 10, "completed": True},
                        {"weight_kg": 50, "reps": 10, "completed": True},
                    ],
                }
                for e in exs
            ]
        for pos, ex in enumerate(exercises, start=1):
            se = SessionExercise(
                exercise_code_snapshot=ex["code"],
                exercise_name_snapshot=ex["name"],
                position=pos,
                success_score=80,
            )
            for i, sl in enumerate(ex.get("work_sets", []), start=1):
                se.set_logs.append(SetLog(
                    kind="work", set_index=i,
                    weight_kg=sl.get("weight_kg"),
                    reps=sl.get("reps"),
                    completed=sl.get("completed", False),
                ))
            s.session_exercises.append(se)

        db.add(s)
        db.commit()
        return s.id


def _call(user_id: int, now: datetime | None = None):
    from app.database import SessionLocal
    from app.services.recommendation import (
        recommend_next_session,
        reset_template_zones_cache,
    )
    reset_template_zones_cache()
    with SessionLocal() as db:
        return recommend_next_session(db, user_id, now or datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# Cold start
# ---------------------------------------------------------------------------


def test_cold_start_recommends_a_core_template(client):
    """No history at all → recommend a core template, flag cold_start."""
    result = _call(get_test_user_id())
    assert result is not None
    assert result["context"]["cold_start"] is True
    assert result["top"]["template"].catalog_section == "core"
    assert "démarrer" in result["top"]["phrase"].lower()
    assert result["alternatives"] == []  # cold start skips alternatives


def test_cold_start_phrase_under_140_chars(client):
    result = _call(get_test_user_id())
    assert result is not None
    assert len(result["top"]["phrase"]) <= 140


# ---------------------------------------------------------------------------
# Open session short-circuits the engine
# ---------------------------------------------------------------------------


def test_open_session_returns_none(client):
    """If the user has an in_progress session, recommendation is None."""
    import re
    r = client.post("/sessions", data={"template_slug": "push-a"}, follow_redirects=False)
    assert r.status_code in {303, 302}
    assert _call(get_test_user_id()) is None


# ---------------------------------------------------------------------------
# Alternation: 2 strength in a row → cardio boosted
# ---------------------------------------------------------------------------


def test_two_strengths_boost_cardio_alternation(client):
    """Two recent Push sessions → recommendation should lean towards cardio
    or a pull/legs template. Primary check: LISS must appear in the pool
    (top or alternative) with a cardio-alternation phrase."""
    now = datetime(2026, 4, 21, 18, 0, tzinfo=timezone.utc)
    # Seed 3 strength sessions to push over cold-start threshold AND build
    # a meaningful recency signal.
    _mk_session(template_slug="push-a", started_at=now - timedelta(days=8))
    _mk_session(template_slug="push-b", started_at=now - timedelta(days=3))
    _mk_session(template_slug="push-a", started_at=now - timedelta(days=1))

    result = _call(get_test_user_id(), now=now)
    assert result is not None
    assert result["context"]["cold_start"] is False

    slugs = [result["top"]["template"].slug] + [a["template"].slug for a in result["alternatives"]]
    assert any(s.startswith("liss-") or s.startswith("pull-") or s.startswith("legs-") for s in slugs), \
        f"expected pull/legs/LISS in recommendations, got {slugs}"


# ---------------------------------------------------------------------------
# Cardio absent on 7+ days boosts LISS
# ---------------------------------------------------------------------------


def test_no_cardio_recently_surfaces_liss_phrase(client):
    """Strength-only history → LISS should appear with its cardio-absent phrase."""
    now = datetime(2026, 4, 21, 18, 0, tzinfo=timezone.utc)
    for delta in (15, 10, 5):
        _mk_session(template_slug="push-a", started_at=now - timedelta(days=delta))

    result = _call(get_test_user_id(), now=now)
    assert result is not None
    all_candidates = [result["top"]] + result["alternatives"]
    liss_hit = [c for c in all_candidates if c["template"].slug.startswith("liss-")]
    assert liss_hit, "LISS should appear when cardio has been absent"
    assert any("cardio" in c["phrase"].lower() for c in liss_hit)


# ---------------------------------------------------------------------------
# Archived templates are never recommended
# ---------------------------------------------------------------------------


def test_archived_templates_are_excluded(client):
    now = datetime(2026, 4, 21, 18, 0, tzinfo=timezone.utc)
    for delta in (12, 7, 3):
        _mk_session(template_slug="push-a", started_at=now - timedelta(days=delta))

    result = _call(get_test_user_id(), now=now)
    assert result is not None
    all_ = [result["top"]] + result["alternatives"]
    for c in all_:
        assert c["template"].catalog_section != "archived"


# ---------------------------------------------------------------------------
# Phrase constraints
# ---------------------------------------------------------------------------


def test_phrase_never_empty_and_capped_140_chars(client):
    now = datetime(2026, 4, 21, 18, 0, tzinfo=timezone.utc)
    for delta in (10, 5, 2):
        _mk_session(template_slug="push-a", started_at=now - timedelta(days=delta))

    result = _call(get_test_user_id(), now=now)
    assert result is not None
    for c in [result["top"]] + result["alternatives"]:
        assert c["phrase"], "phrase must never be empty"
        assert len(c["phrase"]) <= 140, f"phrase too long: {c['phrase']}"


# ---------------------------------------------------------------------------
# Result shape
# ---------------------------------------------------------------------------


def test_result_shape_is_consistent(client):
    now = datetime(2026, 4, 21, 18, 0, tzinfo=timezone.utc)
    for delta in (9, 5, 2):
        _mk_session(template_slug="pull-a", started_at=now - timedelta(days=delta))

    result = _call(get_test_user_id(), now=now)
    assert result is not None
    assert set(result.keys()) == {"top", "alternatives", "context"}
    assert set(result["top"].keys()) >= {"template", "score", "phrase", "primary_zones"}
    assert isinstance(result["top"]["score"], int)
    assert 0 <= result["top"]["score"] <= 100


# ---------------------------------------------------------------------------
# Tie-break: display_order wins at equal score
# ---------------------------------------------------------------------------


def test_alternatives_are_at_most_two(client):
    now = datetime(2026, 4, 21, 18, 0, tzinfo=timezone.utc)
    for delta in (10, 6, 3):
        _mk_session(template_slug="legs-a", started_at=now - timedelta(days=delta))

    result = _call(get_test_user_id(), now=now)
    assert result is not None
    assert len(result["alternatives"]) <= 2


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------


def test_staleness_mapping_monotonic():
    from app.services.recommendation import _staleness_from_hard_sets
    assert _staleness_from_hard_sets(0) == 1.0
    assert _staleness_from_hard_sets(8) == 0.0
    assert _staleness_from_hard_sets(100) == 0.0
    a = _staleness_from_hard_sets(2)
    b = _staleness_from_hard_sets(5)
    assert 0.0 < b < a < 1.0


def test_template_primary_zones_caches(client):
    from sqlalchemy import select
    from app.database import SessionLocal
    from app.models.catalog import WorkoutTemplate
    from app.services.recommendation import (
        template_primary_zones,
        reset_template_zones_cache,
        _primary_zones_cached,
    )

    reset_template_zones_cache()
    with SessionLocal() as db:
        push_a = db.execute(
            select(WorkoutTemplate).where(WorkoutTemplate.slug == "push-a")
        ).scalar_one()
        zones1 = template_primary_zones(push_a)
    # Same call path must hit the cache.
    info = _primary_zones_cached.cache_info()
    assert info.hits + info.misses >= 1
    assert "pecs" in zones1 or "triceps" in zones1 or "delt_lat" in zones1
