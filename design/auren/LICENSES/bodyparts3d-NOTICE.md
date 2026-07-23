# NOTICE — BodyParts3D (source primaire de dérivation du BodyMap)

**Licence** : Creative Commons Attribution 4.0 International (**CC BY 4.0**) — voir [`CC-BY-4.0.txt`](CC-BY-4.0.txt).
**Revalidée le** : 2026-07-23 sur la page de licence officielle
`https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html` (mise à jour de licence 2025-02-27).

## Attribution obligatoire (texte exact)
```
BodyParts3D, © The Database Center for Life Science licensed under
CC Attribution 4.0 International
```

## Portée dans le BodyMap Auren
- **Base corporelle** (`body-front-base`, `body-back-base`) : dérivée du maillage `FMA7163` (skin).
- **9 zones** : `pecs · delt_lat · delt_post · upper_back · biceps · triceps · quads · posterior · calves`,
  dérivées des maillages BodyParts3D 4.0 (release IS-A, package `isa_BP3D_4.0_obj_99.zip`,
  sha256 `40665852c49f218326590e204db91064a1ecfc3c6f8cbd7bbbcaac62c7cd409e`).

## Modifications déclarées
Extraction des maillages superficiels, rendu orthographique monochrome, vectorisation (Potrace 1.16),
simplification (Inkscape 1.4.4), regroupement en 11 zones fonctionnelles Auren, mise au contrat SVG
(viewBox `0 0 240 200`, 14 IDs stables). **Œuvre dérivée sous attribution** — Auren ne revendique **pas** la
propriété des données anatomiques sous-jacentes.

## Ce qui n'est pas revendiqué
Aucun endossement de DBCLS. Aucune revue anatomique professionnelle. Aucune clairance juridique.
L'éditeur déclare lui-même que la donnée peut contenir des erreurs et n'est pas un modèle canonique complet.

## Date d'accès des sources
Archives et licence relevées et hachées le **2026-07-23** (cf. `SB_ASSET_03_1_PROVENANCE_REGISTRY.md`).
