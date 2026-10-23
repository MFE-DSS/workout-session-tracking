# AUREN V2 catalogue — identity contract, duplicate pass

Date: 2026-10-23. Operator rulings applied: R10 (duplicate review), R2 (identity part), R3 (identity part), R12.
Output: `identity_map.json`, one entry for each of the 107 `exercise_id`s. No historical id is deleted or rewritten. Each LEGACY_ALIAS points to the CANONICAL record of its identity. The V2 compiler sees exactly one candidate per `scientific_identity_id`.

## Decision rule (applied to source facts, not to curator guesses)

- **EXACT_CANONICAL_DUPLICATE**: the names differ only by synonym, translation or word order, and no source fact separates them (requirements, atlas cues, template notes). This also covers an entry whose own facts state the qualifier the other carries in its name, for example a template note "Banc à 45°" or an atlas cue "câble derrière le dos".
- **LEGITIMATE_VARIANT**: both entries state different values of a dimension (attachment, grip, foot placement, body position, laterality, equipment). This also covers a qualified entry next to a generic one whose name denotes a clearly different default, for example bilateral vs "unilatéral" or standing vs "assis".
- **UNRESOLVED**: one entry states a qualifier, the other is silent, and the qualifier is a plausible default of the generic entry, so the generic may be the same exercise. It also covers cases where the source facts conflict or the name is ambiguous. Each record keeps its own identity and is flagged here.
- **Choosing the canonical record**: in an exact group, the canonical is the entry whose name and facts state the execution most completely, judged on a stated attachment or angle, an atlas card of the same name, and stated requirements.
- **Atlas card sharing**: a shared card is not used as proof on its own. The card describes a machine or station; "Lat pulldown", for example, is also attached to the unilateral pulldown. A card's cues are used only as facts about the exercise the card is named after.

## Reviewed groups

| # | Members | Classification | Canonical chosen | Reason (source facts) |
|---|---|---|---|---|
| G01 | hip-thrust-smith, hip-thrust-smith-machine | EXACT | hip-thrust-smith → `smith_hip_thrust` | "Smith" = "Smith machine"; same atlas card "Hip thrust Smith", same `smith_rack`, template notes say the same thing |
| G02 | hip-thrust-halteres vs G01 | LEGITIMATE_VARIANT | — (own identity `dumbbell_hip_thrust`) | dumbbell vs Smith: equipment differs |
| G03 | mollets-debout-machine, releves-mollets-debout-machine | EXACT | releves-mollets-debout-machine → `standing_calf_raise_machine` | same `machine_standing_calf_raise`; the atlas card on releves-… is named "Mollets debout machine" |
| G04 | releves-mollets-debout vs G03 | LEGITIMATE_VARIANT | — (`bodyweight_standing_calf_raise`) | bodyweight, requirements [] vs machine |
| G05 | roulette-abdominale, roulette-abdominale-paren-ab-wheel-rollout | EXACT (R2) | roulette-abdominale → `kneeling_ab_wheel_rollout` | same `ab_wheel`, both templates "Genoux au sol … extension complète si possible" |
| G06 | pushdown-corde, triceps-pushdown-corde | EXACT | triceps-pushdown-corde → `cable_rope_triceps_pushdown` | same name minus "Triceps"; pushdown-corde has every legacy field null |
| G07 | triceps-pushdown-barre vs G06 | LEGITIMATE_VARIANT | — (`cable_straight_bar_triceps_pushdown`) | straight bar vs rope, both stated |
| G08 | triceps-extension-poulie-haute-paren-corde vs G06 / G09 | UNRESOLVED | — (`high_pulley_rope_triceps_extension`) | same requirements as triceps-pushdown-corde (high anchor + rope), but the name can be a rope pushdown or an overhead extension facing away; no cue or note |
| G09 | extension-overhead-cable-paren-corde vs pushdowns | LEGITIMATE_VARIANT | — (`cable_rope_overhead_triceps_extension`) | overhead shoulder position stated (name + "position haute") |
| G10 | cable-cross-over-paren-bashaut, ecarte-pec-aux-cables-paren-incline-bashaut | EXACT | cable-cross-over-paren-bashaut → `low_to_high_cable_fly` | cross-over = écarté aux câbles; both bas→haut; same card, same requirements (two independent columns, no bench); templates agree |
| G11 | curl-cable-basse, curl-poulie-basse | EXACT | curl-poulie-basse → `low_cable_biceps_curl` | câble = poulie, both "basse"; no attachment, cue or note on either |
| G12 | curl-poulie-basse-paren-barre vs G11 | UNRESOLVED | — (`low_cable_straight_bar_curl`) | bar stated; the generic states no attachment and the bar is its usual default |
| G13 | curl-marteau-cable-corde, curl-marteau-cable-paren-corde | EXACT | curl-marteau-cable-paren-corde → `cable_rope_hammer_curl` | identical words; only parentheses differ |
| G14 | curl-prise-neutre-cable vs G13 | UNRESOLVED | — (`cable_neutral_grip_curl`) | neutral grip = hammer grip; attachment (rope or handles) and anchor unstated |
| G15 | curl-incline-halteres, curl-incline-halteres-paren-banc-45 | EXACT | curl-incline-halteres-paren-banc-45 → `incline_dumbbell_curl_45` | the generic's own template note says "Banc à 45°, laisser les bras pendre"; same requirements |
| G16 | lat-pulldown-prise-large, tirage-poulie-haute-prise-large | EXACT | tirage-poulie-haute-prise-large → `wide_grip_lat_pulldown` | Lat pulldown = Tirage poulie haute (the card is named "Lat pulldown"); "prise large" in both names |
| G17 | lat-pulldown-prise-neutre, tirage-poulie-haute-prise-neutre | UNRESOLVED | — (`neutral_grip_lat_pulldown`, `close_neutral_grip_lat_pulldown`) | the names translate each other, but only tirage-… states a width ("Prise neutre serrée"); close V-handle and wide parallel handles are both neutral grips |
| G18 | tirage-vertical-unilateral-cable vs pulldowns | LEGITIMATE_VARIANT | — (`unilateral_cable_pulldown`) | one arm at a time (name + template) |
| G19 | rear-delt-fly-machine, rear-delt-fly-machine-paren-pec-deck-inverse, reverse-fly-machine | EXACT | rear-delt-fly-machine → `reverse_pec_deck_fly` | same `machine_rear_delt_fly`; reverse fly = rear delt fly = reverse pec deck; cues agree |
| G20 | face-pull-cable, face-pull-cable-paren-corde | EXACT | face-pull-cable-paren-corde → `cable_rope_face_pull` | same high anchor and card; the generic's card prescribes a pull to the face with external rotation and thumbs back, which requires a split attachment; no fact separates the two |
| G21 | pullover-cable-paren-bras-tendus-poulie-haute, straight-arm-pulldown-cable | UNRESOLVED | — (`high_pulley_straight_arm_cable_pullover`, `straight_arm_cable_pulldown`) | the name describes the straight-arm pulldown movement, but its source equipment conflicts (`machine_pullover`, "Pullover machine" card); its attachment is unstated vs a bar |
| G22 | pullover-cable-paren-bras-tendus vs G21 / G23 | UNRESOLVED | — (`straight_arm_cable_pullover`) | anchor height unstated (standing high pulley vs lying low pulley); same name/equipment conflict |
| G23 | pullover-machine vs the cable pullovers | LEGITIMATE_VARIANT | — (`machine_pullover`) | machine by name, requirement and card (holds if the cable names are right, see G22) |
| G24 | rowing-chest-supported, rowing-machine-chest-supported | UNRESOLVED | — (`chest_supported_row_elbows_open`, `chest_supported_row_machine`) | same machine requirement, and the card attached to the second entry bears the first's name, but their cues contradict ("coudes légèrement ouverts" vs "coudes vers les hanches"); rowing-chest-supported science is DISPUTED |
| G25 | elevations-laterales-cable, elevations-laterales-cable-paren-derriere-le-dos | EXACT | …-paren-derriere-le-dos → `behind_back_cable_lateral_raise` | the generic's own card prescribes "Position câble derrière le dos"; same low anchor, unilateral |
| G26 | elevations-laterales-halteres, elevations-laterales-halteres-assis | LEGITIMATE_VARIANT | — (`standing_dumbbell_lateral_raise`, `seated_dumbbell_lateral_raise`) | seated (seated_support + "Rester assis") vs generic standing |
| G27 | tirage-front-cable-paren-prise-large, upright-row-cable | UNRESOLVED (R12) | — (`wide_grip_cable_upright_row` "Tirage menton câble — prise large", `cable_upright_row`) | the tirage template ("menton, coudes hauts") puts it in the upright-row family, with a wide grip stated; upright-row-cable states no width or attachment |
| G28 | leg-press-paren-pieds-bas, leg-press-paren-pieds-bas-serres | UNRESOLVED | — (`leg_press_low_feet`, `leg_press_low_narrow_feet`) | same card and quad intent; the generic "pieds bas" states no stance width |
| G29 | leg-press-paren-pieds-hauts-ecartes vs G28 | LEGITIMATE_VARIANT | — (`leg_press_high_wide_feet`) | high/wide vs low feet (card: "pieds hauts = fessiers/ischios") |
| G30 | releve-de-jambes-suspendu, hanging-knee-raise | UNRESOLVED | — (`hanging_leg_raise`, `hanging_bent_knee_raise`) | template "monter les genoux au-dessus des hanches" does not say whether the legs are straight or bent |
| G31 | rowing-haltere-un-bras, rowing-haltere-un-bras-paren-banc | UNRESOLVED | — (`one_arm_dumbbell_row`, `bench_supported_one_arm_dumbbell_row`) | the generic states no support; bench support is the common form |
| G32 | machine-shoulder-press, neutral-grip-shoulder-press-machine | LEGITIMATE_VARIANT | — (`machine_overhead_press`, `neutral_grip_machine_overhead_press`) | neutral grip stated vs the generic "coudes à hauteur des épaules": grip/plane differs |
| G33 | rowing-cable-assis-prise-large / -prise-neutre / -prise-serree | LEGITIMATE_VARIANT | — (3 identities) | three different grips stated in the names on one station |
| G34 | traction-assistee-machine, traction-assistee-unilaterale | LEGITIMATE_VARIANT | — (2 identities) | laterality differs |
| — | y-raise-haltere | UNIQUE (R3) | `prone_incline_y_raise` | identity fixed by operator ruling R3 |

All other records are UNIQUE: no other entry shares their name, equipment and execution.

## Counts

| Item | Count |
|---|---|
| Records | 107 |
| Canonical scientific identities (= compiler candidates) | 94 |
| Legacy aliases | 13 (12 exact groups: 11 pairs + 1 triple) |
| Records in exact groups (canonical + alias) | 25 |
| Legitimate variants (records) | 16 |
| Unresolved (records, each keeps its own identity) | 18, in 11 groups |
| Unique | 48 |

## For the operator (UNRESOLVED queue)

Each of these can be merged later by one decision on the execution. No merge was made:
- G08: triceps extension poulie haute (corde): is it the pushdown or the overhead extension?
- G12: curl poulie basse: is the attachment the bar?
- G14: curl prise neutre câble: is it the rope hammer curl?
- G17: lat pulldown prise neutre: is it the close V-handle?
- G21, G22: the cable pullovers. Fix the EKB equipment first (`machine_pullover` on cable-named entries).
- G24: chest-supported row: does the elbow path follow the card or the template?
- G27: upright row câble: what grip width?
- G28: leg press pieds bas: what stance width?
- G30: hanging leg raise: straight or bent legs?
- G31: one-arm dumbbell row: bench support?
