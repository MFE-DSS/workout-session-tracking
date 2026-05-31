# Sprint Sb_22a.next Build Report — Lower subzone fix

**Date :** 2026-05-31
**Type :** BUILD CORRECTIF CIBLÉ — ferme la classe "faux N1 zone-lower" identifiée immédiatement après Sb_22a.
**Prérequis :** Sb_22a livré (`56b090f`, deployé sur prod `prod/2026-05-31-1407`).
**Motif d'ouverture :** verdict humain explicite — 1 faux N1 confirmé déterministe sur `Adduction assise` (leg extensions / leg curls remontés en `Équivalent`) → règle "1+ faux N1 → NO-GO Sb_22b" appliquée.
**Successeur :** Sb_22b — gating sur ce rapport.

---

## 1. Objectif du sprint

Corriger les faux `N1 Équivalent` produits par la granularité insuffisante de `zone_primary=lower` dans le graphe de substitution. Le fix est volontairement **court, ciblé et défensif** :

- introduire une sous-zone `muscle_group` au niveau du registre `exercise_properties.json`
- l'imposer sur `lower` uniquement (V1.1 scope strict)
- enrichir `compute_proximity()` et `_classify_suggestion()` pour bloquer N1 si la sous-zone diffère
- **ne pas** rouvrir le chantier substitution global

## 2. Fichiers modifiés

| Fichier | Type | Nature |
|---|---|---|
| `data/exercise_properties.json` | Modify | `_version` `v1` → `v1.1` ; ajout `muscle_group` sur les 9 entrées `lower` ; doc header mis à jour. |
| `app/services/substitution.py` | Modify | `compute_proximity()` +10 si `muscle_group` identique (et les 2 non-null). `_classify_suggestion()` bloque N1 si origine a un `muscle_group` et candidat ne matche pas — sortie N2 avec rationale `autre groupe (X)`. |
| `scripts/catalog_pattern_qa.py` | Modify | Ajout enum `VALID_LOWER_MUSCLE_GROUPS` ; `_validate_entry()` hard-error si `zone_primary=lower` sans `muscle_group` valide. |
| `tests/test_substitution_tiered.py` | Modify | +7 tests Sb_22a.next : adduction N1 exclut leg ext/curl, adduction garde adducteurs en N1, leg ext apparaît en N2 avec rationale, proximité bonus muscle_group, asymétrie non-null, QA all lower entries, non-régression non-lower. |
| `docs/SPRINT_Sb_22a_next_lower_subzone_fix_BUILD_REPORT.md` | New | Ce rapport. |

**0 modification BD · 0 modèle touché · 0 réécriture historique.**

## 3. `muscle_group` ajoutés (V1.1 scope = `lower` only)

| Exercice | Avant | Après (Sb_22a.next) |
|---|---|---|
| Adduction assise | — | `adductors` |
| Adduction debout câble | — | `adductors` |
| Adduction couchée machine | — | `adductors` |
| Leg extensions assises | — | `quadriceps` |
| Leg extension câble unilatéral | — | `quadriceps` |
| Reverse Nordic | — | `quadriceps` |
| Leg curls allongé | — | `hamstrings` |
| Leg curls assis | — | `hamstrings` |
| Sliding leg curl | — | `hamstrings` |

Total 9 entrées `lower` renseignées. Aucun ajout sur `pecs` / `arms` / `shoulders` / etc. (hors scope strict V1.1).

Enum verrouillé `VALID_LOWER_MUSCLE_GROUPS = {adductors, quadriceps, hamstrings, glutes, calves}`. Le QA refuse toute autre valeur ou l'absence sur une entrée `lower` (hard error exit 1).

## 4. Nouvelles règles de classement

### 4.1 `compute_proximity()`

Composante ajoutée :

```
+ 10 si muscle_group_a == muscle_group_b   (et les deux non-null)
```

Score plafond passe de 95 à 105.

Le bonus ne s'applique **pas** si une seule des deux valeurs est null — évite de comparer un exo `lower` (avec sous-zone) à un exo `arms` (sans sous-zone), comparaison non significative.

### 4.2 `_classify_suggestion()` — bloque N1 si sous-zone différente

Règle ajoutée en tête de la classification :

```
mg_blocks_n1 = bool(origin.muscle_group) and (origin.muscle_group != candidate.muscle_group)
```

Conséquence :
- si origine a `muscle_group=adductors` et candidat a `muscle_group=quadriceps`, **impossible d'être N1** quelle que soit la coïncidence des 4 autres dimensions
- la classification retombe en N2 si `pattern_motor` identique et `proximity ≥ 50`
- ou en N3 sinon

Le rationale N2 surface la différence : `"même pattern · même équipement, autre groupe (quadriceps)"`. L'utilisateur voit immédiatement pourquoi le candidat n'est pas un équivalent.

### 4.3 Effet asymétrie — non-lower inchangé

Pour les zones autres que `lower` (où `muscle_group` est null V1.1), la règle ne s'applique pas. Le comportement Sb_22a sur Push/Pull/Shoulders reste identique. Garanti par `test_non_lower_exercise_unaffected_by_muscle_group_rule`.

## 5. Cas Adduction — avant / après

| Suggestion | Niveau Sb_22a | Niveau Sb_22a.next |
|---|---|---|
| Adduction couchée machine | N1 | **N1** (inchangé — vrai adducteur) |
| Adduction debout câble | N1 | **N1** (inchangé — vrai adducteur, badge `Proche` car équipement diffère) |
| Leg extensions assises | N1 ❌ | **N2** ✅ avec rationale `autre groupe (quadriceps)` |
| Leg curls allongé | N1 ❌ | **N2** ✅ avec rationale `autre groupe (hamstrings)` |
| Leg curls assis | N1 ❌ | **N2** ✅ avec rationale `autre groupe (hamstrings)` |
| Leg extension câble unilatéral | N2 | **N2** (inchangé — déjà N2 car équipement diffère + maintenant sous-zone diffère) |
| Reverse Nordic | N2 | **N2** (inchangé) |

**3 faux N1 corrigés**, 0 vrai N1 perdu, 0 sub utile disparue (tous restent N2 accessibles directement dans le drawer).

## 6. Non-régression sur les autres familles MVP

Vérifié sur 7 exos pivots — comptes N1/N2/N3 strictement identiques à ceux de Sb_22a `56b090f` :

| Exercice (origine) | N1 | N2 | N3 |
|---|---:|---:|---:|
| Rowing câble assis prise neutre | 4 | 2 | 4 |
| Tirage poulie haute prise large | 4 | 1 | 3 |
| Machine shoulder press | 4 | 0 | 0 |
| Chest Press machine | 0 | 5 | 0 |
| Incline Smith Press | 1 | 5 | 0 |
| Curl EZ-bar debout | 0 | 5 | 0 |
| Triceps pushdown corde | 5 | 0 | 0 |

Aucun delta. Le fix est strictement local à la zone `lower`.

## 7. État des tests

```
770 tests passing in 237.89s   (+7 vs 763, 0 régression)
  - 7 nouveaux tests Sb_22a.next dans test_substitution_tiered.py
  - 41 tests substitution au total (10 existants + 24 Sb_22a + 7 Sb_22a.next)

catalog_pattern_qa : OK exit 0 (53 exercices validés, 3 soft warnings legacy v13)
                     enforce muscle_group sur les 9 entrées lower
ruff/bandit : inchangés (advisory)
```

## 8. Matrice de couverture mise à jour (§C.4ter spec)

| Famille | Exos | ≥ 1 N1/N2 avant | ≥ 1 N1/N2 après | Δ |
|---|---:|---:|---:|---:|
| Adduction | 3 | 3 | 3 | 0 |
| Rowing horizontal | 7 | 7 | 7 | 0 |
| Tirage vertical | 7 | 7 | 7 | 0 |
| Shoulder press | 5 | 5 | 5 | 0 |
| Leg extension | 2 | 2 | 2 | 0 |
| Leg curl | 4 | 4 | 4 | 0 |
| Triceps | 5 | 5 | 5 | 0 |
| Curl biceps | 12 | 12 | 12 | 0 |
| Chest/Incline | 7 | 7 | 7 | 0 |
| **TOTAL** | **52** | **52** | **52** | **0** |
| **Couverture** | | **100 %** | **100 %** | **0 pt** |

**Couverture utile maintenue à 100 %**. Le fix ne dégrade aucun cas — il améliore strictement la pertinence des N1.

## 9. Verdict explicite

### ✅ Sb_22b PRÊT

Justification :
- Le faux N1 unique signalé (Adduction → leg ext/curl) est corrigé déterministe.
- Les vrais N1 adducteurs sont préservés.
- Aucun nouveau faux N1 introduit (vérifié par les 7 spot-checks de non-régression).
- 770 tests verts, QA OK, couverture MVP 100 % maintenue.
- Garde-fou pérenne ajouté : le QA refuse une entrée `lower` sans `muscle_group` valide → impossible de réintroduire la classe de bug en oubliant le champ.

Recommandation prochain sprint : **Sb_22b — Profile Synthesis v2** (cf spec `SPIGNOS_PROFILE_SYNTHESIS_SPEC_v2.md`).

Sb_22a.next ne ferme pas la limite plus large §9.1 de Sb_22a (les zones `pecs`/`arms`/`shoulders` restent sans sous-zone V1.1). Cette extension est volontairement reportée — pas de signal utilisateur l'exigeant aujourd'hui, et le fix actuel suffit pour la classe "lower" qui était la seule à manifester un faux N1 visible.
