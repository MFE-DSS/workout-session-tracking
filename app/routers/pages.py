"""Navigation + catalog pages (home, library, history, progress).

The session logging flow lives in `app.routers.sessions`.
"""
from __future__ import annotations

from datetime import UTC

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.config import get_settings
from app.deps import CurrentUser, DbSession
from app.models.catalog import TemplateExercise, WorkoutTemplate
from app.models.session import SessionExercise, SetLog, WorkoutSession
from app.services.kpis import (
    compute_global_kpis,
    compute_recent_exercise_activity,
    compute_template_kpis,
)
from app.services.launcher import (
    BRANCH_TREE,
    TYPE_LABELS,
    get_available_types,
    get_available_variants,
    resolve_branch,
)
from app.services.quality_score import compute_session_quality
from app.services.session_state import latest_open_session
from app.services.time_format import format_duration_short, session_duration
from app.services.timeline import (
    TimelinePoint,
    build_bodyweight_timeline_svg,
    build_quality_timeline_svg,
)
from app.templating import templates

router = APIRouter(tags=["pages"])


def _load_templates(db) -> list[WorkoutTemplate]:
    stmt = (
        select(WorkoutTemplate)
        .options(
            selectinload(WorkoutTemplate.exercises).selectinload(
                TemplateExercise.rep_targets
            )
        )
        .order_by(WorkoutTemplate.display_order, WorkoutTemplate.slug)
    )
    return list(db.execute(stmt).scalars().all())


# Catalog section labels for the library page.
CATALOG_SECTIONS = [
    ("core", "Programmes principaux"),
    ("utility", "Modules utilitaires"),
    ("specialization", "Modules de spécialisation"),
]


def _build_reco_context(db, user_id: int, open_session) -> dict | None:
    """Sb_12 — wrap the recommendation service for the home/launcher contexts.

    Returns None when a session is already open (the partial hides itself
    anyway, but short-circuiting saves a query).
    """
    if open_session is not None:
        return None
    try:
        from app.services.recommendation import recommend_next_session
        return recommend_next_session(db, user_id)
    except Exception:
        # Recommendation is a non-critical signal — never break the home
        # or launcher because of it.
        return None


def _template_work_set_count(db, template_id: int) -> int:
    """Prescribed working sets for a template.

    Sb_UIV2_HOME_RECO_BADGE_01 (décision D2) — the badge states the volume next
    to « RECOMMANDÉ ». Counted here with one aggregate query rather than walking
    `template.exercises[*].rep_targets` in Jinja, which would fire N+1 lazy loads
    on every home render.
    """
    from sqlalchemy import func

    from app.models.catalog import RepTarget, TemplateExercise

    return db.execute(
        select(func.count(RepTarget.id)).join(
            TemplateExercise, RepTarget.template_exercise_id == TemplateExercise.id
        ).where(TemplateExercise.template_id == template_id)
    ).scalar_one()


#: Libellés produit des bandes de récupération. Volontairement descriptifs et
#: prudents : « estimée » partout, aucune prétention physiologique.
_BAND_LABELS = {
    "likely_available": "disponible",
    "partially_recovered": "récupération partielle",
    "likely_fatigued": "encore fatiguée",
    "unknown": "non mesurée",
}

#: Formes courtes, imposées à 360 px (`Sx_UIV3_04 §13`). Même vocabulaire,
#: jamais un synonyme de plus.
_BAND_SHORT = {
    "likely_available": "prête",
    "partially_recovered": "partielle",
    "likely_fatigued": "chargée",
    "unknown": "n.m.",
}

#: Nombre de segments pleins, `Sx_UIV3_00 §5`. C'est la BANDE qui est encodée,
#: jamais l'`estimate` 0–1 : une barre proportionnelle serait une affirmation de
#: pourcentage, que `zone_recovery` refuse explicitement de faire.
_BAND_SEGMENTS = {
    "likely_available": 3,
    "partially_recovered": 2,
    "likely_fatigued": 1,
    "unknown": 0,
}

#: Du pire au meilleur. Sert à désigner la zone qui EXPLIQUE qu'une alternative
#: n'ait pas été retenue. `unknown` vient en tête : ne pas savoir est un motif
#: d'écartement plus fort qu'une fatigue mesurée.
_BAND_RANK = {
    "unknown": 0,
    "likely_fatigued": 1,
    "partially_recovered": 2,
    "likely_available": 3,
}


def _reco_zone_state(db, user_id: int, primary_zones) -> list[dict]:
    """État de récupération des zones que la séance recommandée vise.

    Sb_UIV2_HOME_RECO_WHY_01 (décision D6) — le cycle de ce produit n'est pas un
    calendrier, c'est une rotation pilotée par la récupération. L'état corporel
    n'est donc pas une vignette décorative posée à côté de la recommandation :
    c'est **son explication**. Le hero dit « Push A » ; ceci dit pourquoi.

    Lecture seule, aucun calcul propre : les bandes viennent de `zone_recovery`,
    les libellés de `muscle_mapping`. Une zone sans estimation est rendue
    « non mesurée » — jamais « disponible » par défaut.
    """
    if not primary_zones:
        return []
    from datetime import datetime

    from app.services.muscle_mapping import ZONE_LABELS
    from app.services.zone_recovery import build_zone_recovery

    try:
        estimates = build_zone_recovery(db, user_id, now=datetime.now(UTC))
    except Exception:
        # Non-critical readout: never break the home over an estimate.
        return []

    by_zone = {e.zone_code: e for e in estimates}
    return [_zone_row(code, by_zone, ZONE_LABELS) for code in primary_zones]


def _zone_row(code: str, by_zone: dict, labels: dict) -> dict:
    """Une zone, rendue. Le libellé porte le sens ; la forme le renforce.

    `Sx_UIV3_00 §5` — on expose la BANDE et un nombre de segments, jamais
    l'`estimate` 0–1. Le rendre proportionnellement serait une affirmation de
    pourcentage physiologique, que `zone_recovery` refuse de faire.
    """
    band = getattr(getattr(by_zone.get(code), "band", None), "value", "unknown")
    return {
        "zone": code,
        "label": labels.get(code, code),
        "band": band,
        "band_label": _BAND_LABELS.get(band, _BAND_LABELS["unknown"]),
        "band_short": _BAND_SHORT.get(band, _BAND_SHORT["unknown"]),
        "segments": _BAND_SEGMENTS.get(band, 0),
    }


def _home_causal_context(db, user_id: int, reco: dict | None) -> dict:
    """Tout ce dont le Causal Cockpit a besoin, en UNE lecture de `zone_recovery`.

    `Sx_UIV3_01` — trois sorties, trois `UI_DATA_GAP` refermés **par
    pass-through de présentation** (`Sx_UIV3_00 §0`) :

      `zones`        G3 partiel — les zones que la séance proposée vise
      `tally`        G3 — les 11 zones comptées par bande
      `alternatives` G1 + G2 — les options écartées, et la zone qui l'explique

    **Aucune décision métier n'est créée ici.** Les alternatives et leur score
    sont produits par `recommend_next_session` et simplement transmis ; la zone
    limitante est un TRI des bandes existantes, pas une nouvelle inférence ; le
    comptage est une somme. `recommendation.py` et `zone_recovery.py` ne sont
    pas touchés.
    """
    empty = {"zones": [], "tally": [], "tally_total": 0, "alternatives": []}
    if not reco:
        return empty

    from datetime import datetime

    from app.services.muscle_mapping import ZONE_LABELS
    from app.services.zone_recovery import build_zone_recovery

    try:
        estimates = build_zone_recovery(db, user_id, now=datetime.now(UTC))
    except Exception:
        # Readout non critique : la home ne tombe jamais pour une estimation.
        return empty

    by_zone = {e.zone_code: e for e in estimates}
    rows = [_zone_row(e.zone_code, by_zone, ZONE_LABELS) for e in estimates]

    # — G3. Le total DOIT valoir 11 : une garde le pinne. Les bandes vides sont
    #   omises à l'affichage, jamais du comptage.
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["band"]] = counts.get(row["band"], 0) + 1
    tally = [
        {
            "band": band,
            "count": counts[band],
            "segments": _BAND_SEGMENTS[band],
            "band_label": _BAND_LABELS[band],
        }
        for band in _BAND_SEGMENTS
        if counts.get(band)
    ]

    top = reco.get("top") or {}
    targeted = [
        _zone_row(code, by_zone, ZONE_LABELS)
        for code in (top.get("primary_zones") or [])
    ]

    return {
        "zones": targeted,
        "tally": tally,
        "tally_total": sum(counts.values()),
        # — G1 + G2. Extrait dans son propre helper : Sonar a mesuré la
        #   complexité cognitive de la fonction à 16 pour 15 autorisés, et
        #   c'est ce bloc qui la portait. Le sortir la ramène sous le seuil ET
        #   donne un nom à ce qu'il fait.
        "alternatives": _rejected_alternatives(reco, by_zone, ZONE_LABELS),
    }


def _rejected_alternatives(reco: dict, by_zone: dict, labels: dict) -> list[dict]:
    """Les options écartées, et **la zone qui l'explique**.

    Ce qu'aucun des cinq produits comparés ne montre : l'inverse d'une
    recommandation. Le moteur classe déjà — il produit un score et des
    alternatives — et l'affichage le jetait.

    Aucune décision nouvelle : la zone limitante est un **tri** des bandes
    déjà calculées, du pire au meilleur.
    """
    out: list[dict] = []
    for alt in (reco.get("alternatives") or [])[:2]:
        template = alt.get("template")
        zones = [
            _zone_row(code, by_zone, labels)
            for code in (alt.get("primary_zones") or [])
        ]
        limiting = min(
            zones, key=lambda z: _BAND_RANK.get(z["band"], 9), default=None
        )
        # Toutes les zones disponibles → ce n'est pas la récupération qui a
        # écarté l'option, c'est le score. Le dire, plutôt qu'afficher une zone
        # « disponible » à côté du mot « écarté », ce qui n'expliquerait rien.
        by_recovery = limiting is not None and limiting["band"] != "likely_available"
        out.append({
            "name": getattr(template, "name", None) or alt.get("name") or "",
            "slug": getattr(template, "slug", None),
            "score": alt.get("score"),
            "zone_label": limiting["label"] if by_recovery else None,
            "zone_band": limiting["band"] if by_recovery else None,
            "zone_short": limiting["band_short"] if by_recovery else None,
            "reason_is_recovery": by_recovery,
        })
    return out


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: DbSession, user: CurrentUser) -> HTMLResponse:
    from datetime import datetime, timedelta

    from app.services.performance import compute_composite_score
    from app.services.timeline import build_sparkline_svg

    open_session = latest_open_session(db, user.id)
    # Bound once: the badge needs both the recommendation and its set count.
    _reco = _build_reco_context(db, user.id, open_session)
    open_since: str | None = None
    if open_session is not None:
        open_since = format_duration_short(
            session_duration(open_session.started_at, end=None)
        )

    # Board KPIs
    global_kpis = compute_global_kpis(db, user_id=user.id)

    # Sparkline: composite scores for last 14 days
    window_start = datetime.now(UTC) - timedelta(days=14)
    sparkline_stmt = (
        select(WorkoutSession)
        .where(WorkoutSession.user_id == user.id)
        .where(WorkoutSession.status == "completed")
        .where(WorkoutSession.excluded_from_stats.is_(False))
        .where(WorkoutSession.started_at >= window_start)
        .order_by(WorkoutSession.started_at.asc())
        .options(
            selectinload(WorkoutSession.session_exercises)
            .selectinload(SessionExercise.set_logs)
        )
    )
    recent_sessions = list(db.execute(sparkline_stmt).scalars().all())

    from app.services.quality_score import session_kind as _session_kind
    sparkline_points = []
    sparkline_kinds: list[str | None] = []
    for s in recent_sessions:
        quality = compute_session_quality(s)
        total_work = sum(
            1 for se in s.session_exercises
            for sl in se.set_logs if sl.kind == "work"
        )
        done_work = sum(
            1 for se in s.session_exercises
            for sl in se.set_logs if sl.kind == "work" and sl.completed
        )
        cr = done_work / total_work if total_work > 0 else 0.0
        composite = compute_composite_score(quality, cr)
        sparkline_points.append((composite,))
        sparkline_kinds.append(_session_kind(s))

    sparkline_svg = build_sparkline_svg(sparkline_points, kinds=sparkline_kinds)
    # Sb_10 G1 — show the kind legend on the home sparkline only when
    # the 14-day window actually mixes strength and cardio sessions,
    # otherwise it adds noise.
    sparkline_has_mixed_kinds = (
        "strength" in sparkline_kinds and "cardio" in sparkline_kinds
    )

    from app.services.behavioral import compute_behavioral_state

    behavioral = compute_behavioral_state(db, user.id)

    from app.services.readiness import (
        READINESS_FIELD_LABELS,
        READINESS_LABELS,
        SCALE_FIELDS,
        get_today_readiness,
    )
    readiness_today = get_today_readiness(db, user.id)

    # Sb_27.1 — coaching loop home payload. Composed read-only on top of
    # existing services (recommendation, quality_score, session columns).
    # Never touches scoring core or persists state.
    from app.services.home import build_home_payload

    home_payload = build_home_payload(db, user)

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "page_title": "Accueil",
            "open_session": open_session,
            "open_since": open_since,
            "kpis": global_kpis,
            "sparkline_svg": sparkline_svg,
            "sparkline_has_mixed_kinds": sparkline_has_mixed_kinds,
            "reco": _reco,
            # D2 — volume shown beside the badge. None when there is no
            # recommendation; the template then omits the figure rather than
            # printing a zero it did not measure.
            "reco_top_sets": (
                _template_work_set_count(db, _reco["top"]["template"].id)
                if _reco and _reco.get("top") else None
            ),
            # D6 — pourquoi CETTE séance : l'état des zones qu'elle vise.
            "reco_zone_state": (
                _reco_zone_state(db, user.id, _reco["top"].get("primary_zones"))
                if _reco and _reco.get("top") else []
            ),
            # `Sx_UIV3_01` — la cause, le bilan 11 zones et les options
            # écartées. Une seule lecture de `zone_recovery` pour les trois.
            "causal": _home_causal_context(db, user.id, _reco),
            "behavioral": behavioral,
            "readiness_today": readiness_today,
            "readiness_labels": READINESS_LABELS,
            "readiness_field_labels": READINESS_FIELD_LABELS,
            "readiness_scale_fields": SCALE_FIELDS,
            "home": home_payload,
        },
    )


@router.get("/launcher", response_class=HTMLResponse, name="launcher")
def launcher(
    request: Request,
    db: DbSession,
    user: CurrentUser,
    type: str | None = Query(None),
    variant: str | None = Query(None),
) -> HTMLResponse:
    active_session = latest_open_session(db, user.id)

    # Step 1: no type, or invalid type → list types.
    if type is None or type not in BRANCH_TREE:
        types = get_available_types(db)
        return templates.TemplateResponse(
            request,
            "launcher.html",
            {
                "page_title": "Nouvelle séance",
                "step": 1,
                "types": types,
                "active_session": active_session,
                "reco": _build_reco_context(db, user.id, active_session),
            },
        )

    type_key = type
    type_label = TYPE_LABELS.get(type_key, type_key)
    type_branches = BRANCH_TREE[type_key]

    # Direct type (e.g., cardio): jump to step 3.
    if variant is None and "_direct" in type_branches:
        templates_list = resolve_branch(db, type_key, None)
        if templates_list:
            return templates.TemplateResponse(
                request,
                "launcher.html",
                {
                    "page_title": "Nouvelle séance",
                    "step": 3,
                    "type_key": type_key,
                    "type_label": type_label,
                    "templates_list": templates_list,
                    "active_session": active_session,
                },
            )
        # Fall through to step 1 if direct branch is empty.
        types = get_available_types(db)
        return templates.TemplateResponse(
            request,
            "launcher.html",
            {
                "page_title": "Nouvelle séance",
                "step": 1,
                "types": types,
                "active_session": active_session,
            },
        )

    # Step 2: type, no variant → list variants.
    if variant is None:
        variants = get_available_variants(db, type_key)
        return templates.TemplateResponse(
            request,
            "launcher.html",
            {
                "page_title": "Nouvelle séance",
                "step": 2,
                "type_key": type_key,
                "type_label": type_label,
                "variants": variants,
                "active_session": active_session,
            },
        )

    # Step 3: type + variant → list templates.
    templates_list = resolve_branch(db, type_key, variant)
    if not templates_list:
        # Invalid/empty variant → fall back to step 2.
        variants = get_available_variants(db, type_key)
        return templates.TemplateResponse(
            request,
            "launcher.html",
            {
                "page_title": "Nouvelle séance",
                "step": 2,
                "type_key": type_key,
                "type_label": type_label,
                "variants": variants,
                "active_session": active_session,
            },
        )

    return templates.TemplateResponse(
        request,
        "launcher.html",
        {
            "page_title": "Nouvelle séance",
            "step": 3,
            "type_key": type_key,
            "type_label": type_label,
            "templates_list": templates_list,
            "active_session": active_session,
        },
    )


@router.get("/library", response_class=HTMLResponse)
def library(request: Request, db: DbSession, user: CurrentUser) -> HTMLResponse:
    all_templates = _load_templates(db)
    # Group templates by catalog_section for display
    grouped: dict[str, list] = {}
    for tpl in all_templates:
        section = getattr(tpl, "catalog_section", "core")
        if section in ("archived", "user"):
            # archived: retired from the catalog. user: published custom
            # programs (PUBLICATION_01) — owner-private, they live under
            # "Mes programmes", never in the shared library.
            continue
        grouped.setdefault(section, []).append(tpl)
    return templates.TemplateResponse(
        request,
        "library.html",
        {
            "page_title": "Programmes de séance",
            "sections": CATALOG_SECTIONS,
            "grouped": grouped,
            "active_session": latest_open_session(db, user.id),
        },
    )


@router.get("/library/{slug}", response_class=HTMLResponse)
def template_detail(
    slug: str, request: Request, db: DbSession, user: CurrentUser
) -> HTMLResponse:
    stmt = (
        select(WorkoutTemplate)
        .where(WorkoutTemplate.slug == slug)
        .options(
            selectinload(WorkoutTemplate.exercises).selectinload(
                TemplateExercise.rep_targets
            )
        )
    )
    tpl = db.execute(stmt).scalar_one_or_none()
    if tpl is None or tpl.catalog_section == "user":
        # A published custom program (catalog_section "user", PUBLICATION_01) is
        # not part of the shared catalog — it must not be reachable by slug here.
        raise HTTPException(status_code=404, detail="Template not found")
    return templates.TemplateResponse(
        request,
        "template_detail.html",
        {
            "page_title": tpl.name,
            "template": tpl,
            "active_session": latest_open_session(db, user.id),
        },
    )


_HISTORY_STATUS_CHOICES = ("all", "in_progress", "completed")


@router.get("/history", response_class=HTMLResponse)
def history(
    request: Request,
    db: DbSession,
    user: CurrentUser,
    status: str = Query("all"),
) -> HTMLResponse:
    status = status if status in _HISTORY_STATUS_CHOICES else "all"

    stmt = (
        select(WorkoutSession)
        .where(WorkoutSession.user_id == user.id)
        .order_by(WorkoutSession.started_at.desc())
        .limit(100)
    )
    if status != "all":
        stmt = stmt.where(WorkoutSession.status == status)

    sessions = list(db.execute(stmt).scalars().all())

    # Per-session counts of exercise cards and "done" cards.
    # A card is "done" if it has at least one work set and every work
    # set has `completed=True`. We compute it all in Python so we stay
    # portable across SQLite and PostgreSQL without dialect-specific
    # aggregates.
    session_stats: dict[int, dict] = {}
    if sessions:
        sids = [s.id for s in sessions]
        work_rows = db.execute(
            select(
                SessionExercise.id,
                SessionExercise.session_id,
                SetLog.kind,
                SetLog.completed,
            )
            .join(SetLog, SetLog.session_exercise_id == SessionExercise.id, isouter=True)
            .where(SessionExercise.session_id.in_(sids))
        ).all()

        # { session_id: { exercise_id: [ (kind, completed), ... ] } }
        grouped: dict[int, dict[int, list[tuple]]] = {}
        for se_id, sid_, kind, completed in work_rows:
            grouped.setdefault(sid_, {}).setdefault(se_id, []).append((kind, completed))

        for s in sessions:
            exercises = grouped.get(s.id, {})
            total = len(exercises)
            done = 0
            for _, sl_list in exercises.items():
                work_sets = [c for k, c in sl_list if k == "work"]
                if work_sets and all(work_sets):
                    done += 1
            session_stats[s.id] = {"total": total, "done": done}

    # Per-session duration string (unused for empty history list).
    durations: dict[int, str] = {}
    for s in sessions:
        durations[s.id] = format_duration_short(
            session_duration(s.started_at, end=s.ended_at)
        )

    return templates.TemplateResponse(
        request,
        "history.html",
        {
            "page_title": "Historique",
            "sessions": sessions,
            "session_stats": session_stats,
            "durations": durations,
            "status_filter": status,
            "status_choices": _HISTORY_STATUS_CHOICES,
            "active_session": latest_open_session(db, user.id),
        },
    )


@router.get("/progress", response_class=HTMLResponse)
def progress(request: Request, db: DbSession, user: CurrentUser) -> HTMLResponse:
    global_kpis = compute_global_kpis(db, user_id=user.id)
    template_kpis = compute_template_kpis(db, user_id=user.id)
    recent_activity = compute_recent_exercise_activity(db, limit=10, user_id=user.id)

    # Sprint 8: build quality + bodyweight timeline SVGs from
    # completed non-excluded sessions, oldest first.
    timeline_stmt = (
        select(WorkoutSession)
        .where(WorkoutSession.user_id == user.id)
        .where(WorkoutSession.status == "completed")
        .where(WorkoutSession.excluded_from_stats.is_(False))
        .order_by(WorkoutSession.started_at.asc())
        .options(
            selectinload(WorkoutSession.session_exercises)
            .selectinload(SessionExercise.set_logs)
        )
    )
    eligible = list(db.execute(timeline_stmt).scalars().all())

    from app.services.quality_score import session_kind as _session_kind
    quality_points = [
        TimelinePoint(
            label=s.started_at.strftime("%d/%m"),
            value=compute_session_quality(s),
            kind=_session_kind(s),
        )
        for s in eligible
    ]
    bw_points = [
        TimelinePoint(
            label=s.started_at.strftime("%d/%m"),
            value=s.bodyweight_kg,
        )
        for s in eligible
        if s.bodyweight_kg is not None
    ]

    quality_svg = build_quality_timeline_svg(quality_points)
    bodyweight_svg = build_bodyweight_timeline_svg(bw_points)

    # Sb_27.3 — weekly training loop tile at the top of /progress (OQ-1
    # tranchée : enrichir /progress, pas de nouvelle route). Composed
    # read-only on top of existing services (anomalies, model columns).
    from app.services.weekly_loop import build_weekly_loop

    weekly = build_weekly_loop(db, user)

    # `UX4_03` — les trois signaux comportementaux existaient, calculés, et
    # n'étaient rendus NULLE PART : `/progress` annonçait « la régularité »
    # dans son chapeau sans jamais l'afficher, et `UX4_01` les a retirés du
    # Profil parce qu'ils y répondaient à la mauvaise question.
    #
    # COMPOSITION EN LECTURE SEULE. `compute_behavioral_state` est le même
    # service que consomme l'accueil : aucun calcul nouveau, aucun modèle,
    # aucune migration. On branche une valeur déjà produite sur la surface qui
    # la promettait.
    # `UX4_03B` — le gabarit ne reçoit ni l'état comportemental, ni les faits :
    # il reçoit la vue-modèle. L'audit `UX4_03A` a montré que trois champs de
    # `BehavioralState` ne sont pas présentables tels quels — `fatigue_score`
    # rend 45,0 pour une ABSENCE de déclaration, `consistency_score` pose une
    # séance par jour comme le 100 %, et `trend_direction` rend « stable » pour
    # 0 séance contre 0. Ne pas les passer au gabarit rend la correction
    # STRUCTURELLE : aucun changement de libellé ne peut les ramener.
    #
    # `compute_behavioral_state` n'est plus appelé ici. `progress_facts` lit les
    # faits — des comptages et une déclaration recopiée — sans passer par un
    # moteur de décision, que `test_no_decision_engine_was_touched` gèle depuis
    # `e8614bd` précisément pour que la présentation n'y touche pas.
    from app.services.progress_facts import build_progress_facts
    from app.services.progress_signals import (
        build_progress_rail,
        build_progress_signals,
        build_rail_days,
        build_rail_summary,
        has_any_trace,
    )
    from app.services.zone_exposure import (
        build_zone_exposure,
        build_zone_exposure_view,
    )

    facts = build_progress_facts(db, user.id)
    signals = build_progress_signals(facts)
    rail = build_progress_rail(facts)
    rail_summary = build_rail_summary(facts)
    # `TRAIN1-A` / A5 — le niveau 2 du rail, rendu côté serveur. Pas de route
    # jour : une projection locale des mêmes `facts.days`, qui renvoie vers la
    # surface de séance déjà existante quand il y en a une.
    rail_days = build_rail_days(facts)
    # `TRAIN1-A` / A4 — l'instrument ou sa forme compacte. Le gabarit n'a pas à
    # redécider ce que le service sait déjà.
    has_traces = has_any_trace(facts)

    # `TRAIN1-B` / A10 — L'INSTRUMENT PROGRESSIF.
    #
    # Identité analytique = celle d'`A1`, pas `(gabarit, code)`. Mesuré sur le
    # catalogue : 106 identités héritées pour 68 exercices réels, et
    # `Leg extensions assises` vit dans 4 gabarits sous 3 codes différents.
    # Le gabarit devient une PROVENANCE.
    #
    # Le cardio est une voie SÉPARÉE, au niveau séance : ses données vivent sur
    # `WorkoutSession`, pas sur `SessionExercise`, et il n'a ni série ni charge.
    from app.services.cardio_lane import build_cardio_facts
    from app.services.progression_facts import build_progression_facts
    from app.services.progression_view import (
        build_cardio_view,
        build_progression_view,
    )

    progression = build_progression_view(build_progression_facts(db, user.id))
    cardio = build_cardio_view(build_cardio_facts(db, user.id))

    # `TRAIN1-A` / A11 — LA DOMINANCE HEBDOMADAIRE REJOINT « PAR PROGRAMME ».
    #
    # Deux blocs disaient le même fait sur deux fenêtres : « Séances
    # dominantes · cette semaine » dans `weekly_loop`, et « Par programme ·
    # historique » plus bas. `UX4_03D` avait rendu les deux fenêtres
    # explicites — le moins cher des correctifs — sans supprimer la seconde
    # lecture. Une seule liste, deux colonnes : aucun fait perdu, un bloc et
    # une carte de moins.
    _this_week = {
        t["name"]: t["count"] for t in (weekly.get("dominant_templates") or [])
    }
    for tk in template_kpis:
        tk.week_count = _this_week.get(tk.name, 0)

    # `UX4_03D` — « où ai-je travaillé pendant les MÊMES quatorze jours ? ».
    # Même fenêtre que le rail : deux instruments côte à côte sur des fenêtres
    # différentes rouvriraient la contradiction que l'écrémage a fermée.
    exposure = build_zone_exposure_view(build_zone_exposure(db, user.id))

    return templates.TemplateResponse(
        request,
        "progress.html",
        {
            "page_title": "Progression",
            "kpis": global_kpis,
            "template_kpis": template_kpis,
            "recent_activity": recent_activity,
            "quality_svg": quality_svg,
            "bodyweight_svg": bodyweight_svg,
            "active_session": latest_open_session(db, user.id),
            # `TRAIN1-A` / A11 — LE CONTENEUR `weekly_loop` EST RETIRÉ.
            #
            # Il rendait trois cartes en tête de Progression, dont deux
            # duplications mesurées : « 3 séances cette semaine » et « Semaine
            # précédente : 2 (+1) » répétaient ce que la ligne « Séances » et
            # les quatorze cellules du rail disent déjà — c'est exactement la
            # cadence qu'`UX4_03D` déclarait absorbée par le rail, et qui
            # survivait ici. Sur un compte vide, la même phrase « Pas encore
            # assez de données cette semaine » s'affichait DEUX FOIS dans la
            # même carte.
            #
            # Les producteurs ne sont pas supprimés : `build_weekly_loop` reste
            # appelé, et ses deux faits UNIQUES sont absorbés — l'anomalie
            # ci-dessous, la dominance hebdomadaire dans « Par programme ».
            "top_anomaly": weekly.get("top_anomaly"),
            "signals": signals,
            "rail": rail,
            "rail_summary": rail_summary,
            "rail_days": rail_days,
            "has_traces": has_traces,
            "exposure": exposure,
            "progression": progression,
            "cardio": cardio,
        },
    )


@router.get("/physique", response_class=HTMLResponse)
def physique(
    request: Request,
    db: DbSession,
    user: CurrentUser,
    window: int = Query(30),
) -> HTMLResponse:
    from app.services.muscle_scoring import compute_physique_dashboard

    window = window if window in (30, 60, 90) else 30
    dashboard = compute_physique_dashboard(db, user.id, window_days=window)

    return templates.TemplateResponse(
        request,
        "physique.html",
        {
            "page_title": "Physique",
            "dashboard": dashboard,
            "window": window,
            "active_session": latest_open_session(db, user.id),
            # Sb_BI_01.3 — the guardrail link to /body/intelligence is only
            # shown when the surface actually exists (flag ON), never a dead
            # 404 link. The physique score/grade/radar and the shared
            # compute_physique_dashboard service are left untouched.
            "body_intelligence_enabled": get_settings().body_intelligence_enabled,
        },
    )


@router.get("/dashboard", response_model=None)
def dashboard(
    request: Request,
    db: DbSession,
    user: CurrentUser,
    window: int = Query(30),
) -> RedirectResponse:
    """Sb_27.6 — DEPRECATED. OQ-3 tranchée verbatim user : `/dashboard`
    n'est plus une surface principale. Redirige vers `/` (Home coaching).

    Le template `dashboard.html` et le service `compute_dashboard` sont
    volontairement préservés (pas de suppression brutale de code métier)
    pour permettre une réintroduction future si nécessaire — mais aucun
    lien n'y pointe désormais depuis la navigation.

    Le paramètre `window` est ignoré pendant la redirection ; il restera
    accepté tant que d'éventuels bookmarks externes existent.
    """
    return RedirectResponse(url="/", status_code=303)


@router.get("/readiness/history", response_class=HTMLResponse)
def readiness_history(
    request: Request, db: DbSession, user: CurrentUser
) -> HTMLResponse:
    from app.services.readiness import (
        READINESS_FIELD_LABELS,
        READINESS_LABELS,
        SCALE_FIELDS,
        get_readiness_history,
    )
    entries = get_readiness_history(db, user.id, days=90)
    return templates.TemplateResponse(
        request,
        "readiness_history.html",
        {
            "page_title": "Historique Readiness",
            "entries": entries,
            "readiness_labels": READINESS_LABELS,
            "readiness_field_labels": READINESS_FIELD_LABELS,
            "readiness_scale_fields": SCALE_FIELDS,
        },
    )
