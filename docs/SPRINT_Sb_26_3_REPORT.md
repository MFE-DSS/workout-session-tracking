# Sb_26.3 — Deploy / Observability (Sprint Report)

**Date :** 2026-06-13
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Spec parente :** `docs/strategy/Sx_26_ENGINEERING_CONTROL_PLANE_AND_ANTI_DRIFT_HARDENING_SPEC.md`
**Lot Sx_26 :** §16 — Sb_26.3 (Deploy / Observability — troisième lot du cycle)
**Statut :** ✅ Livré

---

## 1. Résumé exécutif

Sb_26.3 livre une base d'observabilité minimale et opérable : deploy SHA tracking, `/healthz/strict` enrichi, Sentry/Discord en opt-in strict, runbook complet. Aucune stack lourde (Prometheus, Grafana, Docker) introduite, aucune feature produit touchée.

**Verdict :** ✅ **Sb_26.4 PRÊT**.

## 2. Périmètre livré

### 2.1 Fichiers créés

| Fichier | Rôle |
|---|---|
| `scripts/write_deploy_state.py` | CLI appelé par `deploy_prod.sh` → écrit `var/deploy_state.json` après health check |
| `scripts/prod_state_report.py` | Diagnostic JSON tout-en-un (deploy, backup, disk, healthz optionnel) — pas de secrets |
| `scripts/alert_discord.py` | Webhook alerter strictement opt-in via `DISCORD_WEBHOOK_URL` — no-op si absent |
| `tests/test_observability.py` | 11 tests : healthz enrichi, writer schema, prod report, alerter opt-in, Sentry opt-in |
| `docs/OBSERVABILITY_RUNBOOK.md` | Runbook complet : Sentry, UptimeRobot, Discord, procédures incident |
| `docs/SPRINT_Sb_26_3_REPORT.md` | Ce rapport |

### 2.2 Fichiers modifiés

| Fichier | Changement |
|---|---|
| `app/routers/health.py` | `/healthz/strict` : ajout `deploy` + `disk` (informationnels, ne flap pas) ; helpers privés `_read_deploy_state` + `_disk_usage` |
| `app/config.py` | Ajout 4 settings : `deploy_state_path`, `sentry_dsn`, `sentry_environment`, `sentry_traces_sample_rate` + property `sentry_enabled` |
| `app/main.py` | Helper `_init_sentry_if_enabled(settings)` appelé dans `create_app()` — try-import-pass si SDK absent |
| `scripts/deploy_prod.sh` | Section "Recording deploy state (Sb_26.3)" entre health check et summary — best-effort, n'échoue jamais le deploy |
| `tests/test_ops_closure.py` | `test_healthz_strict_payload_shape_contract` étendu aux nouveaux champs `deploy` + `disk` |
| `docs/MIGRATION_HARDENING.md` | §5 procédure rollback paramétrée avec `APP_DIR`/`APP_USER` + valeurs prod réelles `/opt/workout-session-tracking` + `ubuntu` |

### 2.3 Fichiers NON touchés (par contrat)

- `app/routes` métier (sessions, coach_report, leaderboard, squads, etc.) : **aucune** modification
- `app/templates/` : **aucune** modification
- `app/models/` : **aucune** modification (interdiction "ne modifie pas les modèles SQLAlchemy")
- `migrations/` : **aucune** nouvelle migration (interdiction "ne crée pas de migration Alembic")
- `.github/workflows/deploy-production.yml` : **non touché** (interdiction "ne déclenche pas le deploy prod automatiquement")
- `app/services/*` métier (scoring, reco, substitution, coach_report, body_tracking) : **aucun** fichier touché
- `requirements.txt` : **non modifié** — sentry-sdk reste optionnel (installé séparément en prod si l'opérateur active Sentry)

## 3. Décisions clés

### 3.1 Sentry strictement opt-in + soft import

Si `SENTRY_DSN` est vide → `_init_sentry_if_enabled()` retourne `False` immédiatement, aucun import de `sentry_sdk`, aucun network call.
Si `SENTRY_DSN` est posé MAIS `sentry_sdk` pas installé → catch `ImportError`, retourne `False` silencieusement.
Si les deux conditions sont remplies → `sentry_sdk.init(..., send_default_pii=False)`.

Conséquence : `requirements.txt` n'a pas besoin d'inclure `sentry-sdk`. L'opérateur prod installe `sentry-sdk` séparément après avoir posé `SENTRY_DSN`. CI et dev local : zéro impact, zéro override comportement.

### 3.2 Discord webhook via stdlib `urllib`

Pas de nouvelle dépendance Python (pas de `requests`). Utilise `urllib.request` + 2 `# noqa: S310` documentés (le webhook URL vient strictement de `DISCORD_WEBHOOK_URL` env, contrôlé par l'opérateur).

### 3.3 Deploy state — schéma minimal, jamais bloquant

`var/deploy_state.json` ne contient que SHA, timestamp, service, app_dir, health_at_deploy. Pas de hostname (déjà visible via systemd), pas de username, pas de path complet, pas de version pip. Lisible par n'importe qui (publique via /healthz/strict) — surface de leak minime, valeur opérationnelle élevée.

Le writer est appelé via `|| warn ...` dans deploy_prod.sh : **un échec d'écriture du deploy_state ne fait pas échouer le deploy**. C'est de l'observabilité, pas de la correctness.

### 3.4 `/healthz/strict` reste 503 uniquement pour DB/backup réels

`deploy.errors` non vide n'a aucun effet sur le code HTTP. Un fichier `deploy_state.json` cassé n'écrit pas 503 sur UptimeRobot — c'est ce qui distingue un signal opérationnel (DB down) d'un signal informationnel (rien n'a écrit le state).

### 3.5 Pas de Prometheus/Grafana, pas de Docker

Sx_26 §1 hard contract. Runbook §1 documente les signaux disponibles (HTTP probes + fichier local + CLI) — suffisants pour V1 sans introduire une stack opérationnelle.

### 3.6 Paramétrer les chemins prod dans MIGRATION_HARDENING.md

L'ancienne version mentionnait `/srv/workout` + user `workout` (defaults dev de `deploy_prod.sh`). La réalité prod est `/opt/workout-session-tracking` + `ubuntu` (cf. `scripts/deploy_from_github_actions.sh` lignes 37-38). Corrigé en utilisant `${APP_DIR}` / `${APP_USER}` partout, avec une note explicite donnant les valeurs réelles.

## 4. Tests et vérifications (DoD)

Exécutés localement le 2026-06-13 :

| Check | Résultat | Notes |
|---|---|---|
| `pytest --ignore=tests/test_v1_acceptance.py -q` | ✅ **928 passed** | +11 nouveaux (observability) + contract test mis à jour |
| `python scripts/catalog_qa.py` | ✅ OK | inchangé |
| `python scripts/machine_atlas_qa.py` | ✅ OK | inchangé |
| `PYTHONPATH=. python scripts/check_alembic_drift.py` | ✅ OK no diff | aucune migration |
| `python scripts/check_schema_snapshot.py` | ✅ OK | snapshot inchangé |
| `python scripts/check_migration_patterns.py` | ✅ OK | aucune migration ajoutée |
| `python scripts/check_migration_roundtrip.py` | ✅ OK | inchangé |
| `python scripts/check_ruff_budget.py` | ✅ OK | **546 ≤ 548** (baseline inchangée par contrat) |
| `shellcheck -S warning scripts/deploy_prod.sh` | ✅ exit 0 | section deploy_state shellcheck-clean |

Validation CI réelle : voir §6 (post-push).

## 5. Sécurité / secrets

| Vérification | Statut |
|---|---|
| Aucun token / DSN / webhook hardcodé | ✅ tout via env var |
| `.env` toujours dans `.gitignore` | ✅ (non modifié) |
| Sentry `send_default_pii=False` | ✅ forcé dans `_init_sentry_if_enabled` |
| `/healthz/strict` ne leak ni secret ni password ni token | ✅ test `test_healthz_strict_does_not_expose_secrets` |
| `prod_state_report.py` JSON ne contient ni `password`/`secret`/`webhook`/`dsn`/`token` | ✅ test `test_prod_state_report_emits_json_no_secrets` |
| `alert_discord.py` exit 0 sans env, jamais de POST silencieux | ✅ test `test_alert_discord_disabled_when_env_unset` |

## 6. CI réelle (post-push)

À renseigner après push.

- [ ] Job `pytest + QA scripts` (test + drift + snapshot + patterns + roundtrip) — vert attendu
- [ ] Job `lint (ruff budget + bandit + actionlint + shellcheck)` — vert attendu
- [ ] Job `SonarCloud` — vert attendu
- [ ] Pas de régression sur les status checks Sb_26.1/Sb_26.2

## 7. Auto-fix scope

`ruff check --fix` sur les fichiers que j'ai créés/modifiés (8 fichiers). 21 fixes auto (UP017, I001), 4 S310 documentés + noqa (URL open audit légitime). Le refactor SonarLint S5713 (redundant TimeoutError dans except OSError) simplifié.

**Budget ruff** : 548 → **546** (mes auto-fixes ont nettoyé 2 warnings legacy au passage dans les imports modifiés). Per contrat user "Si des warnings ruff diminuent, ne pas baisser la baseline dans ce sprint sauf commit séparé explicitement dédié" → baseline reste à 548.

**Aucun fichier produit / scoring / reco / substitution / coach report / body tracking / migration n'a été touché.**

## 8. Contraintes respectées

| Contrainte (verbatim user) | Statut |
|---|---|
| Ne touche pas aux features produit | ✅ |
| Ne modifie pas scoring/reco/substitution/coach report/body tracking | ✅ |
| Ne modifie pas les modèles SQLAlchemy | ✅ |
| Ne crée pas de migration Alembic | ✅ |
| Ne modifie pas le flow auth | ✅ |
| Ne rend pas Sentry obligatoire | ✅ opt-in via `SENTRY_DSN`, try-import-pass |
| Ne hardcode aucun token, webhook, domaine privé ou secret | ✅ tout via env |
| Ne déclenche pas le deploy prod automatiquement | ✅ `deploy-production.yml` non touché |
| Ne supprime aucun smoke test | ✅ aucun test retiré |
| Ne casse pas les gates Sb_26.1 et Sb_26.2 | ✅ toutes vertes en local |
| Périmètre autorisé respecté (scripts/, docs/, tests/, health.py, config.py, main.py, deploy_prod.sh) | ✅ aucun autre fichier `app/` modifié |

## 9. Limites assumées et reportées

| Item | Pourquoi pas dans Sb_26.3 | Reporté à |
|---|---|---|
| Sentry release tracking auto (lier release SHA → deploy_state) | V1 simple suffit | Sb_26.next |
| Auto-rollback sur /healthz down N fois | Risque > bénéfice en V1 | post-Sx_26 |
| Logs structurés JSON | Hors scope Sb_26.3 | Sb_27+ |
| Métriques temps réel (p95 endpoints) | Couvert par Sb_26.6 (Performance baseline) | Sb_26.6 |
| Distributed tracing | Stack lourde, hors scope V1 | post-Sx_26 |
| Status page publique | Hors scope produit V1 | post-Sx_26 |
| Cleanup ruff baseline 548 → 546 (consolidation) | Contrat "pas de baseline-down hors sprint dédié" | `Sb_26.next.ruff-cleanup-N` |
| Test E2E real Sentry envoi (mock SDK) | Couvert par opt-in test ; vrai envoi nécessite Sentry réel | post-déploiement opt-in |

## 10. Backlog immédiat (Sx_26 §16)

| Lot | Objet | Bloquant ? |
|---|---|---|
| **Sb_26.4** | Security baseline (secrets scan, dep audit weekly) | Non bloqué par Sb_26.3 |
| Sb_26.5 | Spec/process discipline (template Sx, lien Sx↔commits) | Non bloqué |
| Sb_26.6 | Performance baseline (p95 endpoints, slow query log) | Non bloqué |
| Sb_26.7 | Multi-tenant prep (read-only V1, scope auth) | Non bloqué |

## 11. Verdict

| Critère DoD | Statut |
|---|---|
| pytest passe | ✅ 928 passed |
| catalog_qa passe | ✅ |
| machine_atlas_qa passe | ✅ |
| check_alembic_drift passe | ✅ |
| check_schema_snapshot passe | ✅ |
| check_migration_patterns passe | ✅ |
| check_migration_roundtrip passe | ✅ |
| check_ruff_budget passe (total ≤ 548) | ✅ 546 ≤ 548 |
| lint job passe (à confirmer post-push) | ⏳ |
| Aucun secret commité | ✅ |
| Sentry disabled-by-default | ✅ |
| Alerting disabled-by-default | ✅ |
| Rapport sprint livré | ✅ |

### ✅ **Sb_26.4 PRÊT**

---

**Co-Authored-By :** Claude Opus 4.7
