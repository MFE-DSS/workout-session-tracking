"""Sprint 5 mobile polish tests:

- Exercise jump bar
- Exercise card "done" state
- After-save next-exercise anchor redirect
- Active session banner
- Filter-aware empty state on /history
- Warmup / work sub-headers
"""
from __future__ import annotations

import re


def _start(client, slug: str = "push-a") -> int:
    r = client.post("/sessions", data={"template_slug": slug}, follow_redirects=False)
    return int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


def _e2_ids(sid: int) -> tuple[int, list[int]]:
    """Return (session_exercise_id, [work set ids]) for E2 of a session."""
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog

    with SessionLocal() as db:
        se = db.execute(
            select(SessionExercise)
            .where(SessionExercise.session_id == sid)
            .where(SessionExercise.exercise_code_snapshot == "E2")
        ).scalar_one()
        work_ids = sorted(
            s.id for s in db.execute(
                select(SetLog).where(SetLog.session_exercise_id == se.id)
            ).scalars().all()
            if s.kind == "work"
        )
        return se.id, work_ids


# ---------------------------------------------------------------------------
# Exercise jump bar
# ---------------------------------------------------------------------------


def test_jump_bar_renders_one_item_per_exercise(client):
    sid = _start(client, "push-a")
    body = client.get(f"/sessions/{sid}").text
    # Push A has 7 exercises (v10) -> 7 jump items + 1 feedback shortcut
    # Sb_29.1 — la nav porte désormais plusieurs classes additionnelles
    # (session-focus__jump, session-focus__sticky-jump). On vérifie la
    # présence de la classe sans contraindre l'ordre exact.
    assert "ex-jump" in body
    for code in ["E1", "E2", "E3", "E4", "E5", "E6", "E7"]:
        assert f'>{code}</span>' in body
    # FB shortcut to #session-feedback
    assert "#session-feedback" in body
    assert "FB" in body
    # Default progress 0/2 ... 0/3 etc.
    assert ">0/2<" in body or ">0/3<" in body


def test_jump_bar_marks_completed_exercise_as_done(client):
    sid = _start(client, "push-a")
    se_id, work_ids = _e2_ids(sid)
    # Fill ALL work sets of E2
    data = {"muscle_sensation": "strong"}
    for i, wid in enumerate(work_ids, start=1):
        data[f"set_{wid}_weight_kg"] = str(60 + i)
        data[f"set_{wid}_reps"] = "10"
        data[f"set_{wid}_completed"] = "1"
    client.post(f"/sessions/{sid}/exercises/{se_id}", data=data, follow_redirects=False)

    body = client.get(f"/sessions/{sid}").text
    # E2 jump item must carry the --done modifier and 3/3
    assert re.search(
        r'class="[^"]*ex-jump__item--done[^"]*"[^>]*href="#exercise-' + str(se_id) + r'"',
        body,
    ) or re.search(
        r'href="#exercise-' + str(se_id) + r'"[^>]*class="[^"]*ex-jump__item--done',
        body,
    )
    # And the in-card progress should be 3/3 too (look for the ex-jump__prog spelling)
    assert ">3/3<" in body


# ---------------------------------------------------------------------------
# Exercise card done state
# ---------------------------------------------------------------------------


def test_exercise_card_gets_done_class_when_all_work_sets_completed(client):
    sid = _start(client, "push-a")
    se_id, work_ids = _e2_ids(sid)
    data = {"muscle_sensation": "strong"}
    for i, wid in enumerate(work_ids, start=1):
        data[f"set_{wid}_weight_kg"] = str(60 + i)
        data[f"set_{wid}_reps"] = "10"
        data[f"set_{wid}_completed"] = "1"
    client.post(f"/sessions/{sid}/exercises/{se_id}", data=data, follow_redirects=False)

    body = client.get(f"/sessions/{sid}").text
    # The form for E2 must carry the exercise-card--done modifier
    pattern = (
        r'class="[^"]*exercise-card--done[^"]*"[^>]*id="exercise-'
        + str(se_id)
        + r'"'
    )
    assert re.search(pattern, body)


def test_exercise_card_done_class_absent_when_partial(client):
    sid = _start(client, "push-a")
    se_id, work_ids = _e2_ids(sid)
    # Mark only ONE work set as completed
    wid = work_ids[0]
    client.post(
        f"/sessions/{sid}/exercises/{se_id}",
        data={
            f"set_{wid}_weight_kg": "60",
            f"set_{wid}_reps": "10",
            f"set_{wid}_completed": "1",
        },
        follow_redirects=False,
    )
    body = client.get(f"/sessions/{sid}").text
    pattern = (
        r'class="[^"]*exercise-card--done[^"]*"[^>]*id="exercise-'
        + str(se_id)
        + r'"'
    )
    assert not re.search(pattern, body)


# ---------------------------------------------------------------------------
# Next-exercise anchor redirect
# ---------------------------------------------------------------------------


def test_save_exercise_card_redirects_to_next_exercise(client):
    sid = _start(client, "push-a")
    se_id, _ = _e2_ids(sid)  # E2 -> next is E3
    r = client.post(
        f"/sessions/{sid}/exercises/{se_id}",
        data={},
        follow_redirects=False,
    )
    assert r.status_code == 303
    location = r.headers["location"]
    # The next exercise (E3) anchor must be different from se_id
    assert f"#exercise-{se_id}" not in location
    assert "/sessions/" in location and "#exercise-" in location


def test_save_last_exercise_card_redirects_to_session_feedback(client):
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import SessionExercise

    sid = _start(client, "push-a")
    with SessionLocal() as db:
        # E8 is the last exercise of Push A
        last_se = db.execute(
            select(SessionExercise)
            .where(SessionExercise.session_id == sid)
            .order_by(SessionExercise.position.desc())
            .limit(1)
        ).scalar_one()
        last_id = last_se.id

    r = client.post(
        f"/sessions/{sid}/exercises/{last_id}",
        data={},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert "#session-feedback" in r.headers["location"]


# ---------------------------------------------------------------------------
# Active session banner
# ---------------------------------------------------------------------------


# Sb_UI_03.3 — the global .active-banner is REMOVED. The active-session state
# is now carried by the "Séance" tab of the bottom nav / rail
# (has-active-session + a discreet dot + sr-only "En cours"); the Home hero
# stays the single direct "Reprendre" surface. These tests are re-oriented from
# "banner present/absent" to "no banner anywhere + nav indicator present when a
# session is open", the new truth — not weakened.
def test_active_session_indicator_on_library_when_session_open(client):
    _start(client, "push-a")
    body = client.get("/library").text
    assert "active-banner" not in body  # global banner gone
    assert "has-active-session" in body  # Séance tab flagged
    assert "En cours" in body  # accessible indicator text


def test_no_active_banner_on_secondary_pages(client):
    _start(client, "push-a")
    for url in ["/history", "/progress", "/rules", "/exercise-history/push-a/E2"]:
        body = client.get(url).text
        assert "active-banner" not in body, f"banner must be gone on {url}"
        assert "has-active-session" in body, f"nav indicator missing on {url}"


def test_no_active_indicator_when_no_session_open(client):
    body = client.get("/library").text
    assert "active-banner" not in body
    assert "has-active-session" not in body
    assert "En cours" not in body


def test_no_active_banner_on_session_detail_page(client):
    sid = _start(client, "push-a")
    body = client.get(f"/sessions/{sid}").text
    assert "active-banner" not in body
    # /sessions/{id} keeps the Séance tab active (is_sess covers /sessions).
    # Note: the session_detail view does not pass `active_session` to the
    # template (unchanged — routers are out of scope for Sb_UI_03.3), so the
    # has-active-session indicator is not rendered here; this mirrors the old
    # banner which was also hidden on this page. The Séance tab is still active.
    nav = re.search(r'<nav class="app-bottom-nav".*?</nav>', body, re.DOTALL).group(0)
    active = [re.search(r'__label">([^<]+)<', it).group(1)
              for it in re.findall(r'<a class="app-bottom-nav__item[^>]*>.*?</a>', nav, re.DOTALL)
              if 'aria-current="page"' in it]
    assert active == ["Séance"]


def test_no_active_banner_on_home(client):
    """Home already has the Reprendre hero — no global banner."""
    _start(client, "push-a")
    body = client.get("/").text
    assert "active-banner" not in body


# ---------------------------------------------------------------------------
# History filter-aware empty state
# ---------------------------------------------------------------------------


def test_history_empty_state_specific_to_in_progress_filter(client):
    body = client.get("/history?status=in_progress").text
    assert "Aucune séance en cours" in body


def test_history_empty_state_specific_to_completed_filter(client):
    body = client.get("/history?status=completed").text
    assert "Aucune séance terminée" in body


# ---------------------------------------------------------------------------
# Warmup / work sub-headers
# ---------------------------------------------------------------------------


def test_session_detail_has_warmup_and_work_subheaders(client):
    sid = _start(client, "push-a")
    body = client.get(f"/sessions/{sid}").text
    # Both group titles must show up at least once per card
    assert "set-group-title" in body
    # Warmup subheading appears for every exercise (7 cards in v10)
    assert body.count(">Échauffement</h4>") >= 7
    # "Travail" heading now includes a C05 hint span; count the heading text
    assert body.count("Travail\n") >= 7 or body.count("Travail ") >= 7 or body.count(">Travail<") >= 7
