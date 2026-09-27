"""`TRAIN A` — la décision servie lit le contrat CANONIQUE de récupération.

CE QUE LA MIGRATION CORRIGE
----------------------------
Le chemin servi calculait sa propre récupération : un ratio 0–1 dérivé de
`RECOVERY_HOURS_TARGET`. Son défaut tenait en une ligne — une zone **jamais
entraînée** y valait `1.0`, donc « pleinement récupérée ». Une affirmation
physiologique que rien n'appuyait.

Mesuré sur 66 comparaisons zone×corpus contre le contrat canonique :
**62 % de désaccord, dont 40 sur 41 de cette seule cause.**

CE QUE LA MIGRATION NE CHANGE PAS, ET C'EST LE POINT
-----------------------------------------------------
L'arbitrage a tranché : « sans charge observée » est **NON LIMITANT**. Il
n'y a aucune preuve qui doive écarter ce candidat. Il occupe donc le même
RANG qu'une zone connue disponible — et **pas la même PREUVE**.

Mesuré avant d'écrire une ligne :

    pénaliser le « sans charge observée »  →  9 gagnants changés sur 10
    migrer en le gardant non limitant      →  0 gagnant changé sur 60

La distinction rang / preuve vit dans `recovery_evidence_by_zone`, que
l'explication lit et que le classement ignore.

⚠ CHAQUE GARDE ICI A ÉTÉ VUE ROUGE PAR MUTATION.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

pytestmark = pytest.mark.usefixtures("client")


# ═══════════════════════════════════════════════════════════════════════
#  L'ADAPTATEUR DE DÉCISION
# ═══════════════════════════════════════════════════════════════════════


def test_sans_charge_observee_est_non_limitant():
    """`§1` — aucune preuve ne doit écarter ce candidat."""
    from app.services.recovery_contract import RecoveryBand
    from app.services.zone_recovery import NON_LIMITANT, _DECISION_PAR_BANDE

    assert _DECISION_PAR_BANDE[RecoveryBand.UNKNOWN.value] == NON_LIMITANT
    assert _DECISION_PAR_BANDE[RecoveryBand.LIKELY_AVAILABLE.value] == NON_LIMITANT


def test_sans_charge_observee_n_est_pas_une_preuve():
    """`§1`–`§2` — même rang, preuve différente.

    C'est toute la tranche en deux assertions : le classement les traite
    pareil, et l'explication ne le peut pas.
    """
    from app.services.recovery_contract import (
        Confidence, RecoveryBand, ZoneRecoveryEstimate,
    )
    from app.services.zone_recovery import (
        decision_de_recuperation, preuve_positive_de_recuperation,
    )

    inconnue = ZoneRecoveryEstimate(
        zone_code="pecs", estimate=None, band=RecoveryBand.UNKNOWN,
        confidence=Confidence.NONE, basis=("rien",))
    connue = ZoneRecoveryEstimate(
        zone_code="pecs", estimate=1.0, band=RecoveryBand.LIKELY_AVAILABLE,
        confidence=Confidence.HIGH, basis=("72 h",))

    assert decision_de_recuperation(inconnue) == decision_de_recuperation(connue)
    assert preuve_positive_de_recuperation(inconnue) is False
    assert preuve_positive_de_recuperation(connue) is True


def test_la_fatigue_connue_reste_limitante():
    """Une migration qui cesserait de limiter serait pire que le défaut."""
    from app.services.recovery_contract import (
        Confidence, RecoveryBand, ZoneRecoveryEstimate,
    )
    from app.services.zone_recovery import LIMITANT, decision_de_recuperation

    fatiguee = ZoneRecoveryEstimate(
        zone_code="quads", estimate=0.1, band=RecoveryBand.LIKELY_FATIGUED,
        confidence=Confidence.HIGH, basis=("8 h",))
    assert decision_de_recuperation(fatiguee) == LIMITANT


def test_aucun_score_pondere_ne_traverse_l_adaptateur():
    """`§1` — catégoriel, jamais un nombre.

    Traduire la bande en flottant pour réutiliser l'ancienne clé aurait
    reconduit le mensonge d'origine sous une couche de respectabilité.
    """
    from app.services.zone_recovery import _DECISION_PAR_BANDE

    for valeur in _DECISION_PAR_BANDE.values():
        assert isinstance(valeur, str)
        assert not isinstance(valeur, bool)


# ═══════════════════════════════════════════════════════════════════════
#  LE CLASSEMENT SERVI LIT LE CANONIQUE
# ═══════════════════════════════════════════════════════════════════════


def test_le_classement_ne_lit_plus_le_ratio_herite():
    """`§4` — le calcul dupliqué quitte le chemin SERVI.

    `availability_by_zone` survit pour `V2`, qui reste servi comme banc de
    comparaison. Ce qui doit disparaître, c'est sa lecture par la politique
    SERVIE.
    """
    import ast
    import inspect
    import pathlib

    from app.services import recommendation_v3 as v3

    # ⚠ LA DOCSTRING N'EST PAS DU CODE. Elle EXPLIQUE quel champ a été
    # abandonné, donc elle le nomme. Scanner le texte brut accuserait la
    # prose qui acte la migration — c'est la cinquième fois que ce dépôt
    # paie cette confusion. On lit l'AST, pas les caractères.
    arbre = ast.parse(inspect.getsource(v3._bande_de_recuperation).lstrip())
    lus = {n.attr for n in ast.walk(arbre) if isinstance(n, ast.Attribute)}
    assert "decision" in lus, "la bande ne lit pas la décision canonique"
    assert "availability_by_zone" not in lus, (
        "la politique servie lit encore le ratio hérité"
    )

    # ⚠ ET `recommendation.py` N'EST PAS TOUCHÉ. C'est la garde de gel qui
    # a imposé cette forme : la première écriture y avait ajouté deux
    # champs et un import du contrat canonique. Ce module-ci migre ; le
    # socle de signaux, partagé avec `V2`, ne bouge pas.
    import app.services.recommendation as socle

    source_socle = pathlib.Path(socle.__file__).read_text(encoding="utf-8")
    assert "zone_recovery" not in source_socle


def test_une_carte_absente_ne_vaut_pas_une_autorisation():
    """Repli : panne de la chaîne d'évidence ⇒ neutre, jamais `RECUPEREE`.

    Une indisponibilité technique ne doit pas se lire comme un feu vert.
    """
    from app.services.recommendation_v3 import (
        PARTIELLE, _bande_de_recuperation,
    )

    from app.services.recommendation_v3 import RecuperationCanonique

    assert _bande_de_recuperation(
        ("pecs",), RecuperationCanonique()) == PARTIELLE


def test_une_seule_zone_limitante_suffit():
    """Le PIRE sur les zones, pas la moyenne.

    Une moyenne laisserait une zone à plat se faire compenser par une zone
    fraîche — et le gabarit passerait.
    """
    from app.services.recommendation_v3 import (
        INSUFFISANTE, _bande_de_recuperation,
    )
    from app.services.zone_recovery import LIMITANT, NON_LIMITANT

    from app.services.recommendation_v3 import RecuperationCanonique

    recup = RecuperationCanonique(
        decision={"pecs": NON_LIMITANT, "quads": LIMITANT})
    assert _bande_de_recuperation(("pecs", "quads"), recup) == INSUFFISANTE


# ═══════════════════════════════════════════════════════════════════════
#  §6 — LES DEUX MUTATIONS EXIGÉES
# ═══════════════════════════════════════════════════════════════════════


def test_sans_charge_observee_ne_dit_jamais_zones_recuperees():
    """`§2` · MUTATION 1 — la phrase exige une PREUVE, pas un rang.

    Si `NO_OBSERVED_LOAD` produisait « zones récupérées », cette garde doit
    rougir. C'est le cas d'un utilisateur neuf : aucune zone n'a jamais été
    chargée, toutes sont non limitantes, et le produit ne sait rien.
    """
    from app.services.recommendation_v3 import (
        FACTEUR_RECUPERATION, RECUPEREE, expliquer,
    )

    class _T:
        slug, name, display_order = "push-a", "Push A", 1

    class _V:
        template = _T()
        slug = "push-a"
        zones = ("pecs",)
        rang = (RECUPEREE, 0, 0, 1, None, None, 1, "push-a")
        facteurs = {
            "recuperation": RECUPEREE,
            "preuve_recuperation": False,      # ← sans charge observée
            "deficit_couverture": 0.0,
            "repetition": 0,
            "repetition_justifiee": False,
            "modalite_delaissee": False,
            "dernier_passage": None,
            "observation_partielle": False,
        }

    explication = expliquer(_V())
    tout = " ".join(explication.get("facteurs_gagnants", ()))
    assert FACTEUR_RECUPERATION not in tout, (
        "« zones récupérées » affirmé sans aucune preuve de récupération"
    )
    for interdit in ("récupér", "fraîch", "prêt"):
        assert interdit not in tout.lower(), (
            f"langage de récupération sans preuve : {tout!r}"
        )


def test_une_preuve_reelle_autorise_la_phrase():
    """Le versant complémentaire : sans lui, la garde ci-dessus serait
    satisfaite par une explication qui ne parle JAMAIS de récupération."""
    from app.services.recommendation_v3 import (
        FACTEUR_RECUPERATION, RECUPEREE, expliquer,
    )

    class _T:
        slug, name, display_order = "push-a", "Push A", 1

    class _V:
        template = _T()
        slug = "push-a"
        zones = ("pecs",)
        rang = (RECUPEREE, 0, 0, 1, None, None, 1, "push-a")
        facteurs = {
            "recuperation": RECUPEREE,
            "preuve_recuperation": True,       # ← zone connue disponible
            "deficit_couverture": 0.0,
            "repetition": 0,
            "repetition_justifiee": False,
            "modalite_delaissee": False,
            "dernier_passage": None,
            "observation_partielle": False,
        }

    tout = " ".join(expliquer(_V()).get("facteurs_gagnants", ()))
    assert FACTEUR_RECUPERATION in tout


def test_l_inconnu_ne_devient_pas_limitant():
    """`§6` · MUTATION 2 — l'absence d'observation n'écarte personne.

    Le symétrique du défaut d'origine : corriger « inconnu = récupéré » en
    « inconnu = fatigué » remplacerait une invention par une autre, et
    changerait 9 gagnants sur 10.
    """
    from app.services.recommendation_v3 import (
        RECUPEREE, _bande_de_recuperation,
    )
    from app.services.zone_recovery import NON_LIMITANT

    from app.services.recommendation_v3 import RecuperationCanonique

    recup = RecuperationCanonique(decision={"pecs": NON_LIMITANT},
                                  preuve={"pecs": False})
    assert _bande_de_recuperation(("pecs",), recup) == RECUPEREE, (
        "une zone sans charge observée est devenue limitante"
    )


# ═══════════════════════════════════════════════════════════════════════
#  BOUT EN BOUT
# ═══════════════════════════════════════════════════════════════════════


def _seance(db, user_id, slug, jours):
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    from app.models.catalog import WorkoutTemplate
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    t = db.execute(select(WorkoutTemplate).options(
        selectinload(WorkoutTemplate.exercises)).where(
        WorkoutTemplate.slug == slug)).scalar_one()
    quand = datetime.now(UTC) - timedelta(days=jours)
    s = WorkoutSession(
        user_id=user_id, template_id=t.id,
        template_slug_snapshot=t.slug, template_name_snapshot=t.name,
        started_at=quand, ended_at=quand, status="completed",
        excluded_from_stats=False)
    for te in t.exercises:
        se = SessionExercise(
            exercise_code_snapshot=te.code or f"E{te.position}",
            exercise_name_snapshot=te.name, position=te.position)
        for k in range(3):
            se.set_logs.append(SetLog(
                kind="work", set_index=k + 1, weight_kg=60.0, reps=8,
                completed=True, completed_at=quand))
        s.session_exercises.append(se)
    db.add(s)
    db.commit()


def test_un_utilisateur_neuf_ne_s_entend_pas_dire_qu_il_est_recupere(client):
    """Le défaut d'origine, dans sa forme la plus visible.

    Aucune séance, donc aucune zone chargée. L'ancien modèle rendait `1.0`
    partout et l'explication pouvait annoncer « zones récupérées » à
    quelqu'un dont le produit ne sait rigoureusement rien.
    """
    from app.database import SessionLocal
    from app.models.user import User
    from app.services import advice_memory
    from app.services.recommendation_v3 import FACTEUR_RECUPERATION

    with SessionLocal() as db:
        u = db.query(User).first()
        uid = u.id

    with SessionLocal() as db:
        reco = advice_memory.recommander(
            db, uid, now=datetime.now(UTC),
            politique=advice_memory.POLITIQUE_SERVIE,
            avec_memoire=advice_memory.MEMOIRE_SERVIE)

    assert reco and reco.get("top")
    facteurs = " ".join(reco["top"].get("facteurs") or [])
    assert FACTEUR_RECUPERATION not in facteurs


def test_la_carte_canonique_est_bien_peuplee(client):
    """Une garde verte parce que la carte est VIDE ne garderait rien.

    Sans ceci, un `Signals` qui ne recevrait jamais sa carte laisserait
    toutes les gardes ci-dessus passer sur le repli neutre.
    """
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.recommendation_v3 import recuperation_canonique

    with SessionLocal() as db:
        uid = db.query(User).first().id
        _seance(db, uid, "push-a", 1)
        recup = recuperation_canonique(db, uid, datetime.now(UTC))

    assert recup.decision, "la carte de décision est vide"
    assert recup.preuve, "la carte de preuve est vide"
    assert set(recup.decision) == set(recup.preuve)
