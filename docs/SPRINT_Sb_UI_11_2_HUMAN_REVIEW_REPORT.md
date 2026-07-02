# Sb_UI_11.2 — Human Review Report

**Sprint :** `Sb_UI_11.2_BASELINE_RUNTIME_INTEGRATION_PATCH`
**Sprint report source :** `docs/SPRINT_Sb_UI_11_2_BASELINE_RUNTIME_PATCH_REPORT.md`
**Commit :** `a2846a253612409d00284c7ce3946506a8577e04`
**CI run :** [`28604484292`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28604484292)
**Date review :** 2026-07-02
**Reviewer :** opérateur (Martin Feldmann)
**Verdict :** ✅ **SPRINT ACCEPTED**

---

## 1. Verdict

**Sb_UI_11.2 Baseline Runtime Integration Patch est accepté en human review.**

Le patch résout les frictions d'intégration observées lors de la tentative de capture P0 manuelle. Le tooling exploite désormais l'environnement applicatif existant (`.env`, `DATABASE_URL`, `SessionLocal`, `app_secret_key`, contrat cookie signé) au lieu de dupliquer la config dans un environnement parallèle.

**Baseline P0 n'est toujours pas capturée** — la capture reste une action locale opérateur, par design. Le CLI est simplement beaucoup plus utilisable qu'avant : plus de `.env.baseline` manuel, plus d'exports shell fragiles, plus de zsh parse errors.

## 2. Preuve CI

| Élément | Valeur |
|---|---|
| Run ID | `28604484292` |
| SHA commit | `a2846a253612409d00284c7ce3946506a8577e04` |
| Event | `push` (CI complète comme voulu — fichiers hors `docs/`) |
| Durée | 21 min 21 s (16:09:38 → 16:30:59 UTC) |
| Conclusion | ✅ **SUCCESS** |

## 3. 3 jobs verts

| Job | Conclusion | Steps |
|---|---|---|
| **lint** (ruff budget + bandit + actionlint + shellcheck + pip-audit + gitleaks + spec protocol + auth scope) | ✅ success | 21/21 |
| **pytest + QA scripts** | ✅ success | 17/17 |
| **SonarCloud** | ✅ success | 9/9 |

## 4. Décisions validées

### 4.1. Intégration app runtime

- ✅ Le tooling baseline exploite désormais l'environnement applicatif existant
- ✅ `DATABASE_URL` existant est réutilisé (pas de fork de config)
- ✅ Aucun environnement baseline parallèle n'est requis
- ✅ Le runtime local prépare les fixtures nécessaires automatiquement
- ✅ Le contrat auth cookie signé (`session_token` via `URLSafeTimedSerializer(app_secret_key)`) est réutilisé — cookie généré verbatim identique à ce que produit `app.services.auth.create_session_cookie`
- ✅ `visual_baseline_capture.py` peut consommer `--runtime-file` avec runtime > env vars pour la résolution des IDs
- ✅ Compatibilité env vars Sb_UI_11.1 conservée (fallback)

### 4.2. Refus prod hard

- ✅ `app_env == "production"` → exit code 11 (refus catégorique)
- ✅ `app_env == "prod"` (alias) → exit code 11
- ✅ DB URL non-locale → exit code 12 (allowlist : sqlite:///..., localhost/127.0.0.1 postgres)
- ✅ Signature DB courte n'expose jamais les credentials (test dédié)

### 4.3. Sécurité livraison

- ✅ Aucun PNG committé (`git status | grep -Ei .png` vide pre-commit)
- ✅ Aucun runtime artefact local committé (`auth-state.json`, `runtime.json`, DB, `.env`, `.env.baseline`)
- ✅ Aucun secret / cookie / token réel committé — gitleaks PASS
- ✅ Aucun compte prod utilisé — matrice + fixture 100% locales
- ✅ Password fixture généré aléatoirement (32 chars alphanumériques), jamais loggé
- ✅ Cookie value jamais loggée (test canary `test_write_storage_state_writes_file_but_never_logs_cookie`)

### 4.4. Zones intactes

- ✅ `app/` (services, routers, models, static, templates) intact
- ✅ `migrations/` intact
- ✅ `.github/workflows/deploy-production.yml` intact
- ✅ `.github/workflows/ci.yml` intact (path filter préservé)
- ✅ `requirements.txt`, `requirements-lock.txt` intacts (Playwright reste extra optionnel `[baseline]`)
- ✅ Aucun renommage `SPIGNOS` → `Auren` dans le code

## 5. Baseline P0 status

| Item | Statut |
|---|---|
| Runtime tooling available | ✅ **yes** (matrice + runtime prepare/verify + capture --runtime-file) |
| P0 baseline captured | ❌ **NO** — capture locale reste opérateur, par design |
| Chromium installé en CI | ❌ **no** (comportement voulu) |
| Playwright installé dans requirements runtime | ❌ **no** (extra optionnel `[baseline]`) |

## 6. Sb_UI_04.1 status

**`Sb_UI_04.1_CSS_FOUNDATION_BUILD` reste BLOQUÉ.**

Ce sprint ne peut pas démarrer avant :

1. **Baseline P0 réellement capturée localement** — 14 screenshots minimum (7 écrans P0 × 2 viewports, cible pratique 16), uploadés comme artefact ou release tag
2. **OR** — **dérogation opérateur explicite** documentée dans un sprint override léger

**Aucune dérogation n'est accordée dans cette review.** Le chemin canonique passe par la capture P0 avec le nouveau runtime CLI, avant tout code visuel.

## 7. Confirmation docs-only (ce sprint de review)

**Scope strict respecté.** Aucun périmètre applicatif touché dans ce commit d'acceptance :

- ❌ `app/` (aucun service, aucun router, aucun template, aucun static, aucun CSS, aucun JS)
- ❌ `tests/` (le tooling reste sur `a2846a2`, aucun test modifié)
- ❌ `scripts/` (le tooling reste sur `a2846a2`, aucun script modifié)
- ❌ `migrations/`
- ❌ `.github/workflows/`
- ❌ `.env`, config runtime, manifest, favicon
- ❌ `requirements-lock.txt`, `pyproject.toml`, `package.json`
- ❌ Aucun PNG, aucun `runtime.json`, aucun `auth-state.json`, aucune DB fixture

Fichiers touchés dans ce commit d'acceptance :

- `docs/strategy/SPEC_REGISTRY.md` — Sb_UI_11.2 ✅ DELIVERED + CI GREEN + HUMAN REVIEW ACCEPTED
- `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` — prochaine action = capture P0 locale opérateur avec nouveau CLI runtime
- `docs/SPRINT_Sb_UI_11_2_HUMAN_REVIEW_REPORT.md` — ce rapport

## 8. Prochaine action recommandée

**Capture P0 locale opérateur** avec le nouveau runtime CLI (2 commandes) :

```bash
# 1. Prérequis (une fois)
pip install -e '.[baseline]'
python -m playwright install chromium

# 2. Lancer l'app locale dans un terminal
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# 3. Préparer le runtime (autre terminal)
python scripts/visual_baseline_runtime.py prepare \
    --base-url http://127.0.0.1:8000 \
    --out-dir var/visual-baseline

# 4. Capturer P0
python scripts/visual_baseline_capture.py \
    --base-url http://127.0.0.1:8000 \
    --priority P0 \
    --viewport all \
    --out-dir var/visual-baseline \
    --runtime-file var/visual-baseline/runtime.json

# 5. Vérifier
find var/visual-baseline -name "*.png" | wc -l   # attendu ≥14
```

Puis :
- Upload artefact CI OU release tag `baseline-preauren-YYYYMMDD`
- Documenter dans `docs/BASELINE_P0_CAPTURED_YYYYMMDD.md`
- **Alors seulement** ouvrir `Sb_UI_04.1_CSS_FOUNDATION_BUILD` sur override explicite

## 9. Références

- Sprint report source : `docs/SPRINT_Sb_UI_11_2_BASELINE_RUNTIME_PATCH_REPORT.md`
- Sprint précédent : `docs/SPRINT_Sb_UI_11_1_SCREENSHOT_TOOLING_BUILD_REPORT.md` + acceptance
- Spec source : `docs/strategy/Sx_UI_11_SCREENSHOT_REGRESSION_BASELINE_SPEC.md`
- Spec cible reskin : `docs/strategy/Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC.md`
- Registry : `docs/strategy/SPEC_REGISTRY.md` §1sexies
- Roadmap : `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`

## 10. Verdict final

✅ **Sb_UI_11.2 ACCEPTED — CI GREEN + RUNTIME INTEGRATED.**

**Baseline P0 : pending local capture with new runtime CLI.**
**`Sb_UI_04.1` remains BLOCKED until P0 baseline captured or explicit operator override (not granted).**
