# SB_ASSET_03.1 — Déclaration d'usage d'IA

**Cycle** : `Sx_ASSET_03` (amendé SOURCE-REUSE-FIRST) · **Build** : `Sb_ASSET_03.1` · **Date** : 2026-07-23

```
AI_USAGE:
NONE
```

## Portée de la déclaration
Couvre l'intégralité du build `Sb_ASSET_03.1` : acquisition des sources, extraction des maillages, inspection
topologique, scène Blender, rendus, vectorisation, alignement, assemblage SVG, validation, previews et
package d'intake.

## Ce qui n'a PAS été fait
Aucun outil génératif n'a produit, modifié, complété ou corrigé :
- de la **géométrie** (maillage, silhouette, contour, chemin SVG) ;
- une **frontière musculaire** ou une limite de zone ;
- une **preuve de provenance** ;
- une **validation anatomique**.

Aucune image, aucun modèle 3D et aucun tracé n'a été synthétisé. Aucun moodboard, aucune exploration
stylistique et aucune variation de contours par IA n'a été employée — bien que la spec les autorise.

## Origine réelle de chaque élément géométrique

| Élément | Origine |
|---|---|
| `body-front-base`, `body-back-base` | rendu orthographique du maillage **BodyParts3D `FMA7163` (skin)**, vectorisé par **Potrace 1.16** |
| 9 zones (`pecs`, `delt_lat`, `delt_post`, `upper_back`, `biceps`, `triceps`, `quads`, `posterior`, `calves`) | rendus orthographiques de **maillages BodyParts3D 4.0** identifiés par leur **FMA ID officiel**, vectorisés par **Potrace 1.16** |
| `zone-lats`, `zone-core` | **chemins vectoriels DrawingML de Servier Medical Art**, convertis en SVG par un script stdlib écrit pour ce build, masqués en monochrome, puis vectorisés par **Potrace 1.16** |
| Simplification finale (export compact) | **Inkscape 1.4.4**, verbe intégré `path-simplify` |
| Mise au contrat (viewBox, 14 IDs, groupes) | **script Python stdlib déterministe** (`vectorize_and_assemble.py`) |

Chaque coordonnée du prototype est donc **traçable à une source sous licence**, via une chaîne d'outils
déterministe et rejouable. Aucune n'est d'origine générative.

## Outils employés (aucun n'est un modèle génératif)

| Outil | Version | Rôle |
|---|---|---|
| Blender | 5.2.0 LTS (`fbe6228777e7`) | import OBJ, inspection topologique BMesh, caméras orthographiques, rendus |
| Potrace | 1.16 | vectorisation raster → chemins |
| Inkscape | 1.4.4 (`dcaf3e7`) | simplification de courbes (verbes CLI intégrés uniquement) |
| Python | 3.14.1 (stdlib seule) | mapping FMA, conversion DrawingML, assemblage, validation |
| Google Chrome (headless) | système | rendu SVG → PNG pour contrôle visuel et previews |

**Aucune extension Python Inkscape n'a été utilisée** — la restriction CVE-2025-15523 (extensions désactivées
en lancement CLI sur DMG macOS officiel) a été **testée** et reste **sans effet** sur ce pipeline.

## Conséquence contractuelle
La clause « géométrie générée non déclarée = livraison bloquée » ne trouve pas à s'appliquer : **aucune
géométrie générée n'existe dans ce livrable**.

## Verdict

**Verdict :** `AI_USAGE: NONE` — aucun usage d'IA, à aucune étape, sous aucune forme. Toute la géométrie
provient de sources ouvertes sous licence (BodyParts3D CC BY 4.0, Servier Medical Art CC BY 4.0),
transformée par des outils déterministes dont les versions et paramètres sont consignés.
