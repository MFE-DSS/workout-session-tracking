# mobile/training-history Specification

## Purpose
Fournir une lecture native propriétaire des séances, séries, occurrences d'exercice et mesures de poids datées, sans altérer les faits canoniques. Distinguer faits réalisés, prescription capturée, contexte absent et couverture incertaine ; préserver les unités typées et les contrats AUREN acceptés.

## Requirements

### Requirement: Lectures possédées bornées et sans mutation
Le système SHALL exposer des listes, détails et occurrences propriétaires paginés, no-store, sans altérer les faits canoniques ni présenter le catalogue actuel comme une ancienne prescription capturée.

#### Scenario: Référence étrangère ou modifiée
- **WHEN** le client demande une séance absente, étrangère ou sans propriétaire
- **THEN** le système retourne le même not-found privé
- **AND** une référence observée modifiée sur un objet possédé impose une actualisation plutôt qu'une fusion par ID numérique

#### Scenario: Page interrompue
- **WHEN** une continuation échoue ou que son scan borné reste partiel
- **THEN** les lignes confirmées restent distinctes de la continuation inconnue et de la couverture incomplète
- **AND** aucun historique vide ou snapshot immuable n'est déduit

### Requirement: Fréquence factuelle et planification inconnue
Le système SHALL distinguer statut enregistré, exclusion et séance complétée avec faits de travail sur une période civile explicite résolue serveur, sans reconstruire un calendrier prescrit depuis la cadence ou les templates courants.

#### Scenario: Clôture sans travail observé
- **WHEN** une séance completed ne contient aucun fait de série de travail complétée
- **THEN** son statut completed reste visible
- **AND** elle n'est pas comptée comme séance réalisée ou réussite d'un objectif planifié

#### Scenario: Semaine courante partielle
- **WHEN** quatre ou douze semaines civiles sont choisies
- **THEN** les bornes/fuseau exacts et la semaine courante partielle sont explicites
- **AND** un calendrier prescrit absent reste indisponible plutôt que zéro

### Requirement: Faits historiques typés et contexte préservé
Le système SHALL préserver la sémantique du réglage observé, l'équipement, la séparation prescription/observation et NON_EVALUABLE scientifique dans l'historique natif read-only.

#### Scenario: Charge par haltère ou affichage machine
- **WHEN** le client lit un réglage PER_IMPLEMENT ou MACHINE_DISPLAY_KG observé
- **THEN** sa valeur typée et son unité sont affichées sans conversion en masse externe totale
- **AND** un contexte absent ou différent empêche une comparaison inférée des charges

#### Scenario: Autorité de travail scientifique retirée
- **WHEN** une séance scientifique possédée est ouverte en lecture historique
- **THEN** ses observations vérifiées restent lisibles sous le contrat canonique existant
- **AND** le présentateur historique ne propose aucune commande de travail ou permission nouvelle

### Requirement: Chronologie canonique du poids dans Progress Core
Le système SHALL consommer le contrat existant de poids BodyMeasurement sous consentement et distinguer chronologie mesurée, qualité, couverture partielle et accès indisponible, sans nouveau modèle de poids ni écrivain.

#### Scenario: Lecture poids bloquée ou partielle
- **WHEN** consentement, flag corporel, transport ou pagination empêchent une lecture complète
- **THEN** le module poids affiche cet état indépendamment de l'historique des séances
- **AND** aucun fallback de poids profil, zéro pour manque ou tendance complète n'est inventé

#### Scenario: Dates identiques ou qualité invalide
- **WHEN** plusieurs IDs de mesure partagent une date ou qu'une mesure est non finie/hors bornes actuelles
- **THEN** les enregistrements et leur qualité restent accessibles
- **AND** seuls les points connus valides sont tracés sans moyenne, prédiction ou interpolation à travers les faits invalides

### Requirement: Consommateur natif réel et cycle de lecture isolé
Le système SHALL monter la famille Progrès dans les quatre onglets existants, invalider les réponses tardives de compte/sélection, conserver les composants AUREN LOCKED et obtenir les acceptations visuelles humaines applicables avant livraison UI.

#### Scenario: Changement de compte pendant une lecture
- **WHEN** la réponse du compte A arrive après passage au compte B
- **THEN** les valeurs A ne sont ni rendues ni fusionnées sous B
- **AND** le journal et les contrôleurs de mutation conservent leur propriétaire canonique unique

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
