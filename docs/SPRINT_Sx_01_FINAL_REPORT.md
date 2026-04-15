# Sprint Sx_01 FINAL Report — Exercise Feedback Rationalization (Final Spec)

**Date:** 2026-04-14
**Type:** Spec only — aucun build
**Prerequisite:** Sb_R3 clos et stabilise
**Suivi par :** Sx_02 UX mobile bloc exercice

---

## Objectif

Produire le spec FINAL rigoureux du signal feedback exercice, aligne avec la realite du code apres audit exhaustif, et servir de base exploitable pour Sx_02.

---

## Revision majeure vs audits precedents

Mes audits precedents (Sx_01 initial + §13 deviations + Sx_04) affirmaient que **`compute_success_score()` n'existait pas** et que `success_score` etait simplement "non rendu dans le formulaire". C'etait **incorrect**.

Le code reel montre :
- `app/services/feedback.py:28` — fonction `compute_success_score(session_exercise, template_exercise) -> Optional[int]`
- `app/routers/sessions.py:408-409` — appel systematique dans le POST `update_exercise_card`
- `tests/test_feedback.py` — 11 tests valident l'algorithme
- `tests/test_session_flow.py:286`, `test_restore.py:264`, `test_export.py:88` — assertions explicites `in {100, 80, 50}` + commentaires "derived by compute_success_score"

**Conclusion :** le build Sb_01 a effectivement implemente la **derivation automatique** de `success_score`. Le spec FINAL verrouille cet etat comme etat canonique, sans reouvrir les debats anterieurs qui reposaient sur une lecture incomplete du code.

---

## Decisions finales (D1-D5)

- **D1 — `success_score` DERIVE** par `compute_success_score()` snap vers {100, 80, 50}
- **D2 — `muscle_sensation` SAISI OPTIONNEL** dans un `<details>` discret
- **D3 — `execution_quality` + `reps_target` RETIRES DE L'UI** — colonnes DB preservees, aucun consumer analytique
- **D4 — `concentration` + `global_state` + `bodyweight_kg` inchanges** — saisis optionnels dans session feedback
- **D5 — `free_note` exercice + session inchanges** — saisie libre optionnelle

---

## Taxonomie cible 3 axes

| Axe | Role | Champs | Source |
|-----|------|--------|--------|
| **A — Performance mecanique** | Base de calcul, objectif | weight, reps, completed | Saisie directe |
| **B — Qualite technique** | Adherence a la prescription | success_score | **Derive** de Axe A + catalogue |
| **C — Ressenti physiologique / ciblage** | Signal subjectif non-derivable | muscle_sensation, concentration, global_state, free_note | Saisie necessaire |

Les 3 axes sont orthogonaux. Aucun doublon actif.

---

## Matrice consumers — produits / consommateurs

### Impact D1 (success_score derive)

**Producteur unique :** `update_exercise_card` via `compute_success_score()`.

**11 consumers :** `quality_score`, `kpis` (2 fonctions), `delta`, `stats` (2 fonctions), `exercise_history`, `export_builder`, `sharing`, `session_recap`, `restore`. Aucun ne sait (ni n'a besoin de savoir) que la valeur est derivee — ils lisent `se.success_score` tel quel.

### Impact D3 (execution_quality + reps_target orphelins)

**Producteurs actuels :** aucun (non parsés par le router).

**Seuls consumers :** `export_builder` (CSV/JSON) + `restore` (reimport). Aucun KPI, scoring, delta, ou dashboard.

---

## Compatibilite historique

- **Zero migration DB** — toutes les decisions sont applicables sur le schema existant
- **Snapshots immutables** — exercise_code_snapshot, exercise_name_snapshot, template_*_snapshot jamais modifies
- **Valeurs manuelles historiques de success_score** — preservees, coexistent avec les nouvelles valeurs derivees dans le meme range {100, 80, 50}
- **Valeurs historiques de execution_quality / reps_target** — preservees, les exports continuent de les inclure
- **Re-save d'une session historique** — bascule son success_score vers la valeur derivee (consequence assumee d'une edition volontaire)

---

## Inputs par exercice — avant / apres

| Etat | Inputs (5 work sets) | Delta |
|------|---------------------|-------|
| Avant Sb_01 | 27 | — |
| Apres Sb_01 (etat actuel) | 17 max, 15 realistement | **-37%** |

**Effet de bord positif :** la carte exercice devient tactique (que fait-on ?) plutot que reflective (comment ca s'est passe ?). Le reflectif est deporte en fin de seance (feedback session) et en re-lecture sur `/done`.

---

## Livrables produits

| Fichier | Type | Contenu |
|---------|------|---------|
| `docs/strategy/SPIGNOS_EXERCISE_FEEDBACK_RATIONALIZATION_SPEC_FINAL.md` | New | Spec FINAL 10 sections — audit, taxonomie, decisions D1-D5, matrice consumers bidirectionnelle, compat historique, impacts grandes surfaces, risques, DoD, recommandations P1-P5, synthese |
| `docs/SPRINT_Sx_01_FINAL_REPORT.md` | New | Ce rapport synthetique |

**Aucun fichier code modifie.** Spec only.

---

## Recommandations ordonnees pour le futur build

| Priorite | Action | Quand |
|----------|--------|-------|
| **P1** | Sx_02 UX mobile — s'appuyer sur §6.6 du spec FINAL comme source de verite UI | **Next sprint** |
| P2 | Ajouter un axe "adherence a la prescription" au body engineering dashboard | Apres 3 mois de donnees post-Sb_01 |
| P3 | Wording UI neutre pour success_score (legende "derive des reps vs cible") | Si remontee de confusion user |
| P4 | Mode feedback avance reactivable (reintroduire `<details>` pour execution_quality / reps_target) | Uniquement sur demande user experte explicite |
| P5 | Cleanup orphelins DB (migration destructive) | Jamais par defaut — a reconsiderer si triggers Sx_03.1 atteints |

---

## Definition of Done

| Critere | Statut |
|---------|--------|
| Doublons demontres ou refutes | ✓ (§1 audit table) |
| Primary vs derived tranche | ✓ (§2 taxonomie + §3 decisions D1-D5) |
| Modele cible lisible | ✓ (§2 + §6.6) |
| Impacts consumers documentes | ✓ (§4 matrice bidirectionnelle — 7 services cartographies) |
| Compatibilite historique traitee | ✓ (§5 — zero migration, snapshots immutables, coexistence) |
| Base prete pour Sx_02 UX mobile | ✓ (§6.6 : liste exacte des inputs, taxonomie des champs visibles/caches) |

**Spec FINAL : approuve. Pret pour Sx_02.**

---

## Bloqueurs pour Sx_02

**Aucun.** Sx_02 peut designer le flux focus-exercice en utilisant le §6.6 comme cahier des charges UI. Les questions structurelles (`success_score` visible ? orphelins visibles ? muscle_sensation position ?) sont toutes tranchees dans ce spec FINAL et ne sont pas a reouvrir.

---

## Synthese executive (4 lignes)

- Signal exercice post-Sb_01 : **7 champs primaires** + **1 derive** (success_score) + **2 orphelins preserves** (execution_quality, reps_target).
- Taxonomie : Performance mecanique / Qualite technique (derivee) / Ressenti physiologique (subjectif).
- Zero migration, zero breaking change, historique preserve.
- Base validee pour enchainer Sx_02.
