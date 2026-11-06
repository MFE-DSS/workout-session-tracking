# Curation01 — preuves et limites

6 novembre2026. Recherche primaire, métadonnées PubMed recoupées via Europe PMC ; accès détaillé ci-dessous. Les champs population/limites ne valent pas généralisation au novice universel. Aucun protocole chiffré de ces études n’est importé comme dose initiale.

## E0 reste l’autorité unique

Réutilisation : EV-60 modalités ; EV-62 quadriceps ; EV-63/64 actions et synergies ; EV-65 limites longueur/région ; EV-66 biarticularité ; EV-68 variation ; EV-70 EMG corroboratif seulement ; EV-71 hiérarchie longitudinale adaptée → action chargée/anatomie → UNKNOWN. Aucun nouvel identifiant E0 n’est injecté dans les rôles ou le producteur. Le delta compatible E0 est proposé/non appliqué dans [evidence-delta.v1.json](evidence-delta.v1.json), pas un deuxième registre chargé au runtime.

Les résumés E0 historiques « hypertrophie identique » (EV-60) ou une équivalence universelle de longueur (EV-65) sont lus avec les limites réelles des études : absence de différence détectée ne prouve pas une équivalence générale. Pas de réécriture silencieuse de l’autorité épinglée.

## Vérifications bibliographiques et décisions

### EV-62 — PMID 41630124 ; DOI 10.1249/MSS.0000000000003957

[Source primaire](https://pmc.ncbi.nlm.nih.gov/articles/PMC13215645/). Accès : FULL_TEXT_XML_READ_VIA_EUROPE_PMC. Population : 17 untrained adults.

Knee extension and leg press differ in RF response; press also grows gluteus maximus and adductor magnus. Unilateral Life Fitness machines, standardized hip start, hip-width straight foot at top edge; no high-wide versus low-foot comparison.

Décision : REUSE_AND_VERIFY_EXISTING_SOURCE.

### EV-62 — PMID 34743671 ; DOI 10.1080/02640414.2021.1929736

[Source primaire](https://pubmed.ncbi.nlm.nih.gov/34743671/). Accès : PRIMARY_ABSTRACT_VIA_EUROPE_PMC. Population : Adults; exact sample not available from abstract.

Smith squat and leg-extension regional responses differ. Within-group significance patterns alone do not demonstrate every between-group difference; not feet-forward Smith or cable/reverse-Nordic trial.

Décision : BIBLIOGRAPHIC_CORROBORATION_NOT_NECESSARY_NEW_CLAIM.

### EV-62 — PMID 41379528 ; DOI 10.1519/JSC.0000000000005338

[Source primaire](https://doi.org/10.1519/JSC.0000000000005338). Accès : PRIMARY_ABSTRACT_VIA_EUROPE_PMC_AND_PUBLISHER. Population : 63 untrained young women;8wk.

Leg extension favored RF; Smith squat favored distal VL. Ultrasound selected sites; specific trained conditions; no exact cable or feet-forward transfer.

Décision : BIBLIOGRAPHIC_CORROBORATION_NOT_NECESSARY_NEW_CLAIM.

### EV-64 — PMID 37877099 ; DOI 10.3389/fphys.2023.1279170

[Source primaire](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2023.1279170/full). Accès : FULL_TEXT_PRIMARY_PUBLISHER. Population : 34 untrained college-aged completers;9wk.

Squat and hip thrust produced similar gluteal growth; squat more thigh growth. Not leg press, hack or feet-forward Smith; acute EMG did not consistently predict outcome. [Correction2026 vérifiée](https://doi.org/10.3389/fphys.2026.1987823) : précise don de matériel/conflits d’intérêts et enregistrement rétrospectif ; aucun changement de résultat annoncé. Cette limite s’ajoute aux limites de configuration.

Décision : REUSE.

### EV-66 — PMID 33009197 ; DOI 10.1249/MSS.0000000000002523

[Source primaire](https://pmc.ncbi.nlm.nih.gov/articles/PMC7969179/). Accès : PRIMARY_ABSTRACT_AND_FULL_TEXT_XML. Population : 20 healthy untrained adults;12wk.

Seated versus prone knee-flexion training yielded differing biarticular hamstring responses. Neither condition was an RDL, good morning or back extension; BF short head is monoarticular.

Décision : REUSE.

### PROPOSED_HAMSTRING_SPECIFICITY — PMID 38857522 ; DOI 10.1249/MSS.0000000000003490

[Source primaire](https://pmc.ncbi.nlm.nih.gov/articles/PMC11419281/). Accès : PRIMARY_ABSTRACT_AND_FULL_TEXT_XML. Population : 42 healthy young males;12wk.

Different eccentric knee-flexion exercises produced different hamstring/head patterns. No hinge arm; supports specificity limitation, never direct hinge effectiveness or ranking.

Décision : OPTIONAL_NEW_E0_CLAIM_IF_NEEDED.

### PROPOSED_CALF_KNEE_POSITION — PMID 38156065 ; DOI 10.3389/fphys.2023.1272106

[Source primaire](https://pubmed.ncbi.nlm.nih.gov/38156065/). Accès : PRIMARY_ABSTRACT_AND_FULL_TEXT_XML_PMC10753835. Population : 14 untrained adults;unilateral machines;12wk.

Knee-extended standing versus knee-flexed seated training differed for gastrocnemius and whole triceps surae; soleus response similar. No nontraining control; small sample; not bodyweight or press equivalence; no seated soleus-superiority finding.

Décision : NEW_E0_CLAIM_REQUIRED_FOR_REGIONAL_CALF_DESCRIPTOR.

### PROPOSED_CALF_KNEE_POSITION — DOI 10.1007/s42978-024-00299-4

[Source primaire](https://www.sciopen.com/article/10.1007/s42978-024-00299-4?issn=2096-6709). Accès : PRIMARY_PUBLISHER_ABSTRACT. Population : 30 trained young adults;unilateral;8wk.

Straight-leg toe press favored medial gastrocnemius thickness relative to seated calf; lateral gastrocnemius and soleus results equivocal. Selected thickness sites, no whole-muscle volume or proof soleus superiority; university accepted manuscript link was403.

Décision : PRIMARY_CORROBORATION.

### EV-65 — PMID 40570881 ; DOI 10.1055/a-2615-4935

[Source primaire](https://pubmed.ncbi.nlm.nih.gov/40570881/). Accès : PRIMARY_REVIEW_ABSTRACT. Population : 12 young-adult studies.

Regional pooled length effects small with ambiguity; not universal length ranking. Limited muscle-length contrast and pooled designs; do not override specific direct trials.

Décision : REUSE_WITH_CAUTION.

### PROPOSED_LENGTH_CAUTION — PMID 41777276 ; DOI 10.1055/a-2733-7605

[Source primaire](https://pmc.ncbi.nlm.nih.gov/articles/PMC12951042/). Accès : FULL_TEXT_XML_READ. Population : Unstructured narrative synthesis.

Length, ROM, exercise selection and external torque interact. Narrative not systematic; its soleus narrative is stronger than Burke primary abstract; use primary result.

Décision : NO_NEW_CLAIM_NEEDED.

### OPTIONAL_REVERSE_NORDIC — PMID 30293403 ; DOI 10.23736/S0022-4707.18.08873-4

[Source primaire](https://pubmed.ncbi.nlm.nih.gov/30293403/). Accès : PRIMARY_ABSTRACT. Population : 26 subjects;8wk eccentric training.

RF architecture changed following eccentric reverse Nordic protocol. Not direct canonical bidirectional exercise; uncontrolled training/detraining sequence, not comparative superiority.

Décision : NO_NEW_E0_NECESSARY_FOR_ANATOMY_ADMISSION.

### EV-68 — PMID 35438660 ; DOI 10.1519/JSC.0000000000004258

[Source primaire](https://pubmed.ncbi.nlm.nih.gov/35438660/). Accès : Verified Europe PMC core metadata and abstract; publisher retrieval returned402.. Population : 8 studies,241 young men.

Supports purposeful systematic variation, not universal rankings. Limited populations and variation protocols; not proof of candidate-specific superiority.

Décision : REUSE_EXISTING_E0.

### EV-60 — PMID 37582807 ; DOI 10.1186/s13102-023-00713-4

[Source primaire](https://doi.org/10.1186/s13102-023-00713-4). Accès : Verified Europe PMC core metadata/abstract; open full text available as PMC10426227.. Population : Adults18-60,13 studies overall;5 hypertrophy studies.

No detected hypertrophy difference; strength adaptations are modality-specific. No proof of universal equivalence; heterogeneous measurements and limited hypertrophy evidence.

Décision : REUSE_EXISTING_E0.

### PROPOSED-UC-LAT-01 — PMID 40692697 ; DOI 10.3389/fphys.2025.1611468

[Source primaire](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2025.1611468/full). Accès : Full text inspected at publisher and abstract verified Europe PMC.. Population : 24 resistance-trained men/women,8weeks,within-person unilateral allocation.

Comparable lateral-delt growth with DB/cable raises at matched ROM in this trial; no universal cable superiority. Cable aligned approximately with hand; not behind-back low-cable. Matched ROM, trained adults, ultrasound sites, high-volume failure protocol, not initial bootstrap prescription validation.

Décision : PROPOSED_E0_DELTA_NOT_PROMOTED.

### PROPOSED-UC-ANAT-01 — PMID 18691376 ; DOI 10.1111/j.1469-7580.2008.00965.x

[Source primaire](https://pmc.ncbi.nlm.nih.gov/articles/PMC2644775/). Accès : Full text inspected PMC2644775.. Population : 8 older human cadaver upper extremities,81-98years.

Subregional shoulder leverage depends on joint position and plane; anatomical capacity does not uniquely settle mixed-exercise contribution magnitude. No living loaded exercise force sharing or hypertrophy; elevation limited to120degrees; cannot settle vertical-pull pec SECONDARY/MINOR or unspecified rear-delt trajectory.

Décision : PROPOSED_E0_DELTA_NOT_PROMOTED.

### PROPOSED-UC-ANAT-02 — PMID 23916077 ; DOI 10.1016/0268-0033(94)90057-4

[Source primaire](https://pubmed.ncbi.nlm.nih.gov/23916077/). Accès : PubMed abstract inspected.. Population : Human dissection/volumetric anatomy; sample size not verified from abstract.

Trapezius attachments support clavicular/scapular mechanics; upper fibres raise shoulder girdle through clavicle rather than simple direct scapular pull. Does not settle PRIMARY versus SECONDARY in unspecified DB upright-row configuration; no hypertrophy study.

Décision : PROPOSED_E0_DELTA_NOT_PROMOTED.

### PROPOSED-UC-PRESS-01 — PMID 32922646 ; DOI 10.70252/fdnb1158

[Source primaire](https://intjexersci.com/files/ijes/vol13/iss6/12.pdf). Accès : Europe PMC core metadata/abstract verified; publisher PDF search excerpt identifies44degree incline.. Population : 47 untrained young men,8weeks,onceweekly training.

Angle may affect one measured pec site; preserve angle identity without exact transfer to DB30 or Smith30. Barbell comparison at44degrees; only one of3 thickness sites differed; insufficient for exact candidate regional superiority.

Décision : PROPOSED_OPTIONAL_E0_DELTA_NOT_REQUIRED_FOR_ADMISSION.

## Correction de portée de la presse

PMID41630124 : le texte intégral décrit une presse unilatérale Life Fitness, pieds à largeur de hanches, orientés droit, bord supérieur de la plateforme ; il ne compare pas les deux variantes canoniques pieds bas / hauts écartés. Le résultat ne valide donc pas le « a fortiori » des notes historiques. L’overlay remplace seulement leur base longitudinale par action chargée/anatomie, sans classer arbitrairement le rôle glute en SECONDARY. Le high-wide reste non admis et son rôle historique PRIMARY n’est pas promu comme nouveau résultat scientifique.

## Décisions de région utilisables

- Quadriceps : extension du genou et position de hanche rendent le droit fémoral pertinent ; une presse/squat n’établit pas une exposition régionale identique. Aucun huitième slot ajouté.
- Ischio-jambiers : extension de hanche des chefs biarticulaires ne démontre ni flexion de genou ni couverture du chef court du biceps fémoral. Un hinge n’est pas une couverture totale.
- Mollets : conserver genou étendu/fléchi. Les essais ne démontrent pas une supériorité d’hypertrophie du soléaire en position assise. Presse et poids du corps ne reprennent pas automatiquement les effets de machine.
- Épaule : ne pas transférer le câble unilatéral à hauteur de main de Larsen au câble bas derrière le dos. Les bras de levier anatomiques ne résolvent pas à eux seuls pec/rear delts des tirages.
- Pectoraux/dos : angle et trajectoire sont des identités d’exécution, pas des pourcentages de croissance, une largeur/épaisseur chiffrée ou une hiérarchie universelle.

Le récit2026 PMID41777276 est explicitement une revue **non structurée**, pas une nouvelle synthèse systématique ni une autorité supérieure aux résultats primaires. Les affirmations soléaire sont bornées par Kinoshita/Burke.
