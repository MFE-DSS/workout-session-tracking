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
