# Dual-Mode UI Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite the entire UI to a dual-mode system — desktop cockpit (multi-signal, analytical) and mobile narration (sequential, decision-oriented) — across 1 CSS file, 1 base template, and 17 page templates.

**Architecture:** Complete CSS rewrite from scratch using Inter + JetBrains Mono, 8px spacing system, 7 atomic components. Templates restructured with semantic HTML and dual-mode layout via a single 768px breakpoint. No backend changes — presentation only.

**Tech Stack:** CSS3, Jinja2, Google Fonts (Inter, JetBrains Mono)

**Validation:** After each task, run `pytest --tb=short -q` — all existing tests must pass (pages still render 200/303). Visual verification via `uvicorn app.main:app --port 8001`.

---

## File Structure

| Action | File | Responsibility |
|--------|------|----------------|
| Rewrite | `app/static/css/app.css` | Complete design system + all component styles |
| Modify | `app/templates/base.html` | Font imports, topbar, container, footer |
| Modify | `app/templates/_macros.html` | Field + segmented macros updated |
| Modify | `app/templates/index.html` | Cockpit/narration board |
| Modify | `app/templates/profile.html` | Personal state with desktop grid |
| Modify | `app/templates/leaderboard.html` | Strict ranking |
| Modify | `app/templates/progress.html` | Analytical cockpit |
| Modify | `app/templates/session_detail.html` | Strict session logging |
| Modify | `app/templates/history.html` | Clean session list |
| Modify | `app/templates/exercise_history.html` | Exercise progression |
| Modify | `app/templates/library.html` | Template catalog |
| Modify | `app/templates/template_detail.html` | Template exercises |
| Modify | `app/templates/rules.html` | Method rules |
| Modify | `app/templates/welcome.html` | Public landing |
| Modify | `app/templates/login.html` | Auth form |
| Modify | `app/templates/register.html` | Auth form |
| Modify | `app/templates/password_change.html` | Auth form |
| Modify | `app/templates/admin_sessions.html` | Admin management |
| Modify | `app/templates/export.html` | Export/backup |

---

### Task 1: CSS Design System — Complete Rewrite

**Files:**
- Rewrite: `app/static/css/app.css`

This is the foundation. The ENTIRE CSS file is replaced. Every subsequent task depends on these classes existing.

- [ ] **Step 1: Rewrite app.css with the complete design system**

Replace the entire content of `app/static/css/app.css` with the new design system. The file must contain ALL styles needed by ALL templates. Structure it in this exact order:

1. **CSS Variables** (`:root` block with all design tokens from the spec)
2. **Reset + Base** (`*`, `html, body`, `a`, `input`, `button`, `textarea`, `select`)
3. **Typography** (`.page-title`, `.section-header`, `.text-muted`, `.text-dim`, `.text-mono`, `.lede`)
4. **Layout** (`.container`, `.cockpit-grid`, `.cockpit-main`, `.cockpit-side`, `.auth-container`)
5. **Topbar** (`.topbar`, `__brand`, `__nav`, `__link`)
6. **Active Banner** (`.active-banner`, `__dot`, `__label`, `__name`, `__cta`)
7. **Card** (`.card`, `.card--flush`, `.card__title`, `.card__actions`)
8. **KPI** (`.kpi-row`, `.kpi`, `.kpi__value`, `.kpi__label`, `.kpi--accent`)
9. **Insight** (`.insight`, `.insight__reco`)
10. **Sparkline/Chart** (`.sparkline-wrap`, `.timeline-chart`)
11. **Badge** (`.badge`, `--completed`, `--in-progress`, `--neutral`, `--excluded`, `--delta`)
12. **Grade Badge** (`.grade-badge`, `--a`, `--b`, `--c`)
13. **Tooltip** (`.tooltip`, `__trigger`, `__content`)
14. **Button** (`.btn`, `--primary`, `--ghost`, `--danger`, `--sm`, `--wide`, `--end`)
15. **Form Fields** (`.field`, `__label`, `__input`; `.field-row`; `.segmented`, `__option`)
16. **Tiles** (`.tile-grid`, `.tile`, `--primary`, `--resume`, `__label`, `__hint`)
17. **Lists — generic** (`.item-list`, `.item-row`, `__head`, `__name`, `__date`, `__meta`, `--active`)
18. **Stats List** (`.stats-list`, `li` styling for key-value pairs)
19. **Template Cards** (`.template-card`, `--cardio`, `__link`, `__row`, `__name`, `__kind`, `__focus`, `__hint`)
20. **Exercise List** (`.exercise`, `__head`, `__code`, `__name`, `__scheme`, `__notes`, `.sets`, `__item`)
21. **Session Detail** (`.session-page`, `.session-header`, `.ex-jump`, `.exercise-card`, `.set-list`, `.set-row`, `.done-summary`, `.last-time`, `.delta`, `.method-reminder`)
22. **Leaderboard** (`.lb-row`, `--self`, `__rank`, `__name`, `__points`, `__meta`)
23. **KPI Grid — progress page** (`.kpi-grid`, `.kpi-card`, `__value`, `__label`, `__sub`)
24. **Template KPI / Activity** (`.template-kpi-list`, `.template-kpi`, `.activity-list`, `.activity-row`)
25. **Filter Bar** (`.filter-bar`, `__item`, `.is-active`)
26. **History Row** (`.history-row`, `__link`, `__head`, `__date`, `__values`, `__meta`)
27. **Admin** (`.admin-list`, `.admin-row`, `--excluded`, `__link`, `__head`, `__meta`, `__actions`)
28. **Export** (`.export-card`, `.export-stats`, `.integrity-ok`, `.integrity-fail`, `.integrity-errors`)
29. **Body Profile Form** (`.body-profile`, `__field`)
30. **Trend Indicator** (`.trend-indicator`, `--up`, `--down`, `--stable`)
31. **Utility** (`.empty`, `.back`, `.hint`, `.kpi-note`, `.cardio`)
32. **Footer** (`.foot`)
33. **Desktop Breakpoint** (`@media (min-width: 768px)` — all desktop overrides in one block)

Key design tokens:

```css
:root {
  --bg: #0f1115;
  --surface: #161a22;
  --surface-2: #1e222c;
  --border: #232834;
  --fg: #e8ecf1;
  --fg-muted: #9aa3ad;
  --fg-dim: #5a6270;
  --accent: #f25f3a;
  --accent-soft: #f25f3a1a;
  --ok: #2ecc71;
  --ok-soft: #2ecc711a;
  --warn: #f4a261;
  --danger: #e74c3c;
  --info: #3b82f6;
  --font: 'Inter', system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', 'SF Mono', monospace;
  --radius: 8px;
  --radius-sm: 4px;
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-2xl: 48px;
}
```

Key principles for every component:
- Font: `var(--font)` base, `var(--font-mono)` for data values
- Card: `background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: var(--space-md);`
- KPI value: `font-family: var(--font-mono); font-size: 24px; font-weight: 700;`
- KPI label: `font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--fg-muted);`
- Section header: `font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: var(--fg-muted);`
- Buttons: `border-radius: var(--radius-sm);` not `--radius`
- Inputs: `background: var(--surface-2); border: 1px solid transparent; border-radius: var(--radius-sm);` focus: `border-color: var(--accent);`
- Badge: `font-family: var(--font-mono); font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: var(--radius-sm);`
- Insight block: `border-left: 3px solid var(--accent); padding-left: var(--space-md);`
- Container: `max-width: 640px;` mobile, `max-width: 960px;` desktop
- Topbar: opaque `var(--bg)` background (no blur), `border-bottom: 1px solid var(--border);`
- Touch targets: minimum 44px height for interactive elements
- Transitions: `transition: opacity 0.15s, border-color 0.15s;` where needed
- Desktop grid at ≥768px: `.cockpit-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-lg); }`

The desktop breakpoint block must contain overrides for:
- `.container` max-width 960px
- `.cockpit-grid` enabled (display: grid)
- `.tile-grid` 3 columns
- `.template-list` 2 columns
- `.kpi-grid` 2x2 grid
- Topbar nav gap increase

- [ ] **Step 2: Verify syntax**

Run: `python -c "open('app/static/css/app.css').read()" && echo "OK"`
Expected: OK

- [ ] **Step 3: Run tests to verify nothing is broken**

Run: `pytest --tb=short -q`
Expected: All existing tests PASS (CSS changes don't affect route tests)

- [ ] **Step 4: Commit**

```bash
git add app/static/css/app.css
git commit -m "style: rewrite CSS design system — Inter, JetBrains Mono, 8px grid, dual-mode"
```

---

### Task 2: Base template + macros

**Files:**
- Modify: `app/templates/base.html`
- Modify: `app/templates/_macros.html`

- [ ] **Step 1: Update base.html**

Replace `app/templates/base.html` entirely:

```html
<!doctype html>
<html lang="fr">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <meta name="theme-color" content="#0f1115" />
    <meta name="mobile-web-app-capable" content="yes" />
    <meta name="apple-mobile-web-app-capable" content="yes" />
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
    <link rel="manifest" href="{{ url_for('static', path='manifest.webmanifest') }}" />
    <link rel="icon" href="{{ url_for('static', path='icons/favicon.svg') }}" type="image/svg+xml" />
    <link rel="stylesheet" href="{{ url_for('static', path='css/app.css') }}" />
    <title>{{ page_title }} · SPIGNOS</title>
  </head>
  <body>
    <header class="topbar">
      <a class="topbar__brand" href="{{ url_for('home') }}">SPIGNOS</a>
      <nav class="topbar__nav" aria-label="Navigation">
        <a class="topbar__link" href="{{ url_for('home') }}">Accueil</a>
        <a class="topbar__link" href="{{ url_for('library') }}">Programme</a>
        <a class="topbar__link" href="{{ url_for('history') }}">Historique</a>
        <a class="topbar__link" href="{{ url_for('leaderboard_page') }}">Board</a>
        <a class="topbar__link" href="{{ url_for('profile_page') }}">Profil</a>
        <form method="post" action="{{ url_for('logout') }}" style="display:inline;">
          <button type="submit" class="topbar__link topbar__link--btn">Logout</button>
        </form>
      </nav>
    </header>
    {% if active_session %}
      <a class="active-banner" href="{{ url_for('session_detail', session_id=active_session.id) }}">
        <span class="active-banner__dot" aria-hidden="true"></span>
        <span class="active-banner__label">Séance en cours</span>
        <span class="active-banner__name">{{ active_session.template_name_snapshot }}</span>
        <span class="active-banner__cta">Reprendre →</span>
      </a>
    {% endif %}
    <main class="container">
      {% block content %}{% endblock %}
    </main>
    <footer class="foot">
      <small>SPIGNOS · FastAPI SSR · v1</small>
    </footer>
  </body>
</html>
```

Key changes from current:
- Added Google Fonts preconnect + stylesheet links (Inter + JetBrains Mono)
- Brand: "SPIGNOS" (not "Workout")
- Removed "Règles" from nav (secondary, accessible from session page)
- Title suffix: "SPIGNOS" (not "Workout")
- Footer: monospace-styled "SPIGNOS · FastAPI SSR · v1"
- Topbar logout button: added `topbar__link--btn` class for reset styling

- [ ] **Step 2: Update _macros.html**

Replace `app/templates/_macros.html` entirely:

```html
{# Reusable form macros for the design system. #}

{% macro segmented(name, options, selected) %}
<div class="segmented">
  {% for opt in options %}
    {% set val = opt[0] if opt is iterable and opt is not string else opt %}
    {% set label = opt[1] if opt is iterable and opt is not string else opt %}
    <label class="segmented__option">
      <input type="radio" name="{{ name }}" value="{{ val }}"
        {% if val|string == selected|string %}checked{% endif %}>
      <span>{{ label }}</span>
    </label>
  {% endfor %}
</div>
{% endmacro %}

{% macro field_group(label, for_id=None) %}
<label class="field"{% if for_id %} for="{{ for_id }}"{% endif %}>
  <span class="field__label">{{ label }}</span>
  {{ caller() }}
</label>
{% endmacro %}
```

- [ ] **Step 3: Run tests**

Run: `pytest --tb=short -q`
Expected: All PASS

- [ ] **Step 4: Commit**

```bash
git add app/templates/base.html app/templates/_macros.html
git commit -m "style: update base layout — Inter/JetBrains Mono, SPIGNOS brand, clean nav"
```

---

### Task 3: Board page (index.html) — cockpit/narration

**Files:**
- Modify: `app/templates/index.html`

- [ ] **Step 1: Rewrite index.html**

Replace `app/templates/index.html` entirely. The page must implement:

**Mobile (narration):** Vertical flow — insight → KPIs → sparkline → link → resume tile → action tiles

**Desktop (cockpit at ≥768px):** `.cockpit-grid` with left column (insight + KPIs + sparkline) and right column (action tiles). Resume tile full-width above.

Structure:
```html
{% extends "base.html" %}
{% block content %}
<h1 class="page-title">Accueil</h1>

{% if open_session %}
  <a class="tile tile--resume" href="{{ url_for('session_detail', session_id=open_session.id) }}">
    <div class="tile__label">Reprendre · en cours</div>
    <div class="tile__hint">
      {{ open_session.template_name_snapshot }} ·
      démarrée le {{ open_session.started_at.strftime('%d/%m %H:%M') }}
      {% if open_since %}· depuis {{ open_since }}{% endif %}
    </div>
  </a>
{% endif %}

<div class="cockpit-grid">
  <div class="cockpit-main">
    <div class="insight">
      <div class="kpi kpi--accent">
        <span class="kpi__value">{{ "%.0f"|format(behavioral.readiness_score) }}</span>
        <span class="kpi__label">disponibilité</span>
      </div>
      <p class="insight__reco">{{ behavioral.recommendation }}</p>
    </div>

    <div class="card">
      <div class="kpi-row">
        <div class="kpi">
          <span class="kpi__value">{{ kpis.sessions_this_week }}</span>
          <span class="kpi__label">cette sem.</span>
        </div>
        <div class="kpi">
          <span class="kpi__value">{{ "%.0f"|format(kpis.avg_success_score_30d) if kpis.avg_success_score_30d is not none else "—" }}</span>
          <span class="kpi__label">score moy.</span>
        </div>
        <div class="kpi">
          <span class="kpi__value">{% if kpis.completion_rate_30d is not none %}{{ "%.0f"|format(kpis.completion_rate_30d * 100) }}%{% else %}—{% endif %}</span>
          <span class="kpi__label">complétion 30j</span>
        </div>
      </div>
      {% if sparkline_svg %}
        <div class="sparkline-wrap">{{ sparkline_svg|safe }}</div>
      {% else %}
        <p class="text-dim" style="font-size:13px;margin:var(--space-sm) 0;">Pas encore de données</p>
      {% endif %}
      <a class="text-muted" href="{{ url_for('progress') }}" style="display:block;text-align:right;font-size:13px;margin-top:var(--space-sm);">Voir analyse complète →</a>
    </div>
  </div>

  <div class="cockpit-side">
    <div class="tile-grid">
      <a class="tile tile--primary" href="{{ url_for('library') }}">
        <div class="tile__label">Nouvelle séance</div>
        <div class="tile__hint">Choisir un programme et démarrer</div>
      </a>
      <a class="tile" href="{{ url_for('history') }}">
        <div class="tile__label">Historique</div>
        <div class="tile__hint">Sessions passées</div>
      </a>
      <a class="tile" href="{{ url_for('progress') }}">
        <div class="tile__label">Progression</div>
        <div class="tile__hint">KPI et tendances</div>
      </a>
      <a class="tile" href="{{ url_for('library') }}">
        <div class="tile__label">Programmes</div>
        <div class="tile__hint">Tous les programmes</div>
      </a>
      <a class="tile" href="{{ url_for('rules_page') }}">
        <div class="tile__label">Règles</div>
        <div class="tile__hint">Rappels techniques</div>
      </a>
      <a class="tile" href="{{ url_for('admin_sessions') }}">
        <div class="tile__label">Gestion</div>
        <div class="tile__hint">Gérer les séances</div>
      </a>
    </div>
  </div>
</div>
{% endblock %}
```

Desktop: `.cockpit-grid` becomes 2 columns (60/40). `.cockpit-main` gets the analytical content, `.cockpit-side` gets the action tiles.

Mobile: `.cockpit-grid` is single column, `.cockpit-main` before `.cockpit-side`.

- [ ] **Step 2: Run tests**

Run: `pytest tests/test_board_kpis.py tests/test_board_behavioral.py tests/test_session_flow.py::test_home_offers_resume_when_an_open_session_exists -v`
Expected: All PASS

- [ ] **Step 3: Commit**

```bash
git add app/templates/index.html
git commit -m "style: rewrite Board page — cockpit/narration dual layout with insight block"
```

---

### Task 4: Profile page

**Files:**
- Modify: `app/templates/profile.html`

- [ ] **Step 1: Rewrite profile.html**

Desktop: 2-column grid. Left = identity + 30 days. Right = physical profile. Mobile: stacked.

Key structural changes:
- Identity stats in `.card` with `.stats-list` (unified pattern)
- 30 days section: 2 rows of `.kpi-row` (sessions/trend + fatigue/consistency/streak) + chart
- Physical profile: `.card` with `.body-profile` form
- Wrap left + right in `.cockpit-grid`

Template variables available: `user`, `session_count`, `completed_count`, `quality_svg`, `sessions_30d_count`, `trend`, `trend_label`, `behavioral`, `active_session`

- [ ] **Step 2: Run tests**

Run: `pytest tests/test_profile_enrich.py tests/test_profile_behavioral.py tests/test_register_profile.py -v`
Expected: All PASS

- [ ] **Step 3: Commit**

```bash
git add app/templates/profile.html
git commit -m "style: rewrite Profile page — personal state cockpit with body profile"
```

---

### Task 5: Leaderboard page

**Files:**
- Modify: `app/templates/leaderboard.html`

- [ ] **Step 1: Rewrite leaderboard.html**

Single column (both modes). Clean ranking rows in a `.card--flush`. Grade badges with tooltips. Self-row with accent left border.

Template variables: `entries`, `current_username`, `active_session`

- [ ] **Step 2: Run tests**

Run: `pytest tests/test_leaderboard.py tests/test_leaderboard_ui.py -v`
Expected: All PASS

- [ ] **Step 3: Commit**

```bash
git add app/templates/leaderboard.html
git commit -m "style: rewrite Leaderboard — strict ranking with grade badges"
```

---

### Task 6: Progress page

**Files:**
- Modify: `app/templates/progress.html`

- [ ] **Step 1: Rewrite progress.html**

Desktop: KPI grid 2x2 top, then 2-column (template KPIs left + activity right), charts full width. Mobile: sequential.

Template variables: `kpis`, `template_kpis`, `recent_activity`, `quality_svg`, `bodyweight_svg`, `active_session`

- [ ] **Step 2: Run tests**

Run: `pytest tests/test_kpis.py -v`
Expected: All PASS

- [ ] **Step 3: Commit**

```bash
git add app/templates/progress.html
git commit -m "style: rewrite Progress page — analytical cockpit with KPI grid"
```

---

### Task 7: Session detail page (most complex — 331 lines)

**Files:**
- Modify: `app/templates/session_detail.html`

- [ ] **Step 1: Rewrite session_detail.html**

Always single column (input page, not analytical). Apply strict card styling, unified badges, aligned inputs, compact jump-nav. Keep all existing functionality — every form field, every segmented control, every exercise card.

Key changes:
- `.card` with `--border` for exercise cards
- `.badge` variants unified
- Input fields use `.field` pattern
- Set rows aligned to 8px grid
- Jump nav: horizontal scroll, compact
- Method reminder: collapsible via `<details>`

This is the largest template. Preserve ALL template variables and form actions. Every `name=` attribute must remain identical.

Template variables: `session`, `exercises_with_sets`, `method_rules`, `exercise_stats`, `active_session`, plus form POST actions.

- [ ] **Step 2: Run tests**

Run: `pytest tests/test_session_flow.py -v`
Expected: All PASS (all form submissions, redirects, and data persistence still work)

- [ ] **Step 3: Commit**

```bash
git add app/templates/session_detail.html
git commit -m "style: rewrite Session Detail — strict cards, unified badges, 8px grid"
```

---

### Task 8: History + Exercise History

**Files:**
- Modify: `app/templates/history.html`
- Modify: `app/templates/exercise_history.html`

- [ ] **Step 1: Rewrite history.html**

Filter bar with `.segmented`-style pills. Session rows as clean list items with badges.

Template variables: `sessions`, `session_stats`, `durations`, `status_filter`, `status_choices`, `active_session`

- [ ] **Step 2: Rewrite exercise_history.html**

Back nav, header, history rows with delta badges.

Template variables: `exercise_code`, `exercise_name`, `template_slug`, `template_name`, `history_entries`, `active_session`

- [ ] **Step 3: Run tests**

Run: `pytest tests/test_session_flow.py::test_history_lists_created_sessions tests/test_exercise_history.py -v`
Expected: All PASS

- [ ] **Step 4: Commit**

```bash
git add app/templates/history.html app/templates/exercise_history.html
git commit -m "style: rewrite History and Exercise History — clean lists with unified badges"
```

---

### Task 9: Library + Template Detail + Rules

**Files:**
- Modify: `app/templates/library.html`
- Modify: `app/templates/template_detail.html`
- Modify: `app/templates/rules.html`

- [ ] **Step 1: Rewrite library.html**

Template cards strict. Left border accent (strength) or info (cardio).

Template variables: `templates`, `active_session`

- [ ] **Step 2: Rewrite template_detail.html**

Exercise list with code badges, set scheme, rep targets.

Template variables: `template`, `active_session`

- [ ] **Step 3: Rewrite rules.html**

Rule cards strict, body text 14px.

Template variables: `rules`, `active_session`

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_library.py tests/test_session_flow.py::test_rules_page_renders_seeded_rules -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add app/templates/library.html app/templates/template_detail.html app/templates/rules.html
git commit -m "style: rewrite Library, Template Detail, Rules — strict catalog cards"
```

---

### Task 10: Auth pages (welcome, login, register, password_change)

**Files:**
- Modify: `app/templates/welcome.html`
- Modify: `app/templates/login.html`
- Modify: `app/templates/register.html`
- Modify: `app/templates/password_change.html`

- [ ] **Step 1: Rewrite all 4 auth templates**

All centered in `.auth-container` (max-width 400px). Single `.card`. Unified button style. Error display via `.integrity-errors`.

Welcome: brand statement + login/register buttons.
Login: username + password fields, submit, links.
Register: username + password + confirm, submit, links.
Password change: current + new + confirm, submit, back link.

Template variables:
- welcome: none
- login: `error`, `success`
- register: `error`
- password_change: `error`, `success`

- [ ] **Step 2: Run tests**

Run: `pytest tests/test_auth.py tests/test_register_profile.py -v`
Expected: All PASS

- [ ] **Step 3: Commit**

```bash
git add app/templates/welcome.html app/templates/login.html app/templates/register.html app/templates/password_change.html
git commit -m "style: rewrite Auth pages — centered cards, strict forms"
```

---

### Task 11: Admin + Export pages

**Files:**
- Modify: `app/templates/admin_sessions.html`
- Modify: `app/templates/export.html`

- [ ] **Step 1: Rewrite admin_sessions.html**

Admin rows in `.card--flush` list. Danger buttons clear. Exclude toggle.

Template variables: `sessions`, `active_session`

- [ ] **Step 2: Rewrite export.html**

3 cards: journal stats, download actions, backup status. Stats list unified.

Template variables: `total_sessions`, `completed_sessions`, `work_sets_done`, `first_session_date`, `last_session_date`, `json_url`, `csv_url`, `backup_*`, `integrity_*`, `active_session`

- [ ] **Step 3: Run tests**

Run: `pytest tests/test_session_management.py tests/test_export.py -v`
Expected: All PASS

- [ ] **Step 4: Commit**

```bash
git add app/templates/admin_sessions.html app/templates/export.html
git commit -m "style: rewrite Admin and Export pages — strict lists, clear actions"
```

---

### Task 12: Final integration verification

- [ ] **Step 1: Run full test suite**

Run: `pytest -v`
Expected: All tests PASS (only pre-existing failures from missing .vscode files)

- [ ] **Step 2: Visual smoke test**

Run: `python -m uvicorn app.main:app --port 8001`

Verify manually:
- `/` shows cockpit layout on desktop (2 columns), narration on mobile (vertical)
- `/profile` shows 2-column grid on desktop
- `/leaderboard` shows clean ranking with grade badges
- `/progress` shows analytical grid on desktop
- `/sessions/{id}` shows strict cards with aligned inputs
- `/welcome`, `/login`, `/register` show centered auth cards
- All forms submit correctly
- Font rendering: Inter for text, JetBrains Mono for values

- [ ] **Step 3: Commit if fixes needed**

```bash
git add -A
git commit -m "fix: UI integration adjustments after visual review"
```
