# UX-CAL-02 — périmètre soumis au GO BUILD

**PROPOSED / NO_GO_BUILD.** La validation demandée porte sur ce design et le
croquis G1 ; les pixels réellement implémentés seront soumis avant commit UI.

## Fichiers possédés et changements permis

- `clients/mobile/src/ui/plan/{calibrationInstrument.tsx,calibrationModel.ts,calibrationEncounterInstrument.tsx,PlanV3FirstUseScreen.tsx}` : seules branches de calibrage/entrée décrites dans design, pas proposition/ack/observed/exécution.
- Nouveaux helpers locaux `clients/mobile/src/ui/plan/calibration{Layout,Help,Controls}.tsx` ou `.ts` : composition, groupes de choix, aide verbatim et état UI ; aucun nouveau système global.
- `clients/mobile/src/api/{firstPlanV3.ts,calibrationV1.ts,firstUseV3.ts}` et nouveau `calibrationProfilesV2.ts` : compatibilité/décodage/croisement/aide intégrité ; aucun nouveau endpoint ou format serveur.
- `clients/mobile/src/domain/planV3Types.ts` : types client stricts pour champs déjà servis, sans nouvelle sémantique transport/SCI.
- Tests voisins existants et nouveaux de ces modules ; consommateurs HTTP/propriétaires sous `tests/test_plan_cal_01_owned.py`, `tests/test_first_plan_v3_runtime_http.py` et helpers `tests/plan_v3_test_support.py` read-only, ou test dédié consommant ces mêmes supports ; aucune factory SCI positive dans le chemin servi.
- Docs de ce change, `docs/plan/ux-cal-02/`, append de SPEC_REGISTRY, nouvel espace de reçu visuel `clients/mobile/visual-contract/review-receipts/ux-cal-02/`. Nouvelles fixtures/tests visuels explicitement bornés à cette composition si nécessaires, sans réécriture de baselines LOCKED.

Tout helper nouveau reste dans ces namespaces. Une dépendance partagée non
listée réellement nécessaire est à exposer avant extension ; ne pas modifier
globalement AccountFrame, PrimaryAction, theme, routes ou le journal.

## Read-only et hors-périmètre

`tools/science_*`, docs/schémas/fixtures/manifeste/registres SCI, SDK et contrat
historique `firstPlan.ts`/`firstPlan.contract.json`, workers/builders/autorités
serveur, modèles/migrations et schéma SQLite, baselines approuvées, identité et
tokens. Aucun install/updgrade, données personnelles, nouvelle admission,
activation, Store/OTA, déploiement ou reprise du chantier mannequin.

## Milieu contrôlé et livraison

Bases jetables, app de test isolée, données de démonstration marquées et vrais
consommateurs ; aucune collecte réelle ou preuve clinique. Appareils/simulateurs
à inventorier et propriétaires à distinguer avant manipulation. Ne pas arrêter
les appareils/processus de l'opérateur. Reçus de388/389 préservés.

Une fois scope/G1 approuvés : implémentation, tests/revues, rendu natif/acceptation
pixels puis commit/push/PR/CI/merge/closeout autonomes sous GOV-MERGE-01. Pas de
nouvelle question de merge. Si un gate appareil ne peut être exécuté, le nommer
comme limite et ne pas prétendre à son PASS ou à une recette physique complète.
