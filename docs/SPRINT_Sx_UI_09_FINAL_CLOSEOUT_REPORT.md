# Sx_UI_09 — Accessibility & Motion — FINAL CLOSEOUT REPORT

**Verdict** : ✅ **Sx_UI_09 — CLOSED / HUMAN REVIEW COMPLETE**
**Type** : CLOSEOUT — docs-only (aucun code/test/CSS/template touché)
**Date** : 2026-07-19
**Baseline canonique** : `64a7435`
**Spec fondatrice** : `Sx_UI_09_ACCESSIBILITY_MOTION_SPEC.md` (SPEC RÉDIGÉE, Option A)

> Le cycle **Accessibility & Motion** ferme la dette a11y transverse identifiée par `Sx_UI_12` et
> différée par `Sx_UI_03`. Socle **WCAG 2.2 AA**, produit **non médical**, **SSR/no-JS**, tokens Auren
> Terminal existants (**0 nouvelle couleur**). 3 lots livrés + acceptés, chacun CI 3/3 verte.

## 1. Baseline Git
HEAD canonique = origin = `64a7435`, working tree clean. Aucun closeout Sx_UI_09 préexistant. Le cycle
(6 commits) est intact ; des merges Custom (persistence-05) sont posés dans l'historique sans chevaucher
les fichiers a11y.

## 2. Chaîne de preuves (6 commits vérifiés)
```
Sb_UI_09.1  build a2c753a → CI 29586630426 3/3 → review ef3b6a1
Sb_UI_09.2  build ac6cf20 → CI 29655710750 3/3 → review d80c8a5
Sb_UI_09.3  build 1281e85 → CI 29692113635 3/3 → review 64a7435
```
Tous présents (`git log -1 <sha>`). **3 CI vérifiées par SHA exact**, 3/3 chacune (pytest+QA / lint /
SonarCloud), premier coup pour les 3.

## 3. Matrice des sous-sprints

| Lot | Portée | Build | CI (SHA) | Human review | Verdict |
|---|---|---|---|---|---|
| `Sb_UI_09.1` Reduced-Motion Global | bloc `@media (prefers-reduced-motion: reduce)` universel dans `app.css` | `a2c753a` | `29586630426` ✅3/3 | `ef3b6a1` | ✅ ACCEPTED |
| `Sb_UI_09.2` Form-Errors ARIA | `role="alert"` sur 8 conteneurs / 7 templates + `aria-describedby` login/register | `ac6cf20` | `29655710750` ✅3/3 | `d80c8a5` | ✅ ACCEPTED |
| `Sb_UI_09.3` Contrast Guard | test de garde des ratios de contraste des tokens (déjà AA) | `1281e85` | `29692113635` ✅3/3 | `64a7435` | ✅ ACCEPTED |

## 4. Objectifs de la spec Sx_UI_09 — verdicts

| Objectif (spec, Option A) | Verdict | Lot / preuve |
|---|---|---|
| Reduced-motion **global** (transitions/animations décoratives) | **ACHIEVED** | `09.1` — bloc universel `*, ::before, ::after`, motion only |
| Form-errors **annoncées** (`role="alert"`/`aria-live`) | **ACHIEVED** | `09.2` — 8 conteneurs, rendu HTTP réel prouvé (401 → role=alert) |
| Champs↔message reliés (`aria-describedby`) | **ACHIEVED** | `09.2` — login/register, conditionnel `{% if error %}` |
| Pas d'`aria-invalid` faux (état par-champ inconnu) | **ACHIEVED WITH DOCUMENTED CHOICE** | `09.2` — 0 attribut (honnête ; backend ne dit pas le champ fautif) |
| Contraste tokens **verrouillé ≥ AA** | **ACHIEVED** | `09.3` — test de garde, ratios ≥ 4.5 (min `--fg-dim` 5.31), mutation prouve l'efficacité |
| **WCAG 2.2 AA** (pas AAA), **non médical** | **ACHIEVED** | 3 lots — 2.3.3/4.1.3/3.3.1/1.4.3 AA ; aucun contenu clinique |
| **SSR / no-JS** préservé | **NON-GOAL PRESERVED** | 3 lots — aucun JS ajouté ; annonces SSR au reload |
| Tokens Auren existants (**0 nouvelle couleur**) | **NON-GOAL PRESERVED** | 3 lots — aucun hex neuf ; le garde verrouille les tokens existants |
| Acquis a11y **non refaits** | **PRESERVED** | skip-link/aria-current/landmarks/tap ≥44px/SVG décoratifs préservés (hors scope) |
| Charts SVG / BodyMap / refonte auth | **NON-GOAL (deferred V2)** | non traités (surveillance), conformément à la spec §5 |
| CI verte + human review par lot | **ACHIEVED** | matrice §3 (3 CI 3/3 + 3 reviews) |

**Recadrage notable (documenté)** : l'audit `Sx_UI_12` supposait un **gap contraste** sur `--fg-dim`.
La mesure l'a **infirmé** (`--fg-dim` = 6.06:1 sur `--bg`, min 5.31 sur `--surface-2`, tous ≥ AA). L'axe
contraste est donc devenu un **test de garde** (`09.3`) et non une correction — décision honnête prise en
spec puis exécutée.

## 5. Non-goals préservés
Aucun AAA · aucun JavaScript · aucune nouvelle couleur/token d'identité · aucune correction `--fg-dim`
(déjà AA) · aucune refonte charts/BodyMap/auth standalone · aucun changement route/service/model/
migration/données/logique métier · non médical. Les 3 lots sont **template/CSS/test only**.

## 6. État a11y du produit (post-cycle)
- **Motion** : `prefers-reduced-motion` respecté globalement (transitions/animations décoratives → ~0).
- **Erreurs de formulaire** : annoncées (`role="alert"`) sur les 7 templates, reliées au formulaire
  (`aria-describedby`) sur login/register ; pas de faux `aria-invalid`.
- **Contraste** : tokens de texte verrouillés ≥ AA par test (régression future = CI rouge).
- **Acquis conservés** : skip-link, `aria-current` par région, `sr-only`, landmarks, tap ≥44px, SVG
  décoratifs `aria-hidden`, no-JS, `:focus-visible`.

## 7. Résidus / dettes différées (correctement séparés)
- **Charts SVG / BodyMap** : accessibilité fine différée (surveillance V2, non médical).
- **Pages auth standalone** : seuls les form-errors ont été traités (ciblé) ; passe a11y complète = V2.
- **`aria-invalid` par-champ** : nécessiterait un backend qui identifie le champ fautif (hors scope UI).
Ces éléments **ne sont pas** des omissions du cycle (non-goals V1 explicites, spec §5).

## 8. Risques acceptés (mineurs)
- Inspection lecteur d'écran réel (VoiceOver/NVDA) = **action opérateur** (pas d'environnement d'AT ici) ;
  rendu HTTP réel du `role="alert"` prouvé programmatiquement (login 401).
- Le bloc reduced-motion universel `*` avec `!important` : couvre aussi les blocs scopés existants
  (idempotent, vérifié ; pas de conflit).

## 9. Architecture préservée
FastAPI SSR + Jinja2, no-JS/no-SPA/no-React, PWA progressive, Auren Terminal (graphite/mono/ambre
`#C8A24B`, 0 nouvelle couleur). Aucun contrat POST/route/service/model touché.

---

## Verdict

**Verdict :** ✅ **Sx_UI_09 — CLOSED / HUMAN REVIEW COMPLETE.** Le cycle Accessibility & Motion est
**intégralement livré et accepté** : ses **3 lots** (`09.1` reduced-motion global · `09.2` form-errors
ARIA · `09.3` contrast guard) sont **human-review accepted**, chacun avec **CI 3/3 verte** (SHA exacts,
premier coup). Socle **WCAG 2.2 AA** atteint sur les axes réels : `prefers-reduced-motion` respecté
globalement (motion only, 0 perte d'info) · erreurs de formulaire annoncées (`role="alert"` + rendu HTTP
réel prouvé, pas de faux `aria-invalid`) · contraste des tokens **verrouillé par test** (déjà AA — l'axe
était un garde, pas une correction, l'hypothèse contraste de `Sx_UI_12` étant infirmée). **Non-goals
préservés** : pas d'AAA, pas de JS, 0 nouvelle couleur, pas de refonte charts/BodyMap/auth, non médical.
Acquis a11y (skip-link/aria-current/landmarks/tap/no-JS) **préservés, non refaits**. **Ferme la dette a11y
transverse de la queue `Sx_UI_12`.** Aucun fichier applicatif touché par le closeout (docs-only).

**Prochaine piste** (non commencée) : queue résiduelle `Sx_UI_12` — il reste **`Sb_UI_11.3` Final Auren
Baseline** (capture visuelle de référence post-Auren/post-shell) puis le **`Sx_UI` Global Final Closeout**.
Conditionnels non démontrés : `05R`/`06.4`/`08.3`. Gate externe : nom/domaine Auren =
`BLOCKED FOR PROFESSIONAL CLEARANCE`.
