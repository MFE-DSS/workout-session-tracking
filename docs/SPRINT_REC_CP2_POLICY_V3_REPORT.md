# REC-CP2 — politique V3 à précédence explicite, et comparaison en ombre

**Statut** : livré · **Branche** : `sb/rec-cp2-policy` · **Base** : `REC-CP1`

⚠ **V3 NE PILOTE RIEN.** MISSION, la création de séance et toute surface
utilisateur lisent encore V2. Une garde de ce sprint vérifie qu'aucun fichier
hors du banc de mesure ne référence `recommendation_v3`. La promotion passe par
la porte du `§12`.

---

## 1. L'instrument d'abord — parce qu'il était faux

`REC-CP1` a livré un corpus qui **ne pouvait pas** juger une politique fondée
sur la couverture. Mesuré avant d'écrire une ligne de V3 :

```
legs-a : 7 exercices, 2 semés
         ignorés → Leg extensions · Leg curls · Adduction
                   · Relevés mollets · Roulette abdominale
exposition 14 j du corpus :
         biceps 4 · lats 6 · pecs 12 · posterior 6 · quads 6
         triceps 4 · upper_back 6
```

**Sept zones sur onze.** `core`, `calves`, `delt_lat`, `delt_post` n'étaient
jamais servies, quoi que fasse l'utilisateur simulé. Or `liss-abs` a pour unique
zone `core` : il était structurellement, et à jamais, « la zone la plus
délaissée ».

Une séance terminée pose les exercices de son gabarit. Tronquer à deux, c'était
**fabriquer un déficit permanent puis le mesurer**.

Correction : `semer_seance` pose désormais la séance entière. La garde CP1 qui
épinglait « exactement deux exercices » a rougi — c'est ainsi qu'elle devait
fonctionner — et le changement est déclaré dans son corps.

**V2 est inchangé par cette correction.** Son épinglage en boucle ouverte est
donc robuste, et le diagnostic de `REC-CP1` tient.

---

## 2. ⚠ La découverte qui corrige `REC-CP1` : la boucle fermée

Les dix-sept trajectoires sont en **boucle ouverte** — l'historique est écrit
d'avance et le conseil n'est jamais suivi. J'ai ajouté un mode **boucle
fermée** : chaque recommandation est exécutée avant la suivante.

J'attendais que V2 s'y bloque aussi. **Il ne s'y bloque pas du tout.**

```
boucle fermée, 10 décisions suivies
v2 : série max 1 · concentration 0,40 · tranché par le catalogue 0,40
v3 : série max 1 · concentration 0,20 · tranché par le catalogue 0,10
```

Six gabarits différents pour V2 sur dix décisions. Le blocage mesuré en boucle
ouverte était donc, pour une large part, l'effet d'un corpus qui **ne suit
jamais le conseil** : un gabarit recommandé mais jamais effectué reste
éternellement « jamais fait », donc éternellement le plus ancien au départage.

Les deux modes restent vrais, et c'est leur **écart** qui énonce le défaut :

| | comportement de V2 |
|---|---|
| conseil **suivi** | tourne correctement, six gabarits sur dix décisions |
| conseil **décliné** | répète le même conseil indéfiniment |

> V2 n'est pas « épinglé ». **Il n'a aucune notion d'avoir déjà donné un conseil
> que l'utilisateur a écarté.** C'est une caractérisation plus étroite que celle
> de `REC-CP1`, et plus juste.

Et la boucle fermée confirme la mutation par une mesure indépendante : une fois
le cardio effectué, le bonus d'alternance s'éteint, les scores V2 s'effondrent
en égalités, et **40 %** des décisions tombent sur `display_order`. C'est le
défaut `A` que `REC-CP1` avait prédit à 72 % sous mutation — il se manifeste ici
sans aucune mutation.

---

## 3. V3 — une précédence, pas de nouveaux poids

Le `§5` interdisait de commencer par régler des constantes. V3 n'en règle
aucune : il change la **forme** de la décision.

| Rang | Critère | Pourquoi ici |
|---|---|---|
| 0 | éligibilité | filtres V2 inchangés — un filtre de sécurité n'est pas une préférence |
| 1 | récupération | **minimum** sur les zones, pas moyenne : une zone à plat ne se compense pas |
| 2 | couverture longitudinale | le signal que le moteur calculait sans jamais le lire |
| 3 | justification de répétition | pénalisée, puis **levée** quand la couverture la porte |
| 4 | modalité délaissée | récence appliquée au couple force/cardio |
| 5 | ancienneté du gabarit, puis de la famille | le départage que la spec promet depuis l'origine |
| 6 | ordre de catalogue | dernier recours déterministe, aucun aléatoire |

Ce que V3 **supprime** : `WEIGHT_ALTERNATION = 20`, accordé dès que les deux
dernières séances étaient de la force — une condition **vraie en permanence**
pour quiconque s'entraîne en force — et le `+10` cardio-absent sans expiration.
Trente points constants offerts à une catégorie.

Ce que V3 **n'invente pas** : aucun seuil physiologique. Le déficit est relatif
à **la médiane de l'utilisateur lui-même**. Quatorze jours reste un horizon
d'observation (`§8`). Les cibles 24/36/48/72 h sont celles de V2, réutilisées
sans retouche. Aucun apprentissage automatique (`§15`), aucun aléatoire (`§10`).

### La borne causale qu'il a fallu ajouter

`compute_template_kpis` est la source de `last_done_at` que la spec désigne
depuis l'origine — **le moyen existait, le moteur ne l'avait jamais branché**.
Mais elle n'avait aucune borne haute : rejouée à une date passée, elle aurait
rendu la dernière séance **future**, et le départage aurait tranché sur le
futur. Elle reçoit un `until` optionnel, sur le patron de `REC-CP0a`.

---

## 4. La comparaison en ombre — boucle ouverte

```
                        V2                        V3
trajectoire        conc  cata            conc  cata
push-pull-legs     1.00  0.00            0.67  0.00
legs-lourd         1.00  0.00            0.80  0.80
equilibre          1.00  0.00            0.78  0.00
cardio-absent      1.00  0.00            0.60  0.00
substitutions      1.00  0.00            0.50  0.00
exercice-non-mappe 1.00  0.00            0.75  0.00
```

V3 reflète la trajectoire là où V2 rendait des séquences identiques pour
`push-lourd`, `pull-lourd` et `legs-lourd`.

**`legs-lourd` reste à 0,80 de départage par catalogue, et ce n'est pas caché.**
Après cinq séances de jambes, tous les gabarits du haut du corps sont également
délaissés **et** également jamais effectués : il n'existe aucune preuve pour en
préférer un. Le `§10` désigne l'ordre de catalogue comme dernier recours ; c'est
ce cas. En boucle fermée — le mode qui correspond à un utilisateur réel — la
part tombe à **0,10**.

### ⚠ Ce que ce rapport refuse de conclure

`§11` : **la variété n'est pas la justesse.** Aucune garde de ce sprint ne dit
que V3 est meilleur parce qu'il propose des séances plus variées.

J'avais d'abord écrit une garde « V3 ne doit pas répéter le même gabarit sur
toute une trajectoire ». Elle échouait sur sept trajectoires — **et elle avait
tort, pas V3**. En boucle ouverte l'utilisateur décline le conseil : la zone
reste réellement la plus délaissée, donc la redonner est honnête.

Elle est remplacée par l'invariant réel, `REPEAT_REQUIRES_EVIDENCE` : répéter
est permis, mais porté par la couverture — jamais par une égalité, un
`display_order`, un `slug` ou une donnée manquante.

---

## 5. Gardes

11 gardes neuves (`tests/test_rec_cp2_policy.py`), 14 de `REC-CP1` conservées.

- **V3 ne pilote rien** — balayage des importations réelles dans `app/`,
  `tests/`, `scripts/`, hors banc de mesure.
- **Causalité de la nouvelle entrée** — une décision au J+5 ne voit pas une
  séance du J+10 ; la garde vérifie aussi que **sans** la borne elle la verrait,
  sinon elle ne mesurerait pas la borne.
- **Ignorance ≠ déficit maximal** — le piège de `REC-CP0b` en miroir : une zone
  à zéro parce qu'un nom est illisible passerait pour la plus sous-servie et
  épinglerait la recommandation dans l'autre sens.
- **Médiane nulle ⇒ le critère se tait** — plutôt que de déclarer tout le monde
  en déficit maximal.
- **Minimum, pas moyenne**, sur la récupération.
- Déterminisme · séance exclue inerte · répétition possible et portée.

---

## 6. Ce qui reste avant toute promotion (`§12`)

1. **Le cas « conseil décliné » n'est traité par aucune des deux politiques.**
   C'est le vrai énoncé du défaut de dogfood, et il déborde le scoring : il
   suppose de mémoriser ce qui a été proposé, pas seulement ce qui a été fait.
   `DESIGN_PROPOSAL`, non implémenté — aucune persistance nouvelle n'a été
   inventée ici.
2. **`REC-CP3`** doit rendre l'explication structurée ; V3 expose déjà
   `facteurs` par candidat pour qu'elle n'ait rien à re-dériver.
3. `liss-only` n'a **aucun** exercice au catalogue, donc aucune zone. Fait de
   catalogue relevé, non interprété.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
