# Sx_UI_03 — App Shell & Navigation — FINAL CLOSEOUT REPORT

**Verdict** : ✅ **Sx_UI_03 — CLOSED / HUMAN REVIEW COMPLETE**
**Type** : CLOSEOUT — docs-only (aucun code/test/asset/template touché)
**Date** : 2026-07-17
**Baseline canonique** : `0056baf` (merges Custom PR #23/#24 posés au-dessus du cycle)
**Spec fondatrice** : `Sx_UI_03_APP_SHELL_NAVIGATION_SPEC.md` (SPEC ACCEPTED)

> Le cycle **App Shell & Navigation** transforme le shell dense (menu hamburger 10 entrées + active-banner
> overlay) en un modèle **app-like** : bottom nav mobile 4 destinations, rail desktop, session active
> intégrée au shell, skip link. **Aucune route renommée, aucun métier touché, no-JS préservé.**

## 1. Baseline Git
HEAD canonique = origin = `0056baf`, working tree clean. Le cycle (7 commits) est **intact dans
l'historique** ; les merges Custom PR #23/#24 (persistence `user_programs`) sont posés **au-dessus**, sans
chevauchement shell. Aucun closeout Sx_UI_03 préexistant.

## 2. Chaîne de preuves (7 commits vérifiés)
```
Sb_UI_03.1  build 5a35ba8 + fix 4cd512a → CI 29484014891 3/3 → review ea151b6
Sb_UI_03.2  build f89f765             → CI 29508124300 3/3 → review a3a32c9
Sb_UI_03.3  build 0569178             → CI 29564964557 3/3 → review ac16d49
```
Tous présents (`git log -1 <sha>`). **3 CI vérifiées par SHA exact**, 3 jobs (`pytest + QA`, `lint`,
`SonarCloud`) `success` chacune.

## 3. Matrice des sous-sprints

| Lot | Portée | Build | CI (SHA) | Human review | Verdict |
|---|---|---|---|---|---|
| `Sb_UI_03.1` Mobile Bottom Navigation | bottom nav 4 destinations, SSR/no-JS, safe-area, tap ≥44px | `5a35ba8`(+`4cd512a`) | `29484014891` ✅3/3 | `ea151b6` | ✅ ACCEPTED |
| `Sb_UI_03.2` Desktop Rail / Secondary Shell | rail ≥1024px, mêmes 4 destinations, secondaires `<details>`, breakpoint 1024 | `f89f765` | `29508124300` ✅3/3 | `a3a32c9` | ✅ ACCEPTED |
| `Sb_UI_03.3` App Shell Hardening | topbar rétrogradée, active-banner supprimée + indicateur Séance, skip link | `0569178` | `29564964557` ✅3/3 | `ac16d49` | ✅ ACCEPTED |

## 4. Objectifs de la spec Sx_UI_03 — verdicts

| Objectif (spec) | Verdict | Lot / preuve |
|---|---|---|
| Bottom nav mobile **≤4 entrées** (Séance/Programmes/Progression/Profil) | **ACHIEVED** | `03.1` — 4 destinations, mapping partagé |
| Rail desktop latéral gauche (≥1024px) | **ACHIEVED** | `03.2` — `<aside class="app-rail">`, breakpoint 1024 |
| Rétrograder les secondaires (Historique/Physique/Coach/Squads/Classement) | **ACHIEVED** | `03.3` — topbar secondaire, `is-subactive`, 0 route supprimée |
| Session active **intégrée au shell** (fin de l'overlay `.active-banner`) | **ACHIEVED** | `03.3` — banner supprimée, indicateur onglet Séance, Home hero = surface Reprendre |
| **Action principale hors tab bar** (CTA contextuel, pas dans la nav) | **ACHIEVED** | `03.1`/`03.3` — 0 CTA/form dans bottom nav/rail |
| Safe-area iOS (`env(safe-area-inset-bottom)`) | **ACHIEVED** | `03.1` — bottom nav |
| **No-JS** compatible (SSR, progressive enhancement) | **ACHIEVED** | 3 lots — `<details>` natifs, liens natifs, 0 JS requis |
| **Aucun renommage de route** (nav = routes existantes) | **NON-GOAL PRESERVED** | 3 lots template+CSS only, url_for inchangés |
| Skip link (contrat shell a11y) | **ACHIEVED** | `03.3` — `#main-content`, 1er interactif |
| Un seul actif par région, jamais `aria-current="false"` | **ACHIEVED** | mapping dérivé `request.url.path`, testé |
| CI verte + human review pour chaque build | **ACHIEVED** | matrice §3 (3 CI 3/3 + 3 reviews) |
| Accessibilité **transverse** (reduced-motion, form aria-live, contraste global) | **EXTERNAL / DEFERRED** | → `Sx_UI_09` (hors scope Sx_UI_03 ; skip link seul livré ici) |

## 5. Non-goals préservés
Aucun renommage de route/service/model/table · aucun changement métier (reco/readiness/overload/
substitution/BI/Home logic) · aucun framework/SPA/React/bundler · aucun JS requis pour naviguer · aucune
migration · aucun asset/manifest/icon touché. Les 3 lots sont **template + CSS only** ; `index.html`
byte-identique (03.3).

## 6. État réel du shell (post-cycle)
- **Mobile (<1024px)** : bottom nav 4 destinations (Séance/Programmes/Progression/Profil) + topbar
  **secondaire** (Historique/Physique/Coach/Squads/Classement + Contact + logout POST) + skip link.
- **Tablette portrait (769–1023px)** : bottom nav conservée, rail absent.
- **Desktop (≥1024px)** : rail latéral gauche (4 destinations + secondaires `<details>` + Contact +
  logout) ; bottom nav + topbar masquées ; contenu décalé + `max-width` 960px ; skip link.
- **Session active** : plus d'overlay `.active-banner` ; Home hero = unique surface « Reprendre » ;
  indicateur discret (dot ambre statique + `sr-only « En cours »`) sur l'onglet Séance.
- **Focus Mode** : resserré 720px desktop, sticky CTA/rest timer/F1-F2-F3/contrats POST préservés.

## 7. Résidus / dettes différées (correctement séparés)
- **`Sx_UI_09` Accessibility & Motion** (NOT OPENED) : reduced-motion global, aria-live des erreurs,
  aria-invalid/aria-describedby, contraste transverse, auth standalone, charts/BodyMap. Le skip link
  était le **seul** élément a11y de Sx_UI_03.
- **Limite héritée** (non-régressive, documentée) : le view `session_detail` ne passe pas `active_session`
  → l'indicateur nav n'apparaît pas sur `/sessions/{id}` (identique à l'ancienne bannière ; onglet Séance
  y reste actif). Élargir la disponibilité = toucher les routers (hors scope shell).
- Ces éléments **ne sont pas** des omissions du cycle.

## 8. Risques acceptés (mineurs)
- Inspection pixel (rendu navigateur mobile/tablette/desktop) = **action opérateur** (pas de navigateur en
  environnement) ; inspections programmatiques satisfaisantes à chaque lot.
- 4 tests `test_vscode_*` échouent au full sweep **local** (worktree sans `.vscode/`) — environnementaux,
  CI réelle verte.

## 9. Architecture préservée
FastAPI SSR + Jinja2, no-JS/no-SPA/no-React, PWA progressive, Auren Terminal (graphite/mono/ambre
`#C8A24B`, **0 nouvelle couleur** sur les 3 lots). Breakpoint unifié 1024px. Bottom nav + rail dérivent du
**même mapping Jinja** (`is_sess`/`is_programs`/`is_prog`/`is_prof`, source unique).

---

## Verdict

**Verdict :** ✅ **Sx_UI_03 — CLOSED / HUMAN REVIEW COMPLETE.** Le cycle App Shell & Navigation est
**intégralement livré et accepté** : ses **3 lots applicatifs** (`03.1` bottom nav mobile · `03.2` rail
desktop / secondary shell · `03.3` shell hardening) sont **human-review accepted**, chacun avec **CI 3/3
verte** (SHA exacts vérifiés). Le shell passe d'un **menu hamburger dense 10 entrées + active-banner
overlay** à un **modèle app-like** : bottom nav 4 destinations (mobile), rail latéral (desktop), topbar
rétrogradée en navigation secondaire, session active **intégrée au shell** (Home hero = surface Reprendre
+ indicateur onglet Séance), skip link. **Non-goals préservés** : aucun renommage de route, aucun métier
touché, no-JS intégral, Auren Terminal (0 nouvelle couleur). **Dettes a11y transverses correctement
différées à `Sx_UI_09`.** Le cycle ferme le résidu `Sx_UI_03` identifié par `Sx_UI_12`.

**Prochaine piste** (non commencée) : queue résiduelle `Sx_UI_12` — **`Sx_UI_09` Accessibility & Motion
spec** (à ouvrir), `Sb_UI_11.3` Final Auren Baseline, puis `Sx_UI` Global Final Closeout. `Sb_SESSION_UX_01.5`
reste FIELD TEST READY (indépendant).
