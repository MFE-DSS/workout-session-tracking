# Human Review — Sb_UI_03.1 — Mobile Bottom Navigation

**Verdict** : ✅ **HUMAN REVIEW: ACCEPTED**
**Type** : HUMAN REVIEW — docs-only (aucun code/CSS/template/test touché)
**Date** : 2026-07-16
**Baseline canonique** : `fd875fa` (merge PR #22 Custom, posé **au-dessus** du build)
**Worktree** : `work/sb-ui-03-1-human-review` (isolé sur `fd875fa`)

> Distinction d'état : **CODE COMPLETE** `5a35ba8` + fix `4cd512a` · **CI GREEN** run `29484014891` 3/3 ·
> **HUMAN REVIEW ACCEPTED** = le présent commit `docs(review)` séparé.

## 1. Baseline Git
HEAD canonique = origin = `fd875fa`, working tree clean. Local FF depuis `4cd512a` → `fd875fa`
(fast-forward pur, aucun rebase/reset). Aucune revue 03.1 préexistante.

## 2. Preuve d'ascendance `4cd512a`
`git merge-base --is-ancestor 4cd512a HEAD` → **exit 0** ; `merge-base 4cd512a HEAD` = **`4cd512a`**.
Le build (build `5a35ba8` + fix `4cd512a`) est **intact dans l'historique canonique**.

## 3. Analyse du merge Custom (`4cd512a..fd875fa`)
`fd875fa` = **Merge PR #22 `Sb_CUSTOM_PROGRAM_LAUNCH_01 seed wipe-guard`**, initiative **indépendante**.
Changements = `app/services/seed.py`, `tests/test_seed_wipe_guard.py`, docs `*CUSTOM_PROGRAM*`, +
`SPEC_REGISTRY.md`/`ROADMAP_AND_NEXT_STEPS.md` (partagés). **Aucun fichier de shell.**

**Absence de drift shell (vérifiée)** — `git diff --quiet 4cd512a..HEAD` retourne **0 (UNCHANGED)** pour :
`app/templates/base.html`, `app/static/css/app.css`, `app/static/css/session_focus.css`,
`tests/test_app_shell_navigation.py`, `tests/test_session_focus_sticky_cta.py`,
`tests/test_session_management.py`, `docs/SPRINT_Sb_UI_03_1_..._REPORT.md`. → **pas de POST-BUILD SHELL
DRIFT**.

## 4. Commits audités
- **Build `5a35ba8`** `feat(ui): add Auren mobile bottom navigation` : `base.html` + `app.css` +
  `session_focus.css` + `test_app_shell_navigation.py` (neuf) + `test_active_navigation_semantics.py`
  (réorienté) + 3 docs. **Aucun** router/service/model/migration/data/manifest/icon/JS (vérifié
  `git diff --name-only 6322c22..5a35ba8`).
- **Fix `4cd512a`** `test(ui): reorient two shell-coupled tests…` : `test_session_focus_sticky_cta.py`
  + `test_session_management.py` + report. **Tests + docs uniquement, 0 code applicatif.**

## 5. Diff fonctionnel (`6322c22..5a35ba8`)
Périmètre = shell HTML + CSS shell + offset Focus Mode + tests shell/nav + docs. Confirmé **sans**
route/service/model/migration/data/auth/POST/reco/readiness/overload/substitution/BI/manifest/icon/JS.

## 6. Audit des tests réorientés — **TESTS REORIENTED — INTENT PRESERVED**
| Test | Ancienne assertion | Nouvelle vérité | Intention préservée ? |
|---|---|---|---|
| `test_single_aria_current_per_route` | 1 `aria-current=page` **global** | 1 **par région** (topbar ET bottom nav) | ✅ **plus strict** (2 régions vérifiées) |
| `test_css_contains_sticky_cta_block` | `position:sticky … bottom: 0` | `bottom: 0` **ou** `var(--app-bottom-nav-h)` | ✅ protège toujours sticky + sélecteur carte active + offset bas |
| `test_progress_shows_no_timeline_when_no_data` (+ pendant) | `"<svg" (not) in body` | `"timeline-chart" (not) in body` | ✅ **plus précis** (cible le graphe réel, pas les icônes) |
Aucune assertion supprimée ni rendue triviale. Rejet non déclenché.

## 7. Structure de la bottom nav (rendu HTTP réel)
`<nav class="app-bottom-nav" aria-label="Navigation principale">` — **exactement 4** `<a>` natifs :
Séance / Programmes / Progression / Profil. Label texte visible pour chacun ; SVG inline décoratifs
(`aria-hidden="true"` + `focusable="false"`). **Aucun** form / bouton d'action / CTA Démarrer /
Reprendre / logout. **Aucun JS.** (33 tests dédiés verts.)

## 8. Mapping actif (routes réelles)
| Onglet | href | Actif pour | Vérifié |
|---|---|---|---|
| Séance | `/` | `/`, `/sessions/{id}` | ✅ |
| Programmes | `/library` | `/library`, `/launcher` | ✅ |
| Progression | `/progress` | `/progress`, `/history`, `/physique`, `/body/intelligence`, `/coach-report` | ✅ |
| Profil | `/profile` | `/profile`, `/squads`, `/leaderboard` | ✅ |
**Exactement 1 actif par région**, jamais `aria-current="false"` (10 routes testées). Mapping dérivé
de `request.url.path` (pas l'URL complète → robuste aux query strings).

## 9. Navigation secondaire
Historique / Physique / Coach / Classement / Squads / **Déconnexion (POST)** restent dans le menu
topbar `<details>` (no-JS) ; Contact au footer. Marque Auren → Home. **Aucune route supprimée**, aucun
lien mort, logout **jamais** converti en GET. Topbar desktop utilisable.

## 10. Logout POST
`<form method="post" action="{{ url_for('logout') }}">` **inchangé** (test `test_logout_still_post` ✅).

## 11. Inspection mobile (360×640)
Inspection **programmatique** (pas de navigateur dans l'environnement — rendu pixel = **NOT OBSERVED**,
action opérateur en validation) : `position: fixed; bottom: 0; z-index: 40`, `min-height: 56px` /
`min-width: 44px` (tap ≥44), `env(safe-area-inset-bottom)`, `white-space: nowrap` (labels non tronqués),
`.foot` dégagé de 72px (pas de chevauchement), `.container` déjà 96px bottom. Accent actif **unique**
`var(--accent)` (ambre), **0 hex brut**, **aucune 2ᵉ couleur d'accent**. À confirmer visuellement par
l'opérateur : lisibilité, netteté SVG, confort tap, absence de barre « flottante ».

## 12. Inspection desktop (1440×900)
`@media (min-width: 769px)` → `.app-bottom-nav { display: none }` + `--app-bottom-nav-h: 0px` (token
neutralisé) + `.foot` rétabli à `+16px` (pas d'espace inférieur mobile résiduel). Topbar = fallback
fonctionnel. **Aucun rail desktop inventé** dans `.1`. → **DESKTOP FUNCTIONAL — RAIL DEFERRED TO
Sb_UI_03.2**.

## 13. Focus Mode
Sticky CTA : `bottom: var(--app-bottom-nav-h, 0px)` — décalé **au-dessus** de la bottom nav mobile,
= 0 en desktop (comportement inchangé). Token `--app-bottom-nav-h` = **contrat partagé** (défini
`:root`, consommé par le CTA), pas un nombre magique. `is_sess` inclut `/sessions/*` → **Séance actif**
en séance. Console/rest-timer/jump-bar/POST/no-JS **non touchés**. (133 tests focus/heads verts.)

## 14. Active banner
`.active-banner` **inchangé** : pointe vers la séance active, conserve « Reprendre → », no-JS. Positionné
sous la topbar dans le flux ; la bottom nav étant `fixed` en bas, **aucun chevauchement**. Non remplacée
par la bottom nav (intégration profonde différée à `03.3`). (`test_active_banner_preserved` ✅.)

## 15. CSS & accessibilité
Tap ≥44/56px · `env(safe-area-inset-bottom)` · `padding-bottom` contenu+footer · `z-index: 40`
raisonnable · masquage `@media ≥769px` · token hauteur = 0 desktop · accent via `var(--accent)` ·
**0 nouvel hex / gradient / ombre étrangère / webfont**. A11y : état actif = couleur **+ `aria-current`**
(pas couleur seule), labels visibles, `:focus-visible` (outline accent), SVG décoratifs, landmarks
(`<nav aria-label>`), ordre DOM logique. **Dette candidate (hors scope, NON traitée)** : reduced-motion
non ajouté ici (→ `Sx_UI_09`).

## 16. Tests locaux de revue
- Dédiés + réorientés (`app_shell_navigation` + `session_focus_sticky_cta` + `session_management` +
  `active_navigation_semantics`) : **81 passed**.
- Suites adjacentes (nav/topbar/mobile/pwa/auth/session_focus/active_banner/progress/history/profile/
  library/auren/shell/cockpit) : **738 passed, 0 failed** (294s).
- Garde-fous : ruff budget **543 ≤ 548** ✅ · spec_protocol ✅. Aucun test modifié durant la revue.

## 17. CI finale (run `29484014891`, SHA `4cd512a`)
| Job | Résultat |
|---|---|
| pytest + QA scripts | ✅ success (dont Alembic drift · schema snapshot · migration patterns · migration roundtrip · perf baseline — tous **success**) |
| lint (ruff budget + bandit + actionlint + shellcheck) | ✅ success |
| SonarCloud | ✅ success (code réellement analysé) |
Aucun job mandatory skipped, aucun timeout sur le run final.

## 18. Incidents CI historiques (non masqués)
- **Run initial `29481248620` ROUGE** (`pytest + QA`) : 2 tests asservis au shell (sticky CTA `bottom:0`
  littéral · `<svg` global sur `/progress`) cassés par des conséquences **légitimes** du build →
  réorientés (fix `4cd512a`, tests only). **Vrai échec de test**, pas infra.
- **Incident SonarCloud** : sur le run `29484014891`, SonarCloud a échoué **3× sur HTTP 504 Gateway
  Timeout** (`api.sonarcloud.io/analysis/jres` — provisioning JRE **upstream**, avant analyse). Panne
  **infra externe** (SonarCloud était `success` sur `9203e4c`/`bbfbe32`/`7bdf4ba`). Résolue par **re-run
  du seul job échoué** une fois l'API rétablie (HTTP 200) — **aucun commit de contournement**. Le run
  final a **réellement analysé le code** avec succès.

## 19. Non-régressions
Aucun backend / route / service / model / migration / data / manifest / icon / JS / contrat POST touché.
Topbar/nav secondaire/logout POST/active-banner/heads PWA/Focus Mode/no-JS **préservés**. Merge Custom
indépendant, sans chevauchement, historique intact.

## 20. Critères §20 — 20/20 satisfaits
(1) `4cd512a` ancêtre ✅ · (2) no shell drift ✅ · (3) 4 destinations ✅ · (4) liens corrects ✅ · (5) 1
actif/route ✅ · (6) pas de `aria-current=false` ✅ · (7) secondaires accessibles ✅ · (8) logout POST ✅ ·
(9) no-JS ✅ · (10) tap/safe-area ✅ · (11) pas de chevauchement mobile ✅ (prog.) · (12) desktop
fonctionnel ✅ · (13) Focus Mode utilisable ✅ · (14) sticky CTA accessible ✅ · (15) active banner ✅ ·
(16) palette Auren Terminal ✅ · (17) 0 backend/contrat ✅ · (18) intentions tests préservées ✅ · (19)
inspection mobile programmatique satisfaisante (pixel = opérateur) · (20) CI 3/3 ✅.

---

## Verdict

**Verdict :** ✅ **Sb_UI_03.1 — HUMAN REVIEW: ACCEPTED.** Bottom navigation mobile app-like conforme à
`Sx_UI_03` (1er lot) : **4 destinations** top-level (Séance/Programmes/Progression/Profil), SSR/no-JS,
liens natifs, SVG décoratifs, **1 actif par région** dérivé du path (jamais "false"), tokens Auren
existants (**0 nouvelle couleur**), tap ≥44px, safe-area iOS, masquée ≥769px (topbar = fallback ; **rail
desktop différé à `Sb_UI_03.2`**). Routes secondaires **toutes préservées** (menu topbar + Contact),
**logout POST** intact, active-banner intact, heads PWA intacts, Focus Mode offset via **token partagé**
(0 desktop). Aucun backend/route/service/model/migration/manifest/asset/JS/contrat. 3 tests réorientés
**sans affaiblissement** (2 plus stricts/précis). Merge Custom `fd875fa` **sans drift shell** (7 fichiers
byte-identiques). **CI 3/3 verte** sur `4cd512a` (incident SonarCloud 504 = infra upstream, résolu par
re-run sans commit ; run final a analysé le code). Inspection pixel mobile/desktop = action opérateur
(pas de navigateur en environnement) — inspection programmatique satisfaisante.

**Statut** : `Sb_UI_03.1` — **CODE COMPLETE · CI GREEN · HUMAN REVIEW ACCEPTED**. Conservés :
`Sb_UI_03.2` NOT OPENED · `Sb_UI_03.3` NOT OPENED · `Sx_UI_09` NOT OPENED · `Sb_UI_11.3` PENDING ·
`Sb_SESSION_UX_01.5` FIELD TEST READY / OPERATOR EVIDENCE PENDING.

**Prochaine action** (non commencée) : **`GO BUILD — Sb_UI_03.2 Desktop Rail / Secondary Shell`**.
