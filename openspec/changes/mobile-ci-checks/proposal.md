# Proposal — CI-01 / mobile-ci-checks

## Why

Le client mobile possède des tests Jest et une commande `typecheck`, mais la CI actuelle ne les lance pas.
La comparaison de captures Playwright ne garde ni la logique native ni tous les types. L'opérateur place CI-01
entre CODX-00 et MOB-02 pour rendre ces vérifications systématiques avant de durcir la séance.

## What Changes

- Ajouter à `.github/workflows/ci.yml` un job `mobile checks (Jest + TypeScript)` sur chaque PR et push déjà couvert.
- Installer le client depuis `clients/mobile/package-lock.json` avec `npm ci` sous Node 22.
- Exécuter Jest sans watch, en série, puis `npm run typecheck` ; aucun `continue-on-error` pour ces commandes.
- Prouver les deux échecs bloquants et une exécution verte sur une CI GitHub réelle avant merge.

## Capabilities

### New Capabilities

Aucune capacité produit ; `skip_specs: true` pour ce changement d'infrastructure CI.

### Modified Capabilities

Aucune exigence produit ni contrat visuel modifié.

## Non-goals

Pas de code métier, de changement de dépendance mobile, de modification du lock, de baseline, de réduction des
shards backend, de changement de trigger/concurrency, de couverture Sonar mobile ou de déploiement.
Pas d'installation de Spec Kit. Pas de modification automatique des protections GitHub.

## Dependencies

Relecture de cette proposition avant apply (`CLAUDE.md §6`). CODX-00 précède la livraison.
Accès aux runs GitHub pour prouver le pipeline ; tier attendu `ci_infra`, full sweep local borné et CI réelle requis.

## Impact

Workflow existant, garde de workflow ciblée si utile, rapport et registre. Nouveau check GitHub à rendre requis
dans la protection de branche après observation de son nom réel et décision de l'opérateur. Un job rouge dans
le workflow ne suffit pas à prouver qu'un administrateur ne peut pas merger : distinguer les deux garanties.
