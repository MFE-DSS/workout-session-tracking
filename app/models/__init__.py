"""ORM models package.

Import submodules here so that `Base.metadata` is populated as soon as the
package is imported (used by `init_db` and Alembic autogenerate later).
"""
from app.models import (  # noqa: F401
    body_consent,
    body_zone,
    catalog,
    challenge,
    exercise_muscle_mapping,
    measurement,
    muscle,
    readiness,
    session,
    sharing,
    squad,
    training_preferences,
    user,
    user_program,
)
