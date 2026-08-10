# SPRINT Sb_MORPHO_POOL_COVERAGE_01 — exercise_properties Coverage for Morphotype Priorities (RAPPORT)

**Base canonique :** `6b03f29` · **Branche :** `sb/morpho-pool-coverage-01` · **Tier :** SHARED_CODE (traité comme tel par prudence §1 — `exercise_properties.json` est lu par substitution + générateur ; `check_scope` disait ISOLATED, **remonté d'un cran**)
**Origine :** finding de `Sb_MARTIN_PROGRAM_01` — les priorités morphotype de Martin (deltoïdes latéraux/postérieurs, mollets) n'étaient **pas couvertes** par le pool de scoring.
**Livré sous le protocole agentique** (`CLAUDE.md §4`) : `GO BUILD` → autonome jusqu'à `PR GREEN / MERGE PENDING`. **Pas de merge.**

## 1. Ce qui est livré

La **couverture `exercise_properties`** des exercices morphotype prioritaires, **débloquant les
slots-priorités du générateur** (les slots latéraux/postérieurs/mollets/hinge se **remplissent**
au lieu d'être signalés vides). Deux volets :

- **Données** : +16 entrées `data/exercise_properties.json` (les exercices E4–E8 du template
  « Full Body — Morphotype Priority » : RDL/hinge, élévations latérales, oiseau/rear-delt, mollets
  debout/assis — **prescrits + substituts**), sur des **noms EKB existants** (0 expansion EKB).
- **Générateur** : extension **additive** de la désambiguïsation par `muscle_group` — la zone macro
  `shoulders` (comme `lower` avant elle) fusionne plusieurs zones détaillées (delt_lat vs delt_post) ;
  le générateur les sépare par `muscle_group` (`delts_lateral`/`delts_rear`). Ajout d'une règle
  **« pas de doublon d'exercice entre slots »** (propriété de qualité de programme).

Cohérence référentielle maintenue : `data/exercise_knowledge_base.json` (16 records `gap → covered`,
`_counts` recalculés), compteurs de couverture (EKB QA), tests morpho re-basés.

## 2. Brainstorming / Options / Risques / Choix retenu (CLAUDE.md §3)

**Préflight** : cartographie du blast radius — le pool est lu par substitution (N2/N3 de **tous**
les exercices) et par le générateur ; couplage `exercise_properties ↔ exercise_knowledge_base`
(consistance pinnée) ↔ compteurs figés (`EXPECTED_GAPS`, covered/gap/props, blackholes) ↔ tests morpho.

| Décision (arbitrée avec l'opérateur) | Choix |
|---|---|
| **Scope** | ✅ **Ciblé** : E4–E8 + substituts (16 noms), **quad intact** (reste Leg extension, pas de bascule Hack Squat) |
| **Générateur** | ✅ **Code + données** : désambiguïsation `shoulders` par `muscle_group` (miroir exact de `lower`) — sinon les slots latéral/postérieur collideraient |

**Point dur 1 — `shoulders` surchargée** : sans désambiguïsation, une élévation latérale et un oiseau
(mêmes `shoulders/isolation_upper`) seraient indistinguables → même exercice pour les 2 slots. Résolu
par `muscle_group` (`delts_lateral`/`delts_rear`), généralisant `_REGION_ZONE_MUSCLE_GROUP`.

**Point dur 2 — collision mollets** : la taxonomie `muscle_group` ne sépare pas mécaniquement
gastrocnémien/soléaire (tous `calves`) → les 2 slots mollets piquaient le même exercice. Résolu par
la règle **no-duplicate** (déterministe, ordre de slot fixe) : slot4 → « Calf press leg press »,
slot5 → « Mollets assis machine » (mouvement assis, cohérent soléaire).

**Risques traités** :
1. **Régression substitution N1/N2/N3** (nouveau pool) → suite substitution **58 verte** + full sweep. *Testé.*
2. **Fabrication** → la règle no-fabrication tient (pool vide ⇒ coverage gap, jamais d'invention) ;
   test dédié robuste au pool réel (`pool={}`). *Testé.*
3. **Incohérence référentielle** `properties ↔ EKB` → 16 records EKB curés (`gap→covered`, zone fine +
   macro `FINE_TO_MACRO`, `confidence=measured`, `properties_source`), `_counts` + compteurs QA re-basés,
   diff EKB **minimal** (round-trip byte-exact vérifié). *Testé (32 EKB verts).*
4. **Vocabulaire muscle_group** → lower : `hamstrings`/`glutes`/`calves` déjà admis ; shoulders :
   `delts_lateral`/`delts_rear` (non contraints par le garde lower-only). *Testé.*
5. **quad sur-spécialisé** → **écarté par scope** (Hack Squat non couvert ; quad reste maintenance). *Vérifié.*

## 3. Fichiers touchés

| Fichier | Changement |
|---|---|
| `data/exercise_properties.json` | **+16 entrées** (posterior/lateral/rear/calves, noms EKB existants) |
| `app/services/morpho_program_generator.py` | `_REGION_ZONE_MUSCLE_GROUP` (ajout `shoulders`) + règle **no-duplicate** (`used`) — additif |
| `data/exercise_knowledge_base.json` | 16 records `gap→covered` (curation) + `_counts` (covered 51→67, gap 52→36, blackholes 19→12) |
| `tests/test_ekb_coverage.py` | `EXPECTED_GAPS` 52→36 + compteurs (gaps 36, covered 67, props 69) |
| `tests/test_exercise_knowledge_base.py` | covered 51→67, gaps 52→36, blackholes 19→12 |
| `tests/test_morpho_program_generator.py` | flips gap→rempli + test no-fabrication robuste (pool vide) + test muscle-group |
| `tests/test_martin_program.py` | flips gap→rempli (programme complet 8/8, 8 distincts) |
| docs | ce rapport + note de résolution dogfood + registry + roadmap |
| **substitution.py / slot_intent.py / morphology_profile.py / reference_split.json / migrations** | **aucun** |

## 4. Résultat — programme de Martin désormais complet

`generated_program_id = mpg1-b837ae570d6161b5` — **8/8 slots remplis, 8 exercices distincts, 0 warning** :

| Slot | Intent | Exercice | Score |
|---|---|---|---|
| 1 | lateral_delt | Élévations latérales câble | 80 |
| 2 | upper_chest | Chest Press machine | 80 |
| 3 | rear_delt | Face pull câble | 80 |
| 4 | calves gastroc | Calf press leg press | 80 |
| 5 | calves soléaire | Mollets assis machine | 80 |
| 6 | upper_back | Rowing chest-supported | 80 |
| 7 | quad (maintien) | Leg extension câble unilatéral | 60 |
| 8 | posterior hinge | Back extension 45° (bias ischios) | 90 |

## 5. Tests

Générateur + martin **31** (flips + no-fabrication robuste + muscle-group + distinctness) · EKB QA **32**
(EXPECTED_GAPS 36, compteurs, blackholes 12) · substitution **58** (N1/N2/N3 inchangé). **Full sweep
parallélisé (shared_code) : 2933 passés, 0 échec** — **3 régressions consommateurs captées puis
corrigées in-scope** : compteurs figés `ekb_classifiability_qa.py` (52→36 / 51→67 / 19→12) + son test ;
`test_program_quality_reviews::test_runtime_fields_are_populated` (le décalage alphabétique de
`_known_exercises(3)` rendait le programme all-lower → grade C sans cap ; ancré sur 3 exercices
zone-diversifiés → grade B, cap renseigné).

## 6. Interdits tenus

**0 modif `substitution.py`** (N1/N2/N3 & `compute_proximity` intacts) · **0 expansion EKB** (noms
existants) · **0 mutation `reference_split.json`** · **0 migration/DB/table** · **0 UI/publication/session** ·
**0 hardcoding Martin en logique globale** · **0 nouveau template**.

## 7. Validation

check_scope ISOLATED (**traité SHARED_CODE par prudence §1** — le pool est lu par substitution) ·
`check_spec_protocol` PASS · `check_ruff_budget` **543 ≤ 548** · `ruff` clean · **full sweep
parallélisé 2933 vert** (0 échec après correction des 3 régressions consommateurs).

## Verdict

**Verdict :** ✅ **Sb_MORPHO_POOL_COVERAGE_01 — PR GREEN / MERGE PENDING (à valider en CI).** Couverture
`exercise_properties` des priorités morphotype : générateur désambiguïse `shoulders`, règle no-duplicate,
programme de Martin **complet (8/8, distincts)**, référentiel EKB cohérent, **substitution N1/N2/N3
inchangée**. **Le merge reste un GO humain.**
