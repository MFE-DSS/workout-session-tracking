# MOB-06 — contrat de lecture et départ proposé avant build

12novembre2026. GO BUILD/G1 reçu (AUTHORIZATION.json) ; montage produit non livré.
Adaptateur du
catalogue et des programmes existants, aucun nouveau moteur/table/migration serveur ; une table locale opérationnelle.

## Identité / négociation / bornes
`X-Auren-Library-Contract: owned-library/1.0.0`, requis et réémis hors401 ;406 si
absent/incompatible, no-store sur succès/erreurs. Bearer/ApiUser, owner dérivé du
serveur, preuve auth epoch/hash/device capturée et relue sous guard_owner pour
les nouveaux effets. Transports client identité et library de même backend_scope,
AuthSession.revision gardée avant/après refresh/réponse, retryUnauthorized:false
sur mutations. Aucun token/identifiant reçu du client ne choisit le propriétaire.

Configurations proposées : library_controlled_test_enabled false par défaut ;
library_backend_identity explicite immuable par banc ; library_signing_key propre
au moins32caractères, aucun repli sur hostname ou dev-secret. Sans identité/clé,
API indisponible503. Écritures sous APP_ENV=test ETflag, données exclusivement
synthétiques autorisées. Pas d'activation/deploiement dans le build.

## Endpoints fermés
- GET /me/library : section=all|programs|core|utility|specialization, zone canonique
  facultative, limit1..100(default30), cursor<=4096. Pas de query inconnue/doublée.
- GET /me/library/items/{source_ref} : détail courant de la source possédée ou
  catalogue, référence HMAC fermée et owner/backend/contrat liés. Étranger/inconnu404.
- POST /me/library/start : JSON8KiB maximum, corps exact
  {contract_version:'owned-library/1.0.0',selection_ref:<refcourante>}. Pas de clé
  request_id artificiellement présentée comme idempotence serveur inexistante.
L'état de séance ouverte est relu via la projection propriétaire déjà consommée
par Today. Aucun nouveau endpoint de succès fictif, pas d'API web par cookie.

## Lecture bornée et révision mutable
Deux limites d'index avant construction d'arbres :500gabarits visibles et
200programmes possédés dans la sélection demandée ; SQL limit(cap+1), pas de
list_drafts chargeant des arbres sans borne avant cette admission. Au plus
5000slots d'exercice examinés pour l'index/résolution de zones. Si dépassé :
413source_too_large, jamais une collection tronquée appelée COMPLETE.
Les comptes de séances/exercices/séries viennent d'agrégats serveur ou du
constructeur canonique, pas d'estimations client. Filtrage par zone réemploie le
résolveur canonique et ignore une zone hors vocabulaire comme le web ; le DTO
rend requested_zone et applied_zone, donc aucun faux « zéro résultat » implicite.

La page est construite dans une transaction de lecture cohérente. Révision opaque
= empreinte du corpus projeté d'index sous ces bornes (ordre/identités/statuts/
comptes/zones réellement affichés), liée owner/backend/schema/contrat et epoch.
Les pages suivantes recalculent cette même empreinte : source différente409
source_changed, aucun assemblage de deux révisions. Pas de snapshot persistant
ou nouveau cache canonique. Curseur HMAC à schéma fermé : owner/epoch/backend/
contract/schema/section/requested_zone/applied_zone/limit/revision/offset. L'offset
est borné au corpus, aucun SQL libre. Changement d'identité/schema/secret invalide
les jetons ;413,409,transportinconnu ne deviennent pas EMPTY.

DTO page fermé : contract_version,owner_id,read_revision,section,
requested_zone,applied_zone,groups,entries,next_cursor,collection_state.
collection_state PARTIAL si next_cursor, COMPLETE sinon ; l'absence de programme
personnel hors filtre est un état connu, pas une erreur. Chaque entrée indique
kind CATALOG_SESSION|OWNED_PROGRAM,source_ref,name,source_status,counts et zones.
Programmes composés en séances, jamais présenté comme une séance de séries
agrégées ; les champs non disponibles ont valeur null et état UNKNOWN explicite.
Les groupes/catalogue suivent leurs sections et display_order/slug ; programmes
suivent updated_at DESC puis id DESC comme départage stable ; les sections sont
programs,core,utility,specialization dans cet ordre explicite. Pas de score ni
préférence de tri inventés.

Détail borné : au plus50séances et200slots d'exercice par programme ; détail d'une
séance au plus200slots, notes au plus8192caractères chacune et réponse totale
2MiB. Au plus100rep_targets par slot et10000par détail ; comptage SQL et requêtes
bornées avant hydratation des relations, fingerprint et sérialisation. Les textes
d'identité sont bornés à1024caractères, le texte total à1MiB avant rendu. Index :
pas de chargement des rep_targets pour obtenir leurs comptes agrégés.
Dépassement explicite413, aucune perte silencieuse de texte/faits. Les
libellés conservent les sources exactes ; un nom est affichable mais ne devient
pas une identité SCI. Les références template_exercise/id/code/machine et les
min/max de prescriptions restent typés, pas des charges ou séries effectuées.

DTO détail fermé : contract_version,owner_id,read_revision,source,composition,
selection et limitations. Pour OWNED_PROGRAM, selection=null : chaque séance de
composition porte son propre source_ref,domain_launchable,native_support et
selection_ref|null. Le détail de CETTE séance se charge par son source_ref et
fournit le contrat de départ exact. Pour CATALOG_SESSION, selection désigne cette
seule séance ; jamais un programme entier ou une somme de séances. source porte kind,ids canoniques de stockage et statut ;
composition contient les séances/exercices/rep_targets prévus, sans transformer
un champ absent en0. selection contient selection_ref ou null et un motif fermé
si non démarrable ; pas de capacité scientifique déduite de cette métadonnée.
Toutes les valeurs numériques finies et IDs entiers sûrs JS sont validés ; une
source corrompue est indisponible, jamais normalisée pour produire un positif.

## Référence de sélection et départ frais
La selection_ref HMAC lie owner/backend/schema/contrat, nature catalogue ou
program/session/publication, template_id/slug et empreinte du contenu de séance
pertinent au départ. La commande ne transporte aucun poids/calibrage/ack SCI.
Le profil natif admis est legacy-strength/1.0.0 : type strength connu et au moins
une série de travail réellement exécutable. Les types cardio/zero-work-set/forme
invalide ou inconnue restent domain_launchable selon leur domaine, mais
native_support=UNSUPPORTED|UNKNOWN avec raison NATIVE_EXECUTION_UNSUPPORTED et
selection_ref=null. Le POST revalide ces conditions avant instantiate_session,
même si un ancien token avait été obtenu avant modification de la composition.
Le POST re-résout la vraie source et compare son empreinte courante ; archive,
statut/lien ou contenu changés refusent le départ. Ref fraîche n'est pas une
permission d'équipement, de force ou d'applicabilité SCI.

Sous la même transaction : garde auth/device fraîche, résolution propriétaire
et statut published nonarchived pour un programme, absence d'autre séance via
admit_legacy_start(reject_any_open=True), préflight environnement complet,
instantiate_session et matérialisation entière ou rollback. Source library est
écrite sur la séance créée, aucun programme/template n'est muté. Pas d'épisode
de recommandation sans véritable décision. Les SetLog restent incomplets et
observationsnull jusqu'aux vrais logs, jamais « terminés » par création.

Succès201 : {contract_version,owner_id,source_ref,execution_profile:'LEGACY',
execution:<vraie execution_read_model possédée>}. Décodeur strict côté client pour
ce profil et IDs, aucune donnée V3 passée au contrôleur legacy. Si le profil réel
est SCI, la reprise utilise le contrôleur V3 et ses droits actuels/ack ; aucune
nouvelle consigne n'est autorisée par cet adaptateur de bibliothèque.

Refus fermés : auth401 ; foreign_or_missing404 ; unsupported_contract406 ;
stale_selection/session_open/start_blocked409 ; acquisition_unavailable403 ;
invalid_request422 ; source_too_large413 ; storage_unavailable503. session_open
ne vaut que refus de cette nouvelle création. L'identité/profil viennent d'une
relecture fraîche de la projection propriétaire canonique déjà consommée par
Today ; reprise explicite même si l'intention refusée est déjà résolue. Échec de
cette relecture : nouveau départ toujours désactivé, vérification explicite
disponible. Ce n'est pas une permission de travail. Un status/code/écho non reconnu reste UNKNOWN côté
mutation. Une réponse de lecture ne termine jamais une intention incertaine.

Sous-types fermés à décoder sans clés supplémentaires : counts contient sessions,
exercise_slots et prescribed_sets (entiers sûrs non négatifs ou null), avec
count_state KNOWN|PARTIAL|UNKNOWN. source_status vaut AVAILABLE|DRAFT|VALIDATED|PUBLISHED ;
VALIDATED conserve l'état canonique « validé » du programme, sans publication
implicite : lecture disponible, selection_ref=null, aucun départ autorisé.
une source archivée est absente, pas silencieusement réactivée. zones est une
liste unique de clés du vocabulaire canonique. native_support contient state
SUPPORTED|UNSUPPORTED|UNKNOWN et reason null|NATIVE_EXECUTION_UNSUPPORTED.
limitations est une liste unique de codes SOURCE_CONTEXT_UNKNOWN,
PRESCRIPTION_PARTIAL,NATIVE_EXECUTION_UNSUPPORTED ; aucun texte de diagnostic
client n'est traité comme fait serveur. Un code futur inconnu refuse le DTO,
sans inventer un état vide ou une permission.

Chaque réponse de mutation décodable lie owner_id,contract_version et
request_sha256 (SHA256 du JSON canonique exact reçu). Ce digest d'écho ne constitue
aucune persistance/idempotence serveur. Un refus certain porte aussi
effect='NOT_CREATED' et code fermé, émis uniquement après absence d'effet ou
rollback confirmé. Seuls403acquisition_unavailable,404foreign_or_missing,
406unsupported_contract,409stale_selection|session_open|start_blocked,
413source_too_large et422invalid_request dans cette enveloppe exacte peuvent
résoudre l'intention comme REFUSED_CONFIRMED / creation_outcome=NOT_CREATED.
Un401,503,timeout,écho incorrect,enveloppe absente ou code inconnu conserve
SENT_UNKNOWN, même si le statut HTTP est4xx. Un refus sans écho valable n'est
jamais une preuve de non-création. session_open reste un refus de CE nouveau
départ, pas le reçu de création de la séance déjà ouverte.

## Intention locale et réconciliation sans faux reçu
Une seule nouvelle table SQLite opérationnelle library_pending_openings_v1 sur
la connexion/queue du journal possédé, pas un second fichier/history d'entraînement.
Aucune modification des schémas active_session/outbox ; le stockage n'utilise pas
saveSnapshot ni le JSON exclusif Legacy/V3.

Colonnes exactes : owner_id entier positif,backend_scope normalisé,local_id UUID,
local_version=1,source_ref,selection_ref,method='POST',path='/me/library/start',
payload_json canonique/digestSHA256 local,created_at_ms technique,state
PREPARED|SENT_UNKNOWN|RESOLVED,resolution_kind nullable
CREATED_CONFIRMED|REFUSED_CONFIRMED|RESUMED_OWNED|INTENTION_CANCELLED,creation_outcome
UNKNOWN|CONFIRMED|NOT_CREATED,session_id nullable,session_profile nullable LEGACY|PLAN_V3.
PK(owner_id,backend_scope,local_id), index unique partiel une intention non résolue
par owner/backend. local_id n'est PAS un request_id idempotent serveur. Chaque
lecture/écriture/ACK est filtré par owner/backend et garde auth/référence de
connexion, tout changement tardif étant annulé. Digest vérifié avant envoi/reprise.

Attachement via journal.ts/journalTypes.ts sur la Serial existante et un module
libraryPendingOpenings ; port web explicitement non durable, donc aucun départ
annoncé garanti sur ce port. Hydratation des intentions avant autoriser un
nouveau départ, que le snapshot courant soit Legacy ou V3 (y compris V3 achevé).
Claim/save d'un autre profil ne supprime ni ne masque l'intention. Le garde global
localOpeningState reçoit son état possédé explicite ; pas de propriété injectée
dans un snapshot qui serait écrasée lors d'un changement de profil.

Préparer → commit local → relecture exacte → SENT_UNKNOWN durable → POST une fois.
Échec local : zéro POST. Réception201 validée : beginLegacy courant et transition
existante ; seulement après sauvegarde confirmée, résoudre CREATED_CONFIRMED avec
creation_outcome=CONFIRMED et l'identité réellement renvoyée. Une panne locale
laisse l'intention non résolue, jamais un nouveau départ automatique.

Réponse perdue/401/timeout/réponse malformée : intention conservée, pas de replay
automatique. Le garde global de nouvelles actions l'inclut au même titre qu'une
intention legacy/V3 ou une fermeture en attente. A/B/backend/refresh tardifs ne
changent ni le formulaire ni le journal d'un autre propriétaire.

Après kill/reconnexion : lire la projection propriétaire courante. Une séance
ouverte est un fait pour une action explicite Reprendre ; un slug semblable ne
prouve pas la commande initiale. Ne pas libeller cette lecture « reçu exact de
création ». La résolution locale RESUMED_OWNED conserve creation_outcome=UNKNOWN
et référence la vraie séance/profil repris, sans prétendre qu'elle vient de cette
commande. Sans fait concluant, UNKNOWN persiste et l'utilisateur peut vérifier à
nouveau ou annuler explicitement l'intention locale (INTENTION_CANCELLED,
creation_outcome=UNKNOWN). Cette annulation ne supprime, ne ferme et ne certifie
aucune séance côté serveur ; ses faits restent lisibles dans Today/Progrès.

Une action humaine ultérieure de nouvelle séance est une intention fraîche,
après relecture et sous toutes les gardes, jamais le rejeu d'un request_id absent
du serveur. Aucune reprise/abandon implicite par bouton de retry. Une idempotence
serveur universelle demanderait un autre contrat, pas un succès simulé.

## Précisions d'implémentation et de revue
- Les zones projetées sont {state:MAPPED|NO_ZONES_DEFINED|ZONES_UNKNOWN,codes:[…]}.
  Le vocabulaire source est exactement ZONE_LABELS du domaine bibliothèque,
  fermé dans libraryVocabulary.json et lié par test ; ne pas substituer les
  quinze zones d'une autre taxonomie anatomique. requested_zone inconnu reste
  écho lisible et non appliqué, contrairement à un code de résultat inconnu.
- Le client compare la référence demandée et les identités root/session renvoyées
  via le payload public de la référence signée. Cette vérification de cohérence
  ne vérifie pas le HMAC et ne remplace jamais l'autorité propriétaire serveur.
- Les lectures précédentes portent leur date technique de réception en mémoire,
  conservée après échec ; ce n'est pas la date d'une observation ou une permission.
- Le prédicat de durée de vie de l'attachement SQLite est retenu en plus du
  prédicat de chaque opération, avant/après chaque attente et dans la transaction.
  Une connexion retirée ne peut plus lire, préparer, marquer ou résoudre.
- SQLite reçoit un BEGIN explicite avant les projections multi-requêtes : le
  mode historique pysqlite ne le fait pas sur SELECT. Une connexion non SQLite
  sans REPEATABLE READ/SERIALIZABLE est refusée503 ; aucune compatibilité cible
  PostgreSQL non vérifiée n'est revendiquée.
