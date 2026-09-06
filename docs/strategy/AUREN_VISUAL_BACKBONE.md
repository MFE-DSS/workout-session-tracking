# `AUREN_VISUAL_BACKBONE` — le socle visuel, gravé

> **Statut : `NORMATIF` sur ce qu'il affirme, `PROVISOIRE` sur ce qu'il marque
> comme tel.** Écrit le 2026-09-04 au terme du `BLOC 0` du
> `PHILOSOPHICAL UI RE-DESIGN PASS`, et validé par la première matérialisation
> réelle (`P-03`, viseur, trois états).
>
> **Ce document est la mémoire de référence du produit sur son aspect visuel.**
> Il existe parce qu'une conversation n'en est pas une. Tout agent ou humain
> qui touche à une surface d'AUREN le lit d'abord.
>
> Il **ne remplace pas** `AUREN_UIUX_V3_FOUNDATION_CONTRACT` : il en supersède
> des points nommés (§8) et en confirme d'autres (§7, §9, §10).
>
> Compagnons : `AUREN_UI_DECISION_BACKLOG` (ce qui reste à trancher) ·
> `AUREN_UI_REARBITRATION_REGISTER` (l'inventaire des 79 objets).

---

## 1. Le principe produit — `PH-01`

> **AUREN n'est pas un journal d'entraînement. C'est un instrument
> d'allocation de ressource.**

Une ressource finie — énergie, endurance, capacité — se **dépense** pour
produire du stress d'entraînement, donc de la performance. Le cockpit existe
pour **optimiser cette allocation**.

**Conséquences qui gouvernent tout le reste :**

* La **jauge** est la représentation native du produit, pas un ornement.
* La question de chaque écran n'est pas *« que dois-je montrer ? »* mais
  **« où en est la ressource, et qu'est-ce que cette action va lui coûter ou
  lui rendre ? »**
* **Allocation, pas suffisance.** Une jauge montre *où est passée l'énergie*,
  jamais *si tu en fais assez*. Ce refus est **testé** —
  `test_the_service_never_names_a_target` interdit les mots `target`, `cible`,
  `optimal`, `undertrained`, `recommend` dans `zone_exposure`. Sa docstring dit :
  *« le refus qui définit l'instrument »*.

---

## 2. L'échelle de profondeur — **dérivée du produit, pas inventée**

La profondeur visuelle **encode la profondeur structurelle**. Un objet paraît
posé sur un autre parce qu'il est **dedans**.

| Niveau | Ce que c'est | Traitement |
|---|---|---|
| **1 — châssis** | le fond, le backbone du cockpit | surface la plus basse, pas d'élévation |
| **2 — instruments** | tableau de bord, profil, programmes | logement, bordure, encastrement |
| **3 — modules** | ce qu'un instrument contient | plaque encastrée dans le logement |
| **4 — en vol** | séance en cours, séries, substituts, alternatives | l'objet actif, seul à porter la lueur |

**Ces quatre niveaux ne sont pas une échelle neuve** : ce sont les quatre fonds
`--t-void` / `--t-base` / `--t-surface` / `--t-raised` déjà déclarés et mesurés
par `UIV3_COCKPIT_LADDER_01`, auxquels la structure produit donne un sens.

> ⚠ **DÉFAUT OUVERT, trouvé le 2026-09-04 en exposant `U1`.** La marche
> **L0→L1 vaut 1,065**, sous le plancher de perception de **1,12** que le
> projet s'est lui-même fixé — et la garde ne la vérifie pas
> (`test_adjacent_depth_steps_are_perceptible` boucle sur `for i in (1, 2)`).
> À 1,065, **le châssis et le champ ne se distinguent pas à l'œil**. Deux
> issues, et c'est un arbitrage : soit L0 n'est pas un niveau produit (un vide
> de cadrage, jamais lu comme surface), soit sa valeur change. **`U2` bute
> dessus.**

**L'imbrication est l'objectif, pas une tolérance** — à condition d'être
**codifiée** : un châssis contenant des instruments est légitime ; une carte
dans une carte sans responsabilité propre ne l'est pas.

**Forme et profondeur sont indépendantes.** Un composant peut être arrondi et
parfaitement plat. Le rayon appartient à la forme (`SYS-022`), l'élévation à la
profondeur (`SYS-078`).

---

## 3. Le langage

### 3.1 Couleur — **rôles d'abord, valeurs ensuite**

**Ne jamais raisonner « vert = succès, ambre = action ».** Toujours
`RÔLE → TOKEN → VALEUR`.

**25 rôles**, livrés par `U1`. ⚠ *J'avais écrit « 16 » avant d'avoir lu le CSS :
neuf rôles existaient déjà dans le produit et manquaient à mon ontologie
(`action-hover`, `action-dim`, la triade bleue, `data-unknown`,
`glyph-decorative`, et un quatrième niveau de surface). Le code avait raison.*

| Groupe | Rôles |
|---|---|
| **surface** | `surface-chassis` L0 · `surface-canvas` L1 · `surface-group` L2 · `surface-instrument` L3 |
| **texte** | `text-primary` · `text-secondary` · `text-muted` · `text-on-action` |
| **structure** | `border-subtle` · `border-emphasis` · `glyph-decorative` *(non-texte)* |
| **action / interaction** | `action-primary` · `action-hover` · `action-terminal` · `action-dim` · `state-active` · `focus` |
| **provenance** | `origin-system` · `origin-system-data` · `origin-system-line` |
| **donnée** | `data-unknown` — l'absence n'est ni une action ni une production |
| **support** | `support-information` · `support-success` · `support-warning` · `support-error` |

**Deux distinctions non négociables :**
`origin-system ≠ support-information` — la provenance n'est pas une nature de
feedback. `action-primary ≠ state-active` — même s'ils aliasent aujourd'hui la
même valeur ambre.

**Valeurs de départ** — la palette AUREN existante et **mesurée** (`§4`),
reprise et améliorée, **jamais table rase** :

```
ambre     #C8A24B     action dominante · objet ou état actif
bleu      #7DD3FC     origine système — ce que le moteur produit
          #5FA8D3 · #4A7FB5
graphite  #0F1318 · #151A21 · #1B2029     surfaces et filets
```

Toute valeur modifiée est **repromue en token avec sa mesure de contraste**
(`CLAUDE.md §5.4`). `var(--token-inexistant, #hex)` reste interdit.

**Interdiction conservée** : la **récupération** ne reçoit **jamais** de
sémantique feu tricolore. Les rôles `support-*` existent pour le feedback
d'opération — formulaire, erreur, succès — **jamais** pour `RECOVERY BAND`,
`RECOVERY ZONE`, `RECOVERY ESTIMATE`.

### 3.2 Typographie — quatre rôles, deux modificateurs

| Rôle | Emploi |
|---|---|
| `DISPLAY / ACTION` | titre de surface, valeur d'instrument |
| `SECTION` | titre de bloc |
| `BODY / READOUT` | corps, lecture |
| `META / MICRO` | étiquette, provenance, légende |

**Modificateurs** — `NUMERIC` (`tabular-nums` obligatoire pour toute valeur
comparable ; mono uniquement quand la comparaison d'instrument y gagne) ·
`EMPHASIS` (graisse gouvernée).

> **`NUMERIC` est un modificateur, jamais un rang de taille.** Une valeur
> chiffrée reçoit le rôle de son emploi — instrument, corps ou méta — et le
> modificateur par-dessus.

**Valeurs finales : `PROVISOIRE`.** Elles exigent `PREVIEW TYPOGRAPHY / DENSITY`
approuvée avant de superséder `FOUNDATION_CONTRACT §8`.

**Défaut mesuré à corriger** : aujourd'hui `body` vaut 14 px et
`section-header` 13 px — **le titre de bloc est plus petit que le corps qu'il
introduit**, sur 101 usages.

### 3.3 Densité — **deux contextes nommés**

| Contexte | Régime |
|---|---|
| **`EFFORT`** | dense — tous les instruments pertinents présents simultanément |
| **`LECTURE`** | aéré — peu d'objets, une action claire |

Le **density budget** de `FOUNDATION_CONTRACT §9` est **conservé intégralement**
— il mesure des *outcomes*, pas des tokens : px avant le CTA dominant · px
vides · objets interactifs · **scroll avant l'action principale, cible 0**.

**La densité est contextuelle, jamais spécifique à une page.**

### 3.4 Mouvement — autorisé, subordonné

Le mouvement **sert un état qui change**, jamais l'agrément. Le défaut reste
**statique et fin**. `prefers-reduced-motion` est un contrat, pas une option.

### 3.5 Texture — décorative **et** structurelle

Scanlines, grain et lueur de phosphore sont autorisés :
**décoratifs** au service de la direction artistique, **et structurels** —
*« tout doit vivre dans l'objet »*.

> **Contrainte de premier rang qui les rend soutenables :
> le texte doit être intuitif et très simple.** Peu de texte, gros, simple.
> C'est ce qui paie le grain.

---

## 4. Le patron d'instrument — **prouvé par `P-03`**

Validé par l'opérateur le 2026-09-04 sur trois états rendus.

### 4.1 Composition

```
fil d'état          position · précédent · suivant · retour
titre               nom de l'objet + affordance de rang 2
méta                une ligne, majuscules, discrète
plaque              l'illustration ou le contenu explicatif, annoté
readout souverain   la valeur, très grande, en phosphore
jauge à verdict     segments : forme ET couleur
référence           la dernière fois, en bleu système
incréments          manipulation directe, cible ≥ 44 px
commande            un TRAIT, pas un aplat
```

### 4.2 Règles qui en sortent

1. **Le châssis remplace la carte** sur une surface d'instrument.
2. **Un changement d'état se lit par le châssis entier**, jamais par un objet
   qui surgit. Le repos en est la preuve : même instrument, autre phosphore.
3. **La commande dominante peut être un trait.** L'aplat n'est pas nécessaire à
   la domination — la cible tactile, si.
4. **Un verdict porte forme *et* couleur.** Flèche haute au-dessus de la cible,
   tiret à la cible, curseur sur l'élément courant.
5. **Le rang 2 vit sur le titre**, pas dans un bouton concurrent.
6. **Aucun espace perdu** : ce qui n'est pas utile à un état se replie et rend
   sa place au readout.

### 4.3 Contrat de lecture — deux coups d'œil

| Rang | Ce qui doit être compris |
|---|---|
| **1 — sans lire** | l'objet · où j'en suis · la valeur en cours · la référence |
| **2 — au second regard** | ce qui précède et suit · ce qui est substituable · comment bien faire |

---

## 5. Invariants non négociables

* **`no-color-only-state`** (`§7`) — un état porte toujours une forme.
* **Cible tactile 44 px** — standard produit, pas le seuil WCAG de 24.
* ~~**Sans JavaScript** (`§10`)~~ — **SUPERSÉDÉ le 2026-09-06.** Voir `§5bis`.
* **Le client possède l'interaction, le serveur possède la vérité** — la
  couche cliente peut porter l'état d'un écran ; **aucune donnée d'entraînement
  ne dépend d'elle pour survivre.** Voir `§5bis`.
* **Contraste = contrat de COUPLE**, jamais propriété d'un token seul. Chaque
  couple `avant-plan / arrière-plan` déclare son minimum et sa mesure.
* **Aucune sémantique de cible** dans `zone_exposure` — garde vivante.
* **Aucune revendication d'activation musculaire** (`%`, EMG) dans une
  illustration. Dessiner le **geste** est autorisé ; affirmer l'**effet** ne
  l'est pas.
* **Validation implicite** — `Entrée`/`Done`, jamais au `blur` (`DF-B`,
  `D9`/`D10`).
* **Aucun style inline statique non contracté** — l'inline ne survit que pour
  une valeur réellement dynamique, allowlistée. Mesuré : **5 sur 708**.

---

## 5bis. La couche cliente — amendement du 2026-09-06

**Décision de l'opérateur, prise explicitement.** L'invariant « sans
JavaScript » est levé au profit d'une **couche cliente structurée** : état
partagé entre objets, composants réutilisables, éventuellement une petite
bibliothèque.

### Pourquoi il est levé

Il n'a pas échoué — il a **plafonné**. Le programme UI a montré, objet après
objet, des défauts que le rendu serveur seul ne peut pas résoudre : un profil
qui affiche les données groupées par domaine et les fait éditer groupées par
stockage, avec **cinq liens vers quatre ancres de la même page** ; des tiroirs
qui perdent leur état à chaque soumission ; une saisie qui reposte l'écran
entier pour changer un nombre.

Ces défauts sont **structurels au rendu par page**, pas à l'écriture des
gabarits. C'est le motif que l'opérateur nomme « step two ».

### Ce qui devient possible

* un objet **cohérent** là où il y a aujourd'hui six blocs qui se renvoient
  les uns aux autres ;
* l'**édition en place**, sans rechargement ni saut d'ancre ;
* un **état partagé** entre objets d'un même écran ;
* des **composants** réutilisables, au lieu d'une classe CSS par forme.

### La frontière, et elle est dure

> **Le client possède l'interaction. Le serveur possède la vérité.**

Une séance en cours est un **enregistrement d'entraînement** : si le navigateur
meurt entre deux séries, ce qui a été saisi ne disparaît pas. Aucune donnée ne
vit uniquement dans la mémoire du client. C'est la seule limite que cet
amendement pose à la décision, et elle protège l'objet même du produit.

⚠ *Cette frontière est ma proposition à l'intérieur de la décision de
l'opérateur, pas sa formulation. Elle est écrite pour être contestée, pas pour
être supposée.*

### ⚠ L'invariant n'est pas une phrase — il est tenu par 48 fichiers de tests

**Mesuré le 2026-09-06 : 84 mentions de « sans JS » / « sans JavaScript » /
« repli sans » dans 48 fichiers de `tests/`.**

Lever la phrase de ce document est une ligne. L'invariant, lui, est **exécuté**
— sur le flux de séance (`test_df_b_session_flow`), le héros de décision
(`test_home_decision_hero`), le minuteur de repos, la carte corporelle, la
coque, les préférences d'entraînement, l'installabilité PWA.

Ces gardes ne tombent pas d'elles-mêmes : elles ne mordront que sur les
surfaces **qui basculent**. Mais chaque bascule les rencontrera, et il faudra à
chaque fois **décider** — la garde protège-t-elle une capacité que le produit
garde (« la séance s'enregistre même sans script »), ou seulement le moyen
d'hier ? Les deux réponses existent dans ce lot, et elles ne se devinent pas
en masse.

C'est le chiffre à provisionner, pas la ligne du `§5`.

### Ce que ça CASSE, et qu'il faut refaire

Ce point n'est pas une réserve : c'est un coût à provisionner.

* **Les gardes de rendu cessent de mesurer.** Une bonne partie des gardes UI
  lisent le HTML **servi**. Sur une surface dont l'interaction vit côté client,
  ce HTML ne décrit plus l'écran — la garde reste verte et ne garde rien. C'est
  la forme la plus dangereuse du défaut relevé dans
  `guards-that-guard-nothing`, appliquée d'un coup à une famille entière.
* **Le harnais de capture doit être refait.** Il photographie un rendu initial.
  Il devra piloter des **états**, pas des routes.
* **`CLAUDE.md §5.1`** — l'exposition au rendu avant commit — devient *plus*
  nécessaire, pas moins : c'est la seule garde qui continue de voir juste.

### Ce qui n'est PAS décidé

* **quelles surfaces basculent, et dans quel ordre** — l'opérateur a nommé
  `/profile` comme première ;
* **quelle bibliothèque, s'il y en a une** — « zéro framework » était une
  décision distincte, elle n'est pas levée par celle-ci ;
* **le sort des surfaces servies** qui n'ont aucune raison de basculer.

### Ce qui ne change pas

Tous les autres invariants du `§5` restent entiers : cible tactile 44 px,
`no-color-only-state`, contraste comme contrat de couple, validation implicite,
aucune revendication d'activation musculaire, aucune sémantique de cible dans
`zone_exposure`. Aucun d'eux ne dépendait du mode de rendu.

---

## 6. Ce que ce document supersède

| Contrat ancien | Remplacé par | Condition |
|---|---|---|
| `SYS-078` « surface par défaut sans ombre, une seule élévation » | **§2** l'échelle à 4 niveaux | ✅ appliqué |
| `VIS-015` « interdire les cartes imbriquées » | **§2** l'imbrication codifiée est l'objectif | ✅ appliqué |
| `SYS-014` « ambre = action utilisateur » | **§3.1** l'ontologie des rôles | ✅ appliqué |
| `FOUNDATION_CONTRACT §8` Typography | **§3.2** | ⏳ **après `PREVIEW TYPOGRAPHY` approuvée** |
| Système d'ombres `--shadow-sm/md` | **§2** | ⏳ après `PREVIEW CHROME` |
| Générations `--t-*` et `--color-*` | **§3.1** | ⏳ après table de migration |

`FOUNDATION_CONTRACT §7` (no-color-only-state), **`§9` (density budget)** et
`§10` (no-JS) sont **confirmés, non superseded**.

---

## 7. Ce qui reste provisoire

* Les **valeurs** de l'échelle typographique.
* Les **valeurs** des 16 rôles de couleur — seuls les rôles sont fermés.
* Le nombre exact de niveaux d'élévation visuelle par niveau structurel.
* **L'illustration biomécanique professionnelle** — chantier reconnu,
  **parqué**, à brancher sur le programme d'assets existant (17 specs,
  3 plaques régionales produites). Le viseur est validé **avec un placeholder
  assumé**.
