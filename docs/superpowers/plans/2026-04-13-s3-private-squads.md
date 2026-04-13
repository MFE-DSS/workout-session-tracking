# S3 — Private Squads Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add private squads — small groups that can compare training activity via scoped leaderboards, with invite codes and strict privacy.

**Architecture:** Three new DB tables (squads, squad_memberships, squad_invite_codes), one Alembic migration, a squad service for CRUD/invitation/leaderboard, a new router with SSR templates, and privacy tests. The existing global leaderboard scoring logic is reused but filtered to squad members.

**Tech Stack:** SQLAlchemy 2.0, Alembic, FastAPI, Jinja2, pytest + httpx

---

## File Structure

| File | Responsibility |
|------|---------------|
| `app/models/squad.py` | Squad, SquadMembership, SquadInviteCode ORM models |
| `app/services/squad.py` | CRUD, invitation, membership, scoped leaderboard |
| `app/routers/squads.py` | All squad SSR routes |
| `app/templates/squads_list.html` | User's squads + create/join buttons |
| `app/templates/squad_detail.html` | Members, scoped leaderboard, invite, leave/delete |
| `app/templates/squad_create.html` | Name form |
| `app/templates/squad_join.html` | Code form |
| `migrations/versions/20260413_add_squads.py` | Migration for 3 tables |
| `tests/test_squad_service.py` | Service unit tests |
| `tests/test_squad_routes.py` | Route integration tests |
| `tests/test_squad_privacy.py` | Privacy enforcement tests |

---

### Task 1: Squad Models + Migration

**Files:**
- Create: `app/models/squad.py`
- Create: `migrations/versions/20260413_add_squads.py`
- Modify: `app/models/__init__.py`
- Modify: `app/database.py`

- [ ] **Step 1: Create the Squad models**

Create `app/models/squad.py`:

```python
"""Private squads — small groups for scoped leaderboards.

A squad is owned by one user. Members join via short invite codes.
No data beyond training activity is shared within a squad.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Squad(Base):
    __tablename__ = "squads"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    memberships: Mapped[list["SquadMembership"]] = relationship(
        back_populates="squad", cascade="all, delete-orphan"
    )
    invite_codes: Mapped[list["SquadInviteCode"]] = relationship(
        cascade="all, delete-orphan"
    )


class SquadMembership(Base):
    __tablename__ = "squad_memberships"
    __table_args__ = (
        UniqueConstraint("squad_id", "user_id", name="uq_squad_membership"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    squad_id: Mapped[int] = mapped_column(
        ForeignKey("squads.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(16), nullable=False, default="member"
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    squad: Mapped["Squad"] = relationship(back_populates="memberships")


class SquadInviteCode(Base):
    __tablename__ = "squad_invite_codes"

    id: Mapped[int] = mapped_column(primary_key=True)
    squad_id: Mapped[int] = mapped_column(
        ForeignKey("squads.id", ondelete="CASCADE"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(12), nullable=False, unique=True)
    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    used_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
```

- [ ] **Step 2: Register models**

In `app/models/__init__.py`, add `squad`:
```python
from app.models import catalog, measurement, readiness, session, squad, user  # noqa: F401
```

In `app/database.py`, find the model import line and add `squad`:
```python
from app.models import catalog, measurement, readiness, session, squad  # noqa: F401
```

- [ ] **Step 3: Create the migration**

First run `alembic heads` to get current head. Then create `migrations/versions/20260413_add_squads.py`:

```python
"""Add squads, squad_memberships, and squad_invite_codes tables.

Revision ID: <generate>
Revises: <current_head>
Create Date: 2026-04-13
"""
from alembic import op
import sqlalchemy as sa

revision = "<generate>"
down_revision = "<current_head>"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "squads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(64), nullable=False, unique=True),
        sa.Column("owner_id", sa.Integer(),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
    )

    op.create_table(
        "squad_memberships",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("squad_id", sa.Integer(),
                  sa.ForeignKey("squads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(16), nullable=False, server_default="member"),
        sa.Column("joined_at", sa.DateTime(timezone=True),
                  server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.UniqueConstraint("squad_id", "user_id", name="uq_squad_membership"),
    )

    op.create_table(
        "squad_invite_codes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("squad_id", sa.Integer(),
                  sa.ForeignKey("squads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(12), nullable=False, unique=True),
        sa.Column("created_by", sa.Integer(),
                  sa.ForeignKey("users.id"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_by", sa.Integer(),
                  sa.ForeignKey("users.id"), nullable=True),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("squad_invite_codes")
    op.drop_table("squad_memberships")
    op.drop_table("squads")
```

Fill in the revision IDs from `alembic heads`, then run: `alembic upgrade head`

- [ ] **Step 4: Verify migration**

Run: `python -c "from app.database import SessionLocal; db = SessionLocal(); print('OK'); db.close()"`
Run: `pytest tests/test_alembic_drift.py -v`
Expected: Both pass.

- [ ] **Step 5: Commit**

```bash
git add app/models/squad.py app/models/__init__.py app/database.py migrations/versions/20260413_add_squads.py
git commit -m "feat(s3): squad models + migration — squads, memberships, invite codes"
```

---

### Task 2: Squad Service — CRUD + Invitation + Scoped Leaderboard

**Files:**
- Create: `app/services/squad.py`
- Create: `tests/test_squad_service.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_squad_service.py`:

```python
"""Tests for squad service — CRUD, invitation, scoped leaderboard."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from tests.helpers import get_test_user_id


def _create_second_user(db):
    """Create a second user for squad tests."""
    from app.models.user import User
    from app.services.auth import hash_password
    from sqlalchemy import select

    existing = db.execute(
        select(User).where(User.username == "squadmate")
    ).scalar_one_or_none()
    if existing:
        return existing.id

    user = User(
        username="squadmate",
        password_hash=hash_password("pass1234"),
        is_active=True,
    )
    db.add(user)
    db.commit()
    return user.id


def test_create_squad(client):
    from app.database import SessionLocal
    from app.services.squad import create_squad

    uid = get_test_user_id()
    with SessionLocal() as db:
        squad = create_squad(db, uid, "Test Squad")
    assert squad.name == "Test Squad"
    assert squad.owner_id == uid


def test_create_squad_adds_owner_as_member(client):
    from app.database import SessionLocal
    from app.services.squad import create_squad, get_user_squads

    uid = get_test_user_id()
    with SessionLocal() as db:
        create_squad(db, uid, "Auto Member Squad")
    with SessionLocal() as db:
        squads = get_user_squads(db, uid)
    assert len(squads) >= 1
    names = [s.name for s in squads]
    assert "Auto Member Squad" in names


def test_create_squad_duplicate_name_fails(client):
    import pytest
    from app.database import SessionLocal
    from app.services.squad import create_squad, SquadError

    uid = get_test_user_id()
    with SessionLocal() as db:
        create_squad(db, uid, "Unique Squad")
    with SessionLocal() as db:
        with pytest.raises(SquadError, match="existe déjà"):
            create_squad(db, uid, "Unique Squad")


def test_generate_invite_code(client):
    from app.database import SessionLocal
    from app.services.squad import create_squad, generate_invite_code

    uid = get_test_user_id()
    with SessionLocal() as db:
        squad = create_squad(db, uid, "Invite Squad")
    with SessionLocal() as db:
        code = generate_invite_code(db, squad.id, uid)
    assert code.startswith("SPGN-")
    assert len(code) == 9  # SPGN-XXXX


def test_join_by_code(client):
    from app.database import SessionLocal
    from app.services.squad import create_squad, generate_invite_code, join_by_code

    uid = get_test_user_id()
    with SessionLocal() as db:
        squad = create_squad(db, uid, "Join Squad")
        sid = squad.id
    with SessionLocal() as db:
        code = generate_invite_code(db, sid, uid)
    with SessionLocal() as db:
        mate_id = _create_second_user(db)
    with SessionLocal() as db:
        result = join_by_code(db, mate_id, code)
    assert result is not None
    assert result.id == sid


def test_join_expired_code_fails(client):
    from app.database import SessionLocal
    from app.models.squad import SquadInviteCode
    from app.services.squad import create_squad, generate_invite_code, join_by_code, SquadError
    import pytest

    uid = get_test_user_id()
    with SessionLocal() as db:
        squad = create_squad(db, uid, "Expired Squad")
        sid = squad.id
    with SessionLocal() as db:
        code_str = generate_invite_code(db, sid, uid)
        # Manually expire the code
        code_obj = db.execute(
            __import__("sqlalchemy").select(SquadInviteCode)
            .where(SquadInviteCode.code == code_str)
        ).scalar_one()
        code_obj.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
        db.commit()

    with SessionLocal() as db:
        mate_id = _create_second_user(db)
    with SessionLocal() as db:
        with pytest.raises(SquadError):
            join_by_code(db, mate_id, code_str)


def test_leave_squad(client):
    from app.database import SessionLocal
    from app.services.squad import create_squad, generate_invite_code, join_by_code, leave_squad, get_squad_members

    uid = get_test_user_id()
    with SessionLocal() as db:
        squad = create_squad(db, uid, "Leave Squad")
        sid = squad.id
    with SessionLocal() as db:
        code = generate_invite_code(db, sid, uid)
    with SessionLocal() as db:
        mate_id = _create_second_user(db)
    with SessionLocal() as db:
        join_by_code(db, mate_id, code)
    with SessionLocal() as db:
        leave_squad(db, sid, mate_id)
    with SessionLocal() as db:
        members = get_squad_members(db, sid)
    usernames = [m["username"] for m in members]
    assert "squadmate" not in usernames


def test_owner_cannot_leave(client):
    import pytest
    from app.database import SessionLocal
    from app.services.squad import create_squad, leave_squad, SquadError

    uid = get_test_user_id()
    with SessionLocal() as db:
        squad = create_squad(db, uid, "Owner Stuck Squad")
    with SessionLocal() as db:
        with pytest.raises(SquadError, match="owner"):
            leave_squad(db, squad.id, uid)


def test_delete_squad(client):
    from app.database import SessionLocal
    from app.services.squad import create_squad, delete_squad, get_user_squads

    uid = get_test_user_id()
    with SessionLocal() as db:
        squad = create_squad(db, uid, "Delete Squad")
        sid = squad.id
    with SessionLocal() as db:
        delete_squad(db, sid, uid)
    with SessionLocal() as db:
        squads = get_user_squads(db, uid)
    names = [s.name for s in squads]
    assert "Delete Squad" not in names


def test_squad_leaderboard(client):
    from app.database import SessionLocal
    from app.services.squad import create_squad, compute_squad_leaderboard

    uid = get_test_user_id()
    with SessionLocal() as db:
        squad = create_squad(db, uid, "LB Squad")
        sid = squad.id
    with SessionLocal() as db:
        lb = compute_squad_leaderboard(db, sid)
    assert isinstance(lb, list)
    assert len(lb) >= 1
    assert lb[0]["username"] == "testuser"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_squad_service.py::test_create_squad -v`
Expected: FAIL (ImportError)

- [ ] **Step 3: Implement the squad service**

Create `app/services/squad.py`:

```python
"""Squad CRUD, invitation, membership, and scoped leaderboard.

Squads are small private groups (~12 people) for comparing training
activity. No body/readiness data is shared — only session-based metrics.
"""
from __future__ import annotations

import secrets
import string
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.session import SessionExercise, WorkoutSession
from app.models.squad import Squad, SquadInviteCode, SquadMembership
from app.models.user import User
from app.services.quality_score import compute_session_quality
from app.services.performance import compute_grade, GRADE_LABELS


class SquadError(Exception):
    """Raised for squad business rule violations."""
    pass


# --- CRUD ---


def create_squad(db: Session, owner_id: int, name: str) -> Squad:
    """Create a squad and add the owner as first member."""
    name = name.strip()
    if not name:
        raise SquadError("Le nom de la squad ne peut pas être vide.")

    existing = db.execute(
        select(Squad).where(Squad.name == name)
    ).scalar_one_or_none()
    if existing:
        raise SquadError(f"Une squad nommée '{name}' existe déjà.")

    squad = Squad(name=name, owner_id=owner_id)
    db.add(squad)
    db.flush()  # get squad.id

    membership = SquadMembership(
        squad_id=squad.id, user_id=owner_id, role="owner"
    )
    db.add(membership)
    db.commit()
    return squad


def get_user_squads(db: Session, user_id: int) -> list[Squad]:
    """Return squads where user is a member."""
    return list(db.execute(
        select(Squad)
        .join(SquadMembership, SquadMembership.squad_id == Squad.id)
        .where(SquadMembership.user_id == user_id)
        .order_by(Squad.name)
    ).scalars().all())


def get_squad_or_none(db: Session, squad_id: int) -> Squad | None:
    return db.execute(
        select(Squad).where(Squad.id == squad_id)
    ).scalar_one_or_none()


def is_member(db: Session, squad_id: int, user_id: int) -> bool:
    return db.execute(
        select(SquadMembership)
        .where(SquadMembership.squad_id == squad_id)
        .where(SquadMembership.user_id == user_id)
    ).scalar_one_or_none() is not None


def get_membership(db: Session, squad_id: int, user_id: int) -> SquadMembership | None:
    return db.execute(
        select(SquadMembership)
        .where(SquadMembership.squad_id == squad_id)
        .where(SquadMembership.user_id == user_id)
    ).scalar_one_or_none()


def get_squad_members(db: Session, squad_id: int) -> list[dict]:
    """Return member info for a squad: username, role, joined_at."""
    rows = db.execute(
        select(User.id, User.username, SquadMembership.role, SquadMembership.joined_at)
        .join(SquadMembership, SquadMembership.user_id == User.id)
        .where(SquadMembership.squad_id == squad_id)
        .order_by(SquadMembership.joined_at)
    ).all()
    return [
        {"user_id": r[0], "username": r[1], "role": r[2], "joined_at": r[3]}
        for r in rows
    ]


def delete_squad(db: Session, squad_id: int, owner_id: int) -> None:
    """Delete a squad. Only the owner can do this."""
    squad = get_squad_or_none(db, squad_id)
    if not squad or squad.owner_id != owner_id:
        raise SquadError("Seul le propriétaire peut supprimer la squad.")
    db.delete(squad)
    db.commit()


# --- Invitation ---


def _generate_code() -> str:
    """Generate a short invite code: SPGN-XXXX."""
    chars = string.ascii_uppercase + string.digits
    suffix = "".join(secrets.choice(chars) for _ in range(4))
    return f"SPGN-{suffix}"


def generate_invite_code(db: Session, squad_id: int, owner_id: int) -> str:
    """Generate an invite code for a squad. Only the owner can do this."""
    squad = get_squad_or_none(db, squad_id)
    if not squad or squad.owner_id != owner_id:
        raise SquadError("Seul le propriétaire peut générer un code d'invitation.")

    # Generate unique code (retry once on collision)
    for _ in range(5):
        code = _generate_code()
        existing = db.execute(
            select(SquadInviteCode).where(SquadInviteCode.code == code)
        ).scalar_one_or_none()
        if not existing:
            break
    else:
        raise SquadError("Impossible de générer un code unique.")

    invite = SquadInviteCode(
        squad_id=squad_id,
        code=code,
        created_by=owner_id,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=48),
    )
    db.add(invite)
    db.commit()
    return code


def join_by_code(db: Session, user_id: int, code: str) -> Squad:
    """Join a squad using an invite code."""
    code = code.strip().upper()

    invite = db.execute(
        select(SquadInviteCode).where(SquadInviteCode.code == code)
    ).scalar_one_or_none()

    if not invite:
        raise SquadError("Code d'invitation invalide.")
    if invite.used_by is not None:
        raise SquadError("Ce code a déjà été utilisé.")
    if invite.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise SquadError("Ce code a expiré.")

    # Check not already member
    if is_member(db, invite.squad_id, user_id):
        raise SquadError("Vous êtes déjà membre de cette squad.")

    # Create membership
    db.add(SquadMembership(
        squad_id=invite.squad_id, user_id=user_id, role="member"
    ))

    # Mark code as used
    invite.used_by = user_id
    invite.used_at = datetime.now(timezone.utc)

    db.commit()

    return db.execute(
        select(Squad).where(Squad.id == invite.squad_id)
    ).scalar_one()


# --- Membership ---


def leave_squad(db: Session, squad_id: int, user_id: int) -> None:
    """Leave a squad. Owner cannot leave (must delete)."""
    membership = get_membership(db, squad_id, user_id)
    if not membership:
        raise SquadError("Vous n'êtes pas membre de cette squad.")
    if membership.role == "owner":
        raise SquadError("Le owner ne peut pas quitter. Supprimez la squad.")
    db.delete(membership)
    db.commit()


# --- Scoped Leaderboard ---


def compute_squad_leaderboard(db: Session, squad_id: int) -> list[dict]:
    """Compute leaderboard scoped to squad members.

    Returns: list of dicts with rank, username, total_points, avg_points,
    grade, session_count, last_session_date, last_session_template, streak.
    """
    # Get member user IDs
    member_rows = db.execute(
        select(SquadMembership.user_id, User.username)
        .join(User, User.id == SquadMembership.user_id)
        .where(SquadMembership.squad_id == squad_id)
    ).all()

    if not member_rows:
        return []

    raw = []
    for user_id, username in member_rows:
        sessions = db.execute(
            select(WorkoutSession)
            .where(
                WorkoutSession.user_id == user_id,
                WorkoutSession.status == "completed",
                WorkoutSession.excluded_from_stats.is_(False),
            )
            .options(
                selectinload(WorkoutSession.session_exercises)
                .selectinload(SessionExercise.set_logs)
            )
            .order_by(WorkoutSession.started_at.desc())
        ).scalars().all()

        total_pts = 0.0
        counted = 0
        last_date = None
        last_template = None

        for s in sessions:
            total_work = sum(
                1 for se in s.session_exercises
                for sl in se.set_logs if sl.kind == "work"
            )
            if total_work == 0:
                continue
            done_work = sum(
                1 for se in s.session_exercises
                for sl in se.set_logs if sl.kind == "work" and sl.completed
            )
            quality = compute_session_quality(s)
            session_pts = quality * (done_work / total_work)
            total_pts += session_pts
            counted += 1
            if last_date is None:
                last_date = s.started_at
                last_template = s.template_name_snapshot

        # Streak computation
        from datetime import date as date_type
        today = date_type.today()
        session_dates = {s.started_at.date() for s in sessions}
        streak = 0
        check = today
        while check in session_dates:
            streak += 1
            check -= timedelta(days=1)

        avg = round(total_pts / counted, 1) if counted > 0 else 0.0
        grade = compute_grade(avg, counted)

        raw.append({
            "username": username,
            "total_points": round(total_pts, 1),
            "avg_points": avg,
            "grade": grade,
            "grade_label": GRADE_LABELS.get(grade, ""),
            "session_count": counted,
            "last_session_date": last_date,
            "last_session_template": last_template,
            "streak": streak,
        })

    # Sort by total_points desc, then username asc
    raw.sort(key=lambda x: (-x["total_points"], x["username"]))

    # Add rank
    for i, entry in enumerate(raw, 1):
        entry["rank"] = i

    return raw
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_squad_service.py -v`
Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add app/services/squad.py tests/test_squad_service.py
git commit -m "feat(s3): squad service — CRUD, invite codes, join, leave, scoped leaderboard"
```

---

### Task 3: Squad Routes + Templates

**Files:**
- Create: `app/routers/squads.py`
- Create: `app/templates/squads_list.html`
- Create: `app/templates/squad_detail.html`
- Create: `app/templates/squad_create.html`
- Create: `app/templates/squad_join.html`
- Modify: `app/main.py`
- Modify: `app/templates/base.html`
- Create: `tests/test_squad_routes.py`

- [ ] **Step 1: Write failing route tests**

Create `tests/test_squad_routes.py`:

```python
"""Integration tests for squad routes."""
from __future__ import annotations


def test_squads_list_renders(client):
    r = client.get("/squads")
    assert r.status_code == 200
    assert "Squads" in r.text or "squads" in r.text.lower()


def test_squads_list_requires_auth(client):
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    r = client.get("/squads", follow_redirects=False)
    assert r.status_code == 303


def test_squad_create_page_renders(client):
    r = client.get("/squads/create")
    assert r.status_code == 200
    assert "Créer" in r.text or "créer" in r.text


def test_squad_create_post(client):
    r = client.post("/squads/create", data={"name": "Route Test Squad"}, follow_redirects=False)
    assert r.status_code == 303
    # Should redirect to the squad detail
    assert "/squads/" in r.headers["location"]


def test_squad_detail_page(client):
    # First create a squad
    r = client.post("/squads/create", data={"name": "Detail Test"}, follow_redirects=False)
    location = r.headers["location"]
    r2 = client.get(location)
    assert r2.status_code == 200
    assert "Detail Test" in r2.text


def test_squad_detail_non_member_gets_403(client):
    # Create squad, logout, login as different user, try to access
    r = client.post("/squads/create", data={"name": "Private Squad"}, follow_redirects=False)
    location = r.headers["location"]

    # Logout and register a new user
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    client.post("/register", data={
        "username": "outsider",
        "password": "testpass123",
        "password_confirm": "testpass123",
    }, follow_redirects=False)
    client.post("/login", data={
        "username": "outsider",
        "password": "testpass123",
    }, follow_redirects=False)

    r2 = client.get(location)
    assert r2.status_code == 403


def test_squad_join_page_renders(client):
    r = client.get("/squads/join")
    assert r.status_code == 200
    assert "Rejoindre" in r.text or "code" in r.text.lower()


def test_squad_invite_and_join_flow(client):
    # Create squad
    r = client.post("/squads/create", data={"name": "Flow Squad"}, follow_redirects=False)
    squad_url = r.headers["location"]
    squad_id = squad_url.rstrip("/").split("/")[-1]

    # Generate invite code
    r2 = client.post(f"/squads/{squad_id}/invite", follow_redirects=False)
    assert r2.status_code == 303

    # Get the code from the redirect page
    r3 = client.get(squad_url)
    assert "SPGN-" in r3.text

    # The code is displayed — we need to extract it
    import re
    code_match = re.search(r"SPGN-[A-Z0-9]{4}", r3.text)
    assert code_match, "Invite code not found in page"
    invite_code = code_match.group(0)

    # Logout and login as different user
    client.post("/logout", follow_redirects=False)
    client.cookies.clear()
    client.post("/register", data={
        "username": "joiner",
        "password": "testpass123",
        "password_confirm": "testpass123",
    }, follow_redirects=False)
    client.post("/login", data={
        "username": "joiner",
        "password": "testpass123",
    }, follow_redirects=False)

    # Join
    r4 = client.post("/squads/join", data={"code": invite_code}, follow_redirects=False)
    assert r4.status_code == 303

    # Should now be able to see the squad
    r5 = client.get(squad_url)
    assert r5.status_code == 200
    assert "joiner" in r5.text


def test_squad_nav_link_present(client):
    r = client.get("/squads")
    assert "Squads" in r.text
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_squad_routes.py::test_squads_list_renders -v`
Expected: FAIL (404)

- [ ] **Step 3: Create the router**

Create `app/routers/squads.py`:

```python
"""Squad routes — create, join, detail, leave, delete."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.deps import CurrentUser, DbSession
from app.services.squad import (
    SquadError,
    compute_squad_leaderboard,
    create_squad,
    delete_squad,
    generate_invite_code,
    get_membership,
    get_squad_members,
    get_squad_or_none,
    get_user_squads,
    is_member,
    join_by_code,
    leave_squad,
)
from app.templating import templates

router = APIRouter(tags=["squads"])


@router.get("/squads", response_class=HTMLResponse)
def squads_list(request: Request, db: DbSession, user: CurrentUser) -> HTMLResponse:
    squads = get_user_squads(db, user.id)
    squad_info = []
    for s in squads:
        members = get_squad_members(db, s.id)
        membership = get_membership(db, s.id, user.id)
        squad_info.append({
            "squad": s,
            "member_count": len(members),
            "role": membership.role if membership else "member",
        })
    return templates.TemplateResponse(
        request, "squads_list.html",
        {"page_title": "Squads", "squad_info": squad_info},
    )


@router.get("/squads/create", response_class=HTMLResponse)
def squad_create_page(request: Request, user: CurrentUser) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "squad_create.html",
        {"page_title": "Créer une squad", "error": None},
    )


@router.post("/squads/create", response_model=None)
async def squad_create_submit(
    request: Request,
    name: Annotated[str, Form()] = "",
    db: DbSession = None,
    user: CurrentUser = None,
):
    try:
        squad = create_squad(db, user.id, name)
        return RedirectResponse(url=f"/squads/{squad.id}", status_code=303)
    except SquadError as e:
        return templates.TemplateResponse(
            request, "squad_create.html",
            {"page_title": "Créer une squad", "error": str(e)},
        )


@router.get("/squads/join", response_class=HTMLResponse)
def squad_join_page(request: Request, user: CurrentUser) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "squad_join.html",
        {"page_title": "Rejoindre une squad", "error": None},
    )


@router.post("/squads/join", response_model=None)
async def squad_join_submit(
    request: Request,
    code: Annotated[str, Form()] = "",
    db: DbSession = None,
    user: CurrentUser = None,
):
    try:
        squad = join_by_code(db, user.id, code)
        return RedirectResponse(url=f"/squads/{squad.id}", status_code=303)
    except SquadError as e:
        return templates.TemplateResponse(
            request, "squad_join.html",
            {"page_title": "Rejoindre une squad", "error": str(e)},
        )


@router.get("/squads/{squad_id}", response_class=HTMLResponse)
def squad_detail(
    squad_id: int, request: Request, db: DbSession, user: CurrentUser,
) -> HTMLResponse:
    squad = get_squad_or_none(db, squad_id)
    if not squad:
        raise HTTPException(status_code=404)
    if not is_member(db, squad_id, user.id):
        raise HTTPException(status_code=403, detail="Accès réservé aux membres.")

    members = get_squad_members(db, squad_id)
    leaderboard = compute_squad_leaderboard(db, squad_id)
    membership = get_membership(db, squad_id, user.id)
    is_owner = squad.owner_id == user.id

    # Get latest invite code (if any, for display)
    from sqlalchemy import select
    from app.models.squad import SquadInviteCode
    from datetime import datetime, timezone
    latest_code = db.execute(
        select(SquadInviteCode)
        .where(SquadInviteCode.squad_id == squad_id)
        .where(SquadInviteCode.used_by.is_(None))
        .where(SquadInviteCode.expires_at > datetime.now(timezone.utc))
        .order_by(SquadInviteCode.expires_at.desc())
        .limit(1)
    ).scalar_one_or_none()

    return templates.TemplateResponse(
        request, "squad_detail.html",
        {
            "page_title": squad.name,
            "squad": squad,
            "members": members,
            "leaderboard": leaderboard,
            "is_owner": is_owner,
            "latest_code": latest_code.code if latest_code else None,
            "current_user_id": user.id,
        },
    )


@router.post("/squads/{squad_id}/invite", response_model=None)
async def squad_invite(
    squad_id: int, db: DbSession, user: CurrentUser,
):
    try:
        generate_invite_code(db, squad_id, user.id)
    except SquadError:
        pass
    return RedirectResponse(url=f"/squads/{squad_id}", status_code=303)


@router.post("/squads/{squad_id}/leave", response_model=None)
async def squad_leave(
    squad_id: int, db: DbSession, user: CurrentUser,
):
    try:
        leave_squad(db, squad_id, user.id)
    except SquadError:
        pass
    return RedirectResponse(url="/squads", status_code=303)


@router.post("/squads/{squad_id}/delete", response_model=None)
async def squad_delete(
    squad_id: int, db: DbSession, user: CurrentUser,
):
    try:
        delete_squad(db, squad_id, user.id)
    except SquadError:
        pass
    return RedirectResponse(url="/squads", status_code=303)
```

- [ ] **Step 4: Register the router**

In `app/main.py`, add to the imports:
```python
from app.routers import admin, auth_routes, export, health, leaderboard, pages, readiness, sessions, squads
```

And add to the router registrations:
```python
    app.include_router(squads.router)
```

- [ ] **Step 5: Create templates**

Create `app/templates/squads_list.html`:

```html
{% extends "base.html" %}
{% block content %}
<h1 class="page-title">Squads</h1>

<div style="display:flex;gap:var(--space-sm);margin-bottom:var(--space-md);">
  <a class="btn btn--primary" href="/squads/create">Créer une squad</a>
  <a class="btn btn--ghost" href="/squads/join">Rejoindre avec un code</a>
</div>

{% if not squad_info %}
  <p class="text-dim">Vous n'êtes membre d'aucune squad.</p>
{% else %}
  <div class="card-list">
    {% for info in squad_info %}
    <a class="card" href="/squads/{{ info.squad.id }}" style="display:block;text-decoration:none;margin-bottom:var(--space-sm);">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <b>{{ info.squad.name }}</b>
        <span class="badge">{{ info.member_count }} membre{% if info.member_count != 1 %}s{% endif %}</span>
      </div>
      <div class="text-dim" style="font-size:13px;">
        {% if info.role == 'owner' %}Propriétaire{% else %}Membre{% endif %}
        · Créée le {{ info.squad.created_at.strftime('%d/%m/%Y') }}
      </div>
    </a>
    {% endfor %}
  </div>
{% endif %}
{% endblock %}
```

Create `app/templates/squad_create.html`:

```html
{% extends "base.html" %}
{% block content %}
<h1 class="page-title">Créer une squad</h1>

<div class="card" style="max-width:400px;">
  {% if error %}
    <p class="text-warn" style="margin-bottom:var(--space-sm);">{{ error }}</p>
  {% endif %}
  <form method="post" action="/squads/create">
    <label class="field">
      <span class="field__label">Nom de la squad</span>
      <input type="text" name="name" maxlength="64" required placeholder="Ex: Crew du lundi">
    </label>
    <button type="submit" class="btn btn--primary" style="margin-top:var(--space-md);width:100%;">Créer</button>
  </form>
</div>

<a class="btn btn--ghost" href="/squads" style="margin-top:var(--space-md);display:inline-block;">← Retour</a>
{% endblock %}
```

Create `app/templates/squad_join.html`:

```html
{% extends "base.html" %}
{% block content %}
<h1 class="page-title">Rejoindre une squad</h1>

<div class="card" style="max-width:400px;">
  {% if error %}
    <p class="text-warn" style="margin-bottom:var(--space-sm);">{{ error }}</p>
  {% endif %}
  <form method="post" action="/squads/join">
    <label class="field">
      <span class="field__label">Code d'invitation</span>
      <input type="text" name="code" maxlength="12" required
             placeholder="SPGN-XXXX" style="text-transform:uppercase;font-family:var(--font-mono);">
    </label>
    <button type="submit" class="btn btn--primary" style="margin-top:var(--space-md);width:100%;">Rejoindre</button>
  </form>
</div>

<a class="btn btn--ghost" href="/squads" style="margin-top:var(--space-md);display:inline-block;">← Retour</a>
{% endblock %}
```

Create `app/templates/squad_detail.html`:

```html
{% extends "base.html" %}
{% block content %}
<h1 class="page-title">{{ squad.name }}</h1>

<div class="cockpit-grid">
  <div class="cockpit-main">
    {# Scoped leaderboard #}
    <div class="card">
      <h2 class="card__title">Classement</h2>
      {% if leaderboard %}
      <div class="leaderboard-table" style="overflow-x:auto;">
        <table style="width:100%;font-size:13px;">
          <thead>
            <tr>
              <th>#</th>
              <th>Membre</th>
              <th>Score</th>
              <th>Séances</th>
              <th>Grade</th>
              <th>Streak</th>
            </tr>
          </thead>
          <tbody>
            {% for e in leaderboard %}
            <tr{% if e.username == squad.name %} style="font-weight:600;"{% endif %}>
              <td>{{ e.rank }}</td>
              <td>{{ e.username }}</td>
              <td>{{ "%.0f"|format(e.total_points) }}</td>
              <td>{{ e.session_count }}</td>
              <td><span class="grade-badge grade-badge--{{ e.grade|lower }}">{{ e.grade }}</span></td>
              <td>{{ e.streak }}j</td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
      {% else %}
        <p class="text-dim">Aucune donnée encore.</p>
      {% endif %}
    </div>
  </div>

  <div class="cockpit-side">
    {# Members list #}
    <div class="card">
      <h2 class="card__title">Membres ({{ members|length }})</h2>
      <ul class="stats-list">
        {% for m in members %}
        <li>
          <span>{{ m.username }}</span>
          <b>{% if m.role == 'owner' %}Propriétaire{% else %}Membre{% endif %}</b>
        </li>
        {% endfor %}
      </ul>
    </div>

    {% if is_owner %}
    {# Owner controls #}
    <div class="card">
      <h2 class="card__title">Invitation</h2>
      {% if latest_code %}
        <p style="font-size:14px;">Code actif : <code style="font-size:16px;font-weight:700;">{{ latest_code }}</code></p>
        <p class="text-dim" style="font-size:12px;">Valable 48h, usage unique.</p>
      {% else %}
        <p class="text-dim" style="font-size:13px;">Aucun code actif.</p>
      {% endif %}
      <form method="post" action="/squads/{{ squad.id }}/invite" style="margin-top:var(--space-sm);">
        <button type="submit" class="btn btn--ghost" style="width:100%;">Générer un code</button>
      </form>
    </div>

    <div class="card" style="margin-top:var(--space-sm);">
      <form method="post" action="/squads/{{ squad.id }}/delete"
            onsubmit="return confirm('Supprimer cette squad ? Cette action est irréversible.');">
        <button type="submit" class="btn" style="width:100%;color:var(--danger);">Supprimer la squad</button>
      </form>
    </div>
    {% else %}
    {# Member controls #}
    <div class="card">
      <form method="post" action="/squads/{{ squad.id }}/leave"
            onsubmit="return confirm('Quitter cette squad ?');">
        <button type="submit" class="btn btn--ghost" style="width:100%;">Quitter la squad</button>
      </form>
    </div>
    {% endif %}
  </div>
</div>
{% endblock %}
```

- [ ] **Step 6: Add Squads to navbar**

In `app/templates/base.html`, add between Dashboard and Board:

```html
        <a class="topbar__link" href="{{ url_for('squads_list') }}">Squads</a>
```

- [ ] **Step 7: Run tests**

Run: `pytest tests/test_squad_routes.py -v`
Expected: All PASS.

Run: `pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q`
Expected: Full suite passes.

- [ ] **Step 8: Commit**

```bash
git add app/routers/squads.py app/main.py app/templates/squads_list.html app/templates/squad_create.html app/templates/squad_join.html app/templates/squad_detail.html app/templates/base.html tests/test_squad_routes.py
git commit -m "feat(s3): squad routes + templates — create, join, detail, leave, delete, scoped leaderboard"
```

---

### Task 4: Privacy Tests + Documentation + Sprint Report

**Files:**
- Create: `tests/test_squad_privacy.py`
- Create: `docs/strategy/SPIGNOS_SQUADS_SPEC.md`
- Create: `docs/strategy/SPIGNOS_SQUADS_PRIVACY_MODEL.md`
- Create: `docs/SPRINT_S3_REPORT.md`

- [ ] **Step 1: Create privacy tests**

Create `tests/test_squad_privacy.py`:

```python
"""Privacy enforcement tests for squads.

Verifies that private data (measurements, readiness, weight, notes)
is NEVER exposed in squad views or scoped leaderboard.
"""
from __future__ import annotations


def test_squad_detail_does_not_contain_body_measurements(client):
    """Body measurements must never appear in squad detail."""
    r = client.post("/squads/create", data={"name": "Privacy Squad"}, follow_redirects=False)
    location = r.headers["location"]
    r2 = client.get(location)
    body = r2.text.lower()
    # These measurement terms should NOT appear
    assert "chest_cm" not in body
    assert "arm_cm" not in body
    assert "thigh_cm" not in body
    assert "waist_cm" not in body
    assert "hip_cm" not in body
    assert "neck_cm" not in body
    assert "tour de poitrine" not in body
    assert "tour de taille" not in body


def test_squad_detail_does_not_contain_readiness(client):
    """Readiness data must never appear in squad detail."""
    r = client.post("/squads/create", data={"name": "Privacy Squad 2"}, follow_redirects=False)
    r2 = client.get(r.headers["location"])
    body = r2.text.lower()
    assert "sleep_quality" not in body
    assert "fatigue_level" not in body
    assert "soreness_level" not in body
    assert "stress_level" not in body
    assert "motivation_level" not in body
    assert "readiness" not in body  # no readiness data in squad context


def test_squad_detail_does_not_contain_bodyweight(client):
    """Per-session bodyweight must not appear."""
    r = client.post("/squads/create", data={"name": "Privacy Squad 3"}, follow_redirects=False)
    r2 = client.get(r.headers["location"])
    body = r2.text.lower()
    assert "bodyweight" not in body
    assert "poids" not in body


def test_squad_leaderboard_only_contains_allowed_fields(client):
    """Scoped leaderboard should only contain: rank, username, score, sessions, grade, streak."""
    from app.database import SessionLocal
    from app.services.squad import create_squad, compute_squad_leaderboard
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    with SessionLocal() as db:
        squad = create_squad(db, uid, "LB Privacy Squad")
    with SessionLocal() as db:
        lb = compute_squad_leaderboard(db, squad.id)

    for entry in lb:
        allowed_keys = {
            "rank", "username", "total_points", "avg_points", "grade",
            "grade_label", "session_count", "last_session_date",
            "last_session_template", "streak",
        }
        assert set(entry.keys()) == allowed_keys, f"Unexpected keys: {set(entry.keys()) - allowed_keys}"
```

- [ ] **Step 2: Run privacy tests**

Run: `pytest tests/test_squad_privacy.py -v`
Expected: All PASS.

- [ ] **Step 3: Create docs**

Create `docs/strategy/SPIGNOS_SQUADS_SPEC.md`:

```markdown
# SPIGNOS Squads Spec

## Purpose
Private groups for comparing training activity and motivation.
No feed, no comments, no public discovery.

## Data Model
- Squad: name (unique), owner_id
- SquadMembership: squad_id, user_id, role (owner/member)
- SquadInviteCode: code (SPGN-XXXX), expires 48h, single-use

## Invitation Flow
1. Owner generates code on squad detail page
2. Shares code via external channel (message, in-person)
3. Invitee enters code on /squads/join
4. Membership created, code marked as used

## Scoped Leaderboard
Same scoring as global leaderboard but filtered to squad members.
Shows: rank, username, score, sessions, grade, streak, last activity.

## Privacy
See SPIGNOS_SQUADS_PRIVACY_MODEL.md
```

Create `docs/strategy/SPIGNOS_SQUADS_PRIVACY_MODEL.md`:

```markdown
# SPIGNOS Squads Privacy Model

## Principle
Squads share training activity, never body or health data.

## Shared with Squad Members
- Username
- Aggregate score (total_points, avg_points)
- Grade (A/B/C)
- Session count
- Last session date and template used
- Streak (consecutive training days)

## Never Shared
- Body measurements (chest, arms, thighs, waist, hips, neck, calves)
- Readiness entries (sleep, fatigue, soreness, stress, motivation)
- Bodyweight (per-session or profile)
- Session notes
- Body engineering dashboard score
- Set details (weight, reps)
- Exercise feedback (success score, muscle sensation)

## Enforcement
- Service layer returns only allowed fields
- Privacy tests verify no leakage in responses
- No body/readiness data is queried in squad service
```

Create `docs/SPRINT_S3_REPORT.md`:

```markdown
# Sprint S3 Report — Private Squads Foundation

**Date:** 2026-04-13
**Status:** Complete
**Prerequisites:** S0, S1, S2

## Objective

Add private squads — small groups with invite codes, scoped leaderboard,
and strict privacy model.

## Deliverables

| Artifact | Path | Status |
|----------|------|--------|
| Models | `app/models/squad.py` | Done — Squad, Membership, InviteCode |
| Migration | `migrations/versions/20260413_add_squads.py` | Applied |
| Service | `app/services/squad.py` | Done — CRUD, invite, join, leave, leaderboard |
| Router | `app/routers/squads.py` | Done — 10 routes |
| Templates | `app/templates/squad_*.html` | Done — 4 templates |
| Privacy tests | `tests/test_squad_privacy.py` | Done |
| Spec | `docs/strategy/SPIGNOS_SQUADS_SPEC.md` | Done |
| Privacy model | `docs/strategy/SPIGNOS_SQUADS_PRIVACY_MODEL.md` | Done |

## Verification Commands

```bash
pytest tests/test_squad_service.py -v
pytest tests/test_squad_routes.py -v
pytest tests/test_squad_privacy.py -v
pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q
```

## Gaps for S4

- No challenges (monthly private competitions)
- No compare mode (1:1 member comparison)
- No share cards (visual exports)
- No template sharing
```

- [ ] **Step 4: Run full test suite**

Run: `pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q`
Expected: All pass.

- [ ] **Step 5: Commit**

```bash
git add tests/test_squad_privacy.py docs/strategy/SPIGNOS_SQUADS_SPEC.md docs/strategy/SPIGNOS_SQUADS_PRIVACY_MODEL.md docs/SPRINT_S3_REPORT.md
git commit -m "docs(s3): privacy tests + squad spec + privacy model + sprint S3 report"
```
