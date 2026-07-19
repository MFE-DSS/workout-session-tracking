# Sprint Sb_UI_09.3 — Contrast Guard — BUILD REPORT

**Statut** : 🟢 **CODE COMPLETE — CI PENDING — HUMAN REVIEW PENDING**
**Type** : build UI (**test only**) — 3ᵉ et dernier lot de `Sx_UI_09` Accessibility & Motion
**Date** : 2026-07-19
**Baseline** : `bf5998e` (revue 09.2 acceptée + merges Custom PR #27)
**Worktree** : `work/sb-ui-09-3-contrast-guard`

---

## 1. Baseline
Local FF vers HEAD réel `bf5998e` (merges Custom PR #27 hardening, **app.css/tokens non touchés**).
Working tree clean. Aucun build 09.3 préexistant.

## 2. Brainstorming (Options / Risques / Choix)
**Rappel spec** : `Sb_UI_09.3` = **test de garde**, PAS une correction — les tokens sont **déjà AA**
(mesuré en spec Sx_UI_09 : `--fg-dim` = 6.06:1 sur `--bg`). Objectif : **verrouiller** l'acquis contre
régression future.

| Option | Description | Verdict |
|---|---|---|
| **A** | Test qui **lit les tokens depuis app.css** (`:root`) + calcule les ratios WCAG + asserte ≥ AA | ✅ **RETENU** |
| B | Hard-coder les valeurs dans le test | ❌ fragile (désync si un token change) |
| C | Outil externe (axe/pa11y) | ❌ dépendance, hors no-JS/CI-safe |

**Choix : Option A** — le test **parse les vraies valeurs** de `app.css` (robuste : si un token change,
le test relit la vraie valeur et échoue s'il descend sous AA). Calcul WCAG en **pur stdlib** (luminance
relative), **aucune dépendance**, CI-safe.

## 3. Implémentation
`tests/test_contrast_guard.py` (**test only, 0 CSS modifié**) :
- `_tokens()` parse `--name: #hex;` depuis `app.css` (root wins).
- `_rel_luminance()` + `_ratio()` = formule WCAG 2.2 (stdlib).
- Seuils : **AA_NORMAL = 4.5** (texte normal), **AA_LARGE = 3.0** (large/UI).
- Paires vérifiées : `--fg`/`--fg-muted`/`--fg-dim` × `--bg`/`--surface`/`--surface-2` (AA normal) ;
  `--accent` × `--bg` (AA normal) ; `--on-accent` × `--accent` (texte sur bouton ambre, AA normal) ;
  `--accent` × surfaces (UI 3.0).

## 4. Ratios mesurés (transparence — tous ≥ AA)
| Token texte | sur `--bg` | sur `--surface` | sur `--surface-2` |
|---|---|---|---|
| `--fg` #E8ECEF | 15.69 | 14.71 | 13.75 |
| `--fg-muted` #A7B0BA | 8.49 | 7.96 | 7.44 |
| `--fg-dim` #8A94A0 | 6.06 | 5.68 | **5.31** (min) |
| `--accent` #C8A24B | 7.74 | 7.26 | 6.79 |
`--on-accent` #0A0C0F sur `--accent` : **8.14**. Le token le plus serré (`--fg-dim` / `--surface-2` =
**5.31**) reste **au-dessus** du seuil AA normal (4.5). Le garde est **effectif** (échouerait si un token
descendait sous 4.5).

## 5. Tests ajoutés
`test_contrast_guard.py` (**8 tests**) : tokens présents, `--fg*` ≥ AA sur les 3 fonds, `--fg-dim`
verrouillé explicitement, `--accent` ≥ AA sur `--bg` + ≥ UI sur surfaces, `--on-accent` ≥ AA sur
`--accent`, sanity du helper (black/white ≈ 21, identique = 1), no-CSS-change (tokens gardent leurs
valeurs auditées).

## 6. Tests réorientés
**Aucun** — build test-only, aucune modification de CSS/template.

## 7. Scope
`tests/test_contrast_guard.py` (neuf) · docs. **Aucun** CSS/template/route/service/model/migration/data/
manifest/asset/JS/contrat/couleur/Custom. **0 fichier applicatif touché** (le CSS reste identique).
check_scope = **ISOLATED** ; broad sweep ciblé exécuté.

## 8. Résultats locaux
- `test_contrast_guard.py` : **8 passed**.
- Broad sweep ciblé (contrast/reduced/motion/form_errors/a11y/css/auren/shell/pwa) : **379 passed, 0 failed** (81s).
- ruff clean ; budget **543 ≤ 548** ; spec PASS ; check_scope ISOLATED.

## 9. Accessibilité
WCAG 2.2 — 1.4.3 Contrast (Minimum, AA) : tous les tokens de texte sont **verrouillés ≥ 4.5:1** (texte
normal) sur les 3 fonds, l'accent ≥ 4.5:1 sur `--bg` et ≥ 3.0:1 (UI) sur les surfaces. Toute régression
future d'un token sous AA **fait échouer la CI**.

## 10. Cycle Sx_UI_09 après ce lot
Les **3 lots** sont livrés : `09.1` reduced-motion ✅ · `09.2` form-errors ARIA ✅ · `09.3` contrast guard
(ce lot). Reste : **`Sx_UI_09` closeout** (docs).

## 11. Statut
🟢 **CODE COMPLETE — CI PENDING — HUMAN REVIEW PENDING.**

---

## Verdict

**Verdict :** 🟢 **Sb_UI_09.3 CODE COMPLETE (CI + human review pending).** 3ᵉ et dernier lot de `Sx_UI_09` :
un **test de garde** verrouille le contraste WCAG 2.2 AA des tokens Auren Terminal. Le test **lit les
vraies valeurs** de `app.css` (robuste au changement), calcule les ratios en **pur stdlib** (0 dépendance,
CI-safe) et asserte ≥ 4.5:1 (texte) / ≥ 3.0:1 (UI). **Aucune correction CSS** — les tokens sont **déjà
AA** (hypothèse contraste de `Sx_UI_12` infirmée en spec : `--fg-dim` = 6.06:1 sur `--bg`, min 5.31 sur
`--surface-2`, tous ≥ AA). Le garde est effectif (échouerait sous 4.5). **Test only** : 0 fichier
applicatif touché, aucun CSS/template/route/service/model/migration/manifest/asset/JS/contrat/Custom. 8
tests dédiés, **0 réorienté**. ruff clean, budget 543 ≤ 548, check_scope ISOLATED.

**Prochaine étape** (séparée, non commencée) : `GO VALIDATE — Sb_UI_09.3 Contrast Guard` (puis, les 3 lots
acceptés, closeout `Sx_UI_09`).
