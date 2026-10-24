"""`D9` — mission, démarrage, série confirmée, fin et abandon, par l'API mobile.

Les gardes passent par les routes réelles. Celles qui comparent au web le font
contre la route web ELLE-MÊME, jamais contre une copie de sa logique.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from tests.helpers import get_test_user_id

API = "/api/mobile/v1"

#: Riche mais sans Smith : `push-a` y est SERVABLE avec deux adaptations réelles
#: (même mesure que `test_train_a_environment_experience`).
_SANS_SMITH = [
    "adjustable_bench", "dumbbells", "barbell_and_plates", "ez_bar",
    "dual_adjustable_pulley", "cable_rope", "cable_straight_bar",
    "lat_pulldown_station", "low_row_station", "pull_up_bar", "ab_wheel",
    "butterfly_machine", "chest_press_machine", "chest_supported_row",
    "hack_squat_machine", "leg_extension", "leg_press", "lying_leg_curl",
    "pullover_machine", "rear_delt_fly_machine", "seated_calf_raise",
    "seated_leg_curl", "shoulder_press_machine", "standing_calf_raise",
]


def _token(user_id: int | None = None) -> dict:
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.device_auth import open_device_session

    with SessionLocal() as db:
        issued = open_device_session(db, db.get(User, user_id or get_test_user_id()))
        db.commit()
    return {"Authorization": f"Bearer {issued.access_token}"}


def _other_user() -> int:
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        u = User(username="autrui", password_hash="!unusable")  # noqa: S106
        db.add(u)
        db.commit()
        return u.id


def _start(client, h, slug="push-a", **extra):
    client.cookies.clear()
    return client.post(f"{API}/sessions", headers=h, json={"template_slug": slug, **extra})


def _sessions():
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    with SessionLocal() as db:
        return [(s.id, s.status, s.excluded_from_stats, s.ended_at)
                for s in db.query(WorkoutSession).order_by(WorkoutSession.id)]


def _set_rows(sid):
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog

    with SessionLocal() as db:
        rows = (db.query(SetLog).join(SessionExercise)
                .filter(SessionExercise.session_id == sid).all())
        return {r.id: (r.kind, r.completed, r.weight_kg, r.reps, r.completed_at) for r in rows}


def _put(client, h, sid, set_id, *, op="op-00000001", weight=40.0, reps=10, at=None,
         estimated=False):
    at = at or datetime.now(UTC)
    return client.put(f"{API}/sessions/{sid}/sets/{set_id}", headers=h, json={
        "op_id": op, "weight_kg": weight, "reps": reps,
        "performed_at": at.isoformat(), "performed_at_estimated": estimated})


def _aware(dt):
    return dt.replace(tzinfo=UTC) if dt.tzinfo is None else dt


# ───────── MISSION ─────────


def test_mission_is_the_served_recommendation(client):
    h = _token()
    client.cookies.clear()
    r = client.get(f"{API}/mission", headers=h)
    assert r.status_code == 200
    m = r.json()
    assert m["state"] == "READY"
    assert m["primary_action"] == ("START" if m["executable"] else None)
    assert m["template"]["slug"] == m["decision"]["top"]
    assert m["decision"]["policy"] == "v3"
    assert m["reason"]["phrase"]
    assert m["duration_estimate"] is None


def test_mission_matches_what_the_web_recommends(client):
    """Même moteur, même utilisateur, même instant : même conseil."""
    from app.database import SessionLocal
    from app.services import advice_memory

    with SessionLocal() as db:
        reco = advice_memory.recommander(db, get_test_user_id(),
                                         politique=advice_memory.POLITIQUE_SERVIE,
                                         avec_memoire=advice_memory.MEMOIRE_SERVIE)
    h = _token()
    client.cookies.clear()
    m = client.get(f"{API}/mission", headers=h).json()
    assert m["template"]["slug"] == reco["top"]["template"].slug
    assert m["decision"]["fingerprint"] == reco["context"]["empreinte_contexte"]


def test_an_open_session_turns_the_mission_into_resume(client):
    h = _token()
    sid = _start(client, h).json()["session_id"]
    m = client.get(f"{API}/mission", headers=h).json()
    assert m["state"] == "RESUME"
    assert m["primary_action"] == "RESUME"
    assert m["session"]["id"] == sid
    assert m["position"]["sets_done"] == 0


# ───────── DÉMARRAGE ─────────


def test_start_creates_exactly_one_session(client):
    h = _token()
    avant = len(_sessions())
    r = _start(client, h)
    assert r.status_code == 201
    plan = r.json()
    assert len(_sessions()) == avant + 1
    assert plan["status"] == "in_progress"
    assert plan["sets"], "un plan exécutable porte des séries"
    assert plan["cursor_set_id"] == plan["sets"][0]["set_id"]
    assert set(plan["on_complete"]) == {str(s["set_id"]) for s in plan["sets"]}
    assert plan["on_complete"][str(plan["sets"][-1]["set_id"])] == {"kind": "BILAN"}


def test_a_second_start_is_refused_while_one_is_open(client):
    h = _token()
    first = _start(client, h).json()["session_id"]
    r = _start(client, h, "pull-a")
    assert r.status_code == 409
    assert r.json()["detail"] == {"error": "session_open", "session_id": first}
    assert len(_sessions()) == 1


def test_an_unknown_template_is_a_404(client):
    r = _start(client, _token(), "nope")
    assert r.status_code == 404
    assert _sessions() == []


def test_start_materializes_train_a_adaptations_like_the_web(client):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from app.services.training_preferences import save_available_equipment_items

    uid = get_test_user_id()
    with SessionLocal() as db:
        save_available_equipment_items(db, uid, _SANS_SMITH)
    jar = dict(client.cookies)
    web = client.post("/sessions", data={"template_slug": "push-a"}, follow_redirects=False)
    web_sid = int(web.headers["location"].rsplit("/", 1)[1])
    client.post(f"/sessions/{web_sid}", data={"action": "end"}, follow_redirects=False)
    mob_sid = _start(client, _token()).json()["session_id"]
    client.cookies.update(jar)

    def lignes(sid):
        with SessionLocal() as db:
            s = db.get(WorkoutSession, sid)
            return [(se.position, se.exercise_name_snapshot, se.substituted_name)
                    for se in sorted(s.session_exercises, key=lambda x: x.position)]

    assert lignes(mob_sid) == lignes(web_sid)
    assert sum(1 for *_, exe in lignes(mob_sid) if exe) >= 2, "prémisse : deux adaptations"


def test_a_partial_materialization_commits_nothing(client, monkeypatch):
    """PARTIEL = ÉCHEC, par LA fonction du web : la remplacer couvre les deux routes."""
    import app.routers.sessions as web_sessions
    from app.database import SessionLocal
    from app.services.training_preferences import save_available_equipment_items

    with SessionLocal() as db:
        save_available_equipment_items(db, get_test_user_id(), _SANS_SMITH)
    vrai = web_sessions._poser_adaptations
    monkeypatch.setattr(web_sessions, "_poser_adaptations",
                        lambda session, plan: vrai(session, plan[:-1]))
    r = _start(client, _token())
    assert r.status_code == 409
    assert r.json()["detail"] == {"error": "start_blocked", "reason": "equipment"}
    assert _sessions() == []


def test_a_refused_template_creates_no_session(client):
    from app.database import SessionLocal
    from app.services.training_preferences import save_available_equipment_items

    with SessionLocal() as db:
        save_available_equipment_items(db, get_test_user_id(), ["ab_wheel"])
    r = _start(client, _token(), "legs-a")
    assert r.status_code == 409
    assert r.json()["detail"]["error"] == "start_blocked"
    assert _sessions() == []


def test_start_records_the_advice_episode_like_the_web(client):
    from app.database import SessionLocal
    from app.models.recommendation_episode import RecommendationEpisode

    h = _token()
    client.cookies.clear()
    m = client.get(f"{API}/mission", headers=h).json()
    d = m["decision"]
    sid = _start(client, h, m["template"]["slug"], creation_source="reco_top",
                 decision=d).json()["session_id"]
    with SessionLocal() as db:
        ep = db.query(RecommendationEpisode).one()
        assert (ep.outcome, ep.session_id, ep.proposed_top_slug) == (
            "ACCEPTED_TOP", sid, d["top"])
    assert _sessions()[0][0] == sid


# ───────── SÉRIE CONFIRMÉE ─────────


def _first_set(client, h):
    plan = _start(client, h).json()
    return plan["session_id"], plan["sets"]


def test_a_set_command_completes_exactly_that_set(client):
    h = _token()
    sid, sets = _first_set(client, h)
    target = sets[0]["set_id"]
    at = datetime.now(UTC)
    r = _put(client, h, sid, target, weight=42.5, reps=9, at=at)
    assert r.status_code == 200
    assert r.json()["state"] == "ACKNOWLEDGED"
    assert r.json()["applied"] is True
    rows = _set_rows(sid)
    kind, done, w, reps, completed_at = rows[target]
    assert (kind, done, w, reps) == ("work", True, 42.5, 9)
    assert abs((_aware(completed_at) - at).total_seconds()) < 1, "performed_at, pas l'heure serveur"
    assert [k for k, v in rows.items() if v[1]] == [target], "aucune autre série touchée"


def test_the_same_op_id_never_duplicates_a_set(client):
    h = _token()
    sid, sets = _first_set(client, h)
    target = sets[0]["set_id"]
    first = _put(client, h, sid, target, op="op-replay-01")
    before = _set_rows(sid)
    again = _put(client, h, sid, target, op="op-replay-01",
                 at=datetime.now(UTC) + timedelta(seconds=30))
    assert again.status_code == 200
    assert again.json()["applied"] is False
    assert _set_rows(sid) == before, "un rejeu ne réécrit rien, pas même la date"
    assert first.json()["performed_at"] == again.json()["performed_at"]


def test_a_correction_keeps_the_original_time(client):
    h = _token()
    sid, sets = _first_set(client, h)
    target = sets[0]["set_id"]
    _put(client, h, sid, target, op="op-first-001", reps=8)
    t0 = _set_rows(sid)[target][4]
    _put(client, h, sid, target, op="op-fix-0001", reps=10)
    assert _set_rows(sid)[target][3] == 10
    assert _set_rows(sid)[target][4] == t0


def test_a_set_command_never_touches_note_sensation_or_substitution(client):
    from app.database import SessionLocal
    from app.models.session import SessionExercise

    h = _token()
    sid, sets = _first_set(client, h)
    se_id = sets[0]["se_id"]
    with SessionLocal() as db:
        se = db.get(SessionExercise, se_id)
        se.free_note, se.muscle_sensation, se.substituted_name = "note", "good", "Autre"
        db.commit()
    _put(client, h, sid, sets[0]["set_id"])
    with SessionLocal() as db:
        se = db.get(SessionExercise, se_id)
        assert (se.free_note, se.muscle_sensation, se.substituted_name) == (
            "note", "good", "Autre")
        assert se.success_score is not None, "le score dérivé suit la série"


def test_a_set_command_on_someone_elses_session_is_a_404(client):
    h = _token()
    sid, sets = _first_set(client, h)
    other = _token(_other_user())
    r = _put(client, other, sid, sets[0]["set_id"])
    assert r.status_code == 404
    assert not any(v[1] for v in _set_rows(sid).values())
    assert client.get(f"{API}/sessions/{sid}/execution", headers=other).status_code == 404
    assert client.post(f"{API}/sessions/{sid}/finish", headers=other,
                       json={}).status_code == 404
    assert client.post(f"{API}/sessions/{sid}/abandon", headers=other,
                       json={}).status_code == 404
    assert _sessions()[0][1] == "in_progress"


def test_a_set_of_another_session_is_a_404(client):
    h = _token()
    sid, sets = _first_set(client, h)
    client.post(f"{API}/sessions/{sid}/finish", headers=h, json={})
    sid2, _ = _first_set(client, h)
    assert _put(client, h, sid2, sets[0]["set_id"]).status_code == 404


@pytest.mark.parametrize("weight,reps", [(-1, 8), (40, 0), (40, 101), (2000, 8)])
def test_an_implausible_set_is_refused(client, weight, reps):
    h = _token()
    sid, sets = _first_set(client, h)
    assert _put(client, h, sid, sets[0]["set_id"], weight=weight, reps=reps).status_code == 422


def test_a_closed_session_refuses_new_sets(client):
    h = _token()
    sid, sets = _first_set(client, h)
    client.post(f"{API}/sessions/{sid}/finish", headers=h, json={})
    r = _put(client, h, sid, sets[0]["set_id"])
    assert r.status_code == 409
    assert r.json()["detail"] == {"error": "session_closed"}


# ───────── REMPLACEMENT ─────────


def _sub(client, h, sid, se_id, name, op="op-sub-0001"):
    return client.post(f"{API}/sessions/{sid}/exercises/{se_id}/substitute", headers=h,
                       json={"op_id": op, "name": name})


def _with_substitutes(plan):
    return next(e for e in plan["exercises"] if e["substitutes"])


def test_a_proposed_substitute_is_applied_and_only_that(client):
    from app.database import SessionLocal
    from app.models.session import SessionExercise

    h = _token()
    plan = _start(client, h).json()
    ex = _with_substitutes(plan)
    r = _sub(client, h, plan["session_id"], ex["se_id"], ex["substitutes"][0])
    assert r.status_code == 200
    assert r.json()["executed_name"] == ex["substitutes"][0]
    with SessionLocal() as db:
        se = db.get(SessionExercise, ex["se_id"])
        assert se.substituted_name == ex["substitutes"][0]
        assert se.exercise_name_snapshot == ex["prescribed_name"], "l'identité prévue reste"
    again = _sub(client, h, plan["session_id"], ex["se_id"], ex["substitutes"][0])
    assert again.json()["applied"] is False


def test_a_substitute_the_server_never_proposed_is_refused(client):
    h = _token()
    plan = _start(client, h).json()
    ex = plan["exercises"][0]
    assert _sub(client, h, plan["session_id"], ex["se_id"], "Inventé").status_code == 422


def test_no_substitution_once_a_work_set_is_done(client):
    h = _token()
    plan = _start(client, h).json()
    ex = _with_substitutes(plan)
    first = next(s for s in plan["sets"] if s["se_id"] == ex["se_id"])
    _put(client, h, plan["session_id"], first["set_id"])
    r = _sub(client, h, plan["session_id"], ex["se_id"], ex["substitutes"][0])
    assert r.status_code == 409
    assert r.json()["detail"] == {"error": "substitution_locked"}


# ───────── D11 — le temps ─────────


def test_an_anchored_time_in_the_future_is_refused(client):
    h = _token()
    sid, sets = _first_set(client, h)
    r = _put(client, h, sid, sets[0]["set_id"], at=datetime.now(UTC) + timedelta(minutes=10))
    assert r.status_code == 422
    assert r.json()["detail"] == {"error": "performed_at_out_of_bounds"}


def test_an_anchored_time_before_the_start_is_refused(client):
    h = _token()
    sid, sets = _first_set(client, h)
    r = _put(client, h, sid, sets[0]["set_id"], at=datetime.now(UTC) - timedelta(hours=2))
    assert r.status_code == 422


def test_the_tolerance_admits_a_small_clock_skew(client):
    h = _token()
    sid, sets = _first_set(client, h)
    r = _put(client, h, sid, sets[0]["set_id"], at=datetime.now(UTC) + timedelta(seconds=60))
    assert r.status_code == 200


def test_an_estimated_time_is_clamped_not_lost(client):
    h = _token()
    sid, sets = _first_set(client, h)
    r = _put(client, h, sid, sets[0]["set_id"], estimated=True,
             at=datetime.now(UTC) + timedelta(days=3))
    assert r.status_code == 200
    assert r.json()["performed_at_adjusted"] is True
    stored = _aware(_set_rows(sid)[sets[0]["set_id"]][4])
    assert stored <= datetime.now(UTC)


def test_sets_of_an_exercise_cannot_go_back_in_time(client):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    h = _token()
    sid, sets = _first_set(client, h)
    with SessionLocal() as db:  # la séance a commencé il y a dix minutes
        s = db.get(WorkoutSession, sid)
        s.started_at = _aware(s.started_at) - timedelta(minutes=10)
        db.commit()
    a, b = sets[0], sets[1]
    assert a["se_id"] == b["se_id"], "prémisse : deux séries du même exercice"
    now = datetime.now(UTC)
    _put(client, h, sid, a["set_id"], op="op-order-01", at=now - timedelta(minutes=1))
    # Après le début, mais AVANT la série précédente : seul l'ordre la refuse.
    r = _put(client, h, sid, b["set_id"], op="op-order-02", at=now - timedelta(minutes=5))
    assert r.status_code == 422
    ok = _put(client, h, sid, b["set_id"], op="op-order-03", at=now)
    assert ok.status_code == 200


# ───────── LECTURE D'EXÉCUTION ─────────


def test_execution_restores_done_sets_and_the_cursor(client):
    h = _token()
    sid, sets = _first_set(client, h)
    _put(client, h, sid, sets[0]["set_id"], weight=30, reps=12)
    plan = client.get(f"{API}/sessions/{sid}/execution", headers=h).json()
    assert plan["done"][str(sets[0]["set_id"])]["reps"] == 12
    assert plan["cursor_set_id"] == sets[1]["set_id"]
    assert plan["allowed_actions"] == ["COMPLETE_SET", "FINISH", "PAUSE", "ABANDON"]


# ───────── R16 — TERMINER / PAUSE / ABANDONNER ─────────


def test_finish_keeps_what_was_done_and_fabricates_nothing(client):
    h = _token()
    sid, sets = _first_set(client, h)
    _put(client, h, sid, sets[0]["set_id"])
    before = _set_rows(sid)
    r = client.post(f"{API}/sessions/{sid}/finish", headers=h, json={})
    assert r.status_code == 200
    body = r.json()
    assert (body["status"], body["excluded_from_stats"], body["applied"]) == (
        "completed", False, True)
    assert body["work_sets_done"] == 1
    assert body["work_sets_total"] == len(sets)
    assert _set_rows(sid) == before, "aucune série complétée, ni effacée"
    assert _sessions()[0][1:3] == ("completed", False)


def test_finish_is_idempotent(client):
    h = _token()
    sid, _ = _first_set(client, h)
    first = client.post(f"{API}/sessions/{sid}/finish", headers=h, json={}).json()
    again = client.post(f"{API}/sessions/{sid}/finish", headers=h, json={}).json()
    assert again["applied"] is False
    assert again["ended_at"] == first["ended_at"]


def test_an_offline_finish_is_dated_when_decided_within_bounds(client):
    h = _token()
    sid, sets = _first_set(client, h)
    _put(client, h, sid, sets[0]["set_id"])
    decided = datetime.now(UTC) - timedelta(seconds=1)
    r = client.post(f"{API}/sessions/{sid}/finish", headers=h,
                    json={"at": (decided - timedelta(days=1)).isoformat()})
    ended = datetime.fromisoformat(r.json()["ended_at"])
    done_at = _aware(_set_rows(sid)[sets[0]["set_id"]][4])
    assert ended >= done_at, "une séance ne finit pas avant sa dernière série"


def test_pause_keeps_the_session_resumable(client):
    """PAUSE n'écrit rien : la séance reste ouverte, la mission rend RESUME."""
    h = _token()
    sid, sets = _first_set(client, h)
    _put(client, h, sid, sets[0]["set_id"])
    m = client.get(f"{API}/mission", headers=h).json()
    assert (m["state"], m["session"]["id"], m["position"]["sets_done"]) == ("RESUME", sid, 1)


def test_abandon_closes_and_excludes_but_never_erases(client):
    h = _token()
    sid, sets = _first_set(client, h)
    _put(client, h, sid, sets[0]["set_id"])
    before = _set_rows(sid)
    r = client.post(f"{API}/sessions/{sid}/abandon", headers=h, json={})
    assert r.status_code == 200
    assert (r.json()["status"], r.json()["excluded_from_stats"]) == ("completed", True)
    assert _set_rows(sid) == before, "les faits restent en base"
    assert _sessions()[0][1:3] == ("completed", True)
    assert client.get(f"{API}/mission", headers=h).json()["state"] != "RESUME"


def test_abandon_and_finish_do_not_overwrite_each_other(client):
    h = _token()
    sid, _ = _first_set(client, h)
    client.post(f"{API}/sessions/{sid}/abandon", headers=h, json={})
    r = client.post(f"{API}/sessions/{sid}/finish", headers=h, json={})
    assert r.status_code == 409
    assert r.json()["detail"] == {"error": "session_abandoned"}
    sid2, _ = _first_set(client, h)
    client.post(f"{API}/sessions/{sid2}/finish", headers=h, json={})
    r = client.post(f"{API}/sessions/{sid2}/abandon", headers=h, json={})
    assert r.json()["detail"] == {"error": "session_finished"}


def test_an_abandoned_session_is_shown_as_excluded_in_web_history(client):
    h = _token()
    jar = dict(client.cookies)
    sid, _ = _first_set(client, h)
    client.post(f"{API}/sessions/{sid}/abandon", headers=h, json={})
    client.cookies.update(jar)
    page = client.get("/history")
    assert page.status_code == 200
    assert "exclu des KPI" in page.text


# ───────── non-régression web ─────────


def test_a_mobile_session_is_a_normal_web_session(client):
    h = _token()
    jar = dict(client.cookies)
    sid, sets = _first_set(client, h)
    for i, st in enumerate(sets[:3]):
        r = _put(client, h, sid, st["set_id"], op=f"op-web-{i:04d}")
        assert r.status_code == 200
    client.post(f"{API}/sessions/{sid}/finish", headers=h, json={})
    client.cookies.update(jar)
    assert client.get(f"/sessions/{sid}").status_code == 200
    assert client.get(f"/sessions/{sid}/done").status_code == 200
    assert client.get("/history").status_code == 200
    assert sum(1 for v in _set_rows(sid).values() if v[1]) == 3


def test_no_mobile_route_renders_html(client):
    from app.main import app

    mobiles = [r for r in app.routes if getattr(r, "path", "").startswith(API)]
    assert mobiles, "prémisse : l'API est montée"
    for r in mobiles:
        assert "HTMLResponse" not in repr(getattr(r, "response_class", ""))
