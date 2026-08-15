# SPRINT Sb_BODYZONE_CALF_PRESS_ADJUDICATION_01 — une correction exacte (RAPPORT)

**Train :** `AUREN_RELEASE_READINESS_01`, tranche 1/3 ·
**Base canonique :** `0ca6ee3` · **Branche :** `sb/bodyzone-calf-press-adjudication-01`

---

## 1. La contradiction, et le seam qui existait déjà

« Calf press leg press » était classé :

| Source | Zone |
|---|---|
| EKB (`zone_primary`) | `calves` |
| `exercise_properties.json` (`muscle_group`) | `calves` |
| classifieur de noms canonique | **`quads`** |

Le classifieur gagnait, donc `SetContributionPolicy` créditait les
quadriceps pour un exercice de mollets. Signalé en
`Sb_SLOT_INTENT_COVERAGE_01`, rendu **mesurable** par
`Sb_SET_CONTRIBUTION_POLICY_01`, adjugé ici.

**Cause mécanique** : le classifieur parcourt une liste **ordonnée** ; le groupe
`quads` contient « leg press » et gagne avant que le groupe `calves` ne soit
atteint. Exactement l'artefact des deux corrections historiques déjà présentes.

**Le seam existait** : `body_zone_source.KNOWN_MAPPING_CORRECTIONS`, avec sa
précédence documentée *correction revue → `ExerciseMuscleMapping` → classifieur*.
Une entrée y a été ajoutée. **Aucun second moteur de correspondance**, aucune
règle générique déplacée.

---

## 2. Ce qui ne devait pas bouger — et n'a pas bougé

**Diff de correspondance sur les 105 exercices canoniques : 1 seul changement.**

```
Calf press leg press
  avant : quads   (substring_fallback)
  après : calves  (reviewed_correction)
```

Aucun ajout, aucune suppression, aucun autre déplacement.

| Contrôle collatéral | Résultat |
|---|---|
| `Leg Press (pieds bas)` / `(pieds bas, serrés)` / `(pieds hauts, écartés)` | **quads**, inchangés |
| Exercices de mollets canoniques (4) | **calves**, inchangés |
| Classifieur générique lui-même | **intact** — un test vérifie qu'il répond toujours `quads` |
| Matrice de substitution N1/N2/N3 (69 exercices) | **0 changement** |
| `mapping_rows` / seed | cohérent — la correction est déjà appliquée à la source |

Le tiroir de substitution ne pouvait pas bouger : il lit
`exercise_properties.json`, pas les zones canoniques. Vérifié plutôt que
supposé.

---

## 3. Impact BEFORE → AFTER, mesuré honnêtement

**Sur la contribution de l'exercice** — la correction fait ce qu'elle doit :

| | Zone créditée | 4 séries physiques |
|---|---|---|
| Avant | `quads` | 4 effectives aux quadriceps |
| Après | `calves` | 4 effectives aux mollets |

**Sur la fixture canonique cadence 4 : aucun changement.** Ni les compteurs, ni
la couverture, ni le total physique (96).

La raison est simple et vaut d'être dite plutôt que masquée : **l'allocateur ne
sélectionne pas cet exercice**. Il retient « Mollets assis machine » pour les
mollets et réutilise cette identité d'une séance à l'autre (stabilité des
identités, tranche 3 du train précédent). « Calf press leg press » reste un
candidat de repli.

La correction prendra effet dès qu'il sera retenu — restriction de matériel
excluant la machine assise, besoin d'une seconde identité mollets, ou catalogue
élargi. **Exhiber un gain de couverture ici serait inventer un effet qui
n'existe pas sur cette fixture.**

Conformément au brief, **rien d'autre n'a été ajusté** en réaction aux
compteurs.

---

## 4. Langage

L'entrée de correction cite ses preuves — deux sources curées contre un
artefact de liste ordonnée — et qualifie explicitement la décision
d'**attribution de programmation**. Aucun pourcentage, aucune mention EMG,
aucune revendication d'activation. Un test interdit ces termes dans la preuve.

> Correction de rédaction : ma première version disait « no EMG claim ». Un
> démenti met malgré tout le cadre physiologique sous les yeux du lecteur — le
> test l'a refusé, à raison. Reformulé en positif.

---

## 5. Tests — 13 dédiés

Résolution vers `calves` par le chemin `reviewed_correction` · preuve enregistrée
et citant ses deux sources · contribution créditant `calves` et **plus** `quads` ·
**diff complet sur 105 exercices avec liste attendue exacte** (les deux
corrections historiques + la nôtre, rien d'autre — sinon HARD STOP) · les trois
presses à cuisses ordinaires restent `quads` · le classifieur générique n'a pas
été réécrit · les exercices de mollets restent `calves` · tiroir de substitution
inchangé · aucune revendication scientifique · seed cohérent · constat honnête
que le planificateur ne sélectionne pas cet exercice.

Un test existant mis à jour : `test_the_calf_press_miscredit_is_pinned`
surveillait la contradiction ; il surveille désormais sa **résolution**, et
vérifie au passage que la presse à cuisses ordinaire n'a pas suivi.

## Verdict

Une contradiction connue de longue date est résolue **au bon endroit** : le seam
de corrections revues, prévu exactement pour les artefacts de liste ordonnée,
avec sa preuve écrite.

Le diff complet sur le référentiel montre **un seul exercice déplacé**. C'était
le vrai risque du sprint, et il est mesuré, pas supposé.

**L'effet sur le plan actuel est nul**, parce que l'allocateur ne retient pas cet
exercice — dit franchement plutôt que déguisé en amélioration.

---

## Closeout (post-merge)

| | |
|---|---|
| PR | **#101** — `--merge --match-head-commit`, **sans** squash / `--admin` / force |
| Build | `87df204` — **vert au premier passage**, aucun correctif |
| Merge | **`fa62329`** |
| Gate Sonar | **`OK`** — 0 smell, 0 bug, 0 vulnérabilité |
| Threads / Gitar | **0 / 0** |
| Tests | full sweep local **4 309** |

### Capacité CI — **HEALTHY**

| | Shard A | Shard B |
|---|---|---|
| min MemAvailable | **5 182 Mo** | **5 028 Mo** |
| min SwapFree | 3 071 Mo — **jamais entamé** | 3 071 Mo — **jamais entamé** |

Cinquième tranche consécutive au-dessus de 5 Go sur les deux shards.
