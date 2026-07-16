# Sprint Sb_CUSTOM_PROGRAM_LAUNCH_01 — Seed Wipe-Guard — BUILD

**Statut** : 🟢 **BUILD READY FOR REVIEW** (non commité, non poussé, CI non lancée)
**Type** : CODE BUILD — sécurité seed, premier build du track `Sx_CUSTOM_PROGRAM`
**Date** : 2026-07-15
**Specs** : `Sx_CUSTOM_PROGRAM_05` §4 (wipe-guard) + `Sx_CUSTOM_PROGRAM_BUILD_GATE_00` §5-6
**Branche** : `sb/custom-program-launch-01-seed-wipe-guard` (worktree dédié, rebasée sur la
canonique `9a405a7`, 12 commits docs du track rejoués sans conflit)
**Préflight** : ✅ GO PATCH validé par l'opérateur (audit read-only complet avant toute ligne)

---

## 0. Étape 0 — Brainstorming / Options / Risques / Choix retenu

### Décision : **garde par `catalog_section != 'user'`, sans migration** (Option A)

| Option | Description | Verdict |
|---|---|---|
| **A — Section-guard** (retenue) | filtre des 3 DELETE sur `catalog_section != 'user'` ; valeur `user` libre (le système n'occupe que core/utility/specialization/archived) + garde d'entrée refusant un payload qui la revendiquerait | ✅ zéro migration, critère net, réserve officiellement le namespace |
| B — Slug-prefix `up%` | filtre sur le préfixe de slug custom | ❌ **rejetée au préflight** : `upper-pecs-delts` et `upper-back-arms` (système, archivés) commencent par `up` — collision réelle |
| C — Colonne `owner_user_id` | flag d'ownership dédié | ❌ rejetée ici : exige une migration, explicitement interdite dans ce build ; reste le plan de `LAUNCH_02` (OQ-LAUNCH-A/B) |

### Risque / parade critique

| Risque | Parade |
|---|---|
| Le filtre casse la reconstruction système | tests #4/#6 : teardown + rebuild complets vérifiés sur payload synthétique ET boot réel |
| Enfants custom supprimés par jointure mal écrite | sous-requêtes résolues AVANT suppression des parents ; ordre RepTarget → TemplateExercise → WorkoutTemplate conservé ; tests #2/#3 |
| Namespace `user` revendiqué un jour par le JSON système | garde d'entrée `ValueError` (fail-fast au boot) + test #9 + test #10 sur le JSON réel |

## 1. Objectif

Empêcher le reseed du catalogue (`seed_reference_split`, déclenché à chaque bump de version
de `reference_split.json`) de détruire les futurs templates custom — **le risque critique #1
du track Custom Program** (spec 05 §4), qui devait être neutralisé avant tout autre build.

## 2. Rappel du risque

Avant ce patch : `db.execute(delete(RepTarget))` / `delete(TemplateExercise)` /
`delete(WorkoutTemplate)` — **sans filtre** (`seed.py` l.58-60). Tout template custom aurait
été silencieusement détruit, avec ses enfants, au premier bump de version du catalogue
système. Fenêtre d'exposition réelle dès `LAUNCH_03` (materializer) ; d'où l'ordre
non négociable du gate : ce build en premier.

## 3. Patch appliqué

`app/services/seed.py` uniquement (+40/-3) :

1. **Constante** `CUSTOM_CATALOG_SECTION = "user"` — namespace réservé, documenté.
2. **Garde d'entrée** : un payload système déclarant `catalog_section: "user"` lève
   `ValueError` (fail-fast, jamais de corruption silencieuse du namespace).
3. **Wipe-guard** : les 3 DELETE deviennent filtrés — templates système
   (`catalog_section != 'user'`) résolus d'abord, puis leurs exercises par jointure, puis
   les rep_targets de ces exercises ; suppression dans l'ordre enfants → parents.
   **Les rows custom et tout leur arbre survivent à chaque reseed.**
4. Docstring du module mise à jour (contrat wipe-guard).

Rien d'autre : `load_reference_payload`, la boucle de reconstruction, `seed_method_rules`,
le contrat de retour `bool` et l'appel au boot (`main.py`) sont **byte-identiques**.

## 4. Tests ajoutés — `tests/test_seed_wipe_guard.py` (nouveau, 10 tests)

| # | Test | Exigence couverte |
|---|---|---|
| 1 | `test_custom_template_survives_reseed` | mandat #1 |
| 2 | `test_custom_template_exercises_survive_reseed` | mandat #2 |
| 3 | `test_custom_rep_targets_survive_reseed` | mandat #3 |
| 4 | `test_system_templates_rebuilt_on_version_bump` | mandat #4 |
| 5 | `test_no_custom_template_deleted_by_reseed` (2 customs, 2 bumps) | mandat #5 |
| 6 | `test_system_children_fully_replaced` (zéro orphelin système) | mandat #6 |
| 7 | `test_seed_idempotent_same_version_is_noop` | mandat #7 |
| 8 | `test_boot_catalog_unchanged_without_custom_rows` (boot réel intact, 0 row `user`) | mandat #6 |
| 9 | `test_seed_payload_claiming_user_section_is_rejected` | garde d'entrée |
| 10 | `test_reference_split_json_never_uses_user_section` | garde du JSON réel |

**Mandat #8 respecté** : aucun test ne crée de `UserProgram*` — la row custom est un
`WorkoutTemplate` ordinaire en section `user`, exactement ce que produira le materializer.

## 5. Tests exécutés (local)

| Suite | Résultat |
|---|---|
| `test_seed_wipe_guard.py` (dédiés, nouveau) | **10/10** (4,7 s, premier coup) |
| Adjacents seed/catalogue (`catalog_integrity` ×2, `session_schema`, `session_builder`, `session_flow`) | **42 passed / 0 échec** |
| ruff (`seed.py` + test neuf) | clean |
| `check_ruff_budget` | **543 ≤ 548** |
| `check_spec_protocol` | PASS |
| **Full sweep local** | exigé par le tier (§6) — résultat consigné dans le rapport de session au moment du GO COMMIT |

## 6. check_scope

**TIER : SHARED_CODE** (`seed.py` importé par `main.py`) — conforme à l'anticipation du
préflight. Checks requis : ruff neufs ✅ · budget ✅ · spec ✅ · targeted ✅ · broad sweep
scoped ✅ · **full sweep local** (lancé ; CI réelle au push = source de vérité).

## 7. Risques résiduels

| Risque | État |
|---|---|
| La reco (`catalog_section != 'archived'`) ingérerait une row `user` | connu, **sans fenêtre d'exposition** (aucune row `user` ne peut exister avant `LAUNCH_03`) ; filtre = `LAUNCH_04`, ordre du gate inchangé |
| `/library` face à une section `user` | non rendue (itération sur `CATALOG_SECTIONS` hardcodé) — vérifié au préflight |
| Namespace `user` encore non porté par un modèle d'ownership | assumé V1 ; `owner_user_id` = `LAUNCH_02` (OQ-LAUNCH-A/B) |

## 8. Confirmations de périmètre

✅ **Aucune migration** · ✅ **aucune table/modèle `UserProgram*`** · ✅ **aucun wizard** ·
✅ **aucune matérialisation** · ✅ aucun scoring/EKB build · ✅ aucune data modifiée ·
✅ aucun template/CSS/JS/UI · ✅ aucune route/service hors `seed.py` · ✅ aucun deploy ·
✅ repo principal et worktrees spec/UI non touchés.

---

## Verdict

**Verdict :** 🟢 **Sb_CUSTOM_PROGRAM_LAUNCH_01 — BUILD READY FOR REVIEW** (pas accepted).

Le risque critique #1 du track est neutralisé : le reseed catalogue ne peut plus détruire
une row custom (`catalog_section='user'`, namespace officiellement réservé et gardé en
entrée), tout en reconstruisant le système exactement comme avant. Patch minimal (+40/-3,
un seul fichier de code), 10 tests dédiés verts au premier coup, 42 adjacents verts,
ruff/budget/spec verts, tier SHARED_CODE assumé (full sweep + CI réelle obligatoires).
**Prochaines étapes : full sweep vert → GO COMMIT → GO PUSH + CI 3/3 → GO VALIDATE.**
