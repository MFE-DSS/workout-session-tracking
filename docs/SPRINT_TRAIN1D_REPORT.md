# `TRAIN1-D` — Convergence épistémique

**Canonique de départ** : `308b0da` · **Tier `check_scope`** : `SHARED_CODE`
**Arbitrages exécutés** : C1 · C2 · C3 · C5 · C10

---

## 1. Brainstorming / Options / Risques / Choix retenu (`CLAUDE.md §3`)

### Ce que le relevé avait établi, et qui cadre la tranche

`/coach-report` rendait **369 mots sur un compte peuplé et 349 sur un compte
sans une seule séance** — une surface qui ne varie pas avec les données, le
symptôme exact qui a condamné `/physique`. Et elle était plus prescriptive que
Physique ne l'a jamais été : cinq consignes chiffrées, dont une **cible OMS**.

### La difficulté propre à cette tranche

Physique se retirait. Le Coach Report **ne se retire pas** : il a une intention
distincte, écrite dans son chapeau — « à présenter à un coach externe » — et un
bouton Imprimer. Un document destiné à un tiers a des raisons d'exister qu'un
cockpit quotidien n'a pas.

L'arbitrage opérateur tranche : **document, pas destination**. Il fallait donc
distinguer, à l'intérieur d'un même écran, ce qui relevait de sa nature de
document (les inférences, les références) de ce qui n'avait de place nulle part
(les prescriptions).

| Option | Verdict |
|---|---|
| Retirer la surface comme `/physique` | ✗ détruit une intention légitime |
| La laisser et retirer seulement la cible OMS | ✗ quatre autres prescriptions restaient |
| **Requalifier** : document utilitaire, prescriptions retirées, provenance renforcée | ✓ **retenue** |

### Le risque, et sa mitigation

« Move to Export/utility access » supposait que cet accès existe. **Il
n'existait pas** : `/export` n'était liée depuis **aucun gabarit** du dépôt —
route vivante, surface inatteignable autrement qu'en tapant l'URL. Déplacer le
document là l'aurait envoyé dans un cul-de-sac. La destination a donc été
rendue réelle dans la même livraison.

---

## 2. Ce que la tranche livre

### C1 — Le Coach Report devient un document

| Avant | Après |
|---|---|
| onglet **Progression** actif | **aucun onglet primaire** — classe des utilitaires, comme `/export` |
| atteignable depuis la nav Progression | menu utilitaire + **bloc dédié sur `/export`** |
| « Axes de travail suggérés » : jusqu'à 3 consignes chiffrées | **bloc retiré** → « 9. Couverture des données » |
| « cible OMS 150'/sem » à côté du volume réel | **référence attribuée**, détachée du cas personnel |
| « Zones négligées » | « Zones les moins travaillées » |
| `**Dos épaisseur**` rendu littéralement | corrigé, et `\|safe` retiré avec |

**Les cinq prescriptions retirées** et leur sort :

| Consigne | Décision |
|---|---|
| « Rééquilibrer X : viser 2 séances/sem sur 4 semaines » | retirée — le fait vit au bloc 4 |
| « Augmenter le volume cardio — cible OMS 150'/sem » | **référence** au bloc « Références externes » |
| « Diversifier les patterns moteurs » | retirée — le fait vit au bloc 5 |
| « Augmenter la fréquence : viser 2-3 séances/sem » | retirée — le fait vit au bloc 2 |
| « Logger le poids de corps — indispensable pour… » | **convertie en couverture** : « Poids de corps : renseigné sur 0 % des séances » |

`CLAUDE.md §5.3` — **aucune soustraction seule** : les faits sur lesquels ces
consignes reposaient sont tous restés à l'écran, et un bloc neuf (la
couverture) arrive dans la même livraison.

### C2 — Le Profil

Six `—` à l'échelle d'une valeur → **zéro**. La règle appliquée n'est pas celle
de Progression, et la différence est décisive : là-bas un dénominateur absent
est un fait sur lequel personne ne peut agir, donc la carte disparaît ; ici la
donnée manque parce que personne ne l'a saisie, et la saisie est à un clic.
L'état vide porte donc **l'action** — cinq affordances « Ajouter », une
« À compléter ».

- « Morphologie **0 / 13 mesures** » → « **À compléter** ». Un dénominateur
  posé comme un score à remplir, dans un produit qui vient de retirer les
  scores.
- La **configuration d'entraînement quitte le niveau 1** — et reste éditable :
  `weekly_planner` et `user_programs` consomment ses trois valeurs. Retirer la
  lecture sans garder l'écriture aurait rendu les entrées du planificateur
  inatteignables. `TRAIN2` lui donne son domicile.
- **Aucun champ sans consommateur ne subsistait au niveau 1** : l'audit a
  vérifié `height_cm`, `resting_hr`, le poids et les champs de compte, tous
  lus par au moins un service. La règle a sélectionné exactement le bloc que
  l'ordre nommait.

### C3 — Le modèle épistémique canonique

`app/services/epistemic.py` — **deux axes déclarés orthogonaux** :

```
NATURE     MEASURED · DERIVED · INFERRED · NOT_DEDUCIBLE
COVERAGE   COMPLETE · PARTIAL · UNKNOWN
```

**`DERIVED` est neuf, et il corrige une imprécision de fond.** Les blocs 2, 4 et
6 du rapport s'annonçaient « Mesuré » alors que ce sont des **comptages** :
exacts, reproductibles, et malgré tout des dérivations. Les appeler mesures
faisait passer une convention de comptage — *qu'est-ce qu'une séance qui
compte ?* — pour une observation brute. Les blocs 3 et 5 s'annonçaient
« Inféré » alors qu'un ratio ne suppose rien : eux aussi sont **calculés**.

`COVERAGE` traduit les états historiques de `zone_exposure`. **`zero` devient
`COMPLETE`** : « des séances existent, aucune n'a touché les onze zones » est
une observation entière dont la valeur est nulle. Un état non reconnu dégrade
vers `UNKNOWN`, **jamais** vers `COMPLETE` — arrondir une ignorance vers le
haut fabriquerait le mensonge que ces deux axes existent pour empêcher.

**On ne badge pas tout** (`OPERATOR_DECISION`). Le niveau 1 de Progression ne
porte aucune pastille, et une garde le vérifie. Le badge est réservé aux
surfaces qui assemblent des natures différentes dans un même document —
aujourd'hui le seul Coach Report, qui gagne enfin **la légende** disant ce que
ses étiquettes signifient : il en portait depuis `Sb_23` sans jamais l'écrire,
dans un document destiné à un tiers.

### C5 — Science

Les ancres `#rule-<slug>` existaient déjà — **invisibles**. Rien à l'écran ne
disait qu'une règle a un identifiant, ni lequel ; `/progress` pointait déjà
vers `#rule-plages-repetitions` sans que le lecteur, une fois arrivé, sache où
il avait atterri.

- l'identifiant est **rendu et cliquable** sur chacune des sept règles ;
- la règle visée **s'annonce** à l'arrivée (`:target`) ;
- **liens profonds contextuels** : bloc 6 du rapport → `#rule-carnet-progression`,
  garde-fous → `#section-method` ;
- une garde **épingle les sept slugs** et vérifie que tout lien profond du dépôt
  vise une cible existante. Un `#ancre` absent ne lève aucune erreur : il dépose
  le lecteur en haut de onze écrans.

---

## 3. Preuve au rendu (`CLAUDE.md §5.1`) — 3 formats × 2 comptes × 4 surfaces

360×800 · 390×844 · 430×932, compte peuplé et compte vide.

| Surface | écrans (390) | mots | tirets nus | Markdown | prescriptions |
|---|---|---|---|---|---|
| Coach, peuplé | 3,8 | 489 | **0** | **0** | **0** |
| Coach, vide | 3,5 | 431 | **0** (était 5) | **0** | **0** |
| Profil, peuplé | 1,8 | 116 | **0** (était 6) | 0 | — |
| Profil, vide | 1,8 | 116 | **0** | 0 | — |
| Science | 11,2 | 1 446 | 0 | 0 | 7 identifiants rendus |
| Export | 1,6 | 106 | 2 | 0 | — |

**Le rapport a grossi : 369 → 489 mots.** Je le dis plutôt que de le taire.
C'est le coût de ce que l'arbitrage demande — une légende de quatre natures, un
bloc de couverture, une référence attribuée, une limite de plus aux garde-fous.
Ce coût est **délibérément localisé ici** : c'est précisément pour cela que C3
interdit de badger le niveau 1 des autres surfaces.

**Deux défauts trouvés au rendu, pas à la relecture :**

1. **Cinq tirets nus sur le Coach vide.** Le bloc discipline rendait `—` dans
   une pastille `not-deductible` : la bordure disait la bonne chose, le texte
   disait un signe. Le modèle canonique a un libellé pour cet état — « Non
   déductible » s'écrit désormais en toutes lettres.
2. **Les identifiants de règle faisaient 38 px de cible**, pas 44. J'avais posé
   12 px de remplissage sur un texte de 11 px sans mesurer. Relevé au
   `getBoundingClientRect` : Science est passée de 17 à **10** cibles sous le
   standard.

**Un faux positif de mon propre instrument, vérifié avant d'être signalé** : la
sonde marquait « PRESCRIPTION viser » sur Science. Le mot vit dans le corps de
la règle `plages-repetitions` — « viser l'échec à 8 reps d'abord » — c'est-à-dire
la description d'une méthode dans un document de référence, pas un objectif
calculé pour quelqu'un. Rien à corriger.

---

## 4. Relecture des décisions UI (`CLAUDE.md §5.2`)

| Règle | Verdict |
|---|---|
| **5.1** exposition préalable | **respectée** — 24 relevés, 8 captures pleine page ; 2 défauts trouvés à l'œil |
| **5.2** relecture consignée | **respectée** — ce tableau |
| **5.3** jamais une soustraction seule | **respectée** — le bloc 9 part, la couverture arrive ; le Coach quitte Progression et gagne une destination réelle ; la config quitte le L1 et reste éditable |
| **5.4** toute couleur est un token mesuré | **respectée** — `coach-tag--derived` est neuf : `#eef5fb` sur `#1e4b6e`, **10,4:1** mesuré sur le fond réel de la pastille, plus sa variante d'impression (le rapport est fait pour être imprimé) |
| **5.5** centralité avant facilité | **respectée** — C1 puis C2 (les deux surfaces qui ne varient pas avec les données) avant C5 et C10 |

---

## 5. Mes propres fautes, dans cette tranche

1. **Deux gardes passaient pour la mauvaise raison**, toutes deux trouvées en
   plantant le défaut :
   - « le Coach Report est atteignable depuis `/export` » restait verte alors
     que le bloc était supprimé — satisfaite par le lien du **menu utilitaire**,
     présent sur toutes les pages. Elle prouvait l'existence de la navigation,
     pas celle de la destination. Elle lit maintenant `<main>`.
   - « la référence n'est pas déclenchée par un seuil » cherchait un `<` dans la
     source : elle ne voyait donc pas un seuil écrit avec `>`, ce qu'un futur
     correctif écrirait naturellement. Elle est devenue **comportementale**.
2. **Trois assertions fausses au premier jet** — Jinja échappe les apostrophes
   en `&#39;`, et mon motif de lien profond oubliait l'apostrophe fermante de
   `url_for('science_page')`, si bien que la garde n'auditait **aucun** lien.
3. **Une cible tactile posée sans la mesurer** (38 px annoncés 44).

---

## 6. Vérifications

| Contrôle | Résultat |
|---|---|
| `check_scope.py` | `SHARED_CODE` |
| ruff, reproduction exacte du rapport CI | **0** occurrence dans les fichiers de la tranche |
| pré-scan AST `S9073` / `S5863` / `S1192` | 2 trouvées **dans mon code neuf**, corrigées avant push |
| gardes plantées | **16 / 16 rougissent** |
| gardes existantes migrées | **7**, aucune supprimée ni affaiblie |
| suite complète en local | `scripts/run_local_sweep.sh` |

---

## 7. Ce que je n'ai pas fait, et pourquoi

- **Les deux `—` d'Export subsistent.** Ils relèvent de **C7**, que l'arbitrage
  a placé dans `TRAIN1-E`. Respecter le séquencement plutôt que grappiller.
- **Aucun lien profond ajouté dans la console de séance**, où vivent pourtant
  tempo, temps de repos et rest-pause. C'est une surface `SOVEREIGN` : y
  toucher demande son propre cadrage.
- **Les deux avertissements « ceci ne fait encore rien »** du Profil restent.
  Je les avais signalés ; l'arbitrage C2 ne les a pas retenus.
- **`/dashboard` et `muscle_scoring`** restent tels que `TRAIN1-C` les a laissés.
