# Sx_UI_11 — Human Review Report

**Spec :** `docs/strategy/Sx_UI_11_SCREENSHOT_REGRESSION_BASELINE_SPEC.md`
**Sprint report source :** `docs/SPRINT_Sx_UI_11_REPORT.md`
**Commit spec :** `2a2be71c659311548ea3b55644b63b41873b719c`
**Date review :** 2026-07-02
**Reviewer :** opérateur (Martin Feldmann)
**Verdict :** ✅ **SPEC ACCEPTED**

---

## 1. Verdict

**Sx_UI_11 Screenshot Regression Baseline Spec est accepté en human review.**

La spec devient la source de vérité normative pour toute décision de baseline visuelle dans le cycle `Sx_UI`. Tout sprint de build baseline (`Sb_UI_11.k`) et tout sprint code visuel (`Sx_UI_04` et suivants) doit s'y référer pour l'outillage, la matrice, l'auth, les fixtures, le scénario session active, le storage, la convention nommage, la diff tolerance et la dépendance à Sx_UI_04.

## 2. Décisions validées

| Domaine | Décision validée |
|---|---|
| Outil | **Playwright Python binding** (OQ-G tranché) |
| Screenshots capturés dans Sx_UI_11 | **aucun** — spec pure, aucun outil installé |
| Scripts créés dans Sx_UI_11 | **aucun** — spec pure |
| Packages ajoutés | **aucun** — `requirements-lock.txt`, `pyproject.toml`, `package.json` intacts |
| CI workflow modifié | **aucun** — `.github/workflows/` intact |
| Viewports baseline | mobile **360×640** + desktop **1440×900** |
| Matrice maximale | **18 écrans × 2 viewports = 36 screenshots** |
| P0 minimum obligatoire avant Sx_UI_04 build | **14 screenshots** (7 écrans × 2 viewports), sauf dérogation opérateur explicite |
| Auth baseline | compte fixture local uniquement, **jamais** compte prod |
| Règle anti-secret | hard : jamais de password en clair dans scripts / logs / commits |
| Fixtures DB | déterministes, locales, **jamais** dépendantes de la prod (6 fixture IDs §7) |
| Storage V1 | **artefacts CI + release tag**, baseline locale `.gitignore` |
| Diff visual V1 | **revue humaine primaire**, aucun gate CI binaire pixel-perfect |
| No-JS baseline | **hors-scope V1**, tests HTML Sx_29 suffisent |
| Sx_UI_04 build | **BLOQUÉ** tant que baseline P0 pas disponible OU dérogation opérateur explicite |
| UI build général | **toujours bloqué** |

## 3. OQ résolues

Toutes les OQ ouvertes par Sx_UI_11 sont résolues V1 par cette spec + acceptance :

| OQ | Résolution |
|---|---|
| **OQ-G** | ✅ Playwright confirmé (Python binding) |
| **OQ-V** | ✅ Storage V1 = artefacts CI + release tag ; baseline locale `.gitignore` |
| **OQ-W** | ✅ Fixture DB dédiée locale, 6 fixture IDs, jamais dépendante prod |
| **OQ-X** | ✅ Screenshots local seulement V1, CI optionnelle en Sb_UI_11.2 |
| **OQ-Y** | ✅ Tests HTML Sx_29 suffisent, no-JS baseline hors-scope V1 |
| **OQ-Z** | ✅ Revue humaine primaire V1, seuils numériques différés Sb_UI_11.2 |
| **OQ-AA** | ✅ Playwright Python binding V1 (réversible) |
| **OQ-AB** | ✅ P0 obligatoires, P1 recommandés, P2 différables ; dérogation P0-only autorisée |

**Aucune OQ résiduelle spécifique à Sx_UI_11.**

Les OQ résiduelles cumulées avant tout code applicatif Sx_UI_04 restent :

- OQ-R (Sx_UI_03) — organisation Progression sous-nav — décision `Sx_UI_04`
- OQ-H (Sx_UI_02) — palette hex figée — décision `Sx_UI_04`
- OQ-I (Sx_UI_02) — font sans final — décision `Sx_UI_04`
- OQ-J (Sx_UI_02) — font mono final — décision `Sx_UI_04`
- OQ-K (Sx_UI_02) — fluid clamp vs tailles fixes — décision `Sx_UI_04`
- OQ-M (Sx_UI_02) — Style Dictionary vs custom naming — décision `Sx_UI_04`
- OQ-L (Sx_UI_02) — dark mode — Sx_UI_02bis ou Sx_UI_09bis
- OQ-A (Sx_UI_01) — due diligence juridique Auren — bloque uniquement Sx_UI_10

## 4. Confirmation docs-only

Ce sprint de review est **strictement documentaire**. Aucun périmètre applicatif touché :

- ❌ `app/` (aucun service, aucun router, aucun template, aucun static, aucun CSS, aucun JS)
- ❌ `tests/`
- ❌ `migrations/`
- ❌ `scripts/`
- ❌ `.github/workflows/`
- ❌ `.env`, config runtime, manifest, favicon
- ❌ `requirements-lock.txt`, `pyproject.toml`, `package.json`
- ❌ Aucun fichier de tokens implémenté
- ❌ Aucun renommage `SPIGNOS` → `Auren` dans le code

Fichiers touchés dans le commit d'acceptance :

- `docs/strategy/SPEC_REGISTRY.md` — Sx_UI_11 ✅ ACCEPTED, Sx_UI_04 🟡 READY TO OPEN en SPEC ONLY, Sb_UI_11.1 candidat futur non-ouvert
- `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` — prochaine action = GO Sx_UI_04 SPEC ONLY (build reste bloqué)
- `docs/SPRINT_Sx_UI_11_HUMAN_REVIEW_REPORT.md` — ce rapport

## 5. Confirmation no build

**BUILD NOT AUTHORIZED.**

- **Aucun Playwright installé** dans ce commit d'acceptance
- **Aucun screenshot capturé**
- **Aucun script créé**
- **Aucun package Python / Node ajouté** aux dépendances
- **Aucun CI workflow modifié**
- **Aucun sprint de build `Sb_UI_11.k` ni `Sb_UI_04.k` ouvert**

`Sx_UI_04` (Session Focus Reskin — premier sprint autorisé à modifier du code visuel) reste bloqué pour son sprint de **build** par :

1. `Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC` livré et accepté (prochaine action)
2. **Baseline P0 disponible** (14 screenshots minimum) OU dérogation opérateur explicite documentée
3. OQ résiduelles Sx_UI_02 tranchées (OQ-H hex, OQ-I sans, OQ-J mono, OQ-K scale, OQ-M naming)
4. OQ résiduelle Sx_UI_03 (OQ-R Progression sub-nav)

L'écriture de la spec `Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC` en SPEC ONLY est **autorisée** dès maintenant (option A retenue par l'opérateur). Elle ne déclenche aucun build code.

## 6. Choix opérateur : Option A retenue

**Option A** — Ouvrir `Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC` en **SPEC ONLY** ensuite.

**Option B rejetée V1** — `Sb_UI_11.1_SCREENSHOT_TOOLING_BUILD` reste candidat futur non-ouvert. Peut être ouvert avant, pendant ou après Sx_UI_04 SPEC, mais obligatoire avant tout build visuel sauf dérogation opérateur explicite.

**Rationale opérateur (interprétation) :**

Rédiger la spec `Sx_UI_04` en parallèle permet de trancher les OQ résiduelles Sx_UI_02 + Sx_UI_03 (palette hex, fonts, scale, sous-nav Progression) dans un contexte concret de reskin, sans devoir attendre le tooling baseline. Le build `Sb_UI_04.k` reste bloqué jusqu'à baseline P0 — l'ordre spec/build/tooling se cristallise ainsi :

1. Sx_UI_04 SPEC ONLY (docs-only, prochaine action GO)
2. Sb_UI_11.1 BUILD (tooling, hors-cycle, déclenche CI complète) — quand opérateur le décide
3. Sb_UI_04.1 BUILD (premier code visuel Sx_UI_04) — après Sb_UI_11.1 + baseline P0 OU dérogation

## 7. Rappels normatifs

- **Aucun Playwright installé** — l'outil est recommandé mais pas installé. `pip install playwright` + `playwright install chromium` restent à jouer dans `Sb_UI_11.1` uniquement.
- **Aucun screenshot capturé** — la baseline n'existe pas encore. Cette spec définit uniquement le protocole.
- **Baseline P0 obligatoire avant premier build visuel** — 14 screenshots minimum (7 écrans P0 × 2 viewports) OU dérogation opérateur explicite documentée dans un sprint override léger.
- **Règle anti-secret hard** — jamais de password en clair, `.env.baseline` git-ignore obligatoire, `--verbose` interdit sur curl/playwright quand secret transite.
- **Fixture user local uniquement** — jamais de compte prod (`martin_prod_smoke_20260702_1037` ou similaire) réutilisé.
- **Storage baseline non-versionné par défaut** — `.gitignore` sur `baseline/`, artefacts CI + release tag comme référence long terme.

## 8. Prochaine action recommandée

**Ouvrir `Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC` en SPEC ONLY** sur override explicite opérateur.

Contenu attendu de Sx_UI_04 (aperçu, à finaliser lors de l'ouverture) :

- Périmètre reskin : `app/static/css/session_focus.css` + `app/templates/_partials/session_focus_header.html` + `app/templates/_partials/exercise_card.html` + `app/templates/_partials/rest_timer.html` (pas de modif service métier, ni router, ni model)
- Application des tokens Sx_UI_02 (palette teal chirurgical désaturé, spacing 4px-based, mono metrics, WCAG 44×44)
- Intégration bottom nav Sx_UI_03 (visible mais discrète dans focus mode)
- Résolution des OQ résiduelles Sx_UI_02/03 (OQ-H hex, OQ-I sans, OQ-J mono, OQ-K scale, OQ-M naming, OQ-R Progression sub-nav)
- Aucun changement de route
- Aucun changement métier
- Statut BUILD toujours BLOCKED tant que baseline P0 pas disponible OU dérogation

Ce prochain sprint bénéficiera du path filter `Sb_OPS.ci-path-filter` : push docs-only → aucun run CI complet (7ᵉ push docs-only consécutif skippé attendu).

## 9. Références

- Spec acceptée : `docs/strategy/Sx_UI_11_SCREENSHOT_REGRESSION_BASELINE_SPEC.md`
- Sprint report source : `docs/SPRINT_Sx_UI_11_REPORT.md`
- Roadmap cycle : `docs/strategy/UI_TRANSFORMATION_ROADMAP.md`
- Registry : `docs/strategy/SPEC_REGISTRY.md` §1quinquies
- Roadmap globale : `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`
- Specs précédentes acceptées : `docs/strategy/Sx_UI_01_BRAND_FOUNDATION_SPEC.md`, `docs/strategy/Sx_UI_02_DESIGN_TOKENS_SPEC.md`, `docs/strategy/Sx_UI_03_APP_SHELL_NAVIGATION_SPEC.md`
- CI cost optimization : `docs/SPRINT_Sb_OPS_ci_path_filter_BUILD_REPORT.md` — path filter validé sur 6 pushes docs-only consécutifs (`b4ed2c6`, `fdfd71a`, `b3ae3a9`, `88ca206`, `2a2be71`)

## 10. Verdict final

✅ **Sx_UI_11 SPEC ACCEPTED — READY FOR Sx_UI_04 SPEC ONLY.**
