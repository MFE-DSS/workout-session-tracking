"""Authentication + account lifecycle routes.

Public: /welcome, /login, /register
Private: /logout, /profile, /profile/password
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.config import get_settings
from app.deps import CurrentUser, DbSession
from app.models.session import SessionExercise, WorkoutSession
from app.models.user import User
from app.services.auth import (
    clear_session_cookie,
    create_reset_token,
    create_session_cookie,
    get_current_user,
    hash_password,
    verify_password,
    verify_reset_token,
)
from app.services.email import send_email
from app.services.password_policy import (
    TOO_LONG_MESSAGE,
    is_password_too_long,
    validate_password_policy,
)
from app.services.quality_score import compute_session_quality
from app.services.session_state import latest_open_session
from app.services.timeline import TimelinePoint, build_quality_timeline_svg
from app.templating import templates

router = APIRouter(tags=["auth"])

# Sb_20.3 — hardening thresholds. Password 4 → 8 chars (OWASP basic).
# Existing accounts unaffected — the threshold only applies to
# registration and password-change flows.
MIN_PASSWORD_LENGTH = 8
MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 64

# Sb_AUTH_PASSWORD_LENGTH_01 — the login view is rendered from three branches
# (over-long password, bad credentials, and the GET page). Naming it once keeps
# them from drifting apart.
LOGIN_TEMPLATE = "login.html"

# Sb_20.3 — username regex: alphanumeric + underscore + dash only.
# Mirrors the path-param regex on /users/{username} so the public
# profile route never has to deal with surprising characters.
import re as _re

USERNAME_REGEX = _re.compile(r"^[a-zA-Z0-9_-]+$")

# Sb_20.3 — email regex (basic but strict). Replaces the prior loose
# check `"@" in email` + dot in domain. Not RFC 5322 — production
# email validation should ride on real send (DNS, SMTP) — but this
# rejects obviously invalid inputs at registration time.
EMAIL_REGEX = _re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ---------------------------------------------------------------------------
# Public
# ---------------------------------------------------------------------------


@router.get("/welcome", response_class=HTMLResponse)
def public_landing(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "welcome.html", {"page_title": "Bienvenue"},
    )


@router.get("/login", response_class=HTMLResponse)
def login_page(
    request: Request,
    db: DbSession,
    success: str | None = None,
) -> HTMLResponse:
    user = get_current_user(request, db)
    if user is not None:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        request,
        LOGIN_TEMPLATE,
        {
            "page_title": "Connexion",
            "error": None,
            "success": success,
        },
    )


@router.post("/login", response_model=None)
async def login_submit(
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db: DbSession,
):
    # Sb_AUTH_PASSWORD_LENGTH_01 — reject an over-long password BEFORE touching
    # the database or bcrypt. Under bcrypt 5 the verify below raises past 72
    # bytes, which would turn a bad input into a 500. Only the MAXIMUM is
    # enforced here: a minimum check at login would lock out accounts created
    # before the floor was raised, and would say something about stored
    # credentials. This early return leaks nothing — it depends solely on the
    # length of the attacker's own input, never on whether the account exists.
    if is_password_too_long(password):
        return templates.TemplateResponse(
            request,
            LOGIN_TEMPLATE,
            {"page_title": "Connexion", "error": TOO_LONG_MESSAGE, "success": None},
            status_code=400,
        )

    user = db.execute(
        select(User).where(User.username == username, User.is_active.is_(True))
    ).scalar_one_or_none()

    # Constant-time: always run bcrypt even if user is None, so the
    # response timing doesn't leak whether the username exists.
    # The dummy hash is a real bcrypt hash of "dummy" — passlib will
    # run the full comparison against it and return False.
    _DUMMY = "$2b$12$LJ3m4ys3Lg3mRIkFLfTMD.ue1tjUTO7ZzNzm3Lf0QLjHEjLN2yJXi"
    pw_ok = verify_password(password, user.password_hash if user else _DUMMY)

    if user is None or not pw_ok:
        return templates.TemplateResponse(
            request,
            LOGIN_TEMPLATE,
            {"page_title": "Connexion", "error": "Identifiants invalides.", "success": None},
            status_code=401,
        )

    response = RedirectResponse(url="/", status_code=303)
    create_session_cookie(response, user.id)
    return response


@router.post("/logout")
def logout(request: Request) -> RedirectResponse:
    response = RedirectResponse(url="/welcome", status_code=303)
    clear_session_cookie(response)
    return response


# ---------------------------------------------------------------------------
# Password reset (public)
# ---------------------------------------------------------------------------


@router.get("/forgot-password", response_class=HTMLResponse)
def forgot_password_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "forgot_password.html",
        {"page_title": "Mot de passe oublié", "error": None, "success": False},
    )


@router.post("/forgot-password", response_class=HTMLResponse)
async def forgot_password_submit(
    request: Request,
    email: Annotated[str, Form()],
    db: DbSession,
) -> HTMLResponse:
    email_clean = email.strip().lower()
    if email_clean:
        user = db.execute(
            select(User).where(User.email == email_clean)
        ).scalar_one_or_none()
        if user is not None:
            token = create_reset_token(user.id)
            settings = get_settings()
            reset_url = f"{settings.app_base_url}/reset/{token}"
            send_email(
                to=user.email,
                subject="SPIGNOS \u2014 R\u00e9initialisation de mot de passe",
                body=(
                    f"Bonjour,\n\n"
                    f"Une demande de r\u00e9initialisation de mot de passe a \u00e9t\u00e9 faite "
                    f"pour votre compte SPIGNOS.\n\n"
                    f"Cliquez sur ce lien pour choisir un nouveau mot de passe "
                    f"(valide 1 heure) :\n{reset_url}\n\n"
                    f"Si vous n'avez pas fait cette demande, ignorez cet email.\n\n"
                    f"\u2014 SPIGNOS"
                ),
            )
    return templates.TemplateResponse(
        request, "forgot_password.html",
        {"page_title": "Mot de passe oublié", "error": None, "success": True},
    )


@router.get("/reset/{token}", response_class=HTMLResponse)
def reset_password_page(token: str, request: Request) -> HTMLResponse:
    user_id = verify_reset_token(token)
    return templates.TemplateResponse(
        request, "reset_password.html",
        {
            "page_title": "R\u00e9initialiser le mot de passe",
            "token": token,
            "valid": user_id is not None,
            "error": None,
        },
    )


@router.post("/reset/{token}", response_model=None)
async def reset_password_submit(
    token: str,
    request: Request,
    new_password: Annotated[str, Form()],
    new_password_confirm: Annotated[str, Form()],
    db: DbSession,
):
    user_id = verify_reset_token(token)
    if user_id is None:
        return templates.TemplateResponse(
            request, "reset_password.html",
            {
                "page_title": "R\u00e9initialiser le mot de passe",
                "token": token, "valid": False,
                "error": "Ce lien a expir\u00e9 ou est invalide.",
            },
            status_code=400,
        )

    error = validate_password_policy(new_password)
    if error is None and new_password != new_password_confirm:
        error = "Les mots de passe ne correspondent pas."

    if error:
        return templates.TemplateResponse(
            request, "reset_password.html",
            {
                "page_title": "R\u00e9initialiser le mot de passe",
                "token": token, "valid": True, "error": error,
            },
            status_code=400,
        )

    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        return templates.TemplateResponse(
            request, "reset_password.html",
            {
                "page_title": "R\u00e9initialiser le mot de passe",
                "token": token, "valid": False,
                "error": "Utilisateur introuvable.",
            },
            status_code=400,
        )

    user.password_hash = hash_password(new_password)
    db.commit()
    return RedirectResponse(url="/login?success=password_reset", status_code=303)


# ---------------------------------------------------------------------------
# Registration (public)
# ---------------------------------------------------------------------------


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request, db: DbSession) -> HTMLResponse:
    user = get_current_user(request, db)
    if user is not None:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        request, "register.html",
        {"page_title": "Inscription", "error": None},
    )


@router.post("/register", response_model=None)
async def register_submit(
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    password_confirm: Annotated[str, Form()],
    email: Annotated[str, Form()] = "",
    db: DbSession = None,
):
    error = None
    username_clean = username.strip()
    # Sb_AUTH_PASSWORD_LENGTH_01 — one call, evaluated before the chain so the
    # policy cannot be reached twice or skipped by a reordering.
    password_error = validate_password_policy(password)
    if len(username_clean) < MIN_USERNAME_LENGTH:
        error = f"Le nom d'utilisateur doit faire au moins {MIN_USERNAME_LENGTH} caractères."
    elif len(username_clean) > MAX_USERNAME_LENGTH:
        error = f"Le nom d'utilisateur dépasse {MAX_USERNAME_LENGTH} caractères."
    elif not USERNAME_REGEX.match(username_clean):
        # Sb_20.3 — explicit allowlist (CWE-20). Rejects unicode,
        # punctuation, spaces — only [a-zA-Z0-9_-] survive.
        error = "Le nom d'utilisateur ne peut contenir que des lettres, chiffres, _ et -."
    elif password_error is not None:
        error = password_error
    elif password != password_confirm:
        error = "Les mots de passe ne correspondent pas."
    else:
        existing = db.execute(
            select(User).where(User.username == username_clean)
        ).scalar_one_or_none()
        if existing is not None:
            error = "Ce nom d'utilisateur est déjà pris."

    # Email validation (only if provided) — Sb_20.3 strict regex.
    email_clean = email.strip().lower() if email.strip() else None
    if error is None and email_clean:
        if not EMAIL_REGEX.match(email_clean):
            error = "Adresse email invalide."
        else:
            email_exists = db.execute(
                select(User).where(User.email == email_clean)
            ).scalar_one_or_none()
            if email_exists is not None:
                error = "Cet email est déjà associé à un compte."

    if error:
        return templates.TemplateResponse(
            request, "register.html",
            {"page_title": "Inscription", "error": error},
            status_code=400,
        )

    user = User(
        username=username_clean,
        password_hash=hash_password(password),
        email=email_clean,
    )
    db.add(user)
    db.commit()

    # Auto-login after registration.
    response = RedirectResponse(url="/", status_code=303)
    create_session_cookie(response, user.id)
    return response


# ---------------------------------------------------------------------------
# Profile (private)
# ---------------------------------------------------------------------------


@router.get("/profile", response_class=HTMLResponse)
def profile_page(
    request: Request,
    db: DbSession,
    user: CurrentUser,
) -> HTMLResponse:
    session_count = db.execute(
        select(func.count(WorkoutSession.id))
        .where(WorkoutSession.user_id == user.id)
    ).scalar_one() or 0
    completed_count = db.execute(
        select(func.count(WorkoutSession.id))
        .where(WorkoutSession.user_id == user.id)
        .where(WorkoutSession.status == "completed")
    ).scalar_one() or 0

    # 30-day quality timeline
    now = datetime.now(UTC)
    window_30 = now - timedelta(days=30)
    window_60 = now - timedelta(days=60)

    sessions_30d = db.execute(
        select(WorkoutSession)
        .where(WorkoutSession.user_id == user.id)
        .where(WorkoutSession.status == "completed")
        .where(WorkoutSession.excluded_from_stats.is_(False))
        .where(WorkoutSession.started_at >= window_30)
        .order_by(WorkoutSession.started_at.asc())
        .options(
            selectinload(WorkoutSession.session_exercises)
            .selectinload(SessionExercise.set_logs)
        )
    ).scalars().all()

    from app.services.quality_score import session_kind as _session_kind
    quality_points = [
        TimelinePoint(
            label=s.started_at.strftime("%d/%m"),
            value=compute_session_quality(s),
            kind=_session_kind(s),
        )
        for s in sessions_30d
    ]
    quality_svg = build_quality_timeline_svg(quality_points)
    sessions_30d_count = len(sessions_30d)

    # Trend: compare 30d count vs previous 30d
    prev_30d_count = db.execute(
        select(func.count(WorkoutSession.id))
        .where(WorkoutSession.user_id == user.id)
        .where(WorkoutSession.status == "completed")
        .where(WorkoutSession.excluded_from_stats.is_(False))
        .where(WorkoutSession.started_at >= window_60)
        .where(WorkoutSession.started_at < window_30)
    ).scalar_one() or 0

    if sessions_30d_count > prev_30d_count:
        trend = "up"
        trend_label = "\u2191 en hausse"
    elif sessions_30d_count < prev_30d_count:
        trend = "down"
        trend_label = "\u2193 en baisse"
    else:
        trend = "stable"
        trend_label = "\u2192 stable"

    # `UX4_03B` — L'ÉTAT COMPORTEMENTAL N'EST PLUS CALCULÉ ICI.
    #
    # `UX4_01` a retiré les modules analytiques du Profil sans retirer le calcul
    # qui les alimentait. Le gabarit ne lisait plus aucun champ de `behavioral`,
    # mais chaque affichage du Profil exécutait quand même les requêtes du
    # moteur — dont un chargement des trois dernières séances avec leurs séries.
    #
    # Ce n'était pas seulement du coût : c'était le dernier chemin par lequel
    # `readiness_score` — un composite dont 100 % de la valeur vient d'un défaut
    # quand le compte est vide — pouvait ressortir à l'écran par un simple
    # accès d'attribut depuis le gabarit. Couper l'alimentation ferme le risque
    # sans toucher au moteur, qui est gelé.
    from app.models.catalog import WorkoutTemplate

    # Body measurements.
    #
    # Sb_MORPHO_PROFILE_RUNTIME_01 — capture and display are deliberately two
    # different field sets, because they answer two different questions.
    #
    # `capture_fields` is the canonical writer's whitelist: exactly what this
    # form is allowed to persist. Rendering the form from anything else would
    # let it post a key the writer silently ignores.
    #
    # `MEASUREMENT_FIELDS` stays the *display* set for charts and history, and
    # it still contains the legacy `calf_cm`. New entries no longer write that
    # column, but users who have years of it must keep seeing their curve —
    # "historical data remains readable exactly as it is".
    from app.services import body_profile as bp
    from app.services.measurements import (
        MEASUREMENT_FIELDS,
        MEASUREMENT_LABELS,
        MEASUREMENT_UNITS,
        find_related_templates,
        get_latest_measurement,
        get_measurement_series,
    )
    from app.services.timeline import build_measurement_timeline_svg

    capture_fields = [(s.key, s.label) for s in bp.BODY_MEASUREMENT_FIELDS]

    # Sb_MORPHO_PROFILE_READMODEL_01 — read-only. Owner-scoped like every other
    # read on this page; no planner consumer reads this value.
    from app.services.morphology_readmodel import build_morphology_readmodel

    morpho = build_morphology_readmodel(db, user.id)

    latest_measurement = get_latest_measurement(db, user.id)
    latest_values: dict[str, str] = {}
    if latest_measurement:
        for field in {*MEASUREMENT_FIELDS, *(k for k, _ in capture_fields)}:
            val = getattr(latest_measurement, field, None)
            latest_values[field] = str(val) if val is not None else ""

    # Build per-field SVG charts
    measurement_charts: dict[str, str] = {}
    for field in MEASUREMENT_FIELDS:
        series = get_measurement_series(db, user.id, field)
        points = [
            TimelinePoint(label=dt.strftime("%d/%m"), value=val)
            for dt, val in series
        ]
        measurement_charts[field] = build_measurement_timeline_svg(
            points, title=MEASUREMENT_LABELS[field],
            unit=MEASUREMENT_UNITS.get(field, ""),
        )

    # Related templates per field
    all_templates = list(db.execute(
        select(WorkoutTemplate).order_by(WorkoutTemplate.slug)
    ).scalars().all())
    related_templates: dict[str, list[str]] = {
        field: find_related_templates(field, all_templates)
        for field in MEASUREMENT_FIELDS
    }

    return templates.TemplateResponse(
        request, "profile.html",
        {
            "page_title": "Profil",
            "user": user,
            # `UX4_02` / TRAIN 2 — `preferences` et ses trois vocabulaires ont
            # suivi l'éditeur vers `/plan`. Ils n'alimentaient que lui : le
            # gabarit du Profil n'en lit plus une seule occurrence. Les laisser
            # aurait coûté une requête par affichage du Profil, pour rien.
            "measure_saved": request.query_params.get("measure_saved") == "1",
            "measure_error": request.query_params.get("measure_error") == "1",
            "capture_fields": capture_fields,
            "morpho": morpho,
            "session_count": session_count,
            "completed_count": completed_count,
            "quality_svg": quality_svg,
            "sessions_30d_count": sessions_30d_count,
            "trend": trend,
            "trend_label": trend_label,
            "latest_values": latest_values,
            "measurement_charts": measurement_charts,
            "measurement_labels": MEASUREMENT_LABELS,
            "measurement_fields": MEASUREMENT_FIELDS,
            "related_templates": related_templates,
            "active_session": latest_open_session(db, user.id),
            # Sb_31.X — gate the Body Intelligence v2 discovery link.
            "body_intelligence_enabled": get_settings().body_intelligence_enabled,
        },
    )


@router.post("/profile/body", response_model=None)
async def profile_body_submit(
    request: Request,
    email: Annotated[str, Form()] = "",
    height_cm: Annotated[str, Form()] = "",
    resting_hr: Annotated[str, Form()] = "",
    db: DbSession = None,
    user: CurrentUser = None,
):
    """Save physical profile fields.

    `UX4_01` — **la tension artérielle n'est plus acquise ici**, et ce handler
    ne touche plus `bp_systolic` / `bp_diastolic`.

    Décision opérateur (`AUREN_UI_BLUEPRINT §5ter`) : `REMOVE_NO_ASK` de
    l'acquisition courante, **données existantes préservées**. La donnée
    traversait `providers.py` et `coach_report.py` jusqu'à un gabarit sans
    jamais atteindre `recommendation.py` ni `zone_recovery.py` — affichée,
    jamais décisionnelle.

    **Ne pas assigner est ce qui rend la préservation vraie.** Tant que le
    handler écrivait `user.bp_systolic = _int_or_none(bp_systolic)` avec un
    défaut de formulaire à `""`, **retirer le champ du gabarit suffisait à
    effacer la valeur stockée au prochain enregistrement** — le piège de
    sérialisation déjà payé sur la console de séance. Une garde le prouve en
    enregistrant, pas en le lisant.
    """
    def _int_or_none(v: str, lo: int, hi: int) -> int | None:
        v = v.strip()
        if not v:
            return None
        try:
            n = int(v)
        except ValueError:
            return None
        if n < lo or n > hi:
            return None
        return n

    user.height_cm = _int_or_none(height_cm, 100, 250)
    user.resting_hr = _int_or_none(resting_hr, 30, 220)

    email_clean = email.strip().lower() if email.strip() else None
    if email_clean:
        # Sb_20.3 — strict regex same as registration.
        if EMAIL_REGEX.match(email_clean):
            existing = db.execute(
                select(User).where(User.email == email_clean, User.id != user.id)
            ).scalar_one_or_none()
            if existing is None:
                user.email = email_clean
    elif not email.strip():
        user.email = None

    db.commit()

    return RedirectResponse(url="/profile", status_code=303)


@router.post("/profile/preferences", response_model=None)
async def profile_preferences_submit(
    request: Request,
    sessions_per_week: Annotated[str, Form()] = "",
    focus_1: Annotated[str, Form()] = "",
    focus_2: Annotated[str, Form()] = "",
    focus_3: Annotated[str, Form()] = "",
    equipment: Annotated[list[str], Form()] = None,
    equipment_declared: Annotated[str, Form()] = "",
    db: DbSession = None,
    user: CurrentUser = None,
):
    """Save declared training preferences (Sb_TRAINING_PREFERENCES_01).

    The owner is `CurrentUser`, resolved from the authenticated session — the
    form never carries a `user_id`, so a forged one cannot escape the owner
    scope. There is nothing to trust because nothing is read.

    **Nothing here invents a value.** An empty cadence field stays `None`; the
    equipment list is only stored when the hidden `equipment_declared` marker
    proves the section was actually submitted, which is what keeps "no
    declaration" distinguishable from "declared nothing available".
    """
    from app.services.training_preferences import (
        PreferenceValidationError,
        save_training_preferences,
    )

    cadence: int | None = None
    raw_cadence = sessions_per_week.strip()
    if raw_cadence:
        try:
            cadence = int(raw_cadence)
        except ValueError:
            return RedirectResponse(url="/plan?pref_error=1", status_code=303)

    ordered = [slot.strip() for slot in (focus_1, focus_2, focus_3) if slot.strip()]
    # An untouched priority section leaves all three selects empty. That is
    # "not declared" (None), not "explicitly no priority" ([]) — the two are
    # different statements and the contract keeps them apart.
    priorities: list[str] | None = ordered if ordered else None

    families: list[str] | None = None
    if equipment_declared.strip():
        families = list(equipment or [])

    try:
        save_training_preferences(
            db,
            user.id,
            sessions_per_week=cadence,
            focus_priorities=priorities,
            available_equipment=families,
        )
    except PreferenceValidationError:
        return RedirectResponse(url="/plan?pref_error=1", status_code=303)

    return RedirectResponse(url="/plan?pref_saved=1", status_code=303)


@router.post("/profile/measurements", response_model=None)
async def profile_measurements_submit(
    request: Request,
    db: DbSession = None,
    user: CurrentUser = None,
):
    """Save a body measurement entry by delegating to the canonical writer.

    Sb_MORPHO_PROFILE_RUNTIME_01 — this route used to be a second, independent
    writer on `body_measurements` (`Sx_MORPHO_CAPTURE_01_SPEC` §2). It kept its
    own inline bounds, its own whitelist-free parsing, and an **upsert-by-day**
    semantic, while `body_profile.create_measurement` treated the same table as
    an append-only series. Two writers, one table, two temporal contracts.

    It now delegates. Three behaviours change, deliberately:

    - **Append-only.** A second entry on an already-measured day creates a new
      dated row instead of overwriting the first. Correcting a measurement is
      adding a later fact, not rewriting the earlier one. Rows already written
      by the old upsert path stay exactly as they are — the change is
      prospective, nothing is migrated, merged or deleted.
    - **Bounds are enforced, not silently dropped.** The old parser turned an
      out-of-range value into `None`, so a mistyped `1750` cm simply vanished
      with a success redirect. The canonical validator rejects it and the user
      is told, which is the spec's `§6` rule against silent truncation.
    - **The legacy single `calf_cm` column is no longer written.** The canonical
      whitelist carries the lateralized `calf_cm_left/right`, and the model has
      documented them as the source of truth since Sb_Body_01. Historical
      `calf_cm` values remain readable and keep charting.

    Data quality rules kept from the previous implementation: a future date is
    capped to today, and a fully empty submission is a no-op rather than an
    error.
    """
    from app.services import body_profile as bp

    form = await request.form()

    # Parse date — fallback to today if empty/invalid.
    now = datetime.now(UTC)
    dt = now
    measured_at = (form.get("measured_at") or "").strip()
    if measured_at:
        try:
            dt = datetime.strptime(measured_at, "%Y-%m-%d").replace(
                tzinfo=UTC
            )
        except ValueError:
            pass

    # Cap future dates to today.
    if dt.date() > now.date():
        dt = now

    raw = {
        spec.key: (form.get(spec.key) or "")
        for spec in bp.BODY_MEASUREMENT_FIELDS
    }

    # A fully empty submission stays a no-op: `parse_and_validate` treats "no
    # field at all" as an error, which would turn an accidental empty submit
    # into a red banner. Preserved from the previous behaviour on purpose.
    if not any(v.strip() for v in raw.values()):
        return RedirectResponse(url="/profile", status_code=303)

    try:
        cleaned = bp.parse_and_validate(raw)
    except ValueError:
        return RedirectResponse(url="/profile?measure_error=1", status_code=303)

    bp.create_measurement(db, user.id, cleaned, measured_at=dt)

    return RedirectResponse(url="/profile?measure_saved=1", status_code=303)


# ---------------------------------------------------------------------------
# Password change (private)
# ---------------------------------------------------------------------------


@router.get("/profile/password", response_class=HTMLResponse)
def password_change_page(
    request: Request,
    user: CurrentUser,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "password_change.html",
        {"page_title": "Changer le mot de passe", "error": None, "success": False},
    )


@router.post("/profile/password", response_model=None)
async def password_change_submit(
    request: Request,
    current_password: Annotated[str, Form()],
    new_password: Annotated[str, Form()],
    new_password_confirm: Annotated[str, Form()],
    db: DbSession,
    user: CurrentUser,
):
    error = None
    # Sb_AUTH_PASSWORD_LENGTH_01 — the CURRENT password is checked against the
    # maximum too: it reaches bcrypt.verify, which under bcrypt 5 raises past
    # 72 bytes. Its minimum is NOT re-checked — an account created before the
    # floor was raised must still be able to authenticate to change it.
    current_error = validate_password_policy(current_password, check_minimum=False)
    new_error = validate_password_policy(
        new_password, field_label="Le nouveau mot de passe"
    )
    if current_error is not None:
        error = current_error
    elif not verify_password(current_password, user.password_hash):
        error = "Le mot de passe actuel est incorrect."
    elif new_error is not None:
        error = new_error
    elif new_password != new_password_confirm:
        error = "Les nouveaux mots de passe ne correspondent pas."

    if error:
        return templates.TemplateResponse(
            request, "password_change.html",
            {"page_title": "Changer le mot de passe", "error": error, "success": False},
            status_code=400,
        )

    user.password_hash = hash_password(new_password)
    db.commit()

    return templates.TemplateResponse(
        request, "password_change.html",
        {"page_title": "Changer le mot de passe", "error": None, "success": True},
    )


# ---------------------------------------------------------------------------
# Contact (private)
# ---------------------------------------------------------------------------


@router.get("/contact", response_class=HTMLResponse)
def contact_page(request: Request, user: CurrentUser) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "contact.html",
        {"page_title": "Contact", "error": None, "success": False},
    )


@router.post("/contact", response_model=None)
async def contact_submit(
    request: Request,
    subject: Annotated[str, Form()],
    message: Annotated[str, Form()],
    user: CurrentUser,
):
    """Send a contact message to the site administrator."""
    subject_clean = subject.strip()
    message_clean = message.strip()

    if not subject_clean or not message_clean:
        return templates.TemplateResponse(
            request, "contact.html",
            {"page_title": "Contact", "error": "Sujet et message requis.", "success": False},
            status_code=400,
        )

    # Rate limit: cap message length
    if len(message_clean) > 2000:
        message_clean = message_clean[:2000]

    from app.config import get_settings
    settings = get_settings()
    admin_email = settings.smtp_from  # same as the noreply address

    body = (
        f"Message de : {user.username}"
        f"{(' <' + user.email + '>') if user.email else ''}\n"
        f"---\n\n"
        f"{message_clean}\n"
    )

    sent = send_email(
        to=admin_email,
        subject=f"[SPIGNOS Contact] {subject_clean}",
        body=body,
    )

    if not sent:
        return templates.TemplateResponse(
            request, "contact.html",
            {
                "page_title": "Contact",
                "error": "Impossible d'envoyer le message. Réessaie plus tard.",
                "success": False,
            },
            status_code=500,
        )

    return templates.TemplateResponse(
        request, "contact.html",
        {"page_title": "Contact", "error": None, "success": True},
    )
