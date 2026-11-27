# Proposition distincte — fin bornée du worker après résultat vérifié

27 novembre2026. **PROPOSÉ / GO NON REÇU / aucun code appliqué.**

## Défaut nouveau mesuré
Le contexte public est corrigé. Sur le code26c6356, les campagnes natives déclarées à l’avance admettent4/7 V3 et4/7 mixtes100 ; trois SIGXCPU par famille. Les sept sorties de chaque famille contiennent un DTO/digest valide, mais le parent refuse correctement toute sortie issue d’un enfant non terminé avec succès. Aucun de ces refus n’est renommé succès.
Un wrapper diagnostique séparé, sans changement des sources ou limites, a observé un mixte ayant retourné main puis exécuté le témoin atexit à1,867390sCPU ; l’enfant est ensuite mort SIGXCPU à2,010212sCPU. Ceci localise ce témoin dans la phase après atexit ; cela n’attribue pas chaque instruction de GC ni tous les refus nominaux à une cause unique. Le wrapper n’est pas une qualification nominale.

## Brainstorming / Options / Risques / Choix proposé
- Conserver HOLD sans autre correction : sûr mais ne rend pas le lecteur fiable.
- Éprouver une fin explicite du seul enfant après fermeture/flush et statut exact : proposition bornée au défaut mesuré ; risque de sauter une obligation de nettoyage, à réfuter par tests et revue avant admission.
- Refactoriser les imports ou élargir les budgets : hors du présent delta ; aucune optimisation générale implicite. Accepter stdout après un signal est interdit.
Ce choix reste proposé, non accepté. Aucun changement worker n’est appliqué.

## Delta technique à soumettre avant apply
Fichier produit proposé : `app/services/muscle_observed_load/worker.py` uniquement. Tests proposés : `tests/test_muscle_observed_load_worker.py`, plus relecture des consommateurs existants et requalification sur le banc Linux autorisé. Aucun changement dans cet amendement V3 déjà autorisé.
Étudier puis éprouver une terminaison explicite du seul enfant après retour de main, fermeture des captures, encodage borné et flush explicite de la sortie ; conserver le code de sortie exact et le refus des exceptions. L’option `os._exit(status)` évitant le démontage général de l’interpréteur reste une proposition à tester/revoir, pas un correctif déjà prouvé ou appliqué.

## Gates exigées pour ce futur delta
- RED : conserver les refus nominaux actuels et le témoin post-atexit.
- GREEN : terminaison réussie du vrai worker sur Legacy/V3/mixte100, sortie complète, digest vérifié indépendamment, aucune donnée retournée si erreur/écriture partielle/pipe rompu.
- Capture SQLite close/read-only avant terminaison ; aucune obligation d’écriture différée ou nettoyage métier abandonnée.
- Parent : sortie anormale/signal/digest corrompu toujours refusés ; kill/wait, slot et propriétaire inchangés.
- CPU2/3s,AS512Mio,wall3s,SQL4096,VM2M,JSON/sortie inchangés. Aucun signal CPU ignoré ni prolongation du budget ; aucune promotion de stdout après SIGXCPU.
- Requalification répétée, revue indépendante, CI et livraison autonome sous GOV-MERGE-01 si admis. Tout défaut persistant conserve HOLD.

## Frontières
Ni nouvelle image cloud, activation, QA, infra, SCI, writer, TIME-01, client, données réelles ou release. Le futur paquet déployable et ses autorisations restent séparés.

## Décision réellement nécessaire
Autorisation distincte requise parce que worker.py est exclu des trois fichiers du GO V3 actuel. Formule proposée : « Autoriser le scope correctif de fin de processus du seul worker et ses tests décrit ici, à budgets inchangés et lecteur désactivé, sans opération de déploiement. »
