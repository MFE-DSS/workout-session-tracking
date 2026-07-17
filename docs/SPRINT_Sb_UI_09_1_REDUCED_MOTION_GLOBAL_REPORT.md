# Sprint Sb_UI_09.1 — Reduced-Motion Global — BUILD REPORT

**Statut** : 🟢 **CODE COMPLETE — CI PENDING — HUMAN REVIEW PENDING**
**Type** : build UI (CSS only) — 1er lot de `Sx_UI_09` Accessibility & Motion
**Date** : 2026-07-17
**Baseline** : `79957f1` (spec Sx_UI_09 commitée)
**Worktree** : `work/sb-ui-09-1-reduced-motion`

---

## 1. Baseline
HEAD local = origin = `79957f1`, working tree clean. Aucun build 09.1 préexistant.

## 2. Brainstorming (Options / Risques / Choix)
**Inventaire audité** (`app.css`) : **9 transitions décoratives** (opacity/color/background/border/width/
r/filter, 0.15–0.3s), **0 `@keyframes`/`animation:` actif** (le seul `pulse` a été retiré en 03.3),
**0 bloc reduced-motion**. Modèle existant : `session_focus.css:360` (`@media (prefers-reduced-motion:
reduce) { … transition: none }`).

| Option | Description | Verdict |
|---|---|---|
| **A** | Bloc **universel** `*, *::before, *::after` neutralisant transitions/animations décoratives | ✅ **RETENU** |
| B | Énumérer les 9 sélecteurs | ❌ fragile (nouvelle transition = gap), verbeux |
| C | Ne rien faire | ❌ gap persiste |

**Choix : Option A** — pattern WCAG 2.2 de référence (a11y-project), **robuste aux transitions futures**,
0 perte d'info (les transitions ne portent que du décoratif). **Risque écarté** : le `*` universel
recouvre aussi les transitions scopées `.session-focus` — mais `transition-duration: 0.01ms` est
idempotent avec leur `transition: none` (même effet, pas de conflit) ; `!important` garantit la priorité.

## 3. Implémentation
Bloc ajouté en **fin d'`app.css`** :
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
**Motion only** : neutralise durées d'animation/transition + scroll-behavior. **Aucun** `display:none`/
`visibility:hidden` (pas de perte de contenu), aucun changement d'ordre DOM/couleur/layout. Additif :
aucun sélecteur existant modifié ; blocs scopés (`session_focus`/`body_intelligence`) préservés.

## 4. Tests ajoutés
`tests/test_reduced_motion.py` (**9 tests**) : présence du bloc `@media (prefers-reduced-motion: reduce)`,
sélecteur universel (`*`/`::before`/`::after`), neutralisation transitions **et** animations, `!important`,
bloc scopé session_focus préservé, **0 hex neuf**, pas de `display:none`/`visibility:hidden`, transitions
de base conservées (animent à pleine vitesse sans préférence reduced-motion), smoke rendu + CSS servi.

## 5. Tests réorientés
**Aucun** — le build est purement **additif** (nouveau bloc en fin de fichier). Aucun test asservi cassé.

## 6. Scope
`app/static/css/app.css` (bloc reduced-motion additif) · `tests/test_reduced_motion.py` (neuf) · docs.
**Aucun** template/route/service/model/migration/data/manifest/icon/JS/contrat/couleur/Custom.
check_scope = **ISOLATED** (additif, aucun sélecteur existant modifié) ; broad sweep ciblé exécuté.

## 7. Résultats locaux
- `test_reduced_motion.py` : **9 passed**.
- Broad sweep ciblé (css/shell/nav/mobile/session_focus/home/pwa/auth/auren/a11y/body_intelligence) :
  **808 passed, 0 failed** (390s).
- ruff clean ; budget **543 ≤ 548** ; spec PASS ; check_scope ISOLATED.

## 8. Accessibilité
Respect global de `prefers-reduced-motion` (WCAG 2.2 — Success Criterion 2.3.3 Animation from
Interactions, niveau AAA mais bonne pratique AA). Cohérent avec les blocs scopés existants. **Motion
only** : aucune information supprimée quand la préférence est active.

## 9. Non-régressions
Aucun contenu/ordre DOM/couleur/layout modifié ; transitions de base intactes sans préférence
reduced-motion ; blocs scopés préservés ; no-JS ; aucun backend.

## 10. Dettes Sx_UI_09 restantes (lots suivants)
`Sb_UI_09.2` Form-Errors ARIA (login/register `role=alert`/`aria-live`/`aria-invalid`, SSR-only) ·
`Sb_UI_09.3` Contrast Guard (test de garde ratios tokens) · `Sx_UI_09` closeout.

## 11. Statut
🟢 **CODE COMPLETE — CI PENDING — HUMAN REVIEW PENDING.**

---

## Verdict

**Verdict :** 🟢 **Sb_UI_09.1 CODE COMPLETE (CI + human review pending).** Premier lot de `Sx_UI_09` :
respect **global** de `prefers-reduced-motion` via un bloc universel (`*, *::before, *::after`) en fin
d'`app.css`, neutralisant les transitions/animations **décoratives** (WCAG 2.2, pattern de référence,
robuste aux ajouts futurs). **Motion only** — aucune perte d'information, aucun changement de contenu/
ordre DOM/couleur/layout ; blocs scopés (`session_focus`/`body_intelligence`) préservés. **CSS only** :
aucun template/route/service/model/migration/manifest/asset/JS/contrat/Custom. 9 tests dédiés, **0 test
réorienté** (build additif). ruff clean, budget 543 ≤ 548, check_scope ISOLATED.

**Prochaine étape** (séparée, non commencée) : `GO VALIDATE — Sb_UI_09.1 Reduced-Motion Global`.
