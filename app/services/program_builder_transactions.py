"""SQLite owner serialization shared by all program writers; never startup DDL."""

from contextlib import contextmanager
from functools import wraps

from app.services.plan_v3.transactions import guard_owner


@contextmanager
def owner_transaction(db, owner, *, auth_proof=None, commit=True):
    root = not db.info.get("program_builder_transaction")
    if root:
        if db.get_bind().dialect.name != "sqlite":
            raise ValueError("program_builder_storage_unsupported")
        guard_owner(db, owner, **(auth_proof or {}))
        # Discard cached reads only after reservation. Every callback then sees
        # the committed owner tree, including relationship collections.
        db.expire_all()
        db.info["program_builder_transaction"] = owner
    elif db.info["program_builder_transaction"] != owner:
        raise ValueError("program_builder_owner_changed")
    try:
        yield
        if root and commit:
            db.commit()
        else:
            db.flush()
    except Exception:
        if root:
            db.rollback()
        raise
    finally:
        if root:
            db.info.pop("program_builder_transaction", None)


def program_writer(function):
    @wraps(function)
    def guarded(db, user_id, *args, commit=True, **kwargs):
        with owner_transaction(db, user_id, commit=commit):
            return function(db, user_id, *args, commit=commit, **kwargs)

    return guarded
