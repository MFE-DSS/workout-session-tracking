# SCI-RUNTIME-02 — closeout du correctif, qualification opérationnelle HOLD

26 novembre 2026 — Europe/Paris. **Code livré ; publication de ce closeout, CI finale et cleanup suivis par le reçu vivant final.** Le lecteur reste désactivé et NOT_QUALIFIED. Aucun GO d'activation ou release n'est déduit.

## Livraison vérifiée

Autorisation exacte : « Autoriser ce correctif SCI-RUNTIME-02 », call_12d65838fae34f55aee3aee31ea82f69. Parent c454af863278b0801a568437038eb4efb94db588 ; [PR450](https://github.com/MFE-DSS/workout-session-tracking/pull/450), HEAD0014c2e1bc02cec7e9b744ed20d9b0575b768859, mergefc3d8135ec08f028e32adb76a8a46701bdf53992. Arbres HEAD/merge identiques. Merge commit gardé par expected_head_sha, quatre checks protégés Actions15368 verts, MERGEABLE, aucune revue ni thread bloquant ; aucun bypass, force ou squash.

Seuls worker.py et son test changent côté produit. Limites installées avant imports ; ORM incident fixé à sqlite:///:memory: ; vraie captation serveur séparée, read-only, propriétaire et snapshot conservés. Budgets, SCI, TIME-01, writers, données historiques, VPS, mobile et flags inchangés.

[CI PR45849496665](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/45849496665) et [CI canoncode45852847004](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/45852847004) completed/success,11jobs chacune. Chacune a exécuté9024backend/3ignorés,140suites/1610mobiles+TypeScript et77visuels. Les résultats locaux ne remplacent pas ces campagnes.

## Expériences et limites conservées

[Reçu avant GO](QUALIFICATION_RECEIPT.md) et [résultats après GO](BUILD_RESULTS.md). RED réel avant correctif ; garde de test renforcé après revue et témoin de mutation avec var préexistant. Dernier ciblé+broad357PASS/1skipexistant, sans full sweep local (tierISOLATED), Ruff/budget260≤548, Bandit, OpenSpec33/33, protocole et Gitleaks delta/rangeGit passants. Revue indépendante finale : aucunCritical/Important restant.

Les refus antérieurs ne sont pas effacés. Sur HEAD exact0014c2e, un nouveau nominal a reçu SIGXCPU(-24) à2,2114s monotones/2,0706s CPU enfant, avec wait/reap/slot libéré. Cette cause est prouvée pour **ce run** ; elle n'est pas attribuée rétroactivement aux anciens503/échecs sans retour enfant observé. Aucun plafond augmenté.

Dans cette même campagne HEAD exact : vrai HTTPA200/PARTIAL/reps9, B200/PARTIAL/reps999, propriétaire vide200/EMPTY ;401sansBearer,422injection de configuration ; lectures parallèles200et503rapide compatible avec busy. Base inchangée après GET ; serveur et enfants nettoyés. Captation instrumentée séparée :19statements/11SELECT après setup ; DML refusé. Compte VM exact et temps SQL pur restent non mesurés ; les témoins de plafonds ne les remplacent pas.

## Profil et sécurité

Image historique b8fc63f attestée, source HEAD0014c2e montée readonly ;3346fichiers exactement identiques à Git. Debian13.3, Python3.11.14, SQLite3.46.1, amd64 émulé sur DockerDesktopARM64, UID10001/caps0/no-new-privileges ;1CPU/2Gio/pids128. AS512Mio, CPU2/3s, CORE0 et sortie1Mio conservés. La preuve d'import/nominal n'est ni une image complète reconstruite ni une qualification VPS/amd64 natif.

Profil TEST_FIXTURE_NOT_OPERATIONAL ; digest336c2023d6f8732d7febffc288e2889ee60049bde54a13678b2adc2615351d12. Inventaire final source/bundle/autorité et parents : root-owned, aucun bit022, ACL ni symlink relevé ; montagesro et refus d'écriture effectifs. La préparation antérieure avec modes0664/0775 reste distinguée. Le digest attendu provient de la préparation privée contrôlée, jamais d'une requête HTTP. La confiance des futurs parents/montages/ACL/configurations reste à qualifier ; aucune sécurité globale n'est déclarée.

SonarPR450 : ERRORconsultatif, nouvelle couverture0%, couverture91,8%,0nouveau bug/vulnérabilité/smell/hotspot. Canoncodefc3d813, analysec02dbdcd-71f1-4c18-8c31-52c82c8c6e19 : ERRORconsultatif,9bugs/9vulnérabilités/768smells/0hotspot, couverture91,8%, nouvelle91,75186735180378%. Ces métriques globales ne constituent pas des défauts nouveaux du patch. AlerteGitHub13/S8707 sur supervisor.py relue : APIstateNULL, fixed_at/dismissed_atNULL ; aucune résolution déduite. Aucun état, règle ou seuil édité par l'agent.

## Archive et conservation

Archive OpenSpec par CLI :2026-11-26-sci-runtime-02 ; une exigence canonique ajoutée, aucun retrait/modification de contrat SCI. Cinq fichiers archivés identiques ; tasks actualisé au checkpoint et lien relatif BUILD_AMENDMENT ajusté à sa profondeur d'archive. Le seul suivi publication/CI/cleanup reste historiquement ouvert dans les tâches et sera résolu par les reçus vivants finaux, sans réécriture du checkpoint.

Preuves privées : `/Users/martinfeldmann/auren-review/sci-runtime-02-evidence-20261126`, dont EXACT_HEAD_SOURCE_PROOF.json, EXACT_HEAD_QUALIFICATION.json, DELIVERY_LEDGER.json et logs complets. Bases et Bearer synthétiques hors Git.38conteneurs jetables arrêtés et19volumes propres à nos essais supprimés après conservation ; image historique et preuves gardées, aucun daemon/service personnel ou prune global touché. Nettoyage Git uniquement après propreté, ancestralité et zéro travail unique.

Revue indépendante du présent delta documentaire : aucunCritical/Important ; un lien vers le change actif supprimé a été corrigé. Ciblé+broad documentaire51PASS, OpenSpec32/32strict, protocole/budget et diffcheck passants. Aucune seconde revue indépendante du remplacement de lien n'est revendiquée.

## Verdict et prochaine opération

Catalogue **PASS** ; parités SCI composants **PASS** ; bootstrap EROFS corrigé.
**Runtime opérationnel HOLD / chemins opérationnels HOLD / lecteur NOT_QUALIFIED, disabled.**
Prochaine qualification : image/source/profil de confiance exacts sur Linux amd64 natif, avec mêmes plafonds et mesures manquantes complétées. Aucun VPS, activation, DATA, APK, OTA ou déploiement n'est autorisé par ce closeout.
