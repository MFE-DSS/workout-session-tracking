# Tasks

## 1. Backend de production joignable

- [x] 1.1 Après le merge de GOV-01, dispatcher `deploy-production.yml` sur le SHA canonique exact (GO opérateur du 2026-10-31) et vérifier le run vert, la migration `device_sessions` appliquée et le tag `deploy/prod/<date>-<sha>` posé
- [x] 1.2 Smoke : `GET https://spignos.com/api/mobile/v1/mission` sans jeton rend le 401 JSON de l'app et aucun en-tête `WWW-Authenticate: Basic` ; `POST /api/mobile/v1/auth/login` avec de mauvais identifiants rend le refus de l'app — sinon STOP et rapport
- [x] 1.3 Créer un compte de test pour la passe émulateur par `/register` ; vérifier qu'il se connecte au web

## 2. Corrections Android dans le client

- [x] 2.1 Exécuter `python scripts/check_scope.py` dans le worktree et suivre les vérifications locales qu'il exige
- [x] 2.2 Ajouter la fonction pure de décision du retour (`close-sheet` / `exit-sheet` / `system`) et son test jest couvrant série, repos, reprise, feuille ouverte, MISSION, bilan, connexion ; vérifier `npm --prefix clients/mobile test`
- [x] 2.3 Brancher un seul abonnement `BackHandler` dans `ConnectedApp` qui applique cette décision (`exit-sheet` → `requestExit()` existant) ; vérifier sur émulateur : retour en série et au repos ouvre « Quitter la séance », retour sur la feuille la ferme sans commande
- [x] 2.4 Dériver l'étiquette de session d'appareil de `deviceIdentity()` (fonction pure + test jest, longueur bornée) et retirer « iPhone AUREN » ; vérifier côté serveur l'étiquette de la session créée depuis l'émulateur
- [x] 2.5 Mesurer le clavier sur émulateur (connexion, saisie numérique d'une charge) ; si un champ ou son action est recouvert, corriger le comportement d'évitement sur Android, montrer avant / après à l'opérateur, puis vérifier les deux écrans au clavier
- [x] 2.6 `npm --prefix clients/mobile run typecheck` et suite jest verts ; gate du contrat visuel (`clients/mobile/visual-contract/run.sh test`) vert sans aucune baseline modifiée

## 3. Distribution interne

- [x] 3.1 Ajouter `clients/mobile/eas.json` (profil `pilot` : APK, distribution interne, `developmentClient: false`, `EXPO_PUBLIC_API_URL=https://spignos.com`) et `android.versionCode` dans `app.json` ; vérifier `npx expo config --type public` sans erreur
- [x] 3.2 L'opérateur fait `eas login` ; `eas init` lie le projet (`extra.eas.projectId`) ; vérifier `eas project:info`
- [ ] 3.3 Après merge du change, `eas build -p android --profile pilot` sur le SHA mergé ; vérifier un APK téléchargeable et noter sa référence (build id, SHA, versionCode)

## 4. Passe appareil

- [x] 4.1 Installer JDK + Android SDK cmdline-tools + émulateur + image système récente (confirmation opérateur) ; vérifier `adb devices` et un émulateur démarré
- [x] 4.2 Installer l'APK du profil `pilot` sur l'émulateur et jouer le parcours 1 → 10 sur la production avec le compte de test (connexion, MISSION, démarrage, séries, repos, fin, bilan, relance en cours de séance → reprise, série hors ligne puis envoi) ; vérifier la séance côté serveur
- [x] 4.3 Rejouer la checklist d'appareil en navigation gestuelle puis à trois boutons (safe areas, barres système, défilement, cibles, polices, icônes, BodyMap SVG, densité, transitions, erreur / chargement, reprise, relance — aucun écran ne déborde) ; captures des écrans critiques ; tout écart de rendu mesuré et montré à l'opérateur
- [x] 4.4 Rédiger le rapport de sprint (flux supportés, référence APK, appareil / Android testés, captures, bugs connus, bloquants, divergences, checklist réussite / échec) et la checklist du testeur ; ligne du registre mise à jour

## 5. Remise au testeur

- [ ] 5.1 Envoyer à l'opérateur le lien d'installation, les consignes (autoriser l'installation, créer son compte sur `https://spignos.com/register`, pas de suppression de compte disponible) et la checklist ; consigner les retours du testeur (RAPPORTÉ, séparé du MESURÉ)

## Workflow follow-up

- Archiver le change après merge et après les retours du testeur (`openspec archive android-pilot-readiness`), et passer la ligne du registre à MERGÉE.
