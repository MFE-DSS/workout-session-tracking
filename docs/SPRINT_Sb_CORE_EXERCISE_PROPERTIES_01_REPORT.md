# SPRINT Sb_CORE_EXERCISE_PROPERTIES_01 — rendre `core` programmable (RAPPORT)

**Train :** `AUREN_EFFECTIVE_VOLUME_COMPLETION_01`, tranche 2/4 ·
**Base canonique :** `8412ccd` · **Branche :** `sb/core-exercise-properties-01` ·
**Tier :** `check_scope` disait `ISOLATED` — **verdict corrigé à la main**, et
c'est ce qui a sauvé la tranche (§5).

---

## 1. Préflight — table de preuves, exercice par exercice

Les **8** exercices que le référentiel canonique classe `core` :

| Exercice | BodyZone | EKB `zone_primary` | Dans un template curé | Motif / matériel connus | Décision |
|---|---|---|---|---|---|
| Crunch câble à genoux | `core` | `core` | **oui** (×3) | aucun | **doté** |
| Pallof press câble | `core` | `core` | **oui** | aucun | **doté** |
| Relevé de jambes suspendu | `core` (correction revue) | `calves` ⚠︎ | **oui** | aucun | **doté** |
| Roulette abdominale | `core` | `core` | **oui** (×2) | aucun | **doté** |
| Roulette abdominale (ab wheel rollout) | `core` | `core` | **oui** | aucun | **doté** |
| Decline crunch | `core` (classifieur seul) | `null`, `todo` | **non** | aucun | **laissé dehors** |
| Hanging knee raise | `core` (classifieur seul) | `null`, `todo` | **non** | aucun | **laissé dehors** |
| Machine crunch | `core` (classifieur seul) | `null`, `todo` | **non** | aucun | **laissé dehors** |

La preuve décisive est la **présence dans un template curé de
`reference_split.json`** : le catalogue les **programme déjà**, avec un
`set_scheme` réel. C'est le signal le plus fort disponible qu'il s'agit
d'exercices utilisables, et il manque totalement aux trois autres.

`Relevé de jambes suspendu` porte `calves` dans l'EKB — artefact déjà arbitré
par `KNOWN_MAPPING_CORRECTIONS`, dont le contrat de zones renvoie `core`.

---

## 2. Le matériel n'est pas inventé — et c'est la décision principale

**Aucune source du dépôt ne dit avec quel matériel ces exercices se font** : ni
`exercise_properties`, ni l'EKB, ni `machine_slug` / `machine_family` dans
`reference_split`.

Aucun `equipment_family` n'est donc déclaré. Conséquence tenue :

- **sans restriction de matériel** ⇒ `core` est programmable ;
- **sous restriction** ⇒ le filtre écarte un candidat sans matériel déclaré, et
  la zone sort en **`UNMET_EQUIPMENT`**.

C'est exact : ce qui manque est un **matériel documenté**, pas un exercice.
Deviner « câble » parce que le nom contient « câble » serait l'inférence par le
nom que le brief interdit — et doublement fausse ici, le vocabulaire existant
(`barbell`/`bodyweight`/`cable`/`dumbbell`/`machine`/`smith`) n'ayant aucune
famille pour une roulette abdominale.

**Zéro fabrication prime sur la complétude** : trois exercices restent dehors,
nommés.

---

## 3. Le full sweep a refusé ma première conception — et il avait raison

La première version écrivait les cinq entrées dans `exercise_properties.json`.
Les tests ciblés passaient. **Le full sweep a fait tomber quatre choses** que
le sweep ciblé ne voyait pas :

| Test | Ce qu'il protège |
|---|---|
| `test_exercise_properties_loads_and_validates` | **chaque entrée doit déclarer un `equipment_family`** |
| `test_covered_status_matches_properties_membership` | cohérence EKB `coverage_status` ↔ appartenance au registre |
| `test_gaps_are_exactly_the_52_known_missing_names` | liste de lacunes EKB épinglée |
| `test_martin_generated_program_is_pinned_and_complete` | empreinte du programme morpho |

Le premier est un **vrai contrat**, pas un test périmé. Il ne laissait que deux
issues : **inventer** un matériel (interdit) ou **relâcher le contrat** du
registre de substitution pour tout le dépôt.

### L'erreur était de catégorie

`exercise_properties.json` se décrit lui-même comme les « propriétés enrichies
par exercice **pour la substitution heuristique** ». Un exercice de tronc n'est
pas un candidat de substitution : il est inatteignable par N1, N2, N3 et les
passerelles. **Le placer là était une erreur de catégorie que le contrat a
révélée.**

**Seam retenu, le plus petit possible** : un registre `planner_candidates`
distinct, que le planificateur compose avec le registre de substitution. Celui-ci
reste **inchangé au bit près** — les 69 entrées, le contrat, la cohérence EKB et
l'empreinte morpho passent tous sans modification.

L'isolement du tiroir devient une propriété **par construction** plutôt qu'une
propriété démontrée : il n'y a rien de nouveau à voir pour la substitution.

---

## 4. Motif : aucun vocabulaire nouveau

`core` est un `PatternMotor` **déjà présent** dans `VALID_PATTERN_MOTORS` — et
jusqu'ici inutilisé. Aucun `flexion_core`, `anti_rotation` ni `anti_extension`
n'est créé ; un test l'interdit.

## 5. Tier corrigé à la main

`check_scope` a classé la première version `ISOLATED` : il n'inspecte que
`app/`, et le changement portait sur un **fichier de données**.

C'est un faux négatif **déjà consigné en mémoire** : `exercise_properties.json`
a un rayon d'impact `shared_code`. Verdict remonté d'un cran à la main, et
**full sweep local** lancé malgré l'avis de l'outil.

**C'est précisément ce sweep qui a sauvé la tranche.** Sans lui, une conception
violant un contrat de données serait partie en CI — et le sweep ciblé, lui,
était vert.

---

## 6. Résultat

| | Avant | Après |
|---|---|---|
| Zones servables sans restriction | 10/11 | **11/11** |
| Séries physiques/semaine | 44 | **48** |
| Séries effectives | 50 | **54** |
| Σ bornes basses | 126 | 126 |

Le créneau `core` sélectionne « Crunch câble à genoux », 4 séries.

L'écart au budget **reste large** — cette tranche ferme une lacune de
*servabilité*, pas de volume. C'est la tranche 3 qui alloue la capacité.

---

## 7. Tests — 27 dédiés

Registre de substitution **intact** (69 entrées, aucun ajout) · aucun candidat
de tronc atteignable dans le tiroir, vérifié exercice par exercice · bridges
vérifiés · le pool du planificateur étend sans muter (cache compris) ·
aucun matériel inventé · vocabulaire existant seulement · classement canonique
vérifié pour chaque ajout · présence en template curé prouvée · les trois sans
preuve restent absents · `core` programmable sans restriction · honnêtement
`UNMET_EQUIPMENT` sous restriction · `core` ne crédite que `core` · le pool
grandit d'exactement 5 · le chargeur valide toujours · aucune autre zone ne
change de dose · déterminisme.

### Neuf tests existants mis à jour — et pourquoi ce n'est pas un affaiblissement

Cinq épinglaient la lacune que cette tranche ferme. **Quatre autres utilisaient
le créneau `core` vide comme simple décor** pour éprouver une garde générale
(« un créneau vide ne couvre rien », « un créneau vide ne devient pas un
exercice »). Ces gardes restent indispensables : elles ont été **re-ciblées sur
une restriction de matériel**, seule situation produisant encore un créneau
vide. Les supprimer aurait retiré la protection en même temps que son décor.

## Verdict

`core` devient programmable **parce que la preuve existait**, pas parce qu'il
fallait atteindre 11/11 : cinq exercices que le catalogue programme déjà, avec
le `PatternMotor` qui les attendait.

**Aucun matériel n'a été inventé**, et la conséquence est assumée — la zone est
honnêtement indisponible sous restriction, avec la bonne raison nommée. Trois
exercices restent dehors faute de preuve.

**Le résultat le plus utile de cette tranche est la conception qu'elle a
abandonnée.** Écrire les cinq entrées dans le registre de substitution
paraissait évident et passait tous les tests ciblés ; c'est le **full sweep**,
lancé contre l'avis de `check_scope`, qui a montré qu'un contrat de données
l'interdisait — et que le vrai problème était une erreur de catégorie, pas un
champ manquant.

Le registre de substitution finit **inchangé au bit près**, et l'isolement du
tiroir n'a plus besoin d'être prouvé : il est structurel.
