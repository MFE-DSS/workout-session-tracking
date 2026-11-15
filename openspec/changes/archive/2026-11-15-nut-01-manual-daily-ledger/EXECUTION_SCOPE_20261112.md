# NUT-01 — scope exécutable proposé

12 novembre2026. Préparation restaurée, pas encore GO BUILD. Le contrat manuel/cibles et ses gates restent ceux du change existant ; [PERSISTENCE_AND_COMMANDS](PERSISTENCE_AND_COMMANDS.md) ferme les détails SQL/concurrence/couverture.

## Séquence et fichiers possédés
1. Domaine/backend synthétiques : nouveaux `app/models/nutrition.py`, `app/services/nutrition_commands.py`, `nutrition_reads.py`, `nutrition_consent.py`, `app/routers/mobile_nutrition.py`, `migrations/versions/nutrition_manual_01.py` ; montage dans `app/routers/mobile_api.py`, flag fermé dans `app/config.py`, enregistrement `app/models/__init__.py`, exclusion DDLstartup dans `app/database.py`, snapshot `data/schema_snapshot.sql`. Parent BODY obligatoire avant migration applicable. Route inventory via les features nutrition existantes, sans VERIFIED_NATIVE anticipé.
2. Vrais clients/stockage/reprise : nouveaux `clients/mobile/src/api/nutrition.ts`, `nutritionResource.ts`, `storage/nutritionPendingCommands.ts`, `sync/nutritionRecovery.ts`, tests dédiés. Partagés journal.ts/journal.web.ts/journalTypes.ts : attachement d'une table et partition existante seulement ; aucun changement du contrat de séries. Tests backend `test_nutrition_{commands,api,reads,consent,migration}.py` et consommateurs.
3. Consommateur natif dans Progrès et détails/cibles/jour, source/new ui/nutrition ; points partagés ConnectedApp.tsx et TrainingHistoryHost.tsx sous lease séquencé après BODY. Aucun chevauchement de PR. La grammaire de composition BODY demeure suspendue : pas d'invention autonome d'un nouveau cockpit NUT. G1/composition/pixels NUT restent à accepter avant intégration UI correspondante/commit. Le GO domaine ne devient pas un GO de nouvelle géométrie.
4. Documentation change/spec/registre/inventaire/copies et manifeste candidat ; tests/ciblés/broad/full migration/migrationchecks/mobileTS/sécurité/revue indépendante/CI exactes puis merge autonome GOV-MERGE-01 une fois TOUTES les gates applicables satisfaites.

## Deux états de permission à distinguer
Le GO demandé ici autorise le build contrôlé du domaine NUT manuel, cibles, API, clients et recovery sur données synthétiques, ainsi que leurs tests. La livraison verticale complète reste l'objectif du même change ; la composition native et son G1/pixels sont encore des gates réelles. Pas de nouveau GO routine pour merge/corrections/closeout dans ce scope. Pas de scienceprescriptive, média/provider, nouveau tab, modification de primitiveLOCKED, configurationEAS, APK/OTA, remote migration, donnée personnelle ou déploiement.

## Définition de COMPLETE
Jour/cibles réellement acquis et relus dans ConnectedApp via HTTP et SQLite serveur/local, ownership/concurrence/dates/null/corrections/completeness/couverture/recovery éprouvés, master/composition accepté et rendus réel iOS/Android selon capacités, contrôles et CI finaux verts/revue, PR et merge vérifiés. Sans consommateur ou gate visuel : backend préparé/validé, jamais COMPLETE/parité native prétendue.

Le protocole fermé WIRE_AND_READ_PROTOCOL.md répond àR1–R5 et prévaut sur les formulations de transport/consent/pagination imprécises du premier design. Les CHECK entiers/booleans et liens parentrevision valent pour DAY ET TARGET.
