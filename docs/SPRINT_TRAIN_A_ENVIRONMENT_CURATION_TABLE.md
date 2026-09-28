# `TRAIN A` — Annexe : vocabulaires et table de curation

**Généré depuis les données**, jamais recopié à la main. Source :
`data/equipment_registry.json`, `data/equipment_curation.json`,
`data/exercise_knowledge_base.json`, `data/reference_split.json`.

Le commentaire de chaque décision vit dans
`docs/SPRINT_TRAIN_A_ENVIRONMENT_MODEL_REPORT.md`.

### Vocabulaire des capacités internes — 29

| capacité | ce qu'elle affirme |
|---|---|
| `ab_wheel` | une roulette abdominale |
| `barbell_ez` | une barre EZ (coudée) et ses disques |
| `barbell_straight` | une barre droite et ses disques |
| `cable_anchor_adjustable` | un ancrage dont la hauteur se règle librement |
| `cable_anchor_high` | un point d'ancrage de câble en position haute |
| `cable_anchor_low` | un point d'ancrage de câble en position basse |
| `cable_bilateral_independent` | deux colonnes de câble chargées indépendamment, utilisables ensemble |
| `dip_station` | barres parallèles supportant le corps suspendu bras tendus |
| `dumbbells` | une paire d'haltères |
| `flat_bench_support` | banc horizontal supportant un torse allongé |
| `incline_bench_support` | banc dont le dossier s'incline |
| `machine_butterfly` | la fonction machine « Butterfly / pec deck » |
| `machine_chest_press` | la fonction machine « Chest press » |
| `machine_chest_supported_row` | la fonction machine « Rowing à appui pectoral » |
| `machine_hack_squat` | la fonction machine « Hack squat » |
| `machine_leg_extension` | la fonction machine « Leg extension » |
| `machine_leg_press` | la fonction machine « Presse à cuisses » |
| `machine_lying_leg_curl` | la fonction machine « Leg curl allongé » |
| `machine_pullover` | la fonction machine « Pullover machine » |
| `machine_rear_delt_fly` | la fonction machine « Rear delt fly / pec deck inversé » |
| `machine_seated_calf_raise` | la fonction machine « Mollets assis » |
| `machine_seated_leg_curl` | la fonction machine « Leg curl assis » |
| `machine_shoulder_press` | la fonction machine « Shoulder press » |
| `machine_standing_calf_raise` | la fonction machine « Mollets debout » |
| `overhead_hang_bar` | une barre haute permettant une suspension complète |
| `pulldown_seated_station` | station de tirage vertical assis avec cale-cuisses dédiée |
| `row_seated_station` | station de tirage horizontal assis avec cale-pieds dédiée |
| `seated_support` | une assise permettant d'exécuter le mouvement assis |
| `smith_rack` | un rack à barre guidée (Smith) |

### Vocabulaire des objets déclarables — 26

| objet | libellé | capacités dérivées | provenance |
|---|---|---|---|
| `ab_wheel` | Roulette abdominale | `ab_wheel` | identité canonique AUREN (« roulette abdominale ») |
| `adjustable_bench` | Banc inclinable | `flat_bench_support` · `incline_bench_support` · `seated_support` | ACE #25 Incline Chest Press — Equipment « Bench, Dumbbells » |
| `barbell_and_plates` | Barre droite et disques | `barbell_straight` | atlas/EKB: famille `barbell` |
| `butterfly_machine` | Butterfly / pec deck | `machine_butterfly` | machine_atlas: slug `butterfly-machine`, modalité `machine` |
| `chest_press_machine` | Chest press | `machine_chest_press` | machine_atlas: slug `chest-press-machine`, modalité `machine` |
| `chest_supported_row` | Rowing à appui pectoral | `machine_chest_supported_row` | machine_atlas: slug `chest-supported-row`, modalité `machine` |
| `dip_station` | Barres à dips | `dip_station` | identité canonique AUREN (« Dips ») |
| `dual_adjustable_pulley` | Poulie double réglable | `cable_anchor_adjustable` · `cable_anchor_high` · `cable_anchor_low` · `cable_bilateral_independent` | Life Fitness Signature Series Dual Adjustable Pulley — 22 réglages de hauteur, deux colonnes de 390 lb indépendantes, accessoires corde/barre/poignées fournis |
| `dumbbells` | Haltères | `dumbbells` | atlas: modalité `haltere` |
| `ez_bar` | Barre EZ | `barbell_ez` | identité canonique AUREN (« EZ-bar ») |
| `flat_bench` | Banc plat | `flat_bench_support` · `seated_support` | ACE — champ Equipment « Bench » sur les pressés couchés |
| `hack_squat_machine` | Hack squat | `machine_hack_squat` | machine_atlas: slug `hack-squat-machine`, modalité `machine` |
| `lat_pulldown_station` | Station de tirage vertical | `pulldown_seated_station` | Life Fitness Signature Series MJ4 Multi-Jungle — le « Dual Pulley Lat Pulldown » et le « Single Pulley Low Row » y sont deux stations sélectorisées distinctes, chacune avec sa propre colonne de 260 lb |
| `leg_extension` | Leg extension | `machine_leg_extension` | machine_atlas: slug `leg-extension`, modalité `machine` |
| `leg_press` | Presse à cuisses | `machine_leg_press` | machine_atlas: slug `leg-press`, modalité `machine` |
| `low_row_station` | Station de tirage horizontal assis | `row_seated_station` | Life Fitness Signature Series MJ4 Multi-Jungle — le « Dual Pulley Lat Pulldown » et le « Single Pulley Low Row » y sont deux stations sélectorisées distinctes, chacune avec sa propre colonne de 260 lb |
| `lying_leg_curl` | Leg curl allongé | `machine_lying_leg_curl` | machine_atlas: slug `lying-leg-curl`, modalité `machine` |
| `pull_up_bar` | Barre de traction | `overhead_hang_bar` | identité canonique AUREN (« suspendu ») |
| `pullover_machine` | Pullover machine | `machine_pullover` | machine_atlas: slug `pullover-machine`, modalité `machine` |
| `rear_delt_fly_machine` | Rear delt fly / pec deck inversé | `machine_rear_delt_fly` | machine_atlas: slug `rear-delt-fly-machine`, modalité `machine` |
| `seated_calf_raise` | Mollets assis | `machine_seated_calf_raise` | machine_atlas: slug `seated-calf-raise`, modalité `machine` |
| `seated_leg_curl` | Leg curl assis | `machine_seated_leg_curl` | machine_atlas: slug `seated-leg-curl`, modalité `machine` |
| `shoulder_press_machine` | Shoulder press | `machine_shoulder_press` | machine_atlas: slug `shoulder-press-machine`, modalité `machine` |
| `single_adjustable_pulley` | Poulie réglable simple | `cable_anchor_adjustable` · `cable_anchor_high` · `cable_anchor_low` | Life Fitness Signature Series Dual Adjustable Pulley — 22 réglages de hauteur, deux colonnes de 390 lb indépendantes, accessoires corde/barre/poignées fournis — variante à une seule colonne |
| `smith_machine` | Smith (barre guidée) | `smith_rack` | atlas: modalité `smith`, un seul appareil physique (§10) |
| `standing_calf_raise` | Mollets debout | `machine_standing_calf_raise` | machine_atlas: slug `standing-calf-raise`, modalité `machine` |

### Table de curation — les 68 prescrits

| # | exercice | gabarits | classe | exigences | preuve |
|---|---|---|---|---|---|
| 1 | Adduction assise | 1 | machine | **INCONNU** | — |
| 2 | Butterfly pec machine | 1 | machine | `machine_butterfly` | ATLAS |
| 3 | Cable cross-over (bas→haut) | 1 | cable | `cable_anchor_adjustable` · `cable_bilateral_independent` | ATLAS |
| 4 | Chest Press machine | 3 | machine | `machine_chest_press` | ATLAS |
| 5 | Crunch câble à genoux | 3 | — | **INCONNU** | — |
| 6 | Curl EZ-bar debout | 2 | barbell | `barbell_ez` | IDENTITE_AUREN |
| 7 | Curl incliné haltères | 1 | dumbbell | `dumbbells` · `incline_bench_support` | IDENTITE_AUREN |
| 8 | Curl incliné haltères (banc 45°) | 2 | dumbbell | `dumbbells` · `incline_bench_support` | IDENTITE_AUREN |
| 9 | Curl marteau câble (corde) | 1 | cable | **INCONNU** | — |
| 10 | Curl marteau haltères | 1 | dumbbell | `dumbbells` | EXTERNE |
| 11 | Curl poulie basse | 1 | cable | `cable_anchor_low` | IDENTITE_AUREN |
| 12 | Curl poulie basse (barre) | 1 | cable | `cable_anchor_low` | IDENTITE_AUREN |
| 13 | Dips pectoraux (buste penché) | 1 | bodyweight | `dip_station` | IDENTITE_AUREN |
| 14 | Développé couché haltères | 1 | dumbbell | `dumbbells` · `flat_bench_support` | EXTERNE |
| 15 | Développé incliné haltères 30° | 2 | dumbbell | `dumbbells` · `incline_bench_support` | EXTERNE |
| 16 | Extension overhead câble (corde) | 2 | cable | **INCONNU** | — |
| 17 | Face pull câble | 3 | cable | `cable_anchor_high` | ATLAS |
| 18 | Face pull câble (corde) | 1 | cable | `cable_anchor_high` | ATLAS |
| 19 | Hack Squat machine | 2 | machine | `machine_hack_squat` | ATLAS |
| 20 | Hip thrust Smith | 1 | smith | `smith_rack` | ATLAS |
| 21 | Hip thrust Smith machine | 1 | smith | `smith_rack` | ATLAS |
| 22 | Incline Smith Press | 1 | smith | `incline_bench_support` · `smith_rack` | ATLAS |
| 23 | Kickback câble | 1 | cable | **INCONNU** | — |
| 24 | Leg Press (pieds bas) | 1 | machine | `machine_leg_press` | ATLAS |
| 25 | Leg Press (pieds bas, serrés) | 1 | machine | `machine_leg_press` | ATLAS |
| 26 | Leg Press (pieds hauts, écartés) | 1 | — | **INCONNU** | — |
| 27 | Leg curls allongé | 2 | machine | `machine_lying_leg_curl` | ATLAS |
| 28 | Leg curls assis | 2 | machine | `machine_seated_leg_curl` | ATLAS |
| 29 | Leg extensions assises | 4 | machine | `machine_leg_extension` | ATLAS |
| 30 | Machine shoulder press | 3 | machine | `machine_shoulder_press` | ATLAS |
| 31 | Mollets assis machine | 3 | machine | `machine_seated_calf_raise` | ATLAS |
| 32 | Neutral Grip Shoulder Press machine | 1 | machine | `machine_shoulder_press` | ATLAS |
| 33 | Pallof press câble | 1 | — | **INCONNU** | — |
| 34 | Pullover câble (bras tendus) | 1 | machine | `machine_pullover` | ATLAS |
| 35 | Pullover câble (bras tendus, poulie haute) | 1 | machine | `machine_pullover` | ATLAS |
| 36 | Pullover machine | 1 | machine | `machine_pullover` | ATLAS |
| 37 | Rear delt fly machine | 2 | machine | `machine_rear_delt_fly` | ATLAS |
| 38 | Rear delt fly machine (pec deck inversé) | 1 | machine | `machine_rear_delt_fly` | ATLAS |
| 39 | Relevé de jambes suspendu | 1 | — | `overhead_hang_bar` | IDENTITE_AUREN |
| 40 | Relevés mollets debout | 1 | bodyweight | **INCONNU** | — |
| 41 | Relevés mollets debout machine | 2 | machine | `machine_standing_calf_raise` | ATLAS |
| 42 | Reverse fly machine | 1 | machine | **INCONNU** | — |
| 43 | Romanian Deadlift barre | 1 | barbell | `barbell_straight` | IDENTITE_AUREN |
| 44 | Romanian Deadlift haltères | 2 | dumbbell | `dumbbells` | EXTERNE |
| 45 | Roulette abdominale | 2 | — | `ab_wheel` | IDENTITE_AUREN |
| 46 | Roulette abdominale (ab wheel rollout) | 1 | — | `ab_wheel` | IDENTITE_AUREN |
| 47 | Rowing chest-supported | 1 | machine | **INCONNU** | — |
| 48 | Rowing câble assis prise large | 1 | cable | `row_seated_station` | ATLAS |
| 49 | Rowing câble assis prise neutre | 1 | cable | `row_seated_station` | ATLAS |
| 50 | Rowing câble assis prise serrée | 1 | cable | `row_seated_station` | ATLAS |
| 51 | Rowing haltère un bras (banc) | 1 | dumbbell | `dumbbells` · `flat_bench_support` | EXTERNE |
| 52 | Rowing machine chest-supported | 2 | machine | `machine_chest_supported_row` | ATLAS |
| 53 | Shrugs haltères | 1 | — | `dumbbells` | IDENTITE_AUREN |
| 54 | Skull crushers EZ-bar | 1 | — | `barbell_ez` · `flat_bench_support` | EXTERNE |
| 55 | Squat Smith machine (pieds avancés) | 1 | smith | `smith_rack` | ATLAS |
| 56 | Straight-arm pulldown câble | 2 | cable | **INCONNU** | — |
| 57 | Tirage front câble (prise large) | 2 | — | **INCONNU** | — |
| 58 | Tirage poulie haute prise large | 2 | cable | `pulldown_seated_station` | ATLAS |
| 59 | Tirage poulie haute prise neutre | 3 | cable | `pulldown_seated_station` | ATLAS |
| 60 | Tirage vertical unilatéral câble | 2 | cable | `pulldown_seated_station` | ATLAS |
| 61 | Triceps extension poulie haute (corde) | 1 | cable | `cable_anchor_high` | IDENTITE_AUREN |
| 62 | Triceps pushdown barre | 3 | cable | **INCONNU** | — |
| 63 | Triceps pushdown corde | 2 | cable | **INCONNU** | — |
| 64 | Écarté arrière d'épaule câble | 1 | cable | **INCONNU** | — |
| 65 | Écarté pec aux câbles (incliné bas→haut) | 1 | cable | `cable_anchor_adjustable` · `cable_bilateral_independent` | ATLAS |
| 66 | Élévations latérales câble | 3 | cable | `cable_anchor_low` | ATLAS |
| 67 | Élévations latérales câble (derrière le dos) | 2 | cable | `cable_anchor_low` | ATLAS |
| 68 | Élévations latérales haltères assis | 2 | — | `dumbbells` · `seated_support` | IDENTITE_AUREN |

### Détail des lignes INCONNUES

* **Adduction assise** — famille `machine` sans slug d'atlas : l'identité de l'appareil n'est pas résolue et aucune source externe exacte n'a été trouvée
* **Crunch câble à genoux** — hauteur d'ancrage non écrite et non sourcée
* **Curl marteau câble (corde)** — hauteur d'ancrage non écrite et non sourcée
* **Extension overhead câble (corde)** — s'exécute d'une poulie basse OU haute selon les références ; aucune source autoritaire exacte pour trancher
* **Kickback câble** — hauteur d'ancrage non écrite et non sourcée
* **Leg Press (pieds hauts, écartés)** — DÉFAUT DE DÉPÔT : `equipment_family` ET `machine_slug` sont tous deux NULL alors que « Leg Press (pieds bas) » porte le slug `leg-press`. Très probablement le même appareil — mais l'affirmer serait inférer par le nom. Correction d'EKB à arbitrer
* **Pallof press câble** — ancrage à hauteur de torse — ni « haut » ni « bas » dans le vocabulaire actuel ; aucune source exacte
* **Relevés mollets debout** — CONFLIT DE CHAMPS : `equipment_family = bodyweight` mais `machine_slug = standing-calf-raise`, dont l'atlas donne `equipment: machine`. Deux déclarations structurées se contredisent — c'est le SEUL désaccord famille/modalité des 39 exercices à slug, mesuré. Sa sœur « Relevés mollets debout machine » porte le même slug avec `family = machine` et reste, elle, résolue. Arbitrage requis
* **Reverse fly machine** — DÉFAUT DE DÉPÔT : famille `machine`, slug NULL, alors que « Rear delt fly machine » porte `rear-delt-fly-machine`. Correspondance à arbitrer
* **Rowing chest-supported** — DÉFAUT DE DÉPÔT : famille `machine`, slug NULL, alors que « Rowing machine chest-supported » porte `chest-supported-row`. À arbitrer
* **Straight-arm pulldown câble** — hauteur haute très probable mais non écrite et non sourcée
* **Tirage front câble (prise large)** — CONFLIT D'IDENTITÉ : très proche de « Tirage poulie haute prise large » (slug `lat-pulldown`) mais l'EKB ne porte ni slug ni alias. Les assimiler serait exactement ce que le §7 interdit
* **Triceps pushdown barre** — hauteur d'ancrage non écrite et non sourcée
* **Triceps pushdown corde** — hauteur d'ancrage non écrite et non sourcée
* **Écarté arrière d'épaule câble** — hauteur d'ancrage et nombre de colonnes non écrits et non sourcés

### Correspondances d'identité déclarées (§7)

* **Curl marteau haltères** — ACE « Hammer Curl » ↔ AUREN « Curl marteau haltères » — même mouvement, prise neutre, haltères
* **Développé couché haltères** — ACE « Chest Press (Dumbbells) » ↔ AUREN « Développé couché haltères » — même exécution (décubitus dorsal, banc plat, deux haltères)
* **Développé incliné haltères 30°** — ACE « Incline Chest Press » (45–60°) ↔ AUREN « Développé incliné haltères 30° » — l'ANGLE diffère, l'exigence de banc inclinable non. L'EKB porte déjà l'alias « Incline Dumbbell Press » vers ce nom
* **Rowing haltère un bras (banc)** — ACE « Single Arm Row » ↔ AUREN « Rowing haltère un bras (banc) » — exécution identique, le nom AUREN nomme déjà le banc
* **Skull crushers EZ-bar** — ACE « Lying Barbell Triceps Extensions » ↔ AUREN « Skull crushers EZ-bar » — même mouvement allongé ; l'IMPLÉMENT diffère (droite vs EZ), l'exigence de banc non

🤖 Generated with [Claude Code](https://claude.com/claude-code)
