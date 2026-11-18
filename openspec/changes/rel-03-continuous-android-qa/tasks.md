## 1. Proposition
- [x] Réconcilier canonique/reçus/manifestes/registre et worktrees sans toucher au banc actif.
- [x] Vérifier dépendances et métadonnées natives de l'APK existant, linkage/channels EAS en lecture seule.
- [x] Définir options, périmètre, continuité d'identité, autorisations séparées et sources de coûts.
- [x] Revue indépendante de préparation : nothing important left ; précision gel incluant refresh/GET writers intégrée.
- [x] OpenSpec/protocole initiaux et GO BUILD REL-03 exact avant apply (BUILD_AUTHORIZATION).
## 2. Build contrôlé après GO
- [x] Implémenter outils, entrypoint/config portable et backup/restore en copie, nouveaux endpoints QA bornés.
- [x] Préparer profil/version/identités et Expo Updates via CLI officielle, classifier compatibilité/refus ; pas d'OTA production.
- [x] Workflow manuel et préflight de gate protégé, aucun acte publiant au merge.
- [x] check_scope puis checks requis, tests consommateurs, revues et CI exacte ; livraison du code prêt sous GOV-MERGE-01.
- [x] Compléter tout le code/config indépendant avant paquet unique de décision fournisseur/quotas/diffusion.
## 3. Opérations sous autorisations distinctes
- [ ] Compte/connexion/spend/cible approuvés ; vrai service HTTPS stable avec persistance, health/version et coût constatés.
- [ ] Cutover QA seul, sauvegarde complète/restauration en copie, continuité auth/owner/faits et rollback constatés.
- [ ] Nouveau APK EAS attesté, upgrade installé sans effacement/signature inchangée ; client source/runtime/backend exacts.
- [ ] Vrai update QA autorisé et rollback sur client installé ; incompatibilité refusée ; redémarrage/SQLite/réseau/session vérifiés.
- [ ] Appareils physiques : résultats distincts, jamais déduits de l'émulateur.
- [ ] Reçus finaux, CI/canonique/Sonar réels, closeout du scope effectivement atteint et nettoyage de ses seuls éléments sans travail unique.

## Correction de préparation du transport
- [x] Dépôt public réellement vérifié ; supprimer tout transport DB en artefact public.
- [x] Producteur/importeur privés chiffrés, vrais consommateurs locaux et revue fraîche Task4 ; aucun upload réel.
- [x] Revue globale finale, sweep/CI/merge du code préparatoire ; opérations du §3 restent ouvertes.

## Reçu du code, 10 novembre

PR398 fusionnée d67f12a ; CI canonique42852368435 success11jobs et workflow réel
PREPARE42852655171 prepare PASS/release skipped. [Reçu détaillé](../../../docs/release/rel-03/CODE_DELIVERY_RECEIPT.md).
Candidat non distribuable. Le paquet externe est préparé et relu ; l’opérateur
demande une explication avant décision, aucune autorisation externe acquise.
Le §3 reste ouvert ; aucun archivage COMPLETE ni faux nouveau binaire.

## Correction de compatibilité de schéma,15novembre

- [x] Reproduire le refus d'une vraie base Alembic `nutrition_manual_01` et enlever la fixture estampillée artificiellement PLAN.
- [x] Aligner les pins database/release/candidate sans affaiblir schéma exact/intégrité/FK, conserver les faits auth/PLAN/BODY/NUT en backup/export/restore neufs.
- [ ] Terminer broad consommateurs, revue indépendante et livraison CI/PR du correctif ; [plan et preuves](SCHEMA_COMPATIBILITY_REPAIR.md).
- Les opérations du §3 et les propositions OVH/origine/configuration de fonctionnalités restent distinctes et non exécutées.

## Reçu de réconciliation —15novembre, canonique683e883

Le repair schéma précédent est effectivement livré par412/413, puis ses consommateurs suivent program_builder_operations_01 avec414/415. Leurs reçus finaux et les CI exactes résolvent le suivi laissé ouvert ci-dessus ; aucune nouvelle migration/repair à réaliser. PREPARE_ONLY43759443931 réel sur683e883 est non distribuable, sans build/release. Les tâches opérationnelles du §3 restent ouvertes.

## Extension OVH, avant toute nouvelle application
- [x] Réconcilier les trois blockers actuels : observation fournisseur, origine exacte et configuration des fonctionnalités réellement livrées.
- [x] Préparer scope et contrat proposés, conserver les autorisations déjà acquises et les frontières de données/déploiement.
- [x] Revue indépendante du paquet concret ; un Important de liaison origine→upstream→conteneur corrigé dans le contrat et les témoins requis. Les autres détails sont d’implémentation ; aucune seconde revue indépendante du texte corrigé prétendue.
- [x] Acceptation opérateur du seul delta technique OVH avant code : call_657199a80f2441d3b3bd3d450dfaaabf, « Autoriser le build technique REL‑03 OVH » ; aucun nouveau GO des scopes produit.
- [ ] Après ce GO : plan/leases, RED→GREEN, préparation locale, tests/CI/revue et livraison scopée sous GOV-MERGE-01.
- [ ] Sous autorisations opérationnelles ultérieures seulement : producteur/transport privé réel, hôte supporté, observateur installé, service synthétique isolé, DNS/TLS et candidat installé.

## OPS-02 — poursuite explicite après maintenance #422

- [x] Scope local et leases réconciliés sur348dc8c3 ; mandat OPS-02 distinct des opérations distantes.
- [x] Transport privé explicite, durabilité/UNKNOWN/readback, isolation dédiée et initialisation vide canonique implémentés et testés ; [ledger](OPS02_SCOPE_AND_LEDGER.md).
- [x] Préflight frais en lecture seule et paquet opérationnel borné préparés ; backup historique défectueux conservé comme tel.
- [ ] Finir contrôlesCI_INFRA/revue du paquet, CI exacte et livraison du delta technique.
- [ ] GO opérationnel unique, séparation humaine GitHub, garde privée, image réelle et QA qualifié.
- [ ] Candidat Android consolidé et update/rollback installés sous leurs autorisations distinctes ; recette physique séparée.

## OPS-03 — 18 November public qualification

- [x] Authoritative/public A record and no AAAA; existing ACME accounts, actual QA certificate/renewal dry-run, scoped vhost and loaded nginx generation.
- [x] Fresh restricted observations around public TLS, exact image/config/API/SCI/schema identity and current synthetic HTTP smokes; personal services preserved.
- [x] Post-public-write encrypted export/disposable restore; prior backups retained. [Actual operational receipt](../../../docs/release/rel-03/OPS03_PUBLIC_QUALIFICATION_20261118.md).
- [ ] Deliver exact target/native fingerprint/candidate metadata through scope checks, independent review, CI and guarded merge. [Scope/ledger](OPS03_SCOPE_AND_LEDGER.md).
- [ ] Freeze merged source, fresh PREPARE and candidate-bound release proof, then distinct candidate GO. No automatic build at merge.
- [ ] Signed APK/upgrade, complete installed-client smokes, controlled update/rollback and separate physical acceptance remain open.
