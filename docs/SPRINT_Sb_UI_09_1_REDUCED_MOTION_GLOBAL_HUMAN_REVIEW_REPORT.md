# Human Review — Sb_UI_09.1 — Reduced-Motion Global

**Verdict** : ✅ **HUMAN REVIEW: ACCEPTED**
**Type** : HUMAN REVIEW — docs-only (aucun code/CSS/test touché)
**Date** : 2026-07-17
**Baseline canonique** : `a1fe5a6` (merges Custom PR #25/#26 posés au-dessus du build)
**Worktree** : `work/sb-ui-09-1-review` (isolé sur `a1fe5a6`)

> Distinction d'état : **CODE COMPLETE** `a2c753a` · **CI GREEN** run `29586630426` 3/3 (premier coup) ·
> **HUMAN REVIEW ACCEPTED** = le présent commit `docs(review)` séparé. 1er lot de `Sx_UI_09`.

## 1. Baseline Git
HEAD canonique = origin = `a1fe5a6`, working tree clean. Local FF `a2c753a` → `a1fe5a6` (fast-forward
pur). Aucune revue 09.1 préexistante.

## 2. Ascendance & absence de drift
`git merge-base --is-ancestor a2c753a HEAD` → **exit 0** ; `merge-base` = **`a2c753a`**. Le build est
**intact dans l'historique**. **0 drift** — `git diff --quiet a2c753a..HEAD` = UNCHANGED pour
`app.css`, `test_reduced_motion.py`, `SPRINT_..._REPORT.md`.

## 3. Merges Custom (`a2c753a..a1fe5a6`)
3 commits **chantier Custom Program** : `63137f9` (draft CRUD service) + `d12acc7` (Merge PR #26) +
`a1fe5a6` (closeout PERSISTENCE_03/04). Fichiers = `app/services/user_program_drafts.py`,
`tests/test_user_program_drafts.py`, docs Custom + registry/roadmap. **Aucun** chevauchement avec
`app.css`/tests/docs 09.1 (vérifié). Indépendants, sans drift shell.

## 4. Commit build audité (`a2c753a`)
`feat(ui): add global reduced-motion support` : `app/static/css/app.css` (bloc additif) +
`tests/test_reduced_motion.py` (neuf) + 3 docs. **Périmètre CSS + test + docs uniquement** — aucun
router/service/model/migration/data/manifest/icon/JS/template/contrat/Custom (vérifié `git diff
--name-only 007c428..a2c753a`).

## 5. Purement additif (point de sûreté clé)
`git show a2c753a -- app/static/css/app.css` = **0 ligne supprimée** : le build **n'a modifié aucun
sélecteur existant**, il ajoute uniquement le bloc reduced-motion en fin de fichier. Risque de
régression sur le CSS existant = **nul par construction**.

## 6. Le bloc reduced-motion
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```
- **Pattern universel WCAG 2.2** (a11y-project / référence) : couvre `*`/`::before`/`::after`, **robuste
  aux transitions ajoutées ultérieurement** (pas d'énumération fragile).
- **Motion only** : neutralise durées d'animation/transition + scroll-behavior. **Aucun** `display:none`/
  `visibility:hidden`, aucun changement de contenu/ordre DOM/couleur/layout (`test_reduced_motion_no_
  display_or_layout_change`).
- **Cohérence** : les blocs scopés existants (`session_focus.css`, `body_intelligence.css`) sont
  **préservés** (`test_scoped_reduced_motion_blocks_preserved`) ; `transition-duration: 0.01ms` est
  idempotent avec leur `transition: none` (même effet, pas de conflit).
- **0 nouvelle couleur** (`test_no_new_hex_colour_in_reduced_motion`).

## 7. Justesse du périmètre (audit vs spec Sx_UI_09)
La spec `Sb_UI_09.1` demandait un bloc reduced-motion **global** neutralisant les transitions/animations
**décoratives**. Audité : le repo a **9 transitions décoratives** (opacity/color/bg/border/width) et
**0 animation active** (le seul `@keyframes pulse` a été retiré en 03.3) → aucune perte d'information
possible. Conforme à la spec (motion décoratif seulement).

## 8. Tests
`test_reduced_motion.py` (**9 tests, tous verts**) : présence bloc `@media`, sélecteur universel
(`*`/`::before`/`::after`), neutralisation transitions **et** animations, `!important` (≥3), bloc scopé
session_focus préservé, 0 hex neuf, pas de `display:none`/`visibility:hidden`, transitions de base
conservées (animent à pleine vitesse sans préférence), smoke rendu + CSS servi. **0 test réorienté**
(build purement additif → aucun test asservi cassé).

## 9. Tests locaux de revue
- Dédiés : **9 passed** (verbose vérifié).
- Suites adjacentes (reduced/motion/css/shell/nav/mobile/session_focus/home/pwa/auth/auren/a11y/
  body_intelligence/cockpit/sticky) : **811 passed, 0 failed** (434s).
- Garde-fous : ruff budget **543 ≤ 548** ✅ · spec_protocol ✅. Aucun test modifié durant la revue.

## 10. CI finale (run `29586630426`, SHA `a2c753a`)
| Job | Résultat |
|---|---|
| pytest + QA scripts | ✅ success (dont Alembic drift · schema snapshot · migration patterns · migration roundtrip · perf baseline — tous **success**) |
| lint (ruff budget + bandit + actionlint + shellcheck) | ✅ success |
| SonarCloud | ✅ success |
**3/3 verte du premier coup** (aucun incident CI).

## 11. Non-régressions
Aucun template/route/service/model/migration/data/manifest/icon/JS/contrat/couleur touché. Transitions
de base intactes hors préférence reduced-motion ; blocs scopés préservés ; no-JS ; contenu/ordre DOM/
layout inchangés. Merges Custom indépendants, sans chevauchement.

## 12. Critères d'acceptation — satisfaits
Ascendance ✅ · 0 drift ✅ · bloc `@media (prefers-reduced-motion: reduce)` présent ✅ · sélecteur
universel ✅ · neutralise transitions + animations ✅ · `!important` ✅ · motion only (0 display:none/
layout) ✅ · blocs scopés préservés ✅ · 0 nouvelle couleur ✅ · purement additif (0 sélecteur modifié) ✅ ·
CSS only, 0 backend/Custom ✅ · 9 tests dédiés verts, 0 réorienté ✅ · CI 3/3 ✅.

---

## Verdict

**Verdict :** ✅ **Sb_UI_09.1 — HUMAN REVIEW: ACCEPTED.** Le respect **global** de `prefers-reduced-motion`
est livré via un bloc universel (`*, *::before, *::after`) en fin d'`app.css`, neutralisant les
transitions/animations **décoratives** (pattern WCAG 2.2 de référence, robuste aux ajouts futurs).
**Purement additif** — 0 ligne supprimée, aucun sélecteur existant modifié → risque de régression nul par
construction. **Motion only** : aucune perte d'information, aucun `display:none`/changement de contenu/
ordre DOM/couleur/layout ; blocs scopés (`session_focus`/`body_intelligence`) préservés ; 0 nouvelle
couleur. Audit conforme à la spec (9 transitions décoratives, 0 animation active → aucune info perdue).
**CSS only** : aucun template/route/service/model/migration/manifest/asset/JS/contrat/Custom. 9 tests
dédiés verts, **0 réorienté**. **CI 3/3 verte** sur `a2c753a` (premier coup). Merges Custom `a1fe5a6`
sans drift. Inspection pixel = action opérateur.

**Statut** : `Sb_UI_09.1` — **CODE COMPLETE · CI GREEN · HUMAN REVIEW ACCEPTED**. Conservés :
`Sb_UI_09.2` (form-errors ARIA) NOT OPENED · `Sb_UI_09.3` (contrast guard) NOT OPENED · `Sx_UI_09`
closeout après les 3 lots.

**Prochaine action** (non commencée) : **`GO BUILD — Sb_UI_09.2 Form-Errors ARIA`** (login/register
`role=alert`/`aria-live`/`aria-invalid`, SSR-only).
