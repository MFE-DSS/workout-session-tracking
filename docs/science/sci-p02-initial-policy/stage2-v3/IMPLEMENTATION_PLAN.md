# SCI-P02 stage2 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement task-by-task, inline. No routine approval between tasks.

**Goal:** Livrer le vrai producteur v3 et une admission limitée effective sous les décisions reçues, sans runtime.
**Architecture:** Registre successeur dédié réutilisant les sources curées pinées ; plan compilé depuis sept contextes réellement observés/acceptés ; validation d’invariants indépendante et recomputation stricte ; positif seulement après revue SCI effective.
**Tech Stack:** Python/Pydantic/pytest/JSON/SHA256 existants, aucune dépendance nouvelle.
**Spec:** openspec/changes/science-initial-policy-v3-producer/design.md et BUILD_AUTHORIZATION.md.

## Global Constraints
- Contrats3, historiques1/2/3, donnéesE0/catalogue, SDK/API/UI/DB restent inchangés. Nouveaux modules dédiés seulement.
- Cas limité adulte déclaré non clinique, hypertrophie, cadence2, limitations[] connues ; sept réglages observés qualifiés/acceptés, aucun bootstrap positif.
-2sets/intention,8–12reps,cible subjective2RIR,120s poly/90s mono : conventions explicitement acceptées, pas optima.14sets/séance,28/semaine.
- TempsUNKNOWN sauf réfutation structurelle ; aucun fit/durée positive. Ack exact pour droit de commencer, aucune activation.
- Aucun label du caller, objet copié ou autorité de test n’admet une politique. Publication ADMITTED uniquement après revue SCI effective et décisions réelles.
- Source/code/policy/autorité versionnés sans cycle de hash ; registre vide et anciens rejeux byte-identiques.
- PLAN prépare sa propre proposition dans un autre worktree sans code/shared writes ; merge SCI sous standing GO seulement après readiness finale.

## Review Focus
- Bool/nonfinite/copies imbriquées, dataclass remplacé et racine source trafiquée ne produisent pas d’autorité.
- Disponibilité seule, contexte/côté différent, ancien import ou acceptation périmée ne prouvent pas une prescription observée exécutable.
- Une préoccupation ou exclusion utilisée contradictoire invalide le positif, même si les faits minimaux suffisent.
- Le producteur peut se tromper : le validateur contrôle allocation/dose/source/zone/temps indépendamment avant comparaison stricte.
- Ack ancien ou retrait de référence ne donne pas droit de commencer ; schema positif, temps et runtime restent distincts.

### Task 1: Registre successeur, sources et doctrine exacte
**Files:** tools/science_initial_policy/v3_admission.py ; docs/science/sci-p02-initial-policy/stage2-v3/authority/ ; tests/test_science_initial_policy_v3_admission.py.
**Interfaces:** V3Registry immuable avec historique V2Registry, policy/binding/sources, digests, statut d’admission et actif ; load_v3_registry(root=ROOT)->V3Registry ; assert_trusted_v3(registry,require_admitted=True)->None. Le loader n’est pas piné par sa propre publication ; artefacts finaux le pinneront.
- [ ] RED : module absent, sources exactes, scope/dose/sept identités/réalisation, refus d’objet caller/tamper/path escape et ancienne autorité vide ; aucun runtime permis.
- [ ] Implémenter loader/candidat de publication ; initialement CANDIDATE tant que revue effective manque, jamais inventer reviewer ou admission.
- [ ] GREEN dédié et autorités historiques ; Ruff/protocole selon tier ; commit avec trailer requis.
Expected: nouveaux tests verts, anciens pins intacts, pas de sortie positive publiée.

### Task 2: Vrai plan v3 et validation indépendante
**Files:** tools/science_initial_policy/v3_producer.py ; tools/science_initial_policy/v3_validation.py ; tests/test_science_initial_policy_v3.py.
**Interfaces:** compile_plan_v3(request,registry)->PlanV2 + tuple[TimeAssessmentV3] ou blockers ; produce_v3(request,registry)->FirstPlanRecommendationV3 ; validate_admitted_exchange_v3(request,result,registry)->FirstPlanRecommendationV3. Réutilise modèles v3/assessment/calibration1.1/matching et rôles curés, pas leur validateur négatif comme autorité positive.
- [ ] RED tests de compilation2×7slots/28sets, réglages/acceptations courants exacts, quinze zones honnêtes, borne750s sous structure liée au binding ; temps inconnu et effet d’ack sur empreintes.
- [ ] RED adverses : 5faits manquants/conflits, cadence3/limitation, exclusion, inconnu/appareil/côté/unité, concern/restart non admis, source/versions/owner/fingerprint et bool/copies.
- [ ] Implémenter pur/déterministe. Tout positif exige assert_trusted_v3(...require_admitted=True). generated_at=max(as_of,acktime), aucune horloge globale ou nouvelle identité persistée.
- [ ] Invariants indépendants d’allocation/dose/refs/contexte/qualification/zone/temps/ack, puis recomputation canonique sensible aux types ; pas validation du schéma seule.
- [ ] GREEN compilation/adverses sous candidat, positif gardé fermé tant que l’admission effective manque ; tests positifs d’autorité à terminer Task3. Commit.
Expected: vrai compilateur testable, pas de succès scientifique depuis statut CANDIDATE.

### Task 3: Admission effective, preuve positive et livraison
**Files:** outils précédents si finalisation de pins ; tools/science_initial_policy/v3_fixtures.py ; tests positifs dédiés ; artefacts/handoff/reçu dans stage2-v3 ; OpenSpec/registre.
**Interfaces:** artifacts()->dict[path,bytes], CLI --write explicite et vérification par défaut ; exports real-producer/synthetic-input/NOT_SERVED, pas de nouvelle fixture d’autorité de test.
- [ ] Revue SCI fraîche du bundle effectif/code/conventions, cas observé, C6 et inconnus. Si non défendable : garder CANDIDATE et rendre le manque précis, pas forcer ADMITTED.
- [ ] Après revue effective favorable et décisions reçues : consigner auteurs/reviewer/preuves, figer sources/code/binding/registre réels. Aucun changement des règles approuvées pour rendre le positif facile.
- [ ] RED→GREEN vraie sortie SCIENTIFICALLY_READY/UNKNOWN/REQUIRES_TIME_ACK puis ELIGIBLE sur ack exact, via vrai loader/producer/validateur. Faux binding/retiré/pins/stale/feasibility fabriqués refusés.
- [ ] Export explicite des seules preuves nécessaires, manifests reproductibles, handoff PLAN complet sans négociation/serveur fictifs.
- [ ] check_scope puis dédié/broad scientifique/historique selon tier, sécurité/protocole/OpenSpec ; revue code fraîche complète sur modèle le plus capable, une passe Important RED→GREEN, mineurs consignés.
- [ ] Commit/push/PR/CI HEAD, merge exactSHA sous GO permanent, CI canonique ; archive/closeout du scope réellement livré, contrôle canonique final et cleanup propre. Préparation PLAN conservée indépendante.
Expected: un positif admis effectif pour le cas observé ou blocker SCI précis ; jamais runtime servi, ancien client inchangé, réception des preuves par PLAN.

## Preflight / choix locaux
Task1 produit autorité et sources pour Task2 ; Task2 code doit être inclus dans le binding final Task3, sans pinner le loader dans son propre digest. Une publication candidate peut évoluer avant sa première admission/publication finale ; aucun ancien hash n’est réécrit. La revue SCI précède le tag effectif et le positif autoritaire, la revue code suit sur le bundle complet. Exécution native poursuit le GO explicite ; les revues et PLAN sont des tâches distinctes déléguées, pas des implementers par tâche.
