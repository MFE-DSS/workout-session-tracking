# SPIGNOS Dual-Mode UI Refactor — Design Spec

**Date:** 2026-04-12
**Scope:** Full CSS rewrite + 18 template refactor. Desktop cockpit / Mobile narration.

## Philosophy

Engineered, structured, calm, precise. Inspired by Palantir Foundry, Linear, industrial dashboards. No sci-fi, no retro, no decoration. A professional internal tool, not a consumer fitness app.

## Decisions

- Full refactor of all 18 templates (Option C)
- Design system rewrite from scratch (not patching existing CSS)
- Desktop cockpit (multi-column, analytical) at ≥768px
- Mobile narration (vertical flow, sequential) below 768px
- Inter + JetBrains Mono fonts via external CDN link
- 8px spacing system throughout

## Constraints

- No route changes, no backend logic changes
- CSS-only interactions (no JS)
- Presentation-only refactor
- All existing functionality preserved

---

## 1. Design System

### CSS Variables

```css
:root {
  /* Surfaces */
  --bg:         #0f1115;
  --surface:    #161a22;
  --surface-2:  #1e222c;
  --border:     #232834;

  /* Text */
  --fg:         #e8ecf1;
  --fg-muted:   #9aa3ad;
  --fg-dim:     #5a6270;

  /* Accents */
  --accent:     #f25f3a;
  --accent-soft: #f25f3a22;
  --ok:         #2ecc71;
  --warn:       #f4a261;
  --danger:     #e74c3c;

  /* Typography */
  --font:       'Inter', system-ui, sans-serif;
  --font-mono:  'JetBrains Mono', monospace;

  /* Spacing (8px system) */
  --space-xs:   4px;
  --space-sm:   8px;
  --space-md:   16px;
  --space-lg:   24px;
  --space-xl:   32px;
  --space-2xl:  48px;

  /* Radii */
  --radius:     8px;
  --radius-sm:  4px;
}
```

### Typography Scale

| Element | Font | Size | Weight | Color |
|---------|------|------|--------|-------|
| Page title | Inter | 18px | 600 | `--fg` |
| Section header | Inter | 13px | 600 | `--fg-muted` |
| Body text | Inter | 14px | 400 | `--fg` |
| KPI value | JetBrains Mono | 24px | 700 | `--fg` |
| KPI label | Inter | 11px | 400 | `--fg-muted` |
| Badge text | JetBrains Mono | 11px | 600 | varies |
| Input text | Inter | 14px | 400 | `--fg` |
| Small/hint | Inter | 12px | 400 | `--fg-dim` |

Section headers: uppercase, letter-spacing 0.5px.

### Layout

- Mobile (<768px): `max-width: 640px`, single column, padding `--space-md`
- Desktop (≥768px): `max-width: 960px`, grid layouts for cockpit pages
- Breakpoint: 768px separates narration (mobile) from cockpit (desktop)
- Container centered with `margin: 0 auto`

---

## 2. Atomic Components

### 2.1 `.card`

Strict container. No decoration.

- `background: var(--surface)`
- `border: 1px solid var(--border)`
- `border-radius: var(--radius)`
- `padding: var(--space-md)`
- Variant: `.card--flush` — no padding (for lists that bleed to edges)

### 2.2 `.kpi` + `.kpi-row`

Single metric display.

- `.kpi__value`: JetBrains Mono, 24px, 700
- `.kpi__label`: Inter, 11px, uppercase, `--fg-muted`
- `.kpi--accent`: value colored `--accent` (used only for readiness)
- `.kpi-row`: flex container, gap `--space-md`, aligns 3-4 KPIs horizontally

### 2.3 `.badge`

Compact status indicator.

- Inline-flex, padding 2px 8px, `--radius-sm`, JetBrains Mono 11px
- Variants: `--completed` (ok bg), `--in-progress` (accent), `--neutral` (border), `--excluded` (dim)
- `.grade-badge`: round 22px circle, centered. A=ok, B=accent, C=fg-muted bg

### 2.4 `.btn`

Action trigger.

- Base: `--surface-2` bg, border, padding 8px 16px, `--radius-sm`, 14px, weight 500
- `.btn--primary`: accent bg, dark text
- `.btn--ghost`: transparent, border only
- `.btn--danger`: danger bg
- `.btn--sm`: smaller padding 4px 10px, 12px font
- `.btn--wide`: full width

### 2.5 `.field`

Form input.

- Label: 12px, `--fg-muted`, above input
- Input: `--surface-2` bg, border transparent, `--radius-sm`, padding 8px 12px
- Focus: border-color `--accent`
- `.segmented`: horizontal radio group, badge-like visual

### 2.6 `.tooltip`

Info on hover/focus.

- `.tooltip__trigger`: position relative, tabindex=0, cursor pointer
- `.tooltip__content`: absolute, `--surface-2` bg, border, opacity 0 → 1
- Shown via `:hover` and `:focus-within`
- Mobile: degrades to always-visible inline text OR focus-tap

### 2.7 `.section-header`

Section divider.

- 13px, 600, uppercase, letter-spacing 0.5px, `--fg-muted`
- Optional: `border-bottom: 1px solid var(--border)`, padding-bottom `--space-sm`

### 2.8 `.insight`

Behavioral block — PRIMARY output element.

- `border-left: 3px solid var(--accent)`
- `padding-left: var(--space-md)`
- Recommendation text: 13px, `--fg-muted`, line-height 1.5
- Only element with accent border in the entire UI

---

## 3. Template Structure

### 3.1 base.html

**Topbar:** Opaque `--bg` background (no blur/backdrop-filter). Brand 600 weight. Nav links 13px, gap 16px. Border-bottom `--border`. Sticky.

**Container:** `max-width: 640px` → `max-width: 960px` at 768px breakpoint.

**Active banner:** Simplified. Dot indicator + text + arrow. Surface bg.

**Footer:** JetBrains Mono 11px, `--fg-dim`.

### 3.2 index.html (Board)

**Mobile (narration — vertical flow):**
1. Page title ("Accueil")
2. `.insight` block — readiness score + recommendation sentence
3. `.kpi-row` — 4 KPIs (séances, score moy, complétion, disponibilité)
4. Sparkline in `.card`
5. Link "Voir analyse complète →"
6. Resume tile (if active session)
7. Action tiles (6 tiles in 2-col grid)

**Desktop (cockpit — ≥768px):**
- 2 column grid: 60% / 40%
- Left: insight + KPIs + sparkline + link
- Right: action tiles stacked
- Resume tile: full width above grid

### 3.3 profile.html

**Mobile:**
1. Identity card (username, joined, status, session counts)
2. "30 derniers jours" card (séances + tendance row, fatigue + régularité + streak row, quality chart)
3. Physical profile card (form)
4. Password change button

**Desktop (≥768px):**
- 2 column grid: 55% / 45%
- Left: identity + 30 jours
- Right: physical profile
- Password button below grid

### 3.4 leaderboard.html

Single column (both modes). Card with list rows. Rank + name + grade badge/tooltip + points + meta. Self-row: left border accent.

### 3.5 progress.html

**Mobile:** Sequential — KPI grid (2x2) → template KPIs → activity list → charts

**Desktop (≥768px):** KPI grid 2x2 top, then 2-column: template list left + activity list right, charts full width below.

### 3.6 session_detail.html

Always single column (data entry page, not analytical). Cards stricter. Inputs aligned to 8px grid. Badges unified. Jump-nav compact horizontal scroll. Exercise cards as `.card` with internal sections.

### 3.7 history.html

Single column. Filter bar: `.segmented`-style toggle. Session rows: card-like with badges.

### 3.8 exercise_history.html

Single column. Back nav + header + history rows with delta badges.

### 3.9 library.html + template_detail.html

Single column. Template cards strict. Exercise lists clean.

### 3.10 rules.html

Single column. Rule cards strict, body text 14px.

### 3.11 Auth pages (welcome, login, register, password_change)

Centered, `max-width: 400px`. Single `.card`. Unified button style.

### 3.12 admin_sessions.html

Single column. Admin rows in card--flush. Danger buttons clear.

### 3.13 export.html

Single column. 3 cards (journal, download, backup). Stats list unified with `export-stats` pattern.

---

## 4. Desktop vs Mobile Behavior

| Page | Mobile | Desktop |
|------|--------|---------|
| index | Vertical narration flow | 2-col cockpit grid |
| profile | Stacked cards | 2-col layout |
| progress | Sequential sections | 2-col analytical grid |
| session_detail | Single column | Single column (unchanged) |
| All others | Single column | Single column (unchanged) |

Breakpoint: `@media (min-width: 768px)` switches layout. All content is identical — only arrangement changes.

---

## 5. Interaction Rules

- CSS-only transitions: `opacity 0.15s`, `transform 0.15s`
- Focus states: `outline: 2px solid var(--accent)`, offset 2px
- Tooltips: `:hover` + `:focus-within` (accessible)
- No hover-only interactions — all info visible by default
- Touch targets minimum 44px
- No animations that distract

---

## 6. Font Loading

Add to `base.html` `<head>`:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
```

Fallback: `system-ui, sans-serif` for Inter, `monospace` for JetBrains Mono.

---

## 7. Files Summary

| Action | File |
|--------|------|
| Rewrite | `app/static/css/app.css` — complete design system from scratch |
| Modify | `app/templates/base.html` — font imports + topbar + container + footer |
| Modify | `app/templates/_macros.html` — updated classes for field/segmented |
| Modify | `app/templates/index.html` — cockpit/narration dual layout |
| Modify | `app/templates/profile.html` — personal state with grid desktop |
| Modify | `app/templates/leaderboard.html` — strict ranking display |
| Modify | `app/templates/progress.html` — analytical cockpit |
| Modify | `app/templates/session_detail.html` — strict cards, unified badges |
| Modify | `app/templates/history.html` — clean list with filter |
| Modify | `app/templates/exercise_history.html` — clean history rows |
| Modify | `app/templates/library.html` — strict template cards |
| Modify | `app/templates/template_detail.html` — clean exercise list |
| Modify | `app/templates/rules.html` — strict rule cards |
| Modify | `app/templates/welcome.html` — centered auth card |
| Modify | `app/templates/login.html` — centered auth card |
| Modify | `app/templates/register.html` — centered auth card |
| Modify | `app/templates/password_change.html` — centered auth card |
| Modify | `app/templates/admin_sessions.html` — admin list strict |
| Modify | `app/templates/export.html` — export cards strict |
