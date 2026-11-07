# SCI admission étape 1 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax.

**Goal:** Livrer un consommateur scientifique isolé toujours NOT_ADMITTED, avec trois durcissements réellement consommés et fixtures déterministes de refus.
**Architecture:** Recalculer et vérifier strictement le vrai résultat historique v2, sans changer ses sorties. Évaluer séparément calibration/temps corrigés sous nouvelles versions, puis émettre une décision à six gates depuis un registre vide piné ; aucun résultat historique ou READY n'est fabriqué.
**Tech Stack:** Python3.11+, Pydantic2, pytest, JSON/SHA256 ; dépendances existantes, aucun backend/mobile.
**Spec:** openspec/changes/science-initial-policy-admission/design.md §D5 et BUILD_AUTHORIZATION.md.

## Global Constraints
- Préserver code, sources et fixtures historiques ; nouveaux modules/artéfacts dédiés uniquement.
- NOT_ADMITTED/NOT_SERVED, pas de candidate_plan/READY, registre bindings vide ; autorité de test jamais admise.
- Nouvelle version de diagnostic explicite, aucun contrat FirstPlan v1 modifié.
- check_scope avant checks, ciblés/broad scientifique sans full sweep local ; CI réelle HEAD avant merge.
- Registre root/path/code sourcés/pinés ; modèle construit ou dataclass remplacée ne vaut pas confiance.

## Review Focus
- Ancien événement réimporté après début mais mesuré avant : pas activité courante ; concerns historiques conservés (Task1).
- Basse partielle et chevauchement/unknown/source/scope : réfutation conditionnelle seule, aucune somme injustifiée (Task1).
- JSON bool/int/float, NaN/inf, doublon d'objet, modèle construct invalide : comparaison stricte avant confiance (Task2).
- Registre modifié, binding forgé, provenance/code dérivés : refus sans ouverture d'autorité (Task2).
- Observations modifiées mais Blueprint inchangé, ordre des événements : empreinte complète et rejeu canonique (Task3).

### Task 1: Diagnostics successeurs réellement consommables
**Files:** tools/science_initial_policy/admission_calibration.py, admission_time.py ; tests/test_science_initial_policy_admission_system.py.
**Interfaces:** calibrate_for_admission(episode, *, min_reps, max_reps)->dict ; assess_time_for_admission(session, *, budget_minutes, components, structure, layout)->dict. Réutiliser validation/arithmétique historiques sans modifier leurs modules.
- [ ] Écrire tests échouants : historique seul NEEDS_CALIBRATION ; activité courante IN_PROGRESS ; concern conservé ; réglage comparable accepté conservé.
- [ ] Tester borne basse disjointe partielle, manque haute, source/scope invalide, clock/overlap/unilatéral : aucun faux fit ni Duration.
- [ ] Exécuter RED, implémenter wrappers minimaux, vérifier GREEN ; versions nouvelles explicites.
- [ ] Commit des diagnostics après checks ciblés.

### Task 2: Registre vide et évaluateur strict
**Files:** admission_registry.py, admission_system.py ; même test dédié.
**Interfaces:** load_admission_registry(root=ROOT)->AdmissionRegistry ; assert_trusted_admission_registry(registry)->None ; verify_evaluation_strict(request,result,bundle)->dict ; evaluate_admission(request,result,bundle,registry)->dict.
- [ ] Tester False→0 et int→float refusés (types JSON exacts), NaN/inf/modèle altéré, résultat frais recalculé et entrée non mutée.
- [ ] Tester registry drift, manifest/code drift, binding non vide, registre forgé ou remplacé ; aucune voie positive admise dans cette version.
- [ ] Implémenter validation sensible aux types, vérification du vrai v2 et recomputation des diagnostics successeurs, six gates négatives avec raisons/digests.
- [ ] Exécuter RED→GREEN, vérifier chaque diagnostic nouveau dans la sortie, commit.

### Task 3: Artefacts et livraison du scope
**Files:** admission_system_fixtures.py ; dossier admission-system-01 registre/manifeste/schéma/fixtures/reçu ; tests dédiés ; registry global et change SCI uniquement.
**Interfaces:** generated_cases()->list[dict] ; génération --write explicite et vérification sans writer par défaut, via modèle de résultat exporté.
- [ ] Tester manquant/conflit/suffisant historique/ancien épisode/borne partielle/types/version/source refusés ; résultat propre au sujet/empreintes, pas plan.
- [ ] Générer les artefacts depuis fonctions réelles ; protéger rejouabilité v1/v2 et pins historiques avec tests broad existants.
- [ ] check_scope puis Ruff fichiers neufs/budget/Bandit/protocole/OpenSpec et broad science ; pas de full local.
- [ ] Revue code et science indépendantes, corrections Important RED→GREEN ; commit/push/CI exacte, merge sous GO permanent si readiness acquise.
- [ ] CI canonique, Sonar réel, closeout du seul scope étape1, parent et gates positives ouverts ; nettoyage seulement après intégration vérifiée.

## Rulings
- Les reviewers ont déjà relu le design ; l'opérateur vient d'autoriser ce build borné. Exécution native continue, sans redemander une revue de plan routinière.
- Étape1 est indépendante et s'achève avec un verdict négatif vérifié ; les critères d'admission positive ne sont pas supprimés ni déclarés acquis.
