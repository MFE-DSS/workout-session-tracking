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
