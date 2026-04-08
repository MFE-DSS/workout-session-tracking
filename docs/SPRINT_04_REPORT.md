# Sprint 04 — Exercise History, Delta, Alembic Drift Guard

Branch : `claude/sprint-reporting-fitness-app-V7Qr6`
Tests  : 95 passed (was 71)

## Shipped

- **Exercise history detail page** at
  `GET /exercise-history/{template_slug}/{exercise_code}`. Lists
  every occurrence of one identity (newest first), with status
  badge, completed work sets summary, success_score and
  muscle_sensation badges, and a per-row delta vs the next-older
  row. Empty state is explicit.

- **Delta surface on session detail**: next to "Dernière fois",
  each exercise card now shows a compact "Delta" block comparing
  the current first completed work set to the prior session's
  first completed work set (same identity key). Rendered only
  when at least one piece is comparable.

- **Delta rule (frozen)**: pure functions in
  `app/services/delta.py` (`compute_delta`, `format_delta`).
  Documented in `docs/PRODUCT_SPEC.md`. Non-null pieces joined
  with `" · "`, zeros shown as `"="`, signed integers when the
  delta is exact (`+2 kg`, not `+2.0 kg`).

- **Navigation**: the exercise code badge in each session-detail
  card is now a link to `/exercise-history/{slug}/{code}`. The
  "Activité récente par exercice" rows on `/progress` are also
  clickable and point to the same page.

- **History / resume duration**:
  - Home "Reprendre" tile now reads
    "Reprendre · en cours / Push A · démarrée le 08/04 18:30 · depuis 1 h 15".
  - History rows show a `"depuis Xh Ymin"` or `"durée Xh Ymin"`
    badge depending on status.
  - New `app/services/time_format.py` helper (SQLite-naive-datetime
    safe).

- **Alembic drift guard**:
  - `tests/test_alembic_drift.py` applies the full migration
    chain to a temp DB and calls `compare_metadata` against
    `Base.metadata`. Zero diff required to pass.
  - `migrations/env.py` hardened: a pre-set `sqlalchemy.url` on
    the Alembic `Config` is now respected (otherwise the test
    would be fighting `get_settings()` underneath).
  - `scripts/check_alembic_drift.py` — CLI-style wrapper for
    pre-commit hooks. Exits 0/1, prints the diff on failure.
  - `alembic.ini`: added `path_separator = os` to silence a
    deprecation warning introduced by Alembic 1.18+.

- 24 new tests (71 -> 95). New files:
  test_delta.py (9), test_exercise_history.py (13),
  test_alembic_drift.py (2).

## Decisions

### Delta identity = same as last-time
`(template_slug_snapshot, exercise_code_snapshot)`. Keeps cross-
template separation (E2 Push A vs E2 Pull B) and survives catalog
rewrites via snapshots. Consistent with Sprint 2 and Sprint 3.

### Delta anchor = first completed work set
Same anchor as the progression hint. Simple, sober, documented.
Picking the "best" set would require a best-of rule that is
subjective; picking set_index=1 is mechanical.

### Exercise history list includes in_progress
Both in_progress and completed sessions show up on the exercise
history page, with a status badge. The user can spot their
current attempt next to past ones. Deltas still only render when
both compared rows have a first completed work set.

### Drift guard placement
In pytest + a standalone script. Keeping it in pytest means a
regular `pytest -q` catches it; the standalone script is the
pre-commit entry point that doesn't require pytest.

### Duration display
Minimal helper, no localization, no seconds. `"{m} min"` below an
hour, `"{h} h {mm}"` above. Naive-datetime safe.

## Files

### Created
- `app/services/delta.py`
- `app/services/exercise_history.py`
- `app/services/time_format.py`
- `app/templates/exercise_history.html`
- `scripts/check_alembic_drift.py`
- `tests/test_alembic_drift.py`
- `tests/test_delta.py`
- `tests/test_exercise_history.py`
- `docs/SPRINT_04_REPORT.md`

### Modified
- `app/services/stats.py` — `last_time` entries now expose
  `success_score` and `session_id` too.
- `app/routers/sessions.py` — import delta + exercise_history,
  compute per-card delta_labels, new `/exercise-history/...`
  route.
- `app/routers/pages.py` — compute home open_since, history
  durations, keep passing recent_activity to /progress.
- `app/templates/session_detail.html` — clickable exercise code,
  new Delta block inside each card.
- `app/templates/progress.html` — activity rows are now links
  to the exercise history page.
- `app/templates/index.html` — Reprendre tile shows duration.
- `app/templates/history.html` — duration badge per row.
- `app/static/css/app.css` — `.delta`, `.badge--delta`,
  `.exercise-card__code--link`, `.history-list`, `.history-row`,
  `.history-row__*` styles.
- `migrations/env.py` — respect pre-set `sqlalchemy.url`.
- `alembic.ini` — `path_separator = os` (silences deprecation).
- `docs/PRODUCT_SPEC.md` — new "Exercise history identity rule"
  and "Delta rule" sections.
- `docs/DOMAIN_MODEL.md` — read-side helpers updated + Alembic
  drift guard section.
- `docs/ARCHITECTURE.md` — services layout updated + drift guard
  subsection under Alembic workflow.
- `README.md` — Sprint 4 report link.

### Deleted
None.

## Tests

```
tests/
  test_health.py                    1
  test_library.py                   9
  test_session_schema.py            2
  test_session_builder.py           4
  test_session_flow.py             17
  test_last_time.py                 6
  test_kpis.py                      7
  test_history_upgrade.py           6
  test_progression_hint.py         10
  test_export.py                    4
  test_past_session_readability.py  5
  test_delta.py                     9  ← new
  test_exercise_history.py         13  ← new
  test_alembic_drift.py             2  ← new
  -----                            --
  total                            95
```
