# Sprint Sb_UI_03.3 — App Shell Hardening — BUILD REPORT

**Statut** : 🟢 **CODE COMPLETE — CI PENDING — HUMAN REVIEW PENDING**
**Type** : build UI (template + CSS) — **3ᵉ et dernier** lot applicatif de `Sx_UI_03`
**Date** : 2026-07-16
**Baseline** : `a3a32c9` (revue 03.2 acceptée)
**Worktree** : `work/sb-ui-03-3-shell-hardening`

---

## 1. Baseline
HEAD local = origin = `a3a32c9`, working tree clean, 0/0. Aucun build 03.3 préexistant.

## 2. Brainstorming (§5 — 15 réponses)
1. **Doublons topbar** : Accueil/Programmes/Progression/Profil (4 primaires) → retirés. 2. **Restent au
menu** : Historique/Physique/Coach/Squads/Classement/Contact/Déconnexion. 3. **Contact ajouté au menu**
(parité rail). 4. **Une seule logique `is_*`** (réutilisée). 5. **Secondaires = `is-subactive`** (pas
`aria-current`). 6. Primaire correspondant porte l'`aria-current`. 7. **`active_session` pas universel**
(passé par 8 routers ; l'indicateur suit **exactement** la disponibilité de l'ancienne bannière — identique,
non régressif). 8. **Home hero suffisant** (`index.html` a Reprendre + Démarrer une autre) → non touché.
9. **Indicateur** `has-active-session` + `app-shell__session-dot` sur l'item Séance (bottom nav + rail),
href reste `/`. 10. **Accessibilité** = `<span class="sr-only">En cours</span>` (une seule stratégie, pas
d'`aria-label` en plus pour éviter double annonce). 11. **CSS `.active-banner` mort** → supprimé. 12.
**Tests asservis** : banner + 10 entrées topbar → réorientés. 13. **Skip link** visible au focus, tokens
existants. 14. **Différé Sx_UI_09** : reduced-motion, aria-live erreurs, aria-invalid, contraste transverse,
auth standalone, charts/BodyMap. 15. **Périmètre minimal** = ces 3 résidus.
**Conclusion : SECONDARY TOPBAR ONLY · ACTIVE SESSION SIGNAL IN PRIMARY NAV · HOME HERO IS THE ONLY
RESUME SURFACE · SKIP LINK SHELL CONTRACT · SSR/NO-JS · NO BUSINESS LOGIC.**

## 3. État initial
Topbar `<details>` mobile/tablette portait **10 destinations** (dont les 4 primaires déjà dans la bottom
nav + le rail). Bannière globale `.active-banner` rendue au-dessus du contenu sur les pages passant
`active_session`. Aucun skip link.

## 4. Duplication topbar observée
Accueil (`/`), Programmes (`/library`), Progression (`/progress`), Profil (`/profile`) — **dupliquaient**
les 4 destinations primaires de la bottom nav / rail.

## 5. Nouvelle navigation secondaire
Topbar `<summary aria-label="Navigation secondaire">` + `<nav aria-label="Navigation secondaire">` :
Historique · Physique · Coach · Squads · Classement · **Contact** · Déconnexion (POST). Lien secondaire
courant = `is-subactive` (jamais `aria-current`). `<details>` natif, no-JS. Masquée ≥1024px (rail).

## 6. Routes préservées
**Aucune route supprimée.** Les 4 primaires restent dans la bottom nav (<1024px) + le rail (≥1024px) ;
les secondaires dans le menu topbar + Contact. Rétrogradation = réduction de priorité, pas suppression.

## 7. Ancienne active-banner
`<a class="active-banner">` (dot pulsant + label + nom + CTA Reprendre) rendue globalement. CSS =
bloc principal (l.204-235) + override Auren Terminal (l.3093-3099) + décalage rail (03.2) + `@keyframes
pulse`. Classification : **CSS MORT** (aucune surface applicative ne l'utilise, vérifié `rg active-banner
app/templates` = 0).

## 8. Nouveau pattern session active
- **Home** : hero `index.html` inchangé (Reprendre + Démarrer une autre) = **unique surface directe**.
- **Autres pages** : plus de bannière ; état porté par l'onglet Séance.
- **Bottom nav + rail** : `{% if active_session %}` → classe `has-active-session` + `<span
  app-shell__session-dot aria-hidden>` (point ambre **statique**) + `<span class="sr-only">En cours</span>`.
  href Séance reste `/` (aucun lien conditionnel `/sessions/{id}`). Sans session : rien.
- **Limite héritée documentée** : `active_session` n'est pas passé par le view `session_detail` (routers
  hors scope) → l'indicateur n'apparaît pas sur `/sessions/{id}` (comportement **identique** à l'ancienne
  bannière qui y était déjà cachée) ; l'onglet Séance y reste **actif** (`is_sess`).

## 9. Suppression active-banner
Markup retiré de `base.html` ; CSS mort retiré (3 blocs `.active-banner*` + `@keyframes pulse` orphelin).
Références historiques des rapports **conservées**. Aucun CSS mort gardé pour éviter d'adapter des tests.

## 10. Home hero préservé
`index.html` **byte-identique** (vérifié `git diff --quiet`). Today Decision Model / open_session / CTA
Reprendre / Démarrer une autre séance **intacts**.

## 11. Indicateurs bottom nav / rail
`has-active-session` + `app-shell__session-dot` (6px, `var(--accent)`, **0 animation**) + `sr-only « En
cours »`. Texte accessible **1× par région** (bottom nav + rail = 2 au total). Non dépendant de la couleur
seule (texte sr-only).

## 12. Skip link
`<a class="skip-link" href="#main-content">Aller au contenu principal</a>` = **premier élément
interactif** du `<body>` (avant topbar/rail/bottom nav). `<main id="main-content">`. CSS : `position:
fixed`, hors écran au repos (`translateY(-120%)`), visible au `:focus`/`:focus-visible` (`translateY`),
`z-index: 100` (> rail 50), min-height 44px, tokens Auren (`--surface-2`/`--fg`/`--accent`), **0 hex neuf**.
Fonctionne clavier/no-JS/mobile/tablette/desktop/Focus Mode. **Pas** ajouté aux pages auth standalone.

## 13. CSS mort supprimé
3 blocs `.active-banner*` + `@keyframes pulse` (orphelin après suppression du dot). Nouveaux : `.skip-link`,
`.sr-only`, `.app-shell__session-dot`, `.topbar__link.is-subactive`.

## 14. Tests ajoutés
`tests/test_app_shell_hardening.py` (**26 tests**) : topbar secondaire (0 primaire, secondaires présents,
logout POST, 0 aria-current, is-subactive), session active (indicateur présent/absent, href `/`, 1 texte/
région, Home hero intact, pas de CTA global sur page secondaire, session_detail), skip link (1er interactif,
href/label, main#id, CSS focus, 0 hex), cleanup (0 `.active-banner` CSS, 0 `@keyframes pulse`, dot sans
animation, breakpoints .1/.2 inchangés), non-régression (4 bottom nav + 4 rail, heads PWA, no-JS, mapping
partagé).

## 15. Tests réorientés
- `test_active_navigation_semantics.py` : `_active_labels` cible désormais la **bottom nav** (topbar n'a
  plus d'`is-active`) ; tests home→Séance, history/physique→Progression, leaderboard→Profil ;
  `test_single_aria_current_per_route` → topbar **0** aria-current + bottom nav **1** + rail **1** (plus
  strict) ; `test_all_nav_links…` → `test_all_routes_reachable…` (secondaires + 4 primaires, 0 route perdue).
- `test_mobile_polish.py` : 5 tests banner → **indicateur nav** (banner absente partout, `has-active-session`
  présent si session ouverte).
- `test_app_shell_navigation.py` + `test_app_shell_desktop_rail.py` : sentinelles `test_active_banner_
  preserved` → `test_active_session_indicator_replaces_banner` (banner absente, indicateur présent).
**Aucune assertion supprimée sans remplacement plus précis.**

## 16. Captures
Tooling Sx_UI_11 local ; 360×640 / 768×1024 / 1024×768 / 1440×900 + états Home/Progress/Profile/session
avec & sans session = **action opérateur** (aucun PNG committé, pas de navigateur en environnement).

## 17. Scope
`app/templates/base.html` · `app/static/css/app.css` · `tests/test_app_shell_hardening.py` (neuf) ·
`tests/test_active_navigation_semantics.py` · `tests/test_mobile_polish.py` ·
`tests/test_app_shell_navigation.py` · `tests/test_app_shell_desktop_rail.py` (réorientés) · docs.
`index.html` **byte-identique**. **Aucun** router/service/model/migration/data/manifest/icon/JS/contrat
POST/logique Home/fichier Custom. **check_scope dit ISOLATED mais le mandat impose SHARED_CODE** (base.html
partagé, ~37 pages) → **full sweep local exécuté** (remontée d'un cran, prudence).

## 18. Résultats locaux
- `test_app_shell_hardening.py` : **26 passed**.
- Réorientés + asservis (`active_navigation_semantics` + `mobile_polish` + `shell_terminal` +
  `auren_visible` + `app_shell_navigation` + `app_shell_desktop_rail`) : **131 passed**.
- **Full sweep local** (SHARED_CODE, mandat §20) : **2304 passed, 4 failed** (742s). Les 4 échecs =
  `test_v1_acceptance.py::test_vscode_*` (présence de `.vscode/launch.json`/`settings.json`) —
  **pré-existants et environnementaux** (`.vscode/` absent du worktree git ; `test_vscode_settings_json_
  exists` échoue **aussi sur la baseline canonique** `a3a32c9`), **sans aucun lien avec le shell**. La CI
  réelle (checkout complet) reste la source de vérité.
- ruff clean ; budget **543 ≤ 548** ; spec PASS.

## 19. Dettes Sx_UI_09 (différées, non traitées ici)
Audit global reduced-motion · aria-live des erreurs · aria-invalid / aria-describedby des formulaires ·
audit contraste transverse · accessibilité des pages auth standalone · charts et BodyMap. Le **skip link**
est le seul élément a11y de `.3` (explicitement requis par Sx_UI_03).

## 20. Statut
🟢 **CODE COMPLETE — CI PENDING — HUMAN REVIEW PENDING.** `Sx_UI_03` **non** marqué fermé (revue humaine +
closeout à venir).

---

## Verdict

**Verdict :** 🟢 **Sb_UI_03.3 CODE COMPLETE (CI + human review pending).** Les 3 résidus du shell sont
fermés : (1) topbar **rétrogradée en navigation secondaire** (4 primaires retirés — vivent dans bottom
nav/rail ; secondaires + Contact + logout POST conservés ; `is-subactive`, jamais 2ᵉ `aria-current` ;
0 route supprimée) ; (2) **active-banner globale supprimée** (CSS mort + `@keyframes pulse` retirés) →
Home hero = unique surface Reprendre, état actif porté par l'onglet **Séance** (`has-active-session` +
point ambre statique + `sr-only « En cours »`, href `/` inchangé) ; (3) **skip link** `#main-content`
(1er interactif, hors écran → visible au focus, tokens Auren, 0 hex neuf). Template + CSS only ;
`index.html` **byte-identique** ; aucun backend/route/service/model/migration/data/manifest/asset/JS/
contrat/logique Home/Custom. 26 tests dédiés + réorientations honnêtes (non affaiblies, plusieurs plus
strictes). Breakpoints .1/.2 inchangés, bottom nav/rail intacts. Dettes a11y transverses **différées à
`Sx_UI_09`**.

**Prochaine étape** (séparée, non commencée) : `GO VALIDATE — Sb_UI_03.3 App Shell Hardening`.
