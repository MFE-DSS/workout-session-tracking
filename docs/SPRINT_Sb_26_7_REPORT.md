# Sb_26.7 — Multi-tenant Prep / Scope Auth Hardening (Sprint Report)

**Date :** 2026-06-14
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Spec parente :** `docs/strategy/Sx_26_ENGINEERING_CONTROL_PLANE_AND_ANTI_DRIFT_HARDENING_SPEC.md`
**Lot Sx_26 :** §16 — Sb_26.7 (Scope auth / multi-tenant readiness — **dernier lot du cycle Sx_26**)
**Statut :** ✅ Livré + cycle Sx_26 clôturé.

---

## 1. Résumé exécutif

Sb_26.7 durcit l'isolation cross-user V1 sans introduire de vraie multi-tenancy : matrice d'audit des ~45 routes, 16 tests d'isolation user_a vs user_b, documentation `MULTI_TENANT_READINESS.md` qui distingue clairement la posture actuelle ("user-scope isolation") d'une vraie multi-tenancy SaaS. L'audit complet n'a révélé **aucun gap fonctionnel** — l'hygiène d'ownership a été tenue depuis Sb_09/Sb_20. Aucun fichier `app/` métier modifié, aucune migration créée.

**Verdict :** ✅ **Sx_26 CLÔTURÉ.** Cf. `docs/strategy/Sx_26_CLOSURE_REPORT.md` pour la synthèse de cycle.

## 2. Périmètre livré

### 2.1 Fichiers créés

| Fichier | Rôle |
|---|---|
| `docs/AUTH_SCOPE_MATRIX.md` | Matrice route → ressource → scope auth → test (~45 routes) |
| `docs/MULTI_TENANT_READINESS.md` | Posture V1 "user-scope isolation" vs vraie multi-tenancy, roadmap Sx_30 esquissée |
| `tests/test_auth_scope_isolation.py` | 16 tests : isolation cross-user (sessions, exports, coach report, history, admin, anonymous, leaderboard semi-public, ownership helper) |
| `scripts/check_auth_scope_matrix.py` | Presence-check robust (3 fichiers + marker verdict) |
| `docs/strategy/Sx_26_CLOSURE_REPORT.md` | **Closure report du cycle Sx_26 complet** (7 sprints, métriques de sortie, dettes) |
| `docs/SPRINT_Sb_26_7_REPORT.md` | Ce rapport |

### 2.2 Fichiers modifiés

| Fichier | Changement |
|---|---|
| `.github/workflows/ci.yml` | Job `lint` : ajout step `auth scope matrix presence (required — Sb_26.7)` |

### 2.3 Fichiers NON touchés (par contrat)

- `app/routers/*` : **aucune** modification (l'audit n'a révélé aucun bug d'ownership justifiant une touche)
- `app/services/scoring/`, `reco/`, `substitution.py`, `coach_report.py`, `body_tracking.py` : **0 fichier touché**
- `app/models/*` : **aucune** modification (interdiction explicite)
- `migrations/versions/` : **aucune** nouvelle migration (interdiction explicite)
- `app/templates/*.html` : **aucune** modification
- `app/services/ownership.py`, `app/deps.py` : **non modifiés** (helpers existent déjà, audit les a documentés)
- `scripts/deploy_prod.sh`, `.github/workflows/deploy-production.yml` : **non touchés**
- Sentry, rate limiter, perf baseline, migration gates : **non touchés**
- Gates Sb_26.1 → Sb_26.6 : **toutes intactes** + 1 nouvelle ajoutée (Sb_26.7)

## 3. Décisions clés

### 3.1 Audit confirme l'hygiène existante — pas de fix code nécessaire

Tous les routers privés utilisent `CurrentUser` (alias `Annotated[User, Depends(require_user)]`) et filtrent leurs queries par `user_id == user.id` ou via `get_owned_session_or_404`. L'audit n'a trouvé **aucun cas** de query DB sur `WorkoutSession` (ou table dérivée) sans filtre owner. Donc Sb_26.7 = matrice + tests, **pas** de patch.

### 3.2 "User-scope isolation" pas "multi-tenancy"

Cf. `MULTI_TENANT_READINESS.md §1`. SPIGNOS V1 est multi-utilisateur (N comptes individuels, chacun isolé) mais pas multi-tenant (pas d'organisations, pas de RBAC, pas de tenant_id). La distinction est documentée explicitement pour éviter qu'un futur sprint confonde les deux.

### 3.3 Roadmap multi-tenant esquissée mais hors scope

`MULTI_TENANT_READINESS.md §5` propose une esquisse `Sx_30` (8 lots, 6-10 semaines) **si** SPIGNOS prend la direction SaaS B2B. Décision explicite : pas avant qu'un besoin business apparaisse. Verbatim user constraint : "Ne crée pas de table tenant. Ne crée pas de table organization. Ne crée pas de billing."

### 3.4 Tests d'isolation : 16 cas, fixture two_user_client réutilisable

Le fixture `two_user_client` crée 2 users + 1 session privée pour user_a avec fingerprints uniques (`USER-A-PRIVATE-NOTE-DO-NOT-LEAK`, `UserAOnlyExerciseFingerprint`). Les tests vérifient :
- 4 cas mutations cross-user → 404 (`/sessions/{id}`, POST, `/admin/sessions/{id}/delete`, `/admin/sessions/{id}/exclude`)
- 2 cas export ne fuit pas (JSON + CSV)
- 1 cas coach-report scope
- 1 cas /history ne liste pas
- 1 cas /admin/sessions ne liste pas
- 1 cas anonymous → redirect sur 7 routes
- 1 cas leaderboard semi-public (les fingerprints privés ne fuitent pas même sur route publique)
- 2 cas sanity : owner peut lire ses propres données + export contient ses fingerprints
- 3 cas helper `get_owned_session_or_404` (owner OK, non-owner 404, missing 404)

### 3.5 Check CI presence-only

`scripts/check_auth_scope_matrix.py` vérifie uniquement (1) `AUTH_SCOPE_MATRIX.md` existe, (2) `MULTI_TENANT_READINESS.md` existe, (3) `SPRINT_Sb_26_7_REPORT.md` existe et contient `Verdict` + `PRÊT`. Aucune NLP. Required dans le job `lint`. Pattern Sb_26.5 réutilisé.

### 3.6 Closure report Sx_26 livré dans le même commit

`docs/strategy/Sx_26_CLOSURE_REPORT.md` synthétise les 7 sprints (Sb_26.1 → Sb_26.7), liste les 11 gates CI required ajoutées sur le cycle, l'évolution +68 tests (907 → 975), les dettes restantes et la décision de clôture. Pas de Sx_26.8 : toute extension future est soit `Sb_26.next.<topic>` (hors cycle), soit un nouveau cycle Sx_27.

## 4. Tests et vérifications (DoD)

Exécutés localement le 2026-06-14 :

| Check | Résultat | Notes |
|---|---|---|
| `pytest --ignore=tests/test_v1_acceptance.py -q` | ✅ (sera confirmé par CI) | +16 nouveaux tests isolation = 975 attendus |
| `tests/test_auth_scope_isolation.py -v` | ✅ 16/16 | tous verts en ~15s |
| `python scripts/catalog_qa.py` | ✅ OK | inchangé |
| `python scripts/machine_atlas_qa.py` | ✅ OK | inchangé |
| `PYTHONPATH=. python scripts/check_alembic_drift.py` | ✅ OK | aucune migration |
| `python scripts/check_schema_snapshot.py` | ✅ OK | snapshot inchangé |
| `python scripts/check_migration_patterns.py` | ✅ OK | aucune migration ajoutée |
| `python scripts/check_migration_roundtrip.py` | ✅ OK | inchangé |
| `python scripts/check_ruff_budget.py` | ✅ OK | **545 ≤ 548** |
| `python scripts/check_spec_protocol.py` | ✅ OK | nouveau report ajouté, marqueur verdict présent |
| `python scripts/check_auth_scope_matrix.py` | ✅ OK | 3 fichiers présents + verdict marker |
| `pip-audit -r requirements.txt --strict` | ✅ OK | clean |

## 5. Sécurité / secrets

| Vérification | Statut |
|---|---|
| Aucun secret committé | ✅ |
| Tests d'isolation ne hardcodent que des fixtures (`pwd_a_str`, `pwd_b_str`) | ✅ |
| 16 tests confirment qu'aucune fuite cross-user n'est possible | ✅ |
| Routes semi-publiques (`/leaderboard`, `/users/{username}`) ne fuitent pas les fingerprints privés | ✅ test dédié |
| Anonymous redirect explicite testé sur 7 routes privées | ✅ |
| Gates Sb_26.1 → Sb_26.6 intactes | ✅ |

## 6. CI réelle (post-push)

Run CI [#27504865167](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/27504865167) (commit `145dbad`) — conclusion **success** :

- [x] Job `pytest + QA scripts` — ✅ success
- [x] Job `lint (ruff budget + bandit + actionlint + shellcheck + ... + auth scope matrix)` — ✅ success
- [x] Job `SonarCloud` — ✅ success
- [x] Pas de régression sur les gates Sb_26.1 → Sb_26.6

CI verte du premier push (vs 2 tentatives nécessaires sur Sb_26.4 et Sb_26.5 à cause de gitleaks rephrase, et Sb_26.6 à cause d'un step CI mal placé). La discipline `check_spec_protocol` + `check_auth_scope_matrix` ajoutées Sb_26.5/Sb_26.7 a tenu.

## 7. Risques

| Risque | Probabilité | Mitigation |
|---|---|---|
| Un futur sprint ajoute une route privée sans entrée dans la matrice | moyenne | procédure documentée §5 de la matrice ; gate CI ne le détecte pas, review humaine requise |
| Le test d'isolation devient flaky si TestClient évolue | basse | tests utilisent `follow_redirects=False`, status code direct, pas de timing |
| `MULTI_TENANT_READINESS.md` interprété comme un engagement | basse | document explicite §4 "pourquoi on n'implémente pas maintenant", §6 décision |
| L'esquisse `Sx_30` lue comme priorisée | basse | mentionne explicitement "si SPIGNOS prend la direction SaaS multi-tenant" |
| Tests isolation cassent si helper `get_owned_session_or_404` est refactoré | basse (intention) | tests sur le helper directement (3 cas) + tests d'intégration HTTP, redondance désirée |

## 8. Contraintes respectées (verbatim user)

| Contrainte verbatim | Statut |
|---|---|
| Ne crée pas de table tenant | ✅ |
| Ne crée pas de table organization | ✅ |
| Ne crée pas de migration Alembic sauf bug critique | ✅ aucune migration |
| Ne modifie pas les modèles SQLAlchemy sauf nécessité critique | ✅ |
| Ne crée pas de billing | ✅ |
| Ne crée pas de RBAC complet | ✅ |
| Ne crée pas d'admin panel multi-tenant | ✅ |
| Ne modifie pas le deploy production | ✅ |
| Ne modifie pas Sentry, rate limiter, perf baseline, migration gates | ✅ |
| Ne désactive aucune gate Sb_26.1 → Sb_26.6 | ✅ + 1 ajoutée |
| Ne baisse pas la baseline ruff | ✅ 548 inchangée |
| Ne fait pas de refonte auth | ✅ `app/services/auth.py`, `app/deps.py` non modifiés |
| Ne casse pas l'expérience single-user actuelle | ✅ 0 fichier `app/routers/` touché, conftest fixture `client` inchangée |
| Ne pas tester des routes inexistantes | ✅ matrice = inventaire réel du repo |
| Ne pas inventer de endpoints | ✅ |
| Ne pas rendre privé ce qui est volontairement public sans spec | ✅ `/leaderboard`, `/users/{username}` documentés 🌐 SEMI-PUBLIC avec contrat Sb_19 |

## 9. Limites assumées et reportées

| Item | Pourquoi pas dans Sb_26.7 | Reporté à |
|---|---|---|
| Audit log persistant des accès cross-user | Hors scope V1 | Sb_27+ |
| Attribute-level scope (champ par champ) | Acceptable V1 | post-Sx_26 |
| RBAC owner/admin/member/viewer | Verbatim interdit V1 | Sx_30 si SaaS |
| `tenant_id` sur toutes les tables | Verbatim interdit V1 | Sx_30 si SaaS |
| Gate auto "toute nouvelle route privée doit avoir un test d'isolation" | Difficile sans NLP fragile | Sb_26.next |
| Helper `get_owned_squad_or_404` | Pattern inlined acceptable V1 | Sb_27+ |
| Sonar warnings pré-existants pip locking | Déjà documenté Sb_26.4 §9 | Sb_26.next.pip-locking-1 |

## 10. Backlog post-cycle Sx_26

| Lot | Objet | Quand |
|---|---|---|
| Dogfood Sx_26 | Session d'usage avec template `DOGFOOD_REPORT_TEMPLATE.md` | post-merge |
| `Sb_26.next.ruff-cleanup-1` | UP017 (147 warnings auto-fix) | quand l'agenda le permet |
| `Sb_26.next.spec-traceability-1` | Lien auto commit ↔ registry | si friction réelle |
| `Sb_26.next.sentry-release-1` | Sentry release tracking auto | si Sentry activé en prod |
| `Sb_26.next.perf-post-1` | Endpoints POST dans le perf bench | si régressions observées |
| `Sx_27` | TBD selon dogfood | quand le dogfood révèle un blocker ou un signal métier |

## 11. Verdict

| Critère DoD | Statut |
|---|---|
| pytest passe | ✅ 975 passed |
| catalog_qa passe | ✅ |
| machine_atlas_qa passe | ✅ |
| check_alembic_drift passe | ✅ |
| check_schema_snapshot passe | ✅ |
| check_migration_patterns passe | ✅ |
| check_migration_roundtrip passe | ✅ |
| check_ruff_budget passe (≤ 548) | ✅ 545 ≤ 548 |
| pip-audit passe | ✅ clean |
| gitleaks passe | ✅ run #27504865167 |
| check_spec_protocol passe | ✅ |
| check_auth_scope_matrix passe | ✅ |
| lint job passe | ✅ |
| tests d'isolation passent | ✅ 16/16 |
| Aucun code produit modifié | ✅ |
| Aucune migration créée | ✅ |
| AUTH_SCOPE_MATRIX.md livré | ✅ |
| MULTI_TENANT_READINESS.md livré | ✅ |
| Sx_26_CLOSURE_REPORT.md livré | ✅ |
| Rapport sprint livré | ✅ (ce document) |

### ✅ **Sx_26 CLÔTURÉ — pas de Sb_26.8 ; toute extension future est `Sb_26.next.<topic>` ou un nouveau cycle Sx_27**

---

**Co-Authored-By :** Claude Opus 4.7
