"""`UI-CP7.5B` — le closeout est un INSTRUMENT DE TRANSITION, pas un tableau.

La nouvelle règle macro d'acceptation (`arbitrage opérateur §1`) dit qu'une
tranche UI ne compte comme transformation que si elle change matériellement au
moins un axe parmi TOPOLOGIE D'OBJETS · MODÈLE D'INTERACTION · HIÉRARCHIE DE
DÉCISION · PROPRIÉTÉ DE L'INFORMATION · CHROME PERSISTANT — et que « cacher du
contenu hérité dans un `<details>` » n'en est pas un.

Ces gardes épinglent donc les axes, pas la prose ni l'espacement.

⚠ CHAQUE GARDE ICI A ÉTÉ VÉRIFIÉE PAR MUTATION. Une garde qui n'a jamais été
vue rouge ne garde rien — ce dépôt en a recensé seize.
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DONE = ROOT / "app/templates/session_done.html"
ROUTEUR = ROOT / "app/routers/sessions.py"


def _sans_commentaires(src: str) -> str:
    """Le gabarit SANS ses commentaires Jinja.

    ⚠ J'AI DÉJÀ LU MA PROPRE PROSE COMME DU CODE. En `UI-CP7`, trois gardes
    ont accusé un gabarit sain parce qu'elles trouvaient `#999` et
    `.doc-head__title` dans les commentaires que j'avais écrits juste
    au-dessus. Ici les commentaires citent « Qualité », « card » et
    « dashboard » en les décrivant comme retirés : une garde naïve les
    trouverait et conclurait l'inverse de la vérité.
    """
    return re.sub(r"\{#.*?#\}", "", src, flags=re.S)


def _demarrer(client, slug: str = "push-a") -> int:
    r = client.post("/sessions", data={"template_slug": slug},
                    follow_redirects=False)
    return int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


def _clore(client, sid: int, **champs) -> str:
    data = {"action": "end"}
    data.update(champs)
    client.post(f"/sessions/{sid}", data=data, follow_redirects=False)
    return client.get(f"/sessions/{sid}/done").text


def _compter_classe(html: str, nom: str) -> int:
    """Compte les ÉLÉMENTS portant la classe `nom`, en jetons.

    ⚠ `html.count("closeout__commande")` en rendait DEUX : l'élément et son
    `closeout__commande-fleche`. Une sous-chaîne n'est pas un objet — c'est
    la troisième fois de ce programme, et la deuxième de ma main.
    """
    return sum(
        1 for attr in re.findall(r'class="([^"]*)"', html)
        if nom in attr.split()
    )


def _sans_commentaires_python(src: str) -> str:
    """Le module SANS ses commentaires `#`.

    Même piège que côté gabarit, et je viens de le retomber : le commentaire
    qui EXPLIQUE la suppression de `implicit_by_se` contient le mot
    `implicit_by_se`, donc la garde concluait que le calcul était resté.
    """
    return re.sub(r"(?m)^\s*#.*$", "", src)


# ───────── AXE 1 · TOPOLOGIE D'OBJETS ─────────


def test_le_closeout_ne_porte_plus_aucune_carte():
    """Huit `.card` de même poids ne hiérarchisaient rien.

    Le relief est dépensé sur UN objet plein — la commande — au lieu d'être
    étalé sur huit boîtes identiques.
    """
    src = _sans_commentaires(DONE.read_text(encoding="utf-8"))
    for attr in re.findall(r'class="([^"]*)"', src):
        assert "card" not in attr.split(), (
            f"une carte survit dans le closeout : class=\"{attr}\""
        )


def test_une_seule_section_de_premier_rang_est_titree(client):
    """Cinq `<h2>` de même rang se disputaient l'attention.

    Il ne reste qu'un `DISPLAY` : le nom de la séance. Aucun `<h2>`, parce
    qu'il n'y a plus de sections concurrentes à titrer.
    """
    sid = _demarrer(client)
    body = _clore(client, sid, concentration="high", global_state="good")
    corps = body[body.index('class="closeout"'):]
    assert corps.count("<h1") == 1, "le closeout doit porter UN seul titre"
    assert "<h2" not in corps, (
        "un titre de section est réapparu — la page redevient une pile de "
        "blocs co-souverains"
    )


# ───────── AXE 2 · HIÉRARCHIE DE DÉCISION ─────────


def test_une_seule_commande_dominante_et_elle_mene_au_debrief(client):
    """⚠ LA DOMINANTE D'AVANT MENAIT À UNE SURFACE DÉPRÉCIÉE.

    L'ancien closeout portait `btn btn--primary btn--wide` → « Voir la
    synthèse » → `/dashboard`, que `test_navigation_does_not_promote_dashboard`
    déclare dépréciée. Cinq sorties de même rang, et la seule mise en avant
    était la mauvaise.
    """
    sid = _demarrer(client)
    body = _clore(client, sid, concentration="high", global_state="good")
    corps = body[body.index('class="closeout"'):]

    assert _compter_classe(corps, "closeout__commande") == 1, (
        "il doit y avoir exactement UNE commande dominante"
    )
    assert "/progress" in corps, "la commande dominante doit mener au débrief"
    assert "/dashboard" not in corps, (
        "le closeout promeut à nouveau /dashboard, surface dépréciée"
    )
    assert "btn--primary" not in corps, (
        "un second bouton primaire recrée la concurrence de rang"
    )


def test_le_closeout_ne_rend_plus_aucun_score_numerique(client):
    """Arbitrage opérateur : « neither numeric score survives in closeout ».

    « Qualité 92 » et « Fiabilité 90 » cohabitaient sans dire ce qu'ils
    décidaient. §15 exigeait qu'un score prouve quelle décision il sert ;
    aucun des deux ne pouvait.
    """
    sid = _demarrer(client)
    body = _clore(client, sid, concentration="high", global_state="good")
    corps = body[body.index('class="closeout"'):]

    for interdit in ("Qualité", "Fiabilité de la saisie",
                     "Décomposition du score", "confidence-badge",
                     "implicit-pill", "score-breakdown"):
        assert interdit not in corps, (
            f"{interdit!r} est revenu sur le closeout"
        )


def test_le_routeur_ne_calcule_plus_les_charges_de_score():
    """La contrepartie serveur : on ne calcule plus ce qu'on ne rend plus.

    Sans cette garde, le rendu pourrait repartir d'un simple `{% if %}` dans
    le gabarit, sur une charge utile restée en place.
    """
    src = _sans_commentaires_python(ROUTEUR.read_text(encoding="utf-8"))
    bloc = src[src.index("def session_done("):]
    fin = bloc.find("\ndef ", 1)
    bloc = bloc[:fin] if fin > 0 else bloc
    for interdit in ("implicit_by_se", "breakdown", "build_session_review"):
        assert interdit not in bloc, (
            f"{interdit!r} est encore calculé pour le closeout"
        )


# ───────── AXE 3 · MODÈLE D'INTERACTION ─────────


def test_la_prose_de_consigne_ne_revient_pas():
    """⚠ « Pense à indiquer ton ressenti sur les PROCHAINES séances. »

    L'ancienne surface décrivait un comportement futur au lieu d'offrir le
    geste présent. Un contrôle remplace une consigne.
    """
    src = _sans_commentaires(DONE.read_text(encoding="utf-8"))
    for consigne in ("Pense à", "N'oublie pas", "Pense a"):
        assert consigne not in src, (
            f"prose de consigne rendue : {consigne!r} — le closeout doit "
            "offrir le contrôle, pas prescrire un comportement"
        )


def test_le_releve_descend_dans_la_profondeur_sans_disparaitre(client):
    """`CLAUDE.md §5.3` — jamais une soustraction seule.

    ⚠ MESURÉ : `/sessions/{id}` rend un 303 vers cette page pour toute séance
    terminée, et `/history` n'est qu'une liste. Le closeout est donc la SEULE
    lecture possible de ce qu'on vient d'enregistrer. Le relevé change de
    RANG, il ne change pas de propriétaire — faute de second propriétaire.
    """
    sid = _demarrer(client)
    body = _clore(client, sid, concentration="high", global_state="good")

    assert "closeout__releve" in body, (
        "le relevé par exercice a disparu sans remplaçant"
    )
    # Et il est bien DANS la profondeur, pas au repos.
    tiroir = body[body.index("closeout__cycle"):]
    assert "closeout__releve" in tiroir, (
        "le relevé est au repos au lieu d'être dans le tiroir de cycle de vie"
    )


def test_la_redirection_qui_fait_du_closeout_le_seul_proprietaire(client):
    """PRÉMISSE de la garde ci-dessus, épinglée séparément.

    Si un jour `/sessions/{id}` cesse de rediriger, le relevé a un meilleur
    domicile et cette décision doit être reconsidérée. La garde le dira.
    """
    sid = _demarrer(client)
    client.post(f"/sessions/{sid}", data={"action": "end"},
                follow_redirects=False)
    r = client.get(f"/sessions/{sid}", follow_redirects=False)
    assert r.status_code == 303, (
        "`/sessions/{id}` ne redirige plus une séance terminée : une surface "
        "de détail existe peut-être désormais, et le relevé du closeout "
        "mérite d'y déménager"
    )
    assert r.headers["location"].endswith("/done")


# ───────── AXE 4 · LA MESURE DE COMPLÉTION DÉPEND DU TYPE ─────────


def test_une_seance_cardio_ne_rend_pas_zero_serie(client):
    """⚠ L'ancien écran rendait « Work sets 0 / 0 » en tête d'une séance LISS.

    La durée réelle vivait six cartes plus bas. La ligne de fait porte
    désormais ce qui mesure réellement la séance qu'on vient de faire.
    """
    sid = _demarrer(client, "liss-only")
    body = _clore(client, sid, concentration="high", global_state="good",
                  cardio_duration_min="42", cardio_bpm_avg="131",
                  cardio_machine_type="rameur")
    corps = body[body.index('class="closeout"'):]

    assert "0 séries" not in corps and "0 / 0" not in corps, (
        "une séance cardio rend un compte de séries de travail"
    )
    assert "42" in corps, "la durée réelle du cardio n'est pas rendue"


def test_une_substitution_absente_ne_se_rend_pas(client):
    """« 0 substitution » n'apprend rien : le silence est la bonne lecture."""
    sid = _demarrer(client)
    body = _clore(client, sid, concentration="high", global_state="good")
    corps = body[body.index('class="closeout"'):]
    assert "substitution" not in corps, (
        "le closeout annonce des substitutions qu'il n'y a pas eu"
    )


# ───────── AXE 5 · L'ALERTE D'ANOMALIE DONNE SA RAISON AU TIROIR ─────────


def test_le_tiroir_annonce_les_points_a_verifier_ferme(client):
    """Un tiroir qui ne promet rien ne s'ouvre pas.

    Le compte d'anomalies est visible TIROIR FERMÉ — c'est la seule
    conséquence que ces anomalies ont jamais eue : rouvrir pour corriger.
    """
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    sid = _demarrer(client)
    # Règle A : une série cochée sans charge ni reps.
    with SessionLocal() as db:
        se = db.query(SessionExercise).filter_by(session_id=sid).first()
        db.add(SetLog(session_exercise_id=se.id, kind="work", set_index=99,
                      weight_kg=None, reps=None, completed=True))
        db.commit()

    body = _clore(client, sid, concentration="high", global_state="good")
    assert "closeout__alerte" in body, (
        "des anomalies existent et le tiroir fermé n'en dit rien"
    )
    assert "à vérifier" in body

    with SessionLocal() as db:
        assert db.get(WorkoutSession, sid).status == "completed"


def test_sans_anomalie_le_tiroir_ne_crie_pas(client):
    """La contrepartie : pas d'alerte inventée sur une séance saine."""
    sid = _demarrer(client)
    body = _clore(client, sid, concentration="high", global_state="good")
    assert "closeout__alerte" not in body, (
        "une alerte paraît sur une séance sans anomalie"
    )
