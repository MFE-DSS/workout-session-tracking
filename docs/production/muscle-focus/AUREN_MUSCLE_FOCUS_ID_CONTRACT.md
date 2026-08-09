# AUREN — Muscle Focus ID Contract (`Sb_ASSET_03B.1`)

**Type** : contrat d'identifiants normatif — **DOCS-ONLY**. Fige le **namespace d'IDs** des Muscle Focus
Plates (N2 régional + N3 muscle) **sans produire aucune géométrie**. `ASSET INTEGRATION GATE: BLOCKED` ·
`PLATE GEOMETRY: NOT PRODUCED`.
**Référence normative amont** : [`../../strategy/Sx_ASSET_03B_MUSCLE_FOCUS_TECHNICAL_SURFACE_SYSTEM_SPEC.md`](../../strategy/Sx_ASSET_03B_MUSCLE_FOCUS_TECHNICAL_SURFACE_SYSTEM_SPEC.md) §7-§10.
**Base** : `ff9541a`. **Contrat de plaque** — analogue documentaire du contrat SVG master (`Sx_ASSET_01`).

> **`CONTRACT VERSION: 0.2.0`** — semver. Tout changement **incompatible** (retrait/renommage d'un ID stable,
> changement de grammaire, ajout d'un segment obligatoire) **exige un bump majeur** et un commit modifiant ce
> fichier. Un ajout **purement additif** (nouveau label `part-*`, nouvel index, **acceptation d'un schéma d'ids
> P0 alternatif borné, cf. §3bis**) → bump mineur. Correction de formulation → patch.
> **v0.2.0 (`Sb_ASSET_03B.2R-D1`, évolution gouvernée additive)** : reconnaît le **schéma d'ids déterministe du
> pipeline opérateur** pour les **trois plaques N2 P0** (§3bis) — additif, `geom-*` reste la grammaire cible.

---

## 1. Principe cardinal — isolement vis-à-vis de l'API `zone-*`

Le master global (`auren_bodymap_master.svg`) possède un **espace d'IDs figé et immuable** : `auren-bodymap`,
`body-front-base`, `body-back-base`, les **11** `zone-<code>`, et les enfants `geom-<zone>-<view>-<side>-<index>`.
Cet espace **est l'API métier (Layer A)**. Le système de plaques est une **couche géométrique dérivée
(Layer B)** ; il **ne doit jamais** ré-émettre un ID appartenant à l'API.

**Règle #1 (anti-collision dure)** : une plaque **n'émet JAMAIS** d'ID de la forme `zone-<code>`. Les codes de
zone restent l'exclusivité du master global. Une plaque **référence** une zone (champ `zone_codes` du
descripteur, cf. schéma) mais ne **matérialise pas** un élément `zone-<code>`.

**Règle #2 (isolement de racine)** : chaque plaque est un **document SVG autonome** dont l'élément racine porte
un ID **préfixé plaque** (§3), distinct de `auren-bodymap`. Le master n'est **pas** modifié, **pas** importé,
**pas** étendu.

**Règle #3 (unicité en composition)** : si un document runtime co-rend **plusieurs plaques** ou **une plaque +
le compact global** (ex. récap de séance), l'unicité DOM est garantie par le **préfixe de racine** (§5). Aucun
ID court n'est exposé « nu » dans un document multi-surfaces.

**Règle #4 (crop du master = ré-émission, jamais inline)** : une Regional Plate (N2) est un **crop documenté
du master validé** (spec §15). Elle **ne réutilise JAMAIS les IDs du master** : elle **ré-émet** sa géométrie
sous le namespace plaque (`geom-<key>-…`, préfixé racine). Inliner `zone-pecs` ou `geom-pecs-front-left-01` du
master dans une plaque **dupliquerait** l'ID au niveau du DOM (le master et la plaque étant conçus pour
coexister à l'écran, cf. Overview « récap de séance → Regional ») et casserait `getElementById`, `<use href>`,
`aria-labelledby`, sélecteurs CSS `#id`. **Double isolement** intentionnel : le vocabulaire de côté plaque est
`l|r|c` (≠ master `left|right|center`) et les vues plaque incluent `lateral|section` (≠ master `front|back`
seuls) — même sans préfixe, un `geom-*` de plaque **ne peut pas** matcher byte-à-byte un `geom-*` master.

---

## 2. Grammaire d'IDs (BNF informel)

```
plate-root       ::= "auren-plate-" level "-" key
level            ::= "region" | "muscle"
key              ::= region-key | zone-code
region-key       ::= "chest"|"shoulders"|"back"|"arms"|"core"|"quads"|"posterior"|"calves"
zone-code        ::= <un des 11 codes figés>  (§4)

geom-id          ::= "geom-" key "-" view "-" side "-" index
view             ::= "front" | "back" | "lateral" | "section"
side             ::= "l" | "r" | "c"            (c = central/médian, ex. rectus, sternum)
index            ::= two-digit, "01".."NN", stable par (key,view,side)

part-id          ::= "part-" zone-code "-" label      (sous-head intra-zone, Layer B, JAMAIS un code)
label            ::= [a-z][a-z0-9]*                    (ex. clavicular, sternocostal, long, lateral)

mark-id          ::= "mark-" zone-code "-" ("origin"|"insertion") "-" index
overlay-id       ::= "overlay-" ("insertion"|"fiber"|"contraction"|"exercise")
view-ctrl-id     ::= "view-" view
layer-toggle-id  ::= "layer-toggle"
caption-id       ::= "caption-" key                    (module texte a11y, hors surface)
legend-id        ::= "legend-" key
provenance-id    ::= "provenance-" key
```

**Casse** : `kebab`/`snake` exactement comme les codes de zone (les codes composés gardent leur underscore :
`delt_lat`, `delt_post`, `upper_back`). Jamais de capitales, jamais d'espace, jamais d'accent.

---

## 3. Racines de plaque figées (19)

**8 Regional Plates (N2)** — clefées sur un code/macro existant. La clé régionale mélange **deux
taxonomies** — 5 clés = **macro**, 3 clés = **zone** (héritage : `legs` n'a **pas** de plaque régionale, il
est éclaté en `quads`/`posterior`/`calves`). Cette ambiguïté est **levée par le champ typé
`region_key_kind` du descripteur** (`macro | zone`, cf. schéma), jamais inférée. Colonne **Kind** ci-dessous :

| Plate | Root ID | Kind | `zone_codes` couverts |
|---|---|---|---|
| Chest | `auren-plate-region-chest` | macro | `pecs` |
| Shoulders | `auren-plate-region-shoulders` | macro | `delt_lat`, `delt_post` |
| Back | `auren-plate-region-back` | macro | `lats`, `upper_back` |
| Arms | `auren-plate-region-arms` | macro | `biceps`, `triceps` |
| Core | `auren-plate-region-core` | macro | `core` |
| Quads | `auren-plate-region-quads` | zone | `quads` |
| Posterior | `auren-plate-region-posterior` | zone | `posterior` |
| Calves | `auren-plate-region-calves` | zone | `calves` |

**`legs` n'a AUCUNE plaque régionale** (`auren-plate-region-legs` est **interdit** en v0.1.0).

**11 Muscle Plates (N3)** — 1:1 avec les 11 zones figées :

| Plate | Root ID | Mode |
|---|---|---|
| Pecs | `auren-plate-muscle-pecs` | muscle-heads |
| Deltoïde latéral | `auren-plate-muscle-delt_lat` | muscle-heads |
| Deltoïde postérieur | `auren-plate-muscle-delt_post` | muscle-heads |
| Lats | `auren-plate-muscle-lats` | muscle-heads |
| Haut du dos | `auren-plate-muscle-upper_back` | **grouped-honest** |
| Biceps | `auren-plate-muscle-biceps` | muscle-heads |
| Triceps | `auren-plate-muscle-triceps` | muscle-heads |
| Quadriceps | `auren-plate-muscle-quads` | muscle-heads |
| Chaîne postérieure | `auren-plate-muscle-posterior` | **grouped-honest** |
| Mollets | `auren-plate-muscle-calves` | muscle-heads |
| Core | `auren-plate-muscle-core` | muscle-heads |

Les clefs `quads`, `posterior`, `calves`, `core` existent en **N2 (region)** ET **N3 (muscle)** : la collision
est levée par le segment `level` (`region` vs `muscle`). Aucune autre racine n'est autorisée par v0.1.0.

---

## 3bis. Schéma d'ids P0 du pipeline opérateur (v0.2.0 — variante bornée acceptée)

Les **trois plaques N2 P0** livrées par `Sb_ASSET_03B.2R` (chest / shoulders / posterior) sont produites par
un **pipeline opérateur déterministe** (projection orthographique + rastérisation + potrace) et **gelées**
(intake byte-exact, `Sb_ASSET_03B.2R-D1`). Elles n'utilisent **pas** la grammaire d'authoring `geom-*` (§2)
mais un **schéma descriptif préfixé-racine** :

```
p0-child-id ::= <plate-root> "--" [view "-"] role "-" index
view        ::= "front" | "back"
role        ::= "context" | "hero" | "delt-anterior" | "delt-lateral" | "delt-posterior" | "gluteus" | "hamstring"
index       ::= three-digit "000".."NNN", stable par (view, role)
```
Ex. `auren-plate-region-chest--context-000`, `auren-plate-region-shoulders--front-delt-anterior-000`,
`auren-plate-region-posterior--back-hamstring-000`. Les **classes** portent la sémantique de calque
(`auren-mf-view-front/back`, `auren-mf-context`, `auren-mf-hero`, `auren-mf-part`).

**Bornes dures — ce schéma reste soumis à toutes les règles de sûreté** (vérifiées par le guard) :
1. **Isolement de racine (Règle #2/#3)** : chaque id enfant est préfixé par la racine plaque `auren-plate-region-*`
   via `--`. Disjonction dure avec les ids master **préservée**.
2. **Aucune émission réservée (Règle #1/#6)** : **aucun** `zone-<code>`, `auren-bodymap`, `body-*-base`,
   ni attribut `score/data-score/value/activation/emg`. Aucune couleur métier codée en dur (`fill="#..."`).
3. `geom-*` **reste la grammaire cible** pour toute plaque **authored** future (N3, plaques régionales
   régénérées) ; cette variante est **bornée aux 3 plaques P0 gelées** et n'autorise aucun nouvel id `geom-*`
   non conforme.

Cette reconnaissance est **additive** (bump mineur) : elle **n'affaiblit aucune règle dure** et **n'altère pas**
la grammaire `geom-*` ; elle **acte** que le schéma P0 gelé satisfait les invariants de sûreté sans réécriture
géométrique (interdite au niveau intake).

---

## 4. Registre des `part-*` autorisés (sous-heads Layer B)

Labels d'affichage intra-zone **normés** (jamais un code métier, jamais scoré). Un label absent de cette table
est **interdit** en v0.1.0 (l'ajouter = bump mineur du contrat).

| Zone | `part-*` autorisés |
|---|---|
| `pecs` | `part-pecs-clavicular`, `part-pecs-sternocostal` |
| `delt_lat` | `part-delt_lat-anterior`, `part-delt_lat-lateral` |
| `delt_post` | `part-delt_post-posterior` |
| `biceps` | `part-biceps-long`, `part-biceps-short` |
| `triceps` | `part-triceps-long`, `part-triceps-lateral`, `part-triceps-medial` |
| `quads` | `part-quads-rectus`, `part-quads-vastus_lateralis`, `part-quads-vastus_medialis`, `part-quads-vastus_intermedius` |
| `calves` | `part-calves-gastrocnemius`, `part-calves-soleus` |
| `core` | `part-core-rectus`, `part-core-oblique_external`, `part-core-transverse` |
| `upper_back` | `part-upper_back-trapezius`, `part-upper_back-rhomboid` *(grouped-honest : nommés sans localisation prétendue)* |
| `posterior` | `part-posterior-gluteus`, `part-posterior-hamstring` *(grouped-honest)* |
| `lats` | *(aucun sous-head en v0.1.0 — nappe unique ; largeur = message, cf. spec §16)* |

`delt_lat` et `delt_post` matérialisent le **même deltoïde sous deux angles fonctionnels** : leurs `part-*` ne
prétendent pas à des muscles distincts, seulement à des **faisceaux** vus. Cohérent avec le contrat radar
(`delt_lat`/`delt_post` sont 2 zones métier, mais 1 macro `shoulders`).

---

## 5. Règle d'unicité DOM en composition

**ID logique** (forme courte, utilisée dans les blueprints et l'authoring) : `geom-chest-front-c-01`.
**ID rendu** (forme page-unique, exposée au DOM quand ≥ 2 surfaces coexistent) : `<plate-root>--<id-logique>`,
ex. `auren-plate-region-chest--geom-chest-front-c-01`.

- Un runtime qui rend **une seule** plaque en isolation **peut** exposer la forme courte (SVG = document
  scoped). Dès qu'une **seconde** surface est présente dans le même document (autre plaque, compact global,
  overlay), le **préfixe de racine `--` est obligatoire** sur **tous** les enfants.
- Le séparateur est `--` (double tiret) : il ne peut pas apparaître dans un `key`, un `view`, un `label` ou un
  `index` (tous en simple-tiret / underscore), donc le parsing racine↔enfant est **non ambigu**.

---

## 6. Mots réservés / émissions interdites

Une plaque **ne doit jamais** émettre :

- `zone-<code>` (réservé API Layer A) ;
- `auren-bodymap`, `body-front-base`, `body-back-base` (réservés master) ;
- `zone-unknown` (l'état `unknown` n'a pas de géométrie, héritage du contrat master) ;
- un `part-*` hors table §4 ;
- un attribut `score`, `data-score`, `value`, `activation`, `emg` (une plaque **n'introduit aucune donnée**) ;
- une couleur métier codée en dur (`fill="#..."` de sémantique) — la couleur vient des **tokens runtime**
  (Auren Terminal), l'ID ne la porte pas.

**Règle exercice (anti sous-zone implicite)** : `overlay-exercise` **clef sur `zone_codes` uniquement**,
**jamais** sur un `part-*`. La base exercice (`muscle_mapping.py` / `exercise_knowledge_base.json`) classe à la
**granularité zone** (`zone_primary`/`zone_macro`/`movement_pattern`/`chain`) — **aucun champ faisceau**
n'existe. Une plaque peut **surligner visuellement** un faisceau (`part-*`), mais la **liste d'exercices reste
la zone** (« exercices — Pectoraux »), jamais « — chef claviculaire ». Attribuer un exercice à un faisceau
précis créerait une **donnée sous-zone** (12ᵉ granularité interdite) ou une **fausse précision** que la donnée
ne porte pas.

---

## 7. Prédicats de validation (pour un futur governance guard)

Un test de gouvernance (analogue à `test_auren_bodymap_master.py`) devra, quand des plaques existeront,
vérifier — sur la **forme logique** :

1. `plate-root` ∈ les **19** racines figées (§3) — set exact, ni plus ni moins pour v0.1.0.
2. **Disjonction dure** : `{ids de plaque} ∩ {ids master} = ∅` ; en particulier **aucun** ID ne matche
   `^zone-`.
3. Tout `geom-*` respecte `^geom-(<key>)-(front|back|lateral|section)-(l|r|c)-\d{2}$`.
4. Tout `part-*` ∈ la table §4 (aucun label hors-registre).
5. `index` **stable** par `(key,view,side)` : renuméroter = bump majeur.
6. Aucune émission interdite §6 ; en particulier `^(score|data-score|activation|emg)` absent des attributs.
7. `CONTRACT VERSION` présent et cohérent avec le `contract_version` de chaque descripteur (schéma dédié).

*(Ces prédicats sont **spécifiés ici**, non implémentés : aucun test n'est écrit tant qu'aucune géométrie
n'existe. Ils bornent le futur build géométrique.)*

---

## Verdict

**Verdict :** 🟢 **`MUSCLE FOCUS ID CONTRACT v0.1.0: LOCKED (DOCS-ONLY).`** Namespace de plaque **figé et
disjoint de l'API `zone-*`** : 19 racines (`auren-plate-region-*` ×8, `auren-plate-muscle-*` ×11), grammaire
`geom/part/mark/overlay/view/layer-toggle/caption/legend/provenance`, registre `part-*` normé, règle d'unicité
DOM par préfixe de racine, mots réservés, et 7 prédicats de validation pour le futur guard. **Aucune géométrie,
aucun ID matériel émis.** `PLATE GEOMETRY: NOT PRODUCED` · `ASSET INTEGRATION GATE: BLOCKED`.
