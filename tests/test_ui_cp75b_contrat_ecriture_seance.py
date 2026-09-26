"""`UI-CP7.5B` — rouvrir une séance n'efface plus ce qu'on avait déclaré.

⚠ CE DÉFAUT ÉTAIT EN PRODUCTION, SUR LA BOUCLE PRIMAIRE.
--------------------------------------------------------
`update_session` écrivait six champs **inconditionnellement** depuis le
formulaire : absent → `None`. Or le bouton « Rouvrir pour éditer » du closeout
poste un formulaire qui ne porte QUE `action=reopen`.

Mesuré sur la vraie route, avant correction :

    avant rouverture : ('high', 'good', 78.5, 'bonne séance')
    après rouverture : (None, None, None, None)

La gravité n'est pas seulement la perte de saisie. `concentration` et
`global_state` sont consommés par `behavioral`, qui produit le
`fatigue_score`, que **le moteur de recommandation** consomme à son tour.
Rouvrir une séance dégradait donc silencieusement la décision suivante.

C'est la même classe de défaut que le contrat d'écriture corporel de
`CP7.5A` : une sémantique de REMPLACEMENT appliquée à un formulaire PARTIEL.
Trouvée en construisant le closeout, pas en le cherchant.
"""
from __future__ import annotations


def _demarrer(client, slug: str = "push-a") -> int:
    r = client.post("/sessions", data={"template_slug": slug},
                    follow_redirects=False)
    assert r.status_code in {302, 303}
    return int(r.headers["location"].rstrip("/").split("/")[-1])


def _signaux(session_id: int) -> tuple:
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    with SessionLocal() as db:
        s = db.get(WorkoutSession, session_id)
        return (s.concentration, s.global_state, s.bodyweight_kg, s.free_note)


def test_rouvrir_une_seance_preserve_les_signaux_declares(client):
    """⚠ LE CAS QUI A RÉVÉLÉ LE DÉFAUT."""
    sid = _demarrer(client)
    client.post(f"/sessions/{sid}", data={
        "concentration": "high", "global_state": "good",
        "bodyweight_kg": "78.5", "free_note": "bonne séance",
        "action": "end"}, follow_redirects=False)

    avant = _signaux(sid)
    assert avant == ("high", "good", 78.5, "bonne séance"), (
        f"prémisse : les signaux sont bien enregistrés — {avant}"
    )

    # Le formulaire de rouverture ne porte QUE `action`.
    client.post(f"/sessions/{sid}", data={"action": "reopen"},
                follow_redirects=False)

    assert _signaux(sid) == avant, (
        "rouvrir a effacé des signaux que l'utilisateur avait déclarés — et "
        "que le moteur de recommandation consomme"
    )


def test_le_cardio_survit_aussi_a_une_rouverture(client):
    """Les quatre champs cardio subissaient le même effacement.

    Une garde qui ne couvrirait que les signaux de ressenti laisserait la
    moitié du défaut en place.
    """
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    sid = _demarrer(client, "liss-only")
    client.post(f"/sessions/{sid}", data={
        "cardio_duration_min": "42", "cardio_bpm_avg": "128",
        "cardio_machine_type": "rameur", "action": "end"},
        follow_redirects=False)

    with SessionLocal() as db:
        s = db.get(WorkoutSession, sid)
        avant = (s.cardio_duration_min, s.cardio_bpm_avg, s.cardio_machine_type)
    assert avant == (42, 128, "rameur"), f"prémisse : cardio saisi — {avant}"

    client.post(f"/sessions/{sid}", data={"action": "reopen"},
                follow_redirects=False)

    with SessionLocal() as db:
        s = db.get(WorkoutSession, sid)
        apres = (s.cardio_duration_min, s.cardio_bpm_avg, s.cardio_machine_type)
    assert apres == avant, f"le cardio a été effacé par la rouverture : {apres}"


def test_un_champ_soumis_vide_efface_toujours(client):
    """⚠ ON N'A PAS RENDU L'EFFACEMENT IMPOSSIBLE, ON L'A RENDU EXPLICITE.

    Corriger une note en la vidant reste un geste légitime. Ce qui disparaît
    est l'effacement par ABSENCE, qui n'était le geste de personne.
    """
    sid = _demarrer(client)
    client.post(f"/sessions/{sid}", data={
        "concentration": "high", "free_note": "à corriger"},
        follow_redirects=False)
    assert _signaux(sid)[3] == "à corriger"

    client.post(f"/sessions/{sid}", data={
        "concentration": "high", "free_note": ""}, follow_redirects=False)
    assert _signaux(sid)[3] in (None, ""), (
        "un champ soumis vide ne s'efface plus — l'effacement explicite a été "
        "perdu en corrigeant l'effacement implicite"
    )


def test_le_formulaire_complet_ecrit_toujours_tout(client):
    """Le comportement de la saisie complète ne change pas.

    C'est la contrepartie : restreindre l'écriture aux champs soumis ne doit
    pas empêcher le formulaire qui les soumet tous de tous les écrire.
    """
    sid = _demarrer(client)
    client.post(f"/sessions/{sid}", data={
        "concentration": "low", "global_state": "fatigued",
        "bodyweight_kg": "80", "free_note": "dur"}, follow_redirects=False)
    assert _signaux(sid) == ("low", "fatigued", 80.0, "dur")
