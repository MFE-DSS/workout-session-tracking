# AUREN — Muscle Focus P0 Plate Blueprints (`Sb_ASSET_03B.1`)

**Type** : **7 blueprints P0 exacts** — **DOCS-ONLY**. Chaque blueprint **fige le descripteur** d'une plaque P0
(les 3 zones les plus critiquées) **sans produire aucune géométrie**. `ASSET INTEGRATION GATE: BLOCKED` ·
`PLATE GEOMETRY: NOT PRODUCED`.
**Références** : [`AUREN_MUSCLE_FOCUS_ID_CONTRACT.md`](AUREN_MUSCLE_FOCUS_ID_CONTRACT.md) ·
[`AUREN_MUSCLE_FOCUS_DESCRIPTOR_SCHEMA.md`](AUREN_MUSCLE_FOCUS_DESCRIPTOR_SCHEMA.md) ·
[`AUREN_MUSCLE_FOCUS_VIEW_AND_CROP_CONTRACT.md`](AUREN_MUSCLE_FOCUS_VIEW_AND_CROP_CONTRACT.md) · spec §13, §16.

## Périmètre P0 (7 blueprints)

Les **3 zones les plus critiquées**, en paires Regional + Muscle → **7 plaques** :

| # | Plate | Level | Zone(s) |
|---|---|---|---|
| 1 | `auren-plate-region-chest` | N2 | `pecs` |
| 2 | `auren-plate-muscle-pecs` | N3 | `pecs` |
| 3 | `auren-plate-region-shoulders` | N2 | `delt_lat`, `delt_post` |
| 4 | `auren-plate-muscle-delt_lat` | N3 | `delt_lat` |
| 5 | `auren-plate-muscle-delt_post` | N3 | `delt_post` |
| 6 | `auren-plate-region-posterior` | N2 | `posterior` |
| 7 | `auren-plate-muscle-posterior` | N3 (grouped-honest) | `posterior` |

**Cadrage P0 commun** (spec §13 + adversarial #7) : vues **`front`/`back` uniquement** · mode **clean +
caption** · **+ lien exercice N2 en liste** (granularité **zone**) — *aucune plaque n'est livrée sans route
vers une action de training*. Overlays techniques (insertions/fibres/contraction), vues `lateral`/`section`, et
Exercise Mechanics Overlay interactif = **P1** (hors P0). `markers: []` en P0 (viennent avec l'overlay P1) ;
la **forme clean** doit néanmoins respecter le cas d'exigence §16.

---

## 1 — `auren-plate-region-chest` (N2)

```yaml
plate_id: auren-plate-region-chest
level: 2-regional
mode: muscle-heads
schema_version: "0.1.0"
zone_codes: [pecs]
macro: chest
region_key_kind: macro
views: [front]
viewbox_local: "<crop master demi-torse — figé au build géométrique>"
parts: [part-pecs-clavicular, part-pecs-sternocostal]
markers: []
exercise_link_granularity: zone
exercise_link_mode: list
source_refs: [servier-smart, openstax-ap1-2013]
attribution_required: true
ai_usage: NONE
non_medical: true
scored: false
caption_mirrors_overlay: true
```
- **Cas d'exigence (§16)** : éventail **convergent** claviculaire + sterno-costal vers une **insertion humérale
  unique** — jamais deux blobs symétriques.
- **Caption (miroir)** : « Pectoraux — chef claviculaire, chef sterno-costal. Rôle : adduction/flexion de
  l'épaule. Représentation non médicale, non mesurée. »
- **Lien exercice** : liste « exercices — Pectoraux » (zone), route vers l'action « ajouter à la séance ».

## 2 — `auren-plate-muscle-pecs` (N3)

```yaml
plate_id: auren-plate-muscle-pecs
level: 3-muscle
mode: muscle-heads
schema_version: "0.1.0"
zone_codes: [pecs]
macro: chest
region_key_kind: null
views: [front]                    # P0 ; lateral (convergence) = P1
viewbox_local: "<repère local pecs — figé au build>"
parts: [part-pecs-clavicular, part-pecs-sternocostal]
markers: []                       # insertion humérale = overlay P1
exercise_link_granularity: zone
exercise_link_mode: list          # interactive-overlay = P1
source_refs: [servier-smart, openstax-ap1-2013]
attribution_required: true
ai_usage: NONE
non_medical: true
scored: false
caption_mirrors_overlay: true
```
- **Cas d'exigence (§16)** : point de **convergence latéral** vers l'insertion — tue le cliché « poumons ».
- **Caption (miroir)** : idem #1, granularité faisceau **visuelle seulement** (surlignage), exercices = zone.

## 3 — `auren-plate-region-shoulders` (N2)

```yaml
plate_id: auren-plate-region-shoulders
level: 2-regional
mode: muscle-heads
schema_version: "0.1.0"
zone_codes: [delt_lat, delt_post]
macro: shoulders
region_key_kind: macro
views: [front, back]              # back requis pour le faisceau postérieur
viewbox_local: "<crop master épaule — figé au build>"
parts: [part-delt_lat-anterior, part-delt_lat-lateral, part-delt_post-posterior]
markers: []
exercise_link_granularity: zone
exercise_link_mode: list
source_refs: [servier-smart, openstax-ap1-2013]
attribution_required: true
ai_usage: NONE
non_medical: true
scored: false
caption_mirrors_overlay: true
```
- **Cas d'exigence (§16)** : 3 faisceaux **en contexte osseux** (clavicule / acromion / épine scapulaire),
  insertion deltoïdienne commune ; **vue dos requise** pour le postérieur.
- **Caption (miroir)** : « Épaules — deltoïde : faisceaux antérieur, latéral, postérieur. Rôle :
  abduction/flexion/extension de l'épaule. Non médical, non mesuré. »

## 4 — `auren-plate-muscle-delt_lat` (N3)

```yaml
plate_id: auren-plate-muscle-delt_lat
level: 3-muscle
mode: muscle-heads
schema_version: "0.1.0"
zone_codes: [delt_lat]
macro: shoulders
region_key_kind: null
views: [front]                    # lateral (3 faisceaux 3/4) = P1
viewbox_local: "<repère local deltoïde latéral — figé au build>"
parts: [part-delt_lat-anterior, part-delt_lat-lateral]
markers: []
exercise_link_granularity: zone
exercise_link_mode: list
source_refs: [servier-smart, openstax-ap1-2013]
attribution_required: true
ai_usage: NONE
non_medical: true
scored: false
caption_mirrors_overlay: true
```
- **Cas d'exigence (§16)** : ancrage osseux **obligatoire** (sans lui les faisceaux sont indistinguables).
- **Note zone** : `delt_lat`/`delt_post` = **même deltoïde** sous deux angles fonctionnels (2 zones métier, 1
  macro `shoulders`) — les `part-*` nomment des **faisceaux vus**, pas des muscles distincts. `delt_lat` a une
  **couverture exercice EKB propre** (zone existante) → lien exercice zone honnête.

## 5 — `auren-plate-muscle-delt_post` (N3)

```yaml
plate_id: auren-plate-muscle-delt_post
level: 3-muscle
mode: muscle-heads
schema_version: "0.1.0"
zone_codes: [delt_post]
macro: shoulders
region_key_kind: null
views: [back]                     # le postérieur EXIGE la vue dos
viewbox_local: "<repère local deltoïde postérieur — figé au build>"
parts: [part-delt_post-posterior]
markers: []
exercise_link_granularity: zone
exercise_link_mode: list
source_refs: [servier-smart, openstax-ap1-2013]
attribution_required: true
ai_usage: NONE
non_medical: true
scored: false
caption_mirrors_overlay: true
```
- **Cas d'exigence (§16)** : faisceau postérieur ancré sur l'**épine scapulaire**, **vue dos requise**.
- **Caption (miroir)** : « Deltoïde postérieur — extension/rotation externe de l'épaule. Non médical. »

## 6 — `auren-plate-region-posterior` (N2)

```yaml
plate_id: auren-plate-region-posterior
level: 2-regional
mode: muscle-heads
schema_version: "0.1.0"
zone_codes: [posterior]
macro: legs
region_key_kind: zone             # posterior est une ZONE (legs éclatée), pas une macro
views: [back]
viewbox_local: "<crop master bassin→cuisse postérieure — figé au build>"
parts: [part-posterior-gluteus, part-posterior-hamstring]
markers: []
exercise_link_granularity: zone
exercise_link_mode: list
source_refs: [servier-smart, openstax-ap1-2013]
attribution_required: true
ai_usage: NONE
non_medical: true
scored: false
caption_mirrors_overlay: true
```
- **Cas d'exigence (§16)** : crop **bassin→cuisse** ; distinguer fessier (superficiel, hanche) des 3 ischios ;
  **pas de « bas du corps générique »**.
- **`macro: legs`** alors qu'il n'existe **aucune** `auren-plate-region-legs` : `legs` est éclatée en
  quads/posterior/calves (ID Contract §3). La plaque régionale est clefée **zone** (`region_key_kind: zone`).

## 7 — `auren-plate-muscle-posterior` (N3, **grouped-honest**)

```yaml
plate_id: auren-plate-muscle-posterior
level: 3-muscle
mode: grouped-honest              # fessiers + ischios NOMMÉS sans localisation prétendue
schema_version: "0.1.0"
zone_codes: [posterior]
macro: legs
region_key_kind: null
views: [back]
viewbox_local: "<repère local chaîne postérieure — figé au build>"
parts: [part-posterior-gluteus, part-posterior-hamstring]
markers: []                       # insertion ischiatique commune = overlay P1
exercise_link_granularity: zone
exercise_link_mode: list
source_refs: [servier-smart, openstax-ap1-2013]
attribution_required: true
ai_usage: NONE
non_medical: true
scored: false
caption_mirrors_overlay: true
```
- **Mode grouped-honest** : la plaque **ne gagne jamais** une précision que la donnée ne porte pas (héritage
  agrégat honnête). Fessier et ischios sont **nommés** (labels `part-*`), pas prétendument localisés au faisceau.
- **Cas d'exigence (§16)** : insertion ischiatique commune ; vecteur d'extension de hanche (schéma, P1).
- **Caption (miroir)** : « Chaîne postérieure — fessiers et ischio-jambiers (groupe). Rôle : extension de
  hanche, flexion du genou. Groupe honnête : localisation par faisceau non prétendue. Non médical, non mesuré. »

---

## Invariants P0 (futur guard)

1. **Exactement 7** blueprints P0, `plate_id` ∈ 19 racines figées, aucun doublon.
2. `views ⊆ {front, back}` pour **tous** (P0) ; `markers == []` (overlay = P1) ; `mode`/`level` cohérents.
3. `exercise_link_granularity == "zone"` et `exercise_link_mode == "list"` pour **tous** (adversarial #7 : pas
   de cul-de-sac de connaissance ; #3 : pas de sous-zone).
4. `scored == false`, `non_medical == true`, `ai_usage == NONE` pour **tous** ; `caption_mirrors_overlay ==
   true`.
5. Aucune plaque n'émet un `zone-<code>` ni ne matérialise une 12ᵉ zone (les faisceaux sont des `part-*`).

## Verdict

**Verdict :** 🟢 **`MUSCLE FOCUS P0 BLUEPRINTS: LOCKED (7 / DOCS-ONLY).`** Les 7 descripteurs P0
(chest N2+N3, shoulders N2 + delt_lat N3 + delt_post N3, posterior N2+N3) sont figés : vues `front`/`back`,
clean + caption + **lien exercice zone-liste** (jamais cul-de-sac, jamais sous-zone), cas d'exigence §16 en
contraintes de forme, caption-miroir, sources Servier + OpenStax 1ʳᵉ éd. **Aucune géométrie, aucun viewBox
chiffré.** `PLATE GEOMETRY: NOT PRODUCED` · `ASSET INTEGRATION GATE: BLOCKED`.
