# Body Measurement Tracking — Design Spec

**Date:** 2026-04-12
**Scope:** Time-series body measurements with evolution graphs and muscle-template mapping on /profile

## Decisions

- 6 measurements: weight, chest, arm (biceps), waist, thigh, calf
- All on `/profile` (no new route)
- New table `body_measurements` (time-series, not static fields)
- Muscle → template mapping hardcoded (dict matching against template `focus`)
- Partial entry allowed (fill only what you measured)
- Existing static profile fields (height, hr, bp) remain on User model

## Constraints

- No new routes
- No JS
- No modification to session flow
- Additive migration only

---

## 1. Data Model

### New table: `body_measurements`

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| `id` | Integer | PK | Auto-increment |
| `user_id` | Integer | NOT NULL | FK → users.id ON DELETE CASCADE |
| `measured_at` | DateTime(tz) | NOT NULL | Date of the measurement (user-chosen) |
| `weight_kg` | Float | NULL | Body weight in kg |
| `chest_cm` | Float | NULL | Chest circumference |
| `arm_cm` | Float | NULL | Arm circumference (contracted biceps) |
| `waist_cm` | Float | NULL | Waist circumference |
| `thigh_cm` | Float | NULL | Thigh circumference |
| `calf_cm` | Float | NULL | Calf circumference |
| `created_at` | DateTime(tz) | NOT NULL | Server timestamp, DEFAULT now() |

**Index:** `(user_id, measured_at DESC)` — covers all timeline queries.

**Design rules:**
- One row = one measurement session (all 6 fields in one INSERT)
- All measurement fields nullable (partial entry OK)
- `measured_at` is the real date, `created_at` is the insertion timestamp
- FK cascade: delete user → delete all measurements

### New model file: `app/models/measurement.py`

SQLAlchemy model `BodyMeasurement` with columns as above.

### Migration

Additive CREATE TABLE + CREATE INDEX. No DROP, no ALTER on existing tables.

### Existing User fields

`height_cm`, `weight_kg`, `resting_hr`, `waist_cm`, `bp_systolic`, `bp_diastolic` stay on User. They serve a different purpose (static medical/reference profile). The body measurement table tracks evolution over time.

---

## 2. Service: `app/services/measurements.py`

### Muscle → Measurement Mapping

```python
MEASUREMENT_MUSCLE_MAP = {
    "weight_kg": [],
    "chest_cm": ["pectoral", "pectoraux", "pecs"],
    "arm_cm":   ["biceps", "triceps", "bras"],
    "waist_cm": ["abdos", "abs", "cardio"],
    "thigh_cm": ["jambes", "quadriceps", "cuisses"],
    "calf_cm":  ["mollets", "jambes"],
}
```

Labels for display:

```python
MEASUREMENT_LABELS = {
    "weight_kg": "Poids (kg)",
    "chest_cm": "Tour de poitrine (cm)",
    "arm_cm": "Tour de bras (cm)",
    "waist_cm": "Tour de taille (cm)",
    "thigh_cm": "Tour de cuisses (cm)",
    "calf_cm": "Tour de mollets (cm)",
}
```

### Functions

**`find_related_templates(field_name: str, templates: list[WorkoutTemplate]) -> list[str]`**
- Takes a measurement field name and list of catalog templates
- Matches keywords from `MEASUREMENT_MUSCLE_MAP[field_name]` against `template.focus` (case-insensitive substring)
- Returns list of template names (e.g., `["Push A", "Push B"]`)
- Returns empty list for `weight_kg` (global, not muscle-specific)

**`get_measurement_history(db: Session, user_id: int, limit: int = 20) -> list[BodyMeasurement]`**
- Returns last N measurements ordered by `measured_at DESC`

**`get_latest_measurement(db: Session, user_id: int) -> BodyMeasurement | None`**
- Returns most recent measurement (for form pre-fill)

**`get_measurement_series(db: Session, user_id: int, field: str, limit: int = 20) -> list[tuple[datetime, float]]`**
- Returns `(measured_at, value)` pairs for a single field, non-null only
- Ordered by `measured_at ASC` (for timeline charts)
- Used to build per-field SVG graphs

---

## 3. Timeline Graphs

Reuse the existing `_build_svg()` function from `app/services/timeline.py`.

New function: **`build_measurement_timeline_svg(points: list[TimelinePoint], title: str) -> str`**
- Similar to `build_bodyweight_timeline_svg` (auto-ranged Y axis)
- Custom title parameter (e.g., "Tour de poitrine")
- Color: `--accent` (#f25f3a) for all measurement charts (consistent)
- Returns empty string if fewer than 2 points

Build 6 SVG strings in the route, one per measurement field.

---

## 4. Route Integration

### `GET /profile` — enriched

Additional data loaded and passed to template:
- `latest_measurement`: most recent BodyMeasurement (for form pre-fill)
- `measurement_charts`: dict of 6 SVG strings `{"weight_kg": "<svg>...", "chest_cm": "<svg>...", ...}`
- `related_templates`: dict of 6 lists `{"weight_kg": [], "chest_cm": ["Push A", "Push B"], ...}`

### `POST /profile/measurements` — new endpoint

- Accepts form: `measured_at` (date string), `weight_kg`, `chest_cm`, `arm_cm`, `waist_cm`, `thigh_cm`, `calf_cm`
- Parses date, validates ranges (weight 30-300, circumferences 10-200)
- Creates `BodyMeasurement` row
- Redirects to `/profile`

---

## 5. Template: profile.html

Replace the "Profil physique" section (body-profile form) with:

### Section "Mesures corporelles"

**Formulaire "Nouvelle mesure"** in a `.card`:
- Date input (`measured_at`, default: today)
- 6 number inputs in `.body-profile` grid (2 columns)
- Pre-filled with latest measurement values (or empty)
- Labels: "Poids (kg)", "Poitrine (cm)", "Bras (cm)", "Taille (cm)", "Cuisses (cm)", "Mollets (cm)"
- Submit button "Enregistrer la mesure"

**Graphes d'évolution** below the form:
- 6 mini cards in a grid (2 columns desktop, 1 column mobile)
- Each card: title + SVG timeline + "Programmes associés : X, Y" text muted
- If < 2 data points: "Pas encore de données"

### Section "Profil médical" (reduced)

Keep static fields on User: `height_cm`, `resting_hr`, `bp_systolic`, `bp_diastolic`. Smaller form, labeled "Données de référence". Existing `POST /profile/body` endpoint continues to work but with fewer fields (remove `weight_kg` and `waist_cm` which are now tracked temporally).

---

## 6. Files Summary

| Action | File |
|--------|------|
| Create | `app/models/measurement.py` — BodyMeasurement model |
| Create | `app/services/measurements.py` — CRUD + muscle mapping |
| Create | `migrations/versions/20260412_add_body_measurements.py` |
| Create | `tests/test_measurements.py` |
| Modify | `app/services/timeline.py` — add `build_measurement_timeline_svg()` |
| Modify | `app/routers/auth_routes.py` — enrich profile + POST /profile/measurements |
| Modify | `app/templates/profile.html` — measurement form + graphs + reduced static profile |
| Modify | `app/static/css/app.css` — `.measurement-grid` for 2-col graph layout |
