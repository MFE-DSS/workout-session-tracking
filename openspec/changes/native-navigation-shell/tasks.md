# Tasks

## 1. Décisions et pointe technique

- [x] 1.1 Obtenir les décisions D1 (onglets) et D2 (apparence de la barre) de l'opérateur ; les consigner dans `design.md`
- [ ] 1.2 Pointe sur une branche jetable : installer `expo-router` 58.0.x et ses pairs, monter `ExpoRoot` avec `require.context('./src/routes')` sous `ConnectedApp` ; vérifier export web, build iOS de développement et build Android EAS ; consigner le résultat (ou basculer sur le repli `createNativeTabsProps`)

## 2. Coque

- [ ] 2.1 Exécuter `python scripts/check_scope.py` dans le worktree et suivre les vérifications locales qu'il exige
- [ ] 2.2 Ajouter les fonctions pures `initialSpace` et `backInShell` avec leurs tests jest (reprise prioritaire, connexion, retour à la racine d'un espace, retour au premier espace)
- [ ] 2.3 Extraire l'état de séance de `ConnectedApp` dans un fournisseur unique ; vérifier que les tests jest de synchro, journal et outbox restent verts
- [ ] 2.4 Monter la coque NativeTabs (espaces de D1) et la pile de séance plein écran ; vérifier sur émulateur : démarrer, séance sans barre, bilan → retour à la MISSION, relance → reprise d'abord
- [ ] 2.5 États des espaces non migrés (au plus une action, aucune donnée fictive) ; rendu exposé à l'opérateur avant commit

## 3. Revue visuelle

- [ ] 3.1 Rendre la barre d'onglets (iOS et Android, clair sur fond AUREN) selon D2, icônes AUREN ; planche avant commit ; ACCEPT de l'opérateur
- [ ] 3.2 Gate du contrat visuel : baselines existantes identiques au pixel ; baseline de la barre ajoutée seulement après approbation

## 4. Passe appareil et livraison

- [ ] 4.1 Passe émulateur Android et iPhone : parcours PLAT-01 complet dans la coque, retour Android (`mobile/android-platform` + `backInShell`)
- [ ] 4.2 Rapport de sprint (ADR retenu, décisions D1/D2, mesures) et ligne du registre ; PR

## Workflow follow-up

- Archiver après merge ; MOB-02 (`session-native-integration`) part de la pile de séance de cette coque.
