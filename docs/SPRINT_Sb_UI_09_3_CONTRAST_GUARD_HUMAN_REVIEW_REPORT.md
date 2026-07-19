# Human Review — Sb_UI_09.3 — Contrast Guard

**Verdict** : ✅ **HUMAN REVIEW: ACCEPTED**
**Type** : HUMAN REVIEW — docs-only (aucun code/test touché)
**Date** : 2026-07-19
**Baseline canonique** : `e88865c` (closeout Custom PERSISTENCE_05 posé au-dessus du build)
**Worktree** : `work/sb-ui-09-3-review` (isolé sur `e88865c`)

> Distinction d'état : **CODE COMPLETE** `1281e85` · **CI GREEN** run `29692113635` 3/3 (premier coup) ·
> **HUMAN REVIEW ACCEPTED** = le présent commit `docs(review)` séparé. **3ᵉ et dernier lot de `Sx_UI_09`.**

## 1. Baseline Git
HEAD canonique = origin = `e88865c`, working tree clean. Local FF `1281e85` → `e88865c`. Aucune revue
09.3 préexistante.

## 2. Ascendance & absence de drift
`git merge-base --is-ancestor 1281e85 HEAD` → **exit 0**. **0 drift** — `git diff --quiet 1281e85..HEAD`
= UNCHANGED pour `test_contrast_guard.py`, `SPRINT_..._REPORT.md`, **et `app.css`** (crucial : les tokens
que le garde vérifie sont exactement ceux du build).

## 3. Merges Custom (`1281e85..e88865c`)
1 commit **chantier Custom** : `e88865c` (docs-only closeout PERSISTENCE_05). Fichiers = docs Custom +
registry/roadmap. **Aucun** chevauchement avec le test/app.css 09.3. Indépendant.

## 4. Commit build audité (`1281e85`)
`test(ui): lock WCAG AA contrast of Auren tokens` : `tests/test_contrast_guard.py` (neuf) + 3 docs.
**Test only** — **0 fichier applicatif** (aucun CSS/template/route/service/model/migration/data/manifest/
asset/JS/contrat/couleur/Custom, vérifié `git diff --name-only bf5998e..1281e85`).

## 5. Le test de garde — conception
`test_contrast_guard.py` **lit les vraies valeurs** de `app.css :root` (`_tokens()` parse `--name: #hex`)
— pas de valeurs hard-codées → **robuste au changement** (si un token change, le test relit la vraie
valeur). Calcul WCAG 2.2 en **pur stdlib** (`_rel_luminance` + `_ratio`, formule officielle), **0
dépendance**, CI-safe. Seuils : AA_NORMAL = 4.5 (texte), AA_LARGE = 3.0 (UI).

## 6. Le garde est EFFECTIF (test de mutation — point clé)
Vérification indépendante que le test **asserte réellement** (n'est pas trivial) :
- Valeur réelle la plus serrée : `--fg-dim` / `--surface-2` = **5.31** (> seuil AA 4.5) → **passe**.
- **Mutation** : si `--fg-dim` était dégradé à `#6B7280` → ratio = **3.38 < 4.5** → **le garde
  ÉCHOUERAIT**. → le test protège **réellement** contre une régression de contraste. ✅
- Sanity du helper : black/white ≈ **21**, couleur identique = **1** (`test_ratio_helper_sane`).

## 7. Ratios mesurés (re-calculés indépendamment — tous ≥ AA)
| Token texte | sur `--bg` | sur `--surface` | sur `--surface-2` |
|---|---|---|---|
| `--fg` | 15.69 | 14.71 | 13.75 |
| `--fg-muted` | 8.49 | 7.96 | 7.44 |
| `--fg-dim` | 6.06 | 5.68 | **5.31** (min) |
| `--accent` | 7.74 | 7.26 | 6.79 |
`--on-accent` / `--accent` : **8.14**. Tous ≥ 4.5 (texte normal). **Aucune correction CSS n'était
nécessaire** — les tokens sont déjà AA (l'hypothèse contraste de `Sx_UI_12` est infirmée). Le lot
**verrouille** l'acquis, il ne le crée pas.

## 8. Tests
`test_contrast_guard.py` (**8 tests, tous verts**) : tokens présents, `--fg*` ≥ AA sur les 3 fonds,
`--fg-dim` verrouillé explicitement, `--accent` ≥ AA sur `--bg` + ≥ UI sur surfaces, `--on-accent` ≥ AA
sur `--accent`, sanity du helper, no-CSS-change (tokens gardent leurs valeurs auditées). **0 test
réorienté** (test-only, aucune modification de CSS/template).

## 9. Tests locaux de revue
- Dédiés : **8 passed** (verbose vérifié).
- Test de mutation : garde prouvé effectif (dégradation → échec).
- Suites adjacentes (contrast/reduced/motion/form_errors/a11y/css/auren/shell/pwa/nav) :
  **428 passed, 0 failed** (133s).
- Garde-fous : ruff budget **543 ≤ 548** ✅ · spec_protocol ✅. Aucun test modifié durant la revue.

## 10. CI finale (run `29692113635`, SHA `1281e85`)
| Job | Résultat |
|---|---|
| pytest + QA scripts | ✅ success (dont Alembic drift · schema snapshot · migration patterns · migration roundtrip · perf baseline — tous **success**) |
| lint (ruff budget + bandit + actionlint + shellcheck) | ✅ success |
| SonarCloud | ✅ success |
**3/3 verte du premier coup** (aucun incident CI).

## 11. Non-régressions
Aucun CSS/token modifié (`app.css` byte-identique) ; aucun template/route/service/model/migration/data/
manifest/asset/JS/contrat touché. Le garde ne change rien au rendu — il **protège** l'existant.

## 12. Accessibilité (WCAG)
1.4.3 Contrast (Minimum, AA) : tous les tokens de texte verrouillés ≥ 4.5:1 sur les 3 fonds, accent ≥
4.5:1 sur `--bg` et ≥ 3.0:1 (UI) sur les surfaces. Toute régression future d'un token sous AA fait
échouer la CI.

## 13. Critères d'acceptation — satisfaits
Ascendance ✅ · 0 drift (app.css inclus) ✅ · test lit les vraies valeurs ✅ · calcul WCAG stdlib correct
(sanity 21/1) ✅ · **garde effectif (mutation → échec)** ✅ · tous tokens ≥ AA re-vérifiés ✅ · aucune
correction CSS ✅ · test only, 0 fichier applicatif ✅ · 8 tests verts, 0 réorienté ✅ · CI 3/3 ✅.

---

## Verdict

**Verdict :** ✅ **Sb_UI_09.3 — HUMAN REVIEW: ACCEPTED.** Un **test de garde** verrouille le contraste WCAG
2.2 AA des tokens Auren Terminal. Le test **lit les vraies valeurs** de `app.css` (robuste), calcule les
ratios en **pur stdlib** (0 dépendance, CI-safe) et asserte ≥ 4.5:1 (texte) / ≥ 3.0:1 (UI). **Garde prouvé
effectif** par test de mutation : une dégradation de `--fg-dim` (5.31 → 3.38) le ferait échouer — ce n'est
pas un test trivial. **Aucune correction CSS** — les tokens sont **déjà AA** (`--fg-dim` min 5.31, accent
6.79–7.74, on-accent 8.14 ; hypothèse Sx_UI_12 infirmée) ; le lot verrouille l'acquis. **Test only** :
`app.css` byte-identique, 0 fichier applicatif touché. 8 tests dédiés verts, **0 réorienté**. **CI 3/3
verte** sur `1281e85` (premier coup). Merge Custom `e88865c` sans drift.

**Statut** : `Sb_UI_09.3` — **CODE COMPLETE · CI GREEN · HUMAN REVIEW ACCEPTED**.

**🎯 `Sx_UI_09` a désormais ses 3 lots livrés + acceptés** (`09.1` reduced-motion · `09.2` form-errors
ARIA · `09.3` contrast guard) → prêt pour son **closeout**.

**Prochaine action** (non commencée) : **`GO CLOSEOUT — Sx_UI_09 Accessibility & Motion`** (les 3 lots
étant acceptés), après quoi la queue `Sx_UI_12` ne comptera plus que `Sb_UI_11.3` Final Baseline + le
closeout global `Sx_UI`.
