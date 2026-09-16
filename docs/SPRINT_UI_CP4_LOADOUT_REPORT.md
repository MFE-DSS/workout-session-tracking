# UI-CP4 — LOADOUT · le registre typé

**Question possédée** : « avec quoi puis-je m'entraîner — quelle configuration
je choisis ? »

**Arbitrage opérateur** : concept **A — REGISTRE**, avec une correction
architecturale : *LOADOUT est un registre TYPÉ, pas une liste plate d'objets
sémantiquement identiques.*

---

## 1. Brainstorming / Options / Risques / Choix retenu (`CLAUDE.md §3`)

Trois modèles d'interaction ont été construits sur les **données réelles** du
catalogue semé, puis soumis à l'opérateur dans un artefact d'arbitrage.

| | Modèle | Verdict |
|---|---|---|
| **A** | **Le registre** — une ligne par configuration, dépli sur place, commande dans le dépli | **retenu** |
| B | La console de chargement — un emplacement « chargé » + rail de remplacement | écarté : décide bien, **compare mal**, et comparer est le cœur de la question |
| C | Par le corps — la zone comme entrée principale | écarté **sur preuve** (voir §2, fait 01) |

**Emprunt à B, retenu** : l'état de sélection vit dans la **requête**
(`?loadout=`), jamais en base. Patron déjà employé par EXECUTION (`?active=`,
`?rest=`) ; permet le dépli **sans JavaScript** ; n'invente **aucune**
sémantique de domaine.

---

## 2. Quatre faits mesurés, dont deux qui ont écarté l'évidence

### 01 · Les zones discriminent MAL — ce qui écarte le concept C

| Séance | Zones travaillées | Séries |
|---|---|---|
| Legs A — Quad dominant | Quadriceps · Ischios · Mollets · Core | 22 |
| Legs B — Postérieur dominant | Quadriceps · Ischios · Mollets · Core | 22 |
| Push A | Pectoraux · Delt. lat. · Delt. post. · Triceps | 21 |
| Push B | Pectoraux · Delt. lat. · Delt. post. · Triceps | 22 |

Deux paires **rigoureusement identiques** en zones. Seul le **nom** les sépare.
S'y ajoute que les programmes de l'utilisateur n'ont pas de zones fiables
(`focus` est une chaîne libre) : le concept C aurait rendu invisible la moitié
de LOADOUT.

### 02 · Le volume était le seul discriminant invisible

De **0 à 24 séries** sur le catalogue, affiché **nulle part**. Il est désormais
sur chaque ligne.

### 03 · Un nom promet ce que la donnée ne porte pas

« Session courte — Full upper **45 min** » prescrit **18 séries sur 7
exercices**, à peine moins que Push A (21). La durée n'existe pas comme donnée
structurée et une décision antérieure a refusé de l'estimer. **Le nom reste un
nom** : ni analysé, ni corrigé, ni promu en champ. Une garde statique interdit
au module de toucher au vocabulaire de la durée.

### 04 · Deux absences opposées étaient rendues identiques

Traité en §5.

---

## 3. L'ontologie typée finale

`WorkoutTemplate` et `UserProgram` restent **deux objets de domaine distincts**.
Aucune table n'est fusionnée. Ce qui fusionne est la **perception**.

| Type | Classe | Commande | Charge annoncée |
|---|---|---|---|
| **SÉANCE** | `SessionRow` | `Démarrer` — si le domaine sait l'exécuter | `21 séries · 7 exercices` |
| **PROGRAMME** | `ProgramRow` | **aucune** | `4 séances · 24 exercices` |

**La distinction est structurelle, pas conditionnelle.** `ProgramRow` n'a aucun
champ pouvant porter un démarrage — ni slug, ni identifiant de séance. Un START
inventé pour un programme n'est pas seulement interdit : il est **inexprimable**.
Une garde statique le vérifie sur les champs de la dataclasse, pas sur le rendu :
elle protège demain, pas seulement aujourd'hui.

**Un programme se démarre par l'une de ses séances**, et seulement quand le
domaine le dit : programme **publié**, **non archivé**, séance **matérialisée**
en gabarit. C'est la condition exacte qu'applique déjà `user_programs/detail.html` —
reprise, pas réécrite.

**Une séance non démarrable existe quand même** : elle se décrit, se compare, se
déplie, et dit pourquoi elle ne part pas. Première écriture : seules les
démarrables entraient dans `sessions`. Conséquence mesurée au rendu — sur un
**brouillon**, l'état où un programme passe le plus clair de sa vie, aucune
séance n'était dépliable, donc l'état `ZONES_UNKNOWN` **ne pouvait jamais
s'afficher**. Une branche que son entrée n'atteint jamais n'est pas une
précaution : c'est du code mort qui se croit vivant.

---

## 4. Le rang, et pourquoi il n'est pas un réflexe (§3 de l'arbitrage)

Trois axes candidats ont été confrontés aux données :

* **TYPE** — programme / séance ;
* **PROVENANCE** — à moi / catalogue ;
* **EXÉCUTABLE MAINTENANT** — démarrable / non démarrable.

⚠ **Sur le domaine actuel, les trois coïncident.** Tout programme appartient à
l'utilisateur ; tout gabarit du catalogue est commun ; un programme n'est jamais
directement démarrable là où une séance l'est toujours. Ce n'est donc pas un
arbitrage entre trois rangs mais **un seul rang que trois raisons justifient** —
et il fallait le dire ainsi plutôt que prétendre avoir tranché.

Les trois sections du catalogue (`core` / `utility` / `specialization`)
survivent : sémantique de décision réelle, déjà en base. Les effacer aurait été
une soustraction sans remplacement.

**Les séances de programme publié (`catalog_section = "user"`) ne sont pas des
lignes de premier rang** : elles vivent dans leur programme, qui est leur
composition réelle. Les rendre aussi en haut les dupliquerait sans raison de
décision.

---

## 5. Les trois absences de zone (§7 de l'arbitrage)

L'opérateur a corrigé la proposition sur ce point précis, et la correction porte
loin : **`KNOWN / INFERRED / UNKNOWN` est une grammaire de PREUVE, pas un
remplaçant des états de domaine.** Deux des trois états sont parfaitement
**CONNUS**.

| État | Ce que le produit sait | Rendu | Preuve |
|---|---|---|---|
| `NO_ZONES_DEFINED` | aucun exercice : il SAIT qu'aucune zone n'est prescrite | « Aucune zone prescrite — cette séance ne cible aucun groupe musculaire cartographié. » | **KNOWN** |
| `NO_PRIORITY_MATCH` | des zones existent, aucune déclarée | **les zones, sans marque** — aucune phrase d'absence | **KNOWN** |
| `ZONES_UNKNOWN` | des exercices existent, aucun reconnu | « Zones non cartographiées… », filet pointillé `--t-unknown` | **UNKNOWN** |

`NO_PRIORITY_MATCH` **n'écrit rien** : les zones rendues disent l'absence mieux
qu'une phrase, et l'écrire en ferait un reproche (`A4`).

⚠ **`ZONES_UNKNOWN` est inatteignable depuis le catalogue** : 80 exercices sur
80 y résolvent en `DB_EXACT`. Il ne peut venir que d'un programme écrit à la
main — c'est exactement ce que le labo sème, faute de quoi la garde aurait été
vacuante.

**Une garde a retourné une doctrine.** L'ancienne exigeait qu'un gabarit sans
zone ne rende **rien** (« pas de module vide, pas de "aucune zone" »). Mais
rendre le même vide pour « aucun exercice » et pour « exercices non reconnus »
confond une certitude avec une lacune. A4 interdit le module vide et le
reproche ; elle n'a jamais demandé de taire un fait.

---

## 6. L'ambre

**Mesuré avant** : `/library` portait **53 occurrences d'ambre** dans **trois
rôles** — 0 aplat, 11 bordures, 42 textes. L'ambre ne désignait plus une
décision, il coloriait une catégorie.

**Après** : `--t-amber` n'habille que la **commande dominante**, et une seule
ligne est dépliée à la fois. Le registre fermé n'en porte **aucun**.

⚠ **Une zone déclarée n'est plus en ambre**, et c'est un changement de doctrine
assumé : `--t-amber` est documenté « action utilisateur · objet actif ». Une
priorité déclarée n'est ni l'un ni l'autre — c'est un **rappel de ce que
l'utilisateur a dit**. La colorier en ambre est précisément ce qui produisait 42
textes ambre. Elle se distingue désormais par le **poids** et un **souligné** —
deux canaux non colorimétriques — et son sens complet reste dit hors écran.

**L'ambre revient au programme uniquement** quand aucune de ses séances ne peut
le porter (brouillon) : un écran garde un propriétaire d'action dominant, jamais
deux.

**Un état porte délibérément ZÉRO ambre** : un programme publié déplié, aucune
séance encore choisie. La décision qui attend là est un **choix parmi des
lignes**, et aucun élément ne la possède — en peindre un reviendrait à choisir à
la place de l'utilisateur. La phrase « Choisis la séance à démarrer » le dit ;
l'ambre apparaît quand la séance est choisie.

| État | Aplats ambre |
|---|---|
| registre fermé | **0** |
| une séance de catalogue dépliée | **1** — sa commande |
| un programme publié déplié, aucune séance choisie | **0** — le choix n'a pas de propriétaire |
| une séance de programme choisie | **1** — sa commande |
| un brouillon déplié | **1** — « Ouvrir le programme », sa seule capacité réelle |
| une séance de brouillon choisie | **1** — toujours celle du programme |

---

## 7. La formule unique de séries de travail

`loadout.work_sets()` — *plages de reps prescrites, hors échauffement* — et elle
vaut pour les deux arbres via `getattr(rt, "is_warmup", False)`.

⚠ **Le plan de tranche annonçait « deux formules concurrentes ». Vérifié dans le
code : c'était faux.** `RepTarget` (catalogue) n'a **aucune** colonne
`is_warmup` — les échauffements y sont générés à l'instanciation, jamais
stockés. Les deux écritures rendaient la même valeur ; ce qui divergeait était
la **définition**, pas le **résultat**. Et le troisième compte soupçonné
(`user_programs.py`, `existing_set_count`) ne mesure pas une charge : il énonce
ce qu'une régénération **détruirait**. Trois questions différentes, pas trois
réponses à la même.

Vérifié au labo : une séance à 1 échauffement + 4 séries de travail annonce
bien **4 séries**.

---

## 8. Capacités préservées (`CLAUDE.md §5.3`)

| Capacité | Avant | Après |
|---|---|---|
| Démarrer depuis le catalogue | carte → bouton | ligne → dépli → commande |
| Démarrer une séance de programme publié | `/programs/<id>` | **aussi** depuis le registre |
| Ouvrir / éditer un programme | `/programs` | ligne de programme → « Ouvrir le programme » |
| **Créer un programme** | bouton de `/programs` | **lien du rang « Mes programmes »** |
| Filtrer par zone | `?zone=` | inchangé |
| Déclarer ses priorités | lien « Modifier » | inchangé |
| Route `/programs` | — | **conservée**, aucune route supprimée |

⚠ **Le piège le plus vicieux de la tranche.** L'entrée de coque « Mes
programmes » disparaît. Si le rang s'effaçait faute de programme, **créer un
programme deviendrait inatteignable** pour exactement l'utilisateur qui en a le
plus besoin — et l'anomalie serait **invisible sur un compte peuplé**, donc
invisible sur toute capture de démonstration. Le rang survit à son propre vide ;
une garde le vérifie.

Sous filtre de zone il s'efface en revanche comme les autres : « aucun programme
ne travaille cette zone » est une réponse au filtre, et y afficher « aucun
programme personnel » mentirait sur la cause du vide.

---

## 9. Coque

Deux liens secondaires partent — « Mes programmes » et « Explorer » — parce
qu'ils menaient à deux surfaces qui n'en font plus qu'une, et que l'onglet
primaire « Programmes » y mène déjà. Un lien secondaire qui double une
destination primaire est précisément ce que la règle du menu interdisait déjà.

Les variables `is_my_programs` et `is_library` partent avec eux : une variable
qui ne décide plus rien n'est pas neutre — la personne suivante la trouverait et
croirait à un oubli de câblage.

**Conséquence de nommage** : la page s'appelait « Explorer », enfant du domaine
« Programmes ». Elle absorbe « Mes programmes », elle **est** le domaine, et
porte son nom. Le défaut que l'ancien nom évitait — trois niveaux pour le même
mot — ne revient pas : les rangs disent « Mes programmes » et « Séances… »,
jamais « Programmes » une seconde fois.

---

## 10. Hors périmètre, tenu

Aucune migration globale de cards ou de tokens · aucune fusion de persistance ·
aucune sémantique de « programme actif » · aucun widget CP3.6 · MISSION reste
fermée · `/science` intouché · `recommendation.py` intouché · aucune migration.

`.template-card` reste **vivant** sur `launcher` et `template_detail` : c'est
une tranche de surface, pas une migration de composants. Aucune règle CSS n'a
été supprimée.

**`/programs` reste une surface vivante, et ce n'est pas un oubli.** Elle n'est
plus dans la coque, mais elle est le **parent du flux d'édition** : les pages
`user_programs/detail.html` et `new.html` y reviennent par « ← Mes programmes ».
Ce n'est donc pas une route orpheline — le défaut documenté d'`/export`, une
surface inatteignable autrement qu'en tapant l'URL.

La frontière est nette : **LOADOUT choisit ; `/programs` et ses enfants
gèrent le cycle de vie.** Le lien de retour appartient au second domaine, pas au
premier ; le repointer vers LOADOUT aurait fait traverser une frontière que
cette tranche vient justement d'établir.

**PROGRAM_LIFECYCLE** (créer / éditer / archiver / restaurer) est consigné comme
responsabilité distincte, **hors LOADOUT**. LOADOUT choisit et inspecte ; il ne
gère pas de cycle de vie. Le cul-de-sac d'archivage déjà consigné — service sans
route, message de quota promettant un archivage inatteignable — **reste ouvert**
et n'est pas un bloqueur CP4.

---

## 10 bis. Mesures — AVANT vs APRÈS, sur le même labo

**Labo représentatif** (7 cas exigés par §12) : priorités déclarées
(Dos épaisseur · Épaules · Bras) · un programme **publié** matérialisé d'un plan
(4 séances, 24 exercices) · un **brouillon** fait à la main · séances force ·
une séance cardio **sans série prescrite** · les paires A/B **aux zones
identiques** · une séance aux exercices **non reconnus** du référentiel.

⚠ Le septième cas n'existait pas avant cette tranche : **80 exercices sur 80 du
catalogue résolvent en `DB_EXACT`**, donc `ZONES_UNKNOWN` est inatteignable
depuis le catalogue seul. Sans le semer, la garde aurait été vacuante.

### 390 × 844

| Compteur | AVANT `/library` | AVANT `/programs` | APRÈS registre fermé | APRÈS max déplié |
|---|---|---|---|---|
| Écrans | **4,14** | 1,00 | **2,36** | 2,96 |
| Destinations | 2 | | **1** | |
| Mots visibles | 436 | 19 | **208** | 275 |
| Conteneurs | 26 | 5 | **2** | 12 |
| Commandes visibles | 28 | 3 | 18 | 24 |
| Formulaires de démarrage | **13** | 0 | **0** | **1** |
| **Ambre — aplat** | 0 | 1 | **0** | **1** |
| **Ambre — bordure** | 11 | 1 | **0** | **0** |
| **Ambre — texte** | 42 | 0 | **0** | **0** |
| **Ambre — total** | **53** | 2 | **0** | **1** |
| Débordement horizontal | non | non | **non** | **non** |

**5,14 écrans sur deux destinations → 2,36 sur une.** **53 occurrences d'ambre
dans trois rôles → 1 aplat, et seulement quand une décision attend.**

### Gestes

| | AVANT | APRÈS |
|---|---|---|
| Inspecter une configuration | 1 — **change de page** | 1 — **sur place** |
| Démarrer | 1 | **2** |

Le geste supplémentaire est **assumé** : c'est le prix de l'interdiction du
démarrage accidentel. Avant, treize boutons « Démarrer » étaient visibles d'un
coup ; un pouce qui glissait lançait une séance.

### Cibles tactiles · large

Poignée **69 px**, commande **46 px** — au-dessus du plancher produit de 44
(`UIV3_TARGETS_44_01`). À 1280 px, la poignée est bornée à **720 px** : le
registre ne s'étire pas jusqu'aux bords, la charge se pose au bout du nom et non
au bout de l'écran.

### Registre filtré

`?zone=lats` : **1,89 écran**, 4 configurations sur 15, et **chaque ligne porte
la zone demandée**.

⚠ **Trois occurrences d'ambre y subsistent** — la puce de filtre active
(bordure + texte) et son rappel dans le repli. Style **préexistant**
(`.zone-filter__chip.is-active`), non touché par CP4, et défendable : l'ambre y
marque le filtre que l'utilisateur a lui-même choisi, donc un objet actif au
sens de la doctrine. **Consigné, pas corrigé en douce.**

### L'écart avec mes estimations d'arbitrage

L'artefact soumis à l'opérateur portait des **estimations de conception**,
étiquetées comme telles, avec l'engagement de rapporter l'écart.

| | Estimé | Mesuré | Écart |
|---|---|---|---|
| Écrans | ≈1,6 | **2,36** | **+48 %** — j'étais optimiste |
| Conteneurs | 1 | **2** | +1 |
| Occurrences d'ambre | 1 | **0** fermé / **1** déplié | tenu |
| Formulaires de démarrage | 1 | **1** | tenu |

Les deux tenus portent sur ce que la tranche **décide** ; le raté porte sur ce
qu'elle **produit**. Une estimation de hauteur faite sans écrire le CSS reste
une estimation de hauteur.

---

## 10 ter. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

Décision par décision, contre ce qui vient d'être écrit. Un relevé de décisions
n'est pas un menu dans lequel on choisit les items commodes.

### `DESIGN_DECISIONS_UIV2_SURFACES.md`

| Décision | Verdict | Comment |
|---|---|---|
| **Q1** — la connexion porte l'identité | non concernée | surface non touchée |
| **Q2** — ancre visuelle de l'accueil | non concernée | MISSION reste fermée |
| **Q3** — « état du jour » replié | non concernée | |
| **Q4** — la ligne de série est un instrument | non concernée | EXECUTION non touchée |
| **Q5** — trois rangs de surface | **respectée** | ligne = rang 2 (un filet, aucun cadre) · dépli = rang 1 (fond plus présent, il porte la commande) · notes et méta = rang 3 (typographie et espace seuls). **La carte redevient un signal : il n'y en a plus aucune ici.** |
| **Q6** — échelle 32 / 22 / 15 / 12 | **respectée, après correction** | ⚠ première écriture : 12,5 · 11,5 · 10 px — **trois barreaux inventés** à côté de l'échelle. Corrigé : nom au rang BODY (15), tout le méta au rang META (12), le genre distingué par **interlettrage et couleur**, qui ne coûtent aucun rang. Coût mesuré de la correction : **+0,08 écran**. La limite connue `.btn` à 14 px est héritée, non aggravée. |
| **Q7** — un seul aplat ambre par écran, **strict** | **respectée** | 0 fermé · 1 déplié · jamais 2. Vérifié sur 8 états. |
| **Q8** — aucune opacité décorative, tout par token mesuré | **respectée** | aucune valeur littérale, aucun `rgba()` introduit ; `--t-unknown` employé pour ce qu'il désigne |
| **Tokens bleus** | non concernée | aucun bleu introduit |

### `AUREN_VISUAL_BACKBONE.md` — invariants non négociables

| Invariant | Verdict |
|---|---|
| `no-color-only-state` — un état porte toujours une forme | **respectée** — priorité déclarée = poids + souligné ; zones inconnues = phrase + filet pointillé |
| Cible tactile 44 px (standard produit, pas WCAG 24) | **respectée** — poignée 69 px, commande 46 px |
| `SSR is the functional baseline` | **respectée** — **zéro JavaScript** ; le dépli est un lien |
| Écriture d'entraînement récupérable sans JS | **respectée** — `POST` de formulaire inchangé |
| Contraste = contrat de couple | **respectée** — aucun couple nouveau : tokens existants sur fonds existants |
| Aucune sémantique de cible dans `zone_exposure` | non concernée — module non touché |
| Aucun style inline statique | **respectée** — aucun introduit |
| §4.2.3 — la commande dominante **peut** être un trait | **respectée** — l'aplat reste licite (`Q7` le plafonne à un), et il est ici le seul objet coloré de l'écran |

**Aucune décision violée.** Une a été corrigée en cours de tranche (`Q6`), et la
correction est mesurée plutôt qu'affirmée.

---

## 11. Défauts trouvés PENDANT la tranche, et par quoi

Aucun n'a été trouvé en relisant le code. Chacun a été trouvé par une mesure,
un rendu, ou une garde — c'est le seul point qui compte.

| # | Défaut | Trouvé par |
|---|---|---|
| 1 | **Une branche que son entrée n'atteint jamais** — sur un brouillon, aucune séance n'était dépliable, donc `ZONES_UNKNOWN` ne pouvait **jamais** s'afficher. | le **rendu** du brouillon |
| 2 | **Un second résolveur de zones**, avec ses propres constantes d'état, à côté de celui du produit — et `annotate_templates` rendu mort du même geste. | relecture après un `grep` de consommateurs |
| 3 | **Créer un programme serait devenu inatteignable** à zéro programme, une fois l'entrée de coque retirée. Invisible sur un compte peuplé. | raisonnement sur `§5.3`, confirmé par mutation |
| 4 | **Le filtre ne justifiait plus aucune ligne** : les zones passées au dépli, un registre filtré gardait huit lignes sans dire pourquoi. | une garde de 2026 (`Sb_UI_BIBLIO_01`) qui avait **déjà** arrêté ce défaut une fois, en sens inverse |
| 5 | **Le dépli débordait de 14 px** à droite des lignes en large. | la **capture** à 1280 px |
| 6 | **Le registre aurait fait trois lignes par configuration** — l'inverse du but. | maquette, avant d'écrire le CSS |
| 7 | **Je réécrivais le pluriel** que `app/templating.py` possède déjà, nommé et gardé. | une garde de prose (`test_no_parenthesised_plural`) |
| 8 | **Le titre d'onglet disait encore « Explorer »** alors que la surface ne s'appelait plus ainsi nulle part à l'écran — et une garde de nommage passait donc **pour la bonne raison apparente** : la chaîne était bien dans la page, dans le `<title>`. | le sweep complet, en cherchant pourquoi UNE garde du fichier passait quand trois tombaient |
| 9 | **Une méthode morte survivait avec son savoir** — `TemplateZones.shown()`, dont le dernier appelant était la carte supprimée. | `grep` d'appelants après coup |

### Deux erreurs de MESURE, pas de produit

* **Le serveur servait l'ancien code.** `uvicorn` sans `--reload` : deux séries
  de mesures décrivaient l'implémentation précédente, et j'ai commencé à
  diagnostiquer un bug de service qui n'existait pas. Le service interrogé
  directement a tranché en une commande. **Un serveur lancé n'est pas un code à
  jour** — 8ᵉ forme de « mesurer le mauvais objet ».
* **`&` devient `&amp;` dans un attribut.** Mon extracteur de clés de test
  cherchait `[?&]loadout=` ; sous filtre l'URL porte `?zone=…&amp;loadout=…`, la
  classe voyait « ; », et le registre filtré **paraissait vide** alors qu'il
  rendait ses lignes. La garde accusait le produit de son propre défaut
  d'écriture.

### Deux défauts que je connais et que j'ai refaits

* **Une garde qui lit sa propre prose** : mon commentaire expliquant le retrait
  de `is_my_programs` faisait tomber la garde qui vérifiait ce retrait. 13ᵉ
  instance recensée dans ce dépôt.
* **Borner un fragment HTML au premier `</li>`** : les zones sont une liste
  **imbriquée**, donc le premier `</li>` ferme une zone, pas le dépli. Trois
  gardes ont alors accusé le produit de ne pas marquer ce qu'il marquait.
  ⚠ **Le fichier que je modifiais documentait déjà ce piège, en toutes lettres,
  à propos des cartes.**

---

## 12. Gardes

**Nouveau fichier `tests/test_ui_cp4_loadout.py` — 27 gardes**, dont deux
**vérifiées par mutation** (le défaut planté, la garde rouge, l'arbre restauré) :

* `ProgramRow` reçoit un champ `slug` → **rouge** ;
* le rang « Mes programmes » cesse de survivre à son vide → **rouge**.

La première est **statique et porte sur les champs de la dataclasse**, pas sur
le rendu : une garde de rendu vérifie qu'on n'affiche pas un START aujourd'hui ;
celle-ci vérifie qu'on ne *peut pas* l'afficher demain.

**Gardes existantes REPOINTÉES, jamais supprimées** — 24 assertions dans 6
fichiers épinglaient une **écriture** (la carte, « Explorer », « Catalogue
complet », treize formulaires visibles) là où elles protégeaient une
**propriété**. Chacune a été réécrite sur sa propriété, avec la raison du
déplacement inscrite dans le test.

Deux ont été **renforcées** au passage :

* « aucun formulaire dans une carte » devient **« aucun formulaire dans aucun
  lien »**. L'ancienne ne regardait que `template-card__link` : sur une surface
  sans carte elle serait passée au vert **sans rien observer**.
* « le texte libre `focus` ne double pas les zones » devient **« `focus` ne
  remonte nulle part sur cette surface »** — une absence totale au lieu d'une
  substitution conditionnelle.

Une a **changé de doctrine**, en le disant : `A4` interdit le module vide et le
reproche ; elle n'a jamais demandé de **taire un fait**. Une séance sans zone
prescrite le dit désormais.

### Le rayon d'impact, mesuré et non supposé

`check_scope` a classé la tranche **`SHARED_CODE`** — `base.html` est observé
globalement, `template_zone_context` est importé ailleurs. Le tier autorise à
sauter le sweep complet en local ; **il a été lancé quand même**, et c'était le
bon choix :

| Où | Gardes tombées |
|---|---|
| Fichiers que j'éditais | 19 |
| **Ailleurs dans le produit** | **8** — `test_library` · `test_morpho_dogfood` · `test_no_parenthesised_plural` · `test_recommendation_telemetry` · `test_session_flow` · `test_ux4_02c_coherence` (×3) |

**Huit gardes qu'aucun filtre `-k` n'aurait nommées.** Un sweep ciblé borne ce
qu'on a pensé à nommer, pas le rayon d'impact.

⚠ **J'AI ÉDITÉ PENDANT LA MESURE, DEUX FOIS.** Le premier sweep corrigeait ce
qu'il découvrait au fur et à mesure : ses premiers lots ont jugé un code déjà
remplacé. Il a servi à **découvrir**, pas à certifier.

Le second a subi la même chose, une fois, vers son lot 55 — le remplacement de
`aria-expanded` par `aria-current` sur les poignées. Plutôt que de le déclarer
sans conséquence, le rayon en a été **borné** :

* **aucun** test ni script du dépôt ne référence `aria-expanded` (recherche
  exhaustive) ;
* la seule garde qui compte les `aria-current` compte `="page"`, distinct du
  `="true"` employé ici — comme les puces de filtre le font déjà ;
* les **78 gardes** qui rendent cette surface ont été rejouées sur l'arbre
  **d'après** le changement.

Le verdict du sweep vaut donc pour l'arbre livré. **La bonne pratique reste de
geler l'arbre avant de mesurer** — c'est une discipline que cette tranche a
enfreinte deux fois, et l'avoir rattrapée par une mesure ne l'excuse pas.

---

## 13. Vérification

| Contrôle | Résultat |
|---|---|
| `check_scope` | `SHARED_CODE` |
| `ruff` sur tous les fichiers touchés | vert |
| `check_ruff_budget` | 267 / 548 |
| `check_spec_protocol` | vert |
| Pré-scan `python:S9073` | 0 — un assert composite **préexistant** séparé au passage (`MAJOR`, poids 15) |
| Gardes ciblées | 87 vertes sur les 6 fichiers repointés, 27 sur le fichier neuf |
| Mutation | 2 défauts plantés, 2 gardes rouges, arbre restauré |
| Sweep local complet, chemin absolu, **sans pipe** | **`tous les lots sont verts.`** — 331/331 fichiers, 98 lots, pic 2023 Mo / budget 2256, aucun fichier sauté |
| Rendu exposé à l'opérateur avant tout commit de gabarit (`§5.1`) | **fait** — 5 captures, 8 états |
