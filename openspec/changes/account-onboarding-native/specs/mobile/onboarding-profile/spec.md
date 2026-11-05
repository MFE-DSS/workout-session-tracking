# Spec Delta — mobile/onboarding-profile

## Purpose

Définit l’acquisition progressive des déclarations utiles au compte mobile, avec provenance, absence explicite, historique de poids existant et consentement, sans transformer un prototype de labo en vérité produit.

## ADDED Requirements

### Requirement: Déclarations minimales et reprenables
L’onboarding MUST distinguer les données nécessaires au compte des déclarations facultatives et annoncer l’usage de chaque donnée demandée. Les déclarations enregistrées MUST survivre à la relance et une soumission répétée MUST NOT créer de doublons.

#### Scenario: Interruption du parcours
- **WHEN** l’utilisateur ferme puis rouvre l’app après un enregistrement confirmé
- **THEN** les déclarations confirmées sont reprises depuis leur source canonique, sans recommencer une création de compte

#### Scenario: Question facultative ignorée
- **WHEN** l’utilisateur ne déclare pas une donnée facultative
- **THEN** cette donnée reste absente et aucune préférence de labo ou valeur moyenne ne la remplace

#### Scenario: Réponse incertaine
- **WHEN** le réseau coupe pendant l’enregistrement
- **THEN** le client distingue saisie locale, attente et confirmation serveur ; il ne prétend pas avoir enregistré une déclaration non confirmée

### Requirement: Objectifs et unités explicitement définis
Les objectifs et choix d’unités MUST utiliser un vocabulaire, une finalité et une persistance approuvés. Un objectif déclaré MUST NOT devenir une calibration, une mesure corporelle ou une performance observée. La préparation MUST NOT inventer de champ canonique absent.

#### Scenario: Vocabulaire ou stockage non approuvé
- **WHEN** un choix n’existe que dans le labo et n’a pas de contrat produit accepté
- **THEN** son implémentation reste bloquée et il n’est ni collecté sans usage défini ni présenté comme déjà pris en charge

#### Scenario: Unité d’affichage approuvée
- **WHEN** l’utilisateur choisit une unité selon le contrat accepté
- **THEN** sa saisie, sa restitution et les conversions conservent le sens et la précision prévus sans réécrire l’historique stocké

### Requirement: Une seule chronologie de poids
Le poids daté MUST provenir de la chronologie corporelle canonique existante. Une donnée manquante MUST rester inconnue. La compatibilité avec un champ hérité MUST NOT créer une seconde série temporelle ni inventer une date de mesure.

#### Scenario: Historique existant
- **WHEN** l’utilisateur possède déjà des mesures de poids
- **THEN** les lectures mobiles retrouvent ses mesures et leurs dates sans les recopier dans une nouvelle chronologie

#### Scenario: Profil hérité sans mesure datée
- **WHEN** seul un poids de profil sans date de mesure existe
- **THEN** il n’est pas transformé en entrée historique fabriquée ; sa présentation suit la décision de compatibilité approuvée

#### Scenario: Mesure d’un autre propriétaire
- **WHEN** une lecture ou écriture cible une mesure étrangère au compte authentifié
- **THEN** elle est refusée et ne révèle pas sa valeur

### Requirement: Préférences déclarées et environnement canonique
La fréquence, les priorités et l’équipement MUST conserver les validations et vocabulaires canoniques. Non-déclaré et liste explicitement vide MUST rester distincts. L’environnement concret MUST utiliser ses identifiants existants sans inventer de disponibilité ou de substitution.

#### Scenario: Absence de déclaration
- **WHEN** aucun équipement ou aucune fréquence n’a été déclaré
- **THEN** le système n’affirme ni équipement complet ni fréquence par défaut

#### Scenario: Déclaration d’un environnement existant
- **WHEN** le compte choisit un environnement reconnu selon le parcours approuvé
- **THEN** les services canoniques valident ses identifiants et continuent de déterminer la faisabilité des séances

### Requirement: Consentement corporel séparé et révocable
Les données corporelles MUST respecter le consentement explicite, versionné et révocable existant. Consentir aux mesures MUST NOT autoriser des photos, une analyse d’image ou un fournisseur externe.

#### Scenario: Consentement absent
- **WHEN** le compte n’a pas accepté la finalité corporelle concernée
- **THEN** le mobile ne déclenche pas ce traitement et la création du compte ne vaut pas consentement implicite

#### Scenario: Retrait
- **WHEN** l’utilisateur retire le consentement selon le contrat canonique
- **THEN** le traitement futur cesse et les choix de suppression respectent la politique approuvée, sans promesse d’effacement non exécuté

### Requirement: Surfaces natives soumises au contrat visuel
Les nouvelles compositions d’onboarding MUST être acceptées par l’opérateur avant commit UI et réutiliser les primitives visuelles canoniques. Le web et les écrans de labo MUST NOT être portés comme référence pixel approuvée.

#### Scenario: Rendu non accepté
- **WHEN** une composition ne possède pas d’acceptation visuelle
- **THEN** elle reste un candidat et aucune nouvelle baseline n’est auto-approuvée


### Requirement: Adaptateur des déclarations canoniques existantes
La ressource mobile de déclarations MUST déléguer au service training_preferences existant. Son remplacement complet MUST exiger les trois clés héritées, conserver null distinct de [], refuser les champs supplémentaires et préserver l'environnement concret écrit séparément. Elle MUST NOT modifier la lecture minimale MOB-02 ni introduire de durée, objectif de labo ou effet scientifique nouveau.

#### Scenario: Remplacement incomplet
- **WHEN** le client omet un des trois champs hérités lors du PUT
- **THEN** la requête est refusée sans effacer de déclaration existante

#### Scenario: Réponse de remplacement perdue
- **WHEN** le client ne peut confirmer le résultat du PUT
- **THEN** il conserve un état inconnu, ne rejoue pas automatiquement l'écriture et permet une lecture explicite de l'état serveur

#### Scenario: Réponse après changement de compte
- **WHEN** une réponse de lecture ou d'écriture arrive après le départ du compte émetteur
- **THEN** le client l'annule sans exposer ces préférences au nouveau compte

### Requirement: Aucun inventaire matériel à gérer dans le parcours natif
Le recadrage opérateur du 5 novembre MUST primer sur la proposition d'acquisition manuelle. Le mobile MUST NOT demander une liste de matériel ni déduire un équipement complet d'une salle générique. Il MUST préserver les déclarations historiques lors d'une modification de fréquence ou de priorités. La proposition d'exercices et leur substitution MUST utiliser les règles canoniques ; un nouveau traitement de disponibilité inconnue requiert un contrat de domaine avant implémentation.

#### Scenario: Modification de fréquence sans inventaire
- **WHEN** l'utilisateur change sa fréquence depuis Profil
- **THEN** aucune famille ni liste d'objets ne lui est demandée et les déclarations de matériel existantes sont conservées

#### Scenario: Disponibilité non connue
- **WHEN** aucune preuve ne décrit la disponibilité d'un équipement
- **THEN** le mobile ne fabrique pas une compatibilité et ne remplace pas la décision de domaine par une liste de matériel obligatoire
