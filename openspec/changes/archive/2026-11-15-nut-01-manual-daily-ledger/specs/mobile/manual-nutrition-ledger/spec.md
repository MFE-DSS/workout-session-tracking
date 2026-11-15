# Spec Delta — mobile/manual-nutrition-ledger

## ADDED Requirements

### Requirement: Journal manuel quotidien autonome
Le système SHALL servir un agrégat quotidien explicitement déclaré kcal/P/C/F, date/zone/provenance, sans fournisseur. Il MUST distinguer null et zéro et MUST NOT fabriquer des apports ou recommandations.
#### Scenario: Calories connues seulement
- **WHEN** seul le total kcal est saisi
- **THEN** les macros restent inconnues et le jour n'est pas automatiquement complet

### Requirement: Corrections et complétude explicites
Une correction SHALL append une révision propriétaire sous CAS sans modifier l'original. La tête seule SHALL alimenter totaux/graphique. La complétude SHALL rester un geste distinct et être invalidée par une mutation sans nouvelle confirmation exacte.
#### Scenario: Corriger un jour terminé
- **WHEN** un apport est modifié sans reconfirmation de complétude
- **THEN** la nouvelle tête est partielle et l'ancienne demeure auditée sans double compte

### Requirement: Cibles utilisateur sourcées
Les cibles SHALL être saisies/versionnées par l'utilisateur et liées aux jours par référence exacte propriétaire. Variantes entraînement/repos MUST rester un choix humain sans inférence depuis absence de séance.
#### Scenario: Changement de cible
- **WHEN** un preset est modifié après un jour confirmé
- **THEN** la comparaison historique de ce jour conserve sa référence d'origine

### Requirement: Histoire et tendance factuelles
Les lectures SHALL distinguer connu/absent/partiel/retiré et expliciter la couverture de chaque somme/différence. Elles MUST NOT interpoler l'inconnu ou comparer périodes non appariées.
#### Scenario: Trois jours renseignés sur sept
- **WHEN** la semaine contient trois apports connus et quatre absents
- **THEN** le total est étiqueté renseigné sur trois jours, pas apport complet de sept jours

### Requirement: Reprise et isolation propriétaires
Commandes et reçus SHALL être atomiques côté serveur et durables localement avant HTTP, sous owner/backend et namespace DAY/TARGET. Replay exact SHALL précéder CAS et nouvelle permission ; timeout MUST rester inconnu.
#### Scenario: Réponse perdue
- **WHEN** un commit serveur est acquis avant kill client
- **THEN** même clé/corps retrouve son reçu sans double révision et B ne lit ni ne rejoue A

### Requirement: Permissions et modes futurs distincts
Le support nutrition SHALL utiliser une finalité distincte du consentement corporel et attendre ses gates de traitement réel. Les modes caméra/étiquette/barcode/texte MUST rester non servis avant leur scope propre ; ils MUST NOT bloquer la clôture du manuel.
#### Scenario: Aucun fournisseur autorisé
- **WHEN** le journal manuel contrôlé est construit et testé sous son GO
- **THEN** ses apports/cibles/historique fonctionnent sans clé, photo ou appel externe

### Requirement: Engineering distinct de release externe
Le scope SHALL attendre GO/G1 et pixels applicables ; merge SHALL alimenter le manifeste MVP sans APK/OTA automatique. DATA/physique/RC/déploiement MUST rester distincts.
#### Scenario: Merge du journal
- **WHEN** ses contrôles et revue sont acceptés
- **THEN** le reçu engineering ne prétend ni nouvel APK installé ni acceptation physique
