# `Sb_UI_SQUAD_FAMILLE_01` — je m'étais arrêté à deux gabarits sur huit

`Sb_UI_SQUAD_READABILITY_01` a corrigé, il y a six heures, un badge dont le
texte blanc mesurait **3,07 : 1** sur son fond vert — sous le seuil AA. Son
rapport reprochait, en toutes lettres, *une décision appliquée là où c'était
commode*.

**Je l'avais corrigé sur une surface sur trois.** Les deux autres l'ont gardé.

## 1. Ce que le balayage de classe aurait dû trouver

La tranche précédente a bien balayé `.stats-list` — dix usages lus un par un.
Elle n'a **pas** balayé le badge qu'elle venait de corriger.

| | |
|---|---|
| gabarits de la famille `squad*` | **8** |
| traités par `Sb_UI_SQUAD_READABILITY_01` | 2 |
| **laissés** | **6**, portant **31 attributs `style`** |
| dont le badge à **3,07 : 1** | **2** — `squad_challenges`, `squad_challenge_detail` |

C'est le même défaut, dans la même famille, sous les yeux de la tranche qui le
nommait.

## 2. Le vocabulaire existait — celui que je venais d'écrire

Sur 31 occurrences et 14 déclarations distinctes, **huit classes existaient
déjà** : `.sq-scroll`, `.sq-table`, `.sq-back`, `.sq-field`, `.pd-error`,
`.pd-block`, et `.badge--actif`. Six ont été ajoutées, dont **aucune n'est une
couleur**.

## 3. Une unification d'espacement, comptée

Les quatre champs de `squad_challenge_create` s'espaçaient de **16 px** ; le
reste de la famille utilise `.sq-field`, à **8 px**. Ils le rejoignent.

**Mesuré au rendu : le formulaire passe de 394 à 370 px.** Vingt-quatre pixels,
soit trois écarts inter-champs — comptés, pas constatés après coup.

## 4. Le contraste, mesuré dans le navigateur

| Badge « actif » | Texte | Fond | Ratio |
|---|---|---|---|
| **avant** | `rgb(255,255,255)` | `rgb(110,158,122)` | **3,07 : 1** ⛔ |
| **après** | `rgb(10,12,15)` | `rgb(110,158,122)` | **6,37 : 1** ✅ |

`--on-accent` existait ; les deux gabarits ne l'atteignaient pas.

## 5. Une couleur en dur que j'ai trouvée, et que je ne livre pas

Le balayage des hexadécimaux **dans les attributs `style`** rend six
occurrences sur cinq gabarits. Lues une par une :

| Couleur | Où | Verdict |
|---|---|---|
| `#fff` ×2 | badges squad | **corrigé ici** — 3,07 → 6,37 : 1 |
| `#c0392b` | `profile.html` | **défaut RÉEL, non livré** — voir ci-dessous |
| `#a33` (2,69 : 1) · `#222` (1,10 : 1) | `body_assessment/*` | surfaces en **404** derrière `BODY_ASSESSMENT_ENABLED` |
| `#e66` (5,60 : 1) | `measurement_form` | conforme |

### `#c0392b`, et un quatrième trou dans ma garde

`profile.html` écrit `color: var(--color-danger, #c0392b)`. Ma garde des tokens
fantômes (`#210`) ne l'a pas signalé, parce qu'elle voit `--color-danger`
**défini** — mais il ne l'est que dans `session_focus.css`, **la feuille du
viseur**.

Vérifié au navigateur : `/profile` charge `app.css`, `interaction.css` et
`target_closure.css`. **Pas `session_focus.css`.** Le token y résout à `''`, et
c'est bien `#c0392b` qui serait peint — à **3,21 : 1**, sous AA.

**La garde ne modélise pas la PORTÉE des feuilles.** Un token défini dans une
feuille qu'une page ne charge pas est, pour cette page, un fantôme. Quatrième
trou de cette garde en une nuit, et le plus subtil des quatre.

**Non livré**, pour deux raisons cumulées : la branche qui rend cette ligne ne
s'affiche pas avec les données du labo — donc `§5.1` est insatisfiable —, et
`profile.html` est la surface en attente d'arbitrage.

Le balayage de portée trouve **trois** cas au total. Les deux autres —
`var(--radius-md, 10px)` et `var(--motion-duration-fast, 120ms)` dans
`app.css` — ont des **replis sensés** : ils rendent correctement hors du viseur
et prennent le token dedans. Ce ne sont pas des défauts. *Sur trois
accusations, une seule tenait.*

## 5bis. Et une deuxième famille traitée aux deux tiers

Le même constat, sur l'autre famille de la nuit. `Sb_UI_AUTH_01` avait traité
`login` et `register` ; **`welcome` est resté** avec ses neuf attributs
`style` — et sans l'accroche `Q1` que portent ses deux sœurs.

C'est l'accueil **non authentifié**, celui que l'opérateur a nommé « la vraie
première impression ».

**Les neuf attributs partent. Aucune valeur n'est réglée**, et c'est délibéré :
deux d'entre elles sont hors échelle et hors grille — le lede à **13 px**
(entre BODY 15 et META 12) et le rembourrage bas à **60 px** (7,5 × 8). Les
corriger serait re-régler une surface dont l'échelle est un arbitrage
d'opérateur, pas une dette mécanique. Elles sont transposées **à l'identique**,
avec l'avertissement écrit dans la feuille.

**L'accroche manquante n'est pas ajoutée non plus** : mettre du texte sur la
première impression du produit est une décision de contenu sur la surface la
plus exposée. Signalée.

Rendu : **932 px avant, 932 px après** · marque à `32px / 2.56px / center`
inchangée · styles inline **9 → 0**.

## 5ter. Et une TROISIÈME — ce n'est plus un oubli, c'est un mode

`Sb_UI_PROGRAM_EDITOR_STYLES_01` a traité qualité, publication et génération,
et a **différé `plan.html` en le disant** : une autre tranche touchait la même
ligne au même moment. La raison était bonne. Elle a cessé de l'être quand cette
tranche a mergé — et le gabarit est resté.

**Trois familles traitées aux deux tiers en une nuit : squad, auth, éditeur.**
Le motif est le même à chaque fois : une tranche s'arrête à ce qu'elle avait
ouvert, et la sœur restante n'a plus de propriétaire. Un « différé, dit
explicitement » n'est pas une garde — c'est une note dans un rapport que
personne ne relit.

Neuf attributs `style` → 0. Rendu : `/plan` passe de **1250 à 1251 px**, sept
tailles de corps inchangées. Le pixel vient de l'alignement des marges sur la
grille (`.75rem` → 8 px, retrait de liste `1.25rem` → 24 px).

⚠ Une valeur reste hors échelle et est **transposée telle quelle** : `.9em`,
soit **12,6 px** sur un corps de 14. Comme pour `welcome`, régler l'échelle
d'une surface est un arbitrage, pas une dette mécanique.

## 6. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| **Q1** · **Q2** · **Q3** · **Q6** · **Q8** | non concernées |
| **Q4** / **DF-C** | non concernées — aucune valeur ni clé rendue |
| **Q5** — trois rangs de surface | **respectée** : aucun conteneur ajouté ni retiré |
| **Q7** — un seul aplat ambre par écran | **respectée** : aucun aplat touché ; le badge vert n'est pas un ambre de commande |
| **`§5.3`** jamais une soustraction seule | respectée : rien ne disparaît |
| **`§5.4`** toute couleur est un token mesuré | **c'est le motif** : deux `#fff` remplacés par `--on-accent`, ratios écrits |
| **`§5.5`** la centralité avant la facilité | **respectée à contre-courant** : la tranche existe précisément parce que la précédente s'était arrêtée au facile |

## 7. Vérifications

`check_scope` **SHARED_CODE** · broad sweep ciblé : **162 tests** · cliquet des
styles inline resserré **174 → 125** (22 gabarits) · ruff OK.

Rendu exposé (`§5.1`) depuis deux serveurs, sur les **cinq** routes
atteignables de la famille :

| Route | Hauteur | Styles inline dans `main` |
|---|---|---|
| `/squads/create` · `/squads/join` · `/squads/1/compare` · `/squads/1/challenges` | inchangées | **3, 4, 5, 4 → 0** |
| `/squads/1/challenges/create` | inchangée (formulaire **394 → 370 px**, compté) | **6 → 0** |

## Verdict

**LIVRÉ.** La famille squad est à zéro attribut `style` sur ses huit gabarits,
et le badge à 3,07 : 1 ne survit nulle part. Une couleur en dur de plus est
localisée, mesurée et **non livrée** — avec la raison, et avec le trou de garde
qui l'avait laissée passer.

## 7bis. Le viseur, prouvé intact sur toute la nuit

Le viseur intra-séance était **interdit par le mandat**, et la nuit a pourtant
beaucoup touché `app.css` — tokens sémantiques, rang SECTION, familles `.pd-*`,
`.sq-*`, `.welcome-*`. Une garde par lecture de gabarit ne suffit pas à le
prouver : une règle partagée peut l'atteindre sans le nommer.

Vérifié par **comparaison de rendu**, entre la canonique d'avant la nuit
(`ffb4f62`) et celle d'aujourd'hui, servies simultanément :

| | avant la nuit | maintenant |
|---|---|---|
| `main` du viseur | **1772 px** | **1772 px** |
| signature typographique (taille + couleur + graisse, **67 éléments**) | `dc926c1cd4b5a859` | `dc926c1cd4b5a859` |
| pied de page **partagé** | 76 px | 79 px |
| `<small>` du pied | **9,17 px** | **11 px** |

**Le contenu du viseur est identique au pixel.** Les trois pixels d'écart de la
page entière viennent du **pied de page partagé**, hors du viseur, où
`Sb_UI_PROGRAM_DETAIL_01` a retiré le `smaller` que le **navigateur** imposait :
`.foot` vaut 11 px, et le `<small>` qu'il contient y appliquait un ratio de
0,833 — soit **9,17 px que personne n'avait décidés**, sur toutes les pages.

C'est une correction, elle est partagée, et elle n'entre pas dans le viseur.

## 8. Ce qui reste ouvert

* **`profile.html` — `var(--color-danger, #c0392b)`**, à 3,21 : 1. Le token
  correct est `--danger`, qui vit dans `app.css`. À faire avec l'arbitrage de
  `/profile` ;
* **la garde des tokens fantômes ne modélise pas la portée des feuilles.**
  L'invariant juste serait : *un token utilisé depuis une feuille globale ou un
  gabarit doit être défini dans une feuille globale.* Trois cas aujourd'hui,
  dont un seul est un défaut ;
* **`body_assessment/*`** — deux couleurs sous AA (`#a33` à 2,69, `#222` à
  1,10) sur des surfaces en 404. Ni livrables ni vérifiables tant que le
  drapeau est fermé ;
* **`welcome.html` n'a pas l'accroche `Q1`** que portent `login` et
  `register`. Ajouter du texte à la première impression du produit est une
  décision de contenu — signalée, pas prise ;
* **deux valeurs hors échelle sur `welcome`** — lede 13 px, rembourrage bas
  60 px — transposées à l'identique et documentées dans la feuille.
