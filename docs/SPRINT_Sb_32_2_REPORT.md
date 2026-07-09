# Sprint Sb_32.2 — ExerciseMuscleMapping + classify_exercise DB lookup/fallback

**Statut** : 🟢 DELIVERED — pending GO commit + CI + human review
**Date** : 2026-07-08
**Cycle** : Sx_32 Deep Feature/Object Refactor (backend métier) — **in progress**
**Spec** : [`docs/strategy/Sx_32_MUSCLE_BODYZONE_MODEL_SPEC.md`](strategy/Sx_32_MUSCLE_BODYZONE_MODEL_SPEC.md)
**Sb_32.1** : ✅ HUMAN REVIEW ACCEPTED (commit `21c1149`) — fondation `BodyZone`/`Muscle` + baseline `classify_exercise`.
**Contrainte #1** : invariance historique — `classify_exercise` doit reproduire la baseline Sb_32.1 à l'identique.

---

## 0. Étape 0 — Brainstorming / Options / Risques / Choix retenu

> Étape obligatoire (règle permanente Sb_32.1) : raisonnement documenté AVANT code.

### Problème

Rendre la classification exercice→zone **relationnelle** (`ExerciseMuscleMapping`)
et offrir un chemin de classification **DB-backed**, sans changer d'un iota le
comportement de `classify_exercise(name)` (garde-fou = baseline Sb_32.1, 91 exercices).

### Découverte structurante (audit code réel)

`data/reference_split.json` **n'a pas de code d'exercice stable** : le champ
`code` est un **slot de jour d'entraînement** (E1…E7, 7 codes pour 91 lignes),
réutilisé entre exercices différents. La **seule identité stable par exercice
aujourd'hui est le `name`** — c'est précisément la clé de `classify_exercise`.
→ Décision : `exercise_code` de la table = **le nom d'exercice**. Ainsi le lookup
DB et le fallback substring sont keyés sur **la même valeur** → équivalence
prouvable contre la baseline. (OQ-32-A visait `exercise_code` : on l'implémente
avec l'identité réelle disponible, sans en inventer une.)

### Options comparées

| Option | Description | Verdict |
|---|---|---|
| **A** | `ExerciseMuscleMapping(exercise_code, body_zone_code, role, source, …)` + lookup DB **optionnel** + fallback substring conservé | ✅ **RETENU** |
| B | Mapping **DB-only**, sans fallback | ❌ REJETÉ : casse tout exercice hors backfill (unknown/nouveaux) → régression garantie ; viole « fallback substring conservé » |
| C | Cache global / seed runtime / import de la fixture `tests/` dans le service ou la migration | ❌ REJETÉ : dépendance `tests/` en prod, non déterministe, cache DB global fragile ; interdits par le brief |

### Évaluation (critères brief)

- **Risque consumers** : nul — les 7 callers appellent `classify_exercise(name)`
  (positionnel, name-only) ; les nouveaux paramètres sont **keyword-only** avec
  défaut `None` → signature 100% rétrocompatible.
- **Perf** : lookup indexé sur `exercise_code` ; name-only ne touche jamais la DB.
- **Testabilité** : lookup ↔ baseline testable exhaustivement (91 exercices).
- **Compat SQLite** : additive `CREATE TABLE`/`CREATE INDEX`, FK naturelles.
- **Robustesse migration** : backfill **statique généré au build** depuis la
  baseline (pas d'import runtime de la fixture) → déterministe ; guard `_table_exists`.
- **Extension future `body_map_descriptor`** : colonnes `role`/`source`/`muscle_code`
  (nullable) + FK `muscles.code` déjà prêtes.

### Choix retenu (synthèse)

Option **A**. `exercise_code = name`. Lookup DB optionnel, name-only inchangé,
fallback substring conservé, backfill statique déterministe depuis la baseline,
`muscle_code` NULL (aucune anatomie inventée), rôles `primary`/`secondary`
seulement. **Aucun consommateur muté.**

### Risques restants

- Un futur exercice absent du backfill retombe sur le substring (comportement
  voulu) ; sa migration vers un mapping explicite est un sous-sprint ultérieur.
- `exercise_code = name` devra être stabilisé en slug si le catalogue introduit
  un identifiant propre (documenté pour Sb_32.3+).

---

## 1. Objectif

1. Modèle `ExerciseMuscleMapping` (relation explicite exercice→zone).
2. Migration additive-only + backfill depuis la baseline Sb_32.1.
3. Chemin de classification DB-backed **optionnel** dans `classify_exercise`,
   avec fallback substring historique.
4. Preuve d'invariance : lookup DB **et** name-only reproduisent la baseline
   (91 exercices) à l'identique.

**Hors scope** (verrouillé) : aucune bascule de consommateur (coach / body
intelligence / scoring / substitution / readiness), aucune UI, aucun endpoint.

---

## 2. Changements effectués

### 2.1 `app/models/exercise_muscle_mapping.py` (NOUVEAU, 87 l.)

Table `exercise_muscle_mappings` : PK int + `exercise_code` (nom, `String(256)`) +
`body_zone_code` (FK `body_zones.code` `ON DELETE CASCADE`) + `muscle_code`
(FK `muscles.code` `ON DELETE SET NULL`, nullable) + `role` + `source` +
`position` (ordre secondaire) + `is_active` + `created_at`. `__table_args__` :
`UniqueConstraint(exercise_code, body_zone_code, role)` + 2 index (`exercise_code`,
`body_zone_code`).

### 2.2 `app/models/__init__.py` (MODIFIÉ) — enregistrement `exercise_muscle_mapping`.

### 2.3 `app/services/muscle_mapping.py` (MODIFIÉ)

- Extraction du substring historique en `_classify_exercise_by_patterns(name)`
  (comportement **inchangé**).
- Nouveau `_classify_exercise_by_lookup(db, exercise_code)` → lookup DB
  (`primary` + `secondary` ordonnés par `position`, `id`) ou `None`.
- `classify_exercise(name, *, exercise_code=None, db=None)` : si `db` **et**
  `exercise_code` fournis → lookup d'abord, fallback substring sinon. Sans eux →
  **strictement identique** à l'ancien substring. Format toujours `tuple[str, list[str]]`.

### 2.4 `migrations/versions/20260708_add_exercise_muscle_mapping.py` (NOUVEAU, 243 l.)

- `revision = "k2l7f3g4i65"`, `down_revision = "j1k6e2f3h54"`.
- `create_table` + 2 `create_index` (guard `_table_exists`).
- Backfill **87 lignes statiques** (`_BACKFILL_ROWS`, générées au build depuis la
  baseline, **pas** d'import runtime de `tests/`) : 65 primary + 22 secondary.
  `position` calculé par groupe (primary=0, secondary=1..n). `unknown` jamais inséré.
- `downgrade` : drop des 2 index + de la table uniquement.

### 2.5 `data/schema_snapshot.sql` (MODIFIÉ, +9 l. additives) — 1 table + 2 index.

---

## 3. Backfill (dérivé de la baseline Sb_32.1)

| Métrique | Valeur |
|---|---|
| Exercices baseline | 91 |
| Noms uniques (identité réelle) | 65 |
| Conflits de classification par nom | **0** |
| Lignes `primary` | 65 |
| Lignes `secondary` | 22 |
| **Total mapping rows** | **87** |
| `unknown` insérés | **0** (fallback conserve `unknown`) |

> Les 91 lignes baseline se dédupliquent en 65 noms d'exercice uniques (le même
> nom apparaît sous plusieurs slots E1…E7). Chaque nom mappe de façon **cohérente**
> (0 conflit), ce qui valide `exercise_code = name`.

---

## 4. Stratégie lookup / fallback

```
classify_exercise(name)                      → substring pur (INCHANGÉ, 0 DB)
classify_exercise(name, db=…, exercise_code=…):
    1. lookup ExerciseMuscleMapping[exercise_code] (rows actifs, ordre position)
    2. mapping trouvé   → (primary, secondary)  [même format]
    3. mapping absent   → fallback substring sur `name`
```

Callers existants (7 : `muscle_scoring`, `body_intelligence_inputs`,
`recommendation` ×2, `profile_metrics`, `session_recap`) appellent tous
`classify_exercise(name)` → **inchangés**, aucun ne passe `db`/`exercise_code`.

---

## 5. Preuve d'invariance (baseline Sb_32.1)

| Chemin | Résultat vs baseline (91 exercices) |
|---|---|
| DB lookup (`exercise_code` = name) | ✅ **0 divergence** |
| name-only `classify_exercise(name)` | ✅ **0 divergence** |
| Ordre des `secondary` | ✅ stable (piloté par `position`) |
| `unknown` sur catalogue | ✅ **0** (aucune régression) |

---

## 6. Tests exécutés

### 6.1 Nouveau fichier `tests/test_exercise_muscle_mapping.py` — 14/14 verts

Couvre les 17 exigences du brief : modèle (1) · migration crée uniquement la
table (2) · additive / aucune table existante mutée (3) · FK `body_zones.code`
valide + `muscle_code` nullable + 0 orphelin (4-5) · backfill count = baseline
known primary+secondary (6) · `unknown` non inséré + rôles {primary,secondary}
seulement (7) · DB lookup == baseline pour 91 (8) · name-only == baseline (9) ·
fallback si mapping absent (10) · format `tuple[str,list[str]]` (11) · ordre
secondary stable (12) · aucun fichier consommateur changé — git diff (13) ·
signature publique rétrocompatible, params keyword-only (14) · pas de régression
unknown (15). Roundtrip (16) + schema snapshot (17) couverts par
`test_migration_hardening.py`.

### 6.2 Checks d'intégrité (tous verts)

| check | résultat |
|---|---|
| `check_alembic_drift` | ✅ no diff |
| `check_schema_snapshot` | ✅ snapshot == head |
| `check_migration_patterns` | ✅ no dangerous pattern |
| `check_migration_roundtrip` | ✅ roundtrip clean |
| `check_spec_protocol` | ✅ pass |
| `check_ruff_budget` | ✅ **541 ≤ 548** (−1 : extraction du helper) |

### 6.3 Sweeps

- Targeted (foundation + mapping + hardening) : **67 passed**.
- Broad (`muscle/bodyzone/exercise_muscle/migration/schema/body_intelligence/coach/scoring/recommendation/profile_metrics/session_recap/catalog`) : **381 passed**.
- Full sweep CI-equivalent : **voir §Verdict** (lancé avant CR).

---

## 7. Invariants préservés

- `classify_exercise(name)` **byte-identique** à l'ancien (baseline 91/91).
- **Aucun** fichier consommateur touché (scoring / coach / body intelligence /
  substitution / readiness / recommendation / profile_metrics / session_recap).
- **Aucune** UI / endpoint / JS / rebrand.
- Migration **additive-only** (aucun DROP/RENAME/UPDATE/DELETE de données historiques).
- `muscles` toujours vide ; `muscle_code` NULL (aucune anatomie inventée).

---

## 8. Fichiers modifiés (whitelist respectée)

| Fichier | État |
|---|---|
| `app/models/exercise_muscle_mapping.py` | NOUVEAU |
| `app/models/__init__.py` | MODIFIÉ (1 import) |
| `app/services/muscle_mapping.py` | MODIFIÉ (lookup optionnel + fallback) |
| `migrations/versions/20260708_add_exercise_muscle_mapping.py` | NOUVEAU |
| `data/schema_snapshot.sql` | MODIFIÉ (+9 l. additives) |
| `tests/test_exercise_muscle_mapping.py` | NOUVEAU |
| `docs/SPRINT_Sb_32_2_REPORT.md` | NOUVEAU |
| `docs/strategy/SPEC_REGISTRY.md` | MODIFIÉ |
| `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` | MODIFIÉ |

Zones interdites (consumers/routers/templates/static/scripts/.github/deps) :
**intactes**. `tests/fixtures/classify_exercise_baseline.json` **inchangé**.

---

## 9. Limites (V1)

- **Consommateurs non migrés** : personne n'utilise encore le lookup DB en prod
  (bascule = sous-sprints suivants, prouvés non-régressifs).
- `exercise_code = name` (pas de slug propre tant que le catalogue n'en a pas).
- `muscle_code` NULL partout ; rôle `stabilizer` non peuplé (non inventé).

---

## 10. Next step — Sb_32.3

`body_map_descriptor` : contrat de représentation corporelle (agrégation
zone→descripteur consommable par UI Worked Area + coach), toujours **review-gated**
et sous garde de non-régression. **Non ouvert dans ce sprint.**

---

## Verdict

**Verdict :** 🟢 **Sb_32.2 ExerciseMuscleMapping + lookup/fallback livré, invariance prouvée — pending GO commit + CI + human review.**

La classification exercice→zone est désormais **relationnelle et backfillée depuis
la baseline Sb_32.1**, avec un chemin DB-backed **optionnel** qui reproduit la
baseline à l'identique (91/91, lookup et name-only) et un fallback substring
conservé. `exercise_code = name` (seule identité stable réelle) rend l'équivalence
prouvable. **Aucun consommateur muté, aucune UI, migration additive-only.** Le
vrai basculement des consommateurs reste un sous-sprint ultérieur. Prêt pour GO commit.
