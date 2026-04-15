# SPIGNOS Exercise System Consolidation Spec (Sx_04 — reconcilie)

**Sprint:** Sx_04_exercise_system_consolidation_spec
**Date:** 2026-04-14 (reecrit apres audit reel du code)
**Status:** Consolidated, reconciled with actual build state
**Supersedes:** version initiale de Sx_04 (ecrite sur hypotheses non verifiees — voir §12)

---

## 1. Purpose

Aligner les 4 chantiers du systeme exercice (Sx_01, Sx_02, Sx_02.1, Sx_03, Sx_03.1) avec la realite du code, verrouiller la grammaire transverse (slot-based vs exercise-based), et cadrer la build queue residuelle sans reouvrir de decisions deja tranchees.

Ce document remplace la version initiale de Sx_04 qui avait ete ecrite sur des hypotheses non verifiees (notamment `success_score` derive automatiquement — ce qui n'a jamais ete implemente, et n'est PAS la decision finale de Sx_01).

---

## 2. Etat reel au 2026-04-14

### Specs ecrites

| Spec | Fichier | Statut spec | Statut build | Remarque |
|------|---------|-------------|--------------|----------|
| Sx_01 — Feedback Rationalization | `SPIGNOS_EXERCISE_FEEDBACK_RATIONALIZATION.md` | Final (decisions A+B+A verrouillees) | **Partiellement built** | Voir §3 |
| Sx_02 — Mobile Exercise Entry UX | `SPIGNOS_MOBILE_EXERCISE_ENTRY_UX.md` | Historique, marque BUILT | **Built (Sb_02)** | Voir §3 |
| Sx_02.1 — Mobile UX Refinements | `SPIGNOS_MOBILE_EXERCISE_ENTRY_UX_REFINEMENTS.md` | Final | **Not built** | 3 gaps identifies |
| Sx_03 — Substitution Graph | `SPIGNOS_EXERCISE_SUBSTITUTION_GRAPH_SPEC.md` | Historique, marque BUILT | **Built (Sb_03)** | Voir §3 |
| Sx_03.1 — Substitution Strategic Refinements | `SPIGNOS_EXERCISE_SUBSTITUTION_GRAPH_REFINEMENTS.md` | Final | **Not built (par design — strategique)** | Triggers documentes pour Option 2 |
| Sx_04 — Consolidation (ce document) | `SPIGNOS_EXERCISE_SYSTEM_CONSOLIDATION_SPEC.md` | Final, reconcilie | — | — |

### Builds deja faits

- **Sb_02** (mobile flow refactor — `<details>` + active_exercise_id + feedback en bas) ✓
- **Sb_03** (substitution graph Option 1 — catalog JSON + substituted_name + actual_exercise_name helper) ✓
- **Sb_01 partiel** (execution_quality/reps_target masques du formulaire, muscle_sensation place dans `<details>`) ✓
- **Sb_01 residuel** : `success_score` n'est plus rendu comme input — deviation vs decision Sx_01 A (voir §3.1)

---

## 3. Reconciliation fine par spec

### 3.1 Sx_01 Feedback Rationalization — statut reel

| Decision Sx_01 | Attendu | Realite code | Statut |
|----------------|---------|--------------|--------|
| `execution_quality` + `reps_target` caches (decision B) | Wrappes dans `<details>Feedback avance</details>` | Non rendus du tout dans le formulaire | **Deviation** : plus radical que la decision (cache complet vs `<details>`) |
| `success_score` saisi manuellement visible (decision A) | Radio 100/80/50 dans le formulaire | Non rendu comme input. Affiche seulement en lecture (recap, history) | **Deviation** : le champ existe en DB et dans le router mais pas en UI d'entree |
| `muscle_sensation` visible et saisi (decision A) | Radio 3 valeurs visible par defaut | Dans un `<details>Sensation musculaire (optionnel)</details>` | **Deviation mineure** : optionnel plutot que visible |

**Arbitrage pour Sx_04 :**

Ces deviations ne cassent rien analytiquement (les colonnes existent, les consumers tolerent les nulls). Elles representent un choix UX plus agressif que ce que Sx_01 avait verrouille — moins d'inputs visibles, davantage de signal laisse en "optionnel" ou "non saisi".

**Decision transverse Sx_04 :**

Accepter la realite actuelle (aucune regression observee) mais **documenter explicitement** que :
- `success_score` existe toujours en DB et dans les consumers (kpis, quality_score, delta)
- Si `success_score` n'est jamais saisi, sa moyenne sera NULL et les KPIs/quality degradent proprement (le code gere deja les NULL)
- **Ne pas re-introduire le radio success_score dans le formulaire** tant que le user ne le demande pas — la simplification actuelle est un gain UX mesurable

Mettre a jour la spec Sx_01 en ajoutant un §13 "Deviations observees dans le build Sb_01" pour aligner la spec et le code.

### 3.2 Sx_02 Mobile Exercise Entry UX — reference historique

Build complet. Spec historique doit etre marque "BUILT (Sb_02)" avec pointeur vers Sx_02.1.

### 3.3 Sx_02.1 Refinements — build pending

3 gaps residuels a traiter en Sb_02.1 :
- Jump bar : 4 etats explicites (future/active/partial/done)
- CTA exercice : libelle contextuel (next code / bilan)
- CTA accessibility : footer renforce + sticky CSS cible

Prerequis : aucun. Independant des autres chantiers. Peut etre build en parallele de tout autre sprint.

### 3.4 Sx_03 Substitution Graph — reference historique

Build complet (Option 1 : JSON static + substituted_name field). Spec historique doit etre marque "BUILT (Sb_03)" avec pointeur vers Sx_03.1.

### 3.5 Sx_03.1 Refinements strategiques — pas de build obligatoire

Document strategique. Definit :
- Comparaison Option 1 vs Option 2 (13 dimensions, Option 1 gagne globalement tant que 0 trigger atteint)
- 3 gaps observables (identite fragile, raison non capturee, niveau d'equivalence non documente)
- 6 triggers concrets pour migrer vers Option 2 (aucun atteint aujourd'hui)
- Recommandation Sx_04 : NOT YET pour Option 2

**Decision Sx_04 consolidee :** Option 2 (canonical `Exercise` entity) est **deferee**. Reaffirme dans §6.

---

## 4. Principes transverses verrouilles

### 4.1 Slot-based vs exercise-based analytics

C'est le principe directeur qui reste intact et doit etre grave dans la grammaire du produit.

**Slot-based** — le point de vue "programme" :
- Identite : `(template_slug_snapshot, exercise_code_snapshot)`
- Consumers : `last_time_by_exercise_code`, `delta`, `progression_hint`, `exercise_history`
- Question repondue : "Comment j'ai progresse sur E2 de Push A ?"
- Insensibilite a la substitution : si le user substitue E2 "Chest Press" par "Developpe couche", le slot E2 reste E2 et son historique reste compare a lui-meme

**Exercise-based** — le point de vue "corps" :
- Identite : nom d'exercice reel (via `actual_exercise_name`)
- Consumers : `muscle_scoring`, `physique dashboard`, `export`
- Question repondue : "Quelles zones musculaires ai-je reellement sollicitees ?"
- Sensibilite a la substitution : la classification zone doit refleter ce qui a ete VRAIMENT fait

Les deux perspectives coexistent et chacune a sa colonne :
- `exercise_code_snapshot` + `exercise_name_snapshot` (prescrit, slot identity) → immutables, source des analytics slot-based
- `substituted_name` (reel, peut etre NULL) → source des analytics exercise-based via `actual_exercise_name()`

### 4.2 Identite catalogue : string-based, bornee par QA

Le catalogue reste gouverne par `reference_split.json`. L'identite des exercices est par nom de chaine, controlee par :
- Le QA script (`scripts/catalog_qa.py`) qui valide que chaque nom est classifiable
- La revue humaine avant bump de version
- Le versioning catalogue (`version: YYYY-MM-DD.vN`)

Pas de FK, pas de canonique, pas d'aliases. C'est un choix deliberatif qui tient tant que les 6 triggers de Sx_03.1 §5 ne sont pas atteints.

### 4.3 Signal primaire reduit

Post Sx_01 + observations build :

| Niveau | Champ | Saisie | Visibilite defaut | Statut DB |
|--------|-------|--------|-------------------|-----------|
| Set | weight_kg | Obligatoire (si done) | Visible | Non null si set complete |
| Set | reps | Obligatoire (si done) | Visible | Non null si set complete |
| Set | completed | Obligatoire | Visible | Non null |
| Set | execution_quality | Optionnel | **Non rendu** | Nullable, souvent NULL |
| Set | reps_target | Optionnel | **Non rendu** | Nullable, souvent NULL |
| Exercice | success_score | Non saisi (post-Sb_01) | **Non rendu en input** (affiche en recap) | Nullable, souvent NULL |
| Exercice | muscle_sensation | Optionnel | Dans `<details>` optionnel | Nullable |
| Exercice | free_note | Optionnel | Visible | Nullable |
| Session | concentration | Optionnel | Visible (feedback) | Nullable |
| Session | global_state | Optionnel | Visible (feedback) | Nullable |
| Session | bodyweight_kg | Optionnel | Visible (feedback) | Nullable |

**Consequence analytique a accepter :** les KPIs qui consomment `success_score` (kpis.avg_success_score, quality_score 40 pts, delta score_trend) vont degrader gracieusement avec NULL. Si aucun user ne saisit success_score, ces metriques ne fournissent pas de signal. C'est acceptable : le user a choisi l'UX ultra-minimale. Le signal est preserve via `completed` + `weight` + `reps` qui restent les donnees objectives de base.

### 4.4 Substitution comme choix utilisateur, pas comme bruit analytique

La substitution est un signal volontaire du user. Les consumers exercise-based (muscle_scoring) le refletent. Les consumers slot-based (delta, progression) l'ignorent. Les deux sont corrects.

Pas de penalite implicite sur les scores. Pas de flag "donnee degradee" en V1.

Si le user substitue systematiquement, le pattern sera detectable plus tard (gouvernance catalogue, pas ce sprint).

---

## 5. Interaction points entre specs (audit post-build)

### 5.1 Sx_01 × Sx_02 × Sx_02.1 : structure du formulaire exercice

Etat actuel :
- `<details>` par carte (Sx_02 ✓)
- Formulaire compact : weight/reps/completed par set + free_note (Sx_01 ✓)
- Pas de radio success_score, pas de `<details>` feedback avance pour eq/rt (deviation Sx_01 — acceptee §3.1)
- Sx_02.1 apportera : jump bar 4 etats, CTA contextuel, footer renforce — tout ceci n'impacte ni Sx_01 ni Sx_03

**Aucun conflit.**

### 5.2 Sx_02 × Sx_03 : substitution picker dans la carte

Position : le picker de substitution est deja dans le `<details>` de la carte exercice, rendu conditionnellement via `can_substitute()`. La compacite de la summary reste intacte (le picker est seulement dans le corps ouvert).

**Aucun conflit.** Sx_02.1 peut rafinir la jump bar et le footer sans toucher au picker.

### 5.3 Sx_01 × Sx_03 : interaction success_score / substitution

Non-problematique en realite actuelle : `success_score` n'est plus saisi, donc il n'y a pas de question "le score s'applique-t-il a l'exercice prescrit ou au substitue".

Si un jour `success_score` est re-introduit comme saisie (trigger exterieur), la decision doit etre : le score reflete l'exercice REELLEMENT fait (exercise-based), pas le slot. Coherent avec muscle_scoring.

### 5.4 Toutes × muscle_scoring + physique dashboard

Chaine post-build :
```
session_exercise
  → actual_exercise_name(se)  [Sb_03]
    → classify_exercise(name)  [muscle_mapping]
      → primary zone + secondary zones
        → zone_scores [muscle_scoring]
          → physique dashboard + body engineering dashboard
```

La substitution change la zone primaire quand pertinent (ex: Dips pecs vs Chest Press). Les deltas de mesures corporelles (chest_cm) restent fidelement associes a la zone. Pas de double comptage.

**Aucun bug de contamination analytique detecte.**

### 5.5 Sx_03 × Sx_03.1 : canonical entity

Les gaps Sx_03.1 (identite fragile, raison manquante, niveau d'equivalence) sont documentes. **Aucun n'est bloquant.** Triggers surveilles pour decision future.

Un build leger Sb_03.1 patch Gap 2 (ajout `session_exercises.substitution_reason` nullable) peut etre instruit a la demande mais n'est pas dans le perimetre obligatoire de Sx_04.

---

## 6. Decisions transverses de Sx_04

### Decision T1 — Option 1 (JSON-based substitution) est le modele permanent V2

Option 2 (canonical Exercise entity) est **deferee jusqu'a trigger**.

Triggers de re-evaluation (Sx_03.1 §5) :
- A : catalogue >150 exercices OU >40 relations de substitution
- B : >1 editeur du catalogue
- C : requete analytique cross-cutting emergente
- D : feature "custom exercises user"
- E : bidirectional graph necessaire
- F : typos/aliases devient un probleme recurrent

Regle : 0 trigger = ne pas migrer. 1 = analyser. 2+ = planifier la migration.

### Decision T2 — Slot-based et exercise-based sont deux grammaires coexistantes

Ne pas chercher a unifier. Chaque consumer documente explicitement laquelle il utilise. `actual_exercise_name()` est l'API officielle pour passer de l'une a l'autre.

### Decision T3 — Signal primaire reduit est acceptable

Le formulaire actuel (weight + reps + completed + free_note + muscle_sensation optionnel) est suffisant pour :
- Alimenter les analyses objectives (tonnage, completion rate, progression)
- Capturer la substitution
- Derogee : KPIs subjectifs (success_score, execution_quality) deviennent NULL-heavy

Pas de rollback. Pas de re-introduction de radios. Si un user expert veut saisir plus, il peut toujours remplir `muscle_sensation` en depliant le `<details>`.

### Decision T4 — Sx_04 ne declenche PAS de build supplementaire obligatoire

Les seuls builds pending identifies :
- **Sb_02.1** (Sx_02.1) — recommande, faible cout, forte valeur UX
- **Sb_03.1** (Sx_03.1 patch Gap 2) — optionnel, tres leger, valeur gouvernance moyen terme

Aucun autre build n'est rendu necessaire par Sx_04.

### Decision T5 — Documentation de reconciliation obligatoire

Marquer explicitement :
- `SPIGNOS_MOBILE_EXERCISE_ENTRY_UX.md` → header "BUILT (Sb_02), refinements in Sx_02.1"
- `SPIGNOS_EXERCISE_SUBSTITUTION_GRAPH_SPEC.md` → header "BUILT (Sb_03), strategic analysis in Sx_03.1"
- `SPIGNOS_EXERCISE_FEEDBACK_RATIONALIZATION.md` → ajouter §13 "Deviations observees dans Sb_01" (success_score non rendu, muscle_sensation en `<details>`, eq/rt non rendus)

Ces marquages assurent qu'un futur contributeur ne reouvre pas un debat deja tranche.

---

## 7. Build queue residuelle

### Sprints de build pending

| Sprint | Depends on | Scope | Priorite | Effort | Valeur |
|--------|-----------|-------|----------|--------|--------|
| **Sb_02.1** | Sx_02.1 | Jump bar 4 etats + CTA contextuel + footer sticky | **Haute** | 3-5h | UX quotidienne |
| **Sb_03.1** | Sx_03.1 | Patch Gap 2 (substitution_reason enum) | Moyenne | 1-2h | Gouvernance moyen terme |

### Sprints deferres explicitement

| Sprint | Trigger requis | Raison du defer |
|--------|----------------|-----------------|
| Canonical Exercise entity build | >= 2 triggers Sx_03.1 | Aucun trigger atteint |
| `compute_success_score()` derive | Besoin produit explicite | Actuellement acceptee comme NULL-heavy |
| Patch Gap 1 (slug-based identity) | QA signale typos recurrents | Aucune recurrence constatee |
| Patch Gap 3 (equivalence_level) | Besoin analytique confidence | Pas de consumer demandeur |
| Bidirectional substitution graph | Feature produit explicite | Pas d'usage actuel |

### Ordre recommande

```
Sb_02.1 (UX refinements)       ← peut etre fait des que possible
  |
  | (independance totale)
  |
Sb_03.1 (patch Gap 2 — optionnel)  ← a arbitrer, pas obligatoire
  |
  | (fin de la queue immediate)
  |
... surveillance des triggers Sx_03.1 ...
```

Pas d'autre sprint. Le systeme exercice V2 est a maturite.

---

## 8. Exposition analytique cible

Apres Sb_02.1 (et eventuellement Sb_03.1), le systeme exercice expose :

| Metrique | Source | Impacts sub |
|----------|--------|-------------|
| Tonnage par zone (30/60/90j) | Work sets × actual_exercise_name → zone | Oui |
| Hard sets par zone | Work sets × actual_exercise_name → zone | Oui |
| Completion rate | Work sets `completed` / total (slot-based) | Non |
| Quality score (0-100) | completed + success_score (nullable) + concentration + global_state | Partiel (degrade si success_score null) |
| Progression delta | First completed set current vs prior (slot-based) | Non |
| Last time | First completed set du meme slot | Non |
| Physique dashboard | zone_scores ponderes (performance + exposure + anthropometry) | Oui (via actual_exercise_name) |
| Body engineering dashboard (5 axes) | Compose : Consistency + Progression + Body trend + Recovery + Balance | Oui pour progression et balance |
| Exercise history detail | Per-slot history avec deltas ligne par ligne | Non (slot-based) |
| Export JSON/CSV | Tout incluant substituted_name | Oui |

---

## 9. Risques residuels au niveau systeme

| Risque | Probabilite | Impact | Action |
|--------|------------|--------|--------|
| success_score jamais saisi → quality_score se degrade a 60/100 max | Haute | Moyen | Accepter. Documenter. Ne pas reintroduire le radio. |
| Catalogue grossit sans gouvernance (arrivee de contributeurs) | Faible | Eleve | Surveiller trigger B. Reouvrir Option 2 si atteint. |
| Typo dans substitutes non catchee par QA script | Faible | Faible | QA script en place. Renforcement via Patch Gap 1 si recurrence. |
| Deviations Sb_01 non documentees creent confusion future | Moyenne | Moyen | **Decision T5 resoud** — documentation explicite des deviations. |
| Sb_02.1 pas build → friction mobile continue | Moyenne | Moyen | Prioriser Sb_02.1. |

---

## 10. Acceptance criteria — Spec Sx_04 (reconcilie)

- [x] Audit reel du code effectue (grep, lecture, verification des deviations)
- [x] Etat reel des 6 specs documente (tableau §2)
- [x] Deviations Sb_01 identifiees et arbitrees (§3.1)
- [x] 4 principes transverses verrouilles (§4)
- [x] 5 interaction points verifies sans conflit (§5)
- [x] 5 decisions transverses ecrites (§6)
- [x] Build queue residuelle claire et minimale (§7)
- [x] Decision T1 "canonical entity deferred" avec triggers explicites (§6 T1)
- [x] Corrections explicites vs version initiale de Sx_04 (§12)

---

## 11. Open questions pour V3 (hors perimetre V2)

1. Quand (et si) introduire `compute_success_score()` derive comme proxy objectif ? Pas avant un besoin produit identifie.
2. Quand (et si) introduire un scoring set-level qui exploite execution_quality et reps_target ? Non demande.
3. Quand (et si) migrer vers canonical Exercise entity ? Surveiller les 6 triggers Sx_03.1 §5.
4. Faut-il un "mode coach expert" qui re-expose success_score + eq/rt + muscle_sensation par defaut ? Si un segment d'utilisateurs experts le demande.

---

## 12. Corrections explicites vs version initiale de Sx_04

La version initiale de Sx_04 (date 2026-04-14, ecrite avant audit reel) contenait les imprecisions suivantes qui sont corrigees dans ce document :

| Imprecision initiale | Realite | Correction apportee |
|---------------------|---------|---------------------|
| "Sx_01 : success_score derived" | Aucune fonction `compute_success_score()` n'existe, et Sx_01 final (decision A) = "reste saisi manuellement" | §3.1 documente la deviation reelle : non rendu en UI, DB nullable, accepte tel quel |
| "Sx_02 : pending build (Sb_02)" | Sb_02 deja build | §2 met a jour le statut, §3.2 marque BUILT |
| "Sx_03 : pending build (Sb_03)" | Sb_03 deja build | §2 met a jour le statut, §3.4 marque BUILT |
| Build queue avec Sb_02, Sb_03, Sb_04 en pending | Tout sauf Sb_02.1 et Sb_03.1 potentiels est fait | §7 nouvelle queue minimale |
| Reference a `compute_success_score()` dans table SessionExercise | Fonction inexistante | Retiree, §4.3 donne le tableau reel du signal primaire |
| Pas de reference aux Sx_02.1 ni Sx_03.1 | Ces specs n'existaient pas au moment de la redaction initiale | §2 et §3 les integrent pleinement |
| Sb_04 "history and analytics alignment" pending | Travaux deja faits (exercise_history utilise actual_exercise_name, export inclut substituted_name, QA script valide) | Sb_04 retire de la queue, absorbe dans Sb_03 |

---

## 13. Conclusion

Le systeme exercice V2 de SPIGNOS est **a maturite**. La gouvernance transverse est claire :
- Un modele de catalogue JSON-based dont la robustesse est surveillee par QA + triggers explicites
- Deux grammaires analytiques (slot-based et exercise-based) qui coexistent proprement
- Un signal primaire minimaliste qui assume ses degradations gracieusement
- Une substitution utilisateur qui fonctionne sans bruit dans les analytiques

Les deux seuls builds residuels (Sb_02.1 recommande, Sb_03.1 optionnel) n'ajoutent aucun concept, seulement du polish UX et un signal de gouvernance.

**Aucune dette structurelle urgente ou non cadree.** Il reste une dette potentielle de canonisation (Option 2 : entite `Exercise` canonique), mais elle est desormais :
- documentee (Sx_03.1 §3)
- surveillee par 6 triggers explicites (Sx_03.1 §5)
- conditionnelle (aucune obligation de migrer tant que 0 trigger n'est atteint)

Ce n'est plus une zone floue — c'est une capacite future sous surveillance. Toute evolution est conditionnee a des declencheurs documentes, pas a une intention abstraite de "propreté".
