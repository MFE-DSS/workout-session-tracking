# SPIGNOS Exercise System Consolidation — Final Spec

**Sprint:** Sx_04_exercise_system_consolidation_spec (FINAL)
**Date:** 2026-04-14
**Status:** Final, consolide les 3 specs fondatrices finalisees
**Supersedes:** version Sx_04 reconciliee anterieure (nov. 2026-04-14) — integree comme premier passage, ce document est la version FINALE post-Sx_01/02/03 FINAL

**Inputs consolides :**
- `SPIGNOS_EXERCISE_FEEDBACK_RATIONALIZATION_SPEC_FINAL.md` (Sx_01 FINAL)
- `SPIGNOS_MOBILE_EXERCISE_ENTRY_UX_SPEC_FINAL.md` (Sx_02 FINAL)
- `SPIGNOS_EXERCISE_SUBSTITUTION_GRAPH_SPEC_FINAL.md` (Sx_03 FINAL)
- Reference historiques (Sx_02 v1, Sx_03.1) marquees "BUILT + SEE FINAL"

---

## 1. Decisions structurantes consolidees

### 1.1 Tableau maitre des decisions

| Zone | Decision | Source | Statut build |
|------|----------|--------|--------------|
| Signal set-level primaire | weight_kg, reps, completed (saisis objectifs) | Sx_01 FINAL D1 | **Built** |
| Signal exercise-level primaire | muscle_sensation (saisi optionnel dans `<details>`), free_note | Sx_01 FINAL D2, D5 | **Built** |
| Signal exercise-level derive | success_score (via `compute_success_score` sur reps vs rep_targets × completion_ratio) | Sx_01 FINAL D1 | **Built** |
| Signal exercise-level orphelin | execution_quality, reps_target (retires de l'UI, colonnes DB preservees) | Sx_01 FINAL D3 | **Built** |
| Signal session-level primaire | concentration, global_state, bodyweight_kg, free_note (saisis optionnels) | Sx_01 FINAL D4 | **Built** |
| Composant exercice mobile | `<details>` par carte, un seul ouvert par defaut, focus-first | Sx_02 FINAL §3-§4 | **Built** (Sb_02) |
| Jump bar 4 etats | future / active / partial / done | Sx_02 FINAL §6.1 | **Built** (Sb_02.1) |
| CTA contextuel | `Enregistrer et passer a {next_code}` / `Enregistrer et terminer` / fallback `Enregistrer` | Sx_02 FINAL §4.2 | **Built** (Sb_02.1) |
| Footer sticky CSS cible | `details[open] .card__actions--exercise` sticky natif, graceful fallback | Sx_02 FINAL §5 | **Built** (Sb_02.1) |
| Flow save → next | POST exercise card, derive success_score, 303 vers `?active={next_id}#exercise-{next_id}` | Sx_02 FINAL §7.1 | **Built** |
| Flow terminal | `action=end` → status=completed → 303 vers `/sessions/{id}/done` | Sb_R3 | **Built** |
| Reopen | `action=reopen` → status=in_progress → 303 vers editable | Sb_R3 | **Built** |
| Prevu vs realise | snapshots immutables (`exercise_name_snapshot`) + substituted_name nullable | Sx_03 FINAL §2, §7 | **Built** |
| Substitution locale | picker `<details>` bloc 4 du body, lock `can_substitute()`, radio group `name="substituted_name"` | Sx_03 FINAL §5 | **Built** (Sb_03) |
| Graphe catalogue | JSON-based dans `reference_split.json`, versione, QA script valide classifiability | Sx_03 FINAL §10 | **Built** |
| Canonical Exercise entity | **DEFERRED** jusqu'a 2+ triggers Sx_03.1 atteints | Sx_03 FINAL §14, P5 | Not built (par design) |
| Niveaux d'equivalence inline | Option A (JSON `{name, level}`) **DEFERRED** a P4 | Sx_03 FINAL §4.2 | Not built (par design) |
| Taxonomie mouvement | 6 dimensions V1 proposees mais **DEFERRED** jusqu'a Option 2 ou feature dedie | Sx_03 FINAL §3 | Not built (par design) |
| Raison de substitution | `substitution_reason` enum nullable, **DEFERRED** a P3 | Sx_03.1 Gap 2, Sx_03 FINAL P3 | Not built (optionnel) |

### 1.2 Resume en une phrase

Le systeme exercice SPIGNOS V2 est **entierement specifie et integralement build**. Les decisions structurelles sont verrouillees, les deviations sont documentees, et toutes les extensions futures sont gardees sous triggers explicites.

---

## 2. Matrice de compatibilite croisee Sx_01 × Sx_02 × Sx_03

### 2.1 Points de rencontre

| # | Decision cross-spec | Sx_01 | Sx_02 | Sx_03 | Conflit ? | Arbitrage final |
|---|--------------------|-------|-------|-------|-----------|----------------|
| 1 | Formulaire exercice contient : weight/reps/completed/muscle_sensation/free_note/substituted_name | source | applique | applique | Non | OK — liste close. Aucun autre input. |
| 2 | `success_score` derive cote serveur, pas saisi | source | applique (absent UI) | neutre | Non | OK |
| 3 | `execution_quality` / `reps_target` orphelins | source | applique (absent UI) | neutre | Non | OK |
| 4 | Position du substitute picker dans le body | neutre | fige (bloc 4/12) | applique | Non | OK — garde-fou verrouille |
| 5 | Lock `can_substitute()` apres premier set completed | neutre | fige | source | Non | OK |
| 6 | Snapshot `exercise_name_snapshot` immutable | neutre (utilise en fallback) | utilise dans `<summary>` | source | Non | OK |
| 7 | Rendu summary carte : `substituted_name or exercise_name_snapshot` | neutre | source (§4.1) | applique | Non | OK — garde-fou verrouille |
| 8 | CTA "Enregistrer et terminer" sur dernier exercice | neutre | source (§4.2) | neutre | Non | OK — pas conflit avec "Terminer la seance" du feedback session |
| 9 | Reouverture d'une session completed permet re-save qui recalcule success_score | source (doctrine) | expose via action=reopen | neutre | Non | OK — consequence assumee |
| 10 | Reouverture d'un exercice done conserve substituted_name (immutable via snapshot logique) | neutre | expose edition | applique | Non | OK — si user change substituted_name et recoche, le nouveau est applique (sauf si set deja completed, can_substitute False) |
| 11 | Muscle_sensation dans `<details>` optionnel | source (decision A assouplie en deviation acceptee) | expose dans body bloc 10 | neutre | Non | OK — deviation documentee en Sx_01 FINAL §13 |
| 12 | Free_note 140 chars au niveau exercice | source | expose | neutre | Non | OK |
| 13 | Free_note 280 chars au niveau session | source | expose dans bloc feedback | neutre | Non | OK |
| 14 | Zero JS dans le composant | neutre | fige | applique | Non | OK — substitute picker est un `<details>` natif |
| 15 | Slot-based vs exercise-based analytics | source (doctrine derivee) | neutre | source (§8) | Non | OK — deux grammaires coexistantes, `actual_exercise_name()` pont |

**Conflits detectes : 0.** Les 3 specs sont coherentes entre elles par construction.

### 2.2 Dependances directionnelles

```
Sx_01 FINAL (signal verrouille)
    │
    ├── impose → Sx_02 (liste close des inputs visibles)
    │           Sx_02 ne peut PAS reintroduire success_score radio
    │
    └── neutre → Sx_03 (substitution ne touche pas au signal set/exercise)

Sx_02 FINAL (composant fige)
    │
    └── impose → Sx_03 (6 garde-fous position/lock/fallback/parsing/data/zero-JS)
                Sx_03 ne peut PAS deplacer le picker ni changer la structure

Sx_03 FINAL (substitution)
    │
    ├── consomme → actual_exercise_name pour analytics exercise-based
    │
    └── ignore → slot-based analytics (last_time, delta, progression) via snapshots
```

### 2.3 Contradictions apparentes resolues

**Contradiction apparente 1 :** Sx_01 decision A initiale disait "success_score saisi manuellement", mais le build Sb_01 a derive. 
→ Resolution : Sx_01 FINAL reconcilie la realite comme doctrine canonique (D1 = derive). Plus de conflit.

**Contradiction apparente 2 :** Sx_02 v1 disait "pending build", mais Sb_02 est deja en production.
→ Resolution : Sx_02 original marque "BUILT + SEE FINAL". Sx_02 FINAL est la reference courante.

**Contradiction apparente 3 :** Sx_03 v1 disait "Canonical Exercise DO NOT BUILD", Sx_03.1 disait "DEFERRED jusqu'a triggers".
→ Resolution : Sx_03 FINAL conserve "DEFERRED" avec 6 triggers explicites. Meme position, wording plus propre.

**Aucune contradiction structurelle restante.**

---

## 3. Modele unifie final du systeme exercice

### 3.1 Taxonomie par niveau + statut

**Niveau SET (table `set_logs`)**

| Champ | Nature | Visibilite UI | Role |
|-------|--------|---------------|------|
| `weight_kg` | Saisi objectif | Standard | Input number step 0.5 |
| `reps` | Saisi objectif | Standard | Input number inputmode numeric |
| `completed` | Saisi objectif | Standard | Checkbox "Fait" |
| `execution_quality` | **Orphelin** | Absent UI | Colonne DB preservee |
| `reps_target` | **Orphelin** | Absent UI | Colonne DB preservee |
| `technique` | Structurel catalogue | Display seulement | Tag RP / DS herite |
| `kind` | Structurel | Display seulement | warmup / work |
| `set_index` | Structurel | Display seulement | Ordinal scope par kind |

**Niveau EXERCICE (table `session_exercises`)**

| Champ | Nature | Visibilite UI | Role |
|-------|--------|---------------|------|
| `success_score` | **Derive cote serveur** | Absent UI en input, affiche en recap | 100/80/50 via `compute_success_score` |
| `muscle_sensation` | Saisi optionnel | Collapsed (`<details>`) | strong/partial/weak |
| `free_note` | Saisi optionnel | Standard | Textarea 140 chars |
| `substituted_name` | Saisi optionnel (Sx_03) | Picker si dispo, badge si choisi | Nom reel si substitue |
| `exercise_code_snapshot` | Structurel immutable | Display seulement | Slot identity |
| `exercise_name_snapshot` | Structurel immutable | Display fallback | Nom prescrit fige |

**Niveau SESSION (table `workout_sessions`)**

| Champ | Nature | Visibilite UI | Role |
|-------|--------|---------------|------|
| `concentration` | Saisi optionnel | Standard (feedback bloc) | high/medium/low |
| `global_state` | Saisi optionnel | Standard | good/flat/fatigued |
| `bodyweight_kg` | Saisi optionnel | Standard | Poids corporel du jour |
| `free_note` | Saisi optionnel | Standard | Textarea 280 chars |
| `cardio_*` | Saisi optionnel (kind=cardio only) | Standard conditionnel | Duration, bpm, calories, machine |
| `status`, `started_at`, `ended_at`, `excluded_from_stats`, `template_*_snapshot`, `user_id` | Structurel | Affiches selectivement | State machine et identite |

### 3.2 Prevu vs Realise (vue synthetique)

```
PREVU (catalogue + template)
  WorkoutTemplate.name → TemplateExercise.name (prescrit)
                      → TemplateExercise.rep_targets (prescription)
                      → TemplateExercise.substitutes_json (substituts autorises)

  ↓ instanciation au create (immutable snapshot)

REALISE (session)
  WorkoutSession (immutable : template_slug_snapshot, template_name_snapshot)
    └── SessionExercise (immutable : exercise_code_snapshot, exercise_name_snapshot)
          ├── substituted_name : NULL si execute tel quel, sinon nom realise
          ├── success_score : derive apres save
          ├── muscle_sensation, free_note : saisis optionnels
          └── SetLog (actual data : weight_kg, reps, completed)
```

**Resolution prevu→realise** : via `app/services/substitution.actual_exercise_name(se)` = `substituted_name or exercise_name_snapshot`.

### 3.3 Visibilite UI standard (cible mobile)

**Par exercice (5 work sets) :**
- Set rows : 3 inputs × 5 = 15 inputs
- Exercice optionnel (collapsed/inline) : muscle_sensation (radio si deplie), free_note, substituted_name (radio si picker deplie)
- Exercice derive (affiche post-save) : success_score en recap

**Par session :**
- Feedback bloc : 3 radios (concentration), 3 radios (global_state), 1 input (bodyweight), 1 textarea (note), 1 bouton Enregistrer + 1 bouton Terminer/Rouvrir
- Cardio optionnel : 4 inputs supplementaires si kind=cardio

**Total standard :** ~17 inputs visibles par exercice + ~7 inputs par session.

---

## 4. Capacite du composant exercice cible

Le composant `<details class="card exercise-card">` peut porter **sans contradiction** :

| Capacite | Mecanisme | Reference |
|----------|-----------|-----------|
| Logging standard | Set rows (weight/reps/done) + muscle_sensation optionnel + free_note | Sx_02 FINAL §4 |
| Save intermediate | Bouton footer CTA `Enregistrer et passer a E{next}` → POST → 303 `?active={next_id}` | Sx_02 FINAL §7.1 |
| Save last | Bouton footer `Enregistrer et terminer` → POST → 303 `#session-feedback` | Sb_02.1 |
| action=end | Bouton `Terminer la seance` dans feedback session bloc → POST action=end → 303 `/done` | Sb_R3 |
| Reopen | Depuis `/done`, bouton `Rouvrir pour editer` → POST action=reopen → 303 editable | Sb_R3 |
| Substitution locale | Picker `<details>` bloc 4 du body, apres done-summary, avant last-time, radio group name=substituted_name | Sx_02 §11 + Sx_03 §5 |
| Affichage done | `<details>` collapsed, class `.exercise-card--done`, border ok, recap inline dans `<summary>` | Sx_02 §6.1 |
| Recap terminal | Page `/sessions/{id}/done` via `session_recap.build_recap()` | Sb_R3 |

**Zero contradiction UX.** Zero contradiction data. Les 8 capacites coexistent dans le meme composant sans conflit.

---

## 5. Lecture consolidee des surfaces de consommation

### 5.1 Surfaces existantes

| Surface | Lecture | Utilise actual_exercise_name ? | Utilise snapshots ? | Impact substitution | Statut |
|---------|---------|-------------------------------|---------------------|-------------------|--------|
| `/history` (liste sessions) | Session-level | Non | Oui (template_name_snapshot) | Neutre | Built |
| `/exercise-history/{slug}/{code}` | Slot-based | Partiel (affiche substituted_name) | Oui (filtre par code) | Visible via prefixe → (futur) | Built |
| `compute_progression_hint` | Slot-based | Non | Oui | Neutre (weight/reps peu importe substitute) | Built |
| `compute_delta` | Slot-based | Non | Oui | Biais possible si substitutes differents entre occurrences | Accepte |
| `last_time_by_exercise_code` | Slot-based | Non | Oui | Neutre | Built |
| `/sessions/{id}/done` recap | Realise | Via session_recap | Oui (exercise_name) | Prefixe → pour substitutes | Built |
| `/physique` dashboard | Realise (zones) | Oui (muscle_scoring) | Non | Classification correcte | Built |
| `/dashboard` (body engineering) | Realise (zones) | Oui (via muscle_scoring) | Non | Correct | Built |
| `/leaderboard` | Session quality | Non (via quality_score) | Neutre | Neutre | Built |
| `/squads/{id}` scoped lb | Session quality | Non | Neutre | Neutre | Built |
| Export JSON/CSV | Les deux | Oui (colonne substituted_name) | Oui | Complet | Built |
| Sharecards | Realise | Oui (sharing.py) | Non | Correct | Built |

### 5.2 Surfaces futures prevues

| Surface | Lecture cible | Pre-requis | Quand |
|---------|---------------|-----------|-------|
| Compare mode entre membres squad (S4) | Slot + realise affiches cote a cote | Design dedie | S4 roadmap |
| Dashboard axe "adherence prescription" | Slot via success_score agrege | Aucun (donnees existent) | Si feature requested |
| Dashboard axe "equilibre patterns" | Realise via motor_pattern | Taxonomie §3 Sx_03 FINAL | Defer Option 2 |
| Alertes desequilibre push/pull | Realise + taxonomie | Taxonomie §3 | Defer |
| Frequence de substitution par slot | Realise + substitution_reason | P3 Sx_03 | Arbitrage |

**Aucune surface existante n'a besoin de rework.** Toutes les surfaces futures sont cartographiees et dependent de triggers explicites.

---

## 6. Ecarts restants avant build

Etant donne que les 3 specs fondatrices sont integralement build, **les ecarts restants sont marginaux**. Liste exhaustive :

### 6.1 Champs DB presents mais hors UI (a maintenir ainsi)

| Champ | Statut | Action |
|-------|--------|--------|
| `set_logs.execution_quality` | Orphelin, NULL sur nouvelles sessions | **Ne rien faire**. Preserve pour compat historique + mode avance reactivable |
| `set_logs.reps_target` | Orphelin, NULL sur nouvelles sessions | **Ne rien faire**. Idem |

### 6.2 Services a creer / refactorer

| Service | Necessite | Priorite |
|---------|-----------|----------|
| Etendre `get_substitutes(te)` pour retourner `list[dict]` au lieu de `list[str]` | Si enrichissement niveaux inline (P4) | Basse (pas trigger) |
| Helper `get_substitute_level(te, name)` | Idem P4 | Basse |
| Helper `actual_substitution_reason(se)` | Si P3 ajoute substitution_reason | Basse |
| `exercise_catalog.py` CRUD canonique | Si Option 2 migration | Tres basse (2+ triggers requis) |
| **Aucun service immediatement necessaire** | — | — |

### 6.3 Routes / templates touches

**Aucun.** Les routes et templates actuels portent l'integralite du systeme specifie.

### 6.4 Risques de migration

**Zero migration DB obligatoire.** Les evolutions possibles sont toutes additives et declenchees par triggers :

| Scenario | Migration | Declencheur |
|----------|-----------|-------------|
| P3 `substitution_reason` enum | ALTER TABLE ADD COLUMN nullable | Arbitrage produit |
| P4 niveaux inline | Zero migration (JSON libre) | Remontee user |
| P5 Option 2 canonical entity | 2 tables + 2-3 FK + backfill | 2+ triggers Sx_03.1 |
| P6 taxonomie mouvement | Sur `exercises` canonique | Apres P5 |

### 6.5 Tests critiques a maintenir

Les tests existants couvrent deja les points critiques :
- `test_feedback.py` (11 tests) — algorithme compute_success_score
- `test_session_flow.py` — flow save → next
- `test_substitution.py` — lock, picker, persistance
- `test_session_done.py` + `test_session_recap.py` — terminal state
- `test_mobile_polish.py` — jump bar + CTA
- `test_past_session_readability.py` — summaries

**Tests manquants pour extensions futures :**
- Si P3 build : `test_substitution_reason_optional`, `test_substitution_reason_enum_validation`
- Si P4 build : `test_substitute_level_parsing`, `test_catalog_qa_rejects_out_of_scope`
- Si P5 build : suite complete `test_canonical_exercise_entity` + backfill

**Aucun test manquant bloquant aujourd'hui.**

---

## 7. Queue build finale

### 7.1 Statut des builds historiques

| Build | Statut reel | Reference |
|-------|-------------|-----------|
| **Sb_01_feedback_signal_refactor** | **BUILT** (success_score derive, orphelins retires UI, muscle_sensation `<details>`) | `compute_success_score` en prod |
| **Sb_02_mobile_session_flow_refactor** | **BUILT** (`<details>` focus, active_exercise_id, save → next, feedback en bas) | `session_detail.html` actuel |
| **Sb_02.1_mobile_ux_refinements** | **BUILT** (jump bar 4 etats, CTA contextuel, footer sticky) | Commit f0cab63 |
| **Sb_03_minimal_substitution_graph_build** | **BUILT** (substitutes_json, substituted_name, picker UI, actual_exercise_name, muscle_scoring cable) | `app/services/substitution.py` |
| **Sb_R3_session_terminal_state** | **BUILT** (route /done, session_recap, redirect auto completed, reopen) | Commit 2418ef8 |
| Sb_04_history_and_analytics_alignment | **ABSORBE dans Sb_03** | exercise_history affiche substituted_name, export inclut la colonne, QA script valide |

**Conclusion :** la queue historique Sb_01 → Sb_04 est **integralement close**. Le systeme exercice est en production.

### 7.2 Queue build residuelle (optionnelle)

| Build | Objectif | Perimetre | Priorite | Pre-requis |
|-------|----------|-----------|----------|-----------|
| **Sb_03.1_substitution_reason** | Ajouter enum optionnel pour capturer le pourquoi d'une substitution | 1 migration (ADD COLUMN), 1 service update, 1 template update (radio dans picker), 2-3 tests | P3 — **arbitrage produit** | Aucun |
| **Sb_03.2_equivalence_levels_inline** | Etendre substitutes JSON pour porter level (exact/approx/fallback) | Catalog JSON format + service get_substitutes + QA script rule | P4 — si remontee "delta bizarre" | Aucun |
| **Sb_O2_canonical_exercise_entity** | Migrer vers table `exercises` + FK | 2 tables, FK optionnelles, backfill ~97 exercices, resolution typos, suite tests | P5 — **SI 2+ triggers Sx_03.1** | Decision produit |
| **Sb_taxonomy_movement_v1** | Deployer 6 dimensions de taxonomie sur exercices canoniques | Requires Sb_O2 + revue catalogue + services pattern analytics | P6 | Sb_O2 build |

### 7.3 Details par build residuel

---

#### Sb_03.1 — Substitution Reason

**Objectif :** capter le pourquoi d'une substitution (machine occupee, blessure, preference...) pour gouvernance catalogue future.

**Perimetre :**
- Fichiers : `app/models/session.py` (+1 colonne), migration Alembic, `app/routers/sessions.py` (parsing), `app/services/substitution.py` (helper), `app/templates/session_detail.html` (radio group dans picker)
- Migration : `ALTER TABLE session_exercises ADD COLUMN substitution_reason VARCHAR(32) NULL;`
- Nouveau enum : `machine_busy | equipment_unavailable | injury | preference | other`

**Criteres d'acceptation :**
- Colonne ajoutee, nullable, valeurs enum controlees
- Radio group optionnel affiche dans picker (sous les options de nom)
- Save parse la valeur, stocke null si absent
- Export CSV/JSON inclut la colonne
- Tests : reason nullable, enum validation, display preserved when unsubstituted

**Risques :** tres faibles. Migration additive pure. Rollback : drop column.

**Tests strategie :** 2-3 tests unitaires + 1 test integration route. Aucune regression attendue sur consumers existants.

**Effort :** 1-2h.

---

#### Sb_03.2 — Equivalence Levels Inline

**Objectif :** enrichir le catalogue avec un niveau d'equivalence par relation de substitution.

**Perimetre :**
- Fichier : `data/reference_split.json` (changement de format)
- Transformation : `"substitutes": ["X", "Y"]` → `"substitutes": [{"name": "X", "level": "exact"}, {"name": "Y", "level": "approx"}]`
- Compatibilite ancien format : `get_substitutes()` accepte les deux formats, wrapper string → `{name, level: null}`
- QA script : rejet si level out_of_scope
- Template : badge discret sur l'option picker (optionnel)

**Migration DB :** aucune (`substitutes_json` est deja TEXT libre).

**Criteres d'acceptation :**
- Nouveau format accepte par le seed
- Ancien format reste accepte (retrocompat)
- QA script refuse level invalide
- Template affiche le niveau comme attribut ou tooltip discret
- Aucun consumer existant casse

**Risques :** faibles. Retrocompat assuree.

**Tests :** parse nouveau format, parse ancien, QA rejette out_of_scope.

**Effort :** 2-3h + revue catalogue (decider le niveau de chaque relation existante).

---

#### Sb_O2 — Canonical Exercise Entity

**Objectif :** introduire une table `exercises` canonique + FK pour robustesse referentielle.

**Perimetre :**
- 2 nouvelles tables : `exercises`, `exercise_substitutions`
- FK optionnelles : `template_exercises.exercise_id`, `session_exercises.prescribed_exercise_id`, `session_exercises.actual_exercise_id`
- Backfill : mapper ~97 exercices du catalogue vers entrees canoniques, resoudre typos
- Services : `exercise_catalog.py` CRUD + resolver, refactor `muscle_mapping.classify_exercise` pour utiliser FK
- Tests exhaustifs : backfill, resolution ambiguites, retrocompat snapshots

**Declencheur obligatoire :** **2+ triggers Sx_03.1 atteints** parmi :
1. >150 exercices OU >40 relations
2. >1 editeur catalogue
3. Requete cross-cutting emergente
4. Feature custom exercises
5. Bidirectional graph necessaire
6. Typos recurrents

**Criteres d'acceptation :**
- Toutes les sessions historiques resolvent correctement leur exercice canonique
- Aucune perte de snapshot (immutabilite preservee)
- Muscle scoring fonctionne via FK
- Analytics slot-based inchangees
- Tests full suite verts

**Risques :** eleves. Backfill ambigus, performances sur grosses sessions, compatibilite historique complexe.

**Effort :** 8-12h + revue catalogue + tests + deploiement progressif.

---

#### Sb_taxonomy_movement_v1 — Taxonomie de mouvement

**Objectif :** deployer les 6 dimensions V1 sur exercices canoniques pour alimenter analytics par pattern.

**Perimetre :**
- Pre-requis obligatoire : Sb_O2 build (canonical entity)
- Ajout de 6 colonnes sur `exercises` : primary_zone (existe indirect), secondary_zones, motor_pattern, compound_isolation, laterality, equipment
- Revue manuelle des ~97 exercices pour assigner toutes les valeurs
- QA script verifie completude
- Helpers analytics pattern-based

**Effort :** revue catalogue longue (2-4h) + code backend (3-5h) + tests (2h).

---

### 7.4 Decision de fusion / decoupage

| Question | Reponse |
|----------|---------|
| Faut-il fusionner Sb_03.1 et Sb_03.2 ? | **Non.** P3 (raison) adresse un signal de gouvernance, P4 (niveaux) adresse l'analytique. Deux besoins orthogonaux, declenches par triggers differents. |
| Faut-il decouper Sb_O2 ? | **Oui si arbitrage produit** : phase 1 creation tables + backfill + FK nullable sans consumer, phase 2 refactor services. Reduit risque. |
| Ajouter un sous-lot intermediaire ? | **Non.** Les builds historiques sont closes, les builds residuels sont chacun auto-consistant. Ne pas fragmenter inutilement. |

---

## 8. Recommandation finale executable

### 8.1 Position actuelle

**Systeme exercice SPIGNOS V2 : COMPLET ET BUILD.** Les 4 builds historiques (Sb_01 → Sb_04 equivalents) sont en production via Sb_01, Sb_02, Sb_02.1, Sb_03, Sb_R3. Zero dette de build structurelle.

### 8.2 Ordre exact recommande pour les builds residuels

```
Attente (pas de trigger actuel)
    │
    ├── [Optionnel arbitrage produit] Sb_03.1 substitution_reason ← peut etre lance immediatement
    │
    ├── [Si remontee "delta bizarre"] Sb_03.2 equivalence_levels_inline
    │
    ├── [Si 2+ triggers Sx_03.1] Sb_O2 canonical_exercise_entity
    │
    └── [Apres Sb_O2] Sb_taxonomy_movement_v1
```

### 8.3 Lot a lancer immediatement

**Aucun lot obligatoire.** Le systeme est mature et fonctionne.

Si une decision produit legere est souhaitee : **Sb_03.1** (substitution_reason) est le meilleur candidat.
- Cout : 1-2h
- Risque : tres faible
- Valeur : signal de gouvernance catalogue moyen terme
- Aucun pre-requis

### 8.4 Lot a differer

**Sb_O2** et **Sb_taxonomy_movement_v1** sont explicitement deferes jusqu'a triggers Sx_03.1 explicites. Les lancer sans trigger serait une erreur architecturale (over-engineering).

### 8.5 Points a figer avant tout code

Avant de lancer Sb_03.1 (si decide) :

1. **Decision produit sur l'enum reason :** confirmer les 5 valeurs (`machine_busy`, `equipment_unavailable`, `injury`, `preference`, `other`)
2. **Wording UI :** libelle du radio group dans le picker ("Raison (optionnel)" ?)
3. **Export CSV :** confirmer la position de la nouvelle colonne dans l'ordre du CSV (eviter de casser les consumers externes)
4. **Test coverage :** confirmer la creation de 2-3 nouveaux tests (`test_substitution_reason.py`)

Avant de lancer Sb_03.2 (si decide) :

1. **Revue catalogue :** assigner un niveau d'equivalence aux 9 relations existantes
2. **Wording UI :** decider si le niveau s'affiche en badge ou tooltip
3. **Format JSON :** valider le schema `{name, level}`

Avant de lancer Sb_O2 (si trigger atteint) :

1. **Verifier les 2+ triggers** documentes dans Sx_03.1 §5
2. **Alignement produit** : pourquoi maintenant ?
3. **Budget** : 8-12h + tests
4. **Plan de backfill** : comment resoudre les typos historiques (mapping manuel vs algo)
5. **Tests de non-regression** : suite complete doit passer

---

## 9. Definition of Done

| Critere | Statut |
|---------|--------|
| 3 specs consolidees sans ambiguite | ✓ (§1 tableau maitre + §3 modele unifie) |
| Arbitrages transversaux figes | ✓ (§2 matrice + §2.3 contradictions resolues) |
| Impacts techniques consolides identifies | ✓ (§6 ecarts marginaux + §7.3 details par build) |
| Queue build finale executable | ✓ (§7 statuts historiques + residuels) |
| Aucun conflit majeur implicite | ✓ (0 conflit detecte dans matrice §2) |
| Prochain sprint build evident | ✓ (§8.2 ordre + §8.3 recommandation) |

---

## 10. Synthese executive

**Systeme exercice SPIGNOS V2 — etat final :**

- **3 specs fondatrices closes** (Sx_01, Sx_02, Sx_03 FINAL) + Sx_04 consolidation
- **4 builds historiques integralement en production** (Sb_01, Sb_02, Sb_02.1, Sb_03, Sb_R3 + absorption Sb_04 dans Sb_03)
- **0 conflit** detecte dans la matrice croisee 3 specs
- **0 build obligatoire** residuel
- **4 builds optionnels** documentes avec triggers explicites (Sb_03.1, Sb_03.2, Sb_O2, Sb_taxonomy_movement_v1)

**Le systeme exercice est en maturite complete — documentaire, implementation, tests, analytics.**

Prochaine action possible : arbitrage produit sur Sb_03.1 (facultatif). Sinon, le systeme peut fonctionner indefiniment dans son etat actuel.
