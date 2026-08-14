# SPRINT Sb_OPS_CI_SCALE_01 — Sharding de la suite (RAPPORT)

**Base :** `sb/ops-ci-runner-stability-01` (#87, non mergée) + canonique `ea8261f` ·
**Branche :** `sb/ops-ci-scale-01` · **Tier :** **CI_INFRA** — validation sur CI réelle
impérative, ce qui est l'objet même du sprint.
**Absorbe et remplace `Sb_OPS_CI_RUNNER_STABILITY_01` (#87)** : le sharding dépend de sa
télémétrie, de sa commande canonique et de son correctif de fuite.

## 1. Cause racine — mesurée avant toute mutation

Trois arrêts du runner sur la PR #86, à 95–96 %, **sans aucun échec de test**. La
télémétrie instrumentée par #87 a donné le verdict :

| | `-n auto` (4 workers) | `-n 2` |
|---|---|---|
| MemAvailable **minimum** | **24 Mo** | **87 Mo** |
| SwapFree minimum | **1 Mo** | **105 Mo** |
| Pic RSS | 4,34 Go | **8,07 Go** |
| Durée | 13 min 33 | 21 min 56 |

Runner : **4 cœurs, 15 989 Mo, 3 071 Mo de swap, ~87 Go de disque libre**.

**`-n 2` a été mesurée puis RÉFUTÉE.** Le pic mémoire a *doublé* et la durée aussi. Le pic
suit le nombre de tests qu'un worker exécute : **4,60 Mo/test** à quatre workers,
**4,28 Mo/test** à deux. Même taux dans deux configurations opposées ⇒ **fuite linéaire par
test**, pas une pression de concurrence.

Conséquence décisive : **le total est invariant au nombre de workers.**

```
3 824 tests × ~4,4 Mo  ≈  16,6 Go     machine : 15,99 Go
```

Aucun réglage de parallélisme ne peut combler un déficit structurel de ~0,6 Go. La seule
voie sans toucher à un seul test : **moins de tests par machine**.

## 2. Ce qui a été livré

**Sharding au niveau FICHIER, jamais plus fin.** Plusieurs modules sont sensibles à l'état
— la `conftest` purge `app.*` à chaque test, des fichiers portent leurs propres fixtures de
module et des hypothèses d'ordre. Découper un fichier casserait des garanties construites
sur plusieurs sprints.

**Manifeste généré, pas maintenu.** Fichiers triés par nom (clé stable, indépendante du
système de fichiers, de l'horloge et des durées) puis distribués en round-robin. Un
nouveau fichier de test est affecté automatiquement ; la partition se reproduit partout.
Round-robin plutôt que blocs contigus : des voisins alphabétiques coûtent souvent pareil.
**226 fichiers → 113 + 113.**

**Deux invariants, vérifiés en CI AVANT d'exécuter quoi que ce soit, et épinglés par
tests** : `union(shards) == suite canonique` et `intersection == ∅`. Un fichier perdu
réduirait la couverture en gardant tous les jobs au vert — c'est exactement l'échec que ce
garde-fou rend impossible.

**Couverture non affaiblie.** Chaque shard écrit `coverage-shard-N.data`
(`relative_files = true` ⇒ chemins identiques d'une machine à l'autre) ; un job aval les
combine via le mode parallèle natif de coverage.py et produit **un unique `coverage.xml`
faisant autorité**. Aucun rapport local de shard n'est publié ; le contrat Sonar est
inchangé.

## 3. Le piège qui aurait fait le plus de dégâts

Une matrice nue renomme le check requis en `pytest + QA scripts (1)` / `(2)` — et rend
**silencieusement toute PR non fusionnable** face à la protection de branche.

Le nom est préservé par un **job agrégateur aval** qui, en plus :

- **échoue bruyamment si un shard a échoué** — il ne peut jamais rapporter un succès
  par-dessus un shard rouge ;
- héberge les contrôles **QA / migration**, qui doivent tourner une fois et non par shard.

## 4. Résultats mesurés

| | `-n auto` | `-n 2` | **Sharded** |
|---|---|---|---|
| MemAvailable min | 24 Mo | 87 Mo | **5 913 / 6 233 Mo** |
| SwapFree min | 1 Mo | 105 Mo | **3 071 Mo — jamais entamé** |
| Pic RSS | 4,34 Go | 8,07 Go | **4,84 / 4,52 Go** |
| Durée phase de test | 13 min 33 | 21 min 56 | **~10 min** (parallèle) |

**Classement : HEALTHY** — cible ≥ 4 Go atteinte avec ~6 Go réels, durée très en deçà des
30 min. Le swap n'est **pas entamé du tout**, contre 1 Mo libre auparavant : c'est la
différence entre « ça passe parfois » et « il y a de la marge ».

### Parité de couverture — expérience contrôlée, même arbre

| | Tests | Couverture | Classes |
|---|---|---|---|
| Monolithique | 3 824 | **93,08 %** | 114 |
| Shardé (1 970 + 1 854) | **3 824** | **93,08 %** | 114 |

**Exacte.** Aucun test retiré, aucun rendu optionnel, pas de `testmon`, pas de seuil Sonar
affaibli, pas de base partagée entre jobs.

> Le chiffre combiné **en CI** est de 92,42 %. L'écart avec le local est un **delta de
> plate-forme** (macOS vs Linux), antérieur et sans rapport avec le sharding : l'A/B
> ci-dessus a été mené sur **une seule machine et un seul arbre**, ce qui est précisément
> ce qui en fait une preuve.

## 5. Deux défauts introduits puis corrigés

**(a) Un artefact de 9 941 lignes committé par erreur** — `coverage-combined.xml`, issu de
mon propre essai local. Retiré, et `coverage-*.xml` désormais ignoré.

**(b) La combinaison a échoué au premier run shardé** :
`Couldn't combine from non-existent path '.coverage.shard-*'`.
`actions/upload-artifact@v4` **ignore les fichiers cachés** par défaut, et
`.coverage.shard-N` est un dotfile : les shards n'ont rien uploadé.

**Le mode de défaillance était pire que la défaillance.** Avec `if-no-files-found: warn`,
un shard manquant aurait combiné ce qui était arrivé et publié une **couverture
sous-estimée** que Sonar aurait jugée complète — silencieusement, et dans le sens vert.
Trois correctifs : nom de fichier visible, `if-no-files-found: error`, et une combinaison
qui **refuse de tourner** si les deux fichiers ne sont pas là.

## 6. Ce qui vient de #87 et reste acquis

Télémétrie `CI_RESOURCE` diffusée sur **stdout** (les arrêts sautaient l'upload d'artefact —
une mesure non récupérée n'existe pas) · `scripts/run_ci_pytest.sh` comme **source unique**
de la commande CI, avec garde anti-divergence · correctif de la **fuite de répertoires
temporaires** du fixture `client` (**53 765 → 0** ; le nettoyage supprimait le fichier DB
mais pas le répertoire, et était placé après le `with`, donc sauté quand un test échouait).

Ce dernier point reste classé **hygiène** : le disque n'a jamais été en tension
(571 Mo consommés sur 87 Go).

## Verdict

**Livré, mergé.** La CI passe d'un régime où elle demandait plus de mémoire que la machine
n'en offre, à **~6 Go de marge et un swap intact**, sans retirer un seul test ni toucher à
la couverture.

**Limite assumée, et elle compte** : le sharding **déplace le mur, il ne le supprime pas**.
La fuite de ~4,4 Mo par test demeure ; la suite grossit d'environ **100 tests par sprint**,
soit ~440 Mo de plus à chaque livraison, répartis sur deux shards. Au rythme actuel la
marge tient largement, mais la correction de la fuite — qui touche l'isolation par test de
`Sb_CI_02_3` et mérite son propre sprint mesuré — reste le seul changement qui modifie la
**pente** plutôt que l'ordonnée.
