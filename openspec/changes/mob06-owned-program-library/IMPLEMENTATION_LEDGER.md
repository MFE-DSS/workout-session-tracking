> Checkpoint technique non UI : les étapes et fichiers de banc décrits ci-dessous
> portent sur le worktree conservé ou des preuves isolées, pas tous sur le HEAD
> de cette PR. La liste versionnée du checkpoint est TECHNICAL_CHECKPOINT.md.
> Aucun LibraryHost, ConnectedApp ou montage produit n’est livré à ce stade.

# MOB-06 — ledger du build autorisé

Base1462482a4e2bcd1fcde121d6f207a2131616e849, même branche
feature/bibliotheque-seances. GO BUILD/G1 call_4321044cec284c79898cb7d2dd483990.
Les choix/options/risques précèdent le code dans design.md ; exécution inline.

## Réalisé, non livré
Lectures bornées et références propriétaire/backend/epoch ; catalogue distinct
du programme ; statuts draft/validated/published conservés ; sélection par séance
supportée ; vrais guard_owner/admit_legacy_start/préflight/instanciation/adaptation
entière/projection d'exécution. Une absence d'observation reste NULL/non complétée.
Factory de routeur explicitement configurée, négociation exacte/Bearer/no-store,
réponses certaines liées au digest, transport incertain jamais converti en reçu.

Client strict/ressource mémoire, store SQLite opérationnel sur port de journal,
contrôleur sans rejeu automatique, Host/présentateur G1 existants nouveaux. Aucun
montage de ces nouvelles sources dans ConnectedApp/mobile_api/journal partagé :
leases séquencés BODY/NUT conservés. Pas de table/migration serveur, SDK, lock,
baseline, publication, APK, OTA ou déploiement.

## RED → GREEN et preuves
- Module de lecture absent puis15tests passants ; campagnes étendues aux bornes,
  programmes étrangers, ordre stable, prescription corrompue et concurrence.
- Source SQLite incohérente reproduite : compte2→3 dans la même lecture ; BEGIN
  explicite, témoin snapshot et deux départs concurrents2/2PASS.
- Service/routeur absents puis vrais consommateurs HTTP, pas de fixture servie.
- Client/store/resource/recovery/Screen/Host absents puis58tests natifs ciblés.
- Revue indépendante entière : deux Important et trois mineurs de fidélité au
  contrat. I1/I2 reproduits (6échecs), corrigés (30testsPASS) ; M1/M2/M3 reproduits
  (3échecs), complétés car exigences explicites du wire/D7,68tests ciblésPASS +TS.
- Broad avant ces derniers compléments :187backendPASS ;94suites/1180mobilesPASS.
  Ces campagnes sont datées, pas présentées comme CI ou SHA final testé.
- Banc iOS de modules : vraie migration/HTTP, perte du201 après commit observé,
  SENT_UNKNOWN natif ; kill/repriseSecureStore/SQLite, zéro replay, relecture
  propriétaire, annulation uniquement locale/UNKNOWN, A/B/A et offline/reconnect.
  Deux erreurs initiales du banc conservées : source QA retirée au seed canonique,
  puis mauvais chemin GET sans /execution. Aucun faux PASS de ces essais.

Preuves persistées hors checkout :
/Users/martinfeldmann/auren-review/critical-path-20261112/MOB06_*.log et
MOB06_IMPLEMENTATION_REVIEW.md, MOB06_NATIVE_PROOF/. Les identifiants du banc
sont privés0600 hors Git. Le banc n'est ni ConnectedApp complet ni recette physique.

## Rulings et coût
1. Nouveaux modules isolés d'abord, fichiers partagés après BODY/NUT — évite une
   PR chevauchante ; coûte une intégration ultérieure avant toute clôture.
2. Pas d'idempotence serveur inventée ; journal opérationnel et vérification
   explicite — un reçu perdu exige intervention utilisateur située, aucun replay.
3. session_open résout NOT_CREATED pour cette tentative et relit la vraie séance
   indépendamment de l'intention — son échec bloque les nouveaux départs, sans
   présenter cette séance comme le reçu d'une demande précédente.
4. Prédicats de connexion ET d'opération gardés — remplacement de journal même
   compte/backend invalide l'ancien port ; aucune réconciliation sur connexion retirée.
5. Vocabulaire, binding de détail et date de réception complètent le contrat
   accepté — aucune nouvelle science, inférence ou métrique de fraîcheur.
6. Lecture non SQLite non répétable refusée — coût : qualification explicite de
   l'isolation et des consommateurs avant un autre moteur de base.

## Gates encore ouvertes
Montage partagé après BODY/NUT, inventaire des routes réellement montées, preuve
ConnectedApp/journal complet, board iOS/Android final normal/grande fonte et pixels
opérateur, revue de l'intégration, contrôles du HEAD final et CI/Sonar réels,
commit/push/merge/closeout. BODY master non accepté conservé, aucun nouveau GO BODY
ou NUT demandé. Les GOs de ces domaines restent acquis.

## Reprise du 13 novembre — patch d’intégration vérifié, non appliqué aux leases
Même branche/canonique1462482 et diff initial33fichiers sauvegardés. Copie d’archive
isolée : root API + inventaire, vrai ConnectedApp/Programmes, store sur connexion
et queue réelles, adoption durable puis Today/reprise, redémarrage SQLite, A/B/A,
offline/reconnect et reçu perdu sans replay.152backend broad,1200mobiles/96suites+TS,
Ruff neuf/budget260≤548/protocole/Bandit/Gitleaks, OpenSpec25/25. Revue indépendante
I1navigation et M1couverture corrigés RED→GREEN, vérification nommée conservée.
Les fichiers libraryOpening/LibraryHost et le test de non-répétition du retour
sont conservés dans la branche (aucune géométrie nouvelle,17tests ciblésPASS).
Patch13chemins conservé et apply --checkPASS, mais leases BODY/NUT non libérés :
4conflits BODY et1NUT dans les copies de prévisualisation ; aucun parent écrasé.
Rendu ConnectedApp iOS réel de lecture ; recette tactile CUA indisponible et
bootstrap du banc corrigé. Aucune acceptation pixels ou preuve Android intégral.
Voir docs/pilot/mob06-library/INTEGRATION_READINESS_20261113.md et le dossier durable
/Users/martinfeldmann/auren-review/mob06-integration-20261113/. Aucun commit/PR/CI
produit, archive, merge ou APK par ce jalon. Planche artistique finale à produire,
programme actif/calendrier absents du domaine à préserver comme inconnus.

### Continuation13novembre — assemblage préparé et passation designer
Résolutions additives des cinq fichiers conflictuels préparées dans une nouvelle
copie, sans modifier BODY/NUT : ConnectedApp/journal/types mobiles combinés ;
routeur/config serveur en prévisualisationAST seulement.106suites/1276mobiles+TS
PASS, témoinSQL de coexistence BODY/bibliothèque gardant V3 et A/B. Revueindépendante
ciblée sans nouvelle régression,11tests/3suitesPASS ; aucun audit complet des
parents ou recette native déduit. Les inputs80BODY/49NUT restent identiques.
Paquetdesigner local : deux masters BODY/Programmes attendus, contenus synthétiques
réels exportés readonly,36fichiers de brief/références/sources empreintés, aucun
secret/DB/envoi tiers. CR dans docs/pilot/mob06-library/CR_DESIGNER_20261113.md ;
preuves /Users/martinfeldmann/auren-review/mob06-critical-path-handoff-20261113/.
Leases/canonique/pixels/CI/release restent ouverts ; aucun commit/PR/merge/APK.

### Réception étudecommune —13novembre
Étude dualmaster18fichiers/7SVG reçue, hashée, nonapprouvée ; aucune reconstruction.
Contrats relus : état prévu sans inférence de nonexécution, vérification du départ
sans ledger d’idempotence inventé, métadonnées BODY exactes. Retourunique etJSON
complet remis directement dans /Users/martinfeldmann/auren-review/dual-master-study-20261113/.
Aucun code/CI/merge/activation ; les preuves1276mobiles restent celles de la
campagne d’assemblage antérieure, pas un nouveau run.

### Révisionétudecommune —13novembre
Révision19fichiers/8SVG reçue sansacceptation ; correctionsP1–B3 observées.
Noms/structuresQA et exemplescataloguecore remis en texte directementcopiable,
pour supprimer la dépendance aux cheminsMac dans le tourdudesignerexterne.
CatalogueMOB06=séances, pasfichesexercices ; identitérepriselue distincte de la
séancedemandée. AucunSVGmodifié ouintégré, aucun code/CI/APKnouveau.
Dossier : /Users/martinfeldmann/auren-review/dual-master-revision-20261113/.


### Complément du 13 novembre — répétition d’assemblage complète

La copie combinée BODY/NUT/MOB-06 couvre désormais 449 fichiers backend par
sweep et reprise bornée, avec quatre écarts conservés puis relectures ciblées
34/25/1 PASS ; mobile final 106 suites/1277 PASS + TypeScript. Les résultats
initiaux ne sont pas réécrits en un faux full sweep uniformément vert.
Les patches serveur/schéma et journal NUT partagé sont préservés hors branche ;
aucun fichier partagé live ni pixel n’est appliqué ici. Master BODY et Programmes
restent non acceptés ; aucune nouvelle PR, CI, release ou clôture de produit.
CR durable : `/Users/martinfeldmann/auren-review/AUREN_CR_ASSEMBLAGE_BODY_NUT_MOB06_2026_11_13.md`.
