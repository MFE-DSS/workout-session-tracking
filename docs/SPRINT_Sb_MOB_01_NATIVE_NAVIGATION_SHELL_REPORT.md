# Sb_MOB_01_NATIVE_NAVIGATION_SHELL — la coque native : quatre espaces, la séance au-dessus

**Date :** 2026-11-03
**Branche :** `sb/mob-01-native-navigation-shell` (change OpenSpec `native-navigation-shell`)
**Verdict :** voir la fin du rapport.

## 0. Commande et décisions de l'opérateur

- Roadmap 2026-10-31 : « MOB-01 shell ADR (current navigation vs Expo Router NativeTabs) », après MOB-00.
- **D1** (2026-10-31) : onglets AUJOURD'HUI · PROGRAMMES · PROGRÈS · PROFIL ; la séance est un parcours plein écran ; le
  social vit sous PROFIL. **D2** : barre système, icônes AUREN.
- **Icônes** : D3 « Famille C » (quatre symboles propriétaires) **rejetée** — « trop sémantique, trop logo ». **D4** :
  « un ancrage propriétaire + trois utilitaires simples » ; tableau
  https://claude.ai/artifact/HpJGvBW8azTfpmQgwPNyec ; recommandation jeu A (c1 · p5 · g3 · h3) acceptée : « go ».

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

| Sujet | Options | Choix |
|---|---|---|
| Navigation | aiguillage fait main · **Expo Router + NativeTabs** · React Navigation (onglets JS) | NativeTabs : barre système iOS/Android, pile par onglet ; pointe jetable verte avant d'écrire (ADR-1) |
| Montage du routeur | `expo-router/entry` · **`ExpoRoot` sous l'entrée actuelle** | sous l'entrée : galeries, labo et fixture de la gate gardent leur chemin (ADR-2) |
| État de séance | déplacer ~500 lignes dans un nouveau fournisseur · **`ConnectedApp` reste propriétaire et fournit** | un seul propriétaire, zéro déplacement — le risque de régression que l'ADR-3 redoutait est évité (écart consigné dans `design.md`) |
| Retour Android dans la coque | comportement par défaut de la barre · **`backInShell` pur, branché** | la règle de la spec, testée, et non une convention implicite de NativeTabs |
| Icônes | quatre symboles propriétaires (D3) · **la marque + trois utilitaires (D4)** | D4, géométrie Lucide 1.66.0 (ISC) vendue et normalisée, aucun paquet importé |

**Risques et parades :** `require.context` sous Metro (→ pointe, export web vérifié) ; barre système partiellement stylable
(→ rendu réel iOS et Android avant décision) ; dépendances natives (→ nouveau build, `versionCode` 2) ; `expo-symbols`
tire `expo-font@58.0.11`, crash dyld au lancement iOS (→ `expo-font` épinglé `58.0.9`, mesuré).

## 2. Livré

- **Coque** : `src/routes/_layout.tsx` (NativeTabs, teintes `plate` / `ink3` / `ink` / `line`, libellés toujours
  visibles), `src/routes/{index,programmes,progres,profil}.tsx`.
- **Décisions pures** (`src/native/shellNav.ts` + 7 tests) : `initialSpace` — démarrage / connexion / reprise / premier
  espace, **branchée sur l'aiguillage de `ConnectedApp`** ; `backInShell` — dépiler / premier espace / système, **branchée
  sur un `BackHandler` du layout**.
- **Fournisseur** `src/shell/ShellContext.tsx` : `ConnectedApp` fournit AUJOURD'HUI (la MISSION ou ses états d'attente,
  construits comme avant), le journal et l'adresse du site.
- **Espaces non migrés** (`src/shell/PendingSpace.tsx`) : `QuietScreen` réutilisé ; au plus une action, la page web
  existante (`/library`, `/progress`, `/profile` — inventaire MOB-00).
- **Icônes** : jeu A sous des noms neutres `assets/tabs/{today,programs,progress,profile}_{default,selected}.png`.
- **Dépendances** (épinglées exactes, comme le reste du projet) : `expo-router` 58.0.29, `expo-linking` 58.0.15,
  `expo-symbols` 58.0.4, `react-native-screens` 4.30.1, `expo-constants` 58.0.14, `expo-font` 58.0.9. `app.json` :
  plugin `expo-router` (`root: ./src/routes`), `versionCode` 2.

## Croquis validé

Source : demandes de l'opérateur citées — D1 (2026-10-31) « AUJOURD'HUI · PROGRAMMES · PROGRÈS · PROFIL », la séance
« parcours plein écran, pas un onglet » ; D2 « barre système, icônes AUREN » ; D4 jeu A « go » ; coque « oui go ».

```
┌──────────────────────────────┐   hors séance                 ┌──────────────────────────────┐   en séance
│ AUREN · AUJOURD'HUI      ••• │                               │ ✕   EXERCICE 1 / 7       ••• │
│                              │                               │                              │
│  MISSION (écran verrouillé,  │                               │  EXÉCUTION (écran verrouillé,│
│  inchangé) ou ses états      │                               │  inchangé) — aucune barre    │
│  d'attente                   │                               │                              │
├──────────────────────────────┤                               │                              │
│ [marque] [pile] [tend.] [oct]│  ← barre SYSTÈME (NativeTabs) │                              │
│ Aujourd'hui Programmes …     │                               │                              │
└──────────────────────────────┘                               └──────────────────────────────┘
```

## Inventaire — une information, une seule fois

| Élément | Information | Source (contrat de données) | Doublon ? |
|---|---|---|---|
| Libellé d'onglet | nom de l'espace | statique (D1) | non |
| Sur-titre d'un espace non migré « AUREN · Programmes » | où l'on est | statique | non — le titre ne répète pas le nom de l'espace |
| Titre « Sur le site, pour l'instant » | état de l'espace | statique | non |
| Texte | ce que l'espace contiendra | D1 + inventaire MOB-00 | non |
| « Ouvrir sur le site » | la seule action | `EXPO_PUBLIC_API_URL` + route web | non |

## Comparaison avec la référence validée

| Référence validée | Tranche / date | Ce qui doit survivre | Survit ? |
|---|---|---|---|
| MISSION-SCREEN-V1 | AUREN_VISUAL_CONTRACT, 2026-10-31 | composition, raison mesurée, fenêtres BodyMap, « Démarrer » | oui — gate 77/77 ; dans l'onglet, au-dessus de la barre sans chevauchement (planche) |
| EXECUTION-SCREEN-V1 | AUREN_VISUAL_CONTRACT, 2026-10-31 | plein écran, aucune barre pendant la série | oui — gate 77/77 ; passe émulateur |
| COMPLETE-SCREEN-V1 | AUREN_VISUAL_CONTRACT, 2026-10-31 | plein écran au-dessus des onglets | oui — gate 77/77 ; rendu hors coque |
| AUREN-MARK-V1 | DA-03.2, 2026-10-27 | dessin primaire non redessiné, compact sous 20 px | oui — icône AUJOURD'HUI = dessin primaire mis à l'échelle |

## Changement unique de l'itération

- Demande : « oui go pour la coque continue jusqu'au bout de ton critical path »
- Changement : la barre d'onglets système entoure la MISSION hors séance ; la séance reste plein écran au-dessus.
- Avant : MISSION plein écran sans barre (planche PLAT-01 https://claude.ai/artifact/Mfi2zWvJJWeKDfFfa6V6kr)   ·
  Après : https://claude.ai/artifact/8vJtiTf7jcyBY1ypDT7orT

## 3. Passe appareil — MESURÉ (émulateur Android 16, Pixel 7, 1080×2400, API de production)

| Scénario de la spec | Résultat |
|---|---|
| Connexion hors de la coque | ✅ connexion seule, aucun onglet |
| Priorité de la reprise (séance serveur ouverte à la connexion) | ✅ reprise plein écran, sans barre |
| Séance au-dessus des onglets | ✅ exécution plein écran, aucune barre pendant la série |
| Retour Android en séance | ✅ ouvre « Quitter la séance » (PLAT-01 inchangé) |
| Abandonner → coque | ✅ la coque réapparaît sur AUJOURD'HUI, MISSION intacte |
| Changer d'espace | ✅ PROGRAMMES, PROGRÈS, PROFIL atteints en un geste |
| Retour à la racine de PROFIL | ✅ ramène à AUJOURD'HUI |
| Retour à la racine d'AUJOURD'HUI | ✅ le système reprend la main (lanceur au premier plan) |
| Relance avec une séance ouverte | ✅ reprise d'abord |
| Mettre en pause → coque | ⚠ **contradiction de la spec** : la pause montre la reprise (séance ouverte) — arbitrage demandé, voir `design.md` |

iOS : build simulateur (iPhone 17 Pro, iOS 26.3) lancé et ouvert sur la connexion ; le parcours connecté n'a pas pu
être joué au clavier (le simulateur n'accepte pas de saisie scriptée) → **à rejouer sur l'iPhone de l'opérateur**.

## 4. Divergences iOS / Android consignées

- iOS 26 n'applique pas la teinte au repos (`ink3`) : seule la pastille de verre marque l'onglet actif ;
  `backgroundColor` ignoré (documenté par Expo). Le symbole « sélectionné » (plein / fermé) porte la différence.
- Android : barre Material 3, teintes et indicateur respectés ; la barre système à 3 boutons reste claire (constat
  PLAT-01, hors périmètre).

## 5. Relecture des décisions (`CLAUDE.md §5.2`) — contrat visuel et socle

| Décision | Statut |
|---|---|
| Surfaces LOCKED inchangées (MISSION, EXÉCUTION, BILAN) | respectée — gate 77 / 77 au pixel |
| AUREN-MARK-V1 jamais redessinée, dessin optique selon la taille | respectée — c1 = dessin primaire mis à l'échelle |
| Toute couleur est un token mesuré | respectée — aucune couleur nouvelle (`plate`, `ink`, `ink3`, `line`) |
| Aucun doublon verbal-visuel | respectée — voir l'inventaire |
| Jamais une soustraction seule | non concernée — rien n'est retiré |
| L'absence n'est pas une affordance (au plus une action) | respectée — une seule action par espace non migré |

## 6. Vérifications

- `tsc --noEmit` ✅ · jest **32 suites / 422 tests** ✅ · export web ✅ (993 modules) · gate du contrat visuel
  **77 / 77 identiques** ✅ (aucune baseline réapprouvée) · `check_scope` : ISOLATED, traité comme `shared_code`
  (`ConnectedApp`, `QuietScreen` partagés) → suite mobile complète.

## Verdict

**Coque fonctionnelle sur Android, prête pour la revue de l'opérateur.** Reste avant PR : l'arbitrage de la
contradiction « pause », la passe iPhone, et l'ACCEPT de la barre (tâche 3.1) ; la baseline de la barre n'est ajoutée
qu'après approbation (3.2).

## Annexe post-merge (2026-11-03)

- **Mergée** : PR #343, commit de merge `8a21657`, méthode `--merge --match-head-commit 0ba3a6b`.
- **CI canonique** : run `41643223779` — 8 / 8 jobs verts (lint, attestation, contrat visuel, 3 shards pytest,
  pytest + QA, SonarCloud). **Sonar** (porte de la PR) : OK, 0 constat nouveau.
- **Incident résolu dans le périmètre** : premier run de PR rouge (`41638643728`, shard 2) — ce rapport n'avait pas
  les quatre sections du protocole d'itération UI (`tests/test_ui_iteration_protocol.py`) ; ajoutées (`0ba3a6b`).
- **Décisions de l'opérateur** : coque acceptée et amendement « pause » accepté (« oui go pour la coque »).
- **Reste** : passe iPhone connectée (tâche 4.1b) avant l'archive du change.
