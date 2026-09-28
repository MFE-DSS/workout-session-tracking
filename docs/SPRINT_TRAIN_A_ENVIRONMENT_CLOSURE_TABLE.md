# `TRAIN A` — Annexe : clôture, vocabulaires, couverture

**Généré depuis les données.** Sources : `data/equipment_registry.json`,
`data/equipment_curation.json`, `data/reference_split.json`,
`data/machine_atlas.json`. Le commentaire vit dans
`docs/SPRINT_TRAIN_A_ENVIRONMENT_CLOSURE_REPORT.md`.

Clôture **105** identités atteignables · **66** avec
exigence établie · **39** `UNKNOWN` ·
**68** prescrites.

## Capacités internes — 33

Jamais exposées à l'utilisateur.

| capacité | ce qu'elle affirme |
|---|---|
| `ab_wheel` | une roulette abdominale |
| `barbell` | une barre chargeable et ses disques |
| `barbell_ez` | une barre EZ (coudée) et ses disques |
| `cable_anchor_adjustable` | un ancrage dont la hauteur se règle librement |
| `cable_anchor_any` | un point d'ancrage de câble librement positionnable, hauteur indifférente. N'est PAS accordé par une station dédiée : on ne fait pas un écarté arrière sur un tirage vertical assis |
| `cable_anchor_high` | un ancrage de câble en position haute |
| `cable_anchor_low` | un ancrage de câble en position basse |
| `cable_attachment_rope` | une corde à fixer sur une poulie |
| `cable_attachment_straight_bar` | une barre droite à fixer sur une poulie |
| `cable_bilateral_independent` | deux colonnes de câble chargées indépendamment, utilisables ensemble |
| `dumbbells` | une paire d'haltères |
| `flat_bench_support` | un banc horizontal supportant un torse allongé |
| `incline_bench_support` | un banc dont le dossier s'incline |
| `machine_assisted_pull_up` | la fonction machine « Traction assistée » |
| `machine_butterfly` | la fonction machine « Butterfly / pec deck » |
| `machine_chest_press` | la fonction machine « Chest press » |
| `machine_chest_supported_row` | la fonction machine « Rowing à appui pectoral » |
| `machine_hack_squat` | la fonction machine « Hack squat » |
| `machine_lateral_raise` | la fonction machine « Élévations latérales » |
| `machine_leg_extension` | la fonction machine « Leg extension » |
| `machine_leg_press` | la fonction machine « Presse à cuisses » |
| `machine_lying_leg_curl` | la fonction machine « Leg curl allongé » |
| `machine_pullover` | la fonction machine « Pullover machine » |
| `machine_rear_delt_fly` | la fonction machine « Pec fly / rear deltoid » |
| `machine_seated_calf_raise` | la fonction machine « Mollets assis » |
| `machine_seated_leg_curl` | la fonction machine « Leg curl assis » |
| `machine_shoulder_press` | la fonction machine « Shoulder press » |
| `machine_standing_calf_raise` | la fonction machine « Mollets debout » |
| `overhead_hang_support` | un appui haut permettant une suspension complète du corps — barre de traction, cadre, anneaux : l'affordance, pas un objet précis |
| `pulldown_seated_station` | une station de tirage vertical assis avec cale-cuisses dédiée |
| `row_seated_station` | une station de tirage horizontal assis avec cale-pieds dédiée |
| `seated_support` | une assise permettant d'exécuter le mouvement assis |
| `smith_rack` | un rack à barre guidée (Smith) |

## Objets déclarables — 29

| objet | libellé | capacités dérivées | provenance |
|---|---|---|---|
| `ab_wheel` | Roulette abdominale | `ab_wheel` | identité canonique AUREN (« roulette abdominale ») |
| `adjustable_bench` | Banc inclinable | `flat_bench_support` · `incline_bench_support` · `seated_support` | ACE #25 Incline Chest Press — « Bench, Dumbbells » |
| `assisted_pull_up` | Traction assistée | `machine_assisted_pull_up` | machine_atlas : slug `assisted-pull-up` |
| `barbell_and_plates` | Barre et disques | `barbell` | EKB : famille `barbell` |
| `butterfly_machine` | Butterfly / pec deck | `machine_butterfly` | machine_atlas : slug `butterfly-machine` |
| `cable_rope` | Corde de poulie | `cable_attachment_rope` | accessoire, déclarable séparément (§4 : une station ne possède pas forcément tous les accessoires) |
| `cable_straight_bar` | Barre de poulie | `cable_attachment_straight_bar` | accessoire, déclarable séparément (§4) |
| `chest_press_machine` | Chest press | `machine_chest_press` | machine_atlas : slug `chest-press-machine` |
| `chest_supported_row` | Rowing à appui pectoral | `machine_chest_supported_row` | machine_atlas : slug `chest-supported-row` |
| `dual_adjustable_pulley` | Poulie double réglable | `cable_anchor_adjustable` · `cable_anchor_any` · `cable_anchor_high` · `cable_anchor_low` · `cable_attachment_rope` · `cable_attachment_straight_bar` · `cable_bilateral_independent` | Life Fitness Signature Series Dual Adjustable Pulley — 22 réglages de hauteur, deux colonnes de 390 lb indépendantes ; corde triceps, barre longue et poignées LIVRÉES avec l'appareil |
| `dumbbells` | Haltères | `dumbbells` | atlas : modalité `haltere` |
| `ez_bar` | Barre EZ | `barbell_ez` | identité canonique AUREN (« EZ-bar »), toujours qualifiée |
| `flat_bench` | Banc plat | `flat_bench_support` · `seated_support` | ACE — champ Equipment « Bench » sur les pressés couchés |
| `hack_squat_machine` | Hack squat | `machine_hack_squat` | machine_atlas : slug `hack-squat-machine` |
| `lat_pulldown_station` | Station de tirage vertical | `pulldown_seated_station` | Life Fitness Signature Series MJ4 Multi-Jungle — le « Dual Pulley Lat Pulldown » et le « Single Pulley Low Row » y sont deux stations sélectorisées distinctes, chacune avec sa propre colonne de 260 lb |
| `lateral_raise_machine` | Élévations latérales | `machine_lateral_raise` | machine_atlas : slug `lateral-raise-machine` |
| `leg_extension` | Leg extension | `machine_leg_extension` | machine_atlas : slug `leg-extension` |
| `leg_press` | Presse à cuisses | `machine_leg_press` | machine_atlas : slug `leg-press` |
| `low_row_station` | Station de tirage horizontal | `row_seated_station` | Life Fitness Signature Series MJ4 Multi-Jungle — le « Dual Pulley Lat Pulldown » et le « Single Pulley Low Row » y sont deux stations sélectorisées distinctes, chacune avec sa propre colonne de 260 lb |
| `lying_leg_curl` | Leg curl allongé | `machine_lying_leg_curl` | machine_atlas : slug `lying-leg-curl` |
| `pull_up_bar` | Barre de traction | `overhead_hang_support` | objet concret accordant l'affordance de suspension (§2) |
| `pullover_machine` | Pullover machine | `machine_pullover` | machine_atlas : slug `pullover-machine` |
| `rear_delt_fly_machine` | Pec fly / rear deltoid | `machine_rear_delt_fly` | machine_atlas : slug `rear-delt-fly-machine` |
| `seated_calf_raise` | Mollets assis | `machine_seated_calf_raise` | machine_atlas : slug `seated-calf-raise` |
| `seated_leg_curl` | Leg curl assis | `machine_seated_leg_curl` | machine_atlas : slug `seated-leg-curl` |
| `shoulder_press_machine` | Shoulder press | `machine_shoulder_press` | machine_atlas : slug `shoulder-press-machine` |
| `single_adjustable_pulley` | Poulie réglable simple | `cable_anchor_adjustable` · `cable_anchor_any` · `cable_anchor_high` · `cable_anchor_low` | Life Fitness Signature Series Dual Adjustable Pulley — 22 réglages de hauteur, deux colonnes de 390 lb indépendantes ; corde triceps, barre longue et poignées LIVRÉES avec l'appareil — variante à une colonne, accessoires déclarés séparément |
| `smith_machine` | Smith (barre guidée) | `smith_rack` | atlas : 4 slugs `smith`, aucun matériel propre déclaré |
| `standing_calf_raise` | Mollets debout | `machine_standing_calf_raise` | machine_atlas : slug `standing-calf-raise` |

## Couverture de la clôture — 105 identités

| # | identité | rôle | exigences | preuve |
|---|---|---|---|---|
| 1 | Adduction assise | prescrit | **INCONNU** | — |
| 2 | Adduction couchée machine | substitut | **INCONNU** | — |
| 3 | Adduction debout câble | substitut | **INCONNU** | — |
| 4 | Arnold press | substitut | **INCONNU** | — |
| 5 | Back extension 45° (bias ischios) | substitut | **INCONNU** | — |
| 6 | Butterfly pec machine | prescrit | `machine_butterfly` | ATLAS |
| 7 | Cable cross-over (bas→haut) | prescrit | `cable_anchor_adjustable` · `cable_bilateral_independent` | ATLAS |
| 8 | Calf press leg press | substitut | **INCONNU** | — |
| 9 | Chest Press machine | prescrit | `machine_chest_press` | ATLAS |
| 10 | Crunch câble à genoux | prescrit | **INCONNU** | — |
| 11 | Curl EZ-bar debout | prescrit | `barbell_ez` | IDENTITE_AUREN |
| 12 | Curl câble basse | substitut | **INCONNU** | — |
| 13 | Curl debout haltères | substitut | `dumbbells` | IDENTITE_AUREN |
| 14 | Curl incliné haltères | prescrit | `dumbbells` · `incline_bench_support` | IDENTITE_AUREN |
| 15 | Curl incliné haltères (banc 45°) | prescrit | `dumbbells` · `incline_bench_support` | IDENTITE_AUREN |
| 16 | Curl marteau câble (corde) | prescrit | **INCONNU** | — |
| 17 | Curl marteau câble corde | substitut | **INCONNU** | — |
| 18 | Curl marteau haltères | prescrit | `dumbbells` | IDENTITE_AUREN |
| 19 | Curl poulie basse | prescrit | `cable_anchor_low` | IDENTITE_AUREN |
| 20 | Curl poulie basse (barre) | prescrit | `cable_anchor_low` · `cable_attachment_straight_bar` | IDENTITE_AUREN |
| 21 | Curl prise neutre câble | substitut | **INCONNU** | — |
| 22 | Decline crunch | substitut | **INCONNU** | — |
| 23 | Dips pectoraux (buste penché) | prescrit | **INCONNU** | — |
| 24 | Développé couché haltères | prescrit | `dumbbells` · `flat_bench_support` | ATLAS |
| 25 | Développé incliné haltères 30° | prescrit | `dumbbells` · `incline_bench_support` | ATLAS |
| 26 | Extension overhead câble (corde) | prescrit | **INCONNU** | — |
| 27 | Face pull câble | prescrit | `cable_anchor_high` | ATLAS |
| 28 | Face pull câble (corde) | prescrit | `cable_anchor_high` · `cable_attachment_rope` | ATLAS |
| 29 | Good morning haltères | substitut | **INCONNU** | — |
| 30 | Hack Squat machine | prescrit | `machine_hack_squat` | ATLAS |
| 31 | Hanging knee raise | substitut | **INCONNU** | — |
| 32 | Hip thrust Smith | prescrit | `smith_rack` | ATLAS |
| 33 | Hip thrust Smith machine | prescrit | `smith_rack` | ATLAS |
| 34 | Hip thrust haltères | substitut | **INCONNU** | — |
| 35 | Incline DB Press 30° | substitut | `dumbbells` · `incline_bench_support` | ATLAS |
| 36 | Incline Dumbbell Press | substitut | `dumbbells` · `incline_bench_support` | ATLAS |
| 37 | Incline Smith Press | prescrit | `incline_bench_support` · `smith_rack` | ATLAS |
| 38 | Kickback câble | prescrit | **INCONNU** | — |
| 39 | Lat pulldown prise large | substitut | **INCONNU** | — |
| 40 | Lat pulldown prise neutre | substitut | **INCONNU** | — |
| 41 | Leg Press (pieds bas) | prescrit | `machine_leg_press` | ATLAS |
| 42 | Leg Press (pieds bas, serrés) | prescrit | `machine_leg_press` | ATLAS |
| 43 | Leg Press (pieds hauts, écartés) | prescrit | `machine_leg_press` | EXTERNE |
| 44 | Leg curls allongé | prescrit | `machine_lying_leg_curl` | ATLAS |
| 45 | Leg curls assis | prescrit | `machine_seated_leg_curl` | ATLAS |
| 46 | Leg extension câble unilatéral | substitut | **INCONNU** | — |
| 47 | Leg extensions assises | prescrit | `machine_leg_extension` | ATLAS |
| 48 | Machine crunch | substitut | **INCONNU** | — |
| 49 | Machine shoulder press | prescrit | `machine_shoulder_press` | ATLAS |
| 50 | Mollets assis machine | prescrit | `machine_seated_calf_raise` | ATLAS |
| 51 | Mollets debout machine | substitut | `machine_standing_calf_raise` | ATLAS |
| 52 | Neutral Grip Shoulder Press machine | prescrit | `machine_shoulder_press` | ATLAS |
| 53 | Pallof press câble | prescrit | **INCONNU** | — |
| 54 | Preacher curl | substitut | **INCONNU** | — |
| 55 | Pullover câble (bras tendus) | prescrit | `machine_pullover` | ATLAS |
| 56 | Pullover câble (bras tendus, poulie haute) | prescrit | `machine_pullover` | ATLAS |
| 57 | Pullover machine | prescrit | `machine_pullover` | ATLAS |
| 58 | Pushdown corde | substitut | **INCONNU** | — |
| 59 | Rear delt fly machine | prescrit | `machine_rear_delt_fly` | ATLAS |
| 60 | Rear delt fly machine (pec deck inversé) | prescrit | `machine_rear_delt_fly` | ATLAS |
| 61 | Relevé de jambes suspendu | prescrit | `overhead_hang_support` | IDENTITE_AUREN |
| 62 | Relevés mollets debout | prescrit | `[]` aucune | EXTERNE |
| 63 | Relevés mollets debout machine | prescrit | `machine_standing_calf_raise` | ATLAS |
| 64 | Reverse Nordic | substitut | **INCONNU** | — |
| 65 | Reverse fly machine | prescrit | `machine_rear_delt_fly` | ATLAS |
| 66 | Romanian Deadlift barre | prescrit | `barbell` | IDENTITE_AUREN |
| 67 | Romanian Deadlift haltères | prescrit | `dumbbells` | ATLAS |
| 68 | Roulette abdominale | prescrit | `ab_wheel` | IDENTITE_AUREN |
| 69 | Roulette abdominale (ab wheel rollout) | prescrit | `ab_wheel` | IDENTITE_AUREN |
| 70 | Rowing chest-supported | prescrit | `machine_chest_supported_row` | ATLAS |
| 71 | Rowing câble assis prise large | prescrit | `row_seated_station` | ATLAS |
| 72 | Rowing câble assis prise neutre | prescrit | `row_seated_station` | ATLAS |
| 73 | Rowing câble assis prise serrée | prescrit | `row_seated_station` | ATLAS |
| 74 | Rowing haltère un bras | substitut | `dumbbells` | ATLAS |
| 75 | Rowing haltère un bras (banc) | prescrit | `dumbbells` · `flat_bench_support` | ATLAS |
| 76 | Rowing machine chest-supported | prescrit | `machine_chest_supported_row` | ATLAS |
| 77 | Shoulder press haltères assis | substitut | `dumbbells` · `seated_support` | ATLAS |
| 78 | Shrugs barre | substitut | **INCONNU** | — |
| 79 | Shrugs câble | substitut | **INCONNU** | — |
| 80 | Shrugs haltères | prescrit | `dumbbells` | IDENTITE_AUREN |
| 81 | Sissy squat machine | substitut | **INCONNU** | — |
| 82 | Skull crushers EZ-bar | prescrit | `barbell_ez` · `flat_bench_support` | EXTERNE |
| 83 | Sliding leg curl | substitut | **INCONNU** | — |
| 84 | Smith shoulder press | substitut | `smith_rack` | ATLAS |
| 85 | Squat Smith machine (pieds avancés) | prescrit | `smith_rack` | ATLAS |
| 86 | Straight-arm pulldown câble | prescrit | **INCONNU** | — |
| 87 | Tirage front câble (prise large) | prescrit | **INCONNU** | — |
| 88 | Tirage poulie haute prise large | prescrit | `pulldown_seated_station` | ATLAS |
| 89 | Tirage poulie haute prise neutre | prescrit | `pulldown_seated_station` | ATLAS |
| 90 | Tirage vertical unilatéral câble | prescrit | `pulldown_seated_station` | ATLAS |
| 91 | Traction assistée machine | substitut | `machine_assisted_pull_up` | ATLAS |
| 92 | Traction assistée unilatérale | substitut | **INCONNU** | — |
| 93 | Triceps extension poulie haute (corde) | prescrit | `cable_anchor_high` · `cable_attachment_rope` | ATLAS |
| 94 | Triceps pushdown barre | prescrit | **INCONNU** | — |
| 95 | Triceps pushdown corde | prescrit | `cable_anchor_high` · `cable_attachment_rope` | ATLAS |
| 96 | Upright row câble | substitut | **INCONNU** | — |
| 97 | Upright row haltères | substitut | **INCONNU** | — |
| 98 | Y-raise haltère | substitut | **INCONNU** | — |
| 99 | Écarté arrière d'épaule câble | prescrit | `cable_anchor_any` | ATLAS |
| 100 | Écarté pec aux câbles (incliné bas→haut) | prescrit | `cable_anchor_adjustable` · `cable_bilateral_independent` | ATLAS |
| 101 | Élévations latérales câble | prescrit | `cable_anchor_low` | ATLAS |
| 102 | Élévations latérales câble (derrière le dos) | prescrit | `cable_anchor_low` | ATLAS |
| 103 | Élévations latérales haltères | substitut | **INCONNU** | — |
| 104 | Élévations latérales haltères assis | prescrit | `dumbbells` · `seated_support` | IDENTITE_AUREN |
| 105 | Élévations latérales machine | substitut | **INCONNU** | — |

## Les `UNKNOWN`, et pourquoi

* **Adduction assise** *(prescrit)* — famille `machine` : aucun slug, aucun alias d'atlas — l'identité de l'appareil n'est pas résolue
* **Adduction couchée machine** *(substitut)* — famille `machine` : aucun slug, aucun alias d'atlas — l'identité de l'appareil n'est pas résolue
* **Adduction debout câble** *(substitut)* — famille `cable` : l'appareil n'est ni slugué ni aliasé dans l'atlas, et la hauteur d'ancrage n'est ni écrite ni sourcée
* **Arnold press** *(substitut)* — famille `dumbbell` : l'implément est déclaré par la modalité, mais le libellé ne règle pas la question du SUPPORT et aucune source ne la règle
* **Back extension 45° (bias ischios)** *(substitut)* — famille `bodyweight` : l'implément est déclaré par la modalité, mais le libellé ne règle pas la question du SUPPORT et aucune source ne la règle
* **Calf press leg press** *(substitut)* — famille `machine` : aucun slug, aucun alias d'atlas — l'identité de l'appareil n'est pas résolue
* **Crunch câble à genoux** *(prescrit)* — ni modalité, ni slug, ni alias, ni libellé d'implément : rien à quoi rattacher une exigence
* **Curl câble basse** *(substitut)* — famille `cable` : l'appareil n'est ni slugué ni aliasé dans l'atlas, et la hauteur d'ancrage n'est ni écrite ni sourcée
* **Curl marteau câble (corde)** *(prescrit)* — famille `cable` : l'appareil n'est ni slugué ni aliasé dans l'atlas, et la hauteur d'ancrage n'est ni écrite ni sourcée
* **Curl marteau câble corde** *(substitut)* — famille `cable` : l'appareil n'est ni slugué ni aliasé dans l'atlas, et la hauteur d'ancrage n'est ni écrite ni sourcée
* **Curl prise neutre câble** *(substitut)* — famille `cable` : l'appareil n'est ni slugué ni aliasé dans l'atlas, et la hauteur d'ancrage n'est ni écrite ni sourcée
* **Decline crunch** *(substitut)* — ni modalité, ni slug, ni alias, ni libellé d'implément : rien à quoi rattacher une exigence
* **Dips pectoraux (buste penché)** *(prescrit)* — §3 — l'atlas déclare `equipment: bodyweight` et ne dit RIEN d'un appui : « dips » ne prouve pas des barres parallèles
* **Extension overhead câble (corde)** *(prescrit)* — famille `cable` : l'appareil n'est ni slugué ni aliasé dans l'atlas, et la hauteur d'ancrage n'est ni écrite ni sourcée
* **Good morning haltères** *(substitut)* — ni modalité, ni slug, ni alias, ni libellé d'implément : rien à quoi rattacher une exigence
* **Hanging knee raise** *(substitut)* — ni modalité, ni slug, ni alias, ni libellé d'implément : rien à quoi rattacher une exigence
* **Hip thrust haltères** *(substitut)* — famille `dumbbell` : l'implément est déclaré par la modalité, mais le libellé ne règle pas la question du SUPPORT et aucune source ne la règle
* **Kickback câble** *(prescrit)* — famille `cable` : l'appareil n'est ni slugué ni aliasé dans l'atlas, et la hauteur d'ancrage n'est ni écrite ni sourcée
* **Lat pulldown prise large** *(substitut)* — famille `cable` : l'appareil n'est ni slugué ni aliasé dans l'atlas, et la hauteur d'ancrage n'est ni écrite ni sourcée
* **Lat pulldown prise neutre** *(substitut)* — famille `cable` : l'appareil n'est ni slugué ni aliasé dans l'atlas, et la hauteur d'ancrage n'est ni écrite ni sourcée
* **Leg extension câble unilatéral** *(substitut)* — famille `cable` : l'appareil n'est ni slugué ni aliasé dans l'atlas, et la hauteur d'ancrage n'est ni écrite ni sourcée
* **Machine crunch** *(substitut)* — ni modalité, ni slug, ni alias, ni libellé d'implément : rien à quoi rattacher une exigence
* **Pallof press câble** *(prescrit)* — ni modalité, ni slug, ni alias, ni libellé d'implément : rien à quoi rattacher une exigence
* **Preacher curl** *(substitut)* — famille `machine` : aucun slug, aucun alias d'atlas — l'identité de l'appareil n'est pas résolue
* **Pushdown corde** *(substitut)* — ni modalité, ni slug, ni alias, ni libellé d'implément : rien à quoi rattacher une exigence
* **Reverse Nordic** *(substitut)* — famille `bodyweight` : l'implément est déclaré par la modalité, mais le libellé ne règle pas la question du SUPPORT et aucune source ne la règle
* **Shrugs barre** *(substitut)* — ni modalité, ni slug, ni alias, ni libellé d'implément : rien à quoi rattacher une exigence
* **Shrugs câble** *(substitut)* — ni modalité, ni slug, ni alias, ni libellé d'implément : rien à quoi rattacher une exigence
* **Sissy squat machine** *(substitut)* — ni modalité, ni slug, ni alias, ni libellé d'implément : rien à quoi rattacher une exigence
* **Sliding leg curl** *(substitut)* — famille `bodyweight` : l'implément est déclaré par la modalité, mais le libellé ne règle pas la question du SUPPORT et aucune source ne la règle
* **Straight-arm pulldown câble** *(prescrit)* — famille `cable` : l'appareil n'est ni slugué ni aliasé dans l'atlas, et la hauteur d'ancrage n'est ni écrite ni sourcée
* **Tirage front câble (prise large)** *(prescrit)* — ni modalité, ni slug, ni alias, ni libellé d'implément : rien à quoi rattacher une exigence
* **Traction assistée unilatérale** *(substitut)* — famille `machine` : aucun slug, aucun alias d'atlas — l'identité de l'appareil n'est pas résolue
* **Triceps pushdown barre** *(prescrit)* — famille `cable` : l'appareil n'est ni slugué ni aliasé dans l'atlas, et la hauteur d'ancrage n'est ni écrite ni sourcée
* **Upright row câble** *(substitut)* — ni modalité, ni slug, ni alias, ni libellé d'implément : rien à quoi rattacher une exigence
* **Upright row haltères** *(substitut)* — ni modalité, ni slug, ni alias, ni libellé d'implément : rien à quoi rattacher une exigence
* **Y-raise haltère** *(substitut)* — ni modalité, ni slug, ni alias, ni libellé d'implément : rien à quoi rattacher une exigence
* **Élévations latérales haltères** *(substitut)* — famille `dumbbell` : l'implément est déclaré par la modalité, mais le libellé ne règle pas la question du SUPPORT et aucune source ne la règle
* **Élévations latérales machine** *(substitut)* — famille `machine` : aucun slug, aucun alias d'atlas — l'identité de l'appareil n'est pas résolue

## Correspondances d'identité déclarées

* **Incline DB Press 30°** — `_aliases` de l'EKB : « Incline DB Press 30° » → « Développé incliné haltères 30° »
* **Incline Dumbbell Press** — `_aliases` de l'EKB : « Incline Dumbbell Press » → « Développé incliné haltères 30° »
* **Leg Press (pieds hauts, écartés)** — Life Fitness Leg Press ↔ « Leg Press (pieds hauts, écartés) » — même appareil, placement de pieds différent
* **Skull crushers EZ-bar** — ACE « Lying Barbell Triceps Extensions » ↔ AUREN « Skull crushers EZ-bar » — même mouvement allongé ; l'IMPLÉMENT diffère (droite vs EZ), l'exigence de banc non

🤖 Generated with [Claude Code](https://claude.com/claude-code)
