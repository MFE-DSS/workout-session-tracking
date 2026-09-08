# UI-CP2.1 — l'échauffement cesse d'être une porte

**Tier `check_scope`** : `SHARED_CODE`.
**Origine** : un constat d'usage réel de l'opérateur, pas une mesure de labo.

---

## 1. Ce que l'opérateur a vécu

> « je clique sur sauter l'échauffement, ça passe à la première série ; mais si
> je valide la première série, ça retourne sur l'échauffement. Et ça désactive
> le timer. […] le CTA pour skipper l'échauffement ne va nulle part. […] la
> redondance que les valeurs doivent être obligatoirement remplies sur les
> échauffements. »

**Reproduit sur le build exact qui tourne en production** (`7943bc2`) :

| étape | état | minuteur |
|---|---|---|
| séance neuve | `warmup` | — |
| SAUTER L'ÉCHAUFFEMENT | `current_set` | — |
| **enregistrer S1** | **`warmup`** | **non** |
| recharger | `warmup` | non |

Le serveur redirigeait pourtant vers `…&rest=1` : **la branche « échauffement »
avalait le signal**. C'est `F1` + `F2`, déjà corrigés par `UI-CP2.0` et `A+`,
mergés mais **non déployés** — le dogfood a donc confirmé qu'une mesure de labo
décrivait un défaut vécu.

---

## 2. Le fond, que `UI-CP2.0` ne fermait pas

Deux trous restaient, identiques sur les deux builds :

* **le saut ne survivait pas au rechargement** — `?skipwarm=1` vit dans l'URL,
  parce que `Q-C` interdit d'écrire des données que l'utilisateur n'a pas
  produites ;
* **le seul moyen DURABLE de sortir de l'échauffement était d'y saisir des
  valeurs**, puisque `completed` se dérive de la présence d'un poids ou de
  répétitions.

L'utilisateur était donc devant un choix que le produit n'a pas à imposer :
**fabriquer des chiffres, ou rebondir**.

---

## 3. Options, et celle qui est retenue

| Option | Verdict |
|---|---|
| **A — persister l'intention de saut** (`warmup_skipped`) | ❌ Colmate le symptôme. Une migration pour contourner une porte qu'on pourrait retirer |
| **B — l'échauffement cesse d'être une porte** *(retenu, tranché par l'opérateur)* | ✅ Supprime le piège à sa racine. Plus rien à sauter, donc plus de bouton qui ne tient pas sa promesse, et plus jamais de valeur obligatoire |
| **C — marquer un échauffement fait sans valeur** | ❌ `completed` est **dérivé** de la présence d'une valeur, et ce contrat irrigue le score de qualité et les statistiques. Le plus direct en apparence, le plus risqué en réalité |

---

## 4. Ce que B change

L'exercice s'ouvre sur sa **première série de travail**. Les échauffements
vivent au-dessus, dans un tiroir replié d'une ligne — `○ Échauffement 0/2` —
disponibles, saisissables, **jamais bloquants**.

`Q-C` n'est pas contredite : elle devient **sans objet**. Rien n'est écrit,
parce qu'il n'y a plus d'obstacle à contourner.

### Le scénario, après

| étape | état | minuteur |
|---|---|---|
| ouverture de l'exercice | **`current_set`** | — |
| enregistrer S1 | **`rest`** | **oui** |
| recharger | **`current_set`** | — |
| recharger sans rien saisir | **`current_set`** | — |

**Zéro échauffement enregistré** dans tous les cas.

### ⚠ `WARMUP` survit, pour un seul cas

Un exercice qui n'a **aucune** série de travail — `work_total == 0` — n'a pas
d'autre travail : ses échauffements *sont* son travail, et l'état reste
souverain pour lui. Le retirer complètement aurait laissé cet exercice sans
état.

---

## 5. Trois retraits, et leurs remplaçants (`§5.3`)

| Retiré | Remplaçant |
|---|---|
| le bouton **« SAUTER L'ÉCHAUFFEMENT »** | **il n'y a plus de porte.** Une commande dont l'objet a disparu se retire, elle ne se remplace pas — une commande de moins dans un cockpit qui en comptait treize de trop |
| le paramètre **`skipwarm`** | retiré du routeur **et** de la signature, pas rendu inerte. Le garder en le lisant sans effet aurait été le calcul mort que `CP-0` a passé une tranche à retirer |
| le second bloc de récapitulatif d'échauffement | fusionné dans le tiroir unique, qui se rend désormais **même quand rien n'est fait** — c'est là qu'on s'échauffe |

---

## 6. Trois gardes supersédées, chacune par une plus forte

Aucune n'est supprimée sans remplaçant nommé, **dans le même fichier et la
même livraison** :

| Supersédée | Remplaçante |
|---|---|
| `test_l_invariant_de_monotonie_tient_sur_toute_la_table` — « une fois le travail commencé, plus jamais `warmup` » | `test_l_echauffement_ne_retient_jamais_un_exercice_qui_a_du_travail` — n'attend plus que le travail **commence** |
| `test_l_echauffement_reste_souverain_tant_que_rien_n_a_commence` — tenait exactement ce que B retire | `test_l_echauffement_reste_souverain_quand_il_EST_le_travail` — garde le seul cas où la souveraineté a un sens |
| `test_skipwarm_n_ecrit_toujours_rien` — gardait qu'un paramètre n'écrivait rien | `test_aucune_valeur_d_echauffement_n_est_requise_pour_avancer` — tient la **propriété d'usage**, prenant la plainte de l'opérateur au mot |

Plus `test_plus_aucune_sortie_ne_propose_de_sauter_l_echauffement`, qui fige le
retrait.

**La table de vérité est réécrite** : elle est la spécification de la machine à
états, et la machine a changé. 13 lignes, dont trois marquées `CP2.1` — celles
dont l'attendu passe de `warmup` à l'état du travail. La colonne `skipwarm` a
disparu avec le paramètre.

---

## 7. Vérifications

| Contrôle | Résultat |
|---|---|
| `check_scope` | `SHARED_CODE` |
| `ruff` | 1 `C901` **préexistant** sur `session_detail`, aucun ajouté |
| `check_ruff_budget` | **267 ≤ 548**, inchangé |
| `check_spec_protocol` | OK |
| **Sweep local complet** | **328 fichiers / 328**, zéro échec, sortie 0, pic 1 761 Mo (budget 1 846) |
| Scénario de l'opérateur rejoué | sur les **trois** builds — production, canonique, cette branche |
| Rendu exposé à l'opérateur | **avant le commit** |

⚠ **Le sweep complet, pas un filtre `-k`.** La tranche précédente avait été
poussée sur un filtre par mots-clés : 1 535 verts en local, deux shards rouges
en CI. Un filtre borne ce qu'on a pensé à *nommer*.
