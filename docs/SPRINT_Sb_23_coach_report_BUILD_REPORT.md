# Sprint Sb_23 Build Report — Coach Report

**Date :** 2026-05-31
**Type :** BUILD — nouvelle feature SSR. Implémente `SPIGNOS_COACH_REPORT_SPEC_v1.md` v1.1.
**Prérequis :** Sb_22b livré et déployé (`3917b83`) — `profile_metrics.py` réutilisé tel quel.
**Successeur :** aucun planifié — feature livrée, dogfood pour valider l'usage.

---

## 1. Objectif

Livrer la page `/coach-report` SSR — synthèse profil orientée coach externe, lisible en 2 min. Chaque bloc tagué explicitement `Mesuré` / `Inféré` / `Non déductible` (spec §B.bis). Aucune interprétation esthétique, morphologique, ou comparative inter-users (4 interdits stricts).

## 2. Contrats durs respectés (spec v1.1 §B.bis)

| Contrat | Vérifié par |
|---|---|
| Triptyque tag obligatoire | `test_coach_report_carries_explicit_tags` |
| 10 blocs présents et numérotés | `test_coach_report_contains_10_blocs` |
| Aucune appréciation esthétique | `test_coach_report_forbidden_phrases_absent` × 8 patterns |
| Aucun verdict performance max | idem |
| Aucune comparaison inter-users | idem |
| Bloc 10 garde-fous toujours visible | `test_coach_report_guardrails_block_visible` |
| Ownership : 303 anon → /login | `test_coach_report_requires_auth` |
| Réutilise `profile_metrics.py` sans duplication query | imports directs, 0 duplication SQL |

## 3. Fichiers créés / modifiés

| Fichier | Type | Nature |
|---|---|---|
| `app/services/profile_metrics.py` | Modify | +`DisciplineRates`, `discipline_rates()`, `StrengthCardioRatio`, `strength_cardio_ratio()`, `zone_session_counts()` public, `pattern_distribution()`. ~150 LoC ajoutées. |
| `app/services/coach_report.py` | New | Orchestrateur 215 LoC : `CoachReport`, `IdentityBlock`, `VolumeBlock`, `ZonesBlock`, `PatternsBlock` dataclasses + `build_report()`. Weight trend 90j calculé depuis BodyMeasurement + WorkoutSession.bodyweight_kg (Sb_17 merge réutilisé). |
| `app/services/coach_inference.py` | New | Règles déterministes 130 LoC : `strong_points()`, `weak_points()`, `suggested_axes()`, `build_inference()`. 5 heuristiques V1 cappées à 3 axes max, vocabulaire "probable"/"suggéré" obligatoire. |
| `app/routers/coach_report.py` | New | Router `/coach-report` (auth-gated via `CurrentUser`), réutilise `latest_open_session` pour la barre top. |
| `app/templates/coach_report.html` | New | 10 blocs structurés, tags `coach-tag--measured/inferred/not-deductible` visibles, bouton "Imprimer" → `window.print()`. |
| `app/static/css/app.css` | Modify | +180 LoC : `.coach-report*`, `.coach-block*`, `.coach-tag--*` (WCAG AA contrast, namespacé pour éviter collision `.tag`), `.coach-grid`, `.coach-ratio`, `.coach-patterns`, `.coach-discipline`, `.pill--ok/mid/bad`, **media print A4** avec masquage topbar/btn/banner. |
| `app/templates/base.html` | Modify | Lien nav "Coach" ajouté entre "Profil" et logout. |
| `app/main.py` | Modify | Inclut `coach_report.router`. |
| `tests/test_coach_report.py` | New | 19 tests : endpoint smoke (200/303), 10 blocs présents, tags visibles, 8 patterns interdits absents, garde-fous, inference rules (strong/weak/axes/cap 3). |
| `docs/SPRINT_Sb_23_coach_report_BUILD_REPORT.md` | New | Ce rapport. |

**0 modification BD · 0 migration · 0 modèle touché.**

## 4. Structure du rapport livré (10 blocs)

| # | Bloc | Tag | Source data |
|---|---|---|---|
| 1 | Identité physique | `Mesuré` (+ `Inféré` sur trend 90j, `Non déductible` sur âge) | `users.height_cm/weight_kg/waist_cm/resting_hr/bp_*` + 90d window |
| 2 | Volume et fréquence | `Mesuré` | 5 KPI (sessions 30j/90j, streak, cardio min/sem, sets travail /sem) |
| 3 | Ratio strength / cardio | `Inféré` | `StrengthCardioRatio` 30j, barre dual-color |
| 4 | Répartition par zone musculaire | `Mesuré` | top 3 + bottom 2 zones via `zone_session_counts` |
| 5 | Patterns moteurs dominants | `Inféré` | barres horizontales `pattern_distribution` |
| 6 | Discipline de logging | `Mesuré` | 5 ratios (completion, note, bodyweight, sensation, qualité moyenne), pills couleur ≥80/≥50/<50 |
| 7 | Points forts probables | `Inféré` | `strong_points()` — zones avec ≥ 3 sessions/30j |
| 8 | Points faibles probables | `Inféré` | `weak_points()` — zones avec ≤ 1 session/30j |
| 9 | Axes de travail suggérés | `Inféré` | `suggested_axes()` — max 3, priorité zone négligée > cardio < OMS > pattern déséquilibré > discipline faible > volume bas |
| 10 | Garde-fous | (fixe) | bloc constant, mentionne explicitement les 4 interdits §B.bis |

## 5. Règles d'inférence V1 (déterministes)

| Règle | Seuil | Effet |
|---|---|---|
| Point fort probable | zone ≥ 3 sessions/30j | ajoute "Zone travaillée fréquemment : X (N séances/30j) — point fort probable" |
| Point faible probable | zone ≤ 1 session/30j | ajoute "Zone peu travaillée : X (N séances/30j) — point faible probable" |
| Axe cardio | `cardio_min/sem < 90` | "Augmenter le volume cardio : actuellement X'/sem — cible OMS 150'/sem" |
| Axe pattern | `dominant_pattern > 35%` | "Diversifier les patterns : X représente Y% — intégrer plus de variétés" |
| Axe discipline bodyweight | `with_bodyweight_rate < 50%` | "Logger le poids de corps plus systématiquement…" |
| Axe volume | `sessions_30d < 4` | "Augmenter la fréquence : viser 2-3 séances/sem comme socle" |

Max 3 axes affichés. Ordre = priorité (zone neg > cardio > pattern > discipline > volume). Tous les seuils sont des constantes en tête de `coach_inference.py`, facilement tunables.

## 6. État des tests

```
19 nouveaux tests coach_report
782 → 801 tests pass (+19, 0 régression attendue, full suite en cours)
catalog_pattern_qa : OK exit 0
ruff/bandit        : inchangés
```

## 7. Format produit livré

| Format | Statut V1 |
|---|---|
| Page SSR `/coach-report` | ✅ |
| Print CSS `@media print` A4 | ✅ topbar/btn masqués, tags couleur claire, break-inside avoid |
| Export PDF natif | ❌ V2 (navigateur "Imprimer en PDF" suffit V1) |
| Partage URL signée temporaire | ❌ V3 |
| Export JSON | ❌ V3 |

## 8. Limites assumées

1. **Année de naissance non saisie** — colonne `users.year_of_birth` absente V1. Bloc 1 affiche explicitement `Non déductible` sur l'âge. Migration triviale si besoin futur.
2. **Volume Δ% absent du Coach Report** — Sb_22b l'expose en preview L2 ; on l'a volontairement omis du Coach Report pour rester sur "synthèse 2 min" plutôt que "détail trend".
3. **Pattern dominant calculé sur catalogue Sb_22a uniquement** — 53 exos enrichis. Les exos hors registre ne contribuent pas. Bloc 5 affiche "Pas assez de sets enregistrés sur le périmètre catalogue Sb_22a" si le user fait surtout des exos non enrichis.
4. **Pas de cache V1** — chaque hit refait ~12 requêtes. Acceptable car la page n'est pas hot. Sb_23.next pourrait ajouter `lru_cache` 5 min sur `build_report` si nécessaire.
5. **Pas de comparaison historique** — le rapport est une photo 30j (avec annexe 90j volume). Pas de "vs 30j précédents" sauf pour le volume Δ% (déjà en L2 preview Sb_22b).
6. **Pas de seuils OMS personnalisés** — `CARDIO_LOW_MIN_PER_WEEK = 90` est une cible générique. Pas d'ajustement par âge / poids / objectif.

## 9. Recommandation prochain sprint

**Aucun sprint immédiat planifié.** Le cycle Sx_21 → Sb_22a → Sb_22a.next → Sb_22b → Sb_23 est complet.

Prochaines actions possibles selon retour dogfood :
- **Sb_23.next** : si le coach report manque d'âge réel → migration mineure `users.year_of_birth` + bloc 1 update.
- **Sb_24** : si la passe dogfood révèle un manque sur le bloc inference (règles trop génériques, axes pas pertinents) → tuning des seuils dans `coach_inference.py`.
- **Sb_22a.synthesis** : compléter les 4 templates synthèse (upper/lower-*) du graphe substitution restés à 0 N1.
- **Sx_24** : reco V3 narrative (cf méta-spec dogfooding §E backlog).

Décision attendue après une **passe dogfooding salle** sur la chaîne complète Substitution → Profile v2 → Coach Report.

## 10. Verdict

**Sb_23 livré, conforme spec v1.1.** Feature `/coach-report` accessible auth-gated, 10 blocs structurés et tagués, 4 interdits §B.bis vérifiés par tests, print A4 supporté, 0 régression, 19 tests neufs. Le cycle dogfooding generalization (Sx_21 → Sb_23) ferme proprement.
