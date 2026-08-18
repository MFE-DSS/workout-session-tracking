# `Sx_UIV3_04` — Home × Session Convergence

**Statut : `APPROVED — OPERATOR`** · 2026-08-18
**Dépend de** `Sx_UIV3_00`, `00A`, `01`, `02`, `03` — **approuvées** avec les
amendements opérateur consignés.
**Amendements opérateur du 2026-08-18** : `A — CausalRail est Home-only` ·
`B — microcopy Session finale` (§1bis).
**Portée : UI/UX uniquement.** Aucun build, aucun fichier `app/` modifié.

**Objet.** Ce document ne crée aucune direction artistique. Il démontre que la
Home Causal Cockpit et l'Active Exercise Future Console parlent **une seule
langue**, et il **tranche les conflits** entre les specs amont. Aucun conflit
ne subsiste après ce document, ou le build ne s'ouvre pas.

---

## 1. Conflits amont — résolus ici

Sept conflits réels ont été trouvés en confrontant `00`, `00A`, `01` et `02`.
Six sont des erreurs de mes specs amont ; le septième est une mesure fausse.

### C1 — La profondeur était mélangée à la sémantique · **AMENDE `00A §1.2`**

`00A` définissait cinq niveaux dont `L3 = system` et `L4 = active/action`.
C'est faux : « système » et « actif » sont des **états sémantiques**, pas des
profondeurs. Un objet système peut être posé ou élevé ; un objet actif aussi.

**Résolution.** La profondeur est **L0–L3 uniquement** et **strictement
indépendante** de l'état sémantique (§2). `L4` est supprimé.

### C2 — Le rail causal virait ambre à la prescription · **AMENDE `01 §3`**

`01` faisait passer le rail en ambre dès « LA SÉANCE ». Or la séance proposée
est **produite par le moteur** : c'est de l'origine système, donc du bleu. Sous
la règle « ambre = action utilisateur », faire virer le rail à la prescription
attribue à l'utilisateur ce que le système a décidé.

**Résolution.** Le rail est **bleu de la cause jusqu'à la prescription
incluse**, et **ambre uniquement au niveau du `CommandDock`**. La bascule
chromatique marque exactement le passage *système → utilisateur*. C'est plus
juste et plus lisible que l'ancien découpage.

### C3 — `REST` et `UNKNOWN` ne se distinguaient que par la couleur · **AMENDE `00A §4`**

`00A` donnait un pointillé aux deux, séparés par ambre vs gris. C'est une
distinction **par la couleur seule** entre deux objets pointillés, ce que
`00 §7` interdit.

**Résolution.** Deux **formes** différentes :
`REST` = anneau pointillé avec **centre plein** (compte à rebours vivant) ·
`UNKNOWN` = cellule **hachurée, jamais remplie**. Plus le libellé, toujours.

### C4 — `:active` classé accessibilité · **AMENDE `00A §5`**

`00A` qualifiait l'absence de `:active` de « défaut d'accessibilité ». C'est
inexact : le retour au toucher est un **contrat d'interaction**.

**Résolution.** `:active` = **T3**. `:focus-visible` = **T2**. Les deux sont
obligatoires ; ils ne sont pas du même tier et ne se substituent pas.

### C5 — `loading` spécifié comme « le libellé devient `…` » · **AMENDE `00A §5`**

Remplacer le libellé par des points de suspension **détruit l'information**
au moment précis où l'utilisateur doute. Et sans JS, ça n'arrive jamais.

**Résolution.** `loading` est une **amélioration progressive** (§8). Sans JS :
aucun état de chargement, le `:active` et le rechargement suffisent. Avec JS :
le libellé est **conservé**, une barre de progression indéterminée de 2 px
apparaît sous le `CommandDock`, `aria-busy="true"` est posé. **Jamais un
`…` seul.**

### C6 — `--t-blue-line` sous la cible · **AMENDE `00 §4` et `00A §1`**

Mesuré sur les surfaces où il se pose réellement, et non sur `--t-base` seul :

| Rail | L0 | L1 | L2 | L3 | pire cas |
|---|---:|---:|---:|---:|---:|
| `--t-blue-line` `#4A7FB5` | 4,72 | 4,43 | **3,94** | **3,40** | **3,40 — sous cible** |
| **`--t-blue-line` v2 `#5A93C9`** | 6,10 | 5,73 | 5,09 | 4,39 | **4,39 ✓** |
| `--t-amber` `#C8A24B` | 8,25 | 7,74 | 6,89 | 5,93 | 5,93 ✓ |

Le token bleu validé au cycle précédent l'avait été **sur `#0F1318`
uniquement**. C'est exactement l'erreur que `CLAUDE.md §5.4` interdit, refaite
un étage plus haut. **`--t-blue-line` passe à `#5A93C9`.**

### C7 — L'inconnu n'avait pas de token conforme · **NOUVEAU**

| Candidat | pire cas L0–L3 |
|---|---:|
| `#6E7A8A` | 3,27 — plancher seul |
| **`--t-unknown` `#828E9E`** | **4,29 ✓** |

**Résolution.** L'inconnu reçoit `--t-unknown: #828E9E`, et son libellé
« non mesurée » est rendu en `--t-fg-muted` (4,64:1 sur L3).

---

## 1bis. Amendements opérateur — 2026-08-18

### A — `CausalRail` est **Home-only**

**Décision opérateur.** Une timeline de séries contient des **données et des
actions utilisateur**. Elle ne peut donc pas porter la sémantique « origine
système ». Employer `CausalRail` — primitive **bleue**, définie comme la marque
de ce que le moteur produit — pour figurer le passé/courant/futur d'une série
serait une **contradiction sémantique directe** avec `§3`.

**Ce que je proposais était faux.** Le §4 de la première rédaction affirmait
« c'est la même primitive, employée sur deux axes ». C'est précisément
l'erreur : un signal ne peut pas garder son sens en changeant d'axe si l'axe
change la nature de ce qu'il relie. Sur la Home il relie **des causes système
à une prescription système**. Sur la Session il relierait **des saisies de
l'utilisateur**. Même filet, sens opposé.

**Résolution.**

| | |
|---|---|
| `CausalRail` | **Home uniquement**. Retiré de la Session, de sa matrice, de ses transitions et de son nommage `view-transition-name`. |
| Chaîne Session | `SystemOrigin` / `DeltaReadout` → `SetInstrument` → `CommandDock` → `RestReadout` |
| Séquence passé / courant / futur | portée par les **`SetInstrument` eux-mêmes** — leur profondeur, leur opacité et leur marqueur d'état suffisent |
| Filet vertical de la Session | **`--t-line-strong` structurel, sans sémantique** — c'est de la profondeur (`§2`), pas un porteur de sens, donc **exempt** du seuil 4:1 (`§5`) |

**Ce n'est pas une neuvième primitive.** Un filet structurel relève de la
profondeur, pas du vocabulaire sémantique : le compte de huit primitives de
`00A §3` est inchangé.

#### Conséquence sur le choix du concept D — assumée

Le classement de `02 §5` donnait à D un **10/10** en « continuité avec la Home
V3 », largement **au titre du rail partagé**. Cet argument tombe. Recalculé
honnêtement, la continuité de D redevient comparable à celle des autres
concepts (elle repose sur `CommandDock` et `SystemOrigin`, que tous partagent) :
**D passe de 49 à 46**, contre 44 pour C.

**D reste retenu, mais pour une autre raison que celle écrite.** Sa supériorité
résiduelle est **entièrement mesurée** : commande à **y = 272** contre 773 pour
C, objet vif à 91–135 contre 83–116, et une bande passé/courant/futur qui
survit intacte comme **dispositif structurel**. La marge est de 2 points, pas
de 5 : c'est à retenir si le dogfood de `B6+B7` déçoit.

### B — Microcopy Session · contrat final

**`Valider · E2` est définitivement supprimé.** Il faisait porter à une
commande de *série* la destination d'un *exercice* — la même confusion de
portée que le `title` fautif attrapé par
`test_cta_copy_does_not_claim_a_set_level_action`.

| État | Commande — **libellé figé** |
|---|---|
| `CURRENT SET` | **`VALIDER Sx`** |
| `REST` | **`PASSER LE REPOS`** |
| `EXERCISE COMPLETE` | **`CONTINUER → Ex`** |
| `LAST EXERCISE COMPLETE` | **`TERMINER LA SÉANCE`** |

Aucune autre formulation n'est autorisée sur un `CommandDock` de Session.
Le sous-titre `→ repos 90 s` reste permis : il énonce la **conséquence**, pas
une seconde action.

### C — `REST` est un état de présentation

> **`REST` = request-scoped presentation state only ; never persisted business
> state.**

Il est **dérivé**, à l'échelle d'une requête, du fait qu'une série vient d'être
enregistrée. Il n'est **jamais** écrit en base, jamais porté par un modèle,
jamais un champ. Le persister créerait une donnée métier nouvelle — hors
périmètre absolu (`00 §13`), et cela ferait de la durée de repos une
affirmation du produit alors qu'elle est une suggestion.

Conséquence directe : un rechargement pendant le repos **ne perd rien**, parce
qu'il n'y avait rien à perdre. Le repli sans JS (`§7.4`) est le comportement
canonique, pas une dégradation.

Ceci clôt `UI_DATA_GAP G4`.

---

## 2. DEPTH — L0 à L3, indépendante du sens

**Règle fondatrice.** La profondeur dit **où** un objet se situe dans
l'empilement. Elle ne dit **jamais** ce qu'il signifie. Deux objets de sens
opposés peuvent partager une profondeur ; un même sens peut apparaître à
plusieurs profondeurs.

| Niveau | Token | Valeur | Rôle structurel |
|---|---|---|---|
| **L0** | `--t-void` | `#070A0D` | derrière l'instrument · hors-champ |
| **L1** | `--t-base` | `#0F1318` | fond de page · la référence |
| **L2** | `--t-surface` | `#191F27` | surface portant une lecture |
| **L3** | `--t-raised` | `#232B36` | surface élevée · overlay en couche supérieure |

Marches mesurées : 1,065 · **1,124** · **1,161**. Plancher **≥ 1,12:1** entre
deux niveaux adjacents (`00A §1.2`).

**Un overlay n'introduit pas de L4.** Il est **L3 en couche supérieure**
(`top-layer`). Trois profondeurs empilées maximum dans une même colonne.

---

## 3. SEMANTIC STATE — trois familles, orthogonales à la profondeur

| Famille | Signal | Sens — **identique sur les deux surfaces** |
|---|---|---|
| **AMBRE** `#C8A24B` | remplissage plein, contour, halo | **action utilisateur · objet actif** |
| **BLEU** `#5A93C9` / `#7DD3FC` | filet 2 px, texte | **origine système · ce que le moteur produit** |
| **GRIS / MOTIF** `#828E9E`, hachure, pointillé | contour, texture | **inconnu · neutre · indisponible** |

**Le même signal visuel a toujours le même sens.** Un filet bleu sur la Home
et un filet bleu sur la Session disent la même chose : *ceci vient du système*.
Un remplissage ambre dit toujours : *ceci est à toi, ou c'est en cours*.

**Interdits de convergence :**

- l'ambre ne marque **jamais** une zone ciblée, un état de récupération, ni une
  prescription — seulement une action ou l'objet courant ;
- le bleu ne marque **jamais** une action ;
- la récupération n'entre dans **aucune** de ces trois familles chromatiques :
  elle est encodée par **comptage de segments et luminance neutre** (`00 §5`).

---

## 4. `CAUSE → PRESCRIPTION → EXÉCUTION → TRANSITION`

La même phrase, jouée par des primitives différentes selon la surface.

| Moment | Home | Session |
|---|---|---|
| **CAUSE** | `RecoveryBand` des zones visées, sur `CausalRail` bleu | `DeltaReadout` — la référence de la dernière séance |
| **PRESCRIPTION** | `SystemOrigin` — nom de la séance, volume, phrase du moteur | `SystemOrigin` — schéma cible `3×8-12` |
| **EXÉCUTION** | — *(l'exécution est la page suivante)* | `SetInstrument` — les champs de la série courante |
| **TRANSITION** | `CommandDock` — `DÉMARRER` | `CommandDock` → `RestReadout` → `CommandDock` |

### Mapping demandé, explicite

```
HOME     SystemOrigin → RecoveryBand → CausalRail → CommandDock
SESSION  SystemOrigin / DeltaReadout → SetInstrument → CommandDock → RestReadout
```

**Lecture.** `CausalRail` n'apparaît **que** dans la chaîne Home. Il y relie
des **causes produites par le système** à une **prescription produite par le
système** : sa sémantique bleue est cohérente de bout en bout.

La Session n'a **pas** de rail sémantique. Sa séquence passé → courant → futur
est portée par les **`SetInstrument` eux-mêmes** — profondeur L3 / L2 / L1,
opacité décroissante, marqueur d'état — et, au besoin, par un **filet
structurel neutre** (`--t-line-strong`) qui n'affirme rien.

**Ce que la convergence est réellement.** Elle ne consiste pas à réemployer la
même primitive partout. Elle consiste à ce que **`SystemOrigin` et
`CommandDock` se comportent à l'identique sur les deux surfaces** — même
chromie, même profondeur, même interaction, même microcopy — et à ce qu'aucun
signal ne change de sens en changeant de page. Une primitive propre à une
surface est un enrichissement ; une primitive dont le sens s'inverse est un
défaut.

---

## 5. Contraste des rails porteurs de sens

**Cible AUREN ≥ 4,00:1 · plancher WCAG ≥ 3,00:1**, mesurés **sur chaque
niveau de profondeur où le rail se pose**, pas sur `--t-base` seul.

| Rail | Rôle | pire cas L0–L3 | Verdict |
|---|---|---:|---|
| `--t-amber` `#C8A24B` | action / actif | **5,93** | cible ✓ |
| `--t-blue-line` **`#5A93C9`** | origine système | **4,39** | cible ✓ |
| `--t-unknown` **`#828E9E`** | inconnu | **4,29** | cible ✓ |
| `--t-line-strong` `#3A4250` | **structurel** | 1,41 | **exempt** — ne porte aucun sens |

**Règle.** Un rail **structurel** (séparation, gouttière) est de la profondeur :
il est exempt du seuil. Un rail **porteur de sens** — causalité, origine, état
— doit clearer **4:1 sur son pire fond**. Sous 3:1, il est refusé sans
discussion.

**Un token qui n'a été mesuré que sur `--t-base` est réputé non mesuré.**

---

## 6. Distinction exacte des cinq états

Chaque état porte **au moins trois signaux**, dont **jamais la couleur seule**.

| État | Profondeur | Forme | Chromie | Texte | Motif |
|---|---|---|---|---|---|
| **`current`** | L3 | contour plein + **halo** | ambre | libellé de la commande | — |
| **`rest`** | L2 | **anneau pointillé, centre plein** | ambre | `repos 0:47` | — |
| **`complete`** | L2 | contour plein, **opacité 0,6** | neutre | valeur figée + `✓` | — |
| **`system`** | L2 | **filet gauche 2 px** | bleu | phrase du moteur | — |
| **`unknown`** | L1 | **contour pointillé, jamais rempli** | `--t-unknown` | « non mesurée » | **hachure 45°** |

**`rest` et `unknown` partagent le pointillé** — ils sont séparés par la
**forme** (centre plein vs hachure vide), par la **chromie** et par le
**texte**. Trois signaux, jamais la couleur seule (résolution de **C3**).

**`complete` et `system` partagent L2** — ils sont séparés par le filet gauche
et l'opacité. La profondeur ne les distingue pas, et c'est normal : la
profondeur ne porte pas le sens (§2).

---

## 7. Transitions

### 7.1 Home → Session

| | |
|---|---|
| Déclencheur | `CommandDock` `DÉMARRER` — `POST /sessions` |
| Élément persistant | `CommandDock` (`view-transition-name: command-dock`) |
| Durée | 300 ms `ease-in-out` |
| Sens | le bouton qui a lancé la séance **devient** la commande de la séance |
| Sans transition | changement de document standard, **aucune ambiguïté** |

### 7.2 Session · `Sx → Rest → Sx+1 → exercice suivant`

| Transition | Persistant | Durée | Ce que le mouvement explique |
|---|---|---:|---|
| `Sx` → `Rest` | `CommandDock` | 240 ms | la commande **change de nature**, elle ne disparaît pas |
| `Rest` → `Sx+1` | `CommandDock`, `SetInstrument` | 200 ms | l'objet courant **descend** d'un cran dans la bande |
| exercice → suivant | `CommandDock` | 300 ms | changement de contexte, pas de série |

`view-transition-name` est réservé aux primitives **qui persistent** d'un état
à l'autre :

| Surface | Noms autorisés |
|---|---|
| **Home** | `command-dock`, `causal-rail` |
| **Session** | `command-dock`, `set-instrument` |

`causal-rail` **n'existe pas en Session** (amendement A). Le filet structurel
de la Session n'est pas nommé : il n'est pas une primitive et ne transitionne
pas.

### 7.3 `prefers-reduced-motion: reduce`

**Toutes** les transitions sont supprimées. Aucune exception, y compris la
barre de chargement du §8. Le changement d'état reste intégralement lisible —
c'est le test de recevabilité de `00A §8` : *si retirer l'animation rend l'état
ambigu, l'état est mal conçu*. Garde **T2**, bloquante.

### 7.4 Sans JS

| Opération | Comportement |
|---|---|
| Démarrer une séance | `<form method="post">` → nouveau document |
| Enregistrer une série | `<form method="post">` → nouveau document, état `rest` rendu serveur |
| Passer le repos | lien ou `<form>` → série suivante |
| Corriger une série | `nav=stay` |
| Terminer | `action=end` |
| Repos | **statique** : `repos suggéré : 90 s`, la commande reste active |
| Overlays | `<details>` en flux |
| Transitions | aucune |

**Aucune fonction n'est perdue sans JS.** Seuls le décompte, le retour de
chargement et les animations disparaissent.

---

## 8. `:active` · `:focus-visible` · `loading`

| | Tier | Obligation | Mécanisme |
|---|---|---|---|
| **`:active`** | **T3** | tout contrôle personnalisé | luminance +8 %, `scale(0.98)`, **CSS pur, sans délai** |
| **`:focus-visible`** | **T2** | tout élément focalisable | contour ambre 2 px, `outline-offset: 3px` |
| **`loading`** | — | **amélioration progressive** | libellé **conservé** + barre indéterminée 2 px sous le `CommandDock` + `aria-busy="true"` |

**`loading` n'est jamais un `…` qui remplace le libellé** (résolution de **C5**).
Sans JS, l'état n'existe pas : `:active` et le rechargement suffisent.

Ces trois comportements sont **identiques sur les deux surfaces**. Un
`CommandDock` se comporte de la même façon qu'il démarre une séance ou qu'il
valide une série.

---

## 9. Overlays — baseline sémantique, upgrade conditionnel

**Ordre imposé, non négociable :**

1. **Baseline** — `<details>/<summary>` **en flux**, sous son déclencheur.
   C'est ce qui est spécifié, testé et capturé en golden state.
2. **Upgrade** — `popover` (Baseline 2024) si supporté : couche supérieure,
   `Échap`, clic extérieur.
3. **Upgrade** — CSS Anchor Positioning si supporté : ancrage au déclencheur.

**Contraintes :**

- un overlay ne contient que du **L3** — jamais une cause, jamais la commande
  dominante, jamais un champ critique ;
- placement par défaut **qui tient sans retournement** : `@position-try` exige
  Safari 18.4+, entre 18.2 et 18.3 le placement est correct mais ne se
  retourne pas ;
- **c'est la version dégradée qui est pinnée** en golden state
  (`03 §9`), parce que c'est elle qui doit rester utilisable.

Overlays autorisés : Home « écarté — et pourquoi » · Session `Adapter`,
cues techniques, historique miniature.

---

## 10. Microcopy — règles communes

| Règle | Home | Session |
|---|---|---|
| **Verbe à l'infinitif** sur toute commande | `Démarrer` | `Valider`, `Passer le repos`, `Continuer` |
| **La destination porte l'information** quand elle change de contexte | `Démarrer` | `Continuer → E2` |
| **La portée du libellé = la portée de l'action** | — | `Valider S2` agit sur une **série** · `Continuer → E2` sur un **exercice** — jamais mélangés |
| **Sous-titre = conséquence**, jamais reformulation | — | `→ repos 90 s` |
| **Jamais de revendication d'IA** | invariant **T1** | invariant **T1** |
| **L'absence se dit, ne se déduit pas** | « non mesurée » | « première fois » |
| **Aucune notification transitoire** | le changement d'état **est** la confirmation | idem |
| **Pas de point final** sur les libellés de contrôle | | |
| **Capitales** réservées aux `CommandDock` et micro-labels | | |

**Vocabulaire unique de la récupération** — quatre libellés, aucun synonyme :
`disponible` · `récupération partielle` · `encore chargée` · `non mesurée`.
Formes courtes autorisées à 360 px : `prête` · `partielle` · `chargée` · `n.m.`

---

## 11. Spacing & density — règles communes

| Règle | Valeur |
|---|---|
| Grille de base | **4 px** |
| Gouttière de page | 14–20 px selon largeur |
| Interligne entre primitives | **multiple de 4**, minimum 12 px |
| Hauteur `CommandDock` | **≥ 56 px** |
| Hauteur d'un `SetInstrument` actif | **≥ 50 px** par champ |
| Cible tactile fréquente | **≥ 44 × 44 px**, mesurée au navigateur |
| Espace vide réservé et non rempli | **≤ 15 %** de la hauteur d'un bloc |
| Scroll avant l'action dominante | **0 px** |
| Profondeurs empilées dans une colonne | **≤ 3** |

`tabular-nums` obligatoire sur toute donnée comparable : charges, répétitions,
compteurs, scores, minuteur.

---

## 12. Clavier

| Comportement | Règle commune |
|---|---|
| Ordre de tabulation | **suit l'ordre de la tâche**, jamais l'ordre du DOM hérité |
| Premier arrêt utile | l'objet courant — `SetInstrument` en Session, le `CommandDock` en Home |
| `Entrée` dans un champ | soumet le formulaire de l'état courant |
| `Échap` | ferme l'overlay ouvert · **jamais** de perte de saisie |
| Piège de focus | **aucun**, y compris en `popover` |
| `:focus-visible` | contour ambre 2 px, offset 3 px — **T2** |
| Clavier virtuel | l'objet courant reste **au-dessus de 45 % de la hauteur du viewport** — à 390 × 844, sous **380 px** |
| `inputmode` | `decimal` pour la charge, `numeric` pour les répétitions |

---

## 13. Comportement 360 / 390 / 430

| | 360 × 800 | 390 × 844 | 430 × 932 |
|---|---|---|---|
| Rôle | **plancher — fait foi** | référence | confort |
| Libellés de bande | formes **courtes** | complètes | complètes |
| Gouttière | 14 px | 16 px | 20 px |
| `ZoneTally` | bandes à zéro **omises** | complet | complet |
| Zones causales Home | **2 maximum** | 2–3 | 2–3 |
| Espace gagné | — | — | va à l'**espacement**, jamais à un bloc de plus |
| Débordement horizontal | **0** | **0** | **0** |

**Règle.** Aucune largeur ne reçoit un contenu que les autres n'ont pas. La
densité s'adapte ; l'information est la même.

---

## 14. CONVERGENCE MATRIX

| Primitive | Home state | Session state | Depth | Semantic | Interaction | A11y | Fallback |
|---|---|---|---|---|---|---|---|
| **`CausalRail`** | cause → `DONC` → prescription | **(absent — Home-only)** | **L1** (filet sur fond) | **bleu** — origine système | non interactif | **décoratif**, `aria-hidden` ; le sens est en texte (`DONC`, intitulés) | filet CSS ; si non rendu, l'ordre vertical suffit |
| **`RecoveryBand`** | zones visées de la séance | *(absent)* | **L1** | **neutre** — jamais ambre, jamais bleu | non interactif | `role="img"` + `aria-label` = libellé complet | segments = éléments de bloc ; dégradation en texte seul |
| **`ZoneTally`** | bilan des 11 zones | *(absent)* | **L1** | neutre | **tapable** → surface corps N2 | `role="img"` par groupe + total en texte | lien vers la page corps |
| **`SystemOrigin`** | phrase du moteur + nom de séance | schéma cible `3×8-12` | **L2** | **bleu** | non interactif | contraste ≥ 4,5:1 pour le texte | filet gauche ; sans lui, le texte reste lisible |
| **`SetInstrument`** | *(absent)* | `current` / `complete` / `future` | **L3** actif, **L2** complété, **L1** futur | **ambre** si `current`, sinon neutre | champs ; ligne complétée **tapable** → `CORRECTION` | `aria-label` complet par champ ; affordance de correction visible | `<input>` natifs dans un `<form>` |
| **`CommandDock`** | `DÉMARRER` / `REPRENDRE` | `VALIDER Sx` / `PASSER LE REPOS` / `CONTINUER → Ex` / `TERMINER LA SÉANCE` | **L3** | **ambre** | `:active` **T3** · `:focus-visible` **T2** · `loading` PE | ≥ 56 px ; le libellé **annonce** le changement d'état | `<button>` dans un `<form>` — jamais sticky |
| **`DeltaReadout`** | *(absent)* | référence de la dernière séance | **L2** | neutre | non interactif | `tabular-nums` ; `aria-hidden` si dupliqué ailleurs | texte simple |
| **`RestReadout`** | *(absent)* | `rest` — **état de présentation, jamais persisté** | **L2** | **ambre**, anneau pointillé centre plein | commande = `PASSER LE REPOS` | `role="timer"` + `aria-live="off"` | **statique** : `repos suggéré : 90 s` |
| *filet structurel Session* | *(absent)* | séquence passé/courant/futur | **profondeur**, pas une primitive | **aucune sémantique** | non interactif | `aria-hidden` | l'ordre vertical et l'opacité suffisent |

**Lecture de la matrice.** Une primitive absente d'une surface n'y est **pas
remplacée par un équivalent** : elle est absente. C'est ce qui empêche la
convergence de devenir de l'uniformisation.

**`CausalRail` est Home-only** (amendement A) : la Session ne dispose d'aucun
rail sémantique, et le filet qui y figure la chronologie est de la
**profondeur** — dernière ligne du tableau, volontairement hors du compte des
huit primitives.

**Invariant de convergence.** Pour chaque ligne, la colonne *Semantic* est
**identique quelle que soit la surface**. C'est la démonstration demandée : le
même signal ne change jamais de sens en changeant de page.

---

## 15. BUILD READINESS GATE

| # | Critère | Verdict | Détail |
|---|---|---|---|
| 1 | Specs cohérentes | **PASS** | 7 conflits trouvés, 7 résolus au §1. `00A §1.2`, `00A §4`, `00A §5`, `00 §4`, `01 §3` sont amendés par ce document. |
| 2 | Aucun `UI_DATA_GAP` non traité | **PASS** | G1/G2/G3/G5 = pass-through de présentation, conditions de `00 §0` remplies. G4 = état de présentation sans persistance. **G6 (RIR) = bloqué et explicitement hors périmètre** — traité, pas ignoré. |
| 3 | Assets nécessaires autorisés | **PASS** | Aucune primitive n'exige d'asset. Tout est CSS et texte. La BodyMap est explicitement exclue (7 zones sur 11 sans plaque approuvée). |
| 4 | Aucune garde T1/T2 à affaiblir | **PASS pour B0** | Vérifié : `test_graphite_surfaces_present` assert `#0f1318 or #151a21` → `--t-base` reste `#0F1318`, la garde tient. `test_amber_accent_present` assert `#c8a24b` → inchangé. `test_no_teal_in_home_css` → sans objet. `test_contrast_guard` est **renforcée**, pas affaiblie. |
| 5 | Golden states réalisables | **PARTIEL** | 11 des 13 le sont aujourd'hui. **`S7`** (substitution ouverte) et **`S8`** (correction) décrivent des surfaces que `02 §7.4` et `§7.6` **créent** : leurs baselines naissent avec leur tranche, pas avant. Normal, mais à inscrire. |
| 6 | Dogfood Session D préparé | **ÉCHEC** | Les prototypes de `/tmp/auren-ui-lab/session/` sont **statiques** : on ne peut pas y enregistrer une série. Or `BLOCKER-4` exige *une séance complète réellement exécutée*. **Par construction, ce dogfood ne peut pas précéder `B6`.** |
| 7 | Working tree clairement identifié | **ÉCHEC** | L'arbre contient la tranche **`D5_SESSION_INSTRUMENT_ROWS_01` non commitée**, qui modifie `app/static/css/app.css`, `session_focus.css`, `exercise_card.html`, `briefing.py` et 4 modules de tests. **`B0` touche `app.css` et `home.css` — recouvrement direct sur `app.css`.** Construire par-dessus mélangerait deux tranches dans un même diff. |

### Verdict

> ## `UIV3 BUILD GATE CLOSED`

**Deux points échouent. Aucun n'est structurel ; les deux sont des questions
d'ordonnancement.**

### Ce qui ferme la porte, et comment l'ouvrir

**Point 7 — bloquant dur, et le seul vrai.**
`D5_SESSION_INSTRUMENT_ROWS_01` est terminée, mesurée, exposée et verte
(1 415 tests), mais **non commitée**, et elle touche le même fichier que `B0`.
Deux issues, toutes deux opérateur :

- **`GO` sur D5** → commit, PR, merge, puis `B0` part d'un arbre propre ;
- **parquer D5** → `git stash` ou branche dédiée, puis `B0` part de la
  canonique.

Tant que l'une des deux n'est pas tranchée, `B0` produirait un diff mêlant une
correction de débordement et une refonte de tokens. **Je ne le fais pas.**

**Point 6 — re-cadrage à confirmer, pas un blocage.**
Le dogfood d'une séance complète **ne peut pas** précéder la construction de la
console : il n'y a rien à exécuter. Il doit donc devenir une **porte de sortie
de `B6`**, pas une porte d'entrée du programme. `B0` (tokens et escalier de
surfaces) n'en dépend en rien.

**Ce re-cadrage est une décision opérateur, pas une hypothèse que je pose.**
`BLOCKER-4` a été validé comme condition préalable ; je constate qu'il est
irréalisable en l'état et je remonte la question plutôt que de le déclarer
satisfait.

**Point 5 — à inscrire, sans conséquence.**
`S7` et `S8` naissent avec leurs tranches. C'est le fonctionnement normal d'une
baseline ; il suffit que `03` le dise, ce que ce document fait.

### État après résolution

Si l'opérateur tranche le point 7 et confirme le re-cadrage du point 6 :

> `UIV3 BUILD GATE OPEN — B0 READY`

`B0` = `UIV3_COCKPIT_LADDER_01` : escalier de surfaces à ≥ 1,12:1 par marche ·
`--t-blue-line` → `#5A93C9` · `--t-unknown` → `#828E9E` · `--t-fg-faint`
réparé et réservé au non-textuel. **CSS uniquement**, aucun template, aucun
service.
