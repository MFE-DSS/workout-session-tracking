# SCI-OPS-QUALIFY-01 — livraison du correctif V3

27 novembre 2026. **Code fusionné ; qualification opérationnelle HOLD ; lecteur DISABLED.** La publication du closeout et son nettoyage Git restent à vérifier au présent instant.

## Source et vérifications

- Parent : `1ac401f44b8af9444a8521b30cd47b7201fd1c8e`.
- HEAD final : `35952b2d3bb022bc81df5b7ed9e504e34ddb1cb4`, [PR #454](https://github.com/MFE-DSS/workout-session-tracking/pull/454).
- Merge : `06122323ea9b341f4cb02f3da9a3746f7d33ca83`. Arbres HEAD/merge identiques.
- [CI PR 46034244806](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/46034244806) : 11 jobs completed/success, quatre protégés. 9 047 tests backend PASS / 3 SKIP existants ; 140 suites / 1 610 tests mobiles et TypeScript PASS ; 77 tests visuels PASS. Exécution réelle, sans réutilisation de verdict.
- [CI canonique 46037607200](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/46037607200) : 11 jobs completed/success, quatre contrôles protégés réussis ; job Sonar réussi. Quality Gate Sonar canonique ERROR (consultatif selon GOV-SONAR-01) : couverture nouveau code 92,1 %, duplication 0,0 % ; seuils agrégés bugs/smells/vulnérabilités en défaut sur la période previous_version depuis avril. Aucun finding du lecteur créé le 27 novembre dans les résultats relus. Aucun état d’issue ni seuil modifié.
- Sonar PR : gate OK. Quatre S9073 corrigés par séparation des assertions, sans modification d’issue, de règle ou de seuil. S8707 relu OPEN/MAJOR sur `supervisor.py:58` et conservé séparément.
- Local : 148 PASS / 4 SKIP Linux existants. Les 38 tests de provenance ont été rejoués après clarification des assertions ; expressions et ordre AST conservés. Tier SHARED_CODE, broad ciblé, aucun full sweep local.
- Revue indépendante du diff entier : aucun Critical/Important restant ; correction du mineur documentaire sur les 1 696 fichiers source.

## Résultat et limites

La validation interne V3 conserve son contexte complet. La projection publique émet explicitement les cinq propriétés admises après les contrôles de binding, d’identité et de reçu. Aucun schéma public ou writer n’est modifié.

Les 1 696 fichiers runtime du candidat Linux `26c6356` sont identiques au code livré. Legacy : 5/5 admis ; Legacy 100 faits : 3/3. V3 14 faits et mixte 100 faits : 4/7 admis chacun ; trois SIGXCPU conservés par famille. Les sorties valides d’un enfant terminé anormalement restent refusées. Digests, parité scientifique et frontière V3 PASS ; qualification fiable HOLD. Aucun budget augmenté.

L’image support `sha256:6baa24c49404b2dd8ad74a3d5b4d6f9af3c83c6923a5711a1ae1bf79aebe5e8c` reste inchangée. Le montage du code corrigé est une qualification de candidat contrôlé, pas une nouvelle image opérationnelle. Image reconstruite et futurs chemins QA restent HOLD. Lecteur DISABLED, activation QA NO.

Un témoin diagnostique mixte a atteint atexit à 1,867390 s CPU avant SIGXCPU à 2,010212 s CPU. Ce témoin ne prouve pas la cause de tous les refus. Le correctif de fin de processus proposé dans `RUNTIME_HOLD_NEXT_AMENDMENT.md` reste sans GO et sans code appliqué.

## Conservation et nettoyage

Seize conteneurs et quatre volumes propres au banc ont été retirés normalement après export privé vérifié. Les dix conteneurs préexistants, volumes, services et configurations ont conservé leurs identités. Les exports et preuves sont empreintés ; 52 244 480 octets de doublons distants ont été retirés après vérification des copies locales. Aucun service QA, secret, DNS, daemon ou donnée réelle modifié.

Preuves privées : `/Users/martinfeldmann/auren-review/sci-ops-qualify-01-evidence-20261127/v3-context-amendment-20261127/`. Aucun identifiant privé ni base synthétique n’est publié dans cette PR.

L’archive conserve cet instant et ses HOLD. Son unique suivi publication/CI/cleanup doit être résolu par les reçus vivants finaux, sans réécrire les observations historiques. Aucune activation, image cloud, APK, OTA ou release n’est autorisée par ce closeout.
