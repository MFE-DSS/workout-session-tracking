# `Sb_UI_PROGRAM_DETAIL_01` — cinq ambres pour une décision

## 1. Comment cette tranche a changé de périmètre

Elle devait être la **résorption des 31 styles inline** de
`user_programs/detail.html`, le gabarit le plus chargé du dépôt. L'arbitrage
portait sur un détail d'espacement : quatre marges à 12 px dans une échelle qui
va 4 / 8 / 16 / 24.

**Le rendu de l'écran a montré autre chose.**

| Mesuré sur l'écran réel | |
|---|---|
| commandes à **aplat ambre** | **5** |
| champs de saisie **ouverts** | **13** |
| formulaires | 15 |
| le titre du programme | rendu **2 fois**, à 24 px d'écart |

Le viseur repose sur **une** commande souveraine. Répété cinq fois, l'ambre
cesse de désigner quoi que ce soit — il redevient un fond parmi d'autres.

Et les treize champs venaient d'**un seul formulaire répété** : le même
« Ajouter l'exercice », avec ses quatre champs et son placeholder identique,
rendu **ouvert** sous chacune des trois séances. Il occupait plus de place que
le contenu auquel il ajoute.

**Les 31 styles inline étaient le symptôme.** Les résorber seuls aurait produit
une PR verte et un écran inchangé — le mode d'échec que `CLAUDE.md §5.5` nomme
explicitement. Le périmètre a donc été **re-soumis à l'opérateur** avant
d'écrire, avec les mesures. Il a tranché la refonte.

## 2. Brainstorming · options · risques · choix retenu

Deux variantes rendues **sur l'écran réel**, avec un programme semé dans le
labo — `/programs` n'en contenait aucun, et un écran vide n'arbitre rien.

| | Forme | Verdict |
|---|---|---|
| **G** | tiroirs + ambre unique + titre dédupliqué | base retenue |
| **H** | G + « Supprimer la séance » au rang du texte | ✅ **retenue** |

Et, séparément : le badge de statut **rejoint la ligne « Version »** plutôt que
de rester seul sur sa ligne avec du vide à sa droite — ✅ retenu.

### Le risque, et pourquoi il est tenu

**Replier un formulaire le rend moins découvrable.** Le compromis est explicite :
l'affordance est un `<summary>` de 44 px qui dit « Ajouter un exercice », visible
sous chaque séance, avec son chevron. Ce qui disparaît, ce n'est pas la
fonction — c'est **quatre champs vides répétés trois fois**.

**Aucun JavaScript** : `<details>` natif, invariant `§5` du socle.

### Ce qui n'a pas été fait, et pourquoi

Le composant `.disclosure` existe déjà. Il n'est **pas** réutilisé ici : il
porte son propre châssis de carte, et ce tiroir vit **dans** une carte de
séance. `Q5` interdit une carte dans une carte sans responsabilité propre.

## 3. Le rang 2 est un trait, pas un aplat

`AUREN_VISUAL_BACKBONE §4.2` règle 3 : *« la commande dominante peut être un
trait ; l'aplat n'est pas nécessaire à la domination, la cible tactile si »*.

| Commande | Avant | Après |
|---|---|---|
| Valider le brouillon | aplat ambre | **aplat ambre** — la seule |
| Ajouter une séance | aplat ambre | contour ambre, rang 2 |
| Ajouter l'exercice × 3 | aplat ambre | contour ambre, **dans le tiroir** |
| Supprimer la séance × 3 | bouton encadré | lien souligné, 44 px de cible |

**Compte exact après livraison** : **1 aplat ambre** et **1 contour ambre
visible** (« Ajouter une séance »). Les trois autres contours n'existent
qu'une fois leur tiroir ouvert, où ils sont l'action de ce tiroir.

Une action **destructive** n'a pas à être un bouton de la taille du titre
qu'elle jouxte. Elle reste reconnaissable par le soulignement.

## 4. Les 31 styles inline partent avec la refonte

`31 → 0`. Le gabarit le plus chargé du dépôt est **intégralement résorbé**, et
le cliquet a de nouveau exigé son resserrage plutôt que de laisser
l'amélioration passer en silence :

```
dette RÉSORBÉE mais ligne de base non mise à jour.
  user_programs/detail.html : 31 → 0
```

**Dette du dépôt : 322 → 291**, sur 37 gabarits au lieu de 38. L'entrée est
**retirée**, pas mise à zéro : un gabarit sans dette n'a rien à déclarer.

Les quatre espacements à 12 px sont **alignés sur 8 px** — arbitrage opérateur.
Étendre l'échelle à chaque valeur rencontrée reviendrait à ne plus en avoir.

## 5. Une faute que je me suis faite en cours de route

J'ai réutilisé `.pd-sessions` — une **pile flex** — pour espacer deux
paragraphes, parce que sa `margin-top` avait la bonne valeur. Cela leur
appliquait un `display:flex` non voulu.

Une classe se choisit sur son **sens**, pas sur la commodité d'une de ses
valeurs. `.pd-section` a été créée pour l'espacement seul, et le commentaire
dans la feuille dit pourquoi les deux existent.

## 6. Un trou entre deux gardes, trouvé en plantant

En vérifiant que mon `<details>` neuf était bien couvert, j'ai planté le défaut
qu'il aurait pu porter : `content: "›"` remplacé par `content: ""` sur
`.pd-drawer > summary::after` — donc un dépliant **sans aucun marqueur
visible**.

**Les deux gardes existantes sont restées vertes.**

| Garde | Ce qu'elle vérifie réellement |
|---|---|
| `test_no_disclosure_relies_on_the_browser_default` | que le `<summary>` **est stylé** — pas ce que ce style fait |
| `test_no_new_summary_loses_its_native_marker` | qu'une **décision est inscrite** à l'inventaire — un journal, pas un contrôle |

Son message dit pourtant « restituer un marqueur explicite **ou** inscrire
l'entrée » : l'inscription seule suffit à la satisfaire.

### La première écriture de la garde manquante accusait quinze surfaces saines

Elle exigeait un `content` **non vide**. Or le marqueur canonique du dépôt,
documenté dans `app.css` sous « MARQUEUR DE DIVULGATION », est un **triangle
dessiné en bordures** :

```css
.why-plan__summary::before {
  content: "";
  border-left: 5px solid currentColor;
  border-top: 4px solid transparent;
  border-bottom: 4px solid transparent;
}
```

`content: ""`, et parfaitement visible. **Troisième fois que j'écris une garde
statique qui accuse du code sain** — et cette fois elle aurait accusé le patron
que le dépôt s'est lui-même donné.

### Ce que la garde livrée vérifie, et ce qu'elle refuse de deviner

« Un marqueur est visible » **n'est pas décidable** depuis le texte d'une
feuille : le contenu, une bordure, un fond, une image ou un élément du gabarit
peuvent tous le porter.

La garde ne le tente pas. Elle vérifie le sous-ensemble **décidable** : un
pseudo-élément déclaré **vide de tout** — pas de contenu, pas de bordure, pas
de fond, pas de dimension — ne dessine rien, et c'est toujours une erreur.

**18 vertes, zéro fausse accusation, et elle attrape la plantation** que les
deux autres laissaient passer.

## 7. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| **Q1** connexion · **Q2** ancre d'accueil · **Q3** état du jour | non concernées |
| **Q4** — « les valeurs deviennent l'objet, le texte recule » | **respectée** : quatre champs vides répétés trois fois étaient du chrome, pas de la valeur |
| **Q5** — trois rangs de surface | **respectée**, et c'est le cœur : le rang 1 (aplat, actionnable) est rendu à la **seule** commande qui décide ; le reste descend au rang 2 (trait) ou au rang 3 (typographie seule, pour la suppression). Aucune carte dans une carte |
| Tokens bleus | non concernés |
| Interdit du feu tricolore sur la récupération | non concerné — le rouge n'est pas introduit ; la suppression reste en `text-muted` |

## 7. Vérifications

`check_scope` **SHARED_CODE** · ruff **OK** · cliquet des styles inline **vert
après resserrage** · garde universelle des tiroirs
(`test_no_disclosure_relies_on_the_browser`) **verte** — 46 assertions ·
broad sweep *(voir appendice)*.

Rendu exposé (`§5.1`) **avant** arbitrage — deux variantes sur l'écran réel — et
**après** implémentation.

**Mesuré** : **2,11 → 1,76 écran** · aplats ambre **5 → 1** · champs ouverts
**13 → 1** · styles inline du gabarit **31 → 0**.

## Verdict

**LIVRÉ.** L'ambre redevient le signe d'une seule décision. Les trois
formulaires identiques se replient derrière une affordance de 44 px, sans
JavaScript. La suppression cesse de dominer ce qu'elle détruit. Et la dette de
styles inline du dépôt passe de 322 à 291, le pire gabarit étant entièrement
nettoyé.

**Ce qui reste ouvert** — 291 styles inline dans 37 gabarits. Les suivants par
volume : `_partials/session_review.html` (23), `body_assessment/body_overview.html`
(21), `squad_detail.html` (20), `user_programs/quality.html` (20). Chacun
mérite d'être regardé avant d'être nettoyé : celui-ci a montré que le nombre de
styles inline mesure surtout **l'absence de mise en page**, pas un défaut
cosmétique.
