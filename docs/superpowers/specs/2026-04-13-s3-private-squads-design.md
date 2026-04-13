# S3 Design Spec — Private Squads Foundation

**Date:** 2026-04-13
**Sprint:** S3_private_squads_foundation
**Status:** Approved

---

## Context

S0-S2 built a complete single-user experience: catalog integrity, lateralized body metrics, daily readiness, and a 5-axis body engineering dashboard. SPIGNOS is now a solid private cockpit.

S3 introduces the first social layer: **private squads** — small groups (~12 people) who can compare training activity and motivate each other, without exposing private body/readiness data.

Currently, the only cross-user feature is the global leaderboard (`/leaderboard`) which ranks ALL active users. There are zero inter-user relationships (no groups, no friendships, no follows).

## Decisions Log

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Invitation mechanism | Code court (SPGN-XXXX, expire 48h) | Mobile-friendly, no notification system needed, private by default |
| Data visibility | Ranking + activity (templates, streak, dates) | Motivating without exposing body/readiness/weight data |
| Governance model | Owner unique + membres (2 roles) | Simple for ~12 people. Admin role is additive later if needed. |

---

## Data Model

### Table: `squads`

| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PK |
| name | VARCHAR(64) | NOT NULL, UNIQUE |
| owner_id | INTEGER | FK → users.id (CASCADE), NOT NULL |
| created_at | DATETIME(tz) | server_default=now() |

### Table: `squad_memberships`

| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PK |
| squad_id | INTEGER | FK → squads.id (CASCADE), NOT NULL |
| user_id | INTEGER | FK → users.id (CASCADE), NOT NULL |
| role | VARCHAR(16) | NOT NULL, DEFAULT 'member' — values: 'owner', 'member' |
| joined_at | DATETIME(tz) | server_default=now() |
| | | UNIQUE(squad_id, user_id) |

### Table: `squad_invite_codes`

| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PK |
| squad_id | INTEGER | FK → squads.id (CASCADE), NOT NULL |
| code | VARCHAR(12) | UNIQUE, NOT NULL — format SPGN-XXXX (4 alphanumeric) |
| created_by | INTEGER | FK → users.id, NOT NULL |
| expires_at | DATETIME(tz) | NOT NULL — created_at + 48h |
| used_by | INTEGER | FK → users.id, nullable — NULL = not yet used |
| used_at | DATETIME(tz) | nullable |
| | | INDEX(code) |

---

## Business Rules

### Creation
- Any authenticated user can create a squad
- Squad name must be unique across the app
- Creator automatically becomes owner + first member

### Invitation
- Only the owner can generate invite codes
- Code format: `SPGN-XXXX` where X is uppercase alphanumeric (A-Z, 0-9)
- Code expires after 48 hours
- Code is single-use (once someone joins, it's consumed)
- Owner can generate multiple codes (for different invitees)

### Joining
- Any authenticated user can enter a code on `/squads/join`
- Code must be valid (exists, not expired, not used)
- User must not already be a member of that squad
- On successful join: mark code as used (used_by, used_at), create membership

### Leaving
- Any member (except owner) can leave voluntarily
- Owner cannot leave — must delete the squad instead

### Deletion
- Only the owner can delete the squad
- Deletion cascades: removes all memberships and invite codes

---

## Privacy Model

### Visible to Squad Members (scoped leaderboard)

| Data | Source |
|------|--------|
| Username | User.username |
| Total score (points) | Leaderboard computation (existing logic) |
| Average score | Leaderboard computation |
| Grade (A/B/C) | Leaderboard computation |
| Session count (completed) | WorkoutSession count |
| Last session date | WorkoutSession.started_at (most recent) |
| Last session template | WorkoutSession.template_name_snapshot |
| Streak (consecutive days) | Computed from session dates |

### Strictly Private (never exposed outside the user)

| Data | Reason |
|------|--------|
| Body measurements (all) | Intimate body data |
| Readiness entries (all) | Personal health state |
| Bodyweight (per-session) | Body data |
| Session notes | Personal annotations |
| Body engineering dashboard score | Leaks readiness/measurement info indirectly |
| Set details (weight, reps) | Training specifics |
| Exercise success scores | Per-exercise feedback |
| Muscle sensation feedback | Per-exercise feedback |

---

## Routes

| Method | Path | Access | Action |
|--------|------|--------|--------|
| GET | `/squads` | Auth | List squads the user belongs to + create/join buttons |
| GET | `/squads/create` | Auth | Create form (name input) |
| POST | `/squads/create` | Auth | Create squad (becomes owner + first member) |
| GET | `/squads/join` | Auth | Join form (code input) |
| POST | `/squads/join` | Auth | Join via code |
| GET | `/squads/{id}` | Member only | Squad detail: members list + scoped leaderboard |
| POST | `/squads/{id}/invite` | Owner only | Generate invite code, display it |
| POST | `/squads/{id}/leave` | Member (not owner) | Leave the squad |
| POST | `/squads/{id}/delete` | Owner only | Delete the squad (cascade) |

### Access Control

- All routes require authentication (`CurrentUser` dependency)
- Squad detail (`/squads/{id}`) requires active membership — non-members get 403
- Owner-only actions check `membership.role == "owner"` — non-owners get 403

---

## Templates

| Template | Content |
|----------|---------|
| `squads_list.html` | User's squads as cards (name, member count, role badge). Buttons: "Créer une squad" + "Rejoindre avec un code" |
| `squad_detail.html` | Squad name, member list (username + role badge + last active), scoped leaderboard table. Owner section: invite code generator, delete button. Member section: leave button. |
| `squad_create.html` | Simple form: squad name + submit |
| `squad_join.html` | Simple form: invite code input + submit. Error messages for invalid/expired/used codes. |

### Navigation

Add "Squads" link in `base.html` navbar between "Dashboard" and "Board".

---

## Service Layer

### `app/services/squad.py`

**Squad CRUD:**
- `create_squad(db, owner_id, name) -> Squad` — validates name unique, owner limit (1), creates squad + owner membership
- `get_user_squads(db, user_id) -> list[Squad]` — squads where user is member
- `get_squad_detail(db, squad_id, user_id) -> dict | None` — returns squad info + members if user is member, None otherwise
- `delete_squad(db, squad_id, owner_id)` — validates ownership, cascading delete

**Invitation:**
- `generate_invite_code(db, squad_id, owner_id) -> str` — validates ownership, generates SPGN-XXXX code, expires in 48h
- `join_by_code(db, user_id, code) -> Squad | None` — validates code, creates membership, marks code used

**Membership:**
- `leave_squad(db, squad_id, user_id)` — validates not owner, removes membership

**Scoped Leaderboard:**
- `compute_squad_leaderboard(db, squad_id) -> list[dict]` — reuses existing leaderboard scoring logic but filtered to squad members only. Returns: rank, username, total_points, avg_points, grade, session_count, last_session_date, last_session_template, streak.

---

## Migration

Single Alembic migration creating the 3 new tables. No changes to existing tables.

---

## Files to Create/Modify

| File | Action |
|------|--------|
| `app/models/squad.py` | **New** — Squad, SquadMembership, SquadInviteCode |
| `app/models/__init__.py` | Modify — import squad |
| `app/database.py` | Modify — import squad |
| `app/services/squad.py` | **New** — CRUD, invitation, membership, scoped leaderboard |
| `app/routers/squads.py` | **New** — all squad routes |
| `app/main.py` | Modify — register squads router |
| `app/templates/squads_list.html` | **New** |
| `app/templates/squad_detail.html` | **New** |
| `app/templates/squad_create.html` | **New** |
| `app/templates/squad_join.html` | **New** |
| `app/templates/base.html` | Modify — nav link |
| `migrations/versions/20260413_add_squads.py` | **New** |
| `tests/test_squad_model.py` | **New** |
| `tests/test_squad_service.py` | **New** |
| `tests/test_squad_routes.py` | **New** |
| `tests/test_squad_privacy.py` | **New** |
| `docs/strategy/SPIGNOS_SQUADS_SPEC.md` | **New** |
| `docs/strategy/SPIGNOS_SQUADS_PRIVACY_MODEL.md` | **New** |
| `docs/SPRINT_S3_REPORT.md` | **New** |

---

## Risks

| Risk | Mitigation |
|------|------------|
| Code collision (SPGN-XXXX) | 36^4 = 1.6M possibilities. Check uniqueness on insert. Retry once on collision. |
| Scoped leaderboard performance | Same query pattern as global leaderboard but with WHERE user_id IN (squad members). Small group (~12) = negligible overhead. |
| Owner deletes squad while members have it open | Cascade delete removes memberships. Members see 404 on next load. No stale data risk. |
| Privacy leak via new routes | test_squad_privacy.py explicitly tests that body/readiness/weight data is absent from squad detail and leaderboard responses. |

---

## Acceptance Criteria

- [ ] User can create a squad (becomes owner)
- [ ] Owner can generate invite codes (SPGN-XXXX format)
- [ ] User can join a squad via valid invite code
- [ ] Squad detail page shows members + scoped leaderboard
- [ ] Non-members cannot access squad detail (403)
- [ ] No private data (measurements, readiness, weight, notes) is exposed in squad views
- [ ] Members can leave (except owner)
- [ ] Owner can delete squad (cascade)
- [ ] Expired/used invite codes are rejected
- [ ] Nav updated with "Squads" link
- [ ] All existing features unaffected
- [ ] All tests pass

---

## DO NOT BUILD

- Feed or activity stream
- Comments or reactions
- Direct messaging between members
- Public squad discovery / search
- Cross-squad rankings
- Squad-scoped body engineering scores
- Admin role (deferred — additive later)
- Squad profile pictures / avatars
