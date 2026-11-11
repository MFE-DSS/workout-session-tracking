# MOB-05A — scope soumis au GO BUILD

**NO_GO_BUILD / G1_PENDING / NOT_ACTIVATED.** Préparation documentaire seule autorisée. La tranche A remplace le protocole de deltas proposé antérieurement ; aucune règle historique n'a été changée.

## Fichiers propres futurs

- app/routers/mobile_training_history.py : quatre GET privés liste/détail/index/occurrences, Bearer/no-store, erreurs sans faits privés.
- app/services/training_history_reads.py : projection bornée, read_context/références signées/owner/period counts/weekly counts, identité exacte, scanner lots200/plafond1000 ; pas de moteur de progression.
- clients/mobile/src/api/trainingHistory.ts et trainingHistoryResource.ts : DTO stricts, dispatch V3 read-only avec validation additionnelle, mémoire/A-B/pagination/unknown.
- clients/mobile/src/ui/history/TrainingHistoryScreen.tsx, SessionFactsScreen.tsx, ExerciseHistoryScreen.tsx, WeightTrend.tsx, historyView.ts : même famille Progrès compacte et charts RN/SVG existants accessibles ; poids via vrai client/resource existants.
- tests/test_mobile_training_history_http.py et test_training_history_reads.py ; tests client/resource/consommateurs dans mêmes répertoires que modules.
- Preuves docs/pilot/mob05a-progress-core/ et clients/mobile/visual-contract/review-receipts/mob05a-progress-core/, chemins exacts inventoriés avant ajout ; aucun manifest/baseline modifié.

## Leases partagés limités, exclusifs et séquencés

- app/routers/mobile_api.py : inclure router seulement, pas writer/starts/recap.
- clients/mobile/ConnectedApp.tsx : instancier les lectures au owner actuel, progress node et invalidations ; aucun refactor séance/calibrage/journal.
- clients/mobile/src/shell/ShellContext.tsx : node progress optionnel ; src/routes/progres.tsx : consommateur réel et retour des niveaux internes, pas tabs layout.
- clients/mobile/src/sync/connectedApp.test.ts : vrai wiring et A/B.
- docs/strategy/SPEC_REGISTRY.md : append de ce scope seulement ; openspec/specs/mobile/feature-migration-map/inventory.yaml : rattacher les quatre routes réelles, aucune exemption de gate ou fonctionnalité nouvelle hors scope.
- Le seul change openspec/changes/mob05-owned-training-history/ ; archive par CLI après merge. Pas de second change MOB05A concurrent.

Séquence composition : **REL03 merge → MOB04 merge → MOB05A**, nouvelle lecture/fetch avant chaque lease partagé ; préparation indépendante et tests de modules propres possibles après GO. Pas PR chevauchante sur ConnectedApp/mobile_api/registre. BODY/NUT gardent leurs propres propositions et ne démarrent pas dans ce build.

## Read-only / interdits

app/models/**, migrations/**, data/schema_snapshot.sql ; tous writers/restore/export, body_profile/mobile_body/BodyMeasurement, weightHistoryClient/Resource, programme/planning/recommandations ; app/services/exercise_history.py et delta.py (anciens calculs web conservés), PLAN/SCI/V3/SDK/JSON historiques/journal/outbox/auth, thème/primitives/UI LOCKED/baselines, package/lock/deps et CI. L'import est autorisé. Si extension nécessaire hors liste : documenter le delta, pas copier une règle ni élargir silencieusement.

## Définition de fin / gates

GO du design/scope et G1 familial ; tests RED→GREEN ciblés et broad des consommateurs requis par check_scope, vraie CI et revue indépendante, vrais rendus iOS/Android et acceptation avant commit UI. Livraison du code via GOV-MERGE-01, merge gardé/CI canonique/Sonar réel/closeout. Preuve en app avec backend synthétique isolé et artefact supporté, APK QA02 ne contient pas la nouveauté et ExpoGo incomplet ne la prouve pas. Distribution externe/OTA/hébergement/DATA restent des permissions distinctes ; aucune activation corporelle réelle ne découle de la lecture poids.
