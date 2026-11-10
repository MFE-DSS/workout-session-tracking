# Design — une action possédée, source explicite

## Context

**PROPOSED / NO_GO_BUILD / NOT_ACTIVATED**,9novembre2026. Canonique2b831411.
`app/services/mobile_read_models.py:107` choisit déjà reprise, puis recommandation historique ; `mobile_api.py:288` expose GET /mission. `ConnectedApp.tsx:1063` consomme réellement MissionScreen ; `resumeFromServer` distingue déjà le marker SCI. Les nouveaux consommateurs PLAN et sept rencontres sont livrés, mais activables seulement dans le banc contrôlé. Le vieux constat « producteur absent » de la proposition du5novembre n'est plus le statut du code SCI livré.

Le manifeste produit ET scientifique est le document conjoint `AUREN_MANIFESTO_V1.md`. Il ne prouve ni activation ni autorisation de cette nouvelle tranche. Captures et export de l'outil pilote non reçus ; aucune parité appareil revendiquée.

## Brainstorming / Options / Risques / Choix retenu

1. Fusionner READY V1/SCI ou déduire les permissions sur mobile : rejeté, autorités distinctes et risque de faux démarrage.
2. Refaire la recommandation et le programme hebdomadaire : hors périmètre et double vérité.
3. Projection serveur mince, nouvelle négociation et délégation aux commandes existantes : choix proposé. Coût : une route/DTO supplémentaires et états explicites ; aucun gain scientifique supposé.

## Proposed transport

`GET /api/mobile/v1/mission-action?requested_path=FIRST_USE|HISTORICAL`, Bearer existant, no-store ; paramètre obligatoire. En-tête exact `X-Auren-Mission-Action: mission-action/1.0.0`, écho exact, mismatch406. Pas de downgrade silencieux. Les anciens clients et GET /mission restent inchangés.

Envelope proposé : contract_version, owner_id de l'auth, requested_path écho, observed_at UTC, state, source, primary_action nullable et payload discriminé. Sources `OPEN_SESSION`, `OWNED_FIRST_USE`, `HISTORICAL_MISSION`, `NONE`. États de projection `RESUME`, `FIRST_USE`, `FIRST_SESSION_HISTORY`, `HISTORICAL_READY`, `NO_MISSION`, `UNAVAILABLE`, `CONFLICT` ; états transport unknown/loading restent côté ressource, distincts de NO_MISSION. Ce ne sont pas de nouveaux statuts SCI.

Capacité de représentation seulement : en-tête optionnel exact `X-Auren-Mission-V3-Host: first-session-runtime/3.0.0`, émis uniquement si le vrai contrôleur/host V3 est présent dans ce client. Il ne choisit aucune autorité et n'autorise aucune collecte ou consigne. Valeur inconnue406. Sans ce host, une séance SCI reste source OPEN_SESSION/OWNED_FIRST_USE connue, état UNAVAILABLE/reason `EXECUTION_PROFILE_REQUIRED`, aucune action legacy ni promesse de lecture typée inexistante.

| requested_path | state / source | action et payload autorisés |
|---|---|---|
| l'un ou l'autre | RESUME / OPEN_SESSION | RESUME_LEGACY et résumé canonique LEGACY, ou RESUME_V3 et identifiant/profil PLAN_V3 recoupés ; jamais les deux |
| FIRST_USE | FIRST_USE / OWNED_FIRST_USE | OPEN_FIRST_USE, références propriétaires/révision connue ou inconnue explicite, aucune dose ou permission nouvelle |
| FIRST_USE | FIRST_SESSION_HISTORY / OWNED_FIRST_USE | OPEN_FIRST_SESSION_HISTORY, session_id du CREATED clos et profil PLAN_V3 ; host/schéma/binding disponibles |
| HISTORICAL | HISTORICAL_READY / HISTORICAL_MISSION | START_LEGACY et payload ServerMission READY inchangé recoupé par isStartable/decision |
| HISTORICAL | NO_MISSION / NONE | action=null, payload=null, aucune proposition |
| l'un ou l'autre | UNAVAILABLE / source connue ou NONE | REFRESH ou null selon motif, aucune commande start ; raisons fermées RUNTIME_NOT_SERVED/AUTHORITY_UNAVAILABLE/SCHEMA_UNAVAILABLE/EXECUTION_PROFILE_REQUIRED/HISTORICAL_NOT_EXECUTABLE |
| l'un ou l'autre | CONFLICT / OPEN_SESSION | action=null, raison MULTIPLE_OPEN_SESSIONS, aucun choix/réparation arbitraire ; réponse de projection200, pas un échec transport |

Tout tuple non listé est refusé côté client. Une action portant une session doit pointer le même session_id/profil que son payload ; les références propriétaires ne proviennent pas du téléphone. Versions du payload : ServerMission V1 conservé ; host PLAN `first-session-runtime/3.0.0`, exécution `first-plan-execution/3.0.0`, inventaire de calibrage2 conservés, sans réétiquetage de l'un en l'autre.

Actions fermées : `RESUME_LEGACY(session_id)`, `RESUME_V3(session_id)`, `OPEN_FIRST_USE`, `OPEN_FIRST_SESSION_HISTORY(session_id)`, `START_LEGACY(template_slug, decision)`, `REFRESH`, ou aucune. Aucun URL arbitraire, owner du body ou exercice/charge fourni par le client. Les champs versionnés/source_ref utiles restent dans le DTO et le détail technique, pas dans le cockpit principal.

## Resolution and permission

1. Une seule séance ouverte possédée a priorité, quel que soit requested_path. Plusieurs séances ouvertes = conflit explicite, aucune réparation. Déterminer le profil depuis le domaine serveur ; ne pas deviner via l'alias d'exercice. `RESUME_V3` ouvre le host typé existant ; lecture/position n'autorise jamais une nouvelle série. Applicabilité actuelle/retrait/hors ligne restent gouvernés par V3.
2. Sans séance ouverte, `FIRST_USE` consulte uniquement la disponibilité et les références propriétaires PLAN existantes. Source/schéma/autorité absents : UNAVAILABLE, aucun appel au recommandateur historique pour fabriquer un positif. Si le parcours est disponible et non déjà créé : OPEN_FIRST_USE, jamais START depuis un simple libellé READY. Le host conserve les acquisitions, snapshot, vrai V3, incertitude, ack exact et commande idempotente déjà livrés. Le GET n'évalue aucun fait utilisateur, n'acquitte et ne crée rien.
3. Handoff CREATED déjà clos : OPEN_FIRST_SESSION_HISTORY via lecture typée existante ; aucune deuxième première séance. L'action n'est exposée que si le consommateur lecture réellement disponible est câblé. Replanifier après cette séance reste hors scope.
4. Sans séance ouverte, `HISTORICAL` délègue au vrai mission_read_model et garde son isStartable/decision/raison/zones. Son READY reste explicitement historique. NO_MISSION reste absence réelle ; pas de template par défaut. Un ancien résultat de commande CREATED ne donne aucune permission actuelle.

Le choix du chemin est une navigation explicite, pas un fait physiologique. Proposition de composition : l'entrée de premier parcours existante demande FIRST_USE ; Aujourd'hui historique demande HISTORICAL. Une bascule sous « Autres parcours » est subordonnée, volontaire et sans mutation. Aucun fallback automatique entre les deux. Ce choix produit est proposé à G1, pas déjà approuvé. La reprise ouverte a priorité dans les deux cas.

**Choix G1 encore matériel :** confirmer cette séparation qui conserve Aujourd'hui HISTORICAL, ou choisir Aujourd'hui FIRST_USE par défaut pour le nouveau consommateur avec bascule historique volontaire. Les deux alternatives ont les mêmes données/commandes et reprennent prioritairement toute séance ouverte ; l'alternative retenue sera inscrite avant apply, sans déduire le choix du cache ou d'un score physiologique. Les anciens clients non négociés conservent leur comportement.

### Purity of the projection GET

Lire métadonnées de séances/handoff/schema sans charger l'exécution. Le handler capabilities existant n'est pas réutilisé : il appelle lock_authority avec verrou par défaut et émet un no-op UPDATE SQLite. Le nouveau lecteur peut appeler `lock_authority(db, lock=False)` pour attester la publication disponible : son worker `authorities` est une introspection de pins, pas une évaluation de faits. Il MUST NOT appeler `produce/evaluate`, les validateurs d'échange utilisateur ou `first_plan_execution_read_model` depuis cette projection. Le read-model d'exécution revalide en effet l'applicabilité et reste réservé à l'action du host.

Les branches reprise/CREATED clos consultent d'abord les faits possédés et binding/schéma, avant la disponibilité de création ; flags off/retrait ne suppriment pas leurs lectures. Contrôle de pureté : aucune instruction DML sur DB dans ce GET, aucun nouveau request_id, aucun appel worker autre que `authorities`, aucun producteur/ack/start. Les méthodes existantes de commande ne sont pas modifiées.

## Native consumer

Un `MissionActionClient` décode union/version/owner/path/action/profil et la ressource capture auth.revision + séquence + requested_path. Changement A/B/logout/chemin ou réponse dépassée : résultat ignoré et cache partitionné/effacé. La ressource ne stocke pas un second plan, journal ou autorité. Les brouillons et outbox continuent dans leurs mécanismes existants.

ConnectedApp branche la projection à Today, délègue START_LEGACY au start existant et OPEN/RESUME V3 à FirstUseV3Controller/PlanV3Host. Éviter l'ouverture automatique de deux hosts/CTA concurrents. Le bootstrap/rejeu d'une intention durable existante conserve son identité ; aucun nouveau request_id ni consentement/ack depuis GET/navigation. Panne après start : réconciliation canonique du même compte/commande, pas nouveau start depuis refresh.

Un seul FirstUseV3Controller et journal, conservés lors de la navigation. Retirer uniquement l'ouverture visuelle systématique du host si la projection doit être affichée ; ne pas supprimer son bootstrap ni effacer son pending. Le load existant peut retrouver les reçus et réconcilier une commande durable du même compte ; un retry de mutation source reste l'action explicite actuelle avec sa clé persistée. La ressource MISSION ne lance aucun de ces POST et s'invalide aussi après start/close, pour qu'un ancien READY ne recouvre pas une séance créée.

Hors ligne : faits de la séance déjà possédée et sortie/journal accessibles suivant son profil ; aucune nouvelle permission V3 déduite du cache. Aucun résultat d'un autre propriétaire. Pas de nouveau stockage de faits ni de migration.

## Visual and platform

Réutiliser Frame C, RecessedWindow, NumericReadout si un fait réel le justifie, mark, tokens et BodyMap fonctionnel. Les quatre baselines MISSION-SCREEN-V1 restent read-only ; raison et zones du serveur, CTA visible, pas de nouvelle couleur/logo/score. UX_BOARD couvre une seule famille orientation/absence/reprise ; vrais rendus iOS/Android comparés aux références avant commit UI. Retour Android ferme le détail/choix de parcours sans démarrer ; safe areas/grandes fontes/AX/focus/reduced motion à éprouver sur cible compatible. Aucun écart métier entre plateformes.

## Gates and rollback

GO BUILD + G1 manquent ; revue fraîche requise avant soumission. DATA/autorité opérationnelle/activation/déploiement et recette physique restent distincts. Build contrôlé proposé sur comptes/bases synthétiques, flags existants inchangés par défaut. Rollback désactive seulement la nouvelle projection/son entrée ; lit encore séances/handoff/journal, aucun effacement ni fallback scientifique permissif. Contrôles check_scope puis broad ciblé et CI réelle sous GOV ; aucun sweep systématique hors verdict. Rien n'est encore implémenté ni testé ici.


Réconciliation du mandat PILOT VALUE DELIVERY du10novembre : [PILOT_VALUE_SCOPE](PILOT_VALUE_SCOPE.md) précise base canonique, option de navigation B, commandes locales et leases séquencés. Statut toujours NO_GO_BUILD/G1_PENDING.

## Revue de composition réelle — choix de correction avant apply

10novembre : le démarrage legacy n'a pas de clé idempotente ; une lecture sans
séance ne prouve pas son refus. Sa réception inconnue reste bloquante, y compris
après relance. Métadonnée locale additive dans le JSON MISSION existant :
`mission_opening:{version:"legacy-start-uncertainty/1.0.0",template_slug,requested_at_ms}`.
Aucune table, migration, seconde copie métier, clé de commande ou rejeu automatique.
Helper MOB04 local, domaine/journal partagés inchangés. Écrire et relire cette
marque avant POST ; la sauvegarde différée conserve la même marque. Restaurer
MISSION avec la marque sans RESET ; logout conserve le fichier propriétaire.
Une réponse négative GET ne l'efface jamais. Seuls le refus explicite de ce POST,
son résultat de création sauvegardé ou une séance possédée retrouvée correspondant
au slug permettent la réconciliation ; aucune preuve de durée de traitement.
La voie legacy peut donc rester à vérifier si le serveur ne fournit aucun reçu,
plutôt qu'émettre un second démarrage. Ce coût conservateur est explicite.

Le contrôleur V3 reste unique mais ne revendique plus un journal vierge au boot :
restaurer seulement un V3 déjà présent, garder l'objet/host disponible ; l'action
V3 explicite restore→load peut revendiquer le journal selon ses gardes existantes.
Un vrai brouillon V3 reste protégé contre un start legacy ; aucun écrasement pour
faire passer la recette. Conflit local ≠ panne réseau.

Reprise legacy : après chaque attente, recouper le même contexte de projection,
compte et journal. Une projection courante vers une autre séance invalide
l'ancien choix local ; basculer seulement sur action explicite et sans commande
non résolue du journal déplacé. Faits anciens conservés. Offline sans lecture
active : Actualiser reste disponible ; séance V3 capturée consultable sous pause/
observation seule, sans permission de travail ajoutée. Ces corrections appartiennent
aux cas reprise/unknown/relance et au stockage existant du GO reçu.

Précision de reprise avant correction résiduelle : une projection confirmée
excluant la reprise legacy locale laisse dans le même snapshot le seul marqueur
`mission_resume_blocked:{version:"mission-resume-exclusion/1.0.0",session_id}`.
Ce n'est ni un statut de séance ni un fait d'entraînement. Une lecture échouée,
une bascule de source ou une relance offline ne l'effacent pas. Une confirmation
possédée de la même séance/profil peut lever ce blocage ; une reprise explicite
d'une autre séance conserve les faits anciens dans le journal. Les snapshots
historiques sans cette preuve négative gardent leur comportement offline existant.
Une continuation après écriture doit revérifier le compte/journal avant tout
état partagé, et un finally de l'ancien compte ne libère pas le vol du nouveau.
