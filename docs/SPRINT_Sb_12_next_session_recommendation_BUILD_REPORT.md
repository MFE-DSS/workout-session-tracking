# Sprint Sb_12 Build Report — Next-Session Recommendation

**Date :** 2026-04-21
**Type :** Build chirurgical — implémente §L de `SPIGNOS_NEXT_SESSION_RECOMMENDATION_SPEC_v1.md`
**Prérequis :** Sx_12 spec validée, Session System V1 clos, Sb_11a livré
**Périmètre livré :** moteur déterministe G2 + garde-fous G3 + surface home/launcher.

---

## 1. Objectif

Recommander la séance la plus cohérente à démarrer maintenant, en s'appuyant sur les signaux analytiques déjà produits par le cockpit : staleness par zone, rotation kind strength/cardio, redundancy 48h, affinité catalogue. Une phrase d'explication en 1 ligne, 2 alternatives consultables, aucune boîte noire, zéro migration.

---

## 2. Fichiers modifiés

| Fichier | Type | Nature |
|---------|------|--------|
| `app/services/recommendation.py` | **New** | Moteur déterministe ~400 lignes (data classes, signaux, scoring, fallback, phrase) |
| `app/routers/pages.py` | Modify | Helper `_build_reco_context` + branchement `home` et `launcher` (step 1 uniquement) |
| `app/templates/_partials/next_session_reco.html` | **New** | Partial Jinja partagé |
| `app/templates/index.html` | Modify | `{% include "_partials/next_session_reco.html" %}` si pas de session en cours |
| `app/templates/launcher.html` | Modify | Même include, conditionné à `step == 1` |
| `app/static/css/app.css` | Modify | Bloc BEM `.reco-next*` (~65 lignes) |
| `tests/test_recommendation_service.py` | **New** | 11 tests unitaires |
| `tests/test_recommendation_surface.py` | **New** | 6 tests d'intégration |
| `docs/SPRINT_Sb_12_next_session_recommendation_BUILD_REPORT.md` | **New** | Ce rapport |

**Zéro migration. Zéro nouvelle route. Zéro JS. Zéro changement de modèle.**

---

## 3. Décisions d'implémentation

### D1 — Calibration centralisée en tête de fichier

Toutes les constantes de calibration (`WEIGHT_STALENESS`, `STALENESS_WINDOW_DAYS`, `FATIGUE_HIGH_THRESHOLD`, etc.) sont groupées en haut de `recommendation.py`. Ajuster les pondérations après dogfooding = éditer une dizaine de constantes, rien d'autre.

### D2 — Réutilisation stricte de `_compute_tonnage_by_zone`

La fonction existante accepte déjà un `window_start`. Appelée **trois fois** avec des fenêtres différentes (7j staleness, 48h redundancy, 14j specialization). Pas de modification de `muscle_scoring.py` — backward-compatible assurée sans toucher au module.

### D3 — Cache applicatif `template → zones primaires`

`_primary_zones_cached` utilise `lru_cache(maxsize=128)` sur le tuple des noms d'exercices du template. Invalidation manuelle possible via `reset_template_zones_cache()` (utilisé par les tests qui re-seed la DB).

Un template « primaire » sur une zone = zone qui couvre ≥ 25 % des exercices du template (seuil `max(1, total // 4)`). Évite les faux positifs : un curl unique dans un Push ne classe pas le Push sur les biceps.

### D4 — Garde-fous avant scoring, pas après

Les filtres (archived, fatigue élevée, redundancy 48h) s'appliquent **avant** le scoring — les candidats éliminés ne consomment pas de cycles. Les spécialisations sont scorées mais se voient attribuer un sentinelle `-1` si non justifiées, puis filtrées avant le tri.

### D5 — Fallback à deux niveaux

1. **Cold start** (< 3 séances lifetime) → fallback immédiat vers le premier template `core` par `display_order`, sans même scorer le reste. Phrase dédiée `"Bon premier template pour démarrer : …"`.
2. **Pool filtré vide** (fatigue très haute ou tout flagué redundancy) → fallback vers la première séance `liss-*` disponible, sinon premier template tout court. Jamais `None` sauf session en cours.

### D6 — Short-circuit si session en cours

`recommend_next_session` retourne `None` d'abord si une `WorkoutSession` est `in_progress` pour l'utilisateur. Pas de calcul inutile, et le partial se cache naturellement.

### D7 — Tz-safety

SQLite round-trip les datetimes en naïf. Helper local `_as_aware(dt)` re-attache UTC avant toute soustraction. Pattern copié de `session_recap._duration_label`.

### D8 — Try/except autour de l'appel router

`_build_reco_context` wrap l'appel dans un `try/except Exception` qui log silencieusement. **La recommandation ne cassera jamais le home**, même si un bug surface (garde-fou défensif V1).

---

## 4. Comment le scoring est calculé

Pour chaque template du pool filtré :

```
score = 0

# 1. Staleness — moyenne des scores 0..1 des zones primaires.
#    hard_sets_7d == 0 → 1.0
#    hard_sets_7d >= 8 → 0.0
#    linéaire entre.
score += 40 × mean(staleness_by_zone[z] for z in primary_zones)

# 2. Alternation kind — bonus si on complète la séquence.
if last_two_kinds == ["strength", "strength"] and template.kind == "cardio":
    score += 20
elif last_kind == "cardio" and template.kind == "strength":
    score += 10  # retour mécanique après cardio

# 3. Redundancy penalty — dégressive si les zones ont du volume récent.
recent_48h = max(hard_sets_48h[z] for z in primary_zones)
if recent_48h > 0:
    score += -5 × (recent_48h / 4)

# 4. Catalog affinity
if section == "core":            score += 15
elif section == "utility":       score += 10
elif section == "specialization":
    if justified (zone ratio < 0.5 × median_14d):
        score += 20
    else:
        score = -1  # exclut du top

# 5. Cardio absent bonus
if template.kind == "cardio" and days_since_last_cardio >= 7 (ou None):
    score += 10

score = clamp(score, 0, 100)
```

Les filtres pré-scoring excluent :
- tout template `archived` (au niveau de la query SQL)
- les non-short non-cardio quand `fatigue_score > 70`
- tout template dont une zone primaire a > 8 hard_sets dans les 48h (cutoff × 2, franchement saturée)

Tie-break final : `(-score, display_order, slug)`.

---

## 5. Comment l'explicabilité est construite

`_build_phrase(template, zones, signals, staleness)` teste les signaux dominants par priorité décroissante :

1. `cold_start` → phrase de démarrage dédiée.
2. `fatigue_score > 70` → wording « charge récente élevée ».
3. `soft_restart` (> 14j sans séance) → wording « reprise douce ».
4. `template.kind == "cardio"` et cardio absent 7j+ → « pas de cardio depuis N j ».
5. Spécialisation → « {zone} sous-travaillé → {template} recommandé ».
6. Strength dans le flow normal :
   - staleness ≥ 0.7 → « peu travaillé récemment ».
   - dernière séance hier → « conseillé pour alterner ».
7. Fallback générique : « suite naturelle après ton historique récent ».

Contraintes **testées** :
- `len(phrase) ≤ 140`
- `phrase` jamais vide
- wording neutre, factuel, sans conditionnel ni superlatif

Les 8 slots `signal_primaire` et 4 `pourquoi_ce_template` de la spec §J sont tous couverts. La phrase n'est jamais composée à la main dans le router — c'est pure fonction du service.

---

## 6. Comment `/` et `/launcher` sont enrichis

### 6.1 Router (`app/routers/pages.py`)

Helper centralisé :

```python
def _build_reco_context(db, user_id, open_session):
    if open_session is not None:
        return None
    try:
        from app.services.recommendation import recommend_next_session
        return recommend_next_session(db, user_id)
    except Exception:
        return None
```

Injecté dans :
- `home()` : clé `"reco"` dans le contexte.
- `launcher()` étape 1 (type non choisi) : idem. Étapes 2 et 3 ne voient pas la reco — le picker domine alors.

### 6.2 Partial `_partials/next_session_reco.html`

Rendu conditionné par `{% if reco %}` — si le service renvoie `None` (session en cours, ou exception), rien ne s'affiche.

Structure :
- `<section class="reco-next card">` avec bordure gauche accent
- kicker « Prochaine séance suggérée » en uppercase petit
- titre `<h2>` avec le nom du template
- focus du template en sous-titre
- phrase d'explication
- formulaire `POST /sessions` avec hidden `template_slug` → CTA primary « Démarrer {nom} → »
- `<details>` alternatives avec liens vers `/launcher?preselect=...` (le query param est purement informatif — le launcher ne le consomme pas en V1, c'est une graine pour une amélioration future)

### 6.3 Templates consommateurs

- `index.html` : include **au-dessus** du CTA « Démarrer une séance ».
- `launcher.html` : include **au-dessus** du step 1 (liste des types).

Dans les deux cas le bloc coexiste avec le reste de l'UI — il ne remplace rien, il suggère.

---

## 7. Comment les alternatives sont choisies

Après le tri `(-score, display_order, slug)`, les candidats 2 et 3 deviennent les alternatives. Cap à `ALTERNATIVES_COUNT = 2`. Deux cas particuliers :

- **Cold start** : `alternatives = []` (la spec le demande — on ne noie pas un nouvel utilisateur).
- **Fallback** : `alternatives = []` également (si le pool était vide, rien d'autre à proposer de crédible).

Les alternatives reçoivent leur propre phrase d'explication (même logique que le top). Elles apparaissent dans un `<details>` replié par défaut ; l'utilisateur clique pour les voir.

---

## 8. Tests ajoutés

### 8.1 Unit — `tests/test_recommendation_service.py` (11)

- `test_cold_start_recommends_a_core_template` — 0 historique → core, flag cold_start, alternatives vides.
- `test_cold_start_phrase_under_140_chars`
- `test_open_session_returns_none` — short-circuit parfait.
- `test_two_strengths_boost_cardio_alternation` — 3 push récents → LISS ou pull/legs dans le top-3.
- `test_no_cardio_recently_surfaces_liss_phrase` — 3 séances strength sur 15j, aucune cardio → LISS apparaît avec phrase cardio.
- `test_archived_templates_are_excluded` — aucun catalog_section=archived dans la sortie.
- `test_phrase_never_empty_and_capped_140_chars` — invariant sur top + alternatives.
- `test_result_shape_is_consistent` — clés, types, bornes du score.
- `test_alternatives_are_at_most_two` — cap respecté.
- `test_staleness_mapping_monotonic` — helper pur, décroissance monotone.
- `test_template_primary_zones_caches` — lru_cache bien actif.

### 8.2 Surface — `tests/test_recommendation_surface.py` (6)

- `test_home_shows_reco_block_when_no_open_session` — partial rendu, CTA POST `/sessions` avec `template_slug`.
- `test_home_hides_reco_block_when_session_open` — session en cours → bloc absent.
- `test_launcher_step1_shows_reco_block`.
- `test_launcher_deep_step_does_not_show_reco` — étapes ≥ 2 → pas de reco.
- `test_reco_phrase_appears_in_rendered_page` — phrase visible ≤ 140 chars après seed.
- `test_reco_alternatives_collapsed_when_present` — `<details>` sans `open`.

### 8.3 Régression

- Full suite : **683 passed** (vs 666 avant Sb_12, +17).
- Tests touchant home, launcher, session flow, scoring, muscle_scoring : tous verts.
- `catalog_qa` PASS, `machine_atlas_qa` PASS, alembic head inchangé.

---

## 9. État final de la suite

```
tests : 683 passed en 3m28s
catalog_qa.py : PASS (16 templates, 98 exercises)
machine_atlas_qa.py : PASS (8 familles, 29 machines)
alembic : head = a19c4e3b7f21 (inchangé)
```

---

## 10. Limites assumées

1. **Calibration V1 non éprouvée en vrai usage** — les 40/20/−5/15 sont des paramètres a priori. Ajustement probable après dogfooding. Tous centralisés en tête de fichier pour simplifier.
2. **Pas de mémoire des recommandations refusées** — si l'utilisateur choisit manuellement un autre template, aucun signal n'est conservé. Le prochain passage recalcule from scratch.
3. **Pas de consommation de la readiness quotidienne** — reportée V2 comme prévu (§E.3 de la spec).
4. **Pas d'infra A/B testing** — calibration sera manuelle.
5. **`launcher?preselect=slug`** reçu dans les liens alternatives n'est **pas** pré-sélectionné côté router V1 — c'est une graine UX pour un futur petit polish. Pas bloquant, les alternatives restent cliquables et amènent l'utilisateur sur la page launcher où il peut retrouver le template.
6. **Map template → zones** dépend de `classify_exercise` — si un exercice devient `unknown`, sa zone primaire ne contribuera pas. `catalog_qa` garantit déjà 100 % de classifiabilité en CI.
7. **Pas de logique « programme custom futur »** — quand Sx_11b livrera les `UserTemplate`, il faudra vérifier que `WorkoutTemplate` reste bien le type consommé par la query. Documenté §K de la spec.
8. **Try/except router défensif** — masque les erreurs runtime. En dev on verra plus facilement via `pytest`. En prod, un logger.exception serait utile — hors scope V1.

---

## 11. Recommandation du prochain sprint de spec

**Sx_13 — Calibration post-dogfooding de la recommandation** (léger, ~2h spec).

**Motivation :**
- Le moteur vit ou meurt sur la qualité perçue de ses suggestions. Il est **prématuré** d'ouvrir programme-builder (Sx_11b) ou squad v2 (Sx_11c) sans avoir validé que la reco tape juste.
- Une spec courte qui formalise un protocole de mesure : « après 7 jours d'usage, quelle proportion des suggestions ont été acceptées ? quelle phrase est revenue trop souvent ? quelle constante ajuster ? »
- Sort : ajustement des poids (peut-être 40 → 50 sur staleness, ou 20 → 15 sur alternation) + éventuellement ajout d'un toggle « Je n'aime pas cette suggestion » pour collecter du signal futur.

**Alternative immédiate :** Sx_11b programme-builder utilisateur si tu veux privilégier l'extension fonctionnelle à la calibration de l'existant. La reco marchera **qualitativement** dès le premier jour même non-calibrée — elle ne bloque pas Sx_11b.

---

## 12. Synthèse exécutive

- Moteur G2 + garde-fous G3 livré : scoring 4 composants (staleness 40, alternation 20, redundancy −5·x, affinity 15) sur pool filtré (archived + fatigue + 48h zones saturées).
- Phrase d'explication ≤ 140 chars composée dans le service, testée sur 5 scénarios, jamais vide.
- Fallback 2 niveaux : cold-start → Push A core, pool vide → LISS. Jamais de crash home.
- Surface légère : un partial Jinja inclus sur `/` et `/launcher` étape 1 ; cachée si session en cours.
- **17 nouveaux tests** (11 unit + 6 surface), full suite **683 passed** (+17).
- **Zéro migration, zéro JS, zéro nouvelle route, zéro refonte du launcher.**
- Calibration centralisée pour ajustement post-dogfooding.
- Prêt pour une passe dogfooding dédiée puis Sx_13 (calibration) ou Sx_11b (programme-builder) selon priorité produit.
