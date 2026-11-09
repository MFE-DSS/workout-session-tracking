## ADDED Requirements

### Requirement: Controlled PLAN acceptance records exact environment identity
La recette SHALL identifier source backend/client, bundle/inventaire/autorité,
schéma DB/config/flags et origine des données synthétiques. Elle SHALL NOT
interpréter un merge comme activation ou déploiement.
#### Scenario: Disposable backend is prepared
- WHEN le banc est initialisé depuis le runtime fusionné
- THEN sa base/bundle/config/génération sont conservés et aucune donnée personnelle ou migration de production n'est utilisée.

### Requirement: Native evidence is distinct from physical release acceptance
Les résultats SHALL distinguer consommateurs HTTP, simulateur/émulateur et
appareil physique. Une preuve physique SHALL nommer device/OS/build réellement
installé/backend et action observée ; sans ces pièces le gate SHALL rester ouvert.
#### Scenario: Simulator passes the owned first-plan flow
- WHEN une app native de test parcourt la chaîne sur simulateur
- THEN ce résultat reste recette synthétique de ce build/hôte et ne ferme pas Android/iPhone physiques ou releasealpha.

### Requirement: Rollback preserves facts and withdrawal closes new guidance
Le rollback contrôlé SHALL empêcher nouveaux traitements/consignes non autorisés
sans effacer journal, observations ou identités durables. Les risques packaging
SHALL être contextualisés sans modifier les gates ou qualifier tout l'historique de faux positif.
#### Scenario: QA authority is withdrawn after observations
- WHEN l'autorité opérationnelle du banc est retirée
- THEN les faits restent lisibles et aucune nouvelle consigne ou création non admissible n'est prétendue.
