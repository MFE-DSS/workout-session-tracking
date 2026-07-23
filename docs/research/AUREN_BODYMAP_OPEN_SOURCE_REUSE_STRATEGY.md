# AUREN — BodyMap Open-Source Reuse Strategy (`Sx_ASSET_03` amendement)

**Type** : recherche source-officielle + stratégie d'acquisition — **DOCS-ONLY** (0 archive téléchargée, 0 image
importée, 0 SVG produit)
**Date d'accès** : **2026-07-23** (relevés effectués à cette date sur les pages officielles des projets)
**Portée** : établir la **hiérarchie de sources** pour une production **SOURCE-REUSE-FIRST** du master BodyMap.
**NON une conclusion juridique.** Établit `OFFICIAL LICENSE EVIDENCE RECORDED AT ACCESS DATE`, jamais
`LEGAL CLEARANCE COMPLETE`. `PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED`.

> **Changement de doctrine.** `Sx_ASSET_03` prévoyait un **master original commandé à un illustrateur**. La
> décision opérateur du 2026-07-23 retient une **dérivation depuis des ressources anatomiques ouvertes,
> créées par des humains, traçables et compatibles commercial**. Ce document remplace la hiérarchie de
> références de la due diligence initiale — il **ne modifie pas** le contrat sémantique BodyMap (immuable).

---

## 1. Correction majeure — BodyParts3D n'est PAS sous CC BY-SA

La due diligence du **2026-07-22** enregistrait BodyParts3D en **CC BY-SA 2.1 Japan** et en concluait que
**toute dérivation était écartée** (copyleft incompatible avec un master propriétaire). **Cette conclusion
était fondée sur une source périmée.**

| | Source consultée | Licence relevée | Statut |
|---|---|---|---|
| **2026-07-22** | miroir GitHub `Kevin-Mattheus-Moerman/BodyParts3D` (`LICENSE_content`, `README.md`) | CC BY-SA 2.1 Japan | ❌ **copie ancienne** — clone figé de la version `3.0` / `20110915` |
| **2026-07-23** | **page de licence officielle DBCLS** `dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html` | **CC BY 4.0 International** | ✅ **officielle et courante — mise à jour 2025-02-27** |

**Le miroir GitHub reproduit la licence telle qu'elle était en 2011.** DBCLS a **relicencié** la base en
**CC BY 4.0 International** ; la page officielle porte la date de mise à jour **2025-02-27**. Le miroir n'est
pas malhonnête — il est simplement **antérieur au changement** et n'a pas été resynchronisé.

### Conséquence directe
```
CC BY 4.0 = PAS de clause ShareAlike.
La DÉRIVATION de BodyParts3D vers un master Auren propriétaire redevient LICITE,
sous réserve d'ATTRIBUTION obligatoire et irrévocable.
```
Le verdict « dérivation écartée » de la due diligence initiale est **annulé** et remplacé par
**`DERIVATION PERMITTED — ATTRIBUTION MANDATORY`**.

### Nuance à ne jamais gommer
CC BY 4.0 autorise la dérivation commerciale, **pas** l'effacement de l'origine :
- l'attribution est **perpétuelle** et doit survivre dans le produit et/ou sa documentation ;
- Auren possède **sa propre contribution créative** (simplification, stylisation, regroupement en 11 zones),
  **pas** les données anatomiques sous-jacentes ;
- écrire « **Auren owns the master** » sans qualification resterait **faux**. Formulation honnête :
  *« master Auren, œuvre dérivée de BodyParts3D (CC BY 4.0), attribution DBCLS conservée »*.

### Règle opérationnelle qui en découle
```
TÉLÉCHARGER UNIQUEMENT DEPUIS L'ARCHIVE OFFICIELLE DBCLS.
Ne jamais acquérir les données via le miroir GitHub ni via un tiers :
la licence applicable est celle de la source dont on obtient effectivement la copie.
```

## 2. BodyParts3D — relevé officiel (2026-07-23)

| Champ | Valeur relevée |
|---|---|
| Projet | **BodyParts3D / Anatomography** |
| Organisation | **Database Center for Life Science (DBCLS)** |
| Page de licence (**opérante**) | `https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html` |
| **Licence** | **Creative Commons Attribution 4.0 International (CC BY 4.0)** |
| SPDX | `CC-BY-4.0` |
| **Mise à jour de la licence** | **2025-02-27** |
| **Attribution exacte requise** | *« BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International »* |
| Release courante | **4.0** (répertoire `LATEST`) |
| Archives OBJ officielles | `isa_BP3D_4.0_obj_99.zip` (**136 Mo**, arbre IS-A) · `partof_BP3D_4.0_obj_99.zip` (**62 Mo**, arbre PART-OF) |
| URL des archives | `https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/<archive>` |
| Index modèles ↔ organes | `isa_parts_list_e.txt` (126 Ko, **2 905 entrées**) |
| Format | **OBJ** (maillages polygonaux, réduction 99 %) |
| Sujet | **un** homme adulte de référence (spécimen unique) |

### Avertissements de qualité

#### A. Avertissement upstream OFFICIEL (source primaire, vérifié)
**Éditeur** : projet BodyParts3D / Anatomography (DBCLS) · **Page** : `http://lifesciencedb.jp/bp3d/info/`
(section *Notice*) · **Date d'accès** : **2026-07-23**. **Citation verbatim** :

> *« There are still many concepts not represented in the data. There could be many ERRORS to be used as
> ANATOMICAL EDUCATION. Some parts were made from scratch by artists or distorted to fit into the
> environment. »*

Compléments officiels relevés à la même date :
> *« Segmentation into finer pieces may cause confusion in assignment of concepts. »* — et, sur la combinaison
> de versions, les systèmes de coordonnées pouvant différer : *« you can combine them at your own risk »*.

```
UPSTREAM QUALITY WARNING:
BodyParts3D declares that the data may contain many errors for anatomical-education use,
that many concepts are still not represented, and that some parts were authored by artists
or distorted to fit the environment. The dataset is not presented as a canonical, complete
model of human anatomy.
```

**Conséquences retenues** :
- le dataset **n'est pas une vérité anatomique** : il ne dispense **pas** du croisement multi-sources ;
- **certaines parties sont d'origine artistique ou déformées** — ce qui renforce l'exigence de contrôle 2D
  (Servier) et de croisement (AnatomyTOOL / OpenStax 1ʳᵉ éd.) ;
- **ne jamais combiner des versions différentes** sans vérifier les systèmes de coordonnées.

#### B. Défauts de maillage SPÉCIFIQUES — **non vérifiés**
Les observations « interpénétrations peau/muscle en release 4.0 » et « triangles non-manifold du modèle de
peau `FMA7163` » proviennent du **README d'un dépôt tiers** (miroir `Kevin-Mattheus-Moerman`), **pas** d'une
déclaration de l'éditeur. Elles n'ont **pas** été vérifiées sur les archives officielles, qui n'ont pas été
téléchargées. Aucune page officielle consultée (`lic.html`, `desc.html`, `download.html`,
`README_e.html` des répertoires `20110915` et `LATEST`) ne les mentionne.

```
SPECIFIC MESH DEFECTS:
NOT YET VERIFIED

BUILD INSPECTION CHECKS:
- inspect potential skin/muscle intersections;
- inspect manifoldness of meshes used by the prototype;
- record affected representation IDs;
- do not generalize a defect to the entire dataset.
```

**Statut de l'observation tierce** : *piste d'inspection*, à confirmer ou infirmer sur les fichiers réels —
**jamais** à citer comme fait officiel. Elle ne justifie pas à elle seule d'écarter la release 4.0.

#### C. Précisions de version relevées (officiel, 2026-07-23)
- Release courante **4.0**, données datées **2013/06/19** ; la **licence** a été mise à jour **2025-02-27**
  (le changement de licence est postérieur aux données, il ne les modifie pas).
- La page descriptive `desc.html` n'affiche que « CC BY » **sans version**, dernière mise à jour **2013/05** :
  **c'est `lic.html` qui fait foi**.
- Le `README_e.html` du répertoire `20110915` porte encore **CC BY-SA 2.1 Japan** — cohérent avec l'origine de
  l'erreur du 2026-07-22 : **les artefacts d'archive anciens conservent l'ancienne licence**.
- **Conséquence build** : `Sb_ASSET_03.1` **compare réellement** les archives disponibles (IS-A / PART-OF,
  et le cas échéant 4.0 vs 3.0) et **documente** son choix — sans présumer que « LATEST = meilleure », ni
  qu'une release est défectueuse sur la foi d'un tiers.

## 3. Servier Medical Art — contrôle 2D

| Champ | Valeur relevée (2026-07-23) |
|---|---|
| Source officielle | `https://smart.servier.com/` |
| Éditeur | Les Laboratoires Servier |
| **Licence** | **CC BY 4.0** (`SPDX: CC-BY-4.0`) |
| Catégorie utile | *Anatomy and the Human Body → Locomotor system → Muscles* — **59 illustrations** |
| Planches pertinentes | *Superficial muscles anterior view — no labels* · *Superficial muscles posterior view — no labels* · `musculature-back` (fichier `Monsieur_muscles_dos`) |
| Formats | **PNG individuel** par illustration · **pack PowerPoint** par catégorie (`SMART-Muscles.pptx`) |
| Attribution affichée | *« A service to medicine provided by Les Laboratoires Servier »* (`www.servier.com`) |

**À déterminer au build, pas maintenant** : le pack `.pptx` contient-il des **objets vectoriels éditables**
(formes PowerPoint exportables en EMF/SVG) ou seulement des **rasters encapsulés** ? Cette question décide si
Servier peut servir de **contrôle 2D vectoriel** ou seulement de **référence visuelle raster**. Un `.pptx`
est un conteneur OOXML : la réponse s'obtient en inspectant `ppt/media/` et `ppt/slides/` — **au build**.

## 4. AnatomyTOOL — croisement anatomique, ressource par ressource

| Champ | Valeur relevée (2026-07-23) |
|---|---|
| Source officielle | `https://anatomytool.org` |
| **Modèle de licence** | **PAR RESSOURCE** — **aucune licence globale de plateforme** |
| Licences observées | CC BY, CC BY-SA, CC BY-NC-SA, domaine public, ressources étudiantes restreintes |
| Contenu étudiant | **temporaire** — supprimé après 16 mois sauf licence CC/domaine public explicite |
| Rôle retenu | **croisement anatomique** (vérification de plausibilité), incorporation seulement si CC0/CC BY |

```
La licence d'AnatomyTOOL n'est JAMAIS généralisée au catalogue.
Chaque ressource envisagée est qualifiée individuellement :
auteur · licence CC exacte · date · incorporable ou non · rôle.
```

## 5. OpenStax — deux éditions, deux licences (ne jamais confondre)

| Édition | Licence relevée | Dates | Usage Auren |
|---|---|---|---|
| **Anatomy and Physiology** (1ʳᵉ éd.) | **CC BY 4.0 International** | publiée 2013-04-25, révisée 2022-01-27 | ✅ **croisement anatomique autorisé**, incorporation possible avec attribution |
| **Anatomy and Physiology 2e** | **CC BY-NC-SA 4.0** | publiée 2022-04-20, révisée 2026-04-23 | ❌ **NC → exclue** de tout produit commercial |

Citation officielle 1ʳᵉ édition : *« Anatomy and Physiology is licensed under a Creative Commons Attribution
4.0 International (CC BY) license »*. Citation officielle 2e : *« Textbook content produced by OpenStax is
licensed under a Creative Commons Attribution-NonCommercial-ShareAlike License »*.

> **Piège actif** : la 2e est la version **mise en avant** sur openstax.org et la plus facile à trouver. Un
> croisement fait « sur OpenStax » sans préciser l'édition **contamine** le produit avec une clause NC.
> **Toute référence OpenStax doit porter l'édition et la licence.**

## 6. Wikimedia — `Muscles front and back.svg`

| Champ | Valeur relevée (2026-07-23) |
|---|---|
| Fichier | `File:Muscles_front_and_back.svg` (Wikimedia Commons) |
| **Licence** | **CC BY-SA 4.0** |
| Auteurs | **OpenStax** (original) + **Tomáš Kebert & umimeto.org** (redessin/modification) |
| Lignage | dérivé de `File:1105_Anterior_and_Posterior_Views_of_Muscles.jpg`, **redessiné manuellement** (surtout la vue dos) |
| Date | 2020-09-13 |
| Format | **SVG à chemins vectoriels éditables** — face **et** dos dans un seul fichier |

**Attrait** : c'est exactement la topologie visée (face+dos, vectoriel, propre) — le chemin le plus court vers
un prototype affichable.
**Blocage** : **ShareAlike**. Si cette géométrie entre dans le master livré, le master devient une œuvre
dérivée **CC BY-SA 4.0** — incompatible avec un asset propriétaire.
**Double lignage** : dérivé d'OpenStax, donc à ne pas traiter comme une source indépendante lors des
croisements (ce n'est pas un second avis, c'est le même).

```
STATUT : PROTOTYPE JETABLE UNIQUEMENT.
Autorisé pour valider la faisabilité (11 zones, viewBox, IDs, lisibilité 60/80/120/360).
INTERDIT dans le master livré. Un prototype BY-SA ne se « nettoie » pas en le retouchant.
```

## 7. Z-Anatomy — référence seulement

| Champ | Valeur relevée (2026-07-23) |
|---|---|
| Projet | **Z-Anatomy** (atlas 3D open source, template Blender) |
| **Licence** | **CC BY-SA 4.0** |
| Sources dérivées déclarées | **BodyParts3D** (attribué *CC BY-SA 2.1 Japan* — **licence périmée**, cf. §1) · Wikipédia (définitions) · *Cranial Nerves and Foramina*, Univ. Dundee CAHID (**CC BY 4.0**) · *Anatomy of the Inner Ear*, Univ. Dundee (**CC BY-NC-SA 4.0**) |
| Volume | > 5 000 structures 3D, > 3 500 définitions |

**Deux disqualifications cumulées** comme base de dérivation :
1. **ShareAlike** sur l'ensemble ;
2. **licences mélangées**, dont au moins un composant **NC** — impossible à démêler proprement dans un
   produit commercial.

Z-Anatomy reste **précieux comme référence de nommage et d'adjacence**, jamais comme géométrie source.

## 8. Hiérarchie de sources retenue

```
PRIMARY DERIVATION SOURCE
  BodyParts3D — archive officielle DBCLS courante — CC BY 4.0
  → seule source dont la géométrie peut entrer dans le master livré

SECONDARY 2D CONTROL
  Servier Medical Art (muscles face/dos) — CC BY 4.0
  → contrôle de silhouette et de position ; incorporable si vectoriel exploitable

ANATOMICAL CROSS-CHECK
  AnatomyTOOL (ressource par ressource, CC0/CC BY seulement)
  OpenStax 1ʳᵉ édition (CC BY 4.0) — JAMAIS la 2e (NC)
  → validation de plausibilité, pas de géométrie importée

REFERENCE ONLY
  Z-Anatomy — CC BY-SA 4.0 + composants NC → aucune géométrie reprise

FAST PROTOTYPE ONLY
  Wikimedia Muscles front and back.svg — CC BY-SA 4.0
  → prototype jetable, exclu du master livré
```

## 9. Matrice de compatibilité (produit commercial propriétaire)

| Source | Licence | Commercial | Dérivation | Copyleft | Entre dans le master livré ? |
|---|---|---|---|---|---|
| BodyParts3D (officiel courant) | CC BY 4.0 | ✅ | ✅ | ❌ aucun | ✅ **oui — attribution obligatoire** |
| Servier Medical Art | CC BY 4.0 | ✅ | ✅ | ❌ aucun | ✅ oui — attribution obligatoire |
| OpenStax 1ʳᵉ éd. | CC BY 4.0 | ✅ | ✅ | ❌ aucun | ⚠️ possible, mais rôle = croisement |
| AnatomyTOOL (CC0/CC BY) | par ressource | ✅ si qualifiée | ✅ | ❌ | ⚠️ ressource par ressource |
| AnatomyTOOL (BY-SA) | CC BY-SA | ✅ | ✅ | ⚠️ SA | ❌ non (composant séparé au mieux) |
| AnatomyTOOL (NC / étudiant) | NC / restreint | ❌ | — | — | ❌ **exclu** |
| OpenStax 2e | CC BY-NC-SA 4.0 | ❌ | — | ⚠️ SA | ❌ **exclu** |
| Wikimedia `Muscles front and back.svg` | CC BY-SA 4.0 | ✅ | ✅ | ⚠️ **SA** | ❌ **prototype uniquement** |
| Z-Anatomy | CC BY-SA 4.0 + NC | ⚠️ mixte | ⚠️ | ⚠️ SA | ❌ **référence uniquement** |

## 10. Règles anti-contamination (dures)

1. **Séparation physique des espaces de travail** : la géométrie CC BY (dérivable) et la géométrie BY-SA/NC
   (prototype/référence) ne partagent **jamais** le même fichier de travail, ni le même calque, ni la même
   scène Blender.
2. **Un prototype BY-SA ne se blanchit pas.** Retoucher, simplifier ou re-vectoriser une source ShareAlike
   produit une œuvre dérivée ShareAlike. Le master livré doit être **reconstruit depuis BodyParts3D**, pas
   « nettoyé » depuis le prototype Wikimedia.
3. **Aucune source non déclarée.** Toute géométrie du master doit être traçable à une source listée §8, avec
   licence et date d'accès.
4. **Le NC est éliminatoire**, sans exception ni « usage interne » (l'app est un produit commercial visé).
5. **L'attribution CC BY est irrévocable** : elle ne disparaît pas parce que le rendu final est stylisé au
   point d'être méconnaissable.
6. **Aucune archive, aucune image, aucun `.pptx` n'est committé dans Git** à ce stade.

## 11. Obligations d'attribution à provisionner

Le produit devra porter, dans une surface de crédits atteignable (documentation et/ou écran « à propos ») :

```
BodyParts3D, © The Database Center for Life Science
licensed under CC Attribution 4.0 International
```
et, si des éléments Servier sont incorporés :
```
Servier Medical Art — Les Laboratoires Servier — CC BY 4.0
```
et, si un croisement OpenStax 1ʳᵉ édition est incorporé : attribution OpenStax + édition + CC BY 4.0.

**La surface de crédits n'existe pas encore dans l'app.** Sa création est une **dette explicite** portée par
`Sb_ASSET_03.2` / `Sx_ASSET_04`, **pas** par cette recherche. `ATTRIBUTION SURFACE: NOT YET IMPLEMENTED`.

## 12. Limites de ce document

- **Pas un avis juridique.** La qualification finale (œuvre dérivée vs originale, portée de l'attribution,
  compatibilité de la chaîne) relève d'un **conseil professionnel**.
- Relevés **datés du 2026-07-23** : les licences peuvent changer — BodyParts3D vient précisément d'en
  administrer la preuve. **Re-vérifier à chaque acquisition réelle.**
- Aucune archive n'a été téléchargée ; **aucun maillage n'a été inspecté**. L'avertissement upstream est
  **cité d'une source officielle** ; les **défauts de maillage spécifiques restent `NOT YET VERIFIED`**
  (observation d'un dépôt tiers, à confirmer au build sur les fichiers réels).
- `PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED` · `ASSET INTEGRATION GATE: BLOCKED`.

## Sources officielles consultées (2026-07-23)
- BodyParts3D — **avertissement qualité officiel** (section *Notice*) : http://lifesciencedb.jp/bp3d/info/
- BodyParts3D — licence : https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html
- BodyParts3D — description : https://dbarchive.biosciencedbc.jp/en/bodyparts3d/desc.html
- BodyParts3D — téléchargement : https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html
- BodyParts3D — miroir historique (licence **périmée**) : https://github.com/Kevin-Mattheus-Moerman/BodyParts3D
- Servier Medical Art : https://smart.servier.com/ · https://smart.servier.com/smart_image/musculature-back/
- AnatomyTOOL — informations légales : https://anatomytool.org/legal-information
- OpenStax — A&P 1ʳᵉ éd. : https://openstax.org/books/anatomy-and-physiology/pages/preface
- OpenStax — A&P 2e : https://openstax.org/books/anatomy-and-physiology-2e/pages/1-introduction
- Wikimedia Commons : https://commons.wikimedia.org/wiki/File:Muscles_front_and_back.svg
- Z-Anatomy : https://github.com/Z-Anatomy/The-blend

## Verdict

**Verdict :** 🟢 **OPEN SOURCE REUSE STRATEGY: DEFINED — SOURCE-REUSE-FIRST.** La correction majeure est
établie sur source officielle : **BodyParts3D est sous CC BY 4.0** (mise à jour **2025-02-27**), et non
CC BY-SA 2.1 Japan comme l'indiquait le miroir GitHub figé en 2011 — **la dérivation vers un master
propriétaire redevient licite, sous attribution obligatoire et irrévocable**. Hiérarchie tranchée :
**BodyParts3D = source de dérivation primaire** ; **Servier = contrôle 2D** (CC BY 4.0, PNG + pack PPT, nature
vectorielle **à déterminer au build**) ; **AnatomyTOOL + OpenStax 1ʳᵉ édition = croisement anatomique**
(la **2e est NC → exclue**) ; **Z-Anatomy = référence seulement** (BY-SA + composant NC) ; **Wikimedia
`Muscles front and back.svg` = prototype jetable** (BY-SA, dérivé d'OpenStax, **exclu du master livré**).
Règles anti-contamination dures posées (séparation des espaces de travail, interdiction de « blanchir » un
prototype ShareAlike, NC éliminatoire, téléchargement depuis la seule archive officielle DBCLS). **Aucune
archive téléchargée, aucune image importée, aucun asset produit.** `ATTRIBUTION SURFACE: NOT YET IMPLEMENTED`
· `PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED` · `ASSET INTEGRATION GATE: BLOCKED`.
