# Sb_UI_11.1 — Human Review Report

**Sprint :** `Sb_UI_11.1_SCREENSHOT_TOOLING_BUILD`
**Sprint report source :** `docs/SPRINT_Sb_UI_11_1_SCREENSHOT_TOOLING_BUILD_REPORT.md`
**Commit :** `e8ba190d8df2530d68939ce3708377a8fb76915f`
**CI run :** [`28595637219`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28595637219)
**Date review :** 2026-07-02
**Reviewer :** opérateur (Martin Feldmann)
**Verdict :** ✅ **SPRINT ACCEPTED**

---

## 1. Verdict

**Sb_UI_11.1 Screenshot Tooling Build est accepté en human review.**

Le tooling minimal (matrice + CLI Playwright + tests + anti-secret hard rule) est livré, la CI est verte, et l'invariant clé est préservé : **aucune baseline P0 n'a été capturée dans ce sprint**. La capture réelle reste une action locale opérateur.

## 2. Preuve CI

| Élément | Valeur |
|---|---|
| Run ID | `28595637219` |
| SHA commit | `e8ba190d8df2530d68939ce3708377a8fb76915f` |
| Event | `push` (CI complète comme voulu — path filter non-applicable) |
| Durée | 21 min 18 s (13:56:19 → 14:17:37 UTC) |
| Conclusion | ✅ **SUCCESS** |

## 3. 3 jobs verts

| Job | Conclusion | Steps | Durée |
|---|---|---|---|
| **lint** (ruff budget + bandit + actionlint + shellcheck + pip-audit + gitleaks + spec protocol + auth scope) | ✅ success | 21/21 | 44 s |
| **pytest + QA scripts** | ✅ success | 17/17 | ~20 min |
| **SonarCloud** | ✅ success | 9/9 | ~1 min |

## 4. Sécurité pass

| Gate | Résultat |
|---|---|
| `gitleaks scan` (Sb_26.4) | ✅ **PASS** — canaries de tests + placeholders `AUREN_BASELINE_*` non détectés comme secrets réels |
| `bandit security scan` (Sb_26.1) | ✅ **PASS** — 0 issues sur les 2 nouveaux scripts (526 lignes analysées) |
| `ruff budget check` (Sb_26.1) | ✅ **PASS** — 534 ≤ 548 baseline |
| `pip-audit runtime dependencies` (Sb_26.4) | ✅ **PASS** — Playwright non-runtime |
| `spec protocol check` (Sb_26.5) | ✅ **PASS** — nouveau sprint report détecté conforme |
| `actionlint` + `shellcheck` (Sb_26.1) | ✅ **PASS** (warning `SC2046` sur `ci.yml:189` préexistant, hors scope) |

## 5. Confirmations invariants

- ✅ **Aucun secret réel dans le commit** — gitleaks PASS + canaries test-only correctement détectés comme non-secrets
- ✅ **Aucun screenshot PNG committé** — matrice, CLI et tests uniquement ; `.gitignore` sur `var/visual-baseline/`, `baseline/`, `test-results/visual-baseline/`
- ✅ **Aucun compte prod utilisé** — test `test_no_prod_account_referenced` verrouille l'invariant (interdit `martin_prod_smoke`, `spignos.com`)
- ✅ **App code untouched** :
  - `app/` (services, routers, models, static, templates)
  - `migrations/`
  - `.github/workflows/deploy-production.yml`
  - `.github/workflows/ci.yml` (path filter préservé)
  - `requirements.txt`, `requirements-lock.txt` (Playwright reste extra optionnel dans `pyproject.toml`, jamais runtime)
  - Aucun renommage `SPIGNOS` → `Auren` dans le code

## 6. Baseline P0 status

| Item | Statut |
|---|---|
| Tooling available | ✅ **yes** (matrice + CLI + tests livrés en `e8ba190`) |
| **P0 baseline captured** | ❌ **NO** — la capture locale reste à exécuter par l'opérateur |
| Chromium installé en CI | ❌ **no** (comportement voulu) |
| Playwright installé dans requirements runtime | ❌ **no** (extra optionnel `[baseline]`) |

## 7. Prochaine action recommandée

**Capture P0 locale par l'opérateur** avec fixture user local, jamais un compte prod.

Étapes canoniques :

```bash
# 1. Installer Playwright localement (jamais en CI)
pip install -e '.[baseline]'
python -m playwright install chromium

# 2. Créer .env.baseline local (git-ignored) avec fixture user
cat > .env.baseline <<'EOF'
AUREN_BASELINE_USERNAME=<fixture-username-local>
AUREN_BASELINE_PASSWORD=<fixture-random-secret-local>
AUREN_BASELINE_ACTIVE_SESSION_ID=<id-from-local-fixture>
AUREN_BASELINE_DONE_SESSION_ID=<id-from-local-fixture>
EOF

# 3. Lancer l'app locale sur DB fixture (workout.db propre)

# 4. Source env + dry-run pour valider
set -a; source .env.baseline; set +a
python scripts/visual_baseline_capture.py --dry-run --priority P0

# 5. Capture réelle
python scripts/visual_baseline_capture.py \
    --base-url http://127.0.0.1:8000 \
    --priority P0 \
    --viewport all \
    --out-dir var/visual-baseline

# 6. Upload artefact CI OU release tag `baseline-preauren-YYYYMMDD`
```

## 8. Sb_UI_04.1 status

**`Sb_UI_04.1_CSS_FOUNDATION_BUILD` reste BLOQUÉ.**

Ce sprint ne peut pas démarrer avant :

1. **Capture P0 locale réellement effectuée** — 14 screenshots minimum, uploadés comme artefact ou release tag
2. **OR** — **dérogation opérateur explicite** documentée dans un sprint override léger

**Aucune dérogation n'est accordée dans cette review.** Le chemin canonique passe par la capture P0 avant tout code visuel.

## 9. Confirmation docs-only (ce sprint de review)

**Scope strict respecté.** Aucun périmètre applicatif touché dans ce commit d'acceptance :

- ❌ `app/` (aucun service, aucun router, aucun template, aucun static, aucun CSS, aucun JS)
- ❌ `tests/`
- ❌ `migrations/`
- ❌ `scripts/` (le tooling reste sur le commit `e8ba190`, non modifié)
- ❌ `.github/workflows/`
- ❌ `.env`, config runtime, manifest, favicon
- ❌ `requirements-lock.txt`, `pyproject.toml`, `package.json`
- ❌ Aucun Playwright installé, aucun screenshot capturé, aucun script créé

Fichiers touchés dans ce commit d'acceptance :

- `docs/strategy/SPEC_REGISTRY.md` — Sb_UI_11.1 ✅ DELIVERED + CI GREEN + HUMAN REVIEW ACCEPTED
- `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` — prochaine action = capture P0 locale opérateur, `Sb_UI_04.1` reste bloqué
- `docs/SPRINT_Sb_UI_11_1_HUMAN_REVIEW_REPORT.md` — ce rapport

## 10. Références

- Sprint report source : `docs/SPRINT_Sb_UI_11_1_SCREENSHOT_TOOLING_BUILD_REPORT.md`
- Spec source : `docs/strategy/Sx_UI_11_SCREENSHOT_REGRESSION_BASELINE_SPEC.md`
- Spec cible reskin : `docs/strategy/Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC.md`
- Registry : `docs/strategy/SPEC_REGISTRY.md` §1sexies
- Roadmap : `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`
- CI cost optimization : `docs/SPRINT_Sb_OPS_ci_path_filter_BUILD_REPORT.md`

## 11. Verdict final

✅ **Sb_UI_11.1 ACCEPTED — CI GREEN + TOOLING DELIVERED.**

**Baseline P0 : pending local capture by operator.**
**`Sb_UI_04.1` remains BLOCKED until P0 baseline captured or explicit operator override (not granted).**
