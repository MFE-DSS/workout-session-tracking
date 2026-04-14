# SPIGNOS — Sprint Synthesis for Prompt Engineer Handoff

**Date:** 2026-04-14
**Branch:** `claude/sprint-reporting-fitness-app-V7Qr6`
**Tests:** 478 passed, 0 failed
**Commits:** 42 commits across 13 sprints (7 builds + 4 specs + 2 polish)

---

## Stack & Architecture (unchanged)

FastAPI SSR + Jinja2 + SQLite + Alembic + Nginx/systemd.
Mobile-first, no SPA, no JS framework, minimal vanilla JS.
Private by default, deterministic scoring, no AI/ML.

---

## What Was Delivered

### Foundation Sprints (S0-S2): Single-User Body Engineering

| Sprint | What | Key Deliverables |
|--------|------|-----------------|
| **S0** — Catalog Integrity | Stabilize exercise catalogue as analytics foundation | QA script (7 checks), 10 CI-blocking tests, governance doc, 5 focus corrections, version v6 |
| **S1** — Body Metrics + Readiness | First body engineering data layer | Lateralized measurements (arm/thigh L/R + hip + neck), readiness lite (5 dimensions 1-5), Home widget, `/readiness/history` |
| **S2** — Body Engineering Dashboard | Unified synthesis across 3 data streams | `/dashboard` with 5-axis scoring (consistency, progression, body trend, recovery, balance), per-axis confidence, graceful degradation |

### Social Sprints (S3-S4): Private Squads & Engagement

| Sprint | What | Key Deliverables |
|--------|------|-----------------|
| **S3** — Private Squads | First social layer | Squad CRUD, invite codes (SPGN-XXXX, 48h expiry), scoped leaderboard, strict privacy model (training activity visible, body/readiness never) |
| **S4** — Challenges, Compare, Sharing | Engagement loops | Time-boxed challenges (4 metrics: sessions/score/tonnage/streak), 1:1 compare mode, template recommendations, anonymized session sharing |

### Exercise System Sprints (Sx/Sb): Signal + UX + Substitution

| Sprint | Type | What | Key Deliverables |
|--------|------|------|-----------------|
| **Sx_01** | Spec | Feedback rationalization | Audit of all feedback fields, decision: success_score derived, eq/rt hidden, sensation optional |
| **Sb_01** | Build | Feedback signal refactor | `compute_success_score()` (snap to {100,80,50}), -41% inputs per exercise (27→16) |
| **Sx_02** | Spec | Mobile exercise entry UX | `<details>` accordion design, compact summary, feedback at bottom |
| **Sb_02** | Build | Mobile session flow | Exercise cards in `<details>`, server-side `?active=` routing, zero JS |
| **Sx_03** | Spec | Exercise substitution graph | JSON catalogue substitutes, additive `substituted_name` field, lock after first set |
| **Sb_03** | Build | Substitution graph | Migration, catalogue v7 (10 exercises with substitutes), select UI, `actual_exercise_name()` for muscle_scoring |
| **Sx_04** | Spec | Exercise system consolidation | Cross-spec alignment, build queue, dependency analysis |

### UX Polish

| Fix | Change |
|-----|--------|
| Substitution UI | Segmented radios (design system) instead of dropdown, collapsed in `<details>` |
| Warmup logic | 2 warmup sets for first exercise only, 1 for the rest |
| History layout | Proper card spacing, no visual overlap |
| Physique grid | Zone cards in responsive 2-column grid instead of vertical stack |
| Feedback labels | French with micro-descriptions ("Focalisé/Correct/Distrait", "En forme/Moyen/Fatigué") |

---

## Current Product State

### Pages

| Route | Function |
|-------|----------|
| `/` | Home — readiness widget, behavioral state, KPIs, sparkline |
| `/dashboard` | Body Engineering — 5-axis synthesis, global score, confidence |
| `/physique` | Physique — radar SVG, 11 zone cards (responsive grid) |
| `/library` | Catalogue — templates grouped by section |
| `/library/{slug}` | Template detail — start session |
| `/sessions/{id}` | Session — `<details>` accordion, substitution, derived scoring |
| `/history` | Session history — clean cards, status filters |
| `/progress` | Progression — KPIs, timelines |
| `/readiness/history` | Readiness — 90-day history |
| `/profile` | Profile — lateralized measurements, protocol tips |
| `/squads` | Squad list — create, join |
| `/squads/{id}` | Squad detail — leaderboard, challenges, activity, compare, share |
| `/squads/{id}/challenges` | Challenge list |
| `/squads/{id}/challenges/{cid}` | Challenge standings |
| `/squads/{id}/compare` | 1:1 member comparison |
| `/leaderboard` | Global leaderboard |
| `/export` | Backup — JSON + CSV |

### Data Model (post all migrations)

| Table | Added by |
|-------|----------|
| `workout_sessions` | V1 |
| `session_exercises` | V1 (+`substituted_name` by Sb_03) |
| `set_logs` | V1 |
| `workout_templates` | V1 (+`catalog_section`, `display_order`) |
| `template_exercises` | V1 (+`substitutes_json` by Sb_03) |
| `rep_targets` | V1 |
| `users` | V1 |
| `body_measurements` | S1 (lateralized: arm_cm_left/right, thigh_cm_left/right, hip_cm, neck_cm) |
| `readiness_entries` | S1 (5 dimensions 1-5, recorded_on DATE, unique per user/day) |
| `squads` | S3 |
| `squad_memberships` | S3 |
| `squad_invite_codes` | S3 |
| `squad_challenges` | S4 |
| `squad_template_recommendations` | S4 |
| `squad_shared_sessions` | S4 |

### Key Architectural Patterns

- **Snapshot resilience**: sessions snapshot template/exercise names at creation. Catalogue can reseed without breaking history.
- **Derived success_score**: computed from set data vs rep_targets, snapped to {100,80,50}. Zero read-side changes — all consumers read the same column.
- **Privacy model**: squads share training activity (score, sessions, streak, templates). Never: body measurements, readiness, weights/reps, notes.
- **Graceful degradation**: dashboard axes activate as data becomes available. Insufficient data = greyed out with guidance, not zero.
- **Focus = editorial, mapping = analytical**: catalogue `focus` field is for UI. `classify_exercise()` is the analytical truth for zone scoring.

---

## Design System & Visual Identity

### Philosophy

SPIGNOS follows an "Engineered, structured, calm, precise" design language. Dark theme only. No decorative elements. Information density is controlled — every pixel earns its place. The aesthetic targets a user who trains seriously and wants a cockpit, not an app that congratulates them for showing up.

### Color Palette

| Token | Hex | Role |
|-------|-----|------|
| `--bg` | `#0f1115` | Page background — near-black |
| `--surface` | `#161a22` | Card/component background |
| `--surface-2` | `#1e222c` | Input fields, nested surfaces |
| `--border` | `#232834` | Subtle borders, separators |
| `--fg` | `#e8ecf1` | Primary text — off-white |
| `--fg-muted` | `#9aa3ad` | Secondary text, labels |
| `--fg-dim` | `#5a6270` | Tertiary text, hints |
| `--accent` | `#f25f3a` | Primary action color — warm orange |
| `--accent-soft` | `#f25f3a1a` | Accent background tint (10% opacity) |
| `--ok` | `#2ecc71` | Success, completed, positive |
| `--ok-soft` | `#2ecc711a` | Success background tint |
| `--warn` | `#f4a261` | Warning, caution |
| `--danger` | `#e74c3c` | Destructive actions, errors |
| `--info` | `#3b82f6` | Informational, cardio type |

### Typography

| Token | Value | Usage |
|-------|-------|-------|
| `--font` | `'Inter', system-ui, sans-serif` | All UI text |
| `--font-mono` | `'JetBrains Mono', 'SF Mono', monospace` | Scores, stats, badges, tabular data |
| Base font size | `14px` | Body text |
| Page title | `18px / 600` | H1 pages |
| Section header | `13px / 600 / uppercase / 0.5px tracking` | Section labels |
| KPI value | `24px / 700 / mono / tabular-nums` | Key numbers |
| Badge | `11px / 600 / mono` | Status pills |

### Spacing Scale

| Token | Value |
|-------|-------|
| `--space-xs` | 4px |
| `--space-sm` | 8px |
| `--space-md` | 16px |
| `--space-lg` | 24px |
| `--space-xl` | 32px |
| `--space-2xl` | 48px |

### Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `--radius` | 8px | Cards, tiles, containers |
| `--radius-sm` | 4px | Buttons, inputs, badges, segmented controls |

### Layout

| Component | Behavior |
|-----------|----------|
| `.container` | `max-width: 640px`, centered, `padding: 16px` sides + `96px` bottom (safe area for mobile nav) |
| `.cockpit-grid` | Single column on mobile (no CSS grid on mobile). On desktop, used with `.cockpit-main` + `.cockpit-side` for 2-column layouts (physique radar + zones, profile form + charts). |
| `.tile-grid` | 2-column grid for home page quick-action tiles |

### Component Library

| Component | CSS Class | Visual |
|-----------|-----------|--------|
| **Card** | `.card` | Dark surface (`--surface`), `1px --border`, `8px radius`, `16px padding` |
| **Badge** | `.badge` | Mono font, 11px, pill shape. Variants: `--completed` (green), `--in_progress` (orange), `--neutral` (grey) |
| **Grade badge** | `.grade-badge` | Circular 22px, bold letter. `--a` green, `--b` orange, `--c` grey |
| **Button** | `.btn` | 14px, 500 weight, `4px radius`. Variants: `--primary` (accent bg), `--ghost` (transparent), `--end` (green, "Terminer"), `--danger` (red), `--sm` (compact) |
| **Segmented control** | `.segmented` | Horizontal radio group in `--surface-2` container. Selected option: `--surface` bg, 600 weight. Used for all 3-option feedback (concentration, sensation, etc.) |
| **KPI block** | `.kpi` | Centered column: large mono value + small uppercase label |
| **Insight block** | `.insight` | Left accent border (3px), 32px value, recommendation text below |
| **Zone card** | `.zone-card` | Compact card with label + score bar + meta. Post-S4: responsive grid layout |
| **Zone bar** | `.zone-bar` | Thin progress bar (4px height), fill proportional to score |
| **Tile** | `.tile` | Home page action block, 80px min-height. `--primary` has accent left border. `--resume` has green left border |
| **Jump bar** | `.ex-jump` | Horizontal scroll nav for exercise cards. Items: code + progress count. States: `--done` (green), `--partial` (orange), `--feedback` (final item) |
| **Exercise card** | `details.exercise-card` | `<details>` accordion. Compact `<summary>` (code + name + progress + recap). Open: accent border. Done: muted colors, green code |
| **Active banner** | `.active-banner` | Sticky bar below topbar with pulsing green dot, session name, "Reprendre →" CTA |
| **Topbar** | `.topbar` | Sticky, `--bg` background, bottom border. Brand + horizontal nav links |
| **Filter bar** | `.filter-bar` | Horizontal tabs (30j/60j/90j or status filters). Active item gets `is-active` class |
| **Stats list** | `.stats-list` | Key-value rows with bottom borders, used in profile and export |
| **Template card** | `.template-card` | Library cards with accent left border (blue for cardio). Name + focus + hint |

### Interactive Patterns

| Pattern | Mechanism | JS |
|---------|-----------|-----|
| **Accordion exercise cards** | `<details open>` server-side via `?active=` query param | Zero |
| **Readiness widget** | `<details>` collapsed form on Home, badges when filled | Zero |
| **Muscle sensation** | `<details>` collapsed optional section in exercise card | Zero |
| **Substitution picker** | `<details>` with segmented radios, collapsed "Machine indisponible ?" | Zero |
| **Scoring rules** | `<details>` collapsible on dashboard page | Zero |
| **SVG radar chart** | Server-rendered SVG, interactive hover/focus via CSS | CSS only (`:hover`, `:focus-within` for data point labels) |
| **SVG timelines** | Server-rendered SVG (bodyweight, quality, measurements) | CSS only |

### Mobile Considerations

| Aspect | Implementation |
|--------|---------------|
| Viewport | `viewport-fit=cover`, safe area padding via `env(safe-area-inset-top)` |
| PWA | Manifest + theme-color + apple-mobile-web-app meta tags |
| Touch targets | Buttons min 44px implied by padding. Segmented options have 6px+8px padding |
| Input types | `inputmode="decimal"` for weight, `inputmode="numeric"` for reps. Number step=0.5 for weight |
| Font smoothing | `-webkit-font-smoothing: antialiased` |
| Container | 640px max-width, 96px bottom padding for thumb-reachable bottom actions |

### Page Layout Map

```
┌─────────────────────────────────────────────┐
│ TOPBAR (sticky)                             │
│ SPIGNOS    Accueil Programme Historique ...  │
├─────────────────────────────────────────────┤
│ ACTIVE BANNER (if session open)             │
│ ● Séance en cours · Push A · Reprendre →    │
├─────────────────────────────────────────────┤
│                                             │
│ CONTAINER (640px max, centered)             │
│                                             │
│   PAGE TITLE                                │
│                                             │
│   CONTENT (varies by page)                  │
│                                             │
│     Home: insight → KPIs → sparkline → tiles│
│     Session: jumpbar → <details> cards → FB │
│     Dashboard: hero score → 5 axis cards    │
│     Physique: radar SVG → zone grid         │
│     Squad: leaderboard → challenges →       │
│            activity → compare → sharing     │
│                                             │
├─────────────────────────────────────────────┤
│ FOOTER                                      │
│ SPIGNOS · FastAPI SSR · v1    Contact       │
└─────────────────────────────────────────────┘
```

### Session Page Flow (post Sb_01 + Sb_02 + Sb_03)

```
┌─ Session Header ────────────────────────────┐
│ Push A — Pecs épaisseur + Delts + Triceps   │
│ Mardi · 14/04 07:24 · [En cours]           │
│ 3 / 25 work sets                            │
└─────────────────────────────────────────────┘

┌─ Jump Bar (horizontal scroll) ──────────────┐
│ [E1 3/3] [E2 0/3] [E3 0/3] ... [FB]       │
└─────────────────────────────────────────────┘

┌─ E1 Incline Smith Press ──────── 3/3 ──────┐
│  60/62.5/65 kg · 10/8/8 reps              │ ← compact (collapsed)
└─────────────────────────────────────────────┘

┌─ E2 Chest Press machine ──────── 0/3 ──────┐  ← OPEN (active)
│                                             │
│  Voir historique E2 →                       │
│  3× 8-12                                   │
│                                             │
│  [Machine indisponible ? Substituer →]      │  ← collapsed <details>
│    ○ Chest Press machine                    │
│    ○ Développé couché haltères              │
│    ○ Dips pectoraux                         │
│                                             │
│  Dernière fois · il y a 5j                  │
│  60/60/60 kg · 10/10/10 reps               │
│  Delta · +2.5 kg · = reps                  │
│  Repère · viser 12 reps avant d'augmenter  │
│                                             │
│  WARMUP                                     │
│  [Warmup #1]  kg [___] reps [___] □ Fait   │
│                                             │
│  WORK                                       │
│  [Work #1]    kg [___] reps [___] □ Fait   │
│  [Work #2]    kg [___] reps [___] □ Fait   │
│  [Work #3]    kg [___] reps [___] □ Fait   │
│                                             │
│  [Sensation musculaire (optionnel)]         │  ← collapsed
│  [Note (optionnel)]                         │
│                                             │
│  [████ Enregistrer E2 ████]                │
└─────────────────────────────────────────────┘

┌─ E3 ... ──────────────────────── 0/3 ──────┐ ← compact
└─────────────────────────────────────────────┘
... (E4-E8 compact) ...

┌─ Bilan de la séance ───────────────────────┐
│  Concentration mentale                      │
│  Étais-tu focalisé sur tes mouvements ?    │
│  [Focalisé] [Correct] [Distrait]           │
│                                             │
│  Énergie générale                           │
│  Comment te sentais-tu ?                    │
│  [En forme] [Moyen] [Fatigué]             │
│                                             │
│  Poids du corps (optionnel) [___] kg       │
│  Note (optionnel) [________________]       │
│                                             │
│  [Enregistrer]  [Terminer la séance]       │
└─────────────────────────────────────────────┘
```

---

## Documentation Produced

### Specs (in `docs/strategy/`)

| File | Purpose |
|------|---------|
| `SPIGNOS_CATALOG_GOVERNANCE.md` | Source of truth, versioning, modification workflow |
| `SPIGNOS_CATALOG_QA_REPORT.md` | Generated QA report (PASS) |
| `SPIGNOS_BODY_METRICS_READINESS_SPEC.md` | Body metrics + readiness spec |
| `SPIGNOS_SCORING_RULES_V1.md` | Dashboard scoring formulas |
| `SPIGNOS_BODY_ENGINEERING_DASHBOARD_V1.md` | Dashboard feature spec |
| `SPIGNOS_SQUADS_SPEC.md` | Squads feature spec |
| `SPIGNOS_SQUADS_PRIVACY_MODEL.md` | Privacy enforcement rules |
| `SPIGNOS_EXERCISE_FEEDBACK_RATIONALIZATION.md` | Feedback field audit + decisions |
| `SPIGNOS_MOBILE_EXERCISE_ENTRY_UX.md` | Mobile UX spec |
| `SPIGNOS_EXERCISE_SUBSTITUTION_GRAPH_SPEC.md` | Substitution spec |
| `SPIGNOS_EXERCISE_SYSTEM_CONSOLIDATION_SPEC.md` | Cross-spec alignment |
| `SPIGNOS_EXERCISE_SYSTEM_ROADMAP.md` | Exercise system roadmap |
| `SPIGNOS_SUPERPOWER_SPRINT_QUEUE.md` | Sprint tracking |

### Sprint Reports (in `docs/`)

S0, S1, S2, S3, S4, Sb_01, Sb_02, Sb_03 — each with deliverables, verification commands, files modified, gaps.

---

## Remaining Build Queue

| Sprint | Status | Scope |
|--------|--------|-------|
| **Sb_04** — History & Analytics Alignment | Pending | exercise_history shows actual name, export includes substituted_name, QA validates substitutes |
| **S5** — Photo Pipeline | Deferred | Progress photos, capture protocol, storage abstraction (experimental branch) |
| **S6** — Image Anthropometry | Deferred | Experimental estimation provider, feature flag, stub/mock (experimental branch) |

---

## Constraints to Maintain

1. **No SPA** — SSR only, no JS framework
2. **No public data** — squads are private, no feed, no global rankings beyond leaderboard
3. **No AI/ML claims** — deterministic scoring, documented formulas
4. **No body data in social** — measurements, readiness, weights/reps never exposed to squad members
5. **No photo as source of truth** — photos are supplementary, manual measurements are canonical
6. **Snapshot resilience** — catalogue can reseed without breaking session history
7. **Mobile-first** — one hand, gym context, minimal inputs

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Tests | 478 passing |
| Commits | 42 |
| New tables | 9 (across S1-S4) |
| New services | 12 |
| New templates | 15 |
| Specs written | 13 |
| Sprint reports | 8 |
| Inputs/exercise | 27 → 16 (-41%) |
| Pages | 17 routes |
