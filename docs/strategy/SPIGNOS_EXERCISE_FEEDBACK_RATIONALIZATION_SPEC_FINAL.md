# SPIGNOS Exercise Feedback Rationalization — Final Spec

**Sprint:** Sx_01_exercise_feedback_rationalization_spec (FINAL)
**Date:** 2026-04-14
**Status:** Final, reconcilie avec la realite du code apres audit exhaustif
**Supersedes:** `SPIGNOS_EXERCISE_FEEDBACK_RATIONALIZATION.md` §13 (deviations Sb_01) — integre ici comme etat canonique

---

## 0. Revision majeure vs versions precedentes

Mes audits precedents (Sx_01 initial + Sx_04) affirmaient que **`compute_success_score()` n'existait pas**. C'est **faux**. L'audit reel du code revele :

- `app/services/feedback.py:28` contient `compute_success_score(session_exercise, template_exercise) -> Optional[int]`
- `app/routers/sessions.py:408-409` l'appelle systematiquement dans le POST `update_exercise_card`
- `tests/test_feedback.py` valide l'algorithme (11 tests)
- `tests/test_session_flow.py:286`, `test_restore.py:264`, `test_export.py:88` verifient que `success_score ∈ {100, 80, 50}` **par derivation**

**Realite du build Sb_01 :** la decision implicite qui a ete prise est **B (derivation)**, pas A (saisie manuelle). Le formulaire ne contient plus de radio `success_score` parce que le champ est calcule cote serveur apres le save. Ce spec FINAL documente cette realite et la verrouille comme etat canonique.

---

## 1. Audit exhaustif des champs feedback — par niveau

### Niveau SET (`set_logs`)

| Champ | Type | Saisi/Derive | Semantique actuelle | Consumer(s) | Statut |
|-------|------|-------------|---------------------|-------------|--------|
| `weight_kg` | FLOAT nullable | **Saisi objectif** | Charge reelle utilisee sur le set | quality_score (indirect via success derived), delta, progression_hint, exercise_history, stats, export, sharing | **Primaire — doit rester saisi** |
| `reps` | INT nullable | **Saisi objectif** | Nombre de reps realises | Idem weight_kg + **feedback.py (pour derivation success_score)** | **Primaire — doit rester saisi** |
| `completed` | BOOL non-null | **Saisi objectif (checkbox)** | L'user a effectivement execute ce set | quality_score (work_completion 40pts), kpis (completion_rate_30d), stats, delta (first completed), progression_hint, leaderboard, feedback.py (filtre des scored sets), export | **Primaire — doit rester saisi** |
| `execution_quality` | STR nullable | Saisi optionnel | clean/acceptable/degraded au niveau set | **Export only** (`export_builder.py:68, 197`, `restore.py`) | **ORPHELIN — retirer de l'UI. Colonne DB preservee.** |
| `reps_target` | STR nullable | Saisi optionnel | target_hit/target_near/target_missed au niveau set | **Export only** (idem) | **ORPHELIN — retirer de l'UI. Colonne DB preservee.** |
| `technique` | STR nullable | Captured from catalog (RP, DS) | Technique d'intensite de la serie | Display, export | **Primaire — donnee catalogue, pas feedback** |
| `kind` | STR non-null | Structurel (warmup/work) | Discrimine warmup vs work | Tous les consumers qui filtrent les work sets | **Structurel — hors scope feedback** |
| `set_index` | INT non-null | Structurel (ordinal) | Numero de serie (scoped par kind) | Structurel + feedback.py (lookup rep_targets) | **Structurel** |

### Niveau EXERCICE (`session_exercises`)

| Champ | Type | Saisi/Derive | Semantique actuelle | Consumer(s) | Statut |
|-------|------|-------------|---------------------|-------------|--------|
| `success_score` | INT nullable | **DERIVE** par `compute_success_score()` | Score 100/80/50 snape depuis `(reps vs rep_targets) × completion_ratio` | **quality_score (40pts), kpis (avg_success_score_30d, template avg), delta (score_trend), stats (summarise), exercise_history, export, sharing, session_recap** | **Derive — ne plus saisir** |
| `muscle_sensation` | STR nullable | **Saisi optionnel** | strong/partial/weak — ressenti de ciblage musculaire | stats (display), exercise_history (display), export, session_recap | **Primaire — signal physiologique unique** |
| `free_note` | STR(140) nullable | Saisi optionnel | Texte libre | Display, export | **Primaire — libre** |
| `substituted_name` | STR(255) nullable | Saisi optionnel (Sx_03) | Nom de l'exercice reellement effectue | muscle_scoring (via actual_exercise_name), exercise_history, export, session_recap, sharing | **Primaire — signal de substitution** |
| `exercise_code_snapshot` | STR non-null | Structurel (immutable) | Slot prescrit (E1, E2...) | Slot-based analytics | **Structurel — immutable** |
| `exercise_name_snapshot` | STR non-null | Structurel (immutable) | Nom prescrit au moment de la creation | Display, history, fallback `actual_exercise_name` | **Structurel — immutable** |

### Niveau SESSION (`workout_sessions`)

| Champ | Type | Saisi/Derive | Semantique actuelle | Consumer(s) | Statut |
|-------|------|-------------|---------------------|-------------|--------|
| `concentration` | STR nullable | **Saisi optionnel** | high/medium/low — focus mental | quality_score (10pts), behavioral.py (fatigue), export | **Primaire — signal subjectif synthetique** |
| `global_state` | STR nullable | **Saisi optionnel** | good/flat/fatigued — etat general | quality_score (10pts), behavioral.py (fatigue), export | **Primaire — signal subjectif synthetique** |
| `bodyweight_kg` | FLOAT nullable | **Saisi optionnel** | Poids du corps ce jour | Timeline bodyweight, export | **Primaire — donnee corporelle** |
| `free_note` | STR(280) nullable | Saisi optionnel | Texte libre session | Display, export | **Primaire — libre** |
| `cardio_duration_min` / `cardio_bpm_avg` / `cardio_machine_calories` / `cardio_machine_type` | Mixed nullable | **Saisi optionnel (kind=cardio only)** | Donnees cardio | Session recap, export | **Primaire — scope cardio** |

---

## 2. Taxonomie cible du signal exercice

Le signal exercice se decompose en **3 axes orthogonaux**. Cette taxonomie sert de reference pour tout futur changement.

### Axe A — Performance mecanique (objective, set-level)

**Definition :** donnees physiques mesurables, sans subjectivite.

**Champs :**
- `weight_kg` (set)
- `reps` (set)
- `completed` (set)

**Caracteristique :** saisie directe au moment de l'execution. Zero interpretation. Un chronometre pourrait les capturer (theorique).

**Role :** base de calcul de TOUT le reste. Si ces champs sont absents, rien ne fonctionne analytiquement.

### Axe B — Qualite technique (derivee OU subjective, set/exercise-level)

**Definition :** evaluation de la qualite d'execution vs objectif prescrit.

**Champs :**
- `success_score` (exercice) — **DERIVE** de (Axe A + `rep_targets` du catalogue)
- `execution_quality` (set) — subjectif, **orphelin** (aucun consumer analytique)
- `reps_target` (set) — subjectif, **orphelin** (aucun consumer analytique)

**Caracteristique cible :** **derivee** chaque fois que possible, via l'algorithme documente dans `app/services/feedback.py`. L'auto-evaluation manuelle introduit un biais (tendance a se donner 100 par habitude) et duplique une info deja derivable.

**Role :** fournit le 40pts du quality score, l'avg_success_score_30d, le score_trend des deltas. Agrege pour representer "a quel point la prescription a ete respectee".

### Axe C — Ressenti physiologique / ciblage (subjectif, exercise/session-level)

**Definition :** perception corporelle et mentale — non-derivable, requiert la voix de l'utilisateur.

**Champs :**
- `muscle_sensation` (exercice) — strong/partial/weak — ressenti de ciblage musculaire
- `concentration` (session) — high/medium/low — focus mental global
- `global_state` (session) — good/flat/fatigued — etat physique general
- `free_note` (exercice/session) — texte libre

**Caracteristique :** **necessairement saisi**. Aucun algorithme ne peut derivate "je n'ai pas senti mon pec travailler" depuis les donnees objectives.

**Role :** alimente le quality score (20pts de concentration+global_state), le behavioral engine (fatigue), les futures correlations zone ↔ sensation (S2+), les alertes de sur-entrainement moyen terme.

---

## 3. Decisions finales verrouillees

### D1 — `success_score` est DERIVE

**Verrouille.** Le champ reste en DB (`session_exercises.success_score`), mais il est calcule automatiquement par `compute_success_score()` apres chaque save d'exercice. Le formulaire ne contient AUCUN radio pour ce champ.

**Algorithme** (documente dans `app/services/feedback.py`) :
```
Pour chaque set complete :
  score_set = 100 si reps >= max_reps
              80  si reps >= min_reps
              50  sinon
              80  si pas de target ou reps null (defaut prudent)
raw = mean(score_sets) × (completed/total_work_sets)
success_score = snap({100, 80, 50})
```

**Impact sur consumers :** INCHANGES. Tous les consumers lisent `se.success_score` tel quel, ne savent pas (et n'ont pas a savoir) qu'il est derive.

### D2 — `muscle_sensation` reste SAISI OPTIONNEL

**Verrouille.** Seul signal qui capture "est-ce que j'ai senti le muscle cible travailler". Non-derivable. Cout UX : 1 tap sur un `<details>` optionnel. Valeur produit : future correlation avec zone scoring.

### D3 — `execution_quality` + `reps_target` RETIRES DE L'UI

**Verrouille.** Colonnes DB preservees (pas de migration). Le formulaire ne les expose plus. Le router ne les parse plus. Tout nouveau log aura ces champs a NULL. Les exports continuent de les inclure (NULL pour nouvelles sessions, renseignes pour sessions historiques).

**Reversibilite :** reintroduire un `<details>Feedback avance</details>` dans le template + re-ajouter le parsing dans le router est un change de ~20 lignes. A ne faire que sous trigger produit explicite (aucun aujourd'hui).

### D4 — `concentration` + `global_state` + `bodyweight_kg` inchanges

Formulaire session feedback. Saisie optionnelle. Zero debat.

### D5 — `free_note` (exercice et session) inchanges

Saisie optionnelle libre. Non-analytique. Preserve.

---

## 4. Matrice des consumers impactes

### Par champ → ou il est lu / ecrit

| Champ | Producteurs (ecriture) | Consumers (lecture) |
|-------|----------------------|---------------------|
| `success_score` | `update_exercise_card` via `compute_success_score()` | `quality_score.compute_session_quality` (40pts), `kpis.compute_global_kpis` (avg_success_score_30d), `kpis.compute_template_kpis` (avg per template), `delta.compute_delta` (score_trend), `stats.summarise_current_exercise`, `stats.last_time_by_exercise_code`, `exercise_history.get_exercise_history`, `export_builder.build_json_payload/csv`, `sharing`, `session_recap.build_recap`, `restore.py` |
| `muscle_sensation` | `update_exercise_card` form parse | `stats.summarise_current_exercise`, `exercise_history` (display), `export_builder`, `session_recap`, `restore.py` |
| `execution_quality` | **aucun en nouvelle session** | `export_builder`, `restore.py` (historiques seulement) |
| `reps_target` | **aucun en nouvelle session** | `export_builder`, `restore.py` (historiques seulement) |
| `completed` | `update_exercise_card` form parse | `quality_score` (40pts), `kpis.compute_global_kpis` (completion_rate, work_sets_done), `stats` (filtre), `delta` (first completed), `progression_hint` (prior first set), `leaderboard` (via quality_score), `feedback.compute_success_score` (filtre), `export_builder` |
| `weight_kg` | form parse | `delta`, `progression_hint`, `exercise_history`, `stats`, `export_builder`, `session_recap`, `sharing` |
| `reps` | form parse | `delta`, `progression_hint`, `exercise_history`, `stats`, `export_builder`, `session_recap`, `sharing`, **`feedback.compute_success_score`** (critique) |
| `concentration` | `update_session` form parse | `quality_score` (10pts), `behavioral.compute_session_fatigue`, `export_builder`, `session_recap` |
| `global_state` | `update_session` form parse | `quality_score` (10pts), `behavioral.compute_session_fatigue`, `export_builder`, `session_recap` |

### Par service → champs lus et impact si le champ bouge

| Service | Champs lus | Impact si champ feedback change |
|---------|-----------|--------------------------------|
| `app/services/feedback.py` | `reps`, `completed`, `rep_targets` (catalog) | CRITIQUE : c'est le producteur de `success_score` |
| `app/services/quality_score.py` | `completed`, `success_score`, `concentration`, `global_state` | Consomme 4 des 7 champs primaires |
| `app/services/kpis.py` | `success_score`, `completed` | Aggregate 30j, template avg |
| `app/services/delta.py` | `weight_kg`, `reps`, `success_score` | Delta tri-dimensionnel |
| `app/services/stats.py` | `success_score`, `muscle_sensation`, `completed`, `weight_kg`, `reps` | Summaries inline |
| `app/services/exercise_history.py` | `success_score`, `muscle_sensation`, `weight_kg`, `reps`, `completed` | Listing historique |
| `app/services/progression_hint.py` | `weight_kg`, `reps`, `completed`, `rep_targets` | Hint mechanique |
| `app/services/behavioral.py` | `concentration`, `global_state` | Fatigue/readiness |
| `app/services/session_recap.py` | `success_score`, `muscle_sensation`, `substituted_name`, `weight_kg`, `reps`, `completed`, `concentration`, `global_state`, `bodyweight_kg` | Surface terminale /done |
| `app/services/export_builder.py` | **TOUS** les champs | Preserve tout y compris orphelins |
| `app/services/leaderboard.py` | Via `quality_score` | Ranking scope global + squad |
| `app/services/sharing.py` | `weight_kg`, `reps`, `success_score`, via `actual_exercise_name` | Sharecards |

---

## 5. Compatibilite historique

### Principe directeur

**Les snapshots sont immutables.** `session_exercises.exercise_code_snapshot`, `exercise_name_snapshot`, `template_slug_snapshot`, `template_name_snapshot` ne sont jamais modifies. Les `set_logs` ne sont jamais modifies retroactivement (sauf le user qui reouvre via `action=reopen` et re-sauvegarde).

### Traitement des champs orphelins en historique

- Les sessions anterieures a Sb_01 peuvent avoir `execution_quality` et `reps_target` remplis. Ces valeurs sont **preservees** (pas de migration destructive).
- Les exports JSON/CSV continuent d'inclure ces colonnes. Les nouvelles sessions y auront NULL, les anciennes auront les valeurs saisies a l'epoque.

### Traitement de `success_score` sur historique

- Les sessions anterieures a Sb_01 peuvent avoir un `success_score` saisi manuellement (qui ne passera pas par `compute_success_score`).
- Ces valeurs sont **preservees telles quelles**.
- Les sessions post-Sb_01 ont un `success_score` derive (100/80/50).
- Les deux coexistent dans la meme table — aucun consumer ne distingue.

### Traitement du re-save (action=reopen → re-save)

- Si un user reouvre une session anterieure a Sb_01 et clique de nouveau sur un exercice, le save recalcule `success_score` via `compute_success_score()`. La valeur manuelle historique est ECRASEE.
- Comportement accepte : c'est la consequence d'une edition volontaire. Si le user ne touche pas, rien ne change.

### Pas de migration

**Zero migration DB.** Toutes les decisions D1-D5 sont applicables sur le schema existant.

---

## 6. Impacts sur les grandes surfaces produit

### 6.1 Scoring (`quality_score`, `kpis`)

**Impact D1 (success_score derive) :**
- `avg_success_score_30d` devient systematiquement renseigne sur nouvelles sessions (plus jamais NULL si au moins un set est complete)
- Consequence : moins de cas NULL dans la page progress, les KPIs sont plus stables
- Le quality_score 40pts est systematiquement calculable

**Pas de regression :** les formules ne changent pas, seule la source de la valeur change.

### 6.2 Historique (`exercise_history`, pages /history)

**Aucun changement visible.** La colonne `success_score` s'affiche normalement. Les valeurs historiques manuelles et les nouvelles valeurs derivees coexistent sans incident.

**Remarque cognitive :** sur des sessions tres recentes, l'user pourrait etre surpris que "son" score soit 80 alors qu'il aurait donne 100 subjectivement. Le wording UI dans `/done` et `/history` doit rester neutre (ne pas suggerer "ton score de satisfaction"). Etat actuel : neutre ("score 80"), OK.

### 6.3 Progression (`delta`, `progression_hint`)

**Delta.score_trend :** devient plus stable car les deux cotes (current et prior) ont un `success_score` derive comparable. Moins de "None" dans les deltas recents.

**progression_hint :** ne consomme pas `success_score`. Zero impact.

### 6.4 Exports (`export_builder`)

**Aucun changement de schema CSV/JSON.** Les colonnes orphelines sont preservees pour compatibilite. Les consumers externes (si un user utilise l'export pour analyse personnelle) ne cassent pas.

### 6.5 Dashboards futurs (body engineering, physique)

**Aucun impact direct.** Les dashboards consomment zone_scores et tonnage. `success_score` n'y apparait qu'indirectement via le quality_score qui nourrit les behavioral signals.

**Opportunite future :** maintenant que `success_score` est deterministe, on peut construire un axe "adherence a la prescription" dans le body engineering dashboard (agrege des success_score par zone). Hors scope de ce spec.

### 6.6 Future UX mobile du bloc exercice (Sx_02 et au-dela)

**Consequence directe :** le formulaire exercice expose uniquement :
- Pour chaque set : `weight`, `reps`, `completed` (3 inputs)
- Pour l'exercice : `muscle_sensation` (optionnel dans `<details>`), `free_note`, substitution si applicable
- Pour la session : `concentration`, `global_state`, `bodyweight_kg`, `free_note`

**Inputs par exercice (5 work sets) :** 15 (sets) + 2 (exercice optionnels) = **17 max**, realistement 15 si l'user skippe les optionnels.

**Avant Sb_01 :** 27 inputs.

**Gain mesurable :** -37% d'inputs. Coherent avec l'hypothese Sx_02.1 (flux mobile focus-exercice compact).

**Effet de bord positif :** la suppression de l'input `success_score` rend la carte exercice beaucoup plus "tactique" (que fait-on ?) et moins "reflective" (comment ca s'est passe ?). Le reflectif est deporte en fin de seance (feedback session) et en re-lecture sur /done.

---

## 7. Risques et mitigations

| Risque | Probabilite | Impact | Mitigation |
|--------|------------|--------|------------|
| `rep_targets` manquants sur un exercice (catalogue incomplete) | Faible | Moyen | `compute_success_score` retourne 80 par defaut. Non-bloquant. |
| User se plaint de "son score change sans qu'il ait touche" | Moyenne | Faible | Le score ne bouge que si l'user re-save. Wording neutre dans l'UI. |
| Historique avec success_score manuel vs derive genere confusion analytique | Faible | Faible | Les valeurs coexistent dans un range borne {100, 80, 50}. Moyennes restent coherentes. |
| Perte de signal subjectif fin (orphelins) | Deja acte | Negligeable | Colonnes DB preservees, mode feedback avance reactivable |
| Consumer tierce (export utilise par outil externe) voit des colonnes vides | Moyenne | Faible | Documenter explicitement dans le changelog export |

---

## 8. Definition of Done (reponse aux criteres)

| Critere | Statut |
|---------|--------|
| Doublons demontres ou refutes | ✓ (§1 : execution_quality/reps_target orphelins, success_score derivable) |
| Primary vs derived tranche | ✓ (§2 taxonomie 3 axes + §3 decisions D1-D5) |
| Modele cible lisible | ✓ (§2 + §6.6) |
| Impacts consumers documentes | ✓ (§4 matrice bidirectionnelle) |
| Compatibilite historique traitee | ✓ (§5 — zero migration, snapshots immutables, coexistence) |
| Base prete pour Sx_02 UX mobile | ✓ (§6.6 : 17 inputs max par exercice, liste precise des champs visibles) |

---

## 9. Recommandations ordonnees pour le futur build

Aucun build obligatoire par ce spec (le build Sb_01 implementant D1-D5 est deja en production). Les recommandations suivantes sont pour les sprints futurs, ordonnees par priorite :

### P1 — Sx_02 UX mobile (next)

**Conditionnement :** Sx_02 peut designer le flux focus-exercice en s'appuyant sur le tableau §6.6 comme source de verite UI. Aucun autre champ a prevoir.

**Ce que Sx_02 n'a PAS a refaire :**
- Question "faut-il afficher success_score ?" → NON (derive)
- Question "faut-il afficher execution_quality/reps_target ?" → NON (orphelins)
- Question "ou mettre muscle_sensation ?" → `<details>` optionnel, position deja validee

### P2 — Axe "adherence a la prescription" dans body engineering dashboard

**Quand :** apres N sessions avec success_score derive stable (au moins 3 mois de donnees propres post-Sb_01).

**Quoi :** un 6e axe potentiel dans le dashboard Sx_04 : "adherence" = agregat des success_score des zones actives. Complete Progression (tonnage) et Consistency (frequence) avec "qualite d'execution vs prescription".

**Pre-requis :** aucun, les donnees existent deja.

### P3 — Wording UI neutre pour success_score

**Quand :** si un user remonte de la confusion ("j'ai donne tout, pourquoi c'est 80 ?").

**Quoi :** ajouter une legende discrete ("derive des reps vs cible") dans `/done` et `/history` pour disperser l'ambiguite.

**Effort :** 10 minutes.

### P4 — Mode feedback avance reactivable

**Quand :** uniquement si un segment d'users experts demande explicitement execution_quality/reps_target pour leur analyse personnelle.

**Quoi :** reintroduire un `<details>Feedback avance</details>` dans le template + parsing router. ~20 lignes.

**Par defaut :** ne PAS faire sans trigger.

### P5 — Cleanup orphelins (long terme)

**Quand :** si le catalogue depasse des seuils de gouvernance (voir triggers Sx_03.1).

**Quoi :** decider si on supprime definitivement les colonnes orphelines (migration DESTRUCTIVE) ou si on conserve. Default : conserver. Migration drop a ne jamais faire legerement.

---

## 10. Synthese executive

**Signal exercice SPIGNOS post-Sb_01 :**

- **3 axes orthogonaux** (performance mecanique, qualite technique, ressenti)
- **7 champs primaires** (weight, reps, completed, muscle_sensation, concentration, global_state, bodyweight)
- **1 champ derive** (success_score)
- **2 champs orphelins preserves** (execution_quality, reps_target)
- **Zero doublon actif** dans le flow de saisie
- **17 inputs max** par exercice de 5 work sets (vs 27 avant Sb_01)
- **Zero migration DB** necessaire pour aligner le modele cible

**Le signal est minimaliste, deterministe ou necessairement subjectif, et pret pour les chantiers suivants.**
