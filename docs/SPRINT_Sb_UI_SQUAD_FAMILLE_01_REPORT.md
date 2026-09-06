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

## 5quater. La discipline s'est appliquée à moi une quatrième fois

En écrivant `§5ter`, j'ai affirmé que la famille `user_programs/*` était close.
**Elle ne l'était pas** : `list.html` (5) et `new.html` (4) en font partie.

J'allais livrer un rapport qui déclare complète une famille qui ne l'est pas,
**dans la tranche même qui dénonce ce mode**. Trouvé en listant le cliquet, pas
en relisant ma prose.

### Le second consommateur prouve que la classe est générique

Les neuf attributs correspondaient **exactement** à des classes écrites deux
heures plus tôt pour `squads_list` et `squad_create` : mêmes barres d'outils,
mêmes piles de cartes cliquables, mêmes panneaux de formulaire. Deux
fonctionnalités sans rapport, la même forme de page.

Leur préfixe disait pourtant `sq-`. Plutôt que de coller « squad » sur une page
de programmes — ce que j'ai assumé pour `.pd-*`, faute d'un second
consommateur —, elles sont **renommées**, parce que cette fois la preuve
existe :

| Avant | Après |
|---|---|
| `.sq-toolbar` | `.page-toolbar` |
| `.sq-list` | `.card-stack` |
| `.sq-card` | `.card--link` |
| `.sq-card__head` · `.sq-card__meta` | `.card__head` · `.card__meta` |
| `.sq-panel` · `.sq-panel--wide` | `.form-panel` · `.form-panel--wide` |
| `.sq-back` | `.page-back` |

Neuf fichiers touchés par le renommage. **Un renommage manqué d'un côté rend
une page non stylée en HTTP 200** — donc vérifié au style calculé, pas au code
de statut :

| Sonde | avant | après |
|---|---|---|
| carte cliquable `/squads` | `block/none/398px` | `block/none/398px` |
| pile `/squads` | `flex/none/398px` | `flex/none/398px` |
| carte cliquable `/programs` | `block/none/398px` | `block/none/398px` |
| panneau `/squads/create` | `392px` | `392px` |

Et un **test de fumée sur 28 routes**, des deux côtés : `28/28` en 200, zéro
erreur JavaScript, styles inline cumulés **87 → 47**.

## 5quinquies. Le rang META n'avait pas de classe

En finissant les six petits gabarits restants — `contact`, `reset_password`,
`password_change`, `launcher`, `science`, `export` —, le motif dominant n'était
plus l'espacement : c'était **`font-size: 12px` recopié en attribut**, quatre
fois sur le seul `/science`.

`Q6` fixe quatre rangs — 32 / 22 / 15 / 12 — et le relevé de décisions les a
écrits **cette nuit**. Deux seulement avaient une classe : `.section-header`
porte SECTION depuis `#208`, et **rien ne portait META**. `.text-dim` et
`.text-muted`, les deux voisines évidentes, ne posent qu'une **couleur** —
les prendre pour un rang de taille était la confusion offerte.

C'est le diagnostic du programme appliqué à une décision d'hier soir : **prise,
écrite, mergée, et sans moyen de l'appliquer.** `.text-meta` existe désormais.

### Trois styles ne faisaient que répéter leur propre classe

```html
<div class="card__actions" style="margin-top: 16px;">
```

`.card__actions` pose déjà `margin-top: var(--space-md)` — **soit 16 px**.
L'attribut ne changeait rien.

Pire : `.card__actions--auth`, **que j'avais créé dans `Sb_UI_AUTH_01` pour
remplacer exactement cet attribut** sur trois AUTRES gabarits, redéclarait la
même valeur. Un modificateur sans effet, né d'une conversion qui n'avait pas
vérifié ce que la classe porteuse donnait déjà.

Les deux formes disparaissent — six gabarits, zéro pixel de mouvement. Il en
reste **deux instances** sur des surfaces que cette tranche ne touche pas
(`profile`, en attente d'arbitrage ; `measurement_form`, en 404).

### Mesure

| Route | Hauteur avant → après | Styles inline dans `main` |
|---|---|---|
| `/contact` · `/profile/password` | **932 → 932 px** | 3 → 0 chacune |
| `/launcher` · `/science` · `/export` | **inchangées** | 7, 4, 2 → 0 |
| `/plan` | 1250 → 1251 px (compté) | 2 → 0 |

Sur **quinze routes comparées**, un seul écart de hauteur — celui de `/plan`,
déjà expliqué. Zéro erreur JavaScript des deux côtés.

## 5sexies. Où en est la dette, une fois classée honnêtement

**Cliquet : 174 → 89** sur 14 gabarits. Le nombre brut ment toujours ; classé
par ce qu'on peut réellement en faire :

| | |
|---|---|
| **60** | surfaces en **404** derrière un drapeau, ou **décommissionnées** — `body_assessment/*` (30), `dashboard` (12), le widget « État du jour » d'`index` (13) et son historique `readiness_history` (5) |
| **17** | `profile.html` — en attente d'arbitrage |
| **4** | `session_detail.html` — le viseur, interdit |
| **8** | **réellement actionnables**, sur 7 gabarits : `user_profile` (2) et six singletons |

⚠ **J'ai d'abord annoncé treize.** `readiness_history` rend le barème 1-à-5 de
l'« État du jour », et son unique point d'entrée est le widget que
l'amendement `Q3` décommissionne. Il part avec lui. Vérifié après avoir publié
le chiffre — *le classement par atteignabilité vaut d'être refait, pas
recopié.*

Depuis le début du programme : **328 → 8 actionnables.**

## 5septies. Les huit derniers — la dette actionnable tombe à zéro

Après le classement du `§5sexies`, huit attributs restaient prenables. Ils le
sont.

Quatre d'entre eux **portaient déjà une classe** qui n'avait pas leurs
propriétés — `.atlas-version`, `.user-profile__notice`, `.user-profile--v2` :
la classe existait, la déclaration vivait à côté. Les autres reçoivent une
classe nommée : `.svg-sprite`, `.inline-form`, `.library-section`,
`.coach-note`.

Deux restes hors échelle, tous deux manqués par **mes propres tranches** :

* `session_done.html` rendait « (indicatif) » à **11 px**, sous le rang META —
  alors que `Sb_UI_SESSION_DONE_01` avait mis cet écran à l'échelle E3 ;
* `coach_report.html` avait une note à **13 px**, entre META et BODY.

Les deux rejoignent META (12). Le second explique l'unique écart de hauteur
inattendu du balayage final : `/coach-report` perd **4 px**, parce que ce
paragraphe court sur trois lignes.

### Ce que la mesure a révélé au passage

**Deux autres paragraphes de `/coach-report` restent à 13 px** — dans des
classes, pas des attributs. Le cliquet ne les voit pas : *il compte des
attributs, pas des valeurs hors échelle.* Retirer les styles inline ne met pas
une surface à l'échelle ; ce sont deux chantiers distincts, et seul le premier
a un cliquet.

### Balayage final, 31 routes

| | avant | après |
|---|---|---|
| routes en 200 | **30/31** | **30/31** |
| styles inline rendus, cumulés | **123** | **34** |
| erreurs JavaScript | aucune | aucune |
| écarts de hauteur sur 30 routes | — | **2**, tous deux comptés (`/plan` +1, `/coach-report` −4) |

Les 34 restants sont exactement : `/profile` (17, en attente d'arbitrage), le
widget décommissionné de l'accueil (13), et **4 largeurs de barre dynamiques**
du rapport coach, qui sont légitimes.

### La dette, à la fin

**81 attributs sur 7 gabarits — et aucun n'est actionnable :**

| | |
|---|---|
| **30** | `body_assessment/*` — routeur en **404** derrière `BODY_ASSESSMENT_ENABLED` |
| **18** | `index` + `readiness_history` — la fonctionnalité **décommissionnée** par `Q3` |
| **17** | `profile.html` — **ton arbitrage** |
| **12** | `dashboard.html` — **aucune route ne le rend** |
| **4** | `session_detail.html` — **le viseur, interdit** |

**328 → 81, dont 0 actionnable.**

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
styles inline resserré **174 → 81** (7 gabarits, tous bloqués) · ruff OK.

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
