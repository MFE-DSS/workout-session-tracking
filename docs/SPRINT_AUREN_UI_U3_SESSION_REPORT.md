# `AUREN_UI_U3_SESSION` — la séance retrouve sa profondeur

> **Tranche 3 de la voie critique UI.** Empilée sur `U2` (PR #184), elle-même
> sur `U1` (PR #183). Surface **souveraine**.
>
> **Aucun changement de composition.** Ni template, ni libellé, ni ordre, ni
> commande. Seule la **profondeur** change — les quatre points du `BLOC 1`
> (`S-08`…`S-11`) restent à trancher et décideront de la composition.

---

## 1. Brainstorming / Options / Risques / Choix retenu (`CLAUDE.md §3`)

| Option | Description | Verdict |
|---|---|---|
| **A** — poser les classes `.lvl-*` dans les gabarits | la primitive appliquée telle quelle | ⛔ les règles de `session_focus.css` chargent APRÈS `app.css` et gagnent : il aurait fallu neutraliser une à une les déclarations concurrentes, sur 107 Ko |
| **B** — remapper les tokens de la séance sur les rôles | une seule autorité, zéro gabarit touché | **retenu** |
| **C** — attendre les arbitrages du `BLOC 1` | pas de travail jeté si la composition change | la profondeur ne dépend pas de la composition ; attendre aurait laissé le défaut en production sans raison |

**Retenu : `B`.** Chirurgical (15 déclarations de fond/ombre concernées), sans
gabarit, et il ferme la cause plutôt que de la contourner.

---

## 2. Trois défauts mesurés, tous invisibles au dépôt

### 2.1 La correction de profondeur n'avait jamais atteint la séance

`UIV3_COCKPIT_LADDER_01` a corrigé l'échelle dans `app.css` — L2 de `#151A21`
à `#191F27`, L3 à `#232B36`, **marches 1,124 et 1,161**. `session_focus.css`
déclarait **ses propres valeurs**, restées aux anciennes :

    marches de la séance   1,067  ·  1,070
    plancher exigé         1,120

**La surface la plus utilisée du produit tournait sous le plancher de
perception que le dépôt s'est lui-même fixé.**

`test_session_css_still_declares_no_palette_token` ne l'a pas vu — et il avait
raison de ne pas le voir : il vérifie que `--t-*` n'est pas redéclaré. La
divergence passait par une **génération `--color-*` entière**, juste à côté.
Une garde qui protège une famille de tokens pendant qu'une famille parallèle
fait le dégât ne garde rien.

### 2.2 L'élévation était inversée

La carte **active** prenait `#151A21` ; les cartes **en attente** `#1B2029`,
**plus clair**. Les exercices qu'on ne fait pas flottaient au-dessus de celui
qu'on fait — l'inverse exact de `Q2=A`, où l'élévation encode la volatilité.

### 2.3 L'exercice actif n'avait aucune surface

Une règle posait explicitement, sur la carte active :

    background: transparent;  box-shadow: none;  border-radius: 0;

Son motif était **juste** — *« deux ambres pleins sur un écran, et l'ambre
cesse de vouloir dire c'est à toi de jouer »* — mais il visait le **cadre
ambre**, pas la surface. **Le rail de 2 px reste ; la surface revient.**

C'est la source concrète de « l'interface plate » : l'objet le plus important
de la séance était littéralement sans fond, sans ombre et sans rayon.

S'y ajoutait `--shadow-sm: none` / `--shadow-md: none`, alors que **trois
règles** écrivent `box-shadow: var(--shadow-sm)`, dont l'en-tête collant et la
barre collante, qui doivent se détacher du contenu défilant dessous.

---

## 3. ⚠ Une garde EXIGEAIT le défaut — supersession à confirmer

`test_session_focus_terminal.TestTerminalCss.test_shadows_neutralized`
assertait `--shadow-sm: none`. Ce n'était pas un oubli : c'était
`SYS-078` (« surface par défaut sans ombre ») épinglé par un test, au nom du
« terminal chrome » de `Sb_UI_02b`.

**Elle garantissait donc que trois `box-shadow` écrits dans le code ne
produisent rien.** C'est la cinquième forme de garde creuse recensée : *une
garde peut exiger le défaut.*

`AUREN_VISUAL_BACKBONE §6` supersède `SYS-078`, sur vos arbitrages `L-07`
(profondeur assumée), `K-01` (échelle à quatre niveaux), `Q1=C` et `Q4=B`.
La garde est donc **migrée**, pas supprimée :

`test_elevation_is_a_hairline_edge_not_a_halo` protège ce qui ne périme pas —
**le registre reste terminal**. Une élévation est une **arête** (un trait de
lumière, un trait d'ombre, flou ≤ 2 px), jamais un halo diffus. C'est la
différence entre un instrument et une carte de tableau de bord web.

> **Point de confirmation opérateur.** C'est une doctrine versionnée qui
> change. Elle a été arbitrée en conversation ; ce rapport la consigne pour
> qu'elle le soit aussi par écrit.

---

## 4. ⚠ `check_scope` a classé cette tranche `ISOLATED`

Modifier la feuille de la surface souveraine a été classé au **niveau de
vérification le plus bas**. Le verdict est pourtant **cohérent avec la
policy** : `global_surfaces` a été peuplée par mesure — *« plus de 40 % de la
suite »* — et `session_focus.css`, scopé à une page, est sous ce seuil.

**Le défaut est dans le critère, pas dans le script.** Pour une feuille de
style, le rayon d'impact est la **surface**, pas le nombre de tests qui la
lisent. Un défaut ici casse l'écran le plus utilisé même si 12 % de la suite
le touche.

Conformément à `CLAUDE.md §1` — *« en cas de doute, remonter d'un cran »* —
cette tranche a été vérifiée **comme `SHARED_CODE`**. `.check-policy.json`
n'est **pas** modifié ici : une évolution de policy passe par un commit dédié,
pas par une tranche UI.

---

## 5. Ce que le navigateur rend

Relevé par `getComputedStyle` sur la page réelle, pas lu dans le CSS :

| Niveau | | Calculé | Texture |
|---|---|---|---|
| puits — la saisie | L0 | `rgb(7, 10, 13)` | relief **creusé** |
| champ | L1 | `rgb(15, 19, 24)` | grain 0.85 |
| logement — en attente | L2 | `rgb(25, 31, 39)` | grain 0.55 |
| plaque — **en vol** | L3 | `rgb(35, 43, 54)` | grain 0.30 |

**L'ordre est rétabli** : plaque > logement > champ > puits.

---

## 6. Relecture des relevés de décisions (`CLAUDE.md §5.2`)

### `DESIGN_DECISIONS_UIV2_SURFACES.md`

| Décision | Verdict |
|---|---|
| `Q1` connexion · `Q2` ancre · `Q3` état du jour | **non concernées** |
| `Q4` la ligne de série devient un instrument | **respectée et servie** — le puits de saisie reçoit enfin un relief creusé, l'instrument se lit comme tel |
| `Q5` trois rangs de surfaces | **respectée** — les rangs portent la responsabilité, l'élévation porte la volatilité. Axes distincts |
| Tokens bleus | **non concernée** — aucune valeur d'accent touchée |
| Convergence Gravl → Auren | **respectée** — trois objets au-dessus de la ligne de flottaison, inchangé |

### `DESIGN_DECISIONS_HOME_UIV2.md`

| Décision | Verdict |
|---|---|
| `D1` interactivité hybride | **respectée** — aucun JS ajouté |
| `D3` sémantique des couleurs | **respectée** — l'ambre reste l'action ; le rail ambre de la carte active est conservé tel quel |
| `D2`, `D4`–`D9` | **non concernées** |

### `Sb_UI_02b` — AUREN TERMINAL

| Point | Verdict |
|---|---|
| tout-mono, zéro webfont | **respecté** |
| ambre unique `#C8A24B` | **respecté** |
| graphite | **respecté** |
| ombres neutralisées | ⚠ **SUPERSÉDÉ** — voir §3 |

**Aucune décision violée. Une décision superséde­e, explicitement.**

---

## 7. Vérifications

| Check | Résultat |
|---|---|
| `check_scope.py` | `ISOLATED` — **traité comme `SHARED_CODE`** (§4) |
| `ruff` (fichier neuf) | à lancer avant commit |
| `check_ruff_budget.py` | respecté |
| `check_spec_protocol.py` | OK |
| Gardes de profondeur | **99 verts** |
| Suite `session_focus` complète | **208 verts** |
| Broad sweep ciblé | **171 verts** |
| Full sweep local | **skippé** — la CI réelle est le filet |

**Gardes plantées avant d'être crues** : ancienne échelle + inversion → 7
échecs · ombres à `none` → 4 échecs. Toutes retirées.

---

## 8. Exposition (`CLAUDE.md §5.1`)

**Écrans entiers**, 390×844, jamais des recadrages. Même serveur, mêmes
données, Playwright substituant la feuille canonique pour la passe « avant » :
aucun écart ne peut venir d'ailleurs que du CSS.

Rendu sur une **copie** de la base locale en scratchpad — jamais la
production. Un compte de laboratoire a été ouvert **sur cette copie
uniquement**, pour atteindre une séance réelle à 7 exercices : un écran vide
n'aurait rien prouvé.

---

## 9. Ce qui reste ouvert

* **`BLOC 1`** — `S-08` à `S-11`, qui décideront de la composition.
* **`S-09`** — la valeur de `action-terminal`.
* **Le critère de `global_surfaces`** dans `.check-policy.json` (§4).
* La dérive de relevé sur `--t-blue-line` (rapport `U1` §4).
