# Proposal — native-feature-migration-map (MOB-00)

## Why

La migration vers l'application native (iOS + Android) n'a pas d'inventaire de ce qu'elle doit reprendre. Les documents existants couvrent des morceaux (vNext §2 par actif, `AUREN_INSTRUMENTS §6.3` par gabarit, `AUREN_UI_BLUEPRINT §5ter.3` pour ~13 capacités) mais aucun ne liste les **110 routes** réellement montées ni ne dit, fonction par fonction, ce que devient chacune. Sans cet inventaire, des fonctions passent entre les mailles (profil, poids, programmes personnels, équipement, historique, récupération…), et la navigation native (MOB-01) se déciderait sans connaître ce qu'elle doit porter. Cette matrice devient le backlog produit.

## What Changes

- **Un inventaire lisible par machine** (`openspec/changes/native-feature-migration-map/inventory.yaml`, puis spec vivante à l'archive) : une entrée par **fonction utilisateur**, avec FEATURE · LEGACY LOCATION · DOMAIN OWNER · API · DATA · USER ACTIONS · NATIVE DESTINATION · STATUS · DEPENDENCIES · VISUAL ASSETS · MIGRATION RISK.
- **Chaque route montée y est rattachée** : la liste est tirée de `app.routes` (110 routes d'API à `36b971a`, 18 modules), jamais d'une mémoire ou d'un `grep`.
- **STATUS** dans la règle de migration du pilotage : `KEEP_DOMAIN` · `REWRITE_NATIVE` · `WEB_ONLY` · `DEPRECATE` · `BLOCKED` (dépendance nommée).
- **Fonctions absentes du web mais demandées** (onboarding, poids en série temporelle, photos de progression, abonnement, exercice personnalisé) : inscrites comme `BLOCKED` ou à concevoir, avec leur dépendance — sans rien inventer de leur contenu.
- **Une garde** (`tests/`) : toute route montée par l'application doit figurer dans l'inventaire ; une route ajoutée sans classement fait échouer la CI.
- **Un rendu lisible** (tableau par famille) pour l'opérateur, généré depuis le YAML.

## Capabilities

### New Capabilities
- `mobile/feature-migration-map` : l'inventaire des fonctions web et leur destination native, et la règle qui le tient exhaustif quand une route apparaît.

### Modified Capabilities
- (aucune)

## Non-goals (hors périmètre)

- Aucun code produit, aucune route modifiée, aucun écran.
- Aucune décision de navigation (MOB-01) ni d'ordre de livraison au-delà de ce que dit la roadmap de l'opérateur ; l'inventaire **informe** ces décisions, il ne les prend pas.
- Aucune migration de la documentation existante : elle est citée, pas recopiée.
- Pas de conception des fonctions nouvelles (onboarding, photos, abonnement) : seulement leur place et leurs dépendances.

## Dépendances bloquantes

- Aucune technique. La revue de l'opérateur porte sur les STATUS proposés : `DEPRECATE` et `WEB_ONLY` sont des décisions produit, présentées comme propositions.

## Impact

- `openspec/changes/native-feature-migration-map/` (inventaire, rendu), `tests/` (une garde d'exhaustivité, stdlib + YAML).
- `docs/strategy/SPEC_REGISTRY.md` (ligne MOB-00), rapport de sprint.
- Tier attendu : `isolated` (un test neuf, des fichiers neufs).
