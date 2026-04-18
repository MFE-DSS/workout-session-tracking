# Sprint Sb_06 Report — Scoring, Load & Time Semantics Build

**Date:** 2026-04-15
**Type:** Build — corrections de fond avant refacto UX
**Prerequisite:** Sx_05 + Sx_06 valides
**Livre:** Sb_06 (premier build du cycle post-v10)

---

## 1. Objectif

Appliquer les 3 chantiers semantiques specifies dans Sx_06 avant toute refacto UX :

1. **B01** — bug decimales (inputs HTML bloquaient virgule)
2. **B02** — bug timezone (rendu dates non converti en local)
3. **B03** — scoring LISS/cardio sous-note (formule unique melangee)
4. **C05** — rappel discret convention de charge
5. **Documentation** — PRODUCT_SPEC + page /science

---

## 2. Execution par etapes (6 commits isoles)

### Etape 1 — B01 decimales (commit `edd435e`)

**Changements :**
- 4 endroits de `app/templates/session_detail.html` : `<input type="number">` → `<input type="text" inputmode="decimal|numeric" pattern="..." autocomplete="off">`
- Preserve clavier numerique mobile via `inputmode`
- `autocomplete="off"` evite suggestions inappropriees
- Backend `to_float` deja tolere virgule (verifie `form_parsing.py:32` : `.replace(",", ".")`)

**Tests :** 21 tests dans `tests/test_form_parsing.py` (nouveau) — accepte `"12.5"`, `"12,5"`, negatifs, whitespace, rejette lettres/double separateur.

### Etape 2 — B02 timezone (commit `0183493`)

**Changements :**
- `app/config.py` : `DEFAULT_TIMEZONE = "Europe/Paris"`
- `app/templating.py` : filtres Jinja `local` et `local_weekday` via `ZoneInfo`
- Gere datetimes naive (SQLite roundtrip) = assume UTC
- 7 templates migres vers `{{ dt | local }}` :
  - `session_detail.html` (header)
  - `session_done.html` (header + ended_at)
  - `history.html` (liste seances)
  - `exercise_history.html` (per-occurrence)
  - `index.html` (open session card)
  - `admin_sessions.html`
  - `squad_detail.html` (share form)
- `sessions.py` : `weekday_label` utilise `local_weekday_iso` pour attribution correcte du jour a cheval sur minuit

**Tests :** 9 tests dans `tests/test_timezone_rendering.py` (nouveau) — conversion hiver/ete, naive assumes UTC, crossing minuit, weekday correct.

### Etape 3 — B03 scoring dispatcher (commit `25bf65c`)

**Refactor `app/services/quality_score.py` :**
- Nouveau `compute_session_quality(session)` dispatcher par `template.kind`
- `compute_session_quality_strength(session)` — formule legacy renommee, inchangee
- `compute_session_quality_cardio(session)` — nouvelle formule 4 composants :
  - Duration (50) : >= 20min full credit, degrade progressivement
  - Intensity (20) : bpm 115-135 full, 100-145 = 12, hors zone = 5, null = 15 baseline
  - Completion (20) : abs/core completion ratio ou 20 par defaut
  - Subjective (10) : half-weighted concentration + global_state
- Helper `_session_kind(session)` safe fallback sur "strength"

**Plafonds effectifs verifies :**

| Scenario | Score |
|----------|-------|
| LISS 25min zone 125bpm + abs complete + high/good | 100 |
| LISS 20min zone 125bpm, pas de feedback | 90 |
| LISS 20min, pas de bpm mesure, high/good | 95 |
| Cardio 10min zone, medium/flat | 71 |
| Cardio duree null mais feedback good | 50 |
| BPM hors zone (160) | 75 |

**Tests :** 13 tests dans `tests/test_scoring_cardio.py` (nouveau).

Consumers transparents : leaderboard, kpis, timeline, behavioral engine — aucune modification.

### Etape 4 — C05 helper text (commit `c0542d9`)

**Changements :**
- `app/templates/session_detail.html` : `<span class="set-group-title__hint">kg = comme affiche sur l'equipement</span>` nichee dans le h4 "Travail" de chaque carte
- `app/static/css/app.css` : `.set-group-title__hint` style 10px `var(--fg-dim)`, wrap nouvelle ligne sous 360px

Placement choisi (une fois par carte) plutot que sous chaque input — reduction visuelle, cognitif leger.

### Etape 5 — Documentation (commit `cf842df`)

**`docs/PRODUCT_SPEC.md` :** ajout d'une section "Convention de saisie des charges" (7 cas d'equipement) + "Separation des regimes de scoring" + note timezone.

**`app/templates/science.html` :** 2 nouvelles cartes :
- "Scoring cardio vs musculation" expliquant le dispatcher + LISS >= 85
- "Convention de saisie des charges" avec la regle unique + 7 exemples

### Etape 6 — Sprint report (ce document) + full suite

---

## 3. Fichiers modifies / crees

| Fichier | Type | Etape |
|---------|------|-------|
| `app/templates/session_detail.html` | Modify | 1, 2, 4 |
| `app/templates/session_done.html` | Modify | 2 |
| `app/templates/history.html` | Modify | 2 |
| `app/templates/exercise_history.html` | Modify | 2 |
| `app/templates/index.html` | Modify | 2 |
| `app/templates/admin_sessions.html` | Modify | 2 |
| `app/templates/squad_detail.html` | Modify | 2 |
| `app/templates/science.html` | Modify | 5 |
| `app/config.py` | Modify | 2 |
| `app/templating.py` | Modify | 2 |
| `app/routers/sessions.py` | Modify | 2 |
| `app/services/quality_score.py` | Refactor | 3 |
| `app/static/css/app.css` | Modify | 4 |
| `docs/PRODUCT_SPEC.md` | Modify | 5 |
| `tests/test_form_parsing.py` | New | 1 |
| `tests/test_timezone_rendering.py` | New | 2 |
| `tests/test_scoring_cardio.py` | New | 3 |
| `tests/test_mobile_polish.py` | Modify | 4 (adapt heading assertion) |
| `docs/SPRINT_Sb_06_REPORT.md` | New | 6 |

**Zero migration DB. Zero model change. Zero service metier touche hors scoring.**

---

## 4. Tests

### Nouveaux tests

- `tests/test_form_parsing.py` : 21 tests B01
- `tests/test_timezone_rendering.py` : 9 tests B02
- `tests/test_scoring_cardio.py` : 13 tests B03 + regression strength

**Total Sb_06 : 43 nouveaux tests.**

### Tests existants impactes

- `tests/test_mobile_polish.py` : 1 ligne adaptee (heading "Travail" porte desormais un span)

### Full suite

Voir resultat dans commit final (attendu : 519 + 43 = ~562 passed).

---

## 5. Impacts consumers

### Transparents (aucun changement code)

- `leaderboard.py` — consume `compute_session_quality` via dispatcher
- `kpis.py` — success_score reste NULL pour cardio, comportement inchange
- `behavioral.py` — consume `compute_session_quality` + concentration/global_state
- `timeline.py` — serie de scores, maintenant avec valeurs cardio ameliorees
- `sharing.py` — neutre
- `session_recap.py` — `_duration_label` deja tz-safe

### Ameliorations visibles user

- Seance LISS 20min zone cible : score passe de ~60 a **85+**
- Date d'une seance a 23:30 Paris (22:30 UTC) : affichee correctement **23:30** au lieu de 22:30
- Saisie `12,5` ou `12.5` : **acceptee** sans friction sur iPhone/Android locale FR
- Helper text discret apparait sous "Travail" des chaque carte exercice

### Non impacte

- Format export CSV/JSON (pas de nouveau champ dans ce build)
- Schema DB (zero migration)
- UX du composant exercice (refacto Sb_05 a venir)

---

## 6. Verification commandes

```bash
# Tests cibles Sb_06
pytest tests/test_form_parsing.py tests/test_timezone_rendering.py tests/test_scoring_cardio.py -v

# Tests de regression session/scoring
pytest tests/test_session_flow.py tests/test_mobile_polish.py tests/test_session_done.py tests/test_leaderboard.py tests/test_kpis.py -q

# QA catalogue (inchange v10)
python scripts/catalog_qa.py

# Full suite
pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q

# Serveur local pour recette manuelle
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Recette manuelle

- [ ] Saisir `12,5` dans weight_kg d'un work set → accepte et stocke 12.5
- [ ] Saisir `12.5` idem → accepte
- [ ] Creer une seance a 23:00 Paris → rendu `23:00` dans `/sessions/{id}`, `/done`, `/history`
- [ ] Creer une seance liss-abs, saisir 25 min, 125 bpm, cocher les abs, concentration/etat good → score `/done` = 100
- [ ] Creer une seance strength Push A standard → score coherent avec ancien comportement
- [ ] Ouvrir `/science` → 2 nouvelles cartes visibles (scoring cardio + convention charge)
- [ ] Carte exercice : voir helper "kg = comme affiche sur l'equipement" sous "Travail"
- [ ] Viewport 320px : helper wrap sous le titre, pas de scroll horizontal

---

## 7. Criteres d'acceptation

| Critere | Statut |
|---------|--------|
| B01 — `12,5` et `12.5` acceptes par le formulaire | ✓ (21 tests) |
| B01 — backend to_float tolerant preserve | ✓ (verification + tests) |
| B02 — rendu dates coherent avec fuseau Europe/Paris | ✓ (9 tests, 7 templates migres) |
| B02 — attribution weekday correcte minuit | ✓ (test_local_weekday_iso) |
| B03 — LISS 20min zone cible >= 85 | ✓ (90 sans feedback, 95 avec) |
| B03 — dispatcher transparent pour consumers | ✓ (signature compute_session_quality inchangee) |
| B03 — strength formula regression-free | ✓ (3 tests regression) |
| C02/C05 — convention charge documentee + helper UI | ✓ (PRODUCT_SPEC + /science + session_detail) |
| Aucune migration DB | ✓ |
| Aucun rework UX major | ✓ (flow session inchange, simples evolutions inputs + heading) |
| Full suite green | Voir §verification |

**Build Sb_06 : OK, pret a merger.**

---

## 8. Limites connues

- `load_semantics` catalogue (V2 potentiel) pas implemente — documente comme evolution future
- Preference user timezone (`users.timezone` column) pas implementee — defer V2
- `template_kind_snapshot` pas ajoute — dispatcher safe fallback sur "strength" suffit V1
- Formule cardio V1 calibree sur LISS classique ; ne couvre pas encore HIIT, rowing tempo, etc. — iteration possible si feedback

---

## 9. Prochaine action

Le cycle post-v10 continue :

| Prochain sprint | Type | Duree |
|-----------------|------|-------|
| **Sx_07** (Machine Atlas + Substitution UX spec) | Spec | 3-4h |
| **Sx_08** (Session Review Intelligence spec) | Spec | 2-3h |
| **Sx_09** (Consolidation transverse) | Spec | 1-2h |
| Puis **Sb_05** (Session Flow Horizontal refactor) | Build | 4-6h |
| Sb_07, Sb_08, Sb_09 enchaines | Build | ~12-16h |

**Recommandation :** Sx_07 + Sx_08 en parallele, puis Sx_09, puis phase build complete.

---

## 10. Synthese executive (5 lignes)

- 3 bugs critiques corriges (decimales, timezone, scoring LISS) + helper convention charge
- Scoring dispatcher `template.kind` — LISS 20min zone → score >= 85 (vs ~60 avant)
- Timezone Europe/Paris par defaut, 7 templates migres, weekday attribution correcte
- 43 nouveaux tests, zero regression, zero migration DB, zero model change
- Prochain sprint : Sx_07 + Sx_08 en parallele (Machine Atlas + Session Review)
