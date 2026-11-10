# REL-03 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Livrer les outils/configurations vérifiables d'un pipeline Android QA continu, puis soumettre le paquet externe sans publication non autorisée.
**Architecture:** Paquet Python QA autour de la vraie app et de sa façade existante ; reçus stricts et copies SQLite complètes. Nouveau profil QA seul, Expo Updates compatible et workflow manuel protégé, aucun déclenchement de publication au merge.
**Tech Stack:** Python verrouillé/FastAPI/SQLite, Expo SDK58, EAS CLI officielle, GitHub Actions.
**Spec:** openspec/changes/rel-03-continuous-android-qa/design.md + BUILD_SCOPE.md + TEST_SPEC.md + BUILD_AUTHORIZATION.md.

## Global Constraints
- Base b9a334d22e6b75e9b83650eb1b2b833d4ed5d169 ; package dev.auren.releaseqa02 et certificat 12b13109a2a41e2e2c0e97578364793e659a7548da4ce210d0dbd2f912f4bc75 conservés.
- Version proposée 0.0.2/versionCode3, canal qa et branche qa, Android uniquement ; profils historiques/pilot conservés.
- Aucun changement du banc QA02 vivant, aucune donnée personnelle, connexion fournisseur, cloud-spend, cutover, build cloud ou publication APK/OTA autorisés.
- Copier DB entière via SQLite backup, jamais restore JSON legacy/écrasement source ; head plan_v3_20261107_01, un writer, vrai SCI et génération courante.
- Source native distincte de source JS ; métadonnées volatiles hors config native/fingerprint ; fingerprint standard sans exclusions permissives.
- Observer sans UI limité à ConnectedApp ; ne pas modifier ses fonctionnalités ou ses contrôleurs.
- check_scope avant vérifications ; full sweep local seulement via scripts/run_local_sweep.sh si tier requis ; CI réelle obligatoire et merge gardé sous GOV-MERGE-01.

## Review Focus
- Un démarrage ou rollback avec DB réutilisant les identités d'un autre environnement doit être refusé, pas réparé par seed.
- Une sauvegarde interrompue/corrompue ou une destination existante conserve la source et ne laisse pas une copie acceptée.
- Health et version distinguent processus sain et autorité retirée ; aucun cache de génération de démarrage présenté comme courant.
- Changement natif ou schéma local, SHA sale, cible non attestée, approbation absente : refus de publication/OTA.
- Observation QA sous compte A/B ne collecte aucun owner/token ni fait et reste absente des profils historiques.

### Task 1: Paquet serveur portable et sauvegardes complètes
**Files:** Create tools/qa_delivery/__init__.py, identity.py, database.py, server.py ; tests/test_qa_delivery_server.py et tests/test_qa_delivery_database.py ; deploy/qa/Dockerfile et README.md. Les responsabilités peuvent rester dans ces quatre modules sans second domaine métier. Gateway QA02 et runtime SCI sont read-only.
**Interfaces:** identity.read_version(db_path: Path, *, environment_id: str, source_sha: str, bundle_root: Path) -> dict ; database.backup_database(source: Path, destination: Path) -> dict ; database.verify_database(path: Path) -> dict ; server.create_qa_app(config) -> ASGI app, façade bornée vers upstream loopback fixe. CLI python -m tools.qa_delivery.server ; copie/restauration CLI via database. Pas de démarrage live par import.
- [ ] RED : tests sur vraie SQLite temporaire head exact, FK, toutes tables/copies et source inchangée ; destination existante/DB corrompue/head inconnu refusés. Tester interruption/nettoyage atomique et backup/restauration en nouvelle copie conservant rows/IDs/refresh/PLAN, sans imprimer secrets.
- [ ] RED : GET /__qa_health et /__qa_version sans identité privée ; génération lue à chaque requête puis retrait visible ; santé DB/schéma/bundle défaillante =>503 sans secret ; wrapper conserve allowlist QA02 et bloque web/admin/email réel, arrêt/upstream indisponible honnêtes.
- [ ] check_scope puis tests ciblés via venv Python PYTHONPATH=. ; enregistrer RED réel avant implementation.
- [ ] Implémenter fonctions/CLI et conteneur portable : app canonique loopback + façade publique supervisées ; configuration synthétique explicite, refus des flags corporels/SMTP/Sentry/log SQL, secrets par référence privée, jamais seed/migration automatique de DB existante. Nouveau service non lancé ici.
- [ ] GREEN ciblé puis broad gateway/config/packaging/identité pertinents, ruff fichiers neufs/budget/protocole ; rapport et commit des seuls fichiers du task après checks. Aucun Docker build si espace/mémoire menacent le banc ; consigner indisponibilité et poursuivre tests ASGI/subprocess isolés.

### Task 2: Reçus de release et profil mobile compatible
**Files:** tools/qa_delivery/releases.py ; tests/test_qa_delivery_releases.py ; clients/mobile/qa-delivery.config.js et qa-delivery-target.json ; app.config.js/eas.json/package.json/package-lock.json ; src/native/qaDelivery.ts, qaDeliveryMetadata.ts et tests ; ConnectedApp.tsx observer seulement.
**Interfaces:** validate_candidate(raw, evidence) -> normalized dict ou refus fermé ; classify_update(before, after) -> JS_ASSETS_ONLY|NEW_APK_REQUIRED|UNAVAILABLE. Observer capture native version/runtime/updateId/isEmbeddedLaunch et SHA JS, aucun owner/token.
- [ ] RED : candidat incomplet/sale/non fusionné/CI rouge/signature/code réutilisé/cible tunnel-production non attestée rejetés ; inconnus restent pending et non distribuables. Versions API/SCI/DB doivent être explicitement compatibles, pas heuristique >=.
- [ ] Installer expo-updates SDK58 avec CLI Expo officielle et expo-application au verrou compatible ; utiliser eas update:configure Android dans contexte nouveau profil seul, inspecter diff et préserver anciens profils. Pas d'update/build/publication.
- [ ] RED puis GREEN : helper nouveau profil résout uniquement cible HTTPS stable attestée, refus placeholder/temporaire/production ; config qa-android et pilot inchangées. Source JS volatile n'entre pas dans extra natif ; fingerprint standard vérifié expérimentalement sur JS seul puis module/config natif modifié en copie.
- [ ] Brancher observer seulement pour nouveau profil dans vrai ConnectedApp ; tests consommateur non-QA sans effet, A/B sans données collectées, champs native et JS distincts. Canal qa/branche qa configurables sous GO, toute mutation distante réellement effectuée consignée ; aucune publication.
- [ ] Tests node/Jest/TypeScript, export Android local si ressources disponibles ; enregistrer limites sans APK fictif.

### Task 3: Orchestrateur manuel et livraison préparatoire
**Files:** .github/workflows/qa-release.yml ; tools/qa_delivery/pipeline.py et bootstrap.py ; tests/test_qa_delivery_pipeline.py et test_qa_delivery_bootstrap.py ; deploy/qa/render.yaml/Dockerfile/README.md ; server.py liveness seulement ; docs/release/rel-03/ et change/registre append.
**Interfaces:** préflight SHA/CI/base/receipts/target ; prepare sans secrets produit candidat NON_DISTRIBUTABLE ; build/update/rollback exigent environnement réellement protégé qa-release et décision externe applicable.
- [ ] RED : dispatch absent/approbation manquante, environnement sans reviewers, credentials absents, branche/channel/runtime différent, update rollout inconnu => aucune action publiant ; prepare fonctionne sans secret.
- [ ] Implémenter workflow dispatch uniquement, permissions minimales, SHA exact, environnement qa-release pour opérations publiantes ; aucun push/PR/merge trigger de distribution, aucun compte/protection/secret créé automatiquement. Éviter scripts publiants utilisables sans préflight.
- [ ] Compléter blueprint portable et opération exacte/coût/région/credentials/continuité/rollback à approuver ; health/probe/backup en copie sur banc jetable, pas transfert live. Prévoir bootstrap de maintenance explicite : liveness200/data_ready=false, tout mobile503, pas DB/secret/serveur canonique créé. Marqueur privé issu du futur cutover approuvé puis validation complète et redémarrage du même artefact avant exec superviseur. Ajouter seul endpoint liveness au server actif, health/version inchangés ; tests vrai ASGI/execfactice à port jetable, aucun liveQA02. Voir PROVIDER_BOOTSTRAP_NOTES.md hors dépôt pour sources et motif ; ne pas ouvrir un serveur de fichiers ni seed une DB à la première installation.
- [ ] check_scope puis contrôles requis, sweep local borné si ci_infra, revue indépendante et corrections scopées ; quatre checks CI HEAD exact obligatoire, Sonar réel.
- [ ] Commit/push/PR/merge gardé après readiness, vérifier CI canonique et closeout du code livré. Ne pas archiver comme pipeline COMPLETE : cible stable/nouveau APK/update réel restent bloqués par décision externe.
- [ ] Soumettre un seul paquet externe concret ; préserver QA02 et worktrees produit. Aucun GO merge supplémentaire.

## Self-review et séquencement
Task1 produit les primitives lues par Task2/3 ; Task2 et Task3 partagent seulement le contrat candidat, sous séquence et review. Aucun fichier Today/Progrès n'est dans le diff fonctionnel REL03. Le lease ConnectedApp observer est séquencé avant futures PR MOB04/MOB05 ; leurs builds reliront le canonique après merge REL03. Approbations externes sont les seules opérations dépendantes laissées ouvertes, sans date/URL/artefact inventés.

### Task 4 — Transport privé chiffré des preuves (correction de préparation)

**Motif constaté10novembre :** repo produit PUBLIC selon l'API GitHub ; aucun producteur qa-continuity-proof n'existe. Un `gh run download` seul n'est pas un workflow de préparation et des DB/auth en artefacts publics ne constituent pas un transport privé. Aucun upload de cette nature n'a été exécuté.

**Choix technique dans le GO outils/workflow/backup existant :** outils pack/upload/import d'une archive chiffrée AES-256-GCM avec Node crypto standard (déjà disponible pour EAS, sans dépendance ni lock Python supplémentaire). Stockage futur dans un dépôt GitHub dédié réellement privé, via API/CLI releases/assets supportées ; pas de nouveau fournisseur de blobs/serveur public. La création/connexion de ce dépôt, clé et tokens reste dans l'unique paquet externe, non autorisée par ce plan. Aucun compte privé existant n'est supposé acquis. Le dépôt produit public ne reçoit jamais les fichiers DB déchiffrés ni la clé.

**Files:** tools/qa_delivery/proofs.py et proof_crypto.cjs ; tests/test_qa_delivery_proofs.py ; leases pipeline.py/test_pipeline.py/.github/workflows/qa-release.yml ; docs/release/rel-03 et références de ce change.
**Interfaces:** pack local à clé privée hors source ; upload explicite vers dépôt privé validé, sans overwrite ; import protégé lit asset immuable/ID/checksum puis déchiffre/valide en RUNNER_TEMP privé. Le prepare sans credentials peut figer des empreintes attendues déclarées NON_VERIFIED/NON_DISTRIBUTABLE, jamais les promouvoir en preuve. Seul le job qa-release approuvé accède à la clé/token lecture du dépôt privé, observe réellement repo/asset et recalcule proof_digest pour égalité exacte avec le paquet approuvé, avant pipeline.publish et ses gates existants.

- [ ] RED→GREEN réel pack/déchiffrement Node standard, wrongkey/header/tag/cipher tampering, bornes archive/fichiers, zip traversal/symlink refusés, absence d'overwrite et perms0600/0700, zéro secret imprimé.
- [ ] RED→GREEN uploader/API frontières injectées uniquement, dépôt public/produit/asset faux refusés, repo privé lu réellement au futur acte ; gh release create/upload supportés, aucune publication appelée maintenant.
- [ ] RED→GREEN vrai consommateur workflow/CLI d'import vers pipeline, pas d'uploader inventé `gh run upload`, pas de téléchargement DB depuis artefact du dépôt public, pas de store de secrets utilisé comme transport de base.
- [ ] Approval unique reste candidate/proof digests exacts ; champs de dispatch ne prouvent rien avant readback/decrypt/validation. Aucun bypass GitHub/SCI, aucun nouveau déclencheur automatique ou changement des quatre checks.
- [ ] Tests ciblés+broad sur helpers/pipeline, Ruff/budget/protocol/actionlint et revue fraîche Task4 puis wholebranch ; pleine CI réelle. Aucun full local doublon pendant le sweep root en cours.

**Coût du choix :** connexion future d'un dépôt privé de preuves + clé séparée et token lecture gérés par l'opérateur, en plus de Render. Zéro nouveau secret/compte/spend effectivement créé ici. La création future du dépôt et l'upload chiffré sont des actes externes explicitement soumis au paquet ; source/artifact privé et chiffrement n'accordent pas de permission scientifique. Les limites effectives de la cible/CI/physique restent ouvertes.
