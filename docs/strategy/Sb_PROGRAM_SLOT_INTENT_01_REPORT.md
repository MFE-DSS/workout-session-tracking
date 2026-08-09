# SPRINT Sb_PROGRAM_SLOT_INTENT_01 — Pure SlotIntent Layer (RAPPORT)

**Base canonique :** `c689429` · **Branche :** `sb/program-slot-intent-01` · **Tier :** ISOLATED (**module pur neuf · 0 migration · 0 DB · 0 modif substitution**)
**Spec :** `Sx_MORPHO_PROGRAM_01_SPEC` §7 (SlotIntent) + §8 (substitution réutilisée) — 2ᵉ build de la file morpho.
**Livré sous le protocole agentique** (`CLAUDE.md §4`) : `GO BUILD` → autonome jusqu'à `PR GREEN / MERGE PENDING`.

## 1. Ce qui est livré

La couche **SlotIntent** — 1ᵉʳ pont morphologie→programmation : un `SlotIntent` décrit **ce qu'un slot d'exercice doit accomplir** (zone cible, pattern moteur, intention, priorité, substitutions acceptables/interdites), **entièrement sur la taxonomie existante**. Module **pur et additif** `app/services/slot_intent.py` : il **réutilise `substitution.compute_proximity` en lecture seule** (import + appel) et **ne modifie pas** `substitution.py` — N1/N2/N3 runtime et la garantie « pattern différent ⇒ jamais N1/N2 » **intacts**.

## 2. Brainstorming / Options / Risques / Choix retenu (CLAUDE.md §3)

**Préflight** : lecture de `substitution.py` (`compute_proximity` : +50 zone/+20 pattern/+15 équipement/+10 chaîne/+10 muscle_group ; enum `PatternMotor` 11 valeurs) + `exercise_properties.json` (**taxonomie macro** : `zone_primary ∈ {pecs, shoulders, back_width, back_thickness, arms, lower}` = les RADAR_AXES ; couverture **partielle** 53 entrées) + `muscle_mapping` (11 zones détaillées + `RADAR_AXES`) + `morphology_profile` (descripteurs priority_candidate).

| Option | Verdict |
|---|---|
| **A** — module **pur** `SlotIntent` + réutilisation **lecture seule** de `compute_proximity`, cibles exprimées dans la taxonomie existante | ✅ **RETENU** — 0 modif substitution, 0 DB/migration, additif, testable |
| **B** — moteur de matching neuf (recalcul de proximité) | ✗ duplique `compute_proximity`, risque de divergence de contrat |
| **C** — modifier `substitution.py` pour accepter un slot | ✗ interdit (sauf STOP) ; casserait potentiellement N1/N2/N3 |

**Double granularité de zone** (résout la taxonomie macro vs détaillée) : `primary_zone` = zone **détaillée** (muscle_mapping : delt_lat, pecs, upper_back…) ; `target_region` = zone **macro** (exercise_properties : shoulders, pecs, lower…), **dérivée** de `primary_zone` via `RADAR_AXES` (réutilisation, jamais redéfinie) → sert au `compute_proximity`.

**Risques traités** :
1. **Modif substitution** → **aucune** : import lecture seule ; test dédié pinne `VALID_PATTERN_MOTORS==11`, `BADGE_N1`, seuil N2, et « pattern différent ⇒ N3 » via `_classify_suggestion`. *Testé + broad sweep substitution vert.*
2. **Mutation catalogue/properties** → module pur ; hash de `reference_split.json` + `exercise_properties.json` **inchangés** après build + scoring. *Testé.*
3. **Fabrication depuis descripteurs non pertinents** → seuls les `*_priority_candidate` non-`not_deductible` produisent un intent ; faits/inférences/gardés → **rien**. *Testé.*
4. **Couverture partielle des properties** (hack/RDL/mollets/latérales absents) → assumée : la SlotIntent **représente** l'intention depuis la taxonomie ; le scoring `compute_proximity` sert les exercices couverts (gaps EKB_02 différés). *Documenté.*

## 3. Fichiers touchés (2 + docs)

| Fichier | Changement |
|---|---|
| `app/services/slot_intent.py` (**neuf, pur**) | `SlotIntent` (dataclass frozen) · `INTENT_REGISTRY` (8 intentions) · `PRIORITY_TO_INTENTS` · `DESCRIPTOR_TO_INTENT` · builders (`build_slot_intent`, `_from_priorities`, `_from_descriptors`) · `target_props`/`score_candidate`/`candidate_pattern_forbidden` (réutilisation `compute_proximity` lecture seule) |
| `tests/test_slot_intent.py` (**neuf**) | 12 tests |
| docs | rapport + registry + roadmap |
| **`substitution.py` / models / migrations / session flow / generator** | **aucun** |

## 4. Modèle livré

`SlotIntent(slot_id, intent_id, primary_zone, target_region, secondary_zones, movement_pattern, chain, priority_level, preferred_exercise_name, acceptable_substitution_families, forbidden_substitution_patterns, rationale, source_descriptors, engine_version)`. **8 intentions** enregistrées (`upper_chest_primary_press`, `upper_back_depth_row`, `quad_minimum_effective_dose`, `posterior_chain_hinge`, `lateral_delt_priority`, `rear_delt_upper_back_accessory`, `calves_gastrocnemius_priority`, `calves_soleus_priority`) — les 8 intentions du programme catalogue « Full Body — Morphotype Priority ». Mappings priorité→intents et **descripteur morphologie→intent** (les 3 `*_priority_candidate` de `Sb_MORPHO_PROFILE_01`).

## 5. Tests

`tests/test_slot_intent.py` — **12 passés** : build depuis priorités (calves→gastroc+soléaire) · priorité inconnue ignorée · **descripteur morphologie Martin → {lateral_delt, upper_chest, rear_delt}** · **gardé/non-priorité → aucun intent** · **8 intentions Full Body représentables** (zone détaillée/macro/pattern) · intent inconnu → None · taxonomie valide · `score_candidate == compute_proximity` + match > mismatch · garde pattern interdit · **0 mutation** catalogue/properties (hash) · **contrat substitution inchangé** (11 patterns, N3 sur pattern différent) · déterminisme.

**Broad sweep** (substitution + tiered + last_time + atlas_follows + muscle_mapping + morphology + full_body + catalog + slot_intent) : **123 passés** — **substitution N1/N2/N3 vert, inchangé**.

## 6. Interdits tenus

**0 modif `substitution.py`** (N1/N2/N3 inchangés, « pattern différent ⇒ jamais N1/N2 » préservé, identité prévu stable, historique intact) · **0 DB/migration/table** · 0 changement session flow / prévu-réalisé / publication Custom · 0 expansion EKB · 0 UI · **0 générateur** (build suivant) · **0 génération programme Martin** (build suivant).

## 7. Validation

check_scope **ISOLATED** · `check_spec_protocol` PASS · `check_ruff_budget` **543 ≤ 548** · `ruff check` fichiers neufs **clean**.

## Verdict

**Verdict :** ✅ **Sb_PROGRAM_SLOT_INTENT_01 — MERGED + CANONICAL CI GREEN.** Couche `SlotIntent` **pure et additive** : priorités/descripteurs morphologie → intentions de slot dans la taxonomie existante, `compute_proximity` **réutilisé en lecture seule**, **substitution N1/N2/N3 inchangée** (0 modif), 0 DB/migration/générateur.

---

## Appendice post-merge (closeout)

- **Merge** : PR **#63 MERGED** 2026-08-09, build `ef549c8` + fix Sonar `6b95ac4`, merge commit **`2c989bd`** via `--merge --match-head-commit 6b95ac4` — **sans squash, sans `--admin`** (gate `CLEAN`, 0 thread).
- **CI canonique** : run **`31329924105`** 3/3 GREEN sur `2c989bd` (pytest+QA · lint · SonarCloud) ; `app/services/slot_intent.py` = **0 issue** Sonar sur main.
- **Incident CI de PR résolu in-scope** : gate Sonar rouge sur `new_vulnerabilities_severity 10 > 9` — **3× `bandit:B101`** (`assert` d'invariant au chargement du module, strippés en `python -O`) → convertis en `raise ValueError` (`6b95ac4`), même convention que `substitution.py` ; invariant préservé et couvert par `test_intents_use_valid_taxonomy`. new_coverage/smells étaient OK.
- **Cleanup** : branche `sb/program-slot-intent-01` + worktree `workout-session-tracking-slot-intent` **conservés** — suppression = **GO humain séparé**.
- **File restante** (sur GO) : `Sb_MORPHO_PROGRAM_GENERATOR_01` → `Sb_MARTIN_PROGRAM_01` → `Sb_MORPHO_DOGFOOD_01`.
