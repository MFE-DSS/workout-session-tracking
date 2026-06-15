# Sx_27 — Coaching Loop & Product Activation (Closure Report)

**Auteur :** opérateur SPIGNOS + Claude Code (Opus 4.7).
**Date de clôture technique :** 2026-06-15.
**Spec :** `docs/strategy/Sx_27_COACHING_LOOP_AND_PRODUCT_ACTIVATION_SPEC.md`.
**Registry :** `docs/strategy/SPEC_REGISTRY.md §1bis`.

---

## 1. Verdict global

✅ **Sx_27 techniquement clôturé.**
⏳ **Validation produit en attente du dogfood réel utilisateur** — non exécuté à la rédaction, cf. `docs/dogfood/DOGFOOD_Sx_27_DEFERRED.md`.

7 lots livrés en CI verte (Sb_27.1 → Sb_27.7), sans aucune modification de service métier core, sans migration, sans nouveau modèle SQLAlchemy, sans nouvelle route, sans LLM, sans dépendance ajoutée. Les hard contracts hérités de Sx_26 ont été respectés verbatim sur la totalité du cycle.

## 2. Récapitulatif par lot (Sb_27.1 → Sb_27.7)

| Sprint | Domaine | CI Run | Livrables clés | Verdict |
|---|---|---|---|---|
| **Sb_27.1** | Home dashboard activation | [#27506478583](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/27506478583) | `app/services/home.py` + 3 tuiles Today/Last/Week, partial `home_coaching_loop.html` | ✅ |
| **Sb_27.2** | Session Review V1 | [#27509053460](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/27509053460) | `app/services/session_review.py` (5 sub-payloads), partial `session_review.html`, règles déterministes notable_movements | ✅ |
| **Sb_27.3** | Weekly training loop | [#27511608805](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/27511608805) | `app/services/weekly_loop.py`, partial `weekly_loop.html`, enrichissement `/progress` (OQ-1 tranchée) | ✅ |
| **Sb_27.4** | Recommendation explanation | [#27531258753](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/27531258753) | `app/services/recommendation_explainer.py` (wrapper externe — `recommendation.py` NON modifié, garde anti-import) | ✅ |
| **Sb_27.5** | Deterministic coach narrative | [#27535088857](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/27535088857) | `app/services/narrative.py` (3 helpers purs), garde anti-"vous" exhaustive, wiring minimal | ✅ |
| **Sb_27.6** | UX simplification (`/dashboard` deprecated) | [#27537795326](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/27537795326) | `/dashboard` → 303 → `/`, nav Synthèse → Progression, `compute_dashboard` préservé | ✅ |
| **Sb_27.7** | Product closure report | (ce sprint) | Ce closure report + dogfood deferred + sprint report | ✅ |

## 3. Valeur produit livrée

### 3.1 Boucle quotidienne (cible §1 spec)

| Question utilisateur | Réponse produit livrée | Surface |
|---|---|---|
| Quoi faire aujourd'hui ? | Tuile Today (template_name + reason) + CTA launcher | `/` |
| Pourquoi cette séance ? | `recommendation_explainer` produit jusqu'à 3 raisons cumulables | tuile Today + nav Coach Report |
| Que signifie ma dernière séance ? | Session Review V1 : summary + quality + ressenti + mouvements remarquables + next_hint | `/sessions/{id}/done` |
| Comment ajuster la prochaine séance ? | Tuile Last + Session Review + hint | `/` + `/sessions/{id}/done` |
| Je progresse ou je dérive ? | Weekly loop : count, delta, dominantes, anomaly, hint | `/progress` |

### 3.2 Narrative humaine (Sb_27.5)

Une phrase déterministe par tuile, ton "tu" informel, **jamais "vous"**, max 1 phrase, max ~120 chars, mobile-first 360×640. Triptyche Mesuré/Inféré/Non déductible préservé partout (Sb_23 hérité).

### 3.3 UX simplifiée (Sb_27.6)

`/dashboard` déprécié proprement (redirect 303 → `/`, code préservé). La nav top distingue clairement `/` (coaching) de `/progress` (analytique).

## 4. Surfaces impactées

### 4.1 Routes enrichies (composer + template, pas de logique métier)

| Route | Enrichissement Sx_27 |
|---|---|
| `GET /` | 3 tuiles coaching + explainer reco + narrative |
| `GET /progress` | weekly loop tile en tête + narrative |
| `GET /sessions/{id}/done` | session review V1 + narrative |

### 4.2 Routes inchangées (par contrat)

`/launcher`, `/history`, `/coach-report`, `/physique`, `/library`, `/science`, `/leaderboard`, `/users/{username}`, `/squads/*`, `/profile/*`, `/healthz*`, `/login`, `/register`, `/forgot-password`, `/sessions` (POST), `/sessions/{id}` (GET/POST), `/sessions/{id}/exercises/{seid}` (POST), `/admin/*`, `/export*`, `/readiness*`.

### 4.3 Services créés (composition read-only)

| Service | Rôle |
|---|---|
| `app/services/home.py` | `build_home_payload(db, user, now)` — Today / Last / Week |
| `app/services/session_review.py` | `build_session_review(db, session)` — 5 sub-payloads |
| `app/services/weekly_loop.py` | `build_weekly_loop(db, user, now)` — count, delta, dominantes, anomaly, hint |
| `app/services/recommendation_explainer.py` | `explain_recommendation(payload)` — wrapper externe |
| `app/services/narrative.py` | `narrate_*(payload)` — 3 helpers purs déterministes |

### 4.4 Surfaces dépréciées

| Route | Statut | Décision |
|---|---|---|
| `GET /dashboard` | DEPRECATED — redirect 303 → / | OQ-3 tranchée Sb_27.6 (pas de suppression brutale ; `compute_dashboard` + template `dashboard.html` préservés pour réintroduction future éventuelle) |

## 5. Tests avant / après

| Métrique | Sx_26 closure (2026-06-14) | Sx_27 closure (2026-06-15) | Δ |
|---|---|---|---|
| Total tests | 975 | **1080** | **+105** |
| Tests nouveaux par sprint Sx_27 | — | Sb_27.1: +13, Sb_27.2: +16, Sb_27.3: +15, Sb_27.4: +24, Sb_27.5: +31, Sb_27.6: +6 (incl. réécriture dashboard_routes) | +105 net |
| Tests désactivés / supprimés | 0 | **0** | 0 |
| Tests réécrits (intention changée) | — | `test_dashboard_routes.py` (5 → 4 tests, deprecated redirect) | 1 fichier |

## 6. CI gates conservées

**Toutes les 11+ gates required de Sx_26 sont restées vertes** sur les 7 sprints du cycle Sx_27. Aucune nouvelle gate required ajoutée par Sx_27 (cycle produit, pas process).

| Gate | Statut Sx_27 |
|---|---|
| pytest | ✅ verte sur les 7 sprints |
| catalog_qa | ✅ verte |
| machine_atlas_qa | ✅ verte |
| check_alembic_drift | ✅ verte (0 migration) |
| check_schema_snapshot | ✅ verte (snapshot inchangé) |
| check_migration_patterns | ✅ verte (0 nouvelle migration) |
| check_migration_roundtrip | ✅ verte (inchangé) |
| check_ruff_budget | ✅ ≤ 548 (mesure 534 stable) |
| pip-audit | ✅ clean |
| gitleaks | ✅ clean |
| check_spec_protocol | ✅ verte |
| check_auth_scope_matrix | ✅ verte |
| perf baseline smoke | ✅ within budget |
| SonarCloud | ✅ verte |

**Ajustement CI** : timeout du job `test` bumpé de 15 → 25 min à Sb_27.5 (suite à la croissance du test suite : ~5-7 min local, jamais > 6 min en CI). Comportement inchangé hors marge.

## 7. Contrats respectés (verbatim Sx_27 + hérités Sx_26)

| Contrat Sx_27 | Statut |
|---|---|
| Pas de LLM | ✅ aucun helper, aucune dep, aucun network call |
| Pas de React Native | ✅ SSR Jinja2 préservé |
| Pas de PostgreSQL | ✅ SQLite intact |
| Pas de multi-tenancy | ✅ |
| Pas de billing | ✅ |
| Pas de refonte UI complète | ✅ partials ajoutés en tête, design system inchangé |
| Pas de nouvelle table SQLAlchemy | ✅ 0 modèle modifié |
| Pas de migration Alembic | ✅ 0 nouvelle migration |
| Pas de modification du scoring core | ✅ `scoring/`, `recommendation.py`, `implicit_signal.py`, `quality_score.py`, `coach_report.py`, `body_tracking.py`, `substitution.py` : 0 fichier touché |
| Pas de modification du flow auth | ✅ |
| Pas de modif Sentry, rate limiter, perf baseline, migration gates | ✅ |
| Pas de gamification (badges/streaks) | ✅ |
| Pas de notifications push/email actives | ✅ |
| Pas de partage social (au-delà des squads) | ✅ |
| Pas de suppression de surfaces existantes | ✅ `/dashboard` déprécié, pas supprimé |
| Une narrative ne ment jamais | ✅ Triptyche Non déductible explicite, garde anti-"vous" |

| Contrat Sx_26 hérité | Statut |
|---|---|
| Snapshots historiques sacrés | ✅ `check_migration_patterns` vert |
| `scoring_version` monotone | ✅ |
| ADD COLUMN ONLY | ✅ N/A (0 migration) |
| Ruff budget ≤ 548 | ✅ 534 |
| pip-audit clean | ✅ |
| gitleaks current tree | ✅ |
| Sentry / Discord opt-in | ✅ inchangés |
| Rate limit per-IP | ✅ inchangé |
| Perf budgets respectés | ✅ within `.performance-budget.json` |
| Scope auth isolation cross-user | ✅ `test_auth_scope_isolation.py` vert |

## 8. Non-goals respectés (verbatim §5 spec)

- ❌ LLM obligatoire → ✅ pas de LLM, narrative 100% déterministe
- ❌ React Native → ✅ SSR préservé
- ❌ PostgreSQL → ✅ SQLite
- ❌ Multi-tenancy → ✅ inchangé
- ❌ Billing → ✅
- ❌ Refonte UI complète → ✅ partials ajoutés, pas de redesign
- ❌ Nouvelle table SQLAlchemy → ✅
- ❌ Migration Alembic → ✅
- ❌ Modification scoring core → ✅
- ❌ Modification flow auth → ✅
- ❌ Modification Sentry/rate limiter/perf/migration gates → ✅
- ❌ Gamification → ✅
- ❌ Notifications push/email actives → ✅
- ❌ Partage social au-delà des squads → ✅
- ❌ Suppression de surfaces existantes → ✅ `/dashboard` déprécié, pas supprimé

## 9. OQ tranchées au cours du cycle

| OQ | Décision tranchée | Tranchée par | Quand |
|---|---|---|---|
| OQ-1 (route weekly) | Enrichir `/progress`, pas de nouvelle route `/weekly` | utilisateur | avant Sb_27.3 |
| OQ-2 (position LLM) | Pas de LLM dans Sx_27 | utilisateur | avant Sb_27.5 |
| OQ-3 (fate de `/dashboard`) | Déprécier proprement, 303 → `/`, code préservé | utilisateur | avant Sb_27.6 |
| OQ-4 (modifier `recommendation.py`?) | Wrapper externe `recommendation_explainer.py`, `recommendation.py` NON modifié | utilisateur | avant Sb_27.4 |
| OQ-5 (viewport mobile) | 360×640 Android moyen | utilisateur | avant Sb_27.1 |
| OQ-6 (ton narrative) | "tu" informel, phrases courtes nominales/suggestives, jamais "vous", pas d'impératif agressif | utilisateur | avant Sb_27.5 |

**Aucun amendement spec produit pendant Sx_27** — toutes les OQ étaient identifiées dans la spec initiale (§16), tranchées en amont de leur Sb cible.

## 10. Dettes restantes (héritées du cycle Sx_27)

| Item | Sprint cible candidat |
|---|---|
| Cleanup effectif `dashboard.html` + `compute_dashboard` après dogfood | `Sb_27.next.cleanup-dashboard` |
| Personnalisation narrative par profil utilisateur | `Sb_28+.narrative-profile` (si dogfood le réclame) |
| Multi-langue (EN) | hors Sx_27, futur cycle |
| Détection PR (Personal Records) | `Sb_27.next.pr-detection` si besoin produit confirmé |
| Telemetry "phrase lue / cliquée" | hors scope V1 |
| Sentry release tracking auto (lier SHA → deploy_state) | hérité Sx_26 — `Sb_26.next.sentry-release` |
| Cleanup ruff baseline 548 → 534 | hérité Sx_26 — `Sb_26.next.ruff-cleanup-N` |
| Endpoints POST dans le perf benchmark | hérité Sx_26 — `Sb_26.next.perf-post-1` |
| Refactor `_build_today` cognitive complexity (Sonar S3776, non-bloquant) | tech-debt diffus |
| Audit log persistant accès cross-user | hérité Sx_26 |
| Strict freshness lockfile cross-Python | hérité Sx_26 |
| **Dogfood réel utilisateur** | **`Sb_27.dogfood-1` quand l'opérateur peut exécuter une session d'usage** (cf. §11) |

**Aucune dette bloquante.** Toutes incrémentales et hors chemin critique.

## 11. Dogfood status

### ⏳ DOGFOOD REAL USAGE = DEFERRED

**Le dogfood réel utilisateur n'a PAS été exécuté à la rédaction de ce closure report.**

Cf. `docs/dogfood/DOGFOOD_Sx_27_DEFERRED.md` pour :
- la position formelle (deferred, non simulé)
- le protocole de dogfood à exécuter
- les critères qui décideront du verdict produit final
- la position default si le dogfood ne se fait pas dans un délai raisonnable

**Conséquence sur le verdict :**

- ✅ **Technical closure** : le code est mergé, les tests passent, les gates sont vertes, la documentation est livrée → Sx_27 **techniquement clos**.
- ⏳ **Product validation** : sans dogfood, on ne sait pas si la boucle de coaching atteint réellement le but utilisateur (§1 spec : "5 questions"). La validation produit reste **pending**.

Cette distinction est délibérée et explicite. Le protocole spec-driven (§9) prévoit qu'une livraison de cycle complet appelle un dogfood ; sans dogfood, le cycle n'est pas **product-validated** mais reste **technically closed**.

## 12. Métriques de sortie

| Métrique | Valeur |
|---|---|
| Sprints livrés | **7/7** prévus initialement |
| OQ-N tranchées | 6 (toutes celles posées en §16 spec) |
| CI runs verts au commit final de chaque sprint | **7/7** |
| Tests ajoutés | **+105** (975 → 1080) |
| Tests désactivés / supprimés | **0** |
| Gates required ajoutées | **0** (cycle produit, pas process) |
| Gates required désactivées | **0** |
| Migrations créées | **0** |
| Modèles SQLAlchemy modifiés | **0** |
| Fichiers `app/services/` métier core touchés | **0** (`scoring/`, `recommendation.py`, `reco/`, `implicit_signal.py`, `quality_score.py`, `coach_report.py`, `body_tracking.py`, `substitution.py`) |
| Nouvelles routes créées | **0** |
| Routes dépréciées | **1** (`/dashboard` → 303 → `/`) |
| Services créés (composition read-only) | **5** (`home.py`, `session_review.py`, `weekly_loop.py`, `recommendation_explainer.py`, `narrative.py`) |
| Hard contracts violés | **0** |
| Spec amendments produits | **0** |
| Faux positifs CI résolus | 1 (timeout job test 15 → 25 min à Sb_27.5) |

## 13. Décision finale

### ✅ **Sx_27 technically closed le 2026-06-15.**
### ⏳ **Product validation pending real dogfood** (cf. §11 + `docs/dogfood/DOGFOOD_Sx_27_DEFERRED.md`).

Toute extension future est :
- soit `Sb_27.next.<topic>-N` (cleanup, fix incrémental, hors cycle)
- soit `Sb_27.dogfood-1` (session d'usage réel + report)
- soit un nouveau cycle **Sx_28** (cf. §14 recommandation)

## 14. Recommandation Sx_28 (next step)

**Ne pas ouvrir Sx_28 avant que le dogfood Sx_27 soit exécuté.**

Le risque sinon = empiler une couche produit (Sx_28) sur des hypothèses non vérifiées par l'usage réel. Le protocole spec-driven (§9) considère le dogfood comme l'input principal du prochain cycle.

### 14.1 Si le dogfood Sx_27 confirme la boucle de coaching

→ **Sx_28** peut viser :
- approfondissement narratif (e.g. comparaison "cette séance vs il y a 1 mois")
- détection PR (si dogfood révèle un besoin)
- personnalisation par profil (récupération, ancienneté)
- réintroduction d'un dashboard simplifié si manqué

### 14.2 Si le dogfood révèle un blocker majeur

→ **`Sb_27.next.<topic>`** : fix incrémental avant tout cycle suivant. Pas de Sx_28 tant que le blocker n'est pas levé.

### 14.3 Si le dogfood ne se fait pas dans 14-30 jours

→ Marquer le cycle "**product validation indefinitely deferred**" et acter que Sx_28 démarre sur des hypothèses non vérifiées. Cette option est **fortement déconseillée** mais opérationnellement possible.

---

**Co-Authored-By :** Claude Opus 4.7
