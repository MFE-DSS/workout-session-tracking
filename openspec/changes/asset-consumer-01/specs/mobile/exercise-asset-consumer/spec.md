# Spec Delta — mobile/exercise-asset-consumer

## ADDED Requirements

### Requirement: Identité exacte et provenance de la paire
Le futur consommateur SHALL lier chaque paire à un asset ID/version, un exercice exact, une réalisation, un équipement, une provenance/droits et un master recevable. Il SHALL NOT remplacer une réalisation par homonymie ni traiter les références mannequin comme sources finales. START et END SHALL partager caméra, échelle, cadrage, matériel et version.

#### Scenario: Référence sans master de production
- **WHEN** seules les cinq références visuelles historiques sont disponibles
- **THEN** leur état reste référence acceptée / vectorisation requise / intégration bloquée et aucune illustration de production n'est déclarée reçue

#### Scenario: Paire incomplète ou réalisation incompatible
- **WHEN** un état, le matériel applicable ou une identité exacte manque
- **THEN** le média complet reste indisponible, avec fallback explicite, sans substitut approchant

### Requirement: Consommateur pilote avant production série
La voie assets SHALL conserver mannequin → Smith incliné START/END → fiche native pilote → sept Push A avant toute règle de série ou extension de catalogue. Le dossier SHALL distinguer ces sept Push A des sept réalisations de calibrage SCI.

#### Scenario: Smith et calibration
- **WHEN** une illustration Smith est préparée
- **THEN** aucune qualification de calibration des sept profils SCI ni équivalence avec chest-press-machine n'est inférée

### Requirement: Séparation illustration, instructions et localisation
La fiche SHALL présenter chaque information une fois, depuis sa source de données applicable. L'image SHALL NOT fournir l'autorité des instructions appareil, d'une permission de geste, d'une anatomie ou d'un effet. BodyMap SHALL garder son résolveur canonique et les onze zones existantes ; les vocabulaires SCI et BodyMap SHALL NOT être convertis implicitement.

#### Scenario: Instructions ou zones absentes
- **WHEN** aucune source d'instructions applicable ou aucune zone canonique n'est fournie
- **THEN** la fiche indique l'absence des instructions et n'invente ni texte gestuel ni zone active depuis l'illustration

### Requirement: Revue native et accessibilité avant intégration
La composition SHALL rester PROPOSED jusqu'au G1 opérateur. Une intégration future SHALL obtenir son GO BUILD, ses revues d'assets et vrais pixels iOS/Android avant commit UI. START/END SHALL être distinguables sans couleur, accessibles dans l'ordre, sans animation nécessaire ; le retour SHALL préserver l'état du parcours appelant.

#### Scenario: Documentation prête sans validation visuelle
- **WHEN** OpenSpec strict et le protocole documentaire passent
- **THEN** aucun G1, pixel accepté, master reçu ou état activé n'est déduit de ces checks
