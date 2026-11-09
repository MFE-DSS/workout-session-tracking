# science/calibration-encounter-extensions Specification

## Purpose
Définir les six rencontres scientifiques isolées qui permettent d'acquérir des
observations provisoirement qualifiées pour les réalisations du premier plan
V3 limité. Préserver familiarisation au réglage choisi, provenance, inconnus,
retrait et autorités historiques sans charge initiale calculée ou activation produit.

## Requirements

### Requirement: Six realization policies remain explicit
Le successeur SHALL identifier séparément chest-press-machine, rowing-chest-supported, romanian-deadlift-halteres, tirage-poulie-haute-prise-neutre, elevations-laterales-machine et releves-mollets-debout-machine, leur realization_ref V3 et leur admission/revue. Une admission historique de candidat SHALL NOT valoir admission de premier usage. Le pilote historique SHALL rester inchangé.
#### Scenario: Pulldown name matches but attachment does not
- WHEN le candidat est nommé tirage mais le contexte ne prouve pas la réalisation câble/prise neutre exacte
- THEN les nouvelles consignes physiques restent indisponibles ; une notice d'un autre dispositif ne comble pas ce manque.

### Requirement: Loaded familiarization precedes every qualifying attempt
Aide et installation SHALL être ouvertes sans sept épisodes ou charge initiale. INITIATE_TRIAL, ACCEPT_EXACT_SETTING et QUALIFIED SHALL exiger familiarisation explicite au réglage choisi, après préparation/choix/contexte et avant essai. Rehearsal sans haltères SHALL NOT devenir essai PER_IMPLEMENT, zéro kg, qualification ou série de travail.
#### Scenario: RDL user has only an unloaded rehearsal
- WHEN une familiarisation sans charge est rapportée mais aucun réglage/haltères et confirmation applicables ne sont acquis
- THEN aucun essai chargé ou qualification n'est autorisé.
#### Scenario: Setting changed after familiarization
- WHEN un nouveau réglage est choisi sans familiarisation applicable à ce choix
- THEN l'ancienne confirmation ou un booléen sur l'essai ne contourne pas la porte de qualification.

### Requirement: Typed observations and withdrawal remain authoritative
Les réglages machine affichés SHALL rester MACHINE_DISPLAY_KG, ceux du RDL PER_IMPLEMENT ; aucun total/incrément/charge personnelle SHALL être calculé. UNKNOWN et préoccupation SHALL fermer les consignes sous leurs règles ; nouvel ID SHALL NOT annuler un blocage et l'enregistrement d'un fait SHALL NOT autoriser sa répétition.
#### Scenario: Concern followed by a fresh encounter identifier
- WHEN une autre rencontre est créée sans politique de reprise après préoccupation
- THEN le blocage est conservé et aucune promotion de confiance ou retry automatique n'est offert.

### Requirement: Positive bridge uses actual published authorities
Six épisodes qualifiés SHALL provenir des évaluateurs/validateurs réels sous publication revue ; le septième SHALL provenir du pilote historique. Le vrai producteur/validateur V3 SHALL conserver ses sept conditions, le temps inconnu et son ack exact. Un schéma valide ou une fixture SHALL NOT créer l'admission.
#### Scenario: One realization lacks admissible first-use procedure
- WHEN une des six procédures n'a pas de décision scientifique défendable
- THEN elle reste non admise, le manque est identifié et aucun sous-ensemble n'est déclaré parcours complet.

### Requirement: Historical and runtime boundaries stay preserved
L'échange encounter1.0.0 et FirstPlan V1/V2/V3, anciens sources/pins/exports SHALL rester rejouables. Ce scope isolé SHALL NOT changer API/SDK/UI/packaging produit ni activer données personnelles ou déploiement.
#### Scenario: New isolated authority is built successfully
- WHEN le nouveau bundle passe les tests et la revue SCI
- THEN cela produit un handoff versionné pour PLAN, pas un import produit ou une autorisation runtime implicite.
