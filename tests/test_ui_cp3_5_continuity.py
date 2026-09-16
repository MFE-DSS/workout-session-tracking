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
