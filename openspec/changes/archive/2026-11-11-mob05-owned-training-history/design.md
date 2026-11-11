# Design — MOB-05A / lectures natives Progress Core

**PROPOSED / NO_GO_BUILD / G1_PENDING**, base b9a334d22e6b75e9b83650eb1b2b833d4ed5d169, 10novembre2026. Réutilise le change préparé mob05-owned-training-history. L'ancien dossier a été sauvegardé ; les comparaisons/deltas legacy et leur protocole pending ne sont pas implémentés et sont retirés de cette tranche, explicitement au profit des faits bruts contextualisés.

## Context et autorités

Progrès est PendingSpace ; ConnectedApp est propriétaire unique journal/sync, ShellContext fournit today/account. /me/sessions est un bilan borné, pas un historique complet. SessionExercise conserve nom/code/position mais pas ancienne dose ni contexte équipement legacy. Le catalogue vivant ne prouve pas le passé. exercise_history.resolve_exercise utilise une identité/alias exacts ; son delta web historique reste inchangé et n'est pas repris sans contexte.

SCI : owned_binding vérifie graphe/digests ; FirstSessionV3Client.execution lit le read-model canonique typé, y compris après retrait avec observation_only/NON_EVALUABLE. Il expose des actions que le présentateur historique doit ignorer. BodyMeasurement est la seule chronologie poids ; mobile_body et WeightHistoryClient/Resource existent, respectent body_enabled/consentement, excluent User.weight_kg et poids de feedback séance. Le resource poids est headless et doit être réellement monté, pas recréé.

Manifeste conjoint produit/science, MOB00 inventory historique/exercice/progrès, visual contract et UI iteration protocol font autorité. UX-CAL-02 compact est accepté ; MISSION et exécution restent LOCKED. QA02 est un vrai APK mais ne contient pas ce nouveau code, pas une preuve de Progress livré.

## Brainstorming / Options / Risques / Choix retenu

1. Porter /progress entier : nombreux dérivés hérités et web dense, faux agrégats SCI possibles ; hors portée.
2. Créer un journal mobile autonome : doublon canonique et synchronisation ; rejeté.
3. **Proposition retenue : quatre lectures bornées + façade native compacte, poids GET existant**. Réutilise le domaine sans inventer d'analyse ; contrepartie réseau explicite, faits antérieurs étiquetés et aucun writer offline.

## D1 — Période et lecture propriétaire bornée

GET /api/mobile/v1/me/training-history?period=4w|12w|all&time_zone=<IANA>&limit=1..100 (défaut50). Bearer existant, no-store, `training-history/1.0.0`, owner serveur. until = instant serveur premier GET exclusif ; 4w = lundi00h local semaine courante moins21jours civils, 12w moins77jours ; all sans borne passée. UTC explicite et zone/bornes renvoyées, pas N×24h en traversant DST. Le client fournit la zone native explicite ; absente/invalide =>422, jamais fallback caché.

Liste triée started_at DESC,id DESC, keyset opaque signé/versionné avec owner/read_id/fenêtre/id_ceiling global au premier GET/position ; aucune offset ni table de lecture. id_ceiling est un filtre, **pas** une garantie de lifetime ou de snapshot : membership LIVE_BOUNDED_MEMBERSHIP. Suppression/restauration/réutilisation de PK peuvent changer les pages. Un entry_ref signé contient contexte de lecture + empreinte owner/session/started_at/created_at si présent/profil/noms capturés et digest binding SCI, sans faits modifiables. La référence atteste une observation de métadonnées, pas un UUID de domaine. Une restauration identique peut être indiscernable ; ne pas promettre immutabilité.

Détail : auth puis lookup owner exact avant validation du token/empreinte ; absent/étranger/ownerNULL =>même404. Référence invalide/étrangère sans fuite ; empreinte changée sur objet possédé =>409 READ_CHANGED, sélection purgée et refresh. Pas de réparation. Les continuations partagent read_context signé ; tokens de type liste/index/occurrence non interchangeables. Auth/fenêtre/sélection changées invalident les réponses tardives.

Entries : entry_ref,session_id,started_at,ended_at nullable,status/excluded réels,noms capturés,execution_profile LEGACY_V1|SCI_V3|UNKNOWN et descripteur observé. Aucun profil déduit seulement de template_id=NULL. Chargement coupé =>unknown/retry, pas EMPTY. completeness COMPLETE|MORE_AVAILABLE et next_cursor ; totaux ne viennent jamais de la première page.

## D2 — Fréquence réalisée, statut et plan

Le premier GET calcule sur toute sa fenêtre et son plafond, par requêtes bornées/groupées : recorded, completed, open, excluded et **completed_with_work** (statut completed, non excluded, au moins un SetLog kind=work réellement completed avec reps ou weight renseignés). Les comptes se recouvrent ; pas de somme décorative. Une clôture sans fait est completed mais ne compte pas comme séance réalisée. SCI compte ses faits SetLog, sans somme de charge ni score. Reps0 explicites restent un fait rapporté, pas une répétition réussie ou qualification.

Pour4w/12w, weekly_counts par semaine civile locale donne completed_with_work et partial_current_week ; [from,until) porte **started_at de la séance**, affiché « séances réalisées démarrées dans cette période ». Aucune fréquence humaine non enregistrée inférée. all renvoie le compte total, sans tableau hebdomadaire illimité ni taux moyen fabriqué. counts_read_at premier GET reste distinct de rows_read_at des pages ; les comptes sont observation à cette date, pas snapshot durable. Refresh remplace toutes pages/comptes/read_id. Si comptage indisponible : champ/status indisponible, pas0.

Plan : `planned_calendar.state=NOT_PERSISTED`, count=null ; templates/cadence courante ne créent pas des séances datées attendues. Une ligne in_progress avec séries non faites est « en cours », ses lignes semées « non réalisées » et prescription capturée SCI séparée. Ne pas titrer ces lignes « séances planifiées » ni inventer un taux d'adhérence. La cadence déclarée n'est pas requise sur la racine compacte ; détail de source facultatif seulement, jamais objectif historique.

## D3 — Détail factuel et exercice

GET /me/training-history/sessions/{session_id}?entry_ref=... : LEGACY retourne `training-session-facts/1.0.0`, noms/code/position/substitution capturés, SetLog bruts et dates/null/completed. Dose/repos/setting/context legacy = UNKNOWN_NOT_CAPTURED. Aucune lecture catalogue pour reconstruire prescription, surcharge ou score. Changement/suppression de template ne change pas ce sens. Warmups distingués des work sets ; cardio brut identifié, pas dépense inventée.

SCI : garde owner+entry_ref V1 puis409 execution_profile_required ; le client appelle le **GET V3 execution existant** via FirstSessionV3Client et compare au descripteur déjà reçu avec la liste : session/profil/started_at/binding/se_id/slot/canonical_exercise_id exacts, jamais corps d'erreur comme payload de succès. Adaptateur historique read-only additionnel valide setting MASS_KG/kg/nombre fini>=0, side BILATERAL, sémantique TOTAL_EXTERNAL/PER_IMPLEMENT/MACHINE_DISPLAY_KG, identité/context exacts de l'observation par rapport au slot, completed/reps/révision/dates offset. Setting observé peut différer du prescrit ; nul = inconnu. Mauvaise forme =>indisponible sans fallback V1. Prescrit capturé repliable, fait réellement observé lisible même sans permission de travail ; aucune commande active/history montée depuis journal mutable.

GET /me/training-history/exercises + /exercises/{exercise_ref} : index/occurrences sous même read_context/fenêtre, identité legacy par resolve_exercise exact, SCI par canonical ID et namespaces séparés. occurrence_ref ajoute se_id/position/identité/binding à entry_ref, vérifié avant détail. Le scan source est par lots200, **1000lignes inspectées maximum/GET**, limit1..100 ; curseur signe source_after et display_after distincts et type. Zéro match avec scan PARTIAL_SCAN n'est pas EMPTY ; index fusionné par exercise_ref sans comptes additionnés et coverage_complete seulement EXHAUSTED. Chaque occurrence donne référence vers faits possédés ; seul le détail choisi déclenche V3, pas N appels moteur pour dessiner une courbe.

**Comparabilité : faits juxtaposés seulement.** Aucun nouveau calcul de delta, record/1RM/progression/force/qualité/continuité SCI. Un détail SCI montre ses séries/réglages réellement observés, regroupables seulement si tuple canonique complet exact (canonical_exercise_id,intent_id,context_ref,realization_ref,equipment_ref,location si porté,side,load_semantics,kind,unit) connu et égal. Toute absence/différence =>NON_COMPARABLE/affichage séparé, jamais rapprochement de nom ou transfert. Pas de conversion affichage machine/par haltère vers total, ni comparaison des chiffres malgré unité « kg » commune. Legacy : nom résolu permet accès à l'historique de cet exercice, **pas** comparabilité d'appareil ; valeurs brutes marquées contexte non capturé, aucun delta ou courbe reliant les charges. Les reps restent faits par série datée, pas amélioration dérivée. L'ancien delta web canonique n'est ni modifié ni servi comme preuve nouvelle.

## D4 — Poids et tendance observée

Monter WeightHistoryClient + WeightHistoryResource existants, GET /me/body/weight-history paginé propriétaire et consent-scoped ; aucun nouveau backend/writer/consent implicite. Période Progress filtre les measured_at dans la fenêtre serveur D1. Pagination existante jusqu'à borne inférieure atteinte ou épuisement ; budget1000mesures par interaction, suite explicite si non épuisée. Tant qu'une page manque, couverture PARTIAL affichée, jamais « aucune mesure dans cette période » prématurément. Pas de modification du DTO historique ni de copie SQLite.

La tendance est **la chronologie des observations**, points RN/SVG datés et liste accessible correspondante ; pas lissage, droite de régression, moyenne7jours, prédiction ou avis perte/gain sain. Même measured_at peut avoir plusieurs mesures distinctes par measurement_id, sans agrégation/suppression ; dernier point tri(date,id) est affichable comme « dernière mesure », pas valeur physiologique certaine. Un seul point =>mesure isolée, pas évolution établie. `quality=KNOWN` finie/positive seule est tracée ; INVALID_NONFINITE/LEGACY_OUTSIDE_CURRENT_BOUNDS restent lisibles étiquetées et interrompent le segment, jamais remplacées par0/interpolées ou effacées. measured_at et recorded_at conservent leurs rôles ; origine/acquisition UNKNOWN restent telles quelles.

BODY flag fermé=>module « Poids indisponible », consent_required=>« Accord requis », unknown/offline≠empty. Pas d'invitation à consentir sans parcours d'acquisition approuvé : ici lecture seule et aide, pas nouveau writer/accord automatique. Aucune lecture de User.weight_kg ou WorkoutSession.bodyweight_kg. Les autres panneaux restent disponibles si poids bloqué, et inversement.

## D5 — État natif, interruption et surfaces

Un TrainingHistoryClient/Resource mémoire, un node progress dans ShellContext fourni par ConnectedApp, onglet existant ; un seul propriétaire auth/journal. Sélections par read_id+entry_ref/occurrence_ref, pas ID seul. auth.revision+séquence fenêtre/ressource/sélection invalident anciennes réponses A/B/logout ; clear mémoire au changement de compte. Refresh complet sur reconnexion explicite/foreground, pas polling ni création. Faits déjà vérifiés du même owner restent marqués « lecture précédente » ; pas de cache après relance promis. Pagination échouée ne purge pas les lignes connues et n'invente pas fin de liste.

Racine : période compacte4/12sem/Tout, fréquence factuelle courte et sessions récentes, exercice au choix avec occurrences, un poids chronologique sous aide/états brefs ; défilement natif, aucun dashboard générique. Drill-down liste→séance→exercice, retour Android revient d'un niveau puis coque. Pas de changement des quatre tabs, MISSION, calibrage, exécution ou compte. RN/SVG existant, pas dépendance nouvelle. Safe areas, grossissement/focus/AX/reducedmotion et affichages320/390 iOS/360/480 Android dans board familial. Aucun chart animé indispensable.

## Gates et coordination

Scope/board soumis au GO puis writing-plan et vrai build ; revue indépendante du read-model et du consommateur. Tests ciblés+broad seloncheck_scope ; vraie CI/visuel et pixels avant commit, baselines conservées. **Leases de composition exclusifs REL03→MOB04→MOB05A** : pas PR chevauchante, relecture du canonique après merge avant composition partagée. BODY/NUT restent préparation propre, ni écriture poids ni nutrition dans ce change. DATA, artefacts distribués et recette physique ouverts ; tests sur synthétique isolé, zéro activation/déploiement partagé implicite.

## Compacité de la liste avant rendu contrôlé

Choix technique dans la composition G1 acceptée : cinq séances récentes visibles
par défaut, lien explicite vers les autres lignes déjà reçues ; quatre semaines
récentes de la période visibles, détail des semaines à la demande. Les comptes
restent ceux de la période entière. Aucun filtre serveur, agrégat, fait, page ou
permission supprimé. Une liste de cinquante séances ou plusieurs années de blocs
hebdomadaires ne devient pas l'écran d'entrée par défaut. Nouvelle lecture/période
replie les détails ; toutes les lignes restent accessibles sans writer ni onglet.

Le nuage de poids affiche aussi les bornes numériques et dates des seuls points
réellement tracés. L'échelle vient des mesures datées affichables, pas d'un objectif,
d'une norme corporelle ou de limites de charge SCI. Sans ces repères, un petit
écart auto-échelonné pourrait sembler être une forte évolution. Aucun zéro,
interpolation, prédiction ou indicateur de réussite ajouté.


## Correctifs de la revue unique du consommateur complet

La revue a relevé cinq Important, traités dans une seule vague avec témoins
RED→GREEN. Une erreur HTTP 5xx est UNKNOWN et conserve les faits déjà confirmés
du même propriétaire. Sortir de Progrès invalide aussi la pagination poids, sans
modifier WeightHistoryClient ni poursuivre des pages en arrière-plan. Les valeurs
legacy invalides restent distinguées des absences avec leur représentation source.
Un SetLog SCI complété ou renseigné sans observation typée est incohérent, refusé.

Chaque entrée/occurrence ajoute `exercise_links` : se_id, nom capturé et référence
opaque propriétaire issue du même résolveur exact que l'index (NULL si inconnue).
Le token de lecture scelle aussi ces liens ; un changement de substitution ou de
résolution exige READ_CHANGED puis refresh. Ce n'est pas une nouvelle équivalence
de charge. Le détail propose le mouvement exact, et une occurrence met son se_id
en tête avec un repère visible. Retour conserve la hiérarchie exercice→Progrès.
Aucun changement du DTO SCI ou du SDK historique. Le contrat historique neuf,
encore non publié, reste training-history/1.0.0.

Deux mineurs sont conservés : erreur initiale de chargement d'index peu explicite
(actualisation racine disponible) et borne de période affichée à la date sans
heure. Les tests/CI ne valent pas acceptation physique, geste ou revue finale
indépendante des correctifs.
