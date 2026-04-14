# S4 — Challenges, Compare Mode, Template Sharing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add engagement loops to squads — time-boxed challenges (4 metrics), 1:1 compare mode, and template/session sharing with strict privacy enforcement.

**Architecture:** Three new tables (squad_challenges, squad_template_recommendations, squad_shared_sessions) in one migration. Three new services (challenge, compare, sharing). Routes added to existing squads router. New templates for challenge pages and compare mode. Squad detail page enriched with activity section.

**Tech Stack:** SQLAlchemy 2.0, Alembic, FastAPI, Jinja2, pytest

---

## File Structure

| File | Responsibility |
|------|---------------|
| `app/models/challenge.py` | SquadChallenge model |
| `app/models/sharing.py` | SquadTemplateRecommendation + SquadSharedSession models |
| `app/services/challenge.py` | create_challenge, compute_standings (4 metrics) |
| `app/services/compare.py` | compute_comparison for 2 members |
| `app/services/sharing.py` | recommend_template, share_session, get_squad_activity |
| `app/routers/squads.py` | Add challenge, compare, sharing routes |
| `app/templates/squad_challenges.html` | Challenge list |
| `app/templates/squad_challenge_create.html` | Challenge form |
| `app/templates/squad_challenge_detail.html` | Challenge standings |
| `app/templates/squad_compare.html` | 1:1 comparison |
| `app/templates/squad_detail.html` | Add activity section + compare form |

---

### Task 1: Models + Migration

**Files:**
- Create: `app/models/challenge.py`
- Create: `app/models/sharing.py`
- Modify: `app/models/__init__.py`
- Modify: `app/database.py`
- Create: `migrations/versions/20260414_add_challenges_sharing.py`

- [ ] **Step 1: Create challenge model**

Create `app/models/challenge.py`:

```python
"""Squad challenges — time-boxed competitions within a squad."""
from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SquadChallenge(Base):
    __tablename__ = "squad_challenges"

    id: Mapped[int] = mapped_column(primary_key=True)
    squad_id: Mapped[int] = mapped_column(
        ForeignKey("squads.id", ondelete="CASCADE"), nullable=False
    )
    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    metric: Mapped[str] = mapped_column(String(32), nullable=False)
    starts_at: Mapped[date] = mapped_column(Date, nullable=False)
    ends_at: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
```

- [ ] **Step 2: Create sharing models**

Create `app/models/sharing.py`:

```python
"""Squad sharing — template recommendations + anonymized session sharing."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SquadTemplateRecommendation(Base):
    __tablename__ = "squad_template_recommendations"

    id: Mapped[int] = mapped_column(primary_key=True)
    squad_id: Mapped[int] = mapped_column(
        ForeignKey("squads.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    template_slug: Mapped[str] = mapped_column(String(64), nullable=False)
    template_name: Mapped[str] = mapped_column(String(128), nullable=False)
    note: Mapped[str | None] = mapped_column(String(280), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class SquadSharedSession(Base):
    __tablename__ = "squad_shared_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    squad_id: Mapped[int] = mapped_column(
        ForeignKey("squads.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    session_id: Mapped[int] = mapped_column(
        ForeignKey("workout_sessions.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
```

- [ ] **Step 3: Register models**

In `app/models/__init__.py`, add `challenge, sharing` to the import line.
In `app/database.py`, add `challenge, sharing` to the model import line.

- [ ] **Step 4: Create migration**

Run `alembic heads`, then create the migration with 3 tables. Use `sa.text("(CURRENT_TIMESTAMP)")` for server_defaults. Run `alembic upgrade head`.

- [ ] **Step 5: Verify**

Run: `pytest tests/test_alembic_drift.py -v` — must pass.

- [ ] **Step 6: Commit**

```bash
git add app/models/challenge.py app/models/sharing.py app/models/__init__.py app/database.py migrations/versions/20260414_add_challenges_sharing.py
git commit -m "feat(s4): models + migration — challenges, recommendations, shared sessions"
```

---

### Task 2: Challenge Service + Tests

**Files:**
- Create: `app/services/challenge.py`
- Create: `tests/test_challenge.py`

- [ ] **Step 1: Create challenge service**

Create `app/services/challenge.py`:

```python
"""Squad challenge CRUD and live standings computation.

Standings are computed live from session data — no materialization.
Four metrics: sessions, score, tonnage, streak.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.challenge import SquadChallenge
from app.models.session import SessionExercise, SetLog, WorkoutSession
from app.models.squad import SquadMembership
from app.models.user import User
from app.services.quality_score import compute_session_quality


VALID_METRICS = {"sessions", "score", "tonnage", "streak"}


class ChallengeError(Exception):
    pass


def create_challenge(
    db: Session, squad_id: int, created_by: int,
    title: str, metric: str, starts_at: date, ends_at: date,
) -> SquadChallenge:
    title = title.strip()
    if not title:
        raise ChallengeError("Le titre ne peut pas être vide.")
    if metric not in VALID_METRICS:
        raise ChallengeError(f"Métrique invalide : {metric}")
    if ends_at <= starts_at:
        raise ChallengeError("La date de fin doit être après la date de début.")

    challenge = SquadChallenge(
        squad_id=squad_id, created_by=created_by,
        title=title, metric=metric,
        starts_at=starts_at, ends_at=ends_at,
    )
    db.add(challenge)
    db.commit()
    return challenge


def get_squad_challenges(db: Session, squad_id: int) -> list[SquadChallenge]:
    return list(db.execute(
        select(SquadChallenge)
        .where(SquadChallenge.squad_id == squad_id)
        .order_by(SquadChallenge.starts_at.desc())
    ).scalars().all())


def get_challenge_or_none(db: Session, challenge_id: int) -> SquadChallenge | None:
    return db.execute(
        select(SquadChallenge).where(SquadChallenge.id == challenge_id)
    ).scalar_one_or_none()


def _get_member_ids_and_names(db: Session, squad_id: int) -> list[tuple[int, str]]:
    rows = db.execute(
        select(SquadMembership.user_id, User.username)
        .join(User, User.id == SquadMembership.user_id)
        .where(SquadMembership.squad_id == squad_id)
    ).all()
    return [(r[0], r[1]) for r in rows]


def _get_user_sessions_in_window(
    db: Session, user_id: int, starts_at: date, ends_at: date,
) -> list[WorkoutSession]:
    start_dt = datetime.combine(starts_at, datetime.min.time()).replace(tzinfo=timezone.utc)
    end_dt = datetime.combine(ends_at + timedelta(days=1), datetime.min.time()).replace(tzinfo=timezone.utc)
    return list(db.execute(
        select(WorkoutSession)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == "completed",
            WorkoutSession.excluded_from_stats.is_(False),
            WorkoutSession.started_at >= start_dt,
            WorkoutSession.started_at < end_dt,
        )
        .options(
            selectinload(WorkoutSession.session_exercises)
            .selectinload(SessionExercise.set_logs)
        )
        .order_by(WorkoutSession.started_at.asc())
    ).scalars().all())


def _compute_sessions(sessions: list[WorkoutSession]) -> int:
    return len(sessions)


def _compute_score(sessions: list[WorkoutSession]) -> float:
    total = 0.0
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
        total += quality * (done_work / total_work)
    return round(total, 1)


def _compute_tonnage(sessions: list[WorkoutSession]) -> float:
    total = 0.0
    for s in sessions:
        for se in s.session_exercises:
            for sl in se.set_logs:
                if sl.kind == "work" and sl.completed and sl.weight_kg and sl.reps:
                    total += sl.weight_kg * sl.reps
    return round(total, 1)


def _compute_streak(sessions: list[WorkoutSession], starts_at: date, ends_at: date) -> int:
    session_dates = {s.started_at.date() for s in sessions}
    best = 0
    current = 0
    d = starts_at
    while d <= ends_at:
        if d in session_dates:
            current += 1
            best = max(best, current)
        else:
            current = 0
        d += timedelta(days=1)
    return best


_METRIC_FN = {
    "sessions": lambda sessions, sa, ea: _compute_sessions(sessions),
    "score": lambda sessions, sa, ea: _compute_score(sessions),
    "tonnage": lambda sessions, sa, ea: _compute_tonnage(sessions),
    "streak": lambda sessions, sa, ea: _compute_streak(sessions, sa, ea),
}

_METRIC_LABELS = {
    "sessions": "séances",
    "score": "points",
    "tonnage": "kg",
    "streak": "jours",
}


def compute_standings(
    db: Session, challenge: SquadChallenge,
) -> list[dict]:
    members = _get_member_ids_and_names(db, challenge.squad_id)
    fn = _METRIC_FN[challenge.metric]
    raw = []
    for user_id, username in members:
        sessions = _get_user_sessions_in_window(
            db, user_id, challenge.starts_at, challenge.ends_at,
        )
        value = fn(sessions, challenge.starts_at, challenge.ends_at)
        raw.append({"username": username, "value": value})

    raw.sort(key=lambda x: (-x["value"], x["username"]))
    for i, entry in enumerate(raw, 1):
        entry["rank"] = i
    return raw
```

- [ ] **Step 2: Create challenge tests**

Create `tests/test_challenge.py`:

```python
"""Tests for squad challenge service."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import pytest
from tests.helpers import get_test_user_id


def _create_squad_for_challenge(client):
    r = client.post("/squads/create", data={"name": f"Challenge Squad {id(client)}"}, follow_redirects=False)
    return int(r.headers["location"].rstrip("/").split("/")[-1])


def test_create_challenge(client):
    from app.database import SessionLocal
    from app.services.challenge import create_challenge

    uid = get_test_user_id()
    sid = _create_squad_for_challenge(client)
    with SessionLocal() as db:
        c = create_challenge(
            db, sid, uid, "Test Challenge", "sessions",
            date.today(), date.today() + timedelta(days=30),
        )
    assert c.title == "Test Challenge"
    assert c.metric == "sessions"


def test_create_challenge_invalid_metric(client):
    from app.database import SessionLocal
    from app.services.challenge import create_challenge, ChallengeError

    uid = get_test_user_id()
    sid = _create_squad_for_challenge(client)
    with SessionLocal() as db:
        with pytest.raises(ChallengeError):
            create_challenge(db, sid, uid, "Bad", "invalid", date.today(), date.today() + timedelta(days=30))


def test_create_challenge_end_before_start(client):
    from app.database import SessionLocal
    from app.services.challenge import create_challenge, ChallengeError

    uid = get_test_user_id()
    sid = _create_squad_for_challenge(client)
    with SessionLocal() as db:
        with pytest.raises(ChallengeError):
            create_challenge(db, sid, uid, "Bad", "sessions", date.today(), date.today() - timedelta(days=1))


def test_compute_standings_sessions(client):
    from app.database import SessionLocal
    from app.services.challenge import create_challenge, compute_standings

    uid = get_test_user_id()
    sid = _create_squad_for_challenge(client)
    with SessionLocal() as db:
        c = create_challenge(
            db, sid, uid, "Sessions Challenge", "sessions",
            date.today() - timedelta(days=7), date.today() + timedelta(days=1),
        )
        cid = c.id
    with SessionLocal() as db:
        from app.models.challenge import SquadChallenge
        c = db.get(SquadChallenge, cid)
        standings = compute_standings(db, c)
    assert len(standings) >= 1
    assert "rank" in standings[0]
    assert "value" in standings[0]
    assert "username" in standings[0]


def test_get_squad_challenges(client):
    from app.database import SessionLocal
    from app.services.challenge import create_challenge, get_squad_challenges

    uid = get_test_user_id()
    sid = _create_squad_for_challenge(client)
    with SessionLocal() as db:
        create_challenge(db, sid, uid, "C1", "sessions", date.today(), date.today() + timedelta(days=7))
    with SessionLocal() as db:
        create_challenge(db, sid, uid, "C2", "tonnage", date.today(), date.today() + timedelta(days=14))
    with SessionLocal() as db:
        challenges = get_squad_challenges(db, sid)
    assert len(challenges) >= 2
```

- [ ] **Step 3: Run tests**

Run: `pytest tests/test_challenge.py -v`
Expected: All PASS.

- [ ] **Step 4: Commit**

```bash
git add app/services/challenge.py tests/test_challenge.py
git commit -m "feat(s4): challenge service — create, standings (4 metrics), list"
```

---

### Task 3: Compare + Sharing Services

**Files:**
- Create: `app/services/compare.py`
- Create: `app/services/sharing.py`
- Create: `tests/test_compare.py`
- Create: `tests/test_sharing.py`

- [ ] **Step 1: Create compare service**

Create `app/services/compare.py`:

```python
"""1:1 comparison between two squad members.

Reuses squad leaderboard data filtered to two specific users.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.services.squad import compute_squad_leaderboard


def compute_comparison(
    db: Session, squad_id: int, user_a_id: int, user_b_id: int,
) -> dict:
    """Return comparison data for two members.

    Returns {"a": entry_dict, "b": entry_dict} where each entry
    has the same keys as a squad leaderboard entry.
    Returns None for a member not found in the leaderboard.
    """
    lb = compute_squad_leaderboard(db, squad_id)
    a_entry = None
    b_entry = None
    for entry in lb:
        # Leaderboard entries have "username" but we need to match by user_id.
        # We'll look up by username since that's what the leaderboard returns.
        pass

    # Need user_ids mapped to usernames
    from app.models.squad import SquadMembership
    from app.models.user import User
    from sqlalchemy import select

    a_username = db.execute(
        select(User.username).where(User.id == user_a_id)
    ).scalar_one_or_none()
    b_username = db.execute(
        select(User.username).where(User.id == user_b_id)
    ).scalar_one_or_none()

    for entry in lb:
        if entry["username"] == a_username:
            a_entry = entry
        if entry["username"] == b_username:
            b_entry = entry

    return {"a": a_entry, "b": b_entry}
```

- [ ] **Step 2: Create sharing service**

Create `app/services/sharing.py`:

```python
"""Squad template recommendations + anonymized session sharing."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.session import SessionExercise, WorkoutSession
from app.models.sharing import SquadSharedSession, SquadTemplateRecommendation
from app.models.user import User
from app.services.substitution import actual_exercise_name


def recommend_template(
    db: Session, squad_id: int, user_id: int,
    template_slug: str, template_name: str, note: str | None = None,
) -> SquadTemplateRecommendation:
    rec = SquadTemplateRecommendation(
        squad_id=squad_id, user_id=user_id,
        template_slug=template_slug, template_name=template_name,
        note=note.strip() if note else None,
    )
    db.add(rec)
    db.commit()
    return rec


def share_session(
    db: Session, squad_id: int, user_id: int, session_id: int,
) -> SquadSharedSession:
    # Verify the session belongs to this user
    session = db.execute(
        select(WorkoutSession)
        .where(WorkoutSession.id == session_id, WorkoutSession.user_id == user_id)
    ).scalar_one_or_none()
    if not session:
        raise ValueError("Session introuvable ou non autorisée.")

    shared = SquadSharedSession(
        squad_id=squad_id, user_id=user_id, session_id=session_id,
    )
    db.add(shared)
    db.commit()
    return shared


def get_squad_activity(db: Session, squad_id: int, limit: int = 20) -> list[dict]:
    """Return recent activity (recommendations + shared sessions) for a squad.

    Returns a list of dicts with type, username, created_at, and type-specific data.
    Ordered by created_at desc.
    """
    # Recommendations
    recs = db.execute(
        select(SquadTemplateRecommendation, User.username)
        .join(User, User.id == SquadTemplateRecommendation.user_id)
        .where(SquadTemplateRecommendation.squad_id == squad_id)
        .order_by(SquadTemplateRecommendation.created_at.desc())
        .limit(limit)
    ).all()

    # Shared sessions
    shares = db.execute(
        select(SquadSharedSession, User.username, WorkoutSession)
        .join(User, User.id == SquadSharedSession.user_id)
        .join(WorkoutSession, WorkoutSession.id == SquadSharedSession.session_id)
        .where(SquadSharedSession.squad_id == squad_id)
        .options(
            selectinload(WorkoutSession.session_exercises)
        )
        .order_by(SquadSharedSession.created_at.desc())
        .limit(limit)
    ).all()

    activity = []

    for rec, username in recs:
        activity.append({
            "type": "recommendation",
            "username": username,
            "created_at": rec.created_at,
            "template_slug": rec.template_slug,
            "template_name": rec.template_name,
            "note": rec.note,
        })

    for shared, username, session in shares:
        exercises = []
        for se in sorted(session.session_exercises, key=lambda x: x.position):
            exercises.append({
                "code": se.exercise_code_snapshot,
                "name": actual_exercise_name(se),
                "success_score": se.success_score,
            })
        activity.append({
            "type": "shared_session",
            "username": username,
            "created_at": shared.created_at,
            "template_name": session.template_name_snapshot,
            "session_date": session.started_at,
            "exercises": exercises,
        })

    activity.sort(key=lambda x: x["created_at"], reverse=True)
    return activity[:limit]
```

- [ ] **Step 3: Create tests**

Create `tests/test_compare.py`:

```python
"""Tests for compare service."""
from __future__ import annotations


def test_compute_comparison_returns_both_members(client):
    from app.database import SessionLocal
    from app.services.compare import compute_comparison
    from app.services.squad import create_squad
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    with SessionLocal() as db:
        squad = create_squad(db, uid, f"Compare Squad {id(client)}")
        sid = squad.id
    with SessionLocal() as db:
        result = compute_comparison(db, sid, uid, uid)
    assert result["a"] is not None
    assert result["a"]["username"] == "testuser"
```

Create `tests/test_sharing.py`:

```python
"""Tests for sharing service."""
from __future__ import annotations


def test_recommend_template(client):
    from app.database import SessionLocal
    from app.services.sharing import recommend_template, get_squad_activity
    from app.services.squad import create_squad
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    with SessionLocal() as db:
        squad = create_squad(db, uid, f"Share Squad {id(client)}")
        sid = squad.id
    with SessionLocal() as db:
        recommend_template(db, sid, uid, "push-a", "Push A", "Try this!")
    with SessionLocal() as db:
        activity = get_squad_activity(db, sid)
    assert len(activity) >= 1
    assert activity[0]["type"] == "recommendation"
    assert activity[0]["template_slug"] == "push-a"


def test_share_session(client):
    import re
    from app.database import SessionLocal
    from app.services.sharing import share_session, get_squad_activity
    from app.services.squad import create_squad
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    # Create a session to share
    r = client.post("/sessions", data={"template_slug": "push-a"}, follow_redirects=False)
    session_id = int(r.headers["location"].split("/")[-1])

    with SessionLocal() as db:
        squad = create_squad(db, uid, f"Session Share Squad {id(client)}")
        sid = squad.id
    with SessionLocal() as db:
        share_session(db, sid, uid, session_id)
    with SessionLocal() as db:
        activity = get_squad_activity(db, sid)
    recs = [a for a in activity if a["type"] == "shared_session"]
    assert len(recs) >= 1
    # Privacy: no weights/reps in exercises
    for ex in recs[0]["exercises"]:
        assert "weight_kg" not in ex
        assert "reps" not in ex


def test_shared_session_wrong_owner_fails(client):
    import pytest
    from app.database import SessionLocal
    from app.services.sharing import share_session
    from app.services.squad import create_squad
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    with SessionLocal() as db:
        squad = create_squad(db, uid, f"Wrong Owner Squad {id(client)}")
        sid = squad.id
    with SessionLocal() as db:
        with pytest.raises(ValueError):
            share_session(db, sid, uid, 999999)  # non-existent session
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_compare.py tests/test_sharing.py -v`
Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add app/services/compare.py app/services/sharing.py tests/test_compare.py tests/test_sharing.py
git commit -m "feat(s4): compare + sharing services — 1:1 comparison, recommend, share session"
```

---

### Task 4: Routes + Templates — Challenges

**Files:**
- Modify: `app/routers/squads.py`
- Create: `app/templates/squad_challenges.html`
- Create: `app/templates/squad_challenge_create.html`
- Create: `app/templates/squad_challenge_detail.html`

- [ ] **Step 1: Add challenge routes to squads router**

Add to `app/routers/squads.py`:

```python
from app.services.challenge import (
    ChallengeError,
    VALID_METRICS,
    _METRIC_LABELS,
    create_challenge,
    compute_standings,
    get_challenge_or_none,
    get_squad_challenges,
)


@router.get("/squads/{squad_id}/challenges", response_class=HTMLResponse, name="squad_challenges")
def squad_challenges_page(request: Request, squad_id: int, db: DbSession, user: CurrentUser):
    squad = get_squad_or_none(db, squad_id)
    if not squad or not is_member(db, squad_id, user.id):
        raise HTTPException(status_code=403)
    challenges = get_squad_challenges(db, squad_id)
    today = date.today()
    return templates.TemplateResponse(request, "squad_challenges.html", {
        "page_title": f"Challenges · {squad.name}",
        "squad": squad,
        "challenges": challenges,
        "today": today,
        "is_owner": squad.owner_id == user.id,
    })


@router.get("/squads/{squad_id}/challenges/create", response_class=HTMLResponse, name="squad_challenge_create")
def squad_challenge_create_page(request: Request, squad_id: int, db: DbSession, user: CurrentUser):
    squad = get_squad_or_none(db, squad_id)
    if not squad or squad.owner_id != user.id:
        raise HTTPException(status_code=403)
    return templates.TemplateResponse(request, "squad_challenge_create.html", {
        "page_title": "Nouveau challenge",
        "squad": squad,
        "metrics": VALID_METRICS,
        "metric_labels": _METRIC_LABELS,
        "error": None,
    })


@router.post("/squads/{squad_id}/challenges/create", name="squad_challenge_create_post")
def squad_challenge_create_post(
    request: Request, squad_id: int, db: DbSession, user: CurrentUser,
    title: str = Form(...), metric: str = Form(...),
    starts_at: str = Form(...), ends_at: str = Form(...),
):
    squad = get_squad_or_none(db, squad_id)
    if not squad or squad.owner_id != user.id:
        raise HTTPException(status_code=403)
    try:
        from datetime import date as date_type
        sa = date_type.fromisoformat(starts_at)
        ea = date_type.fromisoformat(ends_at)
        c = create_challenge(db, squad_id, user.id, title, metric, sa, ea)
        return RedirectResponse(
            url=request.url_for("squad_challenge_detail", squad_id=squad_id, challenge_id=c.id),
            status_code=303,
        )
    except (ChallengeError, ValueError) as exc:
        return templates.TemplateResponse(request, "squad_challenge_create.html", {
            "page_title": "Nouveau challenge",
            "squad": squad,
            "metrics": VALID_METRICS,
            "metric_labels": _METRIC_LABELS,
            "error": str(exc),
        })


@router.get("/squads/{squad_id}/challenges/{challenge_id}", response_class=HTMLResponse, name="squad_challenge_detail")
def squad_challenge_detail_page(
    request: Request, squad_id: int, challenge_id: int, db: DbSession, user: CurrentUser,
):
    squad = get_squad_or_none(db, squad_id)
    if not squad or not is_member(db, squad_id, user.id):
        raise HTTPException(status_code=403)
    challenge = get_challenge_or_none(db, challenge_id)
    if not challenge or challenge.squad_id != squad_id:
        raise HTTPException(status_code=404)
    standings = compute_standings(db, challenge)
    return templates.TemplateResponse(request, "squad_challenge_detail.html", {
        "page_title": challenge.title,
        "squad": squad,
        "challenge": challenge,
        "standings": standings,
        "metric_label": _METRIC_LABELS.get(challenge.metric, ""),
        "today": date.today(),
    })
```

Add `from datetime import date` at the top of the file if not already imported.

- [ ] **Step 2: Create challenge templates**

Create `app/templates/squad_challenges.html`, `squad_challenge_create.html`, `squad_challenge_detail.html` — standard Jinja2 templates extending `base.html`, using existing CSS classes (card, btn, badge, stats-list, etc.).

The challenge list shows active challenges (starts_at <= today <= ends_at) and past ones. The create form has inputs for title, metric (select), start date, end date. The detail page shows a standings table (rank, username, value + metric label).

- [ ] **Step 3: Run session tests to check nothing broke**

Run: `pytest tests/test_squad_routes.py -v --tb=short`
Expected: All pass.

- [ ] **Step 4: Commit**

```bash
git add app/routers/squads.py app/templates/squad_challenges.html app/templates/squad_challenge_create.html app/templates/squad_challenge_detail.html
git commit -m "feat(s4): challenge routes + templates — create, list, detail with standings"
```

---

### Task 5: Routes + Templates — Compare + Sharing + Squad Detail Enrichment

**Files:**
- Modify: `app/routers/squads.py`
- Create: `app/templates/squad_compare.html`
- Modify: `app/templates/squad_detail.html`

- [ ] **Step 1: Add compare and sharing routes**

Add to `app/routers/squads.py`:

```python
from app.services.compare import compute_comparison
from app.services.sharing import get_squad_activity, recommend_template, share_session


@router.get("/squads/{squad_id}/compare", response_class=HTMLResponse, name="squad_compare")
def squad_compare_page(
    request: Request, squad_id: int, db: DbSession, user: CurrentUser,
    a: int = 0, b: int = 0,
):
    squad = get_squad_or_none(db, squad_id)
    if not squad or not is_member(db, squad_id, user.id):
        raise HTTPException(status_code=403)
    members = get_squad_members(db, squad_id)
    comparison = None
    if a and b and a != b:
        comparison = compute_comparison(db, squad_id, a, b)
    return templates.TemplateResponse(request, "squad_compare.html", {
        "page_title": f"Comparer · {squad.name}",
        "squad": squad,
        "members": members,
        "comparison": comparison,
        "selected_a": a,
        "selected_b": b,
    })


@router.post("/squads/{squad_id}/recommend", name="squad_recommend")
def squad_recommend_post(
    request: Request, squad_id: int, db: DbSession, user: CurrentUser,
    template_slug: str = Form(...), template_name: str = Form(""),
    note: str = Form(""),
):
    if not is_member(db, squad_id, user.id):
        raise HTTPException(status_code=403)
    try:
        recommend_template(db, squad_id, user.id, template_slug, template_name, note or None)
    except Exception:
        pass
    return RedirectResponse(
        url=request.url_for("squad_detail", squad_id=squad_id),
        status_code=303,
    )


@router.post("/squads/{squad_id}/share-session", name="squad_share_session")
def squad_share_session_post(
    request: Request, squad_id: int, db: DbSession, user: CurrentUser,
    session_id: int = Form(...),
):
    if not is_member(db, squad_id, user.id):
        raise HTTPException(status_code=403)
    try:
        share_session(db, squad_id, user.id, session_id)
    except (ValueError, Exception):
        pass
    return RedirectResponse(
        url=request.url_for("squad_detail", squad_id=squad_id),
        status_code=303,
    )
```

- [ ] **Step 2: Update squad_detail to include activity + challenge links**

In `app/routers/squads.py`, in the `squad_detail` route, add:

```python
    from app.services.sharing import get_squad_activity
    from app.services.challenge import get_squad_challenges

    activity = get_squad_activity(db, squad_id)
    challenges = get_squad_challenges(db, squad_id)

    # User's completed sessions for the share-session dropdown
    user_sessions = list(db.execute(
        select(WorkoutSession)
        .where(WorkoutSession.user_id == user.id, WorkoutSession.status == "completed")
        .order_by(WorkoutSession.started_at.desc())
        .limit(10)
    ).scalars().all())

    # Available templates for the recommend dropdown
    from app.models.catalog import WorkoutTemplate
    all_templates = list(db.execute(
        select(WorkoutTemplate)
        .where(WorkoutTemplate.catalog_section != "archived")
        .order_by(WorkoutTemplate.display_order)
    ).scalars().all())
```

Add these to the template context: `"activity"`, `"challenges"`, `"user_sessions"`, `"all_templates"`, `"today": date.today()`.

- [ ] **Step 3: Create compare template and update squad_detail template**

Create `app/templates/squad_compare.html` — two member selects + comparison table if both selected.

Update `app/templates/squad_detail.html` to add:
- A "Challenges" section with links to active challenges + "Voir tous" link
- A "Comparer" link to `/squads/{id}/compare`
- An "Activité" section showing recommendations and shared sessions
- A "Recommander un template" form (select template + note + submit)
- A "Partager une séance" form (select session + submit)

- [ ] **Step 4: Run full test suite**

Run: `pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q`
Expected: All pass.

- [ ] **Step 5: Commit**

```bash
git add app/routers/squads.py app/templates/squad_compare.html app/templates/squad_detail.html
git commit -m "feat(s4): compare mode + sharing routes + enriched squad detail page"
```

---

### Task 6: Privacy Tests + Documentation + Sprint Report

**Files:**
- Create: `tests/test_s4_privacy.py`
- Create: `docs/SPRINT_S4_REPORT.md`

- [ ] **Step 1: Create privacy tests**

Create `tests/test_s4_privacy.py`:

```python
"""Privacy enforcement tests for S4 features.

Verifies that private data never leaks in challenge standings,
compare mode, or shared sessions.
"""
from __future__ import annotations


def test_challenge_standings_no_private_data(client):
    """Challenge standings contain only rank, username, value."""
    from datetime import date, timedelta
    from app.database import SessionLocal
    from app.services.challenge import create_challenge, compute_standings
    from app.services.squad import create_squad
    from app.models.challenge import SquadChallenge
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    with SessionLocal() as db:
        squad = create_squad(db, uid, f"Privacy Challenge {id(client)}")
        c = create_challenge(db, squad.id, uid, "P", "sessions",
                            date.today() - timedelta(days=7), date.today() + timedelta(days=1))
        cid = c.id
    with SessionLocal() as db:
        c = db.get(SquadChallenge, cid)
        standings = compute_standings(db, c)
    for entry in standings:
        assert set(entry.keys()) == {"rank", "username", "value"}


def test_shared_session_no_weights_or_reps(client):
    """Shared sessions must not contain weight_kg or reps."""
    from app.database import SessionLocal
    from app.services.sharing import share_session, get_squad_activity
    from app.services.squad import create_squad
    from tests.helpers import get_test_user_id

    uid = get_test_user_id()
    r = client.post("/sessions", data={"template_slug": "push-a"}, follow_redirects=False)
    session_id = int(r.headers["location"].split("/")[-1])

    with SessionLocal() as db:
        squad = create_squad(db, uid, f"Privacy Sharing {id(client)}")
        sid = squad.id
    with SessionLocal() as db:
        share_session(db, sid, uid, session_id)
    with SessionLocal() as db:
        activity = get_squad_activity(db, sid)

    shared = [a for a in activity if a["type"] == "shared_session"]
    assert len(shared) >= 1
    for ex in shared[0]["exercises"]:
        assert "weight_kg" not in ex
        assert "reps" not in ex
        assert "free_note" not in ex
        assert "muscle_sensation" not in ex


def test_compare_page_no_private_data(client):
    """Compare page renders without private body/readiness data."""
    r = client.post("/squads/create", data={"name": f"Privacy Compare {id(client)}"}, follow_redirects=False)
    squad_url = r.headers["location"]
    squad_id = squad_url.rstrip("/").split("/")[-1]

    from tests.helpers import get_test_user_id
    uid = get_test_user_id()

    r2 = client.get(f"/squads/{squad_id}/compare?a={uid}&b={uid}")
    assert r2.status_code == 200
    body = r2.text.lower()
    assert "weight_kg" not in body
    assert "chest_cm" not in body
    assert "readiness" not in body
    assert "bodyweight" not in body
```

- [ ] **Step 2: Run privacy tests**

Run: `pytest tests/test_s4_privacy.py -v`
Expected: All PASS.

- [ ] **Step 3: Run full test suite**

Run: `pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q`
Expected: All pass.

- [ ] **Step 4: Write sprint report**

Create `docs/SPRINT_S4_REPORT.md`:

```markdown
# Sprint S4 Report — Challenges, Compare Mode, Template Sharing

**Date:** 2026-04-14
**Status:** Complete
**Prerequisites:** S3 (private squads)

## Objective

Add engagement loops to squads: time-boxed challenges, 1:1 compare mode,
template recommendations, and anonymized session sharing.

## Deliverables

| Feature | Status |
|---------|--------|
| Challenges (4 metrics) | Done |
| Compare mode (1:1) | Done |
| Template recommendations | Done |
| Anonymized session sharing | Done |
| Privacy enforcement | Tested |

## Verification

```
pytest tests/test_challenge.py tests/test_compare.py tests/test_sharing.py tests/test_s4_privacy.py -v
pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q
```

## Gaps for S5+

- No challenge notifications
- No recurring challenges
- No share cards (dropped by design)
- No cross-squad features
```

- [ ] **Step 5: Commit**

```bash
git add tests/test_s4_privacy.py docs/SPRINT_S4_REPORT.md
git commit -m "docs(s4): privacy tests + sprint S4 report — challenges, compare, sharing complete"
```
