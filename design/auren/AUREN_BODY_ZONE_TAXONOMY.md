# AUREN — Body Zone Taxonomy

**Scaffold** : `Sb_ASSET_01.2` — Body Zone Taxonomy & Mapping Contract.
Contrat sémantique **normatif** des zones corporelles Auren. **Layer A (métier)** uniquement — aucune
géométrie, aucune validation anatomique. Un contrat sémantique **n'est pas** une validation anatomique.

> **Source de vérité runtime** : `app/services/muscle_mapping.py#ZONE_LABELS`. Ce document **miroir** cette
> vérité (parité testée) ; il ne la remplace pas. Le mapping structuré machine-lisible vit dans
> [`source/bodymap/auren_bodymap_mapping.yaml`](source/bodymap/auren_bodymap_mapping.yaml).

---

## 1. Les onze zones (exactement)

| Code | Label FR canonique | Macro compacte | ID SVG stable | Nature |
|---|---|---|---|---|
| `pecs` | Pectoraux | `chest` | `zone-pecs` | functional-body-zone |
| `delt_lat` | Deltoïdes latéraux | `shoulders` | `zone-delt_lat` | functional-body-zone |
| `delt_post` | Deltoïdes postérieurs | `shoulders` | `zone-delt_post` | functional-body-zone |
| `lats` | Dos largeur | `back` | `zone-lats` | functional-body-zone |
| `upper_back` | Dos épaisseur | `back` | `zone-upper_back` | **functional-aggregate** |
| `biceps` | Biceps | `arms` | `zone-biceps` | functional-body-zone |
| `triceps` | Triceps | `arms` | `zone-triceps` | functional-body-zone |
| `quads` | Quadriceps | `legs` | `zone-quads` | functional-body-zone |
| `posterior` | Ischios / Fessiers | `legs` | `zone-posterior` | **functional-aggregate** |
| `calves` | Mollets | `legs` | `zone-calves` | functional-body-zone |
| `core` | Core / Abdos | `core` | `zone-core` | functional-body-zone |

Les labels FR correspondent **exactement** au runtime (`ZONE_LABELS`). Aucun label n'est réinventé ici.

## 2. `unknown` — état de qualification, **pas** une zone

```
code:            unknown
nature:          état de qualification
anatomical_zone: false
label:           À qualifier
visual_behavior: neutral
```

`unknown` :
- **n'est pas** une douzième zone ;
- **ne possède pas** de `zone-unknown` ;
- **ne produit aucune** anatomie active ;
- **ne doit jamais** être ajouté aux métriques de couverture des onze zones ;
- **ne doit jamais** être converti automatiquement en région proche.

C'est l'état retourné par `build_body_map_descriptor(...)` quand aucune zone n'est qualifiée
(`status: unknown`, `needs_qualification: true`).

## 3. Zones agrégées (granularité honnête)

`upper_back` et `posterior` sont des **agrégats fonctionnels du produit**, pas des muscles anatomiques
unitaires.

- **`upper_back`** — zone fonctionnelle de **dos en épaisseur**. Ne prétend **pas** distinguer trapèzes,
  rhomboïdes, faisceaux individuels ou insertion précise.
- **`posterior`** — agrégat fonctionnel **ischios / fessiers / chaîne postérieure basse**. Ne prétend **pas**
  localiser précisément chaque muscle ou faisceau.

> Le futur BodyMap doit refléter la **granularité de la donnée**, jamais une précision supérieure.

## 4. Six macro-régions visuelles compactes

```
pecs                         → chest
delt_lat, delt_post          → shoulders
lats, upper_back             → back
biceps, triceps              → arms
quads, posterior, calves     → legs
core                         → core
```

Chaque zone appartient à **exactement une** macro ; l'union des six macros = les onze zones. Mapping
identique à `_WA_ZONE_TO_REGION` (`app/templates/_partials/worked_area_body_map.html`).

## 5. Macros visuelles ≠ axes analytiques — **règle absolue**

```
BODYMAP COMPACT MACROS ARE NOT RADAR_AXES
```

Le code contient **deux modèles distincts** qu'un futur développeur ne doit **jamais** fusionner :

| | Macros compactes BodyMap (présentation) | `RADAR_AXES` (analytics) |
|---|---|---|
| Dos | **`back`** (lats + upper_back **fusionnés**) | **`back_width`** (lats) + **`back_thickness`** (upper_back) — **séparés** |
| Bas du corps | `legs` (quads + posterior + calves) | **`lower`** (quads + posterior + calves) |
| Core | **`core`** (isolé) | **absent** de RADAR_AXES |
| Rôle | quelle silhouette surligner | scores / radar / Body Intelligence |

`RADAR_AXES` = `[pecs, shoulders, back_width, back_thickness, arms, lower]`. **Ce sprint ne modifie ni
`RADAR_AXES`, ni `RADAR_AXIS_ORDER`, ni les scores de zone, ni les agrégations analytics, ni Body
Intelligence.**

## 6. Layer A (métier, ce sprint) vs Layer B (géométrique, futur)

| Layer A — métier (contrat, ici) | Layer B — géométrique (production humaine, futur) |
|---|---|
| 11 codes, labels FR, 6 macros, mapping | géométrie SVG, paths, coordonnées |
| IDs SVG stables (API) | vues anatomiques détaillées par zone |
| états sémantiques, invariants | variantes corporelles produites |
| `geometry_status: NOT YET PRODUCED` | master anatomique validé |

Le master humain (Layer B) appartient à `OPERATOR_ASSET_03.1` ; l'intake technique à `Sb_ASSET_03.2` ;
l'intégration runtime à `Sb_ASSET_04.1` **après** franchissement de l'`ASSET INTEGRATION GATE`.

## 7. IDs SVG stables (API du pack futur)

```
auren-bodymap · body-front-base · body-back-base
zone-pecs · zone-delt_lat · zone-delt_post · zone-lats · zone-upper_back
zone-biceps · zone-triceps · zone-quads · zone-posterior · zone-calves · zone-core
```

Un ID par zone · **aucun** `zone-unknown` · aucun renommage/minification/alias implicite/ID genré/path
fusionné. Toute évolution incompatible = **nouvelle spec + migration de contrat** (bump `contract_version`).

## 8. États de présentation (5, sans couleur)

`neutral` (zone connue non active) · `primary` (zone principale) · `secondary` (zone secondaire) ·
`unknown` (aucune zone qualifiée) · `disabled` (surface/variante indisponible). **Aucune couleur** dans le
contrat (pilotée par les tokens runtime) ; les états ne sont **jamais** distingués par la seule couleur.

## 9. Évolution du contrat

Nécessitent une **migration de contrat** (nouvelle spec + `contract_version`) : renommer/ajouter/supprimer
un code de zone · changer un ID SVG · modifier le mapping macro · changer un label FR canonique.
N'en nécessitent pas : affiner les vues du Layer B (géométrie), produire une variante corporelle, ajouter
une surface consommatrice.

## 10. Gate

`ASSET INTEGRATION GATE: BLOCKED PENDING HUMAN / ANATOMICAL / LEGAL / MOBILE APPROVALS`. La présence de ce
contrat dans `design/auren/` **n'autorise pas** l'intégration runtime.
