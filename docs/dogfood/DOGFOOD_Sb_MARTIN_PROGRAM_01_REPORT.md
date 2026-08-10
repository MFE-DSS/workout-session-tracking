# DOGFOOD — Sb_MARTIN_PROGRAM_01 : programme morphologie-aware dérivé de Martin (PRIVÉ)

> ⚠️ **PRIVÉ / TEST-ONLY.** Ce document décrit le programme **dérivé** de la fixture dogfood
> privée de Martin (`tests/fixtures/dogfood/martin_program.py`). Il n'est **ni** un template
> catalogue, **ni** un Custom Program, **ni** persisté, **ni** exposé en runtime / `/library`.
> Aucune donnée Martin n'existe en logique globale — uniquement dans la fixture de test.

## 1. Objet

4ᵉ build de la file `Sx_MORPHO_PROGRAM_01`. On **dérive** le programme de Martin en composant,
via le générateur déterministe livré (`Sb_MORPHO_PROGRAM_GENERATOR_01`) :
- ses **descripteurs de morphologie** (`Sb_MORPHO_PROFILE_01`, faits privés → 3 candidats de
  priorité : deltoïdes latéraux, haut des pectoraux, deltoïdes postérieurs/haut du dos) ;
- ses **priorités d'entraînement déclarées** (privées) : 4 priorités morphotype + 3 de maintien ;
- l'**availability** de sa salle (Fitness Park : machine, câble, haltères, barre, smith, poids du corps).

**La dérivation est pure** : rien n'est persisté, aucun template/`reference_split`/`exercise_properties`
n'est muté, aucune expansion EKB. Le passage par le **cycle Custom réel** est le build **suivant**
(`Sb_MORPHO_DOGFOOD_01`), pas ici.

## 2. Programme dérivé (déterministe, `generated_program_id = mpg1-391c65154b3ed546`)

Forme « Full Body — Morphotype Priority » (8 intentions). Ordre : intentions issues des
**descripteurs** de morphologie d'abord, puis le reste issu des **priorités**.

| # | Intention | Priorité morphotype | Exercice préféré (pool) | Score | Statut |
|---|---|---|---|---|---|
| 1 | `lateral_delt_priority` | **deltoïdes latéraux** | — | — | ⚠️ **gap de couverture** |
| 2 | `upper_chest_primary_press` | **haut des pectoraux** | Chest Press machine | 80 | ✅ rempli |
| 3 | `rear_delt_upper_back_accessory` | **deltoïdes postérieurs** | — | — | ⚠️ **gap de couverture** |
| 4 | `calves_gastrocnemius_priority` | **mollets (gastrocnémien)** | — | — | ⚠️ **gap de couverture** |
| 5 | `calves_soleus_priority` | **mollets (soléaire)** | — | — | ⚠️ **gap de couverture** |
| 6 | `upper_back_depth_row` | haut du dos (maintien) | Rowing chest-supported | 80 | ✅ rempli |
| 7 | `quad_minimum_effective_dose` | quadriceps (**maintien**) | Leg extension câble unilatéral | 60 | ✅ rempli |
| 8 | `posterior_chain_hinge` | chaîne postérieure (maintien) | — | — | ⚠️ **gap de couverture** |

**3 slots remplis / 8** · **5 warnings de couverture** · **0 fabrication** · **0 rejected** (aucun
descripteur gardé).

## 3. Finding dogfood MAJEUR — les priorités morphotype de Martin ne sont pas couvertes

**Constat honnête et reproductible** : les **4 muscles-priorités morphotype** de Martin
(deltoïdes **latéraux**, deltoïdes **postérieurs**, **mollets** ×2) sont **exactement ceux que le
pool `exercise_properties` (53 entrées) ne couvre pas**. Le générateur, fidèle à son contrat
« unsupported taxonomy → warning, jamais de fabrication », **omet ces slots avec un warning
explicite** plutôt que d'y placer un faux exercice (ex. une leg extension pour un slot mollets).

**Cause** : le pool de scoring est `exercise_properties.json` (les exos porteurs de `props` pour
`compute_proximity`), qui ne contient **ni** élévations latérales, **ni** oiseau/rear-delt isolé,
**ni** mollets, **ni** hinge isolé. Le catalogue « Full Body — Morphotype Priority » (mergé) mappe
pourtant ces intentions vers de **vrais noms EKB** (E1-E8) — mais ces noms **n'ont pas encore de
`properties`**, donc ils ne sont pas scorables.

**Ce n'est pas un échec de ce build** : le build **réussit** à dériver honnêtement le programme et
à **exposer le blocage concret**. C'est la valeur du dogfood.

## 4. Recommandation (pour la file)

**Avant `Sb_MORPHO_DOGFOOD_01`** (cycle Custom réel), un build de **couverture `exercise_properties`**
(ajouter les `props` des exercices morphotype prioritaires — élévations latérales, oiseau/rear-delt,
mollets debout/assis, hinge — sur des **noms EKB existants**, additif, tier `shared_code`) est
nécessaire pour que les slots-priorités de Martin soient **remplis** plutôt que signalés vides.
Sans lui, un programme Martin passé au cycle réel serait majoritairement des slots vides sur
ses priorités — contraire à l'intention morphotype.

**Aucune action prise ici** : ce build est un finding docs+fixture pur ; l'extension de couverture
sera un sprint dédié **sur GO explicite**.

## 5. Interdits tenus

0 DB · 0 migration · 0 persistance · 0 Custom Program · 0 publication · 0 template · 0 mutation
`reference_split.json`/`exercise_properties.json` · 0 expansion EKB · 0 modif substitution/générateur ·
0 UI/`/library` · **0 donnée Martin en logique globale** (fixture test privée uniquement).
