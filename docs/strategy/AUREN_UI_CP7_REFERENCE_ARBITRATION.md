# `UI-CP7 REFERENCE` — brief d'arbitrage

> **Ouvert le 2026-09-22**, après le merge de `UI-CP6 SHELL` (`81f9c01`).
>
> `UI-CP6` a **classé** les surfaces de document. `UI-CP7` décide à quoi un
> document doit **ressembler**. Ce brief mesure, sépare ce qui va de ce qui
> coûte, et pose **quatre questions fermées**. Rien ne bouge avant l'arbitrage.

---

## 0. La règle qui gouverne cette tranche

`AUREN_INSTRUMENTS §2bis`, mot pour mot :

> **« Un document ne doit jamais avoir l'air d'un instrument en panne. »**
> « La frontière doit être **perceptible** : un document se présente comme un
> document, pas comme un cockpit vide de données. »

C'est le seul critère d'acceptation qui compte. Tout ce qui suit le mesure.

---

## 1. Les quatre surfaces, mesurées

390 × 844, sur **deux comptes** : `pilote` (21 séances) et `pilote-neuf`
(aucune). La comparaison dit si la surface **varie avec les données**.

| Surface | mots | écrans | conteneurs | `.card` | `<details>` | varie avec les données |
|---|---|---|---|---|---|---|
| `/science` | 1 526 | **12,0** | 43 | **18** | 6 | **non** — identique aux deux comptes |
| `/science/atlas` | 2 074 | **15,5** | **105** | **32** | **0** | **non** — identique aux deux comptes |
| `/coach-report` | 489 → 437 | 3,9 → 3,5 | 59 → 44 | 0 | 0 | **oui** |
| `/export` | 100 → 94 | 1,5 → 1,4 | 11 → 9 | 3 | 0 | **un peu** |

**Aucune des quatre ne porte de relevé souverain ni de rail.** Elles ne
prétendent pas être des instruments — c'est déjà un acquis, et une tranche
`REFERENCE` ne doit pas le défaire.

---

## 2. Ce qui va déjà

| Acquis | Mesure |
|---|---|
| Aucune grammaire de cockpit empruntée (relevé, rail, cadre de focus) | **0** sur les quatre |
| `/science` et `/atlas` ne varient pas avec les données — c'est CORRECT pour une référence | sortie identique sur un compte vide et un compte peuplé |
| `/coach-report` varie, et c'est correct aussi : c'est un document **sur** l'utilisateur | 489 vs 437 mots |
| Classement `DOCUMENT` en place, sans coût vertical supplémentaire | `UI-CP6`, mergé |
| Aucun débordement horizontal | **0** sur les quatre |

⚠ **La non-variation est le critère qui a condamné `/physique`** — 349 mots sur
un compte vide, 369 sur un compte peuplé. Pour un **instrument** c'est une
condamnation ; pour une **référence** c'est la définition. Le même chiffre
change de sens selon la classe, et c'est exactement pourquoi la classification
de `UI-CP6` devait précéder cette tranche.

---

## 3. Ce qui coûte

### F1 — `/science/atlas` fait 15,5 écrans et rien ne s'y replie

> ⚠ **CORRECTION, 2026-09-24.** Cette section affirmait que l'atlas n'a
> « AUCUNE navigation interne ». **C'est faux**, et je l'ai découvert en ouvrant
> `atlas.html` au lieu de relire ma propre note.
>
> `atlas.html:6-10` porte un `<nav class="atlas-toc">` avec **une ancre par
> famille**, et `app.css:4679` le rend en pastilles visibles. Le sommaire ancré
> que la `Q3` propose de construire **existe déjà**.
>
> Ce qui manque réellement est le **repli** : `<details>` n'apparaît nulle part
> dans l'atlas, donc les 2 074 mots restent dépliés en permanence.
>
> Conséquence sur l'arbitrage : `Q3 = A` reste la bonne réponse, mais **la
> moitié du travail est faite**. La tranche ajoute le repli et corrige le
> sommaire, elle ne le crée pas.
>
> ⚠ Relevé au passage, **à mesurer au runtime avant d'affirmer** :
> `.atlas-toc__item` déclare `font-size: 12px` et `padding: 4px 10px`, ce qui
> place sa hauteur bien sous le plancher tactile produit de 44 px établi par
> `UI-CP5`. Une déclaration CSS n'est pas une géométrie rendue — c'est
> exactement l'erreur que la cible de 18 px m'avait déjà value.

2 074 mots, 105 conteneurs, **32 cartes**, et **zéro `<details>`** : tout est
déplié en permanence. Une référence anatomique de quinze écrans qu'on ne peut
pas replier ne se consulte pas, elle se subit.

`/science` fait 12 écrans avec 6 divulgations — mieux, mais du même ordre.

### F2 — 50 cartes au total empruntent la grammaire du cockpit

`.card` est le conteneur de **rang 1** du socle (`Q5` : « carte bordée, fond
plus présent · séance recommandée, exercice actif, formulaire ouvert »). Un
document fait de 32 cartes se lit comme un tableau de bord.

C'est précisément « avoir l'air d'un instrument » — pas en panne, mais
emprunté.

### F3 — La plus grosse typographie est 22 px, sur douze écrans

Rang `SECTION` partout. Un document de 1 500 à 2 000 mots n'a **aucun** rang
au-dessus de ses titres de section : ni titre de document, ni hiérarchie de
lecture. L'échelle `Q6` réserve le rang `DISPLAY` (32 px) au « relevé souverain
**ou au titre d'écran** » — la seconde moitié n'est utilisée nulle part ici.

### F4 — Un seul document sur quatre est imprimable

`coach_report` porte un bouton Imprimer et des règles `@media print`. Les trois
autres n'en ont aucune. Or `/coach-report` est décrit dans le dépôt comme
« un document à présenter à un coach externe » — et c'est le seul dont
l'intention d'impression ait été traitée.

### F5 — Le pied de page, explicitement reporté par `UI-CP6`

Il coûte **135 px sur mobile** et porte un mot-marque plus un lien que la
navigation secondaire offre déjà. `UI-CP6 Q3` l'a laissé sur les documents
**temporairement, sur instruction**, en nommant `UI-CP7` comme son propriétaire.

---

## 4. Les quatre questions

### Q1 — Qu'est-ce qui rend un document PERCEPTIBLEMENT un document ?

| | |
|---|---|
| **A** | **Une tête de document** — titre au rang `DISPLAY` (32 px), sous-titre de provenance, date. C'est la moitié inutilisée de `Q6`, et elle distingue immédiatement un document d'un instrument, qui réserve ce rang à un **relevé mesuré**. |
| **B** | **Une colonne de lecture** — largeur de ligne bornée (~65 caractères), typographie de prose, pas de conteneur. La différence se lit à la forme du texte, pas à un ornement. |
| **C** | **Les deux.** |

**Ma recommandation : C**, et dans cet ordre — la tête d'abord, parce qu'elle
est visible sans défiler et qu'elle est ce que `Q6` réserve déjà.

⚠ Ce que je **ne** recommande pas : une couleur, une bordure ou un fond
spécifique aux documents. Ce serait un cinquième dialecte visuel, et
`AUREN_INSTRUMENTS` en accepte **deux**, pas trois.

### Q2 — Les 50 cartes des surfaces `/science`

| | |
|---|---|
| **A** | **Les retirer** — la prose et l'espace suffisent (`Q5`, rang 3 : « aucun conteneur »). |
| **B** | **Les remplacer** par une grammaire de document : filets de séparation, titres, listes de définition. |
| **C** | **Les garder** — la carte est le conteneur du produit, y compris ici. |

**Ma recommandation : B.** `A` seul serait une soustraction nue sur 2 000 mots
et rendrait l'atlas illisible ; `C` maintient l'emprunt que `§2bis` interdit.

### Q3 — Les quinze écrans de l'atlas

| | |
|---|---|
| **A** | **Un sommaire ancré** en tête, plus un repli par zone (`<details>` natif, comme `/science` en a déjà six). |
| **B** | **Une page par zone**, avec un index. Change les routes. |
| **C** | **Ne rien changer** — une référence se parcourt au défilement. |

**Ma recommandation : A.** `B` change les routes, ce qui déborde d'une tranche
de mise en forme et casse tout lien profond existant. `A` réutilise une
primitive que le produit possède déjà et que `/science` emploie.

### Q4 — Le pied de page, et l'impression

| | |
|---|---|
| **A** | **Le pied devient une signature de document** : provenance, date de génération, et l'affordance d'impression — sur les quatre surfaces. Il cesse d'être un pied de page générique pour devenir un objet de document. |
| **B** | **Le retirer partout**, comme sur les instruments. Contact vit déjà dans la navigation secondaire. |
| **C** | **Le garder tel quel.** |

**Ma recommandation : A.** C'est la seule option qui transforme un coût en
fonction : 135 px qui portaient un doublon porteraient la provenance — ce
qu'un document doit dire et qu'aucun des quatre ne dit aujourd'hui, sauf
`coach_report` partiellement.

⚠ **Généraliser l'impression aux quatre surfaces est une extension de portée,
et je la signale plutôt que de la supposer acquise.** L'atlas et `/science` ne
sont peut-être pas destinés au papier.

---

## 5. Hors périmètre proposé

- **aucun** changement de route (donc pas de `B` en `Q3` sans arbitrage explicite) ;
- **aucune** modification du contenu éditorial des références ;
- **aucun** nouveau dialecte chromatique ;
- **aucun** JavaScript ;
- la coque elle-même — `UI-CP6` est close ;
- `/physique`, retirée, reste retirée.

---

## 6. Ce que je n'ai PAS mesuré

Honnêteté de portée :

- le rendu **à l'impression** de `coach_report` (les règles `@media print`
  existent, je ne les ai pas vérifiées sur une sortie réelle) ;
- l'atlas sur un **viewport court** et en paysage ;
- le coût de chargement des illustrations anatomiques ;
- la lisibilité réelle des 2 074 mots — c'est une question éditoriale, pas de
  mise en forme, et elle n'appartient pas à cette tranche.

---

## 7. Défaut déjà corrigé en ouvrant cette tranche

En interrogeant la table de routage plutôt qu'en relisant mon propre code,
`PREFIXES_DOCUMENT` s'est révélé contenir **deux préfixes qui ne désignent
aucune route** : `/atlas` (l'atlas vit à `/science/atlas`) et
`/coach-body-snapshot` (c'est un **partiel** inclus dans `coach_report.html`).

Cause : `§2bis` nomme des **surfaces**, j'en avais fait des **chemins d'URL**.

Inoffensif à l'exécution — un préfixe qui ne matche rien ne classe rien — mais
**ma propre garde l'assertait à vide**. Corrigé, avec une garde qui ferme la
classe en interrogeant `app.routes`. PR **#242**.
