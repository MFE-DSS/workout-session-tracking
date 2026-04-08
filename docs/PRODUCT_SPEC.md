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

## Explicit non-goals (V1)

- Multi-user / auth (single user on a private VPS)
- Alembic migrations (schema evolves via wipe during V1; Alembic
  will be mandatory before the first real prod log)
- PWA offline
- Native apps
- Analytics dashboards (scaffolded in /progress, real widgets in V2+)
- Cardio-specific fields (duration, HR zones)
