# CI Quality Budget — Sb_26.1

**Audience :** contributeurs SPIGNOS (humain + agent Claude Code).
**Créé :** 2026-06-01 (sprint Sb_26.1).
**Statut :** verrouille la politique "baseline locked + no new warnings" pour ruff. Doit être maintenu à jour à chaque palier de cleanup.

---

## 1. Pourquoi un budget plutôt qu'un zéro absolu

SPIGNOS a accumulé **~548 warnings ruff legacy** entre Sb_20.2 (478 estimés) et Sb_26.1 (548 mesurés). Une décision "zéro warning" maintenant imposerait un cleanup massif (~92 % auto-fixables, mais ~50 nécessitent review humaine) qui n'a pas de valeur produit immédiate. À l'inverse, garder ruff en advisory laisse dériver la dette.

Compromis : **figer la baseline + interdire toute aggravation**. Toute évolution du code est neutre sur la dette ruff, et des sprints de cleanup ciblés (`Sb_26.next.ruff-cleanup-N`) réduisent la baseline par paliers.

## 2. Modèle "baseline locked + no new warnings"

| Règle | Effet |
|---|---|
| **R1** : `total_ruff_warnings > baseline_warnings` | CI échoue |
| **R2** : `total_ruff_warnings ≤ baseline_warnings` | CI passe |
| **R3** : `total_ruff_warnings < baseline_warnings` | CI passe + warning informatif "ratchet down" |

R3 nécessite une **mise à jour explicite** de `.ruff-budget.json` (acte volontaire dans une PR cleanup).

## 3. Source de vérité — `.ruff-budget.json`

Fichier à la racine du repo, commit obligatoire. Format :

```json
{
  "baseline_warnings": 548,
  "baseline_date": "2026-06-01",
  "baseline_sprint": "Sb_26.1",
  "baseline_sha": "<sha>",
  "model": "baseline_locked_no_new",
  "policy": {
    "fails_if_total_above_baseline": true,
    "fails_if_new_warnings_above_zero": true,
    "allows_total_decrease": true
  },
  "top_rules_at_baseline": {
    "UP017": 147,
    "I001": 145,
    "UP045": 127,
    "F401": 67,
    "...": "..."
  }
}
```

## 4. Script de check — `scripts/check_ruff_budget.py`

| Usage | Effet |
|---|---|
| `python scripts/check_ruff_budget.py` | Check baseline. Exit 0 OK, exit 1 si dépassement. |
| `python scripts/check_ruff_budget.py --measure` | Affiche le total actuel sans gate (debug). |

Le script lit `.ruff-budget.json`, exécute `ruff check . --output-format=json`, compare et imprime un récap.

## 5. Workflow CI (job `lint`)

À partir de Sb_26.1, le job `lint` :

| Step | Mode | Conséquence |
|---|---|---|
| `ruff format --check .` | advisory | warning sur PR, pas bloquant |
| `python scripts/check_ruff_budget.py` | **required** | échec si total > baseline |
| `bandit -r app/ -ll -f screen` | **required** | échec si Med/High signalé |
| `actionlint` | **required** | échec si workflow syntactic error |
| `shellcheck -S warning` | **required** | échec sur scripts/*.sh warning+error |
| ruff JSON + bandit JSON pour Sonar | advisory | toujours upload artifact |

## 6. Procédure pour passer un palier (baisser la baseline)

Quand un sprint cleanup réduit la dette :

1. Ouvrir un sprint dédié `Sb_26.next.ruff-cleanup-N` (pas mélanger avec un sprint feature)
2. Appliquer les fixes (ex : `ruff check --fix --select UP017 .` pour 147 warnings auto-fixables)
3. Vérifier que pytest passe toujours après les fixes
4. Mesurer le nouveau total : `python scripts/check_ruff_budget.py --measure`
5. Mettre à jour `.ruff-budget.json` :
   - `baseline_warnings` → nouvelle valeur
   - `baseline_date` → date du jour
   - `baseline_sprint` → Sb_26.next.ruff-cleanup-N
   - `top_rules_at_baseline` → re-mesurer
6. Commit message explicite : `chore(ruff): ratchet baseline 548 → 401 (Sb_26.next.ruff-cleanup-1, UP017 fixed)`
7. PR review humaine obligatoire (pas auto-merge)

## 7. Procédure pour bumper la baseline (cas exceptionnel)

**Interdit en sprint feature.** Un warning ne peut JAMAIS être ajouté sans correction immédiate, sauf si :

- Un nouveau type de warning sort dans une version récente de ruff
- ET la règle est légitimement applicable à du code existant qui ne peut pas être corrigé V1
- ET un amendement Sx_xx documente la décision

Procédure :

1. Mesurer le nouveau total après bump de ruff
2. Documenter la justification dans un amendement Sx_xx
3. Bumper `.ruff-budget.json` avec :
   - `baseline_warnings` → nouvelle valeur
   - `baseline_date` → date du jour
   - `_doc` → pointeur vers l'amendement
4. PR review humaine + validation explicite du bump

## 8. Évolutions futures envisagées

| Évolution | Sprint cible |
|---|---|
| Check par fichier modifié (interdire un nouveau warning dans un fichier touché par la PR) | Sb_26.next |
| Lock ruff version exacte dans `requirements.txt` (pour éviter de bumper la dette sans contrôle) | Sb_26.next |
| Auto-bump baseline en cas de cleanup détecté (warning informatif → suggestion auto-PR) | Sb_27+ |
| Distinct budgets par paquet (`app/`, `tests/`, `scripts/`) | Sb_27+ |

## 9. Backlog des paliers de cleanup

État au 2026-06-01 (baseline 548) :

| Sprint | Cible | Effort | Nouvelle baseline visée |
|---|---|---|---|
| `Sb_26.next.ruff-cleanup-1` | UP017 (147) | 2h | ≈ 401 |
| `Sb_26.next.ruff-cleanup-2` | I001 (145) | 1h | ≈ 256 |
| `Sb_26.next.ruff-cleanup-3` | UP045 (127) | 2h | ≈ 129 |
| `Sb_26.next.ruff-cleanup-4` | F401 (67) — review prudent | 3h | ≈ 62 |
| `Sb_26.next.ruff-cleanup-5` | E402, UP037, F541, E702, F841, C901 reste (~52) | 2h | < 20 |
| **Cible long terme** | **0 warning maintenable** | ~10h cumulés | **0** |

## 10. FAQ

> Pourquoi pas zéro warning aujourd'hui ?

Parce que ~92 % des 548 warnings sont auto-fixables triviaux (UP017, I001, UP045) — leur correction n'apporte rien à la valeur produit immédiate et risque de polluer un diff de feature sprint. On les corrige dans des sprints dédiés et tracés.

> Pourquoi pas une baseline plus haute (genre 600) avec un coussin de sécurité ?

Parce qu'un coussin invite à la dérive silencieuse. Le modèle "no new" force à acter chaque ajout.

> Et si un sprint feature corrige incidemment 5 warnings ?

Tant mieux — le script affiche un message "ratchet down" sans échouer. Le contributeur peut updater `.ruff-budget.json` dans la même PR, ou laisser au prochain sprint cleanup de le faire.

> Et si ruff bump version et ajoute 20 nouveaux warnings types ?

Mesurer, documenter dans un amendement, bumper `.ruff-budget.json` explicitement. Pas de bump silencieux.

> Et SonarCloud dans tout ça ?

Inchangé. Sonar reste required avec sa propre Quality Gate (Coverage, ratings A, hotspots). Le budget ruff est une couche complémentaire orientée style + lint Python, alors que Sonar arbitre la qualité globale + sécurité + maintainability.
