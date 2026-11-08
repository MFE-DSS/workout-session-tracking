# PLAN V3 — preuves contrôlées et limites

8 novembre 2026. Base b4a42420afa1aca384a16bd3966ab85a97cfd724,
HEAD documentaire83b5471 puis réalisation non committée pendant les essais.
Les SHA/runs de publication seront ajoutés après leur observation, sans
confondre ces preuves de working tree avec une CI distante.

## Oracles et tests

Les T01–T37 proviennent du TEST_SPEC approuvé ; ce tableau décrit leur couverture,
pas37tests physiques ni37résultats indépendants. Tests réels d'API via FastAPI,
SQLite sur fichier et connexions distinctes ; doubles déterministes réservés aux
retards/fautes du consommateur. Le positif serveur appelle la vraie autorité
SCI dans un bundle isolé hors checkout. Le simulateur n'importe aucun READY.

| ID | Preuve effective | Limite explicite |
|---|---|---|
| T01–05 | test_blueprint_runtime_http/sources : Bearer, no-store,404 privé, CAS/rejeu, provenance, cinq familles, anciens writers et rollback | Consentement DATA réel non admis ; contrôlé synthétique seulement |
| T06–10 | test_first_plan_v3_runtime_authority/http, packaging et calibration : versions, absence/refus, vraies autorités, ack exact, source/pins changés | Aucune nouvelle admission SCI par PLAN |
| T11–15 | test_first_session_commands, recovery_http, session_start_admission : vrais commits/rollback, réponse perdue, clés concurrentes, cancel/tombstone et starts croisés | SQLite prouvé ; PostgreSQL non exécuté ; restauration legacy explicitement exclue |
| T16 | test_first_plan_execution et autorités : retrait après création, lecture/journal/sortie maintenus, nouveau guidage refusé | Aucun pouvoir de détecter une révocation réseau hors ligne |
| T17–18 | firstUseV3.test, API tests et journaux : toutes générations, inconnus, rejets, commandes durables et relecture | Fautes/latences déterministes, pas mesure réseau utilisateur |
| T19–23 | test_first_plan_execution/http et legacy_boundaries ; domaine/SQLite/sync natifs : exact7×2, identités, unités, corrections, transitions et dérivés inapplicables | Aucune estimation de durée, substitution ou progression nouvelle |
| T24 | firstUseV3 et PlanV3Views : vrais consommateurs/composition, états distincts, CREATED avant exécution | V1 préservé, aucun fallback MISSION scientifique |
| T25 | Plan de recette et baselines inchangées ; pixels contrôlés acceptés | **OPEN : Android et iPhone physiques, clavier/retour/accessibilité sur appareils** |
| T26 | test_plan_v3_persistence : sept tables, FK composites, unicité, immutabilité, startup off ; journalV3Integration une table locale | Aucun backfill ni migration de données utilisateur |
| T27 | test_first_plan_v3_runtime_packaging : vrai worker isolé et API hors checkout, sources vérifiées, tamper refusé | Anciennes attestations privées pinées conservées ; aucun factory appelé |
| T28–31 | persistence/sources/authority/legacy boundaries : startup non migré, off/on, source atomique, refus défaut fermé, graphe DATA | DATA production et exploitation restent bloqués |
| T32 | Parcours natif A→J détaillé ci-dessous, processus réellement arrêté/repris et readbacks serveur/SQLite | Simulateur iOS uniquement, pas build Store ni recette physique |
| T33–37 | test_first_calibration_runtime/http et consommateurs calibrationV1/firstUseV3 : ouverture sans sept réglages, vrais load/evaluate/validate, faits séparés d'actions, progression historique et guards | Seule rencontre leg-extension admise ; aucune extension aux six autres réalisations |

Suites mobiles finales : **69suites,749tests, TypeScript passant**.
Backend ciblé : API hermétique/calibration3cas passants ; courses réelles4cas ;
injection avant commit1cas ; broad consommateurs historiques162cas passants.
Les régressions sont également incluses dans le sweep backend final obligatoire
et la CI globale, dont les résultats doivent être cités séparément.

## Parcours natif A→J réellement observé

Environnement : simulateur dédié AUREN-PLAN-CONTROLLED-V2-20261108,
iPhone16/iOS26.3, Expo Go58.0.17, API loopback8097, Metro8098, base jetable
native-controlled-v2.db. Deux comptes synthétiques utilisés pour les actions
natives A/B ; un troisième acquis par HTTP sans séance créée. Aucun identifiant
QA privé, compte réel ou environnement déployé utilisé.

| Étape | Action et lecture obtenue |
|---|---|
| A | Authentification native A ; rencontre ouvrable sans historique de charge et sans budgets/cadence complets |
| B | Déclarations adulte/non clinique, limitations vides et contexte réel **synthétique de test** saisis ; préparation et choix17kg affichés explicitement, jamais calculés |
| C | Familiarisation puis essai distincts,10reps rapportées, qualité acceptable/gêne absente et acceptation exacte ; vrai évaluateurQUALIFIED ; zéro WorkoutSession/SetLog de travail à ce stade |
| D | Six autres épisodes synthétiques acquis explicitement par les vrais POST HTTP de test, avec familiarisation antérieure/essai/acceptation ; aucun factory/backend ne fabrique les faits |
| E | Objectif, cadence2, disponibilités60/60 natifs ; snapshot possédé et vrai producteur/validateur V3 ; tempsUNKNOWN/REQUIRES_TIME_ACK |
| F | Reconnaissance temporelle native exacte puis décisionELIGIBLE ; une commande durable crée session1owner1, sept exercices/quatorze séries non réalisées |
| G | Trois faits natifs acquittés :17display×9 puis17display×8,24display×10 ; arrêt réel du processus et relance retrouvent même séance/cursor/fait |
| H | Transition d'installation sans chrono, repos prescrit120s observé ; sortie volontaire3/14, clôture acquittée sans complétion forcée |
| I | Correction d'un autre consommateur→serveur11/version2 ; correction native10/expected1 reçoit409 ; refus lisible et conservé, choix explicite USE_SERVER_VERSION→RESOLVED sans fauxACK ; nouvelle correction12/version3 acquittée, date initiale et séance clôturée conservées ; relance et journal vérifiés |
| J | Déconnexion A→B après résolution ; partition B sans séance/rencontre/opération A, planB31 distinct du17 de A. Nouveau contexte B : champ charge vide, découverte setup-only admise ; DB contient seulement intention INITIATE_FAMILIARIZATION, pas tentative/acceptation fabriquée |

Readback final serveur : une séancecompleted,14lignes de travail, trois faits
complétés12/8/10reps, toutes leurs masses legacyNULL, cinq opérations serveur
typées (dont correction externe et correction explicite). Le fait refusé local
n'est pas compté comme fait serveur acquitté. Les vrais tests SQLite vérifient
aussi PER_IMPLEMENT, corrections et fermeture/réouverture du fichier ; ce type
n'a pas été journalisé dans la séquence native capturée, distinction conservée.

Captures brutes/empreintes et décision «Valider ces pixels PLAN contrôlés» dans
[UI_REVIEW](UI_REVIEW.md). Erreur CUA noWindowsAvailable/capture blanche apparue
ultérieurement : recaptures de confort non obtenues, PNG simctl originaux non
retouchés. Pas de test de largeur ou appareil supplémentaire déduit.

## Revue finale et unique passe de correction

Revues fraîches code et SCI distinctes, documents conservés dans
`/private/tmp/auren-plan-v3-runtime-review-evidence/` ; elles portent sur la
branche agrégée, pas une réadmission scientifique. Zéro Critical.

| Constat | Correction et preuve RED→GREEN |
|---|---|
| CodeI1 : ancien local masque correction/CAS autre appareil | Fait serveur plus récent prioritaire sur ACKancien, chaîne pending distincte, CAS depuis révision courante ; undo completion/cursor testés |
| CodeI2 : refus409 bloque chaîne et fin | Refus projeté FAILED ; résolution explicite après GET possédé, états RESOLVED persistés, corps/faits immuables et aucune inconnue sautée ; déconnexion et clôture ensuite possibles |
| CodeI3 +SCII1 : permission pilote périmée après pause/échec | Génération portée à travers lectures et mutations ; permissions retirées sur inconnue, faits historiques conservés |
| CodeI4 : historique natif/correction absents | Journal accessible pendant/après séance, faits typés/date/révision/état et corrections explicites ; séance terminée jamais rouverte par correction/arrière-plan |
| SCII2 : réglage non massique montré en kg | Formatage kind+unit+semantics, refus de représentabilité serveur maintenu |
| SCIM1 reclassé Important par contrôleur : découverte setup-only cachée | Action existante rendue avant valeur numérique ; intention seule réellement vérifiée sans fait/charge fabriqué |

Toutes les régressions mobiles font partie des749tests finaux. Pas de deuxième
campagne de revue, de nouveau contrat SCI ou refactor legacy. Rulings et limites
de jugement conservés : pixels jugés par opérateur, DATA/production/physiques non
certifiés, PG non prouvé, multiples opens web historiques conservés mais bloquent
SCI, CSV/restore legacy refusés, première séance SCI unique et six autres pilotes
hors scope. Aucun audit sécurité global revendiqué.

## Contrôles de livraison

Tier MIGRATION ; full local par `bash scripts/run_local_sweep.sh` seulement,
processus frais par lots/watchdog, sans couverture locale. Ancien sweep interrompu
avant dernière projection n'est pas PASS. Ruff neuf/budget260≤548, Bandit ciblé
zéro Medium/High, protocoles/OpenSpec14/14, migrations patterns/roundtrip/drift/
snapshot ont passé. Inventaire des18routes classé,14tests migration-map passants.

Gitleaks : scan des123fichiers modifiés avant derniers reçus sans fuite ; scan
arbre complet signale une clé d'issue Sonar historique inchangée, pas credential.
Aucune allowlist ou politique modifiée. Scan final des changements et CI réelle
restent requis. Les reçus finaux consignent leurs résultats effectifs.

## Référence de migration mise à jour après résultat rouge

Le sweep final a reproduit un seul échec au lot28 :
`test_exercise_knowledge_base::test_alembic_head_unchanged` attendait encore
`z7a2u8v9x20`, face au head approuvé `plan_v3_20261107_01`. Ce fichier n'est
pas dans les sources SCI pinées. L'assertion demeure exacte ; seule sa référence
et le commentaire d'historique changent. Le module complet repassé depuis le
worktree rend24/24. Le log original garde son rouge, aucune suppression de test
ou tolérance de head arbitraire. Le sweep a terminé les418fichiers ; la CI finale doit rejouer la suite entière
sur le HEAD publié.

## Verdict local final, sans masquer les deux sentinelles

Le script borné a terminé418/418fichiers en159lots, deux adaptations4→2→1,
pic des lots aboutis1968Mo pour budget1998Mo. Son **exit1 reste consigné**,
avec deux tests rouges initiaux, pas un faux log de sweep vert :

1. Référence de head Alembic corrigée comme décrit ci-dessus, module24/24.
2. test_worked_area_descriptor::test_no_model_migration_schema_touched inspecte
   `git diff HEAD` du working tree et refuse tout modèle/migration non committé.
   Aucune assertion modifiée : les14tests du module passent sur un snapshot Git
   propre du tree exact dbdf06f08a27e89331ba73e7d3c2770d885f20b9, extrait de
   l'index. Ce snapshot local jetable reproduit la propreté du checkout CI ;
   ce n'est ni une CI distante ni une seconde branche produit publiée.

Tous les autres lots ont passé. Les deux causes sont résolues/vérifiées sans
changement du code produit après le sweep ; aucun échec local non expliqué ne
reste. La CI réelle du HEAD final reste obligatoire avant merge.
