"""Database admission guards. Never commits or rolls back the caller's work."""

from __future__ import annotations

from sqlalchemy import inspect, select, update
from sqlalchemy.orm import Session

from app.models.device_session import DeviceSession
from app.models.user import User


class RuntimeFailure(ValueError):
    def __init__(self, code: str, status: int = 409):
        self.code = code
        self.status = status
        super().__init__(code)


def schema_available(db: Session) -> bool:
    from app.database import Base
    from app.models.first_plan_runtime import PLAN_INDEX_NAMES, PLAN_TABLE_NAMES

    schema = inspect(db.connection())
    if not all(schema.has_table(name) for name in PLAN_TABLE_NAMES):
        return False
    for name in PLAN_TABLE_NAMES:
        expected = Base.metadata.tables[name]
        if {c["name"] for c in schema.get_columns(name)} != set(expected.columns.keys()):
            return False
        if schema.get_pk_constraint(name)["constrained_columns"] != [
            c.name for c in expected.primary_key
        ]:
            return False
    for table_name in (*PLAN_TABLE_NAMES, "workout_sessions", "session_exercises", "set_logs"):
        actual = {item["name"]: item for item in schema.get_indexes(table_name)}
        for index in Base.metadata.tables[table_name].indexes:
            if table_name not in PLAN_TABLE_NAMES and index.name not in PLAN_INDEX_NAMES:
                continue
            found = actual.get(index.name)
            if (
                found is None
                or bool(found["unique"]) != bool(index.unique)
                or found["column_names"] != [c.name for c in index.columns]
            ):
                return False
    return True


def guard_owner(
    db: Session,
    owner_id: int,
    *,
    expected_epoch: int | None = None,
    expected_hash: str | None = None,
    device_id: str | None = None,
) -> User:
    """Reserve SQLite's write lock or PostgreSQL's owner row, then refresh auth.

    UPDATE assigns the epoch to itself: it neither rotates credentials nor
    revokes access. No ORM cache is used as evidence of current authentication.
    """
    conditions = [User.id == owner_id, User.is_active.is_(True)]
    if expected_epoch is not None:
        conditions.append(User.session_epoch == expected_epoch)
    if expected_hash is not None:
        conditions.append(User.password_hash == expected_hash)
    if db.get_bind().dialect.name == "sqlite":
        result = db.execute(
            update(User)
            .where(*conditions)
            .values(session_epoch=User.session_epoch)
            .execution_options(synchronize_session=False)
        )
        if result.rowcount != 1:
            raise RuntimeFailure("authentication_changed", 401)
    query = select(User).where(*conditions).execution_options(populate_existing=True)
    if db.get_bind().dialect.name != "sqlite":
        query = query.with_for_update()
    user = db.scalar(query)
    if user is None:
        raise RuntimeFailure("authentication_changed", 401)
    if device_id is not None:
        ds = db.scalar(
            select(DeviceSession)
            .where(
                DeviceSession.id == device_id,
                DeviceSession.user_id == owner_id,
                DeviceSession.revoked_at.is_(None),
                DeviceSession.session_epoch == user.session_epoch,
            )
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        if ds is None:
            raise RuntimeFailure("authentication_changed", 401)
    return user


def admit_legacy_start(
    db: Session,
    owner_id: int,
    *,
    reject_any_open: bool = False,
    ignore_session_id: int | None = None,
):
    """Serialize legacy admissions with SCI without rewriting legacy journals.

    Web's historical multiple-legacy-session behavior is retained. Any SCI open
    excludes a new legacy admission; mobile additionally retains its existing
    any-open rule, now checked under the database guard.
    """
    from app.models.session import WorkoutSession

    guard_owner(db, owner_id)
    query = select(WorkoutSession).where(
        WorkoutSession.user_id == owner_id, WorkoutSession.status == "in_progress"
    )
    if ignore_session_id is not None:
        query = query.where(WorkoutSession.id != ignore_session_id)
    opened = list(db.scalars(query.execution_options(populate_existing=True)))
    if any(
        reject_any_open or s.template_slug_snapshot == "science:v3:first-session" for s in opened
    ):
        raise RuntimeFailure("session_open")
