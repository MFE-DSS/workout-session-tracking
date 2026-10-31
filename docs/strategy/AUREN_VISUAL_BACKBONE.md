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

> ⚠ **AMENDEMENT 2026-10-23 — client mobile vNext.** Autorité :
> `ADR_AUREN_VNEXT_01` **ACCEPTED — C2** (D1, D2). Pour `clients/mobile/`
> (React Native + Expo) : ~~SSR IS THE FUNCTIONAL BASELINE~~ et ~~« zéro
> framework »~~ ne s'appliquent pas ; l'invariant de remplacement est **« aucune
> écriture d'entraînement ne peut être perdue en silence »**, le legacy web restant
> le repli. Tout ce qui suit reste **entier pour le web**.

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

**Ajout du 2026-10-23 — `ADR_AUREN_VNEXT_01` ACCEPTED — C2** (portée : client mobile seulement) :

| Contrat ancien | Remplacé par | Condition |
|---|---|---|
| §5bis SSR base fonctionnelle · « zéro framework » | invariant « aucune écriture perdue en silence » ; legacy web = repli | ✅ appliqué (mobile) |
| §2 échelle à 4 niveaux · §3.1 **valeurs** · §3.5 textures · §4 patron `P-03` | `LEGACY_VISUAL_REFERENCE` ; direction « instrumentation athlétique » du labo N0 | ✅ appliqué (mobile) |
| `FOUNDATION_CONTRACT §10` no-JS | `§10bis` | ✅ appliqué (mobile) |

**`RETAINED_INVARIANT` sur le mobile** : §1 `PH-01` (allocation, pas suffisance) ·
§3.1 **rôles** (action ≠ système ≠ donnée ; provenance ≠ feedback) · §3.4 mouvement
subordonné à l'état · §4.3 lecture en deux coups d'œil · §5 invariants (cible 44,
aucun état par la couleur seule, contraste de couple, aucune revendication
d'activation musculaire, validation implicite).

---

## 7. Ce qui reste provisoire

* Les **valeurs** de l'échelle typographique.
* Les **valeurs** des 16 rôles de couleur — seuls les rôles sont fermés.
* Le nombre exact de niveaux d'élévation visuelle par niveau structurel.
* **L'illustration biomécanique professionnelle** — chantier reconnu,
  **parqué**, à brancher sur le programme d'assets existant (17 specs,
  3 plaques régionales produites). Le viseur est validé **avec un placeholder
  assumé**. → **ouvert le 2026-10-25 par `DA-01`, §8.**

---

## 8. Direction de marque et système d'assets — `DA-01` (opérateur, 2026-10-25)

Décision opérateur, issue du brainstorm de DA du 2026-10-25 et du cahier des charges des
assets (app + site) remis le même jour. Portée : client mobile et site.

### 8.1 Direction retenue — **A · ALLOCATOR**

Le symbole AUREN ne représente plus un haltère : il représente **une ressource qu'on alloue**
(`PH-01`). Deux rails, un curseur d'allocation, un « A » qui apparaît en négatif sans être
dessiné. Directions écartées : B « Calibration » (risque d'imagerie militaire), C « Trace »
(risque ECG / logo d'IA). Le haltère actuel (`static/brand/`) **n'est plus la marque finale** ;
il peut survivre comme pictogramme générique « force ».

Le mark se juge **en monochrome à 16 px**. S'il n'est reconnaissable qu'avec phosphore, ambre ou
animation, il est raté. Trois constructions à comparer en noir et blanc avant tout effet :
A1 Rail (préférée), A2 Gauge, A3 Gate.

### 8.2 Ce qui est fermé

| Sujet | Décision |
|---|---|
| BodyMap | le master `design/auren/source/bodymap/auren_bodymap_master.svg` est **gardé, jamais redessiné** ; tout dérivé en sort |
| Triptyque d'une séance | **un cadrage par zone du master** (préréglage vue + recadrage), pas six mini-silhouettes face/dos |
| Palette | les tokens actuels de `clients/mobile/src/ui/theme.ts` sont gardés ; aucune couleur neuve sans mesure (`CLAUDE.md §5.4`) |
| Anatomie | BodyParts3D (CC BY 4.0) et Servier Medical Art (CC BY 4.0) comme références documentées ; **jamais d'IA comme source finale** (IA = moodboard) |
| Petites icônes, familles | contrat Tabler : 24 × 24, trait 2, extrémités et jonctions arrondies, `fill="none"`, `stroke="currentColor"` ; la famille se reconnaît **par la forme**, dessinée d'abord en monochrome |
| Textures cockpit | **paramètres de rendu** (lueur, scanlines, grain, hachure), jamais d'image de texture |
| Mouvement riche | Rive (fond d'accueil, récompense) ; micro-transitions et jauges dans le code ; **le cockpit doit convaincre immobile** |
| Exercices | un **mannequin vectoriel commun** articulé + une bibliothèque de matériel ; deux états début / fin au même cadrage |
| Décor | **aucun décor anatomique gratuit** (le fantôme anatomique décoratif est retiré) |
| Icône d'app | géométrie propre en couches (fond · rails · curseur), **aucun effet cuit** ; les apparences système (défaut, sombre, transparente, teintée) sont rendues par l'OS |

### 8.3 Ordre de production — `DA-01` avant toute série

Quatre objets jugent toute la bibliothèque, à quatre échelles (marque → OS → programme → action) :
le mark Allocator · l'icône d'app qui en dérive · le triptyque Push A tiré du master · un écran
d'exercice réel (Smith incliné). **Aucune série (familles, 58 mouvements, planches) avant que les
cinq questions du gate `DA-01` soient à oui** : identifiable à 16 px · AUREN sans écrire AUREN ·
instrument plutôt qu'app de fitness · BodyMap et exercice de la même machine · lisible sans
lueur ni animation.

Partage du travail : le mark, l'icône et l'illustration d'exercice reviennent à l'agent designer
de l'opérateur ; **le triptyque tiré du master et l'écran cockpit se font dans le code** du
client mobile (tranche MISSION).

### 8.4 Roadmap DA — amendée par l'opérateur le 2026-10-25 (supersède l'ordre du §8.3)

Les **primitives d'instrument** passent avant la marque : le mark se dessine une fois que le
langage de l'instrument existe, pas l'inverse.

| Étape | Objet | État |
|---|---|---|
| `DA-01` | Visual DNA (direction Allocator, §8.1–8.2) | ✅ |
| `DA-02.1` | **Calibration Rail** | 🔒 **LOCKED v1** — `AUREN_CALIBRATION_SYSTEM.md` |
| `DA-02.2` | Active Cursor + Reference Marker (+ rail en ligne) | ✅ mergé (PR #286) — **le rail en ligne porte l'ADN** : pleine largeur, barres horizontales, curseur au-dessus / repère dessous (profondeur) |
| `DA-02.3` | Instrument Frame | ✅ mergé (PR #287) — **Frame C (`rail`) = structure verrouillée ; composition intérieure non verrouillée** ; rail en champ ajouté |
| `DA-02.4` | **Instrument Surface** (fusion de « Recessed Window » et « Readout », opérateur 2026-10-25) | ❌ premier rendu **rejeté** (bâti sur le rail en champ, ADN perdu) ; décisions de l'opérateur consignées dans `AUREN_VISUAL_CONTRACT §6` |
| `DA-GOV-01` | **Visual Contract & Regression Gate** | ✅ **mergé** (PR #290, `9c65f7e`) : `AUREN_VISUAL_CONTRACT.md`, baselines DA-02.2, job CI `visual-contract` |
| `DA-02.4B.1` | **Lecture souveraine au-dessus du rail** : rail en ligne DA-02.2 pleine largeur dans Frame C ; valeur choisie au-dessus ; chiffre prescrit sous le repère, sans mot | ✅ **acceptée** (« ACCEPT — LOCK B.1 », 2026-10-25) : `INSTRUMENT-SURFACE-B1` LOCKED, 6 baselines ; Frame C vide gardé (2 baselines) |
| `DA-02.4B.2` | **Divulgation progressive** REST / ADJUSTING : échelle chiffrée et noms de zone masqués au repos | ✅ **acceptée** (2026-10-25) : `INSTRUMENT-SURFACE-B2` LOCKED, 3 baselines au repos ; le « 70 » ne bouge pas ; retour au repos 1,5 s après le dernier geste |
| `DA-02.4B.3` | **Commandes − / +** sous le cadre (R3) | ✅ **acceptée** (2026-10-25) : `INSTRUMENT-CONTROLS-B3` LOCKED, 12 baselines ; allure cockpit différée (R5) |
| `R1, R2, R4, R5` | demandes restantes de l'opérateur (`AUREN_VISUAL_CONTRACT §9`) : surface centrée et plus grande en séance · rail plus haut et plus bas · surbrillance de zone plus contrastée · boutons plus cockpit | R4 ✅ variante V1 (zones inactives 0,35 / 0,30, `AUREN_VISUAL_CONTRACT §14`) ; R2 ✅ option B (rail u = 6, module 390 × 290, §15) ; R5 ✅ allure Rail (§16) ; R1 ✅ carte verticale `SESSION-CARD-R1`, banc (§17) — tranchés par l'opérateur le 2026-10-26 ; montage en séance après E7 |
| `DA-02.5` | **Recessed Window** : la sous-zone interne des instruments (W1 · Inset) | ✅ **acceptée** (2026-10-25) : `RECESSED-WINDOW-V1` LOCKED, 8 baselines ; valeurs au plus grand rôle qui tient |
| `DA-02.6` | **Numeric Readout system** : une seule façon de poser un chiffre (rôles 68 / 40 / 30, unité après à 0,4, décimale même taille) ; taille mesurée dans les fenêtres | ✅ **acceptée** (2026-10-25) : `NUMERIC-READOUT-V1` LOCKED ; 3 baselines de fenêtre réapprouvées, 32 inchangées |
| `DA-03.1` | Manufacturer Mark — exploration (cinq marques à la règle) | ✅ tranchée (2026-10-26) : D primaire, A2 secours |
| `DA-03.2` | **Mark hardening** → `AUREN-MARK-V1` | ✅ **acceptée** (2026-10-27) : `AUREN-MARK-V1` LOCKED (`AUREN_VISUAL_CONTRACT §18`), trois dessins optiques, 9 baselines ; A2 retiré |
| `DA-03.3` | **App icon** → `AUREN-APP-ICON-V1` | ✅ **acceptée** (2026-10-27) : I2 Semantic LOCKED (`AUREN_VISUAL_CONTRACT §19`), document Icon Composer intégré (`ios.icon`), l'haltère retiré comme marque |
| `DA-03.3b` | **App icon en une encre** | ✅ **révisée** (2026-10-28, « le défaut proposé en monochrome ») : I1 remplace I2, même composition, `ink` sur `field` ; la paire `signal` / `system` quitte toute surface de marque (`AUREN_VISUAL_CONTRACT §18–19`) |
| `DA-04.0` | **BodyMap Intake Resolution** : une seule vérité sur le master — est-il autorisé dans le runtime mobile ? | ✅ statué (2026-10-28) : **OUTCOME B — NOT AUTHORIZED FOR APP INTEGRATION** ; technique passe ; manquent revue anatomique, revue juridique, surface d'attribution |
| `DA-04.0b` | **Autorisation interne du master** : décision du propriétaire, voie (b) | ✅ (2026-10-28) : `ACCEPT_INTERNAL_P0_WITH_CONSTRAINTS` — **AUTHORIZED FOR AUREN INTERNAL BUILDS WITH CONSTRAINTS**, diffusion publique non autorisée ; contrat de mapping et planches Muscle Focus réconciliés avec la réalité ; rôle verrouillé : **BodyMap V1 = localisation fonctionnelle** |
| `DA-04.1` | **Triptyque Push A** : trois caméras sur le même master (`push-pecs`, `push-delt-lat`, `push-triceps`), viewBox déterministes, dans Frame C / Recessed Window ; une seule zone dominante, le contexte très diminué ; l'ambre = zone au premier plan, **jamais** une carte d'activation ; zone active ≈ 35–50 % du contenu anatomique visible ; T1 trois fenêtres égales / T2 une dominante + deux secondaires, l'opérateur tranche ; surface d'attribution dans l'app | ✅ **acceptée** (2026-10-29, « ACCEPT T1 », « oui go ») : `PUSH-A-BODYMAP-TRIPTYCH-V1` LOCKED (`AUREN_VISUAL_CONTRACT §20`), T1, zone mise en avant en **`system`** (jamais `signal`), 5 baselines ; cible 35–50 % = préférence, l'orientation prime ; section Licences dans l'app ; aucun montage produit |
| `DA-04.2` | **Toutes les zones, toutes les séances** : une caméra par zone (11), agnostique de tout programme ; le panneau d'une séance se déduit de ses exercices | ✅ **acceptée** (2026-10-29, « Ok, très bien ») : `BODYMAP-ZONES-V1` LOCKED (`AUREN_VISUAL_CONTRACT §21`), 13 baselines ; fenêtres égales, trois par ligne au plus |
| `DA-04.3` | **Le BodyMap dessine le corps MIT** : `react-native-body-highlighter` 3.2.0 (MIT) vendorisé, chemins intouchés, mêmes caméras et zones ; le master reste source de conception | ✅ **acceptée** (2026-10-31, « pour tous les trucs isolés de muscles, c'est bon […] statique », « ouais go on va se satisfaire de cela pour l'instant ») : `BODYMAP-MIT-BODY-V1` LOCKED (`AUREN_VISUAL_CONTRACT §22`), les 18 baselines refaites ; crédit MIT dans l'app ; la dette `ANATOMY-V2` de dessin ne pèse plus sur le runtime |
| `DA-05.0` | **Mannequin canonique** : face, dos, profil, ¾ face, ¾ dos ; puis articulation et matériel | 🟡 **référence reçue** (2026-10-29) : pack de 5 vues approuvé par l'opérateur (face, profil, ¾ face, ¾ dos, dos), généré par IA → **référence visuelle canonique**, jamais source finale ; **reconstruction vectorielle requise** (`AUREN_CANONICAL_MANNEQUIN_V1_SPEC.md`), masses identifiées par les 11 codes de zone ; intégration bloquée. **2026-10-31 : sort du chemin critique** — la reconstruction de l'agent a été rejetée (asymétries) ; l'opérateur produit lui-même les représentations (Midjourney) dans un second temps |
| `DA-04.4` | **Zoom biomécanique** (le muscle pendant la répétition) | ⏸ **DIFFÉRÉ** (opérateur, 2026-10-31 : « mets tout ça de côté […] à faire plus tard dans l'amélioration continue ») — prototype non livré, recherche et sources consignées : `AUREN_VISUAL_CONTRACT §23` ; backlog `MOTION-V2` ci-dessous |
| `DA-05.1` | **Preuve Smith incliné** — redéfinie le 2026-10-31 : l'écran d'exercice réel composé des pièces **verrouillées** (marque, Frame C, fenêtres, lectures chiffrées, BodyMap sur le corps MIT), sans mannequin ni mouvement | ✅ **acceptée** (2026-10-31, « go ») : `EXECUTION-SCREEN-V1` LOCKED (`AUREN_VISUAL_CONTRACT §24`) — zone de l'exercice en série, zone de l'exercice suivant au repos, moins de texte, icônes dessinées, cadrans réduits ; 6 baselines d'écran entier ; répond « BodyMap et exercice de la même machine » |
| Gate `DA-01` final | les cinq questions, dont « BodyMap et exercice de la même machine » | ✅ **passé** (opérateur, 2026-10-31 : « oui à tout ») — identifiable à 16 px · AUREN sans écrire AUREN · instrument plutôt qu'app de fitness · BodyMap et exercice de la même machine · lisible sans lueur ni animation. **Réserve consignée (question 3)** : l'instrument de charge n'entre dans le geste de saisie qu'avec E7 (moteur V2) ; la carte R1 reste la cible. **La DA initiale est close.** |
| `MISSION` + BodyMap de séance | la séance proposée porte le panneau de ses zones, dérivé par le serveur | ✅ **acceptée** (2026-10-31, « go ») : `MISSION-SCREEN-V1` LOCKED (`AUREN_VISUAL_CONTRACT §25`) ; montage des pièces verrouillées dans les écrans réels : MISSION et exécution faits, fin de séance ensuite |
| Fin de séance + BodyMap | les zones travaillées, en BodyMap, séries faites par zone | ✅ **acceptée** (2026-10-31, « OK ») : `COMPLETE-SCREEN-V1` LOCKED (`AUREN_VISUAL_CONTRACT §26`) — **les trois écrans d'une séance (proposer, exécuter, conclure) parlent le même langage** |
| — | familles → les 7 Push A → équipements → autres plates → les 58 mouvements | ensuite seulement, dans cet ordre |
| `MOTION-V2` (backlog) | **Représentation biomécanique pertinente** : les faisceaux du muscle (ex. les trois faisceaux du grand pectoral), comment ils sont disposés, comment ils se raccourcissent et s'allongent pendant le geste ; vue 3D ou ¾ | **hors chemin critique** (opérateur, 2026-10-31) ; amélioration continue ; l'opérateur produira des représentations (Midjourney) ; la mécanique a une source ouverte vérifiée (modèle thoraco-scapulaire, CC BY 4.0) — tout est dans `AUREN_VISUAL_CONTRACT §23` |
| `ANATOMY-V2` (backlog) | **Géométrie anatomique plus nette** : même taxonomie, mêmes 11 IDs, contours nettement plus propres et lisibles — pas forcément plus « médical » ; sert les planches riches (détail d'exercice, fiche éducative, biomécanique) | **hors chemin critique** ; dette documentée, alimentée par les zones que les recadrages `DA-04.1` révèlent trop grossières ; **jamais** une régénération IA du master (perte de traçabilité) |

**Convergence demandée par l'opérateur le 2026-10-31** : « avance sur ton critical path des autres assets
UX UI […] il faut plutôt qu'on converge vers la fin de la préparation de l'application ». Le mouvement et le
mannequin passent en amélioration continue ; l'ordre devient `DA-05.1` (écran d'exercice réel) → gate `DA-01`
final → **montage des pièces verrouillées dans les écrans réels de l'app** (MISSION, exécution, fin de séance ;
l'instrument de charge attend toujours E7).

**Roadmap corrigée par l'opérateur le 2026-10-28** : `DA-04.0` ferme d'abord la vérité sur le master BodyMap ;
**MISSION ne passe pas avant** — une fois la marque finie, le gain différenciant vient de l'anatomie et du
mouvement, pas d'un écran existant remis au nouveau style.

Le gate `DA-01` du §8.3 (cinq questions) reste le critère de **chaque** étape ;
`AUREN_CALIBRATION_SYSTEM §12` y ajoute ses huit conditions pour `DA-02.x`.

**Conséquence sur le code déjà écrit** : la jauge de zone de l'écran MISSION
(`Sb_VNEXT_MOBILE_MISSION_01`) est une lecture de **couverture**, pas une calibration. Elle ne
porte ni référence ni curseur. Elle sera reprise dans le langage de `DA-02.3` à `DA-02.5`
(Instrument Frame, Readout) dès qu'il existera, et ne doit jamais imiter le Calibration Rail.
