"""`UI-CP8D` — une séance terminée a une surface à elle, et la chaîne tient.

⚠ LE DÉFAUT ÉTAIT MESURÉ, PAS SUPPOSÉ.

`JOURNEY C` — finir, voir le débrief, rouvrir la séance — était rompu :

    /sessions/{id}/done   « Voir le débrief »
        → /progress       un agrégat de 2,39 écrans
        → cul-de-sac      rien ne ramène à la séance qu'on vient de finir

Et trois liens du produit prétendaient déjà « ouvrir la séance » —
`history`, `exercise_history`, `admin_sessions` — mais `session_detail`
REDIRIGEAIT (303) toute séance terminée vers le closeout. La navigation
existait ; sa destination était une surface de transition.

`/history` était pire que ça : mesuré, il ne rendait **aucun** lien vers une
séance. Ses lignes ne faisaient que SÉLECTIONNER, rechargeant la page avec
`?session=N` pour faire apparaître un bloc portant un second lien.

Ces gardes épinglent la chaîne causale, pas une mise en page.
"""
from __future__ import annotations

import re

from app.models.session import WorkoutSession


def _demarrer(client, slug: str = "push-a") -> int:
    r = client.post("/sessions", data={"template_slug": slug},
                    follow_redirects=False)
    return int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


def _clore(client, sid: int, **champs) -> None:
    data = {"action": "end"}
    data.update(champs)
    client.post(f"/sessions/{sid}", data=data, follow_redirects=False)


# ───────── LE PROPRIÉTAIRE DURABLE EXISTE ─────────


def test_une_seance_terminee_ne_redirige_plus_vers_la_cloture(client):
    """⚠ CETTE GARDE EST L'INVERSE DE CELLE DE `CP7.5`, ET C'EST VOULU.

    `test_la_redirection_qui_fait_du_closeout_le_seul_proprietaire` épinglait
    le 303 en disant : « le jour où cette route cesse de rediriger, une
    surface de détail existe peut-être, et le relevé du closeout mérite d'y
    déménager. » Ce jour est arrivé, la garde a rougi, et elle est remplacée
    par son contraire.

    C'est le cycle de vie normal d'un cliquet qui garde une PRÉMISSE : il
    meurt quand la prémisse tombe, et il dit pourquoi.
    """
    sid = _demarrer(client)
    _clore(client, sid)

    r = client.get(f"/sessions/{sid}", follow_redirects=False)
    assert r.status_code == 200, (
        f"une séance terminée rend {r.status_code} au lieu de son relevé"
    )
    assert "record__titre" in r.text


def test_le_releve_dit_ce_qui_a_ete_fait(client):
    """La question souveraine, première moitié."""
    sid = _demarrer(client)
    _clore(client, sid)
    corps = client.get(f"/sessions/{sid}").text

    assert "Ce qui a été fait" in corps
    assert "record__exercices" in corps


def test_la_lignee_de_substitution_est_preservee(client):
    """« prescribed vs executed » — un remplacement sans son origine n'est
    pas une lignée."""
    from app.database import SessionLocal
    from app.models.session import SessionExercise

    sid = _demarrer(client)
    with SessionLocal() as db:
        se = (db.query(SessionExercise)
              .filter_by(session_id=sid).order_by(SessionExercise.position)
              .first())
        prescrit = se.exercise_name_snapshot
        se.substituted_name = "Développé incliné haltères"
        db.commit()
    _clore(client, sid)

    corps = client.get(f"/sessions/{sid}").text
    assert "Développé incliné haltères" in corps, "l'exécuté manque"
    assert prescrit in corps, "le PRESCRIT a disparu — ce n'est plus une lignée"
    assert "au lieu de" in corps


# ───────── LA PROVENANCE, QUI N'ÉTAIT RENDUE NULLE PART ─────────


def test_le_releve_dit_d_ou_vient_la_seance(client):
    """⚠ CETTE DONNÉE EXISTE DEPUIS `REC-CP4` ET N'ÉTAIT RENDUE NULLE PART.

    `recommendation_episodes` porte le conseil donné et son issue. C'est la
    SEULE donnée qui relie une séance à la décision qui l'a précédée — donc
    la continuité causale que `§6` réclame.
    """
    from datetime import UTC, datetime

    from app.database import SessionLocal
    from app.models.recommendation_episode import ACCEPTED_TOP, RecommendationEpisode
    from tests.helpers import get_test_user_id

    sid = _demarrer(client)
    _clore(client, sid)
    with SessionLocal() as db:
        db.add(RecommendationEpisode(
            user_id=get_test_user_id(),
            context_fingerprint=f"garde-{sid}",
            policy_version="v3",
            # `decided_at` est NOT NULL : un conseil sans date de décision
            # n'est pas un épisode. Le modèle l'impose, pas ce test.
            decided_at=datetime.now(UTC),
            proposed_top_slug="push-a",
            outcome=ACCEPTED_TOP,
            chosen_slug="push-a",
            session_id=sid,
        ))
        db.commit()

    corps = client.get(f"/sessions/{sid}").text
    assert "record__provenance" in corps, "la provenance n'est pas rendue"
    assert "AUREN recommandait" in corps


def test_une_seance_sans_episode_n_invente_aucune_provenance(client):
    """L'absence d'épisode est un état LÉGITIME — toutes les séances
    antérieures à `REC-CP4`, et toute séance démarrée hors d'un conseil.
    Elle se tait ; elle ne se fabrique pas."""
    sid = _demarrer(client)
    _clore(client, sid)
    corps = client.get(f"/sessions/{sid}").text
    assert "record__provenance" not in corps
    assert "AUREN recommandait" not in corps


# ───────── LA CHAÎNE CAUSALE ─────────


def test_la_cloture_mene_au_releve_de_cette_seance(client):
    """⚠ Elle menait à `/progress`, un agrégat, d'où rien ne revenait."""
    sid = _demarrer(client)
    _clore(client, sid, concentration="high", global_state="good")

    corps = client.get(f"/sessions/{sid}/done").text
    commande = re.search(
        r'<a class="closeout__commande"[^>]*href="([^"]+)"', corps)
    assert commande is not None, "la commande dominante a disparu"
    assert commande.group(1).endswith(f"/sessions/{sid}"), (
        f"la commande mène à {commande.group(1)!r} et non au relevé de "
        "cette séance"
    )


def test_le_journal_mene_directement_a_une_seance(client):
    """⚠ MESURÉ AVANT : `/history` ne rendait AUCUN lien vers une séance.

    Ses lignes rechargeaient la page avec `?session=N` pour faire paraître
    un bloc portant un second lien. Deux gestes, et un état de sélection
    dans l'URL — parce qu'« ouvrir » ne menait nulle part d'utile.
    """
    sid = _demarrer(client)
    _clore(client, sid)

    corps = client.get("/history").text
    assert f"/sessions/{sid}" in corps, (
        "le journal ne mène à aucune séance"
    )
    assert "?session=" not in corps, (
        "la sélection en place est revenue — la ligne doit OUVRIR la séance"
    )


def test_le_releve_remonte_au_journal_et_descend_a_la_progression(client):
    """`§6` — la chaîne se parcourt dans les deux sens, sans archéologie."""
    sid = _demarrer(client)
    _clore(client, sid)
    corps = client.get(f"/sessions/{sid}").text
    suite = corps[corps.index("record__suite"):]
    suite = suite[:suite.index("</nav>")]
    assert "/history" in suite, "on ne remonte pas au journal"
    assert "/progress" in suite, "on ne descend pas à la progression"


# ───────── LA DETTE DE `CP7.5` EST SOLDÉE ─────────


def test_le_releve_a_quitte_la_profondeur_de_la_cloture(client):
    """`D1` — « dès que ce propriétaire existe, le relevé QUITTE la
    profondeur du closeout ». Il existe ; il part."""
    sid = _demarrer(client)
    _clore(client, sid, concentration="high", global_state="good")
    corps = client.get(f"/sessions/{sid}/done").text

    assert "closeout__releve" not in corps, (
        "le relevé par exercice est encore dans le closeout"
    )
    # Et la capacité n'est pas perdue : elle est sur le relevé durable.
    assert "record__exercices" in client.get(f"/sessions/{sid}").text


def test_la_cloture_garde_sa_transition_et_son_cycle_de_vie(client):
    """La contrepartie : retirer le relevé ne doit pas vider le closeout de
    ce qui lui appartient VRAIMENT."""
    sid = _demarrer(client)
    _clore(client, sid, concentration="high", global_state="good")
    corps = client.get(f"/sessions/{sid}/done").text

    assert "closeout__commande" in corps, "la transition a disparu"
    assert 'name="action" value="reopen"' in corps, "le cycle de vie a disparu"
    assert "Séance terminée" in corps


def test_le_bilan_reste_inatteignable_pour_une_seance_terminee(client):
    """PRÉMISSE du déménagement : `?view=bilan` redirigeait DÉJÀ avant
    `CP8D`, donc le relevé durable ne prend la place de rien."""
    sid = _demarrer(client)
    _clore(client, sid)
    from app.database import SessionLocal

    with SessionLocal() as db:
        assert db.get(WorkoutSession, sid).status == "completed"

    r = client.get(f"/sessions/{sid}?view=bilan", follow_redirects=False)
    assert r.status_code == 200, (
        "le relevé doit répondre ; `?view=bilan` est un paramètre mort pour "
        "une séance terminée, pas une seconde surface"
    )
    assert "record__titre" in r.text
