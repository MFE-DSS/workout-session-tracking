# Proposal — android-pilot-readiness (PLAT-01)

## Why

Un testeur pilote, hors du réseau de l'opérateur, doit utiliser AUREN sur son propre téléphone Android d'ici quelques jours. Aujourd'hui l'app n'a jamais tourné sur Android (gate N0 « OPEN — NO DEVICE »), aucun build installable à distance n'existe, et le backend de production (`https://spignos.com`, `ff4239d`) ne sert pas encore l'API mobile `/api/mobile/v1` (D9, PR #282, postérieure au dernier déploiement). Sans cette tranche, le pilote ne peut pas commencer ; avec elle, il joue le parcours de séance complet sur les mêmes contrats que l'iPhone, sans attendre la parité fonctionnelle.

## What Changes

- **Backend joignable** : le canonique est déployé sur `spignos.com` par le workflow existant (`deploy-production.yml` : sauvegarde, migration **additive** `device_sessions`, smoke, tag). Le smoke vérifie que `/api/mobile/v1` répond par le 401 JSON de l'app (et non par un `auth_basic` nginx qui bloquerait le jeton `Bearer`). Le compte du testeur est créé par l'inscription web ouverte (`/register`).
- **Distribution interne Android** : un `eas.json` avec un profil `pilot` (APK, distribution interne, `EXPO_PUBLIC_API_URL=https://spignos.com` inscrit au build) et un `android.versionCode` ; build par EAS Build (compte Expo de l'opérateur, keystore géré par EAS) ; lien d'installation envoyé au testeur. **Pas** de build Play Store, pas d'`.aab`.
- **Retour matériel Android** : aujourd'hui, le bouton retour sur un écran principal quitte l'app, y compris en pleine série. Pendant une séance (série ou repos, hors reprise), retour ouvre la feuille « Quitter la séance » existante — le même chemin que ✕. Ailleurs, comportement du système. Les feuilles (`Modal`) gardent leur fermeture par retour.
- **Identité d'appareil** : la session d'appareil n'est plus étiquetée « iPhone AUREN » en dur ; l'étiquette vient de la plateforme et du modèle (`deviceInfo`).
- **Clavier** : la saisie (connexion, saisie numérique d'une valeur) reste visible au-dessus du clavier Android.
- **Passe appareil** : parcours complet joué sur émulateur Android (barre gestuelle et à trois boutons), puis checklist rejouée par le testeur sur son téléphone ; captures des écrans critiques, divergences de plateforme consignées.

## Capabilities

### New Capabilities
- `mobile/android-platform` : comportements propres à Android du client mobile — retour matériel, clavier, identité d'appareil, notification de fin de repos, barres système — et la règle de consignation des divergences iOS / Android.
- `mobile/internal-distribution` : comment un build installable hors Store est produit pour un testeur identifié, contre quel backend, et ce qu'il doit permettre (parcours pilote en 10 étapes).

### Modified Capabilities
- (aucune — aucune spec vivante n'existe encore)

## Non-goals (hors périmètre)

- Aucune nouvelle fonction : ni onboarding, ni inscription dans l'app, ni journal enrichi, ni profil, ni abonnement, ni mannequin.
- Aucune refonte visuelle propre à Android ; aucun écran verrouillé modifié (`EXECUTION-SCREEN-V1`, `MISSION-SCREEN-V1`, `COMPLETE-SCREEN-V1`, `BODYMAP-MIT-BODY-V1`, primitives d'instrument). Tout écart de rendu Android est **mesuré, documenté et montré** à l'opérateur ; aucune baseline n'est modifiée sans son approbation.
- Pas de publication Play Store, pas de `.aab`, pas de mises à jour OTA.
- Pas de navigation nouvelle (MOB-01) ni d'intégration de séance au-delà de l'existant (MOB-02).
- Pas de suppression de compte, d'export RGPD ni de manifeste de confidentialité (requis au Store, pas au pilote — consigné comme risque).

## Dépendances bloquantes

- **Décision opérateur (prise le 2026-10-31)** : déploiement sur `spignos.com`, EAS Build, émulateur puis testeur.
- **Identifiant externe** : compte Expo de l'opérateur (`eas login` fait par lui ; l'agent ne manipule aucun identifiant).
- **Poste** : JDK + Android SDK cmdline-tools + image système pour l'émulateur (installations soumises à confirmation).
- **Production** : vhost `spignos.com` sans `auth_basic` (vérifié par le smoke) ; GO de déploiement.
- **Testeur** : un compte web, et l'installation d'apps de sources inconnues autorisée sur son téléphone.

## Impact

- `clients/mobile` : `eas.json` (neuf), `app.json` (`versionCode`, clavier), `ConnectedApp.tsx` (retour matériel, étiquette d'appareil), une fonction pure de décision du retour (+ test jest), `src/native/deviceInfo.ts`.
- Production : déploiement du canonique (API mobile + table `device_sessions`) ; aucun code serveur modifié par ce change.
- Données : un second utilisateur réel sur la base de production (isolement par `user_id`, testé) ; pas de suppression de compte disponible — à dire au testeur.
- Documentation : rapport de sprint, ligne du registre, divergences de plateforme consignées dans le `design.md`.
