# Sprint Sb_24.next.reco Build Report — Zone freshness sur N=3 dernières sessions

**Date :** 2026-06-01
**Type :** BUILD CORRECTIF CIBLÉ — ferme le bug de rotation reco signalé en dogfood.
**Prérequis :** Cycle Sx_24 livré et déployé.
**Successeur :** dogfood général reprise.

---

## 1. Résumé exécutif

Le moteur de recommandation (Sb_18 V2 antagonist) ne regardait que la **dernière** session strength pour mesurer le chevauchement de zones. Conséquence observée 3 séances d'affilée par l'utilisateur :

> push (pec/épaules) → pull (dos) → reco propose **encore** push

Cause : le push N-2 est invisible au scoring. L'antagonist binaire de la N-1 dit "push contre pull = 15 pts antagonisme parfait", sans savoir que les pecs viennent juste d'être travaillés à la N-2.

Fix : `_antagonist_bonus()` est **étendu** en `_zone_freshness_bonus()` qui regarde l'**union** des zones des **3 dernières sessions strength** avec un **gradient** au lieu d'un binaire :

```
overlap_count = nb zones du template ∩ union(zones des 3 dernières sessions)
bonus = max(MIN, BASE − STEP × overlap_count)
```

Avec `BASE=15`, `STEP=6`, `MIN=-6` :
| overlap | bonus | interprétation |
|---|---|---|
| 0 | +15 | aucun recouvrement sur 3 séances → idéal |
| 1 | +9 | recouvrement marginal (ex. delts indirects) |
| 2 | +3 | recouvrement notable |
| 3+ | −3 → −6 | retravail manifeste de zones fraîches |

## 2. Diff métier — scénario user dogfood

Reprise du cas observé : `push (N-2)` → `pull (N-1)` → reco pour N

Avant Sb_24.next.reco :

| Template | availability | antagonist (vs N-1 pull) | total ≈ |
|---|---:|---:|---:|
| push | 35 | +15 (perfect) | ≈ 50 |
| legs | 35 | +15 (perfect) | ≈ 50 |

→ Égalité → tiebreaker `display_order` favorise souvent push.

Après Sb_24.next.reco :

| Template | availability | zone-freshness (vs N-1 pull + N-2 push) | total ≈ |
|---|---:|---:|---:|
| push | 35 | **−3** (3 zones overlap pecs+delt_lat+triceps en N-2) | ≈ 32 |
| legs | 35 | **+15** (aucune zone overlap) | ≈ 50 |

→ Legs gagne franchement (+18 pts de delta) — exactement le verdict attendu.

## 3. Fichiers modifiés / créés

| Fichier | Type | Nature |
|---|---|---|
| `app/services/recommendation.py` | Modify | +constantes `RECENT_STRENGTH_SESSIONS_LOOKBACK=3`, `ZONE_FRESHNESS_BONUS_{BASE,STEP,MIN}`. +champ `recent_strength_zones_by_session` sur `Signals`. Population dans `_compute_signals()` (limite N=3 sur l'itération desc déjà existante). +`_zone_freshness_bonus()`. `_score_template()` switché sur la nouvelle fonction. L'ancien `_antagonist_bonus()` reste en place pour les explanations (phrases de motivation de la reco). |
| `tests/test_reco_zone_freshness.py` | New | 17 tests : gradient sanity (5), clamp MIN, scénarios dogfood (push-pull-push pénalisé, push-pull-legs optimal), legacy `_antagonist_bonus` préservé, paramétrique sur la formule. |
| `docs/SPRINT_Sb_24_next_reco_zone_freshness_BUILD_REPORT.md` | New | Ce rapport. |

**0 modèle touché · 0 migration BD · 0 réécriture historique.**

## 4. Contrats respectés

| Contrat | Mécanisme | Test |
|---|---|---|
| Bug push-pull-push fermé déterministe | Gradient sur union N=3 | `test_dogfood_scenario_push_pull_push_penalized` |
| Reco saine push-pull-legs reste optimale | Bonus max si 0 overlap | `test_dogfood_scenario_push_pull_legs_optimal` |
| Pas de session récente → neutre (cold-start safe) | Retour 0 si historique vide | `test_zone_freshness_returns_zero_when_no_history` |
| Clamp anti-dérive | `MIN=-6` jamais franchi | `test_zone_freshness_huge_overlap_clamped_to_min` |
| Legacy antagonist préservé pour explanations | Fonction non touchée | 4 tests legacy verts |
| Non-régression Sb_18 V2 reco | 40 tests reco existants verts | full suite |

## 5. État des tests

```
907 tests passing in 265.42s (vs 890 avant — +17, 0 régression)
  - 17 nouveaux tests test_reco_zone_freshness.py
  - 40 tests reco existants verts (tests/test_recommendation*.py)
  - aucun test de scoring/coach/quality cassé
```

## 6. Limites assumées

1. **Fenêtre en nombre de sessions, pas en jours** — N=3 quel que soit l'espacement temporel. Une séance vieille de 10 jours compte autant qu'une d'hier. Acceptable car les zones se reposent (couvert par la composante `availability`), mais conceptuellement orthogonal. Si besoin, Sb_24.next.reco.next ajouterait une décote temporelle (ex : `weight = max(0, 1 - days_since/14)`).
2. **`STEP=6` calibré à dire d'expert** — produit -3 pts pour 3 zones partagées. Si la pondération doit être tunée, c'est une constante au-dessus du fichier facilement modifiable. Audit empirique via les retours user après quelques séances.
3. **Pas de seuils par zone** — la pénalité est uniforme. On pourrait imaginer pénaliser plus durement les zones lourdes (quads, posterior) qui demandent plus de récup. Hors scope ce sprint.
4. **L'ancien `_antagonist_bonus()` est dupliqué (kept pour explanations)** — petite dette technique. Si on veut nettoyer, on harmonisera les phrases d'explanation avec le nouveau gradient (Sb_24.next.reco.cleanup).
5. **Pas de feedback utilisateur "j'aurais voulu push quand même"** — V1, le user accepte ou rejette via clic alternative. Pas d'apprentissage adaptatif.

## 7. Synthèse

- 1 fonction ajoutée (gradient sur 3 sessions), 1 ligne de scoring switchée.
- 17 tests verrouillent le contrat avant/après et le scénario dogfood précis.
- 0 régression sur les 40 tests reco existants.
- Plage d'impact : push-pull-push gagne ~18 pts de pénalité vs legs. Le tiebreaker structurel disparaît.

Bug terrain fermé. Prochaine reco devrait proposer legs naturellement après push-pull. À toi de valider en salle au prochain choix.

## 8. Recommandation

Tu peux valider en cliquant juste `/` (accueil) après ton historique récent (push + pull) : la reco doit te proposer un template lower-body (lower-quad-bias, lower-posterior-bias, legs-a, legs-b) en top-1, et reléguer push-a/push-b en alternative basse ou hors top.

Si la sortie te paraît cohérente, le cycle Sx_24 + ce fix peuvent être considérés comme la première itération complète et empiriquement validée.
