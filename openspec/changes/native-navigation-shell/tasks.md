# Tasks

## 1. Décisions et pointe technique

- [x] 1.1 Obtenir les décisions D1 (onglets) et D2 (apparence de la barre) de l'opérateur ; les consigner dans `design.md`
- [x] 1.2 Pointe sur une branche jetable : installer `expo-router` 58.0.x et ses pairs, monter `ExpoRoot` avec `require.context('./src/routes')` sous `ConnectedApp` ; vérifier export web, build iOS de développement et build Android EAS ; consigner le résultat (ou basculer sur le repli `createNativeTabsProps`)

## 2. Coque

- [x] 2.1 Exécuter `python scripts/check_scope.py` dans le worktree et suivre les vérifications locales qu'il exige
- [x] 2.2 Ajouter les fonctions pures `initialSpace` et `backInShell` avec leurs tests jest (reprise prioritaire, connexion, retour à la racine d'un espace, retour au premier espace)
- [x] 2.3 Fournir l'état de séance de `ConnectedApp` à la coque par un fournisseur unique (écart consigné dans `design.md`) ; tests jest de synchro, journal et outbox verts (32 suites, 422 tests)
- [x] 2.4 Monter la coque NativeTabs (espaces de D1) et la pile de séance plein écran ; vérifié sur émulateur : démarrer, séance sans barre, abandon → retour à la MISSION, relance → reprise d'abord (la fermeture du bilan emprunte le même chemin `closeBilan` → coque ; non jouée, pour ne pas écrire une séance complète en production)
- [x] 2.5 États des espaces non migrés (au plus une action, aucune donnée fictive) ; rendu exposé à l'opérateur avant commit

## 3. Revue visuelle

- [x] 3.1 Rendre la barre d'onglets (iOS et Android, clair sur fond AUREN) selon D2, icônes AUREN ; planche avant commit ; ACCEPT de l'opérateur (D4 jeu A « go », coque « oui go », 2026-11-03)
- [x] 3.2 Gate du contrat visuel : baselines existantes identiques au pixel (77 / 77) ; baseline de la barre : sans objet — la barre est un composant SYSTÈME, que la gate web ne rend pas (sa référence est la planche approuvée)

## 4. Passe appareil et livraison

- [x] 4.1a Passe émulateur Android : parcours PLAT-01 dans la coque, retour Android (`mobile/android-platform` + `backInShell`)
- [ ] 4.1b Passe iPhone connectée — le simulateur iOS s'ouvre sur la connexion mais n'accepte pas de saisie scriptée ; à jouer sur l'iPhone de l'opérateur avant l'archive
- [x] 4.2 Rapport de sprint (ADR retenu, décisions D1/D2, mesures) et ligne du registre ; PR

## Workflow follow-up

- Archiver après merge ; MOB-02 (`session-native-integration`) part de la pile de séance de cette coque.
