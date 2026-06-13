# SPIGNOS — Sx_26 Engineering Control Plane & Anti-Drift Hardening Spec

**Date :** 2026-06-01
**Type :** SPEC ONLY — gouvernance industrielle avant prochains cycles produit.
**Statut :** v1 draft, à valider avant build Sb_26.x.
**Prérequis :** Cycle Sx_24 livré, Sb_24.next.reco déployé, Synthesis v1 disponible.

---

## 1. Executive summary

SPIGNOS est un produit fonctionnel discipliné mais son **plan de contrôle d'ingénierie** est sous-formalisé pour la trajectoire SaaS : le deploy reste un workflow_dispatch manuel sans manifeste signé, les linters tournent en advisory, le monitoring runtime est absent, les dépendances ne sont pas auto-auditées, la matrice de tests n'est pas catégorisée par typologie, et le protocole spec-driven Claude reste tribal (documenté implicitement dans les rapports mais non codifié comme contrat).

Sx_26 spécifie la **couche de gouvernance industrielle** qui rendra les prochains cycles produit reproductibles, auditable et résistants au drift agent. Aucun code applicatif ni workflow n'est modifié dans ce sprint — Sx_26 produit le contrat, Sb_26.1 → Sb_26.7 l'implémenteront en 7 lots ciblés.

**Cibles atteignables par Sx_26+Sb_26.x** :
- CI passe de "lint advisory" à "lint required mode-Z" avec quota explicite de warnings tolérés
- Deploy production produit un **deploy manifest** signé persistant (audit trail)
- Monitoring runtime baseline : uptime externe + Sentry + alerting d'incident
- Sécurité baseline : rate limiting `/register`+`/login`, headers sécurité audités, dependency auto-audit
- Tests classifiés par typologie + quality gates différenciés
- Templates spec-driven figés (`SPEC_TEMPLATE.md`, `BUILD_REPORT_TEMPLATE.md`)
- Rollback drill scripté + checklist release

**Aucune migration Postgres, aucune migration React Native, aucun changement produit dans ce périmètre.**

## 2. État actuel du repo

| Élément | Valeur |
|---|---|
| Branche active | `claude/sprint-reporting-fitness-app-V7Qr6` |
| Last commit | `1109e8d` (Sb_24.next.reco) |
| Python | 3.11 (pinned via `pyproject.toml`) |
| Volume | ~12 700 LoC `app/`, ~3 500 LoC `tests/`, ~3 000 LoC `scripts/` + `migrations/` |
| Tests | 907 passing, 92 fichiers `tests/test_*.py` |
| Coverage | 89.97 % (SonarCloud confirmé) |
| Migrations | 18 fichiers Alembic, head `5g8d3b9c0e21` |
| Specs Sx_ formelles | 12 docs `docs/strategy/SPIGNOS_*_SPEC*.md` |
| Sprint reports | ~35 docs `docs/SPRINT_*_REPORT.md` |
| Workflows GitHub Actions | 2 (`ci.yml` 195 LoC, `deploy-production.yml` 111 LoC) |
| Scripts deploy | `deploy_prod.sh` 268 LoC, `deploy_from_github_actions.sh` 71 LoC, `smoke_deploy.sh` 119 LoC |
| Linters | ruff (advisory) + bandit (advisory) + SonarCloud (required) |
| Branch protection | required checks = `pytest + QA scripts` + `SonarCloud`. `force-push` interdit. |
| Monitoring runtime | aucun |
| Logs centralisés | aucun |
| Dependency auto-audit | aucun (pas de dependabot) |

## 3. Cartographie CI existante

### 3.1 — Structure `ci.yml`

| Trigger | `pull_request` + `push` sur `main` + branche active |
|---|---|
| Permissions | `contents: read` |
| Concurrence | `ci-${{ github.ref }}` cancel-in-progress |

| Job | Type | Statut | Durée typique |
|---|---|---|---|
| `pytest + QA scripts` | required | bloquant | ~4min30 |
| `ruff + bandit (advisory)` | advisory | `continue-on-error: true` partout | ~30s |
| `SonarCloud` | required | bloquant | ~50s |

### 3.2 — Composants du job `test`

- `actions/checkout@v4`
- `actions/setup-python@v5` python `3.11` + pip cache
- `pip install -r requirements.txt` + dev deps explicites
- `pytest --cov=app --cov-report=xml --cov-report=term`
- `sed` post-process pour préfixer `coverage.xml` (workaround SonarCloud, Sb_20.x)
- `upload-artifact@v4` coverage-xml
- `python scripts/catalog_qa.py`
- `python scripts/machine_atlas_qa.py`
- `python scripts/check_alembic_drift.py`

### 3.3 — Composants du job `lint`

- `ruff check . --output-format=github` + `ruff format --check .` (advisory)
- `bandit -r app/ -ll -f screen` (advisory)
- `ruff check . --output-format=json --output-file=ruff-report.json` (artifact)
- `bandit -r app/ -f json -o bandit-report.json` (artifact)
- Upload `linter-reports` artifact

### 3.4 — Composants du job `sonar`

- `needs: [test, lint]`
- Download artifacts `coverage-xml` + `linter-reports`
- `SonarSource/sonarcloud-github-action@v2`
- Required status check depuis Sb_20.5
- Quality Gate `Spignos Way` — Coverage ≥ 70 %, ratings A, hotspots 0

### 3.5 — Couvertures CI

| Aspect | État |
|---|---|
| Tests Python | ✅ |
| Coverage XML pour Sonar | ✅ (sed workaround) |
| QA catalogue (`catalog_qa.py`, `machine_atlas_qa.py`) | ✅ |
| Drift Alembic (`check_alembic_drift.py`) | ✅ |
| Linters de code | ⚠️ advisory uniquement |
| Linters de templates Jinja | ❌ |
| Linters CSS | ❌ |
| Sec scan dépendances Python | ❌ |
| Sec scan images Docker | n/a (pas de Docker) |
| Audit secrets in code (truffleHog / gitleaks) | ❌ |
| Workflow file lint (actionlint) | ❌ |
| Shell script lint (shellcheck) | ❌ |
| Tests parallèles (pytest-xdist) | ❌ |
| Tests par catégorie / smoke pré-merge | ❌ |
| Caching `pip` | ✅ (via setup-python cache) |
| Caching `~/.cache/pre-commit` | n/a (pas de pre-commit) |
| Node 20 deprecation warnings | ⚠️ checkout@v4 + download-artifact@v4 |

## 4. Cartographie CD / production deploy

### 4.1 — Workflow `deploy-production.yml`

| Trigger | `workflow_dispatch` MANUEL UNIQUEMENT |
|---|---|
| Inputs | `ref` (SHA full ou branche), `skip_smoke` (bool, urgence) |
| Permissions | `contents: write` (pour pousser `deploy/prod/<tag>`) |
| Concurrence | `production-deploy` cancel-in-progress: **false** (serialise) |
| Environment | `production` (audit trail GitHub) |
| Timeout | 15 min |

### 4.2 — Étapes deploy-production.yml

1. Checkout requested ref (`fetch-depth: 0`)
2. Resolve full SHA
3. SSH key setup
4. SSH known_hosts via secret fingerprint
5. SSH execute `deploy_from_github_actions.sh <SHA>` sur le VPS
6. Tag `deploy/prod/YYYY-MM-DD-HHMM-<sha>` poussé au repo
7. Report failure (annotation GitHub)

### 4.3 — Chaîne sur le VPS

```
deploy_from_github_actions.sh
  ├─ sanity check SHA regex 7-40 hex
  ├─ APP_DIR=/opt/workout-session-tracking, APP_USER=ubuntu
  ├─ git fetch origin
  ├─ git reset --hard <SHA>
  ├─ SKIP_GIT_PULL=1 export (évite double pull dans deploy_prod.sh)
  └─ exec deploy_prod.sh

deploy_prod.sh (268 LoC, modulaire)
  ├─ step "Preflight checks"          : git status, app dir exists, service exists
  ├─ step "Recording pre-deploy state": PRE_SHA capture
  ├─ step "Installing dependencies"   : pip install -r requirements.txt
  ├─ step "Checking schema drift"     : python -m scripts.check_alembic_drift
  ├─ step "Running database migrations": alembic upgrade head (output surfaced on failure Sb_24.1 fix)
  ├─ step "Seeding reference catalog" : python scripts/seed_db (idempotent)
  ├─ step "Verifying database connectivity"
  ├─ step "Restarting service"         : systemctl restart workout.service
  └─ step "Running smoke deploy"       : smoke_deploy.sh (sauf si skip_smoke)
```

### 4.4 — Backup automatique

Avant migration, `deploy_prod.sh` copie `var/workout.db` en `var/backups/workout_pre_<SHA>_YYYYMMDD_HHMMSS.db`. Rotation : pas formalisée (rétention manuelle).

### 4.5 — Garde-fous existants

- Concurrent dispatch sérialisé (`cancel-in-progress: false`)
- `set -euo pipefail` partout
- Validation SHA regex (7-40 hex)
- Backup pré-migration
- Smoke test post-deploy
- Deploy tag poussé au repo (audit trail)
- Sudoers restreint sur le VPS au seul script `deploy_from_github_actions.sh`

### 4.6 — Manques

| Manque | Conséquence |
|---|---|
| Pas de **deploy manifest** signé (qui a deployé quoi, quand, depuis quel SHA, vers quel SHA) | Pas d'audit trail consultable hors GitHub Actions history (purge possible) |
| Pas de health checks périodiques post-deploy (uniquement smoke immédiat) | Une dégradation 30 min après deploy n'est pas détectée |
| Pas de `pre-deploy validation` séparée (qui pourrait être run en CI sur le SHA cible avant le dispatch) | Le deploy peut partir sur un SHA qui n'a jamais vu la CI verte (push direct hors PR par exemple) |
| Pas de **dry-run mode** (--dry-run sur deploy_prod.sh) | Tester le pipeline impose un vrai deploy |
| Pas de **canary** ou rolling deploy | n/a single-instance V1, acceptable |
| Rotation backups non formalisée | Disque qui se remplit à terme |
| Pas de notification post-deploy (Discord/Slack/email) | L'humain doit consulter GitHub Actions pour savoir |

## 5. Cartographie tests

### 5.1 — Inventaire

| Catégorie | Fichiers | Estim. nb tests |
|---|---|---|
| **E2E HTTP** via TestClient | ~30 (`test_register_profile.py`, `test_session_management.py`, `test_session_done_pastilles.py`, `test_coach_report.py`, `test_leaderboard.py`, etc.) | ~150 |
| **Unitaire services** | ~40 (`test_implicit_signal.py`, `test_reco_zone_freshness.py`, `test_quality_score_v2.py`, `test_substitution_tiered.py`, etc.) | ~600 |
| **Sécurité / auth** | `test_security.py`, `test_auth.py`, `test_password_reset.py`, `test_squad_routes.py` | ~50 |
| **Drift / migrations** | `test_alembic_drift.py`, `test_scoring_version_migration.py` | ~10 |
| **Catalogue / atlas QA** | `test_catalog_integrity.py`, `test_catalog_substitution_*.py`, `test_machine_atlas.py` | ~40 |
| **Reco engine** | `test_recommendation*.py` (4 fichiers) | ~50 |
| **Behavioral / KPI** | `test_behavioral.py`, `test_board_kpis.py`, `test_kpis.py`, `test_progression_hint.py` | ~30 |
| **Export / persistance** | `test_export.py`, `test_csv_export.py`, `test_export_kind_and_confidence.py` | ~15 |
| **Réservé acceptance V1** | `test_v1_acceptance.py` (ignoré en CI, requires local VS Code) | n/a |
| **Total** | **92 fichiers** | **907 tests** |

### 5.2 — Fixtures et conftest

- `tests/conftest.py` — `client` fixture qui setup une `WorkoutSession` BD SQLite éphémère, crée user `testuser`/`testpass`, log via `/login`, retourne TestClient logged-in
- `tests/helpers.py` — utilitaires factorisés
- `tests/test_v1_acceptance.py` — **ignoré en CI** car requires `code .` local

### 5.3 — Couvertures de typologie

| Typologie | Présent ? |
|---|---|
| Unitaires | ✅ |
| Intégration (TestClient + BD éphémère) | ✅ |
| E2E via Playwright/Selenium navigateur | ❌ |
| Contract tests (Pact) | n/a (no external) |
| Load tests | ❌ |
| Mutation tests | ❌ |
| Property-based (Hypothesis) | ❌ |
| Snapshot tests templates Jinja | ❌ |
| Tests dropdown migration upgrade/downgrade roundtrip | ⚠️ partial (1 test dans `test_scoring_version_migration.py`) |
| Security regression tests (CWE-20, CWE-22) | ⚠️ partial (Sb_20.3) |
| Tests perf budget (latence routes) | ❌ |

### 5.4 — Manques tests

- **Mutation testing** absent — coverage 90 % mais qualité des assertions non auditée
- **Tests de migration roundtrip** (upgrade head → downgrade -1 → upgrade head) non systématiques
- **Tests perf budget** absents — pas d'alerte si `/coach-report` passe de 200ms à 5s
- **Snapshot tests templates** absents — un changement CSS qui casse silencieusement le rendu print A4 n'est pas détecté
- **Pas de catégorisation pytest marks** (`@pytest.mark.slow`, `@pytest.mark.security`) — impossible d'exécuter sous-ensemble

## 6. Cartographie migrations / Alembic drift

### 6.1 — État

- **18 migrations** Alembic (16 actives + 2 récentes Sb_24.1 + Sb_24.5.cleanup)
- Head courant : `5g8d3b9c0e21`
- `check_alembic_drift.py` — autogenerate vs Base.metadata sur DB vide en tempfile, exit 1 si diff
- `test_alembic_drift.py` — équivalent en pytest (lance la même logique)
- Convention figée : **ADD COLUMN ONLY**, jamais `UPDATE`, jamais `DROP` autre que en downgrade

### 6.2 — Garde-fous existants

- Drift check appelé en CI (job `test`)
- Drift check appelé en deploy (`deploy_prod.sh` step "Checking schema drift")
- Server-defaults sur les colonnes NOT NULL
- 2 migrations Sb_24 montrent les patterns OK : `op.add_column()` direct (pas de `batch_alter_table` sur prod)

### 6.3 — Manques

- **Pas de test downgrade roundtrip** — `alembic downgrade -1 && alembic upgrade head` non vérifié en CI
- **Pas de validation des invariants après migration** (ex : compter rows pré et post = identique)
- **Pas de simulation de migration sur BD prod-like** (la CI n'a jamais de data — un bug avec données réelles non détecté, cf incident Sb_24.1 prod failure le 31 mai)
- **Convention "no UPDATE" non auto-enforced** — un sprint futur pourrait introduire un UPDATE par erreur, aucune barrière

## 7. Cartographie sécurité

### 7.1 — Score Sonar

| Rating | Valeur |
|---|---|
| Security | A (0 vuln) |
| Security Review | A (0 hotspots) |
| Reliability | A (0 bugs) |
| Maintainability | A (105 code smells non bloquants) |

### 7.2 — Hardening livré (Sb_20.3)

- `MIN_PASSWORD_LENGTH = 8`
- `USERNAME_REGEX = ^[a-zA-Z0-9_-]+$`
- `EMAIL_REGEX = ^[^@\s]+@[^@\s]+\.[^@\s]+$`
- `/users/{username}` Path param validation déclarative
- Headers sécurité (CSP, X-Frame-Options, X-Content-Type, Referrer-Policy) mis en place

### 7.3 — Couches en place

| Couche | Statut |
|---|---|
| Cookie session signé HMAC | ✅ |
| `httponly` + `samesite=strict` | ✅ |
| Password hash bcrypt | ✅ |
| Ownership checks (`get_owned_session_or_404`, etc.) | ✅ |
| Path param validation déclarative | ✅ |
| `.env` non commité (`.gitignore` configuré) | ✅ |
| Secrets API uniquement via GitHub Secrets | ✅ |

### 7.4 — Manques sécurité

| Manque | Sévérité |
|---|---|
| Pas de **rate limiting** `/register`, `/login`, `/forgot-password` | P0 |
| Pas de **dependency auto-audit** (no dependabot, no safety) | P0 |
| Pas de **gitleaks/trufflehog** scan de l'historique | P1 |
| Pas de **CSP** strict (audit Sonar Sb_20 a accepté du laxisme V1) | P1 |
| Pas de **2FA** | P2 (V1 acceptable) |
| Pas de **session rotation** post-password-change | P2 |
| Pas de **email verification** confirmée | P2 |
| Pas de **password breach check** (HIBP k-anonymity) | P3 |
| Pas de **CAPTCHA** sur register | P3 |
| Pas de **CSRF tokens** explicites (mitigé par `samesite=strict`) | P3 |

## 8. Cartographie monitoring / observabilité

### 8.1 — État actuel

| Couche | Statut |
|---|---|
| Erreurs runtime applicatives | ❌ aucun agrégateur |
| Crash report (Sentry / Rollbar) | ❌ |
| Métriques perf (latence, RPS, taux erreur) | ❌ |
| Uptime externe (UptimeRobot / Cronitor) | ❌ |
| Logs centralisés (Loki, journald only) | ⚠️ journald via systemd, pas centralisé |
| Logs nginx | ✅ `/var/log/nginx/spignos.*` |
| Backup BD | ✅ quotidien automatisé |
| Alerting (email / Discord / push) | ❌ |
| Status page publique | ❌ |
| Dashboard interne | ❌ |
| Audit log applicatif (qui a fait quoi quand) | ⚠️ partial (creation_source télémétrie, mais pas log d'admin) |
| Tracing distribué | n/a (monolithe) |
| Healthcheck endpoint | ✅ `/healthz` (basic) et `/healthz/strict` (DB connectivity + backup dir) |

### 8.2 — Conséquence opérationnelle

Un crash de l'app, un site down, un disque qui se remplit, une migration partielle → détecté uniquement quand l'utilisateur s'en aperçoit. Documenté §8 du `VPS_MULTISITE_RUNBOOK.md` comme dette à traiter.

### 8.3 — Cible Sx_26 monitoring baseline

- Uptime externe sur les 3 sites du VPS (uptimerobot gratuit suffit V1)
- Sentry intégration côté SPIGNOS (sortants `sentry.io` uniquement)
- Alerting Discord/email sur incident
- Documenter dans le runbook les seuils de notification

## 9. Cartographie dépendances

### 9.1 — Inventaire `requirements.txt` (runtime)

```
fastapi>=0.110
uvicorn[standard]>=0.29
sqlalchemy>=2.0
alembic>=1.13
jinja2>=3.1
pydantic>=2.6
pydantic-settings>=2.2
python-multipart>=0.0.9
itsdangerous>=2.2
passlib[bcrypt]>=1.7
bcrypt>=4.0,<5
```

### 9.2 — Inventaire `pyproject.toml` (dev)

```
pytest>=8.0
pytest-cov>=5.0
coverage[toml]>=7.5
httpx>=0.27
ruff>=0.5
bandit>=1.7
```

### 9.3 — Manques

| Manque | Sévérité |
|---|---|
| Pas de **lockfile** (`requirements-lock.txt` ou `uv.lock`) | P1 — un `pip install` aujourd'hui peut tirer une version différente d'il y a 3 mois |
| Pas de **dependabot.yml** | P0 — CVE non remontées |
| Pas de **safety check** ou `pip-audit` en CI | P0 |
| Pas de **renovate** automatic PR | P2 |
| Pas de **pin version exacts** sur deps critiques | P2 |
| Pas de SBOM (CycloneDX/SPDX) | P3 |

## 10. Gaps classés P0/P1/P2/P3

### 10.1 — P0 (bloquant trajectoire SaaS, à traiter Sb_26.x)

| # | Gap | Sprint cible |
|---|---|---|
| P0.1 | Rate limiting `/register` + `/login` + `/forgot-password` | Sb_26.4 |
| P0.2 | Dependabot ou équivalent dependency auto-audit | Sb_26.4 |
| P0.3 | `pip-audit` ou `safety` en CI | Sb_26.4 |
| P0.4 | Monitoring uptime externe (uptimerobot) | Sb_26.3 |
| P0.5 | Sentry intégration runtime | Sb_26.3 |
| P0.6 | Alerting incident | Sb_26.3 |
| P0.7 | Deploy manifest signé + audit trail persistant | Sb_26.2 |

### 10.2 — P1 (qualité opérationnelle)

| # | Gap | Sprint cible |
|---|---|---|
| P1.1 | Linters required (sortir advisory) avec quota tolérance documenté | Sb_26.1 |
| P1.2 | Lockfile requirements | Sb_26.4 |
| P1.3 | Test downgrade roundtrip Alembic en CI | Sb_26.5 |
| P1.4 | Audit secrets historiques (gitleaks scan one-shot) | Sb_26.4 |
| P1.5 | Templates spec-driven `SPEC_TEMPLATE.md` / `BUILD_REPORT_TEMPLATE.md` | Sb_26.6 |
| P1.6 | Rotation backups automatisée | Sb_26.2 |
| P1.7 | Healthcheck périodique post-deploy (pas seulement smoke immédiat) | Sb_26.3 |
| P1.8 | Notification post-deploy (Discord/email) | Sb_26.3 |

### 10.3 — P2 (anti-drift moyen terme)

| # | Gap | Sprint cible |
|---|---|---|
| P2.1 | Mutation testing baseline (mutmut sur 1 service critique) | Sb_26.5 |
| P2.2 | Tests perf budget (latence routes critiques < seuil) | Sb_26.5 |
| P2.3 | actionlint (lint des workflows GitHub Actions) | Sb_26.1 |
| P2.4 | shellcheck (lint des scripts shell) | Sb_26.1 |
| P2.5 | Snapshot tests templates Jinja | Sb_26.5 |
| P2.6 | Catégorisation pytest marks | Sb_26.5 |
| P2.7 | Pre-commit hooks (ruff + bandit local fast) | Sb_26.6 |

### 10.4 — P3 (long terme, hors Sx_26)

- Mypy progressif
- Renovate auto-PR
- CSP strict
- 2FA
- Session rotation
- CAPTCHA / HIBP / CSRF tokens explicites
- SBOM
- Multi-tenancy infra
- i18n
- PWA / mobile native

## 11. Hard contracts anti-drift

Ces contrats doivent être respectés par tout sprint Sb_26.x et tout sprint futur. Les casser = red gate.

### 11.1 — Contrats CI/CD

| # | Contrat |
|---|---|
| HC-CI-1 | Le job `pytest + QA scripts` reste required. |
| HC-CI-2 | Le job `SonarCloud` reste required. |
| HC-CI-3 | Pas de retrait de step QA (catalog_qa, machine_atlas_qa, drift) sans bumper la version majeure du contrat. |
| HC-CI-4 | Le deploy production ne peut JAMAIS être déclenché par `on: push:`. Seulement `workflow_dispatch`. |
| HC-CI-5 | Le `cancel-in-progress: false` sur le job deploy reste verrouillé (sérialisation des déploiements). |
| HC-CI-6 | Le tag `deploy/prod/...` continue à être poussé à chaque deploy réussi. |
| HC-CI-7 | Le smoke test reste obligatoire — `skip_smoke` est usage exceptionnel manuel. |

### 11.2 — Contrats migrations

| # | Contrat |
|---|---|
| HC-MIG-1 | ADD COLUMN ONLY. Jamais `UPDATE` rétroactif sur lignes existantes (Sx_24 §H sacralisé). |
| HC-MIG-2 | Server-default obligatoire sur NOT NULL ajouté. |
| HC-MIG-3 | Drift check passe sur chaque commit (CI + deploy). |
| HC-MIG-4 | Pas de `batch_alter_table` avec server_default sur table peuplée (incident Sb_24.1 fix). |
| HC-MIG-5 | Backup BD pré-migration en production (déjà fait par `deploy_prod.sh`). |
| HC-MIG-6 | Une migration future qui violerait HC-MIG-1 doit être justifiée par une amend Sx_xx explicite. |

### 11.3 — Contrats historique et snapshots

| # | Contrat |
|---|---|
| HC-HIST-1 | `template_slug_snapshot`, `template_name_snapshot`, `exercise_*_snapshot` sont **figés** une fois écrits. |
| HC-HIST-2 | `substituted_name` figé une fois set. |
| HC-HIST-3 | `implicit_label`, `implicit_label_computed_at` figés à la complétion (Sx_24 §C). |
| HC-HIST-4 | `scoring_version` monotone (jamais downgradé en runtime). |
| HC-HIST-5 | Pas de réécriture historique des scores `quality_score` (le score est recalculé à la consultation mais la formule branche par `scoring_version` pour garantir l'invariance). |

### 11.4 — Contrats deploy

| # | Contrat |
|---|---|
| HC-DEPLOY-1 | Manuel `workflow_dispatch` uniquement. Pas d'auto-deploy sur push (Sx_26 maintien explicite). |
| HC-DEPLOY-2 | SSH key restreinte au user `deploy` + sudoers minimal. |
| HC-DEPLOY-3 | Le script `deploy_prod.sh` reste idempotent. |
| HC-DEPLOY-4 | Tout step `deploy_prod.sh` qui échoue surface son output (correctif Sb_24.1 commit `3c018e2` à préserver). |
| HC-DEPLOY-5 | Backup pré-deploy obligatoire. |
| HC-DEPLOY-6 | Le smoke test post-deploy reste obligatoire. |
| HC-DEPLOY-7 | Le runbook `CICD_RUNBOOK.md` doit être à jour à chaque évolution du flow. |

### 11.5 — Contrats sécurité

| # | Contrat |
|---|---|
| HC-SEC-1 | Quality Gate Sonar reste required, ratings A en seuil. |
| HC-SEC-2 | `MIN_PASSWORD_LENGTH = 8` ne peut pas baisser sans Sx_xx explicite. |
| HC-SEC-3 | Headers sécurité (CSP, X-Frame, etc.) restent en place. |
| HC-SEC-4 | Pas de secret en clair dans le repo (audit gitleaks one-shot puis CI continu). |
| HC-SEC-5 | Path param validation déclarative préservée. |

### 11.6 — Contrats spec-driven Claude

| # | Contrat |
|---|---|
| HC-CLAUDE-1 | Aucun sprint build ne s'ouvre sans Spec correspondante validée (`✅ GO Sb_NN`). |
| HC-CLAUDE-2 | Chaque sprint build cite la spec source en commentaire de code. |
| HC-CLAUDE-3 | Chaque sprint build livre un sprint report `docs/SPRINT_*_REPORT.md`. |
| HC-CLAUDE-4 | Chaque sprint build livre un verdict explicite `✅ PRÊT` ou `⏳ ATTENDRE`. |
| HC-CLAUDE-5 | Les hard contracts d'une spec sont testés explicitement (pas seulement documentés). |
| HC-CLAUDE-6 | Un sprint qui dépasse 8 lots est refactoré en plusieurs sprints (lotissement obligatoire). |

## 12. Standard sprint protocol Claude/SuperPower

Sx_26 formalise le protocole qui était jusqu'ici tribal.

### 12.1 — Cycle standard

```
[Étape 0]  Retour dogfooding humain
              ↓
[Étape 1]  Classification selon méta-spec Sx_21 (bug, lacune UX, lacune signal, etc.)
              ↓
[Étape 2]  Décision humaine : patch local OU spec système
              ↓ (si spec système)
[Étape 3]  Sprint Sx_NN SPEC ONLY
              - Inspecte le repo
              - Écrit docs/strategy/SPIGNOS_*_SPEC_v*.md
              - Liste hard contracts
              - Liste acceptance criteria
              - Liste limites assumées
              - Lotissement build chiffré
              - Termine sur verdict ✅ PRÊT ou ⏳ AMENDEMENTS
              ↓
[Étape 4]  Revue humaine + GO/AMEND
              ↓
[Étape 5]  Sprint Sb_NN.1 BUILD
              - Cite la spec verbatim
              - Tests qui verrouillent les hard contracts
              - Sprint report avec section "non-régression vérifiée"
              - Verdict ✅ Sb_NN.2 PRÊT ou ⏳
              ↓
[Étape 6]  GO humain explicite avant Sb_NN.2
              ↓ (loop)
[Étape 7]  Dernier lot Sb_NN.k = audit empirique + sprint report final cycle
              ↓
[Étape 8]  Dogfooding humain valide en condition réelle
              ↓ (retour à Étape 0)
```

### 12.2 — Garde-fous protocolaires

| Garde-fou | Mécanisme |
|---|---|
| Pas de code avant spec validée | HC-CLAUDE-1 |
| Pas de plus de 8 lots par sprint | HC-CLAUDE-6 |
| Spec source citée en code | HC-CLAUDE-2 |
| Sprint report obligatoire | HC-CLAUDE-3 |
| Verdict explicite par sprint | HC-CLAUDE-4 |
| Hard contracts testés | HC-CLAUDE-5 |
| Lotissement chiffré dans la spec | Sx_NN doit lister Sb_NN.k avec effort estimé |
| Dogfood loop intégrée | Méta-spec Sx_21 |

### 12.3 — Templates à créer en Sb_26.6

- `docs/strategy/_SPEC_TEMPLATE.md` — structure obligatoire (résumé, état, modèle, contrats durs, lotissement, limites, risques, verdict)
- `docs/_BUILD_REPORT_TEMPLATE.md` — structure obligatoire (résumé exécutif, fichiers, diff métier, tests, limites, recommandation lot suivant)
- `docs/_AMENDMENT_REPORT_TEMPLATE.md` — pour les micro-passes Sx_NN.1 d'amendements

## 13. Release checklist

À cocher avant chaque deploy production. Cible Sb_26.7 pour formaliser en script.

```
[ ] CI 3/3 verte sur le SHA cible
[ ] Quality Gate Sonar OK sur le SHA cible
[ ] Coverage ≥ 89 % maintenu
[ ] Aucune migration Alembic en attente non testée localement
[ ] Si migration nouvelle : drift check OK + upgrade testé sur copie BD prod
[ ] Si migration nouvelle : downgrade testé localement
[ ] Pas de TODO/XXX/FIXME critique dans les commits inclus
[ ] Sprint report associé livré et lu
[ ] CICD_RUNBOOK.md à jour si flow modifié
[ ] Branch protection toujours active
[ ] Backups quotidien BD prod fonctionnel (timestamp < 24h)
[ ] Free disk space VPS > 20 % avant deploy
[ ] vps-preflight.sh sortie clean
[ ] Décision humaine consciente : "GO deploy"
[ ] Workflow_dispatch lancé avec SHA full (pas branche)
[ ] Smoke test post-deploy PASS
[ ] Tag deploy/prod/... poussé
[ ] Notification post-deploy reçue (Sb_26.3)
[ ] Test fonctionnel manuel sur 1 page critique (`/`, `/sessions/new`, `/coach-report`)
```

## 14. Rollback checklist

À cocher si un deploy a dégradé la production. Cible Sb_26.7 pour scripter.

```
[ ] Identifier SHA précédent stable via tag deploy/prod/... ou `git log`
[ ] Identifier la cause : crash, mauvais comportement, migration foireuse, autre
[ ] Si migration foireuse :
    [ ] sudo -u ubuntu alembic downgrade -1
    [ ] Vérifier var/workout.db (intégrité, rows comptés)
    [ ] Si downgrade impossible : restaurer backup pré-deploy
[ ] Workflow_dispatch deploy-production avec ref = SHA stable précédent
[ ] Smoke test PASS
[ ] Tag deploy/prod/rollback-YYYY-MM-DD-... poussé
[ ] Notification rollback envoyée (Sb_26.3)
[ ] Issue GitHub ouverte avec post-mortem (cause, action prise, prévention)
[ ] CICD_RUNBOOK.md mis à jour si nouveau pattern d'incident
[ ] Spec d'amendement Sx_xx ouverte si un contrat a été violé
```

## 15. Required status checks recommandés

État actuel : `pytest + QA scripts` + `SonarCloud` required.

Cible Sx_26 (après Sb_26.1) :

| Check | Statut cible | Sprint cible |
|---|---|---|
| `pytest + QA scripts` | required | déjà |
| `SonarCloud` | required | déjà |
| `ruff check` | required avec quota | Sb_26.1 |
| `ruff format check` | required | Sb_26.1 |
| `bandit security scan` | required (-ll) | Sb_26.1 |
| `pip-audit` | required (no high) | Sb_26.4 |
| `actionlint` workflows | required | Sb_26.1 |
| `shellcheck` scripts | required (-S warning) | Sb_26.1 |
| `gitleaks` historique | required (one-shot puis CI continu) | Sb_26.4 |

## 16. Nouveau découpage build Sb_26.1 à Sb_26.7

### 16.1 — Sb_26.1 CI hardening (~5h)

- Bump `actions/*` versions Node 24 (deprecation warnings)
- Convertir ruff de advisory à required avec quota explicite (commit le `.ruff.toml` quota si nécessaire)
- Convertir bandit de advisory à required
- Ajouter actionlint sur les workflows GitHub
- Ajouter shellcheck sur les scripts du repo
- Maintenir le smoke test + Sonar required
- Documenter le quota de warnings tolérés dans `docs/CI_QUALITY_BUDGET.md`

### 16.2 — Sb_26.2 deploy manifest and prod-state audit (~4h)

- Ajouter une étape à `deploy_prod.sh` qui produit un `deploy_manifest.json` :
  ```
  {
    "deployed_at": "...",
    "deployed_by_dispatcher": "<github_actor>",
    "from_sha": "...",
    "to_sha": "...",
    "alembic_head_before": "...",
    "alembic_head_after": "...",
    "smoke_test_result": "PASS|FAIL|SKIPPED",
    "backup_path": "/opt/.../var/backups/...",
    "duration_seconds": N
  }
  ```
- Persister en `var/manifests/manifest_YYYYMMDD_HHMMSS.json`
- Cumuler `var/manifests/INDEX.json` (audit trail consultable)
- Ajouter rotation automatique backups (retention 30 jours)
- Endpoint `/admin/deploy-history` (auth admin only) pour consulter

### 16.3 — Sb_26.3 monitoring and alerting baseline (~6h)

- Intégrer Sentry SDK FastAPI côté SPIGNOS (opt-in via env `SENTRY_DSN`)
- UptimeRobot setup pour les 3 sites du VPS
- Webhook Discord (ou email) sur incident
- `/healthz/strict` étendu : check disk space, check backup age, check service uptime
- Cron sur le VPS qui curl `/healthz/strict` toutes les 5 min et alerte si fail
- Documenter dans `docs/MONITORING_RUNBOOK.md`

### 16.4 — Sb_26.4 security baseline (~5h)

- Rate limiting `/register` + `/login` + `/forgot-password` (slowapi ou middleware custom)
- `pip-audit` ajouté en CI required
- `.github/dependabot.yml` avec scope pip + github-actions
- `gitleaks` one-shot scan historique + ajout en CI
- Audit CSP + tightening si possible (sans casser les SVG inline)
- Documenter dans `docs/SECURITY_BASELINE.md`

### 16.5 — Sb_26.5 test quality hardening (~4h)

- Catégorisation pytest marks (`smoke`, `slow`, `integration`, `security`)
- Test downgrade roundtrip Alembic en CI
- Snapshot tests sur 3 templates critiques (`coach_report.html`, `session_done.html`, `index.html`)
- Mutation testing baseline sur `services/quality_score.py` (1 service critique)
- Tests perf budget : `/` < 500ms, `/coach-report` < 800ms, `/sessions/{id}/done` < 600ms
- Documenter le quality budget dans `docs/TEST_QUALITY_BUDGET.md`

### 16.6 — Sb_26.6 spec-driven templates (~3h)

- `docs/strategy/_SPEC_TEMPLATE.md`
- `docs/_BUILD_REPORT_TEMPLATE.md`
- `docs/_AMENDMENT_REPORT_TEMPLATE.md`
- `docs/_SPRINT_PROTOCOL.md` formalise le protocole Sx_NN → Sb_NN.k
- Pre-commit hook optionnel `pre-commit-hooks/check-sprint-title.sh` qui rejette un commit sans préfixe `feat(sb_NN_x):` ou `docs(sx_NN):` ou `fix(sb_NN_x_next):` etc.

### 16.7 — Sb_26.7 rollback drill and release checklist (~3h)

- Scripter la release checklist (§13) en `scripts/release_check.sh`
- Scripter la rollback checklist (§14) en `scripts/rollback.sh`
- Faire un rollback drill sur staging (un environnement éphémère ou sur une copie de la BD prod)
- Documenter post-mortem template dans `docs/POST_MORTEM_TEMPLATE.md`
- Mise à jour `CICD_RUNBOOK.md` avec les sections release + rollback

**Effort total Sb_26.1 → Sb_26.7 : ~30h** sur 2-3 semaines en lotissant proprement.

## 17. Tests à ajouter

Liste consolidée des tests à livrer pendant Sb_26.x.

### 17.1 — CI hardening (Sb_26.1)

- `tests/test_ci_quality_budget.py` : vérifie que le quota ruff documenté n'est pas dépassé
- Lint actionlint passe sur tous les workflows
- Lint shellcheck passe sur tous les scripts

### 17.2 — Deploy manifest (Sb_26.2)

- `tests/test_deploy_manifest.py` : structure du manifest valide, rotation backups OK
- Endpoint `/admin/deploy-history` testé E2E avec auth

### 17.3 — Monitoring (Sb_26.3)

- `tests/test_healthz_strict_extended.py` : disk space, backup age, service uptime
- Mock Sentry SDK pour vérifier qu'une exception capture la stacktrace correctement

### 17.4 — Security (Sb_26.4)

- `tests/test_rate_limiting.py` : `/register` rate-limited après N requêtes/min, `/login` idem
- pip-audit ne signale aucun HIGH au moment du sprint

### 17.5 — Test quality (Sb_26.5)

- Tests perf budget : `tests/test_perf_budget.py` avec marks `@pytest.mark.perf`
- Snapshot tests templates : `tests/test_template_snapshots.py`
- Migration downgrade roundtrip : `tests/test_migration_downgrade.py`

### 17.6 — Spec templates (Sb_26.6)

- `tests/test_spec_protocol.py` : vérifie que les nouvelles specs Sx_xx respectent le SPEC_TEMPLATE.md (sections obligatoires présentes)
- Vérifie qu'un sprint report respecte BUILD_REPORT_TEMPLATE.md

### 17.7 — Rollback (Sb_26.7)

- `tests/test_release_check.py` : `scripts/release_check.sh` retourne 0 en bon état, non-0 sinon
- Test rollback drill noté dans le sprint report

## 18. Non-goals

Explicitement hors scope de Sx_26 / Sb_26.x :

- ❌ Migration React Native ou mobile app native
- ❌ Migration SQLite → PostgreSQL
- ❌ Modification des features produit
- ❌ Multi-tenancy infrastructure
- ❌ Internationalisation (i18n)
- ❌ Modèle de monétisation / billing / Stripe
- ❌ RGPD UI (export complet, delete account) — reporté à Sx_27
- ❌ CGU / mentions légales / privacy policy publiées — reporté à Sx_27
- ❌ Refonte design system / branding
- ❌ Mutation testing exhaustif (seulement baseline 1 service)
- ❌ Load testing exhaustif (V3)
- ❌ Chaos engineering
- ❌ Tracing distribué
- ❌ Microservices
- ❌ Container Docker pour SPIGNOS (reste systemd uvicorn)
- ❌ Auto-scaling
- ❌ CDN
- ❌ Refonte CI vers un autre provider (reste GitHub Actions)
- ❌ Auto-deploy sur push (HC-DEPLOY-1)
- ❌ Suppression du smoke test (HC-CI-7)
- ❌ Suppression du tag prod (HC-CI-6)
- ❌ Réduction des tests existants

## 19. Open questions

| # | Question | Impact | Décision attendue avant |
|---|---|---|---|
| OQ-1 | ✅ **TRANCHÉE 2026-06-01** — modèle "baseline locked + no new warnings". Voir §19bis. | Sb_26.1 | (close) |
| OQ-2 | Sentry self-hosted ou SaaS Sentry.io ? Coût mensuel acceptable ? | Sb_26.3 | Sb_26.3 ouverture |
| OQ-3 | UptimeRobot gratuit ou alternative (Cronitor, betterstack) ? | Sb_26.3 | Sb_26.3 ouverture |
| OQ-4 | Discord webhook personnel ou créer un canal Telegram dédié pour alerting ? | Sb_26.3 | Sb_26.3 ouverture |
| OQ-5 | Rate limit values : 5 register/h par IP est-il acceptable ? | Sb_26.4 | Sb_26.4 ouverture |
| OQ-6 | Authority pour le post-mortem (chaque incident produit-il un PM obligatoire) ? | Sb_26.7 | Sb_26.7 ouverture |
| OQ-7 | Le `dependabot.yml` doit-il auto-merge les patches mineurs ou ouvrir une PR pour review humaine ? | Sb_26.4 | Sb_26.4 ouverture |
| OQ-8 | La rotation backups doit-elle être faite par le script de deploy ou par un cron systemd séparé ? | Sb_26.2 | Sb_26.2 ouverture |
| OQ-9 | `/admin/deploy-history` doit-il être accessible uniquement à un user "admin" (à créer) ou par check sur `users.username == "martin"` (V1 simple) ? | Sb_26.2 | Sb_26.2 ouverture |
| OQ-10 | Mutation testing baseline : pourcentage minimal de "killed mutants" acceptable comme target initial (60 % ? 75 % ?) ? | Sb_26.5 | Sb_26.5 ouverture |

## 19bis. Amendement OQ-1 — modèle baseline locked

**Date amendement :** 2026-06-01
**Décision humaine :** OQ-1 tranchée selon les modalités suivantes.

### 19bis.1 — Modèle retenu

**"Baseline locked + no new warnings"** — pas de cleanup massif des warnings legacy, mais aucun nouveau warning n'est autorisé. La CI échoue si :
- `total_ruff_warnings > B0`, OU
- `new_ruff_warnings > 0`

Réduction progressive par paliers dans les sprints futurs (dédiés `Sb_26.next.ruff-cleanup-N`).

### 19bis.2 — Baseline B0

| Élément | Valeur |
|---|---|
| **B0 fixée le 2026-06-01** | **548 warnings** (mesure réelle à l'amendement) |
| Estimation pré-amendement (Sx_26 §19 initial) | 478 (estimation Sb_20.2, drift d'environ +70 depuis) |
| Distribution dominante actuelle | `UP017` (147) `timezone.utc → datetime.UTC`, `I001` (145) imports, `UP045` (127) `X \| None`, `F401` (67) unused imports |
| Auto-fixable | ~92 % (~505 sur 548) trivialement via `ruff check --fix` |

**Justification du choix B0=548 plutôt que 478** : si la baseline était strictement à 478 verbatim de la consigne user initiale, la CI échouerait immédiatement (mesure réelle 548 > 478). La consigne **non-négociable** "Ne corrige pas massivement les warnings ruff legacy" prime — donc B0 = mesure réelle au jour du sprint.

### 19bis.3 — Versioning de la baseline

Le fichier `.ruff-budget.json` à la racine du repo porte la baseline :

```json
{
  "baseline_warnings": 548,
  "baseline_date": "2026-06-01",
  "baseline_sprint": "Sb_26.1",
  "model": "baseline_locked_no_new",
  "policy": {
    "fails_if_total_above_baseline": true,
    "fails_if_new_warnings_above_zero": true,
    "allows_total_decrease": true
  }
}
```

Le fichier est commit en clair et tout PR doit le maintenir cohérent. Réduire le `baseline_warnings` est un acte volontaire (Sprint cleanup) qui doit être documenté.

### 19bis.4 — Backlog cleanup

| Sprint | Cible | Estimation |
|---|---|---|
| Sb_26.next.ruff-cleanup-1 | UP017 (147 warnings) trivial auto-fix `--unsafe-fixes` désactivé | 2h |
| Sb_26.next.ruff-cleanup-2 | I001 (145) imports formatting | 1h |
| Sb_26.next.ruff-cleanup-3 | UP045 (127) `X \| None` modernization | 2h |
| Sb_26.next.ruff-cleanup-4 | F401 (67) unused imports — review prudent | 3h |
| Sb_26.next.ruff-cleanup-5 | Reste : E402, UP037, F541, E702, F841, C901 (~52 mixtes) | 2h |

**Cible de palier post-cleanup** : `B0 < 50` (warnings résiduels nécessitant review humaine, pas auto-fixables).

### 19bis.5 — Contrats associés

| # | Contrat |
|---|---|
| HC-RUFF-1 | `.ruff-budget.json` est commité, jamais supprimé. |
| HC-RUFF-2 | Toute baseline diminuée doit être actée dans le sprint correspondant (commit message explicite). |
| HC-RUFF-3 | Toute baseline augmentée nécessite un amendement Sx_xx — pas de bump silencieux. |
| HC-RUFF-4 | Le script de check ne se contente pas du total : il échoue aussi si un fichier modifié dans le PR introduit un warning là où il n'y en avait pas. |

---

## 20. Verdict — GO ou WAIT pour build

### Verdict : **✅ GO pour build Sb_26.1**

Justification :
- L'état actuel du repo est documenté et compris (sections 2-9)
- Les gaps sont classés et priorisés (section 10)
- Les hard contracts anti-drift sont énumérés explicitement (section 11)
- Le protocole spec-driven est codifié (section 12)
- Les checklists release et rollback sont rédigées (sections 13-14)
- Le découpage Sb_26.1 → Sb_26.7 est chiffré et chaque lot est cadré (section 16)
- Les non-goals sont explicites pour éviter le scope creep (section 18)
- Les open questions sont listées et bornées au sprint d'ouverture pertinent (section 19)

**Condition pré-Sb_26.1** : valider OQ-1 (quota warnings ruff). Sans cela, le passage de advisory à required ne peut pas être chiffré.

**Recommandation séquence** :
1. Sb_26.1 (CI hardening) — fondations qui débloquent les autres lots
2. Sb_26.4 (security baseline) — P0 sec
3. Sb_26.3 (monitoring) — P0 ops
4. Sb_26.2 (deploy manifest) — audit trail
5. Sb_26.5 (test quality) — anti-drift moyen terme
6. Sb_26.6 (spec templates) — codification protocole
7. Sb_26.7 (rollback drill + release) — clôture cycle

**Cycle Sx_26** se ferme avec un état mesurable : aucune dette P0 restante, protocole spec-driven contractualisé, rollback drillé, monitoring runtime opérationnel.

Avant de lancer Sb_26.1, valider :
- [ ] Cette spec lue intégralement
- [ ] OQ-1 tranchée
- [ ] Pas d'amendements demandés
- [ ] Décision humaine explicite "GO Sb_26.1"

À la livraison de Sb_26.7, le projet est techniquement prêt pour Sx_27 (RGPD / commercialisation) ou Sb_25 (LLM narratif) ou tout autre chantier produit, avec un plan de contrôle d'ingénierie robuste qui empêche le drift agent et garantit la reproductibilité des cycles futurs.
