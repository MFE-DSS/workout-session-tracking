# Sprint Sb_CUSTOM_PROGRAM_PERSISTENCE_03 — User Program Quality Review Persistence — BUILD

**Statut** : 🟢 **PATCH COMPLETE / REVIEW PENDING** (non commité, non poussé, CI non lancée)
**Type** : CODE BUILD — **dernière migration de persistance** du track (trace scoring figée)
**Date** : 2026-07-17
**Specs** : `Sx_CUSTOM_PROGRAM_03` §4/§9-C (modèle `QualityReview` + persistance Option C) + `04` §5/§7
**Branche** : `sb/custom-program-persistence-03-quality-reviews` (worktree dédié, **rebasée sur `edcad4e`** — closeout 02 poussé au préalable, séquence opérateur respectée)
**Préflight** : ✅ GO PATCH validé (head `m4n9h5i6k87`, arbitrage closeout tranché : push d'abord, jamais de mélange)

---

## 0. Étape 0 — Brainstorming / Options / Risques / Choix retenu

| Décision | Choix |
|---|---|
| Périmètre | **Réceptacle pur** : table + ORM, zéro calcul/seuil/microcopy — le moteur = `SCORING_01+` |
| `ekb_version` | **colonne dédiée nullable** (OQ-PERS-J tranchée : traçabilité requêtable, spec 03 §4) |
| `computed_at` | NOT NULL + `server_default=now()` — l'appelant surcharge, le moteur pur reste sans horloge (spec 03 §4) |
| Immutabilité | portée par **unique `(program, version)`** + discipline service future — non exigible en DB, documenté |
| Cascade | delete program → traces supprimées (cohérence d'arbre ; le soft delete reste la voie normale) |
| Séquence docs | closeout 02 poussé **avant** ce patch (`edcad4e`) — aucun mélange de statuts (décision opérateur) |

## 1. Patch appliqué

| Fichier | Nature |
|---|---|
| `app/models/user_program.py` | +1 classe `UserProgramQualityReview` (13 colonnes, docstring contractuelle « réceptacle only ») + relationship `quality_reviews` sur `UserProgram` (ordre `version`, `_TREE_CASCADE`) — seule retouche des modèles mergés = ORM, zéro schéma |
| `migrations/versions/20260717_add_user_program_quality_reviews.py` | **nouveau** — revision **`n5o0i6j7l98`** (revises `m4n9h5i6k87`), **ADD TABLE ONLY**, unique nommée `uq_user_program_quality_review_version`, index FK, guard idempotent, downgrade propre, zéro backfill/seed |
| `data/schema_snapshot.sql` | **+6 lignes additives** (régénéré) |
| `tests/test_user_program_quality_reviews_schema.py` | **nouveau** — 10 tests |

## 2. Tests (mandats couverts)

Existence + **13 colonnes exactes** · cascade delete program → reviews purgées · **unique
`(program, version)`** (IntegrityError sur doublon ; versions multiples et programmes
multiples OK) · `grade` NOT NULL · `scoring_version` NOT NULL · **round-trip des 5 payloads
JSON** (contenu réel sérialisé/relu) · `ekb_version` optionnelle + pinnable + `computed_at`
posé · **ordre relationnel par version** (insertion désordonnée 3-1-2 → lecture 1-2-3) ·
introspection **zéro FK hors arbre** (cible unique = `user_programs`).

| Vérification | Résultat |
|---|---|
| Dédiés | **10/10 premier coup** (7,6 s) |
| Adjacents/sentinelles (racine 9 + enfants 10 + wipe-guard 10 + hardening + session_schema) | **41/41** |
| `check_alembic_drift` / `check_schema_snapshot` / `check_migration_patterns` / `check_migration_roundtrip` (tous en `python -m`) | ✅ **4/4 premier coup** |
| ruff (3 fichiers) | clean |
| `check_ruff_budget` | **543 ≤ 548** |
| `check_spec_protocol` | PASS |
| `check_scope` | **MIGRATION** (attendu) |
| Full sweep local | lancé — verdict au GO COMMIT (rappel : le garde-fou arbre-sale rougira pré-commit par construction, preuve post-commit à refaire comme en 02) |

## 3. Risques résiduels

Immutabilité non exigible en DB (unique + discipline service, documenté) · table non
branchée (pattern fondation) · vocabulaire `grade` non contraint en DB (convention repo).

## 4. Confirmations de périmètre

✅ **Zéro moteur de scoring, zéro calcul, zéro seuil A/B/C, zéro microcopy** · ✅ zéro
API/UI/wizard/EKB/publication · ✅ `session_builder`/seed/data métier/catalogue intacts ·
✅ chantier UI et branche spec non touchés · ✅ 1 migration additive, head `n5o0i6j7l98`.

---

## Verdict

**Verdict :** 🟢 **Sb_CUSTOM_PROGRAM_PERSISTENCE_03 — PATCH COMPLETE / REVIEW PENDING.**

La **persistance du track est complète** : racine + arbre + traces scoring figées. La table
`user_program_quality_reviews` est un réceptacle pur (une row immuable par version publiée,
versions moteur/EKB pinnées, payloads explicables opaques) — tout le sens appartient au futur
moteur `SCORING_01+`. 10 dédiés premier coup, 41 sentinelles vertes, 4 QA verts premier coup.
Prochaines étapes : full sweep → GO COMMIT → PR (CI 3/3) → merge sur GO. **`PERSISTENCE_04`
(CRUD) et le reste de la queue restent NOT AUTHORIZED.**
