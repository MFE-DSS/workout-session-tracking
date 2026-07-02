# Sprint Report — Sb_UI_11.1 Screenshot Tooling Build

**Sprint ID :** `Sb_UI_11.1`
**Type :** **BUILD** — OPS/UI hors-cycle (touche `scripts/`, `tests/`, `pyproject.toml`, `.gitignore`)
**Date :** 2026-07-02
**Auteur :** opérateur (Martin Feldmann) + agent Claude Code
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Verdict :** ✅ **READY FOR HUMAN REVIEW**
**CI attendue :** ✅ **complète au push** (aucun `paths-ignore` — sprint touche du code)

---

## 1. Objectif

Livrer le tooling minimal pour produire une baseline screenshot P0 locale, déterministe, anti-secret, alignée avec `Sx_UI_11_SCREENSHOT_REGRESSION_BASELINE_SPEC.md` et `Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC.md §18`.

**Après ce sprint :**
- Tooling disponible : ✅ **oui** (matrice + CLI + tests)
- P0 baseline captured : ❌ **non** — la capture réelle est locale et doit être exécutée par l'opérateur avec ses credentials fixture, hors CI
- `Sb_UI_04.1` reste **bloqué** jusqu'à baseline P0 réellement capturée localement, OU dérogation opérateur explicite (**non accordée à ce stade**)

## 2. Fichiers créés / modifiés

### Créés

| Fichier | Rôle | Lignes |
|---|---|---|
| `scripts/visual_baseline_matrix.py` | Matrice déterministe des écrans à capturer (P0=8 slugs × 2 viewports = 16, P1=7×2=14, P2=3×2=6). Pure Python, aucun import Playwright, aucun side effect. | 213 |
| `scripts/visual_baseline_capture.py` | CLI Playwright avec `--dry-run`, `--priority`, `--viewport`, `--base-url`, `--out-dir`, `--state-file`, `--strict-p0`. Import Playwright lazy (uniquement en capture réelle). | 232 |
| `tests/test_visual_baseline_matrix.py` | 92 tests unitaires : structure matrice, kebab-case, viewports, chemin sortie, build_plan, env vars, security invariants. | 220 |
| `tests/test_visual_baseline_capture_cli.py` | Tests CLI : dry-run, anti-secret (arguments interdits, canary env leak), strict mode, dry-run sans Playwright. | 190 |
| `docs/SPRINT_Sb_UI_11_1_SCREENSHOT_TOOLING_BUILD_REPORT.md` | Ce rapport. | — |

### Modifiés

| Fichier | Delta |
|---|---|
| `.gitignore` | +5 lignes : `baseline/`, `test-results/visual-baseline/` (les `env.baseline` et `var/visual-baseline/` sont déjà couverts par `.env.*` et `/var/` existants — commentaire explicite ajouté) |
| `pyproject.toml` | +8 lignes : extra `[baseline]` avec `playwright>=1.40` — installation on demand via `pip install -e '.[baseline]'`, jamais en CI |
| `docs/strategy/SPEC_REGISTRY.md` | Sb_UI_11.1 🟢 DELIVERED pending review |
| `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` | Sb_UI_11.1 livré, prochaine action = capture P0 locale, `Sb_UI_04.1` reste bloqué |

## 3. Dépendance ajoutée

**Playwright** comme **extra optionnel** dans `pyproject.toml` :

```toml
baseline = [
    "playwright>=1.40",
]
```

- **Non ajouté** à `requirements.txt` / `requirements-lock.txt` — l'app runtime n'a aucune dépendance à Playwright
- **Non installé en CI** — la CI valide uniquement matrice + CLI + tests (aucun `python -m playwright install chromium` requis)
- **Installation opérateur :**
  ```
  pip install -e '.[baseline]'
  python -m playwright install chromium
  ```

## 4. Pourquoi CI complète attendue

Ce sprint touche :

- `scripts/` (2 nouveaux fichiers)
- `tests/` (2 nouveaux fichiers)
- `pyproject.toml` (dépendance ajoutée)
- `.gitignore` (mise à jour)

**Aucun de ces chemins n'est sous `docs/`.** Le path filter `Sb_OPS.ci-path-filter` (`paths-ignore: ['docs/**']`) **ne s'applique pas**. La CI va donc jouer :

- lint (ruff budget, bandit, actionlint, shellcheck, pip-audit, gitleaks, spec protocol, auth scope matrix)
- pytest + QA scripts (avec les 92 nouveaux tests + suite complète existante)
- SonarCloud

**Durée attendue :** ~22-25 min (aligné avec les runs CI complets précédents observés).

**Aucune installation Chromium en CI** — Playwright reste extra optionnel non installé côté CI.

## 5. Commandes locales

### Dry-run (recommandé en premier)

```bash
python scripts/visual_baseline_capture.py --dry-run --priority P0
```

**Sortie type :**

```
Environment status (values redacted):
  AUREN_BASELINE_USERNAME=<missing>
  AUREN_BASELINE_PASSWORD=<missing>
  AUREN_BASELINE_ACTIVE_SESSION_ID=<missing>
  AUREN_BASELINE_DONE_SESSION_ID=<missing>
  AUREN_BASELINE_TEMPLATE_SLUG=<missing> (optional)
Dry-run: 16 capture(s) planned.
  [P0] home-authenticated/mobile (360×640) → var/visual-baseline/home-authenticated/mobile-authenticated.png | auth=True | fixture=db.user.with_active_session | route_template=/
  [P0] home-authenticated/desktop (1440×900) → var/visual-baseline/home-authenticated/desktop-authenticated.png | ...
  ... (16 lines total)
```

### Capture réelle locale

**Prérequis :**

```bash
pip install -e '.[baseline]'
python -m playwright install chromium
```

**Set env vars (jamais dans un fichier committé) :**

Créer un fichier local `.env.baseline` (git-ignored). Le contenu utilise des valeurs de fixture locale — jamais un compte prod :

```
AUREN_BASELINE_USERNAME=<fixture-username-local>
AUREN_BASELINE_PASSWORD=<fixture-random-secret-local>
AUREN_BASELINE_ACTIVE_SESSION_ID=<id-from-local-fixture>
AUREN_BASELINE_DONE_SESSION_ID=<id-from-local-fixture>
```

Source-le avant capture :

```bash
set -a
source .env.baseline
set +a

# Lance l'app locale sur un DB fixture séparé, puis :
python scripts/visual_baseline_capture.py \
    --base-url http://127.0.0.1:8000 \
    --priority P0 \
    --viewport all \
    --out-dir var/visual-baseline
```

### Strict mode (fail-fast si env manquantes)

```bash
python scripts/visual_baseline_capture.py --dry-run --priority P0 --strict-p0
```

## 6. Dry-run output résumé

Aligné avec la spec §5 : **8 slugs P0** × **2 viewports** = **16 screenshots planifiés**.

**Écart vs Sx_UI_11 §5 (14 P0 minimum) :** 16 > 14, dépasse le minimum. Documenté dans `visual_baseline_matrix.py` : le split `home-authenticated` / `home-no-active-session` + `session-detail-active` / `session-detail-done` ajoute 4 screenshots (vs 12 sans split) — protège les empty states et les 2 states critiques de la session detail. Sx_UI_11 spec §5 §OQ-AB permet ce dépassement V1.

## 7. Anti-secret rule (implémentation)

### Interdictions CLI (hard, refusées avant argparse)

Tout argument dont le nom contient l'un des tokens suivants est **rejeté** avec exit code `2` avant tout parsing :

- `password`
- `token`
- `secret`
- `basic-auth-password`
- `api-key`, `apikey`

Le message d'erreur ne contient **jamais** la valeur — uniquement le nom du flag interdit.

### Valeurs via env uniquement

- Auth : `AUREN_BASELINE_USERNAME`, `AUREN_BASELINE_PASSWORD`
- Session IDs : `AUREN_BASELINE_ACTIVE_SESSION_ID`, `AUREN_BASELINE_DONE_SESSION_ID`
- Optionnel : `AUREN_BASELINE_TEMPLATE_SLUG`

### Redaction stdout/stderr

Le CLI n'affiche jamais la **valeur** de ces variables. Il affiche uniquement `<set>` ou `<missing>` (bracketé pour empêcher la confusion avec la valeur).

### Tests anti-leak

Un test canary set une valeur `CANARY_MUST_NEVER_LEAK_XYZ_123` dans les 4 env vars, capture stdout+stderr du dry-run, et **échoue** si la canary apparaît dans la sortie. ✅ passing.

### Fixture user local uniquement

Convention documentée : compte fixture `baseline_YYYYMMDD_HHMM` créé localement, jamais un compte prod (`martin_prod_smoke_*`, ou tout ce qui pointe vers `spignos.com`). Test `test_no_prod_account_referenced` verrouille l'invariant dans la matrice.

## 8. Tests ajoutés

**92 tests unitaires, tous passent en 0.05s** (sans Chromium installé) :

### `tests/test_visual_baseline_matrix.py` (72 tests dont 54 paramétrés)

- `TestP0Matrix` : les 8 slugs P0 requis présents, ≥14 screenshots, chaque P0 target mobile + desktop
- `TestEntryStructure` : chaque entrée a tous les champs requis, slug kebab-case strict, route commence par `/`
- `TestViewportSize` : dimensions correctes, viewport inconnu → `ValueError`
- `TestOutputPath` : convention `{out_dir}/{slug}/{viewport}-{state}.png`, refus kebab-case invalide, refus viewport inconnu, state suffix override
- `TestBuildPlan` : P0 × all = 16 plans, filtres mobile/desktop, plans déterministes
- `TestEnvVarNames` : préfixes `AUREN_BASELINE_*` respectés
- `TestSecurityInvariants` : aucune valeur credential encodée dans la matrice, aucun compte prod référencé

### `tests/test_visual_baseline_capture_cli.py` (20 tests)

- `TestDryRun` : liste tous les slugs P0, aucun fichier créé, filtre viewport mobile-only
- `TestAntiSecret` (8 paramétrés) : `--password`, `--token`, `--secret`, `--basic-auth-password`, `--api-key`, `--apikey`, `-password` — tous rejetés, valeurs jamais loggées
- Test canary : valeur env `CANARY_MUST_NEVER_LEAK_XYZ_123` **absente** de stdout/stderr après dry-run
- `TestStrictMode` : `--strict-p0` fail exit 4 si env session manquante, pass si tout set
- `TestPlaywrightNotRequiredForDryRun` : dry-run fonctionne même avec `sys.modules['playwright']` bloqué

## 9. DoD local

| Check | Résultat |
|---|---|
| `python scripts/visual_baseline_capture.py --dry-run --priority P0` | ✅ 16 captures listées, env `<missing>`, aucun fichier créé |
| `pytest tests/test_visual_baseline_matrix.py tests/test_visual_baseline_capture_cli.py -q` | ✅ **92 passed in 0.05s** |
| `python scripts/check_ruff_budget.py` | ✅ **OK (534 ≤ 548)** — +5 warnings vs baseline précédent, sous budget |
| `python scripts/check_spec_protocol.py` | ✅ **OK** (35 reports, 32 specs) |
| `bandit scripts/visual_baseline_*.py` | ✅ **0 issues** |
| `git status --short -- app migrations .github/workflows/deploy-production.yml` | ✅ **vide** (zones interdites intactes) |
| Aucun PNG dans `git status` | ✅ **vide** |
| Aucun secret hardcodé dans scripts/tests (seuls canaries test-only) | ✅ **confirmé** |

## 10. Limitations V1

- **CI ne capture pas.** Playwright n'est pas installé en CI V1 ; seules les logiques CLI + matrice + tests structurels sont validées.
- **Fixture DB non créée.** La spec §7 énumère 6 fixture IDs, mais leur seed déterministe est reporté à un futur `Sb_UI_11.2` si nécessaire. V1 opérateur peut créer les données manuellement via `/register`, `/library` etc. sur une DB locale.
- **Auth strategy = env vars seules V1.** Un futur `Sb_UI_11.2` peut ajouter `--state-file` (Playwright `storage_state`) pour éviter le login à chaque run.
- **Empilement no-JS + reduced-motion hors-scope V1.** Sx_UI_11 §9 les repousse à Sb_UI_11.2 optionnel.
- **Diff visual comparator hors-scope V1.** La revue humaine primaire suffit V1 (Sx_UI_11 §12). Un futur `Sb_UI_11.2` peut ajouter un `diff.py` avec seuils configurables.

## 11. Statut baseline

| Item | Statut |
|---|---|
| Tooling available | ✅ **yes** |
| P0 baseline captured | ❌ **no** — capture locale reste à exécuter par l'opérateur avec ses credentials fixture |
| `Sb_UI_04.1` build unblocked | ❌ **non** — baseline P0 requise (fichiers présents dans `var/visual-baseline/` ou release tag) OU dérogation opérateur explicite documentée |

**Aucune dérogation baseline n'est accordée dans ce sprint.** Le chemin canonique passe par capture locale des 16 P0 screenshots avant tout `Sb_UI_04.1`.

## 12. Prochaine action recommandée

**Capture P0 locale par l'opérateur** :

1. `pip install -e '.[baseline]'`
2. `python -m playwright install chromium`
3. Créer `.env.baseline` local (git-ignored) avec fixture user credentials
4. Lancer app locale sur DB fixture
5. `python scripts/visual_baseline_capture.py --base-url http://127.0.0.1:8000 --priority P0 --viewport all --out-dir var/visual-baseline`
6. Uploader les 16 PNG comme artefact CI **OU** release tag `baseline-preauren-YYYYMMDD`
7. **Alors seulement**, opérateur peut ouvrir `Sb_UI_04.1_CSS_FOUNDATION_BUILD`

**Alternative :** dérogation opérateur explicite documentée dans un sprint override léger pour démarrer `Sb_UI_04.1` sans baseline. Non recommandé.

## 13. Références

- Spec source : `docs/strategy/Sx_UI_11_SCREENSHOT_REGRESSION_BASELINE_SPEC.md`
- Spec cible reskin : `docs/strategy/Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC.md`
- Registry : `docs/strategy/SPEC_REGISTRY.md` §1sexies
- Roadmap : `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`
- Path filter : `docs/SPRINT_Sb_OPS_ci_path_filter_BUILD_REPORT.md`
- Focus mode précurseur : `docs/strategy/Sx_29_CLOSURE_REPORT.md`

## 14. Verdict

✅ **READY FOR HUMAN REVIEW.**

Tooling minimal livré : matrice + CLI + 92 tests, avec règle anti-secret hard testée par canary. Aucun app code touché. Aucun screenshot committé. Aucun Chromium installé en CI. `Sb_UI_04.1` reste bloqué en attendant capture P0 locale opérateur ou dérogation explicite.
