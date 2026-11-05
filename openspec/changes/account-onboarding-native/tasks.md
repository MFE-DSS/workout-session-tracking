# Tasks — MOB-03

Statut courant : mandat PRODUCT DELIVERY du 5 novembre, rendu V1 ajustée accepté. Socle compte natif, garde propriétaire et adaptateur des déclarations existantes réalisés. Les acquisitions Blueprint complètes, effacement/STORE-00 et recettes appareil restent ouverts. Voir native-account-delivery.md et SPRINT_MOB03_NATIVE_ACCOUNT_UI_REPORT.md ; les paragraphes de preuves précédents décrivent leurs passes historiques.

## 1. Décisions et garde de périmètre

- [ ] 1.1 Faire accepter D-MOB03-1 à 4 (objectifs/unités, poids/compatibilité, effacement/rétention/journal, acquisitions/UX) et consigner les choix ; preuve : décisions écrites revues par l’opérateur, sans valeur de labo promue implicitement.
- [x] 1.2 Fixer le contrat d’identité et de partition du journal local, y compris credentials et commandes d’un compte quitté ; preuve : matrice propriétaire avant/après relance et cas interdits documentés.
- [ ] 1.3 Exécuter la revue sécurité/qualité prévue par GOV-SONAR-01 avant la nouvelle exposition de données corporelles ; preuve : outils/vérifications réels, constats et limitations consignés, aucune affirmation d’audit exhaustif sans preuve.
- [x] 1.4 Exécuter python scripts/check_scope.py avant les vérifications et suivre son tier réel ; preuve : rapport du diff effectif, sans full sweep local redondant.

## 2. API et cycle de compte

- [x] 2.1 Spécifier puis implémenter l’inscription JSON avec validations auth/password_policy et protection de débit approuvée ; preuve : tests rouges puis verts de validation, unicité, double appui/réponse perdue et absence de secret dans logs.
- [x] 2.2 Câbler restauration, changement de mot de passe et révocation via les frontières canoniques ; preuve : tests auth_scope_isolation, auth_password_policy et d9_mobile_auth concernés, plus route contract et documentation JSON.
- [x] 2.3 Classer chaque route ajoutée dans exactement une entrée MOB-00 ; preuve : test_native_feature_migration_map et absence de route fantôme/non inventoriée.
- [x] 2.4 Conserver les parcours web de mot de passe oublié/réinitialisation et export ; preuve : liens réels vérifiés, aucune route native concurrente non approuvée.

## 3. Vrai consommateur et reprise

- [ ] 3.1 Câbler le vrai consommateur du compte/onboarding avec AuthSession et journal propriétaire ; preuve : tests ConnectedApp réels traversant création, connexion, interruption, relance et changement de compte sans fuite ni envoi sous un autre propriétaire.
- [x] 3.2 Protéger l’action synchrone et les réponses tardives ; preuve : tests de doubles appuis avant réponse, résultat inconnu, retry contrôlé et commande plus récente non écrasée.
- [x] 3.3 Documenter les états d’erreur et récupération du parcours ; preuve : chaque erreur réseau/auth/validation possède un comportement utilisateur reproductible, sans confirmation inventée.

## 4. Déclarations, objectifs, unités et préférences

- [ ] 4.1 Après D-MOB03-1 accepté, réaliser seulement les usages/champs/vocabulaires approuvés ; preuve : tests du domaine/stockage et du consommateur, conversions réversibles selon précision du contrat, absence de recopie du profil LAB ONLY.
- [x] 4.2 Raccorder la lecture/écriture des préférences au service canonique ; preuve : tests training_preferences et API ownership, non-déclaré distinct de vide, absence de défaut ou d’inférence.
- [ ] 4.3 Contractualiser le contexte matériel via propositions/substitutions sans inventaire manuel, après recadrage opérateur ci-dessous ; preuve : résolution canonique et états inconnus explicités, aucune disponibilité de salle inventée, faisabilité et historique préservés. Pas de nouvel algorithme dans ce raccordement.

## 5. Poids, consentement et effacement

- [ ] 5.1 Après D-MOB03-2 accepté, exposer la chronologie existante et son lecteur de référence ; preuve : tests poids daté/absent/hérité sans date inventée, conversions et isolation ; aucune seconde chronologie.
- [ ] 5.2 Raccorder consentement corporel versionné et retrait au service existant ; preuve : tests body_profile et consommateur avant/après retrait ; aucune activation implicite photo/provider.
- [ ] 5.3 Après D-MOB03-3 accepté, implémenter la suppression de compte selon l’inventaire approuvé ; preuve : réauthentification/propriétaire, résultat incertain, révocation, commandes locales et effacement/rétention réels testés sur fixtures isolées, jamais données historiques de production.
- [ ] 5.4 Si une migration est approuvée, appliquer les gates migration imposées par check_scope ; preuve : additive-only, drift/snapshot/roundtrip et compatibilité testés, sans backfill ou action destructive implicite.

## 6. Surfaces natives et intégration finale

- [ ] 6.1 Après D-MOB03-4 accepté, produire le croquis puis le rendu réel des surfaces concernées avec primitives canoniques ; preuve : décision opérateur avant commit UI, inventaire de provenance et relecture des décisions, aucun baseline auto-approuvé.
- [ ] 6.2 Vérifier l’intégration globale : Jest mobile complet, TypeScript, tests ciblés/broad imposés, OpenSpec strict et contrat visuel ; preuve : résultats du diff final, régression MOB-02 réelle (restauration, double appui, substitutions, bilan) absente.
- [ ] 6.3 Publier un seul change/PR sur la base courante, obtenir les checks réels et revue indépendante ; preuve : HEAD exact contrôlé, protections intactes, Sonar vrai verdict consigné ; merge seulement selon les autorisations applicables.
- [ ] 6.4 Préparer backend/client compatibles, rollback et GO déploiement distinct ; preuve : SHA vérifié et environnement cible avant dispatch, puis statut effectivement déployé.
- [ ] 6.5 Exécuter Android puis iPhone connecté sur les parcours de compte, reprise, consentement et préférences ; preuve : appareils/builds/backend identifiés, captures et preuves réelles, aucune passe physique déduite d’un simulateur.
- [ ] 6.6 Mettre à jour le rapport et le registre sans prétendre acquises les gates non exécutées ; preuve : références des commits/runs et tâches restantes exactes.

## Workflow follow-up

- Archiver uniquement après les revues, validations et recettes obligatoires.
- Conserver les gates MOB-02 de déploiement et appareils jusqu’à leurs propres preuves ; sa fusion n’équivaut pas à son archivage.
- Photos/analyse corporelle, octogone du profil, nouvelle bibliothèque de salle et autres capacités restent dans leurs workstreams désignés.

## Preuves locales du socle API — 5 novembre 2026

Parties serveur de 2.1/2.2 implémentées : inscription et changement de mot de passe JSON, garde d'unicité/concurrence, quotas partagés, révocation et erreurs sans reprise de secrets. 241 tests backend ciblés/broad, 478 mobiles, TypeScript, Ruff/budget, Bandit ciblé et OpenSpec strict verts. Ces deux tâches globales ne sont pas cochées : le consommateur natif, la partition propriétaire et les parcours d'incertitude/UI ne sont pas encore raccordés. Pas de CI distante, commit/push bloqués par contrôle automatique ; pas de déploiement. D-MOB03-1 à 4 restent ouverts. Contrat et arbitrages dans les documents MOB03 du dossier docs.


## Reprise native et validation visuelle — 5 novembre

L'opérateur accepte la V1 ajustée après le comparatif et demande la poursuite du critical path. Les consommateurs compte et la partition propriétaire sont testés ; les acquisitions 4.x/5.x ne sont pas déduites de cette acceptation. L'adaptateur des déclarations existantes est testé côté serveur/client, sans raccordement du formulaire Blueprint (4.2 reste partielle). Vérification du diff : 531 tests mobiles, TypeScript, 274 tests backend/broad et gardes UI, Ruff264/548, Bandit ciblé, OpenSpec5/5 ; revue indépendante sans défaut bloquant. Un constat mineur d'en-tête no-store sur erreurs génériques reste différé, sans déclaration exposée. Publication en draft et vérifications CI consignées séparément ; aucune recette physique, suppression, archive ou disponibilité de premier plan déclarée complète.


## Consommateur des préférences — preuve ciblée

4.2 est réalisée : lecture des faits canoniques puis saisie et PUT complet depuis Profil, priorités ordonnées facultatives, familles et fréquence absentes distinctes de valeurs vides. Le vrai ConnectedApp et le modèle couvrent double appui, réponse inconnue/relecture, refus, changement de propriétaire et retour Android. Croquis/rendu acceptés ; compactage en blocs demandé avec revue visuelle déléguée. La recette physique 6.5, l'environnement concret 4.3 et les acquisitions Blueprint non contractualisées restent ouverts.

## Recadrage opérateur après rendu du matériel — 5 novembre

L'opérateur refuse la gestion manuelle de matériel : « Quelqu'un ne va pas commencer à manager la liste de son matériel ». La proposition 4.3 d'inventaire initial est retirée explicitement, non déclarée achevée ; le prototype API/client/UI non committé a été retiré. Partir du profil et proposer exercices/séances, puis permettre les substitutions selon les possibilités réelles, est la direction retenue. Le contrat de compatibilité et de résolution de l'inconnu reste à fournir ; ni une chaîne de salles ni un profil générique ne prouvent les équipements présents. Les familles ne sont plus demandées dans l'éditeur natif ; le PUT existant préserve leurs valeurs confirmées. Le domaine et les déclarations historiques restent inchangés.


## Continuation DATA & FIRST PLAN — état courant

- [x] Matrice complète et graphe des données, sans durée arbitraire ; mécanismes destructifs non autorisés conservés ouverts.
- [x] Fondations réauthentification/révocation, intentions clientes durables, réponses incertaines et marques de retrait ; aucune API d'effacement ou purge serveur prétendue livrée.
- [x] Delta GET poids accepté (« Valider le GET de poids proposé »), lecteur canonique/route/SDK, consentement/flag/propriété et revue de sécurité ciblée ; aucune UI/saisie corporelle.
- [x] SCI v1 reçus, consommateur et fixtures de statuts réalisés ; aucun moteur ou vrai premier plan READY servi.
- [ ] CI du HEAD final de continuation et reçu de publication dans #353.
- [ ] Politique d'effacement et producteurs requis ; déploiement/recettes physiques puis critères globaux. Les tâches globales non acquises ci-dessus restent ouvertes.

## DATA COMPLETION — sous-ensemble technique

- [x] Consommateur poids sans UI, révocation/vides/pages/cycles/auth/réseau/comptes ; chronologie et GET acceptés inchangés.
- [x] Orchestration durable native/web, refus non autoritaire inconnu, états terminaux monotones et tests de reprise/ancien propriétaire sur vrai SQLite.
- [x] Design/fixtures du producteur de suppression, sans route/migration/effacement ; tableau limité aux politiques légales ouvertes.
- [x] Refactor limité de weight_history_page, tests fonctionnels/sécurité conservés.
- [x] Tests runtime du port FirstPlanClient, READY uniquement de protocole non servi ; producteur scientifique non admis conservé indisponible.
- [ ] Revue/CI finale du nouveau HEAD, puis compléter le reçu #353.
- [ ] Gates COMPLETE antérieures : politique/effacement effectif, science et acquisitions/consentement, compatibilité et appareils. Aucune fusion partielle ne les lève.
