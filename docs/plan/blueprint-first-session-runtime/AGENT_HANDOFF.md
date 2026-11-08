# AUREN PLAN V3 — passation du runtime contrôlé

8 novembre2026. **Réalisation contrôlée vérifiée, publication en cours** ; statut
final et SHA/CI dans DELIVERY/CLOSEOUT après observation. Cette passation ne vaut
ni admission DATA, ni activation réelle, ni déploiement ou recette physique.

## Mandat et autorisations acquises

Le mandat FIRST SESSION RUNTIME PREPARATION puis FIRST REAL SESSION DELIVERY a
été borné par BUILD_SCOPE/MINIMAL_PERSISTENCE/BOOTSTRAP_INTEGRATION. L'opérateur
a répondu «Autoriser le build PLAN contrôlé», «Valider ce croquis G1», puis
«Valider ces pixels PLAN contrôlés». GOV-MERGE-01 autorise la livraison complète
du seul scope contrôlé sous gates, sans nouveau GO MERGE routinier.

Base scientifique/produit : canonique b4a42420afa1aca384a16bd3966ab85a97cfd724.
MOB03 compte/préférences/journal et MISSION ne sont pas à rouvrir. Le vrai
producteur3.0.0, policy1.0.0-limited et le pilote leg-extension1.0.0 sont
consommés depuis les autorités publiées ; aucun V4, nouvelle admission, rehash
historique ou remplacement du SDK V1.

## Résultat prouvé et réemploi

Compte authentifié → déclarations/observations propriétaires → snapshot
immuable → vrai SCI → accord temporel → commande atomique → une séance canonique
→ exécution native typée → reprise/journal/correction/fin. La preuve contrôlée
est décrite avec ses sources/limites dans TEST_EVIDENCE, le board dans UI_REVIEW.

Le domaine WorkoutSession/SessionExercise/SetLog reste propriétaire des faits.
Pas de template/warmups/overload ou nouvelle chronologie corporelle. Le binding
conserve prescription, intention et identité canonique complètes ; les faits
exécutés restent séparés. Réglages machine/par élément ne deviennent pas masse
totale. Dérivés incompatibles non évaluables, CSV et restauration legacy refusés
sur ce profil plutôt qu'une conversion silencieuse. Les anciennes séances V1
restent lisibles/journalisables dans leur contrat.

## Contrat consommateur effectif

- Namespace `/api/mobile/v3`, Bearer existant, no-store ; négociation exacte
  `first-session-runtime/3.0.0` et contrat rencontre séparé1.0.0. Les DTO SCI
  restent first-plan-request/recommendation3.0.0 et Blueprint1.0.0.
- Serveur choisit owner/subject/as_of/autorité. Source ledger append-only et
  révision commune aux writers canoniques, UNKNOWN/WITHHELD/CONFLICT/[] distincts,
  provenance par événement ; pas de date renouvelée par lecture.
- Snapshot immuable porte facts/contextes/observations/versions/empreintes ;
  consent assessment transport indépendant du DTO SCI. Hors test synthétique,
  absence DATA pertinente reste UNAVAILABLE ; pas consentement global inventé.
- request_fingerprint, observation_fingerprint, full_evaluation_fingerprint et
  plan_time_fingerprint canoniques gardent leurs rôles distincts. Digests de
  commande/transport/bundle ne remplacent pas identité ou autorité.
- Policy limitée : adulte non clinique déclaré, hypertrophie, cadence2,
  limitations vides et sept réglages bilatéraux actuels qualifiés/acceptés.
  Matériel global inconnu permis si contextes exacts disponibles. Pas poids,
  taille ou inventaire obligatoire. Le pilote leg-extension est accessible
  avant ces sept réglages, mais ne qualifie pas automatiquement les six autres.
- SCIENTIFICALLY_READY ne signifie pas séance créée ou durée connue. Le profil
  limité retourne BUDGET_UNCERTAIN/UNKNOWN ; accord exact→ELIGIBLE, revalidation
  courante avant création. Budget déclaré jamais durée prévue.
- Première session scientifique choisie serveur, handoff unique permanent par
  compte, request_id/digest durable ; rejeu exact rend le même reçu avant CAS
  de fraîcheur. Deux clés ne créent pas deux séances. Cancel antérieur laisse
  tombstone ; CREATED ne se supprime pas par cancel.
- Réponse perdue : conserver corps/clé, lire reçu/handoff ; nouvelle clé jamais
  substituée à unknown. Refus métier confirmé distinct d'erreur infra privée.
- Reprise de position/historique ne vaut pas nouvelle consigne. Applicabilité
  actuelle doit autoriser le travail ; pause/offline/retrait enlèvent les actions
  sans supprimer faits/journal/sortie. Pas de reprise automatique après concern.
- Faits typés : op_id/digest, révision CAS, dates/faits immuables. Refus409 connu
  se résout explicitement après GET propriétaire ; RESOLVED conserve l'ancien
  fait et ne dit jamais ACKED. Correction suivante nouvelle identité/révision.
- Erreurs :401auth,404absent/étranger indistinguables,406version,409CAS/digest/
  séance ouverte,422structure,503privé/indisponible. Un statut HTTP seul ne prouve
  ni création, ni qualification, ni effacement.

## Entrées de code et frontières

| Bloc | Sources |
|---|---|
| Persistence | app/models/first_plan_runtime.py, migration plan_v3_20261107_01, sept tables et indexes composites ; une table locale journal_v3_set_operations |
| Transport | app/routers/mobile_plan_v3.py ;18routes inventoriées et classées dans MOB00 |
| Sources/snapshot | app/services/plan_v3/snapshots.py, transactions.py ; training_preferences flush-only et wrappers historiques |
| Autorités | authority.py, packaging.py, science_worker.py, evaluations.py, calibration.py ; build_plan_v3_runtime_bundle.py |
| Commande/exécution | commands.py, execution.py, journal.py ; gardes legacy et dispatch dérivés |
| Consommateur | APIs parallèles blueprintV3/firstPlanV3/firstSessionV3/firstUseV3/calibrationV1, journal/outbox/sync typés, UI plan et composition contrôlée |

V1 firstPlan.ts/firstPlan.contract.json et sources SCI historiquement pinées
inchangés. Le bundle privé contient les preuves pinées nécessaires au loader,
jamais une factory de données utilisateur. Le test hermétique copie app/data
hors checkout et vérifie les imports effectifs ; aucun fallback poste.

## Exploitation contrôlée et compatibilité

Premier dialecte prouvé : SQLite, vraies connexions concurrentes. PostgreSQL
n'est pas certifié par ces tests. Startup n'applique pas les tables PLAN ;
migration additive sans seed ACTIVE et flags off par défaut. Acquisitions,
évaluations, créations et guidage nécessitent APP_ENV=test et flags contrôlés.
L'environnement natif observé est Expo Go58 dans un simulateur dédié, pas un
IPA de distribution. Aucun déploiement/Store/OTA réalisé.

Voir CONTROLLED_RUNBOOK pour la matrice V1/V3, off/on et rollback conservant
lectures/réconciliation/journal/fin. Ne pas remettre un ancien backend qui
ignore les marqueurs SCI devant ces séances. DATA_BOUNDARY inventorie les copies
et relations nouvelles ; aucune durée ou règle d'effacement n'est inventée.

## Qualité et limites de preuve

69suites/749tests mobiles et TypeScript passants. Revues code et interface SCI
fraîches/distinctes, défauts importants reproduits puis corrigés en une passe
avec régressions. Historique natif exact relu après relance/correction ; A/B
isolés. Pixels acceptés avant commit. MISSION/baselines inchangées.

Le reçu final doit citer le full backend borné du tier MIGRATION, contrôles de
migration/sécurité/protocole, CI du HEAD et canonique, verdict Sonar réel et
cleanup observés. Ne pas transformer une vérification en cours en PASS. Les
scripts/preuves détaillés restent hors checkout sous
`/private/tmp/auren-plan-v3-runtime-review-evidence/` ; aucune donnée QA privée.

## Dépendances encore ouvertes et prochains mandats

| Voie | Livrable nécessaire | Responsable |
|---|---|---|
| DATA réelle | D-POL01–05, finalités/consentement des limitations/observations, copies/export/retrait/effacement/restauration, kernel de fermeture | Responsable des données +architecte |
| SCI première utilisation étendue | Premières rencontres défendables pour les réalisations effectivement nécessaires au-delà du seul pilote ; pas sept faux réglages | Agent SCI +opérateur |
| Runtime réel | Autorité opérationnelle/pub/retrait, bundle/configurations réels, compatibilité déployée et rollback | Architecte/exploitation après DATA et GO distinct |
| RELEASE | Builds/cibles autorisés, Android+iPhone physiques, force-kill/SQLite/clavier/accessibilité/A-B | Opérateur recette +release |
| Suite produit | Replanification après premier handoff/substitution/agrégats seulement sous scope propre | PLAN/MOB04–10 selon roadmap |

Les critères globaux PLAN01–07, DATA01–07 et RELEASE01–06 gardent leur état réel.
Le scope contrôlé ne les supprime ni ne déclare MOB03 complet. Prochain agent :
fetch du canonique frais, lire CLAUDE/GOV-MERGE-01 et ce reçu, préserver checkout
opérateur61ca08c, préparations ARCH et installations QA. Ne pas recréer le socle,
les contrats ou le producteur et ne pas lancer une deuxième PR chevauchante.
