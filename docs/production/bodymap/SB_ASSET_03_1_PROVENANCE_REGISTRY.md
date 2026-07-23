# SB_ASSET_03.1 — Registre de provenance

**Cycle** : `Sx_ASSET_03` (amendé SOURCE-REUSE-FIRST) · **Build** : `Sb_ASSET_03.1` · **Date** : 2026-07-23

```
PROVENANCE: COMPLETE
PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED
ATTRIBUTION SURFACE: NOT YET IMPLEMENTED
```

---

## 1. Source primaire — BodyParts3D (CC BY 4.0)

### Revalidation de licence, le jour du téléchargement
| Champ | Valeur |
|---|---|
| URL officielle | `https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html` |
| Date d'accès | **2026-07-23** · HTTP **200**, TLS actif, **aucun miroir** |
| Licence | **Creative Commons Attribution 4.0 International** |
| Badge CC référencé | `i.creativecommons.org/l/by/4.0/88x31.png` — **by/4.0**, aucune mention `by-sa` |
| Mise à jour de la licence | **2025/02/27** |
| SHA-256 de la copie de page conservée | `50c62d791377653309bc19e6db74dc1987bdd9a18a1ce46f77a7264e53e0eac8` |

**Attribution obligatoire (verbatim, extraite de la page)** :
```
BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International
```

> Le miroir GitHub `Kevin-Mattheus-Moerman/BodyParts3D` affiche encore *CC BY-SA 2.1 Japan* : c'est un clone
> figé de 2011. **Il n'a pas été utilisé.** Le `README_e.html` du répertoire officiel `20110915` porte lui
> aussi l'ancienne licence — les artefacts d'archive anciens conservent l'ancienne mention ; seule `lic.html`
> fait foi.

### Artefacts téléchargés (source officielle DBCLS uniquement)
| Fichier | HTTP | Taille (o) | SHA-256 |
|---|---|---:|---|
| `isa_BP3D_4.0_obj_99.zip` | 200 | 142 903 898 | `40665852c49f218326590e204db91064a1ecfc3c6f8cbd7bbbcaac62c7cd409e` |
| `partof_BP3D_4.0_obj_99.zip` | 200 | 64 888 505 | `9fbc713fffeee924a5a657d9813d84d7eb957bded63adb854931dd5e3eb61c97` |
| `isa_parts_list_e.txt` | 200 | 128 086 | `ab7796deedd49205e77f3609a1cb8c53e2bbee14ecb5c9a6ca05227469780513` |
| `isa_element_parts.txt` | 200 | 1 142 159 | *(index de mapping opérant — cf. mapping FMA)* |
| `partof_element_parts.txt` | 200 | 651 179 | *(idem, hiérarchie PART-OF)* |

Base d'URL : `https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/`. Aucun CDN, aucun miroir, aucun pipe
vers shell, TLS jamais désactivé.

### Intégrité des archives
| Archive | Membres | Décompressé (o) | Traversées `../` | Symlinks | Types |
|---|---:|---:|---:|---:|---|
| IS-A | **2 234** | 479 605 380 | **0** | **0** | 100 % `.obj` |
| PART-OF | **1 258** | 217 566 293 | **0** | **0** | 100 % `.obj` |

### Package retenu
```
SELECTED BODYPARTS3D PACKAGE: ISA
```
**Justification factuelle** : l'archive **IS-A** contient 2 234 OBJ contre 1 258 pour PART-OF, et son index
(`isa_element_parts.txt`, 29 549 lignes / 2 905 concepts FMA / 2 234 element files) couvre **l'intégralité**
des 55 maillages requis — **0 manquant**. Aucun recours à PART-OF n'a été nécessaire ; **aucune géométrie
n'est combinée entre les deux hiérarchies**, ni entre deux releases. La release **3.0 n'a pas été
téléchargée** : la 4.0 s'est révélée matériellement suffisante.

## 2. Source complémentaire — Servier Medical Art (CC BY 4.0)

| Fichier | URL officielle | HTTP | Taille (o) | Content-Type |
|---|---|---|---:|---|
| `SMART-Muscles.pptx` | `smart.servier.com/wp-content/uploads/2016/10/SMART-Muscles.pptx` | 200 | 3 583 969 | `application/vnd.openxmlformats-officedocument.presentationml.presentation` |
| `Monsieur_muscles_dos.png` | `smart.servier.com/wp-content/uploads/2016/10/Monsieur_muscles_dos.png` | 200 | 291 332 | `image/png` |

**Licence** : **CC BY 4.0** — réutilisation, **modification** et **usage commercial** autorisés, attribution
obligatoire. **Attribution retenue** :
```
Image adapted from Servier Medical Art, licensed under CC BY 4.0
```

> `Monsieur_muscles_face.png` **n'existe pas** sous ce nom. La vue antérieure provient du **PPTX**, en
> **vectoriel** — strictement supérieur à un PNG.

### Verdict du conteneur OOXML
```
SERVIER PPTX CONTENT: EDITABLE VECTOR
```
La planche corporelle (slide 3 « Musculature ») est composée de **3 361 chemins `<a:custGeom>` natifs**,
**aucun raster**. Les 2 seuls fichiers EMF du classeur concernent la slide « Muscular contraction », sans
rapport. **La dérivation raster n'a donc pas été nécessaire** : la géométrie est reprise depuis les chemins
vectoriels d'origine, sans transformation destructrice.

## 3. Provenance composite du prototype

```
BODY BASE:
BodyParts3D — FMA7163 (skin) — CC BY 4.0

BODYPARTS3D-DERIVED ZONES:
pecs · delt_lat · delt_post · upper_back · biceps · triceps · quads · posterior · calves

SERVIER-DERIVED ZONES:
lats · core

SERVIER ATTRIBUTION:
Image adapted from Servier Medical Art, licensed under CC BY 4.0

BODYPARTS3D ATTRIBUTION:
BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International

AUREN CONTRIBUTION:
mapping fonctionnel FMA → 11 zones, alignement, simplification, vectorisation,
structure SVG (14 IDs stables), regroupement en onze zones et style produit.

ATTRIBUTION SURFACE:
NOT YET IMPLEMENTED
```

**Ce qu'Auren possède** : sa contribution créative (mapping, simplification, structure, style).
**Ce qu'Auren ne possède pas** : les données anatomiques sous-jacentes. Écrire « Auren owns the master »
sans qualification serait **faux**. L'attribution CC BY est **perpétuelle** et ne s'éteint pas avec la
stylisation.

## 4. Absence de contamination

```
LICENSE CONTAMINATION: NONE
```
| Source écartée | Licence | Statut dans le livrable |
|---|---|---|
| Wikimedia `Muscles front and back.svg` | CC BY-SA 4.0 | **jamais téléchargée dans l'espace de production** |
| Z-Anatomy | CC BY-SA 4.0 + composant NC | **jamais téléchargée** |
| OpenStax **2e** | CC BY-NC-SA 4.0 | **exclue** |

Seules **deux sources CC BY 4.0** ont fourni de la géométrie. OpenStax **1ʳᵉ édition** (CC BY 4.0) et
**Sobotta 1909** (domaine public) ont servi de **contrôle documentaire uniquement** — aucune géométrie
importée.

## 5. Artefacts produits

| Artefact | Taille (o) | SHA-256 |
|---|---:|---|
| `auren_bodymap_master_proto.svg` | **59 620** | `dbb57db333863434442b476277170017db442d83e2eced6e7191266ee9ecfa73` |
| `auren_bodymap_compact.svg` | **8 615** | `8024fd4ced62ca2010808bf85f94c3eaca4d334dde2b7c3b7683c3e5a4676c9a` |
| `auren_bodymap_sb_asset_03_1_intake_package.zip` | **14 495 063** | `098d1b4276d79b771a3ccd97307811160812485dcbe610513d682568678738b1` |

**Aucun de ces fichiers n'est committé.** Ils résident dans l'espace externe, hors de tout dépôt Git.

## Verdict

**Verdict :** **PROVENANCE COMPLÈTE ET VÉRIFIABLE.** Licence BodyParts3D **revalidée le jour du
téléchargement** sur la page officielle (**CC BY 4.0**, maj 2025/02/27, attribution verbatim, page hachée),
trois artefacts téléchargés depuis la **seule** archive DBCLS avec **SHA-256** et tailles conformes, archives
**auditées saines** (0 traversée, 0 symlink). Package **IS-A retenu et justifié** ; aucune combinaison entre
hiérarchies ou releases ; release 3.0 non téléchargée car inutile. Servier acquis depuis la source officielle,
**verdict `EDITABLE VECTOR`** rendant la dérivation raster superflue. Provenance **composite explicite** :
base et 9 zones BodyParts3D, 2 zones Servier, contribution Auren distincte des données amont. **Zéro
contamination** ShareAlike ou NC. `ATTRIBUTION SURFACE: NOT YET IMPLEMENTED` reste une dette ouverte ;
`PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED`.
