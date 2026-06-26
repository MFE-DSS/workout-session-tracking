# Sx_30 — Progressive Overload Engine (SPEC ONLY)

**Auteur :** Claude Code (Opus 4.7) sous override utilisateur explicite 2026-06-16.
**Statut :** ✅ **SPEC ONLY** — aucun build authorized tant que Sb_30.0 (spec review) n'est pas accepté.
**Spec parent / contexte :** `Sx_28_PRODUCT_ROADMAP_RECONCILIATION_SPEC.md` (Option B — Progressive Overload Engine).
**Successeur de :** Sx_29 (Mobile Session Focus Mode) — TECHNICALLY CLOSED + DOGFOOD ✅ PASS 2026-06-16.
**Dépendances :** Sx_27 (Coaching loop : quality_score, implicit_signal, narrative).
**Stack contrainte :** FastAPI SSR + Jinja2 + SQLite. **React production INTERDIT.** JS vanilla uniquement. Aucun bundler.

---

## 1. Executive summary

Sx_30 livre un moteur de surcharge progressive **déterministe, explainable, conservateur**, qui propose à l'utilisateur une cible de poids/reps **par exercice et par premier work set** de la séance suivante. Le moteur consomme le signal de logging affiné par Sx_29 (focus mode) et Sx_27 (quality_score + implicit_signal), pour remplacer la règle 3-lignes actuelle de `progression_hint.py` par un module versionné, testable, capable d'expliquer chaque recommandation par 1 à 3 raisons mécaniques.

Le moteur **ne décide jamais à la place de l'utilisateur** : il propose une cible et une intention ("augmenter", "consolider", "viser top range", "deload"). L'opérateur garde la main, valide ou ignore, et logue ce qu'il veut.

## 2. Pourquoi lancer Sx_30 maintenant

- Sx_27 a livré les **signaux** (quality_score, implicit_signal, coach_inference) sans encore les **traduire en action concrète** au niveau set/exercice.
- Sx_29 a fortement réduit le coût mental du logging (focus mode, sticky CTA, rest timer). Le signal entrant est désormais **plus dense et plus fiable**.
- L'opérateur a explicitement confirmé satisfaisant le dogfood Sx_29 → débloque l'override Option B.
- `progression_hint.py` actuel (50 lignes) ne sait pas faire :
  - moduler par RPE / quality_score
  - distinguer deload vs simple stagnation
  - proposer des **incréments concrets** (kg, reps)
  - persister une version de moteur pour reproductibilité
  - expliquer.

## 3. Human override scope (rappel)

L'override utilisateur reçu le 2026-06-16 autorise :
- **Sx_30 en SPEC ONLY uniquement.**
- Build Sx_30 (`Sb_30.1` et suivants) reste **subordonné** à l'acceptation de la présente spec via `Sb_30.0` (sprint spec review).
- Options C (Sx_31 Body v2) / D (Sx_32 PWA) / E (Sx_33+ Health/API) **restent bloquées**.
- Override **NE débloque PAS** :
  - changement de stack (React, SPA, bundler, dépendance JS externe)
  - changement de moteur de recommandation **template-level** (`recommendation.py`)
  - modification du scoring core (`quality_score.py`) en breaking
  - modification de l'implicit signal (`implicit_signal.py`) en breaking
  - body tracking, PWA, service worker, health integrations.

## 4. Source de vérité actuelle

| Élément | Localisation |
|---|---|
| Recommandation template-level | `app/services/recommendation.py` (898 lignes, **NE PAS toucher**) |
| Progression hint legacy | `app/services/progression_hint.py` (50 lignes, **remplacé** par overload engine — supprimer après migration) |
| Quality score | `app/services/quality_score.py` (260 lignes, **lecture seule** Sx_30) |
| Implicit signal | `app/services/implicit_signal.py` (177 lignes, **lecture seule** Sx_30) |
| Coach inference | `app/services/coach_inference.py` (144 lignes, **lecture seule** Sx_30) |
| Set logging models | `app/models/session.py` (SetLog, SessionExercise, RepTarget) |
| Reco explainer | `app/services/recommendation_explainer.py` (172 lignes — pattern à imiter pour overload explainer) |

## 5. Audit existant — surcharge progressive

### 5.1 Existant

- `progression_hint.py` : règle 3 cas (reps ≥ target_max → "augmenter charge", reps < target_min → "consolider", sinon "viser top range"). Aucun input quality_score, aucun input RPE, aucun input historique > 1 séance.
- `exercise_card.html` consomme `hints[se.exercise_code_snapshot]` injecté par `app/routers/sessions.py` (probable).
- Tests : `tests/test_progression_hint.py` (existence et 3 cas).

### 5.2 Lacunes

- Pas d'incrément concret proposé (+2.5kg ? +5kg ? +1 rep ?).
- Pas de distinction "stagnation 3 séances" vs "1 séance manquée".
- Pas de signal deload (quality_score chute, fatigue cumulée).
- Pas de versioning du moteur (overload_engine_version) → impossible de reproduire ou d'expérimenter.
- Pas d'explainer dédié.
- Pas de gestion exercice **récemment substitué** (cf. `substitution.py`, lecture seule Sx_30).

## 6. Modèle cible — déterministe + explainable

### 6.1 Principe

Pour chaque `SessionExercise` actif (futur ou en cours) d'une séance :
- Lire l'historique des N=3 dernières séances complétées sur le **même code exercice** (snapshot-based pour résister aux substitutions).
- Calculer un **état overload** parmi 5 valeurs :
  - `progress` : prêt à augmenter
  - `consolidate` : ne pas changer
  - `top-range` : viser top des reps avant kg
  - `deload` : alléger (quality drop + stagnation)
  - `unknown` : données insuffisantes
- Pour chaque état, proposer une **cible concrète** (kg, reps) basée sur :
  - dernier work set #1 (poids, reps complétés)
  - target_min / target_max de la séance courante (cf. `RepTarget`)
  - incrément standard par catégorie d'exercice (compound/isolation, cf. `data/reference_split.json`)
- Stocker une **liste ordonnée de raisons** (max 3) lisibles : ex. `["3 séances ≥ top range", "quality_score moyen ≥ 0.8", "pas de signal de fatigue"]`.

### 6.2 Sortie côté template

```jinja
<!-- nouveau partial _partials/overload_hint.html, dans exercise_card -->
<div class="overload-hint overload-hint--{{ hint.state }}">
  <span class="overload-hint__intent">{{ hint.intent_label }}</span>
  <span class="overload-hint__target">{{ hint.target_summary }}</span>
  <details class="overload-hint__why">
    <summary>Pourquoi ?</summary>
    <ul>{% for r in hint.reasons %}<li>{{ r }}</li>{% endfor %}</ul>
  </details>
</div>
```

No-JS friendly : `<details>` natif. Pas de JS obligatoire.

### 6.3 Versioning

- Nouvelle colonne `WorkoutSession.overload_engine_version` (`Integer NOT NULL DEFAULT 1`).
- Bump version à chaque changement de règle.
- Test de reproductibilité : pour un set d'inputs fixé + version = N, sortie déterministe.

## 7. Composants services cibles

| Service | Rôle | Nouveau / Modifié |
|---|---|---|
| `app/services/overload_engine.py` | Calcule l'`OverloadHint` par exercice (état + cible + raisons) | **NEW** |
| `app/services/overload_explainer.py` | Formate les raisons en français court, sans jargon AI | **NEW** |
| `app/services/progression_hint.py` | Legacy à supprimer en Sb_30.4 après migration | **DELETE** |
| `app/routers/sessions.py` | Remplacer injection `hints` par injection `overload_hints` | MODIFIED |
| `app/templates/_partials/exercise_card.html` | Remplacer rendu legacy hint par include `overload_hint.html` | MODIFIED |
| `app/templates/_partials/overload_hint.html` | Rendu SSR de l'OverloadHint | **NEW** |
| `app/static/css/session_focus.css` | Styles overload-hint (5 états visuels, accessibilité non-color) | MODIFIED (extension cohérente Sx_29) |
| `alembic/versions/<new>_overload_engine_version.py` | Ajout colonne `overload_engine_version` sur `workout_sessions` | **NEW** |

## 8. Données d'entrée

Per exercise (snapshot-based) :
- Historique N=3 dernières WorkoutSession `completed` contenant un `SessionExercise` avec même `exercise_code_snapshot` (résiste aux substitutions et renames).
- Pour chaque historique : premier work set complété (poids, reps), `quality_score` agrégé de l'exercice, signaux implicites (`implicit_signal`).
- `RepTarget` de la séance courante (`target_min`, `target_max`).
- Métadonnées exercice : kind (compound/isolation) via `data/reference_split.json`.

Aucune donnée hors snapshot. Aucun appel réseau. Aucune dépendance externe.

## 9. États OverloadHint

| État | Trigger principal | Cible proposée |
|---|---|---|
| `progress` | 2 séances consécutives ≥ target_max **ET** quality_score moyen ≥ 0.75 **ET** pas d'implicit_signal de fatigue | Même reps target, kg + incrément (cf. §10) |
| `consolidate` | Dernière séance dans la range mais < target_max | Mêmes kg, viser top range |
| `top-range` | Dernière séance < target_min | Mêmes kg, viser target_min minimum |
| `deload` | quality_score ≤ 0.55 **OU** 2 séances de baisse de reps consécutive | kg -10% arrondi à l'incrément, viser target_min |
| `unknown` | Données < 1 séance précédente complétée | Pas de cible chiffrée, message "Première fois" |

## 10. Incréments par catégorie

| Catégorie | Compound (squat/bench/dl/row) | Isolation (curl/lateral/calf) |
|---|---|---|
| Standard | +2.5 kg | +1 kg (à plat) ou +2.5 kg (machine) |
| Deload | -10% arrondi vers le bas à l'incrément standard | -10% arrondi vers le bas à l'incrément standard |

Source de la classification : `data/reference_split.json` (existant, lecture seule).

## 11. No-JS fallback + accessibilité

- `overload_hint.html` utilise `<details>` natif HTML : pas de JS requis pour voir les raisons.
- Aucune animation introduite (cohérent OQ-E Sx_29).
- Tap target ≥ 44×44 sur `<summary>` (réutilise `session-focus__tap-target` de Sx_29).
- Non-color cues sur les 5 états : icône `↑` / `→` / `🏁` / `↓` / `?` ou équivalent unicode + `border-left` couleur.
- aria-label sur le wrapper avec l'intention complète pour lecteurs d'écran.

## 12. Tests attendus

- Tests unitaires `overload_engine.py` (par état, par cas limite, par version).
- Tests reproductibilité : `version=1` + inputs figés → sortie figée (snapshot test).
- Tests intégration : sur une `WorkoutSession` réelle, le partial est rendu et contient l'intention + la cible + max 3 raisons.
- Tests no-regression : aucun changement de `quality_score.py`, `recommendation.py`, `implicit_signal.py`, `coach_report.py`, `body_tracking.py`, `substitution.py`. Garde via `tests/test_no_core_drift.py` (existant ou nouveau).
- Tests migration : roundtrip up/down sur la colonne `overload_engine_version` (cf. `check_migration_roundtrip.py`).
- Tests a11y : non-color cues + aria-label présents pour les 5 états.
- Tests no-JS : page session rendue sans JS contient toujours l'intention overload (au moins en mode statique).

## 13. Fichiers impactés (vue d'ensemble)

### Créés
- `app/services/overload_engine.py`
- `app/services/overload_explainer.py`
- `app/templates/_partials/overload_hint.html`
- `alembic/versions/<id>_sx30_overload_engine_version.py`
- `tests/test_overload_engine.py`
- `tests/test_overload_explainer.py`
- `tests/test_overload_hint_template.py`
- `tests/test_overload_no_regression.py`
- `tests/test_overload_migration_roundtrip.py`
- `docs/SPRINT_Sb_30_0_REPORT.md` → `docs/SPRINT_Sb_30_5_REPORT.md`
- `docs/strategy/Sx_30_CLOSURE_REPORT.md` (à clôture)

### Modifiés
- `app/routers/sessions.py` (injection overload_hints uniquement, signature stable)
- `app/templates/_partials/exercise_card.html` (remplacer hint legacy par include overload_hint)
- `app/static/css/session_focus.css` (+~50 lignes styles overload-hint)
- `app/models/session.py` (colonne `overload_engine_version`)
- `app/static/schema_snapshot.sql` (régénéré)
- `docs/strategy/SPEC_REGISTRY.md` + `ROADMAP_AND_NEXT_STEPS.md`

### Supprimés (Sb_30.4)
- `app/services/progression_hint.py` (legacy)
- `tests/test_progression_hint.py` (à remplacer par `test_overload_engine.py`)

## 14. Build queue (à valider en Sb_30.0)

| Sprint | Objet | Touch métier ? |
|---|---|---|
| `Sb_30.0` | **Spec review** + sprint report spec | Aucun |
| `Sb_30.1` | `overload_engine.py` v1 (états + cibles + reasons) + tests unitaires | Nouveau service uniquement |
| `Sb_30.2` | `overload_explainer.py` + intégration router + injection contexte | Router : ajout injection, pas de modification de logique métier |
| `Sb_30.3` | Migration Alembic colonne `overload_engine_version` + template `overload_hint.html` + CSS | Schéma uniquement |
| `Sb_30.4` | Remplacement legacy : suppression `progression_hint.py`, update `exercise_card.html`, déprécation `hints[…]` legacy | Template + service ; **pas** de changement scoring/reco |
| `Sb_30.5` | A11y / tests de non-régression / closure | Tests + docs uniquement |

## 15. Risques

- **R1 — Sur-confiance utilisateur dans la cible chiffrée.** Mitigation : language toujours "tenter", "viser", jamais "tu dois". Reasons obligatoirement affichables.
- **R2 — Drift de version moteur sans rétro-compatibilité.** Mitigation : `overload_engine_version` immutable par session, snapshots tests.
- **R3 — Pollution router `sessions.py`.** Mitigation : injection unique d'un dict `overload_hints`, calcul délégué à `overload_engine.py`.
- **R4 — Substitutions cassent l'historique.** Mitigation : matching sur `exercise_code_snapshot` (snapshot-based), pas sur substituted_name.
- **R5 — Bypass des contrats Sx_27/29 (no React, no service worker).** Mitigation : tests de garde existants étendus.

## 16. Non-goals

- ❌ Pas de changement de `recommendation.py` (template-level reco).
- ❌ Pas de changement de `quality_score.py` (lecture seule).
- ❌ Pas de changement de `implicit_signal.py`.
- ❌ Pas de changement de `coach_report.py` / `coach_inference.py` (lecture seule).
- ❌ Pas de body tracking.
- ❌ Pas de PWA / service worker / offline.
- ❌ Pas de modal/dialog.
- ❌ Pas de toast / animation.
- ❌ Pas de React / SPA / bundler / dépendance JS externe.
- ❌ Pas de nouveau JS hors `session_focus.js` (extension acceptable mais minimal).
- ❌ Pas de persistance des recommandations (recalcul à chaque GET — déterministe).
- ❌ Pas de notification push.
- ❌ Pas de body composition.
- ❌ Pas de health integrations.
- ❌ Pas d'auto-substitution.
- ❌ Pas de cardio / readiness modification.

## 17. Conditions de validation humaine

Sb_30.0 (spec review) est accepté ssi :
- L'opérateur valide les 5 états (§9) et les incréments (§10).
- L'opérateur tranche les OQ §18.
- Aucune contrainte des non-goals (§16) n'est levée sans override séparé documenté.
- Build queue (§14) confirmée ou amendée.

## 18. Open questions (à trancher en Sb_30.0)

- **OQ-A** : Granularité de la cible — proposer kg/reps **par exercice** uniquement (V1) ou **par set** (V2 plus tard) ?
  - Recommandation : par exercice V1, par set différé.
- **OQ-B** : Stockage de la version moteur — colonne `overload_engine_version` sur `workout_sessions` (par séance) ou sur `users` (par profil) ?
  - Recommandation : par séance (reproductibilité incident).
- **OQ-C** : Bypass deload — autoriser un override utilisateur "ignore deload, je suis frais" (V1 ou différer) ?
  - Recommandation : différer V1, pas de bouton override.
- **OQ-D** : Lecture historique — N=3 séances passées ou N variable selon densité d'entraînement (ex. dernières 6 semaines) ?
  - Recommandation : N=3 fixe V1.
- **OQ-E** : Affichage de la cible dans l'input de poids/reps — pré-remplir le champ (V1) ou afficher en placeholder seulement (V1 conservateur) ?
  - Recommandation : placeholder seulement V1. Pré-remplissage différé pour ne pas écraser une intention utilisateur.

## 19. Non-goals (rappel structurel pour spec-protocol)

Voir §16 ci-dessus.

## 20. Verdict

**✅ Sx_30 SPEC PROPOSÉE — en attente de validation Sb_30.0.**

Aucun build avant : (a) review utilisateur des OQ §18, (b) acceptation Sb_30.0, (c) lever explicitement le statut `BUILD AUTHORIZED FOR OPTION B BUILD`.
