# SCI-P02-CANDIDATE-CURATION-01 — curation partiellement admise

6 novembre2026. **CURATION_PARTIALLY_ADMITTED · NOT_SERVED · READY_NOT_PRODUCED**. Base canonique `7e295c0e00aa6d00595efe4078e8d212ca61c869`. Les SHA livrés/CI seront consignés après publication ; aucune réussite distante anticipée.

## Brainstorming / Options / Risques / Choix retenu

Plan écrit avant code dans [candidate-curation-01.md](../../../../openspec/changes/science-initial-plan-policy/candidate-curation-01.md) : éviter mutation de catalogue/E0/pins et faux rôle complet ; choisir overlay versionné et résolveur pur non classant. Les données, crédits, E0 et sorties historiques restent inchangés. La correction porte sur la base de preuve de deux variantes, pas une nouvelle catégorie musculaire.

## État canonique et verdict

Contrats Blueprint/FirstPlan v1 ; producteur isolé1.0.0 et politique0.1.0-proposed conservés ; décisions0.2.0-partially-admitted de SCI-P02-ADMISSION-01 non rouvertes. Overlay `initial-candidate-curation/1.0.0`, aucune liaison au producteur.40candidats/sept intentions :20 admissions conditionnelles,9 alternatives conditionnelles,7 preuves insuffisantes,4 non admis au périmètre initial. **Aucun exercice choisi par défaut.**

## Résultat par intention

### initial_quad_v1

10 candidats : 4 conditionnels, 3 alternatives, 0 preuves insuffisantes, 3 non admis. RF/vaste et position de hanche conservés. Câble posture inconnue, sissy résistance indéfinie et presse high-wide restent retenus hors admission ; pas de comparaison pieds haut/bas déduite de la presse étudiée.

### initial_press_v1

6 candidats : 4 conditionnels, 2 alternatives, 0 preuves insuffisantes, 0 non admis. Six candidats conditionnels dont dips/pompes alternatives dépendantes de capacité. Angle préservé ; aucun partage chiffré du pectoral ni charge transférée.

### initial_row_v1

5 candidats : 4 conditionnels, 0 alternatives, 1 preuves insuffisantes, 0 non admis. Quatre candidats conditionnels ; rowing large retenu car trajectoire et rôle lats non résolus. Banc/poitrine décrivent un support, pas une efficacité supérieure.

### initial_hinge_v1

4 candidats : 2 conditionnels, 1 alternatives, 0 preuves insuffisantes, 1 non admis. Deux RDL conditionnels et back-extension alternative ; good morning retenu car tenue inconnue/upper_back UNKNOWN. Extension de hanche ne couvre pas automatiquement flexion de genou/chef court.

### initial_vertical_pull_v1

5 candidats : 0 conditionnels, 0 alternatives, 5 preuves insuffisantes, 0 non admis. **CATALOG_GAP** : cinq candidats retenus pour rôles pecs/rear delts non résolus, bien que l’intention lat-primary soit défendable. Pas de remplacement par rowing, pas de nouveau pool.

### initial_lateral_delt_v1

6 candidats : 5 conditionnels, 0 alternatives, 1 preuves insuffisantes, 0 non admis. Cinq candidats conditionnels ; upright-row haltères retenu pour upper_back UNKNOWN. Le câble large canonique est un upright row, pas un face pull. Pas de supériorité câble bas derrière le dos.

### initial_calf_v1

4 candidats : 1 conditionnels, 3 alternatives, 0 preuves insuffisantes, 0 non admis. Machine debout conditionnelle ; presse, assis et poids du corps alternatives distinctes. Genou et faisabilité des répétitions restent à confirmer. Assis n’est pas une couverture équivalente du gastrocnémien.

## UNKNOWN et couverture

[Delta de rôles](ROLE_RESOLUTION.md) :14→14, aucune conversion pour satisfaire le contrat. [Matrice7×15 et fixtures](coverage-and-fixtures.v1.json) : chaque zone distingue DIRECT, INDIRECT_KNOWN, MINOR_KNOWN, UNKNOWN et NONE_KNOWN. Deux vues : pool entier et seuls candidats admissibles. NONE_KNOWN signifie aucune contribution répertoriée, pas zéro physiologique. La matrice n’est pas une séance sélectionnée ni une preuve de couverture esthétique complète.

Quads, pecs, haut du dos, ischios biarticulaires, deltoïde latéral et mollets ont des cibles directes possibles ; lats et plusieurs synergies sont connues dans certains rowings mais cela ne remplace pas l’intention verticale vide. Biceps/triceps/deltoïdes antérieurs/postérieurs, glutes/adducteurs et tronc reçoivent des contributions variables selon candidat. Les absences et UNKNOWN par zone restent lisibles sans somme fictive de sets.

## Régions, support et préparation

Les limites régionales actionnables et les preuves sont dans [EVIDENCE.md](EVIDENCE.md). Le support est descriptif (banc, poitrine, siège, guidage Smith, station, auto-stabilisation), non ordinal. SEATED_SUPPORT désigne une assise, pas un dossier déduit ; détails à confirmer. Ni `machine_unspecified`→stack/plate, ni stabilité→meilleure hypertrophie. Aucun label universel « débutant ».

Chaque candidat comporte calibration_mode, faits à confirmer, classes de préparation et invalidations dans [candidates.v1.json](candidates.v1.json). Répartition des classes de calibration : ASSISTANCE_UNSPECIFIED=2, BODYWEIGHT_REALISATION=7, CABLE_UNSPECIFIED=9, FREE_BARBELL=1, FREE_DUMBBELL=8, MACHINE_UNSPECIFIED=11, SMITH_RESISTANCE=2. Les montants, incréments, contrepoids et réalisations sont propres au dispositif ; aucune charge initiale enkg. Poids du corps ne signifie pas8–12 répétitions atteignables ; toutes les faisabilités restent UNCONFIRMED. Unilatéral conserve une réalisation par côté sans transfert de charge.

Préparation des40candidats : CONTEXT_DEPENDENT, confirmation setup/contexte + calibration, familiarisation si non familier. Ces catégories opérationnelles sont des besoins, pas un protocole d’échauffement validé. Aucun nombre de séries ou minutes. Confirmation de disponibilité ne prouve pas calibration, tolérance ou préparation. Aucun inventaire, salle complète ou TTL.

## Preuves et fichiers

E0 existant réutilisé ; deux nouveaux claims régionaux proposés sous forme de patch E0 **non appliqué**, avec population/provenance/limites. Anatomie/EMG ne deviennent pas autorité de volume ou PRIMARY par défaut. Sources et empreintes avant analyse dans [sources.json](sources.json). Le résolveur charge seulement l’overlay relu avec hashes et bornes, lit les confirmations dans leur contexte v1, conserve exclusions/limitations, rend un ensemble non classant et un fingerprint reproductible. Les fixtures générées exercent contexte inconnu et contexte synthétique confirmé sans READY.

## Tests et revues

TDD observé :18échecs/1réussite avant module ;19réussites après ; omission du jeu de sources reproduite rouge puis corrigée (22réussites). Les résultats finaux, revue scientifique fraîche et revue code indépendante sont consignés dans VERIFICATION.md après exécution. Les tests ne prouvent pas la validité scientifique.

## Runtime et handoff

**NOT_SERVED**. Aucun import de curation dans producteur/service, aucune API/UI/mobile/baseline, migration, dose, durée, charge ou déploiement. **READY_NOT_PRODUCED** ; les onze sorties historiques sont protégées. Les consommateurs FirstPlanClient et MISSION ne reçoivent aucun faux READY. Cette opération seule ne ferme ni sélection complète, ni temps positif, ni PLAN/MOB03.

Le prochain travail peut réutiliser40dispositions,29admissions conditionnelles, classes et matrice sans les confondre avec29exercices exécutables. E0 partagé reste inchangé ; sa promotion doit préserver sources_digest et pins historiques.

## NEXT SCIENCE SPIKE

**SCI-P02-PULL-EXPOSURE-RESOLUTION-01** : résoudre de manière bornée l’exécution et la contribution encore inconnues d’au moins un des cinq candidats verticaux existants, ou proposer explicitement un contrat d’incertitude si la catégorie exacte n’est pas soutenable. Pas d’élargissement du pool, pas de MINOR par défaut. Ce blocage de sélection reste en amont d’un plan complet : la préparation/calibration/temps positif n’est donc pas choisie automatiquement malgré son intérêt ultérieur. Aucun GO BUILD du prochain spike n’est déduit de ce handoff.

## Publication vérifiée

PR[#362](https://github.com/MFE-DSS/workout-session-tracking/pull/362), HEADae0169137da3e5e91075ce9fd9f3b1d556dcb2d6, merge1c48301bb855733a610d376ba6d58219a00fe5c4. CI PR42220266909 et canonique42222587746 : completed/success,9jobs chacune,7383backend/3ignorés,54suites/676mobile+TypeScript. Sonar PR Quality Gate OK/0nouvelle issue ouverte ; canonique ERROR hérité, consultatif selon GOV-SONAR-01. Preuves, corrections de tests et limites dans [VERIFICATION.md](VERIFICATION.md). Opération de curation livrée ; admission scientifique partielle, change global/PLAN/MOB03 ouverts, aucun runtime ou déploiement.
