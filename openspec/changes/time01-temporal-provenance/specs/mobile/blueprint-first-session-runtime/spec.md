## ADDED Requirements

### Requirement: Restored execution time is not a fresh native clock anchor
Le client SHALL conserver server_now restauré comme information historique.
Il SHALL NOT l'apparier à un nouvel instant monotone pour fabriquer une date
actuelle non estimée. Une liaison fiable SHALL être acquise seulement depuis
une lecture d'exécution confirmée dans le contrôleur actuel, et SHALL être
invalidée à restore, pause et lecture échouée. Les opérations préparées SHALL
conserver leurs dates, corps et identités lors des reprises.
#### Scenario: Offline process restart restores an old execution
- WHEN le DTO SQLite date d'un processus précédent et aucune lecture fraîche ne réussit
- THEN une nouvelle date acquise est explicitement estimée ; l'ancien server_now ne devient pas une date actuelle vérifiée.
#### Scenario: Rendering stalls before the acquisition action
- WHEN le dernier rendu précède le clic d'acquisition
- THEN la date est prélevée à l'action depuis la liaison actuelle, pas depuis la valeur du rendu.
#### Scenario: A prepared operation survives restart
- WHEN une SET ou FINISH possède déjà une identité et un corps durables
- THEN aucune restauration ne renouvelle sa date ni son identité.
