# AUREN — chemin critique mobile adopté le 3 novembre 2026

Source : roadmap et artefact de reprise transmis par l'opérateur dans la session Codex du 3 novembre.
Ce document fixe l'ordre de pilotage ; chaque changement substantiel garde son cycle OpenSpec et sa PR.
Il ne remplace aucun contrat visuel ou de domaine et ne crée aucune autorisation de merge/publication.

**Recadrage opérateur du 5 novembre :** l'ordre ci-dessous est conservé au service du cockpit personnel de bodybuilding et de la boucle comprendre → planifier → exécuter → mesurer → interpréter → adapter. [Direction et critères par tranche](AUREN_PRODUCT_SCIENCE_REALIGNMENT_2026_11_05.md) ; [dépendances scientifiques et handoff](AUREN_PRODUCT_SCIENCE_DEPENDENCIES.md). MOB-03 est la priorité active : premier véritable parcours utilisateur connecté, pas simple portage des formulaires web. Les futurs sujets nutrition, rapports hebdomadaires et photos ne conditionnent pas MOB-03.

## Voie produit, dans l'ordre

| Ordre | Tranche | État / objectif |
|---|---|---|
| Livré | GOV-01 | OpenSpec intégré |
| Livré | PLAT-01 | Pilote Android ; archive après retours testeur |
| Livré | MOB-00 | Carte de migration web → natif, archivée |
| Livré | MOB-01 | Coque native mergée ; passe iPhone connectée avant archive |
| 1 | CODX-00 | Mergée #346 (`60bea5d`), adaptateur officiel ; archive de clôture |
| 2 | CI-01 | Mergée #347 (`edd7351`), Jest/types en CI et check mobile requis ; archive de clôture |
| 3 | MOB-02 | Séance vraie dans les états dégradés ; D-MOB02-1=A et D-MOB02-2=marque seule acceptées |
| 4 | MOB-03 | Onboarding et compte ; dépendances STORE-00, notamment suppression de compte |
| 5 | MOB-04 | MISSION |
| 6 | MOB-05 | Progrès et journal |
| 7 | MOB-06 | Bibliothèque de programmes |
| 8 | MOB-07 | Constructeur |
| 9 | MOB-08 | Exercices |
| 10 | MOB-09 | Salle / équipement |
| 11 | MOB-10 | Substitutions |
| 12 | UX-LAB-PROFILE | Exploration du profil avant sa réalisation |
| 13 | MOB-11 | Profil / octogone |
| 14 | MOB-12 | Récupération / cardio |
| 15 | BIZ-01 | Abonnement |
| 16 | PLAT-02 | Périmètre à reprendre de sa proposition lors de l'ouverture |
| 17 | PLAT-03 | Périmètre à reprendre de sa proposition lors de l'ouverture |
| Gate | ALPHA | Version alpha du produit avec preuves appareil ; déclenche la création des comptes Store par l'opérateur |

ALPHA est le jalon retenu ici par l'opérateur ; les dates de bêta citées dans l'ancienne passation ne constituent
pas une échéance reconduite par ce document. Les tranches futures ne sont pas ouvertes par leur présence ici.

## STORE-00 — décisions et préparation en parallèle, dès maintenant

Le suivi démarre maintenant ; aucune création de compte, souscription payante ou publication n'a été effectuée.
L'agent prépare les éléments ; l'opérateur décide les identifiants, les entités et les accès.

| Sujet | Décision à obtenir maintenant | Réalisation dépendante | État au démarrage |
|---|---|---|---|
| Identifiant définitif iOS / Android | Choisir les identifiants et l'entité propriétaire avant upload Store ; ne pas reconduire `dev.auren.vnext.lab` par défaut | Configuration de distribution revue dans PLAT | Ouvert |
| Apple Developer / Google Play | Comptes personnels au nom de l'opérateur ; il les créera à l'atteinte de la version alpha | Distribution et signature Store après création des comptes | DÉCIDÉ par l'opérateur le 2026-11-03 ; aucune création anticipée |
| Suppression de compte | Fixer le contrat d'effacement et l'expérience, sans contredire les invariants historiques ; tranche de conception dédiée si conflit | MOB-03 puis API/UX autorisées | Ouvert ; aucune suppression implémentée |
| Confidentialité | Identifier le responsable, l'URL publique et le contenu correspondant aux traitements réellement livrés | Documents, lien dans l'app et métadonnées Store | Ouvert |
| OTA | Choisir canaux/runtime, stratégie de rollback et distinguer code natif / mise à jour compatible | PLAT / change Expo Updates distinct | Ouvert ; aucune OTA publiée |

Avant la tranche Store, vérifier les politiques officielles alors applicables et les preuves de réalisation.
La liste ci-dessus est un registre de travail issu de l'opérateur, pas une validation réglementaire ou Store.
La version alpha du produit et sa diffusion sur les Stores sont deux jalons : conformément à la réponse de
l'opérateur, aucune ouverture de compte n'est demandée avant l'alpha ; la diffusion Store suit leur création.

## Voie assets indépendante

Séquence précisée par le recadrage du 5 novembre :

`master mannequin → Smith incliné START/END → fiche d'exercice native pilote → sept Push A → règles de production série → catalogue restant`

Le catalogue ne part pas en production série avant validation de son composant consommateur. Les équipements suivent leurs besoins MOB-08/09 ; MOTION-V2 reste différé et séparé de toute revendication d'activation musculaire.

Elle progresse sous les contrats d'assets/provenance et les revues visuelles existantes, sans ajouter de seuils
E7 ni d'anatomie inventés. Un asset validé sur banc n'est pas automatiquement intégré à un écran produit.

## Règles de progression

- OpenSpec + contrats AUREN + skills Codex ; aucun Spec Kit ajouté.
- Une branche et une PR par change ; pas de mélange CODX-00 / CI-01 / MOB-02.
- Chaque compte rendu cite les SHA et distingue exécuté aujourd'hui / rapport historique / décision encore ouverte.
- Une fin de tâche dans OpenSpec n'est ni une approbation visuelle ni une preuve appareil.

## GOV-SONAR-01 — politique temporaire MVP

PR #348 mergée `cc80ddd` : Sonar ADVISORY / NON-BLOCKING, vrai ERROR conservé. QA,lint,visuel et mobile
sont requis après vérification API ; OpenSpec strict/scope/protocole et sécurité existante restent obligatoires.
Référence : `SONAR_TEMPORARY_MVP_POLICY.md`. Revue sécurité/qualité avant bêta externe élargie,paiements,
photos/mesures sensibles ou production. Aucun build MOB-02 ouvert par ces clôtures ;préflight final après
intégration documentaire et rebase de la proposition existante.

## Direction opérateur — composants visuels puis alimentation scientifique, 5 novembre

Après le socle du critical path, enrichir les tranches successives par les composants consommateurs, leurs états inconnus et les emplacements d'assets, en suivant le manifeste et les baselines. Les prompts du workstream scientifique seront fournis par l'opérateur. Cette préparation n'autorise ni moteur fictif, ni donnée physiologique inventée, ni nouvelle identité. L'ouverture de chaque tranche et les validations de composition/rendu restent applicables ; le premier plan garde sa dépendance SCI-P01/P02. Priorité immédiate indépendante : préférences existantes natives (MOB-03 4.2), croquis ciblé accepté, rendu et preuves encore à obtenir.
