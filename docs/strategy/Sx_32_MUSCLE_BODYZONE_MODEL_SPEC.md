# Sx_32 — Muscle & BodyZone Formal Model (Deep Feature Refactor Scoping Spec)

**Spec ID :** `Sx_32_MUSCLE_BODYZONE_MODEL_SPEC`
**Cycle :** `Sx_32` — Deep Feature/Object Refactor (backend métier)
**Type :** SPEC ONLY (docs-only) — **cadrage de refonte** ; aucun code, aucune migration
**Date d'ouverture :** 2026-07-07
**Auteur :** opérateur (Martin Feldmann) + agent Claude Code
**Depends on :** cycles UI Sx_UI (fondation visuelle) · `Sx_31 Body Intelligence v2` (CLOSED) · `Sx_30 Overload Engine` (CLOSED)
**Source d'audit :** audit backend read-only 2026-07-07 (models + services)

---

## §0. Status

- **SPEC ONLY** — **BUILD NOT AUTHORIZED**
- **Docs-only strict** — aucun `app/`, `tests/`, `migrations/`, `scripts/`, `.github/` touché
- **Aucun modèle créé, aucune migration écrite** dans ce sprint
- Ce document **cadre** une refonte métier ; il ne l'exécute pas.
- **Override explicite opérateur requise** pour ouvrir tout build `Sb_32.k` (framework spec-driven — un cycle métier ne s'ouvre pas sans mandat).

## §1. Pourquoi cette spec existe

Les cycles UI (`Sx_UI_04` cockpit, `Sx_UI_05` home, `Sx_UI_02b` Auren Terminal) ont **transformé l'interface** mais ont, par contrat verbatim, **verrouillé le métier** (« aucun changement scoring/overload/substitution/coach/body_intelligence/model/migration »). Ils ont ce faisant **révélé une dette structurelle** : plusieurs surfaces UI attendent des objets métier qui **n'existent pas**.

Cas emblématique : le **Worked Area Panel** (Sx_UI_04 §23) affiche « Assistants à qualifier / Stabilisation à qualifier » — non par choix esthétique, mais parce qu'**il n'y a aucun objet Muscle/BodyZone en base** pour les qualifier. Le contrat `exercise_code → body_map_descriptor` (§23.5) est resté **documentaire faute d'implémentation possible**.

Cette spec ouvre le premier axe de refonte profonde : **formaliser un modèle Muscle / BodyZone relationnel**, choisi comme fondation car il débloque le plus de surfaces (Worked Area, coach report, body intelligence, substitution, recommandation).

## §2. État actuel (constat d'audit)

**La classification muscle/zone est heuristique, pas schéma.**

- `app/services/muscle_mapping.py` contient :
  - `ZONE_LABELS` : **11 zones en dur** (pecs, delt_lat, delt_post, lats, upper_back, biceps, triceps, quads, posterior, calves, core).
  - `ZONE_MEASUREMENT` : mapping zone → champ de mesure (`pecs → chest_cm`, certains `None`).
  - `ZONE_VOLUME_TARGET` : cible de volume hebdo par zone.
  - `RADAR_AXIS_ORDER` + agrégats 6 axes radar (immutables, dérivés des 11 zones).
  - `_EXERCISE_PATTERNS` : **liste de mots-clés** → `classify_exercise(name) → (primary_zone, secondary_zones)` par **substring matching** sur le nom d'exercice.
- `data/machine_atlas.json` a un champ `zone` par famille (ex. `pecs`), **mais non lié aux exercices en base** (lookup JSON only).
- `data/exercise_properties.json` a `zone_primary`, `muscle_group`, `pattern_motor` pour ~100 exercices (substitution N2/N3), **non relié au modèle**.

**Conséquences (dette) :**
- Aucun ground truth en base : ajouter un exercice = risque de `("unknown", [])` silencieux.
- 3+ sources de vérité pour la zone (muscle_mapping patterns, machine_atlas.json, exercise_properties.json) — non réconciliées.
- Le Worked Area UI ne peut pas afficher assistants/stabilisation (données inexistantes).
- Les moteurs consommateurs (muscle_scoring, coach_report, body_intelligence, recommendation) reposent tous sur `classify_exercise` heuristique.

## §3. Objectif de la refonte

Introduire un **modèle relationnel Muscle / BodyZone** en base, source de vérité unique, et **migrer les consommateurs** du substring-matching vers des lookups schéma — **sans changer le comportement observable** (invariance historique : mêmes classifications, mêmes scores, mêmes leaderboards).

Résultat cible :
- Un exercice « sait » quels muscles il travaille (primary / secondary / stabilizer) **via des objets en base**, pas via une liste de mots-clés.
- Le contrat `body_map_descriptor` (§23.5 UI) devient **implémentable** → le Worked Area affiche des données réelles.
- Une seule source de vérité zone, réconciliant muscle_mapping + machine_atlas + exercise_properties.

## §4. Ce que la refonte NE change PAS (invariants)

Point de gouvernance critique — la refonte **formalise sans casser** :

- ✅ **Invariance des classifications existantes** : chaque exercice actuellement classé `pecs` doit rester `pecs`. Les 11 zones actuelles sont le **point de départ** du nouveau modèle, pas un remplacement arbitraire.
- ✅ **Invariance des scores/leaderboards** : `muscle_scoring`, `quality_score`, `coach_report`, `body_intelligence` doivent produire des sorties **identiques** post-migration (tests de non-régression obligatoires).
- ✅ **Contrat additive-only migrations** (hérité Sx_26) : ADD COLUMN / ADD TABLE only, jamais DROP/RENAME/UPDATE destructif.
- ✅ **Snapshot identity préservée** : les sessions historiques (`exercise_name_snapshot`) restent classables via le nouveau modèle sans perte.
- ✅ **Aucun claim médical** (garde-fous coach/body existants préservés).
- ✅ **Aucun rebrand SPIGNOS → Auren dans le code** (réservé Sx_UI_10).

La refonte **ajoute des objets et migre les lookups** ; elle ne réécrit pas la logique produit.

## §5. Modèle cible (candidat V1)

Objets relationnels proposés (noms/champs à figer au build) :

### §5.1 `Muscle`
```
id · code (unique, ex. "pectoralis_major") · name (fr, ex. "Grand pectoral")
· category (upper | lower | core) · zone_id (FK BodyZone)
```

### §5.2 `BodyZone`
```
id · slug (unique, ex. "pecs") · label (ex. "Pectoraux")
· measurement_field (nullable, ex. "chest_cm" ou None)
· radar_axis (ex. "pecs") · volume_target_weekly (int, ex. 16)
```
Les 11 zones actuelles (`ZONE_LABELS`) sont **backfillées** en `BodyZone`, avec `ZONE_MEASUREMENT`, `RADAR_AXIS_ORDER`, `ZONE_VOLUME_TARGET` migrés en colonnes → **fin des dicts hardcodés**.

### §5.3 `ExerciseMuscleMapping`
```
id · exercise_code (ou template_exercise_id) · exercise_name_ref
· primary_muscle_id (FK) · secondary_muscle_ids (assoc N-N)
· stabilizer_muscle_ids (assoc N-N, optionnel)
· movement_pattern (nullable, ex. "push_horizontal")
· source (curated | derived | atlas) · confidence (nullable)
```
Backfill depuis `_EXERCISE_PATTERNS` (primary/secondary existants) + enrichissement optionnel via `exercise_properties.json` (muscle_group) + `machine_atlas.json` (zone).

### §5.4 Contrat `body_map_descriptor` (implémente §23.5 UI)
```
exercise_code → { primary_zone, secondary_zones[], stabilizer_zones[],
                  movement_pattern, confidence, source }
```
Dérivé par lookup des objets ci-dessus → consommable par le Worked Area sans nouvelle heuristique.

## §6. Migration des consommateurs (sans régression)

| Consommateur | Aujourd'hui | Après |
|---|---|---|
| `muscle_mapping.classify_exercise()` | substring match | lookup `ExerciseMuscleMapping` (fallback substring conservé pour exercices non mappés) |
| `muscle_scoring` | zones via classify | zones via modèle, mêmes scores |
| `coach_report` (zone summary) | classify | modèle, mêmes seuils/sorties |
| `body_intelligence` (zone distribution) | classify | modèle |
| `substitution` (zone_primary N3) | exercise_properties.json | réconcilié avec le modèle (ou conservé, cf. OQ-32-D) |
| Worked Area UI (Sx_UI_04) | fallback « à qualifier » | `body_map_descriptor` réel |

**Stratégie de sécurité** : `classify_exercise` garde un **fallback substring** pour tout exercice non encore mappé → aucune régression « unknown » nouvelle. Migration progressive.

## §7. Découpage en sous-sprints (proposé)

| Sous-sprint | Portée | Migration |
|---|---|---|
| **Sb_32.1** | Modèle `BodyZone` + `Muscle` + backfill des 11 zones/labels/measurement/radar/volume depuis muscle_mapping (dicts → base). Tests d'invariance : les zones/labels/targets exposés sont identiques. | ADD TABLE bodyzone, muscle |
| **Sb_32.2** | `ExerciseMuscleMapping` + backfill depuis `_EXERCISE_PATTERNS` (primary/secondary). `classify_exercise` bascule sur lookup + fallback substring. Test : classification identique pour tous les exercices connus. | ADD TABLE exercise_muscle_mapping |
| **Sb_32.3** | Contrat `body_map_descriptor` (service de lecture) + enrichissement stabilizers/pattern via atlas/properties. **Branche le Worked Area UI** (surface Sx_UI_04, sous override UI séparé). | (données) |
| **Sb_32.4** | Migration des consommateurs restants (coach_report, body_intelligence, muscle_scoring) vers le modèle + suppression progressive des dicts hardcodés une fois l'invariance prouvée. Hardening + closeout. | (aucune) |

Ordre défendable : **base d'abord (zones/muscles), mapping ensuite, descriptor puis consommateurs.** Chaque sous-sprint est review-gated et prouve la non-régression avant le suivant.

## §8. Risques

- **Invariance historique** : le risque #1. Toute divergence de classification casserait leaderboards / coach reports. → tests de non-régression exhaustifs (comparer classify old vs new sur tout le catalogue) obligatoires avant chaque bascule.
- **Migrations** : 3 nouvelles tables. Contrat additive-only respecté ; downgrades idempotents.
- **Réconciliation des 3 sources** (muscle_mapping / atlas / properties) : conflits possibles (une zone diffère entre sources). → arbitrage explicite documenté (OQ-32-C).
- **Périmètre** : ne PAS entraîner les autres Tier 1 (agrégation readiness, identité exercice, substitution entity) dans ce cycle — ils restent en backlog (§10).

## §9. Open Questions

| ID | Question | Recommandation V1 |
|---|---|---|
| **OQ-32-A** | Clé de mapping : `exercise_code` ou `template_exercise_id` ? | **exercise_code** — cohérent avec l'identité snapshot ; robuste aux reseeds. |
| **OQ-32-B** | Granularité : niveau **Muscle** fin (grand pectoral, triceps…) ou niveau **Zone** (11 zones actuelles) suffisant V1 ? | **Zone V1** (backfill des 11 zones) + `Muscle` comme table préparée mais peuplée au minimum ; granularité fine en V2. |
| **OQ-32-C** | Arbitrage des 3 sources en conflit (muscle_mapping vs atlas vs properties) ? | **muscle_mapping = source primaire** (c'est l'actuel ground truth des scores) ; atlas/properties = enrichissement (stabilizers/pattern), jamais override du primary. |
| **OQ-32-D** | Substitution (N2/N3 via properties) migre-t-elle vers le modèle ou reste-t-elle indépendante V1 ? | **Reste indépendante V1** (hors scope ; c'est un autre axe Tier 1). Réconciliation future. |
| **OQ-32-E** | Fallback substring conservé indéfiniment ou déprécié après backfill complet ? | **Conservé V1** (filet de sécurité) ; dépréciation en Sb_32.4 seulement après invariance prouvée sur 100% du catalogue. |
| **OQ-32-F** | Stabilizers : données réelles disponibles ou fallback « à qualifier » persiste V1 ? | **Fallback V1** pour les stabilizers non sourcés (pas d'invention) ; peuplement progressif depuis données fiables. |
| **OQ-32-G** | Le Worked Area UI (branchement §5.4) est-il dans ce cycle ou dans un sprint UI séparé ? | **Sprint UI séparé** (`Sb_UI_xx`) sous override UI ; Sx_32 fournit le service `body_map_descriptor`, l'UI le consomme après. |

## §10. Backlog documenté (autres candidats Tier 1/2, HORS ce cycle)

Explicitement **différés**, à ouvrir dans des cycles dédiés sous override :
- **Agrégation Readiness / Recovery** (`UserReadinessSummary`, `RecoveryWindow`, `OverloadCompliance`) — readiness devient moteur.
- **Unification identité exercice** (snapshot vs live) + garde overload.
- **Substitution first-class** (`ExerciseSubstitution` persisté, override/curation).
- **Overload compliance model** (hint vs réalisé).
- Tier 2/3 : recomputation implicit signal versionnée, décomposition trend performance, feedback readiness↔overload, ratios body avancés.

## §11. Non-goals

- ❌ Aucun code / modèle / migration dans cette spec (docs-only).
- ❌ Aucune refonte du scoring / overload / coach / recommendation dans ce cycle (seulement leur **source de classification** migre, à sortie identique).
- ❌ Aucun changement d'identité exercice ni de substitution (autres axes).
- ❌ Aucun claim médical / diagnostic nouveau.
- ❌ Aucun rebrand code · aucun changement UI dans ce cycle (le branchement Worked Area est un sprint UI séparé).
- ❌ Aucune granularité muscle fine obligatoire V1 (zone V1).
- ❌ Aucun release tag.

## §12. Definition of Ready (pour ouvrir Sb_32.1)

- ✅ Cette spec acceptée en human review + OQ-32-A→G tranchées.
- ✅ Override explicite opérateur d'ouverture du cycle Sx_32 (métier).
- ✅ Baseline de non-régression définie : snapshot de `classify_exercise` sur tout le catalogue (référence à égaler).

## §13. Acceptance criteria (de cette spec)

- ✅ Dette actuelle (muscle/zone heuristique) documentée sur code réel.
- ✅ Modèle cible (BodyZone / Muscle / ExerciseMuscleMapping / body_map_descriptor) posé.
- ✅ Invariance historique cadrée comme contrainte #1.
- ✅ Découpage 4 sous-sprints review-gated + migrations additive-only.
- ✅ 7 OQ avec recommandation.
- ✅ Backlog des autres axes documenté (pas de scope creep).

## §14. Verdict attendu

- **READY FOR HUMAN REVIEW**
- **Aucun build ouvert** (Sb_32.1 bloqué tant que spec + OQ non validées + override cycle)
- **Aucune migration, aucun code**
- **Aucun release tag**

## §15. Références

- Audit backend (source) : lecture read-only 2026-07-07 (`app/models/`, `app/services/`)
- Code ancré : `app/services/muscle_mapping.py` (11 zones + `_EXERCISE_PATTERNS` + `classify_exercise`)
- Contrat UI en attente : `docs/strategy/Sx_UI_04_FOCUSED_EXERCISE_FLOW_SPEC.md` §23 (Body Representation System, `body_map_descriptor`)
- Cycles clos liés : `Sx_31 Body Intelligence v2`, `Sx_30 Overload Engine`
- Contrat migrations : `Sx_26` (additive-only)
- Registry : `docs/strategy/SPEC_REGISTRY.md`
- Roadmap : `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`
