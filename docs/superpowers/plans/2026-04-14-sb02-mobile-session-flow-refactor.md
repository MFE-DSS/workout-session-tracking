# Sb_02 — Mobile Session Flow Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the session detail page so only one exercise card is expanded at a time (`<details>` accordion), collapsed cards show a compact summary, and the session feedback form moves to the bottom — creating a focused, linear gym flow on mobile.

**Architecture:** Template refactored to wrap each exercise card in `<details>`. The router passes `active_exercise_id` (from `?active=` param or first non-complete exercise). The redirect after save adds `?active={next_id}`. Session feedback form moved below exercise cards. CSS additions for compact summary styling.

**Tech Stack:** Jinja2 template, FastAPI route (minor), CSS, pytest

---

## File Structure

| File | Responsibility |
|------|---------------|
| `app/templates/session_detail.html` | Refactored template with `<details>` accordion |
| `app/routers/sessions.py` | Add `active_exercise_id` to context, `?active=` to redirect |
| `app/static/css/app.css` | Compact summary styles |
| `tests/test_session_flow.py` | Updated assertions for `<details>` structure |
| `tests/test_mobile_polish.py` | Updated redirect URL expectations |

---

### Task 1: Router — Active Exercise Logic + Redirect

**Files:**
- Modify: `app/routers/sessions.py`

- [ ] **Step 1: Add `active_exercise_id` to session_detail route**

In `app/routers/sessions.py`, modify the `session_detail` function. After computing `stats` and before the template response, add:

```python
    # Determine which exercise card to expand (Sb_02 accordion)
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

Add `"active_exercise_id": active_exercise_id` to the template context dict.

- [ ] **Step 2: Add `?active=` to exercise card redirect**

In `update_exercise_card`, change the redirect target. Find (around line 329-332):

```python
    if next_se is not None:
        target = f"/sessions/{session_id}#exercise-{next_se.id}"
    else:
        target = f"/sessions/{session_id}#session-feedback"
```

Replace with:

```python
    if next_se is not None:
        target = f"/sessions/{session_id}?active={next_se.id}#exercise-{next_se.id}"
    else:
        target = f"/sessions/{session_id}#session-feedback"
```

- [ ] **Step 3: Commit**

```bash
git add app/routers/sessions.py
git commit -m "feat(sb02): active exercise logic + ?active= redirect for accordion"
```

---

### Task 2: Template Refactor — `<details>` Accordion + Feedback Bottom

**Files:**
- Modify: `app/templates/session_detail.html`

- [ ] **Step 1: Move session feedback form to after the exercise loop**

In `session_detail.html`, the session feedback form (lines 47-106, `<form id="session-feedback">`) currently sits BEFORE the exercise cards loop. Move the entire block to AFTER the `{% endfor %}` of the exercise loop (after line 294) and BEFORE the method reminder `{% if rules %}` block.

The new order should be:
1. `session-header`
2. `ex-jump` (jump bar)
3. Exercise cards loop (`{% for se in session.session_exercises %}`)
4. Session feedback form (`<form id="session-feedback">`)
5. Method reminder

- [ ] **Step 2: Wrap each exercise card in `<details>` with compact `<summary>`**

Replace the exercise card form wrapper. The current structure is:

```html
{% for se in session.session_exercises %}
  {% set done, total = stats.per_exercise[se.id] %}
  <form
    method="post"
    action="..."
    class="card exercise-card ..."
    id="exercise-{{ se.id }}"
  >
    <header class="exercise-card__head">...</header>
    {# ... rest of card ... #}
  </form>
{% endfor %}
```

Replace with:

```html
{% for se in session.session_exercises %}
  {% set done, total = stats.per_exercise[se.id] %}
  {% set is_active = (active_exercise_id == se.id) %}
  {% set summary = exercise_summaries.get(se.id) %}

  <details
    class="card exercise-card {% if total > 0 and done == total %}exercise-card--done{% endif %}"
    id="exercise-{{ se.id }}"
    {% if is_active %}open{% endif %}
  >
    <summary class="exercise-card__compact">
      <span class="exercise-card__code">{{ se.exercise_code_snapshot }}</span>
      <span class="exercise-card__name">{{ se.exercise_name_snapshot }}</span>
      <span class="exercise-card__progress">{{ done }}/{{ total }}</span>
      {% if done > 0 and summary %}
        <span class="exercise-card__recap">
          {{ summary.weights_str }} kg · {{ summary.reps_str }} reps
        </span>
      {% endif %}
    </summary>

    <form
      method="post"
      action="{{ url_for('update_exercise_card', session_id=session.id, session_exercise_id=se.id) }}"
      class="exercise-card__form"
    >
      {# Keep everything that was inside the old form: #}
      {# set_scheme, done-summary (completed only), last-time, delta, hint #}
      {# warmup sets, work sets, feedback section, submit button #}

      {% if se.template_exercise and se.template_exercise.set_scheme %}
        <div class="exercise-card__scheme">{{ se.template_exercise.set_scheme }}</div>
      {% endif %}

      {% if session.status == 'completed' and summary %}
        <div class="done-summary">
          <span class="done-summary__count">
            Work : {{ summary.work_done }}/{{ summary.work_total }}
          </span>
          <span class="done-summary__values">
            {{ summary.weights_str }} kg · {{ summary.reps_str }} reps
          </span>
          {% if summary.success_score is not none %}
            <span class="done-summary__score">score {{ summary.success_score }}</span>
          {% endif %}
        </div>
      {% endif %}

      {% set lt = last_time.get(se.exercise_code_snapshot) %}
      <div class="last-time {% if not lt %}last-time--empty{% endif %}">
        {% if lt and lt.has_data %}
          <span class="last-time__label">Dernière fois</span>
          <span class="last-time__when">{{ lt.relative }}</span>
          <span class="last-time__values">
            {{ lt.weights_str }} kg · {{ lt.reps_str }} reps
          </span>
        {% elif lt %}
          <span class="last-time__label">Dernière fois</span>
          <span class="last-time__when">{{ lt.relative }}</span>
          <span class="last-time__values">aucune donnée saisie</span>
        {% else %}
          <span class="last-time__label">Dernière fois</span>
          <span class="last-time__values">Aucune séance précédente</span>
        {% endif %}
      </div>

      {% set delta_label = deltas.get(se.exercise_code_snapshot) %}
      {% if delta_label %}
        <div class="delta">
          <span class="delta__label">Delta</span>
          <span class="delta__text">{{ delta_label }}</span>
        </div>
      {% endif %}

      {% set hint = hints.get(se.exercise_code_snapshot) %}
      {% if hint %}
        <div class="hint">
          <span class="hint__label">Repère</span>
          <span class="hint__text">{{ hint }}</span>
        </div>
      {% endif %}

      {% if se.set_logs|length > 0 %}
        {% set warmup_sets = se.set_logs|selectattr('kind', 'equalto', 'warmup')|list %}
        {% set work_sets = se.set_logs|selectattr('kind', 'equalto', 'work')|list %}

        {% if warmup_sets|length > 0 %}
          <h4 class="set-group-title">Warmup</h4>
        {% endif %}
        <ul class="set-list">
          {% for sl in warmup_sets %}
            <li class="set-row set-row--warmup">
              <div class="set-row__label">
                <span class="set-row__kind">Warmup</span>
                <span class="set-row__idx">#{{ sl.set_index }}</span>
                {% if sl.technique %}<span class="tag">{{ sl.technique }}</span>{% endif %}
              </div>
              <div class="set-row__inputs">
                <input type="number" step="0.5" inputmode="decimal"
                       name="set_{{ sl.id }}_weight_kg" placeholder="kg"
                       value="{{ sl.weight_kg if sl.weight_kg is not none else '' }}" />
                <input type="number" inputmode="numeric"
                       name="set_{{ sl.id }}_reps" placeholder="reps"
                       value="{{ sl.reps if sl.reps is not none else '' }}" />
                <label class="set-row__done">
                  <input type="checkbox" name="set_{{ sl.id }}_completed" value="1"
                         {% if sl.completed %}checked{% endif %} />
                  <span>Fait</span>
                </label>
              </div>
            </li>
          {% endfor %}
        </ul>

        {% if work_sets|length > 0 %}
          <h4 class="set-group-title set-group-title--work">Work</h4>
        {% endif %}
        <ul class="set-list">
          {% for sl in work_sets %}
            <li class="set-row set-row--work">
              <div class="set-row__label">
                <span class="set-row__kind">Work</span>
                <span class="set-row__idx">#{{ sl.set_index }}</span>
                {% if sl.technique %}<span class="tag">{{ sl.technique }}</span>{% endif %}
              </div>
              <div class="set-row__inputs">
                <input type="number" step="0.5" inputmode="decimal"
                       name="set_{{ sl.id }}_weight_kg" placeholder="kg"
                       value="{{ sl.weight_kg if sl.weight_kg is not none else '' }}" />
                <input type="number" inputmode="numeric"
                       name="set_{{ sl.id }}_reps" placeholder="reps"
                       value="{{ sl.reps if sl.reps is not none else '' }}" />
                <label class="set-row__done">
                  <input type="checkbox" name="set_{{ sl.id }}_completed" value="1"
                         {% if sl.completed %}checked{% endif %} />
                  <span>Fait</span>
                </label>
              </div>
            </li>
          {% endfor %}
        </ul>
      {% else %}
        <p class="empty">Pas de série pour cet exercice.</p>
      {% endif %}

      <h3 class="card__subtitle">Feedback exercice</h3>

      <details class="field-block field-block--optional">
        <summary class="field__label" style="cursor:pointer;font-size:13px;color:var(--fg-dim);">
          Sensation musculaire (optionnel)
        </summary>
        {{ segmented(
          "muscle_sensation",
          [("strong", "Strong"), ("partial", "Partial"), ("weak", "Weak")],
          se.muscle_sensation
        ) }}
      </details>

      {% call field_group("Note (optionnel)") %}
        <textarea name="free_note" maxlength="140" rows="1">{{ se.free_note or '' }}</textarea>
      {% endcall %}

      <div class="card__actions">
        <button type="submit" class="btn btn--primary">
          Enregistrer {{ se.exercise_code_snapshot }}
        </button>
      </div>
    </form>
  </details>
{% endfor %}
```

- [ ] **Step 3: Remove the old `<header class="exercise-card__head">` block**

The old header (code link + name + progress) is replaced by the `<summary>` in the `<details>`. Make sure the history link is still accessible — add it inside the expanded form area instead:

After the `exercise-card__scheme` div, add:

```html
      <div class="exercise-card__head-expanded">
        <a class="exercise-card__code exercise-card__code--link"
           href="{{ url_for('exercise_history_detail', template_slug=session.template_slug_snapshot, exercise_code=se.exercise_code_snapshot) }}"
           title="Historique {{ se.exercise_code_snapshot }}">
          Voir historique {{ se.exercise_code_snapshot }} →
        </a>
      </div>
```

- [ ] **Step 4: Verify the page renders**

Run: `pytest tests/test_session_flow.py::test_session_detail_renders_exercise_cards -v`
Expected: May need adjustments (Task 3).

- [ ] **Step 5: Commit**

```bash
git add app/templates/session_detail.html
git commit -m "feat(sb02): refactor session template — <details> accordion, compact summary, feedback bottom"
```

---

### Task 3: CSS — Compact Summary Styles

**Files:**
- Modify: `app/static/css/app.css`

- [ ] **Step 1: Add compact summary styles**

Add to the end of `app/static/css/app.css`:

```css
/* --- Sb_02: Exercise card accordion --- */

details.exercise-card {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  margin-bottom: var(--space-md);
  background: var(--surface);
}

details.exercise-card[open] {
  border-color: var(--accent);
}

.exercise-card__compact {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  cursor: pointer;
  list-style: none;
  font-size: 14px;
}

.exercise-card__compact::-webkit-details-marker {
  display: none;
}

.exercise-card__compact::marker {
  display: none;
  content: "";
}

.exercise-card__recap {
  font-size: 12px;
  color: var(--fg-dim);
  margin-left: auto;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 50%;
}

.exercise-card__form {
  padding: 0 var(--space-md) var(--space-md);
}

.exercise-card__head-expanded {
  margin-bottom: var(--space-sm);
}

.exercise-card__head-expanded a {
  font-size: 12px;
  color: var(--fg-dim);
}

details.exercise-card--done .exercise-card__compact {
  color: var(--fg-muted);
}

details.exercise-card--done .exercise-card__compact .exercise-card__code {
  color: var(--ok);
}
```

- [ ] **Step 2: Commit**

```bash
git add app/static/css/app.css
git commit -m "feat(sb02): CSS for exercise card accordion — compact summary, open state accent"
```

---

### Task 4: Fix Tests + Final Verification

**Files:**
- Modify: `tests/test_session_flow.py`
- Modify: `tests/test_mobile_polish.py`
- Modify: other test files as needed

- [ ] **Step 1: Fix tests that check HTML structure**

Tests that check for `exercise-card` class, form structure, or redirect URLs need updating:

**`tests/test_mobile_polish.py`**: Tests that check redirect URLs after exercise card save. The redirect now includes `?active=`. Find assertions like:
```python
assert r.headers["location"] == f"/sessions/{sid}#exercise-{next_id}"
```
Change to:
```python
assert f"active={next_id}" in r.headers["location"]
assert f"#exercise-{next_id}" in r.headers["location"]
```

**`tests/test_session_flow.py`**: Tests that check page renders. The exercise cards are now inside `<details>` elements. Most text-content assertions still work (content is in the DOM regardless of open state). Fix any that check for specific CSS classes on the form wrapper.

- [ ] **Step 2: Run full test suite**

Run: `pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q`
Expected: All pass.

- [ ] **Step 3: Commit**

```bash
git add tests/
git commit -m "test(sb02): adapt tests for <details> accordion and ?active= redirect"
```

---

### Task 5: Sprint Report

**Files:**
- Create: `docs/SPRINT_Sb02_REPORT.md`

- [ ] **Step 1: Run full test suite**

Run: `pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q`
Expected: All pass.

- [ ] **Step 2: Write sprint report**

Create `docs/SPRINT_Sb02_REPORT.md`:

```markdown
# Sprint Sb_02 Report — Mobile Session Flow Refactor

**Date:** 2026-04-14
**Status:** Complete
**Spec:** docs/strategy/SPIGNOS_MOBILE_EXERCISE_ENTRY_UX.md

## Objective

Refactor session detail page for focused mobile gym flow:
one exercise expanded at a time, compact summaries for collapsed
cards, session feedback at bottom.

## Deliverables

| Artifact | Path | Status |
|----------|------|--------|
| Template refactor | `app/templates/session_detail.html` | Done |
| Router changes | `app/routers/sessions.py` | Done |
| CSS additions | `app/static/css/app.css` | Done |

## Changes

- Exercise cards wrapped in `<details>` with server-side `open` attribute
- Compact `<summary>`: code + name + progress + set resume
- Session feedback form moved to bottom (natural gym flow)
- Redirect after save includes `?active={next_id}` for accordion control
- Default active: first non-complete exercise
- Zero JS — pure HTML `<details>` + server-side logic

## Verification

```bash
pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q
```

## Unblocks

- Sb_03 (exercise substitution) can add the select dropdown inside the `<details>` card
```

- [ ] **Step 3: Commit**

```bash
git add docs/SPRINT_Sb02_REPORT.md
git commit -m "docs(sb02): sprint report — mobile session flow refactor complete"
```
