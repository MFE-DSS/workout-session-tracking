# NUT-01 — closeout du journal natif contrôlé

15 novembre 2026. **ENGINEERING MERGE vérifié.** Publication du présent closeout et conservation finale encore en suivi à cet instant. DATA, recette physique et release restent ouvertes.

## Résultat et décision opérateur

ConnectedApp ouvre le journal Nutrition depuis Progrès, dans la coque à quatre onglets. Journée et zone explicites, quatre faits facultatifs, zéro distinct de l’absence, complétude déclarée, cibles personnelles STANDARD/TRAINING/REST et leurs références historiques, corrections et mémoire 7/30 jours. Aucun apport, recommandation ou fournisseur inventé.

Le GO technique, le G1 fonctionnel, le master B DA07 et la famille DA08 sont conservés. Décision native finale : **« Accepter les pixels NUT pour le pilote, avec réserves artistiques »**, question `call_ac972e9af5dd4c2698c6f2c131cce4eb`, reçue avant commit UI. Le refus antérieur est levé pour le pilote contrôlé. Les réserves ne constituent pas une acceptation artistique finale universelle ; aucune variante ou baseline nouvelle après ce gate.

Le reçu exact est archivé dans `openspec/changes/archive/2026-11-15-nut-01-manual-daily-ledger/NATIVE_PIXEL_ACCEPTANCE.json`. Board : http://127.0.0.1:8264/ ; 17 captures. Paquet SHA256 `34754c0bb82e27640bb8f014037e015a9ba38b9e539e43aad7c4e487570b9cf9`.

## Sources et vérification réelle

- [Code #406](https://github.com/MFE-DSS/workout-session-tracking/pull/406), HEAD `fc45ef769ef76c0a4b1bef9b8836967f9d2fefb5`, merge `c9ce3713c43261f896e1e552c09243837ff535da`, parent BODY `5b19dc77071a0bcab3d8048ed7a61e2e0b0e3084`. Arbres HEAD/merge identiques ; commit de merge gardé par expected_head_sha, quatre checks requis relus, aucun thread ou avis bloquant. Aucun bypass, squash ou force-push.
- [CI PR 43705775645](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/43705775645) et [CI canonique 43707036706](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/43707036706) : **completed/success, onze jobs chacune**. Chaque run a réellement exécuté **8 659 tests backend passants / 3 ignorés, 108 suites / 1 292 tests mobiles + TypeScript, 77 visuels**. Attestation SHADOW seulement ; aucun test remplacé par réutilisation ou skip manuel.
- Local : tier MIGRATION ; campagne exhaustive de 447 fichiers, 8 668 PASS / 1 ignoré, composée après arrêt mémoire à 1 906 Mo. Deux fichiers lourds repris par 171 nœuds, puis 178 fichiers de queue, sous garde 1 600 Mo. Pics 305/1 166 Mo. Ce n’est pas un run ininterrompu ; les échecs de ressources restent conservés. Sources app/migration inchangées après campagne, tri d’imports d’un test puis 3 PASS ciblés.
- Quatre checks migration/drift/snapshot passants ; Ruff neuf, budget 260 ≤ 548, protocole, Bandit -ll et Gitleaks passants ; OpenSpec 26/26 avant archive. Dernière suite mobile locale : 108 suites / 1 292 PASS + TypeScript ; 25 gardes UI/documentaires et 14 tests d’inventaire.
- Revue indépendante entière sur 70 sources : cinq Important corrigés en une passe RED→GREEN, deux mineurs différés. Le rapport original et les rulings restent dans REVIEW_AND_VALIDATION.md et review/INDEPENDENT_REVIEW.md. Pas de second avis indépendant des correctifs finaux prétendu.

## Sonar consultatif, sans atténuation

Sur le HEAD exact de #406 : **ERROR**, 47 CODE_SMELL (6 CRITICAL de complexité, 35 MAJOR, 6 MINOR), zéro nouveau bug/vulnérabilité/hotspot ; couverture app 92,2 %, nouvelle 88,70748299319727 %. Le score de gate smells 20 > 14 n’est pas le compte de 47 issues. Aucune modification de seuil ou d’état d’issue.

Canonique c9ce3713, analyse `01d50acd-dc66-43f1-9656-a7595a594621` : **ERROR consultatif**, 8 bugs / 629 smells / 8 entrées sécurité externes historiques / 0 hotspot ; couverture 92,2 %, nouvelle 92,25007550588946 %. Les 16 entrées bug/sécurité ont été inspectées : tous leurs fichiers sont identiques au parent BODY 5b19. Cette attribution ne vaut pas déclaration globale d’innocuité.

## Preuve native et limites

Vrai ConnectedApp iOS 26.3, 390 × 844 pt, API/SQLite réels sur données synthétiques : accord nutrition distinct, zéro/valeurs inconnues, décimal FR 1,25, correction, cible personnelle créée et explicitement associée, complétude indépendante, mémoire et retrait. Une correction a été committée avant une panne de transport 503 de test ; kill/reprise SQLite et lecture du reçu exact, deux POST DAY au total pour création et correction, aucun troisième POST de reprise.

Les Hosts Android de production 360/480 dp et texte 130 % sont distingués des rendus ConnectedApp iOS. Android ConnectedApp complet reste limité dans Expo Go par le module natif conservé ; aucune suppression ou shim. Physique, rotation et gestes/focus/accessibilité exhaustifs restent ouverts. Les vues de mémoire positionnées en Host ne prouvent pas le défilement tactile complet de ConnectedApp. Les incidents de saisie/scroll du banc restent documentés.

Deux mineurs : audit de journée désactivé en lecture seule et accès direct à une ancienne cible liée hors candidats ; états ACTIVE/WITHDRAWN/enabled/complétude non résumés dans chaque ligne d’audit. Les réserves artistiques restent au suivi, sans prétendre livrer le state of the art final.

## Schéma, reprise et release

Deux tables serveur append-only : nutrition_day_revisions_v1 et nutrition_target_revisions_v1. Migration nutrition_manual_01 après body_measurement_operations_01 ; pas de DDL au startup, de réécriture de BODY ou de seconde chronologie corporelle. Accord nutrition_manual distinct, CAS et propriétaires serveur. Table nutrition_pending_commands_v1 sur la connexion/queue du journal possédé ; corps et clés durables avant HTTP, partitions compte/backend, vérification exacte et rejeu seulement explicite.

Rollback : suspendre les nouvelles acquisitions dans la configuration autorisée, préserver révisions et reçus ; downgrade peuplé refusé. Aucun effacement d’historique pour faire repasser une migration. API/contrats dans QA_RELEASE_HANDOFF.md ; SDK/modules/locks/runtime/canal/signature et science inchangés.

L’APK QA02 source 5ed4e0e2 ne contient pas ce slice. Aucun nouvel APK, OTA, service partagé, DNS, déploiement ou activation de données réelles. REL-03 assemble les fonctionnalités réellement fusionnées pour un candidat consolidé sous ses gates. MOB-06 reprend ce parent sans rouvrir BODY/NUT ; ses pixels et sa CI restent distincts.

## Archive et conservation

Archive OpenSpec CLI `2026-11-15-nut-01-manual-daily-ledger`, sept exigences canoniques. 19/20 tâches à l’instant d’archive : la seule case encore ouverte porte sur publication du closeout / vérification CI / nettoyage, à résoudre dans les reçus vivants finaux sans réécrire cet instant historique. Les gates DATA/physique/release sont documentées comme hors clôture engineering et restent ouvertes.

Preuves durables : `/Users/martinfeldmann/auren-review/nut-canonical-integration-20261115/`, dont CODE_MERGE_RECEIPT.json, CI_PR_FINAL.json, CI_CANON_CODE.json, manifests de sources et paquets, logs RED/GREEN et banc privé. Identifiants et clés synthétiques hors Git et du paquet public ; aucun envoi automatique. Le board statique est conservé ; arrêt normal des seuls processus possédés après vérification PID/commande/cwd. Checkout opérateur et appareils personnels préservés.

## Correction bornée du closeout
La première CI du closeout43708884797 sur992c598 échoue dans pytest shard4 : test_nutrition_migration_draft cherche le brouillon gelé dans l’ancien dossier actif, FileNotFoundError. Échec reproduit localement ; chemin ajusté vers le même fichier archivé, dont les octets sont identiques au brouillon de c9ce371. Aucun SQL, migration active ou source produit changé. Le reçu vivant final consignera la CI du nouveau HEAD et conservera ce run rouge.
