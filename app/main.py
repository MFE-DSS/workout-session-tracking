"""FastAPI entrypoint.

Wires up the DB, seeds the reference catalog idempotently, mounts static
assets, and registers the SSR + health routers. Kept intentionally small:
everything domain-related lives under `app/services` and `app/routers`.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import BASE_DIR, get_settings
from app.database import SessionLocal, init_db
from app.routers import admin, export, health, pages, sessions
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

    app.include_router(health.router)
    app.include_router(pages.router)
    app.include_router(sessions.router)
    app.include_router(export.router)
    app.include_router(admin.router)

    return app


app = create_app()
