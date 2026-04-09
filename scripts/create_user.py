"""Bootstrap the first user or add additional users.

Usage:
  python -m scripts.create_user <username> <password>

Creates a user with the given username and password. Exits 0 on
success, 1 if the username already exists.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: python -m scripts.create_user <username> <password>", file=sys.stderr)
        return 1

    username = sys.argv[1]
    password = sys.argv[2]

    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.user import User
    from app.services.auth import hash_password

    with SessionLocal() as db:
        existing = db.execute(
            select(User).where(User.username == username)
        ).scalar_one_or_none()
        if existing is not None:
            print(f"create_user: username '{username}' already exists.", file=sys.stderr)
            return 1

        user = User(
            username=username,
            password_hash=hash_password(password),
        )
        db.add(user)
        db.commit()
        print(f"create_user: user '{username}' created (id={user.id}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
