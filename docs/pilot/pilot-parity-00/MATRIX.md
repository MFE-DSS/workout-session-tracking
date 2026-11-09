# PILOT-PARITY-00 — matrice de continuité

**9 novembre2026 — base2b831411 ; 32 besoins nommés +4 parcours d’acceptation. Parité pilote NON ÉTABLIE.**

Source structurée exhaustive : [capabilities.v1.json](capabilities.v1.json). Chaque ligne contient les douze champs demandés, les preuves serveur/client, la sémantique des données et le statut du build installé. Captures/export pilote non reçus (EV-PILOT-00) ; les priorités ci-dessous sont des propositions issues du mandat, pas des usages observés du pilote.

SERVED_NATIVE est réservé à une fonction prouvée sur un build cible compatible. Aucun build QA autonome actuel n’est attesté : **0/36 capacités attestées SERVED_NATIVE**, sans nier le câblage réel du compte, de MISSION historique, de séance et du bilan. PARTIAL distingue ces sous-ensembles réellement présents des fonctions absentes. DOMAIN_ONLY n’est pas un service mobile.

| ID | Capacité demandée | État | Priorité proposée | Prochain scope |
|---|---|---|---|---|
| B01 | Poids quotidien, saisie et correction | PARTIAL | P0 | BODY-01 |
| B02 | Mesures brutes et moyenne de poids sept jours | PARTIAL | P0 | BODY-01 |
| B03 | Estimation de masse grasse | BLOCKED | P2 | BODY-IMPORT-01 (non créé) |
| B04 | Estimation de masse musculaire | BLOCKED | P2 | BODY-IMPORT-01 (non créé) |
| B05 | Historique des mesures | PARTIAL | P0 | BODY-01 |
| B06 | Mensurations au ruban et évolutions | DOMAIN_ONLY | P0 | BODY-01 |
| B07 | Périodes historiques sélectionnables | PARTIAL | P1 | BODY-01 |
| T01 | Séances par semaine | PARTIAL | P0 | MOB-05 |
| T02 | Historique de charge par exercice et progression | DOMAIN_ONLY | P0 | MOB-05 |
| T03 | Modèles de séances, choix du programme | DOMAIN_ONLY | P0 | MOB-06 (non créé) |
| T04 | Création personnelle de séance/programme | DOMAIN_ONLY | P1 | MOB-07 (non créé) |
| T05 | Planification hebdomadaire | PARTIAL | P1 | MOB-06 puis SCHED-01 si dates requises (non créés) |
| T06 | Séances prévues versus réalisées | PARTIAL | P0 | MOB-05 |
| T07 | Versionnement des programmes | DOMAIN_ONLY | P1 | MOB-06/MOB-07 (non créés) |
| N01 | Calories quotidiennes | NOT_IMPLEMENTED | P0 | NUT-01 |
| N02 | Protéines quotidiennes | NOT_IMPLEMENTED | P0 | NUT-01 |
| N03 | Glucides quotidiens | NOT_IMPLEMENTED | P0 | NUT-01 |
| N04 | Lipides quotidiens | NOT_IMPLEMENTED | P0 | NUT-01 |
| N05 | Objectifs différents entraînement/repos | NOT_IMPLEMENTED | P0 | NUT-01 |
| N06 | Journal quotidien et corrections | NOT_IMPLEMENTED | P0 | NUT-01 |
| N07 | Synthèse hebdomadaire nutrition | NOT_IMPLEMENTED | P0 | NUT-01 |
| N08 | Complétude des jours saisis | NOT_IMPLEMENTED | P0 | NUT-01 |
| N09 | Détails facultatifs des aliments | NOT_IMPLEMENTED | P2 | NUT-02 si justifié (non créé) |
| R01 | Enregistrements sommeil | PARTIAL | P1 | REC-01 (non créé) |
| R02 | Tendances historiques sommeil | PARTIAL | P2 | REC-01 (non créé) |
| R03 | Import HealthKit/Health Connect | NOT_IMPLEMENTED | P2 | HEALTH-01 (non créé) |
| D01 | PDF d’entraînement téléversé | NOT_IMPLEMENTED | P1 | DOC-01 (non créé) |
| D02 | PDF nutrition téléversé | NOT_IMPLEMENTED | P2 | DOC-01 (non créé) |
| D03 | Versions des documents | NOT_IMPLEMENTED | P1 | DOC-01 (non créé) |
| D04 | Extraction/import de programme | NOT_IMPLEMENTED | P1 | IMPORT-01 (non créé) |
| D05 | Questions sur les documents | NOT_IMPLEMENTED | P2 | DOC-QA-01 si justifié (non créé) |
| D06 | Disponibilité/rendez-vous du coach | OUT_OF_CORE | OUT_OF_CORE | Aucun scope justifié |
| A01 | Se connecter | PARTIAL | P0 | RELEASE-01 existant |
| A02 | Voir et terminer une séance | PARTIAL | P0 | RELEASE-01 et MOB-04 |
| A03 | Récupérer une séance interrompue | PARTIAL | P0 | RELEASE-01 et MOB-04 |
| A04 | MISSION réelle maintenant/pourquoi | PARTIAL | P0 | MOB-04 (proposition sans GO) |

## Lecture et arbitrage

- Aucun besoin constaté uniquement dans le manifeste ne devient livré. Le manifeste produit/science est conjoint, pas deux autorités séparées. MOB00 reste la carte des routes web ; cette matrice complémentaire conserve ses propres états de parité.
- Priorité proposée : MISSION et historique/exercice (MOB04/05), puis saisie corporelle/nutrition manuelle (BODY01/NUT01). Sélection de programme native reste un manque P0 à ouvrir en MOB06 ; le builder/versionnement natifs relèvent de MOB07. Aucun calendrier daté n’existe dans le planner actuel.
- Les anciennes admissions/calibrages sont livrés et non rouverts. Réglages machine/par haltère, faits/prescription et dérivés SCI NON_EVALUABLE restent séparés.
- Nutrition manuelle ne requiert pas une nouvelle enquête SCI ; les recommandations/estimations futures gardent leurs contrats. Sommeil readiness n’est pas durée capteur. Mensuration n’est pas tissu musculaire.
- Captures/export réels, politique DATA et cible installable demeurent nécessaires avant toute parité/appareil/activation. Aucun faux placeholder ne remplace une capacité indisponible.
