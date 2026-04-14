# S4 Design Spec — Challenges, Compare Mode, Template Sharing

**Date:** 2026-04-14
**Sprint:** S4_challenges_compare_sharing
**Status:** Approved
**Prerequisite:** S3 (private squads)

---

## Context

S3 delivered private squads with invite codes and scoped leaderboards. S4 adds the engagement loops: challenges (time-boxed competitions), compare mode (1:1 face-off), and template/session sharing (motivation by example). Share cards were dropped — no value in a private cockpit.

## Decisions Log

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Challenge metric | Owner chooses: sessions, score, tonnage, or streak | Flexibility for different group dynamics |
| Compare mode content | Side-by-side leaderboard metrics table | Simple, reuses existing data, no new scoring |
| Share cards | Dropped | No value in a private product. Leaderboard + challenges cover motivation. |
| Template sharing | Recommend template + share anonymized session resume | Template = point to catalogue. Session = show exercises + scores, NO weights/reps/notes. |

---

## S4a — Private Challenges

### Data Model

**Table: `squad_challenges`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PK |
| squad_id | INTEGER | FK → squads.id (CASCADE), NOT NULL |
| created_by | INTEGER | FK → users.id, NOT NULL |
| title | VARCHAR(128) | NOT NULL |
| metric | VARCHAR(32) | NOT NULL — "sessions", "score", "tonnage", "streak" |
| starts_at | DATE | NOT NULL |
| ends_at | DATE | NOT NULL |
| created_at | DATETIME(tz) | server_default=now() |

No materialized standings table — computed live from session data in the challenge window.

### Metric Computation

| Metric | Formula | Source |
|--------|---------|--------|
| `sessions` | COUNT of completed, non-excluded sessions in [starts_at, ends_at] | WorkoutSession |
| `score` | SUM of session_points (quality * completion_ratio) per member | Same as leaderboard scoring |
| `tonnage` | SUM of (weight_kg * reps) across all completed work sets | SetLog |
| `streak` | Longest consecutive days with a session in [starts_at, ends_at] | WorkoutSession dates |

### Routes

| Method | Path | Access |
|--------|------|--------|
| GET | `/squads/{id}/challenges` | Member |
| GET | `/squads/{id}/challenges/create` | Owner |
| POST | `/squads/{id}/challenges/create` | Owner |
| GET | `/squads/{id}/challenges/{cid}` | Member |

### Rules

- Only squad owner can create challenges
- Challenge has start date and end date (flexible duration, not forced to calendar month)
- Standings computed live — no cron, no materialization
- Past challenges remain visible as historical records
- A squad can have multiple challenges (active and past)

### Templates

- `squad_challenges.html` — list of active + past challenges
- `squad_challenge_create.html` — form: title, metric (select), start date, end date
- `squad_challenge_detail.html` — title, metric, dates, standings table (rank, username, value)

---

## S4b — Compare Mode

### Route

`GET /squads/{id}/compare?a={user_id}&b={user_id}`

### Access

Member of the squad only. Both compared users must be members.

### Content

Side-by-side table:

| Metric | Member A | Member B |
|--------|----------|----------|
| Username | — | — |
| Total score | X | Y |
| Avg score | X | Y |
| Grade | A/B/C | A/B/C |
| Sessions | N | N |
| Streak | N days | N days |
| Last session | date + template | date + template |

Same data as the squad scoped leaderboard, filtered to 2 members.

### UI

On the squad detail page, a "Comparer" section with two member select dropdowns and a "Comparer" button. Submits as GET with query params.

### Template

- `squad_compare.html` — two-column comparison table

---

## S4c — Template Sharing

### Data Model

**Table: `squad_template_recommendations`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PK |
| squad_id | INTEGER | FK → squads.id (CASCADE), NOT NULL |
| user_id | INTEGER | FK → users.id, NOT NULL |
| template_slug | VARCHAR(64) | NOT NULL |
| template_name | VARCHAR(128) | NOT NULL (snapshot) |
| note | VARCHAR(280) | nullable |
| created_at | DATETIME(tz) | server_default=now() |

**Table: `squad_shared_sessions`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PK |
| squad_id | INTEGER | FK → squads.id (CASCADE), NOT NULL |
| user_id | INTEGER | FK → users.id, NOT NULL |
| session_id | INTEGER | FK → workout_sessions.id, NOT NULL |
| created_at | DATETIME(tz) | server_default=now() |

### Privacy rules for shared sessions

The shared session display shows ONLY:
- Username of the sharer
- Template name
- Session date
- List of exercises: code + name (actual, not prescribed if substituted) + derived success_score
- Session status (completed/in_progress)

**NEVER shown:**
- weight_kg (per set)
- reps (per set)
- bodyweight_kg
- free_note (session or exercise)
- muscle_sensation
- readiness data
- body measurements

### Routes

| Method | Path | Access |
|--------|------|--------|
| POST | `/squads/{id}/recommend` | Member |
| POST | `/squads/{id}/share-session` | Member |

Both redirect back to squad detail. Recommendations and shared sessions appear in an "Activité" section on the squad detail page.

### Templates

The squad detail page gains an "Activité" section showing:
- Template recommendations: "{username} recommande {template_name}" + optional note + link to `/library/{slug}`
- Shared sessions: "{username} a partagé {template_name} du {date}" + exercise list with scores

---

## Files to Create/Modify

| File | Action |
|------|--------|
| `app/models/challenge.py` | **New** — SquadChallenge |
| `app/models/sharing.py` | **New** — SquadTemplateRecommendation, SquadSharedSession |
| `app/models/__init__.py` | Modify — import new modules |
| `app/database.py` | Modify — import new modules |
| `app/services/challenge.py` | **New** — create_challenge, compute_standings (4 metrics) |
| `app/services/sharing.py` | **New** — recommend_template, share_session, get_squad_activity |
| `app/services/compare.py` | **New** — compute_comparison(db, squad_id, user_a, user_b) |
| `app/routers/squads.py` | Modify — add challenge, compare, sharing routes |
| `app/templates/squad_detail.html` | Modify — add challenges summary, activity section, compare form |
| `app/templates/squad_challenges.html` | **New** |
| `app/templates/squad_challenge_create.html` | **New** |
| `app/templates/squad_challenge_detail.html` | **New** |
| `app/templates/squad_compare.html` | **New** |
| `migrations/versions/...` | **New** — 3 tables |
| `tests/test_challenge.py` | **New** |
| `tests/test_compare.py` | **New** |
| `tests/test_sharing.py` | **New** |
| `tests/test_s4_privacy.py` | **New** |
| `docs/strategy/SPIGNOS_CHALLENGES_SPEC.md` | **New** |
| `docs/strategy/SPIGNOS_COMPARE_MODE_SPEC.md` | **New** |
| `docs/SPRINT_S4_REPORT.md` | **New** |

---

## Risks

| Risk | Mitigation |
|------|------------|
| Live standings computation is slow for tonnage metric | Query is scoped to squad members (~12) in a date window. Small dataset. |
| Shared session leaks private data | Privacy test suite verifies absence of weights/reps/notes in rendered HTML |
| Multiple active challenges create confusion | UI groups active vs past clearly |
| Compare mode exposes tonnage indirectly | Compare only shows leaderboard metrics (score, sessions, streak). Tonnage visible only in challenge standings when metric=tonnage. |

---

## Acceptance Criteria

- [ ] Squad owner can create a challenge (title, metric, dates)
- [ ] Challenge standings computed correctly for all 4 metrics
- [ ] Past challenges visible as history
- [ ] Compare mode shows side-by-side metrics for 2 squad members
- [ ] Non-members cannot access compare or challenges (403)
- [ ] Any member can recommend a template to the squad
- [ ] Any member can share a session (anonymized — no weights/reps)
- [ ] Activity section on squad detail shows recommendations + shared sessions
- [ ] No private data leaked in any squad view
- [ ] All existing tests pass

---

## DO NOT BUILD

- Share cards / visual exports
- Challenge notifications / reminders
- Challenge comments / reactions
- Auto-challenge creation (recurring)
- Template creation by users (only catalogue templates can be recommended)
- Cross-squad challenges
