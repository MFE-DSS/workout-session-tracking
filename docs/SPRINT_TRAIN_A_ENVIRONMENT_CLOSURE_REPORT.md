# `TRAIN A` — Clôture de substitution et résolution d'environnement

**Branche** : `sb/train-a-environment-closure` sur canonique `337a4a0`
**Tier `check_scope`** : `SHARED_CODE` — **full sweep exécuté quand même**
(l'EKB est une donnée partagée dont le rayon d'impact a déjà piégé ce dépôt)
**Migration** : aucune.
**Filtre dur** : **TOUJOURS ÉTEINT**. Deux gardes AST le vérifient — le
modèle *et* le résolveur sont sans consommateur.

---

## 1. Ce que cette tranche a corrigé chez moi avant de corriger le produit

Deux de mes conclusions précédentes étaient fausses, et les deux dans le même
sens : **j'avais mesuré une seule route et conclu sur le produit.**

### 1.1 — L'atlas se résout aussi **par alias déclaré**

`E1` n'avait interrogé que `machine_slug`. Le produit utilise aussi
`get_machine_by_name`, qui compare le nom à `machine.name` **et à
`machine.aliases`**, en correspondance exacte. Ce n'est pas un rapprochement
approximatif : c'est une correspondance que l'atlas **énonce**.

| | |
|---|---|
| machines de l'atlas | 32 |
| atteintes par `machine_slug` | 25 |
| **jamais atteintes par slug** | **7** |
| identités de la clôture gagnées par la route alias | **11** |

Conséquence directe : **les réparations `§6` et `§7` n'en sont pas.**
`Reverse fly machine` → `rear-delt-fly-machine` et `Rowing chest-supported`
→ `chest-supported-row` étaient **déjà déclarés dans l'atlas**. Le défaut
était dans ma mesure, pas dans le dépôt.

### 1.2 — Le slug du Leg Press n'était pas un défaut, c'était une décision

J'allais restaurer `machine_slug = leg-press` sur
`Leg Press (pieds hauts, écartés)`. `Sx_CAT_01` l'avait **nullifié
délibérément**, sentinelle à l'appui :

> *« leg-press resolves to quad-dominant in the atlas, so keeping the slug
> would break machine-link coherence »*

Le champ porte de la **zone**, pas seulement un appareil. Votre `§0.B`
disait déjà la bonne voie — *« upstream repair at the EQUIPMENT CAPABILITY
level »* — et c'est ce qui est fait : l'exigence est écrite en
`equipment_requirements`, le slug n'est pas touché, la sentinelle tient.

---

## 2. Audit corrigé de `CANONICAL_IDENTITY` (`§1`)

Chaque ligne rejouée contre les quatre gardes. **13 retenues, 1 retirée,
1 requalifiée, 1 élargie.**

| ligne | verdict | ce que les gardes ont dit |
|---|---|---|
| `Curl EZ-bar debout` | ✅ | « EZ-bar » ; « debout » règle le support |
| `Romanian Deadlift barre` | ⚠ **requalifiée** | garde 3 : `barbell_straight` est **plus spécifique** que « barre ». La capacité a été **renommée `barbell`** — l'inférence colle au mot |
| `Curl marteau haltères` | ✅ | ACE #10, `Dumbbells` ; debout |
| `Curl incliné haltères` | ✅ | cas explicitement validé au `§1` |
| `Curl incliné haltères (banc 45°)` | ✅ | cas explicitement validé |
| `Shrugs haltères` | ✅ | debout, aucun support |
| `Élévations latérales haltères assis` | ✅ | `seated_support`, **pas** `flat_bench_support` |
| `Curl debout haltères` | ✅ | ajoutée par la clôture |
| `Relevé de jambes suspendu` | ✅ **généralisée** | `overhead_hang_support`, plus `pull_up_bar` (`§2`) |
| `Roulette abdominale` ×2 | ✅ | l'implément EST l'exercice |
| `Curl poulie basse` | ✅ | cas explicitement validé |
| `Curl poulie basse (barre)` | ✅ **élargie** | + `cable_attachment_straight_bar` (`§4`) |
| `Dips pectoraux (buste penché)` | ❌ **retirée** | `§3`. Et l'interne le confirme : l'atlas déclare `equipment: bodyweight` et **rien** sur un appui |

### La garde 3, appliquée pour de bon

« barre » ne peut pas établir « barre **droite** ». Mesuré dans le corpus :
la barre EZ est **toujours** qualifiée (`EZ-bar`, 2 occurrences sur 2), et
« barre » nue ne désigne jamais une EZ. La régularité est réelle — mais
elle ne rachète pas une capacité trop spécifique. La capacité s'appelle
donc `barbell`, et `barbell_ez` reste distincte : un propriétaire de barre
EZ n'obtient pas le soulevé de terre roumain, un propriétaire de barre
droite n'obtient pas le curl EZ. Les bonnes réponses sans la sur-précision.

### La règle qui manquait, et qui manque encore

Une exigence conjonctive doit être **complète**. Un libellé qui nomme
l'implément mais laisse la question du **support** ouverte ne suffit pas :
`Rowing haltère un bras` (sans « banc ») reste donc `UNKNOWN` là où
`Curl debout haltères` est établi — « debout » ferme la question, pas
« un bras ». *(Mis à jour au `§3.3` : l'atlas ferme finalement ce cas-ci.)*

---

## 3. Les trois réparations amont (`§5`–`§7`) et le cas des mollets (`§8`)

### 3.1 — Leg Press pieds hauts/écartés — réparée au niveau CAPACITÉ

Source : Life Fitness — *« narrow, wide, or staggered foot placements on the
oversized footplate »*. Un seul plateau, plusieurs placements ⇒
`machine_leg_press`. Écrite en `equipment_requirements`, **pas** en
`machine_slug` (voir `§1.2`).

### 3.2 — Reverse fly · Rowing chest-supported — aucune réparation nécessaire

L'atlas les déclarait déjà par alias. La preuve manufacturier existe et
corrobore (Life Fitness *Pectoral Fly / Rear Deltoid* est **un seul appareil
sélectorisé** couvrant les deux exécutions ; Hammer Strength *Select Seated
Row* documente la classe d'appareil à appui pectoral) — mais elle n'a pas
été nécessaire pour décider. Comme le dit le `§6` : **capacité partagée ≠
identité d'exercice identique**. Les deux identités restent distinctes.

### 3.3 — Le banc du rowing un bras, tranché par l'atlas

`one-arm-dumbbell-row` déclare `variants: ["banc plat", "one knee"]`. Le
banc est donc une **alternative documentée** :

* `Rowing haltère un bras` → `dumbbells` seul ;
* `Rowing haltère un bras (banc)` → `dumbbells` **+** `flat_bench_support`,
  parce que *cette identité-ci* nomme le banc. ACE #126 le corrobore.

La discrimination vient de l'interne, pas d'une source externe.

### 3.4 — Preuve de la scission des mollets (`§8`)

| | `Relevés mollets debout` | `Relevés mollets debout machine` |
|---|---|---|
| `equipment_family` | `bodyweight` | `machine` |
| `machine_slug` | **retiré** (était le défaut) | `standing-calf-raise` |
| exigence | **`[]`** — aucun matériel | `machine_standing_calf_raise` |

**La preuve que la scission tient** : `standing-calf-raise` porte
`name: "Mollets debout machine"` et `aliases: ["Standing calf raise"]`.
« Relevés mollets debout » **n'y figure pas**. La version poids du corps ne
peut donc pas se re-résoudre vers la machine par la porte alias. Une garde
vérifie que son exigence est `()` et non `None` — *rien à posséder* est un
fait établi, pas une ignorance.

Effet mesuré : dans un environnement `[]` (aucun matériel déclaré), c'est le
**seul** créneau natif des 106.

---

## 4. La clôture exacte (`§9`)

Mesurée sur les vrais objets : base semée comme le produit la sème, puis
`all_suggestions_flat` interrogé avec les `TemplateExercise` réels.

| | |
|---|---|
| gabarits servis | 17 |
| identités **prescrites** | **68** |
| identités atteintes en **substitut** | 82 |
| **CLÔTURE (union, uniques)** | **105** |
| dont substituts jamais prescrits | 37 |
| arcs `N1` · `N2` · `N3` | 125 · 142 · 116 |
| entrées d'EKB **jamais atteignables** | **0** |

**La clôture est à UN saut, et c'est mesuré, pas supposé** : le seul
appelant de `compute_suggestions` (`app/routers/sessions.py:700`) lui passe
`se.template_exercise`, l'**origine** du gabarit — jamais le nom substitué.
Re-substituer ré-offre donc le même ensemble.

**105 et non 103.** Les deux de plus sont `Incline DB Press 30°` et
`Incline Dumbbell Press` : le moteur de substitution lit
`exercise_properties`, qui porte deux orthographes absentes des 103 noms
canoniques. **Le moteur peut donc proposer un nom que l'EKB ne connaît
pas.** Une garde l'a trouvé ; `requirements_for_exercise` résout désormais
les alias **déclarés** par l'EKB avant de chercher. Sans cela, une exécution
parfaitement définie rendait `UNKNOWN` pour une raison d'orthographe.

---

## 5. Couverture sur la clôture (`§11`)

| | KNOWN | UNKNOWN |
|---|---|---|
| **clôture — 105 identités atteignables** | **66** | **39** |
| dont les 68 prescrites | **58** | 10 |
| dont les 37 substituts seuls | 8 | 29 |

Par classe de preuve : **50 `ATLAS`** · **3 `EXTERNE`** ·
**13 `IDENTITE_AUREN`**.

Le détail ligne à ligne, avec motif pour chaque `UNKNOWN`, vit dans
`data/equipment_curation.json` et dans
[l'annexe](SPRINT_TRAIN_A_ENVIRONMENT_CLOSURE_TABLE.md).

### Le levier « alias manquant », chiffré — et mesuré comme non fiable

39 `UNKNOWN` ; un rapprochement automatique par recouvrement de mots en
propose 12 rattachables à une machine existante. **J'ai vérifié les douze à
la main : cinq sont fausses.**

| proposition automatique | verdict à la lecture |
|---|---|
| `Hip thrust haltères` → `hip-thrust-smith` | ❌ haltères, pas Smith |
| `Sissy squat machine` → `hack-squat-machine` | ❌ deux appareils |
| `Sliding leg curl` → `seated-leg-curl` | ❌ sliders, pas une machine |
| `Élévations latérales haltères` → `cable-lateral-raise` | ❌ haltères, pas câble |
| `Élévations latérales machine` → `cable-lateral-raise` | ❌ **la bonne cible existe** : `lateral-raise-machine` |

**Le rapprochement approximatif se trompe une fois sur deux dans ce dépôt
même.** C'est la démonstration, sur données réelles, que la garde « no fuzzy
match » du `§1` a raison. Rien n'a été appliqué.

Les **7 paires que j'ai vérifiées à la main** et qui tiennent — à approuver
d'un mot, jamais à deviner :

| identité | machine d'atlas | pourquoi |
|---|---|---|
| `Lat pulldown prise large` | `lat-pulldown` | la prise n'est pas un appareil |
| `Lat pulldown prise neutre` | `lat-pulldown` | idem |
| `Élévations latérales machine` | `lateral-raise-machine` | l'atlas la porte, sans alias |
| `Triceps pushdown barre` | `triceps-pushdown-rope` | l'entrée déclare `barre droite` en variante |
| `Pushdown corde` | `triceps-pushdown-rope` | alias d'orthographe |
| `Traction assistée unilatérale` | `assisted-pull-up` | variante unilatérale |
| `Calf press leg press` | `leg-press` | l'identité **nomme** l'appareil |

Approuvées, elles feraient passer la clôture de **66/39** à **73/32**.

---

## 6. Le résolveur (`§12`, `§13`) — bâti, testé, non branché

`app/services/environment_resolution.py`. Quatre états de créneau, trois
états de gabarit, **aucun nombre**.

| environnement \ prescrit | prouvé | inconnu / infaisable |
|---|---|---|
| substitut prouvé disponible | `NATIVE_FEASIBLE` | `ADAPTABLE` |
| aucun prouvé, un chemin inconnu | — | `UNKNOWN` |
| tous les chemins incompatibles | — | `NOT_FEASIBLE` |

`ADAPTABLE` prime sur `UNKNOWN` : une certitude acquise n'est pas retirée
par une incertitude voisine. Refuser d'adapter parce qu'un autre chemin est
flou punirait l'utilisateur pour un trou de curation.

**Le `§10` est tenu par construction** : la liste de substituts est
**fournie** au résolveur, dans l'ordre du moteur (`N1`→`N2`→`N3`, chacun par
proximité) ; il prend le **premier** prouvé exécutable et s'arrête. Aucun
substitut inventé, aucune équivalence élargie, aucune priorité recalculée.
Trois gardes l'épinglent, dont une qui vérifie qu'un exercice faisable
**hors liste** n'est jamais retenu.

---

## 7. Preuve produit (`§19`) — et un défaut qu'elle a trouvé

Quatre environnements, les 17 gabarits réels, les vraies listes de
substituts.

| environnement | gabarits | créneaux (106) |
|---|---|---|
| **salle équipée** (25 objets) | 12 servables · 5 inconnus · **0 infaisables** | 89 natifs · 11 adaptés · 6 inconnus · 0 bloqués |
| **salle privée** (8 objets) | 4 · 6 · 7 | 37 · 41 · 19 · 9 |
| **maison** — haltères + banc (5) | 1 · 8 · 8 | 21 · 41 · 32 · 12 |
| **`[]`** — aucun matériel | 1 · 7 · 9 | **1** · 1 · 88 · 16 |

L'adaptation fonctionne et elle est lisible : en salle maison, `push-a`
remplace `Incline Smith Press` (manque `smith_rack`) par
`Développé incliné haltères 30°`, et `Neutral Grip Shoulder Press machine`
par `Shoulder press haltères assis`.

### Le défaut : deux créneaux, un seul exercice

Le harnais a montré `push-a` résolvant **deux** créneaux distincts vers
`Développé couché haltères`. Une séance qui prescrit deux fois le même
mouvement est une régression produit.

Corrigé : le résolveur préfère un substitut **non déjà retenu** dans la même
séance. Choisir parmi des substituts *déjà autorisés* est explicitement
permis par le `§10` ; éviter un doublon en est un cas, et n'élargit aucune
équivalence. Si le seul chemin exécutable est déjà pris, il est **repris
quand même** et le créneau porte `duplicate=True` — annoncer « infaisable »
une exécution possible serait un mensonge plus coûteux qu'un doublon
visible.

**A/B mesuré, et il ne dit pas ce que j'espérais :**

| environnement | sans préférence | avec |
|---|---|---|
| salle équipée | 7 | **3** |
| salle privée | 18 | **12** |
| **maison** | 22 | **22** |
| `[]` | 0 | 0 |

**En salle maison la correction ne change rien** : il n'existe aucune
alternative à proposer. Ce n'est pas un défaut de résolveur, c'est un
**constat de contenu** — le graphe de substitution autorisé ne peut pas
produire de séance sans répétition dans un environnement haltères-et-banc.
C'est l'argument le plus fort pour le `§17`, et il est désormais mesuré.

### Effet sur le classement V3 et sur l'Advice Memory

**Nul, et par construction.** Le résolveur n'est importé par aucun module de
décision — une garde AST le vérifie —, l'environnement n'entre dans aucun
signal de `recommendation_v3`, et l'empreinte de l'Advice Memory ne le
connaît pas. Ce n'est pas une mesure de non-régression : c'est une absence
de chemin d'appel. Le `§16` sera tenu à l'activation, pas avant.

---

## 8. Contenu sans matériel (`§17`) — **NON LIVRÉ**, et le coût exact

Les cinq identités sont résolues et dédoublonnées contre les 103
(`Glute Bridge` ≠ `Hip thrust` : épaules surélevées et charge externe, deux
mouvements). Leur exigence serait `[]`, donc faisable partout.

**Ce que l'intégration coûte, mesuré :**

| contrat touché | ce qu'il faut faire |
|---|---|
| `test_exactly_103_entries` | passe à 108 |
| snapshot byte-exact des noms | régénéré |
| `test_coverage_split_51_covered_52_gap` (67/36) | recalculé |
| `exercise_properties.json` | 5 entrées neuves — zones, pattern, chaîne |
| `test_blackholes_stay_visible_not_masked` (12) | vérifié |
| `reference_split.json` | un gabarit neuf + ses sentinelles |
| `test_exactly_68_prescribed_and_66_substitutes` | recalculé |

Sept contrats de référence, dont quatre épinglés byte-à-byte. **Je ne l'ai
pas fondu dans une tranche qui refait déjà la curation et livre un
résolveur** : une tranche que personne ne peut relire est une tranche qui
passe verte et casse ailleurs. C'est la porte **G4**, elle est nommée, et
elle est prête à exécuter seule.

`§9` respecté sur son interdiction : **aucun mouvement de tirage au poids du
corps n'a été inventé.**

---

## 9. Portes d'activation (`§18`)

| | porte | état |
|---|---|---|
| **G1** | clôture exacte mesurée | ✅ **105**, à un saut, prouvé |
| **G2** | sémantique déterministe ou `UNKNOWN` explicitement traité | ✅ 4 états, `UNKNOWN` jamais `FEASIBLE`, 39 trous nommés |
| **G3** | objet → capacité couvre toute exigence connue | ✅ garde : toute capacité curée est au vocabulaire |
| **G4** | gabarit de force sans matériel vivant | ❌ **non livré** — `§8` ci-dessus |
| **G5** | résolveur rend les quatre états correctement | ✅ 21 gardes, mutation jouée |
| **G6** | adaptation matérialisée avant `START` | ❌ non ouvert — demande le branchement |
| **G7** | `NULL` hérité préserve le comportement | ✅ garde : `NULL` ⇒ `UNKNOWN`, jamais un refus |
| **G8** | traitement produit de « aucun candidat servable » | ❌ non ouvert |
| **G9** | empreinte environnement-consciente à l'activation causale | ❌ non ouvert, délibérément |

**Quatre portes restent fermées. Le filtre reste éteint.**

---

## 10. Vérifications

* `check_scope` : `SHARED_CODE`. **Full sweep exécuté quand même** — l'EKB
  est une donnée partagée, et ce dépôt a déjà payé trois fois l'excès de
  confiance en `check_scope` sur ce fichier
* `ruff` sur **tous** les fichiers Python du diff : propre ; scan `S9073`
  par AST : aucun
* 68 gardes (47 + 21), mutations jouées
* 287 tests ciblés verts sur le rayon d'impact EKB + substitution

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
