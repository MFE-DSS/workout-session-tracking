# SPIGNOS — Synthèse Architecture, Industrialisation SaaS & Robustesse

**Date :** 2026-06-01
**Type :** Document de synthèse pour architecte amont — état des lieux complet.
**Audience :** architecte, prochaine itération de spec produit/technique.
**Périmètre :** code, métier, image produit, industrialisation, robustesse, garde-fous agent.

---

## A. Vue d'ensemble

SPIGNOS est une application web de suivi de séances de musculation et cardio, mobile-first, dark-theme, server-rendered. Hébergement self-hosted sur VPS OVH partagé avec deux autres sites (`varronotes.com`, `caracalla.co`). Stack monolithique Python/FastAPI sans frontend SPA.

| Identité | Valeur |
|---|---|
| Domaine prod | `spignos.com` |
| Repo | `MFE-DSS/workout-session-tracking` |
| Branche active | `claude/sprint-reporting-fitness-app-V7Qr6` |
| Volume code (LoC `app/`) | ~12 700 |
| Tests | 907 passing |
| Coverage | 89.97 % (SonarCloud confirmé) |
| Sprints livrés | ~30 (Sb_01 → Sb_24.next.reco) |
| Specs livrées | ~10 (Sx_05 → Sx_25) |

## B. Architecture technique

### B.1 — Stack

| Couche | Choix | Version | Rôle |
|---|---|---|---|
| Backend | FastAPI | 0.x | Routes HTTP + ownership + auth |
| Template | Jinja2 | latest | SSR — pas de SPA |
| ORM | SQLAlchemy 2.0 | Mapped declarative | Modèles + migrations |
| Migration | Alembic | Additive-only convention | 16 migrations Alembic à date |
| BD | SQLite | 3.x | Mono-fichier `var/workout.db`, backup quotidien |
| Auth | passlib bcrypt + itsdangerous | — | Cookie de session signé HMAC, pas de JWT |
| Cardio | Réutilisation `WorkoutSession.cardio_*` | — | Pas de capteur externe |
| Mobile | Responsive CSS, viewport 375 | — | `inputmode="decimal/numeric"` claviers |
| Style | CSS custom (~1500 LoC), pas de framework | — | Variables CSS, dark theme |
| JS | ~150 LoC `app/static/js/preview.js` | — | Vanilla, aucun framework |
| Worker | aucun | — | Tâches sync exclusivement |

**Principe directeur** : zéro client-state, zéro framework JS. Toute la logique métier est server-side, Jinja rend le HTML, aucun fetch métier post-load. L'unique JS (preview card sur leaderboard) reste cosmétique.

### B.2 — Structure du repo

```
app/
├── main.py                    # FastAPI app, mount routers
├── config.py                  # Pydantic Settings
├── database.py                # SessionLocal, init_db
├── deps.py                    # CurrentUser, DbSession FastAPI deps
├── enums.py
├── templating.py
├── models/                    # 9 fichiers Mapped declarative
│   ├── catalog.py             # WorkoutTemplate, TemplateExercise, RepTarget
│   ├── session.py             # WorkoutSession, SessionExercise, SetLog
│   ├── user.py
│   ├── readiness.py
│   ├── measurement.py
│   ├── squad.py
│   ├── challenge.py
│   └── sharing.py
├── routers/                   # 10 routeurs FastAPI
│   ├── auth_routes.py
│   ├── sessions.py            # le plus gros : ~700 LoC
│   ├── pages.py               # home, library, history, progress
│   ├── leaderboard.py
│   ├── coach_report.py
│   ├── readiness.py
│   ├── squads.py
│   ├── admin.py
│   ├── export.py
│   └── health.py
├── services/                  # 40+ fichiers, vrai cœur métier
│   ├── auth.py / ownership.py
│   ├── seed.py                # bootstrap catalogue
│   ├── recommendation.py      # moteur reco V2.1 (~700 LoC)
│   ├── substitution.py        # graphe N1/N2/N3 + cross-pattern
│   ├── implicit_signal.py     # 5 labels intra-exo
│   ├── quality_score.py       # scoring V1/V2 dispatch
│   ├── coach_report.py        # 10 blocs + agrégat 30j
│   ├── coach_inference.py     # règles déterministes
│   ├── profile_metrics.py     # primitives streak/cardio/zones
│   ├── muscle_scoring.py      # radar + grades
│   ├── leaderboard.py
│   ├── briefing.py            # chips + peek Sb_11a
│   ├── machine_atlas.py
│   ├── feedback.py / hints.py / progression_hint.py
│   ├── backup_verifier.py / backup_inspector.py
│   └── ~25 autres
├── static/
│   ├── css/app.css            # ~1500 LoC, variables + theme dark
│   └── js/preview.js          # ~150 LoC, vanilla
└── templates/                 # ~35 fichiers Jinja
data/                          # catalogues figés en JSON
├── reference_split.json       # v13 — 14 templates × 6-7 exos
├── exercise_properties.json   # 53 exos × {pattern_motor, muscle_group, …}
├── machine_atlas.json         # 8 familles × ~29 machines
├── cross_pattern_substitutions.json
├── module_cards.json
└── method_rules.json
docs/                          # 50+ rapports + specs
├── strategy/                  # 10 specs Sx_ formelles
├── SPRINT_*_REPORT.md         # ~30 rapports build
└── CICD_RUNBOOK.md, VPS_MULTISITE_RUNBOOK.md, SPRINT_INDEX.md
migrations/versions/           # 16 migrations Alembic
scripts/                       # CLI tooling
├── deploy_prod.sh
├── catalog_qa.py
├── catalog_pattern_qa.py
├── machine_atlas_qa.py
├── check_alembic_drift.py
└── audit_implicit_scoring.py
tests/                         # 907 tests
.github/workflows/             # ci.yml + deploy-production.yml
```

### B.3 — Modèle de données (extrait)

```
User (id, username, password_hash, email, is_active, height_cm, weight_kg, waist_cm, resting_hr, bp_*, coach_llm_enabled?)
  └─ WorkoutSession (template_slug_snapshot, template_name_snapshot, started_at, ended_at, status, scoring_version, creation_source, bodyweight_kg, cardio_*, concentration, global_state, free_note)
      └─ SessionExercise (exercise_code_snapshot, exercise_name_snapshot, position, success_score, muscle_sensation, substituted_name, implicit_label, implicit_label_computed_at)
          └─ SetLog (kind {warmup|work}, set_index, weight_kg, reps, rir, completed)
  ├─ BodyMeasurement, ReadinessEntry
  └─ SquadMembership, SquadInviteCode, SquadChallenge

WorkoutTemplate (slug, name, kind {strength|cardio}, focus, catalog_section, display_order)
  └─ TemplateExercise (code, name, set_scheme, notes, substitutes_json, machine_slug, machine_family)
      └─ RepTarget (min_reps, max_reps)
```

**Invariants critiques** :
- `template_slug_snapshot` + `template_name_snapshot` + `exercise_*_snapshot` sont des **snapshots dénormalisés** sur la session. La catalogue peut évoluer (v12→v13) sans réécrire l'historique.
- `substituted_name` permet la traçabilité prévu (snapshot) vs réalisé (substituted) — sacré, jamais touché par les sprints aval.
- `implicit_label` est figé à la complétion (Sx_24 §C, contrat dur).
- `scoring_version` est monotone (Sx_24 §H, jamais downgradé).

### B.4 — Pipeline d'inférence métier

```
                                    User ouvre /
                                          ↓
                            services.recommendation
                                          ↓
                  ┌───────────────────────────────────────────────┐
                  │   _compute_signals(db, user, now)            │
                  │   ├─ availability_by_zone (12 zones × récup) │
                  │   ├─ recent_strength_zones_by_session (N=3)  │
                  │   ├─ hard_sets_by_zone_24h / 7d / 14d        │
                  │   ├─ kinds_recent (cardio/strength alternance)│
                  │   ├─ days_since_last_cardio / strength       │
                  │   └─ fatigue_score (via behavioral engine)   │
                  └───────────────────────────────────────────────┘
                                          ↓
                  pour chaque template du catalogue :
                  _score_template(template, signals)
                  = availability·35 + zone_freshness + alternation + redundancy_penalty + …
                                          ↓
                  filtres : redundancy 24h, kind allowed
                                          ↓
                  top-1 + 2 alternatives + phrase d'explication
```

### B.5 — Pipeline scoring qualité

```
WorkoutSession.status passe à "completed"
                    ↓
hook _persist_implicit_labels_on_completion (Sb_24.3)
  ├─ pour chaque SessionExercise ≥ 3 work sets complétés :
  │   ├─ detect_intra_set_label(work_sets)
  │   └─ persist implicit_label + computed_at (jamais re-touché)
  └─ bump scoring_version 1→2

Plus tard, consommateurs (leaderboard / coach_report / /done) :
  compute_session_quality(session)
  ├─ if cardio : formule cardio (inchangée)
  ├─ if scoring_version == 1 : V1 (formule legacy bit-pour-bit)
  └─ if scoring_version == 2 : V2 = 0.75·V1 + 0.25·implicit_avg
```

## C. Architecture métier (domaine)

### C.1 — Cycles produit livrés (vue cumulative)

| Cycle | Sprints | Cible métier |
|---|---|---|
| Bootstrap (Sb_01-04) | catalog, sessions, scoring R3 | Saisie + log |
| Session System V1 (Sb_05-10) | flow horizontal, atlas, review | Expérience séance complète |
| Reco engine (Sb_11a → 18) | briefing chips, V1, V2 antagonist | Recommandation séance suivante |
| CI/CD (Sb_16.x) | GitHub Actions → OVH | Pipeline prod |
| Dogfooding fixpacks | wording, textarea, catalog v13 | UX en condition réelle |
| Security & Sonar (Sb_20.x) | coverage, ruff, bandit, hardening | Qualité statique + SAST |
| Substitution Gap Pack (Sb_22a + next) | N1/N2/N3 + muscle_group sous-zone | Graphe substitution agnostique |
| Profile Synthesis v2 (Sb_22b) | L1/L2/L3 + preview JS | Synthèse profil |
| Coach Report v1 (Sb_23) | 10 blocs SSR + print A4 | Synthèse coach externe |
| Cycle Sx_24 (Sb_24.1-8) | scoring implicite + V2 + UI pastilles | Effort inféré non déclaratif |

### C.2 — Catalogue exercices

- **16 templates** strength (push, pull, legs déclinés × intensité, upper/lower split) + cardio (liss-only, liss-abs)
- **53 exercices enrichis** dans `data/exercise_properties.json` avec `{pattern_motor, zone_primary, muscle_group, equipment_family, chain}`
- **8 familles machine × 29 machines** dans `data/machine_atlas.json` avec cues d'exécution + erreurs fréquentes
- **Graphe substitution N1/N2/N3** :
  - N1 = curé humain + 4 dimensions identiques
  - N2 = même pattern_motor + proximity ≥ 50
  - N3 = zone-only ou cross-pattern bridge

### C.3 — Système de scoring qualité

Formule strength **V1** (sessions pré-Sb_24.3) :
```
quality = 40 × (done_work_sets / total_work_sets)
        + 40 × (avg success_score / 100)
        + 10 × concentration_points
        + 10 × global_state_points
```

Formule strength **V2** (sessions post-Sb_24.3) :
```
quality = 0.75 × V1
        + 0.25 × avg(LABEL_SCORE_CONTRIBUTION[implicit_label] for exos labellés ≥ 3 sets)
```

Avec `LABEL_SCORE_CONTRIBUTION` : reserve_probable=30 / incoherent=50 / pyramidal_ascendant=70 / pyramidal_descendant=75 / trajectoire_coherente=90.

Si aucun label dans la session → V2 fallback sur V1 (égalité mathématique). Garantit l'invariance historique.

### C.4 — Système de recommandation

| Composante | Poids | Source |
|---|---|---|
| Availability by zone | 35 | `RECOVERY_HOURS_TARGET` (48-72h selon zone) |
| Zone freshness (3 dernières strength) | 15 → -6 gradient | Sb_24.next.reco |
| Alternation strength/cardio | 20 / 10 | Pénalise 2× même kind d'affilée |
| Redundancy penalty 24h | -5 par zone saturée | Évite double-séance même zone |
| Affinity core/utility/specialization | 10-20 | Templates affichés vs ignorés |
| Cardio absent bonus | +pondéré | Si > 7 jours sans cardio |
| Antagonist bonus (legacy) | conservé pour explanations | Phrase "tu as fait du push hier" |
| Fatigue penalty | dynamique | via `behavioral.compute_state` |

### C.5 — Privacy by design

- Aucune divulgation publique de détails de séance (set logs, notes, exercices)
- Leaderboard expose uniquement : username, grade, score, sessions/30j, radar agrégé
- Profile public `/users/{username}` : radar 30j + métadonnées si user les a saisies + dernière séance résumée
- Pas d'analytics tiers
- Pas de cookies sauf cookie de session signé

## D. Image produit / esthétique

### D.1 — Design system actuel

| Élément | Convention |
|---|---|
| Theme | Dark only, accent bleu `#4a9eff` |
| Typo | System UI stack (Inter / -apple-system) |
| Espacement | `--space-xs/sm/md/lg` via CSS variables |
| Border-radius | `--radius` (8px) / `--radius-sm` (4px) |
| Surfaces | `--surface` / `--surface-2` (élévation) |
| Tonalité | Sobre, no-emoji, minimal jaune-orange-vert pour les tags Mesuré/Inféré/Non déductible |
| Mobile-first | Optimisé 375px viewport, touch-friendly |
| Sans JS | SSR pur sauf preview leaderboard (~150 LoC vanilla) |

### D.2 — Conventions UX dégagées au fil des sprints

- **Carte active = jamais de verdict intrusif** — labels, suggestions, scores agrégés vivent uniquement en review/done/coach report/hints (Sx_24 §G Q1=C)
- **Triptyque `Mesuré` / `Inféré` / `Non déductible`** obligatoire sur le Coach Report (Sx_23 §B.bis)
- **Hiérarchie L1/L2/L3** sur leaderboard + profil (Sx_22b) — un score ne s'affiche jamais à 2 niveaux
- **Pas de PDF natif serveur** — print navigateur (Sx_25 décision verrouillée)
- **Catalogue v* monotone** — versionning catalogue figé, historique sessions intact

### D.3 — Branding

- Nom : SPIGNOS
- Mascotte/logo : aucune (texte simple)
- Voix : française uniquement, ton sobre, vocabulaire technique justifié
- Slogan implicite : « Suivi de séances honnête, sans bullshit, sans pub »

## E. Industrialisation SaaS

### E.1 — Architecture déploiement actuelle

```
Public Internet (HTTPS 443)
        ↓
host nginx (TLS termination + dispatch par server_name)
        ↓
   ┌────┴────┐
   │         │
spignos.com → 127.0.0.1:8000 (uvicorn systemd workout.service)
        ↓
SQLite var/workout.db (mono-fichier, ~5 Mo)

Autres apps partagent le VPS :
  varronotes.com → 127.0.0.1:3000 (Next.js varro.service)
  caracalla.co → 127.0.0.1:3001 + :5000 (Docker compose)
```

| Couche | État |
|---|---|
| VPS | OVH `vps-491c685f`, Ubuntu 24.04 LTS |
| host nginx | systemd, vhosts dans `/etc/nginx/sites-enabled/` |
| TLS | Let's Encrypt × 3 domaines, certbot.timer auto-renew |
| Process | uvicorn via `workout.service` systemd, auto-restart |
| BD | SQLite single-file, backup quotidien automatisé via `scripts/backup_*` |
| Logs | `journalctl -u workout`, nginx `/var/log/nginx/spignos.*` |
| Monitoring | aucun externe — voir §F.6 |
| Pre-flight check | `vps-preflight.sh` installé (diagnostic 3-sec) |

### E.2 — Maturité SaaS — état des lieux honnête

| Caractéristique SaaS | État |
|---|---|
| Multi-tenancy logique (séparation par user_id) | ✅ — toutes les queries filtrent sur `user_id` |
| Multi-tenancy infrastructure (1 DB par tenant) | ❌ — single SQLite partagé, OK V1 mais pas scale |
| Self-service signup | ✅ `/register` ouvert |
| Auth (cookie session signé) | ✅ |
| Reset mdp par mail | ✅ `/forgot-password` + SMTP configuré |
| Verification email | ❌ — `"@" in email` strict mais pas de confirmation |
| Rate limiting | ❌ — `/register` et `/login` non rate-limited (limit assumée Sx_20 §B.6) |
| 2FA | ❌ — pas envisagé V1 |
| Free tier vs paid | ❌ — modèle business non défini |
| Quotas / limits par tenant | ❌ |
| Billing / Stripe | ❌ |
| Multi-langue | ❌ — français uniquement |
| Multi-device sync | ✅ — cookie session, fonctionne sur tablet + mobile + desktop simultanément |
| Backup/restore par user | ❌ — backup global VPS, pas par tenant |
| Export user data (RGPD Art. 20) | ⚠️ — `/export/sessions.json` existe mais doit être vérifié RGPD-complet |
| Suppression de compte (RGPD Art. 17) | ❌ — pas de UI, faisable manuellement en BD |
| Conditions d'utilisation / Politique privacy | ❌ — non publiées |
| Mentions légales | ❌ — non publiées |
| Cookies bandeau | ❌ — pas de cookies analytics |
| Status page publique | ❌ |
| Uptime SLA | ❌ — pas formalisé |

**Verdict pragmatique** : SPIGNOS est un produit fonctionnel mais **pas un SaaS commercialisable** au sens strict. Bascule SaaS nécessite : (a) modèle business, (b) RGPD/CGU complets, (c) multi-tenancy infra propre, (d) rate-limiting, (e) status page + monitoring uptime externe.

### E.3 — Architecture multi-sites VPS

Le VPS héberge 3 sites distincts (spignos / varronotes / caracalla). Convention figée :

> **Aucune app ne bind `0.0.0.0:80` ni `0.0.0.0:443`. Seul host nginx voit l'extérieur. Toutes les apps écoutent en `127.0.0.1:<port>`.**

Garde-fous mis en place :
- `git update-index --skip-worktree` sur les compose files de caracalla pour empêcher git pull d'écraser nos patches
- `vps-preflight.sh` installé en `/usr/local/bin/` — diagnostic instant
- Runbook `docs/VPS_MULTISITE_RUNBOOK.md` — figeage architecture + procédures
- `systemctl enable nginx` — host nginx auto-restart au boot

## F. Robustesse du développement

### F.1 — Tests automatisés

| Catégorie | Nombre | Couverture |
|---|---|---|
| Total | 907 | 89.97 % lines (SonarCloud) |
| Fixtures | TestClient + SessionLocal en mémoire | par test, isolation forte |
| Tests E2E HTTP | ~150 (POST/GET via TestClient) | flow utilisateur |
| Tests unitaires services | ~600 | scoring, reco, substitution, signaux |
| Tests sécurité | ~20 (auth, ownership, headers) | Sb_20.3 |
| Tests migrations Alembic | 5 dédiés (Sb_24.1) + 1 drift check | détection drift au push |
| Tests paramétriques | nombreux (5 labels × cas × …) | combinatoire |

CI exécute la suite complète à chaque push (durée ~4min30).

### F.2 — Contrôle de code statique

| Outil | Statut |
|---|---|
| **ruff** | ✅ — config `[tool.ruff]` E/F/W/I/B/UP/S/C90, advisory en CI (continue-on-error: true) |
| **bandit** | ✅ — SAST, 0 Medium / 0 High, advisory |
| **SonarCloud** | ✅ — Quality Gate `Spignos Way`, required status check |
| **mypy** | ❌ — non configuré (décision Sx_20 §K) |
| **ide diagnostics** | ✅ — alerte temps réel via VS Code (cognitive complexity, etc.) |

### F.3 — SonarCloud Quality Gate

État au dernier scan :

| Métrique | Valeur | Grade |
|---|---|---|
| Coverage | 90.2 % | A |
| Bugs | 0 | A |
| Vulnerabilities | 0 | A |
| Security Hotspots | 0 | A |
| Maintainability (sqale) | 1.0 | A |
| Reliability | 1.0 | A |
| Security Review | 1.0 | A |
| Code smells | 105 | non bloquant |
| Quality Gate | **OK** ✅ | required status check |

### F.4 — CI/CD

Pipeline GitHub Actions (`.github/workflows/ci.yml`) :

```
push origin → 3 jobs parallèles :
  ├─ pytest + QA scripts (required)
  │    ├─ pytest --cov=app --cov-report=xml
  │    ├─ scripts/catalog_qa.py
  │    ├─ scripts/machine_atlas_qa.py
  │    ├─ scripts/catalog_pattern_qa.py
  │    ├─ scripts/check_alembic_drift.py
  │    └─ upload coverage-xml artifact
  ├─ ruff + bandit (advisory, continue-on-error)
  │    ├─ ruff check --output-format=github
  │    ├─ ruff format --check
  │    ├─ bandit -r app/ -ll
  │    ├─ ruff JSON for Sonar
  │    ├─ bandit JSON for Sonar
  │    └─ upload linter-reports artifact
  └─ SonarCloud (required)
       └─ ingère coverage.xml + ruff-report.json + bandit-report.json
```

Branch protection : `required_status_checks` = `pytest + QA scripts` + `SonarCloud`. `allow_force_pushes=false`, `allow_deletions=false`.

Deploy production (`deploy-production.yml`) :
- `workflow_dispatch` manuel (jamais auto)
- SSH-only avec clé restreinte au user `deploy` + sudoers minimal
- Étapes : backup BD → `git pull` → `alembic drift check` → `alembic upgrade head` → seed catalog → `systemctl restart workout` → smoke test
- Tag prod `prod/YYYY-MM-DD-HHMM-<sha>` poussé au repo

### F.5 — Garde-fous migrations

Convention figée tout au long du projet :
- **ADD COLUMN only** — jamais d'`UPDATE` sur lignes existantes
- **Server defaults** pour les valeurs NOT NULL
- **Pas de réécriture historique** sacralisée (Sx_24 §H)
- Drift check à chaque CI (`check_alembic_drift.py`)
- 16 migrations cumulées sans incident en prod

### F.6 — Monitoring runtime

| Couche | État |
|---|---|
| Erreurs serveur applicatives | ❌ — pas d'agrégateur (Sentry, etc.) |
| Erreurs nginx | journalctl + logrotate par défaut |
| Uptime externe | ❌ — pas d'UptimeRobot ou équivalent |
| Métriques perf (latence, taux d'erreur) | ❌ — pas de Prometheus / Grafana |
| Backup BD | ✅ — script quotidien, retention 30j |
| Alertes auto | ❌ — aucune notification push/email |

**Conclusion** : un crash d'app ou un site down n'est détecté que par le user manuellement. Documenté `docs/VPS_MULTISITE_RUNBOOK.md` §8.

### F.7 — Méthodologie de développement — anti-drift agent

Le projet est développé par un binôme **humain + agent Claude Code**. Le risque de drift (agent qui implémente sans cadrage, qui surévalue, qui rentre dans une dette technique invisible) a été méthodiquement réduit par les conventions suivantes :

#### F.7.1 — Spec-first

Chaque cycle commence par un sprint `Sx_NN` (spec only) :
- Aucune ligne de code applicatif touchée
- Document `docs/strategy/SPIGNOS_*_SPEC_v*.md` rédigé exhaustif
- Validation humaine explicite (« GO Sx_NN ») avant ouverture du build
- Le build `Sb_NN` cite la spec verbatim en commentaire de code

Cycles spec/build typiques observés : Sx_20 → Sb_20.1-5 / Sx_21 → Sx_22a + Sx_22b + Sx_23 / Sx_24 → Sb_24.1-8.

#### F.7.2 — Lotissement obligatoire

Aucun sprint build > 8 lots. Sb_24 a été lotté en 8 sous-sprints (Sb_24.1 → Sb_24.8) avec validation humaine entre chaque lot (« GO next » explicite). Limite la surface d'erreur et permet le rollback granulaire.

#### F.7.3 — Tests comme contrat

Chaque sprint build livre des tests qui **expriment littéralement les contrats du spec**. Exemples :
- `test_v1_session_returns_legacy_score` (Sx_24 §H invariance V1)
- `test_curated_cross_pattern_demoted_to_n3` (Sx_22a §C.3 garde-fou)
- `test_re_finish_keeps_first_label_intact` (Sx_24 §C "figé à la complétion")

Si un futur sprint casse l'un de ces tests, le contrat est violé → red gate.

#### F.7.4 — Hard contracts en spec

Les specs récentes (Sx_21 amendments, Sx_24, Sx_25) incluent des sections « contrats durs » avec :
- Listes d'interdits stricts (ex : Sx_25 §C interdit jugement esthétique au LLM)
- Vocabulaire fermé (triptyque `Mesuré`/`Inféré`/`Non déductible`)
- Garde-fous numériques (w_implicit conservatrice à 0.25, scoring_version monotone)

L'agent ne peut pas « réinterpréter » ces verrous sans qu'un test casse.

#### F.7.5 — Dogfooding loop intégré

Le framework méta-spec Sx_21 oblige à classifier chaque retour dogfood selon 6 catégories :
- Bug réel
- Lacune UX
- Lacune de recommandation
- Lacune de graphe de substitution
- Lacune de synthèse analytics
- **Lacune de modèle de signal**

Un retour n'est pas « fixé » tant que sa **classe** n'est pas adressée. Évite les patch locaux récurrents.

#### F.7.6 — Verdict explicite à chaque sprint

Chaque sprint report contient une recommandation explicite signée par l'agent : `✅ Sb_NN+1 PRÊT` ou `⏳ attendre dogfood`. L'humain garde la décision finale. Trace d'audit pour reconstituer les arbitrages.

#### F.7.7 — Skip-worktree sur l'infra VPS

Les fichiers compose de caracalla (sur le VPS, hors du repo SPIGNOS) ont été marqués `git update-index --skip-worktree` après modification locale, pour empêcher un git pull de réécraser les port mappings — incident reproduit 2 fois avant d'être verrouillé.

#### F.7.8 — Conventions de commentaires sourcés

Tout commit non-trivial cite la spec source en commentaire de code (`# Sb_24.3 — persist implicit labels at completion (Sx_24 §C, §D.2)`). Permet de retracer pourquoi une ligne existe sans consulter git log.

### F.8 — Couches de défense contre la régression

```
Code écrit
    ↓
IDE diagnostics (ruff + Python LSP) → boucle locale rapide
    ↓
Tests unitaires pertinents (~5s par fichier)
    ↓
Full suite (~4min30) avant commit
    ↓
CI : pytest + lint + Sonar Quality Gate
    ↓
required status checks branch protection
    ↓
deploy_prod.sh : drift check + alembic upgrade + smoke test
    ↓
Dogfood humain en salle (1-3 séances avant validation)
```

7 couches dont 5 automatisées + 2 humaines. Le moindre relâchement (skip-worktree mal positionné, advisory au lieu de required, etc.) est documenté comme dette.

### F.9 — Limites assumées du dispositif

1. **Pas de mypy** — typages partiels, certaines erreurs runtime possibles
2. **Pas de mutation testing** — coverage 90 % mais qualité d'assertion non auditée
3. **Pas d'audit de dépendance auto** — `dependabot` non configuré
4. **Pas de fuzzing** — surface HTTP non testée adversariellement
5. **Pas de load testing** — capacité de charge prod inconnue
6. **Pas de chaos engineering** — résilience inconnue face à crash BD, disque plein, etc.
7. **Monitoring runtime absent** — détection incident humaine

## G. Synthèse pour l'architecte

### G.1 — Ce qui est solide

- **Domaine métier** finement modélisé, snapshots dénormalisés bien pensés
- **Méthodologie spec-first** disciplinée, contrats durs respectés
- **CI/CD** mature avec 3 jobs + Quality Gate Sonar required
- **Tests** denses (907) avec couverture honnête (89.97 %)
- **Stack simple** (FastAPI + Jinja + SQLite) sans dette de framework
- **Migrations** additives, historique sacralisé
- **Privacy by design** — aucune fuite par construction
- **Anti-drift agent** — garde-fous multicouches éprouvés sur ~10 cycles

### G.2 — Ce qui demande une décision produit avant le code

- **Modèle SaaS / business** — gratuit vs payant, quotas, qui est cible ?
- **RGPD / CGU / mentions légales** — pré-requis pour ouvrir l'accès public
- **Multi-tenancy infra** — SQLite mono-fichier scale à ~quelques centaines d'users V1, faut-il anticiper ?
- **Internationalisation** — français only freine la cible
- **Mobile app native** — pas de React Native / Capacitor envisagé, est-ce un manque ?
- **Coach payant intégré** — modèle marketplace potentiel non spec
- **Analytics produit** — aucun, faut-il instrumentaliser ?

### G.3 — Dette technique connue, classée par priorité

| Priorité | Item | Effort |
|---|---|---|
| **P0** | Monitoring uptime externe (uptimerobot ou self-hosted) | 2h |
| **P0** | Rate limiting `/register` + `/login` | 3h |
| **P1** | Sentry intégration côté SPIGNOS | 4h |
| **P1** | RGPD : export complet user + delete account | 8h |
| **P1** | CGU / Politique privacy / Mentions légales | rédactionnel |
| **P2** | Mypy + typage progressif | 16h |
| **P2** | Dependabot configuration | 1h |
| **P2** | mutation testing (mutmut ou cosmic-ray) | 8h |
| **P3** | Load testing baseline (locust) | 4h |
| **P3** | Migration SQLite → Postgres pour multi-tenancy infra | 40h |
| **P3** | i18n (gettext + français/anglais) | 24h |

### G.4 — Spec candidates pour le prochain cycle

À arbitrer selon priorité business :

1. **Sx_26 — Monetization & accounts management** — modèle de comptes, plan gratuit/payant, billing
2. **Sx_27 — RGPD compliance** — export, suppression, audit log
3. **Sx_28 — Postgres migration + multi-tenancy infra** — préparation scale
4. **Sx_29 — Mobile app PWA + offline** — étendre l'usage mobile
5. **Sx_30 — Coach marketplace** — coach humain payant dans l'app
6. **Sb_25 (déjà spec'é) — Coach Report v2 LLM narratif** — feature différenciante

### G.5 — Indicateurs de santé en sortie

| Indicateur | Valeur | Verdict |
|---|---|---|
| Test passing | 907 / 907 | ✅ |
| Coverage | 89.97 % | ✅ |
| SonarCloud Quality Gate | OK | ✅ |
| Bugs / Vulnerabilities | 0 / 0 | ✅ |
| Migrations sans incident | 16 / 16 | ✅ |
| Sprints livrés sans rollback | ~30 / ~30 | ✅ |
| Specs validées et tracées | 10+ | ✅ |
| Production uptime (estimation) | non mesuré | ⚠️ |
| User actifs | 1 (créateur) | informatif |

---

## H. Verdict synthétique

SPIGNOS est un **produit ingénieré avec discipline**, doté d'un domaine métier riche (scoring, reco, substitution, coach report), d'une CI/CD mature et d'une méthodologie agent éprouvée. La robustesse statique et dynamique du code est conforme aux standards d'une équipe sérieuse.

En revanche, il n'est **pas un SaaS commercialisable en l'état** : modèle business non défini, RGPD non outillé, monitoring runtime absent, multi-tenancy infra non scalée, rate limiting manquant.

La prochaine itération de spec devrait arbitrer entre :
- **Verticaliser** (Sx_26 monétisation, Sx_27 RGPD, Sx_29 PWA) — transformer en SaaS commercialisable
- **Approfondir** (Sb_25 LLM narratif, autres améliorations métier) — pousser la singularité du produit dogfooded
- **Industrialiser** (Sx_28 Postgres, monitoring, load testing) — anticiper l'ouverture publique

Choix entre ces 3 axes = décision produit, pas technique.
