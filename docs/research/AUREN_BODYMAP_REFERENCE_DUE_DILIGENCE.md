# AUREN — BodyMap Reference Due Diligence (Sx_ASSET_03)

**Type** : recherche source-officielle — **DOCS-ONLY** (0 image/référence importée)
**Date d'accès initiale** : **2026-07-22** · **AMENDÉ le 2026-07-23**
**Portée** : évaluer les références anatomiques candidates pour la production du master BodyMap.
**NON une conclusion juridique.** Établit `OFFICIAL LICENSE EVIDENCE RECORDED AT ACCESS DATE`, jamais
`LEGAL CLEARANCE COMPLETE`. Aucun texte de licence, aucune image n'est copié dans le repo à ce stade.

---

## 0. ⚠️ AMENDEMENT 2026-07-23 — LE §1 CI-DESSOUS EST PÉRIMÉ

> **La licence de BodyParts3D relevée le 2026-07-22 était fausse.** Le §1 est **conservé tel quel comme
> preuve historique** de ce qui avait été relevé et de la conclusion qui en avait été tirée — il ne doit
> **plus** être utilisé comme référence opérationnelle.

| | Source consultée | Licence relevée | Statut |
|---|---|---|---|
| 2026-07-22 | miroir GitHub `Kevin-Mattheus-Moerman/BodyParts3D` (`LICENSE_content`) | CC BY-SA 2.1 Japan | ❌ **copie ancienne** (clone figé de la version `3.0` / `20110915`) |
| **2026-07-23** | **page de licence officielle DBCLS** `dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html` | **CC BY 4.0 International** | ✅ **officielle et courante — mise à jour 2025-02-27** |

**Cause de l'erreur** : le miroir GitHub a été traité comme « miroir officiel du dataset » et sa
`LICENSE_content` comme faisant foi. C'est un **clone de 2011** qui reproduit la licence de l'époque ; DBCLS a
depuis **relicencié** la base en **CC BY 4.0 International**. La page descriptive officielle `desc.html`
n'aide pas à trancher : elle affiche « CC BY » **sans version**, avec une dernière mise à jour **2013/05**.
**Seule `lic.html` fait foi.**

**Conséquences** (détail complet : [stratégie de réutilisation](AUREN_BODYMAP_OPEN_SOURCE_REUSE_STRATEGY.md)) :
- **CC BY 4.0 ne comporte aucune clause ShareAlike** → le verdict « **dérivation écartée** » du §1 et du §4
  est **ANNULÉ**. La dérivation vers un master Auren propriétaire est **licite**, sous **attribution
  obligatoire et irrévocable** : *« BodyParts3D, © The Database Center for Life Science licensed under
  CC Attribution 4.0 International »*.
- BodyParts3D passe de **référence spatiale uniquement** à **`PRIMARY DERIVATION SOURCE`**.
- **Règle opérationnelle** : télécharger **exclusivement** depuis l'archive officielle DBCLS — la licence
  applicable est celle de la source dont on obtient effectivement la copie, jamais celle d'un miroir.
- **Nuance conservée** : CC BY autorise la dérivation commerciale, **pas** l'effacement de l'origine. Auren
  possède sa contribution créative, **pas** les données anatomiques sous-jacentes ; « Auren owns the master »
  sans qualification reste **faux**.

**Leçon de méthode retenue** : un miroir, même complet et de bonne foi, **n'est pas une source juridique
primaire**. Seule la page de licence de l'éditeur, relevée à la date d'usage, l'est.

---

## 1. BodyParts3D / Anatomography — ⚠️ SECTION HISTORIQUE PÉRIMÉE (relevé 2026-07-22, cf. §0)

| Champ | Valeur (relevée 2026-07-22) |
|---|---|
| Projet | **BodyParts3D / Anatomography** |
| Organisation | **Database Center for Life Science (DBCLS)** / Life Science Integrated Database Center — Univ. Tokyo |
| Source officielle | `http://lifesciencedb.jp/bp3d/` · `https://dbarchive.biosciencedbc.jp/en/bodyparts3d/` |
| Miroir officiel (données + licence) | `github.com/Kevin-Mattheus-Moerman/BodyParts3D` (`LICENSE_content`, `README.md`) |
| **Licence** | **CC BY-SA 2.1 Japan** (Creative Commons Attribution-ShareAlike / « Attribution-Inheritance ») |
| SPDX (indicatif) | `CC-BY-SA-2.1-JP` |
| Copyright | © **2008** Database Center for Life Science / Life Science Integrated Database Center |
| **Attribution requise (texte exact)** | *« BodyParts3D, © 2008 The Database Center for Life Science licensed under CC Attribution-Share Alike 2.1 Japan »* |
| Format des données | **OBJ** (maillages 3D polygonaux extraits d'IRM full-body) |
| Morphologie | corps humain adulte issu d'imagerie médicale (données volumétriques, non stylisées) |
| Usage commercial | permis par CC BY-SA **sous conditions** (attribution + ShareAlike) |
| Adaptation | permise par CC BY-SA **mais** les dérivés doivent être partagés sous la **même licence** (ShareAlike) |

### ⚠️ Implication ShareAlike — POINT CRITIQUE
CC BY-SA impose que **toute œuvre dérivée** de BodyParts3D soit distribuée sous la **même licence CC BY-SA**.
Une extraction/vectorisation directe du maillage BodyParts3D ferait très probablement du master Auren une
**œuvre dérivée soumise à ShareAlike** — **incompatible** avec un master propriétaire Auren exclusif. La page
`desc.html` mentionnait « CC BY » (sans SA) ; la source officielle (`LICENSE_content` + README) confirme
**CC BY-SA** — la mention « CC BY » seule est erronée et **ne doit pas** être retenue.

### Matrice de classification (produit)
| Usage | Verdict |
|---|---|
| REFERENCE ONLY (repère spatial/volumétrique de position des zones) | ✅ **autorisé** (référence documentaire, pas de copie) |
| DERIVATIVE POSSIBILITY (extraction/vectorisation directe du maillage) | ⚠️ **DERIVATIVE → ShareAlike** — **écarté** pour un master propriétaire |
| ATTRIBUTION REQUIRED | **oui** si toute donnée est réutilisée ; à trancher par conseil juridique |
| LEGAL CLASSIFICATION | **PENDING** (revue juridique professionnelle) |

**Décision produit cible** :
```
BodyParts3D = référence spatiale et volumétrique FORTE (position/adjacence des régions),
PAS le style final, PAS une extraction automatique du master.
Le master reste une création humaine ORIGINALE, redessinée, non dérivée du maillage.
```

## 2. AnatomyTOOL

| Champ | Valeur (relevée 2026-07-22) |
|---|---|
| Source officielle | `https://anatomytool.org` (`/about`, `/legal-information`) |
| Institution | plateforme collaborative (contributions de départements d'anatomie) |
| **Modèle de licence** | **PAR RESSOURCE** — **aucune** licence globale de plateforme |
| Licences observées | CC BY, CC BY-NC-SA (et autres variantes CC), Public Domain, ressources étudiantes **restreintes** |
| Règle | vérifier **la description/licence de CHAQUE ressource individuellement** avant réutilisation |

### Règle impérative
```
La licence d'AnatomyTOOL n'est JAMAIS généralisée à tout le catalogue.
Chaque ressource considérée doit être qualifiée individuellement
(auteur, licence CC exacte, date, reproduction autorisée ou non).
Les ressources CC BY-NC-SA excluent l'usage commercial → à écarter pour un produit.
Les ressources étudiantes non-CC sont restreintes → à écarter.
```

## 3. Autres références
Toute référence additionnelle exigera : auteur · titre · source officielle · URL · date d'accès · licence ·
rôle exact · copie autorisée ou non · décision (consultable / utilisable comme référence / adaptation
possible / rejetée). **Aucune** référence supplémentaire n'est retenue à ce stade.

## 4. Conclusion d'éligibilité — ⚠️ PARTIELLEMENT PÉRIMÉE (cf. §0)
> La première puce est **annulée** par l'amendement du 2026-07-23 : BodyParts3D est **CC BY 4.0**, la
> dérivation est **licite sous attribution**. Les autres puces restent valables.

- ~~**BodyParts3D** : **REFERENCE ONLY** (repère spatial), **CC BY-SA** → **derivative écarté** pour un master
  propriétaire~~ → **ANNULÉ** : **CC BY 4.0**, `PRIMARY DERIVATION SOURCE`, attribution obligatoire ;
  `LEGAL CLASSIFICATION PENDING` (qualification dérivé/original toujours du ressort d'un conseil).
- **AnatomyTOOL** : éligible **ressource-par-ressource** uniquement, CC compatible commercial (CC BY / CC0)
  requise ; NC/étudiant écartés ; qualification individuelle obligatoire.
- ~~**Le master doit être une œuvre humaine ORIGINALE**, informée par des références spatiales, **non dérivée
  automatiquement** d'un dataset sous licence copyleft.~~ → **REMPLACÉ** par la doctrine
  **SOURCE-REUSE-FIRST** : le master peut être **dérivé** de BodyParts3D (CC BY 4.0), avec attribution. La
  contrainte « pas de copyleft » demeure et s'applique désormais à **Z-Anatomy**, au **SVG Wikimedia** et à
  **OpenStax 2e** (cf. [stratégie](AUREN_BODYMAP_OPEN_SOURCE_REUSE_STRATEGY.md)).
- État : **OFFICIAL LICENSE EVIDENCE RECORDED AT ACCESS DATE 2026-07-22** — la clearance juridique complète
  (classification dérivé/original, ShareAlike, attribution, cession) relève d'un **conseil juridique
  professionnel** au moment de `OPERATOR_ASSET_03.1` / `Sb_ASSET_03.2`. `PROFESSIONAL LEGAL CLEARANCE: NOT
  CLAIMED`.

## Sources (officielles / primaires, 2026-07-22)
- BodyParts3D desc. : https://dbarchive.biosciencedbc.jp/en/bodyparts3d/desc.html
- BodyParts3D licence officielle : http://lifesciencedb.jp/bp3d/info_en/license/index.html
- BodyParts3D miroir officiel + `LICENSE_content` : https://github.com/Kevin-Mattheus-Moerman/BodyParts3D
- AnatomyTOOL about : https://anatomytool.org/about
- AnatomyTOOL legal information : https://anatomytool.org/legal-information
