# SPIGNOS Exercise Feedback Rationalization Spec

**Sprint:** Sx_01_exercise_feedback_rationalization_spec
**Date:** 2026-04-13
**Status:** Spec approved, pending build (Sb_01)

---

## 1. Audit Summary — Etat reel du signal feedback

### Champs captures par niveau

**Session level** (`workout_sessions`) :
- `concentration` — STR high/medium/low — feeds quality_score (10pts), behavioral fatigue
- `global_state` — STR good/flat/fatigued — feeds quality_score (10pts), behavioral fatigue
- `bodyweight_kg` — FLOAT — snapshot per session, timeline
- `free_note` — STR 280 chars — non-analytique

**Exercise level** (`session_exercises`) :
- `success_score` — INT 100/80/50 — feeds quality_score (40pts), KPIs avg, deltas, exercise history, leaderboard (indirectly via quality_score)
- `muscle_sensation` — STR strong/partial/weak — feeds display only (stats, exercise history, export)
- `free_note` — STR 140 chars — non-analytique

**Set level** (`set_logs`) :
- `weight_kg` — FLOAT — donnee objective de base
- `reps` — INT — donnee objective de base
- `completed` — BOOL — feeds quality_score (40pts), KPIs completion_rate, delta first_set, progression_hint, leaderboard
- `execution_quality` — STR clean/acceptable/degraded — **feeds ONLY export CSV/JSON**
- `reps_target` — STR target_hit/target_near/target_missed — **feeds ONLY export CSV/JSON**
- `technique` — STR RP/DS (optional intensity technique label)

### Constats critiques verifies dans le code

**1. `execution_quality` et `reps_target` sont analytiquement orphelins.**
Grep exhaustif sur le codebase (hors docs) montre que ces deux champs ne sont consommes que par `app/services/export_builder.py` (lignes d'export JSON et CSV). Aucun KPI, aucun scoring, aucun delta, aucune page ne les exploite. Zero analytics, mais cout UX maximum (2 radios x N work sets).

**2. `success_score` est le champ le plus charge du produit.**
Consumers verifies dans le code :
- `app/services/quality_score.py:60-68` — 40/100 points du session quality
- `app/services/kpis.py:90-98` — `avg_success_score_30d`
- `app/services/kpis.py:292` — per-template avg
- `app/services/delta.py:55-62` — score_trend up/flat/down
- `app/services/stats.py:86, 109` — affichage prior summary et current summary
- `app/services/exercise_history.py:76` — display per-row
- `app/services/export_builder.py` — export JSON/CSV
- `app/services/leaderboard.py` — via `compute_session_quality` → quality_score consomme success_score

**3. `muscle_sensation` est un signal orthogonal unique.**
Il capture "ai-je senti le muscle travailler ?" — signal physiologique que rien d'autre ne capture. Consume display only mais reste le seul champ qui connecte training → ressenti musculaire. Valeur future pour correlation avec zone scoring du physique dashboard.

**4. Cout UX actuel par exercice (5 work sets) : 27 inputs.**
- 5x completed + 5x weight + 5x reps = 15
- 5x execution_quality + 5x reps_target = 10 (dont 0 consumers analytiques)
- 1x success_score + 1x muscle_sensation = 2
Pour 7 exercices : ~189 inputs par session. Les 10 inputs orphelins representent ~37% du cout UX par exercice, pour zero valeur produit.

### Table d'audit champ / consumer / doublon / decision

| Champ | Niveau | Primaire/Derive | Consumers analytiques | Doublon semantique | Decision |
|-------|--------|----------------|----------------------|-------------------|----------|
| weight_kg | Set | Primaire | delta, progression_hint, exercise_history, stats, leaderboard (via quality_score filtering) | Aucun | **INCHANGE — visible** |
| reps | Set | Primaire | delta, progression_hint, exercise_history, stats | Aucun | **INCHANGE — visible** |
| completed | Set | Primaire | quality_score (40pts), kpis (completion_rate), delta (first_set), progression_hint, leaderboard | Aucun | **INCHANGE — visible** |
| execution_quality | Set | Primaire | **export only** | Partiellement avec `completed` (un set non complet est souvent degraded) mais orthogonal en theorie | **CACHE — mode avance** |
| reps_target | Set | Primaire | **export only** | Partiellement avec `success_score` exercice (succes global derive indirectement du hit des targets) | **CACHE — mode avance** |
| technique | Set | Primaire | export, display | Aucun | **INCHANGE — visible** |
| success_score | Exercice | Primaire | quality_score (40pts), kpis, delta, stats, exercise_history, leaderboard, export | Avec agregation de reps_target au niveau set (theorique) | **INCHANGE — visible** |
| muscle_sensation | Exercice | Primaire | stats, exercise_history, export | Aucun (orthogonal a success_score) | **INCHANGE — visible** |
| free_note (exercice) | Exercice | Primaire | display, export | Aucun | **INCHANGE — visible** |
| concentration | Session | Primaire | quality_score (10pts), behavioral | Aucun | **INCHANGE** |
| global_state | Session | Primaire | quality_score (10pts), behavioral | Aucun | **INCHANGE** |

---

## 2. Decisions structurantes

### Decision 1 — `execution_quality` + `reps_target` caches par defaut en mode "Feedback avance"

**Rationale :** Zero consumer analytique, cout UX disproportionne (10 taps/exercice).

**Implementation :** Les deux champs restent dans le modele et dans le formulaire, mais enveloppes dans un element HTML `<details>` natif ferme par defaut. L'utilisateur qui veut les renseigner clique sur "Feedback avance" pour deplier les 2 radios.

**Label UI recommande :** "Feedback avance" (ou "Precisions avancees") — surtout PAS "mode expert" qui peut intimider ou suggerer une obligation de remplissage.

**Options ecartees :**
- **Suppression** rejetee : irreversible, perd la donnee historique, ferme la porte a toute exploitation future.
- **Garder visible** rejete : cout UX trop eleve pour zero valeur actuelle.
- **Mode expert opt-in global** (toggle user preference) rejete : ajoute une table de preferences + logique de switch, complexite disproportionnee pour un usage marginal.

### Decision 2 — `success_score` reste saisi manuellement, signal primaire

**Rationale :**
1. Le changer impacte trop de consumers (quality_score, KPIs, deltas, leaderboard, behavioral, export) — risque de regression eleve.
2. Cout UX de 1 tap — negligeable vs les 10 taps supprimes par la decision 1.
3. Un derive automatique necessiterait `rep_targets` toujours renseignes dans les templates (ce qui n'est pas garanti sur les templates archived).

**Statut analytique explicite (a verrouiller noir sur blanc) :**
> `success_score` est un **signal de synthese operationnel subjectif**, pas un score scientifique de performance. Il capture l'auto-evaluation rapide de l'utilisateur ("comment ca s'est passe globalement sur cet exercice ?") avec 3 niveaux discrets (100/80/50). Il est utilise comme proxy rapide dans les KPIs et deltas, mais ne doit jamais etre interprete comme une mesure objective de la performance biomecanique. Un score derive objectif (base sur reps vs target, tonnage trend, etc.) est l'affaire du physique dashboard et du body engineering dashboard, pas de ce champ.

**Options ecartees :**
- **Derive automatique** (option B) rejete : trop de consumers impactes, necessite rep_targets partout.
- **Hybride avec override** (option C) rejete : complexite UX (expliquer "override") disproportionnee.

### Decision 3 — `muscle_sensation` reste saisi et visible

**Rationale :** 1 seul tap par exercice. Signal physiologique orthogonal unique (aucun autre champ ne capture "ai-je senti le muscle ?"). Valeur future pour correlation avec zone scoring du physique dashboard (S2+) et detection d'asymetries neuro-musculaires (S5+).

**Options ecartees :**
- **Cacher en mode avance** rejete : la valeur produit vs cout (1 tap) est positive.
- **Deplacer en fin de seance** rejete : le ressenti est plus precis capture immediatement apres l'exercice, pas 30 min plus tard.

---

## 3. Modele cible

### Par defaut (mode normal)

Par exercice (5 work sets) :
- **Set row** : 1 checkbox + 1 weight + 1 reps = 3 inputs × 5 = 15 inputs
- **Exercice feedback** : 1 success_score + 1 muscle_sensation + optionnel free_note = 2 inputs
- **Total** : **17 inputs/exercice** (vs 27 actuellement)

Pour une session 7 exercices : ~119 inputs (vs 189 actuellement). **Gain : ~37% d'inputs en moins.**

### Mode feedback avance (opt-in par exercice)

Pour un exercice donne, le user deplie `<details>Feedback avance</details>` dans chaque work set row. Les champs `execution_quality` et `reps_target` deviennent visibles et remplissables. Le reste de l'UX est inchange.

Aucune preference utilisateur persistee — c'est juste un `<details>` HTML natif. L'etat ouvert/ferme est local a la page.

---

## 4. Impacts par composant

| Composant | Impact | Action |
|-----------|--------|--------|
| `app/templates/session_detail.html` | **Modifier** | Wrapper `<details class="advanced-feedback">` autour des 2 radios execution_quality + reps_target dans chaque work set row |
| `app/routers/sessions.py` | **Aucun** | `update_exercise_card` tolere deja les champs null via `enum_str(form.get(...), _SET)` |
| `app/models/session.py` | **Aucun** | Colonnes nullable, pas de migration |
| `app/services/quality_score.py` | **Aucun** | Ne consomme pas execution_quality/reps_target |
| `app/services/kpis.py` | **Aucun** | Idem |
| `app/services/delta.py` | **Aucun** | Idem |
| `app/services/stats.py` | **Aucun** | Idem |
| `app/services/exercise_history.py` | **Aucun** | Idem |
| `app/services/export_builder.py` | **Aucun** | Continue d'exporter les colonnes (null si non rempli) |
| `app/services/behavioral.py` | **Aucun** | Pas de signal set-level |
| Tests existants | **Verifier** | Les tests remplissent parfois execution_quality/reps_target — doivent toujours passer car les champs restent acceptes par le routeur |
| CSS `app/static/css/app.css` | **Modifier** | Style discret pour `details.advanced-feedback` (petit label, padding minimal, pas de box lourde) |

---

## 5. Compatibilite historique

- **Zero breaking change.** Les colonnes restent, les consumers ne changent pas.
- Les donnees historiques (execution_quality/reps_target remplies avant) restent exploitables dans les exports et seront affichees a l'ouverture du `<details>` si le user re-edite une vieille session.
- Les futures sessions auront ces champs a null par defaut (sauf si le user ouvre "Feedback avance" et remplit).

---

## 6. Strategie de migration

**Aucune migration DB requise.** Uniquement :
1. Modification template `session_detail.html`
2. Ajout style CSS discret pour le `<details>`
3. Aucune migration Alembic
4. Aucun script de data migration

---

## 7. Risques

| Risque | Probabilite | Impact | Mitigation |
|--------|------------|--------|------------|
| Perte de signal set-level si on veut construire une analytique dessus plus tard | Faible | Moyen | Colonnes preservees. Mode avance accessible. Re-promouvoir visible si un consumer emerge. |
| `<details>` mal integre visuellement — sous-formulaire qui desaligne la carte exercice | Moyenne | Moyen | **Garde-fou UX explicite dans Sb_01** : les `<details>` ouverts doivent preserver la compacite de la set row, rester lisibles mobile, ne pas affaiblir la CTA principale de validation exercice. |
| L'utilisateur ne trouve pas le mode avance | Faible | Faible | Le `<details>` a un label clair "Feedback avance". Pas critique car le signal n'est pas exploite analytiquement. |
| Tests casses si execution_quality/reps_target deviennent null en mode normal | Nul | — | Le routeur accepte deja les nulls. Tests existants inchanges. |
| Regression sur l'affichage des donnees historiques | Faible | Faible | Quand un user re-ouvre une session passee avec ces champs remplis, le `<details>` reste ferme mais les valeurs existent — il peut l'ouvrir pour voir/editer. |

---

## 8. Acceptance criteria — Spec (Sx_01)

- [x] Audit champ/consumer/doublon verifie dans le code (Grep exhaustif effectue)
- [x] Table d'audit produite avec decisions explicites
- [x] Modele cible (primaire visible vs primaire cache) documente
- [x] Statut analytique de `success_score` explicite noir sur blanc
- [x] Impacts par composant cartographies
- [x] Strategie de compatibilite historique definie (zero breaking change)
- [x] Aucune migration DB requise
- [x] Label UI arbitre ("Feedback avance" et pas "mode expert")
- [x] Garde-fou UX mobile ajoute dans les AC du build
- [x] Bloqueurs pour Sx_02 identifies (aucun)

## 9. Acceptance criteria — Build (Sb_01)

- [ ] `execution_quality` + `reps_target` caches dans `<details class="advanced-feedback">` par defaut dans chaque work set row
- [ ] Label du `<details>` : "Feedback avance" (pas "mode expert")
- [ ] Le formulaire fonctionne avec et sans les champs avances remplis
- [ ] Les valeurs existantes (sessions passees) s'affichent correctement quand le `<details>` est ouvert
- [ ] Aucun consumer analytique casse (quality_score, KPIs, delta, stats, exercise_history, leaderboard, behavioral inchanges)
- [ ] Export CSV/JSON continue d'inclure les colonnes
- [ ] Tests existants passent
- [ ] **Garde-fou UX mobile** : les `<details>` ouverts preservent la compacite de la set row, restent lisibles en mobile sans desaligner la carte exercice, n'affaiblissent pas la CTA principale de validation exercice
- [ ] Gain UX mesurable : -10 inputs/exercice en mode normal (de 27 a 17)

---

## 10. Questions ouvertes

- **RAS cote spec.** Toutes les questions structurantes ont ete tranchees.
- Une question UX secondaire (mais pas bloquante) : faut-il un indicateur visuel quand le `<details>` contient des donnees renseignees (badge, dot) ? A trancher au build si pertinent, pas prioritaire.

---

## 11. Bloqueurs pour Sx_02

**Aucun.** Le modele cible est minimaliste. Sx_02 peut designer le flux mobile focus-exercice en sachant que le feedback par defaut est :
- `weight_kg`, `reps`, `completed` au niveau set
- `success_score`, `muscle_sensation`, `free_note` au niveau exercice
- `execution_quality`, `reps_target` accessibles via `<details>` si besoin

---

## 12. Migration concerns (synthese)

- Pas de migration DB
- Pas de rewrite d'historique
- Pas de changement de consumer
- Uniquement : 1 template + 1 CSS rule
- Rollback trivial : retirer le `<details>` et ca revient au comportement actuel

---

## 13. Deviations observees dans Sb_01 (post-build audit, ajoute par Sx_04)

L'audit reel du code (2026-04-14, voir Sx_04 §3.1) a revele que le build Sb_01 s'est ecarte des decisions A+B+A de cette spec sur **3 points**. Ces deviations sont documentees ici pour eviter toute reouverture de debat.

| Decision Sx_01 | Build Sb_01 | Ecart | Arbitrage Sx_04 |
|----------------|-------------|-------|-----------------|
| Decision B : `execution_quality` + `reps_target` caches dans `<details>Feedback avance</details>` | Champs non rendus du tout dans le formulaire (pas de `<details>`) | Plus radical que la decision — suppression UI complete | **Accepte.** Gain UX superieur, signal inexploite analytiquement, colonnes DB preservees. |
| Decision A : `success_score` saisi manuellement visible | Non rendu comme input. Affiche uniquement en lecture (recap, history) | Le champ existe en DB et dans le router mais pas en UI d'entree | **Accepte.** KPIs consommateurs degradent gracieusement avec NULL. Ne pas re-introduire le radio tant qu'aucun user ne le demande. |
| Decision A : `muscle_sensation` visible et saisi | Wrappe dans `<details>Sensation musculaire (optionnel)</details>` | Mis en "optionnel" plutot que visible par defaut | **Accepte.** Leger ecart sans impact analytique. |

**Consequence analytique a connaitre :**

- `kpis.avg_success_score_30d` → souvent NULL
- `quality_score` → max effectif ~60/100 (perd les 40 pts de success_score si NULL)
- `delta.score_trend` → souvent None
- `exercise_history.success_score` → None sur nouvelles sessions

**Ces comportements sont TOUS deja geres par le code** (checks `is not None` dans les consumers). Aucun bug. Simplement une dynamique de signal reduit qui etait une option du design initial — devenue le comportement reel par decision build.

**Ne pas re-introduire le radio `success_score` dans le formulaire sans trigger produit explicite.**
