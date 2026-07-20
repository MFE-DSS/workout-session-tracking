---
name: AUREN_ASSET_PROGRAM_ROADMAP
type: strategy-roadmap
status: PROGRAM ROADMAP (docs-only) — opened by operator GO 2026-07-19
program: Sx_ASSET — Auren Proprietary Visual Asset System
independent_of: Sx_UI (CLOSED / HUMAN REVIEW COMPLETE)
source_brief: AUREN — Visual Asset Production Brief v1.0 (2026-07-15)
---

# Auren Asset Program — Roadmap

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
**`Sx_ASSET_01` implementation : COMPLETE / READY FOR CLOSEOUT** (01.1 + 01.2 acceptés). Non marqué
`Sx_ASSET_01 CLOSED` — closeout séparé requis. `Sx_ASSET_02` NON ouvert.

## Prochaine action
`GO CLOSEOUT — Sx_ASSET_01 Architecture, Governance & Production Gate` (non commencé).
