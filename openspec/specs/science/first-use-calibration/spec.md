# science/first-use-calibration Specification

## Purpose
Définir une rencontre scientifique isolée depuis zéro réglage qualifié, pour le pilote bilatéral leg-extensions-assises, sans charge initiale calculée ni permission de plan ou de série de travail. Préserver le binding V3 admis et ses sept qualifications ; runtime non servi.

## Requirements

### Requirement: Open without historical qualification
Le contrat de rencontre SHALL permettre d'ouvrir l'accompagnement avec zéro réglage qualifié. Il SHALL demander seulement les faits consommés par l'action suivante, sans inventaire global ou sept épisodes préalables.
#### Scenario: New user with no loads
- WHEN l'utilisateur n'a aucun réglage ni familiarisation confirmée
- THEN CALIBRATION_REQUIRED et les acquisitions utiles sont disponibles, sans charge initiale suggérée et sans autorisation de travail.

### Requirement: Scoped physical exploration
Une consigne physique positive SHALL exiger une politique de rencontre admise pour la réalisation et des instructions/contexte personnels applicables. Le premier pilote SHALL rester leg-extensions-assises bilatéral, sans disponibilité ou assistance inférée.
#### Scenario: Known machine name but unknown handling
- WHEN le nom du candidat est connu mais les instructions ou la manipulation ne sont pas établies
- THEN assistance/revue/acquisition restent possibles mais aucun essai chargé n'est autorisé depuis ce seul nom.

### Requirement: Observations are facts before qualification
Familiarisation, tentative, observation et acceptation SHALL garder leurs identités, dates, sources et sémantiques de réglage. Qualification SHALL satisfaire les conditions effectives C3, pas la seule forme du modèle ou le diagnostic historique.
#### Scenario: Short voluntary attempt
- WHEN la tentative réelle s'arrête avant la fenêtre de qualification sans préoccupation déclarée
- THEN le fait est OBSERVED, sans qualification ni augmentation automatique.
#### Scenario: Actual qualified provisional setting
- WHEN contexte/familiarisation/dernière tentative actuelle comparable et acceptation exacte satisfont toutes conditions C3 sans préoccupation
- THEN QUALIFIED référence le réglage observé provisoire et l'épisode portable, sans affirmer vrai RIR ou optimalité.

### Requirement: Concern cannot be reset by a new encounter
Préoccupation, échec ou qualité/gêne non résolues SHALL bloquer nouvelle consigne et retry. Le ledger propriétaire exhaustif et les prédécesseurs SHALL être vérifiés par le futur adaptateur autoritaire ; un ID neuf SHALL NOT effacer un blocage.
#### Scenario: Concern then new encounter identity
- WHEN une nouvelle rencontre est ouverte après préoccupation sans règle de reprise admise
- THEN elle conserve CONCERN_REVIEW et ne permet pas de recommencer automatiquement.

### Requirement: Calibration is separate from plan work
Une tentative de calibrage SHALL rester CALIBRATION_ACTIVITY. Elle SHALL NOT devenir une série de travail accomplie, un crédit d'exposition ou une permission SCIENTIFICALLY_READY par conversion.
#### Scenario: One exercise qualified
- WHEN le pilote fournit une observation qualifiée et les six autres sont absentes
- THEN l'observation est réutilisable mais le vrai producteur V3 conserve son exigence des sept réalisations qualifiées.

### Requirement: Existing authority and runtime preserved
Le binding V3 admis, les contrats et validateurs historiques SHALL rester inchangés. Nouveau contrat/GO BUILD/tests/fixtures SHALL NOT constituer admission, acquisition personnelle ou activation runtime.
#### Scenario: Synthetic end-to-end bridge
- WHEN un test fournit six autres épisodes explicitement synthétiques puis passe par loader/producteur/validateur V3 réels
- THEN il prouve l'interopérabilité technique uniquement, sans servir les fixtures ni prétendre avoir calibré une vraie personne.
