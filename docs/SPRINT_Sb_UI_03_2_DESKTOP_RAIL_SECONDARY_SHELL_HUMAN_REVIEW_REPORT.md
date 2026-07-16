# Human Review — Sb_UI_03.2 — Desktop Rail / Secondary Shell

**Verdict** : ✅ **HUMAN REVIEW: ACCEPTED**
**Type** : HUMAN REVIEW — docs-only (aucun code/CSS/template/test touché)
**Date** : 2026-07-16
**Baseline canonique** : `3eb8d99` (merges Custom PR #22/#23 posés au-dessus du build)
**Worktree** : `work/sb-ui-03-2-human-review` (isolé sur `3eb8d99`)

> Distinction d'état : **CODE COMPLETE** `f89f765` · **CI GREEN** run `29508124300` 3/3 (premier coup) ·
> **HUMAN REVIEW ACCEPTED** = le présent commit `docs(review)` séparé.

## 1. Baseline Git
HEAD canonique = origin = `3eb8d99`, working tree clean. Local FF `f89f765` → `3eb8d99` (fast-forward
pur). Aucune revue 03.2 préexistante.

## 2. Preuve d'ascendance `f89f765`
`git merge-base --is-ancestor f89f765 HEAD` → **exit 0** ; `merge-base f89f765 HEAD` = **`f89f765`**.
Le build rail est **intact dans l'historique canonique**.

## 3. Analyse des merges Custom (`f89f765..3eb8d99`)
2 commits **chantier Custom Program** : `14804a6 feat(custom-program): add user_programs root
persistence table` + `3eb8d99 Merge PR #23`. Fichiers = `app/models/user_program.py`,
`app/models/__init__.py`, `migrations/versions/…`, `data/schema_snapshot.sql`,
`tests/test_user_program_schema.py`, docs Custom + registry/roadmap. **Aucun fichier de shell.**

**Absence de drift shell (vérifiée)** — `git diff --quiet f89f765..HEAD` retourne **0 (UNCHANGED)** pour :
`base.html`, `app.css`, `session_focus.css`, `test_app_shell_desktop_rail.py`,
`test_app_shell_navigation.py`, `SPRINT_Sb_UI_03_2_..._REPORT.md`. → **pas de POST-BUILD SHELL DRIFT**.

## 4. Commit build audité (`f89f765`)
`feat(ui): add Auren desktop navigation rail` : `base.html` + `app.css` + `session_focus.css` +
`test_app_shell_desktop_rail.py` (neuf) + `test_app_shell_navigation.py` (réorienté) + 3 docs. **Aucun**
router/service/model/migration/data/manifest/icon/JS/Custom (vérifié `git diff --name-only 79d11fd..f89f765`).

## 5. Diff fonctionnel
Périmètre = rail HTML (`<aside class="app-rail">`) + CSS rail + réorientation breakpoint 769→1024 +
resserrement Focus Mode + tests. **0** route/service/model/migration/data/auth/POST/reco/readiness/
overload/substitution/BI/manifest/icon/JS.

## 6. Breakpoint retenu
**1024px unifié** (spec Sx_UI_03) : `<1024px` bottom nav visible / rail masqué (mobile + tablette
portrait) ; `≥1024px` rail visible / bottom nav masquée / topbar masquée. Le breakpoint bottom-nav de .1
est réorienté **769→1024** (un seul breakpoint de bascule, pas de contradiction). Vérifié : le test
`test_css_bottom_nav_hidden_at_1024_not_769` confirme l'absence du masquage à 769px.

## 7. Structure du rail (rendu HTTP réel)
`<aside class="app-rail" aria-label="Navigation latérale">` : `app-rail__brand` (Auren → home) ·
`<nav class="app-rail__primary" aria-label="Navigation principale (desktop)">` (**4** items) ·
`app-rail__spacer` · `<details class="app-rail__secondary"><summary>Plus</summary>` (5 sublinks) ·
`app-rail__footer` (Contact + logout POST). Icônes SVG `aria-hidden`/`focusable=false`, labels visibles,
**0 form/CTA** dans la nav primaire. (46 tests dédiés verts.)

## 8. Navigation primaire & parité mapping
4 destinations **même ordre/href/labels/icônes** que la bottom nav : Séance `/` · Programmes `/library`
· Progression `/progress` · Profil `/profile`. Actif dérivé des **variables partagées** `is_sess`/
`is_programs`/`is_prog`/`is_prof` (source unique, **0 recalcul** — `test_rail_derived_from_shared_mapping`).
**Parité rail↔bottom nav vérifiée** (`test_rail_and_bottom_nav_same_mapping`) : même destination active
pour une route donnée. 10 routes testées : 1 actif/région, jamais `aria-current="false"`.

## 9. Navigation secondaire
`<details>` « Plus » (no-JS) : Historique · Physique · Coach · Squads · Classement — visuellement plus
faibles (`--fg-dim`). Route secondaire active → `is-subactive` (visuel) **sans** 2ᵉ `aria-current`
(`test_rail_no_second_aria_current` : exactement 1 `aria-current` sur `/history`). Contact = lien normal.

## 10. Topbar desktop (Option A)
`≥1024px` : `.topbar { display: none }` (`test_css_topbar_hidden_on_desktop`). Le rail EST la navigation
(marque + nav + secondaires + logout). Jamais rail + hamburger + bottom nav simultanément.

## 11. Logout POST
`<form method="post">` + `<button class="app-rail__logout">` en pied de rail (`test_rail_logout_is_post`).
**Jamais** GET.

## 12. Mapping actif
Source unique (`request.url.path`), familles identiques à .1 (Progression couvre history/physique/
body-intelligence/coach-report ; Profil couvre squads/leaderboard). 1 actif par région.

## 13. Contenu / footer / active-banner
`≥1024px` : décalés `margin-left: var(--app-rail-w)` ; `.container max-width: calc(960px + rail)`
(`test_css_content_shifted_and_capped`). `<1024px` : aucun décalage (mobile intact).

## 14. Comportement responsive
- **Mobile (<1024)** : bottom nav visible, rail absent, mobile inchangé.
- **Tablette portrait (769–1023)** : bottom nav **conservée** (spec), rail absent.
- **Desktop (≥1024)** : rail visible, bottom nav + topbar masquées, contenu décalé+capé.
(Pixel = action opérateur — pas de navigateur en environnement ; inspection programmatique satisfaisante.)

## 15. Focus Mode
`≥1024px` : `.session-focus { max-width: 720px; margin-inline: auto }` (`test_css_focus_mode_tightened_
desktop`) — contenu resserré centré, rail à gauche (horizontal, hors calcul vertical du sticky CTA ;
`--app-bottom-nav-h` reste 0 desktop). Partials métier / contrat POST / ordre F1-F2-F3 **non touchés**.

## 16. Active banner
`.active-banner` **inchangée** ; sur desktop décalée `margin-left: var(--app-rail-w)` (ne couvre pas le
rail). « Reprendre → » conservé. Intégration profonde différée à `.3` (`test_active_banner_preserved`).

## 17. CSS & accessibilité
Rail `position: fixed`, `width: var(--app-rail-w)` (232px), `overflow-y: auto`, `z-index: 50`. A11y :
`<nav aria-label>`, labels visibles, icônes `aria-hidden`/`focusable=false`, `:focus-visible` (outline
accent) sur items/sublinks/logout, `<details>` natif, logout POST, **actif ≠ couleur seule**
(`border-left-color` + `font-weight`, `test_css_rail_active_not_color_only`), tap ≥44px, ordre DOM
logique, aucun `role=button`/`tabindex+`. **0 nouvel hex** (`test_css_rail_no_new_hex_color`), accent via
`var(--accent)`. **Skip link** = candidat `Sx_UI_09` (non ajouté, ne préempte pas). Dette reduced-motion
→ `Sx_UI_09`.

## 18. Tests réorientés
`test_app_shell_navigation.py::test_css_hidden_on_desktop` : breakpoint **769px → 1024px** (nouvelle
vérité spec). **Non affaibli** : exige toujours le masquage de la bottom nav à un breakpoint desktop,
désormais le bon (1024px). Aucune assertion supprimée.

## 19. Tests locaux de revue
- Dédiés rail + réorienté (`test_app_shell_desktop_rail` + `test_app_shell_navigation`) : **73 passed**.
- Suites adjacentes (nav/topbar/mobile/session_focus/sticky/banner/progress/history/profile/library/pwa/
  auth/auren/shell/cockpit/terminal) sur le HEAD de revue `3eb8d99` : **782 passed, 0 failed** (300s).
- Garde-fous : ruff budget **543 ≤ 548** ✅ · spec_protocol ✅. Aucun test modifié durant la revue.

## 20. CI finale (run `29508124300`, SHA `f89f765`)
| Job | Résultat |
|---|---|
| pytest + QA scripts | ✅ success (dont Alembic drift · schema snapshot · migration patterns · migration roundtrip · perf baseline — tous **success**) |
| lint (ruff budget + bandit + actionlint + shellcheck) | ✅ success |
| SonarCloud | ✅ success |
**3/3 verte du premier coup** (aucun incident CI cette fois). Aucun job mandatory skipped, aucun timeout.

## 21. Non-régressions
Aucun backend/route/service/model/migration/data/manifest/icon/JS/contrat POST touché. Bottom nav 03.1
**intacte** (`test_bottom_nav_still_present`), active-banner/heads PWA/no-JS/Focus Mode préservés. Merges
Custom indépendants, sans chevauchement, historique intact.

## 22. Critères d'acceptation — satisfaits
Ascendance ✅ · 0 drift shell ✅ · 4 destinations ✅ · parité mapping rail↔bottom nav ✅ · 1 actif/région
✅ · pas de 2ᵉ aria-current ✅ · secondaires préservées ✅ · logout POST ✅ · no-JS ✅ · tap/focus ✅ ·
breakpoint 1024 ✅ · topbar masquée desktop ✅ · Focus Mode resserré ✅ · sticky CTA inchangé ✅ ·
active-banner intacte ✅ · Auren Terminal (0 hex neuf, actif ≠ couleur seule) ✅ · 0 backend/contrat ✅ ·
tests réorientés intent preserved ✅ · CI 3/3 ✅ · 0 fichier Custom ✅.

---

## Verdict

**Verdict :** ✅ **Sb_UI_03.2 — HUMAN REVIEW: ACCEPTED.** Rail desktop latéral gauche conforme à
`Sx_UI_03` (2ᵉ lot) : **4 destinations** (même ordre/href/labels/icônes/mapping que la bottom nav, source
unique partagée), secondaires dans `<details>` « Plus » (5 routes), Contact + **logout POST** en pied.
**Breakpoint unifié 1024px** (bottom nav 769→1024, spec ; tablette portrait garde la bottom nav) ; topbar
masquée desktop (Option A) ; contenu décalé `margin-left: var(--app-rail-w)` + `max-width` 960px ; Focus
Mode resserré 720px. Tokens Auren existants (**0 nouvelle couleur**), actif ≠ couleur seule (bordure+poids),
tap ≥44px, `:focus-visible`. **1 actif par région**, jamais `aria-current="false"`, pas de 2ᵉ aria-current
sur route secondaire. Aucun backend/route/service/model/migration/manifest/asset/JS/contrat. Bottom nav
03.1 **intacte**. 1 test réorienté (769→1024) **sans affaiblissement**. Merges Custom `3eb8d99` **sans
drift shell** (6 fichiers byte-identiques). **CI 3/3 verte** sur `f89f765` (premier coup). Inspection pixel
= action opérateur.

**Statut** : `Sb_UI_03.2` — **CODE COMPLETE · CI GREEN · HUMAN REVIEW ACCEPTED**. Conservés :
`Sb_UI_03.3` NOT OPENED · `Sx_UI_09` NOT OPENED · `Sb_UI_11.3` PENDING · `Sb_SESSION_UX_01.5` FIELD TEST
READY / OPERATOR EVIDENCE PENDING.

**Prochaine action** (non commencée) : **`GO BUILD — Sb_UI_03.3 Shell Hardening`** (rétrogradation
destructive des entrées topbar + intégration profonde active-session + skip link a11y).
