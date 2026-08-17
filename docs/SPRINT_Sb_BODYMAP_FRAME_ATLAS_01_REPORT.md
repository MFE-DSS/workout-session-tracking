# Sprint `Sb_BODYMAP_FRAME_ATLAS_01` — socle de cadres pré-rendus

**Base canonique** : `92a3b6b`
**Tier `check_scope`** : `SHARED_CODE`
**Statut** : implémentation locale verte — PR à ouvrir

---

## 1. Rapport d'audit des points d'intégration (livrable 1)

Les huit capacités demandées avant build, vérifiées dans le code, pas dans les
rapports.

| # | Capacité | Verdict | Où |
|---|---|---|---|
| 1 | Où `mf-shoulders-view` est défini | **présent** | `muscle_focus.html:52-53` (page `/science`) |
| 2 | Rendu des radios face/dos | **présent** | 2 `<input type="radio">` frères + `<fieldset>`, sélecteurs CSS `:checked ~` |
| 3 | Comment une zone choisit sa surface | **partiel — deux mécanismes disjoints** | voir §1.1 |
| 4 | `zone_recovery[zone].band` colore une surface | **ABSENT** | voir §1.2 |
| 5 | Fallback unknown / macro | **présent** | `worked_area_body_map.html` + `unknown_state` du contrat |
| 6 | Consommateurs des 11 zones | **présent** | `muscle_mapping.py`, contrat YAML, `_WA_ZONE_TO_REGION`, `body_map_descriptor.py` |
| 7 | Tests protégeant `worked_area_body_map.html` | **présent** | `test_worked_area_body_map.py` (185 l.), `test_auren_body_zone_contract.py` (295 l.) |
| 8 | Géométrie disponible | **3 plaques, 4 panneaux** | chest (1), shoulders (2), posterior (1) |

### 1.1 — Trois vocabulaires d'identifiants coexistent

C'est le constat structurant de l'audit. Ils ne se recouvrent pas :

| Vocabulaire | Exemple | Porté par |
|---|---|---|
| Zones métier | `zone-pecs`, `zone-delt_lat` | contrat de design — **implémenté par aucun asset** |
| Plaques BodyParts3D | `front-delt-anterior`, `back-gluteus` | les 3 SVG réels |
| Silhouette schématique | classe CSS `wa-region--chest` | `worked_area_body_map.html` |

Le `stable_svg_id` du contrat (`zone-*`) est une **API du futur pack d'assets** :
`geometry_status: NOT YET PRODUCED` le dit déjà. Aucune régression ici — mais
toute commande de géométrie devra choisir lequel des trois fait foi.

### 1.2 — La capacité 4 n'existe pas

`zone_recovery` **n'atteint aucun template** (`grep zone_recovery app/templates`
→ 0 résultat). Le couplage « la bande de récupération choisit une couleur,
l'identifiant choisit la surface » était une **proposition du brainstorming
Atlas des Cadres**, pas un mécanisme en place. Les plaques de `/science` sont
décoratives (`aria-hidden="true"`) et ne portent aucune donnée.

**Pourquoi ce n'est pas un HARD STOP de ce sprint** : aucun des livrables 01–03
n'en dépend. Le socle déclare des cadres et des zones ; il ne colore rien depuis
la récupération, et ce sprint n'a rien inventé pour combler ce trou. Le brancher
serait un sprint distinct, et il exige d'abord l'arbitrage §1.1.

---

## 2. Brainstorming / Options / Risques / Choix (CLAUDE.md §3)

**Option A — sélecteur générique dans le template.** Boucle Jinja sur une liste
passée par la route. Rejetée : laisse la logique de cadres dans le template,
viole A7.

**Option B — nouveau moteur de rendu BodyMap.** Un service qui produit le SVG.
Rejetée frontalement : le brief interdit d'inventer un moteur, et les 3 plaques
sont gelées par SHA.

**Option C — retenue : contrat déclaratif + généralisation du mécanisme
existant.** Le sélecteur épaules est déjà un **filmstrip** : la plaque est une
bande de N panneaux, le cadre recadre à 1/N, `translateX` glisse. Ce mécanisme
se généralise sans rien réécrire.

**Risque principal identifié et neutralisé** : casser le rendu des plaques
livrées. Pour `--mf-frames: 2` la formule générique
`translateX(calc(-100% / var(--mf-frames)))` se résout à `-50%` — exactement la
valeur codée en dur auparavant. Le rendu est identique par construction, pas par
vérification a posteriori.

---

## 3. Ce qui a été livré

| Livrable | Fichier |
|---|---|
| 02 · contrat zone → surfaces → cadres | `app/services/bodymap_frames.py` *(neuf)* |
| 03 · moteur multi-cadres déclaratif | `app/templates/_partials/bodymap_frame_selector.html` *(neuf)* |
| 03 · CSS générique sur N | `app/static/css/app.css` |
| 04 · socle 11 zones à vide | `zone_surfaces()` / `resolve_zone_surface()` |
| — · miroir du contrat de design | `auren_bodymap_mapping.yaml` → `1.1.0` |
| 05-08 · tests | `test_bodymap_frame_atlas.py` (36), `test_bodymap_frame_atlas_viewport.py` (6) |
| — · question ouverte | `docs/OQ_PEC_SPLIT_01.md` |

### La règle qui gouverne

> Le modèle métier gouverne le visuel. Le visuel ne crée pas de zone.

Appliquée deux fois : la plaque épaules contient des surfaces
`*-delt-anterior` mais **aucune zone `delt_ant` n'existe** (Option A) ; le
pectoral reste **une** zone malgré l'intérêt de la partition (OQ_PEC_SPLIT_01).

### Couverture honnête

`geometry_coverage()` retourne les chiffres réels, testés :
**11 zones · 4 avec plaque · 7 sans · 3 plaques produites.**
Les sept zones sans géométrie (`lats`, `upper_back`, `biceps`, `triceps`,
`quads`, `calves`, `core`) tombent en `macro` et ne sont **jamais** colorées
comme si elles étaient connues.

---

## 4. Acceptation

| # | Critère | Méthode | Résultat |
|---|---|---|---|
| A1 | Aucun changement de taxonomie | liste exacte × 4 tables + contrat | **PASS** |
| A2 | Pas de `delt_ant` | garde sur 8 codes interdits | **PASS** |
| A3 | Pas de split `pecs` | idem + OQ documentée | **PASS** |
| A4 | Multi-cadres sans JS | garde `<script>`/`on*`/WebGL/canvas | **PASS** |
| A5 | 360 px | **Playwright mesuré** : overflow ≤ 0, pastilles ≥ 44 px, filmstrip glisse | **PASS** |
| A6 | Unknown honnête | `None`/`unknown`/`delt_ant`/typo → `RENDER_NONE` | **PASS** |
| A7 | Source déclarative | parité contrat ↔ runtime + garde anti-littéraux | **PASS** |
| A8 | Plaques préservées | 13/13 du garde SHA + comptes de cadres | **PASS** |
| A9 | Non médical | garde sur la **copie visible** uniquement | **PASS** |
| A10 | Diff métier limité | voir §5 | **PASS** |

### A5 — mesuré, pas lu

Les trois derniers défauts réels de ce dépôt (débordement 393 px dans un viewport
de 360, CTA couvert par la barre de navigation, ancre garée sous l'en-tête
collant) ont tous été trouvés par mesure et aucun par lecture. Le test rend donc
le vrai HTML SSR avec la vraie feuille de style à 360×640 et mesure.

Résultat notable : les pastilles passent de **24 px à 44 px** de hauteur. C'est
une amélioration de cible tactile, pas une régression — A5 exigeait de ne pas
*réduire* les cibles critiques.

### Gardes vérifiées par plantation

Une violation a été **plantée** (`delt_ant` ajouté aux zones de la plaque
épaules) : deux gardes indépendantes sont tombées
(`test_a1_frame_module_declares_no_zone_of_its_own`,
`test_a2_shoulders_plate_exposes_only_the_two_business_zones`). Plantation
retirée. Une garde non plantée est une garde non prouvée.

### Deux tests déplacés, aucun affaibli

`test_wrapper_includes_three_plates_and_toggle` lisait le **texte du template**
pour vérifier les ids des radios. Ces ids ne sont plus des littéraux — c'est
précisément ce qu'exige A7. Les assertions sont remontées vers le **HTML rendu**
(`test_science_renders_declared_frame_selector`), ce qui est strictement plus
fort : on prouve le balisage que le navigateur reçoit. La garde a en outre gagné
l'assertion inverse (`mf-shoulders-front` **absent** du template).

`test_contract_parses_with_stdlib_json` épinglait `contract_version == "1.0.0"`
→ `1.1.0`. Extension additive et rétrocompatible.

---

## 5. A10 — diff sur les fichiers protégés

| Cible | Diff |
|---|---|
| `app/services/recommendation.py` | **vide** |
| planner / `slot_intent` / `morpho_program_generator` | **vide** |
| `migrations/` | **vide** |
| `app/models.py` | **vide** |
| `app/services/muscle_mapping.py` (dont `ZONE_VOLUME_TARGET`) | **vide** |
| les 3 SVG de plaques | **vide** (SHA gelés vérifiés) |
| `AGENTS.md` | **non committé** |

---

## 6. Vérifications locales

| Check | Résultat |
|---|---|
| `check_scope.py` | `SHARED_CODE` — full sweep local non requis |
| `ruff` fichiers neufs | propre (`C901` restant = `session_detail`, préexistant, non touché) |
| `check_ruff_budget.py` | 281 ≤ 548 |
| `check_spec_protocol.py` | OK |
| Suites ciblées | 78 passés |
| Broad sweep bodymap/visual/UI | **523 passés** |
| Broad sweep routeur sessions | **901 passés** |

Le full sweep local est légitimement skippé à ce tier ; la CI parallélisée sur PR
reste la source de vérité (`CLAUDE.md` §1).

---

## 7. Ce qui reste hors dépôt (livrable 9)

Le socle sait déclarer et afficher N cadres. Il ne peut pas en **produire**.

1. **Les maillages BodyParts3D ne sont pas versionnés** — workspace opérateur
   externe (`02_catalog/`, `05_review/`). Aucun nouveau cadre ne peut être rendu
   depuis ce dépôt.
2. **Profil corps entier** — plan révélateur de 9 zones sur 11. Le meilleur
   rendement de toute la roadmap. Un seul rejeu du pipeline Blender.
3. **Dessus épaules** — le seul cadre que le profil ne couvre pas.
4. **Les 7 plaques manquantes** — par valeur décroissante : `lats`,
   `upper_back`, puis `quads`, `calves`, puis `biceps`, `triceps`, puis `core`.
5. **Revue anatomique** de chaque tracé — jamais automatisable.
6. **Simplification cockpit** — une planche 4096×2048 reste illisible en
   vignette ; il faut une simplification *dérivée*, pas une réduction d'échelle.

Chaque plaque livrée ensuite **allume sa zone sans qu'une ligne d'UI change** :
`REGIONAL_PLATES` gagne une entrée, `zone_surfaces()` bascule l'entrée de
`macro` à `plate`, et les tests de couverture le constatent.

### Décisions à rendre avant de commander de la géométrie

- **§1.1** — lequel des trois vocabulaires d'identifiants fait foi pour le pack
  d'assets à produire.
- **§1.2** — si et quand `zone_recovery` doit piloter une couleur de surface, et
  sur quelle surface (cockpit, `/science`, ou les deux).
