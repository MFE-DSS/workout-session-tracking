> GO BODY-01/amendement/G1 reçu le 11 novembre 2026 : « Autoriser BODY-01, son amendement et G1 » (call_106057b169a74bc9887b1fea9f527f5d). Apply contrôlé en cours ; pixels non acceptés, aucune activation/release. Les statuts pré-GO ci-dessous gardent leur instant de préparation.

# Design — BODY-01 : mesures datées et corrections traçables

11 novembre 2026, base `3cf77e17f37448980b115d8e0e0adad783c1d0b2`.
**PROPOSED / NO_GO_BUILD / G1_PENDING / APPLY_CLOSED.** Le mandat MVP choisit la direction : conserver les originaux et tracer les corrections. Il ne vaut pas encore approbation de la migration, des lecteurs et du delta normatif ci-dessous. Un seul GO peut approuver ce paquet et G1 ; aucune nouvelle question de principe sur cette direction.

## Intent et contraintes

Saisir poids/tours datés, corriger une erreur et revoir les versions sans fabriquer une nouvelle pesée. BodyMeasurement est le seul stockage de nombres corporels ; BodyConsent existant porte l'accord pertinent. Progrès MOB-05A et son graphique déterministe sont réutilisés. Pas d'APK/OTA à chaque merge, de données personnelles ni déploiement dans ce build contrôlé.

Observé : création INSERT, éditeur web mutable, suppression réelle, lecteurs bruts. Sx_MORPHO_CAPTURE_01_SPEC §2.1 prescrit l'ajout prospectif, les contrats manuels décrivent edit/delete. CONTRACT_RECONCILIATION propose leur amendement explicite ; aucune donnée existante n'est migrée/requalifiée. Aucune formule morphologique, score ou autorité SCI n'est redéfinie.

## Brainstorming / Options / Risques / Choix retenu

1. Édition en place + reçus sans anciennes valeurs : petite, mais perd les originaux ; ancienne option A abandonnée selon le nouveau mandat.
2. Nouvelle table numérique de snapshots : seconde chronologie, rejetée.
3. **Versions dans BodyMeasurement, liens/provenance dans un sidecar metadata, lecteurs courants distincts de l'audit** : choix technique proposé pour réaliser la direction opérateur. Coût assumé : adapter tous les lecteurs pertinents et les writers legacy. Une correction ne compte pas comme observation indépendante.

## B01 — fait, version et provenance

Un relevé logique est identifié par root_ref. Une nouvelle observation crée une racine, même le même jour qu'une autre. Une correction insère une nouvelle ligne BodyMeasurement avec nouvel id, liée à la racine et à son unique tête précédente. Original et versions antérieures inchangés. measurement_id identifie la version physique, distinct de root_ref. Une ligne legacy sans metadata est sa racine et sa version virtuelle 0, sans backfill.

La nouvelle version est une représentation complète du même relevé : champs absents recopiés, null explicite effacé, valeurs soumises validées. Les champs hérités gardent source originale/UNKNOWN et qualité ; seuls les champs corrigés attestent USER_DECLARED / MANUAL_CORRECTION. Une copie n'est pas une nouvelle acquisition. Aucun writer web/natif/helper ne modifie l'original en place.

Champs/bornes BODY_MEASUREMENT_FIELDS, poids kg, tours cm, G/D indépendants. calf_cm hérité lisible non inscriptible ; taille User.height_cm hors scope. Aucun poids de profil/séance copié. Corriger un seul champ conserve les autres, y compris l'héritage hors bornes ; seuls les champs modifiés passent les bornes actuelles. Au moins un fait non nul reste requis, sinon effacement explicite. Date seule possible, PATCH vide/no-op refusé.

## B02 — temps et qualité

Saisie native : measured_on YYYY-MM-DD explicite, valide et non futur en UTC ; stockage 00:00 UTC avec DAY_UTC_CONVENTION, jamais heure réelle prétendue. created_at de la nouvelle ligne et recorded_at d'opération sont serveur. Date du fait distincte de date de correction. Corriger la date déplace le point courant ; ancienne date conservée, pas nouvelle pesée.

SSR conserve son parsing actuel, dont date invalide/future vers now, marqué SERVER_CAPTURE_TIME. Héritage sans preuve UNKNOWN. JSON strict : nombres finis non booléens, clés autorisées ; virgule FR normalisée UI. Lecture/export : value fini ou null, raw_value_repr et quality MISSING / KNOWN / LEGACY_OUTSIDE_CURRENT_BOUNDS / INVALID_NONFINITE. Ni NaN JSON, zéro, omission ni nettoyage des anciennes lignes.

## B03 — persistence additive et identité

Une table serveur body_measurement_operations_v1 : owner_id, request_id unique par owner, command_digest, operation CREATE/CORRECT/ERASE, root_ref, parent_ref nullable, measurement_ref, applied_revision, changed_fields, provenance_by_changed_field, date provenance si changée, fingerprints avant/après, recorded_at et receipt minimal. **Aucune valeur numérique ni corps complet de commande dans ce sidecar.** Nombres/dates du fait uniquement dans BodyMeasurement. Unique(owner,root,revision), enfant CORRECT unique par parent, indexes owner/root/request et supersession. ERASE référence la dernière tête, pas une ligne numérique fantôme. CREATE commence à1, première correction legacy à1 depuis0. Token lie owner/root/tête/révision/fingerprint ; hash ne prouve aucune acquisition.

Aucune colonne/reconstruction/UPDATE/DELETE de migration BodyMeasurement ni backfill. Références historiques sans FK cascade vers ligne numérique effaçable ; liens inter-owner refusés sous garde transactionnelle, tests obligatoires. Sidecar rattaché au cycle du compte ; effacement de copies et réservation d'identité restent coordonnés avec DATA.

SQLite fichier seul dialecte admis initialement : vraie transaction d'écriture globale, pas mutex mémoire. Pour CREATE et CORRECT, id = 1 + max des ids BodyMeasurement et de toutes les références réservées dans le sidecar, tous owners confondus. Allocation/fait/sidecar/reçu dans un commit. PK ordinaire conservée, aucun AUTOINCREMENT/rebuild. Limite positive Number.isSafeInteger : refus explicite à épuisement, jamais réutilisation. Purger les références de réservation exigerait un nouveau mécanisme d'identité avant reprise des writes ; aucune conservation permanente juridique inventée. Autre dialecte ou writer non gardé : non admis avant preuve/revue.

## B04 — commandes communes et concurrence

Auth/owner d'abord. Replay owner/request/digest avant CAS, état courant et permission de nouvelle mutation : ACK historique exact après correction/effacement, sans valeurs ni nouvelle permission. Autre digest409. Sinon transaction d'écriture, relookup replay, consentement/flags, tête/token, validation, INSERT correction ou effacement confirmé, sidecar/reçu atomiques. Deux corrections même tête : une gagne, l'autre409 ; aucune branche/fusion. Même request : un seul effet.

Extraire kernel flush-only, conserver wrappers publics. Tous writers runtime : body.py create/edit/delete, auth_routes.py profile_measurements_submit et callers identifiés au préflight. Edit web conserve présence des champs mais insère une version. Formulaire web token de tête et confirmation de portée ; onglet périmé refusé. Version superseded lisible en audit, non mutable sans relecture de la tête.

Schéma/guard absent après installation : toutes mutations SSR/natives fermées, y compris /profile/measurements hors flag /body. Aucun DDL startup/fallback vers ancien writer/cache comme preuve de transaction. Retrait accord bloque nouvelles captures/corrections, pas reçu minimal historique. Effacement propriétaire ne requiert pas nouveau grant de collecte, selon B06.

## B05 — lecteurs courants et audit

Sélecteur SQL partagé : têtes non effacées, anti-jointure de supersession owner/root, pas N+1. Une version remplacée n'est jamais repli d'un champ explicitement vidé sur sa tête. Les autres relevés indépendants gardent la règle historique du dernier non-null ; aucune nouvelle formule scientifique. Filtres période/as_of sur temps du fait de la tête ; aucune reconstruction d'un ancien score tel que connu à l'époque prétendue.

Lecteurs dans le scope : body_profile (list/poids/export), body_ledger, morphology_runtime, body_intelligence_inputs, measurements, muscle_scoring, dashboard, coach_report. Budget une requête body_ledger et règles G/D conservés ; seule éligibilité des versions change. Aucun snapshot/session/qualification SCI réécrit. Préflight tous usages ORM/SQL ; lecteur oublié/source pinée incompatible => STOP avant activation, pas omission commode.

Audit propriétaire : toutes versions conservées de racine, CURRENT/SUPERSEDED, liens/champs modifiés/provenance. Jamais source du graphique courant/fréquence. Deux observations indépendantes le même jour restent deux faits ; pas nouvelle moyenne, interpolation ou regroupement.

Compatibilité choisie : weight-history/1.0.0 garde forme et décodeur exacts mais filtre les versions remplacées. Son profil limité conserve UNKNOWN plutôt qu'une provenance non transportable ; projection de compatibilité documentée comme telle. Legacy sans correction inchangé. Nouveau DTO body-measurements/1.0.0 source-aware pour BODY et fenêtre poids Progrès, réutilisant le graphique WeightTrend/SVG via modèle de présentation adapté. Ne pas élargir silencieusement le décodeur v1, ni créer cache canonique local. Historique séances MOB-05A inchangé.

Curseur BODY lié owner/plage/body-revision (dérivée du ledger) : mutation concurrente =>409/relecture plutôt qu'un résultat incohérent. Nouveau client garde A/B/période/réponses tardives et précédent/hors ligne/inconnu. Lecteurs nécessitant l'applicabilité des versions refusent si schéma absent, aucun brut de secours ressuscitant les nombres. Rollout migre avant ce code ; compatibilité ancienne version à éprouver sur copie.

## B06 — correction conservée, effacement distinct

« Supprimer ce relevé et ses N versions » est une action confirmée avec CAS tête : hard-delete de toutes les lignes BodyMeasurement de cette racine possédée, jamais tête seule qui ferait revenir l'original. Fait ERASE/reçu sans valeurs ; identifiants réservés/metadata minimales restent copies personnelles DATA. Replay identique. Ancienne version/étrangère ne permet pas effacement d'une autre racine.

GO proposé inclut explicitement cet effacement utilisateur individuel sur bases synthétiques ; migration elle-même sans suppression. Export nouveau exhaustif courant/versions/calf/provenance ; ancien export garde forme et projette les têtes. Suppression de tout profil, fermeture/export globaux et politique copies/backups/local restent des gates DATA avant activation, sans conformité générale prétendue. Clarification normative expose ce reliquat. Aucun délai/purge automatique inventé.

## B07 — transport proposé

Sous /api/mobile/v1/me/body, Bearer existant, no-store :

| Route | Effet |
|---|---|
| GET /measurements | Têtes, plage <=366 jours, limit1–100, curseur owner/plage/body-revision |
| GET /measurements/{root_ref} | Tête possédée, token courant, valeurs/qualités/sources/dates |
| GET /measurements/{root_ref}/versions | Audit borné/paginé, pas série graphique |
| POST /measurements | request_id, measured_on, values ; observation nouvelle |
| POST /measurements/{root_ref}/corrections | request_id, expected_head_token, values partiels, date optionnelle ; nouvelle version |
| POST /measurements/{root_ref}/erase | request_id/token/confirmation de portée ; B06 |
| GET /operations/{request_id} | ACK minimal ; absent=UNKNOWN, pas preuve de non-commit concurrent |
| GET /measurements/export | Route statique avant dynamique, pages exhaustives faits/versions/metadata autorisées |
| GET/POST /consent | BodyConsent existant, version/action explicites, pas grant automatique |

401auth ;404inconnu/étranger ;403accord ;409conflit/cursor/idempotency ;422structure ;503intégrité/schéma. DTO body-measurements/1.0.0 : root_ref, measurement_id/version, état/token, measured_at/date_precision, recorded_at, champs typés/provenance. Reçu request/op/root/version/id/time/state sans nombres. ACK distinct de lecture actuelle.

## B08 — reprise durable sans seconde chronologie

Une table locale body_pending_commands_v1 sur connexion/file du journal possédé : owner/backend_scope, request_id, method/path/body exacts, digest, logical_key=root, PREPARED/SENT_UNKNOWN/ACKED/REJECTED et reçu minimal. Une commande non terminale par racine. Corps/token figés, commit+relecture locale avant HTTP ; panne locale =>aucun envoi. Brouillons non confirmés en mémoire, pas queue offline générale.

Après kill/réponse perdue, même owner/backend authentifiés : « Résultat à vérifier », GET receipt puis replay explicite même clé/corps, jamais nouvelle clé depuis GET absent. ACK persisté avant refresh ; lecture source séparée. A/B/logout invalide UI/promesses, pas transfert payload ; owner retiré/non prouvé ferme lecture/envoi. Tables PLAN/outbox/séries inchangées ; preview mémoire sans mutations. DATA couvre nouvelles copies/effacement/rétention, sans durée/purge implicite après ACK.

## Visuel, vérification et jalons

Famille native G1 UX_BOARD : poids/tours/correction/audit/effacement/reprise. Primitives/tokens/baselines LOCKED. Delta SSR token/confirmation dans même gate. Pixels iOS/Android normal/grands caractères avant commit, pas acceptation héritée de MOB05.

Tier migration attendu après apply, verdict check_scope réel ; ciblés/broad/migration/drift/snapshot et sweep local borné selon règles, vrais consommateurs/courses SQLite, revue indépendante, CI HEAD final, merge GOV-MERGE-01/closeout. Fonctions/organisation internes laissées au builder dans leases, pas extension de domaine.

Engineering : vrais writers/lecteurs cohérents sur synthétique. Manifest MVP classe JS/backend/schema/privacy, SCI inchangé ; pas de nouveau runtime natif présumé sans examen. Integration candidate après smoke composé. External pilot release séparée : cible stable/permissions/RC/autorisation ; aucun APK/OTA ici. QA02/worktrees/appareils préservés.
