# OPS — Sx_32 Post-Closeout Deploy Readiness

**Type** : OPS / readiness check — **aucun déploiement exécuté**.
**Date** : 2026-07-09
**Verdict readiness** : ✅ **READY FOR CONTROLLED DEPLOY (operator dispatch required)**
**Contexte** : Sx_32 TECHNICALLY CLOSED / FOUNDATION CLOSED. Ce document prépare
une décision de déploiement **contrôlée**, sans la prendre.

---

## 1. État de la branche

| Check | Résultat |
|---|---|
| HEAD local | `3e69706e3483e3cbdc0c7155a22c7107578f11e9` |
| HEAD `origin/claude/sprint-reporting-fitness-app-V7Qr6` | `3e69706` — **identique** |
| Working tree | ✅ **clean** |
| Branche par défaut du repo | `claude/sprint-reporting-fitness-app-V7Qr6` (pas de `main`/`master` séparé) |

Le cycle Sx_32 est **déjà sur la branche par défaut** (aucun merge requis, cf.
rapport merge précédent).

---

## 2. Dernier run CI code (source de vérité)

| Item | Valeur |
|---|---|
| Run | [`29029149976`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29029149976) |
| SHA code | `8559e8b` (dernier commit **avec code** avant les 2 closeouts docs-only) |
| Conclusion | ✅ **success 3/3** — 1865 passed |

Les commits postérieurs (`48e1c9e`, `3e69706`) sont **docs-only** (CI skippée via
`paths-ignore: ['docs/**']`) → ils ne changent pas le code déployable. **L'artefact
de code au HEAD est identique à celui validé par le run vert.**

---

## 3. Workflow de déploiement (inspection READ-ONLY)

Fichier : `.github/workflows/deploy-production.yml` (**non modifié**).

### 3.1 Déclenchement

- **`workflow_dispatch` UNIQUEMENT** (manuel). **Aucun deploy automatique** sur
  push/PR/tag/schedule.
- Inputs :
  - `ref` (requis, **défaut `"main"`**) — ⚠️ `main` **n'existe pas** dans ce repo.
    Il **FAUT** passer explicitement `ref = claude/sprint-reporting-fitness-app-V7Qr6`
    **ou** le SHA `3e69706` (ou `8559e8b`, identique côté code).
  - `skip_smoke` (bool, défaut `false`) — ne PAS activer en déploiement normal.
- `concurrency: production-deploy` (deploys sérialisés, jamais annulés en vol).
- `environment: production`, `permissions: contents: write` (pour pousser le tag deploy).

### 3.2 Étapes (dans l'ordre exécuté)

1. Checkout du `ref` demandé (`fetch-depth: 0`).
2. Résolution du SHA complet.
3. Config SSH (clé + known_hosts depuis secrets).
4. **`deploy_from_github_actions.sh <SHA>`** sur le VPS OVH — délègue à
   `scripts/deploy_prod.sh` côté serveur, qui **gère backup + migrations (alembic)
   + restart service + health checks** (cf. en-tête du script).
5. **`smoke_deploy.sh`** sur le VPS (sauf `skip_smoke`) — refresh backup offline
   puis validation `GET /healthz` (200).
6. Sur succès : tag `deploy/prod/<date>-<sha>` poussé sur origin.
7. Sur échec : erreur annotée + `exit 1` (VPS possiblement en état partiel →
   rollback = re-dispatch avec `ref=<sha précédent>`).

---

## 4. Migrations Sx_32 — sûreté (additive-only)

| Migration | Chaîne | `upgrade()` |
|---|---|---|
| `j1k6e2f3h54` (Sb_32.1 BodyZone/Muscle) | `7i0f5d1e2g43 → j1k6e2f3h54` | `create_table` ×2 + `bulk_insert` (11 zones) |
| `k2l7f3g4i65` (Sb_32.2 ExerciseMuscleMapping) | `j1k6e2f3h54 → k2l7f3g4i65` | `create_table` + `create_index` ×2 + `bulk_insert` (87 lignes) |

- **Aucun `DROP` / `RENAME` / `UPDATE` / `DELETE`** dans les `upgrade()` (les seuls
  `drop_table` sont dans les `downgrade()` de rollback — attendu).
- **Ordre linéaire propre** ; head alembic = `k2l7f3g4i65`.
- `scripts/check_migration_patterns.py` → **OK** (additive-only, non-régressif).
- Sb_32.3 / Sb_32.next / scope-guard : **aucune migration** (service / UI / tests).

### Effet au déploiement

`deploy_prod.sh` exécute `alembic upgrade head` : sur une prod actuellement à
`7i0f5d1e2g43` (Sb_Body_01), il appliquera **dans l'ordre** `j1k6e2f3h54` puis
`k2l7f3g4i65` — 3 tables neuves (`body_zones`, `muscles`, `exercise_muscle_mappings`)
+ backfill. **Aucune table existante modifiée** → risque de migration minimal.

---

## 5. Checklist smoke post-deploy (à exécuter APRÈS un futur GO DEPLOY)

| # | Cible | Attendu |
|---|---|---|
| 1 | `GET /healthz` | 200 (liveness) |
| 2 | `GET /healthz/strict` | 200 (backup frais, DB OK) |
| 3 | `GET /` | 200, home décision |
| 4 | Page démarrer / reprendre séance | 200, CTA présent |
| 5 | Session detail Focus Mode | 200, cockpit carte active |
| 6 | **Worked Area — exercice connu** | zone réelle affichée (ex. Chest Press → **Pectoraux / Triceps**) |
| 7 | **Worked Area — exercice inconnu** | **« À qualifier »**, aucune zone inventée |
| 8 | Logging set (weight/reps) | inputs fonctionnels, soumission OK |
| 9 | Substitution link / flow | non cassé (radios `substituted_name` présents) |
| 10 | `GET /progress` | 200 |
| 11 | `GET /body/intelligence` (si `BODY_INTELLIGENCE_ENABLED`) | 200 |
| 12 | `GET /coach-report` (si activé) | 200 |

**Spécifique Sx_32** : en prod (DB migrée), le Worked Area doit résoudre via
`db_lookup` (attribut `data-resolution-path="db_lookup"` sur les exercices du
catalogue backfillé). Un fallback `substring_fallback` sur un exercice catalogue
signalerait un backfill manquant (à investiguer, non bloquant pour le logging).

---

## 6. Checklist opérateur — GO DEPLOY

Étapes pour un déploiement contrôlé (à faire **manuellement**, sur ta décision) :

1. [ ] Confirmer que le run code `29029149976` est toujours vert (`8559e8b`).
2. [ ] Confirmer HEAD branche = `3e69706` (docs-only au-dessus du code validé).
3. [ ] **Dispatch** `Deploy production` avec **`ref = claude/sprint-reporting-fitness-app-V7Qr6`**
   (ou `ref = 3e69706`). **NE PAS** laisser `ref=main` (inexistant). `skip_smoke = false`.
4. [ ] Surveiller le job (SSH deploy + smoke). Deploys sérialisés (concurrency).
5. [ ] Vérifier le tag `deploy/prod/<date>-<sha>` créé sur succès.
6. [ ] Exécuter la **checklist smoke §5** contre l'URL de prod.
7. [ ] En cas d'échec : re-dispatch avec `ref=<sha précédent>` (rollback documenté).

---

## 7. Verdict

**Verdict :** ✅ **READY FOR CONTROLLED DEPLOY — operator dispatch required.**

- Branche par défaut à jour (`3e69706`), tree clean, code validé (run vert 3/3, 1865 passed).
- Migrations Sx_32 **additive-only**, ordre propre, aucun impact sur les tables existantes.
- Deploy strictement **manuel** (`workflow_dispatch`) — **aucun deploy déclenché par ce readiness**.
- Point d'attention unique : `ref` par défaut du workflow = `main` (inexistant) → passer **explicitement** la branche/SHA au dispatch.

**Aucun déploiement exécuté. Aucun release tag. Sb_32.4 non ouvert. Aucune
restructuration de branche.**

**Prochaine décision explicite** : `GO DEPLOY` (dispatch manuel avec le bon `ref`)
**ou** continuer le dev (`Sb_32.4` / cycle Body Intelligence / autre).
