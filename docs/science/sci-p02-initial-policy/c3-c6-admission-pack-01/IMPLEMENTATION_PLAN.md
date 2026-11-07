# C3/C6 v3 isolé — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Réaliser le contrat v3 et les types C3/C6 sans autorité positive ou runtime.
**Architecture:** Réutiliser faits/observations/PlanV2 et la borne partielle de repos existante. Nouveaux types purs pour science/temps/permission et protocole ; frontière d’échange sur les vrais bundle/registre vide ; artefacts de refus non servis.
**Tech Stack:** Python/Pydantic/pytest existants, JSON/SHA256, aucune dépendance nouvelle.
**Spec:** openspec/changes/archive/2026-11-07-science-c3-c6-bootstrap-readiness/design.md et BUILD_AUTHORIZATION.md.

## Global Constraints
- Anciens modèles/registres/hashes/artefacts et FirstPlanClient inchangés ; pas app/API/UI/DB/collecte/activation.
- Aucun kg/temps/incrément/seuil d’apprentissage nouveau ; plateau de réglages fourni avec sens d’effort sourcé.
- Temps inconnu distinct de science et permission ; vrai registre vide ne valide aucune science positive ni permission ELIGIBLE.
- Ack lie sujet/snapshot/révision/requête/observations/plan+temps/politique et instant ; jamais authentification depuis JSON seul.
- UNKNOWN ne devient ni zéro, grade biologique, vraie2RIR ou durée supportée.
- TDD, scoped broad et CI HEAD/canonique, revues distinctes, standing merge seulement du scope complet.

## Review Focus
- Modèles copiés/nonfinite/bool et métadonnées d’ack au mauvais propriétaire/plan/date.
- Repos égaux au budget, supersets/paire inconnue et faux classement positif sous borne partielle.
- Essai interrompu/effort inconnu et réglages d’assistance à ordre d’effort opposé à l’ordre numérique.
- SCIENTIFICALLY_READY structurel pris pour autorité ; labels d’admission/ack du caller refusés par échange réel.
- Rejeu historique et sources pinées, exemples hypothétiques jamais importés/servis en produit.

### Task 1: Types C3 et état temporel C6
**Files:** tools/science_contracts/bootstrap_protocol_v3.py ; tests/test_science_bootstrap_protocol_v3.py.
**Interfaces:** CalibrationProtocolV3, TrialReviewV3, SettingTransitionV3, TimeAssessmentV3 ; assess_structural_time(session,budget_minutes,structure)->TimeAssessmentV3.
- [ ] RED tests quatre phases, source/occurrence/contextes et effort absent, cause interruption non causale, préoccupations, transitions disponibles/unité/sens d’effort, tempsR=budget/R<budget/structure non supportée.
- [ ] Implémenter types/validations purs ; réutiliser Setting/ContextKey/Provenance et assess_time existants, pas produire de décision scientifique d’ajustement.
- [ ] GREEN dédié et temps/calibration historiques, Ruff/protocole, commit.

### Task 2: Contrat v3 et frontière d’échange
**Files:** tools/science_contracts/blueprint_first_plan_v3.py ; tests/test_science_blueprint_first_plan_v3_contracts.py.
**Interfaces:** FirstPlanRequestV3 (faits v2, contrat3 et ack facultatif), FirstPlanRecommendationV3, TimeAcknowledgmentV3 ; request_fingerprint, observation_fingerprint, evaluation_fingerprint ; plan_time_fingerprint ; validate_exchange(...,trusted_bundle,admission_registry).
- [ ] RED tests axes orthogonaux, permission refusée sans autorité, ack lié à toutes références et date, politique/source inadmissible, manque/conflit et compatibilité versions, bool/copies.
- [ ] Implémenter modèles séparés du résultat v2. Requêtes converties uniquement pour réutiliser validation négative v2 interne, jamais un transport/downcast READY.
- [ ] Empreinte facts sans observations/ack, observations sans ack, complète avec ack ; pas de référence circulaire dans ack. Plan/time_fp lie toutes données utilisées pour la reconnaissance.
- [ ] GREEN dédié et contrats historiques, commit.

### Task 3: Artefacts, revues et livraison
**Files:** tools/science_contracts/first_plan_v3_fixtures.py ; docs/science/sci-p01-p02/v3/ ; reçu/handoff de ce seul scope, registre/OpenSpec.
**Interfaces:** artifacts()->dict[path,bytes], CLI --write explicite, vérification par défaut.
- [ ] RED artefacts absents, puis exporter schémas/protocole/exemples non servis, manifeste sources/code, aucune fixture READY réelle ou registre positif.
- [ ] Contrôler scope avant checks, broad science/contrats/consommateurs selon tier ; anciens fichiers byte-identiques.
- [ ] Revue fraîche code et SCI distinctes, Important corrigés RED→GREEN ; dette Sonar factuelle, pas de seuil modifié.
- [ ] Commit/push/PR/CI HEAD puis merge sous GO permanent et canonique ; archive/closeout du seul stage1, étapes2/3 ouvertes. Preuves et cleanup seulement own worktree/branches sans travail unique.
- [ ] Reçu complet des versions/SHA/preuves et prochain scope scientifique/runtimes réel ; aucune fermeture MOB03 ou activation déduite.

## Choix d’exécution
Exécution native en continuité de session selon le GO reçu ; plan ne réouvre pas les décisions humaines. Décomposition en modules nouveaux et empreinte d’observation distincte sont choix locaux de réalisation, sans nouvelle autorité ou protocole numérique. Les deux revues finales sont des contrôles indépendants du scope, pas une admission biologique.
