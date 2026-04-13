"""ORM models package.

Import submodules here so that `Base.metadata` is populated as soon as the
package is imported (used by `init_db` and Alembic autogenerate later).
"""
from app.models import catalog, measurement, readiness, session, user  # noqa: F401
