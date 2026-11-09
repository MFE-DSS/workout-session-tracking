# PLAN-CAL-01 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Sept rencontres guidées réellement propriétaires alimentent le runtime V3 existant.
**Architecture:** Bundle privé inventaire2 parallèle, évaluateurs SCI immuables, projection qualifiée du ledger existant et un instrument natif commun.
**Tech Stack:** Python/SQLAlchemy, worker JSON isolé, TypeScript/Expo58.
**Spec:** design.md, BUILD_SCOPE.md, TEST_SPEC.md, UX_CAL_BOARD.md.

## Global Constraints

Sept tables existantes. Aucune migration, modification SCI/hashes historiques, fixture servie ou activation réelle. Primitives FrameC/RecessedWindow/NumericReadout existantes ; aucun rail E7, incrément universel ou charge calculée. Pixels avant commit UI. GOV-MERGE-01 reçu, pas de nouvelle question routinière.

## Review Focus

Imports différés/relatifs réellement attestés ; contexte courant explicitement sélectionné ; préoccupation globale non masquée ; nouveau réglage disponible invalidant ancienne qualification ; réponse perdue/A-B ne créant pas deuxième séance ou permission périmée.

### Task 1: Bundle inventaire2 et worker réel

**Files:** tools/plan_calibration_runtime_bundle.py, science_worker_v2.py, packaging.py ; tests/test_plan_cal_01_packaging.py.
**Interfaces:** build_bundle(destination,source)->digest ; execute_science autorités enrichies et calibration dispatchée par candidate_id ; anciens appels inchangés.
- [ ] Écrire tests vrai bundle7profils, opérations réelles, source drift, old bundle.
- [ ] Run check_scope puis tests ; Expected: nouveaux imports absents/RED.
- [ ] Implémenter builder/worker et sélection fixe du worker selon inventaire attesté.
- [ ] Tests ciblés packaging anciens+nouveaux ; Expected: PASS.

### Task 2: Acquisition et projection propriétaire

**Files:** calibration_profiles.py, calibration.py, snapshots.py, authority.py, evaluations.py, commands.py, execution.py, mobile_plan_v3.py ; tests/test_plan_cal_01_owned.py.
**Interfaces:** inventaire négocié ; sélection via événement propriétaire ; projection des épisodes guidés qualifiés ; empreinte runtime snapshot.
- [ ] Écrire tests HTTP nouvelle négociation, ouverture zéro réglage, sept rencontres réelles et nouveau choix/contexte/concern/retrait.
- [ ] Run ciblés ; Expected: RED pour capacité absente.
- [ ] Implémenter gardes et événements sous transactions existantes, lookup replay avant fraîcheur conservé.
- [ ] Tester sept→snapshot→V3→ack→start→response loss→même session et typed log ; Expected: PASS.

### Task 3: Contrôleur et instrument natif commun

**Files:** adaptateurs V3/calibration/blueprint/firstUse, PlanV3FirstUseScreen et sous-composants calibration, tests TS consommateurs.
**Interfaces:** inventory2 exact header/echo ; props source-mappées depuis owner envelope ; pas de nouveau contrat SCI.
- [ ] Tests de décodage/contrôleur A-B, pending, reprise, unités et motif explicite ; Expected: RED.
- [ ] Implémenter acquisition commune avec FrameC/RecessedWindow/NumericReadout, sans ±/rail, un CTA par étape.
- [ ] Tests et TypeScript ; Expected: PASS.
- [ ] Board consolidé de rendus natifs iOS/Android, tailles/clavier/a11y et sources ; demander pixels avant commit UI.

### Task 4: Livraison bornée

- [ ] check_scope puis Ruff/budget/spec/OpenSpec, ciblés+broad backend/mobile et garde visuelle selon tier ; Expected: PASS.
- [ ] Revues fraîches code et interface SCI, corriger Important reproduits RED→GREEN ; noter mineurs.
- [ ] Commit avec trailer opérateur, push/PR, contrôles exact HEAD, merge gardé ; CI canonique/Sonar réel.
- [ ] Archive/closeout sous même GO, CI canonique, cleanup seulement après absence travail unique ; CR autonome.

Les tâches ne sont committées qu'après pixels si leur diff contient UI. Autorisation du plan d'exécution déjà portée par GO BUILD, pas de GO supplémentaire nécessaire.
