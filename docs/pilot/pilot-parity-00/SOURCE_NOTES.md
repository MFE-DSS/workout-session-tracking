# Sources — base2b831411 et preuves manquantes

## Canonical authority

- Manifeste produit/science conjoint : docs/strategy/AUREN_MANIFESTO_V1.md, notamment18–20,22,26–29,32–36. La vision n'est pas une preuve de service.
- MOB00 : openspec/specs/mobile/feature-migration-map/{spec,inventory}.md et inventory.yaml ; carte héritée39 fonctions/135 routes à son instant, pas nouveau comptage du runtime.
- Critical path : docs/strategy/AUREN_MOBILE_CRITICAL_PATH_2026_11_03.md ; ses futurs slices ne sont pas ouverts par leur présence. Les mentions historiques « pas de premier plan » sont complétées par PLAN/SCI postérieurs, pas réécrites.
- UX-CAL-02 : docs/plan/ux-cal-02/{DELIVERY,CLOSEOUT,AGENT_HANDOFF,DEVICE_GATES}.md ; reçu final public PR394, code393/mergec721562, closeout394/merge2b831411. Sept rencontres et domaine V3 réutilisés, aucune réadmission.
- DATA-ACT-01 : docs/data/data-act-01/CONTROLLER_DECISIONS.md ; D01partielle, D02–D09/C01–C11 ouverts. Nutrition/santé/documents ont leurs finalités à identifier, pas un consentement corporel universel.
- RELEASE-01 : docs/release/release-01/{README,QA_ENVIRONMENT,QA_RESULTS,INTERNAL_BUILD_BRIEF,PACKAGING_SECURITY_REVIEW}.md ; bench antérieur fe9f6e9, pas binaire pilote courant.
- ASSET-CONSUMER-01 : docs/assets/asset-consumer-01 et son change ; brief/pilote proposé, pas vecteurs mannequin ou Smith servis.

## Static consumer audit

Les ancres par capacité sont dans capabilities.v1.json. Deux audits indépendants lecture seule ont été conservés hors worktree dans /private/tmp/auren-pilot-parity-00-review-evidence/TRAINING_AUDIT.md et MEASUREMENTS_NUTRITION_AUDIT.md. Aucun test/code/DB/SDK modifié par ces audits. Leur taxonomy « code connecté » est resserrée ici : le statut SERVED_NATIVE exige en plus la preuve du build cible, absente aujourd'hui.

Preuve négative bornée : inventaire rg des modèles/services/routers et clients/mobile API/routes/ConnectedApp/package, recherche nutrition/calorie/protéines/carbs/HealthKit/HealthConnect/sommeil/pdf/upload/extract/Q&A/appointment. Les occurrences « macro » de zones corporelles et les calories cardio ne prouvent pas une nutrition ; CoachReport HTML ne prouve pas un document importé. Aucune preuve d'un service externe non inspecté n'est inférée d'une absence locale.

Poids : GET /api/mobile/v1/me/body/weight-history est propriétaire/consent/flag et client headless, sans écran. Le domaine BodyMeasurement reste seul fait daté ; User.weight_kg et bodyweight de séance ne sont pas fusionnés. Aucun poids7j existant ; la moyenne readiness historiquement appelée7j est une autre variable/fenêtre et ne doit pas être copiée. Corrections SSR existantes en place, sans révision/idempotence ; ne pas les appeler append-only.

Entraînement : MissionScreen/ConnectedApp consomment le vrai read-model historique. Programmes/Progrès sont PendingSpace avec liens web. Le journal local de synchronisation et le journal actif SCI ne sont pas un historique global. Des services excluent le marker SCI des agrégats legacy ; /me/sessions actuel ne porte pas cette exclusion explicite : toute nouvelle projection doit décider son dispatch, pas généraliser cette exclusion ou promouvoir NULL en0.

## EV-PILOT-00 / export source

La pièce jointe ce5b76be est un texte de mandat. Inventaire local de pièces jointes : aucune capture ou export fourni pour ce besoin. Une question asynchrone demande dossier/référence et export effectivement disponible. Tant que manquants : aucun écran, nombre, capacité observée ou API de l'outil externe n'est inventé ; toutes priorités restent proposées et la parité non établie. Si reçus, conserver identifiants de preuve, date, champs/capacités et source contrôlée ; ne pas committer de données personnelles ou les copier dans un LLM sans autorisation applicable.
