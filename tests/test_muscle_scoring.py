"""Tests for muscle mapping, scoring, and dashboard."""
from __future__ import annotations

from app.services.muscle_mapping import (
    RADAR_AXES,
    ZONE_LABELS,
    classify_exercise,
)


def test_zone_labels_has_11_zones():
    assert len(ZONE_LABELS) == 11


def test_radar_axes_has_6():
    assert len(RADAR_AXES) == 6


def test_classify_chest_press():
    zone, secondary = classify_exercise("Chest Press machine")
    assert zone == "pecs"
    assert "triceps" in secondary


def test_classify_incline_smith():
    zone, _ = classify_exercise("Incline Smith Press")
    assert zone == "pecs"


def test_classify_lateral_raise():
    zone, _ = classify_exercise("Élévations latérales câble")
    assert zone == "delt_lat"


def test_classify_face_pull():
    zone, _ = classify_exercise("Face pull câble")
    assert zone == "delt_post"


def test_classify_lat_pulldown():
    zone, secondary = classify_exercise("Tirage poulie haute prise neutre")
    assert zone == "lats"
    assert "biceps" in secondary


def test_classify_rowing():
    zone, _ = classify_exercise("Rowing machine chest-supported")
    assert zone == "upper_back"


def test_classify_curl():
    zone, _ = classify_exercise("Curl incliné haltères")
    assert zone == "biceps"


def test_classify_triceps():
    zone, _ = classify_exercise("Triceps extension poulie haute")
    assert zone == "triceps"


def test_classify_hack_squat():
    zone, _ = classify_exercise("Hack Squat machine")
    assert zone == "quads"


def test_classify_rdl():
    zone, _ = classify_exercise("Romanian Deadlift haltères")
    assert zone == "posterior"


def test_classify_calf():
    zone, _ = classify_exercise("Relevés mollets debout")
    assert zone == "calves"


def test_classify_ab_wheel():
    zone, _ = classify_exercise("Roulette abdominale (ab wheel rollout)")
    assert zone == "core"


def test_classify_unknown():
    zone, secondary = classify_exercise("Exercice inconnu xyz")
    assert zone == "unknown"
    assert secondary == []


def test_classify_butterfly():
    zone, _ = classify_exercise("Butterfly pec machine")
    assert zone == "pecs"


def test_classify_dips():
    zone, _ = classify_exercise("Dips pectoraux (buste penché)")
    assert zone == "pecs"


def test_classify_skull_crushers():
    zone, _ = classify_exercise("Skull crushers EZ-bar")
    assert zone == "triceps"


def test_classify_leg_curl():
    zone, _ = classify_exercise("Leg curls assis")
    assert zone == "posterior"


def test_classify_leg_extension():
    zone, _ = classify_exercise("Leg extensions assises")
    assert zone == "quads"


def test_classify_hip_thrust():
    zone, _ = classify_exercise("Hip thrust Smith machine")
    assert zone == "posterior"


def test_classify_shoulder_press():
    zone, _ = classify_exercise("Machine shoulder press")
    assert zone == "delt_lat"


# ---------------------------------------------------------------------------
# Scoring service + radar SVG tests
# ---------------------------------------------------------------------------
from datetime import UTC, datetime, timedelta

from tests.helpers import get_test_user_id


def _add_session_with_sets(client, user_id, exercise_name, sets_data, days_ago=0):
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    now = datetime.now(UTC)
    with SessionLocal() as db:
        s = WorkoutSession(
            user_id=user_id,
            template_slug_snapshot="test",
            template_name_snapshot="Test",
            started_at=now - timedelta(days=days_ago),
            status="completed",
        )
        se = SessionExercise(
            exercise_code_snapshot="E1",
            exercise_name_snapshot=exercise_name,
            position=1,
        )
        for i, (weight, reps) in enumerate(sets_data, 1):
            se.set_logs.append(SetLog(
                kind="work", set_index=i, completed=True,
                weight_kg=weight, reps=reps,
            ))
        s.session_exercises.append(se)
        db.add(s)
        db.commit()


def test_compute_dashboard_empty(client):
    from app.database import SessionLocal
    from app.services.muscle_scoring import compute_physique_dashboard

    uid = get_test_user_id()
    with SessionLocal() as db:
        dash = compute_physique_dashboard(db, uid)

    assert dash.global_score >= 0
    assert len(dash.zone_scores) == 11
    assert len(dash.radar_axes) == 6
    assert dash.radar_svg
    for z in dash.zone_scores:
        assert z.confidence == "faible"


def test_compute_dashboard_with_data(client):
    from app.database import SessionLocal
    from app.services.muscle_scoring import compute_physique_dashboard

    uid = get_test_user_id()
    for d in [28, 21, 14, 7, 3, 1]:
        _add_session_with_sets(client, uid, "Chest Press machine",
                               [(60, 10), (60, 10), (60, 10)], days_ago=d)

    with SessionLocal() as db:
        dash = compute_physique_dashboard(db, uid)

    pecs = next(z for z in dash.zone_scores if z.zone == "pecs")
    assert pecs.score > 0
    assert pecs.hard_sets > 0
    assert len(pecs.top_exercises) > 0


def test_radar_axes_aggregate_zones(client):
    from app.database import SessionLocal
    from app.services.muscle_scoring import compute_physique_dashboard

    uid = get_test_user_id()
    for d in [14, 7, 1]:
        _add_session_with_sets(client, uid, "Curl incliné haltères",
                               [(15, 12), (15, 12)], days_ago=d)
        _add_session_with_sets(client, uid, "Triceps pushdown",
                               [(30, 12), (30, 12)], days_ago=d)

    with SessionLocal() as db:
        dash = compute_physique_dashboard(db, uid)

    arms = next(a for a in dash.radar_axes if a.axis == "arms")
    assert arms.score > 0


from app.services.muscle_scoring import RadarAxis
from app.services.radar import build_radar_svg


def test_radar_svg_renders():
    axes = [
        RadarAxis(axis="pecs", label="Pectoraux", score=80, confidence="élevée"),
        RadarAxis(axis="shoulders", label="Épaules", score=60, confidence="moyenne"),
        RadarAxis(axis="back_width", label="Dos largeur", score=70, confidence="élevée"),
        RadarAxis(axis="back_thickness", label="Dos épaisseur", score=50, confidence="faible"),
        RadarAxis(axis="arms", label="Bras", score=65, confidence="moyenne"),
        RadarAxis(axis="lower", label="Bas du corps", score=55, confidence="faible"),
    ]
    svg = build_radar_svg(axes)
    assert "<svg" in svg
    assert "polygon" in svg
    assert "Pectoraux" in svg
    assert "viewBox" in svg


def test_radar_svg_zero_scores():
    axes = [
        RadarAxis(axis=f"a{i}", label=f"L{i}", score=0, confidence="faible")
        for i in range(6)
    ]
    svg = build_radar_svg(axes)
    assert "<svg" in svg


# --- Integration tests for /physique page ---


def test_physique_page_redirects_to_progression(client):
    """`TRAIN1-C` — la surface est retirée ; le SERVICE reste testé par tout ce
    fichier, et par ses consommateurs `LEGACY_SCORE_CONSUMER`.

    C'est la distinction que cette tranche fait : `compute_physique_dashboard`
    n'est pas supprimé — le classement public en consomme le radar —, mais il
    n'a plus de surface exposée par défaut à un utilisateur connecté.
    """
    r = client.get("/physique", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/progress"


def test_physique_window_param_is_still_accepted(client):
    """Les signets externes portent `?window=60`. La redirection les accueille
    sans 422 — le paramètre est ignoré, pas refusé."""
    r = client.get("/physique?window=60", follow_redirects=False)
    assert r.status_code == 303


def test_physique_page_requires_auth(client):
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    r = client.get("/physique", follow_redirects=False)
    assert r.status_code == 303
