# Design — CI-01

## Context

Base examinée : `fcfbcd7`. `clients/mobile/package.json` expose `test: jest` et `typecheck: tsc --noEmit`.
La CI possède trois shards Python, un agrégateur QA, lint, attestation, Sonar et un job Playwright mobile.
Ce dernier installe le lock et exporte les fixtures ; il ne lance ni Jest ni le typecheck explicite.
Voir `proposal.md` pour le besoin.

## Goals / Non-Goals

**Goals:** erreurs Jest/TypeScript visibles et bloquantes dans la CI pour le même arbre que les autres jobs.
**Non-Goals:** aucune preuve appareil iOS/Android, aucune modification d'écran ou comparaison de baseline supplémentaire.

## Decisions

- **Un job dédié**, indépendant des shards Python : nom `mobile checks (Jest + TypeScript)`, Ubuntu, timeout
  15 minutes, permissions `contents: read`, `working-directory: clients/mobile` pour les étapes `run`.
  Alternative écartée : greffer Jest dans le conteneur visuel, ce qui mélange les diagnostics et les durées.
- **Node 22** via setup-node, cache npm keyé sur `clients/mobile/package-lock.json`. Installer avec
  `npm ci --no-audit --no-fund` ; ne pas résoudre à nouveau ni modifier le lock. Conserver les conventions
  d'actions du dépôt et vérifier la version de setup-node avant implémentation.
- **Commandes exactes** : `npm test -- --ci --runInBand`, puis `npm run typecheck`. Pas de watch, de
  `--passWithNoTests`, de `continue-on-error` ni de sortie masquée par un pipe.
  Le step typecheck peut utiliser `if: ${{ !cancelled() && steps.install.outcome == 'success' }}` avec une étape
  d'installation `id: install` : une erreur Jest ne masque pas le diagnostic TypeScript ; le job reste rouge.
- **Même périmètre de déclenchement** que la CI existante : aucun filtre limitant aux fichiers mobiles. Une
  évolution serveur peut affecter le client ; le code des tests mobiles doit être exécuté sur toute PR.
- **Gardes proportionnées** : étendre le patron des tests de workflow existants pour vérifier commandes,
  installation verrouillée et absence de tolérance d'erreur. Pas de test miroir exhaustif du YAML.
- **Branche protégée** : après un premier run réel, relever le nom du check et soumettre son ajout aux checks
  requis. Ne pas modifier les paramètres du dépôt automatiquement.

## Risks / Trade-offs

- [Tests verts localement mais dépendances incompatibles sur Linux] → installation CI depuis le lock et vrai run PR.
- [Mémoire] → Jest `--runInBand`, job isolé ; sweep Python local via wrapper borné seulement.
- [Échec préexistant] → le rapport doit distinguer base, modification CI et éventuel défaut hors périmètre.
- [Faux vert du pipeline] → mutations séparées d'une assertion Jest et d'un type ; elles doivent faire échouer
  les commandes et le job réels. Ne pas livrer les mutations ; relever leurs runs avant restauration.
- [Branches d'essai non couvertes par le trigger push] → faire ces preuves sur la PR de la tranche, puis
  restaurer les fichiers temporaires et exiger un dernier run vert sur le HEAD à livrer.

## Migration Plan

Après revue opérateur : implémenter le job et sa garde ciblée, exécuter `check_scope` (`ci_infra` attendu), ruff/
budget/protocole, tests ciblés et full sweep borné, puis CI GitHub avec les preuves négatives et positives.
Un changement de pipeline ne sera jamais déclaré livré sur la seule preuve locale.
Rollback : retirer le nouveau job et sa garde dans une livraison revue, sans réduire les gates antérieures.
