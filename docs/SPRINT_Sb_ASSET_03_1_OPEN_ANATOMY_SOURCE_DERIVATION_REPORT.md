# Sprint Sb_ASSET_03.1 — Open Anatomy Source Acquisition & BodyMap Derivation Prototype — REPORT

**Statut** : 🟢 **BUILD COMPLETE / MIXED-SOURCE PROTOTYPE READY FOR TECHNICAL INTAKE**
**Type** : BUILD DE PRODUCTION EXTERNE — **DOCS-ONLY côté Git** (0 SVG/image/archive/OBJ/`.blend` committé)
**Date** : 2026-07-23 · **Baseline** : `cd4aeb3` (= origin, vérifié)

---

## 1. Historique du blocage — conservé

```
INITIAL BUILD ATTEMPT:
BLOCKED — INCOMPLETE FMA MAPPING

ROOT CAUSES:
- incorrect source-index assumption in spec;
- latissimus dorsi absent from inspected BodyParts3D 4.0 mappings;
- rectus abdominis absent from inspected BodyParts3D 4.0 mappings.

OPERATOR DECISION:
SUPPLEMENTAL SERVIER DERIVATION AUTHORIZED

RESUMED BUILD:
COMPLETE — 11/11 zones, contrat tenu, budget compact tenu
```

Un premier essai s'était en outre arrêté à `BLOCKED — REQUIRED VECTOR TOOLING UNAVAILABLE` (Blender,
Inkscape et Potrace absents). Ces deux arrêts sont **conservés** : ils font partie de l'histoire du build.

## 2. Outillage

| Outil | Version | Rôle |
|---|---|---|
| Blender | **5.2.0 LTS** (`fbe6228777e7`) | import OBJ, BMesh, caméras orthographiques, rendus |
| Potrace | **1.16** | vectorisation |
| Inkscape | **1.4.4** (`dcaf3e7`) | simplification de courbes |
| Python | **3.14.1** stdlib seule | mapping, conversion, assemblage, validation |

**Pipeline exclusivement fondé sur des verbes CLI intégrés, testés.** Aucune extension Inkscape — la
restriction **CVE-2025-15523** a été **éprouvée** et reste sans effet. Aucune dépendance applicative ajoutée.
`AI_USAGE: NONE`.

L'installation d'Inkscape a été débloquée en constatant que le `.dmg` de `~/Downloads` était un **alias
Finder de 748 octets**, pas une image disque ; l'outil a été installé depuis le **DMG officiel signé** via
Homebrew cask.

## 3. Acquisition & intégrité

Licence BodyParts3D **revalidée le jour du téléchargement** : **CC BY 4.0 International**, maj **2025/02/27**,
attribution verbatim conforme, page hachée `50c62d79…`. Trois artefacts téléchargés depuis la **seule**
archive officielle DBCLS, avec SHA-256 et tailles conformes aux `Content-Length`.

Archives **saines** : IS-A **2 234 OBJ**, PART-OF **1 258 OBJ**, **0 traversée `../`**, **0 symlink**,
100 % `.obj`.

```
SELECTED BODYPARTS3D PACKAGE: ISA
```
justifié par la couverture intégrale des 55 maillages requis (0 manquant) ; **aucune combinaison** entre
hiérarchies ni entre releases ; la **3.0 n'a pas été téléchargée** (4.0 matériellement suffisante).

## 4. Correction du modèle d'identifiants

La spec désignait `isa_parts_list_e.txt` comme index de mapping. **Vérifié sur les données : faux.** Ses
2 905 ids sont des `BP####`, les OBJ des `FJ####`, **recouvrement 0**. Le fichier opérant est
**`isa_element_parts.txt`** (`FMA → nom → FJ`, **29 549 lignes**, 2 905 concepts, **2 234 element files** =
exactement le compte de l'archive IS-A), identifié via le listing officiel de `LATEST/`.

**Aucune correspondance `BP → FJ` n'a été fabriquée** — elle n'existe pas ; le mapping passe par le concept
FMA.

## 5. Mapping & extraction

**55 maillages** extraits (54 musculaires + `FMA7163 skin`), **0 manquant**, **0 FMA ID inventé**.
Vaste intermédiaire **délibérément exclu** (muscle profond invisible en silhouette). Aucune structure
profonde, aucun organe, aucun squelette.

## 6. Inspection topologique — sur les maillages retenus uniquement

| Métrique | Valeur (55 maillages) |
|---|---:|
| Sommets / faces | 240 971 / 404 370 |
| **Arêtes non-manifold** | **0** |
| **Faces dégénérées** | **0** |
| Arêtes de bord | 70 970 (surfaces ouvertes) |
| **Paires en intersection** | **112** (BVH, paires réellement superposées) |

```
SPECIFIC MESH DEFECTS: VERIFIED ON SELECTED MESHES
- non-manifold edges: NOT OBSERVED (0/55)
- degenerate faces: NOT OBSERVED
- skin/muscle intersections: OBSERVED (112 paires, dont peau × mollets, deltoïde, pecs, biceps)
- open boundaries / multiple shells: OBSERVED (peau : 1 512 arêtes de bord, 100 composantes)
```

**Ce résultat qualifie l'observation tierce** qui avait motivé la prudence initiale : les **intersections
peau/muscle sont confirmées**, mais l'allégation de **triangles non-manifold sur `FMA7163` n'est PAS
reproduite** sur la release 4.0 officielle. **Aucune généralisation au dataset entier n'est faite.**

## 7. Zones Servier

```
SERVIER PPTX CONTENT: EDITABLE VECTOR
```
La planche « Musculature » compte **3 361 chemins `<a:custGeom>` natifs** — aucun raster. La dérivation
raster autorisée **n'a donc pas été nécessaire** : la géométrie vient des chemins vectoriels d'origine.

Un convertisseur **DrawingML → SVG stdlib** a été écrit pour ce build (transformations de forme et de groupe).
Les régions `lats` et `core` ont été isolées, **vérifiées visuellement en navigateur réel**, réduites en
**masque monochrome** avec fermeture morphologique (`stroke-width 6,0`) supprimant le détail fibrillaire, puis
vectorisées → **1 chemin par zone**.

**Alignement par transformation UNIFORME** (aucun étirement indépendant X/Y, aucune rotation, aucun
ajustement « à l'œil ») :

| Zone | Échelle uniforme | Offset (x, y) |
|---|---:|---|
| `lats` | **0,045860** | (161,6537 · 66,5028) |
| `core` | **0,042889** | (42,8427 · 68,5874) |

## 8. Assemblage & validation

| Artefact | Taille | Contrôles | SHA-256 |
|---|---:|---|---|
| `auren_bodymap_master_proto.svg` | 59 620 o | **40/40** | `dbb57db3…` |
| `auren_bodymap_compact.svg` | **8 615 o** ≤ 12 288 | **41/41** | `8024fd4c…` |

Vérifiés : XML valide · root SVG · **viewBox `0 0 240 200` exact** · **14 IDs présents une seule fois** ·
**11 groupes de zones** · **0 `zone-unknown`** · 0 ID dupliqué · **0 path partagé entre groupes** · aucune
balise interdite · aucun `on*` · aucune URL externe · aucun raster · aucun texte/police/filtre/gradient ·
**gouttière [110,130] vide** · bornes viewBox · **safe area ≥ 8** · budget compact.

> **La séparation des zones n'a jamais été dégradée pour gagner des octets** : la réduction vient de
> `path-simplify`, qui n'agit que sur la densité de points.

**Trois bugs de mon propre validateur** ont été trouvés et corrigés en cours de route : double comptage de
l'id racine ; regex `d="` capturant aussi `id="` (les identifiants étaient lus comme des coordonnées) ; et
extrema calculés sur des commandes **relatives** émises par Inkscape comme si elles étaient absolues.

## 9. Revue multi-sources

```
MULTI-SOURCE ANATOMICAL CONSISTENCY REVIEW: COMPLETE — NOT A PROFESSIONAL ANATOMICAL REVIEW
PROFESSIONAL ANATOMICAL REVIEW: NOT CLAIMED
```
**11 PASS · 0 ADJUST · 0 BLOCKED**, contre **OpenStax 1ʳᵉ éd. (CC BY 4.0)** et **Sobotta 1909 (domaine
public)** — deux sources indépendantes entre elles, de BodyParts3D et de Servier. OpenStax 2e (NC), Wikimedia
(dérivé d'OpenStax) et Z-Anatomy (dérivé de BodyParts3D) **exclus** des contrôles.

## 10. Previews & package

**32 previews** exactement, selon la matrice bornée. Les six cas `primary + secondary` ont été choisis par
**Martin Feldmann (responsable produit)** : pecs+delt_lat · lats+upper_back · biceps+triceps ·
quads+posterior · core+pecs · calves+quads.

Package : `auren_bodymap_sb_asset_03_1_intake_package.zip`, **14 495 063 o**, **60 entrées hachées**,
SHA-256 `098d1b4276d79b771a3ccd97307811160812485dcbe610513d682568678738b1`.

## 11. Scope Git

**12 fichiers, 100 % `docs/**`.** **0** SVG/image/archive/OBJ/`.blend`/BMP committé · **0** `app/**` ·
**0** `tests/**` · **0** `design/**` · **0** `data/**` · **0** `migrations/**` · **0** `scripts/**` ·
**0** `.github/**` · **0** dépendance · **0** fichier Custom. Contrat sémantique BodyMap **inchangé**.

---

## Verdict

**Verdict :** 🟢 **Sb_ASSET_03.1: BUILD COMPLETE / MIXED-SOURCE PROTOTYPE READY FOR TECHNICAL INTAKE.**
Le prototype BodyMap est **réellement produit**, hors Git, à partir de **deux sources CC BY 4.0** : base et
9 zones dérivées de **BodyParts3D 4.0** (55 maillages mappés par FMA ID officiel, 0 inventé, 0 manquant),
`lats` et `core` dérivées de **Servier Medical Art** dont le PPTX s'est révélé **`EDITABLE VECTOR`**, alignées
par **transformation uniforme chiffrée**. Le contrat est tenu au sens strict : **viewBox `0 0 240 200`**,
**14 IDs stables uniques**, **11 groupes**, **0 `zone-unknown`**, **0 path partagé**, gouttière vide, safe
area ≥ 8 — **master 40/40** et **compact 41/41 à 8 615 o** sous le budget bloquant de 12 Ko. Inspection
topologique menée **sur les seuls maillages utilisés** : **0 arête non-manifold**, **0 face dégénérée**,
**112 paires en intersection** — ce qui **confirme** les intersections peau/muscle et **ne reproduit pas**
l'allégation de non-manifold sur `FMA7163`, **sans généraliser au dataset**. Revue de cohérence multi-sources
**11 PASS / 0 BLOCKED** contre deux sources indépendantes ; **revue professionnelle NON revendiquée**.
**32 previews** produites, package d'intake **hashé**. **Zéro contamination** ShareAlike ou NC.
`AI_USAGE: NONE`. **Aucun binaire committé** ; le master **n'est pas approuvé** et **rien n'est intégré**.
`BODYMAP MASTER: NOT YET APPROVED` · `ATTRIBUTION SURFACE: NOT YET IMPLEMENTED` ·
`ASSET INTEGRATION GATE: BLOCKED`.

**Prochaine action** (séparée, non commencée) : `GO INTAKE — Sb_ASSET_03.2 BodyMap Prototype Technical
Validation`.
