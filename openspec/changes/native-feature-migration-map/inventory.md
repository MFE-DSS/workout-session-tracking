# Inventaire des fonctions web → destination native (MOB-00)

Généré depuis `inventory.yaml` (base `36b971a`) — ne pas éditer à la main.
**38 fonctions**, **110 routes** rattachées, BLOCKED 9, DEPRECATE 1, KEEP_DOMAIN 4, REWRITE_NATIVE 19, WEB_ONLY 5.
« (proposé) » = proposition de l'agent, à trancher par l'opérateur.

## Mission

| Fonction | Statut | Destination native | Routes | Propriétaire du domaine | Dépendances | Risque |
|---|---|---|---|---|---|---|
| MISSION — la séance du jour et sa raison | KEEP_DOMAIN | MISSION (MissionScreen, livré) | 2 | recommendation_v3 · home · mobile_read_models.mission_read_model · session_state | — | faible — livré ; constat PLAT-01 : raison « déjà bien servi » affichée MESURÉE sur un compte sans séance |
| Écarter une adaptation de plan proposée | REWRITE_NATIVE | MISSION | 1 | plan_adaptation_store | MOB-04 Mission | faible |

## Séance

| Fonction | Statut | Destination native | Routes | Propriétaire du domaine | Dépendances | Risque |
|---|---|---|---|---|---|---|
| Exécuter une séance (démarrer, séries, repos, substitution, terminer, abandonner) | KEEP_DOMAIN | SÉANCE (ExecutionScreen, ResumeScreen, livrés) | 11 | session_builder · console_state · substitution · overload_engine · environment_activation · mobile_read_models | MOB-02 intégration de séance (hors chemin heureux) · E7 pour l'instrument de charge | moyen — reprise, hors ligne et substitution à durcir (MOB-02) |
| Bilan de fin de séance | KEEP_DOMAIN | SÉANCE (CompleteScreen, livré) | 1 | session_recap · stats · session_completion | read model d'historique pour la comparaison « à toi-même » | faible |

## Compte

| Fonction | Statut | Destination native | Routes | Propriétaire du domaine | Dépendances | Risque |
|---|---|---|---|---|---|---|
| Se connecter, se déconnecter | KEEP_DOMAIN | Compte (LoginScreen, livré) | 7 | auth · device_auth · password_policy | — | faible |
| Créer un compte | REWRITE_NATIVE | Compte — entrée de l'onboarding | 3 | auth · password_policy | MOB-03 onboarding · limite de débit d'inscription côté API | moyen — aujourd'hui le testeur doit passer par le web |
| Mot de passe oublié, réinitialisation par lien | WEB_ONLY | hors app — l'écran de connexion renvoie vers le site | 4 | auth · email | — | faible |
| Changer son mot de passe | REWRITE_NATIVE | Compte | 2 | auth · password_policy | MOB-03 compte | faible — révocation par époque de session déjà en place |
| Écrire à l'administrateur | WEB_ONLY | hors app (lien vers le site) | 2 | email | — | faible |
| Exporter son journal (JSON, CSV) | WEB_ONLY | hors app (lien vers le site) | 3 | export_builder · backup_inspector | suppression de compte dans l'app — exigence Store · inexistante | moyen — RGPD : suppression de compte à concevoir avant la diffusion publique |
| Onboarding (compte, corps, entraînement, objectif) | BLOCKED | entrée de l'app | 0 | training_preferences · body_profile · auth | UX-LAB ONBOARDING (ne demander que les données dont on sait l'usage) · consentement explicite (vNext O6) · inscription mobile | élevé |
| Abonnement (gratuit / pro) | BLOCKED | Compte | 0 | — | définition de la valeur produit · compte Apple Developer et Google Play · fournisseur d'achats (RevenueCat à évaluer) · build de développement | élevé |
| Supprimer son compte depuis l'app | BLOCKED | Compte | 0 | auth | exigence Store (Apple, Google) · RGPD · conception de l'effacement (dur vs exclusion) | élevé — bloquant pour toute diffusion publique |

## Profil

| Fonction | Statut | Destination native | Routes | Propriétaire du domaine | Dépendances | Risque |
|---|---|---|---|---|---|---|
| Profil — page de synthèse du compte | REWRITE_NATIVE | PROFIL | 1 | profile_metrics · radar · session_state | UX-LAB PROFILE (axes de l'hexagone / octogone) · MOB-11 | élevé — surface centrale, modèle d'interaction hérité (TRANSITIONAL) |
| Profil physique déclaré (taille, poids, FC de repos, tour de taille, tension) | REWRITE_NATIVE | PROFIL / onboarding | 1 | body_profile | MOB-03 onboarding · consentement explicite (spec vNext O6) | moyen — users.weight_kg écrasé en double de body_measurements.weight_kg : une seule source à choisir |
| Préférences d'entraînement déclarées (objectif, fréquence, durée…) | REWRITE_NATIVE | PROFIL / onboarding | 1 | training_preferences | MOB-03 onboarding | moyen |
| Mesures corporelles et poids, série temporelle datée | REWRITE_NATIVE | PROFIL (BODY_LEDGER) | 8 | measurements · body_ledger · body_profile | consentement aux mesures (body_consent) · choix de la source unique du poids | moyen — la série temporelle EXISTE déjà (body_measurements) ; ne pas en créer une seconde |
| Consentement à l'enregistrement des mesures corporelles | REWRITE_NATIVE | PROFIL / onboarding | 2 | body_profile | SPIGNOS_BODY_PRIVACY_AND_CONSENT_SPEC | moyen — RGPD, retrait effectif |
| Lecture du corps (Body Intelligence) | BLOCKED | PROFIL | 1 | body_intelligence · body_intelligence_inputs · muscle_scoring · radar | UX-LAB PROFILE (axes de l'octogone) · revue des revendications (aucune mesure inventée) · body_assessment_enabled désactivé en production | élevé — frontière entre profil d'allocation mesurable et estimation physique |
| Qualité de capture corporelle (coquille statique) | BLOCKED | PROFIL — photos de progression | 1 | — | photos de progression (conception · consentement · stockage privé) | faible |
| Photos de progression (face, profil, dos), privées par défaut | BLOCKED | PROFIL | 0 | body_profile | conception · consentement · stockage privé · chiffrement · aucune analyse physique avant un modèle validé | élevé — données sensibles |

## Progrès

| Fonction | Statut | Destination native | Routes | Propriétaire du domaine | Dépendances | Risque |
|---|---|---|---|---|---|---|
| Rapport de coach (synthèse en 10 blocs) | BLOCKED | PROGRÈS | 1 | coach_report · coach_inference · body_intelligence · narrative | UX-LAB PROFILE / PROGRÈS · moteur scientifique V2 (couches E0–E8) | élevé — prose dense héritée, revendications à revoir |
| Historique des séances (journal) | REWRITE_NATIVE | PROGRÈS | 1 | flight_recorder · session_state | MOB-05 | moyen |
| Historique d'un exercice | REWRITE_NATIVE | PROGRÈS (et depuis la séance) | 2 | exercise_history | MOB-05 | faible |
| Progrès (KPI, qualité, chronologie) | REWRITE_NATIVE | PROGRÈS | 1 | kpis · quality_score · timeline · progress_facts · progression_view | MOB-05 · UX-LAB PROGRÈS | moyen |
| Anciennes adresses redirigées (/physique, /dashboard, /rules) | DEPRECATE | aucune | 3 | — | — | nul — déjà dépréciées dans le code |

## Récupération

| Fonction | Statut | Destination native | Routes | Propriétaire du domaine | Dépendances | Risque |
|---|---|---|---|---|---|---|
| Check-in de forme du jour et son historique | REWRITE_NATIVE | MISSION (check-in) / PROGRÈS (historique) | 2 | readiness · recovery_contract · zone_recovery | MOB-12 récupération · moteur scientifique V2 (aucune valeur de récupération inventée) | moyen |

## Programmes

| Fonction | Statut | Destination native | Routes | Propriétaire du domaine | Dépendances | Risque |
|---|---|---|---|---|---|---|
| Bibliothèque des programmes modèles et lanceur | REWRITE_NATIVE | SÉANCE ou PROFIL — selon MOB-01 | 3 | launcher · loadout | MOB-06 | moyen — modèle d'interaction hérité (TRANSITIONAL) |
| Programmes personnels (créer, éditer, générer, valider, publier, versionner, lancer) | REWRITE_NATIVE | PROFIL — Programmes (selon MOB-01) | 16 | user_program_drafts · user_program_generator · user_program_quality_preview · user_program_publish · user_program_versioning · user_program_launch | MOB-06 bibliothèque · MOB-07 constructeur (V1 choisir → V4 créer de zéro) · slots d'intention du domaine | élevé — 16 routes, éditeur riche ; découper en V1 → V4 |
| Mon plan hebdomadaire et son matérialisation en brouillon | REWRITE_NATIVE | MISSION ou PROFIL — selon MOB-01 | 2 | weekly_planner · weekly_plan_materialization · planner_candidates | MOB-06 | moyen |
| Environnement d'entraînement concret (salle, équipement) | REWRITE_NATIVE | PROFIL / onboarding | 1 | equipment_model · environment_activation · environment_resolution | MOB-09 · planches d'équipement (assets PO) | moyen — conditionne la faisabilité des séances (start_blocked) |
| Exercice personnalisé de l'utilisateur | BLOCKED | bibliothèque d'exercices (MOB-08) | 0 | exercise_identity | MOB-08 · règle : pas de calibration, de substitution, d'illustration ni de biomécanique sans données | moyen — exercise_properties est le registre de substitution : ne pas créer d'arêtes implicites |

## Référence

| Fonction | Statut | Destination native | Routes | Propriétaire du domaine | Dépendances | Risque |
|---|---|---|---|---|---|---|
| Science — Muscle Focus et règles | BLOCKED | PROFIL ou référence — selon MOB-01 | 1 | bodymap_frames · sci_* | planches BodyParts3D autorisées en interne seulement (diffusion publique bloquée) · revue anatomique | moyen — licence et revue anatomique avant toute diffusion |
| Atlas des machines (catalogue d'exercices consultable) | REWRITE_NATIVE | bibliothèque d'exercices (MOB-08) | 1 | machine_atlas | MOB-08 · illustrations d'exercices (assets PO) | moyen |

## Social

| Fonction | Statut | Destination native | Routes | Propriétaire du domaine | Dépendances | Risque |
|---|---|---|---|---|---|---|
| Squads (groupes, invitations, défis, comparaison, partage) | REWRITE_NATIVE | PROFIL — espace social (place exacte fixée après MOB-01) | 16 | squad · challenge · sharing · compare | opérateur 2026-10-31 : le social migre dans l'app · MOB-01 coque · confidentialité des données partagées | moyen — 16 routes ; les surfaces sociales sont celles qu'on oublie (décision appliquée là où c'était commode) |
| Classement et profils publics | REWRITE_NATIVE | PROFIL — espace social (place exacte fixée après MOB-01) | 3 | leaderboard · performance · profile_metrics · radar | opérateur 2026-10-31 : le social migre dans l'app · MOB-01 coque · confidentialité des profils publics | moyen |

## Exploitation

| Fonction | Statut | Destination native | Routes | Propriétaire du domaine | Dépendances | Risque |
|---|---|---|---|---|---|---|
| Santé du service (sondes) | WEB_ONLY | aucune | 2 | backup_verifier | — | nul |
| Administration des séances (lister, exclure, supprimer) | WEB_ONLY | aucune | 4 | ownership · quality_score | — | faible |
