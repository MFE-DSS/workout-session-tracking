# MOB-03 — arbitrages pour la suite du chemin critique

Date : 5 novembre 2026. Base canonique observée : 90da846. Document de travail pour l'opérateur et son architecte ; aucune décision OPEN n'est présentée comme acceptée.

**Actualisation — recadrage opérateur reçu :** [relevé produit/science/artistique](strategy/AUREN_PRODUCT_SCIENCE_REALIGNMENT_2026_11_05.md). Le tableau ci-dessous conserve les questions initiales ; ses statuts sont à lire avec ce relevé : D1/D4 reçoivent une cible Blueprint en quatre moments, pas encore un contrat de champs supportés ; D2 reçoit le principe de mesure datée et d'héritage séparé ; D3 reste ouvert. L'entrée composée est la direction retenue, sans acceptation visuelle. [Handoff des besoins scientifiques](strategy/AUREN_PRODUCT_SCIENCE_DEPENDENCIES.md), notamment SCI-P01/P02 pour le premier parcours.

**Point de reprise courant :** [CR PO/architecte](MOB03_CR_PO_ARCHITECT_2026_11_05.md). Compte/préférences acceptés, correction sans inventaire acceptée ; les constats de socle ci-dessous sont historiques. D2/D3 restent ouverts. D4 reçoit désormais le refus explicite d'un inventaire manuel : contexte de matériel via proposition/substitution à contractualiser, aucune disponibilité de salle inventée.

## Travail indépendant réalisé localement

Le socle API de compte est implémenté : inscription JSON, changement authentifié du mot de passe, validation partagée avec le web, contraintes uniques, quotas partagés et révocation d'époque. Aucune UI native nouvelle, aucune suppression, donnée corporelle, migration ou publication. Le vrai consommateur compte/onboarding reste à raccorder après les décisions ci-dessous et la revue visuelle.

## Décisions à prendre — propositions de l'agent

| Décision | Sources canoniques | Proposition pour avancer | Conséquence à arbitrer |
|---|---|---|---|
| D-MOB03-1 — objectifs / unités | User, training_preferences ; objectifs seulement dans lab/profile.ts | Ne pas collecter d'objectif global sans consommateur défini ; conserver les unités canoniques actuelles tant que conversions et stockage ne sont pas spécifiés | L'onboarding n'affiche pas un choix inutilisé ; un sélecteur impérial reste une capacité à concevoir, pas une préférence prétendue stockée |
| D-MOB03-2 — poids | BodyMeasurement ; body_profile.list_measurements ; body_ledger.construire_releve ; User.weight_kg hérité | Faire lire la chronologie existante ; conserver le fait hérité séparé sans lui inventer de date ; aucun backfill ou double-write | Décider de la présentation ou de l'omission du poids hérité et du lecteur mobile de référence |
| D-MOB03-3 — suppression | Inventaire MOB-00 account-deletion ; STORE-00 ; session_epoch/device_auth ; données propriétaires | Dresser d'abord la matrice effacement/rétention, réauthentification et journal local ; ne pas ajouter un faux effacement par désactivation | Décision opérateur requise avant toute implémentation destructive ; aucune suppression réalisée ici |
| D-MOB03-4 — parcours / UX | Primitives LOCKED ; OnboardingFlow LAB ONLY ; services de préférences/environnement | Séparer la création du compte des déclarations facultatives ; ne pas obliger à remplir un profil corporel pour commencer une séance ; reprendre les faits confirmés | Valider les acquisitions utiles, l'ordre et les croquis ; équipement riche reste MOB-09 |

## Dépendance technique : propriétaire du journal

**Réponse opérateur du 5 novembre : transition prudente validée.** Ancien journal conservé intact, attribution après vérification serveur, connexion nécessaire une seule fois pour cette attribution initiale. La vérification doit couvrir toutes les séances présentes dans le journal à attribuer ; la partition et ses preuves restent à implémenter. Cette réponse ne clôt pas les décisions D-MOB03-1 à 4.

Le journal connecté actuel utilise auren.db. Avant tout nouveau parcours de changement de compte, il faut un contrat prouvé : identité serveur vérifiée, partition par propriétaire, commandes d'un ancien compte jamais envoyées sous les credentials d'un autre. Proposition technique à revoir : partition explicite par user_id, migration du journal non attribué seulement après preuve d'appartenance d'une séance, conservation isolée en cas d'incertitude et aucun effacement silencieux. Ni le nom du compte ni un simple logout ne prouvent l'appartenance des anciennes lignes.

Les nouvelles API ne changent pas ce journal et aucun nouvel écran d'inscription n'est raccordé avant cette garde. Le retour à l'app QA MOB-02 conserve donc son client actuel.

## Croquis candidats — aucune acceptation visuelle

**Retour opérateur : croquis à revoir avant code UI.** Attente précisée : DA AUREN avec son logo et qualité d'accueil d'une application aboutie. Le cadrage transversal, l'inventaire des surfaces et les informations attendues du PO designer sont rassemblés dans [le dossier UI/UX](MOBILE_UIUX_PO_DESIGNER_BRIEF_2026_11_05.md). Les croquis ci-dessous restent des propositions non acceptées.

Ces croquis définissent les décisions à revoir ; ils ne sont pas des écrans produits et ne créent aucune baseline.

```text
Créer le compte                         Changer le mot de passe
AUREN                                   AUREN
Identifiant                             Mot de passe actuel
Courriel (facultatif)                    Nouveau mot de passe
Mot de passe                            Confirmer
Confirmer                               [Mettre à jour]
[Créer le compte]
[Déjà un compte]
```

Après une réponse d'inscription perdue : résultat à vérifier, aucune confirmation inventée ; proposer la connexion existante avant de créer une autre identité. Après un changement de mot de passe incertain : vérifier l'authentification, sans rejouer silencieusement le changement. Les secrets restent en mémoire de formulaire et SecureStore pour les tokens, jamais dans journal/export.

Les liens réinitialisation et export gardent leur parcours web MOB-00 ; aucun token Bearer mis dans une URL. La destination publique de confidentialité et le responsable restent un point STORE-00 à confirmer avant livraison du parcours complet.

## Suite adoptée du chemin critique

| Tranche | Capacités à préserver selon MOB-00 | Travail suivant |
|---|---|---|
| MOB-03 | auth-register, account-password-change, onboarding, préférences et frontières propriétaires | Terminer les arbitrages, le propriétaire du journal, le consommateur et la revue des surfaces |
| MOB-04 — MISSION | mission-today, plan-adaptation-dismiss, readiness selon son contrat | Établir les sources de chaque information ; aucune recommandation ou valeur temporelle inventée |
| MOB-05 — Progrès / journal | history-journal, exercise-history, progress, coach-report selon leurs dépendances | Distinguer historique réel, données absentes et analyses autorisées ; préserver les contrats de domaine |
| MOB-06 puis MOB-07 | template-library puis custom-programs / constructeur | Garder le domaine serveur, réécrire les interactions natives et leurs validations |
| MOB-08 à MOB-12 | Exercices, salle, substitutions, profil après UX-LAB-PROFILE, récupération/cardio | Ouvrir chaque change dans l'ordre adopté, avec ses décisions et ses preuves |

Les lignes suivantes sont un ordre de pilotage, pas une acceptation anticipée de leur design. Photos, octogone et abonnement gardent leurs workstreams et dépendances. Les validations appareil MOB-02 en cours restent distinctes de la future recette MOB-03.
