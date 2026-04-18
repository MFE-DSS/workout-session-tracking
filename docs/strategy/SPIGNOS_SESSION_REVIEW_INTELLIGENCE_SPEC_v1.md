# SPIGNOS Session Review Intelligence Spec v1

**Sprint:** Sx_08_session_review_intelligence_spec
**Date:** 2026-04-15
**Status:** Spec detaillee (SPEC ONLY)
**Prerequisite:** Sx_05 + Sx_06 valides ; Sx_07 recommande
**Parallelisable avec:** Sx_07 (Machine Atlas + Substitution UX)
**Debloque:** Sb_08 (Session Review + Anomaly Hints build)

---

## 0. Objet

Specifier la couche **Session Review Intelligence** — une synthese post-seance enrichie et quelques detections deterministes d'incoherences. Le but est de **reduire la saisie libre** pendant la seance et de **deporter la valeur vers une cloture intelligente**, sans promettre de l'IA.

Livrables :

1. **Structure rapport final enrichi** dans `/done` (etend Sb_R3)
2. **3-5 regles deterministes I01** (incoherences intra-exercice)
3. **Mecanique hints I03** (carte active) — V1 minimal
4. **Score de confiance I04** — qualite du logging
5. **Reduction notes inline C03** + **synthese finale simplifiee C06**

---

## 1. Principes directeurs

Reaffirme Sx_05 + specifiques Sx_08 :

| Principe | Application |
|----------|-------------|
| **Deterministe, pas predictif** | Aucun ML, aucun LLM. Regles basees sur seuils et comparaisons |
| **Wording neutre** | "A verifier" plutot que "Tu as triche". Pas de ton accusatoire |
| **Non bloquant** | Aucune alerte bloque le flow. Tout est affichage informatif |
| **Explicable** | Chaque hint/alert doit exposer sa logique si l'user demande |
| **Ne pas sur-ingenierer** | V1 = 5 regles max. Ne pas construire un framework d'inference complet |
| **Donnees avant user input** | Preferer inferer d'une donnee existante que demander a l'user |

---

## 2. Rapport final enrichi dans `/done`

### 2.1 Etat actuel (Sb_R3)

`session_recap.build_recap(session)` produit un dict `{header, summary, exercises}` avec :
- Header : template_name, started_at, ended_at, duration_label, kind
- Summary : work_sets_done/total, completion_pct, substitution_count, bodyweight_kg, concentration, global_state, cardio
- Exercises : liste d'objets `{code, name, substituted_name, done, total, score, weights_str, reps_str}`

### 2.2 Extensions proposees

Nouveaux blocs calcules dans `session_recap.py` et rendus dans `session_done.html` :

#### A. Bloc "Top progression" (nouveau)

**Objectif :** mettre en valeur le meilleur signal de progression vs derniere fois.

**Logique :**
- Pour chaque session_exercise qui a un delta (voir `delta.compute_delta`), collecter `(exercise_name, delta)`
- Selectionner le delta avec le **weight_delta** le plus positif (ou reps_delta le plus positif si pas de weight_delta)
- Si aucun delta positif : afficher "Rien de significatif" ou omettre le bloc
- Afficher le top en card dedie dans `/done`

**Exemple rendu :**
```
Top progression
E2 Chest Press machine · +2.5 kg · +1 rep · score en hausse
```

**Signal :** le user comprend d'un coup d'oeil ce qui a le mieux marche.

#### B. Bloc "Zones touchees" (nouveau)

**Objectif :** afficher les zones musculaires reellement sollicitees (via `actual_exercise_name` + `muscle_scoring.classify_exercise`).

**Logique :**
- Pour chaque session_exercise, recuperer `actual_exercise_name(se)` → zone primaire + secondaires
- Compter les **hard sets** (work sets completed) par zone primaire
- Afficher le top 3-5 zones avec count

**Exemple rendu :**
```
Zones sollicitees
Pectoraux · 9 sets
Deltoides lateraux · 4 sets
Triceps · 3 sets
```

#### C. Bloc "A verifier" (nouveau — conditionnel)

**Objectif :** lister les anomalies deterministes detectees (0-N items).

**Logique :** appel a `compute_anomalies(session)` qui retourne liste de `{exercise_code, severity, message}`. Si liste vide, bloc non rendu.

**Regles appliquees (voir §3).**

**Exemple rendu :**
```
A verifier
⚠ E2 Chest Press machine · Set 3 marque fait sans reps ni charge saisis
⚠ E5 Elevations · Charge et reps augmentent simultanement en fin d'exercice
```

#### D. Confidence badge (nouveau — discret)

**Objectif :** afficher un score de confiance du logging (§5).

**Position :** dans le header, a cote du grade ou du completion_pct, discret.

**Exemple rendu :**
```
Resume
Work sets : 18/20 (90%) · Confiance logging : eleve
```

Ou format badge :
```
Confiance : eleve (92)
```

### 2.3 Structure recap v2 (apres Sb_08)

```python
{
  "header": {...},          # inchange
  "summary": {               # etendu
    ...,                    # existant
    "confidence_score": 92,
    "confidence_level": "eleve",  # eleve / moyen / faible
    "top_progression": {...} or None,
    "zones_touched": [...],  # liste ordonnee
    "anomalies": [...],      # 0-N items
  },
  "exercises": [...],        # inchange
}
```

---

## 3. Regles d'anomalies deterministes (I01)

### 3.1 Scope V1

**5 regles maximum** pour V1. Toutes deterministes, toutes chiffrees.

### 3.2 Regle 1 — Set marque "fait" sans donnees saisies

**Condition :** un set avec `completed=True` **et** `weight_kg is None` **et** `reps is None`.

**Pourquoi :** incoherent sauf rare cas (exercice poids du corps non leste sans compter les reps). En pratique, indique que le user a tape "Fait" sans saisir.

**Severite :** info (non bloquante).

**Message :** `"Set #{set_index} marque fait sans reps ni charge saisis"`.

### 3.3 Regle 2 — Charge et reps croissent simultanement en fin d'exercice

**Condition :** pour un exercice donne, comparer le dernier work set complete vs le premier :
- `last.weight_kg > first.weight_kg` **AND**
- `last.reps > first.reps`

**Pourquoi :** surcharge progressive typique = soit charge augmente (reps diminuent souvent), soit reps augmentent (charge fixe). Les deux a la fois en fin d'exercice est rare et suggere soit une erreur de saisie soit une montee anormale de performance.

**Severite :** info.

**Message :** `"Charge et reps croissent simultanement (set 1: {X} kg x {Y} → set {N}: {X'} kg x {Y'}). A verifier."`

### 3.4 Regle 3 — Delta weight extreme vs derniere fois

**Condition :** pour un exercice avec delta vs derniere fois :
- `abs(weight_delta / prior_weight) > 0.30` (30% de variation)

**Pourquoi :** un saut de charge > 30% est rare sans contexte (nouveau programme, retour de blessure). A flagger pour confirmer.

**Severite :** info.

**Message :** `"E{code} : {±X%} de charge vs derniere fois. Volontaire ?"`

### 3.5 Regle 4 — Exercice "done" mais seulement warmup realise

**Condition :** un `session_exercise` ou tous les work sets sont `completed=False` **mais** certains warmups sont `completed=True`.

**Pourquoi :** suggere un abandon d'exercice apres echauffement. Pas une erreur, mais une info utile pour le rapport.

**Severite :** info.

**Message :** `"E{code} : echauffement fait, aucun work set realise"`.

### 3.6 Regle 5 — success_score stricte vs reps

**Condition :** `session_exercise.success_score >= 80` (derive) **mais** tous les work sets ont `reps < min_reps` (sous-cible).

**Pourquoi :** incoherence logique — le derive `compute_success_score` devrait calibrer cela, mais si bug ou donnee manquante, detection utile.

**Severite :** info.

**Message :** `"E{code} : score eleve mais reps sous la cible, a verifier."`

**Note :** cette regle teste la coherence du score derive avec les donnees brutes. Si jamais la derivation evolue (V2), cette regle peut devenir redondante.

### 3.7 Strategie d'ajout de regles futures

- 5 regles V1 = cap dur
- Regle additionnelle doit justifier sa valeur versus le bruit produit
- Chaque regle doit etre testable isolement (tests unit pour `compute_anomalies`)
- Un flag de "severity" pourra etre introduit plus tard si besoin (info / warning)

---

## 4. Hints contextuels I03 (carte active)

### 4.1 Scope V1

**Uniquement sur la carte exercice active** (au moment du logging, pas post-seance).

**Objectif :** suggerer discretement un ajustement base sur l'historique de l'exercice et les donnees saisies en cours.

### 4.2 Regles hints V1

**Limit V1 : 2 hints max.**

#### Hint A — Charge augmentee vs derniere fois

**Condition :** le user a saisi un weight sur le 1er work set `> prior_weight_first_set × 1.10`.

**Message :** `"+{X}% de charge vs derniere fois — prudence sur l'execution"`.

**Position UI :** affichage juste sous le bloc delta dans la carte active.

#### Hint B — Reps reduites sur set N

**Condition :** au cours du logging, si un set intermediaire a `reps < prior_same_set.reps - 2`.

**Message :** `"Set {N} : reps reduites vs derniere fois — fatigue installee ?"`.

**Position UI :** sous la set-row concernee, rendu conditionnel.

### 4.3 Non-objectifs V1

- Pas de hint sur muscle_sensation
- Pas de hint sur rythme de saisie
- Pas de hint qui necessite une lecture cross-exercise
- Pas de hint avec action bouton "Appliquer" (suggestion passive seulement)

### 4.4 Implementation

Nouveau service `app/services/hints.py` :

```python
"""Deterministic contextual hints for the active exercise card.

V1: 2 rules max, displayed alongside the card content. No action
required from the user.
"""

def compute_hints(session_exercise, prior_occurrence) -> list[dict]:
    """Return a list of {code, message} hints for display.

    Rules:
    A. Load increased >10% vs prior first completed set
    B. Reps dropped on a set vs same set index in prior occurrence
    """
    hints = []
    # ... regles
    return hints
```

### 4.5 Rendu template

Ajout dans `session_detail.html` bloc 6bis (apres delta, avant set lists) :

```html
{% set hints = hints_by_exercise.get(se.id, []) %}
{% if hints %}
<div class="exercise-card__hints">
  {% for hint in hints %}
  <p class="hint hint--{{ hint.code }}">
    <span class="hint__icon">💡</span>
    {{ hint.message }}
  </p>
  {% endfor %}
</div>
{% endif %}
```

**Style :** discret, couleur `--accent` sur fond leger, pas d'icone bruyante.

---

## 5. Score de confiance du logging (I04)

### 5.1 Objectif

Score 0-100 qui jauge la **qualite du logging de la seance** (pas la performance), pour :
- Informer l'user qu'une seance incomplete est "moins fiable" analytiquement
- Permettre aux analytics futures de ponderer les valeurs (degrade les cas douteux)

### 5.2 Formule V1

```python
def compute_confidence_score(session) -> int:
    """Return 0..100 logging confidence."""
    points = 0
    max_points = 0

    # 1. Work sets renseignes
    total_work = count_work_sets(session)
    renseignes = count_work_sets_with_data(session)  # weight OR reps
    if total_work > 0:
        points += (renseignes / total_work) * 40
        max_points += 40

    # 2. Completed flag coherent
    completed_sans_donnees = count_completed_without_data(session)
    if total_work > 0:
        penalty = (completed_sans_donnees / total_work) * 15
        points += max(0, 15 - penalty)
        max_points += 15

    # 3. Feedback session
    if session.concentration:
        points += 10
    max_points += 10
    if session.global_state:
        points += 10
    max_points += 10

    # 4. Pas d'anomalies critiques
    anomalies = compute_anomalies(session)
    if len(anomalies) == 0:
        points += 15
    elif len(anomalies) <= 2:
        points += 10
    elif len(anomalies) <= 4:
        points += 5
    # >4 = 0 point
    max_points += 15

    # 5. Bodyweight renseigne (bonus)
    if session.bodyweight_kg:
        points += 10
    max_points += 10

    return round((points / max_points) * 100) if max_points > 0 else 0
```

### 5.3 Niveaux

| Score | Niveau | Affichage |
|-------|--------|-----------|
| 80-100 | eleve | `Confiance : eleve` (badge --ok) |
| 50-79 | moyen | `Confiance : moyen` (badge --warn) |
| 0-49 | faible | `Confiance : faible` (badge --danger discret) |

### 5.4 Surface

- **`/done`** : badge dans le bloc summary
- **Future analytics** : les timelines et dashboards peuvent choisir de degrader l'opacite / mettre un marker sur les sessions a faible confiance (Sb_09)

---

## 6. Reduction notes inline (C03) + synthese finale simplifiee (C06)

### 6.1 Diagnostic actuel

Note libre par exercice (`session_exercises.free_note` max 140 chars) : visible en textarea dans le body de la carte. Taux de remplissage terrain : tres faible.

Note session (`workout_sessions.free_note` max 280 chars) : visible en textarea dans le feedback session. Mieux utilisee.

### 6.2 Arbitrage Sx_08

**Regle :**
- **Note exercice** : deplacee dans un `<details>` optionnel au bas du body, label "Note (optionnel)" → collapsed par defaut
- **Note session** : reste dans le feedback session (post-seance naturelle)

**Impact templates :**

```html
<!-- session_detail.html : note exercice -->
<details class="exercise-card__note">
  <summary>Note (optionnel)</summary>
  <textarea name="free_note" maxlength="140" rows="1">{{ se.free_note or '' }}</textarea>
</details>
```

### 6.3 Synthese finale simplifiee (C06)

**Objectif :** la page `/done` devient la surface principale de reflexion post-seance, remplaceant la bureaucratie des notes inline.

**Contenu final de `/done` apres Sb_08 :**

```
✓ Seance terminee — Push A
Lun 15/04 18:45 → 20:02 · 1h 17m

Resume
• Work sets : 18/20 (90%)
• Bodyweight : 78,5 kg
• Concentration : high · Etat : good
• Confiance logging : eleve (92)

Top progression
E2 Chest Press machine · +2.5 kg · +1 rep · score en hausse

Zones sollicitees
Pectoraux · 9 sets
Deltoides lateraux · 4 sets
Triceps · 3 sets

[A verifier]                       ← conditionnel
⚠ E5 : Charge et reps croissent simultanement

Par exercice (details) ...

Note finale (optionnel)
[ textarea ]

[Voir la synthese →]  [Historique →]
[Rouvrir pour editer]
```

### 6.4 Ne pas ajouter

- Pas de graphique dans `/done` V1
- Pas de resume auto-narre en langage naturel ("Tu as bien progresse aujourd'hui...")
- Pas de coaching tone
- Pas de partage social ajouter (existant sharing.py reste)

---

## 7. Structures donnees nouvelles

### 7.1 Anomaly

```python
@dataclass
class Anomaly:
    exercise_code: str | None  # None si session-level
    rule_code: str             # "A", "B", "C", "D", "E"
    severity: str              # "info" uniquement V1
    message: str
    context: dict              # {set_index, prior_weight, etc.}
```

### 7.2 Hint

```python
@dataclass
class Hint:
    rule_code: str             # "A", "B" V1
    message: str
    context: dict
```

### 7.3 RecapSummary etendu

Dans `app/services/session_recap.py` le dict `summary` gagne :
- `confidence_score: int`
- `confidence_level: str`
- `top_progression: dict | None`
- `zones_touched: list[dict]`
- `anomalies: list[Anomaly]`

---

## 8. Services a creer / modifier

| Service | Action |
|---------|--------|
| `app/services/anomalies.py` | **Nouveau** — `compute_anomalies(session) -> list[Anomaly]` avec 5 regles V1 |
| `app/services/hints.py` | **Nouveau** — `compute_hints(se, prior) -> list[Hint]` avec 2 regles V1 |
| `app/services/confidence.py` | **Nouveau** — `compute_confidence_score(session) -> int` |
| `app/services/session_recap.py` | Extend — `build_recap` inclut confidence, top_progression, zones_touched, anomalies |
| `app/services/stats.py` | Reutilise — fournit deja `summarise_current_exercise` |
| `app/routers/sessions.py` | Modify — charger hints pour la carte active |
| `app/templates/session_detail.html` | Modify — rendu hints, note en `<details>` |
| `app/templates/session_done.html` | Modify — rendu blocs top_progression, zones, anomalies, confidence |

---

## 9. Tests prevus

### Unit

- `tests/test_anomalies.py` (nouveau) : 5 regles × plusieurs cas (declenche / ne declenche pas)
- `tests/test_hints.py` (nouveau) : 2 regles × cas
- `tests/test_confidence.py` (nouveau) : formule, bornes, edge cases
- `tests/test_session_recap.py` extend : nouveaux blocs

### Integration

- `tests/test_session_done.py` extend : rendu top_progression, zones, anomalies si presentes
- `tests/test_session_flow.py` extend : hints affiches sur carte active

### Regression

- Tests Sb_R3 existants inchanges (compat retro build_recap)
- Full suite green

---

## 10. Risques

| Risque | Probabilite | Mitigation |
|--------|------------|------------|
| Regles anomalies trop bruyantes (false positives) | Moyen | Seuils conservateurs V1 (ex: 30% weight delta, pas 20%) ; iterer sur feedback |
| Confidence score mal interprete par user ("je suis puni") | Moyen | Wording neutre ("confiance du logging") + doc page /science |
| Hints dans carte active surchargent visuellement | Moyen | Max 2 hints V1, style discret `--accent` |
| Synthese /done trop longue sur mobile | Faible | Blocs collapsibles via `<details>` si besoin ; prioriser completion_pct + top_progression |
| Regle 5 (success vs reps) devient redondante avec Sx_01 derive | Faible | Acceptable ; peut etre retiree si mainenance montre qu'elle ne declenche jamais |

---

## 11. Acceptance criteria Sx_08

| Critere | Statut |
|---------|--------|
| Structure rapport /done enrichi definie | ✓ §2 |
| 5 regles anomalies specifiees chiffrees + messages | ✓ §3 |
| 2 regles hints V1 specifiees | ✓ §4 |
| Formule confidence score documentee | ✓ §5 |
| Reduction notes inline + synthese finale arbitree | ✓ §6 |
| Structures de donnees (Anomaly, Hint) | ✓ §7 |
| Services a creer identifies | ✓ §8 |
| Tests prevus (unit + integration + regression) | ✓ §9 |
| Risques + mitigation | ✓ §10 |
| Wording neutre garanti (pas de ton accusatoire) | ✓ (§3, §5) |
| Zero JS, zero migration | ✓ |

---

## 12. Livrables Sb_08 attendus

| Fichier | Action |
|---------|--------|
| `app/services/anomalies.py` | **New** — 5 regles + `compute_anomalies` |
| `app/services/hints.py` | **New** — 2 regles + `compute_hints` |
| `app/services/confidence.py` | **New** — `compute_confidence_score` |
| `app/services/session_recap.py` | Modify — enrichir `summary` |
| `app/routers/sessions.py` | Modify — hints per exercise |
| `app/templates/session_detail.html` | Modify — hints rendus, note en `<details>` |
| `app/templates/session_done.html` | Modify — blocs top / zones / anomalies / confidence |
| `app/static/css/app.css` | Modify — styles hints, blocs recap, badge confidence |
| `tests/test_anomalies.py` | **New** |
| `tests/test_hints.py` | **New** |
| `tests/test_confidence.py` | **New** |
| `tests/test_session_recap.py` | Extend |
| `tests/test_session_done.py` | Extend |

**Effort estime Sb_08 : 4-6h.**

---

## 13. Ouvertures Sx_09 et futurs

### 13.1 Lien avec Sx_07 (Atlas Machine)

Les `zones_touched` peuvent etre enrichies avec le `machine_family` si l'atlas est deploye — affichage type "Pectoraux — Developpe : 6 sets (Chest Press, Dev. couche)".

### 13.2 Future analytics pattern-aware (I05)

Les regles d'anomalie peuvent se specialiser sur motor_pattern (push vs pull vs squat) une fois la taxonomie deployee (Option 2 canonical Sx_03). Differe.

### 13.3 Graphe progression long-terme

Top progression V1 regarde 1 occurrence precedente. V2 pourra afficher des tendances sur 3-5 occurrences.

### 13.4 Rapport narratif auto-genere (I02)

**Explicitement defere.** Un rapport en langage naturel ("Tu as bien progresse aujourd'hui, continue...") sort du scope deterministe. Si besoin emerge, requiert LLM → decision produit dediee.

---

## 14. Synthese executive

- Rapport `/done` enrichi avec 4 nouveaux blocs : top progression, zones sollicitees, anomalies, confidence
- 5 regles anomalies deterministes V1 (incoherences set-level et exercise-level)
- 2 hints contextuels V1 sur carte active (charge +10%, reps reduites)
- Score de confiance logging 0-100 base sur 5 composants
- Note exercice reduite en `<details>` ; synthese finale devient le point de reflexion post-seance
- 3 nouveaux services + 5 fichiers modifies ; zero migration, zero JS
- Effort Sb_08 estime 4-6h
- Wording neutre garanti ; aucun ton accusatoire ou predictif
