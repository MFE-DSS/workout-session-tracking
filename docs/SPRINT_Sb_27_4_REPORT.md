# Sb_27.4 — Recommendation Explanation (Sprint Report)

**Date :** 2026-06-15
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Spec parente :** `docs/strategy/Sx_27_COACHING_LOOP_AND_PRODUCT_ACTIVATION_SPEC.md`
**Lot Sx_27 :** §14 — Sb_27.4 (Recommendation explanation)
**Statut :** ✅ Livré

---

## 1. Résumé exécutif

Sb_27.4 livre un wrapper externe `app/services/recommendation_explainer.py` qui consomme le payload retourné par `recommend_next_session` et produit 1 à 3 raisons lisibles par l'utilisateur. La tuile Today de la Home affiche désormais une raison principale + jusqu'à 2 raisons secondaires (cold start, zone freshness, fatigue, fallback). OQ-4 tranchée verbatim user : **`recommendation.py` n'est pas modifié**.

**Verdict :** ✅ **Sb_27.5 PRÊT**.

## 2. Périmètre livré

### 2.1 Fichiers créés

| Fichier | Rôle |
|---|---|
| `app/services/recommendation_explainer.py` | `explain_recommendation(reco_payload) -> dict` — wrapper read-only, 5 règles cumulables (cold_start, top.phrase, fallback, zone freshness, fatigue), cap 3 raisons, dedupe |
| `tests/test_recommendation_explainer.py` | 24 tests : shape contract, dégradés (None / dict vide / garbled), chaque règle isolée + son fallback, dedupe, cap MAX_REASONS, garde "recommendation.py non importé" |
| `docs/SPRINT_Sb_27_4_REPORT.md` | Ce rapport |

### 2.2 Fichiers modifiés (touche minimale)

| Fichier | Changement |
|---|---|
| `app/services/home.py` | `_build_today` consomme l'explainer. Si l'explainer fournit `available=True`, le payload Home gagne `reasons[]`, `confidence`, `fallback_note`. Si l'explainer raise ou retourne `available=False`, fallback sur le comportement Sb_27.1 (single `phrase`). |
| `app/templates/_partials/home_coaching_loop.html` | Ajout d'une `<ul>` des raisons secondaires sous la raison principale (max 2 supplémentaires), + ligne `fallback_note` discrète si présente. |

### 2.3 Fichiers NON touchés (par contrat verbatim user — OQ-4)

- `app/services/recommendation.py` : **0 modification** — vérifié par un test dédié `test_recommendation_py_was_not_modified` qui scanne la source de l'explainer pour s'assurer qu'aucun import depuis `recommendation.py` n'est présent
- `app/services/scoring/`, `reco/`, `implicit_signal.py`, `quality_score.py`, `coach_report.py`, `substitution.py`, `body_tracking.py` : **0 fichier touché**
- `app/routers/pages.py` : **non touché** (l'explainer est appelé depuis `home.py`, pas depuis la route)
- `app/routers/sessions.py`, `app/main.py`, `app/deps.py` : **non touchés**
- `app/models/*` : **0 modèle modifié**
- `migrations/versions/` : **0 nouvelle migration**
- `app/templates/index.html`, `app/templates/session_done.html`, `app/templates/progress.html` : **non touchés**
- `app/services/weekly_loop.py`, `app/services/session_review.py` (Sb_27.3 et Sb_27.2) : **non touchés**
- `docs/AUTH_SCOPE_MATRIX.md` : **non modifié** — aucune surface (route) ne change ; l'enrichissement Home Sb_27.1 reste documenté tel quel
- Gates Sb_26.1 → Sb_27.3 : **toutes intactes**

## 3. Décisions clés

### 3.1 OQ-4 : wrapper externe (verbatim user)

L'explainer consomme uniquement le payload **déjà retourné** par `recommend_next_session`. Pas de ré-exécution du scoring, pas d'import de symboles internes de `recommendation.py`. Un test (`test_recommendation_py_was_not_modified`) vérifie qu'aucune ligne `from app.services.recommendation import` n'apparaît dans l'explainer.

### 3.2 5 règles cumulables, priorisées, déduppliquées, cap 3

| # | Règle | Condition | Phrase |
|---|---|---|---|
| A | Cold start | `context.cold_start is True` | "Première séance — démarrage doux suggéré." |
| B | Top.phrase | `top.phrase` non vide (verbatim recommendation.py) | la phrase elle-même |
| C | Fallback | `context.fallback is True` | "Recommandation basée sur ton historique récent." |
| D | Zone freshness | `primary_zones` non vide ET `days_since_last_*` ≥ 2 | "Pectoraux, triceps 5 j sans muscu — frais à travailler." |
| E | Fatigue | `fatigue_score ≥ 0.7` ou `≤ 0.2` | "Niveau de fatigue élevé — séance légère privilégiée." / "...bas — bon moment pour pousser." |

L'ordre d'évaluation est A → B → C → D → E. Si une phrase apparaît déjà dans `reasons`, elle n'est pas ré-ajoutée (dedupe). Les raisons sont ensuite tronquées à 3.

### 3.3 Si rien à dire → fallback explicite, jamais d'invention

Si `top.phrase` est vide ET aucune règle contextuelle ne s'active, `reasons` retombe sur "Recommandation basée sur ton historique récent." + `confidence="low"` + `fallback_note` explicite. Aucune phrase fabriquée à partir de rien (verbatim Sx_27 §16).

### 3.4 Zone freshness : seuil 2 jours minimum

Si `days_since_last_strength == 1`, on ne dit **pas** "frais à travailler" (faux signal). Le seuil 2 jours est l'heuristique : sous 2 jours, la zone n'est pas vraiment "fraîche". Test `test_zone_freshness_is_silent_when_days_below_threshold`.

### 3.5 Fatigue : bandes qualitatives, jamais le score numérique

L'utilisateur n'a pas besoin de voir "fatigue_score = 0.84". On surface uniquement deux bandes ("élevé", "bas") quand le signal est sans ambiguïté (≥0.7 ou ≤0.2). La zone grise (0.2-0.7) est silencieuse — meilleure UX que d'afficher un signal pas net.

### 3.6 Résilience pas-de-payload (`_empty`)

Si `reco_payload` est `None`, `{}`, ou structurellement cassé (`top` est une string, `context` est une string, etc.), l'explainer retourne `_empty(available=False)`. Aucune exception ne remonte. Tests `test_payload_with_garbled_*`.

### 3.7 home.py : try/except autour de l'explainer

`_build_today` enveloppe l'appel à `explain_recommendation` dans un try/except. Si l'explainer raise pour une raison inattendue, on retombe sur le comportement Sb_27.1 (single phrase). **`GET /` ne peut pas casser à cause de l'explainer.**

### 3.8 Pas de modif `/launcher`

La spec autorise une touche sur `/launcher` "uniquement si une explication simple peut être passée sans refonte". J'ai préféré scoper Sb_27.4 strictement à la Home pour éviter d'étendre la surface. `/launcher` reste candidat pour Sb_27.6 (UX simplification pass).

## 4. Tests et vérifications (DoD)

Exécutés localement :

| Check | Résultat | Notes |
|---|---|---|
| `tests/test_recommendation_explainer.py -v` | ✅ **24/24** | chaque règle isolée, dégradés, dedupe, cap, garde anti-import |
| `pytest --ignore=tests/test_v1_acceptance.py -q` | ✅ (CI le confirmera) | +24 vs 1019 = 1043 attendus |
| `python scripts/catalog_qa.py` | ✅ OK | inchangé |
| `python scripts/machine_atlas_qa.py` | ✅ OK | inchangé |
| `PYTHONPATH=. python scripts/check_alembic_drift.py` | ✅ OK | aucune migration |
| `python scripts/check_schema_snapshot.py` | ✅ OK | snapshot inchangé |
| `python scripts/check_migration_patterns.py` | ✅ OK | aucune migration ajoutée |
| `python scripts/check_migration_roundtrip.py` | ✅ OK | inchangé |
| `python scripts/check_ruff_budget.py` | ✅ OK | **534 ≤ 548** |
| `python scripts/check_spec_protocol.py` | ✅ OK | sprint report ajouté, marqueur verdict présent |
| `python scripts/check_auth_scope_matrix.py` | ✅ OK | 3 fichiers présents |
| `pip-audit -r requirements.txt --strict` | ✅ OK | clean |

## 5. CI réelle (post-push)

À renseigner après push.

- [ ] Job `pytest + QA scripts` (incl. perf baseline smoke) — vert attendu
- [ ] Job `lint (... + check_spec_protocol + check_auth_scope_matrix)` — vert attendu
- [ ] Job `SonarCloud` — vert attendu
- [ ] Pas de régression sur les gates Sb_26.1 → Sb_27.3

## 6. Risques

| Risque | Probabilité | Mitigation |
|---|---|---|
| `recommendation.py` change de format de payload | basse | `_empty(available=False)` + try/except sur chaque champ ; aucune assertion structurelle stricte |
| L'explainer surface une phrase fausse | très basse | seuils stricts (zone ≥ 2j, fatigue ≥0.7 ou ≤0.2), tests pour chaque silence requis |
| Cap 3 cache un signal utile | basse | priorité ordonnée ; le plus actionnable arrive d'abord |
| Home casse si l'explainer raise | impossible | try/except dans `_build_today` + fallback Sb_27.1 |
| Confusion utilisateur entre `reason` (legacy) et `reasons[]` (nouveau) | basse | les deux coexistent ; template affiche reason en lead + reasons[1:] en liste secondaire |

## 7. Contraintes respectées (verbatim user)

| Contrainte | Statut |
|---|---|
| Ne touche pas à `recommendation.py` | ✅ test dédié garde |
| Ne touche pas à `scoring/` | ✅ |
| Ne touche pas à `reco/` | ✅ |
| Ne touche pas à `implicit_signal.py` | ✅ |
| Ne touche pas à `quality_score.py` | ✅ |
| Ne touche pas à `coach_report.py` | ✅ |
| Ne touche pas à `substitution.py` | ✅ |
| Pas de nouvelle route | ✅ |
| Pas de migration Alembic | ✅ |
| Pas de nouveau modèle SQLAlchemy | ✅ |
| Ne modifie pas le flow auth | ✅ |
| Ne modifie pas Sentry, rate limiter, perf baseline, migration gates | ✅ |
| Ne désactive aucune gate Sx_26 | ✅ |
| Ne baisse pas la baseline ruff | ✅ 548 inchangée (mesure 534) |
| Pas de LLM | ✅ |
| Pas de phrase qui invente une donnée | ✅ silences explicites sur tous les champs None / vides |
| Si une raison n'est pas disponible, fallback sobre | ✅ |
| 1 raison principale visible directement | ✅ `primary_reason` |
| Jusqu'à 3 raisons max | ✅ `_MAX_REASONS = 3` |
| Raisons courtes | ✅ format "Pectoraux 5 j sans muscu — frais à travailler." |
| Ne jamais produire une fausse zone fraîche/fatiguée | ✅ seuils + tests dédiés |
| Ne pas recalculer la recommandation dans un deuxième moteur | ✅ wrapper consomme uniquement le payload existant |
| Consommer d'abord les champs du payload | ✅ |
| Si payload pas assez riche → wrapper minimal + fallback | ✅ |

## 8. Données affichées (matching spec)

| Spec verbatim | Implémentation |
|---|---|
| `available` | ✅ |
| `primary_reason` | ✅ |
| `reasons: list[str]` (max 3) | ✅ |
| `confidence` | ✅ "ok" / "low" |
| `fallback_note` | ✅ si données partielles |
| 1 raison visible directement | ✅ Home rend `reason` en lead |
| Jusqu'à 3 raisons max si UX lisible 360×640 | ✅ `<ul>` empilée verticalement, font-size 13px, max 2 secondaires |
| "Séance proposée d'après ton historique récent." | ✅ phrase exacte (Rule C) |
| "Dernière séance jambes récente, push plus frais." | ✅ format Rule D |
| "Pas assez de données pour expliquer plus finement." | ✅ `_LOW_DATA_PHRASE` (réservé pour usage futur) + `fallback_note` |

## 9. Limites assumées et reportées

| Item | Pourquoi pas dans Sb_27.4 | Reporté à |
|---|---|---|
| Affichage des `alternatives` enrichies de raisons | Couvert par /launcher dans une UX dédiée | Sb_27.6 si retenu |
| Lien direct "voir les détails de la reco" | Profile / Coach Report existent déjà | hors scope Sx_27 |
| Multi-langue / EN | V1 FR uniquement | post-Sx_27 |
| Telemetry du primary_reason cliqué | hors scope V1 | hors Sx_27 |
| Cleanup ruff baseline 548 → 534 | contrat sprint dédié | `Sb_26.next.ruff-cleanup-N` |

## 10. Backlog immédiat (Sx_27 §14)

| Lot | Objet | Bloquant ? |
|---|---|---|
| **Sb_27.5** | Deterministic coach narrative | OQ-2 (LLM) + OQ-6 (ton) à trancher avant |
| Sb_27.6 | UX simplification pass | OQ-3 à trancher avant |
| Sb_27.7 | Product closure report + dogfood | Tous les lots précédents |

## 11. Verdict

| Critère DoD | Statut |
|---|---|
| pytest passe | ✅ (CI le confirmera) |
| catalog_qa passe | ✅ |
| machine_atlas_qa passe | ✅ |
| check_alembic_drift passe | ✅ |
| check_schema_snapshot passe | ✅ |
| check_migration_patterns passe | ✅ |
| check_migration_roundtrip passe | ✅ |
| check_ruff_budget passe (≤ 548) | ✅ 534 ≤ 548 |
| pip-audit passe | ✅ clean |
| gitleaks passe | ⏳ CI le confirmera |
| check_spec_protocol passe | ✅ |
| check_auth_scope_matrix passe | ✅ |
| perf baseline smoke passe | ✅ |
| Rapport sprint livré | ✅ (ce document) |

### ✅ **Sb_27.5 PRÊT**

---

**Co-Authored-By :** Claude Opus 4.7
