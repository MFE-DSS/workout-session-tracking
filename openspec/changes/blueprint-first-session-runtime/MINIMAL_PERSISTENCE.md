# PLAN V3 — persistance minimale proposée à approbation

7 novembre 2026, canonique d7de8aa. **Design uniquement, aucun modèle, DDL ou migration appliqués.** Ce document remplace la liste initiale de dix tables du design ; architecture serveur et contrats SCI approuvés conservés.

## Brainstorming / Options / Risques / Choix retenu

Deux variantes respectent les invariants : dix tables spécialisées initialement prévues, ou regroupement des enregistrements de même grain. Proposition retenue : **sept tables, sans nouvelle colonne User/WorkoutSession/SessionExercise/SetLog**, avec trois indexes composites sur tables existantes. Les scopes restent séparés : faits sources, capture, décision, commande, prescription immuable, observation typée et autorité opérationnelle.

Le nombre n'est pas un objectif au détriment des garanties : pas de table JSON universelle, ni idempotence ou provenance supprimée. Le journal source porte sa révision ; un ack est une nouvelle évaluation immuable ; le CREATED durable porte le premier handoff. Une autorité partagée est ajoutée : elle manquait à la liste initiale et ne peut être remplacée par un booléen de processus.

## Réemploi et contre-proposition écartée

| Existant réellement lu | Réemploi | Pourquoi il ne porte pas ces nouvelles lignes sans changement de sens |
|---|---|---|
| User / DeviceSession, deps et device_auth.resolve_access | identité, époque, révocation et garde propriétaire | session_epoch révoque les accès ; il ne devient pas révision Blueprint. Aucune nouvelle identité ou chronologie corporelle dans User |
| TrainingPreferences / services.training_preferences | valeurs canoniques cadence/priorités/matériel conservé | mutable, pas de provenance par fait, de budgets/limitations/objectif/population ni de ledger de qualification ; updated_at global n'est pas une acquisition |
| DecisionTrace | domaine historique conservé, pas nouveau snapshot complet implicite | événement explicatif OWNER_LIFETIME, sans identité idempotente propriétaire/opération/corps, FK snapshot/parent-ack ou statut de commande ; réutiliser ses champs génériques imposerait une nouvelle sémantique/retention à ce contrat |
| RecommendationEpisode | parcours historique conservé | top_slug obligatoire, alternatives de gabarits, policy_version String(16), résultat mutable ; V3 ne possède pas de faux slug/template à lui fournir |
| BodyMeasurement / BodyConsent | chronologie corporelle et finalités actuelles uniquement | ni charge d'appareil, ni limitations, ni ack de temps ; le consentement body_measurements n'autorise pas automatiquement un autre traitement |
| Workflow account_deletion_requests | autorité de fermeture à coordonner | autre machine d'état et capacité secrète ; pas un registre de commandes de séance |
| WorkoutSession / SessionExercise / SetLog | seuls faits canoniques de séance/série | pas d'instantané de prescription V3 ou de sémantique de réglage ; weight_kg n'est pas kg affichés ou kg par haltère. Ajouter seulement le dernier op_id ne protégerait pas d'un ancien rejeu après correction |

Sources : app/models/{user,training_preferences,session,decision_trace,recommendation_episode,body_consent}.py, app/deps.py, app/services/{device_auth,training_preferences,account_deletion_requests}.py. Lecture ciblée, aucune base utilisateur inspectée.

## Conventions de schéma communes

UUID opaques générés serveur pour captures/évaluations ; request_id/op_id du client validés, jamais clés d'identité de compte. owner_id vient de l'authentification. JSON canonique typé dans Text, convention du dépôt ; colonnes explicites pour recherche, FK et unicité. Hash du corps couvre opération/version/cible et types, pas mots de passe/tokens. Horodatages UTC explicites ; événements importés gardent leur occurrence et leur origine.

Six tables propriétaires ont FK users **NO ACTION**, proposition de garde empêchant une suppression racine aveugle avant politique DATA. Ce refus technique ne décide aucune conservation/durée légale. Relations internes sans effacement implicite des preuves. L'exécuteur DATA devra traiter le graphe selon politique admise ; ni purge ni changement de ses invariants dans PLAN. Aucun TTL ou faux consentement inscrit par cette proposition.

### 1. BlueprintSourceEvent — blueprint_source_events

- Invariant : une mutation pertinente et sa provenance acquièrent une seule révision immuable, y compris depuis writers historiques. Remplace SourceRevision + DeclarationRevision + ObservationEvent.
- Champs : id UUID, owner_id, source_revision entier positif, request_id, operation_kind DECLARATION/OBSERVATION/PREFERENCE_WRITE/SOURCE_INVALIDATED, body_digest, payload_version, payload_json typé, recorded_at UTC et source_ref. Occurrence originale dans le payload, pas redatée.
- Contraintes : UNIQUE(owner_id, source_revision), UNIQUE(owner_id, request_id), UNIQUE(owner_id,id) ; index (owner_id,source_revision). Révision courante = MAX(source_revision), zéro seulement si aucun événement ; token texte SCI `blueprint-source/N`, pas entier dans le DTO. Lecture du max puis append sous la garde propriétaire commune ; aucun second compteur libre.
- Transaction : validation/flush canonical TrainingPreferences + événement et révision ensemble ; aucun helper ne committe seul. Champs nouveaux seulement dans le ledger, pas dans User.weight_kg. Un ancien formulaire ne remplace pas les nouveaux faits.
- Lifecycle : append-only ; corrections = nouvel événement ; snapshots et commandes ne modifient pas l'origine passée. DATA doit autoriser ces copies de déclarations/observations et leur export/fermeture.
- Rollback : couper nouvelles acquisitions ; les faits et leurs sources restent lisibles. Pas de DELETE d'événements pour faire revenir une révision.

### 2. OwnedBlueprintSnapshot — owned_blueprint_snapshots

- Invariant : prouver les faits/provenances/épisodes réellement lus à une révision et as_of ; une ligne source mutable ou un hash seul ne suffit pas.
- Champs : id UUID, owner_id, request_id, body_digest, source_revision, as_of, snapshot_version, snapshot_payload_json, transport_digest, consent_assessment_json et références de finalité/version quand applicables. N'inclut pas de consentement corporel par défaut.
- Contraintes : UNIQUE(owner_id,request_id), UNIQUE(owner_id,id) ; index (owner_id,source_revision). Le snapshot ne peut citer une révision d'un autre propriétaire ; vérifier origine du ledger sous verrou.
- Transaction : capture cohérente des sources et du consentement applicable ; reçu/capture committés ensemble. Même clé/corps relit la capture avant CAS ; pas de nouvelle acquisition par GET.
- Lifecycle/DATA : immutable, copie explicite à inventorier ; pas de durée choisie. Retrait invalide usage futur, ne réécrit pas la preuve.
- Rollback : lecture de snapshots existants conservée, capture désactivable.

### 3. FirstPlanEvaluation — first_plan_evaluations

- Invariant : résultat réel reproductible et ack exact récupérables après perte de réponse. Fusion de la table TimeAcknowledgment dans une nouvelle évaluation, jamais UPDATE d'une ancienne décision.
- Champs : id UUID, owner_id, snapshot_id, parent_evaluation_id nullable, operation_kind EVALUATE/TIME_ACK, request_id/body_digest, input_version/result_version, source_revision, authority_generation, request_json canonique, result_json ou erreur transport typée, trois empreintes SCI + plan_time_fingerprint, engine/policy/binding/bundle refs et digests, created_at UTC.
- L'ack est dans request_json/result_json de l'enfant TIME_ACK : acteur authentifié, date serveur, source_ref et empreintes exacts ; parent et demande propriétaire vérifiés. Pas de table d'ack ou second type SCI.
- Contraintes : UNIQUE(owner_id,operation_kind,request_id), UNIQUE(owner_id,id), FK composites (owner_id,snapshot_id) vers snapshot et (owner_id,parent_evaluation_id) vers évaluation ; index (owner_id,snapshot_id,created_at).
- Transaction : vraie exécution producteur + validateur, puis enfant/parent refs et reçu atomiques. Traitement synchrone initial : pas de faux PENDING/worker. Timeout non committé reste UNKNOWN côté transport ; NOT_SERVED n'est pas un résultat SCI inventé.
- Lifecycle/DATA : immutable, nouvelle évaluation lors de changement ; versions originales jamais effacées par revalidation. Copie des faits et de l'ack à admettre par DATA.
- Rollback : relecture historique possible sans producteur actif ; aucune nouvelle permission depuis cache ou ancien ack.

### 4. FirstSessionRequest — first_session_requests

- Invariant : identité durable du premier handoff et exclusion de doublon, même après fin/abandon. Remplace FirstSessionHandoff séparé.
- Champs : owner_id, request_id, body_digest, evaluation_id nullable avant arrivée d'un start annulé, state, session_id nullable, scientific_session_id, terminal_code, created_at/confirmed_at UTC. Corps source exact ou références suffisantes pour récupération, jamais credential.
- Contraintes : UNIQUE(owner_id,request_id) ; **index unique partiel owner_id WHERE state='CREATED'** (SQLite et PostgreSQL) ; UNIQUE(session_id) non nul ; FK composites owner/évaluation et owner/session. CHECK : CREATED exige session_id ; DENIED/CANCELLED n'en portent pas.
- Transaction : même clé/corps rend même résultat ; autre corps 409. Sous garde, rechercher tout CREATED propriétaire avant création, quelle que soit la clé. CREATED demeure CREATED après pause/fin/abandon ; pas de deuxième premier handoff. Erreur transient DB n'est pas un DENIED durable.
- Cancel crée le tombstone même avant start : même identité/digest, aucune évaluation fabriquée. Un POST tardif ne crée rien. Si CREATED a gagné, rendre ALREADY_CREATED et session existante.
- Session + exercices + séries + binding + résultat CREATED dans un commit ; index partiel dernier garde DB, pas substitut à garde des starts historiques.
- Lifecycle/DATA : état de commande et preuve résiduelle à admettre ; aucun effacement automatique. Rollback garde la relecture et le lien, sans nouvelle création.

### 5. FirstPlanExecutionBinding — first_plan_execution_bindings

- Invariant : distinguer prescription, intention et identité scientifique des faits exécutés, sans template fabriqué.
- Champs : session_id PK, owner_id, evaluation_id, execution_profile_version, scientific_session_id, immutable_payload_json (plan/session/slots/prescriptions/réalisation/appareil/côté/réglage/source/versions, mapping complet se_id/set_id), binding_digest, created_at.
- Contraintes : FK composites (session_id,owner_id) vers WorkoutSession et (owner_id,evaluation_id) ; UNIQUE(session_id,owner_id) pour descendants. Mapping vérifié contre le graphe canonique créé et à la relecture ; pas d'autorité depuis un alias String(16).
- Transaction : créé avec la séance. Marker réservé `science:v3:first-session` dans template_slug_snapshot, template_id NULL ; c'est un discriminant de profil, pas un template. Absence/corruption de binding pour ce marker => refus fermé, jamais V1/faux score.
- Lifecycle/DATA : immutable ; pas d'anonymisation UPDATE d'intention. Nouvelle copie des sources à admettre par DATA. Rollback conserve lecteur/profil et faits ; un ancien backend ne sachant pas protéger ce marker n'est pas un rollback admissible.

### 6. FirstPlanSetObservation — first_plan_set_observations

- Invariant : conserver réglage typé + identité d'opération et révision pour que le rejeu ancien ne remette pas une valeur corrigée. SetLog reste la source des reps/complétion/date courantes.
- Champs : id UUID, owner_id, session_id, session_exercise_id, set_id, op_id, body_digest, expected_revision, applied_revision, setting/context typés, receipt_json borné, recorded_at. Pas de copie d'une autre chronologie de mesures.
- Contraintes : UNIQUE(owner_id,op_id), UNIQUE(set_id,applied_revision) ; FK chaînées (session_id,owner_id) vers binding, (session_exercise_id,session_id) vers SessionExercise, (set_id,session_exercise_id) vers SetLog ; index set/revision.
- Transaction : append d'opération et mise à jour canonique SetLog ensemble ; rejouer une op existante rend son reçu, n'applique pas ses anciennes valeurs. Correction nouvelle exige la révision courante. completed_at canonique préservé selon son domaine.
- Lifecycle/DATA : append-only, pas une seconde liste de séries. Le reçu signifie APPLIED à la révision N, pas « état courant N » après correction ; relecture serveur pour courant. Rétention de ces opérations à admettre, aucune purge créant risque de rejeu.
- Rollback : journal factuel et reconciliation d'outbox restent actifs même si nouvelles créations/guidages coupés.

### 7. FirstPlanRuntimeAuthority — first_plan_runtime_authorities

- Invariant : une génération de publication/retrait connue de tous les processus et verrouillable avec un start ; fichiers/flags seuls ne ferment pas la course.
- Champs : profile_key PK, generation entier monotone, state DISABLED/ACTIVE/WITHDRAWN, engine/policy/binding/bundle/registry refs et digests, packaging_digest, approval_ref, updated_at. Aucune donnée de compte.
- Contraintes : génération CAS, refs/digests obligatoires pour ACTIVE ; absence/DISABLED => NOT_SERVED. Aucun seed ACTIVE dans migration/startup. Pas de registre scientifique parallèle : cette ligne sélectionne uniquement une publication que le vrai loader et validateur admettent.
- Transaction : start/nouvelle consigne lit et verrouille cette génération ; publication/retrait prend verrou exclusif. Ordre commun autorité puis propriétaire puis références/commande. Gestion hors activation production ; tests sur base jetable seulement avant GO distinct.
- Lifecycle : état opérationnel, historiques exacts capturés dans évaluations/bindings ; auteur/référence d'activation à fournir par release, aucune preuve d'approbation inventée. Rollback passe DISABLED pour création, garde lectures/journal.

## Indexes sur les trois tables existantes

Nouveaux indexes uniques `(id,user_id)` sur workout_sessions, `(id,session_id)` sur session_exercises, `(id,session_exercise_id)` sur set_logs. Les PK garantissent déjà cette unicité ; indexes ajoutés seulement pour permettre les FK composites d'ownership des nouvelles lignes. Aucun UPDATE/backfill d'historique ni nouvelle colonne. Déclarations metadata depuis le nouveau module, **app/models/session.py piné reste octet-identique**. Contrôle drift/snapshot doit vérifier ces indexes et les nouvelles FK sur les deux dialectes envisagés.

## Garde commune et transactions

PostgreSQL : verrou User propriétaire existant ; génération d'autorité partagée en lecture pour start et exclusive pour retrait. SQLite : vraie réservation d'écriture avant toute mutation métier ; une stratégie proposée est UPDATE no-op de `users.session_epoch` vers sa valeur inchangée, prédicat propriétaire/actif/époque, sans incrément/révocation ni changement logique d'identité. Pas de mutex mémoire ni FOR UPDATE ignoré. Si une transaction de lecture ne peut être promue, rollback de la commande entière, réponse retryable/UNKNOWN, jamais rejet définitif ni changement de clé. Tests sur connexions distinctes exigés ; username/password_hash/epoch/profil inchangés après garde.

Toute garde arrive avant la première écriture métier. Aucun helper ne rollback/committe un travail d'un autre appelant en secret. Les wrappers historiques gardent leur remplacement complet et leur commit public ; l'orchestration PLAN utilise les helpers flush-only. Epoch et DeviceSession sont relus sous la transaction ; révocation/retrait gagnant la course interdit nouveau travail. Ordre autorité (si consommée), User, DeviceSession, sources, évaluation/commande, séance/séries. Les handlers de fermeture/retrait sont coordonnés avec cet ordre.

## Migration et politiques

Alembic head lu sans connexion à une base utilisateur : z7a2u8v9x20. Révision proposée `plan_v3_20261107_01`, down_revision z7a2u8v9x20, à revalider au GO. Création des sept tables/indexes seulement ; aucune donnée historique modifiée. Pas d'application sur DB opérateur/prod. Startup legacy create_all ne doit pas appliquer ce nouveau DDL implicitement ; tests prouvent absence des sept tables avant migration explicite. Rollback applicatif coupe créations ; downgrade destructif non exécuté.

Le graphe DATA étendu doit couvrir événements/captures/évaluations/ack/reçus/bindings/observations et copies/export/backups. **Le GO BUILD peut autoriser ingénierie et bases de test synthétiques ; il ne fournit pas une politique du responsable ni une activation avec données réelles.** Durées, URL, fondements, retrait/effacement restent les décisions DATA existantes, sans nouvelle question sur les choix techniques déjà acceptés.

## Continuité source : désactivé n'est pas non migré

La forme suivante résout explicitement off → préférence modifiée → on, sans huitième table serveur :

| Installation / état | Ancien writer de préférence | Nouvelle admission |
|---|---|---|
| Non migré, flags PLAN off, aucune ligne de séance au marker SCI | comportement canonique historique, aucune requête à table PLAN absente | NOT_SERVED ; première acquisition future ne redatera pas l'héritage |
| Migré, propriétaire jamais entré dans PLAN, DATA/activation non accordées | comportement historique, pas de nouvelle copie PLAN | NOT_SERVED ; acquisition réelle future seulement sous politique |
| Migré, propriétaire avec sources/snapshots/évaluation/binding PLAN existants | **kernel d'intégrité reste actif indépendamment des flags acquisition/création** ; même transaction écrit événement minimal SOURCE_INVALIDATED, champ/cause/source réels sans recopier de valeurs non autorisées, et nouvelle révision | anciens snapshots/acks invalides même si réactivation ultérieure |
| Schéma/kernel indisponible alors que marker/historique SCI existe | ne masquer aucune rupture ; profil SCI fermé ; ancien writer ne simule pas de révision à jour | aucune ancienne évaluation réutilisable ; réparation/reconciliation explicite avant réactivation |

Avant première activation réelle, DATA doit admettre le traitement minimal d'invalidation nécessaire au lifecycle existant, y compris son sort après arrêt des acquisitions. Ce n'est pas une durée ou un fondement légal choisi par PLAN. Si cette autorisation ne subsiste pas, l'autorité passe WITHDRAWN/DISABLED pour toute nouvelle consigne ; on ne continue pas d'enregistrer des données interdites. Une réactivation après rupture exige une **nouvelle génération**, snapshots fraîchement acquis et reconfirmation des faits/qualifications dont la continuité n'est plus prouvable, jamais acceptation silencieuse du vieux cache. Une génération d'autorité seule ne rend pas des faits anciens « courants ».

Le rollback permis conserve donc le kernel et les lecteurs, même lorsque création/évaluation sont off ; revenir à un backend antérieur qui l'ignore n'est pas admissible après données SCI. Même alias/révision ne signifie pas validation inchangée si génération différente. L'installation absente et le schéma corrompu ne sont pas confondus grâce au marker canonique et à la vérification de schéma/migration.

Les writers historiques sans request_id ne reçoivent aucune fausse promesse d'idempotence : événement de mutation généré serveur, nouvelle action réelle, vieux remplacement intégral préservé. Les nouveaux endpoints ont leur clé durable et retrouvent le reçu avant CAS. Recharger réellement les lignes d'identité/DeviceSession dans la transaction, sans se fier au cache ORM résolu avant verrou ; no-op epoch ne révoque rien.

Retrait scientifique et retrait DATA sont distincts : le premier bloque nouveau guidage mais ne prive pas du journal factuel permis ; le second applique sa finalité/politique réellement admise. Si une écriture de journal n'est pas autorisée, ne pas fabriquer d'ack serveur ni purger l'outbox ; état refusé/inconnu et traitement conforme au contrat DATA. Sortie et lecture autorisées restent possibles.

## Une table native additionnelle, dans le journal propriétaire existant

Le minimum serveur est sept tables. Le client nécessite **une seule nouvelle définition SQLite**, `journal_v3_set_operations`, dans le même fichier/transaction propriétaire que le journal/outbox existants ; aucune nouvelle base globale et aucune réattribution de l'ancien journal. Total proposé : **7 tables serveur + 1 locale par partition propriétaire**.

Preuve de non-réemploi : journal.ts déclare journal_sets.weight_kg REAL NOT NULL ; domain/workout.DoneSet.weight est numérique, sync/routes envoie weight_kg. Mettre un réglage par haltère/machine dans ce champ changerait sa vérité. Utiliser seulement outbox comme journal permanent couplerait conservation des faits et purge des commandes acquittées.

- Grain : opération factuelle de série V3, immutable. Colonnes id entier local, op_id UUID unique, session_id, se_id, set_id, local_revision, expected_server_revision, setting/context/fact_json typés, performed_at/estimated, recorded_at_ms. Index (session_id,set_id,local_revision) et unicité op_id. Pas de colonne numérique « kg total » à remplir pour satisfaire l'ancien modèle.
- Une transaction locale conserve fait typé, ligne outbox existante de kind PLAN_V3_SET et snapshot actif V3. Une correction ajoute une opération, ne remplace pas une commande ancienne. Serveur arbitre sa révision ; local saved n'est pas ack serveur.
- Outbox/payload JSON et active_session/snapshot JSON existants sont réutilisés. Avant premier start, snapshot V3 conserve request_id/corps de la commande, reprise par GET ; pas de mutation rejouée automatiquement. Un ancien active_session non réconcilié ne doit pas être écrasé par cet état pré-start.
- Dispatch par ligne/profil dans une outbox mixte : anciennes opérations vont au moteur V1 inchangé, opérations V3 au routeur typé. Accusé d'une ancienne séance ne remplace pas la séance active V3. Nouveaux adapters/domain types séparés, aucun cast `as WorkoutState` V1 sur snapshot V3.
- Propriétaire/génération/retrait : resolveJournal/ownership existants restent l'autorité, aucune ouverture d'une base incertaine pour « migrer » son contenu. CREATE TABLE additif seulement dans partition prouvée ; pas ALTER/DROP/backfill de journal_sets, outbox ou ancien auren.db.
- DATA doit inclure faits locaux, commandes non envoyées/acquittées, sauvegardes et retrait. Pas de purge arbitraire ni reset global. Rollback garde table, faits et réconciliation ; ancien client incapable de V3 ne les interprète pas comme V1.

## Rencontre de calibrage — même ledger, aucune table nouvelle

Les sous-types OBSERVATION de BOOTSTRAP_INTEGRATION portent ouverture, préparation, choix, faits canoniques et retrait. Même owner/request_id/digest/révision ; un événement d’ouverture n’est pas un fait d’exercice. Lecture de rencontre recomputée à révision cohérente, actes liés à leurs preuves/références de lecture ; FirstPlanEvaluation reste réservé au plan et TIME_ACK. Graphe DATA inclut ces nouveaux sous-types, instructions/provenances/retraits et copies ; pas de durée/fondement implicite.
