# SPRINT Sb_SET_CONTRIBUTION_POLICY_01 — comptabilité effective (RAPPORT)

**Train :** `AUREN_EFFECTIVE_VOLUME_COMPLETION_01`, tranche 1/4 ·
**Base canonique :** `4191a37` · **Branche :** `sb/set-contribution-policy-01` ·
**Tier `check_scope` :** **SHARED_CODE**

Comparer **44 séries planifiées** à **126 séries de bornes basses** mélangeait
deux unités. Cette tranche introduit la conversion manquante — et la mesure qui
en sort change le diagnostic, mais pas dans le sens attendu.

---

## 1. Brainstorming / Options / Risques / Choix retenu

### La convention

`SET_CONTRIBUTION_POLICY_VERSION = "set-contribution-v1"` — direct **1,0**,
indirect **0,5**, non résolu **0**.

**`0,5` est un coefficient de comptabilité.** Pas 50 % d'activation, pas un
demi-stimulus, pas une équivalence EMG, pas une fraction mesurée. Aucune
littérature n'est invoquée pour affirmer qu'une série indirecte vaudrait
exactement la moitié d'une directe : c'est une **règle de comptage produit**,
choisie parce qu'elle est déterministe, explicable et **versionnée**.

### Unités entières plutôt que flottants

Le crédit se compte en **demi-séries entières** : direct = 2 unités, indirect =
1. Les gardes de budget comparent donc des `int`, jamais des `float` accumulés.
Un plan à 3 séries indirectes vaut exactement 3 unités = 1,5 série effective,
sans tolérance arbitraire. `effective_sets` n'existe que pour l'affichage.

### D'où vient la contribution — et la conséquence assumée

Du contrat canonique `body_zone_source`, appliqué à l'**exercice réellement
sélectionné**, jamais à l'intention du créneau.

C'est ce que le brief demande, et il faut en assumer la conséquence : quand
l'intention et l'exercice divergent, **le crédit suit l'exercice**. Cela rend
visible un défaut de données jusqu'ici masqué (§4).

### Audit des consommateurs — la question qui évite le pire

| Consommateur | Unité | Décision |
|---|---|---|
| `weekly_plan_materialization` (`set_scheme`, `rep_targets`) | **PHYSIQUE** | inchangé |
| `list.html` « N séries planifiées » | **PHYSIQUE** | inchangé |
| `user_programs` router (`readiness.planned_sets`) | **PHYSIQUE** | inchangé |
| `adaptive_replan` (`sets_before/after`) | **PHYSIQUE** | inchangé (tranche 4) |
| **Comparaison au budget** (`planning_low/baseline/high`) | **EFFECTIF** | **migré** |

Une garde structurelle interdit au matérialisateur de lire `effective_units`,
`effective_sets` ou `indirect_sets` : ce qu'on exécute ne peut pas être ce qu'on
compte.

### Déplacement du verdict de volume

`allocate_zone` **ne décide plus** `UNMET_VOLUME`. Le crédit indirect d'une zone
dépend d'exercices programmés pour **d'autres** zones : aucune allocation isolée
ne peut le connaître. Le planificateur cumule toutes les contributions, puis
tranche.

---

## 2. La mesure obligatoire — et elle contredit l'attente

Fixture déterministe : cadence 4, aucune priorité.

| | |
|---|---|
| Séries **physiques**/semaine | **44** |
| Somme effective **ANCIENNE** (primaire seul) | **44** |
| Somme effective **NOUVELLE** (direct + indirect) | **50** |
| Somme des bornes basses | **126** |
| Zones **sous** `planning_low` | **10 / 11** |
| Zones **≥** `planning_low` | **1** (`biceps`) |
| Zones **≥** `baseline` | **0** |

### Plus grands déficits (séries effectives manquantes)

| Zone | Effectif | Borne basse | Manque |
|---|---|---|---|
| `delt_lat` | 4 | 16 | **−12** |
| `pecs` | 4 | 14 | −10 |
| `lats` | 4 | 14 | −10 |
| `upper_back` | 4 | 14 | −10 |
| `posterior` | 4 | 14 | −10 |

**Le comptage effectif ne referme pas l'écart : 44 → 50 sur 126.**

### Pourquoi si peu — la cause racine, mesurée

Sur les **69 exercices** du pool, seuls **20** portent une zone secondaire au
référentiel canonique, et ces secondaires sont **exclusivement `biceps` (15) et
`triceps` (5)**.

**Neuf zones sur onze sont structurellement incapables de recevoir le moindre
crédit indirect** : la table ne leur en attribue jamais. Un développé couché ne
crédite pas les deltoïdes antérieurs, un squat ne crédite pas les ischios — non
par choix de politique, mais parce que le référentiel ne l'écrit nulle part.

**La conclusion opérationnelle : le déficit n'était pas une erreur d'unité.**
C'était, à 6 séries près, un déficit réel. La tranche 3 doit donc allouer de la
capacité, pas espérer un gain comptable.

---

## 3. Ce que la politique change réellement

Une seule zone bascule : **`biceps`**, 4 directes + 8 indirectes ⇒ **8
effectives**, exactement sa borne basse. Elle passe de « non couverte » à
« couverte », et c'est **vrai** : trois tirages la sollicitent.

`triceps` gagne 2 effectives (6/8) sans atteindre sa borne.

Un test épingle que **seuls `biceps` et `triceps`** peuvent recevoir du crédit
aujourd'hui — il tombera le jour où la curation s'élargit, ce qui est exactement
le signal souhaité.

---

## 4. Le défaut que la comptabilité rend visible

`calves` **perd la moitié de son crédit** : 8 séries physiques, **4 effectives**.

« Calf press leg press » est classé `calves` par l'EKB et **`quads`** par le
classifieur canonique — le groupe `quads` contient « leg press » et gagne dans
une liste ordonnée. Le planificateur le sélectionne pour un créneau **mollets**
(le pool le marque `muscle_group: calves`), mais le contrat de zones le crédite
aux **quadriceps**.

Résultat mesurable : `quads` affiche **8 effectives pour 4 séries physiques**,
`calves` **4 pour 8**.

**Deux sources du dépôt se contredisent sur le même exercice**, et jusqu'ici
personne ne pouvait le voir. Ce n'est pas une régression introduite ici : c'est
la même divergence que j'avais signalée en `Sb_SLOT_INTENT_COVERAGE_01` et
laissée hors périmètre — elle a désormais une **conséquence chiffrée**.

**Non corrigée dans cette tranche**, délibérément : `body_zone_source` prévoit un
mécanisme de corrections revues, mais y ajouter une entrée modifie
`resolve_exercise_zones` pour **tous** ses consommateurs (`muscle_scoring`,
rapport de parité, seed DB). C'est un sprint de données avec son propre rayon
d'impact, pas un ajout de passage. **Épinglé par un test**, pour qu'une
correction soit un choix explicite.

---

## 5. Tests — 34 dédiés, 2 plantations

Barème (direct 4→4, indirect 4→2, composé sur deux zones, zone en double créditée
**une** fois, jamais >1 effective par série physique) · aucun crédit fabriqué
(exercice inconnu ⇒ rien, `unknown` jamais stocké, 0/négatif ⇒ rien) · unités
entières (bornes converties, 3 indirectes = exactement 1,5) · physique ≠ effectif
(total physique inchangé à 44, `calves` 8 physiques / 4 effectives) · le crédit
indirect est **porteur** (sans lui `biceps` n'atteint pas sa borne) · traçabilité
et langage · non-régressions (matérialisation en physique, garde structurelle,
déterminisme).

**Plantations** : secondaire promu en direct ⇒ **6 tests tombent** · crédit
fabriqué pour une zone inconnue ⇒ **2 tests tombent**.

**Correction de mon propre texte** : le `basis` disait « pas une fraction
d'activation musculaire » — un démenti, mais qui met malgré tout le cadre
physiologique sous les yeux du lecteur. Reformulé en **positif** (« crédit
indirect au coefficient 0,5 — convention de comptage versionnée ») ; le démenti
complet vit dans `ACCOUNTING_GUARD`, à destination du code.

### Tests existants mis à jour — l'unité a changé, pas la garde

Deux tests comparaient `planned_sets` **physiques** à la bande — exactement la
confusion que la tranche supprime. Ils comparent désormais `is_within_band`
(effectif). Le témoin de « zone atteignant sa bande » passe de `calves` à
`biceps`, avec la raison écrite dans le test.

## Verdict

La frontière physique/effectif est fermée : la dose exécutée et la dose comptée
ne peuvent plus être confondues, et une garde structurelle l'empêche.

**Mais la mesure invalide l'espoir d'un gain comptable : 44 → 50 sur 126.** Le
référentiel n'attribue de zone secondaire qu'à 20 exercices sur 69, toutes vers
`biceps`/`triceps` — neuf zones ne peuvent structurellement rien recevoir. Le
déficit est réel.

**La suite doit donc être poursuivie sur les NOUVEAUX déficits mesurés**, comme
le brief l'exige, et la tranche 3 doit allouer de la capacité réelle.

Un défaut de données est rendu visible et chiffré (`calves` / `quads`) : c'est
une décision produit, remontée et épinglée, pas comblée en passant.

---

## Closeout (post-merge)

| | |
|---|---|
| PR | **#97** — `--merge --match-head-commit`, **sans** squash / `--admin` / force |
| Build | `1e4c7e5` — **vert au premier passage**, aucun correctif |
| Merge | **`b56d12b`** |
| Gate Sonar | **`OK`** — couverture du neuf **98,8 %**, 0 smell, 0 bug, 0 vulnérabilité |
| Threads / Gitar | **0 / 0** |
| Tests | **4 205** (shard 1 : 2 261 · shard 2 : 1 944) |

### Capacité CI — **HEALTHY**, et en amélioration

| | Shard A | Shard B |
|---|---|---|
| min MemAvailable | **5 043 Mo** | **5 311 Mo** |
| min SwapFree | 3 071 Mo — **jamais entamé** | 3 071 Mo — **jamais entamé** |

Le minimum des deux shards **remonte à 5 043 Mo**, contre **4 574 Mo** à la fin
du train précédent. La pente signalée alors ne se confirme pas ici : cette
tranche ajoute des tests **purs** (aucun fixture `client`), ce qui valide une
fois de plus le modèle de coût — la mémoire suit les tests HTTP, pas leur
nombre.

### Zéro incident

Vert au premier passage : aucun finding Sonar, aucun conflit, aucune reprise de
CI. Le pré-scan `S9073`/`S5863`/`S3415` et la règle d'ordonnancement (closeout
de N avant branchement de N+1) tiennent pour la deuxième tranche consécutive.
