# MOB-03 — continuation DATA & FIRST PLAN


**Suite courante :** [DATA COMPLETION — reçu technique](MOB03_DATA_COMPLETION_RECEIPT.md). Consommateur poids, cycle durable et tests runtime complétés sans nouvelle UI ; ce rapport conserve la passe précédente et ses preuves historiques.
5 novembre 2026. Change unique `account-onboarding-native`, PR #353. Point de reprise : ce rapport complète le CR PO/architecte. **MOB-03 complet reste ouvert.** Canonique incorporé : 5fd18c3 ; ancien HEAD 2ba9fd4 préservé par merge, sans conflit. Aucun déploiement.

## Brainstorming / Options / Risques / Choix retenu

Le [plan avant code](../openspec/changes/account-onboarding-native/data-first-plan-continuation.md) écarte DELETE users + confiance aveugle dans CASCADE et une table serveur de reçus sans politique. Approche retenue : domaine corporel existant, gardes non destructives, intentions clientes durables et consommateurs fermés sans producteur. Nouveau GET de poids proposé puis accepté explicitement (« Valider le GET de poids proposé »), sans writer ni écran.

## Implémenté dans cette continuation

- Matrice [effacement/conservation](MOB03_DATA_RETENTION_MATRIX.md) et [graphe de 23 tables avec colonnes](MOB03_ACCOUNT_DATA_GRAPH.json), références sociales/copies/exports/sauvegardes/local compris. Aucun fondement légal ou délai arbitraire décidé ; défauts historiques de backup décrits comme observations du code.
- Réauthentification canonique avec relecture d'identité/époque/hash, et révocation globale atomique des anciens accès web/mobile/refresh. Helpers sans endpoint nouveau ni suppression implicite ; transaction appelante, identité périmée refusée.
- Intention d'effacement locale par propriétaire : réserve/claim atomiques, clé conservée après interruption, relecture sans renvoyer une mutation. Relance testée par véritable fermeture/réouverture SQLite (port Node), pas par un simple mock mémoire. Mot de passe absent du stockage. Pas de demande durable serveur prétendue acceptée.
- Résultat DELETED inutilisable sans vérificateur autoritaire et objet de confirmation courant. La marque locale de retrait précède logout/nettoyage ciblé futur ; le résolveur bloque un journal retiré en ligne/hors ligne et les réponses tardives. Aucun purgeur global, API d'effacement ou adaptateur de production fourni. 401/404/timeout ne prouvent rien.
- Important de revue corrigé : refus terminal pouvait bloquer toute nouvelle demande. `retryRejected` relit et vérifie le refus avant renouvellement explicite atomique lié à la précédente ; intentions pending/submitted/unknown non rouvertes. Tests de concurrence, reprise et refus non autoritaire.
- [GET propriétaire de poids](MOB03_WEIGHT_HISTORY_CONTRACT.md) et WeightHistoryClient réels : BodyMeasurement via body_profile, consentement/flag existants, kg, dates UTC et provenance UNKNOWN conservée, pagination stable. Aucune copie de User.weight_kg, aucun double-write ou backfill. Valeurs atypiques signalées sans corriger la base. Nouveau GET inscrit une fois dans MOB-00.
- FirstPlanClient préparé : schémas SCI v1 épinglés, structure/version/fingerprint/propriétaire/génération contrôlés, statuts métier séparés du transport. Le futur adaptateur doit valider l'échange canonique et ses références ; aucun client ne certifie la science depuis le seul schéma. Producteur absent par défaut → NOT_SERVED, aucune URL de moteur inventée ni appel MISSION en repli.

L'entrée AUREN, les formulaires et préférences compacts, les priorités facultatives, les déclarations de matériel historiques et le journal restent préservés. Aucun fichier de composition, token ou baseline visuelle modifié dans cette passe. La nouvelle SDK ne constitue pas une nouvelle page de poids ou un onboarding complet.

## Servi, non servi et dépendances

| Élément | État réel |
|---|---|
| GET poids | Implémenté et testable sous Bearer + flag corporel + consentement ; non déployé ; aucune UI native ajoutée |
| Demande/effacement | Orchestration et stockage local exécutables ; aucun producteur/API d'effacement activé, aucune donnée serveur supprimée |
| SCI-P01/P02 | Schémas/fixtures reçus sur le canonique, consommateur réalisé ; politique dose/temps/projection, adaptateur/API et vrai plan READY manquants |
| MISSION existante | Boucle historique préservée, pas une preuve de transformation Blueprint → premier plan scientifique ; aucun repli scientifique fabriqué |
| Consentement | Gate existante/retrait respectés par lecture ; octroi/retrait natifs et nouvelles acquisitions non livrés par ce GET |
| Recettes | Tests/API/HTTP isolés ; pas de recette physique Android/iPhone/force-kill déduite |

La fixture READY du consommateur est **SYNTHETIC_TEST_ONLY_NOT_SERVED**, tirée de l'exercice de protocole scientifique existant et vérifiée avec autorité de test. Elle est rejetée avec le vrai registre de politiques et n'est importée par aucun consommateur de production. Les huit fixtures SCI publiques restent inchangées. Pas de nouveau volume, seuil, score ou diagnostic depuis un souhait de priorité.

## Vérifications

Diff final local : check_scope **SHARED_CODE** ; **49 suites / 613 tests mobiles passants**, TypeScript sous Node22 ; **347 tests backend ciblés/broad passants** (17 modules, deux avertissements de dépendances). Ruff fichiers neufs et budget **264 ≤ 548**, Bandit ciblé, protocole documentaire et OpenSpec strict **6/6** passent. Aucun full sweep Python local : la CI réelle de la PR couvre le reste. Aucun changement de composition/token/baseline nécessitant une nouvelle acceptation visuelle ; le check visuel de CI reste applicable.

Publication et CI du HEAD final : le [reçu vivant dans la PR #353](https://github.com/MFE-DSS/workout-session-tracking/pull/353) donnera le SHA exact, le run et le verdict Sonar. Les nombres ci-dessus sont des preuves locales ; aucune réussite distante n'est anticipée dans ce fichier avant le push.

Smoke réel réussi : backend HTTP local jetable, fixtures synthétiques uniquement, vrai AuthSession + createTransport + WeightHistoryClient. Connexion propriétaire, deux pages 73/72 kg, headers no-store, déconnexion puis création réelle d'un autre compte → consent_required sans fuite du poids précédent. Serveur arrêté et base jetable retirée. Aucun credential QA ou backend de production utilisé.

Revue indépendante des fondations : 1 Important corrigé avec RED→GREEN ; point de fuseau du curseur reproduit puis normalisé dans le domaine et la frontière HTTP. Revue ciblée supplémentaire du GET après sa validation opérateur : aucun Critical/Important. Cette seconde revue porte le périmètre HTTP nouvellement ouvert, pas un second audit global.

Deux mineurs non bloquants différés : curseur à extrême du calendrier peut répondre 503 privé au lieu de400 ; client Date.parse permissif si un serveur futur sérialisait un jour inexistant (le serveur actuel sérialise des datetime valides). Constat historique no-store sur certaines erreurs génériques d'autres routes conservé comme mineur distinct. Aucun audit de sécurité exhaustif revendiqué.

## Gates et prochain travail

- Responsable/juridiction, exceptions de conservation et durées juridiquement justifiées, sauvegardes exploitées et protection de restauration, références sociales, reçus après effacement, URL réelles de confidentialité/demande : **politique ouverte**, matrice prête à arbitrer. Les chemins app et web doivent partager l'autorité future ; conformité Apple/Google non prétendue acquise.
- Contrats SCI désormais présents ; manquent leur **producteur et politiques approuvés**, la vraie fixture READY et l'adaptateur de démarrage correspondant. La prochaine dépendance scientifique demeure SCI-P02-INITIAL-POLICY ; aucune implémentation de moteur déduite de cette continuation.
- Déploiement compatible/rollback et recettes physiques restent des gates. Aucun identifiant QA lu, aucune installation MOB-02 remplacée.
- Une seule PR #353, pas de nouvelle PR de fonctionnalité. Aucun mécanisme versionné de merge partiel supprimant les gates du change complet n'a été identifié : la PR reste draft tant qu'elles ne sont pas satisfaites. GO MERGE permanent conservé, sans redemande inutile et sans faux GO BUILD.
- Suite autonome débloquée par les décisions/producteurs : raccordement dans ce change, cas de reprise complets et recette. MOB-04 sera spécifié après merge autorisé, sans prétendre l'intelligence initiale achevée.
