# SPRINT Sb_OPS.repo-triage-01 — Triage du bruit repo (RAPPORT)

**Base canonique :** `7eabb25` · **Branche :** `sb/ops-repo-triage-01` · **Tier :** ISOLATED (docs uniquement ; les cleanups sont des opérations git, pas des commits de contenu)
**Livré sous le protocole agentique** (`CLAUDE.md §4`) : `GO BUILD` → audit → exécution du sous-ensemble **non-risqué** → plan opérateur pour le reste.

## 1. Méthode

Audit de l'état du repo avant d'ouvrir le prochain build produit : PRs ouvertes, branches (statut de merge vs canonique), worktrees (propreté + rattachement). **Règle d'exécution** : ne supprimer un worktree que s'il est **mergé dans la canonique ET 100 % propre** (aucun fichier modifié/non-suivi = zéro contenu unique à perdre), **hors** worktrees explicitement protégés (références géométrie/source), **hors** `ops-agent-autonomy-01` (interdit), **hors** branche d'une PR ouverte. Tout ce qui déclenche une condition d'arrêt (dirty · non mergé · fichiers uniques · ownership flou · référence géométrie · PR #46 · dependabot) part en **décision opérateur**.

## 2. Inventaire (avant)

- **11 worktrees** · **11 PRs ouvertes** (#46 ASSET eval harness + **10 dependabot** #1-#12/#45) · branches locales mergées (7 `work/*`) et non mergées (5 orphelines `sb-body-*`/`sb-ci-*`/`sb-31-*` + `spec/sx-custom-program-01` + PR #46).

## 3. Cleanups EXÉCUTÉS (non-risqués, mergés + propres)

3 worktrees ASSET 03B **mergés dans la canonique** (SHA = ancêtre de `7eabb25`) **et strictement propres** → worktree retiré (sans `--force`, prouvant l'absence de contenu non-suivi) + **branche locale ET remote** supprimées (mergées, aucune PR ouverte) :

| Worktree | Branche (locale+remote) | SHA | Preuve |
|---|---|---|---|
| `…-sb-asset-03b-2-posterior-mode-fix` | `work/sb-asset-03b-2-posterior-mode-contract-fix` | `c4bff19` | mergée + propre + 0 PR |
| `…-sb-asset-03b-2r-d1-intake` | `work/sb-asset-03b-2r-d1-p0-intake` | `772dc75` | mergée + propre + 0 PR |
| `…-sb-asset-03b-2-p0-regional` | `work/sb-asset-03b-2-p0-regional-plates` | `93ee5fa` | mergée + propre + 0 PR |

**Réversible** : chaque branche étant mergée, son contenu vit dans la canonique ; un worktree peut être recréé (`git worktree add`) à tout moment. **Aucun candidat géométrie perdu** — ces worktrees ne contenaient aucun fichier non-suivi (ils vivent hors Git, cf. PR #46). Worktrees : **11 → 8**.

## 4. Plan de décision opérateur (DIFFÉRÉ — conditions d'arrêt atteintes)

Rien de ce qui suit n'a été touché ; chaque item nécessite un GO explicite.

| Item | État | Condition d'arrêt | Recommandation |
|---|---|---|---|
| **PR #46** (`…synthetic-multimodel-review`) | OUVERTE | **fichiers uniques non mergés** (`tools/evals/muscle_focus/` **absent de la canonique**, 22 tests) → **NON superseded** | **Garder** — décider merge (harness d'eval réutilisable) ou close. Pas superseded par l'intake/runtime ASSET mergé. |
| **10 PRs dependabot** (#1-#12, #45) | OUVERTES | non superseded par du merge | Décision opérateur : merger les bumps voulus / laisser dependabot rebaser / close. Non auto-fermées. |
| worktree `sb-asset-03-2` | **DIRTY** (1 rapport non-suivi) | dirty worktree | Commit-or-discard opérateur, puis suppression si mergé+propre. |
| worktree `sb-asset-03b-1` | **DIRTY** (6 modifiés + 9 docs non-suivis) | dirty worktree + travail unique non-commité | **Ne pas supprimer** — contient du travail doc non sauvegardé (blueprint Muscle Focus). Décider commit/rescue. |
| worktree `custom` (`spec/sx-custom-program-01`) | propre, **NON mergé** | branche non superseded (travail unique) | Garder (spec du futur builder) sauf obsolescence explicite. |
| worktree `geometry-reference` (detached `557b5a0`) | propre | **référence géométrie protégée** | Sûr à retirer sur GO explicite (detached, contenu de référence). |
| worktree `source-reset` (`…bodyparts3d-source-reset`) | propre, mergé | **référence source protégée** | Sûr à retirer sur GO explicite (mergé+propre) mais protégé par la mission. |
| 5 branches orphelines (`sb-31-x-body-intelligence-flag-gate`, `sb-body-01-1-body-flag-gate-before-auth`, `sb-body-01-manual-profile`, `sb-body-02-1-capture-quality-shell`, `sb-ci-01-gitleaks-pr-hardening`) | **NON mergées**, sans worktree | non superseded / ownership flou | Décision opérateur : conserver ou supprimer après confirmation qu'elles ne portent pas de travail unique. |
| worktree `ops-agent-autonomy-01` | — | **INTERDIT** (mission) | Non touché. |
| `AGENTS.md` (repo principal) | non-suivi | **report-only** (mission) | Non touché — signalé uniquement. |

## 5. Garanties (contraintes tenues)

**Contenu canonique non modifié** (hors ce rapport docs) · **aucun commit app/tests/templates/static/migrations** · `ops-agent-autonomy-01` **non supprimé** · **aucun worktree dirty supprimé** · `AGENTS.md` **non touché** · **PR #46 non fermée** (preuve : non superseded) · **références géométrie/source non supprimées**. Suppressions limitées aux 3 branches/worktrees **mergés + propres + sans PR ouverte**.

## Verdict

**Verdict :** 🟢 **Sb_OPS.repo-triage-01 — PR GREEN / MERGE PENDING (record) + CLEANUP PLAN / OPERATOR DECISION REQUIRED (reste).** 3 worktrees ASSET mergés+propres retirés (worktrees 11→8, branches locales+remote supprimées, zéro perte). Tout le reste (PR #46 non-superseded, 10 PRs dependabot, 2 worktrees dirty, 1 spec non mergée, 2 références protégées, 5 branches orphelines) est **documenté pour décision opérateur** — aucune action risquée prise. Merge de ce rapport = GO humain.

---
