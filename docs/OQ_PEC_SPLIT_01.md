# OQ_PEC_SPLIT_01 — partition claviculaire / sternocostale du pectoral

**Statut : `DOCUMENTED — NOT BUILT`**
Ouverte par `Sb_BODYMAP_FRAME_ATLAS_01` sur décision architecte. Aucun code n'a
été écrit pour cette question, volontairement.

---

## La question

Le grand pectoral est aujourd'hui **une seule zone métier** (`pecs`) et **une
seule surface** dans la plaque `muscle_focus_plate_chest.svg`. Or la distinction
entre chef **claviculaire** (haut) et chef **sternocostal** (bas) porte une
décision d'entraînement réelle : le sens de l'inclinaison du banc.

Faut-il modéliser cette partition ?

## La décision prise

**Non — pas comme zone métier.** `pecs` reste une zone unique.

La distinction peut être portée par :

- du **texte pédagogique** (déjà le cas : la carte « Pectoraux — face » énonce
  explicitement sa limite honnête, « aucune sous-division … n'est représentée ») ;
- un futur **cadre `profile`**, qui montrerait l'angle des deux chefs sans créer
  de zone — un cadre est un point de vue, jamais une zone.

## Pourquoi ce n'est pas un simple lot de contenu

Ajouter `pec_clavicular` / `pec_sternal` à la taxonomie ne coûte pas une ligne :
les onze zones sont lues par au moins cinq consommateurs, dont un intouchable.

| Consommateur | Effet d'une douzième zone |
|---|---|
| `ZONE_VOLUME_TARGET` | il faut répartir la cible hebdomadaire de 16 séries entre deux zones — arbitrage produit, pas technique |
| `RADAR_AXES` | l'axe `pecs` devrait agréger deux zones au lieu d'une |
| `slot_intent.primary_zone` | les créneaux de programme existants désignent `pecs` |
| `muscle_mapping` (exercices → zones) | chaque exercice de poussée doit être re-qualifié |
| **`recommendation.py`** | **NON MODIFIABLE** — contient une table de zones et un mapping `push` |

La dernière ligne est bloquante : `recommendation.py` référence `pecs` et ne peut
pas être modifié. Toute partition exigerait soit une dérogation explicite, soit
une couche d'agrégation qui présenterait deux zones au visuel et une seule au
moteur — c'est-à-dire exactement l'incohérence que la règle de gouvernance
interdit.

## La règle qui tranche

> Le modèle métier gouverne le visuel. Le visuel ne crée pas de zone.

Une plaque plus fine que le modèle est un fait acceptable : la plaque épaules
contient des surfaces `*-delt-anterior` sans qu'il existe de zone `delt_ant`
(décision Option A, même sprint). La finesse graphique n'oblige pas la finesse
métier.

## Ce qu'il faudrait pour rouvrir

1. Une **décision produit** sur la répartition du volume hebdomadaire.
2. Une **dérogation explicite** sur `recommendation.py`, ou une stratégie
   d'agrégation validée.
3. Une **géométrie produite** : la partition n'existe dans aucune plaque
   aujourd'hui, et le pipeline vit dans le workspace opérateur externe.

Tant que ces trois éléments ne sont pas réunis, la question reste documentée et
non construite. Les gardes `test_a2_a3_*` de
`tests/test_bodymap_frame_atlas.py` échouent si un code de zone interdit
apparaît — y compris par inadvertance.
