# MOB-04 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rendre Aujourd'hui utile avec reprise possédée, commande inconnue explicite et accès au vrai premier parcours ou à la recommandation historique choisie.
**Architecture:** Nouvelle projection GET sans mutation, client/resource en mémoire, host Today déléguant aux commandes et au journal existants. MISSION historique reste intacte, contrôleur PLAN unique.
**Tech Stack:** Python/FastAPI/SQLAlchemy, TypeScript/ReactNative/Expo existants, sans dépendance ni schéma.
**Spec:** design.md + PILOT_VALUE_SCOPE.md + BUILD_SCOPE.md + UX_BOARD.md + BUILD_AUTHORIZATION.md dans ce change.

## Global Constraints
- Base b9a334d22e6b75e9b83650eb1b2b833d4ed5d169 ; nouvelle base relue après mergeREL03 avant lease partagé.
- API mission-action/1.0.0, requested_path FIRST_USE|HISTORICAL explicite, X-Auren-Mission-Action exact, hostV3 explicite first-session-runtime/3.0.0.
- Séance ouverte possédée et commande locale pending/unknown prioritaires ; jamais nouveau start/ack/qualification depuis GET/navigation/cache.
- MISSION-SCREEN-V1, calibrage/ack/exécution, SCI/V1 historiques, journal/outbox et compte inchangés.
- Pas de table/migration/dépendance, données réelles, activation, déploiement ou publication externe ; quatre onglets conservés.
- GO/G1 reçus, pixels iOS/Android encore PENDING avant commit UI ; baselines read-only.
- Leases exclusifs REL03→MOB04→MOB05A, aucune PR chevauchante ConnectedApp/mobile_api/registre/inventory ; modules propres indépendants permis.

## Review Focus
- Métadonnées de capabilities actuelles ne doivent pas appeler un loader qui UPDATE sous verrou ou déclenche évaluation utilisateur ; GET trace DML doit rester vide.
- Une intention locale dont la réponse a été perdue bloque toute action contradictoire malgré une lecture serveur sans séance ouverte.
- Un CREATED fermé se relit après retrait/flags off, sans rouvrir la séance ni créer un deuxième handoff.
- Une réponse tardive après logout/changementA-B/source/mutation ne remplace pas l'état courant ; l'échec de réseau n'est pas NO_MISSION.
- Le même contrôleur PLAN survit à la navigation et conserve clés/brouillons/acks, sans seconde source ou lancement automatique hors choix.

### Task 1: Projection serveur et transport propres
**Files:** app/services/mission_action.py ; app/routers/mobile_mission.py ; tests/test_mission_action.py ; tests/test_mobile_mission_http.py.
**Interfaces:** project_mission_action(db, owner_id:int, requested_path:str, *, v3_host:bool=False, now:datetime|None=None)->dict ; router sans prefix parent à inclure sous /api/mobile/v1 après lease. Envelope fermée selon design. Le GET n'appelle pas first_plan_execution_read_model ; owned_binding et lock_authority(lock=False) sont lectures de métadonnées autorisées.
- [ ] RED testservice : deux séances ouvertes=>CONFLICT et aucune recommandation, séanceA invisibleàB, firstuse runtimeoff sansfallback, histoirehistoriqueREADY réelle/profil/inexécutable et sourceobligatoire.
- [ ] check_scope puis pytest tests/test_mission_action.py, attenduFAIL moduleabsent.
- [ ] Implémenter projection sous no_autoflush, lookupowner et comptesouverts avantautorité ; schema_available puis handoffCREATED fermé/binding, lecturecourante lock=False seulementpremierparcours ; raisonsfermées et profilrecoupé, jamais evaluate/ack/start.
- [ ] RED testsHTTP routermonté dans fixtureapp isolée via APIRouter temporaire, Bearerseul/no-store/422sansvaleursprivées,406négociation/source/host,401/étranger, aucune DML/capture de faits. Intégration de route réelle dans mobile_api attendTask3.
- [ ] GREEN tests ciblés et broad mobile-readmodels/PLAN autorités/statuts existants pertinents ; Ruffneuf/budget/protocole, rapport des limites. Commitbackendpropre autorisé sans UI, pasdePRavantleases/scopecomplet.

### Task 2: Client strict et ressource indépendante
**Files:** clients/mobile/src/api/missionAction.ts et missionActionResource.ts +tests.
**Interfaces:** MissionActionClient(auth,transport).read(path,host)->Promise<outcome> ; MissionActionResource.state/refresh/selectPath/invalidate, snapshots copiesmémoire et auth.revision/sequence. Aucun stockage/journal/SDKnouveau.
- [ ] RED tupleowner/path/source/action/profil/session incohérents rejetés, mauvaiseversion/echohost, transportunknown distinctabsence ; `isStartable` canonique vérifie historique.
- [ ] GREEN client, puis RED→GREEN raceA/B/logout/path/mutation/doubleread et réponseperdue ; stalelecture désactive nouveauStart, pas nouveau request_id.
- [ ] Jest ciblé+TS et vrais clientsV1/V3 consommateurs broad, pas galerie commepreuve.

### Task 3: Host Today et lease de composition après REL03
**Files:** clients/mobile/src/ui/mission/MissionActionHost.tsx +tests ; ConnectedApp.tsx/ShellContext.tsx ; app/routers/mobile_api.py inclure router ; inventoryMOB00 source et rendu généré ; tests/srcsyncconnectedApp ; registreappend ; docs/pilot/mob04-mission/.
**Interfaces:** Host reçoit ressource/projection, étatlocaljournalcontrôleur et callbacks existants, pas nouveau propriétaire séance. Today FIRST_USE par défaut ; choix historique explicite seulement. Ressource invalideaprèsstart/close/reconcile.
- [ ] Relire canonique après mergeREL03, intégrer proprement son observer sans modifier mission/exécution/compte ou reprendre un ancienConnectedApp.
- [ ] RED→GREEN vrai wiring/auth/currentlocalpending/unknown/CREATEDclosed/returning/norecommendation/foregroundreconnect sanscoldrestart ; mêmecontrôleur/journalunique et mêmeclécommande. MainCTA respecteétats et isStartable, sourcehistorique explicite.
- [ ] Rendre familleG1 acceptée et référencecarteMISSIONintacte ; Détailscompacts horscartelocked, phrasemoteur inchangée, actionstactiles/AX/back/safeareas/fonts/reducedmotion.
- [ ] Monter vrai GET dansrouterglobal +inventaireMOB00, rejouerHTTP et gardeexhaustivité routes. Ciblé+broad/TS/Jest seloncheck_scope ; aucun full backend systématique.
- [ ] Vrais rendus iOS/Android sur artefactcompatible et HTTPsynthétique, board source-labellé avantaprès puis acceptationopérateur AVANT commitUI. Si outillage/disque bloque, nommerborne et préparerle reste, pas fauxpixelsExpoGo incomplet.

### Task 4: Revue et livraison
**Files:** tests/rapports de ce scope, reçusvisuels/docs/registre, archiveCLI.
- [ ] Revue fraîchemix données/natif sur diffcomplet avec ReviewFocus et limites, corrigerCritical/Important RED→GREEN ; aucun GoMerge supplémentaire.
- [ ] Vérifications applicables, sécurité, OpenSpecstrict, gitleaks, CI4checks HEADexact/basefraîche, Sonarconsultatifréel.
- [ ] CommitUIaprèsacceptation, push/PRunique, mergegardéGOV, CIcanonique, archive/closeout/cleanup seulsélémentssanstravailunique.
- [ ] Paritédelta uniquementpreuvesréellesetnouveauSHA/artefact ; recettephysique/DATA/diffusion restent distinctes ; MOB05A exécutableensuite.

## Self-review et séquence
Task1 produitcontrat pourTask2, Task2pourTask3 ; aucunfichierpartagéREL03avantsonmerge. Headerhostn'autoriseaucunescience, readers puretéDML testée. Task3estseulpointUI ; aucuncommitdecompositiontantquepixelsnonacceptés. L'exécutioninlineéconomise une série d'agents ; revueglobalefraîche en fin sous mêmesgates.
