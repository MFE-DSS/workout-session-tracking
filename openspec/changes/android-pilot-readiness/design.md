# Design — android-pilot-readiness

## Context

Motivation : voir `proposal.md` (Why). Exigences : `specs/mobile/android-platform/spec.md` et `specs/mobile/internal-distribution/spec.md`.

**Observé dans le code (canonique `2413178`) :**
- `clients/mobile/index.ts` choisit `ConnectedApp` seulement si `EXPO_PUBLIC_API_URL` est défini au build ; sinon c'est le labo sur fixtures. La valeur est inscrite dans le bundle (pas de réglage à l'exécution).
- `ConnectedApp.tsx` route à la main : `BOOT | LOGIN | APP`, puis dans `APP` selon la phase (`SET`/`REST` → exécution, `paused` → reprise, `COMPLETE` → bilan, sinon MISSION / écrans d'attente). Aucun `BackHandler`. La feuille de sortie est ouverte par `requestExit()` (iOS : `ActionSheetIOS` ; ailleurs : la `Sheet` dessinée).
- Toutes les feuilles sont des `Modal` avec `onRequestClose` : le retour matériel les ferme déjà.
- `auth.login(username, password, 'iPhone AUREN')` (ligne 340) : étiquette codée en dur. `src/native/deviceInfo.ts` expose déjà plateforme et modèle (`expo-device`).
- `app.json` : package `dev.auren.vnext.lab`, adaptive icon, `predictiveBackGestureEnabled: false` (le retour passe donc par `BackHandler`), pas de `versionCode`, pas d'`eas.json`.
- `LoginScreen` et `OnboardingFlow` : `KeyboardAvoidingView` avec `behavior` indéfini hors iOS. Expo 58 impose l'affichage bord à bord sur Android ; dans ce mode, la fenêtre n'est plus redimensionnée par le clavier — le bouton de connexion, posé en bas après un espaceur `flex: 1`, risque d'être recouvert. **À vérifier sur émulateur avant de corriger.**
- `src/native/restNotification.ts` crée un canal Android `rest` (importance HIGH), sans alarme exacte.
- Production : `ff4239d`, sans `/api/mobile/v1` ni `device_sessions` ; déploiement par `deploy-production.yml` (SHA exact, sauvegarde, migrations, smoke, tag).

## Goals / Non-Goals

**Goals :** le plus petit ensemble de changements qui rend le parcours pilote sûr sur Android, sans toucher au rendu verrouillé.

**Non-Goals (niveau design) :** pas de bibliothèque de navigation (MOB-01) ; pas de gestion du geste « retour prédictif » d'Android 14+ (désactivé, reste désactivé) ; pas de mise à jour OTA (`expo-updates`) ; pas de canal de build iOS dans `eas.json`.

## Decisions

1. **EAS Build, profil `pilot` (choix de l'opérateur).** `android.buildType: apk`, `distribution: internal`, `env.EXPO_PUBLIC_API_URL = https://spignos.com`, `developmentClient: false` (build autonome, bundle JS embarqué). *Alternative écartée :* build Gradle local — installation JDK/SDK plus lourde et keystore à garder hors dépôt ; reste possible en repli. Le keystore est géré par EAS ; aucun secret n'entre dans le dépôt. `eas init` inscrit `extra.eas.projectId` (identifiant public, pas un secret).
2. **Décision du retour = fonction pure testée.** `backAction({ screen, inWorkout, paused, sheetOpen })` → `'close-sheet' | 'exit-sheet' | 'system'`, appelée par un seul abonnement `BackHandler` dans `ConnectedApp`. `exit-sheet` réutilise `requestExit()` : aucun nouveau chemin de sortie, aucune nouvelle feuille. *Alternative écartée :* un `BackHandler` par écran — dispersé, et les écrans verrouillés n'ont pas à connaître la plateforme. `close-sheet` reste assuré par `Modal.onRequestClose` ; la fonction le renvoie pour que la règle soit testée en un seul endroit.
3. **Étiquette d'appareil dérivée de `deviceIdentity()`** : `AUREN · <plateforme> · <modèle>` (modèle absent → plateforme seule), limitée à la longueur acceptée par le serveur. Fonction pure testée.
4. **Clavier : corriger seulement ce que l'émulateur montre.** Si le bouton de connexion est recouvert, `behavior` passe à `'padding'` sur Android aussi (ou `'height'` selon la mesure) — un changement de comportement, pas de rendu ; les deux variantes sont mesurées et montrées.
5. **Déploiement avant le build.** Le build vise `https://spignos.com` ; le smoke (`GET /api/mobile/v1/mission` sans jeton → 401 JSON de l'app, pas d'en-tête `WWW-Authenticate: Basic`) précède toute remise au testeur.
6. **Passe appareil en deux temps (choix de l'opérateur).** Émulateur Android sur le Mac (API récente, densité xxhdpi, navigation gestuelle puis à trois boutons, police système agrandie une fois), parcours complet sur le backend de production avec un compte de test ; puis checklist rejouée par le testeur sur son téléphone, captures renvoyées.

**Divergences iOS / Android consignées par ce change :**

| Sujet | iOS | Android | Raison |
|---|---|---|---|
| Sortie de séance | `ActionSheetIOS` natif | `Sheet` dessinée (existant) + retour matériel → même feuille | convention native |
| Retour hors séance | geste de bord du système | retour système (quitte l'app ; état restauré à la relance) | convention native |
| Notification de repos | horaire tenu par le système | sans alarme exacte : retard possible, mesuré (`NOTIF-LATENESS`) | permission d'alarme exacte non demandée |
| Police | `System` (SF) | `sans-serif` / `sans-serif-condensed` (existant) | polices système ; écart de métrique à mesurer sur émulateur |
| Étiquette d'appareil | `AUREN · ios · <modèle>` | `AUREN · android · <modèle>` | identité réelle |

## Risks / Trade-offs

- [Le vhost `spignos.com` porte un `auth_basic`] → le smoke le détecte avant le build ; STOP et rapport (réglage serveur hors dépôt).
- [Migration en production] → additive (`device_sessions`), sauvegarde automatique du workflow ; aucune donnée existante touchée.
- [Polices Android plus larges → débordement d'un écran verrouillé] → mesuré sur émulateur ; écart montré à l'opérateur ; aucune refonte sans revue.
- [Clavier bord à bord] → vérification avant correctif (décision 4).
- [File d'attente EAS gratuite lente] → le build part dès le smoke vert ; repli Gradle local si besoin.
- [Second utilisateur réel sans suppression de compte ni export] → dit au testeur ; requis avant le Store, pas pour le pilote.
- [L'émulateur n'est pas un téléphone] → la checklist du testeur sur son appareil reste la preuve physique ; le rapport sépare MESURÉ (émulateur) et RAPPORTÉ (testeur).

## Migration Plan

1. Merger GOV-01 ; déployer le canonique sur la production (`deploy-production.yml`, SHA exact) ; smoke.
2. Compte du testeur via `/register`.
3. Changements app → PR → CI verte → merge.
4. `eas build -p android --profile pilot` sur le SHA mergé ; passe émulateur ; remise du lien + checklist.

**Retour arrière :** un build interne se désinstalle ; le déploiement se rejoue sur le SHA précédent (`ff4239d`) par le même workflow — la table additive `device_sessions` reste sans effet sur le web.

## Open Questions

- Version d'Android et modèle du téléphone du testeur (pour cibler l'image de l'émulateur au plus près) — sans effet sur les specs ni les tâches.
