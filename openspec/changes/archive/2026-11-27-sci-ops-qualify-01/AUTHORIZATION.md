# Autorités et leases — 27 novembre 2026

Mandat reçu : **SCI-OPS-QUALIFY-01 / Exact Deployment Package & Trusted Operational Runtime**, conversation opérateur du27novembre2026.

Autorisé maintenant : réconciliation, analyse, préparation locale avec les outils déjà admis, preuves privées, proposition exacte d'opérations nouvelles. Non autorisé par ce mandat seul : nouveau build cloud, transfert/load et nouveau banc distant lorsque ces opérations dépassent les GO antérieurs. Le mandat exige de présenter leur delta exact et d'arrêter l'action dépendante.

**État : PREPARATION_AUTHORIZED / CLOUD_TRANSFER_NATIVE_LAB_GO_PENDING / QA_ACTIVATION_NOT_AUTHORIZED.**

Scope SCI03 clos/#452/#453 ; FILE_LEASES.json archivé indique RELEASED_AFTER_CODE_MERGE. Nouvelle branche `spec/sci-ops-qualify-01`, parent1ac401f. Leases de cette passe : seulement `openspec/changes/sci-ops-qualify-01/**`, ses documents de sortie et preuves privées `/Users/martinfeldmann/auren-review/sci-ops-qualify-01-evidence-20261127`. Aucun lease pris sur app, tests, tools, deploy, CI, mobile ou service distant.

GOV-MERGE-01 acquis pour les seuls périmètres autorisés ; ni build cloud ni self-approval GitHub ni activation n'en découlent. Finding Sonar `AaIXJeDDSfdp1gNdbPO0`/pythonsecurity:S8707 conservé OPEN selon le dernier reçu SCI03 ; statut vivant à relire avant conclusion sécurité, aucun changement d'issue proposé.

## Acte opérateur reçu ensuite — 27 novembre 2026
Pièce jointe `ba2a5305-a9da-4459-84fd-3ab2cb2de8a7/Pasted text.txt` : « J'autorise le périmètre décrit dans OPERATIONAL_DELTA.md du 27 novembre 2026 ». Original et SHA256 conservés dans `execution-20261127/OPERATOR_GO.txt` et `AUTHORIZATION_RECEIPT.json` privés. Le statut préparatoire ci-dessus conserve son instant historique ; le statut courant devient **CLOUD_PRIVATE_TRANSPORT_NATIVE_LAB_AUTHORIZED / GITHUB_APPROVAL_SEPARATE / QA_ACTIVATION_NOT_AUTHORIZED**.

Une tentative PREPARE_IMAGE seulement au SHA1ac401f complet ; pas d'auto-approbation. Avant acquisition/transfert :20Gio libres Mac/VPS,3Gio mémoire VPS, garde et destinations vérifiées. Investigation disque non destructive admise ; toute suppression antérieure doit être précisément inventoriée et soumise à son autorisation applicable. Aucun prune ni modification des conteneurs actifs. Le nettoyage autorisé du futur banc reste borné à ses seuls IDs/labels et preuves conservées.

## DISK AND IMAGE RESUME — acte opérateur reçu
Le message opérateur du27novembre2026 autorise le nettoyage strict des entrées npm/npx/pip inventoriées ; uv seulement via une opération officielle sélective sûre, sinon conservation. Préflight identités, liens et références actives obligatoire ; aucun élargissement. « Aucun second dispatch » est expressément maintenu. Suivi privé distinct demandé pour l'incident de relevé, sans valeur de clé ni révocation arbitraire. Reçu de l'exécution dans DISK_AND_IMAGE_RESUME_RECEIPT.md ; nouveau dispatch non autorisé tant que le delta IMAGE_RETRY_DELTA.md n'est pas accepté.

## Nouvelle intention autorisée ensuite
Réponse opérateur du27novembre2026 à la décision IMAGE_RETRY_DELTA.md : « oui go j'autorise et avance sur ton critical path ». Une seule nouvelle intention au même SHA est donc autorisée, sans modification de garde ni réutilisation de l'approbation erronée. Acte privé `execution-20261127/retry-02/AUTHORIZATION.json` avec empreinte du delta accepté ; préflights et intention durable séparés de la première tentative. L'approbation humaine propre au nouveau run et toutes les frontières QA/SCI/DATA/release restent obligatoires.

## Approbation effective et paquet acquis
Le 27 novembre2026, après le « fait » opérateur, le run45990407820/attempt1 a été relu : approbation réelle MFE-DSS du seul environnement qa-release, commentaire `APPROVE_QA_IMAGE 1ac401f44b8af9444a8521b30cd47b7201fd1c8e`. Les jobs prepare et prepare-qa-image sont completed/success ; release est skipped par le mode PREPARE_IMAGE. Reçu, artefacts, garde privée, archive déchiffrée et image chargée concordent sur la source1ac401f et l’image `sha256:6baa24c49404b2dd8ad74a3d5b4d6f9af3c83c6923a5711a1ae1bf79aebe5e8c`. Aucun nouvel autre dispatch. Le banc neuf `auren-sciops01-4asdnlol-*` est autorisé par les actes précédents ; sa campagne et ses refus sont conservés. L’approbation image ne vaut ni activation QA ni admission DATA.

## GO BUILD AMENDMENT V3 — acte explicite reçu le 27 novembre 2026
L’opérateur autorise « l’amendement de projection du contexte V3 décrit dans BUILD_AMENDMENT.md du 27 novembre 2026, ses trois fichiers de code/tests, ses vérifications et sa livraison sous GOV-MERGE-01 ». Référence : message opérateur SCI-OPS-QUALIFY-01 / GO BUILD AMENDMENT V3 de cette session. Statut courant : BUILD_V3_CONTEXT_AUTHORIZED ; ACTIVATION/DATA/RELEASE/CLOUD_IMAGE_NON_AUTORISÉS.
Lease exact : app/services/muscle_observed_load/provenance.py ; tests/test_muscle_observed_load_provenance.py ; tests/test_muscle_observed_load_writer_readback.py ; documents du change. Parent revérifié par fetch : 1ac401f44b8af9444a8521b30cd47b7201fd1c8e. Les refus historiques et le paquet image restent conservés. Requalification du code corrigé sur banc Linux autorisée ; aucune nouvelle image cloud ni modification du QA.
