# Contrats scientifiques v2 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement task-by-task.

**Goal:** Livrer les contrats v2 exécutables, leurs schémas/fixtures non servies et validations sans modifier v1 ni admettre une politique.
**Architecture:** Faits Blueprint/provenance et observations typées réutilisés. Nouveaux modèles v2 purs séparés de leur validation d'échange ; l'autorité disponible reste le registre piné vide existant, donc aucun READY validé/servi. Aucun nouveau producteur scientifique négatif ou positif.
**Tech Stack:** Python/Pydantic/pytest existants ; JSON/SHA256 ; pas dépendance nouvelle.
**Spec:** openspec/changes/archive/2026-11-07-science-initial-policy-positive-admission/design.md et BUILD_AUTHORIZATION.md.

## Global Constraints
- V1, code/artefacts v2 historiques, FirstPlanClient, registres/pins/APP/UI inchangés.
- UNKNOWN ne devient ni zéro/crédit ni absence physiologique ; quinze zones complètes déclarées seulement.
- Réglage observé/bootstrap à union typée, provenance actuelle ; aucun kg/temps froid ou score inventé.
- READY exige gates réelles et durée complète admise ; registre courant vide ne peut jamais le valider.
- Fixture de contrat n'est pas sortie d'un producteur admis : aucun READY public ou autorité de test promue.
- Scopecheck avant vérification, broad science ciblé sans full local ; CI obligatoire HEAD et canonique après merge.

## Review Focus
- Models construits/copiés sans validation et nested bool/int/nonfinite (Task1/2).
- Identité/contexte/réalisation/as_of et changement d'observation distinct du fingerprint des faits (Task1/2).
- Quinze zones UNKNOWN et contributions dupliquées/étrangères (Task1/2).
- Bootstrap incomplet, ancien réglage/acceptation réimportés, unité/side non représentable (Task1/2).
- Faux binding ou champs READY malgré registre vide/durée inconnue (Task2/3).

### Task 1: Modèles et empreintes v2
**Files:** tools/science_contracts/blueprint_first_plan_v2.py ; tests/test_science_blueprint_first_plan_v2_contracts.py.
**Interfaces:** FirstPlanRequestV2, FirstPlanRecommendationV2, PlanV2, Prescription unions, Duration unions, ZoneReport ; request_fingerprint(request)->str ; evaluation_fingerprint(request)->str ; exported_schemas()->dict.
- [ ] Tests RED des discriminants/UNKNOWN/unités/quinze zones/identités/temps/empreintes.
- [ ] Implémenter validation structurelle stricte ; réutiliser Blueprint v1, CalibrationEpisode et Setting, pas écrire de nouveaux faits.
- [ ] Revalider les modèles copiés avant frontière/fingerprints ; ordre sémantique stable, priorité ordonnée préservée.
- [ ] GREEN ciblé puis commit.

### Task 2: Validation d'échange et autorité absente
**Files:** tools/science_contracts/first_plan_v2_validation.py ; même test dédié.
**Interfaces:** validate_exchange(request,response,*,trusted_bundle,admission_registry)->FirstPlanRecommendationV2.
- [ ] RED refus mauvais subject/snapshot/versions/fingerprints, assessment faux, fake binding/READY, contexte/exercice étranger et provenance incohérente.
- [ ] Vérifier références avec le vrai bundle piné et registre d'admission vide inchangé. Préserver conflit→manque→policy et raisons utiles.
- [ ] Contrôler les références de plans, réglages réellement observés/reconfirmés et qualité de durée ; la forme n'accorde pas l'autorité.
- [ ] GREEN échange et contrats historiques, commit. Aucun positif revendiqué depuis une autorité hypothétique.

### Task 3: Artefacts, livraison et CR agent
**Files:** tools/science_contracts/first_plan_v2_fixtures.py ; docs/science/sci-p01-p02/v2/ ; reçu sous positive-admission-01 et registre/change du seul scope.
**Interfaces:** artifacts()->dict[str,bytes] ; génération explicite --write, vérification par défaut.
- [ ] RED nouveaux artefacts manquants, puis vrais cas contrats suffisant/insuffisant/conflit/unknown/withheld et altération refusée ; pas READY public.
- [ ] Générer schémas/fixtures déterministes et manifeste des sources/code ; préserver anciens exports.
- [ ] Checks tier ISOLATED, broad science/consommateurs ; revues code/science distinctes, Important RED→GREEN si besoin.
- [ ] Publication/CI/merge sous GO permanent puis contrôles canoniques, Sonar réel et closeout du seul contrat ; preuves/cleanup.
- [ ] CR complet pour l'agent : réalisé/servi/nonservi, versions/SHA/tests/PR, données/décisions exactes C3/C6, autres gates DATA/PLAN/RELEASE préservées, prochaine injection bornée.

## Rulings
Le GO explicite couvre le design proposé et son exécution native ; pas de nouvelle question de plan. Noms supplémentaires de modules de validation/génération sont la décomposition locale du fichier de contrat, pas une refonte du repo. Le registre actuel vide demeure le seul profil d'autorité disponible ; les tests structurels ne simulent pas un binding réellement admis.
