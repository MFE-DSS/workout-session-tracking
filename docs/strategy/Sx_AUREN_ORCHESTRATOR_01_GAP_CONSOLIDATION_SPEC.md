# Sx_AUREN_ORCHESTRATOR_01 — Gap Consolidation & Orchestrator Roadmap (SPEC)

**Statut :** SPEC ONLY (docs-only, 0 code, 0 migration) · **Base canonique :** `8d9631c`
**Objet :** produire la **feuille de route canonique pilotée par les manques** qui fait d'AUREN un
**orchestrateur d'entraînement personnel déterministe et conscient de la biomécanique**.
**Ce document ne réécrit aucune roadmap ancienne** : il **réconcilie** l'existant réellement livré,
le blueprint opérateur, et les manques restants.

> **Méthode.** Chaque classification ci-dessous provient d'un **audit du code actif** (4 explorations
> parallèles en lecture seule sur la canonique), pas de la lecture des anciens rapports. Les
> affirmations portent une preuve `fichier:ligne`. Là où un rapport ancien et le code se
> contredisent, **le code fait foi** et la contradiction est signalée.

---

## 0. Résumé exécutif — les 6 constats qui structurent la roadmap

1. **La fondation biomécanique existe mais n'est pas la source de vérité.** `BodyZone` /
   `ExerciseMuscleMapping` ne sont atteints que par **un unique chemin d'intégration DB, étroit** —
   le lecteur `app/services/body_map_descriptor.py` (`:56` pour `ExerciseMuscleMapping`, `:75` pour
   `BodyZone`), servant la seule body-map de la carte de séance et emprunté depuis plusieurs points
   d'appel/fournisseurs (`app/routers/sessions.py:341`). **12+ consommateurs lourds**
   (recommandation, scoring, coach, Body Intelligence, radar) utilisent encore la **classification
   par sous-chaîne** (`app/services/muscle_mapping.py:109-120`) ou un JSON.
   ⇒ **`Sb_32.4` reste une fondation bloquante.**
2. **Deux défauts vivants et visibles par l'utilisateur ont été découverts pendant l'audit**
   (non listés dans le blueprint) — voir §C.0. Ils sont peu coûteux et devancent la fondation.
3. **Readiness / fatigue / récupération / disponibilité sont fragmentés** : **5 calculs
   indépendants, 6+ échelles**, **une seule** arête d'intégration inter-modules, et elle est
   *fail-open*. ⇒ un **contrat sémantique unique** est nécessaire (conception seulement, ici).
4. **Le cardio est une île de données** : capturé, exporté, affiché — et **explicitement exclu** du
   modèle de récupération (`app/services/recommendation.py:352-355`).
5. **Le moteur de morphologie est orphelin** : `morphology_profile.py` / `slot_intent.py` /
   `morpho_program_generator.py` n'ont **aucune accessibilité depuis un routeur**. La morphologie est
   **fixture de test uniquement** ; `wingspan_cm` n'existe **nulle part** hors du module pur.
6. **Contrainte d'architecture permanente** : `recommendation.py` et le cœur de scoring **ne doivent
   pas être modifiés** (motif « wrapper externe », précédent `recommendation_explainer.py`). Cette
   règle **contraint la conception** de tout ce qui touche à la planification et à la récupération.

---

## A. CURRENT CAPABILITY MAP

Légende : **DELIVERED** · **LEGACY/SPLIT-SoT** (livré mais source de vérité éclatée ou doublée) ·
**PARTIAL** · **MISSING** · **DEFERRED** (décision opérateur) · **REJECTED** (non scientifique).

### A.1 Chaîne produit cible, état réel

| # | Capacité de la chaîne AUREN | État | Preuve (code actif) |
|---|---|---|---|
| 1 | **Body facts** (capture) | **PARTIAL** | `POST /profile/measurements` 10 champs `app/routers/auth_routes.py:505` ; `POST /body/measurements` 12 champs **gated OFF** `app/routers/body.py:86` + `app/config.py:86` ; **2 écrivains ungated/gated aux champs divergents** |
| 2 | **Morphology descriptors** | **DELIVERED (pur) / MISSING (runtime)** | `app/services/morphology_profile.py:403` pur, docstring `:23-25` « ne lit ni n'écrit BodyMeasurement » ; **aucun routeur** ne l'appelle ; `wingspan_cm` absent de tout modèle |
| 3 | **Training priorities** | **PARTIAL** | vocabulaire fermé `morphology_profile.FOCUS_CANDIDATE_VOCAB` ; **aucune surface** de déclaration utilisateur |
| 4 | **SlotIntents** | **DELIVERED** | `app/services/slot_intent.py` (8 intentions, registre) |
| 5 | **Exercise candidates** | **DELIVERED** | `app/services/morpho_program_generator.py` (couplage biparti maximum, no-fabrication) |
| 6 | **Weekly volume budget** | **MISSING** | `ZONE_VOLUME_TARGET` existe (`muscle_mapping.py:52-64`) mais **aucun budget hebdomadaire ajustable** ni consommateur |
| 7 | **Weekly plan** | **MISSING** | aucun planificateur ; `Sb_27.3` a explicitement tranché **pas de route `/weekly`** |
| 8 | **Today recommendation** | **DELIVERED (mais modèle propre)** | `app/services/recommendation.py` + wrapper `recommendation_explainer.py` |
| 9 | **Session execution** | **DELIVERED / CLOSED** | `Sx_UI_04` closeout ; `app/routers/sessions.py:380-420` |
| 10 | **Substitution** | **DELIVERED / CLOSED** | `app/services/substitution.py`, invariants N1/N2/N3 en code `:193-243` |
| 11 | **Feedback / logging** | **DELIVERED / CLOSED** | `Sx_FB_01` VERIFIED |
| 12 | **Overload** | **DELIVERED / CLOSED** | `app/services/overload_engine.py`, garde substitution `overload_inputs.py:258-264` |
| 13 | **Recovery estimate** | **PARTIAL / FRAGMENTÉ** | 3 modèles disjoints — voir §C.2 |
| 14 | **Adaptive replanning** | **MISSING** | aucun replanificateur |
| 15 | **Body Intelligence / explication** | **DELIVERED (code) / DEFERRED (activation)** | `app/routers/body_intelligence.py:101` ; flag `body_intelligence_enabled` défaut **False** `app/config.py:95` |

### A.2 Fondations transverses

| Fondation | État | Preuve |
|---|---|---|
| Moteur de substitution | **DELIVERED / CLOSED** | API publique stable, lecture seule `substitution.py:380-382` |
| Rationale de suggestion N1/N3 | **PARTIAL** | seul **N2** porte un `rationale` ; `substitution.py:238` et `:243` renvoient `None` |
| Raison de substitution **utilisateur** | **MISSING** | `substitution_reason` : **0 occurrence** dans `app/`, `migrations/`, `tests/` |
| `exercise_properties.json` (scoring) | **DELIVERED** | 69 entrées, validé au chargement `substitution.py:143-149` |
| `exercise_knowledge_base.json` (catalogue) | **PARTIAL** | `_counts` = 103 total / **36 gaps** / **12 blackholes** ; **4 sous-scores qualité non calculables** `program_quality_engine.py:52-57` |
| `BodyZone` / `ExerciseMuscleMapping` | **LEGACY/SPLIT-SoT** | tables peuplées **par migration uniquement** ; **un unique chemin d'intégration DB étroit** (lecteur `body_map_descriptor`, plusieurs points d'appel) |
| Cycle Custom Program (draft→publish→launch) | **DELIVERED / CLOSED** | `PUBLICATION_01→04` mergés |
| Export / backup | **PARTIAL** | sessions seules `export_builder.py:100-126` ; export body **gated OFF** ; **restore CLI-only** |
| Auren UI transformation | **CLOSED** (rebrand légal ouvert) | `Sx_UI_10` closeout ; interne « SPIGNOS » subsiste |

---

## B. TARGET ORCHESTRATOR ARCHITECTURE

### B.1 Principe directeur

> **La couche agentique propose et explique. Les services déterministes détiennent l'état du
> programme et toutes les mutations.** Aucune écriture n'est jamais décidée par un modèle.

### B.2 Chaîne cible (couches, pas modules)

```
[Capture]        body facts · préférences · availability · readiness quotidienne
      ↓ (adapters, déterministes)
[Interprétation] MorphologyProfile (FACT/INFERENCE + confiance bornée)
      ↓
[Priorisation]   TrainingPriorities (vocabulaire fermé, borné, révocable)
      ↓
[Intention]      SlotIntent (taxonomie existante)
      ↓
[Sélection]      candidats EKB (compute_proximity, lecture seule)
      ↓
[Budget]         WeeklyVolumeBudget — PLAGE ajustable par zone, jamais une « vérité »
      ↓
[Plan]           WeeklyPlan (proposition déterministe, non contraignante)
      ↓
[Aujourd'hui]    Today recommendation  ← recommendation.py EXISTANT (non modifié) + wrapper
      ↓
[Exécution]      session focus · substitution · logging   ← TOUS EXISTANTS, CLOS
      ↓
[Adaptation]     overload (existant) · RecoveryEstimate (nouveau, ESTIMATION)
      ↓
[Explication]    Body Intelligence · Orchestrator Explainer
```

### B.3 Le contrat sémantique unique (conception seulement — **rien n'est implémenté ici**)

L'audit prouve la fragmentation (§C.2). La cible est **un seul contrat**, `Sx_RECOVERY_READINESS_01` :

- **`ReadinessSignal`** — état déclaré du jour (subjectif, 1–5, source `readiness_entries`).
- **`FatigueSignal`** — charge accumulée dérivée (sessions récentes, force **et** cardio).
- **`ZoneRecoveryEstimate`** — **ESTIMATION** par zone, `0.0–1.0` + `confidence` + `basis`,
  **jamais** un pourcentage physiologique mesuré.
- **Règle d'échelle unique** : toute valeur normalisée est `0.0–1.0`, croissante = « plus
  disponible ». Toute conversion est explicite et testée. *(La collision d'échelle actuelle §C.0-B
  est exactement le défaut que cette règle interdit.)*
- **Règle de dégradation** : une entrée manquante donne `confidence: "insufficient"` et un
  comportement **neutre explicite** — **jamais** un *fail-open* silencieux vers « frais »
  (défaut actuel `recommendation.py:403-406`).

**Contrainte majeure de conception** : `recommendation.py` **ne peut pas être modifié**. Le contrat
est donc introduit comme **service neuf** ; `recommendation.py` conserve son modèle interne jusqu'à
une migration **explicitement autorisée à part**. Le contrat s'expose d'abord aux **nouveaux**
consommateurs (planificateur, replanification, explainer) et au **wrapper** existant.

---

## C. GAP MATRIX

### C.0 Défauts vivants découverts par l'audit (hors blueprint — additions justifiées)

| ID | Défaut | Preuve | Impact utilisateur | Sévérité |
|---|---|---|---|---|
| **C.0-A** | `_zone_session_counts` initialise les **6 axes MACRO** puis les remplit avec des **11 zones DÉTAILLÉES**, filtrées par `if z in counts` → **seul `pecs` peut jamais être compté** | `app/services/profile_metrics.py:201` vs `:205` + `:213` | `coach_inference` « zone travaillée / peu travaillée » et le radar Body Intelligence sont **structurellement faux** | 🔴 haute |
| **C.0-B** | `fatigue_score` produit en **0–100** (`behavioral.py`) est lu avec des seuils **0–1** (`>= 0.7`) | `recommendation.py:894` vs `recommendation_explainer.py:162-171` | « Niveau de fatigue élevé — séance légère privilégiée » est émis **quasiment toujours** (défaut neutre = 50.0) ; la branche « bon moment pour pousser » est **inatteignable** ; **les tests pinnent la mauvaise échelle** | 🔴 haute |

Ces deux défauts sont **peu coûteux**, **isolés**, et **user-visible**. Ils sont placés en **P0**,
**avant** la fondation `Sb_32.4` (qui est le sprint le plus risqué du cycle) — corriger un mensonge
affiché ne doit pas attendre une refonte.

### C.1 Fondation biomécanique

| Question | Réponse prouvée |
|---|---|
| `BodyZone`/`ExerciseMuscleMapping` sont-ils la source de vérité ? | **NON.** Chemin DB **opt-in** : `muscle_mapping.py:181` n'interroge la base que si `db` **et** `exercise_code` sont fournis. **Un seul chemin d'intégration** les fournit — le lecteur `body_map_descriptor.py` (`:56` mapping, `:75` `BodyZone`), atteint depuis `sessions.py:341` ; aucune autre surface n'emprunte ce chemin. |
| Qui utilise encore la sous-chaîne ? | `recommendation.py:181,362` · `muscle_scoring.py:89,151,166` · `profile_metrics.py:205` · `session_recap.py:126` · `coach_report.py:184` (indirect) · `body_intelligence_inputs.py:129` (indirect) · `scripts/catalog_qa.py:212` |
| Qui utilise un JSON parallèle ? | `program_quality_engine.py` (EKB détaillé) · `morpho_program_generator.py` + `slot_intent.py` (`exercise_properties` macro) |
| Les erreurs connues sont-elles corrigées ? | **Non, elles sont figées** : `Rear delt fly machine (pec deck inversé)` → `pecs` et `Relevé de jambes suspendu` → `calves` sont **backfillés tels quels** dans `migrations/…20260708_add_exercise_muscle_mapping.py:92-94` **et** dans l'EKB |
| Combien de taxonomies de zones coexistent ? | **≥ 5** copies vivantes + vocabulaires EKB (`7` macro EKB vs `6` `RADAR_AXES`) |
| Risque de peuplement | `create_all()` (`app/database.py:98-111`) peut créer les tables **avant** Alembic → backfill **définitivement sauté** (`…bodyzone_muscle_tables.py:120`) |

⇒ **`Sb_32.4` est retenue comme fondation bloquante**, conformément à la consigne.

### C.2 Fragmentation readiness / fatigue / récupération / disponibilité — **VERDICT : FRAGMENTÉ**

| Concept | Module propriétaire | Échelle | Persisté | Consommateurs décisionnels |
|---|---|---|---|---|
| Readiness déclarée (jour) | `readiness.py` | **1–5 int** | ✅ `readiness_entries` | **AUCUN** |
| Readiness comportementale | `behavioral.py:68` | **0–100 float** | ❌ | affichage seulement |
| Fatigue comportementale | `behavioral.py:42-58` | **0–100 float** | ❌ | `recommendation` (seule arête) |
| Disponibilité par zone | `recommendation.py:384-396` | **0.0–1.0 ratio** | ❌ | scoring interne |
| Axe récupération dashboard | `dashboard.py:343` | **0–100 float** | ❌ | dashboard |
| `fatigue_signal` overload | `overload_inputs.py:176` | **bool** | ❌ | overload |
| `availability` (générateur) | `morpho_program_generator.py` | **frozenset équipement** | ❌ | génération |
| `recovery_spacing` | `program_quality_engine.py:53` | **NON IMPLÉMENTÉ** | — | — |

**Collisions concrètes** : « readiness » = 2 choses affichées **sur la même page** (`index.html:99-150`
vs `:160`) · « disponibilité » = **3** choses (zone-recovery, score comportemental, équipement) ·
**collision d'échelle vivante** (§C.0-B) · « fatigue » a **3 types** (`int 1-5`, `float 0-100`, `bool`) ·
**l'unique arête d'intégration est fail-open** (`recommendation.py:403-406` : toute exception ⇒
fatigue `0.0` = « parfaitement frais »).

**Absents du repo** (vérifié) : ACWR, TRIMP, session-RPE, TSS, décroissance exponentielle, usage HRV.

### C.3 Cardio

**Île de données.** 4 colonnes capturées (`app/models/session.py:103-106`), consommées en
affichage/export/qualité, et **explicitement exclues** du modèle de récupération force :
`recommendation.py:352-355` saute les sessions cardio avant de calculer `last_hit_by_zone`. Une
sortie Z2 de 90 min a **zéro** effet sur la disponibilité. ⇒ `Sb_CARDIO_FATIGUE_BRIDGE_01` retenu.

### C.4 Morphologie runtime

Moteur **orphelin** : aucun routeur n'atteint `morpho_program_generator` ; la seule morphologie
réelle est une **fixture de test privée**. `waist/chest/thigh/calf` sont capturables et `height_cm`
existe sur `User`, mais **aucun adaptateur** ne les convertit en `MorphologyFacts`, et
**`wingspan_cm` n'existe dans aucun modèle**. ⇒ `Sx_MORPHO_CAPTURE_01_SPEC` doit trancher
explicitement : ajouter une colonne (migration) **ou** dériver **ou** omettre.

### C.5 Body Intelligence / `/physique`

BI **livré** mais **flag `False` par défaut** (`app/config.py:95`), **aucun `.env` du repo ne
l'active**, **absent du smoke de déploiement**, et **deux documents se contredisent** sur l'état
prod. ⇒ **risque #1 de l'audit** : `Sb_BI_01.activation` doit **commencer par établir la vérité
d'état prod**. `/physique` **n'est pas supersédé** : la décision est déjà prise (Option B, route
conservée, dépréciation progressive) ⇒ la convergence **exécute** cette décision, elle ne la rouvre pas.

---

## D. SCIENTIFIC GUARDRAILS (contraignants pour toute slice ci-dessous)

1. **Le volume hebdomadaire est une PLAGE ajustable, jamais une vérité universelle.** Interdit
   d'écrire ou d'impliquer « 10-16 séries = optimal ». Tout budget expose `min`/`max`/`basis` et est
   **ajustable par l'utilisateur**. `ZONE_VOLUME_TARGET` existant est une **valeur de départ**, pas une cible morale.
2. **L'échec n'est pas requis pour l'hypertrophie.** La proximité de l'échec est une **entrée
   facultative** assortie d'un **coût de fatigue**, jamais une exigence ni un score de vertu.
3. **La récupération est une ESTIMATION.** Vocabulaire obligatoire : « estimation », « estimé ».
   **Interdit** : « récupéré à X % », toute prétention de mesure physiologique. Chaque estimation
   porte `confidence` et `basis`.
4. **L'anthropométrie ne biaise qu'avec confiance bornée.** Autorisé : orienter une priorité ou une
   sélection avec `confidence` déclarée. **Interdit** : `ape index → exercice` déterministe, longueur
   de fémur, posture, insertions, dyskinésie, diagnostic. *(Garde déjà appliqué en code :
   `morphology_profile.GUARDED_NOT_DEDUCTIBLE`.)*
5. **Agentique propose, déterministe décide.** Aucune mutation d'état de programme par un modèle.
6. **Zéro revendication d'activation musculaire / EMG.** Les zones sont des **attributions
   d'attribution**, pas des mesures.
7. **Honnêteté des manques** (déjà en vigueur dans le générateur) : signaler un trou plutôt que
   fabriquer. Interdit de combler un slot vide par un exercice plausible.

---

## E. DATA SOURCE-OF-TRUTH MATRIX

| Donnée | SoT **actuelle** | SoT **cible** | Slice qui converge |
|---|---|---|---|
| Exercice → zone musculaire | **sous-chaîne** `muscle_mapping._EXERCISE_PATTERNS` (de facto) | `ExerciseMuscleMapping` + `BodyZone` | `Sb_32.4` |
| Propriétés de scoring substitution | `exercise_properties.json` | **inchangé** (clos) | — |
| Métadonnées catalogue / qualité | `exercise_knowledge_base.json` | inchangé, **complété** | curation EKB (hors périmètre) |
| Zones du radar / coach | copies durcies (≥5) | `BodyZone.radar_axis` | `Sb_32.4` |
| Readiness déclarée | `readiness_entries` | **inchangé** (déjà persisté) | `Sx_RECOVERY_READINESS_01` |
| Fatigue accumulée | `behavioral.py` (dérivé, non persisté) | `FatigueSignal` du contrat | `Sx_RECOVERY_READINESS_01` |
| Récupération par zone | `recommendation.RECOVERY_HOURS_TARGET` (privé) | `ZoneRecoveryEstimate` | `Sb_RECOVERY_ESTIMATE_01` |
| Charge cardio | **nulle part** (4 colonnes inertes) | entrée de `FatigueSignal` | `Sb_CARDIO_FATIGUE_BRIDGE_01` |
| Faits de morphologie | **fixture de test** | `MorphologyFacts` depuis capture réelle | `Sx_MORPHO_CAPTURE_01` → `Sb_MORPHO_PROFILE_RUNTIME_01` |
| Priorités d'entraînement | fixture privée | préférences utilisateur persistées | `Sb_TRAINING_PREFERENCES_01` |
| Budget de volume | `ZONE_VOLUME_TARGET` (constante) | budget **ajustable** par utilisateur | `Sb_WEEKLY_VOLUME_BUDGET_01` |
| État du programme | services Custom Program | **inchangé** (clos) | — |
| Corps / mesures | `body_measurements` (**2 écrivains divergents**) | **1** écrivain réconcilié | `Sb_PHYSIQUE_BI_CONVERGENCE_01` |

---

## F. BUILD DEPENDENCY GRAPH

```
        P0 hotfixes (indépendants, aucun pré-requis)
        ├── Sb_ZONE_COUNT_TAXONOMY_FIX_01 ─┐
        └── Sb_FATIGUE_SCALE_FIX_01 ───────┤
                                           │
Sb_MORPHO_DOGFOOD_01 (PR #68, en cours) ───┤
                                           ▼
                            Sb_32.4_BODYZONE_CONSUMER_MIGRATION   ← fondation bloquante
                                           │
                     ┌─────────────────────┼───────────────────────┐
                     ▼                     ▼                       ▼
        Sx_RECOVERY_READINESS_01   Sb_TRAINING_PREFERENCES_01   Sx_MORPHO_CAPTURE_01
              (SPEC)                        │                    (SPEC)
                     │                      ▼                       │
        ┌────────────┼──────────┐   Sb_WEEKLY_VOLUME_BUDGET_01      ▼
        ▼            ▼          │           │            Sb_MORPHO_PROFILE_RUNTIME_01
Sb_CARDIO_    Sb_RECOVERY_      │           ▼                       │
FATIGUE_      ESTIMATE_01       └──► Sb_WEEKLY_PLANNER_01           ▼
BRIDGE_01           │                       │           Sb_MORPHO_EXPLAINABILITY_UI_01
        └───────────┴───────────────────────┤
                                            ▼
                                  Sb_ADAPTIVE_REPLAN_01
                                            │
   Sb_BI_01.activation ──► Sb_PHYSIQUE_BI_CONVERGENCE_01            │
                                            │                       │
   Sb_SUBSTITUTION_REASON_01 ──┐            │                       │
   Sb_EXERCISE_PREFERENCES_01 ─┤            │                       │
   Sx_DECISION_ANALYTICS_01 ───┴────────────┴───────────────────────┤
                                                                    ▼
                                                    Sb_ORCHESTRATOR_EXPLAINER_01
                                                                    ▼
                                                       Sb_ORCHESTRATOR_E2E_01
```

---

## G. ORDERED SPRINT QUEUE

> **Format par slice** : Goal · Deps · Reads · Writes · DB · Consumer impact · Tests · Acceptance ·
> STOP · **NE DOIT PAS reconstruire**.
> **Aucune slice n'est autorisée par ce document** : chacune requiert un `GO BUILD` explicite.

### P0 — Vérité et fondation

#### P0.0 `Sb_MORPHO_DOGFOOD_01` — *(en vol, PR #68)*
Dernier build de `Sx_MORPHO_PROGRAM_01`. **Non ré-ouvert ici.** Ferme la file morphologie.

#### P0.1 `Sb_ZONE_COUNT_TAXONOMY_FIX_01` — **AJOUT justifié par l'audit**
- **Goal** : corriger la collision macro/détaillée de `_zone_session_counts` (§C.0-A) pour que le
  coach et le radar BI cessent d'afficher une lecture structurellement fausse.
- **Deps** : aucune. **Reads** : sessions, `classify_exercise`. **Writes** : aucun. **DB** : **0 migration**.
- **Consumer impact** : `coach_report`, `coach_inference` (texte visible), `body_intelligence_inputs`.
- **Tests** : unitaires sur la projection zone→axe + test de non-régression prouvant que ≥2 axes
  peuvent désormais être non nuls ; broad sweep coach/BI.
- **Acceptance** : « zone travaillée / peu travaillée » reflète les vraies séances, pas seulement `pecs`.
- **STOP** : si la correction impose de changer une taxonomie publique → escalader dans `Sb_32.4`.
- **NE DOIT PAS reconstruire** : le classifieur, le radar, BI.

#### P0.2 `Sb_FATIGUE_SCALE_FIX_01` — **AJOUT justifié par l'audit**
- **Goal** : réconcilier l'échelle `fatigue_score` entre producteur (0–100) et lecteur (0–1) (§C.0-B),
  **et corriger les tests qui pinnent la mauvaise échelle**. Supprimer le *fail-open* silencieux.
- **Deps** : aucune. **Reads** : `behavioral.fatigue_score`. **Writes** : aucun. **DB** : **0 migration**.
- **Consumer impact** : `recommendation_explainer` (texte visible).
- ⚠️ **Contrainte dure** : `recommendation.py` **non modifiable** → la correction vit dans le
  **wrapper** et/ou la normalisation à la frontière.
- **Tests** : table de conversion explicite ; test prouvant que la branche « bon moment pour
  pousser » est atteignable ; non-régression du filtre de fatigue.
- **Acceptance** : le message de fatigue reflète l'état réel ; plus de dégradation muette vers « frais ».
- **STOP** : si la correction exige de toucher `recommendation.py` → STOP + arbitrage.
- **NE DOIT PAS reconstruire** : le moteur de recommandation, `behavioral.py`.

#### P0.3 `Sb_32.4_BODYZONE_CONSUMER_MIGRATION` — **fondation bloquante**
- **Goal** : faire de `ExerciseMuscleMapping`/`BodyZone` la **source de vérité** pour les
  consommateurs lourds (scoring, coach, BI, radar), et retirer progressivement les dicts durcis.
- **Deps** : P0.1 (sinon on migre une projection fausse). **Reads** : tables body zone.
  **Writes** : aucun métier. **DB** : **0 nouvelle table** ; ⚠️ **exige un chemin de peuplement
  applicatif fiable** (le backfill migration est sautable, §C.1) → **peut nécessiter un seed** : à trancher.
- **Consumer impact** : **large** (le sprint le plus risqué du cycle, déjà qualifié tel).
- **Tests** : garde de non-régression `classify(old) == classify(new)` sur l'intégralité du
  référentiel, **+ liste explicite des divergences volontaires** (les collisions connues §C.1 doivent
  être **corrigées ou documentées**, pas re-figées) ; full sweep obligatoire.
- **Acceptance** : ≥1 consommateur lourd lit la DB, aucun changement d'attribution non documenté.
- **STOP** : divergence non explicable · nécessité d'un seed non autorisé · couverture DB < référentiel.
- **NE DOIT PAS reconstruire** : `body_map_descriptor` (déjà correct), la substitution, l'EKB.

#### P0.4 `Sx_RECOVERY_READINESS_01_SPEC` — **SPEC ONLY**
- **Goal** : concevoir le **contrat sémantique unique** (§B.3) réconciliant les 5 concepts / 6 échelles.
- **Deps** : P0.2 (l'échelle doit être assainie avant d'être normalisée). **DB** : aucune (spec).
- **Acceptance** : un vocabulaire, une échelle, une règle de dégradation, une matrice de migration
  par consommateur, et un **plan de coexistence** avec `recommendation.py` non modifiable.
- **STOP** : si le contrat impose de modifier `recommendation.py` → l'écrire comme **arbitrage explicite**.
- **NE DOIT PAS reconstruire** : `readiness.py` (CRUD correct), `overload_engine` (isolé volontairement).

### P1 — Orchestration

| Slice | Goal · Deps · DB · STOP (condensé) |
|---|---|
| `Sb_TRAINING_PREFERENCES_01` | Persister les préférences déclarées (priorités, jours/semaine, équipement). Deps P0.3. **DB : nouvelle table probable → migration additive**. STOP : si le modèle empiète sur `UserProfile`. NE PAS reconstruire : le profil, le vocabulaire de priorités (`FOCUS_CANDIDATE_VOCAB`). |
| `Sb_WEEKLY_VOLUME_BUDGET_01` | Budget **plage ajustable** par zone (§D.1). Deps préférences + P0.3. DB : additive. STOP : toute formulation « optimal ». NE PAS reconstruire : `ZONE_VOLUME_TARGET` (réutiliser comme valeur de départ). |
| `Sb_WEEKLY_PLANNER_01` | Plan hebdomadaire **déterministe et non contraignant** depuis budget + intentions. Deps budget. DB : lecture ; écriture éventuelle du plan = additive. ⚠️ **Ne modifie pas `recommendation.py`**. STOP : conflit avec la décision « pas de route `/weekly` » (`Sb_27.3`) → arbitrage. NE PAS reconstruire : la recommandation du jour. |
| `Sb_CARDIO_FATIGUE_BRIDGE_01` | Relier la charge cardio au signal de fatigue (§C.3). Deps P0.4. DB : 0 nouvelle colonne attendue (les 4 existent). STOP : si un modèle de charge exige une revendication physiologique → borner en estimation. NE PAS reconstruire : la capture cardio. |
| `Sb_RECOVERY_ESTIMATE_01` | Implémenter `ZoneRecoveryEstimate` (**ESTIMATION** + `confidence` + `basis`). Deps P0.4, cardio bridge. DB : additive si persisté. STOP : « % récupéré » dans une surface. NE PAS reconstruire : `RECOVERY_HOURS_TARGET` (réutiliser comme base déclarée). |
| `Sb_ADAPTIVE_REPLAN_01` | Replanifier après écart réel (séance manquée/écourtée). Deps planner + recovery. DB : additive. STOP : mutation d'un programme publié sans cycle de version. NE PAS reconstruire : le cycle Custom Program. |
| `Sx_MORPHO_CAPTURE_01_SPEC` | **SPEC** : comment capturer les faits morphologiques réels. **Doit trancher `wingspan_cm`** (colonne / dérivation / omission) et réconcilier les **2 écrivains** de `body_measurements`. **0 photo** (contrainte dure existante). STOP : toute dérive vers photo/composition. |
| `Sb_MORPHO_PROFILE_RUNTIME_01` | Brancher le moteur morphologie **orphelin** sur des données réelles (§C.4). Deps capture. DB : selon spec capture. STOP : ambiguïté de migration. NE PAS reconstruire : `morphology_profile.py` (pur, clos). |
| `Sb_MORPHO_EXPLAINABILITY_UI_01` | Exposer « pourquoi ce programme » (descripteurs → priorités → slots → exercices) **avec confiance bornée**. Deps runtime. DB : 0. STOP : toute formulation médicale. NE PAS reconstruire : le générateur. |
| `Sb_BI_01.activation` | ⚠️ **Commencer par établir la vérité d'état prod** du flag (docs contradictoires, §C.5), puis activer + **ajouter `/body/intelligence` au smoke**. Deps dogfood BI. DB : 0. STOP : divergence prod/repo non résolue. NE PAS reconstruire : BI (livré). |

### P2 — Convergence, préférences, analytique

| Slice | Goal · Deps · DB · STOP (condensé) |
|---|---|
| `Sb_PHYSIQUE_BI_CONVERGENCE_01` | **EXÉCUTER** la décision déjà prise (Option B : BI primaire, `/physique` déprécié progressivement, route conservée) **sans la rouvrir**, et réconcilier les **2 écrivains** de `body_measurements`. Deps `Sb_BI_01.activation`. DB : possible unification additive. STOP : toute remise en cause de l'Option B → hors périmètre. NE PAS reconstruire : `Sb_BI_01.3`, `Sb_BI_01.next` (clos). |
| `Sb_SUBSTITUTION_REASON_01` *(renommé depuis `Sb_03.1`)* | Capturer la **raison utilisateur** d'une substitution (le prompt existe déjà mais n'est jamais capté, `exercise_card.html:530`), **et** combler le `rationale` manquant de N1/N3. **Renommage justifié** : `Sb_03.1` est un identifiant hérité d'une autre lignée de spec → collision d'ID. DB : colonne additive nullable. STOP : modification du moteur de substitution. NE PAS reconstruire : `substitution.py` (clos). |
| `Sb_EXERCISE_PREFERENCES_01` | Préférences/exclusions d'exercices (aimé, à éviter, blessure-safe **sans revendication médicale**). Deps préférences d'entraînement. DB : additive. STOP : toute formulation clinique. |
| `Sx_DECISION_ANALYTICS_01_SPEC` | **SPEC** : tracer les décisions de l'orchestrateur (quoi/pourquoi/sur quelle base) pour l'audit et l'amélioration. DB : conception seulement. STOP : collecte de données personnelles hors périmètre. |
| `Sb_ORCHESTRATOR_EXPLAINER_01` | Une explication unifiée de bout en bout de la chaîne. Deps la majorité de P1. DB : 0. STOP : explication non traçable à une donnée réelle. NE PAS reconstruire : `recommendation_explainer`, BI, l'explainer morpho. |

### FINAL

| Slice | Contenu |
|---|---|
| `Sb_ORCHESTRATOR_E2E_01` | Preuve de bout en bout : *body facts → … → adaptive replanning*, sur une **fixture privée**, via les **services existants**, avec **0 fabrication** et **0 revendication interdite**. Modèle directement réutilisable : `Sb_MORPHO_DOGFOOD_01`. |

---

## H. DEFERRED / REJECTED FEATURES

**Différés par l'opérateur** (ne pas ouvrir sans override explicite) : GymProfile / multi-salles ·
interopérabilité wearables · Apple Health / Health Connect · import OCR/photo/PDF · expansion
sociale · réécriture front natif · React/SPA *(interdiction permanente en production)*.

**Rejetés — non scientifiques** (jamais implémentés, jamais revendiqués) : diagnostic médical ou
postural · inférence de masse grasse · inférence précise de segments osseux (fémur/humérus) ·
revendications EMG / pourcentage d'activation · « % de récupération mesuré ».

**Différés hérités, confirmés par l'audit** : `Sb_CUSTOM_PROGRAM_EKB_04` (seed DB) · leviers CI 3-4 ·
`Sb_UI_05.2`/`.3`→`.5` · curation EKB (débloque 4 sous-scores qualité) · rebrand légal AUREN
(**gate externe**, hors ingénierie).

---

## I. DEFINITION OF DONE — programme complet

AUREN est un orchestrateur déterministe et conscient de la biomécanique lorsque **tout** ce qui suit
est vrai :

1. **Une** source de vérité exercice→zone, lue par tous les consommateurs lourds (`Sb_32.4`).
2. **Un** contrat sémantique readiness/fatigue/récupération, **une** échelle, dégradation explicite.
3. La récupération est **toujours** présentée comme une **estimation** avec confiance et base.
4. Le volume hebdomadaire est une **plage ajustable**, jamais une vérité affichée.
5. La charge cardio **contribue** au signal de fatigue.
6. La morphologie provient de **données utilisateur réelles**, plus d'une fixture de test.
7. La chaîne complète est **traçable et explicable** : chaque exercice proposé remonte à une
   intention, une priorité, un descripteur, un fait — avec confiance bornée.
8. Toute mutation d'état reste détenue par des **services déterministes** ; l'agentique propose.
9. **Zéro fabrication** : tout manque est signalé, jamais comblé par une valeur plausible.
10. **Zéro revendication interdite** dans toute surface (médical, composition, EMG, % mesuré).
11. Un test **E2E** parcourt la chaîne sur une fixture privée, sans exposer de donnée personnelle.
12. Les CI/gates existants restent verts, sans affaiblissement de gate.

---

## 7. Non-goals / Périmètre interdit

Ce document est **SPEC ONLY**. Il **n'autorise aucun build** et **ne produit aucun code**.

**Hors scope, explicitement :**
- **Aucune implémentation** : ni service, ni modèle, ni migration, ni test applicatif, ni UI.
- **Aucune réouverture** des cycles clos : moteur de substitution · surcharge progressive `Sx_30` ·
  architecture de séance focalisée `Sx_UI_04` · rationalisation du feedback `Sx_FB_01` ·
  transformation UI Auren `Sx_UI_10` · générateur morphologie · cycle Custom Program (publication,
  versioning, lancement) · backup/export **en tant qu'architecture** (leurs manques sont notés, pas rouverts).
- **Aucune modification** de `recommendation.py` ni du cœur de scoring (contrainte permanente).
- **Aucune réécriture** des roadmaps antérieures : ce document les **réconcilie** et les référence.
- **Aucune décision de merge, de cleanup, ni d'activation de flag** — toutes restent des GO humains.
- **Aucune revendication médicale, posturale, de composition corporelle, d'insertion, de longueur
  osseuse, d'EMG ou de pourcentage de récupération mesuré.**
- Les fonctionnalités listées en §H restent **fermées** sans override explicite.

---

## Verdict

**Verdict :** ✅ **Sx_AUREN_ORCHESTRATOR_01 — SPEC LIVRÉE (docs-only).** La roadmap canonique
pilotée par les manques est établie sur un **audit du code actif** : 6 constats structurants,
**2 défauts vivants découverts** et placés en P0, une **fondation bloquante confirmée** (`Sb_32.4`),
une **fragmentation prouvée** de readiness/fatigue/récupération à unifier par contrat, et une
**file ordonnée** P0→P2→E2E dont **chaque slice** porte objectif, dépendances, attentes DB, impact
consommateurs, niveau de test, critères d'acceptation, conditions d'arrêt et interdits de
reconstruction. **Aucun build n'est autorisé par ce document.**
