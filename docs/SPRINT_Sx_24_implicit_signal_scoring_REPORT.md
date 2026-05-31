# Sprint Sx_24 Spec Report — Implicit Signal Scoring + Checkbox Deprecation

**Date :** 2026-05-31
**Type :** SPEC ONLY — unique spec couvrant N9 (checkbox) + N10 (scoring implicite).
**Prérequis :** Sb_22a.next2 livré (atlas suit le réalisé).
**Successeur build :** Sb_24 (lotté en 8 sous-sprints, ~19 h cumulées).

---

## 1. Résumé exécutif

Sx_24 livre **une seule spec système** qui ferme deux retours dogfooding convergents (N9 + N10) en posant un **modèle de signal à 3 couches** :

| Couche | Définition courte | Recalcul rétroactif |
|---|---|---|
| `Saisi` | Valeur fournie par l'utilisateur | ❌ jamais |
| `Dérivé` | Agrégation déterministe de Saisis | ✅ libre |
| `Implicite` | Estimation par règle d'inférence d'effort/intent | ❌ **figé à la complétion** |

**Contrats durs verrouillés** (selon arbitrages Q1-Q4) :
- Q1 = **C** : labels Implicites visibles ET intégrés au scoring, mais **pas dans la carte active** (review / done / coach report / hints uniquement)
- Q2 = **A V1.1** : périmètre intra-exercice uniquement
- Q3 = **fusion** : vide = non fait, sans distinction skip volontaire (limitation documentée)
- Q4 = **historique figé** : mécanisme `scoring_version` sur `workout_sessions`, formule V1 préservée éternellement pour les sessions pré-Sb_24

Aucun recalcul rétroactif, aucune `UPDATE` rétroactive sur l'historique — **stabilité produit garantie**.

## 2. Fichiers créés

| Fichier | Type | Cible |
|---|---|---|
| `docs/strategy/SPIGNOS_IMPLICIT_SIGNAL_SCORING_SPEC_v1.md` | New | Spec complète (sections A→N) |
| `docs/SPRINT_Sx_24_implicit_signal_scoring_REPORT.md` | New | Ce rapport |

**0 ligne code applicatif touchée.** Implémentation = Sb_24 (8 lots, ~19 h).

## 3. Modèle livré

### 3.1 — 5 labels Implicites intra-exo détectables

| Label | Condition (sur ≥3 work sets) | Contribution scoring V2 |
|---|---|---|
| `reserve_probable` | (w↑ ou =) ET (r↑ ou =) sur tous sets | 30 |
| `incoherent` | Aucun pattern net | 50 |
| `pyramidal_ascendant` | w strictement croissant + r constant ou ↓ | 70 |
| `pyramidal_descendant` | w strictement décroissant + r constant ou ↑ | 75 |
| `trajectoire_coherente` | w constant + r décroissant | 90 |

Pondération scoring V2 : `w_implicit = 0.25`.

### 3.2 — Dépréciation checkbox `fait`

- Nouvelles sessions : `completed = (weight_kg is not None) OR (reps is not None)`, dérivé côté serveur au POST.
- Sessions historiques : `completed` reste figé tel que saisi à T0.
- Mécanisme de discrimination : `workout_sessions.scoring_version` (1 = historique, 2 = post-Sb_24).

### 3.3 — Surfaces UI (sobre, Q1=C)

| Surface | Affichage label |
|---|---|
| Carte active | ❌ |
| `/sessions/{id}/done` review | ✅ pastilles par exercice |
| Coach Report | ✅ agrégat 30j taggé `Inféré` |
| Hints (Sb_08) | ✅ renforcement éducatif |
| Leaderboard / public profile | ❌ privacy |

## 4. Décisions clés

| Décision | Justification |
|---|---|
| `scoring_version` sur `workout_sessions` | Permet la coexistence V1/V2 sans recalcul rétroactif (Q4). Code plus complexe qu'un recalcul global mais c'est le prix de la stabilité historique. |
| Label persisté à la complétion | Évite la dérive : si on raffine les règles, les anciennes sessions gardent leur classification. Conforme Q4. |
| 5 labels (pas plus) | Lisible. Si la palette doit s'étendre, on incrémente `scoring_version`. |
| Pondération `w_implicit = 0.25` | Calibrée à dire d'expert. Audit empirique en Sb_24.8 avant merge. |
| Pas de RPE numérique V1 | Demande un modèle calibré + data validée. V2 si pertinent. |

## 5. Lotissement Sb_24 build (8 sous-sprints, ~19 h)

| Lot | Sujet | h |
|---|---|---|
| Sb_24.1 | Migration BD (ADD COLUMN sans UPDATE) | 2 |
| Sb_24.2 | `services/implicit_signal.py` + 8-10 tests | 3 |
| Sb_24.3 | Hook complétion (calcul + persist) | 2 |
| Sb_24.4 | Dépréciation checkbox (form + handler) | 3 |
| Sb_24.5 | `quality_score.py` V2 branché sur `scoring_version` | 3 |
| Sb_24.6 | UI review pastilles + score ventilé | 3 |
| Sb_24.7 | Coach Report étendu (bloc Implicite) | 2 |
| Sb_24.8 | Sprint report + audit empirique V1/V2 | 1 |

Sb_24.1 ouvre, Sb_24.8 ferme. Lots Sb_24.2/4 peuvent partir en parallèle de Sb_24.3 si besoin.

## 6. Backlog post-Sb_24

- **Sb_24.next1** — V1.2 cross-exo (fatigue inter-mouvement même zone) — déjà cadré Q2-B
- **Sb_24.next2** — Affichage label sur historique liste séances
- **Sb_24.next3** — RPE numérique 1-10 estimé (V2)
- **Sb_24.next4** — Swipe-left "skip volontaire" si fusion §E.3 cause des frictions

## 7. Acceptance criteria Sx_24

- [x] Modèle 3 couches `Saisi` / `Dérivé` / `Implicite` documenté (§C)
- [x] 5 labels intra-exo définis avec contributions scoring (§D, §F)
- [x] Dépréciation checkbox détaillée avec mécanisme de gating (§E)
- [x] Contrat de stabilité historique verrouillé (§H, `scoring_version`)
- [x] Surfaces UI cadrées sobrement (§G)
- [x] Acceptance criteria build (§I)
- [x] Lotissement Sb_24 chiffré (§K)
- [x] Risques + mitigations (§L)
- [x] Limites assumées + cas limites (§J)

## 8. Verdict

**Sx_24 prête.** Spec interne autonome. Sb_24 peut s'ouvrir sur le lot Sb_24.1 dès validation humaine.

**Recommandation prochain sprint** : tu valides la spec Sx_24, j'ouvre Sb_24.1 (migration BD ADD COLUMN — 2 h, faible risque, débloque tous les autres lots). Ensuite Sb_24.2 (service `implicit_signal.py`) qui est l'unité testable de la spec sans toucher au reste de l'app.

OU si tu préfères, j'enchaîne directement sur **Sx_25 — Coach Report v2 LLM narratif encadré**, et on revient sur Sb_24 build après. Les deux sont indépendants.
