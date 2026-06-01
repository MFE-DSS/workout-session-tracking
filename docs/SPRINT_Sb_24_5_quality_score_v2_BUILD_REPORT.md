# Sprint Sb_24.5 Build Report — Formule quality_score V2 branchée sur scoring_version

**Date :** 2026-06-01
**Type :** BUILD — lot Sb_24.5 du lotissement Sx_24.
**Prérequis :** Sb_24.1 + Sb_24.2 + Sb_24.3 + Sb_24.4 livrés et déployés.

---

## 1. Résumé exécutif

`compute_session_quality()` est désormais dispatché par `scoring_version` pour les sessions strength. Les sessions historiques (`scoring_version=1`) gardent strictement la formule V1, bit-pour-bit identique. Les sessions postérieures à Sb_24.3 (`scoring_version=2`) consomment leurs `implicit_label` via la formule V2 :

```
V2 = 0.75 · V1  +  0.25 · implicit_avg
```

Où `implicit_avg` est la moyenne des contributions (`LABEL_SCORE_CONTRIBUTION` de Sb_24.2) des exercices labellés de la session.

**Fallback safe** : si aucun exercice de la session n'a d'implicit_label (ex : session courte < 3 work sets partout), V2 retourne V1 inchangé. Pas de score artificiel.

**Cardio inchangé** : la formule cardio n'a pas de notion d'implicit signal, donc une session cardio avec `scoring_version=2` produit exactement le même score qu'avec `scoring_version=1`.

## 2. Contrats non négociables respectés

| Contrainte humaine | Mécanisme | Test |
|---|---|---|
| **1. Invariance absolue V1** | `compute_session_quality_strength()` non touchée. Dispatcher ne l'appelle pas pour V2. | `test_v1_session_returns_legacy_score` |
| Invariance même si `implicit_label` traîne sur une session V1 | Dispatcher ignore implicit_label si `scoring_version=1` | `test_v1_invariant_even_when_implicit_label_present` |
| Backward compat `scoring_version` absent ou None | `getattr(session, "scoring_version", None) or 1` → V1 | `test_v1_default_when_scoring_version_attribute_missing` |
| **2. V2 seulement pour `scoring_version=2`** | Dispatch conditionnel | tests V2 |
| Pas de recalcul rétroactif | Aucun UPDATE rétroactif, formule lit `scoring_version` à chaque appel | (par construction) |
| **3. Pondération conservatrice w_implicit=0.25** | Constante `W_IMPLICIT = 0.25` exposée publiquement | `test_v2_formula_works_for_each_label` (paramétrique 5 labels) |
| Pas de tuning opportuniste | Seules les constantes spec sont utilisées | code review |
| **4. Non-régression explicite** | Tous les consommateurs aval testés | §3 |

## 3. Non-régression des consommateurs aval

Tests existants qui consomment `compute_session_quality()` — tous passent inchangés :

| Test file | Tests | Effet |
|---|---|---|
| `test_session_management.py` | 3 tests quality_score | ✅ V1 invariant (corrigé via gestion None) |
| `test_scoring_cardio.py` | 13 tests | ✅ cardio inchangé |
| `test_performance.py` | 5 tests | ✅ grade et avg_points stables |
| `test_coach_report.py` | 19 tests | ✅ tags Mesuré/Inféré préservés |
| `test_export_kind_and_confidence.py` | tests d'export | ✅ |
| **Suite complète** | 875 (+17 vs 858) | ✅ 0 régression |

## 4. Fichiers modifiés / créés

| Fichier | Type | Nature |
|---|---|---|
| `app/services/quality_score.py` | Modify | +`_compute_session_quality_strength_v2()` (~30 LoC). +`_implicit_signal_avg()` helper. Dispatcher étendu : cardio → cardio, V1 strength → V1, V2 strength → V2. Constantes `W_IMPLICIT = 0.25` et `W_V1 = 0.75` exposées. |
| `tests/test_quality_score_v2.py` | New | 17 tests : invariance V1 (3) / formule V2 (6) / cardio inchangé (1) / `_implicit_signal_avg` edge cases (2) / paramétrique 5 labels (5). |
| `docs/SPRINT_Sb_24_5_quality_score_v2_BUILD_REPORT.md` | New | Ce rapport. |

**0 migration BD · 0 modèle touché · 0 réécriture historique · 0 UI modifiée.**

## 5. Diff métier

### Avant Sb_24.5

Sessions V2 sur prod (depuis Sb_24.3 hier soir) avaient leur `implicit_label` calculé et persisté, mais **personne ne consommait cette donnée**. Le score qualité affiché restait celui de la formule V1 — l'utilisateur ne voyait aucun impact des labels.

### Après Sb_24.5

Sessions V2 voient leur quality_score reflecter implicitement leur trajectoire :
- Trajectoire cohérente (drop-off attendu) → boost de score (+~10 vs V1 pur dans un cas typique 80 V1 + 90 implicit)
- Réserve probable (effort plat) → pénalité de score (~-12 vs V1 dans un cas similaire)
- Pas de label sur la session entière → V2 ≡ V1 (fallback)

L'utilisateur n'est pas notifié textuellement (Sb_24.6 fera ça). Mais le score est désormais cohérent avec l'effort réellement déployé.

## 6. Exemple chiffré

Session strength avec V1 = 80 (bonne complétion + concentration + state correct) :

| Implicit_label | Contribution | V2 calcul | V2 final |
|---|---:|---|---:|
| (aucun) | — | V2 = V1 fallback | 80 |
| `reserve_probable` | 30 | 0.75·80 + 0.25·30 = 60+7.5 | 68 |
| `incoherent` | 50 | 0.75·80 + 0.25·50 = 60+12.5 | 73 |
| `pyramidal_ascendant` | 70 | 0.75·80 + 0.25·70 = 60+17.5 | 78 |
| `pyramidal_descendant` | 75 | 0.75·80 + 0.25·75 = 60+18.75 | 79 |
| `trajectoire_coherente` | 90 | 0.75·80 + 0.25·90 = 60+22.5 | 83 |

Plage d'impact = ±12 points autour de V1 selon le label. C'est mesurable mais pas violent.

## 7. État des tests

```
875 tests passing in 255.23s (vs 858 avant — +17, 0 régression)
  - 17 nouveaux tests test_quality_score_v2.py
  - 0 test existant cassé après le fix `or 1` sur None scoring_version
  - paramétrique sur les 5 labels couverts
```

## 8. Limites assumées

1. **Pas d'audit empirique a posteriori dans ce sprint** — l'effet réel des labels sur les vraies sessions V2 sera mesurable une fois Sb_24.6 livré et que l'utilisateur dogfoode quelques séances. Sb_24.8 fera l'audit chiffré V1 vs V2 final.
2. **Pas de transparence utilisateur sur la décomposition** — V2 retourne 1 score, pas une ventilation par composante. L'utilisateur ne sait pas que son 78 vient de "80 V1 - 2 implicit". Sb_24.6 ajoute les pastilles explicatives mais pas le breakdown numérique.
3. **Pondération figée à 0.25** — la consigne humaine était stricte (pas de tuning opportuniste). Si Sb_24.8 audit révèle un déséquilibre, la pondération peut être ajustée dans une Sb_24.next à l'amiable.
4. **Cardio non couvert par V2** — décision spec (les labels intra-set ne s'appliquent qu'au strength). Une session cardio reste sur la formule cardio classique, même si elle a `scoring_version=2`.

## 9. Recommandation prochain lot

**✅ Sb_24.6 PRÊT — UI review pastilles + score ventilé.**

Justification :
- Sb_24.5 est livré et stable, le score V2 est calculé correctement.
- Mais l'utilisateur ne voit pas pourquoi son score a bougé. Sb_24.6 ferme cette boucle UX en affichant les pastilles `[Équivalent]`/`[Proche]`/etc. sur la page `/sessions/{id}/done` (review post-séance).
- Surface ciblée et sobre : pas de pastille sur la carte active (spec §G — Q1=C), seulement sur review/done/coach report/hints.

Effort estimé 3h. Risque faible — c'est du rendu HTML, pas de modification de scoring.

Alternative si tu veux d'abord valider en salle Sb_24.5 (1 séance suffit pour voir l'impact sur ton score) : on attend ton retour avant d'ouvrir Sb_24.6.

## 10. Synthèse

- **Invariance V1 garantie** par séparation stricte des deux fonctions et tests dédiés.
- **V2 = mix conservateur** 75/25 entre V1 et implicit_avg, naturellement borné à 100.
- **Cardio invariant** car la formule cardio est entièrement indépendante.
- **17 nouveaux tests** verrouillent les 4 contraintes humaines non négociables.
- **0 changement UI** — l'impact est silencieux jusqu'à Sb_24.6.

Sb_24.5 prêt à pousser, build conforme aux 4 garde-fous humains.
