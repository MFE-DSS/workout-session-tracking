## ADDED Requirements

### Requirement: Projection possédée et source explicite
La projection MISSION SHALL dériver le propriétaire de l'authentification et distinguer source historique, premier parcours et reprise typée sans confondre leurs permissions. requested_path et version SHALL être explicites et recoupés ; une négociation invalide MUST être refusée.

#### Scenario: Résultat d'un compte quitté
- **WHEN** une réponse arrive après logout, changement de propriétaire ou chemin
- **THEN** le consommateur l'ignore et ne remplace aucune donnée du compte courant.

### Requirement: Reprise prioritaire sans création de permission
Une séance ouverte possédée SHALL être prioritaire et reprendre via son profil canonique. Un résultat historique ou hors ligne MUST NOT autoriser une nouvelle consigne SCI.

#### Scenario: Séance SCI ouverte hors ligne
- **WHEN** une reprise V3 possède des faits locaux mais aucune applicabilité actuelle établie
- **THEN** lecture/journal/sortie restent accessibles suivant le contrat V3 et aucune nouvelle série de travail n'est autorisée par la projection.

### Requirement: Premier parcours sans fallback scientifique
Le chemin FIRST_USE SHALL réutiliser PLAN, ses producteurs/validateurs, ack et commande existants. Une lecture ou navigation MUST NOT fabriquer une acquisition, un ack, une séance ou remplacer une indisponibilité SCI par un READY historique.

#### Scenario: Producteur indisponible
- **WHEN** FIRST_USE ne dispose pas de son autorité/runtime actuel
- **THEN** une indisponibilité explicite est présentée sans nouveau start ni résultat de réussite.

#### Scenario: Premier handoff déjà créé
- **WHEN** une commande CREATED a déjà lié sa séance possédée
- **THEN** une relecture retrouve cette même séance et ne crée jamais une deuxième première séance.

### Requirement: Composition et commandes conservées
Les cartes historiques LOCKED, la raison et les zones serveur SHALL être conservées. La famille des nouveaux états SHALL obtenir croquis puis vrais pixels acceptés avant commit UI ; une action dominante ne masque aucune action obligatoire.

#### Scenario: Projet de nouvelle carte
- **WHEN** une orientation visible nouvelle est proposée
- **THEN** son information/source et ses états sont revus en une famille avec comparaison aux baselines intactes, sans cinquième onglet ni donnée décorative.


Réconciliation du mandat PILOT VALUE DELIVERY du10novembre : [PILOT_VALUE_SCOPE](../../../PILOT_VALUE_SCOPE.md) précise base canonique, option de navigation B, commandes locales et leases séquencés. Statut toujours NO_GO_BUILD/G1_PENDING.
