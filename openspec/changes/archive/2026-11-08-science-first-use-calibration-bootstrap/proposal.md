# Why
Le binding V3 admis au canonique d7de8aa exige sept réglages courants qualifiés. Cela permet de produire un plan observé limité, mais ne définit pas l'entrée d'une personne sans historique. Le protocole C3 existant décrit familiarisation/essai/observation/décision ; il manque un contrat d'accompagnement avant qualification, distinct d'un plan et d'une séance de travail.

# What Changes
- Proposer `first-calibration-encounter/1.0.0`, un contrat autonome réutilisant ContextKey, Setting, CalibrationEvent/Episode et les références C3 existantes. Aucun FirstPlan V4.
- Ouvrir l'interaction avec zéro réglage qualifié et un seul exercice à la fois. Séparer collecte d'information, exploration conditionnellement supportée, observation et qualification.
- Premier candidat d'admission : `leg-extensions-assises`, bilatéral, réalisation déjà curée ; dispositif réel, réglage compréhensible et instructions spécifiques sont nécessaires avant un essai. Le choix du réglage appartient à l'utilisateur avec assistance si nécessaire, pas à une prédiction logicielle.
- Faire qualifier une observation par les règles effectives C3 du profil V3, sans transformer un essai de calibrage en série de travail. Les six autres réalisations restent disponibles à leur qualification observée historique ; leur accompagnement initial positif exige une procédure candidate spécifique revue, pas une extension implicite de ce pilote.
- Après GO du delta : types/évaluateur pur/validateur/exports/tests et cas d'admission scientifique effectif du pilote. Aucun API/SDK/DB/UI/collecte/activation.

# Capabilities
## New Capabilities
- `science/first-use-calibration` : accompagnement borné depuis réglage inconnu vers observation utilisable.
## Modified Capabilities
Aucune. Le binding `initial-plan-v3-binding/1.0.0`, son protocole, ses sept préconditions et ses validateurs sont conservés octet pour octet.

# Impact
Nouveaux modules isolés proposés sous tools/science_calibration_bootstrap/, tests dédiés, exports sous docs/science/sci-p02-initial-policy/first-use-calibration-bootstrap/, ce change et un append au registre documentaire. Consommateurs PLAN inchangés ; handoff proposé dans [CONTRACT_AND_PLAN.md](../../../../docs/science/sci-p02-initial-policy/first-use-calibration-bootstrap/CONTRACT_AND_PLAN.md).

# Approval boundary
PROPOSED / NO_GO_BUILD / NOT_ADMITTED / NOT_SERVED. L'ancien GO observé et le GO de contrat V3 n'autorisent pas ce nouvel accompagnement positif. Demande opérateur : approuver le pilote/protocole proposé et son build isolé, sous revue scientifique du bundle effectif avant publication de toute admission. GO MERGE permanent après ce GO et contrôles ; aucun déploiement.

# Completion
Préparation : design/contrat/test specification/cas d'admission concrets et revue fraîche. Build futur : une vraie trajectoire d'évaluateur sur faits synthétiques explicitement étiquetés, avec observation qualifiée portable vers V3 et aucun faux plan positif. Le plan complet requiert encore sept observations réelles et le runtime PLAN ; le pilote ne ferme pas ces dépendances.
