# Sprint Sb_32.1 — BodyZone + Muscle Foundation + Backfill

**Statut** : 🟢 DELIVERED — pending GO commit + CI + human review
**Date** : 2026-07-08
**Cycle** : Sx_32 Deep Feature/Object Refactor (backend métier) — premier vrai code métier
**Spec** : [`docs/strategy/Sx_32_MUSCLE_BODYZONE_MODEL_SPEC.md`](strategy/Sx_32_MUSCLE_BODYZONE_MODEL_SPEC.md) (HUMAN REVIEW ACCEPTED, commit `47f3fac`)
**Contrainte #1** : invariance historique — aucun comportement métier existant ne change en `.1`.

---

## 0. Étape 0 — Brainstorming / Options / Risques / Choix retenu

> Étape obligatoire depuis Sb_32.1 : documenter le raisonnement AVANT d'écrire du code.

### Problème à cadrer

Formaliser les 11 zones corporelles aujourd'hui **hardcodées** dans
`app/services/muscle_mapping.py` (dicts `ZONE_LABELS` / `ZONE_MEASUREMENT` /
`ZONE_VOLUME_TARGET` / `RADAR_AXES`) en un **objet relationnel `BodyZone`**,
sans muter aucun consommateur (`classify_exercise` et tout le reste restent
inchangés). Préparer aussi la table `Muscle` pour la granularité fine à venir.

### Option A — Backfill dans la migration (`op.bulk_insert`), PK int + `code` unique **[RETENU]**

- Les 11 zones sont insérées **par la migration Alembic**, valeurs **dérivées
  à l'exécution** des constantes `muscle_mapping` (import du module dans la
  migration) → zéro valeur réécrite à la main, zéro divergence possible.
- PK int auto + colonne `code` unique (identité stable, robuste aux reseeds),
  strictement alignée sur **tous** les models existants (`readiness`,
  `body_consents`, etc.).
- Guard `_table_exists` (idempotent) ; backfill conditionné à la création.

### Option B — Seed runtime via `app/services/seed.py` **[REJETÉ]**

- `seed.py` est un **fichier de service INTERDIT** par la whitelist du sprint.
- Timing non déterministe (dépend d'un run de seed) vs migration qui garantit
  l'état dès `upgrade head`. Rejeté.

### Option C — `code` comme clé primaire (pas de PK int) **[REJETÉ]**

- Diverge de la convention du repo (PK int partout). Rejeté pour cohérence et
  pour ne pas compliquer les FK futures.

### Sous-décision — table `muscles` peuplée ou vide en V1 ?

- **Vide en V1 [RETENU]** : OQ-32-B (granularité analytique = Zone en V1) +
  OQ-32-F (aucune anatomie fine inventée). Peupler `muscles` exigerait
  d'inventer un mapping muscle→zone qui n'existe nulle part aujourd'hui →
  violerait « invariance / ne rien inventer ». Table **créée mais vide**,
  peuplement reporté à un sous-sprint sur sources explicites.

### Risques identifiés & parades

| Risque | Parade |
|---|---|
| Divergence backfill vs source de vérité | Backfill **dérivé** des constantes à l'exécution (jamais recopié) → impossible par construction. Test value-for-value en plus. |
| Zone `core` absente de `RADAR_AXES` → crash / valeur inventée | `radar_axis` **NULL** pour core (jamais forcé). Test dédié `test_core_zone_is_off_radar`. |
| Régression silencieuse de `classify_exercise` | **Baseline non-régression** figée (91 exercices) + test qui compare l'output courant à la baseline. |
| Mutation accidentelle d'une table existante | Test `test_no_existing_table_mutated` compare le schéma pré/post migration table par table. |
| Drift schema snapshot | `data/schema_snapshot.sql` régénéré ; `check_schema_snapshot` + `check_alembic_drift` verts. |

### Choix retenu (synthèse)

Option **A** + table `muscles` **vide V1**. Le plus conservateur : additive-only,
backfill dérivé de la vérité existante, aucun consommateur muté, invariance
prouvée par tests. `classify_exercise` intact — sa bascule vers un lookup DB est
explicitement reportée à `Sb_32.2`.

---

## 1. Objectif

Poser la **fondation relationnelle** du refactor Muscle/BodyZone :

1. Modèle `BodyZone` (première brique DB de la vérité zone/label/measurement/radar/volume).
2. Modèle `Muscle` (préparé, vide V1).
3. Migration additive-only : 2 tables neuves + backfill des 11 zones.
4. Baseline de non-régression `classify_exercise` (91 exercices catalogue).
5. Batterie de tests d'invariance.

**Hors scope `.1`** (verrouillé) : aucune bascule de `classify_exercise`, aucun
`ExerciseMuscleMapping`, aucun `body_map_descriptor`, aucune UI, aucun consommateur
(coach / body intelligence / scoring) touché.

---

## 2. Changements effectués

### 2.1 `app/models/body_zone.py` (NOUVEAU, 47 l.)

Modèle `BodyZone` — table `body_zones`. PK int + `code` unique + `label` +
`measurement_field` (nullable) + `radar_axis` (nullable) + `volume_target`
(nullable) + `is_active` (default `1`) + `created_at` (server_default `now()`).

### 2.2 `app/models/muscle.py` (NOUVEAU, 43 l.)

Modèle `Muscle` — table `muscles`. PK int + `code` unique + `name` +
`body_zone_code` (FK `body_zones.code` `ON DELETE SET NULL`, nullable) +
`category` (nullable) + `is_active` + `created_at`. **Vide en V1.**

### 2.3 `app/models/__init__.py` (MODIFIÉ)

Enregistrement de `body_zone` et `muscle` dans le tuple d'import du package
(ordre alphabétique) → `Base.metadata` peuplé pour `init_db` / Alembic.

### 2.4 `migrations/versions/20260708_add_bodyzone_muscle_tables.py` (NOUVEAU, 140 l.)

- `revision = "j1k6e2f3h54"`, `down_revision = "7i0f5d1e2g43"`.
- `upgrade()` : `create_table` body_zones + muscles (guards `_table_exists`) ;
  backfill des 11 zones via `op.bulk_insert`, lignes **dérivées des constantes
  `muscle_mapping`** par `_zone_backfill_rows()` (import à l'exécution).
- `downgrade()` : drop des 2 nouvelles tables uniquement (guards).
- **Additive-only** : aucun `DROP`/`RENAME`/`UPDATE`/`DELETE` de données
  existantes. `muscles` reste vide.

### 2.5 `tests/fixtures/classify_exercise_baseline.json` (NOUVEAU, 609 l.)

Snapshot de `classify_exercise()` pour les **91 exercices** du catalogue
(`data/reference_split.json`) : `code`, `name`, `primary`, `secondary`. Source
de vérité de la non-régression pour `Sb_32.2`.

### 2.6 `tests/test_bodyzone_muscle_foundation.py` (NOUVEAU, 235 l., 11 tests)

### 2.7 `data/schema_snapshot.sql` (MODIFIÉ, +6 l.)

Régénéré via `scripts/generate_schema_snapshot.py`. **Additif seulement** :
2 tables ajoutées (`body_zones`, `muscles`), aucune table existante modifiée.

---

## 3. Backfill des 11 zones (dérivé, non recopié)

| code | label | measurement_field | radar_axis | volume_target |
|---|---|---|---|---|
| pecs | Pectoraux | chest_cm | pecs | 16 |
| delt_lat | Deltoïdes latéraux | — | shoulders | 18 |
| delt_post | Deltoïdes postérieurs | — | shoulders | 10 |
| lats | Dos largeur | — | back_width | 16 |
| upper_back | Dos épaisseur | — | back_thickness | 16 |
| biceps | Biceps | arm_avg | arms | 10 |
| triceps | Triceps | arm_avg | arms | 10 |
| quads | Quadriceps | thigh_avg | lower | 16 |
| posterior | Ischios / Fessiers | thigh_avg | lower | 16 |
| calves | Mollets | — | lower | 10 |
| **core** | Core / Abdos | waist_cm | **— (NULL)** | 10 |

> `core` est la seule zone absente de `RADAR_AXES` → `radar_axis = NULL`
> (comportement existant préservé, jamais inventé).

---

## 4. Tests et vérification

### 4.1 Nouveaux tests (`test_bodyzone_muscle_foundation.py`) — 11/11 verts

Structure & modèles : `test_bodyzone_model_exists`, `test_muscle_model_exists`,
`test_migration_creates_only_new_tables`, `test_no_existing_table_mutated`.
Backfill : `test_bodyzone_backfill_matches_current_zone_constants`,
`test_bodyzone_backfill_preserves_labels_measurement_radar_volume`,
`test_core_zone_is_off_radar`, `test_muscle_table_created_and_empty_v1`.
Non-régression : `test_muscle_mapping_invariance_baseline_exists`,
`test_current_classify_exercise_matches_committed_baseline`,
`test_no_unknown_regression_on_catalog`.

### 4.2 Checks d'intégrité migration/schéma (tous verts)

| check | résultat |
|---|---|
| `scripts/check_alembic_drift.py` | ✅ no diff |
| `scripts/check_schema_snapshot.py` | ✅ snapshot == head |
| `scripts/check_migration_patterns.py` | ✅ no dangerous pattern |
| `scripts/check_migration_roundtrip.py` | ✅ roundtrip clean (26 objets identiques) |
| `scripts/check_spec_protocol.py` | ✅ pass |
| `scripts/check_ruff_budget.py` | ✅ 542 ≤ 548 (aucune dette ajoutée) |
| `tests/test_migration_hardening.py` + `test_alembic_drift.py` | ✅ 14 passed |

### 4.3 Full sweep (CI-equivalent, `--ignore=tests/test_v1_acceptance.py`)

```
1813 passed in 501.48s (0:08:21)
```

Roundtrip vérifié manuellement : `upgrade head` → 11 zones + muscles vide →
`downgrade -1` → 2 tables droppées, tables existantes préservées → `upgrade head`
→ 11 zones restaurées.

---

## 5. Fichiers modifiés (whitelist respectée)

| Fichier | État |
|---|---|
| `app/models/body_zone.py` | NOUVEAU |
| `app/models/muscle.py` | NOUVEAU |
| `app/models/__init__.py` | MODIFIÉ (2 imports) |
| `migrations/versions/20260708_add_bodyzone_muscle_tables.py` | NOUVEAU |
| `tests/fixtures/classify_exercise_baseline.json` | NOUVEAU |
| `tests/test_bodyzone_muscle_foundation.py` | NOUVEAU |
| `data/schema_snapshot.sql` | MODIFIÉ (+6 l. additives) |
| `docs/SPRINT_Sb_32_1_REPORT.md` | NOUVEAU (ce rapport) |
| `docs/strategy/SPEC_REGISTRY.md` | MODIFIÉ (statut Sb_32.1) |
| `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` | MODIFIÉ (statut Sb_32.1) |

Aucun fichier de zone interdite touché : `muscle_mapping.py`, `seed.py`, services,
routes, templates, CSS, `base.html` **inchangés**.

---

## 6. Limites et non-objectifs

- **`classify_exercise` NON migré** vers un lookup DB — reste substring-matching
  (bascule = `Sb_32.2`, prouvée non-régressive contre la baseline).
- **`muscles` vide** — aucun mapping muscle→zone inventé (sources explicites plus tard).
- Aucun `ExerciseMuscleMapping`, aucun `body_map_descriptor`, aucune UI, aucun
  consommateur (coach / body intelligence / scoring) touché.

---

## 7. Critères d'acceptation (DoD)

- [x] Étape 0 Brainstorming documentée dans le rapport.
- [x] Modèles `BodyZone` + `Muscle` créés, enregistrés dans `Base.metadata`.
- [x] Migration additive-only (2 tables neuves, guards idempotents, downgrade sûr).
- [x] Backfill des 11 zones dérivé des constantes existantes (value-for-value).
- [x] `muscles` vide V1.
- [x] Baseline non-régression `classify_exercise` (91 exercices) capturée + testée.
- [x] `classify_exercise` et tous les consommateurs inchangés.
- [x] `schema_snapshot.sql` régénéré (additif) ; drift/snapshot/patterns/roundtrip verts.
- [x] Ruff 542 ≤ 548 ; spec protocol vert.
- [x] Full sweep 1813 passed.
- [ ] **GO commit** (en attente).
- [ ] CI réelle verte (3/3) au push.
- [ ] Human review.

---

## 8. Synthèse exécutive

Première brique **relationnelle** de la refonte métier Sx_32 : les 11 zones
corporelles, jusqu'ici hardcodées, existent désormais en base (`body_zones`),
**backfillées depuis la vérité existante sans rien recopier ni inventer**. La
table `muscle` est prête (vide). **Aucun comportement métier ne change** : une
baseline de non-régression fige l'output actuel de `classify_exercise` pour que
`Sb_32.2` prouve l'équivalence exacte lors de la bascule vers un lookup DB.
Additive-only, roundtrip propre, 1813 tests verts. En attente de **GO commit**.

## 11. Verdict

🟢 **Fondation BodyZone/Muscle livrée V1, invariance prouvée — pending GO commit + CI + human review.**

La refonte métier Sx_32 démarre par sa brique la plus conservatrice : une
table `body_zones` backfillée **par dérivation** des constantes existantes (zéro
divergence possible), une table `muscles` créée mais vide (aucune anatomie
inventée), et **aucun consommateur muté**. L'invariance historique (contrainte
#1) est garantie à trois niveaux : (1) migration additive-only + roundtrip propre,
(2) test schéma table-par-table pré/post migration, (3) baseline non-régression
de `classify_exercise` sur les 91 exercices catalogue. Full sweep 1813 passed,
tous les checks migration/schéma/ruff/spec verts. Le vrai basculement fonctionnel
(`classify_exercise` → lookup DB) est explicitement reporté à `Sb_32.2`, qui
devra reproduire la baseline à l'identique. **Prêt pour GO commit.**
