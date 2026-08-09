# SPRINT Sb_MORPHO_PROGRAM_GENERATOR_01 — Deterministic Morphology-Aware Program Generator (RAPPORT)

**Base canonique :** `1b1d36d` · **Branche :** `sb/morpho-program-generator-01` · **Tier :** ISOLATED (**module pur neuf · 0 migration · 0 DB · 0 modif substitution · 0 UI · 0 publication**)
**Spec :** `Sx_MORPHO_PROGRAM_01_SPEC` §7-§10 (SlotIntent + substitution réutilisée + availability + générateur déterministe additif) — **3ᵉ build** de la file morpho.
**Livré sous le protocole agentique** (`CLAUDE.md §4`) : `GO BUILD` → autonome jusqu'à `PR GREEN / MERGE PENDING`. **Pas de merge.**

## 1. Ce qui est livré

La couche **générateur** — 3ᵉ pont de la file : à partir de **descripteurs de morphologie** (ou des `MorphologyFacts` sous-jacents) + **priorités d'entraînement** + **availability** optionnelles, elle produit une **proposition de programme déterministe** faite de `SlotIntent`s ordonnés et d'exercices EKB candidats. Module **pur, déterministe et additif** `app/services/morpho_program_generator.py` : il **compose en lecture seule** les trois briques déjà livrées —

- `morphology_profile.build_morphology_profile` (Sb_MORPHO_PROFILE_01) — faits → descripteurs,
- `slot_intent` (Sb_PROGRAM_SLOT_INTENT_01) — descripteurs/priorités → `SlotIntent`s,
- `substitution.compute_proximity` (via `slot_intent.score_candidate`) **en LECTURE SEULE** + `substitution.load_exercise_properties` comme **pool candidat** —

et **ne modifie ni `substitution.py`, ni un template, ni `reference_split.json`, ni `exercise_properties.json`, ni une session, ni la publication, ni la DB**. Rien n'est persisté : la sortie est un objet `GeneratedProgram` **en mémoire**.

## 2. Brainstorming / Options / Risques / Choix retenu (CLAUDE.md §3)

**Préflight** (lectures des contrats réels) : `slot_intent.py` (registre 8 intentions, `target_props`/`score_candidate`/`candidate_pattern_forbidden`, double granularité zone détaillée→macro via `RADAR_AXES`), `morphology_profile.py` (`build_morphology_profile`, `guarded_not_deductible`, confidence `not_deductible`), `substitution.load_exercise_properties()` (**pool `{name: props}` — 53 entrées, taxonomie MACRO** `{pecs, back_thickness, back_width, shoulders, arms, lower}`) et `compute_proximity` (+50 zone/+20 pattern/+15 équipement/+10 chaîne/+10 muscle_group), fixture privée `martin_morphology`.

| Option | Verdict |
|---|---|
| **A** — générateur **pur** composant `morphology_profile` + `slot_intent` + `compute_proximity` **lecture seule** + pool `exercise_properties`, sortie proposition **en mémoire** (fingerprint déterministe) | ✅ **RETENU** — 0 DB/migration/substitution/publication, additif, déterministe, testable |
| **B** — générateur écrivant un `WorkoutTemplate`/Custom Program | ✗ interdit ce sprint (persistance, publication, EKB) — build `Sb_MARTIN_PROGRAM_01` |
| **C** — nouveau moteur de scoring propre | ✗ duplique `compute_proximity`, divergence de contrat |

**Point dur résolu — la zone macro `lower` est surchargée.** `exercise_properties.zone_primary` fusionne quadriceps/ischios/adducteurs/**mollets** sous `lower`. Un scoring naïf (zone + pattern) aurait fait **choisir une leg extension pour un slot mollets** (même zone `lower`, même pattern `isolation_lower`) — une **fabrication silencieuse**. **Choix retenu** : désambiguïser `lower` par la **taxonomie `muscle_group` existante**, clé = `primary_zone` détaillée du slot (`quads→quadriceps`, `posterior→hamstrings`, `calves→"calves"`). Les mollets n'ayant **aucun représentant dans le pool**, ils ne qualifient rien → **warning explicite de couverture, jamais un faux exercice de jambe**. Les zones hautes (`pecs`/`back_thickness`/`shoulders`/`arms`) restent qualifiées par **pattern_motor** exact. C'est l'invariant « unsupported taxonomy names omitted with explicit warning ».

**Risques traités** :
1. **Fabrication d'un exercice hors intention** (mollets/latéraux/rear-delts/hinge absents du pool) → contrat de qualification **zone + (pattern | muscle_group)** + **filtre `forbidden`** → ces slots renvoient **`preferred=None` + warning de couverture**. *Testé.*
2. **Modif substitution** → **aucune** : import lecture seule de `compute_proximity`/`load_exercise_properties` ; `substitution.py` inchangé, N1/N2/N3 intacts. *Testé + broad sweep substitution vert.*
3. **Mutation de données** → générateur pur ; sha de `reference_split.json` + `exercise_properties.json` **inchangés** après génération ; pool partagé (`lru_cache`) **non muté** (lecture seule). *Testé.*
4. **Couplage publication/session** → **aucun import** de `session_builder`/`publication`/routes/models/DB (garde statique AST). *Testé.*
5. **Non-déterminisme** → itération triée du pool, tri stable `(-score, name)`, fingerprint `sha256` (aucune horloge/aléa). Même entrée ⇒ même `generated_program_id` + mêmes sélections. *Testé.*
6. **Hardcoding Martin** → **aucun** dans la logique globale ; Martin n'est qu'une **fixture de test privée**. *Vérifié.*
7. **Calves sans preuve** → `calves` n'est pas un descripteur morphologie mappé ; il ne peut venir **que d'une priorité explicite** → invariant « calves only if descriptor/priority evidence exists ». *Testé.*

## 3. Fichiers touchés (2 + docs)

| Fichier | Changement |
|---|---|
| `app/services/morpho_program_generator.py` (**neuf, pur**) | `SlotSelection`/`RejectedDescriptor`/`GeneratedProgram` (dataclasses frozen) · `generate_program()` · `_compose_slot_intents` (dedup par intent_id, re-slotting stable) · `_qualifies`/`_rank_qualifying`/`_select_for_slot` (réutilisation `compute_proximity` lecture seule + désambiguïsation `lower` par `muscle_group`) · `_fingerprint` (sha256 déterministe) |
| `tests/test_morpho_program_generator.py` (**neuf**) | 18 tests |
| docs | ce rapport + registry + roadmap |
| **`substitution.py` / `slot_intent.py` / `morphology_profile.py` / modèles / migrations / templates / `reference_split.json` / session flow / publication** | **aucun** |

## 4. Modèle livré

`generate_program(*, facts=None, descriptors=None, priorities=(), availability=None, pool=None, max_fallbacks=3) -> GeneratedProgram`.

**Entrées** : `facts` (`MorphologyFacts` → descripteurs) **ou** `descriptors` explicites (prioritaires, permet d'injecter un descripteur gardé en test) ; `priorities` `(clé, rang)` (ex. `calves`) ; `availability` (familles d'équipement Fitness Park) ; `pool` (défaut **lecture seule** `load_exercise_properties()`).

**Sortie `GeneratedProgram`** (données pures, jamais persistées) : `generated_program_id` (**fingerprint sha256 stable**, préfixe `mpg1-`) · `engine_version` · `source_descriptors` · `priorities` · `availability` · `selections` (liste ordonnée de `SlotSelection` : `slot_id`/`intent_id`/`primary_zone`/`target_region`/`movement_pattern`/`priority_level`/`preferred_exercise`/`preferred_score`/`fallback_candidates`/`rationale`/`warning`/`slot_intent`) · `rejected_descriptors` (gardés/`not_deductible` → aucun slot) · `warnings` (couverture manquante / availability / proposition vide).

**Distinction honnête des manques** : **coverage gap** (rien ne qualifie — trou EKB/properties) ≠ **availability gap** (des candidats qualifient mais aucun disponible sous `availability`). Aucun des deux ne fabrique un exercice.

## 5. Tests

`tests/test_morpho_program_generator.py` — **18 passés** : déterminisme depuis la fixture Martin (fingerprint + `to_dict` égaux) · fingerprint sensible aux entrées · **descripteurs Martin → {lateral_delt, upper_chest, rear_delt}** · **3 mappings descripteur→intent requis** · **8 intentions « Full Body — Morphotype Priority » reproductibles** (déterministe) · **sélections réelles** (upper_chest→pecs push_horizontal 80 · upper_back→back_thickness pull_horizontal 80 · quad→quadriceps 60) · **quads en maintien** (un seul slot `quad_minimum_effective_dose`) · **slots à taxonomie creuse → warning de couverture, 0 fabrication** (posterior/latéral/rear/mollets×2) · **calves seulement sur preuve de priorité** (jamais depuis descripteurs seuls ; priorité `calves` → 2 slots, `preferred=None`) · **gardé → 0 slot + `rejected_descriptors`** · proposition vide → warning · **availability filtre** (machine → machine) · **availability gap** (kettlebell → warning) · **0 mutation** `reference_split.json`/`exercise_properties.json` (sha) + pool partagé intact · **garde statique AST : aucun import** session_builder/publication/routes/models/DB · **contrat substitution inchangé** (`compute_proximity` 105/85, `VALID_PATTERN_MOTORS==11`, `score_candidate==compute_proximity`) · slot_intent map toujours ses descripteurs.

**Broad sweep ciblé** (substitution + tiered + last_time + last_time_substitution + atlas_follows + muscle_mapping + morphology + full_body + catalog + catalog_cleanup + slot_intent + generator + user_program×2) : **180 passés** — **substitution N1/N2/N3 vert, inchangé**.

## 6. Interdits tenus

**0 modif `substitution.py`** (N1/N2/N3 inchangés, « pattern différent ⇒ jamais N1/N2 » préservé, `compute_proximity` inchangé) · **0 DB/migration/table/modèle** · **0 UI / `/library`** · **0 publication / cycle Custom Program / création de template** · **0 modif `reference_split.json` / `exercise_properties.json` / EKB** (aucune expansion) · **0 changement session flow / prévu-réalisé** · **0 hardcoding Martin** en logique globale (fixture de test privée uniquement) · **0 génération/persistance de programme Martin** (build suivant `Sb_MARTIN_PROGRAM_01`).

## 7. Validation

check_scope **ISOLATED** · `check_spec_protocol` PASS · `check_ruff_budget` **544 ≤ 548** · `ruff check` fichiers neufs **clean**.

## Verdict

**Verdict :** ✅ **Sb_MORPHO_PROGRAM_GENERATOR_01 — PR GREEN / MERGE PENDING (à valider en CI).** Générateur **pur, déterministe et additif** : descripteurs/priorités morphologie → intentions de slot → exercices EKB candidats via `compute_proximity` **lecture seule**, **substitution N1/N2/N3 inchangée** (0 modif), 0 DB/migration/publication, **manques de couverture signalés honnêtement (0 fabrication)**. **Le merge reste un GO humain.**
