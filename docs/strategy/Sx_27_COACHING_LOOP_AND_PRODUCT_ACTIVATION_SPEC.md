# Sx_27 — Coaching Loop & Product Activation (SPEC ONLY)

> **Statut :** SPEC ONLY — aucun code livré à ce stade. Validation humaine explicite requise avant l'ouverture de Sb_27.1.
> Référence protocole : `docs/strategy/SPEC_DRIVEN_ENGINEERING_PROTOCOL_v1.md`.
> Cycle parent immédiat (clos) : `docs/strategy/Sx_26_CLOSURE_REPORT.md`.

**Auteur :** opérateur SPIGNOS + Claude Code (Opus 4.7).
**Date :** 2026-06-14.
**Version :** v1.

---

## 1. Executive summary

Sx_26 a livré un control plane technique solide (CI, migrations, observabilité, sécurité, process, perf, scope auth). Le repo est **prêt** à supporter un cycle produit.

Sx_27 attaque l'autre côté : transformer la masse de services et de pages déjà construits (recommendation, coach report, briefing, history, dashboard, progress, physique, leaderboard…) en **une boucle de coaching réellement utilisable au quotidien** par un utilisateur seul.

Le but n'est PAS d'ajouter une nouvelle feature majeure, c'est de **connecter** les briques existantes pour répondre à 5 questions concrètes que l'utilisateur se pose :

1. *Quoi faire aujourd'hui ?*
2. *Pourquoi cette séance ?*
3. *Ce que ma dernière séance signifie ?*
4. *Comment ajuster la prochaine ?*
5. *Est-ce que je progresse ou je dérive ?*

Si Sx_27 est livré, l'utilisateur ouvre l'app et obtient une réponse claire à chacune sans cliquer plus de 2 fois. C'est l'**activation produit** du V1 : passer d'un journal d'entraînement à un coach.

## 2. Problème utilisateur

### 2.1 Friction réelle observée (état actuel)

| Question | Surface qui devrait répondre | Friction actuelle |
|---|---|---|
| *Quoi faire aujourd'hui ?* | `/launcher` | Recommandation existe (`recommend_next_session`) mais l'écran d'entrée (`/`) ne la met pas au centre — l'utilisateur doit cliquer "launcher" puis comprendre les options |
| *Pourquoi cette séance ?* | `/launcher`, `/coach-report` | La logique de reco existe (zone freshness, fatigue, méthode) mais n'est PAS racontée à l'utilisateur en langage humain |
| *Que signifie ma dernière séance ?* | `/sessions/{id}/done`, `/coach-report` | La page "done" recense les sets, pas le sens. Le coach report est à part. |
| *Comment ajuster ?* | `/coach-report`, briefing | Le briefing existe mais arrive avant la séance, pas en boucle de feedback après |
| *Je progresse ?* | `/progress`, `/physique`, `/dashboard` | 3 surfaces séparées avec des données partielles, pas de synthèse hebdo |

### 2.2 Conséquence

Le produit a la **donnée** pour coacher (services scoring V2, reco, substitution, body tracking, coach report blocs Mesuré/Inféré, implicit signal scoring). Mais l'utilisateur ne **vit** pas cette boucle. Il vit un journal d'entraînement avec des onglets.

Sx_27 = livrer la **boucle quotidienne et hebdo** qui exploite ces données déjà-présentes.

## 3. État produit actuel (inventaire honnête)

### 3.1 Pages existantes (cf. `docs/AUTH_SCOPE_MATRIX.md`)

| Page | Rôle actuel | Pertinence pour la boucle |
|---|---|---|
| `GET /` | landing connecté, liste sessions + reco | **point d'entrée à activer** |
| `GET /launcher` | choix de séance | utile, mais doit citer la reco par défaut |
| `GET /history` | liste sessions paginée | OK pour lookup, pas pour synthèse |
| `GET /progress` | dashboard analytics | données utiles, présentation à raffiner |
| `GET /dashboard` | KPIs | redondant avec /progress et / — à clarifier |
| `GET /physique` | body tracking | utile en input pour reco/coach |
| `GET /coach-report` | 10 blocs Mesuré/Inféré/Non déductible | **donnée riche, mal exposée dans la boucle quotidienne** |
| `GET /sessions/{id}/done` | recap d'une séance terminée | **doit devenir un "session review"** vrai |
| `GET /science`, `/library`, `/rules` | catalogue méthodologique | référence — pas dans la boucle quotidienne |
| `/leaderboard`, `/users/{username}` | semi-public Sb_19 | hors scope coaching individuel |

### 3.2 Services existants à câbler ensemble

| Service | Fournit |
|---|---|
| `app/services/recommendation.py:recommend_next_session` | la séance suggérée + raison (zone freshness, fatigue) |
| `app/services/briefing.py` | un briefing pré-séance |
| `app/services/coach_report.py:build_report` | 10 blocs structurés Mesuré/Inféré/Non déductible |
| `app/services/coach_inference.py:build_inference` | inférences sur le report |
| `app/services/session_recap.py` | recap d'une session terminée |
| `app/services/implicit_signal.py` | scoring V2 + label implicite |
| `app/services/quality_score.py` | quality_score V2 (Sx_24) |
| `app/services/profile_metrics.py:build_preview` | radar + grade utilisé en leaderboard |
| `app/services/anomalies.py` | détection d'anomalies trends |
| `app/services/behavioral.py` | comportements (skip, completion ratio) |
| `app/services/dashboard.py`, `kpis.py`, `stats.py`, `delta.py`, `timeline.py` | data brute pour l'utilisateur |
| `app/services/progression_hint.py` | hint progression par exercice |
| `app/services/hints.py` | hints transverses |
| `app/services/confidence.py` | confiance des inférences |

**Constat** : tout est déjà construit. Sx_27 = **composition + UX**, pas reconstruction.

## 4. Capacités existantes réutilisables

Sx_27 doit explicitement **réutiliser** (et pas ré-implémenter) :

| Capacité | Source | Usage prévu |
|---|---|---|
| Reco "next session" déterministe | `recommendation.recommend_next_session` | Home dashboard + bloc "Pourquoi ?" |
| Zone freshness gradient 3 sessions | `recommendation._zone_freshness_bonus` (Sb_24.next.reco) | Pourquoi cette séance |
| Coach report 10 blocs | `coach_report.build_report` | Weekly loop + session review |
| Inférences coach | `coach_inference.build_inference` | Narrative déterministe |
| Implicit label per exercise | `implicit_signal._persist_implicit_labels_on_completion` (Sb_24.3) | Session review |
| Quality score V2 | `quality_score` + `scoring_version=2` | Session review + weekly |
| Substitution matrix | `substitution.py` (Sx_22) | Pourquoi alternatives proposées |
| Body radar + grade | `profile_metrics.build_preview` | Section "Je progresse ?" |
| Anomaly detection | `anomalies.py` | Section "Je dérive ?" |
| Backup-aware health | `/healthz/strict` enrichi (Sb_26.3) | hors UX produit, juste pour rappel |
| Performance budgets larges | `.performance-budget.json` (Sb_26.6) | les nouvelles routes doivent rester within budget |
| Rate limiter | Sb_26.4 | inchangé, les routes coaching restent authentifiées normalement |

**Aucune nouvelle dépendance Python.** Aucun nouveau service externe.

## 5. Non-goals

- ❌ Pas de **LLM obligatoire**. Si une narrative est livrée, elle est **déterministe** (templating + règles), pas générée. Un opt-in LLM ultérieur reste possible mais hors Sx_27.
- ❌ Pas de **React Native**. UI reste SSR Jinja2.
- ❌ Pas de **PostgreSQL**. SQLite reste la stack V1.
- ❌ Pas de **multi-tenancy**. Cf. `docs/MULTI_TENANT_READINESS.md`.
- ❌ Pas de **billing**, pas de paywall.
- ❌ Pas de **refonte UI complète**. Touches ciblées par page, pas de redesign system.
- ❌ Pas de **nouvelle table SQLAlchemy** au niveau métier. Les colonnes existantes suffisent (cf. §10).
- ❌ Pas de **migration Alembic** (le contrat Sx_26 "ADD COLUMN ONLY" reste, et même cela on essaie de l'éviter dans Sx_27).
- ❌ Pas de **modification du scoring** core (`quality_score`, `implicit_signal`, `recommendation`). On consomme, on ne ré-arbitre pas.
- ❌ Pas de **modification du flow auth**, du rate limiter, des observability/security/perf gates Sx_26.
- ❌ Pas de **gamification** type badges/streaks dans Sx_27 — option ultérieure si dogfood le réclame.
- ❌ Pas de **notifications push / email actives** — l'utilisateur ouvre l'app, pas l'inverse.
- ❌ Pas de **partage social** au-delà des squads existants (Sx_22).
- ❌ Pas de **suppression** de surfaces existantes (history, leaderboard, science) — elles restent accessibles mais ne sont plus le point d'entrée.

## 6. Hard contracts hérités de Sx_26

Tous les contrats durs de Sx_26 restent en vigueur sur Sx_27 (cf. `docs/strategy/Sx_26_CLOSURE_REPORT.md`). Les plus critiques pour ce cycle :

| HC-SX26-* | Verbatim | Mécanisme de surveillance |
|---|---|---|
| Snapshots historiques sacrés | `template_*_snapshot`, `exercise_*_snapshot`, `substituted_name`, `implicit_label`, `scoring_version` ne sont JAMAIS dropés ni mutés rétroactivement | `check_migration_patterns.py` |
| ADD COLUMN ONLY | convention par défaut sur toute migration | `check_migration_patterns.py` |
| `scoring_version` monotone | ne décroît jamais | review humaine + tests existants |
| Ruff budget | total ≤ 548 | `check_ruff_budget.py` |
| pip-audit clean | `--strict` | gate CI Sb_26.4 |
| gitleaks current tree | required | gate CI Sb_26.4 |
| Sentry / Discord / Sentry DSN | strictement opt-in | tests Sb_26.3 + Sb_26.4 |
| Rate limit `/login,/register,/forgot-password` | per-IP buckets, 429 sober | tests Sb_26.4 |
| Perf budgets | tous endpoints within `.performance-budget.json` p95 | gate CI Sb_26.6 |
| Scope auth isolation | cross-user 404, exports per-user, semi-public docs respectés | `tests/test_auth_scope_isolation.py` |
| Spec/process discipline | sprint report verdict, non-goals dans spec, registry à jour | `check_spec_protocol.py` + `check_auth_scope_matrix.py` |
| SonarCloud required | Quality Gate green | gate CI Sb_20.5 |

**Tout Sb_27.k qui violerait l'un de ces contrats doit être REJETÉ en GO/NO-GO review.**

## 7. Modèle fonctionnel cible

### 7.1 La boucle quotidienne (1 minute, 1 écran)

```
              ┌─────────────────────────────────────┐
              │       /  (Home — point d'entrée)    │
              │                                     │
              │  Aujourd'hui — Push A recommandé    │
              │  Pourquoi ? Pectoraux 5 j frais     │
              │  Triceps frais. Squat lourd hier.   │
              │                                     │
              │  [ Lancer Push A ]   [ Choisir ]    │
              │                                     │
              │  Hier — Pull B "intense"            │
              │  3 RPE rouges, 1 PR épaule.         │
              │                                     │
              │  Cette semaine — 3 séances faites,  │
              │  zone jambes en dette de fraîcheur. │
              └─────────────────────────────────────┘
```

Trois blocs sur `/` :
1. **Today** : la reco par défaut + "Pourquoi" en 1-2 lignes (déterministes).
2. **Last session** : récap qualitatif (label implicite, quality_score, anomalies notables).
3. **This week** : compteur séances + zone(s) en dette + signal trend.

### 7.2 La boucle hebdomadaire (≤ 3 minutes, 1 page)

Activée via un onglet ou un bouton "Bilan semaine" depuis Home :
- compteur séances + volume par zone (déjà calculable via `kpis.py`, `dashboard.py`)
- delta vs semaine précédente (cf. `delta.py`)
- 1 anomalie max mise en avant (`anomalies.py`)
- 1 hint actionnable (`hints.py`)
- lien vers `/coach-report` pour aller plus profond

### 7.3 Le post-séance (Session Review V1)

`/sessions/{id}/done` devient un vrai **session review**, pas un recap :
- label implicite global (déjà disponible via `implicit_signal`)
- quality_score V2 avec barème lisible
- top 3 mouvements remarquables (PR ? regression ? RPE rouge ?)
- 1 phrase déterministe : *« Séance dense — épaule 2 RPE rouges, à surveiller. »*
- bouton vers reco prochaine séance déjà calculée

## 8. Pages / routes impactées

| Route existante | Action Sx_27 |
|---|---|
| `GET /` | **refonte modérée du template** : ajout 3 blocs Today/Last/Week. Backend `pages.py` enrichi pour passer les payloads. |
| `GET /sessions/{id}/done` | **enrichissement** : nouveaux composants Jinja, réutilise `session_recap`, `implicit_signal`, `quality_score`, `anomalies`, `progression_hint` |
| `GET /coach-report` | **inchangé fonctionnellement**, mais lié explicitement depuis Home et Weekly. Possible ajout d'une narrative en tête (déterministe). |
| `GET /launcher` | **lien depuis Home** clarifié. Possible ajout du "Pourquoi" sur chaque option proposée. |
| `GET /progress` | revisité visuellement (pas refondu) ; renvoie vers le weekly loop |
| `GET /dashboard` | candidat à **fusion/dépréciation douce** avec Home, OQ-3 |
| `GET /history` | inchangé (page de lookup, pas de coaching) |

**Nouvelles routes éventuelles** (toutes facultatives, dépendent du découpage) :
- `GET /weekly` ou `GET /loop/week` : la page bilan hebdo (peut aussi être un sous-chemin de `/progress`).
- `GET /sessions/{id}/review` : si on sépare review et done. Probablement enrichissement de `/done` suffit.

Préférence par défaut : **pas de nouvelle route**, enrichir l'existant. À trancher par OQ-1.

## 9. Services impactés

Aucun service métier core n'est ré-écrit. Les services suivants peuvent être étendus **en composition** (nouvelles fonctions `build_home_payload`, `build_session_review`, `build_weekly_loop`) qui appellent ce qui existe déjà :

| Nouveau / Étendu | But |
|---|---|
| `app/services/home.py` (nouveau) | `build_home_payload(db, user, now)` → { today_reco, last_session_recap, weekly_summary } |
| `app/services/session_review.py` (nouveau) | `build_session_review(db, session)` → enrichit `session_recap` avec implicit_label, quality_score, anomalies |
| `app/services/weekly_loop.py` (nouveau) | `build_weekly_loop(db, user, now)` → { sessions_count, volume_by_zone, deltas, top_anomaly, hint } |
| `app/services/narrative.py` (nouveau, déterministe) | helpers pour générer 1-2 phrases templates depuis des dicts d'inférence. **Pas de LLM.** |

Aucun de ces services ne touche `scoring/`, `reco/`, `substitution.py`, `coach_report.py`, `body_tracking.py` internes. Ils **les appellent**.

**Pas d'ajout de modèle SQLAlchemy.** Pas de nouvelle table. Pas de nouvelle migration. Les colonnes nécessaires existent toutes (`implicit_label`, `scoring_version`, `quality_score`, `started_at`, `completed_at`, `excluded_from_stats`, etc.).

## 10. Données nécessaires (et déjà présentes)

| Donnée | Source | Sb concerné |
|---|---|---|
| `WorkoutSession.user_id` | model existant | scope auth Sb_26.7 |
| `WorkoutSession.status` | model existant | session lifecycle |
| `WorkoutSession.started_at` / `completed_at` | model existant | timeline |
| `WorkoutSession.template_*_snapshot` | model existant | reco context |
| `WorkoutSession.scoring_version` | Sb_24.5 | quality_score V2 dispatch |
| `WorkoutSession.quality_score` | Sb_24.5 | session review |
| `WorkoutSession.excluded_from_stats` | Sb_24.4 + admin | filtre weekly |
| `SessionExercise.implicit_label` | Sb_24.1 + Sb_24.3 hook | session review per-exercise |
| `SessionExercise.implicit_label_computed_at` | Sb_24.1 | freshness check |
| `SetLog.kind`, `weight_kg`, `reps`, `completed` | model existant | recap |
| Body measurements + readiness | tables existantes | weekly section |
| `template_exercise.method_id` | catalog | progression hint |
| Substitution graph | Sx_22 | "alternatives proposées" |

**Aucune nouvelle donnée à persister.** Toute la matière est déjà là.

## 11. UX cible (principes, pas wireframe)

### 11.1 Hiérarchie d'info

1. **Décision immédiate** : "Lance Push A". 1 ligne, 1 bouton.
2. **Contexte rapide** : "Pourquoi ?" 1 ou 2 raisons en 1 phrase.
3. **Mémoire courte** : "Hier" 1 ligne.
4. **Pulse hebdo** : "Cette semaine" 2 lignes.
5. **Approfondissement** : liens vers `/coach-report`, `/progress`, `/launcher` pour qui veut creuser.

### 11.2 Ton

- Bref, opérationnel ("Pectoraux frais"), pas littéraire ("Vos pectoraux se reposent depuis trois jours et bénéficieraient d'un stimulus…").
- Évite le jargon non-déjà-utilisé dans l'app.
- Aucune phrase ne ment : si une donnée est `Non déductible`, on le dit (réutilise le triptyche `Mesuré/Inféré/Non déductible` du coach report Sb_23).

### 11.3 Mobile-first

Toutes les nouvelles tuiles tiennent en un viewport mobile 360×640. Si une tuile ne tient pas, elle est repensée — pas mise dans un scroll horizontal.

### 11.4 Performance

Les nouvelles routes doivent respecter `.performance-budget.json` Sb_26.6. Si `/` ou `/sessions/{id}/done` dépasse, on optimise — on n'élargit pas le budget.

### 11.5 Accessibilité de base

- Contraste suffisant.
- Boutons ≥ 44×44px.
- Pas de seul-couleur pour signaler une info critique (un anomaly rouge a aussi un label texte).

## 12. Risques

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| Le "Pourquoi" déterministe sonne robotique | moyenne | UX faible | itération sur templates ; opt-in LLM dans un cycle ultérieur |
| Ajout de blocs sur `/` dégrade p95 | moyenne | gate CI Sb_26.6 casse | mesure locale + sub-services pré-calculés ; cache faible coût |
| Composition cassée si un service métier change | basse | régression silencieuse | tests de contract sur les payloads (pas sur les valeurs exactes) |
| Refonte Home casse l'expérience habituée | moyenne | friction utilisateur (toi) | dogfood interne avant merge final |
| `coach_inference` produit du bruit en l'absence de données | moyenne | tuiles vides ou trompeuses | utilisation du label `Non déductible` (Sb_23) explicite |
| Sx_27 dérive vers une refonte UI | moyenne | scope creep | Sb_27.6 sprint dédié "UX simplification pass" volontairement borné |
| `/dashboard` vs `/` vs `/progress` reste confus | élevée si on ne tranche pas | UX trouble | OQ-3 à trancher avant Sb_27.1 |
| L'utilisateur veut LLM tout de suite | basse | demande hors scope | doc OQ-2 documente la position |
| Tests d'isolation Sb_26.7 cassent si une nouvelle route oublie le scope | moyenne | gate CI | template `BUILD_SPRINT_PROMPT_TEMPLATE.md` impose l'ajout matrice |

## 13. Tests attendus

Chaque `Sb_27.k` doit livrer ses propres tests, et toutes les gates Sx_26 doivent rester vertes. Spécifiquement :

| Type de test | Surface | Sb concerné |
|---|---|---|
| Unitaires sur `build_home_payload` | dict shape, présence des 3 sous-payloads | Sb_27.1 |
| Unitaires sur `build_session_review` | shape + cas dégradés (no implicit_label, no quality_score) | Sb_27.2 |
| Unitaires sur `build_weekly_loop` | shape + cas zéro session, cas anomalie présente | Sb_27.3 |
| Snapshot tests sur les phrases narratives (chaînes templates) | éviter régression silencieuse | Sb_27.5 |
| Cross-user isolation sur nouvelles routes | aucune fuite | tous les Sb_27.k qui ajoutent une route |
| Tests d'accessibilité a minima sur templates (présence labels, alt) | Sb_27.6 |
| Perf smoke des nouveaux endpoints | within budget | toutes |
| Tests existants (975) ne régressent pas | tous | tous |

## 14. Découpage build Sb_27.1 → Sb_27.7

### Sb_27.1 — Home dashboard activation

**Objectif :** transformer `GET /` en point d'entrée coaching. Backend + template ; pas de nouvelle route.

**Livrables :**
- `app/services/home.py:build_home_payload(db, user, now)`
- Modification ciblée `app/routers/pages.py` (route `/`) pour passer le payload
- Modification template `app/templates/index.html` (3 nouveaux blocs Today / Last / Week — peut réutiliser partials)
- Tests : `tests/test_home_payload.py` (shape + cas dégradés)
- Matrice `AUTH_SCOPE_MATRIX.md` : route `/` annotée explicitement (déjà SELF, juste documenter l'enrichissement)

**Effort estimé :** M.

**DoD spécifique :**
- 975 + N tests passent
- `/` reste within budget perf
- aucun fichier scoring/reco/substitution/coach_report/body tracking touché
- pas de nouvelle migration
- pas de nouvelle table

### Sb_27.2 — Session review V1

**Objectif :** `GET /sessions/{id}/done` devient un session review (label implicite, quality_score, top 3 mouvements remarquables, 1 phrase déterministe).

**Livrables :**
- `app/services/session_review.py:build_session_review(db, session)`
- Modif `app/routers/sessions.py` route `/sessions/{id}/done` pour passer le payload (sans toucher `_load_session` ni `get_owned_session_or_404`)
- Modif template `app/templates/session_done.html`
- Tests : `tests/test_session_review.py` (shape, cas dégradé sans implicit_label, owner-only via test_auth_scope_isolation déjà couvert)

**Effort estimé :** M.

**DoD spécifique :**
- ownership inchangée (couvert par tests Sb_26.7)
- aucune touche `scoring/`, `implicit_signal.py`, `quality_score.py`

### Sb_27.3 — Weekly training loop

**Objectif :** livrer la page bilan hebdo. Décision OQ-1 : nouvelle route `/weekly` ou enrichissement `/progress`.

**Livrables :**
- `app/services/weekly_loop.py:build_weekly_loop(db, user, now)`
- Route choisie selon OQ-1
- Template
- Tests : `tests/test_weekly_loop.py` (cas semaine vide, cas avec anomalie, cas avec hint)
- Mise à jour matrice auth scope

**Effort estimé :** M.

### Sb_27.4 — Recommendation explanation

**Objectif :** rendre la reco "Today" lisible. Le "Pourquoi" en 1-2 lignes.

**Livrables :**
- Extension `recommendation.recommend_next_session` pour renvoyer un champ `reasons: list[str]` **déterministe** (déjà calculé internement, juste exposé) — si nécessaire, sinon helper séparé `build_reasons(reco_payload)`
- Réutilisation dans Home (Sb_27.1) et Launcher (lien)
- Tests : couvrir les 4-5 raisons types (zone freshness, fatigue, substitution, méthode, default)

**Effort estimé :** S-M.

**Note :** dépend de l'OQ-4 (modifier `recommendation.py` ou wrapper externe).

### Sb_27.5 — Deterministic coach narrative

**Objectif :** ajouter une couche narrative **déterministe** (templates + règles, pas LLM) sur le coach report et sur les blocs Today/Last/Week.

**Livrables :**
- `app/services/narrative.py` : helpers `narrate_session(session_review)`, `narrate_week(weekly_loop)`, `narrate_reco(reco_with_reasons)`
- Templates de phrases (Jinja ou Python f-strings, à trancher dans le sprint)
- Tests snapshot sur 5-10 cas typiques (zéro phrase inventée — si une donnée manque, on ne narre pas plutôt que de mentir)

**Effort estimé :** S.

**Hard contract spécifique Sx_27 :** la narrative ne ment jamais. Si la donnée est `Non déductible`, la phrase l'est aussi.

### Sb_27.6 — UX simplification pass

**Objectif :** simplification ciblée et **bornée** des écrans existants en complément des nouveaux blocs. Pas de redesign system.

**Livrables :**
- Décision OQ-3 (fusion ou clarification `/dashboard` vs `/`) appliquée
- Ajustements CSS et nav pour réduire la friction (boutons clairs, hierarchie verticale)
- Mise à jour `app/templates/base.html` si nécessaire (nav simplifiée)
- Tests : aucun test produit nouveau, mais tests d'accessibilité a minima (présence des labels, alt sur images) + tests existants verts
- Documentation : `docs/UX_SIMPLIFICATION_NOTES.md` traçant les choix

**Effort estimé :** S-M.

**Non-goal :** aucune refonte du flow de session capture, aucun changement de couleur palette de fond.

### Sb_27.7 — Product closure report

**Objectif :** dogfooder le cycle Sx_27 puis livrer le closure report.

**Livrables :**
- Dogfood report selon `docs/templates/DOGFOOD_REPORT_TEMPLATE.md` après une session d'usage réelle
- `docs/strategy/Sx_27_CLOSURE_REPORT.md` (synthèse, métriques, dettes, signal pour Sx_28)
- Mise à jour `SPEC_REGISTRY.md`

**Effort estimé :** S.

## 15. DoD globale du cycle Sx_27

Critères mesurables au niveau cycle (au-delà des DoD individuelles) :

- [ ] L'utilisateur ouvre `/` et a en moins de 5 secondes (perception) une réponse aux 5 questions §1
- [ ] 0 nouvelle migration Alembic créée
- [ ] 0 modèle SQLAlchemy modifié
- [ ] 0 service métier core touché (`scoring/`, `reco/`, `substitution.py`, `coach_report.py`, `body_tracking.py`, `implicit_signal.py`)
- [ ] Toutes les gates Sx_26 restent vertes (les 11 required + SonarCloud)
- [ ] Aucune route ne dépasse son budget p95 dans `.performance-budget.json`
- [ ] Tous les nouveaux endpoints sont entrés dans `docs/AUTH_SCOPE_MATRIX.md` et couverts par `tests/test_auth_scope_isolation.py`
- [ ] Aucun secret commité (gitleaks vert)
- [ ] Ruff budget ≤ 548 (idéalement on ratchet down si possible, mais pas dans le sprint principal)
- [ ] Une narrative ne ment jamais (test snapshot dédié)
- [ ] Le dogfood report Sb_27.7 valide ou invalide explicitement l'activation produit
- [ ] `docs/strategy/Sx_27_CLOSURE_REPORT.md` livré avec verdict explicite

## 16. Open questions (OQ-N)

### OQ-1 — Page bilan hebdo : nouvelle route ou enrichir `/progress` ?

| Option | Avantage | Coût |
|---|---|---|
| Nouvelle route `/weekly` | sémantique claire, surface dédiée | matrice à mettre à jour, nouvelle entrée perf budget, redondance avec `/progress` |
| Enrichir `/progress` | zéro nouvelle route, déjà dans la mind map utilisateur | risque de noyer la synthèse dans des graphiques détaillés |

**Recommandation par défaut :** enrichir `/progress` avec un encart "Cette semaine" en haut + lien Home. Pas de nouvelle route.

**Qui tranche :** opérateur. **Délai :** avant Sb_27.3.

### OQ-2 — LLM narrative dans Sx_27 ?

**Position par défaut :** non, narrative déterministe. Le LLM serait un cycle ultérieur (Sx_28+) opt-in via env var (analogie Sentry Sb_26.3). Sb_27.5 doit poser une **interface** pour qu'un futur backend LLM se branche, mais sans le brancher.

**Qui tranche :** opérateur. **Délai :** avant Sb_27.5.

### OQ-3 — `/dashboard` vs `/` vs `/progress`

Trois pages avec overlap. Tranche :

| Option | Détail |
|---|---|
| Fusionner `/dashboard` dans `/` | redirect 302 sur `/dashboard` |
| Garder `/dashboard` comme vue compacte mobile-only | clarifier le rôle |
| Déprécier `/dashboard` proprement | redirect + note + plan de suppression |

**Recommandation par défaut :** déprécier `/dashboard`, redirect vers `/`. Plan de suppression Sb_27.next ou plus tard.

**Qui tranche :** opérateur. **Délai :** avant Sb_27.6.

### OQ-4 — Étendre `recommendation.recommend_next_session` ou wrapper externe ?

Pour exposer les "raisons" :

| Option | Risque |
|---|---|
| Modifier `recommendation.py` pour renvoyer un champ `reasons` | touche un service core (interdit verbatim) |
| Wrapper externe (`app/services/recommendation_explainer.py`) qui ré-exécute la logique de scoring pour reconstruire les raisons | duplication, risque de divergence |
| Émettre les raisons via un side-channel (logger / debug payload) déjà existant à exploiter | possible si déjà disponible — à vérifier au début de Sb_27.4 |

**Recommandation par défaut :** vérifier d'abord si `recommend_next_session` renvoie déjà une trace structurée des bonus/malus appliqués. Si oui → consommer. Si non → wrapper externe minimal, **sans** modifier `recommendation.py`.

**Qui tranche :** opérateur. **Délai :** au démarrage Sb_27.4.

### OQ-5 — Mobile-first : viewport cible

Confirme-t-on **360×640** comme viewport référence pour valider la hiérarchie ?

**Recommandation par défaut :** oui (Android moyen). Tests visuels manuels en dogfood Sb_27.7.

**Qui tranche :** opérateur. **Délai :** avant Sb_27.1.

### OQ-6 — Ton de la narrative

Tu (informel) ou Vous (poli) ? Phrases impératives ("Lance Push A") ou suggestives ("Push A recommandé") ?

**Recommandation par défaut :** Tu informel + phrases courtes nominales ("Push A recommandé"). Cohérent avec un coach IRL.

**Qui tranche :** opérateur. **Délai :** avant Sb_27.5.

## 17. Verdict GO/WAIT

### Pré-requis pour GO Sb_27.1

| Critère | Statut |
|---|---|
| `Sx_26_CLOSURE_REPORT.md` livré + cycle clos | ✅ (2026-06-14) |
| `SPEC_DRIVEN_ENGINEERING_PROTOCOL_v1.md` en vigueur | ✅ |
| Toutes les gates Sx_26 vertes | ✅ run #27504865167 |
| Cette spec lue et validée par l'opérateur | ⏳ humain |
| OQ-5 (viewport) tranchée | ⏳ humain — recommandation par défaut acceptée si pas de retour |
| OQ-3 différable au Sb_27.6 | ✅ pas bloquant pour Sb_27.1 |

### Verdict

✅ **GO Sb_27.1** dès que :

1. L'opérateur a relu cette spec et acquiesce
2. L'opérateur confirme OQ-5 (viewport cible) — défaut 360×640
3. Aucune autre OQ ne bloque Sb_27.1 spécifiquement (OQ-1 et OQ-3 sont à trancher avant respectivement Sb_27.3 et Sb_27.6)

Si l'opérateur souhaite **trancher toutes les OQ en amont**, ouvrir un sprint dédié `Sb_27.0.amend-OQ` selon `docs/templates/AMENDMENT_TEMPLATE.md` — recommandé si la spec semble dépendre fortement d'OQ-2 (position LLM) ou OQ-4 (modif recommendation.py).

### ⏳ WAIT si

- OQ-2 tranche en faveur d'un LLM obligatoire dans Sx_27 → la spec change de nature, nécessite amendement §17bis
- OQ-4 révèle qu'il faut modifier `recommendation.py` → conflit avec hard contract "ne pas modifier les services scoring/reco core" → amendement obligatoire avant tout build
- Le dogfood post-Sx_26 (pas encore fait à la rédaction) révèle un blocker non-coaching (ex: un bug perf, un crash) → corriger d'abord en `Sb_26.next.<fix>`, puis revenir à Sx_27

### Position recommandée

✅ **GO Sb_27.1**, avec OQ-5 confirmée par défaut, et OQ-1 / OQ-3 / OQ-4 / OQ-6 différées au démarrage de leur Sb_27.k respectif.

OQ-2 (LLM) doit être tranchée **avant** Sb_27.5, mais ne bloque pas Sb_27.1 → 27.4.

---

**Statut de cette spec :** `DRAFT — READY FOR HUMAN REVIEW`
