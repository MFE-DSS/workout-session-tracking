# Tasks

## 1. Inventaire

- [ ] 1.1 Exécuter `python scripts/check_scope.py` dans le worktree et suivre les vérifications locales qu'il exige
- [ ] 1.2 Extraire la liste des routes montées depuis `app.routes` du worktree (preuve que `app` est chargé depuis ce worktree) et la garder hors dépôt ; vérifier 110 routes d'API à la base du change
- [ ] 1.3 Écrire `inventory.yaml` : une entrée par fonction utilisateur, les onze champs, chaque route rattachée à une seule fonction, chaque fonction lue dans son routeur, son gabarit et son service ; vérifier qu'aucune route n'est orpheline
- [ ] 1.4 Ajouter les fonctions demandées absentes du web (onboarding, poids en série temporelle, photos de progression, abonnement, exercice personnalisé) en `BLOCKED` avec leurs dépendances ; vérifier qu'aucune n'a de contenu inventé
- [ ] 1.5 Vérifier à la main un échantillon d'au moins 10 entrées (route, gabarit, service) et consigner les corrections dans le rapport

## 2. Garde

- [ ] 2.1 Ajouter `tests/test_native_feature_migration_map.py` : champs obligatoires, statut fermé, `BLOCKED` avec dépendance, exhaustivité des routes dans les deux sens, exclusions nommées vérifiées ; vérifier qu'elle passe
- [ ] 2.2 Vérifier que la garde mord : une route retirée de l'inventaire, une route fantôme ajoutée, un statut inconnu, un `BLOCKED` sans dépendance — chacun la fait échouer (mutations hors dépôt)

## 3. Rendu et revue

- [ ] 3.1 Générer `inventory.md` (tableau par famille) depuis le YAML par un script du change ; vérifier qu'il correspond au YAML
- [ ] 3.2 Publier le rendu à l'opérateur, statuts `DEPRECATE` / `WEB_ONLY` marqués comme propositions ; consigner ses arbitrages
- [ ] 3.3 Rapport de sprint (§3 Brainstorming / Options / Risques / Choix, échantillon vérifié, verdict) et ligne du registre

## Workflow follow-up

- Archiver après merge : la spec vivante `mobile/feature-migration-map` et l'inventaire déménagent sous `openspec/specs/`, la garde suit le chemin.
- Les proposals `native-navigation-shell` (MOB-01) et `session-native-integration` (MOB-02) partent de cet inventaire.
