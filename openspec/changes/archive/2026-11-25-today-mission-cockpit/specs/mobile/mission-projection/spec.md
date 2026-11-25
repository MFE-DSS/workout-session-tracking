## MODIFIED Requirements

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

## ADDED Requirements

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
