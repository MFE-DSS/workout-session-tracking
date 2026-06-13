# Sb_26.1 — CI Hardening (Sprint Report)

**Date :** 2026-06-13
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Spec parente :** `docs/strategy/Sx_26_ENGINEERING_CONTROL_PLANE_AND_ANTI_DRIFT_HARDENING_SPEC.md`
**Lot Sx_26 :** §16 — Sb_26.1 (CI Hardening — premier lot du cycle)
**Statut :** ✅ Livré

---

## 1. Résumé exécutif

Sb_26.1 ferme la principale dérive identifiée dans Sx_26 §10 (ruff advisory → silencieux) et durcit le pipeline CI en rendant **required** quatre nouvelles gates (ruff budget, bandit Med/High, actionlint, shellcheck) sans toucher au code métier ni casser un seul test existant.

L'arbitrage clé est l'amendement **Sx_26 §19bis OQ-1** : modèle "baseline locked + no new warnings" plutôt que zéro ruff immédiat (qui aurait imposé un cleanup massif de 548 warnings legacy).

**Verdict :** ✅ **Sb_26.2 PRÊT**.

## 2. Périmètre livré

### 2.1 Fichiers créés

| Fichier | Rôle |
|---|---|
| `.ruff-budget.json` | Source de vérité unique pour la baseline ruff (548 warnings figés au 2026-06-01) |
| `scripts/check_ruff_budget.py` | Script CLI : compare ruff actuel vs baseline, exit 1 si dépassement |
| `docs/CI_QUALITY_BUDGET.md` | Doc complète : modèle, procédures de ratchet, backlog cleanup, FAQ |
| `docs/SPRINT_Sb_26_1_REPORT.md` | Ce rapport |

### 2.2 Fichiers modifiés

| Fichier | Changement |
|---|---|
| `docs/strategy/Sx_26_..._SPEC.md` | Amendement §19 → ✅ TRANCHÉE + ajout §19bis (modèle OQ-1) |
| `.github/workflows/ci.yml` | Job `lint` réécrit : ruff budget + bandit -ll + actionlint + shellcheck **required** |
| `scripts/deploy_prod.sh` | 2 fixes shellcheck SC2027 (suppression doubles guillemets imbriqués lignes 54-55) |

### 2.3 Fichiers NON touchés (par contrat dur)

- `app/**` : aucune modification (interdiction "Ne touche pas au code métier")
- `tests/**` : aucune modification (interdiction "Ne casse pas pytest")
- `alembic/**`, `data/**` : aucune modification (interdiction migrations + features produit)
- `scripts/seed_db.py`, `scripts/catalog_qa.py`, `scripts/machine_atlas_qa.py`, `scripts/check_alembic_drift.py` : aucune modification
- `.github/workflows/deploy-production.yml`, `sonar-project.properties` : aucune modification

## 3. Décisions clés (Sx_26 §19bis)

### 3.1 OQ-1 — Tranchage

| Question | Tranchée |
|---|---|
| Modèle de gate ruff ? | **baseline locked + no new warnings** |
| Baseline B0 ? | **548 warnings mesurés au 2026-06-01** (≠ 478 estimés en Sx_26 §19 — voir §3.2) |
| Versioning ? | `.ruff-budget.json` à la racine (JSON commité) |
| Cleanup ? | **Pas dans Sb_26.1**. Sprints dédiés `Sb_26.next.ruff-cleanup-1..5` |
| Bump baseline ? | Interdit en sprint feature. Procédure formelle dans `docs/CI_QUALITY_BUDGET.md §7` |

### 3.2 Divergence baseline 478 vs 548 — note de transparence

L'estimation 478 dans Sx_26 §19 venait d'un comptage Sb_20.2 (advisory ruff). Mesure réelle au 2026-06-01 sur la branche courante : **548**. La consigne **non-négociable** "Ne corrige pas massivement les warnings ruff legacy" prime sur le chiffre estimé : la baseline est figée à la mesure réelle du jour. Si la divergence est un signal de dérive entre Sb_20.2 et Sb_26.1, c'est précisément ce que Sb_26.1 supprime à partir de maintenant.

Top 10 règles à la baseline (cf. `.ruff-budget.json`) : UP017 (147), I001 (145), UP045 (127), F401 (67), E402 (19), UP037 (8), F541 (8), E702 (8), F841 (5), C901 (4).

## 4. Job CI `lint` — nouvelle composition

| Step | Mode | Bloque CI ? | Justification |
|---|---|---|---|
| `ruff format --check .` | advisory | ❌ | formatter pas dans périmètre Sb_26.1 — futur sprint |
| `python scripts/check_ruff_budget.py` | **required** | ✅ | gate principale — fail si total > 548 |
| `bandit -r app/ -ll -f screen` | **required** | ✅ | projet 0 Med/0 High depuis Sb_20.2 — verrouillage |
| `reviewdog/action-actionlint@v1` (`fail_level: error`) | **required** | ✅ | empêche un workflow syntactiquement cassé d'arriver en main |
| `shellcheck -S warning scripts/*.sh` | **required** | ✅ | sécurise les scripts shell critiques (deploy_prod.sh, smoke, etc.) |
| ruff JSON + bandit JSON (upload artifact) | advisory | ❌ | consommés par SonarCloud |

Le job `test` (pytest + QA) et le job `sonar` (SonarCloud required) sont **inchangés** — aucune réduction de gate existante.

## 5. Tests et vérifications (DoD)

Exécutés localement le 2026-06-13 :

| Check | Résultat | Notes |
|---|---|---|
| `pytest --ignore=tests/test_v1_acceptance.py -q` | ✅ **907 passed** (4m25s) | aucun test cassé |
| `python scripts/catalog_qa.py` | ✅ OK | `warning_details: []` |
| `python scripts/machine_atlas_qa.py` | ✅ OK | `error_details: []` |
| `PYTHONPATH=. python scripts/check_alembic_drift.py` | ✅ "OK (no diff)" | comme en CI |
| `python scripts/check_ruff_budget.py` | ✅ "OK: ruff budget respected (548 ≤ 548)" | gate verte |
| `shellcheck -S warning scripts/*.sh` | ✅ exit 0 | après fix SC2027 |
| `ruff check scripts/check_ruff_budget.py` | ✅ clean | auto-fix du fichier que j'ai créé |

Validation CI réelle : voir §8 (post-push).

## 6. Auto-fix scope (très limité)

Deux corrections mineures introduites **uniquement** pour ne pas faire échouer les nouvelles gates required :

1. **`scripts/check_ruff_budget.py`** (fichier que j'ai créé) — 3 warnings auto-fixés (I001 + 2× F541) sur **mon propre fichier**. Aucune touche à du code legacy.
2. **`scripts/deploy_prod.sh` lignes 54-55** — suppression de guillemets doubles imbriqués (SC2027). Aucun changement de comportement : la chaîne affichée est identique, seule l'absence de l'effet "double quote inutile" change. Vérification : `shellcheck -S warning` repasse exit 0, le script n'est de toute façon exécuté qu'en prod via `deploy-production.yml`.

**Aucun fichier `app/`, `tests/`, `alembic/`, `data/` n'a été touché.**

## 7. Contraintes respectées

| Contrainte (verbatim user) | Statut |
|---|---|
| Ne touche pas au code métier | ✅ aucun fichier `app/` modifié |
| Ne corrige pas massivement les warnings ruff legacy | ✅ baseline figée, 0 fix legacy |
| Ne transforme pas Sb_26.1 en sprint de refactoring | ✅ scope CI/CD/tooling uniquement |
| Ne casse pas pytest + QA scripts | ✅ 907 tests verts, QA verts |
| Ne casse pas SonarCloud required | ✅ job `sonar` inchangé, JSON reports toujours upload |
| Ne supprime aucun step QA existant | ✅ tous steps `test` job intacts |
| Ne change pas le deploy production | ✅ `deploy-production.yml` non modifié, `deploy_prod.sh` change cosmétique uniquement |
| Ne change pas les migrations | ✅ `alembic/` non touché, drift check passe |
| Ne touche pas aux features produit | ✅ aucune route, template, service modifié |

## 8. CI réelle (post-push)

Run CI [#27478562739](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/27478562739) (commit `94438ad`) — conclusion **success** :

- [x] Job `pytest + QA scripts` — ✅ success
- [x] Job `lint (ruff budget + bandit + actionlint + shellcheck)` — ✅ success
- [x] Job `SonarCloud` — ✅ success
- [x] Pas de régression sur les status checks required

## 9. Limites assumées et reportées

| Item | Pourquoi pas dans Sb_26.1 | Reporté à |
|---|---|---|
| Gate "no new warning par fichier modifié" (granularité PR) | Complexité diff-based — V1 simple total suffisant | Sb_26.next |
| Lock ruff version exacte dans `requirements.txt` | Hors scope CI — concerne dépendances | Sb_26.next |
| Cleanup ruff legacy (548 → 0) | Hors scope ("pas de refactoring") | Sb_26.next.ruff-cleanup-1..5 |
| Cleanup formatter (`ruff format`) | Advisory en V1 — risque de churn énorme | Sb_27+ |
| Pre-commit hooks locaux | Hors scope CI Github Actions | Sb_26.next |
| Sx_26 §16 lots Sb_26.2 → Sb_26.7 | Lot suivant du cycle | Sb_26.2 |

## 10. Backlog immédiat (Sx_26 §16)

| Lot | Objet | Bloquant ? |
|---|---|---|
| **Sb_26.2** | Snapshot/migration hardening (drift CI sur PR, snapshot lockfile, rollback dry-run) | Non bloqué par Sb_26.1 |
| Sb_26.3 | Deploy/observability (alerting, /healthz/strict, deploy SHA tracking) | Non bloqué |
| Sb_26.4 | Security baseline (secrets scan, dep audit weekly) | Non bloqué |
| Sb_26.5 | Spec/process discipline (template Sx, lien Sx↔commits) | Non bloqué |
| Sb_26.6 | Performance baseline (p95 endpoints, slow query log) | Non bloqué |
| Sb_26.7 | Multi-tenant prep (read-only V1, scope auth) | Non bloqué |

## 11. Verdict

| Critère DoD | Statut |
|---|---|
| pytest passe | ✅ 907 passed |
| catalog_qa passe | ✅ |
| machine_atlas_qa passe | ✅ |
| check_alembic_drift passe | ✅ |
| ruff budget check passe | ✅ 548 ≤ 548 |
| aucun nouveau warning autorisé | ✅ (gate verrouillée) |
| SonarCloud reste required | ✅ (`ci.yml` job `sonar` non modifié) |
| rapport Sb_26.1 livré | ✅ (ce document) |

### ✅ **Sb_26.2 PRÊT**

Conditions de levée du flag :
- Sb_26.1 mergé en main
- CI verte sur PR Sb_26.1
- Statuts required mis à jour côté GitHub Settings (manuel) : ajouter `lint` aux required checks si pas déjà fait

---

**Co-Authored-By :** Claude Opus 4.7
