"""`D9` — les deux read models de l'application (`Sx_AUREN_MOBILE_EXPERIENCE_VNEXT §8`).

LE SERVEUR GARDE LE CERVEAU
-----------------------------
Ces fonctions ne décident rien. Elles sérialisent ce que les services canoniques
rendent déjà — la recommandation servie (V3 + mémoire de conseil), le guidage de
surcharge, le dernier résultat, les substituts — sous la forme que le labo `N0`
a validée sur iPhone. Elles remplacent `clients/mobile/scripts/generate_fixtures.py`,
qui calculait les mêmes objets pour un fichier figé.

* `mission_read_model` : quoi faire maintenant, et pourquoi. `RESUME` quand une
  séance est ouverte — aucune recommandation n'est alors calculée, comme sur le web.
* `execution_read_model` : le plan d'UNE séance, entier, pour que l'exécution
  continue hors ligne (`§8.8`) : exercices, séries de travail, table des
  transitions, séries déjà enregistrées, position de reprise.

Pas de méga-objet : rien de l'historique, du profil ou du corps n'y entre.
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.enums import SessionStatus
from app.models.session import SessionExercise, SetLog, WorkoutSession
from app.services.console_state import REST_FALLBACK_SECONDS
from app.services.mission_position import open_session_position
from app.services.muscle_mapping import classify_exercise
from app.services.overload_engine import compute_overload_hint
from app.services.overload_explainer import explain_overload_hint
from app.services.overload_inputs import build_overload_input_for_exercise
from app.services.session_recap import _ZONE_LABELS
from app.services.stats import last_time_by_exercise_code
from app.services.substitution import actual_exercise_name, compute_suggestions

#: Ce que l'application peut faire d'une séance OUVERTE. Une séance close n'en offre aucune.
OPEN_ACTIONS = ("COMPLETE_SET", "FINISH", "PAUSE", "ABANDON")

#: Les clés du contrat JSON que plusieurs objets partagent, nommées une fois :
#: le client `N0` lit exactement ces chaînes.
STATE, PRIMARY_ACTION, TEMPLATE, PHRASE = "state", "primary_action", "template", "phrase"
ALTERNATIVES, REASONS, ORIGIN = "alternatives", "reasons", "origin"
SET_ID, SE_ID, WEIGHT_KG = "set_id", "se_id", "weight_kg"

_GUIDANCE_KEYS = (STATE, "intent_label", "target_summary", REASONS, "is_silent")


def iso_utc(dt: datetime | None) -> str | None:
    """ISO 8601 en UTC explicite. SQLite rend des `datetime` naïfs : ils SONT de l'UTC."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC).isoformat()


def _split_name(name: str) -> tuple[str, str | None]:
    head, _, tail = name.partition(" — ")
    return head, tail or None


# ── MISSION ──────────────────────────────────────────────────────────────


def _resume(db: Session, s: WorkoutSession) -> dict[str, Any]:
    pos = open_session_position(db, s.id)
    name, subtitle = _split_name(s.template_name_snapshot)
    return {
        STATE: "RESUME",
        "session": {"id": s.id, "template_slug": s.template_slug_snapshot,
                    "name": name, "subtitle": subtitle,
                    "started_at": iso_utc(s.started_at)},
        "position": None if pos is None or not pos.is_meaningful else {
            "exercise_index": pos.exercise_index, "exercise_total": pos.exercise_total,
            "sets_done": pos.sets_done, "sets_total": pos.sets_total,
            "exercise_name": pos.exercise_name, "set_index": pos.set_index,
        },
        PRIMARY_ACTION: "RESUME",
    }


def _candidate(c: dict[str, Any]) -> dict[str, Any]:
    tpl = c[TEMPLATE]
    return {"slug": tpl.slug, "name": _split_name(tpl.name)[0], PHRASE: c[PHRASE],
            "executable": bool(tpl.exercises)}


def mission_read_model(db: Session, user_id: int) -> dict[str, Any]:
    from app.services import advice_memory
    from app.services.recommendation_explainer import explain_recommendation
    from app.services.session_state import latest_open_session

    ouverte = latest_open_session(db, user_id)
    if ouverte is not None:
        return _resume(db, ouverte)

    reco = advice_memory.recommander(db, user_id, politique=advice_memory.POLITIQUE_SERVIE,
                                     avec_memoire=advice_memory.MEMOIRE_SERVIE)
    top = reco.get("top")
    if top is None:
        # L'environnement déclaré ne laisse aucun candidat servable : le dire,
        # ne rien inventer à la place.
        return {STATE: "NO_MISSION", PRIMARY_ACTION: None}
    tpl = top[TEMPLATE]
    exercises = sorted(tpl.exercises, key=lambda te: te.position)
    name, subtitle = _split_name(tpl.name)
    expl = top.get("explication") or {}
    alternatives = [_candidate(a) for a in reco.get(ALTERNATIVES, [])]
    return {
        STATE: "READY",
        TEMPLATE: {"slug": tpl.slug, "name": name, "subtitle": subtitle},
        "reason": {PHRASE: top[PHRASE],
                   REASONS: explain_recommendation(reco)[REASONS],
                   "winning": list(expl.get("facteurs_gagnants", ())),
                   "limiting": list(expl.get("facteurs_limitants", ())),
                   "horizon": expl.get("horizon"), "provenance": expl.get("provenance")},
        ALTERNATIVES: alternatives,
        "scope": {"exercise_count": len(exercises),
                  "work_set_count": sum(len(te.rep_targets) for te in exercises),
                  "first_exercise": ({"name": exercises[0].name,
                                      "set_scheme": exercises[0].set_scheme}
                                     if exercises else None)},
        "executable": bool(exercises),
        # L'identité de la décision voyage jusqu'au démarrage, qui seul l'écrit
        # (`REC-CP4`) — exactement les quatre champs cachés du formulaire web.
        "decision": {"fingerprint": reco["context"].get("empreinte_contexte"),
                     "policy": reco["context"].get("politique"),
                     "top": tpl.slug,
                     ALTERNATIVES: [a["slug"] for a in alternatives]},
        "duration_estimate": None,
        PRIMARY_ACTION: "START" if exercises else None,
    }


# ── EXÉCUTION ────────────────────────────────────────────────────────────


def load_owned_session(db: Session, session_id: int, user_id: int) -> WorkoutSession | None:
    return db.execute(
        select(WorkoutSession)
        .where(WorkoutSession.id == session_id, WorkoutSession.user_id == user_id)
        .options(
            selectinload(WorkoutSession.session_exercises).selectinload(SessionExercise.set_logs),
            selectinload(WorkoutSession.session_exercises)
            .selectinload(SessionExercise.template_exercise),
        )
    ).scalar_one_or_none()


def _work_sets(se: SessionExercise) -> list[SetLog]:
    return sorted((x for x in se.set_logs if x.kind == "work"), key=lambda x: x.set_index)


def _rep_range(se: SessionExercise) -> dict | None:
    te = se.template_exercise
    targets = sorted(te.rep_targets, key=lambda t: t.set_index) if te else []
    return {"min": targets[0].min_reps, "max": targets[0].max_reps} if targets else None


def _prefill(hint, first_prev: dict, rng: dict | None) -> dict:
    """D6 : cible du moteur, sinon dernière série faite, sinon rien."""
    if hint and hint.target_weight_kg is not None:
        # Jamais sous la cible basse du moteur : pré-remplir 11 quand il vise 12
        # ferait contredire la saisie par le guidage affiché juste au-dessus.
        reps = max(first_prev.get("reps") or 0, hint.target_reps_min or 0) or None
        return {WEIGHT_KG: hint.target_weight_kg, "reps": reps, ORIGIN: "OVERLOAD_TARGET"}
    if first_prev.get(WEIGHT_KG) is not None:
        return {WEIGHT_KG: first_prev[WEIGHT_KG], "reps": first_prev.get("reps"),
                ORIGIN: "LAST_SET"}
    return {WEIGHT_KG: None, "reps": (rng or {}).get("min"), ORIGIN: "NONE"}


def _best(db: Session, s: WorkoutSession, code: str) -> dict | None:
    """Meilleure série de travail ENREGISTRÉE — charge, puis reps — base des records.

    Même portée que `last_time_by_exercise_code` : même gabarit, même code (les
    codes `E1…` sont locaux au gabarit). Un record ne se compare qu'au même objet.
    """
    rows = db.execute(
        select(SetLog.weight_kg, SetLog.reps)
        .join(SessionExercise, SetLog.session_exercise_id == SessionExercise.id)
        .join(WorkoutSession, SessionExercise.session_id == WorkoutSession.id)
        .where(WorkoutSession.user_id == s.user_id, WorkoutSession.id != s.id,
               WorkoutSession.template_slug_snapshot == s.template_slug_snapshot,
               SessionExercise.exercise_code_snapshot == code, SetLog.kind == "work",
               SetLog.completed.is_(True), SetLog.weight_kg.is_not(None),
               SetLog.reps.is_not(None))).all()
    if not rows:
        return None
    weight, reps = max(rows, key=lambda r: (r[0], r[1]))
    return {WEIGHT_KG: weight, "reps": reps}


def _exercise(db: Session, s: WorkoutSession, se: SessionExercise, last: dict) -> dict:
    inp = build_overload_input_for_exercise(db, s, se)
    hint = compute_overload_hint(inp) if inp else None
    guidance = explain_overload_hint(hint) if hint else None
    prev = last.get(se.exercise_code_snapshot) or {}
    rng = _rep_range(se)
    te = se.template_exercise
    suggestions = compute_suggestions(te) if te else {}
    # même règle que le relevé serveur (`session_recap._zones_touched`)
    primary, _ = classify_exercise(actual_exercise_name(se))
    return {
        SE_ID: se.id, "code": se.exercise_code_snapshot,
        "prescribed_name": se.exercise_name_snapshot, "executed_name": actual_exercise_name(se),
        "set_scheme": te.set_scheme if te else None, "rep_range": rng,
        "guidance": guidance and {k: guidance[k] for k in _GUIDANCE_KEYS},
        "previous": ({"relative": prev.get("relative"), "weights": prev.get("weights_str"),
                      "reps": prev.get("reps_str")} if prev.get("has_data") else None),
        "prefill": _prefill(hint, prev.get("first_set") or {}, rng),
        "substitutes": [sg.name for lvl in ("N1", "N2") for sg in suggestions.get(lvl, [])][:4],
        "zone": None if primary == "unknown" else {"zone": primary,
                                                    "label": _ZONE_LABELS.get(primary, primary)},
        "rest_seconds": None,
        "best": _best(db, s, se.exercise_code_snapshot),
    }


def transitions(sets: list[dict]) -> dict[str, dict]:
    """Table du chemin nominal (`§8.8`), calculée côté serveur ; le client la suit.

    Après la dernière série d'un exercice : repos, PUIS l'exercice suivant — le
    chemin que le labo a fait valider sur iPhone.
    """
    table: dict[str, dict] = {}
    for i, st in enumerate(sets):
        nxt = sets[i + 1] if i + 1 < len(sets) else None
        if nxt is None:
            table[str(st[SET_ID])] = {"kind": "BILAN"}
        elif nxt[SE_ID] == st[SE_ID]:
            table[str(st[SET_ID])] = {"kind": "REST_THEN_SET", SET_ID: nxt[SET_ID]}
        else:
            table[str(st[SET_ID])] = {"kind": "REST_THEN_EXERCISE", SE_ID: nxt[SE_ID],
                                      SET_ID: nxt[SET_ID]}
    return table


def execution_read_model(db: Session, s: WorkoutSession) -> dict[str, Any]:
    now = datetime.now(UTC)
    last = last_time_by_exercise_code(db, s, now)
    ses = sorted(s.session_exercises, key=lambda se: se.position)
    sets, done = [], {}
    for se in ses:
        for x in _work_sets(se):
            sets.append({SET_ID: x.id, SE_ID: se.id, "index": x.set_index})
            if x.completed:
                done[str(x.id)] = {WEIGHT_KG: x.weight_kg, "reps": x.reps,
                                   "performed_at": iso_utc(x.completed_at)}
    cursor = next((st[SET_ID] for st in sets if str(st[SET_ID]) not in done), None)
    is_open = s.status == SessionStatus.IN_PROGRESS.value
    return {
        "session_id": s.id, "template_slug": s.template_slug_snapshot,
        "template_name": s.template_name_snapshot,
        # Abandonner = clore ET exclure des statistiques : l'état canonique existant,
        # sans valeur de statut neuve. On rend les deux faits, pas une étiquette dérivée.
        "status": s.status, "excluded_from_stats": bool(s.excluded_from_stats),
        "started_at": iso_utc(s.started_at), "ended_at": iso_utc(s.ended_at),
        "server_now": now.isoformat(), "rest_default_seconds": REST_FALLBACK_SECONDS,
        "exercises": [_exercise(db, s, se, last) for se in ses],
        "sets": sets, "on_complete": transitions(sets),
        "done": done, "cursor_set_id": cursor if is_open else None,
        "allowed_actions": list(OPEN_ACTIONS) if is_open else [],
    }
