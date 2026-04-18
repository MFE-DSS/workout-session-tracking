# Sprint Sb_08 Report — Session Review Intelligence

**Date:** 2026-04-18
**Type:** Build Anomalies + Hints + Confidence + /done enrichi
**Prerequisite:** Sx_09 figé, Sb_07 livré
**Débloque:** Sb_09

---

## 1. Objectif

Enrichir la synthèse post-séance avec des détections déterministes (anomalies), suggérer discrètement sur la carte active (hints), calculer un score de confiance du logging, et réduire la saisie libre inline. Zéro JS, zéro migration.

---

## 2. Décisions d'implémentation

### D1 — Trois services indépendants

- `app/services/anomalies.py` : 5 règles déterministes (A–E), toutes `info`, toutes chiffrées, retourne une liste de dataclasses `Anomaly`.
- `app/services/hints.py` : 2 règles V1 (A–B), dataclass `Hint`, destiné à la carte active uniquement.
- `app/services/confidence.py` : formule 5 composantes (40+15+10+10+15+10 pts), bornée 0–100, renvoie aussi un niveau (`eleve`/`moyen`/`faible`).

Chaque service a des tests unit dédiés (12 + 8 + 6 = 26 tests).

### D2 — `session_recap` étendu, pas refactoré

`build_recap` accepte un `prior_weight_by_code` optionnel, et étend le dict `summary` avec 4 nouveaux blocs :
- `confidence_score: int`, `confidence_level: str`
- `top_progression: dict | None`
- `zones_touched: list[dict]`
- `anomalies: list[dict]`

Compat retro : signature reste backward-compatible (paramètre optionnel), shape existant inchangé.

### D3 — Top progression via attribut transient

Plutôt que requêter le prior dans `session_recap`, le routeur attache `se._prior_summary` à chaque `SessionExercise` avant l'appel à `build_recap` (per-request only). Cela évite de coupler le service de recap à la session DB.

### D4 — Hints actifs via variable template séparée

La variable Jinja `hints` existante (repères de progression Sb_01) est conservée. Les nouveaux hints contextuels Sb_08 passent par `sb08_hints_by_exercise`, rendus dans un bloc dédié **uniquement sur la carte active** (`is_active`).

### D5 — Note exercice en `<details>`

Le textarea `free_note` (140 chars) est replié dans un `<details class="exercise-card__note">` — ouvert par défaut seulement si une note existe déjà. Objectif Sx_08 §6 : réduire la pression visuelle sur la carte. Note session (280 chars) inchangée.

### D6 — Wording neutre garanti

Toutes les formulations suivent §1 de Sx_08 : « À vérifier » et non « Tu as triché » ; « Confiance du logging » et non « Séance fiable » ; « Volontaire ? » et non « Suspect ».

---

## 3. Règles et formules

### 3.1 Anomalies (5 règles info-level)

| Code | Trigger | Message |
|------|---------|---------|
| A | Set `completed=True` sans weight ni reps | « Set #N marqué fait sans reps ni charge saisis » |
| B | `last.weight > first.weight` **ET** `last.reps > first.reps` | « Charge et reps croissent simultanément… À vérifier. » |
| C | `|weight_delta / prior| > 0.30` | « ±X% de charge vs dernière fois. Volontaire ? » |
| D | Warmup completed, aucun work set completed | « Échauffement fait, aucun work set réalisé » |
| E | `success_score ≥ 80` **ET** toutes reps `< min_reps` | « Score élevé mais reps sous la cible, à vérifier. » |

### 3.2 Hints carte active (2 règles)

| Code | Trigger | Message |
|------|---------|---------|
| A | Weight 1ʳᵉ série `> prior × 1.10` | « +X% de charge vs dernière fois — prudence sur l'exécution » |
| B | Une série avec `reps < prior_same_set.reps − 2` | « Set N : reps réduites vs dernière fois — fatigue installée ? » |

Cap strict : 1 hint B max par carte (les suivants sont ignorés pour éviter le bruit).

### 3.3 Confidence score (0–100)

```
40 × (work_sets_with_data / total_work_sets)
15 − (completed_empty_sets / total_work_sets × 15)    [min 0]
10 si concentration présente
10 si global_state présent
15/10/5/0  selon len(anomalies) ≤ 0/2/4/>4
10 si bodyweight présent
───────
total / max × 100 → arrondi
```

Niveaux : ≥ 80 `eleve`, 50–79 `moyen`, < 50 `faible`.

---

## 4. Changements effectués

| Fichier | Type | Nature |
|---------|------|--------|
| `app/services/anomalies.py` | New | 5 règles + dataclass Anomaly + `compute_anomalies` |
| `app/services/hints.py` | New | 2 règles + dataclass Hint + `compute_hints` |
| `app/services/confidence.py` | New | `compute_confidence_score` + `level_for` |
| `app/services/session_recap.py` | Modify | +4 blocs summary, signature `prior_weight_by_code=None` |
| `app/services/stats.py` | Modify | `_summarise_prior` expose aussi `sets: [...]` (additif) |
| `app/routers/sessions.py` | Modify | Calcul hints Sb_08 par carte, `_prior_summary` transient pour /done |
| `app/templates/session_detail.html` | Modify | Rendu hints actifs + note en `<details>` |
| `app/templates/session_done.html` | Modify | 4 nouveaux blocs : confidence badge, top progression, zones, à vérifier |
| `app/static/css/app.css` | Modify | Styles confidence, top-progression, zones, anomalies, hints actifs, note details |
| `tests/test_anomalies.py` | New | 12 tests (5 règles × trigger/silent + clean session) |
| `tests/test_hints.py` | New | 8 tests (2 règles + coexistence + cap B) |
| `tests/test_confidence.py` | New | 6 tests (formule, bornes, bonus, thresholds) |
| `tests/test_session_recap.py` | Extend | 3 nouveaux tests sur blocs Sb_08 |
| `tests/test_session_done.py` | Extend | 3 nouveaux tests rendu (confidence, zones, anomalies) |
| `docs/SPRINT_Sb_08_REPORT.md` | New | Ce rapport |

**Zéro migration DB. Zéro nouvelle route. Zéro JS.**

---

## 5. Tests

### Nouveaux tests Sb_08 : 32 au total

- `test_anomalies.py` (12) : A trigger/silent, B trigger/silent, C trigger/silent/no-prior, D trigger/silent, E trigger/silent, aggregate clean
- `test_hints.py` (8) : A trigger/silent/no-prior, B trigger/silent, A+B coexist, cap B, empty
- `test_confidence.py` (6) : high clean, low on empty, bodyweight bonus, bornes, thresholds, penalty anomalies
- `test_session_recap.py` (3) : shape Sb_08 blocs, zones non vides, rule A surface
- `test_session_done.py` (3) : badge confidence, zones block, anomalies block

### Régression

- Full suite : **627 passed** (vs 595 après Sb_07, +32)
- 55 tests session/recap/done/flow/nav/mobile ciblés : verts
- 4 tests recap existants inchangés (compat retro `build_recap`)

---

## 6. Garde-fous Sx_02 + Sx_05 + Sx_08 respectés

| Garde-fou | Statut |
|-----------|--------|
| SSR + zéro JS | ✓ |
| Snapshots immutables | ✓ (anomalies lisent uniquement) |
| Déterministe, pas prédictif | ✓ (pas de ML, pas de LLM) |
| Wording neutre | ✓ (« À vérifier », « Volontaire ? », « Prudence ») |
| Non bloquant | ✓ (affichage info-level uniquement) |
| Zéro migration | ✓ |
| Une carte active | ✓ (hints conditionnés par `is_active`) |
| Cap dur V1 (5 anomalies / 2 hints) | ✓ |

---

## 7. Vérification

```bash
# Tests cibles Sb_08
pytest tests/test_anomalies.py tests/test_hints.py tests/test_confidence.py -v

# Tests surface
pytest tests/test_session_recap.py tests/test_session_done.py -v

# Full suite
pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q

# Serveur local
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Recette manuelle

- [ ] Démarrer Push A, saisir E1 avec +20 kg vs dernière fois → sur la carte active, hint A affiche « +X% de charge vs dernière fois — prudence ».
- [ ] Saisir E1 set 2 avec reps très basses vs prior → hint B affiche « Set 2 : reps réduites… ».
- [ ] Cocher un set « Fait » sans rien saisir → terminer la séance → sur `/done`, le bloc « À vérifier » contient « Set #N marqué fait sans reps ni charge ».
- [ ] Séance propre → `/done` affiche badge « Confiance du logging : eleve (9X) », bloc « Top progression », bloc « Zones sollicitées ».
- [ ] Note exercice pliée par défaut, s'ouvre si déjà remplie.

---

## 8. Critères d'acceptation

| Critère | Statut |
|---------|--------|
| 5 règles anomalies déterministes + tests | ✓ |
| 2 hints V1 carte active + tests | ✓ |
| Confidence score formulé + testé | ✓ |
| `/done` affiche top progression / zones / à vérifier / confidence | ✓ |
| Note exercice réduite en `<details>` | ✓ |
| Wording neutre garanti | ✓ |
| Zéro JS, zéro migration | ✓ |
| Full suite verte | ✓ (627) |

**Build Sb_08 : OK, prêt à merger.**

---

## 9. Limites et non-objectifs

- Rule C passive sans prior (acceptable — on ne peut pas juger)
- Top progression regarde 1 occurrence précédente (V1)
- Zones : regroupement par zone primaire uniquement (pas de secondaires)
- Pas de graphique dans `/done`
- Pas de narration auto-générée (différé Sx_08 §13.4)
- Hints cap strict V1 : pas d'auto-apply, pas de rythme, pas de muscle_sensation

---

## 10. Synthèse exécutive (5 lignes)

- 3 nouveaux services déterministes : anomalies (5 règles), hints (2 règles), confidence (formule 5 composantes).
- `/done` enrichi de 4 blocs : badge confiance, top progression, zones sollicitées, à vérifier.
- Note exercice repliée en `<details>`, hints contextuels uniquement sur carte active.
- 32 nouveaux tests ; full suite 627 passed.
- Prochain sprint : Sb_09 History Visual & Analytics Alignment (3–5h).
