"""Sb_27.3 — Weekly training loop payload composer.

Composes the "Cette semaine" tile rendered at the top of `GET /progress`:

* sessions_count + previous_week comparison + delta
* volume_signal (deterministic phrase based on count)
* dominant_templates (top 2 by occurrence in the week)
* top_anomaly (first surfaced from existing `compute_anomalies` service,
  never invented)
* hint (deterministic phrase from count + delta + anomaly presence)
* data_quality flag + explicit "Non déductible" fallbacks

Read-only composition on top of existing services
(`anomalies.compute_anomalies`, model columns). Never modifies state,
never touches scoring core, never persists. Caller is the authenticated
user — every query is scoped via `user_id`.

Contract (Sx_27 §11, §16 verbatim):
* Never invents a value. Missing/insufficient data → explicit fallback
  text ("Pas encore assez de données cette semaine.", "Aucune anomalie
  détectée.", etc.).
* Phrases are deterministic (no LLM).
"""
from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.session import SessionExercise, WorkoutSession
from app.models.user import User

_LOW_DATA_NOTE = "Pas encore assez de données cette semaine."
_NO_ANOMALY_NOTE = "Aucune anomalie détectée."
_MAX_DOMINANT = 2


def build_weekly_loop(
    db: Session, user: User, now: datetime | None = None
) -> dict[str, Any]:
    """Top-level composer. Always returns the full key set.

    The whole composer is also wrapped in a `_safe` so a single
    catastrophic DB error degrades the tile rather than crashing
    `/progress`.
    """
    ref = now or datetime.now(UTC)
    try:
        payload = _compose(db, user, ref)
    except Exception as exc:  # noqa: BLE001 — degrade gracefully
        payload = _empty_payload(ref, error=exc.__class__.__name__)

    # Sb_27.5 — attach a deterministic narrative one-liner. Pure function,
    # never raises on missing fields.
    try:
        from app.services.narrative import narrate_week

        payload["narrative"] = narrate_week(payload)
    except Exception:  # noqa: BLE001, S110 — narrative is best-effort, never blocks
        pass
    return payload


def build_progress_week(
    db: Session, user: User, now: datetime | None = None
) -> dict[str, Any]:
    """`TRAIN1-C` — CE QUE `/progress` CONSOMME, ET RIEN D'AUTRE.

    `build_weekly_loop` produit quatorze clés. Depuis `TRAIN1-A`, la surface en
    lit **deux** : les programmes dominants de la semaine et l'anomalie. Les
    douze autres étaient calculées à chaque affichage puis jetées.

    Quatre d'entre elles ne sont pas de simples calculs perdus, ce sont des
    PHRASES — `narrative`, `hint`, `volume_signal`, `data_quality_note`. Elles
    prescrivent (« pense à la récupération »), encouragent (« bon démarrage »)
    et qualifient (« données partielles »). Les produire pour une surface qui a
    retiré son conteneur, c'est garder vivante une voix que la surface a
    congédiée : il suffit d'un `{{ weekly.hint }}` pour la faire revenir sans
    que rien ne l'arbitre.

    `build_weekly_loop` N'EST PAS SUPPRIMÉE, et `narrate_week` non plus. La
    décision porte sur ce que **le chemin Progression** calcule, pas sur
    l'existence de services réutilisables. Ceux-ci restent testés et appelables.

    Même dégradation que le composeur complet : une erreur DB rend un payload
    vide plutôt que de faire tomber `/progress`.
    """
    ref = now or datetime.now(UTC)
    try:
        week_start = _start_of_iso_week(ref)
        sessions = _load_window_sessions(
            db, user.id, week_start, week_start + timedelta(days=7))
        counter = Counter(s.template_name_snapshot for s in sessions)
        return {
            "dominant_templates": [
                {"name": name, "count": cnt}
                for name, cnt in counter.most_common(_MAX_DOMINANT)
            ],
            "top_anomaly": _pick_top_anomaly(sessions),
        }
    # Dégradation, jamais une page cassée : `/progress` vaut mieux sans son
    # anomalie qu'en erreur 500 parce qu'une requête hebdomadaire a échoué.
    except Exception:  # noqa: BLE001
        return {"dominant_templates": [], "top_anomaly": None}


def _start_of_iso_week(ref: datetime) -> datetime:
    """Monday 00:00 UTC of the ISO week containing `ref`."""
    monday = ref - timedelta(days=ref.weekday())
    return monday.replace(hour=0, minute=0, second=0, microsecond=0)


def _empty_payload(ref: datetime, *, error: str | None = None) -> dict[str, Any]:
    week_start = _start_of_iso_week(ref)
    week_end = week_start + timedelta(days=7)
    payload: dict[str, Any] = {
        "available": False if error else True,
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "sessions_count": 0,
        "previous_week_sessions_count": None,
        "delta_sessions_count": None,
        "volume_signal": _LOW_DATA_NOTE,
        "dominant_templates": [],
        "top_anomaly": None,
        "top_anomaly_note": _NO_ANOMALY_NOTE,
        "hint": None,
        "hint_note": _LOW_DATA_NOTE,
        "data_quality": "low",
        "data_quality_note": _LOW_DATA_NOTE,
    }
    if error:
        payload["error_type"] = error
    return payload


def _compose(db: Session, user: User, ref: datetime) -> dict[str, Any]:
    week_start = _start_of_iso_week(ref)
    week_end = week_start + timedelta(days=7)
    prev_start = week_start - timedelta(days=7)

    # ── current week sessions
    current_sessions = _load_window_sessions(db, user.id, week_start, week_end)
    sessions_count = len(current_sessions)

    # ── previous week count
    previous_count = _count_window_sessions(db, user.id, prev_start, week_start)

    delta = sessions_count - previous_count if previous_count is not None else None

    # ── if no session at all this week → bail to fallback payload
    if sessions_count == 0:
        payload = _empty_payload(ref)
        payload["previous_week_sessions_count"] = previous_count
        payload["delta_sessions_count"] = delta
        return payload

    # ── dominant templates (top N by count)
    template_counter = Counter(s.template_name_snapshot for s in current_sessions)
    dominant_templates = [
        {"name": name, "count": cnt}
        for name, cnt in template_counter.most_common(_MAX_DOMINANT)
    ]

    # ── top_anomaly via existing service, first non-empty wins
    top_anomaly = _pick_top_anomaly(current_sessions)

    # ── volume signal (phrase deterministe selon count)
    volume_signal = _volume_signal(sessions_count)

    # ── hint deterministe
    hint = _hint_for(sessions_count, delta, top_anomaly)

    # ── data quality flag: "ok" if >= 2 sessions, "low" otherwise
    if sessions_count >= 2:
        data_quality = "ok"
        data_quality_note = ""
    else:
        data_quality = "low"
        data_quality_note = "Données partielles — la semaine vient juste de commencer."

    return {
        "available": True,
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "sessions_count": sessions_count,
        "previous_week_sessions_count": previous_count,
        "delta_sessions_count": delta,
        "volume_signal": volume_signal,
        "dominant_templates": dominant_templates,
        "top_anomaly": top_anomaly,
        "top_anomaly_note": _NO_ANOMALY_NOTE if top_anomaly is None else None,
        "hint": hint,
        "hint_note": None if hint else _LOW_DATA_NOTE,
        "data_quality": data_quality,
        "data_quality_note": data_quality_note,
    }


# ───────── DB helpers ─────────


def _load_window_sessions(
    db: Session, user_id: int, start: datetime, end: datetime
) -> list[WorkoutSession]:
    stmt = (
        select(WorkoutSession)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == "completed",
            WorkoutSession.excluded_from_stats.is_(False),
            WorkoutSession.started_at >= start,
            WorkoutSession.started_at < end,
        )
        .order_by(WorkoutSession.started_at.asc())
        .options(
            selectinload(WorkoutSession.session_exercises).selectinload(
                SessionExercise.set_logs
            )
        )
    )
    return list(db.execute(stmt).scalars().all())


def _count_window_sessions(
    db: Session, user_id: int, start: datetime, end: datetime
) -> int:
    from sqlalchemy import func

    return int(
        db.execute(
            select(func.count(WorkoutSession.id)).where(
                WorkoutSession.user_id == user_id,
                WorkoutSession.status == "completed",
                WorkoutSession.excluded_from_stats.is_(False),
                WorkoutSession.started_at >= start,
                WorkoutSession.started_at < end,
            )
        ).scalar_one()
    )


# ───────── signals ─────────


def _volume_signal(count: int) -> str:
    """Match the Sb_27.1 home phrasing for consistency."""
    if count == 1:
        return "1 séance cette semaine. Bon départ."
    if count <= 3:
        return f"{count} séances cette semaine."
    return f"{count} séances cette semaine. Volume soutenu."


def _pick_top_anomaly(
    sessions: list[WorkoutSession],
) -> dict[str, Any] | None:
    """Run `compute_anomalies` on each session ; surface the first non-empty
    one with a small context payload. Never invents — if the service returns
    nothing, we return None."""
    try:
        from app.services.anomalies import compute_anomalies
    except Exception:
        return None

    for s in sessions:
        try:
            anomalies = compute_anomalies(s)
        except Exception:  # noqa: S112 — per-session anomaly failure is non-fatal
            continue
        if not anomalies:
            continue
        first = anomalies[0]

        # ════════════════════════════════════════════════════════════════
        # ⚠ CETTE FONCTION LISAIT QUATRE ATTRIBUTS QUI N'EXISTENT PAS.
        #
        # Elle demandait `first.code`, `first.label` et
        # `first.session_exercise_id`. `Anomaly` porte `exercise_code`,
        # `rule_code`, `severity`, `message` et `context` — et rien d'autre.
        #
        # Les `getattr(..., None)` rendaient l'absence SILENCIEUSE : aucune
        # exception, un dict bien formé, et le gabarit qui fait
        # `{{ label or code }}` imprimait `None or None`, c'est-à-dire la
        # chaîne « None ». Toute anomalie affichée sur `/progress` l'a donc
        # été sous le nom « Anomalie None », et l'utilisateur ne pouvait
        # jamais savoir laquelle.
        #
        # C'est exactement le motif que ce dépôt a déjà nommé ailleurs : un
        # repli défensif sur un contexte manquant produit un objet vert et
        # sans comportement. Trouvé en REGARDANT l'écran, pas en lisant le
        # code — aucune garde ne comparait le rendu à un mot lisible.
        #
        # On lit désormais les VRAIS champs. `message` est déjà écrit pour
        # être lu par un humain (« +25% de charge vs dernière fois.
        # Volontaire ? ») ; `rule_code` est un identifiant de règle, gardé
        # comme repli technique mais jamais comme libellé principal.
        # ════════════════════════════════════════════════════════════════
        code = getattr(first, "rule_code", None)
        label = getattr(first, "message", None)
        if not label and not code:
            # Une anomalie qu'on ne sait pas NOMMER n'est pas une
            # information : la taire vaut mieux que d'afficher un objet vide.
            continue

        return {
            "code": code,
            "label": label or code,
            "session_id": s.id,
            "session_template": s.template_name_snapshot,
            "exercise_name": _exercise_name_for(s, first),
        }
    return None


def _exercise_name_for(session, anomaly) -> str | None:
    """Nom de l'exercice visé par une anomalie, ou `None`.

    Le lien passe par `exercise_code` — le SEUL que les règles produisent
    réellement. La version précédente cherchait `session_exercise_id`, qui
    n'existe pas sur `Anomaly` : la boucle ne s'exécutait jamais et le nom
    était toujours absent.

    Le nom SUBSTITUÉ prime : si l'utilisateur a remplacé l'exercice,
    l'anomalie porte sur ce qu'il a réellement fait.
    """
    code = getattr(anomaly, "exercise_code", None)
    if not code:
        return None
    for se in session.session_exercises:
        if se.exercise_code_snapshot == code:
            return se.substituted_name or se.exercise_name_snapshot
    return None


def _hint_for(
    sessions_count: int, delta: int | None, top_anomaly: dict | None
) -> str | None:
    """Deterministic single-phrase hint.

    Priority:
      1. anomaly present → "Vérifie <exercise>"
      2. ≥ 4 sessions → "Volume soutenu — pense à la récupération."
      3. delta ≥ +2 vs semaine précédente → "Tu accélères vs la semaine passée."
      4. delta ≤ -2 → "Rythme en baisse vs la semaine passée."
      5. 1 séance → "Bon démarrage — un deuxième passage solidifierait la semaine."
      6. fallback générique
    """
    if top_anomaly is not None:
        exercise = top_anomaly.get("exercise_name") or "la dernière séance"
        return f"Anomalie détectée sur {exercise} — jette un œil au détail."
    if sessions_count >= 4:
        return "Volume soutenu cette semaine — pense à la récupération."
    if delta is not None and delta >= 2:
        return "Tu accélères vs la semaine passée — garde le rythme."
    if delta is not None and delta <= -2:
        return "Rythme en baisse vs la semaine passée — la prochaine séance compte."
    if sessions_count == 1:
        return "Bon démarrage — un deuxième passage solidifierait la semaine."
    return "Continue sur cette base — les recommandations s'affinent à chaque séance."
