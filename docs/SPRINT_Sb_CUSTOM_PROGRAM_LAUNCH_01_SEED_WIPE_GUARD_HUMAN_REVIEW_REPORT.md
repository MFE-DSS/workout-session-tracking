# Human Review — Sb_CUSTOM_PROGRAM_LAUNCH_01 Seed Wipe-Guard

**Verdict** : ✅ **HUMAN REVIEW ACCEPTED / CI BUSINESS GREEN / SONARCLOUD UPSTREAM BLOCKED /
MERGE FORBIDDEN**
**Date** : 2026-07-16
**Type** : revue humaine — docs-only (aucun code touché par cette revue)
**Track** : `Sx_CUSTOM_PROGRAM` — premier build de code du track (gate `BUILD_GATE_00` §4-5)
**Branche** : `sb/custom-program-launch-01-seed-wipe-guard`, build commit `248af1c`
**PR** : [#22](https://github.com/MFE-DSS/workout-session-tracking/pull/22) — **draft, OPEN**

> Distinction explicite d'état :
> - **CODE COMPLETE** : `248af1c` (poussé, PR draft #22).
> - **CI MÉTIER GREEN** : pytest + QA ✅ (2190 passed) · lint ✅.
> - **SONARCLOUD** : ❌ bloqué par panne upstream (HTTP 504, 2 attempts identiques).
> - **HUMAN REVIEW ACCEPTED** : le présent document.
> - **MERGE : INTERDIT** tant que SonarCloud n'est pas vert (ou décision CI ultérieure explicite).

---

## 1. Verdict

- ✅ **Human review accepted** — le wipe-guard est validé sur le fond et sur les preuves.
- ✅ **pytest + QA scripts green** — **2190 passed**, 2 warnings (25:03) : suite complète
  autoritaire, wipe-guard et migration checks inclus.
- ✅ **lint green** — ruff budget **543 ≤ 548**, bandit/actionlint/shellcheck, spec protocol PASS.
- ❌ **SonarCloud blocked by upstream HTTP 504** (§5) — le scanner n'a jamais analysé le code.
- ❌ **Merge forbidden** tant que SonarCloud n'est pas vert **ou** qu'une décision de policy
  CI ultérieure et explicite n'est pas prise par l'opérateur.

## 2. Scope accepté

**Seed wipe-guard uniquement** : protection des futurs templates custom
(`WorkoutTemplate`), de leurs `TemplateExercise` et de leurs `RepTarget` contre le reseed
catalogue ; **comportement du seed système inchangé** (teardown + reconstruction intégrale
des rows système à chaque bump de version). **Aucune migration · aucun `UserProgram*` ·
aucune matérialisation · aucun wizard** — périmètre du gate respecté à la lettre
(5 fichiers : `seed.py`, test dédié, rapport, registry, roadmap).

## 3. Patch accepté (`app/services/seed.py`, +40/-3, seul fichier de code)

- **Changement exact** : les trois `db.execute(delete(...))` non filtrés de
  `seed_reference_split()` (ex-l.58-60) sont remplacés par des suppressions **ciblées sur
  les rows système** : les ids des templates système sont résolus d'abord
  (`WorkoutTemplate.catalog_section != 'user'`), puis les ids de leurs exercises par
  jointure, puis les rep_targets de ces exercises — suppression dans l'ordre
  enfants → parents.
- **Critère utilisé** : **`catalog_section = 'user'`** = namespace réservé des futurs
  templates custom (constante `CUSTOM_CATALOG_SECTION`), choisi au préflight parce que la
  valeur est **libre** (le système n'occupe que core/utility/specialization/archived) et
  qu'il ne requiert **aucune migration**. Le critère slug-prefix `up%` envisagé au gate a
  été **invalidé au préflight** (collision avec `upper-pecs-delts`/`upper-back-arms`).
- **Pourquoi les customs ne sont plus détruits** : toute row hors du périmètre
  `!= 'user'` est simplement **invisible aux DELETE** ; l'arbre custom complet survit à
  chaque reseed, tandis que le catalogue système continue d'être reconstruit à l'identique
  depuis le JSON.
- **Garde d'entrée** en prime : un payload système revendiquant `catalog_section: "user"`
  lève `ValueError` (fail-fast) — le namespace ne peut pas être corrompu par le seed.

## 4. Tests acceptés

| Preuve | Résultat |
|---|---|
| Tests dédiés `test_seed_wipe_guard.py` (10 : survie template/exercises/rep_targets, multi-customs multi-bumps, reconstruction système, zéro orphelin, idempotence, boot réel, garde d'entrée, JSON réel) | **10/10, premier coup** |
| Adjacents seed/catalogue (catalog_integrity ×2, session_schema, session_builder, session_flow) | **42 passed / 0 échec** |
| **CI complète métier** (run `29479993187`, job pytest + QA) | **2190 passed** |
| Ruff budget | **543 ≤ 548** |
| Spec protocol | **PASS** |
| check_scope | **SHARED_CODE — assumé** (full sweep local tenté : hang connu documenté roadmap, interrompu ; la CI a exécuté la même suite complète) |

Aucun test ne crée de `UserProgram*` (mandat #8) : la row custom de test est un
`WorkoutTemplate` ordinaire en section `user` — exactement l'artefact du futur materializer.

## 5. Incident SonarCloud (non-actionnable par patch)

- **Run** : `29479993187` (PR #22, event pull_request).
- **Attempt 1** : step « SonarQube scan » — `Failed to query JRE metadata: GET
  https://api.sonarcloud.io/analysis/jres?os=linux&arch=x86_64 failed with HTTP 504
  Gateway Timeout`.
- **Attempt 2** (re-run `--failed` sur GO opérateur) : **même erreur, même endpoint,
  même timeout ~30 s**.
- **Échec AVANT toute analyse de code** (provisioning JRE) ; corroboration : l'endpoint
  `api.sonarcloud.io` ne répondait pas non plus depuis la machine locale.
- **Conclusion : panne upstream SonarCloud** — non-actionnable par un patch du repo ;
  aucun patch CI/workflow, aucun skip GitHub Actions, aucune modification de config
  SonarCloud (interdits opérateur respectés).

## 6. Invariants vérifiés

no migration · no `UserProgram*` · no data change · no EKB build · no scoring · no wizard ·
no materialization · no UI/Auren · no deploy · **PR draft only** (ni merge, ni
ready-for-review, ni squash, ni fast-forward canonique) · repo principal et worktrees
spec/UI intacts · rollback = revert d'un seul commit.

## 7. Décision

| Élément | Décision |
|---|---|
| **Human review** | ✅ **ACCEPTED** |
| **PR #22** | reste **draft** |
| **Merge** | ❌ **BLOCKED** — jusqu'à SonarCloud vert (ou décision CI explicite ultérieure) |
| **Next action avant merge** | **re-run du job SonarCloud échoué** (`gh run rerun 29479993187 --failed`) quand le service est rétabli, sur GO |
| **`Sb_CUSTOM_PROGRAM_PERSISTENCE_01`** | reste **NOT OPENED** |
| **Build queue** | **paused until PR #22 CI 3/3** |

---

## Verdict

**Verdict :** ✅ **Sb_CUSTOM_PROGRAM_LAUNCH_01 Seed Wipe-Guard — HUMAN REVIEW ACCEPTED /
CI BUSINESS GREEN / SONARCLOUD UPSTREAM BLOCKED / MERGE FORBIDDEN.**

Le risque critique #1 du track Custom Program est neutralisé et validé humainement : le
reseed catalogue ne détruit plus que les rows système (`catalog_section != 'user'`), le
namespace custom est réservé et gardé en entrée, l'arbre custom complet survit (prouvé par
10 tests dédiés + 2190 passed en CI métier). SonarCloud est bloqué par une panne upstream
(504 ×2, avant analyse) : la PR #22 reste draft et **le merge reste interdit** jusqu'au
3/3. La build queue reste en pause ; `PERSISTENCE_01` non ouvert. Aucun code touché par
cette revue.
