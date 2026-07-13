# Sprint Sx_CAT_01 — Catalog Integrity Cleanup

**Statut** : 🟢 DELIVERED LOCALEMENT — **NON commité, NON poussé, CI non lancée** (LOCAL BATCH MODE)
**Type** : CODE BUILD — catalog data integrity cleanup, no schema change, no session migration
**Date** : 2026-07-13
**Cycle** : batch local (avancer sans CI complète à chaque micro-sprint)
**Préconditions** : `Sx_UI_07.2` HUMAN REVIEW ACCEPTED ✅ ; CI timeout 45 baseline ✅ ; BI activation deferred ✅ ; dogfooding peut être différé ✅.

---

## 0. But produit

Nettoyer les **incohérences sémantiques** du catalogue (`machine_slug`/`machine_family`
contredisant le nom/notes d'un exercice) **sans changer l'architecture, sans migrer
l'historique, sans toucher aux services**. Améliore la fiabilité des **futures**
séances (body mapping, substitutions, lecture par zones) — les snapshots historiques
ne bougent pas.

---

## 1. Étape 0 — Brainstorming / Options / Choix retenu

### Options

| Option | Description | Verdict |
|---|---|---|
| **A** | Data-only semantic cleanup (`reference_split.json`) | ✅ **RETENU** |
| B | Data + règle QA sentinelle | ❌ non nécessaire (règle non triviale/fragile → différée) |
| C | Service/mapping refactor | ❌ trop large |
| D | Programme redesign complet | ❌ trop risqué avant dogfooding |

### 15 sujets clivants tranchés

1. **`data/reference_split.json` uniquement** (pas de seed.py).
2. **Corriger maintenant** (3 anomalies prouvées CLEAR).
3. **Slugs de templates conservés.**
4. **Codes E1/E2/… conservés.**
5. **Positions conservées.**
6. **Corriger `machine_slug`/`machine_family` uniquement** (pas les noms).
7. **set_scheme / rep_targets conservés.**
8. **Pas d'ajout d'exercice** (aucune anomalie critique le justifiant).
9. **machine_family incohérente corrigée** ; en cas de doute → null.
10. **muscle_mapping non touché.**
11. **machine_atlas non touché.**
12. **Tests sentinelles ajoutés** (nouveau fichier), tests existants non modifiés.
13. **Impact futures séances uniquement** (les champs machine sont snapshotés à la création).
14. **Snapshots historiques inchangés** (preuve : `seed.py:81-82` copie les champs à la création de la SessionExercise).
15. **Suite du batch** : feedback rationalization ou substitution graph (proposition en fin).

**Choix : Option A** — data-only, corrections `machine_slug`/`machine_family` sur 3
exercices prouvés, aucun autre champ touché, `catalog_qa.py` **non modifié** (règle B
non nécessaire → tier ISOLATED).

### Risques / parades

| Risque | Parade |
|---|---|
| Casser `check_machine_links` (slug↔famille atlas) | `machine_slug=null` sur les 3 → lève la contrainte de cohérence ; familles corrigées résolvent dans l'atlas. catalog_qa **PASS** après fix. |
| Toucher un champ immuable | diff strict prouve : **seuls `machine_slug`/`machine_family`** changent |
| Migrer l'historique | les champs sont **snapshotés à la création** → aucune session existante affectée |
| Corriger un cas ambigu | 3 cas **CLEAR** seulement ; 0 DOUBTFUL fixé |

---

## 2. Audit complet du catalogue

**Périmètre** : 16 templates, **98 exercices**. Audit read-only de la cohérence
`name` + `notes` ↔ `machine_slug` + `machine_family` (familles valides :
pecs-press, pecs-fly, shoulders-press, shoulders-lateral-posterior, back-vertical,
back-horizontal, legs-quad-dominant, legs-posterior-calves, null).

**Baseline avant fix** : `catalog_qa.py` **PASS** (0 error), `machine_atlas_qa.py`
**PASS**. Les anomalies sont **sémantiques**, pas structurelles — c'est pourquoi
`check_machine_links` (qui vérifie la cohérence slug↔atlas, pas la cohérence
mouvement↔famille) ne les détectait pas.

### 2.1 Anomalies — classement

| # | Exercice | Anomalie | Classe |
|---|---|---|---|
| 1 | **push-b / E5** « Tirage front câble (prise large) » | notes « cibler les deltoïdes latéraux » (upright row épaules) mais `back-vertical` + `lat-pulldown` (mouvement dos) | **FIX NOW (CLEAR)** |
| 2 | **catch-up-shoulders / E4** « Tirage front câble (prise large) » | idem (même exercice, autre template) | **FIX NOW (CLEAR)** |
| 3 | **legs-b / E3** « Leg Press (pieds hauts, écartés) » | notes « cibler les fessiers et ischios » (postérieur) mais `legs-quad-dominant` | **FIX NOW (CLEAR)** |
| — | ~95 autres exercices | cohérents | **OK — no change** |
| — | (aucun) | — | **DOCUMENT ONLY : 0** · **DEFERRED : 0** |

---

## 3. Diff des corrections

**3 exercices, 6 lignes — SEULS `machine_slug`/`machine_family` changent :**

| Exercice | Avant | Après |
|---|---|---|
| push-b / E5 | `slug=lat-pulldown`, `family=back-vertical` | `slug=null`, `family=shoulders-lateral-posterior` |
| catch-up-shoulders / E4 | `slug=lat-pulldown`, `family=back-vertical` | `slug=null`, `family=shoulders-lateral-posterior` |
| legs-b / E3 | `slug=leg-press`, `family=legs-quad-dominant` | `slug=null`, `family=legs-posterior-calves` |

**Choix `slug=null`** : les mouvements upright-row (E5/E4) n'ont **pas de machine
exacte** dans l'atlas (que lateral-raise/face-pull/rear-delt) ; pour E3, `leg-press`
résout vers `legs-quad-dominant` dans l'atlas → garder le slug casserait
`check_machine_links` avec la nouvelle famille postérieure. Règle brief appliquée :
**doute → null plutôt qu'une mauvaise machine**. La famille corrigée reste
sémantiquement juste et résout dans l'atlas.

---

## 4. Preuve : champs immuables inchangés

Diff limité aux 6 lignes machine (grep sur le diff) → **aucun** :
- `slug` de template · `code` (E1-E7) · `position` · `set_scheme` · `rep_targets` ·
  `name` · `notes` · `substitutes` — **tous inchangés**.
- Test sentinelle `test_fixed_exercises_keep_code_position_scheme_reps_name` verrouille
  code/position/set_scheme/name/rep_targets des 3 exercices.
- Test `test_template_slugs_unchanged` verrouille les 16 slugs de templates.

---

## 5. Preuve : snapshots historiques non migrés

`app/services/seed.py:81-82` copie `machine_slug`/`machine_family` **depuis le
catalogue au moment de la création** de la `SessionExercise` (snapshot). Les sessions
déjà en base gardent donc leurs anciennes valeurs — **aucune migration, aucun UPDATE
historique**. Le cleanup n'affecte que les **futures** séances créées après
re-seed. Aucun modèle, aucune migration, `data/schema_snapshot.sql` intact.

---

## 6. Tests locaux

### `tests/test_catalog_integrity_cleanup.py` (NOUVEAU, 9 tests)
- **Corrections** : E5/E4/E3 → famille corrigée + slug null (3 tests) ;
- **Champs immuables** : code/position/set_scheme/name/rep_targets des 3 exercices conservés ;
- **Garde** : aucun upright-row (notes deltoïdes latéraux) ne reste `lat-pulldown`/`back-vertical` ;
- **Atlas** : les familles corrigées résolvent dans `machine_atlas.json` ;
- **Invariants** : codes uniques / positions séquentielles / 16 slugs de templates intacts.

### Résultats locaux
- Dédiés : **9/9 verts**.
- `python scripts/catalog_qa.py` : **PASS** (0 error) — inchangé avant/après fix.
- `python scripts/machine_atlas_qa.py` : **PASS**.
- **Broad sweep local** (catalog/seed/launcher/library/session/body_intelligence/physique/progress/history) : **785 passed, 0 failed** — aucune régression.
- `check_scope` = **ISOLATED** (data + test isolés ; `catalog_qa.py` non modifié → pas de QA_TOOL/SHARED_CODE).
- ruff clean sur fichiers touchés, budget **543 ≤ 548** ; spec protocol vert.

> **Note LOCAL BATCH MODE** : ces tests ont tourné **en local uniquement**. Aucun
> commit, aucun push, aucune CI GitHub déclenchée. La CI complète sera lancée plus
> tard sur un batch cohérent.

---

## 7. Limites

- **3 corrections seulement** (cas CLEAR prouvés) ; le reste du catalogue est cohérent.
- **`slug=null` perd un slug qui était correct** pour E3 (`leg-press`) — compromis
  assumé pour aligner la famille sur les notes sans casser `check_machine_links` et
  sans toucher l'atlas (hors périmètre).
- **Pas de règle QA sémantique ajoutée** (Option B) : détecter « famille contredit
  les notes » automatiquement serait fragile (parsing de langage libre) → différé.
- **Pas d'ajout d'exercice**, pas de redesign de programme.

---

## 8. Next (dans le batch)

- **Feedback rationalization** (spec/build) — réorganiser la sémantique de feedback
  de séance, ou
- **Substitution graph** (spec) — formaliser le graphe de substitutions
  (`cross_pattern_substitutions.json` existe).

Proposition en fin de sprint : GO CONTINUE BATCH (Feedback / Substitution) ou GO
BATCH COMMIT + CI complète.

---

## Verdict

**Verdict :** 🟢 **Sx_CAT_01 Catalog Integrity Cleanup — DELIVERED LOCALEMENT (batch mode, non commité).**

3 incohérences sémantiques **CLEAR** corrigées dans `data/reference_split.json`
(push-b/E5, catch-up-shoulders/E4 : upright row mal classé en dos → épaules ;
legs-b/E3 : leg press postérieur mal classé en quad). **Seuls `machine_slug`
(→ null) et `machine_family` changent** — aucun slug/code/position/set_scheme/
rep_target/nom touché ; aucun service/modèle/migration ; snapshots historiques
inchangés (champs snapshotés à la création). catalog_qa + atlas_qa **PASS** ; 9 tests
dédiés verts. **Non commité, non poussé, CI non lancée** — WAIT GO batch.
