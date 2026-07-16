# Sprint Sb_UI_03.1 — Mobile Bottom Navigation — BUILD REPORT

**Statut** : 🟢 **CODE COMPLETE — CI PENDING — HUMAN REVIEW PENDING**
**Type** : build UI (template + CSS) — premier lot de `Sx_UI_03` App Shell & Navigation
**Date** : 2026-07-16
**Baseline** : `6322c22` (Sx_UI_12 reconciliation, `Sx_UI RESIDUAL QUEUE: READY`)
**Worktree** : `work/sb-ui-03-1-mobile-shell`

---

## 1. Baseline
HEAD local = origin = `6322c22`, branche canonique, working tree clean, 0/0. Aucun build 03.1
préexistant (matches = références documentaires uniquement).

## 2. Constat shell initial
Shell = **topbar + menu hamburger `<details>` dense à 10 destinations top-level** (Accueil, Programmes,
Historique, Physique, Progression, Classement, Squads, Profil, Coach, Déconnexion) + Contact au footer.
**Aucune bottom navigation.** Active-session en `.active-banner` persistant. `aria-current` déjà géré
côté topbar (Sx_NAV_01, dérivé de `request.url.path`).

## 3. Brainstorming (§4 — 10 réponses)
1. **Topbar actuelle** : 10 destinations top-level (voir §2). 2. **Familles → 4 onglets** : Séance
(`/`,`/home*`,`/sessions/*`) · Programmes (`/library*`,`/launcher*`) · Progression (`/progress*`,
`/history*`,`/physique*`,`/body/intelligence*`,`/coach*`) · Profil (`/profile*`,`/squads*`,
`/leaderboard*`). 3. **Secondaires préservées** : restent dans le menu topbar `<details>` (aucune route
supprimée). 4. **Menu secondaire** = `<details>` natif existant, conservé. 5. **Structure** :
`<nav class="app-bottom-nav" aria-label="Navigation principale">` + 4 `<a>` natifs SSR. 6. **Offsets** :
`.foot` padding-bottom mobile + `env(safe-area-inset-bottom)` ; `.container` avait déjà 96px. 7. **Focus
Mode** : offset du sticky CTA via token partagé. 8. **SVG** : 4 glyphes inline 1-trait `currentColor`,
sobres. 9. **Tests asservis** : `test_active_navigation_semantics` (compte global → réorienté par
région), `test_mobile_polish`/`test_ux_navigation` (banner = invariant), `test_session_focus_*` (sticky
CTA/timer = invariant). 10. **Périmètre minimal** : bottom nav mobile seule ; topbar = fallback desktop ;
rail desktop **différé à 03.2** ; active-banner intact ; aucune rétrogradation destructive (→ 03.3).
**Conclusion : MOBILE SHELL ONLY · SSR/NO-JS · SECONDARY ROUTES PRESERVED · DESKTOP RAIL DEFERRED.**

## 4. Architecture retenue
Bottom nav `position: fixed; bottom: 0`, 4 items flex égaux, `var(--surface)` + `border-top
var(--border)`, `env(safe-area-inset-bottom)`. Icônes SVG inline décoratives (`aria-hidden`,
`focusable="false"`), label texte toujours visible. Onglet actif = classe `is-active` + `aria-current="page"`
dérivés de `request.url.path` (variables Jinja `is_sess`/`is_programs`/`is_prog`/`is_prof`, réutilisant
les `is_*` existantes). Accent actif = `var(--accent)` (#C8A24B **existant**). Masquée `@media (min-width:
769px)` (topbar = fallback desktop).

## 5. Mapping actif (§7)
| Onglet | href | Actif pour |
|---|---|---|
| Séance | `home` (`/`) | `/`, `/home*`, `/sessions/*` |
| Programmes | `library` | `/library*`, `/launcher*` |
| Progression | `progress` | `/progress*`, `/history*`, `/physique*`, `/body/intelligence*`, `/coach*` (couvre `/coach-report`) |
| Profil | `profile_page` | `/profile*`, `/squads*`, `/leaderboard*` |
**Exactement 1 actif par région** (topbar ET bottom nav) ; jamais `aria-current="false"`.

## 6. Navigation secondaire
Toutes les destinations restent accessibles via le menu topbar `<details>` (Historique/Physique/Coach/
Classement/Squads/Déconnexion) + Contact au footer. Logout **reste POST**. Aucune route supprimée.

## 7. Modifications HTML (`base.html`)
- Bloc de variables `is_sess`/`is_prog`/`is_prof` (mapping 4 onglets, dérivé path).
- `<nav class="app-bottom-nav">` avec 4 `<a>` + SVG inline, ajouté après `<footer>`.
- Topbar/menu/active-banner/heads **inchangés**.

## 8. Modifications CSS
- `app.css` : token `--app-bottom-nav-h: 56px` (`:root`) ; bloc `.app-bottom-nav*` (tokens existants
  only, tap ≥44/56px, safe-area, `:focus-visible`) ; offset `.foot` mobile ; `@media ≥769px` masque la
  nav + neutralise le token (`0px`) + rétablit `.foot`.
- `session_focus.css` : sticky CTA `bottom: 0` → `bottom: var(--app-bottom-nav-h, 0px)` (offset mobile,
  0 desktop) — **unique** modification, strictement nécessaire (§11).

## 9. Focus Mode
Audit `session_focus.css` : sticky CTA = `position: sticky; bottom: 0; z-index 100`. Sans offset, la
bottom nav fixed le recouvrirait/serait recouverte sur mobile. Correctif : offset `bottom` = hauteur nav
via token partagé `--app-bottom-nav-h` (0 en desktop). Sticky jump bar / rest timer / console **non
touchés**. Aucun service/partial métier modifié.

## 10. Tests ajoutés
`tests/test_app_shell_navigation.py` (**33 tests**) : structure (4 items, labels/liens exacts, icônes
décoratives, 0 form/bouton), active state (10 routes → bon onglet, 1 actif, jamais "false"), secondaire
(5 destinations + logout POST + menu no-JS), CSS (tap target, safe-area, masquage desktop, 0 hex neuf,
`var(--accent)`, focus-visible), Focus Mode offset token, non-régression (brand Auren, active-banner,
heads PWA, no-JS, path-derived).

## 11. Tests réorientés
`test_active_navigation_semantics.py::test_single_aria_current_per_route` : l'invariant « exactement 1
`aria-current=page` **global** » devient « exactement 1 **par région** » (topbar ET bottom nav) — le
shell a désormais 2 régions de navigation, chacune marquant son onglet actif (pattern a11y correct,
spec Sx_UI_03 « chaque destination annonce son état actif »). **Non affaibli** : le test vérifie
désormais les DEUX régions (plus strict). Helper `_region()` ajouté. Aucune assertion supprimée pour
faire passer le build.

## 12. Screenshots
Tooling Sx_UI_11 local (non committé, `.gitignore`). After-captures mobile 360×640 + desktop 1440×900 =
**à exécuter par l'opérateur** en validation (aucun PNG committé). Inspection humaine attendue : 4
destinations lisibles, nav calme, pas de chevauchement, contenu atteignable, usage une main, accent actif
visible non dominant, menu secondaire accessible.

## 13. Résultats locaux
- `test_app_shell_navigation.py` : **33 passed**.
- Nav asservis (`active_navigation_semantics` + `ux_navigation` + `mobile_polish` + shell) : **69 passed**.
- Focus/heads/auren (`session_focus_*` + `pwa_public_auth_heads` + `auren_pwa_assets` + `auren_visible`) :
  **133 passed**.
- Broad sweep ciblé (surfaces base.html/CSS, `-k nav/shell/mobile/topbar/base/foot/home/pwa/auth/layout/a11y`) : **586 passed, 0 failed** (191s).
- ruff clean ; budget **543 ≤ 548** ; spec_protocol PASS ; check_scope = **ISOLATED** (5 fichiers).

## 14. Scope
`app/templates/base.html` · `app/static/css/app.css` · `app/static/css/session_focus.css` ·
`tests/test_app_shell_navigation.py` (neuf) · `tests/test_active_navigation_semantics.py` (réorienté) ·
docs (report + registry + roadmap). **Aucun** router/service/model/migration/manifest/asset/icon/JS ;
aucun contrat POST ; 4 destinations only ; secondaires + logout POST + no-JS préservés ; desktop
fonctionnel (topbar fallback).

## 15. Risques
- Tests asservis d'autres suites pouvant compter `aria-current` globalement → couverts par le broad
  sweep + CI réelle (source de vérité non-régression).
- Offset Focus Mode : token partagé, neutralisé en desktop — comportement desktop inchangé.
- `session_focus.css` : avertissements `css:S4666` (sélecteurs dupliqués) **pré-existants**, non
  introduits, hors scope.

## 16. Éléments différés
Rail desktop → **`Sb_UI_03.2`**. Rétrogradation des entrées secondaires + intégration profonde
active-session → **`Sb_UI_03.3`**. Accessibilité/motion globale → **`Sx_UI_09`**. Baseline visuelle
finale → **`Sb_UI_11.3`**.

## 17. Statut
🟢 **CODE COMPLETE — CI PENDING — HUMAN REVIEW PENDING.**

---

## Verdict

**Verdict :** 🟢 **Sb_UI_03.1 CODE COMPLETE (CI + human review pending).** Bottom navigation mobile
app-like livrée : 4 destinations top-level (Séance/Programmes/Progression/Profil), SSR/no-JS, liens
natifs, SVG décoratifs, onglet actif dérivé du path (1 par région, jamais "false"), tokens Auren
existants (0 nouvelle couleur), tap ≥44px, safe-area iOS, masquée ≥769px (topbar = fallback desktop).
Routes secondaires **toutes préservées** (menu topbar + Contact footer), logout POST intact, active-banner
intact, heads PWA intacts, no-JS intact. Offset Focus Mode via token partagé (0 en desktop). 33 tests
dédiés + asservis verts ; 1 test réorienté (nouvelle vérité par région, non affaibli). Aucun
backend/route/service/model/migration/manifest/asset/JS. Rail desktop différé à **`Sb_UI_03.2`**.

**Prochaine étape** (séparée, non commencée) : `GO VALIDATE — Sb_UI_03.1 Mobile Bottom Navigation`.
