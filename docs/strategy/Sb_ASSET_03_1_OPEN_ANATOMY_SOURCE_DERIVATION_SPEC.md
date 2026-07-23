# Sb_ASSET_03.1 — Open Anatomy Source Acquisition & BodyMap Derivation Prototype — SPEC

> **Statuts courants (réconciliés à l'intake `Sb_ASSET_03.2`, 2026-07-23)** :
> ```
> BODYMAP DERIVATION PROTOTYPE: PRODUCED EXTERNALLY
> SPECIFIC MESH DEFECTS: VERIFIED ON SELECTED MESHES (0 non-manifold, 0 degenerate, 112 intersecting pairs)
> SERVIER PPTX CONTENT: EDITABLE VECTOR
> PACKAGE V2: SELF-DESCRIBING / DETERMINISTIC / RELOCATABLE (f45e0dbf…) — package v1 SUPERSEDED
> Sb_ASSET_03.2: TECHNICAL INTAKE IN PROGRESS → ACCEPTED FOR DESIGN SOURCE / HUMAN REVIEW PENDING
> BODYMAP FINAL MASTER: NOT YET APPROVED
> ASSET INTEGRATION GATE: BLOCKED
> ```
> Les formulations pré-build (« 2 points non tranchés », « package ISA/PART-OF à décider ») ne valent que
> dans les sections historiques datées ci-dessous.

**Type** : SPEC DE BUILD — **EXÉCUTÉE le 2026-07-23** · **Statut** : 🟢 **BUILD COMPLETE / MIXED-SOURCE
PROTOTYPE READY FOR TECHNICAL INTAKE** (cf. [rapport de build](../SPRINT_Sb_ASSET_03_1_OPEN_ANATOMY_SOURCE_DERIVATION_REPORT.md))
**Programme** : `Sx_ASSET` · cycle **`Sx_ASSET_03` amendé SOURCE-REUSE-FIRST** · **Date** : 2026-07-23
**Baseline** : `357802b` (brief opérateur) ; posé sur HEAD canonique réel `141ebd4` (avances Custom SCORING,
indépendantes, 0 fichier BodyMap).

> **Aucune archive n'est téléchargée, aucun maillage n'est traité, aucun SVG n'est produit par cette spec.**
> Elle définit le **pipeline** de `Sb_ASSET_03.1` et ses critères d'acceptation. Le contrat sémantique BodyMap
> (`Sb_ASSET_01.2`) reste **immuable**. `ASSET INTEGRATION GATE: BLOCKED`.

Documents opposables : [stratégie de réutilisation](../research/AUREN_BODYMAP_OPEN_SOURCE_REUSE_STRATEGY.md) ·
[due diligence](../research/AUREN_BODYMAP_REFERENCE_DUE_DILIGENCE.md) ·
[contrat SVG](../production/bodymap/AUREN_BODYMAP_SVG_STRUCTURE_AND_DELIVERY_CONTRACT.md) ·
[brief illustrateur](../production/bodymap/AUREN_BODYMAP_ILLUSTRATOR_BRIEF.md).

---

## 1. Mission

Produire un **prototype de master BodyMap dérivé de sources anatomiques ouvertes**, conforme au contrat
structurel (viewBox `0 0 240 200`, 14 IDs stables, 11 zones, 0 `zone-unknown`), **sans commande externe** et
**sans intégration runtime**. Le livrable est un **prototype de dérivation**, pas le master final approuvé.

**Ce que ce build change par rapport à `OPERATOR_ASSET_03.1`** : il **supprime la dépendance à un illustrateur
nommé** comme préalable. La géométrie provient de **BodyParts3D (CC BY 4.0)**, retravaillée par outillage
reproductible, et non d'un dessin commandé.

## 2. Prérequis d'entrée (gate d'ouverture du build)

| # | Prérequis | Nature |
|---|---|---|
| 1 | Licence BodyParts3D **re-vérifiée le jour du téléchargement** sur `lic.html` (pas sur un miroir) | vérification |
| 2 | Espace de travail **hors dépôt Git** pour archives et rendus intermédiaires | infrastructure |
| 3 | Blender + Inkscape/Potrace disponibles, **versions relevées** | outillage |
| 4 | Décision `4.0` vs `3.0` **documentée après inspection réelle** (cf. §4) | décision de build |

**Aucun illustrateur, aucun relecteur professionnel, aucun contrat n'est requis pour ouvrir ce build.**

## 3. Pipeline normatif (13 étapes)

### Phase A — Acquisition
1. **Téléchargement borné** depuis l'**archive officielle DBCLS uniquement** :
   `https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/` — `isa_BP3D_4.0_obj_99.zip` (136 Mo) et/ou
   `partof_BP3D_4.0_obj_99.zip` (62 Mo). **Aucun miroir, aucun CDN, aucun paquet tiers.**
2. **Hashes & provenance** : `sha256` de chaque archive, date/heure d'accès, URL exacte, licence relevée le
   jour même, taille. Consignés dans le registre de provenance du build. **Les archives ne sont jamais
   committées.**
3. **Mapping OBJ → muscles pertinents** via `isa_parts_list_e.txt` (2 905 entrées) : établir la table
   `FMA id → nom d'organe → zone Auren` pour les **seules structures utiles** aux 11 zones.

### Phase B — Sélection & scène
4. **Sélection des structures superficielles** uniquement (pectoraux, deltoïdes, grand dorsal, trapèze,
   biceps, triceps, quadriceps, ischio-jambiers/fessiers, mollets, abdominaux) — **aucune structure profonde,
   aucun organe, aucun squelette** dans le rendu final.
5. **Scène Blender reproductible** : fichier `.blend` versionné hors Git mais **décrit par un script** ou une
   procédure écrite rejouable (import, échelle, orientation, nommage des collections par zone).
6. **Caméra orthographique face/dos** : deux rendus strictement orthographiques, **même échelle, même centre
   vertical**, correspondant à la grille du contrat (face centre x=60, dos centre x=180).

### Phase C — Rendu & vectorisation
7. **Rendu monochrome par structure ou groupe** : chaque zone rendue isolément en aplat, sans ombrage, sans
   matériau, sans lumière — l'objectif est une **silhouette d'occupation**, pas une image anatomique.
8. **Export PNG/SVG de travail** (haute résolution, hors Git).
9. **Vectorisation** Inkscape/Potrace : conversion des aplats en chemins ; paramètres de seuil et de lissage
   **consignés** pour reproductibilité.
10. **Nettoyage & simplification** : réduction du nombre de points, suppression des artefacts de
    vectorisation, fermeture des contours, lissage compatible « instrument biomécanique » (cf. brief §3).

### Phase D — Mise au contrat
11. **Regroupement dans les 11 zones Auren** : un `<g id="zone-<code>">` **unique** par zone, agrégats
    `upper_back` et `posterior` assumés comme **functional-aggregate** (pas de sur-précision).
12. **Mise au contrat structurel** : `viewBox 0 0 240 200` · **14 IDs stables** · **0 `zone-unknown`** ·
    0 ID dupliqué · 0 path partagé entre zones · IDs enfants `geom-<zone>-<view>-<side>-<index>`.
13. **Comparaison croisée** Servier / AnatomyTOOL / OpenStax 1ʳᵉ édition : vérifier position et adjacence de
    chaque zone contre **au moins deux sources indépendantes**, consigner les écarts.

### Phase E — Preuves
- **Previews de contrôle** selon la matrice bornée existante (32 previews, cf. protocole de revue).
- **Aucun fichier dans `app/static/`** · **aucune intégration runtime** · **aucun test modifié**.

## 4. Qualité des données — état de la preuve & inspections obligatoires

### Avertissement upstream OFFICIEL (vérifié, source primaire)
Éditeur BodyParts3D / Anatomography, `http://lifesciencedb.jp/bp3d/info/` (section *Notice*), accédé le
**2026-07-23** — verbatim :
> *« There are still many concepts not represented in the data. There could be many ERRORS to be used as
> ANATOMICAL EDUCATION. Some parts were made from scratch by artists or distorted to fit into the
> environment. »*

```
UPSTREAM QUALITY WARNING:
BodyParts3D declares that the data may contain many errors for anatomical-education use,
that many concepts are still not represented, and that some parts were authored by artists
or distorted to fit the environment. The dataset is not presented as a canonical, complete
model of human anatomy.
```
→ **Le dataset ne dispense pas du croisement multi-sources** (§3 étape 13). Ne **jamais** combiner deux
versions sans vérifier les systèmes de coordonnées (l'éditeur signale qu'ils peuvent différer).

### Défauts de maillage spécifiques — **non vérifiés**
Les observations « interpénétrations peau/muscle en 4.0 » et « `FMA7163` non-manifold » proviennent du README
d'un **dépôt tiers**, pas de l'éditeur, et n'ont **pas** été vérifiées sur les archives (non téléchargées).
Elles valent comme **pistes d'inspection**, pas comme faits.

```
SPECIFIC MESH DEFECTS:
NOT YET VERIFIED

BUILD INSPECTION CHECKS:
- inspect potential skin/muscle intersections;
- inspect manifoldness of meshes used by the prototype;
- record affected representation IDs;
- do not generalize a defect to the entire dataset.
```

### Décision de version (obligatoire, documentée)
Le build **compare réellement** les archives disponibles (**IS-A** vs **PART-OF** ; et le cas échéant **4.0**
vs **3.0**) sur les **seules structures retenues**, puis **documente** le choix. **Interdit** : présumer que
« LATEST = meilleure », comme **écarter une release sur la foi d'un tiers**. La topologie n'est vérifiée que
sur les **maillages effectivement utilisés** par le prototype.

## 5. Sources autorisées (rappel opposable)

```
DÉRIVATION (géométrie entrant dans le livrable)
  BodyParts3D — archive officielle DBCLS — CC BY 4.0 — attribution obligatoire
  Servier Medical Art — CC BY 4.0 — si objets vectoriels exploitables (à déterminer, cf. §6)

CROISEMENT (validation, aucune géométrie importée)
  AnatomyTOOL — ressource par ressource, CC0/CC BY uniquement
  OpenStax 1ʳᵉ édition — CC BY 4.0 — JAMAIS la 2e (CC BY-NC-SA)

RÉFÉRENCE SEULEMENT
  Z-Anatomy — CC BY-SA 4.0 + composant NC

PROTOTYPE JETABLE
  Wikimedia Muscles front and back.svg — CC BY-SA 4.0 — EXCLU du livrable
```

**Contamination = échec de build.** Toute géométrie ShareAlike ou NC présente dans le livrable rend le build
`BLOCKED — LICENSE CONTAMINATION`.

## 6. Question ouverte à trancher au build

Le pack `SMART-Muscles.pptx` de Servier contient-il des **objets vectoriels éditables** ou seulement des
**rasters encapsulés** ? Un `.pptx` est un conteneur OOXML : inspecter `ppt/media/` et `ppt/slides/`.
- **Si vectoriel** → Servier devient un **contrôle 2D vectoriel** incorporable (CC BY 4.0).
- **Si raster** → Servier reste un **contrôle visuel** ; aucune géométrie n'en est extraite.

Cette question **n'est pas tranchée par la spec** et ne doit pas l'être par supposition.

## 7. IA — périmètre borné

**Autorisé** : exploration stylistique · simplification visuelle · proposition de silhouette **non
anatomique** · variation de contours.
**Interdit** : source anatomique unique · source des **frontières musculaires** · preuve de provenance ·
validation anatomique.
**Déclaration obligatoire** de tout usage (outil, version, fonction, finalité, parties affectées, méthode de
reprise humaine). **Géométrie générée non déclarée = livraison bloquée.**

## 8. Gate humain révisé

```
MULTI-SOURCE ANATOMICAL CONSISTENCY REVIEW: REQUIRED
PROFESSIONAL ANATOMICAL REVIEW: NOT CLAIMED / OPTIONAL BEFORE FINAL INTEGRATION DECISION
NAMED ILLUSTRATOR: NO LONGER A PRECONDITION
```

La revue de cohérence multi-sources **remplace**, pour le prototype, l'obligation préalable de revue
professionnelle : chaque zone est validée par **comparaison à au moins deux sources indépendantes** (Servier,
AnatomyTOOL qualifié, OpenStax 1ʳᵉ éd.), avec verdict par zone `PASS / ADJUST / BLOCKED / NOT APPLICABLE`.

**Ce que cette revue n'est pas** : une validation médicale, une preuve clinique, une garantie d'exactitude
anatomique. Elle établit une **cohérence de représentation** entre sources concordantes — rien de plus. La
revue professionnelle reste **possible et recommandée avant la décision d'intégration finale**, et
**n'est pas revendiquée** ici.

## 9. Livrables du build

| Livrable | Committé Git ? |
|---|---|
| `auren_bodymap_master_proto.svg` (prototype au contrat) | à trancher à l'intake `Sb_ASSET_03.2` |
| Registre de provenance (URL, sha256, licence, date, release retenue) | ✅ oui, docs |
| Table de mapping `FMA id → organe → zone Auren` | ✅ oui, docs |
| Procédure Blender/Inkscape rejouable (paramètres consignés) | ✅ oui, docs |
| Rapport de comparaison croisée (par zone, par source) | ✅ oui, docs |
| 32 previews de contrôle | ❌ non (preuves de revue, hors Git) |
| Archives OBJ, `.blend`, PNG intermédiaires | ❌ **jamais** |
| Déclaration d'usage d'IA | ✅ oui, docs |

## 10. Critères d'acceptation

1. Provenance complète et vérifiable (URL officielle, sha256, licence relevée le jour du téléchargement).
2. `viewBox 0 0 240 200` exact · **14 IDs stables** présents · **0 `zone-unknown`** · 0 ID dupliqué ·
   0 path partagé.
3. 11 zones présentes, agrégats honnêtes, aucune structure profonde ni organe visible.
4. Comparaison croisée documentée par zone contre ≥ 2 sources indépendantes.
5. Lisibilité vérifiée à 60 / 80 / 120 px et côte-à-côte à 360 px.
6. **0 contamination** ShareAlike/NC dans le livrable.
7. Attribution BodyParts3D consignée, prête à être portée par la future surface de crédits.
8. `0` fichier `app/**`, `0` test modifié, `0` fichier dans `app/static/`.

## 11. Budgets

`export compact optimisé ≤ 12 Ko` (**bloquant**, inchangé) · master prototype = **indicatif** · archives et
rendus intermédiaires = **aucun budget** (hors Git).

## 12. Risques identifiés

| Risque | Gravité | Traitement |
|---|---|---|
| Contamination BY-SA via le prototype Wikimedia | **élevée** | séparation physique des espaces de travail ; master reconstruit depuis BodyParts3D, jamais « nettoyé » depuis le prototype |
| Confusion OpenStax 1ʳᵉ éd. / 2e (NC) | **élevée** | toute référence OpenStax porte l'édition **et** la licence |
| Défauts de maillage (intersections, non-manifold) — **non vérifiés** | moyenne | `BUILD INSPECTION CHECKS` §4 sur les seuls maillages utilisés ; ne pas généraliser un défaut au dataset |
| Erreurs anatomiques upstream **déclarées par l'éditeur** (parties d'origine artistique ou déformées) | **élevée** | croisement multi-sources obligatoire ; le dataset n'est pas une vérité anatomique |
| Vectorisation produisant une planche médicale | moyenne | rendu monochrome par zone, simplification imposée par le brief §3 |
| Attribution oubliée à l'intégration | moyenne | dette explicite `ATTRIBUTION SURFACE: NOT YET IMPLEMENTED` portée par `Sb_ASSET_03.2`/`Sx_ASSET_04` |
| Sur-précision anatomique non soutenue par la donnée | moyenne | agrégats `upper_back`/`posterior` assumés ; 11 zones, jamais 12 |

## 13. Non-goals

Aucune intégration runtime · aucun fichier `app/static/` · aucun remplacement du prototype BodyMap actuel ·
aucune modification de `app/**`, `tests/**`, `data/**`, `migrations/**` · aucune modification du contrat
sémantique (11 zones, 6 macros, 14 IDs, `RADAR_AXES`) · aucune ouverture de `Sb_ASSET_03.2` · aucun contrat
juridique · aucune revendication de propriété exclusive · aucune clearance juridique · aucune variante P2
(`female_neutral_v1`, `neutral_abstract_v1`, vue latérale) · aucun asset Custom.

## 14. Statut & queue

```
Sx_ASSET_03: AMENDED — SOURCE-REUSE-FIRST
Sb_ASSET_03.1: BUILD COMPLETE / MIXED-SOURCE PROTOTYPE READY FOR TECHNICAL INTAKE
BODYMAP SEMANTIC CONTRACT: ALREADY COMPLETE / IMMUTABLE
BODYMAP MASTER: NOT YET PRODUCED
PRIMARY DERIVATION SOURCE: BodyParts3D official current archive — CC BY 4.0
ATTRIBUTION: MANDATORY
AUREN CREATIVE CONTRIBUTION: DISTINCT FROM UPSTREAM ANATOMICAL DATA
ATTRIBUTION SURFACE: NOT YET IMPLEMENTED
MULTI-SOURCE INDEPENDENCE: REQUIRED
MULTI-SOURCE ANATOMICAL CONSISTENCY REVIEW: REQUIRED
PROFESSIONAL ANATOMICAL REVIEW: NOT CLAIMED
UPSTREAM QUALITY WARNING: OFFICIAL / RECORDED VERBATIM
SPECIFIC MESH DEFECTS: NOT YET VERIFIED
Sb_ASSET_03.2: BLOCKED BY PROTOTYPE DELIVERY
ASSET INTEGRATION GATE: BLOCKED
```

Queue : `Sb_ASSET_03.1` (dérivation prototype) → `Sb_ASSET_03.2` (intake technique) → [gate] →
`Sx_ASSET_04` / `Sb_ASSET_04.1`. **`OPERATOR_ASSET_03.1` (commande externe) reste défini mais n'est plus le
chemin retenu en première intention** — il redevient l'option de repli si la dérivation échoue.

---

## Verdict

**Verdict :** 🟢 **Sb_ASSET_03.1: BUILD COMPLETE / MIXED-SOURCE PROTOTYPE READY FOR TECHNICAL INTAKE.** Le pipeline de dérivation est défini de
bout en bout — acquisition bornée depuis l'**archive officielle DBCLS** (hashes + provenance), mapping OBJ via
`isa_parts_list_e.txt`, sélection des seules structures superficielles, scène Blender reproductible, caméras
orthographiques face/dos alignées sur la grille du contrat, rendu monochrome par zone, vectorisation
Inkscape/Potrace paramétrée, nettoyage, regroupement dans les **11 zones**, mise au contrat (`viewBox
0 0 240 200`, **14 IDs**, **0 `zone-unknown`**), comparaison croisée Servier/AnatomyTOOL/OpenStax 1ʳᵉ éd. et
previews de contrôle. Le gate humain est révisé : **la revue de cohérence multi-sources est REQUISE**, la
**revue professionnelle n'est PAS revendiquée** et reste optionnelle avant décision d'intégration, et
**l'illustrateur nommé n'est plus un préalable**. Deux points restent **explicitement non tranchés** et
doivent l'être au build, pas par supposition : le **choix d'archive/version** (IS-A vs PART-OF, 4.0 vs 3.0,
après comparaison réelle) et la **nature vectorielle ou raster du pack Servier `.pptx`**. L'**avertissement
qualité upstream est officiel et cité verbatim** ; les **défauts de maillage spécifiques restent
`NOT YET VERIFIED`** et sont convertis en `BUILD INSPECTION CHECKS`. Contamination ShareAlike/NC = **échec de
build**. **Aucune archive téléchargée, aucun maillage inspecté, aucun SVG produit, 0 `app/**`, 0 test.**
`ASSET INTEGRATION GATE: BLOCKED` · `PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED`.
