# Sprint Report — Sx_UI_03 App Shell & Navigation Spec

**Sprint ID :** `Sx_UI_03`
**Type :** SPEC ONLY (docs-only)
**Date :** 2026-07-02
**Auteur :** opérateur (Martin Feldmann) + agent Claude Code
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Verdict :** ✅ **READY FOR HUMAN REVIEW**

---

## 1. Résumé

Troisième sprint du cycle `Sx_UI` (Auren Visual & Product Transformation). Ouverture autorisée après :

- `Sx_UI_01` ✅ accepté implicitement par override opérateur
- `Sx_UI_02` ✅ accepté 2026-07-02 (`SPRINT_Sx_UI_02_HUMAN_REVIEW_REPORT.md`)
- `Sb_OPS.ci-path-filter` ✅ opérationnel — ce push docs-only ne déclenchera pas de CI complète

Objectif : définir l'architecture de navigation Auren V1 sans toucher au code. Réduction du chrome global de 10 destinations top-level actuelles (`base.html`) vers **bottom nav ≤ 4 entrées** (Séance / Programmes / Progression / Profil), avec destinations secondaires (Historique, Physique, Coach, Squads, Classement, Déconnexion) reclassées sous Progression ou Profil.

Ce sprint n'ouvre aucun build, ne modifie aucun template, aucun CSS, aucun JS, aucune route, aucun asset. Les décisions sont normatives sur papier et seront implémentées à partir de `Sx_UI_04` (après baseline `Sx_UI_11`).

## 2. Fichiers créés / modifiés

### Créés

- `docs/strategy/Sx_UI_03_APP_SHELL_NAVIGATION_SPEC.md` — spec principale, 24 sections structurantes
- `docs/SPRINT_Sx_UI_03_REPORT.md` — ce rapport de sprint

### Modifiés

- `docs/strategy/SPEC_REGISTRY.md` — Sx_UI_03 🟢 SPEC delivered pending review, Sx_UI_04 blocked (baseline Sx_UI_11 required first), Sx_UI_11 explicité comme "required before first visual build"
- `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` — position mise à jour : prochaine action = human review Sx_UI_03, rappel build UI blocked, rappel screenshot baseline requise avant Sx_UI_04

## 3. Confirmation docs-only

**Scope strict respecté.** Aucun fichier hors `docs/` modifié :

- ❌ `app/` (aucun service, aucun router, aucun template, aucun static, aucun CSS, aucun JS)
- ❌ `tests/`
- ❌ `migrations/`
- ❌ `scripts/`
- ❌ `.github/workflows/`
- ❌ `.env`, config runtime
- ❌ Manifest, favicon, assets
- ❌ Aucun renommage `SPIGNOS` → `Auren` dans le code
- ❌ Aucun template lu **modifié** (lecture read-only autorisée pour diagnostic §3 uniquement)

## 4. Décisions prises (§ de la spec)

| # | Décision | Section |
|---|---|---|
| 1 | Bottom nav V1 = 4 entrées : Séance / Programmes / Progression / Profil | §5 (OQ-C) |
| 2 | Accueil absorbé conceptuellement par Séance, route `/` conservée V1 | §7 (OQ-N) |
| 3 | Historique → sous-section de Progression | §6, §9 (OQ-O) |
| 4 | Physique → sous-section de Progression | §6, §9 (OQ-D) |
| 5 | Coach → contextualisé (Séance, Progression, Session done), pas top-level | §11 (OQ-E) |
| 6 | Squads / Classement → surfaces secondaires opt-in dans Profil | §12 (OQ-P) |
| 7 | Déconnexion → action en fin de liste dans Profil | §6, §10 |
| 8 | Session active pattern : bloc dominant sur Today + point teal dans bottom nav "Séance" + jamais bannière modale | §13 |
| 9 | Header global : title court, max 1 action secondaire, pas de gros logo, "Auren" wordmark uniquement à Sx_UI_10 | §14 |
| 10 | Desktop : rail latéral gauche à partir de ≥ 1024px, bottom nav mobile en dessous | §16 (OQ-Q) |
| 11 | Focus mode session : bottom nav visible mais discrète, ne disparaît pas | §13, §15 |
| 12 | Point session active dans bottom nav = teal `--color-accent`, pas bleu minéral | §20 (OQ-S) |
| 13 | Shell logged-out (`/login`, `/register`) minimal, pas de bottom nav | §20 (OQ-T) |
| 14 | Bottom nav visible sur pages d'erreur (404, 500) si utilisateur authentifié | §20 (OQ-U) |
| 15 | Aucun nouveau token visuel introduit — consommation stricte de Sx_UI_02 | §18 |
| 16 | Baseline `Sx_UI_11` : 13 écrans × 2 viewports (360×640 + 1440×900) = 26 screenshots | §19 |
| 17 | Session detail focus mode preserve la logique Sx_29 (sticky header, jump bar, sticky CTA) — style unifié en Sx_UI_04 | §13, §15 |
| 18 | Aucune route modifiée, aucune redirection dans Sx_UI_03 — les rétrogradations sont purement de nav | §6 |
| 19 | Session logout reste `<form method="post">` pour sémantique HTTP + CSRF | §17 |
| 20 | Empty states définis pour chaque destination top-level | §5.1-5.4 |

## 5. OQ list

Rappel des OQ résolues et non-bloquantes.

**Résolues dans Sx_UI_03 (recommandation V1) :**

| OQ | Résolution |
|---|---|
| OQ-C | Bottom nav = 4 destinations |
| OQ-D | Physique sous Progression |
| OQ-E | Coach contextualisé (pas top-level) |
| OQ-N | Today ≡ Accueil, route `/` V1 |
| OQ-O | Historique sous Progression |
| OQ-P | Squads / Classement dans Profil (opt-in secondaire) |
| OQ-Q | Desktop = rail latéral gauche |
| OQ-S | Point session active = teal (accent principal) |
| OQ-T | Logged-out shell minimal, sans bottom nav |
| OQ-U | Bottom nav sur pages d'erreur si authentifié |

**Pending (non bloquantes) :**

| OQ | Question | Bloque |
|---|---|---|
| **OQ-R** | Séparation Vue d'ensemble / Historique / Physique / Coach dans Progression : sous-onglets SSR, sections empilées, `<details>` ? | Sx_UI_04 merge |

**Pending Sx_UI_02 résiduelles rappelées (ne bloquent pas Sx_UI_03) :**

- OQ-H (palette hex figée exacte)
- OQ-I (font sans final)
- OQ-J (font mono final)
- OQ-K (fluid clamp vs tailles fixes)
- OQ-L (dark mode Sx_UI_02bis vs Sx_UI_09bis)
- OQ-M (Style Dictionary vs custom naming)

Toutes doivent être tranchées avant `Sx_UI_04` merge (premier sprint code applicatif).

**Pending Sx_UI_01 résiduelle :**

- OQ-A (due diligence juridique Auren) — bloque `Sx_UI_10` execution uniquement, pas `Sx_UI_04`.

## 6. Non-goals respectés

Rappel des non-goals (§21 de la spec), tous respectés :

- ✅ Aucun code
- ✅ Aucun template modifié
- ✅ Aucun CSS
- ✅ Aucun JS
- ✅ Aucune route ajoutée / modifiée / supprimée / redirigée
- ✅ Aucun modèle SQLAlchemy touché
- ✅ Aucune migration
- ✅ Aucun asset (icône SVG, image, police web)
- ✅ Aucun logo
- ✅ Pas de manifest update
- ✅ Pas de rebrand code (SPIGNOS reste dans les templates)
- ✅ Pas de suppression réelle de pages/routes
- ✅ Pas de redirection HTTP
- ✅ Pas de changement d'auth
- ✅ Pas de changement métier
- ✅ Pas de build (`Sb_UI_NN.k` non ouvert)
- ✅ Pas de screenshot capture (relève de `Sx_UI_11`)
- ✅ Pas de token visuel nouveau (Sx_UI_02 seul propriétaire)
- ✅ Pas de flag toggle modifié

## 7. DoD local

Sanity checks exécutés en fin de sprint :

- [x] `git diff --name-only` docs-only strict : ✅ **4 fichiers, tous dans `docs/`**
- [x] `git status` hors `docs/` : ✅ **vide**
- [x] Aucun CSS / JS / HTML modifié : ✅ **confirmé**
- [x] Aucun template modifié : ✅ **confirmé** (`app/templates/base.html`, `session_focus_header.html`, `session_detail.html` lus en read-only pour diagnostic §3, jamais modifiés)
- [x] Aucun fichier `app/`, `tests/`, `migrations/`, `scripts/`, `.github/` touché : ✅ **STRICT DOCS-ONLY**

**Verdict DoD local :** ✅ **all green — docs-only strict validé.**

## 8. Path filter expected skip

**Prédiction :** ce push sera 100% docs-only. Le trigger `push` de `.github/workflows/ci.yml` a `paths-ignore: ['docs/**']` depuis `a9ab10c` (Sb_OPS.ci-path-filter validé au push `b4ed2c6`).

**Résultat attendu :** aucun run CI ne doit apparaître sur `gh run list --branch ... --limit 5` pour le SHA du commit Sx_UI_03.

**Vérification post-push :** `PATH FILTER VERIFIED — docs-only push skipped heavy CI` — à confirmer au push.

## 9. Prochain sprint recommandé

Deux options possibles selon décision opérateur :

**Option 1 (recommandée) :** `Sx_UI_11_SCREENSHOT_REGRESSION_SPEC` **SPEC ONLY**.
Rationale : `Sx_UI_04` (premier sprint code visuel) exige baseline `Sx_UI_11` comme précondition. La produire d'abord permet de :
- documenter l'avant/après visuel du reskin
- avoir un point de comparaison pour valider les tokens `Sx_UI_02` en runtime
- servir de proof à réviser en human review de `Sx_UI_04`

Contenu attendu :
- outil retenu (Playwright vs alternatives — OQ-G de Sx_UI_01)
- viewports (360×640 mobile + 1440×900 desktop confirmés)
- liste des 26 screenshots à produire (§19 Sx_UI_03)
- stratégie DB pour les screens session (empty state vs scénario de démo)
- storage baseline (git-tracked SVG/PNG vs artefact CI)
- statut BUILD toujours BLOCKED

**Option 2 :** `Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC` **SPEC ONLY** en parallèle de `Sx_UI_11`.
À condition que `Sx_UI_11` soit ouverte simultanément et que la baseline soit produite avant tout code `Sx_UI_04`.

**Ne pas ouvrir avant validation humaine de `Sx_UI_03`.**

## 10. Références

- Spec de ce sprint : `docs/strategy/Sx_UI_03_APP_SHELL_NAVIGATION_SPEC.md`
- Spec précédente : `docs/strategy/Sx_UI_02_DESIGN_TOKENS_SPEC.md` ✅ accepted
- Spec avant : `docs/strategy/Sx_UI_01_BRAND_FOUNDATION_SPEC.md` ✅ accepted
- Roadmap cycle : `docs/strategy/UI_TRANSFORMATION_ROADMAP.md`
- Registry : `docs/strategy/SPEC_REGISTRY.md` §1quinquies
- Roadmap globale : `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`
- Brainstorm sources : `docs/strategy/brainstorm/UI_TRANSFORMATION_BRAINSTORM_V1_normalized.md`, `..._V2_normalized.md`
- Focus mode précurseur : `docs/strategy/Sx_29_CLOSURE_REPORT.md`
- CI cost optimization : `docs/SPRINT_Sb_OPS_ci_path_filter_BUILD_REPORT.md`

## 11. Verdict

✅ **READY FOR HUMAN REVIEW.**

Navigation V1 posée à 4 entrées mobile + rail latéral desktop. Rétrogradations documentées (Coach contextualisé, Squads/Classement dans Profil, Historique/Physique sous Progression). Session active pattern défini (bloc Today + point teal bottom nav). Règles a11y (WCAG 2.2 44×44, `aria-current`, non-color cues, focus visible). Baseline `Sx_UI_11` préparée (13 écrans × 2 viewports = 26 screenshots). Aucun code touché, aucun template modifié, aucun sprint de build ouvert.
