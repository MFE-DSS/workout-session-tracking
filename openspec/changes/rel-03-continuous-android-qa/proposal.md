# REL-03 — livraison Android QA continue

## Why
RELEASE-QA-02 livre un vrai APK, mais sa cible dépend du poste et du tunnel temporaire. Le binaire existant désactive Expo Updates et ne peut recevoir un futur canal par simple publication JS. Le pilote doit pouvoir recevoir des versions traçables sans refaire son moteur scientifique ni perdre ses faits.

## What Changes
- Ajouter un circuit QA séparé : cible HTTPS stable attestée, opérations persistantes, sauvegarde complète et rollback compatible.
- Préserver package/signature QA, ajouter identité native/JS/serveur distincte et nouveau profil EAS ; installer/configurer Expo Updates pour ce profil seulement.
- Ajouter préparation/contrôle de release et workflow manuel protégé : CI/HEAD/visuel/compatibilité puis approbation de diffusion, jamais publication au merge.
- Vérifier un nouvel APK, upgrade de QA02 sans désinstallation, vrai téléchargement OTA et rollback sur émulateur dédié après autorisations de cible/diffusion. Physique séparé.

## Scope and Non-goals
**PROPOSED / NO_GO_BUILD_REL03 / NO_HOSTING_OR_SPEND_OR_REMOTE_RELEASE_APPROVAL.** Le mandat autorise la préparation ; le GO QA02 ne s'étend pas à cette plateforme. Le design et BUILD_SCOPE sont soumis à revue avant apply.

Aucune nouvelle règle SCI, API métier V1/V3, migration historique/local, réécriture du journal, nouvel écran, baseline, nouveau domaine, Store, OTA production ou traitement réel. DATA reste ouvert. Hébergement payant, credentials fournisseur et publication sur appareils externes restent séparés ; aucun abonnement n'est acquis.

## Impact
Configuration/dépendances natives QA, outils de déploiement/attestation et orchestration de release. Aucun serveur partagé modifié. CLAUDE §6/GOV-MERGE-01 et les validations humaines applicables restent effectifs. COMPLETE seulement après cible stable réellement servie + APK installable + chemin de release contrôlé réellement vérifié.
