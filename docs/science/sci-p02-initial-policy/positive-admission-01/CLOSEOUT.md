# SCI — closeout du contrat premier plan v2

**Contrat isolé fusionné ; admission positive et runtime toujours ouverts.** État de publication au commit de ce reçu ; le reçu vivant de la PR de closeout conserve le suivi final après exécution, sans boucle de commits. Le GO couvre le contrat isolé, pas l'admission positive ni le runtime. Le compte rendu autonome est AGENT_HANDOFF.md ; ce reçu lui ajoute les preuves de publication.

## Périmètre réellement livré
Requête/résultat v2 et profil à cinq faits, deux empreintes distinctes, prescriptions observées/bootstrap et quinze zones qualitatives, durée complète toujours exigée par READY. Validation d'échange avec bundle historique piné et registre réellement vide ; neuf exemples négatifs non servis, cinq exports reproductibles et manifestes. V1, FirstPlanClient, outils historiques, app/mobile, API/UI, registres et activation inchangés.

## Vérifications locales
Tier ISOLATED confirmé sur l'ensemble du diff de branche, 428 tests dans 13 modules dont 80 nouveaux ; deux avertissements de dépendances. Ruff neuf, budget 264 ≤ 548, Bandit ciblé, Gitleaks, protocole et OpenSpec strict 10/10 passants. Aucun full sweep local. Schémas et exemples vérifiés par les modèles/échange et reproduction des octets, sans nouveau validateur JSON Schema indépendant.

Revues fraîches code et SCI distinctes. Deux Important code corrigés dans une seule passe avec cinq régressions : acceptation historique réimportée et blockers d'informations corporelles inventés. Suite dédiée 80/80 puis broad 428/428. Aucun Critical ni mineur relevé par ces revues ; pas d'audit global, de preuve biologique ou de durée réelle certifiée. Les décisions d'exécution et limites de revue sont exhaustives dans AGENT_HANDOFF §10.

## Publication vérifiée et suivi de clôture
PR #371, HEAD 3fc9a23f3d2b69b2e443a26a0a74196e995658e0, base 2cddf5d. CI finale [42378325542](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/42378325542) completed/success, neuf jobs : 7660 backend passants, trois ignorés ; 54 suites/676 tests mobiles et TypeScript, QA/lint/sécurité/visuel passants. Ancien run 42377954457 du HEAD5cae3ce annulé comme obsolète après corrections ; pas une preuve du HEAD final. Annulation normale insuffisante, force-cancel ciblé sur ce seul ancien run ; aucun arrêt du run final.

Merge **114312e8a18b347d6b862a70c081413a1bf611e7**, méthode merge avec garde du HEAD, base2cddf5d relue, zéro thread/revue bloquants. État GitHub UNSTABLE dû uniquement à Sonar consultatif. CI canonique **42379843461 en cours lors de la préparation** : aucun succès anticipé. SonarPR : ERROR/Major,11S5778 de structure de tests, zéro bug/vulnérabilité/hotspot, appcoverage93,8%, new_coverage absent de l’API PR. Aucun seuil/état d’issue changé ; GOV-SONAR-01 conservé. Sonar canonique sera relevé sur sa révision exacte dans le reçu vivant. GO permanent seulement après tous les contrôles obligatoires du HEAD final, base relue et absence de revue bloquante, commit de merge avec garde de SHA, sans bypass.

## Clôture et critères positifs
Archiver seulement la livraison du contrat sous l'autorisation de build borné. Les cases SCI-POS01–07 restent ouvertes dans leur proposition réservée et le parent scientifique ; le choix et la représentation v2 ne sont pas admission C5 du bundle. NOT_ADMITTED / NOT_SERVED / READY_NOT_PRODUCED reste l'état réel. C3 et C6 demandent leurs décisions/protocole/preuves ; binding/producteur/READY puis snapshot/handoff PLAN non réalisés. DATA et RELEASE restent ouverts, aucune distribution/recette physique/déploiement déduit.

La présente maintenance ne modifie que documents/spec/archive, avec critères positifs laissés ouverts. Elle est préparée en draft pendant la CI canonique du code pour éviter une attente séquentielle inutile ; son merge reste bloqué jusqu’au succès de cette CI et de ses propres contrôles applicables. La PR de closeout et sa CI sont à relever après exécution. Après preuve d'intégration et absence de travail unique : préserver les revues/ledger/RED→GREEN hors worktree, conserver les préparations ARCH et QA, nettoyer seulement les éléments de ce scope. Le reçu vivant de PR consignera les derniers SHA/CI/Sonar/cleanup sans boucle de commits de reçus.

Contrôles de cette maintenance : check_scope DOCS et check_spec_protocol passants ; OpenSpec strict10/10, liens locaux vérifiés. Aucun nouveau sweep produit local. Le contenu OpenSpec est hors docs/** : la CI de cette PR reste applicable, sans skip manuel ni réglage du pipeline.
