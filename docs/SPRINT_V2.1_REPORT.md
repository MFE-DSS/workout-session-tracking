# Sprint Visual Identity V2.1 Report

**Date:** 2026-04-14
**Status:** Complete
**Spec:** docs/strategy/SPIGNOS_VISUAL_IDENTITY_V2.md
**Type:** Presentation-only (zero backend changes)
**Tests:** 478 passed, 0 failed

## Objective

Upgrade SPIGNOS visual identity from "generic web app" to "private body
engineering cockpit" — full French lexicon, WCAG-compliant tokens, mobile
hamburger menu, dashboard anti-pseudo-science display, privacy cues.

## Deliverables

| Change | Files | Impact |
|--------|-------|--------|
| CSS tokens (fg-dim WCAG, accent-muted, utilities, chips, mobile menu) | app.css | Tokens + 30 new classes |
| Nav FR + mobile hamburger + footer clean | base.html | Synthèse, Classement, Déconnexion, ☰ mobile |
| Welcome rebrand | welcome.html | "SPIGNOS" + tagline FR |
| Session francisation | session_detail.html | Série, Échauf., Fort/Partiel/Faible, Ressenti |
| Dashboard Synthèse | dashboard.html, dashboard.py | Axes FR, confiance co-principal, grade demoted |
| Labels FR | index, readiness, leaderboard, export, progress | État du jour, Classement, Sauvegarde |
| Squad fixes | squad_*.html | Accents, vars, privacy chips |
| Test adaptations | 5 test files | Label assertions updated |

## Key V2.1 Corrections (from prompt engineer review)

1. **Squads = terme produit** — ilot anglais declare, politique linguistique explicite
2. **Scroll horizontal** — overflow global interdit, rails intentionnels autorises
3. **--fg-dim** — eclaircit #5a6270 → #6e7785 pour WCAG 4.5:1 a 12-14px
4. **Dashboard** — confiance + axes actifs co-principaux, grade A/B/C en chip secondaire
5. **Accent saturation** — --accent-muted (#d4715a) pour hover/focus (Material dark)

## Verification

```bash
pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q  # 478 passed
```

## Zero breaking changes

- No routes changed
- No models changed
- No services changed (except dashboard.py axis labels — already FR)
- No migrations
