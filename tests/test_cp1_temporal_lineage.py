"""CP-1 — le signal historique porte sa lignée temporelle et causale.

**`BEHAVIOUR CHANGE = NONE`.** Aucune prescription ne bouge. Ces gardes le
prouvent mécaniquement plutôt que de l'affirmer.

⚠ CE QUE `CP-1` CORRIGE, MESURÉ AVANT DE L'ÉCRIRE.

Deux historiques dont la **seule** différence est l'existence de séances
substituées produisaient une charge utile **identique champ par champ** :

    A — l'utilisateur s'est entraîné, 2 substituts, le dernier il y a 7 j
    B — l'utilisateur ne s'est pas entraîné depuis 100 jours

    {"relative": "il y a 3 mois", "started_at": "2026-05-29T12:00:00",
     "weights_str": "100", "session_id": 26, ...}          ← LES DEUX

Cause : au retour sur un mouvement prescrit, la politique de substitution saute
les occurrences substituées (`stats.py:157-168`) et remonte jusqu'au dernier
prescrit — mesuré à **93 jours plus vieux** que le dernier entraînement réel.

**L'âge seul est donc insuffisant.** Un repère « il y a 3 mois » peut signifier
un désentraînement réel ou une continuité parfaite par substitution.

⚠ AUCUN SEUIL N'EST INTRODUIT ICI. `performed_at` est un fait ; décider qu'un
âge doit changer une prescription est une hypothèse de domaine, sans preuve
dans ce dépôt. C'est `CP-3`, pas `CP-1`.
"""
from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta

import pytest

from tests.helpers import get_test_user_id

CODE = "E1"
GABARIT = "cp1-lineage"
SUB = "Machine X"
T0 = datetime(2026, 9, 6, 12, 0, tzinfo=UTC)


# ───────────────────────── outillage de scénario ─────────────────────────


def _poser(db, uid, *, jours, sub, kg, statut="completed"):
    """Une séance du gabarit d'essai, à `jours` dans le passé."""
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    s = WorkoutSession(
        user_id=uid, status=statut,
        started_at=T0 - timedelta(days=jours),
        template_slug_snapshot=GABARIT,
        template_name_snapshot="Lignée CP-1",
        excluded_from_stats=False,
    )
    db.add(s)
    db.flush()
    se = SessionExercise(
        session_id=s.id, exercise_code_snapshot=CODE,
        exercise_name_snapshot="Développé", position=1,
        substituted_name=sub,
    )
    db.add(se)
    db.flush()
    if kg is not None:
        db.add(SetLog(session_exercise_id=se.id, kind="work", set_index=1,
                      weight_kg=kg, reps=10, completed=True))
    db.commit()
    return s


def _repere(histoire, sub_courant):
    """Le repère que `stats` retient pour une séance courante donnée."""
    from app.database import SessionLocal
    from app.services.stats import last_time_by_exercise_code

    with SessionLocal() as db:
        uid = get_test_user_id()
        for jours, sub, kg in histoire:
            _poser(db, uid, jours=jours, sub=sub, kg=kg)
        cur = _poser(db, uid, jours=0, sub=sub_courant, kg=None,
                     statut="in_progress")
        db.refresh(cur)
        return last_time_by_exercise_code(db, cur, T0).get(CODE)


# ───────── 1. Les trois histoires — §5 de la directive opérateur ─────────


def test_cas_A_prescrit_puis_prescrit(client):
    """Continuité simple : le repère est la dernière séance, et il est frais."""
    p = _repere([(21, None, 95.0), (7, None, 100.0)], None)
    assert p is not None
    assert p["weights_str"] == "100"
    assert (T0 - p["started_at"].replace(tzinfo=UTC)).days == 7


def test_cas_B_prescrit_puis_substitut_ne_rend_aucun_repere(client):
    """La séance courante est un substitut jamais pratiqué → silence.

    ⚠ Le silence n'est PAS neutre à l'écran : `exercise_card.html:396` rend
    « Première fois » quand il n'y a pas de repère. L'utilisateur a pourtant
    fait ce mouvement **prescrit** il y a sept jours. `CP-1` ne corrige pas
    cette phrase — c'est une décision de politique de sélection, hors
    périmètre — mais la garde fige le comportement pour qu'il ne change pas
    par accident.
    """
    p = _repere([(21, None, 95.0), (7, None, 100.0)], SUB)
    assert p is None


def test_cas_C_retour_au_prescrit_saute_les_substituts(client):
    """LE CAS QUI MOTIVE `CP-1`.

    L'utilisateur s'est entraîné il y a 7 jours (via substitut) et reçoit un
    repère vieux de 100 jours. L'écart mesuré est de **93 jours**.
    """
    p = _repere([(100, None, 100.0), (14, SUB, 80.0), (7, SUB, 82.0)], None)
    assert p is not None
    age_repere = (T0 - p["started_at"].replace(tzinfo=UTC)).days
    dernier_entrainement_reel = 7
    assert age_repere == 100
    assert age_repere - dernier_entrainement_reel == 93, (
        "l'écart entre le repère et le dernier entraînement réel a changé — "
        "la politique de sélection a bougé, ce que CP-1 ne fait PAS"
    )


# ───────── 2. La garde qui prouve que CP-1 sert à quelque chose ─────────


def test_le_signal_distingue_desormais_les_deux_histoires(client):
    """Deux historiques ne différant QUE par des substituts doivent produire
    des signaux DIFFÉRENTS. Cette garde échouait avant `CP-1`.

    Sans elle, `CP-1` ajouterait trois champs sans rien résoudre.
    """
    from app.services.overload_engine import HistoricalSetSignal

    # Le même repère prescrit, dans deux mondes distincts.
    entraine = HistoricalSetSignal(
        weight_kg=100.0, reps=10,
        performed_at=T0 - timedelta(days=100),
        source_session_id=26, substituted_name=None,
    )
    # Ce que le monde « entraîné via substitut » porte EN PLUS : la trace de
    # l'occurrence substituée récente, qui existe dans l'historique.
    substitut_recent = HistoricalSetSignal(
        weight_kg=82.0, reps=10,
        performed_at=T0 - timedelta(days=7),
        source_session_id=28, substituted_name=SUB,
    )

    assert entraine != substitut_recent
    assert substitut_recent.substituted_name == SUB
    assert entraine.substituted_name is None
    assert (substitut_recent.performed_at - entraine.performed_at).days == 93, (
        "les deux occurrences ne sont plus séparées de 93 jours — le scénario "
        "de référence a changé"
    )


def _signaux(histoire, sub_courant):
    """Les signaux historiques que la couche d'entrée produit RÉELLEMENT.

    ⚠ On vise `_history_signals_for_code` et non l'entrée publique
    `build_overload_input_for_exercise`, pour deux raisons de fond :

    * c'est **le point de peuplement** — la fonction que `CP-1` modifie ;
    * l'entrée publique exige un `template_exercise` avec ses `rep_targets`,
      et elle rend `None` dès que la séance courante est substituée (politique
      V1 conservatrice, `overload_inputs.py:326-330`). Elle ne pourrait donc
      pas exercer le cas substitué du tout.

    Une garde qui construirait le signal à la main prouverait que la dataclass
    accepte des champs, pas que la base les remplit.
    """
    from app.database import SessionLocal
    from app.services.overload_inputs import _history_signals_for_code

    with SessionLocal() as db:
        uid = get_test_user_id()
        posees = [_poser(db, uid, jours=j, sub=s, kg=k) for j, s, k in histoire]
        cur = _poser(db, uid, jours=0, sub=sub_courant, kg=None,
                     statut="in_progress")
        db.refresh(cur)
        sigs = _history_signals_for_code(
            db, uid, CODE, cur.id, GABARIT,
            current_is_substituted=sub_courant is not None,
            current_substituted_name=sub_courant,
        )
        return sigs, {s.id for s in posees}


def test_le_signal_transporte_les_trois_champs_depuis_la_base(client):
    """Bout en bout : la lignée vient de la BASE, pas d'un défaut."""
    sigs, ids = _signaux([(9, SUB, 77.5)], SUB)

    assert sigs, "prémisse invalide : aucun signal historique"
    sig = sigs[0]
    assert sig.performed_at is not None, "`performed_at` n'atteint pas le signal"
    assert sig.source_session_id in ids
    assert sig.substituted_name == SUB


def test_le_signal_dit_quand_le_repere_prescrit_est_ancien(client):
    """LE CAS `C`, vu depuis le moteur — la lignée le rend enfin lisible.

    Le signal retenu est le prescrit de 100 jours, et il porte désormais son
    `performed_at` **et** son `substituted_name is None`. Avant `CP-1`, rien
    dans le signal ne disait ni l'un ni l'autre.
    """
    sigs, _ = _signaux(
        [(100, None, 100.0), (14, SUB, 80.0), (7, SUB, 82.0)], None
    )
    assert sigs, "prémisse invalide : aucun signal"
    sig = sigs[0]
    assert sig.weight_kg == 100.0
    assert sig.substituted_name is None
    quand = sig.performed_at
    reference = T0 if quand.tzinfo else T0.replace(tzinfo=None)
    assert (reference - quand).days == 100, (
        "le signal ne porte plus l'âge réel du repère prescrit"
    )


# ───────── 3. Non-régression numérique — `BEHAVIOUR CHANGE = NONE` ─────────


@pytest.mark.parametrize("etat", ["progress", "consolidate", "top-range", "deload"])
def test_la_prescription_ne_depend_pas_de_la_lignee(etat):
    """LA GARDE QUI TIENT `BEHAVIOUR CHANGE = NONE`.

    Le même historique, une fois **nu** et une fois **portant la lignée**,
    doit produire des cibles numériques identiques. Si un jour le moteur se
    met à lire `performed_at`, cette garde rougit — et c'est exactement ce
    qu'on veut, parce que ce serait `CP-3` arrivé sans décision.
    """
    from app.services.overload_engine import (
        HistoricalSetSignal,
        OverloadInput,
        compute_overload_hint,
    )

    #: Des historiques qui déclenchent chacun un état différent.
    HISTOIRES = {
        "progress":    [(100.0, 12), (97.5, 12), (95.0, 11)],
        "consolidate": [(100.0, 10), (97.5, 10), (95.0, 10)],
        "top-range":   [(100.0, 6), (97.5, 10), (95.0, 10)],
        "deload":      [(100.0, 7), (100.0, 9), (100.0, 11)],
    }
    brut = HISTOIRES[etat]

    nu = tuple(HistoricalSetSignal(weight_kg=w, reps=r, quality_score=0.8)
               for w, r in brut)
    avec_lignee = tuple(
        HistoricalSetSignal(
            weight_kg=w, reps=r, quality_score=0.8,
            performed_at=T0 - timedelta(days=200 + i * 30),   # très vieux
            source_session_id=1000 + i,
            substituted_name=SUB if i % 2 else None,
        )
        for i, (w, r) in enumerate(brut)
    )

    def hint(history):
        return compute_overload_hint(OverloadInput(
            exercise_category="compound", target_min=8, target_max=12,
            history=history,
        ))

    a, b = hint(nu), hint(avec_lignee)
    assert a.state == b.state
    assert a.target_weight_kg == b.target_weight_kg
    assert a.target_reps_min == b.target_reps_min
    assert a.target_reps_max == b.target_reps_max
    assert a.reasons == b.reasons, (
        "même les RAISONS doivent être identiques — une lignée qui change un "
        "libellé serait un changement de comportement déguisé"
    )


def test_la_recommandation_designe_le_repere_dont_elle_derive():
    """`reference_signal` pointe l'occurrence dont `target_weight_kg` dérive."""
    from app.services.overload_engine import (
        HistoricalSetSignal,
        OverloadInput,
        compute_overload_hint,
    )

    dernier = HistoricalSetSignal(
        weight_kg=100.0, reps=10, quality_score=0.8,
        performed_at=T0 - timedelta(days=5), source_session_id=42,
    )
    h = compute_overload_hint(OverloadInput(
        exercise_category="compound", target_min=8, target_max=12,
        history=(dernier,
                 HistoricalSetSignal(weight_kg=97.5, reps=10, quality_score=0.8),
                 HistoricalSetSignal(weight_kg=95.0, reps=10, quality_score=0.8)),
    ))
    assert h.reference_signal is dernier
    assert h.reference_signal.source_session_id == 42


def test_l_etat_inconnu_ne_designe_aucun_repere():
    """`unknown` n'a par définition pas d'historique — il ne doit rien inventer."""
    from app.services.overload_engine import OverloadInput, compute_overload_hint

    h = compute_overload_hint(OverloadInput(
        exercise_category="compound", target_min=8, target_max=12, history=(),
    ))
    assert h.state == "unknown"
    assert h.reference_signal is None


# ───────── 4. Le piège du datetime naïf de SQLite ─────────


def test_performed_at_survit_au_dialecte(client):
    """`started_at` est déclarée `DateTime(timezone=True)` et **SQLite rend un
    datetime NAÏF** — mesuré sur ce dépôt.

    Toute arithmétique naïve ⊖ aware lève `TypeError`. Cette garde exige que
    `performed_at` reste exploitable, quel que soit ce que le pilote rend.
    """
    sigs, _ = _signaux([(9, None, 77.5)], None)
    assert sigs, "prémisse invalide : aucun signal"
    quand = sigs[0].performed_at
    assert quand is not None
    # Le calcul d'âge doit être possible sans exploser, naïf ou non.
    reference = T0 if quand.tzinfo else T0.replace(tzinfo=None)
    assert (reference - quand).days >= 0


# ───────── 5. Aucun seuil de vétusté — la frontière avec CP-3 ─────────


def test_le_moteur_reste_aveugle_au_temps():
    """`CP-1` transporte le temps, il ne s'en sert PAS.

    Une règle de décroissance temporelle est une hypothèse de domaine sans
    preuve dans ce dépôt. Cette garde refuse qu'elle apparaisse sans décision
    explicite — c'est la frontière entre `CP-1` (fait) et `CP-3` (politique).

    ⚠ Elle lit le CODE, pas les commentaires : les docstrings de `CP-1`
    parlent abondamment de jours et d'âge, et une sonde naïve les prendrait
    pour du calcul. C'est la forme d'erreur la plus fréquente de ce dépôt.
    """
    import ast
    import pathlib

    src = (pathlib.Path(__file__).resolve().parent.parent
           / "app" / "services" / "overload_engine.py").read_text(encoding="utf-8")
    # `ast.unparse` d'un arbre dont on a retiré les docstrings : il ne reste
    # que du code exécutable, sans un seul commentaire.
    arbre = ast.parse(src)
    for n in ast.walk(arbre):
        if not isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef,
                              ast.AsyncFunctionDef)):
            continue
        corps = n.body
        if (corps and isinstance(corps[0], ast.Expr)
                and isinstance(corps[0].value, ast.Constant)
                and isinstance(corps[0].value.value, str)):
            corps.pop(0)
    code = ast.unparse(arbre)

    INTERDITS = ("timedelta", "days_since", "elapsed", "decay", "staleness",
                 r"\.days", r"now\(")
    trouves = [m for m in INTERDITS if re.search(m, code)]
    assert not trouves, (
        f"le moteur de surcharge utilise le temps : {trouves}. "
        "Une règle de décroissance est une hypothèse de domaine — elle "
        "appartient à CP-3, et elle demande des preuves."
    )


def test_la_garde_de_seuil_mord():
    """Une garde qui n'a jamais vu son motif ne prouve rien."""
    import ast

    faux = "def f(h):\n    '''jours et decay dans la prose'''\n    return h.days > 30\n"
    arbre = ast.parse(faux)
    for n in ast.walk(arbre):
        if isinstance(n, (ast.Module, ast.FunctionDef)):
            c = n.body
            if (c and isinstance(c[0], ast.Expr)
                    and isinstance(c[0].value, ast.Constant)
                    and isinstance(c[0].value.value, str)):
                c.pop(0)
    assert re.search(r"\.days", ast.unparse(arbre)), (
        "la sonde ne verrait pas un vrai usage de `.days`"
    )

    #: Et elle doit ÉPARGNER la prose : une docstring qui parle de jours.
    prose = "def f(h):\n    '''on ne calcule aucun decay ni .days ici'''\n    return h.reps\n"
    a2 = ast.parse(prose)
    for n in ast.walk(a2):
        if isinstance(n, (ast.Module, ast.FunctionDef)):
            c = n.body
            if (c and isinstance(c[0], ast.Expr)
                    and isinstance(c[0].value, ast.Constant)
                    and isinstance(c[0].value.value, str)):
                c.pop(0)
    assert not re.search(r"\.days|decay", ast.unparse(a2)), (
        "la sonde accuse une docstring — elle lit la prose comme du code"
    )
