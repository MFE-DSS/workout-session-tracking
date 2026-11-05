# SCI-P01/02 — plan de réalisation des contrats isolés

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans, tâches exécutées ici et revue indépendante finale.

**Goal:** Fournir les DTO, schémas, fixtures et tests isolés approuvés, sans moteur servi.
**Architecture:** Module pur sous tools/science_contracts, Pydantic strict. JSON Schemas exportés depuis ses types ; fixtures avec provenance synthétique/legacy explicite. Les tests de contrats ne valident pas la dose historique et n'importent aucun producteur servi dans les DTO.
**Tech Stack:** Python3.11, Pydantic2 et pytest existants ; OpenSpec1.14.3.
**Spec:** design.md et specs/science/blueprint-first-plan/spec.md.

## Global Constraints

Aucun changement app/**, clients/**, data/**, migration ou dépendance. Aucun inventaire requis, UNKNOWN≠aucun matériel. Priorité≠faiblesse. Pas de nouvelle prescription issue de chiffres sans politique validée. Approbation opérateur : « Valider les contrats et tests isolés ».

## Review Focus

1. Faits facultatifs conflictuels non utilisés : visibles mais ne bloquent pas artificiellement.
2. Données complètes/politique absente : POLICY_UNAVAILABLE, pas demande de mesures supplémentaire.
3. Plan historique matériel inconnu : aucun READY, pas de compatibilité déduite d'un nom de salle.
4. Références/version/identités rompues et budget temps dépassé : rejet explicite.
5. JSON Schema et DTO cohérents, booléens refusés en cadence/quantité, traces de provenance et inconnus conservés.

## Task 1 — contrat et fixtures

**Files:** tools/science_contracts/blueprint_first_plan_v1.py ; tests/test_science_blueprint_first_plan_contracts.py ; docs/science/sci-p01-p02/v1/*.
**Interfaces:** Blueprint, FirstPlanRequest, FirstPlanRecommendation ; validate_exchange(request,response), decision_fingerprint(request) ; JSON Schemas générés. Fonctions de validation uniquement, aucun générateur de programme.
- [x] Tests RED sur absence de module ; fixtures suffisant/insuffisant/conflit/inconnu/mesure héritée et échanges invalides.
- [x] Implémenter DTO stricts, validators structurels et cross-references ; générer schémas.
- [x] Tests GREEN puis broad ciblé préférences/planification/environnement/catalogue ; ruff/budget/protocole/OpenSpec selon check_scope. Pas de full sweep local.

## Task 2 — handoff et livraison

**Files:** docs/science/sci-p01-p02/README.md, CONTRACT.md, HANDOFF.md, AUDIT_AND_EVIDENCE.md, audit_repo.json ; entrée SPEC_REGISTRY.
- [x] Finaliser contrats humains et table producteur/consommateur/versions/disponibilité, décisions opérateur et premier spike de politique à ouvrir.
- [x] Revue fraîche code/contrats ; corriger Important/Critical avec tests RED→GREEN ; relever mineurs.
- [ ] Commit/push/PR puis CI réelle ; merge par commit sous GO permanent après readiness et revue sans blocage ; CI canonique et closeout exacts, sans activation de moteur.
