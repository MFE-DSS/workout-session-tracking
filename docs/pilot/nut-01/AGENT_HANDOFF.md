# NUT-01 — journal manuel natif et cibles personnelles

15 novembre 2026. Livraison contrôlée synthétique ; reçu rédigé avant le commit final. Le HEAD exact, son CI et le merge seront consignés dans le reçu vivant de PR #406 puis le closeout. Aucun ancien checkpoint ne vaut livraison complète.

## Comportement livré
Deux tables append-only `nutrition_day_revisions_v1` / `nutrition_target_revisions_v1`, unités milli-entières, zéro/null/absence distincts. Jour déclaré et zone explicites. Quatre apports indépendants, complétude humaine distincte, cibles STANDARD/TRAINING/REST saisies humainement et liées par version exacte. Aucun calcul4/4/9 ou objectif par défaut. Accord nutrition_manual séparé de BODY ; nouveaux effets réservés au flag existant et au contexte de test.

Migration additive `nutrition_manual_01` après `body_measurement_operations_01` du parent BODY `5b19dc77071a0bcab3d8048ed7a61e2e0b0e3084`. Les anciennes observations et lignées BODY restent inchangées. Pas de backfill/startupDDL ; downgrade NUT vide possible, historique peuplé refuse le downgrade destructif.

API propriétaire Bearer, négociation `nutrition-manual/1.0.0`, treize routes classées dans l’inventaire canonique. Lectures stables à deux watermarks, curseurs signés propriétaire/backend/fenêtre ; lecture interrompue jamais vide complet. Exact receipt avant permissions de nouvelle acquisition.

ConnectedApp ouvre Nutrition depuis Progrès dans les quatre onglets existants. Le journal SQL propriétaire attache nutritionPending sur la même connexion et queue sérialisée. Commande durable avant HTTP ; premier envoi réservé atomiquement. Après réponse perdue, reçu GET puis rejeu de la même commande seulement sur action explicite et conditions courantes. Aucune nouvelle clé ou répétition POST automatique. A/B/backend et réponses tardives gardés. Refus définitif conserve le brouillon et exige relecture explicite avant nouvelle commande.

## Autorisations
GO technique call_c1496d1a84e04b1a8dd61ad04f063aa6 ; G1 fonctionnel call_4cb89afa5a174deeb907e6a2f4864053 ; master DA07 B call_e22888c3c8c64715bb1544af27dc95fb ; famille DA08 call_cbab5c2ca76c4afd8bb803eb3115f699.
Pixels du board8264 finalement acceptés : **« Accepter les pixels NUT pour le pilote, avec réserves artistiques »**, call_ac972e9af5dd4c2698c6f2c131cce4eb. Ce reçu lève le refus précédent, conserve ses réserves et ne transforme pas le rendu en DA définitive, recette physique ou autorisation de release. Reçu exact : OpenSpec/NATIVE_PIXEL_ACCEPTANCE.json.

## Preuves et limites
Board local persistant http://127.0.0.1:8264/ ;17captures, ZIP SHA25634754c0bb82e27640bb8f014037e015a9ba38b9e539e43aad7c4e487570b9cf9. Sources/empreintes/tests dans `/Users/martinfeldmann/auren-review/nut-canonical-integration-20261115/`. Aucun secret/identifiant de connexion/base synthétique dans les documents Git ou le paquet public.

ConnectedApp iOS réel390×844 : accord, zéro, correction, clavier logiciel1,25g, cible personnelle2100, association, complétude séparée, réponse503 après commit réel, kill/relaunch puis reçu exact sans secondPOST. Historique synthétique via vraies API ; présentateurs Mémoire/Surface réels en Host iOS/Android360/480dp/130%. Android ConnectedApp complet reste limité par ExpoTopicSubscriptionModule dans Expo Go : module conservé, aucun shim. Gestes/focus/IME exhaustifs et appareils physiques ouverts.

## Statuts de parité contrôlée
| Consommateur | État | Limite |
| --- | --- | --- |
| API/domaine NUT | DOMAIN_ONLY (contrats serveur réels) | données synthétiques uniquement |
| ConnectedApp iOS en banc natif | VERIFIED_NATIVE | pas une app distribuée ni appareil physique |
| Présentateur Android Host | PARTIAL | pas de shell ConnectedApp complet ou recette physique |
| APK QA02 actuellement livré | NOT_SERVED | ne contient pas ce code ; source5ed4e0e2 inchangée |
| Photo/OCR/barcode/texte candidat | NOT_SERVED | ports futurs sans fournisseur/permission/action fictive |

## Suite
Après merge et CI canonique, archive/closeout du même scope ; réconcilier MOB-06 sur ce vrai parent NUT et ses leases. REL-03 prépare le candidat consolidé avec API/schéma/runtime/signature/rollback ; aucun APK par merge. DATA, infrastructure partagée, release et appareil restent des gates séparés.
