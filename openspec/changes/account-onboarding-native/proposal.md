# Proposal — account-onboarding-native (MOB-03)

## Why

MOB-02 est mergé : la prochaine dépendance du chemin critique est l’entrée d’un utilisateur réel, sans création de compte sur le web ni préférences de labo présentées comme des faits. L’inventaire MOB-00 décrit déjà les domaines à conserver et les capacités qui restent bloquées.

## What Changes

- Préparer le cycle de compte natif : inscription, connexion existante, reprise d’authentification, changement de mot de passe, déconnexion et suppression demandée par le propriétaire.
- Définir un onboarding reprenable avec données minimales et finalité connue : objectif déclaré, unités, poids daté, préférences d’entraînement et environnement existant. Les choix non déclarés restent absents.
- Réutiliser les services canoniques d’authentification, de consentement, de mesures, de préférences et d’environnement. Garder la réinitialisation du mot de passe et l’export web selon MOB-00.
- Définir l’historique du poids depuis BodyMeasurement, sans seconde chronologie ni migration de données historiques implicitement autorisée.
- Définir les protections d’isolation, consentement versionné et retrait, révocation des jetons et traitement explicite du journal local lors des changements de compte.
- Préparer les décisions encore ouvertes ; aucun objectif de labo, unité non persistée, politique d’effacement ou nouvel écran n’est considéré approuvé par cette proposition.

## Capabilities

### New Capabilities
- `mobile/account-lifecycle` : entrée et sécurité du compte, cycle des credentials, déconnexion et suppression authentifiée.
- `mobile/onboarding-profile` : acquisition progressive des déclarations, unités, poids daté, préférences et environnement, avec consentement et provenance.

### Modified Capabilities
Aucune exigence vivante modifiée pendant cette préparation. L’inventaire MOB-00 reste la source de couverture ; ses routes seront actualisées dans l’implémentation approuvée, jamais avant leur existence.

## Impact

- Sources observées : `app/routers/auth_routes.py`, `mobile_api.py`, `app/models/user.py`, services `auth`, `device_auth`, `training_preferences`, `body_profile`, `measurements`, `body_ledger`, `equipment_model`, `environment_activation`, `environment_resolution`.
- Client concerné ensuite : authentification, coque et consommateurs connectés ; `OnboardingFlow.tsx` et `lab/profile.ts` restent des prototypes, pas des contrats produit.
- Le GET de préférence livré par MOB-02 reste compatible ; les futures API JSON sont à spécifier, sans réutiliser un cookie web comme Bearer.
- Aucune dépendance, migration, API, donnée utilisateur ou baseline changée ici. Base de préparation : merge MOB-02 `90da8461803e87897c3d8f48627c4b704b3cfcd6`.
- Références : MOB-00 `auth-register`, `account-password-change`, `onboarding`, `profile-physical`, `profile-training-preferences`, `body-measurements`, `body-consent`, `gym-equipment`, `account-deletion`.
- Réutiliser les primitives LOCKED `AUREN-MARK-V1`, les boutons, champs et feuilles canoniques de `components.tsx`. Aucune nouvelle composition d’onboarding n’est approuvée : revue opérateur du croquis et du rendu réel avant commit UI.

## Non-goals

Pas de code produit dans cette préparation ; pas de MISSION (MOB-04), journal/progrès (MOB-05), nouvel éditeur de salle/équipements (MOB-09), calibration E7, nouvelle métrique, photo/analyse corporelle, provider, profil octogone ou abonnements. Aucun effacement réel, backfill ou changement du statut de migration sans décision explicite.

## Blocking Decisions

- **D-MOB03-1 — objectifs et unités :** aucun stockage produit canonique pour l’objectif global ou le choix d’unité n’a été identifié dans User/TrainingPreferences ; le vocabulaire du labo ne suffit pas. Confirmer les usages, le vocabulaire et la persistance avant build.
- **D-MOB03-2 — poids :** BodyMeasurement est la chronologie existante ; User.weight_kg est un champ hérité distinct. Valider le lecteur de référence et sa compatibilité, sans double source ni historique inventé.
- **D-MOB03-3 — suppression :** pas d’API de suppression de compte observée. Valider l’inventaire d’effacement/rétention, la réauthentification et les commandes locales en attente avant toute action destructive ; ne pas transposer automatiquement la suppression d’une mesure à tout le compte.
- **D-MOB03-4 — UX :** acquisitions vraiment utiles, ordre reprenable et surfaces à accepter. L’équipement concret réutilise le domaine existant ; ses nouvelles surfaces riches et assets restent à MOB-09.
- Revue sécurité/qualité avant introduction des mesures sensibles selon GOV-SONAR-01 ; consentement existant `SPIGNOS_BODY_PRIVACY_AND_CONSENT_SPEC` à appliquer sans étendre aux photos.

## Exécution partielle autorisée — 5 novembre 2026

Le nouveau mandat opérateur autorise l'avancement sur le chemin critique pendant son absence. La préparation initiale évolue vers le socle API indépendant : inscription JSON avec validations/quota canoniques, changement authentifié du mot de passe et révocation. Aucun objectif/unité, poids, consentement, effacement ou écran nouveau n'est implémenté sans ses décisions. D-MOB03-1 à 4 restent ouverts. Les mentions de « préparation seulement » ci-dessus décrivent l'étape initiale, pas une approbation implicite de ces quatre décisions. Le plan et les résultats sont dans implementation-account-core.md et docs/SPRINT_MOB03_REPORT.md.

## Décision produit ultérieure — pas d'inventaire manuel

Le 5 novembre, après exposition du prototype, l'opérateur rejette la gestion d'une liste de matériel. Cette décision remplace la proposition d'acquisition manuelle initiale, sans supprimer le domaine d'environnement. Le mobile part du profil, présente les propositions du domaine et laisse substituer les exercices ; la résolution de compatibilité et de disponibilité inconnue doit être contractualisée avant intégration. Aucun catalogue manuel, éditeur de salles ou équipement complet supposé n'est autorisé par MOB-03. Les capacités web existantes restent conservées, sans être promues en exigence UX native. Voir le CR MOB-03 PO/architecte du 5 novembre.
