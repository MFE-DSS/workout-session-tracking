# MOB-05A — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to execute inline, task-by-task, with a fresh whole-branch review at completion.

**Goal:** Un vrai onglet Progrès natif propriétaire : faits des séances/exercices, fréquence explicite et chronologie BodyMeasurement, sans writer ni analyse de force.
**Architecture:** Quatre GET bornés/read-only et références signées ; client strict et ressource mémoire ; présentateurs natifs communs ; poids via les deux consommateurs existants ; montage séquencé après MOB04.
**Tech Stack:** FastAPI/SQLAlchemy/ZoneInfo et cryptographie stdlib existants ; TypeScript/React Native/SVG existants. Aucune dépendance, table ou migration.
**Spec:** design.md D1–D5, TEST_SPEC.md, BUILD_SCOPE.md, UX_BOARD.md et BUILD_AUTHORIZATION.md de ce change réutilisé.

## Contraintes globales
- GO BUILD et G1 reçus : « Autoriser MOB-05A et valider G1 ». Nouveaux pixels réels iOS/Android encore PENDING avant commit UI.
- Base de préparation b9a334d ; fetch/relecture des merges REL03 puis MOB04 avant montage partagé. Aucune PR chevauchante ConnectedApp/router/registre/inventory.
- Un seul modèle de poids BodyMeasurement, un journal et une identité AuthSession ; aucun writer poids/nutrition ou accord fabriqué.
- SCI producteur/validateurs/bindings historiques read-only. Lecture V3 historique ne monte ni contrôleur actif ni commandes.
- UNKNOWN/partiel/absence/refus distincts ; machine/par haltère jamais total externe ; pas de progression/record/1RM/scores/deltas nouveaux.
- Faits legacy capturés seulement ; aucune reconstruction depuis le catalogue courant. Planning daté non persisté = count null.
- Tous les tests sur bases/comptes synthétiques ; aucune activation DATA, diffusion, OTA, cloud-spend ou déploiement.
- check_scope avant checks. Ciblé et broad consommateurs requis ; pas de full sweep local systématique hors tier l'exigeant. CI réelle HEAD exact, quatre checks requis et GOV-MERGE-01.

## Interfaces retenues pour le build

Serveur nouveau `training_history_reads.py` : `read_sessions(db,owner_id,*,period,time_zone,limit=50,cursor=None,now=None)`, `read_session_facts(db,owner_id,session_id,entry_ref)`, `read_exercises(db,owner_id,*,read_context,limit=50,cursor=None)`, `read_occurrences(db,owner_id,exercise_ref,*,read_context,limit=50,cursor=None)`. Aucun flush/commit. Les références sont signées avec une séparation de domaine dédiée et le secret serveur existant, jamais un secret client ou une nouvelle identité de compte. Les continuations portent owner/read_id/type/fenêtre/plafond et restent des observations bornées, sans prétention de snapshot permanent.

Le détail SCI retourne le refus V1 explicite `execution_profile_required` ; le client utilise FirstSessionV3Client.execution existant et valide ensuite l'identité/binding/topologie/observations typées contre le descripteur de liste. Aucun champ de permission n'est utilisé pour agir. La partie legacy retourne les faits des SessionExercise/SetLog et cardio capturés ; prescription/contexte non capturés restent inconnus.

Client `TrainingHistoryClient(auth,transport,runtimeV3)` et `TrainingHistoryResource` : état mémoire, période/zone/read_id/selection, refresh/next/selectEntry/selectExercise/back/invalidate. DTO stricts avant exposition ; les noms exacts internes peuvent être ajustés au test consommateur sans changement de contrat scientifique. WeightHistoryClient/Resource restent importés sans modification ; filtre/pagination bornée en présentation selon la fenêtre serveur.

## Review Focus
- Références signées : propriétaire consulté avant vérification d'une référence de détail ; étranger/inconnu/owner NULL identiques404, changement de métadonnées possédées409 sans fuite ; aucune réattribution après restauration de PK.
- Fenêtre DST locale et borne until exclusive, classement started_at,id/plafond global ; counts observés séparément des pages live, jamais somme d'une page ou snapshot garanti.
- Completed sans fait n'est pas performed ; warmups/ligne semée ne fabriquent ni fréquence ni charge ; exclusion factuelle distincte du filtre technique SCI.
- Scan index/occurrences réellement borné200/1000, continuation source distincte affichage, PARTIAL_SCAN avec0match n'est pas EMPTY ; pas d'appel V3 par ligne pour dessiner une courbe.
- Détail SCI : setting observé distinct de prescription ; contexte complet exact pour comparabilité ; zéro/null/NaN/type/unité/révision/date/côté/context mismatch doivent rester explicites sans multiplication.
- Compte A/B, sélection/période et refresh concurrents : jamais d'ancienne réponse exposée comme actuelle ; échec pagination conserve seulement lecture précédente du même owner.
- Poids : vrai consentement/flag, measured_at vs recorded_at, même date plusieurs IDs et trous de qualité ; toutes pages requises avant absence, budget1000 avec suite explicite. Aucun modèle de poids parallèle ni consigne nutritionnelle.

### Task 1 — Lectures serveur et route isolée
**Files:** app/services/training_history_reads.py ; app/routers/mobile_training_history.py ; tests/test_training_history_reads.py ; tests/test_mobile_training_history_http.py.
- [ ] Lire les modèles et helpers canoniques, écrire RED sur owner, fenêtres4w/12w/all/DST, keyset/signature/type/plafond et changements de référence ; fixture de router locale seulement tant que lease partagé indisponible.
- [ ] Implémenter lectures sous no_autoflush avec SQL borné/groupé, dates UTC explicites et contexte de lecture signé. Source réelle WorkoutSession/SessionExercise/SetLog/binding ; aucune lecture catalogue pour prescription historique.
- [ ] RED→GREEN counts factuels/sans plan, détail legacy et garde SCI ; index/occurrences avec lots200 et plafond1000, token tampering et injection rejetés, aucune DML tracée.
- [ ] RED→GREEN Bearer/no-store/401/404uniforme/409/422privé/503 explicite. Ciblé et broad sessions/readmodels/provenance/alias/PLAN read guards selon check_scope.
- [ ] Commit des modules propres après tests ; pas de PR ou montage partagé avant merge MOB04.
**Verification:** pytest -q tests/test_training_history_reads.py tests/test_mobile_training_history_http.py ; broad modules canoniques identifiés par imports et consumers, Ruffneuf/budget/protocole/OpenSpec. Expected : PASS, aucun fallback d'autorité ni write.

### Task 2 — Client strict, V3 historique et poids existant
**Files:** clients/mobile/src/api/trainingHistory.ts, trainingHistoryResource.ts et tests ; helper de témoignages synthétiques sous clients/mobile/test si nécessaire.
- [ ] RED propriétaire/période/token/relecture/profil/erreurDTO avant implémentation ; utiliser vrai AuthSession et transports injectés aux frontières réseau.
- [ ] Décodeur supplémentaire V3 read-only recoupe descripteur/binding/session/topologie/setting/unités/contexte/faits ; refus sans fallback V1, aucune commande/permission active.
- [ ] RED→GREEN ressource paging/refresh/partial/error/A-B/logout/requêtes tardives et sélection invalidée409.
- [ ] RED→GREEN réemploi réel WeightHistoryClient/Resource, fenêtre measured_at, pagination jusqu'à borne/épuisement/plafond1000, trous et mêmes dates, consentement/flag/transport séparés.
**Verification:** Jest fichiers nouveaux + broad clients V3/weight/auth ; TypeScript. Expected : PASS, seuls faits confirmés/contextualisés exposés, aucune nouvelle persistance.

### Task 3 — Présentateurs Progrès
**Files:** clients/mobile/src/ui/history/{TrainingHistoryScreen,SessionFactsScreen,ExerciseHistoryScreen,WeightTrend}.tsx ; historyView.ts et tests.
- [ ] RED→GREEN composants réellement réutilisés : période, fréquence étiquetée, sessions récentes, choix d'exercice, chronologie poids et drill-down avec sources/états d'aide.
- [ ] Graphiques RN/SVG déterministes avec liste accessible équivalente ; aucun lien entre charges inconnues/incompatibles, aucun lissage ou interpolation de poids invalide.
- [ ] Une action dominante par niveau, aide sur demande, états vides/partiels/accord requis/offline distincts, texte grossi, safeareas, retour par niveau, pas d'animation requise.
**Verification:** Jest présentateurs + ressources et TypeScript. Expected : PASS ; aucun ajout de couleur/tab/score ou modification de primitive/baseline.

### Task 4 — Montage réel après lease MOB04
**Files:** mobile_api include ; ConnectedApp progress node/refresh/identité ; ShellContext progress ; src/routes/progres.tsx ; tests connectedApp/routes ; MOB00inventory et rendu généré ; registre append.
- [ ] Fetch/relecture canonique frais après merge MOB04, conserver exactement son Today et l'observer QA REL03, un seul journal/sync/compte.
- [ ] RED→GREEN routes réelles/auth/flags, navigation 4tabs et retours, refresh foreground/reconnect sans staleowner ; interface Progrès réelle, pas galerie seule.
- [ ] Monter vraies lectures HTTP synthétiques et consommateurs natifs ; captures iOS/Android small/large/largefont, clavier seulement si sélection le requiert ; équivalence labels/focus/reducedmotion documentée.
- [ ] Un board consolidé avant/après à côté des références acceptées ; source-labels et limites ExpoGo/émulateur/physique explicites. Obtenir pixels opérateur AVANT tout commit UI.
**Verification:** HTTP réel et tests native wiring ; Jest/TS/ciblé+broad/check_scope ; pixels acceptés. Expected : PASS effectivement observés, pas d'acceptation physique déduite.

### Task 5 — Revue et livraison
- [ ] Revue fraîche du diff complet sur modèle le plus capable selon skill, spec/ReviewFocus/rulings/minors ; corriger Critical/Important en une vague RED→GREEN et suites adaptées, mineurs explicites.
- [ ] Tous checks requis HEAD exact, base actuelle/threads/reviews, sécurité/protocole/OpenSpec et Sonar consultatif réel ; aucun skip/seuil changé.
- [ ] Commit UI après pixels, push/PR unique/merge gardé GOV ; vérifier canonique/CI, archive OpenSpec et closeout du scope code atteint, nettoyage sans travail unique.
- [ ] Parité VERIFIED_NATIVE/DOMAIN_ONLY/PARTIAL/NOT_SERVED/BLOCKED reliée à vrais source/artefact/preuves ; QA02 n'a pas reçu ces fonctions avant release distincte. BODY/NUT restent prochaines préparations avec leur GO/gates propres.

## Self-review / décisions de séquence

Préparation du plan seulement à ce stade : aucun module Progress écrit avant sa tâche et RED. Les helpers de signature ne font pas autorité personnelle et n'inventent pas de snapshot. Les propriétés de membership/limites de preuve sont reprises de D1 ; les données quantitatives de D2–D4 restent factuelles. Les phases de montage attendent explicitement MOB04 et son nouveau canonique. La portée de cette tranche ne ferme ni DATA ni la distribution physique, et ne modifie aucune admission scientifique.
