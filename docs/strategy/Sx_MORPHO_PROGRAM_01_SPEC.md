# Sx_MORPHO_PROGRAM_01 — Morphology-Aware Programming Architecture (SPEC)

**Cycle :** Morphology Program (nouveau) · **Type :** SPEC-ONLY (0 code applicatif, 0 migration, 0 schéma implémenté)
**Statut :** PR PENDING · **Tier attendu :** DOCS
**Amont référencé (additif, jamais redéfini) :**
- `SPIGNOS_BODY_SIGNAL_MODEL_SPEC.md` (Sx Body 01 — faits → mesures confirmées → ratios dérivés → priorités) — **parent direct de la moitié amont** ; SPEC-ONLY, `Sb Body 04 Archetype Engine` **jamais construit**.
- `SPIGNOS_BODY_INTELLIGENCE_ROADMAP.md` §4/§5 — réserve `Sb Body 04` (Archetype) + `Sb Body 05` (Link to Training Engine) = **l'épine de ce pipeline** ; jamais construits.
- `SPIGNOS_BODY_MANUAL_PROFILE_BUILD_SPEC.md` + `app/models/measurement.py` (`BodyMeasurement`) + `app/models/body_consent.py` — **stockage des faits corporels bruts déjà construit, flag-gated OFF**.
- `SPIGNOS_BODY_INTELLIGENCE_V2_SPEC.md` + `app/services/body_intelligence.py` — classification runtime `measured / derived / inferred / not_deductible` + **discipline « une seule priorité »** ; construit, flag OFF.
- `Sx_BI_01_BODY_INTELLIGENCE_ACTIVATION_SPEC.md` §13 — **garde-fou le plus strict du repo** (adopté ici).
- `Sx_CUSTOM_PROGRAM_01/02/03` + `app/services/substitution.py` (Sx_22a) + `app/services/user_program_generator.py` — **la queue déjà construite** (slots, substitution N1/N2/N3, génération déterministe) ; `Sx_CUSTOM_PROGRAM_01 §13` **réserve déjà** l'intégration des signaux corporels comme **V2 additive**.

> Cette spec **réalise et unifie** les slots réservés `Sb Body 04` + `Sb Body 05` et le hook « body-signal V2 » de `Sx_CUSTOM_PROGRAM_01 §13`, sous le **garde-fou strict** de BI-Activation. Elle **ne construit rien** : elle définit l'architecture et la file de build.

---

## §0. Position, non-goals, garde-fou d'écriture

**Ce que cette spec fait** : définir comment des **faits corporels bruts** (fournis par l'opérateur ou saisis via le profil manuel déjà construit) deviennent des **descripteurs de morphologie interprétés**, puis des **priorités d'entraînement**, puis des **intentions de slots d'exercice**, résolus en **exercices concrets** via la substitution existante, filtrés par la **disponibilité d'équipement (Fitness Park)**, et assemblés en **programmes custom déterministes** — sans casser la substitution ni la génération déterministe existantes.

**Ce que cette spec ne fait pas** (hard constraints de la mission, tous tenus) : aucun code applicatif · aucune migration · aucune implémentation de modèle/schéma · aucun stockage de photo · aucun asset image brut committé · aucun diagnostic médical · aucune revendication de posture/pathologie · aucune pseudo-précision anthropométrique · aucune donnée Martin en dur dans un template global (sauf marquée dogfood/privée) · aucune rupture de la substitution · aucun changement du cycle de publication Custom Program · aucune ouverture d'EKB_04 · aucun changement runtime ASSET · aucune exposition `/library` · aucune réécriture de `session_builder`.

---

## §1. Décision 1 — Modèle Fait / Inférence / Recommandation (3 couches strictes)

Reprend et **aligne** le modèle d'états de signal de `SPIGNOS_BODY_SIGNAL_MODEL_SPEC` §1 et la classification de `body_intelligence.py`. Trois couches **non fusionnables**, avec une **frontière d'écriture stricte** (une couche ne peut jamais fabriquer une valeur de la couche amont) :

| Couche | Contenu | Origine autorisée | Interdits |
|---|---|---|---|
| **FACT** | mesure corporelle brute (taille, tour de taille/poitrine/cuisse/mollet, envergure) | opérateur / profil manuel (`BodyMeasurement`, `confirmed_measurement`) | jamais inventée, jamais estimée depuis une photo, jamais un %BF |
| **INFERENCE** | descripteur de morphologie **dérivé** (ratios, tags qualitatifs bornés) + **confiance** | fonction **déterministe pure** des FACTS confirmés | jamais un diagnostic, jamais une longueur de fémur/insertion, jamais une posture |
| **RECOMMENDATION** | priorité d'entraînement + intention de slot + rationale | règle **déterministe** sur les INFERENCES | jamais une injonction médicale, jamais « tu dois », jamais un %activation/EMG |

Invariant de flux (repris de Body Signal Model §1.8) : `FACT → INFERENCE → RECOMMENDATION`, unidirectionnel. Une RECOMMENDATION ne réécrit jamais un FACT. Chaque couche porte sa **version d'engine** (`morpho_descriptor_engine_version`, `morpho_priority_engine_version`) pour tracer sans recomputation du passé (doctrine Sx_30).

---

## §2. Décision 2 — Confidence scoring des interprétations de morphologie

Reprend la **Signal Confidence Policy** (Body Signal Model §3 transverse) + la classification `body_intelligence.py`. Chaque **descripteur** (INFERENCE) porte un `confidence ∈ {measured, derived, inferred, not_deductible}` :
- `measured` : dérivé **uniquement** de FACTS `confirmed_measurement` (ex. ratio épaule/taille à partir de deux tours mesurés).
- `derived` : combinaison de plusieurs mesures avec une hypothèse bornée déclarée (ex. « largeur scapulaire favorable » à partir du ratio épaule/taille au-dessus d'un seuil).
- `inferred` : tendance qualitative faiblement étayée (affichée **avec réserve**, jamais un moteur de décision dur).
- `not_deductible` : ce que le modèle **refuse** d'affirmer (longueur de fémur, insertions, posture, %BF) → **jamais produit**.

Règles dures : un descripteur `inferred` **ne peut pas** à lui seul créer une priorité P1 ; il peut seulement **moduler** une priorité déjà justifiée par un descripteur `measured`/`derived`. Un ratio n'est calculé que si **toutes** ses mesures d'entrée sont `confirmed_measurement` (sinon `not_deductible`). Pas de tendance sous 3 points de données (repris Body Signal Model).

---

## §3. Décision 3 — Garde-fous non-médicaux (garde-fou STRICT adopté)

**Adopte le garde-fou le plus strict du repo** (`Sx_BI_01_ACTIVATION §13`), **plus strict** que le « posture indicative » toléré par Body Signal Model — que cette spec **abandonne explicitement** :
- **Interdits absolus** : composition corporelle · body-fat · **posture / pathologie posturale** · dyskinésie · diagnostic médical · longueur de fémur / d'insertions · **pseudo-précision anthropométrique** (aucune valeur inventée au mm/°).
- **Réconciliation** : la priorité `priority_upper_back_posture` du Body Signal Model est **renommée** `priority_rear_delts_upper_back` (volume d'entraînement du haut du dos / deltoïdes postérieurs — **aucune mention de posture**).
- Microcopie : jamais « tu dois », « optimal », « corrige ta posture » ; toujours « piste », « à considérer », borné et non culpabilisant (doctrine SCORING_02).
- Le morphotype (« longiligne-athlétique ») est un **tag d'orientation non contraignant**, **jamais une vérité primaire** ni un facteur de décision dur (Body Signal Model §4.3).

---

## §4. Décision 4 — Politique de confidentialité (mesures & photos)

- **Photos** : **aucun stockage, aucun commit, aucun asset image brut** dans le repo. La capture MediaPipe/Bodygram (`Sb Body 02/03`) reste **non construite et flag-gated** ; cette spec **ne l'ouvre pas**. Les faits de morphologie proviennent de **mesures numériques** (cm), pas d'images.
- **Mesures personnelles** : données personnelles. Réutilisent le stockage **déjà construit** `BodyMeasurement` + le consentement `body_consents` (flag-gated OFF), **par utilisateur, privé**. Aucune nouvelle table dans cette spec.
- **Données Martin** : l'entrée de morphologie de Martin (§13) est un **input privé dogfood**, **jamais** codée en dur dans un template global. Autorisée **uniquement** dans une **fixture dogfood explicitement marquée privée** (ex. `tests/fixtures/dogfood/…` ou un input opérateur hors Git), consommée par le build dogfood (`Sb_MORPHO_DOGFOOD_01`), **jamais** rendue à un autre utilisateur, jamais exposée via `/library`.
- `provider_raw_output` (si un jour capté) reste « minimisé, traçable, purgeable » (Body Signal Model §1.2) — hors périmètre ici.

---

## §5. Décision 5 — Schéma de descripteur de morphologie (INFERENCE)

Structure logique (à implémenter comme dataclass frozen pure en build, **pas ici**) :

```
MorphologyDescriptor:
  descriptor_key: str        # ex. "shoulder_to_waist_ratio", "limb_leverage_tag"
  kind: "ratio" | "tag"
  value: float | str         # ratio numérique OU tag borné (vocabulaire fermé)
  confidence: measured | derived | inferred | not_deductible
  inputs: [fact_key...]      # FACTS confirmés utilisés (traçabilité)
  is_proxy: bool             # true si substitut faute d'une mesure idéale
  rationale: str             # une ligne, non médicale
  descriptor_engine_version: int
```

**Vocabulaire de descripteurs V1** (réutilise les `derived_ratio` de Body Signal Model §3, sans en inventer de nouveaux non mesurables) :
- Ratios : `shoulder_to_waist_ratio`, `waist_to_height_ratio`, `chest_to_waist_ratio`, `upper_lower_balance_proxy`, symétries `arm_symmetry_ratio`/`thigh_symmetry_ratio` (si mesures G/D présentes).
- Tags bornés (qualitatifs, `derived`/`inferred`, jamais médicaux) : `frame_orientation ∈ {longiligne, équilibré, trapu}` · `leverage_tag ∈ {bras_longs_relatif, neutre, bras_courts_relatif}` (dérivé de l'**ape index déclaré**, borné, **jamais** une longueur de fémur/humérus au cm) · `clavicular_width_tag ∈ {favorable, neutre}` · `waist_tag ∈ {étroit, neutre}`.

L'**ape index** est traité comme un **tag de levier borné**, pas une mesure de segment osseux — cohérent avec « ape index ≈ +4 cm, not extreme » sans revendiquer de longueur de fémur (interdit explicite).

---

## §6. Décision 6 — Schéma de priorité d'entraînement (RECOMMENDATION)

Reprend le modèle de priorités de Body Signal Model §4.1, **réconcilié** (posture retirée) et **étendu** au vocabulaire de la mission (upper chest, calves).

```
TrainingPriority:
  priority_key: str          # vocabulaire fermé ci-dessous
  rank: int                  # 1..N (max 4 actives, cf. discipline)
  target_muscle_families: [str]   # zones/sous-zones EKB (zone_primary/muscle_group)
  indicative_movement_patterns: [PatternMotor]  # enum verrouillé Sx_22a
  trigger: str               # descripteur(s) source + seuil, traçable
  confidence: measured|derived|inferred
  rationale: str             # une ligne, non médicale, non culpabilisante
  priority_engine_version: int
```

**Vocabulaire fermé de priorités V1** : `priority_lateral_delts`, `priority_upper_chest`, `priority_rear_delts_upper_back` (ex-`upper_back_posture`, **sans posture**), `priority_calves`, `priority_back`, `priority_arms`, `priority_waist_control_neat` (volume/NEAT, **jamais** body-fat). Chaque clé → familles musculaires (zones EKB) + patterns moteurs indicatifs (enum Sx_22a).

**Discipline** : au plus **4 priorités actives**, rangées (`rank`) ; chaque priorité **doit** citer un trigger traçable (descripteur measured/derived) ; une priorité `inferred`-seule est **interdite** (§2). Le contre-garde-fou de la mission (« avoid over-specializing quadriceps ») est modélisé comme une **priorité négative / plafond** : `deprioritize_quads` (plafonne le volume quad additionnel), traçable au descripteur « quads déjà forts ».

---

## §7. Décision 7 — Schéma d'intention de slot (Exercise Slot Intent)

Un **slot** décrit **ce qu'un emplacement d'exercice doit accomplir**, exprimé **entièrement sur des champs EKB/`exercise_properties` existants** (donc **aucun changement de schéma** — cf. §8, condition d'arrêt #2 levée) :

```
SlotIntent:
  slot_index: int                 # position dans la séance (miroir de TemplateExercise.code E1..En)
  target_zone_primary: str        # champ EKB existant
  target_muscle_group: str | None # champ exercise_properties existant (nullable honnête)
  required_pattern_motor: PatternMotor | None   # enum Sx_22a verrouillé
  chain_preference: "compound" | "isolation" | None
  priority_key: str | None        # relie le slot à une TrainingPriority (traçabilité)
  intent_reason: str              # rationale courte (déjà pratiqué par Custom_01 §11 : "focus épaules : +1 isolation")
  hard: bool                      # true = contrainte dure (le split l'exige), false = biais souple
```

Le slot **réutilise** le concept déjà présent dans `Sx_CUSTOM_PROGRAM_01 §11` (« chaque slot porte une raison courte ») et la colonne persistée `TemplateExercise.code` (E1..E7). Un slot n'est **pas** un exercice : c'est une **cible** qu'un exercice concret satisfait ou non (résolution §8).

---

## §8. Décision 8 — Règles de compatibilité de substitution (RÉUTILISE Sx_22a, 0 changement)

**Condition d'arrêt #2 levée** : le modèle de substitution existant (`app/services/substitution.py`, `data/exercise_properties.json`) **supporte déjà** l'intention de slot **sans changement de schéma**. Un exercice **satisfait** un `SlotIntent` ssi la fonction **existante** `compute_proximity(slot_props, candidate_props)` et le classifieur `_classify_suggestion` le placent au niveau requis :

- **Résolution d'un slot** = choisir le meilleur candidat dont `pattern_motor == required_pattern_motor` (si `hard`) et `zone_primary == target_zone_primary`, maximisant `compute_proximity` (mêmes poids : +50 zone, +20 pattern, +15 équipement, +10 chaîne, +10 muscle_group).
- **Compatibilité de substitution d'un exercice déjà posé** = **exactement** le comportement N1/N2/N3 existant (`compute_suggestions`) — **inchangé**. La morphologie ne modifie **jamais** l'ordre N1/N2/N3 ni le garde-fou « pattern différent ⇒ jamais N1/N2 » (Sx_22a §C.3). Elle agit **avant** (choix du slot), pas **pendant** la substitution runtime.
- **Invariant** : aucune règle de morphologie ne peut promouvoir une substitution cross-pattern en N1/N2. La morphologie **biaise le choix initial**, la substitution runtime reste **souveraine et inchangée**.

Un `SlotIntent` est donc un **`exercise_properties` partiel + une priorité** ; il vit dans le même espace de propriétés que la substitution → réutilisation totale, zéro nouvelle table.

---

## §9. Décision 9 — Modèle de disponibilité d'équipement (Fitness Park)

Martin s'entraîne à **Fitness Park**. Un slot ne doit proposer que des exercices **réalisables sur l'équipement disponible**.

- **Modèle** : un manifeste de disponibilité `equipment_availability` (data JSON, ajouté par un **build futur**, pas ici) listant les `equipment_family` / `machine_family` **présents** (vocabulaire EKB existant : `equipment_family`, `machine_family`, `machine_slug`).
- **Résolution** : lors du choix d'un candidat de slot, filtrer `candidate.equipment_family ∈ availability` ; sinon retomber sur le meilleur candidat disponible via `compute_proximity` (dégradation honnête, jamais un exercice infaisable).
- **Portée** : profil d'équipement **par utilisateur/salle** (Martin = Fitness Park), **privé**, jamais en dur global. **N'altère jamais** la substitution runtime (qui garde tous ses N1/N2/N3) — l'availability filtre seulement la **génération** initiale.
- **V1** : un seul profil `fitness_park` (dogfood). Généralisation multi-salles = itération future.

---

## §10. Décision 10 — Intégration au générateur déterministe (ADDITIVE)

**Condition d'arrêt #4 levée** : `user_program_generator.py` est un module **pur** (`generate_program_tree(split, sessions)` sur `reference_split.json`) extensible **sans réécriture**.

- **Nouvelle couche pure** (build futur `Sb_MORPHO_PROGRAM_GENERATOR_01`) : `generate_morpho_program_tree(profile, priorities, availability, split, sessions) -> payload`, qui (a) part de la base déterministe existante, (b) **applique les `SlotIntent`** issus des priorités pour **biaiser/insérer** des slots (ex. +1 isolation deltoïde latéral), (c) **résout** chaque slot via §8 filtré par §9, (d) émet un payload **identique en forme** à `generate_program_tree` (consommable par `replace_draft_tree`).
- **Déterminisme préservé** : même `(profile, priorities, availability, split, sessions, EKB_version)` → même payload. **Aucun LLM, aucun random, aucune DB** dans le cœur (doctrine Custom_01 §11).
- **Additivité** : `generate_program_tree` existant **inchangé** ; le nouveau générateur le **compose** (il ne le remplace pas). `replace_draft_tree` reste l'autorité des quotas 7/10 et des positions. Aucune écriture de `WorkoutTemplate`, aucun `session_builder`, aucune migration.

---

## §11. Décision 11 — Frontière d'interprétation agentique (agent propose, déterministe décide)

Frontière **dure** :
- **Un agent (LLM) PEUT** : lire un rapport de morphologie en langage naturel et **proposer** des FACTS structurés candidats + une lecture qualitative — **toujours en sortie structurée, jamais appliquée directement**.
- **Les services déterministes DÉCIDENT** : la conversion FACT→INFERENCE (ratios/tags), INFERENCE→RECOMMENDATION (priorités), la résolution de slots et la génération sont **100 % déterministes et testables**. L'agent **ne calcule pas** un ratio, **ne choisit pas** un exercice, **ne mute pas** un programme.
- **Aucune mutation silencieuse** : toute proposition agentique passe par (a) validation de schéma, (b) confirmation opérateur (dogfood) ou une garde de service, (c) écriture **traçable** (`source_reason`, engine version). Un programme n'est **jamais** modifié sans une action déterministe explicite. Cohérent avec le harnais eval C2 (l'agent juge/propose ; l'agrégation déterministe décide) et Custom_01 §13 (« s'ajoutent comme sous-scores/annotations traçables, jamais une black box »).

---

## §12. Décision 12 — Protocole dogfood pour les mises à jour du programme de Martin

- Les faits de morphologie de Martin (§13) sont chargés comme **fixture dogfood privée** (jamais template global).
- Le build `Sb_MORPHO_DOGFOOD_01` **propose** (agent) → **valide** (déterministe) → produit un **programme custom déterministe** via le pipeline (§10), lançable par le **cycle Custom Program existant** (WIZARD → validate → publish → launch), **sans** toucher le lifecycle de publication (PUBLICATION_01→04 inchangé).
- Mise à jour = **nouvelle version de programme** via le cycle d'édition existant (PUBLICATION_02, `draft v+1`), **jamais** une mutation en place. Chaque changement dérivé d'une priorité porte un `intent_reason` traçable.
- Dogfood report : Martin vit le programme, confirme/infirme les priorités ; les descripteurs `inferred` non confirmés restent des pistes, jamais des décisions dures.

---

## §13. Entrée dogfood Martin (input privé — préservé, non hardcodé global)

Rapport opérateur daté **2026-08-09** (données personnelles — **fixture dogfood privée uniquement**, jamais template global, jamais `/library`) :

- taille **179 cm** · envergure **≈183 cm** · **ape index ≈ +4 cm** (non extrême → `leverage_tag: bras_longs_relatif`, borné) · tour de taille **≈83 cm** · poitrine **≈100 cm** · cuisses **≈55–56 cm** · mollets **≈34–35 cm**.
- structure **longiligne-athlétique** (`frame_orientation: longiligne`, tag non contraignant) · largeur scapulaire/claviculaire **favorable** (`clavicular_width_tag: favorable`) · taille/bassin **relativement étroits** (`waist_tag: étroit`) · **quadriceps déjà forts** (→ `deprioritize_quads`) · lats **acceptables, non faibles**.
- **Priorités (rank)** : **1** `priority_lateral_delts` · **2** `priority_upper_chest` · **3** `priority_rear_delts_upper_back` · **4** `priority_calves`. Contre-garde : **ne pas sur-spécialiser les quadriceps**.
- **Interdits de revendication tenus** : aucune longueur de fémur précise, aucune posture pathologique, aucune insertion, aucune dyskinésie, aucun diagnostic médical, aucune pseudo-précision (les valeurs restent « ≈ », traitées en tags/ratios bornés).

---

## §14. File de build (queue) — chacun sur GO explicite, spec-only ici

| Ordre | Build | Portée | Tier attendu | Gate clé |
|---|---|---|---|---|
| 1 | **`Sb_MORPHO_PROFILE_01`** | Descripteurs de morphologie : FACT→INFERENCE pur (ratios + tags bornés + confidence) sur `BodyMeasurement` existant | isolated/shared_code (**pas de migration** — colonnes déjà présentes) | 0 médical/posture ; ratios `measured`-only ; tests confidence |
| 2 | **`Sb_PROGRAM_SLOT_INTENT_01`** | Schéma `SlotIntent` + résolution via `compute_proximity` existant + priorités→slots | shared_code (réutilise substitution, **0 changement Sx_22a**) | substitution N1/N2/N3 **inchangée** (tests de non-régression) |
| 3 | **`Sb_MORPHO_PROGRAM_GENERATOR_01`** | Générateur déterministe morpho additif (§10) + modèle d'availability (§9) | shared_code | déterminisme prouvé ; générateur existant inchangé ; `replace_draft_tree` autorité |
| 4 | **`Sb_MARTIN_PROGRAM_01`** | Fixture dogfood privée de Martin + programme dérivé (privé) | isolated (fixture + tests) | données privées, **jamais** template global/`/library` |
| 5 | **`Sb_MORPHO_DOGFOOD_01`** | Dogfood réel : Martin lance le programme via le cycle Custom existant, boucle de confirmation | docs/dogfood | lifecycle publication inchangé ; pas de mutation silencieuse |

Ordre imposé par les dépendances : descripteurs → slots → générateur → fixture → dogfood. Chaque item **respecte** tous les hard constraints de §0.

---

## §15. Préflight — conditions d'arrêt (toutes levées)

| Condition d'arrêt | Verdict |
|---|---|
| Spec morphologie/body-intelligence **conflictuelle** existante | **NON** — aucune spec shippée ne mappe morphologie→priorités→slots ; les prédécesseurs (`Body Signal Model`, roadmap `Sb Body 04/05`) sont **spec-only non construits** et **référencés additivement** ; la seule divergence (posture) est **réconciliée** vers le garde-fou strict |
| Substitution ne peut pas supporter le slot intent sans changement de schéma | **NON** — le slot intent s'exprime sur les champs `exercise_properties`/EKB **existants** ; `compute_proximity` fournit la résolution (§8) |
| Décision de stockage de données personnelles **ambiguë** | **NON** — réutilise `BodyMeasurement` + `body_consents` (construits, flag-off) ; **aucune photo** ; Martin = fixture dogfood privée (§4) |
| Générateur non extensible sans réécriture large | **NON** — module pur ; couche morpho **additive** qui le compose (§10) |
| Un changement requis toucherait du code applicatif pendant ce sprint spec-only | **NON** — **0 code applicatif** ; tout est design + file de build |

---

## §16. Non-goals / interdits (récapitulatif contraignant)

Aucun code applicatif · aucune migration · aucune implémentation de modèle/schéma · aucun stockage de photo · aucun asset image brut committé · aucun diagnostic médical · aucune revendication de posture/pathologie/insertion/fémur/dyskinésie · aucune pseudo-précision anthropométrique · aucune donnée Martin en dur dans un template global · aucune rupture de la substitution (Sx_22a inchangé) · aucun changement du cycle de publication Custom Program (PUBLICATION_01→04) · aucune ouverture d'EKB_04 · aucun changement runtime ASSET · aucune exposition `/library` · aucune réécriture de `session_builder`.
