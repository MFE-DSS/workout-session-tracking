# Sprint 01 — Session Creation, Exercise Cards, Normalized Logging

Branch : `claude/sprint-reporting-fitness-app-V7Qr6`
Tests  : 33 passed

## Shipped

- `POST /sessions` : creates a `WorkoutSession` from a template
  slug via `session_builder.instantiate_session`, snapshots
  template name/slug, redirects to `GET /sessions/{id}`.
- `GET /sessions/{id}` : mobile-first logging page. Header with
  template name, started_at, derived weekday, status badge,
  `X/Y work sets` progress. One card per exercise.
- `POST /sessions/{id}` : saves session-level feedback
  (concentration, global_state, bodyweight_kg, free_note), and
  optionally ends (`action=end`) or reopens (`action=reopen`)
  the session.
- `POST /sessions/{id}/exercises/{se_id}` : saves one exercise
  card in one shot — exercise-level feedback + all its warmup
  and work sets in a single POST.
- `GET /rules` : full rule list, seeded from
  `data/method_rules.json` (8 cards).
- Inline method reminder on the session page (first 3 rules as
  `<details>`).
- `GET /history` upgraded : per-session card with status badge,
  concentration, global_state, click-through to `/sessions/{id}`.
- Home resume tile links directly to the in-progress session.
- New enum `SessionStatus` (in_progress, completed), new column
  `workout_sessions.status`.
- New Jinja macros `_macros.html::segmented()` and
  `field_group()`.
- Full CSS update for session detail (segmented controls styled
  via `:has(input:checked)`, 44px tap targets, grid set rows).
- New tests (17 new) — `tests/test_session_flow.py` covering
  all 12 acceptance criteria.

## Form strategy chosen

**Sauvegarde par carte exercice + petit formulaire session-level.**

Justification: mobile ergonomics (user fills an exercise in one
natural block); no JS required; robust to flaky gym Wi-Fi;
small individual forms (~15-25 fields per exercise card); no
monolithic whole-session form. No per-set PATCH API because
the product explicitly preferred simple and robust over
sophisticated.

## Warmup strategy chosen

**Option A: 2 warmup rows pre-populated for every exercise of
every template.** Uniform, deterministic, zero branching on
template kind. Cardio templates (0 exercises) naturally produce
0 warmup rows. Configurable via `instantiate_session(warmup_sets=N)`.

## Files

### Created

- `app/routers/sessions.py`
- `app/services/form_parsing.py`
- `app/templates/_macros.html`
- `app/templates/session_detail.html`
- `app/templates/rules.html`
- `data/method_rules.json`
- `tests/test_session_flow.py`
- `docs/PRODUCT_SPEC.md`
- `docs/DOMAIN_MODEL.md`
- `docs/ARCHITECTURE.md`
- `docs/SPRINT_01_REPORT.md`

### Modified

- `app/enums.py` — +SessionStatus
- `app/models/catalog.py` — +MethodRule
- `app/models/session.py` — +WorkoutSession.status,
  +SessionExercise.template_exercise relationship
- `app/main.py` — include sessions router, seed method rules
- `app/services/seed.py` — +seed_method_rules()
- `app/services/session_builder.py` — set status=in_progress
- `app/routers/pages.py` — latest_open_session filters on status
- `app/templates/base.html` — +Règles link
- `app/templates/index.html` — +Rules tile, resume links to detail
- `app/templates/library.html` — +start form per template
- `app/templates/history.html` — click-through cards, status badge
- `app/static/css/app.css` — session detail CSS
- `README.md`

### Deleted

None.

## Tests

```
tests/
  test_health.py              1
  test_library.py             9
  test_session_schema.py      2
  test_session_builder.py     4
  test_session_flow.py       17  ← new
  ----                        --
  total                      33
```

Previous run: 16. This sprint: 33. All green.

## Notes for the next sprint

- Alembic is now critical. Any schema change after the first
  real prod log will need a migration path.
- The "last time we did this exercise" suggestion (progressive
  overload assist) is the natural Sprint 2 feature.
- `/progress` is still a stub. With real sessions in the DB, we
  can start building KPIs: success_score averages, work set
  completion rate, execution_quality distribution, etc.
