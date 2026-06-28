"""FastAPI entrypoint.

Wires up the DB, seeds the reference catalog idempotently, mounts static
assets, and registers the SSR + health routers. Kept intentionally small:
everything domain-related lives under `app/services` and `app/routers`.
"""
from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response as StarletteResponse

from app.config import BASE_DIR, get_settings
from app.database import SessionLocal, init_db
from app.deps import _redirect_to_login
from app.routers import (
    admin,
    auth_routes,
    body,
    body_intelligence,
    coach_report,
    export,
    health,
    leaderboard,
    pages,
    readiness,
    sessions,
    squads,
)
from app.services.seed import seed_method_rules, seed_reference_split


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    with SessionLocal() as db:
        seed_reference_split(db)
        seed_method_rules(db)
    yield


_request_timing_logger = __import__("logging").getLogger("spignos.request_timing")


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Sb_26.6 — opt-in request timing logger.

    Off by default. When `PERF_REQUEST_TIMING_ENABLED=1`, logs method,
    path, status and duration_ms for every request. No header added to
    the response (avoids leaking timing publicly).
    """

    async def dispatch(
        self, request: StarletteRequest, call_next
    ) -> StarletteResponse:
        if not get_settings().perf_request_timing_enabled:
            return await call_next(request)
        t0 = time.perf_counter()
        response = await call_next(request)
        dt_ms = (time.perf_counter() - t0) * 1000.0
        _request_timing_logger.info(
            "request %s %s -> %d in %.1fms",
            request.method,
            request.url.path,
            response.status_code,
            dt_ms,
        )
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add standard security headers to every response."""

    async def dispatch(
        self, request: StarletteRequest, call_next
    ) -> StarletteResponse:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        # CSP: allow inline styles (needed for our templates) but block
        # everything else from external origins.
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data:; "
            "frame-ancestors 'none'"
        )
        return response


# ─── Sb_26.4 — per-IP rate limiter for sensitive public auth endpoints ───
#
# Single-process, in-memory sliding window. Not Redis-backed by design:
# V1 prod is a single uvicorn process behind nginx, so this is the right
# granularity. If we ever scale horizontally, swap this for Redis at
# the same call site without touching routes.
#
# Buckets are module-level so tests can reset deterministically via
# `_rate_limit_reset_for_tests()`.

_RATE_LIMIT_BUCKETS: dict[tuple[str, str], deque] = defaultdict(deque)
_RATE_LIMIT_LOCK = threading.Lock()

# (method, path) → settings attribute prefix
_RATE_LIMIT_ROUTES: dict[tuple[str, str], str] = {
    ("POST", "/login"): "login",
    ("POST", "/register"): "register",
    ("POST", "/forgot-password"): "forgot",
}


def _rate_limit_reset_for_tests() -> None:
    with _RATE_LIMIT_LOCK:
        _RATE_LIMIT_BUCKETS.clear()


def _rate_limit_check(
    settings, ip: str, route_key: str, *, now: float | None = None
) -> tuple[bool, int]:
    """Returns (allowed, retry_after_seconds).

    `route_key` is one of "login", "register", "forgot" — used as the
    settings prefix for max + window. The bucket key is (ip, route_key)
    so endpoints don't share quota.
    """
    max_attempts = getattr(settings, f"rate_limit_{route_key}_max")
    window = getattr(settings, f"rate_limit_{route_key}_window_seconds")
    ts = now if now is not None else time.monotonic()
    cutoff = ts - window
    with _RATE_LIMIT_LOCK:
        bucket = _RATE_LIMIT_BUCKETS[(ip, route_key)]
        while bucket and bucket[0] < cutoff:
            bucket.popleft()
        if len(bucket) >= max_attempts:
            retry = int(bucket[0] + window - ts) + 1
            return False, max(1, retry)
        bucket.append(ts)
        return True, 0


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sb_26.4 — block per-IP abuse of /login, /register, /forgot-password.

    Replies 429 with a sober message — never reveals whether the
    targeted username/email exists or any other state.
    """

    async def dispatch(
        self, request: StarletteRequest, call_next
    ) -> StarletteResponse:
        settings = get_settings()
        if not settings.rate_limit_enabled:
            return await call_next(request)
        key = (request.method, request.url.path)
        route_key = _RATE_LIMIT_ROUTES.get(key)
        if route_key is None:
            return await call_next(request)
        client_ip = request.client.host if request.client else "unknown"
        allowed, retry_after = _rate_limit_check(settings, client_ip, route_key)
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many attempts. Please retry later."},
                headers={"Retry-After": str(retry_after)},
            )
        return await call_next(request)


def _init_sentry_if_enabled(settings) -> bool:
    """Sb_26.3 — strictly opt-in Sentry init.

    Returns True if Sentry was initialised, False otherwise. Never
    raises: if `sentry-sdk` is not installed OR `SENTRY_DSN` is empty,
    this is a no-op and no external request is issued.
    """
    if not settings.sentry_enabled:
        return False
    try:
        import sentry_sdk  # type: ignore[import-not-found]
    except ImportError:
        return False
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.sentry_environment or settings.app_env,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        send_default_pii=False,
    )
    return True


def create_app() -> FastAPI:
    settings = get_settings()
    _init_sentry_if_enabled(settings)
    app = FastAPI(
        title="Workout Session Tracking",
        version="0.1.0",
        docs_url="/api/docs" if settings.app_env != "prod" else None,
        redoc_url=None,
        lifespan=lifespan,
    )

    app.add_middleware(SecurityHeadersMiddleware)
    # Sb_26.4 — rate limit /login, /register, /forgot-password per IP.
    # Reads settings on each request so tests can toggle via env.
    app.add_middleware(RateLimitMiddleware)
    # Sb_26.6 — opt-in request timing logger (PERF_REQUEST_TIMING_ENABLED=1)
    app.add_middleware(RequestTimingMiddleware)

    app.mount(
        "/static",
        StaticFiles(directory=str(BASE_DIR / "app" / "static")),
        name="static",
    )

    # Global exception handler: redirect to /login when auth is missing.
    @app.exception_handler(_redirect_to_login)
    async def _handle_redirect_to_login(request, exc):
        return RedirectResponse(url="/login", status_code=303)

    app.include_router(health.router)
    app.include_router(auth_routes.router)
    app.include_router(pages.router)
    app.include_router(sessions.router)
    app.include_router(export.router)
    app.include_router(admin.router)
    app.include_router(leaderboard.router)
    app.include_router(readiness.router)
    app.include_router(squads.router)
    app.include_router(coach_report.router)
    # Sb_Body_01 — Manual Body Profile. Routes self-gate on
    # BODY_ASSESSMENT_ENABLED (404 when off), so mounting is inert in prod
    # until the flag is explicitly enabled.
    app.include_router(body.router)
    # Sb_31.2 — Body Intelligence v2 (route /body/intelligence). Track
    # distinct du Body Manual Profile ci-dessus ; aucune dépendance
    # croisée.
    app.include_router(body_intelligence.router)

    return app


app = create_app()
