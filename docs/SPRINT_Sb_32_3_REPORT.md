# Sprint Sb_32.3 — body_map_descriptor service contract

**Statut** : 🟢 DELIVERED — pending GO commit + CI + human review
**Date** : 2026-07-09
**Cycle** : Sx_32 Deep Feature/Object Refactor (backend métier) — **in progress**
**Spec** : [`docs/strategy/Sx_32_MUSCLE_BODYZONE_MODEL_SPEC.md`](strategy/Sx_32_MUSCLE_BODYZONE_MODEL_SPEC.md)
**Sb_32.1 / Sb_32.2** : ✅ HUMAN REVIEW ACCEPTED (`21c1149` / `19543b9`).
**Contrainte #1** : invariance historique — le descriptor reflète les zones déjà prouvées par Sb_32.2, aucun changement de classification/scoring.

---

## 0. Étape 0 — Brainstorming / Options / Risques / Choix retenu

> Étape obligatoire (règle permanente) : raisonnement documenté AVANT code.

### Problème

Exposer un **objet de représentation corporelle stable** (primary/secondary
zones + labels + statut) consommable plus tard par Worked Area UI, coach, body
intelligence et analytics — **sans brancher aucun consommateur**, sans modèle,
sans migration, sans UI. `muscle_mapping.py` est **lecture seule** ce sprint.

### Options comparées

| Option | Description | Verdict |
|---|---|---|
| **A** | Service **pur, non persistant** : `build_body_map_descriptor(...) -> dict` JSON-sérialisable, réutilise les helpers Sx_32 | ✅ **RETENU** |
| B | Table persistée `body_map_descriptor` | ❌ REJETÉ : exige modèle + migration + snapshot — **interdits** en `.3` ; le descriptor est dérivable, pas besoin de le matérialiser |
| C | Branchement direct UI/template depuis `ExerciseMuscleMapping` | ❌ REJETÉ : touche UI/consommateurs — **interdits** ; couple la présentation au modèle sans contrat stable |

### Sous-problème clé — `resolution_path` honnête sans modifier `classify_exercise`

`classify_exercise` n'expose pas quel chemin (lookup DB vs substring) a produit
le résultat, et il est **read-only** ce sprint. Plutôt que deviner ou mentir, le
service **ré-appelle les mêmes helpers privés dans le même ordre** :

1. `_classify_exercise_by_lookup(db, exercise_code)` → `resolution_path = "db_lookup"`
2. sinon `_classify_exercise_by_patterns(name)` → `"substring_fallback"`
   (ou `"unknown"` si résultat = `("unknown", [])`)

→ les zones du descriptor sont **garanties identiques** à `classify_exercise`
(mêmes helpers, même ordre) **et** `resolution_path` ne ment jamais. C'est le
cœur de la conception.

### Évaluation (critères brief)

- **Stabilité contrat** : shape fixe (10 clés toujours présentes), JSON-sérialisable.
- **Coût migration** : nul (aucune persistance).
- **Compat no-JS/SSR** : dict pur, aucune dépendance runtime UI.
- **Testabilité** : invariance vérifiable sur les 2 chemins vs baseline (91).
- **Aucun consumer migré** : personne n'appelle le service en prod.
- **Compat future UI Worked Area** : `zones[]` (code/label/role) directement mappable.

### Choix retenu (synthèse)

Option **A**. Service pur, dict de sortie, `resolution_path` dérivé honnêtement
des helpers Sx_32. Labels depuis `BodyZone` si DB, sinon `ZONE_LABELS`. Unknown →
`"À qualifier"` (aucune zone inventée, aucun muscle fin, aucun stabilizer, aucune
allégation médicale).

### Risques / limites

- `resolution_path` réplique la logique de `classify_exercise` : si un futur
  sprint change cette logique, le descriptor doit être re-synchronisé (couvert
  par les tests d'invariance baseline).
- Descriptor **non branché** en prod (par conception `.3`).
- Pas de persistance : recalculé à chaque appel (acceptable, coût O(1) lookup indexé).

---

## 1. Objectif

Fournir le **contrat + la logique service** d'un `body_map_descriptor`, sans
brancher aucun consommateur, en garantissant que les zones reflètent la baseline
Sb_32.1 / le lookup Sb_32.2.

**Hors scope** (verrouillé) : aucun modèle, migration, schema snapshot, endpoint,
UI Worked Area, template, CSS, JS ; aucun changement `classify_exercise` /
scoring / coach / body intelligence / substitution / readiness ; aucun rebrand.

---

## 2. Changements effectués

### 2.1 `app/services/body_map_descriptor.py` (NOUVEAU)

- `build_body_map_descriptor(name, *, exercise_code=None, db=None) -> dict`.
- `_resolve_zones(...)` : réutilise `_classify_exercise_by_lookup` puis
  `_classify_exercise_by_patterns` (même ordre que `classify_exercise`) →
  `(primary, secondary, resolution_path)`.
- `_label_for(code, db)` : `BodyZone.label` si DB, sinon `ZONE_LABELS`, sinon code.
- Dédup des secondary (jamais de doublon, jamais = primary), ordre stable.
- Unknown → descriptor `status="unknown"` + `"À qualifier"` + `needs_qualification=True`.

### 2.2 `tests/test_body_map_descriptor.py` (NOUVEAU, 16 tests)

**Aucun autre fichier touché** (service pur).

---

## 3. Contrat descriptor (shape fixe, JSON-sérialisable)

```json
{
  "status": "mapped" | "unknown",
  "primary_zone": "pecs" | ... | "unknown",
  "primary_label": "Pectoraux" | "À qualifier",
  "secondary_zones": ["triceps", ...],
  "secondary_labels": ["Triceps", ...],
  "zones": [{"code","label","role":"primary"}, {"code","label","role":"secondary"}, ...],
  "source": "db_lookup" | "substring_fallback" | "unknown",
  "resolution_path": "db_lookup" | "substring_fallback" | "unknown",
  "is_qualified": true|false,
  "needs_qualification": true|false
}
```

- **Primary en premier**, secondary en ordre stable, **pas de doublon**.
- **Unknown ne crée aucune zone** (`zones=[]`), `primary_label="À qualifier"`.
- **Stabilizer / muscle fin non inventés** ; **aucune allégation médicale**.
- `source` == `resolution_path` (miroir explicite ; jamais deviné).

---

## 4. Preuve d'invariance (baseline Sb_32.1)

| Chemin | vs baseline (91 exercices) |
|---|---|
| name-only (substring) | ✅ **0 divergence** ; `resolution_path=substring_fallback` |
| DB lookup (`exercise_code`=name) | ✅ **0 divergence** ; `resolution_path=db_lookup` (91/91) |
| Labels DB (BodyZone) | ✅ résolus (`Pectoraux`, `Triceps`, …) |
| Labels fallback (`ZONE_LABELS`) | ✅ identiques sans DB |
| Unknown | ✅ `status=unknown` + `"À qualifier"`, aucune zone |

---

## 5. Tests exécutés

### 5.1 `tests/test_body_map_descriptor.py` — 16/16 verts

mapped (1) · unknown/À qualifier (2) · primary==baseline (3) · secondary==baseline
(4) · db-lookup==baseline + tous `db_lookup` (5) · fallback sans db==baseline (6) ·
labels BodyZone si db (7) · labels `ZONE_LABELS` sinon (8) · pas de doublon (9) ·
ordre primary-then-secondary (10) · aucun fichier model/migration/schema touché
(11) · aucun consommateur touché (12) · aucun fichier UI touché (13) · aucune
allégation médicale (14) · JSON-sérialisable (15) · contrat de shape/type (16).

### 5.2 Checks (verts, inchangés)

| check | résultat |
|---|---|
| `check_ruff_budget` | ✅ 541 ≤ 548 (aucune dette ajoutée) |
| `check_spec_protocol` | ✅ pass |
| `check_alembic_drift` | ✅ no diff |
| `check_schema_snapshot` | ✅ matches head |
| `check_migration_patterns` | ✅ no dangerous pattern |
| `check_migration_roundtrip` | ✅ clean |

### 5.3 Sweeps

- Targeted (descriptor + mapping + foundation) : verts.
- Broad (`body_map/muscle/bodyzone/exercise_muscle/body_intelligence/coach/scoring`) : **283 passed**.
- Full sweep CI-equivalent : **voir §Verdict**.

---

## 6. Invariants préservés

- `classify_exercise` (name-only) et scoring/coach/body intelligence/substitution/
  readiness **inchangés** — aucun de leurs fichiers touché.
- **Aucun** modèle / migration / schema snapshot (checks migration inchangés verts).
- **Aucune** UI / endpoint / template / CSS / JS / rebrand.
- Zones du descriptor **prouvées == baseline** sur les 2 chemins.

---

## 7. Fichiers modifiés (whitelist respectée)

| Fichier | État |
|---|---|
| `app/services/body_map_descriptor.py` | NOUVEAU |
| `tests/test_body_map_descriptor.py` | NOUVEAU |
| `docs/SPRINT_Sb_32_3_REPORT.md` | NOUVEAU |
| `docs/strategy/SPEC_REGISTRY.md` | MODIFIÉ |
| `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` | MODIFIÉ |

Zones interdites (models/migrations/schema/muscle_mapping/consommateurs/routers/
templates/static/scripts/.github/deps) : **intactes**. Aucun artefact.

---

## 8. Limites (V1)

- Descriptor **non branché** — aucun consommateur ne l'appelle (par conception).
- Pas de persistance (recalcul à la demande).
- `muscle_code` / stabilizer non exposés (aucune anatomie inventée).

---

## 9. Next step

Deux pistes possibles (arbitrage opérateur, aucune ouverte ici) :
- **Sb_32.4** : migration des consommateurs (coach / body intelligence / scoring)
  vers le lookup DB + le descriptor, prouvée non-régressive.
- **Sprint UI Worked Area** : consommer le descriptor dans le template Worked Area
  (SSR/CSS), review-gated.

**Aucun des deux n'est ouvert dans ce sprint.**

---

## Verdict

**Verdict :** 🟢 **Sb_32.3 body_map_descriptor livré, contrat stable + invariance prouvée — pending GO commit + CI + human review.**

Le contrat de représentation corporelle existe : un service **pur, non
persistant, JSON-sérialisable**, qui dérive un descriptor stable (primary/
secondary + labels + statut) des mappings Sx_32, avec un `resolution_path`
**honnête** (db_lookup / substring_fallback / unknown) et un état explicite
`"À qualifier"` pour l'inconnu — **sans inventer d'anatomie ni d'allégation
médicale**. Zones prouvées **== baseline 91/91** sur les deux chemins. **Aucun
consommateur, aucune UI, aucun modèle/migration.** Prêt pour GO commit.
