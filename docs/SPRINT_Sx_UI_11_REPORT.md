# Sprint Report — Sx_UI_11 Screenshot Regression Baseline Spec

**Sprint ID :** `Sx_UI_11`
**Type :** SPEC ONLY (docs-only)
**Date :** 2026-07-02
**Auteur :** opérateur (Martin Feldmann) + agent Claude Code
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Verdict :** ✅ **READY FOR HUMAN REVIEW**

---

## 1. Résumé

Sprint spec-only du cycle `Sx_UI`. Définit le **protocole de baseline visuelle** à consommer par tout sprint de reskin ultérieur (`Sx_UI_04` et suivants), sans installer d'outil, sans écrire de script, sans capturer de screenshot.

Ouverture autorisée après :

- `Sx_UI_01` ✅ accepté (implicite override opérateur)
- `Sx_UI_02` ✅ accepté 2026-07-02 (`fdfd71a`)
- `Sx_UI_03` ✅ accepté 2026-07-02 (`88ca206`)
- `Sb_OPS.ci-path-filter` opérationnel — 5 pushes docs-only consécutifs skippés (`b4ed2c6`, `fdfd71a`, `b3ae3a9`, `88ca206` et le push venir Sx_UI_11)

Objectif : définir 21 sections normatives (§1 à §21) qui cadreront le sprint de build `Sb_UI_11.1` (tooling Playwright, fixtures, premier `capture.py`) et lui feront porter les modifications infra (touchant `scripts/`, `tests/`, potentiellement `.github/workflows/`).

Ce sprint ne modifie aucun template, aucun CSS, aucun JS, aucune route, aucun asset, aucune dépendance. Aucun screenshot n'est capturé.

## 2. Fichiers créés / modifiés

### Créés

- `docs/strategy/Sx_UI_11_SCREENSHOT_REGRESSION_BASELINE_SPEC.md` — spec principale, 21 sections structurantes
- `docs/SPRINT_Sx_UI_11_REPORT.md` — ce rapport de sprint

### Modifiés

- `docs/strategy/SPEC_REGISTRY.md` — Sx_UI_11 🟢 SPEC delivered pending review, Sx_UI_04 blocked until Sx_UI_11 accepted + baseline P0 disponible
- `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` — position : prochaine action = human review Sx_UI_11, rappel build UI toujours bloqué

## 3. Confirmation docs-only

**Scope strict respecté.** Aucun fichier hors `docs/` modifié :

- ❌ `app/` (aucun service, aucun router, aucun template, aucun static, aucun CSS, aucun JS)
- ❌ `tests/`
- ❌ `migrations/`
- ❌ `scripts/`
- ❌ `.github/workflows/`
- ❌ `.env`, config runtime
- ❌ `requirements-lock.txt`, `pyproject.toml`, `package.json` (aucune dépendance ajoutée)
- ❌ Manifest, favicon, assets
- ❌ Aucun renommage `SPIGNOS` → `Auren` dans le code
- ❌ Aucun template lu **modifié** (lecture read-only autorisée pour inventorier les routes existantes uniquement)

## 4. Décisions prises

| # | Décision | Section spec |
|---|---|---|
| 1 | Outil recommandé : **Playwright Python binding** (OQ-G tranché) | §4, §19 |
| 2 | Alternatives Puppeteer / Percy / snapshot manuel écartées V1 | §4 |
| 3 | 2 viewports : mobile 360×640 + desktop 1440×900 | §5 |
| 4 | **Matrice de 18 écrans × 2 viewports = 36 screenshots max**, P0=14 obligatoires, P1=16 recommandés, P2=6 différables | §5 |
| 5 | Baseline P0 minimum obligatoire avant premier code Sx_UI_04 | §5, §14 |
| 6 | Auth : compte de test fixture, **jamais** de compte prod, **jamais** de password en clair (règle anti-secret hard) | §6 |
| 7 | Fixture DB dédiée locale (6 IDs : empty, standard, with_history, with_active_session, with_measurements, body_intelligence.enabled) — jamais dépendante de prod | §7, §19 (OQ-W) |
| 8 | Session active scenario : 3 exos (done + active + future) + sticky CTA + jump bar + header sticky | §8 |
| 9 | No-JS baseline hors-scope V1 (tests HTML Sx_29 suffisent), reduced-motion reporté à Sx_UI_09 | §9, §19 (OQ-Y) |
| 10 | Storage V1 : **artefacts CI + release tag**, `.gitignore` sur baseline locale, réversible en Sb_UI_11.1 | §10, §19 (OQ-V) |
| 11 | Convention nommage : `baseline/{page-slug}/{viewport}-{state}.png` kebab-case strict | §11 |
| 12 | Diff tolerance : layout shift ≥ 4px = rejet par défaut, antialiasing toléré, revue humaine primaire, aucun gate CI binaire V1 | §12, §19 (OQ-Z) |
| 13 | A11y visual checks : tap targets, bottom nav non chevauchante, sticky CTA visible, safe-area, contraste perçu, lisibilité mono, no horizontal scroll | §13 |
| 14 | Sx_UI_04 build ne démarre pas sans baseline P0 (14 screenshots minimum) OU dérogation opérateur explicite | §14 |
| 15 | CI policy : Sx_UI_11 spec = docs-only skip ; Sb_UI_11.1 build = CI complète attendue | §15 |
| 16 | 8 risques identifiés avec mitigations (fragilité, non-déterminisme, secrets, dépendance navigateur, storage, faux sentiment sécurité, staleness, pollution prod) | §16 |
| 17 | Playwright NON installé dans ce sprint | §17 |
| 18 | Screenshots local seulement V1, CI optionnelle Sb_UI_11.2 | §19 (OQ-X) |
| 19 | Python binding Playwright > CLI Node V1 | §19 (OQ-AA) |
| 20 | P0 obligatoires + P1 recommandés + P2 différables avec dérogation P0-only autorisée | §19 (OQ-AB) |
| 21 | Baseline non versionnée dans git par défaut, réversible | §10, §19 (OQ-V) |

## 5. OQ list (Open Questions)

Rappel des OQ résolues et résiduelles.

**Résolues dans Sx_UI_11 (recommandations V1) :**

| OQ | Résolution |
|---|---|
| OQ-G | Playwright confirmé |
| OQ-V | Artefacts CI + release tag, baseline non-versionnée par défaut |
| OQ-W | Fixture DB dédiée locale, jamais dépendante de prod |
| OQ-X | Screenshots local seulement V1, CI optionnelle Sb_UI_11.2 |
| OQ-Y | Tests HTML existants suffisent, no-JS baseline hors-scope V1 |
| OQ-Z | Revue humaine primaire V1, seuils numériques différés à Sb_UI_11.2 |
| OQ-AA | Playwright Python binding V1 |
| OQ-AB | P0 obligatoires, P1 recommandés, P2 différables |

**Pending (non bloquantes pour Sx_UI_04 spec, bloquantes pour Sb_UI_11.1 build) :**

Aucune OQ résiduelle spécifique à Sx_UI_11. Les OQ résiduelles cumulées avant tout code Sx_UI_04 restent :

- OQ-R (Sx_UI_03) — organisation Progression sous-nav — décision `Sx_UI_04`
- OQ-H (Sx_UI_02) — palette hex figée — décision `Sx_UI_04`
- OQ-I (Sx_UI_02) — font sans final — décision `Sx_UI_04`
- OQ-J (Sx_UI_02) — font mono final — décision `Sx_UI_04`
- OQ-K (Sx_UI_02) — fluid clamp vs tailles fixes — décision `Sx_UI_04`
- OQ-M (Sx_UI_02) — Style Dictionary vs custom naming — décision `Sx_UI_04`
- OQ-L (Sx_UI_02) — dark mode — Sx_UI_02bis ou Sx_UI_09bis
- OQ-A (Sx_UI_01) — due diligence juridique Auren — bloque uniquement Sx_UI_10

## 6. Non-goals respectés

Rappel des non-goals (§17 de la spec), tous respectés :

- ✅ Playwright non installé
- ✅ Aucun `pip install`, `npm install`
- ✅ Aucun package ajouté aux dépendances
- ✅ Aucun script screenshot créé
- ✅ Aucune CI modifiée
- ✅ Aucun screenshot capturé
- ✅ Aucun CSS applicatif
- ✅ Aucun template modifié
- ✅ Aucun JS
- ✅ Aucun asset
- ✅ Aucune route ajoutée / modifiée / redirigée
- ✅ Aucune migration Alembic
- ✅ Aucun modèle SQLAlchemy
- ✅ Aucun build (`Sb_UI_11.k` non ouvert)
- ✅ Aucun auth de test implémenté
- ✅ Pas de logo / manifest modifié
- ✅ Pas de renommage SPIGNOS → Auren

## 7. DoD local

Sanity checks exécutés en fin de sprint :

- [x] `git diff --name-only` docs-only strict : ✅ **4 fichiers, tous dans `docs/`**
- [x] `git status` hors `docs/` : ✅ **vide**
- [x] Aucun CSS / JS / HTML modifié : ✅ **confirmé**
- [x] Aucun template modifié : ✅ **confirmé** (routes inventoriées en lecture read-only sur `app/routers/*.py`, jamais modifiées)
- [x] Aucun fichier `app/`, `tests/`, `migrations/`, `scripts/`, `.github/` touché : ✅ **STRICT DOCS-ONLY**
- [x] Aucun package Python / Node ajouté : ✅ **confirmé** (aucune modification `requirements*.txt`, `pyproject.toml`)

**Verdict DoD local :** ✅ **all green — docs-only strict validé.**

## 8. Path filter expected skip

**Prédiction :** ce push sera 100% docs-only. Le trigger `push` de `.github/workflows/ci.yml` a `paths-ignore: ['docs/**']` depuis `a9ab10c`.

**Résultat attendu :** aucun run CI ne doit apparaître sur `gh run list --branch ... --limit 5` pour le SHA du commit Sx_UI_11.

**Historique cumulé path filter :** 5 pushes docs-only skippés jusqu'à `88ca206` (Sx_UI_03 acceptance). Sx_UI_11 sera le 6ᵉ push docs-only skip attendu.

## 9. Prochain sprint recommandé

Deux options selon décision opérateur (§20 de la spec) :

**Option A (recommandée) :** `Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC` **SPEC ONLY**.

Rationale : produire la spec du reskin session en parallèle du futur build baseline `Sb_UI_11.1`. Les deux sprints progressent sans se bloquer mutuellement. Le premier code applicatif `Sx_UI_04` (`Sb_UI_04.k`) reste bloqué jusqu'à disponibilité baseline P0 (14 screenshots minimum) OU dérogation opérateur explicite.

Contenu attendu de Sx_UI_04 :

- Périmètre reskin (session_focus.css + `_partials/session_focus_header.html` + `_partials/exercise_card.html` + `_partials/rest_timer.html` — pas de modif service métier)
- Application des tokens Sx_UI_02 (palette teal, spacing 4px, mono metrics, WCAG 44×44)
- Intégration bottom nav Sx_UI_03 (visible mais discrète dans focus mode)
- Résolution OQ-R (sous-nav Progression), OQ-H (palette hex), OQ-I (font sans), OQ-J (font mono), OQ-K (scale), OQ-M (naming)
- Aucun changement de route
- Aucun changement métier (scoring, overload_engine, substitution, coach_report, body_intelligence intacts)
- Statut BUILD toujours BLOCKED tant que baseline P0 pas disponible

**Option B :** `Sb_UI_11.1_SCREENSHOT_TOOLING_BUILD` **BUILD** (hors-cycle Sx_UI).

Rationale : outiller la baseline immédiatement, en amont de la spec Sx_UI_04. Sprint qui **touchera** `scripts/`, `tests/`, potentiellement `.github/workflows/`, `requirements-lock.txt`. **Déclenchera une CI complète** au push (comportement voulu). Coût compute CI attendu ~22 min.

**Ne pas ouvrir avant validation humaine de `Sx_UI_11`.**

## 10. Références

- Spec de ce sprint : `docs/strategy/Sx_UI_11_SCREENSHOT_REGRESSION_BASELINE_SPEC.md`
- Specs précédentes ✅ acceptées : `docs/strategy/Sx_UI_01_BRAND_FOUNDATION_SPEC.md`, `docs/strategy/Sx_UI_02_DESIGN_TOKENS_SPEC.md`, `docs/strategy/Sx_UI_03_APP_SHELL_NAVIGATION_SPEC.md`
- Roadmap cycle : `docs/strategy/UI_TRANSFORMATION_ROADMAP.md`
- Registry : `docs/strategy/SPEC_REGISTRY.md` §1quinquies
- Roadmap globale : `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`
- Focus mode précurseur : `docs/strategy/Sx_29_CLOSURE_REPORT.md` + `docs/dogfood/DOGFOOD_Sx_29_FOCUS_MODE_TEMPLATE.md`
- CI cost optimization : `docs/SPRINT_Sb_OPS_ci_path_filter_BUILD_REPORT.md`

## 11. Verdict

✅ **READY FOR HUMAN REVIEW.**

Protocole baseline défini sans install d'outil, sans script, sans capture. Matrice 18 écrans × 2 viewports posée avec priorisation P0/P1/P2. Auth strategy avec règle anti-secret hard. Fixture DB déterministe locale. Session active scenario précis. Storage V1 = artefacts CI + release tag. Diff tolerance = revue humaine primaire. Dépendance Sx_UI_04 explicitée avec règle dure + alternative pragmatique. 8 OQ résolues V1, aucune OQ résiduelle spécifique Sx_UI_11. Prochaine action : human review + décision entre Option A (Sx_UI_04 SPEC ONLY parallèle) ou Option B (Sb_UI_11.1 BUILD immédiat).
