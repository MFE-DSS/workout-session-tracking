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
            "weekly": weekly,
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
