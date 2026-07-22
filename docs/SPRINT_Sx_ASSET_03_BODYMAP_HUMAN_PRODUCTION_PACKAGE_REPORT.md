# Sprint Sx_ASSET_03 — BodyMap Human Production Package — SPEC REPORT

**Statut** : 🟢 **SPEC RÉDIGÉE / READY FOR GO COMMIT**
**Type** : SPEC / PRODUCTION PACKAGE / OFFICIAL-SOURCE RESEARCH — **DOCS-ONLY** (0 SVG/image/app/asset/test)
**Date** : 2026-07-22 · **Baseline** : `cf41188` (closeout Sx_ASSET_02) ; posé sur HEAD réel `062ee92`.

> **Le master BodyMap n'est PAS produit.** Ce cycle produit le **package de production** (comment produire),
> pas la silhouette. `BODYMAP SEMANTIC CONTRACT` immuable. `ASSET INTEGRATION GATE: BLOCKED`.

---

## 1-4. Baseline / worktree / collisions / idempotence
HEAD canonique `062ee92` (avance Custom EKB_03 PR closeout après `cf41188`, **indépendante**, 0 fichier
BodyMap/Sx_ASSET_03). `cf41188` ancêtre. Worktree isolé sur `062ee92`. Aucune spec Sx_ASSET_03 préexistante.

## 5-8. Sources auditées & états
`Sx_ASSET_01`/`Sx_ASSET_02` **CLOSED** (registry). Contrat sémantique BodyMap **immuable** (11 zones/6 macros/
14 IDs/5 états/`unknown`/séparation `RADAR_AXES`). Prototype runtime audité (lecture seule) : `viewBox 0 0 60
100`, formes circle/rect, `_WA_ZONE_TO_REGION`, `aria-hidden`, no-JS, consommé par exercise_card — **prototype
à remplacer après gate, 0 modif**. Garde actuel : évolution future = `Sb_ASSET_03.2`.

## 9. Brainstorming (§8)
`SEMANTIC CONTRACT FIRST · ORIGINAL HUMAN MASTER · MALE_NEUTRAL_V1 P0 · FRONT+BACK ORTHOGRAPHIC · 11 ZONE
GROUPS · 6 MACROS · NO ZONE-UNKNOWN · NO AI ANATOMICAL GROUND TRUTH · BODYPARTS3D REFERENCE NOT DERIVATION ·
ANATOMYTOOL RESOURCE-BY-RESOURCE · FULL SOURCE DISCLOSURE · PROFESSIONAL LEGAL REVIEW NOT CLAIMED · ANATOMICAL
& MOBILE REVIEW REQUIRED · NO APP INTEGRATION · GATE BLOCKED`.

## 10-14. Décisions clés
- **Variante V1** : `male_neutral_v1` (P0) ; female/abstract/latérale = P2 non produits.
- **Direction artistique** : instrument biomécanique, non médical/gamer/IA ; lisible 60/80/120/360 px.
- **Grille tranchée** : **viewBox `0 0 240 200`** (face centre 60 / dos centre 180 / gouttière) — non laissé à
  l'illustrateur, justifié (côte-à-côte 360, export compact, testabilité).
- **Structure SVG** : 14 IDs stables figés · **1 `<g id="zone-*">` unique/zone** · convention IDs enfants
  `geom-<zone>-<view>-<side>-<index>` (technique, n'affecte pas Layer A) · 0 `zone-unknown` · 0 path partagé.
- **Agrégats honnêtes** : `upper_back`/`posterior` = functional-aggregate (pas de précision excessive).
- **États** : 5, jamais couleur seule, couleur runtime ; `unknown` = 0 anatomie active.
- **Accessibilité** : décoratif, texte adjacent = vérité, 0 texte/interaction/focus dans le master.

## 15-17. Due diligence références & IA & PI
- **BodyParts3D** (DBCLS, source officielle 2026-07-22) : **CC BY-SA 2.1 Japan** (ShareAlike) → **référence
  spatiale uniquement, dérivation écartée** ; `LEGAL CLASSIFICATION PENDING`.
- **AnatomyTOOL** : licence **par ressource** (qualifier chacune ; NC/étudiant écartés).
- **IA** : moodboard uniquement, jamais vérité anatomique ; déclaration obligatoire ; géométrie non déclarée =
  livraison bloquée.
- **PI** : `PROCUREMENT / LEGAL REQUIREMENTS CHECKLIST` (pas un contrat) ; jamais « Auren owns the master »
  avant signature+sources+revue ; statuts `contract-requirements-defined`/PENDING.

## 18-20. Package illustrateur / manifest / protocole revue
Livrables (master SVG + source native hashée + références + déclarations + previews) ; template manifeste (17
champs, **0 approved**, statuts `not-started`/`professional-review-required`) ; protocole revue anatomique
(compétence documentée, **≠ validation médicale**, verdict par zone) + produit/mobile (360 + 60/80/120,
non-régression logging) + **32 previews bornées**.

## 21-25. Contrat intake futur / budgets / gate / metadata
`Sb_ASSET_03.2` : validations préparées (non implémentées ; 0 test modifié). Budgets par artefact (compact ≤
12 Ko bloquant ; source native aucun budget). Gate **BLOCKED** conservé. Note **§31** : synchro metadata
iconographique requise avant Sx_ASSET_04, **sans rouvrir Sx_ASSET_02** — ne bloque pas Sx_ASSET_03.

## 26. Livrables créés (12 fichiers, 100% docs)
Créés : `strategy/Sx_ASSET_03_..._SPEC.md` · ce rapport · `research/AUREN_BODYMAP_REFERENCE_DUE_DILIGENCE.md` ·
`production/bodymap/` ×6 (INDEX · ILLUSTRATOR_BRIEF · SVG_STRUCTURE_AND_DELIVERY_CONTRACT · IP_PROVENANCE...
· ANATOMICAL_PRODUCT_MOBILE_REVIEW_PROTOCOL · DELIVERY_MANIFEST_TEMPLATE). Modifiés : `SPEC_REGISTRY.md` ·
`ROADMAP_AND_NEXT_STEPS.md` · `AUREN_ASSET_PROGRAM_ROADMAP.md`.

## 27-28. Scope / confirmations
**0** `design/**` (pas de `references/`, pas de `auren_bodymap_master.svg`, pas de `previews/bodymap/`, pas
d'`exports/`) · **0** `tests/**` · **0** `app/**` · **0** binaire/image/font/asset/licence copiée · **0**
fichier Custom. Documents Sx_ASSET_01/02 historiques non modifiés (hors registry/roadmaps).

## 29-30. Git & statut
Working tree du worktree propre. **Non committé** (point d'arrêt §33).
🟢 **SPEC RÉDIGÉE / READY FOR GO COMMIT.**

---

## Verdict

**Verdict :** 🟢 **Sx_ASSET_03: SPEC RÉDIGÉE / READY FOR GO COMMIT.** Package de production humaine du master
BodyMap défini et exécutable : brief illustrateur (male_neutral_v1), contrat SVG tranché (viewBox `0 0 240
200`, 14 IDs, `<g>`/zone, 0 zone-unknown), exigences PI/provenance (checklist, pas un contrat), protocole de
revue (anatomique ≠ médical + produit/mobile + 32 previews bornées), manifest template (0 approved), contrat
`Sb_ASSET_03.2` préparé, budgets par artefact. Due diligence datée : **BodyParts3D CC BY-SA = référence
spatiale uniquement** (dérivation écartée), AnatomyTOOL ressource-par-ressource. **Master NON produit** ;
contrat sémantique immuable ; **12 fichiers 100% docs** ; 0 design/tests/app/asset/Custom ; `ASSET INTEGRATION
GATE: BLOCKED` ; `PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED` ; `Sx_ASSET_01/02` CLOSED.

**Prochaine action** (séparée, non commencée) : `GO COMMIT SPEC — Sx_ASSET_03 BodyMap Human Production Package`.
