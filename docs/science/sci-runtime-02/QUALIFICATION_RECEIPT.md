# SCI-RUNTIME-02 — reçu expérimental et HOLD prouvé

26 novembre2026 — Europe/Paris. Canonique c454af863278b0801a568437038eb4efb94db588. **Instant expérimental AVANT le GO.** Résultats historiques conservés ; le GO reçu et les essais du correctif sont décrits dans [BUILD_RESULTS.md](BUILD_RESULTS.md). ENDPOINT NOT_QUALIFIED ; QA reste désactivé.

## Environnement réellement exécuté
Docker29.3.1, Linuxkit6.12.76 ; conteneur amd64 sous émulation Docker Desktop ARM64. Debian13.3, Python3.11.14, SQLite3.46.1, FastAPI0.141.1/Starlette1.6.0/Uvicorn0.52.3/Pydantic2.13.4/SQLAlchemy2.0.52/httpx0.28.1. UID/GID10001, caps0, no-new-privileges ; cgroup observé1CPU/2Gio/pids128, rootfs/sources/bundle/profilreadonly. Une seule instance HTTP. Archive historique b8fc63f SHA25676f7200d829793a752e33f89a1672eb2b242a12a7a43104c7eaa40e5193b1973 ; code courant monté depuis gitarchivec454af8. Schéma synthétique migré réellement jusqu'à program_builder_operations_01, tête canonique actuelle ; pas nutrition_manual_01 arbitrairement forcée.

Digests distincts : confighistorique5ee90ab09696c4312cbe2a99654d5d2368d26f2050839858cca0ec801128334e ; manifesteamd649a3033f193914277a9651f9e25cbf7db2a9a205e844b28eff413f5f219a3e601 ; indexchargé2b15cf5ffffd4a8e56ca886f342ac350bf50231b2a44a283f6b269f818b9120e. Ce n'est ni une image complète reconstruitec454 ni une preuve VPS/amd64natif.

## Résultats mesurés
- Suite Linux sur source canonique pure : **126PASS/1FAIL**, zéro skip. Échec : test_linux_real_child_admits_actual_catalogue_and_owned_read_without_writes. Les fixtures antérieures, erreurs de préparation/outillage et leurs logs sont conservés séparément, sans être promus en preuve.
- Nominal inchangé : **refus**, enfant retour1/reaped/slotlibéré ;0,7222s monotone,0,7004s CPU enfant, RSS échantillonné maximal77 385 728octets. Ces valeurs décrivent un **échec précoce**, pas le workload réussi. Diagnostic séparé : EROFS /opt/auren/var pendant import ORM.
- Témoins Linux effectifs : AS536870912, CORE0, CPU2/3 ; allocation600Mio refusée ; SIGXCPU(-24) vers2,04s et wait/reap. Les tests timeout/pipe/snapshot/owner/JSON/préfixe/V2/V3/P07 passent comme composants ; ils ne qualifient pas le nominal HTTP complet.
- Captation directe instrumentée séparée du worker :19statements budgétés,11SELECT tracés après setup ; une série réelle/PARTIAL ; DML refusé.0,1000s englobe captation **et projection**, pas du temps SQL pur. Compte VM exact non mesuré ; ne pas convertir l'absence de callback en zéro instruction. Sources18fichiers/676079octets sur ce cas Legacy.
- BroadSCI sur8fichiers : **229PASS/1skip existant**. Ce banc garde les modes Git644/755 sous montage readonly. L'essai antérieur conservé (228PASS/1FAIL/1skip) échouait uniquement parce que notre chmod444 se propageait dans la copie temporaire que le test de génération doit modifier ; ce n'est pas le défaut du worker. Aucun test ignoré ou code SCI modifié pour obtenir le résultat.
- Vrai Uvicorn/FastAPI isolé : nominalA/B/vide503UNAVAILABLE/no-store (0,63–0,87s), sans Bearer401, paramètre de configuration422. Deux lectures parallèles :503rapide compatible avec un refus busy et503de refus nominal ; pas une preuve de débit réussi. Base synthétique identique avant/après les GET ; aucun enfant restant. Pic cgroup campagne243060736octets ; ce n'est pas un RSS individuel. RUSAGE_CHILDREN.maxrss reste un maximum de vie, distinct de l'échantillonnage PID.

## Confiance et transfert
3337fichiers source correspondent octet par octet à l'archive Git indépendante ;18pins profil comparés à Git. Checkout3732entrées, bundle133entrées et autorité5entrées : root-owned, aucune permission d'écriture non fiable ni ACL relevée ; montagesro et écritures UID10001 refusées. Des copies négatives symlink/traversal/digest/parentmutable sont refusées par le helper d'inspection, pas présentées comme une nouvelle protection du loader produit. Les montages/ACL de future QA restent non qualifiés. Le profil QUALIFIED utilisé par les tests porte explicitement TEST_FIXTURE_NOT_OPERATIONAL et n'est pas une admission opérationnelle.

Horloges VM/hôte observées divergent ; leur cause n'est pas établie. Aucun fait TIME-01 ni horodatage historique n'est réinterprété. Temps CPU/latences ci-dessus mesurés monotoniquement dans leur campagne.

## Verdict et prochaine opération
Catalogue **PASS**, parités SCI composants **PASS**. Frontière des chemins du candidat : preuves positives ; **PATH TRUST opérationnel HOLD**. **LINUX RUNTIME HOLD / ENDPOINT NOT_QUALIFIED** : nominalreadonlynonserviable. AlerteSonar13/S8707 relue via API sur supervisor.py:58–60 ; état API renvoyéNULL, fixed_at/dismissed_atNULL, aucun état de résolution déduit. Aucune fermeture ni modification de seuil effectuée. Anciennes CI de c454 restent historiques, aucune CI d'un correctif nouveau n'est revendiquée.

[Amendement minimal proposé](../../../openspec/changes/archive/2026-11-26-sci-runtime-02/BUILD_AMENDMENT.md) : worker.py + testworker, bootstrapORMmémoire fixe, captationréelleinchangée. GO distinct alors requis par mandatphase6, **reçu ensuite** sous call_12d65838fae34f55aee3aee31ea82f69. Aucun élargissement de budget, workflow, Dockerfile, VPS, DATA, mobile ou activation.

Preuves privées : `/Users/martinfeldmann/auren-review/sci-runtime-02-evidence-20261126/`, dont PURE_TESTS_LINUX.log, FINAL_CANONICAL_LINUX.log et INDEPENDENT_SOURCE_PATH_PROOF.json. Données et Bearer synthétiques restent privés, hors Git.
