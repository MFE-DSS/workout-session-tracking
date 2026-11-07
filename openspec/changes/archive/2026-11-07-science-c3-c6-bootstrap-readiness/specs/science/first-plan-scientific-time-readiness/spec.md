## ADDED Requirements

### Requirement: Explicit independent successor
Le futur contrat v3 SHALL représenter séparément l’admissibilité scientifique, l’état temporel et la permission produit. Il SHALL être négocié explicitement ; les contrats v1/v2 et leurs gates temporelles SHALL rester inchangés.
#### Scenario: Uncertain time on an older consumer
- WHEN un résultat successeur avec temps incertain arrive à un consommateur v1/v2
- THEN il n’est ni converti en READY ancien ni traité comme durée SUPPORTED.

### Requirement: No start authority from scientific label alone
SCIENTIFICALLY_READY SHALL nécessiter une autorité scientifique complète applicable et SHALL NOT conférer à lui seul un droit de démarrage. Sans politique produit admise, start_permission SHALL rester DENIED.
#### Scenario: Sufficient facts with no approved exploration policy
- WHEN les faits sont suffisants mais la permission TIME_UNCERTAIN n’est pas admise
- THEN aucun démarrage n’est autorisé depuis un label scientifique ou un acknowledgement fourni dans le corps client.

### Requirement: Honest structural time reasoning
Le calcul temporel SHALL conserver ses composantes inconnues et la portée de sa borne. Une borne partielle de repos sous le budget SHALL NOT prouver une borne haute ou compatibilité positive.
#### Scenario: Prescribed rests fit but setup is unknown
- WHEN les repos prescrits sont sous le budget et préparation/travail/opérations restent inconnus
- THEN le temps reste BUDGET_UNCERTAIN, sans secondes fictives ni facteur de salle.
#### Scenario: Proven rest floor already consumes the budget
- WHEN une borne de repos applicable atteint ou dépasse le budget d’une séance non vide exigeant du travail de durée strictement positive
- THEN cette configuration est STRUCTURALLY_TOO_LONG, sans déclarer tous les autres plans impossibles.

### Requirement: Contextual calibration with non-assessable outcomes
Le protocole successeur SHALL distinguer observation insuffisante, effort déclaré et réglage accepté ; il SHALL préserver sujet/réalisation/appareil/côté/unité/source/date et ne transférer aucune charge.
#### Scenario: A trial stops early due to interruption
- WHEN une tentative comporte peu de répétitions mais la cause est une interruption ou inconnue
- THEN le moteur ne conclut pas automatiquement « charge trop lourde ».
#### Scenario: Setting increment direction is unknown
- WHEN aucun incrément et sens d’effort du dispositif ne sont confirmés
- THEN aucun prochain kg/crans chiffrés n’est proposé depuis un pourcentage générique.

### Requirement: Concerns and time limit preserve facts
Le futur protocole SHALL conserver les préoccupations, interruptions et faits incomplets. Il SHALL NOT imposer une poursuite, un retry ou des repos raccourcis pour respecter artificiellement un budget.
#### Scenario: User reports concern or reaches the declared limit
- WHEN une préoccupation ou limite utilisateur est signalée
- THEN le protocole propose la sortie/revue applicable et conserve les faits, sans succès ou durée exacte inventés.

### Requirement: Reviewed authority before implementation
Seul le build isolé étape1 explicitement approuvé SHALL être réalisé : types/schémas/protocole/validations et exemples négatifs. Tout binding, producteur, statut positif autoritaire ou activation SHALL attendre ses décisions et périmètres approuvés applicables. Un label positif structurel SHALL NOT constituer une autorité.
#### Scenario: Preparatory packet contains recommended admission labels
- WHEN un paquet reçu comporte ADMIT et une recommandation RouteB à approuver
- THEN il est conservé comme source de doctrine, sans ajouter automatiquement des bindings dans un registre ni générer une fixture READY.
