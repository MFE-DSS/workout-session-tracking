# Proposal — native-navigation-shell (MOB-01)

## Why

L'app native n'a pas de navigation : `ConnectedApp.tsx` choisit un écran à la main selon l'état de la séance (connexion → MISSION → exécution → bilan). C'était suffisant pour un seul parcours ; ça ne l'est plus pour les 17 fonctions « à réécrire en natif » de l'inventaire MOB-00 (profil, historique, progrès, programmes, équipement, récupération…). Il faut une coque de navigation durable **avant** de migrer ces espaces, sinon chaque écran inventerait sa propre façon d'être atteint. L'opérateur : « Je garde comme hypothèse MISSION · SÉANCE · PROGRÈS · PROFIL, mais je ne la LOCK pas avant le migration audit […] une mini ADR OpenSpec : keep current navigation vs Expo Router + NativeTabs. »

## What Changes

- **ADR de navigation** (`design.md`) : garder l'aiguillage fait main · **Expo Router + NativeTabs** (barre d'onglets système iOS et Android, recommandé) · React Navigation directe. Le choix retenu est soumis à l'opérateur.
- **Une coque à onglets** pour les espaces de premier niveau, montée **sous l'entrée actuelle** (`index.ts` garde ses galeries, le labo et les fixtures du contrat visuel) : `ExpoRoot` monté par l'app connectée.
- **La séance passe au-dessus des onglets** : démarrer ouvre l'exécution en plein écran, sans barre ; la reprise d'une séance ouverte reste prioritaire à l'ouverture de l'app ; les règles de retour Android de PLAT-01 sont conservées.
- **Les espaces sans contenu migré** affichent leur état réel : ce qu'ils contiendront est listé dans l'inventaire, rien n'est inventé (règle « l'absence n'est pas une affordance » : au plus un pas).
- **Aucun écran verrouillé ne change** (`MISSION-SCREEN-V1`, `EXECUTION-SCREEN-V1`, `COMPLETE-SCREEN-V1`) ; la barre d'onglets et ses icônes passent en revue visuelle (§5.1) avant tout commit.

## Décisions demandées à l'opérateur (avant apply) — tranchées le 2026-10-31 : D1 = AUJOURD'HUI · PROGRAMMES · PROGRÈS · PROFIL ; D2 = barre système, icônes AUREN

- **D1 — les onglets.** Hypothèse de l'opérateur : MISSION · SÉANCE · PROGRÈS · PROFIL. Constat : la séance s'ouvre en plein écran depuis MISSION ; hors séance, un onglet SÉANCE n'aurait rien de propre à montrer. **Recommandé : AUJOURD'HUI (la MISSION) · PROGRAMMES · PROGRÈS · PROFIL**, la séance étant un parcours plein écran et non un onglet. Alternative : garder SÉANCE comme bibliothèque de séances (modèles + lanceur).
- **D2 — l'apparence de la barre.** NativeTabs = la barre **du système** (verre liquide iOS, Material 3 Android) : on règle teintes, libellés et icônes, pas la forme. Options : (a) barre système teintée AUREN, icônes AUREN dessinées (images) ; (b) barre système, icônes SF Symbols / Material ; (c) barre entièrement dessinée par AUREN (onglets JS) — contrôle total, conventions natives perdues. **Recommandé : (a)**, rendu montré avant commit.

## Capabilities

### New Capabilities
- `mobile/navigation-shell` : la structure de navigation de l'app — espaces de premier niveau, place de la séance, priorité de la reprise, retour Android, connexion hors coque, états des espaces non migrés.

### Modified Capabilities
- (aucune — `mobile/android-platform` garde ses exigences de retour ; la coque les respecte)

## Non-goals (hors périmètre)

- Aucune fonction migrée dans les espaces : la coque seulement (MOB-02 et suivants les remplissent).
- Aucune modification des écrans verrouillés, du domaine serveur ni de l'API.
- Pas de liens profonds publics, pas de version web de la coque (le web reste le site existant).
- Pas de décision sur le social ni sur les statuts `WEB_ONLY` proposés par MOB-00.

## Dépendances bloquantes

- Décisions D1 et D2 de l'opérateur.
- Ajout de dépendances natives (`expo-router` 58.0.x et ses pairs : `expo-linking`, `expo-symbols`, `react-native-screens` déjà au SDK) → nouveau build EAS / iOS.
- MOB-00 mergé (l'inventaire est la source des espaces).

## Impact

- Client mobile : `package.json` (dépendances), un répertoire de routes, `ConnectedApp.tsx` découpé (l'aiguillage de séance devient la pile plein écran), icônes d'onglets (assets AUREN).
- Visual contract : nouvelle surface « barre d'onglets » → exploration, revue opérateur, baseline.
- Tests : décision de l'onglet de départ et de la priorité de reprise en fonctions pures testées.
