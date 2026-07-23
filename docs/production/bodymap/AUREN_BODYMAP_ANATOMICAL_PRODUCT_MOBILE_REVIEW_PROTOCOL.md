# AUREN — BodyMap Anatomical / Product / Mobile Review Protocol

**Cycle** : `Sx_ASSET_03`. Protocoles **reproductibles** de revue du futur master (exécutés à
`OPERATOR_ASSET_03.1` / `Sb_ASSET_03.2`). Cette spec **ne réalise aucune revue**.

---

## 0. Gate humain révisé (amendement 2026-07-23 — SOURCE-REUSE-FIRST)

```
MULTI-SOURCE ANATOMICAL CONSISTENCY REVIEW: REQUIRED
PROFESSIONAL ANATOMICAL REVIEW: NOT CLAIMED / OPTIONAL BEFORE FINAL INTEGRATION DECISION
NAMED ILLUSTRATOR: NO LONGER A PRECONDITION
```

Pour un master **dérivé de sources ouvertes** (`Sb_ASSET_03.1`), la revue professionnelle préalable est
**remplacée** par une **revue de cohérence multi-sources** : chaque zone est confrontée à **au moins deux
sources indépendantes** parmi Servier Medical Art (CC BY 4.0), AnatomyTOOL (ressources CC0/CC BY qualifiées)
et OpenStax **1ʳᵉ édition** (CC BY 4.0). Verdict par zone : `PASS / ADJUST / BLOCKED / NOT APPLICABLE`.

**Ce que cette revue n'est pas** : une validation médicale, une preuve clinique, une garantie d'exactitude.
Elle constate une **cohérence de représentation** entre sources concordantes. La revue professionnelle reste
**possible et recommandée avant la décision d'intégration finale** — elle n'est simplement **pas revendiquée**
ni exigée pour produire le prototype.

**Indépendance des sources** : le SVG Wikimedia `Muscles front and back.svg` étant **dérivé d'OpenStax**, il
ne compte **pas** comme second avis face à OpenStax. Z-Anatomy étant **dérivé de BodyParts3D**, il ne compte
pas comme second avis face à la source primaire.

Le §1 ci-dessous reste applicable **tel quel** si une revue professionnelle est effectivement conduite.

## 1. Revue anatomique (professionnelle — applicable si conduite)
### Compétence du relecteur
Compétence **documentée** en anatomie / biomécanique / illustration anatomique / kinésithérapie (ou domaine
voisin pertinent). **Pas** de titre médical précis exigé si non juridiquement nécessaire, mais **compétence
prouvée**. La revue anatomique valide la **cohérence de représentation** — elle **ne transforme pas** l'asset
en dispositif médical / outil diagnostique / mesure EMG / preuve clinique.

### Verdict par zone (les 11) : `PASS` · `ADJUST` · `BLOCKED` · `NOT APPLICABLE`
Vérifier :
- présence des **11 zones** ; aucune inversion face/dos ; aucune zone absurde ;
- cohérence des limites · gauche/droite · face/dos ; proportions ;
- **absence de précision excessive** ; **agrégats honnêtes** (`upper_back`, `posterior`) ;
- **aucune apparence d'activation réelle** ; **aucune connotation pathologique** ;
- absence d'organes / fibres / insertions détaillées ;
- lisibilité des zones ; compatibilité avec les **IDs stables**.

## 2. Revue produit & mobile (grille reproductible)
### À 360 px
face + dos visibles · aucune zone rognée · labels adjacents lisibles · **aucun scroll horizontal imposé par
le BodyMap** · densité compatible avec la carte active.
### À 60 / 80 / 120 px
silhouette reconnaissable · `primary` identifiable en < 1 s · `secondary` visible sans concurrencer `primary`
· `neutral` compréhensible · `unknown` neutre · `biceps`/`triceps` distinguables (si la surface le permet) ·
`lats`/`upper_back` distinguables (dos) · `quads`/`posterior`/`calves` distinguables (vues pertinentes).
### Logging (non-régression UX)
Le BodyMap ne doit **pas** : repousser la console de saisie · augmenter le temps de logging · masquer
poids/reps · transformer la carte en atlas · créer une interaction obligatoire.
### Verdicts produit/mobile : `ACCEPTED` · `ADJUST` · `REJECTED` · `BLOCKED`

## 3. Matrice de previews attendue (bornée — preuves de revue, PAS des assets runtime)
L'opérateur produit **exactement** ces previews :
| # | Preview | Nb |
|---|---|---|
| 1 | `neutral` front + back | 2 |
| 2 | `unknown` front + back (neutre) | 2 |
| 3 | chaque zone en `primary` (11 zones) | 11 |
| 4 | cas `primary + secondary` représentatifs (sélection **bornée à 6**) | 6 |
| 5 | les **6 macros compactes** | 6 |
| 6 | `disabled` | 1 |
| 7 | rendu **2 vues à 360 px** | 1 |
| 8 | rendu à **60 px** | 1 |
| 9 | rendu à **80 px** | 1 |
| 10 | rendu à **120 px** | 1 |
| | **TOTAL** | **32 previews** |

Les cas §4 sont **plafonnés à 6** pour éviter l'explosion combinatoire (11 zones × 11 secondaires = 110 →
borné à 6 cas représentatifs choisis par le responsable produit). Les previews sont des **preuves de revue**,
**pas** des assets runtime, et **n'entrent pas dans `app/static/`**.

## 4. Statut global
Aucun verdict de revue ne fait passer le master en `approved` / `runtime-integrated` : après revue, restent
l'intake technique (`Sb_ASSET_03.2`), la provenance/PI, la revue juridique et l'intégration séparée
(`Sb_ASSET_04.1`, après gate).
