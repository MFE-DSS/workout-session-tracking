# Design — account-onboarding-native (MOB-03)

## Context

Base : merge MOB-02 `90da8461803e87897c3d8f48627c4b704b3cfcd6`. La proposition explique le besoin ; les deux deltas décrivent les garanties attendues. Préparation autorisée seulement : aucun GO BUILD de sémantique ou surface nouvelle.

### Observé dans le dépôt

| Domaine | Existant réel | Écart mobile |
|---|---|---|
| Compte | Inscription formulaire web dans auth_routes, règles auth/password_policy ; User + device_auth et session_epoch | mobile_api possède login/refresh/logout/me, pas d’inscription JSON ni suppression |
| Préférences | training_preferences possède cadence 1–7, priorités ordonnées, familles et items d’équipement ; absence distincte du vide | GET MOB-02 expose la fréquence ; contrats de lecture complète/écriture à préparer |
| Poids | BodyMeasurement, services measurements/body_profile/body_ledger ; User.weight_kg hérité séparé | chronologie et compatibilité à choisir explicitement, pas de nouvelle table d’historique |
| Consentement | body_consents, texte versionné et helpers de body_profile | acquisition/retrait à raccorder à l’identité mobile |
| Objectifs / unités | objectif global du profil LAB ONLY ; kg/cm dans les formulaires observés | aucune persistance produit correspondante identifiée dans User/TrainingPreferences |
| Salle / matériel | equipment_model, environment_activation/resolution, préférences concrètes | réutiliser ce domaine ; bibliothèque riche et assets restent MOB-09 |
| UX | OnboardingFlow de labo, primitives natives existantes | aucune nouvelle composition de compte/onboarding approuvée |

MOB-00 `auth-register`, `account-password-change`, `onboarding`, `profile-physical`, `profile-training-preferences`, `body-measurements`, `body-consent`, `gym-equipment`, `account-deletion` forment la matrice de couverture. `auth-password-reset` et `account-data-export` conservent leur destination WEB_ONLY.

## Goals / Non-Goals

**Goals:** définir une frontière mobile JSON authentifiée, des déclarations confirmées et reprenables, un propriétaire unique par donnée/journal, et des gates testables de consentement, révocation et effacement.
**Non-Goals:** cette préparation n’ajoute ni code, ni migration, ni stockage. Pas de calibration E7, profil octogone, photo/provider, MISSION, nouveau score, journal de progression ou nouveau constructeur de salle.

## Decisions

### Approche proposée, pas une sémantique nouvellement approuvée

- **Garder les domaines existants.** Adapter les routes JSON autour des services existants plutôt que copier les formulaires web ou créer des services de préférences concurrents. Aucune dépendance ajoutée par défaut.
- **Une identité serveur, une partition locale.** Les futurs consommateurs passent par AuthSession et les frontières mobiles ; l’authentification résout user_id. Le passage de compte ne réattribue jamais le journal/outbox à un autre propriétaire. L’approche de migration du journal existant doit être prouvée avant changement.
- **Séparer faits et transport.** Distinguer brouillon, commande persistée, réponse confirmée et résultat inconnu. Le protocole d’inscription et d’écriture reprenable doit empêcher un second compte ou une seconde mesure après réponse perdue.
- **Poids daté : réutiliser l’existant.** Proposition à valider D-MOB03-2 : chronologie BodyMeasurement et lecteurs existants ; compatibilité de User.weight_kg explicitée au lieu d’un backfill ou double-write inventé. Pas de courbe ou dashboard nouveau en MOB-03.
- **Objectifs et unités restent à arbitrer.** Ne pas ériger les quatre objectifs de lab/profile en vocabulaire serveur. Choisir les usages réels, le stockage et les conversions après D-MOB03-1 ; les tâches correspondantes restent bloquées jusque-là.
- **Suppression = opération sensible séparée.** Concevoir l’inventaire propriétaire complet, les credentials, les commandes en attente, la confirmation et la preuve de résultat avant D-MOB03-3. Un soft-delete ne sera pas présenté comme un effacement. Aucune action destructive pendant la préparation.
- **UX avant code.** AUREN-MARK-V1 et primitives boutons/champs/Sheet existantes ; croquis et rendu réel soumis avant commit UI. Le flux de labo sert à repérer les champs et lecteurs, pas à importer ses formulations, hypothèses ou géométries.
- **Compatibilité MOB-02.** Préserver les GET de bilan, les commandes de séance, la restauration complète et les états dégradés. Les futures routes montées doivent être classées une seule fois dans l’inventaire MOB-00.

### Gates de décision, non questions différées

D-MOB03-1 (objectifs/unités), D-MOB03-2 (source du poids/compatibilité), D-MOB03-3 (effacement/rétention/journal) et D-MOB03-4 (acquisitions/UX/équipement) restent **OPEN — apply bloqué sur ces sémantiques**. Le mandat permet de préparer cette proposition, pas de les trancher implicitement. Les scénarios des deltas imposent l’approbation avant leur implémentation ; aucun schéma de payload ou table nouvelle n’est déclaré existant.

### iOS / Android

Même domaine et mêmes garanties de données. Credentials et feuilles/clavier/retour réutilisent les adaptations natives existantes ; pas de divergence fonctionnelle approuvée. Toute divergence introduite ultérieurement doit être motivée et recettée sur les deux plateformes.

## Risks / Trade-offs

- [Échec réseau après création ou mesure] → confirmer par un protocole serveur idempotent approuvé ; tester le vrai consommateur et la réponse perdue.
- [Journal d’un ancien compte envoyé sous le nouveau] → partition propriétaire et migration testées ; aucune purge silencieuse.
- [Poids hérité confondu avec mesure datée] → D-MOB03-2 et tests sans date inventée.
- [Suppression partielle ou promesse excessive] → inventaire de dépendances et D-MOB03-3 ; réauthentification et preuve explicite, sans exécution dans cette préparation.
- [Données sensibles et consentement] → appliquer le contrat existant ; revue sécurité/qualité requise par GOV-SONAR-01 avant la nouvelle exposition.
- [Onboarding qui exige du matériel futur] → acquisition minimale dans le domaine existant ; les surfaces/assets MOB-09 restent hors scope.

## Migration Plan

1. Revue PO/architecte des décisions et des contrats ; aucune migration produite ici.
2. Si un stockage approuvé requiert une migration : additive-only, tier check_scope réel, drift/snapshot/roundtrip et sauvegarde ; aucun backfill ou effacement historique implicite.
3. Contrats JSON et tests d’isolation/idempotence/révocation avant câblage des vrais consommateurs.
4. Revue visuelle avant commit UI ; CI complète sur le HEAD publié ; merge sous conditions permanentes.
5. Déploiement par SHA vérifié avec GO distinct et rollback préparé ; recettes Android puis iPhone.
6. Archive uniquement après les preuves obligatoires. MOB-02 conserve ses gates déploiement/appareils indépendantes.

## Questions opérationnelles différables

Identifiant du compte de recette et disponibilité du téléphone lors de la passe ; ces détails ne changent ni le domaine ni les décisions de produit. Aucun secret dans les artefacts.

## Mandat de build partiel — 5 novembre 2026

L'opérateur demande explicitement d'avancer sur les fonctionnalités du chemin critique pendant son absence. L'agent borne ce build au socle non destructif du compte : inscription JSON, changement authentifié du mot de passe et révocation canoniques, mutualisation des validations web et preuves de routes réelles. D-MOB03-1 à 4 restent OPEN ; leurs sémantiques et compositions ne sont pas implémentées. Aucun choix d'effacement, d'unité ou de donnée corporelle n'est accepté implicitement. Plan technique : implementation-account-core.md ; compte rendu : docs/SPRINT_MOB03_REPORT.md. Pas de nouveau contrat visuel, de migration ou de déploiement.

### Contrat technique de la partie indépendante

POST /api/mobile/v1/auth/register : mêmes champs et validations que /register ; 201 avec paire Bearer et identité, aucun cookie web. Nom/email déjà utilisés : 409 ; données invalides : 400 avec code et message canonique. La contrainte unique existante reste le garde de concurrence. Aucun secret ni clé d'idempotence persisté ; si la réponse est inconnue, le consommateur doit proposer une vérification par login au lieu d'affirmer le succès ou de créer un autre compte. Quota register partagé avec le web.

POST /api/mobile/v1/auth/password : Bearer propriétaire, mot de passe actuel et nouvelle confirmation ; même politique de mot de passe et incrément de session_epoch que le web. La nouvelle paire est émise dans la même transaction pour l'appelant ; tous les anciens credentials sont invalides. Quota login partagé pour la vérification du secret actuel. Les surfaces et la gestion du journal propriétaire restent des tâches non livrées de MOB-03.

Protection technique supplémentaire validée par test concurrent : le changement de mot de passe compare l'époque et le hash courants dans l'UPDATE atomique. Une demande devenue obsolète reçoit 409 credentials_changed et n'émet pas de credentials. Cela conserve le contrat session_epoch tout en empêchant deux nouveaux jeux de jetons au même numéro d'époque après des changements concurrents. Aucune migration ou nouvelle politique de révocation.
