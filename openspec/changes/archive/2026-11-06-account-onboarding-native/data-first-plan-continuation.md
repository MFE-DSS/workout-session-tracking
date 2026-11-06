# MOB-03 — continuation données et premier plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans ; exécution native demandée par le mandat autonome, revue indépendante finale.

**Goal:** Livrer des fondations non destructives et consommateurs vérifiables dans #353.
**Architecture:** Réutiliser body_profile/AuthSession ; ports refusant par défaut tout producteur de suppression ou science absent ; métadonnées locales séparées des faits du journal.
**Tech Stack:** Python/SQLAlchemy et React Native Expo58/TypeScript/Jest existants ; zéro dépendance.
**Spec:** proposal.md, specs/mobile/account-lifecycle/spec.md et specs/mobile/onboarding-profile/spec.md.

## Global Constraints

Aucune suppression réelle/migration serveur/UI nouvelle ; pas d’inventaire ; kg uniquement ; consentement/flag avant lecture corporelle ; inconnu ne devient pas confirmé. GET nouveau après revue du delta.

## Review Focus

1. Epoch/hash/identité périmés entre réauthentification et mutation : refuser.
2. Pagination de dates égales et lignes partielles/invalides : pas de perte ni correction silencieuse.
3. Réponse perdue et relance : request_id conservé, relecture sans rejouer une mutation.
4. Révocation/401/404 ou reçu JSON forgé : aucune autorisation de purge.
5. Réponse scientifique tardive/fingerprint erroné/fixture non servie : ne rien exposer au nouveau compte.

5 novembre 2026. PR unique #353. Canonique 5fd18c3 incorporé sans conflit, HEAD précédent 2ba9fd4 préservé. Mandat opérateur DATA & FIRST PLAN.

## Brainstorming / Options / Risques / Choix retenu

1. Effacer users et compter sur CASCADE : rejeté, références sociales sans cascade et sauvegardes non contractualisées ; risque destructif.
2. Créer immédiatement une table de demandes/receipts et une nouvelle saisie corporelle : nécessite politique de durée/identité après effacement, migration et revue de scope ; prématuré ici.
3. Réutiliser le lecteur corporel, réaliser les gardes et consommateurs non destructifs, proposer uniquement la lecture JSON de poids, puis garder les producteurs indisponibles explicitement : retenu selon le mandat. Cela livre des briques exécutables sans promettre que l'effacement ou le premier plan sont servis.

## Périmètre exécutable

- Domaine body_profile : lecture paginée de poids datés depuis BodyMeasurement uniquement. Anciennes valeurs User.weight_kg absentes du flux. Champs de provenance non stockés = UNKNOWN, source_ref de la ligne et created_at distinct de measured_at. Aucun POST/PUT de mesure ni nouveau consentement ; consentement actif et flag existants requis pour exposer la route proposée.
- Réauthentification : identité relue depuis le serveur, mot de passe vérifié par le service canonique, époque/hash obsolètes refusés ; aucune information secrète dans les valeurs publiques. Révocation via session_epoch existant, pas de nouveau mécanisme de token.
- Suppression : protocole de demande propriétaire avec request_id stable, état incertain après interruption, relecture avant nouvelle mutation, déduplication et génération AuthSession. Port de persistance propriétaire injectable et durable exigé avant production ; aucune API de demande servie tant que le producteur/politique manque. Une preuve de suppression doit correspondre à propriétaire + request_id + politique + révocation + périmètre et sauvegardes vérifiés ; aucune purge de journal non attribué ni reset global. Les gardes de nettoyage sont branchables mais ne reçoivent aucun faux reçu de production.
- Premier plan : consommateur des versions SCI-P01/P02, mapping des statuts, annulation des réponses après changement de compte, aucun cache de réponse sous un autre compte. Producteur absent par défaut = unavailable/NOT_SERVED ; fixtures canoniques de démonstration seulement. Pas de modification de MISSION ou de nouvelle composition.

## Contrôles et delivery

Tests RED→GREEN des contraintes et des vrais consommateurs AuthSession ; tests de route pour la lecture de poids seulement après validation du delta. check_scope puis vérifications de son tier et broad ciblé ; Jest/TypeScript, gardes de migration-map et OpenSpec ; aucune migration ou full sweep local systématique. Revue indépendante sécurité/qualité avant exposition de poids, et revue finale des modifications. Préserver les références LOCKED ; aucun commit UI nouveau prévu.

Publier dans #353 avec CI du HEAD final et CR compact. Le merge du change complet ne sera pas forcé tant que suppression/science/appareils restent obligatoires et qu'aucune politique versionnée n'autorise explicitement ce sous-ensemble. MOB-04 reste préparatoire après un merge autorisé, pas un GO BUILD implicite.

## Tâches

- [x] Inventaire/matrice et sources Apple/Google, sans décider une rétention juridique.
- [x] Lecteur canonique paginé, validation dates/unités/valeurs/provenance et isolation.
- [x] Réauthentification/révocation atomiques sous propriété, tests d'identité obsolète.
- [x] Consommateur de demande/confirmation avec persistance propriétaire et refus de purge non confirmée.
- [x] Consommateur FirstPlanRecommendation et fixtures de statuts, vrai AuthSession et réponses tardives.
- [x] Revue opérateur du delta GET poids puis route/API/client si acceptée ; sinon garder le lecteur et les contrats non exposés.
- [ ] Revue sécurité/qualité, contrôles ciblés et CI réelle ; rapport exact des gates restantes dans #353.

## Revue de construction — précisions retenues

Le relecteur indépendant confirme les fondations non servies. SCI : conserver séparément les six statuts métier et les états de transport, contrôler structure/version/fingerprint et génération, sans autorité de fixture en production. Effacement : un reçu structuré n'est pas une preuve authentifiée ; seul un adaptateur de production propriétaire/autoritaire futur pourra fournir la garantie. Relecture impossible (401/404/révocation) = inconnu, pas purge. Poids : pagination déterministe (measured_at,id), lignes atypiques signalées sans correction ni troncature silencieuse. Le domaine body_profile reste propriétaire de la lecture ; User.weight_kg est exclu. Taille de page maximale 100 : limite de transport, pas politique scientifique ou de rétention.

## Task 1 — domaine et gouvernance

**Files:** app/services/body_profile.py ; app/services/account_lifecycle.py ; tests/test_mob03_data_foundations.py ; docs/MOB03_DATA_RETENTION_MATRIX.md.
**Interfaces:** list_weight_measurements(db,user_id,limit=50,before=None) retourne lignes canoniques ordonnées ; reauthenticate_account(db,user,current_password) retourne User relu sans exposer le secret ; revoke_account_sessions(db,user,current_password) incrémente atomiquement l’époque, transaction appelante.
- [x] Tests RED avant code : chronologie unique/propriétaire/null/égalité de dates/curseur ; compte inactif/secret faux/époque changée ; révocation access/refresh/cookie.
- [x] Implémenter ces helpers dans leurs services canoniques, pas de writer corporel.
- [x] Tests ciblés GREEN puis broad des consommateurs ; commit après revue finale regroupée.

## Task 2 — orchestration propriétaire d'effacement et premier plan

**Files:** clients/mobile/src/api/accountDeletion.ts, firstPlan.ts, leurs tests ; clients/mobile/src/storage/accountRequestStore.ts et .web.ts ; ownership.ts/ownershipStore.ts et tests.
**Interfaces:** AccountDeletionClient(auth,store,producer=null), prepare/reconcile/submit, sans chemin HTTP inventé ; AccountRequestStore read/write propriétaire ; FirstPlanClient(auth,producer=null).read(requestFingerprint), six états de transport et six statuts SCI séparés.
- [x] Tests RED : vrai AuthSession + port transport, request_id durable/reprise, doubles appuis et génération, retour 401/404, receipt non autoritaire, aucun producteur, huit fixtures SCI et mauvais fingerprint/version.
- [x] Implémenter protocoles fermés par défaut, stockage SQLite propriétaire sans secrets et tombstone local seulement après preuve authentifiée ; aucun purgeur global ou adaptateur de production fictif.
- [x] GREEN ciblé, puis Jest/TypeScript et gardes consommateurs ; sécurité/qualité indépendante avant nouvelle exposition.

## Task 3 — lecture JSON de poids après revue, puis publication

**Files:** app/routers/mobile_body.py, mobile_api.py ; inventaire MOB-00 ; clients/mobile/src/api/weightHistory.ts et tests ; documents MOB03 de contrats/CR.
- [x] Attendre la décision de revue du delta GET, consigner la réponse exacte ; sinon ne pas ajouter la route.
- [x] Tests RED de route authentification/consentement/flag/pagination/valeurs manquantes et propriétaire ; client avec vrai AuthSession et réponse tardive.
- [x] Adaptateur GET seulement, données historiques inchangées, cache no-store et validation de curseur ; GREEN.
- [ ] Revue fraîche du diff complet, corrections Important/Critical en une passe RED→GREEN ; check_scope et contrôles exigés, puis publication dans #353 et CI réelle.
- [ ] CR compact : exécuté/publié, tests, décisions de politique, producteurs scientifiques et appareils manquants. Aucune acceptation complète/MOB-04 BUILD implicite.

## Revue opérateur du delta GET

Réponse reçue : **« Valider le GET de poids proposé »**. Autorise la lecture JSON propriétaire/consentie sous flag corporel existant ; aucun writer ou écran nouveau. Task3 est maintenant exécutable. Normaliser tout curseur conscient en UTC avant comparaison SQL ; ce garde devient requis avec une frontière HTTP.

## Revue finale des fondations, avant extension HTTP

Un Important confirmé : renouvellement impossible d'une intention définitivement rejetée. Correction en une passe avec RED→GREEN : relecture autoritaire du refus terminal, puis nouvelle intention explicitement demandée et atomiquement liée à la précédente ; aucune réouverture des intentions pending/submitted/unknown. Le point de fuseau du curseur, mineur tant que non exposé, est traité dans le contrat de la nouvelle route. La revue ciblée de la frontière HTTP corporelle suivra son branchement nouvellement accepté ; elle ne remplace pas les preuves appareil.

## Interfaces et preuve finale de réalisation

Signatures réalisées : AccountDeletionClient(auth,call,store,producer=null,requestId), submit/reconcile/retryRejected/complete ; FirstPlanClient(auth,call,producer=null).load(input). Les signatures esquissées dans Task2 ci-dessus sont remplacées par ces contrats testés. Revue ciblée du GET : aucun Critical/Important ; deux mineurs différés dans le rapport. Vérifications locales finales : 613 tests mobiles, TypeScript, 347 backend, Ruff/budget, Bandit, protocole, OpenSpec6/6. Publication/CI distante à consigner dans #353 ; les cases les regroupant restent ouvertes tant que le reçu ne les prouve pas.
