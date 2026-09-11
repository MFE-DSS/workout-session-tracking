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
| **Sweep local complet** | ⛔ **ce chiffre était faux — voir §9** |
| Scénario de l'opérateur rejoué | sur les **trois** builds — production, canonique, cette branche |
| Rendu exposé à l'opérateur | **avant le commit** |

⚠ **Le sweep complet, pas un filtre `-k`.** La tranche précédente avait été
poussée sur un filtre par mots-clés : 1 535 verts en local, deux shards rouges
en CI. Un filtre borne ce qu'on a pensé à *nommer*.

⚠⚠ Et ça n'a pas suffi : j'avais corrigé l'OUTIL en gardant le GESTE — filtrer
la sortie avant de la lire. Voir **§9**.

---

## 8. Six gardes de plus, et pourquoi elles avaient échappé au relevé

La CI a rendu **six échecs** sur les shards 1 et 2. Ils échouaient **aussi en
local** — donc ce n'était pas un aléa d'infrastructure, mais une part du
travail que je n'avais pas faite.

Toutes appartiennent à la classe déjà traitée au §6 : elles décrivent
l'échauffement-porte. Aucune n'a été supprimée sans remplaçante nommée, dans le
même fichier et la même livraison.

### Deux gardes converties — la propriété change parce que le produit change

| Supersédée | Remplaçante | Ce qui est gagné |
|---|---|---|
| `test_pending_warmup_wins_over_everything` (`test_uiv3_session_console`) | `test_pending_warmup_wins_only_when_it_IS_the_work` | tenait **exactement** le défaut vécu. La remplaçante garde la souveraineté là où elle a un sens **et** vérifie qu'elle est perdue dès qu'il y a du travail |
| `test_skipping_the_warmup_moves_the_instrument_to_the_work_set` (`test_ui_command_intelligibility`) | `test_the_instrument_opens_on_the_work_set_with_no_parameter_at_all` | exigeait qu'un paramètre ait un effet. La remplaçante exige qu'**aucun paramètre ne soit nécessaire**, et rejoue le **rechargement** — le geste exact de la plainte |

### Une garde recentrée — le risque est intact, son porteur a changé

`test_the_skip_is_a_link_not_a_submission` protégeait une chose réelle : un
`<button type="submit">` à l'emplacement de l'échauffement soumettrait la carte
entière, et `_persist_set_values` écrirait alors les séries que porte le DOM.
Le bouton de saut a disparu ; **le tiroir d'échauffement occupe désormais cette
place**. `test_the_warmup_drawer_carries_no_submit_control` y porte le même
invariant — le tiroir reste saisissable, il ne devient jamais une commande.

### Trois montages réparés — la propriété était juste, le cas ne l'atteignait plus

`_exercise()` ne rend plus `WARMUP`. Trois gardes l'utilisaient comme cas
d'échauffement et observaient en réalité un état de travail :

* `test_the_dominant_command_says_the_type_in_words` — comparait deux fois la
  même commande ;
* `test_warmup_and_correction_do_not_start_a_rest` — la propriété (aucun repos
  après un échauffement) est inchangée, seul le montage l'atteint encore ;
* `test_exactly_one_dominant_command_per_state` — voir ci-dessous, la ligne
  d'échauffement a révélé un défaut de libellé.

### ⚠ Deux gardes VERTES qui ne mesuraient plus rien

Elles n'étaient pas dans les six, et c'est ce qui les rend intéressantes.

* `test_skipping_the_warmup_writes_nothing` interrogeait `?skipwarm=1` — un
  paramètre supprimé. Un paramètre inconnu est ignoré : la garde rendait vert
  **par construction**. Recentrée en
  `test_traversing_the_exercise_writes_no_warmup`, elle tient l'enjeu réel de
  `Q-C`, aujourd'hui **plus exposé** qu'avant puisque l'utilisateur traverse
  l'exercice sans jamais toucher le tiroir ;
* `_warmup_state_stub` annonçait « état minimal en `WARMUP` » et montait
  `[warmup, work]` — donc un état de travail. Corrigé.

C'est la forme la plus silencieuse de garde qui ne garde rien : elle ne casse
pas quand on retire ce qu'elle observait.

### 🐞 Un défaut de produit trouvé en réparant un montage

En construisant le seul cas d'échauffement qui subsiste, la commande dominante
s'est révélée dire **« PASSER AUX SÉRIES »** — vers des séries qui, dans cet
état, **n'existent pas** : `WARMUP` n'est atteint que par un exercice sans
aucune série de travail.

C'est le défaut `F1` de `UI-CP2.0`, corrigé côté ÉTAT et **laissé intact côté
LIBELLÉ**. Il dit désormais **« EXERCICE TERMINÉ »**, le mot que `CURRENT_SET`
emploie déjà pour la dernière série de travail — aucun vocabulaire n'est
inventé.

⚠ **Portée réelle, mesurée** : sur le catalogue semé, **0 exercice de gabarit
sur 98** n'a aucune cible de répétitions, et **aucune séance existante** ne
porte un exercice sans série de travail. `WARMUP` est donc structurellement
atteignable et **empiriquement inatteint** — le libellé corrigé n'est visible
par personne aujourd'hui. Il est corrigé parce qu'un état gardé doit être
juste, pas parce qu'un utilisateur le verrait. Dit ici pour que la correction
ne soit pas lue comme un changement d'écran.

---

## 9. ⛔ Mon rapport de sweep du §7 était FAUX

J'ai écrit **« 328 fichiers / 328, zéro échec, sortie 0 »**. Le sweep avait en
réalité **détecté les six échecs et terminé en sortie 1**.

La commande était :

```
bash scripts/run_local_sweep.sh 2>&1 | grep -E "…" | tail -20
```

Trois défauts en une ligne, et ils se couvrent l'un l'autre :

1. **le motif `grep` ne pouvait pas voir la ligne d'échec.** Le script imprime
   `NUMÉROS DES LOTS EN ÉCHEC : …` ; mon motif cherchait `lot .* · (ok|ECHEC)`,
   avec un `·` que cette ligne ne porte pas. J'avais écrit un filtre qui
   laissait passer les bonnes nouvelles et retenait la seule mauvaise ;
2. **`tail -20` a jeté les lots 1 à 105**, donc le lot en échec lui-même ;
3. **le code de sortie lu était celui de `tail`**, pas du script. Un pipeline
   rend le statut de sa dernière commande, et `tail` réussit toujours. « exited
   with code 0 » était le verdict de `tail`.

**Le signal était pourtant là et je l'ai rationalisé** : la ligne de conclusion
`tous les lots sont verts.` était **absente** de la sortie. Je l'ai remarquée
et attribuée au filtre.

**La règle qui en sort** : un rapport vert exige la **présence de la phrase de
succès**, jamais l'absence de phrases d'échec — c'est la seule forme qui
résiste à un filtre mal écrit. Une vérification requise ne se filtre pas avant
d'avoir été lue.

C'est la **sixième** forme de « mesurer le mauvais objet » consignée sur ce
dépôt, et la deuxième en deux jours. La cinquième — un filtre `-k` pris pour un
sweep — avait produit la CI rouge de la tranche précédente. J'avais corrigé
l'outil et gardé le geste : filtrer avant de lire.

### Sweep refait

| Contrôle | Résultat |
|---|---|
| commande | `bash /chemin/absolu/scripts/run_local_sweep.sh > fichier 2>&1` — **aucun pipe** |
| chemin | **absolu**, parce que le script fait `cd` vers l'arbre du SCRIPT (l. 50) : en chemin relatif depuis la canonique, il balaie la canonique |
| **verdict** | **`[local-sweep] tous les lots sont verts.`** — la phrase de succès, lue dans le journal (l. 433) |
| lots | **124 / 124**, `328/328 fichiers`, `Aucun fichier sauté — les lots réduits ont été rejoués` |
| lignes `FAILED` / `ERROR` | **0** sur le journal entier (`grep -c`, pas `tail`) |
| pic mémoire | 1 745 Mo (budget 1 937) |
| sortie | **0, du script lui-même** — aucun pipe pour la falsifier |
