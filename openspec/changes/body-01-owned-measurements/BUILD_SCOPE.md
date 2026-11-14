> GO BODY-01/amendement/G1 reçu le 11 novembre 2026 : « Autoriser BODY-01, son amendement et G1 » (call_106057b169a74bc9887b1fea9f527f5d). Apply contrôlé en cours ; pixels non acceptés, aucune activation/release. Les statuts pré-GO ci-dessous gardent leur instant de préparation.

# BUILD_SCOPE — BODY-01 révisé MVP

**NO_GO_BUILD / G1_PENDING / APPLY_CLOSED / DATA_OPEN / PHYSICAL_OPEN / NOT_ACTIVATED.** Préparation documentaire uniquement actuellement ; pas code/test exécutable/install/migration/commit/push.

## Paquet proposé
GO unique sur CONTRACT_RECONCILIATION, design B01–B08 et G1 : versions dans BodyMeasurement, sidecar metadata, table locale de tentatives, writers/lecteurs communs et effacement individuel des versions sur synthétique. Migration additive sans backfill/rebuild ; SQLite fichier initialement. Pas moyenne7j.

## Leases après GO
| Bloc | Fichiers / portée |
|---|---|
| Normatif | docs/strategy/Sx_MORPHO_CAPTURE_01_SPEC.md §2.1 ; SPIGNOS_BODY_MANUAL_PROFILE_BUILD_SPEC.md correction/effacement ; SPIGNOS_BODY_PRIVACY_AND_CONSENT_SPEC.md correction/effacement/reliquat DATA ; specs OpenSpec mobile concernées/registre |
| Nouveaux | app/models/body_measurement_operation.py ; app/services/body_measurement_commands.py et body_measurement_reads.py ; app/routers/mobile_body_measurements.py |
| Writers | app/services/body_profile.py helpers/wrappers/export ; app/routers/body.py ; auth_routes.py profile_measurements_submit uniquement |
| Lecteurs | app/services/body_ledger.py, morphology_runtime.py, body_intelligence_inputs.py, measurements.py, muscle_scoring.py, dashboard.py, coach_report.py : éligibilité des têtes, pas formule/règle scientifique |
| Schéma/branchement | app/models/__init__.py ; app/database.py garde zéroDDL startup ; composition effective du routeur mobile à figer préflight ; une migration body_measurement_operations_01 head à relire ; data/schema_snapshot.sql |
| Web minimal | templates/body_assessment/measurement_form.html et body_overview.html : token/portée/confirmation, pas refonte |
| Natif | api/bodyMeasurements.ts, ressource/tests ; ui/body/BodyMeasurementsSurface.tsx, MeasurementSheet.tsx, BodyFamilyBoard.tsx ; modèles de présentation stricts |
| Local | storage/bodyPendingCommands.ts ; sync/bodyCommandRecovery.ts et tests ; table BODY unique dans partition/connexion possédée |
| Composition | ConnectedApp.tsx ; routes/progres.tsx et profil.tsx ; shell/ShellContext.tsx ; ui/history/WeightTrend.tsx et consommateur fenêtre poids : provenance réelle, historique séances inchangé |
| Attachement | storage/journal.ts, journalTypes.ts, journal.web.ts extension BODY typée ; ownership.ts/ownershipStore.ts inchangés |
| Tests | nouveaux commandes/lecteurs/API/migration + consommateurs body/profile/poids/ledger/morphology/BI/dashboard/coach/scoring ; client/resource/local/consommateur/visuel, sans affaiblissement |
| Livraison | docs/pilot/body-01/* ; docs/pilot/mvp-integration/* et politique documentaire des trois jalons ; aucun workflow REL-03 modifié |

Chemins mobile relatifs clients/mobile/src sauf ConnectedApp. Noms internes/routeur effectif à fixer préflight, pas nouveaux contrats. Writer/lecteur hors liste ou source pinée incompatible =>revoir lease avant code. NUT/MOB06 partagés séquencés, aucune PR chevauchante.

## Read-only et exclusions
measurement.py aucune colonne/PK/rebuild/AUTOINCREMENT ; User/session ; contrats/engines/registres/hashes SCI/PLAN ; weightHistory.ts décodeur/DTO v1 ; historique séances MOB05 ; ownership ; tables PLAN/outbox/journal_sets/active_session ; tokens/primitives/assets/baselines/tabs ; SDK/lock/EAS/CI/banc QA02. Pas import/photo/provider/NUT.

## Gates
1. GO explicite unique amendement/scope/G1. Pas nouvelle question sur la direction déjà reçue.
2. Préflight canonique/writers/lecteurs/pins/forme migration. DB/app synthétiques isolées, aucun backend partagé.
3. check_scope avant checks, migration attendue : ciblés/broad/migration/drift/snapshot/sweep local borné requis ; jamais pytest -n auto. Vrais HTTP/DBfichier/natif, revue indépendante, CI HEAD final/sécurité/OpenSpec/visuel ; Sonar réel consultatif.
4. Pixels réels natif et petit delta SSR comparés LOCKED, acceptation avant commit UI.
5. Merge/closeout GOV-MERGE-01 sans GO routinier. Engineering ≠ distribution.
6. DATA pour copies/reçus/réservations/export/effacement/backups/local ; physique/activation/release séparés, pas durée/conformité déduite.

Rollback : couper nouveaux writes, garder lectures source-aware/audit/réconciliation/effacement autorisé. Ancien lecteur brut incompatible avec lignées corrigées ; pas de down destructif ni perte de version. Rollout/backup/compatibilité éprouvés sur copie, déploiement réel séparé.

## Leases techniques réconciliés pendant FINAL DELIVERY
Le mandat de reprise autorise les réparations précises du sweep : CSS locale `app/static/css/body_measurements.css`, inventaire MOB00 `openspec/specs/mobile/feature-migration-map/inventory.yaml`, fixtures BI/capture, sentinelle EKB head+parent, garde Worked Area avec quatre chemins exacts BODY, tests CP7.5A et ratchet inline 21→20. Aucun pixel de référence modifié. Le raccordement réel utilise AccountPages et TrainingHistoryHost/Screen ; pas besoin de nouvelles routes de shell ni d’un composant galerie BodyFamilyBoard. Le test `sync/bodyConnectedApp.test.ts` monte le vrai ConnectedApp avec SQLite fichier et transport réel client à frontière HTTP synthétique.
