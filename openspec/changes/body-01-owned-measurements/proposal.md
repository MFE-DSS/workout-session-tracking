> GO BODY-01/amendement/G1 reçu le 11 novembre 2026 : « Autoriser BODY-01, son amendement et G1 » (call_106057b169a74bc9887b1fea9f527f5d). Apply contrôlé en cours ; pixels non acceptés, aucune activation/release. Les statuts pré-GO ci-dessous gardent leur instant de préparation.

# Proposal — BODY-01 / mesures et corrections traçables

11 novembre 2026, base `3cf77e17f37448980b115d8e0e0adad783c1d0b2`.
**PROPOSED / NO_GO_BUILD / G1_PENDING / APPLY_CLOSED / NOT_SERVED_NATIVE.**

## Why
MOB-05A lit le poids daté ; le pilote doit saisir poids/tours et corriger sans perdre l'original. Mandat MVP : engineering merge, integration candidate et release externe séparés, aucun APK par sprint. Préparation existante révisée, pas dupliquée.

## What Changes
Famille native vers BodyMeasurement/BodyConsent : kg/cm/date/provenance et audit. Corrections par nouvelles versions dans BodyMeasurement ; sidecar metadata lignée/reçus/CAS, pas deuxième série numérique. Writers web/natifs et lecteurs courants partagés. Effacement individuel confirmé de toutes les versions distinct de correction et DATA global. Table locale de commandes exactes pour réponse perdue. Amendement canonique explicite CONTRACT_RECONCILIATION à approuver avec scope/G1. Graphiques Progrès réutilisés, pas nouvelle moyenne/inférence.

## Capabilities
### New Capabilities
- `mobile/owned-body-measurements` : acquisition manuelle datée, correction append-only, lecture courante/audit, reprise propriétaire.
### Modified Capabilities
- Fenêtre poids native : nouveau lecteur BODY source-aware/graphique existant ; poids v1 conserve forme/décodeur et filtre les têtes. Amendements corporels nommés, aucune exception tacite.

## Non-goals
Pas de second poids, profil/séance backdaté, moyenne, graisse/posture/score, import/photo/provider, NUT, nouveau moteur SCI, refonte MISSION/exécution/primitives/baselines. Pas APK/OTA/cloud/personnel/activation/déploiement. MULTIMODAL_ACQUISITION reste futur.

## Dependencies et completion
GO réel incluant amendement/migration additive/G1 ; pixels réels avant commit UI. Après GO : vrais consommateurs, guard commun, courses SQLite, migration/checks/CI/revue/merge GOV-MERGE-01. DATA/physique/release séparés. Engineering complet seulement avec création/correction/audit/effacement et Progrès sur vrai serveur, pas depuis mocks/formulaire.
