# `UIV3_COCKPIT_LADDER_01` (B0) — une autorité unique pour la palette cockpit

**Base** : `8fddc91` · **Branche** : `sb/uiv3-cockpit-ladder-01`
**Spec** : `Sx_UIV3_00A` §1 · `Sx_UIV3_04` §1bis C6/C7/C8
**Portée** : CSS et gardes. **Aucun template, aucun service, aucun redesign.**

---

## 1. Pourquoi cette tranche existe

Deux défauts, tous deux invisibles au dépôt jusqu'à la mesure.

**La palette n'était atteignable que depuis la Home.** Les 15 tokens `--t-*`
étaient déclarés sous `.today-home` dans `home.css`. Compté avant la tranche :

| Fichier | Occurrences de `--t-*` |
|---|---:|
| `home.css` | toute la palette, **scopée `.today-home`** |
| `app.css` | **0** |
| `session_focus.css` | **0** |

La convergence Home × Session exigée par `Sx_UIV3_04 §14` — même profondeur,
même chromie sur les deux surfaces — était **littéralement impossible à
écrire**. Trouvé en revérifiant le critère 4 du Build Gate, pas en lisant une
spec.

**L'escalier de profondeur était plat.** Ratios entre niveaux adjacents :

| Marche | Avant | Après |
|---|---:|---:|
| L0 → L1 | 1,051 | 1,065 |
| L1 → L2 | **1,067** | **1,124** |
| L2 → L3 | **1,070** | **1,161** |

Trois marches sous 1,07:1 — une profondeur déclarée par des tokens distincts
et **jamais rendue à l'œil**. En salle, sous éclairage médiocre,
`--t-surface` et `--t-raised` étaient la même couleur.

---

## 2. Les dix preuves exigées

### 1 · Tokens `:root` identiques depuis les deux documents

Lus par `getComputedStyle(document.documentElement)` sur `/` et
`/sessions/{id}` :

| | Avant | Après |
|---|---:|---:|
| Tokens définis sur `:root` | **0 / 19** | **19 / 19** |
| Divergences Home ↔ Session | — | **0** |

### 2 · Escalier de profondeur

`L1→L2 = 1,124` · `L2→L3 = 1,161` — tous deux **≥ 1,12**. Vérifié au
navigateur et pinné par `test_adjacent_depth_steps_are_perceptible`.

### 3 · Filets porteurs de sens · cible AUREN **≥ 4:1** sur **chaque** fond L0–L3

| Token | L0 | L1 | L2 | L3 | pire | verdict |
|---|---:|---:|---:|---:|---:|---|
| `--t-amber` `#C8A24B` | 8,25 | 7,74 | 6,89 | 5,93 | **5,93** | ✓ |
| `--t-blue-mid` `#5FA8D3` | 7,59 | 7,13 | 6,34 | 5,46 | **5,46** | ✓ |
| `--t-blue-line` `#5A93C9` | 6,10 | 5,73 | 5,09 | 4,39 | **4,39** | ✓ |
| `--t-unknown` `#828E9E` | 5,96 | 5,60 | 4,98 | 4,29 | **4,29** | ✓ |

> L'ancienne valeur `#4A7FB5`, « validée » au cycle précédent, donnait
> **3,94 sur L2** et **3,40 sur L3**. Elle n'avait été mesurée que sur
> `--t-base`. C'est l'erreur que `CLAUDE.md §5.4` interdit, commise un étage
> plus haut.

`--t-line` et `--t-line-strong` sont **structurels** : ils séparent, ils
n'affirment rien. Exempts du seuil (`Sx_UIV3_04 §5`), mais pinnés à ≥ 1,2:1
sur L3 — un filet invisible ne sépare plus rien.

### 4 · Tokens de texte sur leur pire fond réel

| Token | pire cas | seuil | verdict |
|---|---:|---:|---|
| `--t-fg` `#E8ECEF` | 12,02 | 4,5 | ✓ |
| `--t-fg-2` `#A7B0BA` | 6,50 | 4,5 | ✓ |
| `--t-fg-muted` `#8A94A0` | 4,64 | 4,5 | ✓ |
| `--t-amber-hover` `#D7B45C` | 7,19 | 4,5 | ✓ |
| `--t-blue-fg` `#7DD3FC` | 8,57 | 4,5 | ✓ |
| `--t-fg-faint` `#6E7A8A` | 3,27 | 3,0 **non-texte** | ✓ |
| `--t-amber-dim` `#8A7538` | 3,18 | 3,0 **non-texte** | ✓ |

`--t-on-amber` sur `--t-amber` : **8,14:1**.

### 5 · Zéro nouveau consommateur hors périmètre

Les quatre tokens introduits — `--t-blue-fg`, `--t-blue-line`,
`--t-blue-mid`, `--t-unknown` — sont **déclarés et consommés nulle part**.
Les câbler serait commencer le redesign, que le périmètre interdit.
Pinné par `test_no_new_token_consumer_outside_the_approved_scope`.

### 6 · Débordement horizontal — **aucune régression**

| Largeur | Surface | Avant | Après |
|---|---|---:|---:|
| 360 × 800 | Home | 0 | **0** |
| 390 × 844 | Home | 0 | **0** |
| 430 × 932 | Home | 0 | **0** |
| 360 × 800 | Session | 37 | **37** |
| 390 × 844 | Session | 31 | **31** |
| 430 × 932 | Session | 29 | **29** |

**Les compteurs Session sont identiques, pas nuls.** Ce sont les débordements
que `D5_SESSION_INSTRUMENT_ROWS_01` corrigeait ; D5 est **parquée**, donc le
défaut est toujours sur la canonique. **B0 ne le corrige pas et ne prétend pas
le corriger** — il ne l'aggrave pas, ce qui est l'exigence.

### 7 · Tests ciblés — **22 verts** (`tests/test_uiv3_cockpit_ladder.py`)

### 8 · Broad sweep — **764 passés, 0 échec**

`check_scope` a classé **`ISOLATED`**. **Remonté d'un cran délibérément** :
`app.css` est la feuille **globale**, lue par toutes les pages, et 656 gardes
UI lisent du CSS. Classer un changement de `:root` global en « fichiers
feuilles » est faux. `CLAUDE.md §1` impose de remonter en cas de doute.

### 9 · Captures navigateur

Avant / après à 390 px, Home et Session — exposées à l'opérateur avant tout
merge (`CLAUDE.md §5.1`).

**La différence visuelle est subtile, et c'est normal** : B0 est une tranche
de tokens, pas un redesign. Ce qui bouge : les surfaces se détachent
réellement du fond, les filets de carte deviennent visibles, le texte
`__summary-hint` remonte de 3,27 à 4,64:1.

### 10 · Déclarations dupliquées retirées

**15 déclarations** supprimées de `.today-home` dans `home.css` :

| Token | Valeur retirée | Valeur à l'autorité |
|---|---|---|
| `--t-void` | `#0A0C0F` | **`#070A0D`** |
| `--t-base` | `#0F1318` | `#0F1318` *(inchangé)* |
| `--t-surface` | `#151A21` | **`#191F27`** |
| `--t-raised` | `#1B2029` | **`#232B36`** |
| `--t-line` | `#2A303A` | **`#333D4B`** |
| `--t-line-strong` | `#3A4250` | **`#475365`** |
| `--t-fg` | `#E8ECEF` | inchangé |
| `--t-fg-2` | `#A7B0BA` | inchangé |
| `--t-fg-muted` | `#8A94A0` | inchangé |
| `--t-fg-faint` | `#5A6472` | **`#6E7A8A`** |
| `--t-amber` | `#C8A24B` | inchangé |
| `--t-amber-hover` | `#D7B45C` | inchangé |
| `--t-amber-dim` | `#8A7538` | inchangé |
| `--t-amber-weak` | `rgba(200,162,75,.12)` | inchangé |
| `--t-on-amber` | `#0A0C0F` | inchangé |

Plus **4 tokens ajoutés** à l'autorité : `--t-blue-fg`, `--t-blue-line`,
`--t-blue-mid`, `--t-unknown` → **19 au total**.

**Conservés localement, avec raison écrite** : `--t-mono`, `--t-radius`,
`--t-radius-sm`. Ce ne sont pas des tokens de palette, ils ne sont **pas
dupliqués**, et rien ne les lit hors de `home.css`. Ils suivront quand la
Session en aura besoin — pas avant.

---

## 3. Deux erreurs de ma part, corrigées

### Le Build Gate affirmait que `test_graphite_surfaces_present` tiendrait

**Il est tombé.** J'avais vérifié que la *valeur* `#0F1318` ne changeait pas ;
je n'avais pas vérifié que le *fichier lu par la garde* la contiendrait
encore. B0 retire les déclarations de `home.css` — la garde y cherchait un hex
qui n'y est plus.

Le critère 4 du gate était donc **exact sur les valeurs et faux sur les
fichiers**. C'est une erreur d'analyse, pas un imprévu.

### `test_amber_accent_present` passait pour une mauvaise raison

Il cherchait `#c8a24b` dans `home.css` — et le trouvait **dans le commentaire
d'en-tête**, pas dans une déclaration. Il serait resté vert alors que l'ambre
avait quitté le fichier.

**Les deux gardes sont ouvertes en deux plutôt qu'affaiblies** : elles
vérifient désormais la **déclaration** à l'autorité **et** la **consommation**
par la Home, sur du CSS débarrassé de ses commentaires. Tier **T4**, mises à
jour sous décision versionnée (`Sx_UIV3_04 §1bis C8`), conformément au registre
de migration.

### Et une troisième, attrapée par ma propre garde

`.today-home__meta-sep` — un « · » `aria-hidden` — portait `--t-fg-faint`
comme couleur de texte. Je l'avais rangé parmi les glyphes décoratifs. La
garde a refusé la distinction, et elle avait raison : « décoratif » se prouve
par `aria-hidden`, pas par le mécanisme CSS qui dessine le caractère. Migré.

---

## 4. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| `Sx_UIV3_00A §1` — escalier ≥ 1,12:1 | **respectée** — 1,124 et 1,161 mesurés |
| `Sx_UIV3_00A §1.3` — token sous son seuil = défaut | **respectée** — `--t-fg-faint` réparé et son consommateur textuel migré |
| `Sx_UIV3_04 §1bis C6` — `--t-blue-line` → `#5A93C9` | **respectée** |
| `Sx_UIV3_04 §1bis C7` — `--t-unknown` → `#828E9E` | **respectée** |
| `Sx_UIV3_04 §1bis C8` — promotion vers `:root` | **respectée** — 19/19, 0 divergence |
| `Sx_UIV3_04 §2` — profondeur indépendante du sens | **respectée** — L0–L3 purement structurels |
| `Sx_UIV3_04 §3` — ambre action, bleu système, gris inconnu | **non concernée** — aucun consommateur câblé |
| `CLAUDE.md §5.3` — jamais une soustraction seule | **respectée** — chaque déclaration retirée est remplacée à l'autorité dans le même commit |
| `CLAUDE.md §5.4` — couleur = token mesuré sur le fond réel | **respectée** — c'est l'objet de la tranche |
| D1, D2, D6, D9 | **non concernées** — aucune surface modifiée |

**Aucune décision violée.**

---

## 5. Interdits du périmètre — tous tenus

Aucun redesign Home · aucun redesign Session · **aucune primitive cockpit
consommée** · aucun template touché · aucun service métier · aucun rail ·
aucune `RecoveryBand` · aucun `CommandDock` · aucune interaction Session
modifiée · aucun framework · D5 non mergée.

Diff : `app/static/css/app.css`, `app/static/css/home.css`,
`tests/test_uiv3_cockpit_ladder.py` (neuf), `tests/test_home_decision_hero.py`
(2 gardes T4 mises à jour), `docs/strategy/*` (sections non-goals exigées par
`check_spec_protocol`), ce rapport.

---

## 6. Vérifications locales

| Check | Résultat |
|---|---|
| `check_scope` | `ISOLATED` — **remonté à shared** délibérément |
| ruff (fichier neuf) | **propre** |
| `check_ruff_budget` | 281 ≤ 548 |
| `check_spec_protocol` | **OK** *(a exigé une section non-goals sur les 5 specs UIV3)* |
| Tests dédiés | **22 passés** |
| Broad sweep CSS | **764 passés, 0 échec** |
| Rendu navigateur | 19/19 tokens, 0 divergence, 0 régression horizontale |

---

## Verdict

**La palette cockpit a désormais une autorité unique, et la profondeur qu'elle
déclarait est enfin rendue.**

Le plus instructif n'est pas la correction, c'est que **trois des défauts de
cette tranche ont été trouvés par des gardes qui se sont retournées contre
moi** : le Build Gate qui affirmait qu'un test tiendrait, un test qui passait
sur un hex de commentaire, et ma propre garde qui a refusé ma classification
d'un séparateur. Aucun des trois n'aurait été vu en relisant le diff.
