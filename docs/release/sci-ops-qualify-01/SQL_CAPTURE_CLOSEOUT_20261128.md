# SCI-SNAPSHOT-READS-01 — reçu final de livraison

28 novembre 2026, Europe/Paris. **Code et archive fusionnés, quatre campagnes CI réussies ; qualification opérationnelle HOLD, lecteur DISABLED.**

## Source et gouvernance

GO opérateur : « ok gO pour le correctif SQL borné ». Parent initial `c8b413efa027467600654a445521ca8e564b4384`. Trois fichiers code/tests autorisés ; seul `sqlite_source.py` change en production. Réutilisation bornée de lectures brutes dans une seule capture SQLite read-only, copies indépendantes, owner/snapshot et comptabilisation physique conservés ; aucun verdict scientifique en cache.

- Code [#459](https://github.com/MFE-DSS/workout-session-tracking/pull/459), HEAD `0e0008cede00c3f369b1c6c827603eb73e972820`, merge `7f05ba1a038d32de0d1568ecb3397e4489ba58da`.
- Archive [#460](https://github.com/MFE-DSS/workout-session-tracking/pull/460), HEAD `cc6f241c3125d3682e044979ad328fe92fa0f460`, merge `0994346e3384ac801615374aacd7630d72670e18`.
- Deux merges avec garde du HEAD, arbres identiques aux HEADs verts, quatre checks requis app15368 et revues sans finding ; aucun bypass. Archive `2026-11-28-sci-snapshot-reads-01`, leases libérés.

## Contrôles effectivement exécutés

| Source | Run | Résultat |
|---|---|---|
| Code PR final | [46129030460](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/46129030460) | success — 11 jobs |
| Code canonique7f05ba1a | [46130918222](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/46130918222) | success — 11 jobs |
| Archive PR | [46131163737](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/46131163737) | success — 11 jobs |
| Archive canonique0994346e | [46132759508](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/46132759508) | success — 11 jobs |

Chacune des trois premières campagnes a réellement exécuté9 074 backend PASS / 3 SKIP existants,140 suites / 1 610 mobiles + TypeScript et 77 visuels, plus QA et sécurité. L’attestation canonique SHADOW n’a pas réutilisé les shards. La quatrième campagne a également exécuté les mêmes 9 074 backend / 3 SKIP, 1 610 mobiles + TypeScript et 77 visuels ; aucun succès n’est emprunté à un ancien run.

Local : 24 tests SQLite, 331 broad / 4 SKIP Linux sur Mac, 14 HTTP ; archive : 61 tests protocole/scope/contrat. Ruff/budget260≤548, Bandit, Gitleaks, protocole et OpenSpec strict. Pas de full sweep local redondant. RED répétés et SQL4096 conservés ; correction du seul harness WAL documentée dans l’archive. Revue indépendante du produit, des tests renforcés et de l’archive : aucun Critical/Important/Minor restant.

## Sonar exact, sans confusion de périodes

Code PR : gate OK, 100 % nouvelle couverture, 92,1 % couverture globale, 0 % nouvelle duplication et zéro nouvelle issue/bug/vulnérabilité ; archive PR : gate OK, zéro nouvelle issue. Première CIcode9b90618 avait trois remarques de tests ; corrigées par assertions plus précises, nouvelle CI0e exécutée intégralement. Aucun état d’issue ou seuil modifié administrativement.

Branche canonique après code : gate ERROR consultatif, période previous_version depuis le 10 avril 2026 ; 9 bugs / 9 vulnérabilités historiques et maintenabilité consignés, couverture92,1%. Les neuf vulnérabilités ouvertes sont antérieures au correctif ; aucune sur sqlite_source.py et aucune introduite par la PRSQL. S8707/supervisor reste OPEN, distinct de ce correctif. Après archive : même gate ERROR consultatif et mêmes réserves, couverture globale 92,1 %. Aucun certificat de sécurité globale ni qualification des futurs cheminsQA.

## Résultat et réserves

Sur les bases synthétiques préservées, sans writer :14V3/SQL282 ;mixte100/SQL557 ;Legacy100/SQL904 ;100V3 structurels/SQL3918 contre refusSQL4096 précédent. Dix digests normalisés et empreintesDB vérifiés ; comptesA/B/vide isolés etUNKNOWN conservés. Python3.14.7/Darwin : **preuve fonctionnelle locale seulement** ; la fixture100V3 ne prétend pas à100STARTs produit autorisés.

Budgets SQL4096,VM2M,CPU2/3s,AS512Mio,wall3s,JSON/sortie intacts. Writers,SCI/P07,DTO,TIME-01,historique,V3 etmobile inchangés.

**Image opérationnelle inchangée/source1f81d5b8 ; runtime exact corrigé HOLD ; lecteur DISABLED / NOT_QUALIFIED pour activation.** Aucun PREPARE_IMAGE,SSH,montage candidat,transfert,actionOVH,activationQA,DATA,APK ouOTA exécuté dans ce scope.

Les actes, preuves, refus et fixtures restent préservés en privé. Ce reçu résout le suivi CI de l’archive ; sa propre publication documentaire et le nettoyage Git borné seront consignés dans le reçu final privé après vérification d’ancestralité. Aucun worktree tiers ni travail unique supprimé.

Prochaine autorisation distincte : un unique paquet image exact reconstruit depuis le canonique final, garde privée/transfert et qualification synthétique isolée sous budgets inchangés. Ne pas réutiliser l’approbation46081408323. Activation et DATA restent ultérieurs.
