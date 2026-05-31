# SPIGNOS — Implicit Signal Scoring + Checkbox Deprecation Spec (Sx_24)

**Date :** 2026-05-31
**Type :** SPEC ONLY — modèle de signal + scoring qualité V2.
**Prérequis :** Sb_22a.next2 livré (atlas suit le réalisé).
**Successeur build :** Sb_24 (build complet en plusieurs lots).

---

## A. Pourquoi cette spec

Deux retours dogfooding convergent vers la même classe de problème : **le système traite les set_logs au niveau le plus naïf possible** (`completed` est une coche utilisateur, le scoring qualité est purement déclaratif).

| Retour | Manifestation | Cause systémique |
|---|---|---|
| N9 | Checkbox "fait" inutile — ajoute des clics sans signal | UX dérive de la BD : on a stocké un booléen explicite parce que la BD voulait un état, alors qu'il est dérivable des données saisies |
| N10 | Scoring qualité repose sur "j'ai été concentré" / sensation musculaire — ignore les patterns objectifs présents dans les set_logs | Pas de couche d'analyse implicite. Les données existent (weight, reps par set), elles ne sont juste pas relues sous l'angle de l'effort réel |

Sx_24 répond aux deux d'un coup en posant un **modèle de signal à 3 couches** (`saisi` / `dérivé` / `implicite`) avec contrat fort sur la **stabilité historique** : aucune session passée ne voit son scoring recalculé.

## B. État actuel — audit chiffré

### B.1 — Modèle `set_logs` actuel

```python
class SetLog:
    kind: str              # "warmup" | "work"
    set_index: int         # 1..N par exercice × kind
    weight_kg: float | None
    reps: int | None
    rir: int | None        # optionnel
    completed: bool        # ← saisi via checkbox "fait" dans la carte
```

**Constat** : `completed` est sémantiquement **redondant** avec `(weight_kg is not None or reps is not None)`. Audit sur la prod : aucune session connue avec `weight=NULL AND reps=NULL AND completed=True`, et aucune avec `weight≠NULL AND completed=False` (cas qui aurait pu exister pour "skip avec valeurs entrées par erreur").

### B.2 — Modèle de scoring actuel (`services/quality_score.py`)

Score 0-100 calculé à partir de :
- complétion (ratio `completed_work_sets / total_work_sets`)
- concentration (saisi)
- sensation musculaire moyenne (saisie par exercice)
- (cardio uniquement) durée + zone FC

**100 % des signaux non-cardio sont déclaratifs.** Les données implicites présentes dans les set_logs (trajectoire weight/reps, drop-off, distribution intra-exo) ne sont pas exploitées.

### B.3 — Volume données disponibles non exploité

Sur une session strength typique (~30 set_logs) :
- 30 × (weight_kg, reps) saisis
- Aucun de ces 30 datapoints ne contribue au score qualité au-delà du compte de complétion

## C. Modèle de signal à 3 couches (contrat dur)

Chaque champ exposé dans l'UI ou utilisé dans le scoring porte un **type de signal** explicite. Le vocabulaire est aligné sur le triptyque Sx_21 (généralisation) + Sx_23 (Coach Report).

| Type | Définition | Exemples actuels | Calcul retroactif autorisé ? |
|---|---|---|---|
| **Saisi** | Valeur fournie directement par l'utilisateur ou par un capteur externe | weight_kg, reps, rir, muscle_sensation, concentration, bodyweight_kg | ❌ jamais — l'historique est intangible |
| **Dérivé** | Valeur calculée déterministiquement par agrégation simple de signaux Saisis | sessions_30d, top_zone, sets_per_week, completed_work_sets | ✅ libre — c'est juste une projection des Saisis |
| **Implicite** | Valeur **estimée** par une **règle d'inférence** documentée, qui exprime une **hypothèse d'effort/intent** | (NEW) intra_set_trajectory_label, reserve_detected, pyramidal_pattern | **⚠️ jamais sur l'historique** (Q4) — seulement à partir des sessions postérieures à Sb_24 |

**Règle de stockage** : tout signal Implicite est **persisté** au moment où la session est marquée `completed` (transition vers fin de séance). On ne le recalcule jamais — ni sur consultation, ni sur changement de règles. Une session passée garde ses labels Implicites figés tels qu'ils étaient au moment de la complétion.

**Conséquence** : si on raffine les règles d'inférence en Sb_24.next, les anciennes sessions gardent leurs anciens labels. C'est explicite et conforme à Q4.

## D. Règles implicites V1.1 — intra-exercice

Périmètre Q2 : V1.1 = **intra-exercice uniquement**. Pas d'inférence cross-exercices, pas de cross-sessions. Une règle prend en entrée la liste ordonnée des **work sets** d'un seul SessionExercise.

### D.1 — Trajectoires détectables

Soit `sets = [(w1, r1), (w2, r2), ..., (wN, rN)]` les work sets complétés d'un exercice, ordonnés par `set_index`. On exige `N ≥ 3` pour qu'une règle se déclenche (en deçà, signal trop pauvre).

| Label | Condition | Interprétation |
|---|---|---|
| `reserve_probable` | (`w` constant OU croissant) ET (`r` constant OU croissant) sur tous les sets | L'effort ne descend pas alors qu'il devrait. Probabilité que l'utilisateur ait gardé de la réserve sur les premiers sets |
| `trajectoire_coherente` | `w` constant et `r` décroissant (au moins -1 entre set 1 et set N) | Drop-off attendu en hypertrophie — bon signal d'effort |
| `pyramidal_ascendant` | `w` strictement croissant sur tous les sets ET `r` (constant OU décroissant) | Pattern de ramp / pyramide. Cohérent avec un échauffement progressif ou une stratégie de force |
| `pyramidal_descendant` | `w` strictement décroissant ET `r` (constant OU croissant) | Drop-set ou stratégie de fatigue maximale |
| `incoherent` | Aucun pattern net (oscillations sans direction) | Soit erreur de saisie, soit séance perturbée |
| (non labellé) | < 3 work sets ou pattern non classable | Pas d'inférence — silencieux |

**Algorithme** (pseudo) :

```
def detect_intra_set_label(work_sets):
    N = len(work_sets)
    if N < 3:
        return None
    ws = [s.weight_kg or 0 for s in work_sets]
    rs = [s.reps or 0 for s in work_sets]
    w_inc_or_eq = all(ws[i+1] >= ws[i] for i in range(N-1))
    r_inc_or_eq = all(rs[i+1] >= rs[i] for i in range(N-1))
    w_strict_inc = all(ws[i+1] > ws[i] for i in range(N-1))
    w_strict_dec = all(ws[i+1] < ws[i] for i in range(N-1))
    r_const = all(rs[i] == rs[0] for i in range(N))
    r_dec = rs[-1] < rs[0]
    
    if w_inc_or_eq and r_inc_or_eq:
        return "reserve_probable"
    if w_strict_inc and (r_const or r_dec):
        return "pyramidal_ascendant"
    if w_strict_dec and (r_const or rs[-1] > rs[0]):
        return "pyramidal_descendant"
    if all(w == ws[0] for w in ws) and r_dec:
        return "trajectoire_coherente"
    return "incoherent"
```

### D.2 — Données nécessaires pour stocker

Ajout d'une colonne sur `session_exercises` :

```python
implicit_label: Mapped[str | None] = mapped_column(String(32), nullable=True)
implicit_label_computed_at: Mapped[datetime | None] = mapped_column(...)
```

Renseignée au moment du **passage de la session en `status="completed"`** — jamais touchée après.

## E. Dépréciation de la checkbox "fait"

### E.1 — Nouvelle sémantique

Pour les **nouvelles** lignes `set_logs` (créées après le déploiement de Sb_24) :

```
completed = (weight_kg is not None) OR (reps is not None)
```

Calculé **côté serveur au moment du POST** (handler `/sessions/{id}/exercise/{xid}`). L'UI ne propose plus de checkbox.

Pour les **anciennes** lignes (créées avant Sb_24) : la valeur `completed` qu'elles portent en BD est **figée** et utilisée telle quelle. Aucune migration.

### E.2 — Mécanisme de gating

Ajout d'une colonne discriminante sur `workout_sessions` :

```python
scoring_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
```

- `scoring_version=1` : sessions historiques (déclaratif pur, `completed` saisi).
- `scoring_version=2` : sessions créées après Sb_24 (déclaratif + Implicite, `completed` dérivé).

Au calcul du `quality_score`, on branche selon la version. Pas d'`ALTER TABLE` rétroactif sur les valeurs.

### E.3 — Cas limite documenté (Q3)

Sans checkbox, l'utilisateur ne peut plus distinguer **skip volontaire** vs **oubli de saisie**. V1.1 fusionne les deux : `weight=NULL AND reps=NULL → completed=False`, sans label de cause. Documenté §J.

Cas warmup : si juste `reps` saisi (pas de poids = bodyweight) → `completed=True`. Cohérent.

## F. Intégration dans le scoring qualité

### F.1 — Formule actuelle (résumé)

```
quality_score_v1 = w_completion * completion_ratio
                 + w_concentration * concentration_score
                 + w_sensation * sensation_avg
                 + (cardio extras)
```

### F.2 — Formule V2 (Sb_24)

```
quality_score_v2 = w_completion * completion_ratio
                 + w_concentration * concentration_score
                 + w_sensation * sensation_avg
                 + w_implicit * implicit_score
                 + (cardio extras)
```

Avec `implicit_score` calculé comme la **moyenne** des contributions par exercice :

| `implicit_label` | Contribution per-exercise (sur 100) |
|---|---|
| `reserve_probable` | 30 — signal négatif modéré |
| `incoherent` | 50 — neutre |
| `pyramidal_ascendant` | 70 |
| `pyramidal_descendant` | 75 |
| `trajectoire_coherente` | 90 |
| `None` (< 3 sets, non labellé) | exclu du calcul de moyenne |

Pondération proposée V1.1 :
- `w_completion = 0.35` (inchangé)
- `w_concentration = 0.15`
- `w_sensation = 0.15`
- `w_implicit = 0.25` (NEW)
- (cardio) reste à part

Total = 0.90 sur la partie strength (10 pts de marge pour ajustements). Tunable en Sb_24.

### F.3 — Garde-fou — pas d'impact rétroactif

Le `quality_score` est calculé à chaque consultation (pas stocké). Mais la **fonction** branche selon `workout_sessions.scoring_version` :

```python
def compute_session_quality(session):
    if session.scoring_version == 1:
        return _compute_v1(session)
    return _compute_v2(session)
```

Une session avec `scoring_version=1` continuera **éternellement** à utiliser la formule V1 — peu importe les évolutions futures. L'utilisateur ne voit jamais son score historique bouger.

## G. Surfaces UI — où les labels apparaissent (Q1=C, sober)

| Surface | Affichage du label Implicite ? |
|---|---|
| `/sessions/{id}` carte active (en cours) | ❌ — pas de verdict intrusif pendant la séance (Q1) |
| `/sessions/{id}/done` page review | ✅ — pastille discrète par exercice + score global ventilé |
| `/coach-report` (Sb_23) | ✅ — agrégat des labels sur 30j (% de sessions avec `reserve_probable`, etc.), tagué `Inféré` |
| Hints panel (Sb_08) | ✅ — peut surfacer "Sur les 3 dernières fois, tu as eu une trajectoire cohérente" comme renforcement éducatif |
| Leaderboard / profil public | ❌ — pas de divulgation publique de signaux d'effort (privacy + risque d'interprétation) |
| Historique liste séances | ❌ — V1 minimal, ajout V1.2 possible |

**Style visuel** : pastilles courtes ASCII-style sans icônes anxiogènes. Exemple wireframe page review :

```
┌──────────────────────────────────────────────┐
│  Push A — Pecs épaisseur + Delts + Triceps   │
│  Score : 76/100                              │
│  ──────────────────────────────────────────  │
│  E1 Incline Smith Press                      │
│      3×8 → 80kg×10, 80kg×8, 80kg×6           │
│      ✓ trajectoire cohérente                 │
│  E2 Chest Press machine                      │
│      3×12 → 60kg×12, 60kg×12, 60kg×12        │
│      ! réserve probable                      │
│  E3 ...                                      │
└──────────────────────────────────────────────┘
```

## H. Backward compat — contrat de stabilité historique

| Élément | Comportement Q4 |
|---|---|
| `set_logs.completed` historiques | **Figés** — valeur explicite saisie au moment T0 reste en BD |
| `set_logs.completed` nouveaux | **Dérivés** — calculés au POST, non saisis |
| `quality_score` d'une session historique | **Stable** — formule V1 utilisée éternellement pour `scoring_version=1` |
| `quality_score` d'une nouvelle session | Formule V2 (Implicite intégré) |
| `implicit_label` sur session historique | **NULL** — pas de backfill |
| `implicit_label` sur nouvelle session | Calculé à la complétion, **figé** |

Pas de migration `UPDATE` sur des champs existants. Uniquement des `ALTER TABLE ... ADD COLUMN ... DEFAULT ... NULL`. La spec §K.1 détaille la migration Alembic.

## I. Acceptance criteria Sx_24

| Critère | Mesure |
|---|---|
| Triptyque signal verrouillé | Spec §C contractualisée, code annoté `# Saisi` / `# Dérivé` / `# Implicite` sur chaque sortie publique |
| Checkbox "fait" disparaît de l'UI | Aucune occurrence `<input type="checkbox" name="completed">` après Sb_24.4 |
| `completed` dérivé côté serveur | Tests unitaires : POST set sans weight/reps → completed=False ; avec weight → True ; avec reps → True |
| Sessions historiques inchangées | Test : `compute_session_quality(session_v1)` retourne exactement la valeur stockée pré-Sb_24 |
| Sessions V2 utilisent la formule étendue | Test : `compute_session_quality(session_v2)` intègre `implicit_score` |
| Labels Implicites calculés à la complétion | Test : POST `/sessions/{id}/finish` → row reçoit son `implicit_label` non-null si ≥ 3 sets |
| Labels figés post-complétion | Test : recalcul de fonction de détection avec règles modifiées ne change pas le label en BD |
| 5 labels détectables documentés | reserve_probable / trajectoire_coherente / pyramidal_ascendant / pyramidal_descendant / incoherent + tests |
| Surface review affiche les labels | Test E2E sur `/sessions/{id}/done` |
| Coach Report agrège les labels 30j | `services/coach_report.py` étend `discipline` ou ajoute un bloc `implicit_signals` taggé `Inféré` |

## J. Limites assumées

1. **Pas de distinction skip volontaire vs oubli** — fusion documentée §E.3. Si le besoin émerge (utilisateurs blessés qui veulent marquer "skip"), ajout d'un swipe-left ou bouton 3-points dans Sb_24.next.
2. **Périmètre intra-exo uniquement V1.1** — la détection cross-exo (fatigue inter-mouvement) est V1.2. Documentée §K backlog.
3. **Pas de RPE estimé numérique V1** — on classe en labels qualitatifs. Une estimation RPE 1-10 demande un modèle calibré (et de la data validée). V2 si pertinent.
4. **N ≥ 3 work sets** — sinon pas de label. Conséquence : les séances "express" avec 1-2 sets/exo n'auront pas de signal Implicite (déclaratif pur).
5. **Pondération `w_implicit = 0.25`** — calibrée à dire d'expert. Sb_24 livre la pondération, Sb_24.next la tune selon retour utilisateur.
6. **Pas de rétroaction sur la calibration** — si les labels Implicites se révèlent trop sévères en pratique (taux de `reserve_probable` > 50 % systématiquement), il faut tuner la règle ET incrémenter `scoring_version` à 3, sans toucher les sessions V2 déjà loggées.
7. **Bodyweight exercises** : `weight=NULL, reps≠NULL` → completed=True, et la trajectoire ne regarde que les reps. Cohérent V1.

## K. Lotissement build (Sb_24)

| Lot | Sujet | Effort estimé | Dépendance |
|---|---|---|---|
| **Sb_24.1** | Migration BD : add `session_exercises.implicit_label`, `workout_sessions.scoring_version` (default 1). Aucun UPDATE sur lignes existantes | 2 h | — |
| **Sb_24.2** | `services/implicit_signal.py` : enum `ImplicitLabel`, fonction `detect_intra_set_label(work_sets)` + 8-10 tests unitaires couvrant les 5 patterns + edge cases (N<3, valeurs None, mixes) | 3 h | Sb_24.1 |
| **Sb_24.3** | Hook complétion : à la transition `status="completed"`, calcule et persiste `implicit_label` sur chaque `session_exercise`. Set `scoring_version=2` sur la session | 2 h | Sb_24.2 |
| **Sb_24.4** | Dépréciation checkbox : retirer du form, dériver `completed` côté handler POST. Tests handler. **Ne touche QUE les nouvelles saisies**, vérifié | 3 h | Sb_24.1 |
| **Sb_24.5** | `services/quality_score.py` V2 : `compute_session_quality()` branche sur `scoring_version`, ajout `_compute_v2` avec `w_implicit` et table de contribution §F.2 | 3 h | Sb_24.2 |
| **Sb_24.6** | UI review `/sessions/{id}/done` : pastilles labels par exercice, score ventilé par contribution | 3 h | Sb_24.5 |
| **Sb_24.7** | Coach Report (Sb_23) étendu : bloc Implicite agrégé 30j (taggé `Inféré`) | 2 h | Sb_24.5 |
| **Sb_24.8** | Sprint report + audit chiffré V1 vs V2 sur un échantillon de sessions | 1 h | tous |

**Effort total Sb_24 : ~19 h** sur 1-2 semaines.

### K backlog post-Sb_24

- **Sb_24.next1** — V1.2 cross-exo : ajouter règles "fatigue inter-mouvement même zone" (cf Q2-B). Spec : `services/implicit_signal.py` reçoit `session_exercises` ordonnés par position et croise sur même `zone_primary`.
- **Sb_24.next2** — affichage label sur historique liste séances.
- **Sb_24.next3** — RPE numérique 1-10 estimé (V2).
- **Sb_24.next4** — swipe-left "skip volontaire" si la fusion §E.3 cause des frictions.

## L. Risques

| Risque | Mitigation |
|---|---|
| Utilisateur perçoit "réserve probable" comme un jugement | Vocabulaire strict — toujours qualifié `probable`, jamais "tu n'as pas donné le max". Page review = surface neutre |
| Calibration trop sévère → tous les exos en `reserve_probable` | Sb_24.8 audit chiffré + ajustement avant merge |
| `scoring_version` complique le code | Acceptable — la stabilité historique vaut ce coût (Q4) |
| Bodyweight (weight=NULL) crée des labels bizarres | Algo §D.1 traite weight=NULL comme 0 → uniformément constant → seul reps compte. Test dédié |
| Race condition à la complétion (multi-tab) | La transition `completed` est idempotente : recalcul de `implicit_label` ne change rien si la trajectoire est la même |
| Utilisateur skippe un set en saisissant 0 par erreur | weight=0 ≠ weight=NULL côté BD. `0 OR reps>0` → completed=True. Acceptable (0 reste un vrai set saisi) |

## M. Acceptance hardrails (résumé exécutif)

| Garde-fou | Valeur |
|---|---|
| Triptyque `Saisi` / `Dérivé` / `Implicite` | Verrouillé §C |
| Pas de recalcul rétroactif | Verrouillé §H (scoring_version) |
| Périmètre intra-exo V1.1 | Verrouillé §D |
| Pas de label sur surface active | Verrouillé §G (sobre, review/done/coach/hints uniquement) |
| Pas de skip volontaire V1 | Documenté §E.3 et §J.1 |

## N. Successeur

**Sx_25** — Coach Report v2 LLM narratif encadré (toujours sur la page SSR imprimable, pas de PDF natif V1). Réutilisera les labels Implicites comme matière première pour la narration.
