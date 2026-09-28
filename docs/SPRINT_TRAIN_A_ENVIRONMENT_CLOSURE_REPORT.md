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
**seul** créneau natif — jusqu'à ce que le `§17` en ajoute quatre.

---

## 4. La clôture exacte (`§9`)

Mesurée sur les vrais objets : base semée comme le produit la sème, puis
`all_suggestions_flat` interrogé avec les `TemplateExercise` réels.

| | |
|---|---|
| gabarits servis | **18** |
| identités **prescrites** | **72** |
| identités atteintes en **substitut** | 84 |
| **CLÔTURE (union, uniques)** | **109** |
| dont substituts jamais prescrits | 37 |
| arcs `N1` · `N2` · `N3` | 127 · **142** · 116 |
| entrées d'EKB **jamais atteignables** | **0** |

**`N2` reste à 142 arcs et 52 identités, exactement comme avant le contenu
sans matériel.** C'est la preuve MESURÉE que le `§10` est tenu : le graphe de
substitution existant n'a pas bougé d'une arête. Seul `N1` monte de 125 à
127, par les deux substituts internes au nouveau gabarit — qui n'affectent
que ses propres créneaux.

**La clôture est à UN saut, et c'est mesuré, pas supposé** : le seul
appelant de `compute_suggestions` (`app/routers/sessions.py:700`) lui passe
`se.template_exercise`, l'**origine** du gabarit — jamais le nom substitué.
Re-substituer ré-offre donc le même ensemble.

**Au premier passage, 105 et non 103.** Les deux de plus sont `Incline DB Press 30°` et
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
| **clôture — 109 identités atteignables** | **70** | **39** |
| dont les 72 prescrites | **62** | 10 |
| dont les 37 substituts seuls | 8 | 29 |

Par classe de preuve : **50 `ATLAS`** · **7 `EXTERNE`** ·
**13 `IDENTITE_AUREN`**. Les quatre `EXTERNE` supplémentaires sont les
identités sans matériel, dont l'exigence est `[]` — une exigence **établie**,
pas une ignorance.

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

Approuvées, elles feraient passer la clôture de **70/39** à **77/32**.

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

Quatre environnements, les **18** gabarits réels, les vraies listes de
substituts.

| environnement | catalogue | créneaux (110) | sans matériel |
|---|---|---|---|
| **salle équipée** (25 objets) | `servable` — 13 · 5 · **0** | 93 natifs · 11 adaptés · 6 inconnus · 0 bloqués | `servable` |
| **salle privée** (8 objets) | `servable` — 5 · 6 · 7 | 41 · 41 · 19 · 9 | `servable` |
| **maison** — haltères + banc (5) | `servable` — 2 · 8 · 8 | 25 · 41 · 32 · 12 | `servable` |
| **`[]`** — aucun matériel | `servable` — **2** · 7 · 9 | **5** · 1 · 88 · 16 | **`servable`** |

**La ligne décisive est la dernière.** Avec *rien du tout* de déclaré, le
catalogue rend `servable` et le gabarit sans matériel passe **natif sur ses
quatre créneaux**. Avant le `§17`, cet environnement n'avait qu'un seul
créneau natif et aucun gabarit de force servable. C'est la porte `G4`, et
elle sert à quelque chose.

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
| **maison** | 22 | **21** |
| `[]` | 0 | **0** |

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

## 8. Contenu sans matériel (`§17`) — **LIVRÉ**, avec deux limites nommées

Quatre identités canoniques neuves, sourcées ACE, exigence `[]` :

| identité AUREN | source | dédoublonnage |
|---|---|---|
| `Pompes` | ACE #41 Push-Up | aucun homonyme |
| `Squat au poids du corps` | ACE #135 | les trois « squat » existants sont appareillés |
| `Fente avant` | ACE #94 | aucun homonyme |
| `Pont fessier` | ACE #49 | **distinct** de `Hip thrust` : épaules au sol, aucune charge externe |

Et un gabarit **vivant** : `no-equipment-full-body`, section `utility`,
quatre créneaux, aucun matériel externe. Il rend `SERVABLE` dans les quatre
environnements testés, y compris `[]`.

**Aucun mouvement de tirage n'a été inventé** (`§17`), et le gabarit
l'assume au lieu de combler pour la symétrie. Une garde vérifie qu'aucune
de ses zones n'est `lats` ni `upper_back`.

### Limite 1 — le `§10` interdit de rendre ce contenu substituable

J'avais ajouté `Pompes` à `exercise_properties.json`, **mécaniquement
nécessaire** pour qu'elle soit proposable en `N2`/`N3` : le moteur n'itère
que ce registre. Une garde nommée *« le registre de substitution est
intouché »* l'a refusée, et **elle a raison** — y écrire une entrée crée une
arête pour TOUS les exercices de même pattern ou de même zone. C'est
« broaden equivalence », que le `§10` interdit.

Conséquence assumée : **le contenu sans matériel est atteignable par
PRESCRIPTION, jamais comme substitut automatique d'un exercice appareillé.**
C'est aussi pourquoi les 21 doublons en salle maison ne se corrigent pas par
du contenu dans cette tranche. **Lever cette limite est un arbitrage
opérateur**, pas une décision de résolveur.

### Limite 2 — la planche frontale n'a pas de dose représentable

`Front Plank` (ACE #32) est sourcée mais **non intégrée**, pour une raison
structurelle : le référentiel canonique est **dérivé du catalogue**, donc une
identité qu'aucun gabarit ne référence est comptée comme une **dérive** par
l'audit. Or elle ne peut pas être prescrite : les 15 formats de `set_scheme`
du catalogue sont tous en répétitions, et un gainage se dose en temps.
Inventer un format serait un changement de schéma déguisé.

### Ce que le vocabulaire fermé ne sait pas classer

Les quatre identités entrent en `gap`, `movement_pattern = None` — comme
`Hack Squat machine`, `Squat Smith machine`, `Leg Press` et
`Crunch câble à genoux`. **Le vocabulaire fermé `pattern_motor` n'a ni jeton
squat ni jeton core**, et il laisse déjà **36 entrées sur 103** sans pattern.
Je n'en ai pas inventé. L'ouvrir reclasserait aussi les entrées existantes :
c'est un arbitrage, pas un effet de bord.

---

## 9. `§14`, `§15`, `§16`, `G8` — bâtis au niveau service, non branchés

| demande | livré |
|---|---|
| `§14` adaptation AVANT `START` | `materialization_plan()` — rend les `(position, prescrit, exécuté)` à poser. La lignée reste entière : le prescrit est porté **à côté** de l'exécuté, pas effacé |
| `§15` explication | `adaptation_notice()` — rend `« Adapté à ton équipement. »`, et **rien** si rien n'a changé. Ni liste, ni décompte |
| `G8` aucun candidat servable | `NO_SERVABLE_CANDIDATE`, un état **nommé** : « rien à proposer » et « rien n'a été calculé » ne doivent pas se ressembler. Un doute laisse le produit proposer ; seul un refus généralisé se dit |
| `§16` / `G9` empreinte | **inchangée, et c'est le contrat** : une garde AST vérifie que `empreinte_de_contexte` ne lit ni l'équipement ni le résolveur. `identite_materielle_environnement()` est prête pour l'activation |

**L'identité matérielle n'est pas la liste du matériel.** Deux
environnements différents qui produisent les mêmes exécutions sont la même
décision : déclarer une machine qu'aucun créneau n'utilise ne périme pas un
refus. Deux gardes le mesurent — l'une prouve l'insensibilité au matériel
inutile, l'autre prouve la sensibilité à une exécution qui change.

⚠ `§15` ne touche **aucun gabarit** : afficher ce fait sur Mission est une
surface visible, donc soumise au `CLAUDE.md §5.1` — un rendu réel soumis à
l'opérateur **avant** tout commit. Le fait existe et est testé ; son
affichage attend votre arbitrage.

---

## 10. Portes d'activation (`§18`)

| | porte | état |
|---|---|---|
| **G1** | clôture exacte mesurée | ✅ **109**, à un saut, prouvé |
| **G2** | sémantique déterministe ou `UNKNOWN` explicitement traité | ✅ 4 états, `UNKNOWN` jamais `FEASIBLE`, 39 trous nommés |
| **G3** | objet → capacité couvre toute exigence connue | ✅ garde : toute capacité curée est au vocabulaire |
| **G4** | gabarit de force sans matériel **vivant** | ✅ `no-equipment-full-body`, `SERVABLE` même avec `[]` |
| **G5** | résolveur rend les quatre états correctement | ✅ 82 gardes, mutation jouée |
| **G6** | adaptation matérialisée avant `START` | ⚠ **plan bâti et testé, non branché** — la pose sur `session_builder` EST l'activation |
| **G7** | `NULL` hérité préserve le comportement | ✅ garde : `NULL` ⇒ `UNKNOWN`, jamais un refus |
| **G8** | traitement produit de « aucun candidat servable » | ⚠ **état nommé et testé au service** ; l'écran reste à arbitrer (`§5.1`) |
| **G9** | empreinte environnement-consciente à l'activation causale | ✅ **absente aujourd'hui, prouvée par AST** ; identité matérielle prête |

**Sept portes franchies, deux à moitié.** `G6` et `G8` ne demandent plus de
conception : elles demandent un **branchement** et un **écran**, c'est-à-dire
précisément les deux gestes que l'activation recouvre. Le filtre servi reste
éteint.

---

## 11. Contrat de livraison UI (`CLAUDE.md §5`)

Cette tranche ne touche **aucun gabarit ni aucune feuille de style**. Elle
change quand même une surface visible : la Bibliothèque passe de **13 à 14
cartes**, le gabarit sans matériel entrant en *SÉANCES UTILITAIRES*. Le §5
s'applique donc, et il n'a pas été contourné.

### 5.1 — exposition visuelle préalable

Rendu **réel** capturé en localhost authentifié, **écran entier**, mobile
390 px et desktop 1280 px, et **soumis à l'opérateur avant livraison**.
Vérifier une chaîne dans le HTML ne vaut pas exposition ; un test vert non
plus.

### 5.2 — relecture du relevé, décision par décision

`docs/DESIGN_DECISIONS_UIV2_SURFACES.md` :

| décision | verdict |
|---|---|
| **Q5** — trois rangs de surface | **respectée** — la carte reprend le rang existant de sa section, aucun conteneur neuf |
| **Q6** — échelle 32/22/15/12 | **non concernée** — aucun rang typographique introduit |
| **Q7** — un seul aplat ambre par écran | **respectée** — la carte n'en porte aucun ; le rendu le montre |
| **Q8** — aucune opacité décorative | **non concernée** — aucune couleur écrite |
| **Q1 · Q2 · Q3 · Q4** | **non concernées** — connexion, accueil, séance |

### 5.3 — jamais une soustraction seule

Aucune soustraction : la tranche **ajoute** un gabarit.

### 5.4 — toute couleur est un token

**Aucune couleur introduite.** La carte hérite intégralement des tokens de
sa section.

---

## 12. Vérifications

* `check_scope` : `SHARED_CODE`. **Full sweep exécuté quand même** — l'EKB
  est une donnée partagée, et ce dépôt a déjà payé trois fois l'excès de
  confiance en `check_scope` sur ce fichier. Verdict sur arbre gelé :
  **`tous les lots sont verts.`** (354 fichiers, aucun sauté)
* `ruff` sur **tous** les fichiers Python du diff : propre ; scan `S9073`
  par AST : aucun
* **82 gardes** (47 + 35), mutations jouées — dont « l'inconnu devient
  servable », attrapée
* 261 tests ciblés verts sur le rayon d'impact EKB + substitution +
  catalogue + identité
* **CI de PR : 9/9 verte** · Sonar `OK`, 0 bug, 0 code smell, couverture
  nouveau code **100 %**

### Deux fautes de méthode, dites plutôt que lissées

**J'ai édité l'arbre PENDANT un sweep.** Son verdict ne valait donc rien —
les derniers lots lisaient un arbre que les premiers n'avaient pas vu. Le
sweep retenu a été rejoué sur un arbre gelé.

**J'ai corrigé deux gardes d'une même famille et laissé la troisième.**
`test_full_body_morphotype_priority` épinglait aussi le compte de gabarits ;
seule la CI l'a vue. Je l'ai ensuite cherchée **par classe**, en AST, sur
toutes les comparaisons entières liées aux gabarits — il n'y en avait que
deux, et les deux sont traitées. C'est le défaut « famille aux deux tiers »,
et il s'est reproduit exactement comme consigné.

---

## 13. Closeout

| | |
|---|---|
| **PR** | [#262](https://github.com/MFE-DSS/workout-session-tracking/pull/262) |
| **Merge** | `d1595cb12e89bcdeb539b3748ec674ab8a920935` |
| **Méthode** | `--merge` avec `--match-head-commit 3784faa` — pas de squash, pas d'`--admin`, pas de force |
| **CI canonique** | run [`36445277190`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/36445277190) — **7/7 verts** |
| **Sonar (autorité de merge : le gate de PR)** | `OK` — **0 issue ouverte sur la PR**, 0 bug, 0 code smell, 0 vulnérabilité, duplication 0 %, couverture nouveau code **100 %** |
| **Threads de revue** | 0, résolu ou non |
| **Migration** | aucune |

### Gate visuel — accepté par l'opérateur

La seule conséquence visible est la Bibliothèque passant de **13 à 14
lignes**. Elle a été soumise en rendu **réel**, authentifié, écran entier,
aux deux points de rupture, avec un **avant/après** produit depuis deux
worktrees distincts servis séparément.

L'opérateur a **accepté**. Ce que la revue a mesuré plutôt qu'affirmé :

| | avant `337a4a0` | après |
|---|---|---|
| lignes de Bibliothèque | 13 | **14** |
| sections | 4 | **4, identiques** |
| débordement horizontal à 390 px | 0 px | **0 px** |
| textes rognés | 0 | **0** |
| poignées sous 44 px | 0 / 13 | **0 / 14** |
| aplats ambre | 1 | **1** |

Diff structurel du DOM rendu, origine normalisée : **une ligne ajoutée,
zéro retirée**, et les trois autres groupes **identiques octet pour
octet**. Classe de ligne `loadout__row` de part et d'autre.

`DESIGN_DECISIONS_UIV2_SURFACES.md` relu décision par décision :
**Q5 · Q6 · Q7 · Q8 respectées**, Q1–Q4 et le reste non concernés,
**aucune violée**.

⚠ Un faux vert attrapé pendant ce gate : mon premier diff structurel
comparait **deux pages de connexion** — un `username` de test à deux
caractères contre `minlength="3"` — et rendait « identiques : True » sur du
vide. Une preuve d'identité de page précède désormais toute comparaison.

### Ce que ce merge ne fait PAS

| | |
|---|---|
| filtre d'environnement servi | **ÉTEINT** — vérifié par AST au HEAD mergé : `environment_resolution` a **zéro importeur** |
| les 7 alias vérifiés | **non appliqués** |
| graphe de substitution | **non élargi** — `exercise_properties` reste à 69 entrées |
| `pattern_motor` | **inchangé** |
| Bibliothèque | **non redessinée** — aucun gabarit, aucune CSS au diff |
| `G6` · `G8` | **documentés comme travail d'activation**, pas implémentés en silence |

### Registre et roadmap

**Aucune mise à jour requise.** Le protocole appliqué à ce train fait le
closeout en **annexe du rapport de sprint** : les deux closeouts précédents
— `456519c` (#259) et `337a4a0` (#261) — n'ont touché que leur rapport,
aucun `SPEC_REGISTRY` ni `ROADMAP`. Vérifié sur le diff de chacun.

### Portes restantes

`G4` est franchie. **`G6` et `G8` restent ouvertes** et ne demandent plus de
conception : un branchement sur `session_builder` et un écran soumis au
`§5.1`. Elles sont le point de départ du sprint d'activation, qui n'est pas
ouvert ici.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
