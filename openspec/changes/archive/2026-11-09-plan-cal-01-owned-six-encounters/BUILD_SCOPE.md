# PLAN-CAL-01 — lease proposé et critères de fin

**GO BUILD CONTRÔLÉ REÇU**,9novembre2026. « Autoriser le build PLAN-CAL-01 contrôlé ». Autorisation sur ce dossier concret,
pas sur les anciens GO SCI ou PLAN379. [Design](design.md), [UX-CAL](UX_CAL_BOARD.md).

## Lease fonctionnel après GO

| Surface | Fichiers bornés | Effet autorisé |
|---|---|---|
| Bundle/worker | nouveau tools/plan_calibration_runtime_bundle.py et app/services/plan_v3/science_worker_v2.py ; packaging.py, authority.py | Inventaire2, routing attesté sept profils, imports réels et publication courante ; pas nouveau moteur |
| Acquisition/projection | calibration.py, snapshots.py ; nouveau calibration_profiles.py si décomposition nécessaire | Faits/selecteurs propriétaires, projection réellement qualifiée et références snapshot |
| Gardes du contexte runtime | evaluations.py, commands.py, execution.py | Confronter snapshot/ack/start/applicabilité à packaging/inventaire/génération actuels ; conserver rejeux historiques et journal |
| HTTP | app/routers/mobile_plan_v3.py | Header/écho et champs d'enveloppe négociés, sélection via observations, mêmes routes ; pas nouveau namespace |
| Contrôleur/adaptateurs | clients/mobile/src/api/{firstPlanV3,calibrationV1,blueprintV3,firstUseV3}.ts, domain/planV3Types.ts, storage/planV3Journal.ts, ConnectedApp.tsx | Décodage inventaire, sélection/reprise, source JSON/drafts/pending et A/B ; pas SDK SCI V1 |
| UX-CAL | PlanV3FirstUseScreen.tsx, nouveaux sous-composants/présentateurs sous src/ui/plan/calibration* ; PlanV3Messages.ts | Choix de mouvement, installation spécifique, unité/réglage exact, faits/motif/retry et historique. G1 avant code, pixels avant commit |
| Tests/preuves | nouveaux tests/test_plan_cal_01_*.py, tests/science/consommateurs PLAN ciblés existants si adaptations strictement nécessaires ; *.test.ts des adaptateurs/domain/storage concernés | Vrais HTTP/bundle/SQLite et contrôleur, aucune fixture servie |
| Documentation | présent change, docs/plan/plan-cal-01/*, append SPEC_REGISTRY, reçu review-receipts/plan-cal-01/* | Autorisation, compatibilité/source map, captures natives brutes et verdict humain, CI/closeout |

Le module de journaling existant ne reçoit que les clés source JSON/drafts
nécessaires à la reprise si leur validation l'exige : aucune table ou migration
SQLite. Pas de nouveau modèle/colonne/index serveur. Aucune modification du
builder scripts/build_plan_v3_runtime_bundle.py ou du worker historique ; s'ils
ne peuvent rester intacts, documenter l'incompatibilité et refaire borner le scope.

## Read-only / exclus

- tools/science_*, docs/science/**, data SCI/catalogues/registries et leurs hashes.
- clients/mobile/src/api/firstPlan.ts, firstPlan.contract.json et schémas SCI V1/V2/V3 ; aucune substitution de contrat.
- app/models, migrations, startup schema, configuration de production/CI, packages/dépendances.
- MISSION, compte/préférences et composition exécution/journal LOCKED ; anciens rendus/baselines/receipts jamais réapprouvés automatiquement.
- Aucune purge, compte QA privé, seed réel, appareil physique ou distribution.

Le présent scope assume SHARED_CODE à confirmer par check_scope : ciblés+broad
réel backend/consommateurs + Jest/TS, pas full local systématique. Nouvelle
migration ou CI infra constituerait un nouveau périmètre à revoir, pas un prétexte
pour lancer un full local au hasard. CI réelle du HEAD et canonique obligatoires.

## Acceptations du slice — toutes à prouver après GO

- PCAL-01 : vrai bundle inventaire2, sept profils explicites ; v1/pilote/replays préservés, mauvaise version/source/parent/worker→refus.
- PCAL-02 : ouverture aide sans épisode ; six réalisations réellement acquises par ledger propriétaire, Setting exact et aucun booléen/label à la place de la familiarisation.
- PCAL-03 : sélection courante explicite, ancien contexte/choix invalide sans effacer faits ni cacher préoccupation/retrait ; UNKNOWN reste tel.
- PCAL-04 : snapshots/évaluations/ack/start liés au contexte runtime actuel, V3/prescriptions/intention intacts ; aucun ancien C3 brut ne court-circuite la rencontre.
- PCAL-05 : réponses perdues/redémarrage/doublons/révision/A-B/tardifs prouvés ; même séance possédée retrouvée et lisible/journalisable nativement.
- PCAL-06 : UX-CAL G1 puis vrais pixels approuvés, sémantiques kg machine/par haltère et motif d'arrêt explicites ; MISSION/baselines inchangées.
- PCAL-07 : vrais tests consommateurs/CI/revues, merge gardé/canonique/Sonar réel/closeout/cleanup ; compte rendu capacité livrée et blocages externes.

Completion autorisée = slice contrôlé réel sur bases/app de test isolées,
**pas** activation de données personnelles ni MOB03 global/release acceptés.
