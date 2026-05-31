"""FastAPI entrypoint.

Wires up the DB, seeds the reference catalog idempotently, mounts static
assets, and registers the SSR + health routers. Kept intentionally small:
everything domain-related lives under `app/services` and `app/routers`.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
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


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Workout Session Tracking",
        version="0.1.0",
        docs_url="/api/docs" if settings.app_env != "prod" else None,
        redoc_url=None,
        lifespan=lifespan,
    )

    app.add_middleware(SecurityHeadersMiddleware)

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

    return app


app = create_app()
