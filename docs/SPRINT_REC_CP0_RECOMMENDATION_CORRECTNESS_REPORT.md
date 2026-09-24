# `REC-CP0` — correction du moteur de recommandation

> **Le défaut rapporté en dogfood** : *la recommandation reste bloquée sur le
> même type de séance au lieu de refléter la trajectoire récente.*
>
> **La directive interdisait d'y répondre en réglant des constantes.** Elle
> avait raison : **aucun** des quatre mécanismes trouvés n'est un problème de
> poids.

---

## 0. Ce que l'audit a établi, avant toute modification

Quatre mécanismes distincts, tous `CODE_TRACED`, poussant tous dans le même
sens — que le moteur ne réagisse pas à la trajectoire récente.

| | Mécanisme | Tranche |
|---|---|---|
| **P4** | aucune requête bornée par la date de décision → tout rejeu lit le futur | **`CP0a`** |
| **P2** | « pas su lire » rend la fraîcheur **maximale** sur la composante à 35 pts | **`CP0b`** |
| **P3** | deux ontologies de zones **dans la même fonction** | **`CP0b`** |
| **P1** | départage par ordre de catalogue, jamais par récence | `CP1` chiffre, `CP2` corrige |

---

## 1. `CP0a` — `HISTORY_IS_CAUSAL`

### Le défaut

`recommend_next_session` accepte un `now`, et
`scripts/reco_calibration_report.py` s'en sert pour **rejouer** le moteur à des
horodatages passés. Or **zéro** des douze requêtes du chemin ne portait de borne
supérieure sur `started_at`.

Une décision évaluée au 1<sup>er</sup> mars lisait les séances du 15 mars.

⚠ **Les chiffres de calibration produits jusqu'ici décrivent un moteur qui
trichait.** C'est une conséquence, pas une précaution : ils ne peuvent pas
servir de base de comparaison à `CP1`.

### Pourquoi personne ne l'avait vu

Deux masques, et les deux comptent :

* `max(0, (now - started).days)` écrasait les deltas négatifs à zéro — une
  séance du futur se lisait « aujourd'hui » au lieu de se signaler ;
* le court-circuit « séance ouverte » n'avait **aucune** borne *et* s'exécutait
  avant que `now` soit résolu. Une séance ouverte aujourd'hui faisait rendre
  `None` à **tous** les horodatages rejoués : l'échantillon se vidait en
  silence, ce qui est plus difficile à remarquer qu'un résultat faux.

### Les six corrections

| Correctif | Fichier |
|---|---|
| `_compute_tonnage_by_zone(…, until=)` — les trois fenêtres 7 j / 24 h / 14 j | `muscle_scoring.py` |
| 5 dernières séances bornées | `recommendation.py` |
| fenêtre force récente bornée | `recommendation.py` |
| `compute_behavioral_state(…, now=)` — **elle n'avait aucun paramètre de temps** | `behavioral.py` |
| court-circuit séance ouverte borné | `recommendation.py` |
| démarrage à froid filtre `excluded_from_stats` | `recommendation.py` |

La convention de borne est celle de `weekly_loop._load_window_sessions` —
`>= début`, `< fin` — **le seul chemin du dépôt qui était déjà correct**. Copiée
plutôt que réinventée.

`TEST_PROVEN` : **6 mutations sur 6 mordent**, chacune replantant le défaut
d'origine.

---

## 2. `CP0b` — `ZONE_ONTOLOGY_IS_COHERENT` et `UNKNOWN_DOES_NOT_MEAN_AVAILABLE`

### Deux ontologies dans la même fonction

Les signaux de tonnage passaient par `resolve_exercise_zones` — corrections
relues, puis base, puis sous-chaîne. Les zones de gabarit, la carte du dernier
travail et la disponibilité passaient par `classify_exercise(name)`,
**sous-chaîne pure**.

Trois exercices du catalogue divergent de façon prouvée :

| Exercice | mesure | recommandation |
|---|---|---|
| `Calf press leg press` | `calves` | **`quads`** |
| `Rear delt fly machine (pec deck inversé)` | `delt_post` | **`pecs`** |
| `Relevé de jambes suspendu` | `core` | **`calves`** |

Le produit mesurait l'entraînement avec une ontologie et décidait la séance
suivante avec une autre.

### Le choix d'autorité est MESURÉ, pas espéré

Le moteur résout désormais ses zones **sans base** (`db=None`), parce que son
cache est indexé par tuple de noms. Ce choix n'est légitime que si les deux
chemins s'accordent. `RUNTIME_MEASURED` via `build_parity_report`, sur les
**102 exercices du catalogue** :

```
exact_matches             99
intentional_divergences    3   (exactement les trois corrections relues)
unexplained_divergences    0
missing_formal_mapping     0
ambiguous_mappings         0

resolve(db, …) vs resolve(None, …)   →   0 divergent sur 102
```

⚠ C'est un fait **daté**, pas une propriété. L'audit qui l'a précédé affirmait
« 68 mappés, zéro conflit » et était devenu faux sans que personne le voie. La
mesure est donc devenue une **garde qui tourne à chaque exécution** sur le
catalogue réel.

### « Inconnu » cessait d'être une ignorance

Une zone sans trace recevait `availability = 1.0` — fraîcheur **maximale** —
que la zone n'ait jamais été travaillée **ou** que le moteur n'ait pas su lire
l'exercice qui l'a travaillée. `WEIGHT_AVAILABILITY = 35` en fait la plus
grosse composante du score.

Un gabarit dont les zones échouent au classement marquait donc le maximum à
**chaque** décision. Ce n'est pas une imprécision : **c'est un mécanisme
d'épinglage.** La substitution en texte libre en est la source vivante —
`sessions.py` accepte un nom arbitraire que le matcher ignore.

**Le moteur connaissait déjà la bonne réponse.** Vingt lignes plus bas,
`_score_template` écrit :

```python
availability = 0.5  # inconnu → neutre
```

…quand un gabarit n'a aucune zone. La décision existait ; le moyen de
l'appliquer de l'autre côté n'existait pas. Aucune valeur nouvelle n'a été
inventée : la sienne a été **nommée** (`AVAILABILITY_INCONNUE`) et appliquée aux
deux moitiés du même problème.

La sémantique est celle de `zone_exposure` — une observation partielle ne
produit pas un zéro, elle produit une ignorance déclarée. **Pas un second
système de confiance.**

`TEST_PROVEN` : 2 mutations sur 2 mordent.

---

## 3. Levée de gel — arbitrage, pas initiative

`recommendation.py` était déclaré **non modifiable** par
`Sx_AUREN_ORCHESTRATOR_01_GAP_CONSOLIDATION_SPEC §6, §P0.2` et
`AUREN_UI_BLUEPRINT §queue`. La spec exigeait : *« STOP : si la correction exige
de toucher `recommendation.py` → STOP + arbitrage. »*

La directive de passe critique du 2026-09-23 **est** cet arbitrage : *« Fix the
root boundary if violated. Do not merely patch the reporting script. »*

Le motif « wrapper externe » ne pouvait pas corriger ceci : **une fuite de
causalité vit dans les requêtes, pas à la frontière.**

Le gel par diff est remplacé par une **garde d'API**, patron exact de
l'amendement `D6` de `behavioral.py` — dont la docstring disait déjà : *« un gel
qui empêche de nettoyer une arme chargée protège mal. »*

`substitution.py` **reste gelé**. L'interdiction reste **entière pour la queue
UI** : la levée vaut pour une tranche de **moteur**, pas de présentation.

---

## 4. Trois gardes du dépôt m'ont arrêté — et les trois avaient raison

| Garde | Ce qu'elle a exigé |
|---|---|
| gel par diff (`test_no_decision_engine_was_touched`) | déclarer l'arbitrage avant de toucher le moteur |
| garde d'API (`Signals`) | déclarer le champ `observation_partielle` au lieu de l'ajouter en silence |
| registre des consommateurs (`test_only_the_authorised_consumer_reads_the_formal_contract`) | déclarer la migration d'ontologie comme **décision revue** |

La troisième a révélé autre chose : `recommendation.py` figurait dans la liste
des consommateurs **interdits**, alors que sa moitié tonnage lisait le contrat
formel depuis `Sb_32.4`. **Le registre décrivait un fichier qui n'existait
plus** — la coupure en deux ontologies y était inscrite, non lue.

---

## 5. Deux de mes propres instruments ont menti

Consignés parce qu'ils sont la même classe d'erreur que celles que ces tranches
corrigent : **mesurer le mauvais objet**.

**La garde causale n'observait que la sortie.** Elle ne mordait que sur 2 bornes
sur 6. Diagnostic en instrumentant les signaux, pas en devinant :

```
days_since_last_strength      2  →  -3
availability_by_zone[pecs]   1.0 →  0.0
hard_sets_by_zone_24h         {} →  {pecs: 12, triceps: 4}
last_strength_session_zones  ['quads'] → ['pecs']
```

Les **entrées** changent massivement ; **le gagnant ne bouge pas**.

⚠ **C'est une seconde information, et elle vaut plus que la première** : le
moteur est à ce point épinglé qu'un bouleversement complet de ses entrées ne
déplace pas sa sortie. C'est la preuve la plus directe du défaut **P1**, et
c'est exactement ce que l'opérateur observe en séance.

La sixième mutation résistait encore parce que **toutes les séances du corpus
avaient le même ressenti** — `_mk_session` pose `good`/`high` par défaut, donc
la fatigue était identique quelles que soient les séances lues.

**Le compteur de findings ruff classait un fichier NEUF en « pré-existant ».**
Il dérivait les lignes ajoutées de `git diff -U0 -- <fichier>`, qui ne rend rien
pour un fichier non suivi. Il a rendu « 0 finding sur mes lignes » alors qu'un
`F541` MAJOR attendait — gate Sonar rouge. Corrigé : un fichier neuf a **toutes**
ses lignes ajoutées.

---

## 6. Ce que `REC-CP0` ne fait PAS

* **Aucun changement de politique de décision.** La correction porte sur ce que
  le moteur a le droit de **lire**, pas sur la façon dont il **décide**.
* **Aucune constante de récupération touchée** (24/36/48/72 h).
* **Aucun seuil inventé.**
* **Aucune migration**, aucun changement de modèle.

L'écart comportemental réel sera **mesuré** par `REC-CP1` sur un corpus de
rejeu, moteur actuel contre candidat V3. La variété n'est pas la justesse.

---

## 7. Vérifications

| Contrôle | `CP0a` | `CP0b` |
|---|---|---|
| `check_scope` | `SHARED_CODE` | `SHARED_CODE` |
| sweep local complet, arbre **gelé** | **`tous les lots sont verts.`** | **`tous les lots sont verts.`** |
| mutations des gardes neuves | **6/6** | **2/2** + API 1/1 |
| budget ruff | 267 → **265** | **265** |
| `check_spec_protocol` | vert | vert |
| couverture du code neuf (Sonar) | **100 %** | **100 %** |

---

## AVENANT POST-MERGE — closeout

| | `CP0a` | `CP0b` |
|---|---|---|
| PR | **#243** | **#244** |
| SHA de tête épinglé | `92283b8` | `75b2ab8` |
| commit de merge | **`a90bad6`** | **`6080559`** |
| CI canonique | **7/7 success** | **7/7 success** |
| gate Sonar (API) | **`OK`** 5/5 | **`OK`** 5/5 |
| threads non résolus | 0 | 0 |

Méthode `--merge`, SHA de tête épinglé, aucun squash, aucun `--admin`, aucun
force. Branches et worktrees supprimés après preuve qu'ils ne contenaient ni
commit unique ni fichier non suivi.

### L'incident Sonar de `CP0a`, et ce qu'il a révélé de mon instrument

Gate rouge au premier passage : `new_code_smells_severity = 15` pour un seuil
de 14. L'arithmétique désignait **une** finding MAJOR — `external_ruff:F541`,
une f-string sans placeholder, dans le fichier de test que je venais d'écrire.

⚠ **J'avais pourtant vérifié.** Mon outil croisait chaque finding avec les
lignes ajoutées par le diff et avait rendu « 0 finding sur mes lignes ». Il
dérivait ces lignes de `git diff -U0 -- <fichier>` — qui **ne rend rien pour un
fichier non suivi**. L'ensemble des lignes ajoutées était donc vide, et toutes
les findings d'un fichier neuf tombaient dans « pré-existant ».

C'est exactement la classe d'erreur que cet outil existe pour prévenir :
**mesurer le mauvais objet**. Corrigé — un fichier neuf a **toutes** ses lignes
ajoutées — et revérifié sur les deux worktrees avant `CP0b`, qui a passé le
gate du premier coup.

### Ce que `REC-CP0` laisse à la suite

* **`P1` — l'épinglage par ordre de catalogue — n'est pas corrigé.** Il est
  diagnostiqué, et sa preuve la plus directe est consignée au `§5` : les
  entrées du moteur peuvent basculer complètement sans que sa sortie bouge.
  `REC-CP1` doit le chiffrer, `REC-CP2` le corriger.
* **Les chiffres de calibration antérieurs sont invalides** — ils décrivent un
  moteur qui lisait le futur. `REC-CP1` doit produire sa propre base.
* **Aucun écart comportemental n'est revendiqué** par `REC-CP0` : la correction
  porte sur ce que le moteur a le droit de lire, pas sur sa façon de décider.

**Déploiement en production : non fait.** Décision séparée.
