# Sb_26.4 — Security Baseline (Sprint Report)

**Date :** 2026-06-14
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Spec parente :** `docs/strategy/Sx_26_ENGINEERING_CONTROL_PLANE_AND_ANTI_DRIFT_HARDENING_SPEC.md`
**Lot Sx_26 :** §16 — Sb_26.4 (Security baseline — quatrième lot du cycle)
**Statut :** ✅ Livré

---

## 1. Résumé exécutif

Sb_26.4 livre une baseline sécurité minimale avant toute ouverture publique : rate limiting per-IP sur les endpoints d'auth, audit de dépendances en CI required, Dependabot, gitleaks, lockfile reproducible (advisory). Aucune touche au code produit métier, aucune migration, aucun modèle SQLAlchemy modifié.

**Verdict :** ✅ **Sb_26.5 PRÊT**.

## 2. Périmètre livré

### 2.1 Fichiers créés

| Fichier | Rôle |
|---|---|
| `.github/dependabot.yml` | PRs hebdo pip + actions, pas d'auto-merge, max 5 ouvertes |
| `requirements-lock.txt` | Lockfile reproducible (pip-compile --strip-extras) |
| `scripts/regen_lockfile.sh` | Script de régénération du lockfile |
| `tests/test_rate_limiting.py` | 10 tests : sliding window + intégration HTTP /login/register/forgot |
| `docs/SECURITY_BASELINE.md` | Documentation complète : archi, rate limit, audit, gitleaks, procédures |
| `docs/SPRINT_Sb_26_4_REPORT.md` | Ce rapport |

### 2.2 Fichiers modifiés

| Fichier | Changement |
|---|---|
| `app/config.py` | Ajout settings rate-limit : `enabled`, `login_max/window`, `register_max/window`, `forgot_max/window` |
| `app/main.py` | Ajout `RateLimitMiddleware` + helpers `_rate_limit_check` / `_rate_limit_reset_for_tests` (module-level buckets) |
| `.github/workflows/ci.yml` | Job `lint` : ajout `pip-audit` (required), `gitleaks` (required), lockfile parse-check (advisory) ; ajout `pip-audit pip-tools` aux installs |

### 2.3 Fichiers NON touchés (par contrat)

- `app/services/scoring/`, `app/services/reco/`, `app/services/substitution.py`, `app/services/coach_report.py`, `app/services/body_tracking.py` : **aucun** fichier touché
- `app/models/*` : **aucune** modification (interdiction "ne modifie pas les modèles SQLAlchemy")
- `migrations/versions/` : **aucune** nouvelle migration (interdiction)
- `app/templates/` : **aucune** modification
- `app/routers/auth_routes.py` : **non touché** (rate limiting implémenté en middleware, pas via décorateur sur la route — préserve la signature existante de l'auth)
- `requirements.txt` : **non modifié** (sentry-sdk reste optionnel, pip-audit/pip-tools sont CI-only)
- `scripts/deploy_prod.sh` : **non touché** (interdiction implicite "Ne pas basculer deploy_prod.sh sur le lockfile sans validation explicite")
- `.github/workflows/deploy-production.yml` : **non touché**

## 3. Décisions clés

### 3.1 Rate limiting : middleware vs décorateur

Choisi : **middleware** Starlette qui intercepte `(method, path)`. Avantage : `auth_routes.py` reste intouché, contrat "ne casse pas l'auth existante" verbatim respecté. Pattern uniforme avec le `SecurityHeadersMiddleware` déjà en place. Désavantage léger : un nouveau route auth devra être déclarée dans `_RATE_LIMIT_ROUTES` (trade-off accepté — V1 a 3 routes ciblées).

### 3.2 In-memory bucket (pas Redis)

Single-process V1, pas de partage entre workers, pas de persistance. Justifié dans `docs/SECURITY_BASELINE.md §2.4`. Le seul cas où ce choix devient sous-dimensionné : multi-worker uvicorn (`--workers N`). À ce moment-là, swap pour Redis sans toucher aux routes (interface `_rate_limit_check` reste stable).

### 3.3 Sober 429 message

Test explicite que la réponse 429 **ne fuit pas** : `user`, `exist`, `registered`, `account`, `email`. Empêche un attaquant d'utiliser le rate limiter comme oracle (« si je suis bloqué après N tentatives sur cet email, c'est qu'il existe »).

### 3.4 pip-audit en CI required

Baseline mesurée le 2026-06-14 : `No known vulnerabilities found`. Donc on peut verrouiller via `--strict`. Si demain une dep est compromise, la CI casse avant le merge, l'opérateur doit corriger ou justifier (procédure §3.2 du runbook).

### 3.5 Lockfile **advisory** en V1

L'auto-bascule sur `pip install -r requirements-lock.txt` est une décision avec impact prod réel (résolution figée, plan de rollback nécessaire). User a explicitement dit "Ne pas basculer deploy_prod.sh sur le lockfile sans validation explicite". Donc V1 livre :
* le lockfile committé
* le script de régénération
* un parse-check CI advisory (ne casse jamais sur diff cross-Python)

La bascule prod est dans le backlog (`docs/SECURITY_BASELINE.md §5.3`).

### 3.6 Dependabot sans auto-merge

User a explicitement précisé "Dependabot ouvre des PRs manuelles, aucun auto-merge". Configuration respecte verbatim : aucune section `auto-merge` dans `dependabot.yml`. Cap volontaire à 5 PRs ouvertes pour forcer la discipline de revue.

### 3.7 gitleaks current-tree, pas full-history

User : "gitleaks doit scanner le current tree / PR en CI. gitleaks full history peut être documenté comme one-shot manuel si trop bruyant." Respecté : `gitleaks/gitleaks-action@v2` en CI required, full-history documentée procédurale dans `SECURITY_BASELINE.md §6.2`.

## 4. Tests et vérifications (DoD)

Exécutés localement le 2026-06-14 :

| Check | Résultat | Notes |
|---|---|---|
| `pytest --ignore=tests/test_v1_acceptance.py -q` | ✅ **938 passed** | +10 nouveaux (rate limiting) |
| `python scripts/catalog_qa.py` | ✅ OK | inchangé |
| `python scripts/machine_atlas_qa.py` | ✅ OK | inchangé |
| `PYTHONPATH=. python scripts/check_alembic_drift.py` | ✅ OK | aucune migration |
| `python scripts/check_schema_snapshot.py` | ✅ OK | snapshot inchangé |
| `python scripts/check_migration_patterns.py` | ✅ OK | aucune migration ajoutée |
| `python scripts/check_migration_roundtrip.py` | ✅ OK | inchangé |
| `python scripts/check_ruff_budget.py` | ✅ OK | **546 ≤ 548** (baseline inchangée par contrat) |
| `pip-audit -r requirements.txt --strict` | ✅ OK | No known vulnerabilities found |
| `shellcheck -S warning scripts/*.sh` | ✅ OK | scripts/regen_lockfile.sh inclus |

Validation CI réelle : voir §6 (post-push).

## 5. Sécurité / secrets

| Vérification | Statut |
|---|---|
| Aucun token, webhook, DSN, ou secret hardcodé | ✅ tout via env |
| `.env` reste dans `.gitignore` | ✅ inchangé |
| Tests rate-limit ne fuitent pas existence utilisateur en 429 | ✅ test `test_login_returns_429_after_max_attempts` |
| pip-audit baseline figée (clean) | ✅ |
| Dependabot pas d'auto-merge | ✅ |
| gitleaks gate required | ✅ |
| Lockfile committé | ✅ |
| `scripts/regen_lockfile.sh` shellcheck-clean | ✅ |

## 6. CI réelle (post-push)

À renseigner après push.

- [ ] Job `pytest + QA scripts` — vert attendu
- [ ] Job `lint (ruff budget + bandit + actionlint + shellcheck + pip-audit + gitleaks)` — vert attendu
- [ ] Job `SonarCloud` — vert attendu
- [ ] Pas de régression sur les gates Sb_26.1/Sb_26.2/Sb_26.3

## 7. Risques identifiés

| Risque | Probabilité | Mitigation |
|---|---|---|
| gitleaks détecte un faux positif sur bcrypt hash de conftest | basse | dummy hash de auth_routes.py et conftest.py — gitleaks default rules ne flag pas bcrypt. Si CI casse : ajouter `gitleaks:allow` inline avec justification |
| Lockfile généré Python 3.14 ne s'installe pas en CI 3.11 | moyenne | parse-check est advisory + `continue-on-error: true`. Si vrai conflit cross-Python, le job CI principal `test` (pip install -r requirements.txt) continue d'utiliser requirements.txt non-locké |
| Rate limit trop agressif en dev local | basse | settings configurables via env, `RATE_LIMIT_ENABLED=0` disponible |
| Dependabot ouvre trop de PRs | basse | cap `open-pull-requests-limit: 5` + groupage `patch-updates` |
| pip-audit ajoute une vuln demain et bloque la CI | moyenne | procédure documentée `docs/SECURITY_BASELINE.md §3.2` — upgrade ou ignore justifié |

## 8. Contraintes respectées

| Contrainte (verbatim user) | Statut |
|---|---|
| Ne modifie pas scoring/reco/substitution/coach report/body tracking | ✅ |
| Ne modifie pas les modèles SQLAlchemy | ✅ |
| Ne crée pas de migration Alembic | ✅ |
| Ne modifie pas les templates produit sauf nécessité absolue | ✅ aucun template touché |
| Ne casse pas l'auth existante | ✅ auth_routes.py non touché, 41 tests auth/security/password_reset verts |
| Ne rend pas obligatoire un service externe | ✅ rate limiter in-memory, Dependabot opt-in repo-side |
| Ne hardcode aucun secret | ✅ |
| Ne déclenche pas de deploy prod | ✅ deploy workflow non touché |
| Ne désactive aucune gate Sb_26.1/Sb_26.2/Sb_26.3 | ✅ toutes inchangées + 2 nouvelles required |
| Ne baisse pas la baseline ruff dans ce sprint | ✅ 548 inchangée (mesure courante 546 toléré par policy `allows_total_decrease: true`) |
| Dependabot ouvre des PRs manuelles, aucun auto-merge | ✅ aucun `auto-merge` dans `.github/dependabot.yml` |
| Pas de CAPTCHA | ✅ |
| Pas de 2FA | ✅ |
| Pas de refonte auth | ✅ |

## 9. Limites assumées et reportées

| Item | Pourquoi pas dans Sb_26.4 | Reporté à |
|---|---|---|
| Lockfile strict cross-Python freshness check | brittle V1 (3.14 local vs 3.11 CI) | Sb_26.next |
| Bascule deploy_prod.sh sur lockfile-install | nécessite validation explicite | Sb_26.next ou plus tard |
| Rate limit multi-process Redis-backed | single-process V1 | Sb_27+ |
| Audit dev/test deps (ruff, pytest, etc.) | risque acceptable V1 (pas en prod) | Sb_27+ |
| SBOM | hors scope V1 | Sb_27+ |
| 2FA / TOTP | interdiction explicite "pas de refonte auth" | Sb_27+ |
| Pre-commit hooks pip-audit / gitleaks | CI suffit V1 | post-Sb_26 |
| Cleanup ruff baseline 548 → 546 (ratchet) | contrat sprint dédié | `Sb_26.next.ruff-cleanup-N` |
| Sonar warnings sur `pip install` (S8541/S8544) sans `--only-binary :all:` | comportement install changé requiert validation | Sb_26.next |
| Strict freshness lockfile vs `pip install` actual | scope V1 advisory only | Sb_26.next |

## 10. Backlog immédiat (Sx_26 §16)

| Lot | Objet | Bloquant ? |
|---|---|---|
| **Sb_26.5** | Spec/process discipline (template Sx, lien Sx↔commits) | Non bloqué par Sb_26.4 |
| Sb_26.6 | Performance baseline (p95 endpoints, slow query log) | Non bloqué |
| Sb_26.7 | Multi-tenant prep (read-only V1, scope auth) | Non bloqué |

## 11. Verdict

| Critère DoD | Statut |
|---|---|
| pytest passe | ✅ 938 passed |
| catalog_qa passe | ✅ |
| machine_atlas_qa passe | ✅ |
| check_alembic_drift passe | ✅ |
| check_schema_snapshot passe | ✅ |
| check_migration_patterns passe | ✅ |
| check_migration_roundtrip passe | ✅ |
| check_ruff_budget passe (total ≤ 548) | ✅ 546 ≤ 548 |
| lint job passe (post-push) | ⏳ |
| pip-audit passe ou décision documentée | ✅ clean baseline |
| gitleaks current tree passe ou décision documentée | ⏳ (CI le confirmera) |
| tests rate limiting passent | ✅ 10/10 |
| Aucun secret commité | ✅ |
| Aucun modèle SQLAlchemy modifié | ✅ |
| Aucune migration créée | ✅ |
| Rapport sprint livré | ✅ |

### ✅ **Sb_26.5 PRÊT**

Conditions de levée :
- Sb_26.4 mergé en main
- CI verte sur le push (3 jobs)
- pip-audit + gitleaks verts en CI réelle
- Ajouter manuellement côté GitHub Settings : pas de changement nécessaire — les 2 nouvelles gates sont **internes** au job `lint` déjà required

---

**Co-Authored-By :** Claude Opus 4.7
