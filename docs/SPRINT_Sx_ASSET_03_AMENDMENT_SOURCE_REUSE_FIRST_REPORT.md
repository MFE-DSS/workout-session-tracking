# Sprint Sx_ASSET_03 — AMENDEMENT « SOURCE-REUSE-FIRST » — REPORT

**Statut** : 🟠 **AMENDED — SOURCE-REUSE-FIRST** — **DOCS-ONLY** — **COMMITTED — `cd4aeb3`, parent `141ebd4`**
**Type** : AMENDEMENT DE STRATÉGIE + RECHERCHE SOURCE-OFFICIELLE — 0 SVG, 0 image, 0 archive, 0 `app/**`
**Date** : 2026-07-23 · **Baseline brief** : `357802b` ; **posé sur HEAD canonique réel `141ebd4`**
(avances Custom `SCORING_01`/`SCORING_02`, indépendantes, 0 fichier BodyMap/Sx_ASSET).

---

## 1. Préflight & collision

`357802b` (baseline du brief) est **ancêtre** de `141ebd4` — vérifié par `git merge-base --is-ancestor`.
Quatre commits Custom sont intervenus depuis (`65d1381`, `d0b80cb`, `7576600`, `141ebd4` — moteur de scoring
et couche de feedback). Ils touchent `SPEC_REGISTRY.md` et `ROADMAP_AND_NEXT_STEPS.md` dans leurs **sections
Custom Program**, disjointes des sections `Sx_ASSET`. Worktree isolé créé **sur le HEAD réel** plutôt que sur
la baseline du brief, pour éviter une collision au moment du merge. Aucun rebase, aucun force-push.

## 2. Étape 0 — Brainstorming / Options / Risques / Choix retenu

### Le problème réel
`OPERATOR_ASSET_03.1` était **bloqué à 7/7 prérequis manquants** : il exigeait un illustrateur nommé, un
relecteur à compétence documentée, un statut contractuel et un canal sécurisé — c'est-à-dire un **engagement
budgétaire et contractuel** avant toute preuve de faisabilité. Le produit ne peut pas avancer tant que ce
préalable n'est pas levé.

### Options envisagées

| Option | Description | Coût | Risque juridique | Verdict |
|---|---|---|---|---|
| **A** — Commande externe (statu quo) | illustrateur nommé, contrat, cession de droits | **élevé** (devis + délai) | faible (cession explicite) | ❌ bloque le produit sur un préalable non financé |
| **B** — Dérivation depuis sources ouvertes | BodyParts3D CC BY 4.0 → Blender → vectorisation → contrat SVG | **faible** (outillage libre) | **moyen** (attribution perpétuelle, qualification dérivé/original) | ✅ **RETENU** |
| **C** — Reprise du SVG Wikimedia | `Muscles front and back.svg`, déjà vectoriel face+dos | **très faible** | **élevé** (ShareAlike contamine le master) | ❌ écarté pour le livrable ; conservé en **prototype jetable** |
| **D** — Génération IA de la géométrie | modèle génératif produisant les silhouettes | faible | **très élevé** (provenance indémontrable, anatomie non fiable) | ❌ écarté — l'IA reste bornée au style |

### Ce qui a rendu B possible
La bascule ne vient pas d'un arbitrage de confort mais d'un **fait juridique nouveau** : BodyParts3D est
**CC BY 4.0** — **sans ShareAlike**. Tant que la source était réputée CC BY-SA, l'option B était **illicite**
pour un master propriétaire, et A était le seul chemin. La correction de ce fait **rouvre** l'espace.

### Risques du choix retenu et traitement

| Risque | Traitement retenu |
|---|---|
| Contamination ShareAlike via le prototype Wikimedia | séparation physique des espaces de travail ; master **reconstruit** depuis BodyParts3D, jamais « nettoyé » depuis le prototype |
| Confusion OpenStax 1ʳᵉ éd. (CC BY) / 2e (CC BY-NC-SA) | toute référence OpenStax porte **édition + licence** ; la 2e est exclue |
| Faux « second avis » (Wikimedia dérivé d'OpenStax, Z-Anatomy dérivé de BodyParts3D) | règle d'**indépendance des sources** écrite dans le protocole de revue |
| Attribution oubliée à l'intégration | dette explicite `ATTRIBUTION SURFACE: NOT YET IMPLEMENTED` |
| Défauts de maillage **non vérifiés** (intersections, non-manifold — source tierce) | `SPECIFIC MESH DEFECTS: NOT YET VERIFIED` + `BUILD INSPECTION CHECKS` sur les seuls maillages utilisés |
| Erreurs anatomiques **déclarées par l'éditeur** (parties artistiques ou déformées) | croisement multi-sources obligatoire ; le dataset n'est **pas** une vérité anatomique |
| Qualité anatomique sans relecteur professionnel | **revue de cohérence multi-sources REQUISE** ; revue professionnelle **non revendiquée**, recommandée avant intégration |

### Choix retenu
**Option B — SOURCE-REUSE-FIRST**, avec `OPERATOR_ASSET_03.1` conservé comme **option de repli** si la
dérivation échoue (silhouettes inexploitables, contamination, qualité insuffisante).

## 3. Recherche officielle (2026-07-23) — 6 familles vérifiées sur sources primaires

| Source | Licence vérifiée | Rôle retenu |
|---|---|---|
| **BodyParts3D** (DBCLS) | **CC BY 4.0 International**, maj **2025-02-27**, release **4.0** | **PRIMARY DERIVATION SOURCE** |
| **Servier Medical Art** | **CC BY 4.0** — 59 illustrations « Muscles », PNG + `SMART-Muscles.pptx` | contrôle 2D face/dos |
| **AnatomyTOOL** | **par ressource**, aucune licence de plateforme | croisement, CC0/CC BY seulement |
| **OpenStax A&P 1ʳᵉ éd.** | **CC BY 4.0** (2013-04-25, rév. 2022-01-27) | croisement autorisé |
| **OpenStax A&P 2e** | **CC BY-NC-SA 4.0** (2022-04-20, rév. 2026-04-23) | ❌ **exclue** (NC) |
| **Wikimedia `Muscles front and back.svg`** | **CC BY-SA 4.0**, dérivé d'OpenStax, SVG éditable | prototype jetable |
| **Z-Anatomy** | **CC BY-SA 4.0** + composant **NC** | référence seulement |

### La correction centrale
La due diligence du **2026-07-22** avait relevé **CC BY-SA 2.1 Japan** sur le **miroir GitHub**
`Kevin-Mattheus-Moerman/BodyParts3D` (`LICENSE_content`) et en avait conclu que **la dérivation était
écartée**. Ce miroir est un **clone de la version 3.0 / 20110915** qui reproduit la licence **de 2011**. La
page de licence **officielle DBCLS** (`lic.html`), **mise à jour 2025-02-27**, donne **CC BY 4.0
International**, avec l'attribution exacte : *« BodyParts3D, © The Database Center for Life Science licensed
under CC Attribution 4.0 International »*.

**Le §1 de la due diligence est conservé tel quel comme preuve historique**, précédé d'un §0 d'amendement qui
le marque périmé — la trace de l'erreur et de sa cause est préservée, conformément à la doctrine du repo.

**Leçon de méthode enregistrée** : un miroir, même complet et de bonne foi, **n'est pas une source juridique
primaire**. Seule la page de licence de l'éditeur, relevée à la date d'usage, l'est. La page descriptive
officielle (`desc.html`) ne suffit pas non plus : elle affiche « CC BY » **sans version**, dernière mise à
jour **2013/05**.

## 3bis. Qualification des avertissements de qualité (correction d'audit)

Un audit du présent amendement a relevé que deux défauts de maillage précis — **interpénétrations peau/muscle
en release 4.0** et **triangles non-manifold du modèle de peau `FMA7163`** — étaient présentés comme des faits
établis alors qu'ils proviennent du **README d'un dépôt tiers** (miroir `Kevin-Mattheus-Moerman`), et non
d'une déclaration de l'éditeur. **Aucune archive n'ayant été téléchargée, ils n'ont pas pu être vérifiés.**

**Option B appliquée** (absence de preuve primaire) :
```
SPECIFIC MESH DEFECTS: NOT YET VERIFIED
BUILD INSPECTION CHECKS:
- inspect potential skin/muscle intersections;
- inspect manifoldness of meshes used by the prototype;
- record affected representation IDs;
- do not generalize a defect to the entire dataset.
```

**En revanche, un avertissement upstream OFFICIEL existe bel et bien** — recherché et trouvé sur le site du
projet (`http://lifesciencedb.jp/bp3d/info/`, section *Notice*, accédé le 2026-07-23), enregistré **verbatim**
plutôt que paraphrasé :
> *« There are still many concepts not represented in the data. There could be many ERRORS to be used as
> ANATOMICAL EDUCATION. Some parts were made from scratch by artists or distorted to fit into the
> environment. »*

Il est **plus fort** que la formulation attendue, et apporte un fait nouveau important : **une partie du
dataset est d'origine artistique ou déformée**. Cela renforce l'obligation de croisement multi-sources — le
dataset **n'est pas une vérité anatomique**. L'éditeur signale aussi que les systèmes de coordonnées peuvent
différer entre versions (« *you can combine them at your own risk* »).

**Note de traçabilité** : ni `desc.html`, ni `lic.html`, ni `download.html`, ni les `README_e.html` des
répertoires `20110915` et `LATEST` ne portent cet avertissement — il n'est présent que sur `lifesciencedb.jp`.
Par ailleurs le `README_e.html` de `20110915` affiche encore **CC BY-SA 2.1 Japan**, ce qui **confirme la
cause** de l'erreur initiale : **les artefacts d'archive anciens conservent l'ancienne licence**.

## 4. Points volontairement NON tranchés

1. **Choix d'archive / de version** — IS-A vs PART-OF, et le cas échéant 4.0 vs 3.0. Exige une **comparaison
   réelle** sur les structures retenues → tranché au build, documenté. Interdit de présumer que
   « LATEST = meilleure », **comme** d'écarter une release sur la foi d'un tiers.
2. **Nature du pack Servier `.pptx`** — objets vectoriels éditables ou rasters encapsulés ? Réponse obtenue en
   inspectant `ppt/media/` et `ppt/slides/` → tranché au build.

Ces deux points sont **écrits comme ouverts** dans la spec `Sb_ASSET_03.1`. Les trancher par supposition
aurait produit une spec fausse.

## 5. Livrables

**Créés (2)**
- `docs/research/AUREN_BODYMAP_OPEN_SOURCE_REUSE_STRATEGY.md` — hiérarchie de sources, matrice de
  compatibilité, règles anti-contamination, obligations d'attribution.
- `docs/strategy/Sb_ASSET_03_1_OPEN_ANATOMY_SOURCE_DERIVATION_SPEC.md` — pipeline 13 étapes, gate révisé,
  critères d'acceptation, risques, non-goals.

**Amendés (6)**
- `docs/research/AUREN_BODYMAP_REFERENCE_DUE_DILIGENCE.md` — §0 d'amendement ; §1 et §4 marqués périmés.
- `docs/strategy/Sx_ASSET_03_BODYMAP_HUMAN_PRODUCTION_PACKAGE_SPEC.md` — §0 amendement, §2, §10, §11, §14,
  §20, verdict.
- `docs/production/bodymap/AUREN_BODYMAP_ILLUSTRATOR_BRIEF.md` — §7 références.
- `docs/production/bodymap/AUREN_BODYMAP_IP_PROVENANCE_AND_SOURCE_DISCLOSURE_REQUIREMENTS.md` — §2 impact
  des licences.
- `docs/production/bodymap/AUREN_BODYMAP_ANATOMICAL_PRODUCT_MOBILE_REVIEW_PROTOCOL.md` — §0 gate révisé.
- `docs/production/bodymap/AUREN_BODYMAP_OPERATOR_PACKAGE_INDEX.md` — chaîne amendée.

**Documents directeurs (3)** : `SPEC_REGISTRY.md` · `ROADMAP_AND_NEXT_STEPS.md` · `AUREN_ASSET_PROGRAM_ROADMAP.md`.

**Non touchés** : `AUREN_BODYMAP_SVG_STRUCTURE_AND_DELIVERY_CONTRACT.md` et
`AUREN_BODYMAP_DELIVERY_MANIFEST_TEMPLATE.md` — le contrat géométrique et le manifeste sont **indépendants de
la méthode d'obtention** de la géométrie et restent valables mot pour mot.

## 6. Scope & confirmations

**0** SVG · **0** image · **0** archive téléchargée · **0** binaire · **0** `design/**` · **0** `tests/**` ·
**0** `app/**` · **0** `data/**` · **0** `migrations/**` · **0** `scripts/**` · **0** `.github/**` ·
**0** fichier Custom · **0** dépendance. Contrat sémantique BodyMap (11 zones, 6 macros, 14 IDs,
`RADAR_AXES`) **intouché**. `Sx_ASSET_01`/`Sx_ASSET_02`/`Sx_UI` **non rouverts**.

## 7. Contrôles

`check_spec_protocol` : **PASS**. `check_scope` : **TIER DOCS** (diff 100 % `docs/**`) → la CI est
légitimement skippée via `paths-ignore` ; aucun autre contrôle local requis par le contrat anti-overcheck.

## 8. Git & statut

Worktree isolé `work/sx-asset-03-source-reuse-amendment` sur `141ebd4`. **COMMITTED — `cd4aeb3`, parent
`141ebd4`**, fast-forward canonique et poussé ; commit 100 % `docs/**` → `CI: SKIPPED — DOCS-ONLY /
PATHS-IGNORE`.

---

## Verdict

**Verdict :** 🟠 **Sx_ASSET_03: AMENDED — SOURCE-REUSE-FIRST** · **`Sb_ASSET_03.1`: SPEC READY / BUILD NOT
STARTED**. L'amendement repose sur une **correction juridique établie sur source officielle** : BodyParts3D
est **CC BY 4.0** (DBCLS, maj **2025-02-27**) et non CC BY-SA 2.1 Japan — le relevé initial venait d'un
**miroir GitHub figé en 2011**. **Sans ShareAlike, la dérivation vers un master propriétaire devient licite**,
sous **attribution obligatoire et irrévocable**, ce qui débloque une voie que l'ancienne doctrine interdisait.
Hiérarchie tranchée (BodyParts3D dérivation · Servier contrôle 2D · AnatomyTOOL + OpenStax **1ʳᵉ éd.**
croisement · Z-Anatomy référence · Wikimedia prototype jetable), règles anti-contamination dures, gate humain
révisé (**cohérence multi-sources REQUISE**, **revue professionnelle NON revendiquée**, **illustrateur nommé
n'est plus un préalable**), pipeline de dérivation en 13 étapes spécifié sans être exécuté. Deux points sont
**délibérément laissés ouverts** pour être tranchés sur inspection réelle au build : **choix d'archive /
version** et **nature vectorielle du pack Servier**. Les avertissements de qualité sont **qualifiés selon leur
niveau de preuve** : l'**avertissement upstream officiel** est cité **verbatim** avec source et date d'accès
(la donnée contient des erreurs déclarées, certaines parties sont **d'origine artistique ou déformées** → le
dataset **n'est pas une vérité anatomique**), tandis que les **défauts de maillage spécifiques**, issus d'un
dépôt tiers et non vérifiés, sont ramenés à `SPECIFIC MESH DEFECTS: NOT YET VERIFIED` + `BUILD INSPECTION
CHECKS`. **Aucun asset produit, aucune archive téléchargée, aucun maillage inspecté, aucun `app/**` touché** ;
le contrat sémantique BodyMap reste **immuable**. Nouvelle dette explicite
`ATTRIBUTION SURFACE: NOT YET IMPLEMENTED`. `BODYMAP MASTER: NOT YET PRODUCED` ·
`ASSET INTEGRATION GATE: BLOCKED` · `PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED`.

**Prochaine action** (séparée, non commencée) : `GO BUILD — Sb_ASSET_03.1 Open Anatomy Source Acquisition &
BodyMap Derivation Prototype`.
