# `Sb_OPS_LOCAL_SWEEP_ADAPTIVE_BATCH_01`

**Canonique de départ** : `a867699` · **Tier `check_scope`** : `CI_INFRA`

---

## 1. Le défaut, mesuré sur quatre tranches consécutives

| Tranche | Lots verts | Issue | Pic / budget |
|---|---|---|---|
| `TRAIN 1-C` | 115 / 139 | **arrêt** | 1866 / 1852 Mo |
| `TRAIN 1-D` | 140 / 140 | abouti | 1634 / 1968 Mo |
| `TRAIN 1-E` | 113 / 140 | **arrêt** | 1932 / 1772 Mo |
| `POST_CONVERGENCE_INTEGRITY_01` | 117 / 140 | **arrêt** | 1936 / 1841 Mo |

**Trois arrêts sur quatre, et pas un seul test rouge dans les trois cas.** Le
garde-fou protégeait la machine — c'est son rôle et il l'a bien fait — mais il
laissait le travail inachevé. À chaque fois la même manœuvre manuelle : lire le
conseil imprimé, relancer avec un lot plus petit, ou finir la queue avec un
runner improvisé.

### La cause n'est pas le code testé

Le budget vaut 60 % de la mémoire **disponible au démarrage** : 2397 Mo une
semaine, 1772 la suivante, selon ce que l'éditeur et ses serveurs de langage
occupent. Le pic d'un lot, lui, ne dépend pas de ce budget.

Sur une machine chargée, la taille de lot par défaut devient donc
**inatteignable quoi que fasse le dépôt**. Aucune tranche produit ne peut
corriger cela, et aucune ne devrait avoir à choisir sa taille de lot à la main.

---

## 2. Le correctif

Au lieu d'abandonner, le sweep **halve le lot et rejoue les mêmes fichiers**.
Le conseil qu'il imprimait, il l'applique.

```
[local-sweep] lot 26 à 1662 Mo, budget 1500 Mo.
[local-sweep] fichiers du lot : … 8 fichiers …
[local-sweep] ADAPTATION 1 : lot ramené à 4,
[local-sweep] les mêmes fichiers sont rejoués. Aucun test n'est sauté.
```

### Trois décisions, et leurs raisons

**Il rétrécit, il ne regrossit jamais.** La pression mémoire d'un poste est
monotone sur la durée d'un sweep — l'éditeur ne rend pas ce qu'il a pris.
Regrossir rouvrirait l'arrêt qu'on vient de payer et ferait osciller la taille
de lot autour du seuil : plus de démarrages, pas moins d'arrêts.

**L'abandon subsiste pour le seul cas où il veut dire quelque chose** : un lot
d'**un** fichier au-dessus du budget. Là, le coût vient de ce fichier — mesuré,
le plus lourd de la suite en vaut 1,3 Go à lui seul — et aucun découpage n'y
changera rien.

**Aucun fichier n'est sauté.** L'index n'avance qu'après un lot réussi, et le
numéro de lot est rendu avant de rejouer. Un sweep qui saute des fichiers en
silence serait pire que celui qui s'arrête : il rendrait un vert qui ne couvre
pas tout.

---

## 3. Preuve, bout en bout

Exécution forcée à `SWEEP_BATCH=8`, `SWEEP_BUDGET_MB=1500` — un budget
volontairement bas pour déclencher la pression :

```
[local-sweep] ADAPTATION 1 : lot ramené à 4
[local-sweep] ADAPTATION 2 : lot ramené à 2
[local-sweep] ADAPTATION 3 : lot ramené à 1
[local-sweep] lot 105 · ok · pic 135 Mo · 280/280 fichiers
[local-sweep] pic mémoire observé : 1366 Mo (budget 1500 Mo)
[local-sweep] 3 adaptation(s) : lot final 1.
[local-sweep] Aucun fichier sauté — les lots réduits ont été rejoués.
[local-sweep] tous les lots sont verts.
```

**280 / 280 fichiers, trois adaptations, zéro intervention.** Dans l'ancienne
version, la première pression aurait rendu un `exit 3` et 27 % de la suite non
exécutée.

---

## 4. Une correction de libellé, et pourquoi elle vaut d'être faite

`LOTS EN ÉCHEC : 4` imprime la **liste des numéros** de lots fautifs. Je l'ai
lu « quatre lots » et j'ai failli rapporter un défaut inexistant, avant de
vérifier dans le script. La ligne dit désormais `NUMÉROS DES LOTS EN ÉCHEC`.

Un message d'outillage qui se lit de deux façons finit par être lu de la
mauvaise.

---

## 5. Vérifications

| Contrôle | Résultat |
|---|---|
| `check_scope.py` | **`CI_INFRA`** |
| `bash -n` + `shellcheck` | propre |
| `test_ci_runner_stability` | 89 → **95** passants |
| preuve d'adaptation | **3 adaptations · 280/280 fichiers · 0 saut** |
| full sweep local | **obligatoire à ce tier** — c'est la preuve ci-dessus |
| CI réelle | **impérative avant merge à ce tier** |

**Aucun gate retiré. Le chemin CI est inchangé** — ce script refuse toujours de
tourner en CI, et `run_ci_pytest.sh` reste la commande du runner.

---

## Closeout post-merge

| | |
|---|---|
| PR | [#159](https://github.com/MFE-DSS/workout-session-tracking/pull/159) |
| Méthode | `--merge`, tête épinglée `4119fd6` |
| Commit de merge | **`5499c34`** |
| CI de PR | **9 / 9** verts · gate Sonar `OK` |
| CI canonique au push | run `32849308202` — **succès** |
| Fils de revue · migration | 0 · aucune |

**Validation CI réelle : satisfaite** (tier `CI_INFRA`).

⚠ Un détail de procédure, consigné : après le merge de #158, GitHub a rendu
`mergeable: UNKNOWN` sur #159 le temps de recalculer l'état contre la nouvelle
base. Ce n'est **pas** un conflit — attendre le recalcul avant de juger évite
de diagnostiquer une panne qui n'existe pas. Même famille que
`ci-dispatch-blocked-by-conflict`, mais bénigne.

### État

**`CLOSED`** — nettoyage exécuté sur ordre opérateur.
