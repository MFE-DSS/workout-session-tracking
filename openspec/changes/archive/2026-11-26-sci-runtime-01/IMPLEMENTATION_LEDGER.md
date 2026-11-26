# SCI-RUNTIME-01 — ledger d'exécution

Parent9ef96e39. GO exact reçu26novembre2026, BUILD_AUTHORIZATION.md.

Préflight : T1 produit CatalogueProjection/document/source_sha256/omitted_paths, T2 lit cette interface sans changer les contrats ; quatre consumers identifiés. Pas de conflit de lease : BUILD-01 clos et sources partagées libérées.

Ruling : exécution inline selon le mandat autonome, plan OpenSpec et ledger du change — pas de micro-GO de tâches — mêmes gates finales.
Ruling : pas de full sweep local shared_code, le verdict check_scope et broad consommateurs font foi ; CI globale exacte obligatoire.

Task 1 : en cours, tests avant produit.

Task 1 : 2 tests RED (capacité absente) puis31 tests catalogue GREEN ; parités réelles Legacy/V2/V3 et bundle complet, port synthétique retiré du test v2.124 tests lecteur/API PASS,3 Linux SKIP surDarwin ; broad186PASS/1skip. Source canonique hash inchangé. Ruff initial introuvable dans l'env QA ; binaire existant de l'env opérateur utilisé sans installation ni mutation de ce checkout.

Task 2 : 2 tests RED (harness absent), puis7PASS/2LinuxSKIP avant ajout du témoin de pipeline réel Linux (3ème skip surMac). Ouvertures ancrées par descripteurs, refus de symlinks/permissions/digest testés ; cinq paramètres HTTP supplémentaires refusés.

Ruling : livrer le correctif admissible avec harness de préqualification et témoins bornés, pas un outil qui autocertifie la campagne complète — Docker daemon inaccessible, mandat §5 autorise la livraison du catalogue avec runtime HOLD — coût : il faudra exécuter et consigner le reste de la campagne sur la cible fidèle avant qualification. Les métriques non exécutées restent NULL.

Ruling : aucune correction du loader produit au titre du diagnostic Sonar — aucun exploit distant démontré, le périmètre autorise les vérifications de confiance dans le harness — coût : les ACL, mounts et répertoires du profil réel restent un verrou d'activation.

Gates locales : scopeSHARED_CODE ; Ruff propre, budget260≤548, Bandit des2nouveaux modules PASS. Revue indépendante du diff entier en cours. Aucun profil opérationnel, activation ou publication.

Final review : revue fraîche sci_runtime_whole_code_review, aucunCritical/Important ;300 cas différentiels +6escapes opaques vérifiés par le reviewer, aucun écart. Il n'a pas réexécuté les campagnes124/186.
Final: minor (deferred): dernier parent contrôlé absent de checked_parent_descriptors, inventaire seulement ; aucun fail-open.
Final: minor (deferred): ancien port semantic_json/commentaire de test projection désormais mort pour le catalogue ; fichier hors liste du présent amendement, aucune lecture masquée.
Final: Ruling: campagne cible exacte hors avis — maintenir runtime et sécurité opérationnelle HOLD — coût : activation impossible avant preuves3.11.14/SQLite/image/ressources/chemins.
Final: Ruling: remédiation loader historique hors avis — pas de patch hors amendement ni dismissalSonar — coût : la confiance locale reste à qualifier.
Final: Ruling: CI/Sonar/closeout encore non examinés — vérifier le futur HEAD réel séparément — coût : aucun merge tant que les gates obligatoires ne sont pas vertes.

Task 1: complete, preuve124PASS/3SKIP dans task-1-tests.log ; source/parité réelle.
Task 2: complete pour livraison partielle admissible, même campagne inclut le harness ; pas de rerun redondant. Host réel darwin/arm64/Python3.11.14/SQLite3.50.4 ; cette valeur n'est pas celle de la cibleLinux. DockerGET/_ping timeout3,001s, aucun daemon modifié. Le harnessCLI termine2/HOLD avec métriques ciblesNULL.

Sécurité : scan optionnel du répertoire entier Gitleaks =1signal dans docs/SONAR_AUDIT_01_REPORT.md:197, fichier inchangé depuiscanonique. Triage du JSON : champ key d'un objet issueSonar (rule/severity/issueStatus/component/line/message/dates), identifiant20caractères, pas un credential. Preuve privée BUILD_GITLEAKS_TRIAGE.json ; aucune valeur sensible affichée, aucune règle/.gitleaksignore modifiée. Le scan du delta et de l'historique pertinent reste requis séparément.
