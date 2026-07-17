# Sprint Sb_CUSTOM_PROGRAM_PERSISTENCE_02 — User Program Children Persistence — BUILD

**Statut** : 🟢 **PATCH COMPLETE / REVIEW PENDING** (non commité, non poussé, CI non lancée)
**Type** : CODE BUILD — deuxième migration du track (tables enfants, lot unique validé opérateur)
**Date** : 2026-07-17
**Specs** : `Sx_CUSTOM_PROGRAM_04` §5 (schéma enfants accepté champ par champ) + `BUILD_GATE_00` §4
**Branche** : `sb/custom-program-persistence-02-children` (worktree dédié, base canonique `a3a32c9`)
**Préflight** : ✅ GO PATCH validé (head `l3m8g4h5j76`, patron catalogue vérifié, lot unique décidé)

---

## 0. Étape 0 — Brainstorming / Options / Risques / Choix retenu

| Option | Description | Verdict |
|---|---|---|
| **A — Lot unique** (retenue, décision opérateur explicite) | 1 migration, 3 tables enfants — l'arbre est cohésif, spec 04 §17 le permet | ✅ |
| B — 3 migrations | split table par table | ❌ réservé au cas de blocage technique (non rencontré) |
| C — Ajouter aussi `quality_reviews` | 4e table | ❌ `PERSISTENCE_03` (dépend du contrat trace de la spec 03) |

Questions tranchées : classes ORM dans `user_program.py` (patron `catalog.py` : un module = un arbre) · relationships `back_populates` + cascade `delete-orphan` + `order_by` position/set_index (constante `_TREE_CASCADE` hissée — évite le code smell S1192 détecté à l'écriture) · `is_warmup` préparé mais default false partout V1 · **zéro FK catalogue/EKB** maintenu strictement.

Risque/parade critique : cascade à 4 niveaux → test de purge en chaîne complet ; profondeur ORM couverte par le patron catalogue éprouvé.

## 1. Patch appliqué

| Fichier | Nature |
|---|---|
| `app/models/user_program.py` | +3 classes (`UserProgramSession`, `UserProgramExercise`, `UserProgramRepTarget`) + relationship `sessions` sur la racine — patron catalogue strict |
| `migrations/versions/20260716_add_user_program_children.py` | **nouveau** — revision **`m4n9h5i6k87`** (revises `l3m8g4h5j76`), **ADD TABLE ONLY ×3**, uniques par parent, index FK, guards idempotents par table, downgrade enfants-d'abord |
| `data/schema_snapshot.sql` | **+18 lignes additives** (régénéré) |
| `tests/test_user_program_children_schema.py` | **nouveau** — 10 tests |

`app/models/__init__.py` **non modifié** (module déjà enregistré, comme mandaté).
**Différés** : `_quality_reviews` (`PERSISTENCE_03`), CRUD (`PERSISTENCE_04`), tout le reste de la queue.

## 2. Tests (mandats 1-12 couverts)

| Mandat | Test | Résultat |
|---|---|---|
| 1-2 existence + colonnes ×3 | `test_child_tables_exist` + `_have_expected_columns` | ✅ |
| 3 cascade program → arbre complet | `test_deleting_program_cascades_through_whole_tree` | ✅ |
| 4-6 uniques (session/exercise position, rep_target set) | 3 tests IntegrityError | ✅ |
| 7 defaults `strength` / `is_warmup=false` | `test_defaults_…` | ✅ |
| 8 zéro FK catalogue/EKB (introspection ×3) | `test_child_tables_have_no_fk_to_catalog_or_ekb` | ✅ |
| 9 ordre relationnel (insertion désordonnée → tri) | `test_relationships_ordered_…` | ✅ |
| 10 non-régression ownership racine | `test_root_ownership_isolation_still_holds` + `test_user_program_schema.py` (9) | ✅ |
| 11 non-régression migration/schema | `test_migration_hardening` + `test_session_schema` | ✅ |
| 12 non-régression seed wipe-guard | `test_seed_wipe_guard.py` (10) | ✅ |

**Dédiés : 10/10 premier coup** (5,6 s) · **adjacents : 43/43** · full sweep : lancé (verdict au GO COMMIT).

## 3. Checks

| Check | Résultat |
|---|---|
| `check_alembic_drift` (en `python -m`) | ✅ OK (no diff) — premier coup, leçon PERSISTENCE_01 appliquée |
| `check_schema_snapshot` | ✅ OK |
| `check_migration_patterns` | ✅ OK |
| `check_migration_roundtrip` | ✅ OK |
| ruff (3 fichiers touchés, dont fix UP037 + constante S1192) | clean |
| `check_ruff_budget` | **543 ≤ 548** |
| `check_spec_protocol` | PASS |
| `check_scope` | **MIGRATION** (attendu) |

## 4. Risques résiduels

Tables non branchées (assumé, pattern fondation) · vocabulaire `kind`/`status` non contraint en DB (convention repo, contrainte au service futur) · cascade 4 niveaux (testée en chaîne).

## 5. Confirmations de périmètre

✅ **Zéro API / UI / wizard / scoring / EKB / publication** · ✅ zéro `published_template_id` ·
✅ `session_builder`/seed/data métier/catalogue/auth intacts · ✅ chantier desktop rail et
branche spec non touchés · ✅ 1 migration additive, head unique `m4n9h5i6k87`.

---

## Verdict

**Verdict :** 🟢 **Sb_CUSTOM_PROGRAM_PERSISTENCE_02 — PATCH COMPLETE / REVIEW PENDING.**

L'arbre de persistance complet du programme utilisateur existe (racine + 3 enfants),
cascades et unicités prouvées, ordre relationnel garanti, zéro couplage catalogue/EKB,
4 checks QA migration verts du premier coup. Prochaines étapes : full sweep → GO COMMIT →
PR (CI 3/3) → merge sur GO. `PERSISTENCE_03+` et le reste de la queue restent NOT AUTHORIZED.

---

## Appendice — Post-merge : verdicts finaux (2026-07-17, closeout)

*Le corps du rapport reflète l'état au moment du build. Cet appendice acte la suite.*

- **Full sweep local** : terminé en 11:48 — **2281 passed, 1 failed** =
  `test_no_model_migration_schema_touched`, garde-fou du sprint UI worked-area qui exige
  zéro modif **non commitée** de models/migrations/snapshot (`git diff HEAD`) → rouge par
  construction sur tout sweep pré-commit d'un sprint de migration ; **14/14 vert
  post-commit** (prouvé). Verdict effectif : **sweep vert**. (Éclaire aussi le « hang »
  supposé des sweeps précédents : à consigner comme piège d'environnement.)
- **Commit** `819f17c` → **PR #24** → **CI PR `29571272500` : 3/3 GREEN premier coup**
  (pytest 2308 passed).
- **MERGE sur GO conditionnel opérateur** : **`0056baf`**, posé sur `ac16d49`
  (review UI 03.3).
- **CI canonique `29574276201` : 3/3 GREEN** — pytest **2308 passed, 2 warnings (27:27)** ·
  lint ✅ · SonarCloud ✅.
- **État final** : arbre de persistance Option C complet sur le trunk ; head Alembic
  **`m4n9h5i6k87`** ; 29 sentinelles track cumulées ; `PERSISTENCE_03` = FIRST NEXT BUILD
  CANDIDATE, NOT OPENED.
