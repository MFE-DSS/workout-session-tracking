# Sprint Sx_ASSET_01 — Auren Visual Asset System — SPEC REPORT

**Type** : SPEC / AUDIT / GOUVERNANCE — **NO CODE / NO ASSET**, docs-only
**Statut** : 🟢 **SPEC LIVRÉE** (attente human review)
**Programme** : `Sx_ASSET` (nouveau, indépendant ; ouvert par GO opérateur)
**Date** : 2026-07-19
**Baseline** : `e4624b7`
**Spec détaillée** : `docs/strategy/Sx_ASSET_01_AUREN_VISUAL_ASSET_SYSTEM_SPEC.md`

---

## Contexte
Nouveau programme visuel **indépendant** de `Sx_UI` (qui reste **CLOSED / HUMAN REVIEW COMPLETE**). Source
directrice : *AUREN — Visual Asset Production Brief v1.0*. Objectif : système d'assets propriétaire,
durable, traçable, intégrable **ultérieurement**, **sans modifier l'app** dans ce sprint.

## Décision : Option A — architecture + gouvernance + gate (docs-only)
Contrat sémantique stable (taxonomie + IDs), 4 layers, pipeline production-only, provenance/licences,
non médical, queue bornée. **0 asset produit.** Verdict `PRODUCTION QUEUE READY` sans autoriser
l'intégration (`ASSET INTEGRATION GATE: BLOCKED`).

## Audit du code réel (faits, baseline `e4624b7`)
| Axe | Constat | Verdict |
|---|---|---|
| BodyMap descriptor | `services/body_map_descriptor.py` (mapped/unknown, primary/secondary, « no anatomy invented ») | source de vérité métier (Layer A) |
| Taxonomie zones | `services/muscle_mapping.py::ZONE_LABELS` = **11 zones exactes** (pecs…core) | **= taxonomie du brief, 0 drift** |
| BodyMap rendu | `_partials/worked_area_body_map.html` (SVG inline CSS/SSR, décoratif, mapping 11→6 déjà présent) | **PROTOTYPE — à remplacer après gate** |
| PWA/icons | `static/icons/` : auren-mark.svg, favicon.svg, apple-touch/icon-192/512/maskable-512 (Sb_UI_10.2) | **PROVISIONAL / ACCEPTED RUNTIME** — non supprimés |
| Iconographie | SVG inline (base.html nav/rail, welcome, worked_area) — custom, pas de lib vendored | inventorier dans semantic map |

## Éléments figés par la spec
- **Taxonomie 11 zones** (`pecs · delt_lat · delt_post · lats · upper_back · biceps · triceps · quads ·
  posterior · calves · core`) + `unknown` (état métier neutre) + **6 macro-régions**.
- **4 layers** séparés (métier/géométrie/présentation/surface).
- **IDs stables** traités comme API (`auren-bodymap`, `zone-*`, `body-front/back-base`).
- **Contrat SVG icônes** (viewBox 24, stroke currentColor, tailles, interdits).
- **Pipeline** SVGO/resvg **production-only** (0 dépendance runtime).
- **Manifest** (15 champs, 8 statuts, `approved` interdit avant revues).
- **Provenance/licences** SPDX ; positionnement **non médical** ; budgets ; P0/P1/P2.

## Gate d'intégration
`ASSET INTEGRATION GATE: BLOCKED PENDING HUMAN / ANATOMICAL / LEGAL / MOBILE APPROVALS` — 15 éléments à
approuver avant tout sprint `app/`.

## Statut du nom Auren
`WORKING PRODUCT NAME · EXTERNAL PROFESSIONAL CLEARANCE OPEN`. Éléments indépendants du nom peuvent
avancer ; brand-bearing = `PROVISIONAL UNTIL PROFESSIONAL CLEARANCE`. Assets PWA existants conservés
(provisoires).

## Build queue (bornée)
`Sx_ASSET_01` (spec) → `Sb_ASSET_01.1` (scaffold+provenance) → `Sb_ASSET_01.2` (taxonomie/mapping) →
`Sx_ASSET_02` (iconographie spec) → `Sb_ASSET_02.1`/`.2` (subset vendored + custom) → `Sx_ASSET_03`
(BodyMap production package) → `OPERATOR_ASSET_03.1` (master humain) → `Sb_ASSET_03.2` (intake) →
`Sx_ASSET_04` (integration slots) → `Sb_ASSET_04.1` (intégration contrôlée) → `Sx_ASSET_05` (closeout).

## Fichiers docs
- `docs/strategy/Sx_ASSET_01_AUREN_VISUAL_ASSET_SYSTEM_SPEC.md`
- `docs/SPRINT_Sx_ASSET_01_AUREN_VISUAL_ASSET_SYSTEM_REPORT.md` (ce fichier)
- `docs/strategy/AUREN_ASSET_PROGRAM_ROADMAP.md`
- `docs/strategy/SPEC_REGISTRY.md` + `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` (entrées)

Aucun `app/**`, `tests/**`, `design/**`, asset, SVG, PNG, licence touché.

## Non-goals
Aucun dessin BodyMap final · aucune génération IA anatomique · aucun logo définitif · aucune intégration
app · aucun template/CSS · aucun outil installé · aucune licence achetée · aucun `design/auren/` créé
(= premier build) · aucune réouverture de `Sx_UI` · aucun fichier Custom · aucun changement métier.

---

## Verdict

**Verdict :** 🟢 **AUREN ASSET PROGRAM: PRODUCTION QUEUE READY (spec livrée, docs-only).** Architecture +
gouvernance du système d'assets Auren définies : **taxonomie 11 zones figée** (= `ZONE_LABELS` réel, **0
semantic contract drift**), 6 macro-régions, 4 layers, IDs-API, contrat SVG, pipeline production-only,
provenance SPDX, non médical, budgets, queue bornée, manifest schématisé. BodyMap et icônes PWA actuels
audités comme **prototype/provisoires** (aucun supprimé). Nom Auren = working name ; brand-bearing =
provisional until clearance. **`Sx_UI` reste CLOSED.** **`ASSET INTEGRATION GATE: BLOCKED`** — pas
d'intégration app. Aucun asset/fichier applicatif produit.

**Recommandation** : **GO COMMIT SPEC** (docs-only), puis premier build **`Sb_ASSET_01.1` Governance
Scaffold & Provenance Registry**.
