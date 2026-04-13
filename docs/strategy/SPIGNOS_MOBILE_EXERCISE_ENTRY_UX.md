# SPIGNOS Mobile Exercise Entry UX Spec

**Sprint:** Sx_02_mobile_exercise_entry_ux_spec
**Date:** 2026-04-14
**Status:** Spec approved, pending build
**Prerequisite:** Sb_01 (feedback signal refactor) — complete

---

## 1. Problem Statement

The session detail page displays all 7 exercise cards as a flat wall of forms. Post-Sb01, each card has ~16 inputs. With 7 exercises: ~112 inputs on a single page. On mobile, the user scrolls constantly through a long page, losing context of where they are.

Additionally, the session feedback form (concentration, global_state, "Terminer") sits BEFORE the exercises — forcing users to scroll past it to reach their first exercise.

## 2. Decision Log

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Visual model | Active exercise unique via `<details>` | Proven HTML pattern in SPIGNOS. Zero JS possible. Focus on one exercise at a time. |
| Compact view | Code + name + progress + set resume | Enough info to know status without opening. Reuses existing done-summary pattern. |
| Session feedback position | Moved to bottom | Natural gym flow: exercises first, then global feedback + "Terminer". |

---

## 3. Target UX Flow

```
Open session → E1 expanded (active), E2-E7 compact
Fill E1 sets → tap "Enregistrer E1"
  POST → redirect → /sessions/{id}?active={E2_id}#exercise-{E2_id}
E2 expanded, E1 collapsed with resume
...repeat for E3-E7...
After E7 → redirect → /sessions/{id}#session-feedback
Fill concentration + global_state + bodyweight
Tap "Terminer la séance"
```

At any time: user can manually open any `<details>` to revisit a previous exercise, or use the jump bar.

---

## 4. Technical Mechanism

### Zero JS approach using `<details open>`

Each exercise card is wrapped in a `<details>` element. The server determines which one gets the `open` attribute.

**Active exercise determination** (in `session_detail` route):

1. Check `?active={id}` query parameter (set by the redirect after save)
2. If no param: find the first exercise where `done < total` (first non-complete)
3. If all exercises are done: no exercise is auto-opened (user goes to feedback)

**Redirect from `update_exercise_card`:**

Current: `f"/sessions/{session_id}#exercise-{next_se.id}"`
New: `f"/sessions/{session_id}?active={next_se.id}#exercise-{next_se.id}"`

When there's no next exercise:
Current: `f"/sessions/{session_id}#session-feedback"`
New: `f"/sessions/{session_id}#session-feedback"` (unchanged — no active param needed)

### No lock-in

The `<details>` elements remain manually openable/closable. The server just pre-opens one. If the user opens two at once, that's fine — it's HTML, not an app state.

---

## 5. Template Structure

### Exercise card — `<details>` wrapper

```html
<details class="card exercise-card {state_classes}"
         id="exercise-{se.id}"
         {% if is_active %}open{% endif %}>

  <!-- SUMMARY: always visible (compact view) -->
  <summary class="exercise-card__compact">
    <span class="exercise-card__code">{code}</span>
    <span class="exercise-card__name">{name}</span>
    <span class="exercise-card__progress">{done}/{total}</span>
    {% if done > 0 and summary %}
      <span class="exercise-card__recap">
        {weights_str} kg · {reps_str} reps
      </span>
    {% endif %}
  </summary>

  <!-- DETAIL: visible when open (full form) -->
  <form method="post" action="...">
    <!-- set_scheme, last-time, delta, hint -->
    <!-- warmup sets, work sets -->
    <!-- muscle_sensation (collapsed), free_note -->
    <!-- submit button -->
  </form>
</details>
```

### Session feedback — moved to bottom

The entire `<form id="session-feedback">` block moves from before the exercise loop to after it. No structural changes to the form itself.

### Page order (new)

```
1. session-header (title, meta, progress)
2. ex-jump (jump bar, sticky)
3. exercise cards (7x <details>, one open)
4. session-feedback (concentration, global_state, bodyweight, note, Terminer/Rouvrir)
5. method-reminder (rules, collapsed)
```

---

## 6. CSS Changes

### New: compact summary styling

```css
.exercise-card__compact {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  cursor: pointer;
  list-style: none; /* remove default <details> marker */
}

.exercise-card__compact::-webkit-details-marker {
  display: none;
}

.exercise-card__recap {
  font-size: 12px;
  color: var(--fg-dim);
  margin-left: auto;
}
```

### Existing: exercise-card as `<details>`

The `.exercise-card` class already applies to the card. When it's a `<details>`, the visual appearance stays the same. The `<summary>` replaces the old `<header>` as the always-visible part.

### Done/partial states

Keep existing `.exercise-card--done` class on the `<details>` element. The compact summary inherits the visual state (green border, dimmed text, etc.).

---

## 7. Route Changes

### `session_detail` (GET)

Add `active_exercise_id` computation:

```python
active_exercise_id = None
active_param = request.query_params.get("active")
if active_param:
    try:
        active_exercise_id = int(active_param)
    except (ValueError, TypeError):
        pass

if active_exercise_id is None:
    # Default: first non-complete exercise
    for se in session.session_exercises:
        done, total = stats["per_exercise"][se.id]
        if total == 0 or done < total:
            active_exercise_id = se.id
            break
```

Pass `active_exercise_id` to the template context.

### `update_exercise_card` (POST)

Change redirect URL to include `?active=`:

```python
if next_se is not None:
    target = f"/sessions/{session_id}?active={next_se.id}#exercise-{next_se.id}"
else:
    target = f"/sessions/{session_id}#session-feedback"
```

---

## 8. Files Impacted

### Must change (build Sb_02)

| File | Change |
|------|--------|
| `app/templates/session_detail.html` | **Refactor** — wrap exercise cards in `<details>`, add compact `<summary>`, move session feedback to bottom |
| `app/routers/sessions.py` | **Modify** — add `active_exercise_id` logic to `session_detail`, add `?active=` to `update_exercise_card` redirect |
| `app/static/css/app.css` | **Modify** — add `.exercise-card__compact`, `.exercise-card__recap`, `<details>` marker removal |

### No change needed

| File | Why |
|------|-----|
| `app/models/session.py` | No data model change |
| `app/services/*` | All services unchanged |
| `app/routers/sessions.py` (POST logic) | Save logic unchanged, only redirect URL changes |

### Tests to update

| Test | Change |
|------|--------|
| `tests/test_session_flow.py` | Assertions on HTML structure may need updating (`<details>` vs `<div>`) |
| `tests/test_mobile_polish.py` | Jump bar and redirect tests may need `?active=` in expected URLs |
| `tests/test_past_session_readability.py` | Summary display assertions may change |

---

## 9. Acceptance Criteria — Spec

- [x] Active exercise mechanism defined (query param + server default)
- [x] Compact view content defined (code + name + progress + resume)
- [x] Session feedback repositioned (bottom)
- [x] Zero JS confirmed (`<details open>` server-side)
- [x] Files impacted listed
- [x] Backward compatibility preserved (manual open still works)

## 10. Acceptance Criteria — Build (Sb_02)

- [ ] Only one exercise card is open by default on page load
- [ ] After saving an exercise, the next exercise auto-opens
- [ ] Compact view shows code, name, progress, and set resume (if sets done)
- [ ] Session feedback form appears after the last exercise card
- [ ] "Terminer" button is at the bottom of the page
- [ ] Jump bar still works (anchors point to correct elements)
- [ ] User can manually open any collapsed exercise
- [ ] All exercises open if `?active=` param is missing and all are done
- [ ] Mobile viewport: one exercise card fills most of the screen (no wall of forms)
- [ ] All existing tests pass

---

## 11. Risks

| Risk | Mitigation |
|------|------------|
| `<details>` auto-scroll behavior varies by browser | The `#exercise-{id}` anchor handles scroll. Tested on Chrome/Safari mobile. |
| Tests check for elements that are now inside `<details>` | `<details>` content is in the DOM regardless of open state. Most test assertions (status code, text content) still work. |
| Session feedback at bottom means more scroll to terminate | Jump bar "FB" item scrolls directly there. And it's the natural end of the flow. |
| User opens multiple `<details>` and page gets long | Acceptable — it's their choice. The default experience is focused. |

---

## 12. DO NOT BUILD

- JS-based accordion (auto-close other `<details>` on open) — not needed, native behavior is fine
- Per-exercise route/page (Option C) — over-engineered for this use case
- Inline set editing (Option B) — different paradigm, not this sprint
- Swipe navigation between exercises — requires significant JS
