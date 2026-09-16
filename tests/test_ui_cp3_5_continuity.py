"""`UI-CP3.5` — le noyau pur de la continuité.

POURQUOI CES GARDES EXISTENT
----------------------------
MISSION était **sans mémoire**. La cible n'est pas d'afficher une phrase qui
ressemble à un souvenir : c'est qu'une décision PRISE à un moment **change
réellement** la projection du plan, et que la répéter rende exactement la même
chose.

Ces gardes tiennent le noyau **PUR** — celui qui ne demande ni base, ni
horloge, ni requête. Les preuves qui exigent une écriture (A, B, C, F, G du
contrat de tranche) viendront avec la persistance ; celles-ci sont D et E, plus
les invariants qui empêchent une adaptation de mentir.
"""
from __future__ import annotations

from app.services.plan_adaptation import (
    REASON_DEFERRED,
    Adaptation,
    ZoneDeferral,
    applicable,
    apply_to_budget,
    build_effective_plan,
    deferrals_for,
)
from app.services.session_completion import (
    MATERIALLY_INCOMPLETE_BELOW,
    SessionCompletion,
    completion_of,
)


class _SL:
    def __init__(self, kind, completed):
        self.kind, self.completed = kind, completed


class _SE:
    def __init__(self, sets):
        self.set_logs = sets


class _Session:
    def __init__(self, exercices):
        self.session_exercises = exercices


def _seance(travail_fait: int, travail_total: int, echauffements: int = 0):
    sets = [_SL("warmup", False) for _ in range(echauffements)]
    sets += [_SL("work", i < travail_fait) for i in range(travail_total)]
    return _Session([_SE(sets)])


# ══════════════════════════════════════════════════════════════════════
#  Le déclencheur — `INCOMPLETE_SESSION`
# ══════════════════════════════════════════════════════════════════════


def test_le_seuil_est_celui_qu_a_tranche_l_operateur():
    """Moins de 50 %. La constante est nommée, et la garde la lit.

    Épingler `0.50` en dur dans le test aurait fait de la garde une seconde
    source de vérité : deux seuils qui divergent au premier ajustement.
    """
    assert MATERIALLY_INCOMPLETE_BELOW == 0.50


def test_une_seance_sous_le_seuil_est_materiellement_incomplete():
    assert completion_of(_seance(4, 11)).is_materially_incomplete


def test_une_seance_au_dessus_du_seuil_ne_l_est_pas():
    """Mesuré sur le labo : une séance à 67 % ne doit RIEN déclencher.

    Sans cette garde, un seuil mal placé ferait de presque toute séance une
    divergence — et un bloc de continuité permanent est exactement ce que le
    §11 interdit.
    """
    assert not completion_of(_seance(14, 21)).is_materially_incomplete


def test_exactement_au_seuil_ne_declenche_pas():
    """`<` et non `<=`. La moitié faite est faite à moitié, pas moins."""
    assert not completion_of(_seance(5, 10)).is_materially_incomplete


def test_une_seance_sans_travail_prescrit_ne_declenche_jamais():
    """⚠ LA GARDE QUI EMPÊCHE D'ACCUSER UN CARDIO.

    Un ratio de `0.0` ferait d'une séance cardio la plus incomplète de toutes.
    `ratio` rend `None` : une donnée manquante n'est jamais promue en zéro —
    c'est la règle n° 1 du contrat de récupération, appliquée ici.
    """
    cardio = completion_of(_seance(0, 0))
    assert cardio.ratio is None
    assert not cardio.is_materially_incomplete


def test_l_echauffement_ne_compte_pas_dans_la_completion():
    """Depuis `UI-CP2.1` l'échauffement n'est plus une porte ; il ne doit pas
    non plus gonfler un compte que l'utilisateur lit comme du travail."""
    avec = completion_of(_seance(4, 11, echauffements=6))
    sans = completion_of(_seance(4, 11))
    assert avec == sans
    assert avec.total == 11


# ══════════════════════════════════════════════════════════════════════
#  La conséquence — un REPORT, jamais une augmentation
# ══════════════════════════════════════════════════════════════════════


def test_une_zone_servie_au_dela_de_sa_cible_ne_produit_rien():
    """Il n'y a rien à reporter — et surtout rien à augmenter."""
    assert deferrals_for({"pecs": 14}, {"pecs": 12}) == ()


def test_une_zone_non_attribuee_n_est_pas_un_zero():
    """⚠ L'ABSENCE N'EST PAS UNE ABSENCE DE TRAVAIL.

    Les exercices que le résolveur ne sait pas classer sont OMIS du compte par
    zone. Les traiter comme des zéros reporterait du travail au motif qu'on
    n'a pas su le classer — une conclusion tirée d'une ignorance.

    ⚠ PREMIÈRE ÉCRITURE VIDE, ATTRAPÉE PAR MUTATION.
    Elle passait `{}` en livré : la boucle itère sur le livré, donc le corps ne
    s'exécutait jamais et la garde ne pouvait rien observer. Elle rendait vert
    quelle que soit l'implémentation.

    Le défaut réel à empêcher est de **parcourir le PLANIFIÉ** en traitant
    l'absence comme un zéro. La garde exerce donc une zone livrée ET une zone
    seulement planifiée, dans le même appel : si l'implémentation bascule de
    côté, la seconde produit un report et la garde tombe.
    """
    reports = deferrals_for({"pecs": 4}, {"pecs": 12, "lats": 10})
    zones = [d.zone_code for d in reports]
    assert zones == ["pecs"], (
        f"`lats` n'a jamais été livrée — son absence n'est pas un zéro : {zones}"
    )


def test_le_report_ne_descend_jamais_sous_ce_qui_a_ete_fait():
    (d,) = deferrals_for({"pecs": 4}, {"pecs": 12})
    assert d.sets_before == 12
    assert d.sets_after == 4
    assert d.sets_deferred == 8


def test_un_report_n_est_jamais_une_augmentation():
    """L'invariant du moteur, tenu au niveau du type."""
    assert ZoneDeferral("pecs", 12, 20).sets_deferred == 0


def test_une_adaptation_sans_consequence_n_est_pas_materielle():
    """Sans cette garde, une décision à report nul afficherait un bloc de
    continuité qui n'annonce aucun changement — du bruit qui ressemble à de la
    mémoire."""
    vide = Adaptation("d", None, "fp", (ZoneDeferral("pecs", 12, 12),), 4, 11)
    pleine = Adaptation("d", None, "fp", (ZoneDeferral("pecs", 12, 4),), 4, 11)
    assert not vide.is_material
    assert pleine.is_material


# ══════════════════════════════════════════════════════════════════════
#  SUPERSESSION — dérivée, jamais marquée
# ══════════════════════════════════════════════════════════════════════


def test_une_adaptation_ne_vaut_que_pour_son_contexte_de_plan():
    a = Adaptation("d", None, "empreinte-A", (), 4, 11)
    assert applicable(a, "empreinte-A")
    assert not applicable(a, "empreinte-B")


def test_un_changement_de_contexte_perime_l_adaptation(monkeypatch):
    """⚠ PREUVE G — une décision prise contre un autre plan n'agit plus.

    On change la cadence : le plan de base change, donc son empreinte, donc
    l'ancienne décision cesse de s'appliquer. L'historique survit — la ligne
    n'est pas touchée — mais le comportement, non.
    """
    from app.services.training_preferences import TrainingPreferencesData

    prefs3 = TrainingPreferencesData(sessions_per_week=3)
    prefs4 = TrainingPreferencesData(sessions_per_week=4)

    base3, _ = build_effective_plan(prefs3, ())
    perimee = Adaptation(
        "d", None, base3.fingerprint,
        (ZoneDeferral("pecs", 12, 4),), 4, 11)

    base4, eff4 = build_effective_plan(prefs4, (perimee,))
    assert base4.fingerprint != base3.fingerprint, (
        "le labo ne discrimine rien : les deux cadences rendent le même plan"
    )
    assert eff4.fingerprint == base4.fingerprint, (
        "une adaptation périmée agit encore sur le plan effectif"
    )


# ══════════════════════════════════════════════════════════════════════
#  PREUVE D — le plan effectif reflète vraiment le delta
# ══════════════════════════════════════════════════════════════════════


def _prefs():
    from app.services.training_preferences import TrainingPreferencesData

    return TrainingPreferencesData(sessions_per_week=4)


def _couverture(plan):
    return {c.zone_code: c.planned_sets for c in plan.zone_coverage}


def test_sans_adaptation_le_plan_effectif_EST_le_plan_de_base():
    base, eff = build_effective_plan(_prefs(), ())
    assert eff.fingerprint == base.fingerprint


def test_le_plan_effectif_differe_du_plan_de_base():
    """⚠ SANS CETTE GARDE, « adopté » SERAIT UN MENSONGE.

    C'est la preuve que le §5 de l'arbitrage exige : une adaptation qui
    n'affecte pas la projection ne peut être annoncée que comme « proposée ».
    """
    prefs = _prefs()
    base, _ = build_effective_plan(prefs, ())
    cible = _couverture(base)
    zone, prevu = max(
        ((z, n) for z, n in cible.items() if n), key=lambda kv: kv[1])

    a = Adaptation("d", None, base.fingerprint,
                   (ZoneDeferral(zone, prevu, prevu // 3),), 4, 11)
    base2, eff = build_effective_plan(prefs, (a,))

    assert base2.fingerprint == base.fingerprint
    assert eff.fingerprint != base.fingerprint
    assert _couverture(eff)[zone] < cible[zone]


def test_aucune_zone_servie_ne_tombe_a_zero():
    """⚠ LE DÉFAUT QUE L'ALLOCATEUR EXISTE POUR EMPÊCHER.

    Une première version de la transformation plafonnait chaque zone à ce que
    le plan de base lui donnait. Mesuré : **biceps 4 → 0** — « un utilisateur
    déclarant Bras recevait un programme sans le moindre curl », le défaut
    nommé dans `_rank_zone`.

    Cause : le plan de base n'atteint jamais la bande basse du budget, donc
    plafonner une BANDE par une COUVERTURE inverse la bande. Cette garde
    empêche la reconstruction de cette erreur.
    """
    prefs = _prefs()
    base, _ = build_effective_plan(prefs, ())
    cible = _couverture(base)
    zone, prevu = max(
        ((z, n) for z, n in cible.items() if n), key=lambda kv: kv[1])

    a = Adaptation("d", None, base.fingerprint,
                   (ZoneDeferral(zone, prevu, 2),), 2, 11)
    _, eff = build_effective_plan(prefs, (a,))
    eff_cov = _couverture(eff)

    orphelines = [z for z, n in cible.items() if n > 0 and eff_cov.get(z, 0) == 0]
    assert orphelines == [], (
        f"ces zones servies tombent à zéro : {orphelines}"
    )


def test_rejouer_rend_exactement_le_meme_plan():
    """⚠ PREUVE E, VERSANT PUR — la décision ne bouge pas, donc le plan non
    plus.

    C'est ce qui permettra à MISSION de citer la même date et le même delta à
    chaque rendu **sans rien mémoriser d'autre que la décision** : la
    projection est déterministe.
    """
    prefs = _prefs()
    base, _ = build_effective_plan(prefs, ())
    a = Adaptation("d", None, base.fingerprint,
                   (ZoneDeferral("pecs", 12, 4),), 4, 11)
    _, eff1 = build_effective_plan(prefs, (a,))
    _, eff2 = build_effective_plan(prefs, (a,))
    assert eff1.fingerprint == eff2.fingerprint


# ══════════════════════════════════════════════════════════════════════
#  La transformation de budget, en isolation
# ══════════════════════════════════════════════════════════════════════


def _budget():
    from app.services.weekly_volume_budget import build_weekly_volume_budget

    return build_weekly_volume_budget(_prefs())


def test_la_transformation_ne_remonte_jamais_une_borne():
    """⚠ PREMIÈRE ÉCRITURE VIDE, ATTRAPÉE PAR MUTATION.

    Elle employait `ZoneDeferral("pecs", 12, 999)` : le report vaut alors
    `max(0, 12 - 999) == 0`, la zone est ignorée avant d'atteindre la
    transformation, et la garde observait un budget inchangé. Verte pour une
    raison qui n'était pas la sienne.

    Il faut un report POSITIF dont la cible dépasse quand même la bande —
    c'est le seul montage qui exerce le `min`.
    """
    b = _budget()
    a = Adaptation("d", None, "fp",
                   (ZoneDeferral("pecs", 999, 50),), 4, 11)
    assert a.deferrals[0].sets_deferred > 0, "le montage n'exerce rien"
    eff = apply_to_budget(b, (a,))
    avant = {z.zone_code: z for z in b.zones}
    for z in eff.zones:
        a0 = avant[z.zone_code]
        assert z.planning_low_sets <= a0.planning_low_sets
        assert z.baseline_sets <= a0.baseline_sets
        assert z.planning_high_sets <= a0.planning_high_sets


def test_deux_adaptations_sur_une_zone_retiennent_la_plus_conservatrice():
    b = _budget()
    a1 = Adaptation("d1", None, "fp", (ZoneDeferral("pecs", 12, 8),), 8, 12)
    a2 = Adaptation("d2", None, "fp", (ZoneDeferral("pecs", 12, 3),), 3, 12)
    eff = apply_to_budget(b, (a1, a2))
    pecs = next(z for z in eff.zones if z.zone_code == "pecs")
    assert pecs.planning_high_sets == 3


def test_la_zone_reportee_dit_pourquoi():
    """Une borne qui bouge sans raison est exactement ce que le dépôt reproche
    aux readouts muets. Le type prévoyait déjà `basis`."""
    b = _budget()
    a = Adaptation("d", None, "fp", (ZoneDeferral("pecs", 12, 4),), 4, 11)
    eff = apply_to_budget(b, (a,))
    pecs = next(z for z in eff.zones if z.zone_code == "pecs")
    autre = next(z for z in eff.zones if z.zone_code == "core")
    assert REASON_DEFERRED in pecs.basis
    assert REASON_DEFERRED not in autre.basis


def test_la_transformation_est_pure():
    """Mêmes entrées, même sortie — et l'entrée n'est pas mutée."""
    b = _budget()
    avant = tuple((z.zone_code, z.planning_high_sets) for z in b.zones)
    a = Adaptation("d", None, "fp", (ZoneDeferral("pecs", 12, 4),), 4, 11)
    r1 = apply_to_budget(b, (a,))
    r2 = apply_to_budget(b, (a,))
    apres = tuple((z.zone_code, z.planning_high_sets) for z in b.zones)
    assert avant == apres, "le budget d'entrée a été muté"
    assert [z.planning_high_sets for z in r1.zones] == [
        z.planning_high_sets for z in r2.zones]


def test_une_completion_est_un_couple_de_comptes_pas_un_score():
    """Aucun pourcentage rendu, aucune note. `SessionCompletion` ne porte que
    `done` et `total` — la précision ne doit pas dépasser le modèle."""
    champs = set(SessionCompletion.__dataclass_fields__)
    assert champs == {"done", "total"}


# ══════════════════════════════════════════════════════════════════════
#  Les preuves d'ÉVÉNEMENT — elles exigent une base
# ══════════════════════════════════════════════════════════════════════


def _demarre(client, slug: str = "push-a") -> int:
    import re as _re

    r = client.post("/sessions", data={"template_slug": slug},
                    follow_redirects=False)
    assert r.status_code in (302, 303), r.status_code
    return int(_re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


def _cadence(uid: int, n: int = 4) -> None:
    from app.database import SessionLocal
    from app.services.training_preferences import save_training_preferences

    with SessionLocal() as db:
        save_training_preferences(db, uid, sessions_per_week=n)


def _remplit(session_id: int, proportion: float) -> None:
    """Coche une PART des séries de travail. Écrit directement — on prépare un
    état, on ne teste pas le formulaire ici."""
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog

    with SessionLocal() as db:
        travail = db.execute(
            select(SetLog)
            .join(SessionExercise,
                  SetLog.session_exercise_id == SessionExercise.id)
            .where(SessionExercise.session_id == session_id)
            .where(SetLog.kind == "work")
            .order_by(SetLog.id.asc())
        ).scalars().all()
        assert travail, "le montage ne discrimine rien : aucune série de travail"
        combien = int(len(travail) * proportion)
        for sl in travail[:combien]:
            sl.weight_kg, sl.reps, sl.completed = 60.0, 8, True
        db.commit()


def _traces(uid: int) -> list:
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.decision_trace import DecisionTrace
    from app.services.decision_analytics import REPLAN_DELTA

    with SessionLocal() as db:
        return list(db.execute(
            select(DecisionTrace)
            .where(DecisionTrace.user_id == uid)
            .where(DecisionTrace.decision_type == REPLAN_DELTA)
        ).scalars().all())


def test_preuve_A_une_cloture_qualifiante_cree_UNE_decision(client):
    """Une seule, et seulement quand la séance le justifie."""
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    _cadence(uid)
    sid = _demarre(client)
    _remplit(sid, 0.3)
    client.post(f"/sessions/{sid}", data={"action": "end"},
                follow_redirects=False)

    assert len(_traces(uid)) == 1, "zéro ou plusieurs décisions pour une clôture"


def test_preuve_A_bis_une_seance_assez_complete_ne_cree_RIEN(client):
    """⚠ LA MOITIÉ QUI EMPÊCHE LA PRÉCÉDENTE D'ÊTRE VIDE.

    Sans elle, un déclencheur qui se déclenche TOUJOURS passerait la preuve A.
    Le silence est la moitié du contrat.
    """
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    _cadence(uid)
    sid = _demarre(client)
    _remplit(sid, 0.9)
    client.post(f"/sessions/{sid}", data={"action": "end"},
                follow_redirects=False)

    assert _traces(uid) == []


def test_preuve_B_des_GET_repetes_n_ecrivent_RIEN(client):
    """⚠ LA PREUVE QUI SÉPARE UNE MÉMOIRE D'UNE RECOMPUTATION.

    On compte les lignes avant et après plusieurs affichages de l'accueil. Une
    continuité qui s'écrirait au rendu produirait une ligne par visite — et
    citerait une date différente à chaque fois.
    """
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    _cadence(uid)
    sid = _demarre(client)
    _remplit(sid, 0.3)
    client.post(f"/sessions/{sid}", data={"action": "end"},
                follow_redirects=False)

    avant = len(_traces(uid))
    assert avant == 1, "le montage ne discrimine rien"

    for _ in range(4):
        assert client.get("/").status_code == 200
        assert client.get("/progress").status_code == 200

    assert len(_traces(uid)) == avant, (
        "un affichage a écrit une décision — c'est une recomputation, pas une "
        "mémoire"
    )


def test_preuve_C_des_GET_repetes_exposent_la_meme_decision(client):
    """Même identité, même date, même delta. C'est cela, se souvenir."""
    from app.database import SessionLocal
    from app.services.plan_adaptation_store import active_adaptations
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    _cadence(uid)
    sid = _demarre(client)
    _remplit(sid, 0.3)
    client.post(f"/sessions/{sid}", data={"action": "end"},
                follow_redirects=False)

    lectures = []
    for _ in range(3):
        client.get("/")
        with SessionLocal() as db:
            (a,) = active_adaptations(db, uid)
            lectures.append((a.decision_id, a.decided_at,
                             tuple((d.zone_code, d.sets_after)
                                   for d in a.deferrals)))

    assert len(set(lectures)) == 1, f"la décision a bougé entre deux lectures : {lectures}"


def test_preuve_F_l_ecartement_retire_l_effet_et_garde_l_histoire(client):
    from app.database import SessionLocal
    from app.services.plan_adaptation_store import active_adaptations, dismiss
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    _cadence(uid)
    sid = _demarre(client)
    _remplit(sid, 0.3)
    client.post(f"/sessions/{sid}", data={"action": "end"},
                follow_redirects=False)

    with SessionLocal() as db:
        (a,) = active_adaptations(db, uid)
        assert dismiss(db, uid, a.decision_id)
        db.commit()

    with SessionLocal() as db:
        assert active_adaptations(db, uid) == (), "l'effet subsiste"

    assert len(_traces(uid)) == 1, (
        "la trace historique a été supprimée — on écarte un EFFET, pas une preuve"
    )


def test_ecarter_deux_fois_est_le_meme_fait(client):
    from app.database import SessionLocal
    from app.services.plan_adaptation_store import active_adaptations, dismiss
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    _cadence(uid)
    sid = _demarre(client)
    _remplit(sid, 0.3)
    client.post(f"/sessions/{sid}", data={"action": "end"},
                follow_redirects=False)

    with SessionLocal() as db:
        (a,) = active_adaptations(db, uid)
        assert dismiss(db, uid, a.decision_id) is True
        db.commit()
    with SessionLocal() as db:
        assert dismiss(db, uid, a.decision_id) is False
        db.commit()


def test_une_trace_d_adaptation_est_immuable(client):
    """⚠ PREUVE E — la décision ne peut pas être réécrite.

    L'écouteur `before_update` de `decision_traces` lève. Cette garde vérifie
    que la protection s'applique bien à NOS lignes, pas seulement en théorie.
    """
    import pytest
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.decision_trace import (
        DecisionTrace,
        DecisionTraceImmutableError,
    )
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    _cadence(uid)
    sid = _demarre(client)
    _remplit(sid, 0.3)
    client.post(f"/sessions/{sid}", data={"action": "end"},
                follow_redirects=False)

    with SessionLocal() as db:
        ligne = db.execute(select(DecisionTrace)).scalars().first()
        assert ligne is not None
        ligne.basis = "[]"
        with pytest.raises(DecisionTraceImmutableError):
            db.commit()


def test_une_seance_cardio_ne_declenche_jamais_a_la_cloture(client):
    """Bout en bout, pas seulement sur la vue-modèle."""
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    _cadence(uid)
    sid = _demarre(client)
    # Aucune série cochée, et on force zéro travail prescrit en les retirant.
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog

    with SessionLocal() as db:
        for sl in db.execute(
            select(SetLog)
            .join(SessionExercise,
                  SetLog.session_exercise_id == SessionExercise.id)
            .where(SessionExercise.session_id == sid)
        ).scalars().all():
            db.delete(sl)
        db.commit()

    client.post(f"/sessions/{sid}", data={"action": "end"},
                follow_redirects=False)
    assert _traces(uid) == []


def test_la_continuite_ne_coute_jamais_la_cloture(client, monkeypatch):
    """⚠ « LE BROUILLON PRIME SUR SA TRACE ».

    Une séance terminée est un fait de l'utilisateur ; la trace est un service
    que le produit se rend à lui-même. Si la seconde explose, la première doit
    rester — l'inverse serait une régression grave pour un enrichissement.
    """
    import app.routers.sessions as routeur
    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    _cadence(uid)
    sid = _demarre(client)
    _remplit(sid, 0.3)

    def explose(*a, **k):
        raise RuntimeError("panne simulée de la continuité")

    monkeypatch.setattr(
        "app.services.plan_adaptation_store.record_adaptation", explose)

    r = client.post(f"/sessions/{sid}", data={"action": "end"},
                    follow_redirects=False)
    assert r.status_code in (302, 303)

    with SessionLocal() as db:
        s = db.get(WorkoutSession, sid)
        assert s.status == "completed", "la clôture a été emportée par la trace"
        assert s.ended_at is not None
    assert routeur is not None


def test_une_seance_entierement_abandonnee_declenche_AUSSI(client):
    """⚠ TROUVÉ PAR LE RENDU, PAS PAR LES GARDES UNITAIRES.

    Une séance à 0 série sur 21 ne produisait AUCUN report, quand une séance à
    une seule série en produisait un. Cause : la répartition par zone omettait
    les zones à zéro, donc une séance entièrement abandonnée paraissait
    « aucune zone touchée ».

    Les deux absences ne sont pas la même : un exercice que le résolveur ne
    sait pas classer est une IGNORANCE ; un exercice classé qui a livré zéro
    est un FAIT.
    """
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    _cadence(uid)
    sid = _demarre(client)
    # Rien n'est coché : la séance est ouverte puis close, telle quelle.
    client.post(f"/sessions/{sid}", data={"action": "end"},
                follow_redirects=False)

    assert len(_traces(uid)) == 1, (
        "une séance entièrement abandonnée ne produit aucune adaptation"
    )


def test_un_exercice_non_classe_reste_omis(client):
    """L'autre moitié : la correction ci-dessus ne doit PAS transformer une
    ignorance en zéro."""
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from app.services.zone_exposure import work_sets_by_zone

    sid = _demarre(client)
    with SessionLocal() as db:
        s = db.execute(
            select(WorkoutSession).where(WorkoutSession.id == sid)
        ).scalars().first()
        for se in s.session_exercises:
            se.substituted_name = "Exercice totalement inconnu du résolveur"
        db.commit()
    with SessionLocal() as db:
        s = db.execute(
            select(WorkoutSession).where(WorkoutSession.id == sid)
        ).scalars().first()
        assert work_sets_by_zone(db, s) == {}, (
            "un exercice non classé a été compté pour zéro"
        )


# ══════════════════════════════════════════════════════════════════════
#  VOCABULAIRE — exigé par `Sx_RECOVERY_READINESS_01_SPEC §8.4`
# ══════════════════════════════════════════════════════════════════════

#: `§8.2` — formulations interdites, plus les deux mots que `UI-CP3.5 §10`
#: proscrit spécifiquement. Sans instance planifiée datée, « manqué » et « en
#: retard » affirment une faute que le modèle ne peut pas prouver.
_INTERDITS = (
    "physiologiquement récupéré",
    "récupération musculaire mesurée",
    "manqué",
    "manquée",
    "en retard",
    "raté",
    "ratée",
)


def test_la_continuite_n_emploie_aucun_mot_interdit(client):
    """⚠ `§8.4` EXIGE CE TEST, et il vit dans le code, pas dans un document.

    On lit le HTML RENDU, pas le gabarit : un libellé assemblé à deux endroits
    diverge, et c'est ce qui rendait une garde de source insuffisante.
    """
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    _cadence(uid)
    sid = _demarre(client)
    client.post(f"/sessions/{sid}", data={"action": "end"},
                follow_redirects=False)

    page = client.get("/").text
    assert "mission-change" in page, (
        "le bloc de continuité ne se rend pas — la garde tournerait à vide"
    )

    bas = page.lower()
    fautifs = [m for m in _INTERDITS if m in bas]
    assert fautifs == [], (
        f"vocabulaire interdit rendu par MISSION : {fautifs}. Sans instance "
        "planifiée datée, ces mots imputent une faute que le modèle ne peut "
        "pas prouver."
    )


def test_la_continuite_dit_des_comptes_et_une_date(client):
    """L'autre moitié : proscrire des mots ne suffit pas si la surface ne dit
    plus rien. Elle doit porter les comptes ET la date de la décision."""
    import re as _re

    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    _cadence(uid)
    sid = _demarre(client)
    client.post(f"/sessions/{sid}", data={"action": "end"},
                follow_redirects=False)

    page = client.get("/").text
    bloc = _re.search(r'<section class="mission-change".*?</section>',
                      page, _re.DOTALL)
    assert bloc, "bloc de continuité introuvable"
    txt = bloc.group(0)
    assert _re.search(r"Ajusté\s+\w+\s+\d{2}/\d{2}", txt), (
        "la décision ne cite pas sa date — sans elle, rien ne distingue une "
        "mémoire d'un recalcul"
    )
    assert _re.search(r"<b>\d+ → \d+</b>", txt), "aucun compte de séries rendu"
    assert "reportées" in txt, (
        "le mot qui empêche de lire une SUPPRESSION a disparu"
    )


def test_aucune_liste_de_zones_sur_mission(client):
    """⚠ `§11` — MISSION n'est pas un flux d'historique.

    Mesuré au rendu : sur une séance abandonnée, détailler chaque zone
    produisait QUATRE lignes de report. On montre la plus matérielle, on compte
    les autres, et on dit le total — rien n'est caché, seule l'énumération
    disparaît.
    """
    import re as _re

    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    _cadence(uid)
    sid = _demarre(client)
    client.post(f"/sessions/{sid}", data={"action": "end"},
                follow_redirects=False)

    page = client.get("/").text
    bloc = _re.search(r'<section class="mission-change".*?</section>',
                      page, _re.DOTALL)
    assert bloc, "bloc de continuité introuvable"
    lignes = len(_re.findall(r'class="mission-change__delta"', bloc.group(0)))
    assert lignes == 1, (
        f"{lignes} lignes de report : MISSION redevient un flux"
    )
