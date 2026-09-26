"""Tests for the /sessions/{id}/done terminal-state route."""
from __future__ import annotations

import re
from datetime import UTC, datetime

from tests.helpers import get_test_user_id


def _mk_completed_session(
    *,
    template_slug: str = "push-a",
    template_name: str = "Push A — test",
    started_at: datetime | None = None,
    ended_at: datetime | None = None,
    user_id: int | None = None,
) -> int:
    """Create and commit a completed WorkoutSession; return its id.

    Mirrors the inline factory pattern used in tests/test_session_recap.py
    (repo convention — no shared factories).
    """
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    started = started_at or datetime(2026, 4, 13, 18, 0, tzinfo=UTC)
    ended = ended_at or datetime(2026, 4, 13, 19, 30, tzinfo=UTC)

    with SessionLocal() as db:
        s = WorkoutSession(
            user_id=user_id if user_id is not None else get_test_user_id(),
            template_id=None,
            template_slug_snapshot=template_slug,
            template_name_snapshot=template_name,
            started_at=started,
            ended_at=ended,
            status="completed",
            concentration="high",
            global_state="good",
            bodyweight_kg=79.4,
        )
        se = SessionExercise(
            exercise_code_snapshot="E1",
            exercise_name_snapshot="Incline Smith Press",
            position=1,
            success_score=80,
        )
        for j in range(1, 4):
            se.set_logs.append(
                SetLog(
                    kind="work",
                    set_index=j,
                    weight_kg=60.0,
                    reps=10,
                    completed=(j <= 2),
                )
            )
        s.session_exercises.append(se)
        db.add(s)
        db.commit()
        return s.id


def test_done_route_returns_200_for_completed_session(client):
    sid = _mk_completed_session()
    r = client.get(f"/sessions/{sid}/done")
    assert r.status_code == 200
    assert "Séance terminée" in r.text
    assert "Push A — test" in r.text


def test_done_route_redirects_when_session_in_progress(client):
    from app.database import SessionLocal
    from app.enums import SessionStatus
    from app.models.session import WorkoutSession

    sid = _mk_completed_session()
    with SessionLocal() as db:
        session = db.get(WorkoutSession, sid)
        session.status = SessionStatus.IN_PROGRESS
        session.ended_at = None
        db.commit()

    r = client.get(f"/sessions/{sid}/done", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == f"/sessions/{sid}"


def test_done_route_404_for_other_users_session(client):
    # Bogus session id → _load_session returns None → 404.
    # This exercises the same ownership guard path that would also
    # reject a session belonging to another user.
    r = client.get("/sessions/999999/done")
    assert r.status_code == 404


def test_action_end_redirects_to_done(client):
    from app.database import SessionLocal
    from app.enums import SessionStatus
    from app.models.session import WorkoutSession

    sid = _mk_completed_session()
    # Downgrade to in_progress so action=end transitions it.
    with SessionLocal() as db:
        session = db.get(WorkoutSession, sid)
        session.status = SessionStatus.IN_PROGRESS
        session.ended_at = None
        db.commit()

    r = client.post(
        f"/sessions/{sid}",
        data={"action": "end"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert r.headers["location"] == f"/sessions/{sid}/done"


def test_action_reopen_redirects_to_editable_session(client):
    sid = _mk_completed_session()  # already status=completed
    r = client.post(
        f"/sessions/{sid}",
        data={"action": "reopen"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert r.headers["location"] == f"/sessions/{sid}"


def test_get_session_completed_redirects_to_done(client):
    sid = _mk_completed_session()
    r = client.get(f"/sessions/{sid}", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == f"/sessions/{sid}/done"


def test_get_session_in_progress_renders_normally(client):
    from app.database import SessionLocal
    from app.enums import SessionStatus
    from app.models.session import WorkoutSession

    sid = _mk_completed_session()
    with SessionLocal() as db:
        s = db.get(WorkoutSession, sid)
        s.status = SessionStatus.IN_PROGRESS
        s.ended_at = None
        db.commit()

    # `UI-CP2` — « éditable » se vérifie sur la surface qui porte l'édition.
    # Le formulaire de séance a quitté l'exécution pour la clôture ; la
    # capacité — une séance rouverte reste modifiable — est inchangée.
    r = client.get(f"/sessions/{sid}?view=bilan")
    assert r.status_code == 200
    # Editable = session-feedback form visible on the page
    assert "session-feedback" in r.text


def test_done_page_shows_summary_block(client):
    """⚠ `UI-CP7.5B` — REPOINTÉE FAIT PAR FAIT, PAS RELÂCHÉE.

    Cette garde épinglait la composition de l'ancien empilement. Chaque
    littéral est repris ci-dessous avec ce qu'il est devenu, pour qu'on ne
    puisse pas confondre un déménagement avec un abandon.

        « Work sets »      → « séries ». Le libellé anglais partait de toute
                             façon ; le fait de complétion reste, en tête.
        « 2 / 3 »          → inchangé, c'est LE fait de la page.
        poids de corps     → `BODY_LEDGER` (`CP7.5A`). Il reste collecté sur
                             le bilan de séance, il n'est plus RENDU ici.
        ligne par exercice → descendue dans le tiroir de cycle de vie.
                             Vérifié : aucune autre surface ne la porte.
        `href="/history"`  → la coque persistante. Quatre sorties de page
                             sur cinq partent, celle-là comprise.
        rouvrir            → inchangé, dans la profondeur.
    """
    sid = _mk_completed_session()
    r = client.get(f"/sessions/{sid}/done")
    assert r.status_code == 200
    body = r.text

    # Le fait de complétion, en tête. Le compte fait est en `<strong>`, donc
    # la comparaison se fait sur le TEXTE rendu : chercher « 2 / 3 » dans le
    # HTML brut échouerait sur un balisage, pas sur une absence.
    texte_brut = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", body))
    assert "2 / 3 séries" in texte_brut

    # Le relevé par exercice survit, dans la profondeur.
    assert "E1" in body
    assert "Incline Smith Press" in body
    assert "2/3" in body

    # L'administration de séance survit, démotée.
    assert "Rouvrir" in body
    assert f"/sessions/{sid}" in body
    assert 'name="action" value="reopen"' in body

    # Et ce qui part est parti pour de bon.
    corps = body[body.index('class="closeout"'):]
    assert "79,4" not in corps, (
        "le poids de corps est rendu au closeout — il appartient à BODY_LEDGER"
    )


def _mk_completed_cardio_session(
    *,
    duration_min: int = 45,
    bpm_avg: int = 132,
    machine_calories: int = 410,
    machine_type: str = "stairmaster",
) -> int:
    """Create a completed cardio WorkoutSession (inline cardio template)."""
    from app.database import SessionLocal
    from app.models.catalog import WorkoutTemplate
    from app.models.session import WorkoutSession

    started = datetime(2026, 4, 13, 18, 0, tzinfo=UTC)
    ended = datetime(2026, 4, 13, 18, 0 + duration_min, tzinfo=UTC)

    with SessionLocal() as db:
        tpl = WorkoutTemplate(
            slug="cardio-liss-test",
            name="Cardio LISS — test",
            kind="cardio",
        )
        db.add(tpl)
        db.flush()
        s = WorkoutSession(
            user_id=get_test_user_id(),
            template_id=tpl.id,
            template_slug_snapshot=tpl.slug,
            template_name_snapshot=tpl.name,
            started_at=started,
            ended_at=ended,
            status="completed",
            cardio_duration_min=duration_min,
            cardio_bpm_avg=bpm_avg,
            cardio_machine_calories=machine_calories,
            cardio_machine_type=machine_type,
        )
        db.add(s)
        db.commit()
        return s.id


def test_done_page_shows_cardio_recap_for_cardio_kind(client):
    sid = _mk_completed_cardio_session()
    r = client.get(f"/sessions/{sid}/done")
    assert r.status_code == 200
    body = r.text
    # ⚠ `UI-CP7.5B` — les faits cardio montent en TÊTE, là où l'ancien écran
    # ouvrait par « Work sets 0 / 0 » et rangeait la durée réelle six cartes
    # plus bas. La mesure de complétion dépend désormais du type de séance.
    corps = body[body.index('class="closeout"'):]
    assert "45" in corps
    assert "min" in corps.lower()
    assert "132" in corps
    assert "bpm" in corps.lower()
    assert "stairmaster" in corps
    # Les calories machine restent lisibles, mais dans le relevé : le produit
    # les qualifie lui-même d'« indicatif », elles ne mesurent pas la séance.
    assert "410" in body
    # Aucun compte de séries de travail sur une séance qui n'en a pas.
    assert "0 / 0" not in corps
    assert "Par exercice" not in body


def test_done_page_shows_substitution_arrow(client):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    sid = _mk_completed_session()
    with SessionLocal() as db:
        session = db.get(WorkoutSession, sid)
        session.session_exercises[0].substituted_name = "Développé couché haltères"
        db.commit()

    r = client.get(f"/sessions/{sid}/done")
    assert r.status_code == 200
    assert "Développé couché haltères" in r.text
    assert "→" in r.text


def test_done_page_shows_confidence_badge(client):
    """⚠ `UI-CP7.5B` — LE SCORE NE SURVIT PAS, ET LA GARDE LE PROUVE.

    Elle exigeait la présence du badge de fiabilité ; elle exige désormais
    son absence. L'arbitrage est explicite : *« QUALITY / CONFIDENCE : neither
    numeric score survives in closeout. A qualitative trust warning may appear
    ONLY when trust materially changes interpretation. »*

    Deux nombres cohabitaient — « Qualité 92 » et « Fiabilité 90 » — sans que
    rien ne dise ce qu'ils décidaient, ni pourquoi il en fallait deux. `§15`
    demandait à tout score encore rendu de prouver quelle décision il sert ;
    aucun des deux ne le pouvait.

    Ce qui les remplace n'est PAS un troisième nombre : une phrase de
    conséquence, rendue uniquement quand un signal consommé par le moteur
    manque, et qui dit l'effet réel — « la prochaine recommandation lira cette
    séance sans savoir ce qu'elle t'a coûté ». Son contrat est gardé dans
    `test_ui_cp75b_instrument_de_transition.py`.

    `compute_confidence_score` n'est PAS supprimé : il reste calculé et part
    dans l'export JSON/CSV, où `confidence_level` est un contrat de données
    déjà livré. C'est son AFFICHAGE qui part.

    ─── mémoire de la garde précédente ────────────────────────────────────
    ⚠ `Sb_UI_SESSION_DONE_01` — ELLE ÉPINGLAIT « Confiance du logging ».

    « logging » est de l'anglais de développeur, et le badge affichait en plus
    la clé brute `eleve` — un identifiant sans accent, parce que c'en est un :
    il part tel quel dans l'export JSON et CSV.

    La garde vérifiait la présence de la ligne ; elle gelait au passage sa
    formulation anglaise. Elle vérifie désormais la PROPRIÉTÉ — la ligne
    existe, elle porte son badge, et elle ne montre pas de clé.
    """
    sid = _mk_completed_session()
    r = client.get(f"/sessions/{sid}/done")
    assert r.status_code == 200
    body = r.text
    # ⚠ `UI-CP7.5B` — ARBITRAGE OPÉRATEUR : « neither numeric score survives
    # in closeout ». Le badge de fiabilité ET le score de qualité partent.
    # Voir la docstring mise à jour ci-dessus.
    assert "Fiabilité de la saisie" not in body
    assert "confidence-badge" not in body
    # La clé ne doit toujours pas atteindre l'écran — a fortiori maintenant.
    texte = re.sub(r"<[^>]+>", " ", body)
    for cle in ("eleve", "logging"):
        assert cle not in texte, (
            f"« {cle} » est rendu à l'écran — c'est une clé de programme, "
            "pas un mot français"
        )


def test_les_zones_sollicitees_appartiennent_au_flight_recorder(client):
    """⚠ `UI-CP7.5B` — DÉMÉNAGEMENT, ET LE PROPRIÉTAIRE EST VÉRIFIÉ.

    « Zones sollicitées » quitte le closeout : c'est de l'analyse, et
    `FLIGHT_RECORDER` la possède. La garde ne se contente PAS de constater
    l'absence — une garde qui vérifie qu'une chose a disparu sans vérifier
    qu'elle est arrivée ailleurs certifie une soustraction (`§5.3`).

    Le propriétaire est `_partials/zone_exposure.html`, inclus par
    `/progress` : le comptage de séries par zone sur quatorze jours. La
    commande dominante du closeout y mène.
    """
    import pathlib

    sid = _mk_completed_session()
    body = client.get(f"/sessions/{sid}/done").text
    corps = body[body.index('class="closeout"'):]
    assert "Zones sollicitées" not in corps

    racine = pathlib.Path(__file__).resolve().parent.parent
    progress = (racine / "app/templates/progress.html").read_text(
        encoding="utf-8")
    assert "zone_exposure" in progress, (
        "le closeout a cédé les zones à FLIGHT_RECORDER, qui ne les rend plus"
    )
    assert (racine / "app/templates/_partials/zone_exposure.html").exists()


def test_done_page_shows_anomalies_when_present(client):
    """Inject a completed-empty set so rule A fires and 'À vérifier' renders."""
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    sid = _mk_completed_session()
    with SessionLocal() as db:
        session = db.get(WorkoutSession, sid)
        # Mark the third set (currently uncompleted) as completed-empty.
        se = session.session_exercises[0]
        work = sorted(
            [sl for sl in se.set_logs if sl.kind == "work"],
            key=lambda s: s.set_index,
        )
        work[-1].completed = True
        work[-1].weight_kg = None
        work[-1].reps = None
        db.commit()

    r = client.get(f"/sessions/{sid}/done")
    body = r.text
    # ⚠ `UI-CP7.5B` — l'anomalie n'a plus sa carte « À vérifier » ; elle est
    # l'ÉTIQUETTE du tiroir de cycle de vie, parce que rouvrir pour corriger
    # est la seule conséquence qu'elle ait jamais eue. Le message intégral
    # reste rendu, dans la profondeur.
    assert "à vérifier" in body
    assert "closeout__alerte" in body
    assert "sans reps ni charge" in body
