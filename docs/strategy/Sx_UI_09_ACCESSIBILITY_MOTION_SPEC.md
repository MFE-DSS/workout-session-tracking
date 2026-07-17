# Sx_UI_09 — Accessibility & Motion — SPEC

**Type** : SPEC / AUDIT — **NO CODE**, docs-only
**Statut** : ✅ **SPEC RÉDIGÉE** (attente human review)
**Date** : 2026-07-17
**Baseline auditée** : `e1d7df2`
**Origine** : queue résiduelle `Sx_UI_12` (dette a11y transverse différée par `Sx_UI_03`)

> Spec de fermeture des **dettes d'accessibilité transverses** identifiées par `Sx_UI_12` et confirmées
> par audit du code réel. Cible **WCAG 2.2 niveau AA**, produit **non médical**, **SSR / no-JS**, tokens
> **Auren Terminal existants** (0 nouvelle couleur). Ne refait pas les acquis a11y déjà en place.

---

## 0. Étape 0 — Brainstorming / Options / Risques / Choix retenu

### 0.1 Contexte audité (faits, baseline `e1d7df2`)
| Axe | État réel mesuré | Verdict |
|---|---|---|
| **reduced-motion** | `session_focus.css` (7) + `body_intelligence.css` (1) ont des blocs `prefers-reduced-motion` ; **`app.css` a des transitions/animations et 0 bloc** | **GAP réel** |
| **form-errors** | `login.html`/`register.html` = `<div class="integrity-errors"><b>{{ error }}</b>` ; **0 `role="alert"`/`aria-live`/`aria-invalid`/`aria-describedby`** (seul `rest_timer` a de l'aria-live, non-form) | **GAP réel** |
| **contraste `--fg-dim`** (`#8A94A0`, 87 usages) | ratio mesuré : **6.06:1 sur `--bg`**, 5.68 sur `--surface`, 5.31 sur `--surface-2` — **tous ≥ 4.5 → AA texte normal PASS** | **PASS (hypothèse Sx_UI_12 infirmée)** → verrouiller par test, pas corriger |
| forces acquises | skip-link ✅ · `aria-current` (12) ✅ · `sr-only` ✅ · landmarks (header/nav/main/footer) ✅ · tap ≥44px ✅ · no-JS ✅ · SVG décoratifs `aria-hidden` ✅ | **ne pas refaire** |

Contrastes de référence (sur `--bg #0F1318`) : `--fg` 15.69 · `--fg-muted` 8.49 · `--accent` 7.74 ·
`--fg-dim` 6.06 — **tous AA-conformes**.

### 0.2 Options
| Option | Description | Verdict |
|---|---|---|
| **A** | Spec ciblée sur les **2 gaps réels** (reduced-motion, form-errors ARIA) + **1 axe verrouillé par test** (contraste, déjà AA) ; WCAG AA ; sans refaire les acquis | ✅ **RETENU** |
| B | Audit a11y **exhaustif** (charts SVG, BodyMap, refonte auth) | ❌ sur-périmètre ; charts/BodyMap = surveillance, pas refonte V1 |
| C | Scope minimal (reduced-motion + form-errors seulement, contraste différé) | ❌ laisse l'axe contraste non verrouillé (régression possible) |
| D | Correction du contraste `--fg-dim` | ❌ inutile : `--fg-dim` **passe déjà AA** (mesuré) ; corriger = churn sans gain |

### 0.3 Risques
| Risque | Parade |
|---|---|
| Sur-périmètre (tout a11y d'un coup) | 3 lots bornés (§9), forces acquises exclues |
| Casser une animation nécessaire à la compréhension | reduced-motion = neutraliser transitions **décoratives** ; conserver l'ordre DOM/état |
| Introduire du JS pour les erreurs | **no-JS** : `role="alert"`/`aria-live` sont **SSR-only** (annoncés au reload), pas de client |
| Régression contraste future | test de garde sur les ratios tokens (verrouille l'acquis) |
| Toucher les pages auth standalone (hors base.html) | autorisé **ciblé** pour les form-errors (login/register), pas de refonte |

### 0.4 Choix retenu
**Option A.** WCAG 2.2 **AA**, non médical, SSR/no-JS, tokens Auren existants. 3 lots : reduced-motion
global · form-errors ARIA · audit/verrouillage contraste. Charts/BodyMap = **non-goal V1** (surveillance).

---

## 1. Objectif
Fermer les dettes a11y transverses **réelles** pour atteindre un socle **WCAG 2.2 AA** cohérent sur le
shell + les surfaces principales, **sans** régresser le no-JS, l'identité Auren Terminal, ni les acquis.

## 2. Cible normative
- **WCAG 2.2 niveau AA** (pas AAA).
- **Produit non médical** : aucune allégation clinique ; l'a11y ne change pas la sémantique métier.
- **SSR / no-JS** : toute annonce d'erreur est rendue côté serveur ; progressive enhancement jamais requis.
- **Tokens Auren Terminal existants** : graphite/mono/ambre `#C8A24B` ; **0 nouvelle couleur**.

## 3. Gaps à fermer (audités)
### 3.1 Reduced-motion (global)
`app.css` définit des `transition:`/`animation:` sans contrepartie `@media (prefers-reduced-motion:
reduce)`. Cible : un bloc reduced-motion **global** ramenant les transitions/animations **décoratives** à
`0ms`/`none`, cohérent avec les blocs déjà présents (`session_focus`/`body_intelligence`). Conserver
l'ordre DOM et les états (jamais de perte d'information).

### 3.2 Form-errors ARIA
Les erreurs de formulaire (login/register — et tout formulaire rendant `error`/`integrity-errors`)
doivent être **annoncées** : conteneur d'erreur `role="alert"` (ou `aria-live="assertive"`), champ invalide
`aria-invalid="true"` + `aria-describedby` pointant le message. **SSR-only** (pas de JS). Champs et labels
inchangés fonctionnellement.

### 3.3 Contraste (verrouillage, pas correction)
`--fg-dim` et les autres tokens de texte **passent déjà AA** (mesuré §0.1). L'axe devient un **test de
garde** : vérifier programmatiquement que les ratios (`--fg`/`--fg-muted`/`--fg-dim`/`--accent` sur
`--bg`/`--surface`/`--surface-2`) restent ≥ 4.5 (texte normal) / ≥ 3.0 (large/UI), pour empêcher toute
régression future. Documenter les edge cases (ex. `--fg-dim` sur `--accent` = à éviter en texte fin).

## 4. Acquis a11y à préserver (ne pas refaire)
Skip link (`Sb_UI_03.3`) · `aria-current` par région (`Sx_NAV_01`/`03.x`) · `sr-only` · landmarks
sémantiques · tap targets ≥44px · SVG décoratifs `aria-hidden`/`focusable=false` · no-JS intégral ·
`:focus-visible` sur nav/skip-link. Ces éléments sont **hors scope** (déjà conformes).

## 5. Non-goals
- ❌ Accessibilité des **charts SVG** / du **BodyMap** (surveillance V2, pas de refonte ici).
- ❌ Refonte des **pages auth standalone** (seuls les form-errors login/register sont touchés, ciblé).
- ❌ Passage **AAA**.
- ❌ Ajout de **JavaScript** (toute a11y reste SSR/progressive-enhancement).
- ❌ Nouvelle couleur / nouveau token d'identité ; correction de `--fg-dim` (déjà AA).
- ❌ Changement de route/service/model/migration/données/logique métier.
- ❌ Activation Body Intelligence ; aucun contenu médical.

## 6. Contraintes
- SSR FastAPI + Jinja2, no-JS, mobile-first, Auren Terminal.
- Template + CSS only par lot ; aucun backend.
- Chaque lot code : ruff budget, spec_protocol, check_scope, **CI 3/3**, human review.
- Reduced-motion : neutraliser le **décoratif**, jamais l'information.

## 7. Risques
Voir §0.3 : sur-périmètre · animation utile neutralisée · JS introduit · régression contraste · auth
standalone. Parades : lots bornés, reduced-motion décoratif seulement, SSR-only, test de garde contraste,
form-errors ciblés.

## 8. Gating
- CI complète (3 jobs) sur chaque build code.
- Docs-only commits skippés par `paths-ignore: docs/**`.
- Baseline visuelle : les changements reduced-motion/contraste sont invisibles au repos → pas de churn
  screenshot ; `Sb_UI_11.3` (baseline finale) reste indépendant.

## 9. Plan de build recommandé (split Sx_UI_09)
| Lot | Portée | Tier probable | Note |
|---|---|---|---|
| **`Sb_UI_09.1`** Reduced-Motion Global | bloc `@media (prefers-reduced-motion: reduce)` dans `app.css` (transitions/animations décoratives → 0) | shared_code (app.css) | cohérent avec les blocs existants ; 0 perte d'info |
| **`Sb_UI_09.2`** Form-Errors ARIA | `role="alert"`/`aria-live` + `aria-invalid`/`aria-describedby` sur login/register (+ formulaires rendant `error`) | isolated→shared | **SSR-only, no-JS** ; labels/champs inchangés |
| **`Sb_UI_09.3`** Contrast Guard | test de garde ratios tokens (≥AA) + doc edge cases | isolated (test+docs) | **verrouille l'acquis**, ne corrige rien (`--fg-dim` déjà AA) |
| **`Sx_UI_09` Closeout** | acter le socle AA | docs | après les 3 lots + reviews |

Ordre recommandé : `09.1 → 09.2 → 09.3 → closeout`. Chaque lot = template/CSS/test only, CI 3/3, review.

## 10. Non-goals (rappel structurel)
Aucun code hors scope · aucun JS · aucune nouvelle couleur · aucune correction `--fg-dim` (déjà AA) ·
aucune refonte charts/BodyMap/auth · aucun AAA · aucun changement route/service/model/métier · non médical.

## Verdict

**Verdict :** ✅ **Sx_UI_09 — SPEC RÉDIGÉE (Option A : socle WCAG AA ciblé).** L'audit du code réel
(baseline `e1d7df2`) confirme **2 gaps a11y réels** — reduced-motion absent d'`app.css`, form-errors
login/register sans `role="alert"`/`aria-live`/`aria-invalid` — et **infirme** l'hypothèse contraste de
`Sx_UI_12` : `--fg-dim #8A94A0` mesure **6.06:1 sur `--bg`** (et ≥5.3 sur les surfaces), soit **AA texte
normal PASS** ; l'axe contraste devient donc un **test de garde** (verrouiller l'acquis) plutôt qu'une
correction. Cible **WCAG 2.2 AA**, **non médical**, **SSR/no-JS**, tokens Auren existants (**0 nouvelle
couleur**). Les acquis (skip-link, `aria-current`, landmarks, tap ≥44px, SVG décoratifs, no-JS) sont
**préservés, pas refaits**. Charts/BodyMap et refonte auth = **non-goals V1**. Split : `Sb_UI_09.1`
reduced-motion → `.2` form-errors ARIA → `.3` contrast guard → closeout. **Aucun fichier applicatif touché
par cette spec.**

**Recommandation** : **GO COMMIT SPEC** (docs-only), puis premier build **`Sb_UI_09.1` Reduced-Motion
Global** (le plus net, CSS-only, sûr). Après `Sx_UI_09` : `Sb_UI_11.3` Final Auren Baseline, puis `Sx_UI`
Global Final Closeout (queue `Sx_UI_12`).
