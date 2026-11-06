# MOB-03 — socle API du compte Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** permettre l'inscription mobile et le changement authentifié du mot de passe avec les règles existantes, sans nouvelle composition UI ni donnée corporelle.
**Architecture:** un service partagé conserve les validations web ; les routes JSON délivrent les paires Bearer canoniques. Les contraintes uniques existantes garantissent qu'un rejeu ne crée pas un second compte. Après réponse perdue, la connexion existante sert à vérifier le compte ; aucun succès implicite ou retry automatique.
**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy, bcrypt et device_auth existants ; aucune dépendance ou migration.
**Spec:** proposal.md, design.md et specs/mobile/account-lifecycle/spec.md du présent change ; mandat opérateur du 5 novembre 2026.

## Global Constraints

- Mandat : avancer sur les fonctionnalités du chemin critique pendant l'absence de l'opérateur ; cette réalisation borne l'apply aux parties indépendantes de D-MOB03-1 à 4.
- D-MOB03-1 à 4 restent OPEN ; pas d'objectif/unité, poids, consentement corporel, suppression ou nouvel écran.
- Les routes web gardent leurs réponses et messages ; cookie web et Bearer restent séparés.
- Aucun secret dans logs/journal/export ; aucune donnée de production utilisée dans les tests.
- Le client QA et sa recette MOB-02 restent inchangés ; pas de déploiement.
- check_scope réel avant vérifications ; broad sweep auth/mobile consommateur ; jamais de full sweep local systématique.

## Review Focus

- Deux inscriptions simultanées pour le même nom : un seul User, échec corrigeable pour l'autre, aucune session orpheline.
- Réponse de création perdue : rejeu refusé sans duplication et récupération par login normal.
- Mot de passe Unicode au-delà de 72 octets : refus avant bcrypt, comportement web maintenu.
- Changement de mot de passe : tous les anciens Bearer/refresh/cookies sont invalides, seule la nouvelle paire fonctionne.
- Les routes natives ne contournent pas les quotas web existants et n'acceptent pas d'identité étrangère.

### Task 1: Inscription mobile canonique

**Files:** Create app/services/account_lifecycle.py, tests/test_mob03_account_api.py ; modify app/routers/auth_routes.py, app/routers/mobile_api.py, app/main.py, openspec/specs/mobile/feature-migration-map/inventory.yaml.
**Interfaces:** register_account(db, *, username, password, password_confirm, email) -> User ; AccountRejected(code, message). La route POST /api/mobile/v1/auth/register renvoie 201, paire Bearer + user, sans cookie web. Collision nom/email : 409 ; saisie invalide : 400 avec code et message canonique. Quota register partagé avec /register.

- [x] Step 1: écrire les tests de création, normalisation, refus, rejeu, isolation cookie, concurrence et quota partagé.
- [x] Step 2: exécuter check_scope puis les tests ; attendu : rouge sur route absente, pas une erreur d'environnement.
- [x] Step 3: extraire le service canonique et raccorder les deux routes sans changement de politique ; classer la route.
- [x] Step 4: vérifier tests nouveaux + web auth/password policy + d9 + rate limit + inventaire ; attendu : exit 0.
- [ ] Step 5: consigner RED/GREEN puis commit scopé avec trailer demandé, sous le GO BUILD du 5 novembre.

### Task 2: Changement de mot de passe mobile et révocation

**Files:** modify service account_lifecycle.py, auth_routes.py, mobile_api.py, main.py, test_mob03_account_api.py, inventory.yaml.
**Interfaces:** change_password(db, user, *, current_password, new_password, new_password_confirm) -> None, sans commit ; POST /api/mobile/v1/auth/password : ApiUser, validations canoniques, époque de session incrémentée et nouvelle paire pour l'appelant dans la même transaction. Les anciens credentials de tous les appareils et cookies deviennent invalides. Quota login partagé pour borner la vérification du secret actuel.

- [x] Step 1: écrire les tests de concurrence de changement (un seul succès, autre 409 credentials_changed), changement nominal, révocation multi-appareil/cookie, refus/absence de mutation, borne UTF-8, cookie seul et identité forgée.
- [x] Step 2: lancer les tests ; attendu : rouge sur route absente.
- [x] Step 3: mutualiser le changement web et exposer le JSON en préservant les réponses web ; classer la route.
- [x] Step 4: exécuter le broad sweep auth/sécurité/mobile, Ruff budget, spec protocol et OpenSpec strict selon check_scope ; attendu : exit 0.
- [ ] Step 5: rapport exact, revue indépendante, commit et PR draft du change existant ; ne pas fusionner un MOB-03 incomplet ni prétendre les gates UI/appareils acquises.

## Delivery checkpoint

Les deux sous-ensembles de code et leurs vérifications/revue sont réalisés localement. Les étapes de commit/push/PR restent non cochées : contrôle automatique exigeant un GO explicite. Aucun change complet ni gate UI/appareil déclaré terminé.
