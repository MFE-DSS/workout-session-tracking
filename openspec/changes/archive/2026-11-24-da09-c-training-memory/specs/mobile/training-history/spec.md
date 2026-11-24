## ADDED Requirements

### Requirement: Semaines natives comme lecture instrumentale factuelle
Le consommateur SHALL représenter les occurrences comptées reçues par segments hebdomadaires, avec bornes exactes, fin exclusive et semaine courante partielle, sans calendrier prescrit, objectif ou progression inférés.

#### Scenario: Coupure de lecture pendant la semaine
- **WHEN** la fenêtre reçue s’arrête avant la fin de la semaine
- **THEN** la lecture indique sa coupure réelle et la fin exclusive dans le fuseau reçu
- **AND** les segments représentent uniquement le compte reçu, sans dater individuellement les occurrences

#### Scenario: Lecture non confirmée
- **WHEN** la lecture échoue sans page ou conserve une page précédente
- **THEN** le statut demeure explicite et aucun compte absent ne devient zéro

### Requirement: Observation de poids sélectionnée exacte et accessible
Le consommateur SHALL sélectionner les observations BodyMeasurement par identité, conserver leurs dates/unités/provenance/versions, employer une sélection historique neutre et fournir une lecture accessible atomique avec navigation séquentielle.

#### Scenario: Même date et même valeur
- **WHEN** plusieurs observations reçues ont une date et une valeur identiques
- **THEN** chaque identité reste sélectionnable et distinguable dans la lecture et l’annonce accessible
- **AND** aucune fusion, moyenne ou interpolation physiologique n’est inventée

#### Scenario: Jour déclaré et accès retiré
- **WHEN** une observation a une précision de jour déclaré
- **THEN** le jour n’est pas attribué à une heure de mesure inventée
- **AND** le retrait d’accord rend les valeurs et sources corporelles indisponibles

### Requirement: Lecture compacte des faits historiques typés
Le consommateur SHALL organiser les séries réalisées et occurrences en mémoire lisible, conserver unités/statuts/incertitudes et divulguer les sources sans modifier les contrats de commande ou les faits canoniques.

#### Scenario: Historique machine ou par haltère
- **WHEN** un réglage historique est MACHINE_DISPLAY_KG ou PER_IMPLEMENT
- **THEN** la valeur et son unité restent typées et aucune masse externe totale n’est calculée
- **AND** les prescriptions et valeurs manquantes restent distinctes des faits confirmés

#### Scenario: Texte agrandi dans les viewports qualifiés
- **WHEN** l’utilisateur consulte le parcours accepté à360/480dp et178,6%
- **THEN** le contenu et les commandes restent atteignables par reflow et défilement
- **AND** les limites D4, gestes TalkBack et recette physique non qualifiés restent consignées
