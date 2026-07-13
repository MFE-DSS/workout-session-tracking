# Sprint Sx_FB_01 — Exercise Feedback Rationalization (VERIFICATION)

**Statut** : 🟢 **VERIFIED — ALREADY DONE** (aucun code touché ; batch local, non commité)
**Type** : VERIFICATION-ONLY — docs-only (le build cible est déjà en place)
**Date** : 2026-07-13
**Cycle** : batch local (à la suite de Sx_CAT_01, non commité)
**Référence décisionnelle** : [`strategy/SPIGNOS_EXERCISE_FEEDBACK_RATIONALIZATION.md`](strategy/SPIGNOS_EXERCISE_FEEDBACK_RATIONALIZATION.md)
**Préconditions** : `Sx_UI_07.2` ACCEPTED ✅ ; Sx_CAT_01 livré localement non commité ✅ (préservé) ; CI timeout 45 ✅ ; BI activation deferred ✅.

---

## 0. Résumé exécutif

Le brief demande de **cacher `execution_quality` + `reps_target` dans un `<details>`
« Feedback avancé »**, en supposant que ces champs sont **actuellement visibles/saisis**
en séance. **L'audit du code réel prouve le contraire** : ces champs sont **déjà
absents du formulaire** — retirés par un build antérieur (**Sb_01**) et **acté** par
**Sx_04 §13** de la spec de référence. **L'objectif produit du sprint est déjà
atteint** (et plus radicalement : suppression UI complète plutôt que `<details>`).

**Décision (arbitrée avec l'opérateur) : verification-only, aucun code touché** — pour
éviter une **régression** (re-introduire des inputs déjà retirés augmenterait le coût
de saisie, contraire à l'objectif).

---

## 1. Étape 0 — Brainstorming / Options / Choix retenu

### Options

| Option | Description | Verdict |
|---|---|---|
| **A** | Documenter « déjà réalisé » (verification-only, no code) | ✅ **RETENU** (arbitrage opérateur) |
| B | Cadrer un vrai sprint feedback différent | ❌ nécessiterait une nouvelle spec (hors GO actuel) |
| C | Implémenter le brief littéralement (ré-introduire les champs) | ❌ **régression** : contredit Sb_01/Sx_04, ré-augmente le coût de saisie |

### Sujets clivants — tranchés par le constat

Les 15 sujets du brief présupposent que les champs sont visibles. Comme ils sont
**déjà cachés (absents)**, la plupart deviennent sans objet. Le sujet réellement
tranché : **cacher ou re-exposer ?** → **ne rien re-exposer** (la spec l'interdit
explicitement : « Ne pas re-introduire … sans trigger produit explicite »).

---

## 2. Audit — template + routeur

### 2.1 Template de séance
- **`app/templates/session_detail.html`** (route `session_detail`, `sessions.py:448`)
  inclut le partial **`app/templates/_partials/exercise_card.html`** qui rend les set
  rows et le feedback exercice.
- **Inputs de saisie réels** (name=) dans `exercise_card.html` :
  `set_{id}_weight_kg`, `set_{id}_reps` (par set), `substituted_name`, `free_note`,
  `muscle_sensation` (via macro `segmented`).
- **Aucun input** `execution_quality` ni `reps_target` — `grep 'name="execution_quality"'`
  et `'name="reps_target"'` → **0 résultat**.
- `muscle_sensation` est **déjà** dans un `<details class="field-block field-block--optional">`
  (« Sensation musculaire (optionnel) »).
- `success_score` : **affiché en lecture seule** (recap session completed), pas d'input.

### 2.2 Routeur `sessions.py` (`update_exercise_card`)
- Lit du formulaire : `concentration`, `global_state`, `muscle_sensation`
  (`sessions.py:608-609, 684` via `enum_str(form.get(...), ...)`).
- **Ne lit PAS** `execution_quality` ni `reps_target` → sur toute nouvelle séance ces
  colonnes restent **null**, sans erreur (le routeur tolère leur absence par
  construction : il ne les cherche pas).

---

## 3. Cible = état actuel (table de vérification)

| Champ | Cible spec | État réel vérifié | Conforme ? |
|---|---|---|---|
| `weight_kg` / `reps` / `completed` (set) | visible | inputs présents (par set) | ✅ |
| `execution_quality` (set) | caché (mode avancé) | **absent du form** (plus radical) | ✅ (objectif atteint) |
| `reps_target` (set) | caché (mode avancé) | **absent du form** | ✅ (objectif atteint) |
| `technique` (set) | visible si déjà | rendu si `sl.technique` | ✅ |
| `success_score` (exo) | visible, inchangé | **lecture seule** (recap) — décision Sb_01/Sx_04 | ✅ (acté) |
| `muscle_sensation` (exo) | visible, inchangé | **`<details>` optionnel** — décision Sb_01/Sx_04 | ✅ (acté) |
| `free_note` (exo) | visible si déjà | `<details>` note | ✅ |

---

## 4. Preuve — le formulaire fonctionne sans les champs avancés

Le routeur ne lit jamais `execution_quality`/`reps_target` : une soumission de séance
**sans** ces champs est le **comportement normal actuel** (toute séance créée
aujourd'hui). Aucune erreur, colonnes → null. C'est exactement la « tolérance à
l'absence » que le brief cherchait à obtenir — elle est **déjà là**.

---

## 5. Preuve — données historiques préservées

- Les **colonnes DB** `execution_quality` (`session.py:252`) et `reps_target`
  (`session.py:253`) existent toujours (SetLog, nullable) — **aucune migration**.
- Les sessions historiques ayant ces valeurs (remplies par import/restore normalisé,
  cf. `restore.py`) **les conservent** en base.
- **Aucun recalcul, aucune suppression, aucune migration.**

---

## 6. Preuve — consumers analytiques inchangés

`grep` exhaustif : `execution_quality`/`reps_target` sont consommés **uniquement** par
`export_builder.py` et `restore.py` — **aucun** KPI / scoring / delta / stats /
exercise_history / behavioral ne les lit (**orphelins analytiques**, exactement comme
la spec §1 le documentait). Donc leur absence en saisie **n'affecte aucun consumer
analytique**.

---

## 7. Preuve — export compatible

`export_builder.py` conserve les 2 colonnes :
- **JSON** : `"execution_quality": sl.execution_quality`, `"reps_target": sl.reps_target` (L85-86) ;
- **CSV** : colonnes `execution_quality`, `reps_target` (headers L165-166 ; valeurs `_opt(...)` L239-240).

L'export reste **structurellement identique** ; les valeurs sont null pour les séances
sans saisie avancée (comportement attendu). **Zéro breaking change export.**

---

## 8. Fichiers modifiés

**AUCUN fichier applicatif ni test touché.** Ce sprint est **verification-only** :
- `data/reference_split.json` reste celui de **Sx_CAT_01** (préservé, non modifié ici) ;
- rapport + registry + roadmap uniquement (docs).

---

## 9. Chemins interdits vérifiés

✅ Aucun touché : `app/models/**`, `migrations/**`, `schema_snapshot.sql`,
`quality_score.py`, `kpis.py`, `delta.py`, `stats.py`, `exercise_history.py`,
`export_builder.py`, `behavioral.py`, `sessions.py`, `pages.py`, `progress.html`,
`history.html`, `body_intelligence*`, `physique.html`, `catalog_qa.py`. Working tree
Sx_CAT_01 **préservé** (non reset, non stash, non restauré).

---

## 10. Tests locaux

Aucun test dédié Sx_FB_01 créé (verification-only — rien à tester de nouveau ; le
comportement cible est déjà couvert par les tests existants de séance/export/kpis qui
passent avec `execution_quality`/`reps_target` null). L'audit s'appuie sur :
- `grep` inputs (0 pour les 2 champs) ;
- `grep` routeur (ne lit pas les 2 champs) ;
- `grep` consumers (orphelins hors export/restore) ;
- lecture de la spec §13 (déviations Sb_01 actées par Sx_04).

> Aucun commit, aucun push, aucune CI (LOCAL BATCH MODE).

---

## 11. Limites

- **Verification-only** : rien n'est amélioré au-delà de constater que la cible est
  atteinte. Si un besoin **réel et différent** émerge (indicateur visuel de données
  historiques, ré-exposition d'un champ demandé par le terrain), il faudra une
  **nouvelle spec** — hors de ce sprint.
- La question ouverte de la spec §212 (badge/dot si `<details>` contient des données)
  reste **non tranchée** — mais elle supposait un `<details>` qui n'existe pas
  (champs retirés). Sans objet en l'état.

---

## 12. Next (dans le batch)

- **Substitution Graph** (spec — `cross_pattern_substitutions.json` existe), ou
- **GO BATCH COMMIT + CI complète** (Sx_CAT_01 + ce rapport de vérification).

---

## Verdict

**Verdict :** 🟢 **Sx_FB_01 Exercise Feedback Rationalization — VERIFIED / ALREADY DONE.**

L'objectif — retirer le coût de saisie des champs orphelins `execution_quality` +
`reps_target` — **est déjà réalisé** (build Sb_01, acté Sx_04 §13) : ces champs sont
**absents du formulaire** (plus radical qu'un `<details>`), le routeur ne les lit pas,
les colonnes DB + l'export les conservent, aucun consumer analytique ne les exploite,
`success_score` est en lecture seule et `muscle_sensation` en `<details>` optionnel —
le tout **acté et accepté**. **Aucun code touché** (arbitrage opérateur : ne pas
ré-introduire une surface de saisie déjà supprimée = éviter une régression). Working
tree Sx_CAT_01 préservé. Non commité, non poussé, CI non lancée.
