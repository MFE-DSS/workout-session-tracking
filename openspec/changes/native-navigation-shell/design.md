# Design — native-navigation-shell (ADR de navigation)

## Context

Motivation : `proposal.md`. Exigences : `specs/mobile/navigation-shell/spec.md`.

**Observé (canonique `baaaf21`)** :
- `index.ts` choisit la racine : galeries de design (`EXPO_PUBLIC_GALLERY`), fixture du contrat visuel (`contract`), labo hors ligne, ou `ConnectedApp` si `EXPO_PUBLIC_API_URL` est défini. La gate visuelle exporte l'app web avec `EXPO_PUBLIC_GALLERY=contract`.
- `ConnectedApp.tsx` (≈ 750 lignes) porte l'auth, la synchro, le journal, la séance et l'aiguillage `BOOT | LOGIN | APP` → reprise / exécution / bilan / MISSION / attente. Retour Android : `backAction` (PLAT-01).
- Aucune bibliothèque de navigation installée. Le SDK 58 épingle `expo-router ~58.0.25` et `react-native-screens ~4.30.0` (`bundledNativeModules.json`).
- `expo-router@58.0.25` exporte `./native-tabs` (stable ; `./unstable-native-tabs` subsiste) et `ExpoRoot` (montage comme composant). Icônes d'onglet : image (`src`), SF Symbol, xcasset, drawable, Material.
- Inventaire MOB-00 : 17 fonctions `REWRITE_NATIVE` réparties sur Mission, Compte, Profil, Progrès, Récupération, Programmes, Référence.

## Goals / Non-Goals

**Goals :** une coque durable, native sur les deux plateformes, qui n'oblige aucune réécriture des écrans verrouillés et laisse intactes les entrées de design et la gate visuelle.
**Non-Goals :** remplir les espaces ; liens profonds publics ; coque web.

## Decisions

### ADR-1 — Expo Router + NativeTabs (recommandé)

| Option | Pour | Contre |
|---|---|---|
| A — garder l'aiguillage fait main + une barre dessinée | zéro dépendance | chaque espace ajoute des états à un fichier déjà à 750 lignes ; pas de pile par espace ; retour Android à recoder partout |
| **B — Expo Router + NativeTabs** | barre **système** iOS / Android (conventions natives, accessibilité, verre liquide iOS 26) ; pile par onglet ; retour Android natif ; routes par fichier ; SDK-aligné | dépendances natives (nouveau build) ; barre stylable en partie seulement |
| C — React Navigation directe (onglets JS) | contrôle visuel total | barre non native ; plus de code de câblage ; ce que Expo Router apporte, sans ses conventions |

**Choix proposé : B.** L'opérateur l'a déjà cité comme favori ; l'app vise iOS et Android, et la barre native est la convention attendue sur les deux.

### ADR-2 — Monter le routeur SOUS l'entrée actuelle

`ConnectedApp` reste la racine connectée et monte `<ExpoRoot context={require.context('./src/routes')} />` pour la coque. *Alternative écartée :* `"main": "expo-router/entry"` — supprimerait la sélection des galeries, du labo et de la fixture du contrat, donc la gate visuelle. Répertoire des routes : `src/routes` (pas `app/`, qui désigne le serveur dans ce dépôt).

### ADR-3 — La séance est une pile plein écran, pas un onglet

L'exécution (et sa reprise) est poussée au-dessus des onglets ; elle garde `ExecutionScreen` / `ResumeScreen` / `CompleteScreen` tels quels. L'état de séance (journal, outbox, synchro) sort de `ConnectedApp` dans un fournisseur unique, lu par la coque et par la pile de séance — un seul propriétaire, pas deux copies.

### ADR-4 — Décisions pures testées

`initialSpace(session, auth)` (reprise > connexion > premier espace) et `backInShell(space, depth)` en fonctions pures (jest), comme `backAction`.

## Risks / Trade-offs

- [`require.context` et Metro] → vérifier dans une pointe (spike) avant d'écrire la coque ; repli : déclarer les routes à la main avec `createNativeTabsProps`.
- [La barre système ne porte pas toute la DA AUREN] → décision D2 de l'opérateur, rendu réel sur iOS et Android avant commit.
- [Régression de séance en déplaçant l'état hors de `ConnectedApp`] → tests jest existants de la synchro / du journal + passe émulateur et iPhone du parcours PLAT-01.
- [Nouveau build natif] → EAS (Android) et build iOS de développement ; versionCode incrémenté.

## Migration Plan

1. Spike `require.context` + `ExpoRoot` sur une branche jetable. 2. Décisions D1/D2. 3. Coque + pile de séance. 4. Revue visuelle de la barre. 5. Passe émulateur + iPhone. 6. PR.

## Décisions de l'opérateur (2026-10-31)

- **D1 — onglets : AUJOURD'HUI · PROGRAMMES · PROGRÈS · PROFIL.** AUJOURD'HUI porte la MISSION ; la séance est un
  parcours plein écran, pas un onglet ; PROGRAMMES regroupe modèles, programmes personnels, plan et équipement ; le
  social (squads, classement, profils publics), que l'opérateur fait migrer (MOB-00), vit sous PROFIL.
- **D2 — barre système, icônes AUREN.** NativeTabs teintée aux couleurs AUREN, icônes dessinées dans la DA (images),
  rendu iOS et Android montré avant commit.

## Résultats de la pointe (2026-10-31, worktree jetable `spike/mob-01-router`, jamais poussé)

- **Export web : ✅** — `index.ts` reste l'entrée ; `ExpoRoot` + `require.context('../routes')` se résolvent (983 modules,
  feuille `native-tabs` incluse). Les galeries et la gate visuelle gardent leur chemin.
- **Build Android natif (EAS `c0d0332c`) : ✅** — NativeTabs compile et s'affiche en barre Material 3 du système ;
  changer d'onglet fonctionne.
- **⚠ Sans icônes, la barre Android est inutilisable** : avec 4 onglets, Material n'affiche le libellé que de l'onglet
  sélectionné, et l'indicateur reste figé sur le premier emplacement quand aucun onglet n'a d'icône. → les icônes
  AUREN (D2) sont **obligatoires**, et `labelVisibilityMode="labeled"` sur Android.
- **Dépendances** : `expo-router` 58.0.29 exige `expo-constants` ≥ 58.0.14 (le projet épingle 58.0.13) → montée
  mineure ; le plugin `expo-router` (avec `root: ./src/routes`) se déclare dans `app.json` (la config dynamique
  `app.config.js` ne peut pas être écrite par `expo install`).
- **Reste à vérifier** : build iOS (barre système iOS) — au moment de la passe iPhone de la tranche.

## Mise en œuvre (2026-11-03)

- **Écart assumé à l'ADR-3 (propriétaire unique, pas de déplacement).** L'état de séance reste dans `ConnectedApp`, qui
  le **fournit** à la coque par `ShellProvider` (`src/shell/ShellContext.tsx`) au lieu d'être déplacé dans un nouveau
  fichier. L'exigence de l'ADR — un seul propriétaire, pas deux copies — est tenue ; déplacer ~500 lignes de synchro,
  journal et outbox n'apportait rien à cette tranche et faisait courir le risque de régression que l'ADR redoutait.
- **La coque n'existe qu'hors séance.** `ConnectedApp` monte `ExpoRoot` (routes `src/routes`) seulement quand ni une
  série, ni un repos, ni le bilan, ni une reprise serveur n'est à l'écran : la séance reste un parcours plein écran
  au-dessus des onglets, et la fin de séance ramène à AUJOURD'HUI (la coque est remontée sur le premier espace).
- **Retour Android dans la coque** : un `BackHandler` du layout applique `backInShell` (fonction pure testée) plutôt
  que le comportement par défaut de la barre ; pendant une séance, `backAction` (PLAT-01) reste seul en jeu.
- **Espaces non migrés** : `PendingSpace` réutilise `QuietScreen` (sur-titre rendu paramétrable, valeur par défaut
  inchangée) ; au plus une action, la page web existante (`/library`, `/progress`, `/profile`, inventaire MOB-00).
- **Icônes** : noms neutres (`assets/tabs/{today,programs,progress,profile}_{default,selected}.png`) — la décision
  d'icônes de l'opérateur (D3 rejetée, D4 en revue) ne change que des fichiers.
- **Dépendance figée** : `expo-symbols` tire `expo-font@58.0.11`, dont le binaire iOS référence un symbole absent de
  `expo-modules-core@58.0.24` (crash dyld au lancement, mesuré 5 fois sur simulateur) → `expo-font` épinglé `58.0.9`.

## Open Questions

- Libellés exacts des onglets (casse, accents dans la barre système) — sans effet sur la structure.
- **Contradiction de la spec, mesurée le 2026-11-03 — TRANCHÉE.** « La séance au-dessus des onglets » exigeait que
  *mettre en pause* ramène à la coque ; « Priorité de la reprise » exige qu'une séance ouverte passe avant tout
  espace. Une séance en pause EST ouverte : l'app (comportement PLAT-01, inchangé) affiche la reprise en plein écran.
  Amendement proposé à l'opérateur sur la planche §5.1 — « terminer ou abandonner ramène à la coque ; mettre en pause
  montre la reprise » — accepté le 2026-11-03 (« oui go pour la coque ») ; spec amendée en conséquence (scénarios
  « Abandon » et « Pause » ajoutés).
