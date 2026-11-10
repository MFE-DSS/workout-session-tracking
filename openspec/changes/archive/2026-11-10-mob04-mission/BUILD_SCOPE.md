# MOB04 — scope à autoriser

**NO_GO_BUILD / G1_PENDING**, base2b831411. Ce fichier propose un scope contrôlé, pas une autorisation.

- Créer `app/services/mission_action.py`, `app/routers/mobile_mission.py` et leurs tests ; montage additif borné dans `app/routers/mobile_api.py`, inventaire MOB00 actualisé via sa source/générateur si route ajoutée.
- Créer `clients/mobile/src/api/missionAction.ts`, `missionActionResource.ts`, tests et présentateur local `src/ui/mission/MissionActionHost.tsx` ; brancher seulement les entrées Today/first-use dans ConnectedApp/ShellProvider et leurs consommateurs de test.
- Leases partagés : `mobile_api.py`, inventaire MOB00, `ConnectedApp.tsx`, ShellProvider et SPEC_REGISTRY ; MOB05/BODY/NUT s'appliquent séquentiellement après merge et relecture de base, jamais des patches concurrents sur ces fichiers.
- Read-only : producteurs/schémas/registres SCI/pins, DTO V1 historiques, tables et commandes PLAN, journal/outbox, primitives globales/tokens, quatre onglets, baselines, UI de calibrage/ack/exécution acceptée. Toute nécessité de sortir de cette liste revient au design avant apply.
- Réutiliser les services de lecture possédés ; ne pas construire un Blueprint ni un plan dans ce scope. Pas de table/migration/dépendance ni de donnée personnelle réelle.
- G1 du board puis vrais pixels iOS/Android avant commit UI ; aucun automatisme de baseline. Une famille, pas un GO par instance.
- Scope guard, tests ciblés et broad consommateurs, TypeScript, protocole/OpenSpec strict, contrôles sécurité applicables et CI obligatoire exact HEAD ; revue indépendante puis merge gardé/CI canonique/closeout/cleanup sous GOV après GO.

Une limite de recette appareil est déclarée comme limite et gate RELEASE ouverte, jamais renommée PASS. Le nouveau code ne vaut pas artefact Android/iPhone attesté ni GO déploiement.


Réconciliation du mandat PILOT VALUE DELIVERY du10novembre : [PILOT_VALUE_SCOPE](PILOT_VALUE_SCOPE.md) précise base canonique, option de navigation B, commandes locales et leases séquencés. Statut toujours NO_GO_BUILD/G1_PENDING.
