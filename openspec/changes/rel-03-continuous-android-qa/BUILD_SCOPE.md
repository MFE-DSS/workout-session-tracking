# REL-03 — scope soumis au GO BUILD

## Extension OVH proposée —15novembre2026

Le GO technique initial est conservé dans BUILD_AUTHORIZATION.md ; les statuts PROPOSED historiques ci-dessous ne l’annulent pas. Le nouveau [delta OVH](OVH_AMENDMENT_SCOPE_20261115.md), [preuve/configuration](OVH_EVIDENCE_AND_CONFIG.md), a reçu son acceptation technique propre, call_657199a80f2441d3b3bd3d450dfaaabf ; voir OVH_BUILD_AUTHORIZATION.json. Source683e883, schéma program_builder_operations_01 déjà livré : aucune réimplémentation BODY/NUT/MOB06/MOB07 ou du repair de sauvegarde. Aucune opération distante, nouveau coût, APK/OTA ou nouvelle composition UI dans cette extension technique.

**Instant historique du scope initial : PROPOSED, avant son GO. État courant : code initial livré, amendement technique OVH autorisé ; aucune opération externe autorisée.**

## Ingénierie contrôlée proposée
- Nouveaux outils/entrypoint de livraison QA, cible attestée, versions/compatibilité, sauvegarde complète en copie et reçus ; façade bornée réutilisée sans toucher au banc QA02 vivant.
- Docker et blueprint hébergement dédiés, sans création d'instance/connexion/paiement ; absence de cible réelle reste bloquante.
- Nouveau profil EAS continu, helper séparé, Expo Updates SDK58 et expo-application explicite au verrou existant si nécessaire. Aucun upgrade global du SDK.
- Canal qa/configuration de projet existant après GO explicite de ce scope ; aucune publication OTA/build cloud avant gate de release/quotas/cible applicable. Le client QA02 reste historiquement non-OTA.
- Orchestrateur manuel GitHub avec préparation sans credentials et gate `qa-release` ; pas de changement des quatre checks requis ou du pipeline CI canonique.
- Observateur de provenance sans écran dans vrai ConnectedApp ; tests, exports locaux, paquet d'actions fournisseur/coût. Pas de fixture servie.

## Fichiers possédés / leases proposés
Nouveaux `tools/qa_delivery/`, `tests/test_qa_delivery_*.py`, `deploy/qa/`, `.github/workflows/qa-release.yml`, `clients/mobile/qa-delivery.config.js`, `clients/mobile/qa-delivery-target.json`, `clients/mobile/src/native/qaDelivery*.ts`, tests et reçus sous `docs/release/rel-03/`.
Leases limités : `clients/mobile/app.config.js`, `eas.json`, `package.json`/lock, `ConnectedApp.tsx` (observer seulement), registre append. Si une adaptation QA de gateway est nécessaire, module nouveau ou helper borné avec replays QA02 préservés ; aucun changement de son processus live. Modifications hors liste nécessitent révision explicite du scope.

## Autorisations distinctes
Le GO BUILD sollicité couvre implémentation/tests/revue/CI/PR/merge du code préparatoire, configuration QA isolée EAS sans publication, et recette locale sur copies/émulateur dédié. **Aucun cloud-spend, nouvelle instance, modification du service partagé, transfert du banc actif, secret externe, build facturé, diffusion APK/OTA à appareils externes, publication production ou activation réelle.**
Après code/config indépendants prêts, fournir une seule décision externe concrète : compte/connexion fournisseur, plan/coût/variable, région, secrets par référence contrôlée, gate de release et opération exacte. Puis, sous autorisation applicable, exécuter cible stable/cutover/build/OTA/rollback sans nouveau GO de merge routinier.

Le build n'est pas COMPLETE tant que cette seconde étape n'est pas réalisée. Aucun faux artefact ou succès de pipeline pour combler le blocage d'infrastructure.
