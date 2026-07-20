# Sprint Sb_CUSTOM_PROGRAM_EKB_02 — Canonical Exercise Knowledge Base JSON — BUILD

**Statut** : 🟢 **PATCH COMPLETE / REVIEW PENDING** (non commité, non poussé, CI non lancée)
**Type** : CODE BUILD — **data-only** (JSON canonique + tests), zéro migration, zéro `app/`, zéro seed
**Date** : 2026-07-20
**Specs** : `Sx_CUSTOM_PROGRAM_02` §4/§5/§6/§7 (identité, taxonomie, variantes, Option A JSON)
**Branche** : `sb/custom-program-ekb-02-canonical-json` (worktree dédié, base `8ef3240` — origin canonique post-closeout EKB_01, head Alembic `n5o0i6j7l98` inchangé)
**Préflight** : ✅ GO PATCH validé (arbitrages : 11 zones fines + zone_macro dérivé ; `variant_group` null V1)

---

## 0. Étape 0 — Brainstorming / Options / Risques / Choix retenu

| Décision | Options | Choix retenu |
|---|---|---|
| Génération du JSON | saisie manuelle · script depuis le snapshot | **script jetable (scratchpad)** lisant le snapshot + les 4 sources → noms **byte-à-byte**, aucune saisie ; script supprimé après génération (seul le JSON reste) |
| `zone_primary` | 6 macro (properties, 51) · 11 fines (baseline, 65) | **11 fines** (arbitrage opérateur) — meilleure couverture, réconciliation `RADAR_AXES` prouvée |
| `zone_macro` | absent · dérivé | **dérivé** des 11 fines via `RADAR_AXES` (mapping déterministe, copié de `muscle_mapping.py`) |
| `variant_group` | dérivé grossier `(pattern, zone)` · null V1 | **null V1** (arbitrage opérateur) — pas de groupe grossier ; curation fine = build ultérieur |
| `variant_key` | slug simple · slug avec marqueur parenthèses | **slug avec marqueur `paren`** — une collision détectée (`Curl marteau câble (corde)` vs `… corde`) résolue déterministiquement, 103 clés uniques |
| 2 orphelines | supprimer · entrée EKB · alias | **`_aliases`** vers un nom canonique existant (`Développé incliné haltères 30°`) — lien **sourcé** par `machine_atlas.json` (alias `Incline DB press`), jamais supprimées, jamais entrées EKB |
| Champs de curation (fatigue/stabilité/durée/overload…) | inventer prudemment · différer | **différés** — non dérivables, ne servent qu'au scoring (`SCORING_01` fermé) |

Risque principal : sur-normalisation des noms → mitigé par génération scriptée depuis le snapshot (jamais de saisie manuelle) et gardé par le drift-check EKB_01 + les tests byte-à-byte.

## 1. Patch appliqué

| Fichier | Nature |
|---|---|
| `data/exercise_knowledge_base.json` | **nouveau** — `_version` `Sb_CUSTOM_PROGRAM_EKB_02.v1`, `_source_snapshot`, `_aliases` (2), `_zone_primary_vocab`/`_zone_macro_vocab`, `_counts`, **103 entrées** (13 champs chacune) |
| `tests/test_exercise_knowledge_base.py` | **nouveau** — **19 tests** |

**Aucune autre modification `data/` · aucun `app/` · aucune migration (head `n5o0i6j7l98`) · aucun seed · `scripts/ekb_coverage_qa.py` intouché.**

## 2. Structure JSON finale (par entrée)

`canonical_name` (byte-à-byte = clé) · `variant_key` (slug déterministe unique) ·
`variant_group` (**null V1**) · `movement_pattern` · `equipment_family` · `zone_primary`
(11 fines) · `zone_macro` (dérivé) · `chain` · `machine_slug` · `machine_family` ·
`coverage_status` (`covered`/`gap`) · `properties_source` · `confidence`
(`measured`/`derived`/`todo`) · `curation_note`.

## 3. Chiffres finaux

| Mesure | Valeur |
|---|---|
| Entrées EKB | **103** (= snapshot EKB_01, byte-à-byte) |
| `variant_key` uniques | **103/103** |
| **Covered** (properties) | **51** — `movement_pattern`/`chain`/`equipment_family` recopiés **verbatim** |
| **Gaps** | **52** — `coverage_status: "gap"`, pattern/chain jamais inventés (`null`) |
| **Trous noirs** (gap sans zone/machine/equipment) | **19** — `confidence: "todo"`, visibles et nommés |
| Zones fines remplies | 65/103 (baseline `classify_exercise`) |
| Equipment rempli (properties + atlas fallback) | 73/103 |
| Aliases orphelins | **2** → `Développé incliné haltères 30°` |

## 4. Mesuré / dérivé / inféré / non déductible

- **Mesuré** : les 51 properties (pattern/zone macro/equipment/chain), machine_slug/family de `reference_split`.
- **Dérivé déterministe** : `variant_key` (slug du nom), `zone_primary` fine (baseline), `zone_macro` (RADAR_AXES), equipment fallback (atlas via slug), `coverage_status`, `_aliases` (sourcé atlas).
- **Inféré (curation, DIFFÉRÉ — rien ici)** : `variant_group` fin, fatigue/stabilité/difficulté/latéralité/setup/durée slot/overload_compatibility, muscles fins.
- **Non déductible** : muscles fins (table `Muscle` vide), tout claim médical (interdit spec §2/§9).

## 5. Les 52 gaps et 19 trous noirs

Les 52 gaps sont **visibles, jamais masqués** (`coverage_status: "gap"`) ; leurs champs dérivables
(zone via baseline pour 33, equipment via atlas pour une partie) sont remplis sans invention, le
reste `null`. Les **19 trous noirs** (ni zone, ni machine, ni equipment dérivable) restent `null`
partout sauf le nom, `confidence: "todo"` : `Back extension 45° (bias ischios)`, `Calf press leg
press`, `Decline crunch`, `Good morning haltères`, `Hanging knee raise`, `Hip thrust haltères`,
`Machine crunch`, `Mollets debout machine`, `Pushdown corde`, `Reverse fly machine`, `Romanian
Deadlift barre`, `Shrugs barre`, `Shrugs câble`, `Sissy squat machine`, `Upright row câble`,
`Upright row haltères`, `Y-raise haltère`, `Élévations latérales haltères`, `Élévations latérales
machine`. Ces gaps sont la précondition mesurée qu'un build de curation ultérieur devra fermer.

## 6. Tests et checks exécutés

| Suite / check | Résultat |
|---|---|
| Dédiés (`test_exercise_knowledge_base.py`) | **19/19 premier coup** |
| Non-régression EKB_01 (`test_ekb_coverage.py`) | **13/13** → total **32/32** |
| `ekb_coverage_qa` (inchangé) | invariances OK, snapshot vert |
| ruff (fichier test neuf) | clean |
| `check_ruff_budget` | **543 ≤ 548** |
| `check_spec_protocol` | PASS |
| **`check_scope`** | **ISOLATED** (JSON `data/` neuf + tests neufs, non importés par l'app) — **full sweep local explicitement skippé** (contrat anti-overcheck), CI complète via PR = source de vérité |

Couverture des 19 tests : 103 clés · clés == snapshot byte-à-byte · `canonical_name == key` ·
`variant_key` présent et unique · `variant_group` null · 51 covered / 52 gap · cohérence
properties (verbatim) · gaps marqués sans invention · 19 trous noirs visibles/todo · 2 alias
présents · chaque alias → nom canonique existant · aucun alias en entrée EKB · zones fines ∈ 11 ·
zone_macro dérivée · enums fermés · non-médical (lexique interdit absent) · `ekb_coverage_qa`
vert · head Alembic inchangé.

## 7. Risques résiduels

Gaps volontairement non comblés (curation = build ultérieur, jamais silencieuse) · `variant_group`
null V1 prive le futur scoring de la redondance jusqu'à un build de curation dédié · le JSON n'est
pas encore consommé (pattern fondation, comme EKB_01) · un check dédié couverture EKB↔snapshot
serait à ajouter en **EKB_03** (spec 02 §14), délibérément hors périmètre ici (`scripts/` intouché
pour rester tier ISOLATED).

## 8. Confirmations de périmètre

✅ **Zéro migration** (head `n5o0i6j7l98`) · ✅ un seul nouveau fichier `data/`
(`exercise_knowledge_base.json`), les 4 sources existantes **intouchées** · ✅ aucun `app/`,
seed, UI, API, scoring, wizard, publication · ✅ `session_builder`/catalogue/tables UserProgram*
intacts · ✅ aucun renommage, aucune orpheline supprimée, aucun muscle fin inventé, aucun claim
médical.

---

## Verdict

**Verdict :** 🟢 **Sb_CUSTOM_PROGRAM_EKB_02 — PATCH COMPLETE / REVIEW PENDING.**

Le JSON canonique EKB existe : 103 entrées byte-à-byte issues du snapshot EKB_01, enrichissement
strictement dérivable (51 covered verbatim, zones fines + macro réconciliées, equipment
multi-source), 52 gaps et 19 trous noirs visibles, 2 orphelines consignées en alias sourcés,
`variant_group` null V1 et champs de curation différés — zéro invention, zéro schéma. 19 dédiés +
13 non-régression verts, check_scope ISOLATED. `EKB_03` (checks complets, spec 02 §14) = **FIRST
NEXT EKB BUILD CANDIDATE / NOT OPENED** · `EKB_04` (seed DB) = **NOT OPENED** · `SCORING_01`,
`WIZARD_*` = **NOT OPENED**.

---

## Appendice post-merge (closeout 2026-07-20)

- **Commit build** : `eeab131` (5 fichiers, +2035) sur `sb/custom-program-ekb-02-canonical-json`,
  base `8ef3240`.
- **PR #29 MERGED** — merge **`eafede6`** sur le canonique (parent immédiat `804b08c`, session
  ASSET, surfaces disjointes — aucun conflit).
- **CI PR `29746901012` : 4/4 GREEN** — les 3 jobs **+ le quality gate externe SonarCloud**, sans
  incident (2ᵉ build de code du track à passer le gate externe).
- **CI canonique `29749856878` sur `eafede6` : 3/3 GREEN** (lint · pytest+QA · SonarCloud).
- **Run ASSET `804b08c` annulé par concurrency** (`cancel-in-progress` sur le même ref) —
  comportement normal, remplacé sans impact par le run descendant `eafede6` qui inclut son contenu.
- **Head Alembic canonique inchangé : `n5o0i6j7l98`** — EKB_02 est bien data-only, zéro schéma.
