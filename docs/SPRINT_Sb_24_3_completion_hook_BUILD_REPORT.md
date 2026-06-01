# Sprint Sb_24.3 Build Report — Completion Hook (implicit label persist + scoring_version=2)

**Date :** 2026-06-01
**Type :** BUILD — lot du milieu de Sx_24 (§K Sb_24.3).
**Prérequis :** Sb_24.1 + Sb_24.2 livrés.
**Portée stricte :** uniquement le hook de complétion. Pas de UI, pas de quality_score V2 (Sb_24.5), pas de checkbox.

---

## 1. Résumé exécutif

Au moment où une session passe en `status="completed"` (action="end" sur `POST /sessions/{id}`), une nouvelle fonction `_persist_implicit_labels_on_completion(session)` :

1. Itère sur `session.session_exercises`
2. Pour chacun, filtre les `work sets` (`kind=="work" AND completed`), trie par `set_index`
3. Appelle `detect_intra_set_label()` (Sb_24.2)
4. Si non-None et le SE n'a pas encore de label → persiste `implicit_label` + `implicit_label_computed_at = now()`
5. Bumpe `session.scoring_version` de 1 → 2 (jamais l'inverse)

**Idempotence forte** : un SE déjà labellé n'est plus jamais touché, peu importe combien de fois la session est reopen/re-end. `scoring_version` est monotone (jamais downgrade au reopen).

## 2. Contrats respectés

| Contrat Sx_24 | Mécanisme | Test |
|---|---|---|
| §C — Implicite = figé à la complétion | `if se.implicit_label is not None: continue` | `test_re_finish_keeps_first_label_intact` |
| §D.2 — Persisté une seule fois | Idempotence sur `implicit_label is None` | idem |
| §H — `scoring_version` monotone | `if session.scoring_version < 2: session.scoring_version = 2` | `test_scoring_version_never_downgraded_on_reopen` |
| §D.1 — `MIN_WORK_SETS=3` | hérité de `detect_intra_set_label` | `test_completion_no_label_for_under_3_work_sets` |
| Pas de retro recompute | Labels passés intacts | `test_re_finish_keeps_first_label_intact` (mutation après → label inchangé) |

## 3. Fichiers modifiés / créés

| Fichier | Type | Nature |
|---|---|---|
| `app/routers/sessions.py` | Modify | +`_persist_implicit_labels_on_completion()` (~25 LoC). Appel dans le handler `POST /sessions/{id}` juste après `status = COMPLETED`, avant `db.commit()`. |
| `tests/test_implicit_label_persistence.py` | New | 6 tests E2E via le vrai handler : happy path / <3 sets → None / reserve_probable / idempotence / scoring_version monotone / multi-exercise. |
| `docs/SPRINT_Sb_24_3_completion_hook_BUILD_REPORT.md` | New | Ce rapport. |

**0 fichier de modèle touché · 0 nouvelle migration · 0 UI changée.**

## 4. État des tests

```
852 tests passing in 251.50s (vs 846 avant — +6, 0 régression)
  - tests/test_implicit_label_persistence.py — 6/6 verts (E2E via TestClient)
  - Sb_24.1 + Sb_24.2 — 37 tests inchangés
```

## 5. Comportement post-Sb_24.3 sur prod

- **Sessions historiques** (`scoring_version=1`) : intactes — pas de label, formule scoring V1 forever (Sb_24.5 n'est pas encore en place mais le contrat est posé).
- **Nouvelles sessions terminées après ce déploiement** : `scoring_version=2`, chaque exercice ≥3 sets travaillés reçoit son label persisté en BD.
- **Visibilité utilisateur** : aucune. Aucune UI n'affiche encore les labels (Sb_24.6 le fera). C'est silencieux par design — on accumule la donnée avant de la rendre visible.

## 6. Limites assumées

1. **Pas de recalcul rétroactif** — voulu (Q4 spec). Si l'utilisateur a fait 50 sessions avant ce déploiement et les revisite, elles restent sans label.
2. **Hook lazy load** — `session.session_exercises` et `se.set_logs` sont lazy-loadés au moment du hook. C'est correct mais ajoute quelques requêtes au commit de fin de séance. Acceptable car la transition end est rare.
3. **Pas de tâche batch pour backfill** — décision produit Q4. On ne backfille pas l'historique même si techniquement possible.
4. **`scoring_version=2` posé mais formule V2 pas encore branchée** — Sb_24.5 ferme cette boucle. Entre-temps, `compute_session_quality()` continue d'utiliser la formule V1 pour les deux versions (compatible car la V1 ne dépend pas de scoring_version).

## 7. Recommandation prochain lot

**Sb_24.4 — dépréciation checkbox "fait" (~3h).**

Périmètre :
- Retirer l'input checkbox du form de saisie (template session_detail.html)
- Dériver `set_log.completed = (weight_kg is not None) OR (reps is not None)` côté handler `POST /sessions/{id}/exercises/{xid}`
- Tests : POST sans weight/reps → completed=False ; avec weight → True ; avec reps → True

Effort 3h. Risque faible — touche seulement le handler de saisie de sets et un template.

OU si tu préfères, **Sb_24.5 — formule scoring V2** (~3h) en parallèle de Sb_24.4 — c'est indépendant (Sb_24.5 lit `scoring_version` qui est déjà posé par Sb_24.3).

## 8. Synthèse

- 1 fonction ajoutée (25 LoC), 1 ligne d'appel dans le handler de fin de séance.
- 6 tests E2E qui passent toutes les transitions (end / reopen / re-end / multi-exercise).
- Idempotence vérifiée — un label ne bouge plus jamais après sa première écriture.
- `scoring_version` posé sur les nouvelles sessions, prêt à être consommé par Sb_24.5.

Fondations Sb_24.1 → 24.2 → 24.3 complètes. La consommation visible commence avec Sb_24.5 ou Sb_24.6.
