# MOB03 — closeout du socle, parcours complet toujours ouvert

**Socle accepté et fusionné ; MOB03 complet, release/Store et déploiement non acceptés.** Décision de découpage : [GOV-MOB03-SPLIT-01](strategy/MOB03_DELIVERY_SPLIT_AUTHORIZATION.md), réponse opérateur « Approuver cette scission traçable ». Aucun ancien critère transféré n'est déclaré réussi.

## Livraison vérifiée

- PR [#353](https://github.com/MFE-DSS/workout-session-tracking/pull/353), HEAD **55872ffcebc0ac8626c8b0c63ce582d03095e601**, merge **db37b76be1cb18d18675b47788b8e680a1dff752**, base vérifiée bf847c7. Méthode merge, garde du SHA, aucun bypass/force-push. Connecteur merge en erreur interne sans effet ; état relu ouvert, puis API standard gh, fusion confirmée.
- [CI PR42126920199](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/42126920199) et [CI canonique42129145012](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/42129145012) : **completed/success**, neuf jobs chacune. La CI canonique a réellement rejoué les tests ; attestation WOULD_REUSE en shadow mode, configuration non changée.
- PR : **7 331 tests backend passants, trois ignorés**, **54 suites/676 tests mobiles + TypeScript**, QA/lint/sécurité/contrat visuel réussis. Local final :248backend ciblés/broad,676mobile+TS, Ruff264≤548/Bandit/protocole/OpenSpec7/7. Aucun full sweep local redondant. Revue indépendante : un Important corrigé par deux régressions RED→GREEN, suites applicables repassées.
- UI : entrée/formulaires/préférences préservés ; premier passage compte créé→état honnête→préférences/Aujourd'hui, croquis et pixels acceptés («Valider ce rendu»). Captures/empreintes versionnées, aucune baseline LOCKED modifiée. Tests de vrai consommateur et SQLite fichier ; aucune recette physique/force-kill native déduite.
- Service de demandes durable isolé : politique/verificateur absents, aucun import de démarrage, route/migration appliquée/worker/purge/révocation irréversible. Poids : une seule chronologie, aucune nouvelle écriture/UI corporelle. Science : aucun snapshot/producteur/handoff réel branché, aucun READY synthétique servi.

## Sonar réel, politique conservée

PR : QualityGateERROR/Major, zéro bug/vulnérabilité/hotspot, couverture93.8%, nouvelle95.5%. Huit nouveaux S5778 de structure des tests d'exception sont différés comme dette de qualité ; dix constats antérieurs inchangés. L'ancien défaut de complexité weight_history_page reste clos. Aucun seuil ou état d'issue modifié.

Canonique : check externe failure/QualityGateERROR, conditions Bugs Blocker, Code smells Critical et Vulnerabilities Minor. Les six entrées de type vulnérabilité consultées sont des imports externes Bandit B110/B112 datés de juin2026, dans des fichiers inchangés par #353 ; aucun nouveau défaut de sécurité confirmé déduit de ces libellés. Ce relevé n'est pas un audit global. GOV-SONAR-01 reste consultatif ; contrôles obligatoires réussis, aucun contournement. La réévaluation avant exposition/production reste une gate de la suite, pas un changement de policy dans ce closeout.

## Archive et suites conservées

[Archive du seul socle](../openspec/changes/archive/2026-11-06-account-onboarding-native/proposal.md), [11 tâches CORE](../openspec/changes/archive/2026-11-06-account-onboarding-native/tasks.md), [correspondance de toutes les anciennes tâches](../openspec/changes/archive/2026-11-06-account-onboarding-native/scope-split-traceability.md). OpenSpec a créé les deux specs canoniques mobile/account-lifecycle et mobile/onboarding-profile, portant explicitement la distinction entre socle et parcours complet. La tâche finale de maintenance/archive a été cochée après les opérations, pas comme réussite d'une gate runtime différée.

- [DATA01–07](proposals/account-data-activation.md) ouverts : cinq arbitrages du contrôleur, consentement/acquisitions, migration/routes/exécuteur, suivi après révocation, effacement/restauration réels.
- [PLAN01–07](proposals/blueprint-first-session-runtime.md) ouverts : admission dose/candidats/temps, snapshot/version/fingerprint, vrai READY et handoff à une première séance possédée. Contrats v1 et producteur isolé1.0.0 sont présents ; politique0.1.0-proposed NOT_ADMITTED/NOT_SERVED.
- [RELEASE01–06](proposals/account-native-release-acceptance.md) ouverts : compatibilité effectivement déployée/rollback, GO distinct, comptesA/B et Android/iPhone physiques, force-kill/SQLite/clavier/accessibilité. [Runbook](MOB03_RELEASE_RUNBOOK.md) prêt, aucune recette prétendue faite.

Aucun nouveau change/PR concurrent de fonctionnalité ni GO BUILD de ces suites. Ce closeout est la maintenance du périmètre déjà livré, distincte d'une deuxième PR d'implémentation chevauchante.

## MOB04 préparé après la fusion autorisée

[Proposition MISSION](proposals/mob04-mission.md) et [10fixtures versionnées](fixtures/mob04-mission.preparation.v1.json), **SPEC_FIXTURE_NOT_SERVED**. Sources MISSION/SCI et empreintes vérifiées ; référence READY historique distincte du premier plan scientifique ; cas réellement utilisable bloqué sans payload. MISSION-SCREEN-V1 et ses quatre baselines restent LOCKED. Aucun écran, moteur, dose ou asset nouveau réalisé ; aucun GO BUILD ou déploiement.

## Publication de ce closeout

Ce bundle modifie uniquement documentation/specs/archive et fixtures de préparation. Ses checks, SHA et verdict de publication sont consignés dans sa PR de closeout après exécution, sans anticiper un résultat distant. Les branches/worktrees portant du travail unique et les preuves QA MOB02 restent protégés ; cleanup limité aux éléments de cette livraison après leur intégration vérifiée.
