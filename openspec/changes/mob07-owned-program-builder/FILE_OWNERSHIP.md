# MOB-07 — fichiers possédés et leases à acquérir

Parent59a28dc, branche spec/mob07-owned-program-builder, même worktree /Users/martinfeldmann/auren-review/mob06-library-20261112. Au15novembre : seules la proposition et son entrée de registre sont modifiées. BODY/NUT/MOB06 sont fusionnés ; aucun writer de ces agents n’est repris. Les inspections REL03/DA08 sont read-only dans des dossiers extérieurs.

## Sources nouvelles proposées
- app/models/program_builder_operations.py : métadonnées/reçus, sans seconde prescription.
- migrations/versions/program_builder_operations_01.py : additive après nutrition_manual_01 ; app/models/__init__.py et data/schema_snapshot.sql pour registration/snapshot.
- app/services/program_builder_commands.py : kernel partagé transaction/replay/CAS/quota.
- app/services/mobile_program_builder.py : readmodel/projection/picker/DTO, pas science nouvelle.
- app/routers/mobile_program_builder.py : Bearer/négociation/bornes owner.
- clients/mobile/src/api/programBuilder.ts, storage/programBuilderPendingCommands.ts, sync/programBuilderRecovery.ts : frontières typées et reprise.
- clients/mobile/src/ui/programs/ProgramBuilderScreen.tsx et présentateurs nécessaires : famille DA08 acceptée, un seul instrument actif.

## Leases partagés nécessaires, même PR après GO
- app/services/user_program_drafts.py, user_program_publish.py, user_program_versioning.py, program_quality_reviews.py : hooks commit/flush et entrée kernel, sans formule modifiée.
- app/services/weekly_plan_materialization.py : regrouper création/arbre dans la même transaction ; plan/générateur restent autorités conservées.
- app/routers/user_programs.py et templates user_programs/new.html, detail.html, generate.html, publish.html, list.html : précondition/CAS et actions sérialisées ; pas nouvelle composition web. plan.html seulement si son formulaire de matérialisation porte l’action.
- app/main.py, app/config.py, clients/mobile/ConnectedApp.tsx, clients/mobile/src/routes/programmes.tsx, src/shell/ShellContext.tsx, src/ui/library/LibraryHost.tsx et LibraryScreen.tsx, src/storage/journal.ts et journalTypes.ts : branchements additifs sous lease, pas réécritureBODY/NUT. La connexion et sa createSerialQueue de src/storage/serial.ts sont réutilisées ; serial.ts reste lu, sans nouvel ordonnanceur. API_URL/transport sont injectés depuis ConnectedApp, sans modifier les profils EAS ou qa-delivery.config.js de REL03. Aucun changement de la géométrie de src/routes/_layout.tsx ou des onglets D4.
- openspec/specs/mobile/feature-migration-map/inventory.yaml et inventory.md : cinq routes proposées classées dès leur montage.
- docs/strategy/SPEC_REGISTRY.md : préparation puis reçu du scope.

## Tests affectés bornés
Nouveaux tests commande/readmodel/API/migration/reprise/ConnectedApp. Broad des tests user_program_drafts, user_programs_editor_http, user_programs_generate_http, user_programs_publish_http, user_program_publish, user_program_new_version, user_program_republication, program_quality_reviews et weekly_plan_materialization ; readback bibliothèque/mission/journal/historique. Migrations : checks canoniques et sweep borné. Les fichiers moteur SCI, JSONEKB, calculs de plan, overload/stats et baselines sont exclus.

Aucun fichier produit n’est actuellement loué ou modifié pour ce scope ; les leases deviennent actifs seulement après GO et vérification de l’absence de writer concurrent. Aucun troisième scope dans cette PR.

## Active leases after exact GO —15November2026

BUILD_AUTHORIZATION.json supersedes the preparation NO_GO for this scope. Backend owns the listed app/migration/web paths; native transport owns api/programBuilder.ts and programBuilderDTO.ts plus tests; root owns domain/storage/recovery/UI and integration docs. Add app/database.py solely for excluding the new receipt table from startup create_all, exactly as existing PLAN/BODY/NUT exclusions; behavioral test required. This is necessary to preserve the approved no-startup-DDL contract, not permission to refactor database initialization. No other worktree or REL03 source lease acquired.

## Required migration consumers,15november

The MOB07 migration advances the snapshot used by tools/qa_delivery/database.py. Backend worker owns the two exact schema pins in that file and releases.py, plus affected test_qa_delivery_{database,releases,server,pipeline}.py assertions. Existing REL03 schema correction is already delivered/cleaned, no concurrent writer remains. No workflow/provider/hostname/signing/EAS/operations lease. This is the minimal snapshot-coupled consumer adaptation; all other release work remains separate.

Active PREPARE template consumer: add docs/release/rel-03/candidate.json only for its current server_schema pin, and the actual-default positive/stale-copy negative in test_qa_delivery_pipeline.py. This file is the workflow default input, not an immutable release receipt. Prior f31 bytes and historical PREPARE receipts remain preserved. No other template field or workflow/provider/source Python change. Backend worker owns this bounded correction after the full sweep; no concurrent owner.
