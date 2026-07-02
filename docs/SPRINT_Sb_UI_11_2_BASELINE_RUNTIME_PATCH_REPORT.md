# Sprint Report — Sb_UI_11.2 Baseline Runtime Integration Patch

**Sprint ID :** `Sb_UI_11.2`
**Type :** **BUILD OPS/UI PATCH** — hors-cycle, patch d'intégration runtime
**Date :** 2026-07-02
**Auteur :** opérateur (Martin Feldmann) + agent Claude Code
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Verdict :** ✅ **READY FOR HUMAN REVIEW**
**CI attendue :** ✅ **complète au push** (fichiers hors `docs/`)

---

## 1. Pourquoi ce patch existe

`Sb_UI_11.1` a livré le tooling nu : matrice + CLI Playwright + tests + anti-secret. La CI est verte. Mais la **capture P0 locale opérateur** a révélé une faiblesse d'intégration :

- l'app dispose déjà d'un environnement fonctionnel via `.env`
- `DATABASE_URL` pointe déjà sur `sqlite:///./var/workout.db`
- la DB locale contient déjà les tables applicatives
- le service d'auth crée déjà un cookie signé `session_token` via `itsdangerous.URLSafeTimedSerializer(app_secret_key)`
- la route `POST /sessions` existe déjà
- **le CLI `visual_baseline_capture.py` exige un `--state-file` mais ne sait pas préparer l'état runtime**

## 2. Erreurs opérateur observées

Frictions cumulées pendant la tentative de capture P0 manuelle :

1. `var/workout-baseline.db` isolée était une fausse piste : pas de table `workout_sessions` (aucune migration jouée hors init).
2. La bonne DB reste `var/workout.db` via `DATABASE_URL` de `.env` existant.
3. La DB locale n'avait qu'une session `completed`, aucune session `in_progress` — impossible de capturer `session-detail-active`.
4. Les exports manuels shell avec placeholders `<ID_IN_PROGRESS>` provoquaient des erreurs zsh.
5. Un script heredoc avec `input()` provoquait `EOFError` selon le shell.
6. `auth-state.json` manquant → `FileNotFoundError` en Playwright.
7. Le CLI ne prépare ni l'auth ni les sessions ni le storage_state.

## 3. Décision : ne pas créer d'environnement parallèle

Le patch **réutilise** l'app runtime existant plutôt que d'introduire un environnement baseline parallèle :

- Lecture directe de `app.config.get_settings()` → `app_env`, `database_url`, `app_secret_key`
- Utilisation de `app.database.SessionLocal` — jamais un nouvel `create_engine`
- Utilisation de `app.services.session_builder.instantiate_session` — jamais de bricolage SQL manuel
- Génération de storage_state avec `itsdangerous.URLSafeTimedSerializer(app_secret_key)` — contrat identique à `app.services.auth._serializer`, cookie accepté verbatim par `get_user_id_from_cookie`
- Refus catégorique de tourner si `app_env == "production"` ou DB URL non-locale (sqlite:/// ou postgres 127.0.0.1/localhost autorisés seulement)

## 4. Fichiers créés / modifiés

### Créés

| Fichier | Rôle | Lignes |
|---|---|---|
| `scripts/visual_baseline_runtime.py` | CLI `prepare` (fixtures + storage_state + runtime.json) + `verify` (contrôle post-hoc). Refuse prod, refuse DB non-locale, mot de passe fixture aléatoire jamais loggé. | ~380 |
| `tests/test_visual_baseline_runtime.py` | 30 tests unitaires : safety guards, password strength, cookie roundtrip avec app.services.auth, storage_state shape, verify command, anti-secret CLI, prepare dry-run sans DB. | ~250 |
| `docs/SPRINT_Sb_UI_11_2_BASELINE_RUNTIME_PATCH_REPORT.md` | Ce rapport. | — |

### Modifiés

| Fichier | Delta |
|---|---|
| `scripts/visual_baseline_capture.py` | + `--runtime-file` argument, + `_load_runtime_file`, + `_resolve_state_file`, `_resolve_route` prend un `runtime` optional (runtime > env fallback), `strict-p0` relaxé si runtime fourni, `_capture_real` applique state_file uniquement aux entrées `auth_required=True` |
| `tests/test_visual_baseline_capture_cli.py` | + 5 classes de tests (`TestRuntimeFileLoading`, `TestResolveRoute`, `TestResolveStateFile`, `TestRuntimeFileInDryRun` — ~15 tests), test canary anti-secret raffiné (credential vs public IDs) |
| `docs/strategy/SPEC_REGISTRY.md` | Sb_UI_11.2 🟢 DELIVERED pending review |
| `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` | Sb_UI_11.2 livré, prochaine action = capture P0 locale avec nouveau runtime CLI |

## 5. Intégration avec `.env` / `DATABASE_URL` existant

Le CLI `visual_baseline_runtime.py prepare` :

1. Charge `app.config.get_settings()` — même contrat que le serveur uvicorn
2. Refuse `app_env=production` (exit code 11) ou `app_env=prod` (alias)
3. Refuse `DATABASE_URL` non-local (exit code 12) :
   - autorisé : `sqlite:///./...`, `sqlite://`, `sqlite+*`
   - autorisé : `postgresql://` avec host `127.0.0.1` ou `localhost`
   - refusé : tout autre schéma / host distant
4. Utilise la même `SessionLocal` que l'app — même DB, même schéma

**Conséquence pour l'opérateur :** aucun `.env.baseline` à créer, aucun `DATABASE_URL` séparé à exporter. La commande respecte simplement l'`.env` existant.

## 6. Stratégie auth via cookie signé

Le CLI génère un `storage_state.json` Playwright avec le même contrat cookie que `app.services.auth` :

- Cookie name : `session_token` (`= SESSION_COOKIE` app)
- Cookie value : `URLSafeTimedSerializer(app_secret_key).dumps({"user_id": <int>})`
- `httpOnly=True`, `sameSite=Strict`, `secure=False` (local http)
- expiration : +7 jours (bien sous `SESSION_MAX_AGE = 30 jours`)

Le cookie est **jamais loggé**. Test unitaire `test_signed_cookie_roundtrip_with_app_auth` valide que le cookie est accepté verbatim par un serializer configuré avec la même clé — garantie contractuelle sans mocker l'app.

**Permissions fichier :** `chmod 600` sur `auth-state.json` et `runtime.json` (best effort — silent no-op sur FS non-POSIX).

## 7. Stratégie session fixture locale

- User baseline : `baseline_local`
  - Créé si absent avec password random 32 chars alphanumériques, **jamais loggé**
  - Réutilisé si présent (idempotent)
- Session `in_progress` : réutilisée si existe pour ce user, sinon `instantiate_session(db, template=push-a, user_id=...)` puis `db.add()` + `db.commit()`
- Session `completed` : idem, mais `status = "completed"` flippé avant commit (baseline visuelle statique, pas une session métriquement valide)
- Template fallback : si `push-a` absent, premier `WorkoutTemplate` disponible ; si aucun template, exit code 13

## 8. Commandes opérateur finales

**Étape 1 — Préparation runtime (une fois) :**

```bash
# Prérequis
pip install -e '.[baseline]'
python -m playwright install chromium

# Lancer l'app locale (DB = var/workout.db par défaut, DATABASE_URL de .env)
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# Dans un autre terminal :
python scripts/visual_baseline_runtime.py prepare \
    --base-url http://127.0.0.1:8000 \
    --out-dir var/visual-baseline
```

**Sortie attendue (aucun secret loggé) :**

```
Baseline runtime prepare
  base_url         : http://127.0.0.1:8000
  app_env          : dev
  db               : sqlite:./var/workout.db
  out_dir          : var/visual-baseline

Runtime prepared (no secrets logged):
  user             : id=1 (created=True)
  active_session_id: 42 (created=True)
  done_session_id  : 43 (created=True)
  state_file       : var/visual-baseline/auth-state.json
  runtime_file     : var/visual-baseline/runtime.json
```

**Étape 2 — Capture P0 :**

```bash
python scripts/visual_baseline_capture.py \
    --base-url http://127.0.0.1:8000 \
    --priority P0 \
    --viewport all \
    --out-dir var/visual-baseline \
    --runtime-file var/visual-baseline/runtime.json
```

**Aucun `.env.baseline`, aucun `read -rs`, aucun export shell manuel.**

**Étape 3 — Vérifier (optionnel) :**

```bash
python scripts/visual_baseline_runtime.py verify \
    --runtime-file var/visual-baseline/runtime.json

find var/visual-baseline -name "*.png" | sort
find var/visual-baseline -name "*.png" | wc -l  # attendu ≥14
```

## 9. Limites V1

- **1 seul user baseline** — la matrice V1 ne teste pas de scénarios multi-user (leaderboard, squads). Ces P2 sont différables.
- **Session `completed` avec status flippé** — sans set logs ni logique de completion réelle. Suffit pour un empty state du done view, mais insuffisant pour une baseline riche du coach report post-séance. À affiner en `Sb_UI_11.3` si nécessaire.
- **Pas de reset destructif** — le CLI réutilise les sessions existantes plutôt que de les nettoyer. Pour une baseline vraiment déterministe pixel-perfect, il faudrait supprimer et recréer. Non requis pour la V1 « revue humaine primaire » (Sx_UI_11 §12).
- **Pas de fallback multi-viewport session-detail** — la même session apparaît pour mobile ET desktop. Suffit pour V1.
- **Env var fallback conservé** pour compat Sb_UI_11.1 — deprecable en Sb_UI_11.3 si l'opérateur ne l'utilise plus.

## 10. Statut

| Item | Statut |
|---|---|
| Runtime tooling available | ✅ **yes** (matrice + runtime prepare/verify + capture --runtime-file) |
| Capture réellement exécutée dans ce sprint | ❌ **no** — l'exécution reste opérateur, par design |
| P0 baseline captured | ❌ **no** — pending local run |
| `Sb_UI_04.1` build unblocked | ❌ **no** — baseline P0 doit être capturée par opérateur avec le nouveau runtime |

## 11. DoD local

| Check | Résultat |
|---|---|
| `pytest tests/test_visual_baseline_*.py -q` | ✅ **145 passed in 0.08 s** (30 nouveaux runtime + 15 nouveaux capture --runtime-file + suite existante) |
| `python scripts/check_ruff_budget.py` | ✅ **OK (542 ≤ 548)** — +8 warnings vs baseline précédent, sous budget |
| `python scripts/check_spec_protocol.py` | ✅ **OK** (35 reports, 32 specs) |
| `bandit scripts/visual_baseline_runtime.py` | ✅ **0 issues** |
| `git status --short -- app migrations .github/workflows/deploy-production.yml app/static app/templates app/routers app/services app/models` | ✅ **vide** |
| `.github/workflows/ci.yml` intact | ✅ |
| Aucun PNG dans `git status` | ✅ |
| Aucun secret / cookie / token hardcodé dans le diff | ✅ (canaries test-only) |

## 12. CI attendue

Ce push touche :

- `scripts/visual_baseline_runtime.py` (nouveau)
- `scripts/visual_baseline_capture.py` (patch --runtime-file)
- `tests/test_visual_baseline_runtime.py` (nouveau)
- `tests/test_visual_baseline_capture_cli.py` (patch tests --runtime-file)
- `docs/` (rapport + registry + roadmap)

**Aucun de ces chemins hors `docs/` ne matche `paths-ignore: ['docs/**']`.** La CI complète va donc se déclencher :

- lint (ruff budget 542, bandit 0 issues, actionlint, shellcheck, pip-audit, gitleaks, spec protocol, auth scope matrix)
- pytest + QA scripts (avec 145 tests baseline verts)
- SonarCloud

**Durée attendue :** ~22-25 min compute.

**Aucune installation Chromium en CI** — Playwright reste extra optionnel non-installé côté runner.

## 13. Prochaine action recommandée

**Capture P0 locale opérateur** avec la nouvelle chaîne runtime → capture, sans `.env.baseline` ni exports shell manuels.

Une fois les 14+ P0 screenshots dans `var/visual-baseline/` :

1. Upload artefact CI OU release tag `baseline-preauren-YYYYMMDD`
2. Documenter la baseline dans un mini-rapport `docs/BASELINE_P0_CAPTURED_YYYYMMDD.md`
3. **Alors seulement**, opérateur peut ouvrir `Sb_UI_04.1_CSS_FOUNDATION_BUILD` sur override explicite

## 14. Références

- Sprint précédent : `docs/SPRINT_Sb_UI_11_1_SCREENSHOT_TOOLING_BUILD_REPORT.md` + acceptance
- Spec source : `docs/strategy/Sx_UI_11_SCREENSHOT_REGRESSION_BASELINE_SPEC.md`
- Spec cible reskin : `docs/strategy/Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC.md`
- App auth contract : `app/services/auth.py` (`SESSION_COOKIE`, `_serializer`)
- App session builder : `app/services/session_builder.py::instantiate_session`
- App config : `app/config.py::get_settings`
- CI cost optimization : `docs/SPRINT_Sb_OPS_ci_path_filter_BUILD_REPORT.md`

## 15. Verdict

✅ **READY FOR HUMAN REVIEW.**

Patch minimal, intégré à l'app existant sans dupliquer la config. 145/145 tests verts, sécurité pass (bandit + ruff + anti-secret + refus prod + refus DB non-locale). Aucun app code UI touché. Aucun screenshot capturé côté sprint (par design). `Sb_UI_04.1` reste bloqué jusqu'à capture P0 locale opérateur ou dérogation explicite (non accordée).
