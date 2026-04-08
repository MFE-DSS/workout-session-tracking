# Product Spec — V1

## North star

A personal hypertrophy logging app for a phone. One user. One gym.
Open it one-handed, pick a workout, log weights / reps / feedback
one tap at a time, close. Analytics later.

## Non-negotiables

1. **Templates, not weekdays.** The library is a set of reusable
   workout templates. The calendar is a projection of real sessions.
2. **Sessions are timestamps.** A session is born when the user
   taps "Démarrer" on a template. `started_at` is the single source
   of truth; weekday is derived.
3. **Normalized feedback.** Every feedback field is a controlled
   vocabulary (enum). Free text exists but is secondary, optional,
   and short.
4. **History survives.** Sessions snapshot the template / exercise
   names at creation time. Rewriting the catalog never orphans
   existing logs.
5. **Mobile first.** No JS required. Large tap targets. No
   horizontal scroll. Readable in low light.
6. **Persistence first.** If it's on screen, it's in SQLite. No
   local client state.

## Saisie levels (frozen)

| Level    | Fields                                                         |
|----------|----------------------------------------------------------------|
| Session  | concentration, global_state, bodyweight_kg, free_note (opt)    |
| Exercise | success_score, muscle_sensation, free_note (opt)               |
| Set      | weight_kg, reps, execution_quality, reps_target, technique, completed |

Free notes: 280 char max at session level, 140 char max at
exercise level, none at set level.

## Warmup strategy — V1 choice

**Option A: 2 warmup rows pre-populated for every exercise, every template.**
Rationale: uniform, deterministic, no branching on template kind.
Cardio templates (which have 0 exercises) naturally produce 0
warmup rows. The user leaves unused warmup lines at
`completed=False` if they only do 1 warmup or none.

Configurable through `app.services.session_builder.instantiate_session(warmup_sets=N)`.

## Session lifecycle

```
            POST /sessions
 template   ──────────────→  WorkoutSession
                              status=in_progress
                              started_at=now()
                              (pre-populated sub-tree)

                            GET/POST /sessions/{id}
                              user fills the cards

                            POST /sessions/{id}  (action=end)
                              status=completed
                              ended_at=now()
```

## Home tiles (action-oriented)

- **Reprendre** — shown only when an `in_progress` session exists
- **Nouvelle séance** — goes to /library
- **Historique**
- **Progression** (placeholder for V2)
- **Bibliothèque**
- **Règles**

## Completed-session rule (V1)

- A completed session (`status == "completed"`) **does not** appear
  in the home "Reprendre" tile. Only `in_progress` sessions do.
- It **does** stay visible in the history, and its detail page
  stays accessible.
- Its detail page stays **fully editable** in V1. The only visual
  difference is the status badge ("Terminée") and the replacement
  of the "Terminer la séance" button with a secondary "Rouvrir".
- Rationale: keeping the same form for both states avoids a
  parallel read-only template and the drift that would bring.
  If the user notices a mistake after ending a session, they can
  fix it in place.
- **Readability (Sprint 3)**: a completed session adds
  `session-page--completed` on the main container. Each
  exercise card shows a compact `done-summary` strip at the
  top ("Work : 3/3 · 60 / 62.5 / 55 kg · 10 / 8 / 12 reps ·
  score 80") and the editable inputs are slightly dimmed.
  The header gets a one-liner note "Séance terminée — éditable
  via Rouvrir".

## Exercise history identity rule (Sprint 4)

The "history of one exercise" groups SessionExercise rows by the
pair `(template_slug_snapshot, exercise_code_snapshot)`. This is
the SAME identity key that "Dernière fois" and the progression
hint already use, kept on purpose for coherence.

- No merging across templates. `E2` on Push A and `E2` on Pull B
  are two distinct identities.
- No merging by exercise name. If two templates spell the same
  name differently, they stay separate.
- The page at `GET /exercise-history/{template_slug}/{exercise_code}`
  lists every occurrence (both `in_progress` and `completed`),
  newest first, with a status badge so the two can be told apart.

## Delta rule (Sprint 4)

On the exercise history detail page, each row is compared to the
immediately NEXT-OLDER row in the same list. On the session detail
page, each exercise card's current first completed work set is
compared to the prior session's first completed work set (the
same one surfaced by "Dernière fois").

**Inputs** for each side:
- `weight_kg` of the first completed work set
- `reps` of the first completed work set
- `success_score` of the exercise card

**Output**: a `Delta` with three optional pieces, or None.

- `weight_delta = current - prior` if both weights are not None
- `reps_delta = current - prior` if both reps are not None
- `score_trend = "up" | "flat" | "down"` if both scores are not None
- delta is None if all three pieces are None (nothing to compare)

**Display format**: comma-joined with " · ".
- `+2.5 kg · +2 reps · score en hausse`
- `= kg · = reps · score stable`
- `-5 kg · -2 reps · score en baisse`
- Missing pieces are simply omitted

Round weights: `2.0` renders as `+2 kg`, not `+2.0 kg`.

## Progression hint rule (Sprint 3)

Each exercise card may show a short "Repère" block below the
"Dernière fois" block. The hint is secondary: it never replaces
the user's judgement, it never claims certainty, it contains no
AI-sounding language. It is a mechanical reference point.

**Inputs** (both required — otherwise no hint is shown):
- `target_min` and `target_max` of the *current* exercise's
  first rep target (via `SessionExercise.template_exercise`)
- `prior_reps` and `prior_weight_kg` of the *prior* session's
  first completed work set (via `last_time_by_exercise_code`)

**Rule**:
- If any input is missing -> no hint (empty)
- If `prior_reps >= target_max` -> "tenter d'augmenter la
  charge sur le premier set"
- If `prior_reps < target_min` -> "consolider la charge
  actuelle"
- Otherwise (prior hit the range but not the top) ->
  "viser {target_max} reps avant d'augmenter la charge"

The rule is implemented in `app/services/progression_hint.py`
and unit-tested.

## Last time rule (Sprint 2)

Each exercise card shows a compact "Dernière fois" block. The
identity used for the lookup is
`(template_slug_snapshot, exercise_code_snapshot)`:

- the current session is **strictly** excluded from its own lookup
- only **work** sets (never warmups) contribute
- only **completed** work sets with at least one of weight/reps
  populated are summarised
- the format chosen is **Option B**:
  `Dernière fois · il y a 5 j · 60 / 62.5 / 55 kg · 10 / 8 / 12 reps`
- empty states are rendered explicitly:
  - no prior session of the same template → "Aucune séance précédente"
  - prior session exists but had no completed work data →
    "aucune donnée saisie"

## KPI rules (Sprint 2)

- **sessions_this_week**: count of `workout_sessions.started_at >=`
  start of current ISO week (Monday 00:00 UTC). All statuses.
- **sessions_last_30**: count over a rolling 30-day window. All
  statuses.
- **completed_last_30**: same window, `status == "completed"` only.
- **avg_success_score_30d**: AVG of `SessionExercise.success_score`
  where the column IS NOT NULL, restricted to `completed`
  sessions started in the 30-day window.
- **completion_rate_30d**: ratio of `SetLog.completed=True` to
  total `SetLog` rows where `SetLog.kind == "work"`, restricted
  to `completed` sessions started in the 30-day window. Warmup
  rows never enter the numerator or the denominator.
- **In-progress sessions are excluded** from long-term averages
  and rates (they would otherwise drag metrics down with
  untouched rows). They are still counted in `sessions_this_week`
  and `sessions_last_30`.
- **NULL success_scores are excluded** from the average, not
  treated as zero.

## Invalid enum rule (V1)

Any POST value that is not in the whitelisted vocabulary for its
field is silently coerced to `NULL`. No 400 is returned. No
invalid value is ever persisted. This is acceptable in V1 because
the SSR UI only emits whitelisted values; invalid POSTs can only
come from direct curl/debug use and do not need a user-visible
error.

## Export rules

### `GET /export/sessions.json` (Sprint 3)
Returns every persisted session in a single JSON payload with a
`schema_version`. No auth (single-user V1), no filtering. Sorted
oldest-first so the file is append-friendly. The export is
intentionally not a round-trip import format for V1.

### `GET /export/sessions.csv` (Sprint 5)
Flat one-row-per-set CSV view of every session. Drops into a
spreadsheet without transformation. Sessions with zero exercises
(cardio) emit one row with empty exercise/set fields so they
still appear when filtering by template. Sessions with exercises
emit one row per `SetLog`, warmups before work, in `set_index`
order. Same denormalised parent columns on every row.

### `GET /export` (Sprint 5)
Small landing page that shows totals (sessions, completed,
work_sets_done, first/last date, schema version) and offers
download buttons for both formats. No filter, no granular UI.

Both formats share the same backup workflow documented in
`deploy/README.md` (SQLite `.backup` for rapid restore + JSON
or CSV dump for long-term archive).

## Mobile polish rules (Sprint 5)

The session detail page is the main daily-use surface. Sprint 5
locks in four small refinements:

1. **Exercise jump bar** at the top of the page: one chip per
   exercise card, showing `code` and `done/total` work sets.
   Coloured by state (`accent` = partial, `ok` = done). A final
   `FB` chip jumps to `#session-feedback`.
2. **Exercise card done state**: `exercise-card--done` class is
   applied when every work set in the card is `completed=True`
   (and there is at least one). Visual: green left border, green
   progress count.
3. **Warmup / work sub-headers**: each exercise card now groups
   its warmup rows under a `Warmup` heading and its work rows
   under a `Work` heading.
4. **After-save next-exercise redirect**: `POST
   /sessions/{id}/exercises/{se_id}` redirects to the next
   exercise's anchor (by `position`). When there is no next
   exercise, it lands on `#session-feedback`. This means the
   user just keeps tapping "Enregistrer" and walks down the
   session.

## Active session banner (Sprint 5)

When an `in_progress` session exists, every page outside `/`
and `/sessions/{id}` shows a small green banner at the top
that links back to that session. The home page does NOT show
the banner because it already has its own larger Reprendre
tile. The session detail page does NOT show it because the
user is already there.

## Explicit non-goals (V1)

- Multi-user / auth (single user on a private VPS)
- PWA offline
- Native apps
- Dashboards with charts (V1 ships KPI cards only — Chart.js is
  out of scope)
- Cardio-specific fields (duration, HR zones)
- Auto-computed reps_target (server-side defaulting from reps vs
  rep target range); V1 keeps the field user-controlled
- Import endpoint for the export (Sprint 3 only ships export;
  reverse direction is YAGNI until we actually need it)
- Smart coaching. The progression hint is a deterministic
  mechanical rule; V1 does not claim anything beyond that.
