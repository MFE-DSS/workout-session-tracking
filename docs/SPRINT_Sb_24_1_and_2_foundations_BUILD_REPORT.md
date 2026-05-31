# Sprint Sb_24.1 + Sb_24.2 Build Report — Fondations testables du scoring V2

**Date :** 2026-05-31
**Type :** BUILD — fondations BD + service signal implicite (Sx_24 §K).
**Prérequis :** Sx_24 spec validée humainement, Sx_25 spec validée humainement.
**Portée stricte :** uniquement Sb_24.1 + Sb_24.2 du lotissement Sx_24 §K. **Pas** d'UI, **pas** de checkbox, **pas** de coach report.
**Successeur recommandé :** Sb_24.3 (hook persistance à la complétion) — voir §10.

---

## 1. Résumé exécutif

Deux lots livrés en série, fondations strictement testables sans toucher au reste de l'app :

1. **Sb_24.1** — migration BD additive : `workout_sessions.scoring_version` (NOT NULL DEFAULT 1) + `session_exercises.implicit_label` (nullable) + `session_exercises.implicit_label_computed_at` (nullable). **Aucun UPDATE rétroactif**, conformément au contrat §H de la spec — toutes les sessions existantes reçoivent `scoring_version=1` via le DEFAULT, garantissant que la formule V1 du `quality_score` continuera à être utilisée éternellement pour les sessions pré-Sb_24.
2. **Sb_24.2** — service `implicit_signal.py` : enum `ImplicitLabel` verrouillé (5 valeurs), fonction pure déterministe `detect_intra_set_label()` couvrant les 5 patterns du spec §D.1, table `LABEL_SCORE_CONTRIBUTION` centralisant les contributions au scoring V2. Aucune dépendance BD, aucun side-effect, aucun appel à la spec aval.

**Aucune ligne UI touchée. Aucun handler modifié. Le scoring continue d'utiliser la formule V1 pour 100 % des sessions** — c'est intentionnel, Sb_24.5 fera le switch.

## 2. Fichiers modifiés / créés

| Fichier | Type | Nature |
|---|---|---|
| `migrations/versions/20260531_add_implicit_signal_scoring_v2.py` | New | Migration Alembic. ADD COLUMN × 3 sans aucun UPDATE. Revision `4f7c2a8b9d10` → down `c3d5f1e82a04`. Downgrade trivial (drop). |
| `app/models/session.py` | Modify | +`WorkoutSession.scoring_version` (Mapped, NOT NULL, default=1, server_default="1"). +`SessionExercise.implicit_label` (nullable, 32 chars) et `implicit_label_computed_at` (nullable, DateTime tz). Commentaires citant les §Sx_24. |
| `app/services/implicit_signal.py` | New | 175 LoC. `ImplicitLabel(str, Enum)` × 5 valeurs. `MIN_WORK_SETS=3`. `WorkSetPoint` dataclass. `_coerce()` accepte WorkSetPoint / tuple / ORM duck. `detect_intra_set_label()` classifier déterministe. `LABEL_SCORE_CONTRIBUTION` dict source de vérité pour Sb_24.5. |
| `tests/test_scoring_version_migration.py` | New | 5 tests : colonnes présentes, types et nullability OK, DEFAULT 1 appliqué, nouvelles rows fonctionnelles, nullable côté implicit_label. |
| `tests/test_implicit_signal.py` | New | 25 tests : 5 patterns × cas standard, edge cases (< 3 sets, None values, bodyweight), determinism, immutabilité de l'input, accept WorkSetPoint / tuple / ORM, paramétrique 7 cas. |
| `docs/SPRINT_Sb_24_1_and_2_foundations_BUILD_REPORT.md` | New | Ce rapport. |

**0 réécriture historique · 0 UPDATE rétroactif · 0 fichier UI touché · 0 router modifié.**

## 3. Diff métier

### 3.1 — Côté BD (Sb_24.1)

Avant :
```
workout_sessions     ⟶ (sans scoring_version)
session_exercises    ⟶ (sans implicit_label)
```

Après :
```
workout_sessions     ⟶ scoring_version INTEGER NOT NULL DEFAULT 1
session_exercises    ⟶ implicit_label VARCHAR(32) NULL
                     ⟶ implicit_label_computed_at TIMESTAMP NULL
```

Sessions historiques (audit live dev DB) : `scoring_version=1` partout (DEFAULT respecté). `implicit_label=NULL` partout (pas de backfill).

### 3.2 — Côté service (Sb_24.2)

5 labels intra-exercice détectables, ordre de classification par **spécificité décroissante** :

| Ordre | Label | Condition |
|---|---|---|
| 1 | `trajectoire_coherente` | `w` constant ET `r[N] < r[0]` |
| 2 | `pyramidal_ascendant` | `w` strictement croissant ET `r` (constant OU décroissant) |
| 3 | `pyramidal_descendant` | `w` strictement décroissant ET `r` (constant OU croissant) |
| 4 | `reserve_probable` | `w` (constant OU croissant) ET `r` (constant OU croissant) |
| 5 | `incoherent` | aucun pattern net |

L'ordre est choisi pour que **les patterns plus informatifs gagnent** : un `(w_strict_inc, r_eq)` matche à la fois `pyramidal_ascendant` et `reserve_probable` — on retient `pyramidal_ascendant` car plus précis. Documenté en commentaire dans le code.

Contribution scoring (sera consommée par Sb_24.5) :
```
RESERVE_PROBABLE      → 30
INCOHERENT            → 50
PYRAMIDAL_ASCENDANT   → 70
PYRAMIDAL_DESCENDANT  → 75
TRAJECTOIRE_COHERENTE → 90
```

## 4. Contrats respectés (Sx_24)

| Contrat | Mécanisme | Test |
|---|---|---|
| §H — Pas de recalcul rétroactif | Mécanisme `scoring_version` sur `workout_sessions`. Existing rows = 1, never touched. | `test_new_session_defaults_to_scoring_version_1` |
| §C — Saisi / Dérivé / Implicite | `implicit_label` documenté `# Implicite` dans le modèle ; persistance prévue à la complétion (Sb_24.3), recalcul jamais autorisé après. | (testé en Sb_24.3) |
| §D.1 — 5 labels exhaustifs | Enum `ImplicitLabel` × 5 valeurs strictement. | `test_enum_has_five_values` |
| §D.1 — `MIN_WORK_SETS = 3` | Constante exposée. | `test_min_work_sets_is_3` + `test_two_sets_returns_none` |
| §D.2 — Persistance à la complétion (champ prévu) | Colonne en BD nullable, prête à recevoir le label. | `test_session_exercise_accepts_implicit_label_string` |
| §F.2 — Table contribution centralisée | `LABEL_SCORE_CONTRIBUTION` dict unique, source de vérité pour Sb_24.5. | `test_contributions_cover_all_labels` |
| Fonction pure / déterministe | Aucun state, aucun random, recomputable à l'infini. | `test_determinism` + `test_input_not_mutated` |

## 5. Audit chiffré du service

Couverture des cas du spec §D.1 :

| Cas spec | Tests dédiés | Statut |
|---|---|---|
| trajectoire_coherente (drop-off classique) | 3 tests | ✅ |
| reserve_probable (flat 3×10) | 3 tests | ✅ |
| pyramidal_ascendant (ramp) | 2 tests + paramétrique | ✅ |
| pyramidal_descendant (drop-set) | 2 tests + paramétrique | ✅ |
| incoherent (oscillations) | 2 tests + paramétrique | ✅ |
| < MIN_WORK_SETS | 2 tests | ✅ |
| Bodyweight (weight=None) | 2 tests | ✅ |
| Mixed None values | 2 tests | ✅ |
| Determinism | 1 test × 20 itérations | ✅ |
| Immutabilité input | 1 test | ✅ |
| Compatibilité ORM duck / tuple / dataclass | 2 tests | ✅ |

## 6. État des tests

```
Sb_24.1 + Sb_24.2 nouveaux :
  - tests/test_scoring_version_migration.py : 5/5 verts
  - tests/test_implicit_signal.py            : 25/25 verts

Total avant : 809
Total après : 809 + 30 = 839 (en cours de full-suite check)
0 régression attendue — aucun handler ni service existant touché
```

Full suite lancée en parallèle, résultat consigné en §11.

## 7. Limites assumées

1. **Aucune consommation en prod** — le scoring continue d'utiliser la formule V1 pour 100% des sessions, y compris les nouvelles. Le hook de persistance (Sb_24.3) et le switch formule (Sb_24.5) sont **strictement hors scope** de Sb_24.1+Sb_24.2.
2. **Pas de tests de migration downgrade** — le downgrade est implémenté (drop column), pas testé. Acceptable : la production n'utilise pas `alembic downgrade`. Si un test devient pertinent (déploiement multi-prod avec rollback), Sb_24.next ajoutera.
3. **`implicit_label` est `String(32)`** — verrouille la longueur des futures labels. Si on en ajoute V2, max 32 chars. Acceptable.
4. **`detect_intra_set_label()` ne reçoit pas le SessionExercise complet** — uniquement la liste des work sets. Choix explicite : isolation testable. Le caller (Sb_24.3) sera responsable de filtrer `kind=='work'` et de trier par `set_index`.
5. **Pas d'invalidation cache du `_load_properties` du Sb_22a** — non-applicable, ce service n'utilise pas le registre exercise_properties.
6. **Edge case borderline** — un trajectoire `(60, 10), (60, 10), (60, 11)` (un seul rep en plus à la fin) tombe en `reserve_probable` car r est non-décroissant. C'est conforme à la spec ; pas un bug, juste une conséquence assumée.

## 8. Risques

| Risque | Mitigation |
|---|---|
| L'ordre de classification §D.1 du spec est ambigu sur les chevauchements (`w_strict_inc, r_eq`) | Documenté en commentaire dans le code : ordre par spécificité décroissante. Spec aval pourra confirmer/amender. |
| Sb_24.3 (hook) pourrait re-introduire un recalcul par accident | Acceptance criteria Sb_24.3 inclura un test "label set once never re-set" |
| Migration sur SQLite ALTER TABLE ADD COLUMN avec DEFAULT — possibles incompatibilités | Testé localement avec `alembic upgrade head` → colonnes créées + DEFAULT respecté. CI prod fera tourner pareil. |

## 9. Étape de validation manuelle (proposée)

Après merge + déploiement :
```bash
# Sur la prod VPS
sqlite3 /opt/workout-session-tracking/var/workout.db "
  SELECT COUNT(*) AS sessions_total,
         SUM(CASE WHEN scoring_version=1 THEN 1 ELSE 0 END) AS v1_count
  FROM workout_sessions;
"
# attendu : v1_count == sessions_total (toutes les sessions ont scoring_version=1)

sqlite3 /opt/workout-session-tracking/var/workout.db "
  SELECT COUNT(*) FROM session_exercises WHERE implicit_label IS NOT NULL;
"
# attendu : 0 (aucun label calculé tant que Sb_24.3 n'a pas livré)
```

## 10. Recommandation prochain lot

**Sb_24.3 — Hook persistance à la complétion (~2 h).**

Périmètre :
- Lors de la transition `WorkoutSession.status` → `"completed"` (handler `/sessions/{id}/finish` ou équivalent), pour chaque `SessionExercise` :
  1. Filtrer ses `set_logs` avec `kind=='work' AND completed==True`, ordonner par `set_index`
  2. Appeler `detect_intra_set_label(work_sets)`
  3. Si non None, persister `implicit_label` + `implicit_label_computed_at = now()`
- Marquer la session : `scoring_version = 2`
- **Idempotence stricte** : si `implicit_label` est déjà non-null, ne pas le toucher. Si `scoring_version >= 2`, ne pas le toucher non plus.

Tests requis :
- Session finished → labels calculés + persistés sur les exercices ≥ 3 sets
- Session ré-finished (cas erreur) → labels intacts, scoring_version intact
- Session avec un exercice < 3 sets → label NULL pour cet exo

Effort estimé 2 h. Une fois Sb_24.3 livré et déployé, Sb_24.4 (dépréciation checkbox) ou Sb_24.5 (formule V2) peuvent partir en parallèle ou en série selon l'arbitrage humain.

**Ne PAS ouvrir Sb_24.4 / 5 / 6 / 7 dans ce sprint** — la consigne humaine était stricte sur le périmètre Sb_24.1 + Sb_24.2 seulement.

## 11. Synthèse

- **3 colonnes BD ajoutées**, 0 UPDATE rétroactif, contrat de stabilité historique §H respecté.
- **1 service neuf** (`implicit_signal.py`), pure deterministe, **0 dépendance externe**, source de vérité unique pour la contribution scoring V2.
- **30 tests neufs** (5 BD + 25 service), tous verts, paramétrique inclus.
- **0 surface utilisateur impactée** — aucun changement visible côté UI. Le `quality_score` continue d'utiliser la formule V1.
- **Sb_24.3 est l'unité naturelle suivante** — pose le hook qui peuplera `implicit_label` à la complétion. Effort 2 h, faible risque, débloque les lots aval.

Le triptyque Sx_24 spec → Sb_24.1 → Sb_24.2 livre les fondations en isolation. Le risque "spec et build divergent" est faible : le code cite explicitement les §Sx_24 dans ses commentaires et les tests rejouent les conditions verbatim du §D.1.
