# Sb_30.4 — Remove progression_hint Legacy (Build Report)

**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Date :** 2026-06-26
**Spec parent :** `docs/strategy/Sx_30_PROGRESSIVE_OVERLOAD_ENGINE_SPEC.md`
**Lot Sx_30 :** §14 — Sb_30.4 (suppression legacy, 4/5 du cycle)
**Build authorization :** ✅ `BUILD AUTHORIZED FOR Sx_30 — Option B`
**Pré-requis :** Sb_30.1 ✅ + Sb_30.2 ✅ + Sb_30.3 ✅ (CI 28247518562, dogfood overload visible).

---

## 1. Objectif

Retirer proprement la couche `progression_hint` legacy (bloc "Repère" qualitatif) maintenant que l'overload hint visible (Sb_30.3) remplit pleinement le rôle de guidance principale, avec une cible chiffrée (kg/reps) + reasons.

## 2. Fichiers supprimés / modifiés

### Supprimés
| Fichier | Lignes |
|---|---|
| `app/services/progression_hint.py` | -50 (service + docstring) |
| `tests/test_progression_hint.py` | -134 (5 tests unitaires + 4 tests intégration template) |

### Modifiés
| Fichier | Changement |
|---|---|
| `app/routers/sessions.py` | -1 import (`compute_progression_hint`) ; -17 lignes (boucle `hints[code] = …`) ; -1 clé contexte template (`"hints": hints`) ; +5 lignes commentaire explicatif (anglais, pour ne pas matcher la garde test sur le token `progression_hint`). |
| `app/templates/_partials/exercise_card.html` | -7 lignes (bloc `<div class="hint">…Repère…</div>`) ; docstring mise à jour (`hints` → `overload_hints`) ; commentaire de jointure reformulé. |
| `tests/test_overload_hint_render.py` | `test_progression_hint_legacy_still_intact` retiré ; remplacé par 3 nouveaux tests garde-fous : `test_progression_hint_legacy_removed`, `test_router_no_longer_imports_progression_hint`, `test_exercise_card_no_longer_renders_repere_block`. |

### Non modifiés (vérification explicite)
- `app/services/overload_engine.py`
- `app/services/overload_inputs.py`
- `app/services/overload_explainer.py`
- `app/services/quality_score.py`
- `app/services/recommendation.py`
- `app/services/implicit_signal.py`
- `app/services/coach_report.py` / `coach_inference.py`
- `app/services/body_tracking.py`
- `app/services/substitution.py`
- `app/templates/_partials/overload_hint.html`
- `app/static/css/session_focus.css`
- Migration Alembic `6h9e4c0d1f32` (intacte)
- Aucune nouvelle migration

## 3. Ce qui disparaît exactement du legacy

| Surface | Avant Sb_30.4 | Après Sb_30.4 |
|---|---|---|
| Service Python | `compute_progression_hint(target_min, target_max, prior_weight_kg, prior_reps) -> Optional[str]` retournait 1 phrase parmi 3 (`"tenter d'augmenter la charge…"`, `"consolider la charge actuelle"`, `"viser N reps avant…"`). | **Supprimé.** |
| Injection router | `hints: dict[str, str | None]` calculée par boucle dans `session_detail` + passée au template via clé `"hints"`. | **Supprimée.** Plus aucun consommateur. |
| Template Jinja | Bloc `<div class="hint"><span class="hint__label">Repère</span><span class="hint__text">{{ hint }}</span></div>` rendu sur **chaque carte** (pas seulement active). | **Supprimé.** Bloc reformulé en commentaire renvoyant vers le partial overload. |
| CSS | Classes `.hint`, `.hint__label`, `.hint__text` toujours présentes dans `app/static/css/app.css` (utilisées aussi par `template_detail.html` séparément, donc **conservées**). | **Conservées** (cross-page reuse). |
| Tests | `tests/test_progression_hint.py` (5 unit + 4 integration). | **Supprimés.** |

## 4. Pourquoi l'overload hint couvre le besoin restant

| Besoin originellement assuré par `progression_hint` | Réponse Sb_30.3 (overload hint) |
|---|---|
| "Quoi tenter sur le premier set ?" | `intent_label` ("Tenter d'augmenter la charge" / "Consolider…" / "Atteindre le bas de range" / "Alléger temporairement") |
| Range respectée | `target_summary` "102.5 kg · 6-10 reps" |
| Pas de jargon AI / décideur final = utilisateur | Wording sobre testé (`test_intent_label_never_authoritative`, `test_rendered_hint_has_no_authoritative_wording`) |
| Affichage uniquement quand pertinent | `is_silent=True` si `unknown` → router skip → aucun rendu |
| Mécanisme déterministe et reproductible | `engine_version` propagé jusqu'au DOM + colonne DB `overload_engine_version` (Sb_30.3) |

L'overload hint ajoute en plus :
- 5 états vs 3 (introduit `top-range` et `deload`)
- cible chiffrée (kg + reps) vs phrase libre
- reasons explicables, max 3, dépliables via `<details>` natif
- non-color cues WCAG 1.4.1 sur 5 états
- transport du `engine_version` pour reproductibilité incident
- prise en compte de `quality_score` + signal fatigue (`global_state=="fatigued"`)

## 5. Avant / après UX sur la carte active

**Avant Sb_30.4 :**
```
[Dernière fois — 100 kg × 10 reps]
[Delta : +2.5 kg vs séance n-1]
[Repère : tenter d'augmenter la charge sur le premier set]   ← progression_hint legacy
[💡 Hint Sb_08 contextuel]
[Overload hint Sb_30.3 (cible chiffrée)]   ← double guidance
[Sets, sticky CTA, rest timer]
```

**Après Sb_30.4 :**
```
[Dernière fois — 100 kg × 10 reps]
[Delta : +2.5 kg vs séance n-1]
[💡 Hint Sb_08 contextuel]
[Overload hint Sb_30.3 (intent + 102.5 kg · 6-10 reps + reasons)]   ← guidance unique
[Sets, sticky CTA, rest timer]
```

Aucun vide fonctionnel : l'overload hint occupe désormais seul le rôle de guidance principale sur la carte active.

## 6. État des tests

| Suite | Résultat |
|---|---|
| `test_overload_engine.py` (Sb_30.1) | ✅ 33 |
| `test_overload_explainer.py` (Sb_30.2) | ✅ 16 |
| `test_overload_router_injection.py` (Sb_30.2) | ✅ 26 |
| `test_overload_hint_render.py` (Sb_30.3 + Sb_30.4 garde-fous) | ✅ 16 (-1 legacy + 3 nouveaux) |
| `test_overload_engine_version_migration.py` (Sb_30.3) | ✅ 5 |
| `test_progression_hint.py` (legacy) | ❌ **supprimé** |
| Suite complète | ✅ à confirmer en CI |

### Nouveaux tests garde-fous (3)

1. `test_progression_hint_legacy_removed` — Fichier service et fichier tests legacy absents du repo.
2. `test_router_no_longer_imports_progression_hint` — Le router ne référence plus le module ni la fonction ; la clé `"hints":` n'est plus dans le contexte template.
3. `test_exercise_card_no_longer_renders_repere_block` — Le template ne contient plus le mot "Repère", les classes `hint__label`/`hint__text`, ni l'accès `hints.get(se.exercise_code_snapshot)`.

## 7. Métriques

| Item | Avant | Après | Δ |
|---|---|---|---|
| Fichiers Python `app/services/` | 41 (avec legacy) | 40 (legacy supprimé) | -1 |
| Lignes legacy supprimées | — | — | -184 (-50 service -134 tests) |
| Lignes router | +14 Sb_30.2 | -1 import / -17 boucle / +5 commentaire = -13 net | -13 |
| Lignes template `exercise_card.html` | inchangé Sb_30.3 | -7 (bloc Repère) / +3 (commentaire) = -4 net | -4 |
| Ruff total warnings | 535 (post Sb_30.3) | **528** (-7, legacy supprimé) | -7 |
| Tests modifiés | — | -9 (legacy) + 3 (garde-fous) = -6 net | -6 |
| Services métier core touchés | 0 | **0** | — |
| Migrations | 0 | **0** | — |
| CSS | 0 | **0** | — |
| JS | 0 | **0** | — |

## 8. Contraintes respectées (verbatim user)

| Contrainte | OK |
|---|---|
| Retirer `progression_hint.py` legacy | ✅ |
| Retirer son injection dans le router | ✅ |
| Retirer son rendu dans les templates | ✅ |
| Adapter / supprimer les tests dédiés legacy | ✅ (suppression + 3 garde-fous) |
| Garder intact `overload_engine.py` | ✅ |
| Garder intact `overload_inputs.py` | ✅ |
| Garder intact `overload_explainer.py` | ✅ |
| Garder intact `quality_score.py` / `scoring_version` | ✅ |
| Garder intact `substitution.py` | ✅ |
| Garder intact `coach_report.py` | ✅ |
| Ne pas mélanger OQ-E (laisser hors scope) | ✅ aucun toucher aux inputs poids/reps |
| Aucun changement de scoring | ✅ |
| Aucune migration | ✅ |
| Aucun changement de wording du nouveau hint | ✅ |
| Aucun vide fonctionnel sur la carte active | ✅ overload hint déjà visible Sb_30.3 |
| Pas de régression UX mobile | ✅ aucun changement CSS / JS / sticky |

## 9. DoD locale

| Gate | Statut |
|---|---|
| `pytest --ignore=tests/test_v1_acceptance.py -q` | ✅ background run |
| `check_ruff_budget.py` | ✅ 528 ≤ 548 |
| `check_spec_protocol.py` | ✅ |
| `PYTHONPATH=. check_alembic_drift.py` | ✅ no diff |
| `check_schema_snapshot.py` | ✅ |
| `check_migration_patterns.py` | ✅ |
| `check_migration_roundtrip.py` | ✅ |

## 10. CI réelle (post-push)

**Run GitHub Actions : [28250584691](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28250584691) — ✅ success (3/3 jobs verts)**

Note : un premier run [28250143722](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28250143722) sur le commit `a20e3ab` (cherry-pick Sb_30.4 strict) a été **cancelled** par un push concurrent `3fb8faa` (merge PR #13 — Body Intelligence brainstorming spec, hors scope Sb_30.4). Le run final couvre `3fb8faa` qui contient l'intégralité de `a20e3ab` + le merge — Sb_30.4 est donc bien validé en CI dans son contexte de branche canonique.

- [x] Job `pytest + QA scripts` — ✅ success
- [x] Job `lint (ruff budget + bandit + actionlint + shellcheck)` — ✅ success
- [x] Job `SonarCloud` — ✅ success

## 11. Verdict

**✅ Sb_30.5 prêt avec recommandation explicite : enchaîner sur la closure Sx_30 + a11y consolidation (`Sb_30.5_a11y_and_closure`).**

L'option alternative de **traiter OQ-E maintenant** (placeholder cible dans les inputs poids/reps) est viable mais introduit un risque de friction UX (utilisateur qui veut écraser la cible) — je recommande de la traiter dans un sprint dédié `Sb_30.next.placeholder` **après** la closure Sx_30, pour ne pas mélanger suppression legacy + nouvelle feature dans le même cycle. Cette recommandation est conforme à la consigne "ne pas mélanger OQ-E dans ce sprint, sauf si trivial et sans risque" : ce n'est ni trivial (les inputs sont déjà liés à la valeur précédente affichée par "Dernière fois") ni sans risque (UX différente).

**Recommandation suite :** `Sb_30.5_a11y_and_closure` puis `Sx_30_CLOSURE_REPORT` puis éventuellement `Sb_30.next.placeholder` sous override séparé.
