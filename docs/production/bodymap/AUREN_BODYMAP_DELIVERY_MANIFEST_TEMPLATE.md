# AUREN — BodyMap Delivery Manifest Template

**Cycle** : `Sx_ASSET_03`. Template **à remplir par l'opérateur** (`OPERATOR_ASSET_03.1`) et vérifié par
`Sb_ASSET_03.2`. Ce fichier est un **gabarit** (valeurs `<...>` à compléter) — il ne décrit aucun master
existant.

> Statuts initiaux figés ci-dessous. **Aucun** `approved` / `legally-cleared` / `runtime-integrated` autorisé.

---

```yaml
# AUREN BodyMap — Delivery Manifest (à remplir à la livraison ; YAML/JSON-compatible)
package_id: auren.bodymap.master.male_neutral_v1
package_version: <semver, ex. 0.1.0>
body_variant: male_neutral_v1
author: <nom>
organisation: <organisation / freelance>
production_start: <YYYY-MM-DD>
production_end: <YYYY-MM-DD>

tool_name: <outil vectoriel>
tool_version: <version>
native_source_filename: <fichier source natif>
native_source_sha256: <sha256 du source natif>
canonical_svg_filename: auren_bodymap_master.svg
canonical_svg_sha256: <sha256 du SVG canonique>

reference_register: <chemin du registre des références consultées + licence de chacune>
third_party_components: <NONE | liste déclarée>
ai_usage: <NONE | {tool, version, functions, purpose/prompts, affected_parts, human_redraw_method}>

stable_ids: [auren-bodymap, body-front-base, body-back-base,
  zone-pecs, zone-delt_lat, zone-delt_post, zone-lats, zone-upper_back,
  zone-biceps, zone-triceps, zone-quads, zone-posterior, zone-calves, zone-core]
viewbox: "0 0 240 200"
zone_groups: <11 groupes <g id="zone-*"> — un par zone, IDs uniques>
delivery_files: <master SVG · source natif · previews (32) · déclarations · notes · changelog · contact sheet>

rights_status: not-yet-confirmed
anatomical_review_status: not-started
product_review_status: not-started
mobile_review_status: not-started
legal_review_status: professional-review-required

operator_notes: <notes de production>
```

## Règles de remplissage
- `stable_ids` : **exactement** les 14 ci-dessus ; **aucun** `zone-unknown` ; aucun ID dupliqué.
- `viewbox` : **`0 0 240 200`** (contrat SVG §1) — non négociable.
- Les 5 statuts de revue restent `not-started` / `not-yet-confirmed` / `professional-review-required` jusqu'aux
  revues réelles.
- **Interdits** : `approved`, `legally-cleared`, `runtime-integrated` (aucune valeur de ce type avant
  franchissement du gate).
- `native_source_sha256` / `canonical_svg_sha256` : calculés à la livraison ; le source natif est **livré dans
  l'archive opérateur**, pas nécessairement committé Git avant intake.
