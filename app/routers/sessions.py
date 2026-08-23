"""Session creation + logging routes.

Architecture note (V1): the session detail page uses **one form per
exercise card** and **one small form for the session-level feedback**.
No per-set PATCH. Justification: on mobile, a user fills an exercise
(warmup + work sets + exercise feedback) in a single block; submitting
that whole block at once is:
  - less round-trips (no PATCH storm)
  - no JS dependency
  - robust to flaky gym connectivity
  - still small per form (an exercise has at most ~8 inputs x 5 rows)

If the product ever needs finer granularity (live set completion on a
smartwatch, for example), a PATCH layer can be added on top without
touching this router.
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.deps import CurrentUser, DbSession
from app.enums import (
    ExerciseSuccessScore,
    MuscleSensation,
    SessionConcentration,
    SessionGlobalState,
    SessionStatus,
    SetExecutionQuality,
    SetRepsTarget,
)
from app.models.catalog import MethodRule, TemplateExercise, WorkoutTemplate
from app.models.session import SessionExercise, WorkoutSession
from app.services.bodymap_frames import regional_plates
from app.services.console_state import (
    build_console_state,
    command_for,
    condense_reference,
    secondary_for,
)
from app.services.delta import compute_delta, format_delta
from app.services.exercise_history import get_exercise_history
from app.services.form_parsing import (
    clean_str,
    enum_str,
    to_float,
    to_int,
)
from app.services.overload_engine import OverloadHint, compute_overload_hint
from app.services.overload_explainer import explain_overload_hint
from app.services.overload_inputs import build_overload_input_for_exercise
from app.services.ownership import get_owned_session_or_404
from app.services.seed import CUSTOM_CATALOG_SECTION
from app.services.session_builder import instantiate_session
from app.services.session_recap import build_recap
from app.services.session_state import latest_open_session
from app.services.stats import (
    last_time_by_exercise_code,
    summarise_current_exercise,
)
from app.services.user_program_launch import is_owned_published_template
from app.templating import local_weekday_iso, templates

router = APIRouter(tags=["sessions"])


# Whitelists derived from app.enums once, reused in form parsing.
_CONCENTRATION = {e.value for e in SessionConcentration}
_GLOBAL_STATE = {e.value for e in SessionGlobalState}
_MUSCLE_SENSATION = {e.value for e in MuscleSensation}
_EXECUTION_QUALITY = {e.value for e in SetExecutionQuality}
_REPS_TARGET = {e.value for e in SetRepsTarget}
_SUCCESS_SCORE = {int(e) for e in ExerciseSuccessScore}


# ----------------------------------------------------------------------
# Create
# ----------------------------------------------------------------------


# Sb_13 — whitelist for `creation_source`. Values outside are silently
# stored as NULL to keep the field strictly analytical.
_CREATION_SOURCE_ALLOWED = {
    "reco_top", "reco_alt", "launcher", "library", "replay",
}


@router.post("/sessions", responses={404: {"description": "Unknown template"}})
def create_session(
    template_slug: Annotated[str, Form()],
    db: DbSession, user: CurrentUser,
    creation_source: Annotated[str | None, Form()] = None,
) -> RedirectResponse:
    tpl = db.execute(
        select(WorkoutTemplate)
        .where(WorkoutTemplate.slug == template_slug)
        .options(
            selectinload(WorkoutTemplate.exercises).selectinload(
                TemplateExercise.rep_targets
            )
        )
    ).scalar_one_or_none()
    if tpl is None:
        raise HTTPException(status_code=404, detail="Unknown template")
    # PUBLICATION_03 (spec 05 §14) — a custom (user) template is owner-private: only the
    # owner, via a published UserProgramSession link, may launch it by slug. System
    # templates stay launchable by all. Foreign custom template = indistinct 404 (no leak).
    if tpl.catalog_section == CUSTOM_CATALOG_SECTION and not is_owned_published_template(
        db, user.id, tpl.id
    ):
        raise HTTPException(status_code=404, detail="Unknown template")

    session = instantiate_session(db, tpl, datetime.now(UTC), user_id=user.id)
    # Sb_13 — telemetry. Silently reject values outside the whitelist so
    # a typo never breaks session creation.
    if creation_source in _CREATION_SOURCE_ALLOWED:
        session.creation_source = creation_source
    db.commit()
    db.refresh(session)
    return RedirectResponse(
        url=f"/sessions/{session.id}", status_code=303
    )


# ----------------------------------------------------------------------
# Read
# ----------------------------------------------------------------------


def _load_session(db: Session, session_id: int, user_id: int) -> WorkoutSession | None:
    stmt = (
        select(WorkoutSession)
        .where(WorkoutSession.id == session_id, WorkoutSession.user_id == user_id)
        .options(
            selectinload(WorkoutSession.template),  # for kind check in template
            selectinload(WorkoutSession.session_exercises)
            .selectinload(SessionExercise.set_logs),
            selectinload(WorkoutSession.session_exercises)
            .selectinload(SessionExercise.template_exercise),
        )
    )
    return db.execute(stmt).scalar_one_or_none()


def _persist_implicit_labels_on_completion(session: WorkoutSession) -> None:
    """Sb_24.3 — compute and freeze implicit signal labels at the moment
    a session transitions to status=completed. Also bumps the session's
    scoring_version to 2 so the new quality_score formula (Sb_24.5) is
    used for it forever, while historic sessions keep version 1.

    Contracts (Sx_24 §C, §D.2, §H) :
      * Idempotent — labels already set are never touched
      * No retroactive recompute — once a label is in the DB, the rule
        engine evolving (Sb_24.next) never modifies it
      * scoring_version is monotonically increased — never decreased
    """
    from app.services.implicit_signal import detect_intra_set_label

    now = datetime.now(UTC)
    for se in session.session_exercises:
        if se.implicit_label is not None:
            # Already labeled in a previous transition — leave it alone.
            continue
        work_sets = sorted(
            (sl for sl in se.set_logs if sl.kind == "work" and sl.completed),
            key=lambda sl: sl.set_index,
        )
        label = detect_intra_set_label(work_sets)
        if label is not None:
            se.implicit_label = label.value
            se.implicit_label_computed_at = now
    # Bump the scoring version (never downgrade).
    if session.scoring_version < 2:
        session.scoring_version = 2


def _session_stats(session: WorkoutSession) -> dict:
    """Per-exercise and global counts of completed work sets."""
    per_exercise: dict[int, tuple[int, int]] = {}
    for se in session.session_exercises:
        work_sets = [sl for sl in se.set_logs if sl.kind == "work"]
        done = sum(1 for sl in work_sets if sl.completed)
        per_exercise[se.id] = (done, len(work_sets))
    done_total = sum(d for d, _ in per_exercise.values())
    work_total = sum(t for _, t in per_exercise.values())
    return {
        "per_exercise": per_exercise,
        "done": done_total,
        "total": work_total,
    }


def _build_overload_placeholder(hint: OverloadHint) -> dict | None:
    """Sb_30.next.placeholder — derive a light placeholder dict from a raw
    :class:`OverloadHint`. Returns ``None`` if no numeric target is
    available (state ``unknown`` is already filtered upstream via
    ``is_silent``, but we keep a defensive None-check).

    Format (Sb_DOGFOOD_01.3 — compact mobile placeholder) :
      - ``weight`` : ``"102.5"`` (valeur nue ; l'unité kg reste portée par le
        label existant à côté du champ ; le placeholder reste court pour tenir
        dans les inputs mobiles étroits).
      - ``reps``   : ``"6-10"`` ou ``"6"`` (deload : range collapsée).

    Le caractère "suggestion" est porté par le placeholder lui-même (texte
    grisé, jamais rempli) et par le contexte de la console de saisie : on
    retire le préfixe ``≈`` qui alourdissait le rendu sur mobile étroit
    (ex. ``"≈ 102.5"``). Aucun verbe ; aucune injection en ``value=`` ;
    jamais un préremplissage.
    """
    if hint.target_weight_kg is None:
        return None
    weight = f"{hint.target_weight_kg:g}"
    if hint.target_reps_min is None and hint.target_reps_max is None:
        reps = None
    elif hint.target_reps_min == hint.target_reps_max:
        reps = f"{hint.target_reps_min}"
    elif hint.target_reps_min is None or hint.target_reps_max is None:
        v = hint.target_reps_min if hint.target_reps_min is not None else hint.target_reps_max
        reps = f"{v}"
    else:
        reps = f"{hint.target_reps_min}-{hint.target_reps_max}"
    return {"weight": weight, "reps": reps}


WEEKDAY_LABELS = {
    1: "Lundi",
    2: "Mardi",
    3: "Mercredi",
    4: "Jeudi",
    5: "Vendredi",
    6: "Samedi",
    7: "Dimanche",
}


def _positive_int(raw: str | None) -> int | None:
    """Un paramètre d'URL est une entrée hostile : il ne lève jamais.

    `?fix=abc`, `?fix=-1`, `?fix=` rendent la page normalement, sans état de
    correction. Refuser bruyamment ferait d'un lien mal recopié une erreur 500.
    """
    if not raw:
        return None
    try:
        value = int(raw)
    except ValueError:
        return None
    return value if value > 0 else None


def _persist_set_values(se, form) -> None:
    """Écrit les valeurs de série postées. `completed` reste dérivé serveur.

    Sx_24 §E : vide = non fait, weight **ou** reps renseigné = fait. Aucune
    checkbox, jamais.

    Sx_UIV3_02 Q3 — « RETIRER CETTE SÉRIE ». `completed` étant dérivé de la
    PRÉSENCE d'une valeur, vider les deux champs dé-complétait déjà la série,
    mais **silencieusement**, comme effet de bord d'un champ effacé par
    accident. La sémantique ne change pas — elle devient **nommée**.
    `clear_set` force les deux valeurs à `None` quelles que soient les valeurs
    sérialisées par le navigateur, pour que l'intention l'emporte sur le
    contenu du formulaire.

    Aucun état persisté nouveau : même colonne, même dérivation.
    """
    clear_set_id = _positive_int(form.get("clear_set"))
    for sl in se.set_logs:
        if sl.id == clear_set_id:
            new_weight = new_reps = None
        else:
            p = f"set_{sl.id}_"
            new_weight = to_float(form.get(p + "weight_kg"))
            new_reps = to_int(form.get(p + "reps"))
        sl.weight_kg = new_weight
        sl.reps = new_reps
        sl.completed = (new_weight is not None) or (new_reps is not None)


def _console_context(
    ordered: list,
    *,
    active_exercise_id: int | None,
    next_code_by_exercise: dict[int, str | None],
    prev_code_by_exercise: dict[int, str | None],
    last_time: dict,
    rest_signal: bool,
    fix_set_id: int | None,
) -> dict[str, dict]:
    """État, commande dominante et sorties secondaires, par exercice.

    `rest` et `fix` ne sont honorés que sur la carte ACTIVE. Un état de repos
    ou de correction sur une carte repliée serait un état d'édition invisible :
    l'utilisateur ne verrait ni la cause ni le moyen d'en sortir.
    """
    states, commands, secondaries, refs = {}, {}, {}, {}
    for se in ordered:
        is_active = se.id == active_exercise_id
        st = build_console_state(
            se,
            next_code=next_code_by_exercise[se.id],
            prev_code=prev_code_by_exercise[se.id],
            rest_signal=rest_signal and is_active,
            fix_set_id=fix_set_id if is_active else None,
        )
        states[se.id] = st
        commands[se.id] = command_for(st)
        secondaries[se.id] = secondary_for(st)
        prior = last_time.get(se.exercise_code_snapshot)
        refs[se.id] = (
            condense_reference(prior["weights_str"], prior["reps_str"])
            if prior and prior.get("has_data") else None
        )
    return {
        "states": states, "commands": commands,
        "secondaries": secondaries, "refs": refs,
    }


@router.get(
    "/sessions/{session_id}",
    response_class=HTMLResponse,
    response_model=None,
)
def session_detail(
    session_id: int, request: Request, db: DbSession, user: CurrentUser
) -> HTMLResponse | RedirectResponse:
    session = _load_session(db, session_id, user.id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status == SessionStatus.COMPLETED:
        return RedirectResponse(
            url=f"/sessions/{session_id}/done", status_code=303
        )

    stats = _session_stats(session)
    rules = db.execute(
        select(MethodRule).order_by(MethodRule.position).limit(3)
    ).scalars().all()

    last_time = last_time_by_exercise_code(
        db, session, datetime.now(UTC)
    )

    # Sb_30.4 — legacy "Repère" hint removed. Guidance now delivered
    # exclusively via overload_hints (deterministic engine + numeric
    # target + reasons, cf. Sx_30 §6). No consumers remain for the
    # legacy `hints` dict ; the import + injection are gone.

    # Sb_30.2 — Progressive Overload Engine V1 injection.
    # Calcule un OverloadHint par SessionExercise et l'explain en payload
    # template (dict). Ne consomme pas encore exercise_card.html (Sb_30.3+).
    # Si l'input est None (target manquante), on rend l'hint silencieux.
    overload_hints: dict[int, dict] = {}
    # Sb_30.next.placeholder — light placeholder hints for the first work
    # set inputs of the active card. Built from the raw OverloadHint
    # (engine output), kept disjoint from `overload_hints` so the template
    # can render the visible hint and the input placeholder independently.
    # We never inject a `value=` here — only `placeholder=` (no pre-fill,
    # cf. règle produit).
    overload_placeholders: dict[int, dict] = {}
    for se in session.session_exercises:
        ov_input = build_overload_input_for_exercise(db, session, se)
        if ov_input is None:
            continue
        hint = compute_overload_hint(ov_input)
        explained = explain_overload_hint(hint)
        if explained["is_silent"]:
            continue
        overload_hints[se.id] = explained
        ph = _build_overload_placeholder(hint)
        if ph is not None:
            overload_placeholders[se.id] = ph

    # Per-exercise compact summary used by the completed-session
    # readability block (still computed even when in_progress, the
    # template decides whether to render it).
    exercise_summaries: dict[int, dict | None] = {
        se.id: summarise_current_exercise(se) for se in session.session_exercises
    }

    from app.services import machine_atlas
    from app.services.body_map_descriptor import build_body_map_descriptor
    from app.services.hints import compute_hints as compute_sb08_hints
    from app.services.substitution import (
        actual_exercise_name,
        can_substitute,
        compute_suggestions,
        get_substitutes,
    )
    substitution_data: dict[int, dict] = {}
    atlas_data: dict[int, dict | None] = {}
    # Sb_32.next — body-map descriptor (Sx_32) per session exercise. First
    # visible consumer of body_map_descriptor: the Worked Area reads the zone
    # actually resolved by the Sx_32 mapping (not just the atlas family).
    # exercise_code = actual exercise name (Sb_32.2 identity convention).
    body_map_data: dict[int, dict] = {}
    sb08_hints_by_exercise: dict[int, list[dict]] = {}
    for se in session.session_exercises:
        # Sb_22a — keep legacy `substitutes` (flat list) for backward
        # compatibility with the existing radio drawer, and add the
        # grouped N1/N2/N3 payload for the new tiered UI.
        subs = get_substitutes(se.template_exercise)
        grouped = compute_suggestions(se.template_exercise)
        substitution_data[se.id] = {
            "substitutes": subs,
            "can_substitute": can_substitute(se),
            "grouped": {
                level: [
                    {"name": s.name, "badge": s.badge, "rationale": s.rationale}
                    for s in grouped[level]
                ]
                for level in ("N1", "N2", "N3")
            },
        }
        # Sb_22a.next2 — atlas suit le réalisé : si un substitut est
        # choisi et présent dans l'atlas, le panel "Comment bien exécuter"
        # et les cues du peek affichent les bonnes consignes. Sinon
        # fallback transparent sur le prescrit.
        atlas_data[se.id] = machine_atlas.get_for_session_exercise(se)
        # Sb_32.next — resolve the worked body zones via the Sx_32 mapping.
        # Uses the name actually performed (follows substitution) as both the
        # display name and the lookup key (Sb_32.2 `exercise_code = name`).
        _ex_name = actual_exercise_name(se)
        body_map_data[se.id] = build_body_map_descriptor(
            _ex_name, exercise_code=_ex_name, db=db
        )
        sb08_hints_by_exercise[se.id] = [
            h.to_dict()
            for h in compute_sb08_hints(se, last_time.get(se.exercise_code_snapshot))
        ]

    # Delta vs the prior occurrence's first completed work set.
    # Only rendered when the CURRENT exercise has a first completed
    # work set AND the prior session had one too.
    delta_labels: dict[str, str | None] = {}
    for se in session.session_exercises:
        code = se.exercise_code_snapshot
        # Current first completed work set
        curr_work = sorted(
            (sl for sl in se.set_logs if sl.kind == "work"),
            key=lambda s: s.set_index,
        )
        curr_done = [
            sl for sl in curr_work
            if sl.completed and (sl.weight_kg is not None or sl.reps is not None)
        ]
        curr_w = curr_done[0].weight_kg if curr_done else None
        curr_r = curr_done[0].reps if curr_done else None

        prior = last_time.get(code)
        prior_w, prior_r, prior_score = None, None, None
        if prior and prior.get("first_set"):
            prior_w = prior["first_set"].get("weight_kg")
            prior_r = prior["first_set"].get("reps")
            prior_score = prior.get("success_score")

        delta = compute_delta(
            curr_w, curr_r, se.success_score,
            prior_w, prior_r, prior_score,
        )
        delta_labels[code] = format_delta(delta)

    # Determine which exercise card to expand (Sb_02 accordion)
    active_exercise_id = None
    active_param = request.query_params.get("active")
    if active_param:
        try:
            active_exercise_id = int(active_param)
        except (ValueError, TypeError):
            pass

    if active_exercise_id is None:
        # Default: first non-complete exercise
        for se in session.session_exercises:
            done, total = stats["per_exercise"][se.id]
            if total == 0 or done < total:
                active_exercise_id = se.id
                break

    # Sb_02.1 — compute jump bar state + next exercise code per card.
    # States (priority: active overrides others):
    #   active  = this card is currently focused
    #   done    = total > 0 and done == total
    #   partial = 0 < done < total
    #   future  = done == 0 (and not active)
    jump_states: dict[int, str] = {}
    next_code_by_exercise: dict[int, str | None] = {}
    prev_code_by_exercise: dict[int, str | None] = {}
    ordered = list(session.session_exercises)
    for idx, se in enumerate(ordered):
        d, t = stats["per_exercise"][se.id]
        if se.id == active_exercise_id:
            jump_states[se.id] = "active"
        elif t > 0 and d == t:
            jump_states[se.id] = "done"
        elif d > 0:
            jump_states[se.id] = "partial"
        else:
            jump_states[se.id] = "future"

        if idx + 1 < len(ordered):
            next_code_by_exercise[se.id] = ordered[idx + 1].exercise_code_snapshot
        else:
            next_code_by_exercise[se.id] = None
        if idx > 0:
            prev_code_by_exercise[se.id] = ordered[idx - 1].exercise_code_snapshot
        else:
            prev_code_by_exercise[se.id] = None

    # Sb_11a — chip for every future/partial card, peek preparing the next
    # exercise at the bottom of the active card.
    from app.services.briefing import build_chip, build_peek
    template_kind_for_briefing = (
        session.template.kind if session.template is not None else None
    )
    briefing_chips: dict[int, dict | None] = {}
    for se in ordered:
        if jump_states.get(se.id) in ("future", "partial"):
            prior = last_time.get(se.exercise_code_snapshot)
            briefing_chips[se.id] = build_chip(
                se.template_exercise, prior, template_kind_for_briefing
            )
        else:
            briefing_chips[se.id] = None

    peek_for_active: dict | None = None
    for idx, se in enumerate(ordered):
        if se.id == active_exercise_id and idx + 1 < len(ordered):
            next_se = ordered[idx + 1]
            peek_for_active = build_peek(
                next_se,
                last_time.get(next_se.exercise_code_snapshot),
                atlas_data.get(next_se.id),
                template_kind_for_briefing,
            )
            break

    # Sx_UIV3_02 §4 — l'ÉTAT devient le contrôleur de la commande.
    console = _console_context(
        ordered,
        active_exercise_id=active_exercise_id,
        next_code_by_exercise=next_code_by_exercise,
        prev_code_by_exercise=prev_code_by_exercise,
        last_time=last_time,
        rest_signal=request.query_params.get("rest") == "1",
        fix_set_id=_positive_int(request.query_params.get("fix")),
    )

    return templates.TemplateResponse(
        request,
        "session_detail.html",
        {
            "page_title": session.template_name_snapshot,
            "session": session,
            # Sb_SESSION_SET_ACTION_01 — signal de repos ÉMIS PAR LE SERVEUR
            # après un enregistrement de série (`nav=stay`). Ce n'est ni une
            # durée persistée ni une valeur de confiance : juste « le repos
            # vient de commencer ». Avec JS le compte à rebours démarre de
            # là ; sans JS l'utilisateur lit un texte et continue — la
            # sauvegarde n'en dépend jamais.
            "rest_active": request.query_params.get("rest") == "1",
            "weekday_label": WEEKDAY_LABELS[local_weekday_iso(session.started_at) or session.weekday_iso],
            "stats": stats,
            "rules": rules,
            "last_time": last_time,
            "overload_hints": overload_hints,
            "overload_placeholders": overload_placeholders,
            "exercise_summaries": exercise_summaries,
            "deltas": delta_labels,
            "active_exercise_id": active_exercise_id,
            "substitution_data": substitution_data,
            "atlas_data": atlas_data,
            "body_map_data": body_map_data,
            "sb08_hints_by_exercise": sb08_hints_by_exercise,
            "briefing_chips": briefing_chips,
            "peek_for_active": peek_for_active,
            "jump_states": jump_states,
            "next_code_by_exercise": next_code_by_exercise,
            "prev_code_by_exercise": prev_code_by_exercise,
            # Sx_UIV3_02 §4 — état de présentation, jamais persisté.
            "console_states": console["states"],
            "console_commands": console["commands"],
            "console_secondaries": console["secondaries"],
            "console_refs": console["refs"],
        },
    )


@router.get(
    "/sessions/{session_id}/done",
    response_class=HTMLResponse,
    name="session_done",
    response_model=None,
)
def session_done(
    session_id: int, request: Request, db: DbSession, user: CurrentUser
) -> HTMLResponse | RedirectResponse:
    session = _load_session(db, session_id, user.id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != SessionStatus.COMPLETED:
        return RedirectResponse(
            url=f"/sessions/{session_id}", status_code=303
        )

    prior_summary_map = last_time_by_exercise_code(
        db, session, datetime.now(UTC)
    )
    prior_weight_by_code: dict[str, float | None] = {}
    for code, prior in prior_summary_map.items():
        fs = prior.get("first_set") if prior else None
        prior_weight_by_code[code] = fs.get("weight_kg") if fs else None

    # Attach prior summary to each SessionExercise so build_recap can compute
    # top_progression without re-querying. Transient attribute, per-request.
    for se in session.session_exercises:
        se._prior_summary = prior_summary_map.get(se.exercise_code_snapshot)

    recap = build_recap(session, prior_weight_by_code=prior_weight_by_code)

    # Sb_24.6 — build a small per-exercise label payload for the review
    # pastilles, and a session-level "score breakdown" when scoring_version
    # >= 2. Both stay None for sessions that have no implicit_label at
    # all (e.g. session courte < 3 sets partout), so the template can
    # conditionally render.
    from app.services.implicit_signal import LABEL_SCORE_CONTRIBUTION, ImplicitLabel
    from app.services.quality_score import (
        W_IMPLICIT,
        W_V1,
        _implicit_signal_avg,
        compute_session_quality,
        compute_session_quality_strength,
    )

    valid_labels = {label.value for label in ImplicitLabel}
    implicit_by_se: dict[int, dict] = {}
    for se in session.session_exercises:
        label_value = getattr(se, "implicit_label", None)
        if label_value in valid_labels:
            label_enum = ImplicitLabel(label_value)
            implicit_by_se[se.id] = {
                "label": label_enum.value,
                "label_display": _LABEL_DISPLAY.get(label_enum.value, label_enum.value),
                "contribution": LABEL_SCORE_CONTRIBUTION[label_enum],
            }

    breakdown: dict | None = None
    if (
        (getattr(session, "scoring_version", 1) or 1) >= 2
        and _session_is_strength(session)
    ):
        avg = _implicit_signal_avg(session)
        # Sb_24.6 — only show the breakdown when the session actually has
        # something to ventilate. No label → V2 falls back to V1 → no
        # decomposition to display (it would just say "V1 → V1").
        if avg is not None:
            v1 = compute_session_quality_strength(session)
            final = compute_session_quality(session)
            breakdown = {
                "v1": v1,
                "implicit_avg": round(avg),
                "weight_v1": W_V1,
                "weight_implicit": W_IMPLICIT,
                "final": final,
                "delta": final - v1,
            }

    # Sb_27.2 — Session Review V1 payload. Composes summary, quality,
    # implicit_signal aggregate, notable_movements (max 3, deterministic
    # rules), and a next_hint phrase. Read-only on top of existing
    # services. Never touches scoring/implicit_signal/quality_score.
    from app.services.session_review import build_session_review

    session_review = build_session_review(db, session)

    return templates.TemplateResponse(
        request,
        "session_done.html",
        {
            "page_title": session.template_name_snapshot,
            "session": session,
            "recap": recap,
            "implicit_by_se": implicit_by_se,
            "breakdown": breakdown,
            "session_review": session_review,
        },
    )


# Sb_24.6 — display labels for the review surface. Keep them short
# (≤ 14 chars) so they fit in the pastille badge.
_LABEL_DISPLAY = {
    "trajectoire_coherente": "Cohérente",
    "reserve_probable": "Réserve probable",
    "pyramidal_ascendant": "Pyramide ↑",
    "pyramidal_descendant": "Pyramide ↓",
    "incoherent": "Incohérente",
}


def _session_is_strength(session) -> bool:
    """Lazy check — avoid importing from quality_score module-level."""
    try:
        kind = session.template.kind if session.template else None
    except Exception:
        kind = None
    return kind != "cardio"


# ----------------------------------------------------------------------
# Update — session-level
# ----------------------------------------------------------------------


@router.post("/sessions/{session_id}")
async def update_session(
    session_id: int, request: Request, db: DbSession, user: CurrentUser
) -> RedirectResponse:
    session = get_owned_session_or_404(db, session_id, user.id)

    form = await request.form()

    session.concentration = enum_str(form.get("concentration"), _CONCENTRATION)
    session.global_state = enum_str(form.get("global_state"), _GLOBAL_STATE)
    session.bodyweight_kg = to_float(form.get("bodyweight_kg"))
    session.free_note = clean_str(form.get("free_note"), max_length=280)

    # Cardio capture (Sb_cardio_capture) — only meaningful for kind=cardio
    # sessions but we parse unconditionally. Non-cardio sessions won't have
    # these fields in the form, resulting in None.
    session.cardio_duration_min = to_int(form.get("cardio_duration_min"))
    session.cardio_bpm_avg = to_int(form.get("cardio_bpm_avg"))
    session.cardio_machine_calories = to_int(form.get("cardio_machine_calories"))
    session.cardio_machine_type = clean_str(
        form.get("cardio_machine_type"), max_length=32
    )

    action = form.get("action")
    if action == "end":
        session.ended_at = datetime.now(UTC)
        session.status = SessionStatus.COMPLETED
        # Sb_24.3 — persist implicit signal labels at completion, exactly once.
        # Idempotent: never re-touch a label that's already set, never
        # downgrade scoring_version. Per Sx_24 §C, §D.2 the persisted
        # label is frozen for life — Sb_24.next2 will bump scoring_version
        # rather than recomputing.
        _persist_implicit_labels_on_completion(session)
    elif action == "reopen" and session.status == SessionStatus.COMPLETED:
        session.ended_at = None
        session.status = SessionStatus.IN_PROGRESS

    db.commit()

    if action == "end":
        return RedirectResponse(
            url=f"/sessions/{session_id}/done", status_code=303
        )
    if action == "reopen":
        return RedirectResponse(
            url=f"/sessions/{session_id}", status_code=303
        )
    return RedirectResponse(
        url=f"/sessions/{session_id}#session-feedback", status_code=303
    )


# ----------------------------------------------------------------------
# Update — exercise card (feedback + all its sets in one submit)
# ----------------------------------------------------------------------


def stay_redirect_target(
    session_id: int,
    se,
    *,
    is_last_exercise: bool = False,
    start_rest: bool = True,
) -> str:
    """Où revenir après avoir enregistré une série, sans quitter l'exercice.

    Sb_SESSION_SET_ACTION_01 — le produit n'avait que `prev` et `next`, qui
    quittent tous deux l'exercice. Le cockpit paraissait donc set-by-set
    alors que la seule action réelle était exercise-by-exercise.

    Trois propriétés portent tout le contrat :

    * **on reste sur le même exercice** — c'est la définition de l'action ;
    * **on retombe sur la PROCHAINE série non complétée**, jamais en haut de
      page : un retour au sommet annulerait les 867 px que
      `Sb_UIV2_SESSION_FOCUS_02` a gagnés devant l'action primaire. Quand
      toutes les séries de travail sont faites, l'ancre vise la carte, donc
      le CTA d'exercice — l'étape suivante réelle ;
    * **sur la DERNIÈRE série du DERNIER exercice, l'ancre vise le bilan**
      (`Sx_UIV3_02` Q4). L'opérateur a tranché : la première transition après
      la dernière série ouvre la surface de bilan, et `TERMINER LA SÉANCE`
      n'est émise que de là. Renvoyer sur la carte laisserait l'utilisateur
      devant un exercice fini sans lui dire où aller ;
    * **`rest=1` est un signal de DÉPART émis par le serveur**, pas une
      durée persistée. Le repos n'est pas historisé ici : un tracé durable
      exigerait une migration, donc un sprint séparé
      (`Sb_REST_EVENT_TRACE_01`).

    Aucune sémantique de complétion n'est introduite : `completed` reste
    dérivé côté serveur de la présence de weight/reps (Sx_24 §E), écrit par
    la boucle de persistance commune, avant cet aiguillage.
    """
    pending = [
        sl for sl in se.set_logs if sl.kind == "work" and not sl.completed
    ]
    pending.sort(key=lambda sl: sl.set_index)
    if pending:
        # Il reste une série : on la vise. `rest=1` seulement si ce qui vient
        # d'être enregistré est une série de TRAVAIL — un échauffement validé
        # ou une correction ne déclenchent pas de repos. Mesuré au navigateur :
        # sans cette distinction, le décompte démarrait avant la première
        # série de travail.
        rest = "&rest=1" if start_rest else ""
        return f"/sessions/{session_id}?active={se.id}{rest}#set-{pending[0].id}"
    if is_last_exercise:
        return f"/sessions/{session_id}#session-feedback"
    # Exercice fini, d'autres restent : pas de repos à annoncer — la commande
    # dominante est devenue `CONTINUER → Ex`, pas une série à enchaîner.
    return f"/sessions/{session_id}?active={se.id}#exercise-{se.id}"


@router.post("/sessions/{session_id}/exercises/{session_exercise_id}")
async def update_exercise_card(
    session_id: int,
    session_exercise_id: int,
    request: Request,
    db: DbSession, user: CurrentUser,
) -> RedirectResponse:
    # Verify the parent session belongs to this user first.
    get_owned_session_or_404(db, session_id, user.id)
    stmt = (
        select(SessionExercise)
        .where(
            SessionExercise.id == session_exercise_id,
            SessionExercise.session_id == session_id,
        )
        .options(
            selectinload(SessionExercise.set_logs),
            selectinload(SessionExercise.template_exercise),
        )
    )
    se = db.execute(stmt).scalar_one_or_none()
    if se is None:
        raise HTTPException(status_code=404, detail="Exercise card not found")

    form = await request.form()

    # Exercise-level feedback
    se.muscle_sensation = enum_str(form.get("muscle_sensation"), _MUSCLE_SENSATION)
    se.free_note = clean_str(form.get("free_note"), max_length=140)

    # Substitution (Sb_03) — only if no work set is completed yet
    from app.services.substitution import can_substitute
    sub_name = clean_str(form.get("substituted_name"), max_length=255)
    if sub_name and can_substitute(se):
        se.substituted_name = sub_name
    elif not sub_name and can_substitute(se):
        se.substituted_name = None

    # Per-set values — the form encodes them as set_{id}_{field}
    # Sb_24.4 — `completed` is derived server-side from the presence of
    # any value (weight or reps), no longer saisi via a checkbox in the
    # UI. Spec Sx_24 §E : vide = non fait, weight or reps renseigné =
    # fait. This change ONLY affects new POSTs. Historic rows keep
    # their existing `completed` value untouched (no migration).
    _persist_set_values(se, form)

    # Derive success_score from set data (Sb_01)
    from app.services.feedback import compute_success_score
    se.success_score = compute_success_score(se, se.template_exercise)

    db.commit()

    # Sb_05 save-on-next + save-on-prev: the form carries an optional
    # `nav` field indicating the target direction:
    #   "prev" → jump to previous exercise (save happens silently first)
    #   anything else → default = jump to next exercise (legacy behaviour)
    nav_direction = (form.get("nav") or "next").strip().lower()

    # Sb_SESSION_SET_ACTION_01 — « stay » : l'action de SÉRIE.
    #
    # Jusqu'ici le produit n'avait que deux issues, `prev` et `next`, toutes
    # deux quittant l'exercice. Le cockpit paraissait donc set-by-set alors
    # que la seule action réelle était exercise-by-exercise.
    #
    # `stay` réutilise EXACTEMENT la persistance ci-dessus — mêmes champs,
    # mêmes valeurs, même dérivation serveur de `completed` à partir de la
    # présence de weight/reps (Sx_24 §E). Aucune sémantique nouvelle, aucune
    # colonne, aucune migration : seule la DESTINATION change.
    #
    # Retour ancré sur la PROCHAINE série non complétée, jamais en haut de
    # page — sinon l'action de série annulerait les 867 px gagnés par
    # Sb_UIV2_SESSION_FOCUS_02.
    #
    # `rest=1` est un SIGNAL DE DÉPART émis par le serveur, pas une durée
    # persistée : le repos n'est pas historisé dans cette tranche (un tracé
    # durable demanderait une migration → Sb_REST_EVENT_TRACE_01).
    # `stay` — l'action de série, qui démarre le repos (contrat
    # `Sb_SESSION_SET_ACTION_01`, inchangé).
    # `stay_norest` — même destination, aucun repos : validation d'un
    # échauffement ou enregistrement d'une correction. Ce ne sont pas des
    # séries de travail exécutées.
    if nav_direction in ("stay", "stay_norest"):
        # Q4 — la dernière série du dernier exercice ouvre le bilan. Il faut
        # donc savoir s'il existe un exercice après celui-ci.
        has_next = db.execute(
            select(SessionExercise.id)
            .where(
                SessionExercise.session_id == session_id,
                SessionExercise.position > se.position,
            )
            .limit(1)
        ).scalar_one_or_none() is not None
        return RedirectResponse(
            url=stay_redirect_target(
                session_id,
                se,
                is_last_exercise=not has_next,
                start_rest=nav_direction == "stay",
            ),
            status_code=303,
        )

    if nav_direction == "prev":
        neighbor = db.execute(
            select(SessionExercise)
            .where(
                SessionExercise.session_id == session_id,
                SessionExercise.position < se.position,
            )
            .order_by(SessionExercise.position.desc())
            .limit(1)
        ).scalar_one_or_none()
        if neighbor is not None:
            target = f"/sessions/{session_id}?active={neighbor.id}#exercise-{neighbor.id}"
        else:
            # Already first exercise; stay on it (reload with same anchor)
            target = f"/sessions/{session_id}?active={se.id}#exercise-{se.id}"
        return RedirectResponse(url=target, status_code=303)

    # Default: next exercise or session feedback
    next_se = db.execute(
        select(SessionExercise)
        .where(
            SessionExercise.session_id == session_id,
            SessionExercise.position > se.position,
        )
        .order_by(SessionExercise.position.asc())
        .limit(1)
    ).scalar_one_or_none()
    if next_se is not None:
        target = f"/sessions/{session_id}?active={next_se.id}#exercise-{next_se.id}"
    else:
        target = f"/sessions/{session_id}#session-feedback"
    return RedirectResponse(url=target, status_code=303)


# ----------------------------------------------------------------------
# Rules page
# ----------------------------------------------------------------------


@router.get("/science", response_class=HTMLResponse, name="science_page")
def science_page(request: Request, db: DbSession, user: CurrentUser) -> HTMLResponse:
    rules = db.execute(
        select(MethodRule).order_by(MethodRule.position)
    ).scalars().all()
    return templates.TemplateResponse(
        request,
        "science.html",
        {
            "page_title": "Science",
            "rules": rules,
            # Sb_BODYMAP_FRAME_ATLAS_01 — declared frames per produced plate.
            # The template renders whatever this mapping declares; it holds no
            # per-region logic of its own.
            "muscle_focus_plates": {p.region: p for p in regional_plates()},
            "active_session": latest_open_session(db, user.id),
        },
    )


@router.get("/rules", name="rules_page")
def rules_redirect() -> RedirectResponse:
    """Legacy URL — /rules redirects 301 to /science."""
    return RedirectResponse(url="/science", status_code=301)


@router.get("/science/atlas", response_class=HTMLResponse, name="science_atlas")
def science_atlas(request: Request, db: DbSession, user: CurrentUser) -> HTMLResponse:
    """Catalogue des machines (atlas) consultable hors séance."""
    from app.services import machine_atlas
    return templates.TemplateResponse(
        request,
        "atlas.html",
        {
            "page_title": "Atlas machines",
            "families": machine_atlas.all_families(),
            "atlas_version": machine_atlas.atlas_version(),
            "active_session": latest_open_session(db, user.id),
        },
    )


# ----------------------------------------------------------------------
# Exercise history detail (Sprint 4)
# ----------------------------------------------------------------------


@router.get(
    "/exercise-history/{template_slug}/{exercise_code}",
    response_class=HTMLResponse,
)
def exercise_history_detail(
    template_slug: str,
    exercise_code: str,
    request: Request,
    db: DbSession, user: CurrentUser,
) -> HTMLResponse:
    entries = get_exercise_history(db, template_slug, exercise_code, user_id=user.id)

    # Use the exercise_name snapshot of the most recent entry so the
    # header reads naturally. Fall back to the raw slug/code if the
    # identity has no history yet.
    display_exercise_name: str | None = None
    display_template_name: str | None = None
    if entries:
        # Fetch the SessionExercise row of the most recent entry to
        # get the snapshotted names. One extra SELECT, cheap.
        row = db.execute(
            select(WorkoutSession, SessionExercise)
            .join(SessionExercise, SessionExercise.session_id == WorkoutSession.id)
            .where(
                WorkoutSession.template_slug_snapshot == template_slug,
                SessionExercise.exercise_code_snapshot == exercise_code,
            )
            .order_by(WorkoutSession.started_at.desc())
            .limit(1)
        ).first()
        if row is not None:
            display_template_name = row[0].template_name_snapshot
            display_exercise_name = row[1].exercise_name_snapshot

    return templates.TemplateResponse(
        request,
        "exercise_history.html",
        {
            "page_title": f"{exercise_code} · {display_exercise_name or exercise_code}",
            "template_slug": template_slug,
            "exercise_code": exercise_code,
            "display_template_name": display_template_name or template_slug,
            "display_exercise_name": display_exercise_name or exercise_code,
            "entries": entries,
            "active_session": latest_open_session(db, user.id),
        },
    )


@router.get("/exercise-history/{slug}", response_class=HTMLResponse)
def exercise_history_by_identity(
    slug: str,
    request: Request,
    db: DbSession, user: CurrentUser,
) -> HTMLResponse:
    """`TRAIN1-B` — l'historique d'un exercice sur son IDENTITÉ STABLE.

    Décision opérateur : « converger le drill-down d'historique d'exercice sur
    la même identité stable ; conserver les entrées héritées en compatibilité
    seulement ».

    La route héritée ci-dessus reste **intacte et fonctionnelle** — aucune
    redirection, aucun changement de contrat : des liens existants la visent,
    et casser une URL pour gagner de l'élégance serait un mauvais échange.
    Elle continue simplement de répondre sur `(gabarit, code)`, c'est-à-dire
    sur une vue **partielle** du même mouvement.

    Mesuré : `Leg extensions assises` vit dans 4 gabarits sous 3 codes. Sous
    l'ancienne clé, son historique était éclaté en quatre sans que rien ne le
    dise. Ici il est entier.
    """
    from app.models.exercise import Exercise
    from app.services.exercise_history import get_exercise_history_by_slug

    exercise = db.execute(
        select(Exercise).where(Exercise.slug == slug)
    ).scalars().first()
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercice inconnu")

    entries = get_exercise_history_by_slug(db, slug, user_id=user.id)

    return templates.TemplateResponse(
        request,
        "exercise_history.html",
        {
            "page_title": exercise.name,
            "template_slug": None,
            "exercise_code": None,
            # Pas de gabarit unique à nommer : l'identité stable en réunit
            # potentiellement plusieurs. Le gabarit est une provenance, rendue
            # ligne par ligne, jamais un titre.
            "display_template_name": None,
            "display_exercise_name": exercise.name,
            "entries": entries,
            "active_session": latest_open_session(db, user.id),
        },
    )
