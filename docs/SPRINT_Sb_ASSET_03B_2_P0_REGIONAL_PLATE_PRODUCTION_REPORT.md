# Sprint Sb_ASSET_03B.2 — P0 Regional Plate Production Package — REPORT

> **⚠️ SUPERSEDED (partiel) par Sb_ASSET_03B.2R (2026-07-29).** Le **socle géométrique Servier** de ce package est
> `SUPERSEDED FOR BODY-FITTING GEOMETRY` : la production P0 dérive désormais de **BodyParts3D 4.0 (CC BY 4.0)**.
> Voir [`strategy/Sb_ASSET_03B_2R_BODYPARTS3D_SOURCE_RESET_SPEC.md`](strategy/Sb_ASSET_03B_2R_BODYPARTS3D_SOURCE_RESET_SPEC.md)
> + [`SPRINT_Sb_ASSET_03B_2R_BODYPARTS3D_SOURCE_RESET_REPORT.md`](SPRINT_Sb_ASSET_03B_2R_BODYPARTS3D_SOURCE_RESET_REPORT.md).
> Le **protocole de revue, les budgets et le contrat d'intake** de ce package **restent valides** ; seule la
> **source géométrique** change (et le deltoïde devient source-segmenté). Historique conservé, non réécrit.

**Statut** : 🟢 **`Sb_ASSET_03B.2: OPEN — PHASE 1 PRODUCTION PACKAGE READY / GEOMETRY PENDING (AWAITING OPERATOR TOOLCHAIN)`** —
docs-only ; **aucune géométrie produite, aucun `ai_usage: NONE` fabriqué, aucune gate franchie**. `ASSET
INTEGRATION GATE: BLOCKED`.
**Type** : PACKAGE DE PRODUCTION + CONTRAT D'INTAKE — sous-cycle `Sx_ASSET_03B`.
**Date** : 2026-07-27 · **Base** : `c70bdb0` · **Worktree** : `work/sb-asset-03b-2-p0-regional-plates`.
**Concurrence connue** : PR #35 (Custom wizard, head `613b6395`) + 10 PR dependabot — **préservées** (0 fichier
partagé touché).

---

## 0. Décision structurante (honnêteté de provenance)

Le GO demandait « produire 3 géométries P0 ». **La géométrie anatomique ne peut pas être produite par
l'assistant IA** sans violer §6 (« aucune génération IA de l'anatomie ») et le Descriptor Schema (`ai_usage:
NONE`), ni sans fabriquer une provenance de source acquise inexistante. **Décision opérateur retenue (question
posée, réponse « toolchain opérateur »)** : la géométrie est produite **hors Git par le toolchain opérateur**
(Blender/Potrace/Inkscape sur figures Servier/OpenStax acquises), comme le master BodyMap en `Sb_ASSET_03.1`.

**Conséquence** : `Sb_ASSET_03B.2` est structuré en **deux lots** :
- **(a) ce commit** = package de production (brief exécutable) + contrat d'intake + docs directeurs ;
- **(b) intake atomique** (sur GO, sur la géométrie livrée) = `§5bis` enactment + guard test + descripteurs/
  registry/manifest/preview à **provenance réelle**.

`§5bis` **n'est pas enacté ici** : couplé atomiquement au guard + géométrie (principe 03B.1, anti « prose-only »).

## 1. Usage des Superpowers
- **Préflight** réel (canonical `c70bdb0`, PR #35 + dependabot inventoriées).
- **Étape 0 — 5 axes arbitrés** (A anatomie/sources · B géométrie/crops · C contrats/IDs/gouvernance · D mobile/
  a11y/revue · E adversarial/SVG-safety/repro) → synthèse unique (spec §2), options rejetées consignées.
- **Question bloquante posée à l'opérateur** (production géométrie IA vs toolchain) → tranchée « toolchain
  opérateur » ; restructuration honnête package/intake.

## 2. Fichiers

**Créés (3)** :
- `docs/strategy/Sb_ASSET_03B_2_P0_REGIONAL_PLATE_PRODUCTION_SPEC.md` (brief exécutable + contrat d'intake)
- `docs/production/muscle-focus/AUREN_MUSCLE_FOCUS_P0_REGIONAL_REVIEW_PROTOCOL.md` (revue par plaque)
- `docs/SPRINT_Sb_ASSET_03B_2_P0_REGIONAL_PLATE_PRODUCTION_REPORT.md` (ce rapport)

**Modifiés** :
- `docs/production/muscle-focus/AUREN_MUSCLE_FOCUS_GOVERNANCE_AMENDMENT.md` (enactment planifié à l'intake 03B.2)
- `docs/strategy/SPEC_REGISTRY.md` · `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` ·
  `docs/strategy/AUREN_ASSET_PROGRAM_ROADMAP.md` (ouverture 03B.2)

**Scope de ce lot** : **100 % `docs/**`**. `0` `design/auren/**` (pas d'enactment `§5bis` ce lot) · `0` SVG/PNG/
géométrie · `0` `tests/**` (guard écrit à l'intake) · `0` `app/**` · `0` migration · `0` `data/**` · `0` Custom.

## 3. Contenu figé (package)
- **Brief géométrique par plaque** (spec §5) : chest (front, éventail convergent, anti-poumons) · shoulders
  (front+back, 3 faisceaux ancrés os) · posterior (back, bassin→cuisse, mode N2 muscle-heads,
  sans fausse localisation des chefs ischio-jambiers).
- **Clarification « crop du master »** (spec §3) : repère spatial seul, géométrie musculaire redessinée, aucun
  ID master recopié, `GLOBAL BODYMAP: UNCHANGED`, contrat des 11 zones inchangé.
- **Sources & licences** (spec §4) : Servier + OpenStax 1ʳᵉ éd. = dérivation ; BodyParts3D/NLM/Z-Anatomy =
  validation ; interdits (2ᵉ éd., SA/NC, MuscleWiki/BioDigital…, IA-anatomie). Champs d'acquisition par plaque.
- **Contrats d'intake** : SVG (§6) · descripteurs/registry (§7) · guard test 26 positifs + négatifs (§8) ·
  budgets (§9) · manifest/provenance/licences (§11) · preview 360 px/desktop/no-JS + captions FR figées (§12).
- **Critères d'acceptation** (§13) · **procédure de revue par plaque** (protocole dédié).

## 3bis. Réconciliation de contrat post-livraison — mode N2 posterior

`POST-MERGE CONTRACT RECONCILIATION` (correction docs-only, non-closeout) :
- le blueprint `Sb_ASSET_03B.1` **était et reste correct** (`auren-plate-region-posterior` N2 = `muscle-heads`) ;
- le package `Sb_ASSET_03B.2` avait employé **par erreur** `grouped-honest` pour le **N2** ;
- la correction **réaligne** 03B.2 **sans modifier** le contrat v0.1.0 (ID Contract / Descriptor Schema /
  blueprint P0 **byte-identiques**) ;
- **N3 `auren-plate-muscle-posterior` reste `grouped-honest`** (inchangé) ;
- **aucune géométrie n'existait** au moment de la correction ; **aucun artefact opérateur** à rejeter ou migrer
  (le snapshot de contrats du workspace opérateur devient toutefois **périmé** → re-snapshot requis avant reprise).
- **Statut inchangé** : `Sb_ASSET_03B.2: OPEN — PHASE 1 PRODUCTION PACKAGE DELIVERED / GEOMETRY PENDING`.

## 4. Ce qui reste AVAL (gated, non fait ici)
Géométrie SVG (toolchain opérateur) · `§5bis` enactment · guard test vert (pos+nég) · descripteurs/registry/
manifest à hash réel · preview HTML · revue humaine · revue anatomique professionnelle · toute intégration
runtime. Aucun de ces éléments n'est produit ni préjugé.

## 5. Vérifications
`git diff --check` propre · `check_scope` **DOCS** (ce lot 100 % docs) · `check_spec_protocol` PASS · diff = 100 %
`docs/**` · aucune réouverture `Sx_UI`/`Sx_ASSET_01/02` · **aucun terme mensonger** (`approved`/`legally cleared`/
`anatomically validated professionally`/`runtime ready`/`integration authorized` absents en affirmation) ·
`design/auren/` **non touché** (BodyMap master/compact intacts).

## 6. Non-goals (rappel)
Aucune géométrie · aucun SVG · aucun enactment `§5bis` ce lot · aucun guard écrit ce lot · aucune plaque N3 ·
aucun overlay · aucune vue lateral/section · aucune intégration `app/` · aucune approbation · aucun franchissement
de gate.

---

## Verdict

**Verdict :** 🟢 **`Sb_ASSET_03B.2: OPEN — PHASE 1 PRODUCTION PACKAGE READY / GEOMETRY PENDING (AWAITING OPERATOR TOOLCHAIN)`.** Le brief
exécutable des 3 Regional Plates P0 + le contrat d'intake (SVG/descripteur/registry/guard/preview) + le protocole
de revue sont figés, honnêtement, **sans fabriquer de géométrie ni de provenance**. La géométrie est produite par
le toolchain opérateur ; `§5bis` enactment + guard + intake à provenance réelle sont livrés **atomiquement à
l'intake** (sur GO). `REGIONAL PLATE GEOMETRY: NOT PRODUCED (this lot)` · `GOVERNANCE AMENDMENT: SPECIFIED /
ENACTMENT SCHEDULED AT INTAKE` · `GLOBAL BODYMAP: UNCHANGED` · `HUMAN ANATOMICAL REVIEW: REQUIRED / NOT STARTED`
· `PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED` · `ASSET INTEGRATION GATE: BLOCKED`. **Prochaine action (sur GO)** :
`GO OPERATOR` (production géométrie) puis `GO INTAKE — Sb_ASSET_03B.2` (enactment + guard + intake atomique, via
PR).
