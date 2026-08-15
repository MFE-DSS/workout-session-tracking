# SPRINT Sb_WEEKLY_PLAN_CAPACITY_ALLOCATOR_01 — allouer la capacité (RAPPORT)

**Train :** `AUREN_EFFECTIVE_VOLUME_COMPLETION_01`, tranche 3/4 ·
**Base canonique :** `00c1657` · **Branche :** `sb/weekly-plan-capacity-allocator-01`

---

## 1. Le constat qui motive la tranche

Le planificateur produisait **48 séries physiques quelle que soit la cadence**,
simplement étalées plus finement :

| Cadence | Exercices/séance | Séries/séance |
|---|---|---|
| 2 | 6 | 24 |
| 4 | 3 | 12 |
| 6 | 2 | 8 |

Le catalogue curé prescrit **6–8 exercices et 18–24 séries** par séance. À
cadence 4, la capacité déclarée permettait ~96 séries ; le plan en utilisait 48.
**La capacité n'était pas allouée, elle était subie.**

---

## 2. Dur / souple, et ce que 126 n'est pas

`Σ planning_low = 126` **n'est pas une cible physiologique** : c'est l'agrégat de
onze valeurs produit héritées. L'objectif est le **meilleur programme faisable
sous contraintes**, pas un compteur au vert.

**DUR** : cadence · matériel · identité canonique (zéro fabrication) · limites
du cycle de vie · plafond `planning_high` **sur l'allocation** · déterminisme.

**SOUPLE, ordonné** : servir toute zone d'abord une fois → remonter les moins
couvertes → minimiser le pire déficit relatif → viser `baseline` → favoriser les
priorités **dans** leur bande → peu d'identités → séances non encombrées.

**Ratio de couverture** = `effective_sets / planning_low_sets`. Un **ratio de
planification** : ni récupération, ni pourcentage d'hypertrophie, ni activation,
ni probabilité de progresser. Jamais affiché comme métrique corporelle
(`COVERAGE_RATIO_GUARD`).

**Forme de séance** : bornes souples 8 exercices / 24 séries, **mesurées** sur
les 15 templates `strength` du dépôt (6–8, médiane 7 ; 18–24, médiane 20).
`PRODUCT_CONVENTION` versionnée — pas « 24 séries est optimal ». Le plafond dur
`MAX_EXERCISES_PER_SESSION` reste intact et n'est jamais approché.

---

## 3. Dépassement : trois états, jamais confondus

| État | Définition | Verdict |
|---|---|---|
| `NONE` | dans la bande | — |
| **`PREVENTABLE`** | l'allocation **directe** dépasse la bande | **défaut — doit rester à 0** |
| `INCIDENTAL` | dépassement par crédit reçu en servant d'autres zones | **autorisé, explicite** |

`planning_high` borne ce qui est **attribué**. Retirer du travail primaire à
`lats` pour faire redescendre un compteur de `biceps` appauvrirait une zone
sous-servie au profit d'une zone que personne n'entraîne directement.

Les zones receveuses de crédit indirect sont **dérivées** de `body_zone_source`
via la politique de contribution — aucune table « le dos donne du biceps ».

**Mesuré : `PREVENTABLE = 0` à toutes les cadences.**

---

## 4. Le défaut que j'ai introduit, et comment il a été trouvé

Ma première réponse à la décision opérateur A a été une **allocation en deux
phases** : servir d'abord les zones ne recevant aucun crédit indirect, puis les
autres avec l'exposition réelle connue. Elle supprimait bien le dépassement.

**Elle a produit un défaut bien pire.** La phase 1 consommait **toute** la
capacité de séance ; la phase 2 ne trouvait plus une seule place libre.
Résultat mesuré :

```
utilisateur déclarant « Bras »
→ biceps : 0 occurrence, 0 exercice, 10 séries effectives
→ triceps : 0 occurrence, 0 exercice,  6 séries effectives
```

**Un programme sans le moindre curl ni pushdown**, avec des compteurs d'apparence
correcte remplis par les tirages et les presses. C'est exactement ce que la porte
de sortie interdit : « every user-declared priority is materially represented ».

**Correction** : suppression des deux phases, et **une seule passe ordonnée** où
la première clé de tri est « cette zone a-t-elle déjà **une occurrence
directe** ». Toute zone servable reçoit donc un exercice réel avant que
quiconque n'en reçoive un second ; les zones receveuses restent servies en
dernier **à égalité**, ce qui conserve l'effet recherché sans affamer personne.

Le dépassement `biceps` redevient **INCIDENTAL** — allocation directe 4 séries,
très en deçà de la bande — ce qu'il aurait toujours dû être classé.

**Une garde a été ajoutée pour ce défaut précis** (`test_a_zone_covered_only_
indirectly_still_gets_a_real_exercise`), et une plantation vérifie qu'elle mord :
neutraliser la clé anti-famine fait tomber deux tests.

---

## 5. Résultats mesurés

| Cadence | Physique | Effectif | Identités | Occurrences | ≥ low | ≥ base | Pire | Médiane | PREV | INC |
|---|---|---|---|---|---|---|---|---|---|---|
| 2 | 48 | 54 | 11 | 12 | 1 | 0 | 0,29 | 0,50 | **0** | 0 |
| 3 | 72 | 84 | 11 | 18 | 3 | 1 | 0,50 | 0,57 | **0** | 0 |
| 4 | **96** | 114 | 11 | 24 | 5 | 2 | 0,57 | 0,86 | **0** | 1 |
| 5 | **120** | 142 | 11 | 30 | **9** | 5 | 0,86 | 1,00 | **0** | 1 |

Toutes les séances : **6 exercices / 24 séries**, dans le précédent catalogue.

**Identités stables à 11 à toutes les cadences** : le volume vient
d'**occurrences répétées**, jamais d'exercices inventés. Un même « Lat pulldown »
revient dans plusieurs séances ; aucun exercice n'apparaît deux fois dans la
même séance.

**À cadence 6, le plan atteint `READY`** — toutes les zones à leur borne basse.
C'est la première fois que la bande produit complète est réalisable.

### Écarts avec la référence sauvegardée — investigués, pas forcés

`identités 11` (référence 10 à cadence 2) et `pire 0,29` (référence 0,00) :
la clé anti-famine sert désormais **toute** zone une fois avant d'en servir une
deuxième. Aucune zone ne reste à zéro, au prix d'une zone en moins à la borne
basse à cadence 2. C'est l'objectif souple n°1 qui prime sur le n°2, comme
spécifié.

---

## 6. Versions

`PLANNER_VERSION` **1 → 2** — la sémantique réalisée change matériellement.
`CAPACITY_ALLOCATOR_VERSION = "capacity-allocator-v1"`.
Les deux entrent dans l'empreinte déterministe du plan.

**`weekly-volume-v1` n'est PAS bumpée** : la politique de volume n'a pas changé,
seule sa réalisation.

---

## 7. Invariant de cadence — retiré et remplacé

`test_cadence_never_changes_the_weekly_set_total` est **retiré** : son
abstraction est devenue fausse.

- **INVARIANT 1 — budget** : changer `sessions_per_week` ne change **aucune**
  borne (`planning_low` / `baseline` / `planning_high`). Testé sur 5 cadences.
- **INVARIANT 2 — réalisation** : plus de capacité ne doit jamais produire une
  solution **lexicographiquement pire**. Comparaison **objective**, pas
  monotonie brute — un plateau reste légitime.

Formulation retenue : « plus de capacité permet de réaliser davantage d'un
budget inchangé », **jamais** « plus de fréquence mérite plus de volume ».

Un méta-test policier écrit puis **supprimé** : il comptait des occurrences de
chaîne et sa première assertion était neutralisée par un `or True`. Il ne
prouvait rien ; la vraie protection est l'invariant 2.

## Verdict

La capacité déclarée est enfin **allouée** : 96 séries à cadence 4 contre 48,
en séances de forme catalogue, avec 11 identités stables et zéro dépassement
préventable.

**Le résultat le plus important n'est pas ce gain, c'est le défaut que j'ai
introduit en chemin.** Optimiser la suppression d'un dépassement comptable m'a
fait produire un programme sans aucun exercice de bras pour un utilisateur qui
avait déclaré « Bras » — des chiffres corrects, une demande non servie. Le
correctif est structurel, et la garde qui l'attrape est prouvée mordante.

---

## Closeout (post-merge)

| | |
|---|---|
| PR | **#99** — `--merge --match-head-commit`, **sans** squash / `--admin` / force |
| Build | `39d9b6e` + correctif Sonar `47dd691` |
| Merge | **`cbf64f2`** |
| Gate Sonar | **`OK`** — couverture du neuf **97,9 %**, **0 smell**, 0 bug, 0 vulnérabilité |
| Threads / Gitar | **0 / 0** |
| Tests | shard 2 : 2 257 · full sweep local **4 272** |

### Capacité CI — **HEALTHY**

| | Shard A | Shard B |
|---|---|---|
| min MemAvailable | **5 148 Mo** | **5 173 Mo** |
| min SwapFree | 3 071 Mo — **jamais entamé** | 3 071 Mo — **jamais entamé** |

Troisième tranche consécutive au-dessus de 5 Go sur les deux shards.

### 1 finding Sonar — et l'affirmation sans preuve qu'il a révélée

`python:S1481` (MINOR) : `allocator_units` lié puis jamais lu — reste d'un
câblage antérieur. Le gate passait (10 < 14), mais la variable morte cachait
plus gênant : la docstring de `_contributions_from_occurrences` **affirmait
qu'un test vérifiait** la coïncidence entre les unités cumulées par
l'allocateur et celles recalculées par la politique partagée. **Ce test
n'existait pas.**

Les deux sont corrigés : la liaison est explicitement écartée, et un test
compare désormais `allocate_capacity` à `contributions_for` sur les mêmes
occurrences. Deux chemins, un seul résultat — la promesse est tenue plutôt
qu'écrite.
