# Domain Model

## Tables

```
workout_templates
  id, slug (UNIQUE), name, kind, focus, cardio_note,
  suggested_label  ← hint only, non-structural

template_exercises
  id, template_id FK(CASCADE), position,
  code, name, set_scheme, notes
  UNIQUE (template_id, position)

rep_targets
  id, template_exercise_id FK(CASCADE),
  set_index, min_reps, max_reps, technique
  UNIQUE (template_exercise_id, set_index)

reference_docs
  id, version (UNIQUE), title, seeded_at

method_rules
  id, slug (UNIQUE), position, title, body

workout_sessions
  id
  template_id FK(SET NULL)          ← nullable, resilience
  template_slug_snapshot   NOT NULL ← denormalized
  template_name_snapshot   NOT NULL ← denormalized
  started_at DATETIME NOT NULL (INDEX)
  ended_at DATETIME NULL
  status VARCHAR(16) NOT NULL       ← in_progress | completed
  concentration, global_state       ← normalized enums, nullable
  bodyweight_kg FLOAT NULL
  free_note VARCHAR(280) NULL
  created_at DATETIME
  @property weekday_iso             ← derived from started_at

session_exercises
  id
  session_id FK(CASCADE)
  template_exercise_id FK(SET NULL) ← nullable, resilience
  exercise_code_snapshot   NOT NULL ← denormalized
  exercise_name_snapshot   NOT NULL ← denormalized
  position
  success_score INT NULL            ← 100|80|50
  muscle_sensation VARCHAR(16) NULL ← strong|partial|weak
  free_note VARCHAR(140) NULL
  UNIQUE (session_id, position)

set_logs
  id
  session_exercise_id FK(CASCADE)
  kind VARCHAR(8) NOT NULL          ← warmup|work
  set_index
  weight_kg FLOAT NULL
  reps INT NULL
  technique VARCHAR(8) NULL         ← RP|DS
  execution_quality VARCHAR(16) NULL
  reps_target VARCHAR(16) NULL
  completed BOOL NOT NULL
  UNIQUE (session_exercise_id, kind, set_index)
```

## Relationship diagram

```
WorkoutTemplate 1 ─── * TemplateExercise 1 ─── * RepTarget
       ▲                        ▲
       │ SET NULL               │ SET NULL
       │                        │
WorkoutSession  1 ─── * SessionExercise 1 ─── * SetLog
```

## Resilience guarantees

- Any write to a `*_snapshot` column happens **once**, at creation
  time, from the server.
- FKs towards the catalog are `ON DELETE SET NULL`. The catalog
  may be wiped and reseeded at any time; historical sessions
  lose only their "reference pointer", never their identity or
  their values.
- SQLite enforces FK cascades because `database.py` installs
  a `PRAGMA foreign_keys=ON` listener on every connection.

## Normalized enum vocabularies

See `app/enums.py` for the single source of truth.

| Field             | Values                                    |
|-------------------|-------------------------------------------|
| template kind     | strength, cardio                          |
| technique         | RP, DS                                    |
| set kind          | warmup, work                              |
| session status    | in_progress, completed                    |
| concentration     | high, medium, low                         |
| global_state      | good, flat, fatigued                      |
| success_score     | 100, 80, 50 (int)                         |
| muscle_sensation  | strong, partial, weak                     |
| execution_quality | clean, acceptable, degraded               |
| reps_target       | target_hit, target_near, target_missed    |

## Read-side helpers (Sprint 2 + 3)

- `app/services/stats.py::last_time_by_exercise_code(db, session, now)`
  returns a dict keyed by `exercise_code_snapshot` pointing at a
  compact summary of the previous session of the same template.
  One SQL query fetches every prior SessionExercise of the same
  template; Python keeps the first hit per code. Each entry
  includes a `first_set: {weight_kg, reps}` field used by the
  progression hint.

- `app/services/stats.py::summarise_current_exercise(se)` returns
  a compact `{work_done, work_total, weights_str, reps_str,
  success_score, muscle_sensation}` dict for completed-session
  rendering. None if the exercise has no completed work set.

- `app/services/progression_hint.py::compute_progression_hint(...)`
  is a pure function: deterministic rule, easily unit-tested.
  See docs/PRODUCT_SPEC.md for the rule text.

- `app/services/kpis.py::compute_global_kpis(db)` returns a
  `GlobalKPIs` dataclass with the rolling 30-day indicators
  (see docs/PRODUCT_SPEC.md for the aggregation rules).

- `app/services/kpis.py::compute_template_kpis(db)` groups
  completed sessions by `template_slug_snapshot` so history
  survives catalog rewrites.

- `app/services/kpis.py::compute_recent_exercise_activity(db, limit)`
  returns a list of `RecentExerciseActivity` rows (one per
  (template_slug, exercise_code) pair) with the number of
  completed sessions in the last 30 days and the weights/reps
  of the most recent completed work sets. Feeds the
  "Activité récente par exercice" section on /progress.

## Schema evolution — Alembic (Sprint 2)

Starting Sprint 2 the schema is managed by Alembic. The baseline
migration in `migrations/versions/` captures the state of all
tables at the end of Sprint 1. Future changes must ship a
migration via `alembic revision --autogenerate -m "message"`
plus manual review before commit.

SQLite compatibility: `env.py` enables `render_as_batch=True`
for SQLite engines, which makes Alembic rewrite ALTER TABLE
operations using the copy-and-rename dance that SQLite needs.
