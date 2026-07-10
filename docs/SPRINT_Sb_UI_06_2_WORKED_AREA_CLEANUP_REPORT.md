# Sprint Sb_UI_06.2 — Worked Area Density Cleanup

**Statut** : 🟢 DELIVERED — pending GO commit + CI + human review
**Date** : 2026-07-10
**Cycle** : Sx_UI_06 Information Density / Dedup
**Spec** : [`docs/strategy/Sx_UI_06_INFO_DENSITY_DEDUP_SPEC.md`](strategy/Sx_UI_06_INFO_DENSITY_DEDUP_SPEC.md)
**Précondition** : `Sb_UI_06.1` HUMAN REVIEW ACCEPTED ✅ (vérifié dans le repo).

---

## 0. Feedback utilisateur

Après l'intégration Sx_32 (Worked Area consommant `body_map_descriptor`), le
panneau « Zone travaillée » de la carte active était **dense et bavard** :
- un chip de code brut (« pecs ») **en plus** du label lisible (« Pectoraux ») ;
- une forme body-map décorative ;
- **jusqu'à 4× « À qualifier »** sur un exercice inconnu (Principal + Assistants +
  Stabilisation + Pattern), dont une row Stabilisation **toujours vide** en V1 ;
- une note longue.
Règle produit : *une information = un seul endroit* ; le Worked Area doit être un
**repère d'entraînement discret**, pas un dashboard anatomique.

---

## 0bis. Brainstorming / Options / Risques / Choix retenu — sujets clivants

> Étape obligatoire. Les 10 sujets clivants du brief, tranchés (décisions
> logiques + confirmation opérateur sur les 3 les plus structurants).

| # | Sujet clivant | Décision | Justification |
|---|---|---|---|
| 1 | Garder « Zone travaillée » ou label plus court ? | **Garder** | Clair, testable, a11y ; c'est le titre de section, pas un doublon. |
| 2 | « Principal / Assistants » ou zones seules ? | **Garder les rôles** | Distinction primary/secondary explicite et utile ; retirée = perte de sens. |
| 3 | Garder les chips ou ligne texte compacte ? | **Retirer le chip** (code brut, aria-hidden) | Redondant avec le label texte « Pectoraux ». Décoratif, aucune sémantique. |
| 4 | « À qualifier » une fois ou par slot vide ? | **Une fois** (sur Principal) | 4× → 1× ; les slots vides (assistants/stabilisation/pattern) sont **masqués**. |
| 5 | Masquer tout le Worked Area en unknown ? | **Non** (rejet Option C) | Le signal « trou de mapping » reste utile ; Principal porte « À qualifier ». |
| 6 | Exposer `resolution_path` visuellement ? | **Non** — `data-*` seul | Debug/smoke uniquement ; jamais de badge utilisateur « db_lookup ». |
| 7 | Note non médicale visible ou implicite ? | **Visible mais raccourcie** | « Estimation — repère, non médical » (microcopy courte, prudence conservée). |
| 8 | Distinguer `db_lookup` / `substring_fallback` en UI ? | **Non** | Bruit technique inutile pour l'utilisateur ; reste en `data-*`. |
| 9 | Différence carte active vs non-active ? | **Sans objet** | Le Worked Area n'existe **que** sur la carte active (contrat Sx_UI_04.3). |
| 10 | Cleanup template seul ou logique route ? | **Template-only (Option A)** | `body_map_data` inchangé, aucune logique de présentation côté route. |

### Options comparées (globale)

| Option | Description | Verdict |
|---|---|---|
| **A** | Template-only compact cleanup (`body_map_data` inchangé) | ✅ **RETENU** — risque faible, conservateur, aucun contrat descriptor brouillé |
| B | Normalisation des labels côté router | ❌ REJETÉ — crée de la logique de présentation en route, brouille le contrat Sx_32 |
| C | Masquer le Worked Area en unknown | ❌ REJETÉ — perd le signal « à qualifier » (trous de mapping) |
| D | Redesign complet | ❌ REJETÉ — trop large pour `.2` |

### Risques / parades
| Risque | Parade |
|---|---|
| Tests asservissant chip / stabilizer / pattern / note | **Ré-orientés vers la nouvelle vérité** (masquage conditionnel), jamais affaiblis |
| CSS orphelin (`.body-zone-chip`, `.worked-area-pattern`) | Laissé inerte (retrait non « strictement nécessaire » ; élargirait le diff/risque) — documenté |
| Perte du signal unknown | Principal porte « À qualifier » ; Worked Area jamais masqué |
| Template partagé non vu par le garde-fou | Surclassement manuel `isolated → shared_code` → broad sweep large |

---

## 1. Changements effectués

### 1.1 `app/templates/_partials/exercise_card.html` (MODIFIÉ, Worked Area seul)

- **Chip de zone retiré** (`.session-focus__body-zone-chip`, code brut aria-hidden).
- **Body-map CSS conservé** (repère visuel discret, aria-hidden).
- **Row Stabilisation retirée** (toujours « À qualifier » en V1 — slot vide permanent).
- **Row Assistants** rendue **uniquement si `secondary_labels` non vide**.
- **Pattern** : passé de div `.worked-area-pattern` à une row `.worked-area-row--pattern`
  rendue **uniquement si une description atlas existe** (plus de « À qualifier » vide).
- **Note raccourcie** : « Lecture indicative issue du mapping exercice — repère
  d'entraînement, non diagnostic médical. » → **« Estimation — repère, non médical. »**
- **`data-resolution-path` conservé** (jamais visible utilisateur).
- `body_map_data` / route **inchangés** (Option A template-only).

---

## 2. Avant / Après

| Cas | Avant | Après |
|---|---|---|
| **Known** (Chest Press) | titre + chip « pecs » + body-map + Principal « Pectoraux » + Assistants « Triceps » + Stabilisation « À qualifier » + Pattern + note longue | titre + body-map + **Principal « Pectoraux »** + **Assistants « Triceps »** + note courte. **0 « À qualifier »**, chip retiré. |
| **Unknown** | 4× « À qualifier » (Principal + Assistants + Stabilisation + Pattern) + chip | **Principal « À qualifier » (1×)** + note courte. Rows vides masquées. Worked Area toujours visible. |

Vérifié en rendu réel : known → 0 « À qualifier », `Pectoraux`×1, `Triceps`,
`data-resolution-path` présent ; unknown → « À qualifier »×1, row secondary absente.

---

## 3. Tests

### 3.1 Nouveaux / étendus
- `tests/test_ui06_dedup.py` (ÉTENDU) : +7 tests D3 (chip retiré · primary 1× ·
  assistants si présents · 0 « À qualifier » sur known · « À qualifier » 1× sur
  unknown · `resolution_path` en `data-*` seul · note courte non médicale).

### 3.2 Ré-orientés vers la nouvelle vérité (non affaiblis)
- `test_session_focus_worked_area.py` : stabilizer retirée / pattern conditionnel /
  note raccourcie.
- `test_session_focus_cockpit.py` : « 3 roles » → primary présent + pas de slot vide.
- `test_worked_area_descriptor.py` : chip retiré du set attendu ; note « non médical ».

### 3.3 Résultats
- Ciblés Worked Area + dedup : **93 passed**.
- ruff **541 ≤ 548** ; spec protocol vert.
- Broad sweep large (16 fichiers Focus Mode) : **voir §Verdict**.
- **Full sweep local** : non exécuté — un test **préexistant hang** localement
  (documenté Sb_UI_06.1, absent en CI). La **CI réelle** (job pytest
  `timeout-minutes: 25`) fait foi.

---

## 4. Invariants préservés

- **D1 / D2 de Sb_UI_06.1 restent vrais** (charge précédente console-only carte
  active ; cible = placeholder case).
- Contrat de logging (`set_*_weight_kg/_reps`, form, no-JS, dérivation serveur) **intact**.
- **Aucun** changement `body_map_descriptor` / `muscle_mapping` / route `sessions`
  / modèle / migration / schema / scoring / coach / body intelligence / substitution
  / readiness / JS / endpoint / rebrand / deploy.
- SSR / no-JS strict ; « À qualifier » jamais inventé ; aucune allégation médicale.
- resolution_path en `data-*` seul (db_lookup / substring_fallback non exposés).

---

## 5. Fichiers modifiés (whitelist)

| Fichier | État |
|---|---|
| `app/templates/_partials/exercise_card.html` | MODIFIÉ (Worked Area) |
| `tests/test_ui06_dedup.py` | MODIFIÉ (+7 tests D3) |
| `tests/test_session_focus_worked_area.py` | MODIFIÉ (ré-orienté) |
| `tests/test_session_focus_cockpit.py` | MODIFIÉ (ré-orienté) |
| `tests/test_worked_area_descriptor.py` | MODIFIÉ (ré-orienté) |
| `docs/SPRINT_Sb_UI_06_2_WORKED_AREA_CLEANUP_REPORT.md` | NOUVEAU |
| `docs/strategy/SPEC_REGISTRY.md` · `ROADMAP_AND_NEXT_STEPS.md` | MODIFIÉS |

`session_focus.css` **non modifié** (retrait du CSS orphelin non strictement
nécessaire — inerte). Aucun service / modèle / migration / route touché. Aucun artefact.

---

## 6. Limites

- CSS orphelin résiduel (`.body-zone-chip`, `.worked-area-pattern`,
  `.worked-area-row--stabilizer`) : inerte, non retiré (hors « strictement
  nécessaire »). Candidat cleanup CSS ultérieur.
- Le Worked Area reste **carte active seulement** (contrat Sx_UI_04.3).

## 7. Statut Body Intelligence

⏸️ **deferred** (aucune migration de consommateur métier dans ce sprint).

## 8. Next step recommandé

- **`Sb_UI_06.3`** (Home : teaser readiness → pointeur + KPI = sous-ensemble), **ou**
- reprise **Body Intelligence** après stabilisation UI (dé-densification terminée).

---

## Verdict

**Verdict :** 🟢 **Sb_UI_06.2 Worked Area density cleanup livré — repère discret, « À qualifier » 1× max, chip décoratif retiré, contrats intacts — pending GO commit + CI + human review.**

Le Worked Area est désormais un **repère d'entraînement discret** : label de zone
lisible sans chip redondant, assistants seulement s'ils existent, plus de slots
vides répétant « À qualifier » (1× max, sur Principal), note courte non médicale,
`resolution_path` en `data-*` pour le smoke. Template-only, `body_map_descriptor`
et la route inchangés ; D1/D2 préservés. Tests ré-orientés vers la nouvelle vérité
(93 verts). Prêt pour GO commit ; la CI réelle fait le full sweep.
