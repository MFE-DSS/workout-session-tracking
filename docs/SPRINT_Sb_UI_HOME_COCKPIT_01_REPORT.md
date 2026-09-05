# `Sb_UI_HOME_COCKPIT_01` — l'accueil devient un cockpit

Direction artistique conduite par l'opérateur le 2026-09-06, sur rendus.
Chaque décision ci-dessous a été **arbitrée sur une image**, pas sur une
description.

## 1. Le constat, mesuré

| | |
|---|---|
| objets au-dessus de 16 px | **1** |
| éléments à **11 px** | **14** |
| éléments à **12 px** | **8** |
| tailles distinctes | **7**, pour **4** rôles |
| cartes bordées | **8**, toutes de même rang |

**Vingt-deux blocs de texte sur trente-sept** vivaient dans les deux plus
petits corps. Aucun registre intermédiaire : 24 px, puis le brouillard.

Et le défaut que le socle documente sur 101 usages était là, vivant : le titre
de bloc (`tile__label`, 11 px) **sous** le corps qu'il introduit (13–15 px).
Deux conventions coexistaient pour ce rôle (`tile__label` 11 px et
`card__title` 14 px), et la **même classe faisait deux métiers** —
`tile__label` titrait aussi les tuiles de navigation, à 15 px.

## 2. Brainstorming · options · risques · choix retenu

### L'intention, puis l'ordre

Quatre lectures possibles de l'écran ont été soumises. Retenu : **les trois
rôles, dans un ordre strict**, puis **AGIR → SITUER → RÉSULTAT** — l'ordre d'un
poste de travail : la décision, puis où elle s'insère, puis ce qu'elle produit.

### Le traitement du rang 2 — trois variantes rendues

| | Forme | Verdict |
|---|---|---|
| **T1** | aucun conteneur, filet de séparation | ✅ **retenu** |
| **T2** | un seul châssis pour tout le rang 2 | écarté — deux objets encadrés se font face |
| **T3** | cartes allégées, bordure retirée | écarté — sept blocs de même fond restent de même rang |

T1 est ce que `Q5` prescrit depuis toujours et que le produit n'avait jamais
appliqué : *« une carte qui entoure tout n'entoure plus rien »*. Le hero
redevient **le seul objet encadré de l'écran**.

### L'échelle typographique — trois variantes rendues

| | Échelle | Verdict |
|---|---|---|
| **E1** | 24 / 16 / 14 / 11 | écarté — hiérarchie trop discrète |
| **E2** | 28 / 18 / 15 / 12 | écarté — **crée une troisième convention** |
| **E3** | **32 / 22 / 15 / 12** | ✅ **retenu** |

E3 n'invente rien : **32 px est le readout souverain de `Progression`**, **22 px
le rang `heading-2` que `Mon plan` rend déjà** — tous deux livrés la veille.
L'accueil s'aligne sur l'application au lieu d'ajouter une convention.

**Conséquence mesurée, assumée** : à 32 px un nom de séance réel tient sur
**trois lignes**, contre deux à 24 et 28. Vérifié au rendu : le hero a la place,
et il est l'objet le plus important de l'écran.

### Le contenu du rang 2, et ce qui en sort

* **restent** : Semaine planifiée · État du corps ;
* **la régularité** quitte sa carte pour une **ligne sous les zones**. ⛔ Le
  ratio « 3 sur 4 » est **interdit** : `_build_weekly_plan` refuse la détection
  plan-réel, qui « reviendrait à deviner quelle séance enregistrée a rempli
  quelle séance planifiée ». Les deux nombres voisinent, ils ne se divisent pas ;
* **« Dernière séance »** est masquée quand une séance est en cours — le hero
  dit déjà la même phrase, 300 px plus haut. Elle reste entière sinon : c'est
  alors la seule trace du passé, et la retirer serait une soustraction ;
* **« Résumé · indicateurs et navigation »** disparaît : il décrivait la
  structure du document, pas son contenu ;
* **la tuile Science sort**. `/science` est une zone d'archive qu'on atteint
  **depuis la question**, et le produit le fait déjà à quatre endroits, dont
  trois pointent vers une règle précise. La tuile de l'accueil était le seul
  lien sans contexte. Vérifié : rien n'est orphelin.

## 3. Trois défauts que seul l'état « compte neuf » a révélés

L'accueil a au moins trois états. N'en dessiner qu'un est l'erreur commise
quatre fois la veille ; un compte neuf a donc été semé exprès.

### a. Le filtre des raisons regardait une POSITION, pas une VALEUR

```
phrase  : « Bon premier template pour démarrer : Push A… »
reasons : [ « Première séance — démarrage doux suggéré. »,
            « Bon premier template pour démarrer : Push A… » ]
```

Le gabarit coupait à `reasons[1:]`, sur l'hypothèse écrite **dans son propre
commentaire** : « `reasons[0]` est déjà la phrase ci-dessus ». Elle est fausse.

Conséquence : la phrase était imprimée **deux fois**, et **la seule raison
différente était jetée en silence**. Le tri gardait le doublon et supprimait
l'information. Le filtre compare désormais la valeur — il ne suppose plus rien
de l'ordre.

⚠ Le défaut n'apparaît qu'à partir de **deux raisons**, c'est-à-dire
précisément sur le **premier écran qu'un utilisateur voit**.

### b. Le lecteur d'écran en savait plus que l'œil

Le bilan des zones rendait un glyphe hachuré et un nombre ; le nom de l'état
n'existait que dans le texte hors écran. Sur un compte neuf, où les onze zones
partagent le même état, la ligne entière se réduisait à « ▨▨▨ 11 ».

Le libellé devient **visible**, et le `sr-only` de la macro est retiré du même
geste — le conserver aurait fait entendre le nom deux fois.

### c. Trois filets d'affilée — introduit par cette tranche

`.cockpit__tally` ferme par un filet, la zone secondaire ouvre par un filet, et
mon `border-top` de rang 2 en ajoutait un troisième. Vu au rendu, corrigé.

## 4. La garde de l'ambre : ce que l'opérateur a demandé, et ce que j'ai livré

Demandé : *« une garde qui compte les aplats par gabarit et refuse le second »*.
Écrite telle quelle, **elle accusait cinq gabarits sains** :

* `index.html` porte **quatre** `today-home__cta` — dans des branches Jinja
  **mutuellement exclusives**. Mesuré au navigateur sur les trois états :
  **un seul aplat visible** ;
* `user_programs/detail.html` en porte trois dans des branches de statut et
  trois dans des `<details>` fermés. Cet écran est **conforme** depuis sa refonte.

« Un aplat par écran » **n'est pas décidable depuis le texte d'un gabarit** :
branches, boucles et tiroirs décident de ce qui rend. Sixième occurrence de ce
mode d'échec ici.

**Livré à la place** : un **cliquet par gabarit**, gelé à 45 occurrences sur 31
gabarits, strict dans les deux sens. Il n'affirme pas « un seul rendu » — il
empêche la dérive qui a produit les cinq. La ligne de base porte elle-même
l'explication, et un test vérifie qu'elle la porte.

**La vraie règle appartient à un harnais de rendu.** Dette nommée.

## 5. Mon harnais m'a menti avant le produit

Le harnais de mesure se reconnectait à **chaque** rendu. Au-delà de dix
tentatives par dix minutes, le limiteur de débit du produit répond « Too many
attempts » — et la page mesurée devient l'écran de connexion.

Symptôme : un état de l'accueil a soudain rendu « 18px×1 · 14px×1 » au lieu de
son échelle complète. **J'ai failli conclure à une régression de cette
tranche.** Le défaut était dans l'instrument.

`scratchpad/lab.py` authentifie désormais **une fois par utilisateur** et
réutilise l'état. C'est la même famille que « le labo doit être
représentatif » : un instrument qui se sabote produit des mesures fausses, et
une mesure fausse coûte plus cher que pas de mesure.

## 6. Les seuils rejoignent l'échelle — et Q1 est enfin appliquée

Les seuils sont livrés **dans la même tranche** que l'accueil : ils partagent
`app.css` et la même échelle. Deux PR y auraient touché le même fichier.

### Q1 disait déjà tout, et rien n'en était appliqué

L'opérateur a demandé que la connexion devienne « une vraie première
impression », en pensant amender Q1. **Aucun amendement n'est nécessaire** :

> **Q1** — « Une porte premium, terminale, silencieuse, **avec une phrase
> forte**. » Structure : marque · **une phrase** · formulaire · liens
> secondaires **hiérarchisés**. Accroche tranchée le 2026-08-19 :
> « S'entraîner avec intention biomécanique. »

Q1 nomme même le défaut : *« aujourd'hui trois liens de poids égal, donc aucun
chemin principal »*. Trois choses manquaient à l'écran :

| Décision Q1 | État avant |
|---|---|
| la marque | présente, mais à **12 px** — le plus petit texte de l'écran, sous un « Connexion » à 18 |
| **la phrase** | **absente** |
| liens hiérarchisés | 13 px contre 12, même couleur — **une hiérarchie d'un pixel** |

**La spec avait raison ; c'est l'écran qui ne la suivait pas.** Livré :

* la marque passe au rang **DISPLAY (32 px)**, l'interlettre gravée conservée
  et resserrée pour la taille ;
* **l'accroche est rendue**, mot pour mot, sur la connexion **et
  l'inscription** — c'est là qu'un visiteur qui ne connaît pas le produit
  décide d'entrer. Pas sur « Mot de passe oublié », qui est un flux de
  récupération, pas une rencontre ;
* « Connexion » redescend au rang **MÉTA** : il redevient l'étiquette du
  formulaire au lieu d'un second titre. L'élément reste un `<h1>` — le niveau
  sémantique ne dépend pas de la taille, et le retirer priverait la page de son
  titre ;
* le **chemin principal** (« S'inscrire ») prend le rang BODY et la couleur du
  texte courant ; les deux sorties mineures restent en MÉTA, en sourdine.

Le vide de l'écran passe de **60 % à 35 %**, sans rien ajouter d'inventé.

### Un seuil portait la navigation de l'application

**Défaut mesuré, pas supposé.** `/forgot-password` étend `base.html`, qui rend
la barre du bas **sans condition d'authentification**. Un visiteur déconnecté y
voyait quatre onglets — Séance, Programmes, Progression, Profil — **qui le
renvoyaient tous au login**. Quatre affordances qui ne mènent nulle part.

`login` et `register` y échappaient par accident : ce sont des documents
autonomes. Le gabarit le documentait lui-même — « la surface se lit comme une
page interne alors que c'est un SEUIL » — **sans nommer la conséquence**.

Le mécanisme existait déjà : `shell_focus_mode` retire la coque pour le viseur.
Il n'est **pas** réutilisé : il pose aussi `is-session-focus-mode` sur le
`<body>`, et du style de séance sur une page de connexion n'aurait aucun sens.
**Deux idées, deux noms** — `shell_bare` retire la coque, rien de plus. C'est la
même discipline que `.pd-section` la veille : une classe se choisit sur son
sens, pas sur la commodité d'une de ses valeurs.

Vérifié après coup : la coque **revient** sur `/`, `/progress`, `/history`,
`/contact` et `/library`.

### 9,17 px sur toutes les pages

`.foot` vaut 11 px et contient un `<small>` : le navigateur y applique son
`smaller`, soit **9,17 px** — pour le nom du produit, en pied de **chaque**
page. Personne ne l'avait écrit ; la feuille du navigateur l'a décidé.

Le `<small>` reste — il porte une nuance sémantique — mais il cesse de choisir
sa taille à notre place.

## 7. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

`docs/DESIGN_DECISIONS_UIV2_SURFACES.md`, décision par décision :

| Décision | Verdict |
|---|---|
| **Q1** — la connexion porte l'identité, version sobre | **appliquée pour la première fois**. L'opérateur pensait devoir l'amender ; elle disait déjà « une porte premium avec une phrase forte » et fixait l'accroche depuis le 2026-08-19. Rien n'en était rendu. **Aucun amendement écrit** — la spec avait raison |
| **Q2** — ancre visuelle = barres de récupération par zone | **respectée** : l'ancre causale du hero n'est pas touchée, seul son corps de texte rejoint l'échelle |
| **Q3** — « État du jour » replié, ouvert d'un geste | **non appliquée, et non touchée ici**. Le produit rend cinq pastilles, pas la ligne compacte que Q3 décrit. L'opérateur a tranché son **décommissionnement** — tranche séparée, avec amendement daté |
| **Q4** — « les valeurs deviennent l'objet, le texte recule » | **respectée**, et c'est l'objet de la tranche |
| **Q5** — trois rangs de surface | **respectée**, et enfin appliquée : rang 1 encadré (le hero seul), rang 2 en filets, rang 3 sans conteneur |
| **Tokens bleus** — origine système | **respectée** : le rail causal et la phrase du moteur restent bleus, aucune valeur changée |
| Interdit du feu tricolore sur la récupération | **respectée** — aucune couleur introduite |

## 7. Vérifications

`check_scope` dit **ISOLATED** ; traité en **SHARED_CODE** — `index.html` et
`home.css` sont des surfaces partagées, et `CLAUDE.md §1` demande de remonter
d'un cran en cas de doute.

ruff **OK** · cliquet des styles inline **vert après resserrage** (291 → **272**,
36 gabarits) · cliquet ambre **3 gardes vertes**, 2 plantations vérifiées ·
gardes de surface, tiroirs et marqueurs **vertes** · broad sweep *(appendice)*.

Rendu exposé (`§5.1`) sur **les trois états** — séance en cours, aucune séance
ouverte, compte neuf — avant et après.

## Verdict

**LIVRÉ.** L'accueil a quatre tailles au lieu de sept, un objet encadré au lieu
de huit, et un ordre lisible. Trois défauts de contenu que seul le compte neuf
révélait sont corrigés, dont un qui **jetait une information** en croyant
retirer un doublon.

**Où en est l'échelle maison, mesuré sur les surfaces livrées :**

| Surface | Plus grand | Rangs employés |
|---|---|---|
| Connexion / Inscription | 32 px | **4** ✓ |
| Accueil | 32 px | **6** — dont 2 appartenant à l'état du jour ✓ |
| Mon plan | 22 px | 7 |
| Mon programme | 18 px | 5 |
| **Progression** | 32 px | **11** — dont du 10 px et du 9 px |

Deux surfaces sur cinq sont alignées. C'est l'ordre arbitré — « l'accueil
d'abord, puis écran par écran » — et `Progression` est de loin la plus
dispersée, malgré son relevé souverain livré la veille.

**Ce qui reste ouvert :**

* **« Ce que disent tes séances »** s'affiche sur un compte qui n'a **aucune
  séance**. Le libellé est au mieux étrange au premier lancement. Corriger
  demande d'écrire de la voix produit — je ne l'invente pas, je le signale ;
* **l'état du jour** reste tel quel : son décommissionnement et le câblage de
  la lecture dérivée dans `/profile` sont une tranche à part, avec amendement
  de `Q3` ;
* les deux tailles résiduelles (13 et 11 px) appartiennent **toutes deux** à
  l'état du jour et partiront avec lui.
