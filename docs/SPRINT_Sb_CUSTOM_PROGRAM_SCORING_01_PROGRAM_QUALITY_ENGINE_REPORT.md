# Sprint Sb_CUSTOM_PROGRAM_SCORING_01 — Program Quality Engine — BUILD

**Statut** : 🟢 **PATCH COMPLETE / REVIEW PENDING** (non commité, non poussé, CI non lancée)
**Type** : CODE BUILD — **moteur pur** (Option A(a) opérateur), zéro DB/ORM/migration/`data/`
**Date** : 2026-07-22
**Specs** : `Sx_CUSTOM_PROGRAM_03` §3 (contrat moteur) · §4 (modèle de sortie) · §5 (sous-scores) · §6 (grade) · §7 (régimes de vérité) · §8 (microcopy) · §15 (queue : SCORING_01 = moteur + dataclasses + tests)
**Branche** : `sb/custom-program-scoring-01-engine` (worktree dédié, base `062ee92`, head Alembic `n5o0i6j7l98` inchangé)
**Préflight** : ✅ GO PATCH validé — Option **A(a)** : moteur pur, 4 sous-scores calculables, 4 déclarés manquants, grade plafonné à B

---

## 0. Étape 0 — Brainstorming / Options / Risques / Choix retenu

| Décision | Options | Choix retenu |
|---|---|---|
| Architecture | A moteur pur · B + adaptateur ORM · C + écriture reviews | **A — moteur pur** (arbitrage opérateur ; la spec §15 assigne la persistance à `SCORING_03`, et B n'a aucun consommateur : wizard fermé) |
| Sous-scores non mesurables | noter 0 · exclure + déclarer | **exclure de la moyenne + `missing_data`** — noter 0 un sous-score non mesurable est un faux négatif, donc de la pseudo-science |
| Grade V1 | permettre A · plafonner à B | **plafonner à B** avec `grade_cap_reason` explicite — 4/8 sous-scores manquants ne permettent pas de conclure à A |
| Source EKB | table DB · JSON canonique | **JSON** (`data/exercise_knowledge_base.json`, lecture seule) — EKB_04 reste DEFERRED |
| Versionnement | ad hoc · patron `overload_engine` | **`PROGRAM_QUALITY_SCORING_VERSION = 1`** exposée sur chaque sortie + `ekb_version` pinné (patron Sx_30 vérifié) |

**Risque principal identifié** — overfitting / pseudo-science. Mitigations appliquées : sous-scores non mesurables exclus (jamais 0) · seuils = constantes versionnées documentées, non ajustées sur une fixture · `confidence` + `coverage_ratio` exposés · `disclaimer` permanent · lexique médical et injonctions testés par grep · aucun historique réel (V2 strict).

## 1. Patch appliqué

| Fichier | Nature |
|---|---|
| `app/services/program_quality_engine.py` | **nouveau** (~420 l.) — dataclasses pures d'entrée (`ProgramDefinition`/`SessionPlan`/`ExerciseSlot`/`UserProfile`) et de sortie (`QualityReviewResult`/`Subscore`), vue EKB read-only, 4 sous-scores, grade hybride + cap V1, helpers extraits (`_aggregate`, `_resolve_grade`, `_build_assumptions`, `_confidence_for`) |
| `tests/test_program_quality_engine.py` | **nouveau** — **19 tests** |

**Zéro `data/` · zéro `app/models/` · zéro migration · zéro seed · zéro API/UI · zéro écriture `quality_reviews` · `user_program_drafts.py` intact.**

## 2. Contrat final du moteur

```
score_program(definition: ProgramDefinition,
              ekb: ExerciseKnowledgeBase | None = None,
              profile: UserProfile | None = None) -> QualityReviewResult
```

Sortie (dataclass frozen, `to_dict()` JSON-sérialisable) : `grade` · `global_score` ·
`subscores` (clé/score/raisons) · `alerts` · `suggestions` · `assumptions` ·
`missing_data` · `confidence` · `coverage_ratio` · `grade_cap_reason` ·
`scoring_version` · `ekb_version` · `disclaimer`.

**Pureté prouvée par le fait** : importer le moteur ne tire **aucun** module
`sqlalchemy` / `app.models` / `app.database` (vérifié à l'exécution, et pinné par un test
qui grep le source du module).

## 3. Sous-scores livrés (4/8)

| Sous-score | Source EKB | Couverture |
|---|---|---|
| `volume_per_zone` | `zone_primary` | 65/103 |
| `push_pull_legs_balance` | `movement_pattern` | 51/103 |
| `frequency_per_zone` | zone × séances | 65/103 |
| `equipment_feasibility` | `equipment_family` + profil déclaré | 73/103 |

## 4. Missing data (4/8) — jamais notés 0

| Sous-score | Raison exacte |
|---|---|
| `recovery_spacing` | champ EKB `fatigue_class` non curé |
| `redundancy` | champ EKB `variant_group` null sur les 103 entrées (V1) |
| `duration_realism` | champ EKB `estimated_slot_minutes` non curé |
| `overload_compatibility` | champ EKB `overload_compatibility` non curé |

Ils sont **exclus de la moyenne** (calculée sur 4 valeurs), listés dans `missing_data`,
et **plafonnent le grade à B**. Leur activation future sera **additive** (curation EKB →
`scoring_version` 2).

## 5. Grade cap et confiance

- **Cap V1** : tout grade calculé A ou B ressort **B**, avec `grade_cap_reason` =
  « Grade plafonné à B : 4 sous-scores sur 8 ne sont pas mesurables tant que l'EKB n'est
  pas curé ». **A est inatteignable en V1** (testé).
- **C reste atteignable** (déséquilibre réel) et **publiable** — le moteur n'émet aucun
  état bloquant (OQ-SCORE-C, testé).
- **`confidence`** dérivée de `coverage_ratio` (part des slots résolus par l'EKB) :
  ≥ 0.8 `moderate` · ≥ 0.5 `low` · sinon `very_low`. Les gaps **réduisent la confiance,
  ne cassent jamais le moteur** (exercice inconnu → assumption, pas d'exception).

## 6. Tests et checks exécutés

| Suite / check | Résultat |
|---|---|
| Dédiés (`test_program_quality_engine.py`) | **19/19** (1 correction d'assertion de test, zéro correction du moteur) |
| Non-régression EKB (coverage + knowledge_base + classifiability) | **46/46** |
| **Broad sweep ciblé** (`-k program_quality or ekb or user_program or quality or scoring`) | **208 passed / 0 failed** |
| `ekb_classifiability_qa` | exit 0 (0 erreur, 4 warnings figées) |
| ruff (2 fichiers neufs) | clean (1 refactor C901 : helpers extraits ; 1 S1172 préventif corrigé) |
| `check_ruff_budget` | **543 ≤ 548** |
| `check_spec_protocol` | PASS |
| **`check_scope`** | **ISOLATED** — `full_sweep_local` explicitement **skippé** par le garde-fou (contrat CLAUDE.md §1) ; la CI PR reste la source de vérité |

Couverture des 19 tests : déterminisme strict (sortie identique, `to_dict()` identique) ·
sérialisabilité JSON · versions exposées · 4 sous-scores présents · 4 manquants déclarés et
jamais notés · moyenne sur 4 valeurs · programme équilibré → **B jamais A** · déséquilibré →
**C** · aucun état bloquant · exercice inconnu sans crash · couverture majoritairement
absente → `very_low` · programme vide sans crash · profil absent → assumptions · **lexique
médical/hormonal absent** · **aucun « tu dois »/« optimal »/« parfait »** · disclaimer présent ·
**aucun import ORM dans le source du moteur**.

## 7. Risques résiduels

Le moteur est **non branché** (aucun appelant : wizard et publication fermés — pattern
fondation du track) · les seuils A/B/C restent à calibrer par le dogfood (OQ-SCORE-A/B,
pondérations uniformes V1) · la montée à 8 sous-scores dépend d'un futur build de curation
EKB, non ouvert · `SCORING_02` (microcopy/alertes/suggestions complètes) et `SCORING_03`
(persistance `quality_reviews`) restent fermés.

## 8. Confirmations de périmètre

✅ Moteur pur (zéro DB/ORM/I-O, prouvé) · ✅ zéro `data/` (EKB lu en lecture seule) · ✅ zéro
`app/models/`, zéro migration (head `n5o0i6j7l98`), zéro seed · ✅ zéro écriture
`UserProgramQualityReview` · ✅ zéro API/UI/wizard/publication · ✅ `session_builder`,
`user_program_drafts.py`, `quality_score.py`/`muscle_scoring.py` intacts · ✅ pas de LLM ·
✅ pas de claim médical (testé).

---

## Verdict

**Verdict :** 🟢 **Sb_CUSTOM_PROGRAM_SCORING_01 — PATCH COMPLETE / REVIEW PENDING.**

Le moteur de scoring existe : pur, déterministe, versionné, explicable sous-score par
sous-score. Il livre honnêtement **4 sous-scores sur 8** et **déclare** les 4 autres comme non
mesurables plutôt que d'inventer un chiffre — grade plafonné à B, confiance dégradée par la
couverture EKB réelle, aucun claim médical. 19 dédiés + 46 non-régression + 208 broad sweep
verts ; check_scope ISOLATED. **`SCORING_02`, `SCORING_03`, `EKB_04`, `WIZARD_*` restent NOT
OPENED.**
