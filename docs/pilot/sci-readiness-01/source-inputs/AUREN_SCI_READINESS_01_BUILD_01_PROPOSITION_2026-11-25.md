# AUREN — SCI-READINESS-01-BUILD-01 : proposition technique à autoriser séparément

**25 novembre2026 — fichier autonome unique, préparation uniquement.**

## Ce qui est prêt et ce qui attend

La proposition définit la future première tranche **backend propriétaire read-only**, au canonique vérifié `1f0122bf4f2d30f7c95d4975b5994d1453363bc5`. Aucun lecteur, route ou test produit n’a été implémenté.

L’avis de l’architecte recommande l’admission du contrat amendé D1–D5. Le dernier mandat fournit une formule conditionnelle à transmettre : **l’acte opérateur d’admission n’est donc pas encore enregistré**. La préparation technique ci-dessous est expressément autorisée ; son exécution ne l’est pas.

**Séquence de décisions :** admission SCI explicite et référencée → GO BUILD distinct de BUILD01 → implémentation/tests/qualification/revue/CI/merge selon gouvernance. Ne pas demander de GO de merge routinier. Le GO BUILD n’autorise ni activation de données réelles, ni modification de service QA, ni release.

## Résultat proposé de la future tranche

Un seul GET `/api/mobile/v1/me/muscle-observed-load`, négocié `muscle-observed-load/1.0.0`, owner issu du Bearer existant et no-store. Fenêtre UTC explicite sur dates canoniques des séries ; séries work/accomplies dans séances terminées/non exclues, sources et manques visibles. Quinze dimensions SCI, P07 non additif et contributions versionnées ; aucune énergie/récupération inférée.

Le résultat sépare preuve de rôles sur les faits inspectés et quantité de fenêtre EXACT/MINIMUM/UNKNOWN. Un préfixe ancien peut manquer une période récente : UNKNOWN/PARTIAL, jamais faux vide, total exhaustif ou « dernier » global. Le dernier temporellement qualifié peut resterNULL, notamment quand la source d’acquisition n’est pas attestée.

## Choix techniques proposés à examiner dans le futur GO

- Un adaptateur SQLite borné et une capture cohérente ; les lecteurs eager actuels ne sont pas modifiés ni employés comme lecteurs bornés.
- Un worker Linux Python standard isolé et jetable pour protéger le processus HTTP. Pas de dépendance ni maintenance VM ; les caps proposés restent à éprouver sur le runtime exact.
- S200/E200/W500/R1000 inchangés ; garde additionnelle G500 pour valider les graphes sans gonfler les contributions. Plafonds SQL, JSON, temps/CPU, adresse mémoire et sortie détaillés dans la section RUNTIME_LIMITS.
- Une exception explicite et unique à la garde SCI, limitée au nouvel importeur descriptif projection.py. Aucun moteur d’allocation ou MISSION ne peut consommer cette projection.
- Désactivation serveur par défaut ; activation d’un environnement réel seulement après qualification et permissions applicables.

Risques produits conservés : un historique volumineux peut ne pas fournir de fait récent dans le préfixe ; un bundle ancien absent peut laisser les associations V3 inconnues ; un nominal dépassant les caps doit resterHOLD et produire une proposition justifiée, pas une augmentation silencieuse.

## Vérifications de préparation

19tests documentairesPASS, budgetRuff259≤548, protocole/OpenSpecstrictPASS. Schéma documentaire complet et contrôlé ;112empreintes de sources vérifiées. Revue indépendante :2Important initiaux (DTO et chaîne d’autorité) corrigés et relus, aucun Critical/Important restant. Ces preuves ne sont ni des tests du futur endpoint, ni une qualification Linux/SQLite de service.

## Lecture du document

Les sections suivantes contiennent tous les éléments utiles au GO technique : fichiers/leases, design, schéma exact et invariants, chaîne d’autorité, plafonds à qualifier, tests et plan. L’acte SCI amendé est reproduit en fin de document pour garder **une seule pièce jointe**, mais reste non signé. Aucune autre pièce du dossier de travail n’est nécessaire pour examiner la proposition.

---

## BUILD_SCOPE.md

### Fichiers et changements proposés — aucun apply

Première tranche **backend uniquement**, une PR après admission et GO distincts. Développement futur au canonique frais dans un worktree isolé, en préservant le brouillon dirty0d4fcfa. Ne pas appliquer ses fichiers produit anciens comme patch. La garde de scope future devra classer le vrai diff ; prévision shared_code (mobile_api/config et garde SCI), aucune migration ni CI infra.

#### Créations produit proposées
- `app/services/muscle_observed_load/__init__.py` : package sans effet de bord.
- `app/services/muscle_observed_load/contracts.py` : paramètres, DTO stricts et erreurs publiques, aucune dépendance de writer.
- `app/services/muscle_observed_load/limits.py` : limites immuables et compteur de budgets.
- `app/services/muscle_observed_load/sqlite_source.py` : transaction propre, requêtes/bytes/ownership/graphe bornés, pas de ORM eager.
- `app/services/muscle_observed_load/provenance.py` : validation d’épisode/contexte/source, aucune réparation.
- `app/services/muscle_observed_load/projection.py` : **seul nouvel importeur direct** des sci_catalogue/sci_identity/sci_exposure existants ; fold purement descriptif/P07.
- `app/services/muscle_observed_load/worker.py` : point d’entrée isolé, OSlimits avant imports lourds ; pas app.main/DDL.
- `app/services/muscle_observed_load/supervisor.py` : slot/Popen/pipe bornés et cleanup, réponse validée.
- `app/routers/mobile_muscle_observed_load.py` : seule nouvelle route GET négociée.
- `data/sci/readiness_bodymap_projection.v1.json` : copie du mapping P07 admis avec version/digest, **pas un BodyMap SVG ni mutation de géométrie**.

#### Modifications partagées exactes proposées
- `app/routers/mobile_api.py` : import et montage du seul router, au voisinage training_history ; aucune mutation de handlers existants.
- `app/config.py` : flag `muscle_observed_load_enabled=False` et `muscle_observed_load_profile_path: str = ""` et `muscle_observed_load_profile_sha256: str = ""`, références de profil technique qualifié, absentes par défaut ; aucun secret. Pas d’activation réelle dans le code ou les réglages.
- `tests/test_sci_exposure.py` : remplacer l’interdiction absolue par exception exacte projection.py seulement, avec test rejetant tout autre consommateur ; aucune suppression de garde ni import d’allocation admis.
- `docs/strategy/Sx_SCI_V2_CATALOGUE_INTEGRATION_01_SPEC.md` : addendum descriptif borné de consommation sous admission, sans promouvoir SCI à l’allocation.
- `docs/strategy/AUREN_PRODUCT_SCIENCE_DEPENDENCIES.md` : reçu d’admission P07/consommation après décision, sans admettre P09/récupération.
- `openspec/specs/mobile/feature-migration-map/inventory.yaml` : une entrée backend GET, destination native future NON RECETTÉE ; status REWRITE_NATIVE, pas une capacité native livrée.
- `docs/strategy/SPEC_REGISTRY.md` et ce seul change : décisions/tests/reçus/closeout.
- `docs/science/sci-readiness-01/ADMISSION.md` et `docs/pilot/sci-readiness-01/` : acte reçu et preuves futures, aucun acte fictif.

Tests nouveaux exacts : `tests/test_muscle_observed_load_contract.py`, `test_muscle_observed_load_sqlite.py`, `test_muscle_observed_load_provenance.py`, `test_muscle_observed_load_projection.py`, `test_muscle_observed_load_worker.py`, `test_mobile_muscle_observed_load.py`. Aucune dépendance/conftest/app.main/database modifiée ; helpers nouveaux dans tests uniquement si nécessaires, à expliciter au diff.

#### Lectures seulement / interdictions
Pas d’édition de sci_exposure/sci_identity/sci_catalogue existants, SetLog/modèles/migrations, writers SET/FINISH, contrôle V3, recommandations/recovery, BODY/NUT ou clients/mobile. Ne pas appeler owned_binding/guard_owner ou load_ledger dans la nouvelle lecture. Pas de fix des quatre scopes historiques ; leur ordre01→04→02→03 reste recommandé, GO séparés.

Aucun écran/asset natif, palette, primitive, signature/APK/OTA, Dockerfile, workflow, service OVH, secret ou DATA. Une exigence non réalisable dans cette liste impose un scope amendé avant apply, pas un fichier partagé supplémentaire opportuniste.

#### Préflight des leases
Inventaire lu sur10worktrees AUREN existants : aucun diff observé sur mobile_api/config/importguard/inventaire au relevé ; plusieurs anciens worktrees ont des deltas de SPEC_REGISTRY.md, qui doivent être réconciliés append-only au parent réel. Aucune réservation de fichier n’est accordée par ce constat. Au GO : re-fetch, inspecter PR/branches et activité réelle, confirmer leases des deux fichiers produit partagés, de l’inventaire et des contrats/gardes ; si conflit, continuer les fichiers neufs indépendants sans PR concurrente. Aucun reset/stash/prune/force ou autre worktree modifié.

La PR future ne doit pas transporter tout le diff de préparation SCI01 ni un autre change : elle contient BUILD01, son acte d’entrée exact et son mapping admis seulement. La préparation scientifique précédente reste préservée séparément ; aucun GO de publication documentaire ou d’implémentation n’est déduit de son état local.


---

## design.md

### Design proposé — première lecture d’exposition documentée

#### Brainstorming / Options / Risques / Choix retenu pour la proposition
- Réutiliser load_ledger/owned_binding : fenêtre started_at, eager reads et corps JSON non bornés ; incompatible sans changer leurs autorités. Écarté.
- Lecteur dans le processus HTTP : simple, mais le parse et une limite mémoire dure ne sont pas isolés du serveur. Écarté pour cette proposition.
- **Choix technique proposé** : endpoint mince + worker Python standard Linux jetable, connexion sqlite3 read-only dédiée et limites avant imports/parses. Réutiliser les identités et folds purs SCI, avec adaptateurs de lecture bornés, sans appeler les writers/locks. Le subprocess de packaging est un précédent de séparation, pas une fonction à réemployer : son timeout20s/capture complète ne fournit pas ces garanties.

Le worker et ses limites sont une proposition d’architecture logicielle, pas une opération d’infrastructure ni un runtime qualifié. Pas de nouveau paquet natif/Python. Les constantes candidates ne sont pas des garanties mesurées.

#### Pipeline exact proposé
1. Route négociée : ApiUser existant, paramètres stricts, no-store, aucun owner fourni par l’appelant. Une seule requête de lecture, aucun cursor/pagination ni cache réutilisé entre captures.
2. Supervisor : slot non bloquant par processus HTTP ; chemin de worker fixe, -I sans shell ; demande interne bornée sans jeton ni mot de passe ; lecture stdout bornée et deadline. Worker lancé seulement si feature activée et profil runtime qualifié correspond au runtime réel.
3. Worker : limites OS Linux appliquées avant imports lourds, manifeste de sources immutable/pinné, puis connexion mode=ro/query_only ; BEGIN explicite avant le premier SELECT. Établir as_of serveur juste avant l’ancrage de cette capture ; revalider until<=as_of. Pas de guard_owner, app.main, init_db, journal.record_first_plan_set ou exécution d’un producteur SCI.
4. Parcours : sessions owner idASC, statut/exclusion inspectés ; exercices idASC par session ; work/completed idASC. S/E/W globaux inchangés, sentinelles non contributives. Lire les TEXT seulement après owner/IDs numériques et admission de bytes via blobopen ; aucun ORM object avec corps eager.
5. V3 : binding ET évaluation capturée, profil explicite, graphes et doses/contexte, révision courante + préfixe des reçus, digests. Ajouter un budget G500 global de lignes scalaires de graphe (y compris sets incomplets/préparatoires) nécessaire au contrôle du graphe ; il ne relève pas W500 ni la couverture. Si un graphe complet ne peut être vérifié sous G/E/W : source UNKNOWN. Gardes pertinentes de owned_binding reproduites par l’adaptateur, jamais appel eager non borné.
6. V3 : conserver catalogue effectif/source_roles/effective_roles du bundle dont l’autorité concorde exactement avec l’évaluation capturée. Vérifier les digests des sources immuables de l’artefact courant autorisé ; pas de téléchargement ni reconstruction d’un vieux bundle. Si la bonne version n’est pas disponible : UNKNOWN ; le catalogue statique courant ne remplace pas ce bundle. Un profil/binding/marker ambigu ne devient pas Legacy par défaut.
7. Legacy : substitution sinon snapshot ; résolution exacte par index SCI puis alias DB borné dans la même capture et nom canonique. Réutiliser le résolveur pur avec db=None ; l’adaptateur fournit les éventuels lookups alias par index, sans ensure_exercise. Le catalogue courant pinné est annoncé comme classification descriptive Legacy de lecture, pas comme mapping historiquement capturé.
8. Provenance : épisode d’origine et révision effective distincts ; exclure de l’appartenance datée NULL/futur/contradiction, préserver les flags originaux quand prouvés. Une date canonique Legacy exploitable peut rester PARTIAL_TIME. Les versions d’acquisition client non liées dans la DB restent UNKNOWN ; **last_qualified_observation peut rester NULL partout en V1**. Ne pas fabriquer une attestation à partir du contrat3.0.0 ou de la date de réception.
9. Fold pur sur les seules clés effectives : preuve de rôles du sous-ensemble séparée du résultat de fenêtre. Contenu incertain gardé dans disclosures, exclu des contributions certaines du minimum. P07 conserve15dimensions et posterior union, aucun crédit scalaire.
10. DTO validé et sérialisé sous plafond avant émission. Une interruption n’autorise PARTIAL qu’à une frontière de fait atomique entièrement validée, sans altérer une capture ; sinon UNAVAILABLE. Aucune émission HTTP/pipe progressive de faits non validés. Fermeture normale ou kill+wait du seul enfant.

#### Cohérence et identité
Le snapshot doit couvrir facts, owner, alias DB, binding, évaluation et reçus. Les fichiers catalogue/politiques sont immuables, bornés et vérifiés par digest avant usage. Pas de mélange avec des identités ORM du parent, ni avec une source changée en dehors de la capture. Un résultat_digest couvre toutes les sources effectivement utilisées, bornes et qualité ; aucune révision globale du journal inventée. Des requêtes successives sont des captures distinctes et ne s’additionnent pas.

#### Ressources et activation
RUNTIME_LIMITS.md est partie intégrante du scope. Runtime Linux/Python3.11.14 du Dockerfile canonique est un candidat, pas la preuve d’un déploiement actuel. Non-Linux/autre dialecte/profil manquant ->UNAVAILABLE, aucun fallback non borné. Flag serveur nouveau false par défaut, aucun réglage distant changé. Le profil qualifié inclut OS/Python/SQLite/source/pins/limites et les bornes de concurrence ; son enregistrement suit les preuves locales/CI, pas une déclaration de l’appelant.

#### Autorité et schéma complétés après revue

SOURCE_AUTHORITY.md fixe le chemin exact manifeste→v3/v2/curation/pull→binding/évaluation, avec hashing/lecture bornés et distinction des sources historiques/checkout ; aucun loader eager réemployé comme lecteur. PROPOSED_RESPONSE.schema.json fixe27objets et WIRE_CONTRACT les invariants croisés. Les deux findings de construction ont des corrections documentaires ; aucun nouveau test produit.


---

## CONTRACT_RECONCILIATION.md

### Réconciliation proposée — gate distinct, aucune permission actuelle

Le canonique interdit encore tout consommateur produit direct des modules SCI (`test_sci_exposure::test_no_product_module_consumes_the_scientific_layer`, spec SCI V2 §§7/9/16 et tableau des tranches). L’admission d’un contrat descriptif et le GO BUILD doivent porter explicitement sur **l’exception de ce seul lecteur** ; ce brouillon ne modifie pas le contrat canonique à lui seul.

Proposition d’amendement futur : autoriser uniquement `app/services/muscle_observed_load/projection.py` à importer les folds/résolveurs SCI ; garder la garde pour tous les autres modules et les moteurs, interdire tout retour de la projection dans MISSION/allocation, conserver les anciens modules et leur fenêtre started_at. Le nouveau contrat est distinct et annonce completed_at +couverture. Ne pas contourner la garde via import dynamique ou copie de politique.

Le mapping P07 est une source de projection versionnée ; aucune géométrie BodyMap modifiée, P09 non admis, aucune activation/récupération. Legacy garde sa résolution canonique ; charges historiques et identité de progression ne fusionnent pas avec identité SCI. V3 exige son bundle effectif applicable et ses sources, pas une qualification par seul identifiant.

TIME-01 et les findings de recompletion/provenance restent sources lues, jamais corrigées. La lecture déclare UNKNOWN si leur provenance manque ; aucun nouveau timestamp, UUID, writer ou replay mutation.

Le choix worker/OSlimits et la restriction initiale Linux/SQLite sont techniques à approuver dans le GO distinct, pas inclus dans la seule admission SCI. Aucun nouveau secret/dépendance ni maintenance VM. Les qualifications AS/CPU/temps/sortie, API et source restent à exécuter. DATA/release sont indépendants ; feature non activée par défaut.


---

## WIRE_CONTRACT.md

### Endpoint / DTO proposés — NOT_SERVED

#### Request
`GET /api/mobile/v1/me/muscle-observed-load?from=<instant>&until=<instant>&time_zone=UTC`

`X-Auren-Muscle-Observed-Load-Contract: muscle-observed-load/1.0.0`, Bearer existant, no-store pour toute réponse dont erreurs. from/until obligatoires, offsets explicites normalisés UTC, from<until<=as_of ; time_zone vaut seulement UTC. Queries inconnues/dupliquées, body GET et header incompatible refusés, aucune session/owner arbitraire. Pas de cursor ni autre route dans BUILD01.

401 auth existante ;406 contrat absent/incompatible ;422 requête invalide sans écho ;503 UNAVAILABLE sur désactivation/profil non qualifié/ressources non sûres/DB indisponible ;200 seulement après validation complète d’un résultat OBSERVED/PARTIAL/UNKNOWN/EMPTY. Codes courts stables, aucun SQL/chemin/secret/corps brut en erreur. Toute erreur d’autorisation garde la sémantique existante ; pas de redirection HTML.

#### Deux niveaux distincts de quantité
`evidence` garde la sémantique canonique ZoneExposure : comptes primary_sets/secondary_sets/minor_sets/unknown_sets, resolved_credit, bound et exact_evidence sur les faits inspectés admis dans ce registre. Sa portée est INSPECTED_ROLE_VECTOR ; exact_evidence ne certifie ni le temps ni l’exhaustivité. L’objet est NULL lorsqu’aucune contribution qualifiable à la zone n’existe ; pas de remplissage depuis un zéro interne.

`window_result` est une **nouvelle métadonnée proposée** : state, documented_sets, resolved_credit, bound et reasons. documented_sets = union de clés effectives certaines, datables et attribuables à cette zone dans la fenêtre canonique. Pas de somme des zones. bound EXACT seulement si toute couverture nécessaire et qualifications sont attestées ; MINIMUM seulement si une part certaine existe et des lacunes subsistent ; sinon bound et nombres NULL, state UNKNOWN/EMPTY selon preuve. Aucun conflit/CONTENT_EXECUTION_MISMATCH non résolu n’augmente le minimum. Crédit MINOR connu0 licite ; ne représente pas zéro effort.

Pour posterior : composants hamstrings/glutes séparés, union distincte certaine avec les mêmes règles de borne ; resolved_credit toujours NULL. Aucun compteur de rôle cumulé ni activation dérivée.

#### Enveloppe stricte proposée
Tous les champs sont requis, nullable là où dit ; extras interdits, nombres finis, bool≠int, max15zones, max500facts, IDs positifs63bits. Aucun float de tonnage ou score.

| Champ | Type et autorité |
|---|---|
| contract_version | literal muscle-observed-load/1.0.0, nouveau contrat |
| availability | AVAILABLE ou UNAVAILABLE, convention des lectures existantes |
| state | OBSERVED/PARTIAL/UNKNOWN/EMPTY/UNAVAILABLE, état de cette projection ; ne pas mélanger avec bound |
| owner_id/read_id/as_of | owner authentifié, UUID de lecture, date de capture UTC ; pas des dates d’effort |
| window | from/until ISO-Z, time_zone UTC, convention de history adaptée à completed_at |
| membership | LIVE_BOUNDED_MEMBERSHIP ; état courant, pas replay d’une ancienne DB |
| policy_id/catalogue_versions/mapping_version | sources réellement utilisées et digests ; aucun catalogue par défaut non attesté |
| coverage | scan COMPLETE/TRUNCATED, temporal COMPLETE/PARTIAL, mapping COMPLETE/PARTIAL, reasons ; nouveaux champs documentaires |
| scan | ordre OWNER_ID_ASC_NESTED, plafonds et nombres effectivement inspectés, branches/sources omises bornées ; pas de total global à COUNT |
| consistency | READ_TRANSACTION, source digests, result_digest ; snapshot DB + sources immuables, pas révision globale |
| zones[] | zone SCI exacte ; evidence, window_result, last_qualified_observation nullable ; exactement15dimensions conservées |
| bodymap_projection | mapping_version,11cibles et3NOT_REPRESENTED, posterior composants/union sans scalaire ; aucun nouvel asset |
| facts[] | session_id/session_exercise_id/set_log_id ; kind/completed/completed_at/reps/weight_kg ; prescribed_name/executed_name, résolution/roles/evidence_refs, contexte/setting réellement conservés et qualification temporelle ; champs absents restent NULL |
| exclusions | compteurs des motifs réellement inspectés ; branche non explorée = quantité inconnue, pas0 ; aucune identité étrangère |

Les champs source viennent de SetLog, LedgerLine, IdentityResolution, ZoneExposure, FirstPlanExecutionBinding/Evaluation/SetObservation. Les nouveaux enveloppes/coverage/window_result/consistency/scan sont explicitement proposés ; leur présence n’est pas une API existante. `observation_json`/`receipt_json` complets ne sont jamais transmis : exposer uniquement op_id, expected/applied_revision, performed_at/estimated/adjusted, recorded_at et les preuves descriptives utiles, après validation.

#### Règles de couverture et statut
- OBSERVED et bound EXACT de fenêtre : scan épuisé, sources pertinentes qualifiées, appartenance et attribution des faits à cette fenêtre prouvées selon D1 ; ne signifie pas totalité de l’entraînement réel ni heure physiologique exacte. PARTIAL_TIME d’origine suffit à garder state PARTIAL même si le décompte du journal est déterminable.
- PARTIAL : au moins une contribution certaine et une lacune de scan/temps/source ; seulement borne MINIMUM possible pour la quantité affectée. Les comptes exacts de rôles du sous-ensemble restent distincts.
- UNKNOWN : pas de part certaine, sources manquantes/troncature/non-datable ; nombres NULL. Un préfixe ancien sans fait dans la fenêtre n’est pas EMPTY.
- EMPTY : seulement domaine V1 effectivement épuisé, aucune donnée/candidat non qualifié susceptible d’affecter la fenêtre ; lecture « aucun fait documentaire admissible » et nombres externes NULL, pas zéro physiologique.
- UNAVAILABLE : impossible de produire une part sûre dans les limites, runtime non admis techniquement ou accès en échec. Aucune ancienne lecture réinjectée par le serveur.
- last_qualified_observation agrégé NULL dès couverture nécessaire incomplète, qualité d’origine non prouvée ou acquisition client non attestée. Une observation inspectée peut rester consultable par sa date sans être présentée comme dernière.

Les réglages machine/PER_IMPLEMENT restent des settings typés ; weight_kg NULL n’est pas comblé. Prescriptions/contextes ne deviennent pas exécutions. Les dates sans source ne sont jamais fabriquées.

#### Schéma exact et invariants croisés proposés

`PROPOSED_RESPONSE.schema.json` fixe tous les objets imbriqués, types, enums, champs requis/nullables et plafonds structurels. C’est une source documentaire à implémenter après GO, pas un codec produit. Les IDs DB sont des entiers positifs63bits ; IDs d’évaluation/opération/scientifiques restent textuels, jamais convertis en position. Le schéma rejette tout champ supplémentaire ; contrôle UTF8/bytes/finitude/doublons JSON en amont, validation sémantique en aval.

Invariants croisés obligatoires (tests Task1/3/5) :
1. `availability=UNAVAILABLE` impose `state=UNAVAILABLE` et seulement l’erreur publique (HTTP401/406/422/503 selon code), aucune donnée propriétaire. AVAILABLE n’accepte pas stateUNAVAILABLE.
2. Les15codes SCI et11cibles sont uniques et exactement ceux de P07 ; trois non-représentés exacts. posterior.components=[hamstrings,glutes], son crédittoujoursNULL. Un set ne compte qu’une fois dans son union.
3. window.from<until<=as_of ; dates Z ; facts retournés seulement IN_WINDOW ou appartenance UNKNOWN, les autres ne sont que motifs/counters d’exclusion. Une membershipUNKNOWN n’augmente aucun minimum/total.
4. window_result boundEXACT exige couverture nécessaire complète, nombres déterminables et aucune inconnue affectant sa quantité ; MINIMUM exige au moins un faitcertain/date/mapping cohérents de la fenêtre, jamais le seul créditinterne0. UNKNOWN/EMPTY ont quantités et boundNULL. PARTIAL_TIME sans contradiction peut laisser un décompte EXACT **du journal canonique** si son appartenance est certaine, sans qualifier l’heure d’effort ; stateglobal restePARTIAL et dernierqualifiéNULL.
5. `evidence.exact_evidence` égale sa définition canonique (`bound=EXACT && execution_uncertain_sets=0`) sur son seul vecteur inspecté. Ne pas y réinjecter une exactitude de fenêtre. evidenceNULL si aucune ligne qualifiable à cette zone.
6. Si scan/qualification nécessaire partiels, aucun last agrégé ; sinon last doit pointer un factprésent, mêmecompleted_at/zone, provenancequalifiée, mappingcertain. Source d’acquisition nonattestée ->NULL, même si estimatedfalse.
7. Toutes les clés/parents de facts sont dans la capture du mêmeowner ; aucune paire de clés+zone dupliquée ; applied_revision=expected_revision+1 lorsqu’elles existent et identitéop/context/digest concordantes. Origin/effective operations indépendantes ; absenceLegacy=NULL.
8. `scan.truncated` concorde avec coverage.scan et les sentinelles/branches ; usage ne dépasse jamais les caps. UNKNOWN ne devient pas EMPTY parce que le préfixe n’a pas trouvé de fait dans la période. EMPTY exige épuisement et aucune inconnue susceptible d’affecter la réponse.
9. Les unités/side/load_semantics sont exactement ceux de la source validée ; champ setting inconnu ne devient pas MASS_KG/TOTAL_EXTERNAL. Nombres nonfinis ou boolen guise d’ID/reps rejetés ; données hors schéma signalées dans les omissions ou UNAVAILABLE, sans clamp/réécriture de DB.
10. Chaque source_ref est canonique/logique, pas un cheminabsolu privé ; version/digest correspond à la source réellement utilisée. Pas de rawJSON, motdepasse, token, note libre ou configuration dans facts/erreurs.

Le JSONSchema ne peut pas à lui seul prouver ces invariants ni les plafonds de ressources ; tous ont des tests de service et d’API dédiés au futur build.

`scan.usage.unvisited_frontiers` compte seulement les frontières d’arrêt reconnues dans le parcours, jamais le nombre total de branches/événements omis. Ce dernier est inconnu sans scan et resteNULL dans exclusions. `fact.set_index` est l’index réel du SetLog, sans devenir une identité universelle.


---

## SOURCE_AUTHORITY.md

### Chaîne d’autorité V3 et SCI — lecture proposée, aucune exécution

`SOURCE_PINS.json` distingue les **112fichiers du checkout examinés** des hashes historiques déclarés dans les manifestes publiés. Leur présence ne qualifie pas le bundle configuré sur un serveur. Des sources historiques peuvent légitimement différer du checkout actuel : ne jamais remplacer leurs hashes par ceux d’aujourd’hui.

#### Entrées autorisées

- Chemin de bundle : configuration serveur existante `plan_v3_bundle_path`, jamais fourni par query/DTO/owner. Aucun réseau ou nouveau bundle reconstruit pour ce lecteur.
- Dans la capture SQLite : ligne `FirstPlanRuntimeAuthority` de `profile_key=first-session-runtime/3.0.0`, scalaires generation/state/packaging_digest/approval_ref et publication_json borné8KiB ; pas d’appel lock_authority (writer possible), ni execute_science.
- `packaging-manifest.v1.json` du bundle : hash doit égaler le packaging_digest attesté. Contrat attendu `plan-v3-private-science-bundle/1.0.0`. Inventaire absent = voie historique ; `plan-calibration-inventory/2.0.0` = extension explicitement validée. Autre version ou preuve absente : UNKNOWN V3.
- Ce sélecteur opérationnel ne donne ni admission SCI nouvelle ni autorité physiologique. BUILD01 conservateur : si la publication actuelle ne permet pas de prouver l’autorité capturée, signaler UNKNOWN ; ne pas supposer que generation actuelle équivaut à generation de l’évaluation.

#### Vérification bornée — ordre obligatoire

1. Propriétaire et marker **template_slug_snapshot** lus dans la même capture ; bindings/evaluation/setparents recoupés. Un marker illisible ou un profil inconnu n’est pas Legacy.
2. Lire manifeste sous cap128KiB et budget global de fichiers16MiB ; maximum128entrées. Vérifier chemins relatifs sans `..`, symlinks ou sortie de racine ; pas de `.pyc`/cache/fichier non attesté utilisé. Le budget de forme JSON reste effectif. En échec, pas d’import/load V3.
3. Vérifier par lecture bornée/stream les hashes des seules sources énumérées, somme des fichiers et identité de package ; ne pas appeler bundle_manifest dont les read_bytes ne sont pas bornés. Les sources doivent être immuables pour l’utilisateur de service et l’importeur doit vérifier tout module tools chargé contre ce manifeste ; aucune réutilisation d’un module tools venant du checkout parent. Si l’ensemble requis ne tient pas dans les caps ou ne peut être attesté : UNKNOWN, aucune augmentation automatique.
4. Racines publiées V3 : `docs/science/sci-p02-initial-policy/stage2-v3/authority/{registry.v1.json,sources.v1.json}`, hashes des constantes `REGISTRY_SHA256`/`MANIFEST_SHA256` de v3_admission. Conserver les contraintes d’admission/binding publiées sans les créer depuis l’appelant.
5. Racines v2 effectives : `calibration-time-01/{policy.v1.json,SOURCE_PINS.json}`, politique de dose `admission-01/policy.json`, `curation-01/candidates.v1.json` et `pull-exposure-01/overlay.v1.json`, avec versions et hashes publiés de leurs loaders. Base v1 : `v1/policy.json`, ses source_hashes, catalogue/schema/registry d’évidence/crédit/équipements. Le schéma quinze zones lu à l’import de sci_exposure est aussi attesté.
6. Rôles : composition **exacte** de `v2_registry._candidate_records` : source_roles=curation.roles ; effective_roles=pull.effective_roles pour candidat d’overlay, sinon curation.roles. Profils realization_ref et effective_catalogue_version calculés selon les fonctions pures de référence et leurs empreintes. Pas de rôle généré par index E1 ou titre de séance.
7. Pour inventaire2, vérifier aussi `calibration-six-extensions/authority/{registry.v1.json,sources.v1.json}`, policy.py et calibration_extension_bundle_digest du manifeste, raccord au parent V3. Cette extension ne permet pas de substituer ses profils de calibration aux rôles effectifs d’exposition.
8. Construire une vue bornée immuable des fichiers validés ; adapter la lecture aux loaders purs de référence sans réemployer leurs accès disque non bornés. Prévoir le code dans `provenance.py` pour extraire/hash les autorités et dans `projection.py` (seul importeur SCI direct) pour les folds et résolutions. Pas d’import d’evaluator ni d’appel evaluate/calibration/producer. Les petits algorithmes de composition/digest réutilisés ou reproduits exactement doivent avoir une parité explicite contre les références attestées, y compris le régime de canonicalisation JSON ; la cohérence n’est pas déclarée depuis le nom des versions.
9. Comparer cette vue au `binding.immutable_payload_json.authority` et à `evaluation.result_json` capturés : champs d’autorité `contract_version,engine_version,policy_version,binding_ref,binding_digest,bundle_digest,effective_science_digest,request_fingerprint,observation_fingerprint,full_evaluation_fingerprint,plan_time_fingerprint,start_policy_ref`. Les fingerprints d’évaluation ne sont pas des versions de catalogue : ils doivent concorder binding↔évaluation, pas avec un fingerprint générique du package. Pour le rattachement au registre, comparer binding_ref, binding_digest, bundle_digest et effective_science_digest et les versions applicables ; publication_json doit également concorder avec ses quatre PIN_FIELDS. Recouper owner/evaluation_id/authority_generation, scientific_session/dose/mapping/graphes/contexte/reçus. Au moindre maillon non prouvé : UNKNOWN, pas correction/fallback.
10. Association scientifique obtenue : canonical_exercise_id exécuté → candidate applicable → effective_roles ; garder raw_role/role_basis/evidence_refs et toutes sources/digests. Si l’adaptateur ne peut conserver une information nécessaire sans invention, cette contribution reste inconnue.

Ni current catalog static hash, ni état ACTIVE, ni seule égalité d’IDs n’attestent l’autorité de la série. Les preuves d’horloge d’acquisition restent un axe distinct : un mapping qualifié ne rend pas estimated=false ou l’heure physiques fiables.

#### Admission amendée / P07

Les hashes de l’acte amendé et du mapping candidat sont épinglés dans proposed_science_inputs de SOURCE_PINS. Ils restent PROPOSED tant que l’acte opérateur n’est pas reçu. Après décision, enregistrement exact/date/référence, sans modifier le texte pour fabriquer un accord ; au build, promouvoir seulement ce mapping admis dans le fichier data/sci/readiness_bodymap_projection.v1.json prévu, avec même contenu sémantique et version explicite. Ne pas attribuer une source canonique fictive au fichier encore local.

#### Tests de ce maillon après GO

Différence de rôle overlay/base, ancien catalogue vs binding, mauvaise publication/digest, signaturetextuelle vraie mais octets autres, graphe tronqué, évaluation étrangère, inventaire2/extensionabsente, fichiersyslink/pyc/oversize, imports depuis mauvaisroot, régimecanonisationdifférent ->UNKNOWN ou UNAVAILABLE explicite. Cas nominal de parité doit prouver les mêmes rôles/digests que le bundle de fixture canonique admissible. Ces tests sont proposés, **non exécutés** dans la préparation.


---

## RUNTIME_LIMITS.md

### Plafonds candidats à qualifier — aucune valeur mesurée de service

Ces valeurs sont des choix d’ingénierie **proposés pour BUILD01**, pas des conclusions admises ou un runtime activé. Aucun budget S/E/W/R de D4 n’est augmenté. Toute valeur changée exige un diff/une justification et de nouvelles preuves, jamais un fallback silencieux.

| Ressource | Plafond proposé | Garde / verdict attendu |
|---|---|---|
| Candidats | S200/E200/W500, R1000 globaux + sentinelles | raw IDs ASC avant qualification ; overflow ->couverture tronquée |
| Contrôle de graphe V3 | G500 lignes scalaires globales, y compris sets préparatoires/incomplets | garde additionnelle, pas des contributions ; insuffisant ->mapping/provenance UNKNOWN |
| Requêtes SQL |4096 statements maximum, y compris PRAGMA/gardes/alias/sentinelles | compteur de l’adaptateur ; aucun appel ORM eager ou COUNT global ; stop avant statement4097 |
| Instructions VM SQL |2 000 000 globales, progress callback tous1000pas | bornes discrètes ; test d’overshoot<=1000pas ; pas garantie de temps OS |
| SQL/deadline de travail |1500ms monotones depuis ouverture du lecteur, lock timeout100ms | progress handler + deadline entre lectures/blobs/parses ; timeout effectif attesté |
| CPU enfant |RLIMIT_CPU soft2s/hard3s | enfant seulement avant imports lourds ; sortie tuée/échec ->UNAVAILABLE |
| Temps supervisor |3000ms monotones depuis entrée service après auth/validation | aucun waiting queue ; kill+wait de l’enfant avant réponse ; création processus/OS cleanup peuvent dépasser : mesurer et ne pas promettre une deadline réseau absolue |
| Mémoire enfant |RLIMIT_AS soft=hard512MiB d’espace d’adressage ; RLIMIT_CORE=0 | limite OS avant imports/parses ; ne pas présenter AS comme mesure précise de RSS ou du serveur entier ; mesurer pic RSS séparément au build |
| Concurrence |1worker actif par processus HTTP, aucune file d’attente | slot occupé ->503 générique ; qualification déploiement doit consigner nombre de processus HTTP et mémoire cumulée ; pas de changement de serveur ici |
| Entrée commande interne |1KiB | owner authentifié +fenêtre +identité de lecture seulement ; pas de token/secret |
| Corps DB JSON |8KiB observation/reçu ET publication_json,128KiB binding ET évaluation,2MiB cumulés | blobopen TEXT readonly après garde owner et rowid, len avant read ; aucune projection ORM de gros TEXT |
| Autres TEXT DB |512octets par nom/identité,512octets template_slug_snapshot ; mêmes2MiB cumulés | pas de troncature silencieuse des identités ; dépassement ->source inconnue ; marker illisible ne devient pas Legacy |
| JSON non fiable |profondeur16,65536tokens par corps, chaîne4096octets, nombres finis | validation UTF8/structure avant matérialisation ; doublons de clés/NaN/Infinity/forme inattendue refusés ; pas json.loads puis contrôle seulement après allocation |
| Fichiers d’autorité immuables |128fichiers /16MiB cumulés, digest vérifié, chemins de manifeste sûrs | lecture/parse bornés, pas réseau ; bundle V3 absent/différent ->UNKNOWN ; politique fondamentale indisponible ->UNAVAILABLE |
| Sortie JSON |1MiB UTF8, max500facts/15zones, erreur publique<=1KiB | serializer et pipe comptent avant émission ; parent lit par blocs bornés, ne capture jamais stdout/stderr sans plafond ; au-delà ->UNAVAILABLE |

L’objectif n’est pas de maximiser le nombre de faits retournés, mais de servir une part prouvée sans mettre en péril l’app. Un historique volumineux peut rester PARTIAL/UNKNOWN/UNAVAILABLE. Ne pas augmenter les plafonds pour transformer un cas rouge en vert.

#### Pourquoi le worker proposé
Les garde-fous SQLite ne bornent pas seuls le parse ni la mémoire du processus HTTP. Le worker jetable permet des limites OS locales sans toucher la VM ou les dépendances. Il ne doit ni servir une requête réseau, ni écrire la DB, ni créer de fichiers de données ; connexions mode=ro/query_only et authorizer à whitelist lectures/transaction/PRAGMA nécessaires. Le parent ne change pas ses propres rlimits ; pas de preexec_fn dans le serveur multithreadé. Les signaux ne ciblent que l’enfant lancé par cette requête.

Le runtime doit prouver la présence et l’efficacité de ces contrôles. Linux/Python3.11.14 est le candidat du Dockerfile canonique ; SQLite exact et AS/CPU restent à mesurer. macOS/Windows/PostgreSQL ou capability absente : qualification HOLD, pas un test mémoire dangereux sur le Mac ni un faux PASS. Tests sémantiques à ports substitués restent séparés des tests Linux réels.

#### Profil de qualification et activation
Le futur rapport doit épingler HEAD/image, OS/Python/SQLite, versions/digests catalogue/bundle, caps, limites réelles du conteneur, nombre de processus HTTP, plans SQL, pics RSS/AS, VM/temps, taux de PARTIAL/UNAVAILABLE et cleanup. État initial NON_QUALIFIED. Activer la route dans un banc synthétique sous GO pour produire ces preuves ; usage d’un runtime réel attend la correspondance exacte au profil qualifié et ses permissions DATA/ops. Aucun flag/secret/service distant changé dans cette préparation ou par le simple merge futur.

La première qualification locale pourrait utiliser l’image QA existante reconstruite dans un banc isolé sous le futur GO ; aucun Dockerfile, pipeline, push d’image ou service QA vivant à modifier. Si les caps rendent le cas nominal indisponible, produire HOLD et un amendement borné justifié, pas prétendre un lecteur utilisable.

#### Références techniques — portée limitée
Les contrôles sont documentés dans les [API Python resource](https://docs.python.org/3.11/library/resource.html) : disponibilité et ressources varient selon la plateforme, AS/CPU sont des limites distinctes. Le [progress handler sqlite3](https://docs.python.org/3.11/library/sqlite3.html#sqlite3.Connection.set_progress_handler) permet d’interrompre le travail SQL, pas de certifier toute latence système. La [documentation subprocess](https://docs.python.org/3.11/library/subprocess.html#subprocess.Popen.kill) précise que la création du processus peut retarder l’effet d’un timeout ; borner aussi le pipe et prouver kill+wait. Ces références API ne qualifient pas notre déploiement.

Le manifeste de packaging a son cap128KiB compris dans16MiB de sources,128entrées maximum. Les empreintes/paths sont contrôlés avant imports et parsing selon SOURCE_AUTHORITY.md. Tous les petits TEXT DB participent aux2MiB DB ; les fichiers d’autorité au budget séparé16MiB. Une fermeture de l’ensemble de sources qui ne tient pas sous128entrées reste UNKNOWN V3, pas une garantie que le package actuel tiendra. Le plafond CPU inclut imports et attestation ; cas nominal à qualifier avant service.


---

## TEST_PLAN.md

### Plan RED/GREEN à exécuter après GO — aucun nouveau test produit exécuté

Les82tests de la qualification initiale et19tests documentaires du retour architecte étaient des campagnes antérieures : ne pas les réutiliser comme CI du futur lecteur. Les40cas source restent des spécifications/témoins, pas un GREEN du nouvel endpoint. Ici RED et GREEN sont des **résultats attendus**, non observés.

| Tests proposés | RED attendu avant code / GREEN futur exigé |
|---|---|
| contract::strict_request_and_nullable_states | module absent puis from/until/UTC/header, extras/dupes/body refusés ; absence reste NULL ; EXACT/MINIMUM séparés de state/availability |
| sqlite::old_id_prefix_misses_recent_window | avant lecteur : absence de réponse ; après : fenêtre récente sans lignes dans préfixe ancien ->UNKNOWN/TRUNCATED, jamais EMPTY/global last/0 |
| sqlite::global_budgets_and_sentinels | S/E/W/R/G globaux, sentinelles non comptées, aucune augmentation automatique ; row/statement/VM caps observés |
| sqlite::time_boundaries | from inclus/until exclu, session commencée avant from admissible ; NULL/futur/contradiction ne contribuent pas au minimum |
| sqlite::owner_and_read_only | deux owners+NULL, alias global lecture seule, SQL trace zéro DML/DDL même après échec ; GET ne crée ni série ni reçu |
| sqlite::snapshot_facts_receipts_and_sources | mutation concurrente atomique après première lecture : paire ancienne cohérente ; nouveau read : paire nouvelle ; pas de mapping/capture mutable mélangé |
| sqlite::text_admission_before_materialization |2MiBTEXT contre cap8KiB, row étrangère, byte total épuisé, mapping/évaluation128KiB ; aucun read/parse interdit |
| provenance::v3_authority_and_graph | mauvais owner/profil/digest/évaluation/contexte/side/setmapping, substitution, graphe tronqué G ->UNKNOWN ; pas d’appel owned_binding/guard_owner |
| provenance::effective_catalogue_missing | absent/ancienne version/overlayeffectiveroles différent : pas de fallback statique ou E1 ; source correcte exactpinned seulement |
| provenance::origin_revision_and_recomplete | correctionfalse flag, decomplete/recomplete, réceptionperdue/rejeu et révisiontrouée ; état courant unique, date contradictoire non placée ; aucun timestamp réécrit |
| provenance::legacy_estimated_adjusted | canonique datable + provenanceinconnue ->PARTIAL_TIME/lastNULL ; appareil/clientversion absente non inventée |
| projection::completed_work_and_uncertainty | vide, warmup, incomplète, séanceouverte/exclue, donnéespartielles ; aucune prescription promue en fait |
| projection::roles_and_p07 | PRIMARY/SECONDARY/MINOR/UNKNOWN, créditconventionnel inchangé, trois dimensions sans dessin, posterior union sans scalar, doublons/révisions dédupliqués |
| projection::minimum_vs_inspected_exact | exact_evidence de rôles vrai mais couverture tronquée ; quantitéfenêtre MINIMUM si contributioncertaine/datée, sinonNULL ; aucun dernieragrégé |
| projection::machine_and_context | settings MACHINE/PER_IMPLEMENT conservés, weight_kgNULL sans tonnage ni masseeffective inférée |
| worker::caps_and_cleanup | Linuxréel : CPU/AS/SQLVM/deadline/profondeur/tokens/UTF8/clésdupes/output dépassés ->réponsebornée/UNAVAILABLE, kill+wait seulchild, pas mémoire démesurée sur Mac |
| worker::concurrency_and_profile |2erequête sansqueue ->503 ; profil réel différent/manquant, OS/dialecte non qualifié, flagfalse ->UNAVAILABLE ; parentsrlimits inchangés |
| http::bearer_negotiation_inventory | cookie seul401, ownerinjectérefusé, no-store toutesréponses, un GET correctementinventorié, pas de nativeparitédéduite |
| guards::only_exact_descriptive_importer | gardeSCI rouge avec nouvelimportavant amendement, puis whitelist exactprojection.py seulement ; tout autrenouvelimportmoteur reste refusé |

Noms et assertions à développer dans les six fichiers neufs indiqués dans BUILD_SCOPE. Les campagnes futures doivent conserver nom, commande, résultat et SHA. Linux resource tests dans runtime isolé ; sur autre OS tester explicitement UNAVAILABLE, sans déclarer une qualification Linux à partir de mocks. Aucun test dangereux d’allocation sans preuve préalable d’une limite OS effective.

#### Local / CI futurs
Exécuter check_scope sur le vrai diff ; prévision shared_code : Ruff fichiers neufs/budget, protocole, tests ciblés +broad obligatoires, **pas full sweep systématique**. Broad proposé : testsSCI exposition/identité/catalogue, history, first_plan execution/persistence/runtime HTTP, mobile_api/protocol/inventaire ; affiner selon imports réels sans omettre les consommateurs. Pas pytest -n auto.

Puis sécurité Bandit/Gitleaks, revue indépendante du diff complet, CI protégée du HEAD réel (backend/mobile/visuel selon pipeline, même sans nouveau pixel) et Sonar réel consultatif. GOV-MERGE-01 seulement après admission/GO/gates satisfaits, sans bypass ; aucune demande routinière de merge. Aucune publication ni nouvelle qualification physique par ce code.

Compléments de revue : tests du schéma complet (chaque objet/extra/enum/nullabilité) et des10invariants croisés ; parité de composition des rôles v2 et digests, manifestes historiques différents du checkout, inventaire2/extension, imports étrangers et plafonds avant loader. Les nouveaux cas restent NON_EXÉCUTÉS.


---

## EXECUTION_PLAN.md

### SCI-READINESS-01-BUILD-01 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development only after recorded SCI admission and separate GO BUILD. Steps use checkbox tracking. This plan is PROPOSED, not authorization to execute.

**Goal:** One owned server read-only projection of documented muscular exposure, with honest coverage and strict runtime boundaries.
**Architecture:** thin GET adapter, bounded supervisor/isolated Linux worker, coherent SQLite source, provenance and pure role projection; existing writers/engine untouched.
**Tech Stack:** existing Python3.11.14/FastAPI/Pydantic/SQLite/SCI assets, standard library subprocess/resource, no dependency addition.
**Spec:** design.md, WIRE_CONTRACT.md, PROPOSED_RESPONSE.schema.json, SOURCE_AUTHORITY.md, RUNTIME_LIMITS.md, CONTRACT_RECONCILIATION.md and amended SCI D1–D5.

#### Global Constraints
Preparation only until admission+GO ; source1f0122bf to refresh at execution ; onechange/onePR ; all caps exact in RUNTIME_LIMITS ; no migration, native, writer, allocation, TIME01 or deployment. New consumer whitelist exact only. Default disabled.

#### Review Focus
- Old-ID prefix can omit recent facts: UNKNOWN/PARTIAL instead of misleading absence.
- Current row vs originreceipt/catalogue revision: no mixed snapshots or currentcatalogue fallback.
- Empty/raw0 vs unknown quantities: canonical evidence scope distinct from window_result.
- Resource kill/output/JSON failure: no unbounded parent capture or orphan child.
- V3 graph/typed machine uncertainty: do not turn a setting into mass or invalid mapping into Legacy.

#### Task1 — strict contract and bounds
Files: new contracts.py/limits.py and test_muscle_observed_load_contract.py.
Interfaces: proposed `parse_query(values, contract_header, *, as_of) -> ObservedLoadQuery`; immutable `ReadLimits`; `ObservedLoadReadError(code,status)`; `ObservedLoadResponse` strict DTO matching WIRE_CONTRACT. No code bodies fixed by this plan.
- [ ] Write named failing tests strict_request_and_nullable_states and unknown/EXACT/MINIMUM combinations; run module, preserve RED.
- [ ] Implement only these types, query codec and immutable limits with exact candidates.
- [ ] Run same tests to GREEN; no new route yet.

#### Task2 — coherent bounded SQLite source
Files: sqlite_source.py and test_muscle_observed_load_sqlite.py.
Interfaces: `open_owned_capture(database_url, owner_id, query, limits) -> context manager[OwnedReadCapture]`; capture exposes scalar candidates, guarded text, bounded alias/binding/evaluation/operation records and stats within the same connection. No externally supplied path.
- [ ] RED tests old_id_prefix_misses_recent_window, budgets, times, owners/read_only, snapshot, text admission.
- [ ] Implement explicit BEGIN/read-only/authorizer/progress +bounded keysets, no canonical reader mutation; G/R joins guarded.
- [ ] GREEN tests including real disposable WAL concurrency and rawbyte/VM/statement probes. No original DB write.

#### Task3 — provenance and projection
Files: provenance.py/projection.py/P07data and provenance/projection tests ; scoped spec/guard amendment only after its authority.
Interfaces: `qualify_fact(capture, candidate, sources) -> QualifiedFact`; `project_capture(capture, query, sources, limits) -> ObservedLoadResponse`. `QualifiedFact` keeps canonical IDs/context plus declared membership/source quality ; never invent a revision or time.
- [ ] RED effective catalogue/graph/episode/replay/unit/roles/partial/minimum/P07 tests from TEST_PLAN and exact importer guard.
- [ ] Amend canonical consumption addendum and guard only as explicitly admitted, implement bounded source adapter and pure fold reuse in sole importer. Existing folds/writers unchanged.
- [ ] GREEN +parity on same canonical role fixtures; no new enginerecommendations or datefix. Record source unknown cases rather than weakening tests.

#### Task4 — bounded worker and supervisor
Files: worker.py/supervisor.py and test_muscle_observed_load_worker.py.
Interfaces: fixed child entry accepts bounded internal owner/query JSON; `read_owned_muscle_observed_load(owner_id, query, *, runtime_profile) -> ObservedLoadResponse`, supervisor owns slot, read-limit, timeout, kill+wait. Child never receives Bearer token.
- [ ] RED/Linux qualification witnesses caps/cleanup, slot/profile and no parentrlimit changes; failed capability ->UNAVAILABLE.
- [ ] Implement isolation with caps before heavy imports ; no unbounded capture_output/communicate stdout, no preexec_fn.
- [ ] GREEN unit failures +actual Linux normal/adversarial cases in isolated runtime, record fingerprint/memory/time/source manifest. If nominal unavailable, HOLD rather than raise caps silently.

#### Task5 — GET integration and delivery
Files: new router ; two sharedfile deltas mobile_api/config ; canonical routeinventory ; test_mobile_muscle_observed_load.py ; scoped docs.
- [ ] Recheck parent/leases and implement RED Bearer/header/query/no-store/disabled/inventory tests.
- [ ] Add defaultfalse feature config +profile reference, mount GET only ; no endpoints/schedules/consents elsewhere.
- [ ] GREEN complete route on synthetic DB, ownerisolation and expected PARTIAL/UNKNOWN/EMPTY; zero DML assertions. Run tier’s local checks/broad/security and full independentreview.
- [ ] After all authorized gates: commit/push/PR, protected CI exactHEAD, mergecommit underGOV, canonicalCI/closeout/cleanup scope only. No sourceCI reuse; no deployment/OTA/activation.

Commits in these tasks are deferred until the whole authorized backend scope is reviewable ; do not publish a technical checkpoint as a complete feature. Current plan never authorizes these unchecked execution steps. Self-review coverage is in PREPARATION_RECEIPT, not a test result of this implementation.

Self-review après revue : Task1 couvre tous les $defs et les10invariants croisés du contrat ; Task3 couvre les10maillons d’autorité, manifeste historique et source overlay, sous lecture bornée et parité. Les nouveaux fichiers schema/authority sont documentaires dans le change ; aucun package runtime supplémentaire créé.


---

## PREPARATION_RECEIPT.md

### Reçu de préparation BUILD01 — 25 novembre2026

Canonique source1f0122bf vérifié après fetch ; préparation seulement, admission SCI et GO BUILD toujours en attente. Aucun module/route/test produit, aucun apply/commit/push/merge/UI/deploy. Worktrees et ancien contrat/paquets conservés.

Contrôles : tierISOLATED pour JSON documentaires, RuffneufN/A, budget259≤548 ; protocole et OpenSpecstrictPASS ;19tests documentaires existantsPASS (1warning dépréciation). Schéma documentaire vérifié Draft202012 :27objets,35référenceslocales et8vecteurs de forme ; ce n’est pas une qualification d’endpoint.112hashes canonique vérifiés, acte/P07 proposés épinglés, état checkout opérateur inchangé. Aucun full sweep ni CI GitHub pour qualifier un produit non implémenté.

Revue builder indépendante :0Critical/2Important initiaux, corrigés par schéma exact et chaîne V3 complète ; relecture ciblée : les2clos, aucun nouveauCritical/Important. Aucune qualification du runtime Linux, des caps ou du futurendpoint par ce verdict.

Plan relu :5tâches, interfaces/champs alignés sur schéma, cinqclasses de risques couvertes par testsnommés, aucune boucle de code produit dans le plan. La première opération reste l’admission opérateur exacte ; GO BUILD ensuite séparé. Le fichier unique de proposition rassemble scope, DTO, autorités, ressources, tests et plan pour examen.


---

## PROPOSED_RESPONSE.schema.json — documentaire, NOT_SERVED

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:auren:proposed:muscle-observed-load:1.0.0",
  "$comment": "DOCUMENTARY PROPOSED SCHEMA. NOT SERVED. Requires cross-field validation in WIRE_CONTRACT; byte/time/resource caps independent. No runtime code generated.",
  "oneOf": [{"$ref":"#/$defs/read_response"},{"$ref":"#/$defs/error_response"}],
  "$defs": {
    "reasons": {"type":"array","maxItems":28,"items":{"type":"string","enum":["SCAN_TRUNCATED","GRAPH_TRUNCATED","RECEIPT_CHAIN_TRUNCATED","NULL_EVENT_TIME","INVALID_EVENT_TIME","FUTURE_EVENT_TIME","CONTRADICTORY_EPISODE","ESTIMATED_ORIGIN","ADJUSTED_ORIGIN","UNKNOWN_ACQUISITION_SOURCE","UNKNOWN_IDENTITY","UNKNOWN_ROLE","EFFECTIVE_CATALOGUE_UNAVAILABLE","SOURCE_DIGEST_MISMATCH","PROFILE_MISMATCH","CONTENT_EXECUTION_MISMATCH","TEXT_LIMIT","JSON_LIMIT","SQL_LIMIT","TIME_LIMIT","MEMORY_LIMIT","OUTPUT_LIMIT","COMPOSITE_NO_CREDIT_AGGREGATION","NOT_REPRESENTED","OUTSIDE_WINDOW","SESSION_NOT_ELIGIBLE","LEGACY_PROVENANCE_NOT_PERSISTED","NO_DOCUMENTED_FACTS"]},"uniqueItems":true},
    "key": {"type":"object","additionalProperties":false,"required":["session_id","session_exercise_id","set_log_id"],"properties":{"session_id":{"type":"integer","minimum":1,"maximum":9223372036854775807},"session_exercise_id":{"type":"integer","minimum":1,"maximum":9223372036854775807},"set_log_id":{"type":"integer","minimum":1,"maximum":9223372036854775807}}},
    "window": {"type":"object","additionalProperties":false,"required":["from","until","time_zone"],"properties":{"from":{"type":"string","format":"date-time","pattern":"Z$","maxLength":40},"until":{"type":"string","format":"date-time","pattern":"Z$","maxLength":40},"time_zone":{"const":"UTC"}}},
    "evidence": {"type":"object","additionalProperties":false,"required":["primary_sets","secondary_sets","minor_sets","unknown_sets","unknown_identity_sets","execution_uncertain_sets","resolved_credit","bound","policy_id","exact_evidence","scope"],"properties":{"primary_sets":{"type":"integer","minimum":0,"maximum":500},"secondary_sets":{"type":"integer","minimum":0,"maximum":500},"minor_sets":{"type":"integer","minimum":0,"maximum":500},"unknown_sets":{"type":"integer","minimum":0,"maximum":500},"unknown_identity_sets":{"type":"integer","minimum":0,"maximum":500},"execution_uncertain_sets":{"type":"integer","minimum":0,"maximum":500},"resolved_credit":{"type":"number","minimum":0},"bound":{"type":"string","enum":["EXACT","MINIMUM"]},"policy_id":{"const":"sci-exposure-credit-v1"},"exact_evidence":{"type":"boolean"},"scope":{"const":"INSPECTED_ROLE_VECTOR"}}},
    "quantity": {"type":"object","additionalProperties":false,"required":["state","documented_sets","resolved_credit","bound","reasons"],"properties":{"state":{"type":"string","enum":["OBSERVED","PARTIAL","UNKNOWN","EMPTY"]},"documented_sets":{"anyOf":[{"type":"integer","minimum":0,"maximum":500},{"type":"null"}]},"resolved_credit":{"anyOf":[{"type":"number","minimum":0},{"type":"null"}]},"bound":{"anyOf":[{"type":"string","enum":["EXACT","MINIMUM"]},{"type":"null"}]},"reasons":{"$ref":"#/$defs/reasons"}}},
    "last": {"type":"object","additionalProperties":false,"required":["key","completed_at","source_zone","qualification"],"properties":{"key":{"$ref":"#/$defs/key"},"completed_at":{"type":"string","format":"date-time","pattern":"Z$","maxLength":40},"source_zone":{"type":"string","enum":["pecs","lats","upper_back","anterior_delts","lateral_delts","rear_delts","biceps","triceps","quads","hamstrings","glutes","adductors","calves","abs","hip_flexors"]},"qualification":{"const":"DOCUMENTARY_PROVENANCE_QUALIFIED"}}},
    "zone": {"type":"object","additionalProperties":false,"required":["zone","evidence","window_result","last_qualified_observation"],"properties":{"zone":{"type":"string","enum":["pecs","lats","upper_back","anterior_delts","lateral_delts","rear_delts","biceps","triceps","quads","hamstrings","glutes","adductors","calves","abs","hip_flexors"]},"evidence":{"anyOf":[{"$ref":"#/$defs/evidence"},{"type":"null"}]},"window_result":{"$ref":"#/$defs/quantity"},"last_qualified_observation":{"anyOf":[{"$ref":"#/$defs/last"},{"type":"null"}]}}},
    "bodymap_target": {"type":"object","additionalProperties":false,"required":["bodymap_zone","components","window_result","last_qualified_observation"],"properties":{"bodymap_zone":{"type":"string","enum":["pecs","lats","upper_back","delt_lat","delt_post","biceps","triceps","quads","posterior","calves","core"]},"components":{"type":"array","maxItems":2,"items":{"type":"string","enum":["pecs","lats","upper_back","anterior_delts","lateral_delts","rear_delts","biceps","triceps","quads","hamstrings","glutes","adductors","calves","abs","hip_flexors"]},"minItems":1,"uniqueItems":true},"window_result":{"$ref":"#/$defs/quantity"},"last_qualified_observation":{"anyOf":[{"$ref":"#/$defs/last"},{"type":"null"}]}}},
    "bodymap": {"type":"object","additionalProperties":false,"required":["mapping_version","targets","not_represented"],"properties":{"mapping_version":{"const":"sci-p07-bodymap-projection/0.1.0"},"targets":{"type":"array","maxItems":11,"items":{"$ref":"#/$defs/bodymap_target"},"minItems":11},"not_represented":{"type":"array","minItems":3,"maxItems":3,"uniqueItems":true,"items":{"type":"string","enum":["anterior_delts","adductors","hip_flexors"]}}}},
    "coverage": {"type":"object","additionalProperties":false,"required":["scan","temporal","mapping","scope","reasons"],"properties":{"scan":{"type":"string","enum":["COMPLETE","TRUNCATED"]},"temporal":{"type":"string","enum":["COMPLETE","PARTIAL"]},"mapping":{"type":"string","enum":["COMPLETE","PARTIAL"]},"scope":{"const":"CURRENT_DOCUMENTED_ELIGIBLE_SUBSET_NOT_REAL_TRAINING_COMPLETENESS"},"reasons":{"$ref":"#/$defs/reasons"}}},
    "budgets": {"type":"object","additionalProperties":false,"required":["sessions","exercises","work_sets","operations","graph_rows","statements"],"properties":{"sessions":{"const":200},"exercises":{"const":200},"work_sets":{"const":500},"operations":{"const":1000},"graph_rows":{"const":500},"statements":{"const":4096}}},
    "usage": {"type":"object","additionalProperties":false,"required":["sessions","exercises","work_sets","operations","graph_rows","statements","sentinels","unvisited_frontiers","db_input_bytes"],"properties":{"sessions":{"type":"integer","minimum":0,"maximum":200},"exercises":{"type":"integer","minimum":0,"maximum":200},"work_sets":{"type":"integer","minimum":0,"maximum":500},"operations":{"type":"integer","minimum":0,"maximum":1000},"graph_rows":{"type":"integer","minimum":0,"maximum":500},"statements":{"type":"integer","minimum":0,"maximum":4096},"sentinels":{"type":"integer","minimum":0,"maximum":1801},"db_input_bytes":{"type":"integer","minimum":0,"maximum":2097152},"unvisited_frontiers":{"type":"integer","minimum":0,"maximum":901}}},
    "scan": {"type":"object","additionalProperties":false,"required":["strategy","limits","usage","truncated","reasons"],"properties":{"strategy":{"const":"OWNER_ID_ASC_NESTED"},"limits":{"$ref":"#/$defs/budgets"},"usage":{"$ref":"#/$defs/usage"},"truncated":{"type":"boolean"},"reasons":{"$ref":"#/$defs/reasons"}}},
    "pin": {"type":"object","additionalProperties":false,"required":["source_ref","sha256"],"properties":{"source_ref":{"type":"string","minLength":1,"maxLength":256},"sha256":{"type":"string","pattern":"^[0-9a-f]{64}$"}}},
    "catalogue": {"type":"object","additionalProperties":false,"required":["catalogue_version","source_kind","digest"],"properties":{"catalogue_version":{"type":"string","minLength":1,"maxLength":256},"source_kind":{"type":"string","enum":["LEGACY_PINNED_READ_CLASSIFICATION","V3_CAPTURED_EFFECTIVE_BUNDLE"]},"digest":{"type":"string","pattern":"^[0-9a-f]{64}$"}}},
    "consistency": {"type":"object","additionalProperties":false,"required":["kind","runtime_profile_digest","result_digest","source_digests"],"properties":{"kind":{"const":"READ_TRANSACTION"},"runtime_profile_digest":{"type":"string","pattern":"^[0-9a-f]{64}$"},"result_digest":{"type":"string","pattern":"^[0-9a-f]{64}$"},"source_digests":{"type":"array","maxItems":128,"items":{"$ref":"#/$defs/pin"}}}},
    "resolution": {"type":"object","additionalProperties":false,"required":["status","query","step","variant_key","scientific_identity_id","canonical_exercise_id","catalogue_version","reason"],"properties":{"status":{"type":"string","enum":["RESOLVED","UNKNOWN_IDENTITY"]},"query":{"anyOf":[{"type":"string","minLength":1,"maxLength":512},{"type":"null"}]},"step":{"anyOf":[{"type":"integer","minimum":1,"maximum":3},{"type":"null"}]},"variant_key":{"anyOf":[{"type":"string","minLength":1,"maxLength":256},{"type":"null"}]},"scientific_identity_id":{"anyOf":[{"type":"string","minLength":1,"maxLength":256},{"type":"null"}]},"canonical_exercise_id":{"anyOf":[{"type":"string","minLength":1,"maxLength":256},{"type":"null"}]},"catalogue_version":{"anyOf":[{"type":"string","minLength":1,"maxLength":256},{"type":"null"}]},"reason":{"anyOf":[{"type":"string","enum":["SCAN_TRUNCATED","GRAPH_TRUNCATED","RECEIPT_CHAIN_TRUNCATED","NULL_EVENT_TIME","INVALID_EVENT_TIME","FUTURE_EVENT_TIME","CONTRADICTORY_EPISODE","ESTIMATED_ORIGIN","ADJUSTED_ORIGIN","UNKNOWN_ACQUISITION_SOURCE","UNKNOWN_IDENTITY","UNKNOWN_ROLE","EFFECTIVE_CATALOGUE_UNAVAILABLE","SOURCE_DIGEST_MISMATCH","PROFILE_MISMATCH","CONTENT_EXECUTION_MISMATCH","TEXT_LIMIT","JSON_LIMIT","SQL_LIMIT","TIME_LIMIT","MEMORY_LIMIT","OUTPUT_LIMIT","COMPOSITE_NO_CREDIT_AGGREGATION","NOT_REPRESENTED","OUTSIDE_WINDOW","SESSION_NOT_ELIGIBLE","LEGACY_PROVENANCE_NOT_PERSISTED","NO_DOCUMENTED_FACTS"]},{"type":"null"}]}}},
    "contribution": {"type":"object","additionalProperties":false,"required":["zone","raw_role","role_basis","evidence_refs","execution_uncertain"],"properties":{"zone":{"type":"string","enum":["pecs","lats","upper_back","anterior_delts","lateral_delts","rear_delts","biceps","triceps","quads","hamstrings","glutes","adductors","calves","abs","hip_flexors"]},"raw_role":{"type":"string","enum":["PRIMARY","SECONDARY","MINOR","UNKNOWN"]},"role_basis":{"anyOf":[{"type":"string","minLength":1,"maxLength":512},{"type":"null"}]},"evidence_refs":{"type":"array","maxItems":64,"items":{"type":"string","minLength":1,"maxLength":512}},"execution_uncertain":{"type":"boolean"}}},
    "setting": {"type":"object","additionalProperties":false,"required":["kind","value","unit"],"properties":{"kind":{"type":"string","minLength":1,"maxLength":64},"value":{"type":"number"},"unit":{"type":"string","minLength":1,"maxLength":64}}},
    "context": {"type":"object","additionalProperties":false,"required":["context_ref","equipment_ref","realization_ref","side","load_semantics"],"properties":{"context_ref":{"anyOf":[{"type":"string","minLength":1,"maxLength":512},{"type":"null"}]},"equipment_ref":{"anyOf":[{"type":"string","minLength":1,"maxLength":512},{"type":"null"}]},"realization_ref":{"anyOf":[{"type":"string","minLength":1,"maxLength":512},{"type":"null"}]},"side":{"anyOf":[{"type":"string","minLength":1,"maxLength":64},{"type":"null"}]},"load_semantics":{"anyOf":[{"type":"string","minLength":1,"maxLength":64},{"type":"null"}]}}},
    "operation": {"type":"object","additionalProperties":false,"required":["op_id","expected_revision","applied_revision","body_digest","recorded_at"],"properties":{"op_id":{"anyOf":[{"type":"string","minLength":1,"maxLength":64},{"type":"null"}]},"expected_revision":{"anyOf":[{"type":"integer","minimum":0,"maximum":9223372036854775807},{"type":"null"}]},"applied_revision":{"anyOf":[{"type":"integer","minimum":0,"maximum":9223372036854775807},{"type":"null"}]},"body_digest":{"anyOf":[{"type":"string","pattern":"^[0-9a-f]{64}$"},{"type":"null"}]},"recorded_at":{"anyOf":[{"type":"string","format":"date-time","pattern":"Z$","maxLength":40},{"type":"null"}]}}},
    "temporal": {"type":"object","additionalProperties":false,"required":["membership","status","performed_at","performed_at_estimated","performed_at_adjusted","reasons"],"properties":{"membership":{"type":"string","enum":["IN_WINDOW","UNKNOWN"]},"status":{"type":"string","enum":["DOCUMENTARY_PROVENANCE_QUALIFIED","CANONICAL_DATE_PARTIAL_ORIGIN","UNKNOWN_MEMBERSHIP","FUTURE","CONTRADICTORY_EPISODE"]},"performed_at":{"anyOf":[{"type":"string","format":"date-time","pattern":"Z$","maxLength":40},{"type":"null"}]},"performed_at_estimated":{"anyOf":[{"type":"boolean"},{"type":"null"}]},"performed_at_adjusted":{"anyOf":[{"type":"boolean"},{"type":"null"}]},"reasons":{"$ref":"#/$defs/reasons"}}},
    "provenance": {"type":"object","additionalProperties":false,"required":["profile","execution_profile_version","evaluation_id","binding_digest","effective_science_digest","origin_operation","effective_operation","source_status","reasons"],"properties":{"profile":{"type":"string","enum":["LEGACY","V3","UNKNOWN"]},"execution_profile_version":{"anyOf":[{"type":"string","minLength":1,"maxLength":64},{"type":"null"}]},"evaluation_id":{"anyOf":[{"type":"string","minLength":1,"maxLength":36},{"type":"null"}]},"binding_digest":{"anyOf":[{"type":"string","pattern":"^[0-9a-f]{64}$"},{"type":"null"}]},"effective_science_digest":{"anyOf":[{"type":"string","pattern":"^[0-9a-f]{64}$"},{"type":"null"}]},"origin_operation":{"anyOf":[{"$ref":"#/$defs/operation"},{"type":"null"}]},"effective_operation":{"anyOf":[{"$ref":"#/$defs/operation"},{"type":"null"}]},"source_status":{"type":"string","enum":["QUALIFIED","UNKNOWN"]},"reasons":{"$ref":"#/$defs/reasons"}}},
    "fact": {"type":"object","additionalProperties":false,"required":["key","kind","completed","completed_at","reps","weight_kg","prescribed_name","executed_name","resolution","contributions","context","setting","temporal","provenance","set_index"],"properties":{"key":{"$ref":"#/$defs/key"},"kind":{"const":"work"},"completed":{"const":true},"completed_at":{"anyOf":[{"type":"string","format":"date-time","pattern":"Z$","maxLength":40},{"type":"null"}]},"reps":{"anyOf":[{"type":"integer","minimum":0,"maximum":2147483647},{"type":"null"}]},"weight_kg":{"anyOf":[{"type":"number","minimum":0},{"type":"null"}]},"prescribed_name":{"anyOf":[{"type":"string","minLength":1,"maxLength":512},{"type":"null"}]},"executed_name":{"anyOf":[{"type":"string","minLength":1,"maxLength":512},{"type":"null"}]},"resolution":{"$ref":"#/$defs/resolution"},"contributions":{"type":"array","maxItems":15,"items":{"$ref":"#/$defs/contribution"}},"context":{"anyOf":[{"$ref":"#/$defs/context"},{"type":"null"}]},"setting":{"anyOf":[{"$ref":"#/$defs/setting"},{"type":"null"}]},"temporal":{"$ref":"#/$defs/temporal"},"provenance":{"$ref":"#/$defs/provenance"},"set_index":{"type":"integer","minimum":1,"maximum":2147483647}}},
    "exclusion": {"type":"object","additionalProperties":false,"required":["reason","inspected_count"],"properties":{"reason":{"type":"string","enum":["SCAN_TRUNCATED","GRAPH_TRUNCATED","RECEIPT_CHAIN_TRUNCATED","NULL_EVENT_TIME","INVALID_EVENT_TIME","FUTURE_EVENT_TIME","CONTRADICTORY_EPISODE","ESTIMATED_ORIGIN","ADJUSTED_ORIGIN","UNKNOWN_ACQUISITION_SOURCE","UNKNOWN_IDENTITY","UNKNOWN_ROLE","EFFECTIVE_CATALOGUE_UNAVAILABLE","SOURCE_DIGEST_MISMATCH","PROFILE_MISMATCH","CONTENT_EXECUTION_MISMATCH","TEXT_LIMIT","JSON_LIMIT","SQL_LIMIT","TIME_LIMIT","MEMORY_LIMIT","OUTPUT_LIMIT","COMPOSITE_NO_CREDIT_AGGREGATION","NOT_REPRESENTED","OUTSIDE_WINDOW","SESSION_NOT_ELIGIBLE","LEGACY_PROVENANCE_NOT_PERSISTED","NO_DOCUMENTED_FACTS"]},"inspected_count":{"anyOf":[{"type":"integer","minimum":0,"maximum":4096},{"type":"null"}]}}},
    "read_response": {"type":"object","additionalProperties":false,"required":["contract_version","availability","state","owner_id","read_id","as_of","window","membership","policy_id","catalogue_versions","mapping_version","coverage","scan","consistency","zones","bodymap_projection","facts","exclusions"],"properties":{"contract_version":{"const":"muscle-observed-load/1.0.0"},"availability":{"const":"AVAILABLE"},"state":{"type":"string","enum":["OBSERVED","PARTIAL","UNKNOWN","EMPTY"]},"owner_id":{"type":"integer","minimum":1,"maximum":9223372036854775807},"read_id":{"type":"string","format":"uuid","maxLength":36},"as_of":{"type":"string","format":"date-time","pattern":"Z$","maxLength":40},"window":{"$ref":"#/$defs/window"},"membership":{"const":"LIVE_BOUNDED_MEMBERSHIP"},"policy_id":{"const":"sci-exposure-credit-v1"},"catalogue_versions":{"type":"array","maxItems":3,"items":{"$ref":"#/$defs/catalogue"}},"mapping_version":{"const":"sci-p07-bodymap-projection/0.1.0"},"coverage":{"$ref":"#/$defs/coverage"},"scan":{"$ref":"#/$defs/scan"},"consistency":{"$ref":"#/$defs/consistency"},"zones":{"type":"array","maxItems":15,"items":{"$ref":"#/$defs/zone"},"minItems":15},"bodymap_projection":{"$ref":"#/$defs/bodymap"},"facts":{"type":"array","maxItems":500,"items":{"$ref":"#/$defs/fact"}},"exclusions":{"type":"array","maxItems":28,"items":{"$ref":"#/$defs/exclusion"}}}},
    "error_response": {"type":"object","additionalProperties":false,"required":["contract_version","availability","state","detail"],"properties":{"contract_version":{"const":"muscle-observed-load/1.0.0"},"availability":{"const":"UNAVAILABLE"},"state":{"const":"UNAVAILABLE"},"detail":{"type":"object","additionalProperties":false,"required":["error"],"properties":{"error":{"type":"string","enum":["unauthorized","muscle_observed_load_contract_required","muscle_observed_load_contract_unsupported","invalid_muscle_observed_load_query","muscle_observed_load_unavailable"]}}}}}
  }
}
```

---

## Acte SCI amendé à confirmer — texte d’entrée conservé

### AUREN — SCI-READINESS-01 : acte d’admission amendé D1–D5

**25 novembre 2026 — UNE pièce autonome à transmettre.**

**Statut : admission recommandée par l’architecte sous amendements ; acte opérateur NON REÇU. Aucun GO BUILD, APPLY, MERGE ou RELEASE.**

Références : retour architecte transmis le25novembre ; CR unique SCI-READINESS-01 ; canonique `1f0122bf4f2d30f7c95d4975b5994d1453363bc5`, revérifié après fetch pour cette révision. La qualification antérieure est conservée. Ce document amende le contrat proposé ; il ne change aucun produit servi.

#### 1. Objet admis à la décision

Une mémoire descriptive du **travail musculaire documenté**, permettant d’explorer les séries enregistrées, leurs séances/mouvements, leurs contributions versionnées, leurs dates et leurs limites. Une série marquée accomplie est un fait enregistré, pas une preuve physique indépendante d’exécution. Aucun score d’énergie, récupération, activation physiologique, conseil ou changement d’allocation V3.

Les statuts ci-dessous décrivent **la proposition soumise**, jamais une acceptation opérateur déjà obtenue.

| Décision | Statut proposé | Contrat à admettre |
|---|---|---|
| **D1 — Faits et période** | **ACCEPT PROPOSED** | Owner serveur ; séance terminée et non exclue ; séries `work && completed`. Fenêtre UTC `[from, until)`, `until <= as_of`, fondée sur `SetLog.completed_at`. Aucun repli sur début/fin de séance ou heure de réception. Les séances ouvertes restent hors du sous-ensemble V1 annoncé. |
| **D2 — Autorité des contributions** | **ACCEPT PROPOSED sous preuve d’autorité** | Politique `sci-exposure-credit-v1` : PRIMARY1, SECONDARY0,5, MINOR0 ; UNKNOWN inconnu. Crédits conventionnels, pas physiologiques. Pour V3 : identité exécutée et rôles effectifs du catalogue/bundle applicable, version et digests attestés. Sans preuve : UNKNOWN, sans catalogue courant de repli, nom approximatif ou position E1–E7. |
| **D3 — SCI-P07** | **ACCEPT PROPOSED** | Mapping versionné `sci-p07-bodymap-projection/0.1.0` : quinze dimensions conservées, onze cibles BodyMap. Renommages lateral_delts→delt_lat, rear_delts→delt_post, abs→core. anterior_delts/adductors/hip_flexors restent accessibles hors dessin. posterior présente hamstrings et glutes séparément et l’union dédupliquée des séries : aucun crédit scalaire ni somme des compteurs de rôles. Les dix autres cibles conservent leur dimension source. BodyMap localise des données documentées. |
| **D4 — Lecture et complétude** | **AMENDED — soumis à admission** | Parcours déterministe, inspection bornée et couverture explicitement distincte de la fenêtre ; règles détaillées ci-dessous. Les limites n’assurent aucune représentativité temporelle. |
| **D5 — Provenance temporelle** | **ACCEPT PROPOSED** | Distinguer date canonique, observation d’origine, révision effective, reçu et heure de lecture. Une date de journal exploitable peut rester PARTIAL_TIME, avec dernier qualifié NULL. Le dernier flag estimated=false ne reconstitue pas l’origine. Une heure réemployée de décompletion/recompletion n’est pas une nouvelle heure d’effort. Aucun ancien timestamp réécrit. |

#### 2. D4 amendé — six règles contractuelles

**1 — Ordre et récence.** Parcours imbriqué par IDs croissants : séances propriétaires, exercices de chaque séance, puis séries de travail accomplies ; opérations V3 par révision croissante. Budgets globaux proposés S200/E200/W500/R1000, avec sentinelles non contributives. Ce préfixe peut privilégier des séances anciennes et manquer les événements récents demandés. Un ID n’est pas une date. Aucun tri récent, échantillon représentatif ou exhaustivité implicite. Pas d’augmentation arbitraire des budgets.

**2 — Trois périmètres.** Séparer : **fenêtre demandée**, **sous-ensemble effectivement inspecté** et **couverture complète attestée**. Cette dernière exige l’épuisement des branches nécessaires et la qualification des sources nécessaires à chaque affirmation. Un scan épuisé ne résout pas automatiquement les dates ou mappings inconnus ; il ne prouve jamais la complétude de l’historique réel de l’athlète.

**3 — Candidats non qualifiables.** NULL, date illisible, futur à as_of ou épisode temporel contradictoire : pas de contribution à un total daté ni à sa borne minimale ; omission et cause explicites. Une branche tronquée reste inexplorée, jamais vide. Identité/rôle/source non prouvés : UNKNOWN. Une date canonique utilisable avec provenance estimée/inconnue reste présentable comme date du journal sous PARTIAL_TIME selon D5, sans certification physique ; cette tolérance ne couvre pas un épisode contradictoire.

**4 — Bornes et dernières observations.** MINIMUM ne contient que des contributions certaines, datables et attribuables à la fenêtre selon l’horloge canonique déclarée, dédupliquées dans la même capture. Sans part certaine : NULL/UNKNOWN. Le crédit0 d’une contribution MINOR connue ne signifie pas absence de travail. Si une couverture nécessaire manque : aucun total exhaustif, aucune absence de travail, aucun dernier événement agrégé prétendument exhaustif ; `last_qualified_observation = NULL`. Un fait inspecté reste consultable individuellement sans être présenté comme « le dernier ». Même avec parcours épuisé, une inconnue susceptible de modifier le résultat empêche sa certification.

**5 — Capture et ressources.** Même capture cohérente pour faits effectifs, owner/graphes, révisions, observations/reçus, bindings et sources/politiques applicables. SQLite : lecteur neuf, transaction explicite avant première lecture, aucun cache périmé ; sources externes immuables épinglées par digest. Caps d’entrée proposés inchangés :8KiB par observation/reçu,128KiB par binding,2MiB cumulés avant parse. Ils ne bornent pas à eux seuls mémoire des objets, CPU ou sortie. Plafonds explicites et éprouvés de forme/profondeur JSON, temps SQL/total, mémoire et sortie sérialisée sont obligatoires avant service. **Leurs valeurs et l’intégration de déploiement restent à qualifier : runtime HOLD jusque-là.**

**6 — Échec fermé.** PARTIAL seulement si la part publiée reste certaine, cohérente et dans tous les plafonds ; sinon UNAVAILABLE. Aucun parse incomplet utilisé comme preuve. PostgreSQL, autre runtime ou stratégie non qualifiée restent HOLD. Une fenêtre trop grande peut légitimement demeurer PARTIAL ou UNAVAILABLE.

#### 3. Trois invariants non négociables

- **Temporalité :** événement non datable ≠ contribution à un total certifié d’une fenêtre ; inconnue ≠ absence d’entraînement.
- **Complétude :** `exact_evidence` qualifie les rôles/crédits du sous-ensemble, pas l’historique complet ni la provenance exacte de l’heure.
- **Autorité :** catalogue actuel de repli, géométrie anatomique ou correction locale non relue ne remplacent jamais l’identité effective et sa source qualifiée.

#### 4. Première implémentation proposée — sans autorisation actuelle

Après admission SCI seulement, préparer un **GO BUILD propre pour la projection serveur read-only et son transport strict**, sur le runtime SQLite qualifié. Inclure owner, faits effectifs Legacy/V3, rôles/politiques, P07, fenêtre, détails de sources, capture et limites/UNKNOWN/PARTIAL. Une source V3 non prouvable reste UNKNOWN. Forme finale de route/DTO, inventaire, fichiers et leases à fixer dans ce futur paquet.

Pas de nouveau writer, migration/index opportuniste, moteur de récupération, modification de classement, auth, TIME-01, SQLite de reprise ou journal historique. Pas d’UI dans cette première tranche proposée. L’instrument natif viendra avec scope/GO explicites ; G1 artistique DA-READINESS-01 conservé et gate des vrais pixels maintenu.

Le lecteur ne sera servi qu’après qualification du runtime exact, des limites et des invariants, tests ciblés/broad, revue et CI applicables. Les40cas documentaires et les expériences isolées antérieures **ne sont pas un GREEN du futur endpoint**. Ajouter notamment les témoins préfixe ancien/manque récent, branche tronquée, rôles exacts/couverture incomplète, borne minimale et dépassements de ressources. Aucun de ces nouveaux tests produit n’a été exécuté dans cette révision documentaire.

#### 5. Risques résiduels et correctifs séparés

Chaînes de reçus/catalogues manquants, dates Legacy peu qualifiées et réemploi V3 peuvent maintenir des résultats UNKNOWN ou un dernier qualifié NULL. Les mesures SQL/snapshot/transport isolées ne certifient ni ORM complet, ni mémoire RSS, ni latence réelle, ni PostgreSQL. Ces limites ne sont pas contournées par l’admission du contrat.

Ordre architecte proposé, **aucun GO BUILD reçu pour ces correctifs** :

1. **hist-01 coverage-explanation** : ne plus dire « déjà bien servi » sans base de comparaison ; prouver l’invariance des classements, candidats et gagnants.
2. **hist-04 provenance-language** : corriger les consommateurs restants, garder le wire hérité ; ne pas rouvrir MISSION déjà corrigé.
3. **hist-02 recorded-strength-evidence** : distinguer exercice planifié et série enregistrée, après admission de l’effet sur les entrées de récupération/allocation ; expliquer les divergences.
4. **hist-03 template-recency** : maximum de récence par slug, après admission séparée des effets sur rang, alternatives et gagnant.

L’ordre3/4 peut dépendre des leases ; aucun regroupement opportuniste. Les findings temporels V3 restent autonomes ; aucune réattribution de l’ancien incident TIME-01.

#### 6. Acte opérateur — à recevoir

**Verdict actuel : HOLD_SIGNATURE_OPÉRATEUR.** D1/D2/D3/D5 restent ACCEPT PROPOSED ; D4 est AMENDED ; runtime de déploiement et PostgreSQL restent HOLD de qualification.

Décision possible à enregistrer : **« J’admets le contrat descriptif SCI-READINESS-01 amendé D1–D5 du25novembre2026, y compris les six règles D4. Cette admission ne vaut pas GO BUILD, APPLY, MERGE, DATA ou RELEASE. »**

Alternative : préciser les amendements demandés et maintenir HOLD. Référence/date de l’acte : **non renseignées**. L’architecte a recommandé l’admission ; aucune signature opérateur n’est déduite de son retour ou de l’envoi de ce document.

PILOT-01/DATA, QA, TIME-01, APK/OTA et acceptation physique gardent leurs décisions indépendantes.


---

## Références de code et traçabilité

La trace complète est conservée sous SOURCE_PINS.json dans le change préparatoire. Ces quelques liens suffisent à retrouver les autorités au SHA examiné ; les hashes du checkout ne remplacent pas les octets d’un bundle historique.

- [app/services/plan_v3/execution.py](https://github.com/MFE-DSS/workout-session-tracking/blob/1f0122bf4f2d30f7c95d4975b5994d1453363bc5/app/services/plan_v3/execution.py) — SHA256 `0f5ce3ef1dbc843aaa01d2495a0c7eb350c629b1d8991e6c60292b24ee9cbb85`.
- [app/services/plan_v3/authority.py](https://github.com/MFE-DSS/workout-session-tracking/blob/1f0122bf4f2d30f7c95d4975b5994d1453363bc5/app/services/plan_v3/authority.py) — SHA256 `53dae42821eff6e9c28e6053c8c46a35d5a0d50632a42408df0bc847bf0de157`.
- [app/services/plan_v3/packaging.py](https://github.com/MFE-DSS/workout-session-tracking/blob/1f0122bf4f2d30f7c95d4975b5994d1453363bc5/app/services/plan_v3/packaging.py) — SHA256 `e84e19ca9188e0a9bd14b82bcb93a524f928aab2b66dde47a1461126caf15731`.
- [tools/science_initial_policy/v2_registry.py](https://github.com/MFE-DSS/workout-session-tracking/blob/1f0122bf4f2d30f7c95d4975b5994d1453363bc5/tools/science_initial_policy/v2_registry.py) — SHA256 `5f9d17f531f28cda18595d0aace9fc8b91340e931bc77d4dedac170cc05ac59b`.
- [tools/science_initial_policy/v3_admission.py](https://github.com/MFE-DSS/workout-session-tracking/blob/1f0122bf4f2d30f7c95d4975b5994d1453363bc5/tools/science_initial_policy/v3_admission.py) — SHA256 `57e1a3e8b5aec960192e6886db9256b568a1ee776503d7daefddd077f9864b83`.
- [tools/science_initial_policy/curation.py](https://github.com/MFE-DSS/workout-session-tracking/blob/1f0122bf4f2d30f7c95d4975b5994d1453363bc5/tools/science_initial_policy/curation.py) — SHA256 `341ba18ac6adeb178b0c0cf90d5a69a1783a77521f7ca24df4a6c1a0093453a5`.
- [tools/science_initial_policy/pull_exposure.py](https://github.com/MFE-DSS/workout-session-tracking/blob/1f0122bf4f2d30f7c95d4975b5994d1453363bc5/tools/science_initial_policy/pull_exposure.py) — SHA256 `5999e3eaf188601e7d115a8c0a9616dbfce0a6711d03e3d19fa565a9f835c5a9`.
- [tools/science_calibration_extension/policy.py](https://github.com/MFE-DSS/workout-session-tracking/blob/1f0122bf4f2d30f7c95d4975b5994d1453363bc5/tools/science_calibration_extension/policy.py) — SHA256 `22f8e6c83a06c851573ee8df106c5fa4e860be5d3d054521ea342e1993ccde5f`.
- [data/sci/exercise_catalogue.schema.json](https://github.com/MFE-DSS/workout-session-tracking/blob/1f0122bf4f2d30f7c95d4975b5994d1453363bc5/data/sci/exercise_catalogue.schema.json) — SHA256 `17d6fef7163cc5d0c9f185d5fa989a9f99cd8491ca01abfa1a9d83f3bcb4fe77`.
- [tests/test_sci_exposure.py](https://github.com/MFE-DSS/workout-session-tracking/blob/1f0122bf4f2d30f7c95d4975b5994d1453363bc5/tests/test_sci_exposure.py) — SHA256 `ba5ffa32d84eeaff24d8e7d07210a3ad919d0fd0c3f30274fb06d475bed4556f`.


---
