## ADDED Requirements

### Requirement: Construction propriétaire et identités
Le constructeur SHALL conserver UserProgram comme source et sélectionner un exercice par identité canonique serveur résolue sans fabriquer de mouvement ou de prescription. Les slots manuels historiques non résolus SHALL pouvoir être conservés inchangés sans nouvelle sélection ; aucun faux statut canonique ne leur est attribué. Les séries/plages SHALL être déclarées par l’utilisateur et rester des faits planifiés.

#### Scenario: Identité devenue inconnue
- **WHEN** la sélection ne se résout plus exactement à son identité et nom canonique applicables
- **THEN** l’écriture est refusée sans substitution fuzzy ni identité inventée.

### Requirement: Transaction et reprise
Toute mutation SHALL conserver commande/reçu et effet domaine atomiquement, sous propriétaire et digest courant. La sauvegarde locale SHALL précéder HTTP et les réponses perdues MUST NOT déclencher de nouveau POST automatique.

#### Scenario: Publication interrompue
- **WHEN** un échec survient avant le commit commun de publication et reçu
- **THEN** aucun template partiel n’est publié et le rejeu ne crée pas de doublon.

#### Scenario: Changement concurrent ou compte étranger
- **WHEN** le digest courant diffère ou le compte demande une source étrangère
- **THEN** le conflit est409 ou le refus404 identique à l’inconnu, sans écrasement ni divulgation.

### Requirement: Publication et historique
VALIDATED SHALL désigner une validation de structure distincte de la publication, et une modification de publié SHALL préserver les templates et occurrences historiques via un cycle explicite. Le départ SHALL rester soumis aux gates MOB06 Legacy/V3.

#### Scenario: Programme publié modifié
- **WHEN** l’utilisateur confirme un nouveau cycle d’édition
- **THEN** les anciennes séances possédées gardent leurs identités, prescriptions et faits.

#### Scenario: Programme historique avec mouvement manuel
- **WHEN** un slot existant ne se résout pas dans le picker canonique et l’utilisateur le conserve
- **THEN** son contenu est préservé sous identité/digest propriétaire sans le transformer en exercice canonique ni bloquer le renommage du programme.

#### Scenario: Ancien formulaire web et quota concurrent
- **WHEN** un formulaire web devenu obsolète écrit après mutation native, ou deux créations réclament le dernier emplacement quota
- **THEN** le kernel commun refuse le conflit CAS sans remplacer l’arbre et n’autorise qu’une création dans le quota.

### Requirement: Préconditions web et conservation du protocole
Les writers web et natifs SHALL utiliser un kernel propriétaire commun pour relecture/CAS/quota et mutation. Les formulaires web périmés ou sans précondition MUST NOT remplacer l’arbre. La saisie libre web et les slots manuels historiques SHALL rester conservés sans nouvelle admission canonique.

#### Scenario: Page rendue avant la nouvelle précondition
- **WHEN** une ancienne page sans jeton de source tente une mutation
- **THEN** la précondition est refusée avec relecture explicite, sans mutation partielle ni données perdues.
