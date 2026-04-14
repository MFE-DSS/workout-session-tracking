# Visual Identity V2.1 — Presentation-Only Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade SPIGNOS visual identity from "generic web app" to "private body engineering cockpit" — French lexicon, WCAG-compliant tokens, mobile hamburger menu, dashboard anti-pseudo-science display, privacy cues, inline style cleanup.

**Architecture:** CSS-first approach: add new tokens + utility classes + component variants to `app.css`, then systematically update templates for lexicon + markup. Zero backend/route/model changes. Tests updated only for changed label text.

**Tech Stack:** CSS custom properties, Jinja2 templates, pytest (text assertions only)

---

## File Structure

| File | Changes |
|------|---------|
| `app/static/css/app.css` | New tokens (`--fg-dim`, `--accent-muted`), utility classes, card variants, chip classes, topbar mobile menu, `.chip--insufficient` pattern |
| `app/templates/base.html` | Nav labels FR, `<details>` hamburger mobile, footer cleanup |
| `app/templates/welcome.html` | Rebrand SPIGNOS + tagline FR |
| `app/templates/session_detail.html` | Franciser Work→Série, Warmup→Échauf., Strong→Fort, "Ressenti exercice" |
| `app/templates/dashboard.html` | "Synthèse", axes FR, hero confiance co-principal, grade demoted |
| `app/templates/index.html` | "État du jour", inline cleanup |
| `app/templates/physique.html` | Inline cleanup |
| `app/templates/history.html` | Inline cleanup |
| `app/templates/leaderboard.html` | "Classement", privacy chip |
| `app/templates/squad_*.html` | Fix accents, fix hardcoded vars, privacy chips |
| `app/templates/progress.html` | Labels FR |
| `app/templates/readiness_history.html` | "Historique état" |
| `app/templates/export.html` | "Sauvegarde", remove dev text |
| Tests | Adapt text assertions |

---

### Task 1: CSS Tokens + Utility Classes + Component Variants

**Files:**
- Modify: `app/static/css/app.css`

- [ ] **Step 1: Update `--fg-dim` token**

In the `:root` block, change:
```css
--fg-dim: #5a6270;
```
To:
```css
--fg-dim: #6e7785;
```

- [ ] **Step 2: Add `--accent-muted` token**

In the `:root` block, after `--accent-soft`, add:
```css
--accent-muted: #d4715a;
```

- [ ] **Step 3: Add utility classes**

After the existing typography helpers section, add:

```css
/* ---- Spacing Utilities ---- */
.mt-xs { margin-top: var(--space-xs); }
.mt-sm { margin-top: var(--space-sm); }
.mt-md { margin-top: var(--space-md); }
.mt-lg { margin-top: var(--space-lg); }
.mb-xs { margin-bottom: var(--space-xs); }
.mb-sm { margin-bottom: var(--space-sm); }
.mb-md { margin-bottom: var(--space-md); }
.mb-lg { margin-bottom: var(--space-lg); }
.gap-sm { gap: var(--space-sm); }
.gap-md { gap: var(--space-md); }
```

- [ ] **Step 4: Add card variants**

After the existing `.card` rules, add:

```css
.card--signal { border-left: 3px solid var(--accent); }
.card--metric { padding: var(--space-sm) var(--space-md); }
.card--evidence { background: var(--bg); border-color: var(--border); }
```

- [ ] **Step 5: Add chip + privacy components**

After the badge section, add:

```css
/* ---- Chips (confidence, privacy, insufficient) ---- */
.chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}

.chip--confidence-high { color: var(--ok); background: var(--ok-soft); }
.chip--confidence-medium { color: var(--warn); background: rgba(244, 162, 97, 0.1); }
.chip--confidence-low { color: var(--fg-dim); background: var(--surface-2); }
.chip--insufficient {
  color: var(--fg-dim);
  background: transparent;
  border: 1px dashed var(--border);
}
.chip--private {
  color: var(--fg-dim);
  background: var(--surface-2);
}
.chip--private::before { content: "🔒 "; font-size: 10px; }
```

- [ ] **Step 6: Add topbar mobile menu styles**

After the existing `.topbar__link--btn` rules, add:

```css
/* ---- Topbar mobile hamburger ---- */
.topbar__toggle {
  display: none;
  background: none;
  border: none;
  color: var(--fg-muted);
  font-size: 20px;
  cursor: pointer;
  padding: 4px 8px;
  list-style: none;
}

.topbar__toggle::-webkit-details-marker { display: none; }

@media (max-width: 768px) {
  .topbar__nav { display: none; }
  .topbar__toggle { display: block; }
  .topbar__menu[open] .topbar__nav {
    display: flex;
    flex-direction: column;
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: var(--bg);
    border-bottom: 1px solid var(--border);
    padding: var(--space-md);
    gap: var(--space-md);
    z-index: 10;
  }
  .topbar__menu[open] .topbar__nav a,
  .topbar__menu[open] .topbar__nav button {
    font-size: 16px;
    padding: var(--space-sm) 0;
  }
}

@media (min-width: 769px) {
  .topbar__menu > .topbar__nav { display: flex; }
  .topbar__toggle { display: none; }
}
```

- [ ] **Step 7: Add hover/focus accent-muted rule**

After the `.btn:hover` rules, add:

```css
.btn--primary:hover { background: var(--accent-muted); border-color: var(--accent-muted); opacity: 1; }
```

(This replaces the old `opacity: 0.9` hover with the desaturated variant.)

- [ ] **Step 8: Commit**

```bash
git add app/static/css/app.css
git commit -m "feat(v2.1): CSS tokens — fg-dim WCAG, accent-muted, utilities, chips, mobile menu"
```

---

### Task 2: Base Template — Nav + Footer + Mobile Menu

**Files:**
- Modify: `app/templates/base.html`

- [ ] **Step 1: Replace the topbar with hamburger mobile menu**

Replace the entire `<header class="topbar">...</header>` block with:

```html
<header class="topbar">
  <a class="topbar__brand" href="{{ url_for('home') }}">SPIGNOS</a>
  <details class="topbar__menu">
    <summary class="topbar__toggle" aria-label="Menu">☰</summary>
    <nav class="topbar__nav" aria-label="Navigation">
      <a class="topbar__link" href="{{ url_for('home') }}">Accueil</a>
      <a class="topbar__link" href="{{ url_for('library') }}">Programmes</a>
      <a class="topbar__link" href="{{ url_for('history') }}">Historique</a>
      <a class="topbar__link" href="{{ url_for('physique') }}">Physique</a>
      <a class="topbar__link" href="{{ url_for('dashboard') }}">Synthèse</a>
      <a class="topbar__link" href="{{ url_for('leaderboard_page') }}">Classement</a>
      <a class="topbar__link" href="{{ url_for('squads_list') }}">Squads</a>
      <a class="topbar__link" href="{{ url_for('profile_page') }}">Profil</a>
      <form method="post" action="{{ url_for('logout') }}" style="display:inline;">
        <button type="submit" class="topbar__link topbar__link--btn">Déconnexion</button>
      </form>
    </nav>
  </details>
</header>
```

- [ ] **Step 2: Clean footer**

Replace:
```html
<small>SPIGNOS · FastAPI SSR · v1</small>
```
With:
```html
<small>SPIGNOS</small>
```

- [ ] **Step 3: Commit**

```bash
git add app/templates/base.html
git commit -m "feat(v2.1): nav FR (Synthèse, Classement, Déconnexion) + mobile hamburger + footer clean"
```

---

### Task 3: Welcome Rebrand + Session Francisation

**Files:**
- Modify: `app/templates/welcome.html`
- Modify: `app/templates/session_detail.html`

- [ ] **Step 1: Rebrand welcome page**

Read `app/templates/welcome.html` first. Replace the English title and subtitle with:
- Title: "SPIGNOS"
- Subtitle/tagline: "Cockpit privé d'entraînement et de suivi corporel."
- Remove any mention of "Workout Session Tracking"

- [ ] **Step 2: Francise session_detail labels**

In `app/templates/session_detail.html`:

Replace all occurrences of "Warmup" with "Échauf." :
- `<span class="set-row__kind">Warmup</span>` → `<span class="set-row__kind">Échauf.</span>`
- `<h4 class="set-group-title">Warmup</h4>` → `<h4 class="set-group-title">Échauffement</h4>`

Replace all occurrences of "Work" with "Série" :
- `<span class="set-row__kind">Work</span>` → `<span class="set-row__kind">Série</span>`
- `<h4 class="set-group-title set-group-title--work">Work</h4>` → `<h4 class="set-group-title set-group-title--work">Travail</h4>`

Replace muscle sensation labels:
- `("strong", "Strong")` → `("strong", "Fort")`
- `("partial", "Partial")` → `("partial", "Partiel")`
- `("weak", "Weak")` → `("weak", "Faible")`

Replace "Feedback exercice" with "Ressenti exercice" (if still present as h3).

Replace "Fait" checkbox label with "✓" or keep as-is (checkbox label is minimal).

- [ ] **Step 3: Commit**

```bash
git add app/templates/welcome.html app/templates/session_detail.html
git commit -m "feat(v2.1): welcome rebrand SPIGNOS + session labels FR (Série, Échauf., Fort/Partiel/Faible)"
```

---

### Task 4: Dashboard — Synthèse + Confiance Co-Principal

**Files:**
- Modify: `app/templates/dashboard.html`

- [ ] **Step 1: Read and update dashboard.html**

Read the current file first. Then apply:

1. Replace page title "Body Engineering" with "Synthèse"
2. In the hero card, restructure to make confiance co-principal:
   - Score number stays large
   - Grade badge becomes small (add `style="font-size:11px;"` or use `.chip` class)
   - "Confiance : X" displayed at same visual weight as the score area (not footnote)
   - "N/5 axes actifs" as a visible badge/chip
3. Replace axis labels:
   - "Training Consistency" → "Régularité"
   - "Overload / Progression" → "Progression"
   - "Body Trend" → "Évolution corporelle"
   - "Recovery / Readiness" → "Récupération"
   - "Muscular Balance" → "Équilibre musculaire"
4. In the scoring rules `<details>`, change summary to "Comment ce score est calculé"
5. Replace link text "Voir historique readiness →" with "Voir historique état →"

- [ ] **Step 2: Commit**

```bash
git add app/templates/dashboard.html
git commit -m "feat(v2.1): dashboard — Synthèse, axes FR, confiance co-principal, grade demoted"
```

---

### Task 5: Home + Readiness + Leaderboard + Export + Progress

**Files:**
- Modify: `app/templates/index.html`
- Modify: `app/templates/readiness_history.html`
- Modify: `app/templates/leaderboard.html`
- Modify: `app/templates/export.html`
- Modify: `app/templates/progress.html`

- [ ] **Step 1: Home — "État du jour"**

In `app/templates/index.html`, replace "Readiness du jour" with "État du jour". Replace "Historique →" readiness link text with "Historique état →".

- [ ] **Step 2: Readiness history title**

In `app/templates/readiness_history.html`, replace "Historique Readiness" with "Historique état".

- [ ] **Step 3: Leaderboard — "Classement" + privacy chip**

In `app/templates/leaderboard.html`, replace page title "Leaderboard" with "Classement". Add a privacy note chip near the top:
```html
<p class="chip chip--private mb-md">Données privées protégées · Seule l'activité agrégée est visible</p>
```

- [ ] **Step 4: Export — "Sauvegarde"**

In `app/templates/export.html`, replace page title "Export" with "Sauvegarde". Remove developer-facing text about nginx basic_auth and cron. Keep the download buttons.

- [ ] **Step 5: Progress — minor FR cleanup**

In `app/templates/progress.html`, verify all labels are FR. Fix any remaining English if found.

- [ ] **Step 6: Commit**

```bash
git add app/templates/index.html app/templates/readiness_history.html app/templates/leaderboard.html app/templates/export.html app/templates/progress.html
git commit -m "feat(v2.1): État du jour, Classement, Sauvegarde, privacy chip, labels FR cleanup"
```

---

### Task 6: Squad Templates — Accents + Privacy + Vars

**Files:**
- Modify: `app/templates/squad_detail.html`
- Modify: `app/templates/squad_challenges.html`
- Modify: `app/templates/squad_challenge_detail.html`
- Modify: `app/templates/squad_challenge_create.html`
- Modify: `app/templates/squad_compare.html`
- Modify: `app/templates/squads_list.html`

- [ ] **Step 1: Read all squad templates and fix**

For each squad template:
1. Fix accent typos: "Activite" → "Activité", "Seance" → "Séance", "Metrique" → "Métrique", "Donnees" → "Données", "termine" → "Terminé"
2. Replace hardcoded color vars `var(--c-success, #2ecc71)` with `var(--ok)` and `var(--c-danger, #e74c3c)` with `var(--danger)`
3. Add privacy chip to squad_detail.html header area:
```html
<p class="chip chip--private mb-sm">Activité partagée · Données privées protégées</p>
```
4. Replace inline styles with utility classes where possible

- [ ] **Step 2: Commit**

```bash
git add app/templates/squad_*.html app/templates/squads_list.html
git commit -m "feat(v2.1): squad templates — fix accents, fix vars, privacy chips, utility classes"
```

---

### Task 7: Fix Tests + Final Verification

**Files:**
- Modify: various test files

- [ ] **Step 1: Find and fix tests that match on changed text**

Tests that assert specific label text need updating:
- "Leaderboard" → "Classement" in test assertions
- "Body Engineering" → "Synthèse" in test assertions
- "Dashboard" → "Synthèse" in nav link checks
- "Logout" → "Déconnexion" in any test
- "Warmup" / "Work" → "Échauf." / "Série" in session tests
- "Strong" / "Partial" / "Weak" → "Fort" / "Partiel" / "Faible"

Search across all test files for these strings and update assertions.

- [ ] **Step 2: Run full test suite**

Run: `pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q`
Expected: All pass.

- [ ] **Step 3: Commit**

```bash
git add tests/
git commit -m "test(v2.1): adapt assertions for FR labels — Synthèse, Classement, Série, Échauf."
```

---

### Task 8: Sprint Report

**Files:**
- Create: `docs/SPRINT_V2.1_REPORT.md`

- [ ] **Step 1: Run full test suite**

Run: `pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q`
Expected: All pass.

- [ ] **Step 2: Write report**

Create `docs/SPRINT_V2.1_REPORT.md`:

```markdown
# Sprint Visual Identity V2.1 Report

**Date:** 2026-04-14
**Status:** Complete
**Spec:** docs/strategy/SPIGNOS_VISUAL_IDENTITY_V2.md
**Type:** Presentation-only (zero backend changes)

## Deliverables

| Change | Files |
|--------|-------|
| CSS tokens (fg-dim WCAG, accent-muted, utilities, chips, mobile menu) | app.css |
| Nav FR + mobile hamburger + footer clean | base.html |
| Welcome rebrand SPIGNOS | welcome.html |
| Session francisation (Série, Échauf., Fort/Partiel/Faible) | session_detail.html |
| Dashboard Synthèse + confiance co-principal | dashboard.html |
| Labels FR (État du jour, Classement, Sauvegarde) | index, readiness, leaderboard, export, progress |
| Squad accents + vars + privacy chips | squad_*.html |

## Verification

```
pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q
```
```

- [ ] **Step 3: Commit**

```bash
git add docs/SPRINT_V2.1_REPORT.md
git commit -m "docs(v2.1): sprint report — visual identity V2.1 complete"
```
