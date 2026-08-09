---
name: AUREN_ASSET_PROGRAM_ROADMAP
type: strategy-roadmap
status: PROGRAM ROADMAP (docs-only) — opened by operator GO 2026-07-19
program: Sx_ASSET — Auren Proprietary Visual Asset System
independent_of: Sx_UI (CLOSED / HUMAN REVIEW COMPLETE)
source_brief: AUREN — Visual Asset Production Brief v1.0 (2026-07-15)
---

# Auren Asset Program — Roadmap

> **⚠️ SOURCE RESET — Sb_ASSET_03B.2R (2026-07-29).** Socle géométrique des Regional Plates P0 réinitialisé de
> Servier vers **BodyParts3D 4.0 (DBCLS officiel, CC BY 4.0)** (Plan A déterministe ; Plan B sculpting humain
> conditionnel ; Plan C Open3DModel CC BY-SA séparé, non autorisé). Couverture P0 **prouvée** (exact-FMA, 35 reps).
> `SOURCE DOCTRINE: RESET LOCALLY` · `P0 GEOMETRY: NOT PRODUCED` · `QUALIFIED ANATOMICAL REVIEW: REQUIRED_PENDING`
> · `RUNTIME: BLOCKED`. Doctrine : [`Sb_ASSET_03B_2R_BODYPARTS3D_SOURCE_RESET_SPEC.md`](Sb_ASSET_03B_2R_BODYPARTS3D_SOURCE_RESET_SPEC.md).

> Programme **indépendant** de `Sx_UI` (clos). Système d'assets propriétaire, traçable, intégrable
> **après gate**. Auren = **instrument de progression biomécanique** (non médical, non atlas, non fitness
> générique, non gamer, non « IA » à gradients, non catalogue bodybuilding). Règle centrale : assets
> produits depuis un **contrat sémantique stable**, jamais page par page.

## Position actuelle
- **`Sx_ASSET_01`** (architecture/gouvernance/gate) : **SPEC RÉDIGÉE 2026-07-19** → `PRODUCTION QUEUE
  READY`. Taxonomie 11 zones figée (= code réel), 6 macros, 4 layers, IDs-API, pipeline production-only,
  provenance SPDX, non médical, budgets, manifest.
- **`ASSET INTEGRATION GATE: BLOCKED PENDING HUMAN / ANATOMICAL / LEGAL / MOBILE APPROVALS`** — aucun
  sprint `app/` avant les 15 approbations.
- Nom Auren = **WORKING PRODUCT NAME · EXTERNAL PROFESSIONAL CLEARANCE OPEN**.

## Build queue (bornée)
| Ordre | Sprint | Portée | Type | Dépendance |
|---|---|---|---|---|
| 1 | `Sx_ASSET_01` | architecture/gouvernance/gate | spec | — (livré) |
| 2 | `Sb_ASSET_01.1` | Governance Scaffold & Provenance Registry (`design/auren/`, manifest, provenance, LICENSES, style rules ; 0 asset tiers) | build | 01 accepté |
| 3 | `Sb_ASSET_01.2` | Body Zone Taxonomy & Mapping Contract (11 zones, 6 macros, mapping YAML, tests IDs/schéma ; 0 dessin) | build | 01.1 |
| 4 | `Sx_ASSET_02` | Functional Iconography Selection Spec (semantic map, Tabler, gaps custom, licence/version) | spec | 01.x |
| 5 | `Sb_ASSET_02.1` | Vendored Icon Subset & License Intake (subset minimal, provenance, licence, SVG normalisés, tests) | build | 02 |
| 6 | `Sb_ASSET_02.2` | Custom Auren Functional Glyphs (gaps démontrés) | build | 02.1 |
| 7 | `Sx_ASSET_03` | BodyMap Human Production Package (brief illustrateur, contrat cession, références, plan revue, grille) | spec | 01.2 |
| 8 | `OPERATOR_ASSET_03.1` | Human BodyMap Master Production | **externe/humain** | 03 |
| 9 | `Sb_ASSET_03.2` | BodyMap Master Intake & Technical Validation (XML/IDs/viewBox/budgets/provenance/resvg/previews ; 0 intégration) | build | 03.1 |
| 10 | `Sx_ASSET_04` | Asset Integration Slots & Consumer Mapping | spec | **gate franchi** |
| 11 | `Sb_ASSET_04.1` | Controlled Runtime Integration (remplacement ciblé prototype + icônes ; CI + baseline + review) | build app | 04 |
| 12 | `Sx_ASSET_05` | Final Asset Pack Closeout | closeout | 04.1 |

## Contrat sémantique (figé — ne pas dériver)
**11 zones** : `pecs · delt_lat · delt_post · lats · upper_back · biceps · triceps · quads · posterior ·
calves · core` (+ `unknown` = état métier neutre). **6 macros** : Chest(pecs) · Shoulders(delt_lat/
delt_post) · Back(lats/upper_back) · Arms(biceps/triceps) · Legs(quads/posterior/calves) · Core(core).
= `ZONE_LABELS` réel. **Aucune 12ᵉ zone.**

## Gates externes / opérateur (hors implémentation)
- **ASSET INTEGRATION** : BLOCKED (15 approbations humain/anatomique/juridique/mobile).
- **BodyMap master** : `OPERATOR_ASSET_03.1` = production humaine externe (illustrateur + relecteur
  anatomique).
- **Licences** : vérif source officielle au build ; aucun agrégateur juridique primaire.
- **Nom Auren** : brand-bearing = `PROVISIONAL UNTIL PROFESSIONAL CLEARANCE` (cf. gate juridique Sx_UI).

## Dépendances
- **Exercise System** : icône future `substitution-preserving-pattern` possible ; `Sx_ASSET` ne modifie
  pas la substitution.
- **Body Intelligence** : le master peut remplacer la géométrie prototype ; **0** ajout de zone / score /
  feature / donnée.
- **PWA** : icônes existantes en production ; remplacement seulement après clearance + validations.
- **Sx_UI** : CLOSED — non rouvert.

## P0 / P1 / P2
- **P0** (fondations) : BodyMap (face/dos · 11 zones · 6 macros · états · compact · previews 360px) ·
  iconographie fonctionnelle · marque/PWA audit · gouvernance.
- **P1** (extension) : glyphes zone · archétypes programmes · empty states · confidence · timeline
  markers · historique substitué/exclu · progression zone.
- **P2** (futur, **hors première queue**) : silhouette féminine · abstraite · vue latérale ·
  micro-animations · texture graphite · éditoriaux.

## Avancement
- **`Sb_ASSET_01.1`** Governance Scaffold & Provenance Registry : 🟢 **CODE COMPLETE — CI GREEN (run
  `29697874021` 3/3) — HUMAN REVIEW ACCEPTED** 2026-07-19 (`SPRINT_Sb_ASSET_01_1_GOVERNANCE_SCAFFOLD_REPORT.md`
  ; revue `SPRINT_Sb_ASSET_01_1_GOVERNANCE_SCAFFOLD_HUMAN_REVIEW_REPORT.md` ; commit `4603551`).
  `design/auren/` créé (README, manifest, provenance, style rules, intake checklist, LICENSES/README) + 21
  tests de garde (stdlib). 0 asset produit ; assets runtime référencés (non copiés) ; `ASSET INTEGRATION
  GATE: BLOCKED` inchangé. **2 dettes cosmétiques → `Sb_ASSET_01.2`** : (a) nuancer le champ `owner`
  (`OPERATIONAL REPOSITORY OWNER — IP OWNERSHIP NOT LEGALLY VERIFIED`, §11.1) ; (b) documenter la
  temporalité du garde binaire (interdiction SVG/PNG sous `design/auren/` = garde du lot, évolue au 1ᵉʳ
  intake `Sb_ASSET_02.1`, §16). Aucune n'est un défaut matériel.
- **`Sb_ASSET_01.2`** Body Zone Taxonomy & Mapping Contract : 🟢 **CODE COMPLETE — CI GREEN (run
  `29702926887` 3/3) — HUMAN REVIEW ACCEPTED** 2026-07-20 (`SPRINT_Sb_ASSET_01_2_BODY_ZONE_TAXONOMY_MAPPING_REPORT.md`
  ; revue `SPRINT_Sb_ASSET_01_2_BODY_ZONE_TAXONOMY_MAPPING_HUMAN_REVIEW_REPORT.md` ; commit `86aba63`).
  **2ᵉ et dernier build du socle `Sx_ASSET_01`.** Contrat sémantique versionné (Layer A, 0 géométrie, 0
  runtime) : `AUREN_BODY_ZONE_TAXONOMY.md` + `source/bodymap/` (`auren_bodymap_mapping.yaml` YAML
  JSON-compatible lu par `json` stdlib — 0 dépendance ; README). Parité runtime **revérifiée indépendamment**
  (`ZONE_LABELS`, `_WA_ZONE_TO_REGION`, descriptor). `unknown` séparé (non-anatomie). IDs SVG figés.
  **`BODYMAP COMPACT MACROS ARE NOT RADAR_AXES`** — `RADAR_AXES` byte-identique. **2 dettes de la revue 01.1
  résolues** : `owner` nuancé (`ip_ownership_status: not-legally-reviewed`) ; garde binaire → garde évolutive
  allowlistée (**prouvée par test négatif** en revue). 29 + 23 tests + broad sweep 273 verts.
  `ASSET INTEGRATION GATE: BLOCKED` inchangé.

## Statut du socle
🔒 **`Sx_ASSET_01` : CLOSED / HUMAN REVIEW COMPLETE** 2026-07-20
(`SPRINT_Sx_ASSET_01_FINAL_CLOSEOUT_REPORT.md` ; closeout `6345f5a`, baseline logique `1fbbb31`). Socle
**GOUVERNANCE + CONTRAT SÉMANTIQUE complet** (01.1 ACCEPTED + 01.2 ACCEPTED ; chaîne `6167485`→`1fbbb31` ;
CI historiques `29697874021` + `29702926887` 3/3). **GRAPHICAL ASSET PRODUCTION: NOT STARTED** (0 asset
produit). **OPEN DEBT: NONE** (dettes 01.1 owner + garde résolues, human review verified). `app/`
byte-identique tout le cycle. **`ASSET INTEGRATION GATE: BLOCKED`** — le closeout n'autorise ni intégration,
ni clearance, ni master, ni anatomie, ni mobile.

Gates ouverts après `Sx_ASSET_01` : `Sx_ASSET_02` **NOT OPENED** · `Sx_ASSET_03`/`OPERATOR_ASSET_03.1`
**HUMAN PRODUCTION PENDING** · clearance nom/assets Auren **EXTERNAL PROFESSIONAL CLEARANCE OPEN** ·
`Sx_ASSET_04`/`Sb_ASSET_04.1` **BLOCKED BY ASSET INTEGRATION GATE**.

## Cycle 02 — Iconographie 🔒 CLOSED / HUMAN REVIEW COMPLETE
🔒 **`Sx_ASSET_02` : CLOSED / HUMAN REVIEW COMPLETE** 2026-07-21
(`SPRINT_Sx_ASSET_02_FINAL_CLOSEOUT_REPORT.md` ; closeout `9ca1e58`). Sélection iconographique COMPLETE +
intake tiers **Tabler P0 (10 SVG)** ACCEPTED + correctif preview + re-review ACCEPTED. **OPEN IMPLEMENTATION
DEBT: NONE.** ICON SOURCE INTAKE: ACCEPTED FOR DESIGN SOURCE ; 10 icônes NOT AUTHORIZED FOR APP INTEGRATION ;
LEGAL CLEARANCE NOT CLAIMED ; `ASSET INTEGRATION GATE: BLOCKED`. Health Icons/custom/P1/BodyMap/runtime NON
produits. Détail par sprint ci-dessous.

- **`Sx_ASSET_02`** Functional Iconography Selection : 🟢 **SPEC COMMITTED** 2026-07-20 (`fe97adc`).
  SEMANTICS BEFORE ICONS. Tabler v3.45.0 MIT (primaire) ; Health Icons CC0 assets/MIT code (NOT REQUIRED FOR
  P0). P0 = 10 Tabler ; 0 gap custom → `Sb_ASSET_02.2 NOT REQUIRED`. Rend `ICON INTAKE GATE: READY FOR
  Sb_ASSET_02.1`.
- **`Sb_ASSET_02.1`** Vendored Icon Subset & License Intake : 🔴 **CODE COMPLETE — CI GREEN (`29749856878`
  3/3 sur `eafede6`) — HUMAN REVIEW REJECTED (preview only)** 2026-07-20 (revue
  `SPRINT_Sb_ASSET_02_1_VENDOR_ICON_SUBSET_LICENSE_INTAKE_HUMAN_REVIEW_REPORT.md` ; commit `804b08c`).
  **PREMIER INTAKE TIERS** : 10 SVG **Tabler v3.45.0** (commit `975920ff…`) + **licence MIT byte-identique**.
  **Assets / licence / gouvernance VÉRIFIÉS et NON remis en cause** (revalidation upstream indépendante 10/10
  byte-for-byte ; licence sha256 `b740a1d4…` ; registre/manifest/provenance 0 approved/0 verified ; garde
  effective par test négatif ; CI descendante 3/3 ; 0 app change). **Rejet UNIQUEMENT sur la surface de
  revue (§14)** : preview via `<img>` → `currentColor` non transmis → icônes **noires invisibles sur fond
  graphite** (`DARK PREVIEW DOES NOT REPRESENT A USABLE REVIEW SURFACE`). **`ASSET INTEGRATION GATE: BLOCKED`**
  ; 10 icônes NOT AUTHORIZED FOR APP INTEGRATION ; `Sb_ASSET_02.2 NOT REQUIRED`.
- **`Sb_ASSET_02.1-fix`** Review Preview Rendering Fix : 🟢 **PREVIEW FIXED — CI GREEN (`29815584673` 3/3
  sur `8342d99`) — HUMAN RE-REVIEW ACCEPTED** 2026-07-21 (`SPRINT_Sb_ASSET_02_1_VENDOR_ICON_SUBSET_LICENSE_INTAKE_HUMAN_REREVIEW_REPORT.md`
  ; `SPRINT_Sb_ASSET_02_1_FIX_PREVIEW_RENDERING_REPORT.md`). Preview via **CSS mask** (10 SVG canoniques via
  `mask-image` — **10 URL distinctes** ; couleur par `background-color: currentColor`) → **graphite sur clair,
  ambre `#C8A24B` sur graphite**, 16/20/24 px, 0 géométrie inline, 0 JS/CDN. **Rendu vérifié en NAVIGATEUR
  RÉEL** (Chrome headless, repo servi localement) : 419 px ambre / **0 px noir** dans la colonne graphite,
  matrice 10×3×2, mobile 360 utilisable. **Immutabilité VÉRIFIÉE** : 10 SVG / registre / LICENSES / manifest /
  provenance / garde **byte-identiques** ; test preview renforcé ; aucun test affaibli. → **`Sb_ASSET_02.1`
  HUMAN REVIEW ACCEPTED · ICON SOURCE INTAKE: ACCEPTED FOR DESIGN SOURCE · Sx_ASSET_02 implementation:
  COMPLETE / READY FOR CLOSEOUT.** `ASSET INTEGRATION GATE: BLOCKED` inchangé.

## Cycle 03 — BodyMap Human Production Package
- **`Sx_ASSET_03`** BodyMap Human Production Package : 🟢 **SPEC COMMITTED** 2026-07-22 (commit
  **`66d18d47a1f1f9a75556bede8de45f9a94daa055`**, parent `062ee92`, poussé sur le canonique ;
  `Sx_ASSET_03_BODYMAP_HUMAN_PRODUCTION_PACKAGE_SPEC.md` + rapport + `research/AUREN_BODYMAP_REFERENCE_DUE_DILIGENCE.md`
  + `production/bodymap/` ×6 ; baseline `cf41188`). **BODYMAP HUMAN PRODUCTION PACKAGE: DEFINED** ·
  **OPERATOR_ASSET_03.1: PACKAGE READY / NOT STARTED**. Transforme le contrat sémantique BodyMap (immuable) en
  **package de production humaine exécutable** — **master NON produit**. Brief illustrateur (`male_neutral_v1`
  P0), **contrat SVG tranché** (viewBox `0 0 240 200`, 14 IDs figés, `<g>`/zone, 0 zone-unknown, convention IDs
  enfants `geom-<zone>-<view>-<side>-<index>`), exigences PI (`PROCUREMENT CHECKLIST`, pas un contrat),
  protocole revue (**anatomique ≠ médical** + produit/mobile + 32 previews bornées), manifest template (0
  approved), contrat `Sb_ASSET_03.2` préparé, budgets par artefact. **Due diligence datée (2026-07-22)** :
  **BodyParts3D CC BY-SA 2.1 Japan** = référence spatiale uniquement (ShareAlike → dérivation écartée) ;
  **AnatomyTOOL** par ressource. IA = moodboard uniquement. 12 fichiers 100% docs ; 0 SVG/design/tests/app/
  asset/Custom. `BODYMAP MASTER: NOT YET PRODUCED` ; `PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED` ; `ASSET
  INTEGRATION GATE: BLOCKED`.

## Amendement 2026-07-23 — SOURCE-REUSE-FIRST
Le master **n'est plus commandé** en première intention. **Correction sur source officielle** :
**BodyParts3D = CC BY 4.0** (DBCLS, maj **2025-02-27**), et non CC BY-SA 2.1 Japan — relevé initial issu d'un
**miroir GitHub figé en 2011**. Sans ShareAlike, **la dérivation vers un master propriétaire est licite** sous
**attribution obligatoire** → `PRIMARY DERIVATION SOURCE`. Hiérarchie : Servier CC BY 4.0 (contrôle 2D) ·
AnatomyTOOL par ressource · OpenStax **1ʳᵉ éd.** (la 2e est NC, exclue) · Z-Anatomy référence (BY-SA + NC) ·
Wikimedia `Muscles front and back.svg` **prototype jetable** (BY-SA, dérivé d'OpenStax). Gate humain révisé :
**cohérence multi-sources REQUISE**, revue professionnelle **non revendiquée/optionnelle**, **illustrateur
nommé n'est plus un préalable**. Nouvelle dette : `ATTRIBUTION SURFACE: NOT YET IMPLEMENTED`.
Détail : [stratégie de réutilisation](../research/AUREN_BODYMAP_OPEN_SOURCE_REUSE_STRATEGY.md) ·
[spec `Sb_ASSET_03.1`](Sb_ASSET_03_1_OPEN_ANATOMY_SOURCE_DERIVATION_SPEC.md).

## Build 03.1 — dérivation mixte exécutée (2026-07-23)
**Prototype réellement produit, hors Git**, depuis **deux sources CC BY 4.0** : base + 9 zones dérivées de
**BodyParts3D 4.0** (55 maillages mappés par FMA ID officiel, base = `FMA7163 skin`), **`lats` et `core`
dérivées de Servier Medical Art** (PPTX qualifié **`EDITABLE VECTOR`**, 3 361 chemins natifs), alignées par
**transformation uniforme chiffrée**. **Contrat tenu** : `viewBox 0 0 240 200`, 14 IDs uniques, 11 groupes,
0 `zone-unknown`, 0 path partagé, gouttière vide, safe area ≥ 8 → **master 40/40** · **compact 41/41 à
8 615 o ≤ 12 Ko**. Topologie mesurée **sur les seuls maillages utilisés** : **0 non-manifold**, **0 face
dégénérée**, **112 paires en intersection** — intersections peau/muscle **confirmées**, non-manifold
`FMA7163` **non reproduit**, **sans généralisation au dataset**. Revue multi-sources **11 PASS / 0 BLOCKED**
(OpenStax 1ʳᵉ éd. + Sobotta 1909, indépendantes) ; **revue professionnelle NON revendiquée**. **32 previews**
et **package d'intake hashé** (14 495 063 o, `098d1b42…`). `AI_USAGE: NONE` · **0 contamination** ShareAlike/NC
· **0 binaire committé**.

## Intake tenté puis corrigé (2026-07-23)
L'intake technique `Sb_ASSET_03.2` (validation indépendante) a **bloqué en reproductibilité** : le producteur
des régions Servier `lats`/`core` n'était pas dans le package (`INCOMPLETE EXECUTABLE BUILD GRAPH`). Tout le
reste passait (intégrité, master 66/66, compact, trois méthodes géométriques concordantes). **Rien n'a été
copié dans `design/auren/`**. Le correctif `Sb_ASSET_03.1-fix` a **scripté le producteur manquant**
(sélecteurs exacts 117/157, parité byte-identique), **relocalisé les 14 scripts**, ajouté graphe explicite et
entrypoint, **rejoué la chaîne en clean-room dans deux racines** (master/compact reproduits exactement), et
réémis un **package v2 auto-descriptif et déterministe** (`f45e0dbf…`). Le master et le compact sont
**inchangés**. Package v1 et preuves d'intake **conservés**.

## Intake réussi avec le package v2 (2026-07-23)
La reprise `Sb_ASSET_03.2` a **validé le prototype indépendamment** avec le package v2 : identité exacte,
manifeste embarqué (`62=61+1`), **replay clean-room byte-identique** (master `dbb57db3…`, compact `8024fd4c…`,
package `f45e0dbf…`, 32 previews) dans une racine vierge à espace+Unicode, SVG conformes (3 méthodes
géométriques, Chrome+Inkscape concordants), provenance **CC BY 4.0 double** sans contamination. Le **master et
le compact entrent en design source** (`design/auren/source/bodymap/`, `exports/svg/`, octets préservés), avec
registre YAML, notices d'attribution, surface de revue HTML et **garde automatisé** ; 97 tests Auren verts.
**Rien n'entre dans `app/**`.**

## Statut des socles
🔒 **`Sx_ASSET_01` : CLOSED** · 🔒 **`Sx_ASSET_02` : CLOSED** · 🟠 **`Sx_ASSET_03` : AMENDED —
SOURCE-REUSE-FIRST** · 🟢 **`Sb_ASSET_03.1` : BUILD COMPLETE** · 🟢 **`Sb_ASSET_03.1-fix` : PACKAGE V2
READY** · 🟢 **`Sb_ASSET_03.2` : TECHNICAL VALIDATION PASSED / ACCEPTED FOR DESIGN SOURCE / HUMAN REVIEW
PENDING**. Programme global `Sx_ASSET` **non fermé**.
`BODYMAP MASTER: TECHNICALLY VALIDATED / NOT YET HUMAN APPROVED` · `ATTRIBUTION SURFACE: NOT YET IMPLEMENTED` ·
`ASSET INTEGRATION GATE: BLOCKED` conservé.

## Cycle 03B — Muscle Focus Technical Surface System (additif · spec) 🟢 SPEC COMMITTED
🟢 **`Sx_ASSET_03B` : SPEC COMMITTED** 2026-07-24 (docs-only ;
`Sx_ASSET_03B_MUSCLE_FOCUS_TECHNICAL_SURFACE_SYSTEM_SPEC.md` + rapport + `research/AUREN_MUSCLE_FOCUS_REFERENCE_RESEARCH.md`
+ `production/muscle-focus/` ×3). **Sous-cycle additif et stratégique** — **ne remplace pas** le bodymap
global, il **redéfinit la couche visuelle premium**. Correction stratégique de cible : le bodymap global était
trop « corps entier » pour être la surface héro ; la vraie valeur = « **comment** ce muscle s'insère, se
contracte, quels exercices le sollicitent », pas « où ça tape ». **Système à 3 niveaux** ancrés sur les **11
zones immuables** : **Niveau 1 = Global BodyMap conservé** (navigation/synthèse/score) · **Niveau 2 = 8
Regional Focus Plates** (une par macro, `legs` éclatée en quads/posterior/calves) · **Niveau 3 = 11 Muscle
Focus / Exercise Mechanics Plates** (faisceaux/insertions/fonctions/exercices ; 9 muscle-heads + 2
grouped-honest). **Aucune 12ᵉ zone** (faisceaux = géométrie Layer B, jamais des codes). Direction visuelle
clean-view + technical-overlay, profondeur par le trait, ancrage osseux, ≤ 3 teintes ; **5 cas d'exigence**
(pectoraux sans « poumons » · deltoïdes 3 faisceaux ancrés sur l'os · postérieur zoom bassin · lats/upper_back
largeur vs épaisseur · core corset non caricatural). **Stratégie de sources source-reuse-first** (Servier +
OpenStax 1ʳᵉ éd. + PD Gray's/Visible Human = géométrie dérivable ; BodyParts3D/Z-Anatomy = validation seulement ;
MuscleWiki/BioDigital/OpenStax 2ᵉ éd. = exclus ; IA = plan B/C borné et déclaré). **Contradiction de licence
arbitrée** par croisement adversarial : BodyParts3D **CC BY 4.0** (officiel DBCLS), le « CC BY-SA » venait du
miroir GitHub figé (piège déjà résolu au BodyMap). **Amendement de gouvernance requis** au build : autoriser
fibres/insertions **uniquement sur la surface plaque dédiée** (le global reste régi par `AUREN_STYLE_RULES §5`).
Queue `Sb_ASSET_03B.1→4` gatée. 7 fichiers créés + 3 mis à jour, **100 % docs**. `MUSCLE FOCUS PLATES:
CONCEPTUALLY DEFINED / NOT PRODUCED` · `GLOBAL BODYMAP: RETAINED AS NAVIGATION / SYNTHESIS LAYER` · `SOURCE
STRATEGY: DEFINED` · `RUNTIME INTEGRATION: NOT STARTED` · `PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED` · `ASSET
INTEGRATION GATE: BLOCKED`.

🟢 **`Sb_ASSET_03B.1` : CLOSED — CANONICAL DELIVERY COMPLETE** (merge `805b8a9` / **PR #34 MERGED** 2026-07-26 ;
blueprint `95f47b3` ; **1er parent réel `c48714b6`** = closeout SCORING_03, canonique avancé avant merge — sans
conflit, SCORING_03 préservé ; **PR CI 3/3 verte** run `30193520498` ; aucun run post-merge — docs-only
paths-ignore ; `docs/SPRINT_Sb_ASSET_03B_1_FINAL_CLOSEOUT_REPORT.md`). `Sb_ASSET_03B.2: READY TO OPEN / NOT
STARTED`. — *build docs ci-dessous (historique).* 🟢 **BLUEPRINT COMPLETE / PLATE CONTRACT LOCKED** 2026-07-24 (docs-only ; base `ff9541a` ;
worktree `work/sb-asset-03b-1-muscle-focus-blueprint`). Vision 03B → **système exécutable sur le papier, 0
géométrie**. **5 axes parallèles** (Contract&IDs · P0 Visual Blueprint · Source **revalidation web réelle** ·
UX/Mobile/A11y · **Adversarial Review**) + synthèse arbitrée. **9 créés + 6 modifiés (100 % `docs/**`)** :
blueprint spec + rapport + `production/muscle-focus/` ×7 (**ID Contract v0.1.0** namespace `auren-plate-*` disjoint de `zone-*`,
descriptor schema, view/crop contract, **7 blueprints P0**, overlay/a11y/mobile, **source ledger revalidé**,
governance amendment). **4 corrections de source** : NLM Visible Human **reclassé terms-based** (validation par
défaut), **clause anti-ingestion IA OpenStax**, Gray's/atlas **PD conditionnel**, Servier **images-only**.
**Amendement `§5bis`** borné aux surfaces plaque (master global inchangé), **spécifié / enactment gaté** au build
géométrie + guard test. **8 findings adversariaux résolus.** `PLATE GEOMETRY: NOT PRODUCED` · `GOVERNANCE
AMENDMENT: SPECIFIED / NOT YET ENACTED` · `SOURCE STRATEGY: REVALIDATED` · `ASSET INTEGRATION GATE: BLOCKED`.

🟢 **`Sb_ASSET_03B.2` : OPEN — PHASE 1 PRODUCTION PACKAGE READY / GEOMETRY PENDING (AWAITING OPERATOR TOOLCHAIN)** (docs-only, lot a) —
2026-07-27, base `c70bdb0`, worktree `work/sb-asset-03b-2-p0-regional-plates`. **Décision de provenance** : la
géométrie anatomique **ne peut pas** être produite par l'assistant IA (§6 interdit l'IA-anatomie ; Descriptor
Schema impose `ai_usage: NONE` ; provenance de source acquise requise) → **produite par le toolchain opérateur**
(Blender/Potrace/Inkscape sur figures Servier/OpenStax acquises), comme le master BodyMap `Sb_ASSET_03.1`.
**Structuré en 2 lots** : **(a)** package de production (ce commit) — brief exécutable des 3 plaques (chest
front / shoulders front+back / posterior back), contrat SVG/descripteur/registry/**guard 26 pos+nég**/preview,
budgets, **clarification « crop du master »** (repère spatial seul, géométrie musculaire redessinée, aucun ID
master recopié, `GLOBAL BODYMAP: UNCHANGED`, contrat 11 zones inchangé), sources (Servier + OpenStax 1ʳᵉ éd. =
dérivation), protocole de revue par plaque ; **(b)** intake atomique (sur GO, sur la géométrie livrée) —
**`§5bis` enactment + guard test + descripteurs/registry/manifest/preview à provenance réelle**. `§5bis` **non
enacté ce lot** (couplé atomiquement au guard + géométrie, principe 03B.1 anti « prose-only »). **3 créés + 4
modifiés, 100 % `docs/**`** ; check_scope DOCS ; spec PASS. PR #35 (Custom wizard) + dependabot **préservées**.
`REGIONAL PLATE GEOMETRY: NOT PRODUCED (this lot)` · `GOVERNANCE AMENDMENT: SPECIFIED / ENACTMENT SCHEDULED AT
INTAKE` · `GLOBAL BODYMAP: UNCHANGED` · `HUMAN ANATOMICAL REVIEW: REQUIRED / NOT STARTED` · `ASSET INTEGRATION
GATE: BLOCKED`.

## Prochaine action
`GO HUMAN REVIEW — Sb_ASSET_03.2 Auren BodyMap Design Source` (non commencé) — revue humaine (produit /
anatomique de cohérence / mobile) sur la surface hors runtime. Puis [gate] avant tout `Sx_ASSET_04`.
`OPERATOR_ASSET_03.1` (commande externe) = **option de repli**, non retenue.
Sous-cycle premium : `Sb_ASSET_03B.1` **CLOSED / DELIVERED** ; `Sb_ASSET_03B.2` **PACKAGE DE PRODUCTION LIVRÉ
(lot a)** → géométrie **par le toolchain opérateur** (sur GO `GO OPERATOR`), puis **`GO INTAKE — Sb_ASSET_03B.2`**
(via PR) = `§5bis` enactment + guard test + intake à provenance réelle, atomiquement sur la géométrie livrée.
Aucun des deux n'est ouvert par ce lot.
`Sx_ASSET_04`/`Sb_ASSET_04.1: BLOCKED BY ASSET INTEGRATION GATE`.

**⚙️ SYNTHETIC INTERNAL REVIEW — Sb_ASSET_03B.2R-C2 (2026-07-30 ; harnais réutilisable MERGÉ via PR #46 `d73af7d`, 2026-08-09).** La géométrie P0
(chest/shoulders/posterior, produite hors Git par le toolchain opérateur BodyParts3D) a passé un
**review interne synthétique single-family multi-agent** (conseil aveugle de 5 juges Claude + arbitre,
harness Promptfoo MIT versionné `tools/evals/muscle_focus/`, calibration 9/9 critiques + 12/12) :
chest **87.6 WITH_CONSTRAINTS**, shoulders **87.6 ACCEPTED_INTERNAL**, posterior **85.2
WITH_CONSTRAINTS**, HIGH partout, 0 veto ; reco globale `SYNTHETIC_ACCEPTED_WITH_CONSTRAINTS`. **Le
dispatch réviseur externe (C1) est différé par le propriétaire, non passé** (ZIP préservé). Ce review
interne **n'est PAS** une revue anatomique professionnelle qualifiée et ne la revendique pas ; une revue
professionnelle future peut le superséder. `RUNTIME/INTAKE/§5bis: BLOCKED` (ce sprint) ; `CANDIDATES: UNCHANGED`.
**Résultat historique** — a alimenté le C3 freeze → intake D1 → runtime 04.1 (déjà livrés). **Résolution `Sb_OPS`
(GO RESOLVE PR #46, 2026-08-09)** : le harnais réutilisable (eval only) a été salvagé et **MERGÉ** via **PR #46**
(`d73af7d`, CI canonique 3/3 GREEN, Sonar delta 0) — versionné pour les revues de plaques futures, sans
runtime/intake/§5bis.
