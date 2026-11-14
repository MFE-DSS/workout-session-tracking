> État actuel12novembre : **GO TECHNIQUE reçu** « Autoriser le build technique NUT-01 », call_c1496d1a84e04b1a8dd61ad04f063aa6 ; [reçu exact](BUILD_AUTHORIZATION.json). Domaine/API/clients/recovery synthétiques en réalisation. G1/composition/pixels, intégration après BODY et activation/release restent des gates distinctes non satisfaites. Les formulations de préparation ci-dessous décrivent leur instant ; ne pas redemander ce GO ni lui attribuer une nouvelle UI.

# Design — NUT-01 / journal manuel quotidien

11 novembre 2026. **PROPOSED / NO_GO_BUILD / G1_PENDING / NOT_SERVED.** Base 3cf77e1. Ce design révisé suit le mandat MVP : manuel et cibles maintenant, acquisition assistée ensuite. La préparation SMART CAPTURE antérieure n'avait aucun GO ; elle reste sauvegardée hors worktree. Pas nouvelle table BodyMeasurement ou calcul SCI.

## Brainstorming / Options / Risques / Choix retenu

1. Attendre provider/vision : bloque le journal pour une dépendance désormais hors premier scope, rejeté.
2. Construire catalogue/repas/itemisation/scan et agrégats ensemble : plus vaste et risque de double compte, différé.
3. **Un agrégat quotidien manuel versionné + cibles utilisateur versionnées**, champs inconnus et couverture explicites : proposition retenue pour une tranche utilisable. L'interface future peut confirmer un candidat vers ce domaine, sans l'activer dans ce build.

## N01 — apports et jour

Une seule représentation servie : DAILY_AGGREGATE_USER_DECLARED. Par owner et local_day YYYY-MM-DD, kcal et protein_g/carbohydrate_g/fat_g indépendants, nullable ; zéro déclaré distinct de manquant. Ce sont les totaux saisis par l'utilisateur, pas une somme de repas prétendument capturés. Aucun remplissage énergétique depuis macros, portion ou aliment reconnu. Au moins un nombre connu pour nouveau jour ; un retrait explicite rend le jour WITHDRAWN, jamais total0.

Saisie numérique décimale FR, stricte finie non booléenne/non négative, clés/unités fermées. Limites techniques de précision/taille fixées et testées comme contraintes de transport, jamais bornes d'apports recommandés. Pas normalisation/saturation/auto-remplissage. Chaque champ atteste USER_DECLARED/MANUAL_DAILY_ENTRY ou correction ; source n'est pas mesure certifiée.

Date passée/aujourd'hui choisie, timezone IANA explicitement confirmée, futur refusé dans cette zone. Jour n'est pas heure de repas ; recorded_at serveur distinct. Changer la timezone de l'app ne réécrit aucune date. Clé logique owner/day (pas une deuxième journée par timezone) ; timezone est le contexte déclaré de la révision. Ce premier journal n'a pas de déplacement automatique d'un jour vers un autre : changement de jour ouvre un autre relevé, sans copie silencieuse.

## N02 — corrections et complétude

Chaque commande append une NutritionDayRevision, jamais overwrite d'un ancien jour : champs absents préservés, null explicite effacé, token de tête requis, original auditable. Une seule tête courante par owner/day, anciennes versions jamais additionnées. No-op refusé. Retrait du dernier fait = geste WITHDRAW explicite, pas zéro. Ce retrait métier conserve audit et **n'est pas effacement des données personnelles**.

`declared_complete` est une action « Journal du jour terminé », distincte de présence de quatre chiffres. Mutation d'apports remet false sauf confirmation explicite liée au nouvel aperçu dans la même commande. Jour complet ne prouve pas consommation mesurée ni exhaustivité objective. Jour absent/incomplet/retiré/valeur inconnue distincts. Aucune case de complétude précochée.

## N03 — cibles déclarées, pas prescription

NutritionTargetRevision append-only : owner, variant STANDARD/TRAINING/REST, effective_from explicite, revision/token, enabled, kcal/P/C/F nullable, source USER_DEFINED_TARGET et recorded_at. Aucun objectif initial, sexe/poids/activité ou recommandation calculée. Un preset doit avoir au moins un nombre connu, ou une désactivation explicite ; désactivation gagnante ne ressuscite pas un ancien preset. Le plus grand effective_from<=jour, puis dernière révision de cette clé, produit un candidat. Correction/date/activation nécessitent action explicite et CAS.

Le journal propose les variantes effectivement définies ; TRAINING/REST sont choisis humainement, jamais inférés d'une séance absente ni d'un plan. STANDARD est une cible générale déclarée, pas une prescription par défaut. Aucun choix automatique quand aucun n'est établi. Le jour conserve la référence exacte de cible acceptée ou null ; changer une cible plus tard ne réécrit pas ses comparaisons historiques. Modifier la référence exige nouvelle révision du jour. Un jour marqué repos n'atteste pas l'absence de toute activité.

Comparaison uniquement champ et jour où apport ET cible sont connus : différence arithmétique avec sources/refs, aucun jugement bon/mauvais. Pas 3 jours d'apports comparés à 7 jours de cibles. Données absentes =>pas de ratio/pourcentage inventé.

## N04 — deux tables serveur, une table locale

NutritionDayRevision : owner/day/TZ/revision, champs/état/complétude validés, provenance, target_ref nullable owner-bound, expected_head, request_id/digest, receipt et recorded_at. Unique(owner,day,revision) et unique(owner,request_id) dans namespace DAY. NutritionTargetRevision : owner/variant/effective_from/revision/valeurs/enabled/provenance, expected_head, request_id/digest, receipt/recorded_at ; unicités correspondantes dans namespace TARGET. FK composite propriétaire pour target_ref ; aucune référence étrangère. Reçus ancrés dans la révision de chaque domaine, pas troisième table concurrente de totaux/opérations. Lectures de status choisissent une namespace fermée, jamais un nom de table fourni librement.

Garde transactionnelle owner réutilisée selon domaine, vraie écriture SQLite fichier/CAS et unicités, aucun mutex mémoire comme preuve. Replay owner/namespace/request/digest avant CAS/permission nouvelle, ACK exact historique ; corps différent409. Révision/fait/reçu dans un commit, rollback sans demi-journal. Migration additive sans backfill/DDL startup. Autre dialecte non déclaré prouvé sans tests réels. Une seule table locale nutrition_pending_commands_v1 sur partition/connexion existante, namespaces DAY/TARGET : commit et lecture de clé/méthode/path/corps/digest/token exacts avant HTTP ; échec stockage interdit envoi. Pas média ni provider dans cette table.

Réponse perdue/kill : UNKNOWN persistant, GET status puis replay explicite même clé/corps sous même owner/backend ; absence pas nouvelle clé. ACK durable avant refresh ; A/B/logout/owner retiré invalident UI/effets, aucune lecture ou émission croisée. Pas queue offline automatique ni payload dans account metadata/lab/outbox de séances. Copies terminales aussi soumises DATA ; aucune durée/purge implicite.

## N05 — API et consommateurs

Contrat nutrition-manual/1.0.0 sous /api/mobile/v1/me/nutrition ; Bearer, no-store, version explicite, 406 mismatch, 404 inconnu/étranger,409 stale/idempotency,422 structure,503 stockage/intégrité. Owner côté serveur, pas policy/provider du body.

| Route | Effet |
|---|---|
| GET /capabilities | MANUAL_DAILY réel seulement ; états lecture/write/contrat, modes futurs non servis |
| GET /days ; GET /days/{day} | Période bornée <=366jours, pagination/couverture, tête et source |
| GET /days/{day}/revisions ; POST /days/{day}/revisions | Audit/intent SET_FIELDS, COMPLETE, WITHDRAW, SET_TARGET_REF sous CAS et clé durable |
| GET /targets ; POST /targets/revisions | Presets déclarés/versionnés, pas recommandation |
| GET /targets/{ref}/revisions | Audit propriétaire, sources et dates |
| GET /operations/{DAY|TARGET}/{request_id} | Reçu exact minimal, pas lecture actuelle |
| GET /export | Pages exhaustives propriétaires jours/versions/cibles/provenance ; pas export séances |
| GET/POST /consent | Finalité nutrition_manual distincte, version/action explicites |

Le modèle BodyConsent accepte déjà un consent_type texte : réutilisation du support technique avec **type nutrition_manual distinct**, jamais grant body_measurements réinterprété. Ce choix technique n'accorde aucun fondement/permission personnelle. Wording et politique réels doivent être approuvés avant activation ; contrôlé synthétique sans service externe après GO propre. Révocation ferme captures/cibles nouvelles, conserve lecture/récupération autorisées selon DATA ; retrait métier pas revendiqué effacement global. Pas bouton effacement média inexistant.

Vrai ConnectedApp dans Progrès, porte Nutrition commune ; pas cinquième tab ni dashboard. Un jour, une action dominante, formulaire compact et aide/source à la demande. Historique récent/période7 ou30jours ; SVG déterministe et alternative texte, champs inconnus non tracés comme0, anciennes versions exclues. Totaux renseignés par champ et nombres de jours connus/absents/partiels/terminés affichés ; somme contrôlée non représentable=>UNKNOWN_ARITHMETIC_RANGE, jamais Infinity. Aucun score d'adhérence ou promesse de nutrition optimale.

## N06 — acquisition future sans faux bouton actif

Port documentaire candidat pour CAMERA/LABEL/BARCODE/FREE_TEXT : source_ref/méthode/champ/unité/date/confiance/version, aperçu humain, jamais write automatique. Un barcode seul n'est pas une valeur nutritionnelle ; repas/portion inconnus restent inconnus. La confirmation future doit définir comment le candidat contribue à l'agrégat pour éviter d'ajouter un total de journée à un repas. Aucun SDK/permission caméra/parser/clé/provider/Capture/Extraction table installé ici. Fournisseur/modèle/coût/copies/extraction exigent scope et GO séparés. Le journal manuel et ses cibles sont complets sans eux.

## N07 — gates et trois jalons

Préparation seulement. Après BODY, canonique/leases/migration revus et GO NUT/G1 réel avant apply. Pixels familiaux synthétiques réels avant commit UI ; tests domaines/API/SQLite/local/natif, revue indépendante, check_scope migration attendu et scripts requis, CI exacte/merge autonome/closeout. DATA pour nutrition/cibles/copies/export/effacement, sécurité/physique/activation/release distincts ; aucune conformité générale.

Après engineering merge : manifeste MVP compatibilité JS/backend/schema/privacy, smoke composé et référence de candidate qualifiée à son niveau de preuve. Pas EAS Build/OTA automatique. REL-03 indépendant, QA02 ancien APK préservé ; aucune activation à partir de cette préparation.
