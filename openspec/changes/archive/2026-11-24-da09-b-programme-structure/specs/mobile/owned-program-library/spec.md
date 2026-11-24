## ADDED Requirements

### Requirement: Composition structurelle sourcée du programme
Le consommateur natif SHALL distinguer les comptes agrégés de l’index et la distribution réellement reçue au détail, conserver l’ordre des séances et des positions d’exercices, et représenter les prescriptions typées sans inventer un programme actif ou un calendrier.

#### Scenario: Composition partielle ou bornée
- **WHEN** des comptes, exercices ou rep_targets sont absents, partiels ou dépassent la borne graphique
- **THEN** la qualification et le reliquat exact restent visibles ou consultables
- **AND** aucune quantité manquante ne devient zéro ou distribution fabriquée

### Requirement: Module sélectionnable et commande propriétaire située
Le consommateur SHALL garder les actions attachées à la source et à la sélection actuelles, préserver PUBLISHED versus VALIDATED et les gardes natives Legacy/V3 existantes, et distinguer une création inconnue d’une occurrence propriétaire retrouvée.

#### Scenario: Sélection et départ incertain
- **WHEN** une séance est sélectionnée ou une réponse de création est perdue
- **THEN** la sélection seule ne crée rien et aucun POST n’est rejoué automatiquement
- **AND** la vérification et l’adoption explicite conservent leurs callbacks et identités existants

### Requirement: Prescriptions visibles et accessibles concordantes
Le consommateur SHALL produire le dessin et le libellé accessible de la séance à partir des mêmes groupes ordonnés, avec exercices, répétitions, préparations et reliquats reçus, et conserver les commandes atteignables par reflow/défilement.

#### Scenario: Ordre et nombreuses prescriptions
- **WHEN** les tableaux reçus ne suivent pas leurs positions ou dépassent les bornes de rendu
- **THEN** chaque mouvement affiché est annoncé une fois dans le même ordre, avec les unités et reliquats correspondants
- **AND** les valeurs et l’action réelle restent consultables sans réduction du texte critique
