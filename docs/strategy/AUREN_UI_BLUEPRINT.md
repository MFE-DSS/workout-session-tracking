# AUREN — UI Blueprint

**Document vivant.** Mis à jour à chaque tranche livrée.
Dernière révision : **2026-08-18**, à la clôture de `UIV3_COCKPIT_LADDER_01`.

---

## 0. À quoi sert ce document

Les specs `Sx_UIV3_*` sont **normatives** : elles disent ce qui *doit* être vrai.
Ce blueprint dit ce qui **est** vrai, ce qui est **prouvé**, et ce qui **reste
à faire**. C'est le point d'entrée unique : on le lit d'abord, on va dans les
specs pour le détail contraignant.

| Besoin | Document |
|---|---|
| Comprendre le système en un tour | **ce blueprint** |
| Règles transverses non négociables | `Sx_UIV3_00` Foundation Contract |
| Grammaire instrumentale | `Sx_UIV3_00A` Cockpit Capability |
| Contrat de l'Accueil | `Sx_UIV3_01` Home Causal Cockpit |
| Contrat de la console de séance | `Sx_UIV3_02` Active Exercise Console |
| Vérification visuelle et a11y | `Sx_UIV3_03` Visual Regression |
| Unité du langage entre surfaces | `Sx_UIV3_04` Convergence |
| Sort des 656 gardes existantes | `AUREN_UIUX_V3_GUARD_MIGRATION_REGISTER` |
| Contrat de livraison UI, bloquant | `CLAUDE.md §5` |

---

## 1. Le principe qui gouverne tout le reste

> **Ce qui compte est mesuré, pas contemplé.**

Ce n'est pas un slogan : c'est la conséquence de quatre défauts livrés en
production avec **CI verte, Sonar vert et 4 898 tests passants**.

| Défaut livré | Ce qui aurait dû l'attraper |
|---|---|
| Badge d'accueil au mauvais registre, token inexistant | aucune garde ne regarde un pixel |
| 31 débordements de texte sur la console de séance | idem |
| Série courante sous la ligne de flottaison | idem |
| 161 cibles tactiles sous 44 px | idem |

**Le dépôt possède 656 gardes UI et aucune ne rend une page.** Elles lisent du
HTML et du CSS. Les quatre défauts ci-dessus ne sont pas dans le HTML : ils
sont dans le **rapport géométrique** entre des éléments rendus.

D'où trois règles qui traversent tout ce document :

1. **Un contraste se mesure sur le fond réel**, pas sur le fond de base.
2. **Une géométrie se mesure dans un navigateur**, pas dans une feuille de style.
3. **Un rendu s'expose à l'opérateur avant commit** (`CLAUDE.md §5.1`). Le
   jugement humain reste la dernière garde ; il cesse d'être la seule.

---

## 2. État du système

### 2.1 Socle de tokens — `UIV3_COCKPIT_LADDER_01`

**Statut : `PR #130 · GREEN · MERGE PENDING`.** Pas encore sur la canonique.

Autorité unique : `app/static/css/app.css :root`. **19 tokens.**

> **Avant cette tranche, la palette n'existait que sous `.today-home`.**
> `app.css` en comptait 0, `session_focus.css` en comptait 0. La convergence
> Home × Session — même profondeur, même chromie sur les deux surfaces —
> était **littéralement impossible à écrire**. Trouvé en revérifiant un
> critère du Build Gate, pas en lisant une spec.

#### Profondeur — L0 à L3, indépendante du sens

La profondeur dit **où** un objet se situe. Elle ne dit **jamais** ce qu'il
signifie.

| Niveau | Token | Valeur | Marche depuis le précédent |
|---|---|---|---:|
| **L0** | `--t-void` | `#070A0D` | — |
| **L1** | `--t-base` | `#0F1318` | 1,065 |
| **L2** | `--t-surface` | `#191F27` | **1,124** |
| **L3** | `--t-raised` | `#232B36` | **1,161** |

**Plancher : 1,12:1 entre niveaux adjacents.** L'ancien escalier valait
1,051 / 1,067 / 1,070 — une profondeur déclarée par des tokens distincts et
**jamais rendue à l'œil**. En salle, sous éclairage médiocre, `--t-surface` et
`--t-raised` étaient la même couleur.

#### Sémantique — trois familles, orthogonales à la profondeur

| Famille | Sens, identique sur toutes les surfaces |
|---|---|
| **AMBRE** | action utilisateur · objet actif |
| **BLEU** | origine système · ce que le moteur produit |
| **GRIS / MOTIF** | inconnu · neutre · indisponible |

**La récupération n'entre dans aucune des trois** : elle est encodée par
comptage de segments et luminance neutre. Vert / orange / rouge est interdit.

#### Contrastes — mesurés sur **chaque** fond L0–L3

| Token | Valeur | L0 | L1 | L2 | L3 | pire | seuil | rôle |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `--t-fg` | `#E8ECEF` | 16,70 | 15,69 | 13,95 | 12,02 | **12,02** | 4,5 | texte |
| `--t-fg-2` | `#A7B0BA` | 9,04 | 8,49 | 7,55 | 6,50 | **6,50** | 4,5 | texte |
| `--t-fg-muted` | `#8A94A0` | 6,45 | 6,06 | 5,39 | 4,64 | **4,64** | 4,5 | texte |
| `--t-fg-faint` | `#6E7A8A` | 4,55 | 4,27 | 3,80 | 3,27 | **3,27** | 3,0 | **non-texte** |
| `--t-amber` | `#C8A24B` | 8,25 | 7,74 | 6,89 | 5,93 | **5,93** | 4,0 | porteur |
| `--t-amber-hover` | `#D7B45C` | 9,99 | 9,38 | 8,35 | 7,19 | **7,19** | 4,5 | texte |
| `--t-amber-dim` | `#8A7538` | 4,42 | 4,16 | 3,70 | 3,18 | **3,18** | 3,0 | **non-texte** |
| `--t-blue-fg` | `#7DD3FC` | 11,90 | 11,18 | 9,94 | 8,57 | **8,57** | 4,5 | texte |
| `--t-blue-mid` | `#5FA8D3` | 7,59 | 7,13 | 6,34 | 5,46 | **5,46** | 4,0 | porteur |
| `--t-blue-line` | `#5A93C9` | 6,10 | 5,73 | 5,09 | 4,39 | **4,39** | 4,0 | porteur |
| `--t-unknown` | `#828E9E` | 5,96 | 5,60 | 4,98 | 4,29 | **4,29** | 4,0 | porteur |

`--t-amber-weak` `rgba(200,162,75,.12)` · `--t-on-amber` `#0A0C0F` (8,14 sur
l'ambre) · `--t-line` `#333D4B` et `--t-line-strong` `#475365`, **structurels**
donc exempts du seuil porteur, mais pinnés à ≥ 1,2:1 — un filet invisible ne
sépare plus rien.

**Seuils.** Texte 4,5 · filet **porteur de sens** 4,0 (cible AUREN, plancher
WCAG 3,0) · non-texte 3,0. **Sur le pire fond réel, jamais sur `--t-base`
seul.**

> `--t-blue-line` valait `#4A7FB5`, « validé » au cycle précédent sur
> `--t-base` uniquement. Mesuré correctement : **3,94 sur L2**, **3,40 sur L3**
> — sous la cible. C'est l'erreur que `CLAUDE.md §5.4` interdit, commise un
> étage plus haut.

**Deux tokens sont non-textuels** : `--t-fg-faint` et `--t-amber-dim`. Aucun
texte ne les porte, sur aucune surface. Une garde le pinne.

### 2.2 Primitives cockpit

**Huit. Une neuvième exige un amendement de `Sx_UIV3_00A §3`.**

| Primitive | Surfaces | Statut |
|---|---|---|
| `CausalRail` | **Home uniquement** | spécifiée |
| `RecoveryBand` | Home, surface corps | spécifiée |
| `ZoneTally` | Home | spécifiée |
| `SystemOrigin` | Home, Session | spécifiée |
| `SetInstrument` | Session | spécifiée |
| `CommandDock` | Home, Session | spécifiée |
| `DeltaReadout` | Session | spécifiée |
| `RestReadout` | Session | spécifiée |

**Aucune n'est construite.** Les tokens qu'elles consommeront existent ; les
câbler serait commencer le redesign, ce que le périmètre de `B0` interdisait —
une garde vérifie que `--t-blue-*` et `--t-unknown` n'ont **aucun**
consommateur.

`CausalRail` est **Home-only** : une timeline de séries porte des données et
des actions **utilisateur**, elle ne peut pas porter la sémantique « origine
système ». La chronologie de la Session est portée par les `SetInstrument`
eux-mêmes et par un **filet structurel neutre** — de la profondeur, pas une
primitive.

### 2.3 Surfaces

| Surface | Cible | Statut | Défaut vivant |
|---|---|---|---|
| **Accueil** | Causal Cockpit | spécifiée, non construite | hero de 422 px dont **115 vides** · cause visible **0 px** au-dessus du pli · 3 échelles d'état concurrentes |
| **Séance** | Future Console | spécifiée, non construite | **31 débordements durs** à 390 px · série courante à y=843 · **161 cibles sous 44 px** · 4,3 écrans par exercice |
| **Connexion** | porte d'identité sobre | décidée, non spécifiée | « ← Retour » sans retour · 3 liens de poids égal |

### 2.4 Plateforme — figée

`FastAPI + Jinja SSR` **KEEP** · HTML/CSS natif **PRIMARY** ·
View Transitions / Popover / Anchor Positioning **ADOPT en amélioration
progressive uniquement** · HTMX **EVALUATE** · React / Vue / Next / React
Native **REJECT** · Capacitor **FUTURE GATE V4**.

Porte d'admission à quatre conditions : `Sx_UIV3_00A §9`.
**`framework only after measured need`.**

---

## 3. Ce que les gardes ont appris

Trois erreurs de la dernière tranche, toutes attrapées par des gardes, toutes
structurellement instructives.

**Une garde peut être exacte sur les valeurs et fausse sur les fichiers.**
Le Build Gate affirmait que `test_graphite_surfaces_present` tiendrait, parce
que `#0F1318` ne changeait pas. Il est tombé : la garde lisait `home.css`, et
la tranche y avait retiré la déclaration. Vérifier une valeur ne dit rien de
l'endroit où un test la cherche.

**Une garde peut passer pour une mauvaise raison.**
`test_amber_accent_present` cherchait `#c8a24b` dans `home.css` et le trouvait
**dans le commentaire d'en-tête**. Elle serait restée verte alors que l'ambre
avait quitté le fichier. → Toute garde qui grep un CSS le fait désormais
**sans les commentaires**.

**« Décoratif » se prouve, ne se décrète pas.**
J'avais rangé `.today-home__meta-sep` — un « · » — parmi les glyphes
décoratifs. Ma propre garde a refusé : c'est un élément réel portant une
`color`. La preuve du caractère décoratif est `aria-hidden`, pas le mécanisme
CSS qui dessine le caractère.

**Conséquence de méthode** : les deux gardes T4 concernées ont été **ouvertes
en deux plutôt qu'affaiblies** — elles vérifient désormais la **déclaration** à
l'autorité **et** la **consommation** par la surface.

---

## 4. Taxonomie des gardes

**656 gardes UI, 39 modules.** Une refonte ne peut pas les traiter en bloc.

| Tier | Nature | Règle |
|---|---|---|
| **T1** | business / data | **jamais** affaiblie |
| **T2** | accessibilité | jamais supprimée sans preuve ≥ |
| **T3** | contrat d'interaction | modifiable **par spec explicite** uniquement |
| **T4** | contrat visuel | évolutif, décision versionnée + baseline |
| **T5** | implémentation héritée | supprimable **le jour où** la spec la remplace |

Tout test modifié pendant un build V3 **déclare son tier dans le diff**. Un T1
ou T2 modifié sans justification bloque la tranche.

**Une docstring historique ne définit jamais le produit contre le runtime
actuel.** Cas constaté : un commentaire affirme qu'aucune action de série
n'existe alors que `nav=stay` l'implémente.

---

## 5. Queue

### Specs — toutes approuvées opérateur le 2026-08-18

`00` Foundation · `00A` Cockpit Capability · `01` Home · `02` Session ·
`03` Visual Regression · `04` Convergence.

### Build

| # | Tranche | Statut | Dépend de |
|---|---|---|---|
| **B0** | `UIV3_COCKPIT_LADDER_01` | **PR #130 · GREEN · MERGE PENDING** | — |
| ~~B1~~ | ~~`UIV3_TOKENS_01`~~ | **ABSORBÉE PAR B0** — les trois tokens bleus existent et sont mesurés | — |
| B2 | `UIV3_HOME_CAUSE_01` — la cause visible sans tap | à faire | B0 |
| B3 | `UIV3_HOME_TALLY_01` — bilan 11 zones | à faire | B2 |
| B4 | `UIV3_HOME_REJECTED_01` — « écarté, et pourquoi » | à faire | B2 + `G1` |
| B5 | `UIV3_HOME_DEPRIORITISE_01` — Disponibilité part, État du jour se replie | à faire | B2 |
| **B6+B7** | `UIV3_SESSION_EXECUTION_CONSOLE_01` — **une seule vertical slice** | à faire | B0, `02`, `04` |
| B8 | `UIV3_TARGETS_44_01` — 0 cible sous 44 px | à faire | B0 |
| B9 | `UIV3_VISUAL_BASELINE_01` — 13 golden states × 3 viewports | à faire | `03` |
| — | `BODY_LEDGER_PAGE_01` — la matrice 11 cellules, second écran | à faire | B3 |
| — | `LOGIN_IDENTITY_GATE_01` | à faire | `00A` |

**`UIV3_SESSION_EXECUTION_CONSOLE_01` livre ensemble** : commande contextuelle ·
série courante **réellement** au-dessus du pli · états `set`/`rest`/`complete` ·
suppression de l'architecture sticky remplacée. Les quatre ou rien.

**Porte de sortie obligatoire** : la tranche ne passe pas `ACCEPTED` sans une
**séance complète réelle** exécutée et validée humainement aux trois viewports.
Les prototypes sont statiques ; le dogfood ne peut pas précéder la console.

**Fichiers interdits pour toute la queue** : `recommendation.py` ·
`zone_recovery.py` · `recovery_contract.py` · `app/models/**` · `migrations/**`
· tout service métier. Une tranche UI qui en a besoin **bloque** et documente
un `UI_DATA_GAP`.

---

## 6. `UI_DATA_GAP`

| # | Gap | Statut |
|---|---|---|
| `G1` | alternatives + score non passées au template | **pass-through possible** — la valeur existe |
| `G2` | zone limitante d'une alternative | **dérivable** des bandes, tri en présentation |
| `G3` | comptage 11 zones par bande | **dérivable** |
| `G4` | état `REST` | **CLOS** — état de présentation à portée de requête, jamais persisté |
| `G5` | volume d'exercice | somme de présentation |
| `G6` | **RIR par série** | **BLOQUÉ** — `SetLog` ne porte ni `rir` ni `rpe`. L'afficher exigerait un modèle et une migration. **Hors périmètre absolu.** |

---

## 7. Travail parqué

**`D5_SESSION_INSTRUMENT_ROWS_01`** — `origin/sb/uiv2-session-instrument-rows-01`
@ `79c0026`. **PARKED / REMOTE-PRESERVED / PARTIALLY SUPERSEDED BY UIV3.**

Ses **choix de surface** sont superseded : `Valider · E2` est supprimé par
l'amendement B, la barre collante par `02 §7.9`.

Ses **correctifs structurels restent valides** et devront être re-dérivés par
`UIV3_SESSION_EXECUTION_CONSOLE_01` :

- `grid-template-columns: 40px` → `auto` — une piste ne peut plus être plus
  petite que son contenu ;
- `flex-wrap: wrap` sur la ligne d'action — le chevauchement devient impossible
  par construction ;
- `flex: 1` → `flex: 1 0 auto` — `flex: 1` implique `flex-basis: 0`, ce qui
  faisait du bouton principal le **premier** candidat au rétrécissement ;
- annexe pleine largeur pour ce qu'une colonne étroite ne peut pas porter.

Ses **14 tests** pinnent des causes structurelles, pas des libellés : ils
survivent à UIV3 (T4).

---

## 8. Ce qui reste ouvert

- **Merge de `B0`** — décision opérateur, seul blocage de la suite.
- **Amendement `Sx_UIV3_02`** : inscrire noir sur blanc qu'aucun texte de la
  console ne porte `--t-fg-faint`. Découvert en réalignant les prototypes sur
  la palette B0 : ils mettaient la charge de référence à **2,91:1**.
- **Le concept D a été noté sur une palette qui n'existe plus.** Géométrie
  inchangée ; jugement perceptif à refaire au dogfood.
- **`DeltaReadout` absent du prototype D** alors que `02 §7.1` le liste en L2.
  C'est la référence de la dernière séance — à faire apparaître avant le
  dogfood.
- **`check_scope` classe `ISOLATED` un changement de `app.css`.** C'est faux :
  c'est la feuille globale. Correctif du script à prévoir, hors périmètre UI.

---

## Non-goals

- Ce blueprint ne remplace aucune spec : en cas de conflit, la spec
  normative l'emporte, et `Sx_UIV3_04` prévaut sur `00` et `00A`.
- Il ne décide rien. Les arbitrages appartiennent à l'opérateur.
- Il ne décrit pas l'implémentation : il décrit l'état et le cap.
