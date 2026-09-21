"""Sprint 8: session management, quality score, timelines."""
from __future__ import annotations

import re
from datetime import UTC, datetime

from tests.helpers import get_test_user_id


def _start(client, slug: str = "push-a") -> int:
    r = client.post("/sessions", data={"template_slug": slug}, follow_redirects=False)
    return int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


def _complete(client, sid: int) -> None:
    client.post(f"/sessions/{sid}", data={
        "concentration": "high", "global_state": "good",
        "bodyweight_kg": "78.5", "action": "end",
    }, follow_redirects=False)


def _fill_e2_and_complete(client, sid: int) -> None:
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog

    with SessionLocal() as db:
        se = db.execute(
            select(SessionExercise)
            .where(SessionExercise.session_id == sid)
            .where(SessionExercise.exercise_code_snapshot == "E2")
        ).scalar_one()
        se_id = se.id
        work_ids = sorted(
            s.id for s in db.execute(
                select(SetLog).where(SetLog.session_exercise_id == se_id)
            ).scalars().all()
            if s.kind == "work"
        )

    data = {"muscle_sensation": "strong"}
    for i, wid in enumerate(work_ids, start=1):
        data[f"set_{wid}_weight_kg"] = str(60 + i)
        data[f"set_{wid}_reps"] = "10"
        data[f"set_{wid}_completed"] = "1"
    client.post(f"/sessions/{sid}/exercises/{se_id}", data=data, follow_redirects=False)
    _complete(client, sid)


# ---------------------------------------------------------------------------
# Quality score (pure function)
# ---------------------------------------------------------------------------


def test_quality_score_perfect_session(client):
    """All work done, all scored 100, high concentration, good state → 100."""
    from app.models.session import SessionExercise, SetLog, WorkoutSession
    from app.services.quality_score import compute_session_quality

    s = WorkoutSession(
        template_slug_snapshot="x", template_name_snapshot="X", user_id=get_test_user_id(),
        started_at=datetime.now(UTC), status="completed",
        concentration="high", global_state="good",
    )
    se = SessionExercise(
        exercise_code_snapshot="E1", exercise_name_snapshot="Ex", position=1,
        success_score=100,
    )
    se.set_logs = [
        SetLog(kind="work", set_index=1, completed=True),
        SetLog(kind="work", set_index=2, completed=True),
        SetLog(kind="warmup", set_index=1, completed=True),
    ]
    s.session_exercises = [se]
    assert compute_session_quality(s) == 100


def test_quality_score_zero_when_nothing_filled(client):
    from app.models.session import WorkoutSession
    from app.services.quality_score import compute_session_quality

    s = WorkoutSession(
        template_slug_snapshot="x", template_name_snapshot="X", user_id=get_test_user_id(),
        started_at=datetime.now(UTC), status="completed",
    )
    s.session_exercises = []
    assert compute_session_quality(s) == 0


def test_quality_score_partial(client):
    """1/2 work done (20pts), score 80 (32pts), medium (6), flat (6) → 64."""
    from app.models.session import SessionExercise, SetLog, WorkoutSession
    from app.services.quality_score import compute_session_quality

    s = WorkoutSession(
        template_slug_snapshot="x", template_name_snapshot="X", user_id=get_test_user_id(),
        started_at=datetime.now(UTC), status="completed",
        concentration="medium", global_state="flat",
    )
    se = SessionExercise(
        exercise_code_snapshot="E1", exercise_name_snapshot="Ex", position=1,
        success_score=80,
    )
    se.set_logs = [
        SetLog(kind="work", set_index=1, completed=True),
        SetLog(kind="work", set_index=2, completed=False),
    ]
    s.session_exercises = [se]
    assert compute_session_quality(s) == 64


# ---------------------------------------------------------------------------
# Admin page
# ---------------------------------------------------------------------------


def test_admin_sessions_page_renders(client):
    _start(client, "push-a")
    r = client.get("/admin/sessions")
    assert r.status_code == 200
    assert "Gestion des séances" in r.text
    assert "Push A" in r.text


def test_admin_sessions_shows_quality_for_completed(client):
    sid = _start(client, "push-a")
    _complete(client, sid)
    body = client.get("/admin/sessions").text
    assert "qualité" in body.lower()


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------


def test_delete_session_removes_it(client):
    """⚠ LA CONFIRMATION EST DÉSORMAIS APPLIQUÉE PAR LE SERVEUR.

    `SESSION_LIFECYCLE` (`UI-CP5`) remplace un `confirm()` JavaScript — côté
    client seulement, donc contournable par cette requête même — par un champ
    que seule la vue de confirmation produit. Le POST le porte maintenant.
    """
    sid = _start(client, "push-a")
    r = client.post(f"/admin/sessions/{sid}/delete",
                    data={"confirmation": "oui"}, follow_redirects=False)
    assert r.status_code == 303

    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    with SessionLocal() as db:
        assert db.get(WorkoutSession, sid) is None


def test_une_suppression_sans_confirmation_ne_supprime_rien(client):
    """LA PROTECTION EST UNE PROPRIÉTÉ DU SERVEUR, plus une chaîne dans un
    gabarit.

    Avant `UI-CP5`, cette requête exacte supprimait : le `confirm()` vivait
    dans `onsubmit` et ne protégeait que les navigateurs coopératifs.
    """
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    sid = _start(client, "push-a")
    r = client.post(f"/admin/sessions/{sid}/delete", follow_redirects=False)
    assert r.status_code == 303
    assert f"/admin/sessions/{sid}/delete" in r.headers["location"], (
        "l'utilisateur doit atterrir sur la confirmation, pas sur un échec"
    )
    with SessionLocal() as db:
        assert db.get(WorkoutSession, sid) is not None, "supprimée sans confirmation"


def test_la_confirmation_chiffre_ce_qui_disparait(client):
    """Une cascade qu'on n'a pas comptée n'est pas un consentement éclairé."""
    sid = _start(client, "push-a")
    body = client.get(f"/admin/sessions/{sid}/delete").text
    assert "définitive" in body
    # Deux assertions plutôt qu'une conjonction : laquelle des deux grandeurs a
    # disparu du décompte est l'information utile (`python:S9073`).
    assert "exercice" in body
    assert "série" in body
    # L'alternative RÉVERSIBLE est offerte dans le même écran.
    assert "exclure des kpi" in body.lower()
    assert "réversible" in body.lower()


def test_la_destination_de_retour_est_close(client):
    """Une destination hors liste est ignorée, jamais suivie.

    Elle remplace un reniflage de l'en-tête `Referer` — que l'appelant
    contrôle, et que `Referrer-Policy: no-referrer` supprime.
    """
    sid = _start(client, "push-a")
    r = client.post(f"/admin/sessions/{sid}/exclude",
                    data={"next": "//evil.example/"}, follow_redirects=False)
    assert r.headers["location"] == "/admin/sessions"

    r = client.post(f"/admin/sessions/{sid}/exclude",
                    data={"next": "/history"}, follow_redirects=False)
    assert r.headers["location"] == "/history"


def test_delete_unknown_session_returns_404(client):
    r = client.post("/admin/sessions/99999/delete", follow_redirects=False)
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Exclude / include
# ---------------------------------------------------------------------------


def test_exclude_toggle_marks_session(client):
    sid = _start(client, "push-a")
    client.post(f"/admin/sessions/{sid}/exclude", follow_redirects=False)

    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    with SessionLocal() as db:
        assert db.get(WorkoutSession, sid).excluded_from_stats is True

    # Toggle back
    client.post(f"/admin/sessions/{sid}/exclude", follow_redirects=False)
    with SessionLocal() as db:
        assert db.get(WorkoutSession, sid).excluded_from_stats is False


def test_excluded_session_not_in_kpis(client):
    from app.database import SessionLocal
    from app.services.kpis import compute_global_kpis

    sid = _start(client, "push-a")
    _complete(client, sid)

    with SessionLocal() as db:
        k1 = compute_global_kpis(db)
        assert k1.completed_last_30 >= 1

    client.post(f"/admin/sessions/{sid}/exclude", follow_redirects=False)

    with SessionLocal() as db:
        k2 = compute_global_kpis(db)
        assert k2.completed_last_30 == 0


def test_admin_page_shows_excluded_badge(client):
    sid = _start(client, "push-a")
    client.post(f"/admin/sessions/{sid}/exclude", follow_redirects=False)
    body = client.get("/admin/sessions").text
    assert "exclu des KPI" in body
    assert "admin-row--excluded" in body


# ---------------------------------------------------------------------------
# Timelines on /progress
# ---------------------------------------------------------------------------


def test_progress_shows_no_timeline_when_no_data(client):
    body = client.get("/progress").text
    # Sb_UI_03.1 — the shell now ships decorative bottom-nav SVG icons, so a
    # bare "<svg" check no longer isolates the timeline chart. Assert on the
    # timeline chart container specifically (the real intent of this test).
    assert "timeline-chart" not in body


def test_une_seance_terminee_alimente_les_agregats_de_progression(client):
    """⚠ REPOINTÉE PAR `UI-CP5 §9` — la courbe « Qualité des séances » est
    retirée, et la propriété gardée n'était pas elle.

    Son axe Y était `compute_session_quality`, un SCORE COMPOSITE tracé en
    hauteur : « toute dimension graphique doit avoir une variable nommée et
    vraie ». Le score par séance reste lisible sur la surface de cycle de vie,
    et par programme sur `/progress`.

    Ce que cette garde protégeait vraiment : **une séance terminée COMPTE**.
    Elle l'observe désormais sur l'agrégat, qui est le fait, plutôt que sur un
    graphique, qui n'en était qu'un rendu.
    """
    from app.database import SessionLocal
    from app.services.kpis import compute_global_kpis
    from tests.helpers import get_test_user_id

    sid = _start(client, "push-a")
    _fill_e2_and_complete(client, sid)

    with SessionLocal() as db:
        kpis = compute_global_kpis(db, user_id=get_test_user_id())
    assert kpis.completed_last_30 >= 1

    body = client.get("/progress").text
    assert "séance" in body.lower()
    assert "Qualité des séances" not in body, (
        "la courbe au score composite est revenue"
    )


def test_progress_shows_bodyweight_timeline_when_bodyweight_present(client):
    sid = _start(client, "push-a")
    client.post(f"/sessions/{sid}", data={
        "concentration": "high", "global_state": "good",
        "bodyweight_kg": "78.5", "action": "end",
    }, follow_redirects=False)
    body = client.get("/progress").text
    assert "Poids corporel" in body


def test_excluded_sessions_leave_the_aggregates(client):
    """⚠ REPOINTÉE PAR `UI-CP5 §9`, et RENFORCÉE.

    L'ancienne observait la disparition d'un graphique. Elle observe désormais
    la disparition du FAIT — dans les deux sens, et sur l'agrégat lui-même.
    Exclure une séance doit la retirer de ce que la page affirme, pas seulement
    d'un rendu.
    """
    from app.database import SessionLocal
    from app.services.kpis import compute_global_kpis
    from tests.helpers import get_test_user_id

    sid = _start(client, "push-a")
    _fill_e2_and_complete(client, sid)

    with SessionLocal() as db:
        avant = compute_global_kpis(db, user_id=get_test_user_id()).completed_last_30
    assert avant >= 1, "prémisse : la séance doit compter avant d'être exclue"

    client.post(f"/admin/sessions/{sid}/exclude", data={"next": "/history"},
                follow_redirects=False)
    with SessionLocal() as db:
        apres = compute_global_kpis(db, user_id=get_test_user_id()).completed_last_30
    assert apres == avant - 1, "la séance exclue pèse encore"

    # Et la bascule inverse la restitue — une exclusion est réversible.
    client.post(f"/admin/sessions/{sid}/exclude", data={"next": "/history"},
                follow_redirects=False)
    with SessionLocal() as db:
        retour = compute_global_kpis(db, user_id=get_test_user_id()).completed_last_30
    assert retour == avant


def test_deleted_sessions_not_in_timelines(client):
    sid = _start(client, "push-a")
    _fill_e2_and_complete(client, sid)

    client.post(f"/admin/sessions/{sid}/delete", follow_redirects=False)
    body = client.get("/progress").text
    assert "Qualité de séance" not in body


# ---------------------------------------------------------------------------
# SESSION_LIFECYCLE — la capacité est préservée, le fardeau de commande non
# ---------------------------------------------------------------------------


def test_the_lifecycle_capability_is_intact(client):
    """⚠ REPOINTÉE PAR `UI-CP5`, ET C'EST LA MOITIÉ QUI COMPTE LE PLUS.

    Elle s'appelait `test_history_has_management_actions` et exigeait que
    CHAQUE séance de `/history` porte ses commandes dans un `<details>`. C'est
    exactement ce que la tranche retire : `FLIGHT_RECORDER` est un instrument
    de lecture — son contrat dit `ACTION : aucune` — et l'écran portait
    **42 formulaires**, deux par séance.

    Mais retirer la garde aurait laissé la capacité sans gardien, et c'est
    précisément ainsi qu'une capacité disparaît sans que personne le voie. Elle
    est donc **déplacée avec son objet** : les trois affordances sont vérifiées
    là où elles vivent maintenant, sur `/admin/sessions`.

    Une conjonction `a or b` cachait en plus laquelle des deux étiquettes on
    exige (`python:S9073`, MAJOR) — et les deux sont légitimes : l'étiquette
    bascule selon l'état de la séance. On vérifie donc la bascule elle-même.
    """
    client.post("/sessions", data={"template_slug": "push-a"}, follow_redirects=False)
    body = client.get("/admin/sessions").text

    assert "Supprimer" in body, "la suppression n'est plus offerte nulle part"
    # L'étiquette de la bascule dépend de l'état ; on exige la bascule, pas un
    # de ses deux mots.
    bascule = ("Exclure des KPI" in body) + ("Inclure dans KPI" in body)
    assert bascule >= 1, "la bascule d'exclusion des KPI a disparu"


def test_history_exposes_the_path_without_exposing_the_controls(client):
    """LE PENDANT, et sans lui la garde ci-dessus autoriserait un cul-de-sac.

    `« Preserve capability. Remove command burden. »` a deux moitiés. La
    première est tenue au-dessus. La seconde est ici : l'instrument de lecture
    ne porte **aucune** commande, et il mène quand même à celle qui existe.

    Un chemin sans commandes, pas des commandes sans chemin.
    """
    client.post("/sessions", data={"template_slug": "push-a"}, follow_redirects=False)
    principal = client.get("/history").text.split("<main", 1)[-1].split("</main", 1)[0]

    assert 'method="post"' not in principal, (
        "une commande est revenue sur l'instrument de lecture"
    )
    assert "/admin/sessions" in principal, (
        "la capacité n'est plus atteignable depuis l'historique"
    )


# ---------------------------------------------------------------------------
# Alembic migration exists for the new column
# ---------------------------------------------------------------------------


def test_alembic_migration_for_excluded_from_stats():
    from pathlib import Path

    versions = Path(__file__).resolve().parent.parent / "migrations" / "versions"
    files = list(versions.glob("*excluded_from_stats*.py"))
    assert len(files) >= 1, "missing migration for excluded_from_stats"
