# SCI-P02-INITIAL-POLICY-ADMISSION — design proposé

## Context

Base `2b52f4984e375faad0a1488feef1bfe3bcab01b0`. [REPORT](../../../../docs/science/sci-p02-initial-policy/admission-system-01/REPORT.md) distingue lecture du code, rejeu réel et décisions proposées. État effectif immuable pour cette passe : `0.3.0-proposed`, `NOT_ADMITTED`, `NOT_SERVED`, `READY_NOT_PRODUCED`. Le parent `science-initial-plan-policy` reste ouvert pour son histoire globale ; cet enfant possède seul la prochaine admission. Les anciens dossiers ne sont ni corrigés en place ni remplacés.

## Goals / Non-Goals

Évaluer le bundle effectivement assemblé, identifier les gates suffisantes et les preuves manquantes, définir une frontière de contrat que PLAN peut implémenter après admission. Aucun changement fonctionnel, schema/JSON, registre, test exécutable ou activation pendant cette préparation. La suffisance utilisateur dépend des cinq REQUIRED_FIELDS actuels, pas de poids/taille/expérience.

## Brainstorming / Options / Risques / Choix retenu

1. **Projeter v2 vers v1 inchangé** : possible seulement après admission d'un calcul d'exposition numérique conventionnel EXACT pour les quinze zones, prescriptions représentables, allocation revue et temps admis. Risque : attribuer au diagnostic qualitatif une précision qu'il ne calcule pas. Aucune impossibilité générale de v1 n'est affirmée : son EXACT peut décrire une convention comptable, jamais une dose biologique mesurée.
2. **Contrat successeur explicite** : séparer complétude d'une déclaration de quinze zones, inconnus d'exposition, prescription bootstrap/réglage opérationnel et admissibilité d'exécution. Coût : DTO/validateur, adaptateur PLAN et consumers à coordonner ; v1 reste intact.
3. **Changer silencieusement READY v1** : exclu, conflit de spec.

Choix de l'auteur proposé : option 2, à faire approuver avant apply ; conserver le blocage C6. Ce choix n'est pas une décision opérateur déjà obtenue. Si option 1 est préférée en revue, elle doit gagner ses preuves/comptabilité propres ; changer le libellé du draft ne suffit pas.

## Observed behavior

`produce_v2` évalue les vrais inputs, sélectionne globalement sept candidats distincts par `match_distinct`, répète l'allocation 2/3 fois et calcule calibration/temps. `EvaluationResult` borne littéralement son admission à NOT_ADMITTED et sa disponibilité à NOT_SERVED. `_recommendation` ne produit jamais candidate_plan ; statut CONFLICTING_DATA, INSUFFICIENT_DATA, sinon POLICY_UNAVAILABLE. `_timing` ajoute toujours POSITIVE_TIME_MODEL_NOT_ADMITTED. `v2_registry` refuse un registre avec approved refs non vides et vérifie sa signature exacte : l'admission exige une nouvelle version, pas une édition du JSON piné.

## Decisions

### D1 — Six gates, aucune admission par libellé

Chaque décision C1..C6 porte **PROPOSED_FOR_SCIENTIFIC_REVIEW**. Conserver une décision revue par gate avec base, limites, reviewer, date, version et déclencheur de révision. C1/C2 reprennent les dispositions bornées existantes comme propositions sur le bundle actuel ; C3..C6 restent non acquis pour le système. Verdict auteur `NOT_ADMITTED`, aucune écriture dans approved_policy_refs. Une réadmission partielle documentaire ne doit pas ouvrir une branche READY.

### D2 — Corrections minimales proposées avant admission

| Sujet et racine observée | Patch proposé, après GO seulement | Oracle / coût |
|---|---|---|
| Ancien historique : `calibrate` calcule `started` sur **tous** les events quand aucune référence n'est qualifiée | Pour qualifier « en cours », examiner les events de l'épisode courant à partir de `started_at` et leur provenance pertinente ; conserver l'ancien historique intact pour une réutilisation actuellement reconfirmée. Ne pas effacer les signaux de préoccupation historiques ni autoriser une reprise non admise | Anciennes tentatives seules → NEEDS_CALIBRATION/null ; familiarisation/tentative courante → IN_PROGRESS ; ancien réglage reconfirmé et accepté dans l'épisode → référence provisoire si toutes conditions restent acquises. Pas de TTL |
| `verify_evaluation` compare des dict Python : `False == 0`, `28 == 28.0` | Définir une comparaison canonique sensible aux types sur toute l'enveloppe, réutilisant validation récursive et sérialisation canonique ; politique numérique explicitée (pas bool/int) | Bool remplacé par nombre refusé ; permutation événementielle sémantiquement identique conserve empreinte/rejeu ; résultat retourné reste le recalcul canonique |
| Temps : `_basis_issues` bloque l'agrégation entière si une borne haute manque | Séparer une borne basse justifiée du besoin d'une borne haute complète ; uniquement composants disjoints sourcés/applicables ou union sûre. Garder UNKNOWN de Duration et aucune affirmation positive si high manque | Basse suffisante peut réfuter cette seule configuration ; couverture partielle, chevauchement ou source inconnue n'autorise aucune somme naïve. Le plancher de repos existant reste disponible |

Ce sont des designs, pas des fixes appliqués. Le troisième durcissement améliore une réfutation, pas une preuve positive ; il ne doit pas retarder artificiellement C6 si aucune source basse utilisable n'existe. Le premier est une correction sémantique exigée par C3 ; le deuxième est requis avant qu'un adaptateur utilise l'enveloppe comme preuve de confiance.

### D3 — Contrat successeur proposé, sans schéma écrit

Nom de travail : `first-plan-recommendation/2.0.0` et contrat request/binding successeur à définir ensemble en apply approuvé. Ce numéro est **proposé**, aucun modèle exporté/servi.

- Conserver les cinq faits requis, provenance/UNKNOWN/WITHHELD, fingerprint de snapshot et empreinte de décision complète ; ne pas changer BodyTrainingBlueprint v1 pour importer un historique caché.
- Décrire les quinze zones avec rôles, base, inconnus et portée ; séparer `coverage_report_complete` (quinze lignes sans omission) de la complétude **numérique**. Aucune absence recensée ne signifie zéro physiologique. UNKNOWN reste UNKNOWN. Le détail numérique facultatif exige sa convention/version admise, jamais une fraction de croissance G17.
- Prescription à union explicite : **bootstrap admis** sans kg froid mais étapes exécutables/familiarisation/essai/arrêt et temps couvrant cette phase ; ou **réglage observé accepté** avec appareil/réalisation/côté/unité et référence de tentative. Le mode non massique n'est plus un NOT_DEFINED vaguement exécutable. Les réalisations unilatérales restent bloquées sans contrat d'appairage admis.
- Garder allocation revue, cadence exacte, compatibilité effective CONFIRMED/NOT_REQUIRED, exclusions, limitations, effort cible distinct de RIR observé et réponse individuelle NOT_ESTIMATED comme conditions strictes.
- Temps : faire porter **nature de base** (modèle validé / convention produit explicitement admise), domaine d'applicabilité, version, provenance, borne et limites. Une convention n'affirme pas probabilité personnelle ni validation scientifique. Sans modèle/convention admis applicable et borne haute couvrant toute préparation/activité/opérations dans budget : pas READY.
- L'état READY signifie autorisation d'exécuter ce protocole initial borné ; il ne signifie ni calibration déjà faite, ni volume optimal, ni prévision individuelle validée. Une évolution de sens est exposée pour revue, jamais projetée en READY v1.
- Le futur validateur recompose registres/politiques/versions/digests et applique les six gates ; ni un JSON conforme ni le champ APPROVED ne crée l'autorité. Versions inconnues/ref retirée → rejet/invalidation. Les statuts transport/produit proposés par PLAN ne sont pas ajoutés implicitement aux enums SCI v1.

### D4 — C6, sortie C retenue comme proposition

Le [protocole temporel](../../../../docs/science/sci-p02-initial-policy/admission-system-01/TIME_PROTOCOL.md) définit collecte, segmentation, analyse et règles de promotion. Ni étude existante ni 1060 secondes synthétiques ne soutient la durée personnelle d'une première séance. La collecte nécessite environnement autorisé, participants/consentements et préenregistrement ; aucune de ces ressources n'est présumée disponible.

### D5 — Design de build isolé concret, à autoriser séparément

**Étape 1 autorisable même sans preuve positive : corrections + mécanisme de refus/admission isolé, aucun READY.** Les racines sont dans `load_calibration.py`, `v2_producer.py::verify_evaluation` et `session_time.py`, mais le choix de compatibilité proposé est de laisser leur chemin historique 2.0.0 intact : nouveaux modules `admission_calibration.py` et `admission_time.py` reprennent les transitions/agrégations pertinentes sous versions successeurs explicites, et `admission_system.py` impose la comparaison sensible aux types après recomputation historique. Tests dédiés `tests/test_science_initial_policy_admission_system.py`. Le consommateur d'admission utilise ces corrections pour son évaluation propre et n'annonce pas que les réponses historiques ont été corrigées en place. Le builder doit arrêter et faire trancher toute incompatibilité de cette préservation avant apply. Aucun remplacement de la politique 0.3.0 ou de ses fixtures n'est autorisé.

Nouveaux modules proposés, exclusivement isolés :

- `tools/science_initial_policy/admission_registry.py` : `load_admission_registry(root)` charge un nouvel inventaire immuable/piné dédié, distinct de `v2_registry`. Il refuse dérive de fichier/matériel, références inconnues, statut ou reviewer absent, entrée révoquée et mismatch d'engine/code SHA/policy/bundle/effective-science/contrat. Le registre initial contient **zéro binding admis** ; une définition de structure ne crée pas une admission.
- `tools/science_initial_policy/admission_system.py` : seul consommateur scientifique de ce registre à cette étape. `evaluate_admission(evaluation_request, evaluation_result, trusted_v2_bundle, trusted_admission_registry)` vérifie d'abord le vrai résultat par recomputation, puis C1..C6 et leur applicabilité. Résultat isolé `initial-policy-admission-result/1.0.0-proposed` : références/digests, verdict par gate, blockers, sans `candidate_plan` ni transport servi. Avec registre vide ou gates ouvertes : NOT_ADMITTED. Aucun `approved_policy_refs` du v2 actuel n'est injecté ou substitué.
- `tools/science_initial_policy/admission_system_fixtures.py` : génération déterministe des refus/invalidation/replay depuis ce vrai consommateur. Aucun cas positif n'emploie une autorité de test comme entrée admise livrée. Une fausse autorité peut seulement exercer son **rejet**.
- Artefacts futurs dédiés dans `admission-system-01/` : `registry.v1.json` (vide tant que pas d'admission réelle), `registry-manifest.v1.json`, `admission-result.v1.schema.json`, `producer-fixtures.v1.json`, manifeste des sources/code et reçu de décisions. Ces noms sont des cibles de build proposées ; aucun de ces JSON n'est créé dans la présente passe.

Les tests d'étape 1 couvrent le registre vide, les six gates négatives, les trois corrections, intégrité/types, changement de source/version et conservation des artefacts anciens. Ils peuvent tous passer **avec NOT_ADMITTED** ; ce succès ne clôt pas C6.

**Étape 2 conditionnée par preuve et choix de contrat : binding exécutable et fixture réelle seulement après admission.** Ajouter un producteur successeur/version de policy propre, références de contrats et fixture générée avec le vrai validateur retenu. Il consomme exclusivement le binding admis de `admission_registry` et sa règle d'applicabilité, jamais un dictionnaire caller labellisé APPROVED. Les champs de l'entrée sont : ID/version/status de décision, C1..C6/reviewers/date/limites, engine et code SHA, policy digest, source manifest/evidence refs, bundle/effective-science, contrat request/result, domaine population/réalisation/temps, déclencheurs de retrait. Les reviewers et leur autorité sont une décision humaine enregistrée dans le dépôt ; aucun faux mécanisme de signature cryptographique n'est présumé.

Un retrait crée une révision/version d'autorité distincte, préserve l'ancien reçu et bloque les nouvelles décisions ; il ne réécrit pas les faits d'entraînement. Le futur adaptateur PLAN ne reçoit qu'une sortie de ce producteur réellement admis et vérifie owner/consentements/transport dans son propre change. Il ne lit pas directement `registry.v1.json` pour fabriquer READY. Aucun nom de version future, hash non encore produit ou proof fixture n'est traité comme livré.

La préparation documentaire et chaque apply futur respectent **un change = une PR** : cet enfant SCI s'ouvre/livre séparément des quatre autres propositions, après sa revue ; pas de PR multi-changes ni archive anticipée du parent.

## Ownership and integration

| Surface | Propriétaire / frontière après GO |
|---|---|
| Ce change + admission-system-01 | SCI, immédiatement documentaire |
| Futur registre/binding successeur, producteur d'admission, tests isolés dédiés | SCI, fichiers exacts à approuver ; nouveaux artefacts dans ce dossier, anciens v1/calibration-time/curation/pull figés |
| `tools/science_contracts/`, contrats SCI exportés | SCI sous revue de contrat explicite, jamais par PLAN en concurrence ; nouveaux modules/versions plutôt qu'amendement silencieux v1 |
| `FirstPlanClient`, types/adaptateur serveur/mobile, API/snapshot | PLAN `blueprint-first-session-runtime` ; reçoit le contrat et implémente ses vérifications après admission |
| Consentements, body_profile, data retention | DATA ; aucune nouvelle chronologie corporelle |
| Tests physiques/builds/rollout | RELEASE ; aucune recette revendiquée ici |

Ordre : revue du dossier → décisions/GO borné → correction C3 et intégrité → preuve/choix C6 → contrat et admission du bundle exact → vrais tests/fixture générée → handoff PLAN. PLAN peut designer en parallèle mais ne s'active pas contre un binding proposé. E0/catalogue, sorties historiques, registres et fingerprints existants restent inchangés. Aucun fichier n'a deux writers.

Le builder historique de séance n'est pas un protocole SCI : `session_builder.instantiate_session` ajoute par défaut deux warmup rows au premier exercice et `max(1, warmup_sets-1)` aux suivants ; même `warmup_sets=0` laisse donc des rows aux suivants. PLAN doit mapper explicitement préparation/calibration admises vers les rows et préserver prescrit/exécuté. Ni ces nombres 2/1 ni le paramètre 0 ne constituent une règle scientifique ou une désactivation garantie. Aucun changement de ce builder n'est fait par SCI.

## Risks / Trade-offs

Le choix v2 coûte une migration consumer, mais rend explicite le changement de sémantique. Autoriser un bootstrap non temporalisé déplacerait l'incertitude à l'utilisateur ; il reste bloqué. Choisir uniquement les sept réalisations bilatérales qualifiées limite la portée sans exiger les quatre pull retenus ni un inventaire. Une collecte sur seuls pratiquants familiers ne validerait pas le novice ; une simple moyenne de temps ne fournirait pas sa borne prédictive.

## Migration / Rollback

Versionner côte à côte ; conserver rejeux, pins et anciennes réponses. L'autorité future doit pouvoir être retirée pour de nouvelles décisions sans réécrire les séances historiques. Retrait de policy/temps/consentement/contexte incompatible invalide la recommandation avant création de séance ; l'idempotence et le traitement d'une séance déjà créée appartiennent à PLAN. Aucun flag ni endpoint n'est changé ici.

## Open Questions

Décisions opérateur/science manquantes : choix du contrat option 1/2 ; validation des conventions exactes C1/C2 et procédure bootstrap C3 ; route temporelle A/B/C et, pour A, tolérance de dépassement/couverture/plan d'échantillonnage préenregistrés par responsable scientifique ; protocole et moyens de collecte autorisés ; GO BUILD borné. Les preuves manquantes ne se résolvent pas par un simple GO. Le choix de charge froide, des quatre pull retenus et un nouvel inventaire de salle ne sont pas des décisions à redemander.
