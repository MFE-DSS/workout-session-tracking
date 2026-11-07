## ADDED Requirements
### Requirement: Explicit successor contract
Le successeur SHALL annoncer request/result v2 et refuser conversion silencieuse depuis ou vers READY v1. Le client v1 SHALL rester défensif tant que PLAN n'a pas livré la négociation sous son scope.
#### Scenario: V2 sent to the existing client
- WHEN un payload v2 arrive au client ne supportant que v1
- THEN il est refusé ou déclaré non supporté, sans conversion ni READY inventé.
### Requirement: Honest qualitative coverage
Le rapport SHALL contenir quinze zones uniques avec sources/rôles/inconnus et distinguer couverture de déclaration et comptabilité numérique admise.
#### Scenario: Unsupported role in a selected exercise
- WHEN une contribution est UNKNOWN
- THEN elle ne devient ni crédit zéro ni faiblesse analysée pour compléter le rapport.
### Requirement: Operational load prescription
La prescription SHALL distinguer réglage observé accepté et bootstrap admis, avec réalisation/appareil/côté/unité et instruction/arrêt sourcés.
#### Scenario: Cold load is unknown
- WHEN aucune charge comparable actuelle n'est confirmée
- THEN un protocole bootstrap est nécessaire et aucun kg ne vient de poids/taille/sexe ou d'un autre exercice.
### Requirement: Supported complete duration before ready
READY SHALL requérir une base temporelle admise applicable couvrant travail/repos/préparation/calibration/opérations dans le budget déclaré, ainsi que toutes les autres gates exactes.
#### Scenario: Arithmetic fits without positive time authority
- WHEN les diagnostics calculent LIKELY_FITS mais la base positive n'est pas admise
- THEN le producteur ne retourne pas READY et conserve la cause temporelle explicite.
### Requirement: Trusted binding and preserved history
Le validateur SHALL contrôler subject/snapshot/version/digests/empreintes et autorité réelle ; les sources/pins/fixtures v1/v2 historiques SHALL rester rejouables.
#### Scenario: Client labels a policy approved
- WHEN le caller fournit APPROVED sans binding du registre de confiance applicable
- THEN la décision reste non admise ; un schéma valide ne crée pas de preuve.
### Requirement: No activation from a proposal
La préparation SHALL rester documentaire, et tout apply nouveau SHALL attendre sa revue de contrat/GO et ses preuves applicables.
#### Scenario: Operator asks to continue after isolated delivery
- WHEN l'opérateur relance le chemin critique sans avoir encore revu ce nouveau contrat
- THEN le delta concret est préparé et présenté, sans API/UI/collecte/activation implicite.
