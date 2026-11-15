# Spec Delta — mobile/owned-body-measurements

## ADDED Requirements

### Requirement: Acquisition canonique datée
Le système SHALL écrire les observations manuelles propriétaires dans BodyMeasurement, en kg/cm et selon BodyConsent pertinent ; il MUST NOT créer une seconde série, copier User.weight_kg ou poids de séance dans la chronologie, ni inventer une date d'acquisition.
#### Scenario: Deux observations le même jour
- **WHEN** un poids puis un tour sont réellement saisis à la même date
- **THEN** deux racines distinctes sont conservées sans upsert

### Requirement: Corrections par versions et provenance
Une correction SHALL insérer une nouvelle version dans BodyMeasurement liée à la tête possédée ; l'original MUST rester inchangé, les champs absents et leur provenance hérités, les null explicites effacés sur la tête. Une correction MUST NOT compter comme nouvelle observation indépendante.
#### Scenario: Correction d'un tour
- **WHEN** seul waist_cm est corrigé
- **THEN** nouvelle tête et original consultable, poids/bras et sources hérités, seul champ corrigé atteste nouvelle provenance

### Requirement: Courant distinct de l'audit
Tous lecteurs courants concernés SHALL utiliser les têtes non effacées ; une version remplacée MUST NOT devenir repli d'un champ vidé. L'audit SHALL distinguer CURRENT et SUPERSEDED. Les formules scientifiques MUST rester inchangées.
#### Scenario: Effacement de champ
- **WHEN** le poids d'une tête est explicitement null après correction
- **THEN** l'ancien poids de cette racine n'alimente ni Progrès ni un lecteur dérivé

### Requirement: Concurrence et replay communs
Les writers natifs et SSR SHALL participer à la même garde transactionnelle ; replay exact propriétaire SHALL précéder CAS/permission de nouvelle mutation. Une tête SHALL avoir un seul successeur de correction.
#### Scenario: Deux corrections concurrentes
- **WHEN** deux connexions corrigent la même tête sous le même token
- **THEN** une seule réussit et l'autre reçoit conflit sans branche ni perte de l'original

### Requirement: Identité et migration additives
L'allocation SQLite CREATE/CORRECT SHALL dépasser les ids et références globales réservées sous vraie transaction d'écriture ; migration MUST NOT backfiller/reconstruire/modifier les anciennes lignes.
#### Scenario: Table vide après effacement
- **WHEN** un nouveau fait est créé après suppression de l'id maximal
- **THEN** son id dépasse les références retenues tous owners confondus et un ancien reçu ne vise pas ce nouveau fait

### Requirement: Effacement réel explicite
L'effacement individuel confirmé SHALL supprimer les nombres de toutes les versions de la racine possédée, sans résurrection. Metadata/réservations/copies locales MUST rester identifiées comme copies DATA ; une correction conservée MUST NOT être présentée comme effacement.
#### Scenario: Supprimer une tête corrigée
- **WHEN** l'utilisateur confirme l'effacement de son relevé et de ses versions sous token courant
- **THEN** aucune version numérique de cette racine ne reste dans BodyMeasurement et le reçu minimal est rejouable

### Requirement: Compatibilité et incertitude
Poids v1 SHALL conserver sa forme et son décodeur tout en filtrant les versions remplacées ; le nouveau client BODY SHALL afficher provenance/qualité réelles dans Progrès avec le graphique existant. Nonfinis/missing/UNKNOWN MUST rester distincts sans NaN JSON ou zéro inventé.
#### Scenario: Source héritée inconnue
- **WHEN** une ancienne valeur sans preuve d'acquisition est recopiée dans une correction
- **THEN** sa provenance reste UNKNOWN et elle n'est pas requalifiée en nouvelle mesure humaine

### Requirement: Reprise propriétaire durable
Le client SHALL persister la commande exacte avant HTTP dans sa partition BODY et réconcilier sous même owner/backend après interruption. Il MUST NOT déduire un refus depuis timeout ou créer une nouvelle clé depuis un GET absent.
#### Scenario: Kill après commit serveur
- **WHEN** l'app est tuée avant ACK local
- **THEN** même clé/corps récupère le reçu original sans double fait et le compte B ne lit ni ne rejoue le payload A

### Requirement: Autorisations et jalons distincts
Le build SHALL attendre le GO explicite amendement/scope/G1 ; les pixels SHALL être acceptés avant commit UI. Engineering merge, integration candidate et external release MUST rester distincts ; aucune activation/APK/OTA ne découle automatiquement du merge.
#### Scenario: Proposition seule
- **WHEN** ce dossier existe sans GO du scope révisé
- **THEN** aucun writer/migration/UI/traitement réel n'est déclaré livré
