# SPRINT Sb_MARTIN_PROGRAM_01 — Martin's Derived Morphology-Aware Program (RAPPORT)

**Base canonique :** `a6d5d75` · **Branche :** `sb/martin-program-01` · **Tier :** ISOLATED (**fixture + tests + docs neufs · 0 code prod · 0 migration · 0 DB · 0 persistance**)
**Spec :** `Sx_MORPHO_PROGRAM_01_SPEC` (déc. 4/10/11/12 : Martin = fixture dogfood privée ; générateur compose ; agent propose / déterministe décide ; dogfood = version dérivée jamais mutée) — **4ᵉ build** de la file morpho.
**Livré sous le protocole agentique** (`CLAUDE.md §4`) : `GO BUILD` → autonome jusqu'à `PR GREEN / MERGE PENDING`. **Pas de merge.**

## 1. Ce qui est livré

La **dérivation** du programme de Martin : à partir de sa **fixture de morphologie privée**
(`Sb_MORPHO_PROFILE_01`) + ses **priorités d'entraînement déclarées** + l'**availability** de sa
salle, on compose — via le **générateur déterministe livré** (`Sb_MORPHO_PROGRAM_GENERATOR_01`) —
sa **proposition de programme** concrète et déterministe. Livraison **pure et privée** :
- **fixture privée** `tests/fixtures/dogfood/martin_program.py` (`martin_training_priorities`,
  `martin_availability`, `martin_program`) — **test-only**, jamais global/runtime/`/library` ;
- **doc dogfood privée** `docs/dogfood/DOGFOOD_Sb_MARTIN_PROGRAM_01_REPORT.md` (programme dérivé + finding) ;
- **tests** `tests/test_martin_program.py`.

**Rien n'est persisté** : aucun Custom Program, aucun template, aucune migration, aucune mutation de
`reference_split.json`/`exercise_properties.json`. Le passage par le **cycle Custom réel** est le
build **suivant** (`Sb_MORPHO_DOGFOOD_01`) — la roadmap versionnée distingue explicitement l'item 4
(dériver, privé) de l'item 5 (cycle réel).

## 2. Brainstorming / Options / Risques / Choix retenu (CLAUDE.md §3)

**Préflight** : le générateur (`generate_program`) est mergé sur la canonique (`7570817`) ; sa
sortie est une proposition **en mémoire** ; la fixture morphologie de Martin expose ses faits
privés. Dérivation exécutée en préflight pour ancrer les attendus.

| Option | Verdict |
|---|---|
| **A** — dériver le programme de Martin **en pur/privé** (fixture + tests + doc dogfood), 0 persistance | ✅ **RETENU** — c'est l'item 4 de la file ; 0 DB/publication/EKB ; testable |
| **B** — créer/persister le programme via le **cycle Custom réel** | ✗ c'est l'**item 5** (`Sb_MORPHO_DOGFOOD_01`), pas ce build |
| **C** — dériver + étendre le pool `exercise_properties` pour remplir les gaps | ✗ hors périmètre (shared_code) ; le gap est un **finding**, extension = sprint dédié sur GO |

**Décision de scope tranchée par la roadmap versionnée** : item 4 = **dériver** (pur/privé), item 5 =
**cycle réel**. Aucune ambiguïté résiduelle → pas de STOP.

**Risques traités** :
1. **Données Martin en logique globale** → **aucune** : priorités/availability vivent dans la
   **fixture privée** ; le générateur global reste sans hardcoding Martin. *Testé (source « private »,
   fichier sous `tests/fixtures/dogfood`).*
2. **Persistance/publication accidentelle** → dérivation pure ; **garde AST** : la fixture n'importe
   ni DB, ni publication, ni session_builder, ni routes/models. *Testé.*
3. **Fabrication d'exercices sur slots non couverts** → le générateur omet + warn ; on **assert 0
   fabrication** sur les 5 slots-priorités non couverts. *Testé.*
4. **Mutation de données** → sha `reference_split.json`/`exercise_properties.json` inchangés. *Testé.*
5. **Expansion EKB implicite** → tous les exercices choisis sont des noms **du pool existant**
   (`picked ⊆ pool`). *Testé.*

## 3. Fichiers touchés (3 neufs + 2 docs)

| Fichier | Changement |
|---|---|
| `tests/fixtures/dogfood/martin_program.py` (**neuf, privé**) | `martin_training_priorities` (4 morphotype + 3 maintien) · `martin_availability` (Fitness Park) · `martin_program()` → `generate_program(...)` |
| `tests/test_martin_program.py` (**neuf**) | 11 tests |
| `docs/dogfood/DOGFOOD_Sb_MARTIN_PROGRAM_01_REPORT.md` (**neuf, privé**) | programme dérivé + finding de couverture |
| docs | ce rapport + registry + roadmap |
| **générateur / substitution / morphology_profile / slot_intent / modèles / migrations / templates / publication** | **aucun** |

## 4. Programme dérivé + finding

`generated_program_id = mpg1-391c65154b3ed546` — 8 intentions (forme « Full Body — Morphotype
Priority »). **3 slots remplis** (upper_chest→Chest Press machine 80 · upper_back→Rowing chest-supported
80 · quad→Leg extension câble unilatéral 60, **maintien**) ; **5 warnings de couverture**
(deltoïdes latéraux, deltoïdes postérieurs, mollets ×2, chaîne postérieure), **0 fabrication**.

**Finding dogfood MAJEUR** : les **muscles-priorités morphotype** de Martin (latéraux, postérieurs,
mollets) sont **précisément ceux que le pool `exercise_properties` ne couvre pas**. La dérivation
réussit et **expose le blocage concret** : avant `Sb_MORPHO_DOGFOOD_01` (cycle réel), un build de
**couverture `exercise_properties`** (props sur noms EKB existants : latérales, oiseau, mollets,
hinge) est nécessaire pour remplir ses slots-priorités. Détail : voir la doc dogfood.

## 5. Tests

`tests/test_martin_program.py` — **11 passés** : dérivation déterministe (id + `to_dict` égaux) ·
**forme 8 intentions Full Body Morphotype** · **3 slots couverts remplis d'exos EKB réels** (pecs/back/quad)
· **availability respectée** (equipment_family ∈ Fitness Park) · **priorités morphotype non couvertes →
warnings honnêtes, 0 fabrication** · **gaps exactement attendus** (5 warns / 3 remplis) · **0 mutation**
data files · **garde AST** anti-persistance/publication · **données Martin privées/test-only** ·
**aucun nouveau nom d'exercice** (`picked ⊆ pool`) · priorités = vocabulaire fermé ranké.

**Broad sweep ciblé** (generator + slot_intent + morphology + substitution + tiered + full_body +
catalog + martin_program) : **122 passés** — **substitution N1/N2/N3 vert, inchangé**.

## 6. Interdits tenus

**0 code prod** (fixture/tests/docs uniquement) · **0 DB/migration/persistance** · **0 Custom Program /
publication / template** · **0 mutation** `reference_split.json`/`exercise_properties.json` · **0
expansion EKB** · **0 modif** générateur/substitution/morphology_profile/slot_intent · **0 UI/`/library`** ·
**0 donnée Martin en logique globale** (fixture test privée uniquement) · **cycle Custom réel = build
suivant** (`Sb_MORPHO_DOGFOOD_01`).

## 7. Validation

check_scope **ISOLATED** · `check_spec_protocol` PASS · `check_ruff_budget` **≤ 548** · `ruff check`
fichiers neufs **clean**.

## Verdict

**Verdict :** ✅ **Sb_MARTIN_PROGRAM_01 — MERGED + CANONICAL CI GREEN.** Programme de
Martin **dérivé** en pur/privé via le générateur livré, déterministe, honnête sur ses manques de
couverture (0 fabrication), **0 persistance / DB / publication / EKB / donnée globale**. Finding :
les priorités morphotype de Martin exigent une **couverture `exercise_properties`** avant le cycle réel.

---

## Appendice post-merge (closeout)

- **Merge** : PR **#65 MERGED** 2026-08-10, build `d00cb33`, merge commit **`364ea6a`** via `--merge --match-head-commit d00cb33` — **sans squash, sans `--admin`** (gate `CLEAN`, `MERGEABLE`, 0 thread non résolu, head épinglé). **Sous protocole agentique** `CLAUDE.md §4` : `GO BUILD` → `GO MERGE`.
- **CI canonique** : run **`31359840845`** (`push`) **3/3 GREEN** sur `364ea6a` (lint · pytest + QA · SonarCloud). Le merge contient des **tests/fixtures** → CI push canonique jouée (pas de skip `paths-ignore`).
- **Sonar sur main** : coverage main **91.4 %** ; gate PR **OK** (0 new smell/bug/vuln/dup). Livraison = **tests + fixture + docs** (0 code prod), rien de nouveau à mesurer côté couverture prod.
- **1 thread Gitar (qualité, non bloquant) résolu avec justification** : mutation `sys.path` / shadowing — le test suit la **convention repo déjà mergée** (`test_slot_intent`, `test_morphology_profile`), aucune collision réelle (noms uniques, dossier unique) ; migration package-qualifiée = **refactor repo-wide hors périmètre** (candidat OPS futur). Aucun changement de code.
- **Cleanup** : branche `sb/martin-program-01` + worktree `workout-session-tracking-martin-program` **conservés** — suppression = **GO humain séparé** (`CLAUDE.md §2`).
- **File restante** (sur GO) : *(recommandé)* build de **couverture `exercise_properties`** → puis `Sb_MORPHO_DOGFOOD_01` (cycle Custom réel).
