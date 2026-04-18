# SPIGNOS Scoring, Load & Time Semantics Spec v1

**Sprint:** Sx_06_scoring_load_and_time_semantics_spec
**Date:** 2026-04-15
**Status:** Spec detaillee (SPEC ONLY — aucun build)
**Prerequisite:** Sx_05 valide
**Suivi par:** Sx_07 (Machine Atlas + Substitution UX) et Sx_08 (Session Review) en parallele
**Debloque:** Sb_06 (premier build du cycle post-v10)

---

## 0. Objet

Produire la specification technique detaillee des **3 chantiers semantiques** que Sb_06 implementera avant toute refacto UX :

1. **Convention canonique de saisie des charges bilaterales** (C02 + C05 + B01)
2. **Separation scoring strength vs cardio** (B03 + P02)
3. **Timezone utilisateur** (B02)

Sx_05 a pose le cadrage global. Sx_06 specifie les regles, formules, et surfaces exactes a modifier.

---

## 1. Chantier A — Convention de charge canonique

### 1.1 Probleme

Ambiguite actuelle de la saisie `weight_kg` dans `set_logs` :

| Cas | User saisit quoi ? |
|-----|-------------------|
| Halteres (developpe couche halteres, curl halteres) | 20 = un seul haltere ? ou 40 = total ? |
| Shoulder press machine a bras independants | 30 = par cote ? ou 60 = total ? |
| Smith machine (bilaterale fixe) | 60 = total barre incluse |
| Hack squat / leg press | 100 = total sur plateforme |
| Cable unilateral (curl cable un bras) | 12 = poids pile |
| Butterfly machine (bilaterale fixe) | 40 = total machine |

Actuellement aucune regle documentee → chaque user decide sa propre convention → historique inconsistent → comparaisons fausses.

### 1.2 Regle canonique

**Regle unique : saisir la charge *telle qu'elle apparait sur l'equipement*.**

| Type d'equipement | Convention | Exemple |
|-------------------|-----------|---------|
| Halteres (bilateraux) | **Un seul haltere** | 20 = deux halteres de 20 |
| Halteres unilateraux (un bras a la fois) | **Un seul haltere** | 20 kg par bras = saisir 20 |
| Machines a bras independants (indep. load) | **Un cote** | Shoulder press machine bras indep. 30 → saisir 30 |
| Machines bilaterales fixes (Smith, hack, leg press, chest press bilaterale, butterfly, pec deck) | **Total affiche** | Hack squat 120 → saisir 120 |
| Cables unilateraux | **Poids de la pile** | Curl cable un bras 12 → saisir 12 |
| Cables bilateraux symetriques | **Poids d'un cote (meme charge)** | Cable cross over 10 par cote → saisir 10 |
| Poids du corps | **Poids externe ajoute (0 si pur BW)** | Dips lestes +20 → saisir 20 ; pull-up BW → saisir 0 |
| Barre olympique libre | **Total barre incluse** | Bench press 20+40 = 60 → saisir 60 |

### 1.3 Justification du choix

- **Simplicite cognitive** : le user regarde l'equipement, saisit le chiffre affiche
- **Minimise l'erreur** : aucune conversion mentale
- **Coherence avec l'UX gym** : c'est la "charge ressentie" sur un cote de mouvement
- **Analytics** : les comparaisons restent coherentes si le meme exercice est toujours saisi de la meme maniere

### 1.4 Alternatives ecartees

| Alternative | Rejet |
|-------------|-------|
| Toujours saisir le total | Oblige a calculer mentalement halteres (20+20=40), friction elevee |
| Toujours saisir par cote | Faux sur bilaterales fixes (user saisirait 30 pour leg press 60 → sous-estime) |
| Champ "par cote" / "total" a chaque exercice | Friction UI insupportable |
| Meta-donnee `load_semantics` par exercice au catalogue | Proposee mais DIFFER V2 (cf. §1.6) |

### 1.5 Rappel discret dans l'UI (C05)

Implementation minimaliste :

- **Helper text** sous le champ `weight_kg` dans la set-row : `"kg (comme affiche sur l'equipement)"`
- Pas de modale, pas d'alerte bloquante
- Texte tres court, `font-size: 11px`, `color: var(--fg-dim)`
- Une fois l'user habitue, le helper reste discret mais toujours visible

Exemple rendu :
```html
<div class="set-row__inputs">
  <label class="set-row__field">
    <input type="text" inputmode="decimal" name="set_123_weight_kg" placeholder="kg">
    <span class="set-row__hint">comme affiche</span>
  </label>
  ...
</div>
```

### 1.6 Champ catalogue `load_semantics` — DIFFER V2

Ajout optionnel a chaque `TemplateExercise` :

```json
{
  "code": "E2",
  "name": "Chest Press machine",
  "load_semantics": "total"
}
```

Valeurs : `"per_side"` | `"total"` | `"bw_added"` | null (= `"total"` par defaut pour compat).

**Differe Sb_06 V1.** Non bloquant. Debloquera plus tard :
- Affichage contextuel du helper ("par cote" vs "total" dynamique)
- Analytics normalisees (total calcule = `weight × (2 si per_side else 1)`)

### 1.7 Bug B01 — fix decimales

**Cause racine confirmee par audit :**
- `app/templates/session_detail.html` utilise `<input type="number">` (HTML5) qui rejette la virgule cote navigateur sur locale FR avant POST
- `app/services/form_parsing.to_float` **accepte deja** la virgule (`value.replace(",", ".")`) — backend OK

**Fix propose :**

```html
<!-- AVANT -->
<input type="number" step="0.5" inputmode="decimal" name="set_{id}_weight_kg">

<!-- APRES -->
<input type="text" inputmode="decimal" pattern="[0-9]*[.,]?[0-9]*"
       name="set_{id}_weight_kg" autocomplete="off">
```

Avantages :
- Accepte point **ET** virgule
- Keyboard numerique preserve sur mobile (`inputmode="decimal"`)
- `pattern` valide cote navigateur sans bloquer
- `autocomplete="off"` evite suggestions inappropriees

Zero regression backend : `to_float` parse les deux formats.

**Surfaces a migrer (audit exhaustif) :**

| Fichier | Lignes | Champs concernes |
|---------|--------|------------------|
| `app/templates/session_detail.html` | 177-232 | set rows : weight_kg (warmup + work) |
| `app/templates/session_detail.html` | 348-353 | session feedback : bodyweight_kg |
| `app/templates/session_detail.html` | 307-317 | cardio : duration_min, bpm_avg, calories |

**Tests requis :**
- Saisie `"12.5"` → stocke 12.5
- Saisie `"12,5"` → stocke 12.5
- Saisie `"abc"` → stocke None (fallback existant)
- Saisie vide → stocke None

---

## 2. Chantier B — Separation scoring strength vs cardio

### 2.1 Probleme

Formule actuelle unique `compute_session_quality(session)` (quality_score.py:44-87) :

```
work_completion (40) + success_score (40) + concentration (10) + global_state (10) = 100
```

Pour une seance cardio (`liss-only`, `liss-abs`) :
- `work_completion` peut etre haut mais base sur tres peu de work sets (0 pour `liss-only`, ~12 pour `liss-abs`)
- `success_score` derive de rep_targets : souvent **None** ou faible sans cible stricte
- Plafond effectif ~60/100 meme pour une seance 30min LISS parfaitement executee

Result : visualisation injuste, user decourage de loguer les cardio.

### 2.2 Dispatcher propose

Nouveau design de `app/services/quality_score.py` :

```python
def compute_session_quality(session: WorkoutSession) -> int:
    kind = session.template.kind if session.template else "strength"
    if kind == "cardio":
        return compute_session_quality_cardio(session)
    return compute_session_quality_strength(session)


def compute_session_quality_strength(session: WorkoutSession) -> int:
    # Formule actuelle renommee, inchangee
    ...


def compute_session_quality_cardio(session: WorkoutSession) -> int:
    # Nouvelle formule §2.3
    ...
```

Le dispatcher est transparent pour tous les consumers (leaderboard, kpis, timeline) qui lisent toujours `quality_score` sans savoir que la formule varie.

### 2.3 Formule cardio V1

**Composants (total 100 pts) :**

| Composant | Max | Signal d'entree |
|-----------|-----|-----------------|
| `duration_component` | 50 | `session.cardio_duration_min` |
| `intensity_component` | 20 | `session.cardio_bpm_avg` vs zone cible LISS (120-130 bpm) |
| `completion_component` | 20 | % de work sets abs completed (si template type `liss-abs` avec exercises) ; 20 par defaut si `liss-only` |
| `subjective_component` | 10 | `concentration` + `global_state` combines (meme logique que strength) |

**duration_component (0-50) :**

```python
def _duration_component(duration_min: Optional[int]) -> float:
    if duration_min is None:
        return 0.0
    if duration_min >= 20:
        return 50.0  # Objectif LISS atteint
    if duration_min >= 15:
        return 40.0  # Presque la
    if duration_min >= 10:
        return 25.0  # Demarrage
    if duration_min >= 5:
        return 10.0
    return 0.0
```

**intensity_component (0-20) :**

```python
def _intensity_component(bpm: Optional[int]) -> float:
    if bpm is None:
        # Pas de capteur BPM : ne penalise pas, retourne baseline
        return 15.0
    # Zone cible LISS : 120-130
    if 115 <= bpm <= 135:
        return 20.0  # Dans zone (avec tolerance)
    if 100 <= bpm <= 145:
        return 12.0  # Proche de la zone
    return 5.0  # Hors zone
```

**completion_component (0-20) :**

```python
def _cardio_completion_component(session) -> float:
    exs = session.session_exercises or []
    if not exs:
        # liss-only pur : pas d'exos abs, full credit
        return 20.0
    total = sum(1 for se in exs for sl in se.set_logs if sl.kind == "work")
    done = sum(1 for se in exs for sl in se.set_logs
               if sl.kind == "work" and sl.completed)
    if total == 0:
        return 20.0
    return 20.0 * (done / total)
```

**subjective_component (0-10) :** inchange vs strength (concentration 5 + global_state 5 ou equivalent).

### 2.4 Plafond effectif LISS bien fait

Scenario type : 25 min velo zone 125 bpm, abs `liss-abs` 4 exos tous completes, concentration high, global_state good.

```
duration_component  = 50  (>= 20 min)
intensity_component = 20  (zone cible)
completion_component= 20  (abs tous fait)
subjective_component= 10  (high + good)
TOTAL               = 100
```

Scenario minimal : 20 min velo sans BPM mesure, pas d'abs, pas de feedback.
```
duration_component  = 50
intensity_component = 15 (baseline bpm null)
completion_component= 20 (pas d'abs → full par default)
subjective_component=  0 (pas de feedback)
TOTAL               = 85
```

**Plafond effectif pour LISS 20min bien fait : >= 85.** Objectif respecte (>= 80 demande dans Sx_05).

### 2.5 Formule strength V1

**Inchangee** — re-documentation pour clarite :

```python
def compute_session_quality_strength(session) -> int:
    # 1. Work set completion (40)
    total_work = 0
    done_work = 0
    for se in session.session_exercises:
        for sl in se.set_logs:
            if sl.kind == "work":
                total_work += 1
                if sl.completed:
                    done_work += 1
    work_component = (done_work / total_work * 40) if total_work > 0 else 0.0

    # 2. Success score (40)
    scores = [se.success_score for se in session.session_exercises
              if se.success_score is not None]
    if scores:
        avg_score = sum(scores) / len(scores)
        score_component = (avg_score / 100) * 40
    else:
        score_component = 0.0

    # 3. Concentration (10)
    concentration_component = float(
        _CONCENTRATION_POINTS.get(session.concentration or "", 0)
    )

    # 4. Global state (10)
    global_state_component = float(
        _GLOBAL_STATE_POINTS.get(session.global_state or "", 0)
    )

    raw = work_component + score_component + concentration_component + global_state_component
    return max(0, min(100, round(raw)))
```

### 2.6 Impacts consumers — matrice exhaustive

| Consumer | Fichier | Impact | Action Sb_06 |
|----------|---------|--------|--------------|
| `quality_score.compute_session_quality` | `app/services/quality_score.py` | Refactor vers dispatcher | Core change |
| `kpis.avg_success_score_30d` | `app/services/kpis.py:90-98` | `success_score` reste NULL pour cardio → deja exclus via `is_not(None)` | Verifier comportement, potentiellement filtrer `template.kind` |
| `kpis.compute_template_kpis` | `app/services/kpis.py:280+` | Agrege avg_success_score par template → OK pour templates strength, NULL pour cardio | Verification neutre |
| `behavioral.compute_behavioral_state` | `app/services/behavioral.py` | Utilise `compute_session_quality` du dernier completed → dispatcher transparent | Neutre |
| `leaderboard.compute_leaderboard` | `app/services/leaderboard.py` | Somme des `session_points = quality_score × completion_ratio` → cardio contribuera differemment | Valider : le score plus eleve pour cardio bien fait = OK |
| `timeline.build_quality_timeline_svg` | `app/services/timeline.py` | Serie de quality scores mixte → visuellement 2 regimes | Sb_09 : dispatcher rendu (couleur par kind ?) |
| Sparkline home | `app/templates/index.html` L108-130 | Idem | Sb_09 |
| `session_recap.build_recap` | `app/services/session_recap.py` | Consomme pas directement quality_score, OK | Neutre |
| `export_builder` | `app/services/export_builder.py` | Exporter `session_kind` en plus | Sb_06 |
| `physique dashboard` + `muscle_scoring` | | Consume `actual_exercise_name` via sessions strength seulement ? | Verifier : ne devrait pas mixer cardio, deja filtre par work sets |

### 2.7 Question consumer : filtrer cardio dans `kpis.avg_success_score_30d` ?

Probleme : aujourd'hui un utilisateur qui fait beaucoup de cardio aura sa moyenne success_score 30j toujours plus propre (seul le strength compte car cardio = NULL). OK.

**Aucune modification necessaire sur kpis.** La formule actuelle est deja implicitement correcte parce que success_score est NULL pour cardio.

### 2.8 Question : `kind` lu de template ou snapshot ?

Actuellement `session.template` pointe vers le TemplateExercise actuel (via FK nullable). Apres une eventuelle re-seed catalogue, `template` peut etre NULL.

**Decision :** ajouter un snapshot `template_kind_snapshot` sur `WorkoutSession` (VARCHAR 16 nullable, default `"strength"`), rempli au create. Permet un dispatcher fiable meme apres re-seed catalogue.

**Migration requise :** ajouter colonne `workout_sessions.template_kind_snapshot` NULLABLE. Backfill via `template.kind` pour sessions existantes. Alembic migration simple.

**Alternative sans migration :** dispatcher lit `session.template.kind if session.template else "strength"`. Default safe mais perd l'info si catalogue reseed → session orphelines deviennent strength par defaut. Acceptable V1.

**Recommandation V1 :** alternative sans migration. Migration additive peut etre ajoutee plus tard.

---

## 3. Chantier C — Timezone utilisateur

### 3.1 Probleme

Etat actuel :
- Stockage : `datetime.now(timezone.utc)` a la creation de session → **UTC correct**
- Rendu : templates utilisent `session.started_at.strftime('%d/%m %H:%M')` → **rendu UTC brut sans conversion locale**

Consequence pour un user a Paris (UTC+1 hiver / UTC+2 ete) :
- Seance commencee a 19:00 locale → stockee 18:00 UTC (hiver) ou 17:00 UTC (ete)
- Rendu : `18:00` (hiver) ou `17:00` (ete) **au lieu de 19:00 attendu**
- Pire : seance vers minuit peut etre attribuee au jour precedent

### 3.2 Solution cible

**Stockage :** UTC maintenu (decision correcte, aucun changement).

**Rendu :** conversion en timezone utilisateur a l'affichage via helper Jinja.

### 3.3 Strategie V1 — simple et robuste

**Decision arbitree :** defaut Europe/Paris pour tous les users, avec extensibilite future.

**Implementation :**

1. Config global `app/config.py` :
```python
DEFAULT_TIMEZONE = "Europe/Paris"
```

2. Helper Jinja `app/templating.py` :
```python
from zoneinfo import ZoneInfo
from datetime import datetime

DEFAULT_TZ = ZoneInfo("Europe/Paris")

def to_local(dt: datetime | None, tz: ZoneInfo = DEFAULT_TZ) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        # SQLite roundtrip peut perdre tzinfo ; assume UTC
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(tz)

templates.env.filters["local"] = to_local
```

3. Templates : `{{ session.started_at | local | strftime('%d/%m %H:%M') }}` ou equivalent.

**Alternative :** exposer `local_started_at` calcule cote route et passer au template. Plus explicite.

### 3.4 Strategie V2 — preference utilisateur

**DIFFER V2.** Necessite :
- Column `users.timezone` VARCHAR(64) NULLABLE DEFAULT NULL
- UI dans /profile pour choisir (autocomplete des fuseaux IANA)
- Helper Jinja lit `user.timezone or DEFAULT_TZ`

**Pas dans Sb_06.** Peut etre ajoute plus tard sans refactor.

### 3.5 Edge cases

| Cas | Comportement |
|-----|--------------|
| `started_at` naive (SQLite roundtrip) | Helper assume UTC, convertit propre |
| Session a cheval sur minuit | Si debut 23:30 locale → stockage 22:30 UTC → rendu 23:30. Attribution jour OK. |
| Change d'heure ete/hiver | Aucun probleme (conversion Astronomique ZoneInfo) |
| User nomade qui change de fuseau | V1 : rendu fige sur Europe/Paris. V2 : preference user respecte. |

### 3.6 Surfaces a migrer

| Fichier | Lignes | Action |
|---------|--------|--------|
| `app/config.py` | n/a | Ajouter `DEFAULT_TIMEZONE = "Europe/Paris"` |
| `app/templating.py` | n/a | Ajouter filter `local` |
| `app/templates/session_detail.html` | 13 | Pipe `| local` |
| `app/templates/session_done.html` | 10, 12 | Pipe `| local` |
| `app/templates/history.html` | 37 | Pipe `| local` |
| `app/templates/admin_sessions.html` | a auditer | Pipe si rendu date |
| `app/templates/index.html` | active_session rendu | Pipe si applicable |
| `app/services/session_recap._duration_label` | `app/services/session_recap.py:17-28` | Deja gere timezone-aware proprement |
| Services qui calculent `now` pour windows (kpis, behavioral) | | **Pas de changement** : `datetime.now(timezone.utc)` reste correct pour les fenetres, seul le rendu change |

### 3.7 Question B02 : rendu weekday

`session.weekday_iso` et `WEEKDAY_LABELS` sont calcules en UTC aujourd'hui :

```python
@property
def weekday_iso(self) -> int:
    return self.started_at.isoweekday()
```

Une session commencee Dimanche 23:30 locale = Lundi 00:30 UTC → `weekday_iso = 1 (Lundi)` au lieu de Dimanche.

**Fix :** exposer `weekday_iso_local` qui applique la conversion timezone avant `isoweekday()`.

---

## 4. Ordre de fix au sein de Sb_06

### Etape 1 — Bugs transparents (pas de refactor)

1. **B01 decimales** : changer `type="number"` → `type="text" inputmode="decimal" pattern="..."` dans 4 endroits
2. Tests unit : `test_form_parsing.py` ajouter cas `"12,5"` et `"12.5"`
3. Commit isole `fix(b01): accept comma separator in weight inputs`

### Etape 2 — Timezone rendu

1. Ajouter `DEFAULT_TIMEZONE` dans `app/config.py`
2. Ajouter helper `local` dans `app/templating.py`
3. Mettre a jour 4-5 templates (filter pipe)
4. Tests integration : verifier que le rendu d'une session UTC-18:00 sur un browser Paris affiche 19:00 (hiver)
5. Commit isole `fix(b02): render session dates in Europe/Paris timezone`

### Etape 3 — Scoring dispatcher

1. Refactor `app/services/quality_score.py` :
   - Renommer ancien `compute_session_quality` → `compute_session_quality_strength`
   - Nouveau `compute_session_quality(session)` dispatcher
   - Nouveau `compute_session_quality_cardio(session)` avec 4 composants
2. Tests unit complets pour cardio (3-5 scenarios : LISS 25min parfait, LISS 10min, cardio sans bpm, cardio abs only, etc.)
3. Tests regression strength : les scores doivent etre identiques a avant
4. Verifier consumer integration (leaderboard, kpis) via tests existants
5. Commit `feat(b03): separate scoring for cardio vs strength sessions`

### Etape 4 — Helper text convention charge

1. Ajouter `<span class="set-row__hint">comme affiche</span>` sous les inputs weight_kg
2. CSS discret `font-size: 11px; color: var(--fg-dim)`
3. Commit `feat(c05): discrete helper on weight inputs`

### Etape 5 — Documentation

1. Mise a jour `docs/PRODUCT_SPEC.md` — section "Convention de saisie des charges"
2. Mise a jour page `/science` pour integrer la convention
3. Commit `docs: document canonical load convention`

### Etape 6 — Sprint report

`docs/SPRINT_Sb_06_REPORT.md` avec details, recette manuelle, resultats tests.

---

## 5. Tests a prevoir

### Tests unitaires nouveaux

| Fichier | Tests |
|---------|-------|
| `tests/test_scoring_cardio.py` (nouveau) | Formule cardio, tous composants, edge cases (null bpm, null duration, etc.) |
| `tests/test_form_parsing.py` (existe ?) | Ajout cas virgule, point, invalide, vide |
| `tests/test_timezone_rendering.py` (nouveau) | Helper `local` filter, edge cases midnight |

### Tests regression

| Fichier | Verification |
|---------|--------------|
| `tests/test_quality_score.py` | Scores strength inchanges (snapshot assertion) |
| `tests/test_leaderboard.py` | Consumers dispatcher transparent |
| `tests/test_kpis.py` | avg_success_score reste neutre sur cardio |
| `tests/test_session_flow.py` | Rendu dates OK |

### Recette manuelle

- [ ] Saisir `12,5` dans weight_kg → accepte
- [ ] Saisir `12.5` dans weight_kg → accepte
- [ ] Session completee a 19:00 local → rendu `19:00` dans `/sessions/{id}`, `/done`, `/history`
- [ ] Faire seance LISS 25min zone cible, valider feedback → score `/done` >= 80
- [ ] Verifier que seance strength recente garde le meme score qu'avant refactor

---

## 6. Risques et mitigation

| Risque | Probabilite | Mitigation |
|--------|------------|------------|
| Scores historiques changent visuellement apres Sb_06 | Moyen | Scores strength calcules a la volee, inchanges. Seuls les scores cardio remontent (amelioration visible) |
| Helper text surcharge UI mobile | Faible | Font 11px, pas de reserve d'espace, sur `var(--fg-dim)` discret |
| Users confondent convention "comme affiche" vs besoin de convertir | Moyen | Page `/science` dediee + helper inline + eventuel catalogue `load_semantics` V2 |
| Migration timezone tardive pour user nomade | Faible | V1 defaut Europe/Paris acceptable ; preference user en V2 |
| Bug tz aware/naive apres roundtrip SQLite | Moyen | Helper `local` gere le cas (assume UTC si naive) ; deja utilise dans session_recap._duration_label |
| Leaderboard recompute modifie ranks | Faible | quality_score cardio passera de ~60 a ~85-95 → user cardio regularement grimpe dans ranking ; comportement souhaite |

---

## 7. Impacts sur consumers non listes dans Sx_05

### 7.1 `feedback.compute_success_score`

Inchange. Consume exclusivement `reps`, `rep_targets`, `completed`. Non affecte par le dispatcher scoring.

### 7.2 `stats.summarise_current_exercise`

Inchange. Consume `set_logs` directement.

### 7.3 `delta.compute_delta`

Inchange.

### 7.4 Dashboards (`dashboard.py`, `muscle_scoring.py`)

Neutres — consument `actual_exercise_name` + sets, pas le quality_score directement.

### 7.5 Export

`export_builder.py` : ajouter `session_kind` (= `template.kind` ou `template_kind_snapshot` si cree) dans le payload JSON/CSV pour permettre analyse externe fine.

---

## 8. Acceptance criteria Sx_06

| Critere | Statut |
|---------|--------|
| Convention charge canonique definie unique et applicable | ✓ §1.2 |
| Alternatives ecartees documentees | ✓ §1.4 |
| Rappel UI discret specifie | ✓ §1.5 |
| Bug B01 cause + fix techniques explicite | ✓ §1.7 |
| Dispatcher strength/cardio specifie | ✓ §2.2 |
| Formule cardio V1 detaillee (4 composants + seuils) | ✓ §2.3 |
| Plafond effectif LISS bien fait >= 80 demontré | ✓ §2.4 |
| Impacts consumers scoring matrices | ✓ §2.6 |
| Strategie timezone V1 + V2 | ✓ §3 |
| Edge cases timezone | ✓ §3.5 |
| Surfaces a migrer listees (fichiers + lignes) | ✓ §§1.7, 2.6, 3.6 |
| Ordre de fix au sein de Sb_06 | ✓ §4 |
| Tests prevus (unit + regression + recette) | ✓ §5 |
| Risques + mitigation | ✓ §6 |

---

## 9. Ouvertures pour Sx_07 et Sx_08

### Pour Sx_07 (Machine Atlas + Substitution UX)

- Le champ `load_semantics` proposes en §1.6 est **differe**. Si Sx_07 decide de structurer le catalogue avec machine family, cela peut etre une occasion de l'ajouter en meme temps (DIFFER mais couple possible).
- Le helper text `"comme affiche"` peut etre enrichi plus tard via info contextuelle de l'atlas machine ("Chest Press machine : charge totale" dynamique).

### Pour Sx_08 (Session Review Intelligence)

- La formule cardio v1 peut generer des donnees utiles pour la couche I04 (confidence score) : un LISS sans duration ni bpm logues aura un score de confiance faible.
- La separation kind-based permet a la couche I01 (incoherences) de specialiser ses regles selon le type de seance (les incoherences de progression de reps n'ont de sens qu'en strength).

---

## 10. Synthese executive

- **Convention charge canonique** : "comme affiche sur l'equipement" — simple, applicable, documentee
- **B01 decimales** : fix HTML `type="text" inputmode="decimal" pattern` — zero regression backend
- **B02 timezone** : stockage UTC conserve, rendu converti Europe/Paris via helper Jinja
- **B03 scoring LISS** : dispatcher par `template.kind` + formule cardio 4 composants — LISS 20min zone cible >= 85/100
- **5 etapes** de fix Sb_06 ordonnees, chacune committable isolement
- **Zero migration DB** (V1). Migration additive possible V2 pour `template_kind_snapshot` et `users.timezone`
- **Prochain sprint recommande** : Sx_07 (Machine Atlas + Substitution UX) et Sx_08 (Session Review) en parallele apres validation humaine Sx_06

Pret pour Sb_06 apres OK humain.
