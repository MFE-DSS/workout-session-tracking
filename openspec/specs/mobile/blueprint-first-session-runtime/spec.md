# mobile/blueprint-first-session-runtime Specification

## Purpose
Relier un snapshot Blueprint propriétaire au producteur scientifique V3 admis,
à une commande de première séance idempotente et au journal natif canonique
typé. Le périmètre contrôlé prouve cette chaîne sur données synthétiques dans
une application native isolée ; la politique DATA, l'activation réelle, le
déploiement et les recettes physiques conservent leurs gates distinctes.

## Requirements

### Requirement: Preparation is not implementation authority
Le change SHALL rester PREPARATION_ONLY sans GO BUILD PLAN. Il SHALL préserver les critères PLAN-01..07 ouverts et SHALL NOT servir un moteur, une API, une fixture READY ou une séance depuis ses documents.
#### Scenario: Scientific isolated build is approved
- WHEN un GO autorise le producteur SCI isolé séparé
- THEN aucune application PLAN ni autorisation de collecte/runtime/déploiement n’est déduite.

### Requirement: Owned canonical sources with honest absence and provenance
Le serveur SHALL construire les faits propriétaires depuis leurs sources canoniques, conserver UNKNOWN/WITHHELD/CONFLICT/KNOWN et les provenances réelles, et distinguer [] déclaré de l’absence. Il SHALL NOT fabriquer Blueprint depuis préférences locales ou promouvoir date de lecture en acquisition.
#### Scenario: Only training cadence is known
- WHEN la cadence est déclarée et budgets/limitations ne sont pas connus
- THEN le contrat canonique rapporte les manques utiles, sans exiger poids/taille/expérience/inventaire ou déduire des limitations vides.
#### Scenario: Legacy writer runs after capture
- WHEN une préférence canonique pertinente change après capture
- THEN source_revision invalide l’évaluation précédente atomiquement sans effacer les faits hors scope de ce writer.

### Requirement: Coherent immutable snapshots and relevant consent
Un snapshot SHALL être propriétaire, cohérent, immuable, versionné avec as_of/source_revision et empreintes canoniques reproductibles. L’assessment de consentement pertinent SHALL venir du contrat DATA, séparément du DTO SCI ; aucun consentement corporel global SHALL être exigé lorsque ce binding ne consomme pas ces données.
#### Scenario: Foreign snapshot is requested
- WHEN un compte demande le snapshot d’un autre compte
- THEN il reçoit le même404 qu’une identité absente, sans fuite de faits.
#### Scenario: Consent authority is unavailable
- WHEN le consentement réellement pertinent ne peut être vérifié
- THEN l’applicabilité reste inconnue/bloquée, jamais un consentement satisfait inventé.

### Requirement: Explicit V3 authority and legacy compatibility
Le runtime SHALL négocier explicitement les versions V3 et le profil admis, appeler le vrai producteur puis le validateur canonique du binding admis, vérifier propriétaire/pins/empreintes et préserver les modèles/validateurs historiques et le SDK scientifique V1 inchangés. Un schéma/label/fixture SHALL NOT faire autorité.
#### Scenario: V3 reaches the pinned V1 consumer
- WHEN une réponse V3 arrive au port V1 ou une version inconnue est demandée
- THEN aucun downgrade/READY V1 n’est fabriqué et la négociation échoue explicitement.
#### Scenario: Missing producer or invalid authority
- WHEN le producteur manque ou un registre/binding/source/pin est absent/retiré/altéré
- THEN le runtime rend absence/indisponibilité/refus fermé, sans fallback historique.

### Requirement: Limited observed admission without assumed inventory
PLAN SHALL consommer uniquement le périmètre effectivement admis par SCI ; le premier positif limité exige adulte déclaré non clinique, hypertrophie, deux séances, limitations connues vides et sept réglages bilatéraux exacts actuels observés/qualifiés/acceptés. Bootstrap SHALL rester hors positif ; l’inventaire global inconnu SHALL NOT devenir full gym ou prérequis d’inventaire.
#### Scenario: Equipment is globally unknown but exact contexts are known
- WHEN les sept réalisations pertinentes sont confirmées et qualifiées selon le binding et l’inventaire global reste UNKNOWN
- THEN ce dernier n’ajoute aucune insuffisance ou disponibilité inventée.
#### Scenario: One setting is still bootstrap
- WHEN une réalisation ne dispose pas d’un réglage actuel qualifié accepté
- THEN aucun SCIENTIFICALLY_READY/ELIGIBLE n’est fabriqué depuis la seule disponibilité.

### Requirement: Science time and start permission remain separate
SCIENTIFICALLY_READY SHALL NOT créer une séance ou garantir le temps. L’incertitude temporelle SHALL rester explicite et la permission SHALL exiger l’ack réel lié au snapshot/révision/empreintes/plan+temps/policy exacts. Une borne de repos sous budget SHALL NOT prouver une borne haute.
#### Scenario: Limited science with unknown time
- WHEN le producteur admis fournit science positive limitée et BUDGET_UNCERTAIN sans ack exact
- THEN la permission reste REQUIRES_TIME_ACK, sans durée estimée compatible prétendue.
#### Scenario: Ack context changes
- WHEN un fait/contexte/plan/temps/policy/version pertinent change après l’ack
- THEN l’ack antérieur ne permet pas le start et une nouvelle décision est requise.

### Requirement: Durable atomic first-session identity
La commande SHALL persister owner/request_id/digest et un seul handoff Blueprint par propriétaire. Même clé/corps SHALL retourner le même résultat ; autre corps SHALL être refusé. Séance canonique, séries, binding, handoff et résultat SHALL committer atomiquement après revalidation fraîche. Seule la première séance du plan admis SHALL être matérialisée par cette voie.
#### Scenario: Lost response after commit
- WHEN la réponse du start se perd après commit puis le client redémarre
- THEN même clé et handoff propriétaire retrouvent le même session_id, sans nouvelle création.
#### Scenario: Two evaluations or different keys race
- WHEN deux demandes de premier handoff concourent pour le même propriétaire
- THEN au plus une séance est liée au handoff, y compris après fin/abandon de celle-ci.

### Requirement: Shared admission and cancellation race safety
Tous les writers d’ouverture applicables SHALL partager l’exclusion DB propriétaire, y compris starts historiques, reopen et restauration. Cancel SHALL atomiser tombstone contre création ; après CREATED seules pause/fin/abandon canoniques SHALL clore la séance sans suppression historique.
#### Scenario: Historic start or reopen races with SCI
- WHEN les deux chemins tentent d’admettre une séance pour le même propriétaire
- THEN la garde persistée empêche une double admission, sans mutex mémoire supposé suffisant.
#### Scenario: Cancel arrives before delayed start
- WHEN cancel gagne l’identité request_id/digest avant le POST start tardif
- THEN la commande reste CANCELLED et aucune séance n’est créée ; si start avait gagné, cancel retourne ALREADY_CREATED.

### Requirement: Exact lossless canonical execution
La séance SHALL utiliser WorkoutSession/SessionExercise/SetLog possédés avec binding immuable complet des intentions/exercices/contextes/prescriptions/versions et liens d’exécution. Elle SHALL NOT hériter warmups2/1, dose, overload, charge ou substitution de template historique. Cible prescrite SHALL rester distincte d’un fait exécuté.
#### Scenario: Template-less session is materialized
- WHEN une décision valide est créée
- THEN les séries exactes sont non complétées, sans poids/reps/date exécutés inventés, avec identité canonique non tronquée dans le binding.
#### Scenario: Setting cannot be represented
- WHEN unité/côté/sémantique/réalisation n’a pas de mapping couvert et approuvé
- THEN création est refusée avant tout commit de séance, sans conversion en kg/bilatéral.

### Requirement: Typed native logging and replay-safe correction
Le profil natif V3 SHALL conserver réglage typé/contexte et faits SetLog dans une transaction, avec op_id/digest/révision. PER_IMPLEMENT/MACHINE_DISPLAY_KG SHALL NOT devenir masse totale ; rejeu ancien SHALL NOT écraser une correction récente. Les états pending/refused/unknown/acked SHALL survivre à la relance.
#### Scenario: Machine setting is logged then app restarts
- WHEN une série est acquittée avec MACHINE_DISPLAY_KG
- THEN le même réglage/context/intent est relu via API native sans totalisation ou fait perdu.
#### Scenario: Old outbox command arrives after correction
- WHEN un op_id déjà acquis est rejoué après correction explicite plus récente
- THEN l’ancien résultat est réacquitté sans remettre l’ancienne valeur.

### Requirement: Profile-aware transitions derivations and lifecycle
Exécution/clôture/agrégats SHALL traiter explicitement le profil SCI : repos prescrits entre séries du même slot seulement, setup inter-exercice sans durée prescrite, aucun score/implicit label/record/continuité historique par fallback incompatible. Comptes de faits autorisés et sortie incomplète SHALL rester conservés.
#### Scenario: Next exercise follows a completed slot
- WHEN la dernière série du slot est faite et le slot suivant existe
- THEN la transition de setup n’invente ni repos chiffré, ni durée0, ni promesse de temps.
#### Scenario: Closure encounters template-less per-implement settings
- WHEN la séance SCI est terminée avec ces observations typées
- THEN aucun score80, NULL→0 ou consigne suivante historique n’est déduit d’un défaut inapplicable.

### Requirement: Resume and journal do not grant renewed work authority
Lecture, réconciliation, journal tardif et sortie SHALL rester possibles après création ; nouvelle consigne/reprise active SHALL exiger l’applicabilité actuelle sans concern bloquante. Une autorité inconnue/offline SHALL rester inconnue ; un simple log de cette séance SHALL NOT invalider de lui-même sa révision d’entrée.
#### Scenario: Policy revoked after creation
- WHEN la policy est retirée ou son état courant ne peut être établi
- THEN séance/faits restent lisibles et journalisables, mais relecture ne donne pas une nouvelle permission de travail.

### Requirement: Native generation and visual boundaries
Les consommateurs SHALL ignorer les réponses retardées d’une ancienne génération/auth/propriétaire et partitionner les identités durables. MISSION SHALL rester visuellement LOCKED ; toute acquisition/proposition/ack/delta visible SHALL passer les gates humaines avant commit UI et les recettes Android/iPhone.
#### Scenario: Account switches during start reconciliation
- WHEN la réponse du compteA arrive après connexion du compteB
- THEN aucun état/commande/séance deA n’est exposé àB.
#### Scenario: Scientific proposal is valid but session is not created
- WHEN la science est disponible sans CREATED propriétaire vérifié
- THEN aucune navigation MISSION/exécution n’est présentée comme succès de démarrage.

### Requirement: Minimal justified persistence
Le scope SHALL employer les sept tables et trois indexes composites de MINIMAL_PERSISTENCE, sans colonne canonique ajoutée ni table d’ack/handoff séparée. SourceEvent SHALL porter révision/provenance ; Evaluation enfant SHALL porter ack ; Request CREATED unique SHALL porter le handoff. Les copies SHALL attendre politique DATA avant activation réelle.
#### Scenario: Two accepted first commands target one owner
- WHEN deux requêtes veulent persister CREATED pour le même propriétaire
- THEN unicité partielle en base et garde commune empêchent deux handoffs, même après fin ou abandon de la première séance.

### Requirement: Reproducible runtime packaging
Le runtime SHALL vérifier manifeste, sources et modules SCI effectivement importés hors checkout. Les fichiers pinés SHALL rester inchangés ; les antécédents historiques SHALL NOT remplacer le code backend courant. Aucun nouveau payload READY de fixture SHALL alimenter le transport ou les assets publics.
#### Scenario: Developer checkout is unavailable
- WHEN l’API tourne depuis le bundle isolé et une dépendance SCI manque ou diverge
- THEN le profil reste NOT_SERVED et aucun succès de schéma ne remplace le vrai producteur validé.

### Requirement: Explicit migration and controlled acceptance
Startup SHALL NOT appliquer le DDL PLAN implicitement. Le GO de scope SHALL distinguer bases de test, activation réelle et déploiement. COMPLETE contrôlé SHALL exiger une séance possédée exécutée dans une vraie application native autorisée, pas un DTO seul. Gates DATA et appareils physiques non prouvées SHALL rester OPEN.
#### Scenario: Native controlled test passes
- WHEN T32 prouve acquisition, vrai plan, ack, création, journal, reprise et lecture historique natives
- THEN cette preuve ferme seulement le périmètre contrôlé approuvé, sans simuler recette Android/iPhone physique ou déploiement.

### Requirement: Consolidated visual review
Toute géométrie nouvelle SHALL attendre le croquis puis le board de pixels réels accepté par l’opérateur. Le board SHALL regrouper acquisition, proposition, ack, observations et états d’erreur à côté des références validées. MISSION et séance SHALL rester LOCKED hors delta visible explicitement accepté.
#### Scenario: Scope is approved before pixels
- WHEN seul le GO BUILD est reçu et aucun board de pixels n’est encore accepté
- THEN le backend peut progresser dans son scope mais aucune géométrie nouvelle n’est committée.

### Requirement: First encounter is independent from full-plan qualification
Le runtime proposé SHALL distinguer rencontre first-calibration-encounter/1.0.0 et plan V3. Il SHALL permettre ouverture/aide sans sept réglages et sans cadence/budgets complets. Les consignes physiques SHALL rester celles du pilote réellement admis, sans étendre les six autres réalisations ni transformer QUALIFIED en permission de première séance.
#### Scenario: New user with one qualified pilot setting
- WHEN l'utilisateur a ouvert sans historique puis qualifié seulement le pilote
- THEN cette observation reste utilisable, le vrai V3 conserve ses autres manques et aucune séance ou six épisodes ne sont fabriqués.

### Requirement: Actual observations and current permissions have separate sources
La projection propriétaire SHALL conserver les faits d'observation réellement présents indépendamment du state de la rencontre. Elle SHALL NOT ajouter de permission, modifier le résultat scientifique ou déduire zéro observation d'une phase FAMILIARIZE.
#### Scenario: Current setting missing after an actual observation
- WHEN le résultat SCI1.0.0 revient en familiarisation alors qu'un essai passé est conservé
- THEN le consommateur distingue le fait passé et la condition courante manquante sans autoriser un nouvel essai ; ledger incomplet reste inconnu.

### Requirement: Private attestation material never becomes runtime user input
Le packaging SHALL conserver les pièces effectivement pinées nécessaires aux vrais loaders et vérifier le code réellement importé. Une pièce synthétique privée SHALL NOT être exposée, appelée comme factory ou utilisée pour remplir les observations/recommandations de l'utilisateur.
#### Scenario: Real loader requires a pinned synthetic source file
- WHEN une pièce de test historique est nécessaire uniquement à la vérification de ses octets
- THEN elle peut rester preuve privée inaccessible au transport, et le chemin runtime produit depuis les seules sources propriétaires ; un appel de factory ou fallback de fixture échoue au test hermétique.

### Requirement: Versioned seven-encounter runtime inventory
Le runtime contrôlé SHALL consommer le pilote et les six extensions via un inventaire privé explicite versionné, vrais loaders/évaluateurs/validateurs et module closure attestée. Les contrats et sources SCI historiques SHALL rester inchangés. Une version inconnue SHALL fermer le nouveau guidage, sans compile_candidate ou fallback checkout.
#### Scenario: New client reaches a pilot-only bundle
- WHEN le consommateur demande plan-calibration-inventory/2.0.0 et que le serveur ne possède que le pilote
- THEN la capacité des six est refusée explicitement, sans downgrade silencieux ou faux supported.

### Requirement: Actual exact-setting encounter acquisition
Chaque nouvelle rencontre SHALL acquérir contexte/réalisation/device/côté/sémantique réels, choix disponible, préparation, familiarisation Setting exact, essai et acceptation distincts par ledger propriétaire. Aide SHALL rester accessible dès zéro épisode ; UNKNOWN SHALL NOT devenir disponibilité, absence de préoccupation, charge ou acceptation.
#### Scenario: Familiarization lacks the chosen setting
- WHEN seule une confirmation sans réglage ou un booléen d'essai est présent pour une des six
- THEN le vrai SCI ferme essai/acceptation/qualification ; aucune normalisation serveur ne fabrique la confirmation manquante.
#### Scenario: Unloaded RDL preparation
- WHEN le geste sans haltères est rapporté avant choix effectif
- THEN il reste préparation sans masse, pas essai PER_IMPLEMENT/BODYWEIGHT/0kg ou série de travail.

### Requirement: Explicit current-context projection preserves all history
Une sélection courante SHALL provenir d'un acte propriétaire explicite, jamais de l'ordre lexical ou dernier épisode. Le snapshot SHALL revérifier la qualification courante des rencontres guidées avec leur vrai profil et conserver toutes préoccupations/retraits pertinents hors filtrage. Historiques non sélectionnés SHALL rester lisibles.
#### Scenario: Available setting changes after an accepted trial
- WHEN un nouveau choix disponible n'a pas sa familiarisation et son acceptation exactes
- THEN l'ancien CALIBRATED C3 brut ne suffit pas à produire un premier plan applicable.
#### Scenario: New unknown device selected
- WHEN un contexte inconnu remplace explicitement le contexte précédent pour la préparation
- THEN ses manques bloquent le positif courant sans supprimer l'ancienne observation ou supposer l'équipement.

### Requirement: Runtime authority context binds snapshot acknowledgment and start
Inventaire, packaging, profils et génération capturés SHALL être vérifiés aux nouveaux evaluate/ack/start/applicability en plus des empreintes SCI/owner/révision. Aucun snapshot ou ancien reçu SHALL être réécrit pour apparaître courant ; le rejeu terminal SHALL retrouver son fait sans redonner permission actuelle.
#### Scenario: Bundle changed with identical V3 pins
- WHEN le packaging ou l'inventaire change mais les pins scientifiques V3 restent identiques
- THEN l'ancien snapshot/ack ne permet pas une nouvelle création, même si la génération opérationnelle a été reconduite par erreur.

### Requirement: Owned recovery and actual V3 handoff
Les consommateurs HTTP/natifs SHALL utiliser les identités durables, source revision et gardes A/B existantes. Sept rencontres réellement qualifiées SHALL alimenter snapshot/vrai V3/validation/ack exact puis commande idempotente et exécution/journal possédés. Temps inconnu et kg machine/par haltère SHALL conserver leur sens.
#### Scenario: First-session response lost after commit
- WHEN sept épisodes guidés applicables ont permis CREATED et que sa réponse se perd
- THEN reprise/handoff retourne la même séance réelle, sans deuxième start ou MISSION fallback.
#### Scenario: Encounter response arrives after account or selection changes
- WHEN une lecture ou écriture de rencontre se termine tardivement
- THEN aucune valeur ou action de l'ancien compte/contexte n'est appliquée au nouveau formulaire.

### Requirement: UX-CAL gates and controlled-only delivery
Les surfaces nouvelles SHALL respecter G1 avant composition et vrais pixels comparés/acceptés avant commit UI. MISSION, instruments et baselines verrouillés SHALL rester préservés. Le build SHALL rester contrôlé par APP_ENV=test/flags et bases/comptes synthétiques isolés, sans activation réelle/migration/déploiement ou acceptation appareil implicites.
#### Scenario: CI passes but pixels have no approval
- WHEN le backend et les tests passent sans décision opérateur sur les nouveaux pixels
- THEN la publication UI attend son gate ; aucun test ou rendu web ne remplace ce verdict ou une recette physique.
