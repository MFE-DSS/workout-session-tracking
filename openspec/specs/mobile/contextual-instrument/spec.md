# mobile/contextual-instrument Specification

## Purpose
Présenter une référence serveur strictement comparable dans l’occurrence V3 courante, tout en conservant l’indépendance du fait saisi, son identité et les autorités canoniques de commande, de temps et de reprise.

## Requirements

### Requirement: Référence serveur dans la même occurrence
L’instrument contextuel SHALL afficher une série précédente uniquement dans la même occurrence V3 propriétaire et le même exercice canonique, selon SAME_RECORDED_CONTEXT_V1, avec contexte connu intégralement identique, réglage typé et révision effective observée par une lecture serveur validée.

#### Scenario: Série antérieure au contexte connu
- **WHEN** la série immédiatement précédente est complétée avec une observation validée dans la même occurrence/exercice/binding et que le contexte complet correspond
- **THEN** son réglage et ses répétitions peuvent être présentés comme observation enregistrée secondaire
- **AND** les champs du fait courant restent indépendants et sans préremplissage

#### Scenario: Legacy ou contexte absent
- **WHEN** le contexte, l’observation effective, le propriétaire ou la cohérence de lecture ne peuvent être établis
- **THEN** aucune valeur de référence comparable n’est affichée
- **AND** absence et lecture inconnue/échouée restent distinctes sans bloquer une acquisition manuelle autrement permise

### Requirement: Retour situé et autorité conservée
L’instrument natif SHALL distinguer brouillon, fait local durable, attente/inconnu, reçu serveur et refus dans le contexte d’exercice, avec les autorités existantes de commande, temps, repos, propriétaire et journal.

#### Scenario: Réponse perdue après acceptation serveur
- **WHEN** le résultat de la commande canonique reste inconnu au client
- **THEN** l’instrument conserve le fait original et son identité d’opération comme à vérifier
- **AND** il ne crée pas de nouvelle mutation et n’appelle pas historique confirmé un fait non relu

#### Scenario: Reçu et relecture courante
- **WHEN** la commande d’origine est acquittée
- **THEN** son reçu peut être montré dans l’objet sans écran de statut supplémentaire obligatoire
- **AND** la relecture du fait reste une lecture propriétaire indépendante

### Requirement: Preuve native bornée et gates humains
UX11 SHALL obtenir l’autorisation de build, de convention d’affichage et de G1 avant code produit, puis l’acceptation des vrais pixels Android intégrés avant commit UI.

#### Scenario: Comparaison sur les mêmes données
- **WHEN** le paquet natif de décision UX11 est produit
- **THEN** sa paire principale avant/après utilise la même source canonique V3 et relève les activations de contrôles et transitions réelles
- **AND** il précise les limites émulateur/fonte/IME/appareil, sans gain de temps non mesuré ni permission OTA
