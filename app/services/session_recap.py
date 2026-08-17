"""Read-only recap aggregation for the /done terminal state view.

Consumes existing session data. Computes no new analytics — only
assembles what's already derivable (duration, done/total work sets,
exercise summaries, substitution badges, cardio block).
"""
from __future__ import annotations

from datetime import timedelta
from typing import Any

from app.models.session import WorkoutSession
from app.services.anomalies import compute_anomalies
from app.services.confidence import compute_confidence_score, level_for
from app.services.muscle_mapping import classify_exercise
from app.services.stats import summarise_current_exercise
from app.services.substitution import actual_exercise_name
from app.services.time_format import format_duration_short


def _duration_label(session: WorkoutSession) -> str:
    if not (session.started_at and session.ended_at):
        return ""
    start = session.started_at
    end = session.ended_at
    # SQLite round-trips DATETIMEs as naive. Align tz frames before subtracting.
    if start.tzinfo is None and end.tzinfo is not None:
        start = start.replace(tzinfo=end.tzinfo)
    elif end.tzinfo is None and start.tzinfo is not None:
        end = end.replace(tzinfo=start.tzinfo)
    delta: timedelta = end - start
    return format_duration_short(delta)


def _kind(session: WorkoutSession) -> str:
    tpl = session.template
    if tpl is None:
        return "strength"
    return tpl.kind or "strength"


def _cardio_block(session: WorkoutSession, kind: str) -> dict[str, Any] | None:
    if kind != "cardio":
        return None
    return {
        "duration_min": session.cardio_duration_min,
        "bpm_avg": session.cardio_bpm_avg,
        "calories": session.cardio_machine_calories,
        "machine_type": session.cardio_machine_type,
    }


_ZONE_LABELS: dict[str, str] = {
    "pecs": "Pectoraux",
    "delt_lat": "Deltoïdes latéraux",
    "delt_post": "Deltoïdes postérieurs",
    "lats": "Dos — largeur",
    "upper_back": "Dos — épaisseur",
    "biceps": "Biceps",
    "triceps": "Triceps",
    "quads": "Quadriceps",
    "posterior": "Chaîne postérieure",
    "calves": "Mollets",
    "core": "Core",
}


def _top_progression(session: WorkoutSession) -> dict[str, Any] | None:
    """Return the exercise with the best weight (or reps) delta vs prior.

    Uses the derived ``prior_summary`` when available (see stats.last_time).
    Since build_recap is called at /done time, we don't refetch; we read
    ``se.prior_summary`` only if the caller attached it. If none attached,
    returns None — a superset attach happens in the router.
    """
    best: tuple[float, int, dict[str, Any]] | None = None
    for se in session.session_exercises:
        prior = getattr(se, "_prior_summary", None)
        if not prior or not prior.get("first_set"):
            continue
        work = sorted(
            (sl for sl in se.set_logs if sl.kind == "work"),
            key=lambda s: s.set_index,
        )
        curr_done = [
            sl for sl in work
            if sl.completed and (sl.weight_kg is not None or sl.reps is not None)
        ]
        if not curr_done:
            continue
        curr_w = curr_done[0].weight_kg
        curr_r = curr_done[0].reps
        prior_w = prior["first_set"].get("weight_kg")
        prior_r = prior["first_set"].get("reps")
        weight_delta = (curr_w - prior_w) if (curr_w is not None and prior_w is not None) else None
        reps_delta = (curr_r - prior_r) if (curr_r is not None and prior_r is not None) else None
        if (weight_delta is None or weight_delta <= 0) and (reps_delta is None or reps_delta <= 0):
            continue
        w_key = weight_delta if weight_delta is not None else 0.0
        r_key = reps_delta if reps_delta is not None else 0
        entry = {
            "code": se.exercise_code_snapshot,
            "name": actual_exercise_name(se),
            "weight_delta": weight_delta,
            "reps_delta": reps_delta,
            "score_trend": (
                "up" if (se.success_score is not None and prior.get("success_score") is not None
                         and se.success_score > prior["success_score"])
                else ("down" if (se.success_score is not None and prior.get("success_score") is not None
                                 and se.success_score < prior["success_score"])
                      else "flat" if (se.success_score is not None and prior.get("success_score") is not None)
                      else None)
            ),
        }
        key = (w_key, r_key, entry)
        if best is None or key > best:
            best = key
    return best[2] if best is not None else None


def _zones_touched(session: WorkoutSession) -> list[dict[str, Any]]:
    """Return zones sorted by completed work-set count (desc)."""
    counts: dict[str, int] = {}
    for se in session.session_exercises:
        name = actual_exercise_name(se)
        primary, _ = classify_exercise(name)
        if primary == "unknown":
            continue
        done_work = sum(
            1 for sl in se.set_logs
            if sl.kind == "work" and sl.completed
        )
        if done_work == 0:
            continue
        counts[primary] = counts.get(primary, 0) + done_work
    ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return [
        {"zone": z, "label": _ZONE_LABELS.get(z, z), "sets": c}
        for z, c in ordered
    ]


def build_recap(
    session: WorkoutSession,
    prior_weight_by_code: dict[str, float | None] | None = None,
) -> dict[str, Any]:
    """Return a dict shaped for the session_done.html template."""
    kind = _kind(session)
    duration_label = _duration_label(session)

    total_work = 0
    done_work = 0
    exercises: list[dict[str, Any]] = []
    for se in session.session_exercises:
        work_sets = [sl for sl in se.set_logs if sl.kind == "work"]
        done_sets = [sl for sl in work_sets if sl.completed]
        total_work += len(work_sets)
        done_work += len(done_sets)
        summary = summarise_current_exercise(se)
        display_name = se.substituted_name or se.exercise_name_snapshot
        exercises.append(
            {
                # Sb_24.6 — expose se.id so the template can look up the
                # implicit_label pastille payload (computed in the router).
                "se_id": se.id,
                "code": se.exercise_code_snapshot,
                "name": se.exercise_name_snapshot,
                "substituted_name": se.substituted_name,
                "display_name": display_name,
                "done": len(done_sets),
                "total": len(work_sets),
                "score": se.success_score,
                "weights_str": summary["weights_str"] if summary else None,
                "reps_str": summary["reps_str"] if summary else None,
                # Sb_SESSION_REVIEW_SIGNAL_01 — RESTITUTION, pas collecte.
                #
                # Ces deux signaux étaient saisis pendant la séance et
                # n'étaient jamais rendus à l'utilisateur : le ressenti
                # musculaire n'apparaissait que dans l'historique par
                # exercice, et la note d'exercice nulle part. On demandait
                # donc une information qu'on ne rendait pas.
                #
                # Aucun nouveau champ, aucune collecte ajoutée : on expose ce
                # que le modèle porte déjà. `None` reste `None` — un ressenti
                # non saisi doit se lire comme non mesuré, jamais comme
                # neutre ou mauvais.
                "muscle_sensation": se.muscle_sensation,
                "note": se.free_note,
            }
        )

    completion_pct = round(100 * done_work / total_work) if total_work else None
    substitution_count = sum(1 for e in exercises if e["substituted_name"])

    anomalies = compute_anomalies(
        session, prior_weight_by_code=prior_weight_by_code
    )
    confidence_score = compute_confidence_score(
        session,
        prior_weight_by_code=prior_weight_by_code,
        anomalies=anomalies,
    )
    confidence_level = level_for(confidence_score)

    return {
        "header": {
            "template_name": session.template_name_snapshot,
            "started_at": session.started_at,
            "ended_at": session.ended_at,
            "duration_label": duration_label,
            "kind": kind,
        },
        "summary": {
            "work_sets_done": done_work,
            "work_sets_total": total_work,
            "completion_pct": completion_pct,
            "substitution_count": substitution_count,
            "bodyweight_kg": session.bodyweight_kg,
            "concentration": session.concentration,
            "global_state": session.global_state,
            # Sb_SESSION_REVIEW_SIGNAL_01 — la note de séance était saisie
            # puis jamais relue. `concentration` et `global_state` étaient
            # déjà restitués ; seule la phrase libre manquait.
            "note": session.free_note,
            "cardio": _cardio_block(session, kind),
            "confidence_score": confidence_score,
            "confidence_level": confidence_level,
            "top_progression": _top_progression(session),
            "zones_touched": _zones_touched(session),
            "anomalies": [a.to_dict() for a in anomalies],
        },
        "exercises": exercises,
    }
