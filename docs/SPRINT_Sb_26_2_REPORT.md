# Sb_26.2 — Snapshot / Migration Hardening (Sprint Report)

**Date :** 2026-06-13
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Spec parente :** `docs/strategy/Sx_26_ENGINEERING_CONTROL_PLANE_AND_ANTI_DRIFT_HARDENING_SPEC.md`
**Lot Sx_26 :** §16 — Sb_26.2 (Snapshot/Migration Hardening — deuxième lot du cycle)
**Statut :** ✅ Livré

---

## 1. Résumé exécutif

Sb_26.2 ferme trois dérives possibles autour des migrations Alembic (Sx_26 §6) sans toucher au modèle de données métier ni créer de nouvelle migration :

1. **Drift silencieux schéma/snapshot** → `check_schema_snapshot.py` + `data/schema_snapshot.sql`
2. **Pattern destructeur non justifié** → `check_migration_patterns.py` (AST lint, grandfathered list pour historique)
3. **Rollback non fiable** → `check_migration_roundtrip.py` (`downgrade -1 + upgrade head` sur fresh SQLite)

Les 3 nouvelles gates passent **required** dans le job `test` de la CI. La procédure de rollback opérationnelle est documentée verbatim.

**Verdict :** ✅ **Sb_26.3 PRÊT**.

## 2. Périmètre livré

### 2.1 Fichiers créés

| Fichier | Rôle |
|---|---|
| `data/schema_snapshot.sql` | Snapshot contractuel généré depuis alembic head (74 lignes, table `alembic_version` exclue) |
| `scripts/generate_schema_snapshot.py` | Génère le snapshot dans `data/schema_snapshot.sql` |
| `scripts/check_schema_snapshot.py` | Vérifie que snapshot committé == alembic head (diff unifié si mismatch) |
| `scripts/check_migration_patterns.py` | AST linter sur `migrations/versions/*.py` (drops, NOT NULL sans default, DELETE/UPDATE/ALTER raw) |
| `scripts/check_migration_roundtrip.py` | Rollback dry-run : upgrade head → downgrade -1 → upgrade head |
| `.migration-policy.json` | Politique : règles, severities, grandfathered list (17 migrations historiques) |
| `tests/test_migration_hardening.py` | 10 tests (linter + snapshot + roundtrip) intégrés au job `test` |
| `docs/MIGRATION_HARDENING.md` | Architecture des gates, procédures (nouvelle migration, rollback prod), contrats durs, FAQ |
| `docs/SPRINT_Sb_26_2_REPORT.md` | Ce rapport |

### 2.2 Fichiers modifiés

| Fichier | Changement |
|---|---|
| `.github/workflows/ci.yml` | Job `test` : ajout de 3 steps required (schema snapshot, migration patterns, migration roundtrip) après `Alembic drift check` |

### 2.3 Fichiers NON touchés (par contrat dur)

- `app/**` : **aucune** modification (interdiction "ne touche pas à app/routes métier", "ne touche pas aux templates produit", "ne modifie pas le modèle de données métier")
- `migrations/versions/**` : **aucune** modification (interdiction "ne crée pas de nouvelle migration Alembic sauf si absolument nécessaire" — aucune nécessité)
- `tests/test_alembic_drift.py`, `tests/test_scoring_version_migration.py` : non touchés
- `.github/workflows/deploy-production.yml` : non touché (interdiction "ne modifie pas le deploy production")
- `scripts/deploy_prod.sh` : non touché
- Tout module scoring / reco / substitution / coach report / body tracking : **aucun fichier touché**

## 3. Architecture des nouvelles gates (résumé)

```
Base.metadata ──(1)── alembic head ──(2)── data/schema_snapshot.sql
                          │
                          │ (3) check_migration_patterns.py (AST lint)
                          │ (4) check_migration_roundtrip.py (down -1 + up)
                          ▼
                  migrations/versions/*.py
```

| Gate | Couvre | Required ? |
|---|---|---|
| (1) `check_alembic_drift.py` | Modèle Python vs head | ✅ (depuis Sb_20.4) |
| (2) `check_schema_snapshot.py` | Head vs snapshot historique | ✅ **NEW Sb_26.2** |
| (3) `check_migration_patterns.py` | Patterns destructeurs | ✅ **NEW Sb_26.2** |
| (4) `check_migration_roundtrip.py` | Rollback fonctionnel | ✅ **NEW Sb_26.2** |

Détail complet : `docs/MIGRATION_HARDENING.md`.

## 4. Décisions clés

### 4.1 Grandfathered list vs cleanup historique

Les 17 migrations existantes utilisent abondamment `op.drop_column` / `op.drop_table` dans leurs `downgrade()`, ce qui est légitime (downgrade ⇒ supprimer ce que upgrade a ajouté). Le linter scanne aussi `upgrade()` où certains historiques font des `drop_column` (ex: `add_substitution`, `add_machine_atlas_links`) — pas destructeur en pratique car ce sont des colonnes ajoutées puis renommées dans le même cycle, mais le linter ne peut pas le savoir.

**Décision** : grandfather les 17 fichiers par nom dans `.migration-policy.json`. Justification :
- "Les snapshots historiques restent sacrés" (contrat dur) ⇒ on **ne ré-écrit pas l'historique** Alembic
- La gate cible le flux entrant — toute migration **future** passe le linter ou justifie chaque exception via `# migration-justify:`
- Cleanup rétroactif = sprint dédié post-Sx_26 (ou jamais, si l'historique fonctionne)

### 4.2 Marker `# migration-justify:` plutôt qu'allowlist par règle

Permet à l'opérateur d'écrire **la raison** au moment de coder la migration, plutôt que de cocher une case JSON déconnectée du code. La preuve de réflexion est dans le diff de la PR.

### 4.3 Roundtrip = `downgrade -1` uniquement

Pas de test `head → base → head`. Raisons (cf. `docs/MIGRATION_HARDENING.md §3.3`) :
- Le modèle de rollback prod n'utilise jamais ce chemin (`deploy_prod.sh die()` hint = `downgrade -1`)
- Plusieurs `downgrade()` historiques sont fragiles sur SQLite (batch + FK)
- Tester ce qu'on n'utilisera jamais = test inutile + brittle

### 4.4 Snapshot exclut `alembic_version`

Sinon le snapshot bouge à chaque ajout de migration sans information sémantique. Le snapshot reflète **le schéma métier**, pas la position de la migration courante.

## 5. Tests et vérifications (DoD)

Exécutés localement le 2026-06-13 :

| Check | Résultat | Notes |
|---|---|---|
| `pytest --ignore=tests/test_v1_acceptance.py -q` | ✅ **917 passed** (4m18s) | +10 nouveaux tests Sb_26.2 vs Sb_26.1 (907) |
| `python scripts/catalog_qa.py` | ✅ OK | `warning_details: []` |
| `python scripts/machine_atlas_qa.py` | ✅ OK | `error_details: []` |
| `PYTHONPATH=. python scripts/check_alembic_drift.py` | ✅ OK no diff | inchangé |
| `python scripts/check_schema_snapshot.py` | ✅ OK | snapshot matches head |
| `python scripts/check_migration_patterns.py` | ✅ OK | 0 unjustified pattern (17 grandfathered) |
| `python scripts/check_migration_roundtrip.py` | ✅ OK | `downgrade -1 + upgrade head` clean |
| `python scripts/check_ruff_budget.py` | ✅ OK | 548 ≤ 548 (en réalité 547 mesuré local — voir §6.2) |

Validation CI réelle : voir §8 (post-push).

## 6. Auto-fix scope (très limité)

### 6.1 Ruff budget : nouveaux fichiers nettoyés

`ruff check --fix` sur les 5 fichiers que j'ai créés :
- `scripts/generate_schema_snapshot.py`
- `scripts/check_schema_snapshot.py`
- `scripts/check_migration_patterns.py`
- `scripts/check_migration_roundtrip.py`
- `tests/test_migration_hardening.py`

5 warnings auto-fixés (I001 imports), 1 warning C901 manuel (refactor `_scan_file` en helpers `_check_drop` / `_check_add_column` / `_check_execute` — cleaner et passe la complexité 17→<15).

**Aucun fichier `app/`, `migrations/`, autre `tests/` n'a été touché.**

### 6.2 Effet sur la baseline ruff

Mesure pré-Sb_26.2 : 548. Mesure post-Sb_26.2 (incluant les 5 nouveaux fichiers cleaned + le refactor C901) : **547**.

Le script `check_ruff_budget.py` affiche `547 ≤ 548` → OK (gate verte).

**Contrat respecté** : "Si des warnings ruff diminuent, ne pas baisser la baseline dans ce sprint sauf commit séparé explicitement dédié." → la baseline reste à 548. La réduction de 1 sera consolidée dans un futur `Sb_26.next.ruff-cleanup-N` ou laissée comme marge.

### 6.3 SonarLint S1871 (branches identiques)

IDE diagnostic signalé : 2 branches identiques dans `main()` du linter de patterns. Mergées en une seule clause `or` — cleaner, comportement strictement identique.

## 7. Contraintes respectées

| Contrainte (verbatim user) | Statut |
|---|---|
| Ne touche pas à `app/routes` métier | ✅ aucun fichier `app/` modifié |
| Ne touche pas aux templates produit | ✅ aucun `.html` touché |
| Ne modifie pas le modèle de données métier sauf nécessité explicitement justifiée | ✅ aucune nécessité, aucune modif |
| Ne crée pas de nouvelle migration Alembic sauf si absolument nécessaire | ✅ 0 nouvelle migration |
| Ne modifie pas le deploy production | ✅ `deploy_prod.sh` et `deploy-production.yml` non touchés |
| Ne touche pas au scoring/reco/substitution/coach report/body tracking | ✅ aucun fichier de ces modules touché |
| Les snapshots historiques restent sacrés | ✅ snapshot SQL fige + linter `drop_column` fail |
| ADD COLUMN ONLY reste la convention par défaut | ✅ linter enforce, grandfather historique seulement |
| Toute exception doit être documentée dans une spec/amendment | ✅ marker `# migration-justify:` obligatoire |
| Aucun test existant ne doit être affaibli | ✅ 907 → 917 (10 ajoutés, 0 désactivé) |
| Le ruff budget ne doit pas dépasser 548 | ✅ 547 ≤ 548 |
| Si des warnings ruff diminuent, ne pas baisser la baseline dans ce sprint | ✅ baseline 548 inchangée |

## 8. CI réelle (post-push)

Run CI [#27479515017](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/27479515017) (commit `8cc8dd0`) — conclusion **success** :

- [x] Job `pytest + QA scripts` (pytest + QA + drift + **snapshot** + **patterns** + **roundtrip**) — ✅ success
- [x] Job `lint (ruff budget + bandit + actionlint + shellcheck)` — ✅ success
- [x] Job `SonarCloud` — ✅ success
- [x] Pas de régression sur les status checks required Sb_26.1

## 9. Limites assumées et reportées

| Item | Pourquoi pas dans Sb_26.2 | Reporté à |
|---|---|---|
| Test roundtrip multi-step (downgrade -3, -5) | V1 simple suffit ; prod fait `-1` | Sb_26.next |
| Vérif compatibilité PostgreSQL (cross-engine snapshot) | SQLite uniquement en V1 ; PG hors Sx_26 | post-Sx_26 |
| Allowlist `op.execute("UPDATE ...")` par règle métier explicite | warn suffit ; review humaine en place | Sb_26.next |
| Test migration sur DB pré-remplie (backfill validation) | Cas par cas dans le sprint qui livre la migration | Sb_27+ |
| Gate "no new migration sans tests pytest associés" | Difficile à automatiser proprement | Sb_27+ |
| Cleanup ruff baseline 548 → 547 (consolidation) | Hors scope (contrat : pas de baseline-down hors sprint dédié) | `Sb_26.next.ruff-cleanup-N` |
| Warnings Sonar pré-existants sur pip locking (S8541/S8544) | Hors scope Sb_26.2 (concerne dépendances, pas migrations) | Sb_26.4 (security baseline) |

## 10. Backlog immédiat (Sx_26 §16)

| Lot | Objet | Bloquant ? |
|---|---|---|
| **Sb_26.3** | Deploy / observability (alerting, /healthz/strict, deploy SHA tracking) | Non bloqué par Sb_26.2 |
| Sb_26.4 | Security baseline (secrets scan, dep audit weekly, pip locking) | Non bloqué |
| Sb_26.5 | Spec/process discipline (template Sx, lien Sx↔commits) | Non bloqué |
| Sb_26.6 | Performance baseline (p95 endpoints, slow query log) | Non bloqué |
| Sb_26.7 | Multi-tenant prep (read-only V1, scope auth) | Non bloqué |

## 11. Verdict

| Critère DoD | Statut |
|---|---|
| pytest passe | ✅ 917 passed (+10 vs Sb_26.1) |
| catalog_qa passe | ✅ |
| machine_atlas_qa passe | ✅ |
| check_alembic_drift passe | ✅ |
| ruff budget check passe | ✅ 547 ≤ 548 |
| lint job passe | ✅ |
| rapport sprint livré | ✅ (ce document) |
| aucune modification de code métier | ✅ |

### ✅ **Sb_26.3 PRÊT**

Conditions de levée :
- Sb_26.2 mergé en main
- CI verte sur le push
- Statuts required côté GitHub Settings : ajouter idéalement `test` (déjà required), aucune nouvelle gate à ajouter — les 3 nouveaux steps sont **internes** au job `test` déjà required

---

**Co-Authored-By :** Claude Opus 4.7
