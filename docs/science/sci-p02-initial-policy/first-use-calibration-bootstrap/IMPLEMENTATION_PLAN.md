# First-use calibration bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Livrer le pilote SCI isolé accepté, depuis zéro réglage vers une observation qualifiable, sans modifier le binding V3.
**Architecture:** Contrat de rencontre autonome et noyau pur déterministe ; frontière publique conditionnée à une nouvelle autorité réelle. Qualification indépendante des conditions C3, puis pont de tests vers vrai V3.
**Tech Stack:** Python/Pydantic2/pytest existants, JSON SHA256 ; aucune dépendance nouvelle.
**Spec:** openspec/changes/science-first-use-calibration-bootstrap/design.md et TEST_SPEC.md de ce dossier.

## Global Constraints
- Pilote leg-extensions-assises bilatéral seulement ; aucune charge/incrément/temps inventé.
- Contrats/validateurs/pins historiques immuables ; aucun app/API/SDK/DB/UI/activation.
- Types stricts, provenance/ordre/identités/exhaustivité connus ou inconnus conservés.
- Preview DRAFT_EVALUATION_SYNTHETIC_NOT_AUTHORITY ; admission effective sous revue SCI avant permissions publiques.
- GO reçu « Valider le pilote et son build isolé » ; GOV-MERGE-01 permanent, pas GO de déploiement.

## Review Focus
- Arrêt libre versus échec/inconnus : ne jamais traduire False en null pour poursuivre (Task2).
- Préoccupation dans un prédécesseur : nouvel ID ne remet pas le ledger à zéro (Task2).
- Fait enregistré tardivement : familiarisation réellement antérieure, pas simple ordre des lignes (Task2).
- Modèle Pydantic copié/bool/NaN ou payload autre propriétaire : revalidation récursive stricte (Task1/2).
- Autorité/manifest/code altérés : aucune permission depuis schéma/preview/hash caller (Task3).

## Task 1: Strict encounter exchange
**Files:** tools/science_calibration_bootstrap/{__init__,contracts}.py ; tests/test_science_calibration_bootstrap_contracts.py.
**Interfaces:** EncounterRequest/EncounterResult, validated_input(raw), input_digest(request). Réutiliser V3Record/Fact/ContextKey/Setting/Episode.
- [ ] Tests B01/B02/B10/B18 : contrat sans setting/épisodes valide ; contexte autre owner, dates futures, bool/NaN/copies altérées rejetés.
- [ ] Observer RED de module absent, implémenter types et cohérence temporelle/identité ; GREEN ciblé.
- [ ] Commit du contrat avec tests, autorisation et préparation admises comme préparation, pas autorité positive.

## Task 2: Candidate encounter and qualification
**Files:** tools/science_calibration_bootstrap/evaluator.py et validation.py ; tests/test_science_calibration_bootstrap.py.
**Interfaces:** compile_candidate(raw, historical_registry) -> EncounterResult non autoritaire ; evaluate(raw, authority=None) -> EncounterResult ; validate_result(raw,response,authority=None) retourne résultat recomputé.
- [ ] RED B03–B09/B11–B15 : zéro→familiarisation→essai→observé→accepté ; manque réglage n'interdit pas lecture, aucune charge créée.
- [ ] Implémenter noyau partagé, permissions distinctes et qualification indépendante, causes d'arrêt sourcées ; pas import de helper privé comme autorité.
- [ ] Cas adverses/futurs/copied/concern/global ledger/retrait et bridge réel V3 avec données synthétiques explicites ; GREEN ciblé.
- [ ] Revue SCI fraîche du protocole opérationnel, types/code candidat et preuve ; corriger Important avec RED→GREEN ; aucune admission anticipée.

## Task 3: Reviewed publication, public evaluator and delivery
**Files:** tools/science_calibration_bootstrap/{policy,artifacts}.py ; authority/{registry,sources}.v1.json et protocole/admission/revue, exports/manifeste/fixtures ; tests dédiés.
**Interfaces:** load_authority(root=ROOT) -> EncounterAuthority réellement pinée ; assert_authority ; export_artifacts(root)/verify_artifacts(root).
- [ ] Tests RED B16/B17 : vrai loader/altération/retraits/version/recomputation, exports reproductibles et positif public seulement après revue effective.
- [ ] Publier politique limitée si revue défendable, son scope/retrait/provenance ; compiler artefacts via vrai évaluateur public, jamais autorité de test.
- [ ] Tests ciblés et broad des consommateurs scientifiques selon check_scope, Ruff neuf/budget/Bandit/Gitleaks/protocole/OpenSpec, conservation des sources historiques.
- [ ] Revue code fraîche whole-branch ; une passe de corrections Important RED→GREEN et broad si changements.
- [ ] CI réelle du HEAD final, PR/merge commit gardé, CI canonique/Sonar réel, closeout/archive séparés, nettoyage après absence de travail unique.

## Self-review
Les18cas couvrent les trois tâches ; entrée/sortie/policy partagent des types uniques. Registre de rencontre distinct du registre de plan, pas de migration. Contrat livré seulement sous le GO reçu ; publication d'admission peut rester refusée si la revue scientifique ne la défend pas.
