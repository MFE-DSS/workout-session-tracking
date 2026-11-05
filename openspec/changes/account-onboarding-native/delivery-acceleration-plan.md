# MOB-03 DELIVERY ACCELERATION Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans ; exécution inline, une revue indépendante finale.

**Goal:** Réaliser le service de demandes isolé et le premier usage honnête dans #353.
**Architecture:** Table SQLAlchemy Core sur le même moteur, metadata dédiée non importée au démarrage, sans migration/route/worker. Service policy-gated, autorité vérificatrice absente par défaut. Contrôleur natif autour des SDK canoniques ; snapshot/start adapters absents par défaut. Une page après composition acceptée, pixels avant commit UI.
**Tech Stack:** SQLAlchemy/Python, Expo/TypeScript/Jest existants ; aucun package nouveau.
**Spec:** delivery-acceleration.md, validé par l'opérateur : « Valider le service isolé proposé », « Valider ce croquis ciblé ».

## Global Constraints

Pas de purge/révocation irréversible/migration appliquée/route/production policy. Pas de nouveau READY ni de donnée scientifique construite localement. Entrée et préférences acceptées conservées. Une PR353, pas de merge tant que COMPLETE bloqué ; split analysé mais non effectué sans arbitrage. Pas de déploiement.

## Review Focus

1. Clés concurrentes et connexions distinctes ne créent pas deux demandes actives.
2. Relecture d'identité/époque/hash et changement de compte bloquent toute mutation/status privé tardif.
3. Capacité de statut ne donne aucun autre accès ; secret absent de DB/receipts, expiration/rotation effectives.
4. Confirmation impossible sans preuve serveur liée à demande/propriétaire/politique et protections réelles.
5. Snapshot absent ou périmé ne devient pas première recommandation ; sortie vers MISSION distincte d'un READY scientifique.

## Task 1 — service durable isolé

Files: app/services/account_deletion_requests.py, tests/test_account_deletion_requests.py.
Interfaces: DeletionRequestService(policy registry absent par défaut), request/read/issue_status_capability/read_status_capability/reject/confirm ; table de workflow non importée par app/models/__init__, initialize explicite sur fixture uniquement.
- [x] RED vrais fichiers SQLite, réauth/stale epoch, politique absente sans écriture, clés idempotentes/concurrentes, restart et rollback/réponse perdue, preuve incomplète, capacité expiration/rotation/mauvais propriétaire.
- [x] Implémenter requêtes transactionnelles CAS sans purge ni incrément d'époque, puis tests ciblés et broad account/auth/poids. Expected: PASS.
- [x] Consigner état NOT_SERVED, nouvelle table proposée séparée du graphe23 métier, politique requise avant toute utilisation, aucune migration implicite.

## Task 2 — parcours natif

Files: clients/mobile/src/api/firstUse.ts/.test.ts, ui/account/FirstUseScreen.tsx, ConnectedApp.tsx et tests consommateurs.
Interfaces: FirstUseController(auth,preferences,firstPlan,snapshot=null), load/state/subscribe/invalidate. Snapshot canonique obligatoire avant FirstPlanClient.load ; états chargement/missing/consent/no_producer/unknown/unavailable/usable. Usable exige port de démarrage admis ; aucun contrat d'exécution inventé.
- [x] RED vrais AuthSession/transport, absent producer, déclarations optionnelles, consentement pertinent, A/B et réponses tardives, versions/empreinte via SDK ; implémenter et GREEN.
- [x] Reproduire uniquement le croquis accepté, brancher après résultat compte créé, préserver coque/retour/préférences ; tests montage/navigation. Expected: PASS.
- [x] Produire rendu comparatif avec références compte et états, revue pixels avant commit UI. Pas de nouvelle baseline auto-validée.

## Task 3 — livraison

Files: docs/MOB03_DELIVERY_ACCELERATION_RECEIPT.md, docs/MOB03_RELEASE_RUNBOOK.md ; proposal/tasks/spec delta explicite.
- [x] Matrice compatibilité, recettes appareil identifiées comme plan, rollback sans reset journal ni rollback DB destructif ; analyse split traçable sans second change/PR.
- [ ] check_scope puis targeted+broad, Jest/TS, Ruff/budget/Bandit/spec/OpenSpec ; pas de full sweep local sans tier l'exigeant.
- [ ] Revue fraîche delta complet, une passe Important/Critical RED→GREEN ; publier mêmePR et vérifier CI finale/Sonar. Aucun merge si gate COMPLETE reste ouverte.
