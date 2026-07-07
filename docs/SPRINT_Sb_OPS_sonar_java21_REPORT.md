# Sprint Report — Sb_OPS.sonar-java21 (SonarCloud Java 21 CI Compatibility Fix)

**Sprint ID :** `Sb_OPS.sonar-java21`
**Type :** OPS BUILD — CI workflow compatibility patch + docs
**Date :** 2026-07-07
**Auteur :** opérateur (Martin Feldmann) + agent Claude Code
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Verdict :** 🟢 **DELIVERED — pending CI**

---

## 1. Contexte

Le build `Sb_UI_02b.1` (Auren Terminal Home re-skin, commit `3b4ba91`) est **fonctionnellement vert** :
- ✅ lint (ruff budget 542 ≤ 548 + bandit + actionlint + shellcheck) success
- ✅ pytest + QA scripts success — **1768 passed**
- ❌ **SonarCloud failure uniquement**

Le job SonarCloud bloque la CI required pour une raison **infra repo-wide**, sans rapport avec le code Home.

## 2. Run concerné

| Élément | Valeur |
|---|---|
| Run | [`28868668286`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28868668286) |
| SHA | `3b4ba9172ae498016569fcc1ef7e14c4291803dc` |
| lint | ✅ success |
| pytest + QA scripts | ✅ success (1768 passed) |
| SonarCloud | ❌ FAILURE (initial + re-run — reproductible, ~28s) |

## 3. Cause racine — Java 17 unsupported

SonarQube Cloud a **déprécié Java 17** côté serveur. L'action legacy `SonarSource/sonarcloud-github-action@v2` embarque un scanner tournant sur **Java 17 Alpine**, désormais **refusé** par SonarCloud.

Logs essentiels (`SonarCloud scan`) :
```
INFO: Java 17.0.11 Alpine (64-bit)
INFO: Analyzing on SonarCloud
INFO: Organization key: mfe-dss
INFO: Project key: MFE-DSS_workout-session-tracking
INFO: 4 languages detected in 292 preprocessed files (done)
INFO: EXECUTION FAILURE
ERROR: Error during SonarScanner execution

The version of Java (17) used to run this analysis is deprecated, and
SonarQube Cloud no longer supports it. Please upgrade to Java 21 or later.
https://docs.sonarsource.com/sonarqube-cloud/analyzing-source-code/scanners/scanner-environment/general-requirements
```

**Preuves que ce n'est pas le code Home :**
- lint ✅ + pytest ✅ (1768 tests) — les jobs qui testent le code passent.
- Le scan a chargé settings, org, quality profiles, active rules, et préprocessé 292 fichiers **avant** de mourir sur le gate de version Java.
- Le commit `3b4ba91` **ne touche ni `.github/`, ni `sonar-project.properties`, ni aucune config CI** (whitelist : `home.css` / `index.html` / test / docs).
- Échec **reproductible au re-run** → non transitoire, rupture de compatibilité serveur SonarCloud.

## 4. Changement CI appliqué

Fichier : `.github/workflows/ci.yml`, job `sonar`, step de scan.

**Avant :**
```yaml
- name: SonarCloud scan
  uses: SonarSource/sonarcloud-github-action@v2
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

**Après :**
```yaml
- name: SonarQube scan
  uses: SonarSource/sonarqube-scan-action@v7.1.0
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

**Conservé à l'identique :**
- `Checkout` avec `fetch-depth: 0` (blame / new-code detection).
- `Download coverage report` (coverage.xml) + `Download linter reports` (ruff/bandit JSON).
- env `SONAR_TOKEN` + `GITHUB_TOKEN`.
- `needs: [test, lint]` · condition du job (push OU PR même repo) · `timeout-minutes: 10`.
- `sonar-project.properties` **inchangé** (projectKey/org/sources/coverage/reports lus à l'identique par la nouvelle action).
- **Pas de `continue-on-error`** — SonarCloud reste **required**, on ne masque pas le signal.

## 5. Justification de `sonarqube-scan-action@v7.1.0`

- `SonarSource/sonarcloud-github-action` est **legacy** (embarque le scanner Java 17).
- L'action officielle actuelle est `SonarSource/sonarqube-scan-action` (renommée), latest visible **v7.1.0**, qui embarque un **scanner sous Java 21** — conforme au nouveau requirement SonarQube Cloud.
- **Aucun `setup-java` ajouté** : la v7 embarque son propre runtime (première tentative = action bump only, comme recommandé). Si la v7.1.0 échoue encore sur Java (peu probable), fallback documenté : ajouter `actions/setup-java@v4` (temurin 21) avant le scan.

## 6. Confirmation aucun code app/test touché

- ✅ `.github/workflows/ci.yml` — modifié (autorisé)
- ✅ `docs/SPRINT_Sb_OPS_sonar_java21_REPORT.md` + registry + roadmap — modifiés (autorisés)
- ❌ Aucun `app/`, `tests/`, `migrations/`, `scripts/`, deps, `pyproject.toml`, `package.json`, `app/static/**`, `app/templates/**`
- ❌ Aucun secret / token / runtime / DB / PNG / release tag touché

## 7. Tests locaux

| Commande | Résultat |
|---|---|
| `check_spec_protocol.py` | ✅ pass |
| `check_ruff_budget.py` | ✅ 542 ≤ 548 |
| `actionlint .github/workflows/ci.yml` | ✅ seul le warning **pré-existant** `SC2046` (ligne 189, non lié) ; aucun nouvel erreur sur le step Sonar |
| YAML parse (python) | ✅ OK |

## 8. Plan de validation post-push

1. Push → CI complète (lint + pytest + SonarCloud).
2. Le job SonarCloud doit désormais tourner sous **Java 21** via `sonarqube-scan-action@v7.1.0` et passer la Quality Gate.
3. Si les 3 jobs verts → **CI repo débloquée**, `Sb_UI_02b.1` peut passer en human review.
4. Si SonarCloud échoue encore sur Java → patch minimal v2 (`actions/setup-java@v4` Java 21 avant le scan), sans toucher au code app.

## 9. Statut

| Item | Statut |
|---|---|
| `Sb_OPS.sonar-java21` | 🟢 **DELIVERED — pending CI** |
| `Sb_UI_02b.1 Home Re-skin` | 🟢 delivered, **bloqué par CI infra** jusqu'au re-run vert (lint+pytest déjà verts) |
| `Sb_UI_02b.2 Focus Re-skin` | ⚪ not opened |
| `Sx_UI_06` | ⚪ future |
| Release tag | ⏸️ deferred |

## 10. Verdict

🟢 **Sb_OPS.sonar-java21 DELIVERED — pending CI.**

**Objectif : restaurer la CI required (SonarCloud sous Java 21), sans masquer le signal, sans toucher au code applicatif.**
