# SCI-RUNTIME-01 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Lever le refus éditorial du catalogue sans perte d'autorité et fournir une qualification Linux conservatrice, sans activation.

**Architecture:** Un parseur spécialisé parcourt le JSON complet attesté et ne matérialise pas les seules notes de curation. Une méthode SourceView dédiée raccorde les quatre consommateurs existants. Un harness externe examine racines/empreintes/runtime et conserve HOLD si la campagne fidèle manque.

**Tech Stack:** Python3.11, stdlib, FastAPI/Pydantic existants, pytest, SQLite.

**Spec:** `openspec/changes/sci-runtime-01/BUILD_AMENDMENT.md` et `BUILD_AUTHORIZATION.md`.

## Global Constraints

- Source complète hashée, seules `records[*].exercise_operational.curation.notes` omises.
- JSON entier,4096 autres chaînes, profondeur16, tokens65536,128sources/16Mio et tous autres plafonds inchangés.
- Aucun writer, politique SCI, TIME-01, source historique, mobile, Dockerfile/workflow ou VPS changé.
- Runtime Linux exact non disponible = HOLD ; aucune fixture ou CI3.11.18 ne vaut qualification3.11.14.
- Sources partagées uniquement celles de l'amendement ; registre documentaire additif.
- Livraison autorisée après gates complètes ; commit de merge gardé sans bypass.

## Review Focus

- Unicode/échappements et doublons dans la note opaque : valider sans matérialiser ni masquer une syntaxe invalide.
- Nombre/exposant non fini, profondeur et tokens sur tout le document : même refus hors exception.
- Source ou digest changé, fichiers symlinkés et dépassement partagé : pas de confiance depuis la seule vue projetée.
- Résolution Legacy et V3 après omission : alias, rôles et exécutions/digests intacts.
- Harness sur Mac, racine modifiable ou mauvaise cible : verdict HOLD, jamais QUALIFIED par défaut.

### Task 1: Catalogue strict et raccordement des autorités

**Files:** Create `app/services/muscle_observed_load/catalogue_source.py` et `tests/test_muscle_observed_load_catalogue_source.py`; Modify provenance.py, projection.py, supervisor.py et tests/test_muscle_observed_load_provenance.py.

**Interfaces:** `project_catalogue(raw: bytes, expected_digest: str, limits: ReadLimits) -> CatalogueProjection` avec document, source_sha256 et omitted_paths. `SourceView.catalogue_view() -> CatalogueProjection`. Consumers lisent `.document` ; le digest reste celui des octets complets.

- [ ] Écrire un test contre le vrai catalogue exigeant la vue sélective et le digest complet ; le faire échouer sur l'absence de capacité (message explicite, pas erreur de collecte).
- [ ] Implémenter le scanner borné sans dépendance ; raccorder les quatre lectures.
- [ ] Tester : frontières4096/4097 des champs retenus, note4302, Unicode/escape, doublons, types/chemins, faux digest, JSON tronqué/suffixe, profondeur/tokens/source.
- [ ] Retirer le port synthétique de la parité v2 ; tester vraies résolutions et bundleinventory2 sous budget commun, V3/extension compris.
- [ ] Vérifier le scope puis tests ciblés/broad du lecteur et consommateurs SCI ; consigner RED/GREEN.
- [ ] Commit après vérification et revue de l'ensemble, selon le gate de livraison du repo.

### Task 2: Harness de qualification conservatrice

**Files:** Create `tools/muscle_observed_load_qualification.py`; Modify `tests/test_muscle_observed_load_worker.py`, `tests/test_mobile_muscle_observed_load.py`; docs du scope.

**Interfaces:** CLI d'observation avec arguments explicites de source/bundle/profil/DB/preuve Linux, sortie JSON bornée, non secret, aucune mutation/activation. Fonctions pures d'admission de preuve et parcours sûr par descripteurs de répertoires fiables. Aucun patch du loader produit.

- [ ] Test RED : hôte non Linux et preuve absente restent HOLD, dossier symlinké/modifiable et digest faux refusés ; flags de succès d'une fixture ne qualifient pas une cible.
- [ ] Implémenter inventaire OS/Python/SQLite/rlimits/confiance/empreintes et décision conservatrice ; réutiliser les témoins worker existants sous leurs limites et conserver leur portée.
- [ ] Vérifier cinq paramètres HTTP de chemin refusés ; compte/profil serveur seul.
- [ ] Diagnostiquer Docker en lecture bornée ; campagne fidèle si disponible, sinon relever chaque mesure non exécutée et conserver HOLD. Aucun autre environnement sans autorisation distincte.
- [ ] Tester le harness et consigner le profil/limites exacts sans fabriquer de profil opérationnel.
- [ ] Commit après gates de l'ensemble.

### Task 3: Revue, livraison et closeout

**Files:** OpenSpec et `docs/science/sci-runtime-01/`, registre, seuls fichiers précédents pour corrections in-scope.

- [ ] Exécuter check_scope, Ruff neuf/budget, Bandit, protocole/OpenSpec, broad requis, Gitleaks pertinent. Pas de sweep local systématique pour shared_code.
- [ ] Revue indépendante du diff entier ; corriger Important par contre-exemple RED→GREEN, consigner limites/minors.
- [ ] Publier une PR du seul scope ; vérifier quatre checks protégés et Sonar réel au HEAD exact, merge gardé sous GOV-MERGE-01.
- [ ] Vérifier CI canonique, archiver via CLI, closeout et nettoyage borné après sauvegarde/ancestralité/zéro travail unique.
- [ ] Reçu séparant catalogue/parité/sécurité/runtime/lecteur global, avec une prochaine action. Aucun effet OPS/DATA/release.

## Brainstorming / Options / Risques / Choix retenu

Analyse et alternatives déjà approuvées : vue sélective avec digest intégral, lecture incrémentale intégrale insuffisante, hausse de plafond écartée. Choix conservateur : conserver tous les champs non éditoriaux et la validation entière, qualification autonome distincte du code livré. Risque : CPU/mémoire du scanner ; preuve Linux requise, jamais contournée.

## Self-review et décisions d'exécution

Toutes les exigences de l'amendement sont rattachées à Task1/2/3. T1 catalogue_view est consommée par les quatre points, T2 ne change pas les contrats. Exécution inline demandée par continuation autonome ; pas de nouvelle revue de plan opérateur. Les étapes de commit restent soumises aux contrôles complets du repo. Le ledger du change conserve les résultats et décisions.
