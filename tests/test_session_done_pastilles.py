"""Sb_24.6 — pastille label + score breakdown on /sessions/{id}/done.

Hard contracts validated:
* La page /sessions/{id}/done répond 200 sur une session terminée.
* Quand au moins un exercice porte un implicit_label, la pastille
  apparaît dans le HTML avec le bon display name.
* Quand aucun exercice n'est labellé, aucune pastille n'apparaît.
* Le bloc "Décomposition du score" s'affiche pour scoring_version=2
  ET au moins un label.
* Pas de bloc breakdown pour scoring_version=1.
* Pas de breakdown pour les sessions cardio.
"""
from __future__ import annotations

from sqlalchemy import select


def _create_and_complete_strength(client, with_pattern=False):
    """Crée une session push-a, log un pattern trajectoire_coherente sur
    le 1er exo si demandé, puis termine la session."""
    r = client.post(
        "/sessions", data={"template_slug": "push-a"}, follow_redirects=False
    )
    assert r.status_code == 303
    sid = int(r.headers["location"].rsplit("/", 1)[-1])

    if with_pattern:
        from sqlalchemy.orm import selectinload

        from app.database import SessionLocal
        from app.models.session import SessionExercise, SetLog

        with SessionLocal() as db:
            se = db.execute(
                select(SessionExercise)
                .where(SessionExercise.session_id == sid)
                .options(selectinload(SessionExercise.set_logs))
                .order_by(SessionExercise.position)
            ).scalars().first()
            # Replace work sets with a clean trajectoire_coherente pattern
            for sl in list(se.set_logs):
                if sl.kind == "work":
                    db.delete(sl)
            db.flush()
            for idx, (w, r_count) in enumerate([(80, 10), (80, 8), (80, 6)], start=1):
                db.add(SetLog(
                    session_exercise_id=se.id, kind="work",
                    set_index=idx, weight_kg=w, reps=r_count, completed=True,
                ))
            db.commit()

    # Finish the session
    client.post(
        f"/sessions/{sid}",
        data={"action": "end"},
        follow_redirects=False,
    )
    return sid


def test_done_page_200_basic(client):
    sid = _create_and_complete_strength(client)
    r = client.get(f"/sessions/{sid}/done")
    assert r.status_code == 200


def test_la_pastille_de_label_ne_revient_pas(client):
    """⚠ `UI-CP7.5B` — GARDE RETOURNÉE PAR ARBITRAGE, ET C'EST CONSIGNÉ.

    Cette garde exigeait la pastille ; elle exige maintenant son absence.
    Le retournement n'est pas une commodité : il est écrit noir sur blanc
    dans la directive de clôture.

        « Do not reintroduce weak composite scoring through the back door.
          Any score / confidence / breakdown still rendered must prove:
          what decision it supports, why the user needs it at closeout,
          why Flight Recorder is not its better owner.
          Otherwise demote/remove it. »

    La pastille ne pouvait rien prouver de tel : son infobulle disait
    « Contribution au score V2 : 90/100 » — un interne de calcul, pour un
    score que le même arbitrage retire de cette surface.

    ⚠ LE LABEL LUI-MÊME N'EST PAS SUPPRIMÉ DU PRODUIT.
    `implicit_label` continue d'être calculé et persisté à la clôture, et
    `body_intelligence_block` en rend la distribution sur 30 jours via
    `coach_report._LABEL_DISPLAY_30D`. Ce qui part est son AFFICHAGE PAR
    EXERCICE sur le closeout, pas la donnée ni sa lecture agrégée.
    """
    sid = _create_and_complete_strength(client, with_pattern=True)
    body = client.get(f"/sessions/{sid}/done").text
    assert "implicit-pill" not in body, (
        "la pastille de label implicite est revenue sur le closeout"
    )

    from app.database import SessionLocal
    from app.models.session import SessionExercise

    # PRÉMISSE : le label existe bien, il n'est simplement plus rendu ICI.
    # Sans cette assertion, la garde passerait aussi le jour où le calcul
    # disparaîtrait — elle prouverait alors l'absence d'une absence.
    with SessionLocal() as db:
        labels = db.execute(
            select(SessionExercise.implicit_label)
            .where(SessionExercise.session_id == sid)
        ).scalars().all()
    assert any(x for x in labels), (
        "prémisse rompue : plus aucun `implicit_label` n'est calculé — cette "
        "garde ne prouve plus rien sur le rendu"
    )


def test_done_page_no_pastille_when_no_label(client):
    """Une session sans pattern (< 3 sets remplis ou aucun set rempli)
    n'a pas de label → aucune pastille rendue."""
    sid = _create_and_complete_strength(client, with_pattern=False)
    r = client.get(f"/sessions/{sid}/done")
    body = r.text
    # Pas de pastille
    assert "implicit-pill--" not in body


def test_la_ventilation_du_score_ne_revient_pas(client):
    """Même retournement, même raison — voir la garde de la pastille.

    « Composante classique (V1) × 0,7 · Moyenne des labels implicites × 0,3 »
    expliquait comment un nombre était fabriqué, sur une page d'où ce nombre
    est retiré. Il ne restait qu'une arithmétique sans objet.
    """
    sid = _create_and_complete_strength(client, with_pattern=True)
    body = client.get(f"/sessions/{sid}/done").text
    for interne in ("Décomposition du score", "Composante classique",
                    "Moyenne des labels implicites", "score-breakdown"):
        assert interne not in body, f"{interne!r} est revenu sur le closeout"


def test_done_page_no_breakdown_when_no_label(client):
    """Session V2 mais sans label → breakdown vaut None → bloc absent."""
    sid = _create_and_complete_strength(client, with_pattern=False)
    r = client.get(f"/sessions/{sid}/done")
    body = r.text
    assert "Décomposition du score" not in body


def test_done_page_handles_v1_session_without_breakdown(client):
    """Sessions historiques V1 ne doivent jamais montrer le breakdown."""
    sid = _create_and_complete_strength(client, with_pattern=True)
    # Force scoring_version back to 1 to simulate a pre-Sb_24.3 session
    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    with SessionLocal() as db:
        s = db.execute(
            select(WorkoutSession).where(WorkoutSession.id == sid)
        ).scalar_one()
        s.scoring_version = 1
        db.commit()
    r = client.get(f"/sessions/{sid}/done")
    assert "Décomposition du score" not in r.text


def test_aucune_contribution_numerique_n_est_exposee(client):
    """L'infobulle « Contribution au score V2 : 90/100 » part avec sa pastille.

    ⚠ Et elle ne pouvait pas être lue au doigt : un `title=` ne s'ouvre pas
    sur un écran tactile. Cette surface se lit sur un téléphone — la
    « transparence » que l'infobulle prétendait offrir n'atteignait personne.
    """
    sid = _create_and_complete_strength(client, with_pattern=True)
    body = client.get(f"/sessions/{sid}/done").text
    assert "Contribution au score" not in body
    assert "/100" not in body, (
        "une contribution ou un score sur 100 est rendu au closeout"
    )
