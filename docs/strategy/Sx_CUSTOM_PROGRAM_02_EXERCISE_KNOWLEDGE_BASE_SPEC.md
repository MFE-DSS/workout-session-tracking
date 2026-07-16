# Sx_CUSTOM_PROGRAM_02 — Exercise Knowledge Base Spec

**Type :** SPEC ONLY / DOMAIN DESIGN / DATA MODEL
**Date :** 2026-07-15
**Statut :** ⚪ SPEC DRAFT OPENED — pending human review · **BUILD NOT AUTHORIZED**
**Track :** `Sx_CUSTOM_PROGRAM` (parent : [`Sx_CUSTOM_PROGRAM_01`](Sx_CUSTOM_PROGRAM_01_INTELLIGENT_PROGRAM_BUILDER_SPEC.md), ✅ HUMAN REVIEW ACCEPTED)
**Branche :** `spec/sx-custom-program-01-intelligent-builder` (worktree isolé, rebasée sur la canonique)
**Autorisations :** aucune migration · aucun seed · aucun code `app/` · aucun `data/` modifié · aucun template/CSS/JS
**Audit source :** audit read-only du 2026-07-15 (chiffres §3, vérifiés par script sur le worktree)

---

## 1. Verdict / statut

**SPEC ONLY.** Ce document définit l'Exercise Knowledge Base (EKB) V1 : rôle, inventaire de
l'existant, identité des exercices, taxonomie, stockage cible, contraintes seed, QA future,
consommateurs. **Rien n'est buildé** : `Sb_CUSTOM_PROGRAM_*` reste NOT AUTHORIZED, aucune
migration, aucun seed, aucun fichier `data/` ni code applicatif n'est modifié par cette spec.

## 2. Rôle de l'EKB

L'EKB est la **source structurée unique** consommée par les trois couches du Custom Program
Builder (Sx_CUSTOM_PROGRAM_01 §3) :

1. **Génération** — le moteur déterministe sélectionne les exercices par contraintes
   (pattern requis par le split, zone de focus, matériel disponible, plafonds de fatigue).
2. **Remplacement d'exercices** (édition par cartes) — listes de remplacement filtrées
   (même `variant_group` / même pattern / même zone / matériel compatible).
3. **Scoring A/B/C** — volume par zone, équilibre push/pull/legs, redondance
   (`variant_group`), fatigue systémique, faisabilité matériel, réalisme durée.

Ce que l'EKB **n'est pas** :
- **pas une vérité médicale** — métadonnées opératoires d'entraînement, aucune allégation
  clinique, aucune donnée de blessure/pathologie ;
- **pas une couche LLM** — contenu versionné, relu par l'opérateur, déterministe ; aucun
  champ généré par LLM comme source de vérité (OQ-CP-H du parent reste hors track).

## 3. Inventaire existant (audit read-only 2026-07-15)

### Ce qui existe déjà

| Source | Contenu | État |
|---|---|---|
| `data/exercise_properties.json` (Sb_22a.v1.1) | **53 entrées** keyées par nom : `pattern_motor`, `zone_primary`, `equipment_family`, `chain` (53/53) ; `muscle_group` (9/53 seulement) | exploitable, **incomplet** |
| `data/reference_split.json` (2026-04-21.v13) | catalogue système : **65 noms prescrits** + **59 substituts distincts** = **103 noms uniques** ; par slot : `machine_slug` (60 slots, **25 slugs distincts**), `machine_family` (**8 familles**), `set_scheme`, `rep_targets`, `substitutes` | source des noms canoniques |
| `data/cross_pattern_substitutions.json` (Sb_22a.v1) | ponts inter-patterns N3 (12 noms cités, tous couverts par les properties) | exploitable tel quel |
| `BodyZone` (Sx_32, `app/models/body_zone.py`) | 11 zones seedées : `code`, `label`, `measurement_field`, `radar_axis`, `volume_target`, `is_active` | **fondation prête** |
| `Muscle` (Sx_32) | table **vide V1** (aucune anatomie inventée — décision Sb_32.1) | réservé |
| `ExerciseMuscleMapping` (Sx_32) | **91 exercices** mappés par **nom** (`exercise_code = name`, découverte Sb_32.2) : `body_zone_code`, `muscle_code` nullable, `role` primary/secondary, `source`, `position` | **fondation prête** |
| QA scripts | `catalog_qa.py` (7 checks structurels reference_split), `catalog_pattern_qa.py`, `machine_atlas_qa.py`, `apply_machine_atlas_links.py` | patterns QA réutilisables |

### Ce qui est incomplet (gaps quantifiés)

- **Couverture** : 52 des 103 noms du catalogue (prescrits + substituts) **absents** de
  `exercise_properties.json` (~50 %). Exemples : Butterfly pec machine, Face pull câble,
  Calf press leg press, Decline crunch…
- **Champs absents partout** : stabilité, classe de fatigue, difficulté technique,
  unilatéral/bilatéral, complexité de setup, durée estimée de slot, compatibilité overload,
  `variant_group`/`variant_key`.
- `muscle_group` rempli sur 9/53 entrées seulement ; table `Muscle` vide.

### Ce qui ne doit pas être renommé

- Les **103 noms historiques** (prescrits + substituts) : l'identité analytique
  (`exercise_name_snapshot`, `ExerciseMuscleMapping.exercise_code = name`, substitution,
  last_time) repose sur eux. **Invariance des noms = contrainte #1** (héritée Sx_32).
- Les 25 `machine_slug` / 8 `machine_family` existants ; les 11 codes `BodyZone`.

## 4. Identité des exercices

- **Clé stable V1 = nom canonique existant** (`canonical_name`), aligné byte-à-byte sur les
  noms du catalogue et du mapping Sx_32. Pas d'UUID, pas de slug nouveau, **aucun renommage
  des noms historiques**.
- Ajouts **additifs** (nouveaux champs, jamais de mutation de la clé) :
  - `variant_key` — identifiant technique dérivé, stable, lisible (ex.
    `elevation-laterale--halteres-debout`), utile aux futurs formulaires/URLs ; jamais
    substitué au nom dans l'analytique.
  - `variant_group` — famille fonctionnelle partagée (ex. `elevation-laterale`), support de
    la redondance (scoring) et du remplacement (édition).
- **Distinctions de niveau** :
  - *exercice canonique* : une entrée EKB (= un nom) ;
  - *variante* : entrée distincte reliée par `variant_group` ;
  - *machine* : attribut (`machine_slug`/`equipment_family`), pas une entrée ;
  - *pattern* : attribut de classification (`movement_pattern`), pas une entrée.

## 5. Taxonomie minimale V1 (champs par entrée EKB)

| Champ | Type / valeurs | Oblig. V1 | Source |
|---|---|---|---|
| `canonical_name` | string, clé unique | ✅ | catalogue existant |
| `variant_key` | slug technique dérivé | ✅ | dérivé du nom |
| `variant_group` | slug de famille | ✅ (groupe singleton admis) | curation |
| `primary_body_zone` | code `BodyZone` (11) | ✅ | mapping Sx_32 / properties |
| `secondary_body_zones` | liste de codes | optionnel | mapping Sx_32 (role=secondary) |
| `primary_muscles` | liste codes `Muscle` | optionnel (table vide V1) | différé (OQ-EKB-C) |
| `equipment_family` | enum (barre/haltères/machine/câble/poids de corps/…) | ✅ | properties + curation |
| `machine_slug` | slug machine | optionnel | reference_split (25 existants) |
| `movement_pattern` | enum patterns moteurs (aligné `pattern_motor` Sb_22a) | ✅ | properties + curation |
| `chain` | `compound` / `isolation` | ✅ | properties (aligné overload §Sb_30) |
| `stability` | `free` / `guided` / `machine` / `bodyweight` | ✅ | curation |
| `fatigue_class` | `low` / `medium` / `high` | ✅ | curation prudente (OQ-EKB-G) |
| `technical_difficulty` | `beginner` / `intermediate` / `advanced` | ✅ | curation prudente |
| `laterality` | `unilateral` / `bilateral` | ✅ | curation |
| `setup_complexity` | `low` / `medium` / `high` | ✅ | curation |
| `estimated_slot_minutes` | int (série+repos+setup, indicatif) | ✅ | heuristique documentée |
| `overload_compatibility` | `standard` / `limited` / `none` (ranges exploitables par le moteur Sx_30) | ✅ | curation |
| `confidence` | `verified` / `inferred` (par entrée, V1 ; par champ = OQ-EKB-H) | ✅ | curation |

Toute valeur est **opératoire et indicative** — vocabulaire d'entraînement, pas de claim
biomécanique absolu ni médical.

## 6. Variantes fines (exemple canonique obligatoire)

Cinq entrées EKB **distinctes**, partageant `variant_group: elevation-laterale`,
`movement_pattern: shoulder_abduction`, `primary_body_zone: delt_lat`, `chain: isolation` :

| Entrée | equipment_family | stability | fatigue | setup | laterality |
|---|---|---|---|---|---|
| Élévation latérale haltères debout | haltères | free | medium | low | bilateral |
| Élévation latérale haltères assis | haltères | free | low | low | bilateral |
| Élévation latérale câble unilatéral | câble | guided | medium | medium | unilateral |
| Élévation latérale machine | machine | machine | low | low | bilateral |
| Élévation latérale machine guidée | machine | machine | low | low | bilateral |

Le partage de `variant_group` permet : détection de redondance (scoring), listes de
remplacement (édition), rotation de variantes (génération). Les champs distincts permettent :
filtre matériel, budget fatigue, budget temps, contrainte de stabilité par niveau.
*(Les libellés exacts seront alignés sur les noms historiques existants au moment du draft
JSON — aucun renommage ; si un libellé n'existe pas au catalogue, il entre comme nouvelle
entrée EKB sans toucher le catalogue système.)*

## 7. Stockage cible (comparaison)

| Option | Description | Pour | Contre |
|---|---|---|---|
| **A — JSON versionné source-of-truth** | `data/exercise_knowledge_base.json` (`_version`), lu à chaud | simple, diffable, review humaine ligne à ligne, zéro migration | pas de FK vers `BodyZone`, requêtes en mémoire |
| **B — Tables DB seedées depuis JSON** | tables `ekb_*` + seed versionné (pattern `reference_split`) | FK réelles (`BodyZone`, futur `Muscle`), requêtable, cohérent Sx_32 | migration + seed = surface sensible ; interdit tant que non gaté |
| **C — Hybride séquencé** | A d'abord (source canonique), B ensuite (seed DB contrôlé, additive-only) | valeur immédiate sans migration ; DB seulement quand prouvé nécessaire | deux étapes |

**Recommandation prudente : Option C séquencée** — le **JSON versionné est la source
canonique** (draft + QA + review humaine sans toucher ni DB ni seed) ; le **seed DB est un
build séparé ultérieur** (`Sb_CUSTOM_PROGRAM_EKB_04`), optionnel, additive-only, ouvert
seulement si les consommateurs le justifient et après acceptance dédiée. Cohérent avec la
position par défaut OQ-CP-D du parent.

## 8. Contraintes seed

- **Aucune modification de seed dans cette spec** (ni dans aucun sprint EKB avant
  `Sb_CUSTOM_PROGRAM_EKB_04` accepté).
- Le futur seed EKB devra être **versionné** (`_version` + table de tracking, pattern
  `ReferenceDoc`), **jamais destructif** (pas de DELETE de rows historiques ; désactivation
  par `is_active`, pattern Sx_32), **QA-gated** (le seed refuse un JSON qui échoue la QA §9),
  et **compatible avec le wipe-guard Custom Program** (contrat dur #1 du parent — les tables
  EKB sont distinctes des tables catalogue ; aucune interaction avec le DELETE de
  `seed_reference_split`).

## 9. QA attendue (future, scripts/tests à livrer avec le draft JSON)

Pattern : `catalog_qa.py` existant (checks structurels + rapport markdown + exit code).

1. **Couverture** : chaque nom du catalogue (prescrits + substituts de `reference_split.json`)
   a une entrée EKB — le gap actuel de 52 noms doit tomber à 0.
2. **Substitutions** : chaque nom cité par `substitutes` et
   `cross_pattern_substitutions.json` pointe vers une entrée EKB connue.
3. **Complétude** : chaque entrée a `primary_body_zone` (code BodyZone valide),
   `movement_pattern`, `equipment_family` non vides.
4. **Invariance** : aucun nom historique supprimé ni renommé (diff vs snapshot des 103 noms).
5. **Unicité** : aucun doublon ambigu (`canonical_name` unique, `variant_key` unique).
6. **Cohérence de groupe** : toutes les entrées d'un `variant_group` partagent pattern et
   zone primaire.
7. **Non-médical** : lexique interdit (grep : claims médicaux/hormonaux) absent des
   métadonnées et descriptions.
8. **Traçabilité** : aucun champ dont la seule source serait un LLM (`confidence` renseigné,
   `inferred` explicite).

## 10. Consommateurs futurs

| Consommateur | Usage EKB |
|---|---|
| Wizard / génération (Sb_CUSTOM_PROGRAM_04 parent) | sélection par contraintes : pattern, zone, matériel, fatigue, temps, difficulté vs niveau |
| Édition / remplacement par cartes | listes filtrées par `variant_group` → pattern → zone ; matériel compatible |
| Scoring A/B/C (Sx_CUSTOM_PROGRAM_03) | volume/zone, équilibre, redondance (`variant_group`), fatigue, réalisme durée (`estimated_slot_minutes`), faisabilité matériel, `overload_compatibility` |
| Librairie custom | affichage des métadonnées des programmes user |
| Matérialisation en `WorkoutTemplate` custom | noms canoniques + `machine_slug`/`machine_family` recopiés dans les rows catalogue custom |
| Overload (Sx_30, inchangé) | cohérence : `chain`/`equipment_family` alignés sur la catégorisation d'incréments existante (`categorize_exercise`) — **sans modifier** `overload_inputs` |

## 11. Non-goals

Pas d'interface UI · pas de migration · pas de seed · pas de scoring (spec 03) · pas de
génération (moteur = spec parent §11, build 04) · pas de session launch · **pas de correction
du catalogue système** (`reference_split.json` intouchable ici, même pour un gap constaté) ·
pas de claims biomécaniques absolus ni médicaux · pas de renommage de noms historiques ·
pas de peuplement de la table `Muscle` (OQ-EKB-C) · pas de rebrand.

## 12. Open questions

| OQ | Question | Position par défaut proposée |
|---|---|---|
| OQ-EKB-A | EKB JSON pur ou seed DB ? | Option C séquencée : JSON canonique d'abord, seed DB optionnel gaté (§7) |
| OQ-EKB-B | Granularité des variantes V1 ? | une entrée par nom historique existant + variantes nouvelles uniquement si consommées par le wizard V1 (pas d'encyclopédie) |
| OQ-EKB-C | Peupler `Muscle` maintenant ou rester BodyZone-first ? | **BodyZone-first V1** ; `Muscle` reste vide (cohérent Sb_32.1, aucune anatomie inventée) |
| OQ-EKB-D | Machines inconnues (salle de l'utilisateur) ? | V1 : familles d'équipement génériques ; machine précise = attribut optionnel ; pas de gestion de parc par salle |
| OQ-EKB-E | Exercices cardio ? | hors EKB V1 (le cardio reste au niveau séance, `kind=cardio` — parent §14) ; OQ rouverte si le wizard V2 l'exige |
| OQ-EKB-F | Abdos / gainage ? | inclus V1 (zone `core` existante) avec `overload_compatibility: limited/none` et rep targets temps différés |
| OQ-EKB-G | Fatigue/technicité sans source externe ? | curation opérateur prudente, valeurs conservatrices, `confidence: inferred` explicite ; jamais présenté comme mesure |
| OQ-EKB-H | `confidence_level` par champ ou par entrée ? | **par entrée V1** (simple) ; par champ si la QA révèle des besoins ciblés |
| OQ-EKB-I | Séparer metadata sûre vs inférée ? | oui, via `confidence` (§5) + `source` au niveau fichier ; pas de fichier séparé V1 |

## 13. Acceptance criteria (cette spec)

- [ ] Audit de l'existant complet et chiffré (§3 : 53 properties / 103 noms / 52 absents /
      91 mappings / 25 machines / QA scripts recensés).
- [ ] Modèle EKB V1 proposé (identité §4 + taxonomie §5 + variantes §6).
- [ ] Stockage recommandé (§7, Option C séquencée).
- [ ] QA future définie (§9, 8 checks).
- [ ] Aucune modification code/data/seed/migration (diff = docs uniquement).
- [ ] Registry/roadmap mis à jour (`SPEC DRAFT OPENED`).
- [ ] Build non autorisé — human review de cette spec = prochaine décision.

## 14. Build queue proposée (aucune n'est ouverte par cette spec)

| Build | Objet | Gate |
|---|---|---|
| `Sb_CUSTOM_PROGRAM_EKB_01` | Audit + QA **read-only** : script de couverture catalogue↔EKB, snapshot des 103 noms, rapport de gaps | spec 02 acceptée |
| `Sb_CUSTOM_PROGRAM_EKB_02` | **JSON canonical EKB draft** (`data/exercise_knowledge_base.json`, 103 entrées, taxonomie §5) — data-only, review ligne à ligne | EKB_01 livré |
| `Sb_CUSTOM_PROGRAM_EKB_03` | **QA script classifiability** (les 8 checks §9, exit code CI-able) | EKB_02 livré |
| `Sb_CUSTOM_PROGRAM_EKB_04` | **Optionnel** : seed DB additive-only (tables `ekb_*`, versionnées, jamais destructives) | acceptance dédiée + GO explicite |

---

*Spec draft — build, migrations, seed et code applicatif explicitement non autorisés.
Prochaine décision : human review de ce document.*
