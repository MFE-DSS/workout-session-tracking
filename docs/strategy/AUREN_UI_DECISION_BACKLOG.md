# `AUREN_UI_DECISION_BACKLOG` — l'ordre de décision

> **Ce document ne décide rien.** Il énumère ce que l'opérateur doit trancher
> pour qu'un contrat puisse être écrit **sans zone d'ombre**, et pour que les
> extrapolations graphiques correspondent à une intention exprimée plutôt qu'à
> une supposition d'agent.
>
> Créé le 2026-09-04, en entrant dans le
> `PHILOSOPHICAL UI RE-DESIGN PASS`.
>
> Compagnon du `AUREN_UI_REARBITRATION_REGISTER` : le registre inventorie
> **ce qui existe** (79 objets) ; ce backlog énumère **ce qui doit être décidé**.

---

## Comment lire ce document

Chaque point porte :

| Champ | Sens |
|---|---|
| `ID` | référence stable, citée par les contrats et les tranches |
| **La question** | formulée comme une vraie fourche, jamais comme une suggestion déguisée |
| **Pourquoi elle bloque** | ce qui ne peut pas être écrit tant qu'elle est ouverte |
| **Ce qui en dépend** | les points et objets en aval |
| **Forme de réponse** | `CHOIX` · `DESCRIPTION` · `RÉFÉRENCE` · `MESURE` |

**Ordre non négociable.** Un point ne doit pas être arbitré avant ceux dont il
dépend — sinon la réponse préempte une décision plus fondamentale. C'est
exactement l'erreur que le `PHILOSOPHICAL PASS` corrige.

---

## Réponses opérateur — `BLOC 0`, session du 2026-09-04

> Notes brutes conservées telles que dictées. La normalisation est **proposée**,
> jamais substituée à la note.

| ID | Note brute | Normalisation proposée | État |
|---|---|---|---|
| `L-01` | *« le cockpit en ce moment, c'est tous les instruments … je veux un cockpit comme on a dans les applications orientées CTA très efficace … visuellement très adaptés pour [faire] une séance de muscu … c'est à moi pour chaque élément de donner des choses »* | **Tableau d'instruments, pas console à valeur unique** : les instruments pertinents sont présents simultanément. **Mais l'action reste sans ambiguïté** — l'efficacité « orientée CTA » porte sur la lisibilité de la commande, pas sur la réduction de l'information. L'opérateur spécifiera **élément par élément**. | ⚠ **tension, voir ci-dessous** |
| `L-02` | *« ce que je ne veux surtout pas : l'interface plate comme aujourd'hui … elle rend mal la dichotomie entre les blocs … beaucoup de données textuelles, très bien parce que c'est de l'information, mais elle doit être dérivée en illustration et image pour être plus intuitive. Ça ne me dérange pas le dégradé, le verre poli, les ombres portées, les coins très arrondis, les couleurs vives, les illustrations — j'adore. C'est vraiment les gros aplats qu'on a aujourd'hui »* | **REJETÉ** : la planéité actuelle · les gros aplats · la dichotomie de blocs illisible · la donnée laissée à l'état de texte. **AUTORISÉ et souhaité** : dégradé · verre dépoli · ombre portée · rayon généreux · couleur vive · illustration. **Règle qui en sort : une donnée doit être dérivée en objet visuel quand elle peut l'être.** | ✅ **fermée** |
| `L-03` | *« si je devais te donner une DA : la représentation transhumaniste de la série Netflix Fallout, inspirée du jeu vidéo … un côté un peu plus codifié, style application cockpit rétro-gaming … des objets qui s'imbriquent mieux entre eux visuellement, avec un meilleur confort »* | **Référence structurelle, pas décorative** : l'instrument-corps (type Pip-Boy) est **un cockpit porté qui affiche l'état du corps** — la métaphore est apte, pas empruntée. Propriétés extraites : châssis d'instrument · lecture en jauge plutôt qu'en phrase · commande physique évidente · iconographie illustrée porteuse de sens · emplacement **codifié et répété** · profondeur assumée. | ✅ **fermée** ⚠ tensions ci-dessous |
| `L-04` | *« clinique calme et engageant »* | **Les trois retenus, pas un choix** : clinique par la factualité, calme par le chrome, engageant **par la réponse de l'instrument** — jamais par la décoration. | 🟡 **à confirmer** |
| `L-05` | *« on doit être dense pendant l'effort et aéré à la lecture »* | **Deux contextes de densité nommés** : `EFFORT` dense · `LECTURE` aéré. `SYS-079` cesse d'être abstrait. | ✅ **fermée** |
| `L-06` | *« oui, peut y avoir un mouvement autorisé, mais l'idée c'est d'avoir un statique fin plutôt que de faire trop de couches UI »* | **Mouvement autorisé mais subordonné** : il sert un état qui change, jamais l'agrément. Le défaut reste **statique et fin**. `prefers-reduced-motion` devient contrat. | ✅ **fermée** |
| `L-07` | *« l'interface plate comme aujourd'hui … les ombres portées, le verre poli, j'adore »* | ⚠ **J'AVAIS INFÉRÉ L'INVERSE ET J'AVAIS TORT.** De *« trop de couches UI »* j'avais déduit un plan unique ; l'opérateur visait le nombre d'écrans, pas l'altitude. **Décision : profondeur assumée**, les objets ont un châssis et une élévation. **`SYS-078` est rouvert** — « surface par défaut sans ombre » ne tient plus. | ✅ **fermée — INVERSÉE** |
| `L-08` | *« une ambition chromatique à voir, oui, en fait je ne sais pas ce que c'est »* + *« les couleurs vives, j'adore »* | Déclinée en tant que telle, mais **bornée par `L-02`** : la couleur vive est autorisée. Reste à trancher **combien de familles** et **ce qu'elles signifient** — reformulé en question produit. | 🟡 **reformulée** |
| `L-09` | *« il y a plein de choses bonnes, mais tout doit être augmenté … on a un bon backbone produit et structurel — planning, programme, tracking — mais tout ça doit être upgradé pour devenir une vraie application … c'est juste les différents CTA, les différentes illustrations »* | **AUCUN objet n'est gelé.** Ce qui est bon est le **backbone produit** — les responsabilités, la structure, le tracking. Ce qui doit changer est **l'expression** : CTA et illustrations. ⚠ **Conséquence forte : les décisions de NIVEAU 1 (responsabilité) sont majoritairement `KEEP` ; le chantier est aux niveaux 2 et 3.** | ✅ **fermée** |

### `PH-01` — LE PRINCIPE PRODUIT, énoncé par l'opérateur le 2026-09-04

> **Note brute.** *« Il faut faire des jauges partout, c'est un truc à mettre en
> place partout, car c'est une notion philosophique à considérer : les jauges,
> c'est notre état d'énergie, d'endurance, de performance, qui est le facteur
> nécessaire — car le cockpit est là pour optimiser l'allocation de notre
> endurance et performance, qui doit être consommée pour augmenter notre charge
> de stress et notre performance body. »*

**Normalisation.** AUREN n'est pas un journal d'entraînement : c'est un
**instrument d'allocation de ressource**. Une ressource finie — énergie,
endurance, capacité — se **dépense** pour produire du stress d'entraînement,
donc de la performance. La jauge n'est pas un ornement : c'est **la
représentation native de cette ressource**.

**Conséquence.** La jauge devient une **primitive transverse** (`X-03` cesse
d'être une question ouverte et devient un objet à concevoir), et la question
« que montre cet écran ? » devient partout « **où en est la ressource, et
qu'est-ce que cette action va lui coûter ou lui rendre ?** »

### Levées de règle et précisions — opérateur, 2026-09-04

| Règle | Décision | Portée |
|---|---|---|
| **« Ne pas inventer de géométrie · ne pas dessiner d'anatomie »** | ⚠ **LEVÉE PARTIELLEMENT.** *« retire la règle du dépôt là, on peut prendre un peu plus de liberté ; si tu as envie de dessiner des illustrations d'exécution dessinée, tu peux le faire »* | **Autorisé** : illustration de **geste et d'exécution**, schéma de machine, pictogramme de mouvement. **Reste interdit** : toute revendication d'**activation musculaire** (`%`, EMG) — c'est une affirmation scientifique, pas une illustration d'interface. La levée porte sur le **dessin**, pas sur la **preuve**. |
| `L-08` **ambition chromatique** | ✅ **FERMÉE.** *« on a déjà les valeurs d'AUREN qu'on avait définies, qui sont à reprendre et améliorer »* | Point de départ = la palette existante et **mesurée** de `§4` : ambre `#C8A24B` · bleus système `#7DD3FC` / `#5FA8D3` / `#4A7FB5` · graphites `#0F1318` / `#151A21` / `#1B2029`. **Reprise et amélioration, pas table rase.** Chaque valeur modifiée est repromue en token **avec sa mesure de contraste** (`CLAUDE.md §5.4`). |
| **Méthode d'arbitrage** | ✅ **FIXÉE.** *« tu mets ton système de questionnement avec tes trois réponses proposées, c'est le recommandé, puis je vais trancher à chaque fois »* | Pour tout point ouvert : **trois options réellement distinctes**, une recommandation motivée, l'opérateur tranche. Jamais de variante de degré. |

### ⚠ Contradictions ouvertes par le `BLOC 0`

| # | Contradiction | À trancher |
|---|---|---|
| `K-01` | profondeur | ✅ **FERMÉE — l'échelle de profondeur est DÉRIVÉE DE LA STRUCTURE PRODUIT, pas inventée.** *« le niveau 1 de base, c'est le background, le backbone du cockpit ; dans le cockpit il y a des éléments comme le tableau de bord, le dashboard de profil, les différents programmes ; dans chaque programme, les modules, le training en cours avec les cartes et séances, les substituts, les alternatives »* → **4 niveaux**, chacun signifiant une profondeur d'imbrication réelle. **`SYS-078` est superseded.** |
| `K-02` | imbrication | ✅ **FERMÉE — l'imbrication est L'OBJECTIF**, pas une tolérance. *« oui, mais c'est aussi l'objectif à terme, c'est justement ça »*. **`VIS-015` « interdire les cartes imbriquées » est superseded** : un châssis contenant des instruments est légitime **parce que codifié**. |
| `K-03` | jauge et daltonisme | ✅ **FERMÉE** — *« la jauge doit porter un sens par la forme aussi, pas seulement par la couleur »*. `§7` `no-color-only-state` **tient**. Voir `PH-01` ci-dessus. |
| `K-04` | registre rétro | ✅ **FERMÉE — on peut aller très loin.** *« châssis et jauge c'est bien, avec des scanlines, grains, lueur de phosphore, c'est très bien … ça rappelle Fallout, thermonucléaire »*. ⚠ **Deux contrats sont superseded, à confirmer explicitement** — voir `K-05`. |
| `K-05` | ⬜ **TOUJOURS OUVERTE — ne pas inférer.** Le contrat de séance `S-00` est compatible avec `A` **comme** avec `B` : « combien de séries », « à quel poids », « la dernière fois » sont des **coûts et des références**, jamais une disponibilité globale. La question ne se pose donc **qu'au moment d'une jauge GLOBALE** — Accueil, Progression. Le travail sur la Séance peut avancer sans elle. | `PH-01` demande des jauges d'**énergie / endurance / performance** partout. Or le produit a **délibérément retiré** le KPI de disponibilité 0–100 de l'accueil *« parce qu'il introduisait une échelle distincte du contrat de récupération »*, et `§4` refuse à la récupération toute palette au motif qu'elle *« suggère un jugement médical que le produit refuse »*. **Une jauge d'énergie globale réintroduit exactement ce qui a été retiré.** À trancher : `PH-01` supersede-t-il ce refus, ou la jauge mesure-t-elle autre chose qu'une disponibilité globale ? |
| `K-06` | ✅ **FERMÉE — les deux.** *« C'est un peu des deux : il y a une partie décorative de surface bien sûr, pour la DA du projet, et après structurelle. Tout doit vivre dans l'objet en réalité. Rappelons que le texte doit être intuitif et très simple. »* → **couche décorative** (scanlines, grain, lueur) au service de la DA, **et** logement structurel : le contenu **vit dans l'objet**. ⚠ **Nouvelle contrainte, de premier rang : le texte doit être intuitif et très simple.** C'est ce qui rend le grain soutenable — peu de texte, gros, simple. | ~~ancienne formulation~~ |
| ~~`K-06` ancien~~ | ⚠ **NOUVELLE — rétro-CRT contre deux contrats** | Scanlines, grain et lueur de phosphore entrent en conflit avec `SYS-077` (matrice de contraste), avec le brief fondateur (*« confiance plutôt qu'excitation graphique »*) et avec `L-04` (*clinique, calme*). Mesuré au lab : **les trois variantes débordent déjà horizontalement à 200 %**. À trancher : ces effets sont-ils **décoratifs de surface** — donc désactivables et sans effet sur la lisibilité — ou **structurels** ? |

---

# `BLOC 0` — LANGAGE ET INTENTION

> **Rien ne se rend avant ce bloc.** Tant qu'il est ouvert, toute proposition
> graphique est une supposition. C'est le seul bloc où je n'ai **aucune**
> évidence produit à opposer : il n'existe que dans votre tête.

### `L-01` — Que veut dire « cockpit instrument » pour AUREN ?

**La question.** Un cockpit peut être plusieurs choses très différentes : un
**tableau de bord d'avion** (beaucoup d'informations, lecture experte, densité
maximale), une **console de mesure** (une valeur souveraine, tout le reste
subordonné), ou un **poste de travail** (chaque commande à portée, rien de
caché). Laquelle ?

**Pourquoi elle bloque.** Le mot « instrument » a servi à rejeter la carte,
mais il ne dit pas encore ce qui le remplace. Les trois lectures produisent des
écrans opposés.

**Ce qui en dépend.** `P-03` · `P-04` · `P-05` · `P-08` · tout `BLOC 1`.
**Forme.** `DESCRIPTION` + `RÉFÉRENCE`.

---

### `L-02` — Que veut dire « dans l'air du temps » pour AUREN ?

**La question.** Le brief fondateur dit **sobriété du chrome, tâche souveraine,
confiance plutôt qu'excitation graphique**. Une direction contemporaine peut
contredire cela — mouvement, profondeur, couleur, gradients, verre dépoli.
**Qu'est-ce qui est autorisé, et qu'est-ce qui reste interdit ?**

**Pourquoi elle bloque.** Sans elle, je choisis à votre place, et le désaccord
n'apparaîtra qu'au rendu.

**Ce qui en dépend.** `L-03` à `L-08` · toute expression visuelle.
**Forme.** `DESCRIPTION`. ⚠ Répondre aussi par la **négative** : ce que vous ne
voulez surtout pas.

---

### `L-03` — Références : ce que vous aimez, et ce que vous en rejetez

**La question.** Trois à cinq produits ou écrans. Pour chacun : **ce que vous y
voyez précisément** — la densité ? la domination d'un chiffre ? l'absence de
cadre ? le calme ? la vitesse de lecture ? — **et ce que vous rejetteriez dans
cette même référence.**

**Pourquoi elle bloque.** Sans le rejet, j'imite. Avec le rejet, j'extrais un
principe.

**Ce qui en dépend.** Toutes les propositions graphiques.
**Forme.** `RÉFÉRENCE` — description écrite suffit, l'image n'est pas requise.

---

### `L-04` — Registre émotionnel

**La question.** AUREN doit-il être **clinique** (neutre, factuel, froid),
**calme** (sobre mais habité), ou **engageant** (l'effort a une intensité, et
l'interface la reconnaît) ?

**Pourquoi elle bloque.** Détermine la couleur, le mouvement, la typographie et
jusqu'au vocabulaire.
**Ce qui en dépend.** `L-05` · `L-06` · `L-08` · tous les libellés.
**Forme.** `CHOIX` + nuance libre.

---

### `L-05` — Densité : une seule, ou par contexte ?

**La question.** Le `density budget` mesure des *outcomes*. Mais l'intention
n'est pas décidée : AUREN doit-il être **dense partout**, **aéré partout**, ou
**dense pendant l'effort et aéré en lecture** ?

**Pourquoi elle bloque.** `SYS-079` a été arbitré « par contexte » sans que les
contextes soient nommés.
**Ce qui en dépend.** `SYS-079` · `SYS-075` valeurs · `BLOC 1` · `BLOC 3`.
**Forme.** `CHOIX`.

---

### `L-06` — Le mouvement est-il autorisé ?

**La question.** Aujourd'hui l'interface est **statique**. Une transition, un
compte à rebours animé, un état qui se remplit : **autorisé, interdit, ou
réservé à l'instrument** ?

**Pourquoi elle bloque.** `P-05` (repos) et `P-04` (validation) changent
radicalement selon la réponse. Et `prefers-reduced-motion` devient un contrat.
**Ce qui en dépend.** `P-04` · `P-05` · `INT-011` expression.
**Forme.** `CHOIX`.

---

### `L-07` — Profondeur : plat, ou en couches ?

**La question.** `SYS-078` a tranché « surface par défaut sans ombre, une
élévation pour le flottant ». Mais **l'intention** reste ouverte : AUREN est-il
un **plan unique** où la hiérarchie se lit par la typographie et l'espace, ou
un **empilement** où les objets ont une altitude ?

**Pourquoi elle bloque.** Décide si un « instrument » est un objet posé sur la
surface ou **la surface elle-même**.
**Ce qui en dépend.** `P-03` · `P-08` · `SYS-078` valeurs.
**Forme.** `CHOIX`.

---

### `L-08` — Ambition chromatique

**La question.** Aujourd'hui : graphite + ambre + bleu système. **Reste-t-on à
un accent unique**, ou le nouveau langage introduit-il davantage ?

**Pourquoi elle bloque.** `SYS-074` a créé 16 rôles **sans valeurs**. Le nombre
de valeurs distinctes est une décision de direction, pas de token.
**Ce qui en dépend.** `SYS-074` valeurs · `SYS-077` matrice · `VIS-027`.
**Forme.** `CHOIX` + `DESCRIPTION`.
⚠ Rappel de contrainte : `§4` interdit le vocabulaire vert/orange/rouge **pour
l'encodage de récupération**. Les rôles de support existent, leurs valeurs ne
peuvent pas fuir vers la récupération.

---

### `L-09` — Ce qui est **déjà bon** et ne doit pas bouger

**La question.** Quels objets actuels sont, selon vous, **déjà justes** ?

**Pourquoi elle bloque.** C'est la seule borne qui empêche une refonte
exhaustive de devenir une réécriture gratuite. Sans elle, je dois traiter les
79 objets comme également suspects.

**Ce qui en dépend.** La profondeur `D0` de tout le registre.
**Forme.** `DESCRIPTION` — nommez-les, même vaguement.

---

## `P-03` — INSTRUMENT DE SÉANCE · décisions arbitrées 2026-09-04

| Q | Décision | Contrainte opérateur associée |
|---|---|---|
| `Q1` coque pendant l'effort | **B** — réduite à un fil d'état ; la bottom-nav disparaît | — |
| `Q2` jauge de séries | **C** — compteur **+ cible + verdict par série** | la jauge doit rendre conscient que *« la série qu'il vient de faire a eu une bonne ou une mauvaise valeur »* et donner *« un incentive concret »*. Sourcé : `overload_hint.target_summary` + le set + `last_time`. ⚠ `execution_quality` et `reps_target` existent au modèle mais **rien ne les collecte ni ne les affiche** — colonnes mortes |
| `Q3` poids | **C** — readout + incréments tactiles, frappe en repli | dégradation propre vers `B` puis `A` sans JS (`§10`) |
| `Q4` position | **B** — indicateur de vol `E3/7`, précédent et suivant nommés | rang 2 |
| `Q5` repos | **B** — le châssis change d'état, le décompte est un readout | *« surtout informationnel, pas un truc embêtant ; qu'il occupe un espace sans faire d'affliction »* |
| `Q6` illustration d'exécution | **C** — à la première série, repliée ensuite | accompagnée de **2 à 3 cues**, pas quatorze — *« les axes principaux pour une exécution parfaite »* |
| `K-05` jauge macro | **C** — **jauge d'ALLOCATION, pas de suffisance** | *« où est passée ton énergie »*, jamais un jugement. **Dérivée de `PH-01` : « optimiser l'allocation »**, donc aucune cible nommée — la garde `test_the_service_never_names_a_target` **tient** |

## `P-03` — ✅ **MÉTAPHORE VALIDÉE PAR L'OPÉRATEUR, 2026-09-04**

> *« Le viseur central, je pense qu'il a un minimalisme et une esthétique très
> efficaces pour ce type d'application. V1 première série, V2 séries suivantes,
> V3 repos — tous les objets sont bien représentés. »*

**Retenu : `M3` viseur**, dans ses trois états.

| État | Contenu | Décision servie |
|---|---|---|
| `V1` première série | illustration annotée en haut · readout · verdict · incréments · commande | `Q6 C` |
| `V2` séries suivantes | illustration repliée en une ligne · **la charge grandit** | `Q6 C` |
| `V3` repos | **le châssis entier change d'état**, phosphore bleu, décompte en readout, prochaine cible annoncée | `Q5 B` |

**Acquis de forme** — commande en **trait, plus en aplat ambre** (`VIS-002`
« moins gros bouton web ») · verdict par **forme ET couleur** (`§7`) ·
substituabilité au **rang 2** portée par le titre · **aucun espace perdu**.

**Reste non représenté** : l'état `cs.is_correcting`.

### 🅿️ `CHANTIER PARQUÉ` — illustration biomécanique professionnelle

> *« Là tu as mis un bonhomme en spaghetti, mais l'idée c'est qu'on comprenne
> une mécanique, une biomécanique. On avait déjà travaillé en partie dans le
> projet pour faire toute cette recherche. On ne va pas trop s'attarder dessus
> pour l'instant, mais dans l'exécution on intégrera une illustration vraiment
> professionnelle. »*

**Statut** : reconnu insuffisant, **parqué, non bloquant**. Le viseur est validé
**avec un placeholder assumé**.

**Ce chantier ne part pas de zéro.** Le dépôt porte déjà **17 specs d'assets
anatomiques** — `Sb_ASSET_03B_2R_BODYPARTS3D_SOURCE_RESET` ·
`Sx_ASSET_03_BODYMAP_HUMAN_PRODUCTION_PACKAGE` ·
`Sb_ASSET_03B_1_MUSCLE_FOCUS_SYSTEM_BLUEPRINT` ·
`Sb_ASSET_03B_2_P0_REGIONAL_PLATE_PRODUCTION` · `AUREN_ASSET_PROGRAM_ROADMAP` —
et **trois plaques régionales déjà produites** (pectoraux, postérieur, épaules).

**L'illustration d'exécution doit se brancher sur ce programme**, pas ouvrir un
second pipeline d'assets à côté. La piste `C` — huit schémas par **patron de
mouvement**, annotés par les `execution_cues` propres à chaque exercice — reste
la seule qui rende le problème fini ; sa **qualité de rendu** relève du
programme d'assets, pas du chantier UI.

---

## `S-00` — CONTRAT DE LECTURE DE L'INSTRUMENT DE SÉANCE

> **Note brute opérateur, 2026-09-04.** *« Combien de séries je dois faire ? À
> quel poids ? Combien j'ai fait la dernière fois ? L'exercice en question —
> c'est déjà bien. Puis avec un deuxième coup d'œil, je peux comprendre celui
> qui était avant, après, que je peux le substituer par quelque chose d'autre,
> et qu'il y a une illustration pour comprendre comment bien l'exécuter. »*

**Deux rangs de lecture, et ils sont désormais contractuels.**

| Rang | Ce qui doit être compris | Sans lire ? |
|---|---|---|
| **Coup d'œil 1** | quel **exercice** · combien de **séries à faire** · à quel **poids** · combien **la dernière fois** | **oui** |
| **Coup d'œil 2** | ce qui **précède / suit** · que c'est **substituable** · **comment bien l'exécuter** | oui, au second regard |

### Ce que ce contrat décide déjà

* **`S-05` est fermé** — l'historique de l'exercice **mérite d'exister pendant
  l'effort**, et au rang 1 : *« combien j'ai fait la dernière fois »*.
* **`S-06` est cadré** — la substitution doit être **perceptible au rang 2**,
  sans être une commande de rang 1.
* **`S-02` est cadré** — la position dans la séance est du **rang 2**, ce qui
  exclut une liste concurrente au rang 1.

### ⚠ La convergence que ces mots produisent

*« Combien de séries je dois faire »* et *« combien j'ai fait la dernière fois »*
sont **la même primitive** : une **jauge de consommation contre une cible, avec
une marque de référence**. C'est `PH-01` appliqué à l'échelle de l'exercice —
**la jauge de séries EST la jauge de ressource**, au plus petit grain.

### ⚠ Contrainte d'asset sur l'illustration d'exécution

`execution_cues` **existe déjà** (source : atlas machine, rendu en texte replié
sous « Technique », 3 cues max). La transformation en illustration est donc un
changement de **métaphore**, pas une capacité neuve.

**Mais l'illustration exige une source.** La règle du dépôt est explicite :
**ne pas inventer de géométrie, ne pas dessiner d'anatomie.** Trois voies
possibles — pictogramme de geste non anatomique · photo/rendu sous licence ·
schéma de machine dérivé de l'atlas existant. **Aucune n'est décidée.**

---

# `BLOC 1` — LA SÉANCE

> Surface souveraine. Quatre tranches livrées ce mois-ci, dogfoodée ce matin.
> **Le bloc où « cockpit instrument » se prouve ou reste un mot.**

---

## 🔴 RETOUR OPÉRATEUR SUR `U4` — 2026-09-04, sur les trois états rendus

Neuf points, consignés verbatim avant reformulation. **Le message est coupé en
fin de phrase** (« … et que ça soit un CTA bien visible dans un style ») : il
en manque au moins la fin.

| # | Verbatim | Nature |
|---|---|---|
| `R1` | *« le trait, c'est moche, on s'en fiche, il ne sert à rien. Il faudra voir comment le faire autre chose, un truc design dans la DA »* | **la commande en trait est REJETÉE** — à refaire |
| `R2` | *« pour la charge à mettre, il faudrait suggérer combien on est censé mettre »* | suggérer la charge (moteur de surcharge / profil) |
| `R3` | *« ça devrait être valider échauffement ou SAUTER L'ÉCHAUFFEMENT »* | l'action secondaire est mal nommée |
| `R4` | *« passer à E2, c'est passer à l'exercice suivant … pour être intelligible, et là insérer dynamiquement l'autre exercice »* | `PASSER À E2` est illisible → nommer l'exercice suivant |
| `R5` | *« si je mets un kilo, un nombre de reps, c'est que j'ai validé la série, donc automatiquement ça met le timer… **il n'y a pas d'étape de validation** »* | ⚠ **changement de flux produit** |
| `R6` | *« le bouton, c'est jamais "valider" »* | la commande dominante change de nature |
| `R7` | *« il faut mieux, plus design, dans les deux autres exercices qui arrivent »* | les cartes en attente |
| `R8` | *« Push A pecs épaisseur — nettoyer »* | le nom de séance en haut |
| `R9` | *« on ne comprend pas que "technique" est opérable → un bouton RECOMMANDATION, un CTA bien visible »* | affordance + renommage |

### ⚠ Deux conflits que `R5`/`R6` ouvrent, et qui exigent votre arbitrage

**1. L'auto-validation existe déjà — mais sur `Entrée`, et c'était délibéré.**
`DF-B` valide sur `Entrée`/`Done`, **jamais au `blur`**, et la prose du code
dit pourquoi : *« un blur part quand on touche l'écran ailleurs, quand le
clavier se referme, quand on veut juste relire — ce n'est pas une intention de
valider, et enregistrer là surprendrait »*. C'est `D9`/`D10`, versionné.

Valider **dès que les deux champs portent une valeur** est un troisième
déclencheur, et il a un défaut mécanique : en tapant `82` alors que les reps
sont déjà saisies, la série partirait sur le `8`. Il faut donc un
temporisateur ou un déclencheur sur le second champ — donc une règle, pas une
évidence.

**2. Supprimer la commande casserait le sans-JS.** Sans JavaScript, il n'y a
aucun autre moyen d'enregistrer. **Mais la sortie existe** : `nav=next` et
`nav=stay` persistent tous deux avant de naviguer. Donc le bouton peut
**changer de nom** — « SÉRIE SUIVANTE → » plutôt que « VALIDER SÉRIE 1 » — sans
être supprimé. `R6` est satisfait par le renommage ; la suppression, non.

### ✅ Arbitrages opérateur — 2026-09-04

| | Décision |
|---|---|
| **`R5` = `C`** | **Valider au `change` du SECOND champ.** L'événement ne part que si la valeur a changé : jamais sur une relecture, jamais en cours de frappe, aucun temporisateur à régler. Respecte le motif de `D9`/`D10` sans en garder la lettre — et **`D9`/`D10` sont donc amendés**, ce qui doit être écrit au relevé, pas seulement fait |
| **`R6`** | satisfait par le **renommage**. Le bouton reste : c'est le seul chemin d'enregistrement sans JavaScript |
| **`R1` = `C`** | **Réglette d'instrument** — pleine largeur, **encastrée dans le châssis**, chevron directionnel. Un contrôle physique, pas un bouton web. Le trait est abandonné |
| **`R2`** | ✅ **fait** — la suggestion du moteur existait déjà et avait été enterrée par la première version du readout (15 px, et un token non-texte). Rendue lisible à 26 px |

> ⚠ `R1 = C` a une conséquence à ne pas manquer : une réglette **encastrée**
> utilise `--relief-carved`. Or le puits de saisie l'utilise aussi. Deux
> objets creusés voisins peuvent cesser de se distinguer — à vérifier **sur
> rendu**, pas en raisonnant.

### ✅ Cinq arbitrages de suivi — 2026-09-04

| | Décision |
|---|---|
| **`Q-A` = `C`** (`R9`) | Un seul panneau **RECOMMANDATION** fusionne *ce que le moteur propose* et *comment bien exécuter*. Le contrat `S-00` place les deux au rang 2 ; un seul contrôle les sert. Le mot « technique » disparaît |
| **`Q-B` = `C`** (`R4`) | « EXERCICE SUIVANT » en libellé, **le nom en sous-ligne** (`dock__sub`, déjà utilisé par « → repos 90 s »). Un nom comme « Neutral Grip Shoulder Press machine » casse un libellé et devient illisible tronqué |
| **`Q-C` = `B`** (`R3`) | « Sauter l'échauffement » est une **pure navigation** : elle va à la première série de travail et **n'écrit rien**. Marquer les échauffements comme faits fabriquerait des données d'entraînement non produites |
| **`Q-D` = `B`** (`R7`) | Les exercices en attente deviennent un **fil d'état** compact (`S-02`). ⚠ **C'est une soustraction** : `§5.3` exige que le fil reprenne ce que les cartes portaient — « dernière fois » et l'avancement — pas qu'il les efface |
| **`Q-E` = `C`** (`R8`) | Le bandeau garde **le code + la zone dominante** (« PUSH A · PECTORAUX »). « Pecs épaisseur + Delts + Triceps » est un nom de gabarit, pas une information de séance |

**Ordre d'exécution retenu** : `R4` + `R9` + `Q-C` + `Q-E` (intelligibilité) →
`R1` réglette → `R5` validation au `change` → `Q-D` fil d'état.

---

| ID | Question | Dépend de | Statut |
|---|---|---|---|
| `S-01` | L'exercice actif prend-il **la surface entière**, ou reste-t-il un objet dans une liste ? | `L-01` `L-07` | ✅ **surface entière** (M3) |
| `S-02` | Que devient la **liste des sept exercices** — indicateur de position, navigation, ou disparition ? | `S-01` | ✅ **fil d'état**, rang 2 |
| `S-03` | La saisie : **champs**, **manipulation directe**, ou **confirmation d'une proposition** ? | `L-01` `L-06` | ✅ **manipulation directe** |
| `S-04` | Le repos : **minuteur**, **état de l'instrument**, ou **intervalle dans la liste des séries** ? | `S-01` `L-06` | ✅ **état de l'instrument** |
| `S-05` | L'**historique** de l'exercice mérite-t-il d'exister pendant l'effort ? | `L-05` | ✅ **la dernière fois seule**, rang 1 |
| `S-06` | « Adapter » : bouton, **action contextuelle du titre**, ou geste ? | `S-01` | ✅ **affordance du titre** |
| `S-07` | La commande dominante : **bouton**, **ligne instrumentale**, ou **zone tactile sans chrome** ? | `L-01` `L-07` | ✅ **trait instrumental** |
| `S-08` | Que voit-on **entre deux exercices** — transition, rien, ou récapitulatif ? | `S-01` `L-06` | ⬜ ouvert |
| `S-09` | « Terminer la séance » : même registre que les autres commandes, ou **traitement terminal distinct** ? | `S-07` | ⬜ ouvert |
| `S-10` | Le **cardio** et le **bilan** en fin de page : ici, ailleurs, ou supprimés de la Séance ? | `S-02` | ⬜ ouvert |
| `S-11` | ⚠ **Point neuf, ouvert par `P-03`** : l'état `cs.is_correcting` (correction d'une série déjà enregistrée) **n'a aucune représentation** dans le viseur validé. Quatrième état, ou variante de `V2` ? | `S-03` | ⬜ ouvert |

---

# `BLOC 2` — L'ACCUEIL

| ID | Question | Dépend de |
|---|---|---|
| `H-01` | L'accueil répond-il à **une** question (« que fais-je maintenant ») ou à deux (« … et où j'en suis ») ? | `L-04` |
| `H-02` | `DÉMARRER` : bouton géant, **ligne instrumentale**, ou la séance elle-même est le contrôle ? | `L-01` `S-07` |
| `H-03` | La **cause causale** (zones visées) reste-t-elle visible sans geste ? | `L-05` |
| `H-04` | Le **bilan 11 zones** : accueil, enfant de Progression, ou les deux ? | `H-01` |
| `H-05` | « Écarté, et pourquoi » : visible, replié, ou supprimé ? | `L-05` |
| `H-06` | « État du jour » : carte, ligne, ou question posée au moment utile (`UX4_01`) ? | `L-01` |
| `H-07` | « Choisir une autre séance » : quelle forme pour un **tertiaire découvrable** ? | `S-07` |

---

# `BLOC 3` — LES SURFACES DE LECTURE

> Progression · fin de séance · historique. **Le domaine où la carte a le plus
> proliféré** — 7, 7 et 12 occurrences.

| ID | Question | Dépend de |
|---|---|---|
| `R-01` | Progression répond-elle à **une** question, ou reste-t-elle un hub ? | `L-04` |
| `R-02` | La fin de séance : **document** de récapitulatif, ou **instrument** de clôture ? | `L-01` |
| `R-03` | ⚠ **DÉFAUT RÉEL, vérifié au code le 2026-09-04.** Le CTA primaire de fin de séance est `url_for('dashboard')` — `session_done.html:245` — qui atteint `/dashboard`, route **dépréciée** rendant un `303` vers `/progress` (`pages.py:954-982`). Le geste le plus probable après une séance traverse une redirection. Quelle est la bonne destination ? | `R-02` |
| `R-04` | L'historique : liste de lignes, ou objets consultables ? | `L-05` |
| `R-05` | Les **11 zones** : où vivent-elles ? ⚠ **J'avais écrit « rend 404 » — c'est FAUX, vérifié le 2026-09-04.** `/progress/body` n'a **aucune route**, et `profile.html:374` documente que le lien n'a **délibérément pas été posé** pour cette raison. Aucun 404 n'est livré : c'est un **écart spec↔implémentation**, pas un lien cassé. | `H-04` |
| `R-06` | Que fait-on des **métriques dont personne n'a demandé la lecture** — score global, grades, ratios ? | `L-04` |

---

# `BLOC 4` — LES SURFACES DE POSSESSION

> Programmes · Plan · Explorer · Profil.

| ID | Question | Dépend de |
|---|---|---|
| `O-01` | La porte du domaine « Programmes » — **arbitrage `U-01` toujours ouvert**, options `A`/`B`/`C+` rendues | — |
| `O-02` | Le Profil : formulaire, ou **état lisible** dont « Mettre à jour » ouvre une acquisition guidée (`UX4_01`) ? | `L-01` |
| `O-03` | Quelles données du Profil **méritent encore d'être demandées** ? L'audit `UX4_01` est prescrit et non fait | `O-02` |
| `O-04` | Explorer : catalogue, ou **corpus contextualisé** (`UX4_02`) ? | `O-01` |
| `O-05` | « Mon plan » : surface propre, ou vue du Profil ? | `O-01` `O-02` |

---

# `BLOC 5` — LES SEUILS

> Login · inscription · accueil public · états vides · erreurs.
> **Surfaces à faible prestige, premières vues par un nouvel utilisateur.**

| ID | Question | Dépend de |
|---|---|---|
| `T-01` | Le login : **sas**, **porte qui se souvient**, ou **pas de surface de login** (identité demandée au moment utile) ? | `L-01` `L-04` |
| `T-02` | Le nom « Auren » doit-il **apparaître à l'écran** au seuil ? Il n'est aujourd'hui que dans le `<title>` | `T-01` |
| `T-03` | Les **trois liens de poids égal** du login : hiérarchie, ou suppression ? Le « ← Retour » **mène ailleurs** | `T-01` |
| `T-04` | L'inscription : même sas, ou chemin distinct ? | `T-01` |
| `T-05` | Un **état vide** est-il un échec ou un point de départ ? *(vu au lab `U-01` : « Aucun programme personnel » sur écran nu)* | `L-04` |
| `T-06` | Une **erreur** : bandeau, champ, ou instrument qui refuse ? | `L-04` |

---

# `BLOC 6` — LA COQUE

| ID | Question | Dépend de |
|---|---|---|
| `N-01` | **Quatre destinations primaires** : est-ce le bon nombre, et les bonnes ? | `BLOC 2`–`4` |
| `N-02` | Les **9 destinations derrière `☰`** — rendu **trois fois** : que mérite d'être atteignable plutôt que simplement accessible ? | `N-01` |
| `N-03` | La coque doit-elle **disparaître pendant la séance** ? | `S-01` | ⚠ **pré-tranché par `P-03`** — le viseur occupe la surface entière et n'a montré aucune coque. **À confirmer explicitement**, car c'est une soustraction (`CLAUDE.md §5.3`) |
| `N-04` | Le **poids de trait** des 8 icônes de coque. ⚠ **J'avais écrit « diverge du contrat » — c'est FAUX, vérifié le 2026-09-04.** `Sx_ASSET_02 §50` **documente `1.7` pour la coque**, `§42/§146` documentent `2` pour le subset vendeur, et **`§208` diffère explicitement la valeur canonique « au build »**. Le dépôt est fidèle à sa spec ; **c'est la valeur qui n'a jamais été tranchée.** | `L-02` |

---

# `BLOC 7` — LES PRIMITIVES TRANSVERSES

> Ne se décident qu'**après** avoir vu les objets réels. Les figer d'abord
> reproduirait l'erreur que ce pass corrige.

| ID | Question | Dépend de |
|---|---|---|
| `X-01` | **La carte survit-elle ?** `A` partout · `B` l'information d'abord · `C` deux primitives, `groupe` et `objet` | `L-07` `S-01` `R-02` |
| `X-02` | Le motif `<details>` — **52 occurrences** : disclosure, ou autre chose ? | `L-05` |
| `X-03` | Un **readout** est-il une primitive ? *(46 px du repos, KPI, delta, dernière fois)* | `S-04` `R-06` | ⚠ **pré-tranché par `P-03`** — le readout souverain y est la primitive dominante. Reste à décider s'il **vaut hors séance** |
| `X-04` | Le **secondaire** : bouton allégé, lien, ou zone tactile sans chrome ? | `S-07` |
| `X-05` | Le **titre de bloc** survit-il comme primitive de texte, ou l'instrument se passe-t-il de titres ? | `X-01` |

---

## 🌙 PASSE DE NUIT — 2026-09-04 / 05, en autonomie

> Mandat opérateur : *« tu fais le critical pass de toute la nuit… la même
> philosophie sur tous les objets… je regarderai le résultat demain matin »*,
> avec `GO MERGE` explicite et l'autorisation de prendre mes recommandations
> comme décisions.

### Ce qui a été mergé

`#183` socle de rôles · `#184` relief et grain · `#185` profondeur de la
séance. Gate complet vérifié avant chacun : checks verts, Sonar `OK`, 0 fil
non résolu, `mergeable CLEAN`, head épinglé. Aucun squash, aucun `--admin`,
aucune branche supprimée — le cleanup reste séparé.

### Défauts trouvés EN REGARDANT, que 5 000 gardes ne voyaient pas

| Défaut | Surface | Nature |
|---|---|---|
| **« En cours · depuis 1502 h 16 »** | accueil | `format_duration_short` n'avait aucune borne haute. Format juste, nombre exact, illisible. Corrigé : au-delà de 24 h, on rend des **jours** |
| **`min-height: 50vh` survivant** | accueil | `Q5` a retiré le `min-height` de la règle de base **et l'a laissé dans la requête média mobile** — la seule qui s'applique à la cible qu'il citait. Le vide avait **augmenté** : 115 → 152 px. Hero 422 → 288 px |
| **« ANOMALIE None »** | progression | `_pick_top_anomaly` lisait **quatre attributs qui n'existent pas** sur `Anomaly`. Les `getattr(..., None)` rendaient l'absence silencieuse. Toute anomalie affichée l'a été sous le nom « None » |
| **« 1 sessions »** | progression | accord manquant **et** anglicisme. Le commentaire du test disait : *« kept "sessions" so the existing assertions stay valid »* — **le défaut a survécu parce qu'un test l'épinglait** |
| **`/rules` → 301 → `/science`** | séance | second lien vivant traversant une redirection héritée, après `R-03`. Deux occurrences font un motif |

### Deux fausses alertes, écartées après vérification

`/profile` 500 et `/body` 404 : la première vient de **ma copie de base**
(antérieure à une migration), la seconde est le comportement **correct** d'une
surface derrière un drapeau éteint. Ni l'une ni l'autre n'est un défaut
produit. ⚠ **Le profil n'a donc pas pu être revu** — c'est le seul trou de la
revue, et il est dit.

### Leçons de méthode, payées

* **Un filtre `-k` est une hypothèse sur le rayon d'impact.** La mienne était
  fausse : six gardes sont tombées en CI, dans des fichiers que mon filtre ne
  couvrait pas. Sur du `shared_code`, c'est le sweep complet qui tranche.
* **Un laboratoire non représentatif fait juger un écran que la donnée rend
  absurde.** Progression semblait être « cinq blocs qui disent rien » — c'était
  ma base, vieille de 62 jours. Avec de la donnée récente, plus une seule ligne
  vide, et deux vrais défauts apparaissent à la place.
* **Ne pas muter l'arbre pendant qu'un sweep le lit.** Je l'ai fait, le verdict
  devenait ininterprétable, et j'ai arrêté le sweep plutôt que de garder son
  résultat.

### 🔴 `D7-RESTE` — une décision opérateur appliquée sur 2 surfaces, oubliée sur 4

Trouvé en balayant les **classes** de défaut plutôt que les écrans. C'est le
défaut le plus sérieux de la nuit, parce qu'il ne s'agit pas d'un oubli de
style : **une décision que vous avez prise n'a été appliquée que là où c'était
commode.**

`OPERATOR_DECISION D7` (`UX4_03B`) a retiré « Streak ». Le commentaire qui la
consigne donne deux motifs, et le premier est un motif **produit** :

> « Le compteur de jours consécutifs **punissait un jour de repos correctement
> pris**, et venait d'un second producteur aux règles différentes de celui du
> moteur comportemental. »

Elle a été appliquée à **deux** surfaces — le rapport coach (remplacé par
« Séances 14 j ») et Progression (`DO_NOT_SURFACE`). Elle est restée **non
appliquée sur quatre** :

| Surface | Ce qui est encore rendu |
|---|---|
| `squad_detail.html:21` | colonne `Streak`, valeur `{{ e.streak }}j` |
| `squad_compare.html:47` | ligne `Streak`, deux valeurs comparées |
| `_partials/profile_preview.html:28` | KPI `Streak` |
| `user_profile.html:43` | KPI `Streak` |

Trois aggravations, dans l'ordre de gravité :

1. **Le motif produit est *pire* là où la décision n'a pas été appliquée.** Un
   compteur qui punit un repos bien pris est discutable sur une page privée ; sur
   un **classement d'escouade**, il fait du repos un désavantage compétitif
   **devant les autres**. La décision a été appliquée aux surfaces intimes et
   oubliée sur les surfaces sociales — exactement l'inverse de l'ordre de
   priorité.
2. **Les deux gardes de D7 existent — et ne regardent qu'un gabarit chacune.**
   `test_coach_report.py:271` bannit `"Streak"` du rapport coach ;
   `test_ux4_progress_signals.py:518` le bannit de `/progress`. Aucune ne
   regarde les quatre autres. Même motif que les gardes aveugles par périmètre
   déjà relevées cette nuit : **la garde existe, elle ne regarde pas où est le
   défaut.**
3. **Il y a bien trois producteurs, comme la décision le soupçonnait** —
   `behavioral.BehavioralState.streak_days` (délibérément conservé, gardé par
   `test_streak_days_is_still_computed`), `profile_metrics.streak_days` et
   `squad._compute_streak`. La décision nommait « un second producteur » ; il y
   en avait un troisième.

Vérifié : `streak` **ne pèse pas** sur le classement — le rang se calcule sur
les points. La retirer ne change aucun ordre.

#### La preuve, mesurée par le code du produit

Trois pratiquants construits dans un laboratoire au schéma courant, puis les
**vrais producteurs** du dépôt appelés dessus :

| | « Streak » affiché | Séances sur 14 j | Rang |
|---|---|---|---|
| **marin** — *se repose correctement* | **1 j** | **6** | 1er, 600 pts |
| **nadia** — *enchaîne les jours consécutifs* | **5 j** | 5 | 2e, 480 pts |
| come — *reprise après coupure* | 0 j | 3 | 3e, 300 pts |

**Marin s'entraîne le plus, il est premier au classement, et la dernière chose
qu'on lit sur sa ligne est « 1j » contre « 5j » pour nadia** — parce qu'il prend
ses jours de repos. C'est exactement la phrase de la décision, devenue un
nombre, sur un écran public.

Vérifié au rendu : `/squads/1` et `/users/nadia` affichent « Streak ».

**✅ LIVRÉ — PR `#189`.** D7 appliquée à la lettre — « remplacé par un
comptage » — avec **un seul producteur** au lieu de trois, en promouvant le
compteur déjà écrit et propre (`coach_report._sessions_in_window`) au rang de
producteur partagé. Le moteur comportemental garde le sien, qui est gardé et
n'est pas rendu.

Deux précisions que l'implémentation a apportées :

* **Les deux producteurs d'affichage ne calculaient pas la même chose.**
  `squad._compute_streak` partait strictement d'aujourd'hui ;
  `profile_metrics.streak_days` accordait un délai de grâce jusqu'à la veille
  pour ne pas perdre une suite avant minuit UTC. **Deux nombres différents pour
  le même utilisateur, le même jour** — l'un sur le classement, l'autre sur la
  carte de profil. La décision disait « aux règles différentes » ; c'était
  littéral.
* **`profile_metrics` portait aussi deux copies du prédicat d'éligibilité**
  (« terminée, non exclue, dans la fenêtre »), l'une pour compter, l'autre pour
  charger les exercices. Extraites en une. Même faute, un cran plus bas.

La garde ajoutée est **universelle par construction** — sa liste vient d'un
`rglob`, pas d'une énumération — et interdit aussi de **lire** `.streak`, sans
quoi une colonne renommée « Constance » rendrait la même valeur.

S'y ajoute, dans la même tranche, le reste du vocabulaire : **neuf libellés
« Sessions… »** encore rendus sur `export`, `coach_report`, `profile_preview` et
`user_profile` — l'anglicisme déjà corrigé sur Progression, resté partout
ailleurs. Y compris **deux lignes au-dessus du commentaire de D7** qui affirme
« même vocabulaire que Progression ».

### 🔴 `X-06` — une seconde palette, non mesurée, vit à côté de la vôtre

Trouvé en balayant §5.4 sur les feuilles de style plutôt que sur les gabarits.
C'est la trouvaille la plus lourde de la nuit **en volume**, et elle est
entièrement chiffrée.

**30 couleurs littérales distinctes, 88 occurrences**, rendues **hors du système
de tokens**, réparties sur `app.css` (50), `body_intelligence.css` (23) et
`session_focus.css` (15).

Ce n'est pas une dispersion aléatoire. C'est **la palette par défaut de
Tailwind**, reconnaissable nuance par nuance :

| Littéral | Nom Tailwind | Saturation | ×  |
|---|---|---|---|
| `#6b7280` | `gray-500` | 9 % | 25 |
| `#4a9eff` | — (bleu électrique) | **100 %** | 5 |
| `#2563eb` | `blue-600` | 83 % | 5 |
| `#f59e0b` | `amber-500` | 92 % | 4 |
| `#d97706` | `amber-600` | 95 % | 4 |
| `#92400e` | `amber-800` | 82 % | 4 |
| `#166534` | `green-800` | 64 % | 4 |
| `#4ade80` | `green-400` | 69 % | 3 |
| `#16a34a` | `green-600` | 76 % | 2 |

**La mesure qui tranche** — la palette que vous avez validée et qui est écrite
dans la feuille vit entre **20 % et 51 % de saturation** :

```
--role-support-success      #6E9E7A   S 20 %
--role-support-information  #7695AD   S 25 %
--role-support-error        #C67D7D   S 39 %
--role-support-warning      #C97F59   S 51 %
```

Onze des couleurs clandestines sont à **S ≥ 56 %**, jusqu'à **100 %**. Sur un
tableau de bord sombre, ce n'est pas une nuance différente : c'est un registre
différent. `.trend--up` rend un vert néon `#4ade80` à dix pixels d'une palette
qui dit sauge `#6E9E7A`.

**Cinq tokens n'existent nulle part** — leur repli est donc littéralement ce que
le produit rend, et §5.4 nomme exactement ce piège (« le repli masque
l'absence ») :

| Token invoqué | Ce qui est réellement rendu | Où |
|---|---|---|
| `--bg-soft` | `rgba(255,255,255,0.02)` ×3 | `app.css` |
| `--bg-elev` | `rgba(0,0,0,0.02)` ×3 | `body_intelligence.css` |
| `--good` | `#4ade80` ×1 | `app.css` — `.trend--up`, surface **sociale** |
| `--warn-soft` | `rgba(224,160,48,0.18)` | `app.css` |
| `--danger-soft` | `rgba(230,80,80,0.18)` | `app.css` |

`--bg-elev → rgba(0,0,0,0.02)` mérite un mot : c'est un film **noir à 2 %** posé
pour produire une élévation, sur un produit **sombre**. L'élévation qu'il
prétend créer est invisible par construction. Il a été écrit pour un thème
clair. Même origine que les 25 `#6b7280`, gris de thème clair.

**Ce que je n'ai PAS fait, et pourquoi.** Je n'ai pas remplacé les 88. Elles
vivent sur le rapport coach, le score breakdown et `body_intelligence` —
**des surfaces que vous n'avez pas vues et que je n'ai pas revues**. §5.1 exige
une exposition avant tout commit UI, et §5.5 dit que la centralité prime : une
décision opérateur non appliquée (`D7`) passe devant une refonte chromatique que
j'aurais choisie seul. Le recensement est le livrable ; l'arbitrage est le vôtre.

⚠ `body_intelligence.css` sert une surface **derrière un drapeau éteint**
(`/body` rend 404, comportement correct). Ses 23 littéraux sont donc **latents**,
pas visibles aujourd'hui — mais ils s'allumeront avec le drapeau.

### ✅ `O-06` — le profil est revu. Le trou de la revue est fermé.

La revue de nuit s'arrêtait sur un aveu : *« le profil n'a pas pu être revu »*.
La cause n'était pas le produit mais **mon laboratoire**, dont la base précédait
la migration `body_measurements.shoulder_width_cm` — d'où un 500.

Reconstruit **au schéma courant** en démarrant l'application sur une base vide :
elle crée son schéma et amorce son catalogue par ses propres moyens (30 tables,
102 exercices, 17 gabarits). Ni `alembic upgrade`, ni `seed_db.py` — les deux
sont sous confirmation humaine. Aucune base de production lue ni écrite.

`/profile` rend **200**. Trois constats, du plus objectif au plus discutable :

1. **« Tape à plat, muscle relâché »** — `profile.html:163`. C'est l'anglais
   *tape* (mètre ruban) laissé dans une phrase d'impératifs français
   (« Mesurer le matin, à jeun… »). On lit le verbe *taper*. La consigne dit
   littéralement de frapper à plat. Correction : « **Mètre ruban** à plat ».
2. **Quatre liens « Ajouter », deux destinations** (`#quicklog_weight`,
   `#reference_data`). Mesuré au rendu, pas déduit. Dans une liste de liens de
   lecteur d'écran, ils sont indiscernables ; à l'œil aussi, hors contexte de
   ligne.
3. **La carte alterne sans règle — et c'est `Q5` qui est violée, nommément.**
   `CORPS` est dans une carte, `COMPTE` non, `NOUVELLE MESURE` oui, `MESURES
   MORPHOLOGIQUES` non, `DONNÉES DE RÉFÉRENCE` oui. Un bloc sur deux.

   `DESIGN_DECISIONS_UIV2_SURFACES.md §Q5` tranche pourtant : trois rangs —
   **actionnable** (carte bordée), **informatif** (filet), **ambiant** (aucun
   conteneur) — et conclut : *« La carte redevient un signal, pas un décor. »*

   Sur `/profile`, la carte n'est ni l'un ni l'autre : elle **alterne**. `COMPTE`
   (utilisateur, e-mail, date d'inscription, statut) est du rang 2 informatif et
   n'a pas de carte — correct. `CORPS`, qui contient quatre liens d'action et un
   champ de saisie, en a une — correct aussi. Mais `MESURES MORPHOLOGIQUES`, un
   état vide, n'en a pas, tandis que `NOUVELLE MESURE`, qui n'est qu'un bloc de
   consigne replié, en a une. La règle est là ; elle n'est pas appliquée.

### 🔎 `O-07` — l'escouade n'a jamais reçu le traitement

Vue au rendu pour la première fois. Outre `D7` :

* **Le `<select>` de partage est blanc pur** — contrôle de formulaire non stylé,
  hérité du navigateur. C'est **l'objet le plus lumineux de tout l'écran**, et
  ce n'est pas l'action principale. Défaut objectif, pas un choix de goût.
* **« Zone danger »** — calque de *danger zone*. Le français dit « zone de
  danger », ou mieux ici : « Actions irréversibles ».
* **« owner » / « member »** — les badges de rôle ne sont pas traduits.
* Le tableau de classement à 5 colonnes **se replie mal** en 430 px : « 600.0
  pts » passe sur deux lignes, les libellés de grade sur trois.

⚠ **Décisions de NOMMAGE, donc les vôtres** — je ne les ai pas prises :
« squad » (« Supprimer la squad », « Retour aux squads »), « Challenges »,
« template » (« Recommander un template »). Ce sont des noms de
fonctionnalité, pas des fautes ; les renommer est un choix produit.

⚠ **Un chevauchement que je n'ai PAS rapporté** : sur la capture pleine page,
la barre de navigation basse paraît recouvrir un formulaire. Vérifié au
viewport et en CSS — `main` porte `padding-bottom: 96px`, la barre est
compensée. C'était un artefact de capture d'un élément `fixed`, le même que
celui déjà rencontré cette nuit. Le signaler aurait coûté une correction
inutile sur un défaut inexistant.

---

## Compte des points ouverts

**Recompté le 2026-09-04**, après `BLOC 0` et `P-03`. Le total passe de 52 à
**53** : `P-03` a fermé 7 points et **en a ouvert un** (`S-11`, `is_correcting`).
Un point ouvert par la matérialisation vaut mieux qu'un point jamais posé.

| Bloc | Total | Fermés | **Ouverts** |
|---|---|---|---|
| `BLOC 0` langage et intention | 9 | 9 | **0** |
| `BLOC 1` séance | 11 | 7 | **4** — `S-08` `S-09` `S-10` `S-11` |
| `BLOC 2` accueil | 7 | 0 | **7** |
| `BLOC 3` lecture | 6 | 0 | **6** |
| `BLOC 4` possession | 5 | 0 | **5** |
| `BLOC 5` seuils | 6 | 0 | **6** |
| `BLOC 6` coque | 4 | 0 | **4** — dont `N-03` pré-tranché |
| `BLOC 7` primitives | 5 | 0 | **5** — dont `X-03` pré-tranché |
| **TOTAL** | **53** | **16** | **37** |

**Le socle est écrit** — `AUREN_VISUAL_BACKBONE`. Les 37 points restants
décident **où il s'applique**, plus jamais **ce qu'il est**.

## Ce que ce backlog garantit

* Aucun contrat n'est écrit sur une intention supposée.
* Aucun point n'est arbitré avant ceux dont il dépend.
* Les 79 objets du registre trouvent chacun **au moins un point** qui décide de
  leur sort — et un objet sans point ouvert est un objet dont la responsabilité
  et la métaphore sont déjà tranchées.
