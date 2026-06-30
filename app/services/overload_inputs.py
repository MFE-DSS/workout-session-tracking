"""Sb_30.2 — Build OverloadInput from DB for the session detail page.

Traduit les snapshots SQL (sessions passées, set_logs, rep_targets,
template_exercises) en :class:`OverloadInput` purs, prêts pour
:func:`overload_engine.compute_overload_hint`.

Pourquoi un module dédié :
- garde :mod:`overload_engine` strictement pur (sans accès DB)
- garde le router :mod:`app.routers.sessions` lisible
- isole la résolution des historiques (N=3 fixe — OQ-D)

Aucune modification des services métier core (``recommendation``,
``quality_score``, ``implicit_signal``, ``coach_*``, ``body_*``,
``substitution``). Lecture seule uniquement.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.enums import SessionStatus
from app.models.session import SessionExercise, SetLog, WorkoutSession
from app.services.overload_engine import (
    HistoricalSetSignal,
    OverloadInput,
)
from app.services.quality_score import compute_session_quality

HISTORY_N = 3

# Mots-clés pour catégoriser un exercice à partir du snapshot name V1.
# Conservateur : si rien ne matche compound, fallback isolation_free.
_COMPOUND_KEYWORDS: tuple[str, ...] = (
    "squat",
    "deadlift",
    "soulev",  # soulevé de terre
    "bench",
    "développé",
    "developpe",
    "press",
    "row",
    "rowing",
    "tirage",
    "tractions",
    "pull-up",
    "pullup",
    "dip",
    "clean",
    "snatch",
    "thruster",
    "lunge",
    "fente",
)


def categorize_exercise(name: str | None, machine_slug: str | None) -> str:
    """Détermine la catégorie pour les incréments d'overload V1.

    Heuristique stable et conservative :

    - ``machine_slug`` renseigné → ``"isolation_machine"`` (incrément 2.5 kg)
    - sinon nom contient un mot-clé compound → ``"compound"`` (incrément 2.5 kg)
    - sinon → ``"isolation_free"`` (incrément 1.0 kg, le plus prudent)

    Raffinable Sb_30.next sans casser le moteur (qui se contente d'un
    lookup ``str``).
    """
    if machine_slug:
        return "isolation_machine"
    low = (name or "").lower()
    for kw in _COMPOUND_KEYWORDS:
        if kw in low:
            return "compound"
    return "isolation_free"


def _first_completed_work_set(se: SessionExercise) -> SetLog | None:
    work_sets = sorted(
        (sl for sl in se.set_logs if sl.kind == "work"),
        key=lambda s: s.set_index,
    )
    for sl in work_sets:
        if sl.completed and sl.weight_kg is not None and sl.reps is not None:
            return sl
    return None


# Sb_30.bugfix.history-identity-guard — facteur d'écart aberrant accepté
# au sein d'une fenêtre d'historique cohérente (même template, même code,
# même politique de substitution). Au-delà, la donnée est jugée
# contaminée par un bug amont et l'input est rejeté (silent).
_IMPLAUSIBLE_WEIGHT_RATIO = 3.0


def _history_signals_for_code(
    db: Session,
    user_id: int,
    exercise_code: str,
    exclude_session_id: int,
    template_slug_snapshot: str,
    *,
    current_is_substituted: bool,
    current_substituted_name: str | None = None,
    n: int = HISTORY_N,
) -> tuple[HistoricalSetSignal, ...]:
    """Lit les N dernières WorkoutSessions COMPLETED pour ``user_id``
    contenant un :class:`SessionExercise` aligné avec l'identité historique
    de l'exercice courant.

    Sb_30.bugfix.history-identity-guard — V2 de l'identité :

    1. **Même template** (``template_slug_snapshot``) : sinon collision
       inter-template (deux exercices différents partagent le même
       ``exercise_code_snapshot``, ex. ``E2`` = Élévations latérales câble
       sur ``catch-up-shoulders`` mais Rowing câble assis sur ``pull-b``).
       Cette règle aligne l'overload sur :func:`last_time_by_exercise_code`.
    2. **Même politique de substitution** :
       - si la séance courante est prescrite (``substituted_name is None``),
         on ne consomme QUE les historiques prescrits (``substituted_name``
         IS NULL côté DB) — éviter de mélanger les charges du prescrit et
         d'une substitution passée.
       - si la séance courante est substituée et que ``current_substituted_name``
         est fourni, on ne consomme que les historiques avec le **même**
         ``substituted_name`` (match strict). Sinon (cas V1 conservateur),
         l'appelant aura déjà retourné ``None`` en amont.

    Snapshot-based : résiste aux renames de template. Pas d'effet de bord.
    """
    sessions = db.execute(
        select(WorkoutSession)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == SessionStatus.COMPLETED,
            WorkoutSession.id != exclude_session_id,
            # Sb_30.bugfix — alignement avec last_time_by_exercise_code
            # (cf. ``app/services/stats.py``).
            WorkoutSession.template_slug_snapshot == template_slug_snapshot,
        )
        .order_by(WorkoutSession.started_at.desc())
        .limit(50)
    ).scalars().all()

    signals: list[HistoricalSetSignal] = []
    for s in sessions:
        if len(signals) >= n:
            break
        match = next(
            (
                se
                for se in s.session_exercises
                if se.exercise_code_snapshot == exercise_code
                and _matches_substitution_policy(
                    se,
                    current_is_substituted=current_is_substituted,
                    current_substituted_name=current_substituted_name,
                )
            ),
            None,
        )
        if match is None:
            continue
        first_set = _first_completed_work_set(match)
        if first_set is None:
            continue
        # quality_score : 0..100 → 0.0..1.0 ; None si non calculable.
        try:
            raw_quality = compute_session_quality(s)
        except Exception:
            raw_quality = None
        q: float | None
        if raw_quality is None:
            q = None
        else:
            q = max(0.0, min(1.0, float(raw_quality) / 100.0))
        fatigue = (s.global_state == "fatigued")
        signals.append(
            HistoricalSetSignal(
                weight_kg=float(first_set.weight_kg or 0.0),
                reps=int(first_set.reps or 0),
                quality_score=q,
                fatigue_signal=fatigue,
            )
        )
    # Sb_30.bugfix.history-identity-guard — défense en profondeur : si
    # malgré les filtres une cohorte historique présente un écart > 3×
    # entre min et max non-nul, on considère la donnée corrompue et on
    # rejette l'input pour ne pas laisser passer un hint trompeur.
    if not _history_weight_is_plausible(signals):
        return tuple()
    return tuple(signals)


def _matches_substitution_policy(
    past_se: SessionExercise,
    *,
    current_is_substituted: bool,
    current_substituted_name: str | None,
) -> bool:
    """Renvoie ``True`` si ``past_se`` peut entrer dans l'historique
    overload de la séance courante au regard de la politique de
    substitution V2.
    """
    past_sub = (past_se.substituted_name or "").strip() or None
    if not current_is_substituted:
        # Prescrit : on ne consomme QUE le prescrit passé.
        return past_sub is None
    # Substitué courant : on exige le même substituted_name exact.
    if current_substituted_name is None:
        return False
    return past_sub == current_substituted_name.strip()


def _history_weight_is_plausible(signals: list[HistoricalSetSignal]) -> bool:
    """Garde-fou d'écart aberrant. Sb_30.bugfix.history-identity-guard.

    Si la fenêtre historique contient ≥ 2 entrées et que le ratio
    max/min des poids non-nuls dépasse :data:`_IMPLAUSIBLE_WEIGHT_RATIO`,
    on considère la donnée comme contaminée (typiquement un mélange
    inter-template ou inter-substitution qui aurait dû être filtré).
    """
    weights = [s.weight_kg for s in signals if s.weight_kg and s.weight_kg > 0]
    if len(weights) < 2:
        return True
    lo, hi = min(weights), max(weights)
    if lo <= 0:
        return True
    return (hi / lo) <= _IMPLAUSIBLE_WEIGHT_RATIO


def build_overload_input_for_exercise(
    db: Session,
    session: WorkoutSession,
    se: SessionExercise,
) -> OverloadInput | None:
    """Construit un :class:`OverloadInput` ou retourne ``None`` si la
    cible (``target_min``/``target_max``) est inconnue.

    Pas d'effet de bord. Pas d'écriture DB.
    """
    te = se.template_exercise
    if te is None or not te.rep_targets:
        return None
    first_rt = sorted(te.rep_targets, key=lambda r: r.set_index)[0]
    if first_rt.min_reps is None or first_rt.max_reps is None:
        return None

    category = categorize_exercise(
        se.substituted_name or se.exercise_name_snapshot,
        getattr(te, "machine_slug", None),
    )

    # Sb_30.bugfix.history-identity-guard — politique de substitution V1.
    # Si la séance courante est substituée, on n'a pas (encore) de chemin
    # sûr pour produire un overload sans risquer le mélange prescrit ↔
    # substitut. V1 conservateur : retourner ``None`` → l'explainer marque
    # le hint silent et l'UI ne propose AUCUNE cible chiffrée.
    current_substituted_name = (se.substituted_name or "").strip() or None
    current_is_substituted = current_substituted_name is not None
    if current_is_substituted:
        # V1 : pas d'historique fiable pour les substituts. La régression
        # inverse (laisser passer la cible du prescrit sur un substitut)
        # est jugée plus dangereuse que de simplement masquer le hint.
        return None

    template_slug = (session.template_slug_snapshot or "").strip()
    if not template_slug:
        # Sans identité de template, on ne peut pas garantir l'absence
        # de collision inter-template ; on reste silencieux.
        return None

    history = _history_signals_for_code(
        db,
        user_id=session.user_id,
        exercise_code=se.exercise_code_snapshot,
        exclude_session_id=session.id,
        template_slug_snapshot=template_slug,
        current_is_substituted=current_is_substituted,
        current_substituted_name=current_substituted_name,
    )
    return OverloadInput(
        exercise_category=category,
        target_min=int(first_rt.min_reps),
        target_max=int(first_rt.max_reps),
        history=history,
    )
