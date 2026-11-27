# SCI-WORKER-EXIT-01 — ledger

27 novembre2026. Parent54f68f65 ; GO explicite reçu, WORK_IN_PROGRESS.

## Brainstorming / Options / Risques / Choix retenu
Design accepté de terminaison explicite du seul point d’entrée. Teardown normal conserve le défaut ; budgets plus larges et stdout après signal interdits. Risque : sauter une finalisation nécessaire ; fermeture, DTO/digest, bornes, écriture et flush sont testés avant statut0.

## RED / GREEN observés
- RED initial7échecs comprenait une erreur de fixture pytest réinstallant stdout/stdin entre setup etcall. Aucun code produit modifié avant réparation du banc de test.
- RED corrigé sur produit inchangé :4FAIL/18PASS/4SKIPLinux : teardown atexit23, digestcorrompu,DTOinvalide,écriturecourte.
- GREEN cibléPy3.14.7 :22PASS/4SKIPLinux. BroadPy3.11.14 après correction du seul nom de fichier contract(s) :160PASS/4SKIP,1warningdépréciationhttpx existant,sortienormale0. La mauvaise invocation sans test est conservée séparément.
- Ruff fichiersmodifiésPASS, budget260≤548, BanditworkerPASS, protocolePASS, OpenSpecchange strictPASS, diffcheckPASS. Aucun budget/baseline ignoré ou changé.
- Produit : worker.pyseulement ; vérificationDTOstrict/digest à la frontière,encodageborné,écriturecomplète,main conserve sescontextmanagers,flush avant statut0 puisos._exit. Superviseur inchangé.
- Le testJSONincomplet et les deuxsignaux vérifient parent/refus/reap/slot, aucune réussite partielle.

## Qualification native et garde opérationnelle
Mac sous20Gio initialement ;aucune mutation distante engagée. Accord distinct de suppression du seul cacheStableDiffusion1.5 reçu, exécution/mesure à confirmer. Docker local ne répond pas en8s ; aucun redémarrage ou reset. Pas de qualificationLinuxnative déduite des testsMac.

## Gates restantes
CampagneLinuxnativebudgetsconstants, revueindépendante,CIHEADexact,merge/closeout. LecteurDISABLED/NOT_QUALIFIED ; imageopérationnellenonrequalifiée.

Nettoyage SD1.5 autorisé call_df8b213a467e4865ba432d7604bf1e2b et exécuté viahuggingface_hub0.36.0 :40entréesrevalidées, gainlibreobservé4 266 754 048octets, libre25 211 232 256octets, seuil20GioPASS. Autresmodèles etcacheGradle conservés.
