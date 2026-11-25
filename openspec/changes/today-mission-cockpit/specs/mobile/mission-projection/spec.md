## MODIFIED Requirements

### Requirement: Composition et commandes conservées
Les cartes historiques V1 LOCKED, leurs quatre références et leurs primitives SHALL être conservées. Un nouveau consommateur cockpit Today/MISSION MAY les remplacer dans le seul chemin approuvé après amendement visuel borné, croquis puis vrais pixels acceptés. La trace exacte du moteur, les zones serveur et les commandes canoniques SHALL rester inchangées. Le libellé de nouveauté MAY être contextualisé comme absence de passage terminé retrouvé pour le modèle de séance, en conservant son suffixe d’incertitude et sa trace brute accessible ; les métadonnées de provenance/horizon SHALL décrire leur véritable portée sans inventer de récupération ; une action dominante MUST NOT masquer une action obligatoire.

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
