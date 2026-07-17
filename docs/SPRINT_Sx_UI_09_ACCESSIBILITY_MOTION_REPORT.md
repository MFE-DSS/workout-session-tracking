# Sprint Sx_UI_09 — Accessibility & Motion — SPEC REPORT

**Type** : SPEC / AUDIT — **NO CODE**, docs-only
**Statut** : 🟢 **SPEC LIVRÉE** (attente human review)
**Date** : 2026-07-17
**Baseline** : `e1d7df2`
**Spec détaillée** : `docs/strategy/Sx_UI_09_ACCESSIBILITY_MOTION_SPEC.md`

---

## Origine
Queue résiduelle `Sx_UI_12` — dette a11y transverse **différée** par le cycle `Sx_UI_03` (App Shell &
Navigation, CLOSED). Le skip link (`Sb_UI_03.3`) était le seul élément a11y livré ; le reste est réservé
à `Sx_UI_09`.

## Décision : Option A — socle WCAG AA ciblé
Spec bornée sur les **gaps a11y réels** (audités sur le code), cible WCAG 2.2 **AA**, produit **non
médical**, **SSR/no-JS**, tokens Auren existants (**0 nouvelle couleur**). Sans refaire les acquis.

## Audit du code réel (faits)
| Axe | Mesure | Verdict |
|---|---|---|
| reduced-motion | `app.css` a des transitions/animations, **0** bloc `prefers-reduced-motion` (seuls `session_focus`/`body_intelligence` en ont) | **GAP** → `Sb_UI_09.1` |
| form-errors | login/register = `<div class="integrity-errors"><b>{{ error }}</b>`, **0** `role=alert`/`aria-live`/`aria-invalid`/`aria-describedby` | **GAP** → `Sb_UI_09.2` |
| contraste `--fg-dim` `#8A94A0` (87 usages) | **6.06:1 sur `--bg`**, 5.68/`--surface`, 5.31/`--surface-2` → **AA texte normal PASS** | **PASS** (hypothèse Sx_UI_12 infirmée) → `Sb_UI_09.3` **test de garde**, pas correction |

Contrastes de référence sur `--bg` : `--fg` 15.69 · `--fg-muted` 8.49 · `--accent` 7.74 · `--fg-dim`
6.06 — **tous AA**.

## Acquis préservés (hors scope)
skip link · `aria-current` par région · `sr-only` · landmarks · tap ≥44px · SVG décoratifs `aria-hidden`
· no-JS · `:focus-visible`.

## Non-goals
Charts SVG / BodyMap (surveillance V2) · refonte auth standalone · AAA · JavaScript · nouvelle couleur ·
correction `--fg-dim` (déjà AA) · changement route/service/model/métier · médical.

## Split recommandé
`Sb_UI_09.1` Reduced-Motion Global → `Sb_UI_09.2` Form-Errors ARIA (SSR/no-JS) → `Sb_UI_09.3` Contrast
Guard (test) → `Sx_UI_09` closeout. Chaque lot : template/CSS/test only, CI 3/3, review.

## Fichiers docs
- `docs/strategy/Sx_UI_09_ACCESSIBILITY_MOTION_SPEC.md` (spec + Non-goals + verdict)
- `docs/SPRINT_Sx_UI_09_ACCESSIBILITY_MOTION_REPORT.md` (ce fichier)
- `docs/strategy/SPEC_REGISTRY.md` + `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` (entrées)

Aucun `app/**`, `tests/**`, asset touché.

---

## Verdict

**Verdict :** 🟢 **Sx_UI_09 — SPEC LIVRÉE (Option A : socle WCAG AA ciblé, docs-only).** Audit du code
réel : **2 gaps** (reduced-motion absent d'`app.css` ; form-errors login/register sans ARIA) + **1 axe
verrouillé par test** (contraste `--fg-dim` **déjà AA** à 6.06:1 — hypothèse Sx_UI_12 infirmée). WCAG 2.2
AA, non médical, SSR/no-JS, tokens Auren (0 nouvelle couleur) ; acquis a11y préservés ; charts/BodyMap/auth
= non-goals V1. Split `09.1`→`.2`→`.3`→closeout. Aucun fichier applicatif touché.

**Recommandation** : **GO COMMIT SPEC** (docs-only), puis premier build **`Sb_UI_09.1` Reduced-Motion
Global** (CSS-only, sûr).
