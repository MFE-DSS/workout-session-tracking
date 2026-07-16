# Sprint Sb_UI_03.2 — Desktop Rail / Secondary Shell — BUILD REPORT

**Statut** : 🟢 **CODE COMPLETE — CI PENDING — HUMAN REVIEW PENDING**
**Type** : build UI (template + CSS) — 2ᵉ lot de `Sx_UI_03` App Shell & Navigation
**Date** : 2026-07-16
**Baseline** : `79d11fd` (merge Custom docs-only posé au-dessus de la revue 03.1 `ea151b6`)
**Worktree** : `work/sb-ui-03-2-desktop-rail`

---

## 1. Baseline
Local `ea151b6` → origin `79d11fd` (commit Custom **docs-only** `docs(closeout): record LAUNCH_01…`,
sans chevauchement shell — `ea151b6` ancêtre) → FF local → worktree sur `79d11fd`. Aucun build 03.2
préexistant. Working tree clean.

## 2. Brainstorming (§4 — 15 réponses)
1. **Réutilisé de .1** : mapping Jinja `is_sess/is_programs/is_prog/is_prof` (**source unique**),
   famille d'icônes SVG, tokens Auren. 2. **Rail ≥1024px** (spec Sx_UI_03 l.284). 3. **769–1023px**
   (tablette portrait) : bottom nav **visible**, rail absent → breakpoint bottom-nav déplacé 769→1024.
   4. **Pas de divergence mapping** : rail réutilise les mêmes `is_*` (approche A, duplication contrôlée).
   5. **Rail fixe** (`position: fixed`, largeur token). 6. **`--app-rail-w: 232px`**, labels non tronqués.
   7. Contenu/footer/banner décalés `margin-left: var(--app-rail-w)`, `max-width` contenu 960px. 8. **Focus
   Mode desktop** : contenu resserré ~720px centré, rail à côté (hors calcul vertical sticky CTA). 9.
   **Secondaires** : `<details>` « Plus » en pied de rail, visuellement plus faible. 10. `<details>` natif
   (no-JS). 11. **Contact + logout POST** dans `app-rail__footer`. 12. **Tests asservis 769px** :
   `test_css_hidden_on_desktop` → réorienté 1024px. 13. **Pas de macro** (4 liens simples ; abstraction
   disproportionnée). 14. **Différé à .3** : rétrogradation destructive topbar, intégration active-session,
   skip link (→ Sx_UI_09). 15. **0 métier** : template+CSS only.
   **Conclusion : DESKTOP RAIL ONLY · SAME FOUR PRIMARY DESTINATIONS · SECONDARY ROUTES PRESERVED ·
   SSR/NO-JS · SESSION-ACTIVE HARDENING DEFERRED TO Sb_UI_03.3.**

## 3. État desktop initial
Avant : la bottom nav 03.1 était masquée dès **769px**, laissant la **topbar hamburger** comme unique
shell desktop (10 destinations). Aucun rail. Le breakpoint 769px était une **vérité temporaire** de .1.

## 4. Stratégie de breakpoint
**Un seul breakpoint de bascule : 1024px** (spec). `<1024px` : bottom nav visible, rail masqué, topbar
disponible (mobile + tablette portrait). `≥1024px` : rail visible, bottom nav masquée, **topbar masquée**
(Option A). Le breakpoint bottom-nav de .1 est **réorienté 769→1024** (pas de breakpoints contradictoires).

## 5. Structure du rail livré
`<aside class="app-rail" aria-label="Navigation latérale">` : marque Auren → `app-rail__brand` ·
`<nav class="app-rail__primary" aria-label="Navigation principale (desktop)">` (4 destinations) ·
`app-rail__spacer` · `<details class="app-rail__secondary"><summary>Plus</summary>` (5 sublinks) ·
`app-rail__footer` (Contact + logout POST). Rail `position: fixed` gauche, `width: var(--app-rail-w)`.

## 6. Navigation primaire
4 destinations, **même ordre / href / labels / icônes** que la bottom nav : Séance `/` · Programmes
`/library` · Progression `/progress` · Profil `/profile`. Actif = **même mapping** (`is_sess`/`is_programs`/
`is_prog`/`is_prof`), 1 actif, jamais `aria-current="false"`. État actif = accent ambre **+ bordure
gauche + poids** (pas couleur seule).

## 7. Navigation secondaire
`<details>` « Plus » (no-JS) : Historique · Physique · Coach · Squads · Classement — visuellement plus
faibles (`--fg-dim`, 13px). Route secondaire active → `is-subactive` (visuel), **jamais** un 2ᵉ
`aria-current="page"` (le primaire correspondant le porte). Contact = lien normal, Déconnexion = form POST.

## 8. Gestion topbar (Option A)
`≥1024px` : `.topbar { display: none }`. Le rail EST la navigation (marque + nav + secondaires + logout).
`base.html` n'a pas de titre de page dynamique dans la topbar → rien d'utile perdu. Jamais rail + hamburger
+ bottom nav simultanément.

## 9. Mapping actif
Dérivé de `request.url.path` via les variables partagées (source unique, pas de recalcul). Familles :
Séance=`/`+`/sessions/*` ; Programmes=`/library`+`/launcher` ; Progression=`/progress`+`/history`+
`/physique`+`/body/intelligence`+`/coach*` ; Profil=`/profile`+`/squads`+`/leaderboard`. **1 actif par
région** (bottom nav OU rail, un seul visible par breakpoint) — testé identique entre les deux.

## 10. Layout contenu / footer
`≥1024px` : `.container` / `.foot` / `.active-banner` décalés `margin-left: var(--app-rail-w)` ;
`.container max-width: calc(960px + rail)`. `<1024px` : aucun décalage (mobile intact). Rail `overflow-y:
auto` (scroll interne si besoin), footer atteignable.

## 11. Focus Mode
`≥1024px` : `.session-focus { max-width: 720px; margin-inline: auto }` — contenu resserré centré, rail à
gauche. Sticky CTA `bottom: var(--app-bottom-nav-h, 0px)` = **0 en desktop** (inchangé) ; le rail est
horizontal → n'entre pas dans le calcul vertical. Partials métier / contrat POST / ordre F1-F2-F3 **non
touchés**.

## 12. Active banner
`.active-banner` **inchangée** fonctionnellement ; sur desktop décalée `margin-left: var(--app-rail-w)`
(alignée au contenu, ne couvre pas le rail). Lien « Reprendre → » conservé. Intégration profonde différée
à `.3`.

## 13. Accessibilité
`<nav aria-label>` (2 régions), labels visibles, icônes `aria-hidden`/`focusable=false`, `:focus-visible`
(outline accent) sur items/sublinks/logout, `<details>` natif, logout **POST**, actif ≠ couleur seule
(bordure+poids), ordre DOM logique, aucun `role="button"`/`tabindex+`. **Skip link** = candidat `Sx_UI_09`
(non ajouté ici, ne préempte pas). Dette reduced-motion transverse → `Sx_UI_09`.

## 14. Tests ajoutés
`tests/test_app_shell_desktop_rail.py` (**46 tests**) : structure (4 items, ordre/labels/href, icônes
décoratives, 0 form/CTA primaire), mapping (10 routes, 1 actif, jamais "false", **parité rail↔bottom
nav**), secondaire (5 routes + Contact + logout POST + `<details>` + pas de 2ᵉ aria-current), CSS (rail
masqué <1024 / visible ≥1024, bottom-nav masquée à 1024 **pas** 769, tokens largeur/max-width, topbar
masquée desktop, Focus 720px, 0 hex neuf, actif ≠ couleur seule, focus-visible, tap 44px), non-régression
(bottom nav présente, active-banner, heads PWA, no-JS, mapping partagé).

## 15. Tests réorientés
`test_app_shell_navigation.py::test_css_hidden_on_desktop` : breakpoint **769px → 1024px** (nouvelle
vérité spec ; le rail prend le relais à 1024px, bottom nav reste en tablette portrait). Regex ajusté,
**non affaibli** (exige toujours le masquage à un breakpoint desktop, désormais le bon).

## 16. Captures
Tooling Sx_UI_11 local (non committé). After-captures **360×640 / 768×1024 / 1024×768 / 1440×900** =
**action opérateur** (aucun PNG committé, pas de navigateur en environnement).

## 17. Résultats locaux
- `test_app_shell_desktop_rail.py` + `test_app_shell_navigation.py` : **73 passed**.
- Broad sweep ciblé (nav/topbar/mobile/session_focus/sticky/banner/progress/history/profile/library/pwa/
  auth/auren/shell/cockpit/terminal/layout) : **795 passed, 0 failed** (294s).
- ruff clean ; budget **543 ≤ 548** ; spec PASS ; check_scope **ISOLATED**.

## 18. Scope
`app/templates/base.html` · `app/static/css/app.css` · `app/static/css/session_focus.css` ·
`tests/test_app_shell_desktop_rail.py` (neuf) · `tests/test_app_shell_navigation.py` (réorienté) · docs.
**Aucun** router/service/model/migration/data/manifest/icon/JS/contrat POST/fichier Custom.

## 19. Risques
- Tests d'autres suites comptant `aria-current` globalement ou asservis au 769px → couverts par broad
  sweep + CI réelle.
- Avertissements CSS pré-existants (`css:S4666`/`S7924`/`emptyRules`) hors scope, non introduits.
- Décalage `margin-left` : scopé `≥1024px` uniquement (mobile intact).

## 20. Éléments différés à `.3` (Shell Hardening)
Rétrogradation **destructive** des 10 entrées topbar (rétablissement sémantique sous Progression/Profil),
intégration profonde active-session (dot dans nav vs banner), skip link a11y (→ `Sx_UI_09`).

## 21. Statut
🟢 **CODE COMPLETE — CI PENDING — HUMAN REVIEW PENDING.**

---

## Verdict

**Verdict :** 🟢 **Sb_UI_03.2 CODE COMPLETE (CI + human review pending).** Rail desktop latéral gauche
livré (`≥1024px`) : marque Auren + **4 destinations** (même ordre/href/labels/icônes/mapping que la bottom
nav, source unique), secondaires dans `<details>` « Plus » (Historique/Physique/Coach/Squads/Classement),
Contact + **logout POST** en pied. Breakpoint unifié **1024px** (bottom nav 769→1024, spec) ; topbar
masquée desktop (Option A) ; contenu décalé `margin-left: var(--app-rail-w)` + `max-width` 960px ; Focus
Mode resserré 720px. Tokens Auren existants (**0 nouvelle couleur**), actif ≠ couleur seule, tap ≥44px,
`:focus-visible`. **Template + CSS only** — aucun backend/route/service/model/migration/data/manifest/
asset/JS/contrat POST. 46 tests dédiés + 1 réorienté (769→1024, non affaibli). Bottom nav 03.1 **intacte**.
Session-active hardening + skip link **différés à `Sb_UI_03.3`/`Sx_UI_09`**.

**Prochaine étape** (séparée, non commencée) : `GO VALIDATE — Sb_UI_03.2 Desktop Rail / Secondary Shell`.
