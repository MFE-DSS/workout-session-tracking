# Human Review — Sb_UI_10.4b — Method Rules User-Facing Data String Pass

**Verdict** : ✅ **HUMAN REVIEW ACCEPTED**
**Type** : HUMAN REVIEW — docs-only (aucun code/donnée/test touché)
**Date** : 2026-07-15
**Repo** : MFE-DSS/workout-session-tracking
**Branche canonique** : `claude/sprint-reporting-fitness-app-V7Qr6`
**Worktree de revue** : `work/auren-migration-review-10-4b` (isolé, mergé FF)

> Distinction d'état :
> - **CODE COMPLETE** : build `bbfbe32` (poussé).
> - **CI GREEN** : run `29420622692` — 3/3 success.
> - **HUMAN REVIEW ACCEPTED** : le présent commit `docs(review)` (séparé du code).

---

## 1. Sprint & commit examinés
- **Sprint** : `Sb_UI_10.4b` Method Rules User-Facing Data String Pass.
- **Commit build** : `bbfbe32` — feat(ui): migrate seeded method-rule product string to Auren.
- **Rapport build** : `docs/SPRINT_Sb_UI_10_4b_METHOD_RULES_DATA_STRING_PASS_REPORT.md`.
- **État Git initial** : canonique `bbfbe32` == origin, working tree **clean**. Revue conduite dans un
  **worktree isolé** (stratégie anti-collision validée au build).

## 2. Verdict CI `29420622692` — 3/3 success
| Job | Résultat |
|---|---|
| **pytest + QA scripts** (inclut migration + schema drift checks) | ✅ **success** |
| **lint** (ruff budget + bandit + actionlint + shellcheck) | ✅ **success** |
| **SonarCloud** | ✅ **success** |
Run associé à **`bbfbe32`** (SHA confirmé). Aucun timeout, aucun rerun masquant, aucun job obligatoire skipped.

## 3. Diff fonctionnel examiné (`aa263be..bbfbe32`)
Périmètre (5 fichiers) : `data/method_rules.json` (M) · `tests/test_auren_user_facing_labels.py` (M) ·
build report (A) · `SPEC_REGISTRY.md` (M) · `ROADMAP_AND_NEXT_STEPS.md` (M). **Aucun**
`app/templates/**`, `app/static/**`, `app/routers/**`, `app/services/**`, `app/models/**`,
`migrations/**`, `manifest`, `schema_snapshot`, CSS/JS, `.github/**`.

## 4. Phrase avant / après (règle `plages-repetitions`)
```
- … Le score d'un exercice dans SPIGNOS est dérivé de la position de tes reps …
+ … Le score d'un exercice dans Auren   est dérivé de la position de tes reps …
```
**Seul le nom produit visible change.** Le reste du body (échec mécanique, plage 8-12, progression de
charge, ponctuation) est **byte-identique** → sens scientifique **strictement inchangé**.

## 5. Invariants JSON vérifiés
- Slugs + **ordre** des 7 règles : identiques.
- Seule `plages-repetitions` a un `body` modifié.
- Clés (`body`/`position`/`slug`/`title`) : inchangées. Structure JSON valide.
- Zéro Orion.

## 6. Audit du seed (`seed_method_rules`)
Lecture seule de `app/services/seed.py` + appel `app/main.py:47` (lifespan startup) :
1. Source = `data/method_rules.json` (`load_method_rules_payload`). ✅
2. Table `method_rules` **vidée** (`delete(MethodRule)`) **avant** réinsertion. ✅
3. Réinsertion à **chaque démarrage** concerné. ✅
4. **Base préexistante → Auren au reseed** — *prouvé* : base peuplée avec l'ancien « SPIGNOS » (1) →
   après `seed_method_rules` → **SPIGNOS=0, Auren=1**. ✅
5. **Aucune migration Alembic** nécessaire (données, pas schéma ; pas de FK entrante). ✅
6. **Idempotent** — *prouvé* : reseed ×2 → 7 règles en base, **0 doublon**. ✅
7. Schéma et identifiants inchangés. ✅

## 7. Rendu utilisateur `/science` (HTTP réel, base seedée)
| Contrôle | Résultat |
|---|---|
| status | **200** |
| « SPIGNOS » visible | **0** ✅ |
| « Orion » visible | **0** ✅ |
| « dans Auren est dérivé » | **présent** ✅ |
| éléments structurants (Science / materialise / diagram) | présents ✅ |
Distinction respectée : la décision porte sur le **corps HTML rendu**, pas la source / commentaires /
logger interne.

## 8. Test sentinelle vérifié
`test_science_remaining_spignos_is_only_the_seeded_method_rule` (== 1) **ré-orienté** en
`test_science_no_visible_spignos_after_method_rule_migration` : `body.count("SPIGNOS") == 0` +
« dans Auren est dérivé ». **Ciblé, lisible, non couplé au full-HTML, sensible aux régressions
futures, cohérent avec le seed réel.** (Test non modifié par cette revue.)

## 9. Identifiants techniques conservés (SPIGNOS interne légitime)
Table `method_rules`, slug `plages-repetitions`, logger `spignos.request_timing`, nom de repo/modules —
**conservés** (catégorie interne/technique). Aucun renommage interne.

## 10. Décision humaine
**HUMAN REVIEW: ACCEPTED.** Les 14 critères §12 satisfaits : chaîne unique migrée, sens scientifique
inchangé, structure/identifiants inchangés, seed remplace l'ancienne valeur + idempotent, aucune
migration, /science rend 0 SPIGNOS + 0 Orion + phrase Auren, sentinelle protège l'état final, aucun
hors-scope, CI 3/3 verte sur `bbfbe32`, working tree de revue propre, aucun travail concurrent détecté.

## 11. Jalon produit
**Aucune surface utilisateur portée par les templates OU les données seedées ne rend désormais le nom
SPIGNOS** (shell `10.1` + auth `10.3` + docs `10.4` + donnée `10.4b`). Le nom interne SPIGNOS
(repo/code/table/logger) reste légitime — le repo entier contient encore SPIGNOS **en interne**, par
conception.

## 12. Éléments différés (inchangés)
`Sb_UI_10.2` — **BLOCKED BY ASSETS** · `Sx_UI_10` Closeout — **BLOCKED BY Sb_UI_10.2** ·
Dogfood Focus F1/F2/F3 — séparé.

---

## Verdict

**Verdict :** ✅ **Sb_UI_10.4b — HUMAN REVIEW ACCEPTED.** La dernière chaîne produit visible seedée
(règle `plages-repetitions`, rendue sur /science) migre SPIGNOS → **Auren**. Data-only, sens
scientifique intact, structure/identifiants JSON conservés, **aucune migration** (table wipe+reinsert
au boot, remplacement sur base préexistante et idempotence prouvés), /science rend **0 SPIGNOS / 0
Orion**, sentinelle ré-orientée, CI 3/3 verte sur `bbfbe32`. **Jalon : plus aucune surface utilisateur
(template + donnée) ne rend SPIGNOS.**

**Prochaines étapes** (non commencées) : `Sb_UI_10.2` (assets PWA, BLOCKED), puis `Sx_UI_10` Closeout ;
dogfood carte active indépendant.
