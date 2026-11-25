# mobile/mission-projection Specification

## Purpose
Fournir une orientation Aujourd’hui possédée, avec source explicite, reprise et commandes à vérifier prioritaires, sans nouvelle prescription ni changement de la carte MISSION verrouillée.

## Requirements

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
Les cartes historiques V1 LOCKED, leurs quatre références, primitives, zones serveur et commandes canoniques SHALL être conservées. Leur remplacement dans le seul chemin Today/MISSION approuvé SHALL exiger un amendement borné, G1 puis vrais pixels acceptés. La nouveauté et la provenance MAY être contextualisées selon les scénarios ci-dessous, sans inventer de récupération ni masquer une action obligatoire.

#### Scenario: Projet de nouvelle carte
- **WHEN** une orientation visible nouvelle est proposée
- **THEN** son information/source et ses états sont revus en une famille avec comparaison aux baselines intactes, sans cinquième onglet ni donnée décorative.

#### Scenario: Projet de nouveau cockpit
- **WHEN** la composition Today/MISSION est proposée
- **THEN** son information/source et ses états sont revus avec comparaison aux baselines V1 intactes et approbation propre avant apply
- **AND** aucun cinquième onglet, nouvelle donnée ou permission n’est créé

#### Scenario: Nouveauté et lecture partielle
- **WHEN** la raison reçue commence par « Jamais fait. », éventuellement suivie du suffixe canonique de lecture partielle
- **THEN** le rendu l’attribue au modèle de séance, conserve le suffixe reçu et rend la trace exacte accessible
- **AND** il ne conclut ni à l’absence de travail musculaire ni à une disponibilité physiologique

### Requirement: Préparation située sans mutation
Le consommateur SHALL déplier la préparation dans le même objet et conserver Démarrer ou l’action applicable accessible, sans étape intermédiaire ni mutation provoquée par la lecture.

#### Scenario: Préparer une proposition confirmée
- **WHEN** l’utilisateur ouvre ou ferme la préparation
- **THEN** seules les données déjà reçues sont révélées et aucun POST n’est émis
- **AND** l’action de démarrage demeure soumise aux gardes canoniques existantes


#### Scenario: Portée de la provenance historique
- **WHEN** la provenance ou l’horizon reçus sont affichés
- **THEN** ils décrivent leur véritable portée historique, sans inventer de récupération ni de borne datée absente
- **AND** la trace exacte du moteur reste accessible et une action dominante ne masque aucune action obligatoire
