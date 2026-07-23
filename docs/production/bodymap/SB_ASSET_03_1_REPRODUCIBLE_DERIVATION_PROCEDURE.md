# SB_ASSET_03.1 — Procédure de dérivation reproductible

> ```
> PACKAGE V1: HISTORICAL / SUPERSEDED
> CURRENT PACKAGE: V2 — see SB_ASSET_03_1_REPRODUCIBILITY_CLOSURE.md
> ```
> La procédure d'origine décrite ici comportait une **étape ad hoc non scriptée** (sélection des régions
> Servier), corrigée par `Sb_ASSET_03.1-fix` : producteur `extract_servier_regions.py`, scripts
> **relocalisés**, graphe de build explicite, entrypoint `run_pipeline.py`. Le pipeline courant est
> **rejouable de bout en bout depuis un workspace vide** (package v2 `f45e0dbf…`), ce qui a été **vérifié
> indépendamment** à l'intake `Sb_ASSET_03.2`.

**Cycle** : `Sx_ASSET_03` (amendé SOURCE-REUSE-FIRST) · **Build** : `Sb_ASSET_03.1` · **Date** : 2026-07-23

> Tous les artefacts binaires (archives, OBJ, `.blend`, BMP, PNG, SVG) vivent **hors Git**, dans
> `EXTERNAL_ROOT`. Ce document décrit la procédure ; il ne contient aucun artefact.

---

## 1. Outillage (versions relevées à l'exécution)

| Outil | Version | Rôle |
|---|---|---|
| macOS | 15.6 (24G84) · Darwin 24.6.0 · **arm64** | plateforme |
| Blender | **5.2.0 LTS** — hash `fbe6228777e7`, build 2026-07-14 | import OBJ, BMesh, caméras, rendus |
| Potrace | **1.16** | vectorisation raster → chemins |
| Inkscape | **1.4.4** (`dcaf3e7`, 2026-05-05) | simplification de courbes |
| Python | **3.14.1** — **stdlib seule** | mapping, conversion, assemblage, validation |
| Google Chrome headless | système | rendu SVG → PNG (contrôle et previews) |

**Aucune extension Inkscape n'est utilisée** : uniquement les **verbes CLI intégrés**
(`select-all`, `path-simplify`, `export-plain-svg`, `export-do`), testés fonctionnels. La restriction
CVE-2025-15523 (extensions Python désactivées en lancement CLI sur DMG macOS officiel) est donc **sans effet**
sur cette procédure. **Aucune dépendance applicative n'a été ajoutée au dépôt.**

## 2. Chaîne complète

```
Archives officielles DBCLS (CC BY 4.0)
   └─ extraction bornée des 55 maillages mappés  ............ extract_selected_meshes.py
        └─ inspection topologique (BMesh + BVH)  ............ inspect_topology.py
             └─ scène Blender + caméras orthographiques  .... build_scene_and_render.py
                  └─ 13 rendus BMP monochromes
                       └─ vectorisation Potrace  ............ vectorize_and_assemble.py
                            └─ mise au contrat (14 IDs)
                                 └─ validation + compact  ... validate_and_compact.py
                                      └─ 32 previews  ....... build_previews.py
                                           └─ package  ...... build_intake_package.py

Planche Servier (CC BY 4.0, DrawingML vectoriel)
   └─ conversion DrawingML → SVG  ..................... pptx_drawingml_to_svg.py
        └─ isolement des régions lats / core  ......... svg_shape_analysis.py
             └─ masque monochrome + fermeture  ........ servier_masks.py
                  └─ Potrace → alignement uniforme  ... vectorize_and_assemble.py
```

## 3. Scène Blender

**Système de coordonnées constaté** (mesuré sur les maillages, non supposé) :
**X** = gauche/droite (**+X = gauche du sujet**) · **Y** = vertical (**−Y = tête**, **+Y = pieds**) ·
**Z** = profondeur (**−Z = antérieur**, **+Z = postérieur**).
Bounding box du corps : **666,94 × 1 719,47 × 292,03** unités.

**Deux caméras orthographiques**, même échelle et même centre vertical :

| Paramètre | Valeur |
|---|---|
| Type | `ORTHO` |
| `ortho_scale` | **1 800** (> hauteur corps 1 719,47 → marge) |
| Résolution | **1 000 × 2 000 px** (identique pour tous les rendus) |
| Distance caméra | 4 000 unités du centre |
| **Clipping** | `clip_start = 1,0` · `clip_end = 8 000` |
| Caméra *front* | position `z = centre_z − 4000`, `rotation_euler = (π, 0, 0)` → regarde vers **+Z** |
| Caméra *back* | position `z = centre_z + 4000`, `rotation_euler = (0, 0, π)` → regarde vers **−Z** |

> **Piège rencontré et corrigé** : les plans de clipping par défaut de Blender (0,1 / 100) placent un corps de
> ~1 700 unités **hors du volume de vue** — les premiers rendus étaient vides. Sans ce réglage explicite, la
> procédure n'est pas reproductible.

**Rendu** : moteur **Workbench**, éclairage `FLAT`, couleur `SINGLE` **noir**, fond clair, ni ombre, ni
cavité, ni contour, ni spéculaire. Objectif : **silhouette d'occupation**, jamais une image anatomique.
Aucun matériau, aucune texture, aucune lumière, aucun gradient.

**13 rendus** : 2 bases (face, dos) + 11 rendus de zones selon les vues contractuelles.

## 4. Vectorisation

| Passe | Paramètres Potrace |
|---|---|
| **Master** | `-s --turdsize 40 --alphamax 1.0 --opttolerance 0.6 --turnpolicy majority` |
| **Compact** | `-s --turdsize 400 --alphamax 1.334 --opttolerance 5.0 --turnpolicy majority` |
| **Masques Servier** | `-s --turdsize 120 --alphamax 1.334 --opttolerance 3.0 --turnpolicy majority` |

Potrace émet `translate(0,H) scale(0.1,−0.1)` avec des commandes **relatives** ; l'assembleur applique
l'affine et convertit en coordonnées **absolues** avant mise au contrat.

## 5. Mise au contrat

```
cadre de rendu 1000×2000 px  →  vue contractuelle
contract_x = centre_vue − 45 + (px / 1000) × 90        centre face = 60 · centre dos = 180
contract_y = 12 + (py / 2000) × 176
```

Résultat : face **x ∈ [15, 105]** ⊂ [10, 110] · dos **x ∈ [135, 225]** ⊂ [130, 230] · **gouttière
[110, 130] vide** · vues dans **y ∈ [12, 188]** ⊂ [10, 190].

> La plage verticale est volontairement resserrée à `[12, 188]` : la simplification de courbes peut déplacer
> un point de contrôle d'environ une unité, et la **safe area ≥ 8 doit tenir APRÈS simplification**.

**Latéralité** : côté du sujet déduit de la position relative au centre de vue, en tenant compte du sens de
chaque caméra (face : `px > centre` = gauche du sujet ; dos : `px < centre` = gauche du sujet).

## 6. Zones Servier — masque et alignement

1. **Conversion DrawingML → SVG** (script stdlib) : `custGeom` (`moveTo`/`lnTo`/`cubicBezTo`/`close`),
   transformations de forme (`a:off`/`a:ext`, mise à l'échelle `path@w/h`) et de **groupe**
   (`a:chOff`/`a:chExt`). **3 361 chemins** convertis pour la planche *Musculature*.
2. **Isolement par région** puis **vérification visuelle en navigateur réel** (surlignage + rendu), avec
   itérations correctives consignées.
3. **Masque monochrome** : aplat noir + **contour de fermeture `stroke-width = 6,0`** (unités Servier) qui
   soude les stries fibrillaires en une **emprise pleine**. C'est l'étape qui supprime le détail fibrillaire
   exigée par la décision opérateur. *(Une valeur de 2,5 laissait subsister des hachures — corrigé.)*
4. **Vectorisation Potrace** du masque → **1 chemin par zone**.
5. **Alignement** sur la base BodyParts3D : **échelle UNIFORME + translation**, calculée par ajustement de la
   bounding box source sur une bounding box cible exprimée en **fractions de la base** :

| Zone | Cible (fractions de la bbox de la base) |
|---|---|
| `lats` | x ∈ [0,22 · 0,78] · y ∈ [0,30 · 0,52] de la base **dos** |
| `core` | x ∈ [0,33 · 0,67] · y ∈ [0,30 · 0,53] de la base **face** |

**Aucun étirement indépendant X/Y**, aucune rotation, aucune déformation locale, aucun ajustement « à
l'œil » : la transformation est **un scalaire et deux translations**, consignés dans
`assembly_report_master.json`.

## 7. Simplification et budget

Le master est structuré (budget indicatif). L'export compact subit **`path-simplify` d'Inkscape en passes
successives** jusqu'à passer sous **12 Ko**, la structure des groupes et les 14 IDs restant intacts.

> **La séparation des zones n'a jamais été dégradée pour gagner des octets** : `path-simplify` n'agit que sur
> la densité de points. Aucune fusion de zones, aucun path partagé.

## 8. Rejouabilité

Tous les scripts sont dans le package d'intake (`procedure/scripts/`) et n'utilisent que la **stdlib**
Python. En repartant des archives officielles (hashes au registre de provenance) et des versions d'outils
ci-dessus, la chaîne est **rejouable de bout en bout**.

**Limite honnête** : Potrace et `path-simplify` sont déterministes à paramètres et entrée constants, mais un
changement de version d'outil peut modifier les chemins produits. Les versions exactes sont donc **partie
intégrante** de la procédure.

## Verdict

**Verdict :** **PROCÉDURE REPRODUCTIBLE ÉTABLIE.** Chaîne complète documentée de l'archive officielle au SVG
contractuel : extraction bornée (55 maillages), inspection topologique, scène Blender paramétrée (caméras
orthographiques, `ortho_scale` 1 800, clipping explicite), 13 rendus monochromes, vectorisation Potrace
paramétrée, mise au contrat par formules explicites, alignement Servier par **transformation uniforme**
chiffrée, simplification Inkscape par **verbes intégrés** et budget compact tenu. Versions d'outils relevées ;
scripts stdlib livrés dans le package ; **aucune dépendance applicative ajoutée** ; **aucune extension
Inkscape** ; `AI_USAGE: NONE`.
