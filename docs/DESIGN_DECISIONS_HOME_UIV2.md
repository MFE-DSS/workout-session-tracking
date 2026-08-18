# Registre des décisions — refonte Accueil (brainstorm 2026-08-17)

**Statut : `DOCUMENTED — NOT BUILT`** · versionné par
`DESIGN_DECISIONS_HOME_UIV2_01` le 2026-08-18, base `c2a2a45`.

Décisions **validées par l'opérateur** pendant le brainstorm visuel.
**Toute maquette et toute implémentation ultérieure doit les porter en entier.**
Une maquette qui en omet une est fausse, même si le reste est juste.

> **Aucune de ces décisions n'est implémentée.** Le sprint qui versionne ce
> document ne touche ni template, ni CSS, ni route. Il existe parce qu'un relevé
> de décisions validées qui vit dans un fichier non suivi par git n'existe pas :
> il disparaît au premier nettoyage, et le travail de brainstorm avec lui.

---

## D1 — Contrat d'interactivité hybride ✅ validé

Registre typographique **et** surface de contrôle. Les deux signaux sont
redondants volontairement : c'est déjà la règle du dépôt pour la sélection, qui
doit rester lisible sans couleur.

**Un seul registre d'étiquette**
- petites majuscules, interlettrage large (~0,09 em), ton éteint
- **jamais** de bordure, **jamais** de chevron, **jamais** de surface tapable

**Trois rangs de contrôle — tous 44 px de cible minimum**

| rang | usage | rendu |
|---|---|---|
| 1 | action dominante, **une seule par écran** | fond ambre plein, chevron |
| 2 | alternative réelle | bordure discrète, casse normale, graisse 600, chevron |
| 3 | navigation | filet sous le texte + chevron, pas de cadre |

**Testable** : une étiquette ne porte jamais bordure ni chevron ; un contrôle
fait toujours ≥ 44 px et porte un chevron.

> Note : la doctrine « un cadre de moins » des tranches UIV2 visait les **cartes
> de contenu imbriquées**, pas les **surfaces de contrôle**. Un bouton qui a une
> surface n'est pas une carte dans une carte.

---

## D2 — Badge d'origine ✅ validé

**« RECOMMANDÉ ⓘ »**, en **bleu**, accompagné du volume (« 21 séries »).

- Le `ⓘ` révèle la **vraie raison**, déjà produite par le moteur
  (`recommendation.py` expose une `phrase` aujourd'hui jamais affichée).
- Même motif que le `ⓘ` existant sur « disponibilité » (`index.html:161`).

**Interdit — « Recommandé IA ».** Le moteur se décrit lui-même comme
*« Deterministic, explainable, zero-ML »*. Aucune revendication d'IA.
Et c'est un avantage : il sait dire **pourquoi**, ce qu'une boîte noire ne fait pas.

---

## D3 — Sémantique des couleurs ✅ validé

| couleur | sens | portée |
|---|---|---|
| **ambre** | action / actif | rang 1, série courante, focus |
| **bleu** | **origine : le système, pas toi** | recommandation, plan proposé, explication |
| graphite | surface, structure | fonds, filets |

**Le bleu est une règle, pas une décoration.** S'il ne sert qu'au badge de
recommandation, c'est une couleur de plus et pas un sens de plus : il doit
valoir partout où le contenu est produit par le système.

---

## D4 — Suppressions ✅ validé

**Retirer avant d'embellir.**

Cibles localisées et **vérifiées encore présentes** au 2026-08-18 — c'est ce qui
rend la décision actionnable plus tard sans réouvrir le dogfood :

| À retirer | Où | Motif opérateur |
|---|---|---|
| « Aucune séance active » | `app/templates/index.html:48` | n'apprend rien |
| doublon « Aujourd'hui » | `app/templates/index.html:26` (bandeau) + sous le résumé | répétition |
| vignette « Cette semaine » vide | `_partials/weekly_loop.html:8,14` · `_partials/home_coaching_loop.html:176` | *« ne sert strictement à rien »* |

Aucune de ces suppressions n'a été effectuée.

---

## D5 — Substitution descriptif → visuel (direction)

Remplacer les objets de texte par des objets visuels de cockpit, **dérivés des
données et des assets déjà présents**. Aucun moteur nouveau, aucune collecte
nouvelle. DA proche de Gravl, spécifiquement Auren.

---

## Rigueur de maquette

Deux reproches opérateur à ne pas répéter :

1. **Ne jamais montrer une vignette amputée.** Chaque maquette rejoue *toutes*
   les décisions déjà validées, pas seulement celle en cours de discussion.
2. **Pas de friction d'objets** : rythme vertical constant, lignes de base
   alignées, rembourrages uniformes entre cartes comparées.

---

## D6 — Le cycle est piloté par la récupération, pas par un calendrier ✅ validé

**Pas de « semaine 3/8, séance 2/4 ».** Le produit n'expose pas une progression
dans un plan linéaire.

> *« C'est dans un cycle en réalité, mais le cycle est plutôt à considérer comme
> le fait qu'il y ait des muscles fatigués, d'autres disponibles — et de chercher
> dans la cyclicité à toujours travailler dans la cohérence de ce qui est
> physiologiquement disponible. »*

**Conséquence majeure sur la conception** : l'état corporel n'est pas une
vignette décorative à côté de la recommandation. C'est **l'explication de la
recommandation**. Le hero dit « Push A » ; les plaques disent *pourquoi* — poussée
récupérée, tirage encore fatigué.

Les deux objets racontent la même histoire et doivent être conçus ensemble. Un
Accueil qui les juxtapose sans les relier rate la décision.

---

## D7 — La régularité est une métrique de premier plan ✅ validé

À mettre en avant, avec une nuance qui écarte le motif habituel :

> *« Pas de faire des séances tous les jours, mais une continuité, dans une
> intensité qui est notée. »*

**Pas un streak quotidien.** La continuité se mesure par le nombre de séances par
semaine, la **qualité du repos** et la **qualité du travail** — trois signaux que
le produit collecte déjà.

Un streak journalier récompenserait la présence ; ce produit doit récompenser la
cohérence. Un jour de repos bien pris ne doit jamais casser un compteur.

---

## D8 — Un onglet Progression ✅ validé

L'Accueil peut garder l'essentiel, mais l'exhaustif mérite sa page.

> *« C'est bien d'avoir un onglet progression qui, de manière exhaustive,
> explique. »*

Cela règle le fourre-tout « Résumé · indicateurs et navigation » : ce qui décide
reste sur l'Accueil, ce qui s'analyse déménage.

---

## D9 — Aucune anticipation au-delà de la séance proposée ✅ validé

**Ne pas afficher la séance N+2.**

> *« La séance d'après va être logiquement adaptée en fonction de la performance
> de la séance en cours. »*

Le produit **ne connaît pas** la suivante : elle dépend de ce qui va se passer
dans celle-ci. L'afficher serait une promesse que le moteur ne peut pas tenir —
la même faute que « Recommandé IA » sous une autre forme.

C'est aussi cohérent avec D1 : une décision par écran.

---

## État d'entraînement corporel — ce qui a bougé depuis le brainstorm

Le brainstorm concluait « c'est de l'assemblage ». **C'était faux**, et quatre
sprints l'ont établi :

| Constat | Sprint |
|---|---|
| Le rendu colorait par **rang DOM**, pas par identifiant — une plaque régénérée aurait recoloré le mauvais muscle | `OQ_POSITIONAL_CSS_01` (résolu) |
| **`zone_recovery` n'atteint aucun template** — le couplage « bande → couleur, identifiant → surface » était une intention, pas un mécanisme | `Sb_BODYMAP_IDENTITY_CONTRACT_01` |
| **4 zones sur 11** ont une géométrie ; 7 n'en ont pas | `Sb_BODYMAP_FRAME_ATLAS_01` |
| Les maillages BodyParts3D ne sont **pas versionnés** | `Sb_BODYMAP_ASSET_INTAKE_01` |

Le socle est prêt (moteur multi-cadres, contrat d'identifiants, couleur par
identité, porte d'intake). Ce qui manque n'est plus du code : c'est de la
**géométrie**, produite hors dépôt.

**Non tranché** : la traduction des bandes de récupération en libellés produit.
Même piège de double vocabulaire que le ressenti musculaire, où
`Sb_SESSION_REVIEW_SIGNAL_01` a délibérément affiché la valeur brute plutôt que
d'inventer une seconde table de libellés.

---

## Ce que ce document ne fait pas

- **Rien n'est implémenté.** Ni D1, ni D2, ni D3, ni D4, ni D5.
- Il ne remplace pas une spec de build : il fixe les **décisions**, pas le plan.
- Il ne préjuge pas de l'ordre des tranches d'implémentation.
- La direction D5 (« descriptif → visuel ») reste une **direction**, pas un
  inventaire d'objets à produire.

## Ce qui est déjà garanti par test

Une seule chose, mais elle est utile tout de suite : **l'interdit de D2**.
`tests/test_home_design_decisions.py` vérifie qu'aucune surface applicative ne
revendique « Recommandé IA ». Le moteur se décrit lui-même comme
*« Deterministic, explainable, zero-ML »* ; une revendication d'IA serait fausse
le jour où quelqu'un l'écrirait, pas le jour où on la relirait.
