# Context
Référence2cddf5d. V1 impose quinze crédits EXACT pour exposure_complete, une durée ESTIMATED dans budget, une sélection faisable par slot et prescription tracée représentable. V2 calcule un draft qualitatif et des réglages typés ; le producteur2.0.0 ne génère aucun candidate_plan et conserve POLICY_UNAVAILABLE. L'évaluateur d'admission1.0.0 et les diagnostics1.1.0-isolated sont livrés, leur registre vide reste figé. Les cinq faits minimaux sont objective, population_scope, sessions_per_week, session_budgets_minutes, limitations.

# Goals / Non-Goals
Définir exactement le prochain contrat réellement consommable et les autorités nécessaires à un premier protocole exécutable. Ne pas confondre complétude d'information et certitude biologique. Hors scope : nouvelle revue générale des muscles/catalogue, quatre pulls retenus inutilisés, UI/API/persistance/collecte/déploiement, équipement complet supposé, analyse de faiblesse depuis souhait, nouveaux nombres de dose/temps ou v1 modifié.

# Brainstorming / Options / Risques / Choix retenu
A. Conserver v1 : exige de calculer puis admettre sa comptabilité conventionnelle numérique et représenter tous les réglages ; le draft actuel ne le fait pas. B. Nouveau contrat : types honnêtes pour quinze zones, bootstrap et réglage non massique, mêmes exigences d'autorité/exécution. C. Renommer le draft READY ou déclarer UNKNOWN=0 : exclu. Proposition auteur : B, déjà recommandée au design précédent, à faire approuver comme évolution de contrat avant code. Aucun gain artificiel sur C6 : durée inconnue n'autorise toujours pas READY.

# Decisions
## D1 — Identités et négociation
Noms proposés : first-plan-request/2.0.0 et first-plan-recommendation/2.0.0. Blueprint v1 réutilisé comme faits, sans ajouter poids/taille obligatoires ; requirement profile versionné propre au successeur. Le profil conserve les cinq faits requis, expérience/poids/taille/priorités facultatifs et leur sémantique UNKNOWN/WITHHELD/CONFLICT. Enveloppe d'observations séparée typée, complète et incluse dans l'empreinte de décision ; aucune dépendance cachée sur historique non cité.

Le futur serveur PLAN annonce les versions supportées et choisit explicitement une version admise. Le client actuel v1 continue à refuser v2 ; pas de payload v2 dans une enveloppe v1. Pas de lecture de plan v1 convertie automatiquement en politique v2.

## D2 — Références et autorité
Le request contient as_of UTC, snapshot_ref/source_revision (future autorité PLAN), faits/provenances, observations/exercice/réalisation/appareil/côté, versions et référence de bundle demandé. Les métadonnées d'owner dans un corps ne constituent pas authentification ; SCI vérifie cohérence de sujet, PLAN ownership courant et état de consentement pertinent.

Le binding de confiance référence les décisions C1..C6 (statut réellement admis, auteur/reviewer/date/applicabilité), engine + code SHA, politique + digest, manifestes des sources/evidence, sélection/curation/pull/réalisation, contrat request/result, durée/protocole et critères de retrait. Aucun label APPROVED du caller, fixture ou simple hash ne crée l'autorité. Registre successeur distinct du registre vide1.0.0 : ancienne autorité et rejouabilité préservées. Les noms des versions futures ne sont pas des admissions.

## D3 — Allocation et prescriptions
Plan : identités uniques session/slot, cadence identique aux faits, intentions et candidats canoniques, ensemble de séries physiques égal à la somme des slots, dose/répétitions/repos/RIR-cible avec policy_ref et evidence_refs admis. Les conventions héritées (deux séries/intention,8–12,cible2RIR,120/90) ne sont ni réadmises ni modifiées par ce contrat. Leur applicabilité au bundle exact requiert C2.

Prescription = union discriminée :
- OBSERVED_SETTING : setting.kind/value/unit, load_semantics, context/equipment/realization/side, episode/event/acceptance refs et provenance qualifiée courante. Calibration1.1.0-isolated consommée, aucun transfert de charge entre exercices ni assistance convertie en kg. Réglage provisoire accepté ≠ vrai RIR/charge optimale.
- BOOTSTRAP_PROTOCOL : protocol_ref admis et étapes exécutables/familiarisation/essai/observation/acceptation-réessai-arrêt. Instruction source et transitions, pas simple texte CALIBRATION_REQUIRED sans marche à suivre. Charge initiale non connue et reported_rir inconnu autorisés en tant que faits, jamais remplacés par cible2RIR observée. Le nombre/règle d'essais et leur prise en compte temporelle doivent être réellement admis ; aucune valeur par défaut créée ici.

Les réalisations unilatérales non appairées restent bloquées tant que leur protocole/règle de temps ne sont pas admis. Tout concern/échec/restart sans autorité bloque la suggestion. Une étape en cours n'est pas déjà exécutée ; séries cibles distinctes des SetLog observés. Le builder historique warmup2/1 ne fournit pas ce protocole.

## D4 — Quinze zones, sans fausse précision
Conserver le vocabulaire zones-15-v1 : pecs,lats,upper_back,anterior_delts,lateral_delts,rear_delts,biceps,triceps,quads,hamstrings,glutes,adductors,calves,abs,hip_flexors.

Une déclaration par zone, ni doublon ni omission : zone, role_status, contributions sourcées et limites. role_status proposé SUPPORTED_ROLES / UNKNOWN / NO_SUPPORTED_ROLE_IN_SELECTED_SET ; le dernier signifie absence de rôle supporté dans cette sélection, jamais absence physiologique de travail/croissance. Les contributions portent exercice/slot/réalisation/role et références admises, pas un pourcentage d'activation. Le rôle pectoral G17 ne s'applique que sous sa qualification exacte, sans fraction inventée.

coverage_report_complete signifie quinze déclarations présentes, pas crédit exact. credited_sets reste absent sans convention numérique séparément admise ; si cette option est un jour utilisée : credit_policy_ref, borne EXACT/LOWER_BOUND/UNKNOWN, valeur nulle si UNKNOWN et limites explicites. Compter des séries physiques affectées à un rôle est une convention de description qui peut chevaucher d'autres zones, pas un volume efficace individuel mesuré. Ne pas en dériver un score de faiblesse/progrès. Réponse individuelle NOT_ESTIMATED.

## D5 — Durée et gates READY
Durée proposée : état UNKNOWN / CONDITIONAL_DIAGNOSTIC / SUPPORTED ; budget déclaré séparé ; lower/upper/unit, base_kind ADMITTED_MODEL / ADMITTED_PRODUCT_CONVENTION, basis_ref/version/provenance/applicability/limitations. UNKNOWN et diagnostic ne portent pas une upper admise par erreur. Une convention ne prétend pas fournir probabilité individuelle validée. Un intervalle de fixture, une moyenne ou un simple titre45min ne suffit pas.

READY v2 exige simultanément : inputs suffisants/non conflictuels, scope/population pris en charge, six gates effectivement admises sur bundle exact, allocation revue cadence-cohérente, toutes réalisations sélectionnées faisables/qualifiées, prescription opérationnelle couvrant bootstrap éventuel, rapport de zones complet et honnête, base temporelle applicable complète dont upper≤budget, versions/pins/fingerprints vérifiés. Un temps qui ne couvre pas essais/préparation/opérations ne passe pas. Absence de C6 → POLICY_UNAVAILABLE avec motif TIME_UNCERTAIN, jamais « ajoute ton poids ».

Aucun nouveau mode « READY malgré temps inconnu » n'est proposé ni approuvé. Un tel choix changerait le produit et nécessite une décision/contrat propres, pas une façon de contourner l'admission.

## D6 — Résultats et consommation
Statuts métier conservés sémantiquement : READY, INSUFFICIENT_DATA, CONFLICTING_DATA, POLICY_UNAVAILABLE, CONSTRAINT_UNSATISFIABLE, REVIEW_REQUIRED. Transport pending/unknown/NOT_SERVED séparé. Assessment nomme les champs réellement manquants/conflits. Blockers identifient gate/code/source et action supportée. Confidence : individual_response NOT_ESTIMATED ; faisabilité distincte de qualité de preuve et limites, aucun score numérique nouveau.

Le result porte contract_version, engine/policy/bundle refs, subject/snapshot refs, request_fingerprint, full_evaluation_fingerprint, binding_digest, generated_as_of, admission/revocation refs et optional candidate_plan. READY est absent du vrai producteur tant que ses conditions manquent. Un plan ne prouve pas création de séance ; la commande possédée/idempotente et son suivi sont PLAN.

## D7 — Fichiers, séquence et risques de collision
Futur build contrats : nouveau tools/science_contracts/blueprint_first_plan_v2.py et artefacts docs/science/sci-p01-p02/v2/, tests dédiés ; sans modifier v1 ni FirstPlanClient. Contrat public définitif seulement après revue du présent delta. Futur binding/producteur : nouveaux modules/version/registre SCI dédiés après vraies admissions ; ne pas relabelliser les sorties 2.0.0.

Les pins v2 actuels incluent FirstPlanClient/son schéma et les sources parent. Un futur changement PLAN doit être coordonné avec une nouvelle référence/version et un dispositif de rejeu historique ; ne pas mettre à jour silencieusement les anciens hashes pour faire passer une CI. La manière de conserver les snapshots sources historiques doit être spécifiée avant ce changement partagé. Aucun fichier backend/schema/mobile n'est écrit en concurrence ici.

# Migration Plan
Côte à côte, pas de migration DB ni backfill. Négociation explicite v1/v2 dans PLAN après GO propre ; le serveur ne doit pas annoncer une version non admise/servie. Retour : retirer le binding v2 et ses ports futurs, préserver snapshots/séances/faits existants ; aucun fallback SCI depuis MISSION.

# Open Questions
Choix du contrat successeur et de ses unions à approuver avant apply. C3 instruction initiale/arrêt/réessai applicable à admettre. C6 : aucune donnée réelle ni convention temporelle applicable approuvée disponible ; voir READY_GATE_DECISIONS.md. Identité/autorisation des responsables et moyens réels de collecte restent à fournir, avec politique DATA pertinente. Ces preuves ne sont pas accordées par « ok go ».
