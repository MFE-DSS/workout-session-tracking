# SCI-P01 / SCI-P02 — contrats du Blueprint et du premier plan

## Why

MOB-03/04 attendent des contrats distinguant données utilisateur suffisantes, politique de prescription validée et faisabilité d'exécution. Le dépôt possède déjà des générateurs, un planificateur hebdomadaire web et un catalogue scientifique ; leur existence ne prouve ni personnalisation scientifique ni respect d'une durée de séance.

Mandat opérateur du 5 novembre 2026 : livrer SCI-P01/02, schémas versionnés, fixtures suffisantes/insuffisantes/conflictuelles, tests, dépendances, état servi/proposé et arbitrages. Pas d'inventaire matériel obligatoire, pas d'équipement complet supposé.

## What Changes

- Auditer les sources canoniques et les 18 gabarits de `reference_split.json`, ainsi que la chaîne de planification réellement exposée sur le web.
- Définir BodyTrainingBlueprint v1 : faits typés, provenance et inconnus, utilité conditionnelle des mesures, préférences distinctes d'observations, suffisance évaluée sans score arbitraire.
- Définir FirstPlanRecommendation v1 : résultat déterministe versionné, contraintes/temps/allocation/slots/candidats, compatibilité et alternatives, explication et incertitude ; séparer insuffisance d'inputs et indisponibilité de politique.
- Livrer un module de DTO/validation **isolé et non importé par app/**, ses JSON Schemas et fixtures de contrat ; aucun algorithme de prescription ou nouvel endpoint. Les fixtures de plan historique restent des exemples à revoir, pas des prescriptions approuvées.
- Handoff lisible et table des décisions nécessaires avant adoption par le mobile. La validation de cette proposition autorise seulement ces artefacts et leurs tests, pas l'activation d'un moteur.

## Non-goals

Aucune UI, baseline, identité visuelle, migration, table, champ serveur partagé, endpoint, écriture de données, curation de catalogue, nouvelle constante de prescription, calibration, photo, nutrition ou diagnostic. Aucun remplacement silencieux du planificateur ou de la recommandation servis. Aucun déploiement.

## Capabilities

### New Capabilities
- `science/blueprint-first-plan` : contrats documentés et vérifiables, non servis.

## Impact

Fichiers dédiés : `docs/science/sci-p01-p02/`, `tools/science_contracts/`, `tests/test_science_blueprint_first_plan_contracts.py`, ce change et entrée étroite du registre de specs. Références en lecture seule à `app/services/`, `app/models/`, `data/`. Manifeste reçu recopié exactement depuis la PR mobile #353 (commit2ba9fd4) car il n'est pas encore dans la base canonique90da846 ; aucune dépendance au code non mergé de cette PR.

## Approval boundary

Statut initial : **PROPOSED**. Audit et rédaction autorisés par le mandat ; validation opérateur de proposition/design avant réalisation du module de contrats et tests. Aucune autorisation d'implémenter une prescription n'est déduite de la validation du contrat. PR distincte ; CI/merge selon CLAUDE et GO permanent une fois les gates applicables remplies.
