# Sx_28 — Product Roadmap Reconciliation & Next Cycle Selection

> **Statut (amendé 2026-06-15 sprint Sb_28.override-build-authorization) :**
> Spec produite sous human override (cf. §2). **Build authorization a basculé** de `BLOCKED` à `AUTHORIZED FOR OPTION A` par décision humaine explicite, sans attendre le dogfood. Le dogfood Sx_27 reste **PENDING** — il n'est ni simulé, ni considéré acquis. Options B/C/D/E restent bloquées jusqu'à dogfood ou override séparé. Prochain cycle autorisé : **Sx_29 Mobile Session Focus Mode**. Voir §15 + §16 + §20.

**Auteur :** opérateur SPIGNOS + Claude Code (Opus 4.7).
**Date :** 2026-06-15.
**Version :** v1.
**Source de vérité officielle :** `docs/strategy/SPEC_REGISTRY.md` (table des cycles livrés).
**Document de reprise éditorial :** `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`.

---

## 1. Executive summary

Sx_28 produit la **réconciliation explicite** entre :
- l'ancienne roadmap conceptuelle S0→S10 (`SPIGNOS_EXERCISE_SYSTEM_ROADMAP.md`, daté 2026-04-14)
- l'état réel du repo en 2026-06-15 (post-clôture technique Sx_27)
- les cycles déjà livrés (Sx_24/26/27 + sprints historiques)
- les dettes techniques et produit restantes
- l'absence actuelle de signal dogfood réel (**DOGFOOD INPUT = PENDING**)

Conclusion provisoire (§15) : **Option A — Mobile Session Focus Mode / Logging Experience** est la recommandation par défaut une fois le dogfood reçu. Mais la spec **ne tranche pas** : elle prépare la décision humaine et bloque tout build en amont.

**Sx_28 STATUS :** `SPEC ONLY UNDER HUMAN OVERRIDE`
**BUILD AUTHORIZATION :** `BLOCKED UNTIL DOGFOOD OR EXPLICIT OVERRIDE`

## 2. Human Override Statement

`docs/strategy/ROADMAP_AND_NEXT_STEPS.md §2` (règle d'or spec-driven) interdit normalement d'ouvrir Sx_28 avant `Sb_27.dogfood-1`. L'opérateur autorise ici un **override délibéré et borné** :

| Override item | Décision opérateur |
|---|---|
| Ouverture de Sx_28 sans dogfood reçu | ✅ autorisée en **SPEC ONLY** |
| Ouverture d'un build `Sb_28.k` | ❌ **interdite** tant que dogfood pas reçu ou explicitement écarté |
| Ouverture de `Sx_29` ou plus | ❌ **interdite** sans Sx_28 mis à jour avec input dogfood ou override explicite |
| Modification de code applicatif dans Sx_28 | ❌ **interdite** (verbatim contrainte) |
| Délai annoncé du dogfood | ~2 jours (cible 2026-06-17) |

Cet override est une **dette de processus** assumée. Si le dogfood arrive en retard ou n'arrive pas :
- soit on attend (option par défaut)
- soit l'opérateur produit un **second override explicite** justifiant l'ouverture d'un build sans dogfood

**Toute violation des limites de l'override ci-dessus invalide Sx_28** et impose une remise à plat.

## 3. Source de vérité actuelle

| Document | Rôle |
|---|---|
| `docs/strategy/SPEC_REGISTRY.md` | **source de vérité officielle** des sprints livrés |
| `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` | document de reprise éditorial (anti-amnésie) |
| `docs/strategy/SPEC_DRIVEN_ENGINEERING_PROTOCOL_v1.md` | protocole verrouillant la méthodologie |
| `docs/strategy/Sx_26_CLOSURE_REPORT.md` | clôture cycle Sx_26 (Engineering Control Plane) |
| `docs/strategy/Sx_27_CLOSURE_REPORT.md` | clôture technique cycle Sx_27 (Coaching Loop) |
| `docs/dogfood/DOGFOOD_Sx_27_DEFERRED.md` | position formelle "dogfood deferred" |
| `docs/strategy/SPIGNOS_EXERCISE_SYSTEM_ROADMAP.md` | **roadmap historique S0→S10** (daté 2026-04-14, plus la source de vérité) |
| `docs/strategy/SPIGNOS_EXERCISE_SYSTEM_CONSOLIDATION_SPEC.md` | spec consolidation système exercices |
| `docs/SPRINT_SYNTHESIS.md` | synthèse handoff 2026-04-14 (478 tests à l'époque, archive) |

Sx_28 produit cette spec mais **ne devient pas une source de vérité concurrente** : il vit comme un instantané décisionnel daté qui sera invalidé ou confirmé par le dogfood.

## 4. État Sx_26 — Engineering Control Plane

✅ **Clôturé 2026-06-14.** Synthèse `Sx_26_CLOSURE_REPORT.md` :

| Lot | Domaine | Statut |
|---|---|---|
| Sb_26.1 | CI hardening (ruff budget, bandit, actionlint, shellcheck) | ✅ |
| Sb_26.2 | Migration hardening (snapshot, linter, roundtrip) | ✅ |
| Sb_26.3 | Observability (deploy_state, healthz strict, Sentry/Discord opt-in) | ✅ |
| Sb_26.4 | Security baseline (rate limit, pip-audit, gitleaks, Dependabot) | ✅ |
| Sb_26.5 | Spec/process discipline (templates + protocol + registry) | ✅ |
| Sb_26.6 | Performance baseline | ✅ |
| Sb_26.7 | Scope auth / multi-tenant readiness | ✅ |

**Hard contracts hérités vivants en Sx_28 :** SQLite, deploy manuel, snapshots historiques, ADD COLUMN ONLY, ruff budget locked, scoring_version monotone, scope auth isolation, perf budgets, pas de LLM obligatoire, Sentry/Discord opt-in.

## 5. État Sx_27 — Coaching Loop & Product Activation

✅ **Technically closed 2026-06-15.** Synthèse `Sx_27_CLOSURE_REPORT.md` :

| Lot | Domaine | Statut |
|---|---|---|
| Sb_27.1 | Home dashboard activation (Today/Last/Week) | ✅ |
| Sb_27.2 | Session Review V1 (`/sessions/{id}/done`) | ✅ |
| Sb_27.3 | Weekly training loop (`/progress`) | ✅ |
| Sb_27.4 | Recommendation explanation (wrapper externe) | ✅ |
| Sb_27.5 | Deterministic coach narrative | ✅ |
| Sb_27.6 | UX simplification (`/dashboard` deprecated) | ✅ |
| Sb_27.7 | Product closure report + dogfood deferred | ✅ |

**Métriques :** 975 → 1080 tests (+105), 0 migration, 0 modèle SQLAlchemy modifié, 0 service core touché, 0 nouvelle route, 0 hard contract violé, 6/6 OQ tranchées.

**Services créés (composition read-only) :** `home.py`, `session_review.py`, `weekly_loop.py`, `recommendation_explainer.py`, `narrative.py`.

**Surfaces enrichies :** `/`, `/progress`, `/sessions/{id}/done`.
**Surface dépréciée :** `/dashboard` → 303 → `/`.

## 6. Dogfood status

### ⏳ **DOGFOOD INPUT = PENDING**

Cf. `docs/dogfood/DOGFOOD_Sx_27_DEFERRED.md`.

| Item | État |
|---|---|
| Dogfood report formel `DOGFOOD_Sx_27_REPORT_<date>.md` | ❌ inexistant |
| Sessions réelles utilisateur exécutées | 0 |
| Critères de succès §3.3 du deferred doc | ⏳ ininstanciables sans données |
| Critères d'échec §3.4 | ⏳ idem |
| Cible humaine pour la livraison | ~2 jours (2026-06-17) |

**Sx_28 NE simule PAS de dogfood.** Aucune section ne suppose des retours utilisateur fictifs. Toutes les options §13 et la matrice §14 sont qualifiées par leur **dépendance dogfood** (cf. §14).

## 7. Ancienne roadmap S0→S10

Document source : `docs/strategy/SPIGNOS_EXERCISE_SYSTEM_ROADMAP.md` (daté 2026-04-14).

| Phase | Nom (verbatim conceptuel) | Date roadmap | Source |
|---|---|---|---|
| S0 | Baseline repo + benchmark | 2026-04-14 | roadmap conceptuelle |
| S1 | Signal exercice | 2026-04-14 | "Feedback Signal Refactor" |
| S2 | Mode séance focus | 2026-04-14 | mobile flow |
| S3 | Catalogue + taxonomie | 2026-04-14 | taxonomie musculaire |
| S4 | Substitution | 2026-04-14 | substitution graph |
| S5 | Recommandation surcharge | 2026-04-14 | next session reco + overload |
| S6 | Body tracking | 2026-04-14 | body metrics + photos |
| S7 | Body Engineering dashboard | 2026-04-14 | dashboard synthese |
| S8 | PWA premium | 2026-04-14 | service worker / offline |
| S9 | Health integrations prep | 2026-04-14 | future |
| S10 | API mobile prep | 2026-04-14 | future |

Cette roadmap reflétait l'intention produit en avril 2026. **2 mois de cycles intermédiaires (Sx_22, Sx_23, Sx_24, Sx_26, Sx_27) ont depuis absorbé une partie des phases**, et le repo n'est plus aligné avec l'ordonnancement original.

## 8. Mapping ancienne roadmap vs repo réel

| S# | Statut réel | Sprint(s) absorbant | Justification |
|---|---|---|---|
| S0 Baseline + benchmark | partiel / obsolète | Sx_26 (Control Plane) | CI baseline + perf baseline déjà livrés Sb_26.1/6, le "benchmark" S0 est moins pertinent |
| S1 Signal exercice | ✅ largement fait | Sb_01 + Sx_24 (implicit signal + quality V2) | success_score, implicit_label, scoring_version V2 livrés |
| S2 Mode séance focus | partiel | session detail existant, mobile partials | flux mobile présent, mais "focus mode" gym ultra-rapide pas livré → reste pertinent |
| S3 Catalogue + taxonomie | partiel | catalog QA + machine atlas (Sb_22) + substitution graph (Sx_22) | taxonomie normalisée encore consolidable |
| S4 Substitution | ✅ V1 fait | Sx_22 substitution graph + `substituted_name` | option canonique différée mais V1 fonctionnel |
| S5 Recommandation surcharge | partiel | Sx_27 (reco + explainer + narrative) | reco livrée, **surcharge progressive stricte non livrée** |
| S6 Body tracking | partiel | body metrics + readiness (Sb_22+) | photos/progression photos/source confidence non livrés |
| S7 Body Engineering dashboard | réorienté | `/dashboard` déprécié Sb_27.6 | valeur migrée vers `/`, `/progress`, `/physique` |
| S8 PWA premium | partiel | manifest + meta présents | service worker / offline / Lighthouse non livrés |
| S9 Health integrations prep | ❌ pas fait | — | reporté |
| S10 API mobile prep | ❌ pas fait | — | reporté |

**Conclusion** : **5/11 phases déjà absorbées ou réorientées**, **5/11 partielles**, **1/11 non commencée**. La roadmap historique ne tient plus comme séquence linéaire — elle devient un **inventaire de blocs candidats** à réorganiser selon le signal dogfood.

## 9. Ce qui est déjà fait

Capacités produit livrées et stabilisées (toutes couvertes par les 1080 tests verts) :

### 9.1 Boucle de coaching Sx_27
- Home `/` avec tuiles Today / Last / Week + narrative déterministe
- Session Review V1 `/sessions/{id}/done` avec quality + ressenti + mouvements remarquables + next_hint
- Weekly loop `/progress` avec count + delta + dominantes + anomaly + hint
- Recommendation explainer (wrapper externe, jusqu'à 3 raisons cumulables)
- Coach Report `/coach-report` (Sx_23) — 10 blocs Mesuré/Inféré/Non déductible

### 9.2 Signal exercice (S1 historique)
- `success_score` auto-dérivé (Sb_01)
- `implicit_label` per exercise (Sx_24)
- `quality_score` V2 + `scoring_version` monotone

### 9.3 Catalogue + taxonomie partielle (S3)
- Catalog QA + machine atlas (Sb_22)
- Référence `data/reference_split.json` + seed
- Muscle mapping + zones

### 9.4 Substitution V1 (S4)
- Substitution graph (Sx_22)
- `substituted_name` snapshot
- Atlas follows substitute (Sb_22a)

### 9.5 Engineering Control Plane (Sx_26)
- CI hardening (ruff budget, bandit, actionlint, shellcheck)
- Migration hardening (snapshot, linter, roundtrip)
- Observability (`/healthz/strict`, deploy_state, Sentry/Discord opt-in)
- Security baseline (rate limit, pip-audit, gitleaks, Dependabot)
- Spec/process discipline (protocol v1, registry, templates)
- Performance baseline (smoke + budget)
- Auth scope isolation + multi-tenant readiness

## 10. Ce qui est partiellement fait

### 10.1 Mode séance focus (S2)
- ✅ `/sessions/{id}` rend la session avec jump bar (Sb_05)
- ✅ Cards exercice avec sets, hints
- ❌ "Focus mode" optimisé gym (carte exercice active unique, gros tap targets, sticky CTA, timer repos, navigation E1/E2/E3 rapide)
- ❌ Fallback no-JS explicite documenté

### 10.2 Recommandation surcharge (S5)
- ✅ Reco next session (Sx_24)
- ✅ Explainer (Sb_27.4)
- ✅ Zone freshness gradient 3 sessions (Sb_24.next.reco)
- ❌ Surcharge progressive stricte (calcul next weight/reps cible par exercice, plateau detection, deload suggestion)
- ❌ Détection PR (Personal Records)

### 10.3 Body tracking (S6)
- ✅ Body measurements + readiness
- ✅ Profile body fields
- ❌ Progression photos
- ❌ Source confidence (mesure soi-même vs balance vs pro)
- ❌ Cohérence inter-mesures (alerter si saut brutal)

### 10.4 PWA premium (S8)
- ✅ `manifest.webmanifest`
- ✅ Meta tags mobile
- ❌ Service worker
- ❌ Cache offline
- ❌ Install prompt
- ❌ Lighthouse gates CI

## 11. Ce qui est obsolète

| Item | Pourquoi obsolète | Décision |
|---|---|---|
| S7 Body Engineering dashboard (route `/dashboard`) | Sb_27.6 a déprécié `/dashboard` → 303 → `/`. La valeur a migré dans `/`, `/progress`, `/physique`. | retirer S7 de toute roadmap future ; cleanup template/service candidat (`Sb_27.next.cleanup-dashboard`) |
| "Baseline repo + benchmark" S0 monolithique | Sx_26 a livré CI + perf baseline en 7 lots structurés. Refaire un S0 unique serait du re-work. | absorber dans Sx_26, ne pas réouvrir |
| Anciens patterns spec-driven pré-Sb_26.5 | Sb_26.5 a formalisé le protocole + templates + registry. | tout nouveau cycle utilise `SPEC_TEMPLATE.md` et `BUILD_SPRINT_PROMPT_TEMPLATE.md` |
| Discussion "fusion `/dashboard` vs `/`" (OQ-3) | Tranchée à Sb_27.6 (dépréciation propre, code préservé). | ne pas rouvrir sauf preuve dogfood |
| Mode V1 single-user (`user_id IS NULL` legacy) | Couvert par `ownership.py` + tests Sb_26.7. Sessions legacy filtrées naturellement. | rien à faire ; observation passive |

## 12. Ce qui reste produit-relevant

Classé par axe métier (pas par S-number ancien) :

### 12.1 Axe "logging en salle" — friction utilisateur en séance
- Focus mode mobile (S2 partiel)
- Sticky CTA + timer repos
- Navigation E1/E2/E3 rapide
- Fallback no-JS

### 12.2 Axe "signal de progression" — surcharge & PR
- Calcul surcharge stricte par exercice (S5 partiel)
- Détection PR + flag
- Deload suggestion sur plateau
- Compare cross-week sur metrics non-volumétriques

### 12.3 Axe "santé corporelle" — body engineering
- Progression photos (S6 partiel)
- Source confidence des mesures
- Cohérence inter-mesures + alerting
- Body composition timeline

### 12.4 Axe "qualité d'installation" — PWA & offline
- Service worker (S8 partiel)
- Cache offline du flux séance
- Install prompt
- Lighthouse gates CI

### 12.5 Axe "intégrations externes" — health / API
- Apple Health / Google Fit (S9 non commencé)
- API mobile native pour future app (S10 non commencé)
- Export iCal / Strava

### 12.6 Axe "cleanup & dette technique"
- Cleanup `dashboard.html` + `compute_dashboard` post-dogfood
- Ruff budget cleanup 548 → 534 (gain disponible, sprint dédié)
- Sentry release tracking auto
- Endpoints POST dans le perf benchmark
- Endpoints health/strict enrichis

## 13. Options de prochain cycle

Chaque option est documentée **sans préférence absolue** — la matrice §14 et la recommandation §15 viennent après.

### Option A — Mobile Session Focus Mode / Logging Experience
**Verbatim ROADMAP_AND_NEXT_STEPS.md §7.1.**

Refondre l'expérience `/sessions/{id}` mobile-first 360×640 pour réduire la friction en salle. Focus carte exercice active, jump bar rapide, sticky CTA, timer repos, no-JS fallback.

- **Cible utilisateur :** "logger en salle sans lever les yeux"
- **Surfaces :** `/sessions/{id}`, partials existants
- **Effort :** M-L (5 sprints prévisionnels `Sb_29.1-5`)
- **Dépendance dogfood :** ⚠️ moyenne — dogfood révèlera si la friction logging est vraiment le blocker n°1

### Option B — Progressive Overload Engine
Détection PR + calcul next weight/reps cible par exercice + plateau detection + deload suggestion.

- **Cible utilisateur :** "comprendre exactement ce que je dois faire la prochaine fois"
- **Surfaces :** nouveau service `overload_engine.py`, intégration dans reco + session review
- **Effort :** L (calculs scoring-adjacent, risque hard contract)
- **Dépendance dogfood :** 🔴 forte — sans dogfood, on ne sait pas si la friction est sur la reco ou sur le logging

### Option C — Body Tracking v2
Photos de progression + source confidence + cohérence inter-mesures + body composition timeline.

- **Cible utilisateur :** "voir mes changements corporels objectivement"
- **Surfaces :** nouveau service `body_tracking_v2.py`, modèles existants étendus
- **Effort :** L (storage photos = nouvelle infra légère, ou pas si on stocke seulement metadata)
- **Dépendance dogfood :** 🔴 forte — body tracking est une feature secondaire ; le dogfood doit confirmer l'intérêt

### Option D — PWA Premium
Service worker + cache offline du flux séance + install prompt + Lighthouse gates CI.

- **Cible utilisateur :** "utiliser l'app en salle même sans réseau"
- **Surfaces :** `app/static/sw.js`, `manifest.webmanifest`, CI Lighthouse
- **Effort :** M (cache strategy + tests offline)
- **Dépendance dogfood :** 🟡 moyenne — la friction réseau est concrète mais probablement pas le blocker principal vu que SSR Jinja2 fonctionne déjà

### Option E — Cleanup only
Pas de nouveau cycle produit. Adresser uniquement les dettes (ruff baseline, cleanup `/dashboard`, Sentry release tracking, perf POST endpoints, etc.).

- **Cible utilisateur :** aucune directe
- **Surfaces :** dispersées
- **Effort :** S-M (chaque cleanup ≈ 1-2 jours)
- **Dépendance dogfood :** 🟢 faible — utile en parallèle de toute option, **fallback recommandé si dogfood tarde**

## 14. Matrice valeur / risque / dépendance dogfood

| Option | Valeur utilisateur attendue | Risque technique | Dépendance dogfood | Coût estimé |
|---|---|---|---|---|
| **A — Focus Mode** | élevée si friction logging confirmée | basse (UI / partials, pas de scoring) | ⚠️ moyenne | M-L (~5 lots) |
| **B — Overload Engine** | élevée si reco insuffisante | **élevée** (touche au scoring-adjacent) | 🔴 forte | L (~6-8 lots) |
| **C — Body Tracking v2** | moyenne (feature secondaire) | moyenne (photos = nouvelle surface) | 🔴 forte | L |
| **D — PWA Premium** | moyenne (qualité d'installation) | basse (frontend uniquement) | 🟡 moyenne | M (~3-4 lots) |
| **E — Cleanup only** | aucune directe, valeur process | très basse | 🟢 faible | S-M (dispersé) |

### 14.1 Heuristique de décision

1. **Si dogfood révèle "friction logging" comme blocker n°1** → Option A
2. **Si dogfood révèle "reco insuffisante"** → Option B (mais préparer mitigation hard contract scoring)
3. **Si dogfood révèle "boucle OK, mais je veux suivre mon corps"** → Option C
4. **Si dogfood révèle "j'oublie d'ouvrir l'app"** → Option D (install prompt + offline)
5. **Si dogfood ne se fait pas dans 14-30 jours** → Option E (cleanup) + acter "indefinitely deferred"
6. **Si dogfood révèle un blocker spécifique** → `Sb_27.next.<fix>` avant tout nouveau cycle

## 15. Recommandation — DÉCISION SOUS OVERRIDE (amendé 2026-06-15)

> ⚠️ Le texte initial était "Recommandation provisoire" en attente de dogfood. **Amendement 2026-06-15 (sprint `Sb_28.override-build-authorization`) :** l'opérateur a décidé de basculer cette recommandation en **DÉCISION SOUS OVERRIDE EXPLICITE** sans attendre le dogfood Sx_27 (qui reste PENDING — non simulé, non considéré acquis).

**DÉCISION SOUS OVERRIDE — Option A : Mobile Session Focus Mode / Visual Interaction Layer.**

### 15.1 Justification

Verbatim Product Owner (cf. `ROADMAP_AND_NEXT_STEPS.md §7.1`) :

> Si le logging en salle n'est pas excellent, toute la couche recommandation/body analytics reposera sur un usage fragile.

L'ordre logique :
1. **Sx_29 (Option A)** — qualité du logging en salle d'abord
2. **Sx_30 (Option B)** — meilleure surcharge avec un meilleur signal logging
3. **Sx_31 (Option C)** — body tracking v2 si dogfood confirme l'intérêt
4. **Sx_32 (Option D)** — PWA premium pour stabiliser l'installation
5. **Sx_33+** — health integrations / API mobile

### 15.1bis — Portée et limites de la décision sous override

| Item | Décision opérateur |
|---|---|
| Option A (Mobile Focus Mode) | ✅ **AUTORISÉE** — build `Sx_29` peut être ouvert |
| Options B / C / D / E | 🔴 **RESTENT BLOQUÉES** jusqu'à dogfood ou override séparé |
| Stack | FastAPI SSR + Jinja2 **conservé** ; React **non autorisé en production** dans ce sprint |
| Lab React exploratoire | Acceptable comme proposition documentaire séparée plus tard ; **NON livré** dans le build principal Sx_29 |
| Dogfood Sx_27 | Reste PENDING. Si livré ultérieurement, peut **reverser** Option A et imposer un fix avant Sx_29 (cf. §15.2) |
| Sb_28.dogfood-integration | Reste **possible** plus tard pour absorber un dogfood reçu après bascule |
| Hard contracts Sx_26/Sx_27 | **Inchangés** — Option A doit les respecter verbatim |

### 15.2 Conditions de bascule vers une autre option (toujours actives malgré override)

Si le dogfood arrive plus tard et révèle l'un des signaux suivants, la décision Option A peut être réévaluée :

| Signal dogfood | Recommandation alternative |
|---|---|
| "Le logging est OK, je perds 0 sets, mais la reco ne me dit pas quoi pousser" | Option B en priorité |
| "Le logging est OK, je veux voir mon corps évoluer" | Option C en priorité |
| "Je ne pense pas à ouvrir l'app" | Option D + investigation push notif différée |
| "Crash / 500 / blocker fonctionnel" | `Sb_27.next.<fix>` AVANT tout nouveau cycle |
| Aucun retour exploitable | Option E (cleanup) + report dogfood |

## 16. Conditions pour ouvrir le prochain build — STATUT SATISFAIT PAR OVERRIDE (amendé 2026-06-15)

Le texte initial conditionnait l'ouverture d'un build à 6 critères dont le dogfood. Le sprint `Sb_28.override-build-authorization` (2026-06-15) substitue la voie OR (override explicite) à la voie AND (dogfood + recommandation finale). Le tableau ci-dessous est annoté.

| Condition | Statut post-override |
|---|---|
| Dogfood Sx_27 livré ET intégré dans Sx_28 (cf. §17) | ⏳ **non satisfaite** — dogfood reste PENDING ; **bypassée par override** ci-dessous |
| OU override explicite humain documenté | ✅ **SATISFAITE** — sprint `Sb_28.override-build-authorization` daté 2026-06-15, justification verbatim dans `docs/SPRINT_Sb_28_OVERRIDE_BUILD_AUTHORIZATION_REPORT.md` et `SPEC_REGISTRY.md` |
| Cette spec mise à jour avec recommandation FINAL (§15 sans "provisoire") | ✅ **SATISFAITE** — §15 renommée "DÉCISION SOUS OVERRIDE", "provisoire" retiré |
| Option retenue identifiée parmi A/B/C/D/E | ✅ **Option A — Mobile Session Focus Mode / Visual Interaction Layer** |
| Verdict §20 mis à jour vers `BUILD AUTHORIZED FOR <Option>` | ✅ **SATISFAITE** — §20 marquée `BUILD AUTHORIZED FOR OPTION A UNDER EXPLICIT HUMAN OVERRIDE` |
| Aucun blocker majeur révélé par dogfood non adressé | ✅ **SATISFAITE par défaut** — pas de dogfood = pas de blocker connu ; risque assumé par l'opérateur (cf. §16.bis) |

### 16.bis — Risques assumés par l'override

L'opérateur acte explicitement les risques suivants en autorisant le build sans dogfood :

| Risque | Mitigation prévue |
|---|---|
| Le dogfood futur pourrait révéler qu'Option A n'était pas le blocker prioritaire | §15.2 reste actif : possibilité de réévaluer Option A et imposer un fix avant la suite |
| Le build Sx_29 pourrait livrer une UX qui ne répond pas à la friction réelle | Sx_29 doit rester décomposable en sprints courts (`Sb_29.1-5`) avec dogfood léger entre chaque |
| L'override pourrait être réutilisé pour Options B/C/D/E sans rigueur | §15.1bis : override **borné à Option A uniquement** ; tout autre option nécessite un override séparé documenté |
| Lab React production sans contrôle | React **non autorisé en production** dans Sx_29 ; lab exploratoire séparé optionnel |

**Sb_28.k ou Sx_29 peut maintenant être ouvert.** Voir §20 verdict + `ROADMAP_AND_NEXT_STEPS.md §10` pour la séquence révisée.

## 17. Comment intégrer le dogfood dans ~2 jours

L'opérateur annonce une livraison dogfood d'ici ~2 jours (cible 2026-06-17). Protocole d'intégration :

### 17.1 Réception du dogfood

1. L'opérateur produit `docs/dogfood/DOGFOOD_Sx_27_REPORT_<YYYY-MM-DD>.md` selon `docs/templates/DOGFOOD_REPORT_TEMPLATE.md` (cf. `DOGFOOD_Sx_27_DEFERRED.md §3.5`).
2. Le report contient :
   - 5-7 sessions vécues sur 10-14 jours (ou justification d'un dogfood plus court)
   - réponses aux 5 questions §1 spec Sx_27
   - frictions ordonnées par fréquence
   - surprises positives / négatives
   - items à backloguer + items à NE PAS faire
   - verdict explicite ✅ / ⚠️ / ❌

### 17.2 Mise à jour de Sx_28

Une fois le dogfood reçu, **un sprint dédié `Sb_28.dogfood-integration`** met à jour cette spec :

| Section | Action |
|---|---|
| §6 Dogfood status | `PENDING` → `RECEIVED YYYY-MM-DD` |
| §13 Options | annoter chaque option avec signal dogfood pertinent |
| §14 Matrice | mettre à jour la colonne "Dépendance dogfood" → faits |
| §15 Recommandation | retirer "provisoire", trancher l'Option finale |
| §16 Conditions | cocher celles maintenant satisfaites |
| §20 Verdict | passer à `BUILD AUTHORIZED FOR <Option>` ou `BLOCKER FOUND, Sb_27.next.<fix> REQUIRED` |

Ce sprint d'intégration est lui-même SPEC ONLY. Il ne déclenche un build qu'à la **revue humaine finale**.

### 17.3 Si le dogfood ne se fait pas dans le délai annoncé

Cf. `DOGFOOD_Sx_27_DEFERRED.md §4` :
- 14 jours sans dogfood → "indefinitely deferred"
- 30 jours sans dogfood → un sprint `Sb_27.dogfood-1` dédié doit être ouvert AVANT tout cycle suivant

Si l'opérateur veut **outrepasser** ces seuils, un troisième override explicite est requis, daté et justifié.

## 18. Non-goals

**Sx_28 ne fait PAS** (verbatim contraintes user + protocole) :

- ❌ Pas de modification de code applicatif (`app/**`)
- ❌ Pas de modification de test applicatif (`tests/**`)
- ❌ Pas de migration Alembic
- ❌ Pas de nouveau modèle SQLAlchemy
- ❌ Pas de modification de service métier core (`scoring/`, `recommendation.py`, `reco/`, `implicit_signal.py`, `quality_score.py`, `coach_report.py`, `body_tracking.py`, `substitution.py`)
- ❌ Pas de modification de template
- ❌ Pas de réouverture de décisions tranchées (OQ-1 à OQ-6 Sx_27 + amendements Sx_26) sans preuve dogfood
- ❌ Pas d'inventaire fictif de retours utilisateur (DOGFOOD INPUT = PENDING, on ne simule rien)
- ❌ Pas de validation produit acquise (on prépare la décision, on ne la prend pas avant dogfood)
- ❌ Pas de démarrage de build `Sb_28.k` ou `Sx_29` (build authorization = BLOCKED)
- ❌ Pas de désactivation de gate Sx_26
- ❌ Pas de baisse de baseline ruff (548 inchangée)
- ❌ Pas de LLM
- ❌ Pas de pretention d'avoir épuisé l'espace des options (§13 liste 5 options ; le dogfood peut révéler une option F non envisagée)

## 19. Open questions

### OQ-A — Délai effectif du dogfood
Le délai annoncé est ~2 jours (2026-06-17). Que faire si le dogfood arrive sous une forme non conforme au template ?

**Recommandation par défaut :** accepter le report même s'il s'écarte du template, à condition qu'il contienne les réponses aux 5 questions §1 + le verdict explicite. Un report imparfait > pas de report.

**Qui tranche :** opérateur. **Délai :** au reception du dogfood.

### OQ-B — Que faire des sprints `Sb_27.next.*` candidates ?
La closure Sx_27 a identifié plusieurs candidats `Sb_27.next.*` (cleanup-dashboard, pr-detection, narrative-profile, etc.). Doivent-ils s'exécuter avant ou après le prochain Sx_ ?

**Recommandation par défaut :** sprints `Sb_27.next.<topic>` à statut **opportuniste** — peuvent être ouverts en parallèle ou en pause d'un cycle Sx_, ne bloquent rien, ne sont jamais prioritaires sur un signal dogfood.

**Qui tranche :** opérateur. **Délai :** au moment d'ouvrir un sprint `Sb_27.next.<topic>`.

### OQ-C — Sb_27.next.ruff-cleanup-N est-il acceptable en Sx_28 ?
La baseline ruff est à 548 alors que la mesure réelle est 534. Le gain de 14 warnings est disponible. Doit-on consolider la baseline maintenant ?

**Recommandation par défaut :** NON dans Sx_28 (qui est spec only). Oui dans un sprint dédié `Sb_26.next.ruff-cleanup-1` quand on aura un cycle build en cours et de la bande passante.

**Qui tranche :** opérateur. **Délai :** à l'ouverture d'un build `Sb_28.k` ou plus tard.

### OQ-D — Réintroduction de `/dashboard` post-dogfood ?
Si le dogfood révèle que l'utilisateur cherche encore une "vue body engineering synthétique", faut-il réintroduire `/dashboard` (template + service préservés) ?

**Recommandation par défaut :** NON par défaut. La valeur a migré vers `/`, `/progress`, `/physique`. Si dogfood révèle vraiment ce besoin, ouvrir un sprint dédié `Sb_27.next.dashboard-reintro` AVEC justification précise + une décision claire UX (nouveau positionnement, pas restauration verbatim).

**Qui tranche :** opérateur, post-dogfood. **Délai :** post-Sx_28.

### OQ-E — Option F : ce qu'on n'a pas envisagé
Le dogfood peut révéler un besoin non listé en §13 (e.g. "import historique de séances depuis Fitbod / Strong", "mode coach pour ami", "challenge hebdo en groupe").

**Recommandation par défaut :** rester ouvert. Si une Option F émerge, l'ajouter en §13 dans le sprint d'intégration §17.2, et l'évaluer dans la matrice §14.

**Qui tranche :** opérateur, post-dogfood. **Délai :** lors de la mise à jour Sx_28 post-dogfood.

## 20. Verdict — AMENDÉ 2026-06-15 (sprint `Sb_28.override-build-authorization`)

### ✅ **BUILD AUTHORIZED FOR OPTION A UNDER EXPLICIT HUMAN OVERRIDE**
### ⏳ DOGFOOD INPUT = PENDING (non simulé, non considéré acquis)
### 🔴 OPTIONS B / C / D / E RESTENT BLOQUÉES (override séparé requis pour chacune)

| Critère | Statut |
|---|---|
| Spec produite avec les 20 sections | ✅ |
| Dogfood input = PENDING (non simulé) | ✅ |
| Roadmap S0→S10 réconciliée vs repo réel | ✅ |
| 5 options de prochain cycle identifiées | ✅ |
| Recommandation tranchée | ✅ Option A (sous override 2026-06-15) |
| Conditions §16 satisfaites par override | ✅ (cf. §16) |
| Protocole d'intégration dogfood documenté | ✅ §17 (reste exécutable a posteriori) |
| Non-goals listés verbatim contraintes | ✅ §18 |
| Open questions identifiées | ✅ 5 OQ |
| `BUILD AUTHORIZATION` explicite | ✅ **AUTHORIZED FOR OPTION A** |
| Stack contrainte | ✅ FastAPI SSR + Jinja2 ; React production NON autorisé Sx_29 |
| Prochain cycle nommé | ✅ Sx_29 Mobile Session Focus Mode |

### Prochaine action autorisée

| Acteur | Action |
|---|---|
| Opérateur | Ouvrir `Sx_29` — Mobile Session Focus Mode (SPEC ONLY d'abord) |
| Agent | Produire `docs/strategy/Sx_29_MOBILE_SESSION_FOCUS_MODE_SPEC.md` selon le prompt verbatim de `ROADMAP_AND_NEXT_STEPS.md §7.3` |
| Opérateur (parallèle) | Continuer à viser le dogfood Sx_27 — son arrivée peut **reverser** Option A si elle révèle qu'une autre friction est prioritaire (§15.2) |
| Opérateur | Si besoin d'un lab React exploratoire, le proposer comme document séparé (hors build Sx_29) |

### Limites strictes de l'override

| Item | Limite |
|---|---|
| Options B (Overload) | 🔴 BLOQUÉE — override séparé requis |
| Options C (Body v2) | 🔴 BLOQUÉE — override séparé requis |
| Options D (PWA) | 🔴 BLOQUÉE — override séparé requis |
| Options E (Cleanup) | 🔴 BLOQUÉE — peut être ouverte à part comme `Sb_27.next.*` opportuniste, mais pas comme cycle Sx_ |
| React en production Sx_29 | 🔴 INTERDIT |
| Lab React exploratoire | ✅ acceptable comme proposition documentaire séparée, JAMAIS livrée dans le build principal Sx_29 |
| Skip de la phase SPEC ONLY pour Sx_29 | 🔴 INTERDIT — Sx_29 doit produire sa spec d'abord, comme tout cycle Sx_ |
| Skip des hard contracts Sx_26/Sx_27 dans Sx_29 | 🔴 INTERDIT |
| Réouverture des décisions tranchées Sx_27 (OQ-1 à OQ-6) | 🔴 INTERDIT sans preuve dogfood |

---

**Statut de cette spec :** `AMENDED — BUILD AUTHORIZED FOR OPTION A UNDER EXPLICIT HUMAN OVERRIDE`
**Build authorization :** `AUTHORIZED FOR OPTION A (Sx_29 Mobile Session Focus Mode) — Options B/C/D/E REMAIN BLOCKED`
**Dogfood Sx_27 :** `PENDING (non simulé, non considéré acquis ; peut reverser Option A si livré plus tard)`
**Stack :** FastAPI SSR + Jinja2 — React production non autorisé Sx_29
