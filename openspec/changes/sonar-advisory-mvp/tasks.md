# Tasks

## 1. Inspection et décision

- [x] 1.1 Relever contrats, workflow, protection/rulesets et HEAD #347 ; consigner les réponses et la décision opérateur du 2026-11-03 dans le rapport.
- [x] 1.2 Préparer proposal/design et documenter les choix imposés : Sonar consultatif, contrôles conservés, scan inchangé, aucune revendication d’audit sécurité exhaustif.

## 2. Diff de gouvernance proposé

- [x] 2.1 Aligner CLAUDE §4, protocole, contexte OpenSpec et policy temporaire ; vérifier le diff ciblé et l’absence de changement produit/workflow/baseline.
- [x] 2.2 Préparer la protection avant/après et les instructions/payload ; relire les noms/app_id via API, préserver tous les autres checks, ne pas revendiquer d’application non vérifiée.
- [x] 2.3 Consigner l’incident 60bea5d, le statut Sonar réel et les triggers de réévaluation dans le rapport et le registre ; aucune issue requalifiée automatiquement.

## 3. Validation et livraison

- [x] 3.1 Exécuter `python scripts/check_scope.py` puis son minimum, dont protocole documentaire et OpenSpec strict ; revue indépendante de la proposition complète (ISOLATED ; 139 tests, budget 264/548, OpenSpec 5/5 ; constat P2 documentaire corrigé).
- [ ] 3.2 Soumettre le diff par PR propre à GOV-SONAR-01 ; relever son HEAD/CI et le GO MERGE distinct avant intégration.
- [ ] 3.3 Relever la fin du sweep complet CI-01 sur son HEAD et sa base effectifs après intégration GOV, les checks PR et les steps sécurité ; le sweep 5d675b6/base 60bea5d ne vaut preuve finale que si cette base reste effective, sinon le conserver comme historique et revalider selon scope. Rapporter les blockers sans substituer les sweeps précédents.

## Workflow follow-up

- Après GO MERGE GOV-SONAR-01, intégration vérifiée et application autorisée de la protection : reprendre #347 sous son GO acquis, vérifier la canonique puis closeout/archives et rebase MOB-02.
- Aucun GO BUILD MOB-02 implicite. Archiver GOV-SONAR-01 après satisfaction de ses tâches et de sa livraison.
