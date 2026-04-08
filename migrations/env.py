"""Alembic migration environment.

Reads DATABASE_URL from the same `app.config.Settings` as the app
itself. One env var drives both runtime and migrations.

`render_as_batch=True` is enabled for SQLite: Alembic then rewrites
ALTER TABLE operations using SQLite's copy-and-rename dance, which
is the only way to change columns or constraints on SQLite.
"""
from __future__ import annotations

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# Make the `app` package importable from the migrations/ folder.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import get_settings  # noqa: E402
from app.database import Base  # noqa: E402

# Side-effect import so `Base.metadata` knows about every model.
from app.models import catalog as _catalog  # noqa: E402, F401
from app.models import session as _session  # noqa: E402, F401

config = context.config

# Inject the DATABASE_URL from app settings at runtime — but only if
# the caller (typically the alembic CLI) has NOT already set one. This
# lets tests and scripts pass a transient DB URL via
# `Config.set_main_option("sqlalchemy.url", ...)` before invoking
# `command.upgrade(...)`, without having to touch environment
# variables.
if not config.get_main_option("sqlalchemy.url"):
    settings = get_settings()
    config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _is_sqlite_url(url: str) -> bool:
    return url.startswith("sqlite")


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=_is_sqlite_url(url),
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=connection.dialect.name == "sqlite",
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
