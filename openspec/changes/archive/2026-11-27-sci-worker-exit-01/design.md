# Design borné

## Brainstorming / Options / Risques / Choix retenu
1. Teardown Python normal : conserve le défaut mesuré et HOLD.
2. Fin explicite au seul point d’entrée après main et flush : option retenue dans l’amendement accepté ; risque de sauter un nettoyage obligatoire, réfuté par tests de fermeture/erreurs et revue.
3. Hausse CPU, acceptation stdout après SIGXCPU, refonte imports/cache : interdits.

Le main reste callable en tests et conserve ses context managers. L’entrée enfant choisit0 seulement après main réussi et flush réussi ; les erreurs retournent un statut non nul. Les signaux conservent leur autorité. Avant émission : snapshot terminé, DTO strict et empreinte du DTO normalisé contrôlés, encodage borné sans NaN. Aucun catalogue ou donnée réutilisés entre requêtes.

Le superviseur n’est pas modifié : exitcode, limites de sortie, timeout, kill/wait, slot, propriétaire et fenêtre restent ses autorités. La qualification de code monté sur image support historique ne vaut pas requalification d’une image reconstruite.

## Ownership
Lease local : spec/sci-worker-exit-01 ; worker.py et test_worker uniquement. Canonique54f68f65 relu ; aucun change actif repéré revendiquant ces fichiers. Les autres worktrees et leases sont conservés. RTK.md absent aux chemins précédemment vérifiés ; aucune règle supplémentaire inventée.
