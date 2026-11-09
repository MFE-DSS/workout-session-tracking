# PLAN V3 — décision de réalisation soumise à l'opérateur

8 novembre 2026. **GO_BUILD_CONTROLLED reçu / production NOT_SERVED.** Décision «Autoriser le build PLAN contrôlé» ; G1 puis pixels acceptés séparément. Le texte de proposition ci-dessous conserve le scope exact revu, non une demande de GO à renouveler. Base b4a42420afa1aca384a16bd3966ab85a97cfd724 après fetch. [Réconciliation calibrage/PLAN](BOOTSTRAP_INTEGRATION.md). [Mandat reçu](OPERATOR_REQUEST.md), [design](design.md), [schéma justifié](MINIMAL_PERSISTENCE.md), [board de croquis](REVIEW_BOARD.md), [tâches](tasks.md).

## Direction reçue, pas à réarbitrer

Snapshot propriétaire, vrai loader/producteur/validateur SCI V3, négociation explicite, évaluation durable, ack exact, commande idempotente, séance canonique et exécution typée/native. MISSION et séance LOCKED ; pas de template/fallback, nouveaux kg, durée, warmups, overload ou substitution fabriqués. Client V1 et replays historiques pinés conservés. Ces orientations sont approuvées par le mandat ; leur réalisation exige encore son GO.

## Proposition exacte de GO BUILD

Autoriser ce change unique à réaliser A→J : acquisition propriétaire → snapshot → négociation → vrai SCI → évaluation → ack → commande → séance atomique → handoff natif → pause/reprise/journal/fin/lecture historique. Inclure les sept tables serveur, la table locale typée et les trois indexes composites et les bords transactionnels décrits dans MINIMAL_PERSISTENCE, **en ingénierie et bases jetables de test uniquement avant gates DATA/runtime**. Pas de second change chevauchant ou de PR par helper.

La revue couvre la forme précise de migration additive (head actuel z7a2u8v9x20, nouvelle révision proposée plan_v3_20261107_01), le graphe/FK/indexes et les nouveaux endpoints du design. Elle n'autorise ni application sur base opérateur/prod, ni purge/rétention, activation avec données réelles, nouvelle baseline, distribution ou déploiement.

### Fichiers possédés / leases partagés proposés

| Bloc | Fichiers créés ou modifiés sous ce GO |
|---|---|
| Modèles | nouveau app/models/first_plan_runtime.py : sept modèles et indexes externes sur classes canoniques, registration app/models/__init__.py ; migrations/versions/plan_v3_20261107_01.py après recheck head |
| Transactions et sources | nouveaux app/services/plan_v3/{transactions,sources,snapshots}.py ; helpers flush-only et wrappers app/services/training_preferences.py ; endpoints historiques qui les appellent, listés par ciblage Task1 |
| Décision et packaging | nouveaux app/services/plan_v3/{science,authority,evaluations,calibration,packaging}.py ; scripts/build_plan_v3_runtime_bundle.py ; pyproject.toml seulement si support packaging nécessaire, jamais réécrire sources SCI pinées |
| Commande/exécution | nouveaux app/services/plan_v3/{commands,execution,journal}.py ; gardes aux starts app/routers/mobile_api.py et app/routers/sessions.py, ouvertures/reopen/restauration/programmes identifiés Task1 |
| API et startup | nouveau app/routers/mobile_plan_v3.py, composition app/main.py selon entrypoint réel, app/config.py flags désactivés ; app/database.py pour empêcher DDL PLAN implicite de create_all |
| Dérivés | callers/read-models non pinés de feedback/implicit_signal/session_completion/session_provenance/stats/recap/weekly_planner/adaptation ; dispatch profil, pas nouvelle formule. Aucun fichier hors inventaire accepté n'est modifié silencieusement |
| Natif | nouveaux clients/mobile/src/api/{blueprintV3,firstPlanV3,firstSessionV3,firstUseV3,calibrationV1}.ts + tests ; composition ConnectedApp.tsx et outbox/stockage séparés du V1 ; composants acquisition/proposition/ack et delta label de réglage après croquis/pixels acceptés |
| Preuves | tests backend HTTP/races/migrations/packaging, consommateurs natifs réels/HTTP et SQLite fichier ; board unique, runbook, reçus ; aucune fixture READY consommée par app |

Les sources SCI historiques et les79sources de rencontre pinées sont **read-only**, y compris app/models/session.py, app/models/user_program.py, app/services/overload_engine.py, overload_inputs.py, session_review.py, time_format.py, firstPlan.ts et firstPlan.contract.json. Ajouter indexes metadata depuis le nouveau module ; adapter les callers. Si un invariant impose vraiment un changement d'une source pinée : démontrer l'incompatibilité et faire revoir un delta versionné, jamais remplacer son hash. Les contrats SCI V1/V2/V3 ne changent pas.

## Packaging : défaut concret constaté

pyproject.toml ne distribue actuellement que app*. Il ne garantit ni tools.science_initial_policy ni les sources de preuve sous data/docs/clients/openspec. Un import réussi depuis le checkout n'est donc pas une preuve de packaging.

Construire un bundle SCI immuable depuis le manifeste publié : fermeture transitive réelle des deux autorités (79sources de rencontre, plus chargeurs/ancres/manifeste de packaging nécessaires), sans confondre les digests ; ajouter métadonnée de packaging avec hashes déjà publiés. Garder le layout relatif attendu et les anciens chemins pinés. Code SCI exécuté doit venir du bundle vérifié : contrôler __file__ et hashes des modules réellement importés, pas seulement une copie attestée à côté d'un autre code.

Les fichiers app/clients pinés comme antécédents restent des preuves historiques ; ne pas les substituer aux modules backend en cours. Le graphe effectif des imports tools doit être vérifié explicitement. Aucun SYNTHETIC_INPUT, v3_fixtures ou producer-fixtures.v3.json au transport/asset public. Certaines pièces synthétiques pinées sont nécessaires en attestation privée au loader ; elles ne sont jamais appelées ou utilisées comme données runtime, selon BOOTSTRAP_INTEGRATION. Les fixtures v1 historiques déjà pinées restent des preuves privées nécessaires au loader, jamais une source de recommandation servie. Aucun nouveau READY n'est importé depuis JSON.

Tests : unpack hors checkout, sans cwd/PYTHONPATH du dépôt ; vrai loader/producer/validator et vraie API consomment ce bundle. Source/helper manquant, altéré, import depuis poste ou policy invalide => NOT_SERVED/refus fermé. Même digests admis et replay historique ; pas de nouvelle autorité parce qu'un packaging hash existe.

## Activation et environnement contrôlé

Flags distincts : capacités/lecture historique, acquisition, évaluation, nouvelles créations et nouvelles consignes. Installation sans données PLAN : aucun nouveau writer actif par défaut. Après données PLAN, le kernel d’intégrité minimal reste requis par MINIMAL_PERSISTENCE indépendamment des flags de création, dans la politique DATA applicable ; pas de seed ACTIVE en migration, pas de DDL automatique à startup, pas d'activation depuis corps client. Couper création n'efface pas lecteurs, réconciliation ou journal des séances déjà créées. Marqueur SCI sans binding/schéma connu ne passe jamais par fallback V1.

GO proposé pour tests : bases temporaires, comptes synthétiques créés via vraie API, observations synthétiques soumises par vrais consommateurs, vrai producteur ; HTTP loopback et application native de test isolée (simulateur iOS si disponible, identifiant/install distincts de QA MOB02). Aucune donnée/credential QA ou production utilisé. L'environnement simulé ne clôt pas la recette physique Android/iPhone.

Premier runtime contrôlé supporté et prouvé : SQLite, dialecte actuel du poste. Garde PostgreSQL définie ; aucun support positif PG annoncé sans tests de course sur serveur réel autorisé. Cette condition reste explicite, pas transformée en PASS de fixture SQLite.

## Frontières de COMPLETE

Le code ne devient pas COMPLETE sur DTO seul : preuve réelle A→J, sources et ack authentifiés, une séance serveur possédée, logging/reprise/fin/lecture historique natives, défauts/réseau/A-B/concurrence et rollback vérifiés dans environnement contrôlé autorisé. Nouvelles géométries : board de croquis puis vrais pixels comparés aux LOCKED, accord opérateur avant commit UI. Aucun changement de baseline automatique.

Les critères physiques Android/iPhone, DATA de production et déploiement restent OPEN avec leurs responsables et propositions, sans être archivés comme acquis. Le closeout de ce deliverable contrôlé doit les conserver distincts ; pas de clôture MOB03 globale ou de split implicite supprimant une exigence. Le GO de scope devra confirmer cette frontière de livraison.

## Autorisations encore nécessaires

1. Revue de ce scope/delta/schéma et **GO BUILD PLAN** ; pas de demande de GO MERGE routinier après autorisation.
2. Croquis consolidé G1 ; ensuite exposition et acceptation des vrais pixels avant commit UI (CLAUDE §5).
3. DATA applicable avant toute activation réelle de ces nouvelles copies/observations ; décisions du responsable, pas durées inventées.
4. Déploiement/distribution et recette physique sous leurs autorisations distinctes.

Après GO, exécution native task-by-task conservée, TDD ciblé puis intégration réelle, revue code et interface SCI distinctes, CI réelle du HEAD final, fixes dans scope, merge commit sous GOV-MERGE-01, canonique/closeout/cleanup. Aucun chantier de schéma partagé concurrent non coordonné.

## Lease natif précis, parallèle au modèle V1

- Créer `clients/mobile/src/domain/{planV3Types,planV3Workout,planV3Applicability}.ts` : réglages typés, snapshot/version V3, SETUP_NEXT_EXERCISE sans timer inventé, état d’applicabilité. Ne pas faire entrer V3 dans DoneSet.weight ou le reducer V1 par cast.
- Créer `src/sync/{planV3Routes,planV3Reconcile,planV3SyncEngine}.ts` et `src/storage/planV3Journal.ts` : commandes/réconciliation profilées et transaction typée, y compris queue mixte avec anciennes commandes V1.
- Lease partagé explicite `clients/mobile/src/storage/{journal.ts,journal.web.ts,journalTypes.ts,outbox.ts}` pour port transactionnel/dispatch additifs ; `src/sync/{syncEngine.ts,reconcile.ts,serverState.ts,summaryContext.ts}` et `src/api/types.ts` seulement pour séparer profils/maintenir callers. Les tests V1 doivent conserver leurs assertions ; pas de changement de firstPlan.ts/contract pinés.
- Composer dans ConnectedApp.tsx et UI `src/ui/{ExecutionScreen,ResumeScreen,OnboardingFlow}.tsx`, `src/ui/account/FirstUseScreen.tsx`, nouveaux composants sous `src/ui/planV3/` après croquis/pixels. `src/domain/workout.ts` et types.ts restent V1 ; si une modification devient nécessaire, la faire revoir au lieu de la glisser hors de ce lease.
- Réutiliser résolution propriétaire existante ; aucun changement de décision d’attribution/retrait du journal. Les accès à la connexion partagée sont gardés par ce resolver, jamais par un nom d’utilisateur.

Seules les modifications nécessaires au profil V3 sont couvertes ; pas de refactor du moteur V1, des animations, design-system ou pipeline d’assets. Les huit définitions de table (7serveur+1locale) et le kernel off/on sont désormais inclus dans la décision de scope à approuver.

## Portée du premier calibrage réconciliée

Inclure les deux routes et sous-types du ledger décrits dans BOOTSTRAP_INTEGRATION, sans table supplémentaire. Ouverture sans sept réglages ni cadence/budgets complets ; guidage positif du seul pilote admis. Projection des observations antérieures séparée des actions actuelles, jamais correction silencieuse d’un résultat SCI piné. Le scope contrôlé prouve A→J pour sept observations réellement soumises au test ; il ne prétend pas admettre le guidage initial des six autres réalisations ou livrer un premier plan universel.

## Moyen de preuve native disponible, non exécuté

Inventaire read-only le8novembre : CoreSimulator/iOS26.3 disponible. Après GO seulement, créer une instance de test PLAN dédiée et bundle/app de test distincts ; ne pas utiliser l’instance iPhone16e déjà démarrée ni AUREN-MOB02-REVIEW. Aucun boot/install/signing/backend de données réelles effectué pendant la préparation. La disponibilité de simctl ne prouve pas le build ni T32 ; cette preuve reste à exécuter. Android/iPhone physiques restent RELEASE, sans PASS inféré.
