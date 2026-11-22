# TIME-01 — provenance temporelle examinée

Base dff03f3, 22 novembre2026. Les horodatages ISO ci-dessous sont UTC,
avec offset explicite ; les millisecondes epoch sont depuis1970 UTC. Une durée
monotone n'est ni une date civile ni une horloge persistable entre processus.

| Valeur | Source / autorité | Persistance et réutilisation | Consommateurs |
|---|---|---|---|
| execution.server_now | datetime.now(UTC) serveur, construction du read model | DTO SQLite : heure de cette lecture, pas heure actuelle après restore | Host, transitions de repos |
| Ancre native avant TIME-01 | Date.parse(server_now) + performance.now() au montage/changement de texte | Appariement possible d'un DTO ancien à un instant nouveau, sans preuve fraîche | date SET et repos |
| Ancre corrigée | réponse d'exécution confirmée + lecture monotone à réception | mémoire du contrôleur seulement ; restore/pause/échec détruit la liaison | affichage dérivé et date à l'action |
| performed_at d'acquisition | avant : valeur du dernier rendu Host ; corrigé : lecture de la liaison à l'action | corps SET immuable avec UUID, avant transport | journal local, outbox, serveur, historique |
| Date estimée sans liaison | Date.now explicitement marquée estimated conformément au repli D11 | revendication incertaine, mêmes bornes serveur ; jamais heure d'effort vérifiée | journal affiche le statut existant |
| recorded_at_ms local | Date.now dans recordFact avant commitSet | transaction SQLite, distinct de performed_at ; peut être postérieur à l'action | preuve d'enregistrement, FIFO durable |
| outbox.created_at_ms SET | copie exacte de recorded_at_ms | même transaction ; rejeu conserve corps/date/UUID | syncEngine et sendPlanV3Outbox |
| FINISH.at | new Date().toISOString dans enqueueClose | corps préparé en transaction, jamais recalculé au rejeu | borne de clôture serveur |
| FINISH.created_at_ms | Date.now dans enqueueClose | heure locale de préparation, distincte du temps d'effort | outbox |
| FirstPlanSetObservation.recorded_at | CURRENT_TIMESTAMP DB serveur | réception/acquisition de l'opération ; n'est pas performed_at | preuve serveur |
| Reçu performed_at | bornes début/précédent/futur du serveur, completed_at canonique | exact rejeu op_id renvoie le reçu initial ; aucune date réécrite par TIME-01 | readback et journal |
| started_at / ended_at | début canonique et clôture bornée serveur | WorkoutSession, historique existant | exécution, historique |
| snapshot.as_of / source_revision / TIME_ACK | capture et décision propriétaires serveur | immuables ; ne servent pas d'ancre d'horloge actuelle | permission V3, jamais estimation du temps d'effort |
| AppState | événement de cycle de vie RN, pas une horloge | pause invalide la liaison et la permission fraîche ; absence d'événement ne prouve pas absence de suspension | contrôleur et Host |
| Repos V3 | completed_at + transition.duration_seconds prescrite, comparés au temps dérivé | pas de compteur décrémenté ou durée0 ajoutée ; pas de nouveau seuil scientifique | workPermissionV3, RestRing |
| RestClock historique | deadlineMs/startedMs epoch murale persistés | moteur Legacy distinct, inchangé | timer.ts, ConnectedApp Legacy |
| Horloge auth | mono injectée dans AuthSession | autorité et durées de jetons séparées, inchangées | aucune date de fait client ne décide l'auth |

Sources : firstUseV3.ts, PlanV3Host.tsx, PlanV3ExecutionScreen.tsx,
PlanV3JournalScreen.tsx, planV3Journal.ts, planV3Sync.ts, firstSessionV3.ts,
app/services/plan_v3/{execution,journal}.py, app/routers/mobile_api.py,
app/models/first_plan_runtime.py. D11 :
docs/strategy/Sx_AUREN_MOBILE_EXPERIENCE_VNEXT_SPEC.md §8.8bis.

## Limites de fraîcheur explicitement conservées

Une réponse fraîchement reçue n'établit pas à elle seule sa latence ni la
continuité d'une horloge pendant une suspension. TIME-01 ne crée pas un seuil
arbitraire de durée de requête ni une politique de dérive. Les traces QA
bornées AUREN_QA_TIME, activées seulement par EXPO_PUBLIC_QA_DELIVERY=1,
relèvent wall_ms, mono_ms, génération, ancre et frontière de lecture/action/
commit. Pas de mesure, prescription, identifiant de compte, token ou DTO.
Elles ne loggent pas chaque tick. Elles doivent encore être acquises dans
l'APK corrigée sous autorisation séparée de publication.

L'estimation est un statut d'incertitude, pas une réparation d'une heure
manquante. Une correction explicite garde set.completed_at s'il existe ;
sinon le formulaire existant propose une nouvelle date explicitement estimée.
Les SET/FINISH préparées avant pause, retard ou redémarrage restent identiques.
