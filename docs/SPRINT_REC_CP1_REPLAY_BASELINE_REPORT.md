# REC-CP1 — Harnais de rejeu déterministe et baseline V2

**Statut** : livré · **Branche** : `sb/rec-cp1-replay` · **Base canonique** : `2cdac58`

Ce sprint ne corrige rien. Il **construit l'instrument de mesure** et **établit
le baseline** contre lequel un candidat V3 sera comparé, puis répond à la
question que l'opérateur a posée au `§6` : le blocage `P1` vient-il du
**départage** (`A`), du **classement primaire** (`B`), ou des **deux** (`C`) ?

**Réponse : `C`, et dans un ordre qui change ce qu'il faut faire.**

---

## 1. Pourquoi ce harnais pouvait enfin être écrit

Avant `REC-CP0a`, rejouer le moteur à une date passée était impossible sans
mentir : **aucune** des douze requêtes du chemin n'était bornée par la date de
décision. Une décision évaluée au 1ᵉʳ mars lisait les séances du 15 mars.

La correction se voit dans la conception du harnais : `rejouer()` **sème toute
la trajectoire d'un coup**, puis fait avancer `now`. C'est licite — et c'est en
soi un test de `REC-CP0a` : si une borne manquait, chaque décision verrait
l'historique entier et **toutes les décisions d'une trajectoire seraient
identiques**. Un harnais contraint de semer incrémentalement pour éviter la
fuite aurait masqué le défaut au lieu de le mesurer.

| Livrable | Fichier |
|---|---|
| Corpus + rejeu + agrégats | `scripts/reco_replay.py` |
| Gardes sémantiques + baseline | `tests/test_rec_cp1_replay.py` (14) |

Les séances sont posées à 18 h, les décisions prises à 12 h **le même jour** :
une décision au jour J voit les séances jusqu'à J−1 inclus et jamais celle de J
— ce que « je me demande quoi faire aujourd'hui » signifie réellement.

---

## 2. ⚠ Un défaut de mon corpus, trouvé avant de conclure

La première version faisait partir chaque trajectoire de zéro. Or
`recommend_next_session` **court-circuite entièrement le scoring** sous trois
séances et rend un repli (`core[0]`, score 50, zéro alternative).

Les trois premières décisions de chaque trajectoire étaient donc ce repli —
`push-a` partout, quelle que soit l'histoire — et j'ai failli lire cet artefact
comme un épinglage du produit. **C'était mon corpus qui produisait un état non
représentatif et le laissait dominer la mesure.**

Correction : un `ECHAUFFEMENT` de trois séances, semé mais **non mesuré**, posé
30 à 26 jours avant l'origine — donc hors des fenêtres 7 j et 14 j. Seule
`demarrage-a-froid` le garde vide : c'est l'état qu'elle observe.

Un second défaut du même genre a été attrapé par une garde : mon helper de test
rejouait toutes les trajectoires sur **le même utilisateur**, empilant les
historiques. Le CLI créait déjà un utilisateur neuf par trajectoire pour cette
raison exacte ; le test ne le faisait pas.

---

## 3. Le baseline V2 — `RUNTIME_MEASURED`

Reproductible par `pytest tests/test_rec_cp1_replay.py -s` (le CLI exige une
base migrée **et** un catalogue semé ; les fixtures fournissent les deux).

```
trajectoire             déc  srT   conc   égal  mMed gagnants
push-pull-push            5    5   1.00   0.00    20 liss-abs×5
push-pull-legs            6    6   1.00   0.00  20.0 liss-abs×6
push-lourd                5    5   1.00   0.00    20 liss-abs×5
pull-lourd                5    5   1.00   0.00    20 liss-abs×5
legs-lourd                5    5   1.00   0.00    20 liss-abs×5
equilibre                 9    9   1.00   0.00    20 liss-abs×9
meme-gabarit-repete       6    6   1.00   0.00  20.0 liss-abs×6
famille-ab                4    4   1.00   0.00  20.0 liss-abs×4
cardio-absent             5    5   1.00   0.00    20 liss-abs×5
cardio-recent             4    3   0.75   0.25  18.5 liss-abs×3, catch-up-shoulders×1
reprise-longue            4    4   1.00   0.00  18.5 liss-abs×4
substitutions             4    4   1.00   0.00  14.0 liss-abs×4
exercice-non-mappe        4    4   1.00   0.00  15.5 liss-abs×4
seance-exclue             4    4   1.00   0.00  20.0 liss-abs×4
demarrage-a-froid         2    2   1.00   0.00  None push-a×2
egalite-exacte            2    2   1.00   0.00  18.5 liss-abs×2
quasi-egalite             4    4   1.00   0.00  20.0 liss-abs×4
```

`conc` = part du gagnant le plus fréquent · `égal` = part des décisions où le
gagnant et son dauphin ont le **même** score · `mMed` = marge médiane.

**`liss-abs` gagne 100 % des décisions dans 15 trajectoires sur 17.**
`push-lourd`, `pull-lourd`, `legs-lourd` et `equilibre` rendent des séquences
**identiques**. Seule `cardio-recent` casse la série — et pour une décision.

Le blocage rapporté en dogfood est donc reproduit et chiffré.

---

### ⚠ 3bis. Ce que ce baseline NE mesure PAS — réserve à lever en `REC-CP2`

`semer_seance` ne pose que **les deux premiers exercices** de chaque gabarit.
Mesuré : `legs-a` compte **sept** exercices ; les cinq ignorés contiennent le
travail de `core` et de `calves`.

Conséquence, relevée sur le corpus :

```
exposition 14 j = biceps 4 · lats 6 · pecs 12 · posterior 6 · quads 6
                  triceps 4 · upper_back 6
```

**Sept zones sur onze.** `core`, `calves`, `delt_lat` et `delt_post` ne sont
**jamais** travaillées par le corpus. Or `liss-abs` a pour unique zone `core`,
et `catch-up-shoulders` a `delt_lat`/`delt_post` — ces gabarits sont donc
structurellement, et à jamais, « la zone la plus délaissée ».

Ce que cela n'affecte pas : le diagnostic. `dispo` est plate parce qu'elle
sature, pas à cause du corpus ; les deux mutations portent sur des constantes ;
et l'absence de lecteur pour la fenêtre 14 j est `CODE_TRACED`.

Ce que cela affecte : **toute politique qui classerait par couverture ne peut
pas être jugée sur ce corpus.** L'instrument doit d'abord semer des séances
complètes. C'est le premier travail de `REC-CP2`, et ce baseline sera
re-mesuré à cette occasion.

(Relevé au passage, sans l'interpréter : `liss-only` n'a **aucun** exercice au
catalogue, donc aucune zone. C'est un fait de catalogue, pas une conclusion.)

## 4. La réponse au `§6` — et deux attributions fausses de ma main

J'ai attribué la cause deux fois, et deux fois à tort. Les deux réfutations sont
consignées parce qu'elles sont la raison d'être du harnais.

### 4.1 « Le départage épingle » — réfuté par la mesure

`recommendation.py:864` trie par `(-score, display_order, slug)` alors que le
commentaire **et** la spec promettent `last_done_at`. C'est un écart réel entre
contrat et code. J'en ai conclu que c'était la cause.

Le corpus dit **0 % d'égalités** et une marge médiane de **20 points**. Le
gagnant n'est pas départagé : il gagne largement. Corriger ce tri ne changerait
rien.

### 4.2 « Le bonus cardio-absent domine » — réfuté par mutation

`MUTATION`, appliquée seule puis annulée : `score += 10` → `score += 0`.
Résultat : **aucun changement**. `liss-abs` tombe de 90 à 80 et reste devant 70
et 65.

### 4.3 La décomposition, qui tranche là où deviner échouait

Six composantes de `_score_template` additionnées à la main sur l'état réel
(trajectoire push-lourde) :

```
gabarit                  tot  dispo  frai  alt   red  aff  car
liss-abs                90.0   35.0    15   20   0.0   10   10
catch-up-shoulders      70.0   35.0    15    0   0.0   20    0
pull-a / pull-b         65.0   35.0    15    0   0.0   15    0
legs-a / legs-b         65.0   35.0    15    0   0.0   15    0
push-a / push-b         59.0   35.0     9    0   0.0   15    0
```

Deux faits, ni l'un ni l'autre n'étant mon hypothèse :

1. **`dispo` — la plus grosse composante du moteur, 35 points — rend la même
   valeur pour tous les candidats.** Elle ne discrimine rien.
2. Le seul discriminant longitudinal est la fraîcheur de zone, au pas de **6
   points**, contre **25 points** d'écart de catégorie.

Le signal de trajectoire **fonctionne** : push-lourd démote bien `push-*` (59
contre 65). Il est d'un ordre de grandeur trop petit pour être visible.

### 4.4 Les deux causes sont empilées

`MUTATION`, appliquée seule puis annulée : `WEIGHT_ALTERNATION` → 0.

| Moteur | Gagnant | Égalités |
|---|---|---|
| intact | `liss-abs` partout | **0 %** |
| bonus cardio à 0 | `liss-abs` partout | 0 % |
| **alternance à 0** | `liss-abs` partout | **72 %** |

Retirer l'alternance ne change pas le gagnant, mais le classement s'effondre en
un peloton à égalité que `display_order` puis `slug` tranchent dans **72 %** des
décisions.

> **`A` est réel mais inactif, masqué par `B`. `B` est ce qui décide
> aujourd'hui.** Ne corriger que `A` ne changerait rien. Ne corriger que `B`
> découvrirait un moteur épinglé par l'ordre du catalogue à 72 %.

Ceci respecte la consigne du `§6` dans ses deux sens : on ne redessine pas tout
le scoring si le départage suffisait — il ne suffit pas, c'est mesuré ; et on
n'appellera pas « V3 » un correctif de départage qui laisserait le classement
primaire ignorer l'évidence longitudinale.

**La condition dominante mérite d'être nommée** : `kinds_recent[:2] ==
["strength", "strength"]` est vraie en permanence pour quiconque s'entraîne en
force. Le bonus d'alternance n'est donc pas un correctif ponctuel de
déséquilibre, c'est **un supplément constant accordé au cardio**.

---

## 5. Les gardes — chacune prouvée capable d'échouer

14 gardes. Les quatre qui portent le diagnostic ont été vérifiées par mutation.

| Garde | Mutation | Verdict |
|---|---|---|
| `…le_classement_ne_discrimine_presque_pas…` | `AFFINITY_CORE` 15 → 35 | 🔴 attrapée (5 pts > 6 pts faux) |
| `…une_seance_exclue_ne_pese_sur_aucune_decision` | filtre `excluded_from_stats` retiré du tonnage | 🔴 attrapée |
| `…le_departage_ne_tranche_rien_aujourd_hui` | `WEIGHT_ALTERNATION` → 0 | 🔴 attrapée (72 % > 15 %) |
| `…le_baseline_v2_est_reproductible` | idem ci-dessus | 🔴 attrapée |

### ⚠ Une garde qui ne gardait rien, corrigée

`test_une_seance_exclue_ne_pese_sur_aucune_decision` comparait d'abord les
**gagnants**. Or `liss-abs` gagne toutes les décisions du corpus : deux
historiques différents rendaient le même gagnant quoi qu'il arrive.

La mutation le prouve noir sur blanc — avec le filtre d'exclusion retiré, la
divergence observée est :

```
jour 4 : ('liss-abs', 90, pecs=12, triceps=4)   vs   ('liss-abs', 90, pecs=6, triceps=2)
```

**Gagnant identique, score identique** — seule l'exposition diverge. La garde
porte désormais sur `(gagnant, score, exposition 14 j)` et refuse de s'exécuter
si la fenêtre d'exposition n'est pas peuplée.

### Propriétés sémantiques épinglées (`§3`)

`SAME_HISTORY => SAME_RECOMMENDATION` · séance exclue inerte · répétition
légitime **possible** (le pendant de `REPEAT_REQUIRES_EVIDENCE` : interdire la
répétition serait aussi faux que l'imposer) · long arrêt visible dans les
signaux · exercice illisible ⇒ observation partielle · aucun agrégat fabriqué
sur corpus vide · semeur unique partagé entre CLI et tests.

**Aucun seuil d'entraînement inventé.** Le corpus n'encode aucune réponse
idéale : il n'existe pas de vérité universelle disant que push → pull → push
impose legs.

---

## 6. Pourquoi le classement ignore la trajectoire — `CODE_TRACED`

La décomposition dit *que* le signal longitudinal est trop petit. Le relevé des
consommateurs dit **pourquoi**.

Le moteur calcule **trois** horizons d'exposition par zone. Voici qui les lit :

| Signal | Horizon | Consommateur |
|---|---|---|
| `hard_sets_by_zone_24h` | 24 h | filtre de redondance + pénalité de score |
| `hard_sets_by_zone_recent` | **7 j** | **aucun** — construit, assigné, jamais lu |
| `hard_sets_14d_by_zone` | **14 j** | `_is_specialization_justified` **uniquement** |

`median_hard_sets_14d` suit le même sort : un seul lecteur, la même fonction.
Et `_is_specialization_justified` rend un **booléen** qui ne concerne que les
gabarits `specialization` — il ne touche jamais le score d'un `push-*`,
`pull-*` ou `legs-*`.

Le seul apport longitudinal au classement des six gabarits du noyau est donc
`_zone_freshness_bonus`, qui regarde les **trois dernières séances de force** —
soit environ six jours.

> **Le moteur mesure la couverture sur deux semaines et ne s'en sert pas pour
> classer.** Une zone sous-travaillée depuis douze jours pèse exactement zéro
> dans le score d'un gabarit du noyau.

C'est l'énoncé précis de `B`. Il est meilleur que « le classement est
insensible » : le classement n'est pas aveugle, il regarde une fenêtre de trois
séances et **ignore la fenêtre de quatorze jours qu'il a déjà calculée**.

⚠ `14 jours est un horizon de MÉMOIRE, pas une vérité physiologique` (`§8`).
Le rendre lisible par le classement n'autorise pas à en faire un seuil
biologique.

## 7. Ce que `REC-CP2` doit traiter, dans cet ordre

1. **Le classement primaire** — `dispo` (35 pts) doit discriminer, ou céder son
   poids à ce qui discrimine. L'écart de catégorie ne doit plus valoir quatre
   fois l'évidence longitudinale.
2. **Le départage, ensuite et obligatoirement** — ancienneté du dernier passage
   avant famille, puis ordre de catalogue déterministe. Sans aléatoire. Sinon le
   correctif du point 1 découvre un épinglage à 72 %.
3. **Les bonus catégoriels permanents** — `alternance` et `cardio absent`
   s'accordent sur des conditions vraies en permanence. Les rendre décroissants
   ou conditionnels à une preuve.

Les constantes de récupération 24/36/48/72 h restent classées **heuristiques**,
pas faits biologiques. 14 jours reste un horizon d'**observation**.

La comparaison V2 vs V3 se fera sur **ce corpus**, avec ces agrégats. La variété
ne sera pas retenue comme preuve de justesse.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---

## Closeout

| | |
|---|---|
| PR | [#245](https://github.com/MFE-DSS/workout-session-tracking/pull/245) |
| Merge | `abb362574cab9909c57ac2f63f120e8d1c232a3c` |
| CI canonique | run `35982648659` — **7/7 verte** |
| Sonar (PR) | gate `OK` — 0 bug, 0 code smell, 0 vulnérabilité, 0 % duplication |
| Sweep local | 337/337 fichiers, `tous les lots sont verts.` |
| Threads de revue | 0 |

Aucun fichier applicatif modifié : la tranche n'ajoute qu'un harnais, des
gardes et ce rapport. Les deux mutations citées au `§4` ont été appliquées
**seule à seule** puis annulées, et l'arbre a été vérifié propre avant commit.

### Ce que cette tranche a appris, au-delà de son objet

Deux fois, la cause du défaut a été attribuée à tort — puis réfutée par une
mesure et non par un raisonnement. Le harnais existe précisément pour rendre
cette réfutation possible avant qu'une correction ne soit écrite.

Et deux défauts appartenaient à l'instrument, pas au produit : un corpus qui
partait de zéro mesurait le repli de démarrage à froid ; un helper de test
empilait toutes les trajectoires sur le même utilisateur. La réserve du `§3bis`
en signale un troisième, corrigé en `REC-CP2`.

### Suite

`REC-CP2` ([#246](https://github.com/MFE-DSS/workout-session-tracking/pull/246))
corrige l'instrument, construit la politique V3 **en ombre** et re-mesure. Il
révise le diagnostic de ce rapport sur un point important : en boucle fermée,
V2 ne se bloque pas.
