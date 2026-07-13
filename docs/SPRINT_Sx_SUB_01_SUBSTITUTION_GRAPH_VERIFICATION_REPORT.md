# Sprint Sx_SUB_01 — Substitution Graph Verification / Gap Closure (VERIFICATION)

**Statut** : 🟢 **VERIFIED — ALREADY DONE (verification-only, no code)** ; batch local, non commité
**Type** : AUDIT / VERIFICATION FIRST — docs-only (moteur déjà conforme)
**Date** : 2026-07-13
**Cycle** : batch local (à la suite de Sx_CAT_01 + Sx_FB_01, non commités)
**Références** : `app/services/substitution.py`, `data/exercise_properties.json`, `data/cross_pattern_substitutions.json`, `docs/strategy/SPIGNOS_EXERCISE_SUBSTITUTION_GRAPH_SPEC.md`, `SPIGNOS_SUBSTITUTION_GAP_PACK_SPEC_v1.md`
**Préconditions** : `Sx_UI_07.2` ACCEPTED ✅ ; Sx_CAT_01 + Sx_FB_01 livrés localement (préservés) ✅ ; CI timeout 45 ✅ ; BI deferred ✅.

---

## 0. Résumé exécutif

Le brief demande de **vérifier** que le graphe de substitution est conforme à
l'architecture cible (N1 strict / N2 même pattern / N3 zone-only ou bridge
cross-pattern ; aucun cross-pattern promu N1/N2 ; Sx_CAT_01 ne dégrade pas le graph).
**L'audit prouve que le moteur est DÉJÀ ENTIÈREMENT CONFORME** (Sb_22a v1.1), avec la
garde anti-cross-pattern **hard-enforced** et **30+ tests** qui verrouillent les
invariants. **Sx_CAT_01 a un impact NUL** sur la substitution.

**Statut retenu : Option A — verification-only. Aucun code, aucun test, aucune data
touchés.**

---

## 1. Étape 0 — Brainstorming / Options / Choix retenu

### Options

| Option | Description | Verdict |
|---|---|---|
| **A** | Verification-only (moteur conforme) | ✅ **RETENU** |
| B | Tests-only hardening | ❌ non nécessaire (30+ tests couvrent déjà les invariants) |
| C | Micro-patch data-only | ❌ aucune anomalie data prouvée |
| D | Refactor substitution.py | ❌ rejeté (aucun bug) |

### 15 sujets clivants — tranchés par l'audit

1. **Verification-only** (moteur conforme).
2. **Moteur N1/N2/N3 existe entièrement** (`substitution.py`, Sb_22a v1.1).
3. **Bridges cross-pattern déjà lus** (`load_cross_pattern_bridges()`, `@lru_cache`).
4. **Bridges = N3 uniquement** (utilisés seulement dans le pool N3).
5. **N1 explicites ne peuvent PAS traverser un pattern moteur** → démotées en N3.
6. **Substitution explicite historique large** → démotée silencieusement en N3 (legacy compat).
7. **Ne pas ajouter de bridge** (2 bridges existants suffisent ; 0 gap prouvé).
8. **exercise_properties non touché** (aucun gap).
9. **reference_split non touché** (Sx_CAT_01 préservé, aucune nécessité).
10. **Pas de test dédié** (les existants verrouillent tout).
11. **substitution.py non touché.**
12. **catalog_pattern_qa.py non touché.**
13. **Historique stable** : substitutions passées via `substituted_name` (snapshot), aucun backfill.
14. **Drawer non bruyant** : caps MAX_N2=5 / MAX_N3=5, dedup, badges stables.
15. **Fin de batch** : recommandation GO BATCH COMMIT + CI (voir §12).

**Choix : Option A** — verification-only.

---

## 2. Audit du moteur actuel (`substitution.py`)

### 2.1 Contrat N1/N2/N3 (conforme)

| Niveau | Règle | Enforcement |
|---|---|---|
| **N1** — Équivalence stricte | liste curée explicite (`substitutes_json`), classée : N1 **uniquement** si match 4-dim (`pattern_motor` + `zone_primary` + `equipment_family` + `chain`) ; sinon démotée N3 | `_add_curated_suggestion` / `_classify_suggestion` |
| **N2** — Fallback proche | **même `pattern_motor`** ET proximité ≥ `PROXIMITY_THRESHOLD_N2` (50) | filtre pattern à la collecte ; invariant defense-in-depth |
| **N3** — Zone-only / bridge | même `zone_primary` mais **pattern différent**, OU bridge cross-pattern (`from_pattern` match) | pool N3 |

Proximité (`compute_proximity`) : zone +50 · pattern +20 · equipment +15 · chain +10 ·
muscle_group +10 (si les deux non-null) → **max 95**.

### 2.2 Garde anti-cross-pattern (HARD-ENFORCED)

Preuve — un exercice de `pattern_motor` différent ne peut **jamais** apparaître en N1/N2 :
1. **N2 collecte** : `if cand_props.get("pattern_motor") != origin_pattern: continue` → exercices d'un autre pattern **exclus** de N2.
2. **Invariant defense-in-depth (N2)** : un candidat même-pattern qui classifierait N3 → `raise ValueError` (attrape toute incohérence du classifier).
3. **N3 zone-only** : `if cand_props.get("pattern_motor") == origin_pattern: continue` → même-pattern exclu du pool zone-only (il appartient à N2).
4. **Curated cross-pattern** : démoté **silencieusement** en N3 (legacy v13, jamais d'exception).

### 2.3 Robustesse

- **Caps** : `MAX_N2 = 5`, `MAX_N3 = 5`.
- **Dedup** : `seen: set[str]` central (origine + toutes suggestions) → aucun doublon inter/intra-niveau.
- **Tolérance exercice absent** : sans propriétés registry → **N1 curated seul**, aucune erreur ; sub curée absente du registry → ajoutée en N1 (fallback gracieux).
- **Labels stables** : `BADGE_N1="Équivalent"`, `BADGE_N2="Proche"`, `BADGE_N3="Élargi"`.
- **Rationales** : N2 (« même pattern · … ») ; N3 zone-only (« même zone · autre pattern ») ; N3 bridge (« intention proche : … »).

### 2.4 Data sources & cache

- `load_exercise_properties()` : `exercise_properties.json`, `@lru_cache(maxsize=1)`, **valide `pattern_motor`** contre l'enum fermé (11 valeurs) → `ValueError` si invalide.
- `load_cross_pattern_bridges()` : `cross_pattern_substitutions.json`, `@lru_cache(maxsize=1)`.

---

## 3. Audit data

### 3.1 `exercise_properties.json` (53 exercices)
Contient `pattern_motor`, `zone_primary`, `equipment_family`, `chain`, `muscle_group`
(optionnel). **Ne contient PAS** `machine_family`/`machine_slug`. Chaque `pattern_motor`
validé à la charge.

### 3.2 `cross_pattern_substitutions.json` (2 bridges)
Structure `bridges` : `from_pattern`/`to_pattern`/`intent`/`exercises_from`/`exercises_to`.
2 bridges **bidirectionnels** rowing (`pull_horizontal`) ↔ tirage vertical
(`pull_vertical`). **Utilisés uniquement en N3**, chacun avec un `intent`.

### 3.3 Soft warnings `catalog_pattern_qa` (préexistants, non bloquants)
3 soft warnings (QA **exit 0**, pas des erreurs) : `pull-b` a des subs curées
`pull_vertical` sur des origines `pull_horizontal` (« migrate to
cross_pattern_substitutions.json »). **Ces warnings concernent des exercices Rowing
(pull-b), PAS les 3 exercices Sx_CAT_01** → **préexistants et indépendants** de ce
batch. Le moteur les gère gracieusement (démotion N3). Documentés comme cleanup
candidate futur, **hors périmètre** de ce sprint verification-only.

---

## 4. Preuve N1/N2/N3 (tests existants)

`tests/test_substitution_tiered.py` (+ `test_substitution.py`) — **41 tests verts** —
verrouillent notamment :
- enum pattern_motor 11 valeurs · proximité 95/20/50 ;
- **`test_n2_candidate_with_different_pattern_is_never_promoted`** (contrat dur N1/N2) ;
- `test_curated_cross_pattern_demoted_to_n3` ;
- `test_rowing_bridges_to_tirage_vertical_in_n3` · `test_n3_bridge_carries_intent_rationale` ;
- caps, dedup (`test_origin_never_suggests_itself`), immutabilité, unknown origin → curated only.

---

## 5. Preuve — cross-pattern reste N3

Filtre N2 (pattern != origin → continue) + démotion curated cross-pattern → N3 +
bridges lus uniquement dans le pool N3. Verrouillé par
`test_n2_candidate_with_different_pattern_is_never_promoted` et
`test_rowing_bridges_to_tirage_vertical_in_n3`.

---

## 6. Preuve — Sx_CAT_01 ne casse pas le graph (impact NUL)

**Question clé** : les corrections Sx_CAT_01 (`machine_family`/`machine_slug` dans
`reference_split.json`) affectent-elles la substitution ?

**Réponse : NON — impact NUL.**
- `substitution.py` **ne lit jamais** `machine_family` ni `machine_slug` :
  `grep 'machine_family\|machine_slug' substitution.py` → **0 résultat**.
- Il lit **uniquement** `pattern_motor`/`zone_primary`/`equipment_family`/`chain`/
  `muscle_group` depuis **`exercise_properties.json`** — un fichier **différent** de
  `reference_split.json`.
- Les champs machine de `reference_split.json` alimentent `seed.py` (snapshot DB),
  `overload_inputs.py`, `machine_atlas.py` — **jamais** la substitution.
- Tests substitution : **41 passed** avec Sx_CAT_01 dans le working tree (0 régression).

---

## 7. Preuve — historique stable

Les substitutions passées sont portées par `substituted_name` (snapshot sur
`SessionExercise`) — aucune re-résolution du graphe pour l'historique. **Aucun
backfill, aucune migration, aucun recalcul.** Le graphe ne s'applique qu'à la
**suggestion** de nouvelles substitutions.

---

## 8. Statut retenu

**ALREADY DONE (verification-only).** Le moteur est conforme, les invariants sont
verrouillés par 30+ tests, aucun micro-gap data, aucune sentinelle critique manquante.
Pas de Option B (tests) ni C (data) nécessaires.

---

## 9. Fichiers modifiés

**AUCUN fichier applicatif / test / data touché.** Ce sprint = **verification-only** :
rapport + registry + roadmap (docs). `substitution.py`, `exercise_properties.json`,
`cross_pattern_substitutions.json`, `catalog_pattern_qa.py`, `reference_split.json`
(Sx_CAT_01 préservé) : **inchangés par ce sprint**.

---

## 10. Chemins interdits vérifiés

✅ Aucun touché : `app/models/**`, `migrations/**`, `schema_snapshot.sql`, `routers/**`,
`templates/**`, `seed.py`, `muscle_mapping.py`, `machine_atlas.py`, `static/**`. Working
tree Sx_CAT_01 + Sx_FB_01 **préservé** (non reset/stash/restauré). `substitution.py` et
`catalog_pattern_qa.py` **non touchés** (pas de STOP nécessaire — aucun code requis).

---

## 11. Tests locaux

- `pytest -k substitution/substitute` (tiered + base) : **41 passed**.
- `scripts/catalog_qa.py` : **PASS** · `scripts/machine_atlas_qa.py` : **PASS** ·
  `scripts/catalog_pattern_qa.py` : **OK** (53 validés, 3 soft warnings préexistants, exit 0).
- Broad sweep local : voir §résultats de session.

> Aucun commit, aucun push, aucune CI (LOCAL BATCH MODE).

---

## 12. Limites & recommandation

**Limites :**
- 3 soft warnings `catalog_pattern_qa` (pull-b Rowing) restent des **cleanup candidates
  futurs** (migrer les subs curées cross-pattern vers les bridges) — **non bloquants**,
  gérés gracieusement, hors périmètre verification-only.
- L'audit ne modifie rien : si un besoin réel de nouveau bridge émerge (dogfood), il
  faudra une spec dédiée.

**Recommandation finale : GO BATCH COMMIT + CI complète.** Le batch local
(Sx_CAT_01 code + Sx_FB_01 verify + Sx_SUB_01 verify) est **cohérent et vérifié** ; il
est temps de sécuriser le seul changement de code (Sx_CAT_01) via la CI réelle.

---

## Verdict

**Verdict :** 🟢 **Sx_SUB_01 Substitution Graph Verification — VERIFIED / ALREADY CONFORMANT.**

Le moteur N1/N2/N3 (`substitution.py`, Sb_22a v1.1) est **entièrement conforme** :
N1 strict (match 4-dim), N2 même `pattern_motor` + proximité ≥ 50, N3 zone-only ou
bridge cross-pattern ; **garde anti-cross-pattern hard-enforced** (filtre + invariant
+ démotion silencieuse) ; caps/dedup/tolérance/labels/rationales robustes ; 2 bridges
N3-only. **Sx_CAT_01 a un impact NUL** (substitution ne lit pas `machine_family`/
`machine_slug`). 41 tests substitution verts ; QA scripts PASS ; historique stable
(snapshots, aucun backfill). **Aucun code touché.** Recommandation : **GO BATCH COMMIT
+ CI complète**.
