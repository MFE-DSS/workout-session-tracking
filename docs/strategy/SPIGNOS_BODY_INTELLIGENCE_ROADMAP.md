# SPIGNOS — Body Intelligence Roadmap

**Sprint :** `Sx Body 00 — Brainstorming & Architecture Framing`
**Branche :** `sx-body-00-brainstorming-spec`
**Date :** 2026-06-26
**Type :** SPEC-FIRST. **Aucun code, aucune migration, aucune dépendance.**
**Document jumeau :** `docs/strategy/SPIGNOS_BODY_SIGNAL_MODEL_BRAINSTORMING.md`

---

## 1. Statut du document

| Champ | Valeur |
|---|---|
| Statut | ⚪ DRAFT — roadmap de cadrage des 5 lots Body Intelligence |
| Portée | Séquence de build, dépendances, branch/merge strategy, gates d'acceptance |
| Convention de nommage | `Sx` = **spec only**, `Sb` = **build** (cf. `SPEC_DRIVEN_ENGINEERING_PROTOCOL_v1.md` + `SPEC_REGISTRY.md`) |
| Hard contracts hérités | SQLite, deploy manuel, snapshots, **ADD COLUMN ONLY**, ruff budget verrouillé, ownership utilisateur, drift guard, smoke/deploy |
| Interdits de ce sprint | Bodygram, MediaPipe, modèle DB, migration, `requirements.txt`, `.env*`, `app/` |

---

## 2. Objectif stratégique

Préparer SPIGNOS à intégrer un module **Body Intelligence** qui transforme photos/mesures → signaux contrôlés → ratios → tags d'archetype non médicaux → recommandations training/nutrition simples → liaison au catalogue / programme / graphe de substitution.

Le faire **sans refonte mobile native**, en respectant l'architecture FastAPI SSR existante, la discipline de production, et la philosophie « pas de feature magique non gouvernable ».

---

## 3. Positionnement dans SPIGNOS

Body Intelligence **s'appuie sur l'existant** plutôt que de le remplacer :
- `body_measurements` (mesures latéralisées, source de vérité) — **réutilisé / étendu** (ADD COLUMN ONLY).
- `readiness_entries` — signal de récupération complémentaire (lecture seule pour Body).
- Body Engineering Dashboard (`GET /dashboard`, 5 axes scorés + confiance + dégradation) — **point d'intégration UX candidat** (axe additionnel ou page `/body` dédiée, cf. OQ-8).
- Graphe de substitution (prévu/réalisé, `actual_exercise_name()`, `classify_exercise()`) — **cible de liaison** pour les recommandations training.
- Signal Confidence Policy (seuils de points/séances) — **réutilisée** pour ne jamais inventer de tendance.

**Frontière dure :** Body Intelligence vit **hors du mode séance**. Il n'injecte aucune complexité dans la saisie des sets.

---

## 4. Les 5 lots de build

> Rappel : `Sx` = spec, `Sb` = build. Le présent sprint `Sx Body 00` est le brainstorming amont.

| Lot | Type | Nom | Scope résumé |
|---|---|---|---|
| **Sx Body 01** | spec | Body Signal Model | Spec formelle du modèle de signal + privacy model. Promotion du brainstorming. |
| **Sb Body 01** | build | Manual Body Profile | Mesures manuelles uniquement. **Crée les tables de base.** Pas de photo AI, pas de MediaPipe, pas de Bodygram. |
| **Sb Body 02** | build | MediaPipe Capture Quality | Score de qualité de capture, validation front/side, métadonnées landmarks. Pas d'estimation de body composition. |
| **Sb Body 03** | build | Bodygram Integration | Protection clé API côté serveur, token de scan, stockage raw provider, mesures normalisées, **consent gate**. |
| **Sb Body 04** | build | Archetype Engine | Ratios → tags → moteur de règles → *rationale* de recommandation. **Pas de modification auto du programme.** |
| **Sb Body 05** | build | Link to Training Engine | Mapping priorités corporelles → familles musculaires → familles d'exercices ; préparation liaison graphe de substitution. UX session non altérée. |

---

## 5. Dépendances entre lots

```
Sx Body 00 (brainstorming)        ← CE SPRINT
        │
        ▼
Sx Body 01 (signal model spec + privacy model)
        │
        ▼
Sb Body 01 (manual profile + TABLES DE BASE)   ◀── verrou : crée le socle data
        │
        ├─────────────┬──────────────┐
        ▼             ▼              ▼
Sb Body 02       Sb Body 03      Sb Body 04
(MediaPipe       (Bodygram       (Archetype
 capture)         integration)    engine)
        │             │              │
        └─────────────┴──────────────┘
                      │
                      ▼
              Sb Body 05 (training engine link)
```

| Lot | Dépend de | Raison |
|---|---|---|
| Sx Body 01 | Sx Body 00 | Promotion du brainstorming validé |
| Sb Body 01 | Sx Body 01 | Build sur spec validée ; crée le socle data |
| Sb Body 02 | Sb Body 01 mergé | a besoin des entités capture/measurement de base |
| Sb Body 03 | Sb Body 01 mergé | a besoin de measurement + provider_raw + consent |
| Sb Body 04 | Sb Body 01 mergé | a besoin de measurements confirmées pour ratios/tags |
| Sb Body 05 | Sb Body 04 | a besoin des tags d'archetype pour le mapping training |

**Règle clé :** `Sb Body 01` est le **goulot d'étranglement de migration**. Les lots 02/03/04 ne partent qu'**après son merge** pour éviter les conflits de migration parallèles (cf. §7-8).

---

## 6. Branch strategy

Séquence de branches (workflow GitHub : branche courte descriptive, changements isolés, PR claire) :

```
sx-body-00-brainstorming-spec       ← CE SPRINT (cette branche)
sx-body-01-signal-model-spec
sb-body-01-manual-profile
sb-body-02-mediapipe-capture-quality
sb-body-03-bodygram-integration
sb-body-04-archetype-engine
sb-body-05-training-engine-link
```

**Règles :**
- `sx-*` = spec only (docs). `sb-*` = build (code + tests + migration éventuelle).
- **Une PR indépendante par branche.** Chaque PR explique le problème, résume les changements, passe les checks/reviews avant merge.
- `sx-*` est mergeable **tôt** (faible risque de conflit, doc only).

### PR map

| PR | Branche | Fichiers | Code app ? | Migration ? | Dépendance ? |
|---|---|---|---|---|---|
| PR 1 | `sx-body-00-brainstorming-spec` | les 2 docs de ce sprint | Non | Non | Non |
| PR 2 | `sx-body-01-signal-model-spec` | `SPIGNOS_BODY_SIGNAL_MODEL_SPEC.md`, `SPIGNOS_BODY_PRIVACY_MODEL.md` | Non (sauf références doc) | Non | Non |
| PR 3 | `sb-body-01-manual-profile` | `app/body_assessment/`, `app/templates/body_assessment/`, `migrations/versions/*`, `tests/` | Oui | **Oui (socle)** | Non |
| PR 4 | `sb-body-02-mediapipe-capture-quality` | capture quality, validation front/side, métadonnées landmarks | Oui | Possible (additif) | MediaPipe (flagué) |
| PR 5 | `sb-body-03-bodygram-integration` | provider serveur, token, raw storage, mesures normalisées, consent gate | Oui | Possible (additif) | Bodygram (flagué) |
| PR 6 | `sb-body-04-archetype-engine` | ratios, tags, rule engine, recommendation rationale | Oui | Possible (additif) | Non |
| PR 7 | `sb-body-05-training-engine-link` | mapping body priorities → muscle families → exercise families, prep substitution | Oui | Possible (additif) | Non |

---

## 7. Parallel development strategy

Pour permettre le travail en parallèle avec d'autres développeurs **sans casser les migrations** :

1. **Specs mergeables tôt.** `sx-body-00` et `sx-body-01` peuvent être mergés dès validation — risque de conflit quasi nul (doc only).
2. **`Sb Body 01` sérialise le socle.** Il crée les tables de base ; **les autres builds partent après son merge**. Pas de migrations parallèles concurrentes si possible.
3. **Providers isolés derrière interfaces.** `BodyMeasurementProvider` (Bodygram) et `CaptureQualityProvider` (MediaPipe) vivent derrière des interfaces → 02 et 03 ne se touchent pas mutuellement et peuvent avancer en parallèle **après** 01.
4. **Archetype engine (04) en parallèle** des providers : il ne dépend que des mesures confirmées de 01, pas des providers.
5. **Module isolé** `app/body_assessment/` : surface de conflit minimale avec les chantiers training/session en cours (ex. cycle overload `Sx_30`).

---

## 8. Merge strategy

| Règle | Détail |
|---|---|
| **Specs d'abord** | `sx-*` mergés avant les builds. |
| **Migrations jamais parallèles** | Idéalement une seule migration « en vol » à la fois ; `Sb Body 01` mergé avant d'ouvrir les migrations de 02/03/04/05. |
| **ADD COLUMN ONLY** | Toute migration est additive, avec snapshot + linter + roundtrip + drift guard (contrat SPIGNOS). |
| **Feature flags obligatoires** | Dès le premier build : `BODY_ASSESSMENT_ENABLED=false`, `BODY_PHOTO_CAPTURE_ENABLED=false`, `BODY_PROVIDER_BODYGRAM_ENABLED=false` (convention `*_enabled: bool = Field(default=False)`). |
| **Aucun impact prod sans migration testée** | Procédure SPIGNOS : migration → drift guard → restart → smoke test. |
| **Registry à jour** | À chaque ouverture/fermeture de sprint, mettre à jour `SPEC_REGISTRY.md` (source de vérité). |

---

## 9. Acceptance gates

| Gate | Lot(s) concerné(s) | Critère |
|---|---|---|
| G-1 Spec-first | Sx Body 00/01 | Docs propres, 0 code, 0 migration, 0 dépendance. |
| G-2 Privacy gate | Sx Body 01, Sb Body 01+ | Consentement + minimisation + suppression spécifiés / implémentés avant toute capture. |
| G-3 Non-médical / non-discriminatoire | tous | Aucun diagnostic, aucune inférence protégée ; wording verrouillé. |
| G-4 Migration discipline | Sb Body 01+ | ADD COLUMN ONLY, snapshot, drift guard, smoke vert (CI 3/3). |
| G-5 Flag OFF par défaut | Sb Body 01+ | Flags désactivés par défaut ; 0 impact prod sans activation. |
| G-6 Hors-session | tous | Mode séance non altéré ; saisie des sets inchangée. |
| G-7 Explicabilité | Sb Body 04+ | Chaque recommandation porte *rationale* + `engine_version`. |
| G-8 Corrigeabilité | Sb Body 01+ | Mesures corrigeables par l'utilisateur. |

---

## 10. Risques de conflit avec les autres chantiers

| Risque | Chantier en concurrence | Mitigation |
|---|---|---|
| Conflit migration | cycle overload `Sx_30` (`overload_engine_version`, migration `6h9e4c0d1f32`), autres `Sb_*` actifs | Sérialiser : `Sb Body 01` ne s'ouvre pas pendant une autre migration en vol ; rebaser sur HEAD à jour. |
| Conflit dashboard | `/dashboard` (5 axes existants) | Décider tôt (OQ-8) : 6ᵉ axe additif **ou** page `/body` dédiée. Préférer page dédiée pour isoler la surface. |
| Conflit catalogue / familles | graphe de substitution, `classify_exercise()` | Body ne modifie pas le catalogue ; il **lit** les familles. Liaison en lecture seule au départ. |
| Conflit `requirements.txt` | Dependabot (nombreuses PR pip ouvertes) | Providers flagués + ajout de dépendance isolé dans la PR du lot concerné (02/03), jamais en spec. |
| Drift de wording | coach narrative (`coach_inference.py`, garde anti-"vous") | Réutiliser la discipline de wording existante ; ajouter une garde linguistique Body. |

---

## 11. Fichiers probablement impactés par lot

> Indicatif. **Aucun de ces fichiers n'est touché dans `Sx Body 00`.**

| Lot | Fichiers probables (futurs) |
|---|---|
| Sx Body 01 | `docs/strategy/SPIGNOS_BODY_SIGNAL_MODEL_SPEC.md`, `docs/strategy/SPIGNOS_BODY_PRIVACY_MODEL.md`, `SPEC_REGISTRY.md` (entrée) |
| Sb Body 01 | `app/body_assessment/`, `app/templates/body_assessment/`, `app/models/` (additif), `migrations/versions/*`, `app/config.py` (flags), `tests/` |
| Sb Body 02 | `app/body_assessment/capture_quality.py` (interface + impl MediaPipe flaguée), `tests/`, `requirements.txt` (dans cette PR uniquement) |
| Sb Body 03 | `app/body_assessment/providers/bodygram.py`, route serveur token, `app/config.py` (flag + secret), `tests/`, `requirements.txt` (cette PR) |
| Sb Body 04 | `app/body_assessment/archetype_engine.py`, `app/body_assessment/recommendations.py`, `tests/` |
| Sb Body 05 | `app/body_assessment/training_link.py` (mapping familles), lecture catalogue/substitution, `tests/` |

---

## 12. Ce qui ne doit pas être codé maintenant

Dans `Sx Body 00` (ce sprint), **strictement interdit** :
- ❌ intégration Bodygram (code/SDK/token).
- ❌ ajout de MediaPipe (code/dépendance).
- ❌ modèle DB / colonne / table.
- ❌ migration Alembic.
- ❌ modification de `requirements.txt`, `.env*`, `app/`.
- ❌ provider technique, interface implémentée.
- ❌ diagnostic médical, inférence de caractéristique protégée, « morphotype » comme vérité primaire.

Seuls livrables autorisés : **les 2 documents Markdown de cadrage**.

---

## 13. Critères de passage vers Sx Body 01

On peut ouvrir `Sx Body 01 — Signal Model Spec` lorsque :
- [ ] Les 2 docs de `Sx Body 00` sont mergés (PR 1).
- [ ] La taxonomie des 6 états de signal est validée par l'opérateur.
- [ ] Les décisions recommandées (D-1 → D-12 du brainstorming) sont arbitrées (acceptées / amendées).
- [ ] Les OQ critiques (OQ-4 rétention, OQ-6 consentement, OQ-8 intégration UX) ont une orientation.
- [ ] La place dans `SPEC_REGISTRY.md` est réservée (nouvelle entrée de cycle Body).

---

## 14. Sprint queue finale

| Ordre | Sprint | Type | Statut | Pré-requis |
|---|---|---|---|---|
| 1 | `Sx Body 00 — Brainstorming & Architecture Framing` | spec | 🟡 ce sprint | — |
| 2 | `Sx Body 01 — Body Signal Model` | spec | 🔵 à ouvrir | PR 1 mergée + arbitrage |
| 3 | `Sb Body 01 — Manual Body Profile` | build | ⏳ | Sx Body 01 ; crée socle data |
| 4 | `Sb Body 02 — MediaPipe Capture Quality` | build | ⏳ | Sb Body 01 mergé |
| 5 | `Sb Body 03 — Bodygram Integration` | build | ⏳ | Sb Body 01 mergé + consent model |
| 6 | `Sb Body 04 — Archetype Engine` | build | ⏳ | Sb Body 01 mergé |
| 7 | `Sb Body 05 — Link to Training Engine` | build | ⏳ | Sb Body 04 |

> **Definition of Done de `Sx Body 00` :** 2 docs Markdown propres · 0 migration · 0 modif runtime · 0 dépendance · 1 roadmap claire · 1 Q&A complet (30) · 1 stratégie branches/merge · 1 cadrage privacy explicite · 1 modèle conceptuel primaire/dérivé/provider/confirmé.
