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

from app.config import BASE_DIR, get_settings
from app.database import SessionLocal, init_db
from app.deps import _redirect_to_login
from app.routers import admin, auth_routes, export, health, pages, sessions
from app.services.seed import seed_method_rules, seed_reference_split


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    with SessionLocal() as db:
        seed_reference_split(db)
        seed_method_rules(db)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Workout Session Tracking",
        version="0.1.0",
        docs_url="/api/docs" if settings.app_env != "prod" else None,
        redoc_url=None,
        lifespan=lifespan,
    )

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

    return app


app = create_app()
