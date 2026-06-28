# Sx_31 — Body Intelligence v2 — Closure Report

**Spec source :** `docs/strategy/SPIGNOS_BODY_INTELLIGENCE_V2_SPEC.md`
**Date closure :** 2026-06-28
**Statut :** ✅ **TECHNICALLY CLOSED** — dogfood device réel PENDING.
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`

---

## 1. Statut final du cycle

**Sx_31 TECHNICALLY CLOSED.** Tous les sprints livrés et validés en CI.
**Dogfood Sx_31** = PENDING (template prêt : `docs/dogfood/DOGFOOD_Sx_31_BODY_INTELLIGENCE_TEMPLATE.md`).

Sx_31 a livré une **couche de lecture corporelle dérivée de l'entraînement** consolidée sur 2 surfaces SSR (`/body/intelligence` page complète + `/coach-report` snapshot compact), strictement pilotée par un composer pur déterministe. Aucune dépendance externe, aucun JS, aucune migration, aucun service métier core muté.

## 2. Sprints livrés

| Sprint | Objet | CI run | Tests Δ |
|---|---|---|---|
| Sx_31 (spec) | Body Intelligence v2 SPEC ONLY (§A-P) | [28300352085](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28300352085) ✅ | 0 |
| Sb_31.1 | `body_intelligence.py` composer pur — 5 états, 7 blocs, 9 seuils figés, dataclasses frozen | [28302706112](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28302706112) ✅ | +38 |
| Sb_31.2 | Route `GET /body/intelligence` + I/O layer + template SSR + CSS dédié | [28317125588](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28317125588) ✅ | +30 |
| Sb_31.3 | Snapshot Body Intelligence dans `/coach-report` (template seul) | [28319392397](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28319392397) ✅ | +23 |
| Sb_31.4 | A11y consolidation + responsive 360px + perf p95 | [28321554285](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28321554285) ✅ | +28 |
| Sb_31.5 | Closure docs + dogfood template (ce sprint) | (post-push) | 0 |
| **Total** | **6 sprints**, 5 CI vertes (+ Sb_31.5 doc) | | **+119** dédiés |

## 3. Architecture finale

```
┌──────────────────────────────────────────────────────────────────┐
│                  Sx_31 Body Intelligence v2                       │
│                                                                   │
│   build_body_intelligence_input(db, user)        ← Sb_31.2 I/O   │
│              compose en lecture seule :                           │
│              • profile_metrics.* (zone counts, dom pattern...)    │
│              • coach_report._weight_trend_90d / _work_sets_pw    │
│              • quality_score.compute_session_quality (moy 30j)    │
│              • confidence.compute_confidence_score (moy 30j)      │
│              • SessionExercise.implicit_label (agrégat 30j)       │
│              • BodyMeasurement (latest) + User.height/waist       │
│              → BodyIntelligenceInput (frozen dataclass)           │
│                                                                   │
│                            │                                      │
│                            ▼                                      │
│   compute_body_intelligence(input)               ← Sb_31.1 pur   │
│              • 7 blocs émis (toujours) avec classification        │
│                Mesuré / Dérivé / Inféré / Hors de portée          │
│              • Arbre priorité 6 étages, déterministe, cap 3       │
│              • 9 seuils figés en constantes nommées               │
│              • Wording sobre, non autoritaire (12 tokens scannés) │
│              → BodyIntelligenceSnapshot (frozen)                  │
│                                                                   │
│                            │                                      │
│              ┌─────────────┴─────────────┐                       │
│              ▼                           ▼                        │
│   /body/intelligence            /coach-report > snapshot block   │
│   (page complète)               (1bis, compact)                  │
│   Sb_31.2 + a11y Sb_31.4        Sb_31.3 + a11y CTA Sb_31.4      │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

**Discipline architecturale Sx_31 confirmée par 4 sprints :**
- Composer = seule source de vérité métier
- Couche I/O isole les accès DB
- Router orchestre uniquement
- Template lit uniquement les champs déjà calculés
- Aucune duplication de seuils ; aucune logique métier dans router/template (tests garde structurels)

## 4. Surfaces touchées

| Surface | État au sortir de Sx_31 |
|---|---|
| `/body/intelligence` | **NEW** — page SSR complète mobile-first, 7 blocs, badges classification, priorités cap 3, limites always-on |
| `/coach-report` | MODIFIED — bloc `1bis. Snapshot Body Intelligence` inséré entre Identité (1) et Volume (2). Service intact. Format A4 préservé. |
| `/profile` | **inchangé** (lien `/profile → /body/intelligence` différé, OQ-G) |
| `/physique` | **inchangé** (vue analytique 11 zones complémentaire) |
| `/progress` | **inchangé** |
| `/` (home) | **inchangé** (carte home différée, OQ-F) |
| `/u/{user}` | **inchangé** |

## 5. Contrats respectés

| Contrat | Statut |
|---|---|
| FastAPI SSR + Jinja2 + SQLite | ✅ stack inchangée |
| Pas de React / SPA / bundler / dep externe | ✅ |
| Pas de JS introduit Sx_31 | ✅ 0 nouveau fichier JS |
| Pas de migration Alembic | ✅ |
| Pas de modèle SQLAlchemy nouveau | ✅ |
| Pas de service métier core muté | ✅ `profile_metrics`, `muscle_scoring`, `quality_score`, `implicit_signal`, `confidence`, `coach_report`, `radar`, `overload_*`, `substitution`, `recommendation`, `body_tracking` tous intacts |
| `coach_report.py` service strictement intact | ✅ test garde explicite Sb_31.3/4 |
| No-JS fallback intégral | ✅ `<details>` natif, role="status", aucun JS requis |
| Mobile 360×640 | ✅ media query stricte + collapse kv + wrapper safety |
| WCAG 1.4.1 non-color cues | ✅ status (?, ~, •) + classification (●, ◆, ▲, ○) + priority (ℹ ⚠ ↘ ⇆ ↻ ✓) |
| WCAG 2.4.6 / 4.1.2 (headings + labels) | ✅ h1 unique + h2 par bloc + aria-labelledby + aria-label sur CTA |
| Vocabulaire non autoritaire / non médical / non esthétique | ✅ 12 tokens scannés par 3 tests garde |
| Distinction Mesuré / Dérivé / Inféré / Non déductible | ✅ badge visible sur chaque bloc + bloc limits always-on |
| Ruff budget ≤ 548 | ✅ 529 (inchangé sur tout le cycle) |
| Dogfoods Sx_27 et Sx_30 restent indépendamment pending | ✅ |

## 6. OQ Sx_31 — état final

| OQ | Décision | Implémentation |
|---|---|---|
| OQ-A : route name | `/body/intelligence` (collision `/body` résolue) | ✅ Sb_31.2 |
| OQ-B : CSS extrait | `body_intelligence.css` dédié, chargé conditionnellement | ✅ Sb_31.2 |
| OQ-C : seuils figés V1 | 9 constantes nommées en haut du composer | ✅ Sb_31.1 |
| OQ-D : BMI dérivé + disclaimer | `bmi_classification="derived"` + `bmi_disclaimer` dans content | ✅ Sb_31.1 + Sb_31.2 |
| OQ-E : overload compliance non V1 | `overload_compliance_status="not_available_v1"` exposé dans bloc limits | ✅ Sb_31.1 |
| OQ-F : carte home | **Différée** `Sb_31.next.home-card` | ⏳ |
| OQ-G : lien `/profile → /body` | **Différée** `Sb_31.next.profile-link` | ⏳ |

**5/7 OQ implémentées, 2/7 explicitement différées sous override séparé** (les 2 OQ différées sont de pure ergonomie, sans impact sur la lecture corporelle elle-même).

## 7. Métriques globales

| Item | Valeur |
|---|---|
| Tests verts pré-Sx_31 | 1287 |
| Tests verts post-Sb_31.5 | **~1419** (+132 net sur le cycle) |
| Tests dédiés Sx_31 (sous-suite) | **119** : 38 composer + 11 inputs + 19 route + 23 coach snapshot + 17 a11y/perf + 11 responsive |
| CI runs verts sur le cycle | 5 (Sx_31 spec, Sb_31.1, .2, .3, .4) + Sb_31.5 doc à valider |
| Migrations | **0** |
| Modèles SQLAlchemy | **0** |
| JS introduit | **0** |
| Dépendances externes ajoutées | **0** |
| Lignes service ajoutées (composer + I/O) | 415 + 240 = **655** |
| Lignes router ajoutées | 47 (route /body/intelligence) + 6 (router coach_report inject) = **53** |
| Lignes template ajoutées | 69 (body) + 122 (block partial) + 18 (priority partial) + 67 (coach snapshot) + 6 (coach include) = **282** |
| Lignes CSS ajoutées | ~230 (`body_intelligence.css`) + 23 (Sb_31.4 a11y/responsive) = **~253** |
| Ruff total warnings | 529 ≤ 548 (inchangé sur tout le cycle) |

## 8. UX avant / après

**Avant Sx_31 :** lecture corporelle fragmentée sur 3-4 pages (`/profile`, `/physique`, `/coach-report`, `/progress`) sans synthèse "qu'est-ce que mon entraînement produit sur mon corps". `coach_report` exposait des chiffres sans priorité actionnable. Aucune surface unique pour "où je sous-travaille / qu'est-ce que je dois ajuster".

**Après Sx_31 :**
- `/body/intelligence` (nouvelle route) — lecture synthétique mobile-first 1-écran avec headline + 7 blocs classifiés + priorités déterministes + limites explicites.
- `/coach-report > 1bis. Snapshot Body Intelligence` — synthèse compacte avant les analyses détaillées, lien explicite vers la vue complète.
- Pipeline canonique consommée par les 2 surfaces — un seul snapshot calculé par requête, reproductible bit-à-bit.
- Wording sobre, classification visible, limites explicites, **anti-pseudo-science** sur l'ensemble.

## 9. Dette restante (sans bloquant)

1. **Dogfood Sx_31 device réel** — PENDING. Template prêt à exécuter (`docs/dogfood/DOGFOOD_Sx_31_BODY_INTELLIGENCE_TEMPLATE.md`).
2. **OQ-F : carte home mini-summary** — différée `Sb_31.next.home-card`, à évaluer post-dogfood.
3. **OQ-G : lien `/profile → /body/intelligence`** — différée `Sb_31.next.profile-link`, ergonomie pure.
4. **Overload compliance agrégée** — différée `Sb_31.next.overload-compliance` (cf. spec §G.5 + dépend de stabilité Sx_30).
5. **Catégorisation V1 par mots-clés** dans `body_intelligence_inputs._radar_zone_counts` mapping — heuristique simple, raffinable si dogfood le révèle.
6. **Lighthouse CI / axe-core** — différé (aligné OQ-D Sx_29 et pattern Sx_30). Audit statique uniquement V1.
7. **Composer v=2** — pas requis V1, bump différé sous override séparé si dogfood réclame.

## 10. Non-goals respectés (rappel structurel pour spec_protocol)

Sx_31 a EXPLICITEMENT exclu, et reste exclu :

- React / SPA / bundler / dépendance JS externe
- Service worker / PWA / push notification (Sx_32)
- HealthKit / Health Connect / wearables (Sx_33+)
- Photos / scans / morphotype (track parallèle Body Signal Model, indépendant)
- LLM / coach AI
- Body composition (DEXA / impédance) — non déductible structurellement
- Score global numérique unique (« body score »)
- Animations / gauges / charts dynamiques (SVG SSR uniquement)
- Mutation des services métier core (`profile_metrics`, `muscle_scoring`, `quality_score`, `implicit_signal`, `confidence`, `coach_report`, `radar`, `overload_*`, `substitution`, `recommendation`, `body_tracking`)
- Nouvelle table SQL / migration Alembic
- API JSON publique sous `/body/intelligence` ou `/coach-report`
- Carte home mini-summary (différée)
- Lien `/profile → /body/intelligence` (différé)
- Overload compliance agrégée (différée)
- Ouverture automatique de Sx_32 / Sx_33+

## 11. Conditions pour ouvrir le prochain cycle

Le prochain cycle Sx_ (Sx_32 PWA / Sx_33+ Health/API / autre) ne peut s'ouvrir que si :

1. **Dogfood Sx_31 device réel exécuté** avec verdict ✅ ou ⚠️ (template prêt).
2. **OU override utilisateur explicite** documenté dans un sprint dédié `Sb_28.override-*`.

Sans l'un de ces deux pré-requis : **NE PAS OUVRIR de nouveau cycle Sx_** automatiquement.

Indépendamment et **sans bloquer** Sx_32+ :
- Dogfood Sx_27 reste PENDING (track produit indépendant).
- Dogfood Sx_30 reste PENDING (track overload indépendant).
- Track parallèle **Body Signal Model** (`SPIGNOS_BODY_SIGNAL_MODEL_SPEC.md`, photos/scans) reste indépendant.
- Sprints `Sb_31.next.*` (home-card / profile-link / overload-compliance / categorize / thresholds-v2) sont des candidats discrétionnaires post-dogfood, sous override séparé pour chacun.

## 12. Verdict final

**✅ Sx_31 TECHNICALLY CLOSED.**

- 6 sprints livrés (Sx_31 spec + Sb_31.1 → Sb_31.5) — 5 CI vertes + Sb_31.5 doc à valider en CI post-push.
- 119 tests dédiés sur le cycle, 0 régression sur l'existant.
- Architecture composer-pur / I/O isolé / router-orchestrateur / template-affichage respectée par 4 tests garde structurels indépendants.
- 5/7 OQ implémentées, 2 différées sous override séparé.
- Aucune dette technique bloquante.
- Dogfood device réel = seule étape pending pour passer à PRODUCT VALIDATED.

**Aucune ouverture automatique de Sx_32 / Sx_33+.** L'opérateur garde le contrôle exclusif via dogfood ou override explicite documenté.
