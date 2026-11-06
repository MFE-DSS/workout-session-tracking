# SCI-P02-ADMISSION-01 — vérifications et reçu

6 novembre2026. Base e9640da. Ce fichier consigne des résultats exécutés, sans déduire une validation scientifique d'une suite verte.

## Local

- Baseline producteur/contrats :72passants avant modifications.
- TDD :26échecs/1passant observés avant modules/artefacts ;27passants après implémentation ;28après garde supplémentaire de perte d'input et hash historique.
- Broad ciblé scientifique : **422passants,1ignoré**,15modules (admission, producteur, contrats, catalogue génération/rulings/validation/lecture/identité/exposition/any_of, intentions/couverture, weekly planner, épistémique, page science). Deux avertissements de dépendances existants. Aucun full sweep Python local.
- check_scope :ISOLATED ; Ruff nouveaux fichiers passe ; budget264≤548 ; Bandit ciblé passe ; check_spec_protocol passe ; OpenSpec strict8/8.
- CLI admission :audit reproduit ; CLI fixtures :11sorties du producteur1.0.0 reproduites à l'octet, aucune READY. JSON v1 et politique0.1.0 intacts. Le nouveau modèle n'est importé par aucun runtime/ancien producteur.
- Aucun test mobile/appareil ou API annoncé ; aucune nouvelle UI ni baseline modifiée.

## Revue indépendante

Revue code fraîche : **aucun Critical/Important, APPROVED technique** ;28tests admission,29producteur historique et CLI rejoués par le relecteur. Minor différé : un slot/prescription non-Mapping provoque AttributeError au lieu de ValueError ; refus sûr, aucun faux fit. L'entrée actuelle vient des diagnostics typés du producteur.

Revue scientifique distincte : **PARTIALLY_ADMITTED, aucun Critical/Important**. Deux suggestions Minor réalisées : ajout de Hermann2025 (2RIR reste une convention, sans équivalence absolue à l'échec) et des sources régionales Kinoshita2026/2023, références indépendamment vérifiées. D1 admis avec limites ; D2 defaults conservateurs conditionnels ; D3 sélection concrète non admise ; D4 borne arithmétique limitée, jamais fit positif. Aucun code de producteur/diagnostic modifié après la revue technique ; une assertion de test conjointe a ensuite été séparée sans changer ses exigences pour le constat Sonar S9073.

Les13sources de l'audit serveur historique (archétypes, slots, prescription) ont été rehashées :0dérive. Les rapports historiques ne sont pas pris comme autorité sans ce contrôle.

## Publication

Le SHA testé, la PR, les runs et Sonar seront consignés dans le reçu de PR après leur exécution. Rien n'est encore servi. L'intégration de cette tranche ne ferme pas le change scientifique global, PLAN ou MOB03.

Premier HEAD publié5d24c5f : PR360, CI42198896664 completed/success,9jobs ;7359backend/3ignorés,54suites/676mobile+TypeScript. Sonar externe ERROR/Major : un seul constat nouveau S9073 (assertion composite dans le nouveau test),0bug/vulnérabilité/hotspot, couverture app93.8%. Correction minimale : trois assertions séparées, mêmes exigences ;28tests admission repassés. Le verdict de ce HEAD ne vaut pas CI du HEAD corrigé ; reçu final dans la PR après vérification.

## Clôture de la seule opération SCI-P02-ADMISSION-01

- PR[#360](https://github.com/MFE-DSS/workout-session-tracking/pull/360), HEAD testé **9ce991adc82df9ad595412acc7e93d9287cd769e**, merge **d5df6c64701b8f5af70226fcda18c18dcc1082f0** ; méthode merge, garde du SHA, base e9640da. Aucun bypass/force-push ni déploiement.
- [CI PR42201392096](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/42201392096) et [CI canonique42203266919](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/42203266919) : **completed/success,9jobs chacune**. Tous les tests backend/QA, mobile/TypeScript, lint/sécurité et contrat visuel requis réussissent. Le canonique a réellement rejoué les shards ; configuration de réutilisation inchangée.
- Sonar PR : **Quality Gate OK,0nouvelle issue**,0bug/vulnérabilité/hotspot, couverture app93.8%. Le S9073 nouveau du premier HEAD est clos par analyse après séparation des assertions, sans changer un seuil/état d'issue. Les outils de diagnostic sont hors `sonar.sources=app` ; la couverture app ne mesure pas leur couverture.
- Analyse canonique liée au SHA d5df6c6 : **Quality Gate ERROR**, conditions Bugs Blocker, Code smells Critical, Vulnerabilities Minor ; couverture app93.8%, nouvelle94.0%. Les6constats vulnérabilité ouverts consultés sont les imports externes Bandit B110/B112 de juin2026 dans des fichiers app inchangés ; aucun nouveau défaut confirmé par ce diff. Relevé limité, pas audit global. GOV-SONAR-01 consultatif conservé ; réévaluation d'exposition/production reste distincte.
- Revue scientifique et revue code indépendantes sans Critical/Important ; bibliographie complétée avec références vérifiées. Minor technique Mapping différé comme décrit plus haut. Après correction de présentation du test, **100tests producteur/contrat/admission repassent**, budget264≤548/protocole/Gitleaks passants ; aucun changement de producteur après revue.
- Maintenance de clôture : référence Grgic2018/PMID28933024 explicitée (EV-55 déjà utilisé), case de publication de cette opération mise à jour. Aucun paramètre, code, schéma ou verdict scientifique changé. `check_scope` **DOCS**, `check_spec_protocol` passant ; aucun nouveau sweep local.

**PARTIALLY_ADMITTED / NOT_SERVED / READY_NOT_PRODUCED.** Cette clôture concerne le spike, pas la politique complète ni PLAN/MOB03. Le change `science-initial-plan-policy` reste actif, sans archivage. Curation/couverture, préparation/calibration et faisabilité positive puis binding du producteur restent nécessaires ; aucune activation runtime implicite.

Le SHA et la CI de ce commit de maintenance seront portés dans sa PR après exécution. Nettoyage borné aux branches/worktree de cette opération après intégration vérifiée ; les worktrees mobile, science antérieure et preuves QA restent protégés. Aucun fichier de credential QA n'a été lu.
