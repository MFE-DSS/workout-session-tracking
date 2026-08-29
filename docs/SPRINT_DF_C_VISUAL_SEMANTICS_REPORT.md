# `DF-C` — le type de série se voit, il ne se déchiffre plus

`OPERATOR_DECISION` — dogfood de séance · branche `sb/df-c-visual-semantics` ·
base `d7ec388`

---

## 1. Le défaut, tel que l'opérateur l'a posé

> `DF-03` — « `É`/`S` sont des **codes techniques**, pas la sémantique visuelle
> d'AUREN. »

Entre deux séries, sur un téléphone, `É1` et `S1` demandaient une **lecture puis
une traduction**. Le contrat de remplacement :

| Dimension | Porteur | État |
|---|---|---|
| **TYPE** — échauffement vs travail | **microglyphe** | neuf |
| **ÉTAT** — passé · courant · futur | marqueurs `✓ ● ○` | **inchangé** |
| **NUMÉRO** | typographie | **inchangé** |

Le numéro n'avait aucune raison de devenir un dessin, et le marqueur d'état
n'avait aucune raison d'absorber le type : **un signe, une chose**.

---

## 2. Brainstorming · options · risques · choix (`CLAUDE.md §3`)

| Option | Ce que ça donne | Pourquoi écartée / retenue |
|---|---|---|
| **A** — mot complet (`Échauffement 1`) | non ambigu | mange la largeur du seul écran qu'on utilise debout ; repousse les valeurs, contre Q4 |
| **B** — couleur seule | compact | **échoue au gate** : en niveaux de gris, plus rien ne distingue |
| **C** — emoji / pictogramme | immédiat | interdit par l'ordre, et hors registre typographique du produit |
| **D** ✅ — **microglyphe de forme** | compact, perceptible avant lecture | tient en niveaux de gris ; hérite de `currentColor`, donc **aucune couleur neuve** |

**Risque principal identifié avant d'écrire** : qu'un dessin devienne la
**seule** vérité, et disparaisse pour un lecteur d'écran. Traité en amont —
`aria-hidden` sur les `<svg>`, et le nom accessible passe **en toutes lettres**
(« Échauffement 1 », « Série de travail 1 »), gardé par deux tests.

**Les deux formes**, choisies pour qu'aucune conversion en gris ne les confonde :

* échauffement → diagonale **ouverte** (`<path>`, `fill="none"`) — la montée ;
* travail → barre horizontale **pleine** (`<rect>`, `fill="currentColor"`) — la charge.

Orientation **et** remplissage diffèrent : deux canaux, pas un.

---

## 3. Le gate, mesuré

Rendu réel, Chromium, 360 / 390 / 430 px, `device_scale_factor=3`, sur **deux
états** — séance neuve et séance avancée.

| | neuve | avancée |
|---|---|---|
| glyphes échauffement / travail | 2 / 3 | 2 / 3 |
| codes rendus | `1 2 1 2 3` | `1 2 3 Échauffement 1 2` |
| **codes alphabétiques restants** | **0** | **0** |
| `<summary>` visibles < 44 px | **0** | **0** |
| débordement horizontal | **non** | **non** |
| densité | 3,6 / 3,3 / 2,9 écr | 3,5 / 3,3 / 2,8 écr |

En **niveaux de gris** à 390 px, la colonne des lignes rend `╱ 1`, `╱ 2`,
`▬ 1`, `▬ 2`, `▬ 3` avec `●` sur la courante et `○` sur les futures. La
distinction tient par **orientation et remplissage**, jamais par la teinte.

### Le glyphe est-il aussi visible que le caractère qu'il remplace ?

La bonne question n'est pas « le contraste est-il bon » — les lignes futures
sont **volontairement** atténuées, c'est la dimension ÉTAT. La question est :
**ai-je dégradé quelque chose ?** Elle se répond en comparant, **au pixel et
dans la même ligne**, le glyphe et l'ordinal qui l'accompagne — pas le glyphe
en pixels contre une couleur *calculée*, qui ne traverse ni l'anticrénelage ni
les opacités empilées.

| Ligne | glyphe | ordinal | verdict |
|---|---|---|---|
| courante — **avec** mon `opacity: .85` | 9,10:1 | 12,02:1 | **plus faible** ✗ |
| future — **avec** `opacity: .85` | 2,25:1 | 2,66:1 | **plus faible** ✗ |
| courante — **sans** | **12,02:1** | 12,02:1 | identique ✓ |
| future — **sans** | **2,66:1** | 2,66:1 | identique ✓ |

J'avais posé cette `opacity` pour « rendre l'échauffement plus discret » — une
subtilité que personne n'a demandée, qui affaiblissait **la seule chose que la
tranche installe**. Retirée. Le glyphe porte désormais exactement la visibilité
du caractère qu'il remplace.

Le **2,66:1 des lignes futures est hérité**, pas introduit : l'ordinal y est
identique, et `É1`/`S1` s'y affichaient dans la même couleur. La discrétion des
lignes futures est portée par `currentColor`, qui suit l'état toute seule.

---

## 4. Les cibles `<summary>`, repliées sur ordre

> « Fold the 5 measured `<summary>` targets below 44px into DF-C. Do not create
> a separate target-size tranche. »

**44 px = standard produit AUREN** (`UIV3_TARGETS_44_01`), **pas** WCAG 2.2 qui
demande 24×24 avec exception d'espacement. Aucune non-conformité réglementaire
n'est corrigée ici.

| Contrôle | Avant | Après | Note |
|---|---|---|---|
| `.session-feedback__note > summary` | 28 px | **44 px** | marqueur natif tué par `flex` → **chevron redessiné** |
| `.rule > summary` ×3 | 20–39 px | **44 px** | idem |
| `.overload-hint__why-toggle` | **29 px** | **44 px** | trouvé tardivement — voir §6 |

Le plancher est posé en `:where()` : **spécificité zéro**, donc n'importe quel
composant peut redéfinir sans lutte de cascade.

> ⚠ `display: flex` sur un `<summary>` **supprime son marqueur natif** — défaut
> mesuré en `UX4_02C`. Le chevron est donc redessiné dans la même règle, sinon
> on échangeait une cible trop petite contre une affordance invisible.

---

## 5. Conflit de spec — traité, pas contourné

**Q4 du relevé versionné décidait explicitement `É1` et `S1`.** Cette tranche les
retire. `CLAUDE.md §4` fait de cela un **arrêt dur** : « ignorer un conflit de
spec », « amender **silencieusement** une spec versionnée ».

Le relevé porte donc un **amendement explicite et daté**
(`docs/DESIGN_DECISIONS_UIV2_SURFACES.md`, Q4), dont l'autorité est la note de
dogfood de l'opérateur (`DF-03`) et l'ordre `GO DF-C`. Il énonce ce qui est
superséde (la colonne « Après », **sur les lignes seulement**) et ce qui reste
entier — dont le point d'état de Q4, conservé tel quel.

### `§5.2` — relecture décision par décision

| Décision | Verdict |
|---|---|
| **Q1** — la connexion porte l'identité | non concernée |
| **Q2** — ancre visuelle de l'accueil | non concernée |
| **Q3** — « État du jour » replié | non concernée |
| **Q4** — la ligne de série est un instrument | **concernée · amendée explicitement** ; « les valeurs deviennent l'objet, le texte recule » est **renforcé**, le point d'état **conservé** |
| **Q5** — trois rangs de surfaces | **respectée** : aucun conteneur ajouté ; le glyphe est rang 3 — typographie et espace seuls |
| **Tokens bleus** | **respectée** : `currentColor`, **aucune couleur introduite**, donc aucun token à mesurer (`§5.4`) |
| **Convergence Gravl → Auren** | respectée : rien n'est ajouté au-dessus de la ligne de flottaison |
| **Ordre de livraison (centralité)** | respectée : la ligne de série est l'objet le plus manipulé de l'écran le plus utilisé |

`§5.3` — **aucune soustraction seule** : les codes partent dans la **même**
livraison que le glyphe qui les remplace, et le numéro survit.

---

## 6. Fautes de l'agent

Six dans l'**instrument**, **une dans le produit**. Deux ont failli me faire
livrer des gardes creuses, et la septième aurait affaibli la seule chose que
cette tranche installe.

1. **Deux gardes vertes alors que leur défaut était planté.** Elles
   n'exerçaient que l'état INITIAL, où le courant est un échauffement et où
   aucune ligne passée n'existe : la branche mutée n'était **jamais rendue**.
2. **Et l'état « avancé » que j'ai écrit pour les corriger était faux aussi** :
   mon POST n'envoyait que la série visée, donc **chaque envoi effaçait les
   précédentes** — exactement le défaut que `DF-B` documente et interdit. Le
   formulaire sérialise toute la carte ; le harnais doit faire pareil.
3. **Une garde de PRÉSENCE ne gardait rien.** « `Série de travail` figure
   quelque part » était déjà satisfait par la ligne courante ; réintroduire un
   code sur les lignes **passées** la laissait verte. La propriété réelle est
   qu'**aucun** nom accessible ne soit un code.
4. **Une mutation CSS non ancrée.** `min-height: 44px` apparaît **25 fois** dans
   la feuille ; ma mutation frappait une règle sans rapport et je concluais
   « garde inutile » sur une garde saine.
5. **Une garde du marqueur satisfaite par la mauvaise règle** : elle cherchait
   `::before` « quelque part autour » et trouvait celle de l'état `[open]`,
   pendant que le marqueur de l'état fermé avait disparu.
6. **Un relevé de cibles trop étroit.** Je ne balayais que la carte de séance et
   j'ai écrit « zéro cible sous 44 ». En mesurant la **page**, « Pourquoi ? »
   sortait à **29 px, visible**. Une mesure trop étroite ne rassure pas : elle
   conclut faux.

7. **Et une faute dans le PRODUIT, la seule** : j'avais posé `opacity: .85` sur
   le glyphe d'échauffement pour « le rendre plus discret ». Personne ne l'avait
   demandé, et mesurée au pixel elle rendait le **porteur du type plus faible
   que l'ordinal qu'il accompagne** (9,10:1 contre 12,02:1). Une décoration qui
   dégrade la propriété qu'on vient d'installer. Retirée — les deux mesures sont
   désormais identiques.

   Elle n'a pas été trouvée par un test mais parce que j'ai voulu **mesurer** au
   lieu d'affirmer. Et ma première mesure était elle-même fausse : elle comparait
   les **pixels** du glyphe à la couleur **calculée** du texte — deux grandeurs
   qui ne traversent ni le même anticrénelage ni les mêmes opacités. Comparer
   deux choses n'est une comparaison que si on les mesure pareil.

L'enseignement, qui prolonge celui de `DF-B` d'un cran : **une garde rouge ne
prouve rien tant qu'on n'a pas vérifié qu'elle est verte pour la bonne raison —
et qu'elle rougit pour la bonne raison.** Ici, cinq des sept vérifications de
garde ont d'abord mesuré autre chose que ce qu'elles annonçaient.

Et son corollaire, payé une fois de plus : **ce qu'aucune garde ne regarde, seule
une mesure le voit.** Les quinze gardes étaient vertes avec l'`opacity` en place.

---

## 7. Gardes

`tests/test_df_c_visual_semantics.py` — **15 gardes**, chacune plantée :

| Défaut planté | Verdict |
|---|---|
| code alphabétique sur la série de travail **courante** | **ROUGE** ✓ |
| code alphabétique sur les lignes **passées / futures** | **ROUGE** ✓ |
| nom accessible redevenu un code | **ROUGE** ✓ |
| les deux glyphes deviennent identiques | **ROUGE** ✓ |
| une couleur en dur entre dans le glyphe | **ROUGE** ✓ |
| le plancher tactile retombe sous 44 | **ROUGE** ✓ |
| le marqueur disparaît alors que `flex` l'a masqué | **ROUGE** ✓ |
| « Pourquoi ? » retombe à 24 px | **ROUGE** ✓ |
| le marqueur fermé de « Pourquoi ? » disparaît | **ROUGE** ✓ |
| le marqueur fermé ne dessine plus rien | **ROUGE** ✓ |
| le récapitulatif perd son nom accessible | **ROUGE** ✓ |
| une atténuation revient sur le glyphe | **ROUGE** ✓ |

**Aucune garde existante n'a été affaiblie ni supprimée.**

### La ligne que le diff a rattrapée, et pas un test

La ligne du **récapitulatif d'échauffement** n'avait **aucun** `sr-only`. Elle
affichait `É1` : le code était sa seule identité. En le remplaçant par un glyphe
`aria-hidden`, elle ne se serait plus annoncée que **« 1 »**.

C'est une **soustraction seule** (`§5.3`) sur le seul canal qui ne voit pas le
dessin — et aucune des treize gardes ne la voyait, parce qu'elles cherchaient la
présence des bons mots quelque part, jamais l'**absence de nom** sur une ligne
précise. La quatorzième garde énonce la propriété : *dès qu'une ligne confie son
type à un glyphe masqué, elle le dit en toutes lettres.*

Trouvé en **relisant le diff**, pas en lisant un test.

---

## 8. Vérifications

| Vérification | Résultat |
|---|---|
| `check_scope.py` | `ISOLATED` — **remonté d'un cran** (`§1`) : `exercise_card.html` est le gabarit central du runtime de séance |
| `tests/test_df_c_visual_semantics.py` | **15 passés** |
| Broad sweep ciblé (console de séance, 4 fichiers) | **83 passés** |
| `tests/test_overload_hint_a11y.py` | **14 passés** |
| ruff (fichier neuf) | **propre** |
| `check_ruff_budget.py` | **276 / 548** |
| `check_spec_protocol.py` | **OK** |
| Pré-scan AST (`S9073` · `S5863` · `S1192` · balise dans commentaire Jinja) | **0** après factorisation de deux littéraux |
| **Full sweep local** | *(voir closeout)* |

---

## 9. Arbitrage soumis à l'opérateur — **non tranché**

La commande dominante dit toujours **`VALIDER É1`** / **`VALIDER S1`**, alors que
plus **aucune** ligne de l'écran ne porte ce nom. La tranche crée donc une
incohérence sur le contrôle **le plus central** de l'écran (`§5.5`).

Trois variantes **rendues réellement** à 360 px — toutes trois tiennent sur une
ligne, hauteur identique (56 px), aucun débordement :

| | Libellé | Remarque |
|---|---|---|
| **A** | `VALIDER É1` | statu quo — garde le code que la tranche retire ailleurs |
| **B** | `VALIDER ÉCHAUFFEMENT 1` | reprend **mot pour mot** le nom accessible déjà rendu |
| **C** | `VALIDER LE 1er` / `VALIDER LA SÉRIE 1` | plus court, mais le type disparaît de l'échauffement |

Je ne tranche pas : c'est une décision d'écriture, et `§5.1` dit que
**l'opérateur tranche**.

---

## 10. Hors périmètre — mesuré, non touché

* **`.sub-elargi > summary`** (« Voir alternatives élargies ») : `list-style:
  none` **et** marqueur webkit masqué, **sans remplacement** — le même défaut
  d'affordance que `UX4_02C`. Il mesure 62 px aujourd'hui, donc **au-dessus** du
  plancher, et n'était **ni** dans les 5 cibles mesurées **ni** dans l'ordre. Le
  corriger serait un changement de périmètre ; c'est consigné pour arbitrage.
* **`.app-rail__secondary-toggle`** (« Plus ») mesure `0×0` : **non rendu**,
  donc pas une cible ratée. Le compter comme telle aurait fait « corriger » un
  élément invisible et laissé le vrai.
* **`DF-D`** — repos adaptatif : différé par l'ordre, rien ici ne l'anticipe.
* Les codes **`E1…E7`** (exercice, pas série) : autre axe, hors de cette tranche.

---

## 11. Closeout post-merge

| | |
|---|---|
| PR | **#174** |
| Merge | **`6bc298e`** — `--merge`, tête épinglée `1d911b1`, **pas de squash, pas de `--admin`, pas de force** |
| CI de PR | **8/8 `pass`** après **un** cycle rouge, hors produit |
| Gate Sonar (PR) | **`OK`** — 0 bug · 0 code smell · 0 vulnérabilité · duplication 0,0 % |
| CI canonique (`push` sur le merge) | run **33261259002** — **succès, 6/6 jobs** |
| Full sweep local | **289/289 fichiers verts**, pic 1961 Mo / 1976 |
| Fils de revue non résolus | **0** |

### Le cycle rouge, et pourquoi il compte

Un seul écart : `new_code_smells_severity` à **15** pour un plafond de 14. Comme
MAJOR pèse exactement 15, l'arithmétique disait **un** finding avant même de le
chercher — c'est le premier réflexe de la route de diagnostic, et il évite de
partir en chasse.

`css:S4666` : *« Duplicate selector `.setline__code`, first used at line 2157 »*.
**Le signalement était exact.** J'avais posé un second bloc en fin de feuille
alors que la règle existait déjà. Aucune propriété ne se chevauchait ici — mais
deux règles pour un même sélecteur laissent croire à deux composants, et la
seconde gagne **en silence** sur toute propriété commune. Un piège posé pour la
prochaine lecture, pas une organisation.

Les trois déclarations ont rejoint la règle d'origine. **Rendu inchangé,
remesuré au pixel** : 12,02:1 / 12,02:1 sur la ligne courante, 2,66:1 / 2,66:1
sur les futures. Balayage de tous les sélecteurs de premier niveau : **zéro
doublon introduit par `DF-C`** (4 préexistants ailleurs, hors périmètre).

C'est la **deuxième fois dans ce train** qu'un signalement d'analyseur qui
« sentait » le faux positif avait raison — après la balise littérale dans un
commentaire Jinja de `DF-B`. La leçon du dépôt tient : ne jamais adjuger un
finding sans le lire.

### Ce que cette tranche laisse au dépôt

**Sept fautes : six dans l'instrument, une dans le produit.** Cinq
vérifications de garde sur sept ont d'abord mesuré autre chose que ce qu'elles
annonçaient — dont un harnais faisant un **POST partiel qui effaçait les séries
précédentes**, exactement ce que `DF-B` documente et interdit.

Et la seule faute qui a atteint le produit — l'`opacity: .85` qui affaiblissait
le porteur du type — **n'a été trouvée ni par un test ni par la CI**. Les quinze
gardes étaient vertes avec elle en place. Seule une mesure au pixel l'a vue, et
**ma première mesure était fausse elle aussi** : elle comparait des pixels à une
couleur calculée.

Trois énoncés, du même bloc :

1. **Une garde rouge ne prouve rien** tant qu'on n'a pas vérifié qu'elle est
   verte pour la bonne raison — et qu'elle rougit pour la bonne raison.
2. **Ce qu'aucune garde ne regarde, seule une mesure le voit.**
3. **Comparer deux choses n'est une comparaison que si on les mesure pareil.**

### Reste ouvert

* **Arbitrage `VALIDER É1`** — §9, trois variantes rendues, **non tranché**.
* **`.sub-elargi > summary`** — marqueur absent sans remplacement, 62 px donc
  au-dessus du plancher, hors périmètre (§10).
* **`DF-D`** — repos adaptatif, différé par l'ordre.
* **Smoke iPhone `DF-B`** — action opérateur, pour marquer
  `DF-B_RUNTIME = VALIDATED_IN_PRODUCTION`.
* **Déploiement** : `6bc298e` **n'est pas en production** — le dernier
  déploiement reste `d7ec388`.
* **Suite** : retour à `UX4_02C_PROGRAMS_REAL_USER_DOGFOOD_01`, puis A2 étape C.
