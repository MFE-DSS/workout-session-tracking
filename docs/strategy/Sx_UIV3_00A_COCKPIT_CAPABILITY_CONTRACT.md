# `Sx_UIV3_00A` — Cockpit Capability Contract

**Statut : `APPROVED — OPERATOR`** (2026-08-18, avec les amendements A/B/C de `Sx_UIV3_04 §1bis`)
**Dépend de** `Sx_UIV3_00` (Foundation Contract), qu'il **étend** sans le contredire.
**Précède** `Sx_UIV3_01` et `Sx_UIV3_02` dans la queue.
**Portée : UI/UX uniquement.** Aucun calcul, aucune donnée nouvelle, aucun modèle.

---

## 0. Pourquoi cette couche existe

`Sx_UIV3_00` gouverne la **vérité** et la **géométrie** : ce qu'on a le droit
d'affirmer, où les choses se posent, combien de pixels elles coûtent. Il est
muet sur la **grammaire instrumentale** — la profondeur, l'illumination d'état,
le retour au toucher, la sémantique du mouvement.

Un écran peut satisfaire entièrement `00` et rester un document bien composé
plutôt qu'un instrument. Ce contrat ferme cet écart.

**Il ne propose aucune fonctionnalité nouvelle.** Il rend visibles quatre
choses que le produit possède déjà, mieux que le marché ne les rend :

```
CAUSE  →  PRESCRIPTION  →  EXÉCUTION  →  TRANSITION
```

---

## 1. Contrast ladder

### 1.1 Le défaut mesuré

L'échelle de surfaces actuelle est **perceptuellement plate**. Ratios entre
niveaux adjacents, calculés sur les tokens réels de `home.css` :

| Marche | Ratio actuel |
|---|---:|
| void → base | **1,051:1** |
| base → surface | **1,067:1** |
| surface → raised | **1,070:1** |
| raised → line | 1,231:1 |
| line → line-strong | 1,311:1 |

Trois marches sous **1,07:1**. La profondeur est **déclarée par des tokens
distincts et non délivrée à l'œil** — en salle, sous éclairage médiocre, sur
un écran à luminosité réduite, `--t-surface` et `--t-raised` sont la même
couleur.

L'échelle de premier plan, elle, est correcte : 3,11 / 6,06 / 8,49 / 15,69.
**Le problème est le fond, pas le texte.**

### 1.2 Les quatre niveaux — **amendé par `04 §1bis A` / C1**

> **Correction.** La première rédaction déclarait **cinq** niveaux dont
> `L3 = system` et `L4 = active/action`. C'était faux : « système » et « actif »
> sont des **états sémantiques**, pas des profondeurs. `L4` est **supprimé** et
> la profondeur devient **strictement indépendante du sens** (`04 §2`).

| Niveau | Rôle **structurel** | Token | Valeur |
|---|---|---|---|
| **L0 — void** | derrière l'instrument, hors-champ | `--t-void` | `#070A0D` |
| **L1 — base** | fond de page, la référence | `--t-base` | `#0F1318` *(inchangé)* |
| **L2 — posé** | surface portant une lecture | `--t-surface` | `#191F27` |
| **L3 — élevé** | surface élevée · overlay en couche supérieure | `--t-raised` | `#232B36` |

Escalier mesuré :

| Marche | Ratio |
|---|---:|
| L0 → L1 | 1,065:1 |
| L1 → L2 | **1,124:1** |
| L2 → L3 | **1,161:1** |

Les filets (`--t-line`, `--t-line-strong`) sont des **séparateurs structurels**,
pas des niveaux de profondeur.

**Règle bloquante.** Deux surfaces adjacentes dans la hiérarchie doivent
différer d'au moins **1,12:1**. En dessous, la distinction n'est pas rendue et
le niveau doit être supprimé plutôt que déclaré.

### 1.3 Deux tokens actuellement en faute

| Token | Valeur | Sur `--t-raised` proposé | Verdict |
|---|---|---:|---|
| `--t-fg-faint` | `#5A6472` | **2,38:1** | **échec** — et il est **utilisé comme couleur de texte** (`home.css:329`, `.today-home__summary-hint`) |
| `--t-amber-dim` | `#8A7538` | **3,18:1** | non-texte / grand texte uniquement |

Correction proposée : `--t-fg-faint` → `#6E7A8A` → **3,27:1** sur L3. Cela
reste **insuffisant pour du corps de texte** : le token est alors explicitement
réservé aux séparateurs, puces et éléments non textuels, et tout texte migre
vers `--t-fg-muted` (4,64:1 sur L3).

> **Règle.** Un token dont le ratio ne permet pas son usage réel est un défaut,
> pas une nuance. La feuille de style documente le ratio **sur le fond le plus
> profond où le token est effectivement composé**, pas sur `--t-base`.

---

## 2. Depth hierarchy

La profondeur est portée par **la luminance et le contour**, jamais par une
ombre portée décorative (`AUREN_STYLE_RULES` : séparation par luminosité).

| Profondeur | Fond | Contour | Usage |
|---|---|---|---|
| **plat** | L1 | aucun | ambiant, rang 3 de Q5 |
| **posé** | L2 | `--t-line` 1 px | readout, rang 2 |
| **élevé** | L3 | `--t-line-strong` 1 px | actionnable, rang 1 |
| **actif** | L3 | **ambre** 1 px + halo `--t-amber-weak` | objet courant |
| **système** | L2 | **filet bleu** 2 px à gauche | produit par le moteur |

**Interdits** : `box-shadow` décoratif · dégradé de fond · plus de trois
niveaux empilés dans une même colonne (carte dans carte dans carte).

---

## 3. Cockpit primitives

**Huit objets, pas vingt.** Toute surface V3 se compose de ceux-là. Un neuvième
exige un amendement de ce contrat.

| Primitive | Rôle | Où |
|---|---|---|
| `CausalRail` | filet vertical continu reliant cause → `DONC` → prescription | **Home uniquement** — amendement A de `04 §1bis` : une timeline de séries porte des données et des actions **utilisateur**, elle ne peut pas porter la sémantique « origine système » |
| `RecoveryBand` | 3/2/1/0 segments + libellé, `unknown` hachuré | Home, surface corps |
| `ZoneTally` | les 11 zones compressées en une ligne | Home |
| `SystemOrigin` | marque de ce que le moteur produit — filet bleu + texte bleu | Home, Session |
| `SetInstrument` | code de série + champs + référence | Session |
| `CommandDock` | la commande dominante de l'état + son sous-titre | Home, Session |
| `DeltaReadout` | comparaison chiffrée à une référence, `tabular-nums` | Session |
| `RestReadout` | minuteur + prochaine série | Session |

`SubstitutionLauncher` n'est **pas** une primitive : c'est un `CommandDock`
secondaire ouvrant un overlay (§7).

**Chaque primitive déclare** : son niveau L1/L2/L3 · son rang de surface ·
ses états · son nom accessible · sa cible tactile.

---

## 4. State illumination

**Un changement d'état ne peut pas être seulement un nouveau libellé.** Il
modifie au moins **trois** signaux parmi : luminance de fond · contour ·
micro-layout · glyphe · position.

| État | Fond | Contour | Micro-layout | Glyphe |
|---|---|---|---|---|
| `CURRENT SET` | L3 | ambre + halo | champs ouverts 50 px | point plein haloé |
| `REST` | L2 | **anneau pointillé, centre plein** | champs → minuteur | anneau ambre à centre plein |
| `COMPLETE` | L2 | `--t-line` | valeur figée, opacité 0,6 | point plein atténué |
| `FUTURE` | L1 | aucun | `—`, opacité 0,32 | point gris |
| `SYSTEM RECOMMENDATION` | L2 | filet bleu 2 px | — | — |
| `UNKNOWN` | L1 | **pointillé + hachure, jamais rempli** | jamais rempli | ░ hachuré vide |

> **Amendé par `04 §1bis` / C3.** La première rédaction séparait `REST` et
> `UNKNOWN` par **la couleur seule** (ambre vs gris) alors que les deux
> portaient un pointillé — ce que `00 §7` interdit.
>
> Ils sont désormais séparés par la **forme** : `REST` = anneau à **centre
> plein** (un compte à rebours vivant) · `UNKNOWN` = cellule **hachurée,
> jamais remplie** (une absence). Plus la chromie, plus le libellé : **trois**
> signaux.

---

## 5. Press · loading · committed

Tout contrôle personnalisé manifeste **immédiatement** qu'il a reçu l'action.
Un SSR sans JS a une latence réseau visible : sans retour, l'utilisateur
retape.

| Phase | Tier | Rendu | Mécanisme |
|---|---|---|---|
| **press** | **T3** | luminance +8 %, `scale(0.98)`, **sans délai** | `:active` — CSS pur, fonctionne sans JS |
| **focus** | **T2** | contour ambre 2 px, `outline-offset: 3px` | `:focus-visible` |
| **loading** | — | le libellé est **conservé** + barre indéterminée 2 px sous le `CommandDock` + `aria-busy="true"` | **amélioration progressive** ; n'existe pas sans JS |
| **committed** | — | l'état a changé — le nouveau libellé **est** la confirmation | rechargement SSR |

**Aucun toast, aucune notification transitoire.** Dans un cockpit, la
confirmation est le changement d'état lui-même. Un message qui disparaît est
une information perdue.

> **Amendé par `04 §1bis` / C4 et C5.**
>
> **C4** — `:active` était qualifié de « défaut d'accessibilité ». Inexact : le
> retour au toucher est un **contrat d'interaction**, donc **T3**.
> `:focus-visible` est l'invariant d'accessibilité, donc **T2**. Les deux sont
> obligatoires et ne se substituent pas.
>
> **C5** — `loading` était spécifié comme « le libellé devient `…` ». Cela
> **détruit l'information** au moment précis où l'utilisateur doute. Le libellé
> est désormais **conservé** ; la progression s'exprime par une barre. **Jamais
> un `…` seul.**

---

## 6. Motion semantics

**Le mouvement explique une transition d'état. Il ne décore jamais.**

| Transition autorisée | Durée | Courbe |
|---|---:|---|
| série validée → repos | 240 ms | `ease-out` |
| repos → série suivante | 200 ms | `ease-out` |
| exercice terminé → exercice suivant | 300 ms | `ease-in-out` |
| Home → séance | 300 ms | `ease-in-out` |

**Interdits** : lueur d'ambiance · pulsation · parallaxe · apparition
échelonnée · toute animation sans changement d'état sous-jacent.

`prefers-reduced-motion: reduce` **supprime toute transition** et conserve le
changement d'état. C'est une garde **T2**, bloquante.

---

## 7. Popover policy

**Objectif** : substitution, « pourquoi ? », cue avancé, historique miniature
cessent d'allonger la console verticalement.

- `popover` (attribut natif, Baseline 2024) porte l'ouverture, la fermeture par
  `Échap`, le clic extérieur et l'empilement top-layer. **Aucun JS.**
- CSS Anchor Positioning (`anchor()`, `position-anchor`) place le panneau
  contre son déclencheur.

**Ce qui est autorisé en overlay** : uniquement du **L3**. Jamais la cause
d'une décision, jamais la commande dominante, jamais un champ de saisie
critique.

### Repli obligatoire

`@position-try` (le retournement automatique) exige Safari **18.4+** ; entre
18.2 et 18.3 le placement est correct mais sans retournement. Le contrat impose
donc :

- un **placement par défaut qui tient sans retournement** ;
- si l'ancrage n'est pas supporté, le panneau se rend **en flux, sous son
  déclencheur** — `<details>` reste le socle sémantique.

Un overlay dont la version dégradée est inutilisable est **rejeté**.

---

## 8. View Transition policy

**Fait corrigé.** Les View Transitions **inter-documents** sont supportées par
Chromium et Safari 18.2+ ; **Firefox les garde derrière un drapeau** au moment
de la rédaction. Ce n'est donc **pas** une capacité universelle.

| Règle | |
|---|---|
| **Statut** | `ADOPT` — **strictement en amélioration progressive** |
| **Jamais** | une transition ne conditionne la compréhension, la navigation ou la sauvegarde |
| **Test de recevabilité** | l'écran doit être **intégralement jugeable sans aucune transition**. Si le retrait de l'animation rend l'état ambigu, l'état est mal conçu. |
| **Périmètre initial** | uniquement les quatre transitions du §6 |
| **Nommage** | `view-transition-name` réservé aux primitives du §3 qui **persistent** d'un état à l'autre. **Home** : `command-dock`, `causal-rail`. **Session** : `command-dock`, `set-instrument`. Voir `04 §7.2`. |
| **Reduced motion** | `prefers-reduced-motion` désactive toutes les transitions — sans exception |

Aucune capture de régression visuelle n'est prise **pendant** une transition
(`Sx_UIV3_03`) : les baselines capturent des états stables.

---

## 9. Framework admission gate

**Décision opérateur du 2026-08-18, figée.**

| Couche | Décision |
|---|---|
| FastAPI + Jinja SSR | **KEEP** |
| HTML / CSS natif | **PRIMARY UI PLATFORM** |
| `session_focus.js` et les 2 autres | **progressive enhancement uniquement** |
| View Transitions API | **ADOPT** progressif (§8) |
| Popover API | **ADOPT** micro-surfaces (§7) |
| CSS Anchor Positioning | **ADOPT** en enhancement (§7) |
| HTMX | **EVALUATE** — pas `ADOPT` |
| React / Vue / Next / React Native | **REJECT** pour tout UIV3 |
| Capacitor / coquille native | **FUTURE GATE** — V4 « Native Reach », hors UIV3 |

### Porte d'admission — `framework only after measured need`

Une dépendance nouvelle n'entre que si **les quatre** conditions sont réunies,
documentées dans une spec :

1. un **défaut mesuré** au navigateur que la plateforme native ne résout pas ;
2. la démonstration que View Transitions **ne suffit pas** ;
3. le maintien intégral du contrat **no-JS** (`Sx_UIV3_00 §10`) ;
4. un **coût de retrait** connu et écrit.

**Cas d'école pour HTMX.** Si le POST d'une série → nouveau document → état
`REST` produit une rupture perceptible que View Transitions ne rattrape pas,
`hx-boost` devient recevable : il améliore liens et formulaires **en
conservant leur fonctionnement sans JS**. Sans mesure de cette rupture,
l'introduire n'apporte rien.

**La parité Live Activity / Dynamic Island / Watch de Hevy sort du périmètre
CSS/SSR** : elle exige ActivityKit/WidgetKit et des vues SwiftUI. C'est une
porte V4, et Capacitor y serait le premier candidat étudié — pas une réécriture
React Native par réflexe.

---

## 10. Glanceability budget

Une porte **humaine**, que rien n'automatise.

> À **390 px**, en **deux secondes**, sans scroll et sans interaction,
> l'utilisateur identifie : **l'état · l'objet actif · la prescription ·
> l'action**.

| Surface | Les quatre éléments |
|---|---|
| **Home** | état des zones causales · la séance proposée · volume/durée · `DÉMARRER` |
| **Session** | état (`S2` / repos / terminé) · la série courante · charge et répétitions cibles · la commande |

**Protocole.** Un dogfood opérateur sur rendu réel, aux trois largeurs. La
question posée est fermée : *« qu'est-ce que tu fais maintenant, et
pourquoi ? »*. Une hésitation vaut échec de la tranche.

**Aucun test automatique ne mesure ceci.** C'est assumé : c'est le seul domaine
où le jugement humain est la seule garde possible — la même raison qui a fait
écrire `CLAUDE.md §5`.

---

## 11. Ce que ce contrat interdit explicitement

- Déclarer un niveau de profondeur que la mesure ne rend pas (< 1,12:1).
- Utiliser un token de texte sous 4,5:1 **sur le fond où il est réellement
  composé**.
- Signaler un changement d'état par le seul libellé.
- Un contrôle personnalisé sans état `:active`.
- Une animation sans changement d'état sous-jacent.
- Un overlay contenant du L1 ou du L2.
- Une dépendance de rendu à View Transitions, Popover ou Anchor Positioning.
- Une neuvième primitive sans amendement de ce document.

---

## 12. `UI_DATA_GAP` levé par ce contrat

| # | Gap | Statut |
|---|---|---|
| **G6** | **RIR par série.** La maquette d'illustration de la console fait apparaître « RIR 2 ». **`SetLog` ne porte ni `rir` ni `rpe`** — vérifié : les deux n'existent que dans les services de planification hebdomadaire, jamais comme valeur journalisée par série. | **BLOQUÉ.** L'afficher exigerait un champ nouveau, donc un modèle et une migration : hors périmètre absolu. La console V3 affiche charge, répétitions et référence — **pas de RIR**, tant qu'une décision métier séparée ne le crée pas. |

---

## 13. Queue amendée

| # | Spec | Statut |
|---|---|---|
| 00 | `AUREN_UIUX_V3_FOUNDATION_CONTRACT` | rédigé |
| **00A** | **`Sx_UIV3_00A_COCKPIT_CAPABILITY_CONTRACT`** (ce document) | **rédigé** |
| 01 | `Sx_UIV3_01_HOME_CAUSAL_COCKPIT_SPEC` | rédigé — **à amender** pour consommer les primitives §3 |
| 02 | `Sx_UIV3_02_ACTIVE_EXERCISE_CONSOLE_SPEC` | rédigé — **à amender** idem, et retirer toute mention de RIR |
| 03 | `Sx_UIV3_03_VISUAL_REGRESSION_A11Y_SPEC` | rédigé — **à étendre** : escalier de contraste et états `:active` deviennent des assertions mesurées |
| 04 | `Sx_UIV3_04_HOME_SESSION_CONVERGENCE` | à rédiger |

Nouvelle tranche de build, en tête de queue :

| # | Tranche | Objectif visible |
|---|---|---|
| **B0** | `UIV3_COCKPIT_LADDER_01` | l'escalier de surfaces corrigé + les deux tokens en faute réparés, contrastes documentés sur le fond réel |

`B0` précède `B1` : les tokens bleus se posent sur des surfaces dont la
profondeur est enfin délivrée.
