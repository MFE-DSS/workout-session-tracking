> État actuel12novembre : **GO TECHNIQUE reçu** « Autoriser le build technique NUT-01 », call_c1496d1a84e04b1a8dd61ad04f063aa6 ; [reçu exact](BUILD_AUTHORIZATION.json). Domaine/API/clients/recovery synthétiques en réalisation. G1/composition/pixels, intégration après BODY et activation/release restent des gates distinctes non satisfaites. Les formulations de préparation ci-dessous décrivent leur instant ; ne pas redemander ce GO ni lui attribuer une nouvelle UI.

# BUILD_SCOPE — NUT-01 manuel et cibles

**TECHNICAL_BUILD_AUTHORIZED / IN_PROGRESS / G1_PENDING / DATA_OPEN.** Build technique indépendant autorisé ; montage partagé et migration canonique séquencés après BODY. Pas de choix fournisseur requis pour le manuel.

## Delta proposé
Deux tables NutritionDayRevision/NutritionTargetRevision et une table locale nutrition_pending_commands_v1 ; journal agrégé quotidien déclaratif, corrections/audit/complétude, cibles STANDARD/TRAINING/REST choisies humainement, lectures/trend/export et reprise exacte. Support technique BodyConsent avec finalité nutrition_manual distincte ; aucune extension implicite de l'accord corporel.

## Leases proposés à figer avant GO
Nouveaux app/models/nutrition.py, services/nutrition_{commands,reads,consent}.py, routers/mobile_nutrition.py, tests domaine/API/reprise/migration ; migration additive nouvelle et schema snapshot. App models registration/routeur mobile composant réel/base garde non DDL. Natif api/nutrition.ts + resource/tests, ui/nutrition/*, storage/nutritionPendingCommands.ts + sync/nutritionRecovery.ts/tests. Partagés séquencés après BODY : ConnectedApp, ShellContext, routes/progres/profil, journal/journalTypes/web attachement local, modèles/export/cycle DATA applicable, registre/spec/manifeste MVP. Aucun PR simultané mêmes sources. Chemins mobile sous clients/mobile/src sauf ConnectedApp.

Avant GO final : figer les chemins effectifs et invariants SQL/index/FK ; revue builder du paquet. Si besoin partagé supplémentaire, revoir scope avant code. Le scope technique et ses leases sont maintenant fixés par EXECUTION_SCOPE_20261112 ; les leases UI partagés restent différés.

## Read-only
SCI/PLAN/calibrage/compte/exécution, BodyMeasurement/lecteurs de versions BODY, historique de séances MOB05, ownership/outbox/séries, thème/primitives/baselines/assets/tabs ; SDK/lock/EAS/CI/banc QA02. Aucun provider/SDK image/média/Capture/Extraction/HealthKit/calories activité.

## Gates
GO NUT/G1 réel, migration revue ; synthetic DB/app isolées. check_scope puis checks tier réel (migration attendu), broad+ciblés/migration/drift/snapshot/sweep local borné requis, mobile/TS/sécurité/visuel, revue indépendante, CI exacte. Pixels réels/acceptation humaine avant UI commit. GOV-MERGE-01 pour commit/push/merge/closeout du scope approuvé ; pas micro-GO merge. DATA/physique/RC/release séparés, pas runtime personnel/hosting/APK/OTA. Rollback coupe writes, garde lectures/audit/reçus ; aucune migration destructive.
