"""Sb_SESSION_REVIEW_SIGNAL_01 — rendre ce qui est déjà collecté.

`Sb_FEEDBACK_SIGNAL_AUDIT_01` a établi que le produit sait ajouter des champs
que personne ne remplit. Le symétrique était vrai aussi : trois signaux
**saisis pendant la séance** n'étaient jamais rendus à l'utilisateur —
`muscle_sensation` et la note par exercice, et la note de séance.

Cette tranche ne collecte RIEN. Elle expose l'existant, et le silence quand
il n'y a rien à dire.
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
RECAP = ROOT / "app/services/session_recap.py"
DONE = ROOT / "app/templates/session_done.html"
CARD = ROOT / "app/templates/_partials/exercise_card.html"


def _start(client, slug: str = "push-a") -> int:
    r = client.post("/sessions", data={"template_slug": slug},
                    follow_redirects=False)
    return int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


def _first_exercise_id(session_id: int) -> int:
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import SessionExercise

    with SessionLocal() as db:
        return db.execute(
            select(SessionExercise.id)
            .where(SessionExercise.session_id == session_id)
            .order_by(SessionExercise.position.asc())
            .limit(1)
        ).scalar_one()


def _finish(client, session_id: int, **fields) -> str:
    data = {"action": "end"}
    data.update(fields)
    client.post(f"/sessions/{session_id}", data=data, follow_redirects=True)
    return client.get(f"/sessions/{session_id}/done").text


# ───────── le recap porte désormais les trois signaux ─────────


def test_the_recap_exposes_the_per_exercise_sensation():
    src = RECAP.read_text(encoding="utf-8")
    assert '"muscle_sensation": se.muscle_sensation' in src


def test_the_recap_exposes_the_per_exercise_note():
    src = RECAP.read_text(encoding="utf-8")
    assert '"note": se.free_note' in src


def test_the_recap_exposes_the_session_note():
    src = RECAP.read_text(encoding="utf-8")
    assert '"note": session.free_note' in src


# ───────── rendu réel ─────────


def test_a_recorded_sensation_comes_back_in_the_review(client):
    sid = _start(client)
    se_id = _first_exercise_id(sid)
    client.post(
        f"/sessions/{sid}/exercises/{se_id}",
        data={"muscle_sensation": "strong", "nav": "stay"},
        follow_redirects=False,
    )
    body = _finish(client, sid)
    assert "session-done__sensation" in body, "the sensation never came back"
    assert "strong" in body


def test_a_recorded_exercise_note_comes_back_in_the_review(client):
    sid = _start(client)
    se_id = _first_exercise_id(sid)
    needle = "coude droit sensible"
    client.post(
        f"/sessions/{sid}/exercises/{se_id}",
        data={"free_note": needle, "nav": "stay"},
        follow_redirects=False,
    )
    body = _finish(client, sid)
    assert needle in body, "the exercise note never came back"


def test_a_recorded_session_note_comes_back_in_the_review(client):
    sid = _start(client)
    needle = "salle bondee, tout decale"
    body = _finish(client, sid, free_note=needle)
    assert needle in body, "the session note never came back"
    assert "Note de séance" in body


# ───────── silence honnête ─────────


def test_nothing_recorded_means_nothing_shown(client):
    """Un ressenti absent se lit « non mesuré », jamais « neutre »."""
    sid = _start(client)
    body = _finish(client, sid)
    assert "session-done__sensation" not in body
    assert "Note de séance" not in body


def test_no_placeholder_text_fills_an_empty_signal():
    src = DONE.read_text(encoding="utf-8")
    for filler in ("Non renseigné", "Aucun ressenti", "Pas de note", "N/A"):
        assert filler not in src, f"placeholder for an unrecorded signal: {filler}"


# ───────── aucune collecte ajoutée ─────────


def test_the_review_collects_nothing(client):
    """La revue RESTITUE. Y ajouter un champ ferait d'elle une surface de
    saisie, ce que cette tranche refuse explicitement."""
    # Assertion resserrée : la revue porte légitimement un `<input hidden>`
    # pour l'action « Rouvrir pour éditer ». L'invariant vise la COLLECTE DE
    # FEEDBACK, pas tout contrôle de formulaire — une garde large aurait
    # interdit du balisage d'action sans rapport.
    src = DONE.read_text(encoding="utf-8")
    assert "<textarea" not in src, "a textarea would make the review a form"
    assert "<select" not in src, "a select would make the review a form"

    feedback_fields = (
        "muscle_sensation", "free_note", "concentration",
        "global_state", "execution_quality", "reps_target",
    )
    for field in feedback_fields:
        assert f'name="{field}"' not in src, (
            f"the review collects {field!r} — restitution must not become "
            "collection"
        )


def test_the_collection_widget_is_unchanged():
    """Le ressenti se saisit toujours au même endroit, avec le même nom."""
    src = CARD.read_text(encoding="utf-8")
    assert '"muscle_sensation",' in src
    assert '("strong", "Fort"), ("partial", "Partiel"), ("weak", "Faible")' in src


def test_no_new_label_vocabulary_was_invented():
    """La valeur brute est rendue, comme le fait déjà `exercise_history`.

    Dupliquer ici la table de libellés du widget de saisie créerait une
    deuxième source de vérité — exactement le doublon recensé par l'audit.
    """
    src = DONE.read_text(encoding="utf-8")
    for label in ("Fort", "Partiel", "Faible"):
        assert f">{label}<" not in src, (
            f"{label!r} duplicates the collection widget's vocabulary"
        )
