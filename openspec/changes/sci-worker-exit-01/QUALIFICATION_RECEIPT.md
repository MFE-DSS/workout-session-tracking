# SCI-WORKER-EXIT-01 — qualification du candidat contrôlé

27 novembre2026. **Candidat code PASS sur le profil testé ; image opérationnelle NON REQUALIFIÉE ; lecteur DISABLED.** Aucun nouveau PREPARE_IMAGE, changementQA/OVHourelease.

## Identité
Parent54f68f65, code13211bcb8f9bd2499af333577d725e914cf78986.1696fichiers attestés ; par rapport au candidatV3précédent seuls worker.py et registry documentaire canonique diffèrent, aucun autre produit. Image supportsha256:6baa24c49404b2dd8ad74a3d5b4d6f9af3c83c6923a5711a1ae1bf79aebe5e8c inchangée ; source candidate montée readonly. Profil synthétique de banc028e0eff060a266d7603f2c263c8bbad0d1313a62726f32ccbed38868b18c7fd,pas une admissionopérationnelle.
Linux/amd64 natif Debian13.3,Python3.11.14,SQLite3.46.1,UID/GID10001 ;conteneur1CPU/2Gio,128PID,networknone,rootfsro,capdropALL,nnp.

## Résultats nominaux déclarés avant campagne
| Cas | Admis / exécutés | CPU min–max | Moyenne / écart-type population | wall min–max |
|---|---:|---:|---:|---:|
| Legacy |7/7|1,415620–1,681174s|1,523107 /0,095795s|1,483683–1,776714s|
| Legacy100 |5/5|1,482917–1,636065s|1,550035 /0,050194s|1,552968–1,722997s|
| V3complet14 |10/10|1,583213–1,786174s|1,706169 /0,054109s|1,651181–1,882059s|
| Mixte100 |10/10|1,753630–1,913728s|1,836472 /0,051722s|1,833127–2,034489s|

32/32exits0,32digests recalculés indépendamment,32enfants reap. PicRSS nominal74 989 568octets. Les résultats restentPARTIAL là où leurs preuves l’exigent ;aucune promotionEXACT. Marge CPU minimale observée surmixte86ms seulement : campagne bornée, pas une garantie sous toutecharge.

Les anciens Legacy5/5,Legacy1003/3,V3etmixte4/7, SIGXCPU et témoin post-atexit restent intacts dans les preuves V3 empreintées. Aucun refus historique reclassé.

## Refus et états conservateurs
- 500et501 :4/4refusSIGXCPU(-24),aucun JSON valide promu.
- Bundleeffectifabsent :2/2refus,exit1,pas de fallbackcataloguecourant.
- ChaîneV3absente,préfixeancien,texteoversized :6/6DTOUNKNOWN admis conservativement,exits0/digestsvalides ;pas de totalinventé.
- Flushéchoué/pipefermé/exceptionavantvalidation :exits1 ;entrée réussieflushée :exit0 sansatexit23. JSONincomplet exit0refuséparparent ;SIGXCPU(-24)/SIGTERM(-15) refusés,reapetslotlibéré.
- CPU2/3s,AS512Mio,wall3s,SQL4096,VM2M,sortie1Mioinchangés. VM2M,allocation600Mio et débordementssortie refusés. Wallcap configuré3s :deuxobservations3,002543et3,002498s,kill/wait réels ;aucunegarantiehard-real-timePopen.
- DiagnosticSQLhorschronométragenominal :V3464unitésbudgetSQL ;mixte825. Aucun nouvelaccèsSQL par la finalisation.
- Snapshotsynthétiqueconcurrent9→9puis88,relectureDMLrefusée,integrityok.
- Readbackdes14identitésSET/reçus/révisions/contextesetsources conservé,machine/PER_IMPLEMENTsansconversionmasse.
- IsolationA/B/comptevide :1/1/0faits,réponsesA/BPARTIALetvideEMPTY,DBinchangée,digests/slotsPASS. L’oracle initial d’isolation reprenait à tort la fixturecanonique8réps/id9999 ;le snapshot exporté contient999réps/id4. Échec de banc conservé et oracle corrigé depuisSQL indépendant,sanschangementproduit.

Un témoin additionnel émet un DTO complet réellement produit puis échoue au flush : statut1 et refus du parent malgré des octets complets, reap et slot libéré. Tests locaux avant revue161PASS/4SKIPLinux, dont ce cas ajouté après le premier broad160PASS.

## Sécurité et portée
1819chemins/parents/permissions/ACLdu banc vérifiés,mutationsnonprivilégiéesrefusées. Ces preuves ne certifientpas unfuturmontageQA ni unadministrateurroot. S8707reste suivi séparément,nonclos. Le rapport inspect_runtime seul conserve sonHOLD générique ; la présente campagne qualifie seulement ce candidat monté et ses essais réels. L’image embarquée anciencode ne devient pasrequalifiée.

Deux défauts de permissions du harness neuf ont empêché les premiers lancements ;ils sont conservés comme échecs de préparation, pas comptés comme essais nominaux. Seuls UID/modes de nos copies etvolumeharness ont été corrigés,sanscapacité supplémentaire.

Preuves privées : /Users/martinfeldmann/auren-review/sci-worker-exit-01-evidence-20261127/,notammentNATIVE_MATRIX_SUMMARY.json,native-results/*.log,HISTORICAL_EVIDENCE_PINS.json. Conservation et nettoyage du banc terminés : voir le reçu ci-dessous.

## Revue et correction de preuve
Revue indépendante fraîche surbb6452b :aucunCriticalproduit ;unImportant de preuve (JSON{}avant signal masquait le contrôle du statut). Correction dans le seul test autorisé :DTOcomplet concordant propriétaire/fenêtre/as_of/profil,digestrecalculé,contrôlepositifpuisSIGXCPU/SIGTERM/flush. Les en-têtes sontfixésentests pour rendre les octets complets identiques.
RED :deuxéchecs attendusDIDNOTRAISE contre un mutantmémoire du seul contrôleexitcode du superviseur ;aucun fichiersupervisor modifié. GREEN :163PASS/4SKIPLinux,sortie0,broadfinal. Native AUTHORITATIVE_STATUS :contrôlecompletexit0admis,JSONincompletexit0refusé,SIGXCPU-24/SIGTERM-15/flush1refusés,reap/pipes/slot après acquisitionréellePASS.
Mineur de formulation corrigé :le premier collect_child direct vérifiait seulement que le slot était disponible ;le nouveau parcoursread_owned prouve réellement sa libération. AucunImportant restant après cette passe ;aucune modificationproduitdepuis13211bc.


## Conservation et nettoyage du banc

Le reçu privé `CLEANUP_RECEIPT.json` vérifie la suppression de nos seuls **25 conteneurs et 4 volumes**. Les sources, fixtures et reçus ont été exportés et vérifiés avant suppression. Les six archives distantes dupliquées ont été retirées seulement après vérification de leurs copies locales.

Les **10 conteneurs préexistants**, leurs identités et configurations, les volumes et les services sont conservés. Docker a retourné les deux montages QA dans un ordre différent : les états bruts restent conservés ; la comparaison trie uniquement par destination unique et conserve tous les champs. Aucun service, flag, secret ou paramétrage existant n’a été modifié. L’image support est conservée.

Le cache SD1.5 explicitement autorisé a été supprimé par le mécanisme officiel Hugging Face après revalidation : **4 266 754 048 octets** d’espace libre récupérés ; **25 211 232 256 octets** libres immédiatement après, seuil de 20 Gio satisfait. Les autres modèles et le cache Gradle n’ont pas été supprimés.

**Livraison Git/CI encore à vérifier.** La qualification porte sur le code monté dans le banc contrôlé ; aucune image opérationnelle reconstruite, activation ou release n’en découle.
