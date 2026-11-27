# Plan exécutable SCI-OPS-QUALIFY-01

## Task 1 — préparer sans opération externe nouvelle
Relire canonique, CLAUDE.md/GOV-MERGE-01, registres et leases SCI03 libérés. Conserver checkout opérateur et worktrees. Produire `git archive` du parent figé, SHA256 et manifeste par fichier. Lire le build REL-03 et le bootstrap ; relever les limites de configuration effectives. Livrable : PACKAGE_PREPARATION.json privé et OPERATIONAL_DELTA.md reviewable. Aucun code produit à écrire.

## Task 2 — après GO opérationnel seulement
Relire protections et espace libre. Déclencher PREPARE_IMAGE exact une fois ; attendre l'approbation humaine effective du run. Acquérir même image et garde, vérifier digest/config/source/dépendances, transférer/load en privé sur la cible existante. Zéro modification des services actifs. Le digest OCI de distribution peut être absent pour Docker save : ne pas l'inventer, enregistrer manifeste/config/archive acquis.

## Task 3 — attester l'image et la chaîne de confiance
Inspecter image/base/OS/arch/Python/SQLite/pip freeze et divergences avec requirements-lock + ajouts Dockerfile. Comparer tous les fichiers embarqués attendus avec le contexte, calculer bundle effectif depuis l'image, inventorier UID/GID/caps/Entrypoint/Cmd, rootfs/montages/parents/ACL/symlinks. Profil root-owned ro, digest attendu de la garde de qualification, pas HTTP. Tenter write/rename/symlink/substitution non privilégiés sur profil et parents, sources et bundle ; tester divergence digest/remplacement contrôlé en clone séparé. Capturer fstat avant/après et refus. Le contrôle ne certifie pas la résistance à root/Docker/hôte, ni une future configuration.

## Task 4 — campagne sur les octets de cette image
Les harnesses SCI03 sont des supports à adapter par paramètres explicitement revus, pas des sources à monter à la place du produit.

| Cas | Répétitions / résultat attendu | Preuve |
|---|---|---|
| Legacy et V3 nominaux | 5 chacun, succès admis sous budgets, digest indépendant | CPU user/system, wall total, RSS/AS, parses et source pins |
| Legacy/V3100 faits | 2 chacun ; succès ou HOLD mesuré, jamais budget augmenté | mêmes métriques, identité/qualification des faits |
| Propriétaires A/B/vide | 2 chacun ; aucun fait étranger, EMPTY distinct de UNKNOWN | requêtes, DTO et réponses privées filtrées |
| Snapshot SQLite avec writer synthétique concurrent | snapshot stable, capture suivante voit la nouvelle version | transactions/intégrité/autorité/révisions |
| Préfixe ancien / catalogue V3 manquant | UNKNOWN/PARTIAL/UNAVAILABLE selon preuve effective | absence de promotion EXACT et absence de fallback courant |
| 500/501 faits et autres dépassements JSON/SQL/VM/sources/sortie | refus conservés, 2 essais chacun | statut/signal, limites réelles, refus même si JSON a été écrit |
| Concurrence HTTP, timeout, kill, pipe trop long | pas de queue supplémentaire ; slot/reap après chaque issue | processes/FD avant-après, code de retour/latence totale |
| GET read-only | empreinte DB inchangée hors writer témoin explicitement séparé | SQL read-only, DML refusé, fichiers avant-après |
| Bootstrap réellement livré | maintenance et lecteur disabled ; env extérieur non transmis | liveness/readiness et appel route réellement observé |

Comparer le profil source/SCI et les résolutions au reçu SCI03, sans prétendre que les témoins historiques sont de nouvelles exécutions. Les sondes de parsing/CPU instrumentées restent distinctes du chemin nominal. Temps de création du sous-processus mesuré dans la latence totale :3s n'est pas une garantie abstraite si la création dépasse le budget.

## Task 5 — qualification, revue et sortie
Émettre cinq verdicts indépendants. Tout résultat d'activation garde NO si lanceur/profil/montage réellement destinés à QA non qualifiés. Préparer SCI-ACTIVATE-01 sans l'appliquer. Revue indépendante de la campagne et de ses écarts avant déclaration QUALIFIED. Si un changement produit devient nécessaire, amendement exact avant apply ; aucune anticipation de son autorisation.

Exécuter `python scripts/check_scope.py` avant contrôles locaux ; préparation docs : protocole documentaire et OpenSpec strict, pas de sweep local ou CI nouvelle prétendue. Pour tout diff de code ultérieurement autorisé, suivre le tier réel, tests ciblés/broad, sécurité, revue et CI du HEAD exact, puis GOV-MERGE-01. Aucun merge d'un checkpoint nommé qualification complète.
