# `AUREN_UI_U2_CHASSIS` — le relief

> **Tranche 2 de la voie critique UI.** Empilée sur `U1` (PR #183). Tier
> `check_scope` : **`SHARED_CODE`**. Arbitrages opérateur du 2026-09-04 :
> **`Q1=C` · `Q2=A` · `Q3=A` · `Q4=B`**.
>
> **Construite et exposée, pas appliquée.** Aucun template n'utilise la
> primitive dans cette tranche — l'application surface par surface est `U3` et
> suivantes, chacune avec sa propre exposition (`§5.1`).

---

## 1. Brainstorming / Options / Risques / Choix retenu (`CLAUDE.md §3`)

L'opérateur avait tranché avant le code : *« la superposition doit être plus
distincte, soit par délimitateur, soit par des contrastes un peu plus sévères »*,
et *« au-delà de la couleur »*. La question ouverte était **comment**.

| Option | Description | Verdict |
|---|---|---|
| **A** — creuser les fonds | plus de contraste entre L0…L3 | ⛔ **impossible, mesuré** — voir §2 |
| **B** — délimiteur seul | arête systématique, fonds inchangés | insuffisant seul : ne dit pas *où* on est |
| **C** — les deux | le fond dit où on est, l'arête dit qu'on change | **retenu** |

**`C` retenu — mais la mesure a vidé sa moitié « fond ».** Ce qui devait être un
appoint est devenu le mécanisme principal.

---

## 2. ⚠ La plage de luminance est épuisée — et c'est mesuré

| Contrainte | Conséquence |
|---|---|
| L1 est la **référence** (`test_the_corrected_values_are_the_approved_ones`) | ne bouge pas |
| `support-error` `#C67D7D` vaut **4,51** sur L3 pour un seuil de **4,5** | **0,01 de marge** — monter L3 rend un message d'erreur illisible |
| L0 poussé au **noir pur** | ne gagne que **1,065 → 1,127** |

Le plafond calculé pour L3 est **exactement sa valeur actuelle**. Une tranche
future qui voudrait « creuser un peu les fonds » casserait un seuil sans le
voir : `test_the_ladder_has_no_headroom_left` échoue désormais à sa place, avec
la cause écrite dans le message.

**Donc le délimiteur n'assiste pas le contraste : il fait le travail que le
contraste ne peut plus faire.**

---

## 3. Le code a corrigé le modèle de profondeur

`--t-void` (L0) n'a **qu'un seul consommateur** dans tout le produit : le fond
du champ de saisie d'une série (`session_focus.css .setline__field`).

**Ce n'est pas un sol de cockpit. C'est un puits.**

Le modèle n'est donc pas une échelle à quatre degrés, mais **trois élévations et
un creux**, le creux étant **orthogonal** — taillé dans le niveau où il se
trouve, jamais un cinquième degré.

| Niveau | Volatilité (`Q2=A`) |
|---|---|
| `.lvl-field` — champ | ne change **jamais** pendant la séance |
| `.lvl-housing` — logement | change **entre** deux séances |
| `.lvl-plate` — plaque | change **pendant** la séance |
| `.lvl-well` — puits | ce dans quoi on **saisit** — creusé |

**Règle mécanique qui décide sans goût** : « cet objet change-t-il pendant une
séance ? » → plaque. « Entre deux ? » → logement. « Jamais ? » → champ. « On y
saisit une valeur ? » → puits.

### La dichotomie demandée : **surélevé ↔ creusé**

Une arête physique se lit à **deux traits** — le côté éclairé et le côté à
l'ombre. **L'ordre des deux décide du sens**, et cette opposition **survit aux
niveaux de gris**. `--relief-raised` pose la lumière à l'intérieur en haut ;
`--relief-carved` y pose l'ombre. Une garde vérifie qu'ils restent opposés :
s'ils devenaient identiques, l'écran resterait « en relief » partout sans
qu'aucun autre test ne bronche.

`state-active` **ne déplace aucun fond** — c'est un état posé sur un niveau
(`BACKBONE §2`), pas un cinquième degré.

---

## 4. Le grain (`Q3=A`), armé après arbitrage sur rendu

Propriété **du niveau**, densité **décroissante avec l'élévation** — ce qui est
proche est net : champ `0.17` · logement `0.10` · plaque `0.05`.

**`--texture-grain` est un multiplicateur RÉEL.** Chaque densité passe par
`calc(var(--texture-grain) * …)`. Le mettre à 0 éteint vraiment les six couches
— vérifié **dans le navigateur**, pas seulement dans le texte du CSS :

    field ::before 0.17 · ::after 0.85 · housing 0.10 · plate 0.05 · éteint 0

Un token déclaré à côté d'opacités écrites en dur serait une **variable
décorative** : on croirait pouvoir éteindre le grain, et `prefers-contrast`
ne l'éteindrait pas. `test_the_grain_token_actually_commands_the_grain` l'interdit.

Trois décisions d'implémentation, chacune gardée :

* **`prefers-contrast: more` éteint le grain** — il réduit le contraste.
  ⚠ `prefers-reduced-motion` ne s'applique **pas** : le grain est statique, et
  l'invoquer serait un alibi d'accessibilité, pas une mesure.
* **Le contenu passe au-dessus** (`z-index: 1`) — sans quoi la contrainte de
  premier rang, « le texte doit rester très simple et lisible », serait perdue
  par un défaut d'empilement plutôt que par un choix.
* **Aucun `overflow: hidden` sur un niveau** — cela rognerait un enfant
  `position: sticky`, dont le CTA collant du mode séance. Le clip passe par
  `border-radius: inherit` sur la surcouche.
* **Le puits ne reçoit pas de grain** : il est petit, il porte une valeur
  saisie, et le texturer coûterait de la lisibilité là où elle vaut le plus
  cher. C'est un choix, pas un oubli.

---

## 5. Deux gardes de `U1` expirent — remplacées, pas supprimées

| Garde retirée | Ce qui la remplace | Pourquoi |
|---|---|---|
| `test_the_role_layer_rewires_no_consumer` | `test_the_chassis_primitive_consumes_roles_and_never_raw_palette` | `U1` prouvait l'inertie ; `U2` consomme légitimement. L'invariant qui ne périme pas : **la primitive parle en emplois, jamais en valeurs** |
| `test_grain_is_declared_but_disarmed` | `test_the_grain_token_actually_commands_the_grain` | `Q3` est tranché. L'invariant qui ne périme pas : **le token doit réellement commander** |

Même procédure que `test_no_new_token_consumer_outside_the_approved_scope` avant
elles (`AUREN_UIUX_V3_GUARD_MIGRATION_REGISTER`) : **la spec les remplace, la
commodité ne les efface pas.**

---

## 6. Deux défauts dans mon propre outillage

Signalés parce qu'ils auraient rendu des gardes creuses :

1. **La fixture fusionnait les `:root` conditionnels avec le `:root` de base.**
   Le `@media (prefers-contrast: more)` met `--texture-grain: 0` ; une lecture
   naïve concluait que le grain était désarmé par défaut — la garde aurait dit
   l'**inverse** de ce que voit un utilisateur ordinaire. Corrigé par un
   appariement d'accolades : une regex ne peut pas apparier des accolades.
2. **`"opacity" in body` comptait le data-URI du bruit**, dont le SVG contient
   littéralement `opacity='.5'`. Resserré sur la déclaration CSS.

Et un troisième dans la planche d'exposition, du même genre que le labo creux de
`U-01` : `.glow` (spécificité 0,1,0) perdait contre `.lvl-plate.is-live` (0,2,0),
donc la variante `C` **rendait la même chose que les autres en prétendant le
contraire**.

---

## 7. Relecture des relevés de décisions (`CLAUDE.md §5.2`)

### `DESIGN_DECISIONS_UIV2_SURFACES.md`

| Décision | Verdict |
|---|---|
| `Q1` connexion · `Q2` ancre · `Q3` état du jour · `Q4` ligne de série | **non concernées** — aucun template touché |
| `Q5` trois rangs de surfaces | **respectée et précisée.** Les trois rangs (actionnable / informatif / ambiant) portent sur la **responsabilité** ; les trois élévations portent sur la **volatilité**. Axes distincts, aucun conflit — un objet ambiant peut vivre sur une plaque s'il change pendant la séance |
| Tokens bleus | **respectée** — inchangés. ⚠ dérive `--t-blue-line` toujours signalée (voir rapport `U1` §4), **non corrigée d'office** |
| Convergence Gravl → Auren | **non concernée** |

### `DESIGN_DECISIONS_HOME_UIV2.md`

| Décision | Verdict |
|---|---|
| `D1` interactivité hybride | **respectée** — la primitive est sans JS |
| `D2` badge d'origine | **non concernée** |
| `D3` sémantique des couleurs | **respectée** — aucune valeur de couleur modifiée par `U2` |
| `D4`–`D9` | **non concernées** |

**Aucune décision violée.**

---

## 8. Vérifications

| Check | Résultat |
|---|---|
| `check_scope.py` | **`SHARED_CODE`** |
| `ruff` (fichiers neufs) | All checks passed |
| `check_ruff_budget.py` | respecté |
| `check_spec_protocol.py` | OK |
| Tests ciblés | **133 verts** |
| Broad sweep ciblé | **188 verts**, dont `test_session_focus_sticky_cta` — la garde qui aurait vu un `overflow: hidden` fautif |
| Full sweep local | **skippé**, conformément au tier |

**Gardes plantées avant d'être crues** : L3 éclairci → 1 échec · puits surélevé
→ 2 échecs (dont la garde qui remplace celle de `U1`) · opacité hors
multiplicateur → 1 échec · `overflow: hidden` → 1 échec. Toutes retirées.

---

## 9. Exposition (`CLAUDE.md §5.1`)

Planche rendue **en composition d'instrument**, pas en bandes empilées — la
leçon du viseur. Tokens et règles `.lvl-*` **extraits du CSS livré** : la planche
montre la primitive réelle, pas une reconstitution, et le générateur échoue si un
token attendu manque.

Grain armé / grain éteint côte à côte : le relief reste dans les deux, parce
qu'il ne dépendait pas de la texture.

---

## 10. Ce que cette tranche laisse ouvert

* **`U3`** — appliquer le châssis à la séance, avec sa propre exposition. Fera
  expirer `test_the_primitive_is_not_applied_yet` (T5).
* **`S-09`** — la valeur de `action-terminal`.
* La dérive de relevé sur `--t-blue-line`.
