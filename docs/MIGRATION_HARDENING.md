# Migration Hardening — Sb_26.2

**Audience :** contributeurs SPIGNOS (humain + agent Claude Code).
**Créé :** 2026-06-13 (sprint Sb_26.2).
**Statut :** verrouille trois gates CI required autour des migrations Alembic.

---

## 1. Pourquoi

Sx_26 §6 a identifié trois dérives possibles sur la couche données :

1. **Drift silencieux** : modèle SQLAlchemy modifié, pas de migration → divergence runtime/schéma en prod.
2. **Migration non rejouable** : `downgrade()` cassé, impossible de faire un rollback opérationnel.
3. **Pattern destructeur** : `drop_column`, `op.execute("DELETE...")`, `NOT NULL` sans default — corruption de données existantes au upgrade.

Sb_26.2 ferme ces trois trous avec des gates CI **required** alimentées par des scripts dédiés. Aucune modification du modèle de données métier, aucune nouvelle migration, aucune touche à `app/`.

## 2. Architecture des gates

```
        ┌──────────────────────────┐
        │  Base.metadata (Python)  │
        └──────────────┬───────────┘
                       │
                       │  (1) check_alembic_drift.py
                       │       Base.metadata vs alembic head
                       ▼
        ┌──────────────────────────┐
        │  alembic head (runtime)  │
        └──────────────┬───────────┘
                       │
                       │  (2) check_schema_snapshot.py
                       │       alembic head vs committed snapshot
                       ▼
        ┌──────────────────────────┐
        │ data/schema_snapshot.sql │  ← source de vérité historique
        └──────────────────────────┘

   (3) check_migration_patterns.py   ← AST lint sur migrations/versions/*.py
   (4) check_migration_roundtrip.py  ← upgrade head → downgrade -1 → upgrade head
```

Sb_26.1 livrait (1). Sb_26.2 livre (2), (3), (4).

## 3. Composants livrés

### 3.1 Snapshot contractuel — `data/schema_snapshot.sql`

Source de vérité unique pour le schéma "head" attendu. Fichier généré, jamais édité à la main.

**Régénérer** (après toute nouvelle migration Alembic) :
```bash
python scripts/generate_schema_snapshot.py
git add data/schema_snapshot.sql
```

**Vérifier** (gate CI) :
```bash
python scripts/check_schema_snapshot.py
# OK: schema snapshot matches alembic head (schema_snapshot.sql).
```

Format : `CREATE TABLE` + `CREATE INDEX` triés par type/nom, normalisés en une ligne, commentés par bloc. La table `alembic_version` est exclue (elle change à chaque migration, sans valeur sémantique).

### 3.2 Linter de patterns dangereux — `scripts/check_migration_patterns.py`

Walk AST sur `migrations/versions/*.py`. Pour chaque `def upgrade()`, flagge :

| Règle | Niveau | Détection |
|---|---|---|
| `drop_column_in_upgrade` | **fail** | `op.drop_column(...)` ou `batch_op.drop_column(...)` |
| `drop_table_in_upgrade` | **fail** | `op.drop_table(...)` |
| `add_column_not_null_no_default` | **fail** | `add_column` avec `nullable=False` sans `server_default=` |
| `execute_delete_in_upgrade` | **fail** | `op.execute("DELETE ...")` |
| `execute_update_in_upgrade` | warn | `op.execute("UPDATE ...")` |
| `execute_alter_in_upgrade` | warn | `op.execute("ALTER ...")` |

Le linter respecte deux mécanismes d'exception :

**Allowlist** : fichiers historiques pré-Sb_26.2 listés dans `.migration-policy.json#grandfathered_files`. Les 17 migrations existantes sont grandfathered telles quelles — on **ne ré-écrit pas l'historique** (Sx_26 §11 hard contract).

**Justification inline** : un commentaire `# migration-justify: <raison>` placé dans les 3 lignes au-dessus de l'appel flaggé désactive l'alerte sur cette ligne. Exemple :

```python
def upgrade() -> None:
    # migration-justify: Sb_99 — table 'legacy_x' renommée en 'x_v2',
    # données déjà migrées via op.execute en amont (cf. sprint Sb_99).
    op.drop_table("legacy_x")
```

L'exigence du marker force le contributeur à **écrire la raison** plutôt qu'à l'avoir uniquement en tête.

### 3.3 Roundtrip / rollback dry-run — `scripts/check_migration_roundtrip.py`

Reproduit en CI exactement ce que ferait un opérateur en prod en cas de bug post-deploy :

```bash
# Modèle prod (deploy_prod.sh die() hint):
sudo -u workout alembic downgrade -1
# fix code
sudo -u workout alembic upgrade head
```

La gate :
1. `alembic upgrade head` (fresh SQLite)
2. `alembic downgrade -1`
3. `alembic upgrade head` (à nouveau)
4. compare le schéma pré/post — doit être identique

**Limites assumées (Sb_26.2 §3.3)** :

* Le **chemin complet** `head → base` n'est **pas** testé. Plusieurs `downgrade()` historiques utilisent `op.drop_table` sur des tables que SQLite/Alembic batch mode gère fragilement. Le modèle de rollback prod n'est de toute façon **jamais** "downgrade jusqu'à base" — c'est toujours "downgrade -1 puis redeploy".
* SQLite n'est pas PostgreSQL : `ALTER TABLE` y est limité, donc certains downgrades batchés peuvent passer en SQLite mais nécessiter validation en PG le jour d'une migration à venir. Ce sera couvert si/quand on bascule prod sur PG (hors scope Sb_26 — cf. Sx_26 §9).

## 4. Procédure pour ajouter une nouvelle migration

```bash
# 1. Modifier le modèle SQLAlchemy dans app/models/...

# 2. Générer la migration
alembic revision --autogenerate -m "Sb_XX.X — description"

# 3. Relire le fichier généré dans migrations/versions/<sha>_*.py
#    Si un pattern dangereux est nécessaire, ajouter le marker:
#    # migration-justify: Sb_XX — <raison>

# 4. Régénérer le snapshot
python scripts/generate_schema_snapshot.py

# 5. Vérifier localement
PYTHONPATH=. python scripts/check_alembic_drift.py
PYTHONPATH=. python scripts/check_schema_snapshot.py
PYTHONPATH=. python scripts/check_migration_patterns.py
PYTHONPATH=. python scripts/check_migration_roundtrip.py
PYTHONPATH=. pytest tests/test_migration_hardening.py tests/test_alembic_drift.py -q

# 6. Commit
git add migrations/versions/ app/models/ data/schema_snapshot.sql
git commit -m "feat(sb_XX_X): ..."
```

## 5. Procédure de rollback prod (dry-run documentée)

**Pré-requis** : avoir backupé la DB (le script `deploy_prod.sh` le fait automatiquement avant chaque deploy, cf. `var/backups/workout_pre_deploy_*.db`).

**Étapes opérateur** :

```bash
# Sur le VPS, dans /srv/workout :

# 1. Confirmer la migration à annuler
sudo -u workout /srv/workout/.venv/bin/alembic current
sudo -u workout /srv/workout/.venv/bin/alembic history --rev-range -3:current

# 2. Rollback d'une étape
sudo -u workout /srv/workout/.venv/bin/alembic downgrade -1

# 3. Revenir au commit précédent
sudo -u workout bash -c 'cd /srv/workout && git log --oneline -5'
sudo -u workout bash -c 'cd /srv/workout && git checkout HEAD~1'

# 4. Redémarrer le service
sudo systemctl restart workout

# 5. Vérifier
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/healthz
# Doit retourner 200

# 6. (Si rollback de données nécessaire — cas critique uniquement)
sudo systemctl stop workout
sudo cp /srv/workout/var/backups/workout_pre_deploy_<timestamp>.db /srv/workout/var/workout.db
sudo chown workout:workout /srv/workout/var/workout.db
sudo systemctl start workout
```

**Garantie CI** : avant tout deploy, la branche en CI a passé :
- `check_alembic_drift` → modèle et schéma alignés
- `check_schema_snapshot` → schéma identique à la baseline contractuelle
- `check_migration_patterns` → aucun pattern destructeur non justifié
- `check_migration_roundtrip` → `downgrade -1 + upgrade head` clean

Si une de ces gates échoue, **le PR ne peut pas merger**, donc le code en prod a forcément un rollback fonctionnel.

## 6. Contrats durs (verrouillés par Sb_26.2)

| Contrat | Mécanisme de verrouillage |
|---|---|
| Snapshots historiques `template_*_snapshot`, `exercise_*_snapshot`, `substituted_name`, `implicit_label` ne sont JAMAIS dropés | linter `drop_column_in_upgrade` + snapshot SQL figé |
| `scoring_version` reste monotone (jamais downgradé) | linter `execute_update_in_upgrade` warn + review humaine |
| ADD COLUMN ONLY est la convention par défaut | linter sur tous les nouveaux fichiers (grandfather pour historique) |
| Toute exception nécessite un marker `# migration-justify:` | enforcé par AST scan |
| Le rollback `downgrade -1` doit fonctionner | gate CI `check_migration_roundtrip` |
| Le schéma runtime ne peut diverger silencieusement du snapshot | gate CI `check_schema_snapshot` |

## 7. Backlog reportée

| Item | Pourquoi pas dans Sb_26.2 | Reporté à |
|---|---|---|
| Test roundtrip multi-step (downgrade -3 par ex) | V1 simple suffit, prod fait `-1` | Sb_26.next |
| Vérif compatibilité PostgreSQL (cross-engine snapshot) | SQLite uniquement en V1 ; PG hors Sx_26 | post-Sx_26 |
| Allowlist `op.execute("UPDATE ...")` par règle métier explicite | warn suffit ; review humaine en place | Sb_26.next |
| Test de migration sur DB pré-remplie (backfill validation) | Hors scope — fait au cas par cas dans le sprint qui livre la migration | Sb_27+ |
| Gate "no new migration sans tests pytest associés" | Difficile à automatiser proprement | Sb_27+ |

## 8. FAQ

> Pourquoi grandfather les 17 migrations existantes ?

Parce que les corriger demanderait soit (a) ré-écrire l'historique Alembic (interdit par Sx_26 §11 hard contract), soit (b) un sprint de cleanup massif sans valeur produit immédiate. La gate cible le **flux entrant** : à partir de Sb_26.2, toute nouvelle migration passe le linter ou justifie chaque exception.

> Pourquoi pas `downgrade jusqu'à base` ?

Voir §3.3. Le modèle de rollback prod n'utilise pas ce chemin, et plusieurs `downgrade()` historiques sont fragiles sur SQLite. Tester ce qu'on n'utilisera jamais en prod = test inutile.

> Si je casse le snapshot par erreur, que se passe-t-il ?

`scripts/check_schema_snapshot.py` affiche un diff unifié explicite. Soit la modif est intentionnelle (régénérer + commit), soit pas (revert la migration).

> Le linter peut-il être contourné en renommant le fichier de migration ?

Non — le scan parcourt tout `migrations/versions/*.py` sauf l'allowlist explicite par nom. Ajouter un nouveau fichier ne le met pas dans l'allowlist.
