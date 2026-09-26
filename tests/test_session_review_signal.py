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
    """Clôt la séance et rend LA SURFACE QUI RESTITUE.

    ⚠ `UI-CP8D` — CE N'EST PLUS LE CLOSEOUT, ET C'EST UN PROGRÈS.

    `Sb_SESSION_REVIEW_SIGNAL_01` a établi que trois signaux saisis pendant
    la séance n'étaient jamais rendus. La correction les avait posés sur
    `/done`, faute de mieux : une séance terminée n'avait aucune surface à
    elle.

    Elle en a une. La restitution vit donc sur le relevé DURABLE, qu'on peut
    rouvrir des semaines plus tard — au lieu d'une surface de transition
    qu'on ne revoit jamais. La propriété est la même, sa portée est plus
    longue.
    """
    data = {"action": "end"}
    data.update(fields)
    client.post(f"/sessions/{session_id}", data=data, follow_redirects=True)
    return client.get(f"/sessions/{session_id}").text


def _closeout(client, session_id: int, **fields) -> str:
    """La surface de TRANSITION — distincte du relevé depuis `UI-CP8D`.

    ⚠ Un helper partagé qui change de cible désarme les gardes de ses
    appelants sans le dire. En repointant `_finish` vers le relevé, j'ai
    emporté avec lui une garde qui parle du closeout. Les deux surfaces ont
    donc chacune leur accès, nommé.
    """
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
    """⚠ `UI-CP7.5B` — GARDE REPOINTÉE SUR SA PROPRIÉTÉ, PAS AFFAIBLIE.

    Elle épinglait `session-done__sensation`, c'est-à-dire une CLASSE CSS :
    une ÉCRITURE, pas une valeur. La recomposition du closeout renomme la
    classe, donc la garde rougissait pour un changement qui ne touche pas la
    propriété qu'elle défend.

    Ce que la tranche `Sb_SESSION_REVIEW_SIGNAL_01` a réellement établi est :
    « un ressenti saisi pendant la séance est RENDU à l'utilisateur ». C'est
    donc la VALEUR qu'on épingle, et c'est strictement plus fort qu'un nom de
    classe — la valeur ne peut pas revenir sous un autre nom.

    Le ressenti a changé de PLACE : il vit désormais dans le relevé, à
    l'intérieur du tiroir de cycle de vie. Vérifié : aucune autre surface ne
    le rendait (`/sessions/{id}` redirige vers `/done`, `/history` ne montre
    pas même les noms d'exercice), donc le retirer d'ici l'aurait supprimé.
    """
    sid = _start(client)
    se_id = _first_exercise_id(sid)
    client.post(
        f"/sessions/{sid}/exercises/{se_id}",
        data={"muscle_sensation": "strong", "nav": "stay"},
        follow_redirects=False,
    )
    body = _finish(client, sid)
    assert "strong" in body, "the sensation never came back"
    assert "record__ressenti" in body, (
        "the sensation is rendered but not as a sensation — it must stay "
        "identifiable, not merely present somewhere in the markup"
    )


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
    """Un ressenti absent se lit « non mesuré », jamais « neutre ».

    Repointée avec sa sœur ci-dessus : même propriété, nouvelle classe.
    """
    sid = _start(client)
    body = _finish(client, sid)
    assert "record__ressenti" not in body
    assert "Note de séance" not in body


def test_no_placeholder_text_fills_an_empty_signal():
    src = DONE.read_text(encoding="utf-8")
    for filler in ("Non renseigné", "Aucun ressenti", "Pas de note", "N/A"):
        assert filler not in src, f"placeholder for an unrecorded signal: {filler}"


# ───────── aucune collecte ajoutée ─────────


def test_the_review_collects_nothing(client):
    """⚠ ARBITRAGE OPÉRATEUR `UI-CP7.5` §13 — GARDE REDÉFINIE, PAS LEVÉE.

    Cette garde interdisait TOUTE collecte sur le closeout. La directive de
    clôture la contredit frontalement :

        « If non-derivable feedback still needs collecting,
          make that the primary object. »
        « Examples of legitimately user-declared signals:
          concentration / general state / optional note »
        « But first audit whether each signal is still consumed anywhere.
          Do NOT ask the user for data merely because a field exists. »

    La directive EST l'arbitrage. Il est consigné ici plutôt qu'appliqué
    tacitement, parce qu'un prompt ne peut pas désactiver une garde versionnée
    en silence.

    ⚠ MAIS LA GARDE AVAIT RAISON SUR L'ESSENTIEL, ET CE NOYAU SURVIT.
    `Sb_FEEDBACK_SIGNAL_AUDIT_01` avait établi que ce produit sait ajouter des
    champs que personne ne remplit, et que dupliquer un point de collecte
    crée deux sources de vérité. Ma première composition allait commettre
    exactement ça : un bilan de ressenti PERMANENT ici, alors que
    `session_detail.html` le collecte déjà au-dessus de « TERMINER LA SÉANCE ».

    Trois invariants tiennent donc toujours, et ils sont testés :

      1. aucun signal PAR EXERCICE n'est collecté ici — ils ont leur widget
         (`exercise_card.html`), et le closeout n'en est pas un second ;
      2. aucun champ n'est INVENTÉ : seuls des champs déjà consommés par un
         service peuvent apparaître ;
      3. la collecte est CONDITIONNELLE à l'absence — elle ne peut pas
         devenir un formulaire au repos. C'est ce que prouve
         `test_la_collecte_de_closeout_est_conditionnelle`.
    """
    src = DONE.read_text(encoding="utf-8")

    # 1 — les signaux PAR EXERCICE gardent leur point de collecte unique.
    par_exercice = ("muscle_sensation", "execution_quality", "reps_target")
    for champ in par_exercice:
        assert f'name="{champ}"' not in src, (
            f"le closeout collecte {champ!r}, qui est un signal PAR EXERCICE "
            "— il a déjà son widget dans `exercise_card.html`, et un second "
            "point de collecte est exactement le doublon que "
            "`Sb_FEEDBACK_SIGNAL_AUDIT_01` a recensé"
        )

    # 2 — aucun champ de saisie libre : la note de séance se saisit là où
    #     elle se saisissait, et le closeout la RESTITUE seulement.
    assert "<textarea" not in src, (
        "une zone de texte ferait du closeout un point de saisie de la note, "
        "alors que `session_detail.html` la collecte déjà"
    )
    assert "<select" not in src


def test_la_collecte_de_closeout_est_conditionnelle(client):
    """⚠ CE QUI EMPÊCHE LA COLLECTE DE DEVENIR UN FORMULAIRE AU REPOS.

    C'est la garde qui rend l'arbitrage §13 tenable : le closeout ne demande
    QUE ce qui manque. Déclarés, les contrôles disparaissent — donc il n'y a
    jamais deux formulaires au repos pour les mêmes colonnes.
    """
    # a) séance close SANS ressenti → les contrôles paraissent.
    sid = _start(client)
    creux = _closeout(client, sid)
    assert 'name="concentration"' in creux, (
        "un signal consommé par le moteur manque, et le closeout ne l'a pas "
        "demandé"
    )
    assert 'name="global_state"' in creux

    # b) séance close AVEC ressenti → plus rien à demander.
    sid2 = _start(client)
    complet = _closeout(client, sid2, concentration="high", global_state="good")
    assert 'name="concentration"' not in complet, (
        "le closeout redemande un signal DÉJÀ déclaré — c'est un second "
        "formulaire au repos, ce que `Sb_SESSION_REVIEW_SIGNAL_01` interdit"
    )
    assert 'name="global_state"' not in complet


def test_le_closeout_ne_collecte_que_des_signaux_consommes():
    """§13 : « Do NOT ask the user for data merely because a field exists. »

    `bodyweight_kg` est le cas d'espèce : le champ existe, `confidence` lui
    donne même 10 points — et le closeout ne le réclame pas, parce que
    `BODY_LEDGER` en est le propriétaire depuis `CP7.5A`.
    """
    src = DONE.read_text(encoding="utf-8")
    assert 'name="bodyweight_kg"' not in src, (
        "le closeout réclame le poids de corps au seul motif que le champ "
        "existe — il appartient à BODY_LEDGER"
    )

    # Et les deux qu'il réclame sont bien consommés par le moteur.
    from app.services import behavioral
    source = __import__("inspect").getsource(behavioral)
    for champ in ("concentration", "global_state"):
        assert champ in source, (
            f"{champ!r} est collecté au closeout mais `behavioral` ne le lit "
            "plus — la prémisse de §13 a cessé d'être vraie"
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
