# Sprint Report — Sb_OPS.ci-path-filter

**Sprint ID :** `Sb_OPS.ci-path-filter`
**Type :** BUILD (infra CI) — override léger hors cycle Sx_
**Date :** 2026-07-02
**Auteur :** opérateur (Martin Feldmann) + agent Claude Code
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Verdict :** ✅ **READY FOR HUMAN REVIEW**

---

## 1. Résumé

Sprint OPS chirurgical pour réduire la facture GitHub Actions sur les cycles docs-only, notamment le futur cycle `Sx_UI` (11 specs docs-only à venir : Sx_UI_01 → Sx_UI_11 hors sprints d'implémentation).

Objectif : ajouter un filtre `paths-ignore: ['docs/**']` sur le trigger `push` du workflow `ci.yml`. Un push dont **tous** les fichiers modifiés sont sous `docs/` ne déclenche plus la CI. Un push contenant **au moins un** fichier hors `docs/` continue de déclencher la CI complète (pytest, linting, QA scripts, SonarCloud).

**Non affecté** : le trigger `pull_request` conserve la CI complète pour toute PR, quelle que soit la nature du diff. Cela garantit qu'aucun merge de PR ne passe sans validation CI récente.

**Non affecté** : `deploy-production.yml` (trigger `workflow_dispatch` seul, aucun trigger automatique).

## 2. Motivation

Constat sur les 4 derniers commits (2026-07-01 → 2026-07-02) :

| Commit | Type | CI run | Contenu diff |
|---|---|---|---|
| `55a96b2` | docs OPS report initial | ✅ vert | 100 % docs |
| `ddd476b` | docs OPS verdict signé | ✅ vert | 100 % docs |
| `34d6762` | docs brainstorm UI + roadmap Auren | ✅ vert (dans batch push) | 100 % docs |
| `2e345e8` | docs Sx_UI_01 Brand Foundation Spec | 🟡 en cours | 100 % docs |

**4 runs CI complets pour du 100 % docs.** ~80 min de compute GitHub Actions dépensés pour valider zéro code. Projection sur le cycle Sx_UI (10 specs docs-only restantes) : **200-300 min de compute purement gaspillé** si la stratégie ne change pas.

Ce sprint casse temporairement la règle « docs-only jusqu'à Sx_UI_04 » du cycle Sx_UI, de façon **contrôlée et explicite**, avec un bénéfice cumulatif sur tous les sprints docs-only futurs (pas seulement Sx_UI).

## 3. Fichiers créés / modifiés

### Créés

- `docs/SPRINT_Sb_OPS_ci_path_filter_BUILD_REPORT.md` — ce rapport

### Modifiés

- `.github/workflows/ci.yml` — ajout `paths-ignore: ['docs/**']` sur le trigger `push` (6 lignes ajoutées, commentaire inline expliquant la règle)
- `docs/strategy/SPEC_REGISTRY.md` — ajout ligne cycle OPS pour trace du sprint

## 4. Périmètre respecté

**Scope strict OPS/infra respecté.** Modifications limitées à :

- ✅ `.github/workflows/ci.yml` — trigger `push` uniquement, ajout paths-ignore
- ✅ `docs/` — ce rapport + update registry

**Aucun impact sur :**

- ❌ `app/` (aucun service, aucun router, aucun template, aucun static)
- ❌ `tests/`
- ❌ `migrations/`
- ❌ `scripts/`
- ❌ `.github/workflows/deploy-production.yml`
- ❌ `.env`, config runtime
- ❌ Logique métier (scoring, substitution, coach_report, body_intelligence, overload_engine, etc.)

## 5. Décisions prises

| # | Décision | Rationale |
|---|---|---|
| 1 | Filter strict `docs/**` uniquement | Le plus sûr. Un fichier `README.md` racine ou `LICENSE` continue de déclencher CI. Aucun risque d'oubli. |
| 2 | Filter uniquement sur `push`, pas sur `pull_request` | Toute PR garde CI complète. Aucun merge ne passe sans validation. Trade-off d'économie/sécurité optimal. |
| 3 | Sprint infra dédié plutôt qu'intégré dans un sprint UI futur | Bénéfice immédiat sur tous les sprints Sx_UI docs-only, sans attendre `Sx_UI_04` (qui est à ~6 sprints). |
| 4 | `deploy-production.yml` non touché | Trigger `workflow_dispatch` seul, aucun déclenchement automatique — rien à filtrer. |

## 6. Test attendu

**Après merge de ce sprint :**

- Push docs-only (ex : Sx_UI_02 spec seule) → CI **skip** attendue. Vérifier via `gh run list --branch ...` que aucun nouveau run n'apparaît pour le SHA.
- Push contenant `.github/workflows/ci.yml` (ce sprint lui-même) → CI **joue** normalement.
- PR docs-only vers main → CI **joue** normalement (trigger `pull_request` non affecté).

**Ce sprint lui-même déclenchera un run CI** puisqu'il modifie `.github/workflows/ci.yml`. C'est attendu et voulu — validation que le filter ne casse pas la syntaxe YAML ni les jobs existants.

## 7. DoD local

- [x] Modification limitée à `.github/workflows/ci.yml` (trigger push) + docs
- [x] Aucun fichier `app/`, `tests/`, `migrations/`, `scripts/` touché
- [x] YAML syntax valide (`python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"` → OK)
- [x] `deploy-production.yml` non touché
- [x] Commentaire inline dans ci.yml explique la règle
- [x] Rapport sprint créé
- [x] Registry mis à jour

## 8. DoD CI

CI réelle : **pending until push.** Ce sprint modifie `.github/workflows/ci.yml`, donc **déclenchera** un run CI (comportement voulu, cf. §6).

À vérifier après run :
- ✅ CI joue normalement (le path filter ne bloque pas le sprint qui modifie ci.yml)
- ✅ Tous les jobs verts (pytest, lint, SonarCloud)

## 9. Prochain step

**Après CI verte + validation opérateur :**

Ouvrir `Sx_UI_02_DESIGN_TOKENS_SPEC` SPEC ONLY. Ce prochain sprint sera **docs-only** et **ne déclenchera plus la CI** grâce à ce filter. Économie immédiate.

**En parallèle** :
- OQ-A due diligence Auren (INPI/EUIPO/USPTO + domaines) reste hors-scope agent
- Mini-gate `PROD_DOGFOOD_57KG_LIVE_CHECK` reste pending

## 10. Références

- Workflow modifié : `.github/workflows/ci.yml`
- Registry : `docs/strategy/SPEC_REGISTRY.md`
- Sprint précédent (Sx_UI_01) : `docs/SPRINT_Sx_UI_01_REPORT.md`
- Roadmap globale : `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`

## 11. Verdict

✅ **READY FOR HUMAN REVIEW.**

Modification infra CI minimale (6 lignes YAML), commentée en français, testée localement en syntaxe. Trade-off économie/sécurité choisi : filter strict `docs/**` sur `push`, PR non affecté. Bénéfice attendu ~90 % de réduction runs CI sur les cycles docs-only à venir.
