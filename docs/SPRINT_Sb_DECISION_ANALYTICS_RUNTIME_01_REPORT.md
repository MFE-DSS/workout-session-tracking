# SPRINT Sb_DECISION_ANALYTICS_RUNTIME_01 — observer sans décider (RAPPORT)

**Train :** `AUREN_DECISION_OBSERVABILITY_01`, tranche 1/2 ·
**Base canonique :** `774e9b6` · **Branche :** `sb/decision-analytics-runtime-01`

---

## 1. Préflight — audit des frontières d'orchestration réelles

Le résultat de l'audit décide de l'architecture, et il est plus favorable
qu'attendu : **chaque producteur retourne déjà sa justification et sa version de
politique**. Aucun moteur n'a besoin de changer.

| Décision | Producteur pur | Basis actuel | Version | Références d'entrée | Frontière collecteur |
|---|---|---|---|---|---|
| `VOLUME_BAND` | `build_weekly_volume_budget(prefs)` | `ZoneVolumeBudget.basis` | `weekly-volume-v1` | prefs déclarées | `build_weekly_volume_budget_for_user(db, uid)` **déjà en base** |
| `ZONE_ALLOCATION` | `allocate_capacity(...)` | `ZoneCoverage.allocation_basis` | `PLANNER_VERSION` | zones de budget, candidats | `WeeklyPlan.zone_coverage` |
| `SLOT_SELECTION` | `generate_program` → `_slots_by_zone` | `ExercisePrescription.rationale` | `PLANNER_VERSION` | intentions, matériel | `WeeklyPlan.prescriptions` |
| `SET_PRESCRIPTION` | `allocate_zone(...)` | `budget_source`, `rep_target_source` | `set-allocation-v1` | créneau + bande | `WeeklyPlan.prescriptions` |
| `CONTRIBUTION_CREDIT` | `contributions_for(prescriptions)` | `ZoneCoverage.contribution_basis` | `set-contribution-v1` | prescriptions | `WeeklyPlan.zone_coverage` |
| `REPLAN_DELTA` | `replan(plan, ...)` | `PlanDelta`, `effective_impact` | `REPLAN_VERSION` | plan, divergences, état | appelant de `replan` |
| `MATERIALIZATION` | `assess_materialization(plan)` | `MaterializationStatus` | `MATERIALIZATION_VERSION` | empreinte de plan | `materialize_weekly_plan(db, ...)` **déjà en base** |
| `RECOVERY_ASSESSMENT` | `build_training_state(...)` | récupération par zone | `RECOVERY_POLICY_VERSION` | séances | **seulement si consommée** |
| `MORPHOLOGY_DESCRIPTOR` | `build_morphology_profile(facts)` | `evidence` du descripteur | `MORPHOLOGY_PROFILE_ENGINE_VERSION` | faits | **non persisté en V1** |

**Conclusion structurante** : `WeeklyPlan` porte déjà tout ce qu'il faut pour les
cinq décisions de génération. Le collecteur lit des **valeurs de retour** ; il
n'appelle aucun moteur, et un test l'impose en interdisant les symboles
`generate_program`, `planner_candidate_pool`, `substitution` et `_rank_zone`
dans son source.

---

## 2. Résolution des OQ (décisions opérateur, appliquées)

| OQ | Résolution appliquée |
|---|---|
| **OQ-1 rétention** | `RETENTION_POLICY_V1 = OWNER_LIFETIME` — aucun TTL, aucune purge, aucun archivage ; `ON DELETE CASCADE` suffit. |
| **OQ-2 alternatives** | Persistées **uniquement** si le moteur les connaissait. Aucun producteur actuel ne retient de classement à ce stade ⇒ **`[]` partout**, jamais reconstruit. |
| **OQ-3 historique** | Trace **immuable**. Écouteur SQLAlchemy `before_update` qui **lève** ; aucun service de mise à jour ni de recalcul. |
| **OQ-4 granularité** | Une trace = une décision sémantique. `CONTRIBUTION_CREDIT` **agrégé par zone** (test : moins de traces que de séries physiques) ; morphologie non persistée. |

---

## 3. Où l'observation se déclenche — et pourquoi pas ailleurs

L'observation vit dans `POST /programs/from-weekly-plan`, **après** la création
du brouillon.

Un rendu de `/programs` calcule lui aussi une proposition. L'observer y
écrirait un groupe de traces **à chaque affichage de page** — exactement ce que
l'opérateur interdit pour la récupération (« pas à chaque rendu de read-model »)
et pour la morphologie. La matérialisation est le moment où l'utilisateur
**agit** : c'est la frontière de décision.

Le chemin produit reste **littéralement inchangé** : le budget est re-dérivé
dans l'observateur (`build_weekly_volume_budget` est pur et déterministe, donc
il rend exactement celui qu'a utilisé le planificateur) plutôt que de
restructurer l'appel qui produit le plan. C'est ce qui rend la preuve de
retirabilité crédible.

---

## 4. Preuves

| Preuve | Résultat |
|---|---|
| Tests dédiés | **30** |
| Balayage ciblé (planner, budget, contribution, replan, drift, programmes) | **254** |
| Drift Alembic | OK |
| Roundtrip migration | 48 objets, schéma identique |
| Patterns de migration | aucun motif dangereux |
| Snapshot de schéma | régénéré |
| Budget ruff | 536 ≤ 548 |
| Pré-scan Sonar S9073 / S1192 | **0 / 0** après correction |

### Les cinq plantations exigées — toutes mordent

| # | Plantation | Garde qui tombe |
|---|---|---|
| 1 | aplatir les sources dans une seule colonne | `test_source_classes_stay_separate_in_storage` |
| 2 | réécrire le `basis` (« Auren a choisi … ») | `test_the_basis_is_cited_verbatim_never_reworded` |
| 3 | collecteur mutant les entrées persistées | `test_observation_does_not_mutate_the_persisted_decision_inputs` |
| 4 | autoriser l'`UPDATE` historique | `test_a_persisted_trace_cannot_be_updated` |
| 5 | fabriquer une alternative rejetée | `test_rejected_alternatives_are_empty_when_the_engine_never_ranked_any` |

### Deux gardes ont dû être écrites ou renforcées **avant** de pouvoir planter

**(a) `basis` verbatim n'était pas gardé.** La plantation 2 n'avait rien à faire
tomber : rien ne comparait le `basis` persisté à celui du moteur. Le test a été
écrit d'abord, avec un compteur `checked` qui échoue si aucune comparaison n'a
eu lieu — sans quoi il serait passé à vide.

**(b) La retirabilité ne couvrait pas la base.** Le test central construit ses
plans depuis des préférences **en mémoire** : un collecteur qui réécrirait
silencieusement les préférences **persistées** serait passé au travers. Un
second test planifie des deux côtés **via la base** et compare empreinte et
préférences. C'est lui, et lui seul, qui attrape la plantation 3.

### Un défaut réel trouvé par mes propres tests

`test_a_collector_failure_does_not_break_materialization` a échoué au premier
passage. `observe_plan_generation_for_user` avale bien ses erreurs, mais **le
site d'appel n'était pas protégé** : le jour où quelqu'un modifie l'observateur
et le laisse lever, la route rendrait 500 **alors que le brouillon est déjà créé
et valide**. Une garantie qui dépend de la discipline interne de l'appelé n'en
est pas une — la route porte désormais sa propre garde, et le brouillon prime
sur sa trace.

---

## 5. Retirabilité — la preuve centrale

Avec collecteur **vs** collecteur entièrement désactivé, sont comparés :
budget, empreinte de plan, prescriptions, contributions, replan, statut de
matérialisation, descripteurs morphologiques. **Identiques.** Le test vérifie
d'abord que le collecteur a réellement tourné (`assert group`, `assert rows`),
sans quoi il ne prouverait rien.

S'y ajoute la parité `recommendation` et une garde structurelle : les quatre
moteurs purs conservent **exactement** leurs paramètres (`build_weekly_plan` →
`{preferences, budget, pool}`), sans `db` ni `user_id`.

---

## 6. Limites énoncées

- **Aucune alternative rejetée n'est disponible aujourd'hui.** Les producteurs
  ne conservent pas leurs classements. Le champ est vide partout — c'est la
  réponse honnête, et une tranche d'instrumentation dédiée sera nécessaire si le
  produit le justifie.
- **`REPLAN_DELTA` et `RECOVERY_ASSESSMENT` ne sont pas encore écrits** : leur
  frontière de consommation est le replan, non branché dans cette tranche.
- `MEASURED_FACT` et `DERIVED_FACT` n'ont pas de colonne dédiée et rejoignent
  `constraint_sources` ; leur `kind` reste intact dans la charge utile, donc la
  nature n'est jamais perdue — mais la requête par nature demande de lire le JSON.

## Verdict

L'observabilité existe et **ne peut pas décider** : les moteurs restent purs,
le collecteur lit leurs sorties, et sa suppression complète ne déplace aucune
sortie produit.

Le vrai risque n'était pas d'écrire des lignes : c'était de laisser
l'observabilité devenir une dépendance de disponibilité. Mes propres tests l'ont
attrapée là où je ne l'avais pas prévue — au site d'appel, pas dans le service.
