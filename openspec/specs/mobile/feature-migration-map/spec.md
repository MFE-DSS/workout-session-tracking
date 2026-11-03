# mobile/feature-migration-map Specification

## Purpose
Tient l'inventaire de toutes les fonctions de l'application web et de leur destination native, pour que la migration mobile ne perde aucune capacité et que le backlog produit parte d'une liste exhaustive.

## Requirements

### Requirement: Une entrée par fonction utilisateur
L'inventaire MUST décrire chaque fonction utilisateur par : FEATURE, LEGACY LOCATION, DOMAIN OWNER, API, DATA, USER ACTIONS, NATIVE DESTINATION, STATUS, DEPENDENCIES, VISUAL ASSETS, MIGRATION RISK.

#### Scenario: Entrée incomplète
- **WHEN** une entrée omet l'un des onze champs
- **THEN** la garde de l'inventaire échoue en nommant l'entrée et le champ manquant

### Requirement: Statut de migration fermé
Le STATUS de chaque fonction MUST être l'un de `KEEP_DOMAIN`, `REWRITE_NATIVE`, `WEB_ONLY`, `DEPRECATE`, `BLOCKED` ; un statut `BLOCKED` MUST nommer sa dépendance.

#### Scenario: Statut inconnu
- **WHEN** une entrée porte un statut hors de la liste
- **THEN** la garde échoue

#### Scenario: Blocage sans cause
- **WHEN** une entrée est `BLOCKED` sans dépendance nommée
- **THEN** la garde échoue

### Requirement: Toute route montée est inventoriée
Chaque route d'API montée par l'application web MUST être rattachée à exactement une fonction de l'inventaire ; la liste des routes est lue dans l'application, jamais recopiée à la main.

#### Scenario: Route ajoutée sans classement
- **WHEN** une nouvelle route est montée et n'apparaît dans aucune entrée
- **THEN** la garde échoue en nommant la méthode et le chemin de la route

#### Scenario: Route disparue
- **WHEN** une entrée cite une route que l'application ne monte plus
- **THEN** la garde échoue en nommant la route fantôme

### Requirement: Fonctions demandées absentes du web
Une fonction demandée par l'opérateur qui n'existe pas dans le web (onboarding, poids en série temporelle, photos de progression, abonnement, exercice personnalisé) MUST figurer dans l'inventaire sans route, avec ses dépendances, et MUST NOT recevoir de contenu inventé.

#### Scenario: Fonction sans existant
- **WHEN** l'inventaire liste « photos de progression »
- **THEN** l'entrée n'a pas de route, son statut est `BLOCKED`, et ses dépendances (conception, consentement, stockage, confidentialité) sont nommées
