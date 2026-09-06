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
* **`SSR is the functional baseline`** — le rendu serveur reste la ligne de
  base fonctionnelle. L'enrichissement JavaScript est autorisé pour la
  manipulation directe, l'édition en place, les minuteurs vivants, les
  transitions de focus, l'état local de dépliage et l'interaction optimiste.
* **`A critical training write must remain recoverable if JS fails`** — aucune
  écriture d'entraînement ne dépend du client pour survivre. Déjà vrai, et
  déjà **gardé** (`test_df_b_session_flow.py:69`). Voir `§5bis`.
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

## 5bis. Le mode de rendu — amendement du 2026-09-06

**L'invariant « sans JavaScript » est remplacé par la doctrine suivante, dans
les termes de l'opérateur :**

```
SSR IS THE FUNCTIONAL BASELINE.

JavaScript progressive enhancement is allowed for:
  - direct manipulation      - inline editing
  - live timers              - focus transitions
  - local disclosure state   - optimistic interaction

A critical training write must remain recoverable if JS fails.
```

### ⚠ Ce n'est PAS une levée d'invariant. C'est une mise à jour du constat.

Le socle décrivait un produit sans JavaScript. **Le produit en a déjà**, et
depuis longtemps :

| Fichier | Lignes | Rôle | Nature |
|---|---|---|---|
| `app/static/js/session_focus.js` | 267 | minuteur de repos à échéance · validation de série sur `Entrée` | enrichissement |
| `app/static/js/preview.js` | 138 | carte-aperçu au survol du classement | enrichissement |
| `app/static/js/prefs_focus_rank.js` | 106 | boutons classés synchronisés sur trois `<select>` natifs | enrichissement |

Tous chargés en `defer`, tous en fin de `<body>`, **aucun `<script>` inline,
aucun attribut `on*=`** dans les 63 gabarits.

**Et la seconde moitié de la doctrine est déjà implémentée ET gardée.**
`session_focus.js` valide la série par :

```js
form.requestSubmit(submitter);   // session_focus.js:234
```

— exactement la soumission qu'un appui sur le bouton aurait produite, sur le
même `<form method="post">`. **Aucun `fetch`, aucun `XMLHttpRequest`, aucun
`sendBeacon`**, et cette absence n'est pas une convention : elle est **testée**.
`tests/test_df_b_session_flow.py:69` bannit tout point d'écriture parallèle.

> *A critical training write must remain recoverable if JS fails* décrit donc
> l'architecture actuelle, pas une cible.

### Ce que l'amendement autorise réellement

Ce qui change n'est pas la permission d'écrire du JavaScript — elle était déjà
prise en pratique. Ce qui change, c'est **l'ambition** : l'enrichissement cesse
d'être une exception tolérée pour devenir le moyen assumé de l'édition en
place, de l'état conservé entre les gestes, et des transitions de focus.

Ce que ça n'autorise pas :
* qu'une **écriture d'entraînement** dépende du client ;
* qu'une surface **cesse de rendre** son état initial côté serveur ;
* un **framework** — « zéro framework » est une décision **distincte**, non
  levée par celle-ci.

### Le verrou réel, et il tient en une ligne

`tests/test_home_decision_hero.py:344` :

```python
assert js_files == ["prefs_focus_rank.js", "preview.js", "session_focus.js"]
```

Un **inventaire exact du répertoire** : tout quatrième fichier fait échouer la
suite. Le commentaire du test (l. 346-357) reconnaît lui-même le défaut —
« écrite comme un inventaire exact du répertoire, elle a transformé une
garantie historique de tranche en **interdiction permanente de toute
amélioration progressive future** ».

Il est à requalifier en garde de **capacité** — *aucun script n'écrit en
parallèle du serveur* — forme que `test_df_b_session_flow.py:69` sait déjà
tenir.

### Le coût à provisionner, mesuré

**84 mentions de « sans JS » dans 48 fichiers de tests.** Triées :

| Nature | Nombre | Ce qu'elles font |
|---|---|---|
| **MOYEN** | ~24 | lisent une chaîne dans un fichier source (`"<script" not in src`) |
| **CAPACITÉ** | 9 | exercent le produit — requête, POST, état persisté relu |
| mixte | 5 | |

**Aucune n'affirme littéralement « la séance s'enregistre sans script ».** La
capacité la plus nette du dépôt — `test_ui_profile_preferences.py:157` — porte
sur les **préférences du profil** : POST réel du repli natif, `303`, puis
relecture en base.

Quatre gardes de la coque sont **quasi identiques** sur le même fichier
(`test_app_shell_hardening`, `_navigation`, `_desktop_rail`,
`test_active_navigation_semantics`).

Basculer une surface ne demande donc pas de « casser 48 fichiers » : cela
demande de **trier ses gardes**, de conserver les capacités, et de réécrire les
moyens **en capacités** quand la surface change de mode de rendu.

### Ce que ça casse, et qu'il faut refaire

* **Les gardes qui lisent le HTML servi cessent de mesurer** sur une surface
  dont l'interaction vit côté client. C'est la forme la plus dangereuse de
  « garde qui ne garde rien » — verte, et aveugle ;
* **le harnais de capture** devra piloter des **états**, pas des routes ;
* **`CLAUDE.md §5.1`** — l'exposition au rendu avant commit — devient *plus*
  nécessaire, pas moins : c'est la seule garde qui continue de voir juste.

### Ce qui ne change pas

Tous les autres invariants du `§5` restent entiers : cible tactile 44 px,
`no-color-only-state`, contraste comme contrat de couple, validation implicite,
aucune revendication d'activation musculaire, aucune sémantique de cible dans
`zone_exposure`. **Aucun ne dépendait du mode de rendu.**

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
