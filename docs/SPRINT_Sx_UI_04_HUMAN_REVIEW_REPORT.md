# Sx_UI_04 — Human Review Report

**Spec :** `docs/strategy/Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC.md`
**Sprint report source :** `docs/SPRINT_Sx_UI_04_REPORT.md`
**Commit spec :** `191555baa6851daf74ee2459303232b7456fb1d4`
**Date review :** 2026-07-02
**Reviewer :** opérateur (Martin Feldmann)
**Verdict :** ✅ **SPEC ACCEPTED**

---

## 1. Verdict

**Sx_UI_04 Session Focus Reskin Spec est accepté en human review.**

La spec devient la source de vérité normative pour toute décision de reskin du Focus Mode session. Toute modification future de `session_focus.css`, `session_detail.html`, ou des partials focus mode devra respecter le périmètre, les invariants, la consommation de tokens et le plan de sous-sprints définis.

Toute exception nécessite un amendement explicite `Sx_UI_04bis`.

## 2. Décisions validées

### 2.1. Statut

- **Sx_UI_04 reste SPEC ONLY**
- Le Focus Mode session est confirmé comme **première surface future de reskin Auren**
- **Aucun build UI n'est autorisé maintenant**

### 2.2. Non-modification confirmée

- ❌ Aucun CSS modifié (`session_focus.css`, `app.css` intacts)
- ❌ Aucun template modifié (`session_detail.html`, `_partials/*.html` intacts)
- ❌ Aucun JS modifié (`session_focus.js` intact)
- ❌ Aucun asset ajouté
- ❌ Aucun screenshot capturé
- ❌ Aucun Playwright installé
- ❌ Aucun changement métier (scoring, overload, substitution, coach, body intelligence intacts)
- ❌ Aucun renommage `SPIGNOS` → `Auren` dans le code

### 2.3. Product invariants verrouillés

- **Routes** : aucune ajoutée, modifiée, redirigée
- **Logging sets** : form POST `url_for('update_exercise_card', ...)` invariant
- **Rest timer** : contrats `data-start-rest`, `data-rest-duration`, `data-rest-skip`, `data-rest-display` invariants
- **Substitution** : accessible depuis card, jamais modifiée par reskin
- **Scoring** : `app/services/scoring/*` intact
- **Overload** : `overload_engine.py`, `overload_inputs.py`, `overload_explainer.py` intacts
- **Coach** : `coach_report.py`, `coach_inference.py` intacts
- **Body Intelligence** : `body_intelligence.py`, `body_intelligence_inputs.py` intacts
- **Auth / rate limit / CSRF** : intacts
- **Models SQLAlchemy** : aucune migration Alembic
- **No-JS fallback** : chaque écran reste utilisable JS désactivé

### 2.4. Future build candidates (rappel §5 de la spec)

| Fichier | Scope de changement autorisé |
|---|---|
| `app/static/css/session_focus.css` | Réécriture ciblée (tokens Sx_UI_02, structure BEM conservée) |
| `app/static/css/app.css` | **Uniquement si strictement nécessaire et localisé** — classes partagées `.badge`, `.btn`, `.field-group` seulement, jamais changements globaux hors scope |
| `app/templates/session_detail.html` | Ajustements structurels minimaux (wrappers, classes tokens) |
| `app/templates/_partials/session_focus_header.html` | Ajustements structurels (classes tokens, ordre méta) |
| `app/templates/_partials/exercise_card.html` | Ajustements structurels (classes tokens badges/boutons/inputs). Zéro changement de champs form. |
| `app/templates/_partials/rest_timer.html` | Ajustements structurels (classes tokens). Data-attrs préservés. |
| `app/static/js/session_focus.js` | **Patch trivial uniquement si absolument nécessaire** (classes CSS via `classList.add`), jamais changement de contrat. |

### 2.5. Dépendance baseline

**Build `Sx_UI_04` reste BLOQUÉ tant que :**

- Baseline P0 `Sx_UI_11` (14 screenshots minimum) n'est pas disponible via `Sb_UI_11.1`
- **OU** dérogation opérateur explicite non documentée

**Aucune dérogation baseline n'est accordée dans cette review.** Le chemin canonique passe par `Sb_UI_11.1` livré avant `Sb_UI_04.1`.

## 3. Confirmation docs-only

Ce sprint de review est **strictement documentaire**. Aucun périmètre applicatif touché :

- ❌ `app/` (aucun service, aucun router, aucun template, aucun static, aucun CSS, aucun JS)
- ❌ `tests/`
- ❌ `migrations/`
- ❌ `scripts/`
- ❌ `.github/workflows/`
- ❌ `.env`, config runtime, manifest, favicon
- ❌ `requirements-lock.txt`, `pyproject.toml`, `package.json`
- ❌ Aucun renommage `SPIGNOS` → `Auren` dans le code

Fichiers touchés dans le commit d'acceptance :

- `docs/strategy/SPEC_REGISTRY.md` — Sx_UI_04 ✅ ACCEPTED, Sb_UI_11.1 🟡 READY TO OPEN en BUILD, Sb_UI_04.1-5 restent blocked
- `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` — prochaine action = GO Sb_UI_11.1 BUILD, rappel Sb_UI_04.1 blocked, rappel aucune dérogation
- `docs/SPRINT_Sx_UI_04_HUMAN_REVIEW_REPORT.md` — ce rapport

## 4. Confirmation no build

**BUILD NOT AUTHORIZED.**

- **Aucun Playwright installé** dans ce commit d'acceptance
- **Aucun screenshot capturé**
- **Aucun script créé**
- **Aucun package Python / Node ajouté** aux dépendances
- **Aucun CI workflow modifié**
- **Aucun sprint `Sb_UI_04.k` ni `Sb_UI_11.1` ouvert** dans ce commit

`Sb_UI_04.1_CSS_FOUNDATION_BUILD` (premier code visuel Sx_UI_04) reste bloqué par :

1. `Sb_UI_11.1_SCREENSHOT_TOOLING_BUILD` livré et P0 baseline disponible (14 screenshots minimum)
2. **OU** dérogation opérateur explicite documentée dans un sprint override léger — **non accordée dans cette review**

## 5. Choix opérateur : Option A retenue

**Option A** — Ouvrir `Sb_UI_11.1_SCREENSHOT_TOOLING_BUILD` en **BUILD** ensuite.

**Option B rejetée V1** — dérogation opérateur explicite pour démarrer `Sb_UI_04.1` sans baseline n'est **pas accordée**.

**Rationale opérateur :**

Livrer d'abord la baseline P0 protège la review humaine du reskin (`Sb_UI_04.1` à `Sb_UI_04.5`) contre le drift silencieux. Sans comparateur avant/après, chaque sous-sprint reskin devient une revue "à l'aveugle" — inacceptable pour un cycle spec-driven.

**Ordre canonique cristallisé :**

1. `Sb_UI_11.1_SCREENSHOT_TOOLING_BUILD` — install Playwright + fixtures + capture P0 (14 screenshots minimum) → **prochaine action**
2. `Sb_UI_04.1_CSS_FOUNDATION_BUILD` — premier code visuel Sx_UI_04, après Sb_UI_11.1 livré
3. `Sb_UI_04.2` → `Sb_UI_04.5` — séquentiels, chaque sous-sprint ouvert sur override explicite après validation du précédent

## 6. Rappels normatifs

- **Baseline P0 obligatoire avant Sb_UI_04.1** — 14 screenshots minimum (7 écrans P0 × 2 viewports). Aucune dérogation.
- **Aucun CSS / template / JS / asset modifié** tant que baseline P0 non disponible.
- **Aucun changement métier** — invariants §4 de la spec strictement respectés lors des futurs sous-sprints.
- **Contrat JS invariant** — `session_focus.js` reçoit au plus un patch trivial (classes CSS uniquement).
- **Macros Jinja invariantes** — `segmented`, `field_group` non modifiées.
- **`app.css` scope minimal** — uniquement `.badge`, `.btn`, `.field-group` référencées par les partials session, jamais changements globaux hors scope.
- **Sb_UI_11.1 déclenchera une CI complète au push** (touche `scripts/`, `tests/`, potentiellement `.github/`, `requirements-lock.txt`) — comportement voulu.

## 7. Prochaine action recommandée

**Ouvrir `Sb_UI_11.1_SCREENSHOT_TOOLING_BUILD` en BUILD** sur override explicite opérateur.

Contenu attendu de Sb_UI_11.1 (aperçu, à finaliser lors de l'ouverture) :

- Install Playwright Python binding + Chromium binary (`pip install playwright` + `playwright install chromium`)
- Configuration `conftest.py` avec fixtures Playwright
- Premier `scripts/capture_baseline.py` ou `tests/visual/capture.py`
- 6 fixture DB IDs livrées (empty, standard, with_history, with_active_session, with_measurements, body_intelligence.enabled)
- Auth strategy fixture user local (compte `baseline_YYYYMMDD_HHMM` avec password random 24 chars)
- Capture des **14 P0 screenshots minimum** (Home / Session detail active / Session detail done / Progression / Profil / Login / Register — chacun × mobile + desktop)
- `.gitignore` sur `baseline/` local
- Upload artefact CI + release tag `baseline-preauren-YYYYMMDD`
- **Déclenchera CI complète** au push (aucun `paths-ignore` — le sprint touche du code)
- Coût compute CI attendu ~22-25 min (installation Chromium + capture 14+ screenshots)

Ce prochain sprint est **hors-cycle Sx_UI** (sprint infra OPS), enregistré dans SPEC_REGISTRY §1sexies (Sprints OPS hors-cycle).

## 8. Références

- Spec acceptée : `docs/strategy/Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC.md`
- Sprint report source : `docs/SPRINT_Sx_UI_04_REPORT.md`
- Roadmap cycle : `docs/strategy/UI_TRANSFORMATION_ROADMAP.md`
- Registry : `docs/strategy/SPEC_REGISTRY.md` §1quinquies + §1sexies
- Roadmap globale : `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`
- Specs précédentes acceptées : `Sx_UI_01`, `Sx_UI_02`, `Sx_UI_03`, `Sx_UI_11`
- Focus mode précurseur : `docs/strategy/Sx_29_CLOSURE_REPORT.md`
- CI cost optimization : `docs/SPRINT_Sb_OPS_ci_path_filter_BUILD_REPORT.md` — path filter validé sur 8 pushes docs-only consécutifs (`b4ed2c6`, `fdfd71a`, `b3ae3a9`, `88ca206`, `2a2be71`, `fc3433a`, `191555b` + push de cette acceptance)

## 9. Verdict final

✅ **Sx_UI_04 SPEC ACCEPTED — READY FOR Sb_UI_11.1 BUILD (Screenshot Tooling).**
