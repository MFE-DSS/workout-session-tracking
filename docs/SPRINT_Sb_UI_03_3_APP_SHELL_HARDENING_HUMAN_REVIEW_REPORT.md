# Human Review — Sb_UI_03.3 — App Shell Hardening

**Verdict** : ✅ **HUMAN REVIEW: ACCEPTED**
**Type** : HUMAN REVIEW — docs-only (aucun code/CSS/template/test touché)
**Date** : 2026-07-17
**Baseline canonique** : `0569178` (build 03.3 ; origin == build, aucun merge parallèle)
**Worktree** : `work/sb-ui-03-3-human-review` (isolé sur `0569178`)

> Distinction d'état : **CODE COMPLETE** `0569178` · **CI GREEN** run `29564964557` 3/3 (premier coup) ·
> **HUMAN REVIEW ACCEPTED** = le présent commit `docs(review)` séparé.
> `Sb_UI_03.3` est le **3ᵉ et dernier lot applicatif de `Sx_UI_03`** → cycle prêt pour son closeout.

## 1. Baseline Git
HEAD canonique = origin = `0569178`, working tree clean. Aucune revue 03.3 préexistante.

## 2. Commit build audité (`0569178`)
`feat(ui): harden Auren app shell navigation` : `base.html` + `app.css` + `test_app_shell_hardening.py`
(neuf) + `test_active_navigation_semantics.py` + `test_mobile_polish.py` + `test_app_shell_navigation.py`
+ `test_app_shell_desktop_rail.py` (réorientés) + 3 docs. **`index.html` byte-identique** (absent du diff).
**Aucun** router/service/model/migration/data/manifest/icon/JS/contrat POST/logique Home/Custom (vérifié
`git diff --name-only a3a32c9..0569178`).

## 3. Résidu 1 — Topbar rétrogradée en navigation secondaire
`<summary aria-label="Navigation secondaire">` + `<nav aria-label="Navigation secondaire">`. **Aucune
destination primaire** (Accueil/Programmes/Progression/Profil retirées — `test_topbar_has_no_primary_
destinations`). Conservés : Historique · Physique · Coach · Squads · Classement · **Contact** ·
Déconnexion **POST** (`test_topbar_keeps_secondary_routes` + `test_topbar_logout_is_post`). Lien
secondaire courant = `is-subactive`, **0 aria-current** dans la topbar (`test_topbar_no_aria_current` +
`test_topbar_secondary_active_uses_subactive`). `<details>` no-JS. **0 route supprimée** (les 4 primaires
vivent dans la bottom nav + le rail — vérifiés présents).

## 4. Résidu 2 — active-banner supprimée + indicateur nav
- **Markup retiré** (`test_no_active_banner_markup_in_template`) ; **CSS mort retiré** : 0 règle
  `.active-banner*`, `@keyframes pulse` orphelin supprimé (`test_no_active_banner_css`).
- **Home hero** = unique surface directe « Reprendre » : `index.html` **byte-identique**
  (`test_home_hero_untouched`) ; pas de CTA global de reprise sur page secondaire
  (`test_no_global_resume_cta_on_secondary_page`).
- **Indicateur nav** (bottom nav + rail) : `has-active-session` + `app-shell__session-dot` (point ambre
  **statique**, `test_session_dot_has_no_animation`) + `sr-only « En cours »`. **Présent** si session
  ouverte, **absent** sinon (`test_indicator_present/absent`). href Séance reste **`/`**
  (`test_seance_href_still_root_with_active_session`) — aucun lien conditionnel `/sessions/{id}`. Texte
  accessible **1× par région** (bottom nav + rail = 2). Non dépendant de la couleur seule (texte sr-only).
- **Limite héritée documentée** : le view `session_detail` ne passe pas `active_session` (routers hors
  scope) → indicateur absent sur `/sessions/{id}` ; comportement **identique** à l'ancienne bannière (qui
  y était déjà cachée) ; l'onglet Séance y reste **actif** (vérifié `test_no_active_banner_on_session_
  detail_page` : bottom nav active == ["Séance"]). **Non-régression.**

## 5. Résidu 3 — Skip link
`<a class="skip-link" href="#main-content">Aller au contenu principal</a>` = **premier élément
interactif** du `<body>` (`test_skip_link_is_first_interactive`), avant topbar/rail/bottom nav.
`<main id="main-content">` (`test_main_has_id`). CSS : `position: fixed`, hors écran au repos
(`translateY(-120%)`) → visible au `:focus`/`:focus-visible` (`translateY(--space-sm)` + outline accent),
`z-index: 100` (> rail 50), min-height 44px, tokens Auren (`--surface-2`/`--fg`/`--accent`), **0 hex neuf**
(`test_skip_link_no_new_hex`). Fonctionne clavier/no-JS/tous viewports. **Pas** ajouté aux pages auth
standalone (conforme §2.4).

## 6. Tests réorientés — intent preserved, non affaiblis
| Fichier | Réorientation | Preuve |
|---|---|---|
| `test_active_navigation_semantics` | `_active_labels` → bottom nav ; home→Séance, history/physique→Progression, leaderboard→Profil ; `single_aria_current` → topbar **0** + bottom nav **1** + rail **1** ; `all_nav_links` → `all_routes_reachable` (secondaires + 4 primaires) | plus strict (3 régions), 0 route perdue |
| `test_mobile_polish` | 5 tests banner → indicateur nav (banner **absente partout** + `has-active-session` si session) | assertions négatives **ajoutées** (plus strict) |
| `test_app_shell_navigation` + `test_app_shell_desktop_rail` | sentinelles `active_banner_preserved` → `active_session_indicator_replaces_banner` | banner absente + indicateur présent |
**Aucune assertion supprimée sans remplacement plus précis.** Diff audité : les `assert "active-banner"
in` deviennent `assert "active-banner" not in` **+ `assert "has-active-session" in`** — renforcement.

## 7. CSS & accessibilité
Skip-link (focus visible, tokens Auren, z-index 100) · sr-only (clip standard) · session-dot ambre
**statique** · `is-subactive` discret. **0 nouvel hex** (`test_skip_link_no_new_hex`). Breakpoints .1/.2
**inchangés** (`test_breakpoints_unchanged` : `@media (min-width: 1024px)` + `.app-rail { display: none }`).
Bottom nav (4) + rail (4) intacts. A11y : `<nav aria-label>`, skip link, indicateur non-couleur-seule,
`<details>` natif, logout POST.

## 8. Responsive & Focus Mode
`<1024px` : topbar secondaire + bottom nav + skip link. `≥1024px` : rail + skip link (topbar/bottom nav
masquées). Aucune active-banner à tout viewport. Focus Mode (720px, sticky CTA, F1/F2/F3, contrats POST)
**préservé** ; sur `/sessions/{id}` onglet Séance actif, skip link cible `#main-content`, aucune bannière.

## 9. Tests locaux de revue
- Dédiés : **`test_app_shell_hardening.py` 26 passed** (verbose vérifié critère par critère).
- Suites adjacentes (nav/topbar/mobile/session_focus/banner/home/progress/history/profile/squad/leaderboard/
  coach/physique/pwa/auth/shell/skip) : **1013 passed, 0 failed** (384s).
- Garde-fous : ruff budget **543 ≤ 548** ✅ · spec_protocol ✅. Aucun test modifié durant la revue.

## 10. CI finale (run `29564964557`, SHA `0569178`)
| Job | Résultat |
|---|---|
| pytest + QA scripts | ✅ success (dont Alembic drift · schema snapshot · migration patterns · migration roundtrip · perf baseline — tous **success**) |
| lint (ruff budget + bandit + actionlint + shellcheck) | ✅ success |
| SonarCloud | ✅ success |
**3/3 verte du premier coup** (aucun incident CI). Note : le full sweep **local** du build avait 4 échecs
`test_vscode_*` (présence `.vscode/*.json`) = **environnementaux** (`.vscode/` absent des worktrees git,
échouent aussi sur la baseline) — **la CI réelle (checkout complet) est verte**, ce qui confirme leur
nature non-régressive.

## 11. Non-régressions
Aucun backend/route/service/model/migration/data/manifest/icon/JS/contrat POST/logique Home touché.
`index.html` byte-identique. Bottom nav 03.1 + rail 03.2 + Focus Mode + heads PWA + no-JS **préservés**.
Breakpoints .1/.2 inchangés.

## 12. Dettes Sx_UI_09 (correctement différées, non traitées ici)
Audit reduced-motion global · aria-live des erreurs · aria-invalid/aria-describedby des formulaires ·
contraste transverse · accessibilité auth standalone · charts/BodyMap. Le skip link était le **seul**
élément a11y de `.3` (explicitement requis par Sx_UI_03). ✅ Périmètre respecté.

## 13. Critères d'acceptation — satisfaits
Topbar 0 primaire + secondaires + Contact + logout POST ✅ · is-subactive sans 2ᵉ aria-current ✅ · 0
route supprimée ✅ · active-banner + CSS mort + pulse retirés ✅ · Home hero byte-identique ✅ · indicateur
present/absent + href `/` + 1 texte/région + statique ✅ · session_detail non-régressif ✅ · skip link 1er
interactif + focus visible + 0 hex ✅ · breakpoints/bottom nav/rail intacts ✅ · tests réorientés intent
preserved (plus stricts) ✅ · 0 backend/contrat/Home/Custom ✅ · index.html intact ✅ · CI 3/3 ✅ · dettes
Sx_UI_09 différées ✅.

---

## Verdict

**Verdict :** ✅ **Sb_UI_03.3 — HUMAN REVIEW: ACCEPTED.** Les 3 résidus du shell sont fermés
proprement : (1) **topbar rétrogradée en navigation secondaire** (4 primaires retirés — vivent dans bottom
nav/rail ; secondaires + Contact + logout POST conservés ; `is-subactive` sans 2ᵉ `aria-current` ; 0 route
supprimée) ; (2) **active-banner supprimée** (markup + CSS mort + `@keyframes pulse` retirés) → Home hero
(`index.html` **byte-identique**) = unique surface « Reprendre », état actif porté par l'onglet Séance
(`has-active-session` + point ambre **statique** + `sr-only « En cours »`, href `/` inchangé, 1 texte/
région) ; (3) **skip link** `#main-content` (1er interactif, hors écran → visible au focus, tokens Auren,
0 hex neuf, pas sur auth standalone). Template + CSS only ; aucun backend/route/service/model/migration/
data/manifest/asset/JS/contrat/logique Home/Custom. 26 tests dédiés + réorientations **honnêtes et plus
strictes** (banner→indicateur, topbar 0 aria-current). Breakpoints .1/.2 + bottom nav (4) + rail (4) +
Focus Mode **intacts**. Limite héritée (`session_detail` sans indicateur) = non-régressive, documentée.
**CI 3/3 verte** sur `0569178` (premier coup). Inspection pixel = action opérateur. Dettes a11y
transverses correctement différées à **`Sx_UI_09`**.

**Statut** : `Sb_UI_03.3` — **CODE COMPLETE · CI GREEN · HUMAN REVIEW ACCEPTED**. **`Sx_UI_03` a désormais
ses 3 lots applicatifs livrés + acceptés** (`03.1` bottom nav · `03.2` rail desktop · `03.3` hardening)
→ prêt pour son **closeout**. Conservés : `Sx_UI_09` NOT OPENED · `Sb_UI_11.3` PENDING ·
`Sb_SESSION_UX_01.5` FIELD TEST READY / OPERATOR EVIDENCE PENDING.

**Prochaine action** (non commencée) : **`GO CLOSEOUT — Sx_UI_03 App Shell & Navigation`** (les 3 lots
étant acceptés), ou toute autre piste de la queue `Sx_UI_12`.
