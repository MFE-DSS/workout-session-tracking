# Sprint Sb_CUSTOM_PROGRAM_PERSISTENCE_01 — User Program Root Persistence — BUILD

**Statut** : 🟢 **BUILD READY FOR REVIEW** (non commité, non poussé, CI non lancée)
**Type** : CODE BUILD — **première migration du track** `Sx_CUSTOM_PROGRAM` (table racine)
**Date** : 2026-07-16
**Specs** : `Sx_CUSTOM_PROGRAM_04` §5-§8 (persistence) + `BUILD_GATE_00` §4 (ordre de build)
**Branche** : `sb/custom-program-persistence-01-user-programs` (worktree dédié, base canonique `79d11fd`)
**Préflight** : ✅ GO PATCH validé (Alembic head unique `k2l7f3g4i65`, conventions relevées, snapshot `data/` acknowledgé)

---

## 0. Étape 0 — Brainstorming / Options / Risques / Choix retenu

### Décision : table racine `user_programs` **seule**, 9 colonnes, zéro FK vers le catalogue

| Option | Description | Verdict |
|---|---|---|
| **A — Racine minimale** (retenue) | 9 colonnes (ownership, identité, statut, version, timestamps, soft delete), unique `(user_id, slug_base)`, 3 index ; **`published_template_id` différé** | ✅ razor-thin, zéro couplage seed/catalogue, une migration |
| B — Racine complète spec 04 | + `wizard_answers_json`, caches grade/score, `published_template_id` | ❌ champs sans consommateur avant wizard/scoring/publication ; FK catalogue prématurée |
| C — Racine + enfants d'un coup | 5 tables | ❌ viole « une migration par build » (gate + spec 04 §13) |

### Questions tranchées

| # | Question | Décision |
|---|---|---|
| 1 | `published_template_id` maintenant ? | **Non** — différé (zéro FK vers `workout_templates` dans ce lot → aucun couplage seed/catalog possible) |
| 2 | Unicité de `slug_base` | **`UNIQUE (user_id, slug_base)`** — prévient à la racine les collisions du futur slug publié `up{uid}-{slug_base}-v{n}` |
| 3 | `current_version` maintenant ? | **Oui** (default 1) — cœur du contrat de versioning (spec 04 §7), coût nul |
| 4 | Vocabulaire `status` | 4 valeurs documentées (constante `USER_PROGRAM_STATUSES`), **seul `draft` actif** tant que wizard/publication ne sont pas buildés |
| 5 | Snapshot `data/schema_snapshot.sql` | **Régénéré** (+12 lignes additives) — artefact QA de migration (précédent Sb_32.x), acknowledgé au préflight |

### Risque / parade critique

| Risque | Parade |
|---|---|
| CASCADE user → programs trop agressif | aligné sur l'existant (`WorkoutSession.user_id` CASCADE) ; testé (`test_deleting_user_cascades_to_programs`) ; aucun flux de suppression user actif en prod |
| Double head Alembic (agent parallèle) | head unique vérifié au préflight **et** au patch ; chantier UI = templates/CSS uniquement |

## 1. Objectif

Créer la **table racine** `user_programs` — première brique de persistance du modèle
Option C (`UserProgram*` = source de vérité d'édition, spec 04) : ownership dur, identité
minimale, statut brouillon, versioning, timestamps, soft delete. **Aucune structure
enfant, aucun consommateur** (le CRUD arrive en `PERSISTENCE_04`).

## 2. Patch appliqué

| Fichier | Nature |
|---|---|
| `app/models/user_program.py` | **nouveau** — modèle `UserProgram` (9 colonnes, contrats documentés dans le docstring : ownership NOT NULL, slug_base figé unique par user, statuts, nouveau cycle post-publication, soft delete) |
| `app/models/__init__.py` | +1 import (enregistrement `Base.metadata`) |
| `migrations/versions/20260716_add_user_programs.py` | **nouveau** — revision `l3m8g4h5j76` (revises `k2l7f3g4i65`), **ADD TABLE ONLY** : 1 table, unique `(user_id, slug_base)`, 3 index, guard `_table_exists` idempotent, downgrade propre (table vide non consommée), **zéro backfill, zéro seed, zéro table existante modifiée** |
| `data/schema_snapshot.sql` | **+12 lignes additives** (régénéré via `generate_schema_snapshot.py`) — artefact QA |
| `tests/test_user_program_schema.py` | **nouveau** — 9 tests |

**Différés (contrat)** : `user_program_sessions`/`_exercises`/`_rep_targets` (`PERSISTENCE_02`),
`_quality_reviews` (`PERSISTENCE_03`), CRUD (`PERSISTENCE_04`), `wizard_answers_json` +
caches score (builds wizard/scoring), `published_template_id` (ère publication).

## 3. Tests ajoutés (9) et exécutés

| Test | Couvre |
|---|---|
| existence table + colonnes exactes | schéma |
| defaults `draft` / version 1 / archived_at NULL | §5-6 spec 04 |
| timestamps server-side | conventions |
| `user_id` NOT NULL (IntegrityError) | ownership dur |
| **delete user → CASCADE programs** | §8 |
| unique `(user_id, slug_base)` (doublon → IntegrityError) | contrat slug |
| même slug_base entre users ≠ → OK | scoping correct |
| isolation des lectures par owner | §8 |
| **zéro FK vers le catalogue** (introspection : cible unique = `users`) | contrat PERSISTENCE_01 |

| Vérification | Résultat |
|---|---|
| Tests dédiés | **9/9, premier coup** (5,1 s) |
| Adjacents (migration_hardening, session_schema, auth, ownership) | **36 passed** |
| **check_alembic_drift** | ✅ OK (no diff) |
| **check_schema_snapshot** | ✅ OK (après régénération) |
| **check_migration_patterns** | ✅ OK |
| **check_migration_roundtrip** | ✅ OK |
| ruff (3 fichiers neufs) | clean |
| `check_ruff_budget` | **543 ≤ 548** |
| `check_spec_protocol` | PASS |
| Full sweep local | lancé (tier migration) — verdict consigné au GO COMMIT |

## 4. check_scope

**TIER : MIGRATION** — conforme à l'anticipation du préflight. Tous les checks du tier
exécutés et verts (dont les 4 `check_migration_*`) ; CI complète réelle = source de vérité
au push/PR.

## 5. Leçon d'environnement consignée (faux positif drift)

Premier run de `check_alembic_drift` **rouge à tort** : lancé `python scripts/...`,
l'import `app` résolvait vers le **repo principal** (install editable
`workout-session-tracking`) qui ne contient pas `user_program.py` → « remove_table »
fantôme. La forme prescrite par le docstring du script (**`python -m scripts.check_…`**,
cwd en tête de path) résout vers le worktree → **OK (no diff)**. Aucun impact CI (checkout
unique). À retenir pour tout build en worktree : **toujours invoquer les scripts QA en
`python -m`**.

## 6. Risques résiduels

| Risque | État |
|---|---|
| Table sans consommateur (code mort temporaire) | assumé par conception — pattern Sb_32.1/.2 (« fondation acceptée, non branchée ») ; CRUD = `PERSISTENCE_04` |
| Vocabulaire `status` non contraint en DB (String, pas CHECK) | convention repo (aucun enum DB ailleurs) ; la contrainte vit dans le service futur + constante |
| CASCADE user | testé ; aligné sur l'existant |

## 7. Confirmations de périmètre

✅ **1 migration, additive-only, ADD TABLE ONLY** · ✅ aucune table enfant · ✅ zéro FK
catalogue · ✅ aucun seed · ✅ `data/` = snapshot QA uniquement (+12, acknowledgé) ·
✅ aucune API/UI/wizard/scoring/EKB/matérialisation · ✅ `session_builder` intact ·
✅ chantier UI et branche spec non touchés · ✅ head Alembic unique (`l3m8g4h5j76`).

---

## Verdict

**Verdict :** 🟢 **Sb_CUSTOM_PROGRAM_PERSISTENCE_01 — BUILD READY FOR REVIEW** (pas accepted).

La racine `user_programs` existe : ownership dur testé (NOT NULL + CASCADE), identité
`slug_base` unique par user, statut/version avec defaults, soft delete, zéro couplage
catalogue. Migration `l3m8g4h5j76` idempotente et roundtrip-propre ; les 4 checks QA
migration verts ; 9 tests dédiés premier coup + 36 adjacents ; snapshot régénéré.
**Prochaines étapes : full sweep → GO COMMIT → GO PR DRAFT (CI 3/3) → GO VALIDATE.**
`PERSISTENCE_02+` et le reste de la queue restent NOT AUTHORIZED.
