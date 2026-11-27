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

## Banc natif en cours
Source candidate13211bc,1696fichiers embarqués attestés. Un seul module produit différent du candidatV3 précédent ; le registry documentaire a évolué par le closeout canonique. Ancienneimage6baa24c4 inchangée.
Deux défauts de packaging ont été conservés : payload600uid1000 illisible parrootcapCHOWNsansDAC ; fichiersharness600illisiblesparUID10001. Corrections des seules permissions/propriétaires du volumeharness neuf ; aucune capacité ajoutée, aucun codeproduit changé. Les premières commandes ne sont pas comptées comme exécutions nominales. ENTRY_SAFETY a réellement tourné et réussi dès le premier montage.
Matrice déclarée :Legacy7,Legacy1005,V310,mixte10010,500/501deuxchacun,chaîneabsente/préfixeancien/texteoversizeddeuxchacun,bundleeffectifabsentdeux. Les dixV3etdixmixtes sont admis,exit0 etdigests valides ; les refus500/501 restentSIGXCPU. Résumé complet après acquisition des reçus.

Finalisation des preuves : oracle d’isolation du snapshotSQL indépendant B=999réps/id4 corrigé uniquementdansleharness. A/B/vide ensuitePASS ; ancienneerreur conservée. Témoin ajouté deDTOcompletréel puisflushéchoué : refusstatut1/reap/slot. Finalbroad161PASS/4SKIPLinuxPy3.11.14 ;targeted23PASS/4SKIPPy3.14.7. Aucun nouveau produit depuis13211bc.

Revue indépendante :Importantcorrigé par témoinDTOcompletpuisstatut(signal/flush). REDmutantmémoire2FAILattendus/GREENréel163PASS4SKIP,nouveau témoinLinux5casPASS avec vrai slotacquis/libéré. Un mineur précision slotdirect résolu parcemêmeparcours. Produitidentique13211bc.


## État vérifié après qualification

La campagne native et la revue sont terminées : 32/32 cas nominaux admis, 38 digests vérifiés en incluant les six résultats UNKNOWN conservateurs. Les refus historiques et adversariaux sont conservés. Le code produit reste identique à 13211bc ; le broad final comporte 163 PASS / 4 SKIP Linux sur Mac.

Le nettoyage du banc est terminé : 25 conteneurs et 4 volumes propres au scope supprimés après export ; les 10 conteneurs préexistants, volumes et services sont inchangés. Reçu privé CLEANUP_RECEIPT.json. Les gates encore ouvertes sont la publication, la CI réelle, le merge et le closeout Git. Image opérationnelle NON REQUALIFIÉE, lecteur DISABLED.


Code PR456 HEAD741d971, merge3aef9d1. CI PR46067424247 et canonique46069395764 réellement completed/success11jobs,9064backend/3SKIP,1610mobiles+TS,77visuels. Sonar PR/canoniqueERROR consultatif ; S5754 maintenabilité au point d’entrée laisséOPEN et triagé, aucun changementseuil/règle. ArchiveCLI27novembre,1exigence ajoutée ; publication/CI closeout et cleanupGit restent ouverts à cet instant.
