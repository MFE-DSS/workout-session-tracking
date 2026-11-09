# RELEASE-01 — dossier de recette et préparation de distribution interne

9 novembre 2026. **SYNTHETIC_QA_PARTIAL / NO_INSTALLABLE_QA_ARTIFACT /
PHYSICAL_ACCEPTANCE_OPEN / NOT_DEPLOYED.** Référence testée :
`fe9f6e9beb585a271ae2c2726e338359057b9f58` (après PLAN-CAL-01). Ce dossier
ne clôture ni RELEASE-01, ni MOB-03 complet, ni DATA-ACT-01.

Le mandat autorise un banc isolé et des comptes synthétiques pour éprouver le
runtime déjà livré. Il n'autorise pas le traitement de données personnelles
réelles, un effacement irréversible ou un déploiement. Aucune implémentation
PLAN/SCI, dépendance, migration, interface ou configuration produit n'est
modifiée par cette tranche documentaire.

## Lire les preuves et leur portée

| Pièce | Contenu |
|---|---|
| [QA_ENVIRONMENT](QA_ENVIRONMENT.md) | SHA, bundle/pins, génération d'autorité, schéma/bootstrap, configuration et hôtes réellement utilisés |
| [QA_RESULTS](QA_RESULTS.md) | Matrice des scénarios observés, partiels ou encore ouverts ; HTTP, natif et physique distingués |
| [INTERNAL_BUILD_BRIEF](INTERNAL_BUILD_BRIEF.md) | Prérequis d'un véritable APK QA interne et d'un build iPhone compatible ; aucun artefact prétendu produit |
| [PACKAGING_SECURITY_REVIEW](PACKAGING_SECURITY_REVIEW.md) | Revue ciblée B404/B603 et risques d'hôte/activation restant à traiter |
| [OpenSpec](../../../openspec/changes/release-01-controlled-plan-acceptance/proposal.md) | Périmètre, design et tâches actives ; aucun archivage anticipé |

Les reçus privés du banc sont conservés dans
`/private/tmp/auren-data-release-01-review-evidence/` avec accès restreint.
Les fichiers source des tests privés peuvent contenir les credentials
synthétiques ; ils ne sont pas destinés à être publiés. Aucun identifiant
personnel d'appareil, token, DB ou credential n'entre dans ce dossier versionné.

## État décisionnel

| Axe | État prouvé / gate restant |
|---|---|
| DATA | Package de décisions distinct ; identité/juridiction et politique applicable encore à compléter et approuver. Pas d'activation réelle ou d'effacement par cette recette |
| QA serveur | Vrai HTTP loopback : sept qualifications synthétiques → snapshot propriétaire → V3 → ack exact → même séance → journal typé ; retrait/restauration d'autorité sans perte de faits observé |
| iOS natif | Vrai ConnectedApp dans Expo Go sur simulateur : connexion, récupération de séance, revalidation et ouverture de saisie machine ; parcours complet et mutation native non prouvés |
| Android natif | Lancement du vrai ConnectedApp bloqué dans Expo Go 58.0.5 : `Cannot find native module 'ExpoTopicSubscriptionModule'` ; aucune recette applicative réussie |
| Physique | iPhone 15 Plus/iOS 27.0.1 détecté, AUREN Lab 0.0.1(1) installé mais SHA/backend inconnus ; aucun Android physique connecté et aucune acceptation physique |
| Installable | Aucun APK AUREN QA produit ; hôte Expo Go et ancien build installé ne constituent pas l'artefact cible attesté |
| Qualité / livraison | Quatre checks obligatoires et Sonar consultatif préservés ; publication, HEAD final, vraie CI et revue indépendante à vérifier par le responsable de livraison |
| Release | Cible/artefacts compatibles, politique, sécurité/rollback cible, recettes Android/iPhone et GO de déploiement restent ouverts |

## Brainstorming / Options / Risques / Choix retenu

Réutiliser une DB personnelle ou un ancien build sans provenance ne donnerait
pas de preuve attribuable. Le banc neuf avec runtime fusionné, vrai serveur,
vrais loaders SCI et données synthétiques permet une preuve limitée utile.
Le choix retenu sépare ce résultat des gates natifs/physiques et documente
l'incompatibilité Android au lieu de déclarer un succès depuis HTTP.
Le futur client compatible exige une cible de build revue et un backend QA
joignable, isolé et autorisé ; aucune publication Store n'est nécessaire pour
un APK QA interne. Risques restants : provenance binaire, accès réseau réel,
persistance locale, autorité et sécurité de l'hôte cible.

La prochaine opération technique est de préparer une cible de build QA
compatible et ses prérequis, puis de reprendre la recette native complète
sur des artefacts attestés. La demande de déploiement final ne sera préparée
que lorsque cible, rollback et risques seront complets. Un merge documentaire
sous GOV-MERGE-01 ne fournit pas cette autorisation.
