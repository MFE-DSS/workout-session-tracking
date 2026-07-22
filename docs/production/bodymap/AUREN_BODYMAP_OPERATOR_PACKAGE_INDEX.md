# AUREN — BodyMap Operator Package — INDEX

**Cycle** : `Sx_ASSET_03` — BodyMap Human Production Package.
**Ce package** : dossier de production humaine **exécutable** par un illustrateur + relecteur anatomique +
responsable produit + responsable provenance/PI. **Il ne produit PAS le master SVG.**

> **BODYMAP SEMANTIC CONTRACT: ALREADY COMPLETE / IMMUTABLE** (`Sb_ASSET_01.2`). Ce package produit le
> **comment produire**, pas la silhouette. `ASSET INTEGRATION GATE: BLOCKED`. `PROFESSIONAL LEGAL CLEARANCE:
> NOT CLAIMED`.

## Contenu du package (`docs/production/bodymap/`)
1. [`AUREN_BODYMAP_OPERATOR_PACKAGE_INDEX.md`](AUREN_BODYMAP_OPERATOR_PACKAGE_INDEX.md) — ce fichier.
2. [`AUREN_BODYMAP_ILLUSTRATOR_BRIEF.md`](AUREN_BODYMAP_ILLUSTRATOR_BRIEF.md) — direction artistique normative.
3. [`AUREN_BODYMAP_SVG_STRUCTURE_AND_DELIVERY_CONTRACT.md`](AUREN_BODYMAP_SVG_STRUCTURE_AND_DELIVERY_CONTRACT.md)
   — contrat géométrique SVG (viewBox, IDs, groupes, livrables).
4. [`AUREN_BODYMAP_IP_PROVENANCE_AND_SOURCE_DISCLOSURE_REQUIREMENTS.md`](AUREN_BODYMAP_IP_PROVENANCE_AND_SOURCE_DISCLOSURE_REQUIREMENTS.md)
   — exigences PI / provenance / déclaration des sources & outils & IA.
5. [`AUREN_BODYMAP_ANATOMICAL_PRODUCT_MOBILE_REVIEW_PROTOCOL.md`](AUREN_BODYMAP_ANATOMICAL_PRODUCT_MOBILE_REVIEW_PROTOCOL.md)
   — protocoles de revue anatomique + produit + mobile.
6. [`AUREN_BODYMAP_DELIVERY_MANIFEST_TEMPLATE.md`](AUREN_BODYMAP_DELIVERY_MANIFEST_TEMPLATE.md) — template de
   manifeste de livraison opérateur.

Références externes : [`../../research/AUREN_BODYMAP_REFERENCE_DUE_DILIGENCE.md`](../../research/AUREN_BODYMAP_REFERENCE_DUE_DILIGENCE.md).
Contrat sémantique source : [`../../../design/auren/AUREN_BODY_ZONE_TAXONOMY.md`](../../../design/auren/AUREN_BODY_ZONE_TAXONOMY.md)
+ [`../../../design/auren/source/bodymap/auren_bodymap_mapping.yaml`](../../../design/auren/source/bodymap/auren_bodymap_mapping.yaml).

## Variante V1 à produire
```
body_variant: male_neutral_v1   (P0 PRODUCTION VARIANT)
female_neutral_v1 / neutral_abstract_v1 / vue latérale : P2 — NON produits en OPERATOR_ASSET_03.1
```

## Ce que l'opérateur (`OPERATOR_ASSET_03.1`) doit remettre
Master SVG canonique `auren_bodymap_master.svg` + source native éditable + registre références + déclarations
(outils/tiers/IA) + previews de revue + manifeste de livraison rempli. **Aucun de ces fichiers n'entre dans
`app/static/` ni ne franchit le gate.**

## Chaîne
```
Sx_ASSET_03 (ce package, spec)  →  OPERATOR_ASSET_03.1 (production humaine externe)
   →  Sb_ASSET_03.2 (intake technique + validation)  →  [gate]  →  Sx_ASSET_04 / Sb_ASSET_04.1 (intégration)
```
**Point d'arrêt** : le package est défini ; le master n'est **pas** produit ; le gate reste **BLOCKED**.
