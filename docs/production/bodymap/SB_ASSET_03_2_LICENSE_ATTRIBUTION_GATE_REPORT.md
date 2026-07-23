# SB_ASSET_03.2 — License & Attribution Gate Report

**Date** : 2026-07-23

## Revalidation le jour de l'intake (§12)
| Source | Page officielle | Licence |
|---|---|---|
| **BodyParts3D** | `dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html` | **CC BY 4.0 International** ✅ |
| **Servier Medical Art** | `smart.servier.com` | **CC BY 4.0** ✅ |

Attributions exactes confirmées :
```
BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International
Image adapted from Servier Medical Art, licensed under CC BY 4.0
```

## Géométrie incorporée — uniquement CC BY 4.0
Vérifié dans les SVG et les scripts générateurs : **0 référence** à Wikimedia, Z-Anatomy, OpenStax 2e, ni à
aucun contenu **BY-SA** ou **NC**. Seules **BodyParts3D** et **Servier Medical Art** fournissent de la
géométrie.

**OpenStax 1ʳᵉ édition (CC BY 4.0)** et **Sobotta 1909 (domaine public)** : contrôle documentaire uniquement,
**aucune géométrie incorporée**.

## Package d'attribution — READY
Déposé dans `design/auren/LICENSES/` :
- `CC-BY-4.0.txt` — **legalcode officiel verbatim** (récupéré de creativecommons.org, > 18 Ko).
- `bodyparts3d-NOTICE.md` — attribution, portée (base + 9 zones), modifications, date d'accès, non-endossement.
- `servier-medical-art-NOTICE.md` — attribution, portée (`lats`, `core`), modifications, non-endossement.

Chaque notice identifie la source, référence CC BY 4.0, **déclare explicitement les modifications**, la date
d'accès, la provenance des zones, et l'**absence d'endossement implicite**.

## Statuts
```
ATTRIBUTION PACKAGE: READY
ATTRIBUTION SURFACE: NOT YET IMPLEMENTED
PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED
LEGAL REVIEW: REQUIRED
```

## Verdict
**LICENSE & ATTRIBUTION GATE: PASS pour l'entrée en design source ; RUNTIME BLOQUÉ.** Les deux sources sont
CC BY 4.0 revalidées, l'attribution est prête et complète, aucune contamination copyleft/NC. **L'absence de
surface de crédits dans l'application interdit toujours l'intégration runtime** — dette explicite portée par
`Sx_ASSET_04`.
