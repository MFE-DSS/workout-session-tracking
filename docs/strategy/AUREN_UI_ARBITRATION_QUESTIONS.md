# `AUREN_UI_ARBITRATION_QUESTIONS` — les 37 points ouverts, trois options chacun

> **Méthode fixée par l'opérateur le 2026-09-04** : *« tu mets ton système de
> questionnement avec tes trois réponses proposées, c'est le recommandé, puis je
> vais trancher à chaque fois »*.
>
> **Trois options réellement distinctes. Jamais une variante de degré.** Une
> recommandation motivée en une ligne. L'opérateur tranche.
>
> Se lit **après** `AUREN_VISUAL_BACKBONE` — le socle est gravé, ces 37 points
> décident **où il s'applique**, plus jamais **ce qu'il est**.
>
> Ordre recommandé (`CLAUDE.md §5.5`, centralité avant facilité) :
> `BLOC 1` → `BLOC 2` → `BLOC 3` → `BLOC 7` → `BLOC 6` → `BLOC 4` → `BLOC 5`.

---

# `BLOC 1` — LA SÉANCE · 4 points

> 7 des 11 points sont fermés par `P-03`. Ces 4 ferment la surface souveraine.

### `S-08` — Que voit-on **entre deux exercices** ?

| | Option |
|---|---|
| **A** | **Rien** — l'instrument bascule directement sur l'exercice suivant. |
| **B** | **Un battement d'instrument** — le châssis tient le verdict de l'exercice qu'on quitte, puis bascule seul. |
| **C** | **Un palier explicite** — récapitulatif + commande « exercice suivant ». |

**→ Recommandé : `B`.** Le repos a déjà prouvé qu'un état se lit par le châssis
entier. `C` rajoute un écran, et `L-09` dit que le nombre d'écrans est le problème.

### `S-09` — « Terminer la séance » : quel registre ?

| | Option |
|---|---|
| **A** | **Même registre** que les autres commandes — un trait parmi les traits. |
| **B** | **Registre terminal distinct** — rôle `action-terminal`, geste à double détente. |
| **C** | **Pas de commande** — la séance se termine quand le dernier exercice est validé. |

**→ Recommandé : `B`.** `action-terminal` existe déjà comme rôle distinct dans
les 16. Une action irréversible ne doit pas ressembler à « série suivante ».

### `S-10` — Le **cardio** et le **bilan** de fin de page

| | Option |
|---|---|
| **A** | **Rester dans la Séance**, en bas de page. |
| **B** | **Devenir des étapes de l'instrument** — le cardio est un exercice, le bilan est l'état de clôture. |
| **C** | **Sortir** de la Séance vers `session_done`. |

**→ Recommandé : `B`.** « En bas de la page » n'existe plus dès lors que
l'instrument prend la surface entière (`S-01`).

### `S-11` — L'état `cs.is_correcting` *(point ouvert par `P-03`)*

| | Option |
|---|---|
| **A** | **Quatrième état de châssis**, avec son propre phosphore. |
| **B** | **Variante de `V2`** — le readout reprend la valeur enregistrée, un marqueur de **forme** dit « correction ». |
| **C** | **Hors instrument** — on corrige depuis l'historique, pas pendant l'effort. |

**→ Recommandé : `B`.** Corriger, c'est ressaisir. Un quatrième phosphore
dilue le code des trois états déjà validés.

---

# `BLOC 2` — L'ACCUEIL · 7 points

### `H-01` — L'accueil répond à combien de questions ?

| | Option |
|---|---|
| **A** | **Une** — « que fais-je maintenant ». |
| **B** | **Deux** — « que fais-je » **et** « où j'en suis ». |
| **C** | **Une question, une jauge** — l'action est la réponse, la **jauge d'allocation 14 jours** est le contexte permanent. |

**→ Recommandé : `C`.** C'est exactement la jauge macro que vous avez tranchée :
*« où est passée ton énergie »*, en fond permanent, sans poser de deuxième question.

### `H-02` — `DÉMARRER`

| | Option |
|---|---|
| **A** | **Bouton géant**. |
| **B** | **Ligne instrumentale** — le trait de `S-07`. |
| **C** | **La séance proposée EST le contrôle** — le châssis entier est la cible. |

**→ Recommandé : `C`.** Supprime la concurrence entre « lire la séance » et
« la démarrer », et donne la cible tactile maximale.

### `H-03` — La **cause causale** (zones visées)

| | Option |
|---|---|
| **A** | **Visible sans geste**, en texte. |
| **B** | **Repliée** derrière un disclosure. |
| **C** | **Portée par l'objet visuel** — la jauge et l'illustration la disent, pas une phrase. |

**→ Recommandé : `C`.** `L-02` : *une donnée doit être dérivée en objet visuel
quand elle peut l'être.*

### `H-04` — Le **bilan 11 zones**

| | Option |
|---|---|
| **A** | **Sur l'accueil**. |
| **B** | **Enfant de Progression**. |
| **C** | **Les deux** — résumé à l'accueil, détail dans Progression. |

**→ Recommandé : `B`.** L'accueil répond à « maintenant » ; 11 zones est de la
lecture, donc contexte `LECTURE`.

### `H-05` — « Écarté, et pourquoi »

| | Option |
|---|---|
| **A** | **Visible**. |
| **B** | **Replié** — présent, non imposé. |
| **C** | **Déplacé** dans l'explication de la séance, hors accueil. |

**→ Recommandé : `B`.** C'est la preuve que le moteur a raisonné : la supprimer
coûte la confiance, l'imposer coûte la densité.

### `H-06` — « État du jour »

| | Option |
|---|---|
| **A** | **Carte** permanente. |
| **B** | **Ligne** compacte. |
| **C** | **Question posée au moment utile** (`UX4_01`). |

**→ Recommandé : `C`.** Déjà prescrit par `UX4_01`. Un état demandé quand il
sert vaut mieux qu'un formulaire qui attend.

### `H-07` — « Choisir une autre séance » (tertiaire découvrable)

| | Option |
|---|---|
| **A** | **Lien texte**. |
| **B** | **Zone tactile sans chrome** sous le contrôle principal. |
| **C** | **Geste** sur l'instrument (balayage). |

**→ Recommandé : `B`.** `C` est invisible et casse le contrat sans-JS (`§10`).

---

# `BLOC 3` — LES SURFACES DE LECTURE · 6 points

### `R-01` — Progression : hub ou question ?

| | Option |
|---|---|
| **A** | **Hub** — porte vers les analyses. |
| **B** | **Une question** — « est-ce que je progresse ». |
| **C** | **Plusieurs instruments empilés**, un par question. |

**→ Recommandé : `B`.** Un hub est une surface qui délègue sa responsabilité.

### `R-02` — La fin de séance : document ou instrument ?

| | Option |
|---|---|
| **A** | **Document** de récapitulatif. |
| **B** | **Instrument de clôture** — le châssis affiche le verdict de la séance. |
| **C** | **Pas de surface** — retour direct à l'accueil avec confirmation. |

**→ Recommandé : `B`.** C'est le moment où l'allocation vient d'être dépensée :
`PH-01` veut qu'on le montre, pas qu'on le liste.

### `R-03` — ⚠ **DÉFAUT RÉEL** — la destination après une séance

`session_done.html:245` pointe vers `url_for('dashboard')` → `/dashboard`, route
**dépréciée** rendant un `303` vers `/progress` (`pages.py:954-982`). **Le geste le
plus probable après une séance traverse une redirection.**

| | Option |
|---|---|
| **A** | **`/progress`** — l'analytique, en direct. |
| **B** | **`/` accueil** — « quand est-ce que je m'entraîne ensuite ». |
| **C** | **Supprimer le CTA** — `session_done` est terminal, la coque suffit. |

**→ Recommandé : `B`.** Après une séance la question suivante est la prochaine
séance, pas la courbe. Dans les trois cas **la redirection disparaît**.

### `R-04` — L'historique

| | Option |
|---|---|
| **A** | **Liste de lignes**. |
| **B** | **Objets consultables**. |
| **C** | **Une jauge temporelle** + le détail à la demande. |

**→ Recommandé : `C`.** L'historique est la trace de l'allocation : c'est une
jauge avant d'être une liste.

### `R-05` — Où vivent les **11 zones** ?

*(Rectification : `/progress/body` n'a aucune route et le lien n'a
**délibérément pas** été posé — `profile.html:374`. Aucun 404 n'est livré.)*

| | Option |
|---|---|
| **A** | **Créer `/progress/body`** comme la spec l'envisageait. |
| **B** | **Section de `/progress`** — pas de route neuve. |
| **C** | **Rester** dans `body_assessment` existant. |

**→ Recommandé : `B`.** `L-09` : le problème est le nombre d'écrans.

### `R-06` — Les métriques dont personne n'a demandé la lecture

| | Option |
|---|---|
| **A** | **Garder** — score global, grades, ratios. |
| **B** | **Supprimer**. |
| **C** | **Garder celles qui alimentent une jauge d'allocation**, retirer le reste. |

**→ Recommandé : `C`.** `PH-01` est le filtre. ⚠ `§5.3` : ce retrait part dans
la **même livraison** que ce qui le remplace.

---

# `BLOC 7` — LES PRIMITIVES TRANSVERSES · 5 points

> À trancher **après** `BLOC 2` et `3` : les figer avant reproduirait l'erreur
> que ce pass corrige.

### `X-01` — **La carte survit-elle ?** *(88 occurrences)*

| | Option |
|---|---|
| **A** | **Oui, partout** — on l'habille. |
| **B** | **Non** — l'information d'abord, plus de contenant générique. |
| **C** | **Deux primitives** — `groupe` (contenant sans valeur propre) et `instrument` (objet qui porte une valeur). |

**→ Recommandé : `C`.** `P-03` l'a déjà démontré sur la séance : le châssis
remplace la carte **là où il y a une valeur**. Ailleurs, un groupe reste utile.

### `X-02` — Le motif `<details>` *(52 occurrences)*

| | Option |
|---|---|
| **A** | **Disclosure partout**, uniformisé. |
| **B** | **Supprimer** — tout est visible ou n'existe pas. |
| **C** | **Séparer deux emplois** — repli de densité (garder) vs. contenu secondaire (promouvoir ou retirer). |

**→ Recommandé : `C`.** 52 occurrences ne peuvent pas avoir une seule cause.

### `X-03` — Un **readout** est-il une primitive transverse ?

| | Option |
|---|---|
| **A** | **Séance seulement**. |
| **B** | **Primitive transverse**. |
| **C** | **Primitive transverse, avec obligation de porter une référence** (« la dernière fois », une cible, un delta). |

**→ Recommandé : `C`.** Un chiffre sans référence n'est pas un readout
d'instrument, c'est une décoration numérique.

### `X-04` — Le **secondaire**

| | Option |
|---|---|
| **A** | **Bouton allégé**. |
| **B** | **Lien**. |
| **C** | **Zone tactile sans chrome**, distincte par la **masse**, jamais par la seule couleur. |

**→ Recommandé : `C`.** Cohérent avec `§7` et avec la commande-trait de `P-03`.

### `X-05` — Le **titre de bloc** survit-il ?

| | Option |
|---|---|
| **A** | **Survit** comme primitive de texte. |
| **B** | **Disparaît** — l'instrument se nomme lui-même. |
| **C** | **Devient l'étiquette du châssis** (rôle `META`), pas un titre de corps. |

**→ Recommandé : `C`.** Règle au passage l'inversion mesurée `body 14px` /
`section-header 13px` **sans** avoir à trancher l'échelle typographique.

---

# `BLOC 6` — LA COQUE · 4 points

### `N-01` — **Quatre destinations primaires** : le bon nombre ?

| | Option |
|---|---|
| **A** | **Garder 4**. |
| **B** | **Réduire à 3**. |
| **C** | **Deux + la séance en cours** quand elle existe. |

**→ Recommandé : différer.** Dépend de `BLOC 2`–`4`. Si vous voulez trancher
maintenant : `A`, et re-trancher après.

### `N-02` — Les **9 destinations derrière `☰`**, rendues **trois fois**

| | Option |
|---|---|
| **A** | **Garder** en l'état. |
| **B** | **Promouvoir** ce qui sert, **retirer** le reste. |
| **C** | **Supprimer le `☰`** — ce qui mérite d'exister mérite une destination. |

**→ Recommandé : `B`.** ⚠ Le **triple rendu** est un défaut à corriger quelle
que soit l'option retenue.

### `N-03` — La coque doit-elle **disparaître pendant la séance** ?

| | Option |
|---|---|
| **A** | **Reste** telle quelle. |
| **B** | **Disparaît** entièrement. |
| **C** | **Se réduit à un fil de retour** — sortir reste possible, naviguer ne l'est plus. |

**→ Recommandé : `C`.** `B` est une soustraction seule (`§5.3`), et une séance
dont on ne peut pas sortir est un piège.

### `N-04` — Le **poids de trait** des icônes

*(Rectification : `Sx_ASSET_02 §50` documente `1.7` pour la coque, `§42/§146`
documentent `2` pour le subset vendeur, et **`§208` diffère explicitement la
valeur canonique « au build »**. Le dépôt est fidèle à sa spec — la valeur n'a
simplement jamais été tranchée.)*

| | Option |
|---|---|
| **A** | **`1.7` partout** — aligner le vendeur sur la coque. |
| **B** | **`2` partout** — aligner la coque sur le vendeur. |
| **C** | **Deux rôles, deux poids** — `1.7` coque, `2` contenu, écrit au contrat. |

**→ Recommandé : `C`.** C'est déjà l'état réel du produit ; il lui manque
seulement d'être **décidé** au lieu d'être subi.

---

# `BLOC 4` — LES SURFACES DE POSSESSION · 5 points

### `O-01` — La porte du domaine « Programmes » *(arbitrage `U-01`)*

⚠ **Trois rendus `A` / `B` / `C+` existent au lab** (`lab_u01`), produits après
re-seed avec deux vrais programmes. **Je les réexpose avant que vous tranchiez** —
je ne résume pas de mémoire un rendu que vous devez voir (`§5.1`).

### `O-02` — Le Profil : formulaire ou état ?

| | Option |
|---|---|
| **A** | **Formulaire** — ce qu'il est aujourd'hui. |
| **B** | **État lisible**, dont « Mettre à jour » ouvre une acquisition guidée (`UX4_01`). |
| **C** | **Instrument** — le profil est la jauge de **ce que le moteur sait de vous**, et ses trous sont visibles. |

**→ Recommandé : `C`.** Un trou dans le profil dégrade une recommandation :
c'est une information d'allocation, donc une jauge.

### `O-03` — Quelles données du Profil méritent d'être demandées ?

| | Option |
|---|---|
| **A** | **Faire l'audit `UX4_01`** d'abord, décider ensuite. |
| **B** | **Garder tout**. |
| **C** | **Ne demander que ce qui change une décision du moteur** — l'audit devient la preuve, pas le préalable. |

**→ Recommandé : `C`.** Le critère est déductible de `PH-01` sans attendre.

### `O-04` — Explorer : catalogue ou corpus ?

| | Option |
|---|---|
| **A** | **Catalogue** — ce qu'il est. |
| **B** | **Corpus contextualisé** (`UX4_02`) — chaque exercice situé par rapport à vous. |
| **C** | **Pas de surface** — on explore depuis la substitution en séance, là où la question se pose. |

**→ Recommandé : `B`.** `C` est séduisant mais supprime le seul endroit où on
découvre sans être déjà en train de s'entraîner.

### `O-05` — « Mon plan »

| | Option |
|---|---|
| **A** | **Surface propre**. |
| **B** | **Vue du Profil**. |
| **C** | **Vue de l'accueil** — la jauge 14 jours **est** le plan. |

**→ Recommandé : `C`**, si `H-01 = C`. Les deux décisions se tiennent.

---

# `BLOC 5` — LES SEUILS · 6 points

> Faible prestige, **premières vues** par un nouvel utilisateur.

### `T-01` — Le login

| | Option |
|---|---|
| **A** | **Sas** classique. |
| **B** | **Porte qui se souvient** — l'identité connue, un seul geste. |
| **C** | **Pas de surface de login** — identité demandée au moment utile. |

**→ Recommandé : `B`.** `C` est incompatible avec des données d'entraînement
personnelles.

### `T-02` — Le nom « Auren » à l'écran *(aujourd'hui seulement dans `<title>`)*

| | Option |
|---|---|
| **A** | **Oui**, en titre au seuil. |
| **B** | **Non**, jamais à l'écran. |
| **C** | **Oui, comme marque d'instrument** — gravée sur le châssis, pas posée en titre. |

**→ Recommandé : `C`.** Un cockpit porte son nom sur sa coque.

### `T-03` — Les **trois liens de poids égal** du login

*(Le « ← Retour » mène ailleurs que là d'où l'on vient.)*

| | Option |
|---|---|
| **A** | **Hiérarchiser** les trois. |
| **B** | **En supprimer deux**. |
| **C** | **Un seul chemin** + un lien de récupération, et le « ← Retour » corrigé ou retiré. |

**→ Recommandé : `C`.** Le retour trompeur est un défaut, quel que soit
l'arbitrage sur le reste.

### `T-04` — L'inscription

| | Option |
|---|---|
| **A** | **Même sas** que le login, deux modes. |
| **B** | **Chemin distinct**. |
| **C** | **Pas d'inscription séparée** — la première connexion crée le compte. |

**→ Recommandé : `A`.** Une seule surface de seuil à concevoir, à tenir, à tester.

### `T-05` — Un **état vide** : échec ou point de départ ?

| | Option |
|---|---|
| **A** | **Échec** — « aucun programme personnel ». |
| **B** | **Point de départ** — l'action qui le remplit. |
| **C** | **Instrument à zéro** — les jauges existent, vides, et disent **ce qui les remplira**. |

**→ Recommandé : `C`.** C'est le défaut vu au lab `U-01` : un écran nu qui
annonce une absence. Un instrument à zéro reste un instrument.

### `T-06` — Une **erreur**

| | Option |
|---|---|
| **A** | **Bandeau** en haut de page. |
| **B** | **Message de champ**. |
| **C** | **Instrument qui refuse** — le châssis passe en état d'erreur, le message vit **dans** l'objet. |

**→ Recommandé : `C`** pour l'erreur d'opération, **`B`** conservé pour la
validation de champ. `K-06` : *tout doit vivre dans l'objet*.

---

## Récapitulatif des recommandations

| Bloc | Recommandations |
|---|---|
| `BLOC 1` | `S-08 B` · `S-09 B` · `S-10 B` · `S-11 B` |
| `BLOC 2` | `H-01 C` · `H-02 C` · `H-03 C` · `H-04 B` · `H-05 B` · `H-06 C` · `H-07 B` |
| `BLOC 3` | `R-01 B` · `R-02 B` · `R-03 B` · `R-04 C` · `R-05 B` · `R-06 C` |
| `BLOC 7` | `X-01 C` · `X-02 C` · `X-03 C` · `X-04 C` · `X-05 C` |
| `BLOC 6` | `N-01` différer · `N-02 B` · `N-03 C` · `N-04 C` |
| `BLOC 4` | `O-01` rendu à réexposer · `O-02 C` · `O-03 C` · `O-04 B` · `O-05 C` |
| `BLOC 5` | `T-01 B` · `T-02 C` · `T-03 C` · `T-04 A` · `T-05 C` · `T-06 C`+`B` |

**Dépendances croisées à connaître avant de trancher** — `H-01` gouverne `O-05` ·
`S-07` gouverne `H-02` et `X-04` · `R-02` gouverne `R-03` · `X-01` dépend de
`BLOC 2`–`3` · `N-01` dépend de `BLOC 2`–`4`.
