# `Sb_BODYMAP_IDENTITY_CONTRACT_01` — contrat d'identifiants BodyMap

**Base** : `28ca001` · **Type** : SPEC / CONTRACT ONLY · **Aucun changement runtime**

Ce document tranche la correspondance entre **zone métier**, **cadre**, **surface
SVG** et **région worked-area**, afin que de nouveaux assets puissent être
commandés sans figer la confusion actuelle.

---

## Non-goals

Ce sprint **ne** fait **pas** :

- pas de nouvel asset, pas de géométrie, pas de rendu ;
- pas de renommage des SVG existants ;
- pas de nouvelle zone métier (ni `delt_ant`, ni split `pecs`) ;
- **pas de branchement `zone_recovery`** — le trou est documenté, pas comblé ;
- pas de correction opportuniste de l'UI, même sur les défauts relevés en §3.

---

## 1. Audit — les huit capacités, listes exactes

### 1.1 Les onze zones métier

Source : `app/services/muscle_mapping.py#ZONE_LABELS`.

```
pecs · delt_lat · delt_post · lats · upper_back · biceps
triceps · quads · posterior · calves · core
```

`unknown` **n'en fait pas partie** : c'est un état de qualification, pas une
douzième zone.

### 1.2 Les identifiants de surface réellement présents dans les SVG

Trois plaques, **56 identifiants**, extraits du fichier et non d'un rapport.

| Plaque | Racine | Jetons de surface | Chemins |
|---|---|---|---|
| chest | `auren-plate-region-chest` | `context` (6) · `hero` (2) | 8 |
| shoulders | `auren-plate-region-shoulders` | `front-context` (12) · `front-delt-anterior` (4) · `front-delt-lateral` (2) · `front-delt-posterior` (4) · `back-context` (5) · `back-delt-anterior` (3) · `back-delt-lateral` (2) · `back-delt-posterior` (3) | 35 |
| posterior | `auren-plate-region-posterior` | `back-context` (6) · `back-gluteus` (2) · `back-hamstring` (2) | 10 |

**Vocabulaire de surface observé** : `context`, `hero`, `delt-anterior`,
`delt-lateral`, `delt-posterior`, `gluteus`, `hamstring`.

### 1.3 Les régions worked-area

Source : `worked_area_body_map.html#_WA_ZONE_TO_REGION`, six macros.

```
chest · shoulders · back · arms · legs · core
```

Rendues comme rectangles schématiques, explicitement **« corps schématique (non
anatomique) »** — ce ne sont pas des surfaces anatomiques et elles ne doivent
jamais être confondues avec les plaques.

### 1.4 Les cadres déclarés

Source : `app/services/bodymap_frames.py#REGIONAL_PLATES`.

| Région | Cadres produits |
|---|---|
| chest | `front` |
| shoulders | `front`, `back` |
| posterior | `back` |

Vocabulaire fermé V1 : `front` · `profile` · `back` · `top`.

### 1.5 Surfaces sans zone métier

`delt-anterior` (7 chemins) · `context` (23 chemins sur les trois plaques).

### 1.6 Zones sans surface

Sept : `lats` · `upper_back` · `biceps` · `triceps` · `quads` · `calves` · `core`.

### 1.7 Surfaces plus fines que la zone

Deux cas, tous deux réels :

- **shoulders** — 3 surfaces de deltoïde (`anterior`, `lateral`, `posterior`)
  pour **2** zones (`delt_lat`, `delt_post`).
- **posterior** — 2 surfaces (`gluteus`, `hamstring`) pour **1** zone
  (`posterior`).

### 1.8 Zones plus fines que la surface

**Aucune.** Aucune surface existante ne recouvre plusieurs zones métier. Le cas
inverse n'existe pas aujourd'hui ; le contrat le déclare néanmoins interdit
(§4.4) pour qu'une future plaque ne l'introduise pas silencieusement.

---

## 2. Le cadre est porté par le groupe, pas par l'identifiant

Point vérifié dans les trois fichiers, et il résout une incohérence apparente.

La structure réelle de chaque plaque est :

```
<g class="auren-mf-view-{frame}">      ← LE CADRE, autoritaire
  <g class="auren-mf-context">         ← contexte osseux, jamais une zone
  <g class="auren-mf-hero|auren-mf-part">  ← une surface
```

`chest` nomme ses chemins `…--hero-000` **sans segment de cadre**, alors que
`shoulders` et `posterior` écrivent `…--front-delt-lateral-000`. Ce n'est **pas
un défaut de chest** : le segment de cadre dans l'identifiant est une
**redondance** de l'information déjà portée par le groupe `auren-mf-view-*`, que
chest omet parce qu'il n'a qu'un cadre.

**Conséquence pour le contrat** : le cadre se lit sur le **groupe**, jamais par
analyse du nom. Un consommateur qui découperait l'identifiant pour deviner le
cadre casserait sur chest.

---

## 3. Un quatrième vocabulaire, non recensé jusqu'ici

Le CR *Atlas des Cadres* en annonçait trois. Il y en a **quatre**, et le
quatrième est le plus fragile.

| # | Vocabulaire | Exemple | Utilisé par |
|---|---|---|---|
| 1 | zones métier | `pecs`, `delt_lat` | `muscle_mapping`, planner, `recommendation.py` |
| 2 | `stable_svg_id` du contrat | `zone-pecs` | **aucun asset, aucun runtime** |
| 3 | identifiants de plaque | `auren-plate-region-shoulders--front-delt-lateral-000` | les 3 SVG |
| 4 | **position DOM** | `> g:nth-of-type(3)` | **`app.css` — le rendu réel** |

Le quatrième mérite d'être dit clairement : **le runtime ne colore pas par
identifiant, il colore par rang.**

```css
#auren-plate-region-shoulders .auren-mf-view-front > g:nth-of-type(3) path { … }
#auren-plate-region-shoulders .auren-mf-view-front > g:nth-of-type(4) path { … }
#auren-plate-region-posterior .auren-mf-view-back  > g:nth-of-type(3) path { … }
```

Autrement dit, les identifiants stables — présentés comme « une API du futur pack
d'assets » — **ne sont consommés par personne**, et la couleur dépend de l'**ordre
des groupes** dans le fichier. Réordonner deux groupes, même sans toucher un seul
tracé, changerait silencieusement la couleur de deux faisceaux. Les SHA gelés
protègent contre l'édition, pas contre une **régénération** du pipeline qui
sortirait les groupes dans un autre ordre.

**Ce sprint ne corrige pas ce défaut** (aucun changement runtime autorisé). Il
l'enregistre comme `OQ_POSITIONAL_CSS_01` et le contrat de production §5 impose
l'ordre des groupes pour que le risque reste borné d'ici là.

---

## 4. Le contrat

### 4.1 Règle de gouvernance

> **Le modèle métier gouverne le visuel. Le visuel ne crée pas de zone.**

Une surface plus fine que sa zone est **autorisée** et doit se **regrouper
explicitement**. Une surface ne devient jamais une zone parce qu'elle existe.

### 4.2 Table complète — zone → cadres → surfaces → région worked-area

| Zone métier | Cadres | Surfaces SVG (plaque) | Région WA | Rendu si absent |
|---|---|---|---|---|
| `pecs` | front | `chest / hero` | `chest` | — |
| `delt_lat` | front, back | `shoulders / delt-lateral` | `shoulders` | — |
| `delt_post` | front, back | `shoulders / delt-posterior` | `shoulders` | — |
| `posterior` | back | `posterior / gluteus` **+** `posterior / hamstring` | `legs` | — |
| `lats` | — | *aucune* | `back` | macro |
| `upper_back` | — | *aucune* | `back` | macro |
| `biceps` | — | *aucune* | `arms` | macro |
| `triceps` | — | *aucune* | `arms` | macro |
| `quads` | — | *aucune* | `legs` | macro |
| `calves` | — | *aucune* | `legs` | macro |
| `core` | — | *aucune* | `core` | macro |
| `unknown` *(état, pas zone)* | — | *aucune* | *aucune* | neutre, rien d'actif |

**4 zones sur 11 ont une géométrie. 7 n'en ont pas.**

### 4.3 Surfaces orphelines — décision par surface (A2)

| Surface | Chemins | Décision | Motif |
|---|---|---|---|
| `delt-anterior` (front + back) | 7 | **MERGE** | Option A architecte : dépeinte par la plaque épaules, **jamais adressable comme zone**. Aucun état propre, aucune couleur propre. |
| `context` (3 plaques) | 23 | **IGNORE** | Contexte osseux, volontairement secondaire. **Ne porte jamais d'état** et ne doit jamais être coloré par une bande de récupération. |
| `hero` (chest) | 2 | *non orpheline* | correspond à `pecs`. |
| `gluteus`, `hamstring` | 4 | *non orphelines* | se **regroupent** sous `posterior` (§4.2). |

Aucune surface n'est classée `RESERVED` : le contrat refuse de réserver un nom
pour une géométrie qui n'existe pas.

### 4.4 Règles d'identité

1. **Un identifiant de chemin est unique dans tout le dépôt.** Le préfixe
   `auren-plate-region-{region}--` le garantit.
2. **Le cadre se lit sur le groupe** `auren-mf-view-{frame}`, jamais par
   découpage du nom (§2).
3. **Une surface appartient à au plus une zone.** Le cas « une surface, plusieurs
   zones » est **interdit** : il rendrait une zone incolorable indépendamment.
4. **Une zone peut posséder plusieurs surfaces**, à condition que le regroupement
   soit **déclaré** dans `REGIONAL_PLATES` et non déduit du nom.
5. **`context` n'est jamais une surface d'état.**
6. **Aucun renommage.** Les 56 identifiants actuels sont figés ; les SHA de
   `tests/test_auren_muscle_focus_runtime.py` en sont la preuve.

### 4.5 Zone sans surface — ce qui doit être rendu (A7)

Une zone sans surface se rend au **grain macro** : la silhouette schématique
`wa-region--{region}` peut la signaler, la plaque non.

Trois interdits, dans cet ordre de gravité :

1. **Jamais verte par défaut.** L'absence de géométrie n'est pas une information
   de disponibilité.
2. **Jamais empruntée à une région voisine.** `lats` ne se rend pas avec la
   plaque `posterior` sous prétexte que les deux sont « le dos ou en dessous ».
3. **Jamais inventée.** Pas de forme approximative « en attendant ».

`unknown` est plus strict encore : **aucune anatomie active**, pas de rendu macro
non plus.

---

## 5. Asset production naming contract

*Section destinée au workspace opérateur externe (Blender → Potrace → Inkscape).*

### 5.1 Grammaire des identifiants

```
Racine  : auren-plate-region-{region}
Chemin  : auren-plate-region-{region}--[{frame}-]{surface}-{NNN}
```

- `{region}` — minuscules, un mot : `chest`, `shoulders`, `posterior`, …
- `{frame}` — `front` | `profile` | `back` | `top`. **Obligatoire dès que la
  plaque contient plus d'un cadre** ; omissible sur une plaque mono-cadre
  (précédent `chest`).
- `{surface}` — jeton en minuscules, tirets autorisés : `hero`, `context`,
  `delt-lateral`, `gluteus`, …
- `{NNN}` — compteur **à trois chiffres, commençant à `000`**, ordre stable.

### 5.2 Structure de groupes exigée

```xml
<svg id="auren-plate-region-{region}" viewBox="0 0 {2048*N} 2048">
  <g class="auren-mf-view-{frame}" transform="translate({2048*i},0)">
    <g class="auren-mf-context"> … </g>          <!-- TOUJOURS en premier -->
    <g class="auren-mf-hero|auren-mf-part"> … </g>
    …
  </g>
</svg>
```

**Trois contraintes non négociables** :

1. **Le contexte est toujours le premier groupe** de chaque vue. Le CSS actuel
   compte les rangs (§3) : déplacer le contexte décalerait toutes les couleurs.
2. **L'ordre des groupes de surface est stable** entre les cadres d'une même
   plaque. Pour les épaules : `anterior`, `lateral`, `posterior` — dans cet ordre,
   en `front` **comme** en `back`.
3. **Filmstrip horizontal** : N cadres côte à côte, panneaux de largeur égale
   (2048), `viewBox` de largeur `2048 × N`, chaque vue translatée de
   `2048 × index`. C'est ce que consomme `.muscle-focus__frame--strip`.

### 5.3 Choix `hero` contre `part`

- `auren-mf-hero` — la plaque montre **un** muscle dominant non subdivisé
  (chest), ou plusieurs muscles distincts non subdivisés (posterior).
- `auren-mf-part` — le muscle est **subdivisé en faisceaux** adressables
  séparément (shoulders).

Le choix n'est pas cosmétique : `part` annonce que les surfaces sont plus fines
que la zone et devront être regroupées (§4.4.4).

### 5.4 Ce qui fait rejeter une livraison d'asset

- un identifiant qui **duplique** un identifiant existant ;
- un **renommage** d'identifiant existant ;
- un groupe `context` qui n'est pas premier ;
- un ordre de surfaces différent entre deux cadres d'une même plaque ;
- une surface qui prétendrait couvrir **deux zones métier** ;
- un nom de surface qui introduirait une **zone métier nouvelle**
  (`delt_ant`, `pec_clavicular`, `pec_sternal`, `upper_pec`, `lower_pec`) ;
- une géométrie **inventée** pour une zone non produite.

### 5.5 File de production, par rendement décroissant

1. **Profil corps entier** — plan révélateur de **9 zones sur 11**.
2. **Dessus épaules** — le seul cadre que le profil ne couvre pas.
3. `lats`, `upper_back` — deux zones très sollicitées, aucune géométrie.
4. `quads`, `calves`.
5. `biceps`, `triceps`.
6. `core`.

---

## 6. Le trou documenté, non comblé (A8)

**`zone_recovery` n'atteint aucun template.** Vérifié à nouveau sur `28ca001` :
`grep -rn "zone_recovery" app/templates` retourne zéro résultat.

Les plaques de `/science` sont **décoratives** (`aria-hidden="true"`) et ne
portent aucune donnée. Le couplage « la bande de récupération choisit une
couleur, l'identifiant choisit la surface » reste une **intention de conception**,
pas un mécanisme.

Ce sprint ne le branche pas — c'est un interdit explicite du brief. Il en pose la
**précondition** : sans le présent contrat, brancher la récupération obligerait à
choisir dans l'urgence lequel des quatre vocabulaires fait foi.

**Précondition supplémentaire, non résolue ici** : tant que le CSS colore par
rang (§3), une bande de récupération pilotée par identifiant **ne fonctionnerait
pas** — les deux mécanismes ne parlent pas de la même chose. `OQ_POSITIONAL_CSS_01`
est donc bloquant pour le branchement, pas seulement souhaitable.

---

## 7. Décisions ouvertes

| Id | Sujet | État |
|---|---|---|
| `OQ_POSITIONAL_CSS_01` | Le CSS colore par `nth-of-type`, pas par identifiant. **Bloquant** pour tout pilotage par la donnée. | ouvert — corriger avant le branchement récupération |
| `OQ_STABLE_ID_ORPHAN_01` | Le vocabulaire `zone-*` du contrat de design n'est implémenté par aucun asset ni consommé par aucun runtime. Faut-il l'implémenter, ou acter que les identifiants de plaque font foi ? | ouvert — **recommandation : acter les identifiants de plaque**, et rétrograder `zone-*` au rang de nom logique |
| `OQ_PEC_SPLIT_01` | Partition claviculaire / sternocostale | documentée, non construite (`docs/OQ_PEC_SPLIT_01.md`) |
| `OQ_WA_SILHOUETTE_01` | La silhouette worked-area est schématique et non anatomique ; doit-elle un jour être remplacée par des plaques réelles ? | ouvert — hors périmètre |

Sur `OQ_STABLE_ID_ORPHAN_01`, ma recommandation est motivée : maintenir deux
familles d'identifiants dont une n'est jamais utilisée coûte de la vigilance sans
rien garantir. Les identifiants de plaque sont réels, testés et gelés par SHA.

---

## 8. Ce qui est désormais commandable

Avec ce contrat, une commande de géométrie est **complète et non ambiguë** : la
grammaire des noms est fixée (§5.1), la structure de groupes est imposée (§5.2),
les critères de rejet sont explicites (§5.4) et l'ordre de production est motivé
par la biomécanique (§5.5).

**Réserve à lever avant de commander** : `OQ_POSITIONAL_CSS_01`. Les contraintes
§5.2 la neutralisent pour des assets conformes, mais elles reportent le risque
sur la discipline du producteur au lieu de l'éliminer dans le code. Un asset
livré demain fonctionnera ; un asset régénéré dans six mois avec un ordre de
groupes différent casserait silencieusement.

---

## Verdict

**CONTRAT ÉTABLI — une réserve technique explicite.**

Les quatre vocabulaires sont recensés — dont un, la position DOM, qui n'avait
jamais été relevé et qui est le plus fragile des quatre. La table
zone → cadre → surface → région est complète, y compris pour les sept zones sans
géométrie. Les surfaces orphelines sont tranchées une par une : `delt-anterior`
**MERGE**, `context` **IGNORE**, aucune réservation spéculative.

Aucune taxonomie nouvelle, aucun renommage, aucun asset, aucun changement
runtime. Le trou `zone_recovery` est documenté et **délibérément laissé ouvert**.

Le point qui change la suite n'est pas la table : c'est **`OQ_POSITIONAL_CSS_01`**.
Le contrat de production le borne, il ne le supprime pas. Tant que la couleur
dépend du rang d'un groupe plutôt que de son identité, la promesse
« l'identifiant choisit la surface » reste une intention — et c'est elle qu'il
faudra tenir avant de brancher la moindre donnée de récupération.

---

## Annexe de clôture (post-merge)

| | |
|---|---|
| Base | `28ca001` |
| PR | **#122 MERGED** |
| Merge | **`3873f58`** via `--merge --match-head-commit 810de7a` — **sans squash, sans `--admin`, sans force** |
| CI canonique | **`32066531124` — 6/6 success** |
| Sonar | `SonarCloud` **success** · gate externe **pass** |
| Gitar | pass |
| Threads | **0 non résolu** |
| CI PR | **7 checks verts du premier coup, aucun aller-retour** |
| Tier `check_scope` | `ISOLATED` |

### Portée réellement tenue

`git diff` du merge : **2 fichiers, 659 insertions, 0 suppression**. Aucun asset,
aucun renommage, aucune ligne de runtime, aucune migration, aucune zone métier.
Le sprint a produit un document et des gardes — rien d'autre, comme annoncé.

### Ce que les gardes rendent impossible

Vingt-six tests lisent les fichiers réels — les SVG, la taxonomie, la feuille de
style — et non ce que le document affirme. Trois d'entre eux méritent d'être
nommés parce qu'ils protègent contre des dérives silencieuses :

- `test_a2_surface_tokens_match_the_audit` — un jeton de surface nouveau ou
  disparu dans un SVG fait tomber le contrat. L'inventaire ne peut pas vieillir.
- `test_context_group_is_first_in_every_view` — le CSS compte les rangs
  (§3) ; déplacer le contexte décalerait toutes les couleurs. La contrainte de
  production §5.2.1 est désormais **exécutable**, pas seulement écrite.
- `test_positional_css_still_present_because_this_sprint_changes_no_runtime` —
  garde inversée : elle **exige** que le défaut soit encore là. Si quelqu'un le
  corrige, le test tombe et force à retirer `OQ_POSITIONAL_CSS_01` en même temps.
  Un défaut corrigé sans que sa question ouverte le soit est un piège pour le
  suivant.

**Plantation vérifiée** : `zone_recovery` injecté dans `muscle_focus.html` fait
tomber `test_a8_zone_recovery_reaches_no_template`, qui **nomme le fichier
fautif**. Plantation retirée, `git diff` vide.

### Un défaut de mesure dans ma propre garde

Premier jet de `test_positional_css_still_present…` : la regex
`#auren-plate-region-\w+[^{]*nth-of-type\(\d\)` comptait **3** au lieu de **5**.
`[^{]*` traverse les retours à la ligne, donc elle fusionnait les sélecteurs
partageant un même bloc et comptait des *règles* là où le contrat parle de
*sélecteurs*. Bornée à la ligne (`[^{\n]*`). Sans cette correction la garde
aurait épinglé un nombre faux et se serait déclenchée au premier ajout de
sélecteur dans un bloc existant.

### Ce que ce contrat ne résout pas

Il rend une commande de géométrie **non ambiguë**. Il ne rend pas le rendu
**robuste** : `OQ_POSITIONAL_CSS_01` reste ouvert, et les contraintes §5.2
reportent le risque sur la discipline du producteur au lieu de l'éliminer dans le
code. Un asset conforme livré demain fonctionnera ; un asset régénéré dans six
mois avec un ordre de groupes différent casserait silencieusement, sans qu'aucun
test actuel ne l'attrape — les gardes vérifient l'ordre des fichiers **présents**,
pas celui d'un fichier à venir.

C'est le prochain sujet, et il est **bloquant** pour le branchement
`zone_recovery`.
